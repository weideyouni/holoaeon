# -*- coding: utf-8 -*-
"""V4.1-B2 校验器：语义技能族 60 → 100（V1-V6）。

  python scripts/verify_semantic_100.py            # 人类可读
  python scripts/verify_semantic_100.py --json     # 机器可读

判据：
V1  成员数 = 100，且文件 target = 100
V2  模块数 = 10，模块名严格等于 V1 规格件十模块（无第十一模块）
V3  扩容成员标签只允许 M / K
V4  基座与索引 mechanism=semantic_bus 严格对应（19 条、去重 16）
V5  可复现：按 V2 规格件重算 canonical sha 等于文件内 sha；重跑构建成员集合一致
V6  覆盖与桥接：十模块全覆盖、成员无重复、桥接 ≤4 且不与成员重叠、目标机制合法
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)

import expand_semantic as ES  # noqa: E402
from holoaeon.fusion_upgrade.semantic_family import Family  # noqa: E402

DATA = os.path.join(ROOT, "data")
REPORTS = os.path.join(ROOT, "reports")
FAMILY = os.path.join(DATA, "semantic_family.json")
SPEC_V1 = os.path.join(DATA, "semantic_modules.json")
SPEC_V4 = os.path.join(DATA, "semantic_modules_v4.json")
INDEX = os.path.join(DATA, "skill_matrix_index.json")
OUT = os.path.join(REPORTS, "v41_semantic_100_check.json")

TARGET = 100


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main(argv) -> int:
    as_json = "--json" in argv
    doc = load(FAMILY)
    spec_v1 = load(SPEC_V1)
    spec_v4 = load(SPEC_V4)
    idx = load(INDEX)["skills"]
    members = doc["members"]
    module_names = [m["name"] for m in spec_v1["modules"]]
    fam = Family.load()
    checks, failed = [], []

    def add(cid, ok, detail):
        checks.append({"id": cid, "ok": bool(ok), "detail": detail})
        if not ok:
            failed.append(cid)

    # V1
    add("V1", len(members) == TARGET and doc.get("target") == TARGET,
        {"members": len(members), "target": doc.get("target")})

    # V2
    names_doc = [m["name"] for m in doc["modules"]]
    add("V2", len(module_names) == 10 and names_doc == module_names
        and doc.get("module_count") == 10
        and [m["name"] for m in spec_v4["modules"]] == module_names
        and all(m["module"] in module_names for m in members),
        {"doc_modules": len(names_doc), "spec_v4_match": [m["name"] for m in spec_v4["modules"]] == module_names})

    # V3
    bad = [m["skill"] for m in members if m["status"] == "expanded" and m["label"] not in ("M", "K")]
    add("V3", bad == [], {"expanded_bad_label": bad[:5]})

    # V4
    index_base = {s["name"] for s in idx if s.get("mechanism") == "semantic_bus"}
    fam_base = {m["skill"] for m in members if m["status"] == "base_index"}
    add("V4", index_base == fam_base and len(index_base) == 16
        and doc.get("base_entry_count") == 19 and doc.get("base_count") == 16,
        {"index_base": len(index_base), "family_base": len(fam_base),
         "base_entry_count": doc.get("base_entry_count")})

    # V5
    body = json.dumps({"members": members, "sha256": ""}, ensure_ascii=False, sort_keys=True)
    sha_now = hashlib.sha256(body.encode("utf-8")).hexdigest()
    rebuilt = ES.build(TARGET, SPEC_V4)
    same_names = [m["skill"] for m in rebuilt["members"]] == [m["skill"] for m in members]
    same_modules = {m["skill"]: m["module"] for m in rebuilt["members"]} == \
        {m["skill"]: m["module"] for m in members}
    add("V5", sha_now == doc.get("sha256") and same_names and same_modules,
        {"sha_now": sha_now[:12], "sha_doc": str(doc.get("sha256"))[:12],
         "rebuild_same": bool(same_names and same_modules)})

    # V6
    bridge = doc.get("bridge_candidates") or []
    overlap = [b["skill"] for b in bridge if b["skill"] in {m["skill"] for m in members}]
    bad_target = [b["skill"] for b in bridge if b.get("target_mechanism") not in ("semantic_bus", "meridian")]
    dups = len(members) - len({m["skill"] for m in members})
    cov = fam.coverage()
    add("V6", len(bridge) <= 4 and overlap == [] and bad_target == []
        and dups == 0 and all(c > 0 for c in cov.values()) and fam.verify()["ok"],
        {"bridge": len(bridge), "overlap": overlap[:3], "dups": dups,
         "min_module": min(cov.values()), "family_ok": fam.verify()["ok"]})

    module_counts = {n: sum(1 for m in members if m["module"] == n) for n in module_names}
    label_split = doc.get("label_split")
    report = {
        "gate_id": "SG-V41-SEMANTIC-100-CHECK-V1",
        "batch": "V4.1-B2",
        "verdict": "PASS" if not failed else "FAIL",
        "failed": failed,
        "passed": len(checks) - len(failed),
        "total": len(checks),
        "checks": checks,
        "member_count": len(members),
        "expanded_count": len(members) - len([m for m in members if m["status"] == "base_index"]),
        "module_count": len(module_names),
        "module_counts": module_counts,
        "label_split": label_split,
        "bridge_candidates": len(bridge),
        "sha256": doc.get("sha256"),
        "spec_id": spec_v4.get("spec_id"),
        "supersedes": spec_v4.get("supersedes"),
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
                                  json.dumps(c["detail"], ensure_ascii=False)[:150]))
        print("结果：%d/%d %s ｜ 成员 %d / 十模块 / 扩容 %d"
              % (report["passed"], report["total"], "全绿" if not failed else "有失败",
                 report["member_count"], report["expanded_count"]))
        print("回执：", OUT)
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
