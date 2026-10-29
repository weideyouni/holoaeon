# -*- coding: utf-8 -*-
"""红线扫描入口：python scripts/redline_scan.py [目录]"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holoaeon.redline import scan_directory  # noqa: E402


def main() -> int:
    target = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "holoaeon")
    rep = scan_directory(target)
    print(f"扫描文件数：{rep['files_scanned']}")
    for v in rep["violations"]:
        print(f"  [{v['kind']}] {v['file']}:{v['line']} — {v['name']}")
    print("结果：", "干净（零违规）" if rep["clean"] else "存在违规")
    return 0 if rep["clean"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
