# -*- coding: utf-8 -*-
"""machine_tool — 工程机床（V25 · 跨线程稳定执行总装）

第一性原理
==========
工程机床的目的 = **跨线程稳定执行**；HoloAeon 的本质 = **确定性规则认知协作**。
机床八段流水线的每一段都是确定性规则（探针、闸门表、台账一致性判断），
没有一处依赖 LLM —— 天然 HoloAeon 化，零妥协。

分层（红线决定，不是设计偏好）
==============================
`holoaeon/` 包内**禁止** `subprocess` 与任何外部执行（`redline.py`: FORBIDDEN_MODULES
含 subprocess、FORBIDDEN_CALLS 含 run/system/popen）。因此本模块分两层：

* **决策层（本文件）**：纯标准库、只读、无任何外部执行。
  git 身份用 `.git` 文件直读（HEAD → refs / packed-refs），不 shell out；
  闸门只做「登记 + 判定」，**真跑由执行层注入结果**。
* **执行层（`scripts/machine_tool_run.py`）**：运维脚本目录（红线不扫），
  负责真跑 git status 与七道闸门，把结果喂回本模块判定，输出 verdict。

八段流水线（S1-S8，顺序固化）
============================
S1 baseline        基线检查：git 身份（文件直读）+ VERSION / DOC_VERSION / EXTRA_PACK_ORDER
S2 quartet         四人组定调：五步协议 + 涌现条件确定性校验
S3 lab_verify      实验田验证：小步慢走（执行层显式触发）
S4 feed_build      投喂包拼装：封口密语 + diff0 声明 + 验证清单
S5 handoff         执行交接：只登记不执行（总监不碰源码，边界清晰）
S6 verify_gate     验证闸门：结果注入 + 期望比对 → verdict
S7 five_site       五地台账：全一致才收口（S4 走归档库口径）
S8 memory_backfill 记忆回填：append-only

使用
====
    python -m holoaeon.machine_tool status     # 只读探针（JSON）
    python -m holoaeon.machine_tool boot       # 开机面板（一屏对齐）
    python -m holoaeon.machine_tool gates      # 闸门表
    python -m holoaeon.machine_tool redlines   # 10 条红线
    python -m holoaeon.machine_tool pipeline   # S1-S8
    python -m holoaeon.machine_tool tick V26   # 推进一个 tick
    python scripts/machine_tool_run.py check   # 真跑闸门（执行层）

设计纪律
========
* 只读为默认模式；写段（S3/S4/S8）必须显式调用，绝不隐式落盘。
* 不新增扩展包（模块级，先例 `butler_os.py` V12），`EXTRA_PACK_ORDER` 不因子系统增长。
* 本文件不参与 ReproHash → diff0 零漂移风险。

封口密语：潮起开门，潮落闭嘴。
证据等级：evidence_class=simulated，仿真≠证明，碳基终裁。
"""
from __future__ import annotations

import json
import os
import re
import sys
import time

SEAL = "潮起开门，潮落闭嘴"

# ---------------------------------------------------------------------------
# 红线（10 条，与 V24 收口态逐条对账）
# ---------------------------------------------------------------------------
RED_LINES = [
    "BUILTIN_LAYERS（L1-L8）一个字符不改",
    "VERSION='0.9.1' 冻结",
    "layers=8 不改",
    "PACK_ORDER=9 不动（核心 25 agents / 47 skills）",
    "graph.py / scheduler.py / hypervector.py 不碰",
    "kernel.py 的 submit 不改",
    "好嘞预案源码不碰 —— 只通过投喂包交豆包执行",
    "diff0 不漂移（判据=bench 16 步 workload 连跑一致性）",
    "升级纪律：小步慢走，一次只改一个小点",
    "记忆 append-only，只追加不删除",
]

# ---------------------------------------------------------------------------
# 八段流水线（D-01：固化顺序，不得跳段）
# ---------------------------------------------------------------------------
PIPELINE = [
    ("S1", "baseline", "基线检查：git 身份（文件直读）+ VERSION + EXTRA_PACK_ORDER"),
    ("S2", "quartet", "四人组定调：五步协议 + 涌现条件校验"),
    ("S3", "lab_verify", "实验田验证：小步慢走（执行层触发）"),
    ("S4", "feed_build", "投喂包拼装：封口 + diff0 声明 + 验证清单"),
    ("S5", "handoff", "执行交接：只登记不执行"),
    ("S6", "verify_gate", "验证闸门：结果注入 + 期望比对"),
    ("S7", "five_site", "五地台账：全一致才收口"),
    ("S8", "memory_backfill", "记忆回填：append-only"),
]

FIVE_STEP = ["道(P4定义问题)", "法(四人共评)", "术(P3约束)", "器(P2算法)", "升维(P1验证)"]

EMERGENCE_RULES = {"P2xP3_min": 0.7, "P1_min": 0.6, "P4_max": 0.4, "order_min": 0.30}

# 闸门注册表：name -> (argv(相对仓库根，sys.executable 起跑), 期望在输出尾部出现的关键字)
# 本表只是**数据**，不在包内执行；执行层 scripts/machine_tool_run.py 按此真跑。
# bench 默认不跑（会写 benchmarks/ 下的运行时产物），需显式 --bench。
GATES = {
    "selftest": (["-m", "holoaeon.selftest"], "25/25"),
    "v3_gate": (["scripts/v3_gate.py"], "PASS"),
    "unittest_main": (["-m", "unittest", "discover", "-s", "tests"], "OK"),
    "unittest_v3": (["-m", "unittest", "discover", "-s", "tests/v3"], "OK"),
    "unittest_verax": (["-m", "unittest", "discover", "-s", "tests/verax"], "OK"),
    "redline": (["scripts/redline_scan.py"], "零违规"),
    "dimension_lock": (["scripts/check_dimension_lock.py"], "全部一致"),
    "bench_diff0": (["benchmarks/bench_public.py"], "DIFF=0"),
}

BENCH_GATE = "bench_diff0"

# 五地坐标（S4 用归档库口径，S5 用 HF model 仓 sha + 文件数）
FIVE_SITE = [
    ("S1_local", "git rev-parse --short HEAD"),
    ("S2_gitee", "git ls-remote <token-url> refs/heads/main"),
    ("S3_github", "git ls-remote origin refs/heads/main"),
    ("S4_vector_sea", "scripts/check_vector_sea_manifest.py"),
    ("S5_hf", "GET huggingface.co/api/models/weideyouni/holoaeon"),
]


# ---------------------------------------------------------------------------
# 语义通信基座：段间载荷（经络机制）
# ---------------------------------------------------------------------------
class Envelope:
    """段间传递的批次记录：batch / stage / payload / seal / ts。"""

    def __init__(self, batch, stage, payload):
        self.batch = batch
        self.stage = stage
        self.payload = payload
        self.seal = SEAL
        self.ts = time.strftime("%Y-%m-%dT%H:%M:%S")

    def to_dict(self):
        return {"batch": self.batch, "stage": self.stage,
                "payload": self.payload, "seal": self.seal, "ts": self.ts}


# ---------------------------------------------------------------------------
# S1 基线探针（细胞骨架：生命周期起点）。纯文件直读，不调用外部命令。
# ---------------------------------------------------------------------------
class BaselineProbe:
    """从 `.git` 目录直读身份；VERSION / DOC_VERSION / EXTRA_PACK_ORDER 走仓内常量。

    dirty / untracked 需要 git 计算索引，包里算不出来 —— 返回 None 并标注
    `dirty_source="not_probed"`，由执行层 `scripts/machine_tool_run.py` 补齐。
    """

    def __init__(self, repo):
        self.repo = repo

    def probe(self):
        head_full = self.read_head()
        version, doc_version = self.identity()
        extra_count, extra_last = self.extras()
        return {
            "repo": self.repo,
            "head": head_full,
            "head_short": (head_full or "")[:7] or None,
            "tracked_dirty": None,
            "untracked": None,
            "dirty_source": "not_probed",
            "version": version,
            "doc_version": doc_version,
            "extra_packs": extra_count,
            "extra_packs_last": extra_last,
            "seal": SEAL,
            "collected_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }

    # -- git 身份（文件直读） ------------------------------------------------
    def _git_dir(self):
        dot_git = os.path.join(self.repo, ".git")
        if os.path.isdir(dot_git):
            return dot_git
        if os.path.isfile(dot_git):
            try:
                with open(dot_git, "r", encoding="utf-8") as handle:
                    text = handle.read().strip()
            except OSError:
                return None
            if text.startswith("gitdir:"):
                target = text.split(":", 1)[1].strip()
                if not os.path.isabs(target):
                    target = os.path.normpath(os.path.join(self.repo, target))
                return target if os.path.isdir(target) else None
        return None

    @staticmethod
    def _read_text(path):
        try:
            with open(path, "r", encoding="utf-8") as handle:
                return handle.read().strip()
        except OSError:
            return None

    def read_head(self):
        git_dir = self._git_dir()
        if not git_dir:
            return None
        head = self._read_text(os.path.join(git_dir, "HEAD"))
        if not head:
            return None
        if not head.startswith("ref:"):
            return head if re.fullmatch(r"[0-9a-f]{40}", head) else None
        ref = head.split(":", 1)[1].strip()
        loose = os.path.join(git_dir, *ref.split("/"))
        sha = self._read_text(loose)
        if sha and re.fullmatch(r"[0-9a-f]{40}", sha):
            return sha
        packed = self._read_text(os.path.join(git_dir, "packed-refs"))
        if packed:
            for line in packed.splitlines():
                line = line.strip()
                if not line or line.startswith("#") or line.startswith("^"):
                    continue
                parts = line.split()
                if len(parts) == 2 and parts[1] == ref:
                    return parts[0]
        return None

    # -- 身份与扩展包 --------------------------------------------------------
    @staticmethod
    def identity():
        try:
            from . import spec
            return getattr(spec, "VERSION", None), getattr(spec, "DOC_VERSION", None)
        except Exception:
            return None, None

    @staticmethod
    def extras():
        try:
            from .packs import EXTRA_PACK_ORDER
            return len(EXTRA_PACK_ORDER), (EXTRA_PACK_ORDER[-1] if EXTRA_PACK_ORDER else None)
        except Exception:
            return None, None


# ---------------------------------------------------------------------------
# S2 四人组定调（五步协议 + 涌现条件确定性判定）
# ---------------------------------------------------------------------------
class QuartetSession:
    """道→法→术→器→升维；涌现四条件全满足才可开工。"""

    def __init__(self, topic):
        self.topic = topic
        self.records = []

    def record(self, step, speaker, statement):
        item = {"step": step, "speaker": speaker, "statement": statement}
        self.records.append(item)
        return item

    @staticmethod
    def emergence_check(p2, p3, p1, p4, order):
        rules = EMERGENCE_RULES
        product = round(p2 * p3, 4)
        return {
            "emergence": bool(product >= rules["P2xP3_min"]
                              and p1 >= rules["P1_min"]
                              and p4 <= rules["P4_max"]
                              and order > rules["order_min"]),
            "P2xP3": product,
            "P1": p1,
            "P4": p4,
            "order": order,
            "rules": dict(rules),
        }

    @staticmethod
    def five_step():
        return list(FIVE_STEP)


# ---------------------------------------------------------------------------
# S3 实验田验证（执行层触发；本类只承载结构位）
# ---------------------------------------------------------------------------
class LabVerify:
    """记录实验田验证位：执行层真跑后回填结果，不做外部调用。"""

    def __init__(self, lab_repo):
        self.lab_repo = lab_repo
        self.last = None

    def record(self, ok, tail):
        self.last = {"ok": bool(ok), "tail": tail, "lab_repo": self.lab_repo}
        return self.last


# ---------------------------------------------------------------------------
# S4 投喂包拼装（确定性模板，不做自然语言生成）
# ---------------------------------------------------------------------------
class FeedPackageBuilder:
    TEMPLATE = ("# AGENT FEED {batch} · {title}\n\n"
                "> **封口密语**：{seal}\n"
                "> **diff0 声明**：{diff0_note}\n"
                "> **五步设计**：{five_step}\n"
                "> **验证清单**：{checklist}\n")

    def build(self, batch, title, diff0_note, checklist):
        body = self.TEMPLATE.format(
            batch=batch, title=title, seal=SEAL, diff0_note=diff0_note,
            five_step="→".join(FIVE_STEP), checklist=checklist)
        return {"batch": batch, "body": body, "complete": bool(
            SEAL in body and diff0_note in body and checklist in body)}


# ---------------------------------------------------------------------------
# S5 执行交接（只登记，不执行）
# ---------------------------------------------------------------------------
class ExecutorHandoff:
    def __init__(self):
        self.handoffs = []

    def register(self, batch, feed_path):
        if not os.path.exists(feed_path):
            return {"ok": False, "error": "feed package not found", "batch": batch}
        item = {"batch": batch, "feed_path": feed_path, "status": "registered",
                "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
        self.handoffs.append(item)
        return {"ok": True, "batch": batch, "status": "registered"}


# ---------------------------------------------------------------------------
# S6 验证闸门（结果注入 + 期望比对；执行层负责真跑）
# ---------------------------------------------------------------------------
class VerificationGate:
    """按注册表判定；`ingest()` 收执行层结果，`record()` 手工补录。"""

    def __init__(self, include_bench=False):
        self.include_bench = include_bench
        self.results = {}

    def names(self):
        return sorted(k for k in GATES if self.include_bench or k != BENCH_GATE)

    def record(self, name, passed, actual):
        if name not in GATES:
            return {"ok": False, "error": "unknown gate", "name": name}
        self.results[name] = {"passed": bool(passed), "expect": GATES[name][1],
                              "actual": actual}
        return self.results[name]

    def ingest(self, name, returncode, output):
        """收执行层的 (returncode, output)，按注册表期望判 PASS。"""
        if name not in GATES:
            return {"passed": False, "error": "unknown gate", "name": name}
        expect = GATES[name][1]
        tail = (output or "")[-800:]
        passed = bool(returncode == 0 and expect in tail)
        item = {"passed": passed, "expect": expect, "returncode": returncode,
                "actual": tail.strip().splitlines()[-1] if tail.strip() else ""}
        self.results[name] = item
        return item

    def missing(self):
        return [n for n in self.names() if n not in self.results]

    def all_green(self):
        return bool(self.results) and not self.missing() and all(
            item.get("passed") for item in self.results.values())


# ---------------------------------------------------------------------------
# S7 五地台账（S4 用归档口径，不参与 sha 一致性）
# ---------------------------------------------------------------------------
class FiveSiteLedger:
    SITES = ["S1_local", "S2_gitee", "S3_github", "S4_vector_sea", "S5_hf"]
    ARTIFACT_SITES = ("S4_vector_sea",)

    def __init__(self):
        self.entries = {}

    def report(self, site, head, mismatch=None):
        ok = mismatch is None or mismatch == []
        self.entries[site] = {"head": head, "ok": ok, "mismatch": mismatch}
        return self.entries[site]

    def consistent(self):
        if len(self.entries) != len(self.SITES):
            return False
        if not all(v["ok"] for v in self.entries.values()):
            return False
        heads = {v["head"] for k, v in self.entries.items()
                 if k not in self.ARTIFACT_SITES}
        return len(heads) == 1


# ---------------------------------------------------------------------------
# S8 记忆回填（皮肤机制：只追加，不删除）
# ---------------------------------------------------------------------------
class MemoryBackfill:
    def __init__(self, path):
        self.path = path

    def append(self, text):
        parent = os.path.dirname(self.path)
        if parent and not os.path.isdir(parent):
            os.makedirs(parent)
        payload = text if text.endswith("\n") else text + "\n"
        with open(self.path, "a", encoding="utf-8") as handle:
            handle.write(payload)
        with open(self.path, "r", encoding="utf-8") as handle:
            return {"ok": True, "path": self.path, "size": len(handle.read())}


# ---------------------------------------------------------------------------
# 总装
# ---------------------------------------------------------------------------
class MachineTool:
    """八段流水线总装：只读段随时可跑；写段与真跑由调用方显式触发。"""

    def __init__(self, repo, lab_repo=None, include_bench=False):
        self.repo = repo
        self.lab_repo = lab_repo
        self.probe = BaselineProbe(repo)
        self.gate = VerificationGate(include_bench=include_bench)
        self.ledger = FiveSiteLedger()
        self.handoff = ExecutorHandoff()
        self.lab = LabVerify(lab_repo) if lab_repo else None

    def red_lines(self):
        return list(RED_LINES)

    def pipeline(self):
        return [stage + " " + name + " — " + desc for stage, name, desc in PIPELINE]

    def status(self):
        base = self.probe.probe()
        base["red_line_count"] = len(RED_LINES)
        base["pipeline_stages"] = len(PIPELINE)
        base["gate_names"] = self.gate.names()
        return base

    def assembly(self):
        """全装配计数（含全部扩展包，非冻结口径；核心九包另算）。"""
        try:
            from .frontend_adapter import build_kernel
            kernel = build_kernel()
            agents = len(getattr(kernel, "agents", {}) or {})
            skills_obj = getattr(kernel, "skills", None)
            if hasattr(skills_obj, "names"):
                skills = len(skills_obj.names())
            else:
                skills = len(skills_obj or {})
            return {"agents": agents, "skills": skills, "source": "build_kernel"}
        except Exception as exc:
            return {"agents": None, "skills": None, "error": str(exc)}

    def boot(self):
        base = self.status()
        return {
            "identity": {"VERSION": base.get("version"),
                         "DOC_VERSION": base.get("doc_version"),
                         "extra_packs": base.get("extra_packs"),
                         "extra_packs_last": base.get("extra_packs_last")},
            "assembly": self.assembly(),
            "commit": {"head_short": base.get("head_short"),
                       "tracked_dirty": base.get("tracked_dirty"),
                       "untracked": base.get("untracked"),
                       "dirty_source": base.get("dirty_source")},
            "gates_expected": {k: GATES[k][1] for k in self.gate.names()},
            "pipeline": self.pipeline(),
            "five_site": [{"site": s, "probe": p} for s, p in FIVE_SITE],
            "seal": SEAL,
        }

    def tick(self, batch):
        """一个 tick = S1 只读探测 + S2 定调骨架。"""
        base = self.probe.probe()
        quartet = QuartetSession(batch)
        quartet.record(FIVE_STEP[0], "P4", "定义问题：本批目标与约束")
        return {"envelope": Envelope(batch, "S1", base).to_dict(),
                "five_step": quartet.five_step(),
                "emergence_check": quartet.emergence_check(0.85, 0.85, 0.85, 0.30, 0.5237),
                "note": "写段（S3/S4/S8）与真跑闸门需显式触发"}

    def check(self):
        """判定，不执行。结果需由执行层 ingest；缺失即 NEEDS_RUNNER。"""
        missing = self.gate.missing()
        verdict = "PASS"
        if missing:
            verdict = "NEEDS_RUNNER"
        elif not self.gate.all_green():
            verdict = "FAIL"
        return {"verdict": verdict, "all_green": self.gate.all_green(),
                "missing_gates": missing, "results": self.gate.results,
                "batch_probe": self.probe.probe(),
                "red_line_count": len(RED_LINES),
                "note": "真跑请用 python scripts/machine_tool_run.py check"}


def _print_panels(panels):
    print("=" * 62)
    print(" holoaeon 工程机床 · 开机面板（%s）" % SEAL[:4])
    print("=" * 62)
    ident = panels["identity"]
    print("[身份] VERSION=%s | DOC_VERSION=%s | extras=%s(末位 %s)" % (
        ident["VERSION"], ident["DOC_VERSION"], ident["extra_packs"], ident["extra_packs_last"]))
    asm = panels["assembly"]
    if asm.get("agents"):
        print("[装配] 全装配 agents=%s skills=%s（含全部扩展包，非冻结口径）" % (
            asm["agents"], asm["skills"]))
    commit = panels["commit"]
    print("[提交] %s | tracked_dirty=%s | untracked=%s | 来源=%s" % (
        commit["head_short"], commit["tracked_dirty"], commit["untracked"],
        commit["dirty_source"]))
    print("[闸门] %d 道：%s" % (len(panels["gates_expected"]),
                              ", ".join(panels["gates_expected"].keys())))
    print("[流水线] %d 段：" % len(panels["pipeline"]))
    for line in panels["pipeline"]:
        print("    " + line)
    print("[五地] 坐标 %d 处（S4 走归档库，S5 走 HF model 仓）" % len(panels["five_site"]))
    print("[封口] %s" % panels["seal"])


def main(argv=None):
    argv = list(argv if argv is not None else sys.argv[1:])
    cmd = argv[0] if argv else "status"
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tool = MachineTool(repo, include_bench=("--bench" in argv))
    if cmd == "status":
        print(json.dumps(tool.status(), ensure_ascii=False, indent=2))
    elif cmd == "boot":
        _print_panels(tool.boot())
    elif cmd == "check":
        print(json.dumps(tool.check(), ensure_ascii=False, indent=2))
    elif cmd == "redlines":
        for index, line in enumerate(tool.red_lines(), 1):
            print("%d. %s" % (index, line))
    elif cmd == "pipeline":
        for line in tool.pipeline():
            print(line)
    elif cmd == "gates":
        for key in tool.gate.names():
            print("%s: %s 期望=%s" % (key, " ".join(GATES[key][0]), GATES[key][1]))
    elif cmd == "tick":
        batch = argv[1] if len(argv) > 1 else "ADHOC"
        print(json.dumps(tool.tick(batch), ensure_ascii=False, indent=2))
    else:
        print("usage: python -m holoaeon.machine_tool "
              "[status|boot|check|redlines|pipeline|gates|tick <batch>] [--bench]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
