# -*- coding: utf-8 -*-
"""
eval_set.py —— 47 技能评测集（W15，旁挂脚本）
================================================================================
每条 eval 四件套：input / reference / scorer / evidence_class。
默认 scorer 是**确定性规则**（routing@1：同一 query 必须路由回该技能）；
LLM-judge 只做披露，不做裁决（V3-5）。

用法：
    python scripts\\eval_set.py --write                 # 生成/刷新 data\\eval_47.json
    python scripts\\eval_set.py --run                   # 跑一遍，打印准确率
    python scripts\\eval_set.py --run --variant trunc12 # 变体（供 eval_diff 对比）
    python scripts\\eval_set.py --run --json out.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from holoaeon.kernel import Kernel  # noqa: E402
from holoaeon.packs import all_packs  # noqa: E402

DATA = os.path.join(ROOT, "data", "eval_47.json")
SCORER = "routing@1"
EVIDENCE_CLASS = "simulated"


def build_kernel() -> Kernel:
    k = Kernel()
    for pack in all_packs():
        pack.install(k)
    return k


def _cases(k: Kernel) -> list:
    cases = []
    for skill in k.skills.all():
        desc = skill.manifest.description or skill.name
        cases.append({
            "skill": skill.name,
            "input": desc,
            "reference": skill.name,
            "scorer": SCORER,
            "evidence_class": EVIDENCE_CLASS,
        })
    return cases


def write_suite() -> dict:
    k = build_kernel()
    cases = _cases(k)
    suite = {"suite": "eval_47", "doc_version": "0.9.3",
             "scorer": SCORER, "evidence_class": EVIDENCE_CLASS,
             "count": len(cases), "skills": len(k.skills.names()),
             "cases": cases}
    os.makedirs(os.path.dirname(DATA), exist_ok=True)
    with open(DATA, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(suite, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    return {"path": DATA, "count": len(cases), "skills": len(k.skills.names())}


def run(variant: str = "raw") -> dict:
    k = build_kernel()
    suite = None
    if os.path.exists(DATA):
        with open(DATA, "r", encoding="utf-8") as fh:
            suite = json.load(fh)
    cases = (suite or {}).get("cases") or _cases(k)
    rows = []
    for i, case in enumerate(cases):
        query = case["input"]
        if variant == "cross":
            # 对抗变体：把别条技能的 self-description 当问句（应当被 diff 抓成回归）
            query = cases[(i + 1) % len(cases)]["input"]
        if variant == "trunc12":
            query = query[:12]
        elif variant == "upper":
            query = query.upper()
        elif variant == "reverse":
            query = query[::-1]
        elif variant == "salt":
            query = "zz zz " + query[:8]
        got = k.skills.best(query)
        rows.append({"skill": case["skill"], "input": case["input"],
                     "reference": case["reference"], "got": got,
                     "ok": got == case["reference"],
                     "score": dict(k.skills.match(query, k=1)).get(got, 0.0)
                     if got else 0.0,
                     "scorer": case.get("scorer", SCORER),
                     "evidence_class": case.get("evidence_class", EVIDENCE_CLASS)})
    ok = sum(1 for r in rows if r["ok"])
    acc = round(ok / len(rows), 4) if rows else 0.0
    scores = [r["score"] for r in rows]
    mean = round(sum(scores) / len(scores), 4) if scores else 0.0
    var = (sum((s - mean) ** 2 for s in scores) / len(scores)) if scores else 0.0
    std = round(var ** 0.5, 4)
    return {"suite": "eval_47", "variant": variant, "cases": len(rows),
            "ok": ok, "accuracy": acc, "score_mean": mean, "score_std": std,
            "evidence_class": EVIDENCE_CLASS,
            "note": "scorer 为确定性规则；judge 分数仅披露、不裁决",
            "rows": rows}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--variant", default="raw")
    ap.add_argument("--json", default="")
    a = ap.parse_args()
    if a.write:
        rep = write_suite()
        print(json.dumps(rep, ensure_ascii=False))
        return 0
    if a.run or not a.write:
        rep = run(a.variant)
        if a.json:
            with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(rep, fh, ensure_ascii=False, indent=2, sort_keys=True)
                fh.write("\n")
        summary = {k: v for k, v in rep.items() if k != "rows"}
        print(json.dumps(summary, ensure_ascii=False))
        return 0 if rep["cases"] else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
