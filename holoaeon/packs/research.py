# -*- coding: utf-8 -*-
"""领域包：科研（research）。假设、实验设计、变量、样本量、复现。"""
from __future__ import annotations

import math
import re

from .base import DomainPack, RoleSpec, SkillSpec, WorkflowSpec


def hypothesis_check(text: str) -> dict:
    """可检验性检查：是否含变量关系、可测量、明确方向。"""
    meas = re.findall(r"\d+\s*%|增加|减少|提高|降低|相关|差异|effect|rate|score",
                      text.lower())
    return {"hypothesis": text,
            "has_measurable": bool(meas),
            "has_direction": any(w in text for w in ["增加", "减少", "提高", "降低",
                                                     "more", "less", "higher", "lower"]),
            "testable": bool(meas)}


def variables_split(text: str) -> dict:
    """拆分自变量/因变量/控制变量（基于标记，确定性）。"""
    iv = re.findall(r"自变量[:：]\s*([^；;。]+)", text)
    dv = re.findall(r"因变量[:：]\s*([^；;。]+)", text)
    cv = re.findall(r"控制变量[:：]\s*([^；;。]+)", text)
    return {"independent": iv, "dependent": dv, "controlled": cv}


def design_experiment(task: str) -> dict:
    """生成实验设计模板（对照/随机/盲法/指标）。"""
    return {"aim": task, "design": {
        "type": "随机对照（RCT）/ 准实验",
        "groups": ["处理组", "对照组（安慰剂/常规）"],
        "randomization": "随机分配 + 分配隐藏",
        "blinding": "单盲/双盲（如可行）",
        "primary_outcome": "主要指标（待填）",
        "secondary_outcome": "次要指标（待填）",
    }}


def sample_size(effect_size: float) -> dict:
    """简化样本量估算（每组，n≈16/d²，双组 α0.05/80%power 的经验近似）。
    仅用于规划，正式研究请用专业功效分析。"""
    d = float(effect_size)
    if d <= 0:
        return {"error": "effect_size 必须为正"}
    n_per_group = math.ceil(16 / (d * d))
    return {"effect_size": d, "n_per_group": n_per_group,
            "n_total": n_per_group * 2,
            "note": "经验近似，非正式功效分析"}


def reproduce_check(text: str) -> dict:
    """可复现性清单。"""
    items = ["数据可得", "代码可得", "随机种子", "参数/超参",
             "环境/版本", "分析流程", "材料方法"]
    hit = [it for it in items if it in text]
    return {"checklist": items, "present": hit,
            "missing": [it for it in items if it not in text]}


class ResearchPack(DomainPack):
    key = "research"
    name = "科研"
    description = "假设、实验设计、变量、样本量、复现与论文。"
    skills = [
        SkillSpec("hypothesis_check", hypothesis_check, "假设可检验性",
                  ["hypothesis"], {"text": "str"}),
        SkillSpec("variables_split", variables_split, "变量拆分",
                  ["variables"], {"text": "str"}),
        SkillSpec("design_experiment", design_experiment, "实验设计模板",
                  ["experiment", "design"], {"task": "str"}),
        SkillSpec("sample_size", sample_size, "样本量估算",
                  ["power", "sample"], {"effect_size": "float"}),
        SkillSpec("reproduce_check", reproduce_check, "可复现性清单",
                  ["reproduce"], {"text": "str"}),
    ]
    roles = [
        RoleSpec("research_designer", "假设与设计",
                 ["hypothesis_check", "variables_split",
                  "design_experiment", "sample_size"]),
        RoleSpec("research_executor", "执行实验",
                 ["design_experiment"]),
        RoleSpec("research_analyzer", "分析与复现",
                 ["reproduce_check", "variables_split"]),
    ]
    workflows = [
        WorkflowSpec("research_pipeline",
                     ["research_designer", "research_executor",
                      "research_analyzer"],
                     "设计→执行→分析"),
    ]
