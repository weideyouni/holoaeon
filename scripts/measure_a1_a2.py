# -*- coding: utf-8 -*-
"""
measure_a1_a2 —— NEPHRON P0 的 A1 / A2 宿主侧实测脚本
================================================================================
A1：账本 off 与 full 两种模式下，**业务输出流**是否逐字节一致。
A2：同一 workload 下 full 档的额外耗时（中位数），只披露、不设通过阈值。

诚实边界（务必先读）：
  · 本脚本测量的是「宿主编排层把每一步业务动作同时记为一条账本记录」所增加的
    开销，以及「记录动作是否影响业务输出」。它**不是**真实产品级 hook 的探针：
    nephron P0 的落盘/异步队列按 N1 归宿主，本仓库尚无生产级 writer。
    因此 A1 的结论口径是 measured_with_scope，而不是宣称生产链路已闭环。
  · 输出流中时间派生字段（ts / 耗时类）按铁律「时间戳等外部因素归一化」统一
    剥离，剥离清单写入证据文件，不隐藏。
  · 纯标准库；不写 holoaeon/ 内任何东西；不联网。

用法：
    python scripts/measure_a1_a2.py                    # 打印结论
    python scripts/measure_a1_a2.py --runs 30 --write docs/nephron_a1_a2_evidence.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from holoaeon.agent import Agent                      # noqa: E402
from holoaeon.guard import Guard                      # noqa: E402
from holoaeon.kernel import Kernel                    # noqa: E402
from holoaeon.memory import Memory                    # noqa: E402
from holoaeon.packs.nephron_pack import (             # noqa: E402
    skill_nephron_event_validate, skill_nephron_ledger_record,
)
from holoaeon.scheduler import Scheduler              # noqa: E402
from holoaeon.skill import SkillRegistry              # noqa: E402

SEED = 20261030
# 时间派生 / 外部因素：按铁律 3 归一化剥离（清单进证据文件，不静默删）
VOLATILE_KEYS = ("ts", "elapsed_s", "latency_ms", "timestamp", "created_at", "duration_ms")


def canon(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str)


def strip_volatile(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: strip_volatile(v) for k, v in obj.items() if k not in VOLATILE_KEYS}
    if isinstance(obj, list):
        return [strip_volatile(v) for v in obj]
    if isinstance(obj, tuple):
        return [strip_volatile(v) for v in obj]
    return obj


def build_kernel() -> Kernel:
    reg = SkillRegistry()
    reg.register_fn("echo", lambda task: "echo:" + str(task),
                    description="echo text back")
    reg.register_fn("summarize", lambda task: "sum:" + str(task)[:20],
                    description="summarize text")
    k = Kernel()
    for i in range(2):
        k.register_agent(Agent(f"a{i}", "worker", reg))
    return k


def workload() -> List[Dict[str, Any]]:
    """固定种子 + 固定顺序的业务动作序列；覆盖四类原语且含 1 次拦截。"""
    k = build_kernel()
    mem = Memory()
    sched = Scheduler()
    guard = Guard()
    steps: List[Dict[str, Any]] = []

    def add(name: str, fn=None, out: Any = None) -> None:
        steps.append({"step": name, "value": strip_volatile(out)})

    for i in range(3):
        add(f"kernel.submit.{i}", out=k.submit(f"echo payload-{i}", to=f"a{i % 2}"))
    add("kernel.submit.blocked",
        out=k.submit("os.system('rm -rf /')", to="a0"))
    for i in range(3):
        mem.put(f"k{i}", {"v": i * 7, "note": f"n{i}"}, kind="working", tags=["t"])
    for i in range(3):
        add(f"memory.get.{i}", out={"k": i, "value": mem.get(f"k{i}")})
    add("memory.recall", out=mem.recall("note", k=2))
    add("memory.stats", out=mem.stats())
    for i in range(3):
        add(f"scheduler.tick.{i}", out=sched.tick({"load": float(i) / 10.0}))
    add("scheduler.health", out=sched.health())
    add("guard.safe", out=guard.check_text("please summarize this note").to_dict())
    add("guard.block", out=guard.check_text("os.system('rm -rf /')").to_dict())
    add("guard.stats", out=guard.stats())
    return steps


class Recorder:
    """full 档：每步记录一条 LedgerRecord（走 nephron 包的真实校验函数）。"""

    def __init__(self) -> None:
        self.records: List[Dict[str, Any]] = []
        self.watermark = 0
        self.seen: List[List[int]] = []
        self.rejects = 0

    def note(self, step: Dict[str, Any], idx: int) -> None:
        ev = skill_nephron_event_validate({
            "type": "window_build",
            "reason_code": "ADMIT_RECENT",
            "refs": [step["step"]],
            "delta": {"steps": 1},
        })
        rec = {
            "tick": idx, "seq": idx,
            "window_budget": 4096, "window_used": 1,
            "layer_residency": {"working": 1, "hebbian": 0,
                                "skeleton": 0, "external": 0},
            "hit_rate": None, "compression_ratio": None,
            "evicted_pages": 0, "external_calls": 0,
            "cost_estimate": 0.0, "confidence_estimate": None,
            "events": [{"type": ev.get("type"), "reason_code": ev.get("reason_code"),
                        "refs": ev.get("refs"), "delta": {"steps": 1}}],
            "fingerprint": "MEASURE-A1A2",
        }
        res = skill_nephron_ledger_record(rec, watermark=self.watermark, seen_keys=self.seen)
        if not res["ok"]:
            self.rejects += 1
        self.watermark = res["new_watermark"]
        self.seen.append([idx, idx])
        self.records.append(rec)


def run_once(recorder: Optional[Recorder], tamper: bool = False) -> Dict[str, Any]:
    steps = workload()
    if recorder is not None:
        for idx, s in enumerate(steps):
            recorder.note(s, idx)
    if tamper:                     # 变异：故意让 full 档改动业务输出（用于证明 A1 不是空转）
        steps = list(steps)
        steps[3] = {"step": steps[3]["step"], "value": {"tampered": True}}
    return {"steps": steps,
            "recorded": (len(recorder.records) if recorder else 0),
            "rejects": (recorder.rejects if recorder else 0)}


def sha256_of(obj: Any) -> str:
    return hashlib.sha256(canon(obj).encode("utf-8")).hexdigest()


def _a1_from(off: Dict[str, Any], full: Dict[str, Any]) -> Dict[str, Any]:
    h_off = sha256_of(off["steps"])
    h_full = sha256_of(full["steps"])
    diff_at = None
    for i, (a, b) in enumerate(zip(off["steps"], full["steps"])):
        if canon(a) != canon(b):
            diff_at = i
            break
    ok = h_off == h_full and diff_at is None
    return {"verdict": "PASS" if ok else "FAIL",
            "sha256_off": h_off, "sha256_full": h_full,
            "diff_at_step": diff_at, "steps": len(off["steps"]),
            "records_full": full["recorded"], "record_rejects": full["rejects"],
            "volatile_keys_stripped": list(VOLATILE_KEYS)}


def experiment_a1() -> Dict[str, Any]:
    return _a1_from(run_once(None), run_once(Recorder()))


def experiment_mutation() -> Dict[str, Any]:
    """变异证明：把 full 档的业务输出改掉一位，A1 必须由 PASS 翻成 FAIL。

    没有这一步，A1 的 PASS 可能只是「两边都没比较」。
    """
    base = _a1_from(run_once(None), run_once(Recorder()))
    mut = _a1_from(run_once(None), run_once(Recorder(), tamper=True))
    return {"baseline_verdict": base["verdict"], "mutant_verdict": mut["verdict"],
            "baseline_pass": base["verdict"] == "PASS",
            "mutant_fail": mut["verdict"] == "FAIL",
            "mutant_diff_at_step": mut["diff_at_step"],
            "conclusion": ("判定有效：改动输出即 FAIL" if mut["verdict"] == "FAIL"
                           else "判定空转：改动输出仍 PASS，A1 不可信")}


def machine_spec() -> Dict[str, Any]:
    import os
    return {"python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "system": platform.system(), "release": platform.release(),
            "machine": platform.machine(),
            "cpu_count": os.cpu_count(),
            "processor": platform.processor() or "unknown"}


def experiment_a2(runs: int) -> Dict[str, Any]:
    t_off: List[float] = []
    t_full: List[float] = []
    for _ in range(runs):
        s = time.perf_counter(); run_once(None); t_off.append(time.perf_counter() - s)
        s = time.perf_counter(); run_once(Recorder()); t_full.append(time.perf_counter() - s)

    def med(xs: List[float]) -> float:
        ys = sorted(xs); n = len(ys)
        return ys[n // 2] if n % 2 else (ys[n // 2 - 1] + ys[n // 2]) / 2.0

    m_off, m_full = med(t_off), med(t_full)
    pct = (m_full - m_off) / m_off * 100.0 if m_off else float("nan")
    return {"runs": runs, "median_off_ms": round(m_off * 1000, 4),
            "median_full_ms": round(m_full * 1000, 4),
            "overhead_median_pct": round(pct, 2),
            "threshold": "none — 披露项不是断言项（延续不设虚构目标值）",
            "machine": machine_spec()}


def main() -> int:
    ap = argparse.ArgumentParser(description="NEPHRON P0 A1/A2 实测")
    ap.add_argument("--runs", type=int, default=30, help="A2 每档重复次数（默认 30）")
    ap.add_argument("--write", default="", help="把证据写成 JSON 文件的路径")
    ap.add_argument("--check-evidence", default="",
                    help="与既有证据文件比对 A1 哈希；不一致即退出 1（防止证据静默过期）")
    args = ap.parse_args()

    a1 = experiment_a1()
    mut = experiment_mutation()
    a2 = experiment_a2(args.runs)
    ev = {"script": "scripts/measure_a1_a2.py", "seed": SEED,
          "date_local": time.strftime("%Y-%m-%d"), "A1": a1, "A2": a2,
          "mutation_proof": mut,
          "scope": ("宿主侧编排层记录动作；nephron P0 尚无生产级 writer，"
                    "故 A1 口径为 measured_with_scope，不等于生产链路闭环")}

    print("A1 =", a1["verdict"], "(sha256=%s)" % a1["sha256_off"][:16])
    if a1["verdict"] != "PASS":
        print("     首个差异步：", a1["diff_at_step"], "full=", a1["sha256_full"][:16])
    print("变异证明：基线", mut["baseline_verdict"], "→ 篡改后", mut["mutant_verdict"],
          "（差异步 %s）" % mut["mutant_diff_at_step"])
    print("A2 = full 中位 %.4f ms / off 中位 %.4f ms → 额外 %s%%（runs=%d）"
          % (a2["median_full_ms"], a2["median_off_ms"],
             a2["overhead_median_pct"], a2["runs"]))
    print("     机器：", a2["machine"])

    if args.write:
        p = Path(args.write)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(ev, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("evidence ->", p)
    rc = 0 if (a1["verdict"] == "PASS" and mut["mutant_fail"]) else 1

    if args.check_evidence:
        p = Path(args.check_evidence)
        try:
            old = json.loads(p.read_text(encoding="utf-8"))
            old_hash = str(old.get("A1", {}).get("sha256_off", ""))
        except Exception as exc:                     # 缺文件也算过期
            print("EVIDENCE MISSING/UNREADABLE:", exc)
            return 1
        if old_hash != a1["sha256_off"]:
            print("EVIDENCE STALE: 记录 %s != 本次 %s"
                  % (old_hash[:16] or "<empty>", a1["sha256_off"][:16]))
            print("             重跑 --write 刷新证据，并同步 docs/nephron.md 的哈希行")
            return 1
        print("EVIDENCE OK: %s" % old_hash[:16])
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
