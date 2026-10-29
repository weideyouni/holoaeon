# -*- coding: utf-8 -*-
"""
HoloAeon —— 零依赖、生物启发的通用多智能体认知框架
================================================================================
纯标准库、全离线、确定性。

快速开始：
    >>> from holoaeon import Kernel, Agent
    >>> k = Kernel()
    >>> k.skills.register_fn("echo", lambda task: "echo:" + task,
    ...                      description="echo the text")
    >>> k.register_agent(Agent("a1", "echoer"))
    >>> k.submit("hello")["results"][0]["output"]
    'echo:hello'
"""
from __future__ import annotations

from .agent import Agent
from .bus import Bus
from .envelope import Envelope
from .graph import AdaptiveGraph
from .guard import Guard
from .hypervector import HypervectorSpace
from .kernel import Kernel
from .memory import Memory
from .model_adapter import ModelAdapter
from .scheduler import Scheduler
from .skill import Skill, SkillRegistry
from .spec import (
    DEFAULT_CONFIG,
    HoloAeonConfig,
    MATRIX_ID,
    RUNTIME_ID,
    VERSION,
)

__all__ = [
    "Agent", "Bus", "Envelope", "AdaptiveGraph", "Guard",
    "HypervectorSpace", "Kernel", "Memory", "ModelAdapter",
    "Scheduler", "Skill", "SkillRegistry",
    "DEFAULT_CONFIG", "HoloAeonConfig", "MATRIX_ID", "RUNTIME_ID", "VERSION",
]

__version__ = VERSION
