#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""B5 · 语义技能族判据（S1-S9）

判据一律可跑、可复算，不用形容词：
S1  成员数 >= target（默认 60）
S2  模块数 == 10，且模块名严格等于 data/semantic_modules.json 的十模块
S3  十模块全覆盖（uncovered_modules == []）
S4  每条成员的 module 必须落在这 10 个之一（无第十一模块）
S5  成员不重复
S6  基座 19 条与索引 mechanism=semantic_bus 完全对应（少一条或多一条都 FAIL）
S7  扩容成员的 B3 标签只允许 M/K（禁止把 T 工具链、X 无关项混进执行族）
S8  可复现：现场重算 canonical sha256 必须等于文件内 sha256
S9  康复桥接候选 <= 4，且 target_mechanism 只能是 semantic_bus / meridian，不计入 60

用法：
  python scripts/check_semantic_family.py            # 写 reports/b5_semantic_check.json
  python scripts/check_semantic_family.py --json     # 只打印
退出码 0 = PASS。
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

FAMILY = os.path.join(ROOT, "data", "semantic_family.json")
MODULES = os.path.join(ROOT, "data", "semantic_modules.json")
INDEX = os.path.join(ROOT, "data", "skill_matrix_index.json")
OUT = os.path.join(ROOT, "reports", "b5_semantic_check.json")

TARGET = 60
BRIDGE_MAX = 4
BRIDGE_TARGETS = ("semantic_bus", "meridian")


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def recompute_sha(members):
    body = json.dumps({"members": members, "sha256": ""}, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def main(argv):
    doc = load(FAMILY)
    spec = load(MODULES)
    idx = load(INDEX)["skills"]
    module_names = [m["name"] for m in spec["modules"]]
    members = doc["members"]
    checks = []
    failed = []

    def add(cid, ok, detail):
        checks.append({"id": cid, "ok": bool(ok), "detail": detail})
        if not ok:
            failed.append(cid)

    add("S1", len(members) >= TARGET, "members=%d target=%d" % (len(members), TARGET))

    declared = doc.get("modules") or []
    same_modules = ([m["name"] for m in declared] == module_names)
    add("S2", len(module_names) == 10 and same_modules and doc.get("module_count") == 10,
        "modules=%d names_match=%s" % (len(declared), same_modules))

    counts = {n: sum(1 for x in members if x["module"] == n) for n in module_names}
    uncovered = [n for n in module_names if counts[n] == 0]
    add("S3", uncovered == [], "uncovered=%s min=%d" % (uncovered, min(counts.values()) if counts else 0))

    bad_module = [x["skill"] for x in members if x["module"] not in module_names]
    add("S4", bad_module == [], "unknown_module=%s" % (bad_module[:5]))

    names = [x["skill"] for x in members]
    add("S5", len(names) == len(set(names)), "dups=%d" % (len(names) - len(set(names))))

    base_from_index = {s["name"] for s in idx if s.get("mechanism") == "semantic_bus"}
    base_in_family = {x["skill"] for x in members if x["status"] == "base_index"}
    add("S6", base_from_index == base_in_family,
        "index=%d family=%d missing=%s extra=%s" % (
            len(base_from_index), len(base_in_family),
            sorted(base_from_index - base_in_family)[:3],
            sorted(base_in_family - base_from_index)[:3]))

    bad_label = [x["skill"] for x in members if x["status"] == "expanded" and x["label"] not in ("M", "K")]
    add("S7", bad_label == [], "expanded_bad_label=%s" % (bad_label[:5]))

    sha_now = recompute_sha(members)
    add("S8", sha_now == doc.get("sha256"), "sha_now=%s sha_doc=%s" % (sha_now[:12], str(doc.get("sha256"))[:12]))

    bridge = doc.get("bridge_candidates") or []
    bad_bridge = [b["skill"] for b in bridge if b.get("target_mechanism") not in BRIDGE_TARGETS]
    overlap = [b["skill"] for b in bridge if b["skill"] in set(names)]
    add("S9", (len(bridge) <= BRIDGE_MAX and bad_bridge == [] and overlap == []),
        "bridge=%d bad_target=%s overlap_with_members=%s" % (len(bridge), bad_bridge[:3], overlap[:3]))

    verdict = "PASS" if not failed else "FAIL"
    report = {
        "gate_id": "SG-B5-SEMANTIC-CHECK-V1",
        "family_id": doc.get("family_id"),
        "verdict": verdict,
        "failed": failed,
        "checks": checks,
        "member_count": len(members),
        "module_count": len(module_names),
        "module_counts": counts,
        "default_route_count": doc.get("default_route_count"),
        "anchor_member_count": doc.get("anchor_member_count"),
        "label_split": doc.get("label_split"),
        "bridge_candidates": len(bridge),
        "sha256": doc.get("sha256"),
    }
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n")

    if "--json" in argv:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(json.dumps({"verdict": verdict, "failed": failed,
                          "members": len(members), "modules": len(module_names),
                          "module_counts": counts, "bridge": len(bridge),
                          "sha256": doc.get("sha256"),
                          "report": OUT}, ensure_ascii=False, indent=2))
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
