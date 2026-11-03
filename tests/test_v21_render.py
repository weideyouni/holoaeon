# -*- coding: utf-8 -*-
"""V21 图像渲染器测试：4 渲染器 + 加载协议 + --img CLI。"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holoaeon.concept_anatomy import ConceptAnatomizer  # noqa: E402
from holoaeon import concept_anatomy_render as rmod  # noqa: E402


def _anatomy():
    return ConceptAnatomizer().anatomize("经络")


class TestRenderers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = _anatomy()
        cls.tokens = {**rmod.DEFAULT_TOKENS}

    def test_extract(self):
        d = rmod._extract(self.result)
        self.assertEqual(d["concept"], "经络")
        self.assertGreaterEqual(len(d["components"]), 6)

    def test_explosion_svg(self):
        svg = rmod.render_explosion(self.result, self.tokens)
        self.assertTrue(svg.startswith("<svg"))
        self.assertIn("概念爆炸图", svg)
        self.assertIn("成品对照", svg)
        self.assertIn("components:", svg)

    def test_explosion_horizontal(self):
        svg = rmod.render_explosion(self.result, {**self.tokens, "img_axis": "horizontal"})
        self.assertIn("axis: horizontal", svg)

    def test_annotated_svg(self):
        svg = rmod.render_annotated(self.result, self.tokens)
        self.assertIn("横截面标注图", svg)
        self.assertIn("放大细节", svg)

    def test_legend_svg(self):
        svg = rmod.render_legend(self.result, self.tokens)
        self.assertIn("图例", svg)
        self.assertIn("零件清单", svg)
        self.assertIn("机制", svg)

    def test_diagram_svg(self):
        svg = rmod.render_diagram(self.result, self.tokens)
        self.assertIn("概念结构图", svg)
        self.assertIn("isometric", svg)

    def test_palette_switch(self):
        svg = rmod.render(self.result, {**self.tokens, "img_palette": "线稿黑白"})
        self.assertIn("#ffffff", svg)


class TestRenderProtocol(unittest.TestCase):
    def setUp(self):
        self.result = _anatomy()

    def test_registry_populated(self):
        for name in ("explosion", "annotated", "legend", "diagram"):
            self.assertIn(name, rmod.RENDER_REGISTRY)

    def test_load_render_fallback(self):
        fn = rmod.load_render("不存在的风格")
        self.assertIs(fn, rmod.render_diagram)

    def test_register_custom(self):
        rmod.register_render("custom_test", lambda a, t: "<svg>custom</svg>", "t")
        fn = rmod.load_render("custom_test")
        self.assertEqual(fn({}, {}), "<svg>custom</svg>")

    def test_render_protocol_entry(self):
        svg = rmod.render(self.result, {"img_style": "explosion"})
        self.assertIn("概念爆炸图", svg)


class TestRenderCli(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def test_module_main_save(self):
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "pen.svg")
            r = subprocess.run(
                [sys.executable, "-X", "utf8", "-m", "holoaeon.concept_anatomy",
                 "经络", "--img", "explosion", "--save", out],
                cwd=self.repo, capture_output=True, text=True, encoding="utf-8",
                timeout=60)
            self.assertEqual(r.returncode, 0, r.stderr)
            d = json.loads(r.stdout)
            self.assertEqual(d["saved"], out)
            self.assertEqual(d["style"], "explosion")
            self.assertTrue(os.path.isfile(out))
            with open(out, encoding="utf-8") as f:
                head = f.read(60)
            self.assertTrue(head.startswith("<svg"))

    def test_all_styles_cli(self):
        for style in ("explosion", "annotated", "legend", "diagram"):
            r = subprocess.run(
                [sys.executable, "-X", "utf8", "-m", "holoaeon.concept_anatomy_render",
                 "经络", "--style", style],
                cwd=self.repo, capture_output=True, text=True, encoding="utf-8",
                timeout=60)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("<svg", r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
