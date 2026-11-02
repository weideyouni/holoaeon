# -*- coding: utf-8 -*-
"""B4 康复域试点 20 例校验器（R1–R9）。只读判定，不改数据。

R1 例数 20 且 case_id 严格 RP-01..RP-20
R2 每例契约 validate_v1 通过，且 contract_id 可复算（指纹不漂移）
R3 每例技能必须真实存在且 B3 判为 M（不许拿 K/T 冒充可执行方法）
R4 每例 mechanism 必须等于索引侧实际机制（不是手写字面量）
R5 target 必须命中 ivsa 真实模块白名单（只映射不调用）
R6 域分布 general ≥ 10 且 medical ≥ 8；medical 三红线齐且全 true
R7 无剂量词、note ≤ 200、budget 为整数且 0–100、lane ∈ read/write
R8 4 条负例探针全部被拒，且命中预期规则编号
R9 复跑字节一致（构建器 --check 同源，这里复核摘要）

用法：python scripts/check_rehab_pilot.py [--json reports/b4_rehab_pilot_check.json]
"""
import argparse
import csv
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from holoaeon.fusion_upgrade import contract as C  # noqa: E402

PILOT = os.path.join(ROOT, "data", "rehab_pilot_20.json")
INDEX = os.path.join(ROOT, "data", "skill_matrix_index.json")
LABELS = os.path.join(ROOT, "data", "skill_usage_labels.csv")
OUT = os.path.join(ROOT, "reports", "b4_rehab_pilot_check.json")

IVSA_MODULES = {
    "ivsa.heartbeat_engine", "ivsa.cytoskeleton", "ivsa.semantic_bus", "ivsa.hebbian_field",
    "ivsa.meridian_mechanism", "ivsa.rehab_host", "ivsa.rehab_ontology", "ivsa.skin_v6",
    "ivsa.skin", "ivsa.sanchang_evidence", "ivsa.model_adapter", "ivsa.eda_pipeline",
    "ivsa.runtime_graph", "ivsa.threadbus", "ivsa.knowledge", "ivsa.spec",
    "ivsa.skin_layers.L1_collapse_addr", "ivsa.skin_layers.L2_resonance_injector",
    "ivsa.skin_layers.L3_trilaminar_align", "ivsa.skin_layers.L4_four_closed_loop",
    "ivsa.skin_layers.L5_dual_track_arbiter", "ivsa.skin_layers.L6_self_learn_inflection",
    "ivsa.skin_layers.L7_quadro_carry", "ivsa.skin_layers.L8_crossthread_verify",
}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=OUT)
    args = ap.parse_args(argv)

    checks = []

    def add(cid, ok, detail):
        checks.append({"id": cid, "ok": bool(ok), "detail": detail})

    for p in (PILOT, INDEX, LABELS):
        if not os.path.isfile(p):
            add("R0", False, "missing={}".format(os.path.basename(p)))
            return finish(checks, args.json)

    with open(PILOT, encoding="utf-8") as f:
        raw = f.read()
    doc = json.loads(raw)
    with open(INDEX, encoding="utf-8") as f:
        idx = json.load(f)
    with open(LABELS, encoding="utf-8") as f:
        labels = {r["name"]: r["label"] for r in csv.DictReader(f)}
    by_name = {x["name"]: x for x in idx["skills"]}

    cases = doc["cases"]
    ids = [c["case_id"] for c in cases]
    add("R1", len(cases) == 20 and ids == ["RP-%02d" % i for i in range(1, 21)],
        "count={} ids_ok={}".format(len(cases), ids == ["RP-%02d" % i for i in range(1, 21)]))

    bad = []
    for c in cases:
        res = C.validate_v1(c["contract"])
        recomputed = C.fingerprint({k: c["contract"][k] for k in C.FINGERPRINT_KEYS
                                    if k in c["contract"]})
        if not res["ok"] or res["contract_id"] != recomputed or c["contract"]["contract_id"] != recomputed:
            bad.append({"case": c["case_id"], "errors": res["errors"]})
    add("R2", not bad, "invalid={}".format(bad[:3]))

    bad_skill = [c["case_id"] for c in cases
                 if c["skill"] not in by_name or c["skill"] not in labels or labels[c["skill"]] != "M"]
    add("R3", not bad_skill, "not_executable_M={}".format(bad_skill))

    drift = [{"case": c["case_id"], "doc": c["mechanism"], "index": by_name.get(c["skill"], {}).get("mechanism")}
             for c in cases if by_name.get(c["skill"], {}).get("mechanism") != c["mechanism"]]
    add("R4", not drift, "mechanism_drift={}".format(drift[:3]))

    bad_target = [c["case_id"] for c in cases if c["target"] not in IVSA_MODULES]
    add("R5", not bad_target, "unknown_target={}".format(bad_target))

    dom = {"general": sum(1 for c in cases if c["payload_domain"] == "general"),
           "medical": sum(1 for c in cases if c["payload_domain"] == "medical")}
    med_bad = [c["case_id"] for c in cases if c["payload_domain"] == "medical"
               and not all(c["contract"]["payload"].get("redlines", {}).get(k) is True
                           for k in C.REDLINE_KEYS)]
    add("R6", dom["general"] >= 10 and dom["medical"] >= 8 and not med_bad,
        "split={} medical_missing_redlines={}".format(dom, med_bad))

    dose_bad, note_bad, budget_bad, lane_bad = [], [], [], []
    for c in cases:
        blob = (c["contract"].get("note") or "") + json.dumps(c["contract"].get("payload", {}).get("notes") or "",
                                                              ensure_ascii=False)
        if any(m in blob.lower() for m in C.DOSE_MARKERS):
            dose_bad.append(c["case_id"])
        if len(c["contract"].get("note") or "") > C.NOTE_MAX:
            note_bad.append(c["case_id"])
        b = c["contract"].get("budget")
        if not isinstance(b, int) or isinstance(b, bool) or not (C.BUDGET_RANGE[0] <= b <= C.BUDGET_RANGE[1]):
            budget_bad.append(c["case_id"])
        if c["lane"] not in ("read", "write"):
            lane_bad.append(c["case_id"])
    add("R7", not (dose_bad or note_bad or budget_bad or lane_bad),
        "dose={} note={} budget={} lane={}".format(dose_bad, note_bad, budget_bad, lane_bad))

    probes = doc["negative_probes"]
    rejected = [p["probe_id"] for p in probes if p["rejected"]]
    matched = [p["probe_id"] for p in probes
               if p["rejected"] and any(e.startswith(p["expected_rule"]) for e in p["errors"])]
    add("R8", len(probes) == 4 and len(rejected) == 4 and len(matched) == 4,
        "probes={} rejected={} rule_matched={}".format(len(probes), rejected, matched))

    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import importlib.util
    spec = importlib.util.spec_from_file_location("grp", os.path.join(ROOT, "scripts", "gen_rehab_pilot.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    same = mod.dump(mod.build()) == raw
    add("R9", same, "byte_consistent={} sha256={}".format(
        same, hashlib.sha256(raw.encode("utf-8")).hexdigest()))

    return finish(checks, args.json, doc)


def finish(checks, out_path, doc=None):
    verdict = "PASS" if all(c["ok"] for c in checks) else "FAIL"
    payload = {"batch": "B4", "verdict": verdict,
               "failed": [c["id"] for c in checks if not c["ok"]], "checks": checks}
    if doc is not None:
        payload.update({"case_count": doc.get("case_count"),
                        "domain_split": doc.get("domain_split"),
                        "mechanism_split": doc.get("mechanism_split"),
                        "uncovered_mechanisms": doc.get("uncovered_mechanisms")})
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
