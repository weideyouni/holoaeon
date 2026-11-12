# -*- coding: utf-8 -*-
"""test_v52_cinema_gate —— ring18 影像域测试（真 unittest）。

覆盖：索引加载/校验/查询 + 风格张量（编码/自检索/负对照/跨类区分）+
指针纪律 + 总闸诚实边界。依赖 data/cinema_directors.json（本批交付物）。
"""
from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holoaeon.cinema_gate import (  # noqa: E402
    ASSET_POINTERS,
    CHAIN_POSITION,
    DIRECTOR_CATEGORIES,
    SEAL,
    CinemaGate,
    DirectorEntry,
    DirectorIndex,
    StyleTensor,
    fingerprint,
    probe,
)
from holoaeon.semvec import tokenize  # noqa: E402
from holoaeon.hypervector import HypervectorSpace  # noqa: E402

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "data", "cinema_directors.json")


def _sample_entry(did="001", name="希区柯克",
                  cat=DIRECTOR_CATEGORIES[0],
                  style="优雅中性色被翠绿和警示红刺破",
                  works="迷魂记、后窗、惊魂记",
                  tags=("精致构图", "互补色对比", "悬疑阴影")):
    return DirectorEntry(did, name, cat, style, works, list(tags))


# ---------------------------------------------------------------- 索引层
class TestDirectorIndex(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = DirectorIndex.load(DATA)

    def test_load_full_200(self):
        self.assertEqual(self.index.count(), 200)
        self.assertEqual(len(self.index.categories()), 10)

    def test_validate_pass(self):
        v = self.index.validate()
        self.assertTrue(v["ok"], v["problems"])

    def test_categories_uniform_20(self):
        stat = self.index.categories()
        self.assertTrue(all(c == 20 for c in stat.values()), stat)

    def test_by_id_lookup(self):
        d = self.index.by_id("141")
        self.assertIsNotNone(d)
        self.assertEqual(d.name, "今敏")
        self.assertEqual(d.category, "动画奇幻与异想视觉")

    def test_by_id_missing_returns_none(self):
        self.assertIsNone(self.index.by_id("999"))

    def test_by_name_lookup(self):
        hits = self.index.by_name("今敏")
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0].id, "141")

    def test_by_category_20(self):
        for cat in DIRECTOR_CATEGORIES:
            self.assertEqual(len(self.index.by_category(cat)), 20, cat)

    def test_category_table_matches_data(self):
        # 十大类声明层与数据层一致（不臆造类目）
        self.assertEqual(set(self.index.categories()),
                         set(DIRECTOR_CATEGORIES))

    def test_load_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            DirectorIndex.load("data/definitely_missing.json")

    def test_first_and_last_entries(self):
        first = self.index.by_id("001")
        last = self.index.by_id("200")
        self.assertEqual(first.name, "希区柯克")
        self.assertEqual(last.name, "克莱尔·德尼")
        self.assertEqual(last.category, "东方美学与留白意境")

    def test_from_list_independent_of_file(self):
        idx = DirectorIndex.from_list([_sample_entry()])
        self.assertEqual(idx.count(), 1)


# ---------------------------------------------------------------- 张量层
class TestStyleTensor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = DirectorIndex.load(DATA)
        cls.st = StyleTensor(cls.index)

    def test_encode_deterministic(self):
        d = self.index.by_id("001")
        a = self.st.encode_entry(d)
        b = self.st.encode_entry(d)
        self.assertEqual(a, b)

    def test_encode_dim_matches_space(self):
        d = self.index.by_id("001")
        self.assertEqual(len(self.st.encode_entry(d)), self.st.space.dim)

    def test_self_retrieval_top1(self):
        for sid in ("001", "050", "100", "141", "200"):
            d = self.index.by_id(sid)
            top = self.st.similar_by_director(d, k=3)
            self.assertEqual(top[0][0].id, sid, "self-retrieval miss %s" % sid)

    def test_negative_control_low_score(self):
        # 家具说明书式无关文本：负对照不应高于自检索分数
        d = self.index.by_id("006")  # 雷弗恩：霓虹
        pos = self.st.similar_by_director(d, k=1)[0][1]
        neg = self.st.similar_by_text("操作系统数据库网络协议审计台账", k=1)
        self.assertGreater(pos, neg[0][1])

    def test_text_query_hits_same_category(self):
        hits = self.st.similar_by_text("霓虹冷蓝 暗夜城市 风格化暴力",
                                       category="霓虹黑色与赛博未来", k=3)
        same = sum(1 for d, _ in hits if d.category == "霓虹黑色与赛博未来")
        self.assertGreaterEqual(same, 2)

    def test_category_axis_dominates_cross_class(self):
        # 同类导演相似度应高于异类（类轴权重大）
        a = self.index.by_id("001")   # 黑色悬疑
        b = self.index.by_id("002")   # 黑色悬疑（大卫·芬奇）
        c = self.index.by_id("141")   # 动画奇幻（今敏）
        va = self.st.encode_entry(a)
        vb = self.st.encode_entry(b)
        vc = self.st.encode_entry(c)
        self.assertGreater(self.st.space.cosine(va, vb),
                            self.st.space.cosine(va, vc))

    def test_encode_name_axis_distinct(self):
        d1 = self.index.by_id("001")
        d2 = self.index.by_id("002")
        n1 = self.st.encode_name(d1)
        n2 = self.st.encode_name(d2)
        self.assertLess(self.st.space.cosine(n1, n2), 0.3)

    def test_name_axis_not_in_style_axis(self):
        # 名轴不混入风格张量（检索"像谁"不被名字字面绑架）
        d = self.index.by_id("001")
        v = self.st.encode_entry(d)
        n = self.st.encode_name(d)
        self.assertLess(self.st.space.cosine(v, n), 0.3)

    def test_shared_tags_yield_similarity(self):
        # 标签重叠的导演应有非零相似（如"霓虹"系）
        d6 = self.index.by_id("006")  # 雷弗恩：霓虹冷蓝
        hits = self.st.similar_by_director(d6, k=5)
        self.assertTrue(all(s > 0 for _, s in hits))


# ---------------------------------------------------------------- 指针纪律
class TestAssetPointers(unittest.TestCase):
    def test_images_not_in_repo_declared(self):
        self.assertIn("不入 git 仓", ASSET_POINTERS["images"])

    def test_remote_pack_honesty(self):
        # 四套提示词文件未提供——如实声明，不虚构
        self.assertIn("未提供", ASSET_POINTERS["remote_full_pack"])
        self.assertIn("不虚构", ASSET_POINTERS["remote_full_pack"])

    def test_md_source_declared(self):
        self.assertIn("59798 B", ASSET_POINTERS["md_source"])

    def test_image_files_actually_exist_outside_repo(self):
        # 素材目录真实存在 202 张图（指针指向实物，非空指针）
        img_dir = r"F:\doubaowork\.tmp_v52_in\图片和附件"
        if os.path.isdir(img_dir):
            n = len([f for f in os.listdir(img_dir) if f.endswith(".jpg")])
            self.assertEqual(n, 202)
        else:
            self.skipTest("素材目录不在本机（执行方环境）")


# ---------------------------------------------------------------- 总闸
class TestCinemaGate(unittest.TestCase):
    def test_self_check_all_green(self):
        sc = CinemaGate(index=DirectorIndex.load(DATA)).self_check()
        self.assertTrue(sc["ok"], sc["checks"])
        for name, c in sc["checks"].items():
            self.assertTrue(c["ok"], "check failed: %s" % name)

    def test_run_manifest_honesty(self):
        m = CinemaGate(index=DirectorIndex.load(DATA)).run()
        self.assertEqual(m["ring"], 18)
        self.assertEqual(m["batch"], "V52")
        h = m["honesty"]
        self.assertFalse(h["neural"])
        self.assertFalse(h["network"])
        self.assertEqual(h["new_dependencies"], 0)
        self.assertEqual(len(h["not_included"]), 3)
        self.assertIn("FilmGrab", h["stills_provenance"])

    def test_run_with_query_demo(self):
        m = CinemaGate(index=DirectorIndex.load(DATA)).run(query="霓虹暗夜暴力")
        demo = m["artifacts"]["query_demo"]
        self.assertEqual(len(demo["hits"]), 5)
        self.assertTrue(all("score" in x for x in demo["hits"]))

    def test_run_index_receipt_real_content(self):
        m = CinemaGate(index=DirectorIndex.load(DATA)).run()
        rec = m["artifacts"]["index_receipt"]
        self.assertEqual(rec["count"], 200)
        self.assertEqual(len(rec["categories"]), 10)

    def test_chain_position(self):
        self.assertEqual(CHAIN_POSITION["ring"], 18)
        self.assertEqual(CHAIN_POSITION["batch"], "V52")
        ups = " ".join(CHAIN_POSITION["upstream"])
        self.assertIn("semvec", ups)
        self.assertIn("hypervector", ups)

    def test_probe_with_small_sample(self):
        r = probe()
        self.assertTrue(r["ok"])
        self.assertEqual(r["seal"], SEAL)

    def test_fingerprint(self):
        fp = fingerprint()
        self.assertEqual(fp["ring"], 18)
        self.assertEqual(fp["seal"], SEAL)
        self.assertEqual(len(fp["categories"]), 10)

    def test_empty_index_self_check_fails_honestly(self):
        # 数据未落盘：自检如实失败（不装绿）
        gate = CinemaGate(index=DirectorIndex([]))
        sc = gate.self_check()
        self.assertFalse(sc["ok"])


# ---------------------------------------------------------------- 复用锚点
class TestReuseAnchors(unittest.TestCase):
    def test_semvec_tokenize_alive(self):
        toks = tokenize("霓虹冷蓝暗夜城市")
        self.assertIn("霓虹", toks)
        self.assertIn("城市", toks)

    def test_hypervector_space_alive(self):
        sp = HypervectorSpace()
        a = sp.make("cinema-test")
        self.assertEqual(len(a), sp.dim)

    def test_style_tensor_uses_hypervector_carrier(self):
        # 张量向量耦合不变：载体=HypervectorSpace（V51/V51R 同层）
        st = StyleTensor(DirectorIndex.load(DATA))
        self.assertIsInstance(st.space, HypervectorSpace)


if __name__ == "__main__":
    unittest.main(verbosity=2)
