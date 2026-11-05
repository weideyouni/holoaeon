# -*- coding: utf-8 -*-
"""V34 茶域编排闸门测试。零依赖，确定性断言。"""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holoaeon.tea_gate import (CHAIN_POSITION, CalibratedTriad,
                               EmergencyFuse, EthicalValves,
                               TruthSourceEnvelope, TeaConductor, SEAL)


class TestTeaGate(unittest.TestCase):
    def test_chain_ring6(self):
        self.assertEqual(CHAIN_POSITION["ring"], 6)
        self.assertEqual(CHAIN_POSITION["name"], "茶域编排")

    def test_triad_pass(self):
        r = CalibratedTriad.check(["绿茶", "乌龙"], 0.7)
        self.assertTrue(r["ok"])

    def test_triad_too_few_candidates(self):
        r = CalibratedTriad.check(["绿茶"], 0.7)
        self.assertFalse(r["ok"])
        self.assertIn("候选不足", r["errors"][0])

    def test_triad_confidence_bounds(self):
        self.assertFalse(CalibratedTriad.check(["a", "b"], 1.2)["ok"])
        self.assertFalse(CalibratedTriad.check(["a", "b"], -0.1)["ok"])

    def test_fuse_emergency(self):
        r = EmergencyFuse.check("患者出现喉头水肿怎么办")
        self.assertTrue(r["fused"])
        self.assertIn("就医", r["action"])

    def test_fuse_clean(self):
        self.assertFalse(EmergencyFuse.check("想了解绿茶冲泡")["fused"])

    def test_ethics_endangered_substitute(self):
        r = EthicalValves.check("野生石斛怎么泡")
        self.assertEqual(r["hits"][0]["action"], "substitute_only")

    def test_ethics_no_claim(self):
        r = EthicalValves.check("这茶能根治失眠吗")
        self.assertTrue(any(h["valve"] == "NO_CLAIM" for h in r["hits"]))

    def test_ledger_append_and_verify(self):
        with tempfile.TemporaryDirectory() as d:
            led = TruthSourceEnvelope(os.path.join(d, "src.jsonl"))
            led.append("tea", {"q": 1})
            led.append("tea", {"q": 2})
            r = led.verify_chain()
            self.assertTrue(r["ok"])
            self.assertEqual(r["rows"], 2)

    def test_conductor_fused_first(self):
        r = TeaConductor().conduct("tea", "过敏性休克现场处理")
        self.assertEqual(r["verdict"], "fused_E14")

    def test_conductor_calibrated(self):
        r = TeaConductor().conduct(
            "tea", "推荐两款茶", candidates=["绿茶", "白茶"],
            confidence=0.6)
        self.assertEqual(r["verdict"], "calibrated")
        self.assertIsNotNone(r["ledger_sha"]) if r.get("ledger_sha") else None


if __name__ == "__main__":
    unittest.main()
