# -*- coding: utf-8 -*-
"""
CircuitGate —— 电子域算子蒸馏（ring17）
================================================================================
源声明（诚实边界）：
  · 灵感源 = 电路学标准学科公理（基尔霍夫定律 / RLC 谐振 / 负反馈 / 忆阻器 /
    阻抗匹配），视频标题《一部影片以最簡單的方式學會電路學》锁定领域。
  · 视频逐字稿不可得（无 CC 字幕 + yt-dlp bot 拦截，2026-11-09 三站核实），
    本模块不含视频逐字稿内容 —— 与 V43/V45 的指针纪律 B 方案同款。
  · 物理隐喻 → 认知算子的映射是工程类比，不是物理仿真。neural=false，
    无神经网络训练，全部为确定性数学映射。

六件套（电路公理 → 认知算子）：
  · KirchhoffFlow  KCL 节点流量守恒 / KVL 回路一致性 → 消息守恒与传递闭环校验
  · ResonatorNode  RLC 谐振（频率+相位+Q 品质因数）→ 节点共振匹配，
                    比余弦相似多出相位维度
  · FeedbackAmp    负反馈误差校正（环路增益/稳定裕度）→ 监督学习误差回路的
                    物理直觉框架（增益过高=发散, 过低=收敛慢）
  · MemristorSynapse 忆阻器 dM/dt = k·I ↔ 赫布 Δw = η·x·y，
                    含漏电衰减 + 阻态保持 —— 对 AdaptiveGraph.hebbian_step 的
                    每突触补强（后者为共激活组两两增强，无遗忘曲线）
  · ImpedanceMatch 阻抗匹配（反射系数 Γ）→ 接口转换效率（发送/接收侧失配损耗）
  · TensorCircuit  张量向量转换：电路概念表 → hypervector 编码（角色-填充绑定 +
                    D/X 张量轴，klein_projection.TensorCoupler 先例）

装配纪律：真实复用 holoaeon.hypervector.HypervectorSpace 与
holoaeon.graph.AdaptiveGraph —— 装配不重写，零新依赖，纯标准库。
"""

from __future__ import annotations

import hashlib
import math
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from .hypervector import HypervectorSpace
from .graph import AdaptiveGraph

# ---------------------------------------------------------------- 链位
CHAIN_POSITION = {
    "ring": 17,
    "layer": "operator",
    "domain": "电子（电路学算子蒸馏）",
    "batch": "V51",
    "upstream": [
        "klein_projection(TensorCoupler 张量耦合先例)",
        "graph(AdaptiveGraph.hebbian_step 赫布先例)",
        "hypervector(Hyperspace D/X 张量轴载体)",
        "forge_gate(ring16 装配上游)",
    ],
}

# 封口密语（校验锚点）
SEAL = "潮起开门，潮落闭嘴"

# ---------------------------------------------------------------- 工具


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _now_iso() -> str:
    import datetime
    return datetime.datetime.now().isoformat(timespec="seconds")


# ================================================================ 一、KCL/KVL


class KirchhoffFlow:
    """基尔霍夫定律 → 消息流守恒校验。

    KCL（节点电流定律）：任一节点流入之和 = 流出之和。
    认知映射：消息中继节点不凭空产生/消灭信息 —— 转发守恒。

    KVL（回路电压定律）：任一回路压降之和 = 0。
    认知映射：相似度沿回路传递的乘积一致性（log 域求和 ≈ 0），
    违反即"传递性破缺"（A~B, B~C 但 A≁C 的环路矛盾检测）。
    """

    def __init__(self, graph: Optional[AdaptiveGraph] = None):
        self.graph = graph

    # -------------------------------------------------- KCL
    def kcl_check(self, flows: Dict[Tuple[int, int], float],
                  internal_nodes: Optional[List[int]] = None) -> dict:
        """对边流量表做节点守恒校验（KCL）。

        flows: {(u,v): weight} —— u→v 的消息流量（有向）。
        internal_nodes:
          · None  —— 全严格模式：所有节点都是内部中继，必须平衡；
          · []    —— 全外部模式：所有失衡都记为 source/sink（合法端口）；
          · [id…] —— 混合模式：清单内节点必须平衡（内部中继），
                      清单外节点失衡记 source/sink（外部端口），不违例。

        违例定义：内部中继节点 balance ≠ 0（消息凭空产生/消灭）。
        """
        if not flows:
            return {"ok": True, "violations": [], "nodes": {},
                    "note": "空流量表，守恒平凡成立"}
        node_ids = set()
        for (u, v) in flows:
            node_ids.add(u)
            node_ids.add(v)
        inflow: Dict[int, float] = {n: 0.0 for n in node_ids}
        outflow: Dict[int, float] = {n: 0.0 for n in node_ids}
        for (u, v), w in flows.items():
            outflow[u] = outflow.get(u, 0.0) + w
            inflow[v] = inflow.get(v, 0.0) + w
        if internal_nodes is None:
            internal_set = set(node_ids)  # 全严格
        else:
            internal_set = set(internal_nodes) & node_ids  # 指定中继域
        violations = []
        tol = 1e-9
        nodes_report = {}
        for n in sorted(node_ids):
            balance = round(inflow[n] - outflow[n], 9)
            # 外部端口允许不平衡（注入/吸收），内部中继必须平衡
            if balance > tol:
                role = "sink"      # 净流入 = 吸收器
            elif balance < -tol:
                role = "source"    # 净流出 = 注入器
            else:
                role = "relay"
            if n in internal_set and abs(balance) > tol:
                violations.append({"node": n, "balance": balance,
                                   "expected": 0.0})
            nodes_report[n] = {
                "inflow": round(inflow[n], 6),
                "outflow": round(outflow[n], 6),
                "balance": balance,
                "role": role,
                "internal": n in internal_set,
            }
        ok = not violations
        return {"ok": ok, "violations": violations, "nodes": nodes_report,
                "tol": tol, "strict_mode": "all" if internal_nodes is None
                else "named"}

    # -------------------------------------------------- KVL
    def kvl_check(self, flows: Dict[Tuple[int, int], float],
                  cycles: Optional[List[List[int]]] = None) -> dict:
        """回路一致性（log 域）。

        对每个环 n0→n1→…→nk=n0，检查 sum(log(w)) ≈ 0，
        即环上权重乘积 ≈ 1（相似度传递闭环）。
        cycles 缺省时用 AdaptiveGraph.detect_cycles()（若挂了图）。
        """
        if cycles is None:
            if self.graph is None:
                return {"ok": True, "loops": [], "note": "无图无可检回路"}
            cycles = self.graph.detect_cycles()
        loops = []
        ok_all = True
        tol = 0.25  # log 域容差 ≈ 乘积因子 e^0.25≈1.28
        for cyc in cycles:
            if len(cyc) < 2:
                continue
            s = 0.0
            missing = []
            for i in range(len(cyc)):
                u, v = cyc[i], cyc[(i + 1) % len(cyc)]
                w = flows.get((u, v))
                if w is None or w <= 0:
                    missing.append((u, v))
                    continue
                s += math.log(w)
            if missing:
                loops.append({"cycle": cyc, "log_sum": None,
                              "missing_edges": missing, "ok": False})
                ok_all = False
            else:
                good = abs(s) <= tol
                loops.append({"cycle": cyc, "log_sum": round(s, 6),
                              "missing_edges": [], "ok": good})
                if not good:
                    ok_all = False
        return {"ok": ok_all, "loops": loops, "tol": tol}

    def fingerprint(self) -> str:
        return _sha256("kirchhoff-flow:" + SEAL)


# ================================================================ 二、RLC 谐振


@dataclass
class ResonatorNode:
    """RLC 谐振器 → 节点共振匹配。

    每个节点是一台确定性派生的谐振器：
      · 固有频率 f0 = sha256(node_key) 派生 ∈ (0, 1]
      · 相位 φ   = atan2(v[0], v[1])，v = hypervector 状态向量
      · 品质因数 Q = 1/(2·damping)，damping 由节点度数派生（高连接=重阻尼=宽带）

    共振得分 = 高斯频率贴近度 × 相位对齐 cos(Δφ) × Q 选择性。
    比余弦相似多出相位维度：同频反相 = 抵消（共振失败），
    这是纯余弦匹配检测不到的失配模式。
    """

    key: str
    frequency: float = 0.0
    phase: float = 0.0
    q_factor: float = 1.0

    def __post_init__(self) -> None:
        if self.frequency <= 0.0:
            h = int(hashlib.sha256(
                ("resonator:" + self.key).encode("utf-8")).hexdigest()[:8], 16)
            self.frequency = ((h % 1000) + 1) / 1000.0  # (0,1]
        if self.q_factor <= 0.0:
            self.q_factor = 1.0

    def match(self, drive_freq: float, drive_phase: float,
              bandwidth: float = 0.05) -> dict:
        """驱动信号 vs 本振共振匹配。"""
        df = abs(drive_freq - self.frequency)
        freq_score = math.exp(-(df ** 2) / (2 * bandwidth ** 2))
        phase_align = math.cos(drive_phase - self.phase)
        # 选择性：高 Q 窄带 —— 对准确匹配放大，对偏频惩罚
        selectivity = min(self.q_factor / 4.0, 1.0) if df < bandwidth else 0.25
        resonance = freq_score * max(phase_align, 0.0) * (0.5 + 0.5 * selectivity)
        return {
            "node": self.key,
            "freq_match": round(freq_score, 6),
            "phase_align": round(phase_align, 6),
            "selectivity": round(selectivity, 6),
            "resonance": round(resonance, 6),
            "resonant": resonance >= 0.5,
        }

    @staticmethod
    def from_state(key: str, state: Sequence[float],
                   degree: int = 3) -> "ResonatorNode":
        """由节点状态向量（AdaptiveGraph.set_state 的快照）派生谐振器。"""
        h = int(hashlib.sha256(
            ("resonator:" + key).encode("utf-8")).hexdigest()[:8], 16)
        freq = ((h % 1000) + 1) / 1000.0
        if len(state) >= 2 and (state[0] or state[1]):
            phase = math.atan2(state[0], state[1])
        else:
            phase = 0.0
        damping = 0.5 + min(degree, 8) / 8.0  # 度数越高阻尼越重
        q = 1.0 / (2.0 * damping)
        return ResonatorNode(key=key, frequency=freq, phase=phase,
                             q_factor=q)


def resonate(graph: Optional[AdaptiveGraph], query_key: str,
             node_keys: Sequence[str], bandwidth: float = 0.05) -> dict:
    """把查询信号向一组节点广播，返回共振榜。

    查询信号也派生为谐振器（同款确定性规则），逐一匹配。
    """
    driver = ResonatorNode(key=query_key)
    results = []
    for nk in node_keys:
        state: List[float] = []
        if graph is not None:
            nid = graph.node_of(nk)
            if nid is not None:
                gn = graph.nodes[nid] if hasattr(graph, "nodes") else None
                state = list(getattr(gn, "state", []) or [])
        r = ResonatorNode.from_state(nk, state) if state \
            else ResonatorNode(key=nk)
        m = driver.match(r.frequency, r.phase, bandwidth)
        m["node_f0"] = round(r.frequency, 4)
        m["node_phase"] = round(r.phase, 4)
        results.append(m)
    results.sort(key=lambda d: -d["resonance"])
    return {"driver": query_key, "bandwidth": bandwidth,
            "results": results, "seal": SEAL}


# ================================================================ 三、负反馈


@dataclass
class FeedbackAmp:
    """负反馈误差校正 → 监督学习误差回路物理直觉框架。

    闭环更新：a_{t+1} = a_t + G·(d - β·a_t) —— G=前向增益(学习率),
    β=反馈系数。误差 e = d - a。
    稳定条件（离散）：|1 - G·β| < 1 ⇒ 0 < G·β < 2。

    认知映射：
      · G·β 过小 → 欠收敛（学得慢）
      · G·β ∈ (0,2) → 收敛，最优 G·β≈1（一拍到位）
      · G·β > 2 → 发散震荡（学习率过大 = 过拟合不稳定的物理同构）
    稳定裕度 margin = 1 - |1 - G·β|。
    """

    gain: float = 1.0        # G：前向增益（学习率同构）
    feedback: float = 1.0     # β：反馈系数
    clip: float = 10.0

    def loop_gain(self) -> float:
        return self.gain * self.feedback

    def stability(self) -> dict:
        t = self.loop_gain()
        stable = 0.0 < t < 2.0
        margin = 1.0 - abs(1.0 - t) if stable else 0.0
        verdict = "underfit" if t < 0.5 else (
            "optimal" if 0.5 <= t <= 1.5 else (
                "stable" if stable else "divergent"))
        return {"loop_gain": round(t, 6), "stable": stable,
                "margin": round(margin, 6), "verdict": verdict}

    def step(self, actual: Sequence[float], target: Sequence[float]) -> dict:
        """一拍负反馈更新（逐维）。返回新状态与误差统计。"""
        if len(actual) != len(target):
            raise ValueError("actual/target 维度不一致: "
                             f"{len(actual)} vs {len(target)}")
        e = [t - a for t, a in zip(target, actual)]
        corr = [self.gain * x for x in e]
        new = []
        for a, c in zip(actual, corr):
            v = a + c
            v = max(-self.clip, min(self.clip, v))
            new.append(v)
        err_before = math.sqrt(sum(x * x for x in e))
        e2 = [t - a for t, a in zip(target, new)]
        err_after = math.sqrt(sum(x * x for x in e2))
        return {"new_state": new,
                "error_before": round(err_before, 6),
                "error_after": round(err_after, 6),
                "reduced": err_after <= err_before + 1e-12}

    def converge(self, initial: Sequence[float], target: Sequence[float],
                 rounds: int = 20, tol: float = 1e-6) -> dict:
        """闭环训练回路：逐拍反馈直至收敛/发散，报告震荡史。"""
        state = list(initial)
        history = []
        prev_err = None
        oscillation_flips = 0
        converged_at = None
        for i in range(rounds):
            r = self.step(state, target)
            state = r["new_state"]
            err = r["error_after"]
            history.append(err)
            if prev_err is not None and (
                    (prev_err - tol) > 0 > err or (prev_err + tol) < 0 < err):
                pass  # 误差恒非负，震荡检测交给环比
            if prev_err is not None and err > prev_err * 1.5 + 1e-12:
                oscillation_flips += 1
            prev_err = err
            if err <= tol:
                converged_at = i + 1
                break
        final_err = history[-1] if history else 0.0
        return {"final_state": state, "rounds_run": len(history),
                "converged": converged_at is not None,
                "converged_at": converged_at,
                "final_error": round(final_err, 8),
                "oscillation_flags": oscillation_flips,
                "stability": self.stability(),
                "history_head": [round(h, 6) for h in history[:5]]}

    def fingerprint(self) -> str:
        return _sha256("feedback-amp:" + SEAL)


# ================================================================ 四、忆阻赫布


@dataclass
class MemristorSynapse:
    """忆阻器 → 带遗忘曲线的赫布权重。

    忆阻公理：dM/dt = k·I(t) —— 阻态随历史电流累积变化并保持。
    赫布同构：Δw = η·x·y —— 突触权重随共激活更新。
    补强（相对 AdaptiveGraph.hebbian_step 的组级两两增强）：
      · 漏电衰减 leak（每拍 λ·w，遗忘曲线）
      · 阻态保持 retain（下限 w_min，长期记忆底座）
      · 每突触独立 update，而非仅组内两两
    """

    weight: float = 0.0
    eta: float = 0.1          # 可塑性速率 k 同构
    leak: float = 0.01        # 漏电衰减系数 λ
    w_min: float = 0.0        # 阻态保持下限
    w_max: float = 1.0        # 饱和上限（器件量程）

    def update(self, pre: float, post: float) -> float:
        """一拍忆阻-赫布更新：w += η·pre·post，再漏电，再夹持。"""
        plastic = self.eta * pre * post
        self.weight = self.weight + plastic
        self.weight -= self.leak * self.weight
        self.weight = max(self.w_min, min(self.w_max, self.weight))
        return self.weight

    def decay_only(self) -> float:
        """静息拍：只漏电不更新（睡眠遗忘）。"""
        self.weight -= self.leak * self.weight
        self.weight = max(self.w_min, min(self.w_max, self.weight))
        return self.weight

    @staticmethod
    def train_pair(seq_pre: Sequence[float], seq_post: Sequence[float],
                   **kw) -> "MemristorSynapse":
        """整段序列训练一个忆阻突触（监督信号→阻态史）。"""
        if len(seq_pre) != len(seq_post):
            raise ValueError("前后序列长度不一致")
        m = MemristorSynapse(**kw)
        for p, q in zip(seq_pre, seq_post):
            m.update(p, q)
        return m

    def snapshot(self) -> dict:
        return {"weight": round(self.weight, 6), "eta": self.eta,
                "leak": self.leak, "w_min": self.w_min, "w_max": self.w_max}


def memristive_hebb(graph: AdaptiveGraph, active_nodes: List[int],
                    eta: float = 0.1, leak: float = 0.01) -> dict:
    """对 AdaptiveGraph 的共激活组做忆阻式组级更新（含漏电）。

    与 AdaptiveGraph.hebbian_step 的差异（扬弃点）：
      · 原版：Δw = η 两两增强 + 全局衰减 + 裁剪 —— 无每突触阻态保持
      · 本版：组内两两忆阻更新 + 静息漏电 + 保持下限，
        输出与原版同形状的回执，便于对照审计。
    """
    n = graph.n
    weights_before = [
        [round(graph.weights[i][j], 4) for j in range(n)] for i in range(n)]
    result = graph.hebbian_step(active_nodes)
    # 静息漏电：在原版结果之上追加遗忘曲线（对称矩阵逐边）
    leaked = 0
    for i in range(n):
        for j in range(i + 1, n):
            w = graph.weights[i][j]
            if w > 0:
                nw = w - leak * w
                if nw < 0:
                    nw = 0.0
                graph.weights[i][j] = nw
                graph.weights[j][i] = nw
                leaked += 1
    return {"hebbian_receipt": result, "leaked_edges": leaked,
            "leak": leak, "n": n,
            "weights_before_sample": weights_before[0][:8],
            "seal": SEAL}


# ================================================================ 五、阻抗匹配


class ImpedanceMatch:
    """阻抗匹配 → 接口转换效率。

    反射系数 Γ = (Z_L - Z_S)/(Z_L + Z_S)；匹配度 = 1 - |Γ|。
    认知映射：发送侧向量与接收侧向量逐维算 Γ，
    失配维度产生"反射"（信息损耗），匹配度即接口转换效率。
    用途：模块接口/前后端信封/模型协议形状的失配审计。
    """

    def __init__(self, clip: float = 1e-9):
        self.clip = clip

    def reflection(self, source: Sequence[float],
                   load: Sequence[float]) -> List[float]:
        if len(source) != len(load):
            raise ValueError("阻抗维度不一致: "
                             f"{len(source)} vs {len(load)}")
        gammas = []
        for z_s, z_l in zip(source, load):
            diff = z_l - z_s
            denom = z_s + z_l
            if abs(denom) < self.clip:
                if abs(diff) < self.clip:
                    gammas.append(0.0)  # 双零维：无反射定义，记完美匹配
                else:
                    # 零和分母（纯反相）：全反射（Γ 饱和到 ±1）
                    gammas.append(math.copysign(1.0, diff))
            else:
                gammas.append(diff / denom)
        return gammas

    def match_score(self, source: Sequence[float],
                    load: Sequence[float]) -> dict:
        gammas = self.reflection(source, load)
        reflect = sum(abs(g) for g in gammas) / max(len(gammas), 1)
        efficiency = 1.0 - reflect
        worst_dim = -1
        worst_g = -1.0
        for i, g in enumerate(gammas):
            if abs(g) > worst_g:
                worst_g = abs(g)
                worst_dim = i
        return {
            "reflection_mean": round(reflect, 6),
            "efficiency": round(max(efficiency, 0.0), 6),
            "worst_dim": worst_dim,
            "worst_reflection": round(worst_g, 6),
            "matched": efficiency >= 0.9,
        }

    def fingerprint(self) -> str:
        return _sha256("impedance-match:" + SEAL)


# ================================================================ 六、张量电路


# 电路概念表（张量向量转换的概念字典 —— 领域词汇表）
CIRCUIT_CONCEPTS: Tuple[str, ...] = (
    "voltage",      # 电压（势差）    —— 驱动
    "current",      # 电流（流量）    —— 消息强度
    "resistance",   # 电阻（耗散）    —— 损耗/成本
    "inductance",   # 电感（磁储能）  —— 惯性/迟滞
    "capacitance",  # 电容（场储能）  —— 缓冲/积累
    "ground",       # 地（零参考）    —— 基线/锚点
    "source",       # 源（激励）      —— 输入/任务
    "loop",         # 回路（闭环）    —— 反馈环
    "node",         # 节点（汇接）    —— Agent 席位
    "switch",       # 开关（通断）    —— 门控/路由
)


class TensorCircuit:
    """张量向量转换：电路描述 → hypervector。

    编码规则（HRR，klein_projection.TensorCoupler 的 D/X 先例）：
      · 概念轴 D = make("concept:" + name)
      · 值轴   X = make("value:" + str(value)) 再 permute 编码顺序
      · 单件   = bind(D, X)（角色-填充绑定，encode_pair 同构）
      · 整电路 = bundle(单件们)（叠加，集合语义）
    由此电路之间可 cosine 相似检索，且 bind/unbind 可逆拆解成分。
    """

    def __init__(self, space: Optional[HypervectorSpace] = None,
                 concepts: Sequence[str] = CIRCUIT_CONCEPTS):
        self.space = space or HypervectorSpace()
        self.concepts = tuple(concepts)

    def concept_axis(self, name: str) -> List[float]:
        """D 轴：概念向量。"""
        if name not in self.concepts:
            raise ValueError(f"未知电路概念: {name}（表内: {self.concepts}）")
        return self.space.make("concept:" + name)

    def value_axis(self, value: float) -> List[float]:
        """X 轴：值向量（量化到 3 位小数保证确定性）。"""
        return self.space.make("value:" + f"{round(float(value), 3):.3f}")

    def encode_component(self, name: str, value: float,
                         order: int = 0) -> List[float]:
        """单元件张量：bind(D, permute(X, order)) —— order 编码位次。"""
        d = self.concept_axis(name)
        x = self.space.permute(self.value_axis(value), shift=order + 1)
        return self.space.bind(d, x)

    def encode_circuit(self, description: Dict[str, float]) -> List[float]:
        """整电路张量：按概念表顺序 bundle。"""
        parts = []
        for i, name in enumerate(self.concepts):
            if name in description:
                parts.append(self.encode_component(name, description[name], i))
        if not parts:
            raise ValueError("空电路描述（无可编码概念）")
        return self.space.bundle(parts)

    def decode_component(self, circuit_vec: List[float], name: str) -> List[float]:
        """可逆拆解：unbind(circuit, D) 取回该概念值轴的近似向量。

        返回的是 permute(X) 的近似，由 retrieve_value 与候选值逐一
        cosine 检索完成解码。
        """
        return self.space.unbind(circuit_vec, self.concept_axis(name))

    def retrieve_value(self, circuit_vec: List[float], name: str,
                       candidates: Sequence[float],
                       order: int = 0) -> List[Tuple[float, float]]:
        """在候选值表中检索该概念的取值（余弦打分）。"""
        approx = self.space.unbind(circuit_vec, self.concept_axis(name))
        scored = []
        for c in candidates:
            x = self.space.permute(self.value_axis(c), shift=order + 1)
            scored.append((c, self.space.cosine(approx, x)))
        scored.sort(key=lambda t: -t[1])
        return scored

    def similarity(self, a: Dict[str, float], b: Dict[str, float]) -> float:
        """两电路描述的张量相似度。"""
        va = self.encode_circuit(a)
        vb = self.encode_circuit(b)
        return self.space.cosine(va, vb)

    def transform(self, circuit_vec: List[float],
                  target_concept: str) -> List[float]:
        """张量变换：把电路张量投到目标概念轴（域转换算子）。

        bind(原张量, D_target) —— 与目标概念绑定的投影（klein D/X 同构）。
        """
        return self.space.bind(circuit_vec, self.concept_axis(target_concept))

    def fingerprint(self) -> str:
        return _sha256("tensor-circuit:" + SEAL)


# ================================================================ 总闸


class CircuitGate:
    """ring17 电子域总闸：六件套自检 + 清单回执。

    职责：装配审计（各件 self-check）→ 产出 manifest（artifacts 真实入卡，
    V49 确立的纪律）→ 诚实边界声明。不执行任何网络/连接操作。
    """

    REQUIRED = ("kirchhoff", "resonator", "feedback",
                "memristor", "impedance", "tensor")

    def __init__(self, space: Optional[HypervectorSpace] = None,
                 graph: Optional[AdaptiveGraph] = None):
        self.space = space or HypervectorSpace()
        self.graph = graph
        self.tensor = TensorCircuit(space=self.space)

    def self_check(self) -> dict:
        checks: Dict[str, dict] = {}
        # 1) KirchhoffFlow：守恒流（KVL 环乘积=1：2×0.5×1）
        flows = {(0, 1): 3.0, (1, 2): 3.0, (2, 0): 3.0}
        kf = KirchhoffFlow()
        kcl = kf.kcl_check(flows)
        loop_flows = {(0, 1): 2.0, (1, 2): 0.5, (2, 0): 1.0}
        kvl = kf.kvl_check(loop_flows, cycles=[[0, 1, 2]])
        checks["kirchhoff"] = {
            "ok": kcl["ok"] and kvl["ok"],
            "kcl_relay_balanced": all(
                n["role"] == "relay" for n in kcl["nodes"].values()),
            "kvl_log_sum_zero": abs(
                kvl["loops"][0]["log_sum"]) < 1e-9 if kvl["loops"] else False,
        }
        # 2) ResonatorNode：同频同相共振 > 异频
        r = ResonatorNode(key="selfcheck")
        m_hit = r.match(r.frequency, r.phase)
        m_miss = r.match((r.frequency + 0.5) % 1.0, r.phase + math.pi)
        checks["resonator"] = {
            "ok": m_hit["resonance"] > m_miss["resonance"],
            "hit": m_hit["resonance"], "miss": round(m_miss["resonance"], 6),
            "phase_dimension": m_hit["phase_align"] > 0 > m_miss["phase_align"],
        }
        # 3) FeedbackAmp：G·β=1 一拍收敛；G·β=2.5 发散
        fa_ok = FeedbackAmp(gain=1.0, feedback=1.0).converge(
            [0.0, 0.0], [1.0, 1.0], rounds=3)
        fa_bad = FeedbackAmp(gain=2.5, feedback=1.0).stability()
        fa_good = FeedbackAmp(gain=1.0, feedback=1.0).stability()
        checks["feedback"] = {
            "ok": fa_ok["converged"] and fa_bad["verdict"] == "divergent"
                  and fa_good["verdict"] in ("optimal", "stable"),
            "one_shot": fa_ok["converged_at"] == 1,
            "divergent_loop_gain": fa_bad["loop_gain"],
        }
        # 4) MemristorSynapse：共激活增权 + 静息漏电 + 保持下限
        m = MemristorSynapse(weight=0.5, eta=0.2, leak=0.1, w_min=0.05)
        w1 = m.update(1.0, 1.0)
        w_hold = None
        for _ in range(50):
            w_hold = m.decay_only()
        checks["memristor"] = {
            "ok": w1 > 0.5 and w_hold is not None and w_hold >= m.w_min - 1e-9,
            "after_pot": round(w1, 6), "after_rest": round(w_hold, 6),
            "retention_floor": m.w_min,
        }
        # 5) ImpedanceMatch：同向量效率=1；反向量效率≈0
        im = ImpedanceMatch()
        same = im.match_score([0.5, 0.5], [0.5, 0.5])
        anti = im.match_score([0.5, 0.5], [-0.5, -0.5])
        checks["impedance"] = {
            "ok": same["efficiency"] > 0.99 and anti["efficiency"] < 0.05,
            "same": same["efficiency"], "anti": anti["efficiency"],
        }
        # 6) TensorCircuit：编码-检索闭环 + 相似度排序
        desc = {"voltage": 5.0, "current": 2.0}
        vec = self.tensor.encode_circuit(desc)
        got = self.tensor.retrieve_value(
            vec, "voltage", [1.0, 2.0, 5.0, 9.0])
        s_close = self.tensor.similarity(desc, desc)
        s_far = self.tensor.similarity(desc, {"ground": 1.0})
        checks["tensor"] = {
            "ok": got and got[0][0] == 5.0 and s_close > s_far,
            "retrieved_top": got[0] if got else None,
            "self_sim": s_close, "far_sim": s_far,
        }
        ok_all = all(c["ok"] for c in checks.values())
        return {"ok": ok_all, "checks": checks,
                "chain_position": CHAIN_POSITION, "seal": SEAL}

    def run(self, demo: bool = False) -> dict:
        """总闸：自检 → manifest 回执。"""
        sc = self.self_check()
        manifest = {
            "batch": CHAIN_POSITION["batch"],
            "ring": CHAIN_POSITION["ring"],
            "domain": CHAIN_POSITION["domain"],
            "generated_at": _now_iso(),
            "self_check": sc,
            "components": {
                "KirchhoffFlow": "KCL/KVL → 消息守恒/回路一致性",
                "ResonatorNode": "RLC 谐振(频率+相位+Q) → 节点共振",
                "FeedbackAmp": "负反馈(环路增益/裕度) → 监督误差回路",
                "MemristorSynapse": "忆阻 dM/dt=kI → 漏电赫布权重",
                "ImpedanceMatch": "反射系数 Γ → 接口转换效率",
                "TensorCircuit": "电路概念表 → hypervector(D/X 轴)",
            },
            "artifacts": {},
            "honesty": {
                "source": "电路学标准学科公理（视频标题锁定域），"
                          "非视频逐字稿（无 CC 字幕，2026-11-09 核实）",
                "physics": "物理隐喻→认知算子的工程类比，非物理仿真",
                "neural": False,
                "network": False,
                "new_dependencies": 0,
                "reuses": ["hypervector.HypervectorSpace",
                           "graph.AdaptiveGraph(hebbian_step)"],
            },
            "seal": SEAL,
        }
        if sc["ok"]:
            manifest["artifacts"]["self_check_receipt"] = {
                "checks": {k: c["ok"] for k, c in sc["checks"].items()}}
        return manifest


# ---------------------------------------------------------------- 模块指纹


def fingerprint() -> dict:
    return {
        "module": "circuit_gate",
        "ring": CHAIN_POSITION["ring"],
        "domain": CHAIN_POSITION["domain"],
        "components": list(CircuitGate.REQUIRED),
        "concepts": list(CIRCUIT_CONCEPTS),
        "sha256": _sha256("circuit-gate-v1:" + SEAL),
        "seal": SEAL,
    }


def probe() -> dict:
    """轻量探针：不建图、全确定性。"""
    gate = CircuitGate()
    return gate.self_check()


def _main(argv: List[str]) -> int:
    import json
    import sys
    cmd = argv[1] if len(argv) > 1 else "probe"
    if cmd == "probe":
        out = probe()
    elif cmd == "run":
        out = CircuitGate().run()
    elif cmd == "fingerprint":
        out = fingerprint()
    else:
        print("usage: python -m holoaeon.circuit_gate "
              "[probe|run|fingerprint]", file=sys.stderr)
        return 2
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if out.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(_main(["circuit_gate"] + sys.argv[1:]))
