# -*- coding: utf-8 -*-
"""B6 · 重启一致测试（SOP-9 第 2 步）

「重启」是真重启：父进程现场训练并把权重落盘，子进程（独立解释器、独立内存）
只从盘上加载后复原赫布场，两边各算一遍 top-k 文本视图，要求**逐字相等**。
本脚本用 subprocess 起子进程——脚本层可以，包内（holoaeon/）不用，红线扫描只看包体。

用法：
    python scripts/test_restart_consistency.py                 # 用 data/hebbian_store.json
    python scripts/test_restart_consistency.py --json reports/b6_restart.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from holoaeon.fusion_upgrade import hebbian_store as HS  # noqa: E402
from holoaeon.skill_matrix.runtime import MatrixRuntime  # noqa: E402

INDEX = os.path.join(ROOT, "data", "skill_matrix_index.json")
STORE = os.path.join(ROOT, "data", "hebbian_store.json")

CHILD = r'''
import hashlib, json, os, sys
store, root = sys.argv[1], sys.argv[2]
sys.path.insert(0, root)
from holoaeon.fusion_upgrade import hebbian_store as HS
from holoaeon.skill_matrix.mech import HebbianField
doc = HS.load(store)
f = HebbianField(HS.DECAY)
HS.restore(doc, f)
seeds = doc["topk"]["seeds"]
k = doc["topk"]["k"]
text = HS.topk_text(f, seeds, k)
edges = HS.canonical([{"a": e["a"], "b": e["b"], "w": e["w"]} for e in doc["edges"]])
print(json.dumps({
    "pid": os.getpid(),
    "verify_ok": HS.verify(doc)["ok"],
    "edges_sha256": hashlib.sha256(edges.encode("utf-8")).hexdigest(),
    "topk_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
    "topk_text": text,
    "edges_restored": len(f._w),
}, ensure_ascii=False))
'''


def _frozen_text(doc):
    lines = []
    for row in doc["topk"]["rows"]:
        for nb in row["neighbors"]:
            lines.append("%s\t%s\t%.5f" % (row["seed"], nb["name"], nb["w"]))
        if not row["neighbors"]:
            lines.append("%s\t-\t0.00000" % row["seed"])
    return "\n".join(lines)


def build_store():
    with open(INDEX, "r", encoding="utf-8") as f:
        idx = json.load(f)
    rt = MatrixRuntime(idx, decay=HS.DECAY, capacity=100)
    replay = HS.replay_into(rt)
    from holoaeon.skill_matrix.mech import MECHANISMS
    seeds = HS.pick_seeds(rt.field, MECHANISMS)
    doc = HS.snapshot(rt.field, {"index_digest": idx.get("digest"),
                                 "index_rows": len(idx.get("skills") or []),
                                 "engine": "holoaeon.skill_matrix.runtime.MatrixRuntime",
                                 "decay": HS.DECAY, "capacity": rt.meridian.capacity},
                      seeds)
    return doc, rt, replay


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=os.path.join(ROOT, "reports", "b6_restart.json"))
    ap.add_argument("--no-write-store", action="store_true", help="用已有落盘文件做父侧基线")
    a = ap.parse_args()

    doc, rt, replay = build_store()
    if a.no_write_store and os.path.exists(STORE):
        doc = HS.load(STORE)
        rt.field._w = {}
        HS.restore(doc, rt.field)

    HS.save(doc, STORE)

    live_text = HS.topk_text(rt.field, doc["topk"]["seeds"], doc["topk"]["k"])
    frozen_text = _frozen_text(doc)
    live_sha = hashlib.sha256(live_text.encode("utf-8")).hexdigest()
    frozen_sha = hashlib.sha256(frozen_text.encode("utf-8")).hexdigest()

    proc = subprocess.run([sys.executable, "-c", CHILD, STORE, ROOT],
                          cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    if proc.returncode != 0:
        print(proc.stderr[-800:])
        return 2
    child = json.loads(proc.stdout.strip().splitlines()[-1])

    report = {
        "test_id": "SG-B6-RESTART-CONSISTENCY-V1",
        "batch": "B6",
        "evidence_class": "simulated",
        "store": "data/hebbian_store.json",
        "store_sha256": doc["sha256"],
        "replay_steps": replay["steps"] if replay else None,
        "parent_pid": os.getpid(),
        "child_pid": child["pid"],
        "child_verify_ok": child["verify_ok"],
        "live_topk_sha256": live_sha,
        "frozen_topk_sha256": frozen_sha,
        "child_topk_sha256": child["topk_sha256"],
        "child_edges_sha256": child["edges_sha256"],
        "edges_restored": child["edges_restored"],
        "edge_count": doc["edge_count"],
        "equal_live_vs_child": live_text == child["topk_text"],
        "equal_frozen_vs_child": frozen_text == child["topk_text"],
        "equal_live_vs_frozen": live_text == frozen_text,
        "topk_lines": len(live_text.splitlines()),
        "verdict": "PASS",
    }
    ok = (report["equal_live_vs_child"] and report["equal_frozen_vs_child"]
          and report["equal_live_vs_frozen"] and child["verify_ok"]
          and child["edges_restored"] == doc["edge_count"])
    report["verdict"] = "PASS" if ok else "FAIL"

    d = os.path.dirname(os.path.abspath(a.json)) if a.json else ""
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with open(a.json, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")

    print(json.dumps({k: report[k] for k in
                      ("verdict", "store_sha256", "parent_pid", "child_pid",
                       "equal_live_vs_child", "equal_frozen_vs_child", "topk_lines",
                       "edge_count", "edges_restored")}, ensure_ascii=False, indent=2))
    print("json=" + os.path.relpath(a.json, ROOT).replace("\\", "/"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
