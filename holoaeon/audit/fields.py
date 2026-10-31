# -*- coding: utf-8 -*-
"""
VERAX · 字段分类与规范化（fields）
================================================================================
把"可复现核心（ReproCore）"与"物理量（Physical）"分开，再对 ReproCore
生成稳定的 ReproHash。纯标准库、只读、不改变任何裁决。

保护哪条立身原则：确定性（同一逻辑回执必得同一哈希）、可审计（字段分类表可查）。
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Tuple

# ------------------------------------------------------------ 字段分类表
# 物理量：本就该每次不同，剔除后不参与比对
PHYSICAL_KEYS = {
    "ts", "timestamp", "elapsed", "duration", "started_at", "finished_at",
    "thread_order", "addr", "pid", "uptime_s", "measure_ts", "id_instance",
}

# 可复现核心：裁决、路由、命中技能、技能输出等
REPRO_KEYS = {
    "runtime_id", "task", "targets", "results", "all_ok", "agent_id", "role",
    "input", "status", "matched", "err", "verdict", "action", "layer",
    "reason_code", "reason", "reasons", "matched_pattern", "summary",
    "message_id", "conversation", "sender", "receiver", "topic", "trace",
    "skill", "count", "files_scanned", "violations", "clean",
    # 自证报告 schema（VERAX 产出自身的字段，必须在表内，否则会被当物理量剔除）
    "gid", "name", "conclusion", "checks", "repro", "honesty", "redline",
    "unknown_fields", "verdict", "verdict_hash", "reprohash", "runs",
    "golden_match", "stable", "reprohash_list", "repro_hash_stable",
    "evidence_class", "diff_physical", "diff_reprocore",
    # 公开基准 workload 轨迹（bench_public 的 16 步 trace，必须在表内，
    # 否则整条 trace 会被当未知字段剔除，DIFF=0 变成恒真空转）
    "steps", "step", "value", "tick", "active", "degraded", "idle",
    "faults", "watch_count", "bodies", "seq", "window",
    # 内核健康快照（kernel.health）
    "agents", "blocked", "guard", "has_adapter", "has_graph", "memory",
    "scheduler", "skills", "submitted",
}

# 不透明载荷：技能输出的内部结构由技能自己声明，原样参与序列化
OPAQUE_KEYS = {"output", "payload", "evidence", "reprocore", "physical"}

CLASS_TABLE = {
    "physical": sorted(PHYSICAL_KEYS),
    "repro": sorted(REPRO_KEYS),
    "opaque": sorted(OPAQUE_KEYS),
}


def classify(key: str) -> str:
    """返回 physical / repro / unknown。"""
    if key in PHYSICAL_KEYS:
        return "physical"
    if key in REPRO_KEYS or key in OPAQUE_KEYS:
        return "repro"
    return "unknown"


def _walk(node: Any, path: str, unknown: List[str],
          opaque: bool = False) -> Any:
    if opaque:
        return node
    if isinstance(node, dict):
        out: Dict[str, Any] = {}
        for key, value in node.items():
            cls = classify(str(key))
            child = "%s.%s" % (path, key)
            if cls == "physical":
                continue
            if cls == "unknown":
                # 未登记字段默认按物理量处理，并显式记录，绝不静默丢弃
                unknown.append(child)
                continue
            out[key] = _walk(value, child, unknown, key in OPAQUE_KEYS)
        return out
    if isinstance(node, (list, tuple)):
        items = [_walk(v, "%s[%d]" % (path, i), unknown, False)
                 for i, v in enumerate(node)]
        # 列表内全是 dict 时按规范文本稳定排序：解决线程完成序不可复现
        if items and all(isinstance(x, dict) for x in items):
            items.sort(key=lambda x: canonical_json(x))
        return items
    if isinstance(node, float):
        if node != node:            # NaN
            return "NaN"
        if node == float("inf"):
            return "Infinity"
        if node == float("-inf"):
            return "-Infinity"
        if node == 0.0:
            return 0.0              # 去掉 -0.0
        return node
    return node


def canonicalize(obj: Any) -> Any:
    """剔除物理量、稳定排序列表，返回可序列化的规范对象。"""
    known: List[str] = []
    return _walk(obj, "$", known)


def canonicalize_report(obj: Any) -> Tuple[Any, List[str]]:
    """返回 (规范对象, 未登记字段路径列表)。"""
    unknown: List[str] = []
    return _walk(obj, "$", unknown), unknown


def canonical_json(obj: Any) -> str:
    """规范 JSON 文本：键升序、UTF-8 原样、非 JSON 值转字符串。"""
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, default=str)


def reprohash(obj: Any, length: int = 16) -> str:
    """ReproHash = sha256(canonical_json(canonicalize(obj)))[:16]。"""
    return hashlib.sha256(
        canonical_json(canonicalize(obj)).encode("utf-8")
    ).hexdigest()[:length]


def split_physical(obj: Dict[str, Any]) -> Dict[str, Any]:
    """把物理量单独快照出来（仅供展示，不进 ReproHash）。"""
    physical: Dict[str, Any] = {}

    def _collect(node: Any, path: str) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                child = "%s.%s" % (path, key)
                if classify(str(key)) == "physical":
                    physical[child] = value
                else:
                    _collect(value, child)
        elif isinstance(node, list):
            for i, value in enumerate(node):
                _collect(value, "%s[%d]" % (path, i))

    _collect(obj, "$")
    return physical
