# -*- coding: utf-8 -*-
"""V4.2-B1 · 三场卡电场补齐 · 旁挂单测（5 项）。"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from holoaeon.fusion_upgrade.three_field import ThreeField  # noqa: E402


class ThreeFieldTest(unittest.TestCase):
    def setUp(self):
        self.tf = ThreeField.load()

    def test_01_field_and_card_counts(self):
        self.assertEqual(self.tf.fields(), ["magnetic", "electric", "liquid"])
        self.assertEqual(self.tf.counts(), {"magnetic": 5, "electric": 3, "liquid": 5})
        self.assertEqual(len(self.tf.cards), 13)

    def test_02_electric_all_structured_gaps(self):
        for card in self.tf.cards_of("electric"):
            self.assertEqual(card["status"], "gap_structured")
            self.assertEqual(card["evidence_tier"], "none")
            self.assertTrue(card["parameter_frame"])
            self.assertGreaterEqual(len(card["retrieval_plan"]["keywords"]), 3)
            self.assertEqual(card["retrieval_plan"]["decision"], "none")

    def test_03_dose_and_efficacy_blocked(self):
        self.assertTrue(self.tf.guard("每次 3 mg，疗程四周")["blocked"])
        self.assertIn("dose_value", self.tf.guard("每次 3 mg")["reasons"])
        self.assertIn("efficacy_claim", self.tf.guard("有效率 90%，可治愈")["reasons"])
        self.assertFalse(self.tf.guard("磁场卡有哪些模态")["blocked"])

    def test_04_describe_has_no_conclusion(self):
        d = self.tf.describe("TF-E-01")
        self.assertEqual(d["evidence_tier"], "none")
        self.assertIn("none", d["decision"])
        self.assertTrue(d["retrieval_plan"])

    def test_05_verify_ok(self):
        v = self.tf.verify()
        self.assertTrue(v["ok"])
        self.assertEqual(v["fields"], 3)
        self.assertEqual(v["cards"], 13)


if __name__ == "__main__":
    unittest.main()
