# -*- coding: utf-8 -*-
"""一次性对齐：把文档里的 30.77ms 改成 ≈31ms（装配耗时随运行波动，精确值在 json）。"""
import os

TARGETS = [
    "README_DIFF0_20261031.md",
    "AGENT_FEED_DIFF0_20261031.md",
    "docs/cookbooks.md",
    "cookbooks/03_offline_deploy_old_laptop/README.md",
    "snapshot/SNAPSHOT.md",
]

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REPL = [
    ("30.77ms", "≈31ms"),
    ("30.77 ms", "≈31 ms"),
    ("30.77", "≈31"),
]

for rel in TARGETS:
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        print("skip(missing)", rel)
        continue
    with open(p, encoding="utf-8") as fh:
        s = fh.read()
    old = s
    for a, b in REPL:
        s = s.replace(a, b)
    if s != old:
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(s)
        print("patched", rel)
    else:
        print("unchanged", rel)
