# -*- coding: utf-8 -*-
"""
VERAX · 自证报告（attest）
================================================================================
把 G1–G24 + 基准复现 + 诚实契约 + 红线 合成一份可复算的自证报告：
  reports/attestation.md   人读（沿用项目 ASCII 回执美学）
  reports/attestation.jsonl 机器读（逐行一条 CheckResult，键序稳定）

verdict_hash 由结论字段规范化生成，不含 ts_build，因此可复现。

保护哪条立身原则：可审计（结论可复算）、诚实纪律（分级随行）。
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List

from .fields import reprohash


@dataclass
class CheckResult:
    gid: str
    name: str
    status: str = "pass"
    evidence: Dict[str, Any] = field(default_factory=dict)
    evidence_class: str = "simulated"

    def to_dict(self) -> Dict[str, Any]:
        return {"gid": self.gid, "name": self.name, "status": self.status,
                "evidence": self.evidence,
                "evidence_class": self.evidence_class}


@dataclass
class Attestation:
    runtime_id: str
    commit: str
    checks: List[CheckResult] = field(default_factory=list)
    repro_summary: List[Dict[str, Any]] = field(default_factory=list)
    honesty_summary: Dict[str, Any] = field(default_factory=dict)
    redline: Dict[str, Any] = field(default_factory=dict)
    ts_build: str = ""
    verdict_hash: str = ""
    conclusion: str = "green"
    unknown_fields: List[str] = field(default_factory=list)


# ------------------------------------------------------------ 组装
def checks_from_selftest(result: Dict[str, Any]) -> List[CheckResult]:
    """把 run_all() 的 details 映射成 CheckResult（G1–G24）。"""
    checks: List[CheckResult] = []
    for idx, item in enumerate(result.get("details", []), 1):
        checks.append(CheckResult(
            gid="G%d" % idx,
            name=item.get("group", "G%d" % idx),
            status="pass" if item.get("passed") else "fail",
            evidence={"detail": item.get("detail", "")},
            evidence_class="simulated",
        ))
    return checks


def checks_from_repro(repro_summary: List[Dict[str, Any]]) -> List[CheckResult]:
    checks: List[CheckResult] = []
    for repro in repro_summary:
        ok = bool(repro.get("repro_hash_stable")) and repro.get("golden_match") is not False
        checks.append(CheckResult(
            gid="BM-%s" % repro.get("task_id"),
            name="复现基准 %s" % repro.get("task_id"),
            status="pass" if ok else "fail",
            evidence={"reprohash": (repro.get("reprohash_list") or [None])[0],
                      "runs": repro.get("runs"),
                      "golden_match": repro.get("golden_match"),
                      "stable": bool(repro.get("repro_hash_stable"))},
            evidence_class="simulated",
        ))
    return checks


def conclusion_of(check_list: List[CheckResult], honesty: Dict[str, Any],
                  redline: Dict[str, Any]) -> str:
    if any(c.status != "pass" for c in check_list):
        return "red"
    if redline.get("violations", 0) > 0:
        return "red"
    if honesty.get("h1", 0) > 0 or honesty.get("h2", 0) > 0:
        return "yellow"
    return "green"


def assemble(selftest: Dict[str, Any], repro_summary: List[Dict[str, Any]],
             honesty: Dict[str, Any], redline: Dict[str, Any],
             runtime_id: str, commit: str,
             unknown_fields: List[str] = None) -> Attestation:
    checks = checks_from_selftest(selftest) + checks_from_repro(repro_summary)
    honesty_summary = {
        "simulated": honesty.get("simulated", 0),
        "measured": honesty.get("measured", 0),
        "third_party": honesty.get("third_party", 0),
        "noncompliant": honesty.get("h1", 0) + honesty.get("h2", 0),
    }
    redline_summary = {"files": redline.get("files", 0),
                       "violations": redline.get("violations", 0),
                       "honesty_flags": honesty.get("h1", 0) + honesty.get("h2", 0)}
    att = Attestation(
        runtime_id=runtime_id, commit=commit, checks=checks,
        repro_summary=repro_summary, honesty_summary=honesty_summary,
        redline=redline_summary,
        ts_build=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        unknown_fields=list(unknown_fields or []),
    )
    att.conclusion = conclusion_of(checks, honesty, redline_summary)
    att.verdict_hash = verdict_hash(att)
    return att


def verdict_hash(att: Attestation) -> str:
    payload = {
        "runtime_id": att.runtime_id,
        "commit": att.commit,
        "conclusion": att.conclusion,
        "checks": [{"gid": c.gid, "status": c.status, "evidence": c.evidence}
                   for c in att.checks],
        "repro": [{"task_id": r.get("task_id"),
                   "reprohash_list": r.get("reprohash_list"),
                   "stable": bool(r.get("repro_hash_stable")),
                   "golden_match": r.get("golden_match")}
                  for r in att.repro_summary],
        "honesty": att.honesty_summary,
        "redline": att.redline,
        "unknown_fields": sorted(att.unknown_fields),
    }
    return reprohash(payload)


# ------------------------------------------------------------ 导出
def write_markdown(att: Attestation, path: str) -> str:
    lines: List[str] = []
    lines.append("=" * 72)
    lines.append("HoloAeon VERAX 自证报告（Self-Attestation）")
    lines.append("=" * 72)
    lines.append("runtime_id : %s" % att.runtime_id)
    lines.append("commit     : %s" % att.commit)
    lines.append("ts_build   : %s   （物理量，不进 verdict_hash）" % att.ts_build)
    lines.append("verdict    : %s" % att.conclusion.upper())
    lines.append("verdict_hash : %s" % att.verdict_hash)
    lines.append("证据分级   : 本报告全部条目默认 simulated；仿真≠证明。")
    lines.append("")
    lines.append("-" * 72)
    lines.append("一、自检与基准逐项（G1–G%d + BM）" % len([c for c in att.checks
                                                     if c.gid.startswith("G")]))
    lines.append("-" * 72)
    lines.append("%-10s %-34s %-6s %s" % ("GID", "NAME", "STATUS", "EVIDENCE"))
    for check in att.checks:
        evidence = check.evidence
        if "detail" in evidence:
            short = str(evidence["detail"])
        else:
            short = "hash=%s golden=%s" % (evidence.get("reprohash"),
                                           evidence.get("golden_match"))
        lines.append("%-10s %-34s %-6s %s" % (check.gid, check.name[:32],
                                              check.status, short[:70]))
    lines.append("")
    lines.append("-" * 72)
    lines.append("二、复现判定（ReproVerdict）")
    lines.append("-" * 72)
    for repro in att.repro_summary:
        lines.append("task_id=%s runs=%s stable=%s golden_match=%s"
                     % (repro.get("task_id"), repro.get("runs"),
                        repro.get("repro_hash_stable"), repro.get("golden_match")))
        lines.append("  reprohash: %s" % ", ".join(repro.get("reprohash_list") or []))
        if repro.get("diff_physical"):
            lines.append("  diff_physical（仅记录，不影响判定）: %d 项"
                         % len(repro["diff_physical"]))
        if repro.get("diff_reprocore"):
            lines.append("  diff_reprocore（非空即判不确定）: %s"
                         % json.dumps(repro["diff_reprocore"], ensure_ascii=False))
    lines.append("")
    lines.append("-" * 72)
    lines.append("三、诚实契约（honesty）")
    lines.append("-" * 72)
    lines.append("simulated=%s measured=%s third_party=%s noncompliant=%s"
                 % (att.honesty_summary.get("simulated"),
                    att.honesty_summary.get("measured"),
                    att.honesty_summary.get("third_party"),
                    att.honesty_summary.get("noncompliant")))
    lines.append("H1（measured 无来源）/ H2（缺 evidence_class）命中计数：%s"
                 % att.redline.get("honesty_flags"))
    lines.append("")
    lines.append("-" * 72)
    lines.append("四、红线（redline）")
    lines.append("-" * 72)
    lines.append("扫描文件数=%s violations=%s"
                 % (att.redline.get("files"), att.redline.get("violations")))
    if att.unknown_fields:
        lines.append("未登记字段（按物理量处理，已告警）：%s"
                     % ", ".join(sorted(att.unknown_fields)))
    lines.append("")
    lines.append("五、门禁退出码：0=绿 / 1=红 / 2=黄（scripts/verax_verify.py）")
    lines.append("六、已知限制：measured 只证明「来源存在」，不证明外部真实性；"
                 "VERAX 不改 C1–C12 行为，只读观测。")
    lines.append("")
    text = "\n".join(lines) + "\n"
    _ensure_dir(os.path.dirname(os.path.abspath(path)))
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    return path


def write_jsonl(att: Attestation, path: str) -> str:
    _ensure_dir(os.path.dirname(os.path.abspath(path)))
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        for check in att.checks:
            handle.write(json.dumps(check.to_dict(), ensure_ascii=False,
                                    sort_keys=True) + "\n")
        handle.write(json.dumps(
            {"gid": "VERDICT", "name": "self-attestation verdict",
             "status": att.conclusion, "evidence": {"verdict_hash": att.verdict_hash},
             "evidence_class": "simulated"}, ensure_ascii=False,
            sort_keys=True) + "\n")
    return path


def _ensure_dir(path: str) -> None:
    if path and not os.path.isdir(path):
        os.makedirs(path)
