# -*- coding: utf-8 -*-
"""V28 全息熔炉测试。零依赖，确定性断言。"""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holoaeon.holo_forge import (AXIOMS, BaseSelector, CHAIN,
                                 CalibrationSnapshot, ChatFrontendPack,
                                 ChainExecutor, FusionForge, HoloForge,
                                 HOLO_MECHANISMS, LegoComposer,
                                 ProjectLibrary, SEAL)


HIST = [{"batch": "V26-MOBIUS-VORTEX", "head": "8f0afb3"},
        {"batch": "V27-KLEIN-PROJECTION", "head": "552951d"}]


def mod(seal=SEAL, schema="x/1", mechs=None, ifaces=None):
    return {"seal": seal, "schema": schema,
            "mechanisms": mechs or ["心跳机制"],
            "interfaces": ifaces or ["link"]}


class TestHoloForge(unittest.TestCase):
    def test_axioms_dual(self):
        self.assertEqual(len(AXIOMS), 2)
        self.assertIn("全息", AXIOMS["holography"])
        self.assertIn("万物互联", AXIOMS["universal_linkage"])

    def test_mechanisms_11(self):
        self.assertEqual(len(HOLO_MECHANISMS), 11)

    def test_chain_definition(self):
        self.assertEqual([c[1] for c in CHAIN], ["回流", "投影", "熔炼"])

    def test_calibrate_self_consistent(self):
        snap = CalibrationSnapshot(HIST).build()
        self.assertTrue(snap["self_consistent"])
        self.assertEqual(snap["robustness"], "healthy")
        self.assertEqual(len(snap["anchors"]), 5)

    def test_calibrate_freeze(self):
        with tempfile.TemporaryDirectory() as d:
            snap = CalibrationSnapshot(HIST).build()
            r = CalibrationSnapshot.freeze(snap, os.path.join(d, "s.json"))
            self.assertTrue(r["frozen"])
            with open(r["path"], "r", encoding="utf-8") as f:
                self.assertEqual(json.load(f)["seal"], SEAL)

    def test_chain_detect_real_package(self):
        pkg = os.path.dirname(os.path.abspath(
            sys.modules["holoaeon.holo_forge"].__file__))
        links = ChainExecutor(pkg).detect()
        by = {l["module"]: l for l in links}
        self.assertTrue(by["holo_forge"]["present"])

    def test_chain_run_envelope(self):
        pkg = os.path.dirname(os.path.abspath(
            sys.modules["holoaeon.holo_forge"].__file__))
        r = ChainExecutor(pkg).run({"batch": "V28"})
        self.assertTrue(r["complete"])
        self.assertEqual(r["envelope"]["payload"]["batch"], "V28")

    def test_base_selector_selective(self):
        cat = {"holoaeon": {"repo": "github.com/weideyouni/holoaeon",
                            "license": "Apache-2.0",
                            "caps": ["swarm", "graph", "guard"]}}
        r = BaseSelector(cat).select(["swarm", "guard"], mode="selective")
        self.assertEqual(r["manifest"]["module_list"], ["swarm", "guard"])
        self.assertEqual(r["best"]["base"], "holoaeon")

    def test_lego_contract_mismatch(self):
        r = LegoComposer.compose(mod(schema="a/1"), mod(schema="b/1"))
        self.assertFalse(r["ok"])

    def test_lego_emergent(self):
        a = mod(mechs=["心跳机制", "皮肤机制"], ifaces=["link", "seal"])
        b = mod(mechs=["经络机制"], ifaces=["link"])
        r = LegoComposer.compose(a, b)
        self.assertTrue(r["one_plus_one_gt_two"])
        self.assertEqual(len(r["union_mechanisms"]), 3)

    def test_fusion_four_states(self):
        r = FusionForge.melt([
            {"name": "a", "state": "product", "reference": "moy"},
            {"name": "b", "state": "plan", "reference": ""}])
        self.assertFalse(r["fusion_complete"])
        self.assertEqual(r["artifacts"][0]["path"],
                         ["plan", "execute", "reference", "product"])

    def test_library_install(self):
        with tempfile.TemporaryDirectory() as d:
            lib = ProjectLibrary(d)
            lib.install({"name": "x"})
            lib.install({"name": "y"})
            self.assertEqual(len(lib.items()), 2)

    def test_frontend_pack(self):
        pack = ChatFrontendPack.render("demo", {"base": "holoaeon",
                                                "mode": "selective",
                                                "module_list": ["graph"]})
        self.assertIn("前端", pack)
        self.assertIn(SEAL, pack)
        self.assertIn("万物互联", pack)


if __name__ == "__main__":
    unittest.main()
