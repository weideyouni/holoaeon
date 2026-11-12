# -*- coding: utf-8 -*-
"""V73 / PL-6 史前大部头导学产品：六面可失败判据。

每一面都必须能单独变红，且红得可解释：
  ① 指针可达 + sha16 一致   ② 不夹带全文（≤200 字）
  ③ 零诊断零处方（单独成例） ④ 四部头覆盖
  ⑤ 导学路径无环、前驱后继可达 ⑥ 确定性（两跑同 digest + self_digest）
"""
import io
import json
import os
import shutil
import tempfile
import unittest

from holoaeon import prehistory_tutor as t


def _write(path, text):
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


class SyntheticBase(unittest.TestCase):
    """合成一个 12 卡 / 4 部头的最小可绿环境，用来逐个把判据打红。"""

    def make_env(self):
        tmp = tempfile.mkdtemp(prefix="v73tutor_")
        self.addCleanup(shutil.rmtree, tmp, True)
        root = os.path.join(tmp, "material")
        os.makedirs(root)
        doc = os.path.join(root, "corpus.md")
        _write(doc, "\n".join(["# 篇一", "", "这一篇讲的是计数与位值制的起源，属于史前记忆的底层。",
                               "", "# 篇二", "", "这一篇讲的是算筹与算盘如何把思考交给外物。", ""]))

        sha = t.file_sha16(doc)
        cards = []
        for sec in t.SECTIONS:
            for i in range(1, 4):
                cards.append({
                    "id": "SYN-%02d-%02d" % (t.SECTIONS.index(sec) + 1, i),
                    "source_pointer": "corpus.md#L2",
                    "sha16": sha,
                    "段落锚": {"line": 2, "heading": "篇一"},
                    "领域": "synthetic",
                    "归属仓": "C05",
                    "导学路径": {"prev": None, "next": None},
                    "evidence_level": "L2",
                    "zero_prescription": True,
                    "section": sec,
                    "summary": "史前记忆的指针短摘要，不含任何诊察与施治措辞。",
                })
        for i, c in enumerate(cards):
            if i % 3 > 0:
                c["导学路径"]["prev"] = cards[i - 1]["id"]
                cards[i - 1]["导学路径"]["next"] = c["id"]

        payload = self.payload(cards)
        path = os.path.join(tmp, "tutor_cards.json")
        _write(path, json.dumps(payload, ensure_ascii=False, indent=2))
        return root, path, payload

    def payload(self, cards, **over):
        base = {
            "schema": t.TUTOR_SCHEMA,
            "version": t.TUTOR_VERSION,
            "material_root_label": "synthetic",
            "sections": list(t.SECTIONS),
            "cards": cards,
            "note": t.NOTE,
        }
        base.update(over)
        return base

    def rewrite(self, path, payload):
        _write(path, json.dumps(payload, ensure_ascii=False, indent=2))
        return path

    def failures(self, root, path):
        out = t.verify(root, path)
        return out["ok"], [f["id"] for f in out["failures"]]


class T1_Positive(SyntheticBase):

    def test_00_synthetic_baseline_green(self):
        root, path, _ = self.make_env()
        ok, fails = self.failures(root, path)
        self.assertTrue(ok, fails)

    def test_01_report_counts(self):
        root, path, _ = self.make_env()
        rep = t.aggregate(root, path)
        self.assertEqual(rep["totals"]["cards"], 12)
        self.assertEqual(rep["totals"]["sections_covered"], 4)
        self.assertEqual(sorted(rep["sections"].values()), [3, 3, 3, 3])

    def test_02_report_has_digest_and_self_digest(self):
        root, path, _ = self.make_env()
        rep = t.finalize(t.aggregate(root, path))
        self.assertEqual(len(rep["digest"]), 16)
        self.assertEqual(len(rep["self_digest"]), 16)
        self.assertNotEqual(rep["digest"], rep["self_digest"])

    def test_03_report_no_abs_path(self):
        root, path, _ = self.make_env()
        rep = t.finalize(t.aggregate(root, path))
        self.assertNotIn("F:\\", json.dumps(rep, ensure_ascii=False))

    def test_04_l1_card_without_summary_is_green(self):
        root, path, payload = self.make_env()
        payload["cards"][0]["evidence_level"] = "L1"
        payload["cards"][0]["summary"] = ""
        self.rewrite(path, payload)
        ok, fails = self.failures(root, path)
        self.assertTrue(ok, fails)


class T2_PointerAndCopy(SyntheticBase):

    def test_10_pointer_unreachable(self):
        root, path, payload = self.make_env()
        payload["cards"][3]["source_pointer"] = "nowhere.md#L1"
        self.rewrite(path, payload)
        ok, fails = self.failures(root, path)
        self.assertFalse(ok)
        self.assertIn("pointer_reachable", fails)

    def test_11_sha_mismatch(self):
        root, path, payload = self.make_env()
        payload["cards"][4]["sha16"] = "0" * 16
        self.rewrite(path, payload)
        ok, fails = self.failures(root, path)
        self.assertFalse(ok)
        self.assertIn("sha_mismatch", fails)

    def test_12_anchor_out_of_range(self):
        root, path, payload = self.make_env()
        payload["cards"][5]["source_pointer"] = "corpus.md#L9999"
        self.rewrite(path, payload)
        ok, fails = self.failures(root, path)
        self.assertFalse(ok)
        self.assertIn("anchor_out_of_range", fails)

    def test_13_summary_oversize_boundary_ok(self):
        root, path, payload = self.make_env()
        payload["cards"][6]["summary"] = "甲" * t.MAX_SUMMARY_CHARS
        self.rewrite(path, payload)
        ok, fails = self.failures(root, path)
        self.assertTrue(ok, fails)

    def test_14_summary_oversize_by_one_is_red(self):
        root, path, payload = self.make_env()
        payload["cards"][6]["summary"] = "甲" * (t.MAX_SUMMARY_CHARS + 1)
        self.rewrite(path, payload)
        ok, fails = self.failures(root, path)
        self.assertFalse(ok)
        self.assertIn("summary_oversize", fails)

    def test_15_l2_without_summary_is_red(self):
        root, path, payload = self.make_env()
        payload["cards"][7]["summary"] = ""
        self.rewrite(path, payload)
        ok, fails = self.failures(root, path)
        self.assertFalse(ok)
        self.assertIn("summary_oversize", fails)


class T3_ZeroPrescription(SyntheticBase):
    """零诊断零处方必须单独成例，不允许被别的绿灯掩盖。"""

    def test_20_banned_term_in_summary(self):
        root, path, payload = self.make_env()
        payload["cards"][1]["summary"] = "这里给出一条用药建议，供参考。"
        self.rewrite(path, payload)
        ok, fails = self.failures(root, path)
        self.assertFalse(ok)
        self.assertIn("prescription_violation", fails)

    def test_21_banned_term_in_heading(self):
        root, path, payload = self.make_env()
        payload["cards"][2]["段落锚"]["heading"] = "诊断与处方示范"
        self.rewrite(path, payload)
        ok, fails = self.failures(root, path)
        self.assertFalse(ok)
        self.assertIn("prescription_violation", fails)

    def test_22_zero_prescription_flag_false(self):
        root, path, payload = self.make_env()
        payload["cards"][3]["zero_prescription"] = False
        self.rewrite(path, payload)
        ok, fails = self.failures(root, path)
        self.assertFalse(ok)
        self.assertIn("prescription_violation", fails)

    def test_23_prescription_is_its_own_criterion(self):
        root, path, payload = self.make_env()
        payload["cards"][3]["summary"] = "本条含剂量说明。"
        self.rewrite(path, payload)
        rep = t.aggregate(root, path)
        crit = {c["id"]: c for c in rep["criteria"]}
        self.assertFalse(crit["prescription_violation"]["ok"])
        self.assertEqual(crit["prescription_violation"]["detail"], [payload["cards"][3]["id"]])

    def test_24_clean_text_not_flagged(self):
        root, path, _ = self.make_env()
        rep = t.aggregate(root, path)
        self.assertEqual(t.banned_hits("导学路径与段落锚，谈的是计数与位值制"), [])


class T4_SectionCoverage(SyntheticBase):

    def test_30_section_missing(self):
        root, path, payload = self.make_env()
        payload["cards"] = [c for c in payload["cards"] if c["section"] != "周易"]
        self.rewrite(path, payload)
        ok, fails = self.failures(root, path)
        self.assertFalse(ok)
        self.assertIn("section_missing", fails)

    def test_31_section_thin(self):
        root, path, payload = self.make_env()
        keep = [c for c in payload["cards"] if c["section"] != "道藏"]
        keep += [c for c in payload["cards"] if c["section"] == "道藏"][:2]
        payload["cards"] = keep
        self.rewrite(path, payload)
        ok, fails = self.failures(root, path)
        self.assertFalse(ok)
        self.assertIn("section_thin", fails)

    def test_32_empty_library(self):
        root, path, payload = self.make_env()
        payload["cards"] = []
        self.rewrite(path, payload)
        ok, fails = self.failures(root, path)
        self.assertFalse(ok)
        self.assertIn("section_missing", fails)


class T5_Path(SyntheticBase):

    def test_40_path_broken(self):
        root, path, payload = self.make_env()
        payload["cards"][0]["导学路径"]["next"] = "SYN-GHOST"
        self.rewrite(path, payload)
        ok, fails = self.failures(root, path)
        self.assertFalse(ok)
        self.assertIn("path_broken", fails)

    def test_41_path_cycle(self):
        root, path, payload = self.make_env()
        cards = payload["cards"]
        cards[0]["导学路径"]["next"] = cards[1]["id"]
        cards[1]["导学路径"]["prev"] = cards[0]["id"]
        cards[1]["导学路径"]["next"] = cards[0]["id"]
        cards[0]["导学路径"]["prev"] = cards[1]["id"]
        self.rewrite(path, payload)
        ok, fails = self.failures(root, path)
        self.assertFalse(ok)
        self.assertIn("path_cycle", fails)

    def test_42_path_symmetry_break(self):
        root, path, payload = self.make_env()
        cards = payload["cards"]
        cards[2]["导学路径"]["next"] = cards[4]["id"]
        self.rewrite(path, payload)
        ok, fails = self.failures(root, path)
        self.assertFalse(ok)
        self.assertIn("path_broken", fails)


class T6_DeterminismAndReport(SyntheticBase):

    def test_50_two_runs_same_digest(self):
        root, path, _ = self.make_env()
        a = t.aggregate(root, path)["digest"]
        b = t.aggregate(root, path)["digest"]
        self.assertEqual(a, b)
        self.assertEqual(len(a), 16)

    def test_51_self_digest_tamper(self):
        root, path, _ = self.make_env()
        rep = t.finalize(t.aggregate(root, path))
        self.assertEqual(t.check(rep), [])
        rep["totals"]["cards"] = 99
        ids = [f["id"] for f in t.check(rep)]
        self.assertIn("self_digest", ids)

    def test_52_report_digest_tamper(self):
        root, path, _ = self.make_env()
        rep = t.finalize(t.aggregate(root, path))
        rep["cards"][0]["summary_chars"] += 1
        ids = [f["id"] for f in t.check(rep)]
        self.assertIn("card_digest", ids)

    def test_53_absolute_path_leak(self):
        root, path, payload = self.make_env()
        payload["note"] = t.NOTE + " 素材根：F:\\doubaowork"
        self.rewrite(path, payload)
        ok, fails = self.failures(root, path)
        self.assertFalse(ok)
        self.assertIn("absolute_path_leak", fails)

    def test_54_schema_drift(self):
        root, path, payload = self.make_env()
        payload["schema"] = "PREHISTORY-TUTOR-v0"
        self.rewrite(path, payload)
        ok, fails = self.failures(root, path)
        self.assertFalse(ok)
        self.assertIn("schema_drift", fails)


class T7_FieldsAndLoading(SyntheticBase):

    def test_60_field_missing(self):
        root, path, payload = self.make_env()
        del payload["cards"][0]["evidence_level"]
        self.rewrite(path, payload)
        ok, fails = self.failures(root, path)
        self.assertFalse(ok)
        self.assertIn("field_missing", fails)

    def test_61_evidence_level_invalid(self):
        root, path, payload = self.make_env()
        payload["cards"][1]["evidence_level"] = "L9"
        self.rewrite(path, payload)
        ok, fails = self.failures(root, path)
        self.assertFalse(ok)
        self.assertIn("summary_oversize", fails)

    def test_62_cards_file_missing(self):
        root, path, _ = self.make_env()
        os.remove(path)
        ok, fails = self.failures(root, path)
        self.assertFalse(ok)
        self.assertIn("cards_unreadable", fails)

    def test_63_cards_file_unreadable(self):
        root, path, _ = self.make_env()
        _write(path, "{not json")
        ok, fails = self.failures(root, path)
        self.assertFalse(ok)
        self.assertIn("cards_unreadable", fails)

    def test_64_card_ids_unique(self):
        root, path, payload = self.make_env()
        ids = [c["id"] for c in payload["cards"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_65_pointer_parser(self):
        self.assertEqual(t.split_pointer("a/b.md#L12"), ("a/b.md", 12))
        self.assertEqual(t.split_pointer("badpointer"), (None, 0))
        self.assertEqual(t.split_pointer("a.md#Lx"), (None, 0))


class T8_RealCorpus(unittest.TestCase):
    """真实站点：跑仓内卡片库 + F 盘素材，必须全绿。"""

    @classmethod
    def setUpClass(cls):
        cls.out = t.verify()

    def test_80_real_corpus_green(self):
        self.assertTrue(self.out["ok"], self.out["failures"])

    def test_81_real_card_count(self):
        self.assertEqual(self.out["report"]["totals"]["cards"], 42)

    def test_82_real_four_sections(self):
        stats = self.out["report"]["sections"]
        self.assertEqual(sorted(stats.keys()), sorted(t.SECTIONS))
        for sec in t.SECTIONS:
            self.assertGreaterEqual(stats[sec], t.MIN_CARDS_PER_SECTION, sec)

    def test_83_real_summaries_within_limit(self):
        self.assertLessEqual(self.out["report"]["totals"]["max_summary_observed"],
                             t.MAX_SUMMARY_CHARS)

    def test_84_real_criteria_all_green(self):
        for c in self.out["report"]["criteria"]:
            self.assertTrue(c["ok"], c["id"])


class T9_Cli(unittest.TestCase):

    def test_90_main_verify_exit_zero(self):
        self.assertEqual(t._main(["prehistory_tutor", "verify"]), 0)

    def test_91_main_bad_command(self):
        self.assertEqual(t._main(["prehistory_tutor", "nonsense"]), 2)


if __name__ == "__main__":
    unittest.main()
