# -*- coding: utf-8 -*-
"""V4.2-B1 校验器：三场卡电场补齐（V1-V9）。

  python scripts/verify_three_field.py            # 人类可读
  python scripts/verify_three_field.py --json     # 机器可读

判据：
V1  场数 = 3，场名严格为 magnetic / electric / liquid，中文名为 磁场 / 电场 / 液态场
V2  卡片数 = 13，场分布 5 / 3 / 5，与客仓只读数据件行数一致
V3  电场 3 张全部为 gap_structured：参数维度非空、检索计划有库/关键词/决策、决策恒 none
V4  全卡 evidence_class = simulated，且 tier 合法（L1-L5 / none）
V5  零剂量：卡片正文与本件全文均无「数字+剂量单位」命中
V6  零疗效承诺：不出现治愈/总有效/显效率/推荐使用/替代药物/可停药
V7  无第十条外推：每张卡都有 guard，gap 卡都有 retrieval_plan，且不得跨场顶替
V8  只读互认：探针前后客仓 sanchang_field_evidence.csv 字节摘要不变
V9  维度锁不变：Kernel 现算 25/47/9
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from holoaeon.fusion_upgrade.three_field import (  # noqa: E402
    DOSE_PATTERN, EFFICACY_WORDS, ThreeField)
from holoaeon.fusion_upgrade.snapshot import _locks  # noqa: E402

DATA = os.path.join(ROOT, "data")
REPORTS = os.path.join(ROOT, "reports")
CARDS = os.path.join(DATA, "three_field_cards.json")
GUEST = r"F:\doubaowork\开源发布_中西医融合康复工程_20261026\integrative-rehab-vsa\data\sanchang_field_evidence.csv"
OUT = os.path.join(REPORTS, "v42_three_field_check.json")

EXPECT_SPLIT = {"magnetic": 5, "electric": 3, "liquid": 5}
VALID_TIERS = ("L1", "L2", "L3", "L4", "L5", "none")


def _sha16(path: str) -> str:
    if not os.path.isfile(path):
        return ""
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def main(argv) -> int:
    as_json = "--json" in argv
    checks, failed = [], []

    def add(cid, ok, detail):
        checks.append({"id": cid, "ok": bool(ok), "detail": detail})
        if not ok:
            failed.append(cid)

    tf = ThreeField.load(CARDS)
    doc = tf.doc
    before = _sha16(GUEST)

    # V1
    names = [f["id"] for f in doc["fields"]]
    cn = [f["name_cn"] for f in doc["fields"]]
    add("V1", names == ["magnetic", "electric", "liquid"]
        and cn == ["磁场", "电场", "液态场"], {"fields": names, "name_cn": cn})

    # V2
    split = {f: len(tf.cards_of(f)) for f in names}
    add("V2", len(tf.cards) == 13 and split == EXPECT_SPLIT,
        {"cards": len(tf.cards), "split": split, "expected": EXPECT_SPLIT})

    # V3
    electric = tf.cards_of("electric")
    bad_e = []
    for c in electric:
        plan = c.get("retrieval_plan") or {}
        if (c.get("status") != "gap_structured"
                or not c.get("parameter_frame")
                or not plan.get("databases") or len(plan.get("keywords") or []) < 3
                or plan.get("decision") != "none"):
            bad_e.append(c["card_id"])
    add("V3", bad_e == [], {"electric_cards": [c["card_id"] for c in electric],
                            "bad": bad_e})

    # V4
    bad_tier = [c["card_id"] for c in tf.cards
                if c.get("evidence_tier") not in VALID_TIERS
                or c.get("evidence_class") != "simulated"]
    add("V4", bad_tier == [], {"bad": bad_tier, "tier_split": tf.tier_split(),
                               "doc_evidence_class": doc.get("evidence_class")})

    # V5
    body = json.dumps(doc, ensure_ascii=False)
    hits = DOSE_PATTERN.findall(body)
    add("V5", hits == [], {"dose_hits": hits[:5]})

    # V6
    eff = [w for w in EFFICACY_WORDS if w in body]
    add("V6", eff == [], {"efficacy_hits": eff})

    # V7
    no_guard = [c["card_id"] for c in tf.cards if not c.get("guard")]
    gap_no_plan = [c["card_id"] for c in tf.gaps() if not c.get("retrieval_plan")]
    substitute = []
    for c in tf.cards:
        guard = str(c.get("guard", ""))
        if "禁止" not in guard and "不得" not in guard:
            substitute.append(c["card_id"])
    add("V7", no_guard == [] and gap_no_plan == [] and substitute == [],
        {"no_guard": no_guard, "gap_no_plan": gap_no_plan, "weak_guard": substitute})

    # V8
    after = _sha16(GUEST)
    guest_rows = 0
    if os.path.isfile(GUEST):
        with open(GUEST, "r", encoding="utf-8-sig") as f:
            guest_rows = max(0, len(f.read().splitlines()) - 1)
    add("V8", before == after and bool(before) and guest_rows == 13,
        {"sha16": after, "changed": before != after, "guest_rows": guest_rows})

    # V9
    add("V9", _locks() == {"agents": 25, "skills": 47, "packs": 9}, _locks())

    cov = tf.coverage()
    report = {
        "gate_id": "SG-V42-THREE-FIELD-CHECK-V1",
        "batch": "V4.2-B1",
        "registry_id": doc.get("registry_id"),
        "verdict": "PASS" if not failed else "FAIL",
        "failed": failed,
        "passed": len(checks) - len(failed),
        "total": len(checks),
        "checks": checks,
        "cards": len(tf.cards),
        "field_split": split,
        "tier_split": tf.tier_split(),
        "gap_cards": cov["gap_cards"],
        "gap_structured": cov["gap_structured"],
        "guest_sanchang": {"sha16": after, "rows": guest_rows},
        "evidence_class": "simulated",
    }
    os.makedirs(REPORTS, exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n")

    if as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        for c in checks:
            print("%s %-3s %s" % ("[OK]" if c["ok"] else "[NG]", c["id"],
                                  json.dumps(c["detail"], ensure_ascii=False)[:160]))
        print("结果：%d/%d %s ｜ 13 卡 = 磁 %d / 电 %d / 液 %d"
              % (report["passed"], report["total"], "全绿" if not failed else "有失败",
                 split.get("magnetic", 0), split.get("electric", 0), split.get("liquid", 0)))
        print("回执：", OUT)
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
