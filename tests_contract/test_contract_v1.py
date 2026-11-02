# -*- coding: utf-8 -*-
"""B1b 契约 v1 单测（旁挂套件，不并入主套 34 项，见 v3_gate.py 说明）。

运行：
  python -m unittest discover -s tests_contract -v

覆盖 data/contract_v1_draft.md §五 的 V1–V8 与 §四 的同参/异参判定：
  T01 V1 必填缺失        T02 V2 枚举越界        T03 V3 白名单越界
  T04 V4 涉医域红线      T05 V5 指纹不符        T06 V6 预算越界
  T07 同参同指纹（含跨进程一致性由 scripts/contract_interop.py 复核）
  T08 异参异指纹        T09 V7 剂量词拦截      T10 V8 未知顶层键
"""
import unittest

from holoaeon.fusion_upgrade import contract as c

COMMON = dict(source="local", target="ivsa", skill="fusion_plan", mechanism="meridian", lane="read")
RED = {"zero_dose": True, "c0_not_efficacy": True, "emergency_120": True}


def medical_doc(**over):
    payload = {"domain": "medical", "inputs": {"case_id": "R-001"}, "redlines": dict(RED)}
    payload.update(over.pop("payload_extra", {}))
    return c.build(**COMMON, payload=payload, **over)


def general_doc(**over):
    return c.build(source="local", target="gitee", skill="fusion_contract",
                   mechanism="semantic_bus", lane="read",
                   payload={"domain": "general"}, **over)


class ContractV1Test(unittest.TestCase):
    def test_01_required_missing(self):
        doc = general_doc()
        doc.pop("skill")
        r = c.validate_v1(doc)
        self.assertFalse(r["ok"])
        self.assertIn("skill", r["missing"])

    def test_02_enum_out_of_range(self):
        doc = general_doc()
        doc["mechanism"] = "quantum_field"
        r = c.validate_v1(doc)
        self.assertFalse(r["ok"])
        self.assertTrue(any("V2" in e for e in r["errors"]))

    def test_03_payload_whitelist(self):
        doc = general_doc()
        doc["payload"]["dose_plan"] = "x"
        doc["contract_id"] = c.fingerprint(doc)
        r = c.validate_v1(doc)
        self.assertFalse(r["ok"])
        self.assertEqual(r["payload_unknown"], ["dose_plan"])

    def test_04_medical_requires_redlines(self):
        doc = medical_doc()
        doc["payload"].pop("redlines")
        doc["contract_id"] = c.fingerprint(doc)
        r = c.validate_v1(doc)
        self.assertFalse(r["ok"])
        self.assertTrue(any("V4" in e for e in r["errors"]))
        # 红线为 false 同样拦截
        bad = medical_doc()
        bad["payload"]["redlines"]["zero_dose"] = False
        bad["contract_id"] = c.fingerprint(bad)
        self.assertFalse(c.validate_v1(bad)["ok"])
        # 通用域不要求红线
        self.assertTrue(c.validate_v1(general_doc())["ok"])

    def test_05_fingerprint_mismatch(self):
        doc = medical_doc()
        doc["contract_id"] = "000000000000"
        r = c.validate_v1(doc)
        self.assertFalse(r["ok"])
        self.assertFalse(r["id_ok"])
        self.assertEqual(r["fingerprint"], c.fingerprint(doc))

    def test_06_budget_range(self):
        for bad in (-1, 101, "3", True, 3.5):
            doc = general_doc(budget=bad)
            doc["contract_id"] = c.fingerprint(doc)
            r = c.validate_v1(doc)
            self.assertFalse(r["ok"], "budget=%r 应被拦截" % (bad,))
            self.assertTrue(any("V6" in e for e in r["errors"]))
        doc = general_doc(budget=3)
        self.assertTrue(c.validate_v1(doc)["ok"])

    def test_07_same_params_same_fingerprint(self):
        a = medical_doc()
        b = medical_doc()
        self.assertEqual(a["contract_id"], b["contract_id"])
        # nonce 不进指纹：同参不同 nonce 仍同指纹，可用于重放检测
        b["nonce"] = "n-20261102-01"
        self.assertEqual(c.fingerprint(a), c.fingerprint(b))
        # 规范化与键书写顺序无关
        body = {"source": "local", "target": "gitee", "skill": "fusion_contract",
                "mechanism": "semantic_bus", "lane": "read", "payload": {"domain": "general", "inputs": {"b": 1, "a": 2}}}
        body2 = {"payload": {"inputs": {"a": 2, "b": 1}, "domain": "general"},
                 "source": "local", "target": "gitee", "skill": "fusion_contract",
                 "mechanism": "semantic_bus", "lane": "read"}
        self.assertEqual(c.fingerprint(body), c.fingerprint(body2))

    def test_08_different_params_different_fingerprint(self):
        base = general_doc()
        cases = []
        for field, value in (("target", "ivsa"), ("skill", "fusion_fuse"),
                             ("mechanism", "cytoskeleton"), ("lane", "write")):
            doc = general_doc()
            doc[field] = value
            doc["contract_id"] = c.fingerprint(doc)
            cases.append((field, doc))
        doc = general_doc()
        doc["payload"] = {"domain": "general", "notes": "改一个键"}
        doc["contract_id"] = c.fingerprint(doc)
        cases.append(("payload", doc))
        for name, doc in cases:
            self.assertNotEqual(c.fingerprint(base), c.fingerprint(doc), name)
            self.assertTrue(c.validate_v1(doc)["ok"], name)

    def test_09_dose_words_blocked(self):
        doc = general_doc(note="每日 3 片")
        doc["note"] = "剂量 5mg"
        doc["contract_id"] = c.fingerprint(doc)
        r = c.validate_v1(doc)
        self.assertFalse(r["ok"])
        self.assertTrue(any("V7" in e for e in r["errors"]))
        # payload.notes 同样拦截
        doc2 = medical_doc(payload_extra={"notes": "每次 2ml"})
        self.assertFalse(c.validate_v1(doc2)["ok"])

    def test_10_unknown_top_level_key(self):
        doc = general_doc()
        doc["priority"] = 1
        doc["contract_id"] = c.fingerprint(doc)
        r = c.validate_v1(doc)
        self.assertFalse(r["ok"])
        self.assertTrue(any("V8" in e for e in r["errors"]))

    def test_11_legacy_api_unchanged(self):
        a = c.make("holoaeon", "ivsa", "matrix_dispatch", "skin_v6", "read")
        b = c.make("holoaeon", "ivsa", "matrix_dispatch", "skin_v6", "read")
        self.assertEqual(a["contract_id"], b["contract_id"])
        self.assertTrue(a["contract_id"].startswith("CT-"))
        self.assertTrue(c.validate(a)["ok"])
        self.assertEqual(c.receipt(a)["seal"], c.receipt(b)["seal"])


if __name__ == "__main__":
    unittest.main()
