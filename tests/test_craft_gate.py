# -*- coding: utf-8 -*-
"""V43 工艺域闸门测试。零依赖，确定性断言。"""
import unittest

from holoaeon import craft_gate as cg


class TestCraftGate(unittest.TestCase):
    def test_chain_ring12(self):
        self.assertEqual(cg.CHAIN_POSITION["ring"], 12)
        self.assertIn("工艺域", cg.CHAIN_POSITION["name"])

    def test_seal(self):
        self.assertEqual(cg.SEAL, "潮起开门，潮落闭嘴")

    def test_six_organs_registered(self):
        for organ in ("全息心跳", "细胞骨架", "语义通信底座",
                      "皮肤机制", "赫布协作场", "经络机制"):
            self.assertIn(organ, cg.ORGAN_MAP)
            self.assertIn("holoaeon.", cg.ORGAN_MAP[organ]["landfall"])

    def test_meridian_four_steps(self):
        for s in cg.STEPS:
            self.assertIn(s, cg.MERIDIAN_MAP)
            self.assertTrue(cg.MERIDIAN_MAP[s])

    def test_step_rail_no_skip(self):
        rail = cg.StepRail()
        r1 = rail.advance()
        self.assertEqual(r1["step"], "study")
        rail.complete()
        r2 = rail.advance()
        self.assertEqual(r2["step"], "build")  # 顺序推进，不可跳到 check

    def test_step_rail_end(self):
        rail = cg.StepRail()
        for _ in cg.STEPS:
            rail.advance()
            rail.complete()
        self.assertFalse(rail.advance()["ok"])

    def test_heartbeat_shape_aligns_bus(self):
        hb = cg.Heartbeat()
        b = hb.beat("study")
        self.assertEqual(b["beat"], 1)
        self.assertEqual(b["step"], "study")
        self.assertIn("uptime_s", b)  # 键名风格与 bus.Bus.heartbeat 对齐

    def test_evidence_ledger_chain(self):
        led = cg.EvidenceLedger()
        led.add("claim1", "ev1")
        led.add("claim2", "ev2")
        self.assertTrue(led.verify()["ok"])

    def test_evidence_ledger_tamper(self):
        led = cg.EvidenceLedger()
        led.add("claim1", "ev1")
        led.add("claim2", "ev2")
        led.entries[0]["claim"] = "TAMPERED"
        self.assertFalse(led.verify()["ok"])

    def test_envelope_requires_refs(self):
        r = cg.SemanticEnvelope.create("study", "build", "载荷", [])
        self.assertFalse(r["ok"])
        r2 = cg.SemanticEnvelope.create("study", "build", "载荷", ["ledger#1"])
        self.assertTrue(r2["ok"])

    def test_envelope_unknown_step(self):
        self.assertFalse(cg.SemanticEnvelope.create(
            "study", "sleep", "x", ["r"])["ok"])

    def test_clean_room_blocks_deep(self):
        gate = cg.CleanRoomGate(mode="clean_room")
        for a in cg.DEEP_ACTIONS:
            self.assertEqual(gate.admit(a)["verdict"], "BLOCK")
        self.assertEqual(gate.admit("inspect_visible")["verdict"], "ALLOW")

    def test_deep_needs_authorization(self):
        gate = cg.CleanRoomGate(mode="deep")
        self.assertEqual(gate.admit("read_source")["verdict"], "BLOCK")
        self.assertEqual(gate.admit("read_source", authorized=True)
                         ["verdict"], "ALLOW")

    def test_similarity_score_full_and_partial(self):
        full = cg.similarity_score(["a", "b", "c"], ["a", "b", "c"])
        self.assertEqual(full["score"], 1.0)
        self.assertEqual(full["diffs"], [])
        part = cg.similarity_score(["a", "b", "c"], ["a"])
        self.assertAlmostEqual(part["score"], 0.3333)
        self.assertEqual(part["diffs"], ["b", "c"])

    def test_similarity_no_checks(self):
        self.assertFalse(cg.similarity_score([], [])["ok"])

    def test_hebbian_reuses_adaptive_graph(self):
        h = cg.HebbianReinforce()
        r = h.reinforce(["study", "build", "check", "ready"])
        self.assertIsInstance(r, dict)

    def test_pipeline_clean_room_end_to_end(self):
        p = cg.CraftPipeline(mode="clean_room", max_rounds=3, threshold=0.9)
        r = p.run("贪吃蛇网页游戏", ["玩法", "计分", "速度曲线", "配色"])
        self.assertTrue(r["ok"])
        self.assertEqual(r["mode"], "clean_room")
        self.assertGreaterEqual(r["score"], 0.9)
        self.assertEqual(r["beats"], 4)  # 一步一拍
        self.assertTrue(r["evidence"]["ok"])
        self.assertIn("零照搬", r["clean_room_declaration"])

    def test_pipeline_refine_rounds_capped(self):
        p = cg.CraftPipeline(mode="clean_room", max_rounds=3, threshold=0.99)
        r = p.run("目标", ["a", "b", "c"])
        self.assertLessEqual(r["rounds"], 3)

    def test_audit_snapshot(self):
        s = cg.audit()
        self.assertTrue(s["zero_guess"].startswith("checked"))
        self.assertFalse(s["neural"])
        self.assertEqual(len(s["organs"]), 6)
        self.assertIn("holoaeon.graph.AdaptiveGraph", s["reused_modules"])


if __name__ == "__main__":
    unittest.main()
