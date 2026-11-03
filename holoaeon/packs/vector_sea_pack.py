# -*- coding: utf-8 -*-
"""
VectorSeaPack —— 向量海能源勘探+加工+分发扩展包（第 14 个扩展包）
================================================================================
V14-SKILL-LATHE-PROTOCOL-PLUGINS · 把"向量海=石油矿藏"沉淀为确定性技能：

  V13 勘探打捞（1-5）：ocr_snapshot / vector_match / tensor_coupling /
                        wisdom_salvage / multi_modal_scan
  V14 机床加工+协议适配（6-8）：skill_lathe / protocol_export / skill_workbench

8 技能 / 4 角色 / 2 工作流；key = "vector_sea"（EXTRA_PACK_ORDER 13→14）。
纯标准库、零外部依赖、确定性、离线；维度不变（只进 EXTRA_PACK_REGISTRY，
不进 PACK_ORDER —— A1 的 25/47/9 不受影响）。
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from typing import Any, Dict, List, Optional

from .base import DomainPack, RoleSpec, SkillSpec, WorkflowSpec
from ..skill_lathe import SkillLathe
from ..protocol_plugins import export_all_protocols, list_protocols

# ============================================================ 常量（确定性口径）
# 能量分级（TVCB）：A≥0.7 / B≥0.4 / C<0.4（C 级丢弃）
GRADE_A = 0.7
GRADE_B = 0.4
# 向量海矿藏口径（V13 投喂包）：617 技能 / 195 篇 / 10 GEMS / 462 项
VECTOR_SEA_CORPUS = {"skills": 617, "documents": 195,
                     "gems": 10, "knowledge": 462}


def _clip01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def _det_fp(parts: List[str]) -> str:
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]


def _tokenize(text: str) -> List[str]:
    """确定性分词：中文按字符、英文按词。"""
    import re
    tokens: List[str] = []
    for seg in re.split(r"[\s,，。.;；:：!！?？()（）\[\]【】{}]+", str(text)):
        if not seg:
            continue
        if any("\u4e00" <= ch <= "\u9fff" for ch in seg):
            tokens.extend(list(seg))
        else:
            tokens.append(seg.lower())
    return tokens


def _cosine(a: List[str], b: List[str]) -> float:
    """词袋余弦相似度（确定性）。"""
    if not a or not b:
        return 0.0
    from collections import Counter
    ca, cb = Counter(a), Counter(b)
    inter = sum((ca & cb).values())
    na = math.sqrt(sum(v * v for v in ca.values()))
    nb = math.sqrt(sum(v * v for v in cb.values()))
    return inter / (na * nb) if na and nb else 0.0


# ============================================================ V13 · 勘探打捞技能
def ocr_snapshot(text: str = "", sample_size: int = 200, **_a: Any) -> dict:
    """OCR 取样快照：文本 → 词频快照（TF-IDF 风格取样，纯文本直通降级）。"""
    raw = str(text or "")
    tokens = _tokenize(raw)
    from collections import Counter
    counts = Counter(tokens)
    top = counts.most_common(sample_size)
    return {"status": "ok", "snapshot": {"tokens": tokens[:sample_size],
            "top_terms": [{"term": t, "count": c} for t, c in top[:20]],
            "total_terms": len(tokens), "unique_terms": len(counts)},
            "mode": "text_direct"}


def vector_match(query: str = "", corpus: Optional[list] = None, **_a: Any) -> dict:
    """向量海余弦搜索：query 与矿藏语料的余弦相似度打捞。"""
    q = _tokenize(str(query or ""))
    items = list(corpus or [])
    matches = []
    for i, item in enumerate(items):
        text = str(item.get("text") or item if isinstance(item, dict) else str(item))
        score = _cosine(q, _tokenize(text))
        if score > 0:
            matches.append({"index": i, "score": round(score, 4),
                            "text": text[:60]})
    matches.sort(key=lambda m: m["score"], reverse=True)
    return {"status": "ok", "query": str(query or ""),
            "corpus_size": len(items), "matches": matches[:10]}


def tensor_coupling(snapshot: Optional[dict] = None, matches: Optional[list] = None,
                    energy: float = 0.6, **_a: Any) -> dict:
    """张量向量耦合体（TVCB）精炼：快照+匹配 → 结构化知识载体。"""
    snap = snapshot or {}
    m = matches or []
    topic = "general"
    top_terms = snap.get("snapshot", {}).get("top_terms", [])
    keywords = [t["term"] for t in top_terms[:8]] if top_terms else []
    if m:
        topic = str(m[0].get("text", "general"))[:24]
    grade = "A" if energy >= GRADE_A else ("B" if energy >= GRADE_B else "C")
    tvcb = {
        "tvcb_id": "TVCB-%s" % _det_fp([str(snap.get("snapshot", {}).get("total_terms", 0)),
                                        str(len(keywords)), topic]).upper(),
        "semantic_vec": [round(float(t["count"]), 4) for t in top_terms[:8]],
        "topic": {"primary": topic},
        "keywords": keywords,
        "idea_pattern": " / ".join(keywords[:3]) if keywords else "general pattern",
        "reusable_points": [str(x.get("text", "")) for x in m[:3]] if m else [],
        "linked_skills": ["ocr_snapshot", "vector_match", "tensor_coupling"],
        "tensor_transform": "tfidf-sampled-cosine",
        "energy_grade": grade,
        "energy_score": round(_clip01(energy), 4),
    }
    return {"status": "ok", "tvcb": tvcb}


def wisdom_salvage(tvcb: Optional[dict] = None, **_a: Any) -> dict:
    """智慧打捞封存：TVCB → 确定性指纹 + 封存结构（不写盘，调用方落 reports/）。"""
    t = tvcb or {}
    seal = {
        "batch": "V14-SKILL-LATHE-PROTOCOL-PLUGINS",
        "tvcb_id": t.get("tvcb_id"),
        "topic": (t.get("topic") or {}).get("primary"),
        "energy_grade": t.get("energy_grade"),
        "fingerprint": _det_fp([str(t.get("tvcb_id")),
                                str((t.get("topic") or {}).get("primary")),
                                str(t.get("energy_grade"))]),
        "sealed_at": "deterministic-offline",
    }
    return {"status": "ok", "seal": seal}


def multi_modal_scan(text: str = "", mode: str = "blocks", **_a: Any) -> dict:
    """多模态遍历穷举：按行/块枚举输入（PDF/图片/文字的通用扫描降级）。"""
    raw = str(text or "")
    mode = mode if mode in ("lines", "blocks") else "blocks"
    units = [ln for ln in raw.splitlines() if ln.strip()] if mode == "lines" else \
        [raw[i:i + 64] for i in range(0, len(raw), 64)] if raw else []
    return {"status": "ok", "mode": mode, "units": len(units),
            "sample": units[:10], "corpus": VECTOR_SEA_CORPUS}


# ============================================================ V14 · 机床+协议技能
def skill_lathe(tvcb: Optional[dict] = None, **_a: Any) -> dict:
    """技能机床：TVCB → SkillSpec（C 级丢弃，A/B 级加工）。"""
    spec = SkillLathe().turn_skill(tvcb or {})
    if spec is None:
        return {"status": "ok", "dropped": True,
                "reason": "energy_grade=C（低品位丢弃）"}
    return {"status": "ok", "skill_spec": {k: v for k, v in spec.items()
                                           if k != "fn"}}


def protocol_export(skill_spec: Optional[dict] = None, **_a: Any) -> dict:
    """遍历穷举导出：SkillSpec → 全部 12 种平台协议格式。"""
    spec = skill_spec or {}
    exports = export_all_protocols(spec)
    return {"status": "ok", "protocol_count": len(exports),
            "exports": exports}


def skill_workbench(action: str = "list", spec: Optional[dict] = None,
                    **_a: Any) -> dict:
    """技能工作台：浏览 / 编辑 / 注册（list/edit/register 三动作演示）。"""
    action = str(action or "list")
    if action == "register":
        s = spec or {}
        return {"status": "ok", "action": "register",
                "registered": s.get("name"),
                "note": "经 DomainPack/kernel.register_fn 注册（离线确定性）"}
    if action == "edit":
        s = dict(spec or {})
        s.pop("fn", None)
        return {"status": "ok", "action": "edit", "edited": s}
    return {"status": "ok", "action": "list",
            "catalog": ["ocr_snapshot", "vector_match", "tensor_coupling",
                        "wisdom_salvage", "multi_modal_scan",
                        "skill_lathe", "protocol_export", "skill_workbench"]}


# ============================================================ 扩展包定义
class VectorSeaPack(DomainPack):
    key = "vector_sea"
    name = "向量海能源勘探+加工+分发平台（V13勘探 × V14机床 × V14协议适配）"
    description = (
        "把向量海（617 技能 + 195 篇 + 10 GEMS + 462 项）当作石油矿藏："
        "勘探（OCR快照→余弦打捞→TVCB精炼→封存）→ 机床（TVCB→SkillSpec）→ "
        "协议适配（12 种平台协议遍历穷举导出）；用户落地=PDF/图片/文字→任意平台可调技能"
    )

    skills = [
        SkillSpec("ocr_snapshot", ocr_snapshot,
                  "OCR 取样快照：文本 → 词频快照（TF-IDF 风格，mineru 缺失时纯文本直通降级）",
                  tags=["vector_sea", "explore", "ocr", "snapshot"],
                  inputs={"text": "str", "sample_size": "int"}),
        SkillSpec("vector_match", vector_match,
                  "向量海余弦搜索：query 与矿藏语料余弦相似度打捞",
                  tags=["vector_sea", "explore", "search", "cosine"],
                  inputs={"query": "str", "corpus": "list"}),
        SkillSpec("tensor_coupling", tensor_coupling,
                  "张量向量耦合体（TVCB）精炼：快照+匹配 → 结构化知识载体",
                  tags=["vector_sea", "refine", "tvcb", "tensor"],
                  inputs={"snapshot": "dict", "matches": "list", "energy": "float"}),
        SkillSpec("wisdom_salvage", wisdom_salvage,
                  "智慧打捞封存：TVCB → 确定性指纹 + 封存结构",
                  tags=["vector_sea", "salvage", "seal", "fingerprint"],
                  inputs={"tvcb": "dict"}),
        SkillSpec("multi_modal_scan", multi_modal_scan,
                  "多模态遍历穷举：按行/块枚举输入（PDF/图片/文字通用扫描降级）",
                  tags=["vector_sea", "scan", "multimodal", "enumerate"],
                  inputs={"text": "str", "mode": "str"}),
        SkillSpec("skill_lathe", skill_lathe,
                  "技能机床：TVCB → SkillSpec（C 级丢弃，A/B 级加工，可注册）",
                  tags=["vector_sea", "lathe", "skill", "manufacture"],
                  inputs={"tvcb": "dict"}),
        SkillSpec("protocol_export", protocol_export,
                  "遍历穷举导出：SkillSpec → 12 种平台协议格式",
                  tags=["vector_sea", "protocol", "export", "plugins"],
                  inputs={"skill_spec": "dict"}),
        SkillSpec("skill_workbench", skill_workbench,
                  "技能工作台：浏览 / 编辑 / 注册（list/edit/register）",
                  tags=["vector_sea", "workbench", "catalog", "register"],
                  inputs={"action": "str", "spec": "dict"}),
    ]

    roles = [
        RoleSpec("explorer", "勘探师（取样+搜索）：OCR快照·余弦打捞·多模态扫描",
                 ["ocr_snapshot", "vector_match", "multi_modal_scan"]),
        RoleSpec("driller", "钻井工（打捞+精炼）：TVCB 精炼·智慧封存",
                 ["tensor_coupling", "wisdom_salvage"]),
        RoleSpec("lathe_operator", "机床操作工（加工+注册）：TVCB→SkillSpec·工作台",
                 ["skill_lathe", "skill_workbench"]),
        RoleSpec("protocol_engineer", "协议工程师（适配+导出）：12 协议遍历穷举",
                 ["protocol_export"]),
    ]

    workflows = [
        WorkflowSpec("explore_drill_refine",
                     ["explorer", "driller", "explorer"],
                     "勘探→钻井→精炼：取样→搜索→TVCB→封存（V13 七阶段闭环）"),
        WorkflowSpec("lathe_export_deploy",
                     ["lathe_operator", "protocol_engineer", "lathe_operator"],
                     "加工→适配→导出→部署：TVCB→SkillSpec→12 协议→任意平台（V14 闭环）"),
    ]


def pack_summary() -> Dict[str, Any]:
    p = VectorSeaPack()
    return {"key": p.key, "skills": len(p.skills), "roles": len(p.roles),
            "workflows": len(p.workflows)}


def main(argv=None) -> int:
    """CLI 入口（演示）：8 技能 / 4 角色 / 2 工作流 + 端到端演示。"""
    args = list(sys.argv[1:] if argv is None else argv)
    print("== HoloAeon 向量海勘探+加工+分发平台（vector_sea 第14扩展包）==")
    print("包契约:", pack_summary())
    if args and args[0].strip() == "--selfcheck":
        snap = ocr_snapshot("向量海 勘探 机床 协议 平台 技能 智慧 打捞")
        m = vector_match("机床 协议", [{"text": "技能机床 协议 适配"},
                                     {"text": "无关文本"}])
        tv = tensor_coupling(snap, m["matches"], energy=0.85)
        sp = skill_lathe(tv["tvcb"])
        ex = protocol_export(sp["skill_spec"])
        ok = (len(VectorSeaPack.skills) == 8 and len(VectorSeaPack.roles) == 4
              and len(VectorSeaPack.workflows) == 2
              and tv["tvcb"]["energy_grade"] == "A"
              and ex["protocol_count"] == 12)
        print("自检:", "PASS" if ok else "FAIL",
              "skills=8 roles=4 workflows=2 TVCB_grade=%s protocols=%d"
              % (tv["tvcb"]["energy_grade"], ex["protocol_count"]))
        return 0 if ok else 1
    print("8 技能: %s" % ", ".join(s.name for s in VectorSeaPack.skills))
    print("4 角色: %s" % ", ".join(r.name for r in VectorSeaPack.roles))
    print("2 工作流: %s" % ", ".join(w.name for w in VectorSeaPack.workflows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
