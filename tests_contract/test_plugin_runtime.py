# -*- coding: utf-8 -*-
"""V4.1-B1 · B8 六项插件接实际推理 · 旁挂单测（6 项）。

运行：python -m unittest discover -s tests_contract -v
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from holoaeon.fusion_upgrade import plugin_runtime as PR  # noqa: E402

IVSA_ROOT = r"F:\doubaowork\开源发布_中西医融合康复工程_20261026\integrative-rehab-vsa"


def _runtime():
    return PR.PluginRuntime.load(root=ROOT, guest_root=IVSA_ROOT)


class PluginRuntimeTest(unittest.TestCase):
    def test_01_default_disabled(self):
        rt = _runtime()
        self.assertFalse(rt.plugin["enabled_by_default"])
        self.assertEqual(rt.resolve_all()["capabilities_loaded"], 0)

    def test_02_explicit_enable_only(self):
        rt = _runtime()
        self.assertFalse(rt.enable("")["ok"])
        self.assertFalse(rt.enable("潮起开门 ")["ok"])
        self.assertTrue(rt.enable("潮起开门")["ok"])
        self.assertTrue(rt.enable(rt.plugin["seal"])["ok"])

    def test_03_six_capabilities_loaded(self):
        rt = _runtime()
        rt.enable("潮起开门")
        got = rt.resolve_all()
        self.assertEqual(got["capabilities_loaded"], 6)
        self.assertEqual(set(rt.declared_capabilities()), set(rt.capability_ids()))

    @unittest.skipUnless(os.path.isdir(IVSA_ROOT), "客仓不在本机")
    def test_04_counts_match_guest(self):
        rt = _runtime()
        rt.enable("潮起开门")
        rows = {r["capability"]: r["rows"] for r in rt.resolve_all()["results"]}
        self.assertEqual(rows["channel_groups_17"], 17)
        self.assertEqual(rows["heartbeat_70_registry"], 70)
        self.assertEqual(rows["rehab_organs_11"], 11)
        self.assertEqual(rows["chronic_diseases_7"], 7)
        self.assertEqual(rows["rehab_cases_20"], 20)
        self.assertEqual(rows["capability_dimensions_147"], 147)

    def test_05_no_ivsa_import(self):
        src = open(os.path.join(ROOT, "holoaeon", "fusion_upgrade",
                                "plugin_runtime.py"), encoding="utf-8").read()
        self.assertNotIn("import ivsa", src)
        self.assertNotIn("integrative", src)
        self.assertNotIn("subprocess", src)

    def test_06_bridge_deterministic_and_guarded(self):
        rt = _runtime()
        rt.enable("潮起开门")
        bridge = PR.ReasoningBridge(rt)
        q = "这条经络通道属于哪个分组？17 通道如何分布"
        a1, a2 = bridge.ask(q), bridge.ask(q)
        self.assertEqual(a1["seal"], a2["seal"])
        self.assertIn("channel_groups_17", a1["routed"])
        self.assertEqual(a1["evidence_class"], "simulated")
        g = bridge.ask("每次服用多少 mg？")
        self.assertTrue(g["guard"]["blocked"])
        self.assertEqual(g["facts"], [])


if __name__ == "__main__":
    unittest.main()
