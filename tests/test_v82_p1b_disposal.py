# -*- coding: utf-8 -*-
"""V82 · P1-B 失效判据处置测试（governable 三态 + p23 真实入参 + 金丝雀 8 只）

背景（四人组 V82 投喂包 §1，源码实锤）：
  · `advisor_gradient_flow` 原 `governable = convexity == "convex"`：
    曲率是浮点差分（线性价值函数理论恒 0，残差 ±1e-17），`>0` 即判 convex → 伪影；
    同时 `flat` 落进 False —— 三态（凸/凹/未判定）被压成一态（V67 `stagnation_side=None` 同病根）。
  · `check_emergence` / `advisor_quartet_tensor` 原
    `"P2×P3_strong(≥0.7)": QUARTET_SIMS["P2×P3"] >= EMERGENCE_P23` ——
    常量 0.7 比常量 0.7，**永真**，涌现四判据第一条从未约束过任何输入。

本文件的分组：
  A 三态映射（注入曲率，含 ±1e-17 残差）
  B 相对容差 tol（锁「随量级」，写死绝对常数即红）
  C P2×P3 判据可假（旧码恒真）
  D 显式 p23 入参优先
  E tensor 入口同为真实入参
  F QUARTET_SIMS 降级为静态先验表（保留、判据不再读）
  G 兼容性（公开示例结果不变）
  H 全链回归（pack 计数 / 其他 skill / selfcheck）
  C1–C8 八只金丝雀（每条锁一种回归）
"""
import ast
import io
import math
import os
import unittest

from holoaeon.packs import quartet_director_pack as q


SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)),
                   ), "holoaeon", "packs", "quartet_director_pack.py")


def _condition(r):
    """取涌现条件字典（键名保持 "P2×P3_strong(≥0.7)"）。"""
    cond = r.get("conditions", r.get("emergence_conditions"))
    assert cond is not None, "输出必须回显涌现条件字典"
    return cond


def _read_src():
    with io.open(SRC, encoding="utf-8") as f:
        return f.read()


class _A_TriState(unittest.TestCase):
    """A · 三态映射：注入曲率直接验三态（入口恒线性，见回执 honest_boundary）。"""

    def test_a1_true_convex(self):
        r = q._classify_curvature(1.0, 0.5)
        self.assertEqual(r["convexity"], "convex")
        self.assertIs(r["governable"], True)

    def test_a2_false_concave(self):
        r = q._classify_curvature(-1.0, 0.5)
        self.assertEqual(r["convexity"], "concave")
        self.assertIs(r["governable"], False)

    def test_a3_none_flat_exact_zero(self):
        r = q._classify_curvature(0.0, 0.5)
        self.assertEqual(r["convexity"], "flat")
        self.assertIsNone(r["governable"])

    def test_a4_none_flat_positive_residue(self):
        r = q._classify_curvature(1e-17, 0.5)
        self.assertIsNone(r["governable"], "1e-17 正残差不得判可治理")

    def test_a5_none_flat_negative_residue(self):
        r = q._classify_curvature(-1e-17, 0.5)
        self.assertIsNone(r["governable"])

    def test_a6_residue_1e16_scale_flat(self):
        """强量级下残差被相对容差吃掉（1e-16 相对）。"""
        r = q._classify_curvature(1e-16, 1.0)
        self.assertIsNone(r["governable"])

    def test_a7_note_present_and_flat_says_undetermined(self):
        for c in (1.0, -1.0, 0.0):
            r = q._classify_curvature(c, 0.5)
            self.assertTrue(r["governable_note"])
        self.assertIn("未判定", q._classify_curvature(0.0, 0.5)["governable_note"])

    def test_a8_tol_boundary(self):
        tol = q._curvature_tol(0.5)
        self.assertIs(q._classify_curvature(tol * 1.0001, 0.5)["governable"], True)
        self.assertIsNone(q._classify_curvature(tol * 0.999, 0.5)["governable"])


class _B_RelativeTolerance(unittest.TestCase):
    """B · tol 相对化：随 |f0| 量级增长，不许写死成绝对常数。"""

    def test_b1_unit_scale(self):
        self.assertAlmostEqual(q._curvature_tol(0.5), 1e-9, places=15)

    def test_b2_tenfold_scale(self):
        self.assertAlmostEqual(q._curvature_tol(10.0), 1e-8, delta=1e-15)

    def test_b3_zero_magnitude_floor(self):
        self.assertAlmostEqual(q._curvature_tol(0.0), 1e-9, places=15)

    def test_b4_grows_with_magnitude(self):
        self.assertGreater(q._curvature_tol(1e6), q._curvature_tol(1.0))


class _C_CriterionCanBeFalse(unittest.TestCase):
    """C · P2×P3 判据必须能假（旧码常量恒真）。"""

    def test_c1_condition_false_on_divergence(self):
        r = q.check_emergence(0.9, 0.9, 0.2, 0.3)
        self.assertIs(_condition(r)["P2×P3_strong(≥0.7)"], False)

    def test_c2_emergence_false_on_divergence(self):
        self.assertIs(q.check_emergence(0.9, 0.9, 0.2, 0.3)["emergence"], False)

    def test_c3_condition_true_on_agree(self):
        r = q.check_emergence(0.85, 0.85, 0.85, 0.30)
        self.assertIs(_condition(r)["P2×P3_strong(≥0.7)"], True)

    def test_c4_p23_echo_default_one(self):
        self.assertAlmostEqual(q.check_emergence(0.85, 0.85, 0.85, 0.30)["p23_similarity"], 1.0)

    def test_c5_p23_echo_divergence(self):
        self.assertAlmostEqual(q.check_emergence(0.9, 0.9, 0.2, 0.3)["p23_similarity"], 0.3, places=4)

    def test_c6_p23_key_always_present(self):
        for args in ((0.85, 0.85, 0.85, 0.30), (0.2, 0.1, 0.9, 0.95), (0, 0, 0, 0)):
            self.assertIn("p23_similarity", q.check_emergence(*args))

    def test_c7_witness_exists(self):
        """存在输入使第一条为 False——判据「活着」的最小证据。"""
        seen_false = False
        for p2, p3 in ((0.9, 0.2), (0.95, 0.30), (0.1, 0.95), (0.9, 0.4)):
            r = q.check_emergence(0.9, p2, p3, 0.3)
            if _condition(r)["P2×P3_strong(≥0.7)"] is False:
                seen_false = True
        self.assertTrue(seen_false, "P2×P3 判据对任何输入都不为假 = 恒真回归")


class _D_ExplicitP23(unittest.TestCase):
    """D · 显式 p23 优先于缺省口径。"""

    def test_d1_explicit_false(self):
        r = q.check_emergence(0.9, 0.9, 0.9, 0.3, p23=0.55)
        self.assertIs(_condition(r)["P2×P3_strong(≥0.7)"], False)
        self.assertAlmostEqual(r["p23_similarity"], 0.55, places=4)

    def test_d2_explicit_true_overrides_divergence(self):
        r = q.check_emergence(0.9, 0.9, 0.2, 0.3, p23=0.9)
        self.assertIs(_condition(r)["P2×P3_strong(≥0.7)"], True)
        self.assertAlmostEqual(r["p23_similarity"], 0.9, places=4)

    def test_d3_out_of_range_clipped(self):
        self.assertAlmostEqual(q.check_emergence(0.9, 0.9, 0.9, 0.3, p23=2.0)["p23_similarity"], 1.0)
        self.assertAlmostEqual(q.check_emergence(0.9, 0.9, 0.9, 0.3, p23=-3.0)["p23_similarity"], 0.0)

    def test_d4_none_equals_absent(self):
        a = q.check_emergence(0.9, 0.9, 0.2, 0.3)
        b = q.check_emergence(0.9, 0.9, 0.2, 0.3, p23=None)
        self.assertEqual(a["p23_similarity"], b["p23_similarity"])
        self.assertEqual(_condition(a), _condition(b))


class _E_TensorEntry(unittest.TestCase):
    """E · advisor_quartet_tensor（skill 入口，str 参数）同口径。"""

    def test_e1_divergence_false(self):
        r = q.advisor_quartet_tensor(p1="0.9", p2="0.9", p3="0.2", p4="0.3")
        self.assertIs(_condition(r)["P2×P3_strong(≥0.7)"], False)
        self.assertIs(r["emergence"], False)

    def test_e2_explicit_p23_str(self):
        r = q.advisor_quartet_tensor(p1="0.9", p2="0.9", p3="0.2", p4="0.3", p23="0.9")
        self.assertIs(_condition(r)["P2×P3_strong(≥0.7)"], True)

    def test_e3_p23_echo(self):
        self.assertIn("p23_similarity",
                      q.advisor_quartet_tensor(p1="0.85", p2="0.85", p3="0.85", p4="0.30"))

    def test_e4_key_name_stable(self):
        """键名不变（topology_resonance_pack 等下游按此键名读取）。"""
        r = q.advisor_quartet_tensor(p1="0.85", p2="0.85", p3="0.85", p4="0.30")
        self.assertIn("P2×P3_strong(≥0.7)", r["emergence_conditions"])


class _F_SimsDemoted(unittest.TestCase):
    """F · QUARTET_SIMS 保留不删，降级为静态先验表。"""

    def test_f1_table_intact(self):
        self.assertEqual(len(q.QUARTET_SIMS), 6)
        self.assertAlmostEqual(q.QUARTET_SIMS["P2×P3"], 0.7)

    def test_f2_still_echoed_as_prior(self):
        r = q.check_emergence(0.85, 0.85, 0.85, 0.30)
        r2 = q.advisor_quartet_tensor(p1="0.85", p2="0.85", p3="0.85", p4="0.30")
        self.assertEqual(r["similarities"], q.QUARTET_SIMS)
        self.assertEqual(r2["similarities"], q.QUARTET_SIMS)

    def test_f3_docstring_marks_prior(self):
        src = _read_src()
        self.assertIn("先验", src.split("QUARTET_SIMS")[0][-400:] + src.split("QUARTET_SIMS", 1)[1][:400])


class _G_Compatibility(unittest.TestCase):
    """G · 兼容性：公开示例与既有调用点结果不变。"""

    def test_g1_public_example(self):
        r = q.check_emergence(0.85, 0.85, 0.85, 0.30)
        self.assertIs(r["emergence"], True)
        self.assertAlmostEqual(r["order"], 0.5237, places=3)

    def test_g2_selfcheck_ok(self):
        self.assertIs(q.advisor_selfcheck()["ok"], True)

    def test_g3_empty_inputs_not_emerged(self):
        self.assertIs(q.check_emergence()["emergence"], False)

    def test_g4_readme_measured_example(self):
        self.assertIs(q.check_emergence(0.88, 0.92, 0.80, 0.34)["emergence"], True)


class _H_ChainRegression(unittest.TestCase):
    """H · 全链回归：pack 计数、默认输入三态、其他 skill 未破。"""

    def test_h1_pack_counts(self):
        p = q.QuartetDirectorPack()
        self.assertEqual((len(p.skills), len(p.roles), len(p.workflows)), (14, 5, 2))

    def test_h2_default_linear_state_undetermined(self):
        """价值函数线性 ⇒ 曲率理论 0 ⇒ 未判定（不是 False，更不是 True）。"""
        r = q.advisor_gradient_flow()
        self.assertIsNone(r["governable"])
        self.assertEqual(r["convexity"], "flat")

    def test_h3_output_carries_tolerance(self):
        r = q.advisor_gradient_flow()
        self.assertIn("curvature_tol", r)
        self.assertGreater(r["curvature_tol"], 0.0)

    def test_h4_other_skills_intact(self):
        self.assertEqual(q.advisor_constraint_audit()["step"], "术")
        self.assertIn("skills", q.pack_summary())


class _Canaries(unittest.TestCase):
    """C1–C8 · 八只金丝雀：每条锁一种回归。"""

    def test_c1_residue_not_convex(self):
        """C1 注入残差的线性态若判 convex 即红。"""
        cases = [([0.3, 0.5, 0.2, 0.8], [0.1] * 4),
                 ([0.1, 0.2, 0.3, 0.4], [0.1] * 4),
                 ([0.7, 0.7, 0.7, 0.7], [0.2] * 4),
                 ([0.11, 0.13, 0.17, 0.19], [0.03] * 4),
                 ([0.2, 0.4, 0.6, 0.8], [0.05] * 4),
                 ([0.9, 0.5, 0.1, 0.0], [0.07] * 4)]
        for st, pe in cases:
            r = q.advisor_gradient_flow(
                current=",".join(str(x) for x in st),
                perturbation=",".join(str(x) for x in pe))
            self.assertIsNot(r["governable"], True,
                             "线性态被判 convex：浮点伪影回归 (%s/%s)" % (st, pe))

    def test_c2_flat_must_be_none(self):
        """C2 flat 返回 False（压回布尔）即红。"""
        r = q.advisor_gradient_flow()
        self.assertIsNone(r["governable"])
        self.assertIsNot(r["governable"], False)

    def test_c3_only_three_states(self):
        """C3 三态之外任何值即红。"""
        vals = {q._classify_curvature(c, 0.5)["governable"] for c in (1.0, -1.0, 0.0, 1e-17)}
        self.assertEqual(vals, {True, False, None})

    def test_c4_constant_truth_regression(self):
        """C4 check_emergence(0.9,0.9,0.2,0.3) 第一条必须 False。"""
        r = q.check_emergence(0.9, 0.9, 0.2, 0.3)
        self.assertIsNot(_condition(r)["P2×P3_strong(≥0.7)"], True,
                         "P2×P3 条件对散开输入仍为 True：常量恒真回归")

    def test_c5_no_sims_in_conditions_ast(self):
        """C5 AST 锁：判据不再读 QUARTET_SIMS（判据-常量耦合回归）。"""
        tree = ast.parse(_read_src())
        hits = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name in (
                    "check_emergence", "advisor_quartet_tensor"):
                for sub in ast.walk(node):
                    if isinstance(sub, ast.Assign) and any(
                            isinstance(t, ast.Name) and t.id == "conditions" for t in sub.targets):
                        for d in ast.walk(sub.value):
                            if isinstance(d, ast.Name) and d.id == "QUARTET_SIMS":
                                hits.append(node.name)
        self.assertEqual(hits, [], "涌现 conditions 仍在读 QUARTET_SIMS: %s" % hits)

    def test_c6_explicit_p23_not_ignored(self):
        """C6 显式 p23 被忽略即红（缺省会是 True，显式 0.55 必须 False）。"""
        d = q.check_emergence(0.9, 0.9, 0.9, 0.3)
        e = q.check_emergence(0.9, 0.9, 0.9, 0.3, p23=0.55)
        self.assertIs(_condition(d)["P2×P3_strong(≥0.7)"], True)
        self.assertIs(_condition(e)["P2×P3_strong(≥0.7)"], False)

    def test_c7_tolerance_relative(self):
        """C7 tol 被删或写死绝对值即红。"""
        self.assertAlmostEqual(q._curvature_tol(10.0) / q._curvature_tol(1.0), 10.0, places=6)
        self.assertAlmostEqual(q._curvature_tol(100.0) / q._curvature_tol(10.0), 10.0, places=6)

    def test_c8_example_still_emerges(self):
        """C8 兼容性破坏即红：示例必须仍 True。"""
        self.assertIs(q.check_emergence(0.85, 0.85, 0.85, 0.30)["emergence"], True)


if __name__ == "__main__":
    unittest.main()
