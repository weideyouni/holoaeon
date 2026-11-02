# -*- coding: utf-8 -*-
"""V4.5-B1 契约测试：本地运行时联调只允许回环、回执诚实、默认全关。"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import live_gateway_probe as probe  # noqa: E402
from holoaeon.fusion_upgrade.model_gateway import build_gateway, load_catalog  # noqa: E402


class TestV45(unittest.TestCase):
    def test_01_rejects_public_host(self):
        with self.assertRaises(SystemExit):
            probe.local_only("https://api.openai.com/v1")

    def test_02_accepts_loopback(self):
        for b in ("http://127.0.0.1:1234/v1", "http://localhost:1234/v1"):
            probe.local_only(b)

    def test_03_loopback_whitelist_is_small(self):
        self.assertEqual(probe.LOOPBACK, {"127.0.0.1", "localhost", "::1", "0.0.0.0"})

    def test_04_lmstudio_default_is_loopback(self):
        cat = load_catalog(ROOT)
        lm = [p for p in cat["providers"] if p["id"] == "lmstudio"][0]
        self.assertIn(lm["default_base_url"].split("//")[1].split(":")[0], probe.LOOPBACK)

    def test_05_report_declares_live_local(self):
        path = os.path.join(ROOT, "reports", "v45_live_probe.json")
        if not os.path.isfile(path):
            self.skipTest("尚无联调回执")
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        self.assertEqual(d["evidence_class"], "live_local")
        self.assertEqual(d["host_scope"], "loopback_only")

    def test_06_probe_body_has_no_secret_fields(self):
        path = os.path.join(ROOT, "reports", "v45_live_probe.json")
        if not os.path.isfile(path):
            self.skipTest("尚无联调回执")
        with open(path, encoding="utf-8") as f:
            blob = f.read()
        self.assertNotIn("sk-", blob)
        self.assertNotIn("Bearer ", blob)

    def test_07_gateway_stays_off(self):
        clean = {k: v for k, v in os.environ.items() if not k.startswith("HOLOAEON_")}
        self.assertEqual(build_gateway(ROOT, environ=clean).state()["enabled"], [])

    def test_08_plan_and_probe_share_protocol(self):
        clean = {k: v for k, v in os.environ.items() if not k.startswith("HOLOAEON_")}
        plan = build_gateway(ROOT, environ=clean).plan("lmstudio", model="m", prompt="p")
        self.assertIn("model", plan["body"])
        self.assertIn("messages", plan["body"])
        host = plan["url"].split("//")[1].split(":")[0]
        self.assertIn(host, probe.LOOPBACK)


if __name__ == "__main__":
    unittest.main()
