# -*- coding: utf-8 -*-
"""
AdaptiveGraph —— HoloAeon 自适应协作图（原"赫布协作场" + "runtime_graph"）
================================================================================
把逻辑矩阵的 agent 投影为一张【有向、带权、可学习】的协作图：

  · 几何     六边形（radius=2 → 19 圆：中心1+内6+外12），承载 n 个节点
  · 权重     几何相邻给基权，先验 FLOW_EDGES 给引导权，对称矩阵
  · 投影     agent_id ↔ 图节点（map_agent）
  · 路由     Dijkstra 加权最短路（引导路由）
  · 拥塞     节点负载 + fan-in 瓶颈识别（bottleneck）
  · 反馈环   DFS 三色检测有向环
  · 自组织   余弦相似性（节点状态趋同则相邻）
  · 自适应   赫布学习：共激活组内两两增强，全局衰减
  · 根因     沿最拥塞边反向追溯（root cause）

纯标准库、确定性。
"""
from __future__ import annotations

import heapq
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .spec import AdaptiveGraphConfig

# 六边形轴向方向
HEX_DIRS = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]


def hex_points(radius: int) -> List[Tuple[int, int]]:
    """radius 内所有六边形轴向坐标（含中心），按距离/角度确定性排序。"""
    pts = []
    for q in range(-radius, radius + 1):
        for r in range(-radius, radius + 1):
            s = -q - r
            if max(abs(q), abs(r), abs(s)) <= radius:
                pts.append((q, r))
    pts.sort(key=lambda p: (max(abs(p[0]), abs(p[1]), abs(-p[0] - p[1])),
                            math.atan2(p[1] + 0.5, p[0] + 0.5)))
    return pts


def hex_distance(a: Tuple[int, int], b: Tuple[int, int]) -> int:
    return (abs(a[0] - b[0]) + abs(a[1] - b[1])
            + abs(a[0] + a[1] - b[0] - b[1])) // 2


@dataclass
class GraphNode:
    nid: int
    name: str
    coord: Tuple[int, int]
    load: float = 0.0
    state: List[float] = field(default_factory=list)
    agent_id: Optional[str] = None

    def snapshot(self) -> dict:
        return {"id": self.nid, "name": self.name, "coord": list(self.coord),
                "load": round(self.load, 3), "agent": self.agent_id}


@dataclass
class AdaptiveGraph:
    """自适应协作图：几何 + 权重 + 路由 + 拥塞 + 反馈环 + 赫布学习。"""
    config: AdaptiveGraphConfig = field(default_factory=AdaptiveGraphConfig)
    node_names: Optional[List[str]] = None
    flow_edges: Optional[List[Tuple[int, int]]] = None

    def __post_init__(self) -> None:
        cfg = self.config
        positions = hex_points(cfg.geometry_radius)
        n = min(cfg.node_count, len(positions))
        names = self.node_names or [f"N{i:02d}" for i in range(n)]
        self.nodes: List[GraphNode] = [
            GraphNode(nid=i, name=names[i], coord=positions[i])
            for i in range(n)
        ]
        # 对称权重矩阵
        self.weights: List[List[float]] = [[0.0] * n for _ in range(n)]
        self._init_geometry_weights()
        self._init_flow_edges()
        self.agent_map: Dict[str, int] = {}

    # ------------------------------------------------------------ 权重初始化
    def _init_geometry_weights(self) -> None:
        for i, a in enumerate(self.nodes):
            for j, b in enumerate(self.nodes):
                if i != j and hex_distance(a.coord, b.coord) == 1:
                    self.weights[i][j] = 0.3
                    self.weights[j][i] = 0.3

    def _init_flow_edges(self) -> None:
        if not self.flow_edges:
            return
        for i, j in self.flow_edges:
            if 0 <= i < self.n and 0 <= j < self.n:
                self.weights[i][j] = 0.6
                self.weights[j][i] = 0.6

    @property
    def n(self) -> int:
        return len(self.nodes)

    # ------------------------------------------------------------ 投影
    def map_agent(self, agent_id: str, node: int) -> int:
        if not (0 <= node < self.n):
            raise ValueError(f"非法节点：{node}")
        self.agent_map[agent_id] = node
        self.nodes[node].agent_id = agent_id
        return node

    def node_of(self, agent_id: str) -> Optional[int]:
        return self.agent_map.get(agent_id)

    # ------------------------------------------------------------ 路由（Dijkstra）
    def neighbors(self, i: int) -> List[int]:
        return [j for j in range(self.n) if self.weights[i][j] > 0]

    def shortest_path(self, src: int, dst: int) -> Tuple[List[int], float]:
        """加权最短路（边代价 = 1 + (1-weight)，权重越高越优先）。"""
        dist = {src: 0.0}
        prev: Dict[int, int] = {}
        pq = [(0.0, src)]
        while pq:
            d, u = heapq.heappop(pq)
            if u == dst:
                break
            if d > dist.get(u, math.inf):
                continue
            for v in self.neighbors(u):
                cost = 1.0 + (1.0 - self.weights[u][v])
                nd = d + cost
                if nd < dist.get(v, math.inf):
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(pq, (nd, v))
        if dst not in dist:
            return [], math.inf
        path = [dst]
        while path[-1] != src:
            path.append(prev[path[-1]])
        path.reverse()
        return path, round(dist[dst], 4)

    # ------------------------------------------------------------ 拥塞 / 瓶颈
    def apply_load(self, loads: Dict[int, float]) -> None:
        for i, v in loads.items():
            if 0 <= i < self.n:
                self.nodes[i].load = max(0.0, min(1.0, v))

    def fan_in(self, node: int) -> int:
        return sum(1 for i in range(self.n) if self.weights[i][node] > 0)

    def bottleneck(self) -> dict:
        """fan-in 最多且负载最高的节点即瓶颈。"""
        best, best_score = -1, -1.0
        for i in range(self.n):
            score = self.fan_in(i) + self.nodes[i].load
            if score > best_score:
                best, best_score = i, score
        if best < 0:
            return {}
        return {"node": best, "name": self.nodes[best].name,
                "fan_in": self.fan_in(best), "load": round(self.nodes[best].load, 3)}

    # ------------------------------------------------------------ 反馈环（DFS 三色）
    def detect_cycles(self) -> List[List[int]]:
        WHITE, GRAY, BLACK = 0, 1, 2
        color = [WHITE] * self.n
        cycles: List[List[int]] = []
        stack: List[int] = []

        def dfs(u: int) -> None:
            color[u] = GRAY
            stack.append(u)
            for v in self.neighbors(u):
                if color[v] == GRAY:
                    idx = stack.index(v)
                    cycles.append(stack[idx:] + [v])
                elif color[v] == WHITE:
                    dfs(v)
            stack.pop()
            color[u] = BLACK

        for i in range(self.n):
            if color[i] == WHITE:
                dfs(i)
        return cycles

    # ------------------------------------------------------------ 自组织（余弦）
    def set_state(self, node: int, state: List[float]) -> None:
        if 0 <= node < self.n:
            self.nodes[node].state = list(state)

    @staticmethod
    def _cosine(a: List[float], b: List[float]) -> float:
        if not a or not b or len(a) != len(b):
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(y * y for y in b))
        return dot / (na * nb) if na and nb else 0.0

    def self_organize(self, threshold: float = 0.8) -> List[Tuple[int, int]]:
        """状态余弦相似且超阈值的节点建立弱连接（自组织）。"""
        added = []
        for i in range(self.n):
            for j in range(i + 1, self.n):
                if self.weights[i][j] == 0 and self._cosine(
                        self.nodes[i].state, self.nodes[j].state) >= threshold:
                    self.weights[i][j] = 0.2
                    self.weights[j][i] = 0.2
                    added.append((i, j))
        return added

    # ------------------------------------------------------------ 赫布学习
    def hebbian_step(self, active_nodes: List[int]) -> dict:
        """共激活组内两两增强 Δw=η，并全局衰减；裁剪到 [0,clip]。"""
        cfg = self.config
        active = sorted(set(active_nodes))
        strengthened = 0
        for a in active:
            for b in active:
                if a != b and 0 <= a < self.n and 0 <= b < self.n:
                    self.weights[a][b] = min(
                        cfg.clip, self.weights[a][b] + cfg.learning_rate)
                    strengthened += 1
        # 全局衰减
        for i in range(self.n):
            for j in range(self.n):
                if i != j:
                    self.weights[i][j] = max(0.0,
                                             self.weights[i][j] * cfg.decay)
        return {"active": active, "strengthened": strengthened}

    # ------------------------------------------------------------ 根因
    def root_cause(self) -> dict:
        """从瓶颈节点反向追溯最重的入边（MTTL 风格）。"""
        bn = self.bottleneck()
        if not bn:
            return {}
        node = bn["node"]
        sources = [i for i in range(self.n) if self.weights[i][node] > 0]
        if not sources:
            return {"node": node, "upstream": []}
        sources.sort(key=lambda i: -(self.nodes[i].load
                                     + self.weights[i][node]))
        return {"node": node, "name": self.nodes[node].name,
                "upstream": [{"node": i, "name": self.nodes[i].name,
                              "load": round(self.nodes[i].load, 3)}
                             for i in sources[:3]]}

    # ------------------------------------------------------------ 视图
    def edge_list(self) -> List[dict]:
        out = []
        for i in range(self.n):
            for j in range(i + 1, self.n):
                if self.weights[i][j] > 0:
                    out.append({"a": i, "b": j,
                                "w": round(self.weights[i][j], 3)})
        return out

    def snapshot(self) -> dict:
        return {
            "nodes": self.n,
            "edges": len(self.edge_list()),
            "agents_mapped": len(self.agent_map),
            "bottleneck": self.bottleneck(),
            "cycles": len(self.detect_cycles()),
            "nodes_detail": [x.snapshot() for x in self.nodes],
        }
