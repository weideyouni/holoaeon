# -*- coding: utf-8 -*-
"""
meridian_recheck —— D03 经络维 214 格 pending-evidence 复核（V64 · 挂账清零批）
================================================================================
挂账原文（V62 台账 data/searchnet_d03_meridian.json）：
  250 格（10 碎片 × 25 机制）= linked 13 / pending-evidence 214 / unlinked 23。
  pending 格的 evidence 是空数组——「没有证据」是如实登记，不是缺陷掩盖。

本批要关的是什么：
  把 214 格从「空了证据位」变成「有判定 + 有证据位说明」——
  判据来自**仓内真实落盘的碎片描述**（data/d03_fragment_essence.json，源自
  V60 打捞回执的 official_desc 原文），而不是凭印象写字。

判定规则（全程可复算）：
  · 文本面 = repo + official_desc + essence + language + leg（统一小写）；
  · 每机制一套判定词（MATCH_VOCAB，**人工映射的复核用词表**，不是官方定义）；
  · 命中 ≥1 词 → linked（evidence 记命中词与命中片段，可逐条复核）；
  · 零命中 → unlinked（evidence 记「文本面无命中」——这也是结论，不是空位）；
  · V62 原有 linked 13 格**保留原证据不推翻**（state 保持 linked，origin=V62）。

为什么不是「全部强行 linked」：那会把「没证据」伪装成「有证据」。
本批的诚实目标是 **pending = 0**（每格都有判定与证据位说明），
而不是 linked 数好看。

产物：data/searchnet_d03_meridian_recheck.json（新台账，原台账不动，
保持 V62 历史可复算）。
"""
from __future__ import annotations

import io
import json
import os
from typing import Any, Dict, List, Optional

SEAL = "潮起开门，潮落闭嘴"
SCHEMA_VERSION = "MERIDIAN-RECHECK-v1.0"
SRC_LEDGER = os.path.join("data", "searchnet_d03_meridian.json")
EVIDENCE_SRC = os.path.join("data", "d03_fragment_essence.json")
OUT_LEDGER = "searchnet_d03_meridian_recheck.json"

# 25 机制判定词（人工映射的「复核用词表」——用于文本面命中判定，非机制官方定义）
MATCH_VOCAB: Dict[str, List[str]] = {
    "A1": ["holograph", "全息", "holistic"],
    "A2": ["interconnect", "万物互联", "ecosystem", "everything"],
    "X1": ["matrix", "matrix-based", "1331", "grid", "大规模矩阵"],
    "X2": ["resonance", "共振", "active node", "108641", "scale"],
    "M01": ["heartbeat", "心跳", "health check", "pulse", "uptime", "monitor"],
    "M02": ["skeleton", "细胞骨架", "backbone", "core engine", "主干"],
    "M03": ["skin", "皮肤", "adapter", "plugin", "interface", "sdk"],
    "M04": ["pipeline", "channel", "stream", "bus", "topics", "partition"],
    "M05": ["hebbian", "赫布", "collaborat", "crew", "cooperat", "multi-agent", "role-playing"],
    "M06": ["semantic", "语义", "message", "protocol", "event streaming", "agent protocol"],
    "M07": ["similarity", "相似", "similar", "cluster", "embedding", "vector", "rag"],
    "M08": ["runtime", "execution", "engine", "orchestrat", "运行"],
    "M09": ["graph", "dag", "workflow", "flow", "node"],
    "M10": ["society", "swarm", "群体", "social", "community", "agents"],
    "M11": ["federation", "governance", "tenant", "城邦", "multi-tenant", "govern"],
    "C1": ["dissipat", "耗散", "entropy", "self-organ", "自组织"],
    "C2": ["hallucination", "幻觉", "grounding", "retrieval", "knowledge-based", "rag"],
    "R1": ["resonance", "共振", "node"],
    "R2": ["fanout", "fan-out", "mandala", "曼陀罗", "broadcast", "expand"],
    "R3": ["mobius", "莫比乌斯", "feedback", "loop", "cycle"],
    "R4": ["klein", "克莱因", "converg", "收敛", "bottleneck"],
    "R5": ["kalman", "卡尔曼", "filter", "state estimat", "estimation"],
    "R6": ["bayes", "贝叶斯", "probabilis", "posterior", "prior"],
    "R7": ["hilbert", "希尔伯特", "vector space", "embedding space", "high-dimension"],
    "R8": ["dissipat", "耗散", "entropy", "metric", "observability", "度量"],
}

VOCAB_DISCLAIMER = ("MATCH_VOCAB 是本批人工映射的复核用词表，用于在碎片文本面做确定性命中判定；"
                    "它不是各机制的官方定义，命中也不等于「该仓库实现了该机制」——"
                    "证据等级如实标为 desc_keyword（描述关键词级）。")


def _load_ledger(root: str) -> Dict[str, Any]:
    with io.open(os.path.join(root, SRC_LEDGER), encoding="utf-8") as f:
        return json.load(f)


def _load_evidence(root: str) -> Dict[str, Dict[str, Any]]:
    with io.open(os.path.join(root, EVIDENCE_SRC), encoding="utf-8") as f:
        data = json.load(f)
    return {r["repo"]: r for r in data["rows"]}


def _text_of(frag: Dict[str, Any]) -> str:
    parts = [frag.get("repo") or "", frag.get("official_desc") or "", frag.get("essence") or "",
             frag.get("language") or "", frag.get("leg") or ""]
    return " ".join(parts).lower()


def _match(mech: str, text: str) -> List[str]:
    vocab = MATCH_VOCAB.get(mech) or []
    return [w for w in vocab if w.lower() in text]


def recheck(root: Optional[str] = None) -> Dict[str, Any]:
    """250 格逐格复核：pending-evidence → linked / unlinked（两态，无 pending）。"""
    root = root or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src = _load_ledger(root)
    frags = _load_evidence(root)
    cells_in: List[Dict[str, Any]] = src.get("table") or []
    if not isinstance(cells_in, list):
        cells_in = []
        problems.append("源台账 table 字段不是列表")
    problems: List[str] = []
    out_cells: List[Dict[str, Any]] = []
    counts = {"linked": 0, "unlinked": 0, "pending_original": 0, "kept_v62": 0}

    for c in cells_in:
        repo = c.get("repo")
        mech = c.get("mech")
        state0 = c.get("state")
        if state0 == "pending-evidence":
            counts["pending_original"] += 1
        if repo not in frags:
            problems.append("碎片不在证据源：{}".format(repo))
            frag = {"official_desc": "", "essence": "", "language": "", "leg": ""}
        else:
            frag = frags[repo]
        # ① V62 原有 linked 且带证据 → 保留不推翻
        if state0 == "linked" and (c.get("evidence") or []):
            counts["kept_v62"] += 1
            counts["linked"] += 1
            out_cells.append({**c, "state": "linked", "origin": "V62",
                              "evidence_kind": "v62_original"})
            continue
        # ② 其余（pending / 无证据 linked / unlinked）→ 按文本面重算
        text = _text_of(frag)
        hits = _match(mech, text) if mech else []
        if hits:
            counts["linked"] += 1
            snippet = (frag.get("official_desc") or frag.get("essence") or "")[:120]
            out_cells.append({
                **c, "state": "linked", "origin": "V64-RECHECK",
                "evidence_kind": "desc_keyword",
                "evidence": [{"kind": "desc_keyword", "hits": hits, "snippet": snippet,
                              "source": "data/d03_fragment_essence.json（V60 打捞回执 official_desc）"}],
            })
        else:
            counts["unlinked"] += 1
            out_cells.append({
                **c, "state": "unlinked", "origin": "V64-RECHECK",
                "evidence_kind": "no_hit",
                "evidence": [],
                "note": "碎片文本面（repo/official_desc/essence/language/leg）对本机制判定词零命中——"
                        "判定为未链接，不是空证据位",
            })

    pending_after = sum(1 for c in out_cells if c.get("state") == "pending-evidence")
    if pending_after != 0:
        problems.append("复核后仍有 pending-evidence：{}".format(pending_after))
    if len(out_cells) != len(cells_in):
        problems.append("格数变化：{} → {}".format(len(cells_in), len(out_cells)))

    by_mech: Dict[str, Dict[str, int]] = {}
    for c in out_cells:
        m = c.get("mech")
        d = by_mech.setdefault(m, {"linked": 0, "unlinked": 0})
        d["linked" if c["state"] == "linked" else "unlinked"] += 1

    return {
        "schema": SCHEMA_VERSION,
        "batch": "V64-HANGOVER-ZERO",
        "dom": "D03 经络维 214 格 pending-evidence 复核",
        "source_ledger": SRC_LEDGER.replace(os.sep, "/"),
        "evidence_source": EVIDENCE_SRC.replace(os.sep, "/"),
        "cells": len(out_cells),
        "summary": {
            **counts,
            "pending_after": pending_after,
            "by_state": {"linked": counts["linked"], "unlinked": counts["unlinked"]},
            "by_mechanism": by_mech,
        },
        "vocab_disclaimer": VOCAB_DISCLAIMER,
        "problems": problems,
        "verdict": "PASS" if not problems else "FAIL",
        "cells_detail": out_cells,
        "seal": SEAL,
    }


def write_ledger(path: Optional[str] = None) -> str:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = path or os.path.join(root, "data", OUT_LEDGER)
    rep = recheck(root)
    payload = {k: v for k, v in rep.items() if k != "cells_detail"}
    payload["cells"] = rep["cells_detail"]
    io.open(out, "w", encoding="utf-8", newline="\n").write(
        json.dumps(payload, ensure_ascii=False, indent=1) + "\n")
    return out


def main(argv: Optional[List[str]] = None) -> int:
    import sys
    argv = list(argv if argv is not None else sys.argv[1:])
    if not argv:
        print("用法：python -m holoaeon.meridian_recheck check | ledger")
        return 1
    if argv[0] == "check":
        rep = recheck()
        print(json.dumps({k: v for k, v in rep.items() if k != "cells_detail"},
                         ensure_ascii=False, indent=1))
        return 0 if rep["verdict"] == "PASS" else 1
    if argv[0] == "ledger":
        print("台账已写：{}".format(write_ledger()))
        return 0
    print("未知命令：{}".format(argv[0]))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
