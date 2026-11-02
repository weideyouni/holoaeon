# -*- coding: utf-8 -*-
"""B2a 六机制映射表单测（旁挂套件，不并入主套 34 项）。

运行：python -m unittest discover -s tests_contract -v
"""
import json
import os
import unittest

from holoaeon.fusion_upgrade import contract as c

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP_FILE = os.path.join(ROOT, "data", "mechanism_map.json")


class MechanismMapTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(MAP_FILE, encoding="utf-8") as f:
            cls.doc = json.load(f)

    def test_01_six_rows_in_order(self):
        self.assertEqual(self.doc["row_count"], 6)
        self.assertEqual([r["mechanism"] for r in self.doc["rows"]], list(c.MECHANISMS))

    def test_02_every_row_has_mapping_rule(self):
        for r in self.doc["rows"]:
            self.assertIsInstance(r["mapping_rule"], str)
            self.assertGreaterEqual(len(r["mapping_rule"].strip()), 6, r["id"])

    def test_03_direction_single_and_one_way(self):
        dirs = {r["direction"] for r in self.doc["rows"]}
        self.assertEqual(len(dirs), 1)
        only = dirs.pop()
        self.assertIn("one-way", only)
        self.assertNotIn("双向", only)
        self.assertNotIn("two-way", only)

    def test_04_digest_recomputable(self):
        import hashlib
        canon = json.dumps(self.doc["rows"], sort_keys=True, separators=(",", ":"),
                           ensure_ascii=False)
        self.assertEqual(self.doc["map_digest"],
                         hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16])

    def test_05_same_and_diff_not_empty(self):
        for r in self.doc["rows"]:
            self.assertTrue(r["same"], r["id"])
            self.assertTrue(r["diff"], r["id"])

    def test_06_no_drift_with_pairs(self):
        for i, p in enumerate(c.PAIRS):
            r = self.doc["rows"][i]
            self.assertEqual(r["mechanism"], p["mechanism"])
            self.assertEqual(r["same"], list(p["same"]))
            self.assertEqual(r["diff"], list(p["diff"]))
            self.assertEqual(r["mapping_rule"], p["bridge"])

    def test_07_map_digest_differs_when_one_row_changes(self):
        import hashlib
        rows = json.loads(json.dumps(self.doc["rows"]))
        rows[0]["mapping_rule"] = rows[0]["mapping_rule"] + "改"
        canon = json.dumps(rows, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        self.assertNotEqual(self.doc["map_digest"],
                            hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16])


if __name__ == "__main__":
    unittest.main()
