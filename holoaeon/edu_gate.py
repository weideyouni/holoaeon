# -*- coding: utf-8 -*-
"""edu_gate — 教育域编排闸门（V36，教育大师 V3.0 蒸馏 · 领域编排环第四环）
D-11 链位：领域编排环（第八环·教育域）——cosmo_gate（第七环）之后。
第一性原理：血缘链=可追溯性，量规=可评量性；评价是学习闭环的最后一环。
零依赖纯标准库。封口密语：潮起开门，潮落闭嘴。
"""
import json
import time

SEAL = "潮起开门，潮落闭嘴"

CHAIN_POSITION = {
    "ring": 8,
    "name": "教育域编排",
    "upstream": ("cosmo_gate", "tea_gate", "math_gate"),
    "role": "血缘信封（可追溯）+ 六维量规（可评量）+ 红线自扫描",
    "same_as_law": "5th independent reproduction (医学/数学/茶/宇宙/教育)",
}

# D-02 六维量规（固定维度，评分∈[0,15]，grade 确定性映射）
RUBRIC_DIMS = ("架构完整性", "四机制实现", "六域能力",
               "安全红线", "工程可复现", "诚实边界")


def grade_of(total):
    if total >= 90:
        return "A"
    if total >= 80:
        return "B+"
    if total >= 70:
        return "B"
    if total >= 60:
        return "C"
    return "D"


class LineageBus:
    """E1：血缘信封——owner/thread_id/父指针/序号严格单调。"""

    def __init__(self, owner, thread_id):
        self.owner = owner
        self.thread_id = thread_id
        self.seq = 0
        self.registry = {}   # seq -> row

    def emit(self, payload, parent=None):
        if parent is not None and parent not in self.registry:
            return {"ok": False, "error": "orphan parent", "seal": SEAL}
        self.seq += 1   # 严格单调
        row = {"owner": self.owner, "thread_id": self.thread_id,
               "seq": self.seq, "parent": parent, "payload": payload,
               "ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "seal": SEAL}
        self.registry[self.seq] = row
        return {"ok": True, "seq": self.seq, "seal": SEAL}

    def lineage(self, seq):
        """血统链回放：从指定序号沿父指针回溯到根。"""
        chain = []
        cur = seq
        while cur is not None:
            if cur not in self.registry:
                return {"ok": False, "error": "missing seq", "seal": SEAL}
            row = self.registry[cur]
            chain.append(row["seq"])
            cur = row["parent"]
        return {"ok": True, "chain": list(reversed(chain)), "seal": SEAL}


class SelfEvalRubric:
    """E2：六维三轮自评量规（确定性分级+递进判定）。"""

    @staticmethod
    def score_round(scores):
        """scores: {dim: 分数∈[0,15]} → 总分+grade。"""
        if set(scores.keys()) != set(RUBRIC_DIMS):
            return {"ok": False, "error": "dims mismatch", "seal": SEAL}
        if any(not (0 <= v <= 15) for v in scores.values()):
            return {"ok": False, "error": "score out of range", "seal": SEAL}
        total = round(sum(scores.values()), 2)
        return {"ok": True, "total": total, "grade": grade_of(total),
                "seal": SEAL}

    @staticmethod
    def progression(rounds):
        """rounds: [{total,grade},...] 递进判定：每轮≥前轮。"""
        ok = all(b["total"] >= a["total"]
                 for a, b in zip(rounds, rounds[1:]))
        return {"progressive": ok, "rounds": len(rounds),
                "first": rounds[0]["grade"], "last": rounds[-1]["grade"],
                "seal": SEAL}


class RedlineSelfScan:
    """E3：红线自扫描——forbidden+missing 清单化（只报不改）。"""

    @staticmethod
    def scan(texts, required):
        """texts: {name: text}; required: [必须出现的键/词]"""
        forbidden_hits = []
        for name, txt in texts.items():
            for bad in ("必赚", "治愈", "应当判处"):
                if bad in txt:
                    forbidden_hits.append({"file": name, "hit": bad})
        missing = [r for r in required
                   if not any(r in t for t in texts.values())]
        return {"forbidden_hits": forbidden_hits,
                "missing_required": missing,
                "ok": not forbidden_hits and not missing,
                "action": "report_only（处置权=碳基终审）", "seal": SEAL}


class EduConductor:
    """总装：血缘→扫描→量规 一次编排。"""

    PIPELINE = ["E1_lineage", "E3_scan", "E2_rubric"]

    def conduct(self, owner, thread_id, emit_payload, texts, required,
                scores):
        bus = LineageBus(owner, thread_id)
        emitted = bus.emit(emit_payload)
        scan = RedlineSelfScan.scan(texts, required)
        rubric = SelfEvalRubric.score_round(scores)
        return {"emitted": emitted, "scan": scan, "rubric": rubric,
                "seal": SEAL}


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "chain"
    if cmd == "chain":
        print(json.dumps(CHAIN_POSITION, ensure_ascii=False, indent=1))
    elif cmd == "rubric":
        print(json.dumps(list(RUBRIC_DIMS), ensure_ascii=False))
    else:
        print("usage: python -m holoaeon.edu_gate [chain|rubric]")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))
