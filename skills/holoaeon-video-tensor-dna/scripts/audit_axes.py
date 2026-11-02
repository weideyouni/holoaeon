#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""轴体检：抓「名义维度满格、实际有轴空转」这类静默失真。

读 tensor_spec.json + concept_matrix.csv，输出每轴命中、空轴、冷轴、每段 distinct。
退出码：0 通过；1 有空轴或轴过粗；2 读取失败。
"""
import argparse
import csv
import json
import os
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True, help="build_tensor.py 的输出目录")
    ap.add_argument("--cold-max", type=int, default=1, help="命中数不超过此值算冷轴")
    ap.add_argument("--min-distinct", type=int, default=8, help="单段 distinct 的期望上界")
    args = ap.parse_args()

    try:
        with open(os.path.join(args.dir, "tensor_spec.json"), encoding="utf-8") as f:
            spec = json.load(f)
        with open(os.path.join(args.dir, "concept_matrix.csv"), encoding="utf-8-sig",
                  newline="") as f:
            rows = list(csv.reader(f))
    except Exception as e:  # noqa: BLE001
        print("读取失败：%s" % e)
        return 2

    header = rows[0]
    concepts = header[2:]
    data = [r for r in rows[1:] if r]
    per_axis = dict((c, sum(int(r[2 + j]) for r in data)) for j, c in enumerate(concepts))
    empty = [c for c, v in per_axis.items() if v == 0]
    cold = [c for c, v in per_axis.items() if 0 < v <= args.cold_max]
    distinct = [sum(1 for v in r[2:] if int(v)) for r in data]

    print("blocks=%d axes=%d cells=%d nnz=%d density=%s"
          % (len(data), len(concepts), spec["stats"]["concept_cells"],
             spec["stats"]["concept_nnz"], spec["stats"]["concept_density"]))
    print("empty_axes=%d %s" % (len(empty), empty))
    print("cold_axes=%d %s" % (len(cold), cold))
    print("distinct max=%d min=%d mean=%.2f"
          % (max(distinct), min(distinct), sum(distinct) / len(distinct)))
    print("top5 " + ", ".join("%s:%d" % (c, v) for c, v in
                             sorted(per_axis.items(), key=lambda kv: -kv[1])[:5]))

    bad = []
    if empty:
        bad.append("存在空轴（词表与原文用词不一致）：%s" % empty)
    if len(concepts) and len(cold) > len(concepts) // 6:
        bad.append("冷轴过多：%d/%d" % (len(cold), len(concepts)))
    if distinct and max(distinct) < args.min_distinct:
        bad.append("轴过粗：单段最多只命中 %d 个轴（期望 ≥%d）" % (max(distinct), args.min_distinct))

    for b in bad:
        print("FAIL " + b)
    print("PASS" if not bad else "MISS")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
