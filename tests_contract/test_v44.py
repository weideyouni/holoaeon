# -*- coding: utf-8 -*-
"""V4.4-B1 旁挂单测：真实模型桥接（离线拼请求，不发网络）。"""
import ast
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from holoaeon.fusion_upgrade import model_gateway as mg  # noqa: E402
from holoaeon.model_adapter import ModelAdapter  # noqa: E402

CLEAN = {k: v for k, v in os.environ.items() if not k.startswith("HOLOAEON_")}


def gw(**env):
    e = dict(CLEAN)
    e.update(env)
    return mg.build_gateway(ROOT, environ=e)


class TestV44Catalog(unittest.TestCase):
    def test_01_catalog_loads(self):
        c = mg.load_catalog(ROOT)
        self.assertEqual(c["id"], "SG-V44-MODEL-PROVIDER-CATALOG-V1")
        self.assertGreaterEqual(len(c["providers"]), 12)
        self.assertEqual(len(c["protocols"]), 5)

    def test_02_every_provider_no_secret(self):
        c = mg.load_catalog(ROOT)
        for p in c["providers"]:
            for k in ("id", "label", "api_style", "base_url_env", "key_env"):
                self.assertTrue(p.get(k), "%s 缺 %s" % (p.get("id"), k))
            self.assertNotIn("sk-", p["key_env"])

    def test_03_default_off(self):
        g = gw()
        st = g.state()
        self.assertEqual(st["enabled"], [])
        self.assertTrue(st["default_off"])
        self.assertEqual(g.attach(ModelAdapter()), [])

    def test_04_switch_and_key_enable(self):
        g = gw(HOLOAEON_REAL_MODELS="1", HOLOAEON_DEEPSEEK_API_KEY="x")
        self.assertIn("deepseek", g.enabled())
        a = ModelAdapter()
        added = g.attach(a)
        self.assertIn("gw:deepseek", added)
        self.assertIn("gw:deepseek", a.names())

    def test_05_local_runtime_no_key(self):
        g = gw(HOLOAEON_REAL_MODELS="1")
        self.assertIn("ollama", g.enabled())
        self.assertIn("vllm", g.enabled())


class TestV44Shapes(unittest.TestCase):
    def test_06_five_protocol_shapes(self):
        shapes = gw().sample_plans("ping")
        self.assertEqual(set(shapes), set(mg.PROTOCOL_SHAPES))
        self.assertIn("messages", shapes["openai_chat"]["body"])
        self.assertIn("max_tokens", shapes["anthropic_messages"]["body"])
        self.assertIn("contents", shapes["google_gemini"]["body"])
        self.assertIn("inferenceConfig", shapes["bedrock_converse"]["body"])
        self.assertIn("api-version", shapes["azure_openai"]["url"])

    def test_07_placeholder_only_when_unconfigured(self):
        plan = gw().plan("openai", prompt="ping")
        self.assertFalse(plan["configured"])
        self.assertFalse(plan["enabled"])
        auth = plan["headers"]["Authorization"]
        self.assertIn("HOLOAEON_OPENAI_API_KEY", auth)
        self.assertLessEqual(len(auth), 120)
        self.assertFalse(plan["network"])

    def test_08_no_network_imports(self):
        path = os.path.join(ROOT, "holoaeon", "fusion_upgrade", "model_gateway.py")
        with open(path, encoding="utf-8") as f:
            tree = ast.parse(f.read())
        banned = {"subprocess", "urllib", "requests", "socket", "http", "aiohttp", "httpx"}
        seen = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                seen.update(a.name.split(".")[0] for a in node.names)
            if isinstance(node, ast.ImportFrom) and node.module:
                seen.add(node.module.split(".")[0])
        self.assertEqual(seen & banned, set())

    def test_09_unknown_provider_raises(self):
        with self.assertRaises(KeyError):
            gw().plan("no-such-provider", prompt="ping")


if __name__ == "__main__":
    unittest.main()
