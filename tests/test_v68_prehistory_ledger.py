# -*- coding: utf-8 -*-
"""V68 测试：史前资产指针总账（PL-1）+ V3 runtime 骨架契约包（PL-2）

六组：
1. 判据可复算（classify 优先级与证据位）
2. 体量统计与指纹口径（files/mb / sha16 / meta_sha16）
3. 建账与 V1 分类继承（只许改判活设施）
4. 可失败判据（篡改/缺件/污染/自校验）
5. 骨架契约机制（缺 19 位即 FAIL / 零断言即 FAIL / 交集不足即 FAIL）
6. 零副作用 + 维度与 DOC 同源
"""
import io
import json
import os
import shutil
import tempfile
import unittest
import zipfile

from holoaeon import prehistory_contract as pc
from holoaeon import prehistory_ledger as pl


def _write(path, text):
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def _write_csv(path, rows):
    import csv
    fieldnames = ["name", "kind", "cls", "sub", "files", "mb", "first", "why"]
    with io.open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})


class TestClassify(unittest.TestCase):
    """组 1：判据优先级 —— 活设施 > HARD_A > B > SOFT_A > C"""

    def test_active_infra_first(self):
        c = pl.classify("vector-sea", "dir")
        self.assertEqual((c["cls"], c["sub"]), (pl.CLS_A, "A2_活体同步设施"))

    def test_active_infra_sync_state(self):
        c = pl.classify(".sync_state", "dir")
        self.assertEqual(c["sub"], "A2_活体同步设施")

    def test_hard_a_repo(self):
        c = pl.classify("holoaeon", "dir")
        self.assertEqual((c["cls"], c["sub"]), (pl.CLS_A, "A0_项目本体"))

    def test_hard_a_feed(self):
        c = pl.classify("AGENT_FEED_V68_X.md", "file")
        self.assertEqual(c["sub"], "A1_关联素材与实验田")

    def test_runtime_zip_is_b1(self):
        c = pl.classify("吴门医派1331x1331_SUPER-MAS-V3.0_runtime_20261018.zip", "file")
        self.assertEqual(c["sub"], "B1_runtime硬核")

    def test_matrix_dir_is_b2(self):
        c = pl.classify("吴门医派1331x1331", "dir")
        self.assertEqual(c["sub"], "B2_矩阵实战化目录")

    def test_history_book_is_b3(self):
        c = pl.classify("计算机语言通史", "dir")
        self.assertEqual(c["sub"], "B3_史前文档")

    def test_archive_is_b4(self):
        c = pl.classify("_历史工程归档_20261017", "dir")
        self.assertEqual((c["cls"], c["sub"]), (pl.CLS_B, "B4_归档与镜像"))

    def test_soft_a_tmp(self):
        c = pl.classify(".tmp_v55_cluster", "dir")
        self.assertEqual((c["cls"], c["sub"]), (pl.CLS_A, "A1_关联素材与实验田"))

    def test_unknown_is_c1(self):
        c = pl.classify("mystery.bin", "file")
        self.assertEqual((c["cls"], c["sub"]), (pl.CLS_C, "C1_未判定"))

    def test_every_verdict_carries_why(self):
        for name, kind in (("vector-sea", "dir"), ("holoaeon", "dir"),
                           ("x_runtime_1.zip", "file"), ("mystery", "file")):
            c = pl.classify(name, kind)
            self.assertTrue(c["why"], "判据必须留证据位: %s" % name)


class TestPropsFingerprint(unittest.TestCase):
    """组 2：体量统计与两种指纹口径"""

    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="v68_props_")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_props_single_file(self):
        p = os.path.join(self.root, "a.txt")
        _write(p, "abcd")
        self.assertEqual(pl.props(p), (1, 4))

    def test_props_dir_recursive(self):
        _write(os.path.join(self.root, "d", "x.txt"), "12")
        _write(os.path.join(self.root, "d", "sub", "y.txt"), "345")
        files, nbytes = pl.props(os.path.join(self.root, "d"))
        self.assertEqual((files, nbytes), (2, 5))

    def test_file_fingerprint_is_sha16(self):
        p = os.path.join(self.root, "a.txt")
        _write(p, "hello")
        kind, val = pl.fingerprint(p)
        self.assertEqual(kind, "sha16")
        self.assertEqual(len(val), 16)

    def test_dir_fingerprint_is_meta_sha16(self):
        p = os.path.join(self.root, "d")
        _write(os.path.join(p, "a.txt"), "hello")
        kind, val = pl.fingerprint(p)
        self.assertEqual(kind, "meta_sha16")
        self.assertEqual(len(val), 16)

    def test_dir_fingerprint_stable(self):
        p = os.path.join(self.root, "d")
        _write(os.path.join(p, "a.txt"), "hello")
        self.assertEqual(pl.fingerprint(p), pl.fingerprint(p))

    def test_dir_fingerprint_changes_on_new_file(self):
        p = os.path.join(self.root, "d")
        _write(os.path.join(p, "a.txt"), "hello")
        before = pl.fingerprint(p)
        _write(os.path.join(p, "b.txt"), "world")
        self.assertNotEqual(before, pl.fingerprint(p))


class TestBuildLedger(unittest.TestCase):
    """组 3：建账 —— 条目守恒、V1 继承、活设施唯一改判"""

    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="v68_ledger_")
        _write(os.path.join(self.root, "holoaeon_demo", "x.txt"), "1")
        _write(os.path.join(self.root, "AGENT_FEED_V68_X.md"), "2")
        _write(os.path.join(self.root, "foo_1331_runtime_20261018.zip"), "3")
        _write(os.path.join(self.root, "某派1331x1331", "y.txt"), "4")
        _write(os.path.join(self.root, "计算机语言通史.md"), "5")
        _write(os.path.join(self.root, "_历史工程归档_2026", "z.txt"), "6")
        _write(os.path.join(self.root, "vector-sea", "w.txt"), "7")
        _write(os.path.join(self.root, ".tmp_v99", "q.txt"), "8")
        _write(os.path.join(self.root, "mystery.bin"), "9")
        self.csv = os.path.join(self.root, "_v1.csv")
        _write_csv(self.csv, [
            {"name": "holoaeon_demo", "kind": "dir", "cls": pl.CLS_A, "sub": "A0_项目本体"},
            {"name": "vector-sea", "kind": "dir", "cls": pl.CLS_B, "sub": "B4_归档与镜像"},
            {"name": "_历史工程归档_2026", "kind": "dir", "cls": pl.CLS_B, "sub": "B4_归档与镜像"},
            {"name": "foo_1331_runtime_20261018.zip", "kind": "file", "cls": pl.CLS_B, "sub": "B1_runtime硬核"},
        ])
        self.led = pl.build_ledger(self.root, deep=True, csv_path=self.csv)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_entry_count_matches_top_level(self):
        on_disk = {e.name for e in os.scandir(self.root)}
        names = {x["name"] for x in self.led["entries"]}
        self.assertEqual(names, on_disk)

    def test_inherits_v1_classification(self):
        e = next(x for x in self.led["entries"] if x["name"] == "_历史工程归档_2026")
        self.assertEqual(e["sub"], "B4_归档与镜像")
        self.assertFalse(e["reclassified"])

    def test_active_infra_reclassified_out(self):
        e = next(x for x in self.led["entries"] if x["name"] == "vector-sea")
        self.assertEqual(e["cls"], pl.CLS_A)
        self.assertEqual(e["sub"], "A2_活体同步设施")
        self.assertTrue(e["reclassified"])

    def test_first_batch_subset_is_b1_b2_b3_b5(self):
        for x in self.led["entries"]:
            if x["first_batch"]:
                self.assertIn(x["sub"], pl.FIRST_BATCH_SUBS)

    def test_summary_counts_self_consistent(self):
        s = self.led["summary"]
        self.assertEqual(s["total"], sum(s["by_cls"].values()))
        self.assertEqual(s["total"], len(self.led["entries"]))
        self.assertEqual(s["total"], s["first_batch"]["items"] + s["suspended"]["items"])

    def test_reclassified_only_active_infra(self):
        self.assertEqual(self.led["summary"]["reclassified"], 1)

    def test_package_digest_non_empty(self):
        self.assertEqual(len(self.led["package_sha256"]), 64)

    def test_criteria_written_into_ledger(self):
        c = self.led["criteria"]
        self.assertIn("vector-sea", c["active_infra"])
        self.assertEqual(c["priority"][0], "ACTIVE_INFRA")
        self.assertEqual(self.led["schema"], pl.LEDGER_SCHEMA)


class TestVerifyLedger(unittest.TestCase):
    """组 4：可失败判据 —— 四条独立失败面"""

    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="v68_verify_")
        _write(os.path.join(self.root, "foo_runtime_1.zip"), "abc")
        _write(os.path.join(self.root, "vector-sea", "w.txt"), "7")
        self.led = pl.build_ledger(self.root, deep=True)
        self.ok, self.problems = pl.verify_ledger(self.led, self.root)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_clean_ledger_passes(self):
        self.assertTrue(self.ok)
        self.assertEqual(self.problems, [])

    def test_summary_edit_detected_by_digest(self):
        bad = json.loads(json.dumps(self.led))
        bad["summary"]["total"] += 1
        ok, p = pl.verify_ledger(bad, self.root)
        self.assertFalse(ok)
        self.assertTrue(any("package_sha256" in x for x in p))

    def test_missing_entry_on_disk_detected(self):
        bad = json.loads(json.dumps(self.led))
        bad["entries"].append({"name": "not_there", "kind": "file", "cls": pl.CLS_C,
                               "sub": "C1_未判定", "files": 0, "mb": 0.0, "first_batch": False})
        bad["package_sha256"] = pl.digest(bad)
        ok, p = pl.verify_ledger(bad, self.root)
        self.assertFalse(ok)
        self.assertTrue(any("missing on disk" in x for x in p))

    def test_fingerprint_drift_detected(self):
        bad = json.loads(json.dumps(self.led))
        for x in bad["entries"]:
            if x.get("first_batch"):
                x["meta_sha16"] = "0" * 16
                x["sha16"] = "0" * 16
        bad["package_sha256"] = pl.digest(bad)
        ok, p = pl.verify_ledger(bad, self.root)
        self.assertFalse(ok)
        self.assertTrue(any("fingerprint drift" in x for x in p))

    def test_active_infra_in_b_class_detected(self):
        bad = json.loads(json.dumps(self.led))
        for x in bad["entries"]:
            if x["name"] == "vector-sea":
                x["cls"] = pl.CLS_B
        bad["package_sha256"] = pl.digest(bad)
        ok, p = pl.verify_ledger(bad, self.root)
        self.assertFalse(ok)
        self.assertTrue(any("active infra" in x for x in p))

    def test_repo_path_leak_detected(self):
        bad = json.loads(json.dumps(self.led))
        bad["entries"].append({"name": "holoaeon/x.py", "kind": "file", "cls": pl.CLS_A,
                               "sub": "A0_项目本体", "files": 1, "mb": 0.0, "first_batch": False})
        bad["package_sha256"] = pl.digest(bad)
        ok, p = pl.verify_ledger(bad, self.root)
        self.assertFalse(ok)
        self.assertTrue(any("repo path leaked" in x for x in p))

    def test_schema_change_detected(self):
        bad = json.loads(json.dumps(self.led))
        bad["schema"] = "SOMETHING-ELSE"
        bad["package_sha256"] = pl.digest(bad)
        ok, p = pl.verify_ledger(bad, self.root)
        self.assertFalse(ok)
        self.assertTrue(any("schema mismatch" in x for x in p))


def _mk_zip(path, files):
    """files: {name: source}"""
    with zipfile.ZipFile(path, "w") as z:
        for n, src in files.items():
            z.writestr(n, src)


_BASE_SRC = "def build_result():\n    return 1\n\n\ndef match_cases():\n    return []\n"
_MAIN_SRC = "def main():\n    return 0\n"
_SELFTEST_2 = "def run_selftest():\n    assert 1 == 1\n    assert 2 == 2\n    return 2\n"
_SELFTEST_0 = "def run_selftest():\n    # G1 G2 G3\n    return 0\n"


class TestContractMechanism(unittest.TestCase):
    """组 5：骨架契约 —— 缺位/零断言/交集不足都必须是 FAIL"""

    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="v68_contract_")
        _mk_zip(os.path.join(self.root, "a1331x1331_SUPER-MAS-V3.0_runtime_20261018.zip"),
                {"pkg/_base.py": _BASE_SRC, "pkg/main.py": _MAIN_SRC, "pkg/selftest.py": _SELFTEST_2})
        _mk_zip(os.path.join(self.root, "b1331x1331_SUPER-MAS-V3.0_runtime_20261018.zip"),
                {"pkg/_base.py": _BASE_SRC, "pkg/main.py": _MAIN_SRC, "pkg/selftest.py": _SELFTEST_0})
        self.con = pc.build_contract(self.root)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_instances_found(self):
        self.assertEqual(self.con["summary"]["instances"], 2)

    def test_entries_and_py_counted(self):
        self.assertEqual(self.con["summary"]["entries"], 6)
        self.assertEqual(self.con["summary"]["py"], 6)

    def test_assert_counts_per_instance(self):
        counts = [r["asserts"] for r in self.con["instances"]]
        self.assertEqual(sorted(counts), [0, 2])

    def test_shared_defs_intersection(self):
        self.assertEqual(self.con["shared_defs"]["_base.py"], ["build_result", "match_cases"])
        self.assertEqual(self.con["shared_defs"]["main.py"], ["main"])
        self.assertIn("run_selftest", self.con["shared_defs"].get("selftest.py", []))

    def test_missing_isomorphic_reported(self):
        rec = self.con["instances"][0]
        self.assertTrue(rec["missing_isomorphic"])
        self.assertNotIn("_base.py", rec["missing_isomorphic"])

    def test_instance_count_mismatch_fails(self):
        ok, p = pc.verify_contract(self.con)
        self.assertFalse(ok)
        self.assertTrue(any("instances" in x for x in p))

    def test_unknown_zero_assert_fails(self):
        bad = json.loads(json.dumps(self.con))
        bad["summary"]["unknown_zero_assert"] = ["b1331x1331...zip"]
        bad["package_sha256"] = pc.digest(bad)
        ok, p = pc.verify_contract(bad)
        self.assertFalse(ok)
        self.assertTrue(any("zero-assert" in x for x in p))

    def test_shared_defs_below_min_fails(self):
        bad = json.loads(json.dumps(self.con))
        bad["summary"]["shared_defs_total"] = 3
        bad["package_sha256"] = pc.digest(bad)
        ok, p = pc.verify_contract(bad)
        self.assertFalse(ok)
        self.assertTrue(any("shared defs" in x for x in p))

    def test_assert_sum_below_min_fails(self):
        bad = json.loads(json.dumps(self.con))
        bad["summary"]["assert_sum"] = 2
        bad["package_sha256"] = pc.digest(bad)
        ok, p = pc.verify_contract(bad)
        self.assertFalse(ok)
        self.assertTrue(any("assert sum" in x for x in p))

    def test_instance_digest_tamper_fails(self):
        bad = json.loads(json.dumps(self.con))
        bad["instances"][0]["asserts"] = 99
        ok, p = pc.verify_contract(bad)
        self.assertFalse(ok)
        self.assertTrue(any("package_sha256" in x for x in p))


@unittest.skipUnless(os.path.isdir(r"F:\\doubaowork"), "本机无 doubaowork 根，跳过真盘冒烟")
class TestRealDiskSmoke(unittest.TestCase):
    """真盘冒烟：22 实例 / 19 位全在 / 65 交集 / 0 断言实例已登记"""

    @classmethod
    def setUpClass(cls):
        cls.con = pc.build_contract(r"F:\\doubaowork")

    def test_22_instances(self):
        self.assertEqual(self.con["summary"]["instances"], 22)

    def test_19_isomorphic_names_all_present(self):
        for r in self.con["instances"]:
            self.assertEqual(r["missing_isomorphic"], [], r["zip"])

    def test_shared_defs_at_least_65(self):
        self.assertGreaterEqual(self.con["summary"]["shared_defs_total"], 65)

    def test_zero_assert_instance_is_registered(self):
        self.assertEqual(len(self.con["summary"]["zero_assert_instances"]), 1)
        self.assertEqual(self.con["summary"]["unknown_zero_assert"], [])

    def test_verify_passes_on_real_disk(self):
        ok, problems = pc.verify_contract(self.con, r"F:\\doubaowork")
        self.assertTrue(ok, problems)


class TestNoSideEffects(unittest.TestCase):
    """组 6a：只读纪律 —— 两条模块不得含写入/改名/删除/子进程/网络调用"""

    FORBIDDEN = ("os.remove", "os.rename", "os.replace", "shutil", "subprocess",
                 "socket", "os.system", "urllib", ".write(")

    def _src(self, mod):
        with io.open(mod.__file__, encoding="utf-8") as f:
            return f.read()

    def test_ledger_module_is_read_only(self):
        src = self._src(pl)
        for bad in self.FORBIDDEN:
            self.assertNotIn(bad, src, "ledger 模块出现副作用调用: %s" % bad)

    def test_contract_module_is_read_only(self):
        src = self._src(pc)
        for bad in self.FORBIDDEN:
            self.assertNotIn(bad, src, "contract 模块出现副作用调用: %s" % bad)

    def test_no_dynamic_exec(self):
        for mod in (pl, pc):
            src = self._src(mod)
            for bad in ("eval(", "exec(", "compile(", "__import__"):
                self.assertNotIn(bad, src, "%s 出现动态执行: %s" % (mod.__name__, bad))


class TestDocAndDimensions(unittest.TestCase):
    """组 6b：DOC 与冻结维度同源"""

    def test_doc_version_is_v68(self):
        from holoaeon import spec
        self.assertEqual(spec.DOC_VERSION, "0.9.62")

    def test_version_frozen(self):
        from holoaeon import spec
        self.assertEqual(spec.VERSION, "0.9.1")

    def test_pack_order_frozen(self):
        from holoaeon import packs
        self.assertEqual(len(packs.PACK_ORDER), 9)

    def test_extra_pack_order_lower_bound(self):
        from holoaeon import packs
        self.assertGreaterEqual(len(packs.EXTRA_PACK_ORDER), 19)


if __name__ == "__main__":
    unittest.main()
