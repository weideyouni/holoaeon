# -*- coding: utf-8 -*-
"""在候选混合公式上做小网格：语义权重 × 基线噪声地板 × 三重 tie-break，求逐条命中。"""
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
skills = k.skills.all()


def score_all(query):
    q_tokens = B.base_tokenize(query)
    q_vec = idx.encode(query)
    out = []
    for s in skills:
        m = s.manifest
        txt = " ".join([m.name, m.description] + list(m.tags))
        b = float(k.skills.score(s, q_tokens, query))
        sv = B._cos(q_vec, idx.encode(txt))
        out.append((b, sv, m.name))
    return out


def norm(vals):
    lo, hi = min(vals), max(vals)
    if hi - lo < 1e-12:
        return [0.0 for _ in vals]
    return [(v - lo) / (hi - lo) for v in vals]


for w in (0.5, 0.6, 0.7, 0.75, 0.8):
    for floor in (0.0, 0.06, 0.10, 0.15):
        ok = 0
        misses = []
        for q, expect in B.INTENTS:
            rows = score_all(q)
            base = [r[0] for r in rows]
            sem = [r[1] for r in rows]
            bn, sn = norm(base), norm(sem)
            scale = 1.0 if floor <= 0 else min(1.0, max(base) / floor)
            best = None
            for i, (b, sv, name) in enumerate(rows):
                mix = (1.0 - w) * scale * bn[i] + w * sn[i]
                key = (round(mix, 9), round(sn[i], 9), round(bn[i], 9), name)
                if best is None or key > best[0]:
                    best = (key, name)
            if best[1] == expect:
                ok += 1
            else:
                misses.append(q)
        print("w=%.2f floor=%.2f -> %d/12  misses=%s" % (w, floor, ok, ";".join(misses[:3])))
