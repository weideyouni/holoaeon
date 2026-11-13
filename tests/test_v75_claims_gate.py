# -*- coding: utf-8 -*-
"""V75 · claims_gate 测试（九组 ≥35 例）。

每组对应块 C 的一面判据或一条契约；七面各有一只金丝雀，先证会红再谈可信。
测试不依赖仓库当前状态：基准绿用注入的 ctx（临时根 + 伪造 README + 临时回执），
只有「注册簿结构」与「真实包链位覆盖」两处直接读仓内真件。
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

from holoaeon import claims_gate as cg  # noqa: E402

README_ZH_OK = """# Demo
![Tests](https://img.shields.io/badge/tests-1778%2B11%2B21%20passed-success.svg)
- **领域编排闸门（环数以 `python -m holoaeon.claims_gate report` 回读为准）**：全环功能见附录
- **工程验收（本机实跑口径）**：主套单测 **1778 OK** + v3 域 **11** + verax 域 **21**（合计 **1810**）· 复算闸 **4 条 0 不匹配**
| 门禁 | `v3_gate 32/32` · `unittest 1778 OK` · `redline 3 文件 0 违规` |
**批次数不写死**，一律以台账回读为准。
包内 .py 以 `find holoaeon -name '*.py' | wc -l` 回读。
**2026-10 → 今 · 版本号以回读为准（不写死）。**
"""

README_EN_OK = """# Demo
[![Tests](https://img.shields.io/badge/tests-1778%2B11%2B21%20passed-success.svg)](#-testing)
- **Gates (measured on this machine)**: main suite **1778 OK** + v3 domain **11** + verax domain **21** (**1810** total)
**2026-10 → present — version is a readback of the ledger, never hardcoded.**
"""


def _mk_fixture():
    root = tempfile.mkdtemp(prefix="v75_claims_")
    pkg = os.path.join(root, "holoaeon")
    os.makedirs(pkg)
    # 3 个 .py：与回执 redline=3 对齐（递归口径）
    with io.open(os.path.join(pkg, "spec.py"), "w", encoding="utf-8", newline="\n") as f:
        f.write('# -*- coding: utf-8 -*-\n"""spec"""\nDOC_VERSION = "0.9.68"\n')
    for i in range(2):
        with io.open(os.path.join(pkg, "mod%d.py" % i), "w", encoding="utf-8", newline="\n") as f:
            f.write('# -*- coding: utf-8 -*-\n"""mod"""\nX = 1\n')
    with io.open(os.path.join(root, "SHA256SUMS"), "w", encoding="utf-8", newline="\n") as f:
        f.write("a  b\nc  d\ne  f\ng  h\n")
    os.makedirs(os.path.join(root, "reports"))
    with io.open(os.path.join(root, "reports", "v75_receipt.json"), "w",
                 encoding="utf-8", newline="\n") as f:
        json.dump({"verification": {"unittest_main": "1778 OK",
                                    "redline": "3 文件 0 违规"},
                   "doc_version": "0.9.68"}, f)
    texts = {"readme_zh": README_ZH_OK, "readme_en": README_EN_OK}
    return root, cg._ctx(root=root, texts=texts)


def _rehash(reg):
    reg = copy.deepcopy(reg)
    reg["self_digest"] = cg.self_digest(reg)
    return reg


class _Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root, cls.ctx = _mk_fixture()
        cls.reg = cg.load_registry()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.root, ignore_errors=True)

    def verify(self, reg=None, ctx=None, today=None):
        return cg.verify(reg if reg is not None else copy.deepcopy(self.reg),
                         ctx or self.ctx, today)

    def face(self, result, name):
        return result["faces"][name]


# =========================================================================
# 组 1 · 正向与加载
# =========================================================================
class TestLoad(_Base):
    def test_01_schema_constants(self):
        self.assertEqual(cg.SCHEMA, "CLAIMS-GATE-v1")
        self.assertEqual(cg.MAX_PIN_AGE_DAYS, 180)
        self.assertEqual(cg.REQUIRED_PIN_FIELDS,
                         ("doc_no", "version", "verified_at", "status"))
        self.assertEqual(cg.VALID_PIN_STATUS, ("current", "superseded", "unknown"))
        self.assertEqual(cg.VALID_CLAIM_KIND, ("current", "historical", "narrative"))
        self.assertGreaterEqual(len(cg.FACES), 9)  # V77 起 9 面；V79 起 10 面（下界断言防退化，不写死）

    def test_02_load_default_registry(self):
        reg = cg.load_registry()
        self.assertEqual(reg["schema"], cg.SCHEMA)
        self.assertTrue(reg["self_digest"])

    def test_03_totals_match_lists(self):
        reg = self.reg
        self.assertEqual(reg["totals"]["doc_claims"], len(reg["doc_claims"]))
        self.assertEqual(reg["totals"]["regulation_pins"], len(reg["regulation_pins"]))
        self.assertEqual(reg["totals"]["historical"],
                         sum(1 for x in reg["doc_claims"] if x["kind"] == "historical"))
        self.assertEqual(reg["totals"]["narrative"],
                         sum(1 for x in reg["doc_claims"] if x["kind"] == "narrative"))

    def test_04_claim_nine_fields(self):
        for item in self.reg["doc_claims"]:
            miss = [k for k in cg.REQUIRED_CLAIM_FIELDS if k not in item]
            self.assertEqual(miss, [], "缺字段: %s" % item.get("id"))

    def test_05_pin_four_fields_and_pointer(self):
        for pin in self.reg["regulation_pins"]:
            for k in cg.REQUIRED_PIN_FIELDS:
                self.assertTrue(pin.get(k), "%s 缺 %s" % (pin.get("id"), k))
            self.assertTrue(pin.get("source_pointer"))
            self.assertIn(pin["status"], cg.VALID_PIN_STATUS)


# =========================================================================
# 组 2 · current 回读一致
# =========================================================================
class TestReadback(_Base):
    def test_06_baseline_green(self):
        # V81 起注册簿含 README / 包内源码叙述位，必须用真实仓上下文回读；
        # fixture root 只有假 README，无法承载真实叙述位（否则本断言测的是假基线）。
        v = cg.verify(copy.deepcopy(self.reg))
        self.assertEqual(v["verdict"], "PASS", json.dumps(v["faces"], ensure_ascii=False)[:600])
        self.assertEqual(v["mismatch"], 0)

    def test_07_badge_tampered_goes_red(self):
        ctx = cg._ctx(root=self.ctx["root"], texts={
            "readme_zh": README_ZH_OK.replace("tests-1778", "tests-999"),
            "readme_en": README_EN_OK})
        v = self.verify(ctx=ctx)
        self.assertFalse(self.face(v, "readback_consistent")["ok"])
        ids = [f["id"] for f in self.face(v, "readback_consistent")["fails"]]
        self.assertIn("badge_tests_zh", ids)

    def test_08_gate_row_readback(self):
        self.assertEqual(cg.readback({"readback": "readme.zh.gate_unittest"}, self.ctx), 1778)

    def test_09_redline_computed_vs_receipt(self):
        self.assertEqual(cg.readback({"readback": "computed.py_recursive"}, self.ctx), 3)
        self.assertEqual(cg.readback({"readback": "computed.py_top"}, self.ctx), 3)
        exp = cg.resolve_expected({"expected_from": "receipt.verification.redline"}, self.ctx)
        self.assertEqual(cg._int_of(exp), 3)

    def test_10_checklist_entries_from_sums(self):
        self.assertEqual(cg.readback({"readback": "computed.sums_entries"}, self.ctx), 4)
        self.assertEqual(cg.readback({"readback": "readme.zh.checklist_entries"}, self.ctx), 4)

    def test_11_doc_version_readback(self):
        self.assertEqual(cg.readback({"readback": "spec.doc_version"}, self.ctx), "0.9.68")
        self.assertEqual(cg.resolve_expected(
            {"expected_from": "receipt.doc_version"}, self.ctx), "0.9.68")

    def test_12_receipt_missing_is_incomplete(self):
        root2, ctx2 = _mk_fixture()
        try:
            os.remove(os.path.join(root2, "reports", "v75_receipt.json"))
            v = self.verify(ctx=ctx2)
            self.assertFalse(self.face(v, "readback_consistent")["ok"])
            details = " ".join(f["detail"] for f in self.face(v, "readback_consistent")["fails"])
            self.assertIn("INCOMPLETE", details)
        finally:
            shutil.rmtree(root2, ignore_errors=True)


# =========================================================================
# 组 3 · historical 时点盒
# =========================================================================
class TestHistorical(_Base):
    def test_13_v46_note_timeboxed(self):
        item = [x for x in self.reg["doc_claims"] if x["id"] == "v46d_badge_note_zh"][0]
        self.assertEqual(item["kind"], "historical")
        self.assertEqual(item["as_of_batch"], "V46")
        self.assertTrue(item["timeboxed"])

    def test_14_drop_as_of_batch(self):
        reg = _rehash(self.reg)
        for x in reg["doc_claims"]:
            if x["id"] == "v46d_badge_note_zh":
                x["as_of_batch"] = ""
                x["timeboxed"] = False
        v = self.verify(reg=reg)
        self.assertFalse(self.face(v, "historical_timeboxed")["ok"])

    def test_15_timeboxed_false(self):
        reg = _rehash(self.reg)
        for x in reg["doc_claims"]:
            if x["id"] == "v73_suite_snapshot":
                x["timeboxed"] = False
        v = self.verify(reg=reg)
        ids = [f["id"] for f in self.face(v, "historical_timeboxed")["fails"]]
        self.assertIn("v73_suite_snapshot", ids)

    def test_16_historical_on_live_slot(self):
        reg = _rehash(self.reg)
        for x in reg["doc_claims"]:
            if x["id"] == "badge_tests_zh":
                x["kind"] = "historical"
                x["as_of_batch"] = "V46"
                x["timeboxed"] = True
        v = self.verify(reg=reg)
        self.assertFalse(self.face(v, "historical_timeboxed")["ok"])


# =========================================================================
# 组 4 · narrative 回读式
# =========================================================================
class TestNarrative(_Base):
    def test_17_three_narrative_claims(self):
        ids = [x["id"] for x in self.reg["doc_claims"] if x["kind"] == "narrative"]
        self.assertEqual(sorted(ids),
                         ["batch_count_zh", "en_timeline_version", "pyfiles_command_zh",
                          "ring_count_zh", "zh_timeline_version"])  # V77 增两条时间线叙述位

    def test_18_ring_written_as_literal(self):
        ctx = cg._ctx(root=self.ctx["root"], texts={
            "readme_zh": README_ZH_OK.replace(
                "环数以 `python -m holoaeon.claims_gate report` 回读为准", "二十四环"),
            "readme_en": README_EN_OK})
        v = self.verify(ctx=ctx)
        ids = [f["id"] for f in self.face(v, "readback_consistent")["fails"]]
        self.assertIn("ring_count_zh", ids)

    def test_19_batch_count_written_as_literal(self):
        ctx = cg._ctx(root=self.ctx["root"], texts={
            "readme_zh": README_ZH_OK.replace("**批次数不写死**，一律以台账回读为准。",
                                              "至今 V60，当前 77 条。"),
            "readme_en": README_EN_OK})
        v = self.verify(ctx=ctx)
        ids = [f["id"] for f in self.face(v, "readback_consistent")["fails"]]
        self.assertIn("batch_count_zh", ids)

    def test_20_pyfiles_command_must_be_find(self):
        ctx = cg._ctx(root=self.ctx["root"], texts={
            "readme_zh": README_ZH_OK.replace(
                "find holoaeon -name '*.py' | wc -l", "ls holoaeon/*.py | wc -l"),
            "readme_en": README_EN_OK})
        v = self.verify(ctx=ctx)
        ids = [f["id"] for f in self.face(v, "readback_consistent")["fails"]]
        self.assertIn("pyfiles_command_zh", ids)


# =========================================================================
# 组 5 · pin 四字段与状态
# =========================================================================
class TestPins(_Base):
    def test_21_six_pins(self):
        ids = sorted(p["id"] for p in self.reg["regulation_pins"])
        self.assertEqual(ids, ["MCP", "MLPS3", "NHSA-CATALOG", "PHARMACOPOEIA",
                               "PHC-2025", "PHC-NORM"])

    def test_22_missing_version(self):
        reg = _rehash(self.reg)
        reg["regulation_pins"][0]["version"] = ""
        v = self.verify(reg=reg)
        ids = [f["id"] for f in self.face(v, "regulation_pinned")["fails"]]
        self.assertIn("MCP", ids)

    def test_23_bad_status(self):
        reg = _rehash(self.reg)
        reg["regulation_pins"][1]["status"] = "latest"
        v = self.verify(reg=reg)
        self.assertFalse(self.face(v, "regulation_pinned")["ok"])

    def test_24_missing_pointer(self):
        reg = _rehash(self.reg)
        reg["regulation_pins"][5]["source_pointer"] = ""
        v = self.verify(reg=reg)
        ids = [f["id"] for f in self.face(v, "regulation_pinned")["fails"]]
        self.assertIn("MLPS3", ids)

    def test_25_unregistered_schemes_absent(self):
        ids = {p["id"] for p in self.reg["regulation_pins"]}
        for bad in ("SLSA", "CycloneDX", "SPDX", "AIIA/T", "Q/KXY"):
            self.assertNotIn(bad, ids)

    def test_26_mcp_has_dual_version_note(self):
        mcp = [p for p in self.reg["regulation_pins"] if p["id"] == "MCP"][0]
        self.assertIn("2026-07-28", mcp["version"])
        self.assertIn("2024-11-05", mcp["note"])


# =========================================================================
# 组 6 · freshness 与 unknown
# =========================================================================
class TestFreshness(_Base):
    def test_27_all_current_fresh(self):
        # 同上：真实注册簿 + 真实仓上下文（fixture 无法承载真实叙述位）；
        # today 不写死——写死会把「V81 当天登记的 verified_at」误判成未来日期。
        v = cg.verify(copy.deepcopy(self.reg))
        self.assertTrue(self.face(v, "pin_freshness")["ok"])
        self.assertTrue(self.face(v, "regulation_pinned")["ok"])

    def test_28_stale_pin(self):
        reg = _rehash(self.reg)
        reg["regulation_pins"][3]["verified_at"] = "2020-01-01"
        v = self.verify(reg=reg, today="2026-11-13")
        self.assertFalse(self.face(v, "pin_freshness")["ok"])
        details = " ".join(f["detail"] for f in self.face(v, "pin_freshness")["fails"])
        self.assertIn("STALE", details)

    def test_29_unknown_with_note_is_legal(self):
        reg = _rehash(self.reg)
        reg["regulation_pins"][2]["status"] = "unknown"
        reg["regulation_pins"][2]["note"] = "未核实现行版本，如实登记"
        v = self.verify(reg=reg, today="2026-11-13")
        self.assertTrue(self.face(v, "pin_freshness")["ok"])

    def test_30_unknown_without_note(self):
        reg = _rehash(self.reg)
        reg["regulation_pins"][2]["status"] = "unknown"
        reg["regulation_pins"][2]["note"] = ""
        v = self.verify(reg=reg, today="2026-11-13")
        self.assertFalse(self.face(v, "pin_freshness")["ok"])

    def test_31_future_verified_at(self):
        reg = _rehash(self.reg)
        reg["regulation_pins"][0]["verified_at"] = "2030-01-01"
        v = self.verify(reg=reg, today="2026-11-13")
        self.assertFalse(self.face(v, "pin_freshness")["ok"])


# =========================================================================
# 组 7 · 七面金丝雀（每面单独喂坏账，只让这一面红）
# =========================================================================
class TestCanary(_Base):
    def test_32_canary_claim_registered(self):
        reg = _rehash(self.reg)
        reg["doc_claims"] = [x for x in reg["doc_claims"] if x["id"] != "gate_redline_zh"]
        v = self.verify(reg=reg)
        self.assertFalse(self.face(v, "claim_registered")["ok"])
        self.assertTrue(self.face(v, "regulation_pinned")["ok"])

    def test_33_canary_readback(self):
        ctx = cg._ctx(root=self.ctx["root"], texts={
            "readme_zh": README_ZH_OK, "readme_en": README_EN_OK})
        reg = copy.deepcopy(self.reg)
        reg["doc_claims"][0]["expected_from"] = "computed.sums_entries"  # 1778 vs 4
        reg["self_digest"] = cg.self_digest(reg)
        v = cg.verify(reg, ctx, None)
        self.assertFalse(self.face(v, "readback_consistent")["ok"])

    def test_34_canary_historical(self):
        reg = _rehash(self.reg)
        for x in reg["doc_claims"]:
            if x["kind"] == "historical":
                x["as_of_batch"] = ""
                x["timeboxed"] = False
        v = self.verify(reg=reg)
        self.assertTrue(self.face(v, "historical_timeboxed")["ok"] is False)

    def test_35_canary_regulation_pinned(self):
        reg = _rehash(self.reg)
        for p in reg["regulation_pins"]:
            p["verified_at"] = ""
        v = self.verify(reg=reg)
        self.assertFalse(self.face(v, "regulation_pinned")["ok"])

    def test_36_canary_freshness(self):
        reg = _rehash(self.reg)
        for p in reg["regulation_pins"]:
            p["verified_at"] = "2019-01-01"
        v = self.verify(reg=reg, today="2026-11-13")
        self.assertFalse(self.face(v, "pin_freshness")["ok"])
        self.assertTrue(self.face(v, "regulation_pinned")["ok"])

    def test_37_canary_self_digest(self):
        reg = copy.deepcopy(self.reg)
        reg["totals"]["doc_claims"] += 1
        v = self.verify(reg=reg)
        self.assertFalse(self.face(v, "determinism_self_digest")["ok"])
        self.assertIn("self_digest", " ".join(
            f["detail"] for f in self.face(v, "determinism_self_digest")["fails"]))

    def test_38_canary_chain_position(self):
        tmp = tempfile.mkdtemp(prefix="v75_pkg_")
        try:
            with io.open(os.path.join(tmp, "ringless.py"), "w",
                         encoding="utf-8", newline="\n") as f:
                f.write('# -*- coding: utf-8 -*-\n"""RinglessGate — 测试件（V99 · ring77 演示域）"""\nX = 1\n')
            rep = cg.check_chain_position(tmp)
            self.assertEqual(rep["declared"], 1)
            self.assertEqual(len(rep["fails"]), 1)
            self.assertIn("UNLOCATED", rep["fails"][0]["detail"])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_39_canary_isolated(self):
        """一面红不得让别的面跟着红（避免「一红全红」的假阳性）。"""
        reg = _rehash(self.reg)
        reg["regulation_pins"][0]["version"] = ""
        reg = _rehash(reg)
        v = self.verify(reg=reg)
        self.assertFalse(self.face(v, "regulation_pinned")["ok"])
        for other in ("claim_registered", "historical_timeboxed",
                      "freshness" if False else "pin_freshness",
                      "determinism_self_digest", "chain_position_coverage"):
            self.assertTrue(self.face(v, other)["ok"], other)

    def test_40_ref_ring_not_self_declared(self):
        """「（ring11 召回层）」是引用他环，不得被判成自我声明。"""
        ring, ambiguous = cg._declared_rings(
            "Twin — 双轨核对（V44）\n第 D-11 链位：第十二环\n与 phc_recall（ring11 召回层）合成")
        self.assertEqual(ring, 12)
        self.assertFalse(ambiguous)


# =========================================================================
# 组 8 · 确定性与 self_digest
# =========================================================================
class TestDeterminism(_Base):
    def test_41_two_runs_same_digest(self):
        a = self.verify()["digest"]
        b = self.verify()["digest"]
        self.assertEqual(a, b)

    def test_42_report_stable(self):
        r1 = cg.report(self.reg, self.ctx)
        r2 = cg.report(self.reg, self.ctx)
        self.assertEqual(r1["digest"], r2["digest"])
        self.assertIn("rings", r1)

    def test_43_self_digest_matches_registry(self):
        self.assertEqual(cg.self_digest(self.reg), self.reg["self_digest"])

    def test_44_digest_changes_on_readback_change(self):
        ctx = cg._ctx(root=self.ctx["root"], texts={
            "readme_zh": README_ZH_OK.replace("tests-1778", "tests-999"),
            "readme_en": README_EN_OK})
        self.assertNotEqual(self.verify()["digest"], self.verify(ctx=ctx)["digest"])


# =========================================================================
# 组 9 · CLI 与异常路径
# =========================================================================
class TestCLI(_Base):
    def test_45_report_rc0(self):
        self.assertEqual(cg.main(["report"]), 0)

    def test_46_unknown_command_rc2(self):
        self.assertEqual(cg.main(["bogus"]), 2)

    def test_47_missing_registry_rc1(self):
        old = cg.default_registry_path
        cg.default_registry_path = lambda: os.path.join(self.root, "nope.json")
        try:
            self.assertEqual(cg.main(["verify"]), 1)
        finally:
            cg.default_registry_path = old

    def test_48_verify_returns_all_faces(self):
        v = self.verify()
        self.assertEqual(sorted(v["faces"].keys()), sorted(cg.FACES))
        for f in cg.FACES:
            self.assertIsInstance(v["faces"][f]["ok"], bool)


# =========================================================================
# 组 10 · 真实仓内覆盖（直读包）
# =========================================================================
class TestRealPackage(unittest.TestCase):
    def test_49_real_chain_position_coverage(self):
        rep = cg.check_chain_position()
        self.assertEqual(rep["fails"], [])
        self.assertGreaterEqual(rep["verified"], 24)
        self.assertGreaterEqual(rep["constants"], 28)

    def test_50_real_module_importable(self):
        self.assertTrue(hasattr(cg, "verify") and hasattr(cg, "report"))
        self.assertTrue(callable(cg.main))


if __name__ == "__main__":
    unittest.main()
