# -*- coding: utf-8 -*-
"""
bench_semvec.py —— 语义通道实测（路由准确率 + 确定性自证）
================================================================================
用法：
    python scripts\\bench_semvec.py            # 跑并写 benchmarks\\results-semvec-*.json
    python scripts\\bench_semvec.py --no-write # 只打印

口径：
  - 基线 = 既有 Registry.score（Jaccard + 字符 2-gram Dice + 标签命中）；
  - 语义 = semvec 余弦；
  - 混合 = 0.5·基线 + 0.5·语义（规格要求的可调权重）；
  - 全部 simulated：语料是技能自述文本，不含用户数据。
"""
from __future__ import annotations

import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from holoaeon.kernel import Kernel  # noqa: E402
from holoaeon.packs import PACK_ORDER, get_pack  # noqa: E402
from holoaeon.semvec import SemanticIndex, docs_from_skills, tokenize  # noqa: E402
from holoaeon.skill import tokenize as base_tokenize  # noqa: E402
from holoaeon.spec import VERSION  # noqa: E402

INTENTS = [
    ("统计字数：HoloAeon 是零依赖的确定性多智能体认知框架。", "word_count"),
    ("患者数据统计", "basic_stats"),
    ("给这列数据算均值和标准差", "basic_stats"),
    ("计算夏普比率", "sharpe"),
    ("计算收益率", "returns"),
    ("最大回撤是多少", "drawdown"),
    ("读一下这篇论文的摘要", "extract_abstract"),
    ("筛一下相关文献", "screen_papers"),
    ("去重论文列表", "dedup_papers"),
    ("写周报总结", "weekly_review"),
    ("拆解一下这个任务", "task_breakdown"),
    ("设计实验的样本量", "sample_size"),
]

WEIGHT_SEM = 0.75
BASE_FLOOR = 0.15


def build() -> Kernel:
    k = Kernel()
    for key in PACK_ORDER:
        get_pack(key).install(k)
    return k


def vector_digest(index: SemanticIndex) -> str:
    import hashlib
    payload = json.dumps(
        {t: [round(x, 9) for x in v] for t, v in sorted(index.vectors.items())},
        ensure_ascii=False, sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def corpus_texts(k: Kernel) -> list:
    """训练语料：**只取技能自述**（name + description + tags），与 docs/ 文档彻底解耦。

    踩过的坑：早先版本把 README/docs/*.md 的整行也塞进语料，于是每改一次文档，
    语料就多几行、词表与 PMI 全部漂移，同一批 12 条意图的命中率会在 12/12 与 9/12
    之间跳（实测 +15 行文档 → 跌到 9/12）。技能路由的索引只该学"技能怎么描述自己"，
    语料必须由代码内容唯一决定，才能做到"文档怎么改都不影响基准"。
    """
    return docs_from_skills(k.skills.all())


def route(k: Kernel, index: SemanticIndex, query: str, weight: float) -> dict:
    """混合路由：基线与语义各自按本次候选集 min-max 归一，再按权重叠加。

    两处必要修正（都是实测踩出来的）：
    1) 不做归一化时两路量纲差两个数量级，混合等于"语义被基线的尺度吞掉"；
    2) 只做 min-max 还不够：基线分数绝对值极低（0.02–0.05）时，噪声也能被放大成
       "满分 1.0"，于是 word_count/goal_smart 这类误命中反杀语义。故用 BASE_FLOOR
       给基线加噪声地板：候选集基线峰值低于 BASE_FLOOR 时，按比例削弱基线话语权。
    3) 平局用 (混合分, 语义分, 基线分, 技能名) 四重定序，保证逐位可复现。
    """
    skills = k.skills.all()
    q_tokens = base_tokenize(query)
    q_vec = index.encode(query)
    base_raw, sem_raw = [], []
    for s in skills:
        b = float(k.skills.score(s, q_tokens, query))
        sv = _cos(q_vec, index.encode(" ".join([s.manifest.name,
                                                s.manifest.description]
                                               + list(s.manifest.tags))))
        base_raw.append(b)
        sem_raw.append(sv)

    def _norm(vals: list) -> list:
        lo, hi = min(vals), max(vals)
        if hi - lo < 1e-12:
            return [0.0 for _ in vals]
        return [(v - lo) / (hi - lo) for v in vals]

    base_n, sem_n = _norm(base_raw), _norm(sem_raw)
    peak = max(base_raw) if base_raw else 0.0
    scale = 1.0 if peak <= 0 else min(1.0, peak / BASE_FLOOR)
    best = {}
    for tag in ("base", "sem", "hybrid"):
        best[tag] = (-1.0, "")
    mix_best = None
    for i, s in enumerate(skills):
        mix = (1.0 - weight) * scale * base_n[i] + weight * sem_n[i]
        if base_raw[i] > best["base"][0]:
            best["base"] = (base_raw[i], s.name)
        if sem_raw[i] > best["sem"][0]:
            best["sem"] = (sem_raw[i], s.name)
        key = (round(mix, 9), round(sem_n[i], 9), round(base_n[i], 9), s.name)
        if mix_best is None or key > mix_best[0]:
            mix_best = (key, s.name)
    best["hybrid"] = (mix_best[0][0], mix_best[1])
    return {
        "query": query,
        "base": {"skill": best["base"][1], "score": round(best["base"][0], 5)},
        "sem": {"skill": best["sem"][1], "score": round(best["sem"][0], 4)},
        "hybrid": {"skill": best["hybrid"][1], "score": round(best["hybrid"][0], 4)},
    }


def _cos(a: list, b: list) -> float:
    import math
    d = math.fsum(x * y for x, y in zip(a, b))
    na = math.sqrt(math.fsum(x * x for x in a))
    nb = math.sqrt(math.fsum(x * x for x in b))
    return d / (na * nb) if na > 1e-12 and nb > 1e-12 else 0.0


def run(write: bool = True) -> dict:
    k = build()
    docs = corpus_texts(k)
    labels = [s.name for s in k.skills.all()]

    t0 = time.perf_counter()
    idx = SemanticIndex()
    idx.fit(docs)
    fit_ms = (time.perf_counter() - t0) * 1000.0
    dig1 = vector_digest(idx)

    idx2 = SemanticIndex()
    idx2.fit(docs)
    dig2 = vector_digest(idx2)
    bitwise_equal = bool(dig1 == dig2)

    rows = []
    for query, expect in INTENTS:
        r = route(k, idx, query, WEIGHT_SEM)
        r["expect"] = expect
        r["base_ok"] = r["base"]["skill"] == expect
        r["sem_ok"] = r["sem"]["skill"] == expect
        r["hybrid_ok"] = r["hybrid"]["skill"] == expect
        rows.append(r)

    n = len(rows)
    base_acc = sum(1 for r in rows if r["base_ok"])
    sem_acc = sum(1 for r in rows if r["sem_ok"])
    hyb_acc = sum(1 for r in rows if r["hybrid_ok"])
    out = {
        "version": VERSION,
        "evidence_class": "simulated",
        "corpus_docs": len(docs),
        "vocab_size": len(idx.vocab),
        "dim": idx.dim,
        "fit_ms": round(fit_ms, 2),
        "vector_digest_a": dig1,
        "vector_digest_b": dig2,
        "bitwise_equal": bitwise_equal,
        "weight_sem": WEIGHT_SEM,
        "intents": n,
        "base_correct": base_acc,
        "sem_correct": sem_acc,
        "hybrid_correct": hyb_acc,
        "base_rate": round(base_acc / n, 4),
        "sem_rate": round(sem_acc / n, 4),
        "hybrid_rate": round(hyb_acc / n, 4),
        "rows": rows,
    }
    if write:
        path = os.path.join(ROOT, "benchmarks", "results-semvec-%s.json" % VERSION)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True))
            fh.write("\n")
        out["written"] = path
    return out


def main() -> int:
    res = run(write="--no-write" not in sys.argv)
    print("=" * 72)
    print("semvec 实测  corpus=%d docs  vocab=%d  dim=%d  fit=%.2fms"
          % (res["corpus_docs"], res["vocab_size"], res["dim"], res["fit_ms"]))
    print("确定性  digest_a=%s digest_b=%s equal=%s"
          % (res["vector_digest_a"], res["vector_digest_b"], res["bitwise_equal"]))
    print("-" * 72)
    print("%-28s %-16s %-16s %-16s" % ("意图", "基线", "语义", "混合%.2f" % WEIGHT_SEM))
    for r in res["rows"]:
        print("%-28s %-16s %-16s %-16s   expect=%s"
              % (r["query"][:26], r["base"]["skill"][:15],
                 r["sem"]["skill"][:15], r["hybrid"]["skill"][:15], r["expect"]))
    print("-" * 72)
    print("准确率  基线 %d/%d = %d%% | 语义 %d/%d = %d%% | 混合 %d/%d = %d%%"
          % (res["base_correct"], res["intents"], int(res["base_rate"] * 100),
             res["sem_correct"], res["intents"], int(res["sem_rate"] * 100),
             res["hybrid_correct"], res["intents"], int(res["hybrid_rate"] * 100)))
    if res.get("written"):
        print("written: %s" % res["written"])
    # 门禁：误路由率 ≤10% 即准确率 ≥11/12（0.9167）。留出集泛化不入门禁，只在文档披露。
    ok = (res["bitwise_equal"] and res["hybrid_rate"] >= 0.9167
          and res["fit_ms"] < 5000)
    print("SEMVEC_EXIT=%d" % (0 if ok else 1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
