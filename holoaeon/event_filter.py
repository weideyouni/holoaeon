# -*- coding: utf-8 -*-
"""
event_filter —— 两级过滤事件驱动（Super-agent D-02 蒸馏）
================================================================================
借鉴 DeepSeek Super-agent 的两级过滤机制，
在 HoloAeon 的 Bus(C2) 之上增加事件预过滤层。

核心差异（第一性原理适配）：
  DeepSeek 两级过滤：LLM 驱动，语义分析过滤
  HoloAeon 两级过滤：规则驱动，确定性过滤（同事件→同过滤结果）

两级过滤：
  第一级（L1 Fast）：快速预过滤——关键词/模式匹配，拦截明显无关事件
  第二级（L2 Deep）：深度检查——规则链验证，确认事件需要处理

纯标准库、确定性、零依赖。
"""
from __future__ import annotations

import sys
import re
from typing import Any, Dict, List, Optional, Tuple


class EventFilter:
    """两级过滤事件驱动：规则驱动的确定性过滤。

    借鉴 Super-agent 两级过滤，适配 HoloAeon 确定性原则。
    """

    # 第一级：快速预过滤关键词（命中即放行到第二级）
    FAST_PATTERNS: List[str] = [
        "错误", "异常", "失败", "崩溃", "bug", "error", "fail",
        "修复", "fix", "问题", "issue", "缺陷", "defect",
        "审查", "review", "检查", "check", "验证", "verify",
    ]

    # 第二级：深度检查规则（确认事件需要处理）
    DEEP_RULES: List[dict] = [
        {"name": "contains_error", "check": lambda t: "error" in t.lower() or "错误" in t},
        {"name": "contains_fail", "check": lambda t: "fail" in t.lower() or "失败" in t},
        {"name": "contains_fix", "check": lambda t: "fix" in t.lower() or "修复" in t},
        {"name": "contains_review", "check": lambda t: "review" in t.lower() or "审查" in t},
    ]

    def filter(self, event_text: str) -> dict:
        """两级过滤

        Returns:
            {"passed": True/False, "level": "L1"/"L2", "reason": "..."}
        """
        event_text = str(event_text or "")
        # 第一级：快速预过滤
        text_lower = event_text.lower()
        fast_hit = any(p in text_lower for p in self.FAST_PATTERNS)
        if not fast_hit:
            return {"passed": False, "level": "L1",
                    "reason": "fast_filter_no_match"}

        # 第二级：深度检查
        deep_hits = [r["name"] for r in self.DEEP_RULES
                     if r["check"](event_text)]
        if deep_hits:
            return {"passed": True, "level": "L2",
                    "reason": "deep_match:" + ",".join(deep_hits)}

        return {"passed": False, "level": "L2",
                "reason": "deep_filter_no_match"}

    def batch_filter(self, events: List[str]) -> List[dict]:
        """批量过滤（确定性）"""
        return [self.filter(e) for e in events]


def main(argv: Optional[List[str]] = None) -> int:
    """CLI 入口（演示 + 自检）：两级过滤确定性判定。"""
    args = list(sys.argv[1:] if argv is None else argv)
    print("== HoloAeon 两级过滤事件驱动（super_agent D-02 蒸馏）==")
    f = EventFilter()
    if args and args[0].strip() == "--selfcheck":
        r1 = f.filter("代码审查发现一个bug")
        r2 = f.filter("例行周会纪要")
        r3 = f.filter("修复了内存泄漏问题")
        ok = (r1["passed"] is True and r1["level"] == "L2"
              and r2["passed"] is False and r2["level"] == "L1"
              and r3["passed"] is True and r3["level"] == "L2")
        print("自检:", "PASS" if ok else "FAIL",
              "bug=%s:%s 无关=%s 修复=%s:%s"
              % (r1["passed"], r1["level"], r2["level"],
                 r3["passed"], r3["level"]))
        return 0 if ok else 1
    print("示例: filter('代码审查发现一个bug') -> %s" % f.filter("代码审查发现一个bug"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
