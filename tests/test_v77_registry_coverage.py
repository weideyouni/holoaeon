# -*- coding: utf-8 -*-
"""V77 · claims_gate 第 8 面 registry_coverage 测试（九组 ≥18 例）。

闸自己也会漏自己：V75 建了七面闸，却漏改自家 README 的 L158「V0.1 → V38」，
根因是注册簿没有「自覆盖」判据。本文件为第 8 面配金丝雀：
先证 UNREGISTERED / VANISHED / NOT_READBACK / ANCHOR_MISSING 四种红都会红，
再证明历史段落不被误伤、真实仓八面全绿。
"""
import copy
import json
import os
import tempfile
import io
import unittest

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holoaeon import claims_gate as cg  # noqa: E402

ZH_CLEAN = """# Demo
![Tests](https://img.shields.io/badge/tests-1200%2B11%2B21%20passed-success.svg)
- **工程验收（本机实跑口径）**：主套单测 **1200 OK** + v3 域 **11**
| 门禁 | `unittest 1200 OK` |
**2026-10 → 今 · 版本号以回读为准（不写死）。**
历史段落：V4.0 → V6.1 是过去的事，不在活体窗口。
"""

EN_CLEAN = """# Demo
[![Tests](https://img.shields.io/badge/tests-1200%2B11%2B21%20passed-success.svg)](#-testing)
- **Gates (measured on this machine)**: main suite **1200 OK** + v3 domain **11**
**2026-10 → present — version is a readback of the ledger, never hardcoded.**
History: V4.0 → V6.1 lives in a past section, outside any live window.
"""

ZH_DIRTY = ZH_CLEAN.replace(
    "**2026-10 → 今 · 版本号以回读为准（不写死）。**",
    "**2026-10 → 今 · HoloAeon V0.1 → V38。**")


def _ctx(zh=ZH_CLEAN, en=EN_CLEAN):
    return cg._ctx(texts={"readme_zh": zh, "readme_en": en})


class _Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reg = copy.deepcopy(cg.load_registry())

    def _fails(self, reg, ctx=None):
        return [f for f in cg.check_registry_coverage(
            _rehash(reg), ctx or _ctx())]

    def assertFaceRed(self, fails, tag):
        self.assertTrue(fails, "期望判红但没有 fail")
        self.assertTrue(any(tag in (f.get("detail") or "") for f in fails),
                        "期望 %s，实际 %r" % (tag, fails))


def _rehash(reg):
    reg = copy.deepcopy(reg)
    reg["self_digest"] = cg.self_digest({k: v for k, v in reg.items()
                                         if k != "self_digest"})
    return reg


def _drop_coverage(reg, cov_id):
    reg = copy.deepcopy(reg)
    reg["coverage"] = [e for e in reg.get("coverage") or [] if e.get("id") != cov_id]
    return reg


class T1RegistryShape(_Base):
    """T1：注册簿结构——8 面在名、6 窗口、6 coverage、17 条声明。"""

    def test_faces_include_registry_coverage(self):
        self.assertIn("registry_coverage", cg.FACES)
        self.assertEqual(len(cg.FACES), 8)

    def test_eight_faces_unique(self):
        self.assertEqual(len(set(cg.FACES)), 8)

    def test_live_windows_count(self):
        self.assertEqual(len(cg.LIVE_WINDOWS), 6)

    def test_windows_have_declared_patterns(self):
        for w in cg.LIVE_WINDOWS:
            for p in w["patterns"]:
                self.assertIn(p, cg.COVERAGE_PATTERNS)

    def test_registry_has_six_coverage_entries(self):
        self.assertEqual(len(self.reg.get("coverage") or []), 6)

    def test_doc_claims_seventeen(self):
        self.assertEqual(self.reg["totals"]["doc_claims"], 17)
        self.assertEqual(self.reg["totals"]["narrative"], 5)


class T2CanaryUnregistered(_Base):
    """T2 金丝雀：窗口内写死位未登记 → UNREGISTERED（L158 病理复现）。"""

    def test_dirty_readme_is_red(self):
        fails = cg.check_registry_coverage(_drop_coverage(self.reg, "cover_zh_timeline"),
                                           _ctx(zh=ZH_DIRTY))
        self.assertFaceRed(fails, "UNREGISTERED")

    def test_dirty_detail_carries_line_and_text(self):
        fails = cg.check_registry_coverage(_drop_coverage(self.reg, "cover_zh_timeline"),
                                           _ctx(zh=ZH_DIRTY))
        detail = [f["detail"] for f in fails if "UNREGISTERED" in f["detail"]][0]
        self.assertIn("V0.1 → V38", detail)
        self.assertIn("@L", detail)

    def test_english_dirty_also_red(self):
        en_dirty = EN_CLEAN.replace(
            "**2026-10 → present — version is a readback of the ledger, never hardcoded.**",
            "**2026-10 → present — HoloAeon V0.1 to V59.**")
        fails = cg.check_registry_coverage(_drop_coverage(self.reg, "cover_en_timeline"),
                                           _ctx(en=en_dirty))
        self.assertFaceRed(fails, "UNREGISTERED")


class T3CanaryVanished(_Base):
    """T3 金丝雀：登记了 must_appear 却在窗口里找不到 → VANISHED（防删文本假绿）。"""

    def test_badge_text_removed_is_red(self):
        # 锚点仍在、数字没了 → VANISHED（与「整行被删」的 ANCHOR_MISSING 区分）
        zh_no_badge = ZH_CLEAN.replace(
            "https://img.shields.io/badge/tests-1200%2B11%2B21%20passed-success.svg",
            "https://img.shields.io/badge/placeholder.svg")
        fails = cg.check_registry_coverage(self.reg, _ctx(zh=zh_no_badge))
        self.assertFaceRed(fails, "VANISHED")

    def test_must_appear_false_not_red_when_absent(self):
        # timeline 的 must_appear=False：改回读式后不出现写死位是正常态
        self.assertEqual([f for f in cg.check_registry_coverage(self.reg, _ctx())
                          if "VANISHED" in (f.get("detail") or "")], [])


class T4CanaryNotReadback(_Base):
    """T4 金丝雀：声称已改回读式但窗口里没有「回读」字样 → NOT_READBACK。"""

    def test_hardcoded_timeline_without_readback(self):
        zh = ZH_CLEAN.replace(
            "**2026-10 → 今 · 版本号以回读为准（不写死）。**",
            "**2026-10 → 今 · HoloAeon 一个零依赖框架。**")
        fails = cg.check_registry_coverage(self.reg, _ctx(zh=zh))
        self.assertFaceRed(fails, "NOT_READBACK")

    def test_readback_word_makes_it_green(self):
        self.assertEqual(cg.check_registry_coverage(self.reg, _ctx()), [])


class T5CanaryAnchorMissing(_Base):
    """T5 金丝雀：锚点整行消失 → ANCHOR_MISSING（结构漂移不许静默跳过）。"""

    def test_missing_zh_acceptance_anchor(self):
        zh = ZH_CLEAN.replace("- **工程验收（本机实跑口径）**", "- 验收行被改名")
        fails = cg.check_registry_coverage(self.reg, _ctx(zh=zh))
        self.assertFaceRed(fails, "ANCHOR_MISSING")

    def test_missing_en_badge_anchor(self):
        en = EN_CLEAN.replace("[![Tests]", "[![Badge")
        fails = cg.check_registry_coverage(self.reg, _ctx(en=en))
        self.assertFaceRed(fails, "ANCHOR_MISSING")


class T6CanaryUnknownWindow(_Base):
    """T6 金丝雀：coverage 指向不存在的窗口 → UNKNOWN_WINDOW。"""

    def test_unknown_window_red(self):
        reg = copy.deepcopy(self.reg)
        reg["coverage"].append({"id": "cover_ghost", "window": "ghost_window",
                                "pattern": "tests_badge"})
        fails = cg.check_registry_coverage(_rehash(reg), _ctx())
        self.assertFaceRed(fails, "UNKNOWN_WINDOW")


class T7HistoricalNotPunished(_Base):
    """T7：历史段落里的版本范围不在活体窗口 → 不许误红。"""

    def test_history_line_ignored(self):
        # ZH_CLEAN 自带「V4.0 → V6.1」历史行：面 8 不应因它判红（其余面另测）
        self.assertEqual(cg.check_registry_coverage(self.reg, _ctx()), [])

    def test_past_segment_version_range_counted_zero(self):
        fails = cg.check_registry_coverage(self.reg, _ctx())
        self.assertEqual([f for f in fails if "UNREGISTERED" in (f.get("detail") or "")], [])


class T8RealRepoEightFaces(_Base):
    """T8：真实仓 + 真实 README 八面全绿，两跑同 digest。"""

    def test_real_repo_pass(self):
        v = cg.verify(self.reg)
        self.assertEqual(v["verdict"], "PASS", msg=str(v["faces"]))
        self.assertEqual(v["mismatch"], 0)

    def test_determinism_two_runs_same_digest(self):
        a = cg.verify(cg.load_registry())
        b = cg.verify(cg.load_registry())
        self.assertEqual(a["digest"], b["digest"])

    def test_registry_coverage_window_count_in_body(self):
        v = cg.verify(self.reg)
        self.assertEqual(v["registry_coverage"]["windows"], 6)
        self.assertEqual(v["registry_coverage"]["entries"], 6)


class T9SelfDigestAndReport(_Base):
    """T9：注册簿自摘要与 report 快照一致（建完改注册簿必红）。"""

    def test_self_digest_matches(self):
        self.assertEqual(cg.check_self_digest(self.reg), [])

    def test_tampered_registry_red(self):
        reg = copy.deepcopy(self.reg)
        reg["doc_claims"][0]["note"] = "被改过了"
        self.assertTrue(cg.check_self_digest(reg))

    def test_report_has_eight_faces(self):
        snap = cg.report(self.reg)
        self.assertEqual(len(snap["faces"]), 8)
        self.assertTrue(all(snap["faces"][f] for f in cg.FACES))


class T10VersionNotZeroed(_Base):
    """T10：版本号不许被 _int_of 归零——0.9.69 与 0.9.70 必须判不同。

    本批实测抓到：V76 时 DOC 升号在闸里被判「相等」（0.9.68 与 0.9.69 都归零成 0），
    版本升号对闸完全隐形；这是闸看不见自己的一种，与 L158 漏改同族。
    """

    def _ver_fixture(self, spec_ver, rec_ver):
        root = tempfile.mkdtemp(prefix="v77_ver_")
        pkg = os.path.join(root, "holoaeon")
        os.makedirs(pkg)
        with io.open(os.path.join(pkg, "spec.py"), "w",
                     encoding="utf-8", newline="\n") as f:
            f.write('DOC_VERSION = "%s"\n' % spec_ver)
        os.makedirs(os.path.join(root, "reports"))
        with io.open(os.path.join(root, "reports", "v77_receipt.json"), "w",
                     encoding="utf-8", newline="\n") as f:
            json.dump({"doc_version": rec_ver}, f)
        return cg._ctx(root=root, texts={"readme_zh": ZH_CLEAN, "readme_en": EN_CLEAN})

    def test_is_version_recognizes_dotted(self):
        self.assertTrue(cg._is_version("0.9.69"))
        self.assertTrue(cg._is_version("12.0.1"))
        self.assertFalse(cg._is_version("1835"))
        self.assertFalse(cg._is_version("主套 1835 OK"))

    def test_version_change_is_red(self):
        ctx = self._ver_fixture("0.9.70", "0.9.69")
        fails = [f for f in cg.check_doc_claims(self.reg, ctx)
                 if f["id"] == "doc_version_spec"]
        self.assertTrue(fails, "0.9.70 vs 0.9.69 必须判红")
        self.assertIn("MISMATCH", fails[0]["detail"])

    def test_same_version_is_green(self):
        ctx = self._ver_fixture("0.9.70", "0.9.70")
        self.assertEqual([f for f in cg.check_doc_claims(self.reg, ctx)
                          if f["id"] == "doc_version_spec"], [])


if __name__ == "__main__":
    unittest.main()
