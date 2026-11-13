# -*- coding: utf-8 -*-
"""V76 双口径收口（Dual Caliber）—— 磁吸附「旧口径」与「桥接口径」并存对照。

为什么要并存而不是替换（实测，非推测）：
    V69 的语义桥（`prehistory_semantic_bridge`）只加两侧显式词表、不动打分函数，
    桥后同一批 15 个样本里 **12 个归属改变**（80%）。若把这组分数直接覆盖进主路
    `forge_bureau.forge_absorb`，V72 已推送的 18 仓归属账会被整体推翻，且主路
    输出一变，下游一切按归属写的断言都得重评。

本模块做什么：**主路一字不动**，把两口径并到一个可调用的入口里：
    · `absorb_dual(spec)` —— 一次给 base / bridge 两套归属 + 逐条归因
    · `build_ledger()`    —— 出 15 样本差异台账（带自摘要）
    · `verify(ledger)`    —— 七面可失败判据（改一个字就红）

三条硬边界（写进字段，不靠嘴说）：
    1. base 必须逐字段等于主路现跑 —— 本模块不重算、不改写、不缓存主路口径；
    2. bridge 只在词表命中时才有归因证据；命中不到就是真空，登记不装已修复；
    3. 零 LLM、零网络、零随机、零新增依赖：同输入同输出。

封口令：潮起开门，潮落闭嘴。
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Sequence

from .forge_bureau import forge_absorb
from .prehistory_semantic_bridge import (KNOWN_VACUUM, SAMPLES, bridged_absorb)

SCHEMA = "DUAL-CALIBER-v1"
SEAL = "潮起开门，潮落闭嘴"

DECISIONS = ("bridge_adopted", "base_kept", "vacuum_kept")

BOUNDARIES: List[str] = [
    "主路 forge_absorb 零改动：本模块只读调用，不写入、不替换、不缓存其结果",
    "bridge 只加文本（两侧显式词表），ngram_dice 与 tie-break 一字未动",
    "真空样本（名字无领域线索）桥后仍 0 分，登记 KNOWN_VACUUM，不伪装已修复",
    "18 仓远端重推属外部动作：本批只出确认表，停在 LOCAL_READY",
    "base 与 bridge 并列登记，任何一方都不是唯一真值，裁决权在碳基",
]


# ------------------------------------------------------------------ 单条对照
def _base_fields(rec: Dict[str, Any]) -> Dict[str, Any]:
    """主路口径的四字段（唯一来源：forge_absorb 自己的返回值）。"""
    a = rec["absorbed_into"]
    return {"repo": a["repo"], "cang": a["cang"],
            "domain": a["domain"], "score": a["score"]}


def _bridge_fields(rec: Dict[str, Any]) -> Dict[str, Any]:
    b = rec["bridged"]
    return {"repo": b["repo"], "cang": b["cang"],
            "domain": b["domain"], "score": b["score"]}


def _decide(base: Dict[str, Any], bridge: Dict[str, Any],
            terms: Sequence[str]) -> str:
    """三态判定：真空 / 有词证且换仓 / 同仓（只是分升）。"""
    if bridge["score"] == 0.0:
        return "vacuum_kept"
    if bridge["repo"] != base["repo"] and terms:
        return "bridge_adopted"
    return "base_kept"


def absorb_dual(spec: Dict[str, Any]) -> Dict[str, Any]:
    """主路可调用的双口径入口：base 逐字段等于 forge_absorb，bridge 另成一列。"""
    base_rec = forge_absorb(spec)
    bridge_rec = bridged_absorb(spec)
    base = _base_fields(base_rec)
    bridge = _bridge_fields(bridge_rec)
    terms = list(bridge_rec["card"]["terms"])
    decision = _decide(base, bridge, terms)
    return {
        "name": spec.get("name", ""),
        "base": base,
        "bridge": bridge,
        "delta": {"repo_changed": bridge["repo"] != base["repo"],
                  "score_delta": round(bridge["score"] - base["score"], 4)},
        "decision": decision,
        "attribution": {"matched_terms": terms,
                        "labels": list(bridge_rec["card"]["labels"]),
                        "evidence": bridge_rec["card"]["evidence"],
                        "vacuum": bool(bridge_rec["card"]["vacuum"])},
        "still_zero": bridge["score"] == 0.0,
    }


# ------------------------------------------------------------------ 台账
def _canonical_digest(payload: Dict[str, Any]) -> str:
    """自摘要：剔掉 self_digest 本身后规范化 JSON 取 sha256 前 16。"""
    body = {k: v for k, v in payload.items() if k != "self_digest"}
    text = json.dumps(body, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _totals(rows: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "samples": len(rows),
        "zero_before": sum(1 for r in rows if r["base"]["score"] == 0.0),
        "zero_after": sum(1 for r in rows if r["still_zero"]),
        "changed": sum(1 for r in rows if r["delta"]["repo_changed"]),
        "unchanged": sum(1 for r in rows if not r["delta"]["repo_changed"]),
        "bridge_adopted": sum(1 for r in rows if r["decision"] == "bridge_adopted"),
        "base_kept": sum(1 for r in rows if r["decision"] == "base_kept"),
        "vacuum_kept": sum(1 for r in rows if r["decision"] == "vacuum_kept"),
    }


def build_ledger(samples: Sequence[str] = SAMPLES) -> Dict[str, Any]:
    """15 样本双口径台账（确定性：同样本集同字节）。"""
    rows = [absorb_dual({"name": n, "description": "", "tags": []})
            for n in samples]
    ledger = {
        "schema": SCHEMA,
        "as_of": "2026-11-13",
        "calibers": ["base", "bridge"],
        "samples": rows,
        "totals": _totals(rows),
        "known_vacuum": list(KNOWN_VACUUM),
        "boundaries": list(BOUNDARIES),
        "seal": SEAL,
    }
    ledger["self_digest"] = _canonical_digest(ledger)
    return ledger


# ------------------------------------------------------------------ 七面判据
def verify(ledger: Dict[str, Any], samples: Sequence[str] = SAMPLES) -> Dict[str, Any]:
    """七面可失败判据：任一面不成立即 FAIL（mismatch 逐条给证据）。"""
    problems: List[str] = []
    faces: Dict[str, bool] = {}

    rows = ledger.get("samples") or []
    if len(rows) != len(samples):
        problems.append("样本条数 %d != 传入 %d" % (len(rows), len(samples)))
    if not rows:
        return {"verdict": "FAIL", "faces": {}, "mismatch":
                ["台账无样本"] + problems,
                "digest": ledger.get("self_digest"), "problems": problems}

    # F1/F2/F3：逐条与现跑重算对账（两读者原则）
    for i, name in enumerate(samples):
        fresh = absorb_dual({"name": name, "description": "", "tags": []})
        row = rows[i] if i < len(rows) else {}
        if row.get("name") != name:
            problems.append("F1 行序错位 #%d：%r != %r" % (i, row.get("name"), name))
        if row.get("base") != fresh["base"]:
            problems.append("F1 base 漂移 %s" % name[:24])
        if row.get("bridge") != fresh["bridge"]:
            problems.append("F2 bridge 漂移 %s" % name[:24])
        if row.get("decision") != fresh["decision"]:
            problems.append("F3 判定漂移 %s" % name[:24])
        if row.get("decision") == "bridge_adopted" and not row["attribution"]["matched_terms"]:
            problems.append("F3 采纳无词证 %s" % name[:24])
        if row.get("delta") != fresh["delta"]:
            problems.append("F3 差值漂移 %s" % name[:24])
    faces["F1_base_readonly_equal"] = not any(p.startswith("F1") for p in problems)
    faces["F2_bridge_rerun_equal"] = not any(p.startswith("F2") for p in problems)
    faces["F3_attribution_traceable"] = not any(p.startswith("F3") for p in problems)

    # F4：零分真空必须逐个在册
    stray = [r["name"] for r in rows
             if r["still_zero"] and not any(v in r["name"] for v in KNOWN_VACUUM)]
    if stray:
        problems.append("F4 未登记真空 %d 条：%s" % (len(stray), "、".join(s[:16] for s in stray)))
    faces["F4_vacuum_registered"] = not stray

    # F5：确定性（同输入两跑同摘要）
    again = build_ledger(list(samples))
    faces["F5_deterministic_digest"] = again["self_digest"] == ledger["self_digest"]
    if not faces["F5_deterministic_digest"]:
        problems.append("F5 重现摘要不一致")

    # F6：totals 与逐条统计一致
    faces["F6_totals_consistent"] = ledger.get("totals") == _totals(rows)
    if not faces["F6_totals_consistent"]:
        problems.append("F6 totals 与逐条不符")

    # F7：自摘要（改一个字即红）
    expect = _canonical_digest(ledger)
    faces["F7_self_digest"] = ledger.get("self_digest") == expect
    if not faces["F7_self_digest"]:
        problems.append("F7 自摘要不符（台账被改过）")

    verdict = "PASS" if all(faces.values()) else "FAIL"
    return {"verdict": verdict, "faces": faces, "problems": problems,
            "mismatch": [] if verdict == "PASS" else problems,
            "digest": ledger.get("self_digest"), "schema": SCHEMA}


# ------------------------------------------------------------------ CLI
def main(argv: Sequence[str] | None = None) -> int:
    argv = list(argv if argv is not None else [])
    action = argv[0] if argv else "verify"
    if action not in ("verify", "report", "build"):
        print("usage: python -m holoaeon.dual_caliber [verify|report|build]")
        return 2
    ledger = build_ledger()
    if action == "build":
        print(json.dumps(ledger, ensure_ascii=False, indent=1))
        return 0
    if action == "report":
        t = ledger["totals"]
        print("双口径台账：%s" % ledger["self_digest"])
        print("  样本 %d / 旧口径零分 %d / 桥后零分 %d / 换仓 %d / 同仓 %d" % (
            t["samples"], t["zero_before"], t["zero_after"], t["changed"], t["unchanged"]))
        print("  判定：adopted %d / base_kept %d / vacuum %d" % (
            t["bridge_adopted"], t["base_kept"], t["vacuum_kept"]))
        for r in ledger["samples"]:
            print("  %-8s %-28s %s(%.4f) -> %s(%.4f) %s" % (
                r["decision"], r["name"][:28], r["base"]["repo"], r["base"]["score"],
                r["bridge"]["repo"], r["bridge"]["score"],
                "、".join(r["attribution"]["matched_terms"]) or "-"))
        return 0
    rep = verify(ledger)
    print("verdict:", rep["verdict"], "| digest:", rep["digest"])
    for k, v in rep["faces"].items():
        print("  %-28s %s" % (k, "OK" if v else "FAIL"))
    for p in rep["problems"]:
        print("  !", p)
    return 0 if rep["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
