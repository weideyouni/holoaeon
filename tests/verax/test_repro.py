# -*- coding: utf-8 -*-
"""VERAX 复现测试：黄金回归值、篡改必红、差异表为空。"""
from __future__ import annotations

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from holoaeon.audit import load_golden, verify  # noqa: E402

GOLDEN_HASH = "2b82a6ef7188ce91"


class TestRepro(unittest.TestCase):
    def test_word_count_is_stable_and_matches_golden(self):
        golden = load_golden("word_count")
        self.assertIsNotNone(golden)
        verdict = verify("word_count", golden["task"], golden.get("args"),
                         golden.get("to"), n=2, golden=golden)
        self.assertTrue(verdict["repro_hash_stable"])
        self.assertTrue(verdict["golden_match"])
        self.assertEqual(verdict["reprohash_list"], [GOLDEN_HASH, GOLDEN_HASH])
        self.assertEqual(verdict["diff_reprocore"], {})

    def test_physical_diffs_are_recorded_but_not_judged(self):
        golden = load_golden("word_count")
        verdict = verify("word_count", golden["task"], n=2, golden=golden)
        self.assertTrue(verdict["diff_physical"])
        self.assertTrue(verdict["repro_hash_stable"])

    def test_tampered_golden_turns_red(self):
        golden = dict(load_golden("word_count"))
        golden["expected_reprohash"] = "0000000000000000"
        verdict = verify("word_count", golden["task"], n=2, golden=golden)
        self.assertFalse(verdict["golden_match"])
        self.assertTrue(verdict["repro_hash_stable"])


if __name__ == "__main__":
    unittest.main()
