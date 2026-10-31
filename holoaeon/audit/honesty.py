# -*- coding: utf-8 -*-
"""
VERAX · 诚实契约校验（honesty）
================================================================================
两条诚实红线，作用于"回执对象"而不是散文：
  H1（红）：evidence_class = measured，但缺少 measure_source / measure_ts
  H2（黄）：回执对象缺少 evidence_class 字段
只扫 VERAX 自己的 receipts/reports，不碰业务包。

保护哪条立身原则：诚实纪律（仿真是仿真）、可审计（不合规可计数）。
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List

from .receipt import EVIDENCE_CLASSES, Receipt


def inspect_receipt(obj: Dict[str, Any], source: str = "") -> List[Dict[str, str]]:
    """检查一条回执对象，返回问题列表。"""
    problems: List[Dict[str, str]] = []
    if "evidence_class" not in obj:
        problems.append({"rule": "H2", "severity": "yellow",
                         "source": source, "detail": "回执缺少 evidence_class"})
        return problems
    cls = obj.get("evidence_class")
    if cls not in EVIDENCE_CLASSES:
        problems.append({"rule": "H1", "severity": "red", "source": source,
                         "detail": "未知证据分级 %r" % (cls,)})
        return problems
    if cls == "measured":
        missing = [need for need in ("measure_source", "measure_ts")
                   if not obj.get(need)]
        if missing:
            problems.append({"rule": "H1", "severity": "red", "source": source,
                             "detail": "measured 缺少 %s" % "/".join(missing)})
    else:
        if obj.get("measure_source") is not None:
            problems.append({"rule": "H2", "severity": "yellow", "source": source,
                             "detail": "%s 不应携带 measure_source" % cls})
    return problems


def scan_receipts(root: str) -> Dict[str, Any]:
    """扫描目录内 *.jsonl / *.json 回执对象。"""
    problems: List[Dict[str, str]] = []
    files = 0
    receipts = 0
    if not os.path.isdir(root):
        return {"files": 0, "receipts": 0, "h1": 0, "h2": 0,
                "problems": [], "clean": True}
    for dirpath, dirnames, filenames in os.walk(root):
        # 跳过缓存、演示用例目录（_cases 里是刻意构造的红/黄用例，不能污染正式报告）
        dirnames[:] = [d for d in dirnames
                       if d not in ("__pycache__", "_cases")]
        if "__pycache__" in dirpath:
            continue
        for name in filenames:
            if not (name.endswith(".jsonl") or name.endswith(".json")):
                continue
            path = os.path.join(dirpath, name)
            files += 1
            with open(path, "r", encoding="utf-8") as handle:
                for lineno, line in enumerate(handle, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except ValueError:
                        continue
                    if not isinstance(obj, dict):
                        continue
                    receipts += 1
                    problems.extend(inspect_receipt(
                        obj, "%s:%d" % (os.path.basename(path), lineno)))

    h1 = sum(1 for p in problems if p["rule"] == "H1")
    h2 = sum(1 for p in problems if p["rule"] == "H2")
    return {"files": files, "receipts": receipts, "h1": h1, "h2": h2,
            "problems": problems, "clean": (h1 == 0 and h2 == 0)}


def compliance(receipts: List[Receipt]) -> Dict[str, Any]:
    """按证据分级汇总合规情况。"""
    summary = {name: 0 for name in EVIDENCE_CLASSES}
    summary["noncompliant"] = 0
    for item in receipts:
        summary[item.evidence_class] = summary.get(item.evidence_class, 0) + 1
        if item.validate():
            summary["noncompliant"] += 1
    return summary
