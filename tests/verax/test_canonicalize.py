# -*- coding: utf-8 -*-
"""VERAX 规范化测试：物理量剔除、列表稳定排序、未登记字段告警。"""
from __future__ import annotations

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from holoaeon.audit import (canonicalize, canonicalize_report, canonical_json,
                            reprohash)  # noqa: E402


class TestCanonicalize(unittest.TestCase):
    def test_physical_only_diff_same_hash(self):
        a = {"status": "ok", "matched": "word_count", "ts": 1.5,
             "output": {"total_chars": 31}}
        b = {"status": "ok", "matched": "word_count", "ts": 9.9,
             "output": {"total_chars": 31}}
        self.assertEqual(reprohash(a), reprohash(b))

    def test_list_order_independent(self):
        a = {"results": [{"agent_id": "b", "status": "ok"},
                         {"agent_id": "a", "status": "ok"}]}
        b = {"results": [{"agent_id": "a", "status": "ok"},
                         {"agent_id": "b", "status": "ok"}]}
        self.assertEqual(reprohash(a), reprohash(b))

    def test_unknown_field_counted_not_silent(self):
        canon, unknown = canonicalize_report({"status": "ok", "mystery": 1})
        self.assertNotIn("mystery", canon)
        self.assertIn("$.mystery", unknown)

    def test_canonical_text_stable(self):
        obj = {"status": "ok", "task": {"skill": None}, "targets": [2, 3]}
        self.assertEqual(canonical_json(canonicalize(obj)),
                         '{"status": "ok", "targets": [2, 3], "task": {"skill": null}}')


if __name__ == "__main__":
    unittest.main()
