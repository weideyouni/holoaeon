# -*- coding: utf-8 -*-
"""在 2000 词表下打印逐条命中的三个通道，并对混合权重做扫描。"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import bench_semvec as B  # noqa: E402
import holoaeon.semvec as S  # noqa: E402

S.MAX_VOCAB = 2000
S.MIN_DF = 1

k = B.build()
docs = B.corpus_texts(k)
idx = S.SemanticIndex()
idx.fit(docs)
print("vocab=%d" % len(idx.vocab))

for q, expect in B.INTENTS:
    r = B.route(k, idx, q, 0.5)
    flag = "ok " if r["hybrid"]["skill"] == expect else "MISS"
    print("%s %-26s base=%-18s sem=%-18s hyb=%-18s expect=%s"
          % (flag, q[:24], r["base"]["skill"][:16], r["sem"]["skill"][:16],
             r["hybrid"]["skill"][:16], expect))

print()
for w in (0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8):
    ok = 0
    for q, expect in B.INTENTS:
        r = B.route(k, idx, q, w)
        ok += r["hybrid"]["skill"] == expect
    print("weight=%.1f hybrid=%d/12" % (w, ok))
