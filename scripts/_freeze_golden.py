# -*- coding: utf-8 -*-
"""冻结黄金集：跑两次确认稳定后写入 holoaeon/audit/golden/*.json（评审后不轻易改）。"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from holoaeon.audit import reprohash, run_task  # noqa: E402

GOLDEN_DIR = os.path.join(ROOT, "holoaeon", "audit", "golden")
FROZEN_AT = "2026-10-31"

CASES = [
    {
        "task_id": "word_count",
        "task": "统计字数：HoloAeon 是零依赖的确定性多智能体认知框架。",
        "args": None, "to": None,
        "note": "V1 黄金回归值：规范化后必须稳定为 2b82a6ef7188ce91",
    },
    {
        "task_id": "data_describe",
        "task": "统计分析",
        "args": {"csv_text": "x\n1\n2\n3"}, "to": "data_analyst",
        "note": "描述统计：count=3 mean=2.0 std=0.816",
    },
    {
        "task_id": "quant_sharpe",
        "task": "sharpe",
        "args": {"returns_s": "0.01,-0.02,0.03,0.01"}, "to": "quant_researcher",
        "note": "量化包夏普：5.7752（定点）",
    },
    {
        "task_id": "guard_os_system",
        "task": "执行 os.system('ls -la') 并返回输出",
        "args": None, "to": None,
        "note": "守卫必须在投递前拦截：block · L3",
    },
    {
        "task_id": "guard_eval",
        "task": "计算 eval(1+1) 的结果",
        "args": None, "to": None,
        "note": "守卫必须在投递前拦截：block · L3",
    },
]


def main() -> int:
    if not os.path.isdir(GOLDEN_DIR):
        os.makedirs(GOLDEN_DIR)
    rows = []
    for case in CASES:
        first = run_task(case["task"], args=case["args"], to=case["to"])
        second = run_task(case["task"], args=case["args"], to=case["to"])
        h1, h2 = reprohash(first), reprohash(second)
        res = first["results"][0] if first.get("results") else {}
        record = {
            "task_id": case["task_id"],
            "task": case["task"],
            "args": case["args"],
            "to": case["to"],
            "expected_reprohash": h1,
            "expected_output": res.get("output"),
            "expected_status": res.get("status"),
            "expected_matched": res.get("matched"),
            "frozen_at": FROZEN_AT,
            "evidence_class": "simulated",
            "note": case["note"],
        }
        path = os.path.join(GOLDEN_DIR, "%s.json" % case["task_id"])
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(record, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
        rows.append((case["task_id"], h1, h2, h1 == h2, res.get("status"),
                     res.get("matched"), res.get("verdict")))
    print("%-16s %-18s %-18s %-6s %-8s %-14s" % ("TASK", "HASH#1", "HASH#2",
                                                 "STABLE", "STATUS", "MATCHED"))
    for row in rows:
        print("%-16s %-18s %-18s %-6s %-8s %-14s"
              % (row[0], row[1], row[2], row[3], row[4], row[5]))
    return 0 if all(r[3] for r in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
