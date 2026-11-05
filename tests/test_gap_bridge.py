# -*- coding: utf-8 -*-
"""V32 缺口进化桥测试。零依赖，确定性断言。"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holoaeon.gap_bridge import (CHAIN_POSITION, GapProposer,
                                 SkipAuditor, StdlibShadowGuard, SEAL)


class TestGapBridge(unittest.TestCase):
    def test_chain_position_bridge(self):
        self.assertEqual(CHAIN_POSITION["ring"], "bridge")
        self.assertIn("magic_lamp", CHAIN_POSITION["upstream"])
        self.assertIn("titan_evolver", CHAIN_POSITION["upstream"])

    def test_shadow_scan_clean_dir(self):
        with tempfile.TemporaryDirectory() as d:
            r = StdlibShadowGuard(d).scan()
            self.assertTrue(r["ok"])
            self.assertEqual(r["offenders"], [])

    def test_shadow_scan_detects_inspect(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "inspect.py"), "w",
                      encoding="utf-8") as f:
                f.write("# stray\n")
            r = StdlibShadowGuard(d).scan()
            self.assertFalse(r["ok"])
            self.assertEqual(r["offenders"][0]["shadow"], "inspect.py")

    def test_shadow_scan_report_only(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "json.py")
            with open(p, "w", encoding="utf-8") as f:
                f.write("# stray\n")
            StdlibShadowGuard(d).scan()
            self.assertTrue(os.path.exists(p))   # 只报不删

    def test_unblock_hint(self):
        hints = StdlibShadowGuard.unblock_hint(
            [{"dir": "x", "shadow": "inspect.py", "stdlib": "inspect"}])
        self.assertIn("rename", hints[0]["hint"])

    def test_skip_audit(self):
        r = SkipAuditor.audit(["test_a ... ok",
                               "test_b ... skipped 'reason'",
                               "test_c ... ok"])
        self.assertEqual(r["skipped_count"], 1)
        self.assertEqual(r["verdict"], "needs_review")

    def test_skip_audit_clean(self):
        r = SkipAuditor.audit(["test_a ... ok"])
        self.assertEqual(r["verdict"], "clean")

    def test_gap_proposer(self):
        r = GapProposer(threshold=0.5).propose(
            ["图数据库", "时序异常检测"], goal="康复工程整合")
        self.assertEqual(r["count"], 2)
        self.assertEqual(r["proposals"][0]["capability"], "图数据库")
        self.assertEqual(r["proposals"][0]["threshold"], 0.5)

    def test_gap_proposer_accepts_str(self):
        r = GapProposer().propose("单gap", goal="g")
        self.assertEqual(r["count"], 1)

    def test_to_titan_contract(self):
        r = GapProposer().propose(["g1"], goal="g")
        rows = GapProposer.to_titan(r["proposals"])
        self.assertEqual(set(rows[0].keys()),
                         {"capability", "source", "evidence", "threshold"})

    def test_seal_everywhere(self):
        for obj in (StdlibShadowGuard(os.getcwd()).scan(),
                    SkipAuditor.audit([]),
                    GapProposer().propose([], goal="g")):
            self.assertEqual(obj["seal"], SEAL)


if __name__ == "__main__":
    unittest.main()
