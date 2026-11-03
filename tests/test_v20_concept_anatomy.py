# -*- coding: utf-8 -*-
"""V20 概念解剖器落地场景版测试：explain() + --explain + __main__ 守卫。"""
from __future__ import annotations

import contextlib
import io
import os
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holoaeon.concept_anatomy import (  # noqa: E402
    CONCEPT_MAP, DIMENSION_CN, ConceptAnatomizer, explain, main)


class TestExplainFunction(unittest.TestCase):
    def test_explain_meridian(self):
        out = explain("经络")
        self.assertIn("一句话", out)
        self.assertIn("机制类概念", out)          # 中文维度
        self.assertIn("topology_resonance.resonance_node", out)
        self.assertIn("由8个零件组成", out)
        self.assertGreater(len(out), 100)

    def test_explain_all_concepts(self):
        for c in CONCEPT_MAP:
            out = explain(c)
            self.assertIn("一句话", out, f"{c} 缺一句话")
            self.assertGreater(len(out), 100, f"{c} 输出太短")
            self.assertIn("怎么验证它在工作", out)

    def test_explain_unknown(self):
        out = explain("不存在概念")
        self.assertIn("不是内置概念", out)
        self.assertIn("可用概念", out)
        self.assertEqual(len(CONCEPT_MAP), 10)

    def test_explain_default_demo(self):
        out = explain()
        self.assertIn("经络", out)                # 默认演示概念

    def test_dimension_cn_covers_all(self):
        for c, e in CONCEPT_MAP.items():
            self.assertIn(e["dimension"], DIMENSION_CN,
                          f"{c} 维度 {e['dimension']} 缺中文名")


class TestCliExplain(unittest.TestCase):
    def test_main_explain_flag(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = main(["--explain", "经络"])
        self.assertEqual(rc, 0)
        self.assertIn("一句话", buf.getvalue())
        self.assertNotIn('"status"', buf.getvalue())   # 文字模式非 JSON

    def test_main_explain_no_concept_defaults(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = main(["--explain"])
        self.assertEqual(rc, 0)
        self.assertIn("经络", buf.getvalue())

    def test_main_no_args_lists_concepts(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = main([])
        self.assertEqual(rc, 0)
        self.assertIn("available_concepts", buf.getvalue())

    def test_main_concept_json_regression(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = main(["经络"])
        self.assertEqual(rc, 0)
        self.assertIn('"status": "DONE"', buf.getvalue())


class TestMainGuardCli(unittest.TestCase):
    """V19 已知点修复验证：python -m holoaeon.concept_anatomy 现在有输出（__main__ 守卫）。"""

    @classmethod
    def setUpClass(cls):
        cls.repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def _run(self, *args):
        return subprocess.run(
            [sys.executable, "-X", "utf8", "-m", "holoaeon.concept_anatomy", *args],
            cwd=self.repo, capture_output=True, text=True, encoding="utf-8",
            timeout=60)

    def test_module_run_explain_has_output(self):
        r = self._run("经络", "--explain")
        self.assertEqual(r.returncode, 0)
        self.assertIn("一句话", r.stdout)          # 修复前为空

    def test_module_run_plain_has_output(self):
        r = self._run("经络")
        self.assertEqual(r.returncode, 0)
        self.assertIn('"status": "DONE"', r.stdout)

    def test_module_run_no_args_has_output(self):
        r = self._run()
        self.assertEqual(r.returncode, 0)
        self.assertIn("available_concepts", r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
