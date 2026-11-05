# -*- coding: utf-8 -*-
"""V35 宇宙域编排闸门测试。零依赖，确定性断言。"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holoaeon.cosmo_gate import (CHAIN_POSITION, DualLoop,
                                 EntropyBalance, MentorRouter, SEAL,
                                 StormIteration)


CANDS = [{"id": "a", "score": 0.9}, {"id": "b", "score": 0.8},
         {"id": "c", "score": 0.7}]
POP = [{"id": "a", "gains": [3, 2]}, {"id": "b", "gains": [2, 3]},
       {"id": "c", "gains": [1, 1]}]


class TestCosmoGate(unittest.TestCase):
    def test_chain_ring7(self):
        self.assertEqual(CHAIN_POSITION["ring"], 7)
        self.assertEqual(CHAIN_POSITION["name"], "宇宙域编排")
        self.assertIn("4th", CHAIN_POSITION["same_as_law"])

    def test_expand_unvisited_first(self):
        pick = DualLoop.expand(CANDS, {"a": 3, "b": 1})
        self.assertEqual(pick["id"], "c")   # 未访问优先（确定性）

    def test_expand_deterministic(self):
        r1 = DualLoop.expand(CANDS, {})
        r2 = DualLoop.expand(CANDS, {})
        self.assertEqual(r1["id"], r2["id"])   # 同输入同输出

    def test_fold_pareto(self):
        r = DualLoop.fold(POP)
        self.assertEqual(sorted(p["id"] for p in r["front"]), ["a", "b"])
        self.assertEqual(r["folded"], 1)   # c 被支配折叠

    def test_breathe_one_beat(self):
        r = DualLoop.breathe(CANDS, {}, POP)
        self.assertIn("expanded", r)
        self.assertIn("front", r)

    def test_router_known(self):
        r = MentorRouter.route("physics")
        self.assertTrue(r["ok"])
        self.assertEqual(r["mentor"], "M-P")
        self.assertEqual(r["star_guide"], "星导-自然")

    def test_router_unknown(self):
        self.assertFalse(MentorRouter.route("astrology")["ok"])

    def test_router_14_subjects(self):
        ok = sum(1 for s in MentorRouter.GROUP
                 if MentorRouter.route(s)["ok"])
        self.assertEqual(ok, 14)

    def test_storm_advance_and_close(self):
        s = StormIteration()
        for _ in range(9):
            s.step()
        last = s.step()
        self.assertTrue(last["done"])   # S10 收口

    def test_storm_fail_holds(self):
        s = StormIteration()
        r = s.step(ok=False)
        self.assertFalse(r["advanced"])   # 失败原地停（不倒退）

    def test_entropy_leap(self):
        self.assertTrue(EntropyBalance.check(0.6, 0.6)["negative_entropy_leap"])
        self.assertFalse(EntropyBalance.check(0.9, 0.2)["negative_entropy_leap"])

    def test_entropy_range_guard(self):
        self.assertFalse(EntropyBalance.check(1.5, 0.5)["ok"])


if __name__ == "__main__":
    unittest.main()
