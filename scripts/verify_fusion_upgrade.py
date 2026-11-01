# -*- coding: utf-8 -*-
"""验收入口：fusion_upgrade 自检（17 项）

  python scripts/verify_fusion_upgrade.py            # 人类可读
  python scripts/verify_fusion_upgrade.py --json     # 机器可读
退出码：0 全绿 / 1 有失败
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holoaeon.fusion_upgrade.selftest import run  # noqa: E402


def main() -> int:
    as_json = "--json" in sys.argv[1:]
    result = run()
    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=1))
    else:
        print("=" * 66)
        print("fusion_upgrade 自检（冷热插拔 + 内外融合协议 + 契约 + 十二批 + 快照）")
        print("=" * 66)
        for item in result["checks"]:
            print("%s %-24s %s" % ("[OK]" if item["ok"] else "[NG]",
                                   item["check"], item["detail"]))
        print("-" * 66)
        print("结果：%d/%d %s" % (result["passed"], result["total"],
                                 "全绿" if result["ok"] else "有失败"))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
