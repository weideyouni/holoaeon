# -*- coding: utf-8 -*-
"""V21 概念视觉锻造台测试：八步流水线 + --forge 集成。"""
from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holoaeon.concept_anatomy import CONCEPT_MAP  # noqa: E402
from holoaeon import concept_visual_forge as forge_mod  # noqa: E402


class TestTextSearch(unittest.TestCase):
    def test_hit_builtin(self):
        s = forge_mod.text_search("经络")
        self.assertTrue(s["hit"])
        self.assertEqual(len(s["components"]), 8)
        self.assertEqual(s["dimension"], "mechanism")

    def test_miss_offtable(self):
        s = forge_mod.text_search("圆珠笔")
        self.assertFalse(s["hit"])
        self.assertIn("圆珠笔", s["description"])
        self.assertGreaterEqual(len(s["related"]), 0)

    def test_all_builtin_searchable(self):
        for c in CONCEPT_MAP:
            self.assertTrue(forge_mod.text_search(c)["hit"], c)


class TestForgePipeline(unittest.TestCase):
    def test_image_desc_v1(self):
        d = forge_mod.image_desc_v1(forge_mod.text_search("经络"))
        self.assertIn("主体", d)

    def test_system_prompt_gen(self):
        p = forge_mod.system_prompt_gen("主体：测试", "工业蓝图", "爆炸分解", "冷灰蓝")
        self.assertIn("工业蓝图", p)
        self.assertIn("爆炸分解", p)
        self.assertIn("冷灰蓝", p)

    def test_matrix_modify(self):
        mx = forge_mod.matrix_modify("主体：测试")
        self.assertEqual(mx["variant_count"], len(forge_mod.FORGE_MATRIX["style"]))
        self.assertEqual(len(mx["variants"]), mx["variant_count"])
        self.assertIn("工业蓝图", mx["variants"][0])

    def test_optimize_prompt(self):
        op = forge_mod.optimize_prompt("主体：测试")
        self.assertIn("负面", op)
        self.assertIn("确定性", op)
        self.assertIn("只画概念映射表内元素", op)

    def test_stylize_three_tiers(self):
        st = forge_mod.stylize("主体：测试")
        self.assertEqual(set(st.keys()), {"blueprint", "art_direction", "artistic"})
        self.assertIn("工业蓝图制图", st["blueprint"])
        self.assertIn("美术设定集", st["art_direction"])
        self.assertIn("艺术创作", st["artistic"])

    def test_forge_full_pipeline(self):
        r = forge_mod.forge("经络")
        self.assertEqual(r["input"], "经络")
        self.assertTrue(r["step2_text_search"]["hit"])
        self.assertEqual(r["step5_matrix"]["variant_count"], 6)
        for k in ("blueprint", "art_direction", "artistic"):
            self.assertIn(k, r["step7_9_stylized"])

    def test_forge_offtable(self):
        r = forge_mod.forge("圆珠笔")
        self.assertFalse(r["step2_text_search"]["hit"])
        self.assertIn("step6_optimized", r)


class TestForgeCli(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def test_module_main_stdout(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = forge_mod.main(["经络"])
        self.assertEqual(rc, 0)
        d = json.loads(buf.getvalue())
        self.assertTrue(d["step2_text_search"]["hit"])

    def test_concept_anatomy_forge_integration(self):
        r = subprocess.run(
            [sys.executable, "-X", "utf8", "-m", "holoaeon.concept_anatomy",
             "圆珠笔", "--forge"],
            cwd=self.repo, capture_output=True, text=True, encoding="utf-8",
            timeout=60)
        self.assertEqual(r.returncode, 0)
        d = json.loads(r.stdout)
        self.assertIn("step7_9_stylized", d)
        self.assertEqual(d["input"], "圆珠笔")

    def test_forge_json_regression(self):
        """V19/V20 输出路径不破：--forge 不污染 --explain 与 JSON 解剖。"""
        r = subprocess.run(
            [sys.executable, "-X", "utf8", "-m", "holoaeon.concept_anatomy",
             "经络", "--explain"],
            cwd=self.repo, capture_output=True, text=True, encoding="utf-8",
            timeout=60)
        self.assertEqual(r.returncode, 0)
        self.assertIn("一句话", r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
