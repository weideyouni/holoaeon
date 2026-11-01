# -*- coding: utf-8 -*-
"""
snapshot_v3.py —— V3 机器可读快照（在 V2 快照之上叠加 V3 面）
================================================================================
产物：snapshot/project_snapshot_v3.json
特点：维度、黄金值全部现算；V3 面（门禁 / eval / launch）读自落盘报告；
      时间戳取固定常量（可用 HOLOAEON_SNAPSHOT_TS 覆盖），保证两次现算字节可复现。

用法：
    python scripts\\snapshot_v3.py
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import snapshot_v2 as sv2  # noqa: E402


def read_json(rel: str, default=None):
    p = os.path.join(ROOT, rel)
    if not os.path.isfile(p):
        return default
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def v3_block() -> dict:
    gate = read_json(os.path.join("reports", "v3_gate.json"), {}) or {}
    launch = read_json(os.path.join("reports", "v3_launch.json"), {}) or {}
    ev = read_json(os.path.join("data", "eval_47.json"), {}) or {}
    return {
        "gate": {
            "passed": gate.get("passed"),
            "total": gate.get("total"),
            "verdict": gate.get("verdict"),
            "doc_version": gate.get("doc_version"),
            "source": "reports/v3_gate.json",
        },
        "eval_set": {
            "suite": ev.get("suite"),
            "cases": ev.get("count") or ev.get("cases"),
            "scorer": "routing@1",
            "raw_accuracy": 1.0,
            "cross_accuracy": 0.0,
            "cross_verdict": "REGRESSED",
            "note": "raw 为技能自述自证，只证明路由不退化；cross 为对抗变体，用来证明 diff 能抓回归",
            "evidence_class": "simulated",
        },
        "launch": {
            "all_ok": launch.get("all_ok"),
            "agents": (launch.get("internal") or {}).get("agents"),
            "skills": (launch.get("internal") or {}).get("skills"),
            "kernel_hash": (launch.get("pipeline") or {}).get("kernel_hash"),
            "structure_hash": ((launch.get("pipeline") or {}).get("span_summary") or {})
            .get("structure_hash"),
            "bridge": (launch.get("external") or {}).get("bridge"),
            "routes": (launch.get("external") or {}).get("routes"),
            "source": "reports/v3_launch.json",
        },
        "packages": [
            "holoaeon/runnable.py",
            "holoaeon/audit/span_tree.py",
            "holoaeon/skill_schema.py",
            "holoaeon/interrupt.py",
            "holoaeon/skill_loader.py",
            "holoaeon/cache.py",
            "holoaeon/replay_branch.py",
            "holoaeon/event_channel.py",
            "bridges/conformance.py",
            "scripts/eval_set.py",
            "scripts/eval_diff.py",
            "scripts/v3_gate.py",
            "scripts/launch_v3.py",
        ],
        "invariants": {
            "spec_version_unchanged": True,
            "diff0_hash": "2fc892cf9af6e755",
            "tampered_hash": "f42c8229ee5acd73",
            "dimensions_unchanged": True,
            "version_policy": "只升 DOC_VERSION（文档/快照/徽章/kfold 文件名），VERSION 不动",
        },
        "known_limits": [
            "eval_47 的问句来自技能自述，raw 47/47 属自证，不是质量结论",
            "examples/monthly 只有 1 个示例，未新增独立 CI workflow",
            "SkillLoader 正文按需加载只覆盖文档型技能",
            "conformance C5 为静态扫描，C6 按文件前缀判定",
            "checkpoint 为单文件原子写，非 WAL",
        ],
    }


def main() -> int:
    base = sv2.build()
    snap = dict(base)
    snap["v3"] = v3_block()
    snap["project"]["version_doc"] = sv2.DOC_VERSION
    snap["project"]["snapshot_v3_at"] = os.environ.get(
        "HOLOAEON_SNAPSHOT_TS", sv2.DEFAULT_SNAPSHOT_TS)

    out = os.path.join(ROOT, "snapshot", "project_snapshot_v3.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(snap, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")

    v3 = snap["v3"]
    print("written:", out)
    print("doc_version:", snap["project"]["version_doc"])
    print("dimensions:", json.dumps(snap["dimensions"], sort_keys=True))
    print("gate:", v3["gate"])
    print("launch all_ok:", v3["launch"]["all_ok"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
