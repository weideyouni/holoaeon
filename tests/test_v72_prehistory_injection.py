# -*- coding: utf-8 -*-
"""V72 史前判据注入包聚合测试（PL-5）：常量 / 指纹 / 发现 / 六判据 / 聚合 / 越界 / 真实站点。

原则：每条判据都要有一条「喂坏它就红」的用例——没有可失败性的断言不算判据。
"""
import copy
import io
import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holoaeon import prehistory_injection as pi  # noqa: E402

REAL_ROOT = r"F:\doubaowork\.tmp_v55_cluster"


def _ledger(cid):
    n = cid[1:]
    return {
        "schema": pi.LEDGER_SCHEMA,
        "version": "1.0",
        "cang_id": cid,
        "repo": "holoaeon-c%s-demo" % n,
        "domain": "演示域",
        "question": "演示问题",
        "phase_main": "土",
        "phase_sub": "水",
        "role": "演示角色",
        "turtle": "保存演示基线",
        "horse": "推演演示路径",
        "n19_anchor": "github.com/weideyouni/holoaeon",
        "cluster_ledger": "holoaeon/c18_cluster.py",
        "ring": 19,
        "seal": pi.SEAL,
        "batch": "V72-PREHISTORY-INJECTION",
        "injected_at": "2026-11-13",
        "mechanism_pointers": {k: "pointer-%d" % i for i, k in enumerate(pi.POINTER_KEYS)},
        "criteria": [{"id": c, "hard": True} for c in pi.CRITERIA_IDS],
        "counters": {"criteria": 6, "mechanism_pointers": 11},
    }


def _make_repo(root, cid):
    repo = "holoaeon-c%s-demo" % cid[1:]
    pkg = "holoaeon_c%s_demo" % cid[1:]
    os.makedirs(os.path.join(root, repo, pkg))
    os.makedirs(os.path.join(root, repo, "tests"))
    with io.open(os.path.join(root, repo, pkg, "ledger.json"), "w",
                 encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(_ledger(cid), ensure_ascii=False, indent=2))
    with io.open(os.path.join(root, repo, pkg, "gate.py"), "w",
                 encoding="utf-8", newline="\n") as fh:
        fh.write("# demo gate\n")
    return repo


class TestConstants(unittest.TestCase):

    def test_schema(self):
        self.assertEqual(pi.INJECTION_SCHEMA, "PREHISTORY-INJECTION-v1")

    def test_expected_repos(self):
        self.assertEqual(pi.EXPECTED_REPOS, 18)

    def test_criteria_count(self):
        self.assertEqual(len(pi.CRITERIA_IDS), 6)
        self.assertEqual(pi.CRITERIA_PER_REPO, 6)

    def test_pointer_count(self):
        self.assertEqual(len(pi.POINTER_KEYS), 11)
        self.assertEqual(pi.POINTERS_PER_REPO, 11)

    def test_ring_and_seal(self):
        self.assertEqual(pi.RING, 19)
        self.assertEqual(pi.SEAL, "潮起开门，潮落闭嘴")

    def test_note_states_boundary(self):
        self.assertIn("不复制", pi.NOTE)


class TestSha16(unittest.TestCase):

    def test_stable(self):
        a = pi.sha16({"x": [1, 2]})
        b = pi.sha16({"x": [1, 2]})
        self.assertEqual(a, b)
        self.assertEqual(len(a), 16)

    def test_key_order_irrelevant(self):
        self.assertEqual(pi.sha16({"a": 1, "b": 2}), pi.sha16({"b": 2, "a": 1}))

    def test_sensitive(self):
        self.assertNotEqual(pi.sha16({"a": 1}), pi.sha16({"a": 2}))


class TestEvaluate(unittest.TestCase):

    def setUp(self):
        self.led = _ledger("C07")
        self.by_id = {c["id"]: c for c in pi.evaluate(self.led)}

    def test_all_green(self):
        self.assertTrue(all(c["ok"] for c in pi.evaluate(self.led)))

    def test_identity_missing_red(self):
        led = copy.deepcopy(self.led)
        led["horse"] = "   "
        self.assertFalse({c["id"]: c["ok"] for c in pi.evaluate(led)}["identity_fields_present"])

    def test_cang_repo_mismatch_red(self):
        led = copy.deepcopy(self.led)
        led["repo"] = "holoaeon-c08-demo"
        self.assertFalse({c["id"]: c["ok"] for c in pi.evaluate(led)}["cang_id_wellformed"])

    def test_anchor_missing_red(self):
        led = copy.deepcopy(self.led)
        led["n19_anchor"] = "github.com/someone/else"
        self.assertFalse({c["id"]: c["ok"] for c in pi.evaluate(led)}["n19_anchor_declared"])

    def test_ring_drift_red(self):
        led = copy.deepcopy(self.led)
        led["ring"] = 18
        self.assertFalse({c["id"]: c["ok"] for c in pi.evaluate(led)}["ring_is_19"])

    def test_seal_drift_red(self):
        led = copy.deepcopy(self.led)
        led["seal"] = "潮起开门"
        self.assertFalse({c["id"]: c["ok"] for c in pi.evaluate(led)}["seal_intact"])

    def test_pointer_missing_red(self):
        led = copy.deepcopy(self.led)
        del led["mechanism_pointers"]["张量载体"]
        self.assertFalse({c["id"]: c["ok"] for c in pi.evaluate(led)}["mechanism_pointers_complete"])

    def test_pointer_extra_red(self):
        led = copy.deepcopy(self.led)
        led["mechanism_pointers"]["额外机制"] = "x"
        self.assertFalse({c["id"]: c["ok"] for c in pi.evaluate(led)}["mechanism_pointers_complete"])


class TestDiscover(unittest.TestCase):

    def test_ignores_unrelated_dirs(self):
        with tempfile.TemporaryDirectory() as td:
            os.makedirs(os.path.join(td, "not-a-repo"))
            _make_repo(td, "C01")
            found = pi.discover(td)
            self.assertEqual(len(found), 1)
            self.assertEqual(found[0]["repo"], "holoaeon-c01-demo")

    def test_flags_missing_ledger(self):
        with tempfile.TemporaryDirectory() as td:
            repo = _make_repo(td, "C02")
            os.remove(os.path.join(td, repo, "holoaeon_c02_demo", "ledger.json"))
            found = pi.discover(td)
            self.assertFalse(found[0]["has_ledger"])

    def test_missing_root_returns_empty(self):
        self.assertEqual(pi.discover(r"Z:\definitely\not\here"), [])


class TestAggregate(unittest.TestCase):

    def test_full_18_green(self):
        with tempfile.TemporaryDirectory() as td:
            for i in range(1, 19):
                _make_repo(td, "C%02d" % i)
            report = pi.aggregate(td)
            self.assertEqual(report["totals"]["repos"], 18)
            self.assertEqual(report["totals"]["green"], 18)
            self.assertEqual(report["totals"]["criteria_pass"], 108)
            self.assertEqual(report["totals"]["pointers"], 198)
            self.assertEqual(pi.check(report), [])

    def test_missing_repo_red(self):
        with tempfile.TemporaryDirectory() as td:
            _make_repo(td, "C01")
            report = pi.aggregate(td)
            fails = [f["id"] for f in pi.check(report)]
            self.assertIn("repo_missing", fails)

    def test_cang_gap_red(self):
        with tempfile.TemporaryDirectory() as td:
            for i in range(1, 18):
                _make_repo(td, "C%02d" % i)
            _make_repo(td, "C19")
            report = pi.aggregate(td)
            fails = [f["id"] for f in pi.check(report)]
            self.assertIn("cang_gap", fails)

    def test_duplicate_cang_red(self):
        with tempfile.TemporaryDirectory() as td:
            for i in range(1, 19):
                _make_repo(td, "C%02d" % i)
            p = os.path.join(td, "holoaeon-c18-demo", "holoaeon_c18_demo", "ledger.json")
            led = _ledger("C18")
            led["cang_id"] = "C01"
            with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(json.dumps(led, ensure_ascii=False))
            report = pi.aggregate(td)
            fails = [f["id"] for f in pi.check(report)]
            self.assertIn("cang_duplicate", fails)

    def test_report_has_no_absolute_path(self):
        with tempfile.TemporaryDirectory() as td:
            _make_repo(td, "C01")
            report = pi.aggregate(td)
            self.assertNotIn("F:\\", json.dumps(report, ensure_ascii=False))
            self.assertEqual(report["root_label"], os.path.basename(td))


class TestZeroCopy(unittest.TestCase):

    def test_clean_repo_ok(self):
        with tempfile.TemporaryDirectory() as td:
            _make_repo(td, "C03")
            repo = os.path.join(td, "holoaeon-c03-demo")
            self.assertTrue(pi.scan_zero_copy(repo)["ok"])

    def test_import_main_repo_red(self):
        with tempfile.TemporaryDirectory() as td:
            _make_repo(td, "C03")
            p = os.path.join(td, "holoaeon-c03-demo", "holoaeon_c03_demo", "bad.py")
            with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
                fh.write("from holoaeon import kernel\n")
            self.assertFalse(pi.scan_zero_copy(os.path.join(td, "holoaeon-c03-demo"))["ok"])

    def test_sys_path_into_main_red(self):
        with tempfile.TemporaryDirectory() as td:
            _make_repo(td, "C03")
            p = os.path.join(td, "holoaeon-c03-demo", "holoaeon_c03_demo", "bad2.py")
            with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
                fh.write("import sys\nsys.path.insert(0, r'F:\\doubaowork\\holoaeon')\n")
            self.assertFalse(pi.scan_zero_copy(os.path.join(td, "holoaeon-c03-demo"))["ok"])


class TestCheck(unittest.TestCase):

    def test_self_digest_detects_tamper(self):
        with tempfile.TemporaryDirectory() as td:
            for i in range(1, 19):
                _make_repo(td, "C%02d" % i)
            report = pi.aggregate(td)
            report["digest"] = "deadbeefdeadbeef"
            self.assertIn("self_digest", [f["id"] for f in pi.check(report)])

    def test_absolute_path_leak_detected(self):
        rep = {"repos": [], "totals": {}, "digest": ""}
        rep["leak"] = r"F:\doubaowork\holoaeon"
        self.assertTrue(pi._leak(rep))

    def test_zero_copy_surfaces_as_failure(self):
        with tempfile.TemporaryDirectory() as td:
            for i in range(1, 19):
                _make_repo(td, "C%02d" % i)
            bad = os.path.join(td, "holoaeon-c18-demo", "holoaeon_c18_demo", "bad.py")
            with io.open(bad, "w", encoding="utf-8", newline="\n") as fh:
                fh.write("import holoaeon\n")
            report = pi.aggregate(td)
            self.assertIn("zero_copy_violation", [f["id"] for f in pi.check(report)])

    def test_ok_flag_flips(self):
        with tempfile.TemporaryDirectory() as td:
            for i in range(1, 19):
                _make_repo(td, "C%02d" % i)
            self.assertTrue(pi.verify(td)["ok"])
            os.remove(os.path.join(td, "holoaeon-c09-demo", "holoaeon_c09_demo", "ledger.json"))
            self.assertFalse(pi.verify(td)["ok"])

    def test_verify_shape(self):
        with tempfile.TemporaryDirectory() as td:
            for i in range(1, 19):
                _make_repo(td, "C%02d" % i)
            out = pi.verify(td)
            self.assertIn("failures", out)
            self.assertIn("report", out)
            self.assertIn("digest", out["report"])


class TestRealSite(unittest.TestCase):
    """真实 18 仓站点：目录不在则整组 skip，绝不假装跑过。"""

    @classmethod
    def setUpClass(cls):
        if not os.path.isdir(REAL_ROOT):
            raise unittest.SkipTest("真实站点不存在")
        cls.out = pi.verify(REAL_ROOT)

    def test_real_18_repos(self):
        self.assertEqual(self.out["report"]["totals"]["repos"], 18)

    def test_real_all_green(self):
        self.assertTrue(self.out["ok"], json.dumps(self.out["failures"], ensure_ascii=False)[:400])
        self.assertEqual(self.out["report"]["totals"]["green"], 18)

    def test_real_criteria_and_pointers(self):
        self.assertEqual(self.out["report"]["totals"]["criteria_pass"], 108)
        self.assertEqual(self.out["report"]["totals"]["pointers"], 198)

    def test_real_cang_ids_contiguous(self):
        ids = [r["cang_id"] for r in self.out["report"]["repos"]]
        self.assertEqual(ids, ["C%02d" % i for i in range(1, 19)])

    def test_real_digest_stable(self):
        again = pi.aggregate(REAL_ROOT)
        self.assertEqual(again["digest"], self.out["report"]["digest"])
        self.assertEqual(self.out["report"]["digest"], "9265369717e254d5")


if __name__ == "__main__":
    unittest.main()
