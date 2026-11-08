# -*- coding: utf-8 -*-
"""teach_gate — 教学域闸门（V45，dive-into-llms 课程三件套蒸馏）
D-11 链位：领域编排环（第十三环·教学域）——craft_gate（第十二环·工艺域）之后。
源蒸馏：GitHub Lordog/dive-into-llms（《动手学大模型》，上海交大张倬胜团队，
38.9k★，公益教程）。核心形状=「课件(概念 Know)+手册(步骤 Do)+脚本(可执行 Run)」
三件套课程单元 × 11 章 × 安全分级。
指针纪律：课件 PDF/ipynb/教程原文不入仓——只取课程结构与映射。
P4 伦理裁决（零武器化）：越狱攻击/大模型隐写/模型水印三章**只代码化防御面**——
红线清单、水印校验器、安全评测项；攻击载荷/隐写工具/规避术生成零函数
（刚性 DNA：真实性、零虚构；不提供任何用于攻击或规避检测的功能）。
有机融合（充分匹配既有技能）：11 章逐一映射 holoaeon 在仓模块——
  提示学习↔magic_lamp、数学推理↔math_gate、多模态↔phc_chronic_engine.FeedEnvelope、
  GUI Agent↔butler_os、智能体安全↔guard、RLHF↔dehallucination 对齐纪律、
  微调部署↔model_adapter、知识编辑↔titan_evolver capability-manifest。
真实复用（不重写）：craft_gate.Heartbeat（课程节拍）、craft_gate.EvidenceLedger
（学习台账）、phc_recall.embed（概念自测相似度）。
关联声明：三件套 Know-Do-Run 与 holo_forge 四态融合（策划-执行-参考-成品）
子集同构——仅记关联，不计 SAME_AS。
零依赖纯标准库（复用同仓 craft_gate/phc_recall/hypervector）。
封口密语：潮起开门，潮落闭嘴。
"""
import re

from .craft_gate import EvidenceLedger, Heartbeat
from .hypervector import HypervectorConfig, HypervectorSpace
from .phc_recall import embed

SEAL = "潮起开门，潮落闭嘴"

CHAIN_POSITION = {
    "ring": 13,
    "name": "教学域编排（课程三件套闸门）",
    "upstream": ("craft_gate", "phc_recall", "magic_lamp", "math_gate",
                 "guard"),
    "role": "11章课程注册+三件套单元+零武器化安全门+自测双轨+学习台账",
    "lineage_note": "Know-Do-Run 与 holo_forge 四态子集同构：关联声明不计SAME_AS",
    "disposition_note": "安全三章只防御面；攻击/隐写/规避载荷零函数",
}

# ── 11 章注册表（dive-into-llms 目录 × holoaeon 在仓模块映射） ─────────
# safety_class: neutral=常规教学；defensive=只防御面（零武器化）
CHAPTERS = {
    "fine_tune": {"cn": "微调与部署", "safety": "neutral",
                  "maps": ("model_adapter",)},
    "prompting": {"cn": "提示学习与思维链", "safety": "neutral",
                  "maps": ("magic_lamp",)},
    "knowledge_edit": {"cn": "知识编辑", "safety": "neutral",
                       "maps": ("titan_evolver",)},
    "math_reasoning": {"cn": "数学推理（迷你R1蒸馏）", "safety": "neutral",
                       "maps": ("math_gate",)},
    "watermark": {"cn": "模型水印", "safety": "defensive",
                  "maps": ("academic_gate",), "defense": "水印校验器（溯源）"},
    "jailbreak": {"cn": "越狱攻击", "safety": "defensive",
                  "maps": ("guard",), "defense": "红线清单与拦截（DANGER_PATTERNS）"},
    "steganography": {"cn": "大模型隐写", "safety": "defensive",
                      "maps": ("guard",), "defense": "隐写检测（可疑载荷审计）"},
    "multimodal": {"cn": "多模态模型", "safety": "neutral",
                   "maps": ("phc_chronic_engine.FeedEnvelope",)},
    "gui_agent": {"cn": "GUI 智能体", "safety": "neutral",
                  "maps": ("butler_os",)},
    "agent_safety": {"cn": "智能体安全", "safety": "defensive",
                     "maps": ("guard",), "defense": "开放场景风险评测清单"},
    "rlhf_alignment": {"cn": "RLHF 安全对齐", "safety": "neutral",
                       "maps": ("dehallucination",)},
}

# 三件套步骤（Know-Do-Run）
LESSON_STEPS = ("concept", "practice", "verify")

# 零武器化：防御面白名单之外的安全章内容一律拒收
_DEFENSE_ALLOWED = ("红线清单", "拦截", "校验器", "检测", "评测", "溯源",
                    "审计")
_FORBIDDEN_MARKS = ("载荷生成", "攻击模板", "规避术", "越狱提示词",
                    "隐写编码器", "水印规避")


class LessonUnit:
    """课程三件套单元：concept(Know)+practice(Do)+verify(Run)。
    安全章（defensive）内容必须命中防御面白名单，含禁区标记即拒收。"""

    @classmethod
    def create(cls, chapter_id, concept, practice, script_ref):
        ch = CHAPTERS.get(chapter_id)
        if not ch:
            return {"ok": False, "error": "unknown chapter", "seal": SEAL}
        for mark in _FORBIDDEN_MARKS:
            blob = concept + practice + str(script_ref)
            if mark in blob:
                return {"ok": False,
                        "error": "零武器化：禁区内容「%s」拒收" % mark,
                        "seal": SEAL}
        if ch["safety"] == "defensive":
            if not any(d in (concept + practice) for d in _DEFENSE_ALLOWED):
                return {"ok": False,
                        "error": "安全章内容必须为防御面（%s）"
                                 % "/".join(ch.get("defense", "").split("（")),
                        "seal": SEAL}
        unit = {"ok": True, "chapter": chapter_id, "cn": ch["cn"],
                "safety": ch["safety"],
                "steps": {s: "pending" for s in LESSON_STEPS},
                "concept": concept, "practice": practice,
                "script_ref": script_ref, "seal": SEAL}
        return unit


class SelfTest:
    """课程自测（twin_verify 双轨的教育域复现）：
    concept=概念相似（phc_recall.embed 余弦，确定性）；
    practice=步骤清单命中率（craft_gate.similarity_score 逐项）。
    对/像并列输出不加权——与 V44 正交纪律同频。"""

    SIM_THRESHOLD = 0.60

    @classmethod
    def concept_check(cls, answer, expected):
        space = HypervectorSpace(HypervectorConfig(dim=256))
        # 确定性余弦（与 phc_recall 内部实现同构，neural=false）
        va, vb = embed(space, answer), embed(space, expected)
        num = sum(x * y for x, y in zip(va, vb))
        da = sum(x * x for x in va) ** 0.5
        db = sum(x * x for x in vb) ** 0.5
        sim = round(num / (da * db), 4) if da and db else 0.0
        return {"ok": True, "track": "concept", "sim": sim,
                "passed": sim >= cls.SIM_THRESHOLD, "seal": SEAL}

    @classmethod
    def practice_check(cls, done, required):
        from .craft_gate import similarity_score
        r = similarity_score(required, done)
        return {"ok": r["ok"], "track": "practice",
                "coverage": r.get("score"), "diffs": r.get("diffs"),
                "passed": r["ok"] and r["score"] >= 1.0, "seal": SEAL}


class Curriculum:
    """课程编排（经络引导=学习路径）：基础→应用→安全→对齐；
    每课节拍走 Heartbeat（复用 craft_gate），台账走 EvidenceLedger。"""

    PATH = ("fine_tune", "prompting", "knowledge_edit", "math_reasoning",
            "multimodal", "gui_agent", "watermark", "jailbreak",
            "steganography", "agent_safety", "rlhf_alignment")

    def __init__(self):
        self.hb = Heartbeat()
        self.ledger = EvidenceLedger()
        self.progress = {cid: None for cid in self.PATH}

    def start_lesson(self, chapter_id):
        if chapter_id not in CHAPTERS:
            return {"ok": False, "error": "unknown chapter", "seal": SEAL}
        beat = self.hb.beat(chapter_id)
        ch = CHAPTERS[chapter_id]
        self.ledger.add("开课", "%s（%s/%s）"
                        % (ch["cn"], ch["safety"],
                           ch.get("defense", "常规教学")))
        self.progress[chapter_id] = {"beat": beat["beat"],
                                     "steps": {s: "pending"
                                               for s in LESSON_STEPS}}
        return {"ok": True, "chapter": chapter_id, "beat": beat["beat"],
                "safety": ch["safety"],
                "maps": ch["maps"], "seal": SEAL}

    def finish_lesson(self, chapter_id, selftest_ok):
        if self.progress.get(chapter_id) is None:
            return {"ok": False, "error": "lesson not started", "seal": SEAL}
        self.progress[chapter_id]["steps"] = {s: "done" for s in LESSON_STEPS}
        self.ledger.add("结课", "%s 自测=%s"
                        % (chapter_id, "PASS" if selftest_ok else "FAIL"))
        return {"ok": True, "chapter": chapter_id,
                "state": "done" if selftest_ok else "blocked", "seal": SEAL}

    def transcript(self):
        """成绩单：台账 SHA 链自校验 + 完课数。"""
        v = self.ledger.verify()
        done = sum(1 for p in self.progress.values()
                   if p and p["steps"]["verify"] == "done")
        return {"ok": v["ok"], "done": done, "total": len(self.PATH),
                "entries": v.get("entries", 0), "seal": SEAL}


class SafetyGate:
    """防御面闸（guard 精神的教学域复现）：安全章自测材料过闸——
    命中禁区标记 → BLOCK；防御面白名单 → ALLOW。"""

    @classmethod
    def admit(cls, material):
        for mark in _FORBIDDEN_MARKS:
            if mark in material:
                return {"verdict": "BLOCK", "mark": mark,
                        "reason": "零武器化", "seal": SEAL}
        return {"verdict": "ALLOW", "mark": None,
                "reason": "防御面或常规内容", "seal": SEAL}


def audit():
    """总闸快照：report-only。"""
    return {"seal": SEAL, "ring": CHAIN_POSITION["ring"],
            "chapters": len(CHAPTERS),
            "defensive": sorted(k for k, v in CHAPTERS.items()
                                if v["safety"] == "defensive"),
            "lesson_steps": list(LESSON_STEPS),
            "zero_weaponization": True,
            "reused": ("craft_gate.Heartbeat", "craft_gate.EvidenceLedger",
                       "craft_gate.similarity_score", "phc_recall.embed"),
            "neural": False}
