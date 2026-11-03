# -*- coding: utf-8 -*-
"""
概念解剖器扩展包（Concept Anatomy Pack）
================================================================================
第 17 个扩展包：5 技能 / 3 角色 / 1 工作流
key = "concept_anatomy"（EXTRA_PACK_ORDER 16→17，V19-CONCEPT-ANATOMIZER）

创意来源：wheresryan22/anatomy（MIT, "The object is the explanation"）创意蒸馏
适配原则：Anatomy=视觉发明(LLM) / HoloAeon=确定性查找(规则) / 交集=概念→机制映射
审视修正（V19 执行侧）：SkillSpec 按 base.py 实际字段（name/fn/description/tags/inputs）
定义，弃用投喂稿的 key/desc/callable/outputs 假字段。

维度不变：只进 EXTRA_PACK_REGISTRY，不进 PACK_ORDER —— A1 的 25/47/9 不受影响。
"""
from __future__ import annotations

from typing import Any, Dict, List

from .base import DomainPack, RoleSpec, SkillSpec, WorkflowSpec
from ..concept_anatomy import CONCEPT_MAP, DESIGN_TOKENS, ConceptAnatomizer


# ============================================================ 技能实现（模块级函数）
def anatomy_concept(concept_name: str = "经络", **_a: Any) -> dict:
    """概念解剖（D-01/D-03）：抽象概念→十步工序→结构化解剖图（确定性）。"""
    ca = ConceptAnatomizer()
    r = ca.anatomize(str(concept_name))
    if "error" in r:
        return {"status": "WARN", "error": r["error"],
                "available": r.get("available", [])}
    return {"status": r["status"], "concept": r["concept"],
            "component_count": r["anatomy"]["component_count"],
            "mechanism": r["anatomy"]["mechanism"],
            "audit_passed": r["anatomy"]["audit"]["all_passed"]}


def anatomy_audit(concept_name: str = "经络", **_a: Any) -> dict:
    """深度审计（D-04）：重叠对 + 穿透 + 一致性 + 确定性 四检查。"""
    ca = ConceptAnatomizer()
    r = ca.anatomize(str(concept_name))
    if "error" in r:
        return {"status": "WARN", "error": r["error"]}
    audit = r["anatomy"]["audit"]
    return {"status": r["status"], "concept": r["concept"],
            "level": audit["level"],
            "checks": list(audit["checks"].keys()),
            "all_passed": audit["all_passed"],
            "overlaps_found": audit["checks"]["overlap"]["overlaps_found"],
            "penetration_issues": audit["checks"]["penetration"]["issues_found"],
            "consistency_issues": audit["checks"]["consistency"]["issues_found"]}


def anatomy_svg(concept_name: str = "城邦架构", **_a: Any) -> dict:
    """等距投影SVG（D-02/D-05）：纯字符串拼接，无 DOM 库。"""
    ca = ConceptAnatomizer()
    r = ca.anatomize(str(concept_name))
    if "error" in r:
        return {"status": "WARN", "error": r["error"]}
    svg = r["output"].get("svg", "")
    return {"status": "ok", "concept": r["concept"],
            "svg_length": len(svg), "has_svg_tag": "<svg" in svg}


def anatomy_map(concept_name: str = "经络", **_a: Any) -> dict:
    """概念映射表（D-01）：HoloAeon 概念→确定性机制固化映射。"""
    entry = CONCEPT_MAP.get(str(concept_name))
    if entry is None:
        return {"status": "WARN", "error": f"未知概念: {concept_name}",
                "available": list(CONCEPT_MAP.keys())}
    return {"status": "ok", "concept": str(concept_name),
            "dimension": entry["dimension"], "mechanism": entry["mechanism"],
            "components": entry["components"],
            "verification": entry["verification"], "source": entry["source"]}


def anatomy_tokens(**_a: Any) -> dict:
    """设计Token系统（D-05）：26 个配置变量（运行时/审计/输出/验证/全息）。"""
    return {"status": "ok", "token_count": len(DESIGN_TOKENS),
            "tokens": DESIGN_TOKENS}


# ============================================================ 扩展包声明
class ConceptAnatomyPack(DomainPack):
    key = "concept_anatomy"
    name = "概念解剖器"
    description = (
        "Anatomy 创意蒸馏：概念→确定性机制→结构化解剖图"
        "（十步工序 + 深度审计 + 26 Token），纯标准库确定性离线"
    )

    skills = [
        SkillSpec("anatomy_concept", anatomy_concept,
                  "概念解剖（十步工序）：抽象概念→结构化解剖图（确定性查找非LLM）",
                  tags=["concept_anatomy", "anatomy", "ten_step", "mechanism"],
                  inputs={"concept_name": "str"}),
        SkillSpec("anatomy_audit", anatomy_audit,
                  "深度审计：重叠对 + 穿透 + 一致性 + 确定性 四检查",
                  tags=["concept_anatomy", "audit", "overlap", "penetration"],
                  inputs={"concept_name": "str"}),
        SkillSpec("anatomy_svg", anatomy_svg,
                  "等距投影SVG渲染（纯字符串拼接，无 DOM 库）",
                  tags=["concept_anatomy", "svg", "isometric", "render"],
                  inputs={"concept_name": "str"}),
        SkillSpec("anatomy_map", anatomy_map,
                  "概念映射表：HoloAeon 概念→确定性机制的固化映射",
                  tags=["concept_anatomy", "map", "mechanism", "lookup"],
                  inputs={"concept_name": "str"}),
        SkillSpec("anatomy_tokens", anatomy_tokens,
                  "设计Token系统：26 个配置变量（运行时/审计/输出/验证/全息）",
                  tags=["concept_anatomy", "tokens", "theme", "config"],
                  inputs={}),
    ]

    roles = [
        RoleSpec("anatomist", "解剖师（执行十步工序的概念解剖专家）",
                 ["anatomy_concept", "anatomy_map"]),
        RoleSpec("auditor", "审计师（深度审计：重叠/穿透/一致性验证专家）",
                 ["anatomy_audit"]),
        RoleSpec("cartographer", "制图师（等距投影SVG渲染专家）",
                 ["anatomy_svg", "anatomy_tokens"]),
    ]

    workflows = [
        WorkflowSpec("full_anatomy",
                     ["anatomist", "auditor", "cartographer"],
                     "取映射→十步解剖→深度审计→渲染SVG（完整解剖流程）"),
    ]


def pack_summary() -> Dict[str, Any]:
    p = ConceptAnatomyPack()
    return {"key": p.key, "name": p.name,
            "skills": len(p.skills), "roles": len(p.roles),
            "workflows": len(p.workflows)}
