# -*- coding: utf-8 -*-
"""B2b 校验器：通道映射 + 词表分域，判据 G1–G8。

用法：python scripts/check_channel_map.py   → 退出码 0/1
G1 channel_map.csv 12 行，LC01–LC12 顺序，分组 气5/血4/神3/淋巴0
G2 目标 17 · 已映射 12 · pending 5（神 1 / 淋巴 4），且 no_arithmetic=true
G3 全仓（csv/json/生成脚本）不出现 "idx % 17" / "%17" 之类的算术推通道写法
G4 与 contract.channel_map() 逐行一致（同源，不各写一套）
G5 通用闸恰 10 槽，且不含任何 E13/E14 槽位；includes_medical=false
G6 医学侧 E14=24 / E13=12，copied_into_holoaeon=false
G7 注入条件按 domain 分域：general 必 not_load medical；medical 额外要求 redlines
G8 词表 spec_digest 可复算
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from holoaeon.fusion_upgrade import contract as c

CSV_F = os.path.join(ROOT, "data", "channel_map.csv")
JSON_F = os.path.join(ROOT, "data", "channel_map.json")
LEX_F = os.path.join(ROOT, "data", "skin_lexicon_rehab.json")
GEN_SCRIPTS = [os.path.join(ROOT, "scripts", "gen_channel_map.py"),
               os.path.join(ROOT, "scripts", "gen_skin_lexicon.py")]


def read_csv(path):
    with open(path, encoding="utf-8") as f:
        lines = [x.rstrip("\n") for x in f if x.strip()]
    header = lines[0].split(",")
    rows = [dict(zip(header, x.split(","))) for x in lines[1:]]
    return header, rows


def main():
    checks = []

    def add(cid, ok, detail):
        checks.append({"id": cid, "ok": bool(ok), "detail": detail})

    missing = [p for p in (CSV_F, JSON_F, LEX_F) if not os.path.isfile(p)]
    if missing:
        add("G0", False, "missing={}".format([os.path.basename(p) for p in missing]))
        print(json.dumps({"verdict": "FAIL", "checks": checks}, ensure_ascii=False, indent=2))
        return 1

    header, rows = read_csv(CSV_F)
    with open(JSON_F, encoding="utf-8") as f:
        meta = json.load(f)
    with open(LEX_F, encoding="utf-8") as f:
        lex = json.load(f)

    groups = {}
    for r in rows:
        groups[r["group"]] = groups.get(r["group"], 0) + 1
    add("G1", len(rows) == 12 and [r["lc"] for r in rows] == ["LC%02d" % i for i in range(1, 13)]
        and groups == {"气": 5, "血": 4, "神": 3}, "rows={} groups={}".format(len(rows), groups))

    add("G2", meta.get("mapped") == 12 and meta.get("targets") == 17 and meta.get("pending") == 5
        and meta.get("pending_detail") == {"神": 1, "淋巴": 4} and meta.get("no_arithmetic") is True,
        "mapped={} targets={} pending={} detail={} no_arithmetic={}".format(
            meta.get("mapped"), meta.get("targets"), meta.get("pending"),
            meta.get("pending_detail"), meta.get("no_arithmetic")))

    hits = []
    for p in [CSV_F, JSON_F] + GEN_SCRIPTS:
        with open(p, encoding="utf-8") as f:
            text = f.read()
        for token in ("idx % 17", "idx%17", "% 17", "%17"):
            if token in text:
                hits.append("{}:{}".format(os.path.basename(p), token))
    add("G3", not hits, "arithmetic_tokens={}".format(hits))

    drift = []
    ref = c.channel_map()["rows"]
    for i, r in enumerate(ref):
        row = rows[i] if i < len(rows) else {}
        if row.get("lc") != r["lc"] or row.get("group") != r["group"] \
                or row.get("target_group") != r["target_group"] or row.get("status") != r["status"]:
            drift.append(r["lc"])
    add("G4", not drift and len(ref) == len(rows), "drift={}".format(drift))

    gen = lex.get("tracks", {}).get("general", {})
    slots = gen.get("slots", [])
    med_tokens = [s for s in slots if "E13" in s or "E14" in s]
    add("G5", len(slots) == 10 and not med_tokens and gen.get("includes_medical") is False
        and gen.get("e13_e14_present") is False,
        "general_slots={} medical_slots_in_general={}".format(len(slots), med_tokens))

    med = lex.get("tracks", {}).get("medical", {})
    add("G6", med.get("e14_count") == 24 and med.get("e13_count") == 12
        and len(med.get("e14_slots", [])) == 24 and len(med.get("e13_slots", [])) == 12
        and med.get("copied_into_holoaeon") is False,
        "e14={}/{} e13={}/{} copied={}".format(len(med.get("e14_slots", [])), med.get("e14_count"),
                                               len(med.get("e13_slots", [])), med.get("e13_count"),
                                               med.get("copied_into_holoaeon")))

    inj = lex.get("injection", {})
    g = inj.get("general_gate", {})
    m = inj.get("medical_gate", {})
    add("G7", "medical" in g.get("must_not_load", []) and "general" in g.get("load", [])
        and "medical" in m.get("load", []) and "redlines" in str(m.get("extra_requirement", "")),
        "general_must_not_load={} medical_extra={}".format(g.get("must_not_load"),
                                                           m.get("extra_requirement")))

    core = {k: v for k, v in lex.items() if k != "spec_digest"}
    canon = json.dumps(core, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    want = hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16]
    add("G8", lex.get("spec_digest") == want,
        "declared={} recomputed={}".format(lex.get("spec_digest"), want))

    verdict = "PASS" if all(x["ok"] for x in checks) else "FAIL"
    print(json.dumps({"batch": "B2b", "channel_digest": meta.get("csv_sha256"),
                      "lexicon_digest": lex.get("spec_digest"), "verdict": verdict,
                      "failed": [x["id"] for x in checks if not x["ok"]],
                      "checks": checks}, ensure_ascii=False, indent=2))
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
