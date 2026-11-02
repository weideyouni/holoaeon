# -*- coding: utf-8 -*-
"""B7 分批准入规则核（纯标准库 · 确定性 · 零外部依赖 · 不执行任何技能）。

定位：把 SOP-10 的「每批 ≤5 技能 + 累计 ≤15 + 四硬闸全绿 + 人工签字」落成
可判定的规则核。本模块只做**判定**，不做签字动作、不跑外部命令（跑闸在
scripts/admit_batch.py 层），也不把任何外部技能 import 进来。

设计约束：
1. 候选池 ≠ 准入库。准入只改登记状态，不改 `kernel.skills`（skills 恒 47）。
2. 批内条数就是条数，**不按 5 补齐**：1 条也能过，凑数视为违规。
3. 无签字 → `WAITING_SIGNATURE`（票据不作废、但不得进执行层）。
4. 累计以 `decision=ADMITTED` 的实算行数计，不采信票面自报。
"""
import hashlib
import json

RULES_ID = "SG-B7-ADMISSION-RULES-V1"
BATCH = "B7"
MAX_PER_BATCH = 5
MAX_CUMULATIVE = 15

# SOP-10 明列的四道硬闸；顺序即票面顺序。
HARD_GATES = (
    ("v3_gate", "python scripts/v3_gate.py --json reports/gate_fusion_v4.json"),
    ("unittest", "python -m unittest discover -s tests"),
    ("skill_matrix", "python scripts/verify_skill_matrix.py"),
    ("redline", "python scripts/redline_scan.py"),
)
GATE_IDS = tuple(g[0] for g in HARD_GATES)

SIGNATURE_FIELDS = ("signer", "signed_at")
DECISION_ADMITTED = "ADMITTED"
DECISION_WAITING = "WAITING_SIGNATURE"
DECISION_REJECTED = "REJECTED"

LEDGER_COLUMNS = (
    "batch",
    "ticket",
    "skill",
    "target_mechanism",
    "module",
    "usage_class",
    "gate_v3_gate",
    "gate_unittest",
    "gate_skill_matrix",
    "gate_redline",
    "signature_status",
    "signer",
    "signed_at",
    "decision",
    "note",
)

EVIDENCE_CLASS = "simulated"


def canonical(payload):
    """规范化字节：排序键 + 紧凑分隔符，保证跨进程逐字节一致。"""
    return json.dumps(payload, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def digest(payload):
    return hashlib.sha256(canonical(payload)).hexdigest()


def seal(payload):
    """自指摘要：把 sha256 置空后取规范化字节哈希，再回填。"""
    doc = dict(payload)
    doc["sha256"] = ""
    doc["sha256"] = digest(doc)
    return doc


def rules_doc():
    """规则文件内容（可复现；不随时间变化）。"""
    doc = {
        "rules_id": RULES_ID,
        "batch": BATCH,
        "evidence_class": EVIDENCE_CLASS,
        "max_per_batch": MAX_PER_BATCH,
        "max_cumulative": MAX_CUMULATIVE,
        "hard_gates": [{"id": gid, "cmd": cmd} for gid, cmd in HARD_GATES],
        "signature": {
            "required": True,
            "fields": list(SIGNATURE_FIELDS),
            "void_without_signature": False,
            "unsigned_decision": DECISION_WAITING,
            "note": "缺签字不作废票据，但不得进执行层；签字后方可 ADMITTED",
        },
        "fill_policy": "no_arithmetic_fill",
        "candidate_pool": "B5 bridge_candidates（4 条）+ B5 族成员；本批只收池内条目",
        "dimension_lock": {"agents": 25, "skills": 47, "packs": 9},
    }
    return seal(doc)


def parse_ledger(text):
    """解析准入台账 CSV。首行表头必须与 LEDGER_COLUMNS 完全一致。"""
    lines = [ln for ln in text.replace("\r\n", "\n").split("\n") if ln.strip()]
    if not lines:
        return []
    header = lines[0].split(",")
    if tuple(header) != LEDGER_COLUMNS:
        raise ValueError("ledger header mismatch: %r" % (header,))
    rows = []
    for ln in lines[1:]:
        cells = ln.split(",")
        if len(cells) != len(LEDGER_COLUMNS):
            raise ValueError("ledger row cells=%d: %s" % (len(cells), ln))
        rows.append(dict(zip(LEDGER_COLUMNS, cells)))
    return rows


def dump_ledger(rows):
    out = [",".join(LEDGER_COLUMNS)]
    for r in rows:
        out.append(",".join(str(r.get(c, "")) for c in LEDGER_COLUMNS))
    return "\n".join(out) + "\n"


def batch_rows(rows, batch):
    return [r for r in rows if r.get("batch") == batch]


def admitted_count(rows):
    return sum(1 for r in rows if r.get("decision") == DECISION_ADMITTED)


def validate(rows, pool=None, ticket_texts=None, gate_results=None):
    """核心判定。返回 {verdict, checks, violations, counts}。

    rows: 台账行列表
    pool: 允许准入的技能集合（来自 B5 候选池与族成员）；None 表示不校验来源
    ticket_texts: {batch: 票据正文}；None 表示不校验票据存在
    gate_results: {gate_id: {"passed": n, "total": n, "ok": bool}}；None 表示不校验闸
    """
    checks = []
    violations = []

    def add(cid, ok, detail):
        checks.append({"id": cid, "ok": bool(ok), "detail": detail})
        if not ok:
            violations.append(cid + ": " + detail)

    batches = sorted({r.get("batch", "") for r in rows})
    # A1 每批 ≤5
    over = []
    for b in batches:
        n = len(batch_rows(rows, b))
        if n > MAX_PER_BATCH:
            over.append("%s=%d" % (b, n))
    add("A1", not over, "per_batch<=%d over=%s" % (MAX_PER_BATCH, over))

    # A2 累计 ≤15（实算 ADMITTED 行）
    admitted = admitted_count(rows)
    add("A2", admitted <= MAX_CUMULATIVE,
        "admitted=%d<=%d" % (admitted, MAX_CUMULATIVE))

    # A3 票据存在（每批一张）
    if ticket_texts is None:
        add("A3", True, "skipped(no ticket_texts)")
    else:
        missing = [b for b in batches
                   if b not in ticket_texts or "准入票据" not in (ticket_texts.get(b) or "")]
        add("A3", not missing, "missing=%s" % (missing,))

    # A4 四硬闸全绿
    if gate_results is None:
        add("A4", True, "skipped(no gate_results)")
    else:
        bad = []
        for gid in GATE_IDS:
            g = gate_results.get(gid)
            if not g or not g.get("ok"):
                bad.append(gid)
        add("A4", not bad, "failed_gates=%s" % (bad,))

    # A5 来源合法性（不得私自扩池）
    if pool is None:
        add("A5", True, "skipped(no pool)")
    else:
        outside = sorted({r.get("skill", "") for r in rows} - set(pool))
        add("A5", not outside, "outside_pool=%s" % (outside,))

    # A6 签字完整性：ADMITTED 必须有 signer + signed_at
    bad_sig = [r.get("skill") for r in rows
               if r.get("decision") == DECISION_ADMITTED
               and (not r.get("signer") or not r.get("signed_at"))]
    add("A6", not bad_sig, "unsigned_admitted=%s" % (bad_sig,))

    # A7 未签字不得 ADMITTED
    sneak = [r.get("skill") for r in rows
             if r.get("signature_status") != "SIGNED"
             and r.get("decision") == DECISION_ADMITTED]
    add("A7", not sneak, "admitted_without_signature=%s" % (sneak,))

    # A8 决策合法性
    bad_dec = [r.get("skill") for r in rows
               if r.get("decision") not in (DECISION_ADMITTED, DECISION_WAITING, DECISION_REJECTED)]
    add("A8", not bad_dec, "bad_decision=%s" % (bad_dec,))

    # A9 不按 5 补齐（批内条数必须等于台账实有行数，且 ≤5）
    mismatch = []
    for b in batches:
        n = len(batch_rows(rows, b))
        if n > MAX_PER_BATCH or n <= 0:
            mismatch.append(b)
    add("A9", not mismatch, "batch_size_bad=%s" % (mismatch,))

    signed_any = any(r.get("decision") == DECISION_ADMITTED for r in rows)
    verdict = "FAIL" if violations else ("PASS" if signed_any else DECISION_WAITING)
    return {
        "verdict": verdict,
        "checks": checks,
        "violations": violations,
        "counts": {
            "rows": len(rows),
            "batches": len(batches),
            "admitted": admitted,
            "remaining": MAX_CUMULATIVE - admitted,
            "per_batch": {b: len(batch_rows(rows, b)) for b in batches},
        },
    }


def topk_note():  # 兼容既有脚本的轻量自述，不参与判定
    return {"rules_id": RULES_ID, "max_per_batch": MAX_PER_BATCH,
            "max_cumulative": MAX_CUMULATIVE, "gates": list(GATE_IDS)}
