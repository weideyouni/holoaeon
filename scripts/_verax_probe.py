# -*- coding: utf-8 -*-
"""临时探针：确认 VERAX 规范化哈希与既往 2b82a6ef7188ce91 口径一致。"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from holoaeon.audit import canonicalize_report, reprohash, run_task  # noqa: E402

TASK = "统计字数：HoloAeon 是零依赖的确定性多智能体认知框架。"

o1 = run_task(TASK)
o2 = run_task(TASK)
h1, h2 = reprohash(o1), reprohash(o2)
canon, unknown = canonicalize_report(o1)

print("hash_1 =", h1)
print("hash_2 =", h2)
print("stable =", h1 == h2, "| match_legacy =", h1 == "2b82a6ef7188ce91")
print("unknown =", unknown)
print("matched =", [r.get("matched") for r in o1["results"]])
print("output  =", json.dumps(o1["results"][0].get("output"), ensure_ascii=False))
print("canon_keys =", sorted(canon.keys()))
print("canon_result_keys =", sorted(canon["results"][0].keys()))

data = run_task("统计分析", args={"csv_text": "x\n1\n2\n3"}, to="data_analyst")
print("data_out =", json.dumps(data["results"][0].get("output"), ensure_ascii=False))
print("data_hash =", reprohash(data))

sharpe = run_task("sharpe", args={"returns_s": "0.01,-0.02,0.03,0.01"},
                  to="quant_researcher")
print("sharpe_out =", json.dumps(sharpe["results"][0].get("output"),
                                ensure_ascii=False))
print("sharpe_hash =", reprohash(sharpe))
