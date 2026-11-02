# -*- coding: utf-8 -*-
"""V4.1-B2 · 语义技能族 60 → 100 · 旁挂单测（4 项）。"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import expand_semantic as ES  # noqa: E402
from holoaeon.fusion_upgrade.semantic_family import Family  # noqa: E402


class Semantic100Test(unittest.TestCase):
    def setUp(self):
        self.fam = Family.load()

    def test_01_members_100_ten_modules(self):
        self.assertEqual(self.fam.count(), 100)
        self.assertEqual(len(self.fam.modules()), 10)

    def test_02_expanded_labels_are_mk(self):
        bad = [m["skill"] for m in self.fam.members
               if m["status"] == "expanded" and m["label"] not in ("M", "K")]
        self.assertEqual(bad, [])

    def test_03_rebuild_is_deterministic(self):
        spec = os.path.join(ROOT, "data", "semantic_modules_v4.json")
        doc = ES.build(100, spec)
        self.assertEqual([m["skill"] for m in doc["members"]],
                         [m["skill"] for m in self.fam.members])
        self.assertEqual(doc["sha256"], self.fam.doc["sha256"])

    def test_04_bridge_and_coverage(self):
        self.assertLessEqual(len(self.fam.bridge_candidates()), 4)
        cov = self.fam.coverage()
        self.assertTrue(all(c > 0 for c in cov.values()))
        self.assertTrue(self.fam.verify()["ok"])


if __name__ == "__main__":
    unittest.main()
