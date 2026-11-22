# -*- coding: utf-8 -*-
"""V84 · 恒真判据常驻金哨（tautology_scan A 口径 + 白名单登记账 + v3_gate 第 34 面 A14）。

投喂包：AGENT_FEED_V84_TAUTOLOGY_GOLDEN_WATCH_20261114.md（§5）
- 静态检测只能判 B 口径（字面常量比较）；未登记命中 = 待复核，不等于已判定为病
- 白名单是登记账：缺 liveness / 条目过期 / 摘要不符 → 红
- 扫描器自检含双方 v1 教训：链式比较拆错边（25 处）、常量环境过宽（16 处）

金丝雀 C1–C8 覆盖「防倒退」与「防误伤」两个方向。
"""

import ast
import io
import json
import os
import tempfile
import unittest

from holoaeon import tautology_scan as S

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _scan_src(src):
    return S.scan_source(src, "(test)", {})


# --------------------------------------------------------------- 1 报告总貌
class TestScanReport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rep = S.scan()

    def test_a1_ok(self):
        self.assertTrue(self.rep["ok"], self.rep.get("drift"))

    def test_a2_hits_total_is_eight(self):
        self.assertEqual(self.rep["hits_total"], 8)

    def test_a3_allowlisted_all_eight(self):
        self.assertEqual(len(self.rep["allowlisted"]), 8)
        self.assertEqual(self.rep["unregistered"], [])

    def test_a4_drift_empty(self):
        self.assertEqual(self.rep["drift"], [])
        self.assertEqual(self.rep["liveness_missing"], [])

    def test_a5_digest_ok(self):
        self.assertTrue(self.rep["digest"]["ok"])
        self.assertTrue(self.rep["digest"]["expected"])

    def test_a6_scope_and_caliber_note(self):
        self.assertIn("holoaeon/", self.rep["scope"])
        self.assertIn("scripts/ tests/", self.rep["scope"])
        self.assertIn("B 口径", self.rep["a_caliber_note"])
        self.assertIn("A 口径", self.rep["a_caliber_note"])
        self.assertEqual(self.rep["seal"], S.TAUTOLOGY_SEAL)


# --------------------------------------------------------------- 2 检测能力
class TestDetection(unittest.TestCase):
    def test_b1_numeric_eq_tautology(self):
        h = _scan_src("C = 0.7\n\ndef f():\n    return C >= 0.7\n")
        self.assertEqual(len(h), 1)
        self.assertEqual(h[0]["kind"], "dead_always_true")

    def test_b2_numeric_eq_kind(self):
        h = _scan_src("C = 1331\n\ndef f():\n    return C == 1331\n")
        self.assertEqual(h[0]["kind"], "tautology_eq")

    def test_b3_always_false(self):
        h = _scan_src('A = "x"\n\ndef f():\n    return A == "y"\n')
        self.assertEqual(h[0]["kind"], "dead_always_false")

    def test_b4_local_const_dict(self):
        src = ('def f():\n    sims = {"P2xP3": 0.7}\n'
               '    return sims["P2xP3"] >= 0.7\n')
        h = _scan_src(src)
        self.assertEqual(len(h), 1)
        self.assertEqual(h[0]["kind"], "dead_always_true")

    def test_b5_membership_in_dict(self):
        src = 'D = {"images": 1}\n\ndef f():\n    return "images" in D\n'
        h = _scan_src(src)
        self.assertEqual(h[0]["kind"], "membership_in_const")

    def test_b6_membership_in_str(self):
        src = 'TXT = "abc"\n\ndef f():\n    return "b" in TXT\n'
        h = _scan_src(src)
        self.assertEqual(h[0]["kind"], "membership_in_const")

    def test_b7_unresolvable_call_not_hit(self):
        src = "def g():\n    return 1\n\ndef f():\n    return g() == 1\n"
        self.assertEqual(_scan_src(src), [])


# --------------------------------------------------------------- 3 常量环境收紧（C5 同族）
class TestConstEnvTightening(unittest.TestCase):
    def test_c1_parameter_not_const(self):
        src = 'def f(mode):\n    return mode == "stagnation_first"\n'
        self.assertEqual(_scan_src(src), [])

    def test_c2_parameter_default_not_const(self):
        src = 'def f(mode="stagnation_first"):\n    return mode == "stagnation_first"\n'
        self.assertEqual(_scan_src(src), [])

    def test_c3_for_target_not_const(self):
        src = "def f():\n    for i in [1, 2]:\n        if i == 1:\n            return 1\n    return 0\n"
        self.assertEqual(_scan_src(src), [])

    def test_c4_with_target_not_const(self):
        src = "def f(h):\n    with h() as fh:\n        return fh == 1\n"
        self.assertEqual(_scan_src(src), [])

    def test_c5_multi_assign_not_const(self):
        src = "def f():\n    x = 0\n    x = 1\n    return x == 1\n"
        self.assertEqual(_scan_src(src), [])

    def test_c6_comprehension_target_not_const(self):
        src = "def f():\n    return [i == 1 for i in [1, 2]]\n"
        self.assertEqual(_scan_src(src), [])


# --------------------------------------------------------------- 4 白名单匹配
class TestAllowlistMatching(unittest.TestCase):
    ENTRIES = [{"id": "X1", "file": "holoaeon/a.py", "line": 10,
                "category": "presence_check", "expr": "K == 1",
                "anchors": ["K==1"], "liveness": "改 K 即变"}]

    def _hit(self, line, expr="K == 1", file="holoaeon/a.py"):
        return {"file": file, "line": line, "expr": expr}

    def test_d1_same_line_matches(self):
        self.assertEqual(S.match_hit(self._hit(10), self.ENTRIES)["id"], "X1")

    def test_d2_tolerance_five_ok_six_not(self):
        self.assertEqual(S.match_hit(self._hit(15), self.ENTRIES)["id"], "X1")
        self.assertIsNone(S.match_hit(self._hit(16), self.ENTRIES))

    def test_d3_other_file_no_match(self):
        self.assertIsNone(S.match_hit(self._hit(10, file="holoaeon/b.py"), self.ENTRIES))

    def test_d4_anchor_mismatch_no_match(self):
        self.assertIsNone(S.match_hit(self._hit(10, expr="K == 2"), self.ENTRIES))


# --------------------------------------------------------------- 5 漂移 / 活性 / 摘要
class TestDriftAndDigest(unittest.TestCase):
    def _doc(self, **over):
        d = {"schema": S.ALLOWLIST_SCHEMA, "as_of": "2026-11-14",
             "entries": [{"id": "X1", "file": "holoaeon/a.py", "line": 10,
                          "category": "presence_check", "expr": "K == 1",
                          "anchors": ["K==1"], "liveness": "改 K 即变"}]}
        d.update(over)
        d["self_digest"] = S.canonical_digest(d)
        return d

    def _scan_with(self, doc):
        tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        try:
            json.dump(doc, tmp, ensure_ascii=False)
            tmp.close()
            return S.scan(allowlist_path=tmp.name)
        finally:
            try:
                os.unlink(tmp.name)
            except OSError:
                pass

    def test_e1_valid_doc_digest_ok(self):
        doc = self._doc()
        self.assertEqual(S.canonical_digest(doc), doc["self_digest"])

    def test_e2_tampered_doc_digest_mismatch(self):
        doc = self._doc()
        doc["as_of"] = "2026-11-15"
        self.assertNotEqual(S.canonical_digest(doc), doc["self_digest"])

    def test_e3_missing_liveness_flagged(self):
        doc = self._doc()
        doc["entries"][0]["liveness"] = ""
        doc["self_digest"] = S.canonical_digest(doc)
        rep = self._scan_with(doc)
        self.assertEqual(rep["liveness_missing"], ["X1"])
        self.assertFalse(rep["ok"])

    def test_e4_stale_entry_drift(self):
        doc = self._doc()
        doc["entries"][0]["line"] = 10   # 指向不存在锚 → 无命中 → drift
        doc["entries"][0]["anchors"] = ["Z==999"]
        doc["self_digest"] = S.canonical_digest(doc)
        rep = self._scan_with(doc)
        self.assertEqual([d["id"] for d in rep["drift"]], ["X1"])
        self.assertFalse(rep["ok"])

    def test_e5_bad_category_drift(self):
        doc = self._doc()
        doc["entries"][0]["category"] = "waived"
        doc["self_digest"] = S.canonical_digest(doc)
        rep = self._scan_with(doc)
        self.assertTrue(any("category" in d["why"] for d in rep["drift"]))
        self.assertFalse(rep["ok"])


# --------------------------------------------------------------- 6 扫描器自检（C4/C5）
class TestScannerSelfcheck(unittest.TestCase):
    def test_f1_selfcheck_ok(self):
        sc = S._selfcheck()
        self.assertTrue(sc["ok"], sc["failures"])
        self.assertEqual(sc["failures"], [])

    def test_f2_chain_no_false_positive(self):
        got = {c["name"]: c["got"] for c in S._selfcheck()["cases"]}
        self.assertEqual(got["chain_no_false_positive"], 0)

    def test_f3_param_default_no_false_positive(self):
        got = {c["name"]: c["got"] for c in S._selfcheck()["cases"]}
        self.assertEqual(got["param_default_not_const"], 0)

    def test_f4_for_target_no_false_positive(self):
        got = {c["name"]: c["got"] for c in S._selfcheck()["cases"]}
        self.assertEqual(got["for_target_not_const"], 0)

    def test_f5_multi_assign_no_false_positive(self):
        got = {c["name"]: c["got"] for c in S._selfcheck()["cases"]}
        self.assertEqual(got["multi_assign_not_const"], 0)

    def test_f6_with_target_no_false_positive(self):
        got = {c["name"]: c["got"] for c in S._selfcheck()["cases"]}
        self.assertEqual(got["with_target_not_const"], 0)

    def test_f7_genuine_tautology_detected(self):
        got = {c["name"]: c["got"] for c in S._selfcheck()["cases"]}
        self.assertEqual(got["genuine_tautology_detected"], 1)

    def test_f8_local_dict_and_membership_detected(self):
        got = {c["name"]: c["got"] for c in S._selfcheck()["cases"]}
        self.assertEqual(got["local_const_dict_detected"], 1)
        self.assertEqual(got["membership_detected"], 1)


# --------------------------------------------------------------- 7 v3_gate 第 34 面挂接
class TestV3Face(unittest.TestCase):
    def setUp(self):
        self.p = os.path.join(ROOT, "scripts", "v3_gate.py")
        with io.open(self.p, encoding="utf-8") as fh:
            self.src = fh.read()

    def test_g1_a14_function_present(self):
        self.assertIn("def a14_tautology_watch", self.src)
        self.assertIn('check("A14.1"', self.src)

    def test_g2_a14_called_in_main(self):
        tree = ast.parse(self.src)
        names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
        self.assertIn("a14_tautology_watch", names)

    def test_g3_module_docstring_mentions_a14(self):
        self.assertIn("A1–A14", self.src)


# --------------------------------------------------------------- 8 金丝雀 C1–C8
class TestCanaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rep = S.scan()
        cls.entries = json.load(io.open(
            os.path.join(ROOT, "data", "tautology_allowlist.json"), encoding="utf-8"))["entries"]

    def _hit_at(self, needle_file, needle_line):
        for h in self.rep["hits"]:
            if h["file"] == needle_file and h["line"] == needle_line:
                return h
        raise AssertionError("未找到命中 %s:%s" % (needle_file, needle_line))

    def test_c1_new_tautology_is_unregistered(self):
        """C1：造一处新恒真（未登记）→ 必须被判为未登记。"""
        h = _scan_src("CONST_A = 0.7\n\ndef f():\n    return CONST_A >= 0.7\n")
        self.assertEqual(len(h), 1)
        self.assertIsNone(S.match_hit(h[0], self.entries))

    def test_c2_entry_removed_leaves_hit_unregistered(self):
        """C2：删白名单一条而代码仍在 → 该命中变未登记（红）。行号从登记簿回读，不写死。"""
        e = next(x for x in self.entries if x["id"] == "T04")
        hit = self._hit_at("holoaeon/packs/topology_resonance_pack.py", e["line"])
        kept = [x for x in self.entries if x["id"] != "T04"]
        self.assertIsNone(S.match_hit(hit, kept))

    def test_c3_tamper_byte_breaks_digest(self):
        """C3：改白名单一字节不重算摘要 → 摘要不符（红）。"""
        doc = {"schema": S.ALLOWLIST_SCHEMA,
               "entries": [dict(e) for e in self.entries]}
        doc["self_digest"] = S.canonical_digest(doc)
        good = S.canonical_digest(doc)
        doc["entries"][0]["liveness"] = doc["entries"][0]["liveness"] + " "
        self.assertNotEqual(S.canonical_digest(doc), good)

    def test_c4_chain_compare_no_false_positive(self):
        """C4：`0 <= x <= 1` 型零误报（四人组 v1 曾 25 处假阳）。"""
        self.assertEqual(_scan_src("def f(x):\n    return 0 <= x <= 1\n"), [])

    def test_c5_const_env_three_classes_no_false_positive(self):
        """C5：参数默认值 / for 目标 / 二次赋值——三类零误判（执行端 v1 曾 16 处假阳）。"""
        self.assertEqual(_scan_src(
            'def f(m="a"):\n    for i in [1]:\n        if i == 1 and m == "a":\n            return 1\n'
            "    x = 1\n    x = 2\n    return x == 2\n"), [])

    def test_c6_missing_liveness_detected_by_scan(self):
        """C6：条目缺 liveness → 红（登记账不容空活性来源）。"""
        doc = {"schema": S.ALLOWLIST_SCHEMA,
               "entries": [{"id": "T01", "file": "x", "line": 1,
                            "category": "presence_check", "expr": "a",
                            "anchors": ["a"], "liveness": ""}]}
        doc["self_digest"] = S.canonical_digest(doc)
        tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        try:
            json.dump(doc, tmp, ensure_ascii=False)
            tmp.close()
            rep = S.scan(allowlist_path=tmp.name)
        finally:
            try:
                os.unlink(tmp.name)
            except OSError:
                pass
        self.assertIn("T01", rep["liveness_missing"])
        self.assertFalse(rep["ok"])

    def test_c7_line_drift_beyond_tolerance(self):
        """C7：行锚超 ±5 → 不再匹配（防误伤/防漏配）。"""
        hit = self._hit_at("holoaeon/packs/subdistill_pack.py", 468)
        moved = [dict(e) for e in self.entries]
        for e in moved:
            if e["id"] == "T02":
                e["line"] = 468 + 6
        self.assertIsNone(S.match_hit(hit, moved))

    def test_c8_eight_legit_uses_not_red(self):
        """C8：8 处正当用途登记后必须静默通过（误伤即这条要拦的）。"""
        self.assertTrue(self.rep["ok"])
        self.assertEqual(len(self.rep["allowlisted"]), 8)
        self.assertEqual(self.rep["unregistered"], [])


# --------------------------------------------------------------- 9 跨批判据活性与在位
class TestCrossBatch(unittest.TestCase):
    def test_h1_v82_predicate_is_live(self):
        from holoaeon.packs import quartet_director_pack as Q
        r = Q.check_emergence(0.9, 0.9, 0.2, 0.3)
        self.assertFalse(r["emergence"])

    def test_h2_v83_sick_sample_still_3482(self):
        from holoaeon.packs import topology_resonance_pack as T
        r = T.quartet_tensor("0.9", "0.9", "0.2", "0.3")
        self.assertEqual(r["p23_similarity"], 0.3482)

    def test_h3_v83_compat_anchor_still_true(self):
        from holoaeon.packs import topology_resonance_pack as T
        r = T.quartet_tensor("0.85", "0.85", "0.85", "0.30")
        self.assertTrue(r["emergence"])

    def test_h4_allowlist_entries_unique_and_enumerated(self):
        doc = json.load(io.open(
            os.path.join(ROOT, "data", "tautology_allowlist.json"), encoding="utf-8"))
        ids = [e["id"] for e in doc["entries"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(e["category"] in ("invariant_selfcheck", "config_dispatch",
                                              "presence_check") for e in doc["entries"]))
        self.assertTrue(all(e["liveness"].strip() for e in doc["entries"]))


# --------------------------------------------------------------- 10 DOC 同步
class TestDocSync(unittest.TestCase):
    def test_i1_doc_version_is_0978(self):
        from holoaeon import spec
        self.assertEqual(spec.DOC_VERSION, "0.9.89")  # V89-I MR-V8 同批重钉

    def test_i2_allowlist_batch_is_v84(self):
        doc = json.load(io.open(
            os.path.join(ROOT, "data", "tautology_allowlist.json"), encoding="utf-8"))
        self.assertEqual(doc["batch"], "V84")
        self.assertEqual(doc["schema"], "TAUTOLOGY-ALLOWLIST-v1")

    def test_i3_spec_comment_mentions_batch(self):
        """DOC_VERSION 行必须标注批号（V##）——批号不写死，防升号漏标。"""
        with io.open(os.path.join(ROOT, "holoaeon", "spec.py"), encoding="utf-8") as fh:
            lines = [ln for ln in fh.read().splitlines() if ln.startswith("DOC_VERSION")]
        self.assertTrue(lines, "spec.py 缺 DOC_VERSION 行")
        self.assertRegex(lines[0], r"#\s*V\d{2}")


if __name__ == "__main__":
    unittest.main()
