# -*- coding: utf-8 -*-
"""V41 实战1号 公共卫生慢病管理智能引擎测试。零依赖，确定性断言。"""
import unittest

from holoaeon import phc_chronic_engine as pe


class TestPhcChronicEngine(unittest.TestCase):
    def test_chain_ring11(self):
        self.assertEqual(pe.CHAIN_POSITION["ring"], 11)
        self.assertIn("公共卫生", pe.CHAIN_POSITION["name"])

    def test_seal(self):
        self.assertEqual(pe.SEAL, "潮起开门，潮落闭嘴")

    def test_a_class_three_diseases(self):
        a = pe.DISEASE_REGISTRY["A"]
        self.assertEqual(set(a), {"hypertension", "t2dm", "copd"})
        for d in a.values():
            self.assertGreaterEqual(d["followup_per_year"], 4)
            self.assertTrue(d["free"])

    def test_six_systems(self):
        self.assertEqual(len(pe.SIX_SYSTEM_ATLAS), 6)
        for key in ("nervous", "cardio_cerebro", "endocrine", "immune",
                    "malignancy", "ortho"):
            self.assertIn(key, pe.SIX_SYSTEM_ATLAS)

    def test_seven_modalities(self):
        self.assertEqual(len(pe.MODALITIES), 7)
        for m in ("tongue_photo", "ear_photo", "eye_photo"):
            self.assertEqual(pe.MODALITIES[m]["kind"], "image")

    def test_envelope_image_needs_structured(self):
        r = pe.FeedEnvelope.create("tongue_photo", b"img",
                                   structured=None, patient_id="p1")
        self.assertFalse(r["ok"])

    def test_envelope_image_with_structured(self):
        r = pe.FeedEnvelope.create("tongue_photo", b"img-bytes",
                                   structured={"自述": "淡红舌薄白苔"},
                                   patient_id="p1")
        self.assertTrue(r["ok"])
        self.assertEqual(len(r["sha256"]), 64)
        self.assertNotIn("img-bytes", str(r))  # 零像素：字节不落引擎态

    def test_envelope_unknown_modality(self):
        self.assertFalse(pe.FeedEnvelope.create("mri", b"x")["ok"])

    def test_sync_manifest(self):
        e = pe.FeedEnvelope.create("lab_report", b"glu 7.8",
                                   patient_id="p2")
        m = pe.FeedEnvelope.sync_manifest([e])
        self.assertEqual(m["archive"], pe.ARCHIVE_DIRS["sync"])
        self.assertEqual(m["items"][0]["sha256"], e["sha256"])

    def test_risk_high_grade_iv(self):
        r = pe.risk_score({"sbp": 185, "acute_event": True})
        self.assertGreaterEqual(r["score"], 60)
        self.assertIn("IV级", r["grade"])  # 急性事件直通红档
        self.assertIn("R01", r["rule_refs"])
        self.assertIn("R08", r["rule_refs"])

    def test_risk_grade_iv_by_score_alone(self):
        r = pe.risk_score({"sbp": 185, "target_damage": True,
                           "comorbid_n": 2, "smoker": True})
        self.assertGreaterEqual(r["score"], 70)
        self.assertIn("IV级", r["grade"])

    def test_risk_subclinical_only(self):
        r = pe.risk_score({"fpg": 6.5, "smoker": True, "bmi": 29})
        self.assertEqual(r["score"], 6 + 8 + 8)
        self.assertIn("I级", r["grade"])

    def test_risk_clean(self):
        r = pe.risk_score({"sbp": 118, "fpg": 5.2, "age": 40})
        self.assertEqual(r["score"], 0)
        self.assertIn("I级", r["grade"])
        self.assertEqual(r["rule_refs"], [])

    def test_risk_disclaimer(self):
        r = pe.risk_score({})
        self.assertIn("执业医师", r["disclaimer"])

    def test_mdt_routes_by_modality_and_disease(self):
        e1 = pe.FeedEnvelope.create("eye_photo", b"i", structured={"s": 1})
        e2 = pe.FeedEnvelope.create("pulse", b"w", structured={"s": 1})
        r = pe.MdtConvene.convene([e1, e2], ["hypertension", "脑卒中后遗症"])
        self.assertIn("眼科", r["depts"])
        self.assertIn("中医科", r["depts"])
        self.assertIn("心血管内科", r["depts"])
        self.assertIn("神经内科", r["depts"])
        self.assertIn("rehab_fusion", r["skills"])
        self.assertIn("执业医师终审", r["decision"])

    def test_mdt_empty_opinion_slots(self):
        e = pe.FeedEnvelope.create("lab_report", b"x")
        r = pe.MdtConvene.convene([e], ["t2dm"])
        self.assertEqual(r["opinion_slots"]["内分泌科"], "")

    def test_followup_normal(self):
        r = pe.FollowupScheduler.plan("hypertension", done_this_year=1)
        self.assertEqual(r["remaining"], 3)
        self.assertIn("常规随访", r["action"])

    def test_followup_unsatisfied_two_weeks(self):
        r = pe.FollowupScheduler.plan("t2dm", control="unsatisfied")
        self.assertIn("2周内再次随访", r["action"])

    def test_followup_acute_reflux(self):
        r = pe.FollowupScheduler.plan("copd", acute=True)
        self.assertIn("转诊", r["action"])
        self.assertIn("2周内追踪", r["action"])
        self.assertIn("mobius", r["reflux_note"])

    def test_followup_non_a_class_rejected(self):
        self.assertFalse(pe.FollowupScheduler.plan("gout")["ok"])

    def test_port_pool_limit10(self):
        pool = pe.PortPool()
        for i in range(10):
            self.assertTrue(pool.acquire("t%d" % i)["ok"])
        self.assertFalse(pool.acquire("t11")["ok"])
        self.assertTrue(pool.release("t0")["ok"])
        self.assertTrue(pool.acquire("t11")["ok"])

    def test_port_pool_no_double_hold(self):
        pool = pe.PortPool()
        pool.acquire("a")
        self.assertFalse(pool.acquire("a")["ok"])

    def test_mlps3_checklist_and_chain(self):
        self.assertIn("安全审计", pe.MLPS3.CHECKLIST)
        d1 = pe.MLPS3.chain_entry("login:admin")
        d2 = pe.MLPS3.chain_entry("read:archive", d1)
        ok = pe.MLPS3.audit([("login:admin", d1), ("read:archive", d2)])
        self.assertTrue(ok["ok"])
        tampered = pe.MLPS3.audit([("login:admin", d1),
                                   ("read:TAMPERED", d2)])
        self.assertFalse(tampered["ok"])

    def test_capacity_3w(self):
        r = pe.CapacityPlanner.estimate()
        self.assertEqual(r["adults_35plus"], 16500)
        self.assertEqual(r["port_pool"], 10)
        self.assertEqual(r["followup_visits_per_year"],
                         (4125 + 1650 + 495) * 4)

    def test_audit_snapshot(self):
        s = pe.audit()
        self.assertTrue(s["zero_network"])
        self.assertTrue(s["zero_diagnosis"])
        self.assertEqual(s["port_limit"], 10)


if __name__ == "__main__":
    unittest.main()

