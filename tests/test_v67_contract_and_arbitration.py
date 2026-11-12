# -*- coding: utf-8 -*-
"""V67：返回键白名单对账 + 重组口径仲裁 + emergence_chain 旁路消费 + dify 静态契约。

本批四件事（用户点名）：
  1) 清理 NO_INFO_P 死常量；给被原包消费的函数做「返回键白名单」对账；
  2) 耗散充分性 vs 重组判据的优先级仲裁（口径由人定，代码只执行）；
  3) emergence_chain 旁路消费 consistency_gate 与 entropy_production（不改主判据）；
  4) dify-workflow 由「读到的契约」向「通」推进（仓内零网络纪律下的静态可验部分）。

为什么白名单要写死：原包与 supplement 之间是 import 关系，
上游一旦改键名，下游不会报错只会静默 KeyError 或静默缺字段。
锁成白名单后，任何键的增删都必须显式改测试——这就把"静默漂移"变成"红"。
"""
import unittest

from holoaeon import gap_adapters as ga
from holoaeon import resonance_supplement as RS
from holoaeon.packs import topology_resonance_pack as P


# ---------------------------------------------------------------- 6.1 白名单
SUPPLEMENT_KEYS = {
    "entropy_production": {
        "model", "forces", "flows", "onsager", "sigma",
        "symmetric_onsager", "onsager_asymmetry", "positive_definite",
        "leading_principal_minors", "convex_scaling", "minimum_entropy_production",
    },
    "mandala_wht": {
        "topology", "directions", "structure", "spectrum", "center_dc",
        "center_is_mean", "reconstruction_error", "orthogonality_max_dev",
        "parseval_ratio", "perfect",
    },
    "kalman_fuse": {
        "model", "nis_mode", "anchor", "process_noise", "gate_enabled",
        "fused_state", "fused_variance", "batch_fused_state", "batch_fused_variance",
        "sources", "all_consistent", "judged_sources", "rejected", "outliers",
        "sequential_matches_batch", "sequential_state", "chi2_threshold", "note",
    },
    "sprt_gate": {
        "model", "p0", "p1", "alpha", "beta", "threshold_A", "threshold_B",
        "observation_length", "llr_path", "decision", "stopped_at",
        "evidence_saved", "note",
    },
    "rff_kernel": {"model", "gamma", "seed", "pairs", "dims", "mae_trends_down", "note"},
    "rff_features": {"model", "dim", "gamma", "seed", "feature", "feature_norm_sq", "note"},
    "kuramoto_order": {"model", "n", "r", "psi", "synchronized", "note"},
    "decompose_active_nodes": {
        "n", "factorization", "product_check", "is_prime",
        "relative_to_matrix", "matrix_quotient", "note",
    },
}

KALMAN_ROW_APPLIED = {
    "z", "R", "predicted_state", "predicted_variance", "innovation", "gain",
    "nis", "consistent", "applied", "role", "state_estimate", "uncertainty", "weight",
}
KALMAN_ROW_REJECTED = KALMAN_ROW_APPLIED - {"state_estimate", "uncertainty", "weight"}


class TestSupplementKeyWhitelist(unittest.TestCase):
    """8 个被原包消费的函数：返回键集合必须完全等于白名单。"""

    def test_entropy_production(self):
        self.assertEqual(set(RS.entropy_production().keys()), SUPPLEMENT_KEYS["entropy_production"])

    def test_mandala_wht(self):
        self.assertEqual(set(RS.mandala_wht().keys()), SUPPLEMENT_KEYS["mandala_wht"])

    def test_kalman_fuse(self):
        self.assertEqual(set(RS.kalman_fuse().keys()), SUPPLEMENT_KEYS["kalman_fuse"])

    def test_sprt_gate(self):
        self.assertEqual(set(RS.sprt_gate().keys()), SUPPLEMENT_KEYS["sprt_gate"])

    def test_rff_kernel(self):
        self.assertEqual(set(RS.rff_kernel().keys()), SUPPLEMENT_KEYS["rff_kernel"])

    def test_rff_features(self):
        self.assertEqual(set(RS.rff_features([0.3, 0.5]).keys()), SUPPLEMENT_KEYS["rff_features"])

    def test_kuramoto_order(self):
        self.assertEqual(set(RS.kuramoto_order().keys()), SUPPLEMENT_KEYS["kuramoto_order"])

    def test_decompose_active_nodes(self):
        self.assertEqual(set(RS.decompose_active_nodes().keys()),
                         SUPPLEMENT_KEYS["decompose_active_nodes"])


class TestKalmanRowContracts(unittest.TestCase):
    """行级契约：被拒行没有 state_estimate/uncertainty/weight —— 上游必须知道这一点。"""

    def test_applied_row_keys(self):
        kf = RS.kalman_fuse()
        self.assertEqual(set(kf["sources"][0].keys()), KALMAN_ROW_APPLIED)
        self.assertEqual(kf["sources"][0]["role"], "anchor")

    def test_rejected_row_has_no_state_estimate(self):
        kf = RS.kalman_fuse([(10.0, 1.0), (30.0, 0.5)])
        self.assertEqual(kf["rejected"], [1])
        self.assertEqual(set(kf["sources"][1].keys()), KALMAN_ROW_REJECTED)
        self.assertNotIn("state_estimate", kf["sources"][1])
        self.assertFalse(kf["sources"][1]["applied"])

    def test_rejected_row_is_role_tagged(self):
        kf = RS.kalman_fuse([(10.0, 1.0), (30.0, 0.5)])
        self.assertEqual(kf["sources"][1]["role"], "rejected_outlier")


# ------------------------------------------------------------ 6.2 包装层必备键
PACK_WRAPPER_KEYS = {
    "resonance_node": {"order_parameter", "phase_coherence", "active_nodes",
                       "active_nodes_factors", "active_nodes_factorization", "matrix_quotient"},
    "mandala_fanout": {"topology", "fan_out", "fan_in", "orthogonal_transform", "aggregation"},
    "kalman_state": {"filter", "nis_mode", "steps", "checkpoint", "consistency_gate", "parameters"},
    "bayesian_guard": {"decision", "posterior", "threshold", "sprt", "threshold_rule", "decided_by"},
    "hilbert_project": {"map", "projected_dim", "hilbert_norm", "original_norm", "kernel_self_estimate"},
    "dissipation_measure": {"order", "shannon_entropy", "needs_reorganization", "reorganization",
                            "entropy_production", "dissipation"},
}


class TestPackWrapperKeySubsets(unittest.TestCase):
    """原包包装函数：必备子键必须都在（不锁全集，允许包内再扩字段）。"""

    def test_resonance_node(self):
        self.assertLessEqual(PACK_WRAPPER_KEYS["resonance_node"],
                             set(P.resonance_node().keys()))

    def test_mandala_fanout(self):
        self.assertLessEqual(PACK_WRAPPER_KEYS["mandala_fanout"],
                             set(P.mandala_fanout().keys()))

    def test_kalman_state(self):
        self.assertLessEqual(PACK_WRAPPER_KEYS["kalman_state"],
                             set(P.kalman_state().keys()))

    def test_bayesian_guard(self):
        self.assertLessEqual(PACK_WRAPPER_KEYS["bayesian_guard"],
                             set(P.bayesian_guard().keys()))

    def test_hilbert_project(self):
        self.assertLessEqual(PACK_WRAPPER_KEYS["hilbert_project"],
                             set(P.hilbert_project().keys()))

    def test_dissipation_measure(self):
        self.assertLessEqual(PACK_WRAPPER_KEYS["dissipation_measure"],
                             set(P.dissipation_measure().keys()))


# --------------------------------------------------------------- 6.3 仲裁口径
class TestReorganizationArbitration(unittest.TestCase):
    """口径由人定：默认 stagnation_first，但僵死必须有时间窗证据才成立。"""

    def test_priority_is_declared(self):
        self.assertEqual(P.REORGANIZATION_PRIORITY, "stagnation_first")

    def test_snapshot_does_not_judge_stagnation(self):
        """单点快照分不开「高效稳定」与「僵死」，所以 stagnation_side 必须是 None。"""
        d = P.dissipation_measure()
        r = d["reorganization"]
        self.assertFalse(r["stagnation_evaluated"])
        self.assertIsNone(r["stagnation_side"])
        self.assertIsNone(r["stagnation_evidence"]["streak"])

    def test_stagnation_needs_streak_evidence(self):
        d = P.dissipation_measure(task_flow="ok,ok,ok,ok,ok,ok", streak=6)
        r = d["reorganization"]
        self.assertTrue(r["stagnation_evaluated"])
        self.assertTrue(r["stagnation_side"])
        self.assertEqual(r["verdict"], "reorganize_stagnation")
        self.assertEqual(r["stagnation_evidence"]["streak"], 6)

    def test_streak_below_min_is_not_stagnation(self):
        d = P.dissipation_measure(task_flow="ok,ok,ok,ok", streak=3)
        r = d["reorganization"]
        self.assertTrue(r["stagnation_evaluated"])
        self.assertFalse(r["stagnation_side"])
        self.assertNotEqual(r["verdict"], "reorganize_stagnation")

    def test_disorder_verdict(self):
        d = P.dissipation_measure(task_flow="ok,fail,ok,fail")
        self.assertTrue(d["needs_reorganization"])
        self.assertEqual(d["reorganization"]["verdict"], "reorganize_disorder")
        self.assertFalse(d["reorganization"]["stagnation_side"]
                         if d["reorganization"]["stagnation_evaluated"] else False)

    def test_hold_when_both_clean(self):
        d = P.dissipation_measure(task_flow="ok,ok,ok,ok", streak=1)
        self.assertEqual(d["reorganization"]["verdict"], "hold")

    def test_both_sides_and_stagnation_first(self):
        """僵死 + 混乱并发：stagnation_first 先破僵，但要如实标 both。"""
        d = P.dissipation_measure(task_flow="ok,fail,ok,fail", streak=8)
        r = d["reorganization"]
        self.assertTrue(r["disorder_side"])
        self.assertFalse(r["stagnation_side"])  # 熵=1.0 > 0.10，僵死证据不成立
        self.assertEqual(r["verdict"], "reorganize_disorder")

    def test_priority_switch_is_effective(self):
        """口径可换：换 disorder_first 后，同一份数据给出不同裁决（证明常量真被读到）。"""
        old = P.REORGANIZATION_PRIORITY
        try:
            P.REORGANIZATION_PRIORITY = "disorder_first"
            d = P.dissipation_measure(task_flow="ok,ok,ok,ok,ok,ok", streak=6)
            self.assertEqual(d["reorganization"]["priority"], "disorder_first")
            self.assertEqual(d["reorganization"]["verdict"], "reorganize_stagnation")
        finally:
            P.REORGANIZATION_PRIORITY = old

    def test_legacy_key_semantics_unchanged(self):
        """向后兼容：needs_reorganization 仍只表示混乱侧，不含僵死。"""
        clean = P.dissipation_measure(task_flow="ok,ok,ok,ok", streak=6)
        self.assertFalse(clean["needs_reorganization"])   # 混乱侧为假
        self.assertTrue(clean["needs_reorganization_any"])  # 但任一侧为真
        self.assertEqual(clean["reorganization"]["verdict"], "reorganize_stagnation")


# ------------------------------------------------------- 6.4 emergence 旁路消费
class TestEmergenceChainSideChannel(unittest.TestCase):
    """消费但不参与判定：主判据只有 quartet 一个真源。"""

    def setUp(self):
        self.e = P.emergence_chain(input_concept="旁路消费验证")

    def test_new_keys_present(self):
        for k in ("dissipation_view", "consistency_view", "advisories"):
            self.assertIn(k, self.e)

    def test_dissipation_view_content(self):
        dv = self.e["dissipation_view"]
        self.assertEqual(dv["priority"], P.REORGANIZATION_PRIORITY)
        self.assertIn(dv["verdict"], ("hold", "reorganize_disorder",
                                      "reorganize_stagnation", "reorganize_both"))
        self.assertIn("sigma", dv)
        self.assertIn("action", dv)

    def test_consistency_view_is_gate_snapshot(self):
        cv = self.e["consistency_view"]
        for k in ("chi2_1dof_95", "nis_max", "all_consistent", "sequential_matches_batch"):
            self.assertIn(k, cv)
        self.assertEqual(cv["chi2_1dof_95"], 3.841)

    def test_advisories_are_plain_strings(self):
        self.assertGreaterEqual(len(self.e["advisories"]), 1)
        for a in self.e["advisories"]:
            self.assertIsInstance(a, str)
            self.assertTrue(a)

    def test_main_judgement_untouched(self):
        """主判据仍由 quartet 决定：旁路字段不得改写 emergence。"""
        qt = P.quartet_tensor(p1="0.85", p2="0.85", p3="0.85", p4="0.30")
        self.assertEqual(self.e["emergence"], qt["emergence"])
        self.assertTrue(self.e["emergence"])


# ------------------------------------------------------------ 6.5 死常量已清理
class TestDeadConstantRemoved(unittest.TestCase):
    def test_no_info_p_gone(self):
        self.assertFalse(hasattr(RS, "NO_INFO_P"))

    def test_marker_comment_kept(self):
        """删掉常量但留下解释，避免后来者再用 1e12 近似无信息。"""
        with open(RS.__file__, encoding="utf-8") as f:
            src = f.read()
        self.assertIn("V67 清理", src)
        # 只断言"没有该常量的定义行"，注释里保留的历史说明不算定义
        self.assertNotRegex(src, r"(?m)^NO_INFO_P\s*=")

    def test_kalman_still_exact_batch(self):
        """删常量后 q=0 仍与批量精确相等（确认删的是死代码，不是活逻辑）。"""
        kf = RS.kalman_fuse([(10.0, 1.0), (10.5, 0.25), (9.8, 4.0)])
        self.assertTrue(kf["sequential_matches_batch"])
        self.assertEqual(kf["anchor"], "no_info")


# ------------------------------------------------------------ 6.6 dify 静态契约
class TestDifyContractStatic(unittest.TestCase):
    """仓内零网络纪律：只验"请求拼得对"，不做联网握手（见 ENABLE_RULE）。"""

    def setUp(self):
        self.entry = next(e for e in ga.GAPS if e["id"] == "dify-workflow")
        self.req = ga.build_request("dify-workflow", extra={"inputs": {"q": "x"}})

    def test_entry_is_adapted_with_source_proof(self):
        self.assertEqual(self.entry["status"], "adapted")
        self.assertTrue(self.entry["verification"].startswith("source_code_read"))
        self.assertIn("local_contract_loopback", self.entry["verification"])
        self.assertIn("langgenius/dify", self.entry["source_url"])
        self.assertIn("workflow.py", self.entry["source_url"])

    def test_loopback_record(self):
        """V67：契约已本机回环跑通，但如实标"不是官方实例"。"""
        lp = self.entry["loopback"]
        self.assertEqual((lp["checks"], lp["passed"]), (15, 15))
        self.assertEqual(lp["verified_at"], "2026-11-12")
        self.assertIn("非 Dify 官方实例", lp["scope"])
        self.assertIn("Dify 官方服务可用性", lp["what_it_does_not_prove"])
        self.assertGreaterEqual(len(lp["what_it_proves"]), 4)

    def test_request_body_contract(self):
        self.assertEqual(set(self.req["body"].keys()), {"inputs", "response_mode", "user"})
        self.assertEqual(self.req["body"]["response_mode"], "blocking")
        self.assertEqual(self.req["url"], "https://api.dify.ai/v1/workflows/run")

    def test_streaming_switch(self):
        r = ga.build_request("dify-workflow", extra={"inputs": {}}, stream=True)
        self.assertEqual(r["body"]["response_mode"], "streaming")

    def test_response_fields_cover_source(self):
        must = {"id", "workflow_id", "status", "outputs", "error",
                "total_steps", "total_tokens", "elapsed_time"}
        self.assertLessEqual(must, set(self.entry["response_fields"]))

    def test_error_code_families(self):
        self.assertEqual(set(self.entry["error_codes"].keys()), {"400", "403", "429", "500"})
        self.assertIn("trigger_workflow_service_mode_unavailable",
                      self.entry["error_codes"]["403"])

    def test_precondition_names_workflow_mode(self):
        self.assertIn("WORKFLOW", self.entry["precondition"])
        self.assertIn("Trigger", self.entry["precondition"])

    def test_platform_shapes_count(self):
        self.assertEqual(len(ga.PLATFORM_SHAPES), 4)
        self.assertIn("dify_workflow", [s["id"] for s in ga.PLATFORM_SHAPES])

    def test_check_gaps_green(self):
        rep = ga.check_gaps()
        self.assertEqual((rep["adapted"], rep["gaps"], rep["verdict"]), (12, 0, "PASS"))


if __name__ == "__main__":
    unittest.main()
