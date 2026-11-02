# -*- coding: utf-8 -*-
"""V5.0 旁挂单测：康复域知识库索引与影子维度（不触碰 25/47/9）。"""
import io
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)

KB = os.path.join(ROOT, "data", "v5_rehab_kb.json")


def load(p):
    with io.open(p, encoding="utf-8") as f:
        return json.load(f)


class TestV5RehabKB(unittest.TestCase):
    def setUp(self):
        self.kb = load(KB)

    def test_01_kb_identity(self):
        self.assertEqual(self.kb["id"], "SG-V5-REHAB-KB-V1")
        self.assertEqual(self.kb["batch"], "V5.0-B1")
        self.assertTrue(self.kb["entries"])

    def test_02_lock_untouched(self):
        lock = self.kb["lock"]
        self.assertEqual((lock["agents"], lock["skills"], lock["packs"]), (25, 47, 9))

    def test_03_shadow_not_in_lock(self):
        sd = self.kb["shadow_dimension"]
        self.assertEqual(sd["slot"], "EXT-DIM-02")
        self.assertFalse(sd["participates_in_dimension_lock"])
        self.assertFalse(sd["affects_diff0_hash"])

    def test_04_evidence_tier_unchanged(self):
        er = self.kb["evidence_register"]
        self.assertTrue(er["tier_unchanged"])
        self.assertEqual(len(er["cards"]), 4)
        for c in er["cards"]:
            self.assertEqual(c["tier_before"], "none")
            self.assertEqual(c["tier_after"], "none")

    def test_05_no_original_text_copied(self):
        for e in self.kb["entries"]:
            if e["layer"].startswith("ivsa_"):
                self.assertFalse(e["copied"], e["entry_id"])

    def test_06_ivsa_rows_total(self):
        self.assertEqual(self.kb["totals"]["ivsa_rows"], 300)
        self.assertEqual(self.kb["totals"]["entries"], 14)

    def test_07_redlines_declared(self):
        rl = self.kb["redlines"]
        for key in ("zero_dose", "no_diagnosis", "no_device", "no_original_text"):
            self.assertIn(key, rl)

    def test_08_slots_claimed(self):
        slots = load(os.path.join(ROOT, "data", "extension_slots.json"))
        by = {s["slot_id"]: s for s in slots["slots"]}
        self.assertEqual(by["EXT-DIM-02"]["status"], "occupied")
        self.assertEqual(by["EXT-EVIDENCE-01"]["status"], "occupied")
        self.assertEqual(by["EXT-EVIDENCE-01"]["evidence"], "none")
        self.assertEqual(len(slots["slots"]), 12)

    def test_09_slot_registry_reads_clean(self):
        from holoaeon.fusion_upgrade import slot_registry as sr
        payload = sr.load(ROOT)
        self.assertEqual(sr.validate(payload), [])
        summary = sr.summary(payload)
        self.assertEqual(summary["total"], 12)


if __name__ == "__main__":
    unittest.main()
