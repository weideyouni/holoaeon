# -*- coding: utf-8 -*-
"""topology_runtime 端到端集成测试（V11 补丁 PR-3）。

运行：
    python -m unittest discover -s tests -v
"""
from __future__ import annotations

import unittest

from holoaeon.topology_runtime import (
    Checkpoint,
    CircuitBreaker,
    DissipationMonitor,
    StateReducer,
)


class TestStateReducer(unittest.TestCase):
    def test_exponential_smoothing_alpha_05(self):
        r = StateReducer(alpha=0.5)
        r.apply("score", 1.0)
        out = r.apply("score", 2.0)
        self.assertAlmostEqual(r.get("score"), 1.5)  # 0.5*2 + 0.5*1
        self.assertEqual(out["revision"], 2)

    def test_alpha_clamped(self):
        r = StateReducer(alpha=3.0)
        self.assertEqual(r.alpha, 1.0)
        r2 = StateReducer(alpha=-1.0)
        self.assertEqual(r2.alpha, 0.0)

    def test_dict_merge(self):
        r = StateReducer()
        r.apply("g", {"a": 1})
        r.apply("g", {"b": 2})
        self.assertEqual(r.get("g"), {"a": 1, "b": 2})

    def test_replace_reducer(self):
        r = StateReducer()
        r.apply("k", 1.0)
        r.apply("k", 9.0, reducer="replace")
        self.assertEqual(r.get("k"), 9.0)

    def test_snapshot_restore(self):
        r = StateReducer()
        r.apply("k", 1.0)
        snap = r.snapshot()
        r.apply("k", 100.0)
        r.restore(snap)
        self.assertEqual(r.get("k"), 1.0)
        self.assertEqual(r.snapshot()["revision"], snap["revision"])


class TestCheckpoint(unittest.TestCase):
    def test_save_restore_latest(self):
        cp = Checkpoint()
        cp.save("s0", {"v": 1})
        cp.save("s1", {"v": 2})
        self.assertEqual(cp.count(), 2)
        self.assertEqual(cp.restore(), {"v": 2})

    def test_restore_by_seq(self):
        cp = Checkpoint()
        cp.save("s0", {"v": 1})
        cp.save("s1", {"v": 2})
        self.assertEqual(cp.restore(0), {"v": 1})
        self.assertIsNone(cp.restore(99))

    def test_empty_chain_returns_none(self):
        cp = Checkpoint()
        self.assertIsNone(cp.restore())

    def test_list_entries(self):
        cp = Checkpoint()
        cp.save("s0", {"v": 1})
        entries = cp.list()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["seq"], 0)
        self.assertEqual(entries[0]["label"], "s0")

    def test_restore_returns_copy(self):
        cp = Checkpoint()
        cp.save("s0", {"v": 1})
        got = cp.restore()
        got["v"] = 999
        self.assertEqual(cp.restore(), {"v": 1})


class TestCircuitBreaker(unittest.TestCase):
    def test_three_failures_opens(self):
        cb = CircuitBreaker(failure_threshold=3, reset_after=5)
        for _ in range(3):
            cb.record(False)
        self.assertEqual(cb.status()["state"], CircuitBreaker.OPEN)
        self.assertTrue(cb.is_open())

    def test_open_after_reset_goes_half_open(self):
        cb = CircuitBreaker(failure_threshold=3, reset_after=5)
        for _ in range(5):  # 第 5 次调用 %5==0 → HALF_OPEN 探测
            cb.record(False)
        self.assertEqual(cb.status()["state"], CircuitBreaker.HALF_OPEN)

    def test_half_open_success_closes(self):
        cb = CircuitBreaker(failure_threshold=3, reset_after=5)
        for _ in range(5):
            cb.record(False)
        self.assertEqual(cb.status()["state"], CircuitBreaker.HALF_OPEN)
        cb.record(True)
        self.assertEqual(cb.status()["state"], CircuitBreaker.CLOSED)

    def test_half_open_failure_reopens(self):
        cb = CircuitBreaker(failure_threshold=3, reset_after=5)
        for _ in range(5):
            cb.record(False)
        self.assertEqual(cb.status()["state"], CircuitBreaker.HALF_OPEN)
        cb.record(False)
        self.assertEqual(cb.status()["state"], CircuitBreaker.OPEN)

    def test_success_decays_failures(self):
        cb = CircuitBreaker(failure_threshold=3, reset_after=5)
        cb.record(False)
        cb.record(False)
        cb.record(True)
        cb.record(True)
        self.assertEqual(cb.status()["failures"], 0)
        self.assertEqual(cb.status()["state"], CircuitBreaker.CLOSED)

    def test_trace_logs(self):
        cb = CircuitBreaker()
        cb.record(True)
        self.assertEqual(len(cb.trace()), 1)
        self.assertTrue(cb.trace()[0]["ok"])


class TestDissipationMonitor(unittest.TestCase):
    def test_empty_metrics(self):
        m = DissipationMonitor()
        d = m.metrics()
        self.assertEqual(d["total"], 0)
        self.assertEqual(d["order"], 1.0)
        self.assertFalse(d["needs_reorganization"])

    def test_all_ok_zero_entropy(self):
        m = DissipationMonitor(window=10)
        for _ in range(4):
            m.record(True)
        d = m.metrics()
        self.assertEqual(d["success"], 4)
        self.assertEqual(d["shannon_entropy"], 0.0)
        self.assertEqual(d["order"], 1.0)

    def test_mixed_flow_triggers_reorganization(self):
        m = DissipationMonitor(window=4)
        for ok in (True, False, True, False):
            m.record(ok)
        d = m.metrics()
        self.assertEqual(d["shannon_entropy"], 1.0)  # 二元最大熵
        self.assertEqual(d["order"], 0.0)
        self.assertTrue(d["needs_reorganization"])

    def test_window_slides(self):
        m = DissipationMonitor(window=2)
        for ok in (True, False, True):
            m.record(ok)
        self.assertEqual(m.metrics()["total"], 2)  # 只保留最近 2 步

    def test_trend_and_trace(self):
        m = DissipationMonitor(window=4)
        m.record(True)
        m.record(False)
        self.assertEqual(len(m.trend()), 2)
        self.assertEqual(len(m.trace()), 2)
        self.assertGreater(m.trend()[1]["entropy"], 0.0)


if __name__ == "__main__":
    unittest.main()
