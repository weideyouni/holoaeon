#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把一段视频的逐字稿压成可复算的张量规格（幂等）。

输入：transcript.txt（飞书妙记产物，Speaker N HH:MM:SS.mmm 分块）
输出：blocks.json / concept_matrix.csv / tensor_spec.json / digest.txt

指纹口径固定：sha256(json([[i,t,chars,questions,n_num]+概念计数行], separators=(",",":"))[:])
同一输入两次运行 digest 必等；改轴/改段/改正文必变；改人工标注不变。

用法：
  python build_tensor.py --transcript <t.txt> --out <dir>
  python build_tensor.py --transcript <t.txt> --out <dir> --axes "空间,时空,引力"
  python build_tensor.py --transcript <t.txt> --out <dir> --axes-json axes.json
"""
import argparse
import csv
import hashlib
import json
import os
import re

# 默认 24 轴（冻结档；扩轴请另立 profile，不要原地改）
PROFILE_SPACE = [
    "空间", "时空", "牛顿", "莱布尼茨", "爱因斯坦", "广义相对论",
    "引力", "引力波", "黑洞", "质量", "时间", "光年",
    "实验", "观察", "天文台", "刚性", "弹性波", "能量",
    "量子", "量子纠缠", "涌现", "信息", "微观", "宇宙",
]

SEG_RE = re.compile(r"Speaker\s*(\d+)\s+(\d{2}):(\d{2}):(\d{2})\.(\d{3})\s+")
NUM_RE = re.compile(r"[0-9]+(?:\.[0-9]+)?")
Q_RE = re.compile(r"[？?]")


def split_blocks(raw):
    pos = list(SEG_RE.finditer(raw))
    blocks = []
    for i, m in enumerate(pos):
        start = m.end()
        end = pos[i + 1].start() if i + 1 < len(pos) else len(raw)
        body = raw[start:end].strip()
        if not body:
            continue
        t = (int(m.group(2)) * 3600 + int(m.group(3)) * 60
             + int(m.group(4)) + int(m.group(5)) / 1000)
        blocks.append({"i": len(blocks) + 1, "t": round(t, 1), "text": body})
    return blocks, len(pos)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--transcript", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--axes", default="", help="逗号分隔的概念轴，覆盖默认 24 轴")
    ap.add_argument("--axes-json", default="", help="{\"concepts\": [...]} 形式的轴文件")
    ap.add_argument("--name", default="video-tensor")
    ap.add_argument("--duration", type=float, default=0.0, help="视频时长（秒），用于 A2 自检")
    args = ap.parse_args()

    if args.axes_json:
        with open(args.axes_json, encoding="utf-8") as f:
            concepts = json.load(f)["concepts"]
    elif args.axes:
        concepts = [c.strip() for c in args.axes.split(",") if c.strip()]
    else:
        concepts = list(PROFILE_SPACE)

    os.makedirs(args.out, exist_ok=True)
    with open(args.transcript, "r", encoding="utf-8") as f:
        raw = f.read()
    blocks, n_marks = split_blocks(raw)

    for b in blocks:
        txt = b["text"]
        b["chars"] = len(txt)
        b["questions"] = len(Q_RE.findall(txt))
        b["numerals"] = NUM_RE.findall(txt)
        b["n_num"] = len(b["numerals"])
        b["concept_hits"] = dict((c, txt.count(c)) for c in concepts if c in txt)
        b["concept_count"] = sum(b["concept_hits"].values())
        b["distinct_concepts"] = len(b["concept_hits"])

    mat = [[b["concept_hits"].get(c, 0) for c in concepts] for b in blocks]
    nnz = sum(1 for row in mat for v in row if v)
    cells = len(blocks) * len(concepts)

    first_seen = {}
    for j, c in enumerate(concepts):
        for i, row in enumerate(mat):
            if row[j]:
                first_seen[c] = i + 1
                break

    stats = {
        "blocks": len(blocks),
        "speaker_marks": n_marks,
        "duration_s": blocks[-1]["t"] if blocks else 0.0,
        "chars_total": sum(b["chars"] for b in blocks),
        "chars_mean": round(sum(b["chars"] for b in blocks) / len(blocks), 1) if blocks else 0.0,
        "chars_max": max([b["chars"] for b in blocks]) if blocks else 0,
        "questions_total": sum(b["questions"] for b in blocks),
        "numerals_total": sum(b["n_num"] for b in blocks),
        "concept_cells": cells,
        "concept_nnz": nnz,
        "concept_density": round(nnz / cells, 4) if cells else 0.0,
        "concept_hits_total": sum(b["concept_count"] for b in blocks),
        "concept_hits_mean_per_block": round(
            sum(b["concept_count"] for b in blocks) / len(blocks), 2) if blocks else 0.0,
    }

    spec = {
        "name": args.name,
        "shape": [len(blocks), len(concepts), 4],
        "axes": {
            "d0_segment": "语段（按说话人块切分，时间升序）",
            "d1_concept": "概念轴（%d 个，本次冻结，不可增删）" % len(concepts),
            "d2_feature": ["出现频次", "论证角色", "证据等级", "认知层级"],
        },
        "note": "d2 第 2-4 维为人工标注 ordinal 值，不进指纹；第 1 维为现算计数。",
        "density_d0_d1": stats["concept_density"],
    }

    canon = [[b["i"], b["t"], b["chars"], b["questions"], b["n_num"]] + row
             for b, row in zip(blocks, mat)]
    blob = json.dumps(canon, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    digest = hashlib.sha256(blob).hexdigest()

    json.dump(blocks, open(os.path.join(args.out, "blocks.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    with open(os.path.join(args.out, "concept_matrix.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["block", "t_sec"] + concepts)
        for b, row in zip(blocks, mat):
            w.writerow([b["i"], b["t"]] + row)
    json.dump({"spec": spec, "stats": stats, "first_seen": first_seen, "digest": digest},
              open(os.path.join(args.out, "tensor_spec.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    open(os.path.join(args.out, "digest.txt"), "w", encoding="utf-8").write(digest + "\n")

    warn = []
    if n_marks and len(blocks) != n_marks:
        warn.append("空段 %d 个被跳过（marks=%d, blocks=%d）" % (n_marks - len(blocks), n_marks, len(blocks)))
    if args.duration and blocks and abs(blocks[-1]["t"] - args.duration) > 30:
        warn.append("末段 t=%.1f 与视频时长 %.1f 相差超过 30 秒" % (blocks[-1]["t"], args.duration))

    print(json.dumps({"digest": digest, "stats": stats, "warnings": warn,
                      "first_seen": first_seen}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
