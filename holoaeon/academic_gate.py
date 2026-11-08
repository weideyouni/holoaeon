# -*- coding: utf-8 -*-
"""academic_gate — 学术笔痕闸门（V40，学术诚实纪律蒸馏）
D-11 链位：领域编排环（第十环·学术域）——shengui_gate（第九环）之后。
源蒸馏：GitHub AIScientists-Dev/academic-humanizer（MIT，v0.3.3）。
指针纪律：只取形状，不搬资产——图案目录/保全台账/断言-证据纪律三形状入环，
上游六层提示词原文不入仓（取形状弃资产）。
P4 诚实裁决：上游自陈 "not for evading AI-use disclosure"，与本仓刚性 DNA
（真实性、零虚构零模拟）同向——本环是学术诚实闸（claim ≤ evidence），
不是检测规避器；"去 AI 味"营销面弃用，只保留确定性可审计的三纪律。
SAME_AS-06（第六次独立趋同，待碳基终审裁定）：断言≤证据的绑定纪律，
与医学母版（三态药理学的证据分级）在无串谋下同构——
医学→数学→茶→宇宙→教育→学术，第六次。
处置权分离：本环 report-only，零改写函数；改写权=人类作者/碳基终审。
零依赖纯标准库。封口密语：潮起开门，潮落闭嘴。
"""
import re
from collections import Counter

SEAL = "潮起开门，潮落闭嘴"

CHAIN_POSITION = {
    "ring": 10,
    "name": "学术域编排（学术笔痕闸门）",
    "upstream": ("shengui_gate", "doc_anatomy", "magic_lamp"),
    "role": "图案目录扫描+保全台账不动点+断言-证据强度对账，report-only",
    "ethics_note": "不为规避 AI 使用披露设计；学术诚实=claim ≤ evidence",
    "lineage_note": "SAME_AS-06：与医学母版证据绑定纪律独立趋同（待碳基终审裁定）",
    "disposition_note": "处置权分离：零改写函数，报告不落笔",
}

# 图案目录（上游 L1 通用 tell + L2 学术 tell 的确定性子集）：
# (编号, 类别, 编译正则, 处置建议)。只报不改（处置权分离）。
_TELL_DEFS = [
    ("T01", "hype",
     r"paves the way|opens new avenues|sheds light on|paramount importance"
     r"|bridges the gap|pivotal (?:moment|step)|has the potential to revolutionize"
     r"|groundbreaking|revolutioniz\w+",
     "改为具体失败模式/具体结果"),
    ("T02", "ai_vocab",
     r"\b(?:delve|underscor\w+|intricate|tapestry|testament|pivotal"
     r"|showcas\w+|foster\w*|realm|seamless(?:ly)?)\b",
     "删除或换朴素直述"),
    ("T03", "filler",
     r"[Ii]t is worth noting that|[Ii]t should be (?:noted|emphasized) that"
     r"|[Ii]n order to|(?<![\w-])Notably,|(?<![\w-])Importantly,",
     "若重要，句子自会显示；删外壳"),
    ("T04", "em_dash",
     r"—|(?<!\d)--(?!\d)",
     "改逗号/冒号/括号/拆句（上游裁定 em-dash 全移除；数字区间 en-dash 除外）"),
    ("T05", "empty_intensifier",
     r"(?:extensive|comprehensive|thorough) (?:experiments|evaluations?)"
     r"|a wide range of|\b(?:numerous|various)\b",
     "换具体清单：三个数据集/五颗种子"),
    ("T06", "novelty",
     r"\bnovel\b|to the best of our knowledge|for the first time",
     "每节≤1 次；改指认与最近前邻的具体差异"),
    ("T07", "formulaic_opener",
     r"In recent years,|With the rapid development of|Despite recent advances",
     "直接给出结构性局限/事实"),
    ("T08", "vague_hedge",
     r"\b(?:somewhat|relatively|fairly|quite)\b|to some extent",
     "量化或删除"),
    ("T09", "overclaim",
     r"\b(?:prove[sn]?|proving|demonstrat\w+|establish\w*|confirm\w*"
     r"|guarantee\w*)\b",
     "降级为 show/provide evidence，并挂证据指针"),
    ("T10", "copula", r"serves as", "改 is"),
    ("T11", "unbacked_significance",
     r"significantly(?!\s*(?:\(|p\s*[<≤]|\d))",
     "挂检验名与 p 值，或删词"),
]

TELL_PATTERNS = [(tid, cat, re.compile(rx), advice)
                 for tid, cat, rx, advice in _TELL_DEFS]

# 保全白名单（上游 L3）：证据系对冲是学术正确，绝不标红、绝不"加硬"。
HEDGE_WHITELIST = ("suggests", "is consistent with", "we hypothesize",
                   "may indicate", "appears to")

STRONG_VERBS = re.compile(
    r"\b(?:prove[s]?|proving|demonstrat\w+|establish\w*|confirm\w*"
    r"|guarantee\w*)\b", re.I)
_EVIDENCE_MARK = re.compile(r"\[\d|\(\s*(?:Table|Figure|Fig\.|Section|Eq)"
                            r"|\d")
_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")
_CONNECTIVES = ("Moreover", "Furthermore", "Additionally", "In particular")


def ledger(text):
    """保全台账：抽取数字与引文键（含计数）。引文不动点的最小不变量。

    全息对位：内容域的引文不动点 ≈ 工程域的 SHA 不动点（V38 check_sums）——
    都是"审计过的最小可信不变量"。数字/引文一律不改不增不减。
    """
    nums = Counter(re.findall(r"\d+(?:\.\d+)?", text))
    cites = Counter(re.findall(r"\[[0-9,\s]+\]|\[@?[A-Za-z][\w-]*\d{4}[\w;-]*\]",
                               text))
    return {"numbers": dict(nums), "cites": dict(cites), "seal": SEAL}


def check_preservation(original, rewritten):
    """引文不动点校验：数字与引文键多重集必须完全相等（L3 红线）。"""
    a, b = ledger(original), ledger(rewritten)
    ca, cb = Counter(a["numbers"]), Counter(b["numbers"])
    sa, sb = Counter(a["cites"]), Counter(b["cites"])
    missing = list((ca - cb) + (sa - sb))
    added = list((cb - ca) + (sb - sa))
    return {"ok": not missing and not added,
            "missing": missing, "added": added, "seal": SEAL}


def scan(text):
    """确定性扫描：返回 findings（编号/类别/位置/片段/建议）。不落笔。"""
    findings = []
    for tid, cat, rx, advice in TELL_PATTERNS:
        for m in rx.finditer(text):
            findings.append({"id": tid, "cat": cat, "pos": m.start(),
                             "snippet": m.group(0)[:60], "advice": advice})
    # 连接词连跑：相邻两句同以 Moreover/Furthermore/... 开头（上游 2.6）
    pos = 0
    starts = []
    for s in _SENT_SPLIT.split(text):
        starts.append((pos, s))
        pos += len(s) + 1
    for i in range(len(starts) - 1):
        w0 = starts[i][1].lstrip().split(" ", 1)[0].rstrip(",")
        w1 = starts[i + 1][1].lstrip().split(" ", 1)[0].rstrip(",")
        if w0 in _CONNECTIVES and w1 in _CONNECTIVES:
            findings.append({"id": "T12", "cat": "connective_run",
                             "pos": starts[i + 1][0], "snippet": w1,
                             "advice": "让逻辑承载衔接，删连接词"})
    return findings


def claim_evidence(text):
    """断言-证据对账（上游 L4）：强动词句必须带数字/引文/图表指针，
    否则记 unbacked_claim——没有动词比它的证据更强。"""
    out = []
    pos = 0
    for s in _SENT_SPLIT.split(text):
        if STRONG_VERBS.search(s) and not _EVIDENCE_MARK.search(s):
            out.append({"type": "unbacked_claim", "pos": pos,
                        "snippet": s.strip()[:80],
                        "advice": "挂证据指针或降级动词"})
        pos += len(s) + 1
    return out


def audit(text):
    """总闸：图案 findings + 断言对账 + 保全台账；verdict=PASS/FINDINGS。"""
    findings = scan(text)
    claims = claim_evidence(text)
    return {"verdict": "PASS" if not findings and not claims else "FINDINGS",
            "findings": findings, "claims": claims,
            "ledger": ledger(text), "seal": SEAL}
