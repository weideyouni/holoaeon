# -*- coding: utf-8 -*-
"""V4.3 · 交付目录 PKG 漂移诊断（把「改 01/06 就会漂」变成一条命令）。

坑的成因
--------
交付目录（`HoloAeon_V4冷热插拔赋能升级_20261102`）不在任何 git 仓里，但它的 28 个包内文件
被 `scripts/five_site_dna.py` 的 `PKG_FILES` 逐个哈希登记。改其中任何一个（例如 01 总策划、
06 验收票据），`package` 段就漂；而 06/01 又可能被打进确定性 zip，所以正确处置顺序是：

    诊断 -> 重建 zip（build_b9_closeout.py）-> 重建清单（five_site_dna.py build）-> 复核

本脚本就是这一步「诊断 + 一键重建 + 复核」的可执行版本。`--fix` 会依次调用上述两个脚本，
不手改任何文件内容；`--check` 只读。

用法
----
    python scripts/check_delivery_pkg.py            # 只诊断
    python scripts/check_delivery_pkg.py --fix       # 诊断 -> 重建 zip/清单 -> 复核

要新增交付件而不想触发漂移：把它写成**不进 PKG_FILES 的补记件**（如 `07_...补记.md`），
或显式登记进 `PKG_FILES` 后按上面顺序重建。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from typing import Any, Dict, List, Optional

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))

import five_site_dna as dna  # noqa: E402  （复用同一份 PKG_FILES/口径，避免两套定义）


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def snapshot(pkg: str, names: List[str]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for name in names:
        path = os.path.join(pkg, name.replace("/", os.sep))
        if os.path.isfile(path):
            out[name] = {"bytes": os.path.getsize(path), "sha256": sha256(path)}
    return out


def diagnose(pkg: Optional[str] = None, manifest: Optional[str] = None) -> Dict[str, Any]:
    pkg = pkg or dna.PKG
    manifest = manifest or dna.MANIFEST
    with open(manifest, encoding="utf-8") as f:
        man = json.load(f)
    registered = man.get("package", {})
    live = snapshot(pkg, dna.PKG_FILES)
    drift = []
    for name in dna.PKG_FILES:
        if name not in live:
            drift.append("package:missing:%s" % name)
        elif name not in registered:
            drift.append("package:unregistered:%s" % name)
        elif (registered[name].get("sha256") != live[name]["sha256"]
              or registered[name].get("bytes") != live[name]["bytes"]):
            drift.append("package:changed:%s" % name)
    extra = [name for name in registered
             if name not in dna.PKG_FILES and name != getattr(dna, "ZIP_NAME", "")]
    return {"verdict": "PASS" if not drift else "DRIFT", "checked": len(dna.PKG_FILES),
            "drift": drift, "extra_registered": extra,
            "remedy": ["python scripts/build_b9_closeout.py",
                       "python scripts/five_site_dna.py build",
                       "python scripts/five_site_dna.py verify"]}


def run_step(args: List[str]) -> Dict[str, Any]:
    out = subprocess.run([sys.executable] + args, cwd=REPO_ROOT,
                         capture_output=True, text=True, encoding="utf-8")
    return {"step": " ".join(args), "returncode": out.returncode,
            "tail": (out.stdout or out.stderr).strip().splitlines()[-1:]}


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="交付目录 PKG 漂移诊断/一键重建")
    ap.add_argument("--pkg", default=None)
    ap.add_argument("--fix", action="store_true")
    args = ap.parse_args(argv)
    res = diagnose(args.pkg)
    if args.fix and res["drift"]:
        res["steps"] = [run_step(["scripts/build_b9_closeout.py"]),
                        run_step(["scripts/five_site_dna.py", "build"])]
        res = diagnose(args.pkg)
        res["fixed"] = True
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0 if res["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
