# -*- coding: utf-8 -*-
"""
红线扫描入口（VERAX 扩展版）
================================================================================
  python scripts/redline_scan.py [目录]                 # 代码红线（AST，默认 holoaeon/）
  python scripts/redline_scan.py --receipts=<目录>       # 追加诚实红线 H1/H2（扫 *.jsonl）

退出码：0 干净 / 1 存在代码违规或 H1 / 2 仅 H2（黄）
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holoaeon.redline import scan_directory  # noqa: E402


def main() -> int:
    argv = sys.argv[1:]
    receipts_dir = None
    target = None
    for item in argv:
        if item.startswith("--receipts="):
            receipts_dir = item.split("=", 1)[1]
        elif not item.startswith("--"):
            target = item
    if target is None:
        target = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "holoaeon")

    rep = scan_directory(target)
    print(f"扫描文件数：{rep['files_scanned']}")
    for v in rep["violations"]:
        print(f"  [{v['kind']}] {v['file']}:{v['line']} — {v['name']}")
    print("结果：", "干净（零违规）" if rep["clean"] else "存在违规")
    code = 0 if rep["clean"] else 1

    if receipts_dir:
        from holoaeon.audit import scan_receipts

        honesty = scan_receipts(receipts_dir)
        print(f"诚实红线：回执 {honesty['receipts']} 条 / H1 {honesty['h1']} / "
              f"H2 {honesty['h2']}")
        for problem in honesty["problems"][:10]:
            print(f"  [{problem['rule']}] {problem['source']} — {problem['detail']}")
        if honesty["h1"]:
            code = max(code, 1)
        elif honesty["h2"]:
            code = max(code, 2)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
