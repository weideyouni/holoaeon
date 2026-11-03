# -*- coding: utf-8 -*-
"""
router_layer —— Router 持续运行层（Super-agent D-01 蒸馏）
================================================================================
借鉴 DeepSeek Super-agent 的 Router-Worker 双层设计，
在 HoloAeon 的 Scheduler(C6) tick 之上增加一个持续运行的 Router 层。

核心差异（第一性原理适配）：
  DeepSeek Router：LLM 驱动，自主决策任务分派
  HoloAeon Router：规则驱动，确定性分派（同输入→同分派结果）

职责：
  · 持续接收任务输入（Envelope 信封）
  · 规则驱动分派到合适的 Agent（不依赖 LLM）
  · 维护共享上下文（Shared State）
  · 聚合 Worker 结果

纯标准库、确定性、零依赖。
不碰 Scheduler(C6)/Kernel(C8)/graph.py。
"""
from __future__ import annotations

import sys
import time
from collections import deque
from typing import Any, Callable, Deque, Dict, List, Optional


class RouterLayer:
    """Router 持续运行层：规则驱动的任务分派协调器。

    借鉴 Super-agent Router 概念，适配 HoloAeon 确定性原则。
    """

    def __init__(self) -> None:
        self.task_queue: Deque[dict] = deque()       # 任务队列（持续运行）
        self.shared_context: Dict[str, Any] = {}      # 共享上下文
        self.dispatch_rules: List[dict] = []          # 分派规则（确定性）
        self.worker_results: Dict[str, Any] = {}      # Worker 结果聚合
        self.is_running: bool = False
        self.started_at: Optional[str] = None

    # ------------------------------------------------------------------ 规则
    def register_rule(self, pattern: str, target_agent: str,
                      priority: int = 0) -> None:
        """注册确定性分派规则（非 LLM）

        Args:
            pattern: 任务关键词模式（如 "写文章"→writing_planner）
            target_agent: 目标 Agent 名
            priority: 优先级（数字越大越优先）
        """
        self.dispatch_rules.append({
            "pattern": str(pattern),
            "target": str(target_agent),
            "priority": int(priority),
        })
        # 按优先级排序（确定性）
        self.dispatch_rules.sort(key=lambda r: r["priority"], reverse=True)

    # ------------------------------------------------------------------ 运行
    def start(self) -> None:
        """启动持续运行层（记录运行态，规则驱动无自旋占用）。"""
        self.is_running = True
        self.started_at = time.strftime("%Y-%m-%dT%H:%M:%S")

    def stop(self) -> None:
        """停止运行层。"""
        self.is_running = False

    # ------------------------------------------------------------------ 分派
    def receive(self, task: str, metadata: Optional[dict] = None) -> str:
        """接收任务（持续运行入口）

        Returns:
            分派到的 Agent 名（确定性，同输入→同输出）
        """
        self.task_queue.append({"task": str(task),
                                "metadata": dict(metadata or {})})
        return self._dispatch(str(task))

    def _dispatch(self, task: str) -> str:
        """规则驱动分派（确定性，不用 LLM）

        借鉴 Super-agent Router 的任务分派，
        但用关键词规则匹配代替 LLM 推理。
        匹配降级链（确定性）：连续子串命中 → 有序字符匹配（允许间隔词）。
        """
        task_lower = task.lower()
        for rule in self.dispatch_rules:
            if self._match_rule(rule["pattern"], task_lower):
                return rule["target"]
        return "*"  # 默认广播给所有 Agent

    @staticmethod
    def _match_rule(pattern: str, task_lower: str) -> bool:
        """确定性规则匹配：先试连续子串，再试有序字符（同输入→同结果）。"""
        pat = pattern.lower()
        if pat in task_lower:
            return True
        # 有序字符匹配：pattern 的每个字符按顺序出现在 task 中
        it = iter(task_lower)
        return all(ch in it for ch in pat)

    # ------------------------------------------------------------------ 聚合
    def aggregate(self, worker_name: str, result: Any) -> None:
        """聚合 Worker 结果（Super-agent Router 的聚合职责）"""
        self.worker_results[str(worker_name)] = result

    # ------------------------------------------------------------------ 上下文
    def get_shared_context(self, key: Optional[str] = None) -> Any:
        """获取共享上下文（Super-agent Router 的共享上下文维护）"""
        if key is not None:
            return self.shared_context.get(key)
        return self.shared_context

    def update_shared_context(self, key: str, value: Any) -> None:
        """更新共享上下文"""
        self.shared_context[str(key)] = value

    # ------------------------------------------------------------------ 状态
    def status(self) -> dict:
        """Router 状态快照"""
        return {
            "queue_size": len(self.task_queue),
            "rules_count": len(self.dispatch_rules),
            "workers_reporting": len(self.worker_results),
            "is_running": self.is_running,
            "started_at": self.started_at,
            "shared_context_keys": list(self.shared_context.keys()),
        }


def main(argv: Optional[List[str]] = None) -> int:
    """CLI 入口（演示 + 自检）：规则注册 → 确定性分派 → 状态快照。"""
    args = list(sys.argv[1:] if argv is None else argv)
    print("== HoloAeon Router 持续运行层（super_agent D-01 蒸馏）==")
    r = RouterLayer()
    r.register_rule("写文章", "writing_planner")
    r.register_rule("分析数据", "data_analyst")
    r.register_rule("监控", "watchdog_operator", priority=1)
    r.start()
    if args and args[0].strip() == "--selfcheck":
        t1 = r.receive("帮我写一篇文章")
        t2 = r.receive("分析这份销售数据")
        t3 = r.receive("系统监控告警")
        t4 = r.receive("无关闲聊")
        ok = (t1 == "writing_planner" and t2 == "data_analyst"
              and t3 == "watchdog_operator" and t4 == "*"
              and r.status()["rules_count"] == 3
              and r.status()["is_running"] is True)
        print("自检:", "PASS" if ok else "FAIL",
              "dispatch=[%s,%s,%s,%s] queue=%d"
              % (t1, t2, t3, t4, r.status()["queue_size"]))
        return 0 if ok else 1
    print("示例分派: receive('帮我写一篇文章') -> %s" % r.receive("帮我写一篇文章"))
    print("状态: %s" % r.status())
    return 0


if __name__ == "__main__":
    sys.exit(main())
