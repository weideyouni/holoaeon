# 自适应协作图

协作图把智能体放置在六边形晶格上，支持路由、负载、自组织与根因分析。

## 1. 六边形拓扑

六边形密铺天然具有均匀邻接结构。`hex_points(radius)` 生成晶格位置：

| radius | 位置数 |
|---|---|
| 0 | 1 |
| 1 | 7 |
| 2 | 19（默认） |

默认取前 17 个位置作为图节点。相邻节点间建立几何边，作为基础权重。

## 2. 核心能力

| 方法 | 作用 |
|---|---|
| `shortest_path(a, b)` | Dijkstra 最短路，先验流边作为引导 |
| `apply_load({node: load})` | 施加负载（裁剪到 0–1） |
| `fan_in(node)` | 入边数量 |
| `bottleneck()` | fan-in 最大且负载最高的节点 |
| `detect_cycles()` | 反馈环检测（六边形天然含环） |
| `hebbian_step(active)` | 共激活节点强化共享边 |
| `self_organize()` | 状态余弦相似的节点生长弱连接 |
| `root_cause()` | 从瓶颈反向追溯最重入边 |
| `edge_list()` | 全部正权重边 |

## 3. 赫布学习

```
每轮：所有边全局衰减（decay = 0.99）
共激活节点 i, j：w_ij += lr（lr = 0.12），权重对称，裁剪到上限
```

"共同激活的连接被强化"，频繁协作的节点形成稳定通路。

## 4. 自组织

状态向量余弦相似度超过阈值（默认 0.8）且当前无连接的节点，建立弱连接（0.2），
模拟相似节点自发聚集。

## 5. 根因分析

从瓶颈节点出发，沿入边反向追溯负载与权重最高的上游，形成可解释的因果链。

## 6. 关于环

六边形密铺天然包含大量环，`detect_cycles` 报告这些环是几何特性，不是缺陷。环在
反馈系统中可用于识别循环依赖。

## 7. 用法

```python
from holoaeon.graph import AdaptiveGraph
g = AdaptiveGraph(flow_edges=[(0, 1), (1, 2)])
path, dist = g.shortest_path(0, 2)
g.hebbian_step([0, 1])
print(g.bottleneck(), g.root_cause())
```
