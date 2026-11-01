# -*- coding: utf-8 -*-
"""
skill_matrix.mech —— 六机制确定性内核（全息心跳 / 细胞骨架 / 皮肤 / 语义通信 / 赫布场 / 经络）
================================================================================
设计纪律：
  · 纯标准库、零依赖、离线可跑、无随机源；
  · 同输入同输出（同一进程内两次调用逐字相等，跨进程仅依赖有序集合）；
  · 只做结构与调度，不执行任何外部技能脚本，不联网，不写盘（由调用方决定落盘）。
"""
from __future__ import annotations

import hashlib
import math
from typing import Any, Dict, Iterable, List, Sequence, Tuple

DIM = 768                                   # 与仓库既有 hypervector 维度一致
MECHANISMS: Tuple[str, ...] = (
    "holographic_heartbeat",                # 全息心跳
    "cytoskeleton",                         # 细胞骨架
    "skin_v6",                              # 皮肤 SG-SKIN-V6.0 八层
    "semantic_bus",                         # 语义通信底座
    "hebbian_field",                        # 赫布协作场
    "meridian",                             # 经络机制
)
MECH_CN = {
    "holographic_heartbeat": "全息心跳",
    "cytoskeleton": "细胞骨架",
    "skin_v6": "皮肤八层",
    "semantic_bus": "语义通信底座",
    "hebbian_field": "赫布协作场",
    "meridian": "经络机制",
}


# ============================================================ 0. 基础向量运算
def node_vector(name: str, dim: int = DIM) -> List[int]:
    """节点双极向量：SHAKE-256 一次性展开 dim 字节，奇偶映射到 ±1。"""
    raw = hashlib.shake_256(name.encode("utf-8")).digest(dim)
    return [1 if b & 1 else -1 for b in raw]


def bundle(vectors: Sequence[Sequence[int]]) -> List[int]:
    """叠加（bundle）：逐位求和后取符号，0 归 +1，保证确定性。"""
    if not vectors:
        return [1] * DIM
    acc = [0] * len(vectors[0])
    for v in vectors:
        for i, b in enumerate(v):
            acc[i] += b
    return [1 if x >= 0 else -1 for x in acc]


def cosine(a: Sequence[int], b: Sequence[int]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return round(dot / (na * nb), 5)


def fingerprint(vec: Sequence[int]) -> str:
    bits = bytes(1 if x > 0 else 0 for x in vec)
    return hashlib.sha256(bits).hexdigest()[:16]


# ============================================================ 1. 全息心跳
def heartbeat(names: Iterable[str], dim: int = DIM) -> dict:
    """一拍心跳：每节点相位 + 全量叠加签名。

    相位 = 节点在有序名单里的位次 % 12（对应十二经络次序，便于与经络机制对齐）。
    全息性：任取子集叠加仍与全量签名高度相关，故"残缺即部分可读"可复算。
    """
    ordered = sorted(names)
    vecs = [node_vector(n, dim) for n in ordered]
    sig_vec = bundle(vecs)
    beats = []
    for i, (n, v) in enumerate(zip(ordered, vecs)):
        beats.append({"node": n, "phase": i % 12, "pulse": sum(v[:16])})
    return {"nodes": len(ordered), "beats": beats,
            "signature": fingerprint(sig_vec), "dim": dim}


def hologram_residual(names: Iterable[str], keep: int, dim: int = DIM) -> dict:
    """全息残差：留 keep 个节点的叠加 vs 全量叠加的余弦，用于验证"越全越清晰"。"""
    ordered = sorted(names)
    full = bundle([node_vector(n, dim) for n in ordered])
    part = bundle([node_vector(n, dim) for n in ordered[:max(1, keep)]])
    return {"kept": max(1, keep), "total": len(ordered),
            "cosine": cosine(part, full), "signature": fingerprint(part)}


# ============================================================ 2. 细胞骨架
def build_skeleton(edges: Iterable[Tuple[str, str, float]]) -> dict:
    """骨架装配：节点度、载荷、主干（按度降序）。"""
    deg: Dict[str, int] = {}
    load: Dict[str, float] = {}
    uniq = {}
    for a, b, w in edges:
        if a == b:
            continue
        key = tuple(sorted((a, b)))
        uniq[key] = round(max(uniq.get(key, 0.0), float(w)), 5)
        deg[a] = deg.get(a, 0) + 1
        deg[b] = deg.get(b, 0) + 1
        load[a] = load.get(a, 0.0) + float(w)
        load[b] = load.get(b, 0.0) + float(w)
    nodes = sorted(deg)
    backbone = sorted(nodes, key=lambda n: (-deg[n], n))[:8]
    return {"nodes": len(nodes), "edges": len(uniq),
            "degree": {n: deg[n] for n in nodes},
            "load": {n: round(load[n], 5) for n in nodes},
            "backbone": backbone,
            "max_degree": max(deg.values()) if deg else 0}


def _components(nodes: List[str], edges: Dict[Tuple[str, str], float], removed: str) -> int:
    alive = [n for n in nodes if n != removed]
    adj: Dict[str, List[str]] = {n: [] for n in alive}
    for (a, b) in edges:
        if a == removed or b == removed:
            continue
        adj[a].append(b)
        adj[b].append(a)
    seen, comps = set(), 0
    for n in alive:
        if n in seen:
            continue
        comps += 1
        stack = [n]
        while stack:
            cur = stack.pop()
            if cur in seen:
                continue
            seen.add(cur)
            stack.extend(x for x in adj[cur] if x not in seen)
    return comps


def skeleton_robustness(edges: Iterable[Tuple[str, str, float]]) -> dict:
    """骨架鲁棒性：逐个抽掉节点，统计连通分量增量与最大连通占比。"""
    pairs = {(a, b): float(w) for a, b, w in edges if a != b}
    nodes = sorted({x for pair in pairs for x in pair})
    base = _components(nodes, pairs, "")
    rows = []
    for n in nodes:
        rows.append({"removed": n, "components": _components(nodes, pairs, n),
                     "delta": _components(nodes, pairs, n) - base})
    worst = sorted(rows, key=lambda r: (-r["delta"], r["removed"])[:2])
    return {"nodes": len(nodes), "base_components": base,
            "worst": worst[:3], "stable": all(r["delta"] <= 1 for r in rows)}


# ============================================================ 3. 皮肤 SG-SKIN-V6.0
SKIN_LAYERS: Tuple[str, ...] = (
    "L1_parse", "L2_normalize", "L3_schema", "L4_policy",
    "L5_redline", "L6_budget", "L7_audit", "L8_seal",
)
REDLINE_TOKENS: Tuple[str, ...] = (
    "os.system", "subprocess", "eval(", "exec(", "rm -rf", "cmd /c",
    "requests.get", "socket", "base64.b64decode", "pickle.loads",
)
_REQUIRED = ("query", "lane")


def skin_gate(req: Dict[str, Any], budget: int = 64) -> dict:
    """八层皮肤：逐层判定，任一层失败即拒绝并给出层名与原因（fail-closed）。"""
    trace: List[Dict[str, Any]] = []
    ctx: Dict[str, Any] = {"budget": budget, "cost": 0, "audit": []}

    def layer(name: str, ok: bool, reason: str = "") -> bool:
        trace.append({"layer": name, "ok": bool(ok), "reason": reason})
        return bool(ok)

    # L1 解析
    if not layer("L1_parse", isinstance(req, dict) and bool(req), "请求必须是非空 dict"):
        return {"verdict": "REJECT", "layer": "L1_parse", "trace": trace}
    # L2 归一化（去控制字符、裁长度）
    q = str(req.get("query", ""))
    q = "".join(ch for ch in q if ch.isprintable()).strip()[:512]
    ctx["query"] = q
    if not layer("L2_normalize", bool(q), "query 归一化后为空"):
        return {"verdict": "REJECT", "layer": "L2_normalize", "trace": trace}
    # L3 结构
    missing = [k for k in _REQUIRED if k not in req]
    if not layer("L3_schema", not missing, "缺字段 %s" % missing):
        return {"verdict": "REJECT", "layer": "L3_schema", "trace": trace}
    # L4 权限
    perm = int(req.get("permission", 0))
    if not layer("L4_policy", 0 <= perm <= 2, "permission=%s 超出只读/受限档" % perm):
        return {"verdict": "REJECT", "layer": "L4_policy", "trace": trace}
    # L5 红线
    hit = [t for t in REDLINE_TOKENS if t in q.lower()]
    if not layer("L5_redline", not hit, "命中红线 %s" % hit):
        return {"verdict": "REJECT", "layer": "L5_redline", "trace": trace}
    # L6 预算
    cost = max(1, len(q) // 32 + 1)
    ctx["cost"] = cost
    if not layer("L6_budget", cost <= ctx["budget"], "cost=%d > budget=%d" % (cost, ctx["budget"])):
        return {"verdict": "REJECT", "layer": "L6_budget", "trace": trace}
    # L7 留痕
    rec = hashlib.sha256((q + "|" + str(cost)).encode("utf-8")).hexdigest()[:16]
    ctx["audit"].append(rec)
    layer("L7_audit", True, rec)
    # L8 封缄
    seal = hashlib.sha256(("|".join(ctx["audit"]) + "|" + str(len(trace))).encode("utf-8")).hexdigest()[:16]
    layer("L8_seal", True, seal)
    return {"verdict": "PASS", "layer": "L8_seal", "trace": trace,
            "seal": seal, "cost": cost, "query": q}


# ============================================================ 4. 语义通信底座
def shingles(text: str, sizes: Sequence[int] = (2, 3, 4)) -> set:
    """中文无分词场景字符滑窗；英文按空白切词也纳入，保证中英混排都能区分。"""
    norm = "".join(text.lower().split())
    out = set()
    for n in sizes:
        for i in range(max(0, len(norm) - n + 1)):
            out.add(norm[i:i + n])
    for tok in text.lower().split():
        if tok:
            out.add("<" + tok + ">")
    return out


def text_signature(text: str) -> str:
    sh = sorted(shingles(text))
    return hashlib.sha256("|".join(sh).encode("utf-8")).hexdigest()[:16]


def semantic_overlap(a: str, b: str) -> float:
    sa, sb = shingles(a), shingles(b)
    if not sa or not sb:
        return 0.0
    return round(len(sa & sb) / len(sa | sb), 5)


def encode(topic: str, payload: Dict[str, Any]) -> dict:
    return {"topic": topic, "fp": text_signature(topic + "|" + repr(sorted(payload.items()))),
            "payload": payload, "bus": "HOLOAEON-BUS-v1.0"}


def decode(env: dict) -> dict:
    expect = text_signature(env["topic"] + "|" + repr(sorted(env["payload"].items())))
    return {"ok": expect == env["fp"], "payload": env["payload"] if expect == env["fp"] else None}


def route(query: str, families: Iterable[str]) -> dict:
    """按语义重叠把查询落到技能族（同分按族名排序，确定性）。"""
    scored = [(f, semantic_overlap(query, f)) for f in families]
    scored.sort(key=lambda t: (-t[1], t[0]))
    return {"query": query, "family": scored[0][0] if scored else None,
            "score": scored[0][1] if scored else 0.0,
            "top3": scored[:3]}


# ============================================================ 5. 赫布协作场
class HebbianField:
    """共激活强化 + 衰减：w += delta·(1-w) 收敛于 1，衰减按比例回落。"""

    def __init__(self, decay: float = 0.02) -> None:
        self.decay = float(decay)
        self._w: Dict[Tuple[str, str], float] = {}

    @staticmethod
    def _key(a: str, b: str) -> Tuple[str, str]:
        return (a, b) if a <= b else (b, a)

    def weight(self, a: str, b: str) -> float:
        return round(self._w.get(self._key(a, b), 0.0), 5)

    def co_activate(self, a: str, b: str, delta: float = 1.0) -> float:
        if a == b:
            return self.weight(a, b)
        k = self._key(a, b)
        w = self._w.get(k, 0.0)
        w = w + float(delta) * (0.99 - w)
        self._w[k] = round(min(0.99, w), 5)
        return round(self._w[k], 5)

    def decay_all(self) -> int:
        for k in list(self._w):
            v = self._w[k] * (1.0 - self.decay)
            if v < 0.01:
                del self._w[k]
            else:
                self._w[k] = round(v, 5)
        return len(self._w)

    def neighbors(self, node: str, k: int = 3) -> List[Tuple[str, float]]:
        rows = []
        for (a, b), w in self._w.items():
            if a == node:
                rows.append((b, w))
            elif b == node:
                rows.append((a, w))
        rows.sort(key=lambda t: (-t[1], t[0]))
        return rows[:k]

    def path(self, a: str, b: str) -> dict:
        """最短路（边代价 = 1/权重），Dijkstra 简化版。"""
        if a == b:
            return {"path": [a], "cost": 0.0}
        adj: Dict[str, List[Tuple[str, float]]] = {}
        for (x, y), w in self._w.items():
            c = 1.0 / max(w, 1e-6)
            adj.setdefault(x, []).append((y, c))
            adj.setdefault(y, []).append((x, c))
        dist = {a: 0.0}
        prev: Dict[str, str] = {}
        done = set()
        frontier = [a]
        while frontier:
            cur = min(frontier, key=lambda n: dist.get(n, float("inf")))
            frontier.remove(cur)
            if cur in done:
                continue
            done.add(cur)
            if cur == b:
                break
            for nxt, c in adj.get(cur, []):
                nd = dist[cur] + c
                if nd < dist.get(nxt, float("inf")):
                    dist[nxt] = nd
                    prev[nxt] = cur
                    frontier.append(nxt)
        if b not in dist:
            return {"path": [], "cost": None}
        path = [b]
        while path[-1] != a:
            path.append(prev[path[-1]])
        return {"path": list(reversed(path)), "cost": round(dist[b], 5)}


# ============================================================ 6. 经络机制
CHANNELS: Tuple[str, ...] = tuple("LC%02d" % i for i in range(1, 13))


class Meridian:
    """十二正经：每条一条气血预算通道，流量分配 + 淤堵检测 + 再平衡。"""

    def __init__(self, budget: int = 100) -> None:
        self.capacity = int(budget)
        self.used: Dict[str, int] = {c: 0 for c in CHANNELS}
        self.flowed: Dict[str, int] = {c: 0 for c in CHANNELS}

    def flow(self, channel: str, amount: int = 1) -> dict:
        if channel not in self.used:
            return {"ok": False, "reason": "未知经络 %s" % channel}
        nxt = self.used[channel] + int(amount)
        if nxt > self.capacity:
            return {"ok": False, "channel": channel, "reason": "本经预算耗尽",
                    "used": self.used[channel], "capacity": self.capacity}
        self.used[channel] = nxt
        self.flowed[channel] += 1
        return {"ok": True, "channel": channel, "used": nxt, "capacity": self.capacity}

    def blocked(self, threshold: float = 0.85) -> List[str]:
        return sorted(c for c in CHANNELS if self.used[c] >= self.capacity * threshold)

    def balance(self) -> dict:
        """把富余经络（<50%）的余量匀给最淤堵的两条，单次最多各 10。"""
        rich = [c for c in CHANNELS if self.used[c] < self.capacity * 0.5]
        poor = sorted(CHANNELS, key=lambda c: (-self.used[c], c))[:2]
        moved = {}
        for target in poor:
            need = self.capacity - self.used[target]
            for src in rich:
                free = int(self.capacity * 0.5) - self.used[src]
                if free <= 0:
                    continue
                take = min(free, need, 10)
                if take > 0:
                    self.used[src] += take
                    self.used[target] += take
                    moved[target] = moved.get(target, 0) + take
                    need -= take
                if need <= 0:
                    break
        return {"moved": moved, "blocked": self.blocked()}

    def report(self) -> dict:
        return {"channels": len(CHANNELS), "capacity": self.capacity,
                "load": {c: self.used[c] for c in CHANNELS},
                "blocked": self.blocked()}
