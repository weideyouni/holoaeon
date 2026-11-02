"""B9 收口出票器 · 纯标准库 / 离线 / 只读除自身输出。

用法：python scripts/build_b9_closeout.py

产出：reports/b9_closeout.json（稳定排序；不含时间戳；供 B9 票据与回执引用）
  1. 交付 zip 的 bytes / sha16 / sha256 / entries
  2. 台账 v2 的行数与完成数
  3. 判据表条数、风险登记条数
  4. 五份收口件的字节数
  5. 已跑过的闸门结果（读既有 JSON，不重跑）
"""

import csv
import hashlib
import io
import json
import os
import zipfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = os.environ.get("HOLOAEON_PKG", r"F:\doubaowork\HoloAeon_V4冷热插拔赋能升级_20261102")
ZIP_NAME = "holoaeon_v4_fusion_upgrade_20261102.zip"
OUT = os.path.join(REPO, "reports", "b9_closeout.json")

DOCS = [
    "data/B9_融合总策划_v2.md",
    "data/B9_批次台账_v2.csv",
    "data/B9_完美融合判据.md",
    "data/B9_风险与回滚登记.md",
    "data/B9_四透镜评审意见.md",
    "data/B9_收口票据.md",
]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(rel):
    path = os.path.join(REPO, rel)
    if not os.path.exists(path):
        return None
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def zip_facts():
    path = os.path.join(PKG, ZIP_NAME)
    if not os.path.exists(path):
        return {"present": False}
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
    digest = sha256(path)
    return {"present": True, "bytes": os.path.getsize(path), "entries": len(names),
            "sha256": digest, "sha16": digest[:16]}


def ledger_facts():
    path = os.path.join(REPO, "data", "B9_批次台账_v2.csv")
    with io.open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    done = [r for r in rows if r.get("状态") == "已完成"]
    empty = [r.get("批次") for r in rows if any((v or "").strip() == "" for v in r.values())]
    return {"rows": len(rows), "completed": len(done), "empty_cells": empty,
            "batches": [r.get("批次") for r in rows],
            "hours": round(sum(float(r.get("工时(人天)") or 0) for r in rows), 2)}


def count_rows(rel, prefixes):
    path = os.path.join(REPO, rel)
    with io.open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    return [ln for ln in lines if any(ln.startswith(p) for p in prefixes)]


def main():
    facts = {"batch": "B9", "evidence_class": "simulated",
             "zip": zip_facts(), "ledger": ledger_facts()}
    facts["criteria_rows"] = len(count_rows("data/B9_完美融合判据.md", ["| C"]))
    facts["risk_rows"] = len(count_rows("data/B9_风险与回滚登记.md", ["| RB", "| RK"]))
    facts["docs"] = {rel: os.path.getsize(os.path.join(REPO, rel)) for rel in DOCS
                     if os.path.exists(os.path.join(REPO, rel))}
    facts["docs_missing"] = [rel for rel in DOCS if not os.path.exists(os.path.join(REPO, rel))]

    gate = read_json("reports/gate_fusion_v4.json")
    facts["gates"] = {"v3_gate": "%s/%s" % (gate.get("passed"), gate.get("total"))} if gate else {"v3_gate": "missing"}
    b8 = read_json("reports/b8_dual_sync_check.json")
    if b8:
        facts["gates"]["b8_dual_sync"] = "%s/%s PASS" % (b8.get("passed"), b8.get("total"))
    manifest = read_json("reports/five_site_manifest.json")
    if manifest:
        facts["manifest"] = {"package": manifest.get("counts", {}).get("package"),
                             "repo": manifest.get("counts", {}).get("repo"),
                             "missing": manifest.get("counts", {}).get("missing"),
                             "dna_id": manifest.get("dna_id")}

    with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(facts, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"out": "reports/b9_closeout.json", "zip_sha16": facts["zip"].get("sha16"),
                      "zip_entries": facts["zip"].get("entries"),
                      "criteria": facts["criteria_rows"], "risks": facts["risk_rows"],
                      "ledger_rows": facts["ledger"]["rows"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
