# -*- coding: utf-8 -*-
"""V40 学术笔痕闸门测试。零依赖，确定性断言。"""
import unittest

from holoaeon import academic_gate as ag


class TestAcademicGate(unittest.TestCase):
    def test_chain_ring10(self):
        self.assertEqual(ag.CHAIN_POSITION["ring"], 10)
        self.assertIn("学术", ag.CHAIN_POSITION["name"])

    def test_seal(self):
        self.assertEqual(ag.SEAL, "潮起开门，潮落闭嘴")

    def test_notes_present(self):
        for key in ("ethics_note", "disposition_note", "lineage_note"):
            self.assertIn(key, ag.CHAIN_POSITION)

    def test_ethics_not_evasion(self):
        self.assertIn("规避", ag.CHAIN_POSITION["ethics_note"])

    def test_disposition_report_only(self):
        self.assertFalse(hasattr(ag, "rewrite"))
        self.assertFalse(hasattr(ag, "humanize"))

    def test_scan_hype(self):
        f = ag.scan("This work paves the way for a new paradigm.")
        self.assertTrue(any(x["id"] == "T01" for x in f))

    def test_scan_ai_vocab(self):
        f = ag.scan("We delve into intricate dependencies.")
        self.assertIn("ai_vocab", {x["cat"] for x in f})

    def test_scan_filler(self):
        f = ag.scan("It is worth noting that the gain holds.")
        self.assertTrue(any(x["id"] == "T03" for x in f))

    def test_scan_em_dash(self):
        f = ag.scan("The method — surprisingly — scales.")
        self.assertTrue(any(x["id"] == "T04" for x in f))

    def test_en_dash_range_not_flagged(self):
        self.assertFalse(any(x["id"] == "T04"
                             for x in ag.scan("improves 2--6 points")))

    def test_hedge_whitelist_clean(self):
        f = ag.scan("The results suggest the mechanism is consistent "
                    "with the data.")
        self.assertEqual(f, [])

    def test_connective_run(self):
        f = ag.scan("Moreover, it is fast. Furthermore, it scales.")
        self.assertTrue(any(x["id"] == "T12" for x in f))

    def test_unbacked_claim(self):
        c = ag.claim_evidence("We prove that the method is superior.")
        self.assertEqual(len(c), 1)

    def test_backed_claim_clean(self):
        c = ag.claim_evidence("We establish convergence at rate 0.01 "
                              "(Table 3).")
        self.assertEqual(c, [])

    def test_ledger(self):
        d = ag.ledger("Accuracy is 0.91 vs 0.86 [7] and [3, 9].")
        self.assertEqual(d["numbers"]["0.91"], 1)
        self.assertEqual(d["cites"]["[7]"], 1)

    def test_preservation_ok(self):
        a = "Accuracy is 0.91 [7] over 3 seeds."
        self.assertTrue(ag.check_preservation(a, a)["ok"])

    def test_preservation_number_changed(self):
        r = ag.check_preservation("Accuracy is 0.91 [7].",
                                  "Accuracy is 0.95 [7].")
        self.assertFalse(r["ok"])
        self.assertIn("0.91", r["missing"])
        self.assertIn("0.95", r["added"])

    def test_preservation_cite_dropped(self):
        r = ag.check_preservation("as shown [7, 9].", "as shown [7].")
        self.assertFalse(r["ok"])

    def test_audit_verdict(self):
        self.assertEqual(
            ag.audit("Clean text with 3 seeds [7].")["verdict"], "PASS")
        self.assertEqual(
            ag.audit("It is worth noting that 2 points are gained.")
            ["verdict"], "FINDINGS")


if __name__ == "__main__":
    unittest.main()
