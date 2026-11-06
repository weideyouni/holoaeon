# -*- coding: utf-8 -*-
"""V37 神龟域闸门测试。零依赖，确定性断言。"""
import unittest

from holoaeon.shengui_gate import (CHAIN_POSITION, DNAEngine, DualCore,
                                   HierarchyLock, MetabolismLoop, SEAL,
                                   SanjiaoBus, ShenguiConductor,
                                   WuxingBalance, WUXING_TABLE)


DNA = DNAEngine({"rule_a": "冻结", "rule_b": "等保"},
                {"p1": 1, "p2": 2, "p3": 3, "p4": 4, "p5": 5,
                 "p6": 6, "p7": 7, "p8": 8, "p9": 9, "p10": 10})


class TestShenguiGate(unittest.TestCase):
    def test_chain_ring9(self):
        self.assertEqual(CHAIN_POSITION["ring"], 9)
        self.assertIn("双系统首桥", CHAIN_POSITION["name"])
        self.assertIn("同源认亲", CHAIN_POSITION["lineage_note"])

    def test_metaphor_note(self):
        self.assertIn("隐喻", CHAIN_POSITION["metaphor_note"])
        self.assertIn("不主张意识觉醒", CHAIN_POSITION["metaphor_note"])

    def test_allocate_scales_with_compliance(self):
        hi = DualCore.allocate(0.9, 0.8, 0.8)
        lo = DualCore.allocate(0.3, 0.8, 0.8)
        self.assertGreater(hi["quota"], lo["quota"])

    def test_allocate_range_guard(self):
        self.assertFalse(DualCore.allocate(1.5, 0.5, 0.5)["ok"])

    def test_freeze_on_forbidden(self):
        r = DualCore.freeze("尝试绕过审核")
        self.assertTrue(r["freeze"])
        self.assertIn("资源冻结", r["actions"])

    def test_dna_rigid_immutable(self):
        r = DNA.mutate({"rule_a": "改"})
        self.assertFalse(r["ok"])

    def test_dna_mutation_limit(self):
        changes = {f"p{i}": i + 1 for i in range(1, 11)}   # 全改=100%
        self.assertFalse(DNA.mutate(changes)["ok"])

    def test_dna_small_mutation_ok(self):
        r = DNA.mutate({"p1": 11})
        self.assertTrue(r["ok"])   # 1/10=10% ≤15%

    def test_hierarchy_apoptosis_and_incinerate(self):
        h = HierarchyLock()
        h.spawn("c1", "僧", 1)
        self.assertEqual(h.tick("c1")["fate"], "apoptosis")
        h.spawn("c2", "触手", 5)
        self.assertEqual(h.tick("c2", fault=True)["fate"], "incinerated")

    def test_hierarchy_orphan_owner(self):
        h = HierarchyLock()
        self.assertFalse(h.spawn("c9", "不存在的脏腑", 3)["ok"])

    def test_cell_cannot_command_organ(self):
        h = HierarchyLock()
        self.assertFalse(h.cross_command("cell:c1", "organ:法")["ok"])

    def test_sanjiao_forbidden_direct(self):
        bus = SanjiaoBus()
        r = bus.send("upper", "cell:c1", "organ:法", {})
        self.assertFalse(r["ok"])

    def test_sanjiao_log_auditable(self):
        bus = SanjiaoBus()
        bus.send("upper", "organ:佛", "organ:法", {"cmd": 1})
        self.assertEqual(len(bus.log), 1)

    def test_wuxing_thresholds(self):
        r = WuxingBalance(cpu_mem=0.8, attack=True).balance()
        organs = [a["organ"] for a in r["actions"]]
        self.assertIn("心_佛模块", organs)
        self.assertIn("肝_触手棱镜", organs)

    def test_wuxing_table_five(self):
        self.assertEqual(len(WUXING_TABLE), 5)

    def test_metabolism_purge(self):
        m = MetabolismLoop()
        m.step("脏数据", quality="waste")
        r = m.step("好知识", quality="valid")
        self.assertIn(r["stage"], ("吸收", "排泄"))

    def test_dual_mode_isolation(self):
        c = ShenguiConductor(["每日早课", "生成周报"])
        self.assertEqual(c.mode("生成周报")["mode"], "compat")
        self.assertEqual(c.mode("设计量子引擎")["mode"], "enhanced")

    def test_conductor_freeze_first(self):
        c = ShenguiConductor([])
        r = c.conduct("越权操作", 0.9, 0.9, 0.9)
        self.assertEqual(r["verdict"], "frozen_by_compliance")

    def test_seal_all(self):
        for obj in (DualCore.freeze(""), DNA.mutate({}),
                    HierarchyLock().tick("none"),
                    SanjiaoBus().send("x", "a", "b", {}),
                    WuxingBalance().balance(),
                    MetabolismLoop().step("x", "valid")):
            self.assertEqual(obj["seal"], SEAL)


if __name__ == "__main__":
    unittest.main()
