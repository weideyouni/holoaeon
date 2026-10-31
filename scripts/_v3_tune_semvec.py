# -*- coding: utf-8 -*-
"""网格实测：MIN_DF × MAX_VOCAB × 混合权重，对 12 条意图求准确率。只为找可行组合，不写文档。"""
import itertools
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import bench_semvec as B  # noqa: E402
import holoaeon.semvec as S  # noqa: E402

k = B.build()
docs = B.corpus_texts(k)

print("%-8s %-6s %-6s %-8s %-10s %-10s %-10s" % ("maxvocab", "mindf", "vocab", "fit_ms", "base", "sem", "hybrid"))
for maxv, mindf in itertools.product([300, 800, 1200, 2000], [1, 2]):
    S.MAX_VOCAB = maxv
    S.MIN_DF = mindf
    t0 = time.perf_counter()
    idx = S.SemanticIndex()
    idx.fit(docs)
    fit_ms = (time.perf_counter() - t0) * 1000.0
    base_ok = sem_ok = hyb_ok = 0
    for q, expect in B.INTENTS:
        r = B.route(k, idx, q, 0.5)
        base_ok += r["base"]["skill"] == expect
        sem_ok += r["sem"]["skill"] == expect
        hyb_ok += r["hybrid"]["skill"] == expect
    print("%-8d %-6d %-6d %-8.1f %-10s %-10s %-10s"
          % (maxv, mindf, len(idx.vocab), fit_ms,
             "%d/12" % base_ok, "%d/12" % sem_ok, "%d/12" % hyb_ok))
