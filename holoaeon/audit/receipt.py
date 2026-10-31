# -*- coding: utf-8 -*-
"""
VERAX · 诚实契约（receipt）
================================================================================
每条回执必须声明 evidence_class ∈ {simulated, measured, third_party}。
默认 simulated；measured 必须携带来源与测量时刻，否则判为不合规。

保护哪条立身原则：诚实纪律（仿真不写成实测）、可审计（来源可回溯）。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

EVIDENCE_CLASSES = ("simulated", "measured", "third_party")


@dataclass
class Receipt:
    receipt_id: str
    source_path: str
    evidence_class: str = "simulated"
    measure_source: Optional[str] = None
    measure_ts: Optional[str] = None
    reprocore: Dict[str, Any] = field(default_factory=dict)
    physical: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> List[str]:
        """返回问题列表；空列表表示合规。"""
        problems: List[str] = []
        if self.evidence_class not in EVIDENCE_CLASSES:
            problems.append("未知证据分级：%s" % self.evidence_class)
        if self.evidence_class == "measured":
            if not self.measure_source:
                problems.append("measured 缺少 measure_source")
            if not self.measure_ts:
                problems.append("measured 缺少 measure_ts")
        else:
            if self.measure_source is not None:
                problems.append("%s 不应携带 measure_source" % self.evidence_class)
            if self.measure_ts is not None:
                problems.append("%s 不应携带 measure_ts" % self.evidence_class)
        return problems

    def to_dict(self) -> Dict[str, Any]:
        return {
            "receipt_id": self.receipt_id,
            "source_path": self.source_path,
            "evidence_class": self.evidence_class,
            "measure_source": self.measure_source,
            "measure_ts": self.measure_ts,
            "reprocore": self.reprocore,
            "physical": self.physical,
        }
