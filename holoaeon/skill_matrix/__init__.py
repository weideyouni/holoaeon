# -*- coding: utf-8 -*-
"""skill_matrix —— 全量技能矩阵旁挂包（六机制 + 全量索引 + 跨线程运行时）。"""
from __future__ import annotations

import os
from typing import Iterable, List

MATRIX_ID = "SG-MATRIX-SKILL-HOLOAEON-V3.0"
DEFAULT_INDEX = os.path.join("data", "skill_matrix_index.json")

_DEFAULT_ROOTS = (
    os.path.join(os.path.expanduser("~"), "AppData", "Local", "DoubaoWork", "User Data",
                 "Default", ".doubaowork", "agent_mode", "workspace", ".skills"),
    os.path.join(os.path.expanduser("~"), "AppData", "Local", "DoubaoWork", "User Data",
                 "Default", ".doubaowork", "agent_mode", "workspace", ".user_skills"),
    os.path.join(os.path.expanduser("~"), "DoubaoWork", "skills"),
    os.path.join(os.path.expanduser("~"), ".agents", "skills"),
    os.path.join("F:" + os.sep, "doubaowork", ".agents", "skills"),
)


def default_roots() -> List[str]:
    """返回当前机器上真实存在的默认技能根目录（不存在的自动剔除）。"""
    return [r for r in _DEFAULT_ROOTS if os.path.isdir(r)]


from .mech import (CHANNELS, DIM, MECH_CN, MECHANISMS, HebbianField, Meridian,  # noqa: E402
                   build_skeleton, bundle, cosine, decode, encode, fingerprint,
                   heartbeat, hologram_residual, node_vector, route, semantic_overlap,
                   shingles, skeleton_robustness, skin_gate, text_signature)
from . import index as skill_index  # noqa: E402
from .runtime import MatrixRuntime, load_runtime  # noqa: E402

__all__ = [
    "MATRIX_ID", "DIM", "MECHANISMS", "MECH_CN", "CHANNELS",
    "node_vector", "bundle", "cosine", "fingerprint", "heartbeat", "hologram_residual",
    "build_skeleton", "skeleton_robustness", "skin_gate",
    "shingles", "text_signature", "semantic_overlap", "encode", "decode", "route",
    "HebbianField", "Meridian", "MatrixRuntime", "load_runtime",
    "skill_index", "default_roots", "DEFAULT_INDEX",
]
