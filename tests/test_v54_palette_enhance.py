# -*- coding: utf-8 -*-
"""V54 测试：底部辅助色块行 + 指纹 bundle sha256 版本 + 跨类目检索权重。

六组真 unittest（V50 纪律：不用 print 断言，不 mock 网络零依赖件）：
  组1 TestAuxData          辅助色数据（200/三态/浅色块 OCR 补）
  组2 TestPaletteTensorV2  辅助色张量（V53 兼容/低权重参与/主带主导不破）
  组3 TestVersionFinger    版本指纹轴（确定性/异版本可分/自洽）
  组4 TestCategoryWeight   跨类目检索权重（cw=1 回归一致/0 纯风格/2 类目 boost）
  组5 TestCompatRegression V52/V53 套件兼容回归 + 主色名修正生效
  组6 TestGateV2           V54 总闸（aux/version 检查/manifest 三主题）

运行：cd .tmp_v54 && python -m unittest tests.test_v54_palette_enhance -v
"""
import io
import json
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holoaeon.cinema_gate import (  # noqa: E402
    DIRECTOR_CATEGORIES, DirectorIndex, StyleTensor)
from holoaeon.palette_gate import (  # noqa: E402
    AUX_WEIGHT, PaletteColor, PaletteEntry, PaletteGate,
    PaletteGateV2, PaletteIndex, PaletteIndexV2, PaletteTensor,
    PaletteTensorV2, _file_sha16, aux_by_id, aux_relation_stats,
    encode_aux, load_aux, version_report)

DATA_MAIN = os.path.join("data", "cinema_palettes.json")
DATA_AUX = os.path.join("data", "cinema_palette_aux.json")


def _hex_dist(h1, h2):
    a = [int(h1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(h2[i:i + 2], 16) for i in (1, 3, 5)]
    return sum(abs(x - y) for x, y in zip(a, b))


class TestAuxData(unittest.TestCase):
    """组1：辅助色块行数据。"""

    def test_aux_load_200(self):
        aux = load_aux()
        self.assertEqual(len(aux), 200)
        self.assertEqual(aux[0].id, "001")

    def test_aux_stats_sum(self):
        stats = aux_relation_stats(load_aux())
        self.assertEqual(sum(stats.values()), 200)
        self.assertEqual(stats["missing"], 0)
        self.assertEqual(stats["duplicate_of_main"], 121)
        self.assertEqual(stats["supplementary"], 62)

    def test_aux_001_supplementary(self):
        e = aux_by_id(load_aux(), "001")
        self.assertEqual(e.relation, "supplementary")
        self.assertEqual(len(e.colors), 4)
        # 像素源（001 OCR 无辅助行文字），视觉参照 ±12 RGB
        refs = ["#7B241C", "#F7DC6F", "#283747", "#F8B195"]
        for c, r in zip(e.colors, refs):
            self.assertLessEqual(_hex_dist(c["hex"], r), 36)  # 3×12 容差

    def test_aux_141_duplicate(self):
        e = aux_by_id(load_aux(), "141")
        self.assertEqual(e.relation, "duplicate_of_main")
        names = [c["name"] for c in e.colors]
        self.assertIn("欲望痴迷", names)
        self.assertTrue(all(c["source"].startswith("ocr") for c in e.colors))

    def test_aux_062_light_color_ocr(self):
        # 062 神圣与纯洁 #F0EDE6 与米色背景 RGB 距离≈4，像素不可分 → OCR 补
        e = aux_by_id(load_aux(), "062")
        self.assertEqual(e.relation, "mixed")
        target = [c for c in e.colors if c["name"] == "神圣与纯洁"]
        self.assertTrue(target)
        self.assertEqual(target[0]["source"], "ocr")
        self.assertLessEqual(_hex_dist(target[0]["hex"], "#F0EDE6"), 24)

    def test_aux_source_values(self):
        for e in load_aux():
            for c in e.colors:
                self.assertIn(c["source"], ("ocr", "pixel", "ocr+pixel"))


class TestPaletteTensorV2(unittest.TestCase):
    """组2：辅助色入张量（低权重）。"""

    @classmethod
    def setUpClass(cls):
        cls.aux = load_aux()
        cls.idx = PaletteIndex.load()
        cls.t53 = PaletteTensor()
        cls.t54 = PaletteTensorV2(aux_entries=cls.aux)

    def test_v53_weight_zero_equivalent(self):
        # aux_weight=0 → 纯 V53 行为（增强不破坏既有语义）
        e = self.idx.by_id("001")
        v53 = self.t53.encode_palette(e)
        t0 = PaletteTensorV2(aux_entries=self.aux)
        t0.AUX_WEIGHT = 0
        v0 = t0.encode_palette(e)
        self.assertEqual([round(x, 6) for x in v53],
                         [round(x, 6) for x in v0])

    def test_aux_changes_vector(self):
        e = self.idx.by_id("001")
        v53 = self.t53.encode_palette(e)
        v54 = self.t54.encode_palette(e)
        cos = self.t54.space.cosine(v53, v54)
        self.assertGreater(cos, 0.9)      # 低权重 → 高相似
        self.assertLess(cos, 0.9999)      # 但确实参与（非恒等）

    def test_aux_deterministic(self):
        e = self.idx.by_id("141")
        a = self.t54.encode_palette(e)
        b = self.t54.encode_palette(e)
        self.assertEqual([round(x, 9) for x in a], [round(x, 9) for x in b])

    def test_main_dominance_kept(self):
        # 含 aux 的全板张量仍满足 V53 主导断言（0.5-0.999）
        e = self.idx.by_id("001")
        ranked = sorted(e.colors, key=lambda c: -c.share)
        mono = self.t54.encode_colors([ranked[0].hex], [1.0])
        full = self.t54.encode_palette(e)
        cos = self.t54.space.cosine(full, mono)
        self.assertGreater(cos, 0.5)
        self.assertLess(cos, 0.999)

    def test_encode_aux_weight_zero(self):
        out = encode_aux(self.t54, ["#1A2332"], 0.0)
        self.assertEqual(max(abs(x) for x in out), 0.0)


class TestVersionFinger(unittest.TestCase):
    """组3：指纹 bundle sha256 版本轴。"""

    @classmethod
    def setUpClass(cls):
        cls.idx = PaletteIndexV2.load()

    def test_version_vector_deterministic(self):
        a = self.idx.tensor.version_vector("ab" * 16)
        b = self.idx.tensor.version_vector("ab" * 16)
        self.assertEqual([round(x, 9) for x in a], [round(x, 9) for x in b])

    def test_version_diff_shapes(self):
        v1 = self.idx.tensor.version_vector("ab" * 16)
        v2 = self.idx.tensor.version_vector("cd" * 16)
        cos = self.idx.tensor.space.cosine(v1, v2)
        self.assertLess(cos, 0.5)         # 异版本可分（近似正交）

    def test_check_version_self(self):
        sig = self.idx.data_sha16
        vv = self.idx.tensor.version_vector(sig)
        self.assertAlmostEqual(
            self.idx.tensor.check_version(sig, vv), 1.0, places=4)

    def test_check_version_foreign(self):
        q = self.idx.tensor.version_vector("ff" * 16)
        s = self.idx.tensor.check_version(self.idx.data_sha16, q)
        self.assertLess(s, 0.5)           # 异版本对账失败

    def test_file_sha16_stable(self):
        self.assertEqual(_file_sha16(DATA_MAIN), _file_sha16(DATA_MAIN))
        h = io.open(DATA_MAIN, "rb").read()
        import hashlib
        self.assertEqual(_file_sha16(DATA_MAIN),
                        hashlib.sha256(h).hexdigest()[:16])

    def test_version_report_cli(self):
        rep = version_report()
        self.assertTrue(rep["ok"])
        self.assertEqual(rep["main_sha16"], self.idx.data_sha16)
        self.assertTrue(rep["aux_sha16"])


class TestCategoryWeight(unittest.TestCase):
    """组4：跨类目检索权重（cinema_gate 增强）。"""

    @classmethod
    def setUpClass(cls):
        cls.idx = DirectorIndex.load()
        cls.st = StyleTensor(cls.idx)
        cls.cat = DIRECTOR_CATEGORIES[0] if DIRECTOR_CATEGORIES else ""

    def test_cat_weight_1_regression(self):
        # V52 兼容红线：cw=1.0 与不带参数完全一致
        text = "霓虹 暗夜 城市"
        a = self.st.similar_by_text(text, self.cat, k=8)
        b = self.st.similar_by_text(text, self.cat, k=8, cat_weight=1.0)
        self.assertEqual([d.id for d, _ in a], [d.id for d, _ in b])
        self.assertEqual([round(s, 6) for _, s in a],
                         [round(s, 6) for _, s in b])

    def test_cat_weight_0_pure_style(self):
        # cw=0 + 给 category == 不给 category（纯风格轴）
        text = "霓虹 暗夜 城市"
        a = self.st.similar_by_text(text, self.cat, k=8, cat_weight=0.0)
        b = self.st.similar_by_text(text, "", k=8)
        self.assertEqual([d.id for d, _ in a], [d.id for d, _ in b])

    def test_cat_weight_boost_same_category(self):
        # 类目 boost 单调性：cw=2 的同类别命中率 > cw=0.5
        text = "霓虹 暗夜 城市 赛博"
        low = self.st.similar_by_text(text, self.cat, k=10, cat_weight=0.5)
        high = self.st.similar_by_text(text, self.cat, k=10, cat_weight=2.0)
        n_low = sum(1 for d, _ in low if d.category == self.cat)
        n_high = sum(1 for d, _ in high if d.category == self.cat)
        self.assertGreaterEqual(n_high, n_low)
        self.assertGreater(n_high, 0)

    def test_by_director_weight_regression(self):
        d = self.idx.by_id("001") or self.idx.directors[0]
        a = self.st.similar_by_director(d, k=5)
        b = self.st.similar_by_director(d, k=5, cat_weight=1.0)
        self.assertEqual([x.id for x, _ in a], [x.id for x, _ in b])

    def test_by_director_zero_explores(self):
        d = self.idx.directors[0]
        a = self.st.similar_by_director(d, k=5)
        b = self.st.similar_by_director(d, k=5, cat_weight=0.0)
        # 跨类目探索：cw=0 时 Top 命中应引入异类别（或至少分数序列不同）
        if a and b:
            same_a = sum(1 for x, _ in a if x.category == d.category)
            same_b = sum(1 for x, _ in b if x.category == d.category)
            self.assertLessEqual(same_b, same_a)

    def test_category_hit_rate(self):
        self.assertEqual(self.st.category_hit_rate([], "x"), 0.0)
        hits = self.st.similar_by_text("霓虹 城市", k=5)
        rate = self.st.category_hit_rate(hits, "")
        self.assertEqual(rate, 0.0)

    def test_encode_query_weighted_math(self):
        # 数学结构：cw=0 且有 category == bundle(纯 toks)
        import math as _m
        q0 = self.st.encode_query("霓虹 城市", "whatever", 0.0)
        toks = []
        from holoaeon.semvec import tokenize
        for t in tokenize("霓虹 城市"):
            toks.append(self.st.space.make("tok:" + t))
        ref = self.st.space.bundle(toks)
        self.assertEqual([round(x, 6) for x in q0],
                         [round(x, 6) for x in ref])


class TestCompatRegression(unittest.TestCase):
    """组5：V52/V53 套件兼容回归 + 主色名修正生效。"""

    def test_v52_suite_on_enhanced_module(self):
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName("tests.test_v52_cinema_gate")
        res = unittest.TextTestRunner(verbosity=0).run(suite)
        self.assertEqual(len(res.failures) + len(res.errors), 0)

    def test_v53_suite_on_v2_data(self):
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName("tests.test_v53_palette_gate")
        res = unittest.TextTestRunner(verbosity=0).run(suite)
        self.assertEqual(len(res.failures) + len(res.errors), 0)

    def test_data_v2_name_coverage_up(self):
        doc = json.load(io.open(DATA_MAIN, encoding="utf-8"))
        named = sum(1 for p in doc["palettes"] for c in p["colors"]
                    if not c["name"].startswith("色"))
        self.assertGreater(named, 700)   # v1=591 → v2=869（修正生效）

    def test_001_names_fixed(self):
        doc = json.load(io.open(DATA_MAIN, encoding="utf-8"))
        e = next(p for p in doc["palettes"] if p["id"] == "001")
        self.assertEqual(e["colors"][0]["name"], "深夜暗蓝")
        self.assertFalse(any(c["name"].startswith("色")
                             for c in e["colors"]))

    def test_062_names_fixed(self):
        doc = json.load(io.open(DATA_MAIN, encoding="utf-8"))
        e = next(p for p in doc["palettes"] if p["id"] == "062")
        self.assertFalse(any(c["name"].startswith("色")
                             for c in e["colors"]))


class TestGateV2(unittest.TestCase):
    """组6：V54 总闸。"""

    def test_gate_v2_self_check(self):
        g = PaletteGateV2()
        sc = g.self_check()
        self.assertTrue(sc["ok"])
        self.assertIn("aux", sc["checks"])
        self.assertIn("version", sc["checks"])
        self.assertTrue(sc["checks"]["aux"]["ok"])
        self.assertTrue(sc["checks"]["version"]["ok"])

    def test_gate_v2_run_manifest(self):
        m = PaletteGateV2().run()
        self.assertEqual(m["batch"], "V54")
        self.assertIn("aux", m["v54_themes"])
        self.assertIn("version", m["v54_themes"])
        self.assertIn("name_fix", m["v54_themes"])
        self.assertEqual(m["honesty"]["aux_weight"], AUX_WEIGHT)

    def test_gate_v2_query_demo(self):
        m = PaletteGateV2().run(query_hexes=["#1A2332", "#C31F3A"])
        hits = m["artifacts"]["query_demo"]["hits"]
        self.assertEqual(hits[0]["id"], "001")
        self.assertGreater(hits[0]["score"], 0.4)

    def test_gate_v1_still_works(self):
        # V53 总闸（PaletteGate）在 v2 数据上仍可用（数据字段兼容）
        g = PaletteGate()
        self.assertEqual(g.index.count(), 200)


if __name__ == "__main__":
    unittest.main()
