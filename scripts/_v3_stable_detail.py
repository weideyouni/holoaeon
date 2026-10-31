"""稳定语料单点明细：vocab=1200 / w=0.75 / floor=0.15，逐条打印。"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import holoaeon.semvec as sv  # noqa: E402
from holoaeon.semvec import SemanticIndex, docs_from_skills  # noqa: E402
from _v3_tune_stable import INTENTS, build_kernel, route  # noqa: E402

sv.MAX_VOCAB = 1200
k = build_kernel()
docs = docs_from_skills(k.skills.all())
idx = SemanticIndex()
idx.fit(docs)
print("docs=%d vocab=%d" % (len(docs), len(idx.vocab)))
for q, want in INTENTS:
    got = route(k, idx, q, 0.75, 0.15)
    print("%-6s %-22s -> %-18s expect=%s" % ("OK" if got == want else "MISS", q, got, want))
