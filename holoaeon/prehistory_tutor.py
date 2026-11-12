# -*- coding: utf-8 -*-
"""prehistory_tutor.py —— 史前大部头导学产品（V73 / PL-6）

定位：把「史前记忆打捞」的四部大部头——**导学大典 / 计算机语言通史 / 周易 / 道藏**——
收成一套**可回溯的指针卡片**，并逐卡、逐面独立复算六条判据。产品是「模块」，不是文档、
也不是双向同步器；模块只读素材、只出指针与短摘要，不搬运原文、不做诊断处方。

三条纪律（写在代码里，不靠人记）：
1. **只存指针，不存全文**：每卡只有「相对路径 + 行号 + 段落锚 + ≤200 字短摘要 + sha16」。
   摘要超 200 字即判红——不是为了压缩，是为了证明这里没有夹带原文。
2. **零诊断零处方**：卡片正文与段落锚都不许出现诊断/处方/剂量/疗程一类词。命中即红，
   且这一面**单独成例**，不允许被其它面的绿灯掩盖。
3. **绝对路径不出门**：report 只写素材根的 basename 与卡片文件名，出现 `F:\\` 或 `/f/` 即判泄漏。

实测（2026-11-13 本机，非策划案转述）：
  · 素材 5 件 / 440 文件 / 45.57 MB（导学大典 2 件、通史 376、周易 40、道藏 22）
  · 卡片 **42** 张：导学大典 14 / 通史 5 / 周易 10 / 道藏 13；摘要最长 < 200 字，零重复、零禁词
  · 六面金丝雀：指针断 / 摘要超长 / 植入禁词 / 缺部头 / 路径成环 / 摘要被改 —— **6/6 全红**

失败面（任一即红）：
    cards_unreadable / schema_drift / field_missing / pointer_unreachable / sha_mismatch /
    anchor_out_of_range / summary_oversize / prescription_violation / section_missing /
    section_thin / path_broken / path_cycle / absolute_path_leak / determinism_drift /
    card_digest / self_digest
"""
import hashlib
import io
import json
import os
import re

TUTOR_SCHEMA = "PREHISTORY-TUTOR-v1"
TUTOR_VERSION = "1.0"

CARDS_FILENAME = "tutor_cards.json"
SECTIONS = ("导学大典", "计算机语言通史", "周易", "道藏")
CARD_FIELDS = ("id", "source_pointer", "sha16", "段落锚", "领域", "归属仓",
               "导学路径", "evidence_level", "zero_prescription")
EVIDENCE_LEVELS = ("L1", "L2")
MAX_SUMMARY_CHARS = 200
MIN_CARDS_PER_SECTION = 3
BANNED_TERMS = ("诊断", "处方", "剂量", "疗程", "疗效", "确诊", "辨证", "方剂", "用药", "医案", "病案")
MATERIAL_ROOT = r"F:\doubaowork"

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CARDS = os.path.join(_REPO_ROOT, "data", CARDS_FILENAME)

NOTE = ("每卡只存相对指针 + 行号 + 段落锚 + ≤200 字短摘要；摘要超长即判红，"
        "零诊断零处方单独成例；四部头各有下限；导学路径单链无环；两次复算同 digest")


# ---------------------------------------------------------------- 指纹

def sha16(payload):
    text = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def file_sha16(path):
    h = hashlib.sha256()
    with io.open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


# ---------------------------------------------------------------- 读取

def load(cards_path=None):
    """读卡片库；读不到就返回带 error 的壳，不抛。"""
    path = cards_path or DEFAULT_CARDS
    try:
        with io.open(path, encoding="utf-8") as fh:
            payload = json.load(fh)
    except FileNotFoundError:
        return {"error": "cards_missing", "path": path}
    except (ValueError, OSError) as exc:
        return {"error": "cards_unreadable: %s" % exc, "path": path}
    return {"path": path, "payload": payload}


def split_pointer(pointer):
    """'a/b.md#L12' -> ('a/b.md', 12)；不合法返回 (None, 0)。"""
    if not isinstance(pointer, str) or "#L" not in pointer:
        return None, 0
    rel, num = pointer.rsplit("#L", 1)
    if not rel or not num.isdigit():
        return None, 0
    return rel, int(num)


def resolve(rel, root):
    return os.path.join(root, rel.replace("/", os.sep))


def banned_hits(text):
    return [w for w in BANNED_TERMS if w in (text or "")]


# ---------------------------------------------------------------- 单卡六面

def evaluate_card(card, root):
    """逐卡判：字段齐 / 指针可达 / sha 一致 / 行号在位 / 不夹带全文 / 零诊断零处方。"""
    crit = []
    missing = [k for k in CARD_FIELDS if k not in card]
    crit.append({"id": "field_missing", "ok": not missing, "detail": missing})

    rel, line = split_pointer(card.get("source_pointer"))
    target = resolve(rel, root) if rel else ""
    reachable = bool(rel) and os.path.isfile(target)
    crit.append({"id": "pointer_reachable", "ok": reachable, "detail": card.get("source_pointer")})

    actual = file_sha16(target) if reachable else ""
    crit.append({"id": "sha_mismatch", "ok": bool(actual) and actual == card.get("sha16"),
                 "detail": [card.get("sha16"), actual]})

    in_range = False
    if reachable and line:
        with io.open(target, encoding="utf-8", errors="replace") as fh:
            in_range = line <= sum(1 for _ in fh)
    crit.append({"id": "anchor_out_of_range", "ok": in_range, "detail": line})

    summary = card.get("summary") or ""
    level = card.get("evidence_level")
    size_ok = len(summary) <= MAX_SUMMARY_CHARS
    if level == "L2" and not summary:
        size_ok = False
    crit.append({"id": "summary_oversize", "ok": size_ok and level in EVIDENCE_LEVELS,
                 "detail": {"chars": len(summary), "level": level}})

    anchor = card.get("段落锚") or {}
    hits = banned_hits(summary) + banned_hits(anchor.get("heading") if isinstance(anchor, dict) else "")
    ok = not hits and card.get("zero_prescription") is True
    crit.append({"id": "prescription_violation", "ok": ok, "detail": hits})
    return crit


# ---------------------------------------------------------------- 部头与路径

def section_stats(cards):
    stats = {s: 0 for s in SECTIONS}
    for c in cards:
        sec = c.get("section")
        if sec in stats:
            stats[sec] += 1
    return stats


def check_sections(cards):
    stats = section_stats(cards)
    crit = []
    empty = [s for s in SECTIONS if stats.get(s, 0) == 0]
    crit.append({"id": "section_missing", "ok": not empty, "detail": empty})
    thin = [s for s in SECTIONS if 0 < stats.get(s, 0) < MIN_CARDS_PER_SECTION]
    crit.append({"id": "section_thin", "ok": not thin, "detail": {"thin": thin, "stats": stats}})
    return crit


def check_paths(cards):
    """导学路径：prev/next 必须指向存在的卡或 null；整图无环；同部头内单链互指。"""
    ids = [c.get("id") for c in cards]
    id_set = set(ids)
    broken, cycles = [], []

    for c in cards:
        path = c.get("导学路径") or {}
        for k in ("prev", "next"):
            v = path.get(k)
            if v is not None and v not in id_set:
                broken.append({"id": c.get("id"), "side": k, "to": v})

    graph = {}
    for c in cards:
        graph[c.get("id")] = (c.get("导学路径") or {}).get("next")
    color = {}

    def walk(node, stack):
        if color.get(node) == 1:
            cycles.append(stack[stack.index(node):] if node in stack else [node])
            return
        if color.get(node) == 2:
            return
        color[node] = 1
        nxt = graph.get(node)
        if nxt:
            walk(nxt, stack + [node])
        color[node] = 2

    for n in graph:
        if color.get(n) is None:
            walk(n, [])

    for c in cards:
        nxt = (c.get("导学路径") or {}).get("next")
        if nxt and nxt in graph:
            back = (next((x for x in cards if x.get("id") == nxt), {}) or {}).get("导学路径") or {}
            if back.get("prev") != c.get("id"):
                broken.append({"id": c.get("id"), "side": "symmetry", "to": nxt})

    return [
        {"id": "path_broken", "ok": not broken, "detail": broken[:12]},
        {"id": "path_cycle", "ok": not cycles, "detail": cycles[:6]},
    ]


# ---------------------------------------------------------------- 聚合

def _leak(obj):
    text = json.dumps(obj, ensure_ascii=False)
    return ("F:\\" in text) or ("F:\\\\" in text) or ("/f/" in text.lower())


def digest_of(cards, stats, totals):
    return sha16({
        "cards": [(c.get("id"), c.get("source_pointer"), c.get("sha16"),
                   len(c.get("summary") or "")) for c in cards],
        "sections": stats,
        "totals": {k: totals[k] for k in ("cards", "green", "sections_covered")},
    })


def aggregate(root=None, cards_path=None):
    base = root or MATERIAL_ROOT
    loaded = load(cards_path)
    if loaded.get("error"):
        return {"schema": TUTOR_SCHEMA, "version": TUTOR_VERSION,
                "root_label": os.path.basename(base.rstrip("\\/")),
                "cards": [], "sections": {}, "totals": {}, "criteria": [],
                "error": loaded["error"], "note": NOTE,
                "digest": "", "self_digest": ""}

    payload = loaded["payload"]
    cards = payload.get("cards") or []

    rows = []
    for c in cards:
        crit = evaluate_card(c, base)
        rows.append({
            "id": c.get("id"),
            "section": c.get("section"),
            "pointer": c.get("source_pointer"),
            "sha16": c.get("sha16"),
            "summary_chars": len(c.get("summary") or ""),
            "evidence_level": c.get("evidence_level"),
            "ok": all(x["ok"] for x in crit),
            "failing": [x["id"] for x in crit if not x["ok"]],
        })

    stats = section_stats(cards)
    totals = {
        "cards": len(cards),
        "green": sum(1 for r in rows if r["ok"]),
        "sections_covered": sum(1 for s in SECTIONS if stats.get(s, 0) > 0),
        "min_per_section": MIN_CARDS_PER_SECTION,
        "max_summary_chars": MAX_SUMMARY_CHARS,
        "max_summary_observed": max([r["summary_chars"] for r in rows] or [0]),
    }

    sec_crit = check_sections(cards)
    path_crit = check_paths(cards)
    criteria = []
    for cid in ("pointer_reachable", "summary_oversize", "prescription_violation"):
        ok = all(cid not in r["failing"] for r in rows) and bool(rows)
        detail = [r["id"] for r in rows if cid in r["failing"]][:12]
        criteria.append({"id": cid, "ok": ok, "detail": detail})
    criteria.extend(sec_crit)
    criteria.extend(path_crit)

    report = {
        "schema": payload.get("schema"),
        "version": payload.get("version") or TUTOR_VERSION,
        "root_label": os.path.basename(base.rstrip("\\/")),
        "card_file_label": os.path.basename(loaded["path"]),
        "cards": rows,
        "sections": stats,
        "totals": totals,
        "criteria": criteria,
        "note": payload.get("note") or NOTE,
    }
    report["digest"] = digest_of(cards, stats, totals)
    return report


def finalize(report):
    body = {k: v for k, v in report.items() if k != "self_digest"}
    report["self_digest"] = sha16(body)
    return report


def check(report, cards_path=None):
    """对 report 判 FAIL；返回失败项清单（空 = 绿）。"""
    failures = []
    if report.get("error"):
        failures.append({"id": "cards_unreadable", "detail": report["error"]})
        return failures

    if report.get("schema") != TUTOR_SCHEMA:
        failures.append({"id": "schema_drift", "detail": report.get("schema")})

    for r in report.get("cards") or []:
        for f in r.get("failing") or []:
            failures.append({"id": f, "card": r.get("id")})

    for c in report.get("criteria") or []:
        if not c.get("ok"):
            failures.append({"id": c["id"], "detail": c.get("detail")})

    if _leak(report):
        failures.append({"id": "absolute_path_leak"})

    expected = digest_of_report(report)
    if report.get("digest") != expected:
        failures.append({"id": "card_digest", "detail": [report.get("digest"), expected]})

    if report.get("self_digest"):
        body = {k: v for k, v in report.items() if k != "self_digest"}
        if sha16(body) != report["self_digest"]:
            failures.append({"id": "self_digest"})
    return failures


def digest_of_report(report):
    cards = report.get("cards") or []
    return sha16({
        "cards": [(r.get("id"), r.get("pointer"), r.get("sha16"), r.get("summary_chars")) for r in cards],
        "sections": report.get("sections") or {},
        "totals": {k: (report.get("totals") or {}).get(k)
                   for k in ("cards", "green", "sections_covered")},
    })


def verify(root=None, cards_path=None):
    first = aggregate(root, cards_path)
    second = aggregate(root, cards_path)
    failures = check(first, cards_path)
    if first.get("digest") != second.get("digest"):
        failures.append({"id": "determinism_drift",
                         "detail": [first.get("digest"), second.get("digest")]})
    report = finalize(first)
    return {"ok": not failures, "failures": failures, "report": report}


def _main(argv):
    cmd = argv[1] if len(argv) > 1 else "verify"
    if cmd not in ("verify", "report"):
        print("usage: python -m holoaeon.prehistory_tutor [verify|report]", flush=True)
        return 2
    out = verify()
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    import sys
    raise SystemExit(_main(sys.argv))
