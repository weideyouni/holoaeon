# -*- coding: utf-8 -*-
"""B4 康复域试点 20 例 · 旁挂单测（不并入主套 34 项）。

运行：python -m unittest discover -s tests_contract -v
"""
import csv
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from holoaeon.fusion_upgrade import contract as C  # noqa: E402

PILOT = os.path.join(ROOT, "data", "rehab_pilot_20.json")
LABELS = os.path.join(ROOT, "data", "skill_usage_labels.csv")
INDEX = os.path.join(ROOT, "data", "skill_matrix_index.json")


class RehabPilotTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(PILOT, encoding="utf-8") as f:
            cls.doc = json.load(f)
        cls.cases = cls.doc["cases"]
        with open(LABELS, encoding="utf-8") as f:
            cls.labels = {r["name"]: r["label"] for r in csv.DictReader(f)}
        with open(INDEX, encoding="utf-8") as f:
            cls.idx = {x["name"]: x for x in json.load(f)["skills"]}

    def test_01_twenty_cases_ordered(self):
        self.assertEqual(len(self.cases), 20)
        self.assertEqual([c["case_id"] for c in self.cases], ["RP-%02d" % i for i in range(1, 21)])

    def test_02_all_contracts_valid(self):
        for c in self.cases:
            self.assertTrue(C.validate_v1(c["contract"])["ok"], c["case_id"])

    def test_03_skills_are_executable_M(self):
        for c in self.cases:
            self.assertIn(c["skill"], self.labels)
            self.assertEqual(self.labels[c["skill"]], "M", c["skill"])

    def test_04_mechanism_follows_index(self):
        for c in self.cases:
            self.assertEqual(c["mechanism"], self.idx[c["skill"]]["mechanism"])

    def test_05_medical_cases_carry_redlines(self):
        for c in self.cases:
            if c["payload_domain"] == "medical":
                red = c["contract"]["payload"]["redlines"]
                for k in C.REDLINE_KEYS:
                    self.assertIs(red[k], True)

    def test_06_no_dose_and_budget_int(self):
        for c in self.cases:
            blob = (c["contract"].get("note") or "").lower()
            for m in C.DOSE_MARKERS:
                self.assertNotIn(m, blob)
            self.assertIsInstance(c["contract"]["budget"], int)

    def test_07_negative_probes_all_rejected(self):
        probes = self.doc["negative_probes"]
        self.assertEqual(len(probes), 4)
        for p in probes:
            self.assertTrue(p["rejected"], p["probe_id"])


if __name__ == "__main__":
    unittest.main()
