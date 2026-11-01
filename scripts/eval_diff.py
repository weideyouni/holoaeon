# -*- coding: utf-8 -*-
"""
eval_diff.py —— 双轨对比（W15，旁挂脚本）
================================================================================
确定性轨：逐条比 ok（routes 是否仍回到原技能）。
质量轨：逐条比 score（judge/规则分只**披露**，不裁决）。
任何一侧的差异都列出明细，不污染黄金值。

用法：
    python scripts\\eval_diff.py --left a.json --right b.json
    python scripts\\eval_diff.py --variant trunc12      # 内部跑 raw vs 变体
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
SCRIPTS = os.path.dirname(os.path.abspath(__file__))
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

import eval_set  # noqa: E402


def diff(left: dict, right: dict) -> dict:
    li = {r["skill"]: r for r in left.get("rows", [])}
    ri = {r["skill"]: r for r in right.get("rows", [])}
    common = sorted(set(li) & set(ri))
    improved, regressed, unchanged = [], [], 0
    score_moved = []
    for name in common:
        a, b = li[name], ri[name]
        if a["ok"] != b["ok"]:
            (improved if b["ok"] else regressed).append(name)
        else:
            unchanged += 1
        if abs(float(a.get("score", 0.0)) - float(b.get("score", 0.0))) > 1e-9:
            score_moved.append({"skill": name,
                                "left": a.get("score"), "right": b.get("score")})
    return {
        "left": {"variant": left.get("variant"), "accuracy": left.get("accuracy"),
                 "cases": left.get("cases")},
        "right": {"variant": right.get("variant"), "accuracy": right.get("accuracy"),
                  "cases": right.get("cases")},
        "common": len(common),
        "improved": improved,
        "regressed": regressed,
        "unchanged": unchanged,
        "score_moved": score_moved[:10],
        "score_moved_count": len(score_moved),
        "verdict": "REGRESSED" if regressed else "OK",
        "note": "质量轨只披露；裁决走确定性轨",
    }


def _load(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--left", default="")
    ap.add_argument("--right", default="")
    ap.add_argument("--variant", default="cross")
    ap.add_argument("--json", default="")
    a = ap.parse_args()
    if a.left and a.right:
        left, right = _load(a.left), _load(a.right)
    else:
        left, right = eval_set.run("raw"), eval_set.run(a.variant)
    rep = diff(left, right)
    if a.json:
        with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(rep, fh, ensure_ascii=False, indent=2, sort_keys=True)
            fh.write("\n")
    print(json.dumps(rep, ensure_ascii=False))
    return 0 if rep["common"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
