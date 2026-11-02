# -*- coding: utf-8 -*-
r"""
build_skill_matrix.py —— 全量技能索引 + F 盘以往项目基座清单（只读扫描，确定性输出）
================================================================================
用法：
  python scripts/build_skill_matrix.py                    # 默认 5 个技能根 + F:\doubaowork
  python scripts/build_skill_matrix.py --roots A B        # 指定技能根
  python scripts/build_skill_matrix.py --projects P       # 指定以往项目目录
  python scripts/build_skill_matrix.py --json out.json    # 额外打印摘要到文件
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holoaeon.skill_matrix import DEFAULT_INDEX, default_roots  # noqa: E402
from holoaeon.skill_matrix import index as Ix  # noqa: E402
from holoaeon.skill_matrix.mech import semantic_overlap  # noqa: E402
from holoaeon.skill_matrix.index import MECH_LEXICON  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASELINE = os.path.join(ROOT, "data", "skill_matrix_baseline.json")
SKIP_PREFIX = (".", "_")
FILE_CAP = 4000


def dir_stats(path: str) -> Dict[str, object]:
    files = py = 0
    skill_md = 0
    for base, dirs, names in os.walk(path):
        if files >= FILE_CAP:
            break
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for n in names:
            files += 1
            if n.endswith(".py"):
                py += 1
            elif n == "SKILL.md":
                skill_md += 1
    return {"files": files, "py_files": py, "skill_md": skill_md, "capped": files >= FILE_CAP}


def mech_guess(name: str) -> str:
    best, score = "unmapped", 0.0
    for key, words in MECH_LEXICON.items():
        sc = max((semantic_overlap(name, w) for w in words), default=0.0)
        if sc > score:
            best, score = key, sc
    return best


def scan_projects(root: str) -> List[dict]:
    rows: List[dict] = []
    if not os.path.isdir(root):
        return rows
    for entry in sorted(os.listdir(root)):
        p = os.path.join(root, entry)
        if entry.startswith(SKIP_PREFIX) or not os.path.exists(p):
            continue
        is_dir = os.path.isdir(p)
        stat = os.stat(p)
        if is_dir:
            ds = dir_stats(p)
            kind = "dir"
            py = ds["py_files"]
            files = ds["files"]
        else:
            kind = "zip" if entry.lower().endswith(".zip") else (
                "md" if entry.lower().endswith(".md") else "file")
            py, files = 0, 1
        rows.append({"name": entry, "kind": kind,
                     "bytes": int(stat.st_size) if not is_dir else 0,
                     "files": files, "py_files": py,
                     "mechanism": mech_guess(entry),
                     "tier": "基座候选" if (py >= 10 or files >= 50) else "素材"})
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="构建技能索引与基座清单")
    ap.add_argument("--roots", nargs="*", default=None)
    ap.add_argument("--projects", default=r"F:\doubaowork")
    ap.add_argument("--index", default=DEFAULT_INDEX)
    ap.add_argument("--baseline", default=BASELINE)
    ap.add_argument("--json", default=None)
    a = ap.parse_args(argv)

    roots = a.roots or default_roots()
    idx = Ix.build(roots)
    sha = Ix.save(idx, a.index)
    base_rows = scan_projects(a.projects)
    base = {"source": os.path.abspath(a.projects),
            "count": len(base_rows), "entries": base_rows,
            "summary": {"dirs": sum(1 for r in base_rows if r["kind"] == "dir"),
                        "zips": sum(1 for r in base_rows if r["kind"] == "zip"),
                        "md": sum(1 for r in base_rows if r["kind"] == "md"),
                        "baseline_candidates": sum(1 for r in base_rows if r["tier"] == "基座候选"),
                        "py_total": sum(int(r["py_files"]) for r in base_rows)}}
    os.makedirs(os.path.dirname(a.baseline), exist_ok=True)
    payload = json.dumps(base, ensure_ascii=False, indent=1, sort_keys=True)
    with open(a.baseline, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(payload)

    summary = {"index": {"path": a.index, "digest": idx["digest"], "count": idx["count"],
                         "sha16": sha, "roots": len(idx["roots"])},
               "stats": idx["stats"],
               "baseline": dict(base["summary"], path=a.baseline,
                                sha16=__import__("hashlib").sha256(payload.encode("utf-8")).hexdigest()[:16])}
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    if a.json:
        with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(summary, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
