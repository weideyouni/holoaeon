#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""B0 基线冻结 · 维度锁读取校验（HoloAeon 侧）

按 AGENT_FEED_V4_REHAB_FUSION_20261102.md §4 SOP-1 第 4 步要求：
"两侧单测各加一条断言读它"——本脚本读 reports/dimension_lock.json，
对 12 维度锁做断言；不并入 unittest discover，避免破坏 34/21/5 与 v3_gate 32 项锁。
完美判据：退出码 0 = PASS。

密令：潮起开门，潮落闭嘴。evidence_class=simulated，仿真≠证明，碳基终裁。
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOCK = os.path.join(ROOT, "reports", "dimension_lock.json")

EXPECTED = {
    "lock_id": "B0-LOCK-V2.0-REHAB-FUSION",
    "spec_version": "0.9.1",
    "diff0_hash": "2fc892cf9af6e755",
    "tamper_sensitive_hash": "f42c8229ee5acd73",
    "holoaeon_agents": 25,
    "holoaeon_skills": 47,
    "holoaeon_selftest_groups": 25,
    "ivsa_selftest_groups": 21,
    "skill_matrix_runtime_skills": 1199,
}


def main():
    if not os.path.isfile(LOCK):
        print(f"[FAIL] dimension_lock.json 不存在: {LOCK}")
        return 1
    with open(LOCK, "r", encoding="utf-8") as f:
        d = json.load(f)

    fails = []
    if d.get("lock_id") != EXPECTED["lock_id"]:
        fails.append(f"lock_id={d.get('lock_id')} != {EXPECTED['lock_id']}")
    if d.get("evidence_class") != "simulated":
        fails.append("evidence_class != simulated")
    dims = {x["name"]: x["value"] for x in d.get("dimensions", [])}
    if len(d.get("dimensions", [])) != 12:
        fails.append(f"dimensions count={len(d.get('dimensions', []))} != 12")
    for k, v in EXPECTED.items():
        if k == "lock_id":
            continue
        if dims.get(k) != v:
            fails.append(f"{k}={dims.get(k)!r} != {v!r}")
    gates = d.get("audit", {}).get("seven_gates", [])
    if len(gates) != 7:
        fails.append(f"seven_gates count={len(gates)} != 7")
    if d.get("audit", {}).get("violation_count") != 0:
        fails.append("violation_count != 0")

    if fails:
        print("[FAIL] dimension_lock 校验失败：")
        for x in fails:
            print("  -", x)
        return 1
    print("[PASS] dimension_lock.json 12 维度 + 7 闸 + 0 violation 全部一致")
    print("       diff0_hash=2fc892cf9af6e755 tamper=f42c8229ee5acd73 spec_version=0.9.1")
    return 0


if __name__ == "__main__":
    sys.exit(main())
