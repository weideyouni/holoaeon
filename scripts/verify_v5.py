# -*- coding: utf-8 -*-
"""V5.0 判据 D1–D10：康复域知识库入库 + 影子维度 + 证据登记（只读校验）。"""
import hashlib
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB = os.path.join(ROOT, "data", "v5_rehab_kb.json")
SLOTS = os.path.join(ROOT, "data", "extension_slots.json")
LOCK = os.path.join(ROOT, "reports", "dimension_lock.json")
IVSA = r"F:\doubaowork\开源发布_中西医融合康复工程_20261026\integrative-rehab-vsa"
DOSE_RE = re.compile(r"(\d+(\.\d+)?\s?(mg|g|ml|μg|ug)\b)|\b(mg/kg|mg·kg)\b|每日\s?\d+\s?次|每次\s?\d+")
URL_RE = re.compile(r"https?://", re.I)


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(65536), b""):
            h.update(c)
    return h.hexdigest()


def load(p):
    with io.open(p, encoding="utf-8") as f:
        return json.load(f)


checks = []


def add(cid, ok, detail):
    checks.append({"id": cid, "ok": bool(ok), "detail": detail})


kb = None
try:
    kb = load(KB)
except Exception as exc:
    add("D1", False, "kb unreadable: %s" % type(exc).__name__)

if kb:
    add("D1", kb.get("id") == "SG-V5-REHAB-KB-V1" and bool(kb.get("entries")),
        "id=%s entries=%d" % (kb.get("id"), len(kb.get("entries") or [])))

    # D2 索引与真实文件同源（哈希复算）
    bad = []
    for e in kb["entries"]:
        if not e.get("sha256"):
            continue
        src = e["source"]
        p = os.path.join(IVSA, src.split("ivsa/", 1)[1].replace("/", os.sep)) if src.startswith("ivsa/") \
            else os.path.join(ROOT, src.replace("/", os.sep))
        if not os.path.isfile(p):
            bad.append(src + ":missing")
            continue
        if e["bytes"] != os.path.getsize(p) or e["sha256"] != sha256(p):
            bad.append(src + ":drift")
    add("D2", bad == [], "recomputed=%d bad=%s" % (sum(1 for e in kb["entries"] if e.get("sha256")), bad))

    lock = kb.get("lock") or {}
    add("D3", (lock.get("agents"), lock.get("skills"), lock.get("packs")) == (25, 47, 9),
        "kb lock=%s/%s/%s" % (lock.get("agents"), lock.get("skills"), lock.get("packs")))

    real = load(LOCK)
    dims = real.get("dimensions") or []
    by_name = {d.get("name"): d.get("value") for d in dims if isinstance(d, dict)}
    add("D3b", (by_name.get("holoaeon_agents"), by_name.get("holoaeon_skills"),
                by_name.get("holoaeon_domain_packs")) == (25, 47, 9),
        "dimensions=%d agents/skills/packs=%s/%s/%s" % (
            len(dims), by_name.get("holoaeon_agents"), by_name.get("holoaeon_skills"),
            by_name.get("holoaeon_domain_packs")))

    sd = kb.get("shadow_dimension") or {}
    add("D4", sd.get("participates_in_dimension_lock") is False and sd.get("affects_diff0_hash") is False
        and sd.get("slot") == "EXT-DIM-02",
        "shadow=%s lock=%s diff0=%s" % (sd.get("id"), sd.get("participates_in_dimension_lock"), sd.get("affects_diff0_hash")))

    er = kb.get("evidence_register") or {}
    cards = er.get("cards") or []
    untouched = [c["card_id"] for c in cards if c.get("tier_after") == "none" and c.get("tier_before") == "none"]
    add("D5", len(cards) == 4 and len(untouched) == 4 and er.get("tier_unchanged") is True,
        "cards=%d tier_none=%d" % (len(cards), len(untouched)))

    # D6 红线：索引内不得出现剂量/诊断式表述
    blob = json.dumps(kb, ensure_ascii=False)
    hits = DOSE_RE.findall(blob)
    add("D6", not hits, "dose_hits=%d" % len(hits))

    # D7 不复制客仓正文：ivsa 条目 copied=False 且无 header 内容以外的长文本
    copied = [e["entry_id"] for e in kb["entries"] if e["layer"].startswith("ivsa_") and e.get("copied")]
    long_text = [e["entry_id"] for e in kb["entries"] if len(str(e.get("note", ""))) > 200]
    add("D7", copied == [] and long_text == [], "copied=%s long=%s" % (copied, long_text))

    # D8 无公网地址 / 无凭证
    add("D8", not URL_RE.search(blob) and "sk-" not in blob.lower(), "url=%s" % bool(URL_RE.search(blob)))

    # D9 卡槽状态与 kb 一致（DIM-02 已认领、EVIDENCE-01 已解封）
    slots = load(SLOTS)
    by = {s["slot_id"]: s for s in slots["slots"]}
    d2 = by.get("EXT-DIM-02", {})
    e1 = by.get("EXT-EVIDENCE-01", {})
    add("D9", d2.get("status") == "occupied" and e1.get("status") == "occupied"
        and e1.get("evidence") == "none",
        "DIM-02=%s EVIDENCE-01=%s ev=%s" % (d2.get("status"), e1.get("status"), e1.get("evidence")))

    # D10 四件新文件已登记进 REPO_FILES
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import five_site_dna as dna
    need = ["data/v5_rehab_kb.json", "scripts/build_v5_rehab_kb.py", "scripts/verify_v5.py",
            "tests_contract/test_v5.py"]
    listed = list(getattr(dna, "REPO_FILES"))
    missing = [n for n in need if n not in listed]
    add("D10", missing == [], "repo_files=%d missing=%s" % (len(listed), missing))

passed = sum(1 for c in checks if c["ok"])
out = {"id": "SG-V5-REHAB-KB-CHECK-V1", "passed": passed, "total": len(checks),
       "failed": [c["id"] for c in checks if not c["ok"]],
       "verdict": "PASS" if passed == len(checks) else "FAIL",
       "totals": (kb or {}).get("totals", {}), "checks": checks}
print(json.dumps(out, ensure_ascii=False, indent=2))
if "--json" in sys.argv:
    dest = sys.argv[sys.argv.index("--json") + 1]
    dest = dest if os.path.isabs(dest) else os.path.join(ROOT, dest)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with io.open(dest, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write("\n")
sys.exit(0 if passed == len(checks) else 1)
