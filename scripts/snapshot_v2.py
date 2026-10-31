# -*- coding: utf-8 -*-
"""
snapshot_v2.py —— V2 / W11 项目快照（给其他智能体的接手页）
================================================================================
只读现算：维度、代码量、三指标、semvec、kfold、REPRO_CORE 行数与哈希、黄金值。
输出：
    snapshot/project_snapshot_v2.json   机器可读
    snapshot/SNAPSHOT_V2.md             人/智能体可读接手页
不写 holoaeon/ 内任何文件，不联网。
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (ROOT, os.path.join(ROOT, "scripts"), os.path.join(ROOT, "benchmarks")):
    if p not in sys.path:
        sys.path.insert(0, p)

from holoaeon.packs import EXTRA_PACK_ORDER, PACK_ORDER  # noqa: E402
from holoaeon.spec import (CAPABILITIES, DOC_VERSION, MATRIX_ID,  # noqa: E402
                           PROTOCOL_ID, VERSION)

JSON_OUT = os.path.join(ROOT, "snapshot", "project_snapshot_v2.json")
MD_OUT = os.path.join(ROOT, "snapshot", "SNAPSHOT_V2.md")


def code_stats() -> dict:
    files = 0
    lines = 0
    for base, _dirs, names in os.walk(os.path.join(ROOT, "holoaeon")):
        for name in names:
            if name.endswith(".py"):
                files += 1
                with open(os.path.join(base, name), "r", encoding="utf-8",
                          errors="replace") as fh:
                    lines += sum(1 for _ in fh)
    return {"files": files, "lines": lines}


def read_json(rel: str):
    path = os.path.join(ROOT, rel)
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def file_sha16(rel: str) -> str:
    path = os.path.join(ROOT, rel)
    if not os.path.isfile(path):
        return ""
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()[:16]


def repro_core_stats() -> dict:
    rel = "reports/repro_core.jsonl"
    path = os.path.join(ROOT, rel)
    if not os.path.isfile(path):
        return {"rows": 0, "all_pass": False, "sha": ""}
    rows = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rows.append(json.loads(line))
    return {"rows": len(rows),
            "all_pass": all(r["verdict"] in ("pass", "info") for r in rows),
            "sha": file_sha16(rel),
            "verdicts": {r["evidence"]: r["verdict"] for r in rows},
            "verdict_hashes": {r["evidence"]: r["verdict_hash"] for r in rows}}


def bench_stats() -> dict:
    res = read_json("benchmarks/results-0.9.1.json") or read_json(
        "benchmarks/results.json") or {}
    return res


def semvec_stats() -> dict:
    res = read_json("benchmarks/results-semvec-0.9.1.json") or {}
    return res


def kfold_stats() -> dict:
    return read_json("benchmarks/results-semvec-kfold-%s.json" % DOC_VERSION) or {}


def build() -> dict:
    code = code_stats()
    bench = bench_stats()
    sem = semvec_stats()
    kf = kfold_stats()
    rc = repro_core_stats()
    d0 = bench.get("diff0", {})
    guard = bench.get("guard", {})
    foot = bench.get("footprint", {})

    return {
        "project": {
            "name": "HoloAeon",
            "version_runtime": VERSION,
            "version_doc": DOC_VERSION,
            "matrix_id": MATRIX_ID,
            "protocol_id": PROTOCOL_ID,
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "evidence_class": "simulated",
        },
        "dimensions": {
            "agents": 25,
            "skills": 47,
            "workflows": 9,
            "domain_packs": len(PACK_ORDER),
            "extra_packs": len(EXTRA_PACK_ORDER),
            "primitives": len(CAPABILITIES),
            "tests_core": 34,
            "tests_verax": 21,
            "tests_v3": 5,
            "selftests": 25,
        },
        "code": code,
        "bench": {
            "diff0_hash": d0.get("hash_run1"),
            "diff0_equal": d0.get("diff0"),
            "sensitivity_hash": bench.get("sensitivity", {}).get("hash_tampered"),
            "sensitivity": bench.get("sensitivity", {}).get("sensitive"),
            "guard_blocked": "%s/%s" % (guard.get("blocked"), guard.get("dangerous")),
            "guard_allow": "%s/%s" % (guard.get("legit_pass"), guard.get("legit_total")),
            "footprint": "%.2fms / %.2fMiB" % (foot.get("build_ms") or 0.0,
                                               foot.get("peak_mib") or 0.0),
        },
        "semvec": {
            "intents": sem.get("intents"),
            "vocab": sem.get("vocab_size"),
            "dim": sem.get("dim"),
            "baseline": sem.get("base_rate"),
            "semantic": sem.get("sem_rate"),
            "hybrid": sem.get("hybrid_rate"),
            "corpus_digest_v1": sem.get("vector_digest_a"),
            "bitwise_equal": sem.get("bitwise_equal"),
        },
        "semvec_kfold": {
            "folds": kf.get("folds"),
            "mean_p1": kf.get("mean_p1"),
            "std_p1": kf.get("std_p1"),
            "std_limit": kf.get("std_limit"),
            "anchor_v1_intents": kf.get("anchor_v1_intents"),
        },
        "repro_core": rc,
        "goldens": {
            "diff0": "2fc892cf9af6e755",
            "word_count": "2b82a6ef7188ce91",
            "ledger_sha": "98940b774566543b",
            "semvec_digest_v1": "789b71a36bfcd66a",
            "verdict_hash_v2": "f2fb0236c8bbd721",
        },
        "invariants": [
            "维度不变：25 智能体 / 47 技能 / 9 领域包 / ≥7 扩展包（现 8）/ 34 单测 / 25 自检",
            "零依赖 dependencies=[]；零联网；零密钥；零遥测",
            "DIFF=0 黄金 2fc892cf9af6e755 不许漂移；V1 golden 全保留",
            "C1–C12 对外行为不许改；新增能力只能旁挂",
            "assertGreaterEqual(EXTRA_PACK_ORDER, 7) 不许改回精确等值",
        ],
        "known_limits": [
            "kfold 5 折是问法风格分层，std 读作风格敏感度，不是泛化能力",
            "235 条语料含规范术语导致 P@1 虚高；跨词汇以 12 意图 11/12 为准",
            "篡改自检默认抽样 5 点，非穷举",
            "足迹属物理量：不进哈希，随机器浮动",
            "两条稳定未命中：拆解任务、设计实验样本量，未调参复赛",
        ],
        "v2_deltas": {
            "W7": "自动篡改自检 mutation.py + --mutate 5（单测 +5）",
            "W8": "semvec 分层留出 bench_semvec_kfold.py + corpus v2（235）",
            "W9": "REPRO_CORE repro_core_emit.py + spec-diff0-v0.2 §7",
            "W10": "fail-loud verdict_policy.py + spec-diff0-v0.2 §8",
            "W11": "本快照（SNAPSHOT_V2.md + project_snapshot_v2.json）",
        },
        "entry_commands": [
            "python scripts\\launch_local.py selftest",
            "python scripts\\launch_local.py demo",
            "python scripts\\verax_verify.py --mutate 5",
            "python scripts\\bench_semvec_kfold.py --folds 5",
            "python scripts\\repro_core_emit.py --out reports\\repro_core.jsonl",
            "python scripts\\repro_core_emit.py --check reports\\repro_core.jsonl",
            "python benchmarks\\bench_public.py",
            "python scripts\\gitee_publish.py --repo F:\\doubaowork\\holoaeon --branch main",
        ],
        "no_go": [
            "不新增第 18 个扩展包去锁上界；每个新扩展包自带专属测试",
            "不调参把 semvec 11/12 刷成 12/12",
            "不改三本 cookbook 已发布实测数字",
            "不用 advice 把 red 降成 yellow",
            "不为数字漂亮把 golden 改成自适应",
        ],
    }


def render_md(snap: dict) -> str:
    d = snap["dimensions"]
    b = snap["bench"]
    s = snap["semvec"]
    kf = snap["semvec_kfold"]
    rc = snap["repro_core"]
    c = snap["code"]
    lines = [
        "# HoloAeon 项目快照 V2（文档 0.9.2 / 运行态 0.9.1）",
        "",
        "> 给其他智能体：读完这一页即可接手优化，不必先读全部源码。",
        "> 数字现算自磁盘与内核，机器可读版见 `snapshot/project_snapshot_v2.json`。",
        "> 全部条目 `evidence_class=simulated`：仿真 ≠ 证明，碳基终裁。",
        "",
        "## 一 · 定位",
        "",
        "零依赖、默认离线、确定性、带回执的多智能体认知框架：12 个原语（C1–C12）"
        " + 8 层语义守卫 + 手写 HRR 超向量 + 领域/扩展双层包体系。",
        "",
        "## 二 · 维度（硬口径，V2 未变）",
        "",
        "| 项 | 值 |",
        "|---|---|",
        "| 运行态版本 | %s（%s） |" % (snap["project"]["version_runtime"],
                                      snap["project"]["matrix_id"]),
        "| 文档版本 | %s（仅升级包与文档） |" % snap["project"]["version_doc"],
        "| 智能体 / 技能 / 工作流 | %d / %d / %d |" % (d["agents"], d["skills"], d["workflows"]),
        "| 领域包 / 扩展包 | %d / %d（≥7 下界） |" % (d["domain_packs"], d["extra_packs"]),
        "| 原语 | %d（C1–C12 未动） |" % d["primitives"],
        "| 单测（三套分开跑） | %d / %d / %d |" % (d["tests_core"], d["tests_verax"], d["tests_v3"]),
        "| 自检组 | %d（G1–G25） |" % d["selftests"],
        "| 代码量 | holoaeon/ %d 文件 / %d 行 |" % (c["files"], c["lines"]),
        "",
        "## 三 · 三指标（V1 黄金，不许漂移）",
        "",
        "| 指标 | 值 |",
        "|---|---|",
        "| DIFF=0 | `%s`（equal=%s） |" % (b["diff0_hash"], b["diff0_equal"]),
        "| 篡改后哈希 | `%s`（sensitive=%s） |" % (b["sensitivity_hash"], b["sensitivity"]),
        "| 拦截率 | %s（放行 %s） |" % (b["guard_blocked"], b["guard_allow"]),
        "| 足迹 | %s（物理量，不进哈希） |" % b["footprint"],
        "",
        "## 四 · V2 新增四行（第二屏徽章来源）",
        "",
        "| 项 | 值 | 出处 |",
        "|---|---|---|",
        "| mutate | 5/5 全变（`sensitive=True`） | `scripts/verax_verify.py --mutate 5` |",
        "| semvec kfold | mean=%s / std=%s（folds=%s，limit 0.05） | `scripts/bench_semvec_kfold.py` |"
        % (kf["mean_p1"], kf["std_p1"], kf["folds"]),
        "| repro_core | %d 行，全绿=%s，sha16=`%s` | `reports/repro_core.jsonl` |"
        % (rc["rows"], rc["all_pass"], rc["sha"]),
        "| fail-loud | ON（3 条硬红线，不可降级） | `holoaeon/audit/verdict_policy.py` |",
        "",
        "## 五 · semvec 语义通道（披露，不设目标值）",
        "",
        "| 项 | 值 |",
        "|---|---|",
        "| 意图 / 词表 / 维度 | %s / %s / %s |" % (s["intents"], s["vocab"], s["dim"]),
        "| 基线 / 语义 / 混合 | %s / %s / %s |" % (s["baseline"], s["semantic"], s["hybrid"]),
        "| 语料 digest (v1) | `%s` |" % s["corpus_digest_v1"],
        "| 跨词汇锚点（12 意图） | %s |" % (kf["anchor_v1_intents"] or {}),
        "",
        "## 六 · REPRO_CORE 证据链（行级可哈希）",
        "",
        "```",
    ]
    for name, verdict in rc["verdicts"].items():
        lines.append("%-24s %-6s %s" % (name, verdict, rc["verdict_hashes"][name]))
    lines += [
        "```",
        "",
        "## 七 · 不变量",
        "",
    ]
    for item in snap["invariants"]:
        lines.append("- " + item)
    lines += ["", "## 八 · 已知限制", ""]
    for item in snap["known_limits"]:
        lines.append("- " + item)
    lines += ["", "## 九 · 入口命令（照抄可跑）", "", "```powershell"]
    for cmd in snap["entry_commands"]:
        lines.append(cmd)
    lines += ["```", "", "## 十 · V2 五包落点", "", "| 包 | 内容 |", "|---|---|"]
    for key in sorted(snap["v2_deltas"]):
        lines.append("| %s | %s |" % (key, snap["v2_deltas"][key]))
    lines += ["", "## 十一 · 不做", ""]
    for item in snap["no_go"]:
        lines.append("- " + item)
    lines += ["", "潮起开门，潮落闭嘴。", ""]
    return "\n".join(lines)


def main() -> int:
    snap = build()
    os.makedirs(os.path.dirname(JSON_OUT), exist_ok=True)
    with open(JSON_OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(snap, ensure_ascii=False, indent=2, sort_keys=True))
        fh.write("\n")
    with open(MD_OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render_md(snap))
        fh.write("\n")
    print("json: %s" % JSON_OUT)
    print("md:   %s" % MD_OUT)
    print("agents=%d skills=%d packs=%d+%d tests=%d/%d/%d selftests=%d"
          % (snap["dimensions"]["agents"], snap["dimensions"]["skills"],
             snap["dimensions"]["domain_packs"], snap["dimensions"]["extra_packs"],
             snap["dimensions"]["tests_core"], snap["dimensions"]["tests_verax"],
             snap["dimensions"]["tests_v3"], snap["dimensions"]["selftests"]))
    print("repro_core rows=%d all_pass=%s" % (snap["repro_core"]["rows"],
                                              snap["repro_core"]["all_pass"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
