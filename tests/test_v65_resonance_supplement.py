# -*- coding: utf-8 -*-
"""V65 拓扑共振与耗散验证域 · 外部补齐批测试

覆盖：
- 文献锚与上游项目台账的结构完整性（机制 7 位全覆盖、usage 合规）
- 七位机制的可实测数学判据（熵产率 / 正交分发 / 多源融合 / 序贯检验 / 核近似 / 序参量 / 常数分解）
- check() 总闸与台账落盘
"""
import io
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holoaeon import resonance_supplement as rs  # noqa: E402


class TestSchemaAndLedgers(unittest.TestCase):
    def test_schema_version(self):
        self.assertEqual(rs.SCHEMA_VERSION, "RESONANCE-SUPPLEMENT-v1.0")

    def test_literature_count(self):
        self.assertEqual(len(rs.LITERATURE), 9)

    def test_literature_fields(self):
        for item in rs.LITERATURE:
            for key in ("id", "mechanisms", "title", "author", "year", "source", "claim", "usable"):
                self.assertIn(key, item, item.get("id"))
                self.assertTrue(str(item[key]).strip(), item.get("id"))

    def test_literature_covers_seven_mechanisms(self):
        covered = set()
        for item in rs.LITERATURE:
            covered.update(item["mechanisms"])
        self.assertEqual(covered, {"C1", "R2", "R5", "R6", "R7", "R8", "X2"})

    def test_upstream_count(self):
        self.assertEqual(len(rs.UPSTREAM), 12)

    def test_upstream_usage_discipline(self):
        allowed = {"method_only", "readonly_reference"}
        for item in rs.UPSTREAM:
            self.assertIn(item["usage"], allowed, item["full_name"])

    def test_upstream_fields(self):
        for item in rs.UPSTREAM:
            for key in ("full_name", "stars", "target", "role", "usage", "absorb"):
                self.assertIn(key, item, item.get("full_name"))
            self.assertIsInstance(item["stars"], int)
            self.assertGreaterEqual(item["stars"], 0)

    def test_mechanism_links_seven(self):
        self.assertEqual(set(rs.MECHANISM_LINKS), {"C1", "R2", "R5", "R6", "R7", "R8", "X2"})
        for key, val in rs.MECHANISM_LINKS.items():
            self.assertTrue(hasattr(rs, val["impl"].split("+")[0]), val["impl"])

    def test_reports(self):
        self.assertEqual(rs.literature_report("C1")["count"], 2)
        self.assertEqual(rs.upstream_report("R5")["count"], 2)
        self.assertGreater(rs.upstream_report()["total_stars"], 0)


class TestEntropyProduction(unittest.TestCase):
    def test_sigma_value(self):
        got = rs.entropy_production()
        self.assertAlmostEqual(got["sigma"], 2.55, places=6)

    def test_flows(self):
        got = rs.entropy_production()
        self.assertAlmostEqual(got["flows"][0], 2.15, places=6)
        self.assertAlmostEqual(got["flows"][1], 0.8, places=6)

    def test_symmetric_and_positive_definite(self):
        got = rs.entropy_production()
        self.assertTrue(got["symmetric_onsager"])
        self.assertTrue(got["positive_definite"])
        self.assertEqual(got["leading_principal_minors"], [2.0, 1.91])

    def test_convex_scaling(self):
        got = rs.entropy_production()
        for row in got["convex_scaling"]:
            self.assertAlmostEqual(row["ratio_to_t2"], 1.0, places=6)

    def test_asymmetric_detected(self):
        got = rs.entropy_production(onsager=[[2.0, 0.5], [0.1, 1.0]])
        self.assertFalse(got["symmetric_onsager"])
        self.assertGreater(got["onsager_asymmetry"], 0.0)

    def test_negative_definite_rejected(self):
        got = rs.entropy_production(onsager=[[2.0, 0.3], [0.3, -1.0]])
        self.assertFalse(got["positive_definite"])


class TestMandalaWht(unittest.TestCase):
    def test_reconstruction_exact(self):
        got = rs.mandala_wht()
        self.assertLessEqual(got["reconstruction_error"], 1e-12)
        self.assertTrue(got["perfect"])

    def test_orthogonality(self):
        got = rs.mandala_wht()
        self.assertLessEqual(got["orthogonality_max_dev"], 1e-12)

    def test_center_is_mean(self):
        got = rs.mandala_wht()
        self.assertAlmostEqual(got["center_dc"], 4.5, places=6)
        self.assertTrue(got["center_is_mean"])

    def test_spectrum_shape(self):
        got = rs.mandala_wht([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])
        self.assertEqual(got["spectrum"], [4.5, -0.5, -1.0, 0.0, -2.0, 0.0, 0.0, 0.0])

    def test_uniform_only_dc(self):
        got = rs.mandala_wht([3.0] * 8)
        self.assertEqual(got["spectrum"], [3.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

    def test_parseval(self):
        got = rs.mandala_wht()
        self.assertAlmostEqual(got["parseval_ratio"], 1.0, places=9)

    def test_requires_eight(self):
        with self.assertRaises(ValueError):
            rs.mandala_wht([1.0, 2.0, 3.0])


class TestKalmanFuse(unittest.TestCase):
    def test_fused_state(self):
        got = rs.kalman_fuse()
        self.assertAlmostEqual(got["fused_state"], 10.371429, places=6)

    def test_fused_variance(self):
        got = rs.kalman_fuse()
        self.assertAlmostEqual(got["fused_variance"], 0.190476, places=6)

    def test_weights_sum_to_one(self):
        got = rs.kalman_fuse()
        self.assertAlmostEqual(sum(s["weight"] for s in got["sources"]), 1.0, places=9)

    def test_sequential_equals_batch(self):
        got = rs.kalman_fuse()
        self.assertTrue(got["sequential_matches_batch"])

    def test_all_consistent_on_clean_sources(self):
        got = rs.kalman_fuse()
        self.assertTrue(got["all_consistent"])
        for row in got["sources"]:
            self.assertLess(row["nis"], rs.CHI2_1DOF_95)

    def test_outlier_detected(self):
        got = rs.kalman_fuse([(10.0, 1.0), (10.5, 0.25), (9.8, 4.0), (30.0, 0.5)])
        self.assertFalse(got["all_consistent"])
        self.assertTrue(got["outliers"])


class TestSprt(unittest.TestCase):
    def test_thresholds(self):
        got = rs.sprt_gate()
        self.assertAlmostEqual(got["threshold_A"], 2.890372, places=6)
        self.assertAlmostEqual(got["threshold_B"], -2.251292, places=6)

    def test_stops_on_h1(self):
        got = rs.sprt_gate([1, 1, 0, 1, 1, 0, 1, 0, 1, 1])
        self.assertEqual(got["decision"], "H1")
        self.assertEqual(got["stopped_at"], 5)

    def test_stops_on_h0(self):
        got = rs.sprt_gate([0, 0, 0, 1, 0, 0, 0, 0, 0, 0])
        self.assertEqual(got["decision"], "H0")
        self.assertEqual(got["stopped_at"], 9)

    def test_llr_monotone_path_on_h1(self):
        got = rs.sprt_gate([1, 1, 0, 1, 1, 0, 1, 0, 1, 1])
        self.assertEqual(len(got["llr_path"]), got["stopped_at"])

    def test_short_observation_continues(self):
        got = rs.sprt_gate([0])
        self.assertEqual(got["decision"], "CONTINUE")


class TestRffKernel(unittest.TestCase):
    def test_error_decreases_with_dim(self):
        got = rs.rff_kernel()
        self.assertTrue(got["mae_trends_down"])
        self.assertLess(got["dims"][-1]["mae"], got["dims"][0]["mae"])

    def test_mae_values(self):
        got = rs.rff_kernel()
        self.assertAlmostEqual(got["dims"][0]["mae"], 0.198497, places=6)
        self.assertAlmostEqual(got["dims"][2]["mae"], 0.034768, places=6)

    def test_deterministic(self):
        a = rs.rff_kernel()
        b = rs.rff_kernel()
        self.assertEqual(a["dims"], b["dims"])

    def test_pair_count(self):
        got = rs.rff_kernel()
        self.assertEqual(got["pairs"], 36)


class TestKuramoto(unittest.TestCase):
    def test_synchronized_case(self):
        got = rs.kuramoto_order([0.0, 0.01, 0.02, 0.0, 0.01])
        self.assertGreater(got["r"], 0.99)
        self.assertTrue(got["synchronized"])

    def test_desynchronized_case(self):
        got = rs.kuramoto_order([0.0, 1.2, 2.5, 3.9, 5.1])
        self.assertLess(got["r"], 0.2)
        self.assertFalse(got["synchronized"])

    def test_critical_coupling(self):
        got = rs.kuramoto_sweep()
        self.assertAlmostEqual(got["kc_theory"], 0.797885, places=6)

    def test_sweep_monotone_tail(self):
        curve = rs.kuramoto_sweep()["curve"]
        tail = [x["r"] for x in curve[-4:]]
        for i in range(len(tail) - 1):
            self.assertGreaterEqual(tail[i + 1], tail[i])

    def test_empirical_critical_exists(self):
        got = rs.kuramoto_sweep()
        self.assertIsNotNone(got["kc_empirical"])

    def test_active_nodes_factorization(self):
        got = rs.decompose_active_nodes()
        self.assertEqual(got["factorization"], [13, 61, 137])
        self.assertTrue(got["product_check"])
        self.assertFalse(got["is_prime"])

    def test_active_nodes_ratio(self):
        got = rs.decompose_active_nodes()
        self.assertAlmostEqual(got["relative_to_matrix"], 0.061325, places=6)
        self.assertEqual(got["matrix_quotient"], {"q": 81, "r": 830})


class TestCheckAndLedger(unittest.TestCase):
    def test_check_passes(self):
        got = rs.check()
        self.assertEqual(got["verdict"], "PASS")
        self.assertEqual(got["passed"], 7)
        self.assertEqual(got["mechanisms"], 7)

    def test_check_covers_all(self):
        got = rs.check()
        self.assertEqual({x["mechanism"] for x in got["items"]}, {"C1", "R2", "R5", "R6", "R7", "R8", "X2"})

    def test_ledger_roundtrip(self):
        tmp = os.path.join(tempfile.mkdtemp(), "ledger.json")
        payload = rs.ledger(tmp)
        self.assertTrue(payload["check"]["verdict"] == "PASS")
        with io.open(tmp, encoding="utf-8") as f:
            back = json.load(f)
        self.assertEqual(back["schema"], rs.SCHEMA_VERSION)
        self.assertEqual(len(back["literature"]), 9)
        self.assertEqual(len(back["upstream"]), 12)


if __name__ == "__main__":
    unittest.main()
