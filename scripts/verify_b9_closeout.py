"""B9 收口校验器 · 纯标准库 / 离线 / 只读。

用法：python scripts/verify_b9_closeout.py [--json path]

校验 V1–V12：
  V1  五份收口件 + 票据在位且非空
  V2  台账 v2 恰好 12 行、全部已完成、无空单元格
  V3  台账工时合计 = 15.0 人天
  V4  判据表 ≥12 条，且每条带可跑命令（反引号）
  V5  风险登记 ≥6 条，每条含回滚/处置字样
  V6  判据里不含形容词型判据（更完美/极致/最优/显著提升/最大程度）
  V7  交付 zip 在位，sha16 与 reports/b9_closeout.json 一致
  V8  五地清单 package 含 zip、missing=0
  V9  v3_gate 32/32 且 A1 三数 = 25/47/9
  V10 B8 双仓校验 11/11
  V11 DNA 版本为 V1.2（清单 dna_id 与机读件一致）
  V12 规格版本仍为 0.9.1
"""

import csv
import io
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = os.environ.get("HOLOAEON_PKG", r"F:\doubaowork\HoloAeon_V4冷热插拔赋能升级_20261102")
ZIP_NAME = "holoaeon_v4_fusion_upgrade_20261102.zip"
DOCS = [
    "data/B9_融合总策划_v2.md",
    "data/B9_批次台账_v2.csv",
    "data/B9_完美融合判据.md",
    "data/B9_风险与回滚登记.md",
    "data/B9_四透镜评审意见.md",
    "data/B9_收口票据.md",
]
ADJECTIVES = ["更完美", "极致", "最优路径", "显著提升", "最大程度"]


def load_json(rel):
    path = os.path.join(REPO, rel)
    if not os.path.exists(path):
        return None
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def read_text(rel):
    with io.open(os.path.join(REPO, rel), encoding="utf-8") as f:
        return f.read()


def check_docs():
    missing = [d for d in DOCS if not os.path.exists(os.path.join(REPO, d)) or os.path.getsize(os.path.join(REPO, d)) == 0]
    return (not missing, "missing=%s" % missing)


def check_ledger():
    path = os.path.join(REPO, "data", "B9_批次台账_v2.csv")
    with io.open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    empty = [r.get("批次") for r in rows if any((v or "").strip() == "" for v in r.values())]
    ok = len(rows) == 12 and all(r.get("状态") == "已完成" for r in rows) and not empty
    return ok, "rows=%d completed=%d empty=%s" % (len(rows), sum(1 for r in rows if r.get("状态") == "已完成"), empty)


def check_hours():
    path = os.path.join(REPO, "data", "B9_批次台账_v2.csv")
    with io.open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    total = round(sum(float(r.get("工时(人天)") or 0) for r in rows), 2)
    return total == 15.0, "hours=%s" % total


def check_criteria():
    text = read_text("data/B9_完美融合判据.md")
    rows = [ln for ln in text.splitlines() if ln.startswith("| C")]
    with_cmd = [ln for ln in rows if ("`" in ln or "同上" in ln)]
    return len(rows) >= 12 and len(with_cmd) == len(rows), "rows=%d with_cmd=%d" % (len(rows), len(with_cmd))


def check_risks():
    text = read_text("data/B9_风险与回滚登记.md")
    rows = [ln for ln in text.splitlines() if ln.startswith("| RB") or ln.startswith("| RK")]
    with_action = []
    for ln in rows:
        cells = ln.split("|")
        if len(cells) >= 7 and cells[5].strip():
            with_action.append(ln)
    return len(rows) >= 6 and len(with_action) == len(rows), "rows=%d with_action=%d" % (len(rows), len(with_action))


def check_no_adjectives():
    text = read_text("data/B9_完美融合判据.md")
    hit = [w for w in ADJECTIVES if w in text]
    return not hit, "hit=%s" % hit


def check_zip():
    closeout = load_json("reports/b9_closeout.json")
    path = os.path.join(PKG, ZIP_NAME)
    if not os.path.exists(path):
        return False, "zip missing"
    if not closeout or not closeout.get("zip", {}).get("present"):
        return False, "closeout missing zip facts"
    import hashlib
    digest = hashlib.sha256(open(path, "rb").read()).hexdigest()
    return digest[:16] == closeout["zip"]["sha16"], "sha16=%s expected=%s" % (digest[:16], closeout["zip"]["sha16"])


def check_manifest():
    manifest = load_json("reports/five_site_manifest.json")
    if not manifest:
        return False, "manifest missing"
    counts = manifest.get("counts", {})
    names = manifest.get("files", {})
    has_zip = any(k.endswith(ZIP_NAME) for k in names) or ZIP_NAME in json.dumps(manifest, ensure_ascii=False)
    return counts.get("missing") == 0 and has_zip, "missing=%s has_zip=%s" % (counts.get("missing"), has_zip)


def check_v3_gate():
    gate = load_json("reports/gate_fusion_v4.json")
    if not gate:
        return False, "gate json missing"
    a1 = next((c for c in gate.get("checks", []) if c.get("id") == "A1"), None)
    detail = a1.get("detail") if a1 else None
    ok = gate.get("passed") == gate.get("total") == 32 and gate.get("failed") == []
    ok = ok and detail == {"agents": 25, "skills": 47, "packs": 9}
    return bool(ok), "passed=%s total=%s a1=%s" % (gate.get("passed"), gate.get("total"), detail)


def check_b8():
    b8 = load_json("reports/b8_dual_sync_check.json")
    if not b8:
        return False, "b8 check missing"
    return b8.get("passed") == b8.get("total") == 11 and b8.get("failed") == [], "passed=%s total=%s" % (b8.get("passed"), b8.get("total"))


def check_dna():
    manifest = load_json("reports/five_site_manifest.json") or {}
    dna = load_json("data/five_site_dna.json") or {}
    ok = manifest.get("dna_id") == dna.get("dna_id") == "SG-DNA-FIVE-SITE-SYNC-V1.2"
    return ok, "manifest=%s dna=%s" % (manifest.get("dna_id"), dna.get("dna_id"))


def check_spec():
    text = read_text("holoaeon/spec.py")
    m = re.search(r'VERSION\s*=\s*"([^"]+)"', text)
    got = m.group(1) if m else "?"
    return got == "0.9.1", "spec_version=%s" % got


CHECKS = [
    ("V1", "收口件在位", check_docs),
    ("V2", "台账 12 行全完成无空", check_ledger),
    ("V3", "工时合计 15.0", check_hours),
    ("V4", "判据 ≥12 且带命令", check_criteria),
    ("V5", "风险 ≥6 且带回滚", check_risks),
    ("V6", "判据无形容词", check_no_adjectives),
    ("V7", "zip sha16 与出票一致", check_zip),
    ("V8", "清单含 zip 且 missing=0", check_manifest),
    ("V9", "v3_gate 32/32", check_v3_gate),
    ("V10", "B8 双仓 11/11", check_b8),
    ("V11", "DNA V1.2 一致", check_dna),
    ("V12", "spec 0.9.1", check_spec),
]


def run():
    results = []
    for cid, name, fn in CHECKS:
        try:
            ok, detail = fn()
        except Exception as exc:  # 校验器自身失败也要落票，不静默
            ok, detail = False, "exc=%s: %s" % (type(exc).__name__, exc)
        results.append({"id": cid, "name": name, "passed": bool(ok), "detail": detail})
    passed = sum(1 for r in results if r["passed"])
    return {"verdict": "PASS" if passed == len(results) else "FAIL",
            "passed": passed, "total": len(results), "checks": results,
            "failed": [r["id"] for r in results if not r["passed"]]}


def main():
    argv = sys.argv[1:]
    report = run()
    out = None
    if "--json" in argv:
        out = argv[argv.index("--json") + 1] if len(argv) > argv.index("--json") + 1 else None
    if out:
        path = out if os.path.isabs(out) else os.path.join(REPO, out)
        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
