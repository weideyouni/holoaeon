# -*- coding: utf-8 -*-
"""V4.2-B1 · 三场卡电场补齐（只读查询 + 红线闸）。

三场 = 磁场 / 电场 / 液态场。本模块只做三件事：
1. 把 `data/three_field_cards.json` 读成确定性查询接口（场、卡、缺口、覆盖）。
2. 对空白卡执行「结构化补齐」：参数维度 + 证据等级 none + 检索计划 + 顶替禁令。
   补齐 ≠ 补出证据：结论字段恒为 none，等原始文献回填。
3. 红线闸：剂量数值、疗效承诺、接设备/下参数处方一律拦下，不降级口径。

本模块不 import ivsa、不联网、不接设备、不写回客仓。
"""
from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, "data", "three_field_cards.json")

FIELD_ORDER = ("magnetic", "electric", "liquid")

DOSE_PATTERN = re.compile(r"\d+\s*(?:mg|毫克|ml|毫升|μg|ug|g/日|克/日|IU|单位)")
EFFICACY_WORDS = ("治愈", "总有效", "显效率", "推荐使用", "替代药物", "可停药")
DEVICE_WORDS = ("开机参数", "设置参数", "调参", "输出强度设为", "接设备")
CLINICAL_WORDS = ("诊断为", "确诊为", "治疗方案是", "处方为")


def load(path: Optional[str] = None) -> Dict[str, Any]:
    with open(path or DATA, "r", encoding="utf-8") as f:
        return json.load(f)


class ThreeField(object):
    def __init__(self, doc: Dict[str, Any]) -> None:
        self.doc = doc
        self.fields_list = [f["id"] for f in doc["fields"]]
        self.anchors = {f["id"]: list(f.get("anchors") or []) for f in doc["fields"]}
        self.cards = list(doc["cards"])

    @classmethod
    def load(cls, path: Optional[str] = None) -> "ThreeField":
        return cls(load(path))

    # -- 查询 -------------------------------------------------------------
    def fields(self) -> List[str]:
        return list(self.fields_list)

    def name_cn(self, field: str) -> str:
        for f in self.doc["fields"]:
            if f["id"] == field:
                return f["name_cn"]
        return ""

    def cards_of(self, field: str) -> List[Dict[str, Any]]:
        if field not in self.fields_list:
            raise KeyError("未知场：%s，可选：%s" % (field, self.fields_list))
        return [c for c in self.cards if c["field"] == field]

    def card(self, card_id: str) -> Optional[Dict[str, Any]]:
        for c in self.cards:
            if c["card_id"] == card_id:
                return dict(c)
        return None

    def counts(self) -> Dict[str, int]:
        return {f: len(self.cards_of(f)) for f in self.fields_list}

    def tier_split(self) -> Dict[str, int]:
        out: Dict[str, int] = {}
        for c in self.cards:
            key = c.get("evidence_tier", "none")
            out[key] = out.get(key, 0) + 1
        return dict(sorted(out.items()))

    def gaps(self) -> List[Dict[str, Any]]:
        return [dict(c) for c in self.cards
                if str(c.get("evidence_tier")) == "none" or c.get("status", "").startswith("gap")]

    def coverage(self) -> Dict[str, Any]:
        gaps = self.gaps()
        structured = [c["card_id"] for c in gaps if c.get("status") == "gap_structured"]
        return {
            "fields": len(self.fields_list),
            "cards": len(self.cards),
            "counts": self.counts(),
            "tier_split": self.tier_split(),
            "gap_cards": [c["card_id"] for c in gaps],
            "gap_structured": structured,
            "gap_pending_plan": [c["card_id"] for c in gaps
                                 if "retrieval_plan" not in c or not c.get("retrieval_plan")],
        }

    def route(self, text: str) -> List[str]:
        text = (text or "").lower()
        hits = []
        for index, field in enumerate(self.fields_list):
            score = sum(1 for a in self.anchors[field] if a.lower() in text)
            if score:
                hits.append((-score, index, field))
        hits.sort()
        return [f for _, _, f in hits]

    def describe(self, card_id: str) -> Dict[str, Any]:
        """把一张卡读成推理侧可用的描述：只陈述登记事实与护栏，不给结论。"""
        card = self.card(card_id)
        if card is None:
            return {"card_id": card_id, "status": "unknown"}
        decision = "none（证据等级 %s，未回填结论）" % card.get("evidence_tier")
        return {
            "card_id": card["card_id"],
            "field": card["field"],
            "field_cn": self.name_cn(card["field"]),
            "modality": card.get("modality"),
            "parameter_frame": list(card.get("parameter_frame") or []),
            "evidence_tier": card.get("evidence_tier"),
            "evidence_note": card.get("evidence_note"),
            "decision": decision,
            "guard": card.get("guard"),
            "retrieval_plan": card.get("retrieval_plan"),
            "evidence_class": "simulated",
        }

    # -- 红线闸 -----------------------------------------------------------
    def guard(self, text: str) -> Dict[str, Any]:
        text = text or ""
        dose = DOSE_PATTERN.findall(text)
        efficacy = [w for w in EFFICACY_WORDS if w in text]
        device = [w for w in DEVICE_WORDS if w in text]
        clinical = [w for w in CLINICAL_WORDS if w in text]
        reasons = []
        if dose:
            reasons.append("dose_value")
        if efficacy:
            reasons.append("efficacy_claim")
        if device:
            reasons.append("device_command")
        if clinical:
            reasons.append("clinical_decision")
        return {"blocked": bool(reasons), "reasons": reasons,
                "dose_hits": dose[:3], "efficacy_hits": efficacy[:3],
                "device_hits": device[:3], "clinical_hits": clinical[:3],
                "action": "拒绝：不写剂量、不承诺疗效、不接设备、不做诊断" if reasons else "pass"}

    def verify(self) -> Dict[str, Any]:
        cov = self.coverage()
        return {
            "registry_id": self.doc.get("registry_id"),
            "fields": cov["fields"],
            "cards": cov["cards"],
            "counts": cov["counts"],
            "gaps": len(cov["gap_cards"]),
            "gap_structured": len(cov["gap_structured"]),
            "pending_plan": cov["gap_pending_plan"],
            "ok": (cov["fields"] == 3 and all(v > 0 for v in cov["counts"].values())
                   and len(cov["gap_structured"]) == len(cov["gap_cards"])),
        }
