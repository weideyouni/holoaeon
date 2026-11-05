# -*- coding: utf-8 -*-
"""V33 数学编排闸门测试。零依赖，确定性断言。"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holoaeon.math_gate import (CHAIN_POSITION, MathConductor, MathDNA,
                                MathEnvelope, MATH_DNA, MathGate,
                                DomainRouter, SafetyValves, SEAL)


class TestMathGate(unittest.TestCase):
    def test_chain_ring5(self):
        self.assertEqual(CHAIN_POSITION["ring"], 5)
        self.assertEqual(CHAIN_POSITION["name"], "数学编排")
        self.assertEqual(len(CHAIN_POSITION["same_as"]), 4)

    def test_dna_seven(self):
        self.assertEqual(len(MATH_DNA), 7)
        self.assertIn("数值吻合≠定理", MATH_DNA)

    def test_dna_violation_detect(self):
        hits = MathDNA.violations("仿真证明了该结论成立")
        self.assertIn("仿真≠证明", hits)

    def test_valve_m14_blocks(self):
        r = SafetyValves().check("给我荐股并给出目标价")
        self.assertTrue(r["blocked"])
        self.assertEqual(r["hits"][0]["valve"], "M14")

    def test_valve_zero_trade_strips(self):
        r = SafetyValves().check("分析一下买入点和卖出点")
        self.assertFalse(r["blocked"])
        self.assertEqual(r["hits"][0]["valve"], "ZERO_TRADE")

    def test_gate_l2_block(self):
        r = MathGate().request("满仓梭哈这只必赚")
        self.assertEqual(r["verdict"], "blocked_by_L2")

    def test_gate_l5_veto(self):
        r = MathGate().request("这个数值吻合，所以定理成立")
        self.assertEqual(r["verdict"], "vetoed_by_L5")

    def test_gate_pass(self):
        r = MathGate().request("用迭代法求解方程组并分析误差")
        self.assertEqual(r["verdict"], "pass")

    def test_route_domains(self):
        self.assertEqual(DomainRouter.route("给学生讲例题")["domain"], "teaching")
        self.assertEqual(DomainRouter.route("运维巡检探针")["domain"], "ops")

    def test_envelope_zero_forgery(self):
        e = MathEnvelope("math_master", {"x": 1})
        rc = e.receipt()
        self.assertFalse(rc["forged"])
        self.assertTrue(e.verify(rc["digest"])["intact"])
        self.assertFalse(e.verify("deadbeef")["intact"])

    def test_conductor_end_to_end(self):
        r = MathConductor().conduct("math_master", "讲解一下最小二乘拟合")
        self.assertEqual(r["gate"]["verdict"], "pass")
        self.assertEqual(r["route"]["domain"], "research")
        self.assertIn("seal", r)


if __name__ == "__main__":
    unittest.main()
