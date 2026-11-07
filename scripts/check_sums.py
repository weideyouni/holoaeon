# -*- coding: utf-8 -*-
"""check_sums — SHA256SUMS 复算闸（V38，千问 V37 P0 修复）
第一性原理：每个数字都能复算。闸只阻断不重建（重建=批次动作，
自动重建会掩盖追溯性）。改元文件→跑批次重建→闸放行。
零依赖纯标准库。封口密语：潮起开门，潮落闭嘴。
"""
import hashlib
import io
import json
import os
import sys

SEAL = "潮起开门，潮落闭嘴"


def verify(sums_path="SHA256SUMS", root=None):
    root = root or os.getcwd()
    mismatches, unreadable, total = [], [], 0
    p = os.path.join(root, sums_path)
    if not os.path.exists(p):
        return {"ok": False, "error": "SHA256SUMS not found", "seal": SEAL}
    with io.open(p, encoding="utf-8", errors="ignore") as fh:   # C-06 句柄 with
        for line in fh:
            parts = line.split()
            if len(parts) < 2:
                continue
            total += 1
            f = parts[-1]
            fp = os.path.join(root, f)
            try:
                with io.open(fp, "rb") as bf:
                    h = hashlib.sha256(bf.read()).hexdigest()
                if h != parts[0]:
                    mismatches.append({"file": f, "listed": parts[0][:12],
                                       "actual": h[:12]})
            except Exception as e:
                unreadable.append({"file": f, "error": str(e)[:60]})
    return {"ok": not mismatches and not unreadable,
            "total": total, "mismatches": mismatches,
            "unreadable": unreadable,
            "action": "report_only",                             # C-08 拆分，不作隐式拼接
            "action_note": "重建由批次流程执行，闸只阻断",
            "seal": SEAL}


def main(argv):
    root = argv[1] if len(argv) > 1 else os.getcwd()
    r = verify("SHA256SUMS", root)
    print(json.dumps(r, ensure_ascii=False, indent=1))
    return 0 if r["ok"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
