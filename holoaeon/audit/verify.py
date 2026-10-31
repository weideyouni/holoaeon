# -*- coding: utf-8 -*-
"""
VERAX · 复现验证器（verify）
================================================================================
用 n 个全新内核喂同一任务，比对 ReproHash；可选与 golden 冻结值比对。
只读观测：不改内核行为，不写内核状态。

保护哪条立身原则：确定性（同逻辑必得同哈希）、可审计（每次判定留差异表）。
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from .fields import canonicalize, canonical_json, reprohash, split_physical

GOLDEN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "golden")


# ------------------------------------------------------------ 内核工厂
def build_kernel(packs: Optional[List[str]] = None):
    """造一个装齐领域包的全新内核（冷插拔）。"""
    from ..kernel import Kernel
    from ..packs import PACK_ORDER, get_pack

    kernel = Kernel()
    for key in (packs if packs is not None else PACK_ORDER):
        get_pack(key).install(kernel)
    return kernel


def run_task(task: str, args: Optional[Dict[str, Any]] = None,
             to: Any = None, packs: Optional[List[str]] = None) -> Dict[str, Any]:
    """在全新内核上执行一次任务，返回原回执（不改动）。"""
    return build_kernel(packs).submit(task, to=to, args=args)


# ------------------------------------------------------------ golden
def load_golden(task_or_file: str) -> Optional[Dict[str, Any]]:
    """按 task_id 读取 golden/*.json；不存在返回 None。"""
    if os.path.isfile(task_or_file):
        path = task_or_file
    else:
        path = os.path.join(GOLDEN_DIR, "%s.json" % task_or_file)
        if not os.path.isfile(path):
            return None
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def list_golden() -> List[str]:
    if not os.path.isdir(GOLDEN_DIR):
        return []
    return sorted(name[:-5] for name in os.listdir(GOLDEN_DIR)
                  if name.endswith(".json"))


# ------------------------------------------------------------ 差异
def _diff(a: Any, b: Any, path: str = "$") -> Dict[str, Any]:
    diff: Dict[str, Any] = {}
    if isinstance(a, dict) and isinstance(b, dict):
        for key in sorted(set(a) | set(b)):
            if key not in a or key not in b:
                diff["%s.%s" % (path, key)] = {"left": a.get(key, "<missing>"),
                                               "right": b.get(key, "<missing>")}
            else:
                diff.update(_diff(a[key], b[key], "%s.%s" % (path, key)))
        return diff
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            diff["%s.length" % path] = {"left": len(a), "right": len(b)}
            return diff
        for i, (x, y) in enumerate(zip(a, b)):
            diff.update(_diff(x, y, "%s[%d]" % (path, i)))
        return diff
    if canonical_json(a) != canonical_json(b):
        diff[path] = {"left": a, "right": b}
    return diff


# ------------------------------------------------------------ 复现判定
def verify(task_id: str, task: str, args: Optional[Dict[str, Any]] = None,
           to: Any = None, n: int = 2,
           golden: Optional[Dict[str, Any]] = None,
           packs: Optional[List[str]] = None) -> Dict[str, Any]:
    runs: List[Dict[str, Any]] = []
    hashes: List[str] = []
    cores: List[Any] = []
    physicals: List[Dict[str, Any]] = []
    for _ in range(max(1, n)):
        out = run_task(task, args=args, to=to, packs=packs)
        runs.append(out)
        hashes.append(reprohash(out))
        cores.append(canonicalize(out))
        physicals.append(split_physical(out))

    stable = len(set(hashes)) == 1
    diff_repro: Dict[str, Any] = {}
    if len(cores) > 1:
        base = cores[0]
        for idx in range(1, len(cores)):
            diff_repro.update(_diff(base, cores[idx]))
    diff_phys = _diff(physicals[0], physicals[-1]) if len(physicals) > 1 else {}

    match: Optional[bool] = None
    if golden:
        expected = golden.get("expected_reprohash")
        match = bool(expected) and expected == hashes[0]
        first = runs[0]["results"][0] if runs[0].get("results") else {}
        if "expected_output" in golden:
            if _diff(golden["expected_output"], first.get("output")):
                match = False
        if golden.get("expected_status") and first.get("status") != golden["expected_status"]:
            match = False
        if golden.get("expected_matched") and first.get("matched") != golden["expected_matched"]:
            match = False

    return {
        "task_id": task_id,
        "runs": len(runs),
        "reprohash_list": hashes,
        "repro_hash_stable": stable,
        "golden_match": match,
        "diff_physical": diff_phys,
        "diff_reprocore": diff_repro,
        "all_ok": [bool(r.get("all_ok")) for r in runs],
        "matched_skills": [r["results"][0].get("matched") if r.get("results") else None
                           for r in runs],
    }


def verify_all(n: int = 2) -> List[Dict[str, Any]]:
    """跑全部 golden 任务。"""
    results: List[Dict[str, Any]] = []
    for task_id in list_golden():
        golden = load_golden(task_id)
        if not golden:
            continue
        results.append(verify(task_id, golden["task"], golden.get("args"),
                              golden.get("to"), n=n, golden=golden))
    return results
