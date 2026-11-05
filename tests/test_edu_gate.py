# -*- coding: utf-8 -*-
"""V36 教育域编排闸门测试。零依赖，确定性断言。"""
import unittest

from holoaeon.edu_gate import (CHAIN_POSITION, EduConductor,
                               LineageBus, RedlineSelfScan,
                               SelfEvalRubric, SEAL)

SCORES = {"架构完整性": 14.5, "四机制实现": 14.5, "六域能力": 14.0,
          "安全红线": 14.0, "工程可复现": 13.5, "诚实边界": 13.0}


class TestEduGate(unittest.TestCase):
    def test_chain_ring8(self):
        self.assertEqual(CHAIN_POSITION["ring"], 8)
        self.assertEqual(CHAIN_POSITION["name"], "教育域编排")
        self.assertIn("5th", CHAIN_POSITION["same_as_law"])

    def test_emit_seq_monotonic(self):
        bus = LineageBus("edu", "t1")
        a = bus.emit({"m": 1})
        b = bus.emit({"m": 2}, parent=a["seq"])
        self.assertEqual(b["seq"], a["seq"] + 1)   # 严格单调

    def test_orphan_rejected(self):
        bus = LineageBus("edu", "t1")
        r = bus.emit({"m": 1}, parent=99)
        self.assertFalse(r["ok"])

    def test_lineage_chain(self):
        bus = LineageBus("edu", "t1")
        a = bus.emit({"m": 1})
        b = bus.emit({"m": 2}, parent=a["seq"])
        c = bus.emit({"m": 3}, parent=b["seq"])
        r = bus.lineage(c["seq"])
        self.assertEqual(r["chain"], [a["seq"], b["seq"], c["seq"]])

    def test_rubric_grade(self):
        r = SelfEvalRubric.score_round(SCORES)
        self.assertTrue(r["ok"])
        self.assertEqual(r["grade"], "B+")

    def test_rubric_dim_mismatch(self):
        self.assertFalse(SelfEvalRubric.score_round({"bad": 1})["ok"])

    def test_rubric_range_guard(self):
        s = dict(SCORES); s["架构完整性"] = 16
        self.assertFalse(SelfEvalRubric.score_round(s)["ok"])

    def test_progression_true(self):
        r1 = SelfEvalRubric.score_round(SCORES)
        higher = {k: v + 0.5 for k, v in SCORES.items()}
        r2 = SelfEvalRubric.score_round(higher)
        p = SelfEvalRubric.progression([r1, r2])
        self.assertTrue(p["progressive"])

    def test_progression_false_on_regression(self):
        r1 = SelfEvalRubric.score_round(SCORES)
        lower = {k: v - 1 for k, v in SCORES.items()}
        r2 = SelfEvalRubric.score_round(lower)
        self.assertFalse(SelfEvalRubric.progression([r1, r2])["progressive"])

    def test_scan_forbidden_and_missing(self):
        r = RedlineSelfScan.scan({"a.md": "这个必赚"},
                                 required=["诚实边界"])
        self.assertFalse(r["ok"])
        self.assertEqual(r["forbidden_hits"][0]["hit"], "必赚")
        self.assertIn("诚实边界", r["missing_required"])

    def test_scan_report_only_clean(self):
        r = RedlineSelfScan.scan({"a.md": "诚实边界 完整"}, required=["诚实边界"])
        self.assertTrue(r["ok"])

    def test_conductor_end_to_end(self):
        r = EduConductor().conduct(
            "edu", "t1", {"hello": 1}, {"a.md": "诚实边界 完整"},
            ["诚实边界"], SCORES)
        self.assertTrue(r["emitted"]["ok"])
        self.assertTrue(r["scan"]["ok"])
        self.assertEqual(r["rubric"]["grade"], "B+")

    def test_seal_all(self):
        for obj in (LineageBus("o", "t").emit({}),
                    SelfEvalRubric.score_round(SCORES),
                    RedlineSelfScan.scan({}, [])):
            self.assertEqual(obj["seal"], SEAL)


if __name__ == "__main__":
    unittest.main()
