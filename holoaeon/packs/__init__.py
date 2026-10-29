# -*- coding: utf-8 -*-
"""HoloAeon 九大领域包注册表 + 横切扩展包（第十：认知主权；第十一：SD-Distill；第十二：全域生活）。"""
from __future__ import annotations

from typing import Dict, List

from .base import DomainPack
from .business import BusinessPack
from .data import DataPack
from .gaoyi_pack import GaoyiPack
from .growth import GrowthPack
from .literature import LiteraturePack
from .optimization import OptimizationPack
from .quant import QuantPack
from .research import ResearchPack
from .sovereignty_pack import SovereigntyPack
from .omnicore_pack import OmniCorePack
from .omnilife_pack import OmniLifePack
from .subdistill_pack import SubdistillPack
from .writing import WritingPack

# 九大领域包（每次调用返回新实例，避免共享状态）
PACK_REGISTRY: Dict[str, type] = {
    WritingPack.key: WritingPack,
    LiteraturePack.key: LiteraturePack,
    ResearchPack.key: ResearchPack,
    DataPack.key: DataPack,
    GrowthPack.key: GrowthPack,
    BusinessPack.key: BusinessPack,
    QuantPack.key: QuantPack,
    OptimizationPack.key: OptimizationPack,
    GaoyiPack.key: GaoyiPack,
}

PACK_ORDER: List[str] = [
    "writing", "literature", "research", "data",
    "growth", "business", "quant", "optimization", "gaoyi",
]


def get_pack(key: str) -> DomainPack:
    if key not in PACK_REGISTRY:
        raise KeyError(f"未知领域包：{key}，可选：{PACK_ORDER}")
    return PACK_REGISTRY[key]()


def all_packs() -> List[DomainPack]:
    return [PACK_REGISTRY[k]() for k in PACK_ORDER]


# ------------------------------------------------------------------------------------
# 横切扩展包（第十包起）：**不进 PACK_ORDER**，故不改变 G15 的 n_agents==25 / n_skills==47
# 断言；由 G18 / G19 / G20 分别验证，也可显式 get_extra_pack(key) 取用。
# ------------------------------------------------------------------------------------
EXTRA_PACK_REGISTRY: Dict[str, type] = {
    SovereigntyPack.key: SovereigntyPack,
    SubdistillPack.key: SubdistillPack,
    OmniLifePack.key: OmniLifePack,
    OmniCorePack.key: OmniCorePack,
}

EXTRA_PACK_ORDER: List[str] = ["sovereignty", "subdistill", "omnilife", "omnicore"]


def get_extra_pack(key: str) -> DomainPack:
    if key not in EXTRA_PACK_REGISTRY:
        raise KeyError(f"未知扩展包：{key}，可选：{EXTRA_PACK_ORDER}")
    return EXTRA_PACK_REGISTRY[key]()


def all_extra_packs() -> List[DomainPack]:
    return [EXTRA_PACK_REGISTRY[k]() for k in EXTRA_PACK_ORDER]
