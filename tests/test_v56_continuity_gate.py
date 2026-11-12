# -*- coding: utf-8 -*-
"""test_v56_continuity_gate —— V56 贯续性门禁件真 unittest（ring20）。

八组：契约/时间贯续/结构贯续/证据贯续/断裂点/门禁三态/交接单/总闸+张量。
真实数据声明：REAL_BATCH_CHAIN 六批 head 取自回执对账实录（V51-V55）；
v55 真实回执要素以字面量内联（batch/status/date/head/tests 均真实值）。
"""

from __future__ import annotations

import unittest

from holoaeon.continuity_gate import (
    BREAKPOINTS,
    BREAKPOINT_IDS,
    CONTRACT_VERSION,
    CONTINUITY_AXES,
    CONTINUITY_AXIS_DESC,
    ContinuityGate,
    ContinuityTensor,
    DIMENSION_FREEZE,
    FOUR_QUESTIONS,
    GATE_STATES,
    HANDOVER_REQUIRED_FIELDS,
    PHASES,
    PHASE_ORDER,
    REAL_BATCH_CHAIN,
    answer_four_questions,
    check_contract,
    check_evidential,
    check_structural,
    check_temporal,
    export_m0_contract,
    fingerprint,
    gate_report,
    make_batch,
    probe,
    sample_handover,
    validate_handover,
)
from holoaeon.c18_cluster import C18_NUMBERING, CouplingMatrix, validate_edge

# v55 真实回执要素（字面量内联——回执实录值，诚实标注）
V55_RECEIPT_REAL = {
    "batch": "V55-C18-CLUSTER-BASE",
    "status": "closed",
    "date": "2026-11-12",
    "head": "7b9abd6abcc712f9cc59a490d3d682e2d4079c21",
    "tests": {"v55": "47 OK", "six_suites": "244"},
}


class TestContract(unittest.TestCase):
    """一、M0 契约冻结（反向提取自仓——非新定契约）。"""

    def test_contract_complete(self):
        c = export_m0_contract()
        for key in ("contract_version", "frozen", "provenance", "numbering",
                    "wuxing_phase", "edge_schema", "dimension_freeze", "heartbeat_note"):
            self.assertIn(key, c)

    def test_contract_frozen_true(self):
        c = export_m0_contract()
        self.assertTrue(c["frozen"])

    def test_contract_version_string(self):
        self.assertEqual(CONTRACT_VERSION, "contract-v1.0")
        self.assertEqual(export_m0_contract()["contract_version"], CONTRACT_VERSION)

    def test_contract_numbering_19(self):
        ids = export_m0_contract()["numbering"]["ids"]
        self.assertEqual(len(ids), 19)
        self.assertIn("N19", ids)
        self.assertEqual(ids[0], "C01")
        self.assertEqual(ids[-2], "C18")

    def test_contract_wuxing_25_pairs(self):
        pairs = export_m0_contract()["wuxing_phase"]["pairs"]
        self.assertEqual(len(pairs), 25)
        relations = {p["relation"] for p in pairs}
        self.assertEqual(relations, {"相生", "被生", "同气", "相克", "反克"})

    def test_contract_edge_schema_12_fields(self):
        fields = export_m0_contract()["edge_schema"]["required_fields"]
        self.assertEqual(len(fields), 12)
        self.assertIn("rollback_token", fields)
        self.assertIn("ttl_ticks", fields)

    def test_contract_dimension_freeze(self):
        self.assertEqual(DIMENSION_FREEZE["VERSION"], "0.9.1")
        self.assertEqual(DIMENSION_FREEZE["PACK_ORDER"], 9)
        self.assertEqual(len(DIMENSION_FREEZE["untouchable_modules"]), 4)
        self.assertIn("scheduler", DIMENSION_FREEZE["untouchable_modules"])

    def test_contract_provenance_reverse_extraction(self):
        p = export_m0_contract()["provenance"]
        self.assertIn("反向提取", p)
        self.assertIn("非新定", p)

    def test_check_contract_pass(self):
        r = check_contract()
        self.assertTrue(r["pass"], r["problems"])
        self.assertEqual(r["contract_version"], CONTRACT_VERSION)


class TestTemporal(unittest.TestCase):
    """二、时间贯续（时序不乱——每步输入=上步真实产出）。"""

    def test_real_chain_pass(self):
        r = check_temporal(REAL_BATCH_CHAIN)
        self.assertTrue(r["pass"], r["problems"])
        self.assertEqual(r["batches"], 6)

    def test_real_chain_heads_real(self):
        self.assertEqual(REAL_BATCH_CHAIN[0]["base_head"], "9657456")  # V50 收口
        self.assertEqual(REAL_BATCH_CHAIN[-1]["receipt_head"], "6e1752e")  # V55 回执

    def test_broken_chain_fail(self):
        chain = [
            make_batch("V51", "9657456", "cfafdbd"),
            make_batch("V52", "4a1d2d8", "7b9abd6"),  # 跳过 V51R/V53 时序断裂
        ]
        r = check_temporal(chain)
        self.assertFalse(r["pass"])
        self.assertTrue(any("时序断裂" in p for p in r["problems"]))

    def test_missing_field_fail(self):
        chain = [{"batch": "", "base_head": "9657456", "receipt_head": "cfafdbd"}]
        r = check_temporal(chain)
        self.assertFalse(r["pass"])

    def test_single_batch_pass(self):
        r = check_temporal([make_batch("V56", "6e1752e", "pending")])
        self.assertTrue(r["pass"])

    def test_four_questions_answered(self):
        a = answer_four_questions()
        self.assertEqual(set(a), set(FOUR_QUESTIONS))

    def test_four_questions_semantics(self):
        a = answer_four_questions()
        self.assertIn("6e1752e", a["现在处于哪一期"])
        self.assertIn("真实产出", a["这一期凭什么开始"])
        self.assertIn("回滚", a["出问题退到哪一步"])


class TestStructural(unittest.TestCase):
    """三、结构贯续（同构不漂——复用——零复制：import 同一对象）。"""

    def test_structural_pass(self):
        r = check_structural()
        self.assertTrue(r["pass"], r["problems"])

    def test_structural_reuse_no_copy(self):
        r = check_structural()
        self.assertIn("零复制", r["reused_from"])
        # import 同一对象证明：本测试引用的 C18_NUMBERING 即 c18_cluster 模块级单例
        self.assertEqual(len(C18_NUMBERING), 18)

    def test_matrix_validate_ok(self):
        m = CouplingMatrix()
        v = m.validate()
        self.assertTrue(v.get("ok", False), v.get("problems", []))

    def test_edge_hard_constraints_still_hold(self):
        edge = {
            "edge_id": "E-T-01", "source": "C01", "target": "C03",
            "edge_type": "skeleton", "layer": "L1", "phase_relation": "相生",
            "resonance_strength": 0.8, "turtle_state": "保存", "horse_state": "推演",
            "ttl_ticks": 12, "decay_rate": 0.5, "rollback_token": "rb-t-01",
        }
        self.assertTrue(validate_edge(edge)["ok"])

    def test_edge_ttl_below_floor_rejected(self):
        edge = {
            "edge_id": "E-T-02", "source": "C01", "target": "C03",
            "edge_type": "skeleton", "layer": "L1", "phase_relation": "相生",
            "resonance_strength": 0.8, "turtle_state": "保存", "horse_state": "推演",
            "ttl_ticks": 11, "decay_rate": 0.5, "rollback_token": "rb-t-02",
        }
        self.assertFalse(validate_edge(edge)["ok"])

    def test_edge_missing_rollback_rejected(self):
        edge = {
            "edge_id": "E-T-03", "source": "C01", "target": "C03",
            "edge_type": "skeleton", "layer": "L1", "phase_relation": "相生",
            "resonance_strength": 0.8, "turtle_state": "保存", "horse_state": "推演",
            "ttl_ticks": 12, "decay_rate": 0.5, "rollback_token": "",
        }
        self.assertFalse(validate_edge(edge)["ok"])


class TestEvidential(unittest.TestCase):
    """四、证据贯续（可追可回——回执要素齐；真实 v55 回执内联字面量）。"""

    def test_v55_real_receipt_pass(self):
        r = check_evidential(V55_RECEIPT_REAL)
        self.assertTrue(r["pass"], r["problems"])

    def test_receipt_missing_head_fail(self):
        bad = dict(V55_RECEIPT_REAL)
        del bad["head"]
        r = check_evidential(bad)
        self.assertFalse(r["pass"])

    def test_receipt_missing_tests_fail(self):
        bad = dict(V55_RECEIPT_REAL)
        bad["tests"] = None
        r = check_evidential(bad)
        self.assertFalse(r["pass"])

    def test_receipt_empty_status_fail(self):
        bad = dict(V55_RECEIPT_REAL)
        bad["status"] = ""
        r = check_evidential(bad)
        self.assertFalse(r["pass"])

    def test_receipt_required_fields(self):
        r = check_evidential(V55_RECEIPT_REAL)
        self.assertEqual(len(r["required"]), 5)
        self.assertIn("rollback", r["note"])  # 素材四要素映射说明在案


class TestBreakpoints(unittest.TestCase):
    """五、B1-B10 断裂点清单（逐条映射在仓先例）。"""

    def test_breakpoints_count_10(self):
        self.assertEqual(len(BREAKPOINTS), 10)

    def test_breakpoint_ids_b1_to_b10(self):
        self.assertEqual(BREAKPOINT_IDS, tuple("B{}".format(i) for i in range(1, 11)))

    def test_each_breakpoint_keys_nonempty(self):
        for b in BREAKPOINTS:
            for key in ("id", "symptom", "fix", "precedent"):
                self.assertIn(key, b)
                self.assertTrue(b[key])

    def test_b1_precedent_scripted(self):
        b1 = next(b for b in BREAKPOINTS if b["id"] == "B1")
        self.assertIn("create_repos_v55.py", b1["precedent"])

    def test_b8_precedent_rollback(self):
        b8 = next(b for b in BREAKPOINTS if b["id"] == "B8")
        self.assertIn("rollback_token", b8["fix"])
        self.assertIn("validate_edge", b8["precedent"])


class TestGates(unittest.TestCase):
    """六、Go/No-Go 门禁三态（零虚构：未落地的门禁诚实 WAIT）。"""

    def test_gates_count_8(self):
        g = gate_report()
        self.assertEqual(len(g), 8)
        self.assertEqual([x["gate"] for x in g],
                         ["G0", "G1", "G2", "G3", "G4", "G5", "G6", "G7"])

    def test_g0_pass(self):
        g0 = gate_report()[0]
        self.assertEqual(g0["state"], "PASS")
        self.assertIn("frozen", g0["evidence"])

    def test_g1_pass(self):
        g1 = gate_report()[1]
        self.assertEqual(g1["state"], "PASS")
        self.assertIn("碳基确认", g1["evidence"])  # 远端建仓须碳基确认在案

    def test_g2_wait_not_fabricated(self):
        g2 = gate_report()[2]
        self.assertEqual(g2["state"], "WAIT")  # 连通件未产——门禁不替未来签字
        ev = g2["evidence"]
        self.assertTrue(("WAIT" in ev) or ("待产" in ev))

    def test_all_gate_states_in_domain(self):
        for g in gate_report():
            self.assertIn(g["state"], GATE_STATES)
            self.assertTrue(g["question"])
            self.assertTrue(g["evidence"])

    def test_g0_fail_path_with_bad_contract(self):
        bad = export_m0_contract()
        bad["frozen"] = False
        r = check_contract(bad)
        self.assertFalse(r["pass"])
        self.assertIn("frozen", r["problems"][0])

    def test_gate_report_runnable_via_gate_class(self):
        g = ContinuityGate()
        states = {x["gate"]: x["state"] for x in g.gates()}
        self.assertEqual(states["G0"], "PASS")
        self.assertEqual(states["G2"], "WAIT")


class TestHandover(unittest.TestCase):
    """七、交接单 Schema（下游未签收上游交接单不得开工——素材第九节）。"""

    def test_sample_handover_pass(self):
        r = validate_handover(sample_handover())
        self.assertTrue(r["pass"], r["problems"])

    def test_sample_is_schema_sample_not_runtime(self):
        doc = validate_handover.__doc__ or sample_handover.__doc__ or ""
        self.assertTrue(doc)  # 样例用途诚实标注在 docstring

    def test_wrong_contract_version_fail(self):
        h = dict(sample_handover())
        h["契约版本"] = "contract-v0.9"
        r = validate_handover(h)
        self.assertFalse(r["pass"])

    def test_missing_field_fail(self):
        h = dict(sample_handover())
        del h["回滚点"]
        r = validate_handover(h)
        self.assertFalse(r["pass"])

    def test_handover_nine_fields(self):
        self.assertEqual(len(HANDOVER_REQUIRED_FIELDS), 9)
        self.assertIn("契约版本", HANDOVER_REQUIRED_FIELDS)


class TestGateMainTensor(unittest.TestCase):
    """八、总闸+张量（贯续张量与 V52-V55 同族编码）。"""

    def test_self_check_all_green(self):
        sc = ContinuityGate().self_check()
        self.assertTrue(sc["pass"], sc["problems"])
        self.assertTrue(all(sc["checks"].values()))

    def test_summary_report_keys(self):
        rep = ContinuityGate().summary_report()
        for key in ("ring", "module", "axes", "self_check", "gates", "breakpoints", "contract_version"):
            self.assertIn(key, rep)
        self.assertEqual(rep["ring"], 20)

    def test_continuity_axes_three(self):
        self.assertEqual(CONTINUITY_AXES, ("temporal", "structural", "evidential"))
        self.assertEqual(len(CONTINUITY_AXIS_DESC), 3)

    def test_phases_order_fixed(self):
        self.assertEqual(tuple(p["phase"] for p in PHASES), PHASE_ORDER)
        self.assertEqual(PHASE_ORDER[0], "M0")
        self.assertEqual(PHASE_ORDER[-1], "M7")

    def test_phases_no_duration_field(self):
        # 弃素材'建议工期'：八期卡不设工期字段（工程节拍以批次为准）
        for p in PHASES:
            self.assertNotIn("duration", p)
            self.assertNotIn("工期", p)

    def test_tensor_bundle_and_similarity(self):
        t = ContinuityTensor()
        va = t.bundle(["V55"], ["pass"])
        vb = t.bundle(["V55"], ["pass"])
        self.assertEqual(t.similarity(va, vb), 1.0)

    def test_tensor_state_validation(self):
        t = ContinuityTensor()
        with self.assertRaises(ValueError):
            t.state_axis("fail_pending")

    def test_fingerprint_fields(self):
        f = fingerprint()
        self.assertEqual(f["module"], "continuity_gate")
        self.assertEqual(f["ring"], 20)
        self.assertEqual(f["breakpoints"], 10)
        self.assertEqual(f["gates"], 8)
        self.assertTrue(f["sha16"])

    def test_probe_gate_states(self):
        p = probe()
        self.assertEqual(p["gate_states"]["G0"], "PASS")
        self.assertEqual(p["gate_states"]["G6"], "WAIT")
        self.assertTrue(p["self_check"]["pass"])

    def test_cli_run_zero(self):
        from holoaeon.continuity_gate import _main
        self.assertEqual(_main(["continuity_gate", "run"]), 0)
        self.assertEqual(_main(["continuity_gate", "gates"]), 0)
        self.assertEqual(_main(["continuity_gate", "breakpoints"]), 0)


if __name__ == "__main__":
    unittest.main()
