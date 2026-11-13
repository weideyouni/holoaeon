# -*- coding: utf-8 -*-
"""
ci_preflight.py —— V78a 本地 CI 预检闸（旁挂脚本，不改内核、不进 discover）
================================================================================
把 `.github/workflows/ci.yml` 里的 10 个步骤**原样搬回本地**跑一遍，输出
`reports/ci_preflight.json`；任一步 FAIL，退出码 1。

为什么要有这台闸
----------------
2026-11-13 那次「186 次连续 failure」里最贵的一课，不是某个测试红了，而是
**本地全绿、云端全红**——本地绿从来不是云端绿的证据：
  · 本机有 F 盘素材、有客仓、有交付包，云端 checkout 里一个都没有；
  · 本机的 `SHA256SUMS` 是 CRLF 工作区口径，Linux 上必然不匹配。
修完那一批后，剩下的问题变成「怎么让下一次不再靠人去云端撞」。答案是：
**把 ci.yml 的步骤表当成一份契约，本地照抄一份、机器校验两边不许漂移。**

与 ci.yml 的契约（双向，机器判定）
--------------------------------
STEPS 里每个 `ci_name` 必须与 ci.yml 的 `- name:` 行**双向对齐**：
  · 正向：STEPS 声明的每一面，ci.yml 里都得有；
  · 反向：ci.yml 里的每个 `- name:`，STEPS 里都得认领。
这条契约由 `scripts/v3_gate.py` 的**第 33 面（A13）**机械校验——
以后 ci.yml 加了步骤而这里没跟上，v3_gate 直接红，不会悄悄漂移。

口径
----
  · 本闸只「复刻命令 + 汇总退出码」，判定仍归各门禁自己（不另立阈值）；
  · 零网络、零新增依赖、纯标准库；
  · `doc_version` 从 `holoaeon/spec.py` 实时读，不在本文件硬编码；
  · evidence_class=measured（本机实跑；仿真 ≠ 证明，判据仍以各闸为准）。

用法
----
    python scripts\\ci_preflight.py
    python scripts\\ci_preflight.py --json reports\\ci_preflight.json
    python scripts\\ci_preflight.py --only claims_gate --only redline
    python scripts\\ci_preflight.py --list
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from holoaeon.spec import DOC_VERSION  # noqa: E402

CI_WORKFLOW = os.path.join(ROOT, ".github", "workflows", "ci.yml")
DEFAULT_OUT = os.path.join(ROOT, "reports", "ci_preflight.json")
STEP_TIMEOUT = 900  # 秒；单步上限，防某步卡死时整闸挂住

# ---------------------------------------------------------------------------
# STEPS：与 ci.yml 的 `- name:` 一一对应，顺序即执行顺序。
#   ci_name 是**前缀**：ci.yml 里写 "Contract tests (tests_contract, 184 cases)"，
#   这里只需 "Contract tests" 即可命中；v3_gate A13 按前缀做双向校验。
#   kind = info  → 只记录，不判红（本地只有一个解释器，矩阵是 CI 的事）
#        = run   → 单条命令，rc 即判据
#        = multi → 多个脚本依次跑，任一 rc≠0 即红
# ---------------------------------------------------------------------------
STEPS = [
    {"id": "interpreter", "ci_name": "Interpreter", "kind": "info",
     "cmd": ["-VV"],
     "desc": "解释器版本（CI 跑 py3.8/3.10/3.12 矩阵；本地只记录当前版本）"},

    {"id": "unit_tests", "ci_name": "Unit tests", "kind": "run",
     "cmd": ["-m", "unittest", "discover", "-s", "tests"],
     "desc": "主套 unittest（V73 起含真语料组，无 F 盘素材时按守卫跳过）"},

    {"id": "contract_tests", "ci_name": "Contract tests", "kind": "run",
     "cmd": ["-m", "unittest", "discover", "-s", "tests_contract"],
     "desc": "契约测试（客仓/交付包不在本机时按守卫跳过）"},

    {"id": "dimension_lock", "ci_name": "Dimension lock", "kind": "run",
     "cmd": ["scripts/check_dimension_lock.py"],
     "desc": "维度锁：25/47/9 不漂移 + diff0 双口径"},

    {"id": "design_vocab", "ci_name": "Design vocabulary gate", "kind": "run",
     "cmd": ["scripts/verify_design_vocab.py"],
     "desc": "设计词表 D1-D8 八面"},

    {"id": "selftest", "ci_name": "Self-test", "kind": "run",
     "cmd": ["-m", "holoaeon.selftest"],
     "desc": "自检 25/25"},

    {"id": "redline", "ci_name": "Red-line scan", "kind": "run",
     "cmd": ["scripts/redline_scan.py"],
     "desc": "红线扫描（网络/依赖/危险调用）"},

    {"id": "nephron", "ci_name": "NEPHRON A1 verdict", "kind": "run",
     "cmd": ["scripts/measure_a1_a2.py", "--runs", "3"],
     "desc": "A1 判定（离载/满载字节等同 + 变异必须 FAIL），A2 只披露"},

    {"id": "claims_gate", "ci_name": "Claims gate", "kind": "run",
     "cmd": ["-m", "holoaeon.claims_gate", "verify"],
     "desc": "八面闸：叙述位 + 外部规定版本双注册簿"},

    {"id": "examples", "ci_name": "Examples 01-04", "kind": "multi",
     "cmd": ["examples/01_basic_matrix.py", "examples/02_semantic_routing.py",
             "examples/03_hebbian_collaboration.py", "examples/04_domain_pipeline.py"],
     "desc": "四例冒烟（逐个跑，任一失败即红）"},
]


# ---------------------------------------------------------------- 契约查询
def declared_ci_names() -> list:
    """STEPS 声明认领的 ci.yml 步骤名（前缀），供 v3_gate 第 33 面机械校验。"""
    return [s["ci_name"] for s in STEPS]


def read_ci_names(workflow: str = CI_WORKFLOW) -> list:
    """读 ci.yml 里所有 `- name:` 的取值（去掉 list 前缀与引号）。"""
    if not os.path.exists(workflow):
        return []
    names = []
    with open(workflow, "r", encoding="utf-8") as fh:
        for line in fh:
            stripped = line.strip()
            if not stripped.startswith("- name:"):
                continue
            value = stripped[len("- name:"):].strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
                value = value[1:-1]
            if value:
                names.append(value)
    return names


def _rel(path: str) -> str:
    """把路径转成相对 ROOT 的 / 分隔形式；跨盘（relpath 抛 ValueError）时退回绝对路径。

    为什么要兜这一层：篡改演练会把 workflow 拷到临时目录（可能是别的盘）再比对，
    relpath 在「C: 上的文件对 F: 上的根」会直接抛 ValueError，把一次正常的判红演练变成崩溃。
    """
    try:
        return os.path.relpath(path, ROOT).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def contract_report(workflow: str = CI_WORKFLOW) -> dict:
    """双向对齐报告：missing = ci.yml 有而 STEPS 没认领；unused = STEPS 有而 ci.yml 没有。"""
    ci_names = read_ci_names(workflow)
    claimed = declared_ci_names()

    def covered(name: str, prefixes: list) -> bool:
        return any(name.startswith(p) for p in prefixes)

    missing = [n for n in ci_names if not covered(n, claimed)]
    unused = [p for p in claimed if not covered_by_prefix(p, ci_names)]
    return {
        "workflow": _rel(workflow),
        "ci_steps": len(ci_names),
        "claimed_steps": len(claimed),
        "missing": missing,
        "unused": unused,
        "aligned": not missing and not unused,
    }


def covered_by_prefix(prefix: str, names: list) -> bool:
    return any(n.startswith(prefix) for n in names)


# ---------------------------------------------------------------- 执行
def _argv(cmd: list) -> list:
    """把相对脚本路径 / -m 模块调用统一成当前解释器的 argv。

    V78a 首跑踩出来的规则（三条，缺一条就会把参数当路径）：
      · 若 cmd 只有一个元素且含空格 → 先按空白切（允许写成整串命令）；
      · tokens[0] 以 '-' 开头 → 是解释器开关 / 模块调用，全部原样交给 python
        （``-m holoaeon.claims_gate verify`` 里的 verify 是子命令，不是文件）；
      · 否则 tokens[0] 是脚本相对路径（拼 ROOT），**其余 tokens 原样**
        （``--runs 3`` 的 3 是参数值，拼成 ``ROOT\\3`` 会让 argparse 直接报废）。
    """
    if len(cmd) == 1 and " " in str(cmd[0]):
        tok = str(cmd[0]).split()
    else:
        tok = [str(c) for c in cmd]
    if not tok:
        return [sys.executable]
    if tok[0].startswith("-"):
        return [sys.executable] + tok
    return [sys.executable, os.path.join(ROOT, tok[0].replace("\\", "/"))] + tok[1:]


def _tail(text: str, lines: int = 4) -> str:
    kept = [ln.strip() for ln in (text or "").splitlines() if ln.strip()]
    return " | ".join(kept[-lines:])[:400]


def run_step(step: dict) -> dict:
    """跑一步，返回机读结果。info 类不判红。"""
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    t0 = time.time()
    outputs = []
    rc = 0

    cmds = [_argv(step["cmd"])] if step["kind"] != "multi" else [_argv([c]) for c in step["cmd"]]
    for argv in cmds:
        try:
            proc = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True,
                                  encoding="utf-8", errors="replace",
                                  timeout=STEP_TIMEOUT, env=env)
            out = (proc.stdout or "") + (proc.stderr or "")
            outputs.append(out)
            if proc.returncode != 0:
                rc = proc.returncode
                break
        except subprocess.TimeoutExpired:
            rc = 124
            outputs.append("TIMEOUT after %ss: %s" % (STEP_TIMEOUT, " ".join(argv)))
            break
        except Exception as exc:  # noqa: BLE001
            rc = 125
            outputs.append("SPAWN_ERROR %s: %s" % (type(exc).__name__, exc))
            break

    ok = True if step["kind"] == "info" else (rc == 0)
    return {
        "id": step["id"],
        "ci_name": step["ci_name"],
        "kind": step["kind"],
        "desc": step["desc"],
        "rc": rc,
        "seconds": round(time.time() - t0, 2),
        "ok": ok,
        "summary": _tail(outputs[-1] if outputs else ""),
    }


# ---------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=DEFAULT_OUT)
    ap.add_argument("--only", action="append", default=[], help="只跑指定 id（可多次）")
    ap.add_argument("--list", action="store_true", help="只打印步骤表，不执行")
    a = ap.parse_args()

    if a.list:
        for s in STEPS:
            print("%-16s %-28s %s" % (s["id"], s["ci_name"], s["desc"]))
        return 0

    steps = [s for s in STEPS if not a.only or s["id"] in a.only]
    if not steps:
        print("没有匹配的步骤：%r" % (a.only,))
        return 2

    print("CI 预检 · %d 步 · DOC %s · 解释器 %s"
          % (len(steps), DOC_VERSION, sys.version.split()[0]))
    results = []
    for s in steps:
        print("  → %-16s %s ..." % (s["id"], s["ci_name"]), end="", flush=True)
        r = run_step(s)
        results.append(r)
        print(" %s (%.2fs)" % ("PASS" if r["ok"] else "FAIL(rc=%s)" % r["rc"], r["seconds"]))
        if not r["ok"]:
            print("     %s" % r["summary"])

    failed = [r["id"] for r in results if not r["ok"]]
    contract = contract_report()
    rep = {
        "gate": "ci_preflight",
        "doc_version": DOC_VERSION,
        "python": sys.version.split()[0],
        "workflow": contract["workflow"],
        "contract": contract,
        "steps": results,
        "passed": len(results) - len(failed),
        "total": len(results),
        "failed": failed,
        "verdict": "PASS" if not failed else "FAIL",
        "evidence_class": "measured",
        "note": "本地复刻 ci.yml 命令；判定归各门禁自身；本地绿不代表云端绿，只代表差异已被压到最小",
    }
    out_path = os.path.abspath(a.json)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(rep, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    print(json.dumps({"passed": rep["passed"], "total": rep["total"],
                      "failed": rep["failed"], "verdict": rep["verdict"],
                      "aligned": contract["aligned"]}, ensure_ascii=False))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
