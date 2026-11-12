# -*- coding: utf-8 -*-
"""
mechanism_bearers —— 机制承载对账（V64 · 挂账清零批 · 7 位未覆盖真关闭）
================================================================================
挂账原文（V63 回执 honest_boundaries）：
  「V63 机床资产 14 位 × 25 机制，直连 18/25，7 位机制未被任何机床资产承载：
    C1 自组织耗散 / R2 曼陀罗一拖八 / R5 卡尔曼滤波 / R6 贝叶斯干涉 /
    R7 希尔伯特空间 / R8 耗散度量 / X2 108641 活跃节点共振。」

本批查实的根因（不是拍脑袋，是逐符号验过的）：
  **这 7 位在仓内一直有真实实现体，缺的是「承载者登记」**——
    · holoaeon/packs/topology_resonance_pack.py（1265 行，第 12 扩展包）里
      真正写出了 mandala_fanout / kalman_state / bayesian_guard /
      hilbert_project / dissipation_measure 五个函数，以及
      ACTIVE_NODES=108641、EMERGENCE_THRESHOLD=108641、
      DISSIPATION_ENTROPY_MAX=0.95、MANDALA_TOTAL=9 四个常量；
    · holoaeon/topology_runtime.py 里真正写出了 StateReducer / Checkpoint /
      CircuitBreaker / DissipationMonitor 四个类（耗散监控的运行时载体）。

  所以「未覆盖」的准确含义是：**V63 的 14 位机床资产清单里没有这两位承载者**，
  而不是仓内没有实现。本模块把这件事登记成可复算的对账，而不是把 18/25
  改写成 25/25 糊过去。

双口径（分开报、不混）：
  · lathe_direct  —— 由 14 位机床资产直接承载的机制数（V63 台账复算，不变）；
  · bearer_only   —— 由机制侧承载者（本模块登记的模块+符号）承载的机制数；
  · total_unique  —— 两口径并集去重后的机制覆盖数（目标 25/25）。

纪律：
  · 校验一律 **import 真模块 + getattr 真符号**，不数关键词、不猜名字；
  · 函数须 callable，常量须等于登记值（值不符即 FAIL，不宽容）；
  · 不改 V63 的 data/forge_bureau_meridian.json（历史台账保持可复算）。
"""
from __future__ import annotations

import importlib
import io
import json
import os
from typing import Any, Dict, List, Optional

SEAL = "潮起开门，潮落闭嘴"
SCHEMA_VERSION = "MECHANISM-BEARERS-v1.0"
DATA_OUT_NAME = "mechanism_bearers.json"
FORGE_LEDGER = os.path.join("data", "forge_bureau_meridian.json")

# 7 位挂账机制的承载登记（module/symbol/kind/expected 全部实测可验）
BEARERS: tuple = (
    {
        "mech": "C1", "name": "自组织耗散", "layer": "耗散验证",
        "module": "holoaeon.topology_runtime", "symbol": "DissipationMonitor",
        "kind": "class",
        "why": "运行时的耗散监控器：状态归约/检查点/熔断/耗散四件套里专管耗散观测",
        "doc_quote": "topology_runtime（StateReducer+Checkpoint+CircuitBreaker+DissipationMonitor）",
        "extra": {"module": "holoaeon.packs.topology_resonance_pack", "symbol": "dissipation_measure"},
    },
    {
        "mech": "R2", "name": "曼陀罗一拖八", "layer": "经络子机制",
        "module": "holoaeon.packs.topology_resonance_pack", "symbol": "mandala_fanout",
        "kind": "function",
        "why": "1 中心 → 8 方位扩散并聚合（MANDALA_TOTAL=9 与之一致）",
        "doc_quote": "曼陀罗一拖八：1 中心 → 8 方位扩散，结果聚合。",
        "extra": {"module": "holoaeon.packs.topology_resonance_pack", "symbol": "MANDALA_TOTAL", "expected": 9},
    },
    {
        "mech": "R5", "name": "卡尔曼滤波", "layer": "经络子机制",
        "module": "holoaeon.packs.topology_resonance_pack", "symbol": "kalman_state",
        "kind": "function",
        "why": "多源状态估计 + 不确定性传播（卡尔曼状态融合）",
        "doc_quote": "卡尔曼滤波状态融合：多源状态估计 + 不确定性传播。",
        "extra": None,
    },
    {
        "mech": "R6", "name": "贝叶斯干涉", "layer": "经络子机制",
        "module": "holoaeon.packs.topology_resonance_pack", "symbol": "bayesian_guard",
        "kind": "function",
        "why": "基于历史拦截率的概率拦截（同族异名：碳基称干涉，仓内实名守卫）",
        "doc_quote": "贝叶斯推理守卫：基于历史拦截率的概率拦截。",
        "extra": None,
    },
    {
        "mech": "R7", "name": "希尔伯特空间", "layer": "经络子机制",
        "module": "holoaeon.packs.topology_resonance_pack", "symbol": "hilbert_project",
        "kind": "function",
        "why": "有限维 → 近似无限维的希尔伯特空间投影",
        "doc_quote": "希尔伯特计算空间投影：有限维 → 近似无限维。",
        "extra": None,
    },
    {
        "mech": "R8", "name": "耗散度量", "layer": "经络子机制",
        "module": "holoaeon.packs.topology_resonance_pack", "symbol": "dissipation_measure",
        "kind": "function",
        "why": "系统熵 + 秩序/失序平衡的耗散结构度量",
        "doc_quote": "耗散结构度量：系统熵 + 秩序/失序平衡。",
        "extra": {"module": "holoaeon.packs.topology_resonance_pack",
                  "symbol": "DISSIPATION_ENTROPY_MAX", "expected": 0.95},
    },
    {
        "mech": "X2", "name": "108641 活跃节点共振", "layer": "矩阵",
        "module": "holoaeon.packs.topology_resonance_pack", "symbol": "ACTIVE_NODES",
        "kind": "constant", "expected": 108641,
        "why": "活跃节点与涌现阈值同值 108641（共振对数超阈值→涌现）",
        "doc_quote": "ACTIVE_NODES=108641 / EMERGENCE_THRESHOLD=108641",
        "extra": {"module": "holoaeon.packs.topology_resonance_pack",
                  "symbol": "EMERGENCE_THRESHOLD", "expected": 108641},
    },
)

# 25 位机制全表（与 meridian_link.KERNEL_MECHANISMS 对齐，用于并集口径）
MECHANISM_IDS: tuple = (
    "A1", "A2", "X1", "X2", "M01", "M02", "M03", "M04", "M05", "M06", "M07",
    "M08", "M09", "M10", "M11", "C1", "C2", "R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8",
)


# ---------------------------------------------------------------------------
# 一、符号级校验（import + getattr，不数关键词）
# ---------------------------------------------------------------------------

def _load_symbol(module_name: str, symbol: str) -> Any:
    mod = importlib.import_module(module_name)
    return getattr(mod, symbol)


def _verify_one(item: Dict[str, Any]) -> Dict[str, Any]:
    problems: List[str] = []
    try:
        target = _load_symbol(item["module"], item["symbol"])
    except Exception as exc:  # 承载者无法导入=最硬的失败
        return {"mech": item["mech"], "ok": False,
                "problems": ["{}.{} 不可导入：{}".format(item["module"], item["symbol"], exc)]}
    kind = item.get("kind")
    if kind in ("function", "class"):
        if not callable(target):
            problems.append("{}.{} 不可调用（{}）".format(item["module"], item["symbol"], type(target).__name__))
    elif kind == "constant":
        if not isinstance(target, int) or target != item.get("expected"):
            problems.append("{}.{} != {}（实 {!r}）".format(
                item["module"], item["symbol"], item.get("expected"), target))
    else:
        problems.append("未知承载类型：{}".format(kind))

    extra = item.get("extra")
    extra_ok = None
    if extra:
        try:
            ex = _load_symbol(extra["module"], extra["symbol"])
            if "expected" in extra:
                extra_ok = (ex == extra["expected"]) and not isinstance(ex, bool)
                if not extra_ok:
                    problems.append("附加承载 {}.{} != {}（实 {!r}）".format(
                        extra["module"], extra["symbol"], extra.get("expected"), ex))
            else:
                extra_ok = callable(ex)
                if not extra_ok:
                    problems.append("附加承载 {}.{} 不可调用".format(extra["module"], extra["symbol"]))
        except Exception as exc:
            extra_ok = False
            problems.append("附加承载不可导入：{}".format(exc))

    return {"mech": item["mech"], "name": item["name"], "layer": item["layer"],
            "module": item["module"], "symbol": item["symbol"], "kind": kind,
            "why": item["why"], "doc_quote": item["doc_quote"],
            "extra_ok": extra_ok, "ok": not problems, "problems": problems}


def check_bearers() -> Dict[str, Any]:
    """7 位承载者逐项符号级校验。"""
    rows = [_verify_one(b) for b in BEARERS]
    bad = [r for r in rows if not r["ok"]]
    return {
        "schema": SCHEMA_VERSION,
        "bearers": len(BEARERS),
        "verified": len(rows) - len(bad),
        "failed": [r["mech"] for r in bad],
        "verdict": "PASS" if not bad else "FAIL",
        "rows": rows,
    }


# ---------------------------------------------------------------------------
# 二、双口径覆盖（lathe_direct / bearer_only / total_unique）
# ---------------------------------------------------------------------------

def lathe_direct_mechanisms(ledger_path: Optional[str] = None) -> Dict[str, Any]:
    """从 V63 的 350 格机床台账复算「被机床资产直连的机制数」（不硬写 18）。"""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = ledger_path or os.path.join(root, FORGE_LEDGER)
    if not os.path.exists(path):
        return {"ok": False, "problems": ["台账不在位：{}".format(path)], "mechanisms": []}
    with io.open(path, encoding="utf-8") as f:
        data = json.load(f)
    cells = data.get("table") or []
    if not isinstance(cells, list):
        cells = []
    linked: Dict[str, int] = {}
    unlinked: Dict[str, int] = {}
    for c in cells:
        mech = c.get("mech")
        if not mech:
            continue
        if c.get("state") == "linked":
            linked[mech] = linked.get(mech, 0) + 1
        else:
            unlinked[mech] = unlinked.get(mech, 0) + 1
    direct = sorted(m for m in MECHANISM_IDS if linked.get(m, 0) > 0)
    return {"ok": True, "cells": len(cells), "mechanisms": direct,
            "count": len(direct), "linked_cells": sum(linked.values())}


def coverage(ledger_path: Optional[str] = None) -> Dict[str, Any]:
    """双口径覆盖报告——两口径分开报，并集才算「全机制有承载」。"""
    rep = check_bearers()
    direct = lathe_direct_mechanisms(ledger_path)
    bearer_ids = sorted({r["mech"] for r in rep["rows"] if r["ok"]})
    union = sorted(set(direct.get("mechanisms", [])) | set(bearer_ids))
    problems: List[str] = []
    if rep["verdict"] != "PASS":
        problems.append("承载者校验未过：{}".format(rep["failed"]))
    if not direct.get("ok"):
        problems.append("机床台账复算失败：{}".format(direct.get("problems")))
    unknown = [m for m in union if m not in MECHANISM_IDS]
    if unknown:
        problems.append("口径外机制：{}".format(unknown))
    return {
        "schema": SCHEMA_VERSION,
        "lathe_direct": {"count": direct.get("count", 0), "mechanisms": direct.get("mechanisms", [])},
        "bearer_only": {"count": len(bearer_ids), "mechanisms": bearer_ids},
        "total_unique": {"count": len(union), "mechanisms": union},
        "full": len(union) == len(MECHANISM_IDS),
        "verdict": "PASS" if (not problems and len(union) == len(MECHANISM_IDS)) else "FAIL",
        "problems": problems,
        "note": "两口径分开报、不混：机床直连 与 机制侧承载 各自计数，并集=全机制有承载",
    }


def build_ledger(ledger_path: Optional[str] = None) -> Dict[str, Any]:
    rep = check_bearers()
    cov = coverage(ledger_path)
    return {
        "schema": SCHEMA_VERSION,
        "batch": "V64-HANGOVER-ZERO",
        "dom": "25 位机制承载对账（7 位挂账真关闭）",
        "hangover_origin": "V63 receipt honest_boundaries：直连 18/25、7 位未覆盖",
        "root_cause": ("7 位并非仓内无实现——topology_resonance_pack 实现了其中 6 位，"
                       "topology_runtime 承载 C1；缺的是 V63 机床资产清单未登记这两位承载者"),
        "bearers": rep,
        "coverage": cov,
        "seal": SEAL,
    }


def write_ledger(path: Optional[str] = None) -> str:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = path or os.path.join(root, "data", DATA_OUT_NAME)
    payload = build_ledger()
    io.open(out, "w", encoding="utf-8", newline="\n").write(
        json.dumps(payload, ensure_ascii=False, indent=1) + "\n")
    return out


def main(argv: Optional[List[str]] = None) -> int:
    import sys
    argv = list(argv if argv is not None else sys.argv[1:])
    if not argv:
        print("用法：python -m holoaeon.mechanism_bearers check | coverage | ledger")
        return 1
    cmd = argv[0]
    if cmd == "check":
        rep = check_bearers()
        print(json.dumps(rep, ensure_ascii=False, indent=1))
        return 0 if rep["verdict"] == "PASS" else 1
    if cmd == "coverage":
        cov = coverage()
        print(json.dumps(cov, ensure_ascii=False, indent=1))
        return 0 if cov["verdict"] == "PASS" else 1
    if cmd == "ledger":
        print("台账已写：{}".format(write_ledger()))
        return 0
    print("未知命令：{}".format(cmd))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
