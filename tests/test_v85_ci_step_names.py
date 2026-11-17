# -*- coding: utf-8 -*-
"""V85 · HA-3：ci.yml 步骤名回读式 + claims_gate 第 12 面 `ci_step_names_readback`
================================================================================
病灶：`.github/workflows/ci.yml` 步骤名写死「Contract tests (tests_contract, 184 cases)」
   与「v3 gate (33 faces incl. A13 CI contract)」，而 v3 实际 34 面、契约用例数也在涨。
   步骤名是给人看的断言，写死即撒谎；换批即过期且无人发现。

判据（面 12 三条）：
  HARDCODED_COUNT  `- name:` 里出现「N faces / N cases / N 面 / N 例」→ 红
  STEP_MISSING     没有 v3 gate 步骤 → 红
  NOT_READBACK     步骤名无任何「回读 / readback」声明 → 红

证红口径：临时 ci.yml 注入写死面数即红；修成回读式即绿。
"""
from __future__ import unicode_literals

import os
import shutil
import tempfile
import unittest

import holoaeon.claims_gate as cg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CI = os.path.join(ROOT, ".github", "workflows", "ci.yml")

GOOD = """name: CI
jobs:
  test:
    steps:
      - name: Interpreter
        run: python -VV
      - name: v3 gate (face count readback, incl. A13 CI contract)
        run: python scripts/v3_gate.py
"""

HARDCODED = """name: CI
jobs:
  test:
    steps:
      - name: Contract tests (tests_contract, 184 cases)
        run: python -m unittest discover -s tests_contract
      - name: v3 gate (33 faces incl. A13 CI contract)
        run: python scripts/v3_gate.py
"""

NO_V3 = """name: CI
jobs:
  test:
    steps:
      - name: Unit tests (case count readback)
        run: python -m unittest discover -s tests
"""

NO_READBACK = """name: CI
jobs:
  test:
    steps:
      - name: v3 gate
        run: python scripts/v3_gate.py
"""


class _Tmp(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="v85ci_")

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def _write(self, text, name="ci.yml"):
        p = os.path.join(self.dir, name)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(text)
        return p

    def _fails(self, text, name="ci.yml"):
        p = self._write(text, name)
        return cg.ci_step_names_readback({"ci_workflow": p})


class TestFaceStructure(unittest.TestCase):
    """组 1 · 结构：第 12 面进 FACES，面数走下界不写死。"""

    def test_s1_face_registered(self):
        self.assertEqual(cg.FACE_CI_STEPS, "ci_step_names_readback")
        self.assertIn(cg.FACE_CI_STEPS, cg.FACES)

    def test_s2_face_is_last(self):
        self.assertEqual(cg.FACES[-1], cg.FACE_CI_STEPS)

    def test_s3_faces_lower_bound(self):
        self.assertGreaterEqual(len(cg.FACES), 12)  # V85 起 12 面；下界口径

    def test_s4_faces_unique(self):
        self.assertEqual(len(set(cg.FACES)), len(cg.FACES))

    def test_s5_report_has_face(self):
        rep = cg.verify()
        self.assertIn(cg.FACE_CI_STEPS, rep["faces"])
        self.assertIn("ci_steps", rep)


class TestRealRepo(unittest.TestCase):
    """组 2 · 真仓：当前 ci.yml 必须全绿（回读式已落地）。"""

    def test_r1_real_ci_green(self):
        fails = cg.ci_step_names_readback({"ci_workflow": CI})
        self.assertEqual(fails, [], "真仓 ci.yml 步骤名仍有写死位: %s" % fails)

    def test_r2_step_names_readable(self):
        names = cg.read_ci_step_names(CI)
        self.assertTrue(names)
        self.assertGreaterEqual(len(names), 10)

    def test_r3_v3_step_present(self):
        names = [n for _, n in cg.read_ci_step_names(CI)]
        self.assertTrue(any(n.startswith("v3 gate") for n in names))

    def test_r4_readback_declared(self):
        blob = " ".join(n for _, n in cg.read_ci_step_names(CI)).lower()
        self.assertIn("readback", blob)


class TestRedCases(_Tmp):
    """组 3 · 证红：写死面数 / 缺步骤 / 无回读声明。"""

    def test_d1_hardcoded_faces_red(self):
        fails = self._fails(HARDCODED)
        hard = [f for f in fails if f["detail"].startswith("HARDCODED_COUNT")]
        self.assertGreaterEqual(len(hard), 1, "写死 33 faces 未被拦: %s" % fails)
        self.assertTrue(any("33 faces" in f["detail"] for f in hard))

    def test_d2_hardcoded_cases_red(self):
        fails = self._fails(HARDCODED)
        self.assertTrue(any("184 cases" in f["detail"] for f in fails))

    def test_d3_missing_v3_step_red(self):
        fails = self._fails(NO_V3)
        self.assertTrue(any(f["detail"].startswith("STEP_MISSING") for f in fails))

    def test_d4_no_readback_red(self):
        fails = self._fails(NO_READBACK)
        self.assertTrue(any(f["detail"].startswith("NOT_READBACK") for f in fails))

    def test_d5_missing_file_incomplete(self):
        fails = cg.ci_step_names_readback(
            {"ci_workflow": os.path.join(self.dir, "nope.yml")})
        self.assertEqual(len(fails), 1)
        self.assertTrue(fails[0]["detail"].startswith("INCOMPLETE"))

    def test_d6_good_file_green(self):
        self.assertEqual(self._fails(GOOD), [])

    def test_d7_quoted_name_detected(self):
        text = GOOD.replace(
            "- name: v3 gate (face count readback, incl. A13 CI contract)",
            '- name: "v3 gate (7 faces)"')
        fails = self._fails(text)
        self.assertTrue(any(f["detail"].startswith("HARDCODED_COUNT") for f in fails))

    def test_d8_cn_caliber_detected(self):
        text = GOOD.replace(
            "- name: v3 gate (face count readback, incl. A13 CI contract)",
            "- name: v3 gate (34 面，含 A13)")
        fails = self._fails(text)
        self.assertTrue(any("34 面" in f["detail"] for f in fails))


class TestNoRegression(_Tmp):
    """组 4 · 不误伤：既有步骤名（维度锁 / 契约前缀）不得被判写死。"""

    def test_n1_dimension_lock_ok(self):
        text = GOOD.replace(
            "- name: Interpreter",
            "- name: Dimension lock (25 / 47 / 9 must not drift)")
        self.assertEqual(self._fails(text), [])

    def test_n2_examples_ok(self):
        text = GOOD.replace("- name: Interpreter", "- name: Examples 01-04 (smoke)")
        self.assertEqual(self._fails(text), [])

    def test_n3_other_faces_still_pass(self):
        rep = cg.verify()
        for f in cg.FACES:
            self.assertTrue(rep["faces"][f]["ok"], "%s 面色变" % f)


if __name__ == "__main__":
    unittest.main()
