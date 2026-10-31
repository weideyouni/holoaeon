# -*- coding: utf-8 -*-
"""V2 / W7 篡改自检：单点改一个字，ReproHash 必变。

守护"确定性"不是空话：如果哈希对内容不敏感，DIFF=0 就只是两次跑同一个错误。
"""
from __future__ import annotations

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from holoaeon.audit import load_golden, run_task  # noqa: E402
from holoaeon.audit.mutation import (DEFAULT_N, SEED_DEFAULT,  # noqa: E402
                                     apply_mutation, leaf_paths,
                                     mutate_selftest, path_text)


def _receipt():
    golden = load_golden("word_count")
    return run_task(golden["task"], args=golden.get("args"), to=golden.get("to"))


class TestMutationSelftest(unittest.TestCase):
    def test_mutation_selftest_five_points_all_change(self):
        res = mutate_selftest(_receipt(), n=DEFAULT_N)
        self.assertEqual(res["mutations"], DEFAULT_N)
        self.assertEqual(res["changed"], DEFAULT_N)
        self.assertTrue(res["sensitive"])

    def test_mutation_selftest_single_path_changes_hash(self):
        receipt = _receipt()
        paths = leaf_paths(receipt)
        self.assertTrue(paths)
        res = mutate_selftest(receipt, n=1)
        self.assertEqual(res["changed"], 1)
        self.assertNotEqual(res["details"][0]["golden"],
                            res["details"][0]["observed"])
        self.assertTrue(res["details"][0]["path"].startswith("$"))
        self.assertIn(res["details"][0]["path"],
                      [path_text(p) for p in paths])

    def test_mutation_selftest_is_deterministic(self):
        receipt = _receipt()
        a = mutate_selftest(receipt, n=DEFAULT_N, seed=SEED_DEFAULT)
        b = mutate_selftest(receipt, n=DEFAULT_N, seed=SEED_DEFAULT)
        self.assertEqual([d["path"] for d in a["details"]],
                         [d["path"] for d in b["details"]])
        self.assertEqual([d["observed"] for d in a["details"]],
                         [d["observed"] for d in b["details"]])

    def test_mutation_does_not_touch_original(self):
        receipt = _receipt()
        before = repr(receipt)
        res = mutate_selftest(receipt, n=DEFAULT_N)
        self.assertTrue(res["changed"] >= 1)
        self.assertEqual(before, repr(receipt))

    def test_zero_mutations_is_not_sensitive(self):
        """空转保护：一条都不改时不许返回 sensitive=True。"""
        res = mutate_selftest(_receipt(), n=0)
        self.assertEqual(res["mutations"], 0)
        self.assertEqual(res["changed"], 0)
        self.assertFalse(res["sensitive"])


if __name__ == "__main__":
    unittest.main()
