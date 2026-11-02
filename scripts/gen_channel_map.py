# -*- coding: utf-8 -*-
"""B2b 12→17 通道映射表：data/channel_map.csv + data/channel_map.json

用法：python scripts/gen_channel_map.py [--check]

口径：
  · 12 条 LC01–LC12 逐行写死分组（气5 / 血4 / 神3 / 淋巴0），禁止按序号取模推导通道
  · 目标 17 通道 = 气5 + 血4 + 神4 + 淋巴4；未映射 pending=5（神 1 / 淋巴 4）
  · 单行单组，同一 LC 不跨组；映射关系与 contract.channel_map() 同源
不写时间戳，复跑字节一致。
"""
import csv
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from holoaeon.fusion_upgrade import contract as c

CSV_OUT = os.path.join(ROOT, "data", "channel_map.csv")
JSON_OUT = os.path.join(ROOT, "data", "channel_map.json")
HEADER = ["lc", "group", "target_group", "status", "rule"]


def build():
    ch = c.channel_map()
    rows = [{k: r[k] for k in HEADER} for r in ch["rows"]]
    doc = {
        "map_id": "SG-CHANNEL-MAP-HOLOAEON-IVSA-V1",
        "batch": "B2b",
        "frozen_at": "2026-11-02",
        "evidence_class": "simulated",
        "rows": rows,
        "row_count": len(rows),
        "mapped": ch["mapped"],
        "targets": ch["targets"],
        "pending": ch["pending"],
        "pending_detail": ch["pending_detail"],
        "no_arithmetic": ch["no_arithmetic"],
        "arithmetic_policy": "禁止按行序号取模推导通道；12 行写死，未映射目标登记待办（写法见坑表 V4-5）",
        "rule_note": "12 行写死；未映射目标登记为待办，不许用补位/取模补齐",
    }
    return doc, rows


def csv_text(rows):
    import io
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=HEADER, lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow(r)
    return buf.getvalue()


def main(argv):
    doc, rows = build()
    text = csv_text(rows)
    doc["csv_sha256"] = hashlib.sha256(text.encode("utf-8")).hexdigest()

    if "--check" in argv:
        ok = True
        for p, content in ((CSV_OUT, text),
                           (JSON_OUT, json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=True) + "\n")):
            if not os.path.isfile(p):
                ok = False
                continue
            with open(p, encoding="utf-8") as f:
                if f.read() != content:
                    ok = False
        print(json.dumps({"verdict": "PASS" if ok else "FAIL", "byte_consistent": ok}, ensure_ascii=False))
        return 0 if ok else 1

    with open(CSV_OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    with open(JSON_OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"csv": CSV_OUT, "json": JSON_OUT, "row_count": len(rows),
                      "mapped": doc["mapped"], "targets": doc["targets"],
                      "pending": doc["pending"], "csv_sha256": doc["csv_sha256"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
