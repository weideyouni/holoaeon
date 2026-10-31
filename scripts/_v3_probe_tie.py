"""打印 '给这列数据算均值和标准差' 的候选前三，确认是否平局。"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import bench_semvec as B  # noqa: E402
from holoaeon.semvec import SemanticIndex  # noqa: E402
from holoaeon.kernel import Kernel  # noqa: E402
from holoaeon.packs import PACK_ORDER, get_pack  # noqa: E402

k = Kernel()
for key in PACK_ORDER:
    get_pack(key).install(k)
idx = SemanticIndex()
idx.fit(B.corpus_texts(k))

q = "给这列数据算均值和标准差"
q_tokens = B.base_tokenize(q)
q_vec = idx.encode(q)
rows = []
for s in k.skills.all():
    b = float(k.skills.score(s, q_tokens, q))
    se = B._cos(q_vec, idx.encode(" ".join(
        [s.manifest.name, s.manifest.description] + list(s.manifest.tags))))
    rows.append((s.name, b, se))
def _norm(vals):
    lo, hi = min(vals), max(vals)
    if hi - lo < 1e-12:
        return [0.0 for _ in vals]
    return [(v - lo) / (hi - lo) for v in vals]


bs = _norm([r[1] for r in rows])
ss = _norm([r[2] for r in rows])
peak = max(r[1] for r in rows)
scale = 1.0 if peak <= 0 else min(1.0, peak / B.BASE_FLOOR)
print("peak=%.6f scale=%.6f n=%d" % (peak, scale, len(rows)))
mix = [(rows[i][0], (1 - B.WEIGHT_SEM) * scale * bs[i] + B.WEIGHT_SEM * ss[i],
       bs[i], ss[i]) for i in range(len(rows))]
for name, m, b, s in sorted(mix, key=lambda t: -t[1])[:4]:
    print("  %-18s mix=%.9f base_n=%.9f sem_n=%.9f" % (name, m, b, s))
