# -*- coding: utf-8 -*-
"""B6 · 赫布落盘与通道配额自检（H1–H9）

用法：
    python scripts/check_hebbian_store.py
    python scripts/check_hebbian_store.py --json reports/b6_hebbian_check.json
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from holoaeon.fusion_upgrade import hebbian_store as HS  # noqa: E402
from holoaeon.skill_matrix.mech import MECHANISMS, HebbianField  # noqa: E402
from holoaeon.skill_matrix.runtime import MatrixRuntime  # noqa: E402

INDEX = os.path.join(ROOT, "data", "skill_matrix_index.json")
STORE = os.path.join(ROOT, "data", "hebbian_store.json")
QUOTA = os.path.join(ROOT, "data", "channel_quota.csv")
RESTART = os.path.join(ROOT, "reports", "b6_restart.json")
LOCK = os.path.join(ROOT, "reports", "b0_lock_v4fusion.json")

EXPECT_ROWS = 17
EXPECT_MAPPED = 12
EXPECT_PENDING = 5
EXPECT_QUOTA_TOTAL = 1200


def _rebuild():
    with open(INDEX, "r", encoding="utf-8") as f:
        idx = json.load(f)
    rt = MatrixRuntime(idx, decay=HS.DECAY, capacity=100)
    HS.replay_into(rt)
    seeds = HS.pick_seeds(rt.field, MECHANISMS)
    doc = HS.snapshot(rt.field, {"index_digest": idx.get("digest"),
                                 "index_rows": len(idx.get("skills") or []),
                                 "engine": "holoaeon.skill_matrix.runtime.MatrixRuntime",
                                 "decay": HS.DECAY, "capacity": rt.meridian.capacity},
                      seeds)
    return doc, rt


def _frozen_text(doc):
    lines = []
    for row in doc["topk"]["rows"]:
        for nb in row["neighbors"]:
            lines.append("%s\t%s\t%.5f" % (row["seed"], nb["name"], nb["w"]))
        if not row["neighbors"]:
            lines.append("%s\t-\t0.00000" % row["seed"])
    return "\n".join(lines)


def check():
    out = []

    # H1 落盘文件存在且能解析
    ok = os.path.isfile(STORE)
    doc = HS.load(STORE) if ok else {}
    out.append({"id": "H1", "name": "落盘文件存在且可解析", "ok": bool(ok and doc.get("store_id") == HS.STORE_ID),
                "detail": {"path": "data/hebbian_store.json", "store_id": doc.get("store_id"),
                           "bytes": os.path.getsize(STORE) if ok else 0}})

    # H2 自哈希 + 结构
    v = HS.verify(doc)
    out.append({"id": "H2", "name": "自指 sha256 复算一致 + 边表结构", "ok": v["ok"],
                "detail": {k: v[k] for k in ("sha256", "recomputed", "edge_count", "edges_len",
                                            "key_order_ok", "weights_ok")}})

    # H3 规模非空
    topo = HS.topology(doc)
    out.append({"id": "H3", "name": "边/节点规模自洽", "ok": doc.get("edge_count", 0) > 0
                and topo["nodes"] == doc.get("node_count"),
                "detail": topo})

    # H4 重跑同参得到同摘要（确定性）
    fresh, _ = _rebuild()
    out.append({"id": "H4", "name": "重跑即同摘要（确定性）", "ok": fresh["sha256"] == doc.get("sha256"),
                "detail": {"disk": doc.get("sha256"), "rebuilt": fresh["sha256"]}})

    # H5 复原往返：load → restore → top-k 逐字相等
    f = HebbianField(HS.DECAY)
    HS.restore(doc, f)
    text = HS.topk_text(f, doc["topk"]["seeds"], doc["topk"]["k"])
    out.append({"id": "H5", "name": "load→restore→top-k 与冻结基线逐字相等", "ok": text == _frozen_text(doc),
                "detail": {"lines": len(text.splitlines()), "edges_restored": len(f._w)}})

    # H6 重启一致测试票据
    rep = {}
    if os.path.isfile(RESTART):
        with open(RESTART, "r", encoding="utf-8") as fh:
            rep = json.load(fh)
    ok = (rep.get("verdict") == "PASS"
          and rep.get("equal_live_vs_child") is True
          and rep.get("equal_frozen_vs_child") is True
          and rep.get("store_sha256") == doc.get("sha256"))
    out.append({"id": "H6", "name": "独立进程重启后 top-k 逐字相等", "ok": bool(ok),
                "detail": {k: rep.get(k) for k in ("parent_pid", "child_pid",
                                                   "equal_live_vs_child", "equal_frozen_vs_child")}})

    # H7 配额表形状
    rows = []
    if os.path.isfile(QUOTA):
        with open(QUOTA, "r", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
    mapped = [r for r in rows if r["status"] == "mapped"]
    pending = [r for r in rows if r["status"] == "pending"]
    qsum = sum(int(r["quota"]) for r in rows)
    ok = (len(rows) == EXPECT_ROWS and len(mapped) == EXPECT_MAPPED
          and len(pending) == EXPECT_PENDING and qsum == EXPECT_QUOTA_TOTAL
          and all(int(r["headroom"]) >= 0 for r in rows)
          and len({r["channel"] for r in rows}) == EXPECT_ROWS
          and len({r["group"] for r in rows}) == 4)
    out.append({"id": "H7", "name": "17 通道配额表形状与配额总量", "ok": bool(ok),
                "detail": {"rows": len(rows), "mapped": len(mapped), "pending": len(pending),
                           "quota_total": qsum, "groups": sorted({r["group"] for r in rows})}})

    # H8 配额表可重算（字节一致）
    from scripts.gen_channel_quota import render, rows as quota_rows  # noqa: E402
    rs, _, _ = quota_rows()
    with open(QUOTA, "r", encoding="utf-8") as fh:
        disk = fh.read()
    out.append({"id": "H8", "name": "配额表可重算（字节一致）", "ok": disk == render(rs),
                "detail": {"regenerated_rows": len(rs)}})

    # H9 维度与规格未动
    lock = {}
    if os.path.isfile(LOCK):
        with open(LOCK, "r", encoding="utf-8") as fh:
            lock = json.load(fh)
    from holoaeon import spec as SPEC  # noqa: E402
    from holoaeon.packs import EXTRA_PACK_ORDER, PACK_ORDER  # noqa: E402
    obs = (((lock.get("observed") or {}).get("A1_detail")) or {})
    agents, skills, packs = obs.get("agents"), obs.get("skills"), obs.get("packs")
    ok = (agents == 25 and skills == 47 and packs == 9
          and len(PACK_ORDER) == 9 and len(EXTRA_PACK_ORDER) == 10
          and getattr(SPEC, "VERSION", None) == "0.9.1")
    out.append({"id": "H9", "name": "维度 25/47/9 与 spec 0.9.1 未动", "ok": bool(ok),
                "detail": {"lock": {"agents": agents, "skills": skills, "packs": packs},
                           "PACK_ORDER": len(PACK_ORDER), "EXTRA_PACK_ORDER": len(EXTRA_PACK_ORDER),
                           "spec_version": getattr(SPEC, "VERSION", None)}})

    verdict = "PASS" if all(x["ok"] for x in out) else "FAIL"
    return {"check_id": "SG-B6-HEBBIAN-CHECK-V1", "batch": "B6",
            "evidence_class": "simulated", "verdict": verdict,
            "failed": [x["id"] for x in out if not x["ok"]],
            "checks": out,
            "store_sha256": doc.get("sha256"),
            "edge_count": doc.get("edge_count")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=os.path.join(ROOT, "reports", "b6_hebbian_check.json"))
    a = ap.parse_args()
    rep = check()
    d = os.path.dirname(os.path.abspath(a.json))
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with open(a.json, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(rep, ensure_ascii=False, indent=2) + "\n")
    for c in rep["checks"]:
        print(("[OK]   " if c["ok"] else "[FAIL] ") + c["id"] + " " + c["name"])
    print("verdict=%s failed=%s json=%s" % (rep["verdict"], rep["failed"],
                                            os.path.relpath(a.json, ROOT).replace("\\", "/")))
    return 0 if rep["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
