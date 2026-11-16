# -*- coding: utf-8 -*-
"""世殊医道慢病管理智能引擎架构模块（SSYD Chronic Engine, ring 12）。

定位
----
本模块是 ``holoaeon`` 的**模块级旁挂**（不是第 10 个 pack，不改 25/47/9，也不改
``spec.VERSION``）。它接在 ring 11 ``phc_chronic_engine`` 之后，负责“中西医融合的
慢病风险分层 → 五维病机候选 → 用药安全提示 → MDT 路由 → 随访/转诊回流”这一条
确定性架构链；公共卫生建档、A/B/C/D 服务包与容量测算仍归 ring 11。

边界（硬）
----------
* 零诊断：输出只称“风险分层/证候候选/需医师复核”，不落疾病诊断。
* 零处方、零剂量：不出现任何可执行中药或西药剂量、用法、疗程。
* 零像素：舌/耳/眼等图像只收 SHA256 指针 + 结构化自述，原始字节不进入引擎状态。
* 零网络：纯标准库、全离线、确定性；同输入两次运行结果逐字节一致。
* E14 急症直通线下急诊/120；E13 妊娠与高风险组合只做教育性提示。
* 最终裁决权在碳基执业医师，本模块不替代面诊。

证据口径：``evidence_class=simulated``，仿真 ≠ 证明。
封存密令：潮起开门，潮落闭嘴。
"""
from __future__ import annotations

import hashlib
import json

SEAL = "潮起开门，潮落闭嘴"
ENGINE_ID = "SG-SSYD-CHRONIC-ENGINE-ARCH-V1.0"
VERSION = "1.0.0"
EVIDENCE_CLASS = "simulated"
FINAL_AUTHORITY = "碳基执业医师终裁"

#: 编排链位置：ring 11 公共卫生慢病引擎之后，ring 12 为世殊医道中西医融合慢病域。
CHAIN_POSITION = {
    "ring": 12,
    "name": "世殊医道·中西医融合慢病管理域（慢病管理智能引擎）",
    "upstream": ("phc_chronic_engine", "academic_gate", "shengui_gate", "pharma_gate"),
    "downstream": ("followup_reflux", "mdt_router", "physician_final"),
    "relation_to_phc": "ring 11 管公共卫生服务包与容量；ring 12 管风险-证候-用药安全-随访闭环，不重复建档",
}

#: 八病种域。followup_per_year 为最低随访次数，不代表治疗方案。
DISEASE_REGISTRY = {
    "htn": {
        "cn": "高血压",
        "system": "cardio_cerebro",
        "tcm_domain": "眩晕/头痛",
        "followup_per_year": 4,
        "annual_exam": True,
        "key_metrics": ("sbp", "dbp", "egfr", "urine_albumin"),
        "red_flags": ("hypertensive_emergency", "chest_pain", "consciousness_change"),
    },
    "t2dm": {
        "cn": "2型糖尿病",
        "system": "endocrine",
        "tcm_domain": "消渴",
        "followup_per_year": 4,
        "annual_exam": True,
        "key_metrics": ("fpg", "hba1c", "egfr", "urine_albumin", "foot_exam"),
        "red_flags": ("glucose_crisis", "consciousness_change"),
    },
    "copd": {
        "cn": "慢性阻塞性肺疾病",
        "system": "immune",
        "tcm_domain": "肺胀",
        "followup_per_year": 4,
        "annual_exam": True,
        "key_metrics": ("fev1", "symptom_score", "exacerbation_count"),
        "red_flags": ("rest_dyspnea", "consciousness_change"),
    },
    "chd": {
        "cn": "冠心病",
        "system": "cardio_cerebro",
        "tcm_domain": "胸痹",
        "followup_per_year": 4,
        "annual_exam": True,
        "key_metrics": ("bp", "ldl", "egfr", "symptom_class"),
        "red_flags": ("chest_pain", "rest_dyspnea", "consciousness_change"),
    },
    "ckd": {
        "cn": "慢性肾脏病",
        "system": "endocrine",
        "tcm_domain": "水肿/关格",
        "followup_per_year": 4,
        "annual_exam": True,
        "key_metrics": ("egfr", "urine_albumin", "potassium", "bp"),
        "red_flags": ("major_bleeding", "consciousness_change", "rest_dyspnea"),
    },
    "stroke": {
        "cn": "卒中后二级预防",
        "system": "cardio_cerebro",
        "tcm_domain": "中风",
        "followup_per_year": 4,
        "annual_exam": True,
        "key_metrics": ("bp", "ldl", "nihss", "adl"),
        "red_flags": ("fast_positive", "consciousness_change", "chest_pain"),
    },
    "ra": {
        "cn": "类风湿关节炎",
        "system": "immune",
        "tcm_domain": "痹证",
        "followup_per_year": 4,
        "annual_exam": True,
        "key_metrics": ("das28", "crp", "esr", "liver_renal"),
        "red_flags": ("major_bleeding", "consciousness_change"),
    },
    "oa": {
        "cn": "膝骨关节炎",
        "system": "ortho",
        "tcm_domain": "骨痹",
        "followup_per_year": 2,
        "annual_exam": True,
        "key_metrics": ("pain_score", "function_score", "bmi"),
        "red_flags": ("major_bleeding",),
    },
}

#: 世殊医道五维病机轴。只作学术候选，不与西医诊断做 1:1 等价。
PATTERN_AXIS = {
    "xu": {
        "cn": "虚",
        "signs": ("乏力", "气短", "自汗", "食少", "腰膝酸软"),
        "note": "本虚可为气血阴阳不足；与多种慢病多对多，不落单一诊断。",
    },
    "yu": {
        "cn": "郁",
        "signs": ("情志抑郁", "胸胁胀满", "善太息", "烦躁", "脉弦"),
        "note": "气机郁滞可见于多病种；情绪量表与证候分开记录。",
    },
    "yu_blood": {
        "cn": "瘀",
        "signs": ("痛有定处", "面色晦暗", "肌肤甲错", "舌质紫暗", "脉涩"),
        "note": "瘀阻为慢病常见兼证；抗凝/抗血小板人群须先由医师评估出血风险。",
    },
    "han": {
        "cn": "寒",
        "signs": ("畏寒", "肢冷", "遇寒加重", "便溏", "脉紧"),
        "note": "寒热两极须与感染、甲状腺功能、外周循环等现代评估并行。",
    },
    "shi": {
        "cn": "湿",
        "signs": ("头身困重", "苔腻", "腹胀", "水肿", "大便黏滞"),
        "note": "湿/痰湿可见于代谢、呼吸、肾脏等多域；不做单病种绑定。",
    },
}

#: 疾病 → 病机候选（多对多，置信度仅为学术权重，不是诊断概率）。
DISEASE_PATTERN_LINKS = {
    "htn": (("xu", 0.55), ("yu", 0.60), ("yu_blood", 0.50), ("shi", 0.45)),
    "t2dm": (("xu", 0.60), ("shi", 0.65), ("yu_blood", 0.40), ("yu", 0.35)),
    "copd": (("xu", 0.70), ("shi", 0.55), ("yu_blood", 0.40), ("han", 0.35)),
    "chd": (("yu_blood", 0.65), ("xu", 0.55), ("han", 0.45), ("yu", 0.40)),
    "ckd": (("xu", 0.65), ("shi", 0.60), ("yu_blood", 0.45), ("han", 0.30)),
    "stroke": (("yu_blood", 0.70), ("xu", 0.55), ("shi", 0.50), ("yu", 0.35)),
    "ra": (("shi", 0.60), ("han", 0.55), ("yu_blood", 0.50), ("xu", 0.45)),
    "oa": (("xu", 0.55), ("han", 0.50), ("yu_blood", 0.45), ("shi", 0.35)),
}

EVIDENCE_TAGS = {
    "classic": "【原典记载】",
    "theory": "【学派理论推演】",
    "simulation": "【模型仿真假设】",
    "modern": "【现代医学参考】",
}

#: E14 急症熔断：任一为真即直通线下急诊/120。
EMERGENCY_FLAGS = {
    "chest_pain": "急性胸痛或胸闷持续不缓解",
    "fast_positive": "突发面瘫/上肢无力/言语含糊（FAST 任一项）",
    "rest_dyspnea": "静息状态下呼吸困难或血氧持续下降",
    "consciousness_change": "意识改变、晕厥或抽搐",
    "hypertensive_emergency": "血压极高伴胸痛/呼吸困难/神经症状",
    "glucose_crisis": "高血糖危象表现（深大呼吸、脱水、意识异常）",
    "major_bleeding": "大量出血、黑便呕血或难以止住的出血",
}
EMERGENCY_ACTION = "立即线下急诊或拨打 120"
EMERGENCY_DO_NOT = "不展开线上自救、不自行加减或停用任何药物"

#: 风险规则 SR01–SR14。points 只用于分层，不代表病情严重度的完整判断。
RISK_RULES = (
    {"id": "SR01", "desc": "收缩压≥180 或舒张压≥110", "points": 30},
    {"id": "SR02", "desc": "收缩压160–179 或舒张压100–109", "points": 20},
    {"id": "SR03", "desc": "收缩压140–159 或舒张压90–99", "points": 10},
    {"id": "SR04", "desc": "空腹血糖≥11.1 或随机血糖≥13.9", "points": 25},
    {"id": "SR05", "desc": "HbA1c≥9.0%", "points": 20},
    {"id": "SR06", "desc": "eGFR<30", "points": 30},
    {"id": "SR07", "desc": "eGFR 30–59", "points": 15},
    {"id": "SR08", "desc": "任一 E14 急症标志", "points": 40},
    {"id": "SR09", "desc": "靶器官损害或明确并发症", "points": 20},
    {"id": "SR10", "desc": "当前吸烟", "points": 8},
    {"id": "SR11", "desc": "BMI≥28", "points": 8},
    {"id": "SR12", "desc": "合并慢病≥2 种", "points": 10},
    {"id": "SR13", "desc": "年龄≥65 岁", "points": 5},
    {"id": "SR14", "desc": "妊娠或备孕（E13 复核标志）", "points": 10},
)

GRADE_THRESHOLDS = ((70, "IV"), (50, "III"), (30, "II"), (0, "I"))


def grade_of(score):
    """分数 → 风险档；边界值归入更高档。"""
    for floor, grade in GRADE_THRESHOLDS:
        if score >= floor:
            return grade
    return "I"


def emergency_triage(profile):
    """E14 急症判定。返回结构固定，便于上游直接熔断。"""
    hits = [key for key in EMERGENCY_FLAGS if bool(profile.get(key))]
    return {
        "e14": bool(hits),
        "hits": [{"key": k, "cn": EMERGENCY_FLAGS[k]} for k in hits],
        "action": EMERGENCY_ACTION if hits else "",
        "do_not": EMERGENCY_DO_NOT if hits else "",
        "evidence_tag": EVIDENCE_TAGS["modern"],
    }


def assess_risk(profile):
    """确定性风险分层：返回命中规则、分数与档位。"""
    sbp = profile.get("sbp")
    dbp = profile.get("dbp")
    fpg = profile.get("fpg")
    hba1c = profile.get("hba1c")
    egfr = profile.get("egfr")
    hits = []

    def add(rule_id, points, detail=""):
        hits.append({"id": rule_id, "points": points, "detail": detail})

    if sbp is not None and dbp is not None:
        if sbp >= 180 or dbp >= 110:
            add("SR01", 30)
        elif sbp >= 160 or dbp >= 100:
            add("SR02", 20)
        elif sbp >= 140 or dbp >= 90:
            add("SR03", 10)
    if fpg is not None and fpg >= 11.1:
        add("SR04", 25)
    if hba1c is not None and hba1c >= 9.0:
        add("SR05", 20)
    if egfr is not None:
        if egfr < 30:
            add("SR06", 30)
        elif egfr < 60:
            add("SR07", 15)
    if emergency_triage(profile)["e14"]:
        add("SR08", 40)
    if profile.get("target_organ_damage"):
        add("SR09", 20)
    if profile.get("smoking"):
        add("SR10", 8)
    if profile.get("bmi") is not None and profile["bmi"] >= 28:
        add("SR11", 8)
    if int(profile.get("comorbidities") or 0) >= 2:
        add("SR12", 10)
    if profile.get("age") is not None and profile["age"] >= 65:
        add("SR13", 5)
    if profile.get("pregnant"):
        add("SR14", 10)

    score = min(100, sum(h["points"] for h in hits))
    grade = "IV" if emergency_triage(profile)["e14"] else grade_of(score)
    return {
        "score": score,
        "grade": grade,
        "hits": hits,
        "grade_thresholds": [{"floor": f, "grade": g} for f, g in GRADE_THRESHOLDS],
        "acute_direct_iv": bool(emergency_triage(profile)["e14"]),
        "evidence_tag": EVIDENCE_TAGS["simulation"],
        "note": "风险分数是确定性规则求和，不是预后预测；须由医师结合面诊复核。",
    }


def syndrome_candidates(diseases):
    """疾病集合 → 五维病机候选（多对多，带置信度与证据层）。"""
    if not diseases:
        raise ValueError("diseases must be non-empty")
    merged = {}
    for d in diseases:
        if d not in DISEASE_PATTERN_LINKS:
            raise ValueError("unknown disease: %r" % (d,))
        for pattern, conf in DISEASE_PATTERN_LINKS[d]:
            merged[pattern] = max(merged.get(pattern, 0.0), conf)
    ordered = sorted(merged.items(), key=lambda kv: (-kv[1], kv[0]))
    return {
        "patterns": [
            {
                "key": key,
                "cn": PATTERN_AXIS[key]["cn"],
                "confidence": conf,
                "signs": list(PATTERN_AXIS[key]["signs"]),
                "note": PATTERN_AXIS[key]["note"],
            }
            for key, conf in ordered
        ],
        "mapping": "many_to_many",
        "no_one_to_one_equivalence": True,
        "evidence_tag": EVIDENCE_TAGS["theory"],
        "final_authority": FINAL_AUTHORITY,
    }


def medication_safety(profile, meds=None):
    """用药安全提示（教育性，零剂量、零停药建议）。

    只报“需要处方医师复核的风险组合”，不给替代药、不给剂量、不建议自行停换。
    """
    meds = [str(m).strip().lower() for m in (meds or []) if str(m).strip()]
    flags = []

    def flag(code, cn, reason):
        flags.append({"code": code, "cn": cn, "reason": reason,
                      "action": "由处方医师复核；不自行停药、换药或加减量",
                      "evidence_tag": EVIDENCE_TAGS["modern"]})

    raas = {"acei", "arb", "ace inhibitor", "angiotensin receptor blocker"}
    nsaid = {"nsaid", "ibuprofen", "diclofenac", "naproxen", "celecoxib"}
    anticoag = {"warfarin", "doac", "apixaban", "rivaroxaban", "dabigatran", "edoxaban"}
    if len(raas & set(meds)) >= 2:
        flag("M01", "RAAS 双重阻断", "ACEI 与 ARB 联用属于重复阻断，需专科复核。")
    if nsaid & set(meds):
        egfr = profile.get("egfr")
        if (egfr is not None and egfr < 60) or profile.get("ckd"):
            flag("M02", "NSAID × 肾功能下降", "肾功能下降人群使用 NSAID 需评估肾损伤与出血风险。")
        if anticoag & set(meds):
            flag("M03", "NSAID × 抗凝", "抗凝药与 NSAID 并用增加出血风险，需处方医师复核。")
    if "metformin" in meds and profile.get("egfr") is not None and profile["egfr"] < 30:
        flag("M04", "二甲双胍 × 重度肾功能下降", "eGFR<30 时需由医师按说明书与指南重新评估。")
    if profile.get("pregnant"):
        flag("M05", "E13 妊娠期用药复核", "妊娠或备孕期任何慢病用药均需产科与专科共同评估；本引擎零剂量。")
    if profile.get("liver_impairment"):
        flag("M06", "肝功能不全复核", "肝功能不全时多种慢病用药需重新评估，须由处方医师决定。")
    return {
        "flags": flags,
        "zero_dose": True,
        "zero_prescription": True,
        "no_self_discontinuation": True,
        "evidence_tag": EVIDENCE_TAGS["modern"],
    }


def followup_plan(profile, diseases, control_ok=True, acute_referral=False):
    """随访计划：基础年随访 + 未达标 2 周复访 + 急性转诊 2 周回流追踪。"""
    if not diseases:
        raise ValueError("diseases must be non-empty")
    items = []
    for d in diseases:
        if d not in DISEASE_REGISTRY:
            raise ValueError("unknown disease: %r" % (d,))
        reg = DISEASE_REGISTRY[d]
        per_year = int(reg["followup_per_year"])
        interval = max(30, int(round(365 / per_year)))
        items.append({
            "disease": d,
            "cn": reg["cn"],
            "followup_per_year": per_year,
            "interval_days": interval,
            "annual_exam": bool(reg["annual_exam"]),
            "metrics": list(reg["key_metrics"]),
        })
    actions = []
    if not control_ok:
        actions.append({"when": "now+14d", "action": "未达标复访（2 周内）",
                        "evidence_tag": EVIDENCE_TAGS["modern"]})
    if acute_referral:
        actions.append({"when": "now+14d", "action": "急性转诊回流追踪（2 周内）",
                        "reflux_note": "mobius/LIN-E01", "evidence_tag": EVIDENCE_TAGS["modern"]})
    return {
        "items": items,
        "actions": actions,
        "annual_exam_required": any(i["annual_exam"] for i in items),
        "evidence_tag": EVIDENCE_TAGS["modern"],
    }


MDT_DEPARTMENTS = {
    "htn": ("心血管内科", "全科/慢病门诊"),
    "t2dm": ("内分泌科", "全科/慢病门诊"),
    "copd": ("呼吸内科", "全科/慢病门诊"),
    "chd": ("心血管内科", "全科/慢病门诊"),
    "ckd": ("肾内科", "全科/慢病门诊"),
    "stroke": ("神经内科", "康复医学科"),
    "ra": ("风湿免疫科", "全科/慢病门诊"),
    "oa": ("骨科", "康复医学科"),
}


def convene_mdt(diseases, patterns=None):
    """MDT 路由：科室 + 中医证候席位；意见槽保持空白，医师终裁。"""
    depts = []
    for d in diseases:
        if d not in MDT_DEPARTMENTS:
            raise ValueError("unknown disease: %r" % (d,))
        for dept in MDT_DEPARTMENTS[d]:
            if dept not in depts:
                depts.append(dept)
    tcm_seats = [PATTERN_AXIS[p]["cn"] for p in (patterns or ()) if p in PATTERN_AXIS]
    return {
        "departments": depts,
        "tcm_pattern_seats": tcm_seats,
        "opinion_slots": [{"seat": "待填", "opinion": "", "physician": "", "signed": False}
                          for _ in range(len(depts) + len(tcm_seats))],
        "final_authority": FINAL_AUTHORITY,
        "note": "意见槽空白是结构性要求：引擎不代替任何科室表态。",
    }


MODALITIES = {
    "lab_report": {"kind": "text", "pixel": False},
    "physical_exam": {"kind": "text", "pixel": False},
    "imaging_report": {"kind": "text", "pixel": False},
    "pulse": {"kind": "structured", "pixel": False},
    "tongue_photo": {"kind": "image", "pixel": True},
    "ear_photo": {"kind": "image", "pixel": True},
    "eye_photo": {"kind": "image", "pixel": True},
    "wearable": {"kind": "structured", "pixel": False},
}


class Envelope:
    """多模态信封：图像只留 SHA256 与结构化自述，字节不外泄。"""

    @staticmethod
    def create(modality, payload=None, structured=None):
        if modality not in MODALITIES:
            return {"ok": False, "reason": "unknown_modality"}
        spec = MODALITIES[modality]
        if spec["pixel"]:
            if not structured:
                return {"ok": False, "reason": "image_requires_structured"}
            if payload is None:
                return {"ok": False, "reason": "image_requires_pointer"}
            raw = payload if isinstance(payload, bytes) else str(payload).encode("utf-8")
            return {
                "ok": True,
                "modality": modality,
                "sha256": hashlib.sha256(raw).hexdigest(),
                "structured": dict(structured),
                "pixel_retained": False,
                "raw_bytes_retained": False,
                "evidence_tag": EVIDENCE_TAGS["modern"],
            }
        return {
            "ok": True,
            "modality": modality,
            "structured": dict(structured or {}),
            "pixel_retained": False,
            "evidence_tag": EVIDENCE_TAGS["modern"],
        }


class AuditChain:
    """轻量 SHA 审计链：任一环被改，后续校验即断。"""

    def __init__(self):
        self.items = []

    def append(self, event, data):
        prev = self.items[-1]["digest"] if self.items else "0" * 64
        body = json.dumps({"event": event, "data": data, "prev": prev},
                          ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
        self.items.append({"event": event, "data": data, "prev": prev, "digest": digest})
        return digest

    def verify(self):
        prev = "0" * 64
        for item in self.items:
            body = json.dumps({"event": item["event"], "data": item["data"], "prev": prev},
                              ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            if hashlib.sha256(body.encode("utf-8")).hexdigest() != item["digest"]:
                return False
            prev = item["digest"]
        return True

    def tail(self):
        return self.items[-1]["digest"] if self.items else ""


#: 容量测算默认口径（3 万常住人口；仅用于资源估算，不是流行病学结论）。
CAPACITY_DEFAULTS = {
    "population": 30000,
    "adult35_ratio": 0.55,
    "prevalence": {
        "htn": 0.25, "t2dm": 0.10, "copd": 0.03, "chd": 0.02,
        "ckd": 0.08, "stroke": 0.015, "ra": 0.005, "oa": 0.10,
    },
}


def capacity_plan(population=None, adult35_ratio=None, prevalence=None):
    """年度随访工作量估算：人数 × 年随访次数。"""
    pop = int(population if population is not None else CAPACITY_DEFAULTS["population"])
    ratio = float(adult35_ratio if adult35_ratio is not None
                  else CAPACITY_DEFAULTS["adult35_ratio"])
    prev = dict(CAPACITY_DEFAULTS["prevalence"])
    if prevalence:
        prev.update(prevalence)
    adults = int(round(pop * ratio))
    rows = []
    total_visits = 0
    for d, p in sorted(prev.items()):
        count = int(round(adults * float(p)))
        visits = count * int(DISEASE_REGISTRY[d]["followup_per_year"])
        total_visits += visits
        rows.append({"disease": d, "patients": count,
                     "followup_per_year": DISEASE_REGISTRY[d]["followup_per_year"],
                     "annual_visits": visits})
    return {
        "population": pop,
        "adult35_ratio": ratio,
        "adults35": adults,
        "rows": rows,
        "total_patients": sum(r["patients"] for r in rows),
        "total_annual_visits": total_visits,
        "evidence_tag": EVIDENCE_TAGS["simulation"],
        "note": "默认患病率为教学示例参数，不是本地流行病学实测；落地须替换为本地口径。",
    }


class Engine:
    """单入口编排：急症 → 风险 → 证候 → 用药 → MDT → 随访。"""

    def __init__(self):
        self.audit = AuditChain()

    def run(self, profile, diseases, meds=None, control_ok=True,
            acute_referral=False, entries=None):
        if not isinstance(profile, dict):
            raise ValueError("profile must be a dict")
        if not diseases:
            raise ValueError("diseases must be non-empty")
        for d in diseases:
            if d not in DISEASE_REGISTRY:
                raise ValueError("unknown disease: %r" % (d,))
        patient_ref = hashlib.sha256(
            str(profile.get("patient_id") or "anonymous").encode("utf-8")).hexdigest()[:16]

        triage = emergency_triage(profile)
        risk = assess_risk(profile)
        patterns = syndrome_candidates(diseases)
        med = medication_safety(profile, meds)
        mdt = convene_mdt(diseases, [p["key"] for p in patterns["patterns"]])
        follow = followup_plan(profile, diseases, control_ok=control_ok,
                               acute_referral=acute_referral)
        envelope = []
        for e in (entries or []):
            envelope.append(Envelope.create(e.get("modality"), e.get("payload"),
                                            e.get("structured")))

        self.audit.append("intake", {"patient_ref": patient_ref,
                                     "diseases": list(diseases),
                                     "entry_count": len(envelope)})
        self.audit.append("triage", {"e14": triage["e14"], "grade": risk["grade"]})

        report = {
            "engine_id": ENGINE_ID,
            "version": VERSION,
            "chain_ring": CHAIN_POSITION["ring"],
            "evidence_class": EVIDENCE_CLASS,
            "patient_ref": patient_ref,
            "diseases": [{"code": d, "cn": DISEASE_REGISTRY[d]["cn"]} for d in diseases],
            "emergency": triage,
            "risk": risk,
            "syndrome": patterns,
            "medication_safety": med,
            "mdt": mdt,
            "followup": follow,
            "envelope": envelope,
            "zero_dose": True,
            "zero_diagnosis": True,
            "zero_pixels": True,
            "zero_network": True,
            "final_authority": FINAL_AUTHORITY,
            "audit_tail": self.audit.tail(),
            "audit_ok": self.audit.verify(),
            "disclaimers": [
                "本报告为学术/教学用结构化建议，不构成诊断、处方或治疗方案。",
                "风险分数与证候候选均须执业医师结合面诊、检验与影像复核。",
                "出现 E14 急症标志时，仅执行线下急诊/120 指引，不展开线上自救。",
                "所有结论 evidence_class=simulated；仿真 ≠ 证明。",
            ],
            "seal": SEAL,
        }
        if triage["e14"]:
            report["decision"] = "E14_EMERGENCY_DIRECT"
        else:
            report["decision"] = "PHYSICIAN_REVIEW_REQUIRED"
        return report


def audit():
    """模块自述快照（可被上游健康检查调用）。"""
    return {
        "engine_id": ENGINE_ID,
        "version": VERSION,
        "chain_position": dict(CHAIN_POSITION),
        "diseases": sorted(DISEASE_REGISTRY),
        "disease_count": len(DISEASE_REGISTRY),
        "patterns": sorted(PATTERN_AXIS),
        "pattern_count": len(PATTERN_AXIS),
        "risk_rules": [r["id"] for r in RISK_RULES],
        "risk_rule_count": len(RISK_RULES),
        "emergency_flags": sorted(EMERGENCY_FLAGS),
        "modalities": sorted(MODALITIES),
        "zero_dose": True,
        "zero_diagnosis": True,
        "zero_pixels": True,
        "zero_network": True,
        "evidence_class": EVIDENCE_CLASS,
        "final_authority": FINAL_AUTHORITY,
        "seal": SEAL,
    }
