# -*- coding: utf-8 -*-
"""V76 双口径收口批测试：七面判据 + 金丝雀（逐面篡改必红）。

口径纪律：
  · base 必须逐字段等于主路 forge_absorb —— 这是「主路零改动」的唯一可验证形态；
  · bridge 与 bridged_absorb 现跑一致 —— 第二口径不许手写；
  · 真空样本不许被伪装成已修复 —— F4 单独守这一条。
"""

import copy
import unittest

from holoaeon.dual_caliber import (BOUNDARIES, DECISIONS, SCHEMA, absorb_dual,
                                   build_ledger, verify)
from holoaeon.forge_bureau import forge_absorb
from holoaeon.prehistory_semantic_bridge import (EXPECTED_ZERO_BEFORE,
                                                 KNOWN_VACUUM, SAMPLES,
                                                 ZERO_AFTER_MAX,
                                                 bridged_absorb)


class T1SchemaAndConstants(unittest.TestCase):
    """T1 · 常量与边界声明。"""

    def test_schema(self):
        self.assertEqual(SCHEMA, "DUAL-CALIBER-v1")

    def test_decisions_three(self):
        self.assertEqual(DECISIONS, ("bridge_adopted", "base_kept", "vacuum_kept"))

    def test_boundaries_five(self):
        self.assertEqual(len(BOUNDARIES), 5)

    def test_boundaries_nonempty(self):
        for b in BOUNDARIES:
            self.assertTrue(b.strip())

    def test_seal_in_ledger(self):
        led = build_ledger()
        self.assertEqual(led["seal"], "潮起开门，潮落闭嘴")


class T2SingleRecord(unittest.TestCase):
    """T2 · 单条对照：base 与主路逐字段相等。"""

    def test_base_equals_mainline_all_samples(self):
        for name in SAMPLES:
            spec = {"name": name, "description": "", "tags": []}
            dual = absorb_dual(spec)
            main = forge_absorb(spec)["absorbed_into"]
            with self.subTest(name=name[:20]):
                self.assertEqual(dual["base"]["repo"], main["repo"])
                self.assertEqual(dual["base"]["cang"], main["cang"])
                self.assertEqual(dual["base"]["domain"], main["domain"])
                self.assertEqual(dual["base"]["score"], main["score"])

    def test_bridge_equals_bridged_absorb(self):
        for name in SAMPLES:
            spec = {"name": name, "description": "", "tags": []}
            dual = absorb_dual(spec)
            br = bridged_absorb(spec)["bridged"]
            with self.subTest(name=name[:20]):
                self.assertEqual(dual["bridge"]["repo"], br["repo"])
                self.assertEqual(dual["bridge"]["cang"], br["cang"])
                self.assertEqual(dual["bridge"]["score"], br["score"])

    def test_delta_flags_consistent(self):
        for name in SAMPLES:
            dual = absorb_dual({"name": name, "description": "", "tags": []})
            expect = dual["bridge"]["repo"] != dual["base"]["repo"]
            with self.subTest(name=name[:20]):
                self.assertEqual(dual["delta"]["repo_changed"], expect)

    def test_score_delta_rounding(self):
        for name in SAMPLES:
            dual = absorb_dual({"name": name, "description": "", "tags": []})
            with self.subTest(name=name[:20]):
                self.assertEqual(
                    dual["delta"]["score_delta"],
                    round(dual["bridge"]["score"] - dual["base"]["score"], 4))

    def test_decision_legal(self):
        for name in SAMPLES:
            dual = absorb_dual({"name": name, "description": "", "tags": []})
            self.assertIn(dual["decision"], DECISIONS)

    def test_adopted_has_terms(self):
        for name in SAMPLES:
            dual = absorb_dual({"name": name, "description": "", "tags": []})
            if dual["decision"] == "bridge_adopted":
                with self.subTest(name=name[:20]):
                    self.assertTrue(dual["attribution"]["matched_terms"])

    def test_vacuum_kept_zero_and_registered(self):
        for name in SAMPLES:
            dual = absorb_dual({"name": name, "description": "", "tags": []})
            if dual["decision"] == "vacuum_kept":
                with self.subTest(name=name[:20]):
                    self.assertEqual(dual["bridge"]["score"], 0.0)
                    self.assertTrue(any(v in name for v in KNOWN_VACUUM))

    def test_same_repo_never_adopted(self):
        for name in SAMPLES:
            dual = absorb_dual({"name": name, "description": "", "tags": []})
            if not dual["delta"]["repo_changed"] and dual["bridge"]["score"] > 0.0:
                with self.subTest(name=name[:20]):
                    self.assertEqual(dual["decision"], "base_kept")


class T3LedgerTotals(unittest.TestCase):
    """T3 · 台账汇总与 V69 实测基线对账。"""

    def setUp(self):
        self.led = build_ledger()

    def test_sample_count(self):
        self.assertEqual(len(self.led["samples"]), len(SAMPLES))

    def test_zero_before_matches_v69(self):
        self.assertEqual(self.led["totals"]["zero_before"], EXPECTED_ZERO_BEFORE)

    def test_zero_after_matches_v69(self):
        self.assertEqual(self.led["totals"]["zero_after"], ZERO_AFTER_MAX)

    def test_changed_count(self):
        self.assertEqual(self.led["totals"]["changed"], 12)

    def test_totals_partition(self):
        t = self.led["totals"]
        self.assertEqual(t["changed"] + t["unchanged"], t["samples"])
        self.assertEqual(t["bridge_adopted"] + t["base_kept"] + t["vacuum_kept"],
                         t["samples"])

    def test_self_digest_shape(self):
        d = self.led["self_digest"]
        self.assertEqual(len(d), 16)
        int(d, 16)

    def test_calibers(self):
        self.assertEqual(self.led["calibers"], ["base", "bridge"])

    def test_deterministic(self):
        self.assertEqual(build_ledger()["self_digest"], self.led["self_digest"])

    def test_known_vacuum_listed(self):
        self.assertEqual(self.led["known_vacuum"], list(KNOWN_VACUUM))


class T4VerifyFaces(unittest.TestCase):
    """T4 · 七面判据在干净台账上全绿。"""

    def setUp(self):
        self.led = build_ledger()

    def test_verdict_pass(self):
        rep = verify(self.led)
        self.assertEqual(rep["verdict"], "PASS")
        self.assertEqual(rep["mismatch"], [])

    def test_seven_faces(self):
        rep = verify(self.led)
        self.assertEqual(len(rep["faces"]), 7)
        self.assertTrue(all(rep["faces"].values()))

    def test_face_names(self):
        keys = set(verify(self.led)["faces"])
        for k in ("F1_base_readonly_equal", "F2_bridge_rerun_equal",
                  "F3_attribution_traceable", "F4_vacuum_registered",
                  "F5_deterministic_digest", "F6_totals_consistent",
                  "F7_self_digest"):
            self.assertIn(k, keys)

    def test_digest_carried(self):
        self.assertEqual(verify(self.led)["digest"], self.led["self_digest"])

    def test_schema_carried(self):
        self.assertEqual(verify(self.led)["schema"], SCHEMA)


class T5Canary(unittest.TestCase):
    """T5 · 金丝雀：每一面单独篡改都必须红（能红才算判据）。"""

    def setUp(self):
        self.led = build_ledger()

    def _bad(self, mutate):
        bad = copy.deepcopy(self.led)
        mutate(bad)
        return verify(bad)

    def test_f1_base_score_tamper(self):
        rep = self._bad(lambda d: d["samples"][0]["base"].update(score=0.9))
        self.assertEqual(rep["verdict"], "FAIL")
        self.assertFalse(rep["faces"]["F1_base_readonly_equal"])

    def test_f2_bridge_repo_tamper(self):
        rep = self._bad(lambda d: d["samples"][1]["bridge"].update(repo="holoaeon-zz"))
        self.assertEqual(rep["verdict"], "FAIL")
        self.assertFalse(rep["faces"]["F2_bridge_rerun_equal"])

    def test_f3_decision_tamper(self):
        rep = self._bad(lambda d: d["samples"][2].update(decision="base_kept"))
        self.assertEqual(rep["verdict"], "FAIL")
        self.assertFalse(rep["faces"]["F3_attribution_traceable"])

    def test_f4_unregistered_vacuum(self):
        # 把第一条（有名有姓、桥后有词证）谎报成零分真空 → 未在册
        def mutate(d):
            d["samples"][0]["still_zero"] = True
        rep = self._bad(mutate)
        self.assertEqual(rep["verdict"], "FAIL")
        self.assertFalse(rep["faces"]["F4_vacuum_registered"])

    def test_f5_digest_from_other_run(self):
        def mutate(d):
            d["self_digest"] = "0" * 16
        rep = self._bad(mutate)
        self.assertEqual(rep["verdict"], "FAIL")
        self.assertFalse(rep["faces"]["F7_self_digest"])

    def test_f6_totals_tamper(self):
        rep = self._bad(lambda d: d["totals"].update(changed=3))
        self.assertEqual(rep["verdict"], "FAIL")
        self.assertFalse(rep["faces"]["F6_totals_consistent"])

    def test_row_order_swap(self):
        def mutate(d):
            d["samples"][0], d["samples"][1] = d["samples"][1], d["samples"][0]
        rep = self._bad(mutate)
        self.assertEqual(rep["verdict"], "FAIL")

    def test_extra_sample_row(self):
        def mutate(d):
            d["samples"].append(copy.deepcopy(d["samples"][0]))
        rep = self._bad(mutate)
        self.assertEqual(rep["verdict"], "FAIL")

    def test_boundaries_tamper_red(self):
        def mutate(d):
            d["boundaries"] = ["一条假的边界"]
        rep = self._bad(mutate)
        self.assertEqual(rep["verdict"], "FAIL")
        self.assertFalse(rep["faces"]["F7_self_digest"])

    def test_problems_reported(self):
        rep = self._bad(lambda d: d["samples"][0]["base"].update(repo="holoaeon-zz"))
        self.assertTrue(rep["problems"])
        self.assertTrue(any("F1" in p for p in rep["problems"]))


class T6Cli(unittest.TestCase):
    """T6 · CLI 三档动作。"""

    def test_verify_exit_zero(self):
        from holoaeon import dual_caliber as dc
        self.assertEqual(dc.main(["verify"]), 0)

    def test_report_exit_zero(self):
        from holoaeon import dual_caliber as dc
        self.assertEqual(dc.main(["report"]), 0)

    def test_build_exit_zero(self):
        from holoaeon import dual_caliber as dc
        self.assertEqual(dc.main(["build"]), 0)

    def test_bad_action(self):
        from holoaeon import dual_caliber as dc
        self.assertEqual(dc.main(["nope"]), 2)

    def test_default_is_verify(self):
        from holoaeon import dual_caliber as dc
        self.assertEqual(dc.main([]), 0)


if __name__ == "__main__":
    unittest.main()
