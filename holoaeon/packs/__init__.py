# -*- coding: utf-8 -*-
"""HoloAeon 八大领域包注册表。"""
from __future__ import annotations

from typing import Dict, List

from .base import DomainPack
from .business import BusinessPack
from .data import DataPack
from .growth import GrowthPack
from .literature import LiteraturePack
from .optimization import OptimizationPack
from .quant import QuantPack
from .research import ResearchPack
from .writing import WritingPack

# 八大领域包（每次调用返回新实例，避免共享状态）
PACK_REGISTRY: Dict[str, type] = {
    WritingPack.key: WritingPack,
    LiteraturePack.key: LiteraturePack,
    ResearchPack.key: ResearchPack,
    DataPack.key: DataPack,
    GrowthPack.key: GrowthPack,
    BusinessPack.key: BusinessPack,
    QuantPack.key: QuantPack,
    OptimizationPack.key: OptimizationPack,
}

PACK_ORDER: List[str] = [
    "writing", "literature", "research", "data",
    "growth", "business", "quant", "optimization",
]


def get_pack(key: str) -> DomainPack:
    if key not in PACK_REGISTRY:
        raise KeyError(f"未知领域包：{key}，可选：{PACK_ORDER}")
    return PACK_REGISTRY[key]()


def all_packs() -> List[DomainPack]:
    return [PACK_REGISTRY[k]() for k in PACK_ORDER]
