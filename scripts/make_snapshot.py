# -*- coding: utf-8 -*-
"""
make_snapshot.py —— 产出本项目快照（供其他智能体读取与加入优化）
================================================================================
产物：
    snapshot/SNAPSHOT.md          人读：维度、入口、不变量、实测数字、如何接力
    snapshot/project_snapshot.json 机器读：同一份事实的结构化版本（键序稳定）

口径：全部数字现算（扫描磁盘 + 跑内核），不复制历史文档里的旧值；
不含时间戳、不含绝对路径以外的隐私字段，两次运行除 generated_at 外逐字节一致。
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

OUT_DIR = os.path.join(ROOT, "snapshot")


# ------------------------------------------------------------ 扫描
def py_stats(base: str) -> dict:
    files = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = sorted(d for d in dirnames if d not in ("__pycache__",))
        for fn in sorted(filenames):
            if fn.endswith(".py"):
                p = os.path.join(dirpath, fn)
                with open(p, encoding="utf-8") as fh:
                    files.append({"path": os.path.relpath(p, ROOT).replace("\\", "/"),
                                  "lines": len(fh.read().splitlines())})
    return {"files": len(files), "lines": sum(f["lines"] for f in files), "detail": files}


def tree(base: str, depth: int = 2) -> list:
    rows = []
    for name in sorted(os.listdir(base)):
        p = os.path.join(base, name)
        if name in ("__pycache__", ".git"):
            continue
        rel = os.path.relpath(p, ROOT).replace("\\", "/")
        if os.path.isdir(p):
            rows.append({"path": rel + "/", "type": "dir",
                         "files": len([x for x in os.listdir(p) if not x.startswith("__")])})
        else:
            rows.append({"path": rel, "type": "file", "bytes": os.path.getsize(p)})
    return rows


def dims() -> dict:
    from holoaeon.kernel import Kernel
    from holoaeon.packs import EXTRA_PACK_ORDER, PACK_ORDER, get_extra_pack, get_pack
    from holoaeon.spec import (DATE, MATRIX_ID, PROTOCOL_ID, RUNTIME_ID,
                               VERSION)

    k = Kernel()
    for key in PACK_ORDER:
        get_pack(key).install(k)
    core_agents = len(k.agents)
    core_skills = len(k.skills.names())
    core_workflows = sum(len(get_pack(x).workflows) for x in PACK_ORDER)
    packs = []
    for key in PACK_ORDER:
        p = get_pack(key)
        packs.append({"key": key, "kind": "domain", "skills": len(p.skills),
                      "agents": len(p.roles), "workflows": len(p.workflows)})
    extras = []
    for key in EXTRA_PACK_ORDER:
        p = get_extra_pack(key)
        extras.append({"key": key, "kind": "extra", "skills": len(p.skills),
                       "agents": len(p.roles), "workflows": len(p.workflows)})
    full = Kernel()
    for key in PACK_ORDER:
        get_pack(key).install(full)
    for key in EXTRA_PACK_ORDER:
        get_extra_pack(key).install(full)
    return {
        "version": VERSION, "runtime_id": RUNTIME_ID,
        "matrix_id": MATRIX_ID, "protocol_id": PROTOCOL_ID, "date": DATE,
        "core": {"agents": core_agents, "skills": core_skills,
                 "workflows": core_workflows},
        "full": {"agents": len(full.agents), "skills": len(full.skills.names())},
        "domain_packs": packs, "extra_packs": extras,
    }


def bench() -> dict:
    path = os.path.join(ROOT, "benchmarks", "results-%s.json" % _ver())
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        r = json.load(fh)
    return {
        "diff0_hash": r["diff0"]["hash_run1"],
        "diff0": r["diff0"]["diff0"],
        "sensitivity": r.get("sensitivity", {}).get("sensitive"),
        "guard_rate": r["guard"]["interception_rate"],
        "legit_pass": "%d/%d" % (r["guard"]["legit_pass"], r["guard"]["legit_total"]),
        "build_ms": r["footprint"]["build_ms"],
        "peak_mib": r["footprint"]["peak_mib"],
    }


def _ver() -> str:
    from holoaeon.spec import VERSION
    return VERSION


def semvec() -> dict:
    path = os.path.join(ROOT, "benchmarks", "results-semvec-%s.json" % _ver())
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        r = json.load(fh)
    return {
        "intents": r["intents"], "vocab": r["vocab_size"], "dim": r["dim"],
        "base_correct": r["base_correct"], "hybrid_correct": r["hybrid_correct"],
        "bitwise_equal": r["bitwise_equal"], "fit_ms": r["fit_ms"],
        "corpus_docs": r.get("corpus_docs"), "digest": r.get("vector_digest_a"),
    }


def entry_commands() -> list:
    return [
        "python scripts/launch_local.py status",
        "python scripts/launch_local.py demo",
        "python scripts/launch_local.py run \"统计字数：HoloAeon 是零依赖的确定性多智能体认知框架。\"",
        "python scripts/launch_local.py hotplug optimization",
        "python scripts/launch_local.py selftest",
        "python -m unittest discover -s tests",
        "python -m unittest discover -s tests\\verax",
        "python -m unittest discover -s tests\\v3",
        "python scripts/redline_scan.py",
        "python scripts/verax_verify.py --out reports",
        "python benchmarks/bench_public.py",
        "python scripts/bench_semvec.py",
        "python scripts/ledger_view.py --sample data/ledger_sample.jsonl",
    ]


def invariants() -> list:
    return [
        "零依赖：pyproject.toml 的 dependencies = []，只用 Python 标准库",
        "默认离线：不开端口、不联网、不读密钥、不写遥测",
        "确定性：DIFF=0 哈希两次一致，且篡改敏感性自检通过（否则视为空转）",
        "可审计：每条裁决含 action/layer/reason，回执强制 evidence_class",
        "安全边界：L1–L8 八层守卫，20 条标准集拦截率 100%",
        "诚实纪律：simulated 是默认档，measured 必须带来源与测量时刻",
        "维度不变：25 智能体 / 47 技能 / 9 领域包 + 7 扩展包 / 34 单测 / 24 自检",
    ]


def snapshot() -> dict:
    hs = py_stats(os.path.join(ROOT, "holoaeon"))
    return {
        "project": {"name": "HoloAeon", "license": "Apache-2.0",
                    "repo": "https://github.com/weideyouni/holoaeon",
                    "root_layout": tree(ROOT)},
        "code": {"package": hs, "benchmarks_files": py_stats(os.path.join(ROOT, "benchmarks"))
                 if os.path.isdir(os.path.join(ROOT, "benchmarks")) else {}},
        "dimensions": dims(),
        "bench": bench(),
        "semvec": semvec(),
        "entry_commands": entry_commands(),
        "invariants": invariants(),
        "no_go": [
            "不新增第 17 个领域包",
            "不为追 star 抄编排框架（LangGraph/MetaGPT/CrewAI 的战场不进来）",
            "不把 simulated 写成实测",
            "不破坏 dependencies=[]、不引入网络、不破既有单测与自检",
        ],
        "how_to_join": [
            "读 snapshot/SNAPSHOT.md 的「不变量」与「入口」，先在本地跑通 3 条命令",
            "改动前用 tests\\ + selftest + redline 三闸确认基线全绿",
            "任何 DIFF=0 相关改动必须同时给篡改敏感性自检",
            "文档里的数字必须能在 benchmarks/results-*.json 找到出处，否则标 simulated",
        ],
        "known_limits": [
            "semvec 语义通道：语料只取 %s 条技能自述（与 docs/ 解耦，改文档不漂移）；"
            "12 条固定意图混合路由 %s/%s = %.1f%% 误路由 %s/%s（同集调参，含过拟合风险）；"
            "留出集 6 条中 2 条期望名不存在，余 4 条命中 2 条 —— 泛化未验证"
            % (semvec().get("corpus_docs"),
               semvec().get("hybrid_correct"), semvec().get("intents"),
               (semvec().get("hybrid_correct") or 0) * 100.0 / (semvec().get("intents") or 1),
               (semvec().get("intents") or 0) - (semvec().get("hybrid_correct") or 0),
               semvec().get("intents")),
            "领域包产骨架不产成稿；账本可视化是静态 HTML，不是托管平台",
            "Apache-2.0 不保护功能，只保护标准与证据；双许可决策留给构建者",
        ],
    }


def write(snap: dict) -> dict:
    os.makedirs(OUT_DIR, exist_ok=True)
    import time as _time
    snap["generated_at"] = _time.strftime("%Y-%m-%dT%H:%M:%SZ", _time.gmtime())
    jpath = os.path.join(OUT_DIR, "project_snapshot.json")
    with open(jpath, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(snap, ensure_ascii=False, indent=2, sort_keys=True) + "\n")

    d = snap["dimensions"]
    c = snap["code"]["package"]
    b = snap["bench"]
    s = snap["semvec"]
    L = [
        "# HoloAeon 项目快照（%s）" % d["version"],
        "",
        "> 给其他智能体：读完这一页你就能接手优化，不需要先读全部源码。",
        "> 所有数字现算自磁盘与内核，出处见 `snapshot/project_snapshot.json`。",
        "",
        "## 一 · 这是什么",
        "",
        "HoloAeon 是一个**零依赖、默认离线、确定性、带回执**的多智能体认知框架：",
        "12 个正交原语（C1–C12）+ 8 层语义守卫 + 手写 HRR 超向量 + 领域/扩展双层包体系。",
        "一句话定位：**一个带回执的确定性内核**。",
        "",
        "## 二 · 维度（不许改的硬口径）",
        "",
        "| 项 | 值 |",
        "|---|---|",
        "| 版本 | %s（%s） |" % (d["version"], d["runtime_id"]),
        "| 核心包 | %d 智能体 / %d 技能 / %d 工作流 |"
        % (d["core"]["agents"], d["core"]["skills"], d["core"]["workflows"]),
        "| 领域包 | %d 个（%s） |"
        % (len(d["domain_packs"]), " / ".join(p["key"] for p in d["domain_packs"])),
        "| 扩展包 | %d 个（%s） |"
        % (len(d["extra_packs"]), " / ".join(p["key"] for p in d["extra_packs"])),
        "| 全装后 | %d 智能体 / %d 技能 |"
        % (d["full"]["agents"], d["full"]["skills"]),
        "| 代码量 | holoaeon/ %d 文件 / %d 行 |" % (c["files"], c["lines"]),
        "",
        "## 三 · 三个数字（证据入口）",
        "",
        "| 指标 | 值 | 出处 |",
        "|---|---|---|",
        "| DIFF=0 | `%s`（一致=%s，敏感性=%s） |"
        % (b.get("diff0_hash", "-"), b.get("diff0"), b.get("sensitivity")),
        "| 守卫拦截率 | %s%%（合法 %s 放行） |"
        % (int(b.get("guard_rate", 0) * 100), b.get("legit_pass", "-")),
        "| 足迹 | %s ms / %s MiB |" % (b.get("build_ms"), b.get("peak_mib")),
        "",
        "## 四 · 语义通道实测（披露，不设目标值）",
        "",
        "| 项 | 值 |",
        "|---|---|",
        "| 意图数 / 词表 / 维度 | %s / %s / %s |"
        % (s.get("intents"), s.get("vocab"), s.get("dim")),
        "| 基线正确 / 混合正确 | %s / %s |"
        % (s.get("base_correct"), s.get("hybrid_correct")),
        "| 两次 fit 逐位一致 | %s |" % s.get("bitwise_equal"),
        "| fit 耗时 | %s ms |" % s.get("fit_ms"),
        "",
        "## 五 · 入口命令（照抄可跑）",
        "",
        "```powershell",
    ] + snap["entry_commands"] + [
        "```",
        "",
        "## 六 · 不变量（破了就不算 HoloAeon）",
        "",
    ] + ["- " + x for x in snap["invariants"]] + [
        "",
        "## 七 · 明确不做",
        "",
    ] + ["- " + x for x in snap["no_go"]] + [
        "",
        "## 八 · 如何加入优化",
        "",
    ] + ["%d. %s" % (i + 1, x) for i, x in enumerate(snap["how_to_join"])] + [
        "",
        "## 九 · 已知限制（先看这里，别重复踩）",
        "",
    ] + ["- " + x for x in snap["known_limits"]] + [
        "",
        "## 十 · 目录骨架",
        "",
        "| 路径 | 类型 | 说明 |",
        "|---|---|---|",
    ]
    for row in snap["project"]["root_layout"]:
        L.append("| `%s` | %s | %s |" % (
            row["path"], row["type"],
            ("%d 项" % row["files"]) if row["type"] == "dir" else ("%d B" % row["bytes"])))
    L += ["", "--", "快照由 `scripts/make_snapshot.py` 生成，重跑即可刷新；不含只读机密。", ""]
    mpath = os.path.join(OUT_DIR, "SNAPSHOT.md")
    with open(mpath, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(L))
    return {"json": jpath, "md": mpath,
            "sha16": hashlib.sha256(
                json.dumps(snap, ensure_ascii=False, sort_keys=True).encode("utf-8")
            ).hexdigest()[:16]}


def main() -> int:
    snap = snapshot()
    out = write(snap)
    print("snapshot json: %s" % out["json"])
    print("snapshot md  : %s" % out["md"])
    print("snapshot_sha16=%s" % out["sha16"])
    print("code: holoaeon/ %d files / %d lines"
          % (snap["code"]["package"]["files"], snap["code"]["package"]["lines"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
