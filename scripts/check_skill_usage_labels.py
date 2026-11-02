# -*- coding: utf-8 -*-
"""B3 判据校验器：1229 行用途分类 + 抽样 40 复核，判据 U1–U7。

用法：python scripts/check_skill_usage_labels.py          → 退出码 0/1
      python scripts/check_skill_usage_labels.py --json   → 输出回执 JSON
U1 行数 1229 且与索引 count / name 集合逐一对应（不许多、不许少、不许重名混淆）
U2 label 只取 K/M/T/X/U 五值，无空值（"全有值"= 每行 label 非空且合法）
U3 五类计数相加 == 1229，且 U（待判）≤ 20
U4 stage1 判定的行 score ≥ TH；stage2 行必须有 domain/weak 依据（reason 非空）
U5 抽样 40：条数 40、agree ≥ 36（90%），且失败项必须写明改判理由
U6 复跑字节一致（--check 由 classify_skill_usage.py 提供，这里做二次比对）
U7 CSV 自身 sha256 与 generation 回执一致（防手工改表后没重跑）
"""
import csv
import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "data", "skill_matrix_index.json")
CSV_F = os.path.join(ROOT, "data", "skill_usage_labels.csv")
VERDICT_F = os.path.join(ROOT, "data", "b3_sample_verdicts.json")
OUT = os.path.join(ROOT, "reports", "b3_usage_labels_check.json")
LABELS = ("K", "M", "T", "X", "U")


def main():
    checks = []

    def add(cid, ok, detail):
        checks.append({"id": cid, "ok": bool(ok), "detail": detail})

    missing = [os.path.basename(p) for p in (INDEX, CSV_F, VERDICT_F) if not os.path.isfile(p)]
    if missing:
        add("U0", False, "missing={}".format(missing))
        print(json.dumps({"verdict": "FAIL", "checks": checks}, ensure_ascii=False, indent=2))
        return 1

    with open(INDEX, encoding="utf-8") as f:
        idx = json.load(f)
    with open(CSV_F, encoding="utf-8") as f:
        text = f.read()
    rows = list(csv.DictReader(io.StringIO(text)))
    with open(VERDICT_F, encoding="utf-8") as f:
        sample = json.load(f)

    names_idx = [x.get("name") for x in idx["skills"]]
    names_csv = [r["name"] for r in rows]
    add("U1", len(rows) == 1229 and len(names_csv) == idx["count"] and names_csv == names_idx,
        "rows={} index_count={} order_identical={}".format(len(rows), idx["count"],
                                                          names_csv == names_idx))

    bad = [r["name"] for r in rows if r.get("label", "") not in LABELS]
    add("U2", not bad, "invalid_or_empty={}".format(bad[:5] + (["..."] if len(bad) > 5 else [])))

    counts = {k: 0 for k in LABELS}
    for r in rows:
        counts[r["label"]] += 1
    total = sum(counts.values())
    add("U3", total == 1229 and counts["U"] <= 20,
        "sum={} counts={} undecided={}".format(total, counts, counts["U"]))

    weak = [r["name"] for r in rows
            if r["stage"] == "stage1" and float(r["score"]) < 0.80
            or r["stage"] not in ("stage1", "stage2", "stage2-weak", "undecided")
            or not r["reason"]]
    add("U4", not weak, "bad_stage_or_reason={}".format(weak[:5]))

    agree = sample.get("agree", 0)
    dis = [x["name"] for x in sample.get("items", []) if x["verdict"] == "disagree"]
    all_noted = all(x.get("note") for x in sample.get("items", []) if x["verdict"] == "disagree")
    add("U5", len(sample.get("items", [])) == 40 and agree >= 36 and all_noted and len(dis) == sample.get("disagree"),
        "sample={} agree={}/40 disagree={} notes_complete={}".format(
            len(sample.get("items", [])), agree, len(dis), all_noted))

    # U6 复跑字节一致由 classify_skill_usage.py --check 负责，这里核一次同源构建
    sys.path.insert(0, ROOT)
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "csu", os.path.join(ROOT, "scripts", "classify_skill_usage.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    rebuilt, rcounts, rdigest = mod.build()
    same = mod.csv_text(rebuilt) == text
    add("U6", same and rcounts == counts, "byte_consistent={} digest={}".format(same, rdigest))

    actual = hashlib.sha256(text.encode("utf-8")).hexdigest()
    add("U7", sample.get("csv_sha256") == actual,
        "csv_sha256={}".format(actual))

    verdict = "PASS" if all(c["ok"] for c in checks) else "FAIL"
    doc = {"batch": "B3", "index_digest": idx.get("digest"), "labels_digest": rdigest,
           "csv_sha256": actual, "counts": counts, "sample": {"agree": agree,
           "disagree": len(dis), "threshold": 36}, "verdict": verdict,
           "failed": [c["id"] for c in checks if not c["ok"]], "checks": checks}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    print(json.dumps(doc, ensure_ascii=False, indent=2))
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
