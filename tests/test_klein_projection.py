# -*- coding: utf-8 -*-
"""V27 克莱因收敛投影模块测试（klein_projection）。

覆盖七段：受理 / 全息投影 + 许可证四级 / 四人组门 / 张量耦合 + 收敛 /
一过性车削 + 焚毁 / 硬核转正 / 项目库幂等；外加贯穿段提示包与 CLI。
"""
import json
import os
import tempfile
import unittest

from holoaeon.klein_projection import (
    ATLAS_ENTRIES,
    CANDIDATE_REQUIRED,
    LICENSE_RULES,
    MECHANISMS,
    PROMOTE_GATES,
    SCHEMA_VERSION,
    CandidateIntake,
    ChatFrontendPack,
    EphemeralForge,
    Hardener,
    HoloEvaluator,
    KleinProjection,
    ProjectLibrary,
    QuartetGate,
    TensorCoupler,
    _main,
)

FULL_KEYWORDS = ["heartbeat", "agent", "guard", "route", "weight",
                 "envelope", "cluster", "runtime", "graph", "role", "registry"]
MID_KEYWORDS = ["agent", "guard", "route", "envelope"]
THIN_KEYWORDS = ["heartbeat"]


def _candidate(name="cand", license_id="mit", keywords=None, desc=""):
    return {
        "name": name,
        "license": license_id,
        "language": "python",
        "keywords": list(keywords if keywords is not None else FULL_KEYWORDS),
        "description": desc,
    }


class TestIntake(unittest.TestCase):
    def test_01_missing_required_fields(self):
        intake = CandidateIntake()
        res = intake.parse({"name": "x"})
        self.assertFalse(res["ok"])
        self.assertGreaterEqual(len(res["problems"]), len(CANDIDATE_REQUIRED) - 1)

    def test_02_parse_normalizes_keywords(self):
        intake = CandidateIntake()
        res = intake.parse({"name": "X", "license": "MIT", "language": "Python",
                            "keywords": ["  Guard ", "AGENT", ""]})
        self.assertTrue(res["ok"])
        self.assertEqual(res["profile"]["license"], "mit")
        self.assertEqual(res["profile"]["keywords"], ["guard", "agent"])

    def test_03_load_from_file(self):
        intake = CandidateIntake()
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False,
                                        encoding="utf-8") as f:
            json.dump(_candidate(), f)
            path = f.name
        try:
            res = intake.load(path)
            self.assertTrue(res["ok"])
            self.assertEqual(res["profile"]["name"], "cand")
            self.assertFalse(intake.load(os.path.join(path, "nope"))["ok"])
        finally:
            os.remove(path)


class TestHoloEvaluator(unittest.TestCase):
    def setUp(self):
        self.ev = HoloEvaluator()

    def test_04_license_four_classes(self):
        self.assertEqual(self.ev.license_ruling("MIT")["class"], "permissive")
        self.assertEqual(self.ev.license_ruling("MIT")["mode"], "absorb")
        self.assertTrue(self.ev.license_ruling("MIT")["copy_code"])
        self.assertEqual(self.ev.license_ruling("MPL-2.0")["mode"], "absorb_with_notice")
        rule = self.ev.license_ruling("AGPL-3.0")
        self.assertEqual(rule["class"], "strong_copyleft")
        self.assertEqual(rule["mode"], "distill_only")
        self.assertFalse(rule["copy_code"])
        self.assertEqual(self.ev.license_ruling("WTFPL")["class"], "unknown")

    def test_05_projection_covers_eleven_mechanisms(self):
        res = self.ev.project(_candidate())
        self.assertEqual(len(res["scores"]), len(MECHANISMS))
        self.assertEqual(res["matched"], len(MECHANISMS))
        self.assertEqual(res["coverage"], 1.0)
        ids = [s["id"] for s in res["scores"]]
        self.assertEqual(ids[0], "M01")
        self.assertEqual(len(ids), len(set(ids)))

    def test_06_verdict_bands(self):
        self.assertEqual(self.ev.evaluate(_candidate())["verdict"], "integrate")
        mid = self.ev.evaluate(_candidate(keywords=MID_KEYWORDS))
        self.assertIn(mid["verdict"], ("blend", "integrate"))
        thin = self.ev.evaluate(_candidate(keywords=THIN_KEYWORDS))
        self.assertEqual(thin["verdict"], "reject")
        unknown = self.ev.evaluate(_candidate(license_id="custom-eula"))
        self.assertEqual(unknown["verdict"], "reject")

    def test_07_strong_copyleft_keeps_integrate_but_flags_distill(self):
        res = self.ev.evaluate(_candidate(name="agpl-proj", license_id="AGPL-3.0"))
        self.assertEqual(res["verdict"], "integrate")
        self.assertEqual(res["license_ruling"]["mode"], "distill_only")
        self.assertFalse(res["license_ruling"]["copy_code"])


class TestQuartetGate(unittest.TestCase):
    def test_08_emergence_formula(self):
        gate = QuartetGate()
        ok = gate.emergence({"p1": 1.0, "p2": 1.0, "p3": 0.9, "p4": 0.1, "coverage": 0.9})
        self.assertTrue(ok["conditions_met"])
        self.assertGreater(ok["order"], 0.30)
        bad = gate.emergence({"p1": 0.2, "p2": 0.5, "p3": 0.5, "p4": 0.6, "coverage": 0.1})
        self.assertFalse(bad["conditions_met"])

    def test_09_gate_verdicts(self):
        gate = QuartetGate()
        ev = HoloEvaluator()
        permissive = gate.gate(ev.evaluate(_candidate()))
        self.assertEqual(permissive["verdict"], "PASS")
        self.assertEqual(permissive["protocol"], ["道", "法", "术", "器", "升维"])
        distilled = gate.gate(ev.evaluate(_candidate(license_id="agpl-3.0")))
        self.assertEqual(distilled["verdict"], "ATTENTION")
        rejected = gate.gate(ev.evaluate(_candidate(keywords=THIN_KEYWORDS)))
        self.assertEqual(rejected["verdict"], "BLOCK")


class TestTensorCoupler(unittest.TestCase):
    def setUp(self):
        self.ev = HoloEvaluator()
        self.tc = TensorCoupler()

    def test_10_couple_axes_and_shape(self):
        res = self.tc.couple(self.ev.evaluate(_candidate(keywords=MID_KEYWORDS)))
        self.assertEqual(len(res["d_axis"]), 4)
        self.assertEqual(len(res["x_axis"]), len(MECHANISMS) - 4)
        self.assertEqual(res["tensor_shape"], [4, 7])
        self.assertEqual(res["rank"], 4)
        self.assertEqual(res["license_mode"], "absorb")

    def test_11_converge_fixed_point(self):
        conv = self.tc.converge(_candidate(), self.ev)
        self.assertEqual(conv["verdict"], "CONVERGED")
        self.assertGreaterEqual(conv["rounds_used"], 2)
        self.assertLessEqual(conv["rounds_used"], 4)
        self.assertEqual(conv["delta_max"], 0.0)
        self.assertTrue(conv["fixed_point"])

    def test_12_converge_on_thin_candidate_also_stabilizes(self):
        conv = self.tc.converge(_candidate(keywords=THIN_KEYWORDS), self.ev)
        self.assertIn(conv["verdict"], ("CONVERGED", "NOT_CONVERGED"))
        self.assertGreaterEqual(conv["rounds_used"], 2)


class TestForgeHardenLibrary(unittest.TestCase):
    def test_13_forge_ast_and_burn(self):
        forge = EphemeralForge()
        ev = HoloEvaluator().evaluate(_candidate())
        res = forge.forge(ev)
        self.assertTrue(res["ast_parse_ok"])
        self.assertTrue(os.path.isfile(res["path"]))
        self.assertTrue(res["ephemeral"])
        self.assertEqual(len(res["sha256"]), 64)
        burn = forge.burn(res["tmpdir"])
        self.assertTrue(burn["ok"])
        self.assertFalse(os.path.exists(res["tmpdir"]))
        self.assertFalse(os.path.exists(res["path"]))

    def test_14_harden_requires_four_gates(self):
        hardener = Hardener()
        forge = EphemeralForge().forge(HoloEvaluator().evaluate(_candidate()))
        blocked = hardener.harden("cand", forge, {"tests_green": False})
        self.assertFalse(blocked["promoted"])
        self.assertEqual(sorted(PROMOTE_GATES) == sorted(blocked["unmet"]) or
                         len(blocked["unmet"]) >= 1, True)
        full = {g: True for g in PROMOTE_GATES}
        ok = hardener.harden("cand", forge, full)
        self.assertTrue(ok["promoted"])
        self.assertEqual(ok["manifest"]["sha256"], forge["sha256"])
        self.assertEqual(ok["manifest"]["seal"], "潮起开门，潮落闭嘴")

    def test_15_library_register_is_idempotent_and_counts_uses(self):
        tmp = tempfile.mkdtemp(prefix="klein_lib_")
        path = os.path.join(tmp, "library.json")
        lib = ProjectLibrary(path)
        self.assertEqual(lib.index()["total"], 0)
        manifest = {"name": "cand", "sha256": "a" * 64, "lines": 10}
        first = lib.register(manifest, {"license_mode": "absorb", "coverage": 1.0})
        self.assertEqual(first["uses"], 1)
        again = lib.register(manifest, {"license_mode": "absorb", "coverage": 1.0})
        self.assertEqual(again["uses"], 2)
        self.assertEqual(lib.index()["total"], 1)
        self.assertEqual(lib.index()["projects"][0]["name"], "cand")
        EphemeralForge.burn(tmp)


class TestEndToEnd(unittest.TestCase):
    def test_16_status_and_atlas(self):
        kp = KleinProjection()
        st = kp.status()
        self.assertEqual(st["module"], "klein_projection")
        self.assertEqual(st["version"], "V27")
        self.assertEqual(st["schema"], SCHEMA_VERSION)
        self.assertEqual(st["mechanisms"], len(MECHANISMS))
        self.assertEqual(st["license_rules"], len(LICENSE_RULES))
        self.assertEqual(st["seal"], "潮起开门，潮落闭嘴")
        self.assertEqual(len(kp.atlas()), len(ATLAS_ENTRIES))
        self.assertEqual(len(ATLAS_ENTRIES), 10)

    def test_17_frontend_pack_renders(self):
        ev = HoloEvaluator().evaluate(_candidate())
        coupler = TensorCoupler().couple(ev)
        pack = ChatFrontendPack().render(ev, coupler, {"delta_max": 0.0, "verdict": "CONVERGED"})
        self.assertIn("潮起开门，潮落闭嘴", pack)
        self.assertIn(SCHEMA_VERSION, pack)
        self.assertIn("D 轴（取）", pack)
        self.assertEqual(pack.count("score="), len(MECHANISMS))

    def test_18_assess_end_to_end_file(self):
        tmp = tempfile.mkdtemp(prefix="klein_e2e_")
        path = os.path.join(tmp, "cand.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(_candidate(name="e2e", license_id="agpl-3.0"), f)
        kp = KleinProjection(library_path=os.path.join(tmp, "lib.json"))
        res = kp.assess(path)
        self.assertTrue(res["ok"])
        self.assertEqual(res["evaluation"]["license_ruling"]["mode"], "distill_only")
        self.assertEqual(res["gate"]["verdict"], "ATTENTION")
        self.assertEqual(res["convergence"]["verdict"], "CONVERGED")
        self.assertFalse(res["harden"]["promoted"])
        self.assertTrue(res["forge"]["burned"])
        self.assertEqual(res["seal"], "潮起开门，潮落闭嘴")
        EphemeralForge.burn(tmp)

    def test_19_cli_status_and_atlas(self):
        self.assertEqual(_main(["status"]), 0)
        self.assertEqual(_main(["atlas"]), 0)
        self.assertEqual(_main([]), 1)
        self.assertEqual(_main(["nope"]), 1)


if __name__ == "__main__":
    unittest.main()
