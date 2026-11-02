# -*- coding: utf-8 -*-
"""B5 · 语义技能族 60 条 · 旁挂单测（不并入主套 34 项）。

运行：python -m unittest discover -s tests_contract -v
"""
import hashlib
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from holoaeon.fusion_upgrade.semantic_family import Family  # noqa: E402

FAMILY = os.path.join(ROOT, "data", "semantic_family.json")
SPEC = os.path.join(ROOT, "data", "semantic_modules.json")
INDEX = os.path.join(ROOT, "data", "skill_matrix_index.json")


class SemanticFamilyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(FAMILY, encoding="utf-8") as f:
            cls.doc = json.load(f)
        with open(SPEC, encoding="utf-8") as f:
            cls.spec = json.load(f)
        with open(INDEX, encoding="utf-8") as f:
            cls.idx = json.load(f)["skills"]
        cls.members = cls.doc["members"]
        cls.module_names = [m["name"] for m in cls.spec["modules"]]
        cls.fam = Family.load()

    def test_01_at_least_sixty_members(self):
        self.assertGreaterEqual(len(self.members), 60)

    def test_02_exactly_ten_modules(self):
        self.assertEqual(len(self.doc["modules"]), 10)
        self.assertEqual([m["name"] for m in self.doc["modules"]], self.module_names)

    def test_03_every_module_covered(self):
        counts = self.fam.coverage()
        self.assertEqual(len(counts), 10)
        for name, c in counts.items():
            self.assertGreater(c, 0, name)

    def test_04_no_eleventh_module(self):
        for m in self.members:
            self.assertIn(m["module"], self.module_names)

    def test_05_base_matches_index(self):
        index_base = {s["name"] for s in self.idx if s.get("mechanism") == "semantic_bus"}
        fam_base = {m["skill"] for m in self.members if m["status"] == "base_index"}
        self.assertEqual(index_base, fam_base)

    def test_06_expansion_is_executable_or_knowledge(self):
        for m in self.members:
            if m["status"] == "expanded":
                self.assertIn(m["label"], ("M", "K"), m["skill"])

    def test_07_no_duplicate_members(self):
        names = [m["skill"] for m in self.members]
        self.assertEqual(len(names), len(set(names)))

    def test_08_digest_recomputable(self):
        body = json.dumps({"members": self.members, "sha256": ""},
                          ensure_ascii=False, sort_keys=True)
        self.assertEqual(hashlib.sha256(body.encode("utf-8")).hexdigest(),
                         self.doc["sha256"])

    def test_09_bridge_candidates_bounded(self):
        bridge = self.doc["bridge_candidates"]
        self.assertLessEqual(len(bridge), 4)
        names = {m["skill"] for m in self.members}
        for b in bridge:
            self.assertIn(b["target_mechanism"], ("semantic_bus", "meridian"))
            self.assertNotIn(b["skill"], names)

    def test_10_route_is_deterministic(self):
        a = self.fam.route("向量嵌入与指纹去重")
        b = self.fam.route("向量嵌入与指纹去重")
        self.assertEqual(a, b)
        self.assertTrue(a)
        self.assertEqual(self.fam.route(""), [self.spec["default_module"]])


if __name__ == "__main__":
    unittest.main()
