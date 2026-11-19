# -*- coding: utf-8 -*-
"""V88 P1-B：tautology_scan 第五类 activity_probe 金丝雀与结构断言。

委托源（跨仓零 import）：longaeon-rejuvenation-matrix @ ea4e2c1
longaeon/models/_guard.py L99-L108 activity_check（扰动测活性思路）。

金丝雀口径：
  · 旧病害模型（忽略入参、常数输出的二态布尔）→ activity_suspect 必标；
  · 修后模型（入参驱动输出、三态思路）→ 不标；
  · 抛错/超时 → unverifiable（suspect=None），不冒充命中；
  · 默认关闭（纯静态零执行），--with-activity 才开探针；固定种子 + 超时熔断。
"""
import unittest

from holoaeon import tautology_scan as S


class TestV88ActivityProbe(unittest.TestCase):
    def test_default_off(self):
        rep = S.scan()
        ap = rep["activity_probe"]
        self.assertFalse(ap["enabled"])
        self.assertEqual(ap["suspects"], [])
        self.assertEqual(ap["probed"], 0)

    def test_constant_fn_suspect(self):
        def old(x):
            return True  # 忽略入参：常数输出（旧二态布尔病害模型）

        res = S.probe_callable(old, [0.5], [0.95])
        self.assertTrue(res["suspect"])
        self.assertEqual(res["reason"], "constant_output")

    def test_sensitive_fn_not_suspect(self):
        def new(x):
            return x > 0.5  # 入参驱动输出（修后三态思路的模型）

        res = S.probe_callable(new, [0.5], [0.95])
        self.assertFalse(res["suspect"])
        self.assertEqual(res["reason"], "output_changes")

    def test_error_unverifiable(self):
        def boom(x):
            raise ValueError("x")

        res = S.probe_callable(boom, [0.5], [0.95])
        self.assertIsNone(res["suspect"])
        self.assertIn("unverifiable", res["reason"])

    def test_enabled_scan_structure(self):
        rep = S.scan(with_activity=True)
        ap = rep["activity_probe"]
        self.assertTrue(ap["enabled"])
        self.assertGreaterEqual(ap["probed"], 0)
        self.assertIn("seed", ap)
        self.assertIn("timeout_s", ap)
        for s in ap["suspects"]:
            self.assertIn("file", s)
            self.assertIn("func", s)
            self.assertIn("reason", s)

    def test_seed_and_timeout_fixed(self):
        self.assertEqual(S.ACTIVITY_SEED, 20261119)
        self.assertGreater(S.ACTIVITY_TIMEOUT, 0)
        self.assertGreater(S.ACTIVITY_TOLERANCE, 0)

    def test_probe_result_is_pending_review_not_verdict(self):
        def old(x):
            return 1.0

        res = S.probe_callable(old, [0.5], [0.95])
        # suspect 是「待复核」标记，不是判定为病
        self.assertTrue(res["suspect"])


if __name__ == "__main__":
    unittest.main()
