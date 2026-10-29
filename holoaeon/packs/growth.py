# -*- coding: utf-8 -*-
"""领域包：个人成长（growth）。目标、习惯、复盘、时间/精力。"""
from __future__ import annotations

import re

from .base import DomainPack, RoleSpec, SkillSpec, WorkflowSpec


def goal_smart(text: str) -> dict:
    """SMART 目标检查：具体/可衡量/可达成/相关/有时限。"""
    checks = {
        "specific": len(text) > 10,
        "measurable": bool(re.search(r"\d|%|次|个|篇", text)),
        "achievable": True,
        "relevant": True,
        "time_bound": bool(re.search(r"天|周|月|年|before|by|day|week", text.lower())),
    }
    return {"goal": text, "checks": checks,
            "score": sum(checks.values()),
            "is_smart": all(
                [checks["specific"], checks["measurable"],
                 checks["time_bound"]])}


def habit_plan(task: str) -> dict:
    """习惯养成计划：锚点 + 最小行动 + 追踪。"""
    return {"habit": task, "plan": {
        "anchor": "在【现有习惯】之后",
        "minimum_action": "2 分钟版本（先开始）",
        "track": "连续打卡 + 断签补一次",
        "environment": "降低阻力（备好工具）",
    }}


def task_breakdown(task: str) -> dict:
    """把目标拆为最小可执行步骤（确定性模板）。"""
    return {"goal": task, "steps": [
        "1. 明确交付物/完成标准",
        "2. 拆出第一块可在 2 小时内完成的行动",
        "3. 列出依赖与所需资源",
        "4. 排进日程（具体时间）",
        "5. 完成后检查并迭代",
    ]}


def weekly_review(text: str) -> dict:
    """周复盘模板。"""
    return {"input": text, "review": [
        "本周完成了什么",
        "什么做得好/什么没做好",
        "数据/指标如何",
        "学到什么",
        "下周 3 件要事",
    ]}


def energy_mapping(text: str) -> dict:
    """按高/中/低精力时段映射任务（每行：时段<TAB>等级）。"""
    high, low = [], []
    for line in text.splitlines():
        parts = line.split("\t")
        if len(parts) == 2:
            (high if parts[1].strip() in ("高", "high") else low).append(parts[0])
    return {"high_energy_slots": high, "low_energy_slots": low,
            "advice": "高精力做深度工作，低精力做常规事务"}


class GrowthPack(DomainPack):
    key = "growth"
    name = "个人成长"
    description = "目标、习惯、复盘、时间与精力管理。"
    skills = [
        SkillSpec("goal_smart", goal_smart, "SMART 目标检查",
                  ["goal", "smart"], {"text": "str"}),
        SkillSpec("habit_plan", habit_plan, "习惯养成计划",
                  ["habit"], {"task": "str"}),
        SkillSpec("task_breakdown", task_breakdown, "任务拆解",
                  ["breakdown", "plan"], {"task": "str"}),
        SkillSpec("weekly_review", weekly_review, "周复盘",
                  ["review", "reflection"], {"text": "str"}),
        SkillSpec("energy_mapping", energy_mapping, "精力映射",
                  ["energy", "time"], {"text": "str"}),
    ]
    roles = [
        RoleSpec("growth_goal_coach", "目标与拆解",
                 ["goal_smart", "task_breakdown"]),
        RoleSpec("growth_habit_coach", "习惯养成",
                 ["habit_plan", "energy_mapping"]),
        RoleSpec("growth_review_coach", "复盘",
                 ["weekly_review", "energy_mapping"]),
    ]
    workflows = [
        WorkflowSpec("growth_loop",
                     ["growth_goal_coach", "growth_habit_coach",
                      "growth_review_coach"],
                     "目标→习惯→复盘"),
    ]
