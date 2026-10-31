# -*- coding: utf-8 -*-
"""VERAX 诚实契约测试：H1（measured 无来源）、H2（缺字段）、合规路径。"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from holoaeon.audit import Receipt, inspect_receipt, scan_receipts  # noqa: E402


class TestHonesty(unittest.TestCase):
    def test_measured_without_source_is_h1(self):
        problems = inspect_receipt({"evidence_class": "measured"}, "demo")
        self.assertEqual([p["rule"] for p in problems], ["H1"])

    def test_missing_class_is_h2(self):
        problems = inspect_receipt({"task": "x"}, "demo")
        self.assertEqual([p["rule"] for p in problems], ["H2"])

    def test_compliant_measured_receipt(self):
        receipt = Receipt("r1", "path", "measured",
                          measure_source="selftest run 2026-10-31",
                          measure_ts="2026-10-31T00:00:00Z")
        self.assertEqual(receipt.validate(), [])

    def test_simulated_with_source_is_flagged(self):
        receipt = Receipt("r2", "path", "simulated",
                          measure_source="fake source")
        self.assertTrue(receipt.validate())

    def test_scan_counts_both_rules(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "receipts.jsonl")
            with open(path, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(json.dumps({"evidence_class": "measured"}) + "\n")
                handle.write(json.dumps({"task": "x"}) + "\n")
                handle.write(json.dumps({"evidence_class": "simulated"}) + "\n")
            report = scan_receipts(tmp)
        self.assertEqual(report["h1"], 1)
        self.assertEqual(report["h2"], 1)
        self.assertEqual(report["receipts"], 3)
        self.assertFalse(report["clean"])


if __name__ == "__main__":
    unittest.main()
