# -*- coding: utf-8 -*-
"""external_skill_registry —— 外部技能族的族级登记桥接（V6.0-B1）

定位：这是「1199 条外部技能」与内核之间的**桥**，不是复制，也不是并入 47 条内置技能。
登记表在 data/v6_skill_family_registry.json（1229 条索引 → 58 个域×机制族），
本模块只做三件确定性的事：

  1. load / stats        —— 读登记表并复核成员数与摘要（可回读、可对账）
  2. family_of / match   —— 技能名 → 所属族；任务文本 → 候选族（确定性打分，无随机源）
  3. route               —— 给内核一个「没命中内置技能时」的候选出口

红线：纯标准库、离线、确定性；不读凭证、不联网、不写盘、不改 kernel.skills 的 47 条。
密令：潮起开门，潮落闭嘴。evidence_class=simulated，仿真≠证明，碳基终裁。
"""
from __future__ import annotations

import hashlib
import json
import os

REGISTRY_ID = "SG-V6-SKILL-FAMILY-MAP-V1"
BRIDGE_ID = "SG-V6-SKILL-FAMILY-BRIDGE-V1"
REGISTRY_FILE = "v6_skill_family_registry.json"
_CACHE = {}


def _root(root=None):
    if root:
        return root
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(here))


def registry_path(root=None):
    return os.path.join(_root(root), "data", REGISTRY_FILE)


def load(root=None):
    """读登记表（带缓存）。缺失时返回空壳而不是抛异常，便于 CI/异机降级。"""
    p = registry_path(root)
    key = os.path.abspath(p)
    if key in _CACHE:
        return _CACHE[key]
    if not os.path.isfile(p):
        data = {"id": REGISTRY_ID, "families": [], "family_count": 0,
                "member_total": 0, "missing": True}
        _CACHE[key] = data
        return data
    with open(p, encoding="utf-8") as f:
        data = json.load(f)
    _CACHE[key] = data
    return data


def families(root=None):
    return list(load(root).get("families", []))


def stats(root=None):
    """族级统计 + 摘要复核（成员总数与登记表声明值必须相等）。"""
    d = load(root)
    fams = d.get("families", [])
    names = sorted(n for f in fams for n in f.get("members", []))
    digest = hashlib.sha256("\n".join(names).encode("utf-8")).hexdigest()
    return {
        "bridge_id": BRIDGE_ID,
        "registry_id": d.get("id"),
        "family_count": len(fams),
        "member_total": len(names),
        "declared_total": d.get("member_total"),
        "runtime_skills": d.get("runtime_skills"),
        "members_sha256": digest,
        "digest_match": digest == d.get("members_sha256"),
        "missing": bool(d.get("missing")),
        "dimension_lock": d.get("dimension_lock", {}),
    }


def family_of(name, root=None):
    """技能名 → 族 id（找不到返回 None）。"""
    for f in families(root):
        if name in f.get("members", ()):
            return f.get("id")
    return None


def match(task, k=3, root=None):
    """任务文本 → 候选族（确定性打分）。

    打分只看两件事：族标签/关键词是否出现在任务里（中文可命中），
    以及技能名的英文 token 与任务 token 的交集。
    排序固定为 (-score, family_id)，同输入必得同输出。
    """
    text = (task or "").lower()
    toks = set(t for t in _split(text) if len(t) >= 2)
    scored = []
    for f in families(root):
        score = 0
        for kw in f.get("keywords", ()):
            kk = str(kw).lower()
            if kk and kk in text:
                score += 2
        label = str(f.get("label", "")).lower()
        if label and label in text:
            score += 2
        for name in f.get("members", ()):
            for t in _split(name.lower()):
                if t in toks:
                    score += 1
        if score:
            scored.append({"family": f.get("id"), "label": f.get("label"),
                           "domain": f.get("domain"),
                           "mechanism": f.get("mechanism"),
                           "score": score, "count": f.get("count"),
                           "sample": list(f.get("sample", ()))})
    scored.sort(key=lambda x: (-x["score"], str(x["family"])))
    return scored[:k]


def _split(text):
    """中英混合分词：ASCII 连续段按非字母数字切；CJK 连续段按 bigram 切。

    缺陷根因（千问 2026-11-03 耦合装入报告 P0-1）：中文 isalnum() 为真且无空格，
    整句会塌成单 token，使成员名/关键词的 token 交集匹配对中文完全失效。
    CJK bigram 是零依赖下最简可用方案（V22+ 补丁升级采纳千问方案）。
    确定性：纯字符扫描，同输入必得同 token 列表。
    """
    out, buf_ascii, buf_cjk = [], "", ""

    def _flush_cjk():
        nonlocal buf_cjk
        if len(buf_cjk) == 1:
            out.append(buf_cjk)
        elif len(buf_cjk) > 1:
            out.extend(buf_cjk[i:i + 2] for i in range(len(buf_cjk) - 1))
        buf_cjk = ""

    for ch in text:
        if '\u4e00' <= ch <= '\u9fff':
            if buf_ascii:
                out.append(buf_ascii)
                buf_ascii = ""
            buf_cjk += ch
        elif ch.isalnum():
            if buf_cjk:
                _flush_cjk()
            buf_ascii += ch
        else:
            if buf_ascii:
                out.append(buf_ascii)
                buf_ascii = ""
            if buf_cjk:
                _flush_cjk()
    if buf_ascii:
        out.append(buf_ascii)
    if buf_cjk:
        _flush_cjk()
    return out


def route(task, k=3, root=None):
    """给内核的候选出口：命中返回候选族，未命中显式说明（不静默兜底）。"""
    cands = match(task, k=k, root=root)
    st = stats(root)
    if st["missing"]:
        return {"status": "registry_missing", "candidates": [],
                "bridge_id": BRIDGE_ID}
    if not cands:
        return {"status": "no_family_matched", "candidates": [],
                "bridge_id": BRIDGE_ID, "family_count": st["family_count"],
                "hint": "登记表有族但任务词面无命中；显式指定 family 或用内置 47 技能"}
    return {"status": "ok", "candidates": cands, "bridge_id": BRIDGE_ID,
            "family_count": st["family_count"]}
