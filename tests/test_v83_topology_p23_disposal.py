# -*- coding: utf-8 -*-
"""V83 · 同型恒真第二处处置：topology_resonance_pack.quartet_tensor 的 P2×P3。

投喂包：AGENT_FEED_V83_TOPOLOGY_P23_DISPOSAL_20261114.md（§5）
- p23 缺省 = 本函数自有 `_cosine(vecs["P2"], vecs["P3"])` 真实共振（vecs = [s, 1-s]）
- p23 显式优先（clip01，非法回缺省口径）
- `sims` 常量表降级静态先验，只回显不参与判定
- 输出增 `p23_similarity`（无门槛回显）
- 8 金丝雀防倒退（含 AST 锁判据-常量耦合）
"""

import ast
import io
import unittest

from holoaeon.packs import topology_resonance_pack as T
from holoaeon.packs import quartet_director_pack as Q

SICK = ("0.9", "0.9", "0.2", "0.3")          # 病样本：p2/p3 差 0.7，cos ≈ 0.3482
ANCHOR = ("0.85", "0.85", "0.85", "0.30")    # test_v67:251 兼容锚（cos = 1.0）
COS_SICK = 0.3482                            # round(cos([0.9,0.1],[0.2,0.8]), 4)


def qt(*a, **k):
    return T.quartet_tensor(*a, **k)


def cond(r):
    return r["emergence_conditions"]["P2×P3_strong(≥0.7)"]


# ---------------------------------------------------------------- A 缺省口径（真实余弦）
class TestDefaultCosine(unittest.TestCase):
    def test_a1_sick_p23_value_is_real_cosine(self):
        r = qt(*SICK)
        self.assertEqual(r["p23_similarity"], COS_SICK)

    def test_a2_sick_first_condition_false(self):
        self.assertFalse(cond(qt(*SICK)))

    def test_a3_sick_emergence_false(self):
        self.assertFalse(qt(*SICK)["emergence"])

    def test_a4_same_scores_cos_is_one(self):
        r = qt("0.9", "0.9", "0.9", "0.3")
        self.assertEqual(r["p23_similarity"], 1.0)

    def test_a5_mid_scores_cos_is_one(self):
        self.assertEqual(qt("0.5", "0.5", "0.5", "0.3")["p23_similarity"], 1.0)

    def test_a6_opposite_scores_low_cos(self):
        self.assertEqual(qt("0.9", "0.9", "0.1", "0.3")["p23_similarity"], 0.2195)

    def test_a7_rounded_to_four_places(self):
        v = qt(*SICK)["p23_similarity"]
        self.assertEqual(round(v, 4), v)


# ---------------------------------------------------------------- B 显式 p23 优先
class TestExplicitP23(unittest.TestCase):
    def test_b1_explicit_low_kills_condition(self):
        r = qt(*ANCHOR, p23="0.55")
        self.assertFalse(cond(r))
        self.assertEqual(r["p23_similarity"], 0.55)

    def test_b2_explicit_high_passes(self):
        r = qt(*ANCHOR, p23="0.9")
        self.assertTrue(cond(r))
        self.assertEqual(r["p23_similarity"], 0.9)

    def test_b3_explicit_overrides_real_cosine(self):
        # cos(p2,p3)=1.0，但显式 0.3 必须按 0.3 判
        r = qt("0.9", "0.9", "0.9", "0.3", p23="0.3")
        self.assertFalse(cond(r))
        self.assertFalse(r["emergence"])
        self.assertEqual(r["p23_similarity"], 0.3)

    def test_b4_threshold_inclusive(self):
        self.assertTrue(cond(qt(*ANCHOR, p23="0.7")))

    def test_b5_below_threshold_exclusive(self):
        self.assertFalse(cond(qt(*ANCHOR, p23="0.6999")))

    def test_b6_clip_upper(self):
        self.assertEqual(qt(*ANCHOR, p23="1.2")["p23_similarity"], 1.0)

    def test_b7_clip_lower(self):
        self.assertEqual(qt(*ANCHOR, p23="-0.1")["p23_similarity"], 0.0)

    def test_b8_unparsable_falls_back_to_cosine(self):
        """非法 p23 字符串回缺省余弦口径（并在来源字段标注 fallback）。"""
        r = qt(*SICK, p23="abc")
        self.assertEqual(r["p23_similarity"], COS_SICK)
        self.assertIn("fallback", r.get("p23_source", ""))


# ---------------------------------------------------------------- C 输出结构
class TestOutputShape(unittest.TestCase):
    def test_c1_p23_similarity_present(self):
        self.assertIn("p23_similarity", qt(*SICK))

    def test_c2_similarities_still_echo_six_pairs(self):
        r = qt(*SICK)
        self.assertEqual(len(r["similarities"]), 6)
        self.assertEqual(r["similarities"]["P2×P3"], 0.7)

    def test_c3_conditions_four_keys(self):
        self.assertEqual(len(qt(*SICK)["emergence_conditions"]), 4)

    def test_c4_condition_tracks_p23(self):
        self.assertFalse(cond(qt(*SICK, p23="0.1")))
        self.assertTrue(cond(qt(*SICK, p23="0.8")))

    def test_c5_weight_matrix_preserved(self):
        w = qt(*SICK)["weight_matrix"]
        self.assertEqual(len(w), 5)
        self.assertEqual(w["道"]["P4"], 0.5)

    def test_c6_note_and_tensor_space(self):
        r = qt(*SICK)
        self.assertEqual(r["tensor_space"], "R^4")
        self.assertIn("note", r)


# ---------------------------------------------------------------- D 无门槛回显
class TestNoThresholdEcho(unittest.TestCase):
    def test_d1_res_pairs_excludes_p23_when_low(self):
        r = qt(*SICK)
        self.assertNotIn("P2×P3", [x["pair"] for x in r["resonance_pairs"]])

    def test_d2_p23_still_echoed_despite_absence(self):
        r = qt(*SICK)
        self.assertEqual(r["p23_similarity"], COS_SICK)
        self.assertNotEqual(r["p23_similarity"], 0.0)

    def test_d3_when_pair_resonates_value_matches(self):
        r = qt(*ANCHOR)
        hit = [x for x in r["resonance_pairs"] if x["pair"] == "P2×P3"]
        self.assertTrue(hit)
        self.assertEqual(hit[0]["resonance"], r["p23_similarity"])


# ---------------------------------------------------------------- E 兼容锚（既有测试零破坏）
class TestCompatAnchor(unittest.TestCase):
    def test_e1_anchor_emergence_true(self):
        self.assertTrue(qt(*ANCHOR)["emergence"])

    def test_e2_anchor_p23_is_one(self):
        self.assertEqual(qt(*ANCHOR)["p23_similarity"], 1.0)

    def test_e3_anchor_order_tracks_v67_expectation(self):
        # test_v67 的样本 order 仍 > 0.30（涌现第四判据不变）
        self.assertGreater(qt(*ANCHOR)["order"], 0.30)


# ---------------------------------------------------------------- F 两包口径并存（登记事实）
class TestTwoCalibersCoexist(unittest.TestCase):
    def test_f1_director_caliber_is_gap_based(self):
        d = Q.check_emergence(0.9, 0.9, 0.2, 0.3)
        self.assertEqual(d["p23_similarity"], 0.3)

    def test_f2_topology_caliber_is_cosine(self):
        self.assertEqual(qt(*SICK)["p23_similarity"], COS_SICK)

    def test_f3_two_values_differ(self):
        d = Q.check_emergence(0.9, 0.9, 0.2, 0.3)["p23_similarity"]
        t = qt(*SICK)["p23_similarity"]
        self.assertNotEqual(d, t)

    def test_f4_each_is_stable(self):
        self.assertEqual(qt(*SICK)["p23_similarity"], qt(*SICK)["p23_similarity"])
        self.assertEqual(Q.check_emergence(0.9, 0.9, 0.2, 0.3)["p23_similarity"],
                         Q.check_emergence(0.9, 0.9, 0.2, 0.3)["p23_similarity"])


# ---------------------------------------------------------------- G 静态表保留（谱系）
class TestStaticTablesKept(unittest.TestCase):
    def test_g1_sims_values_unchanged(self):
        self.assertEqual(qt(*SICK)["similarities"],
                         {"P1×P2": 0.5, "P1×P3": 0.4, "P1×P4": 0.3,
                          "P2×P3": 0.7, "P2×P4": 0.5, "P3×P4": 0.4})

    def test_g2_weight_matrix_intact(self):
        w = qt(*SICK)["weight_matrix"]
        self.assertEqual(w["升维"], {"P1": 0.5, "P2": 0.3, "P3": 0.4, "P4": 0.4})

    def test_g3_source_keeps_sims_definition(self):
        src = io.open(T.__file__, encoding="utf-8").read()
        self.assertIn('"P2×P3": 0.7', src)

    def test_g4_docstring_declares_static_prior(self):
        doc = T.quartet_tensor.__doc__ or ""
        self.assertIn("静态先验", doc)


# ---------------------------------------------------------------- H 确定性 / 边界
class TestDeterminism(unittest.TestCase):
    def test_h1_repeat_identical(self):
        a, b = qt(*SICK), qt(*SICK)
        self.assertEqual(a, b)

    def test_h2_empty_defaults_07(self):
        r = qt()
        self.assertEqual(r["scores"]["P1"], 0.7)
        self.assertEqual(r["p23_similarity"], 1.0)

    def test_h3_out_of_range_scores_clipped(self):
        r = qt("1.5", "0.9", "0.9", "-0.2")
        self.assertEqual(r["scores"]["P1"], 1.0)
        self.assertEqual(r["scores"]["P4"], 0.0)


# ---------------------------------------------------------------- 金丝雀 C1-C8（防倒退，改前必红）
class _Canaries(unittest.TestCase):
    def test_canary_c1_no_constant_in_judgement(self):
        """C1 源码涌现判据再引用 sims 即红（AST 锁）。"""
        src = io.open(T.__file__, encoding="utf-8").read()
        tree = ast.parse(src)
        fn = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef) and n.name == "quartet_tensor")
        # 1) emergence 赋值表达式里不得引用 sims
        em_assigns = [n for n in ast.walk(fn)
                      if isinstance(n, ast.Assign)
                      and any(isinstance(t, ast.Name) and t.id == "emergence"
                              for t in n.targets)]
        self.assertTrue(em_assigns, "quartet_tensor 应有 emergence 赋值")
        for a in em_assigns:
            names = [x.id for x in ast.walk(a.value) if isinstance(x, ast.Name)]
            self.assertNotIn("sims", names, "emergence 判据引用常量表（恒真回归）")
        # 2) emergence_conditions 字典的值里不得引用 sims
        cond_nodes = []
        for n in ast.walk(fn):
            if isinstance(n, ast.Dict):
                for k, v in zip(n.keys, n.values):
                    if isinstance(k, ast.Constant) and k.value == "emergence_conditions":
                        cond_nodes.append(v)
        self.assertTrue(cond_nodes, "应输出 emergence_conditions")
        for v in cond_nodes:
            names = [x.id for x in ast.walk(v) if isinstance(x, ast.Name)]
            self.assertNotIn("sims", names, "判据条件字典引用常量表（恒真回归）")

    def test_canary_c2_sick_sample_must_not_be_true(self):
        """C2 病样本第一条必须 False（旧码恒真 → 红）。"""
        self.assertFalse(cond(qt(*SICK)))
        self.assertFalse(qt(*SICK)["emergence"])

    def test_canary_c3_explicit_p23_must_be_honoured(self):
        """C3 显式 p23 被忽略即红。"""
        self.assertFalse(cond(qt("0.9", "0.9", "0.9", "0.3", p23="0.55")))
        self.assertEqual(qt("0.9", "0.9", "0.9", "0.3", p23="0.55")["p23_similarity"], 0.55)

    def test_canary_c4_same_infrastructure(self):
        """C4 p23_similarity 与 _cosine 独立重算一致；共振项同值。"""
        p2, p3 = 0.9, 0.2
        expect = round(T._cosine([p2, 1 - p2], [p3, 1 - p3]), 4)
        self.assertEqual(qt(*SICK)["p23_similarity"], expect)

    def test_canary_c5_anchor_locked(self):
        """C5 兼容锚锁死：0.85 全同 → True 且 p23=1.0。"""
        r = qt(*ANCHOR)
        self.assertTrue(r["emergence"])
        self.assertEqual(r["p23_similarity"], 1.0)

    def test_canary_c6_static_table_not_deleted(self):
        """C6 sims 表被删（谱系破坏）即红。"""
        src = io.open(T.__file__, encoding="utf-8").read()
        self.assertIn('"P1×P2": 0.5, "P1×P3": 0.4, "P1×P4": 0.3', src)

    def test_canary_c7_two_calibers_coexist(self):
        """C7 两包口径并存锁：0.3（1-|p2-p3|）vs ≈0.3482（cos），不同且各自稳定。"""
        d = Q.check_emergence(0.9, 0.9, 0.2, 0.3)["p23_similarity"]
        t = qt(*SICK)["p23_similarity"]
        self.assertEqual(d, 0.3)
        self.assertEqual(t, COS_SICK)
        self.assertNotEqual(d, t)

    def test_canary_c8_echo_without_threshold(self):
        """C8 无门槛回显：res_pairs 空也必须如实回显 cos（置 0 即红）。"""
        r = qt(*SICK)
        self.assertNotIn("P2×P3", [x["pair"] for x in r["resonance_pairs"]])
        self.assertGreater(r["p23_similarity"], 0.3)
        self.assertEqual(r["p23_similarity"], COS_SICK)


if __name__ == "__main__":
    unittest.main()
