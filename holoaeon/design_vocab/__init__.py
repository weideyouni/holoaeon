"""设计语汇（Design Vocabulary）旁挂模块 —— V4.7-B1。

把 Impeccable（github.com/pbakaus/impeccable，Apache-2.0）的"设计词汇 + 确定性反模式检测"
这一范式本地化成本仓可运行、可自检、可扩展的纯标准库实现。

边界（与仓内红线一致）：
- 不 vendor 上游引擎，不复制上游代码；只沿用"24 个命令 / 确定性规则 / P0–P3 分级"这套范式，规则实现为本仓自写。
- 不调 LLM、不出网、不读凭证；所有判定由确定性文本规则给出。
- 旁挂：不改变 25 智能体 / 47 技能 / 9 域包，不改 diff0/tamper 指纹，不动 extension_slots.json 的 12 条声明。
"""

from .vocabulary import COMMANDS, GROUPS, command_ids, by_group
from .detectors import RULES, Finding, scan
from .compile_modes import COMPILE_MODES, elaborate, simulate, netlist
from .hebbian import cooccurrence, normalize, similarity
from .meridian import CHANNELS, route

__all__ = [
    "COMMANDS",
    "GROUPS",
    "command_ids",
    "by_group",
    "RULES",
    "Finding",
    "scan",
    "COMPILE_MODES",
    "elaborate",
    "simulate",
    "netlist",
    "cooccurrence",
    "normalize",
    "similarity",
    "CHANNELS",
    "route",
]
