# -*- coding: utf-8 -*-
"""V4.6 契约测试：扩展卡槽（只声明不接线）。"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from holoaeon.fusion_upgrade import slot_registry as sr
from holoaeon.fusion_upgrade.model_gateway import build_gateway


class SlotTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = sr.load(ROOT)

    def test_01_validates_clean(self):
        self.assertEqual(sr.validate(self.payload), [])

    def test_02_lock_unchanged(self):
        s = sr.summary(self.payload)
        self.assertEqual(s["lock"], {"agents": 25, "skills": 47, "packs": 9})

    def test_03_ids_unique_and_prefixed(self):
        ids = [x["slot_id"] for x in self.payload["slots"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(i.startswith("EXT-") for i in ids))

    def test_04_kinds_and_status_whitelisted(self):
        for s in self.payload["slots"]:
            self.assertIn(s["kind"], sr.KINDS)
            self.assertIn(s["status"], sr.STATUSES)

    def test_05_open_slots_are_claimable(self):
        opens = sr.open_slots(self.payload)
        self.assertGreaterEqual(len(opens), 1)
        for s in opens:
            self.assertTrue(s["next_action"])

    def test_06_no_public_url_in_slots(self):
        for s in self.payload["slots"]:
            blob = " ".join(str(s.get(k) or "") for k in ("contract", "next_action", "notes"))
            self.assertFalse(sr._has_public_url(blob), s["slot_id"])

    def test_07_slots_do_not_switch_anything_on(self):
        clean = {k: v for k, v in os.environ.items() if not k.startswith("HOLOAEON_")}
        gw = build_gateway(ROOT, environ=clean)
        self.assertEqual(gw.state()["enabled"], [])

    def test_08_bad_payload_reports_errors(self):
        bad = json.loads(json.dumps(self.payload))
        bad["slots"][0]["slot_id"] = "X-1"
        bad["lock"]["agents"] = 26
        errs = sr.validate(bad)
        self.assertTrue(any("前缀" in e for e in errs))
        self.assertTrue(any("维度锁" in e for e in errs))

    def test_09_guide_covers_every_slot(self):
        with open(os.path.join(ROOT, "docs", "扩展卡槽与协作开发指南.md"), encoding="utf-8") as f:
            text = f.read()
        for s in self.payload["slots"]:
            self.assertIn(s["slot_id"], text)


if __name__ == "__main__":
    unittest.main()
