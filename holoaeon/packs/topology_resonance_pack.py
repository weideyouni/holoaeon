# -*- coding: utf-8 -*-
"""
TopologyResonancePack —— 拓扑共振扩展包（第 12 个扩展包）
================================================================================
将多智能体城邦术语（Node-State-Edge-Runtime-Graph-Topology 九层）与数学概念
（1331×1331共振、曼陀罗一拖八、莫比乌斯扩张、克莱因收敛、希尔伯特空间、
卡尔曼滤波、贝叶斯推理）融合为确定性可调用的技能。

核心哲学：自组织相似性耗散结构
  · 每个智能体是一个小节点（Node）
  · 节点通过相似性边连接形成图（Graph）
  · 外部任务能量流入 → 驱动系统远离平衡态
  · 自组织（余弦相似+赫布学习）→ 熵减 → 秩序涌现
  · 共振超阈值 → 涌现效果（Emergence）

维度不变：只进 EXTRA_PACK_REGISTRY，不进 PACK_ORDER —— A1（25/47/9）不受影响。
纯标准库、确定性、离线。
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

from .base import DomainPack, RoleSpec, SkillSpec, WorkflowSpec

# ============================================================ 数学常量
# 1331 = 11³，1331×1331 = 11⁶ = 1,771,561（逻辑位置）
MATRIX_ROWS = 1331
MATRIX_COLS = 1331
LOGICAL_POSITIONS = MATRIX_ROWS * MATRIX_COLS  # 1,771,561
# 108641：实际活跃节点（稀疏实例化率 ≈ 6.13%）
ACTIVE_NODES = 108641
# 曼陀罗：1 中心 + 8 方位 = 9（九宫/八卦）
MANDALA_DIRECTIONS = 8
MANDALA_TOTAL = 9
# 共振阈值：余弦相似度超过此值则共振
RESONANCE_THRESHOLD = 0.75
# 涌现阈值：共振对数超过此值则触发涌现
EMERGENCE_THRESHOLD = 108641
# 耗散熵阈值：系统熵超过此值则触发自组织重组
DISSIPATION_ENTROPY_MAX = 0.95


# ============================================================ 1. 共振节点
def resonance_node(node_states: str = "", **_: Any) -> dict:
    """1331×1331 共振节点检测：计算节点状态相似性共振对。

    数学内核：
      1331×1331 = 1,771,561 逻辑位置，108641 实际活跃
      共振 = 余弦相似度 × 负载均衡因子
      共振对超阈值 → 涌现信号

    城邦映射：Node 层增强 + Agent Registration/Discovery
    """
    # 解析节点状态（格式："state1,state2;state3,state4" 或自动生成）
    if node_states:
        nodes = []
        for state_str in node_states.split(";"):
            vals = [float(x) for x in state_str.split(",") if x.strip()]
            if vals:
                nodes.append(vals)
    else:
        # 确定性默认：9 个节点（曼陀罗结构）的示例状态
        nodes = [
            [1.0, 0.0, 0.0],  # 中心
            [0.8, 0.6, 0.0],  # N
            [0.7, 0.7, 0.1],  # NE
            [0.6, 0.8, 0.0],  # E
            [0.7, 0.7, -0.1], # SE
            [0.8, 0.6, 0.0],  # S
            [0.7, 0.7, 0.1],  # SW
            [0.6, 0.8, 0.0],  # W
            [0.7, 0.7, -0.1], # NW
        ]

    n = len(nodes)
    resonance_pairs: List[Dict] = []

    for i in range(n):
        for j in range(i + 1, n):
            cos_sim = _cosine(nodes[i], nodes[j])
            if cos_sim >= RESONANCE_THRESHOLD:
                resonance_pairs.append({
                    "node_a": i, "node_b": j,
                    "resonance": round(cos_sim, 4),
                    "type": "resonant_pair",
                })

    emergence = len(resonance_pairs) > 0
    emergence_ratio = len(resonance_pairs) / max(1, n * (n - 1) // 2)

    return {
        "matrix": f"{MATRIX_ROWS}×{MATRIX_COLS} = {LOGICAL_POSITIONS}",
        "active_nodes": ACTIVE_NODES,
        "sparse_ratio": round(ACTIVE_NODES / LOGICAL_POSITIONS, 6),
        "current_nodes": n,
        "resonance_pairs": resonance_pairs[:20],  # 前20对
        "resonance_count": len(resonance_pairs),
        "resonance_threshold": RESONANCE_THRESHOLD,
        "emergence": emergence,
        "emergence_ratio": round(emergence_ratio, 4),
        "note": "共振 = 余弦相似度 ≥ 阈值；涌现 = 共振对 > 0",
    }


# ============================================================ 2. 曼陀罗扩散
def mandala_fanout(task: str = "", center: str = "", **_: Any) -> dict:
    """曼陀罗一拖八：1 中心 → 8 方位扩散，结果聚合。

    数学内核：
      曼陀罗结构 = 1 中心 + 8 方位（N/NE/E/SE/S/SW/W/NW）= 9 节点
      Fan-out：中心向 8 方位发送任务
      Fan-in：8 方位返回结果 → 中心聚合

    城邦映射：Fan-out/Fan-in + Orchestrator-Worker
    """
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

    # 中心节点任务分发
    fan_out = []
    for d in directions:
        fan_out.append({
            "direction": d,
            "task": task or "默认扩散任务",
            "center": center or "N00",
            "status": "dispatched",
        })

    # 确定性模拟 8 方位执行（非真实调用，确定性哈希模拟结果）
    fan_in = []
    for i, d in enumerate(directions):
        # 确定性"执行结果"：基于方向索引的确定性哈希
        result_hash = _det_hash(f"{task}:{d}:{i}")
        success = result_hash % 10 > 2  # 70% 确定性成功
        fan_in.append({
            "direction": d,
            "result": f"output_{d}_{result_hash % 1000}",
            "status": "ok" if success else "partial",
        })

    # 中心聚合
    successes = sum(1 for r in fan_in if r["status"] == "ok")
    all_ok = successes == MANDALA_DIRECTIONS

    return {
        "topology": "mandala",
        "structure": f"1中心 + {MANDALA_DIRECTIONS}方位 = {MANDALA_TOTAL}节点",
        "task": task or "默认扩散任务",
        "fan_out": fan_out,
        "fan_in": fan_in,
        "aggregation": {
            "center": center or "N00",
            "successes": successes,
            "total": MANDALA_DIRECTIONS,
            "all_ok": all_ok,
            "quorum": successes >= MANDALA_DIRECTIONS // 2 + 1,
        },
        "note": "曼陀罗一拖八：中心分发 → 8方位执行 → 中心聚合",
    }


# ============================================================ 3. 莫比乌斯边
def mobius_edge(edge_states: str = "", **_: Any) -> dict:
    """莫比乌斯扩张：边的翻转——输出变输入的反馈环。

    数学内核：
      莫比乌斯带：单面单边，翻转性质
      边状态翻转：output → inverted input
      支持双向状态流：A→B 与 B→A 互为翻转

    城邦映射：Conditional Edge + Back Edge + Handoff
    """
    # 解析边状态（格式："0.3,0.5,0.2;0.1,0.9,0.0"）
    if edge_states:
        states = []
        for s in edge_states.split(";"):
            vals = [float(x) for x in s.split(",") if x.strip()]
            if vals:
                states.append(vals)
    else:
        # 默认：2 条边的状态向量
        states = [[0.3, 0.5, 0.2], [0.1, 0.9, 0.0]]

    edges = []
    for i, state in enumerate(states):
        # 莫比乌斯翻转：状态向量取反
        flipped = [-x for x in state]
        # 翻转后再归一化
        norm_orig = math.sqrt(sum(x * x for x in state))
        norm_flip = math.sqrt(sum(x * x for x in flipped))
        # 相似度（翻转后应接近 -1，表示完全反相）
        if norm_orig and norm_flip:
            cos_orig_flip = sum(a * b for a, b in zip(state, flipped)) / (norm_orig * norm_flip)
        else:
            cos_orig_flip = 0.0

        edges.append({
            "edge_id": i,
            "forward_state": [round(x, 4) for x in state],
            "mobius_flipped": [round(x, 4) for x in flipped],
            "cosine_forward_flipped": round(cos_orig_flip, 4),
            "topology": "mobius",  # 单面翻转
            "feedback": "output→inverted_input",
        })

    # 莫比乌斯回路：最后一条边的翻转连回第一条边
    if len(edges) >= 2:
        loop闭合 = True
        mobius_loop = {
            "edges": len(edges),
            "loop_closed": loop闭合,
            "total_flips": len(edges),
            "topology": "mobius_loop",
            "note": "莫比乌斯回路：边首尾翻转相接，单面闭环",
        }
    else:
        mobius_loop = {"edges": len(edges), "loop_closed": False}

    return {
        "topology": "mobius",
        "property": "single_sided_flip",
        "edges": edges,
        "mobius_loop": mobius_loop,
        "note": "莫比乌斯扩张：边翻转 = 输出→反相输入，支持反馈环",
    }


# ============================================================ 4. 克莱因收敛
def klein_convergence(paths: str = "", **_: Any) -> dict:
    """克莱因收敛：多路径收敛检测 + 瓶颈根因。

    数学内核：
      克莱因瓶：无内外之分，四维嵌入
      收敛：多条路径汇聚到同一节点
      根因：fan-in 最高 + 负载最高的节点

    城邦映射：Merge Edge + Loop Detection + Circuit Breaker
    """
    # 解析路径（格式："0→1→3;0→2→3;0→1→2→3"）
    if paths:
        path_list = []
        for p in paths.split(";"):
            nodes = [int(x) for x in p.split("→") if x.strip() or x == "0"]
            path_list.append(nodes)
    else:
        # 默认：3条路径汇聚到节点3
        path_list = [[0, 1, 3], [0, 2, 3], [0, 1, 2, 3]]

    # 收敛点检测：统计每个节点被多少条路径到达
    convergence: Dict[int, int] = {}
    for path in path_list:
        for node in path[1:]:  # 跳过起点
            convergence[node] = convergence.get(node, 0) + 1

    # 收敛节点（被多条路径到达）
    convergence_nodes = [
        {"node": n, "path_count": c, "convergence_strength": round(c / len(path_list), 4)}
        for n, c in sorted(convergence.items(), key=lambda x: -x[1])
        if c > 1
    ]

    # 根因节点 = 收敛强度最高
    root_cause = convergence_nodes[0] if convergence_nodes else None

    # 克莱因瓶性质：无内外 → 所有节点都在"同一面"
    all_nodes = set()
    for path in path_list:
        all_nodes.update(path)
    klein_property = {
        "total_nodes": len(all_nodes),
        "inside_outside": "无内外之分",
        "embedding": "4D → 3D 投影（克莱因瓶不可在3D无自交嵌入）",
    }

    # 熔断检测：如果收敛强度 > 阈值，触发熔断
    circuit_breaker = False
    if root_cause and root_cause["convergence_strength"] > 0.8:
        circuit_breaker = True

    return {
        "topology": "klein",
        "property": "no_inside_outside",
        "paths": path_list,
        "path_count": len(path_list),
        "convergence_nodes": convergence_nodes,
        "root_cause": root_cause,
        "klein_property": klein_property,
        "circuit_breaker": circuit_breaker,
        "note": "克莱因收敛：多路径汇聚 → 根因识别 → 熔断保护",
    }


# ============================================================ 5. 卡尔曼状态
def kalman_state(observations: str = "", **_: Any) -> dict:
    """卡尔曼滤波状态融合：多源状态估计 + 不确定性传播。

    数学内核：
      状态：x (均值) + P (方差)
      预测：x' = x, P' = P + Q（过程噪声）
      更新：K = P/(P+R), x = x + K·(z-x), P = (1-K)·P
      多次观测 → 状态收敛 + 不确定性降低

    城邦映射：State Reducer + Checkpoint + Shared State
    """
    # 解析观测值（格式："1.0,0.9,1.1,0.95,1.05"）
    if observations:
        obs = [float(x) for x in observations.split(",") if x.strip()]
    else:
        # 默认：5次观测，真实值约1.0
        obs = [1.0, 0.9, 1.1, 0.95, 1.05]

    # 卡尔曼滤波（标量版）
    x = obs[0]  # 初始状态估计
    P = 1.0     # 初始方差（大 = 不确定）
    Q = 0.01    # 过程噪声
    R = 0.1     # 观测噪声

    steps = []
    for i, z in enumerate(obs):
        # 预测
        x_pred = x
        P_pred = P + Q
        # 更新
        K = P_pred / (P_pred + R)
        x = x_pred + K * (z - x_pred)
        P = (1 - K) * P_pred
        steps.append({
            "step": i,
            "observation": z,
            "kalman_gain": round(K, 6),
            "state_estimate": round(x, 6),
            "uncertainty": round(P, 6),
        })

    # 状态快照（Checkpoint）
    checkpoint = {
        "final_state": round(x, 6),
        "final_uncertainty": round(P, 6),
        "convergence": P < 0.01,  # 不确定性收敛
        "observations": len(obs),
    }

    return {
        "filter": "kalman_scalar",
        "parameters": {"Q": Q, "R": R, "initial_P": 1.0},
        "steps": steps,
        "checkpoint": checkpoint,
        "note": "卡尔曼滤波：多源观测 → 状态融合 → 不确定性收敛 → 快照",
    }


# ============================================================ 6. 贝叶斯守卫
def bayesian_guard(feature: str = "", history: str = "", **_: Any) -> dict:
    """贝叶斯推理守卫：基于历史拦截率的概率拦截。

    数学内核：
      先验：P(block) = 历史拦截率
      似然：P(feature|block) / P(feature|allow)
      后验：P(block|feature) = P(feature|block)·P(block) / P(feature)
      后验 > 阈值 → BLOCK

    城邦映射：Guardrail + Permission/Policy + Retry Policy
    """
    # 先验：历史拦截率（默认 0.15 = 15% 拦截率）
    if history:
        parts = [float(x) for x in history.split(",") if x.strip()]
        blocked = sum(1 for p in parts if p > 0.5)
        prior_block = blocked / len(parts) if parts else 0.15
    else:
        prior_block = 0.15

    prior_allow = 1.0 - prior_block

    # 特征似然表（确定性，基于工程经验）
    likelihood_table = {
        "write": {"block": 0.70, "allow": 0.20},
        "delete": {"block": 0.85, "allow": 0.05},
        "read": {"block": 0.05, "allow": 0.60},
        "execute": {"block": 0.60, "allow": 0.15},
        "network": {"block": 0.90, "allow": 0.10},
        "safe": {"block": 0.02, "allow": 0.80},
    }

    # 查询特征
    feat_key = feature.lower().strip() if feature else "safe"
    if feat_key not in likelihood_table:
        feat_key = "safe"

    ll = likelihood_table[feat_key]
    p_feature_given_block = ll["block"]
    p_feature_given_allow = ll["allow"]

    # 贝叶斯推理
    p_feature = p_feature_given_block * prior_block + p_feature_given_allow * prior_allow
    if p_feature > 0:
        posterior_block = (p_feature_given_block * prior_block) / p_feature
    else:
        posterior_block = prior_block

    # 决策
    threshold = 0.5
    decision = "BLOCK" if posterior_block > threshold else "ALLOW"

    # 重试策略（如果 BLOCK）
    retry_policy = {
        "max_retries": 3,
        "backoff": "exponential",
        "requires_authorization": True,
    } if decision == "BLOCK" else None

    return {
        "filter": "bayesian",
        "prior": {"block": round(prior_block, 4), "allow": round(prior_allow, 4)},
        "feature": feat_key,
        "likelihood": ll,
        "posterior": {"block": round(posterior_block, 6),
                      "allow": round(1 - posterior_block, 6)},
        "threshold": threshold,
        "decision": decision,
        "retry_policy": retry_policy,
        "note": "贝叶斯守卫：先验(历史) + 似然(特征) → 后验(概率) → 决策",
    }


# ============================================================ 7. 希尔伯特投影（辅助）
def hilbert_project(vector: str = "", dimensions: int = 0, **_: Any) -> dict:
    """希尔伯特计算空间投影：有限维 → 近似无限维。

    数学内核：
      希尔伯特空间：完备内积空间，可无限维
      有限向量 v ∈ R^n → 希尔伯特投影 v_h ∈ R^N (N >> n)
      基函数：φ_k(x) = x^k / sqrt(k!)（归一化多项式基）
      投影：v_h[k] = v[k % n] · φ_k(k)

    城邦映射：Memory + Context + Observability
    """
    # 解析输入向量
    if vector:
        v = [float(x) for x in vector.split(",") if x.strip()]
    else:
        v = [1.0, 0.5, -0.3, 0.8]

    n = len(v)
    # 投影维度（默认 10 倍原维度，模拟"更高维空间"）
    N = dimensions if dimensions > 0 else n * 10

    # 希尔伯特投影
    projection = []
    for k in range(N):
        # 归一化多项式基 φ_k = 1/sqrt(k+1)（简化版，避免大数溢出）
        phi_k = 1.0 / math.sqrt(k + 1)
        v_h_k = v[k % n] * phi_k
        projection.append(round(v_h_k, 6))

    # 内积（希尔伯特空间度量）
    inner_product = sum(v_h ** 2 for v_h in projection)
    hilbert_norm = math.sqrt(inner_product)

    # 原空间 vs 希尔伯特空间范数比较
    orig_norm = math.sqrt(sum(x ** 2 for x in v))

    return {
        "space": "hilbert",
        "original_dim": n,
        "projected_dim": N,
        "expansion_ratio": round(N / n, 2),
        "original_vector": [round(x, 4) for x in v],
        "projection_sample": projection[:20],  # 前20维
        "projection_full_length": len(projection),
        "hilbert_norm": round(hilbert_norm, 6),
        "original_norm": round(orig_norm, 6),
        "norm_preservation": round(hilbert_norm / orig_norm, 6) if orig_norm else 0,
        "note": "希尔伯特投影：有限维→高维近似，保持内积结构",
    }


# ============================================================ 8. 耗散度量（辅助）
def dissipation_measure(task_flow: str = "", **_: Any) -> dict:
    """耗散结构度量：系统熵 + 秩序/失序平衡。

    数学内核：
      耗散结构（Prigogine）：开放系统通过能量流入维持低熵秩序
      Shannon 熵：H = -Σ p_i · log2(p_i)
      秩序度：O = 1 - H/H_max
      耗散率：能量输入 - 有效功

    城邦映射：Observability + Traceability + Audit
    """
    # 解析任务流（格式："ok,ok,fail,ok,ok,ok,fail,ok"）
    if task_flow:
        results = [x.strip() for x in task_flow.split(",") if x.strip()]
    else:
        results = ["ok", "ok", "fail", "ok", "ok", "ok", "fail", "ok",
                   "ok", "ok"]

    total = len(results)
    ok_count = sum(1 for r in results if r == "ok")
    fail_count = total - ok_count

    # 概率分布
    p_ok = ok_count / total if total else 0
    p_fail = fail_count / total if total else 0

    # Shannon 熵
    entropy = 0.0
    if p_ok > 0:
        entropy -= p_ok * math.log2(p_ok)
    if p_fail > 0:
        entropy -= p_fail * math.log2(p_fail)

    # 最大熵（均匀分布）
    entropy_max = math.log2(2) if total > 0 else 1.0  # 二元分布最大熵=1
    # 秩序度
    order = 1.0 - entropy / entropy_max if entropy_max else 0.0

    # 耗散率（能量输入 vs 有效功）
    energy_in = total  # 任务数 = 能量输入
    work_done = ok_count  # 成功 = 有效功
    dissipation = energy_in - work_done  # 耗散 = 失败数
    dissipation_rate = dissipation / energy_in if energy_in else 0

    # 自组织触发判断
    needs_reorganization = entropy > DISSIPATION_ENTROPY_MAX or order < 0.3

    return {
        "structure": "dissipative",
        "task_flow": results,
        "total": total,
        "success": ok_count,
        "failure": fail_count,
        "probabilities": {"ok": round(p_ok, 4), "fail": round(p_fail, 4)},
        "shannon_entropy": round(entropy, 6),
        "entropy_max": round(entropy_max, 6),
        "order": round(order, 6),
        "disorder": round(1 - order, 6),
        "dissipation": {
            "energy_in": energy_in,
            "work_done": work_done,
            "dissipated": dissipation,
            "dissipation_rate": round(dissipation_rate, 4),
        },
        "needs_reorganization": needs_reorganization,
        "emergence_condition": "熵 > 0.95 或 秩序 < 0.3 → 触发自组织重组",
        "note": "耗散度量：能量流入 → 熵减 → 秩序涌现；失序超阈 → 自组织重组",
    }


# ============================================================ 9. 道步：优化问题定义
def dao_define_problem(variables: str = "", objective: str = "",
                       constraints: str = "", **_: Any) -> dict:
    """道步：定义优化问题本体（设计变量+目标函数+约束条件）。

    方法论映射：第一章·道——优化问题的数学模型=城邦的"宪法"
    城邦映射：设计变量→智能体参数空间，目标函数→全局效用，约束→协议边界
    主导透镜：P4 持衡
    """
    var_list = ([v.strip() for v in variables.split(",") if v.strip()]
                if variables else ["agent_role", "permission", "bandwidth"])
    obj_map = {
        "diff0": "diff0不漂移（硬约束）",
        "efficiency": "全局效能最大化",
        "convergence": "收敛速度最大化",
        "emergence": "涌现效果最大化",
    }
    obj_key = objective.lower().strip() if objective else "efficiency"
    obj_desc = obj_map.get(obj_key, f"自定义目标：{objective}")
    const_list = ([c.strip() for c in constraints.split(",") if c.strip()]
                  if constraints else
                  ["diff0=2fc892cf9af6e755", "agents=25", "skills=47", "guard_layers=8"])
    dim = len(var_list)
    return {
        "step": "道", "lens": "P4持衡",
        "design_variables": var_list, "dimension": dim,
        "objective": obj_key, "objective_desc": obj_desc,
        "constraints": const_list, "constraint_count": len(const_list),
        "feasible_region": f"R^{dim} 上的可行域（由 {len(const_list)} 个约束界定）",
        "tensor_view": f"设计变量=R^{dim}中的点，目标函数=流形上的势函数",
        "note": "道步：定义本体——设计变量=参数张量，目标=全局效用，约束=协议边界",
    }


# ============================================================ 10. 法步：梯度分析
def fa_gradient_analysis(current: str = "", perturbation: str = "",
                         **_: Any) -> dict:
    """法步：梯度方向+泰勒预测+凸性判断。

    方法论映射：第二章·法——微积分基石与梯度流动的拓扑意义
    城邦映射：梯度=价值导向，泰勒展开=有限理性预测，凸规划=可治理性
    主导透镜：四人共评
    """
    if current:
        state = [float(x) for x in current.split(",") if x.strip()]
    else:
        state = [0.3, 0.5, 0.2, 0.8]
    n = len(state)
    if perturbation:
        pert = [float(x) for x in perturbation.split(",") if x.strip()]
        if len(pert) != n:
            pert = [0.1] * n
    else:
        pert = [0.1] * n

    weights = [1.0 / (i + 1) for i in range(n)]
    f_current = sum(w * x for w, x in zip(weights, state))
    f_pert = sum(w * (x + p) for w, x, p in zip(weights, state, pert))
    gradient = [(f_pert - f_current) / (p if p != 0 else 1.0) for p in pert]
    grad_norm = math.sqrt(sum(g * g for g in gradient))
    grad_dir = [g / grad_norm if grad_norm else 0.0 for g in gradient]
    delta = sum(g * p for g, p in zip(gradient, pert))
    taylor_1 = f_current + delta
    pert2 = [p * 2 for p in pert]
    f_pert2 = sum(w * (x + p2) for w, x, p2 in zip(weights, state, pert2))
    denom = sum(p * p for p in pert) if any(pert) else 1.0
    curvature = (f_pert2 - 2 * f_pert + f_current) / denom
    taylor_2 = taylor_1 + 0.5 * curvature * denom
    convexity = "convex" if curvature > 0 else ("concave" if curvature < 0 else "flat")
    return {
        "step": "法", "lens": "四人共评",
        "current_state": [round(x, 4) for x in state],
        "gradient": [round(g, 6) for g in gradient],
        "gradient_direction": [round(g, 6) for g in grad_dir],
        "f_current": round(f_current, 6), "f_perturbed": round(f_pert, 6),
        "taylor_first": round(taylor_1, 6),
        "taylor_second": round(taylor_2, 6),
        "curvature": round(curvature, 6),
        "convexity": convexity,
        "governable": convexity == "convex",
        "note": "法步：梯度=价值导向，泰勒=有限理性预测，凸性=可治理性",
    }


# ============================================================ 11. 术步：约束处理
def shu_constraint_handling(constraints: str = "",
                            violations: str = "", **_: Any) -> dict:
    """术步：拉格朗日乘子+KKT条件+惩罚函数。

    方法论映射：第三章·术——约束处理与拉格朗日的"契约精神"
    城邦映射：λ=内部定价，KKT=动态治理规则，惩罚=信誉体系
    主导透镜：P3 构弦
    """
    if constraints:
        cl = []
        for c in constraints.split(","):
            parts = c.strip().split(":")
            if len(parts) == 2:
                cl.append({"name": parts[0].strip(), "type": parts[1].strip()})
            else:
                cl.append({"name": parts[0].strip(), "type": "hard"})
    else:
        cl = [{"name": "diff0", "type": "hard"}, {"name": "agents=25", "type": "hard"},
              {"name": "skills=47", "type": "hard"}, {"name": "guard=8", "type": "hard"},
              {"name": "bandwidth", "type": "soft"}]
    if violations:
        vv = [float(x) for x in violations.split(",") if x.strip()]
    else:
        vv = [0.0] * len(cl)

    multipliers = []
    for i, c in enumerate(cl):
        v = vv[i] if i < len(vv) else 0.0
        lam = (100.0 * v if v > 0 else 0.0) if c["type"] == "hard" else 10.0 * v
        multipliers.append({"constraint": c["name"], "type": c["type"],
                            "violation": round(v, 4), "lambda": round(lam, 4),
                            "active": v > 0})
    kkt_ok = all((m["violation"] > 0 and m["lambda"] > 0) or
                 (m["violation"] == 0 and m["lambda"] == 0) for m in multipliers)
    active = [m for m in multipliers if m["active"]]
    penalty = sum(m["lambda"] * m["violation"] for m in multipliers)
    advice = (f"主动约束：{', '.join(m['constraint'] for m in active)}；乘子已激活"
              if active else "无主动约束；常规状态靠自律（KKT互补松弛：乘子=0）")
    return {
        "step": "术", "lens": "P3构弦",
        "constraints": multipliers,
        "kkt_complementary_slackness": kkt_ok,
        "active_constraints": [m["constraint"] for m in active],
        "total_penalty": round(penalty, 4),
        "governance_advice": advice,
        "note": "术步：λ=影子价格，KKT=动态治理，惩罚=信誉负反馈",
    }


# ============================================================ 12. 器步：算法选择
def qi_algorithm_selection(problem_type: str = "", dimension: int = 0,
                           **_: Any) -> dict:
    """器步：搜索算法选择决策树。

    方法论映射：第四章·器——搜索算法与智能体进化策略
    城邦映射：梯度下降=自主学习，牛顿=高阶认知，DFP/BFGS=认知地图，单纯形=群体编队
    主导透镜：P2 筑基
    """
    algos = {
        "gradient_descent": {"order": "一阶", "conv": "线性", "cost": "低",
                             "req": "梯度可计算", "map": "自主学习引擎",
                             "v9": "mandala_fanout"},
        "newton": {"order": "二阶", "conv": "二次", "cost": "高",
                   "req": "海森矩阵", "map": "高阶认知能力", "v9": "kalman_state"},
        "conjugate_gradient": {"order": "一阶+记忆", "conv": "超线性", "cost": "中",
                               "req": "梯度+共轭方向", "map": "经验复用",
                               "v9": "mobius_edge"},
        "dfp_bfgs": {"order": "拟二阶", "conv": "超线性", "cost": "中",
                     "req": "梯度+迭代", "map": "自适应认知地图",
                     "v9": "hilbert_project"},
        "simplex": {"order": "零阶", "conv": "慢但稳健", "cost": "低",
                    "req": "仅函数值", "map": "群体编队", "v9": "mandala_expand"},
        "powell": {"order": "零阶+共轭", "conv": "超线性", "cost": "中",
                   "req": "仅函数值", "map": "团队默契", "v9": "klein_convergence"},
    }
    ptype = problem_type.lower().strip() if problem_type else "default"
    dim = dimension if dimension > 0 else 4
    if ptype in ("convex", "smooth", "differentiable"):
        rec = "newton" if dim <= 10 else ("dfp_bfgs" if dim <= 100 else "conjugate_gradient")
    elif ptype in ("nonconvex", "noisy", "blackbox"):
        rec = "simplex" if dim <= 5 else "powell"
    else:
        rec = "gradient_descent"
    a = algos[rec]
    return {
        "step": "器", "lens": "P2筑基",
        "problem_type": ptype, "dimension": dim,
        "recommended": rec,
        "detail": {"order": a["order"], "convergence": a["conv"],
                   "cost": a["cost"], "requirement": a["req"],
                   "city_map": a["map"], "v9_anchor": a["v9"]},
        "all_algorithms": {k: {"order": v["order"], "convergence": v["conv"],
                               "map": v["map"], "v9": v["v9"]}
                          for k, v in algos.items()},
        "note": "器步：梯度下降=自主学习，牛顿=高阶认知，DFP/BFGS=认知地图，单纯形=群体编队",
    }


# ============================================================ 13. 四人组张量向量化
def quartet_tensor(p1: str = "", p2: str = "", p3: str = "",
                   p4: str = "", **_: Any) -> dict:
    """四人组张量向量化：权重矩阵+共振检测+决策熵+涌现判断。

    P1探微[愿景×拓扑×涌现] / P2筑基[工程×算法×收敛]
    P3构弦[架构×约束×度量] / P4持衡[本体×共振×平衡]
    """
    scores = []
    for s in [p1, p2, p3, p4]:
        scores.append(max(0.0, min(1.0, float(s))) if s else 0.7)
    p1s, p2s, p3s, p4s = scores

    weight_matrix = {
        "道": {"P1": 0.3, "P2": 0.3, "P3": 0.3, "P4": 0.5},
        "法": {"P1": 0.2, "P2": 0.3, "P3": 0.3, "P4": 0.3},
        "术": {"P1": 0.2, "P2": 0.3, "P3": 0.5, "P4": 0.3},
        "器": {"P1": 0.2, "P2": 0.5, "P3": 0.3, "P4": 0.3},
        "升维": {"P1": 0.5, "P2": 0.3, "P3": 0.4, "P4": 0.4},
    }
    sims = {"P1×P2": 0.5, "P1×P3": 0.4, "P1×P4": 0.3,
            "P2×P3": 0.7, "P2×P4": 0.5, "P3×P4": 0.4}

    vecs = {f"P{i+1}": [s, 1 - s] for i, s in enumerate(scores)}
    res_pairs = []
    pair_names = [("P1", "P2"), ("P1", "P3"), ("P1", "P4"),
                  ("P2", "P3"), ("P2", "P4"), ("P3", "P4")]
    for a, b in pair_names:
        cos = _cosine(vecs[a], vecs[b])
        if cos >= 0.75:
            res_pairs.append({"pair": f"{a}×{b}", "resonance": round(cos, 4)})

    # 决策熵：用标准差度量分歧（相似评分→低分歧→高秩序）
    mean = sum(scores) / len(scores)
    variance = sum((s - mean) ** 2 for s in scores) / len(scores)
    std = math.sqrt(variance)
    max_std = 0.5  # [0,1]范围4个值的最大标准差
    agreement = 1.0 - min(std / max_std, 1.0)
    entropy = 1.0 - agreement  # 高熵=高分歧
    e_max = 1.0
    order = agreement

    emergence = (sims["P2×P3"] >= 0.7 and p1s >= 0.6 and
                 p4s <= 0.4 and order > 0.30)

    return {
        "tensor_space": "R^4",
        "scores": {"P1": round(p1s, 4), "P2": round(p2s, 4),
                   "P3": round(p3s, 4), "P4": round(p4s, 4)},
        "weight_matrix": weight_matrix,
        "similarities": sims,
        "resonance_pairs": res_pairs,
        "resonance_count": len(res_pairs),
        "decision_entropy": round(entropy, 6),
        "entropy_max": round(e_max, 6),
        "order": round(order, 6),
        "emergence_conditions": {
            "P2×P3_strong(≥0.7)": sims["P2×P3"] >= 0.7,
            "P1_vision(≥0.6)": p1s >= 0.6,
            "P4_risk(≤0.4)": p4s <= 0.4,
            "order(>0.30)": order > 0.30,
        },
        "emergence": emergence,
        "note": "四人组张量：权重矩阵+共振+熵+涌现触发",
    }


# ============================================================ 14. 涌现链完整闭环
def emergence_chain(input_concept: str = "", **_: Any) -> dict:
    """涌现链完整闭环：道→法→术→器→升维→共振→涌现。

    将五步决策协议串联执行，从输入概念到涌现判断的完整链路。
    """
    concept = input_concept.strip() if input_concept else "默认升级需求"

    dao = dao_define_problem(
        variables="agent_role,permission,bandwidth,memory",
        objective="efficiency",
        constraints="diff0,agents=25,skills=47,guard_layers=8")
    fa = fa_gradient_analysis(
        current="0.3,0.5,0.2,0.8", perturbation="0.1,0.1,0.1,0.1")
    shu = shu_constraint_handling(
        constraints="diff0:hard,agents:hard,skills:hard,guard:hard,bandwidth:soft",
        violations="0,0,0,0,0.2")
    qi = qi_algorithm_selection(problem_type="convex", dimension=4)
    hil = hilbert_project(vector="0.3,0.5,0.2,0.8")
    mob = mobius_edge()
    kle = klein_convergence()
    bay = bayesian_guard(feature="safe")
    qt = quartet_tensor(p1="0.85", p2="0.85", p3="0.85", p4="0.30")
    emergence = qt.get("emergence", False)

    return {
        "chain": "emergence",
        "input_concept": concept,
        "steps": {
            "道_dao": {"lens": "P4", "objective": dao["objective_desc"],
                       "dim": dao["dimension"], "constraints": dao["constraint_count"]},
            "法_fa": {"lens": "四人共评",
                      "gradient_dir": fa["gradient_direction"],
                      "convexity": fa["convexity"], "governable": fa["governable"]},
            "术_shu": {"lens": "P3", "active": shu["active_constraints"],
                       "kkt_ok": shu["kkt_complementary_slackness"],
                       "penalty": shu["total_penalty"]},
            "器_qi": {"lens": "P2", "algorithm": qi["recommended"],
                      "convergence": qi["detail"]["convergence"],
                      "city_map": qi["detail"]["city_map"]},
            "升维_shengwei": {"lens": "P1",
                              "hilbert_dim": hil["projected_dim"],
                              "mobius_loop": mob["mobius_loop"].get("loop_closed", False),
                              "klein_root": (kle.get("root_cause", {}) or {}).get("node"),
                              "bayesian_decision": bay["decision"]},
        },
        "quartet": {"scores": qt["scores"],
                    "resonance_count": qt["resonance_count"],
                    "entropy": qt["decision_entropy"],
                    "order": qt["order"]},
        "emergence": emergence,
        "emergence_conditions": qt["emergence_conditions"],
        "note": "涌现链：道→法→术→器→升维→共振→涌现（完整闭环）",
    }


# ============================================================ 辅助函数
def _cosine(a: List[float], b: List[float]) -> float:
    """余弦相似度（确定性）。"""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


def _det_hash(s: str) -> int:
    """确定性哈希（sha256 取前8字节，不用 random）。"""
    import hashlib
    h = hashlib.sha256(s.encode("utf-8")).hexdigest()
    return int(h[:8], 16)


# ============================================================ 16. 城邦治理（V11-D）
def city_state_governance(calls: str = "", threshold: int = 3,
                          retry_policy: str = "exponential", **_: Any) -> dict:
    """城邦治理：循环检测 + 熔断 + 重试策略。

    数学内核：
      Loop Detection：调用链窗口指纹（窗口=4），重复环 → 检测
      Circuit Breaker：连续失败 ≥ threshold → 熔断隔离
      Retry Policy：指数/线性退避（base·2^i）

    城邦映射：治理规则 → Guardrail / Policy / Audit（第八层可观测与治理）。
    """
    if calls:
        seq = [x.strip().lower() for x in calls.split(",") if x.strip()]
    else:
        seq = ["ok", "ok", "fail", "fail", "fail", "ok"]
    threshold = max(1, int(threshold))

    # Loop Detection：窗口指纹
    loop_detected = False
    loop_seen = set()
    for i in range(len(seq) - 3):
        window = tuple(seq[i:i + 4])
        if window in loop_seen:
            loop_detected = True
            break
        loop_seen.add(window)

    # Circuit Breaker：最长连续失败
    max_run = 0
    cur_run = 0
    for r in seq:
        if r == "fail":
            cur_run += 1
            max_run = max(max_run, cur_run)
        else:
            cur_run = 0
    tripped = max_run >= threshold

    # Retry Policy（退避）
    base_delay = 1.0
    retries = max(0, max_run - 1)
    if retry_policy.lower() == "exponential":
        delays = [base_delay * (2.0 ** i) for i in range(max_run)]
    elif retry_policy.lower() == "linear":
        delays = [base_delay * (i + 1) for i in range(max_run)]
    else:
        delays = [base_delay] * max_run

    return {
        "governance": "city_state",
        "call_sequence": seq,
        "loop_detection": {"window": 4, "detected": loop_detected},
        "circuit_breaker": {"failure_threshold": threshold,
                            "max_consecutive_failures": max_run,
                            "tripped": tripped},
        "retry_policy": {"policy": retry_policy, "max_retries": retries,
                         "backoff_delays": [round(d, 3) for d in delays]},
        "note": "城邦治理：循环检测(指纹环) + 熔断(连续失败) + 重试(退避)",
    }


# ============================================================ 17. 耗散涌现监控（V11-D）
def dissipation_emergence_monitor(task_flow: str = "", window: int = 10,
                                  **_: Any) -> dict:
    """耗散涌现监控：Observability + Traceability + 耗散熵趋势。

    数学内核：
      Shannon 熵：H = -Σ p_i·log2(p_i)（逐步累积）
      趋势：熵/秩序随步骤演化（时间序列）
      涌现：末步秩序 > 0.7 且 熵减（末步熵 < 首步熵）

    城邦映射：可观测性 → Observability / Traceability（第八层）。
    """
    if task_flow:
        results = [x.strip().lower() for x in task_flow.split(",") if x.strip()]
    else:
        results = ["ok", "ok", "fail", "ok", "ok", "ok",
                   "fail", "ok", "ok", "ok"]
    window = max(2, int(window))
    seq = results[-window:]

    # 累积趋势（Traceability：逐步快照）
    steps = []
    for i in range(1, len(seq) + 1):
        sub = seq[:i]
        ok_c = sum(1 for r in sub if r == "ok")
        p_ok = ok_c / len(sub)
        p_fail = 1.0 - p_ok
        ent = 0.0
        if p_ok > 0:
            ent -= p_ok * math.log2(p_ok)
        if p_fail > 0:
            ent -= p_fail * math.log2(p_fail)
        steps.append({"step": i, "entropy": round(ent, 6),
                      "order": round(1.0 - ent, 6)})

    # 涌现判定：半窗窗口熵比较（前半 vs 后半，熵减 = 从混沌走向有序）
    half = max(1, len(seq) // 2)
    head = seq[:half]
    tail = seq[half:]

    def _w_entropy(items: List[str]) -> float:
        ok_c = sum(1 for r in items if r == "ok")
        p_ok = ok_c / len(items)
        p_fail = 1.0 - p_ok
        ent = 0.0
        if p_ok > 0:
            ent -= p_ok * math.log2(p_ok)
        if p_fail > 0:
            ent -= p_fail * math.log2(p_fail)
        return ent

    ent_head = _w_entropy(head)
    ent_tail = _w_entropy(tail)
    order_last = 1.0 - ent_tail
    emergence = order_last > 0.7 and ent_tail < ent_head
    ok_count = sum(1 for r in seq if r == "ok")
    error_rate = (len(seq) - ok_count) / len(seq) if seq else 0.0

    return {
        "monitor": "dissipation_emergence",
        "window": window,
        "sequence": seq,
        "observability": {"total": len(seq), "ok_count": ok_count,
                          "error_rate": round(error_rate, 4)},
        "traceability": {"steps": steps},
        "trend": {"entropy_head": round(ent_head, 6),
                  "entropy_tail": round(ent_tail, 6),
                  "order_last": round(order_last, 6)},
        "emergence": emergence,
        "note": "耗散涌现监控：半窗熵比较 + 秩序 → 涌现判断（order>0.7 且熵减）",
    }


# ============================================================ 扩展包定义
class TopologyResonancePack(DomainPack):
    key = "topology_resonance"
    name = "拓扑共振（自组织相似性耗散结构）"
    description = (
        "将城邦术语（Node-State-Edge-Runtime）与数学概念"
        "（1331共振·曼陀罗·莫比乌斯·克莱因·希尔伯特·卡尔曼·贝叶斯）"
        "融合为确定性技能；每个智能体是小节点，通过相似性边连接，"
        "外部能量流入驱动熵减，共振超阈值触发涌现"
    )

    skills = [
        SkillSpec("resonance_node", resonance_node,
                  "1331×1331共振节点检测：余弦相似度共振对 + 涌涌现信号",
                  tags=["topology", "resonance", "node", "emergence"],
                  inputs={"node_states": "str"}),
        SkillSpec("mandala_fanout", mandala_fanout,
                  "曼陀罗一拖八：1中心→8方位扩散，结果聚合（Fan-out/Fan-in）",
                  tags=["topology", "mandala", "fanout", "orchestrator"],
                  inputs={"task": "str", "center": "str"}),
        SkillSpec("mobius_edge", mobius_edge,
                  "莫比乌斯扩张：边翻转反馈环（输出→反相输入）",
                  tags=["topology", "mobius", "edge", "feedback"],
                  inputs={"edge_states": "str"}),
        SkillSpec("klein_convergence", klein_convergence,
                  "克莱因收敛：多路径汇聚检测 + 根因识别 + 熔断",
                  tags=["topology", "klein", "convergence", "circuit_breaker"],
                  inputs={"paths": "str"}),
        SkillSpec("kalman_state", kalman_state,
                  "卡尔曼滤波状态融合：多源观测→状态估计→不确定性收敛→快照",
                  tags=["state", "kalman", "filter", "checkpoint"],
                  inputs={"observations": "str"}),
        SkillSpec("bayesian_guard", bayesian_guard,
                  "贝叶斯推理守卫：先验(历史)+似然(特征)→后验→概率拦截",
                  tags=["guard", "bayesian", "probabilistic", "policy"],
                  inputs={"feature": "str", "history": "str"}),
        SkillSpec("hilbert_project", hilbert_project,
                  "希尔伯特空间投影：有限维→高维近似，保持内积结构",
                  tags=["memory", "hilbert", "projection", "context"],
                  inputs={"vector": "str", "dimensions": "int"}),
        SkillSpec("dissipation_measure", dissipation_measure,
                  "耗散结构度量：Shannon熵+秩序度+耗散率+自组织触发",
                  tags=["observability", "dissipation", "entropy", "audit"],
                  inputs={"task_flow": "str"}),
        # --- 五步决策协议 + 四人组张量 + 涌现链 ---
        SkillSpec("dao_define_problem", dao_define_problem,
                  "道步：定义优化问题本体（设计变量+目标函数+约束条件）",
                  tags=["quartet", "dao", "optimization", "ontology"],
                  inputs={"variables": "str", "objective": "str", "constraints": "str"}),
        SkillSpec("fa_gradient_analysis", fa_gradient_analysis,
                  "法步：梯度方向+泰勒预测+凸性判断（可治理性）",
                  tags=["quartet", "fa", "gradient", "convexity"],
                  inputs={"current": "str", "perturbation": "str"}),
        SkillSpec("shu_constraint_handling", shu_constraint_handling,
                  "术步：拉格朗日乘子+KKT条件+惩罚函数（约束处理）",
                  tags=["quartet", "shu", "lagrangian", "kkt"],
                  inputs={"constraints": "str", "violations": "str"}),
        SkillSpec("qi_algorithm_selection", qi_algorithm_selection,
                  "器步：搜索算法选择决策树（梯度/牛顿/共轭/DFP/单纯形）",
                  tags=["quartet", "qi", "algorithm", "search"],
                  inputs={"problem_type": "str", "dimension": "int"}),
        SkillSpec("quartet_tensor", quartet_tensor,
                  "四人组张量向量化：权重矩阵+共振检测+决策熵+涌现判断",
                  tags=["quartet", "tensor", "resonance", "emergence"],
                  inputs={"p1": "str", "p2": "str", "p3": "str", "p4": "str"}),
        SkillSpec("emergence_chain", emergence_chain,
                  "涌现链完整闭环：道→法→术→器→升维→共振→涌现",
                  tags=["quartet", "emergence", "chain", "protocol"],
                  inputs={"input_concept": "str"}),
        # --- 城邦治理（V11-D：第八层可观测与治理）---
        SkillSpec("city_state_governance", city_state_governance,
                  "城邦治理：循环检测 + 熔断 + 重试策略（Guardrail/Policy/Audit）",
                  tags=["governance", "circuit_breaker", "loop_detection", "retry"],
                  inputs={"calls": "str", "threshold": "int",
                          "retry_policy": "str"}),
        SkillSpec("dissipation_emergence_monitor",
                  dissipation_emergence_monitor,
                  "耗散涌现监控：Observability + Traceability + 耗散熵趋势",
                  tags=["observability", "monitor", "traceability", "emergence"],
                  inputs={"task_flow": "str", "window": "int"}),
    ]

    roles = [
        RoleSpec("topology_architect", "拓扑架构师：共振·扩散·翻转",
                 ["resonance_node", "mandala_fanout", "mobius_edge"]),
        RoleSpec("convergence_guardian", "收敛守护者：汇聚·守卫·耗散",
                 ["klein_convergence", "bayesian_guard", "dissipation_measure"]),
        RoleSpec("state_estimator", "状态估计师：滤波·投影",
                 ["kalman_state", "hilbert_project"]),
        RoleSpec("quartet_strategist", "四人组策略师：道·法·术·器·张量",
                 ["dao_define_problem", "fa_gradient_analysis",
                  "shu_constraint_handling", "qi_algorithm_selection",
                  "quartet_tensor"]),
        RoleSpec("emergence_architect", "涌现架构师：五步闭环·涌现验证",
                 ["emergence_chain", "quartet_tensor", "hilbert_project"]),
    ]

    workflows = [
        WorkflowSpec("topology_resonance_flow",
                     ["topology_architect", "state_estimator", "convergence_guardian"],
                     "拓扑共振：共振检测→状态估计→收敛守护（自组织相似性耗散涌现）"),
        WorkflowSpec("quartet_decision_flow",
                     ["quartet_strategist", "emergence_architect"],
                     "四人组决策：道→法→术→器→升维→共振→涌现（五步协议闭环）"),
    ]


def pack_summary() -> Dict[str, Any]:
    p = TopologyResonancePack()
    return {"key": p.key, "skills": len(p.skills), "roles": len(p.roles),
            "workflows": len(p.workflows)}


# ============================================================ 15. Graph 集成（V11-A）
def _check_graph_node(graph: Any, node: int) -> Optional[str]:
    """校验 graph 是否为 AdaptiveGraph 且节点 id 在范围内（确定性错误信息）。

    只读校验，不修改任何图状态。
    """
    if not all(hasattr(graph, a) for a in ("n", "nodes", "weights")):
        return "graph 非 AdaptiveGraph（缺少 n/nodes/weights）"
    if not (0 <= node < graph.n):
        return f"节点越界：{node} 不在 [0,{graph.n})"
    return None


def graph_mandala_expand(graph: Any, center_node_id: int = 0,
                         fanout: int = 8, **_: Any) -> dict:
    """曼陀罗扇出：以 center 为中心，向 fanout 个空闲节点建立出边（Fan-out）。

    城邦映射：Fan-out/Fan-in 模式 → Subgraph 嵌套。
    实现：不改 graph.py，仅操作 graph.weights 建立中心→子节点边；
    子节点 = 与中心无既有边、且负载最低的空闲节点（确定性选择）。
    图节点数量固定（AdaptiveGraph node_count），本函数只连边、不增删节点。
    """
    err = _check_graph_node(graph, center_node_id)
    if err:
        return {"topology": "mandala_expand", "error": err}
    fanout = max(1, min(int(fanout), graph.n - 1))
    # 确定性选择子节点：未与中心相连，按 (节点负载, id) 升序
    candidates = []
    for j in range(graph.n):
        if j == center_node_id or graph.weights[center_node_id][j] > 0:
            continue
        candidates.append((graph.nodes[j].load, j))
    candidates.sort()
    children = [j for _, j in candidates[:fanout]]
    edge_weight = 0.5  # 曼陀罗引导权：中心→方位
    for j in children:
        graph.weights[center_node_id][j] = edge_weight
        graph.weights[j][center_node_id] = edge_weight
    return {
        "topology": "mandala_expand",
        "center": center_node_id,
        "center_name": graph.nodes[center_node_id].name,
        "fanout_requested": fanout,
        "children": [{"node": j, "name": graph.nodes[j].name} for j in children],
        "edges_added": len(children),
        "edge_weight": edge_weight,
        "note": "曼陀罗扇出：中心→N 子节点（仅连边，不新增节点）",
    }


def graph_mobius_flip(graph: Any, node_a: int = 0, node_b: int = 1,
                      **_: Any) -> dict:
    """莫比乌斯翻转：在 node_a 与 node_b 之间建立双向回边（Back Edge）。

    城邦映射：Cyclic Graph → 重试/反思/迭代循环。
    回边权重 = max(原权重, 0.4) + 0.3（反馈增强），建边后用 DFS 检测环。
    """
    err = _check_graph_node(graph, node_a) or _check_graph_node(graph, node_b)
    if err:
        return {"topology": "mobius_flip", "error": err}
    if node_a == node_b:
        return {"topology": "mobius_flip",
                "error": f"自环不允许：{node_a}=={node_b}"}
    base = max(graph.weights[node_a][node_b], 0.4)
    flip_w = round(min(1.0, base + 0.3), 3)  # 回边增强
    graph.weights[node_a][node_b] = flip_w
    graph.weights[node_b][node_a] = flip_w
    cycles = graph.detect_cycles()
    return {
        "topology": "mobius_flip",
        "node_a": node_a,
        "node_b": node_b,
        "back_edge_weight": flip_w,
        "edge_type": "back_edge",
        "cycles_detected": len(cycles),
        "cycles": cycles[:5],
        "note": "莫比乌斯翻转：双向回边 → 反馈循环（可重试/反思/迭代）",
    }


def graph_klein_convergence(graph: Any, max_iter: int = 100,
                            threshold: float = 0.3, **_: Any) -> dict:
    """克莱因收敛：迭代收敛图权重直到拓扑稳定，含熔断。

    收敛规则（确定性）：每轮把每条边权重向全局平均密度靠拢：
      w' = w + η·(avg − w)，η = 0.1；两轮间最大绝对变化 < threshold 或达
      max_iter 即停止。熔断：变化量连续三轮单调上升（发散迹象）→ 熔断。

    城邦映射：克莱因瓶 → 无边界动态平衡态 → Circuit Breaker。
    """
    if not all(hasattr(graph, a) for a in ("n", "nodes", "weights", "edge_list")):
        return {"topology": "klein_convergence", "error": "graph 非 AdaptiveGraph"}
    max_iter = max(1, min(int(max_iter), 1000))
    eta = 0.1
    prev_delta: Optional[float] = None
    rising = 0
    circuit_breaker = False
    final_delta = 0.0
    iterations = 0
    for it in range(max_iter):
        total = 0.0
        count = 0
        for i in range(graph.n):
            for j in range(i + 1, graph.n):
                if graph.weights[i][j] > 0:
                    total += graph.weights[i][j]
                    count += 1
        avg = total / count if count else 0.0
        max_delta = 0.0
        for i in range(graph.n):
            for j in range(i + 1, graph.n):
                w = graph.weights[i][j]
                if w <= 0:
                    continue
                nw = round(w + eta * (avg - w), 6)
                nw = max(0.0, min(1.0, nw))
                delta = abs(nw - w)
                if delta > max_delta:
                    max_delta = delta
                graph.weights[i][j] = nw
                graph.weights[j][i] = nw
        iterations = it + 1
        final_delta = max_delta
        if prev_delta is not None:
            if max_delta > prev_delta:
                rising += 1
                if rising >= 3:
                    circuit_breaker = True
                    break
            else:
                rising = 0
        prev_delta = max_delta
        if max_delta < threshold:
            break
    return {
        "topology": "klein_convergence",
        "iterations": iterations,
        "max_iter": max_iter,
        "converged": (not circuit_breaker) and (final_delta < threshold),
        "circuit_breaker": circuit_breaker,
        "final_weight_delta": round(final_delta, 6),
        "threshold": threshold,
        "edges_after": len(graph.edge_list()),
        "note": "克莱因收敛：权重迭代向平均密度靠拢；发散连续三轮→熔断",
    }
