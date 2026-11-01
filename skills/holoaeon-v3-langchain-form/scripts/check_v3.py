# -*- coding: utf-8 -*-
"""
check_v3.py —— 技能自带的一键校验包装（零依赖）
================================================================================
定位 HoloAeon 仓库 → 依次跑 单测 / 自检 / DIFF=0 / V3 门禁 / 本地装载。
任一失败即以非零退出码结束（fail-loud）。

用法：
    python check_v3.py                # 自动向上查找仓库根
    python check_v3.py --repo F:\\doubaowork\\holoaeon
    python check_v3.py --quick        # 只跑 V3 门禁
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys


def find_repo(start: str) -> str:
    cur = os.path.abspath(start)
    while True:
        if os.path.isfile(os.path.join(cur, "holoaeon", "spec.py")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            return ""
        cur = parent


def run(cmd, cwd: str) -> int:
    print("$ " + " ".join(cmd))
    proc = subprocess.run(cmd, cwd=cwd)
    return proc.returncode


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="")
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()

    repo = a.repo or find_repo(os.getcwd())
    if not repo or not os.path.isfile(os.path.join(repo, "holoaeon", "spec.py")):
        print("找不到 HoloAeon 仓库根（需要含 holoaeon/spec.py）。请用 --repo 指定。")
        return 2

    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONPATH"] = repo

    steps = []
    if not a.quick:
        steps.append([sys.executable, "-m", "unittest", "discover", "-s", "tests"])
        steps.append([sys.executable, "-c",
                      "from holoaeon.selftest import run_all; r=run_all(); "
                      "print('selftest', r['ok'], r['groups']); "
                      "raise SystemExit(0 if r['ok'] else 1)"])
        steps.append([sys.executable, os.path.join("benchmarks", "bench_public.py"),
                      "--no-write"])
    steps.append([sys.executable, os.path.join("scripts", "v3_gate.py")])
    if not a.quick:
        steps.append([sys.executable, os.path.join("scripts", "launch_v3.py")])

    worst = 0
    for cmd in steps:
        code = subprocess.run(cmd, cwd=repo, env=env).returncode
        worst = max(worst, code)
    print("-" * 60)
    print("WORST_EXIT=%d  repo=%s" % (worst, repo))
    return worst


if __name__ == "__main__":
    raise SystemExit(main())
