# -*- coding: utf-8 -*-
"""V6.0-B1 契约测试：族级登记表 + 桥接 + 路由第三态 + L3 精度 + 资源红线。

覆盖投喂包 PR-1/PR-2/PR-4 的验收点，全部确定性、离线。
密令：潮起开门，潮落闭嘴。evidence_class=simulated。
"""
import ast
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from holoaeon.agent import Agent, ALLOW_SINGLE_SKILL_FALLBACK  # noqa: E402
from holoaeon.fusion_upgrade import external_skill_registry as esr  # noqa: E402
from holoaeon.kernel import Kernel  # noqa: E402
from holoaeon.redline import RedlineVisitor, _stdlib_names  # noqa: E402
from holoaeon.spec import HoloAeonConfig  # noqa: E402


class FamilyRegistryTest(unittest.TestCase):
    def test_01_registry_shape(self):
        st = esr.stats(ROOT)
        self.assertEqual(st["registry_id"], "SG-V6-SKILL-FAMILY-MAP-V1")
        self.assertGreaterEqual(st["family_count"], 50)
        self.assertEqual(st["member_total"], 1229)
        self.assertEqual(st["declared_total"], 1229)
        self.assertTrue(st["digest_match"])
        self.assertFalse(st["missing"])

    def test_02_dimension_lock_untouched(self):
        st = esr.stats(ROOT)
        self.assertEqual(st["dimension_lock"],
                         {"agents": 25, "skills": 47, "packs": 9, "extra_packs": 10})
        self.assertEqual(st["runtime_skills"], 1199)

    def test_03_family_of_is_total(self):
        fams = esr.families(ROOT)
        total = sum(f["count"] for f in fams)
        self.assertEqual(total, 1229)
        sample = fams[0]["members"][0]
        self.assertEqual(esr.family_of(sample, ROOT), fams[0]["id"])


class BridgeRouteTest(unittest.TestCase):
    def test_04_match_is_deterministic(self):
        a = esr.match("文献 语义通信 综述", k=3, root=ROOT)
        b = esr.match("文献 语义通信 综述", k=3, root=ROOT)
        self.assertEqual(a, b)
        self.assertTrue(a)
        self.assertIn("family", a[0])

    def test_05_route_reports_no_match_honestly(self):
        r = esr.route("", k=3, root=ROOT)
        self.assertEqual(r["status"], "no_family_matched")
        self.assertEqual(r["candidates"], [])
        self.assertIn("hint", r)


class KernelFallbackTest(unittest.TestCase):
    def test_06_no_agent_matched_third_state(self):
        cfg = HoloAeonConfig(broadcast_on_no_match=False)
        cfg.allow_single_skill_fallback = False
        k = Kernel(cfg)
        res = k.submit("完全无关的任务 zzz")
        self.assertEqual(res["status"], "no_agent_matched")
        self.assertFalse(res["all_ok"])
        self.assertEqual(res["targets"], [])
        self.assertIn("hint", res)
        self.assertIn("external_candidates", res)

    def test_07_star_still_broadcasts(self):
        k = Kernel()
        k.register_agent(Agent("a1"))
        k.register_agent(Agent("a2"))
        res = k.submit("anything", to="*")
        self.assertEqual(res["targets"], ["a1", "a2"])

    def test_08_single_skill_fallback_is_marked_degraded(self):
        k = Kernel()
        k.skills.register_fn("only", lambda task: "ok:" + task)
        agent = k.register_agent(Agent("solo", skill_names=["only"]))
        res = k.submit("zzz 无关任务", to="solo")
        self.assertTrue(res["all_ok"])
        self.assertTrue(res["results"][0]["degraded"])

    def test_09_switch_off_fails_loud(self):
        k = Kernel(HoloAeonConfig(broadcast_on_no_match=False))
        k.skills.register_fn("only", lambda task: "ok")
        agent = k.register_agent(Agent("solo", skill_names=["only"]))
        agent._cfg_allow_single_fallback = False
        res = k.submit("zzz 无关任务", to="solo")
        self.assertEqual(res["results"][0]["status"], "no_skill")
        self.assertFalse(agent._last_fallback)
        self.assertTrue(ALLOW_SINGLE_SKILL_FALLBACK)


class RedlineResourceRuleTest(unittest.TestCase):
    def _scan(self, source):
        v = RedlineVisitor("sample.py", _stdlib_names())
        v.visit(ast.parse(source))
        return v.violations

    def test_10_nested_open_is_flagged(self):
        bad = "import json\nx = json.load(open('a.json'))\n"
        got = self._scan(bad)
        self.assertTrue([x for x in got if x["kind"] == "resource"])

    def test_11_read_after_open_is_flagged(self):
        bad = "t = open('a.txt').read()\n"
        got = self._scan(bad)
        self.assertTrue([x for x in got if x["kind"] == "resource"])

    def test_12_with_block_is_clean(self):
        good = ("import json\nwith open('a.json') as f:\n    x = json.load(f)\n")
        self.assertEqual([x for x in self._scan(good) if x["kind"] == "resource"], [])


if __name__ == "__main__":
    unittest.main()
