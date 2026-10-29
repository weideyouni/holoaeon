# -*- coding: utf-8 -*-
"""领域包：企业运营（business）。商业模式、OKR、KPI、SWOT、风险。"""
from __future__ import annotations

import csv
import io

from .base import DomainPack, RoleSpec, SkillSpec, WorkflowSpec


def business_model_canvas(task: str) -> dict:
    """商业模式画布（9 模块）。"""
    return {"venture": task, "canvas": {
        "customer_segments": "客户细分",
        "value_propositions": "价值主张",
        "channels": "渠道",
        "customer_relationships": "客户关系",
        "revenue_streams": "收入来源",
        "key_resources": "关键资源",
        "key_activities": "关键活动",
        "key_partnerships": "关键合作",
        "cost_structure": "成本结构",
    }}


def okr_gen(task: str) -> dict:
    """OKR 模板（1 目标 + 3 关键结果）。"""
    return {"objective": task, "key_results": [
        "KR1（可量化，基线→目标）",
        "KR2（可量化）",
        "KR3（可量化）",
    ]}


def swot_analysis(task: str) -> dict:
    """SWOT 四象限模板。"""
    return {"subject": task, "swot": {
        "strengths": "优势（内部）",
        "weaknesses": "劣势（内部）",
        "opportunities": "机会（外部）",
        "threats": "威胁（外部）",
    }}


def kpi_dashboard(csv_text: str) -> dict:
    """从 CSV 读取 KPI（指标,值,目标）并计算达成。"""
    rows = list(csv.reader(io.StringIO(csv_text)))
    out = []
    for r in rows[1:]:
        if len(r) >= 3:
            try:
                val, tgt = float(r[1]), float(r[2])
                out.append({"metric": r[0], "value": val, "target": tgt,
                            "attainment": round(val / tgt, 3) if tgt else 0})
            except ValueError:
                continue
    return {"kpis": out, "count": len(out)}


def meeting_agenda(task: str) -> dict:
    """会议议程模板。"""
    return {"meeting": task, "agenda": [
        "目标（为什么开）",
        "议题与时间分配",
        "讨论与决策",
        "行动项（负责人/截止）",
    ]}


def risk_register(text: str) -> dict:
    """风险登记（每行：风险,可能性,影响 1-5）。"""
    risks = []
    for line in text.splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 3:
            try:
                p, i = int(parts[1]), int(parts[2])
                risks.append({"risk": parts[0], "probability": p,
                              "impact": i, "score": p * i})
            except ValueError:
                continue
    risks.sort(key=lambda x: -x["score"])
    return {"risks": risks, "high": [r for r in risks if r["score"] >= 12]}


class BusinessPack(DomainPack):
    key = "business"
    name = "企业运营"
    description = "商业模式、OKR、KPI、SWOT、会议与风险管理。"
    skills = [
        SkillSpec("business_model_canvas", business_model_canvas, "商业模式画布",
                  ["strategy", "canvas"], {"task": "str"}),
        SkillSpec("okr_gen", okr_gen, "OKR 生成",
                  ["okr", "planning"], {"task": "str"}),
        SkillSpec("swot_analysis", swot_analysis, "SWOT 分析",
                  ["strategy", "swot"], {"task": "str"}),
        SkillSpec("kpi_dashboard", kpi_dashboard, "KPI 看板",
                  ["kpi", "dashboard"], {"csv_text": "str"}),
        SkillSpec("meeting_agenda", meeting_agenda, "会议议程",
                  ["meeting"], {"task": "str"}),
        SkillSpec("risk_register", risk_register, "风险登记",
                  ["risk"], {"text": "str"}),
    ]
    roles = [
        RoleSpec("biz_strategist", "战略规划",
                 ["business_model_canvas", "swot_analysis"]),
        RoleSpec("biz_operator", "OKR/KPI 运营",
                 ["okr_gen", "kpi_dashboard", "meeting_agenda"]),
        RoleSpec("biz_risk_manager", "风险合规",
                 ["risk_register", "meeting_agenda"]),
    ]
    workflows = [
        WorkflowSpec("business_pipeline",
                     ["biz_strategist", "biz_operator", "biz_risk_manager"],
                     "战略→运营→风控"),
    ]
