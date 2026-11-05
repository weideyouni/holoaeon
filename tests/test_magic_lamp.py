# -*- coding: utf-8 -*-
"""V29 神灯模式测试。零依赖，确定性断言。"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holoaeon.magic_lamp import (GitHubSearchPlanner, LampProposal,
                                 LampWish, MagicLamp, ORG_PATTERNS, SEAL,
                                 SkillAssembler)

FULL_REQ = ["开源吸纳", "状态回传", "基线检查", "乐高拼接", "涌现判定"]


class TestMagicLamp(unittest.TestCase):
    def test_org_patterns_six(self):
        self.assertEqual(len(ORG_PATTERNS), 6)
        self.assertEqual(ORG_PATTERNS[3]["name"], "一过性先行")

    def test_wish_rejects_empty(self):
        self.assertFalse(LampWish.create("", [])["ok"])

    def test_full_coverage_assembly(self):
        w = LampWish.create("整合开源项目", FULL_REQ)
        hits = __import__("holoaeon.magic_lamp", fromlist=["x"]) \
            .KnownSkillIndex.match(w["requirements"])
        asm = SkillAssembler.assemble(w["requirements"], hits)
        self.assertGreaterEqual(asm["coverage"], 0.99)

    def test_gap_triggers_search_plan(self):
        r = MagicLamp().wish("做个图数据库", ["图数据库", "开源吸纳"])
        self.assertEqual(r["proposal"]["state"], "needs_search")
        self.assertIsNotNone(r["search_plan"])
        self.assertFalse(r["search_plan"]["module_network"])

    def test_search_plan_offline(self):
        p = GitHubSearchPlanner.plan(["图数据库"], "gdb")
        self.assertEqual(p["executed_by"], "director_or_doubao(联网侧)")
        self.assertIn("github", p["queries"][0])

    def test_chain_order(self):
        from holoaeon.magic_lamp import LampChainTrigger
        t = LampChainTrigger.trigger({"goal": "g"}, [])
        self.assertEqual(len(t["chain"]), 3)
        self.assertIn("回流", t["order"])

    def test_probe_pass_and_burn(self):
        r = MagicLamp().wish("整合", FULL_REQ)
        self.assertTrue(r["probe"]["probe_ok"])
        self.assertTrue(r["probe"]["burned"])

    def test_probe_fail_blocks(self):
        r = MagicLamp().wish("整合", FULL_REQ, checker=lambda p: False)
        self.assertEqual(r["proposal"]["state"], "test_failed")

    def test_proposal_contains_seal(self):
        r = MagicLamp().wish("整合", FULL_REQ)
        self.assertIn(SEAL, r["proposal"]["text"])

    def test_state_ready_when_full_coverage(self):
        r = MagicLamp().wish("整合", FULL_REQ)
        self.assertEqual(r["proposal"]["state"], "ready_assembled")

    def test_pipeline_nine(self):
        self.assertEqual(len(MagicLamp.PIPELINE), 9)


if __name__ == "__main__":
    unittest.main()
