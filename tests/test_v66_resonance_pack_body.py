# -*- coding: utf-8 -*-
"""
V66 · 判据回写原包（7 把尺子搬进 topology_resonance_pack 本体）+ 标准 NIS + dify-workflow 清零
================================================================================
验收三件事：
  ① 原包 6 个软内核换成可失败的硬判据（mandala_fanout / kalman_state /
     bayesian_guard / hilbert_project / dissipation_measure / resonance_node）；
  ② resonance_supplement.kalman_fuse 的 NIS 从「融合 vs 观测」改为
     「预测 vs 观测」的标准口径，并带 χ²(1) 一致性门控；
  ③ gap_adapters 的 dify-workflow 由源码取证补齐（12 adapted / 0 gap）。
"""
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holoaeon import resonance_supplement as rs  # noqa: E402
from holoaeon.packs import topology_resonance_pack as P  # noqa: E402


class TestSingleSourceOfTruth(unittest.TestCase):
    """七把尺子的数学只许有一份：原包必须从 resonance_supplement 取。"""

    def test_pack_imports_from_supplement(self):
        self.assertIs(P.kalman_fuse, rs.kalman_fuse)
        self.assertIs(P.mandala_wht, rs.mandala_wht)
        self.assertIs(P.sprt_gate, rs.sprt_gate)
        self.assertIs(P.rff_features, rs.rff_features)
        self.assertIs(P.entropy_production, rs.entropy_production)
        self.assertIs(P.kuramoto_order, rs.kuramoto_order)

    def test_nis_threshold_is_chi2_1dof_95(self):
        self.assertEqual(P.NIS_CHI2_95, rs.CHI2_1DOF_95)
        self.assertAlmostEqual(P.NIS_CHI2_95, 3.841, places=3)

    def test_active_nodes_frozen_and_decomposed(self):
        # 冻结值不可动（test_v62_meridian_link 断言 108641）
        self.assertEqual(P.ACTIVE_NODES, 108641)
        self.assertEqual(P.ACTIVE_NODES, math.prod(P.ACTIVE_NODE_FACTORS))
        self.assertEqual(P.ACTIVE_NODE_FACTORS, (13, 61, 137))


class TestResonanceNodeOrderParameter(unittest.TestCase):
    """X2：原包不再只有"相似对计数"，补了真正的序参量 r。"""

    def setUp(self):
        self.r = P.resonance_node()

    def test_keeps_original_keys(self):
        for k in ("matrix", "active_nodes", "sparse_ratio", "current_nodes",
                  "resonance_pairs", "resonance_count", "resonance_threshold",
                  "emergence", "emergence_ratio"):
            self.assertIn(k, self.r)

    def test_order_parameter_in_unit_interval(self):
        self.assertGreaterEqual(self.r["order_parameter"], 0.0)
        self.assertLessEqual(self.r["order_parameter"], 1.0)

    def test_phase_coherence_is_judged_not_decorative(self):
        self.assertIn(self.r["phase_coherence"], ("synchronized", "incoherent"))
        expect = "synchronized" if self.r["order_parameter"] >= 0.75 else "incoherent"
        self.assertEqual(self.r["phase_coherence"], expect)

    def test_factorization_and_quotient(self):
        self.assertEqual(self.r["active_nodes_factorization"], [13, 61, 137])
        self.assertEqual(self.r["matrix_quotient"]["quotient"], 81)
        self.assertEqual(self.r["matrix_quotient"]["remainder"], 830)


class TestMandalaOrthogonal(unittest.TestCase):
    """R2：扇出从"骰子"换成 Hadamard 正交变换，判据必须能失败。"""

    def setUp(self):
        self.m = P.mandala_fanout(task="扩容", center="N00")

    def test_keeps_original_contract(self):
        for k in ("topology", "structure", "task", "fan_out", "fan_in", "aggregation"):
            self.assertIn(k, self.m)
        self.assertEqual(len(self.m["fan_out"]), 8)
        self.assertEqual(len(self.m["fan_in"]), 8)

    def test_transform_is_lossless_and_orthogonal(self):
        ot = self.m["orthogonal_transform"]
        self.assertEqual(ot["reconstruction_error"], 0.0)
        self.assertEqual(ot["orthogonality_max_dev"], 0.0)
        self.assertAlmostEqual(ot["parseval_ratio"], 1.0, places=12)
        self.assertTrue(ot["perfect"])

    def test_center_is_dc_and_equals_mean(self):
        ot = self.m["orthogonal_transform"]
        self.assertTrue(ot["center_equals_mean"])
        self.assertAlmostEqual(ot["center_dc"], 4.5, places=6)

    def test_default_spectrum_matches_v65_ruler(self):
        self.assertEqual(self.m["orthogonal_transform"]["spectrum"],
                         [4.5, -0.5, -1.0, 0.0, -2.0, 0.0, 0.0, 0.0])

    def test_uniform_loads_means_no_fanout(self):
        """八方位齐步 → 谱只剩直流项：没有分化就没有扇出。"""
        u = P.mandala_fanout(loads="3,3,3,3,3,3,3,3")
        self.assertEqual(u["orthogonal_transform"]["spectrum"],
                         [3.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        self.assertEqual(u["aggregation"]["effective_fanout"], 0)

    def test_bad_loads_fall_back_instead_of_raising(self):
        r = P.mandala_fanout(loads="1,2,3")
        self.assertEqual(len(r["loads"]), 8)
        self.assertTrue(r["orthogonal_transform"]["perfect"])


class TestKalmanStandardNis(unittest.TestCase):
    """R5：NIS 用预测值算，离群源只预测不吸收。"""

    def test_q0_matches_batch_exactly(self):
        got = rs.kalman_fuse([(10.0, 1.0), (10.5, 0.25), (9.8, 4.0)], process_noise=0.0)
        self.assertTrue(got["sequential_matches_batch"])
        self.assertAlmostEqual(got["fused_state"], got["batch_fused_state"], places=9)

    def test_nis_is_prediction_based(self):
        got = rs.kalman_fuse(process_noise=0.0)
        self.assertEqual(got["nis_mode"], "standard_predict_versus_observation")
        # 锚源（无预测）不参与一致性判定
        self.assertIsNone(got["sources"][0]["consistent"])
        for row in got["sources"][1:]:
            pred = row["predicted_state"]
            s = row["predicted_variance"] + row["R"]
            self.assertAlmostEqual(row["nis"], (row["z"] - pred) ** 2 / s, places=5)

    def test_clean_nis_values(self):
        got = rs.kalman_fuse(process_noise=0.0)
        self.assertAlmostEqual(got["sources"][1]["nis"], 0.2, places=6)
        self.assertAlmostEqual(got["sources"][2]["nis"], 0.085714, places=5)

    def test_outlier_rejected_and_fusion_not_dragged(self):
        got = rs.kalman_fuse([(10.0, 1.0), (10.5, 0.25), (9.8, 4.0), (30.0, 0.5)],
                             process_noise=0.0)
        self.assertFalse(got["all_consistent"])
        self.assertEqual(got["rejected"], [3])
        # 关键：融合值不被离群源拉偏，仍等于干净三源的融合
        self.assertAlmostEqual(got["fused_state"], 10.371429, places=6)

    def test_gate_off_reproduces_legacy_dragged_value(self):
        got = rs.kalman_fuse([(10.0, 1.0), (10.5, 0.25), (9.8, 4.0), (30.0, 0.5)],
                             process_noise=0.0, gate=False)
        self.assertAlmostEqual(got["fused_state"], 15.786207, places=5)

    def test_supplement_check_still_passes(self):
        self.assertEqual(rs.check()["verdict"], "PASS")


class TestKalmanStatePack(unittest.TestCase):
    def test_keeps_original_keys(self):
        k = P.kalman_state()
        for key in ("filter", "parameters", "steps", "checkpoint", "note"):
            self.assertIn(key, k)
        for key in ("final_state", "final_uncertainty", "convergence", "observations"):
            self.assertIn(key, k["checkpoint"])
        for key in ("step", "observation", "kalman_gain", "state_estimate", "uncertainty"):
            self.assertIn(key, k["steps"][0])

    def test_steps_carry_nis_and_prediction(self):
        k = P.kalman_state()
        for s in k["steps"]:
            for key in ("measurement_variance", "predicted_state", "innovation",
                        "nis", "consistent", "applied"):
                self.assertIn(key, s)

    def test_gate_threshold_exposed(self):
        gate = k_gate = P.kalman_state()["consistency_gate"]
        self.assertEqual(gate["chi2_1dof_95"], P.NIS_CHI2_95)

    def test_outlier_path_rejects_and_holds(self):
        k = P.kalman_state(observations="10.0,10.5,9.8,30.0",
                           observation_noise="1.0,0.25,4.0,0.5", process_noise=0.0)
        self.assertEqual(k["checkpoint"]["rejected_sources"], [3])
        self.assertFalse(k["checkpoint"]["all_consistent"])
        self.assertGreater(k["checkpoint"]["nis_max"], P.NIS_CHI2_95)
        self.assertAlmostEqual(k["checkpoint"]["final_state"], 10.371429, places=6)


class TestBayesianCostSensitive(unittest.TestCase):
    """R6：0.5 硬编码 → 代价敏感阈值 + SPRT 双门限。"""

    def test_threshold_is_cost_ratio_not_half(self):
        b = P.bayesian_guard(feature="network")
        self.assertAlmostEqual(b["threshold"], 1.0 / 11.0, places=6)
        self.assertIn("cost_fn", b["threshold_rule"])

    def test_dangerous_feature_blocks(self):
        b = P.bayesian_guard(feature="network")
        self.assertEqual(b["decision"], "BLOCK")
        self.assertEqual(b["decided_by"], "posterior_cost_threshold")
        self.assertEqual(b["retry_policy"]["max_retries"], 3)

    def test_safe_feature_allows(self):
        for f in ("read", "safe"):
            b = P.bayesian_guard(feature=f)
            self.assertEqual(b["decision"], "ALLOW")
            self.assertIsNone(b["retry_policy"])

    def test_posterior_matches_bayes_formula(self):
        b = P.bayesian_guard(feature="network")
        prior, ll = 0.15, b["likelihood"]
        p = ll["block"] * prior + ll["allow"] * (1 - prior)
        self.assertAlmostEqual(b["posterior"]["block"],
                               ll["block"] * prior / p, places=6)

    def test_evidence_uses_sprt_and_stops_early(self):
        b = P.bayesian_guard(feature="execute", evidence="1,1,0,1,1,0,1,0,1,1")
        self.assertEqual(b["decided_by"], "sprt")
        self.assertEqual(b["sprt"]["decision"], "H1")
        self.assertEqual(b["sprt"]["stopped_at"], 5)
        self.assertAlmostEqual(b["sprt"]["threshold_A"], 2.890372, places=6)
        self.assertAlmostEqual(b["sprt"]["threshold_B"], -2.251292, places=6)

    def test_history_sets_prior(self):
        a = P.bayesian_guard(feature="read", history="0.9,0.8,0.7,0.2")
        self.assertAlmostEqual(a["prior"]["block"], 0.75, places=4)


class TestHilbertRff(unittest.TestCase):
    """R7：假投影 → 随机傅里叶特征，范数不再随维数膨胀。"""

    def test_keeps_projected_dim_key(self):
        # emergence_chain 只消费 hilbert["projected_dim"]
        h = P.hilbert_project()
        self.assertEqual(h["projected_dim"], 40)
        self.assertEqual(h["original_dim"], 4)

    def test_self_kernel_near_one(self):
        h = P.hilbert_project()
        self.assertLess(abs(h["kernel_self_estimate"] - 1.0), 0.2)

    def test_norm_does_not_inflate_with_dim(self):
        small = P.hilbert_project(dimensions=40)
        large = P.hilbert_project(dimensions=400)
        # 旧实现 Σ1/(k+1) 会发散膨胀；RFF 应保持同量级
        self.assertLess(large["hilbert_norm"], small["hilbert_norm"] * 2.0)
        self.assertLess(large["projection_full_length"], 401)

    def test_uses_rff_features(self):
        h = P.hilbert_project()
        self.assertEqual(h["map"], "random_fourier_features")
        self.assertIn("exp(-", h["kernel"])


class TestDissipationEntropyProduction(unittest.TestCase):
    """R8：Shannon 熵 + 熵产率 σ = XᵀLX（力/流结构）。"""

    def setUp(self):
        self.d = P.dissipation_measure()

    def test_keeps_original_keys(self):
        for k in ("structure", "task_flow", "total", "success", "failure",
                  "probabilities", "shannon_entropy", "entropy_max", "order",
                  "disorder", "dissipation", "needs_reorganization", "note"):
            self.assertIn(k, self.d)

    def test_sigma_positive_and_pd(self):
        ep = self.d["entropy_production"]
        self.assertGreater(ep["sigma"], 0.0)
        self.assertTrue(ep["symmetric_onsager"])
        self.assertTrue(ep["positive_definite"])
        self.assertEqual(ep["leading_principal_minors"], [2.0, 1.91])

    def test_force_is_probability_vector(self):
        ep = self.d["entropy_production"]
        self.assertAlmostEqual(sum(ep["forces"]), 1.0, places=6)
        self.assertEqual(ep["forces"], [0.8, 0.2])

    def test_all_fail_has_high_entropy(self):
        d = P.dissipation_measure(task_flow="fail,fail,fail,fail")
        self.assertEqual(d["success"], 0)
        self.assertAlmostEqual(d["shannon_entropy"], 0.0, places=6)  # 单一结果熵为0
        self.assertEqual(d["probabilities"]["fail"], 1.0)

    def test_half_fail_is_max_entropy(self):
        d = P.dissipation_measure(task_flow="ok,fail,ok,fail")
        self.assertAlmostEqual(d["shannon_entropy"], 1.0, places=6)
        self.assertAlmostEqual(d["order"], 0.0, places=6)
        self.assertTrue(d["needs_reorganization"])


class TestEmergenceChainStillWorks(unittest.TestCase):
    """emergence_chain 消费 hil["projected_dim"] 与 bay["decision"]，换芯后必须仍通。"""

    def test_chain_runs(self):
        e = P.emergence_chain(input_concept="换芯验证")
        self.assertIn("emergence", e)
        self.assertIn("steps", e)

    def test_downstream_keys_present(self):
        e = P.emergence_chain(input_concept="换芯验证")
        blob = repr(e)
        self.assertIn("ALLOW", blob)


class TestOtherFunctionsUntouched(unittest.TestCase):
    """未换芯的函数保持原语义（锚点回归）。"""

    def test_mobius_edge_flips(self):
        m = P.mobius_edge()
        self.assertEqual(m["topology"], "mobius")
        self.assertTrue(m["mobius_loop"]["loop_closed"])
        for e in m["edges"]:
            self.assertEqual(e["cosine_forward_flipped"], -1.0)

    def test_klein_convergence_scales(self):
        k = P.klein_convergence()
        self.assertEqual(k["topology"], "klein")
        self.assertEqual(k["path_count"], 3)
        self.assertGreater(k["root_cause"]["convergence_strength"], 0.0)

    def test_pack_summary(self):
        s = P.pack_summary()
        self.assertIn("topology_resonance", repr(s))


class TestDifyWorkflowGap(unittest.TestCase):
    """③ dify-workflow 端点缺口已由源码取证关闭。"""

    def test_gap_closed(self):
        from holoaeon import gap_adapters as ga
        rep = ga.check_gaps()
        self.assertEqual(rep["gaps"], 0)
        self.assertEqual(rep["adapted"], 12)
        self.assertEqual(rep["verdict"], "PASS")

    def test_request_shape_from_source(self):
        from holoaeon import gap_adapters as ga
        r = ga.build_request("dify-workflow", extra={"inputs": {"q": "x"}})
        self.assertEqual(r["url"], "https://api.dify.ai/v1/workflows/run")
        self.assertEqual(set(r["body"].keys()), {"inputs", "response_mode", "user"})
        self.assertEqual(r["body"]["response_mode"], "blocking")

    def test_streaming_mode(self):
        from holoaeon import gap_adapters as ga
        r = ga.build_request("dify-workflow", extra={"inputs": {}}, stream=True)
        self.assertEqual(r["body"]["response_mode"], "streaming")
        self.assertTrue(r["stream"])


if __name__ == "__main__":
    unittest.main()
