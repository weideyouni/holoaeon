# -*- coding: utf-8 -*-
"""test_v53_palette_gate —— ring18 色卡层测试（真 unittest）。

覆盖：hex/RGB 工具 + 色卡公理角色分配 + 占比加权张量 + 索引加载/校验/
检索 + 双源诚实边界 + 总闸。依赖 data/cinema_palettes.json（本批交付物）。
"""
from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holoaeon.palette_gate import (  # noqa: E402
    CHAIN_POSITION,
    COLOR_AXIOM,
    SEAL,
    PaletteColor,
    PaletteEntry,
    PaletteGate,
    PaletteIndex,
    PaletteTensor,
    classify_roles,
    fingerprint,
    hex_to_rgb,
    probe,
    rgb_cosine,
    rgb_to_hex,
)
from holoaeon.hypervector import HypervectorSpace  # noqa: E402

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "data", "cinema_palettes.json")


def _sample_palette():
    return PaletteEntry("001", "希区柯克", "黑色悬疑与冷调惊悚", [
        PaletteColor("深夜暗蓝", "#1A2332", 0.36),
        PaletteColor("雾霭钢蓝", "#3D5A6C", 0.19),
        PaletteColor("暗金琥珀", "#8B6914", 0.13),
        PaletteColor("深墨绿", "#2E4A38", 0.12),
        PaletteColor("恐惧猩红", "#C41E3A", 0.09),
        PaletteColor("暖米妆", "#D4C5A9", 0.11),
    ])


# ---------------------------------------------------------------- 工具
class TestColorUtils(unittest.TestCase):
    def test_hex_rgb_roundtrip(self):
        self.assertEqual(hex_to_rgb("#1A2332"), (0x1A, 0x23, 0x32))
        self.assertEqual(rgb_to_hex((26, 35, 50)), "#1A2332")

    def test_hex_invalid_raises(self):
        for bad in ("12345", "#GGHHII", "xyz", "#12345G"):
            with self.assertRaises(ValueError):
                hex_to_rgb(bad)

    def test_rgb_cosine(self):
        self.assertGreater(rgb_cosine((255, 0, 0), (250, 10, 10)), 0.99)
        self.assertLess(rgb_cosine((255, 0, 0), (0, 0, 255)), 0.1)

    def test_rgb_cosine_zero_vector(self):
        self.assertEqual(rgb_cosine((0, 0, 0), (0, 0, 0)), 0.0)


# ---------------------------------------------------------------- 公理
class TestColorAxiom(unittest.TestCase):
    def test_primary_is_largest_share(self):
        roles = classify_roles(_sample_palette().colors)
        self.assertTrue(roles["ok"])
        self.assertEqual(roles["primary"]["name"], "深夜暗蓝")
        self.assertAlmostEqual(roles["primary_share"], 0.36, places=4)

    def test_secondary_one_or_two(self):
        roles = classify_roles(_sample_palette().colors)
        self.assertLessEqual(len(roles["secondary"]), 2)
        self.assertGreaterEqual(len(roles["secondary"]), 1)

    def test_accent_exists(self):
        roles = classify_roles(_sample_palette().colors)
        self.assertIsNotNone(roles["accent"])

    def test_axiom_constants_match_source(self):
        # 素材公理原文：主色 40%+ / 辅色 20-30% / 点缀 5%
        self.assertEqual(COLOR_AXIOM["primary"]["min_share"], 0.30)
        self.assertEqual(COLOR_AXIOM["secondary"]["max_count"], 2)
        self.assertEqual(COLOR_AXIOM["accent"]["max_share"], 0.10)

    def test_empty_raises_not_ok(self):
        self.assertFalse(classify_roles([])["ok"])

    def test_weighted_rgb_primary_dominant(self):
        e = _sample_palette()
        r, g, b = e.weighted_rgb()
        # 深夜暗蓝主导 → 加权色偏暗（亮度低于纯白一半）
        self.assertLess(r + g + b, 382)


# ---------------------------------------------------------------- 张量
class TestPaletteTensor(unittest.TestCase):
    def test_encode_deterministic(self):
        pt = PaletteTensor()
        a = pt.encode_colors(["#1A2332", "#3D5A6C"], [0.6, 0.4])
        b = pt.encode_colors(["#1A2332", "#3D5A6C"], [0.6, 0.4])
        self.assertEqual(a, b)

    def test_encode_dim(self):
        pt = PaletteTensor()
        v = pt.encode_palette(_sample_palette())
        self.assertEqual(len(v), pt.space.dim)

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            PaletteTensor().encode_colors([])
        with self.assertRaises(ValueError):
            PaletteTensor().encode_colors(["#111111"], [0.5, 0.5])

    def test_weight_sensitivity(self):
        # 同色不同权重 → 主导权重偏向单色张量
        pt = PaletteTensor()
        blue = "#1A2332"
        red = "#C41E3A"
        blue_heavy = pt.encode_colors([blue, red], [0.9, 0.1])
        red_heavy = pt.encode_colors([blue, red], [0.1, 0.9])
        mono_blue = pt.encode_colors([blue], [1.0])
        mono_red = pt.encode_colors([red], [1.0])
        self.assertGreater(pt.space.cosine(blue_heavy, mono_blue),
                           pt.space.cosine(red_heavy, mono_blue))
        self.assertGreater(pt.space.cosine(red_heavy, mono_red),
                           pt.space.cosine(blue_heavy, mono_red))

    def test_carrier_is_hypervector_space(self):
        pt = PaletteTensor()
        self.assertIsInstance(pt.space, HypervectorSpace)

    def test_palette_self_sim_is_one(self):
        pt = PaletteTensor()
        e = _sample_palette()
        v = pt.encode_palette(e)
        self.assertGreater(pt.space.cosine(v, v), 0.999)


# ---------------------------------------------------------------- 索引
class TestPaletteIndex(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = PaletteIndex.load(DATA)

    def test_load_full_200(self):
        self.assertEqual(self.index.count(), 200)

    def test_validate_pass(self):
        v = self.index.validate()
        self.assertTrue(v["ok"], v["problems"])

    def test_every_palette_six_colors(self):
        for e in self.index.entries:
            self.assertEqual(len(e.colors), 6, "%s 色数≠6" % e.id)

    def test_shares_normalized(self):
        for e in self.index.entries:
            tot = sum(c.share for c in e.colors)
            self.assertGreaterEqual(tot, 0.90, "%s 占比 %.3f" % (e.id, tot))
            self.assertLessEqual(tot, 1.10, "%s 占比 %.3f" % (e.id, tot))

    def test_hex_all_valid(self):
        for e in self.index.entries:
            for c in e.colors:
                rgb = hex_to_rgb(c.hex)  # 抛错即失败
                self.assertTrue(all(0 <= x <= 255 for x in rgb))

    def test_by_id_001(self):
        e = self.index.by_id("001")
        self.assertIsNotNone(e)
        self.assertEqual(e.name, "希区柯克")
        # 001 属 OCR 零行三态（色名占位"色1"），锚点断言像素主源 hex 保真
        roles = e.roles()
        self.assertEqual(roles["primary"]["hex"].upper(), "#1A2332")
        self.assertGreaterEqual(roles["primary_share"], 0.38)

    def test_by_id_141_ocr_anchor(self):
        # 141 今敏属 OCR 全对齐三态：色名从图内图例 OCR 对齐（樱花粉为主色名）
        e = self.index.by_id("141")
        self.assertIsNotNone(e)
        self.assertEqual(e.name, "今敏")
        roles = e.roles()
        self.assertEqual(roles["primary"]["name"], "樱花粉")
        self.assertEqual(roles["primary"]["hex"].upper(), "#FBE4EA")

    def test_by_id_missing(self):
        self.assertIsNone(self.index.by_id("999"))

    def test_similar_by_hexes_returns_k(self):
        hits = self.index.similar_by_hexes(
            ["#1A2332", "#3D5A6C", "#C41E3A"], [0.5, 0.3, 0.2], k=5)
        self.assertEqual(len(hits), 5)
        self.assertTrue(all(s > 0 for _, s in hits))

    def test_similar_by_palette_self_excluded(self):
        e = self.index.by_id("001")
        hits = self.index.similar_by_palette(e, k=5)
        self.assertTrue(all(h.id != "001" for h, _ in hits))

    def test_load_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            PaletteIndex.load("data/definitely_missing.json")


# ---------------------------------------------------------------- 总闸
class TestPaletteGate(unittest.TestCase):
    def test_self_check_all_green(self):
        sc = PaletteGate(index=PaletteIndex.load(DATA)).self_check()
        self.assertTrue(sc["ok"], sc["checks"])
        for name, c in sc["checks"].items():
            self.assertTrue(c["ok"], "check failed: %s" % name)

    def test_run_manifest_honesty(self):
        m = PaletteGate(index=PaletteIndex.load(DATA)).run()
        self.assertEqual(m["ring"], 18)
        self.assertEqual(m["batch"], "V53")
        h = m["honesty"]
        self.assertFalse(h["neural"])
        self.assertEqual(h["new_dependencies"], 0)
        self.assertIn("双源交叉", h["extraction"])
        self.assertEqual(len(h["not_included"]), 3)

    def test_run_with_query(self):
        m = PaletteGate(index=PaletteIndex.load(DATA)).run(
            query_hexes=["#1A2332", "#3D5A6C"])
        demo = m["artifacts"]["query_demo"]
        self.assertEqual(len(demo["hits"]), 5)

    def test_axiom_in_manifest(self):
        m = PaletteGate(index=PaletteIndex.load(DATA)).run()
        self.assertIn("color_axiom", m)
        self.assertEqual(m["color_axiom"]["primary"]["min_share"], 0.30)

    def test_chain_position(self):
        self.assertEqual(CHAIN_POSITION["ring"], 18)
        self.assertEqual(CHAIN_POSITION["batch"], "V53")
        ups = " ".join(CHAIN_POSITION["upstream"])
        self.assertIn("cinema_gate", ups)
        self.assertIn("hypervector", ups)

    def test_probe_small_sample(self):
        r = probe()
        self.assertTrue(r["ok"])
        self.assertEqual(r["seal"], SEAL)

    def test_fingerprint(self):
        fp = fingerprint()
        self.assertEqual(fp["ring"], 18)
        self.assertEqual(fp["seal"], SEAL)
        self.assertIn("主40%", fp["axiom"])

    def test_empty_index_fails_honestly(self):
        gate = PaletteGate(index=PaletteIndex([]))
        self.assertFalse(gate.self_check()["ok"])


# ---------------------------------------------------------------- 复用锚点
class TestReuseAnchors(unittest.TestCase):
    def test_cinema_gate_upstream_alive(self):
        from holoaeon.cinema_gate import DirectorIndex
        idx = DirectorIndex.load()
        self.assertEqual(idx.count(), 200)

    def test_category_consistency_v52_v53(self):
        # V53 调色板的类目应与 V52 索引一致（同一素材双层）
        from holoaeon.cinema_gate import DirectorIndex
        v52 = {d.id: d.category for d in DirectorIndex.load().directors}
        for e in PaletteIndex.load(DATA).entries:
            self.assertEqual(e.category, v52.get(e.id),
                             "%s 类目与 V52 不一致" % e.id)


if __name__ == "__main__":
    unittest.main(verbosity=2)
