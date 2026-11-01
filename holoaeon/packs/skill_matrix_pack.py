# -*- coding: utf-8 -*-
"""
SkillMatrixPack —— 全量技能矩阵旁挂扩展包（第 9 个扩展包，不进 PACK_ORDER）
================================================================================
把"以往全部豆包 Work 技能 × HoloAeon 六机制"的整合成果，变成内裤里可直接调用的
六个确定性技能：status / query / dispatch / mechanism / quartet / baseline。

维度不变：本包只进 EXTRA_PACK_REGISTRY，不进 PACK_ORDER，
故 A1 断言（agents==25 / skills==47 / packs==9）不受影响。
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

from .base import DomainPack, RoleSpec, SkillSpec, WorkflowSpec

_PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # holoaeon/../ = 仓库根
_ROOT = os.path.dirname(_PKG)
INDEX_PATH = os.path.join(_ROOT, "data", "skill_matrix_index.json")
BASELINE_PATH = os.path.join(_ROOT, "data", "skill_matrix_baseline.json")

_CACHE: Dict[str, Any] = {"rt": None}


def get_runtime(rebuild: bool = False):
    """懒加载运行时：优先读落盘索引；无则现场扫默认技能根（不落盘）。"""
    if _CACHE["rt"] is not None and not rebuild:
        return _CACHE["rt"]
    from ..skill_matrix import MatrixRuntime, default_roots, skill_index
    idx = None if rebuild else skill_index.load(INDEX_PATH)
    if idx is None:
        roots = default_roots()
        idx = skill_index.build(roots)
    _CACHE["rt"] = MatrixRuntime(idx)
    return _CACHE["rt"]


# ---------------------------------------------------------------- 六技能实现
def skill_matrix_status(_q: str = "", **_: Any) -> dict:
    rt = get_runtime()
    return {"matrix_id": "SG-MATRIX-SKILL-HOLOAEON-V3.0",
            "index": {"digest": rt.index.get("digest"), "count": rt.index.get("count"),
                      "roots": len(rt.index.get("roots", []))},
            "stats": rt.status()["stats"],
            "runtime": {"calls": rt.calls, "hebbian_edges": rt.status()["hebbian_edges"],
                        "blocked_channels": rt.status()["meridian"]["blocked"]},
            "mechanisms": list(rt.index.get("stats", {}).get("by_mechanism", {}).keys())}


def skill_matrix_query(query: str = "", top: int = 3, **_: Any) -> dict:
    rt = get_runtime()
    from ..skill_matrix import semantic_overlap
    rows = [(r["name"], semantic_overlap(query or "", r["name"] + " " + r["description"]),
             r["mechanism"], r["domain"]) for r in rt.rows.values()]
    rows.sort(key=lambda t: (-t[1], t[0]))
    return {"query": query, "hits": [{"skill": n, "score": s, "mechanism": m, "domain": d}
                                     for n, s, m, d in rows[:max(1, int(top))]]}


def skill_matrix_dispatch(query: str = "", lane: str = "read", permission: int = 0,
                          **_: Any) -> dict:
    return get_runtime().dispatch(query or "", lane=lane, permission=int(permission))


def skill_matrix_mechanism(name: str = "holographic_heartbeat", n: int = 24, **_: Any) -> dict:
    from ..skill_matrix import (Meridian, HebbianField, build_skeleton, decode, encode,
                               heartbeat, hologram_residual, node_vector, skin_gate,
                               skeleton_robustness)
    if name == "holographic_heartbeat":
        nodes = ["N%02d" % i for i in range(int(n))]
        hb = heartbeat(nodes)
        return {"mechanism": name, "nodes": hb["nodes"], "signature": hb["signature"],
                "residuals": [hologram_residual(nodes, k) for k in (4, 8, 16, 24 if n >= 24 else n)]}
    if name == "cytoskeleton":
        nodes = ["N%02d" % i for i in range(int(n))]
        edges = [(nodes[i], nodes[(i + 1) % len(nodes)], 1.0) for i in range(len(nodes))]
        edges.append((nodes[0], nodes[len(nodes) // 2], 1.0))
        return {"mechanism": name, "skeleton": build_skeleton(edges),
                "robustness": skeleton_robustness(edges)}
    if name == "skin_v6":
        return {"mechanism": name,
                "pass": skin_gate({"query": "统计这周的销售额", "lane": "read"}),
                "reject": skin_gate({"query": "os.system('x')", "lane": "read"})}
    if name == "semantic_bus":
        env = encode("语义通信底座", {"n": 3})
        return {"mechanism": name, "envelope": env, "decode": decode(env)}
    if name == "hebbian_field":
        f = HebbianField()
        for a, b in (("A", "B"), ("B", "C"), ("A", "C")):
            f.co_activate(a, b)
        return {"mechanism": name, "weight_ab": f.weight("A", "B"),
                "path": f.path("A", "C"), "neighbors_b": f.neighbors("B")}
    if name == "meridian":
        m = Meridian(budget=10)
        for _ in range(10):
            m.flow("LC03", 1)
        return {"mechanism": name, "overflow": m.flow("LC03", 1),
                "balance": m.balance(), "report": m.report()}
    return {"mechanism": name, "error": "未知机制"}


def skill_matrix_quartet(task: str = "", **_: Any) -> dict:
    return get_runtime().quartet_review(task or "")


def skill_matrix_baseline(_q: str = "", **_: Any) -> dict:
    if not os.path.isfile(BASELINE_PATH):
        return {"ok": False, "reason": "基座清单未生成，先跑 scripts/build_skill_matrix.py"}
    with open(BASELINE_PATH, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return {"ok": True, "baseline": data}


class SkillMatrixPack(DomainPack):
    key = "skill_matrix"
    name = "全量技能矩阵（六机制旁挂）"
    description = ("把以往全部豆包 Work 技能映射进六机制并跨线程可调："
                   "全息心跳 / 细胞骨架 / 皮肤八层 / 语义通信底座 / 赫布协作场 / 经络")

    skills = [
        SkillSpec("matrix_status", skill_matrix_status,
                  "技能矩阵总览：索引摘要、六机制归类、运行时调用数、经络淤堵",
                  tags=["matrix", "status"], inputs={}),
        SkillSpec("matrix_query", skill_matrix_query,
                  "在全量技能索引里按语义重叠检索候选技能（返回机制/领域归类）",
                  tags=["matrix", "retrieval"], inputs={"query": "str", "top": "int"}),
        SkillSpec("matrix_dispatch", skill_matrix_dispatch,
                  "一次调用走完 皮肤八层 → 语义路由 → 赫布强化 → 经络流量，返回带封缄回执",
                  tags=["matrix", "dispatch"], inputs={"query": "str", "lane": "str"}),
        SkillSpec("matrix_mechanism", skill_matrix_mechanism,
                  "单独演示某一机制（heartbeat/cytoskeleton/skin_v6/semantic_bus/hebbian_field/meridian）",
                  tags=["matrix", "mechanism"], inputs={"name": "str", "n": "int"}),
        SkillSpec("matrix_quartet", skill_matrix_quartet,
                  "四人组复核：探微/筑基/构弦/持衡四透镜对同一任务给出各自最相关机制与技能",
                  tags=["matrix", "quartet", "persona_quartet"], inputs={"task": "str"}),
        SkillSpec("matrix_baseline", skill_matrix_baseline,
                  "读取 F 盘以往项目汇总的基座化清单（旧工程 → 今日机制的挂载表）",
                  tags=["matrix", "baseline"], inputs={}),
    ]

    roles = [
        RoleSpec("matrix_lead", "技能矩阵总控：编排 query/dispatch/quartet", ["matrix_status", "matrix_dispatch", "matrix_quartet"]),
        RoleSpec("matrix_auditor", "矩阵审计：机制核对与基座清单校验", ["matrix_mechanism", "matrix_baseline", "matrix_query"]),
    ]

    workflows = [
        WorkflowSpec("skill_matrix_flow", ["matrix_lead", "matrix_auditor"],
                     "总控检索派发 → 审计核对机制与基线上报"),
    ]


def pack_summary() -> dict:
    p = SkillMatrixPack()
    return {"key": p.key, "skills": len(p.skills), "roles": len(p.roles),
            "workflows": len(p.workflows), "agents_created": len(p.roles),
            "index_path": INDEX_PATH, "baseline_path": BASELINE_PATH}
