# -*- coding: utf-8 -*-
"""B6 · 赫布权重落盘（SOP-9 第 1 步）

做法：拿固定回放集（24 条，写死在 hebbian_store.REPLAY_QUERIES）走一遍
      MatrixRuntime.dispatch，共激活累进 HebbianField，然后把边权重 + top-k 基线
      冻结成 data/hebbian_store.json。同一输入两次跑必须得到同一 sha256。

用法：
    python scripts/hebbian_persist.py --out data/hebbian_store.json
    python scripts/hebbian_persist.py --check        # 只复算，不重写文件
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from holoaeon.fusion_upgrade import hebbian_store as HS  # noqa: E402
from holoaeon.skill_matrix.mech import MECHANISMS  # noqa: E402
from holoaeon.skill_matrix.runtime import MatrixRuntime  # noqa: E402

INDEX = os.path.join(ROOT, "data", "skill_matrix_index.json")
DEFAULT_OUT = os.path.join(ROOT, "data", "hebbian_store.json")


def build():
    with open(INDEX, "r", encoding="utf-8") as f:
        idx = json.load(f)
    rt = MatrixRuntime(idx, decay=HS.DECAY, capacity=100)
    replay = HS.replay_into(rt)
    seeds = HS.pick_seeds(rt.field, MECHANISMS)
    meta = {
        "index_digest": idx.get("digest"),
        "index_rows": len(idx.get("skills") or []),
        "engine": "holoaeon.skill_matrix.runtime.MatrixRuntime",
        "decay": HS.DECAY,
        "capacity": rt.meridian.capacity,
    }
    doc = HS.snapshot(rt.field, meta, seeds)
    return doc, replay


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--check", action="store_true", help="不写盘，只复算并与已有文件比对")
    a = ap.parse_args()

    doc, replay = build()
    info = {
        "out": os.path.relpath(a.out, ROOT).replace("\\", "/"),
        "sha256": doc["sha256"],
        "edge_count": doc["edge_count"],
        "node_count": doc["node_count"],
        "seeds": len(doc["topk"]["seeds"]),
        "replay_steps": replay["steps"],
        "load": replay["load"],
        "mechanism_hits": replay["mechanism_hits"],
    }

    if a.check:
        on_disk = HS.load(a.out)
        same_bytes = HS.canonical(on_disk) == HS.canonical(doc)
        info["on_disk_sha256"] = on_disk.get("sha256")
        info["byte_consistent"] = same_bytes
        print(json.dumps(info, ensure_ascii=False, indent=2))
        return 0 if same_bytes and on_disk.get("sha256") == doc["sha256"] else 1

    size = HS.save(doc, a.out)
    info["bytes"] = size
    print(json.dumps(info, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
