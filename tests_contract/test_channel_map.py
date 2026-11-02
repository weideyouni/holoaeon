# -*- coding: utf-8 -*-
"""B2b 通道映射与词表分域单测（旁挂套件，不并入主套 34 项）。

运行：python -m unittest discover -s tests_contract -v
"""
import hashlib
import json
import os
import unittest

from holoaeon.fusion_upgrade import contract as c

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_F = os.path.join(ROOT, "data", "channel_map.csv")
JSON_F = os.path.join(ROOT, "data", "channel_map.json")
LEX_F = os.path.join(ROOT, "data", "skin_lexicon_rehab.json")


def read_csv(path):
    with open(path, encoding="utf-8") as f:
        lines = [x.rstrip("\n") for x in f if x.strip()]
    header = lines[0].split(",")
    return [dict(zip(header, x.split(","))) for x in lines[1:]]


class ChannelMapTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = read_csv(CSV_F)
        with open(JSON_F, encoding="utf-8") as f:
            cls.meta = json.load(f)
        with open(LEX_F, encoding="utf-8") as f:
            cls.lex = json.load(f)

    def test_01_twelve_rows(self):
        self.assertEqual(len(self.rows), 12)

    def test_02_groups_sum_to_targets(self):
        groups = {}
        for r in self.rows:
            groups[r["group"]] = groups.get(r["group"], 0) + 1
        self.assertEqual(groups, {"气": 5, "血": 4, "神": 3})
        self.assertEqual(self.meta["mapped"], 12)
        self.assertEqual(self.meta["targets"], 17)

    def test_03_pending_registered_not_filled(self):
        self.assertEqual(self.meta["pending"], 5)
        self.assertEqual(self.meta["pending_detail"], {"神": 1, "淋巴": 4})
        self.assertTrue(self.meta["no_arithmetic"])

    def test_04_no_arithmetic_in_sources(self):
        for p in (CSV_F, JSON_F):
            with open(p, encoding="utf-8") as f:
                text = f.read()
            for token in ("idx%17", "idx % 17", "%17"):
                self.assertNotIn(token, text)

    def test_05_same_source_as_contract(self):
        ref = c.channel_map()["rows"]
        self.assertEqual(len(ref), len(self.rows))
        for a, b in zip(ref, self.rows):
            self.assertEqual(a["lc"], b["lc"])
            self.assertEqual(a["group"], b["group"])
            self.assertEqual(a["target_group"], b["target_group"])

    def test_06_general_gate_has_no_medical_rules(self):
        gen = self.lex["tracks"]["general"]
        self.assertEqual(gen["count"], 10)
        self.assertEqual(len(gen["slots"]), 10)
        for s in gen["slots"]:
            self.assertNotIn("E13", s)
            self.assertNotIn("E14", s)
        self.assertFalse(gen["includes_medical"])

    def test_07_medical_split_counts_and_not_copied(self):
        med = self.lex["tracks"]["medical"]
        self.assertEqual(med["e14_count"], 24)
        self.assertEqual(med["e13_count"], 12)
        self.assertFalse(med["copied_into_holoaeon"])

    def test_08_injection_is_domain_gated(self):
        g = self.lex["injection"]["general_gate"]
        m = self.lex["injection"]["medical_gate"]
        self.assertEqual(g["must_not_load"], ["medical"])
        self.assertIn("medical", m["load"])
        self.assertIn("redlines", m["extra_requirement"])

    def test_09_lexicon_digest_recomputable(self):
        core = {k: v for k, v in self.lex.items() if k != "spec_digest"}
        canon = json.dumps(core, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        self.assertEqual(self.lex["spec_digest"],
                         hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16])


if __name__ == "__main__":
    unittest.main()
