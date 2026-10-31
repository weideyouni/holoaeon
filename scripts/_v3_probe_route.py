# -*- coding: utf-8 -*-
"""诊断脚本：打印错案各通道原始分数与文档文本，定位语义通道的偏差来源。"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import bench_semvec as B  # noqa: E402

FAILS = [
    ("给这列数据算均值和标准差", "basic_stats"),
    ("写周报总结", "weekly_review"),
    ("设计实验的样本量", "sample_size"),
]

k = B.build()
docs = B.corpus_texts(k)
idx = B.SemanticIndex()
idx.fit(docs)
skills = k.skills.all()

for q, expect in FAILS:
    qv = idx.encode(q)
    q_tokens = B.base_tokenize(q)
    rows = []
    for s in skills:
        m = s.manifest
        txt = " ".join([m.name, m.description] + list(m.tags))
        b = float(k.skills.score(s, q_tokens, q))
        sv = B._cos(qv, idx.encode(txt))
        rows.append((b, sv, m.name, m.description[:40]))
    rows.sort(key=lambda r: -r[0])
    print("=" * 70)
    print("QUERY:", q, " expect:", expect)
    print("-- top by base --")
    for b, sv, name, desc in rows[:5]:
        print("  base=%.4f sem=%.4f  %-24s %s" % (b, sv, name, desc))
    rows2 = sorted(rows, key=lambda r: -r[1])
    print("-- top by sem --")
    for b, sv, name, desc in rows2[:5]:
        print("  base=%.4f sem=%.4f  %-24s %s" % (b, sv, name, desc))
    for name in {expect} | {rows2[0][2]}:
        for s in skills:
            if s.manifest.name == name:
                print("  [doc] %s :: %s" % (name, (" ".join([s.manifest.name, s.manifest.description] + list(s.manifest.tags)))[:160]))
