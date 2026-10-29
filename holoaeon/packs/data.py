# -*- coding: utf-8 -*-
"""领域包：数据处理（data）。CSV 概况、缺失、统计、归一化、离群。"""
from __future__ import annotations

import csv
import io
import math
from typing import List

from .base import DomainPack, RoleSpec, SkillSpec, WorkflowSpec


def _parse(csv_text: str):
    rows = list(csv.reader(io.StringIO(csv_text)))
    if not rows:
        return [], []
    return rows[0], rows[1:]


def _numeric_columns(header, rows):
    cols = {}
    for ci, name in enumerate(header):
        vals = []
        for r in rows:
            if ci < len(r) and r[ci] != "":
                try:
                    vals.append(float(r[ci]))
                except ValueError:
                    vals = []
                    break
        if vals:
            cols[name] = vals
    return cols


def csv_profile(csv_text: str) -> dict:
    """CSV 概况：行列数、列类型、数值列。"""
    header, rows = _parse(csv_text)
    nums = _numeric_columns(header, rows)
    return {"columns": len(header), "rows": len(rows),
            "header": header,
            "numeric_columns": list(nums.keys()),
            "categorical_columns": [h for h in header if h not in nums]}


def missing_report(csv_text: str) -> dict:
    """每列缺失值统计。"""
    header, rows = _parse(csv_text)
    out = {}
    for ci, name in enumerate(header):
        miss = sum(1 for r in rows if ci >= len(r) or r[ci] == "")
        out[name] = {"missing": miss,
                     "rate": round(miss / len(rows), 3) if rows else 0}
    return out


def basic_stats(csv_text: str) -> dict:
    """数值列描述统计（均值/方差/最小最大）。"""
    header, rows = _parse(csv_text)
    nums = _numeric_columns(header, rows)
    out = {}
    for name, vals in nums.items():
        mean = sum(vals) / len(vals)
        var = sum((x - mean) ** 2 for x in vals) / len(vals)
        out[name] = {"count": len(vals), "mean": round(mean, 3),
                     "std": round(math.sqrt(var), 3),
                     "min": min(vals), "max": max(vals)}
    return out


def normalize_column(values: str) -> dict:
    """min-max 归一化（values 为逗号分隔数字）。"""
    nums = [float(x) for x in values.split(",") if x.strip()]
    if not nums:
        return {"values": []}
    lo, hi = min(nums), max(nums)
    rng = hi - lo
    norm = [round((x - lo) / rng, 4) if rng else 0 for x in nums]
    return {"min": lo, "max": hi, "normalized": norm}


def outlier_detect(values: str) -> dict:
    """IQR 离群点检测。"""
    nums = sorted(float(x) for x in values.split(",") if x.strip())
    if len(nums) < 4:
        return {"outliers": []}
    q1 = nums[len(nums) // 4]
    q3 = nums[(3 * len(nums)) // 4]
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    out = [x for x in nums if x < lo or x > hi]
    return {"bounds": [round(lo, 3), round(hi, 3)], "outliers": out}


class DataPack(DomainPack):
    key = "data"
    name = "数据处理"
    description = "数据清洗、概况、统计、归一化与离群检测。"
    skills = [
        SkillSpec("csv_profile", csv_profile, "CSV 概况",
                  ["csv", "profile"], {"csv_text": "str"}),
        SkillSpec("missing_report", missing_report, "缺失值报告",
                  ["missing", "clean"], {"csv_text": "str"}),
        SkillSpec("basic_stats", basic_stats, "描述统计",
                  ["stats", "eda"], {"csv_text": "str"}),
        SkillSpec("normalize_column", normalize_column, "归一化",
                  ["normalize", "scale"], {"values": "str"}),
        SkillSpec("outlier_detect", outlier_detect, "离群检测",
                  ["outlier", "iqr"], {"values": "str"}),
    ]
    roles = [
        RoleSpec("data_cleaner", "清洗与缺失",
                 ["missing_report", "normalize_column", "outlier_detect"]),
        RoleSpec("data_analyst", "分析与统计",
                 ["basic_stats", "csv_profile"]),
        RoleSpec("data_reporter", "报告",
                 ["csv_profile", "basic_stats"]),
    ]
    workflows = [
        WorkflowSpec("data_pipeline",
                     ["data_cleaner", "data_analyst", "data_reporter"],
                     "清洗→分析→报告"),
    ]
