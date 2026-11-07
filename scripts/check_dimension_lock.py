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

# 冻结快照项：文档态，随版本演进，不参与运行态校验
# 与 EXPECTED（运行态锁死项）性质不同：
#   EXPECTED 的值永远不变（如 spec_version=0.9.1）
#   FROZEN_SNAPSHOT 的值会随 DOC_VERSION 演进（如 spec_doc_version 0.9.4→0.9.18）
# 校验策略：只读取并打印差异，不判 FAIL——演进是受控的，碳基终审
FROZEN_SNAPSHOT = {
    "spec_doc_version": {
        "frozen_value": "0.9.4",
        "current_source": "holoaeon.spec.DOC_VERSION",
        "reason": "文档版本号，随批次演进，不参与运行态锁死校验",
        "note_cmd": "python -c \"from holoaeon.spec import DOC_VERSION; print(DOC_VERSION)\"",
    },
    "holoaeon_domain_packs": {
        "frozen_value": 9,
        "current_source": "holoaeon.packs.PACK_ORDER len",
        "reason": "九领域包数，V1 起未变",
        "note_cmd": "python -c \"from holoaeon.packs import PACK_ORDER; print(len(PACK_ORDER))\"",
    },
    "holoaeon_extra_packs": {
        "frozen_value": 9,
        "current_source": "holoaeon.packs.EXTRA_PACK_ORDER len",
        "reason": "扩展包数，随批次演进，以命令回读为准，不记时点快照",
        "note_cmd": "python -c \"from holoaeon.packs import EXTRA_PACK_ORDER; print(len(EXTRA_PACK_ORDER))\"",
    },
    "holoaeon_unittests": {
        "frozen_value": "34/21/5",
        "current_source": "tests/ + tests/v3 + tests/verax 实跑计数",
        "reason": "三套测试计数，随批次演进，以命令回读为准，不记时点快照",
        "note_cmd": "python -c \"import subprocess,sys;r=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests'],capture_output=True,text=True);print([l for l in r.stderr.splitlines() if l.startswith('Ran')][-1])\"",
    },
}


def read_frozen_snapshot_current():
    """读取冻结快照项的当前值（只读，不校验）。"""
    current = {}
    try:
        from holoaeon.spec import DOC_VERSION
        current["spec_doc_version"] = DOC_VERSION
    except Exception:
        current["spec_doc_version"] = "(读取失败)"
    try:
        from holoaeon.packs import PACK_ORDER, EXTRA_PACK_ORDER
        current["holoaeon_domain_packs"] = len(PACK_ORDER)
        current["holoaeon_extra_packs"] = len(EXTRA_PACK_ORDER)
    except Exception:
        current["holoaeon_domain_packs"] = "(读取失败)"
        current["holoaeon_extra_packs"] = "(读取失败)"
    # unittest 计数不在此自动跑（避免拖慢校验），只标注"见实测"
    current["holoaeon_unittests"] = "(见实测，不自动跑)"
    return current


def print_frozen_snapshot():
    """打印冻结快照项当前值与冻结值的差异（仅供碳基终审视察，不判 FAIL）。"""
    current = read_frozen_snapshot_current()
    print("[SNAPSHOT] 冻结快照项（不参与校验，仅供碳基终审视察）：")
    for key, meta in FROZEN_SNAPSHOT.items():
        cur = current.get(key, "(未知)")
        frozen = meta["frozen_value"]
        if key == "holoaeon_unittests":
            note = "← 见 README 实测值"
        elif str(cur) == str(frozen):
            note = "← 一致"
        else:
            note = "← 演进（正常）"
        print(f"  - {key}: 冻结={frozen}  当前={cur}  {note}")


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
    print_frozen_snapshot()
    return 0


if __name__ == "__main__":
    sys.exit(main())
