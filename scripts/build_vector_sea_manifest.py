# -*- coding: utf-8 -*-
"""V4.3 · 向量海清单重建器（把「先 74、后 manifest」的顺序写进代码）。

坑的成因
--------
`74_SHA256SUMS` 是向量海里的一份清单快照。若先 `os.listdir` 建 `manifest.json`、再覆盖
`74_SHA256SUMS`，则 74 自身已被登记进 manifest，而它的内容又在同一次运行里变过 ——
manifest 里那份 sha/bytes 立刻过期，`check_vector_sea_manifest.py` 就会报
`missing/bad_bytes: ["74_SHA256SUMS"]`（自指）。反过来则永远自洽：

    1) 先把主机 `SHA256SUMS` 覆盖成 `74_SHA256SUMS`
    2) 再 `os.listdir` 全量重建 `manifest.json`（排除自身、扁平 `{名:{sha256,bytes}}`、`sort_keys`）

用法
----
    python scripts/build_vector_sea_manifest.py            # 重建（含 74 同步）
    python scripts/build_vector_sea_manifest.py --check     # 只校验，不写

两种模式都输出一行 JSON。`--check` 的 `verdict=PASS` 等价于「顺序正确且清单自洽」。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from typing import Any, Dict, List, Optional

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_S4 = r"F:\doubaowork\vector-sea\holoaeon-v4-cold-hot-plug"
MANIFEST = "manifest.json"
SUMS_74 = "74_SHA256SUMS"

STEPS = ("copy_74_SHA256SUMS", "build_manifest")


def plan_steps() -> List[str]:
    """固定顺序：74 必须在 manifest 之前。"""
    return list(STEPS)


def self_reference(names: List[str], manifest_name: str = MANIFEST) -> List[str]:
    """清单里是否包含自身（自指检测）。"""
    return [n for n in names if n == manifest_name]


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def entries(s4: str) -> List[str]:
    return sorted(n for n in os.listdir(s4)
                  if os.path.isfile(os.path.join(s4, n)) and n != MANIFEST)


def build(s4: str, sums_src: Optional[str] = None) -> Dict[str, Any]:
    sums_src = sums_src or os.path.join(REPO_ROOT, "SHA256SUMS")
    shutil.copy2(sums_src, os.path.join(s4, SUMS_74))       # 第 1 步
    names = entries(s4)                                     # 第 2 步（此时 74 已是终态）
    man = {n: {"sha256": sha256(os.path.join(s4, n)),
               "bytes": os.path.getsize(os.path.join(s4, n))} for n in names}
    with open(os.path.join(s4, MANIFEST), "w", encoding="utf-8", newline="\n") as f:
        json.dump(man, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    return {"verdict": "BUILT", "entries": len(man), "steps": plan_steps(),
            "self_reference": self_reference(names)}


def check(s4: str, sums_src: Optional[str] = None) -> Dict[str, Any]:
    sums_src = sums_src or os.path.join(REPO_ROOT, "SHA256SUMS")
    mf = os.path.join(s4, MANIFEST)
    if not os.path.isfile(mf):
        return {"verdict": "FAIL", "reason": "manifest_missing"}
    with open(mf, encoding="utf-8") as f:
        man = json.load(f)
    names = entries(s4)
    bad = {
        "missing": [n for n in names if n not in man],
        "extra": [n for n in man if n not in names],
        "bad_sha256": [n for n in names if n in man
                       and man[n].get("sha256") != sha256(os.path.join(s4, n))],
        "bad_bytes": [n for n in names if n in man
                      and man[n].get("bytes") != os.path.getsize(os.path.join(s4, n))],
    }
    sums_ok = (not os.path.isfile(os.path.join(s4, SUMS_74)) or
               sha256(os.path.join(s4, SUMS_74)) == sha256(sums_src))
    ok = not any(bad.values()) and sums_ok
    out = {"verdict": "PASS" if ok else "FAIL", "entries": len(man),
           "dir_files": len(names), "sums_74_in_sync": sums_ok,
           "steps": plan_steps(), "self_reference": self_reference(list(man))}
    out.update(bad)
    return out


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="向量海 74/manifest 重建与自洽校验")
    ap.add_argument("--dir", default=DEFAULT_S4)
    ap.add_argument("--sums", default=None)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    res = check(args.dir, args.sums) if args.check else build(args.dir, args.sums)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    if args.check:
        return 0 if res["verdict"] == "PASS" else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
