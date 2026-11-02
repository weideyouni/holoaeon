"""赫布协作场：命中的共现权重与自组织相似性。

规则很朴素：同一批界面里反复一起出现的规则，就是"被同一个坏习惯绑在一起"的一组，
把它们连成有权边；反复迭代归一后，权重收敛、量纲稳定，可直接用于排序与聚类。

- 纯函数：同一批输入必得同一批权重。
- 无阈值魔法：权重就是共现次数除以文档数，可手算复核。
"""

from __future__ import annotations

import math
from typing import Dict, Iterable, List, Sequence, Set, Tuple


def _doc_sets(rule_sets: Iterable[Iterable[str]]) -> List[Set[str]]:
    return [set(x) for x in rule_sets]


def cooccurrence(rule_sets: Iterable[Iterable[str]]) -> Dict[Tuple[str, str], float]:
    """共现权重：(规则A, 规则B) → 同时出现的文档占比（A<B 保证无向边只存一份）。"""
    docs = _doc_sets(rule_sets)
    if not docs:
        return {}
    total = float(len(docs))
    counts: Dict[Tuple[str, str], int] = {}
    for d in docs:
        names = sorted(d)
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                key = (names[i], names[j])
                counts[key] = counts.get(key, 0) + 1
    return {k: v / total for k, v in sorted(counts.items())}


def normalize(weights: Dict[Tuple[str, str], float], rounds: int = 3) -> Dict[Tuple[str, str], float]:
    """按最大权归一到 [0,1]，迭代 rounds 次（确定性，用于把不同批次拉到同一量纲）。"""
    out = dict(weights)
    for _ in range(max(1, rounds)):
        if not out:
            return {}
        peak = max(out.values())
        if peak <= 0:
            return out
        out = {k: v / peak for k, v in out.items()}
    return {k: round(v, 6) for k, v in sorted(out.items())}


def _vector(node: str, weights: Dict[Tuple[str, str], float]) -> Dict[str, float]:
    vec: Dict[str, float] = {}
    for (a, b), w in weights.items():
        if a == node:
            vec[b] = vec.get(b, 0.0) + w
        elif b == node:
            vec[a] = vec.get(a, 0.0) + w
    return vec


def similarity(left: str, right: str, weights: Dict[Tuple[str, str], float]) -> float:
    """两节点在共现场里的余弦相似度；无共同邻居时为 0.0，自身为 1.0。"""
    if left == right:
        return 1.0
    va = _vector(left, weights)
    vb = _vector(right, weights)
    if not va or not vb:
        return 0.0
    common = set(va) & set(vb)
    if not common:
        return 0.0
    dot = sum(va[k] * vb[k] for k in common)
    na = math.sqrt(sum(v * v for v in va.values()))
    nb = math.sqrt(sum(v * v for v in vb.values()))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return round(dot / (na * nb), 6)


def neighbors(node: str, weights: Dict[Tuple[str, str], float], top: int = 3) -> List[Tuple[str, float]]:
    """取与某节点最强的若干邻居，同权按名称排序，保证输出稳定。"""
    vec = _vector(node, weights)
    return sorted(vec.items(), key=lambda kv: (-kv[1], kv[0]))[: max(0, top)]
