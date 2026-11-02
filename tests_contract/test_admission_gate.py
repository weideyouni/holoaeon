# -*- coding: utf-8 -*-
"""B7 准入规则核旁挂单测（10 项）。只测判定，不跑闸、不签字、不联网。"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from holoaeon.fusion_upgrade import admission as ADM  # noqa: E402


def row(**kw):
    base = {"batch": "B7-1", "ticket": "data/B7_准入票据_B7-1.md", "skill": "s1",
            "target_mechanism": "semantic_bus", "module": "检索", "usage_class": "K",
            "gate_v3_gate": "32/32", "gate_unittest": "34/34",
            "gate_skill_matrix": "17/17", "gate_redline": "69/69",
            "signature_status": "PENDING", "signer": "", "signed_at": "",
            "decision": ADM.DECISION_WAITING, "note": ""}
    base.update(kw)
    return base


GATES_OK = {g: {"passed": 1, "total": 1, "ok": True} for g in ADM.GATE_IDS}


class TestRules(unittest.TestCase):
    def test_01_rule_constants(self):
        self.assertEqual(ADM.MAX_PER_BATCH, 5)
        self.assertEqual(ADM.MAX_CUMULATIVE, 15)
        self.assertEqual(len(ADM.HARD_GATES), 4)
        self.assertEqual(ADM.GATE_IDS, ("v3_gate", "unittest", "skill_matrix", "redline"))

    def test_02_rules_seal_stable(self):
        d1 = ADM.rules_doc()
        d2 = ADM.rules_doc()
        self.assertEqual(d1["sha256"], d2["sha256"])
        self.assertEqual(len(d1["sha256"]), 64)
        self.assertNotEqual(d1["sha256"], "")

    def test_03_ledger_roundtrip(self):
        rows = [row(skill="a"), row(skill="b")]
        text = ADM.dump_ledger(rows)
        back = ADM.parse_ledger(text)
        self.assertEqual([r["skill"] for r in back], ["a", "b"])
        self.assertEqual(ADM.dump_ledger(back), text)

    def test_04_header_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            ADM.parse_ledger("a,b,c\n1,2,3\n")


class TestValidate(unittest.TestCase):
    def test_05_per_batch_limit(self):
        rows = [row(skill="s%d" % i) for i in range(6)]
        res = ADM.validate(rows, gate_results=GATES_OK)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertFalse(next(c for c in res["checks"] if c["id"] == "A1")["ok"])

    def test_06_cumulative_limit(self):
        rows = []
        for b in ("B7-1", "B7-2", "B7-3"):
            for i in range(5):
                rows.append(row(batch=b, skill="%s_%d" % (b, i), decision=ADM.DECISION_ADMITTED,
                                signature_status="SIGNED", signer="张三", signed_at="2026-11-02"))
        self.assertEqual(len(rows), 15)
        res = ADM.validate(rows, gate_results=GATES_OK)
        self.assertTrue(next(c for c in res["checks"] if c["id"] == "A2")["ok"])
        rows.append(row(batch="B7-4", skill="x", decision=ADM.DECISION_ADMITTED,
                        signature_status="SIGNED", signer="张三", signed_at="2026-11-02"))
        res2 = ADM.validate(rows, gate_results=GATES_OK)
        self.assertFalse(next(c for c in res2["checks"] if c["id"] == "A2")["ok"])

    def test_07_unsigned_waits(self):
        res = ADM.validate([row()], gate_results=GATES_OK)
        self.assertEqual(res["verdict"], ADM.DECISION_WAITING)
        self.assertEqual(res["counts"]["admitted"], 0)

    def test_08_unsigned_cannot_admit(self):
        res = ADM.validate([row(decision=ADM.DECISION_ADMITTED)], gate_results=GATES_OK)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertFalse(next(c for c in res["checks"] if c["id"] == "A7")["ok"])

    def test_09_signed_needs_name_and_date(self):
        res = ADM.validate([row(decision=ADM.DECISION_ADMITTED, signature_status="SIGNED",
                                signer="张三", signed_at="")], gate_results=GATES_OK)
        self.assertFalse(next(c for c in res["checks"] if c["id"] == "A6")["ok"])

    def test_10_pool_gate_ticket(self):
        res = ADM.validate([row(skill="not_in_pool")], pool={"a", "b"},
                           ticket_texts={}, gate_results=GATES_OK)
        self.assertEqual(res["verdict"], "FAIL")
        ids = {c["id"]: c["ok"] for c in res["checks"]}
        self.assertFalse(ids["A3"])  # 票据缺失
        self.assertFalse(ids["A5"])  # 池外技能
        red = {g: {"passed": 0, "total": 0, "ok": False} for g in ADM.GATE_IDS}
        res2 = ADM.validate([row(skill="a")], pool={"a"},
                            ticket_texts={"B7-1": "准入票据"}, gate_results=red)
        self.assertFalse({c["id"]: c["ok"] for c in res2["checks"]}["A4"])


if __name__ == "__main__":
    unittest.main()
