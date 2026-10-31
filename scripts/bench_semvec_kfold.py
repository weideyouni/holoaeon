# -*- coding: utf-8 -*-
"""
bench_semvec_kfold.py —— V2 / W8 分层留出集（5 折）评估
================================================================================
用法：
    python scripts\\bench_semvec_kfold.py --folds 5
    python scripts\\bench_semvec_kfold.py --folds 5 --no-write

口径（务必连带读）：
  · 折 = 问法风格层（原句 / 口语 / 客气 / 书面 / 追加话术），每折 47 条，
    覆盖全部技能各一次；索引只在技能自述上 fit，问句不进语料 → 无训练泄漏；
    因此 std 读作"路由对问法风格的敏感度"，不是"模型泛化能力"。
  · 每折报 P@1（命中期望技能即 1），对 5 折取 mean / std（总体标准差）。
  · 门禁：std ≤ 0.05 且 5 折全跑通 → 绿（0）；std > 0.05 → 黄（2），
    并把数值写进 docs/spec-diff0-v0.2.md §9 已知限制。
  · 不调参刷分：权重与噪声地板沿用 bench_semvec.py 的 WEIGHT_SEM / BASE_FLOOR。
"""
from __future__ import annotations

import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from bench_semvec import BASE_FLOOR, INTENTS, WEIGHT_SEM, build, corpus_texts, route  # noqa: E402
from holoaeon.semvec import SemanticIndex  # noqa: E402
from holoaeon.spec import DOC_VERSION, VERSION  # noqa: E402

CORPUS = os.path.join(ROOT, "data", "semvec_corpus_v2.json")
STD_LIMIT = 0.05
EXIT_GREEN, EXIT_YELLOW = 0, 2


def _pstdev(values):
    n = len(values)
    if n == 0:
        return 0.0
    mean = math.fsum(values) / n
    var = math.fsum((v - mean) ** 2 for v in values) / n
    return math.sqrt(var)


def load_corpus(path: str = CORPUS) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def run(folds: int = 5, write: bool = True, path: str = CORPUS) -> dict:
    payload = load_corpus(path)
    tiers = payload["tiers"]
    if folds > len(tiers):
        raise SystemExit("语料只有 %d 层，无法切 %d 折" % (len(tiers), folds))
    items = payload["items"]

    k = build()
    docs = corpus_texts(k)
    idx = SemanticIndex()
    idx.fit(docs)

    per_fold = []
    for tier in tiers[:folds]:
        subset = [it for it in items if it["tier"] == tier]
        base_ok = sem_ok = hyb_ok = 0
        misses = []
        for it in subset:
            r = route(k, idx, it["query"], WEIGHT_SEM)
            if r["base"]["skill"] == it["expect"]:
                base_ok += 1
            if r["sem"]["skill"] == it["expect"]:
                sem_ok += 1
            if r["hybrid"]["skill"] == it["expect"]:
                hyb_ok += 1
            else:
                misses.append({"query": it["query"], "expect": it["expect"],
                               "got": r["hybrid"]["skill"]})
        n = len(subset) or 1
        per_fold.append({"fold": tier, "n": len(subset),
                         "base_p1": round(base_ok / n, 4),
                         "sem_p1": round(sem_ok / n, 4),
                         "hybrid_p1": round(hyb_ok / n, 4),
                         "misses": misses[:6]})

    hyb = [f["hybrid_p1"] for f in per_fold]
    mean = math.fsum(hyb) / len(hyb) if hyb else 0.0
    std = _pstdev(hyb)

    # 跨词汇锚点：V1 的 12 条意图（问句不含技能名里的规范术语，属"真改写"），
    # 单独报告，用来对冲"235 条语料里含技术术语导致 P@1 虚高"的偏差。
    anchor_ok = 0
    for query, expect in INTENTS:
        if route(k, idx, query, WEIGHT_SEM)["hybrid"]["skill"] == expect:
            anchor_ok += 1
    anchor = {"intents": len(INTENTS), "hybrid_correct": anchor_ok,
              "hybrid_rate": round(anchor_ok / (len(INTENTS) or 1), 4)}
    out = {
        "version": VERSION,
        "doc_version": DOC_VERSION,
        "evidence_class": "simulated",
        "corpus": os.path.relpath(path, ROOT).replace("\\", "/"),
        "corpus_sha": payload.get("corpus_sha"),
        "skills": payload["skills"],
        "count": payload["count"],
        "folds": len(per_fold),
        "weight_sem": WEIGHT_SEM,
        "base_floor": BASE_FLOOR,
        "vocab_size": len(idx.vocab),
        "dim": idx.dim,
        "mean_p1": round(mean, 4),
        "std_p1": round(std, 4),
        "std_limit": STD_LIMIT,
        "min_p1": round(min(hyb), 4) if hyb else 0.0,
        "max_p1": round(max(hyb), 4) if hyb else 0.0,
        "per_fold": per_fold,
        "anchor_v1_intents": anchor,
        "note": ("折=问法风格层，索引只在技能自述上 fit，问句不进语料；"
                 "std 读作问法风格敏感度，不是泛化能力。235 条含规范术语，"
                 "P@1 虚高，跨词汇能力以 anchor_v1_intents 为准。simulated。"),
    }
    if write:
        dst = os.path.join(ROOT, "benchmarks",
                           "results-semvec-kfold-%s.json" % DOC_VERSION)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(out, ensure_ascii=False, indent=2,
                                sort_keys=True))
            fh.write("\n")
        out["written"] = dst
    out["exit"] = EXIT_GREEN if std <= STD_LIMIT else EXIT_YELLOW
    return out


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    folds = 5
    if "--folds" in argv:
        folds = int(argv[argv.index("--folds") + 1])
    res = run(folds=folds, write="--no-write" not in argv)
    print("=" * 72)
    print("semvec 分层留出  folds=%d  skills=%d  queries=%d  vocab=%d  dim=%d"
          % (res["folds"], res["skills"], res["count"], res["vocab_size"],
             res["dim"]))
    print("corpus=%s sha=%s" % (res["corpus"], res["corpus_sha"]))
    print("-" * 72)
    print("%-14s %-6s %-8s %-8s %-9s" % ("折(问法层)", "n", "基线P@1", "语义P@1", "混合P@1"))
    for f in res["per_fold"]:
        print("%-14s %-6d %-8.4f %-8.4f %-9.4f"
              % (f["fold"], f["n"], f["base_p1"], f["sem_p1"], f["hybrid_p1"]))
    print("-" * 72)
    print("混合 P@1  mean=%.4f  std=%.4f  min=%.4f  max=%.4f  (limit std<=%.2f)"
          % (res["mean_p1"], res["std_p1"], res["min_p1"], res["max_p1"],
             res["std_limit"]))
    print("跨词汇锚点（V1 12 意图，含改写）  %d/%d = %.1f%%"
          % (res["anchor_v1_intents"]["hybrid_correct"],
             res["anchor_v1_intents"]["intents"],
             res["anchor_v1_intents"]["hybrid_rate"] * 100))
    if res.get("written"):
        print("written: %s" % res["written"])
    print("KFOLD_EXIT=%d" % res["exit"])
    return res["exit"]


if __name__ == "__main__":
    raise SystemExit(main())
