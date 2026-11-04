# -*- coding: utf-8 -*-
"""v3 单测：router_layer 中文路由（V23-H，补千问 P2-8）。

验证 RouterLayer 对中文任务描述的路由能力（按实际 API 适配）：
- 连续子串匹配（降级链第一级）
- 逐字符按序匹配（降级链第二级）
- 无匹配时广播兜底（返回 "*"）
- 中英混合任务路由

放在独立目录 tests/v3，保持 tests/ 顶层计数独立。evidence_class=simulated。
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from holoaeon.router_layer import RouterLayer  # noqa: E402


class TestRouterChinese(unittest.TestCase):
    """中文路由测试（真实 API：register_rule(pattern, target) / receive(task)->str）。"""

    def test_chinese_exact_match(self):
        """中文技能关键词连续命中。"""
        r = RouterLayer()
        r.register_rule("小说", "writer")
        self.assertEqual(r.receive("帮我写一篇小说"), "writer")

    def test_chinese_substring_match(self):
        """中文连续子串匹配（pattern 是 task 的一段）。"""
        r = RouterLayer()
        r.register_rule("数据分析", "analyst")
        self.assertEqual(r.receive("我需要数据分析服务"), "analyst")

    def test_chinese_char_order_match(self):
        """中文逐字符按序匹配（降级链第二级，允许词间插入）。"""
        r = RouterLayer()
        r.register_rule("科研综述", "researcher")
        # "科研综述" 不连续出现，但 科→研→综→述 按序出现
        self.assertEqual(r.receive("开展科研与综述工作"), "researcher")

    def test_chinese_no_match_broadcast(self):
        """无规则命中时广播兜底（返回 '*'）。"""
        r = RouterLayer()
        r.register_rule("小说", "writer")
        self.assertEqual(r.receive("翻译成英文"), "*")

    def test_mixed_cn_en_routing(self):
        """中英混合任务路由（英文 pattern 经 lower 命中）。"""
        r = RouterLayer()
        r.register_rule("data", "analyst")
        self.assertEqual(r.receive("写一份 data 分析报告"), "analyst")

    def test_routing_deterministic(self):
        """同输入 → 同分派结果（确定性）。"""
        r = RouterLayer()
        r.register_rule("写作", "writer")
        first = r.receive("帮我写作")
        second = r.receive("帮我写作")
        self.assertEqual(first, "writer")
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
