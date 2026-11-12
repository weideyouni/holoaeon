# -*- coding: utf-8 -*-
"""V71 测试：史前矩阵族谱（PL-4）

七组：
1. 骨架签名原语（确定性 / 排序无关 / 排除隐藏件 / zip 与目录同口径）
2. 绝对路径与泄漏面（相对路径纪律 + 盘符即红）
3. L1 精确族（同骨架跨域双态 / 域内同族 / 母版规则）
4. L2 近亲族（Jaccard 连通分量 / 阈值 / 空集不制造假证据 / 证据字段）
5. 差异矩阵（增删改 / 可复算 / 母版错位即红）
6. 可失败判据七面（数字漂移 / 虚构血缘 / 母版缺失 / 孤儿差异 / 不可复算 / 摘要篡改）
7. 零副作用 + 真实现场（skipUnless）
"""
import io
import json
import os
import shutil
import tempfile
import unittest
import zipfile

from holoaeon import prehistory_family as pf


def _write(path, text, size_pad=0):
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
        if size_pad:
            f.write("x" * size_pad)


def _mk_zip(path, entries):
    """entries: [(name, content)]"""
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with zipfile.ZipFile(path, "w") as z:
        for name, content in entries:
            z.writestr(name, content)


class SkelTest(unittest.TestCase):
    """组 1：签名原语"""

    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="v71_skel_")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_signature_stable_across_runs(self):
        p = os.path.join(self.root, "a")
        _write(os.path.join(p, "x.py"), "print(1)")
        s1 = pf.skeleton(p)["sig"]
        s2 = pf.skeleton(p)["sig"]
        self.assertEqual(s1, s2)
        self.assertEqual(len(s1), 16)

    def test_signature_order_independent(self):
        a = os.path.join(self.root, "a")
        b = os.path.join(self.root, "b")
        for name in ("z.py", "a.py", "m/inside.py"):
            _write(os.path.join(a, name), "pass")
            _write(os.path.join(b, name), "pass")
        self.assertEqual(pf.skeleton(a)["sig"], pf.skeleton(b)["sig"])

    def test_size_change_breaks_signature(self):
        a = os.path.join(self.root, "a")
        b = os.path.join(self.root, "b")
        _write(os.path.join(a, "x.py"), "pass")
        _write(os.path.join(b, "x.py"), "pass", size_pad=10)
        self.assertNotEqual(pf.skeleton(a)["sig"], pf.skeleton(b)["sig"])

    def test_relative_path_only(self):
        p = os.path.join(self.root, "a")
        _write(os.path.join(p, "sub", "x.py"), "pass")
        items = pf.skeleton(p)["items"]
        for name, _size in items:
            self.assertFalse(name.startswith("/"))
            self.assertNotIn(":", name)
            self.assertNotIn("\\", name)

    def test_hidden_files_excluded(self):
        p = os.path.join(self.root, "a")
        _write(os.path.join(p, "x.py"), "pass")
        _write(os.path.join(p, ".gitkeep"), "")
        self.assertEqual(pf.skeleton(p)["files"], 1)

    def test_hidden_dir_excluded(self):
        p = os.path.join(self.root, "a")
        _write(os.path.join(p, "x.py"), "pass")
        _write(os.path.join(p, ".git", "config"), "x")
        self.assertEqual(pf.skeleton(p)["files"], 1)

    def test_zip_skeleton_matches_dir_skeleton(self):
        p = os.path.join(self.root, "a")
        _write(os.path.join(p, "x.py"), "pass")
        z = os.path.join(self.root, "a.zip")
        _mk_zip(z, [("x.py", "pass")])
        self.assertEqual(pf.skeleton(p)["sig"], pf.skeleton(z)["sig"])

    def test_zip_macosx_excluded(self):
        z = os.path.join(self.root, "a.zip")
        _mk_zip(z, [("x.py", "pass"), ("__MACOSX/._x.py", "junk")])
        self.assertEqual(pf.skeleton(z)["files"], 1)

    def test_cap_truncates(self):
        p = os.path.join(self.root, "a")
        for i in range(8):
            _write(os.path.join(p, "f%d.py" % i), "pass")
        rec = pf.dir_skeleton(p, cap=3)
        self.assertTrue(rec["capped"])
        self.assertEqual(rec["files"], 3)

    def test_unsupported_artefact_raises(self):
        p = os.path.join(self.root, "a.txt")
        _write(p, "x")
        with self.assertRaises(ValueError):
            pf.skeleton(p)


class FamilyTest(unittest.TestCase):
    """组 2-5：聚族、近亲、差异"""

    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="v71_fam_")
        self.a = os.path.join(self.root, "a")
        self.b = os.path.join(self.root, "b")
        self.c = os.path.join(self.root, "c")
        for name in ("main.py", "spec.py", "heartbeat.py"):
            _write(os.path.join(self.a, name), "pass")
            _write(os.path.join(self.b, name), "pass")
        # c 与 b 名字重叠但多一个文件
        _write(os.path.join(self.c, "main.py"), "pass")
        _write(os.path.join(self.c, "spec.py"), "pass")
        _write(os.path.join(self.c, "extra.py"), "pass")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_same_skeleton_same_group(self):
        recs = [pf.skeleton(self.a), pf.skeleton(self.b)]
        groups = pf.cluster(recs)
        self.assertEqual(len(groups), 1)
        self.assertEqual(len(list(groups.values())[0]), 2)

    def test_pick_master_prefers_more_files(self):
        m = pf.pick_master([
            {"name": "one", "files": 3, "bytes": 100},
            {"name": "two", "files": 5, "bytes": 100},
        ])
        self.assertEqual(m["name"], "two")

    def test_pick_master_tie_prefers_larger_bytes(self):
        m = pf.pick_master([
            {"name": "one", "files": 3, "bytes": 100},
            {"name": "two", "files": 3, "bytes": 200},
        ])
        self.assertEqual(m["name"], "two")

    def test_pick_master_tie_prefers_shorter_name(self):
        m = pf.pick_master([
            {"name": "a-very-long-name", "files": 3, "bytes": 100},
            {"name": "s", "files": 3, "bytes": 100},
        ])
        self.assertEqual(m["name"], "s")

    def test_diff_detects_added(self):
        ma = {"name": "a", "items": [("x.py", 10)]}
        ch = {"name": "c", "items": [("x.py", 10), ("y.py", 5)]}
        d = pf.diff_matrix(ma, ch)
        self.assertEqual(d["added"], ["y.py"])
        self.assertEqual(d["added_count"], 1)

    def test_diff_detects_removed(self):
        ma = {"name": "a", "items": [("x.py", 10), ("z.py", 3)]}
        ch = {"name": "c", "items": [("x.py", 10)]}
        d = pf.diff_matrix(ma, ch)
        self.assertEqual(d["removed"], ["z.py"])

    def test_diff_detects_resized(self):
        ma = {"name": "a", "items": [("x.py", 10)]}
        ch = {"name": "c", "items": [("x.py", 99)]}
        d = pf.diff_matrix(ma, ch)
        self.assertEqual(d["resized"], [["x.py", 10, 99]])

    def test_diff_reproducible(self):
        ma = {"name": "a", "items": [("x.py", 10), ("y.py", 2)]}
        ch = {"name": "c", "items": [("x.py", 10), ("z.py", 5)]}
        d1 = pf.diff_matrix(ma, ch)
        d2 = pf.diff_matrix(ma, ch)
        self.assertEqual(d1["diff_sha16"], d2["diff_sha16"])

    def test_jaccard_identical(self):
        self.assertEqual(pf.jaccard_sets({"a", "b"}, {"a", "b"}), 1.0)

    def test_jaccard_partial(self):
        self.assertAlmostEqual(pf.jaccard_sets({"a", "b"}, {"a", "c"}), 1.0 / 3.0, places=4)

    def test_jaccard_empty_is_zero_not_one(self):
        self.assertEqual(pf.jaccard_sets(set(), {"a"}), 0.0)

    def test_components_group_by_names(self):
        recs = [pf.skeleton(self.b), pf.skeleton(self.c)]
        comps, pairs = pf.components(recs, threshold=0.5)
        self.assertEqual(len(pairs), 1)
        self.assertEqual(len(comps), 1)
        self.assertGreaterEqual(pairs[0]["jaccard"], 0.5)

    def test_components_threshold_excludes_far(self):
        d = os.path.join(self.root, "d")
        for name in ("m1.py", "m2.py", "m3.py"):
            _write(os.path.join(d, name), "pass")
        e = os.path.join(self.root, "e")
        _write(os.path.join(e, "zzz.py"), "pass")
        comps, pairs = pf.components([pf.skeleton(d), pf.skeleton(e)], threshold=0.5)
        self.assertEqual(len(pairs), 0)
        self.assertEqual(len(comps), 2)

    def test_cross_scope_not_compared(self):
        recs = [pf.skeleton(self.a), pf.skeleton(self.c)]
        comps, pairs = pf.components(recs, threshold=0.1)
        self.assertEqual(len(pairs), 1)


class CheckTest(unittest.TestCase):
    """组 6：可失败判据"""

    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="v71_chk_")
        self.a = os.path.join(self.root, "a")
        self.b = os.path.join(self.root, "b")
        for name in ("main.py", "spec.py"):
            _write(os.path.join(self.a, name), "pass")
            _write(os.path.join(self.b, name), "pass")
        self.z = os.path.join(self.root, "a_runtime.zip")
        _mk_zip(self.z, [("main.py", "pass"), ("spec.py", "pass")])
        self.dir_paths = [self.a, self.b]
        self.zip_paths = [self.z]
        self.report = self._build()

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def _build(self):
        """先建一次拿真值，再把期望常量钉成小样本值后重建（避免大数字常量挡住结构测试）。"""
        first = pf.build_family(self.root, dir_paths=self.dir_paths, zip_paths=self.zip_paths)
        s = first["summary"]
        import unittest.mock as mock
        patcher = mock.patch.multiple(
            pf,
            EXPECTED_DIRS=s["dirs"], EXPECTED_ZIPS=s["zips"],
            EXPECTED_FILES=s["files"], EXPECTED_BYTES=s["bytes"],
            EXPECTED_EXACT_FAMILIES=s["exact_families"],
            EXPECTED_SINGLETONS=s["singletons"],
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        return pf.build_family(self.root, dir_paths=self.dir_paths, zip_paths=self.zip_paths)

    def test_clean_report_passes(self):
        ok, problems = pf.check_family(self.report)
        self.assertTrue(ok, problems)

    def test_counts_registered(self):
        s = self.report["summary"]
        self.assertEqual(s["dirs"], 2)
        self.assertEqual(s["zips"], 1)
        self.assertEqual(s["exact_families"], 1)   # a + b + zip 同骨架
        self.assertEqual(s["singletons"], 0)

    def test_schema_drift_fails(self):
        bad = dict(self.report)
        bad["schema"] = "WRONG"
        ok, problems = pf.check_family(bad)
        self.assertFalse(ok)
        self.assertIn("schema mismatch", problems)

    def test_file_total_drift_fails(self):
        bad = json.loads(json.dumps(self.report))
        bad["summary"]["files"] += 1
        ok, problems = pf.check_family(bad)
        self.assertFalse(ok)
        self.assertIn("files", " ".join(problems))

    def test_phantom_lineage_fails(self):
        bad = json.loads(json.dumps(self.report))
        bad["families"][0]["members"] = [os.path.basename(self.a), "not-exist"]
        ok, problems = pf.check_family(bad)
        self.assertFalse(ok)

    def test_master_missing_fails(self):
        bad = json.loads(json.dumps(self.report))
        bad["families"][0]["master"] = "ghost"
        ok, problems = pf.check_family(bad)
        self.assertFalse(ok)
        self.assertIn("master missing", " ".join(problems))

    def test_master_rule_violation_fails(self):
        bad = json.loads(json.dumps(self.report))
        members = bad["families"][0]["members"]
        # 选一个不是最优的成员当母版
        bad["families"][0]["master"] = sorted(members)[-1] if len(members) > 1 else members[0]
        worst = pf.pick_master([{"name": m, "files": 1, "bytes": 1} for m in members])
        if worst["name"] != bad["families"][0]["master"]:
            ok, problems = pf.check_family(bad)
            self.assertFalse(ok)

    def test_orphan_diff_fails(self):
        bad = json.loads(json.dumps(self.report))
        bad["families"][0]["diffs"] = []
        ok, problems = pf.check_family(bad)
        self.assertFalse(ok)
        self.assertIn("orphan diff", " ".join(problems))

    def test_diff_not_reproducible_fails(self):
        bad = json.loads(json.dumps(self.report))
        bad["families"][0]["diffs"][0]["diff_sha16"] = "deadbeefdeadbeef"
        ok, problems = pf.check_family(bad)
        self.assertFalse(ok)
        self.assertIn("diff not reproducible", " ".join(problems))

    def test_near_evidence_missing_fails(self):
        bad = json.loads(json.dumps(self.report))
        bad["near_families"] = [{
            "family_id": "near-x", "scope": "dir", "size": 2, "jaccard_min": 1.0,
            "master": os.path.basename(self.a),
            "members": [os.path.basename(self.a), os.path.basename(self.b)],
            "diffs": [], "content_verified": False,
        }]
        ok, problems = pf.check_family(bad)
        self.assertFalse(ok)
        self.assertIn("evidence", " ".join(problems))

    def test_near_content_verified_true_fails(self):
        bad = json.loads(json.dumps(self.report))
        bad["near_families"] = [{
            "family_id": "near-x", "scope": "dir", "size": 2, "jaccard_min": 1.0,
            "evidence": pf.NEAR_EVIDENCE, "content_verified": True,
            "master": os.path.basename(self.a),
            "members": [os.path.basename(self.a), os.path.basename(self.b)],
            "diffs": [],
        }]
        ok, problems = pf.check_family(bad)
        self.assertFalse(ok)
        self.assertIn("content_verified=False", " ".join(problems))

    def test_absolute_path_leak_fails(self):
        bad = json.loads(json.dumps(self.report))
        bad["records"][0]["items"].append([r"F:\doubaowork\x.py", 10])
        ok, problems = pf.check_family(bad)
        self.assertFalse(ok)
        self.assertIn("leaks absolute path", " ".join(problems))

    def test_digest_tamper_fails(self):
        bad = json.loads(json.dumps(self.report))
        bad["note"] = "edited"
        ok, problems = pf.check_family(bad)
        self.assertFalse(ok)
        self.assertIn("family_digest mismatch", " ".join(problems))

    def test_capped_object_fails(self):
        bad = json.loads(json.dumps(self.report))
        bad["summary"]["capped_objects"] = ["x"]
        ok, problems = pf.check_family(bad)
        self.assertFalse(ok)
        self.assertIn("file cap", " ".join(problems))


class RealSiteTest(unittest.TestCase):
    """组 7：真实现场（本机 F:\\doubaowork 才跑）"""

    ROOT = r"F:\doubaowork"

    @unittest.skipUnless(os.path.isdir(r"F:\doubaowork"), "needs local site")
    def test_real_site_build_passes(self):
        report = pf.build_family(self.ROOT)
        ok, problems = pf.check_family(report)
        self.assertTrue(ok, problems[:6])
        s = report["summary"]
        self.assertEqual(s["dirs"], 194)
        self.assertEqual(s["zips"], 22)
        self.assertEqual(s["files"], 8277)
        self.assertEqual(s["bytes"], 98484518)
        self.assertEqual(s["exact_families"], 14)
        self.assertEqual(s["singletons"], 188)
        self.assertGreaterEqual(s["near_families"], 1)

    @unittest.skipUnless(os.path.isdir(r"F:\doubaowork"), "needs local site")
    def test_real_site_twin_is_cross_scope(self):
        report = pf.build_family(self.ROOT)
        for f in report["families"]:
            self.assertEqual(f["kind"], "twin")
            self.assertEqual(f["scopes"], ["dir", "zip"])

    @unittest.skipUnless(os.path.isdir(r"F:\doubaowork"), "needs local site")
    def test_real_site_near_declares_not_verified(self):
        report = pf.build_family(self.ROOT)
        for f in report["near_families"]:
            self.assertFalse(f["content_verified"])
            self.assertEqual(f["evidence"], pf.NEAR_EVIDENCE)


if __name__ == "__main__":
    unittest.main()
