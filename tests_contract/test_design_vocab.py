# -*- coding: utf-8 -*-
"""V5.1 契约测试：设计语汇旁挂引擎（不改维度、不动卡槽 12 条）。"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from holoaeon.design_vocab import detectors as dv
from holoaeon.design_vocab import compile_modes as cm
from holoaeon.design_vocab import hebbian as hb
from holoaeon.design_vocab import meridian as md
from holoaeon.design_vocab import vocabulary as vc

SLOP = """<style>
body { font-family: Inter, sans-serif; }
.hero { background: linear-gradient(135deg, #7c3aed, #6366f1); }
.card { border-radius: 999px; }
.chip { border-radius: 9999px; }
.btn { border-radius: 999px; }
</style>
<div class="card">
  <div class="card">
    <h1>HOLOAEON SUPERSYSTEM MATRIX ENGINE IS LIVE AND READY TO SHIP</h1>
    <h3>🚀 升级</h3>
    <p style="color:#888;font-size:11px;margin:0;padding:0;">Lorem ipsum dolor sit amet</p>
    <div class="card"><p>x</p></div>
  </div>
</div>
<div style="box-shadow: 0 1px 2px #000, 0 4px 8px #111, 0 12px 24px #222;"></div>
<p style="-webkit-background-clip:text;background:linear-gradient(90deg,#7c3aed,#6366f1);font-size:11px;">y</p>
"""

CLEAN = """<style>
body { font-family: var(--font-sans); }
.card { border-radius: 6px; }
</style>
<div class="card">
  <h1>HoloAeon</h1>
  <h2>当前状态</h2>
  <p style="color:#1A1B1C;margin:0;">正文说明</p>
</div>
"""


class DesignVocabTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(ROOT, "data", "design_vocab_registry.json"), encoding="utf-8") as f:
            cls.reg = json.load(f)
        with open(os.path.join(ROOT, "data", "extension_slots.json"), encoding="utf-8") as f:
            cls.slots = json.load(f)

    def test_01_registry_declares_upstream_without_vendoring(self):
        src = self.reg["source"]
        self.assertEqual(self.reg["id"], "SG-V51-DESIGN-VOCAB-V1")
        self.assertEqual(src["upstream_license"], "Apache-2.0")
        self.assertEqual(src["upstream_commands"], 24)
        self.assertEqual(src["upstream_rules"], 62)
        self.assertFalse(src["vendored"])
        self.assertFalse(src["engine_copied"])
        self.assertFalse(src["text_copied"])

    def test_02_commands_are_24_and_groups_covered(self):
        self.assertEqual(len(vc.COMMANDS), 24)
        self.assertEqual(len(set(vc.command_ids())), 24)
        for g in vc.GROUPS:
            self.assertGreaterEqual(len(vc.by_group(g)), 1)

    def test_03_rules_unique_with_legal_severity_and_channel(self):
        ids = [r[0] for r in dv.RULES]
        self.assertEqual(len(ids), 12)
        self.assertEqual(len(set(ids)), 12)
        for rid, name, sev, chan in dv.RULES:
            self.assertIn(sev, dv.SEVERITY_ORDER)
            self.assertEqual(md.RULE_CHANNEL[rid], chan)
            self.assertTrue(name)

    def test_04_slop_hits_all_rules_clean_hits_none(self):
        hits = dv.scan(SLOP)
        self.assertEqual(sorted({h.rule_id for h in hits}), sorted(r[0] for r in dv.RULES))
        self.assertEqual(dv.scan(CLEAN), [])
        self.assertEqual(dv.scan(SLOP), dv.scan(SLOP))  # 确定性

    def test_05_compile_modes_agree(self):
        full = cm.compile_text(SLOP)
        self.assertEqual(full["simulate"]["findings"], len(dv.scan(SLOP)))
        self.assertGreater(full["elaborate"]["components"], 0)
        self.assertGreater(full["netlist"]["edges"], 0)
        self.assertEqual(full["simulate"]["verdict"], "FAIL")
        # P0 必须排在先修位
        self.assertEqual(cm.simulate(SLOP)["first_fix"], dv.rank(dv.scan(SLOP))[0].rule)

    def test_06_hebbian_is_symmetric_and_normalized(self):
        raw = hb.cooccurrence([sorted({h.rule_id for h in dv.scan(SLOP)})] * 2)
        norm = hb.normalize(raw)
        self.assertTrue(all(0.0 <= w <= 1.0 + 1e-9 for w in raw.values()))
        self.assertTrue(all(0.0 <= w <= 1.0 + 1e-9 for w in norm.values()))
        self.assertEqual(hb.similarity("DV-01", "DV-01", raw), 1.0)
        self.assertEqual(hb.similarity("DV-01", "DV-12", {}), 0.0)

    def test_07_meridian_covers_four_channels(self):
        route = md.route(dv.scan(SLOP))
        self.assertEqual(sorted(route["counts"]), sorted(n for n, _ in md.CHANNELS))
        self.assertEqual(route["total"], len(dv.scan(SLOP)))
        self.assertGreaterEqual(len(route["blocked"]), 2)
        for name, _ in md.CHANNELS:
            self.assertTrue(md.channel_rules(name))

    def test_08_dimension_lock_and_slots_untouched(self):
        with open(os.path.join(ROOT, "reports", "dimension_lock.json"), encoding="utf-8") as f:
            lock = json.load(f)
        dims = {d["name"]: d["value"] for d in lock["dimensions"]}
        self.assertEqual(dims["holoaeon_agents"], 25)
        self.assertEqual(dims["holoaeon_skills"], 47)
        self.assertEqual(dims["holoaeon_domain_packs"], 9)
        self.assertEqual(len(self.slots["slots"]), 12)
        self.assertTrue(all(not s["slot_id"].startswith("EXT-DESIGN") for s in self.slots["slots"]))
        self.assertEqual(self.slots["lock"], {"agents": 25, "skills": 47, "packs": 9, "note": self.slots["lock"]["note"]})


if __name__ == "__main__":
    unittest.main()
