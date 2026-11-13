# -*- coding: utf-8 -*-
"""
test_v78_ci_preflight.py —— V78a 本地预检闸的测试（12 例）
================================================================================
判据分三类：
  A. 结构：步骤表 10 面、id 唯一、字段齐、kind 合法；
  B. 契约：正向（声明都命中 ci.yml）+ 反向（ci.yml 每步都被认领）+ 篡改必红；
  C. 行为：info 不判红、失败命令必判红、--list 不执行、报告字段齐、零第三方依赖。

「可失败」是本批的重点：一台永远绿的闸等于没有闸，
所以 T07/T09 专门证明它在该红的时候会红。
"""
from __future__ import annotations

import ast
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "scripts", "ci_preflight.py")
WORKFLOW = os.path.join(ROOT, ".github", "workflows", "ci.yml")

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def load_preflight():
    spec = importlib.util.spec_from_file_location("ci_preflight_under_test", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestStructure(unittest.TestCase):
    """A 类：步骤表本身像不像一张表。"""

    @classmethod
    def setUpClass(cls):
        cls.m = load_preflight()

    def test_01_ten_steps(self):
        """T01：步骤表恰好 12 面（V78b：+Manifest integrity / +v3 gate），与 ci.yml 对齐。"""
        self.assertEqual(len(self.m.STEPS), 12)
        self.assertEqual(len(self.m.declared_ci_names()), 12)

    def test_02_unique_ids_and_kinds(self):
        """T02：id 唯一，kind 只能是 info / run / multi。"""
        ids = [s["id"] for s in self.m.STEPS]
        self.assertEqual(len(ids), len(set(ids)))
        for s in self.m.STEPS:
            self.assertIn(s["kind"], ("info", "run", "multi"))

    def test_03_fields_present(self):
        """T03：每面都有 id / ci_name / kind / desc / cmd，且 desc 非空。"""
        for s in self.m.STEPS:
            for key in ("id", "ci_name", "kind", "desc", "cmd"):
                self.assertIn(key, s, "缺失字段 %s in %s" % (key, s.get("id")))
            self.assertTrue(str(s["desc"]).strip())
            self.assertTrue(len(s["cmd"]) >= 1)


class TestContract(unittest.TestCase):
    """B 类：ci.yml 与预检器两张表不许漂移。"""

    @classmethod
    def setUpClass(cls):
        cls.m = load_preflight()

    def test_04_forward_every_claim_exists(self):
        """T04（正向）：预检器声明的每一面，ci.yml 里都得有。"""
        ci_names = self.m.read_ci_names(WORKFLOW)
        for prefix in self.m.declared_ci_names():
            self.assertTrue(any(n.startswith(prefix) for n in ci_names),
                            "ci.yml 缺这一步：%s" % prefix)

    def test_05_reverse_every_ci_step_claimed(self):
        """T05（反向）：ci.yml 里的每个 - name，预检器都得认领。"""
        rep = self.m.contract_report(WORKFLOW)
        self.assertEqual(rep["missing"], [], "无人认领的 ci 步骤：%r" % (rep["missing"],))

    def test_06_contract_aligned(self):
        """T06：双向对齐结论为 True，且两边计数都是 12（V78b）。"""
        rep = self.m.contract_report(WORKFLOW)
        self.assertTrue(rep["aligned"])
        self.assertEqual(rep["ci_steps"], 12)
        self.assertEqual(rep["claimed_steps"], 12)
        self.assertEqual(rep["unused"], [])

    def test_07_tampered_workflow_goes_red(self):
        """T07（可失败证明）：给 ci.yml 塞一个没人认领的步骤，对齐必须判红。"""
        with open(WORKFLOW, "r", encoding="utf-8") as fh:
            text = fh.read()
        tampered = text + "\n      - name: Shadow step nobody claimed\n        run: echo hi\n"
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "ci_tampered.yml")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(tampered)
            rep = self.m.contract_report(path)
        self.assertFalse(rep["aligned"], "多出一个没人认领的步骤，必须判不对齐")
        self.assertIn("Shadow step nobody claimed", rep["missing"])


class TestBehaviour(unittest.TestCase):
    """C 类：跑起来的行为与报告。"""

    @classmethod
    def setUpClass(cls):
        cls.m = load_preflight()

    def test_08_info_step_never_red(self):
        """T08：info 类（解释器版本）只记录，不参判红。"""
        step = next(s for s in self.m.STEPS if s["kind"] == "info")
        r = self.m.run_step(step)
        self.assertTrue(r["ok"])
        self.assertEqual(r["rc"], 0)
        self.assertTrue(r["summary"])

    def test_09_failing_command_goes_red(self):
        """T09（可失败证明）：一条必然失败的命令，必须 rc≠0 且 ok=False。"""
        bad = {"id": "boom", "ci_name": "Boom", "kind": "run",
               "cmd": ["-c", "import sys; sys.exit(7)"], "desc": "故意失败"}
        r = self.m.run_step(bad)
        self.assertFalse(r["ok"])
        self.assertEqual(r["rc"], 7)

    def test_10_multi_step_stops_on_first_failure(self):
        """T10：multi 类第一步失败即停，不继续跑后面的脚本（rc≠0 即红）。"""
        bad = {"id": "boom2", "ci_name": "Boom2", "kind": "multi",
               "cmd": ["examples/__nonexistent_step__.py", "examples/01_basic_matrix.py"],
               "desc": "multi"}
        r = self.m.run_step(bad)
        self.assertFalse(r["ok"])
        self.assertNotEqual(r["rc"], 0)

    def test_11_list_does_not_execute(self):
        """T11：--list 只打印步骤表，不执行任何门禁（rc=0 且列出 12 行，V78b）。"""
        proc = subprocess.run([sys.executable, SCRIPT, "--list"], cwd=ROOT,
                              capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=120)
        self.assertEqual(proc.returncode, 0, proc.stderr[-300:])
        lines = [ln for ln in (proc.stdout or "").splitlines() if ln.strip()]
        self.assertEqual(len(lines), 12)

    def test_12_report_fields_and_zero_dependency(self):
        """T12：报告字段齐（含契约段），且源码不引第三方库。"""
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "ci_preflight.json")
            proc = subprocess.run([sys.executable, SCRIPT, "--only", "interpreter",
                                   "--json", out], cwd=ROOT, capture_output=True,
                                  text=True, encoding="utf-8", errors="replace",
                                  timeout=180)
            self.assertEqual(proc.returncode, 0, proc.stderr[-300:])
            with open(out, "r", encoding="utf-8") as fh:
                rep = json.load(fh)
        for key in ("gate", "doc_version", "steps", "passed", "total",
                    "failed", "verdict", "contract", "evidence_class"):
            self.assertIn(key, rep)
        self.assertEqual(rep["gate"], "ci_preflight")
        self.assertEqual(rep["verdict"], "PASS")
        self.assertEqual(rep["total"], 1)
        self.assertIn(rep["contract"]["aligned"], (True, False))
        self.assertEqual(rep["evidence_class"], "measured")

        # 参数不被误当路径：多 token 命令只有第一个拼 ROOT，其余原样
        # （V78a 首跑就是把 ``--runs 3`` 拼成 ROOT\--runs / ROOT\3 才红的）
        argv = self.m._argv(["scripts/measure_a1_a2.py", "--runs", "3"])
        self.assertEqual(os.path.normpath(argv[1]),
                         os.path.normpath(os.path.join(ROOT, "scripts", "measure_a1_a2.py")))
        self.assertEqual(argv[2:], ["--runs", "3"])
        argv2 = self.m._argv(["-m", "holoaeon.claims_gate", "verify"])
        self.assertEqual(argv2[1:], ["-m", "holoaeon.claims_gate", "verify"])

        # 零第三方依赖：顶层 import 只允许标准库与本仓 holoaeon
        stdlib_ok = {"argparse", "json", "os", "subprocess", "sys", "time",
                     "importlib", "hashlib", "unicodedata", "re", "io", "textwrap",
                     "__future__"}
        with open(SCRIPT, "r", encoding="utf-8") as fh:
            tree = ast.parse(fh.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for al in node.names:
                    root = al.name.split(".")[0]
                    self.assertTrue(root in stdlib_ok or root == "holoaeon",
                                    "第三方依赖：%s" % al.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                root = node.module.split(".")[0]
                self.assertTrue(root in stdlib_ok or root == "holoaeon",
                                "第三方依赖：%s" % node.module)


if __name__ == "__main__":
    unittest.main(verbosity=2)
