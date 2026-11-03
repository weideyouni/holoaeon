# -*- coding: utf-8 -*-
"""
工程技能本地化工具箱（Engineering Skills Pack）
第18扩展包：8技能/4角色/2工作流
key = "eng_skills"
EXTRA_PACK_ORDER 17→18
DOC_VERSION 0.9.16→0.9.17（V22）

创意来源：mattpocock/skills（MIT, 310K★, "Skills for Real Engineers"）
本地化原则：LLM提示词→确定性Python函数，规则驱动非LLM驱动
全息适配：8技能映射8个自组织机制（心跳/经络/语义/骨架/皮肤/去幻觉/赫布/城邦）

审视修正（V22 投喂稿→实现）：
  1. 批次编号 V21→V22（原编号与概念解剖器图像增强版撞车）
  2. session_handoff.handoff_id 时间戳→确定性 sha1（同状态→同 id）
  3. _access_weights 模块级累积→默认固定基线（learning=True 才增量，默认确定性）
  4. grill_plan 中文分词→正则 [a-zA-Z0-9_]+|[\u4e00-\u9fff]+
  5. _compute_frontier 模板 f-string 双重插值→普通字符串+format
  6. import json/time 移置顶部；补 main() CLI + __main__ 守卫
  7. dual_axis_review 命令→真实入口
"""
from __future__ import annotations

import hashlib
import json
import re
import sys

from typing import Any, Dict, List

from .base import DomainPack, RoleSpec, SkillSpec, WorkflowSpec
from ..concept_anatomy import CONCEPT_MAP

# 中文/中英混合分词（holoaeon-dev-dna 规范：勿用空白 split）
_WORD_RE = re.compile(r"[a-zA-Z0-9_]+|[\u4e00-\u9fff]+")

# 赫布场：术语访问权重（默认确定性基线；learning=True 时增量增强）
_BASE_WEIGHT: Dict[str, float] = {
    "core": 0.75,
    "mechanism": 0.70,
    "runtime": 0.68,
    "architecture": 0.65,
    "security": 0.62,
    "other": 0.55,
}
_LR = 0.12
_DECAY = 0.99
_access_weights: Dict[str, float] = {}


def _bump(term: str) -> None:
    old = _access_weights.get(term, 0.5)
    _access_weights[term] = old * _DECAY + _LR * (1.0 - old)


def _reset_weights() -> None:
    """重置访问权重为初始基线（确定性：函数入口保证同输入同输出）。"""
    _access_weights.clear()


def _weight_for(term: str, entry: dict) -> float:
    dim = entry.get("dimension", "other")
    return _BASE_WEIGHT.get(dim, _BASE_WEIGHT["other"])


def _summarize(state: dict) -> str:
    return json.dumps(state, ensure_ascii=False, sort_keys=True)[:500]


def _suggest_skills(state: dict, focus: str) -> List[str]:
    skills = []
    blob = str(state).lower() + " " + focus.lower()
    if "bug" in blob or "error" in blob:
        skills.append("hypothesis_debug")
    if "plan" in blob or "design" in blob:
        skills.append("grill_plan")
    if "review" in blob:
        skills.append("dual_axis_review")
    if not skills:
        skills = ["grill_plan", "shared_glossary"]
    return skills


def _extract_refs(state: dict) -> List[str]:
    return [k for k in state.keys()][:10]


def _find_unfinished(state: dict) -> List[str]:
    return [k for k, v in state.items()
            if isinstance(v, str) and ("todo" in v.lower() or "wip" in v.lower())]


def _compute_frontier(keywords: List[str], depth: int) -> List[dict]:
    templates = [
        {"question": "为什么选择{k}？", "recommendation": "需要明确理由", "branch": "motivation"},
        {"question": "{k}的约束是什么？", "recommendation": "列出所有硬约束", "branch": "constraint"},
        {"question": "{k}如何验证？", "recommendation": "selftest+diff0", "branch": "verify"},
    ]
    result = []
    for k in keywords[:5]:
        idx = depth % len(templates)
        t = templates[idx]
        result.append({"question": t["question"].format(k=k),
                       "recommendation": t["recommendation"],
                       "branch": t["branch"]})
    return result


# ============================================================ 8个本地化技能

def grill_plan(plan_description: str = "", depth: int = 3, **_a) -> dict:
    """审讯规划：输入计划描述→返回结构化问题清单。心跳机制映射。
    确定性：同一计划描述→同一问题清单（中文按正则分词）。"""
    keywords = [w for w in _WORD_RE.findall(plan_description) if len(w) > 1]
    if not keywords:
        keywords = ["plan"]
    questions = []
    for d in range(depth):
        frontier = _compute_frontier(keywords, d)
        for q in frontier:
            questions.append({"round": d + 1, "question": q["question"],
                              "recommended_answer": q["recommendation"],
                              "branch": q["branch"]})
    return {"plan": plan_description, "questions": questions,
            "total_rounds": depth, "total_questions": len(questions),
            "mechanism": "心跳机制", "seal": "潮起开门，潮落闭嘴"}


def session_handoff(current_state: dict = None, next_focus: str = "", **_a) -> dict:
    """会话交接：压缩当前状态为交接文档。经络机制映射。
    确定性：同一状态→同一交接文档（handoff_id 由状态内容派生，非时间戳）。"""
    cs = current_state or {}
    blob = json.dumps(cs, ensure_ascii=False, sort_keys=True) + "|" + next_focus
    handoff_id = "handoff_" + hashlib.sha1(blob.encode("utf-8")).hexdigest()[:12]
    return {"handoff_id": handoff_id,
            "from_state": _summarize(cs), "next_focus": next_focus,
            "suggested_skills": _suggest_skills(cs, next_focus),
            "context_refs": _extract_refs(cs),
            "unfinished": _find_unfinished(cs),
            "redacted": True, "mechanism": "经络机制",
            "seal": "潮起开门，潮落闭嘴"}


def re_explain(text: str = "", glossary: dict = None, learning: bool = False, **_a) -> dict:
    """重新解释：用项目术语重新表达。语义通信基座映射。
    确定性：同一文本+同一词汇表→同一重新解释（learning=False 默认，权重不漂移）。"""
    g = glossary or CONCEPT_MAP
    replacements = {}
    simplified = text
    for term, entry in g.items():
        if term in simplified:
            replacements[term] = entry.get("description", "")[:80]
            simplified = simplified.replace(term, f"【{term}】")
            if learning:
                _bump(term)
    return {"original": text, "simplified": simplified,
            "replacements": replacements, "glossary_terms_found": len(replacements),
            "mechanism": "语义通信基座", "seal": "潮起开门，潮落闭嘴"}


def quick_prototype(design_question: str = "", mode: str = "logic", **_a) -> dict:
    """快速原型：验证设计问题不污染主分支。细胞骨架映射。"""
    if mode not in ("logic", "ui"):
        mode = "logic"
    return {"question": design_question, "mode": mode, "throwaway": True,
            "location": "prototype/branch",
            "validation_plan": ["1.创建隔离worktree", "2.最小验证逻辑",
                                "3.selftest确认不破坏", "4.验证设计问题",
                                "5.记录结论", "6.删除worktree"],
            "golden_check": "diff0不变", "mechanism": "细胞骨架",
            "seal": "潮起开门，潮落闭嘴"}


def deterministic_tdd(feature: str = "", **_a) -> dict:
    """确定性TDD：红绿重构+selftest+diff0。皮肤机制映射。"""
    return {"feature": feature,
            "cycle": [
                {"step": "RED", "action": f"写失败测试: test_{feature}",
                 "guard": "selftest应失败但不崩溃"},
                {"step": "GREEN", "action": "最小实现让测试通过",
                 "guard": "selftest 25/25 PASS"},
                {"step": "REFACTOR", "action": "重构不改变行为",
                 "guard": "diff0不漂移+golden通过"}],
            "seams": ["public_interface"],
            "anti_patterns": ["implementation_coupled", "tautological", "horizontal_slicing"],
            "vertical_slice": True, "mechanism": "皮肤机制",
            "seal": "潮起开门，潮落闭嘴"}


def dual_axis_review(since: str = "HEAD~1", **_a) -> dict:
    """双轴审查：Standards+Spec。皮肤机制映射。"""
    return {"since": since,
            "axis_standards": {"name": "Standards", "tool": "redline",
                               "check": "编码标准+Fowler基线",
                               "command": "python scripts\\redline_scan.py",
                               "expected": "零违规"},
            "axis_spec": {"name": "Spec", "tool": "verify_v44",
                          "check": "忠实实现规格",
                          "command": "python scripts\\verify_v44.py",
                          "expected": "13/13 A1-A13 全绿"},
            "parallel": True, "mechanism": "皮肤机制",
            "seal": "潮起开门，潮落闭嘴"}


def hypothesis_debug(bug_description: str = "", **_a) -> dict:
    """假设驱动调试：系统化调试环。去幻觉映射。"""
    return {"bug": bug_description,
            "phases": [
                {"phase": "1.最小化", "action": "最小复现路径", "guard": "稳定复现"},
                {"phase": "2.假设", "action": "≥3个假设+充分理由", "guard": "莱布尼茨PSR"},
                {"phase": "3.仪表化", "action": "加日志验证假设", "guard": "数据支持/排除"},
                {"phase": "4.修复", "action": "只改根因", "guard": "最小改动"},
                {"phase": "5.回归", "action": "selftest+diff0+golden", "guard": "不漂移"}],
            "anti_pattern": "猜测→改→试→猜测（禁止）",
            "mechanism": "去幻觉", "seal": "潮起开门，潮落闭嘴"}


def shared_glossary(query: str = None, learning: bool = False, **_a) -> dict:
    """共享词汇表：CONCEPT_MAP+访问权重。赫布协作场+经络映射。
    确定性：同一查询→同一结果（learning=False 默认权重=dimension 固定基线）。"""
    _reset_weights()
    glossary = {}
    for term, entry in CONCEPT_MAP.items():
        if learning:
            _bump(term)
            w = _access_weights.get(term, 0.5)
        else:
            w = _weight_for(term, entry)
        glossary[term] = {"dimension": entry["dimension"],
                          "mechanism": entry["mechanism"],
                          "description": entry["description"][:100],
                          "access_weight": round(w, 4)}
    if query:
        matched = {t: g for t, g in glossary.items()
                   if query.lower() in t.lower() or
                   query.lower() in g["description"].lower()}
        return {"query": query, "matched": matched, "resonance_count": len(matched),
                "mechanism": "赫布协作场+经络", "seal": "潮起开门，潮落闭嘴"}
    return {"glossary": glossary, "total_terms": len(glossary),
            "mechanism": "赫布协作场", "seal": "潮起开门，潮落闭嘴"}


# ============================================================ CLI（pyproject holoaeon-eng 入口）

def main(argv: List[str] = None) -> int:
    """holoaeon-eng 命令行入口：--list / --skill <name> --args <json> / --roles / --workflows。"""
    import argparse
    parser = argparse.ArgumentParser(
        prog="holoaeon-eng", description="工程技能本地化工具箱（第18扩展包，V22）")
    parser.add_argument("--list", action="store_true", help="列出 8 个本地化技能")
    parser.add_argument("--skill", metavar="NAME", help="调用单个技能（grill_plan/session_handoff/...）")
    parser.add_argument("--args", metavar="JSON", default="{}",
                        help="技能参数 JSON（如 '{\"plan_description\":\"加个缓存\"}'）")
    parser.add_argument("--roles", action="store_true", help="列出 4 个角色")
    parser.add_argument("--workflows", action="store_true", help="列出 2 个工作流")
    args = parser.parse_args(argv)

    if args.list or not (args.skill or args.roles or args.workflows):
        print("工程技能本地化工具箱（eng_skills）8 技能：")
        for s in PACK.skills:
            print(f"  - {s.name}: {s.description}")
        if args.list:
            return 0
    if args.roles:
        print("角色（4）：")
        for r in PACK.roles:
            print(f"  - {r.name}: {r.description}（技能: {', '.join(r.skills)}）")
        return 0
    if args.workflows:
        print("工作流（2）：")
        for w in PACK.workflows:
            print(f"  - {w.name}: {w.description}（步骤: {' → '.join(w.steps)}）")
        return 0
    if args.skill:
        fn = SKILL_FN.get(args.skill)
        if fn is None:
            print(f"未知技能: {args.skill}（可选: {', '.join(SKILL_FN)}）", file=sys.stderr)
            return 1
        try:
            params = json.loads(args.args)
        except json.JSONDecodeError as e:
            print(f"--args 不是合法 JSON: {e}", file=sys.stderr)
            return 1
        print(json.dumps(fn(**params), ensure_ascii=False, indent=2))
        return 0
    return 0


# ============================================================ 扩展包声明
class EngineeringSkillsPack(DomainPack):
    key = "eng_skills"
    name = "工程技能本地化工具箱"
    description = (
        "mattpocock/skills 310K★ 蒸馏本地化：8技能映射8个全息机制，"
        "LLM提示词→确定性Python函数，纯标准库"
    )

    skills = [
        SkillSpec("grill_plan", grill_plan,
                  "审讯规划：计划描述→结构化问题清单（心跳机制）",
                  tags=["eng_skills", "grill", "plan", "heartbeat"],
                  inputs={"plan_description": "str", "depth": "int"}),
        SkillSpec("session_handoff", session_handoff,
                  "会话交接：压缩状态为交接文档（经络机制）",
                  tags=["eng_skills", "handoff", "session", "bus"],
                  inputs={"current_state": "dict", "next_focus": "str"}),
        SkillSpec("re_explain", re_explain,
                  "重新解释：用项目术语重新表达（语义通信基座）",
                  tags=["eng_skills", "explain", "seb", "glossary"],
                  inputs={"text": "str"}),
        SkillSpec("quick_prototype", quick_prototype,
                  "快速原型：验证设计不污染主分支（细胞骨架）",
                  tags=["eng_skills", "prototype", "throwaway", "kernel"],
                  inputs={"design_question": "str", "mode": "str"}),
        SkillSpec("deterministic_tdd", deterministic_tdd,
                  "确定性TDD：红绿重构+selftest+diff0（皮肤机制）",
                  tags=["eng_skills", "tdd", "red_green", "guard"],
                  inputs={"feature": "str"}),
        SkillSpec("dual_axis_review", dual_axis_review,
                  "双轴审查：Standards+Spec并行（皮肤机制）",
                  tags=["eng_skills", "review", "redline", "verify"],
                  inputs={"since": "str"}),
        SkillSpec("hypothesis_debug", hypothesis_debug,
                  "假设驱动调试：系统化调试环（去幻觉）",
                  tags=["eng_skills", "debug", "hypothesis", "psr"],
                  inputs={"bug_description": "str"}),
        SkillSpec("shared_glossary", shared_glossary,
                  "共享词汇表：CONCEPT_MAP+访问权重（赫布+经络）",
                  tags=["eng_skills", "glossary", "hebbian", "meridian"],
                  inputs={"query": "str"}),
    ]

    roles = [
        RoleSpec("planner", "规划师（审讯规划+会话交接）",
                 ["grill_plan", "session_handoff"]),
        RoleSpec("reviewer", "审查师（双轴审查+确定性TDD）",
                 ["dual_axis_review", "deterministic_tdd"]),
        RoleSpec("debugger", "调试师（假设调试+快速原型）",
                 ["hypothesis_debug", "quick_prototype"]),
        RoleSpec("linguist", "语言师（重新解释+共享词汇表）",
                 ["re_explain", "shared_glossary"]),
    ]

    workflows = [
        WorkflowSpec("full_engineering",
                     ["planner", "reviewer", "debugger", "linguist"],
                     "规划→交接→TDD→审查→调试→解释→词汇（完整工程流程）"),
        WorkflowSpec("quick_fix",
                     ["debugger", "reviewer"],
                     "假设调试→双轴审查（快速修复流程）"),
    ]


PACK = EngineeringSkillsPack()
SKILL_FN: Dict[str, Any] = {s.name: s.fn for s in PACK.skills}

if __name__ == "__main__":
    sys.exit(main())
