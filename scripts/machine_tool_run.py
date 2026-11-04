# -*- coding: utf-8 -*-
"""machine_tool_run — 工程机床执行层（真跑闸门 / 补齐 git 工作区状态）

为什么单独一个脚本？
    红线（holoaeon/redline.py）禁止包内 import subprocess 与调用 run/system/popen。
    机床的「真跑」必须留在包外 —— 本脚本是唯一有执行权的一层：
      · 决策（闸门表、期望口径、verdict、台账一致性）在 holoaeon.machine_tool
      · 执行（subprocess 起进程、git status）就在本文件
    这一分层不是变通，是纪律：包=确定性逻辑，脚本=运维执行。

用法
====
    python scripts/machine_tool_run.py status            # 探针 + 真实工作区状态
    python scripts/machine_tool_run.py boot              # 开机面板（含 live 脏数）
    python scripts/machine_tool_run.py check             # 真跑七道闸门
    python scripts/machine_tool_run.py check --bench     # 追加 diff0（会写 benchmarks 产物）
    python scripts/machine_tool_run.py gate selftest     # 只跑一道

退出码：verdict=PASS → 0；FAIL / NEEDS_RUNNER → 1。
封口密语：潮起开门，潮落闭嘴。
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from holoaeon.machine_tool import (  # noqa: E402
    GATES,
    MachineTool,
    _print_panels,
)


def run_argv(argv, timeout=300):
    """以仓库根为 cwd，sys.executable 起跑，返回 (rc, 合并输出)。"""
    try:
        proc = subprocess.run(
            [sys.executable] + argv, cwd=REPO, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=timeout)
    except Exception as exc:
        return 127, "EXEC_ERROR: %s" % exc
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def git_status():
    """真实工作区状态：tracked 改动数 / untracked 数 / 当前分支 HEAD。"""
    try:
        proc = subprocess.run(["git", "status", "--porcelain"], cwd=REPO,
                              capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=30)
    except Exception as exc:
        return {"tracked_dirty": None, "untracked": None, "error": str(exc)}
    if proc.returncode != 0:
        return {"tracked_dirty": None, "untracked": None,
                "error": (proc.stderr or "").strip()}
    tracked = 0
    untracked = 0
    for line in (proc.stdout or "").splitlines():
        if not line.strip():
            continue
        if line.startswith("??"):
            untracked += 1
        else:
            tracked += 1
    return {"tracked_dirty": tracked, "untracked": untracked, "error": None}


def live_status(tool):
    base = tool.status()
    base.update(git_status())
    base["dirty_source"] = "git status --porcelain"
    return base


def live_boot(tool):
    panels = tool.boot()
    workspace = git_status()
    panels["commit"].update({
        "tracked_dirty": workspace.get("tracked_dirty"),
        "untracked": workspace.get("untracked"),
        "dirty_source": "git status --porcelain",
    })
    return panels


def run_gate(tool, name):
    argv, expect = GATES[name]
    rc, output = run_argv(argv)
    return tool.gate.ingest(name, rc, output)


def run_check(tool):
    for name in tool.gate.names():
        run_gate(tool, name)
    result = tool.check()
    result["batch_probe"] = live_status(tool)
    return result


def main(argv=None):
    argv = list(argv if argv is not None else sys.argv[1:])
    cmd = argv[0] if argv else "check"
    include_bench = "--bench" in argv
    tool = MachineTool(REPO, include_bench=include_bench)

    if cmd == "status":
        print(json.dumps(live_status(tool), ensure_ascii=False, indent=2))
        return 0
    if cmd == "boot":
        _print_panels(live_boot(tool))
        return 0
    if cmd == "check":
        result = run_check(tool)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get("verdict") == "PASS" else 1
    if cmd == "gate":
        if len(argv) < 2 or argv[1] not in GATES:
            print("usage: python scripts/machine_tool_run.py gate <%s>"
                  % "|".join(sorted(GATES)))
            return 1
        print(json.dumps(run_gate(tool, argv[1]), ensure_ascii=False, indent=2))
        return 0
    print("usage: python scripts/machine_tool_run.py [status|boot|check|gate <name>] [--bench]")
    return 1


if __name__ == "__main__":
    sys.exit(main())
