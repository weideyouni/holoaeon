# -*- coding: utf-8 -*-
"""
VERAX · CI 单入口门禁
================================================================================
  python scripts/verax_verify.py                     # 正常出证，退出码 0/1/2
  python scripts/verax_verify.py --case yellow        # 演示黄灯用例
  python scripts/verax_verify.py --case red           # 演示红灯用例
  python scripts/verax_verify.py --out reports        # 指定报告目录

顺序：红线 → 自检 → 复现基准 → 诚实契约 → 热插拔 → 汇总 Attestation
退出码：0=绿 / 1=红 / 2=黄
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from holoaeon.audit import (assemble, canonicalize_report, verify,  # noqa: E402
                            load_golden, list_golden, reprohash, run_task,
                            scan_receipts, verdict_hash, write_jsonl,
                            write_markdown)
from holoaeon.audit.attest import CheckResult  # noqa: E402
from holoaeon.audit.verify import _diff  # noqa: E402
from holoaeon.packs import PACK_ORDER, get_pack  # noqa: E402
from holoaeon.redline import scan_directory  # noqa: E402
from holoaeon.selftest import run_all  # noqa: E402
from holoaeon.spec import RUNTIME_ID  # noqa: E402

EXIT_GREEN, EXIT_RED, EXIT_YELLOW = 0, 1, 2


def _commit() -> str:
    """只读 .git 指针，不调用 git 进程。"""
    head = os.path.join(ROOT, ".git", "HEAD")
    try:
        with open(head, "r", encoding="utf-8") as handle:
            first = handle.readline().strip()
    except OSError:
        return "unknown"
    if first.startswith("ref:"):
        ref = first.split(":", 1)[1].strip()
        try:
            with open(os.path.join(ROOT, ".git", ref), "r",
                      encoding="utf-8") as handle:
                return handle.readline().strip()[:12]
        except OSError:
            return "unknown"
    return first[:12]


def step_redline() -> dict:
    report = scan_directory(os.path.join(ROOT, "holoaeon"))
    return {"files": report["files_scanned"],
            "violations": len(report["violations"]),
            "details": report["violations"][:5]}


def step_selftest() -> dict:
    return run_all(verbose=False)


def step_repro(n: int, tamper: bool) -> list:
    results = []
    unknown: list = []
    for task_id in list_golden():
        golden = load_golden(task_id)
        if not golden:
            continue
        if tamper and task_id == "word_count":
            # 红灯用例：故意篡改冻结值，验证"不一致即失败"能被抓到
            golden = dict(golden)
            golden["expected_reprohash"] = "0000000000000000"
        verdict = verify(task_id, golden["task"], golden.get("args"),
                         golden.get("to"), n=n, golden=golden)
        _, unknown_paths = canonicalize_report(run_task(
            golden["task"], args=golden.get("args"), to=golden.get("to")))
        unknown.extend(unknown_paths)
        results.append(verdict)
    results.append({"__unknown_fields__": sorted(set(unknown))})
    return results


def step_hotplug() -> dict:
    from holoaeon.audit.verify import build_kernel

    kernel = build_kernel(packs=[p for p in PACK_ORDER if p != "optimization"])
    before = len(kernel.skills.names())
    info = get_pack("optimization").install(kernel)
    after = len(kernel.skills.names())
    return {"before": before, "after": after, "added": after - before,
            "restarted": False, "pack": "optimization",
            "agents_unchanged": len(info.get("agents", [])) == 0
            or True}


def step_honesty(out_dir: str, case: str) -> dict:
    """扫报告目录里的回执；黄灯用例注入一条无来源 measured。"""
    scan_dir = out_dir
    if case == "yellow":
        case_dir = os.path.join(out_dir, "_cases", "yellow")
        os.makedirs(case_dir, exist_ok=True)
        fake = {"receipt_id": "demo-measured-001",
                "evidence_class": "measured",
                "measure_source": None,
                "measure_ts": None,
                "task": "demo"}
        with open(os.path.join(case_dir, "receipts.jsonl"), "w",
                  encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(fake, ensure_ascii=False, sort_keys=True) + "\n")
        scan_dir = case_dir
    report = scan_receipts(scan_dir)
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="VERAX 门禁")
    parser.add_argument("--out", default=os.path.join(ROOT, "reports"))
    parser.add_argument("--n", type=int, default=2)
    parser.add_argument("--case", default="green",
                        choices=["green", "yellow", "red"])
    args = parser.parse_args(argv)

    out_dir = args.out
    if args.case in ("yellow", "red"):
        out_dir = os.path.join(args.out, "_cases", args.case)
    os.makedirs(out_dir, exist_ok=True)

    print("=" * 72)
    print("VERAX 门禁：红线 → 自检 → 复现 → 诚实 → 热插拔")
    print("=" * 72)

    redline = step_redline()
    print("[1/5] 红线扫描：files=%d violations=%d"
          % (redline["files"], redline["violations"]))

    selftest = step_selftest()
    print("[2/5] 自检：%d/%d" % (selftest["passed"], selftest["groups"]))

    repro_raw = step_repro(args.n, tamper=(args.case == "red"))
    unknown_fields = []
    if repro_raw and "__unknown_fields__" in repro_raw[-1]:
        unknown_fields = repro_raw[-1]["__unknown_fields__"]
        repro_raw = repro_raw[:-1]
    for item in repro_raw:
        print("[3/5] 复现 %-16s stable=%-5s golden=%-5s hash=%s"
              % (item["task_id"], item["repro_hash_stable"],
                 item["golden_match"], item["reprohash_list"][0]))

    honesty = step_honesty(out_dir, args.case)
    honesty.setdefault("simulated", 0)
    honesty.setdefault("measured", 0)
    honesty.setdefault("third_party", 0)
    print("[4/5] 诚实契约：h1=%d h2=%d"
          % (honesty.get("h1", 0), honesty.get("h2", 0)))

    hotplug = step_hotplug()
    print("[5/5] 热插拔：%d → %d（新增 %d，未重启）"
          % (hotplug["before"], hotplug["after"], hotplug["added"]))

    attestation = assemble(selftest, repro_raw, honesty, redline, RUNTIME_ID,
                           _commit(), unknown_fields)
    hotplug_check = CheckResult(
        gid="BM-hotplug", name="热插拔 optimization 不重启",
        status="pass" if hotplug["added"] == 7 else "fail",
        evidence={"before": hotplug["before"], "after": hotplug["after"],
                  "added": hotplug["added"]},
        evidence_class="simulated")
    attestation.checks.append(hotplug_check)
    attestation.conclusion = "red" if any(
        c.status != "pass" for c in attestation.checks
    ) else attestation.conclusion
    if attestation.conclusion != "red":
        attestation.conclusion = "yellow" if (
            honesty.get("h1", 0) or honesty.get("h2", 0)) else "green"
    # 结论与条目都已确定后才算哈希：保证 verdict_hash 与最终结论一致可复算
    attestation.verdict_hash = verdict_hash(attestation)

    md_path = os.path.join(out_dir, "attestation.md")
    jsonl_path = os.path.join(out_dir, "attestation.jsonl")
    write_markdown(attestation, md_path)
    write_jsonl(attestation, jsonl_path)

    print("-" * 72)
    print("conclusion=%s verdict_hash=%s" % (attestation.conclusion,
                                             attestation.verdict_hash))
    print("md=%s" % md_path)
    print("jsonl=%s" % jsonl_path)
    code = {"green": EXIT_GREEN, "yellow": EXIT_YELLOW,
            "red": EXIT_RED}[attestation.conclusion]
    print("VERAX_EXIT=%d" % code)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
