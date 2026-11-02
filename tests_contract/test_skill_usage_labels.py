# -*- coding: utf-8 -*-
"""B3 用途二次分类单测（旁挂套件，不并入主套 34 项）。

运行：python -m unittest discover -s tests_contract -v
"""
import csv
import hashlib
import io
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "data", "skill_matrix_index.json")
CSV_F = os.path.join(ROOT, "data", "skill_usage_labels.csv")
VERDICT_F = os.path.join(ROOT, "data", "b3_sample_verdicts.json"
                         )
LABELS = ("K", "M", "T", "X", "U")


class UsageLabelsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CSV_F, encoding="utf-8") as f:
            cls.text = f.read()
        cls.rows = list(csv.DictReader(io.StringIO(cls.text)))
        with open(INDEX, encoding="utf-8") as f:
            cls.idx = json.load(f)
        with open(VERDICT_F, encoding="utf-8") as f:
            cls.sample = json.load(f)

    def test_01_row_count_and_order(self):
        self.assertEqual(len(self.rows), 1229)
        self.assertEqual([r["name"] for r in self.rows], [x["name"] for x in self.idx["skills"]])

    def test_02_every_row_has_label(self):
        for r in self.rows:
            self.assertIn(r["label"], LABELS)
            self.assertTrue(r["reason"])

    def test_03_counts_sum_and_undecided_cap(self):
        counts = {k: 0 for k in LABELS}
        for r in self.rows:
            counts[r["label"]] += 1
        self.assertEqual(sum(counts.values()), 1229)
        self.assertLessEqual(counts["U"], 20)

    def test_04_stage_threshold_enforced(self):
        for r in self.rows:
            if r["stage"] == "stage1":
                self.assertGreaterEqual(float(r["score"]), 0.80)
            self.assertIn(r["stage"], ("stage1", "stage2", "stage2-weak", "undecided"))

    def test_05_sample40_agreement(self):
        self.assertEqual(len(self.sample["items"]), 40)
        self.assertGreaterEqual(self.sample["agree"], 36)
        dis = [x for x in self.sample["items"] if x["verdict"] == "disagree"]
        for x in dis:
            self.assertTrue(x["note"])

    def test_06_sample_is_deterministic_stride(self):
        rows = sorted(self.rows, key=lambda r: r["name"])
        n = len(rows)
        expect = [rows[i * n // 40]["name"] for i in range(40)]
        self.assertEqual([x["name"] for x in self.sample["items"]], expect)

    def test_07_csv_digest_matches_verdict_file(self):
        self.assertEqual(hashlib.sha256(self.text.encode("utf-8")).hexdigest(),
                         self.sample["csv_sha256"])


if __name__ == "__main__":
    unittest.main()
