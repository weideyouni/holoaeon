"""V26 莫比乌斯漩涡模块（mobius_vortex）—— 状态回流环。

第一性原理
==========
正程（总监 → 豆包派发）已由 ACP 打通；缺的是回程（豆包 → 总监状态回流）。
莫比乌斯环带 = 单侧曲面：执行面走一圈回到总监面，无内外之分 —— 两面本就是
同一张状态面。因此状态回传**不建新通道**，只承认既有事实：同一文件系统
（`F:/doubaowork/`）即莫比乌斯接口面。

五段组合（漩涡的五圈水流）
========================
1. StateBeacon    豆包侧：执行后写状态灯塔 JSON（batch/head/gates/five_site/lessons/seal）
2. VortexIngest   总监侧：读灯塔，两级校验（L1 schema 快筛 + L2 seal 深校），杜绝幻觉回执
3. MobiusRing     三点对齐：灯塔 HEAD / 实时 git HEAD / 账面 HEAD（玉安记忆）
4. QuartetBrief   确定性聚合生成四人组简报（P4问题 / P2事实 / P3风险 / P1建议）
5. SkillAtlas     静态映射表：把模块功能自动匹配到既有技能与意义（零 LLM）

工程纪律（投喂包 §6 逐条对账）
============================
* 纯标准库（json/os/re/sys/time），零网络、零密钥、零外部依赖。
* 不 shell out：git 身份沿用 V25 `BaselineProbe` 的 `.git` 文件直读（HEAD→refs→packed-refs），
  故不触发 redline 的 `subprocess` 禁用项；仓内导入一律相对导入。
* 不碰 graph / scheduler / hypervector / kernel.submit；不新增扩展包（模块级，先例 butler_os V12 / machine_tool V25）。
* 新文件不参与 ReproHash → diff0 零漂移。
* 灯塔路径可注入；默认 `reports/state_beacon.json`（好嘞预案内，五地同步自然覆盖）。
* 简报只陈述，不自动执行建议 —— 人（碳基终审）决断。

证据等级：evidence_class=simulated，仿真≠证明，碳基终裁。
封口密语：潮起开门，潮落闭嘴。
"""
from __future__ import annotations

import json
import os
import re
import sys
import time

from .machine_tool import BaselineProbe, SEAL

SCHEMA_VERSION = "MOBIUS-BEACON-v1.0"

BEACON_REQUIRED = (
    "schema_version", "seal", "batch", "head", "head_short",
    "doc_version", "extra_packs", "gates", "five_site", "lessons", "created_at",
)

SHA_RE = re.compile(r"^[0-9a-f]{40}$")
DEFAULT_BEACON = os.path.join("reports", "state_beacon.json")
DEFAULT_MEMORY_DIR = r"F:\doubaowork\holoaeon_memory"

#  SkillAtlas 展开顺序即 §3 表顺序（确定性，便于断言条数）
ATLAS_ENTRIES = (
    {"module": "MobiusRing", "part": "对齐判定", "target": "mobius_edge",
     "source": "quartet_toolkit（14技能）",
     "meaning": "环面拓扑原语：单侧曲面=执行面与总监面同一状态面"},
    {"module": "VortexIngest", "part": "schema/seal 校验", "target": "dehallucination",
     "source": "V15 扩展包",
     "meaning": "回执真实性校验，杜绝幻觉状态"},
    {"module": "StateBeacon", "part": "事件发布", "target": "Envelope/Bus",
     "source": "HoloAeon 内核",
     "meaning": "语义通信基座，回执即事件"},
    {"module": "VortexIngest", "part": "前置过滤", "target": "event_filter",
     "source": "V16 super_agent 蒸馏",
     "meaning": "两级过滤：L1 schema快筛 + L2 seal深校"},
    {"module": "MobiusRing", "part": "断链告警", "target": "external_watchdog",
     "source": "V16 super_agent 蒸馏",
     "meaning": "只告警不拦截，独立于 Guard"},
    {"module": "MobiusRing", "part": "账面 HEAD 读取", "target": "memory_of_yuan",
     "source": "V17 专用记忆",
     "meaning": "玉安记忆=账面唯一来源"},
    {"module": "QuartetBrief", "part": "简报输出", "target": "machine_tool S2/S8",
     "source": "V25 机床",
     "meaning": "简报=定调输入+回填来源"},
    {"module": "StateBeacon", "part": "五地状态核对", "target": "FiveSiteLedger",
     "source": "V25 机床",
     "meaning": "全一致才收口"},
    {"module": "SkillAtlas", "part": "索引", "target": "vector_sea",
     "source": "V14 扩展包",
     "meaning": "617技能索引，Atlas 的放大版"},
    {"module": "QuartetBrief", "part": "简报登记簿", "target": "BatchLedger",
     "source": "城邦架构（V11）",
     "meaning": "多批次简报归档"},
)


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def _read_json(path):
    """读 JSON；失败返回 None。句柄用 with 关闭，不用内联 open(...).read()。"""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return None


def _write_json(path, payload):
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    return path


# ---------------------------------------------------------------------------
# 第一圈：StateBeacon —— 豆包侧状态灯塔（S6 验证回执的产物即灯塔）
# ---------------------------------------------------------------------------
class StateBeacon:
    """执行面写下的状态，总监面原样读到——同一张面，无需翻译层。"""

    def __init__(self, batch, head=None, head_short=None, doc_version=None,
                 extra_packs=None, gates=None, five_site=None, lessons=None,
                 repo=None, created_at=None):
        self.batch = batch
        self.head = head
        self.head_short = head_short or ((head or "")[:7] or None)
        self.doc_version = doc_version
        self.extra_packs = extra_packs
        self.gates = dict(gates or {})
        self.five_site = dict(five_site or {})
        self.lessons = list(lessons or [])
        self.repo = repo
        self.created_at = created_at or _now()

    @classmethod
    def collect(cls, batch, repo, gates=None, five_site=None, lessons=None):
        """从仓库实读身份与版本，拼一份灯塔。"""
        probe = BaselineProbe(repo).probe()
        return cls(
            batch=batch,
            head=probe.get("head"),
            head_short=probe.get("head_short"),
            doc_version=probe.get("doc_version"),
            extra_packs=probe.get("extra_packs"),
            gates=gates,
            five_site=five_site,
            lessons=lessons,
            repo=repo,
        )

    def payload(self):
        return {
            "schema_version": SCHEMA_VERSION,
            "seal": SEAL,
            "batch": self.batch,
            "head": self.head,
            "head_short": self.head_short,
            "doc_version": self.doc_version,
            "extra_packs": self.extra_packs,
            "gates": dict(self.gates),
            "five_site": dict(self.five_site),
            "lessons": list(self.lessons),
            "repo": self.repo,
            "created_at": self.created_at,
        }

    def write(self, path):
        return _write_json(path, self.payload())

    @staticmethod
    def read(path):
        return _read_json(path)


# ---------------------------------------------------------------------------
# 第二圈：VortexIngest —— 总监侧读灯塔，两级校验（L1 schema 快筛 + L2 seal 深校）
# ---------------------------------------------------------------------------
class VortexIngest:
    """校验不过=不承认。回执真实性是生命线（接 V15 去幻觉纪律）。"""

    def __init__(self, expected_seal=SEAL, expected_schema=SCHEMA_VERSION):
        self.expected_seal = expected_seal
        self.expected_schema = expected_schema

    def load(self, path):
        beacon = StateBeacon.read(path)
        result = self.validate(beacon)
        result["path"] = path
        return result

    def validate(self, beacon):
        problems = []
        if not isinstance(beacon, dict):
            return {"ok": False, "level": "load", "problems": ["灯塔不可读或非合法对象"],
                    "beacon": None}

        if beacon.get("schema_version") != self.expected_schema:
            problems.append("schema_version 期望 %s，实际 %r"
                            % (self.expected_schema, beacon.get("schema_version")))

        missing = [key for key in BEACON_REQUIRED if key not in beacon]
        if missing:
            problems.append("缺少必填键：" + ",".join(missing))

        head = beacon.get("head")
        if head is not None and not SHA_RE.match(str(head)):
            problems.append("head 不是 40 位十六进制：%r" % (head,))

        for key in ("gates", "five_site"):
            if key in beacon and not isinstance(beacon.get(key), dict):
                problems.append("%s 必须是对象" % key)
        if "lessons" in beacon and not isinstance(beacon.get("lessons"), list):
            problems.append("lessons 必须是数组")

        level = "L1_schema" if problems else "L2_seal"
        seal_ok = beacon.get("seal") == self.expected_seal
        if not seal_ok:
            problems.append("封口密语不符：期望 %r，实际 %r"
                            % (self.expected_seal, beacon.get("seal")))

        return {
            "ok": not problems,
            "level": "ok" if not problems else level,
            "seal_ok": seal_ok,
            "schema_ok": level == "L2_seal",
            "problems": problems,
            "beacon": beacon,
        }


# ---------------------------------------------------------------------------
# 第三圈：MobiusRing —— 三点对齐（灯塔 / 实时 / 账面）
# ---------------------------------------------------------------------------
class MobiusRing:
    """执行面走一圈回到总监面。三点不一致时：以实时为准，并回填账面（断线恢复协议）。"""

    def __init__(self, repo, memory_dir=None):
        self.repo = repo
        self.memory_dir = memory_dir or DEFAULT_MEMORY_DIR

    def live_head(self):
        return BaselineProbe(self.repo).read_head()

    def book_head(self):
        """账面 HEAD = 玉安记忆 version_history 最近一条带 head 的记录。"""
        doc = _read_json(os.path.join(self.memory_dir, "version_history.json"))
        if not isinstance(doc, dict):
            return None
        history = doc.get("history") or []
        for entry in reversed(history):
            if not isinstance(entry, dict):
                continue
            head = entry.get("head") or entry.get("head_full")
            if head:
                return head
        return None

    def align(self, beacon_head, book_head=None):
        live = self.live_head()
        book = self.book_head() if book_head is None else book_head
        notes = []

        if live is None:
            return {
                "beacon_head": beacon_head, "live_head": None, "book_head": book,
                "consistent": False, "verdict": "UNKNOWN",
                "source_of_truth": None, "backfill_needed": False,
                "notes": ["实时 HEAD 不可读：仓库不是 git 工作区或 .git 结构异常"],
            }

        consistent = (beacon_head == live == book)
        if beacon_head is None:
            notes.append("灯塔未携带 HEAD")
        elif beacon_head != live:
            notes.append("灯塔 HEAD %s ≠ 实时 HEAD %s" % (str(beacon_head)[:7], live[:7]))
        if book is None:
            notes.append("账面 HEAD 缺失：玉安记忆 version_history 无可用记录")
        elif book != live:
            notes.append("账面 HEAD %s ≠ 实时 HEAD %s（需回填）" % (book[:7], live[:7]))

        return {
            "beacon_head": beacon_head,
            "live_head": live,
            "book_head": book,
            "consistent": consistent,
            "verdict": "ALIGNED" if consistent else "DRIFT",
            "source_of_truth": "live",
            "backfill_needed": not consistent,
            "notes": notes,
        }


# ---------------------------------------------------------------------------
# 第四圈：QuartetBrief —— 确定性聚合，零 LLM
# ---------------------------------------------------------------------------
class QuartetBrief:
    """把灯塔 + 环面对齐结果压成四人组看得懂的一页：P4问题 / P2事实 / P3风险 / P1建议。"""

    ROLES = (("P4", "持衡 / Sutskever", "问题"), ("P2", "筑基 / Jeff Dean", "事实"),
             ("P3", "构弦 / Kavukcuoglu", "风险"), ("P1", "探微 / Hassabis", "建议"))

    def compose(self, beacon, ring):
        beacon = beacon or {}
        gates = beacon.get("gates") or {}
        five_site = beacon.get("five_site") or {}
        lessons = beacon.get("lessons") or []
        ring_verdict = ring.get("verdict")

        red_gates = sorted(str(k) for k, v in gates.items() if v is not True)
        bad_sites = sorted(
            str(k) for k, v in five_site.items()
            if not (isinstance(v, dict) and v.get("ok") is True)
        )

        facts = [
            "批次 %s" % (beacon.get("batch") or "(未标注)"),
            "HEAD %s" % (beacon.get("head_short") or beacon.get("head") or "?"),
            "DOC %s / EXTRA %s" % (beacon.get("doc_version") or "?", beacon.get("extra_packs", "?")),
            "闸门 %d/%d 绿" % (len(gates) - len(red_gates), len(gates)),
            "五地 %d 地已报，未一致 %d" % (len(five_site), len(bad_sites)),
            "环面 %s" % (ring_verdict or "?"),
        ]

        risks = []
        if ring_verdict == "DRIFT":
            risks.append("环面三点不一致：" + "；".join(ring.get("notes") or ["未知"]))
        elif ring_verdict == "UNKNOWN":
            risks.append("环面无法判定：实时 HEAD 不可读")
        if red_gates:
            risks.append("红灯闸门：" + ",".join(red_gates))
        if bad_sites:
            risks.append("五地未一致：" + ",".join(bad_sites))
        for lesson in lessons:
            risks.append("经验待吸收：" + str(lesson))

        if risks:
            question = "以上 %d 项未决，是否先修再收口？" % len(risks)
        else:
            question = "本批无未决项，是否推进下一批投喂？"

        advice = []
        if ring_verdict == "DRIFT":
            advice.append("以实时 HEAD 为准，并把账面回填玉安记忆 version_history，再发下一份灯塔")
        if red_gates:
            advice.append("按投喂包 §7 验证清单重跑红灯项；不以回执替代实测")
        if bad_sites:
            advice.append("补齐五地回读（S2 token-https / S3 origin / S5 HF 内容 sha256）")
        if lessons:
            advice.append("把 lessons 写进 ENGINE_LATHE 踩坑库后再开下一批")
        if not advice:
            advice.append("可收口：S8 回填记忆，接着发下一批灯塔")

        verdict = "BLOCK" if (red_gates or ring_verdict in ("DRIFT", "UNKNOWN")) else (
            "ATTENTION" if bad_sites or lessons else "PASS")

        return {
            "batch": beacon.get("batch"),
            "seal": SEAL,
            "roles": [{"role": r, "name": n, "kind": k} for r, n, k in self.ROLES],
            "p4_question": question,
            "p2_facts": facts,
            "p3_risks": risks,
            "p1_advice": advice,
            "verdict": verdict,
            "ring": ring,
            "created_at": _now(),
        }


# ---------------------------------------------------------------------------
# 第五圈：SkillAtlas —— 自动匹配功能技能与意义（静态表，确定性）
# ---------------------------------------------------------------------------
class SkillAtlas:
    def __init__(self, entries=None):
        self.entries = list(entries or ATLAS_ENTRIES)

    def all(self):
        return [dict(item) for item in self.entries]

    def match(self, keyword):
        needle = (keyword or "").strip().lower()
        if not needle:
            return []
        hits = []
        for item in self.entries:
            haystack = " ".join(str(item.get(k) or "") for k in
                                ("module", "part", "target", "source", "meaning")).lower()
            if needle in haystack:
                hits.append(dict(item))
        return hits


# ---------------------------------------------------------------------------
# 总装：MobiusVortex —— 创作面与接管面同一张状态面
# ---------------------------------------------------------------------------
class MobiusVortex:
    def __init__(self, repo=None, memory_dir=None, beacon_path=None):
        self.repo = repo or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.memory_dir = memory_dir or DEFAULT_MEMORY_DIR
        self.beacon_path = beacon_path or os.path.join(self.repo, DEFAULT_BEACON)
        self.ingest = VortexIngest()
        self.ring = MobiusRing(self.repo, self.memory_dir)
        self.brief = QuartetBrief()
        self.atlas = SkillAtlas()

    def status(self):
        head = self.ring.live_head()
        return {
            "module": "mobius_vortex",
            "version": "V26",
            "schema": SCHEMA_VERSION,
            "seal": SEAL,
            "repo": self.repo,
            "beacon_path": self.beacon_path,
            "beacon_exists": os.path.isfile(self.beacon_path),
            "live_head": head,
            "live_head_short": (head or "")[:7] or None,
            "book_head": self.ring.book_head(),
            "atlas_entries": len(self.atlas.entries),
            "collected_at": _now(),
        }

    def emit(self, batch, gates=None, five_site=None, lessons=None, path=None):
        beacon = StateBeacon.collect(batch, self.repo, gates, five_site, lessons)
        target = path or self.beacon_path
        beacon.write(target)
        return {"path": target, "beacon": beacon.payload()}

    def receive(self, path=None):
        return self.ingest.load(path or self.beacon_path)

    def align(self, path=None):
        result = self.ingest.load(path or self.beacon_path)
        beacon = result.get("beacon") or {}
        return self.ring.align(beacon.get("head"))

    def report(self, path=None):
        result = self.ingest.load(path or self.beacon_path)
        if not result.get("ok"):
            return {"ok": False, "ingest": result, "brief": None}
        beacon = result["beacon"]
        ring = self.ring.align(beacon.get("head"))
        brief = self.brief.compose(beacon, ring)
        return {"ok": True, "ingest": {"ok": True, "level": result["level"]},
                "ring": ring, "brief": brief}

    def close_loop(self, batch=None, gates=None, five_site=None, lessons=None):
        """A→H 的最后一步：发灯塔 → 读回 → 对齐 → 出简报（莫比乌斯面闭合成环）。"""
        emitted = self.emit(batch or "V26-EXEC", gates, five_site, lessons)
        return self.report(emitted["path"])


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    tool = MobiusVortex()
    action = argv[0] if argv else "status"

    if action == "atlas":
        keyword = argv[1] if len(argv) > 1 else None
        payload = tool.atlas.match(keyword) if keyword else tool.atlas.all()
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    if action == "beacon":
        batch = argv[1] if len(argv) > 1 else "V26-EXEC"
        print(json.dumps(tool.emit(batch), ensure_ascii=False, indent=2))
        return 0
    if action == "ingest":
        print(json.dumps(tool.receive(argv[1] if len(argv) > 1 else None),
                         ensure_ascii=False, indent=2))
        return 0
    if action == "align":
        print(json.dumps(tool.align(argv[1] if len(argv) > 1 else None),
                         ensure_ascii=False, indent=2))
        return 0
    if action == "brief":
        print(json.dumps(tool.report(argv[1] if len(argv) > 1 else None),
                         ensure_ascii=False, indent=2))
        return 0
    print(json.dumps(tool.status(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
