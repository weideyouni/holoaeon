"""打印 weekly_review / extract_abstract 的清单文本与切词结果。"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from holoaeon.semvec import tokenize  # noqa: E402
from holoaeon.kernel import Kernel  # noqa: E402
from holoaeon.packs import PACK_ORDER, get_pack  # noqa: E402

k = Kernel()
for key in PACK_ORDER:
    get_pack(key).install(k)

for name in ("weekly_review", "extract_abstract"):
    m = k.skills.get(name).manifest
    raw = " ".join([m.name, m.description] + list(m.tags))
    print("[%s]" % name)
    print("  desc:", m.description)
    print("  tags:", m.tags)
    print("  toks:", tokenize(raw))
print("[query 写周报总结]")
print("  toks:", tokenize("写周报总结"))
