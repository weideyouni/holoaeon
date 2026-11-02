"""B9 收口契约单测（旁挂）。只读校验：不生成产物、不联网。

覆盖：收口件在位 / 台账 12 行 / 工时 15.0 / 判据条数与可跑命令 / 风险登记 / 无形容词 /
DNA V1.2 一致 / 排除项包含 B9 清单类产物 / 规格版本 0.9.1 / 校验器整体 PASS。
"""

import importlib.util
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

_spec = importlib.util.spec_from_file_location(
    "verify_b9_closeout", os.path.join(ROOT, "scripts", "verify_b9_closeout.py"))
V9 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V9)

from holoaeon.fusion_upgrade import dual_sync as DS  # noqa: E402


class TestB9Closeout(unittest.TestCase):
    def test_01_docs_present(self):
        ok, detail = V9.check_docs()
        self.assertTrue(ok, detail)

    def test_02_ledger_rows_and_status(self):
        ok, detail = V9.check_ledger()
        self.assertTrue(ok, detail)

    def test_03_hours_total(self):
        ok, detail = V9.check_hours()
        self.assertTrue(ok, detail)

    def test_04_criteria_count_and_commands(self):
        ok, detail = V9.check_criteria()
        self.assertTrue(ok, detail)

    def test_05_risks_registered(self):
        ok, detail = V9.check_risks()
        self.assertTrue(ok, detail)

    def test_06_no_adjective_criteria(self):
        ok, detail = V9.check_no_adjectives()
        self.assertTrue(ok, detail)

    def test_07_dna_v12_consistent(self):
        ok, detail = V9.check_dna()
        self.assertTrue(ok, detail)

    def test_08_sums_excludes_b9_manifest_like(self):
        excluded = set(DS.SUMS_EXCLUDES)
        self.assertEqual(len(excluded), 9)
        for rel in ("data/B9_收口票据.md", "reports/b9_closeout.json",
                    "reports/b9_closeout_check.json", "reports/five_site_manifest.json"):
            self.assertIn(rel, excluded)

    def test_09_spec_version_locked(self):
        ok, detail = V9.check_spec()
        self.assertTrue(ok, detail)

    def test_10_verifier_all_green(self):
        report = V9.run()
        self.assertEqual(report["verdict"], "PASS", json.dumps(report["failed"], ensure_ascii=False))


if __name__ == "__main__":
    unittest.main()
