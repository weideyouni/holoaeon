# -*- coding: utf-8 -*-
"""test_v51_circuit_gate —— ring17 电子域算子蒸馏测试（真 unittest）。

覆盖六件套 + 总闸 + 诚实边界 + 封口密语。全部确定性、无网络。
"""
from __future__ import annotations

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holoaeon.circuit_gate import (  # noqa: E402
    CIRCUIT_CONCEPTS,
    CHAIN_POSITION,
    SEAL,
    CircuitGate,
    FeedbackAmp,
    ImpedanceMatch,
    KirchhoffFlow,
    MemristorSynapse,
    ResonatorNode,
    TensorCircuit,
    fingerprint,
    memristive_hebb,
    probe,
)
from holoaeon.graph import AdaptiveGraph  # noqa: E402
from holoaeon.hypervector import HypervectorSpace  # noqa: E402


# ---------------------------------------------------------------- 一、KCL/KVL
class TestKirchhoffFlow(unittest.TestCase):
    def test_kcl_balanced_relay_passes(self):
        flows = {(0, 1): 3.0, (1, 2): 3.0, (2, 0): 3.0}
        r = KirchhoffFlow().kcl_check(flows)
        self.assertTrue(r["ok"])
        self.assertEqual(r["violations"], [])
        self.assertTrue(all(n["role"] == "relay"
                            for n in r["nodes"].values()))

    def test_kcl_source_sink_marked_not_violation(self):
        # 全外部模式（internal_nodes=[]）：0 注入 5、1 吸收 5 —— 合法端口
        flows = {(0, 1): 5.0}
        r = KirchhoffFlow().kcl_check(flows, internal_nodes=[])
        self.assertTrue(r["ok"])
        self.assertEqual(r["nodes"][0]["role"], "source")
        self.assertEqual(r["nodes"][1]["role"], "sink")

    def test_kcl_mixed_mode_internal_only(self):
        # 混合模式：0 是外部源（合法），1 是内部中继必须平衡，2 外部吸收
        flows = {(0, 1): 5.0, (1, 2): 5.0}
        r = KirchhoffFlow().kcl_check(flows, internal_nodes=[1])
        self.assertTrue(r["ok"])
        self.assertEqual(r["nodes"][0]["role"], "source")
        self.assertEqual(r["nodes"][1]["role"], "relay")
        self.assertEqual(r["nodes"][2]["role"], "sink")
        # 反例：把吸收器 2 也声明为内部 → 2 失衡成违例
        r2 = KirchhoffFlow().kcl_check(flows, internal_nodes=[1, 2])
        self.assertFalse(r2["ok"])
        self.assertTrue(any(v["node"] == 2 for v in r2["violations"]))

    def test_kcl_relay_imbalance_is_violation(self):
        # 全严格（默认）：节点 1 吃掉 2 —— 违例
        flows = {(0, 1): 5.0, (1, 2): 3.0}
        r = KirchhoffFlow().kcl_check(flows)
        self.assertFalse(r["ok"])
        self.assertTrue(any(v["node"] == 1 for v in r["violations"]))

    def test_kvl_product_consistency(self):
        flows = {(0, 1): 2.0, (1, 2): 0.5, (2, 0): 1.0}
        r = KirchhoffFlow().kvl_check(flows, cycles=[[0, 1, 2]])
        self.assertTrue(r["ok"])
        self.assertAlmostEqual(r["loops"][0]["log_sum"], 0.0, places=9)

    def test_kvl_transitivity_break_detected(self):
        # 乘积 = 4：log_sum ≈ 1.386 > tol，传递性破缺被检出
        flows = {(0, 1): 4.0, (1, 2): 1.0, (2, 0): 1.0}
        r = KirchhoffFlow().kvl_check(flows, cycles=[[0, 1, 2]])
        self.assertFalse(r["ok"])

    def test_kvl_missing_edge_reported(self):
        flows = {(0, 1): 1.0}
        r = KirchhoffFlow().kvl_check(flows, cycles=[[0, 1, 2]])
        self.assertFalse(r["ok"])
        self.assertTrue(r["loops"][0]["missing_edges"])


# ---------------------------------------------------------------- 二、谐振
class TestResonatorNode(unittest.TestCase):
    def test_deterministic_derivation(self):
        a = ResonatorNode(key="node-A")
        b = ResonatorNode(key="node-A")
        self.assertEqual(a.frequency, b.frequency)
        self.assertEqual(a.phase, b.phase)
        self.assertGreater(a.frequency, 0.0)
        self.assertLessEqual(a.frequency, 1.0)

    def test_resonance_hit_beats_miss(self):
        r = ResonatorNode(key="hit-check")
        hit = r.match(r.frequency, r.phase)
        miss = r.match((r.frequency + 0.5) % 1.0, r.phase + math.pi)
        self.assertGreater(hit["resonance"], miss["resonance"])
        self.assertTrue(hit["resonant"])
        self.assertFalse(miss["resonant"])

    def test_phase_dimension_detects_antiphase(self):
        # 同频反相：频率满分但相位对齐为 -1 —— 纯余弦匹配盲区
        r = ResonatorNode(key="phase-check")
        anti = r.match(r.frequency, r.phase + math.pi)
        self.assertLess(anti["phase_align"], 0.0)
        self.assertLess(anti["resonance"], 0.05)

    def test_from_state_derives_phase(self):
        st = [1.0, 1.0]  # atan2(1,1)=π/4
        r = ResonatorNode.from_state("st-node", st, degree=3)
        self.assertAlmostEqual(r.phase, math.pi / 4, places=6)
        self.assertGreater(r.q_factor, 0.0)
        self.assertLess(r.q_factor, 1.0)  # damping>0.5 ⇒ Q<1

    def test_higher_degree_lower_q(self):
        lo = ResonatorNode.from_state("q", [1.0, 0.0], degree=1)
        hi = ResonatorNode.from_state("q", [1.0, 0.0], degree=8)
        self.assertGreater(lo.q_factor, hi.q_factor)


# ---------------------------------------------------------------- 三、负反馈
class TestFeedbackAmp(unittest.TestCase):
    def test_one_shot_convergence_at_optimal_gain(self):
        fa = FeedbackAmp(gain=1.0, feedback=1.0)
        r = fa.converge([0.0, 0.0], [1.0, 1.0], rounds=3)
        self.assertTrue(r["converged"])
        self.assertEqual(r["converged_at"], 1)
        self.assertAlmostEqual(r["final_error"], 0.0, places=9)

    def test_divergent_loop_gain_detected(self):
        fa = FeedbackAmp(gain=2.5, feedback=1.0)
        s = fa.stability()
        self.assertFalse(s["stable"])
        self.assertEqual(s["verdict"], "divergent")
        r = fa.converge([0.0], [1.0], rounds=10)
        self.assertFalse(r["converged"])

    def test_underfit_slow_convergence(self):
        fa = FeedbackAmp(gain=0.1, feedback=1.0)
        s = fa.stability()
        self.assertEqual(s["verdict"], "underfit")
        r = fa.converge([0.0], [1.0], rounds=20, tol=1e-6)
        self.assertFalse(r["converged"])  # 20 拍内到不了 1e-6

    def test_step_reduces_error_and_clips(self):
        fa = FeedbackAmp(gain=1.0, feedback=1.0, clip=10.0)
        r = fa.step([0.0, 0.0], [5.0, 5.0])
        self.assertTrue(r["reduced"])
        self.assertEqual(r["new_state"], [5.0, 5.0])
        # 过冲夹持：增益 2.5 单拍 5→7.5，clip 上限保护量程
        fa2 = FeedbackAmp(gain=2.5, feedback=1.0, clip=6.0)
        r2 = fa2.step([5.0], [5.0])
        self.assertLessEqual(r2["new_state"][0], 6.0)

    def test_dimension_mismatch_raises(self):
        fa = FeedbackAmp()
        with self.assertRaises(ValueError):
            fa.step([0.0], [1.0, 2.0])


# ---------------------------------------------------------------- 四、忆阻赫布
class TestMemristorSynapse(unittest.TestCase):
    def test_hebbian_plasticity(self):
        m = MemristorSynapse(weight=0.5, eta=0.2)
        w = m.update(1.0, 1.0)
        self.assertGreater(w, 0.5)  # Δw = η·x·y > 0

    def test_anti_correlation_depresses(self):
        m = MemristorSynapse(weight=0.5, eta=0.2)
        w = m.update(1.0, -1.0)
        self.assertLess(w, 0.5)  # 负相关 = 抑制

    def test_leak_forgetting_curve(self):
        m = MemristorSynapse(weight=0.9, leak=0.1, w_min=0.0)
        w = m.decay_only()
        self.assertAlmostEqual(w, 0.81, places=6)

    def test_retention_floor(self):
        m = MemristorSynapse(weight=0.5, leak=0.5, w_min=0.1)
        for _ in range(40):
            w = m.decay_only()
        self.assertGreaterEqual(w, m.w_min - 1e-9)

    def test_saturation_cap(self):
        m = MemristorSynapse(weight=0.99, eta=0.9, w_max=1.0)
        w = m.update(1.0, 1.0)
        self.assertLessEqual(w, 1.0)

    def test_train_pair_sequence(self):
        pre = [1.0, 1.0, 1.0, 1.0]
        post = [1.0, 1.0, 1.0, 1.0]
        m = MemristorSynapse.train_pair(pre, post, eta=0.2, leak=0.0)
        self.assertGreater(m.weight, 0.0)
        with self.assertRaises(ValueError):
            MemristorSynapse.train_pair([1.0], [1.0, 2.0])

    def test_memristive_hebb_on_adaptive_graph(self):
        g = AdaptiveGraph()
        active = [0, 1]
        r = memristive_hebb(g, active, leak=0.05)
        self.assertIn("hebbian_receipt", r)
        self.assertGreater(r["leaked_edges"], 0)
        self.assertEqual(r["n"], g.n)
        # 漏电后权重非负
        for i in range(g.n):
            for j in range(g.n):
                self.assertGreaterEqual(g.weights[i][j], 0.0)


# ---------------------------------------------------------------- 五、阻抗匹配
class TestImpedanceMatch(unittest.TestCase):
    def test_perfect_match(self):
        im = ImpedanceMatch()
        r = im.match_score([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
        self.assertGreater(r["efficiency"], 0.99)
        self.assertTrue(r["matched"])

    def test_anti_phase_full_reflection(self):
        im = ImpedanceMatch()
        r = im.match_score([0.5, 0.5], [-0.5, -0.5])
        self.assertLess(r["efficiency"], 0.05)
        self.assertFalse(r["matched"])

    def test_zero_zero_dimension_no_reflection(self):
        im = ImpedanceMatch()
        gammas = im.reflection([0.0, 1.0], [0.0, 1.0])
        self.assertEqual(gammas[0], 0.0)

    def test_dimension_mismatch_raises(self):
        im = ImpedanceMatch()
        with self.assertRaises(ValueError):
            im.match_score([1.0], [1.0, 2.0])

    def test_partial_mismatch_worst_dim_reported(self):
        im = ImpedanceMatch()
        src = [1.0, 1.0, 1.0]
        ld = [1.0, 1.0, -1.0]  # 第 2 维全反射
        r = im.match_score(src, ld)
        self.assertEqual(r["worst_dim"], 2)
        self.assertGreater(r["worst_reflection"], 0.99)
        self.assertGreater(r["reflection_mean"], 0.0)


# ---------------------------------------------------------------- 六、张量电路
class TestTensorCircuit(unittest.TestCase):
    def setUp(self):
        self.tc = TensorCircuit()

    def test_concept_table_complete(self):
        for c in ("voltage", "current", "resistance", "ground",
                  "source", "loop", "node", "switch"):
            self.assertIn(c, CIRCUIT_CONCEPTS)
        self.assertEqual(len(CIRCUIT_CONCEPTS), 10)

    def test_unknown_concept_rejected(self):
        with self.assertRaises(ValueError):
            self.tc.concept_axis("photon")

    def test_encode_deterministic(self):
        d = {"voltage": 5.0, "current": 2.0}
        self.assertEqual(self.tc.encode_circuit(d),
                         self.tc.encode_circuit(d))

    def test_encode_empty_raises(self):
        with self.assertRaises(ValueError):
            self.tc.encode_circuit({})

    def test_value_axis_quantization(self):
        self.assertEqual(self.tc.value_axis(5.0), self.tc.value_axis(5.0004))
        self.assertNotEqual(self.tc.value_axis(5.0),
                            self.tc.value_axis(5.1))

    def test_retrieve_roundtrip(self):
        d = {"voltage": 5.0, "current": 2.0}
        vec = self.tc.encode_circuit(d)
        got = self.tc.retrieve_value(vec, "voltage", [1.0, 2.0, 5.0, 9.0])
        self.assertEqual(got[0][0], 5.0)

    def test_similarity_ordering(self):
        a = {"voltage": 5.0, "current": 2.0}
        close = {"voltage": 5.0, "current": 2.0}
        far = {"ground": 1.0}
        self.assertGreater(self.tc.similarity(a, close),
                            self.tc.similarity(a, far))

    def test_transform_binds_target_axis(self):
        d = {"voltage": 5.0}
        vec = self.tc.encode_circuit(d)
        t = self.tc.transform(vec, "ground")
        # 投影与原向量不相关（绑定生成新独立向量）
        self.assertLess(self.tc.space.cosine(vec, t), 0.3)

    def test_decode_component_unbind_shape(self):
        d = {"voltage": 5.0}
        vec = self.tc.encode_circuit(d)
        approx = self.tc.decode_component(vec, "voltage")
        self.assertEqual(len(approx), self.tc.space.dim)


# ---------------------------------------------------------------- 总闸
class TestCircuitGate(unittest.TestCase):
    def test_probe_all_green(self):
        r = probe()
        self.assertTrue(r["ok"])
        for name, c in r["checks"].items():
            self.assertTrue(c["ok"], f"component failed: {name}")

    def test_run_manifest_honesty(self):
        m = CircuitGate().run()
        self.assertEqual(m["ring"], 17)
        self.assertEqual(m["batch"], "V51")
        h = m["honesty"]
        self.assertFalse(h["neural"])
        self.assertFalse(h["network"])
        self.assertEqual(h["new_dependencies"], 0)
        self.assertIn("非视频逐字稿", h["source"])
        self.assertIn("hypervector", h["reuses"][0])

    def test_run_artifacts_real_content(self):
        m = CircuitGate().run()
        self.assertIn("self_check_receipt", m["artifacts"])
        self.assertIn("checks", m["artifacts"]["self_check_receipt"])
        self.assertEqual(len(m["artifacts"]["self_check_receipt"]["checks"]), 6)

    def test_chain_position_upstream_names_real_modules(self):
        ups = " ".join(CHAIN_POSITION["upstream"])
        self.assertIn("klein_projection", ups)
        self.assertIn("graph", ups)
        self.assertIn("hypervector", ups)
        self.assertIn("forge_gate", ups)

    def test_seal_and_fingerprint(self):
        fp = fingerprint()
        self.assertEqual(fp["ring"], 17)
        self.assertEqual(fp["seal"], SEAL)
        self.assertEqual(len(fp["components"]), 6)
        self.assertEqual(fp["sha256"],
                         __import__("hashlib").sha256(
                             ("circuit-gate-v1:" + SEAL).encode("utf-8")
                         ).hexdigest())

    def test_gate_reuses_hypervector_space(self):
        gate = CircuitGate(space=HypervectorSpace())
        self.assertIsInstance(gate.space, HypervectorSpace)
        # TensorCircuit 与总闸共享同一空间（装配不重造）
        self.assertIs(gate.tensor.space, gate.space)


# ---------------------------------------------------------------- 复用对照
class TestReuseAnchors(unittest.TestCase):
    """V51 扬弃点：新算子必须真实复用既有资产，不重写。"""

    def test_adaptive_graph_hebbian_compatible(self):
        g = AdaptiveGraph()
        before = g.weights[0][1]
        g.hebbian_step([0, 1])
        # 原版先跑通（回归保护）
        self.assertIsInstance(g.weights, list)

    def test_hebbian_step_returns_receipt(self):
        g = AdaptiveGraph()
        r = g.hebbian_step([0, 1, 2])
        self.assertIsInstance(r, dict)

    def test_hypervector_space_bind_bundle_alive(self):
        sp = HypervectorSpace()
        a = sp.make("a")
        b = sp.make("b")
        c = sp.bind(a, b)
        d = sp.unbind(c, b)
        # HRR 逆是近似逆（|fft(b)|² 加权畸变）：取"显著优于无关向量"阈值
        self.assertGreater(sp.cosine(a, d), 0.5)
        self.assertGreater(sp.cosine(a, d), sp.cosine(a, sp.make("zzz")))


if __name__ == "__main__":
    unittest.main(verbosity=2)
