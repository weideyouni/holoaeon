# -*- coding: utf-8 -*-
"""SSYD 慢病管理智能引擎单测（确定性、零网络、零剂量断言）。"""
import json
import os
import unittest

from holoaeon import ssyd_chronic_engine as se


class TestIdentity(unittest.TestCase):
    def test_ring12(self):
        self.assertEqual(se.CHAIN_POSITION["ring"], 12)

    def test_name(self):
        self.assertIn("慢病", se.CHAIN_POSITION["name"])

    def test_upstream_phc(self):
        self.assertIn("phc_chronic_engine", se.CHAIN_POSITION["upstream"])

    def test_seal(self):
        self.assertEqual(se.SEAL, "潮起开门，潮落闭嘴")

    def test_engine_id(self):
        self.assertEqual(se.ENGINE_ID, "SG-SSYD-CHRONIC-ENGINE-ARCH-V1.0")

    def test_evidence_class(self):
        self.assertEqual(se.EVIDENCE_CLASS, "simulated")


class TestRegistry(unittest.TestCase):
    def test_eight_diseases(self):
        self.assertEqual(set(se.DISEASE_REGISTRY), {
            "htn", "t2dm", "copd", "chd", "ckd", "stroke", "ra", "oa"})

    def test_followup_minimum(self):
        for d, reg in se.DISEASE_REGISTRY.items():
            self.assertGreaterEqual(reg["followup_per_year"], 2, d)
            self.assertTrue(reg["annual_exam"], d)

    def test_systems(self):
        allowed = {"cardio_cerebro", "endocrine", "immune", "ortho"}
        for reg in se.DISEASE_REGISTRY.values():
            self.assertIn(reg["system"], allowed)

    def test_tcm_domain_nonempty(self):
        for reg in se.DISEASE_REGISTRY.values():
            self.assertTrue(reg["tcm_domain"])

    def test_five_patterns(self):
        self.assertEqual(len(se.PATTERN_AXIS), 5)
        self.assertEqual({p["cn"] for p in se.PATTERN_AXIS.values()},
                         {"虚", "郁", "瘀", "寒", "湿"})

    def test_links_reference_known_patterns(self):
        for d, links in se.DISEASE_PATTERN_LINKS.items():
            self.assertIn(d, se.DISEASE_REGISTRY)
            for key, conf in links:
                self.assertIn(key, se.PATTERN_AXIS)
                self.assertGreater(conf, 0)
                self.assertLessEqual(conf, 1)

    def test_multi_to_many(self):
        for links in se.DISEASE_PATTERN_LINKS.values():
            self.assertGreaterEqual(len(links), 3)

    def test_four_evidence_tags(self):
        self.assertEqual(set(se.EVIDENCE_TAGS), {"classic", "theory", "simulation", "modern"})


class TestRisk(unittest.TestCase):
    def test_fourteen_rules(self):
        ids = [r["id"] for r in se.RISK_RULES]
        self.assertEqual(ids, ["SR%02d" % i for i in range(1, 15)])

    def test_grade_boundaries(self):
        self.assertEqual(se.grade_of(70), "IV")
        self.assertEqual(se.grade_of(69), "III")
        self.assertEqual(se.grade_of(50), "III")
        self.assertEqual(se.grade_of(49), "II")
        self.assertEqual(se.grade_of(30), "II")
        self.assertEqual(se.grade_of(29), "I")

    def test_sr01(self):
        r = se.assess_risk({"sbp": 182, "dbp": 112})
        self.assertEqual([h["id"] for h in r["hits"]], ["SR01"])
        self.assertEqual(r["score"], 30)

    def test_sr02(self):
        r = se.assess_risk({"sbp": 165, "dbp": 102})
        self.assertEqual([h["id"] for h in r["hits"]], ["SR02"])

    def test_sr03(self):
        r = se.assess_risk({"sbp": 145, "dbp": 92})
        self.assertEqual([h["id"] for h in r["hits"]], ["SR03"])

    def test_sr04_sr05(self):
        r = se.assess_risk({"fpg": 12.0, "hba1c": 9.5})
        self.assertEqual([h["id"] for h in r["hits"]], ["SR04", "SR05"])
        self.assertEqual(r["score"], 45)

    def test_sr06_sr07_exclusive(self):
        self.assertEqual([h["id"] for h in se.assess_risk({"egfr": 25})["hits"]], ["SR06"])
        self.assertEqual([h["id"] for h in se.assess_risk({"egfr": 55})["hits"]], ["SR07"])

    def test_lifestyle_and_age(self):
        r = se.assess_risk({"smoking": True, "bmi": 30, "comorbidities": 2, "age": 70})
        self.assertEqual([h["id"] for h in r["hits"]], ["SR10", "SR11", "SR12", "SR13"])
        self.assertEqual(r["score"], 31)

    def test_acute_direct_iv(self):
        r = se.assess_risk({"chest_pain": True, "sbp": 130, "dbp": 80})
        self.assertEqual(r["grade"], "IV")
        self.assertTrue(r["acute_direct_iv"])
        self.assertIn("SR08", [h["id"] for h in r["hits"]])

    def test_cap_100(self):
        r = se.assess_risk({"sbp": 190, "dbp": 120, "fpg": 14, "hba1c": 10,
                            "egfr": 20, "chest_pain": True, "target_organ_damage": True,
                            "smoking": True, "bmi": 32, "comorbidities": 3,
                            "age": 80, "pregnant": True})
        self.assertEqual(r["score"], 100)


class TestEmergency(unittest.TestCase):
    def test_flags_count(self):
        self.assertEqual(len(se.EMERGENCY_FLAGS), 7)

    def test_triage_hit(self):
        t = se.emergency_triage({"fast_positive": True})
        self.assertTrue(t["e14"])
        self.assertEqual(t["action"], "立即线下急诊或拨打 120")
        self.assertIn("不展开线上自救", t["do_not"])

    def test_triage_clear(self):
        t = se.emergency_triage({})
        self.assertFalse(t["e14"])
        self.assertEqual(t["action"], "")


class TestSyndrome(unittest.TestCase):
    def test_candidates(self):
        s = se.syndrome_candidates(["htn", "t2dm"])
        self.assertTrue(s["no_one_to_one_equivalence"])
        self.assertEqual(s["mapping"], "many_to_many")
        self.assertEqual(s["evidence_tag"], se.EVIDENCE_TAGS["theory"])

    def test_unknown_disease(self):
        with self.assertRaises(ValueError):
            se.syndrome_candidates(["unknown"])

    def test_confidence_order(self):
        s = se.syndrome_candidates(["copd"])
        confs = [p["confidence"] for p in s["patterns"]]
        self.assertEqual(confs, sorted(confs, reverse=True))


class TestMedication(unittest.TestCase):
    def test_raas_duplicate(self):
        m = se.medication_safety({}, ["acei", "arb"])
        self.assertEqual([f["code"] for f in m["flags"]], ["M01"])

    def test_nsaid_ckd(self):
        m = se.medication_safety({"egfr": 45}, ["ibuprofen"])
        self.assertIn("M02", [f["code"] for f in m["flags"]])

    def test_nsaid_anticoag(self):
        m = se.medication_safety({"ckd": True}, ["naproxen", "warfarin"])
        codes = [f["code"] for f in m["flags"]]
        self.assertIn("M02", codes)
        self.assertIn("M03", codes)

    def test_metformin_severe_renal(self):
        m = se.medication_safety({"egfr": 22}, ["metformin"])
        self.assertEqual([f["code"] for f in m["flags"]], ["M04"])

    def test_pregnancy_e13(self):
        m = se.medication_safety({"pregnant": True}, [])
        self.assertEqual([f["code"] for f in m["flags"]], ["M05"])
        self.assertTrue(m["zero_dose"])
        self.assertTrue(m["zero_prescription"])

    def test_no_self_discontinuation(self):
        m = se.medication_safety({"egfr": 40}, ["ibuprofen"])
        self.assertIn("不自行停药", m["flags"][0]["action"])


class TestFollowup(unittest.TestCase):
    def test_base_plan(self):
        f = se.followup_plan({}, ["htn", "oa"])
        self.assertEqual([i["followup_per_year"] for i in f["items"]], [4, 2])
        self.assertTrue(f["annual_exam_required"])

    def test_uncontrolled_two_weeks(self):
        f = se.followup_plan({}, ["htn"], control_ok=False)
        self.assertEqual(f["actions"][0]["when"], "now+14d")

    def test_acute_reflux(self):
        f = se.followup_plan({}, ["htn"], acute_referral=True)
        self.assertIn("mobius/LIN-E01", f["actions"][0]["reflux_note"])

    def test_unknown_disease(self):
        with self.assertRaises(ValueError):
            se.followup_plan({}, ["x"])


class TestMdt(unittest.TestCase):
    def test_slots_blank(self):
        m = se.convene_mdt(["htn", "ckd"], ["xu", "shi"])
        self.assertTrue(all(s["opinion"] == "" and not s["signed"]
                            for s in m["opinion_slots"]))
        self.assertEqual(m["final_authority"], se.FINAL_AUTHORITY)

    def test_departments_dedup(self):
        m = se.convene_mdt(["htn", "chd"])
        self.assertEqual(m["departments"].count("心血管内科"), 1)


class TestEnvelope(unittest.TestCase):
    def test_image_requires_structured(self):
        r = se.Envelope.create("tongue_photo", b"img", structured=None)
        self.assertFalse(r["ok"])
        self.assertEqual(r["reason"], "image_requires_structured")

    def test_image_pointer_only(self):
        r = se.Envelope.create("tongue_photo", b"img-bytes",
                               structured={"color": "淡红"})
        self.assertTrue(r["ok"])
        self.assertFalse(r["pixel_retained"])
        self.assertFalse(r["raw_bytes_retained"])
        self.assertEqual(len(r["sha256"]), 64)
        self.assertNotIn("img-bytes", json.dumps(r, ensure_ascii=False))

    def test_unknown_modality(self):
        self.assertFalse(se.Envelope.create("x", b"y", {})["ok"])

    def test_all_images_pixel_flag(self):
        for m in ("tongue_photo", "ear_photo", "eye_photo"):
            self.assertTrue(se.MODALITIES[m]["pixel"])


class TestAuditChain(unittest.TestCase):
    def test_chain_valid(self):
        a = se.AuditChain()
        a.append("a", {"x": 1})
        a.append("b", {"y": 2})
        self.assertTrue(a.verify())
        self.assertEqual(len(a.tail()), 64)

    def test_tamper_detected(self):
        a = se.AuditChain()
        a.append("a", {"x": 1})
        a.append("b", {"y": 2})
        a.items[0]["data"]["x"] = 9
        self.assertFalse(a.verify())


class TestCapacity(unittest.TestCase):
    def test_defaults_adults(self):
        c = se.capacity_plan()
        self.assertEqual(c["adults35"], 16500)

    def test_total_recomputable(self):
        c = se.capacity_plan()
        self.assertEqual(c["total_annual_visits"], sum(r["annual_visits"] for r in c["rows"]))
        self.assertEqual(c["total_patients"], sum(r["patients"] for r in c["rows"]))

    def test_custom_population(self):
        c = se.capacity_plan(population=10000, adult35_ratio=0.5)
        self.assertEqual(c["adults35"], 5000)


class TestEngine(unittest.TestCase):
    def _run(self, **kw):
        profile = {"patient_id": "p-001", "sbp": 150, "dbp": 95, "fpg": 7.2,
                   "egfr": 70, "age": 60, "bmi": 25, "comorbidities": 1}
        profile.update(kw.pop("profile", {}))
        return se.Engine().run(profile, kw.pop("diseases", ["htn", "t2dm"]), **kw)

    def test_report_flags(self):
        r = self._run()
        self.assertTrue(r["zero_dose"])
        self.assertTrue(r["zero_diagnosis"])
        self.assertTrue(r["zero_pixels"])
        self.assertTrue(r["zero_network"])
        self.assertEqual(r["final_authority"], se.FINAL_AUTHORITY)

    def test_physician_review(self):
        self.assertEqual(self._run()["decision"], "PHYSICIAN_REVIEW_REQUIRED")

    def test_emergency_decision(self):
        r = self._run(profile={"chest_pain": True}, diseases=["chd"],
                      meds=["aspirin"], control_ok=True)
        self.assertEqual(r["decision"], "E14_EMERGENCY_DIRECT")
        self.assertEqual(r["risk"]["grade"], "IV")

    def test_deterministic_json(self):
        a = json.dumps(self._run(), ensure_ascii=False, sort_keys=True)
        b = json.dumps(self._run(), ensure_ascii=False, sort_keys=True)
        self.assertEqual(a, b)

    def test_patient_ref_hashed(self):
        r = self._run()
        self.assertEqual(len(r["patient_ref"]), 16)
        self.assertNotIn("p-001", json.dumps(r, ensure_ascii=False))

    def test_empty_diseases(self):
        with self.assertRaises(ValueError):
            se.Engine().run({}, [])

    def test_envelope_requires_structured(self):
        r = self._run(entries=[{"modality": "tongue_photo", "payload": b"img"}])
        self.assertEqual(r["envelope"][0]["reason"], "image_requires_structured")

    def test_audit_valid(self):
        r = self._run()
        self.assertTrue(r["audit_ok"])
        self.assertEqual(len(r["audit_tail"]), 64)


class TestModuleHygiene(unittest.TestCase):
    def test_source_no_network_tokens(self):
        path = os.path.abspath(se.__file__)
        with open(path, encoding="utf-8") as f:
            src = f.read()
        for token in ("import requests", "import socket", "urllib.request", "http.client"):
            self.assertNotIn(token, src)

    def test_audit_snapshot(self):
        a = se.audit()
        self.assertEqual(a["disease_count"], 8)
        self.assertEqual(a["pattern_count"], 5)
        self.assertEqual(a["risk_rule_count"], 14)
        self.assertEqual(a["emergency_flags"], sorted(se.EMERGENCY_FLAGS))
        self.assertTrue(a["zero_dose"])


if __name__ == "__main__":
    unittest.main()
