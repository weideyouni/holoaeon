# -*- coding: utf-8 -*-
"""V70 测试：判据三档 / selftest 三层证据 / B4 点单闸门

分三类：
- 现场类（skipUnless 本机三处证据在位）：把真值逐项钉住，口径漂了当场红；
- 合成类（不依赖外界）：只证明四失败面真的能红，不证明数据正确；
- 纪律类：零写入、危险调用零命中、DOC 与冻结维度不变。
"""
import io
import json
import os
import re
import unittest

from holoaeon import prehistory_criteria as pc
from holoaeon import spec

ROOT = r"F:\doubaowork"
EVI = os.path.join(ROOT, "_规划局_20261112")
STATIC_JSON = os.path.join(EVI, "selftest静态审查_22实例.json")
RUN_JSON = os.path.join(EVI, "selftest实跑_22实例.json")
LEDGER_JSON = r"F:\doubaowork\holoaeon_lathe\prehistory_ledger_V68.json"
MOD = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "holoaeon", "prehistory_criteria.py")

HAVE_SITE = all(os.path.exists(p) for p in (STATIC_JSON, RUN_JSON, LEDGER_JSON))


def _load(p):
    with io.open(p, encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------- 合成夹具
SYN_STATIC = [
    {"zip": "a.zip", "asserts": 10, "danger": []},
    {"zip": "b.zip", "asserts": 0, "danger": []},
    {"zip": "c.zip", "asserts": 5, "danger": []},
]
SYN_RUN = [
    {"zip": "a.zip", "rc": 0, "state": "pass", "sec": 1.0},
    {"zip": "b.zip", "rc": 0, "state": "pass", "sec": 1.0},
    {"zip": "c.zip", "rc": 0, "state": "pass", "sec": 1.0},
]
SYN_B4 = [
    {"name": "x", "files": 10, "mb": 1.0, "three_state": "SUSPENDED", "first_batch": False},
    {"name": "y", "files": 20, "mb": 2.0, "three_state": "SUSPENDED", "first_batch": False},
]


class TiersLogic(unittest.TestCase):
    """判据计算的纯逻辑（合成名单，不依赖磁盘）。"""

    def test_union_superset_of_both(self):
        names = ["1331x1331_A", "矩阵实战化_B", "矩阵V3_C", "多智能体矩阵_D", "无条件_E"]
        t = pc.tiers(names)
        self.assertEqual(sorted(t["union"]), sorted(["1331x1331_A", "矩阵实战化_B", "矩阵V3_C", "多智能体矩阵_D"]))
        self.assertEqual(t["count"]["v1"], 4)
        self.assertEqual(t["count"]["v68"], 2)   # 矩阵V3_C / 多智能体矩阵_D 不含 1331 也不含「矩阵实战化」

    def test_v68_matches_bare_1331(self):
        names = ["alpha1331", "beta1331x1331", "gamma"]
        t = pc.tiers(names)
        self.assertEqual(t["count"]["v68"], 2)
        self.assertEqual(t["count"]["v1"], 1)
        self.assertEqual(t["only_in_199"], ["alpha1331"])

    def test_v1_only_case(self):
        names = ["类硅基生命V2.0_1331x131基座", "疾病图谱融合矩阵V3实战化"]
        t = pc.tiers(names)
        self.assertEqual(t["count"]["v1"], 1)
        self.assertEqual(t["only_in_194"], ["疾病图谱融合矩阵V3实战化"])

    def test_fingerprint_is_order_insensitive(self):
        self.assertEqual(pc.set_fingerprint(["b", "a", "c"]), pc.set_fingerprint(["c", "a", "b"]))

    def test_fingerprint_changes_on_member_change(self):
        self.assertNotEqual(pc.set_fingerprint(["a", "b"]), pc.set_fingerprint(["a", "b", "c"]))

    def test_count_drift_fires(self):
        names = ["1331x1331_only_one"]
        t = pc.tiers(names)
        ok, problems = pc.check_tiers(t)
        self.assertFalse(ok)
        self.assertTrue(any("criteria_drift" in p for p in problems))

    def test_set_drift_fires(self):
        names = ["1331x1331_A"]
        t = pc.tiers(names)
        ok, problems = pc.check_tiers(t)
        self.assertFalse(ok)
        self.assertTrue(any("set_drift" in p for p in problems))

    def test_diff_drift_fires(self):
        names = ["1331x1331_A"]
        t = pc.tiers(names)
        t["count"] = dict(pc.EXPECT_COUNT)
        t["intersection"] = pc.EXPECT_INTERSECTION
        t["only_in_199"] = []
        t["only_in_194"] = []
        t["set_sha16"] = pc.EXPECT_SET_SHA16
        ok, problems = pc.check_tiers(t)
        self.assertFalse(ok)
        self.assertTrue(any("diff_drift" in p for p in problems))

    def test_expect_tables_are_self_consistent(self):
        # 三档数字关系：194 + 7 = 199 + 2 = 201
        self.assertEqual(pc.EXPECT_COUNT["v1"] + len(pc.EXPECT_ONLY_IN_199), 201)
        self.assertEqual(pc.EXPECT_COUNT["v68"] + len(pc.EXPECT_ONLY_IN_194), 201)
        self.assertEqual(pc.EXPECT_COUNT["union"], 201)
        self.assertEqual(pc.EXPECT_COUNT["v1"], 194)
        self.assertEqual(pc.EXPECT_COUNT["v68"], 199)


class SelftestLayers(unittest.TestCase):
    """三层证据的函数逻辑（合成夹具）。"""

    def test_layers_counts(self):
        s = pc.selftest_layers(SYN_STATIC, SYN_RUN)
        self.assertEqual(s["total"], 3)
        self.assertEqual(s["L1"], 3)
        self.assertEqual(s["L2"], 3)
        self.assertEqual(s["L3"], 2)          # b.zip 领断言，不计 L3
        self.assertEqual(s["zero_assert"], ["b.zip"])

    def test_total_drift_fires_on_synthetic(self):
        s = pc.selftest_layers(SYN_STATIC, SYN_RUN)
        ok, problems = pc.check_selftest(s)
        self.assertFalse(ok)
        self.assertTrue(any("total_drift" in p for p in problems))

    def test_l3_overclaim_fires(self):
        s = pc.selftest_layers(SYN_STATIC, SYN_RUN)
        s["L3"] = s["L2"] + 5
        ok, problems = pc.check_selftest(s)
        self.assertFalse(ok)
        self.assertTrue(any("l3_overclaim" in p for p in problems))

    def test_rc_nonzero_fires(self):
        s = pc.selftest_layers(SYN_STATIC, SYN_RUN)
        s["rc_nonzero"] = ["c.zip"]
        ok, problems = pc.check_selftest(s)
        self.assertFalse(ok)
        self.assertTrue(any("rc_nonzero" in p for p in problems))

    def test_danger_fires(self):
        s = pc.selftest_layers(SYN_STATIC, SYN_RUN)
        s["danger_any"] = ["a.zip"]
        ok, problems = pc.check_selftest(s)
        self.assertFalse(ok)
        self.assertTrue(any("danger_calls" in p for p in problems))

    def test_unregistered_zero_fires(self):
        s = pc.selftest_layers(SYN_STATIC, SYN_RUN)
        s["zero_assert"] = ["b.zip", "d.zip"]
        ok, problems = pc.check_selftest(s)
        self.assertFalse(ok)
        self.assertTrue(any("unregistered_zero_assert" in p for p in problems))

    def test_known_exception_missing_fires(self):
        s = pc.selftest_layers(SYN_STATIC, SYN_RUN)
        s["zero_assert"] = []
        ok, problems = pc.check_selftest(s)
        self.assertFalse(ok)
        self.assertTrue(any("known_exception_missing" in p for p in problems))

    def test_asserts_sum_drift_fires(self):
        s = pc.selftest_layers(SYN_STATIC, SYN_RUN)
        s["asserts_sum"] = 1
        ok, problems = pc.check_selftest(s)
        self.assertFalse(ok)
        self.assertTrue(any("asserts_sum_drift" in p for p in problems))


class B4Gate(unittest.TestCase):
    """B4 闸门：未点单不许进第一批。"""

    def test_count_drift_fires(self):
        ok, problems = pc.check_b4(SYN_B4)
        self.assertFalse(ok)
        self.assertTrue(any("b4_count_drift" in p for p in problems))

    def test_files_drift_fires(self):
        rows = [dict(r) for r in SYN_B4] * 5      # 10 行
        rows = rows[:9]
        ok, problems = pc.check_b4(rows)
        self.assertFalse(ok)
        self.assertTrue(any("b4_files_drift" in p for p in problems))

    def test_illegal_state_fires(self):
        rows = [dict(r) for r in SYN_B4] * 5
        rows = rows[:9]
        rows[0]["three_state"] = "MAYBE"
        ok, problems = pc.check_b4(rows)
        self.assertFalse(ok)
        self.assertTrue(any("illegal_state" in p for p in problems))

    def test_unauthorized_touch_fires(self):
        rows = [dict(r) for r in SYN_B4] * 5
        rows = rows[:9]
        rows[0]["three_state"] = "SUSPENDED"
        rows[0]["first_batch"] = True
        ok, problems = pc.check_b4(rows)
        self.assertFalse(ok)
        self.assertTrue(any("unauthorized_touch" in p for p in problems))

    def test_authorized_allows_first_batch(self):
        rows = [dict(r) for r in SYN_B4] * 5
        rows = rows[:9]
        rows[0]["three_state"] = "AUTHORIZED"
        rows[0]["first_batch"] = True
        ok, _ = pc.check_b4(rows)
        # 仍会因 totals 不符而红，但 authorized_touch 不该出现
        problems_detail = pc.check_b4(rows)[1]
        self.assertFalse(any("unauthorized_touch" in p for p in problems_detail))

    def test_point_sheet_default_all_suspended(self):
        rows = [dict(r) for r in SYN_B4] * 5
        rows = rows[:9]
        sheet = pc.point_sheet(rows)
        self.assertEqual(len(sheet), 9)
        self.assertTrue(all(x["state"] == "SUSPENDED" for x in sheet))

    def test_point_sheet_respects_authorization_map(self):
        rows = [dict(r) for r in SYN_B4] * 5
        rows = rows[:9]
        sheet = pc.point_sheet(rows, {"x": "AUTHORIZED", "y": "EXCLUDED"})
        by_name = {x["name"]: x for x in sheet}
        self.assertEqual(by_name["x"]["state"], "AUTHORIZED")
        self.assertEqual(by_name["y"]["state"], "EXCLUDED")
        default_sheet = pc.point_sheet(rows)
        self.assertIn("未点单", default_sheet[0]["action"])

    def test_states_vocabulary_frozen(self):
        self.assertEqual(set(pc.B4_STATES), {"AUTHORIZED", "EXCLUDED", "SUSPENDED"})


class ReportShape(unittest.TestCase):

    def _rep(self, t=None, s=None, b4=None):
        t = t or pc.tiers(["1331x1331_A"])
        s = s or pc.selftest_layers(SYN_STATIC, SYN_RUN)
        b4 = b4 or SYN_B4
        return pc.build_report(t, s, b4, note="unit")

    def test_keys(self):
        rep = self._rep()
        self.assertEqual(set(rep.keys()),
                         {"schema", "version", "criteria", "tiers", "selftest",
                          "b4", "stop_states", "note", "report_digest"})

    def test_digest_stable(self):
        self.assertEqual(self._rep()["report_digest"], self._rep()["report_digest"])

    def test_digest_changes_when_member_changes(self):
        a = pc.build_report(pc.tiers(["1331x1331_A"]), pc.selftest_layers(SYN_STATIC, SYN_RUN), SYN_B4)
        b = pc.build_report(pc.tiers(["1331x1331_B"]), pc.selftest_layers(SYN_STATIC, SYN_RUN), SYN_B4)
        self.assertNotEqual(a["report_digest"], b["report_digest"])

    def test_tamper_fails_self_digest(self):
        rep = self._rep()
        rep["b4"]["count"] = 7
        ok, problems = pc.verify_report(rep)
        self.assertFalse(ok)
        self.assertTrue(any("self_digest" in p or "b4_count" in p for p in problems))

    def test_stop_states_declared(self):
        rep = self._rep()
        self.assertEqual(rep["stop_states"]["H1_B4"], "SUSPENDED")
        self.assertEqual(rep["stop_states"]["H2_criteria"], "RESOLVED")
        self.assertEqual(rep["stop_states"]["H3_selftest"], "RESOLVED")
        self.assertIn("REMOVED", rep["stop_states"]["H4_S3"])

    def test_no_wallclock_in_report(self):
        text = json.dumps(self._rep(), ensure_ascii=False)
        self.assertIsNone(re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", text))


class SourceDiscipline(unittest.TestCase):
    """静态纪律：本模块不写盘、不联网、不调外部进程。"""

    @classmethod
    def setUpClass(cls):
        with io.open(MOD, encoding="utf-8") as fh:
            cls.src = fh.read()

    def test_no_writers(self):
        for bad in ("open(..., 'w')", "open(...,\"w\")", "os.remove", "os.rename",
                    "shutil.rmtree", "os.rmdir", "os.makedirs"):
            self.assertNotIn(bad, self.src)
        self.assertNotIn("'w'", self.src)
        self.assertNotIn('"w"', self.src)

    def test_no_danger_calls(self):
        for bad in ("subprocess", "socket", "urllib", "requests",
                    "eval(", "exec(", "__import__"):
            self.assertNotIn(bad, self.src)
        # re.compile 是判据本身，不是危险调用：先摘掉它再查裸 compile(
        self.assertNotIn("compile(", self.src.replace("re.compile(", ""))

    def test_reads_dir_only(self):
        self.assertIn("os.scandir", self.src)
        self.assertIn("follow_symlinks=False", self.src)


class DocAndDimensions(unittest.TestCase):

    def test_doc_version_bumped(self):
        self.assertEqual(spec.DOC_VERSION, "0.9.70")  # V77

    def test_version_frozen(self):
        self.assertEqual(spec.VERSION, "0.9.1")

    def test_pack_order_frozen(self):
        from holoaeon import packs
        self.assertEqual(len(packs.PACK_ORDER), 9)
        self.assertGreaterEqual(len(packs.EXTRA_PACK_ORDER), 19)


@unittest.skipUnless(HAVE_SITE, "本机缺三处证据文件，跳过真盘校验")
class RealSite(unittest.TestCase):
    """现场类：真值逐项钉住。口径一变即红。"""

    @classmethod
    def setUpClass(cls):
        cls.names, cls.note = pc.scan_tier_names(ROOT)
        cls.t = pc.tiers(cls.names)
        cls.static = _load(STATIC_JSON)
        cls.run_rows = _load(RUN_JSON)
        cls.s = pc.selftest_layers(cls.static, cls.run_rows)
        cls.b4 = pc.b4_candidates(_load(LEDGER_JSON))

    def test_scan_nonempty(self):
        self.assertGreater(len(self.names), 100, "顶层目录数异常，判据失去意义")

    def test_three_counts(self):
        self.assertEqual(self.t["count"], pc.EXPECT_COUNT)

    def test_intersection_192(self):
        self.assertEqual(self.t["intersection"], 192)

    def test_set_sha16(self):
        self.assertEqual(self.t["set_sha16"], pc.EXPECT_SET_SHA16)

    def test_diff_rosters(self):
        self.assertEqual(sorted(self.t["only_in_199"]), sorted(pc.EXPECT_ONLY_IN_199))
        self.assertEqual(sorted(self.t["only_in_194"]), sorted(pc.EXPECT_ONLY_IN_194))

    def test_tiers_check_passes(self):
        ok, problems = pc.check_tiers(self.t)
        self.assertTrue(ok, problems)

    def test_selftest_layers(self):
        self.assertEqual(self.s["total"], 22)
        self.assertEqual(self.s["L1"], 22)
        self.assertEqual(self.s["L2"], 22)
        self.assertEqual(self.s["L3"], 21)
        self.assertEqual(self.s["asserts_sum"], 1410)
        self.assertEqual(self.s["asserts_min"], 0)
        self.assertEqual(self.s["asserts_max"], 96)
        self.assertEqual(self.s["zero_assert"], [pc.KNOWN_ZERO_ASSERT])

    def test_selftest_check_passes(self):
        ok, problems = pc.check_selftest(self.s)
        self.assertTrue(ok, problems)

    def test_b4_counts(self):
        sm = pc.b4_summary(self.b4)
        self.assertEqual(sm["count"], 9)
        self.assertEqual(sm["files"], 119157)
        self.assertEqual(sm["mb"], 10166.9)

    def test_b4_all_suspended_and_out_of_batch(self):
        self.assertEqual(set(r["three_state"] for r in self.b4), {"SUSPENDED"})
        self.assertEqual([r["name"] for r in self.b4 if r["first_batch"]], [])

    def test_b4_check_passes(self):
        ok, problems = pc.check_b4(self.b4)
        self.assertTrue(ok, problems)

    def test_biggest_three_by_mb(self):
        top = [r["name"] for r in self.b4[:3]]
        self.assertEqual(top[0:2], ["_历史工程归档_20261017", "本地养分摄入重构_20261011"])

    def test_report_verifies(self):
        rep = pc.build_report(self.t, self.s, self.b4, note="real-site")
        ok, problems = pc.verify_report(rep)
        self.assertTrue(ok, problems)

    def test_report_digest_reproducible(self):
        a = pc.build_report(self.t, self.s, self.b4, note="real-site")["report_digest"]
        b = pc.build_report(self.t, self.s, self.b4, note="real-site")["report_digest"]
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
