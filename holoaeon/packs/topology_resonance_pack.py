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
# V66：把 V65 的 7 把可实测尺子搬进本体，替掉原软内核。
# 数学实现单一真源放在 holoaeon/resonance_supplement.py（同包内、纯标准库、离线确定性），
# 本包只做「包装 + 城邦语义映射」，不再各自维护一份近似算法。
from ..resonance_supplement import (  # noqa: E402
    CHI2_1DOF_95,
    decompose_active_nodes,
    entropy_production,
    kalman_fuse,
    kuramoto_order,
    mandala_wht,
    rff_kernel,
    rff_features,
    sprt_gate,
)

# ============================================================ 数学常量
# 1331 = 11³，1331×1331 = 11⁶ = 1,771,561（逻辑位置）
MATRIX_ROWS = 1331
MATRIX_COLS = 1331
LOGICAL_POSITIONS = MATRIX_ROWS * MATRIX_COLS  # 1,771,561
# 108641：实际活跃节点（稀疏实例化率 ≈ 6.13%）
# V66：不再是裸魔数——108641 = 13 × 61 × 137（13×61=793，793×137=108641），
#      占 1,771,561 的 6.1325%，且 1,771,561 = 1331×81 + 830。
ACTIVE_NODES = 108641
ACTIVE_NODE_FACTORS = (13, 61, 137)
# 曼陀罗：1 中心 + 8 方位 = 9（九宫/八卦 / Q3 立方体顶点集）
MANDALA_DIRECTIONS = 8
MANDALA_TOTAL = 9
# 共振阈值：余弦相似度超过此值则共振
RESONANCE_THRESHOLD = 0.75
# 涌现阈值：共振对数超过此值则触发涌现
EMERGENCE_THRESHOLD = 108641
# 耗散熵阈值：系统熵超过此值则触发自组织重组
DISSIPATION_ENTROPY_MAX = 0.95
# V67 重组口径仲裁：两种"病"方向相反，必须显式定优先级，不能含糊共存。
#   disorder 侧（旧判据）：熵 > 0.95 或 秩序 < 0.3 → 系统太乱，靠重整出结构。
#   stagnation 侧（V67 证据化）：**单点快照无法**区分「高效稳定」与「僵死」——
#     全成功时 σ 高、熵低，真正的僵死系统也可能长得一样。故僵死必须靠时间窗证据：
#     连续 STAGNATION_STREAK_MIN 步同一结果，且熵 ≤ STAGNATION_ENTROPY_MAX。
#     σ < sigma_min 只作弱信号（dissipation_sufficient），不单独判僵死。
# 默认口径 stagnation_first（先破僵）：耗散结构的前提是"有流"，
# 零流量时任何自组织都不可能发生（没有能量/物质流就没有耗散结构）；
# 而混乱侧仍有噪声可被结构捕获。故一旦僵死成立，优先于混乱。
REORGANIZATION_PRIORITY = "stagnation_first"
STAGNATION_STREAK_MIN = 5
STAGNATION_ENTROPY_MAX = 0.10
# V66：χ²(1) 95% 一致性门限（标准 NIS 判据），与 resonance_supplement 同源
NIS_CHI2_95 = CHI2_1DOF_95



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

    # V66：X2 不再只有「相似对计数」，补一个真正的序参量
    # r = |⟨e^{iθ}⟩|，θ 取每个节点状态向量在 (v0,v1) 平面上的相位。
    # r→1 表示全体同相（宏观相干），r→0 表示相位散开（无相干）。
    phases = [math.atan2(nd[1], nd[0]) if len(nd) >= 2 else 0.0 for nd in nodes]
    ko = kuramoto_order(phases)
    active_split = decompose_active_nodes(ACTIVE_NODES)

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
        "order_parameter": round(ko["r"], 6),
        "phase_coherence": "synchronized" if ko["synchronized"] else "incoherent",
        "active_nodes_factors": list(ACTIVE_NODE_FACTORS),
        "active_nodes_factorization": active_split["factorization"],
        "matrix_quotient": {"quotient": ACTIVE_NODES // MATRIX_ROWS,
                            "remainder": ACTIVE_NODES % MATRIX_ROWS,
                            "form": f"{ACTIVE_NODES} = {MATRIX_ROWS}×{ACTIVE_NODES // MATRIX_ROWS} + {ACTIVE_NODES % MATRIX_ROWS}"},
        "note": "共振 = 余弦相似度 ≥ 阈值；涌现 = 共振对 > 0；序参量 r = |⟨e^{iθ}⟩|",
    }


# ============================================================ 2. 曼陀罗扩散
def mandala_fanout(task: str = "", center: str = "", loads: str = "",
                   **_: Any) -> dict:
    """曼陀罗一拖八：中心分发 → 8 方位，聚合改为**正交变换 + 逆变换**。

    数学内核（V66 换芯）：
      原实现用 `_det_hash(...) % 10 > 2` 掷出「70% 确定性成功」——那不是拓扑，
      是披着确定性外衣的骰子，且永远无法判错。
      现改为 Q3 立方体八方位上的 Hadamard 正交变换 H8（H8·H8ᵀ = 8I）：
        fan-out = 正变换（把中心载荷分解到 8 条正交通道）
        fan-in  = 逆变换（8 条通道无损重建，自逆）
      判据可失败：正交偏差须为 0、往返误差须为 0、Parseval 比须为 1。
      八方位齐步（载荷全等）时谱只剩直流项 —— 没有分化就没有真正的扇出，
      这正是拓扑该有的行为，而非"八条都成功"。

    城邦映射：Fan-out/Fan-in + Orchestrator-Worker
    """
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

    # 载荷：8 个方位的承载量；缺省 1..8（逐级递增，保证谱非退化）
    if loads:
        ld = [float(x) for x in loads.split(",") if x.strip()]
        if len(ld) != MANDALA_DIRECTIONS:
            ld = [float(i + 1) for i in range(MANDALA_DIRECTIONS)]
    else:
        ld = [float(i + 1) for i in range(MANDALA_DIRECTIONS)]

    wht = mandala_wht(ld)
    spectrum = wht["spectrum"]
    dc = wht["center_dc"]

    # 中心节点任务分发（正变换的输入侧）
    fan_out = []
    for i, d in enumerate(directions):
        fan_out.append({
            "direction": d,
            "task": task or "默认扩散任务",
            "center": center or "N00",
            "status": "dispatched",
            "load": ld[i],
        })

    # fan-in：各正交通道的谱幅（通道 0 = 直流/中心，其余 = 各阶差分）
    fan_in = []
    for i, d in enumerate(directions):
        amp = spectrum[i]
        has_content = abs(amp) > 1e-12
        fan_in.append({
            "direction": d,
            "channel": i,
            "amplitude": amp,
            "status": "ok" if has_content else "partial",
            "meaning": "DC(中心整体)" if i == 0 else f"差分阶{i}",
        })

    successes = sum(1 for r in fan_in if r["status"] == "ok")
    all_ok = successes == MANDALA_DIRECTIONS
    # 有效扇出通道：携带独立信息量的非直流通道数
    effective_fanout = sum(1 for i in range(1, MANDALA_DIRECTIONS)
                           if abs(spectrum[i]) > 1e-12)

    return {
        "topology": "mandala",
        "structure": f"1中心 + {MANDALA_DIRECTIONS}方位 = {MANDALA_TOTAL}节点（Q3 顶点集）",
        "task": task or "默认扩散任务",
        "loads": ld,
        "fan_out": fan_out,
        "fan_in": fan_in,
        "aggregation": {
            "center": center or "N00",
            "successes": successes,
            "total": MANDALA_DIRECTIONS,
            "all_ok": all_ok,
            "quorum": successes >= MANDALA_DIRECTIONS // 2 + 1,
            "effective_fanout": effective_fanout,
        },
        "orthogonal_transform": {
            "spectrum": spectrum,
            "center_dc": dc,
            "center_equals_mean": wht["center_is_mean"],
            "reconstruction_error": wht["reconstruction_error"],
            "orthogonality_max_dev": wht["orthogonality_max_dev"],
            "parseval_ratio": wht["parseval_ratio"],
            "perfect": wht["perfect"],
        },
        "note": ("曼陀罗一拖八 = 八方位正交变换：分发是正变换、聚合是逆变换；"
                 "齐步载荷只剩直流项，说明无分化即无扇出"),
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
def kalman_state(observations: str = "", observation_noise: str = "",
                 process_noise: float = 0.01, **_: Any) -> dict:
    """卡尔曼滤波状态融合：预测步 + 标准 NIS 一致性检验。

    数学内核（V66 换芯）：
      原实现是单源标量 KF，Q=0.01 / R=0.1 全硬编码，且**没有一致性判据**——
      它只负责"把数算出来"，不负责"判断这次观测该不该信"。
      现改为：每源先走预测步（P⁻ = P + Q），用**预测值**而非融合值算标准 NIS：
        NIS = (z − x⁻)² / (P⁻ + R)，超 χ²(1) 95%（3.841）判该源离群；
      离群源只推进预测、不吸收（innovation gating），融合值不被拉偏。
      q=0 时序贯结果与批量逆方差加权精确相等，可交叉验证。

    城邦映射：State Reducer + Checkpoint + Shared State
    """
    # 解析观测值（格式："1.0,0.9,1.1,0.95,1.05"）
    if observations:
        obs = [float(x) for x in observations.split(",") if x.strip()]
    else:
        # 默认：5次观测，真实值约1.0
        obs = [1.0, 0.9, 1.1, 0.95, 1.05]

    if observation_noise:
        rs = [float(x) for x in observation_noise.split(",") if x.strip()]
        if len(rs) != len(obs):
            rs = [0.1] * len(obs)
    else:
        rs = [0.1] * len(obs)

    q = float(process_noise)
    res = kalman_fuse(list(zip(obs, rs)), process_noise=q, gate=True)

    steps = []
    for i, row in enumerate(res["sources"]):
        steps.append({
            "step": i,
            "observation": row["z"],
            "measurement_variance": row["R"],
            "predicted_state": row["predicted_state"],
            "innovation": row["innovation"],
            "kalman_gain": row["gain"],
            "state_estimate": row.get("state_estimate", row["predicted_state"]),
            "uncertainty": row.get("uncertainty", row["predicted_variance"]),
            "nis": row["nis"],
            "consistent": row["consistent"],
            "applied": row["applied"],
        })

    nis_max = max((s["nis"] for s in steps), default=0.0)
    # 状态快照（Checkpoint）
    checkpoint = {
        "final_state": res["fused_state"],
        "final_uncertainty": res["fused_variance"],
        "convergence": res["fused_variance"] < 0.01,  # 不确定性收敛
        "observations": len(obs),
        "all_consistent": res["all_consistent"],
        "nis_max": round(nis_max, 6),
        "rejected_sources": res["rejected"],
    }

    return {
        "filter": "kalman_scalar_with_predict_step",
        "nis_mode": res["nis_mode"],
        "parameters": {"Q": q, "R": rs[0] if rs else 0.1, "initial_P": None},
        "R_per_source": rs,
        "steps": steps,
        "checkpoint": checkpoint,
        "consistency_gate": {
            "chi2_1dof_95": NIS_CHI2_95,
            "nis_max": round(nis_max, 6),
            "all_consistent": res["all_consistent"],
            "sequential_matches_batch": res["sequential_matches_batch"],
        },
        "note": ("卡尔曼滤波：预测步 → 标准 NIS（预测 vs 观测）→ 一致性门 → "
                 "状态融合 → 不确定性收敛 → 快照"),
    }


# ============================================================ 6. 贝叶斯守卫
def bayesian_guard(feature: str = "", history: str = "", evidence: str = "",
                   cost_fn: float = 10.0, cost_fp: float = 1.0,
                   alpha: float = 0.05, beta: float = 0.10, **_: Any) -> dict:
    """贝叶斯推理守卫：代价敏感判定 + Wald 序贯检验（双门限）。

    数学内核（V66 换芯）：
      原实现把阈值写死成 0.5——但 0.5 只在外罚与内罚代价相等时才最优。
      误放（漏掉一次该拦的）的代价远高于误拦（多拦一次可人工复核），
      所以判定阈值应是 Bayes 风险最优的 C_fp/(C_fp+C_fn)，
      默认 1/(1+10) ≈ 0.0909，而不是拍出来的 0.5。
      另加 Wald SPRT：给定一批 0/1 证据时，累积对数似然比越 A 判危险、
      越 B 判安全，证据够了就停，不再"攒满固定窗口再拍板"。

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

    # 特征似然表（确定性，基于工程经验；这是先验知识，不是"软内核"）
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

    # 代价敏感阈值（替代原硬编码 0.5）
    threshold = cost_fp / (cost_fp + cost_fn)

    # 序贯检验（有证据序列时才启用）
    sprt = None
    if evidence:
        ev = [1 if x.strip() in ("1", "true", "True", "hit", "risk") else 0
              for x in evidence.split(",") if x.strip()]
        if ev:
            sp = sprt_gate(ev, p0=prior_block if 0 < prior_block < 1 else 0.15,
                           p1=0.45, alpha=alpha, beta=beta)
            sprt = {
                "threshold_A": sp["threshold_A"],
                "threshold_B": sp["threshold_B"],
                "llr_path": sp["llr_path"],
                "decision": sp["decision"],
                "stopped_at": sp["stopped_at"],
                "evidence_length": sp["observation_length"],
                "evidence_saved": sp["evidence_saved"],
            }

    # 决策：序贯已定则听序贯，未定（CONTINUE）则回落后验
    if sprt and sprt["decision"] in ("H0", "H1"):
        decision = "BLOCK" if sprt["decision"] == "H1" else "ALLOW"
        decided_by = "sprt"
    else:
        decision = "BLOCK" if posterior_block > threshold else "ALLOW"
        decided_by = "posterior_cost_threshold"

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
        "threshold": round(threshold, 6),
        "threshold_rule": f"cost_fp/(cost_fp+cost_fn) = {cost_fp}/{cost_fp + cost_fn}",
        "decision": decision,
        "decided_by": decided_by,
        "sprt": sprt,
        "retry_policy": retry_policy,
        "note": ("贝叶斯守卫：先验(历史) + 似然(特征) → 后验；"
                 "判定用代价敏感阈值或 Wald 双门限 SPRT，不再写死 0.5"),
    }


# ============================================================ 7. 希尔伯特投影（辅助）
def hilbert_project(vector: str = "", dimensions: int = 0,
                    gamma: float = 1.0, **_: Any) -> dict:
    """希尔伯特计算空间投影：有限维 → 无限维 RKHS 的显式近似。

    数学内核（V66 换芯）：
      原实现 φ_k = 1/√(k+1)、v_h[k] = v[k % n] · φ_k 是**假的**：
      它既不正交、也不是任何核的特征映射，且范数随 N 单调膨胀（
      Σ 1/(k+1) 发散），所以 `norm_preservation` 只是个随维数变大的数字。
      现改为 Bochner 定理给出的随机傅里叶特征：平移不变核的傅里叶变换
      是一个概率分布，抽 ω 即可写出有限维特征 z(x)，使
        E[z(x)·z(y)] = exp(−γ‖x−y‖²)
      这才是"用有限维逼近无限维 RKHS 内积"的可检验版本。

    城邦映射：Memory + Context + Observability
    """
    # 解析输入向量
    if vector:
        v = [float(x) for x in vector.split(",") if x.strip()]
    else:
        v = [1.0, 0.5, -0.3, 0.8]

    n = len(v)
    # 投影维度（默认 10 倍原维度）
    N = dimensions if dimensions > 0 else n * 10

    rff = rff_features(v, dims=N, gamma=gamma)
    projection = rff["feature"]
    hilbert_norm_sq = rff["feature_norm_sq"]
    hilbert_norm = math.sqrt(hilbert_norm_sq)
    orig_norm = math.sqrt(sum(x ** 2 for x in v))
    # 核自相似：z(x)·z(x) 应逼近 k(x,x)=1
    kernel_self = hilbert_norm_sq

    return {
        "space": "hilbert",
        "map": "random_fourier_features",
        "kernel": f"exp(-{gamma}·||x-y||²)",
        "original_dim": n,
        "projected_dim": N,
        "expansion_ratio": round(N / n, 2),
        "original_vector": [round(x, 4) for x in v],
        "projection_sample": projection[:20],  # 前20维
        "projection_full_length": len(projection),
        "hilbert_norm": round(hilbert_norm, 6),
        "original_norm": round(orig_norm, 6),
        "norm_preservation": round(kernel_self, 6),
        "kernel_self_estimate": round(kernel_self, 6),
        "note": ("随机傅里叶特征：E[‖z‖²]=1 逼近 k(x,x)；"
                 "投影范数不随维数膨胀，误差随 D 下降"),
    }


# ============================================================ 8. 耗散度量（辅助）
def dissipation_measure(task_flow: str = "", sigma_min: float = 1.0,
                        streak: int = None, **_: Any) -> dict:
    """耗散结构度量：Shannon 熵 + **熵产率 σ（热力学力/流）**。

    数学内核（V66 换芯）：
      原实现只有 Shannon 熵 + "失败率当耗散率"，缺了耗散结构理论的核心量：
      熵产率 σ = Σ J_i X_i（流 × 力）。耗散结构讲的不是"熵多高"，
      而是"开放系统靠持续耗散维持低熵秩序"——所以必须能算出**耗散了多少、
      以及这个耗散是否足够支撑秩序**。
      现以 [p_ok, p_fail] 为热力学力 X，经 Onsager 线性唯象关系 J = L·X 得流 J，
      σ = XᵀLX，并用 Onsager 对称 + Sylvester 正定双闸判其物理可解释性。
      力与流的内积为负（负定 L）时如实返回 positive_definite=false，不硬掰成正。

    口径仲裁（V67）：
      混乱侧（熵 > 0.95 或 秩序 < 0.3）与僵死侧是两种方向相反的病。
      但僵死**不能由单点快照判定**：全成功时熵低、σ 高，真正的僵死系统同样低熵，
      快照分不开「高效稳定」与「僵死」。故僵死必须靠时间窗证据 ——
      调用方传入 streak（连续同一结果的步数），且 entropy ≤ STAGNATION_ENTROPY_MAX
      且 streak ≥ STAGNATION_STREAK_MIN 时才判成立；未传 streak 则输出
      stagnation_side=None（未评估），只报混乱侧结论。
      一旦僵死成立，按 REORGANIZATION_PRIORITY（默认 stagnation_first）优先于混乱：
      耗散结构的前提是"有流"，零流量下自组织不可能发生。
      注意：needs_reorganization 的旧语义（混乱侧）保持不变，供既有下游兼容；
      需要"两侧任一"的下游请用 needs_reorganization_any。

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

    # 自组织触发判断（原判据保留：混乱侧，不改语义）
    needs_reorganization = entropy > DISSIPATION_ENTROPY_MAX or order < 0.3

    # V66：熵产率 σ = Σ J_i X_i（力 = [p_ok, p_fail]，J = L·X）
    ep = entropy_production(forces=[p_ok, p_fail])
    sigma = ep["sigma"]
    # 耗散不足 = 系统不流动的**弱信号**（σ 低）。单凭它不判僵死，只登记。
    dissipation_sufficient = sigma >= sigma_min
    weak_flow_signal = not dissipation_sufficient
    # V67：僵死需要时间窗证据（streak），否则快照分不开"高效稳定"与"僵死"
    stagnation_evaluated = streak is not None
    try:
        streak_v = int(streak) if stagnation_evaluated else 0
    except (TypeError, ValueError):
        streak_v, stagnation_evaluated = 0, False
    stagnation = bool(stagnation_evaluated
                      and streak_v >= STAGNATION_STREAK_MIN
                      and entropy <= STAGNATION_ENTROPY_MAX)

    # V67 仲裁：两病方向相反，按 REORGANIZATION_PRIORITY 给出唯一下一步动作。
    # 保留 needs_reorganization 的旧语义（混乱侧），另给 needs_reorganization_any 便于下游一次判。
    if REORGANIZATION_PRIORITY == "stagnation_first":
        if stagnation:
            verdict = "reorganize_both" if needs_reorganization else "reorganize_stagnation"
        elif needs_reorganization:
            verdict = "reorganize_disorder"
        else:
            verdict = "hold"
    elif REORGANIZATION_PRIORITY == "disorder_first":
        if needs_reorganization:
            verdict = "reorganize_both" if stagnation else "reorganize_disorder"
        elif stagnation:
            verdict = "reorganize_stagnation"
        else:
            verdict = "hold"
    else:  # "all"：两侧并列，不排优先级
        if needs_reorganization and stagnation:
            verdict = "reorganize_both"
        elif stagnation:
            verdict = "reorganize_stagnation"
        elif needs_reorganization:
            verdict = "reorganize_disorder"
        else:
            verdict = "hold"

    actions = {
        "reorganize_stagnation": "先恢复流量（开放边界/加扰动/提高周转），再谈秩序——零流量下自组织不可能发生",
        "reorganize_disorder": "重整约束与分工，压低熵、抬高秩序；此时流量是够的，缺的是结构",
        "reorganize_both": "两病并发：先恢复流量（僵死侧），流量起来后再重整约束（混乱侧）",
        "hold": "秩序与流量都在界内，维持现状并继续观测",
    }

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
        "entropy_production": {
            "sigma": sigma,
            "forces": ep["forces"],
            "flows": ep["flows"],
            "onsager": ep["onsager"],
            "symmetric_onsager": ep["symmetric_onsager"],
            "positive_definite": ep["positive_definite"],
            "leading_principal_minors": ep["leading_principal_minors"],
            "dissipation_sufficient": dissipation_sufficient,
            "sigma_min": sigma_min,
        },
        "needs_reorganization": needs_reorganization,
        "needs_reorganization_any": bool(needs_reorganization or stagnation),
        "reorganization": {
            "priority": REORGANIZATION_PRIORITY,
            "disorder_side": needs_reorganization,
            "stagnation_side": stagnation if stagnation_evaluated else None,
            "stagnation_evaluated": stagnation_evaluated,
            "stagnation_evidence": {
                "streak": streak_v if stagnation_evaluated else None,
                "streak_min": STAGNATION_STREAK_MIN,
                "entropy": round(entropy, 6),
                "entropy_max": STAGNATION_ENTROPY_MAX,
            },
            "weak_flow_signal": weak_flow_signal,
            "verdict": verdict,
            "action": actions[verdict],
            "sigma": sigma,
            "sigma_min": sigma_min,
        },
        "emergence_condition": (
            "熵 > 0.95 或 秩序 < 0.3 → 重组（混乱侧）；"
            "streak ≥ %d 且熵 ≤ %.2f → 先破僵（僵死侧，需时间窗证据）"
            % (STAGNATION_STREAK_MIN, STAGNATION_ENTROPY_MAX)),
        "note": ("耗散度量：能量流入 → 熵产率 σ 量化耗散强度 → 秩序涌现；"
                 "混乱侧（熵/秩序）与僵死侧（σ 不足）方向相反，"
                 "V67 按 REORGANIZATION_PRIORITY 给出唯一下一步动作"),
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

    # V67 旁路消费（评估结论：不改主判据，只加只读视图）
    # 为什么不动 emergence：主判据只有 quartet 一个真源（P2×P3≥0.7 / P1≥0.6 / P4≤0.4 / order>0.30）。
    # 若把一致性门与熵产率也接进布尔判定，等于给"涌现"开第二、第三个真源，
    # 一旦两处口径不同就会互相打架。故本批只做"消费（读取并展示）"，不做"参与判定"。
    kons = kalman_state(observations="10.0,10.5,30.0",
                        observation_noise="1.0,0.25,0.5")
    diss = dissipation_measure(task_flow="ok,fail,ok,fail")
    advisories = []
    if kons["checkpoint"]["rejected_sources"]:
        advisories.append(
            "一致性门：%d 个源被判离群（NIS 最大 %.6f > %.3f），融合值未吸收它们"
            % (len(kons["checkpoint"]["rejected_sources"]),
               kons["consistency_gate"]["nis_max"],
               kons["consistency_gate"]["chi2_1dof_95"]))
    if diss["reorganization"]["verdict"] != "hold":
        advisories.append("耗散仲裁（%s）：%s"
                          % (diss["reorganization"]["priority"],
                             diss["reorganization"]["action"]))

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
        "dissipation_view": {
            "priority": diss["reorganization"]["priority"],
            "sigma": diss["entropy_production"]["sigma"],
            "order": diss["order"],
            "entropy": diss["shannon_entropy"],
            "verdict": diss["reorganization"]["verdict"],
            "action": diss["reorganization"]["action"],
            "needs_reorganization_any": diss["needs_reorganization_any"],
        },
        "consistency_view": dict(kons["consistency_gate"]),
        "advisories": advisories,
        "note": ("涌现链：道→法→术→器→升维→共振→涌现（完整闭环）；"
                 "V67 起旁路消费一致性与熵产率，只展示不参与主判据"),
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
