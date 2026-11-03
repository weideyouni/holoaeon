# -*- coding: utf-8 -*-
"""
TCMRehabPack —— 中西医系统康复工程·旗舰领域包（第 11 个扩展包，不进 PACK_ORDER）
================================================================================
把"中西医系统康复工程"从通用基座的分支提回旗舰领域包：与 holoaeon 通用内核
彻底解耦 —— 本包只依赖标准库，离线可跑，静态 TCM 知识以内嵌数据承载，
不依赖任何外部数据库 / 网络 / GPU。

4 个核心技能：
  tcm_syndrome       辨证分型（确定性规则映射，症状 → 证型候选 + 依据说明）
  tcm_formula_lookup 方药检索（静态方剂索引：方名 → 组成/主治，只列药名不给剂量）
  tcm_rehab_plan     康复方案（确定性分阶段模板，不诊疗）
  tcm_kb_bridge      知识库桥接（把 holoaeon 技能矩阵摘要桥接给外部 TCM 项目审计）

医学纪律（继承全局红线，不可移动）：
  · 零剂量：本包所有输出不含任何具体剂量（含毒药材只标"须医师处方"，熔断 E13/E14）
  · 不诊疗：一切输出为"教学/研究参考"，evidence_class=simulated，碳基终裁
  · 归属标注：方剂/证型归属按公开资料标注，不冒认医家学派

维度不变：只进 EXTRA_PACK_REGISTRY，不进 PACK_ORDER —— A1（25/47/9）不受影响。
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from .base import DomainPack, RoleSpec, SkillSpec, WorkflowSpec

# ----------------------------------------------------------------------------
# 静态知识（内嵌、只读、确定性；公开常识性条目，非医学处方）
# ----------------------------------------------------------------------------

# 常见证型 → 关键症状关键词（确定性规则表；条目为教学示例，不做诊断）
SYNDROME_RULES: Dict[str, tuple] = {
    "风寒束表": ("恶寒", "发热", "无汗", "头痛", "鼻塞", "流清涕"),
    "风热犯表": ("发热重", "咽痛", "口渴", "黄涕", "汗出", "咳嗽黄痰"),
    "气阴两虚": ("乏力", "气短", "自汗", "盗汗", "口干", "舌红少苔"),
    "脾虚湿盛": ("纳差", "腹胀", "便溏", "乏力", "苔腻", "身重"),
    "肝郁气滞": ("胁胀", "善太息", "情志不舒", "嗳气", "脉弦"),
    "瘀血阻络": ("刺痛", "固定痛", "舌暗", "瘀斑", "入夜加重"),
}

# 静态方剂索引（方名 → (出处, 组成药名, 主治概述)；**只列药名，不给剂量**）
FORMULAS: Dict[str, tuple] = {
    "桂枝汤": ("《伤寒论》", ("桂枝", "芍药", "生姜", "大枣", "甘草"),
               "太阳中风表虚证：恶风、汗出、脉浮缓（教学示例，剂量须医师处方）"),
    "麻黄汤": ("《伤寒论》", ("麻黄", "桂枝", "杏仁", "甘草"),
               "太阳伤寒表实证：恶寒发热、无汗、身痛（教学示例，剂量须医师处方）"),
    "银翘散": ("《温病条辨》", ("金银花", "连翘", "薄荷", "荆芥", "淡豆豉", "牛蒡子", "桔梗", "甘草", "芦根", "竹叶"),
               "风温初起：发热、咽痛、微恶风寒（教学示例，剂量须医师处方）"),
    "四君子汤": ("《太平惠民和剂局方》", ("人参", "白术", "茯苓", "甘草"),
                 "脾胃气虚：食少便溏、面色萎白（教学示例，剂量须医师处方）"),
    "逍遥散": ("《太平惠民和剂局方》", ("柴胡", "当归", "白芍", "白术", "茯苓", "甘草", "生姜", "薄荷"),
               "肝郁血虚脾弱：胁胀、情志不舒（教学示例，剂量须医师处方）"),
    "血府逐瘀汤": ("《医林改错》", ("桃仁", "红花", "当归", "川芎", "赤芍", "生地", "牛膝", "柴胡", "枳壳", "桔梗", "甘草"),
                   "胸中血瘀：刺痛固定、舌暗有瘀（教学示例，剂量须医师处方）"),
}

# 毒剧药熔断（E13/E14）：命中即拒给任何剂量/组成细节，只提示医师处方
TOXIC_HERBS = ("附子", "乌头", "马钱子", "蟾酥", "雄黄", "砒霜", "细辛",
               "川乌", "草乌", "天仙子", "巴豆", "甘遂", "大戟", "芫花")

REHAB_STAGES = ("评估期", "恢复期", "巩固期", "维持期")


def _strip_dose(text: str) -> str:
    """零剂量保护：任何输出进入前先剥离数字+剂量单位模式，防止漏出剂量。"""
    import re
    return re.sub(r"\d+(\.\d+)?\s*(g|克|mg|毫克|ml|毫升|片|粒|丸|钱|两)", "", text)


# ---------------------------------------------------------------- 四技能实现
def tcm_syndrome(symptoms: str = "", **_kwargs: Any) -> dict:
    """辨证分型：输入症状关键词（逗号/顿号分隔）→ 命中证型候选 + 依据 + 熔断提示。"""
    if not symptoms:
        return {"ok": True, "candidates": [], "note": "请提供症状描述（教学场景，不构成诊断）",
                "evidence_class": "simulated"}
    keys = [k for k in _strip_dose(symptoms).replace("，", ",").replace("、", ",").split(",") if k.strip()]
    hits = []
    for name, words in SYNDROME_RULES.items():
        matched = [w for w in words if w in symptoms]
        if matched:
            hits.append({"syndrome": name, "matched": matched, "count": len(matched),
                         "disclaimer": "教学示例，非诊断结论"})
    hits.sort(key=lambda h: -h["count"])
    return {"ok": True, "candidates": hits[:5],
            "note": "辨证分型为确定性规则映射，仅供研究与教学参考；临床请由执业医师完成",
            "evidence_class": "simulated"}


def tcm_formula_lookup(formula: str = "", **_kwargs: Any) -> dict:
    """方药检索：方名 → 出处/组成/主治；只列药名不给剂量；毒剧药熔断。"""
    if not formula:
        names = sorted(FORMULAS.keys())
        return {"ok": True, "index": names, "note": "内置方剂索引（示例库）",
                "evidence_class": "simulated"}
    name = formula.strip()
    # E13/E14 毒剧药熔断
    for t in TOXIC_HERBS:
        if t in name:
            return {"ok": False, "blocked": True, "herb": t,
                    "note": "含毒剧药材：仅允许教学层面提及，须医师处方，本包不给出任何剂量/组成细节",
                    "evidence_class": "simulated"}
    hit = FORMULAS.get(name)
    if not hit:
        # 模糊匹配（子串）
        hit = next((v for k, v in FORMULAS.items() if name in k), None)
    if not hit:
        return {"ok": False, "blocked": False, "note": "索引中无此方（示例库有限）",
                "evidence_class": "simulated"}
    source, herbs, indication = hit
    return {"ok": True, "formula": name, "source": source, "herbs": list(herbs),
            "indication": _strip_dose(indication),
            "dose": "零剂量：本包不提供任何具体剂量，须医师处方",
            "evidence_class": "simulated"}


def tcm_rehab_plan(condition: str = "", stage: str = "恢复期", **_kwargs: Any) -> dict:
    """康复方案：确定性分阶段模板（评估→恢复→巩固→维持），不诊疗、不给医疗处方。"""
    st = stage if stage in REHAB_STAGES else "恢复期"
    plan = {
        "评估期": ("采集基线", "功能/症状记录", "设定可衡量目标"),
        "恢复期": ("基础功能训练", "症状监测", "分阶段回归日常活动"),
        "巩固期": ("负荷渐进", "防复发要点", "自我管理技能"),
        "维持期": ("长期习惯养成", "定期复评", "转归记录"),
    }
    return {"ok": True, "condition": condition or "（待填）", "stage": st,
            "plan": list(plan[st]), "dose": "零剂量",
            "note": "通用康复流程模板，非个体化医疗方案；具体干预须由执业医师/康复师制定",
            "evidence_class": "simulated"}


def tcm_kb_bridge(scope: str = "summary", **_kwargs: Any) -> dict:
    """知识库桥接：把 holoaeon 技能矩阵的确定性摘要桥接给外部 TCM 项目审计。
    只读、零网络；输出 count/digest/roots + medical_context 审计标记。"""
    try:
        with open("data/skill_matrix_index.json", encoding="utf-8") as f:
            idx = json.load(f)
        summary = {"count": idx.get("count"), "digest": idx.get("digest"),
                   "roots": len(idx.get("roots", [])),
                   "stats": idx.get("stats", {})}
    except Exception as exc:
        summary = {"error": str(exc)}
    return {"ok": True, "scope": scope, "index": summary,
            "medical_context": "external_tcm_project_audit",
            "note": "外部中西医康复工程项目可按此摘要做审计分类；本包与通用基座解耦",
            "evidence_class": "simulated"}


TCM_SKILLS = ("tcm_syndrome", "tcm_formula_lookup", "tcm_rehab_plan", "tcm_kb_bridge")


class TCMRehabPack(DomainPack):
    key = "tcm_rehab"
    name = "中西医系统康复工程（旗舰领域包）"
    description = ("把中西医系统康复工程提回旗舰领域包：辨证分型、方药检索、康复方案、"
                   "知识库桥接四技能，纯标准库离线确定性，零剂量/不诊疗/碳基终裁；"
                   "旁挂注册，不改 25/47/9")

    skills = [
        SkillSpec("tcm_syndrome", tcm_syndrome,
                  "辨证分型：症状关键词 → 证型候选 + 依据 + 熔断提示（教学示例，非诊断）",
                  tags=["tcm", "syndrome", "rehab"], inputs={"symptoms": "str"}),
        SkillSpec("tcm_formula_lookup", tcm_formula_lookup,
                  "方药检索：方名 → 出处/组成/主治；只列药名不给剂量；毒剧药熔断 E13/E14",
                  tags=["tcm", "formula", "rehab"], inputs={"formula": "str"}),
        SkillSpec("tcm_rehab_plan", tcm_rehab_plan,
                  "康复方案：确定性分阶段模板（评估/恢复/巩固/维持），不诊疗",
                  tags=["tcm", "rehab", "plan"], inputs={"condition": "str", "stage": "str"}),
        SkillSpec("tcm_kb_bridge", tcm_kb_bridge,
                  "知识库桥接：技能矩阵确定性摘要 + medical_context 审计标记（外部 TCM 项目用）",
                  tags=["tcm", "bridge", "audit"], inputs={"scope": "str"}),
    ]

    roles = [
        RoleSpec("tcm_rehab_assistant", "中西医康复助手：辨证、方药检索、康复方案",
                 ["tcm_syndrome", "tcm_formula_lookup", "tcm_rehab_plan"]),
        RoleSpec("tcm_kb_bridger", "知识库桥接：对外部 TCM 项目提供审计摘要",
                 ["tcm_kb_bridge"]),
    ]

    workflows = [
        WorkflowSpec("tcm_rehab_flow", ["tcm_rehab_assistant", "tcm_kb_bridger"],
                     "先辨证分型 → 方药检索 → 康复方案模板 → 知识库桥接审计摘要"),
    ]


def pack_summary() -> Dict[str, Any]:
    p = TCMRehabPack()
    return {"key": p.key, "skills": len(p.skills), "roles": len(p.roles),
            "workflows": len(p.workflows), "skill_names": list(TCM_SKILLS)}
