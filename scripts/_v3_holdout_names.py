# -*- coding: utf-8 -*-
"""核查留出集期望名是否存在，并打印每条的 top3 候选，区分「期望写错」与「真错」。"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import bench_semvec as B  # noqa: E402

HOLDOUT = [
    ("算一下这组数的最大值和最小值", "basic_stats"),
    ("这篇论文讲了什么，给我摘要", "extract_abstract"),
    ("把论文列表去掉重复的", "dedup_papers"),
    ("检查账本指纹是否一致", "replay_check"),
    ("按收益率序列回测策略", "backtest"),
    ("写一段产品文案", "copywriting"),
]

k = B.build()
idx = B.SemanticIndex()
idx.fit(B.corpus_texts(k))
names = set(s.name for s in k.skills.all())

for q, expect in HOLDOUT:
    rows = sorted(B.route(k, idx, q, B.WEIGHT_SEM).values(), key=lambda x: 0)
    r = B.route(k, idx, q, B.WEIGHT_SEM)
    print("Q %s | expect=%s exists=%s | hyb=%s" % (q, expect, expect in names, r["hybrid"]["skill"]))
print()
print("候选名包含关键词：")
for kw in ("stat", "abstract", "dedup", "replay", "back", "copy", "text", "summary"):
    hits = sorted(n for n in names if kw in n)
    print("  %-9s %s" % (kw, hits[:8]))
