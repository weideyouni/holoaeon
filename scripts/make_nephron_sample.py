# -*- coding: utf-8 -*-
"""生成 NEPHRON P0 的黄金样例：示例账本 JSONL + 回放报告 Markdown
================================================================================
用途：给贡献者一份"能被回放器真正吃下去"的最小账本，用来验证字段是否够用。
      所有内容由 `holoaeon.packs.nephron_pack` 的纯函数产出，不手写、不臆造。
运行：python scripts/make_nephron_sample.py
产出：examples/nephron_ledger_sample.jsonl
      examples/nephron_replay_report.md
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from holoaeon.packs import nephron_pack as npk

OUT_DIR = os.path.join(ROOT, "examples")
FP = npk.skill_nephron_generation_fingerprint(
    {"weights": "llama-7b-q4", "templates": "tmpl-v4", "quantization": "q4_k_m",
     "loras": ["lora-med", "lora-code"], "retriever": "bge-m3-v1.5"})["fingerprint"]


def _ev(t, code, refs, **delta):
    return {"type": t, "reason_code": code, "refs": list(refs), "delta": delta}


def build_ledger() -> list:
    recs = [
        {"tick": 0, "seq": 0, "window_budget": 8, "window_used": 4,
         "layer_residency": {"working": 2, "hebbian": 1, "skeleton": 1, "external": 0},
         "hit_rate": None, "compression_ratio": None, "evicted_pages": 0,
         "external_calls": 0, "cost_estimate": 0.0, "confidence_estimate": None,
         "events": [_ev("window_build", "WINDOW_BUILD_COMPLETE", []),
                    _ev("page_admit", "ADMIT_RECENT", ["p-100"], score=0.62),
                    _ev("page_admit", "ADMIT_RECENT", ["p-101"], score=0.58),
                    _ev("page_admit", "ADMIT_LINEAGE_TRUSTED", ["p-102"], score=0.51),
                    _ev("page_admit", "ADMIT_HIGH_RELEVANCE", ["p-103"], score=0.77),
                    _ev("page_reject", "REJECT_REDUNDANT", ["p-104"]),
                    _ev("layer_miss", "LAYER_MISS_ALL", [])],
         "fingerprint": FP},
        {"tick": 1, "seq": 1, "window_budget": 8, "window_used": 4,
         "layer_residency": {"working": 1, "hebbian": 2, "skeleton": 1, "external": 0},
         "hit_rate": 0.5, "compression_ratio": None, "evicted_pages": 0,
         "external_calls": 0, "cost_estimate": 0.1, "confidence_estimate": 0.8,
         "events": [_ev("window_build", "WINDOW_BUILD_COMPLETE", []),
                    _ev("layer_hit", "LAYER_HIT_DEEP", ["p-102"]),
                    _ev("page_admit", "ADMIT_RECENT", ["p-101"], score=0.60),
                    _ev("page_admit", "ADMIT_LINEAGE_TRUSTED", ["p-102"], score=0.55),
                    _ev("page_admit", "ADMIT_RECENT", ["p-105"], score=0.49),
                    _ev("page_admit", "ADMIT_HIGH_RELEVANCE", ["p-103"], score=0.74),
                    _ev("page_reject", "REJECT_STALE_FINGERPRINT", ["p-106"])],
         "fingerprint": FP},
        {"tick": 2, "seq": 2, "window_budget": 8, "window_used": 3,
         "layer_residency": {"working": 1, "hebbian": 1, "skeleton": 1, "external": 0},
         "hit_rate": 0.66, "compression_ratio": None, "evicted_pages": 0,
         "external_calls": 1, "cost_estimate": 0.3, "confidence_estimate": 0.7,
         "events": [_ev("window_build", "WINDOW_BUILD_COMPLETE", []),
                    _ev("retrieval", "RETRIEVAL_DEEP_TAX", ["p-107"], ms=420, tax=0.15),
                    _ev("page_summarize", "SUMM_BUDGET_PRESSURE", ["p-100"],
                        from_len=900, to_len=120),
                    _ev("page_admit", "ADMIT_LINEAGE_TRUSTED", ["p-102"], score=0.58),
                    _ev("page_admit", "ADMIT_RECENT", ["p-101"], score=0.57),
                    _ev("page_admit", "ADMIT_HIGH_RELEVANCE", ["p-107"], score=0.71),
                    _ev("page_reject", "REJECT_BUDGET_EXCEEDED", ["p-105"])],
         "fingerprint": FP},
        {"tick": 3, "seq": 3, "window_budget": 8, "window_used": 4,
         "layer_residency": {"working": 2, "hebbian": 1, "skeleton": 1, "external": 0},
         "hit_rate": 0.5, "compression_ratio": None, "evicted_pages": 0,
         "external_calls": 0, "cost_estimate": 0.1, "confidence_estimate": 0.75,
         "events": [_ev("window_build", "WINDOW_BUILD_COMPLETE", []),
                    _ev("page_admit", "ADMIT_RECENT", ["p-101"], score=0.59),
                    _ev("page_admit", "ADMIT_LINEAGE_TRUSTED", ["p-102"], score=0.60),
                    _ev("page_admit", "ADMIT_HIGH_RELEVANCE", ["p-107"], score=0.69),
                    _ev("page_admit", "ADMIT_RECENT", ["p-108"], score=0.44),
                    _ev("page_reject", "REJECT_NO_LINEAGE", ["p-109"])],
         "fingerprint": FP},
        {"tick": 4, "seq": 4, "window_budget": 8, "window_used": 3,
         "layer_residency": {"working": 1, "hebbian": 1, "skeleton": 1, "external": 0},
         "hit_rate": 0.75, "compression_ratio": None, "evicted_pages": 0,
         "external_calls": 0, "cost_estimate": 0.05, "confidence_estimate": 0.82,
         "events": [_ev("window_build", "WINDOW_BUILD_COMPLETE", []),
                    _ev("layer_hit", "LAYER_HIT_SHALLOW", ["p-101"]),
                    _ev("page_admit", "ADMIT_LINEAGE_TRUSTED", ["p-102"], score=0.61),
                    _ev("page_admit", "ADMIT_HIGH_RELEVANCE", ["p-107"], score=0.66),
                    _ev("page_admit", "ADMIT_RECENT", ["p-101"], score=0.58)],
         "fingerprint": FP},
        {"tick": 5, "seq": 5, "window_budget": 8, "window_used": 2,
         "layer_residency": {"working": 1, "hebbian": 0, "skeleton": 1, "external": 0},
         "hit_rate": None, "compression_ratio": None, "evicted_pages": 0,
         "external_calls": 0, "cost_estimate": 0.0, "confidence_estimate": 0.6,
         "events": [_ev("window_build", "WINDOW_BUILD_COMPLETE", []),
                    _ev("page_admit", "ADMIT_LINEAGE_TRUSTED", ["p-102"], score=0.63),
                    _ev("page_admit", "ADMIT_HIGH_RELEVANCE", ["p-107"], score=0.70),
                    _ev("degradation", "DEGRADE_CONFIDENCE_FLOOR", ["p-110"],
                        floor=0.6, actual=0.52),
                    _ev("page_reject", "REJECT_TRUST_RADIUS", ["p-111"])],
         "fingerprint": FP},
    ]
    # 末尾放一条"换代际"的记录，用来演示指纹失配必须留痕（A7）
    rec6 = {"tick": 6, "seq": 6, "window_budget": 8, "window_used": 1,
            "layer_residency": {"working": 1, "hebbian": 0, "skeleton": 0, "external": 0},
            "hit_rate": None, "compression_ratio": None, "evicted_pages": 0,
            "external_calls": 0, "cost_estimate": 0.0, "confidence_estimate": None,
            "events": [_ev("window_build", "WINDOW_BUILD_COMPLETE", []),
                       _ev("fingerprint_mismatch", "FINGERPRINT_MISMATCH_STALE", ["p-102"]),
                       _ev("page_reject", "REJECT_STALE_FINGERPRINT", ["p-102"])],
            "fingerprint": "0000DEADBEEF0000"}
    recs.append(rec6)
    return recs


def build_slot_snapshots() -> list:
    def slot(sid, cls, occ, tick, frag, owner, rec):
        return {"slot_id": sid, "slot_class": cls, "occupant_page": occ,
                "allocated_tick": tick, "fragment_flag": frag,
                "owner_symbiont": owner, "reclaimability": rec}
    return [
        {"tick": 0, "entries": [slot("s-001", "trunk", "p-102", 0, False, None, "cold"),
                                slot("s-002", "trunk", "p-101", 0, False, None, "warm"),
                                slot("s-050", "reserve", None, 0, False, None, "hot")]},
        {"tick": 4, "entries": [slot("s-001", "trunk", "p-102", 0, False, None, "cold"),
                                slot("s-002", "trunk", "p-107", 2, False, "m-retrieval", "warm"),
                                slot("s-003", "trunk", None, 0, True, None, "hot"),
                                slot("s-050", "reserve", None, 0, False, None, "hot")]},
    ]


def build_report(ledger: list, snaps: list) -> str:
    verify = npk.skill_nephron_ledger_verify(ledger)
    det = npk.skill_nephron_replay_determinism(ledger)
    acc = npk.skill_nephron_acceptance_check()
    fields = npk.skill_nephron_field_dictionary()
    lines = []
    A = lines.append
    A("# NEPHRON P0 回放报告（黄金样例）")
    A("")
    A("> 本报告由 `python scripts/make_nephron_sample.py` 生成，"
      "内容全部来自 `holoaeon.packs.nephron_pack` 的纯函数；不是手写样张。")
    A("")
    A("## 1. 账本概况")
    A("")
    A("| 项 | 值 |")
    A("|---|---|")
    A("| 记录数 | %d |" % verify["count"])
    A("| tick 区间 | 0 – %d |" % max(r["tick"] for r in ledger))
    A("| 链摘要 | `%s` |" % verify["chain_digest"])
    A("| 只追加核验 | %s |" % ("通过（seq 单调 / 主键唯一 / 无缺口 / tick 不倒退）"
                                     if verify["ok"] else "不通过：" + str(verify["checks"])))
    A("| 代际指纹 | `%s`（tick 0–5 同代际，tick 6 故意换代际） |" % FP)
    A("| 字段字典条目 | %d（与结构定义一致：%s） |"
      % (fields["count"], fields["match_schema"]))
    A("| 回放确定性 | %s（`%s` == `%s`） |"
      % ("通过" if det["stable"] else "不通过", det["hash_1"], det["hash_2"]))
    A("")
    A("## 2. 逐 tick 窗口构成表")
    A("")
    for t in sorted({r["tick"] for r in ledger}):
        w = npk.skill_nephron_replay_window(ledger, t, "full")
        m = w["manifest"]
        inp = npk.skill_nephron_replay_inputs(ledger, t)
        A("### tick %d" % t)
        A("")
        A("| 进（page_id / score / 理由码） | 摘要（page_id / from→to / 理由码） | 拒（page_id / 理由码） |")
        A("|---|---|---|")
        adm = "<br>".join("%s / %.2f / `%s`" % (a["page_id"], a["score"], a["reason_code"])
                          for a in m["admitted"]) or "—"
        sm = "<br>".join("%s / %d→%d / `%s`" % (s["page_id"], s["from_len"], s["to_len"],
                                                s["reason_code"]) for s in m["summarized"]) or "—"
        rj = "<br>".join("%s / `%s`" % (r["page_id"], r["reason_code"])
                         for r in m["rejected"]) or "—"
        A("| %s | %s | %s |" % (adm, sm, rj))
        A("")
        A("决策输入：预算 %d → 使用 %d；四层驻留 %s；命中率 %s；代价 %s；置信度 %s。"
          % (inp["window_budget"], inp["window_used"],
             "/".join("%s=%d" % (kk, inp["layer_residency"].get(kk, 0))
                      for kk in ("working", "hebbian", "skeleton", "external")),
             "null（本 tick 无检索）" if inp["hit_rate"] is None else inp["hit_rate"],
             inp["cost_estimate"],
             "null" if inp["confidence_estimate"] is None else inp["confidence_estimate"]))
        A("")
    A("## 3. 变更时间线（相邻 tick 差异）")
    A("")
    tl = npk.skill_nephron_replay_timeline(ledger, 0, 99)
    A("| tick | 进入 | 离开 | 拒绝数 | 指纹失配 | 代际变更 |")
    A("|---|---|---|---|---|---|")
    for i, row in enumerate(tl["rows"]):
        ent = "、".join(row.get("entered", []))
        if not ent:
            ent = "（首帧）" if i == 0 else "—"
        A("| %d | %s | %s | %d | %d | %s |"
          % (row["tick"], ent,
             "、".join(row.get("left", [])) or "—", row["rejected"],
             row["fingerprint_mismatch"],
             "是" if row.get("fingerprint_changed") else "否"))
    A("")
    A("## 4. 槽位快照（最近快照 ≤ tick）")
    A("")
    A("| 查询 tick | 快照 tick | 年龄 | 陈旧 | 条目数 | 说明 |")
    A("|---|---|---|---|---|---|")
    for t in (2, 6, 40):
        sl = npk.skill_nephron_replay_slots(snaps, t)
        if sl["available"]:
            A("| %d | %d | %d | %s | %d | `replay_scope=%s`（P0 不重演槽位变化） |"
              % (t, sl["snapshot_tick"], sl["age_ticks"],
                 "是" if sl["stale"] else "否", len(sl["entries"]), sl["replay_scope"]))
        else:
            A("| %d | — | — | — | 0 | 无快照：%s |" % (t, sl["reason"]))
    A("")
    A("## 5. 验收状态（A1–A8）")
    A("")
    A("| 编号 | 结论 | 本包能否自证 | 状态 |")
    A("|---|---|---|---|")
    for r in acc["rows"]:
        A("| %s | %s | %s | `%s` |" % (r["id"], r["claim"], r["pack_can_prove"], r["status"]))
    A("")
    A("待人工实测：%s；总判定 `%s`。" % ("、".join(acc["pending"]) or "无", acc["verdict"]))
    A("")
    A("---")
    A("")
    A("潮起开门，潮落闭嘴。")
    return "\n".join(lines) + "\n"


def main() -> None:
    ledger = build_ledger()
    snaps = build_slot_snapshots()
    jl = os.path.join(OUT_DIR, "nephron_ledger_sample.jsonl")
    rp = os.path.join(OUT_DIR, "nephron_replay_report.md")
    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)
    with open(jl, "w", encoding="utf-8", newline="\n") as fh:
        for r in ledger:
            fh.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
    with open(rp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(build_report(ledger, snaps))
    v = npk.skill_nephron_ledger_verify(ledger)
    print("ledger:", jl, "records=%d" % v["count"], "verify_ok=%s" % v["ok"])
    print("report:", rp)


if __name__ == "__main__":
    main()
