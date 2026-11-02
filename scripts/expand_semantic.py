#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""B5 · 语义技能族扩容（19 -> >=60）确定性构建器

规则（全部来自索引与 B3 标签，不手写结论）：
1. 基座：`data/skill_matrix_index.json` 中 mechanism == semantic_bus 的条目原样继承（19 条）。
2. 扩容：B3 标签为 M/K 的条目，按 `data/semantic_modules.json` 的十模块锚点做确定性打分，
   取每个模块内分数最高者，按模块顺序轮流配额，单模块上限 per_module_cap。
3. 康复域缺口候选：domain/描述含康复、且未入族的 M/K 条目中，各取 1 条挂到语义总线与经络，
   标记 status=candidate_bridge，不计入 60。
4. 模块恒为 ivsa 十模块，禁止第十一模块。

用法：
  python scripts/expand_semantic.py --target 60            # 写 data/semantic_family.json
  python scripts/expand_semantic.py --target 60 --check    # 只校验字节可复现
"""
import argparse
import csv
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
INDEX = os.path.join(ROOT, "data", "skill_matrix_index.json")
LABELS = os.path.join(ROOT, "data", "skill_usage_labels.csv")
MODULES = os.path.join(ROOT, "data", "semantic_modules.json")
OUT = os.path.join(ROOT, "data", "semantic_family.json")

FAMILY_ID = "SG-B5-SEMANTIC-FAMILY-V1"
EXPANSION_LABELS = ("M", "K")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_labels(path):
    out = {}
    with open(path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            out[row["name"]] = row["label"]
    return out


def text_of(skill):
    return (skill["name"] + " " + (skill.get("description") or "")).lower()


def hits_of(text, anchors):
    return sum(1 for a in anchors if a.lower() in text)


def best_module(text, modules, default_name):
    """确定性打分：命中数降序，平手按模块顺序。"""
    rows = []
    for i, m in enumerate(modules):
        rows.append((hits_of(text, m["anchors"]), -i, m["name"]))
    h, neg_i, name = max(rows)
    return (default_name if h == 0 else name, h)


def canonical(members, digests_in):
    body = json.dumps({"members": members, "sha256": ""}, ensure_ascii=False, sort_keys=True)
    sha = hashlib.sha256(body.encode("utf-8")).hexdigest()
    return dict(digests_in, sha256=sha)


def build(target, spec_path=MODULES):
    idx = load_json(INDEX)["skills"]
    labels = load_labels(LABELS)
    spec = load_json(spec_path)
    modules = spec["modules"]
    default_name = spec["default_module"]
    cap = spec["targets"]["per_module_cap"]

    by_name = {s["name"]: s for s in idx}
    raw_base = [s for s in idx if s.get("mechanism") == "semantic_bus"]
    base = []
    seen_base = set()
    for s in raw_base:
        if s["name"] in seen_base:
            continue
        seen_base.add(s["name"])
        base.append(s)
    base_names = {s["name"] for s in base}

    pools = {m["name"]: [] for m in modules}
    for s in idx:
        if s["name"] in base_names:
            continue
        if labels.get(s["name"]) not in EXPANSION_LABELS:
            continue
        text = text_of(s)
        name, h = best_module(text, modules, default_name)
        if h == 0:
            continue
        total = sum(hits_of(text, m["anchors"]) for m in modules)
        pools[name].append((-h, -(h / total if total else 0.0), s["name"]))

    for k in pools:
        pools[k].sort()

    members = []
    default_route_count = 0
    for s in base:
        name, h = best_module(text_of(s), modules, default_name)
        basis = "anchor" if h > 0 else "default_route"
        if basis == "default_route":
            default_route_count += 1
        members.append({
            "skill": s["name"],
            "module": name,
            "module_basis": basis,
            "status": "base_index",
            "label": labels.get(s["name"], "?"),
            "mechanism": "semantic_bus",
            "source": "index:mechanism=semantic_bus",
        })

    taken = set(base_names)
    chosen = {m["name"]: 0 for m in modules}
    order = [m["name"] for m in modules]
    round_no = 0
    while len(members) < target and round_no < cap:
        round_no += 1
        for name in order:
            if len(members) >= target:
                break
            if chosen[name] >= cap:
                continue
            pool = pools[name]
            while pool:
                cand = pool.pop(0)[2]
                if cand in taken:
                    continue
                taken.add(cand)
                s = by_name[cand]
                members.append({
                    "skill": cand,
                    "module": name,
                    "module_basis": "anchor",
                    "status": "expanded",
                    "label": labels.get(cand, "?"),
                    "mechanism": s.get("mechanism"),
                    "source": "B3 label M/K + module anchors",
                })
                chosen[name] += 1
                break

    members.sort(key=lambda x: (x["module"], x["skill"]))

    bridge = []
    want = {"semantic_bus": spec["targets"]["bridge_candidates"] - 1, "meridian": 1}

    def has_mech(mech):
        return sum(1 for b in bridge if b["target_mechanism"] == mech)

    for s in idx:
        if has_mech("semantic_bus") >= want["semantic_bus"] and has_mech("meridian") >= want["meridian"]:
            break
        if s["name"] in taken or s["name"] in base_names:
            continue
        if labels.get(s["name"]) not in EXPANSION_LABELS:
            continue
        text = text_of(s)
        if "康复" not in text and "rehabilitation" not in text:
            continue
        target_mech = "meridian" if (s.get("mechanism") == "meridian" or "经络" in text or "meridian" in text) else "semantic_bus"
        if has_mech(target_mech) >= want[target_mech]:
            continue
        name, h = best_module(text, modules, default_name)
        bridge.append({
            "skill": s["name"],
            "module": name,
            "module_basis": "anchor" if h > 0 else "default_route",
            "target_mechanism": target_mech,
            "label": labels.get(s["name"]),
            "status": "candidate_bridge",
            "note": "康复域缺 M 类语义/经络技能，登记为候选，B7 准入前不进执行层",
        })

    module_counts = {}
    for m in modules:
        module_counts[m["name"]] = sum(1 for x in members if x["module"] == m["name"])

    doc = {
        "family_id": FAMILY_ID,
        "domain_scope": "semantic_bus",
        "modules": [{"id": m["id"], "name": m["name"]} for m in modules],
        "module_count": len(modules),
        "member_count": len(members),
        "target": target,
        "base_entry_count": len(raw_base),
        "base_count": len(base),
        "base_dup_names": len(raw_base) - len(base),
        "expanded_count": len(members) - len(base),
        "module_counts": module_counts,
        "uncovered_modules": [k for k, v in module_counts.items() if v == 0],
        "default_route_count": default_route_count,
        "anchor_member_count": len(members) - default_route_count,
        "label_split": {
            "M": sum(1 for x in members if x["label"] == "M"),
            "K": sum(1 for x in members if x["label"] == "K"),
            "other": sum(1 for x in members if x["label"] not in ("M", "K")),
        },
        "members": members,
        "bridge_candidates": bridge,
        "inputs": {
            "index_count": len(idx),
            "index_digest": load_json(INDEX).get("digest"),
            "usage_labels": "SG-B3-SKILL-USAGE-LABELS-V1",
            "module_spec": spec["spec_id"],
        },
        "sha256": "",
    }
    doc = canonical(members, doc)
    return doc


def dump(doc, path):
    text = json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return text


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=int, default=60)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--spec", default=MODULES,
                    help="模块规格件；V4.1 用 data/semantic_modules_v4.json（cap=10, min=100）")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)

    doc = build(args.target, args.spec)
    text = dump(doc, args.out)
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()

    if args.check:
        if not os.path.isfile(args.out):
            print(json.dumps({"verdict": "FAIL", "reason": "missing output"}, ensure_ascii=False))
            return 1
        old = open(args.out, "r", encoding="utf-8").read()
        same = old == text
        print(json.dumps({"byte_consistent": same, "sha256": sha,
                          "members": doc["member_count"],
                          "modules": doc["module_count"]}, ensure_ascii=False))
        return 0 if same else 1

    print(json.dumps({"out": args.out, "sha256": sha,
                      "members": doc["member_count"],
                      "base_entries": doc["base_entry_count"],
                      "base_unique": doc["base_count"],
                      "expanded": doc["expanded_count"],
                      "module_counts": doc["module_counts"],
                      "uncovered": doc["uncovered_modules"],
                      "bridge": len(doc["bridge_candidates"])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
