"""经络引导：把命中按四通道分流，给出"该先通哪条脉"的顺序。

四通道沿用仓内既有分组（blood / lymph / qi / shen），不新增第五通道、不改既有通道语义：
- blood（血脉）：承载结构——嵌套、胶囊泛滥这类"骨架堵点"。
- lymph（淋巴）：清浊代谢——冗余装饰、占位文案、行内样式堆积。
- qi（气）：声势与表达——字体默认值、紫蓝渐变、喊口号、渐变文字。
- shen（神）：意图与可读——字号过小、标题跳级、标题塞 emoji。

route 只做计数与排序，判定仍由 detectors 给出，二者不互相覆盖。
"""

from __future__ import annotations

from typing import Dict, List, Sequence

from .detectors import Finding

CHANNELS = (
    ("blood", "血脉：结构承载"),
    ("lymph", "淋巴：清浊代谢"),
    ("qi", "气：声势表达"),
    ("shen", "神：意图可读"),
)

# 每条规则只归一个通道，四通道均非空（与 detectors._rule_table 的第四列一致）
RULE_CHANNEL = {
    "DV-01": "qi",
    "DV-02": "qi",
    "DV-03": "blood",
    "DV-04": "shen",
    "DV-05": "shen",
    "DV-06": "qi",
    "DV-07": "lymph",
    "DV-08": "shen",
    "DV-09": "lymph",
    "DV-10": "lymph",
    "DV-11": "qi",
    "DV-12": "blood",
}


def route(findings: Sequence[Finding]) -> Dict[str, object]:
    """按通道分流并给出最堵的那条通道。"""
    counts: Dict[str, int] = {name: 0 for name, _ in CHANNELS}
    for f in findings:
        channel = f.channel if f.channel in counts else RULE_CHANNEL.get(f.rule_id, "")
        if channel in counts:
            counts[channel] += 1
    total = sum(counts.values())
    ordered = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return {
        "total": total,
        "counts": counts,
        "blocked": [name for name, n in ordered if n > 0],
        "worst": ordered[0][0] if total else "",
        "empty_channels": [name for name, n in ordered if n == 0],
    }


def channel_rules(channel: str) -> List[str]:
    """返回某通道下的规则 id（未知通道返回空列表）。"""
    names = {name for name, _ in CHANNELS}
    if channel not in names:
        return []
    return sorted(rid for rid, ch in RULE_CHANNEL.items() if ch == channel)
