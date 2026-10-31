# -*- coding: utf-8 -*-
"""留出集实测：未参与调参的意图，用来估算泛化而非宣称 100%。
口径说明：留出集只作披露，不进门禁（门禁仍以 12 条固定意图为准，保持可复跑）。"""
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

ok = 0
for q, expect in HOLDOUT:
    r = B.route(k, idx, q, B.WEIGHT_SEM)
    hit = r["hybrid"]["skill"] == expect
    ok += hit
    print("%s %-24s hyb=%-20s expect=%s" % ("ok  " if hit else "MISS", q[:22],
                                            r["hybrid"]["skill"][:18], expect))
print("holdout=%d/%d" % (ok, len(HOLDOUT)))
