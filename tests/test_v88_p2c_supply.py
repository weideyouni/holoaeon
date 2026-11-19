# -*- coding: utf-8 -*-
"""V88 P2-C：SUPPLY-CHAIN-2026-11 pin 与 L1-L5 自评表金丝雀。

判据：第 7 条 pin fast/90；三边界字段在位；source_sha16 与自评表字节一致；
自评表标 self_assessed=true（非获证）、结论 L3-L4、含「不引入该风险」边界表述。
"""
import hashlib
import io
import os
import unittest

from holoaeon import claims_gate as G


def _sha16(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


class TestV88SupplyChain(unittest.TestCase):
    def setUp(self):
        self.reg = G.load_registry()
        self.pin = next(
            (p for p in self.reg["regulation_pins"]
             if isinstance(p, dict) and p.get("id") == "SUPPLY-CHAIN-2026-11"),
            None)
        self.report = os.path.join(G.repo_root(),
                                   "reports", "security_tier_self_assessment_20261119.md")

    def test_pin_registered(self):
        self.assertIsNotNone(self.pin, "SUPPLY-CHAIN-2026-11 未登记")

    def test_tier_fast_90(self):
        self.assertEqual(self.pin["risk_tier"], "fast")
        self.assertEqual(self.pin["max_age_days"], 90)

    def test_three_boundaries(self):
        bounds = self.pin.get("boundaries") or []
        self.assertEqual(len(bounds), 3)
        joined = " ".join(bounds)
        self.assertIn("holoaeon/", joined)
        self.assertIn("宿主", joined)
        self.assertIn("不引入该风险", joined)

    def test_source_sha_matches_report(self):
        self.assertTrue(os.path.exists(self.report))
        self.assertEqual(self.pin["source_sha16"], _sha16(self.report))

    def test_report_self_assessed_l3l4(self):
        text = io.open(self.report, encoding="utf-8").read()
        self.assertIn("self_assessed=true", text)
        self.assertIn("L3–L4", text)
        self.assertIn("不引入该风险", text)
        self.assertIn("非第三方认证", text)
        self.assertNotIn("获证通过", text)
        self.assertNotIn("已获证", text)

    def test_gate_green_real(self):
        res = G.verify(self.reg, G._ctx())
        self.assertEqual(res["mismatch"], 0)


if __name__ == "__main__":
    unittest.main()
