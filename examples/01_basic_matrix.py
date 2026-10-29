# -*- coding: utf-8 -*-
"""示例 1：最小内核 —— 注册技能、创建 agent、提交任务。
运行：python examples/01_basic_matrix.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holoaeon.agent import Agent
from holoaeon.kernel import Kernel
from holoaeon.skill import SkillRegistry


def main() -> None:
    k = Kernel()

    # 1) 注册确定性技能
    k.skills.register_fn(
        "outline", lambda task: "outline:" + task,
        description="make an outline for a task", tags=["plan"])
    k.skills.register_fn(
        "summarize", lambda task: "summary:" + task,
        description="summarize the given text", tags=["summary"])

    # 2) 创建 agent 并加入内核
    k.register_agent(Agent("planner", "planner", k.skills,
                           skill_names=["outline", "summarize"]))

    # 3) 提交任务（自动选择 agent）
    rep = k.submit("please make an outline for the article")
    print("结果：", rep["results"][0]["output"])
    print("健康：", k.health())


if __name__ == "__main__":
    main()
