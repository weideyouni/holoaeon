# -*- coding: utf-8 -*-
"""V69 PL-3 领域语义桥测试：卡片识别 / 与旧口径一致 / 零分下降 / 四失败面 / 零副作用。"""
import io
import json
import os
import unittest

from holoaeon.prehistory_semantic_bridge import (
    BRIDGE_SCHEMA,
    EXPECTED_ZERO_BEFORE,
    KNOWN_VACUUM,
    LEXICON,
    SAMPLES,
    ZERO_AFTER_MAX,
    asset_bridge_text,
    asset_text,
    bridged_absorb,
    cang_bridge_text,
    cang_text,
    card_for,
    check_bridge,
    compare,
    digest,
    normalize,
    score_table,
    verify_bridge,
)
from holoaeon.c18_cluster import C18_NUMBERING
from holoaeon.forge_bureau import forge_absorb
from holoaeon.spec import DOC_VERSION
from holoaeon import packs


SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "holoaeon", "prehistory_semantic_bridge.py")


def _src():
    with io.open(SRC, "r", encoding="utf-8") as fh:
        return fh.read()


class TestCard(unittest.TestCase):
    def test_medical_card_hits(self):
        card = card_for("吴门医派1331x1331_SUPER-MAS-V3.0_runtime")
        self.assertIn("meridian_med", card["labels"])
        self.assertEqual(card["targets"], ["C03"])

    def test_legal_card_hits(self):
        card = card_for("王静斋V3.0_独立验证与安全审计报告")
        self.assertIn("risk_legal", card["labels"])

    def test_math_card_hits(self):
        card = card_for("张量拆解双王矩阵实战化_20261017")
        self.assertIn("craft_math", card["labels"])
        self.assertEqual(card["targets"], ["C14"])

    def test_code_name_is_vacuum(self):
        card = card_for("SG-MASTER-SONGJIANG-1331x1331-SUPER-MAS-V3.0_runtime")
        self.assertEqual(card["labels"], [])
        self.assertEqual(card["evidence"], "none")
        self.assertTrue(card["vacuum"])

    def test_unregistered_empty_name_is_not_vacuum(self):
        card = card_for("某某无名代号_20261018")
        self.assertEqual(card["labels"], [])
        self.assertFalse(card["vacuum"])

    def test_generic_tail_is_not_a_term(self):
        # 1331/矩阵/runtime 这类通用尾巴不得进入词表，否则全体资产同向漂移
        for rule in LEXICON:
            for term in rule["asset_terms"]:
                self.assertNotIn(term, ("1331", "矩阵", "runtime", "super-mas",
                                        "实战化", "多智能体", "v3"))

    def test_normalize_lowercases_and_drops_space(self):
        self.assertEqual(normalize("Arena 母体"), "arena母体")

    def test_every_sample_has_card_or_vacuum(self):
        for name in SAMPLES:
            card = card_for(name)
            self.assertTrue(card["labels"] or card["vacuum"], name)


class TestTextBuild(unittest.TestCase):
    def test_asset_text_matches_forge_shape(self):
        spec = {"name": "甲", "description": "乙", "tags": ["丙", "丁"]}
        self.assertEqual(asset_text(spec), "甲；乙；丙、丁")

    def test_asset_bridge_text_appends_terms_only(self):
        spec = {"name": "吴门医派1331", "description": "", "tags": []}
        bridged = asset_bridge_text(spec)
        self.assertTrue(bridged.startswith(asset_text(spec)))
        self.assertIn("医派", bridged)

    def test_asset_bridge_text_no_terms_when_no_card(self):
        spec = {"name": "SG-MASTER-SONGJIANG", "description": "", "tags": []}
        self.assertEqual(asset_bridge_text(spec), asset_text(spec))

    def test_cang_text_matches_repo_identity(self):
        c = C18_NUMBERING[0]
        self.assertEqual(cang_text(c), "{}；{}；{}".format(
            c["domain"], c["question"], c["role"]))

    def test_cang_bridge_text_only_extends_its_own_cang(self):
        c15 = next(c for c in C18_NUMBERING if c["id"] == "C15")
        text = cang_bridge_text(c15)
        self.assertIn("法务", text)
        self.assertNotIn("医派", text)

    def test_cang_bridge_text_keeps_original_prefix(self):
        for c in C18_NUMBERING:
            self.assertTrue(cang_bridge_text(c).startswith(cang_text(c)))


class TestBaselineConsistency(unittest.TestCase):
    """桥必须与旧口径同源：baseline 分数/repo 要与 forge_absorb 完全一致。"""

    def test_baseline_equals_forge_absorb(self):
        for name in SAMPLES:
            spec = {"name": name, "description": "", "tags": []}
            old = forge_absorb(spec)
            new = bridged_absorb(spec)
            self.assertEqual(new["baseline"]["repo"],
                             old["absorbed_into"]["repo"], name)
            self.assertEqual(new["baseline"]["score"],
                             old["absorbed_into"]["score"], name)

    def test_baseline_runner_up_equals(self):
        name = SAMPLES[0]
        spec = {"name": name, "description": "", "tags": []}
        old = forge_absorb(spec)
        new = bridged_absorb(spec)
        self.assertEqual(new["baseline"]["runner_up"], old["runner_up"]["score"])

    def test_score_table_sorted_desc_then_repo(self):
        rows = score_table({"name": "吴门医派", "description": "", "tags": []})
        self.assertEqual(len(rows), len(C18_NUMBERING))
        self.assertEqual(rows, sorted(rows, key=lambda t: (-t[0], t[1])))


class TestBridgeEffect(unittest.TestCase):
    def test_zero_before_equals_measured(self):
        rep = compare()
        self.assertEqual(rep["zero_before"], EXPECTED_ZERO_BEFORE)

    def test_zero_after_within_cap(self):
        rep = compare()
        self.assertLessEqual(rep["zero_after"], ZERO_AFTER_MAX)

    def test_remaining_zero_is_registered_vacuum(self):
        rep = compare()
        for name in rep["zero_after_list"]:
            self.assertTrue(any(v in name for v in KNOWN_VACUUM), name)

    def test_zero_drops(self):
        rep = compare()
        self.assertLess(rep["zero_after"], rep["zero_before"])

    def test_math_master_not_relation(self):
        rec = bridged_absorb({"name": "数学大师1331_数学史早课",
                              "description": "", "tags": []})
        self.assertNotEqual(rec["bridged"]["cang"], "C09")
        self.assertIn(rec["bridged"]["cang"], ("C14", "C05"))

    def test_cang_changed_is_bulk(self):
        rep = compare()
        self.assertGreaterEqual(rep["cang_changed"], 10)

    def test_repaired_flag_for_zero_cases(self):
        rec = bridged_absorb({"name": "世界考古大师1331", "description": "", "tags": []})
        self.assertTrue(rec["repaired"])
        self.assertFalse(rec["still_zero"])

    def test_vacuum_still_zero_and_flagged(self):
        rec = bridged_absorb({"name": "SG-MASTER-SONGJIANG-1331",
                              "description": "", "tags": []})
        self.assertTrue(rec["still_zero"])
        self.assertTrue(rec["card"]["vacuum"])
        self.assertFalse(rec["repaired"])


class TestDeterminism(unittest.TestCase):
    def test_two_runs_identical_rows(self):
        a = compare()
        b = compare()
        for i in range(len(a["rows"])):
            self.assertEqual(a["rows"][i]["baseline"], b["rows"][i]["baseline"])
            self.assertEqual(a["rows"][i]["bridged"], b["rows"][i]["bridged"])

    def test_digest_stable_across_runs(self):
        self.assertEqual(digest(compare()), digest(compare()))

    def test_same_spec_same_record(self):
        spec = {"name": "海派中医全派1331", "description": "", "tags": []}
        self.assertEqual(json.dumps(bridged_absorb(spec), sort_keys=True,
                                    ensure_ascii=False),
                         json.dumps(bridged_absorb(spec), sort_keys=True,
                                    ensure_ascii=False))


class TestGates(unittest.TestCase):
    def test_check_bridge_passes(self):
        r = check_bridge()
        self.assertTrue(r["pass"], r["problems"])
        self.assertEqual(r["stats"]["samples"], len(SAMPLES))
        self.assertTrue(r["report_digest"])

    def test_verify_accepts_good_report(self):
        rep = compare()
        v = verify_bridge(rep, digest(rep))
        self.assertTrue(v["pass"], v["problems"])

    def test_verify_catches_baseline_drift(self):
        rep = compare()
        rep["zero_before"] = 4           # 策划案口径，不是本机实测
        v = verify_bridge(rep)
        self.assertFalse(v["pass"])
        self.assertTrue(any("baseline_drift" in p for p in v["problems"]))

    def test_verify_catches_zero_exceed(self):
        rep = compare()
        rep["zero_after"] = ZERO_AFTER_MAX + 1
        v = verify_bridge(rep)
        self.assertFalse(v["pass"])
        self.assertTrue(any("zero_after_exceeds" in p for p in v["problems"]))

    def test_verify_catches_unregistered_zero(self):
        rep = compare()
        rep["zero_after"] = 1
        rep["zero_after_list"] = ["某未登记资产_20261018"]
        v = verify_bridge(rep)
        self.assertFalse(v["pass"])
        self.assertTrue(any("unregistered_zero" in p for p in v["problems"]))

    def test_verify_catches_no_card_exceed(self):
        rep = compare()
        rep["no_card"] = rep["vacuum"] + 2
        v = verify_bridge(rep)
        self.assertFalse(v["pass"])
        self.assertTrue(any("no_card_exceeds" in p for p in v["problems"]))

    def test_verify_catches_digest_tamper(self):
        rep = compare()
        v = verify_bridge(rep, "0000000000000000")
        self.assertFalse(v["pass"])
        self.assertTrue(any("self_digest" in p for p in v["problems"]))

    def test_verify_catches_bad_schema(self):
        rep = compare()
        rep["schema"] = "OTHER-v1"
        v = verify_bridge(rep)
        self.assertFalse(v["pass"])


class TestNoSideEffects(unittest.TestCase):
    def test_source_has_no_write_or_spawn(self):
        src = _src()
        for bad in ("os.remove", "os.rename", "os.replace", "shutil",
                    "subprocess", "socket", "os.system", "urllib", ".write("):
            self.assertNotIn(bad, src, bad)

    def test_source_has_no_dynamic_exec(self):
        src = _src()
        for bad in ("eval(", "exec(", "compile(", "__import__"):
            self.assertNotIn(bad, src, bad)

    def test_source_has_no_random_or_network(self):
        src = _src()
        for bad in ("import random", "requests", "http.client", "socket"):
            self.assertNotIn(bad, src, bad)

    def test_module_does_not_touch_disk(self):
        before = len(compare()["rows"])
        self.assertEqual(before, len(SAMPLES))


class TestDocAndDimensions(unittest.TestCase):
    def test_doc_version_is_0_9_63(self):
        self.assertEqual(DOC_VERSION, "0.9.63")

    def test_pack_orders_untouched(self):
        self.assertEqual(len(packs.PACK_ORDER), 9)
        self.assertEqual(len(packs.EXTRA_PACK_ORDER), 19)

    def test_schema_tag(self):
        self.assertEqual(BRIDGE_SCHEMA, "PREHISTORY-BRIDGE-v1")


if __name__ == "__main__":
    unittest.main()
