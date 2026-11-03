# -*- coding: utf-8 -*-
"""V22+ 千问评估补丁：中文分词修复验证（PR-3）。

投喂包：AGENT_FEED_V22_QIANWEN_EVALUATION_PATCH_20261104.md（批次编号 V22→V22+ 裁决）。
断言口径按真实登记表 data/v6_skill_family_registry.json 实测校准：
  - _split 中文 bigram 化（P0-1 修复的直接证据）；
  - match 中文长句可路由（不再中文全盲）；
  - 大小写归一化一致（P0-2 已修，回归保护）；
  - 确定性（同输入同输出）。
"""
import unittest

from holoaeon.fusion_upgrade.external_skill_registry import _split, match


class TestChineseSplit(unittest.TestCase):
    def test_cjk_bigram(self):
        """CJK 连续段按 bigram 切。"""
        result = _split("视频张量")
        self.assertIn("视频", result)
        self.assertIn("张量", result)

    def test_long_chinese_sentence(self):
        """千问报告 P0-1 实测用例：长中文句不再塌单 token。"""
        result = _split("把视频逐字稿转成张量")
        self.assertGreater(len(result), 1, "长中文句不应塌成单 token")
        self.assertTrue(any("视频" in t for t in result),
                        "bigram 覆盖相邻字符对，'视频' 必须在 token 内")

    def test_mixed_cn_en(self):
        """中英混合分词：英文段按空白切，中文段走 bigram，互不污染。
        （_split 只分词不归一化，大小写由 match 的 text.lower() 处理，
        回归保护见 test_match_case_insensitive。）"""
        result = _split("Gitee GitHub 三地同步")
        self.assertIn("Gitee", result)
        self.assertIn("GitHub", result)
        self.assertTrue(any("三地" in t or "地同" in t for t in result),
                        "中文段应切出 bigram（三地/地同）")

    def test_match_chinese_route(self):
        """千问报告实测场景：中文长句 match 不再全盲（修复前几乎全塌单 token）。"""
        result = match("数据经络皮肤细胞骨架", k=3)
        self.assertGreater(len(result), 0, "含族关键词的中文任务应能命中族")
        self.assertIn("F08", [c["family"] for c in result],
                      "经络族 F08 应在候选（keywords 数据+经络 命中）")

    def test_match_case_insensitive(self):
        """大小写归一化（P0-2 回归保护）：DATA/data 应命中相同族。"""
        r1 = match("DATA 经络", k=3)
        r2 = match("data 经络", k=3)
        self.assertGreater(len(r1), 0)
        self.assertEqual([c["family"] for c in r1], [c["family"] for c in r2])

    def test_determinism(self):
        """确定性：同输入同输出（无随机源）。"""
        r1 = match("数据经络皮肤", k=3)
        r2 = match("数据经络皮肤", k=3)
        self.assertEqual(r1, r2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
