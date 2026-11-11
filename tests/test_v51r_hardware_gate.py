# -*- coding: utf-8 -*-
"""test_v51r_hardware_gate —— V51R 强化批测试（真 unittest）。

覆盖：EDA 三段（elaborate/simulate/netlist）× V51 六算子复用 × 升级契约
耦合 × 张量耦合不变 × compile_modes 范式对齐 × 总闸诚实边界。
全部确定性、无网络、无内核实例。
"""
from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holoaeon.hardware_gate import (  # noqa: E402
    CHAIN_POSITION,
    COMPILE_STAGES,
    NETLIST_MECHANISM,
    SEAL,
    HardwareGate,
    NetlistElaborator,
    NetlistSimulator,
    NetlistSynthesizer,
    TensorCouple,
    UpgradeContractCoupler,
    fingerprint,
    probe,
)
from holoaeon.circuit_gate import CIRCUIT_CONCEPTS  # noqa: E402


DESC = {"voltage": 5.0, "current": 2.0, "resistance": 1.0}


# ---------------------------------------------------------------- 一、展开段
class TestNetlistElaborator(unittest.TestCase):
    def test_elaborate_devices_deterministic(self):
        nl1 = NetlistElaborator().elaborate(DESC)
        nl2 = NetlistElaborator().elaborate(DESC)
        self.assertEqual(nl1, nl2)
        self.assertEqual(nl1["mode"], "elaborate")
        self.assertEqual(nl1["components"], 3)
        self.assertEqual(nl1["ports"], 3)
        self.assertEqual(nl1["devices"][0]["id"], "D00-voltage")

    def test_elaborate_daisy_chain_closed(self):
        nl = NetlistElaborator().elaborate(DESC)
        ids = [d["id"] for d in nl["devices"]]
        for i, e in enumerate(nl["edges"]):
            self.assertEqual(e["from"], ids[i])
            self.assertEqual(e["to"], ids[(i + 1) % len(ids)])  # 环闭环
        self.assertEqual(nl["anchors"]["source"], ids[0])
        self.assertEqual(nl["anchors"]["ground"], ids[-1])

    def test_elaborate_rejects_unknown_concept(self):
        with self.assertRaises(ValueError):
            NetlistElaborator().elaborate({"photon": 1.0})

    def test_elaborate_rejects_empty(self):
        with self.assertRaises(ValueError):
            NetlistElaborator().elaborate({})

    def test_elaborate_sha_stable(self):
        nl = NetlistElaborator().elaborate(DESC)
        self.assertEqual(len(nl["sha256"]), 16)

    def test_elaborate_weight_normalized(self):
        nl = NetlistElaborator().elaborate(DESC)
        for e in nl["edges"]:
            self.assertGreaterEqual(e["weight"], 0.0)
            self.assertLessEqual(e["weight"], 1.0)

    def test_elaborate_concept_table_shared_with_tensorcircuit(self):
        # 概念词汇表与 TensorCircuit 同一来源（张量耦合口径一致）
        nl = NetlistElaborator().elaborate(DESC)
        for d in nl["devices"]:
            self.assertIn(d["concept"], CIRCUIT_CONCEPTS)


# ---------------------------------------------------------------- 二、仿真段
class TestNetlistSimulator(unittest.TestCase):
    def setUp(self):
        self.nl = NetlistElaborator().elaborate(DESC)
        self.sim = NetlistSimulator().simulate(self.nl)

    def test_simulate_mode_and_waves(self):
        self.assertEqual(self.sim["mode"], "simulate")
        for lane in ("kirchhoff", "resonant", "feedback",
                     "impedance", "memrist"):
            self.assertIn(lane, self.sim)

    def test_kcl_strict_pass_on_daisy_chain(self):
        # 菊花链闭环等权循环：每器件流入=流出 → KCL 全严格通过
        self.assertTrue(self.sim["kirchhoff"]["kcl_ok"])
        self.assertEqual(self.sim["kirchhoff"]["violations"], 0)

    def test_verdict_pass_or_warn_not_fail(self):
        self.assertIn(self.sim["verdict"], ("PASS", "WARN"))

    def test_resonant_ranked_all_devices(self):
        self.assertEqual(self.sim["resonant"]["ranked"], 3)

    def test_feedback_wave_reported(self):
        fb = self.sim["feedback"]
        self.assertIn("converged", fb)
        self.assertIn("stability", fb)
        self.assertGreaterEqual(fb["rounds_run"], 1)

    def test_impedance_pairs_count(self):
        self.assertEqual(len(self.sim["impedance"]["pairs"]), 3)
        self.assertGreaterEqual(self.sim["impedance"]["mean_efficiency"], 0.0)

    def test_memrist_states_cover_edges(self):
        self.assertEqual(len(self.sim["memrist"]["states"]), 3)

    def test_simulate_requires_elaborate_input(self):
        with self.assertRaises(ValueError):
            NetlistSimulator().simulate({"mode": "not_elaborate"})

    def test_kcl_violation_yields_fail(self):
        # 构造破缺环：删一条环边 → 末器件只进不出 → KCL 全严格 FAIL
        nl = NetlistElaborator().elaborate(DESC)
        nl["edges"] = nl["edges"][:2]  # (0,1),(1,2) 留存，缺 (2,0)
        sim = NetlistSimulator().simulate(nl)
        self.assertEqual(sim["verdict"], "FAIL")
        self.assertFalse(sim["kirchhoff"]["kcl_ok"])


# ---------------------------------------------------------------- 三、综合段
class TestNetlistSynthesizer(unittest.TestCase):
    def setUp(self):
        self.nl = NetlistElaborator().elaborate(DESC)
        self.sim = NetlistSimulator().simulate(self.nl)
        self.syn = NetlistSynthesizer().synthesize(self.nl, self.sim)

    def test_synthesize_shape_aligned(self):
        # 形状对齐 compile_modes.netlist：nodes/edges/weights
        for key in ("mode", "nodes", "edges", "weights"):
            self.assertIn(key, self.syn)
        self.assertEqual(self.syn["mode"], "netlist")
        self.assertEqual(self.syn["nodes"], 3)
        self.assertEqual(self.syn["edges"], 3)

    def test_synthesize_sha_full_64(self):
        self.assertEqual(len(self.syn["sha256"]), 64)

    def test_synthesize_deterministic(self):
        syn2 = NetlistSynthesizer().synthesize(
            NetlistElaborator().elaborate(DESC),
            NetlistSimulator().simulate(
                NetlistElaborator().elaborate(DESC)))
        self.assertEqual(self.syn["sha256"], syn2["sha256"])

    def test_synthesize_verdict_carried(self):
        self.assertEqual(self.syn["verdict"], self.sim["verdict"])

    def test_synthesize_weights_impedance_damped(self):
        for key, w in self.syn["weights"].items():
            self.assertGreaterEqual(w, 0.0)
            self.assertLessEqual(w, 1.0)

    def test_synthesize_rejects_wrong_input(self):
        with self.assertRaises(ValueError):
            NetlistSynthesizer().synthesize({"mode": "x"}, self.sim)
        with self.assertRaises(ValueError):
            NetlistSynthesizer().synthesize(self.nl, {"mode": "x"})

    def test_meridian_note_present(self):
        self.assertIn("meridian", self.syn["meridian_note"])


# ---------------------------------------------------------------- 四、契约耦合
class TestUpgradeContractCoupler(unittest.TestCase):
    def setUp(self):
        self.result = HardwareGate().compile(DESC)
        self.cp = UpgradeContractCoupler().couple(
            self.result["elaborate"], self.result["netlist"])

    def test_contract_valid_reuses_fusion_upgrade(self):
        # 真实复用 fusion_upgrade.contract 三件套（非自造形状）
        self.assertTrue(self.cp["validate"]["ok"])
        self.assertIn("contract_id", self.cp["contract"])
        self.assertEqual(self.cp["contract"]["mechanism"], NETLIST_MECHANISM)
        self.assertEqual(self.cp["contract"]["lane"], "read")

    def test_receipt_verdict_follows_netlist(self):
        expected = self.result["netlist"]["verdict"].lower()
        self.assertEqual(self.cp["receipt"]["verdict"], expected)

    def test_receipt_evidence_class_simulated(self):
        # 只读契约回执（不换代码不执行外部技能）
        self.assertEqual(self.cp["receipt"]["evidence_class"], "simulated")
        self.assertIn("不改对端代码", self.cp["receipt"]["note"])

    def test_hot_swap_note_declares_not_executes(self):
        self.assertIn("不执行内核热装", self.cp["hot_swap_note"])

    def test_couple_rejects_non_netlist(self):
        with self.assertRaises(ValueError):
            UpgradeContractCoupler().couple(
                {"mode": "elaborate"}, {"mode": "simulate"})


# ---------------------------------------------------------------- 五、张量耦合
class TestTensorCouple(unittest.TestCase):
    def setUp(self):
        self.gate = HardwareGate()
        self.result = self.gate.compile(DESC)
        self.tc = TensorCouple()

    def test_elaborate_tensor_dim_matches_space(self):
        et = self.tc.elaborate_tensor(self.result["elaborate"])
        self.assertGreater(len(et), 0)

    def test_netlist_tensor_bundle(self):
        nt = self.tc.netlist_tensor(self.result["netlist"])
        self.assertGreater(len(nt), 0)

    def test_netlist_tensor_empty_raises(self):
        with self.assertRaises(ValueError):
            self.tc.netlist_tensor({"mode": "netlist", "weights": {}})

    def test_similarity_self_beats_far(self):
        far = {"ground": 1.0}
        same = self.tc.similarity(DESC, DESC)
        other = self.tc.similarity(DESC, far)
        self.assertGreater(same, other)

    def test_similarity_deterministic(self):
        a = self.tc.similarity(DESC, DESC)
        b = self.tc.similarity(DESC, DESC)
        self.assertEqual(a, b)

    def test_carrier_is_circuit_gate_tensorcircuit(self):
        # 载体= V51 原件 TensorCircuit（张量向量耦合不变）
        from holoaeon.circuit_gate import TensorCircuit as TC
        self.assertIsInstance(self.tc.tc, TC)


# ---------------------------------------------------------------- 六、范式对齐
class TestParadigmAlignment(unittest.TestCase):
    def test_compile_stages_match_compile_modes(self):
        # 三段名与 design_vocab.compile_modes.COMPILE_MODES 一致
        self.assertEqual([s[0] for s in COMPILE_STAGES],
                         ["elaborate", "simulate", "netlist"])

    def test_compile_modes_precedent_alive(self):
        # 在仓先例原样可跑（回归保护）
        from holoaeon.design_vocab import compile_modes
        r = compile_modes.compile_text("<div class=\"a\">x</div>")
        self.assertIn("elaborate", r)
        self.assertIn("simulate", r)
        self.assertIn("netlist", r)

    def test_compile_one_pass(self):
        r = HardwareGate().compile(DESC)
        self.assertEqual(r["elaborate"]["mode"], "elaborate")
        self.assertEqual(r["simulate"]["mode"], "simulate")
        self.assertEqual(r["netlist"]["mode"], "netlist")

    def test_chain_position_ring17_sibling(self):
        self.assertEqual(CHAIN_POSITION["ring"], 17)
        self.assertEqual(CHAIN_POSITION["batch"], "V51R")
        ups = " ".join(CHAIN_POSITION["upstream"])
        self.assertIn("circuit_gate", ups)
        self.assertIn("fusion_upgrade.contract", ups)
        self.assertIn("compile_modes", ups)


# ---------------------------------------------------------------- 七、总闸
class TestHardwareGate(unittest.TestCase):
    def test_probe_all_green(self):
        r = probe()
        self.assertTrue(r["ok"])
        for name, c in r["checks"].items():
            self.assertTrue(c["ok"], f"check failed: {name}")

    def test_run_manifest_structure(self):
        m = HardwareGate().run()
        self.assertEqual(m["ring"], 17)
        self.assertEqual(m["batch"], "V51R")
        self.assertEqual(m["stages"], ["elaborate", "simulate", "netlist"])
        self.assertEqual(m["mechanism"], "meridian")
        for art in ("elaborate_receipt", "simulate_receipt",
                    "netlist_receipt", "contract_receipt"):
            self.assertIn(art, m["artifacts"])

    def test_run_manifest_honesty(self):
        m = HardwareGate().run()
        h = m["honesty"]
        self.assertFalse(h["neural"])
        self.assertFalse(h["network"])
        self.assertEqual(h["new_dependencies"], 0)
        self.assertIn("非设备驱动", h["hardware"])
        self.assertIn("circuit_gate", h["reuses"][0])
        self.assertIn("fusion_upgrade.contract", h["reuses"][1])

    def test_run_tensor_coupling_declared_unchanged(self):
        m = HardwareGate().run()
        t = m["tensor_coupling"]
        self.assertIn("不变", t["carrier"])
        self.assertGreater(t["dim"], 0)
        self.assertEqual(len(t["elaborate_tensor_sha16"]), 16)

    def test_run_custom_description(self):
        m = HardwareGate().run({"capacitance": 3.0, "source": 1.5})
        self.assertEqual(m["artifacts"]["elaborate_receipt"]["components"], 2)

    def test_seal_and_fingerprint(self):
        fp = fingerprint()
        self.assertEqual(fp["ring"], 17)
        self.assertEqual(fp["batch"], "V51R")
        self.assertEqual(fp["seal"], SEAL)
        self.assertEqual(fp["stages"], ["elaborate", "simulate", "netlist"])
        self.assertEqual(fp["mechanism"], "meridian")

    def test_gate_shares_tensor_space(self):
        gate = HardwareGate()
        # TensorCouple 与 circuit_gate.TensorCircuit 装配链共享同一空间
        self.assertIsInstance(gate.tensor.tc.space.dim, int)


if __name__ == "__main__":
    unittest.main(verbosity=2)
