# -*- coding: utf-8 -*-
"""V85 · 同型第三处治理：topology_resonance_pack 的 `governable` 三态化
================================================================================
病灶（四人组与千问逐行核验一致）：
  `fa_gradient_analysis` 末段
      convexity = "convex" if curvature > 0 else ("concave" if curvature < 0 else "flat")
      "governable": convexity == "convex"
  曲线判定用**浮点判符号、零容差**，而价值函数在本技能里是固定的线性权重和，
  二阶差分理论上恰为 0，浮点舍入给出 ±1e-17 残差：
      · 残差为正 → "convex" → `governable=True`（凭空判「可治理」）
      · 残差为负 → "concave" → `governable=False`（平域被冒充成「不可治理」）
  这正是 V82 已在 `quartet_director_pack` 治掉、本包漏治的同构副本。

本测试六组：
  1. 三态基础（默认线性态必须 None，不是 True / False）
  2. 判定装置 helper（相对容差 + 三分支）
  3. 与 quartet 侧口径对齐（同一 tol 口径、同一「未判定」措辞）
  4. emergence 链透传（法步字段真实可达）
  5. AST 锁（`governable` 不得再写成 `convexity == "convex"`；必须走 helper）
  6. 金丝雀 C1–C8（每条锁一种回归）

证红口径：本文件在**未改源码**上必红（C1/C2 与三态基础组直接复现 True/False 伪影）；
改码后应全绿。
"""
from __future__ import unicode_literals

import ast
import os
import unittest

import holoaeon.packs.topology_resonance_pack as tp
import holoaeon.packs.quartet_director_pack as q

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "holoaeon", "packs", "topology_resonance_pack.py")

# 线性价值函数 + 有限差分：理论上曲率恒 0，浮点只留残差
LINEAR_CASES = [
    ("0.3,0.5,0.2,0.8", "0.1,0.1,0.1,0.1"),
    ("0.1,0.2,0.3,0.4", "0.1,0.1,0.1,0.1"),
    ("0.7,0.7,0.7,0.7", "0.2,0.2,0.2,0.2"),
    ("0.11,0.13,0.17,0.19", "0.03,0.03,0.03,0.03"),
    ("0.2,0.4,0.6,0.8", "0.05,0.05,0.05,0.05"),
    ("0.9,0.5,0.1,0.0", "0.07,0.07,0.07,0.07"),
]


def _read_src():
    with open(SRC, "r", encoding="utf-8") as fh:
        return fh.read()


def _fa(state, pert):
    return tp.fa_gradient_analysis(
        current=",".join(str(x) for x in state.split(",")),
        perturbation=",".join(str(x) for x in pert.split(",")))


class TestTristateBasics(unittest.TestCase):
    """组 1 · 三态基础：平域不得冒充 True，也不得冒充 False。"""

    def test_t1_default_linear_is_none(self):
        r = tp.fa_gradient_analysis()
        self.assertIsNone(r["governable"], "线性默认态被判了布尔：零容差浮点判符号回归")
        self.assertEqual(r["convexity"], "flat")

    def test_t2_output_carries_tolerance(self):
        r = tp.fa_gradient_analysis()
        self.assertIn("curvature_tol", r)
        self.assertGreater(r["curvature_tol"], 0.0)

    def test_t3_output_carries_note(self):
        r = tp.fa_gradient_analysis()
        self.assertIn("governable_note", r)
        self.assertIn("未判定", r["governable_note"])

    def test_t4_not_false_either(self):
        r = tp.fa_gradient_analysis()
        self.assertIsNot(r["governable"], False, "平域被冒充成「不可治理」")

    def test_t5_gradient_fields_intact(self):
        r = tp.fa_gradient_analysis(current="0.3,0.5,0.2,0.8",
                                    perturbation="0.1,0.1,0.1,0.1")
        self.assertEqual(r["step"], "法")
        self.assertEqual(len(r["gradient"]), 4)
        self.assertEqual(len(r["gradient_direction"]), 4)


class TestClassifyHelper(unittest.TestCase):
    """组 2 · 判定装置：相对容差 + 三分支。"""

    def test_h1_tol_formula(self):
        # tol = 1e-9 * max(1.0, |f0|)
        self.assertAlmostEqual(tp._curvature_tol(0.5), 1e-9, places=18)
        self.assertAlmostEqual(tp._curvature_tol(0.0), 1e-9, places=18)
        self.assertAlmostEqual(tp._curvature_tol(-2.0), 2e-9, places=18)

    def test_h2_scale_constant(self):
        self.assertAlmostEqual(tp.CURVATURE_TOL_SCALE, 1e-9, places=18)

    def test_h3_three_branches(self):
        tol = tp._curvature_tol(0.5)
        up = tp._classify_curvature(tol * 1.0001, 0.5)
        down = tp._classify_curvature(-tol * 1.0001, 0.5)
        flat = tp._classify_curvature(1e-17, 0.5)
        self.assertIs(up["governable"], True)
        self.assertEqual(up["convexity"], "convex")
        self.assertIs(down["governable"], False)
        self.assertEqual(down["convexity"], "concave")
        self.assertIsNone(flat["governable"])
        self.assertEqual(flat["convexity"], "flat")

    def test_h4_helper_returns_all_keys(self):
        for c in (1.0, -1.0, 0.0):
            d = tp._classify_curvature(c, 0.5)
            for k in ("convexity", "governable", "curvature_tol", "governable_note"):
                self.assertIn(k, d)


class TestQuartetAlignment(unittest.TestCase):
    """组 3 · 与 V82 已治的 quartet 侧同口径（同 tol、同措辞）。"""

    def test_a1_same_tol_formula(self):
        for f0 in (0.0, 0.5, 10.0, -3.0, 1e6):
            self.assertAlmostEqual(tp._curvature_tol(f0), q._curvature_tol(f0),
                                   places=18, msg="f0=%r tol 口径不一致" % (f0,))

    def test_a2_same_flat_wording(self):
        a = tp._classify_curvature(0.0, 0.5)["governable_note"]
        b = q._classify_curvature(0.0, 0.5)["governable_note"]
        self.assertIn("未判定", a)
        self.assertIn("未判定", b)

    def test_a3_same_tol_scale_constant(self):
        self.assertAlmostEqual(tp.CURVATURE_TOL_SCALE, q.CURVATURE_TOL_SCALE, places=18)


class TestChainForward(unittest.TestCase):
    """组 4 · emergence 链透传：法步字段真实可达，三态不塌陷。"""

    def test_c1_chain_fa_governable_key(self):
        r = tp.emergence_chain(concept="拓扑共振")
        fa = r["steps"]["法_fa"]
        self.assertIn("governable", fa)
        self.assertIn(fa["governable"], (True, False, None))

    def test_c2_chain_fa_note_present(self):
        r = tp.emergence_chain(concept="拓扑共振")
        self.assertIn("governable_note", r["steps"]["法_fa"])

    def test_c3_chain_quartet_intact(self):
        r = tp.emergence_chain(concept="拓扑共振")
        self.assertIn("quartet", r)
        self.assertIn("scores", r["quartet"])


class TestAstLock(unittest.TestCase):
    """组 5 · AST 锁：`governable` 不得再写成浮点判符号的布尔比较。"""

    def test_l1_no_equality_squeeze(self):
        tree = ast.parse(_read_src())
        hits = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "fa_gradient_analysis":
                for sub in ast.walk(node):
                    if not isinstance(sub, ast.Assign):
                        continue
                    keys = []
                    if isinstance(sub.targets[0], ast.Name):
                        keys.append(sub.targets[0].id)
                    if isinstance(sub.targets[0], ast.Subscript):
                        # dict 字面量里的 "governable" 键由下面的 Dict 扫描处理
                        pass
                    if "governable" in keys:
                        hits.append("assign:%s" % keys[0])
                    if isinstance(sub.value, ast.Compare):
                        # 形如 X == "convex" 的布尔压缩
                        for c in sub.value.comparators:
                            if isinstance(c, ast.Constant) and c.value == "convex":
                                hits.append("compare==convex")
        # dict 字面量内 "governable": convexity == "convex" 也要抓
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "fa_gradient_analysis":
                for sub in ast.walk(node):
                    if isinstance(sub, ast.Dict):
                        for k, v in zip(sub.keys, sub.values):
                            if isinstance(k, ast.Constant) and k.value == "governable":
                                if isinstance(v, ast.Compare):
                                    hits.append("dict:governable==compare")
        self.assertEqual(hits, [], "governable 仍在用布尔比较写死: %s" % hits)

    def test_l2_uses_helper(self):
        tree = ast.parse(_read_src())
        calls = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "fa_gradient_analysis":
                for sub in ast.walk(node):
                    if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name):
                        calls.append(sub.func.id)
        self.assertIn("_classify_curvature", calls,
                      "fa_gradient_analysis 未走 _classify_curvature：三态装置被绕过")

    def test_l3_no_zero_compare(self):
        """曲率不得与字面 0 比较（`curvature > 0` 就是零容差判符号的根）。"""
        tree = ast.parse(_read_src())
        hits = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "fa_gradient_analysis":
                for sub in ast.walk(node):
                    if not isinstance(sub, ast.Compare):
                        continue
                    left = sub.left
                    name = left.id if isinstance(left, ast.Name) else ""
                    if "curv" not in name.lower():
                        continue
                    for c in sub.comparators:
                        if isinstance(c, ast.Constant) and c.value == 0:
                            hits.append("curvature 与字面 0 比较")
        self.assertEqual(hits, [], "仍存在与字面 0 的曲率比较: %s" % hits)


class TestCanaries(unittest.TestCase):
    """组 6 · C1–C8 金丝雀：每条锁一种回归。"""

    def test_c1_linear_never_convex(self):
        """C1 六组线性态只要被判 True 即红（浮点伪影回归）。"""
        for st, pe in LINEAR_CASES:
            r = _fa(st, pe)
            self.assertIsNot(r["governable"], True,
                             "线性态被判可治理：%s/%s curvature=%r"
                             % (st, pe, r["curvature"]))

    def test_c2_linear_never_concave(self):
        """C2 六组线性态只要被判 False 即红（平域冒充不可治理）。"""
        for st, pe in LINEAR_CASES:
            r = _fa(st, pe)
            self.assertIsNot(r["governable"], False,
                             "线性态被判不可治理：%s/%s curvature=%r"
                             % (st, pe, r["curvature"]))

    def test_c3_only_three_states(self):
        vals = {tp._classify_curvature(c, 0.5)["governable"]
                for c in (1.0, -1.0, 0.0, 1e-17, -1e-17)}
        self.assertEqual(vals, {True, False, None})

    def test_c4_tolerance_is_relative(self):
        """C4 tol 被写成绝对常数即红。"""
        self.assertAlmostEqual(tp._curvature_tol(10.0) / tp._curvature_tol(1.0), 10.0, places=6)
        self.assertAlmostEqual(tp._curvature_tol(100.0) / tp._curvature_tol(10.0), 10.0, places=6)

    def test_c5_note_not_empty(self):
        for c in (1.0, -1.0, 0.0):
            self.assertTrue(tp._classify_curvature(c, 0.5)["governable_note"])

    def test_c6_pack_counts_unchanged(self):
        p = tp.TopologyResonancePack()
        self.assertEqual((len(p.skills), len(p.roles), len(p.workflows)), (16, 5, 2))

    def test_c7_fa_skill_registered(self):
        p = tp.TopologyResonancePack()
        names = [getattr(s, "name", "") for s in p.skills]
        self.assertIn("fa_gradient_analysis", names)

    def test_c8_other_legal_steps_intact(self):
        self.assertEqual(tp.dao_define_problem()["step"], "道")
        self.assertEqual(tp.shu_constraint_handling()["step"], "术")


if __name__ == "__main__":
    unittest.main()
