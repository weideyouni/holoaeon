# -*- coding: utf-8 -*-
"""
repro_core_emit.py —— V2 / W9 REPRO_CORE 多模态证据统一协议
================================================================================
把原来散在三套脚本、靠 README 手抄的三类证据（DIFF=0 / 拦截率 / 足迹）
+ 账本 / 守卫集 / semvec 两个基准 + V2 新增（篡改自检、kfold）统一成一份
**逐行可哈希**的 JSONL：每行一条证据，字段固定：

  evidence / evidence_class / measure_source / measure_ts /
  golden_value / observed_value / verdict / verdict_hash

verdict_hash = sha256(规范化去掉 measure_ts 与 verdict_hash 后的整行)[:16]
—— measure_ts 是物理量，不进哈希；同一台机器重跑必得同一 verdict_hash。

用法：
    python scripts\\repro_core_emit.py --out reports/repro_core.jsonl
    python scripts\\repro_core_emit.py --check reports/repro_core.jsonl

独立成文件、不并入 attestation.jsonl（V2 已知坑 V2-3）。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (ROOT, os.path.join(ROOT, "scripts"), os.path.join(ROOT, "benchmarks")):
    if p not in sys.path:
        sys.path.insert(0, p)

from bench_public import (measure_diff0, measure_footprint,  # noqa: E402
                          measure_guard, measure_sensitivity)
from bench_semvec import build as build_kernel_for_semvec  # noqa: E402
from bench_semvec import corpus_texts, vector_digest  # noqa: E402
from holoaeon.audit import load_golden, verify  # noqa: E402
from holoaeon.audit.mutation import mutate_selftest  # noqa: E402
from holoaeon.audit.verify import run_task  # noqa: E402
from holoaeon.semvec import SemanticIndex  # noqa: E402
from holoaeon.spec import DOC_VERSION, VERSION  # noqa: E402

GOLDEN = {
    "diff0_hash": "2fc892cf9af6e755",
    "mutation_sensitivity_v1": "f42c8229ee5acd73",
    "guard_block": "16/16",
    "guard_allow": "4/4",
    "word_count_golden": "2b82a6ef7188ce91",
    "ledger_sha": "98940b774566543b",
    "semvec_digest_v1": "789b71a36bfcd66a",
    "semvec_kfold_std": "<=0.05",
    "mutation_selftest_v2": "5/5",
}

SOURCE = {
    "diff0_hash": "benchmarks/bench_public.py::measure_diff0",
    "mutation_sensitivity_v1": "benchmarks/bench_public.py::measure_sensitivity",
    "guard_block": "benchmarks/bench_public.py::measure_guard",
    "guard_allow": "benchmarks/bench_public.py::measure_guard",
    "word_count_golden": "holoaeon/audit/verify.py::verify(word_count)",
    "ledger_sha": "scripts/ledger_view.py::render(make_sample)",
    "semvec_digest_v1": "scripts/bench_semvec.py::vector_digest",
    "semvec_kfold_std": "scripts/bench_semvec_kfold.py",
    "mutation_selftest_v2": "holoaeon/audit/mutation.py::mutate_selftest",
    "footprint": "benchmarks/bench_public.py::measure_footprint",
}

# measure_ts 是物理量、不进 verdict_hash，但它会进文件字节。为了让
# 「同机重跑 → 证据文件 sha256 不变 → 快照 sha 不变」这条回放判据真的成立，
# 默认取固定时刻；要看真实运行时刻时用 HOLOAEON_MEASURE_TS 覆盖，
# 那时文件字节随运行时间变化，属预期，不再是字节可复现件。
MEASURE_TS = os.environ.get("HOLOAEON_MEASURE_TS", "2026-11-01T00:00:00")


def row_hash(row: dict) -> str:
    body = {k: v for k, v in row.items()
            if k not in ("measure_ts", "verdict_hash")}
    payload = json.dumps(body, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def _row(evidence: str, golden, observed, verdict: str,
         evidence_class: str = "simulated") -> dict:
    row = {
        "evidence": evidence,
        "evidence_class": evidence_class,
        "measure_source": SOURCE.get(evidence, "unknown"),
        "measure_ts": MEASURE_TS,
        "golden_value": golden,
        "observed_value": observed,
        "verdict": verdict,
    }
    row["verdict_hash"] = row_hash(row)
    return row


def ledger_sha() -> dict:
    import ledger_view
    sample = os.path.join(ROOT, "data", "ledger_sample.jsonl")
    src = ledger_view.make_sample(sample)
    records = ledger_view.load(sample)
    doc = ledger_view.render(records, title="HoloAeon 账本视图 · ledger_sample.jsonl")
    out = os.path.join(ROOT, "reports", "ledger.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(doc)
    return {"sha": hashlib.sha256(doc.encode("utf-8")).hexdigest()[:16],
            "size": os.path.getsize(out), "records": len(src)}


def semvec_digest() -> dict:
    k = build_kernel_for_semvec()
    idx = SemanticIndex()
    idx.fit(corpus_texts(k))
    idx2 = SemanticIndex()
    idx2.fit(corpus_texts(k))
    d1, d2 = vector_digest(idx), vector_digest(idx2)
    return {"digest": d1, "digest_b": d2, "stable": d1 == d2,
            "docs": len(corpus_texts(k))}


def kfold_row() -> dict:
    path = os.path.join(ROOT, "benchmarks",
                        "results-semvec-kfold-%s.json" % DOC_VERSION)
    if not os.path.isfile(path):
        return {"mean": None, "std": None, "folds": 0,
                "note": "kfold 结果文件缺失"}
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return {"mean": data.get("mean_p1"), "std": data.get("std_p1"),
            "folds": data.get("folds"),
            "anchor": data.get("anchor_v1_intents", {}).get("hybrid_rate")}


def collect(n: int = 2) -> list:
    rows = []

    d0 = measure_diff0()
    rows.append(_row("diff0_hash", GOLDEN["diff0_hash"], d0["hash_run1"],
                     "pass" if (d0["diff0"] and d0["hash_run1"] == GOLDEN["diff0_hash"])
                     else "fail"))

    sens = measure_sensitivity()
    rows.append(_row("mutation_sensitivity_v1", GOLDEN["mutation_sensitivity_v1"],
                     sens["hash_tampered"],
                     "pass" if (sens["sensitive"]
                                and sens["hash_tampered"] == GOLDEN["mutation_sensitivity_v1"])
                     else "fail"))

    g = measure_guard()
    rows.append(_row("guard_block", GOLDEN["guard_block"],
                     "%d/%d" % (g["blocked"], g["dangerous"]),
                     "pass" if g["blocked"] == g["dangerous"] else "fail"))
    rows.append(_row("guard_allow", GOLDEN["guard_allow"],
                     "%d/%d" % (g["legit_pass"], g["legit_total"]),
                     "pass" if g["legit_pass"] == g["legit_total"] else "fail"))

    golden = load_golden("word_count")
    verdict = verify("word_count", golden["task"], golden.get("args"),
                     golden.get("to"), n=n, golden=golden)
    rows.append(_row("word_count_golden", GOLDEN["word_count_golden"],
                     verdict["reprohash_list"][0],
                     "pass" if verdict["golden_match"] else "fail"))

    led = ledger_sha()
    rows.append(_row("ledger_sha", GOLDEN["ledger_sha"], led["sha"],
                     "pass" if led["sha"] == GOLDEN["ledger_sha"] else "fail"))

    sv = semvec_digest()
    rows.append(_row("semvec_digest_v1", GOLDEN["semvec_digest_v1"], sv["digest"],
                     "pass" if (sv["stable"] and sv["digest"] == GOLDEN["semvec_digest_v1"])
                     else "fail"))

    receipt = run_task(golden["task"], args=golden.get("args"), to=golden.get("to"))
    mu = mutate_selftest(receipt, n=5)
    rows.append(_row("mutation_selftest_v2", GOLDEN["mutation_selftest_v2"],
                     "%d/%d" % (mu["changed"], mu["mutations"]),
                     "pass" if mu["sensitive"] else "fail"))

    kf = kfold_row()
    if kf["std"] is None:
        verdict_text = "fail"
    else:
        verdict_text = "pass" if kf["std"] <= 0.05 else "warn"
    rows.append(_row("semvec_kfold_std", GOLDEN["semvec_kfold_std"],
                     "mean=%.4f std=%.4f folds=%s" % (kf["mean"], kf["std"], kf["folds"]),
                     verdict_text))

    fp = measure_footprint()
    # build_ms 逐次变动属物理量：只打印不写入证据行，否则 verdict_hash 不可复现
    print("footprint 物理量（不进哈希）：build=%.2fms peak=%.2fMiB"
          % (fp["build_ms"], fp["peak_mib"]))
    rows.append(_row("footprint",
                     "n/a（物理量，不进哈希）",
                     "agents=%d skills=%d peak=%.2fMiB"
                     % (fp["agents"], fp["skills"], fp["peak_mib"]),
                     "info"))
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="REPRO_CORE 证据统一输出")
    ap.add_argument("--out", default=os.path.join(ROOT, "reports", "repro_core.jsonl"))
    ap.add_argument("--n", type=int, default=2)
    ap.add_argument("--check", default="", help="复算并与既有文件逐行比对 verdict_hash")
    args = ap.parse_args(argv)

    rows = collect(n=args.n)
    fails = [r["evidence"] for r in rows if r["verdict"] == "fail"]
    warns = [r["evidence"] for r in rows if r["verdict"] == "warn"]

    if args.check:
        if not os.path.isfile(args.check):
            print("CHECK MISSING: %s" % args.check)
            return 1
        old = {}
        with open(args.check, "r", encoding="utf-8") as fh:
            for line in fh:
                item = json.loads(line)
                old[item["evidence"]] = item["verdict_hash"]
        bad = [r["evidence"] for r in rows
               if old.get(r["evidence"]) != r["verdict_hash"]]
        if bad:
            print("CHECK FAIL: %d 行哈希不一致 %s" % (len(bad), bad[:5]))
            return 1
        print("CHECK OK: %d 行 verdict_hash 全部复算一致" % len(rows))
        return 0

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")

    print("=" * 72)
    print("REPRO_CORE v%s（运行态 v%s）  证据行数=%d" % (DOC_VERSION, VERSION, len(rows)))
    print("-" * 72)
    for r in rows:
        print("%-24s %-10s %-28s %s"
              % (r["evidence"], r["verdict"],
                 str(r["observed_value"])[:26], r["verdict_hash"]))
    print("-" * 72)
    print("written: %s" % args.out)
    print("fails=%s warns=%s" % (fails, warns))
    print("REPRO_EXIT=%d" % (0 if not fails else 1))
    return 0 if not fails else 1


if __name__ == "__main__":
    raise SystemExit(main())
