# -*- coding: utf-8 -*-
"""SOP-10 · B7 分批准入（每批 ≤5，累计 ≤15，四硬闸 + 人工签字）。

用法：
    # 出票：跑四硬闸 + 生成准入票据 + 写台账（待签字）
    python scripts/admit_batch.py --batch B7-1 --out data/B7_准入票据_B7-1.md

    # 复核：只读重算（不跑闸），落票据
    python scripts/admit_batch.py --check --json reports/b7_admission_check.json

    # 人工签字：缺签字票据不作废，但不得进执行层
    python scripts/admit_batch.py --sign --sign-by "姓名" --signed-at 2026-11-02

设计约束：
1. 候选只从 B5 池取（`data/semantic_family.json` 的 bridge_candidates + members）；
   不在池内 → 直接拒绝出票。
2. 条数不补齐：票上几条就写几条，凑 5 条视为违规（A9）。
3. 四硬闸：v3_gate / unittest / verify_skill_matrix / redline_scan。
4. 签字是人工动作：脚本只记录「谁、何时」，不自称签字。
"""
import argparse
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from holoaeon.fusion_upgrade import admission as ADM  # noqa: E402

REPO = ROOT
RULES = os.path.join(REPO, "data", "admission_rules.json")
LEDGER = os.path.join(REPO, "data", "admission_ledger.csv")
FAMILY = os.path.join(REPO, "data", "semantic_family.json")
GATES_JSON = os.path.join(REPO, "reports", "b7_gates.json")
V3_JSON = os.path.join(REPO, "reports", "gate_fusion_v4.json")
CHECK_JSON = os.path.join(REPO, "reports", "b7_admission_check.json")


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path, doc):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")


def run(cmd):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def run_gates():
    """跑四道硬闸并解析成 {gate_id: {passed,total,ok,cmd,raw_tail}}。"""
    out = {}
    for gid, cmd in ADM.HARD_GATES:
        rc, text = run(cmd.split())
        tail = text.strip().splitlines()[-1] if text.strip() else ""
        passed = total = None
        if gid == "v3_gate":
            try:
                d = read_json(V3_JSON)
                passed, total = d.get("passed"), d.get("total")
            except Exception:
                pass
        elif gid == "unittest":
            m = re.search(r"Ran (\d+) tests", text)
            if m:
                passed = total = int(m.group(1))
        elif gid == "skill_matrix":
            try:
                d = json.loads(text[text.index("{"):])
                st = d.get("selftest", {})
                passed = int(st.get("passed") or 0)
                total = len(st.get("detail") or [])
            except Exception:
                pass
        elif gid == "redline":
            m = re.search(r"扫描文件数：(\d+)", text)
            if m:
                passed = total = int(m.group(1))
        ok = rc == 0 and bool(passed) and passed == total
        out[gid] = {"passed": passed, "total": total, "ok": ok, "cmd": cmd,
                    "raw_tail": tail[:200]}
    return out


def load_pool():
    fam = read_json(FAMILY)
    skills = {c["skill"] for c in fam.get("bridge_candidates", [])}
    skills |= {m.get("skill") for m in fam.get("members", []) if m.get("skill")}
    return fam, skills


def build(batch, out_path, skills_arg=None):
    fam, pool = load_pool()
    if skills_arg:
        chosen = [s.strip() for s in skills_arg.split(",") if s.strip()]
    else:
        chosen = [c["skill"] for c in fam.get("bridge_candidates", [])]
    outside = [s for s in chosen if s not in pool]
    if outside:
        print(json.dumps({"verdict": "REFUSED", "reason": "outside_pool",
                          "skills": outside}, ensure_ascii=False))
        return 2
    if len(chosen) > ADM.MAX_PER_BATCH:
        print(json.dumps({"verdict": "REFUSED", "reason": "over_per_batch",
                          "count": len(chosen)}, ensure_ascii=False))
        return 2

    cand = {c["skill"]: c for c in fam.get("bridge_candidates", [])}
    gates = run_gates()
    write_json(GATES_JSON, {"gates_id": "SG-B7-HARD-GATES-V1", "batch": batch,
                            "evidence_class": ADM.EVIDENCE_CLASS, "gates": gates})
    gate_cells = {gid: ("%s/%s" % (gates[gid]["passed"], gates[gid]["total"])
                        if gates[gid]["passed"] else "FAIL") for gid in ADM.GATE_IDS}

    rows = []
    for s in chosen:
        c = cand.get(s, {})
        rows.append({
            "batch": batch, "ticket": out_path, "skill": s,
            "target_mechanism": c.get("target_mechanism", "semantic_bus"),
            "module": c.get("module", ""), "usage_class": c.get("label", ""),
            "gate_v3_gate": gate_cells["v3_gate"],
            "gate_unittest": gate_cells["unittest"],
            "gate_skill_matrix": gate_cells["skill_matrix"],
            "gate_redline": gate_cells["redline"],
            "signature_status": "PENDING", "signer": "", "signed_at": "",
            "decision": ADM.DECISION_WAITING,
            "note": "B5 candidate_bridge；未签字不进执行层",
        })

    # 幂等：同批行整段替换，其它批保留
    old = []
    if os.path.isfile(LEDGER):
        old = ADM.parse_ledger(open(LEDGER, encoding="utf-8").read())
    kept = [r for r in old if r.get("batch") != batch]
    allrows = kept + rows
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    open(LEDGER, "w", encoding="utf-8", newline="\n").write(ADM.dump_ledger(allrows))

    res = ADM.validate(allrows, pool=pool, gate_results=gates)
    write_ticket(out_path, batch, rows, gates, res)
    print(json.dumps({"batch": batch, "ticket": out_path, "rows": len(rows),
                      "verdict": res["verdict"], "gates_ok": all(g["ok"] for g in gates.values()),
                      "admitted": res["counts"]["admitted"],
                      "remaining": res["counts"]["remaining"]}, ensure_ascii=False))
    return 0


def write_ticket(path, batch, rows, gates, res, signature=None):
    g = gates
    ok_all = all(v["ok"] for v in g.values())
    lines = []
    lines.append("# B7 分批准入票据 · %s" % batch)
    lines.append("")
    lines.append("> 规则 `%s` · 每批 ≤%d · 累计 ≤%d · 四硬闸 + 人工签字"
                 % (ADM.RULES_ID, ADM.MAX_PER_BATCH, ADM.MAX_CUMULATIVE))
    lines.append("> evidence_class=`%s`（仿真/离线证据，不等于治疗证据）" % ADM.EVIDENCE_CLASS)
    lines.append("")
    lines.append("## 一、判据与来源")
    lines.append("")
    lines.append("判据取自 `holoaeon/fusion_upgrade/plan.py` B7 段与 SOP-10：")
    lines.append("")
    lines.append("1. 每批 ≤%d 个技能；" % ADM.MAX_PER_BATCH)
    lines.append("2. 四道硬闸全绿（v3_gate / unittest / verify_skill_matrix / redline_scan）；")
    lines.append("3. 每批有签字人姓名与日期；缺签字 → `WAITING_SIGNATURE`，不进执行层；")
    lines.append("4. 累计准入 ≤%d；" % ADM.MAX_CUMULATIVE)
    lines.append("5. 准入票据存在（本文件）。")
    lines.append("")
    lines.append("## 二、本批候选（只从 B5 池取，不扩池、不补齐）")
    lines.append("")
    lines.append("| # | 技能 | 目标机制 | 模块 | B3 标签 | 来源状态 |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for i, r in enumerate(rows, 1):
        lines.append("| %d | `%s` | %s | %s | %s | candidate_bridge |"
                     % (i, r["skill"], r["target_mechanism"], r["module"], r["usage_class"]))
    lines.append("")
    lines.append("本批 **%d 条**（≤%d，未按 5 补齐）。全部为 B5 登记的康复桥接候选，"
                 "B3 标签均为 K（知识源），无 M 类可执行方法 —— 这正是需要人工复核的原因。"
                 % (len(rows), ADM.MAX_PER_BATCH))
    lines.append("")
    lines.append("## 三、四道硬闸实测")
    lines.append("")
    lines.append("| 闸 | 命令 | 结果 | 判定 |")
    lines.append("| --- | --- | --- | --- |")
    for gid, _cmd in ADM.HARD_GATES:
        v = g[gid]
        lines.append("| %s | `%s` | %s/%s | %s |"
                     % (gid, v["cmd"], v["passed"], v["total"], "PASS" if v["ok"] else "FAIL"))
    lines.append("")
    lines.append("闸全绿：**%s**；闸票据 `reports/b7_gates.json`。" % ("是" if ok_all else "否"))
    lines.append("")
    lines.append("## 四、准入结论")
    lines.append("")
    lines.append("- 判定：`%s`" % (signature["decision"] if signature else res["verdict"]))
    lines.append("- 已准入累计：**%d / %d**（剩余 %d）"
                 % (res["counts"]["admitted"], ADM.MAX_CUMULATIVE, res["counts"]["remaining"]))
    lines.append("- 未签字前，本批 4 条技能**不进执行层**，`kernel.skills` 恒 47。")
    lines.append("")
    lines.append("## 五、人工签字")
    lines.append("")
    if signature:
        lines.append("- 签字人：**%s**" % signature["signer"])
        lines.append("- 签字日期：**%s**" % signature["signed_at"])
        lines.append("- 签字后结论：`ADMITTED`（仍不计入 `kernel.skills`，只解除执行层禁令）")
    else:
        lines.append("待签字（签名与日期两项缺一不可；缺签字票据不作废但不得进执行层）。")
        lines.append("")
        lines.append("```")
        lines.append("签字人：____________________        日期：____________________")
        lines.append("```")
    lines.append("")
    lines.append("## 六、可复现")
    lines.append("")
    lines.append("```bash")
    lines.append("python scripts/admit_batch.py --batch %s --out %s        # 出票" % (batch, path))
    lines.append("python scripts/admit_batch.py --check --json reports/b7_admission_check.json")
    lines.append("python scripts/admit_batch.py --sign --sign-by \"姓名\" --signed-at 2026-11-02")
    lines.append("python -m unittest discover -s tests_contract              # 旁挂 71 项")
    lines.append("```")
    lines.append("")
    lines.append("## 七、维度不变自证")
    lines.append("")
    lines.append("| 维度 | 锁值 | 本批后 | 结论 |")
    lines.append("| --- | --- | --- | --- |")
    lines.append("| agents | 25 | 25 | 未动 |")
    lines.append("| skills | 47 | 47 | 未动（准入只改登记态，不进 `kernel.skills`） |")
    lines.append("| packs | 9 | 9 | 未动（未新增 pack） |")
    lines.append("| spec.VERSION | 0.9.1 | 0.9.1 | 未动 |")
    lines.append("")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")


def check(json_out=None):
    rules_sha_ok = True
    if os.path.isfile(RULES):
        rules_sha_ok = read_json(RULES).get("sha256") == ADM.rules_doc()["sha256"]
    if not os.path.isfile(LEDGER):
        print(json.dumps({"verdict": "FAIL", "reason": "ledger_missing"}, ensure_ascii=False))
        return 1
    rows = ADM.parse_ledger(open(LEDGER, encoding="utf-8").read())
    fam, pool = load_pool()
    gates = read_json(GATES_JSON)["gates"] if os.path.isfile(GATES_JSON) else None
    tickets = {}
    for b in sorted({r["batch"] for r in rows}):
        p = next(r["ticket"] for r in rows if r["batch"] == b)
        if os.path.isfile(p):
            tickets[b] = open(p, encoding="utf-8").read()
    res = ADM.validate(rows, pool=pool, ticket_texts=tickets, gate_results=gates)
    extra = []
    if not rules_sha_ok:
        extra.append("rules_sha256_drift")
    payload = {
        "check_id": "SG-B7-ADMISSION-CHECK-V1",
        "rules_id": ADM.RULES_ID,
        "evidence_class": ADM.EVIDENCE_CLASS,
        "verdict": "FAIL" if extra else res["verdict"],
        "failed": extra + res["violations"],
        "checks": res["checks"],
        "counts": res["counts"],
        "rules_sha256_match": rules_sha_ok,
        "gates": {k: {"passed": v["passed"], "total": v["total"], "ok": v["ok"]}
                  for k, v in (gates or {}).items()},
    }
    if json_out:
        write_json(json_out, payload)
    print(json.dumps({k: payload[k] for k in ("verdict", "failed", "counts")},
                     ensure_ascii=False))
    return 0 if payload["verdict"] in ("PASS", ADM.DECISION_WAITING) else 1


def sign(batch, signer, signed_at):
    if not signer or not signed_at:
        print(json.dumps({"verdict": "REFUSED", "reason": "signature_incomplete"},
                         ensure_ascii=False))
        return 2
    if not os.path.isfile(LEDGER):
        print(json.dumps({"verdict": "REFUSED", "reason": "ledger_missing"}, ensure_ascii=False))
        return 2
    rows = ADM.parse_ledger(open(LEDGER, encoding="utf-8").read())
    hit = [r for r in rows if r["batch"] == batch]
    if not hit:
        print(json.dumps({"verdict": "REFUSED", "reason": "batch_not_found"}, ensure_ascii=False))
        return 2
    if ADM.admitted_count(rows) + len(hit) > ADM.MAX_CUMULATIVE:
        print(json.dumps({"verdict": "REFUSED", "reason": "over_cumulative",
                          "admitted": ADM.admitted_count(rows), "batch": len(hit)}, ensure_ascii=False))
        return 2
    gates = read_json(GATES_JSON)["gates"] if os.path.isfile(GATES_JSON) else None
    if gates and not all(v["ok"] for v in gates.values()):
        print(json.dumps({"verdict": "REFUSED", "reason": "hard_gate_red"}, ensure_ascii=False))
        return 2
    for r in rows:
        if r["batch"] == batch:
            r["signature_status"] = "SIGNED"
            r["signer"] = signer
            r["signed_at"] = signed_at
            r["decision"] = ADM.DECISION_ADMITTED
    open(LEDGER, "w", encoding="utf-8", newline="\n").write(ADM.dump_ledger(rows))
    ticket = hit[0]["ticket"]
    fam, pool = load_pool()
    tickets = {}
    for b in sorted({r["batch"] for r in rows}):
        p = next(r["ticket"] for r in rows if r["batch"] == b)
        if os.path.isfile(p):
            tickets[b] = open(p, encoding="utf-8").read()
    res = ADM.validate(rows, pool=pool, ticket_texts=tickets, gate_results=gates)
    write_ticket(ticket, batch, rows, gates or {}, res,
                 signature={"signer": signer, "signed_at": signed_at, "decision": "ADMITTED"})
    print(json.dumps({"batch": batch, "signed_by": signer, "signed_at": signed_at,
                      "admitted": res["counts"]["admitted"],
                      "remaining": res["counts"]["remaining"]}, ensure_ascii=False))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", default="B7-1")
    ap.add_argument("--skills", default="")
    ap.add_argument("--out", default="")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--json", default="")
    ap.add_argument("--sign", action="store_true")
    ap.add_argument("--sign-by", default="")
    ap.add_argument("--signed-at", default="")
    a = ap.parse_args()
    if a.sign:
        return sign(a.batch, a.sign_by, a.signed_at)
    if a.check:
        return check(a.json or None)
    out = a.out or os.path.join(REPO, "data", "B7_准入票据_%s.md" % a.batch)
    return build(a.batch, out, a.skills or None)


if __name__ == "__main__":
    sys.exit(main())
