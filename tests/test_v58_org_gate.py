# -*- coding: utf-8 -*-
"""test_v58_org_gate —— V58 组织化推进件真 unittest（ring21）。

八组：编制/任务卡/调拨中枢/C03 G-M/适配器/耗散/批次/总闸+张量。
真实数据声明：build_team_registry 派生自 C18_NUMBERING（V55 在仓真实注册表）；
优先级演示权重取素材建议初值（可标定常量口径）。
"""

from __future__ import annotations

import unittest

from holoaeon.org_gate import (
    ADAPTER_BOUNDARIES,
    ADAPTER_STATES,
    ADAPTER_SUBMODULES,
    ADAPTER_TRANSITIONS,
    ALLOCATION_RULES,
    C03_GM_CRITERIA,
    DEEPENING_BATCHES,
    DISSIPATION_METRICS,
    DISSIPATION_REQUIREMENTS,
    GUIDE_SIX_STEPS,
    LEDGER_REQUIRED_FIELDS,
    ORG_ROLES,
    OrgGate,
    OrgTensor,
    PRIORITY_WEIGHTS,
    RESOURCE_TYPES,
    RESOURCES_REJECTED,
    SELF_QUESTIONS,
    TASK_CARD_REQUIRED_FIELDS,
    adapter_boundary_of,
    adapter_next,
    build_team_registry,
    check_batches,
    check_team_registry,
    compute_dissipation,
    c03_gate_report,
    fingerprint,
    priority_score,
    probe,
    validate_ledger_entry,
    validate_task_card,
)
from holoaeon.c18_cluster import C18_NUMBERING, HUB_IDS


class TestTeamRegistry(unittest.TestCase):
    """一、18 分管小组编制（矩阵式双层）。"""

    def test_registry_18_teams(self):
        reg = build_team_registry()
        self.assertEqual(len(reg), 18)

    def test_registry_ids_match_c18(self):
        reg = build_team_registry()
        self.assertEqual([r["cang"] for r in reg], [c["id"] for c in C18_NUMBERING])

    def test_registry_repo_slugs_real(self):
        reg = build_team_registry()
        by_id = {r["cang"]: r["repo"] for r in reg}
        self.assertEqual(by_id["C01"], "holoaeon-c01-source")
        self.assertEqual(by_id["C03"], "holoaeon-c03-meridian")
        self.assertEqual(by_id["C18"], "holoaeon-c18-cosmos")

    def test_registry_five_roles(self):
        reg = build_team_registry()
        for r in reg:
            self.assertEqual(set(r["roles"]), set(ORG_ROLES))

    def test_registry_owner_unassigned_honest(self):
        reg = build_team_registry()
        self.assertTrue(all(r["owner"] is None for r in reg))  # 未指派即未上岗——零虚构

    def test_check_team_pass(self):
        r = check_team_registry()
        self.assertTrue(r["pass"], r["problems"])

    def test_self_pollution_rule(self):
        bad = build_team_registry()
        bad[0]["owner"] = "甲"
        bad[0]["recorder"] = "甲"  # 仓主=记录员——自证污染
        r = check_team_registry(bad)
        self.assertFalse(r["pass"])


class TestTaskCard(unittest.TestCase):
    """二、任务卡 Schema（四人组职能 × 小组交叉点）。"""

    def test_sample_card_pass(self):
        card = {"card_id": "TC-001", "function": "共振", "cang": "C10",
                "assignee": "适配员A", "acceptor": "四人组·共振智能体",
                "evidence": "共振带激活验收"}
        r = validate_task_card(card)
        self.assertTrue(r["pass"], r["problems"])

    def test_missing_field_fail(self):
        card = {"card_id": "TC-002", "function": "结构", "cang": "C01",
                "assignee": "A", "acceptor": "B"}  # 缺 evidence
        r = validate_task_card(card)
        self.assertFalse(r["pass"])

    def test_assignee_equals_acceptor_fail(self):
        card = {"card_id": "TC-003", "function": "语义", "cang": "C05",
                "assignee": "甲", "acceptor": "甲", "evidence": "x"}
        r = validate_task_card(card)
        self.assertFalse(r["pass"])

    def test_function_outside_quartet_fail(self):
        card = {"card_id": "TC-004", "function": "后勤", "cang": "C02",
                "assignee": "A", "acceptor": "B", "evidence": "x"}
        r = validate_task_card(card)
        self.assertFalse(r["pass"])

    def test_six_required_fields(self):
        self.assertEqual(len(TASK_CARD_REQUIRED_FIELDS), 6)


class TestArbiter(unittest.TestCase):
    """三、资源调拨中枢（优先级公式+调拨规则+账本）。"""

    def test_five_resource_types(self):
        self.assertEqual(len(RESOURCE_TYPES), 5)

    def test_resonance_quota_rejected_with_reason(self):
        self.assertEqual(len(RESOURCES_REJECTED), 1)
        self.assertIn("108641", RESOURCES_REJECTED[0][1])  # 弃因留痕（V55 裁决维持）

    def test_priority_weights_sum_one(self):
        self.assertAlmostEqual(sum(PRIORITY_WEIGHTS.values()), 1.0, places=9)
        self.assertEqual(len(PRIORITY_WEIGHTS), 5)

    def test_priority_hub_higher_than_plain(self):
        self.assertGreater(priority_score("C03"), priority_score("C01"))

    def test_priority_starvation_penalty(self):
        self.assertLess(priority_score("C01", starved_ticks=3), priority_score("C01"))

    def test_priority_blockage_raises(self):
        self.assertGreater(priority_score("C01", blocked_downstream=6),
                           priority_score("C01", blocked_downstream=0))

    def test_priority_phase_match_bonus(self):
        self.assertGreater(priority_score("C05", phase_now="木"),
                           priority_score("C05", phase_now="火"))

    def test_priority_deterministic(self):
        self.assertEqual(priority_score("C03"), priority_score("C03"))  # 确定性（同输入同输出）

    def test_allocation_rules_five(self):
        self.assertEqual(len(ALLOCATION_RULES), 5)

    def test_ledger_entry_pass_and_fail(self):
        good = {"tick": 1, "resource": "心跳时隙", "amount": 2,
                "granted_to": "C03", "priority_value": 0.3, "recycled": False}
        self.assertTrue(validate_ledger_entry(good)["pass"])
        bad = dict(good)
        del bad["priority_value"]
        self.assertFalse(validate_ledger_entry(bad)["pass"])

    def test_ledger_six_fields(self):
        self.assertEqual(len(LEDGER_REQUIRED_FIELDS), 6)


class TestC03Gate(unittest.TestCase):
    """四、C03 经络先行 G-M 门禁（三态诚实）。"""

    def test_gm_six_criteria(self):
        self.assertEqual(len(C03_GM_CRITERIA), 6)

    def test_gm_two_pass_four_wait(self):
        r = c03_gate_report()
        self.assertEqual(r["states"]["同构校验"], "PASS")
        self.assertEqual(r["states"]["回滚"], "PASS")
        for k in ("12 通道", "事件传播", "阻塞机制", "衰减与终止"):
            self.assertEqual(r["states"][k], "WAIT")  # 依赖领域实现与连通件——不虚报

    def test_gm_not_passed_yet(self):
        r = c03_gate_report()
        self.assertFalse(r["pass"])

    def test_gm_hard_rule_recorded(self):
        r = c03_gate_report()
        self.assertIn("禁止启动", r["hard_rule"])
        self.assertIn("总线仓", r["upgrade"])


class TestAdapter(unittest.TestCase):
    """五、自动适配模块（六子模块+状态机+三边界）。"""

    def test_six_submodules(self):
        self.assertEqual(len(ADAPTER_SUBMODULES), 6)

    def test_happy_path_transitions(self):
        state = "IDLE"
        for event in ("DETECTED", "DIFFED", "MIGRATED", "VERIFIED", "COMMITTED"):
            state = adapter_next(state, event)
        self.assertEqual(state, "COMMITTED")

    def test_conflict_path(self):
        state = adapter_next("DIFFED", "CONFLICT")
        state = adapter_next(state, "ESCALATED")
        self.assertEqual(state, "ESCALATED")

    def test_failed_rollback_path(self):
        state = adapter_next("MIGRATED", "FAILED")
        state = adapter_next(state, "ROLLBACK")
        state = adapter_next(state, "ESCALATED")
        self.assertEqual(state, "ESCALATED")

    def test_illegal_transition_rejected(self):
        with self.assertRaises(ValueError):
            adapter_next("IDLE", "COMMITTED")  # 跳步——状态机写死防漂移

    def test_ten_states(self):
        self.assertEqual(len(ADAPTER_STATES), 10)
        self.assertEqual(set(ADAPTER_TRANSITIONS), set(ADAPTER_STATES))

    def test_boundary_tiers(self):
        self.assertEqual(set(ADAPTER_BOUNDARIES), {"可自动", "须人审", "禁止自动"})

    def test_boundary_of_known(self):
        self.assertEqual(adapter_boundary_of("目录补齐"), "可自动")
        self.assertEqual(adapter_boundary_of("共振带语义重定义"), "须人审")
        self.assertEqual(adapter_boundary_of("绕过门禁"), "禁止自动")

    def test_boundary_of_unknown_raises(self):
        with self.assertRaises(ValueError):
            adapter_boundary_of("未知动作")  # 未知不默认可自动


class TestDissipation(unittest.TestCase):
    """六、耗散结构耦合（五要件+D1-D6 口径）。"""

    def test_five_requirements(self):
        self.assertEqual(len(DISSIPATION_REQUIREMENTS), 5)
        for r in DISSIPATION_REQUIREMENTS:
            self.assertEqual(set(r), {"requirement", "engineering", "evidence"})

    def test_six_metrics(self):
        self.assertEqual(len(DISSIPATION_METRICS), 6)
        ids = [m[0] for m in DISSIPATION_METRICS]
        self.assertEqual(ids, ["D1", "D2", "D3", "D4", "D5", "D6"])

    def test_compute_without_flows_not_measured(self):
        r = compute_dissipation()  # 无真实流——零虚构不假报
        self.assertFalse(r["measured"])
        self.assertIsNone(r["D1"])
        self.assertIn("连通件未落", r["reason"])

    def test_compute_with_flows_measured(self):
        r = compute_dissipation(flows=[1.0, 2.0, 3.0], edge_changes=[0.5, 0.5])
        self.assertTrue(r["measured"])
        self.assertAlmostEqual(r["D1"], 2.0, places=3)
        self.assertAlmostEqual(r["D2"], 1.0 / 6.0, places=3)

    def test_compute_deterministic(self):
        a = compute_dissipation(flows=[1, 1], edge_changes=[1])
        b = compute_dissipation(flows=[1, 1], edge_changes=[1])
        self.assertEqual((a["D1"], a["D2"]), (b["D1"], b["D2"]))


class TestBatches(unittest.TestCase):
    """七、领域深化批次表（B0-B6 重构口径——骨架已建成）。"""

    def test_seven_batches(self):
        self.assertEqual(len(DEEPENING_BATCHES), 7)

    def test_18_cangs_covered_once(self):
        flat = [c for b in DEEPENING_BATCHES for c in b["cangs"]]
        self.assertEqual(len(flat), 18)
        self.assertEqual(len(set(flat)), 18)
        self.assertEqual(sorted(flat), sorted([c["id"] for c in C18_NUMBERING]))

    def test_b0_is_c03_first(self):
        self.assertEqual(DEEPENING_BATCHES[0]["cangs"], ("C03",))

    def test_batch_sizes_1_to_3(self):
        for b in DEEPENING_BATCHES:
            self.assertLessEqual(len(b["cangs"]), 3)  # 2-3 仓/批口径（B0 单仓先行例外）

    def test_check_batches_pass(self):
        r = check_batches()
        self.assertTrue(r["pass"], r["problems"])

    def test_batches_note_reconstruction(self):
        r = check_batches()
        self.assertIn("重构口径", r["note"])  # 建仓叙事→深化批次的诚实化留痕


class TestGateMainTensor(unittest.TestCase):
    """八、总闸+张量（引导六步/自我追问/组织张量）。"""

    def test_self_check_all_green(self):
        sc = OrgGate().self_check()
        self.assertTrue(sc["pass"], sc["problems"])

    def test_summary_report_keys(self):
        rep = OrgGate().summary_report()
        for key in ("ring", "module", "self_check", "c03_gate",
                    "dissipation_metrics", "guide_steps", "batches"):
            self.assertIn(key, rep)
        self.assertEqual(rep["ring"], 21)

    def test_guide_six_steps(self):
        self.assertEqual(len(GUIDE_SIX_STEPS), 6)

    def test_self_questions_six(self):
        self.assertEqual(len(SELF_QUESTIONS), 6)
        joined = " ".join(SELF_QUESTIONS)
        self.assertIn("真实产出", joined)  # 与 V56 四问同源精神
        self.assertIn("rollback_token", joined)

    def test_tensor_bundle_and_similarity(self):
        t = OrgTensor()
        va = t.bundle(["C03"], ["仓主", "记录员"])
        vb = t.bundle(["C03"], ["仓主", "记录员"])
        self.assertEqual(t.similarity(va, vb), 1.0)

    def test_tensor_role_validation(self):
        t = OrgTensor()
        with self.assertRaises(ValueError):
            t.role_axis("大队长")  # 须五岗之一

    def test_fingerprint_fields(self):
        f = fingerprint()
        self.assertEqual(f["module"], "org_gate")
        self.assertEqual(f["ring"], 21)
        self.assertEqual(f["adapter_states"], 10)
        self.assertEqual(f["dissipation_metrics"], 6)
        self.assertTrue(f["sha16"])

    def test_probe_priority_demo(self):
        p = probe()
        self.assertTrue(p["self_check"]["pass"])
        sp = p["sample_priority"]
        self.assertGreater(sp["C03_hub"], sp["C01_plain"])
        self.assertLess(sp["C01_starved"], sp["C01_plain"])

    def test_cli_zero(self):
        from holoaeon.org_gate import _main
        for cmd in ("run", "probe", "teams", "batches", "dissipation"):
            self.assertEqual(_main(["org_gate", cmd]), 0, cmd)


if __name__ == "__main__":
    unittest.main()
