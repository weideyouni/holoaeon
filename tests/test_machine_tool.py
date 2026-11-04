# -*- coding: utf-8 -*-
"""V25 工程机床测试。零依赖、确定性断言。

投喂包给 11 例；本批增 2 例实证断言（流水线 8 段顺序固定、基线探针读真实仓库），
共 13 例 —— 机床的价值在"真读到"，只测结构会漏掉这类回归。
"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holoaeon.machine_tool import (  # noqa: E402
    GATES,
    PIPELINE,
    RED_LINES,
    SEAL,
    BaselineProbe,
    Envelope,
    ExecutorHandoff,
    FeedPackageBuilder,
    FiveSiteLedger,
    MachineTool,
    MemoryBackfill,
    QuartetSession,
)

TEST_HEAD = "testhead0000"


class TestMachineToolStructure(unittest.TestCase):
    def test_red_lines_count(self):
        self.assertEqual(len(RED_LINES), 10)

    def test_seal(self):
        self.assertEqual(SEAL, "潮起开门，潮落闭嘴")

    def test_envelope_roundtrip(self):
        env = Envelope("V25", "S1", {"k": 1})
        data = env.to_dict()
        self.assertEqual(data["batch"], "V25")
        self.assertEqual(data["stage"], "S1")
        self.assertEqual(data["payload"], {"k": 1})
        self.assertEqual(data["seal"], SEAL)

    def test_pipeline_stages_fixed(self):
        """8 段顺序固定：S1…S8 且段名不乱序（跳段=纪律失守）。"""
        self.assertEqual(len(PIPELINE), 8)
        codes = [row[0] for row in PIPELINE]
        self.assertEqual(codes, ["S%d" % i for i in range(1, 9)])
        self.assertEqual(PIPELINE[0][1], "baseline")
        self.assertEqual(PIPELINE[-1][1], "memory_backfill")

    def test_gates_registered(self):
        for name in ("selftest", "v3_gate", "redline", "dimension_lock", "bench_diff0"):
            self.assertIn(name, GATES)


class TestQuartet(unittest.TestCase):
    def test_emergence_pass(self):
        result = QuartetSession.emergence_check(0.85, 0.85, 0.85, 0.30, 0.5237)
        self.assertTrue(result["emergence"])
        self.assertEqual(result["P2xP3"], 0.7225)

    def test_emergence_fail(self):
        result = QuartetSession.emergence_check(0.5, 0.5, 0.5, 0.5, 0.2)
        self.assertFalse(result["emergence"])

    def test_five_step_order(self):
        steps = QuartetSession.five_step()
        self.assertEqual(len(steps), 5)
        self.assertEqual(steps[0], "道(P4定义问题)")
        self.assertEqual(steps[-1], "升维(P1验证)")


class TestFeedAndLedger(unittest.TestCase):
    def test_feed_builder_complete(self):
        built = FeedPackageBuilder().build("V25", "工程机床", "diff0 不漂移", "全闸门全绿")
        self.assertTrue(built["complete"])
        self.assertIn(SEAL, built["body"])

    def test_five_site_consistent(self):
        ledger = FiveSiteLedger()
        for site in ledger.SITES:
            ledger.report(site, TEST_HEAD if site != "S4_vector_sea" else "195/195")
        self.assertTrue(ledger.consistent())

    def test_five_site_inconsistent(self):
        ledger = FiveSiteLedger()
        for site in ledger.SITES:
            ledger.report(site, TEST_HEAD if site != "S4_vector_sea" else "195/195")
        ledger.report("S3_github", TEST_HEAD + "9", mismatch=["x"])
        self.assertFalse(ledger.consistent())


class TestWriteBoundary(unittest.TestCase):
    def test_memory_backfill_append_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "MEMORY.md")
            backfill = MemoryBackfill(path)
            backfill.append("line1")
            backfill.append("line2")
            with open(path, "r", encoding="utf-8") as handle:
                content = handle.read()
            self.assertIn("line1", content)
            self.assertIn("line2", content)
            self.assertLess(content.index("line1"), content.index("line2"))

    def test_handoff_rejects_missing(self):
        handoff = ExecutorHandoff()
        result = handoff.register("V99", os.path.join("Z:", "no", "such", "feed.md"))
        self.assertFalse(result["ok"])

    def test_probe_reads_live_repo(self):
        """真探针：能读到 HEAD 与 VERSION（读不到说明探针静默失效）。"""
        repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        probe = BaselineProbe(repo).probe()
        self.assertIsNotNone(probe["head"])
        self.assertEqual(len(probe["head_short"]), 7)
        self.assertTrue(str(probe["version"]).startswith("0.9"))
        self.assertGreaterEqual(probe["extra_packs"], 9)


class TestAssembly(unittest.TestCase):
    def test_status_shape(self):
        repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        status = MachineTool(repo).status()
        self.assertEqual(status["red_line_count"], 10)
        self.assertEqual(status["pipeline_stages"], 8)
        self.assertIn("selftest", status["gate_names"])


if __name__ == "__main__":
    unittest.main()
