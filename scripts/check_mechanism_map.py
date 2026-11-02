# -*- coding: utf-8 -*-
"""B2a 映射表校验器：data/mechanism_map.json 六条判据 M1–M6。

用法：python scripts/check_mechanism_map.py   → 退出码 0/1
M1 六行且机制名与 contract.MECHANISMS 同序
M2 每行 mapping_rule 非空且 >= 6 字
M3 direction 全局单向（含 "one-way" 且不含 "two-way"/"双向"）
M4 map_digest 可复算
M5 每行 same / diff 至少各一条
M6 行内容与 contract.PAIRS 逐字段一致（防止文档与代码各写一套）
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from holoaeon.fusion_upgrade import contract as c

MAP_FILE = os.path.join(ROOT, "data", "mechanism_map.json")


def recompute_digest(rows):
    import hashlib
    canon = json.dumps(rows, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16]


def main():
    checks = []

    def add(cid, ok, detail):
        checks.append({"id": cid, "ok": bool(ok), "detail": detail})

    if not os.path.isfile(MAP_FILE):
        add("M0", False, "missing " + MAP_FILE)
        print(json.dumps({"verdict": "FAIL", "checks": checks}, ensure_ascii=False, indent=2))
        return 1

    with open(MAP_FILE, encoding="utf-8") as f:
        doc = json.load(f)
    rows = doc.get("rows", [])

    mechs = [r.get("mechanism") for r in rows]
    add("M1", len(rows) == 6 and mechs == list(c.MECHANISMS),
        "rows={} mechanisms={}".format(len(rows), mechs))

    rules_ok = [r.get("id") for r in rows
                if not isinstance(r.get("mapping_rule"), str) or len(r["mapping_rule"].strip()) < 6]
    add("M2", not rules_ok, "short_or_missing={}".format(rules_ok))

    d = str(doc.get("direction", ""))
    dirs = [r.get("direction") for r in rows]
    bad_dir = [bool(x) for x in dirs if not isinstance(x, str) or "one-way" not in x
               or "two-way" in x or "双向" in x]
    add("M3", "one-way" in d and "two-way" not in d and "双向" not in d
        and not any(bad_dir) and len(set(dirs)) == 1,
        "direction={!r} distinct_rows={}".format(d, len(set(dirs))))

    want = recompute_digest(rows)
    add("M4", doc.get("map_digest") == want,
        "declared={} recomputed={}".format(doc.get("map_digest"), want))

    thin = [r.get("id") for r in rows if not r.get("same") or not r.get("diff")]
    add("M5", not thin, "thin_rows={}".format(thin))

    drift = []
    for i, p in enumerate(c.PAIRS):
        r = rows[i] if i < len(rows) else {}
        if (r.get("mechanism") != p["mechanism"] or r.get("cn") != p["cn"]
                or r.get("holo_side") != p["holo"] or r.get("ivsa_side") != p["ivsa"]
                or r.get("same") != list(p["same"]) or r.get("diff") != list(p["diff"])
                or r.get("mapping_rule") != p["bridge"]):
            drift.append(p["mechanism"])
    add("M6", not drift, "drift={}".format(drift))

    verdict = "PASS" if all(x["ok"] for x in checks) else "FAIL"
    print(json.dumps({"batch": "B2a", "map_id": doc.get("map_id"),
                      "map_digest": doc.get("map_digest"), "verdict": verdict,
                      "failed": [x["id"] for x in checks if not x["ok"]],
                      "checks": checks}, ensure_ascii=False, indent=2))
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
