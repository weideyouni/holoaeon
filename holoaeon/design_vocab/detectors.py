"""确定性反模式检测（自写 12 条，不宣称与上游 62 条等量）。

上游 Impeccable 用"确定性规则、零 LLM、零 API key"的方式抓 AI 味；本仓沿用这个做法，规则由本仓
自写、可复核、可扩展：每条规则给出 id / 分级（P0–P3，P0 最该先修）/ 归属经络通道 / 命中证据。

判定只读文本，不做渲染、不取网络、不调用模型，因此同一输入必得同一输出。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Sequence, Tuple

SEVERITY_ORDER = ("P0", "P1", "P2", "P3")

_PURPLE = re.compile(r"#(?:6c5ce7|7c3aed|8b5cf6|a855f7|9333ea|6366f1|5b21b6)", re.I)
_GRADIENT = re.compile(r"(?:linear|radial)-gradient\(", re.I)
_FONT_SIZE = re.compile(r"font-size\s*:\s*([0-9]+(?:\.[0-9]+)?)px", re.I)
_HEX_COLOR = re.compile(r"#[0-9a-fA-F]{3,6}")
_EMOJI = re.compile(
    "[\U0001F300-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF]"
)
_SHADOW = re.compile(r"box-shadow\s*:\s*([^;\"']+)", re.I)
_INLINE_STYLE = re.compile(r"style\s*=\s*\"([^\"]*)\"", re.I)
_TAG = re.compile(r"<(/?)(h[1-6]|div)([^>]*)>", re.I)
_CLASS_ATTR = re.compile(r"class\s*=\s*\"([^\"]*)\"", re.I)


@dataclass(frozen=True)
class Finding:
    """一条命中。line 为 1 起的文本行号，evidence 为触发片段的截断原文。"""

    rule_id: str
    rule: str
    severity: str
    channel: str
    line: int
    evidence: str


def _lines(text: str) -> List[str]:
    return text.replace("\r\n", "\n").replace("\r", "\n").split("\n")


def _snip(value: str, limit: int = 48) -> str:
    value = " ".join(value.split())
    return value if len(value) <= limit else value[: limit - 1] + "…"


def _rule_table() -> Tuple[Tuple[str, str, str, str], ...]:
    """(id, 名称, 分级, 经络通道)。规则与通道一一对应，保证四通道都有覆盖。"""
    return (
        ("DV-01", "overused-font", "P1", "qi"),
        ("DV-02", "purple-gradient", "P1", "qi"),
        ("DV-03", "nested-card", "P2", "blood"),
        ("DV-04", "tiny-text", "P0", "shen"),
        ("DV-05", "heading-skip", "P1", "shen"),
        ("DV-06", "shouting-caps", "P2", "qi"),
        ("DV-07", "shadow-stack", "P3", "lymph"),
        ("DV-08", "emoji-ui", "P3", "shen"),
        ("DV-09", "placeholder-copy", "P1", "lymph"),
        ("DV-10", "inline-style-soup", "P2", "lymph"),
        ("DV-11", "gradient-text", "P3", "qi"),
        ("DV-12", "pill-everywhere", "P3", "blood"),
    )


_RULES = _rule_table()
RULES = _RULES


def rule_meta() -> Tuple[Tuple[str, str, str, str], ...]:
    """返回规则元数据表（id, 名称, 分级, 通道）。"""
    return _RULES


def rule_ids() -> Tuple[str, ...]:
    """返回全部规则 id。"""
    return tuple(r[0] for r in _RULES)


def scan(text: str) -> List[Finding]:
    """扫描一段界面源码，返回按（规则 id, 行号）排序的命中列表。"""
    hits: List[Finding] = []
    lines = _lines(text)
    body = "\n".join(lines)
    rule_meta_map = {r[0]: r for r in _RULES}

    def add(rid: str, line_no: int, evidence: str) -> None:
        meta = rule_meta_map[rid]
        hits.append(Finding(rid, meta[1], meta[2], meta[3], line_no, _snip(evidence)))

    # DV-01 无衬线默认字体堆里直接顶 Inter
    for i, line in enumerate(lines, 1):
        if re.search(r"font-family\s*:[^;]*\bInter\b", line, re.I) and "var(" not in line:
            add("DV-01", i, line)

    # DV-02 紫蓝渐变底色
    for i, line in enumerate(lines, 1):
        if _GRADIENT.search(line) and _PURPLE.search(line):
            add("DV-02", i, line)

    # DV-03 卡片套卡片（按 class 含 card 的 div 深度计）
    depth = 0
    for i, line in enumerate(lines, 1):
        for m in _TAG.finditer(line):
            closing, tag, attrs = m.group(1), m.group(2).lower(), m.group(3) or ""
            is_card = tag == "div" and _CLASS_ATTR.search(attrs) and "card" in (_CLASS_ATTR.search(attrs).group(1) or "").lower()
            if closing and is_card:
                depth = max(0, depth - 1)
            elif is_card:
                depth += 1
                if depth >= 2:
                    add("DV-03", i, line)
            elif closing and tag == "div":
                depth = max(0, depth - 1) if depth else 0

    # DV-04 正文级字号过小（<12px）
    for i, line in enumerate(lines, 1):
        for m in _FONT_SIZE.finditer(line):
            if float(m.group(1)) < 12.0:
                add("DV-04", i, line)
                break

    # DV-05 标题跳级（h1 之后直接 h3）
    seen = []
    for i, line in enumerate(lines, 1):
        for m in _TAG.finditer(line):
            if m.group(1):
                continue
            tag = m.group(2).lower()
            if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
                seen.append((tag, i))
    for idx in range(1, len(seen)):
        prev = int(seen[idx - 1][0][1])
        cur = int(seen[idx][0][1])
        if cur > prev + 1:
            add("DV-05", seen[idx][1], "从 h%d 直接跳到 h%d" % (prev, cur))

    # DV-06 整段大写喊口号
    for i, line in enumerate(lines, 1):
        caps = re.findall(r"\b[A-Z][A-Z\s]{31,}\b", line)
        if caps:
            add("DV-06", i, caps[0])

    # DV-07 阴影叠层（>=3 段）
    for i, line in enumerate(lines, 1):
        for m in _SHADOW.finditer(line):
            if m.group(1).count(",") >= 2:
                add("DV-07", i, line)
                break

    # DV-08 标题里塞 emoji
    for i, line in enumerate(lines, 1):
        if re.search(r"<h[1-6][^>]*>", line, re.I) and _EMOJI.search(line):
            add("DV-08", i, line)

    # DV-09 占位文案
    if re.search(r"lorem\s+ipsum", body, re.I):
        for i, line in enumerate(lines, 1):
            if re.search(r"lorem\s+ipsum", line, re.I):
                add("DV-09", i, line)

    # DV-10 行内样式堆积（单元素 >=4 条声明）
    for i, line in enumerate(lines, 1):
        for m in _INLINE_STYLE.finditer(line):
            if m.group(1).count(";") >= 3:
                add("DV-10", i, line)

    # DV-11 渐变文字（背景裁切到文字）
    for i, line in enumerate(lines, 1):
        if re.search(r"background-clip\s*:\s*text", line, re.I) and _GRADIENT.search(body):
            add("DV-11", i, line)

    # DV-12 胶囊圆角泛滥（>=3 处）
    pill_lines = [i for i, line in enumerate(lines, 1) if re.search(r"border-radius\s*:\s*(?:999|9999|50%)", line, re.I)]
    if len(pill_lines) >= 3:
        for i in pill_lines:
            add("DV-12", i, lines[i - 1])

    hits.sort(key=lambda f: (f.rule_id, f.line))
    return hits


def rank(hits: Sequence[Finding]) -> List[Finding]:
    """按 P0→P3 排序，同级按规则 id，便于"先修什么"直接可读。"""
    return sorted(hits, key=lambda f: (SEVERITY_ORDER.index(f.severity), f.rule_id, f.line))
