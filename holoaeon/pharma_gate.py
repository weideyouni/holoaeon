# -*- coding: utf-8 -*-
"""pharma_gate — 药品域闸门（V46，千问 V45 评估 P0-1 采纳 · 医保药品处置维度）
D-11 链位：领域编排环（第十四环·药品域）——teach_gate（第十三环）之后。
缘起：千问 V45 核验（2026-11-09，总分 87.5）P0-1——医保药品库全仓 0 实现
（独立复核实属）。其裁决：**确定性登记表而非向量库**（与总监 V42 扬弃
千问上一轮"装向量库"建议完全趋同——两个独立评估轮次在第一性原理上
收敛：医保查询=精确查表，向量相似在医保场景是危险的）。
指针纪律：本环只交付 schema+登记表引擎+示例条目（evidence_class=simulated）；
真实国家医保目录数据由部署侧联网取官方文（授权后）填入——零联网取数。
零剂量红线：登记字段 schema 无 dose 列，含 dose 字段的条目直接拒收
（千问原话"零剂量原则"，与 IVSA 耦合桥 dose_request 拦截同频）。
诚实纪律：InsuranceCheck 四态——甲类/乙类/非医保/**未登记**。
未登记 ≠ 非医保（目录未收录时返回 unknown 并提示"以官方目录为准"，
防止"库没有=不报销"的危险误判）。
版本时点锁定：每条登记必带 catalog_year + source_doc（医保目录逐年调整，
无时点的数据是过期数据）。
红线拦截：dose_request / clinical_decision / emergency_override /
physical_self_stimulation 四类（IVSA 耦合桥已验证的四类，本环药品域同款）。
零依赖纯标准库。封口密语：潮起开门，潮落闭嘴。
"""
import time

SEAL = "潮起开门，潮落闭嘴"

CHAIN_POSITION = {
    "ring": 14,
    "name": "药品域编排（医保药品处置维度闸门）",
    "upstream": ("phc_chronic_engine", "phc_recall", "guard"),
    "role": "登记表精确查表+保险四态+红线拦截+版本时点锁定",
    "lineage_note": "千问两轮独立趋同（V42弃向量库/V46登记表）：复算精神同频",
    "disposition_note": "零剂量零诊断；未登记≠非医保；真实目录部署侧填入",
}

# 登记表 schema（零剂量：无 dose 字段——schema 级强制）
CATALOG_FIELDS = ("generic_name", "insurance_class", "limited_scope",
                  "catalog_year", "source_doc", "evidence_class")

VALID_CLASSES = ("甲类", "乙类", "非医保")
VALID_EVIDENCE = ("measured", "simulated")

# 红线四类（IVSA 耦合桥同款，药品域变体）
REDLINE_ACTIONS = ("dose_request", "clinical_decision",
                   "emergency_override", "physical_self_stimulation")


def validate_entry(entry):
    """登记条目校验：字段齐、类别合法、证据标注必填、零剂量。"""
    if not isinstance(entry, dict):
        return {"ok": False, "error": "entry must be dict", "seal": SEAL}
    for f in CATALOG_FIELDS:
        if f not in entry:
            return {"ok": False, "error": "missing field: %s" % f,
                    "seal": SEAL}
    if "dose" in entry or any("dose" in k for k in entry):
        return {"ok": False, "error": "零剂量红线：登记表不收剂量字段",
                "seal": SEAL}
    if entry["insurance_class"] not in VALID_CLASSES:
        return {"ok": False, "error": "insurance_class must be 甲类/乙类/非医保",
                "seal": SEAL}
    if entry["evidence_class"] not in VALID_EVIDENCE:
        return {"ok": False, "error": "evidence_class must be measured/simulated",
                "seal": SEAL}
    if not isinstance(entry["catalog_year"], int) or entry["catalog_year"] < 2000:
        return {"ok": False, "error": "catalog_year must be year int",
                "seal": SEAL}
    return {"ok": True, "seal": SEAL}


class DrugRegistry:
    """确定性登记表：register（校验入库）+ lookup（精确查表）。
    精确匹配，不做向量相似——医保场景错判报销资格是危险的。"""

    def __init__(self):
        self.entries = {}

    def register(self, entry):
        v = validate_entry(entry)
        if not v["ok"]:
            return v
        key = entry["generic_name"]
        self.entries[key] = dict(entry)
        return {"ok": True, "drug": key,
                "evidence_class": entry["evidence_class"], "seal": SEAL}

    def lookup(self, generic_name):
        e = self.entries.get(generic_name)
        if e is None:
            return {"ok": True, "found": False, "drug": generic_name,
                    "status": "unknown",
                    "note": "目录未收录——未登记≠非医保，以官方目录为准",
                    "seal": SEAL}
        return {"ok": True, "found": True, "drug": generic_name,
                "insurance_class": e["insurance_class"],
                "limited_scope": e["limited_scope"],
                "catalog_year": e["catalog_year"],
                "source_doc": e["source_doc"],
                "evidence_class": e["evidence_class"], "seal": SEAL}

    def version_pin(self):
        """版本时点锁定：登记表的年份与来源集合（过期可检出）。"""
        years = sorted({e["catalog_year"] for e in self.entries.values()})
        sources = sorted({e["source_doc"] for e in self.entries.values()})
        return {"ok": True, "catalog_years": years, "sources": sources,
                "entries": len(self.entries),
                "note": "医保目录逐年调整，使用前核对 catalog_year",
                "seal": SEAL}


class DisposalGate:
    """处置维度红线闸：四类动作拦截（report-only 出裁决，不执行）。"""

    @classmethod
    def check(cls, action):
        if action in REDLINE_ACTIONS:
            return {"ok": True, "verdict": "BLOCK", "action": action,
                    "reason": "药品域红线：零剂量零诊断零急救指令零刺激",
                    "seal": SEAL}
        return {"ok": True, "verdict": "ALLOW", "action": action,
                "reason": "非红线动作（登记/查询/汇总类）", "seal": SEAL}


# 示例条目（evidence_class=simulated——演示数据，非官方目录转录；
# 真实条目由部署侧联网取国家医保局官方目录填入，标 measured）
SAMPLE_ENTRIES = [
    {"generic_name": "阿司匹林肠溶片（示例）", "insurance_class": "甲类",
     "limited_scope": "示例：限缺血性心脑血管疾病（以官方目录为准）",
     "catalog_year": 2025, "source_doc": "示例-国家基本医疗保险目录（部署侧替换）",
     "evidence_class": "simulated"},
    {"generic_name": "二甲双胍片（示例）", "insurance_class": "甲类",
     "limited_scope": "示例：限2型糖尿病（以官方目录为准）",
     "catalog_year": 2025, "source_doc": "示例-国家基本医疗保险目录（部署侧替换）",
     "evidence_class": "simulated"},
    {"generic_name": "氨氯地平片（示例）", "insurance_class": "乙类",
     "limited_scope": "示例：限高血压（以官方目录为准）",
     "catalog_year": 2025, "source_doc": "示例-国家基本医疗保险目录（部署侧替换）",
     "evidence_class": "simulated"},
]


def build_default_registry():
    """默认登记表：三条示例条目（simulated 标注，指针纪律）。"""
    reg = DrugRegistry()
    for e in SAMPLE_ENTRIES:
        reg.register(e)
    return reg


def audit():
    """总闸快照：report-only。"""
    return {"seal": SEAL, "ring": CHAIN_POSITION["ring"],
            "fields": list(CATALOG_FIELDS),
            "has_dose_field": False,
            "classes": list(VALID_CLASSES) + ["unknown(未登记)"],
            "redline": list(REDLINE_ACTIONS),
            "sample_entries": len(SAMPLE_ENTRIES),
            "sample_evidence": "simulated（部署侧替换为官方目录 measured）",
            "lookup_mode": "exact（精确查表，非向量）",
            "zero_dose": True, "neural": False}

