# -*- coding: utf-8 -*-
"""B6 · 17 通道配额与负载对表（SOP-9 第 3 步）

做法：以 data/channel_map.json（B2b 冻结的 12→17 映射）为准，逐行展开 17 个目标通道：
  · 12 个 mapped 通道：配额 = 该 LC 的经络预算（Meridian capacity，默认 100），
    另用固定回放集实测 load，得 headroom = quota - load；
  · 5 个 pending 通道（神 1 + 淋巴 4）：配额 0、负载 0，如实标注待办，不补位、不取模。
禁止按行序号推导通道号（B2b 的 no_arithmetic 口径）。

用法：
    python scripts/gen_channel_quota.py --out data/channel_quota.csv
    python scripts/gen_channel_quota.py --check
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from holoaeon.fusion_upgrade import hebbian_store as HS  # noqa: E402
from holoaeon.skill_matrix.mech import CHANNELS  # noqa: E402
from holoaeon.skill_matrix.runtime import MatrixRuntime  # noqa: E402

MAP = os.path.join(ROOT, "data", "channel_map.json")
INDEX = os.path.join(ROOT, "data", "skill_matrix_index.json")
DEFAULT_OUT = os.path.join(ROOT, "data", "channel_quota.csv")

# B2b 映射的显式落位（写死，不按序号推导）：LC → 目标通道名
LC_TO_TARGET = {
    "LC01": ("气1", "气"), "LC02": ("气2", "气"), "LC03": ("气3", "气"),
    "LC04": ("气4", "气"), "LC05": ("气5", "气"),
    "LC06": ("血1", "血"), "LC07": ("血2", "血"), "LC08": ("血3", "血"),
    "LC09": ("血4", "血"),
    "LC10": ("神1", "神"), "LC11": ("神2", "神"), "LC12": ("神3", "神"),
}
PENDING_TARGETS = (("神4", "神"), ("淋巴1", "淋巴"), ("淋巴2", "淋巴"),
                   ("淋巴3", "淋巴"), ("淋巴4", "淋巴"))
HEADER = ("channel", "group", "status", "lc", "quota", "load_observed", "headroom", "note")


def measure_load():
    with open(INDEX, "r", encoding="utf-8") as f:
        idx = json.load(f)
    rt = MatrixRuntime(idx, decay=HS.DECAY, capacity=100)
    replay = HS.replay_into(rt)
    return rt.meridian.capacity, replay


def rows():
    capacity, replay = measure_load()
    load = replay["load"]
    out = []
    for lc in CHANNELS:
        target, group = LC_TO_TARGET[lc]
        used = int(load.get(lc, 0))
        out.append({"channel": target, "group": group, "status": "mapped", "lc": lc,
                    "quota": int(capacity), "load_observed": used,
                    "headroom": int(capacity) - used,
                    "note": "配额=该 LC 经络预算；负载=固定回放集实测"})
    for target, group in PENDING_TARGETS:
        out.append({"channel": target, "group": group, "status": "pending", "lc": "",
                    "quota": 0, "load_observed": 0, "headroom": 0,
                    "note": "B2b 待办，配额未分配（不补位、不取模）"})
    return out, capacity, replay


def render(rs):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(HEADER), lineterminator="\n")
    w.writeheader()
    for r in rs:
        w.writerow(r)
    return buf.getvalue()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()

    rs, capacity, replay = rows()
    text = render(rs)
    summary = {"rows": len(rs),
               "mapped": sum(1 for r in rs if r["status"] == "mapped"),
               "pending": sum(1 for r in rs if r["status"] == "pending"),
               "quota_total": sum(r["quota"] for r in rs),
               "load_total": sum(r["load_observed"] for r in rs),
               "capacity_per_channel": capacity,
               "replay_steps": replay["steps"]}

    if a.check:
        with open(a.out, "r", encoding="utf-8") as f:
            on_disk = f.read()
        summary["byte_consistent"] = on_disk == text
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0 if on_disk == text else 1

    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    summary["bytes"] = os.path.getsize(a.out)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
