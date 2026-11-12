# -*- coding: utf-8 -*-
"""tests/test_v62_meridian_link.py —— V62 经络链接模块测试套件（真 unittest）。

八组：注册表 import 对账/碳基点名对账/碎片装载/三态链接判定/穷举表/
汇总/台账/CLI+总闸。实测值固化（linked=13/pending=214/unlinked=23——
零虚构：无证据即挂起，全证据实测才 unlinked）。
"""
import json
import os
import sys
import tempfile
import unittest

from holoaeon import meridian_link as ml
from holoaeon.klein_projection import MECHANISMS as KLEIN_MECHANISMS
from holoaeon.titan_evolver import MECHANISMS as TITAN_MECHANISMS
from holoaeon.holo_forge import HOLO_MECHANISMS
from holoaeon.concept_anatomy import CONCEPT_MAP


def _frag(repo):
    for r in ml.load_fragments():
        if r["repo"] == repo:
            return r
    raise KeyError(repo)


def _mech(mid):
    for m in ml.KERNEL_MECHANISMS:
        if m["id"] == mid:
            return m
    raise KeyError(mid)


# ============================================================ 一、注册表
class TestRegistry(unittest.TestCase):

    def test_registry_count_25(self):
        self.assertEqual(len(ml.KERNEL_MECHANISMS), 25)

    def test_layer_counts(self):
        layers = {}
        for m in ml.KERNEL_MECHANISMS:
            layers[m["layer"]] = layers.get(m["layer"], 0) + 1
        self.assertEqual(layers, {"公理": 2, "矩阵": 2, "核心机制": 11,
                                  "耗散验证": 2, "经络子机制": 8})

    def test_core_matches_klein(self):
        core = [m for m in ml.KERNEL_MECHANISMS if m["layer"] == "核心机制"]
        self.assertEqual([(m["id"], m["name"]) for m in core],
                         [(m["id"], m["name"]) for m in KLEIN_MECHANISMS])

    def test_core_matches_titan(self):
        core = [m for m in ml.KERNEL_MECHANISMS if m["layer"] == "核心机制"]
        self.assertEqual([(m["id"], m["name"]) for m in core],
                         [(m["id"], m["name"]) for m in TITAN_MECHANISMS])

    def test_keys_base_from_klein(self):
        """指针纪律：M01-M11 键基座=klein 原表关键词 import 直用（前缀一致）。"""
        klein_keys = {m["id"]: tuple(m["keywords"]) for m in KLEIN_MECHANISMS}
        for m in ml.KERNEL_MECHANISMS:
            if m["layer"] == "核心机制":
                base = klein_keys[m["id"]]
                self.assertEqual(tuple(m["keys"])[:len(base)], base,
                                 "机制 {} 键基座漂移".format(m["id"]))

    def test_holo_forge_variants_covered(self):
        ids = {m["id"] for m in ml.KERNEL_MECHANISMS}
        for vname in HOLO_MECHANISMS:
            self.assertIn(ml.NAME_VARIANTS.get(vname), ids,
                          "holo_forge 异形名无覆盖：{}".format(vname))

    def test_concept_map_covered(self):
        ids = {m["id"] for m in ml.KERNEL_MECHANISMS}
        for cname in CONCEPT_MAP:
            self.assertIn(ml.CONCEPT_COVERAGE.get(cname), ids,
                          "CONCEPT_MAP 概念无覆盖：{}".format(cname))

    def test_matrix_constants(self):
        from holoaeon.packs.topology_resonance_pack import (
            MATRIX_ROWS, MATRIX_COLS, LOGICAL_POSITIONS, ACTIVE_NODES,
            EMERGENCE_THRESHOLD, RESONANCE_THRESHOLD, DISSIPATION_ENTROPY_MAX,
            MANDALA_TOTAL)
        self.assertEqual((MATRIX_ROWS, MATRIX_COLS, LOGICAL_POSITIONS),
                         (1331, 1331, 1771561))
        self.assertEqual((ACTIVE_NODES, EMERGENCE_THRESHOLD), (108641, 108641))
        self.assertEqual((RESONANCE_THRESHOLD, DISSIPATION_ENTROPY_MAX,
                          MANDALA_TOTAL), (0.75, 0.95, 9))

    def test_sub_funcs_callable(self):
        self.assertEqual(len(ml.SUB_MECH_FUNCS), 8)
        for sid, fn in ml.SUB_MECH_FUNCS.items():
            self.assertTrue(callable(fn), "子机制函数不可调用：{}".format(sid))

    def test_no_duplicate_ids(self):
        ids = [m["id"] for m in ml.KERNEL_MECHANISMS]
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_mech_has_keys_and_anchors(self):
        for m in ml.KERNEL_MECHANISMS:
            self.assertTrue(m["keys"], "无链接键：{}".format(m["id"]))
            self.assertTrue(m["anchors"], "无锚点：{}".format(m["id"]))
            self.assertTrue(m["note"], "无注记：{}".format(m["id"]))

    def test_registry_check_pass(self):
        res = ml.check_registry()
        self.assertTrue(res["pass"], res["problems"])


# ============================================================ 二、碳基点名
class TestNamedByCarbon(unittest.TestCase):

    def test_named_17(self):
        self.assertEqual(len(ml.NAMED_BY_CARBON), 17)

    def test_named_distinct_17(self):
        self.assertEqual(len({mid for _, mid in ml.NAMED_BY_CARBON}), 17)

    def test_named_rounds_4_10_3(self):
        rounds = [len([1 for _, mid in ml.NAMED_BY_CARBON[:4]]),
                  len([1 for _, mid in ml.NAMED_BY_CARBON[4:14]]),
                  len([1 for _, mid in ml.NAMED_BY_CARBON[14:]])]
        self.assertEqual(rounds, [4, 10, 3])

    def test_named_round1(self):
        for label, mid in ml.NAMED_BY_CARBON[:4]:
            self.assertIn(_mech(mid)["name"], ("全息", "自组织相似性",
                                               "自组织耗散", "共振节点"))

    def test_named_check_pass(self):
        res = ml.check_named()
        self.assertTrue(res["pass"], res["problems"])

    def test_unnamed_eight_in_axis(self):
        """包括但不限于兜底：未点名 8 位仍在轴（import 对账承载）。"""
        named_ids = {mid for _, mid in ml.NAMED_BY_CARBON}
        all_ids = {m["id"] for m in ml.KERNEL_MECHANISMS}
        self.assertEqual(sorted(all_ids - named_ids),
                         ["A2", "C2", "M03", "M08", "M09", "M10", "M11", "R8"])


# ============================================================ 三、碎片装载
class TestFragments(unittest.TestCase):

    def test_fragments_10(self):
        self.assertEqual(len(ml.load_fragments()), 10)

    def test_fragments_all_unverified(self):
        for r in ml.load_fragments():
            self.assertEqual(r["verify_status"], "unverified")

    def test_fragments_legs_valid(self):
        legs = sorted({r["leg"] for r in ml.load_fragments()})
        self.assertEqual(legs, ["可观测", "总线", "编排"])

    def test_fragments_essence_only_kafka(self):
        with_ess = [r["repo"] for r in ml.load_fragments() if r.get("essence")]
        self.assertEqual(with_ess, ["apache/kafka"])


# ============================================================ 四、三态链接判定
class TestLinkCell(unittest.TestCase):

    def test_crewai_m08_linked_via_leg(self):
        cell = ml.link_cell(_frag("crewAIInc/crewAI"), _mech("M08"))
        self.assertEqual(cell["state"], "linked")
        self.assertIn(["编排", "leg"], cell["evidence"])

    def test_kafka_m04_linked_two_sources(self):
        cell = ml.link_cell(_frag("apache/kafka"), _mech("M04"))
        self.assertEqual(cell["state"], "linked")
        self.assertIn(["总线", "leg"], cell["evidence"])
        self.assertIn(["事件", "essence"], cell["evidence"])

    def test_kafka_m11_linked_via_essence_log(self):
        cell = ml.link_cell(_frag("apache/kafka"), _mech("M11"))
        self.assertEqual(cell["state"], "linked")
        self.assertIn(["日志", "essence"], cell["evidence"])

    def test_jaeger_m04_linked_via_name_trac(self):
        cell = ml.link_cell(_frag("jaegertracing/jaeger"), _mech("M04"))
        self.assertEqual(cell["state"], "linked")
        self.assertIn(["trac", "name"], cell["evidence"])

    def test_agent_framework_m02_linked_via_name(self):
        cell = ml.link_cell(_frag("microsoft/agent-framework"), _mech("M02"))
        self.assertEqual(cell["state"], "linked")
        self.assertIn(["agent", "name"], cell["evidence"])

    def test_pinpoint_m01_linked_leg_and_name(self):
        cell = ml.link_cell(_frag("pinpoint-apm/pinpoint"), _mech("M01"))
        self.assertEqual(cell["state"], "linked")
        self.assertIn(["可观测", "leg"], cell["evidence"])
        self.assertIn(["apm", "name"], cell["evidence"])

    def test_pending_for_null_essence(self):
        """essence null 的碎片无命中格=pending-evidence（V56 WAIT 先例）。"""
        cell = ml.link_cell(_frag("crewAIInc/crewAI"), _mech("R7"))
        self.assertEqual(cell["state"], "pending-evidence")
        self.assertEqual(cell["evidence"], [])

    def test_unlinked_only_kafka(self):
        """kafka（essence 在案）无命中格=unlinked——全证据实测确定性。"""
        cell = ml.link_cell(_frag("apache/kafka"), _mech("R7"))
        self.assertEqual(cell["state"], "unlinked")

    def test_kafka_unlinked_hilbert_honest(self):
        """诚实固化：kafka×希尔伯特空间无链接（essence 全证据实测无命中）。"""
        cell = ml.link_cell(_frag("apache/kafka"), _mech("R7"))
        self.assertEqual(cell["mech_name"], "希尔伯特空间")
        self.assertEqual(cell["state"], "unlinked")

    def test_evidence_sources_valid(self):
        for row in ml.load_fragments():
            for mech in ml.KERNEL_MECHANISMS:
                for kv in ml.link_cell(row, mech)["evidence"]:
                    self.assertIn(kv[1], ("name", "leg", "essence"))

    def test_cell_carries_mech_identity(self):
        cell = ml.link_cell(_frag("SigNoz/signoz"), _mech("M01"))
        self.assertEqual(cell["mech"], "M01")
        self.assertEqual(cell["mech_name"], "心跳")
        self.assertEqual(cell["layer"], "核心机制")


# ============================================================ 五、穷举表
class TestMeridianTable(unittest.TestCase):

    def test_table_250_cells(self):
        self.assertEqual(len(ml.build_meridian_table()), 250)

    def test_table_no_missing_pairs(self):
        table = ml.build_meridian_table()
        want = {(r["repo"], m["id"]) for r in ml.load_fragments()
                for m in ml.KERNEL_MECHANISMS}
        got = {(c["repo"], c["mech"]) for c in table}
        self.assertEqual(want, got)

    def test_table_states_valid(self):
        for c in ml.build_meridian_table():
            self.assertIn(c["state"], ("linked", "pending-evidence", "unlinked"))

    def test_table_deterministic(self):
        self.assertEqual(ml.build_meridian_table(), ml.build_meridian_table())

    def test_table_counts_measured(self):
        """实测值固化（零虚构）：linked=13/pending=214/unlinked=23。"""
        table = ml.build_meridian_table()
        counts = {"linked": 0, "pending-evidence": 0, "unlinked": 0}
        for c in table:
            counts[c["state"]] += 1
        self.assertEqual(counts, {"linked": 13, "pending-evidence": 214,
                                  "unlinked": 23})

    def test_linkage_check_pass(self):
        res = ml.check_linkage()
        self.assertTrue(res["pass"], res["problems"])
        self.assertEqual(res["cells"], 250)

    def test_linkage_recompute_evidence(self):
        """linked 证据逐格可复算（判定是纯函数——同输入同输出）。"""
        res = ml.check_linkage()
        self.assertTrue(res["pass"])
        self.assertFalse(any("不可复算" in p for p in res["problems"]))


# ============================================================ 六、汇总
class TestSummary(unittest.TestCase):

    def test_summary_cang_c03(self):
        s = ml.meridian_summary()
        self.assertEqual(s["cang"], "holoaeon-c03-meridian")
        self.assertEqual(s["dim"], "D03")

    def test_summary_linked_by_mech(self):
        s = ml.meridian_summary()
        lm = {mid: info["linked"] for mid, info in s["by_mechanism"].items()}
        self.assertEqual(lm["M08"], 6)
        self.assertEqual(lm["M01"], 3)
        self.assertEqual(lm["M04"], 2)
        self.assertEqual(lm["M02"], 1)
        self.assertEqual(lm["M11"], 1)
        self.assertEqual(sum(lm.values()), 13)

    def test_summary_gm_gate_wait4_honest(self):
        """G-M 门禁 4 WAIT 如实携带（门禁不替未来签字）。"""
        s = ml.meridian_summary()
        self.assertFalse(s["gm_gate"]["pass"])
        self.assertEqual(len(s["gm_gate"]["wait_items"]), 4)

    def test_summary_hard_rule_present(self):
        s = ml.meridian_summary()
        self.assertIn("禁止启动任何领域深化批次", s["gm_gate"]["hard_rule"])


# ============================================================ 七、台账
class TestLedger(unittest.TestCase):

    def test_build_ledger_structure(self):
        ledger = ml.build_ledger()
        for k in ("project", "dim_id", "cang", "batch", "date", "schema",
                  "fragments", "mechanisms", "cells", "mechanism_axis",
                  "table", "summary", "seal"):
            self.assertIn(k, ledger)
        self.assertEqual(ledger["batch"], "V62-MERIDIAN-LINK")
        self.assertEqual(ledger["seal"], ml.SEAL)
        self.assertEqual(ledger["cells"], 250)
        self.assertEqual(len(ledger["mechanism_axis"]), 25)

    def test_ledger_deterministic_no_wallclock(self):
        """台账确定性：不含墙钟时间（日期为声明值）——同构两次逐字节相等。"""
        self.assertEqual(json.dumps(ml.build_ledger(), ensure_ascii=False,
                                    sort_keys=False),
                         json.dumps(ml.build_ledger(), ensure_ascii=False,
                                    sort_keys=False))

    def test_write_ledger_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "ledger.json")
            out = ml.write_ledger(p)
            self.assertEqual(out, p)
            with open(p, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            self.assertEqual(data["cells"], 250)
            self.assertEqual(len(data["table"]), 250)

    def test_ledger_table_matches_live(self):
        ledger = ml.build_ledger()
        self.assertEqual(ledger["table"], ml.build_meridian_table())


# ============================================================ 八、CLI+总闸
class TestCLIAndGate(unittest.TestCase):

    def test_cli_check_rc0(self):
        self.assertEqual(ml._main(["meridian_link", "check"]), 0)

    def test_cli_table_rc0(self):
        self.assertEqual(ml._main(["meridian_link", "table"]), 0)

    def test_cli_summary_rc0(self):
        self.assertEqual(ml._main(["meridian_link", "summary"]), 0)

    def test_cli_ledger_rc0(self):
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "ledger.json")
            self.assertEqual(
                ml._main(["meridian_link", "ledger", "--out", p]), 0)
            self.assertTrue(os.path.exists(p))

    def test_cli_table_out_writes(self):
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "t.json")
            self.assertEqual(
                ml._main(["meridian_link", "table", "--out", p]), 0)
            with open(p, "r", encoding="utf-8") as fh:
                self.assertEqual(json.load(fh)["cells"], 250)

    def test_cli_usage_rc1(self):
        self.assertEqual(ml._main(["meridian_link"]), 1)

    def test_cli_unknown_rc1(self):
        self.assertEqual(ml._main(["meridian_link", "bogus"]), 1)

    def test_cli_out_missing_path_rc1(self):
        self.assertEqual(ml._main(["meridian_link", "ledger", "--out"]), 1)

    def test_check_all_pass(self):
        res = ml.check_all()
        self.assertTrue(res["pass"])
        for sec in ("registry", "named", "linkage"):
            self.assertTrue(res[sec]["pass"], res[sec]["problems"])

    def test_check_all_seal(self):
        self.assertEqual(ml.check_all()["seal"], "潮起开门，潮落闭嘴")


if __name__ == "__main__":
    unittest.main()
