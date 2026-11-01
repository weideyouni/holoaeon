# -*- coding: utf-8 -*-
"""
skill_matrix.index —— 全量技能盘查与六机制映射（只读扫描，不执行任何外部脚本）
================================================================================
输入：若干技能根目录（每个子目录含 SKILL.md）
输出：确定性索引（无时间戳、无随机源），按 9 领域 × 6 机制 × 线程档位 三维归类。

纪律：
  · 只读 SKILL.md 头部（前 3000 字符），不 import、不执行技能代码；
  · 索引摘要 index_digest 只由"名字有序拼接"决定，故同集合必得同 digest；
  · 同一技能目录多次出现记为 dup，不重复计数。
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from typing import Dict, Iterable, List, Optional, Tuple

from .mech import semantic_overlap

DOMAIN_LEXICON: Dict[str, Tuple[str, ...]] = {
    "writing": ("写作", "文案", "小说", "润色", "扩写", "摘要", "作文", "稿", "笔记", "公众号"),
    "literature": ("文献", "论文", "检索", "引用", "综述", "pubmed", "arxiv", "刊", "学术史"),
    "research": ("研究", "调研", "实验", "学术", "方法论", "假设", "证伪", "综述"),
    "data": ("数据", "统计", "表格", "excel", "csv", "指标", "报表", "清洗", "看板", "可视化"),
    "growth": ("营销", "运营", "增长", "选题", "小红书", "抖音", "内容", "流量", "种草", "转化"),
    "business": ("商务", "商业", "合同", "销售", "客户", "市场", "报价", "招投标", "策划"),
    "quant": ("量化", "股票", "基金", "回测", "估值", "财报", "交易", "策略", "组合", "仓位"),
    "optimization": ("优化", "求解", "梯度", "单纯形", "遗传算法", "收敛", "调度", "排产"),
    "gaoyi": ("编译", "解释器", "字节码", "运行时", "语法", "ast", "vm"),
}

MECH_LEXICON: Dict[str, Tuple[str, ...]] = {
    "holographic_heartbeat": ("心跳", "同步", "巡检", "健康", "存活", "tick", "监控", "快照", "状态"),
    "cytoskeleton": ("结构", "骨架", "拓扑", "编排", "依赖", "流水线", "架构", "层级", "管线"),
    "skin_v6": ("安全", "合规", "审查", "校验", "红线", "权限", "风控", "审核", "熔断", "隐私"),
    "semantic_bus": ("语义", "路由", "通信", "消息", "总线", "意图", "匹配", "分类", "召回", "索引"),
    "hebbian_field": ("协作", "协同", "联动", "多智能体", "矩阵", "团队", "组合", "圆桌", "分身"),
    "meridian": ("经络", "通道", "资源", "预算", "流量", "链路", "配额", "分流", "气血", "养生"),
}

WRITE_HINTS: Tuple[str, ...] = ("写入", "上传", "发送", "删除", "发布", "推送", "创建", "修改", "同步")

_FM_NAME = re.compile(r"^name\s*:\s*(.+)$", re.M)
_FM_DESC = re.compile(r"^description\s*:\s*(.+)$", re.M)


def list_skill_dirs(roots: Iterable[str]) -> List[Tuple[str, str, str]]:
    """返回 (技能名, 根目录, SKILL.md 绝对路径)，同名多根全部保留（供去重统计）。"""
    out = []
    for root in roots:
        if not os.path.isdir(root):
            continue
        for name in sorted(os.listdir(root)):
            p = os.path.join(root, name, "SKILL.md")
            if os.path.isfile(p):
                out.append((name, root, p))
    return out


def parse_head(path: str, max_chars: int = 3000) -> Dict[str, str]:
    """只读 SKILL.md 头部，抽取 name / description（容忍多行与引号）。"""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            head = fh.read(max_chars)
    except OSError:
        return {"name": "", "description": ""}
    name = ""
    desc = ""
    m = _FM_NAME.search(head)
    if m:
        name = m.group(1).strip().strip("'\"")
    m = _FM_DESC.search(head)
    if m:
        desc = m.group(1).strip().strip("'\"")
        if desc in ("|", ">", "|-", ">-"):
            desc = ""
    if not desc:
        body = re.sub(r"^---[\s\S]*?---", "", head).strip()
        desc = body.splitlines()[0] if body else ""
    return {"name": name, "description": desc[:220]}


def _score(text: str, lexicon: Dict[str, Tuple[str, ...]]) -> Tuple[str, float]:
    best, best_score = "", 0.0
    for key, words in lexicon.items():
        sc = max((semantic_overlap(text, w) for w in words), default=0.0)
        if sc > best_score:
            best, best_score = key, sc
    return best, round(best_score, 5)


def classify(name: str, desc: str) -> Dict[str, object]:
    text = (name + " " + desc).lower()
    domain, dscore = _score(text, DOMAIN_LEXICON)
    mech, mscore = _score(text, MECH_LEXICON)
    lane = "write" if any(h in text for h in WRITE_HINTS) else "read"
    return {"domain": domain or "unmapped", "domain_score": dscore,
            "mechanism": mech or "unmapped", "mech_score": mscore, "lane": lane}


def build(roots: Iterable[str]) -> dict:
    roots = list(roots)
    rows: List[dict] = []
    seen: Dict[str, int] = {}
    for name, root, path in list_skill_dirs(roots):
        head = parse_head(path)
        row = {"name": name, "root": os.path.basename(os.path.dirname(root)) or root,
               "description": head["description"], "bytes": os.path.getsize(path)}
        row.update(classify(head["name"] or name, head["description"]))
        seen[name] = seen.get(name, 0) + 1
        row["dup"] = False
        rows.append(row)
    for row in rows:
        row["dup"] = seen[row["name"]] > 1
    digest = hashlib.sha256("|".join(sorted(r["name"] for r in rows)).encode("utf-8")).hexdigest()[:16]
    return {"digest": digest, "roots": [os.path.abspath(r) for r in roots],
            "count": len(rows), "skills": rows, "stats": summarize(rows)}


def summarize(rows: List[dict]) -> dict:
    def tally(key: str) -> Dict[str, int]:
        out: Dict[str, int] = {}
        for r in rows:
            out[r[key]] = out.get(r[key], 0) + 1
        return dict(sorted(out.items(), key=lambda t: (-t[1], t[0])))

    return {"count": len(rows),
            "by_mechanism": tally("mechanism"),
            "by_domain": tally("domain"),
            "by_lane": tally("lane"),
            "dup_names": sum(1 for r in rows if r.get("dup")),
            "unmapped": sum(1 for r in rows if r["mechanism"] == "unmapped")}


def save(index: dict, path: str) -> str:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    payload = json.dumps(index, ensure_ascii=False, indent=1, sort_keys=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(payload)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def load(path: str) -> Optional[dict]:
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)
