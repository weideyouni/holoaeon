# -*- coding: utf-8 -*-
"""示例 3：自适应协作图与赫布学习 —— 六边形拓扑、共激活强化、瓶颈、根因。
运行：python examples/03_hebbian_collaboration.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.dirname(os.path.abspath(__file__))))

from holoaeon.graph import AdaptiveGraph


def main() -> None:
    # 先验通路：0→1→2
    g = AdaptiveGraph(flow_edges=[(0, 1), (1, 2)])

    # 1) 最短路
    path, dist = g.shortest_path(0, 2)
    print("最短路：", path, "距离：", round(dist, 2))

    # 2) 多轮共激活：0 和 1 频繁协作，连接被强化
    for _ in range(5):
        g.hebbian_step([0, 1])
    w = g.edge_list()
    e01 = next(e for e in w if {e["a"], e["b"]} == {0, 1})
    print("0-1 权重（被强化）：", round(e01["w"], 3))

    # 3) 施加负载 → 拥塞 → 瓶颈
    g.apply_load({1: 5.0})
    print("瓶颈节点：", g.bottleneck())

    # 4) 根因分析
    print("根因：", g.root_cause())

    # 5) 自组织（余弦相似度微调）
    g.self_organize()
    print("快照节点数：", g.snapshot()["nodes"])


if __name__ == "__main__":
    main()
