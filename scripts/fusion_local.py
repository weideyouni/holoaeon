# -*- coding: utf-8 -*-
"""fusion_local.py —— 冷热插拔与内外融合协议的本地操作台（本机可跑、可复算）

用法：
  python scripts/fusion_local.py status                     # 清单 + 现算锁值
  python scripts/fusion_local.py install fusion_upgrade     # 运行期热插拔
  python scripts/fusion_local.py uninstall fusion_upgrade
  python scripts/fusion_local.py roundtrip fusion_upgrade    # 装→卸→逐名比对
  python scripts/fusion_local.py fuse                        # 内外协议全量演练
  python scripts/fusion_local.py contract                    # 契约/六机制/通道映射
  python scripts/fusion_local.py plan [B0]                   # 十二批计划
  python scripts/fusion_local.py snapshot [输出路径]          # 生成项目快照
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holoaeon.fusion_upgrade import contract, plan, protocol, snapshot, swap  # noqa: E402
from holoaeon.fusion_upgrade import manifest as mf  # noqa: E402
from holoaeon.kernel import Kernel  # noqa: E402
from holoaeon.packs import PACK_ORDER, get_extra_pack, get_pack  # noqa: E402


def _kernel(with_self: bool = False) -> Kernel:
    k = Kernel()
    for key in PACK_ORDER:
        get_pack(key).install(k)
    if with_self:
        get_extra_pack("fusion_upgrade").install(k)
    return k


def cmd_status(_args: argparse.Namespace) -> int:
    k = _kernel()
    m = mf.manifest()
    print("内核锁值：agents=%d skills=%d packs=%d"
          % (len(k.agents), len(k.skills.names()), len(PACK_ORDER)))
    print("清单：core=%d extra=%d digest=%s"
          % (m["counts"]["core"], m["counts"]["extra"], m["digest"]))
    for row in m["rows"]:
        print("  [%s] %-18s skills=%-3d roles=%-2d rollback=%s"
              % (row["plug"], row["key"], row["skill_count"], row["role_count"],
                 row["rollback"]))
    return 0


def cmd_install(args: argparse.Namespace) -> int:
    print(json.dumps(swap.hot_install(_kernel(), args.key), ensure_ascii=False, indent=1))
    return 0


def cmd_uninstall(args: argparse.Namespace) -> int:
    print(json.dumps(swap.hot_uninstall(_kernel(with_self=True), args.key),
                     ensure_ascii=False, indent=1))
    return 0


def cmd_roundtrip(args: argparse.Namespace) -> int:
    k = _kernel()
    rt = swap.probe_roundtrip(k, args.key)
    print(json.dumps(rt, ensure_ascii=False, indent=1))
    print("往返一致：%s；内核仍为 agents=%d skills=%d"
          % (rt["ok"], len(k.agents), len(k.skills.names())))
    return 0 if rt["ok"] else 1


def cmd_fuse(_args: argparse.Namespace) -> int:
    k = _kernel(with_self=True)
    rec = protocol.fuse(k)
    out = os.path.join("reports", "fusion_receipts.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(rec, fh, ensure_ascii=False, indent=1)
    print("内部协议：%s  步骤：%s"
          % (rec["internal"]["ok"], [s["step"] for s in rec["internal"]["steps"]]))
    for step in rec["internal"]["steps"]:
        print("  %s %-12s %s" % ("[OK]" if step["ok"] else "[NG]",
                                 step["step"], step["evidence"]))
    print("外部协议：%s  路由：%s  网络调用：%d"
          % (rec["external"]["ok"], [r.get("choice") for r in rec["external"]["routes"]],
             rec["external"]["network_calls"]))
    print("合并回执：ok=%s seal=%s -> %s" % (rec["ok"], rec["seal"], out))
    return 0 if rec["ok"] else 1


def cmd_contract(_args: argparse.Namespace) -> int:
    doc = contract.make("holoaeon", "ivsa", "matrix_dispatch", "skin_v6", "read")
    print("样例契约：", json.dumps(doc, ensure_ascii=False))
    print("校验：", json.dumps(contract.validate(doc), ensure_ascii=False))
    print("回执：", json.dumps(contract.receipt(doc), ensure_ascii=False))
    print("六机制：%d 行 %s" % (contract.pairs()["rows"], contract.pairs()["mechanisms"]))
    ch = contract.channel_map()
    print("通道映射：%d/17 已映射，待办 %d %s"
          % (ch["mapped"], ch["pending"], ch["pending_detail"]))
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    if args.batch:
        print(json.dumps(plan.get(args.batch), ensure_ascii=False, indent=1))
        return 0
    print(json.dumps(plan.summary(), ensure_ascii=False, indent=1))
    v = plan.validate()
    print("九字段校验：ok=%s problems=%d" % (v["ok"], len(v["problems"])))
    return 0 if v["ok"] else 1


def cmd_snapshot(args: argparse.Namespace) -> int:
    res = snapshot.write(args.path or "")
    print(json.dumps(res, ensure_ascii=False, indent=1))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="冷热插拔 + 内外融合协议本地操作台")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("status")
    p.set_defaults(func=cmd_status)
    for name, fn in (("install", cmd_install), ("uninstall", cmd_uninstall),
                     ("roundtrip", cmd_roundtrip)):
        q = sub.add_parser(name)
        q.add_argument("key", nargs="?", default="fusion_upgrade")
        q.set_defaults(func=fn)
    for name, fn in (("fuse", cmd_fuse), ("contract", cmd_contract)):
        sub.add_parser(name).set_defaults(func=fn)
    q = sub.add_parser("plan")
    q.add_argument("batch", nargs="?", default="")
    q.set_defaults(func=cmd_plan)
    q = sub.add_parser("snapshot")
    q.add_argument("path", nargs="?", default="")
    q.set_defaults(func=cmd_snapshot)
    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
