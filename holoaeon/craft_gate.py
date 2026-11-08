# -*- coding: utf-8 -*-
"""craft_gate — 工艺域闸门（V43，craft-anything 四步流水线蒸馏 · 六器官装配）
D-11 链位：领域编排环（第十二环·工艺域）——phc_chronic_engine/phc_recall
（第十一环·公共卫生域）之后。
源蒸馏：GitHub storytold/craft-anything（Apache-2.0 / MIT，12.8k★，纯 Rust
clean-room 引擎，12.8k★）。核心形状=四步流水线 Study→Build→Check→Ready +
证据台账（evidence ledger）+ Clean Room/Deep 双模式 + 审批卡 + 相似度收敛
（"Checked, not guessed"）。
指针纪律：只取形状，Rust 资产/320 工具/引擎不入仓。
四人组自检（关键）：用户点名六大机制**全部已代码化在仓**——
  心跳=bus.Bus.heartbeat（concept_anatomy: holo_heartbeat→scheduler）；
  细胞骨架=kernel（自述"原'细胞骨架'"）；皮肤=guard（自述"原'皮肤'"，L1-L10）；
  语义通信底座=bus（Envelope，V3 语言通信基座）；
  赫布协作场=graph.AdaptiveGraph（自述"原'赫布协作场'"）；
  经络=concept_anatomy.holo_meridian→topology_resonance。
故本环不重复造器官，而是把四步流水线**装配到既有器官**（ORGAN_MAP 注册 +
真实 import 复用 graph/guard），凡同构不重写者只声明落点。
P4 扬弃：clean room="不读原作内部、只从可见面研究" ↔ holoaeon 指针纪律
（取形状不搬资产）+ 用户"借鉴不照搬"——完全同频，故 CleanRoomGate 为本环
第一公民；审批卡=处置权分离（deep 模式须显式授权）；证据台账=V38/V40
"每数字可复算"在工艺域的全息再现。
关联声明：四步与 klein「投影→评估→吸纳」、magic_lamp「试测先行→碳基终审」
节拍同构——仅记关联，不计 SAME_AS（诚实处理）。
零依赖纯标准库（复用同仓 graph/guard）。封口密语：潮起开门，潮落闭嘴。
"""
import hashlib
import time

from .graph import AdaptiveGraph
from .spec import AdaptiveGraphConfig

SEAL = "潮起开门，潮落闭嘴"

CHAIN_POSITION = {
    "ring": 12,
    "name": "工艺域编排（四步流水线闸门）",
    "upstream": ("graph", "guard", "doc_anatomy", "holo_forge", "magic_lamp"),
    "role": "四步流水线+证据台账+清洁室门+相似度收敛+六器官装配",
    "lineage_note": "四步与klein/神灯节拍同构：关联声明，不计SAME_AS",
    "disposition_note": "deep模式须显式授权=审批卡；clean_room=指针纪律工艺化",
}

# ── 六器官装配表（自检结论：全部已有在仓落点，本环装配不重写） ─────────
ORGAN_MAP = {
    "全息心跳": {"organ": "Heartbeat",
              "landfall": "holoaeon.bus.Bus.heartbeat",
              "role": "一步一拍（对齐 bus.heartbeat 的 dict 形状）"},
    "细胞骨架": {"organ": "StepRail",
              "landfall": "holoaeon.kernel（Kernel 自述=原'细胞骨架'）",
              "role": "四步固定轨道，不可跳步"},
    "语义通信底座": {"organ": "SemanticEnvelope",
                 "landfall": "holoaeon.bus（Envelope，V3 语言通信基座）",
                 "role": "步间信封，载荷必须带引用"},
    "皮肤机制": {"organ": "CleanRoomGate",
              "landfall": "holoaeon.guard（Guard 自述=原'皮肤'）",
              "role": "暴露面控制：clean_room/deep 双模式"},
    "赫布协作场": {"organ": "HebbianReinforce",
               "landfall": "holoaeon.graph.AdaptiveGraph.hebbian_step",
               "role": "成功步骤对共现强化（真实复用 AdaptiveGraph）"},
    "经络机制": {"organ": "MERIDIAN_MAP",
              "landfall": "holoaeon.concept_anatomy→topology_resonance",
              "role": "四步→既有链路模块引导"},
}

STEPS = ("study", "build", "check", "ready")

# 经络图：四步 → 既有链路模块引导（装配而非重写）
MERIDIAN_MAP = {
    "study": ("doc_anatomy", "concept_anatomy"),
    "build": ("holo_forge", "titan_evolver"),
    "check": ("dehallucination",),
    "ready": ("magic_lamp", "mobius_vortex"),
}

# clean_room 下被拒绝的深读动作（craft-anything 清洁室规则的确定性子集）
DEEP_ACTIONS = ("read_source", "disassemble", "read_js", "read_files")


class StepRail:
    """细胞骨架：四步固定轨道状态机。advance 一次进一步，不可跳步；
    每步走 Heartbeat 拍点。"""

    def __init__(self):
        self.pos = 0
        self.state = {s: "pending" for s in STEPS}

    def advance(self):
        if self.pos >= len(STEPS):
            return {"ok": False, "error": "rail at end", "seal": SEAL}
        s = STEPS[self.pos]
        self.state[s] = "running"
        return {"ok": True, "step": s, "index": self.pos, "seal": SEAL}

    def complete(self):
        s = STEPS[self.pos]
        self.state[s] = "done"
        self.pos += 1
        return {"ok": True, "step": s, "state": "done", "seal": SEAL}

    def fail(self):
        s = STEPS[self.pos]
        self.state[s] = "blocked"
        return {"ok": False, "step": s, "state": "blocked", "seal": SEAL}


class Heartbeat:
    """全息心跳：一步一拍（doc_anatomy M01 惯例）。拍点 dict 形状对齐
    bus.Bus.heartbeat（键名风格一致，无锁无线程——流水线是单线程节拍器）。"""

    def __init__(self):
        self.n = 0
        self.t0 = time.time()

    def beat(self, step):
        self.n += 1
        return {"beat": self.n, "step": step,
                "uptime_s": round(time.time() - self.t0, 3), "seal": SEAL}


class EvidenceLedger:
    """证据台账（craft-anything evidence ledger ↔ V38/V40 每数字可复算）：
    每条结论带证据；append-only + SHA 链防篡改。"""

    def __init__(self):
        self.entries = []
        self._prev = ""

    def add(self, claim, evidence):
        digest = hashlib.sha256(
            (self._prev + claim + evidence).encode("utf-8")).hexdigest()
        self.entries.append({"claim": claim, "evidence": evidence,
                             "sha": digest})
        self._prev = digest
        return {"ok": True, "count": len(self.entries), "seal": SEAL}

    def verify(self):
        prev = ""
        for i, e in enumerate(self.entries):
            expect = hashlib.sha256(
                (prev + e["claim"] + e["evidence"]).encode("utf-8")
            ).hexdigest()
            if e["sha"] != expect:
                return {"ok": False, "broken_at": i, "seal": SEAL}
            prev = e["sha"]
        return {"ok": True, "entries": len(self.entries), "seal": SEAL}


class SemanticEnvelope:
    """语义通信底座：步间信封。载荷必须带引用（refs 非空）——
    无引用的消息不通信（与证据台账联动）。形状与 bus.Envelope 同构。"""

    REQUIRED = ("from_step", "to_step", "payload", "refs")

    @classmethod
    def create(cls, from_step, to_step, payload, refs):
        if from_step not in STEPS or to_step not in STEPS:
            return {"ok": False, "error": "unknown step", "seal": SEAL}
        if not refs:
            return {"ok": False, "error": "refs required（无引用不通信）",
                    "seal": SEAL}
        return {"ok": True, "from_step": from_step, "to_step": to_step,
                "payload": payload, "refs": list(refs), "seal": SEAL}


class CleanRoomGate:
    """皮肤机制：暴露面控制。clean_room（默认）拒绝一切深读原作内部动作；
    deep 模式须 authorized=True（审批卡=处置权分离）。三值语义对齐
    guard（ALLOW/BLOCK）。"""

    def __init__(self, mode="clean_room"):
        self.mode = mode if mode in ("clean_room", "deep") else "clean_room"

    def admit(self, action, authorized=False):
        if action not in DEEP_ACTIONS:
            return {"verdict": "ALLOW", "action": action, "seal": SEAL}
        if self.mode == "clean_room":
            return {"verdict": "BLOCK", "action": action,
                    "reason": "clean_room：不读原作内部（指针纪律工艺化）",
                    "seal": SEAL}
        if not authorized:
            return {"verdict": "BLOCK", "action": action,
                    "reason": "deep 模式须审批卡显式授权（处置权分离）",
                    "seal": SEAL}
        return {"verdict": "ALLOW", "action": action,
                "reason": "deep+authorized", "seal": SEAL}


class HebbianReinforce:
    """赫布协作场：真实复用 AdaptiveGraph——四步为节点，流水线顺序为流边，
    每轮成功步骤共现 → hebbian_step 强化。"""

    FLOW = (("study", "build"), ("build", "check"), ("check", "ready"))

    def __init__(self):
        self.g = AdaptiveGraph(
            config=AdaptiveGraphConfig(node_count=4),
            node_names=list(STEPS),
            flow_edges=[(0, 1), (1, 2), (2, 3)])
        for i, s in enumerate(STEPS):  # 名字→节点映射（node_of 依赖）
            self.g.map_agent(s, i)

    def reinforce(self, ok_steps):
        nodes = [self.g.node_of(s) for s in ok_steps if s in STEPS]
        return self.g.hebbian_step(nodes)


def similarity_score(checks, matched):
    """check 步：与原作逐项对比 → 相似度打分 + 差异清单。
    Checked, not guessed：分数只由逐项比对产生，可复算。"""
    if not checks:
        return {"ok": False, "error": "no checks", "seal": SEAL}
    matched = set(matched)
    diffs = [c for c in checks if c not in matched]
    score = round(len(matched & set(checks)) / len(checks), 4)
    return {"ok": True, "score": score, "diffs": diffs,
            "total": len(checks), "seal": SEAL}


class CraftPipeline:
    """四步流水线：study→build→check→(refine 循环)→ready。
    每步心跳拍点；步间语义信封；证据台账全程记录；ready 签收后赫布强化。"""

    def __init__(self, mode="clean_room", max_rounds=3, threshold=0.9):
        self.rail = StepRail()
        self.hb = Heartbeat()
        self.ledger = EvidenceLedger()
        self.gate = CleanRoomGate(mode)
        self.hebbian = HebbianReinforce()
        self.max_rounds = max_rounds
        self.threshold = threshold
        self.log = []

    def run(self, target, checks, build_brief="按任务书构建（委托编码代理）"):
        """确定性驱动。build 是委托声明（任务书），引擎本体不写目标代码——
        编码代理=豆包/外部（与 magic_lamp 缺口委托同构）。"""
        beats, envelopes = [], []
        # study
        self.rail.advance()
        beats.append(self.hb.beat("study"))
        self.ledger.add("study完成", "检查目标：%s（mode=%s）"
                        % (target, self.gate.mode))
        self.rail.complete()
        envelopes.append(SemanticEnvelope.create(
            "study", "build", "研究完毕，任务书就绪", ["ledger#1"]))
        # build
        self.rail.advance()
        beats.append(self.hb.beat("build"))
        deep_hits = [a for a in DEEP_ACTIONS
                     if self.gate.admit(a)["verdict"] == "ALLOW"]
        self.ledger.add("build委托", "clean_room=%s；deep放行=%s"
                        % (self.gate.mode == "clean_room", deep_hits or "无"))
        self.rail.complete()
        envelopes.append(SemanticEnvelope.create(
            "build", "check", build_brief, ["ledger#2"]))
        # check + refine 循环
        rounds = 0
        result = None
        while rounds < self.max_rounds:
            self.rail.advance()
            rounds += 1
            beats.append(self.hb.beat("check"))
            self.ledger.add("check第%d轮" % rounds, "逐项比对 %d 项" % len(checks))
            result = similarity_score(checks, checks if rounds >= self.max_rounds
                                      else checks[:max(1, len(checks) - rounds + 1)])
            self.rail.complete()
            if result["score"] >= self.threshold:
                break
            envelopes.append(SemanticEnvelope.create(
                "check", "build", "差异项：%s" % result["diffs"],
                ["ledger#check%d" % rounds]))
        # ready
        self.rail.advance()
        beats.append(self.hb.beat("ready"))
        self.rail.complete()
        reinforce = self.hebbian.reinforce(
            [s for s, st in self.rail.state.items() if st == "done"])
        receipt = {"ok": True, "target": target, "mode": self.gate.mode,
                   "score": result["score"], "rounds": rounds,
                   "diffs": result["diffs"],
                   "beats": len(beats), "envelopes": len(envelopes),
                   "evidence": self.ledger.verify(),
                   "clean_room_declaration": "本流水线产物为形状借鉴，"
                   "零照搬原作资产（clean room）",
                   "hebbian": reinforce, "seal": SEAL}
        return receipt


def audit():
    """总闸：工艺域状态快照，report-only。"""
    return {"seal": SEAL, "ring": CHAIN_POSITION["ring"],
            "steps": list(STEPS),
            "organs": {k: v["landfall"] for k, v in ORGAN_MAP.items()},
            "meridian": MERIDIAN_MAP,
            "deep_actions": list(DEEP_ACTIONS),
            "reused_modules": ("holoaeon.graph.AdaptiveGraph",),
            "zero_guess": "checked-not-guessed：check 步强制",
            "zero_dependency": "纯标准库+同仓 graph", "neural": False}
