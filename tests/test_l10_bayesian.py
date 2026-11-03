# -*- coding: utf-8 -*-
"""L10 贝叶斯层端到端集成测试（V11 补丁 PR-3）。

运行：
    python -m unittest discover -s tests -v
"""
from __future__ import annotations

import unittest

from holoaeon.envelope import Envelope
from holoaeon.guard import (
    ALLOW,
    BLOCK,
    BUILTIN_LAYERS,
    Guard,
    GuardConfig,
    Verdict,
    _L10_LIKELIHOOD,
    l10_bayesian,
)


def _posterior(feature: str, prior: float) -> float:
    ll = _L10_LIKELIHOOD.get(feature, _L10_LIKELIHOOD["safe"])
    p_block = max(0.0, min(1.0, prior))
    p_allow = 1.0 - p_block
    denom = ll["block"] * p_block + ll["allow"] * p_allow
    return (ll["block"] * p_block) / denom if denom > 0 else p_block


class TestL10BayesianDirect(unittest.TestCase):
    """l10_bayesian 纯函数语义（似然表 + 贝叶斯后验）。"""

    def test_no_feature_returns_none(self):
        env = Envelope.create("a", "b", "t", {"task": "x"})
        self.assertIsNone(l10_bayesian(env))

    def test_delete_prior_015_blocks(self):
        env = Envelope.create("a", "b", "t", {"task": "x"})
        env.metadata["bayes_feature"] = "delete"
        env.metadata["bayes_prior"] = 0.15
        v = l10_bayesian(env)
        self.assertIsNotNone(v)
        self.assertEqual(v.action, BLOCK)
        self.assertEqual(v.layer, "L10")
        self.assertAlmostEqual(_posterior("delete", 0.15), 0.75, places=4)

    def test_network_prior_015_blocks(self):
        env = Envelope.create("a", "b", "t", {"task": "x"})
        env.metadata["bayes_feature"] = "network"
        env.metadata["bayes_prior"] = 0.15
        v = l10_bayesian(env)
        self.assertEqual(v.action, BLOCK)
        self.assertAlmostEqual(_posterior("network", 0.15), 0.61363636, places=4)

    def test_write_prior_015_allows(self):
        env = Envelope.create("a", "b", "t", {"task": "x"})
        env.metadata["bayes_feature"] = "write"
        env.metadata["bayes_prior"] = 0.15
        v = l10_bayesian(env)
        self.assertIsNone(v)  # 后验 0.3818 < 0.5 → 放行
        self.assertAlmostEqual(_posterior("write", 0.15), 0.38181818, places=4)

    def test_write_high_prior_blocks(self):
        env = Envelope.create("a", "b", "t", {"task": "x"})
        env.metadata["bayes_feature"] = "write"
        env.metadata["bayes_prior"] = 0.9
        v = l10_bayesian(env)
        self.assertEqual(v.action, BLOCK)

    def test_unknown_feature_falls_back_to_safe(self):
        env = Envelope.create("a", "b", "t", {"task": "x"})
        env.metadata["bayes_feature"] = "bizarre_unknown"
        env.metadata["bayes_prior"] = 0.15
        self.assertIsNone(l10_bayesian(env))

    def test_invalid_prior_falls_back_to_015(self):
        env = Envelope.create("a", "b", "t", {"task": "x"})
        env.metadata["bayes_feature"] = "delete"
        env.metadata["bayes_prior"] = "not-a-number"
        v = l10_bayesian(env)
        self.assertEqual(v.action, BLOCK)
        self.assertAlmostEqual(_posterior("delete", 0.15), 0.75, places=4)


class TestL10GuardMount(unittest.TestCase):
    """Guard 挂载语义：默认关不影响既有行为，开启后 L10 生效。"""

    def test_default_off_not_mounted(self):
        g = Guard()
        names = [n for n, _ in g.layers]
        self.assertNotIn("L10", names)
        self.assertEqual(len(BUILTIN_LAYERS), 8)

    def test_default_off_does_not_block_feature_envelope(self):
        g = Guard()
        env = Envelope.create("a", "b", "t", {"task": "x"})
        env.metadata["bayes_feature"] = "delete"
        env.metadata["bayes_prior"] = 0.15
        v = g.inspect(env)
        self.assertEqual(v.action, ALLOW)  # 未挂载 → 既有行为不变

    def test_on_mounted_and_blocks(self):
        g = Guard(GuardConfig(bayesian_guard=True))
        names = [n for n, _ in g.layers]
        self.assertIn("L10", names)
        env = Envelope.create("a", "b", "t", {"task": "x"})
        env.metadata["bayes_feature"] = "delete"
        env.metadata["bayes_prior"] = 0.15
        v = g.inspect(env)
        self.assertEqual(v.action, BLOCK)
        self.assertEqual(v.layer, "L10")
        self.assertTrue(env.metadata.get("bayesian_guard"))

    def test_on_without_feature_still_allows(self):
        g = Guard(GuardConfig(bayesian_guard=True))
        env = Envelope.create("a", "b", "t", {"task": "x"})
        v = g.inspect(env)
        self.assertEqual(v.action, ALLOW)

    def test_off_does_not_inject_metadata(self):
        g = Guard()
        env = Envelope.create("a", "b", "t", {"task": "x"})
        g.inspect(env)
        self.assertNotIn("bayesian_guard", env.metadata)

    def test_l10_after_l9_order(self):
        g = Guard(GuardConfig(bayesian_guard=True))
        names = [n for n, _ in g.layers]
        self.assertEqual(names[-2:], ["L9", "L10"])  # 附加层顺序：L9 产品层、L10 贝叶斯


if __name__ == "__main__":
    unittest.main()
