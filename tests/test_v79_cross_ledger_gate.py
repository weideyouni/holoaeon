# -*- coding: utf-8 -*-
"""V79 · claims_gate 第 10 面 `cross_ledger_consistency` 测试。

47 例 / 十组 / 8 只金丝雀（C0 最高优先：`intent_vs_blocker`）。
纪律：不写死真实 HEAD / DOC 数值，全部走自造 tmp 上下文（沿用 test_v75 先例）；
不联网、不跑外部命令；selftest 之外零副作用。
"""
import ast
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holoaeon import claims_gate as cg  # noqa: E402

CARBON = "碳基终裁：必须补 workflow scope，当时只是同步报错才搁置，任务从未取消"
D0_WHERE = ("NOTE_20261113_HOLOAEON_S3_MIRROR_MODE.md L1/L3 + "
            "v77_decision_defer_workflow.py L2/L48/L50/L51 + "
            "engineering_machine.STATE.pending")
D0_WAS = "碳基决议：先不加工作流权限，等以后条件允许再做"


def make_sources(doc="0.9.99", main_suite=2000, redline=156,
                 head="aaaaaaa", five="aaaaaaa",
                 stage="closed_execution_side", carbon=CARBON,
                 precedence=cg.CARBON_PRECEDENCE):
    return {
        "head": {"authority": cg.AUTHORITATIVE_SOURCES["head"],
                 "observed": head, "non_evidence": ["git_remote_tracking_ref"]},
        "doc_version": {"authority": cg.AUTHORITATIVE_SOURCES["doc_version"],
                        "observed": doc, "non_evidence": ["runtime_snapshot"]},
        "batch_stage": {"authority": cg.AUTHORITATIVE_SOURCES["batch_stage"],
                        "observed": stage},
        "five_site_head": {"authority": cg.AUTHORITATIVE_SOURCES["five_site_head"],
                           "observed": five,
                           "non_evidence": ["git_remote_tracking_ref"]},
        "main_suite": {"authority": cg.AUTHORITATIVE_SOURCES["main_suite"],
                       "observed": main_suite,
                       "non_evidence": ["runtime_snapshot", "timeboxed_historical"]},
        "redline": {"authority": cg.AUTHORITATIVE_SOURCES["redline"],
                    "observed": redline,
                    "non_evidence": ["runtime_snapshot", "timeboxed_historical"]},
        "carbon_intent": {"authority": cg.AUTHORITATIVE_SOURCES["carbon_intent"],
                          "precedence": precedence, "observed": carbon},
    }


def make_registry(sources=None, conflicts=None):
    return {"schema": "CLAIMS-GATE-v1",
            "ledger_sources": make_sources() if sources is None else sources,
            "ledger_conflicts": list(conflicts or [])}


def d0_conflict(kind="intent_vs_blocker", canon=CARBON):
    return {"id": "D0", "kind": kind, "where": D0_WHERE, "was": D0_WAS,
            "truth": CARBON, "carbon_canon": canon,
            "disposition": "登记为 blocker_not_intent；措辞由 PL-7 批清理"}


def d2_conflict():
    return {"id": "D2", "kind": "caliber_difference",
            "where": "receipt.status vs machine STATE",
            "was": "LOCAL_READY", "truth": "closed_execution_side",
            "disposition": "登记为合法口径差"}


def d4_conflict(observed=None):
    e = {"id": "D4", "kind": "runtime_snapshot",
         "where": "state_beacon#unittest_main_1703",
         "was": "1703", "truth": "运行期快照不随批次手改",
         "disposition": "登记为合法历史键，不删不手改"}
    if observed is not None:
        e["observed_at_register"] = dict(observed)
    return e


def d5_conflict(kind="known_boundary"):
    return {"id": "D5", "kind": kind, "where": "ci.yml vs ci_preflight",
            "was": "本地绿即云端绿", "truth": "local green != cloud green",
            "disposition": "登记为能力边界，不判红"}


class _Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="v79_ledger_")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def ctx(self, **kw):
        c = cg._ctx(self.tmp)
        c["texts"] = {
            "head": kw.get("head", "aaaaaaa"),
            "doc_version": kw.get("doc", "0.9.99"),
            "batch_stage": kw.get("stage", "closed_execution_side"),
            "five_site_head": kw.get("five", "aaaaaaa"),
            "main_suite": kw.get("main_suite", 2000),
            "redline": kw.get("redline", 156),
            "carbon_intent": kw.get("carbon", CARBON),
            "pending_note": kw.get("pending", ""),
            "intent_texts": kw.get("intent_texts", []),
        }
        c["landed_batches"] = kw.get("landed", set())
        return c

    def run_face(self, reg, **kw):
        return cg.cross_ledger_consistency(reg, self.ctx(**kw))

    def kinds(self, res):
        return {f["kind"] for f in res["fails"]}


# ---------------------------------------------------------------------------
# G1 权威源字典结构
# ---------------------------------------------------------------------------
class G1AuthoritativeSources(_Base):
    def test_01_face_name_is_registered_in_faces(self):
        self.assertIn(cg.FACE_CROSS_LEDGER, cg.FACES)
        self.assertGreaterEqual(len(cg.FACES), 10)  # V80 起 11 面；下界口径，面数不写死

    def test_02_authoritative_sources_cover_seven_keys(self):
        self.assertEqual(len(cg.AUTHORITATIVE_SOURCES), 7)
        for key in ("head", "doc_version", "batch_stage", "five_site_head",
                    "main_suite", "redline", "carbon_intent"):
            self.assertIn(key, cg.AUTHORITATIVE_SOURCES)

    def test_03_carbon_intent_is_terminal_utterance(self):
        self.assertEqual(cg.AUTHORITATIVE_SOURCES["carbon_intent"],
                         "carbon_utterance_terminal")

    def test_04_missing_sources_段_is_structural_fail(self):
        res = self.run_face({"ledger_conflicts": []}, **{})
        self.assertFalse(res["ok"])
        self.assertIn("structure", self.kinds(res))

    def test_05_clean_sources_pass(self):
        res = self.run_face(make_registry())
        self.assertTrue(res["ok"], res["fails"])


# ---------------------------------------------------------------------------
# G2 NON_EVIDENCE 白名单
# ---------------------------------------------------------------------------
class G2NonEvidence(_Base):
    def test_06_non_evidence_tuple_is_exact(self):
        self.assertEqual(cg.NON_EVIDENCE, ("git_remote_tracking_ref",
                                           "runtime_snapshot",
                                           "timeboxed_historical"))

    def test_07_authority_cannot_be_remote_tracking_ref(self):
        srcs = make_sources()
        srcs["five_site_head"]["authority"] = "git_remote_tracking_ref"
        res = self.run_face(make_registry(srcs))
        self.assertFalse(res["ok"])
        self.assertTrue(any("authority_mismatch" in f["id"] for f in res["fails"]))

    def test_08_unknown_non_evidence_rejected(self):
        srcs = make_sources()
        srcs["head"]["non_evidence"] = ["chat_memory"]
        res = self.run_face(make_registry(srcs))
        self.assertFalse(res["ok"])
        self.assertTrue(any("non_evidence_unknown" in f["id"] for f in res["fails"]))

    def test_09_declared_sources_are_not_numeric_compared(self):
        self.assertIn("head", cg.DECLARED_ONLY)
        self.assertIn("five_site_head", cg.DECLARED_ONLY)
        srcs = make_sources(head="aaaaaaa")
        res = self.run_face(make_registry(srcs), head="bbbbbbb")
        self.assertTrue(res["ok"], res["fails"])


# ---------------------------------------------------------------------------
# G3 unregistered_conflict 正向
# ---------------------------------------------------------------------------
class G3UnregisteredConflict(_Base):
    def test_10_doc_version_drift_without_registration(self):
        srcs = make_sources(doc="0.9.99")
        res = self.run_face(make_registry(srcs), doc="0.9.100")
        self.assertFalse(res["ok"])
        self.assertEqual(res["unregistered"], ["unregistered_conflict:doc_version"])

    def test_11_main_suite_drift_without_registration(self):
        srcs = make_sources(main_suite=2000)
        res = self.run_face(make_registry(srcs), main_suite=2100)
        self.assertFalse(res["ok"])
        self.assertIn("unregistered_conflict:main_suite", res["unregistered"])

    def test_12_redline_drift_without_registration(self):
        srcs = make_sources(redline=156)
        res = self.run_face(make_registry(srcs), redline=157)
        self.assertFalse(res["ok"])
        self.assertIn("unregistered_conflict:redline", res["unregistered"])

    def test_13_three_drifts_yield_three_fails(self):
        srcs = make_sources(doc="1.0", main_suite=1, redline=2)
        res = self.run_face(make_registry(srcs), doc="2.0", main_suite=2, redline=3)
        self.assertEqual(len(res["unregistered"]), 3)

    def test_14_unregistered_kind_is_named(self):
        srcs = make_sources(doc="0.9.99")
        res = self.run_face(make_registry(srcs), doc="0.9.100")
        self.assertIn("unregistered_conflict", self.kinds(res))


# ---------------------------------------------------------------------------
# G4 unregistered_conflict 反向（已登记不红）
# ---------------------------------------------------------------------------
class G4RegisteredTolerated(_Base):
    def test_15_caliber_difference_covers_doc_key(self):
        srcs = make_sources(doc="0.9.99")
        e = d2_conflict()
        e["keys"] = ["doc_version"]
        res = self.run_face(make_registry(srcs, [e]), doc="0.9.100")
        self.assertTrue(res["ok"], res["fails"])

    def test_16_key_covered_by_where_substring(self):
        srcs = make_sources(doc="0.9.99")
        e = d2_conflict()
        e["where"] = "receipt 与 doc_version 的口径差"
        res = self.run_face(make_registry(srcs, [e]), doc="0.9.100")
        self.assertTrue(res["ok"], res["fails"])

    def test_17_matching_values_never_red(self):
        res = self.run_face(make_registry(), doc="0.9.99")
        self.assertTrue(res["ok"])

    def test_18_uncovered_key_still_red_when_other_key_registered(self):
        srcs = make_sources(doc="0.9.99", main_suite=1)
        e = d2_conflict()
        e["keys"] = ["doc_version"]
        res = self.run_face(make_registry(srcs, [e]), doc="0.9.100", main_suite=2)
        self.assertEqual(res["unregistered"], ["unregistered_conflict:main_suite"])


# ---------------------------------------------------------------------------
# G5 stale_pointer
# ---------------------------------------------------------------------------
class G5StalePointer(_Base):
    def test_19_pointer_to_landed_batch_is_red(self):
        res = self.run_face(make_registry(),
                            pending="下一批 V79 = 跨账闸", landed={"79"})
        self.assertIn("stale_pointer", self.kinds(res))

    def test_20_pointer_to_future_batch_is_ok(self):
        res = self.run_face(make_registry(),
                            pending="下一批 V80 = ENV_DELTA", landed={"79"})
        self.assertTrue(res["ok"], res["fails"])

    def test_21_letter_suffix_batch_detected(self):
        res = self.run_face(make_registry(),
                            pending="下一批 V78a 已落地", landed={"78a"})
        self.assertIn("stale_pointer", self.kinds(res))

    def test_22_empty_note_not_red(self):
        res = self.run_face(make_registry(), pending="")
        self.assertTrue(res["ok"])


# ---------------------------------------------------------------------------
# G6 drift_after_register
# ---------------------------------------------------------------------------
class G6DriftAfterRegister(_Base):
    def test_23_registered_snapshot_changed(self):
        res = self.run_face(make_registry(conflicts=[d4_conflict({"main_suite": 1703})]),
                            main_suite=2000)
        self.assertIn("drift_after_register", self.kinds(res))

    def test_24_registered_snapshot_unchanged(self):
        res = self.run_face(make_registry(conflicts=[d4_conflict({"main_suite": 2000})]),
                            main_suite=2000)
        self.assertTrue(res["ok"], res["fails"])

    def test_25_non_tolerant_kind_skips_drift(self):
        srcs = make_sources(main_suite=2000)
        e = d0_conflict()
        e["observed_at_register"] = {"main_suite": 1}
        res = self.run_face(make_registry(srcs, [e]), main_suite=2000)
        self.assertNotIn("drift_after_register", self.kinds(res))

    def test_26_drift_reports_key_in_id(self):
        res = self.run_face(make_registry(conflicts=[d4_conflict({"main_suite": 1703})]),
                            main_suite=2000)
        self.assertTrue(any(":main_suite" in i for i in res["drifted"]))


# ---------------------------------------------------------------------------
# G7 intent_vs_blocker（最高优先）
# ---------------------------------------------------------------------------
class G7IntentVsBlocker(_Base):
    def test_27_markers_are_exact_six(self):
        self.assertEqual(len(cg.BLOCKER_AS_INTENT_MARKERS), 6)
        for m in ("决议不", "选择不", "不干", "永不",
                  "以后条件允许再做", "暂缓即取消"):
            self.assertIn(m, cg.BLOCKER_AS_INTENT_MARKERS)

    def test_28_text_claiming_carbon_refusal_is_red(self):
        res = self.run_face(make_registry(),
                            intent_texts=[{"where": D0_WHERE, "text": D0_WAS}])
        self.assertIn("intent_vs_blocker", self.kinds(res))

    def test_29_text_registered_as_blocker_not_intent_is_ok(self):
        res = self.run_face(make_registry(conflicts=[d0_conflict()]),
                            intent_texts=[{"where": D0_WHERE, "text": D0_WAS}])
        self.assertTrue(res["ok"], res["fails"])

    def test_30_was_field_with_marker_but_wrong_kind_is_red(self):
        res = self.run_face(make_registry(conflicts=[d0_conflict(kind="known_boundary")]))
        self.assertIn("intent_vs_blocker", self.kinds(res))

    def test_31_canon_conflict_judges_record_not_carbon(self):
        res = self.run_face(make_registry(conflicts=[d0_conflict(canon="碳基决议永不补")]),
                            carbon=CARBON)
        self.assertIn("intent_vs_blocker", self.kinds(res))
        self.assertTrue(any(":canon" in i for i in res["intent_vs_blocker"]))

    def test_32_disposition_must_say_blocker_not_intent(self):
        e = d0_conflict()
        e["disposition"] = "已登记"
        res = self.run_face(make_registry(conflicts=[e]))
        self.assertIn("intent_vs_blocker", self.kinds(res))

    def test_33_harmless_text_is_not_red(self):
        res = self.run_face(make_registry(),
                            intent_texts=[{"where": "README.md",
                                          "text": "本批不做 V80，按四步序排队"}])
        self.assertTrue(res["ok"], res["fails"])

    def test_34_registration_matches_by_filename(self):
        e = d0_conflict()
        e["where"] = "NOTE_20261113_HOLOAEON_S3_MIRROR_MODE.md"
        res = self.run_face(make_registry(conflicts=[e]),
                            intent_texts=[{"where": "NOTE_20261113_HOLOAEON_S3_MIRROR_MODE.md L1",
                                          "text": D0_WAS}])
        self.assertTrue(res["ok"], res["fails"])


# ---------------------------------------------------------------------------
# G8 口径差 / 边界合法登记不误红
# ---------------------------------------------------------------------------
class G8LegalDifferences(_Base):
    def test_35_caliber_difference_registered_not_red(self):
        res = self.run_face(make_registry(conflicts=[d2_conflict()]))
        self.assertTrue(res["ok"], res["fails"])
        self.assertIn("D2", res["registered_boundaries"])

    def test_36_runtime_snapshot_registered_not_red(self):
        res = self.run_face(make_registry(conflicts=[d4_conflict()]))
        self.assertTrue(res["ok"], res["fails"])
        self.assertIn("D4", res["registered_boundaries"])

    def test_37_known_boundary_registered_not_red(self):
        res = self.run_face(make_registry(conflicts=[d5_conflict()]))
        self.assertTrue(res["ok"], res["fails"])
        self.assertIn("D5", res["registered_boundaries"])

    def test_38_by_kind_counts_six_families(self):
        reg = make_registry(conflicts=[d0_conflict(), d2_conflict(), d4_conflict(),
                                       d5_conflict()])
        res = self.run_face(reg)
        self.assertEqual(res["ledger_conflicts"], 4)
        self.assertEqual(sorted(res["by_kind"]),
                         ["caliber_difference", "intent_vs_blocker",
                          "known_boundary", "runtime_snapshot"])


# ---------------------------------------------------------------------------
# G9 八只金丝雀（全红）
# ---------------------------------------------------------------------------
class G9Canaries(_Base):
    def test_39_c0_carbon_refusal_recorded_as_decision(self):
        """C0（最高优先）：删 D0 登记 + 把技术阻塞写成碳基决议 → intent_vs_blocker 红。"""
        reg = make_registry(conflicts=[])
        res = self.run_face(reg, intent_texts=[{"where": D0_WHERE, "text": D0_WAS}])
        self.assertFalse(res["ok"])
        self.assertIn("intent_vs_blocker", self.kinds(res))

    def test_40_c1_unregistered_cross_ledger_conflict(self):
        srcs = make_sources(doc="0.9.99")
        res = self.run_face(make_registry(srcs), doc="0.9.100")
        self.assertFalse(res["ok"])
        self.assertTrue(all(f["face"] == cg.FACE_CROSS_LEDGER for f in res["fails"]))

    def test_41_c2_deleted_caliber_registration(self):
        """C2：删掉口径登记，两值仍不同 → 未登记冲突红。"""
        srcs = make_sources(doc="0.9.99")
        res = self.run_face(make_registry(srcs, []), doc="0.9.100")
        self.assertFalse(res["ok"])
        self.assertIn("unregistered_conflict", self.kinds(res))

    def test_42_c3_pointer_points_to_landed_batch(self):
        res = self.run_face(make_registry(), pending="下一批 V79", landed={"79"})
        self.assertIn("stale_pointer", self.kinds(res))

    def test_43_c4_remote_tracking_cache_used_as_evidence(self):
        srcs = make_sources()
        srcs["five_site_head"]["authority"] = "git_remote_tracking_ref"
        res = self.run_face(make_registry(srcs))
        self.assertFalse(res["ok"])

    def test_44_c5_historical_key_value_changed(self):
        res = self.run_face(make_registry(conflicts=[d4_conflict({"main_suite": 1703})]),
                            main_suite=2000)
        self.assertIn("drift_after_register", self.kinds(res))

    def test_45_c6_self_digest_not_recomputed(self):
        reg = make_registry()
        reg["self_digest"] = "deadbeefdeadbeef"
        fails = cg.check_self_digest(reg)
        self.assertTrue(fails)
        self.assertEqual(fails[0]["face"], "determinism_self_digest")

    def test_46_c7_boundary_disguised_as_resolved(self):
        res = self.run_face(make_registry(conflicts=[d5_conflict("resolved")]))
        self.assertFalse(res["ok"])
        self.assertTrue(any("conflict_kind" in f["id"] for f in res["fails"]))


# ---------------------------------------------------------------------------
# G10 self_digest 自洽 + 零第三方依赖
# ---------------------------------------------------------------------------
class G10DeterminismAndDeps(_Base):
    def test_47_self_digest_stable_and_recomputed(self):
        reg = make_registry(conflicts=[d0_conflict(), d2_conflict()])
        d1 = cg.self_digest(reg)
        d2 = cg.self_digest(reg)
        self.assertEqual(d1, d2)
        reg["self_digest"] = d1
        self.assertEqual(cg.check_self_digest(reg), [])

    def test_48_self_digest_ignores_own_field(self):
        reg = make_registry()
        reg["self_digest"] = "aaa"
        a = cg.self_digest(reg)
        reg["self_digest"] = "bbb"
        self.assertEqual(a, cg.self_digest(reg))

    def test_49_no_drift_on_clean_registry(self):
        reg = make_registry()
        reg["self_digest"] = cg.self_digest(reg)
        self.assertEqual(cg.check_self_digest(reg), [])

    def test_50_claims_gate_imports_stdlib_only(self):
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "holoaeon", "claims_gate.py")
        tree = ast.parse(open(path, encoding="utf-8").read())
        allowed = {"ast", "hashlib", "json", "os", "re", "sys", "datetime",
                   "collections", "itertools", "typing", "types", "time"}
        stdlib = set(getattr(sys, "stdlib_module_names", ())) or set()
        stdlib |= set(sys.builtin_module_names) | allowed
        local = {"holoaeon"}
        bad = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    top = a.name.split(".")[0]
                    if top not in stdlib and top not in local:
                        bad.append(a.name)
            elif isinstance(node, ast.ImportFrom):
                top = (node.module or "").split(".")[0]
                if node.level == 0 and top and top not in stdlib and top not in local:
                    bad.append(node.module)
        self.assertEqual(bad, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
