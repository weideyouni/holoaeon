# -*- coding: utf-8 -*-
"""
群体智能引擎扩展包（Swarm Intelligence Pack）
================================================================================
第 19 个扩展包：5 技能 / 3 角色 / 2 工作流
key = "swarm_intel"（EXTRA_PACK_ORDER 18→19，V24）

创意来源：MiroFish（666ghj/MiroFish, AGPL-3.0）五阶段流水线蒸馏
适配原则：MiroFish=LLM群体涌现预测 / HoloAeon=确定性规则认知协作
         交集=把群体涌现的 pipeline 结构用确定性规则实现
许可证：只蒸馏创意与方法论，不复制任何源代码（思想-表达二分法）

审视修正（V24 执行侧）：
  * SkillSpec 按 base.py 实际字段（name/fn/description/tags/inputs/permissions），
    弃用投喂稿的 key/desc/func 假字段。
  * 角色名与工作流名用小写下划线（与既有包风格一致），展示名放 description。
  * EXTRA_PACK_ORDER 实为 List[str] + EXTRA_PACK_REGISTRY 类注册，非投喂稿的 dict 列表。

维度不变：只进 EXTRA_PACK_REGISTRY，不进 PACK_ORDER —— A1 的 25/47/9 不受影响。
"""
from __future__ import annotations

from typing import Any, Dict

from .base import DomainPack, RoleSpec, SkillSpec, WorkflowSpec
from ..swarm_intel import (swarm_deep_interact, swarm_parallel_simulate,
                           swarm_persona_synthesize, swarm_report_generate,
                           swarm_seed_to_graph)

PACK_META: Dict[str, Any] = {
    "key": "swarm_intel",
    "name": "群体智能引擎",
    "version": "1.0.0",
    "source": "MiroFish (666ghj/MiroFish) 蒸馏本地化",
    "license_note": "MiroFish=AGPL-3.0 / HoloAeon=Apache-2.0；只蒸馏创意方法论，不复制代码",
    "skills_count": 5,
    "roles_count": 3,
    "workflows_count": 2,
}

# 机制覆盖表（11/11 全覆盖）
MECHANISM_COVERAGE: Dict[str, str] = {
    "心跳机制": "five_stage_pipeline 每阶段一个 tick",
    "细胞骨架机制": "persona_architect 装配 agent 实例",
    "皮肤机制": "god_view_injection 注入前载荷过滤",
    "经络机制": "seed_to_graph 图路由 + deep_interact inbox",
    "赫布协作场": "parallel_simulate 主路径/验证路径双路",
    "语义通信基座": "AgentAction 封装为 Envelope",
    "自组织相似性": "report_generate 共振模式提取",
    "runtime": "SwarmOrchestrator 运行时管理",
    "graph": "EntityGraph 邻接表图",
    "类社会组合体": "agent 群体 + 社交演化记录",
    "城邦架构": "多 SimulationRun = 多城邦",
}


# ============================================================ 扩展包声明
class SwarmIntelPack(DomainPack):
    key = "swarm_intel"
    name = "群体智能引擎"
    description = (
        "MiroFish 五阶段流水线蒸馏（Graph→World→Simulate→Report→Interact）："
        "种子建图 + 规则 Persona + 双路并行模拟 + 确定性报告 + 深度采访，"
        "纯标准库零 LLM，11/11 自组织机制覆盖"
    )

    skills = [
        SkillSpec("swarm_seed_to_graph", swarm_seed_to_graph,
                  "种子建图（Stage1）：文本→实体/关系邻接表（规则提取，替代 GraphRAG+Zep）",
                  tags=["swarm_intel", "graph", "seed", "entity"],
                  inputs={"seed_text": "str", "max_entities": "int"}),
        SkillSpec("swarm_persona_synthesize", swarm_persona_synthesize,
                  "角色合成（Stage2）：图实体→规则 Persona（替代 LLM Persona 生成）",
                  tags=["swarm_intel", "persona", "profile", "rule_based"],
                  inputs={"seed_text": "str", "max_entities": "int"}),
        SkillSpec("swarm_parallel_simulate", swarm_parallel_simulate,
                  "并行模拟（Stage3）：主路径+验证路径双路推进，action 记录（替代 OASIS）",
                  tags=["swarm_intel", "simulate", "parallel", "verify"],
                  inputs={"seed_text": "str", "rounds": "int"}),
        SkillSpec("swarm_report_generate", swarm_report_generate,
                  "报告生成（Stage4）：action 统计→涌现模式→结构化报告（替代 ReportAgent+LLM）",
                  tags=["swarm_intel", "report", "emergent", "aggregate"],
                  inputs={"seed_text": "str", "rounds": "int"}),
        SkillSpec("swarm_deep_interact", swarm_deep_interact,
                  "深度交互（Stage5）：采访 agent→规则响应（替代 IPC+LLM interview）",
                  tags=["swarm_intel", "interact", "interview", "inbox"],
                  inputs={"seed_text": "str", "prompt": "str"}),
    ]

    roles = [
        RoleSpec("swarm_orchestrator", "群体编排器（五阶段流水线统一入口，管理多个模拟城邦）",
                 ["swarm_seed_to_graph", "swarm_persona_synthesize",
                  "swarm_parallel_simulate", "swarm_report_generate"]),
        RoleSpec("persona_architect", "角色建筑师（图实体→规则 Persona，装配 agent 实例）",
                 ["swarm_persona_synthesize"]),
        RoleSpec("report_synthesizer", "报告合成器（action 记录→涌现模式→结构化报告）",
                 ["swarm_report_generate", "swarm_deep_interact"]),
    ]

    workflows = [
        WorkflowSpec("five_stage_pipeline",
                     ["swarm_orchestrator", "persona_architect", "report_synthesizer"],
                     "Graph→World→Simulate→Report→Interact（每阶段一个 tick，心跳机制）"),
        WorkflowSpec("god_view_injection",
                     ["swarm_orchestrator", "report_synthesizer"],
                     "在已完成模拟上注入新事件（皮肤机制过滤后注入），观察 agent 反应"),
    ]


def get_manifest() -> Dict[str, Any]:
    p = SwarmIntelPack()
    return {
        "meta": PACK_META,
        "skills": {s.name: {"description": s.description, "tags": s.tags}
                   for s in p.skills},
        "roles": {r.name: {"description": r.description, "skills": r.skills}
                  for r in p.roles},
        "workflows": {w.name: {"description": w.description, "steps": w.steps}
                      for w in p.workflows},
        "mechanism_coverage": MECHANISM_COVERAGE,
        "coverage_count": "%d/11" % len(MECHANISM_COVERAGE),
    }


def pack_summary() -> Dict[str, Any]:
    p = SwarmIntelPack()
    return {"key": p.key, "name": p.name, "skills": len(p.skills),
            "roles": len(p.roles), "workflows": len(p.workflows),
            "coverage_count": "%d/11" % len(MECHANISM_COVERAGE)}
