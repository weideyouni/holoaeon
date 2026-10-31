"""统一门禁跑批：用 Python 子进程抓 stdout+stderr，写成 reports/run_v3_gate.txt。

为什么不用 PowerShell 管道：unittest 的结果走 stderr，经 PS 的 Out-String 会被序列化成
ErrorRecord，日志里只剩 exit=0、看不到 "Ran N tests ... OK"，等于证据缺失。
"""
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "reports", "run_v3_gate.txt")

PY = sys.executable
CMDS = [
    ("status", [PY, "scripts/launch_local.py", "status"]),
    ("selftest", [PY, "scripts/launch_local.py", "selftest"]),
    ("unittest34", [PY, "-m", "unittest", "discover", "-s", "tests"]),
    ("unittest-verax", [PY, "-m", "unittest", "discover", "-s", "tests/verax"]),
    ("unittest-v3", [PY, "-m", "unittest", "discover", "-s", "tests/v3"]),
    ("redline", [PY, "scripts/redline_scan.py"]),
    ("verax_verify", [PY, "scripts/verax_verify.py", "--out", "reports"]),
    ("bench_public", [PY, "benchmarks/bench_public.py"]),
    ("bench_semvec", [PY, "scripts/bench_semvec.py"]),
    ("ledger_view", [PY, "scripts/ledger_view.py", "--sample", "data/ledger_sample.jsonl"]),
    ("make_snapshot", [PY, "scripts/make_snapshot.py"]),
]


def main():
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    lines = ["# HoloAeon V3 gate run  (%s)" % time.strftime("%Y-%m-%dT%H:%M:%S"), ""]
    for name, argv in CMDS:
        lines.append("===== %s =====" % name)
        lines.append("$ " + " ".join(argv[1:]))
        proc = subprocess.run(argv, cwd=ROOT, env=env,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        text = proc.stdout.decode("utf-8", errors="replace").strip()
        lines.append(text)
        lines.append("exit=%d" % proc.returncode)
        lines.append("")
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))
    print("written: %s  bytes=%d" % (OUT, os.path.getsize(OUT)))


if __name__ == "__main__":
    main()
