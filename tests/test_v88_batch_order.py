# -*- coding: utf-8 -*-
"""V88 P2-A：batch_order_monotonic 面金丝雀。

判据：双份 README 首条最新批次行 V 号 == 最新回执 batch（N2 状态节点传入，闸不起 git 子进程）。
金丝雀：README 最新批次改成错误 V 号 → 必红；现场真实文件 → 绿。
"""
import unittest

from holoaeon import claims_gate as G


class TestV88BatchOrder(unittest.TestCase):
    def test_wrong_token_red(self):
        # V0 为活靶：expected 由 spec.py::DOC_VERSION 第三段派生（V99 批起派生值即 V99），
        # 故伪造 token 须取永不等于派生批次的 V0，不能写死旧批次号。
        ctx = G._ctx(texts={
            "readme_zh": "| 最新批次 | **V0 伪批次（错误号）** |\n",
            "readme_en": "| Latest batch | **V0 fake batch (wrong)** |\n",
        })
        fails = G.batch_order_monotonic(ctx)
        ids = [f["id"] for f in fails]
        self.assertIn("readme_zh", ids)
        self.assertIn("readme_en", ids)

    def test_real_files_green(self):
        fails = G.batch_order_monotonic(G._ctx())
        self.assertEqual(fails, [])

    def test_token_regex(self):
        self.assertEqual(
            G._latest_batch_token("| 最新批次 | **V87-A.1 子号** |", "最新批次"),
            "V87-A.1")
        self.assertIsNone(
            G._latest_batch_token("| Previous batch | **V86** |", "最新批次"))

    def test_depth_green_real(self):
        ctx = G._ctx()
        self.assertTrue(G.READBACKS["readme.ledger_depth_ok"](ctx))

    def test_depth_red_on_overflow(self):
        four = "\n".join(["| 最新批次 | **V85** |"] * 4)
        self.assertGreater(
            G._ledger_depth(four, ["最新批次", "上一批次"]), 3)


if __name__ == "__main__":
    unittest.main()
