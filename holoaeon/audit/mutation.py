# -*- coding: utf-8 -*-
"""
VERAX · 自动篡改自检（mutation）
================================================================================
V2 / W7。把"被动两次跑一致"抬升为"主动改一个字、断言哈希必变"：
  给定一条回执，随机（但可复现的种子）挑 N 个 ReproCore 叶子字段做单点篡改，
  每改一处必须得到不同的 ReproHash；任何一处未变即判定"敏感性失效"。

为什么单独成模块而不是塞进测试：
  - 脚本 verax_verify.py --mutate N 与 tests/verax/test_mutation_selftest.py 共用同一实现；
  - 种子固定，同一回执同一 N 必得同一批篡改点，可复算；
  - 只读：篡改发生在深拷贝上，原回执不动。

保护哪条立身原则：确定性（哈希真的对内容敏感，不是恒真空转）。
"""
from __future__ import annotations

import copy
import random
from typing import Any, Dict, List, Optional, Tuple

from .fields import canonicalize, reprohash

SEED_DEFAULT = 20261101
DEFAULT_N = 5


# ------------------------------------------------------------ 叶子路径
def _walk(node: Any, path: Tuple[str, ...], out: List[Tuple[str, ...]]) -> None:
    if isinstance(node, dict):
        for key in node:
            _walk(node[key], path + (str(key),), out)
        return
    if isinstance(node, list):
        for idx, item in enumerate(node):
            _walk(item, path + ("[%d]" % idx,), out)
        return
    out.append(path)


def leaf_paths(obj: Any) -> List[Tuple[str, ...]]:
    """规范对象上的全部标量叶子路径（含空对象本身）。"""
    out: List[Tuple[str, ...]] = []
    _walk(canonicalize(obj), (), out)
    return out


def path_text(path: Tuple[str, ...]) -> str:
    parts = []
    for seg in path:
        parts.append(seg if seg.startswith("[") else "." + seg)
    return "$" + "".join(parts)


# ------------------------------------------------------------ 单点篡改
def mutate_value(value: Any) -> Any:
    """把一个标量改成"确定不同"的另一个标量。"""
    if isinstance(value, bool):
        return not value
    if isinstance(value, int):
        return value + 1
    if isinstance(value, float):
        return round(value + 0.001, 6)
    if isinstance(value, str):
        return value + "·"
    if value is None:
        return "<mutated:null>"
    return "<mutated:%s>" % type(value).__name__


def _set_path(node: Any, path: Tuple[str, ...], value: Any) -> Any:
    head, rest = path[0], path[1:]
    if head.startswith("["):
        idx = int(head[1:-1])
        node[idx] = _set_path(node[idx], rest, value) if rest else value
        return node
    node[head] = _set_path(node[head], rest, value) if rest else value
    return node


def apply_mutation(obj: Any, path: Tuple[str, ...]) -> Any:
    """在深拷贝上篡改一处，返回新对象（原对象不动）。"""
    core = copy.deepcopy(canonicalize(obj))
    if not path:
        return mutate_value(core)
    target = _get_path(core, path)
    _set_path(core, path, mutate_value(target))
    return core


def _get_path(node: Any, path: Tuple[str, ...]) -> Any:
    for seg in path:
        if seg.startswith("["):
            node = node[int(seg[1:-1])]
        else:
            node = node[seg]
    return node


# ------------------------------------------------------------ 自检入口
def mutate_selftest(obj: Any, n: int = DEFAULT_N,
                    seed: int = SEED_DEFAULT) -> Dict[str, Any]:
    """随机取 n 个叶子单点篡改，逐点比对哈希。

    返回 {"mutations": n, "changed": k, "sensitive": bool, "base_hash": ...,
           "details": [{path, golden, observed, changed}]}
    """
    base = obj
    base_hash = reprohash(base)
    paths = leaf_paths(base)
    want = max(0, min(int(n), len(paths)))
    rng = random.Random(seed)
    picked = sorted(rng.sample(list(range(len(paths))), want)) if want else []

    details: List[Dict[str, Any]] = []
    changed = 0
    for idx in picked:
        path = paths[idx]
        mutated = apply_mutation(base, path)
        observed = reprohash(mutated)
        hit = bool(observed != base_hash)
        changed += 1 if hit else 0
        details.append({"path": path_text(path),
                        "golden": base_hash,
                        "observed": observed,
                        "changed": hit})

    sensitive = bool(want > 0 and changed == want)
    return {"mutations": want, "changed": changed, "sensitive": sensitive,
            "base_hash": base_hash, "seed": int(seed), "details": details}
