# -*- coding: utf-8 -*-
"""V86 批3 · F 盘资产全量登记（现场回读，禁写死清单）。

一次顶层 scandir（不递归、不抽样推断），按投喂包 §5.3 枚举规则筛出
产物型净候选，并对每个候选实读「runtime_v3/ + selftest.py + *.zip +
SHA256SUMS」四件齐备度。

用法：python scripts/asset_census.py [--root F:/doubaowork]
产物：reports/asset_census.json（本机留痕，不入 SHA256SUMS 清单）
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # holoaeon
SCAN = r"F:\doubaowork"
EXCLUDE_PARTS = (".tmp", "snapshot", "_历史", "restore", "archive", "vector-sea",
                 "skills_harvest", "_doubao_replica", "__pycache__")
KEY_HINTS = ("实战化", "矩阵", "引擎")


def is_candidate(name):
    if not any(k in name for k in KEY_HINTS):
        return False
    low = name.lower()
    return not any(x in low for x in EXCLUDE_PARTS)


def probe_dir(path):
    """四件齐备度实读：不猜、不抽样。"""
    has_runtime = os.path.isdir(os.path.join(path, "runtime_v3"))
    has_selftest = os.path.isfile(os.path.join(path, "selftest.py"))
    has_sums = os.path.isfile(os.path.join(path, "SHA256SUMS"))
    zips = []
    runtime_py = 0
    try:
        for e in os.scandir(path):
            if e.is_file() and e.name.lower().endswith(".zip"):
                zips.append({"name": e.name, "bytes": e.stat().st_size})
    except OSError:
        pass
    rt = os.path.join(path, "runtime_v3")
    if has_runtime:
        for base, dirs, fns in os.walk(rt):
            runtime_py += sum(1 for f in fns if f.endswith(".py"))
            if runtime_py > 999:
                break
    ready = has_runtime and has_selftest and bool(zips) and has_sums
    return {"runtime_v3": has_runtime, "selftest": has_selftest,
            "zip": zips[:3], "zip_count": len(zips), "sha256sums": has_sums,
            "runtime_py": runtime_py, "four_pieces": ready}


def main():
    scan = SCAN
    if "--root" in sys.argv:
        scan = sys.argv[sys.argv.index("--root") + 1].replace("\\", "/")
    dirs, files = [], []
    for e in os.scandir(scan):
        (dirs if e.is_dir() else files).append(e.name)
    ext = {}
    for f in files:
        ext[os.path.splitext(f)[1].lower() or "(none)"] = \
            ext.get(os.path.splitext(f)[1].lower() or "(none)", 0) + 1
    cand = sorted([d for d in dirs if is_candidate(d)])
    rows = []
    for name in cand:
        row = {"name": name, "v3_family": "V3" in name}
        row.update(probe_dir(os.path.join(scan, name)))
        rows.append(row)
    out = {
        "schema": "HOLOAEON-ASSET-CENSUS-v1.0",
        "scan_root": scan, "top_items": len(dirs) + len(files),
        "dirs": len(dirs), "files": len(files),
        "file_ext": dict(sorted(ext.items(), key=lambda kv: -kv[1])),
        "net_candidates": len(rows),
        "v3_family": sum(1 for r in rows if r["v3_family"]),
        "top_zips": ext.get(".zip", 0),
        "four_pieces_ready": sum(1 for r in rows if r["four_pieces"]),
        "candidates": rows,
        "rule": "顶层名称含 实战化/矩阵/引擎，排除 .tmp/snapshot/_历史/restore/"
                "archive/vector-sea/skills_harvest/_doubao_replica/__pycache__",
        "note": "现场回读，禁写死清单；登记≠装配",
        "seal": "潮起开门，潮落闭嘴",
    }
    d = os.path.join(ROOT, "reports")
    os.makedirs(d, exist_ok=True)
    io.open(os.path.join(d, "asset_census.json"), "w", encoding="utf-8",
            newline="\n").write(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    print("census: top=%d (%d 目录/%d 文件) | 净候选=%d | V3族=%d | top_zip=%d | 四件齐=%d"
          % (out["top_items"], out["dirs"], out["files"], out["net_candidates"],
             out["v3_family"], out["top_zips"], out["four_pieces_ready"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
