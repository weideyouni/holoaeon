# -*- coding: utf-8 -*-
"""prehistory_criteria.py —— 史前矩阵判据三档 + selftest 三层证据 + B4 点单闸门（V70）

定位：把「194 还是 199」「22 个 selftest 到底跑没跑」「B4 那 10 GB 动不动」这三类
扯不清的账，各装一条可失败判据。**本模块不写文件、不读史前原件、不碰 18 仓。**

三条硬纪律（写进代码）：
1. 判据优先于数字：任何计数都由 criteria 字符串导出，改了字符串就跑出新的数，
   不许再手写 194/199/201；口径一变，`set_drift` 立刻红。
2. 证据必须分层：`rc=0` 不是「全绿」。L1 静态存在 / L2 隔离实跑 / L3 有断言且实跑，
   三层各自计数，任何一层不许冒充上一层。
3. 授权前不碰：B4 九项只出点单表，未点单一律 `SUSPENDED`；本模块没有搬运函数。

指纹口径（与 prehistory_ledger 同风格，诚实标注）：
- 集合指纹 `set_sha16` = sha256("\n".join(sorted(names)))[:16]
  —— 能证明「名单逐字未变」，不能证明「这些目录里内容未变」。
"""
import hashlib
import json
import os
import re

CRITERIA_SCHEMA = "PREHISTORY-CRITERIA-v1"
CRITERIA_VERSION = "1.0"

# ---- 判据三档（碳基 2026-11-12 点单：核心 194 保留 + 全集 201 并列）----
CRITERIA_V1 = r"(1331x1331|矩阵实战化|矩阵V3|多智能体矩阵)"
CRITERIA_V68 = r"(1331|矩阵实战化)"
CRITERIA_UNION = r"(1331|矩阵实战化|矩阵V3|多智能体矩阵)"
TIERS = ("v1", "v68", "union")
TIER_LABEL = {
    "v1": "核心集（V1 严格判据，原样保留）",
    "v68": "V68 口径（最简复现 199，仅作对照，不作唯一口径）",
    "union": "全集（并集，与核心集并列登记）",
}
EXPECT_COUNT = {"v1": 194, "v68": 199, "union": 201}
EXPECT_INTERSECTION = 192
EXPECT_ONLY_IN_199 = (
    "_universe1331_build",
    "hermes_1331_bridge_20261026",
    "坍缩矩阵1331_WorkBuddy模拟端口",
    "坍缩矩阵1331通道_跨线程有机模块_20261023",
    "数学大师1331_数学史早课",
    "昭明文选1331矩阵升级包_20261016",
    "类硅基生命V2.0_1331x131基座_20261017",
)
EXPECT_ONLY_IN_194 = (
    "人类疾病图谱融合矩阵V3实战化_20261019",
    "昭明文选数字分身_超级矩阵V3实战化_20261018",
)
EXPECT_SET_SHA16 = "aae1c8aea9199ee7"

# ---- selftest 三层证据（V70 实跑口径）----
SELFTEST_TOTAL = 22
SELFTEST_L3_MIN = 21
ASSERTS_SUM = 1410
ASSERTS_MIN = 0
ASSERTS_MAX = 96
KNOWN_ZERO_ASSERT = (
    "北京瑶医医院项目管理1331x1331_SUPER-MAS-V3.0_runtime_20261018.zip"
)
SELFTEST_LAYERS = ("L1", "L2", "L3")
LAYER_MEANING = {
    "L1": "AST 静态审查：可解析、assert 计数可读、无危险调用",
    "L2": "隔离沙箱实跑：只跑 selftest.py，rc=0",
    "L3": "有断言且实跑 rc=0（L1 断言数 > 0 且 L2 rc = 0）",
}

# ---- B4 九项点单闸门（全 SUSPENDED，未点单不碰）----
B4_COUNT = 9
B4_FILES = 119157
B4_MB = 10166.9
B4_STATES = ("AUTHORIZED", "EXCLUDED", "SUSPENDED")
B4_ALLOW_FIRST_BATCH = {"AUTHORIZED"}


def _ok(flag):
    return bool(flag)


def match_names(names, criteria):
    """按判据正则筛选，返回排序后的名单。正则写死在模块里，不接受外部注入。"""
    pat = re.compile(criteria)
    return sorted(n for n in names if pat.search(n))


def tiers(names):
    """三档计数 + 交集 + 并集指纹。names 为顶层目录名列表（只读输入）。"""
    v1 = match_names(names, CRITERIA_V1)
    v68 = match_names(names, CRITERIA_V68)
    union = match_names(names, CRITERIA_UNION)
    return {
        "v1": v1,
        "v68": v68,
        "union": union,
        "count": {"v1": len(v1), "v68": len(v68), "union": len(union)},
        "intersection": len(set(v1) & set(v68)),
        "only_in_199": sorted(set(v68) - set(v1)),
        "only_in_194": sorted(set(v1) - set(v68)),
        "set_sha16": set_fingerprint(union),
    }


def set_fingerprint(names):
    """集合指纹：sha256("\n".join(sorted(names)))[:16]。"""
    payload = "\n".join(sorted(names))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def scan_tier_names(root):
    """只列顶层目录名（不递归、不读内容）。返回 (names, note)。"""
    names = []
    note = ""
    try:
        with os.scandir(root) as it:
            for e in it:
                try:
                    if e.is_dir(follow_symlinks=False):
                        names.append(e.name)
                except OSError:
                    continue
    except OSError as exc:
        note = "scan failed: %s" % exc
    return sorted(names), note


def selftest_layers(static_rows, run_rows):
    """把静态审查行与实跑行合成三层覆盖。

    static_rows: [{zip, asserts, danger, ...}]
    run_rows:    [{zip, rc, state, sec, ...}]
    """
    static_by = {r["zip"]: r for r in (static_rows or [])}
    run_by = {r["zip"]: r for r in (run_rows or [])}
    both = sorted(set(static_by) & set(run_by))
    l1 = sorted(z for z in both if not static_by[z].get("danger"))
    l2 = sorted(z for z in both if int(run_by[z].get("rc", 1)) == 0
                and str(run_by[z].get("state", "")) == "pass")
    l3 = sorted(z for z in l2 if int(static_by[z].get("asserts", 0)) > 0)
    zero_assert = sorted(z for z in both if int(static_by[z].get("asserts", 0)) == 0)
    return {
        "total": len(both),
        "L1": len(l1),
        "L2": len(l2),
        "L3": len(l3),
        "zero_assert": zero_assert,
        "asserts_sum": sum(int(static_by[z].get("asserts", 0)) for z in both),
        "asserts_min": min((int(static_by[z].get("asserts", 0)) for z in both), default=0),
        "asserts_max": max((int(static_by[z].get("asserts", 0)) for z in both), default=0),
        "rc_nonzero": sorted(z for z in both if int(run_by[z].get("rc", 1)) != 0),
        "danger_any": sorted(z for z in both if static_by[z].get("danger")),
    }


def b4_candidates(ledger):
    """从 V68 台账切片出 B4 候选（零额外 IO），保留原 three_state 不覆盖。"""
    infra = set((ledger.get("criteria") or {}).get("active_infra") or [])
    rows = []
    for x in ledger.get("entries") or []:
        if x.get("sub") != "B4_归档与镜像":
            continue
        if x.get("name") in infra:
            continue
        rows.append({
            "name": x.get("name"),
            "files": int(x.get("files") or 0),
            "mb": float(x.get("mb") or 0.0),
            "three_state": x.get("three_state") or "SUSPENDED",
            "first_batch": bool(x.get("first_batch")),
        })
    rows.sort(key=lambda r: (-r["mb"], r["name"]))
    return rows


def b4_summary(rows):
    return {
        "count": len(rows),
        "files": sum(r["files"] for r in rows),
        "mb": round(sum(r["mb"] for r in rows), 1),
        "by_state": _count_by(rows, "three_state"),
        "first_batch_true": sorted(r["name"] for r in rows if r["first_batch"]),
    }


def _count_by(rows, key):
    out = {}
    for r in rows:
        k = r.get(key)
        out[k] = out.get(k, 0) + 1
    return out


def check_tiers(t):
    """判据失败面。返回 (ok, problems)。"""
    problems = []
    for k in TIERS:
        want = EXPECT_COUNT[k]
        got = (t.get("count") or {}).get(k)
        if got != want:
            problems.append("criteria_drift: %s expected %s got %s" % (k, want, got))
    if t.get("intersection") != EXPECT_INTERSECTION:
        problems.append("intersection_drift: expected %s got %s"
                        % (EXPECT_INTERSECTION, t.get("intersection")))
    if sorted(t.get("only_in_199") or []) != sorted(EXPECT_ONLY_IN_199):
        problems.append("diff_drift: only_in_199 roster changed")
    if sorted(t.get("only_in_194") or []) != sorted(EXPECT_ONLY_IN_194):
        problems.append("diff_drift: only_in_194 roster changed")
    if t.get("set_sha16") != EXPECT_SET_SHA16:
        problems.append("set_drift: expected %s got %s"
                        % (EXPECT_SET_SHA16, t.get("set_sha16")))
    return (not problems), problems


def check_selftest(s):
    """三层证据失败面。返回 (ok, problems)。"""
    problems = []
    if s.get("total") != SELFTEST_TOTAL:
        problems.append("total_drift: expected %s got %s" % (SELFTEST_TOTAL, s.get("total")))
    if s.get("L1") > s.get("total") or s.get("L2") > s.get("total"):
        problems.append("layer_overclaim: L1/L2 exceeds total")
    if s.get("L3") > s.get("L2"):
        problems.append("l3_overclaim: L3 > L2 (cannot assert without running)")
    if s.get("L3") < SELFTEST_L3_MIN:
        problems.append("l3_shortfall: expected >= %s got %s"
                        % (SELFTEST_L3_MIN, s.get("L3")))
    if s.get("rc_nonzero"):
        problems.append("rc_nonzero: %s" % ",".join(s["rc_nonzero"]))
    if s.get("danger_any"):
        problems.append("danger_calls: %s" % ",".join(s["danger_any"]))
    zero = sorted(s.get("zero_assert") or [])
    if zero and zero != sorted([KNOWN_ZERO_ASSERT]):
        problems.append("unregistered_zero_assert: %s" % ",".join(zero))
    if not zero:
        problems.append("known_exception_missing: expected the Beijing Yaoyi zero-assert instance")
    if s.get("asserts_sum") != ASSERTS_SUM:
        problems.append("asserts_sum_drift: expected %s got %s"
                        % (ASSERTS_SUM, s.get("asserts_sum")))
    return (not problems), problems


def check_b4(rows, authorized=None):
    """B4 闸门失败面：未点单不许进第一批。返回 (ok, problems)。"""
    authorized = dict(authorized or {})
    problems = []
    if len(rows) != B4_COUNT:
        problems.append("b4_count_drift: expected %s got %s" % (B4_COUNT, len(rows)))
    total_files = sum(int(r.get("files") or 0) for r in rows)
    total_mb = round(sum(float(r.get("mb") or 0.0) for r in rows), 1)
    if total_files != B4_FILES:
        problems.append("b4_files_drift: expected %s got %s" % (B4_FILES, total_files))
    if total_mb != B4_MB:
        problems.append("b4_mb_drift: expected %s got %s" % (B4_MB, total_mb))
    for r in rows:
        name = r.get("name")
        st = authorized.get(name, r.get("three_state") or "SUSPENDED")
        if st not in B4_STATES:
            problems.append("illegal_state: %s -> %s" % (name, st))
            continue
        if bool(r.get("first_batch")) and st not in B4_ALLOW_FIRST_BATCH:
            problems.append("unauthorized_touch: %s in first_batch as %s" % (name, st))
    return (not problems), problems


def point_sheet(rows, authorized=None):
    """九行点单表（默认全 SUSPENDED，未点单一行不动）。"""
    authorized = dict(authorized or {})
    out = []
    for r in rows:
        st = authorized.get(r["name"], r.get("three_state") or "SUSPENDED")
        out.append({
            "name": r["name"],
            "files": r["files"],
            "mb": r["mb"],
            "state": st,
            "action": "未点单：不扫描、不搬运" if st == "SUSPENDED"
            else ("已授权：可进作业面（需另行执行）" if st == "AUTHORIZED"
                  else "永久排除：不纳入作业面"),
        })
    return out


def build_report(t, s, b4rows, note=""):
    """把三块证据拼成一份可复算报告（不含时间戳，保证同输入同摘要）。"""
    b4 = b4_summary(b4rows)
    report = {
        "schema": CRITERIA_SCHEMA,
        "version": CRITERIA_VERSION,
        "criteria": {
            "v1": CRITERIA_V1,
            "v68": CRITERIA_V68,
            "union": CRITERIA_UNION,
            "tiers": list(TIERS),
            "tier_label": dict(TIER_LABEL),
            "note": "计数由判据导出；口径一变 set_sha16 立刻红",
        },
        "tiers": {
            "count": dict(t["count"]),
            "intersection": t["intersection"],
            "only_in_199": list(t["only_in_199"]),
            "only_in_194": list(t["only_in_194"]),
            "set_sha16": t["set_sha16"],
        },
        "selftest": {
            "total": s["total"],
            "L1": s["L1"], "L2": s["L2"], "L3": s["L3"],
            "zero_assert": list(s["zero_assert"]),
            "asserts_sum": s["asserts_sum"],
            "asserts_min": s["asserts_min"], "asserts_max": s["asserts_max"],
            "layers": list(SELFTEST_LAYERS),
            "layer_meaning": dict(LAYER_MEANING),
        },
        "b4": {
            "count": b4["count"], "files": b4["files"], "mb": b4["mb"],
            "by_state": b4["by_state"],
            "first_batch_true": b4["first_batch_true"],
            "policy": "九项逐项三态；未点单一律 SUSPENDED；不整包裁决、不重扫",
        },
        "stop_states": {
            "H1_B4": "SUSPENDED",
            "H2_criteria": "RESOLVED",
            "H3_selftest": "RESOLVED",
            "H4_S3": "REMOVED (V69 已完成)",
            "H4_S4": "not_started (本批未启动)",
            "H4_S6": "SUSPENDED (依赖 B3 授权)",
        },
        "note": note,
    }
    report["report_digest"] = digest(report)
    return report


def digest(report):
    """自摘要：对稳定序列化取 sha256 前 16 位（不含本字段）。"""
    payload = {k: v for k, v in report.items() if k != "report_digest"}
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True,
                   separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:16]


def verify_report(report):
    """回执级校验：四失败面 + 自摘要。返回 (ok, problems)。"""
    problems = []
    if report.get("schema") != CRITERIA_SCHEMA:
        problems.append("schema mismatch")
    ok_t, p_t = check_tiers(report.get("tiers") or {})
    ok_s, p_s = check_selftest(report.get("selftest") or {})
    b4 = report.get("b4") or {}
    if b4.get("count") != B4_COUNT:
        problems.append("b4_count_drift in report")
    if report.get("report_digest") != digest(report):
        problems.append("self_digest mismatch (report edited after build)")
    problems.extend(p_t)
    problems.extend(p_s)
    return (not problems), problems
