# -*- coding: utf-8 -*-
"""cosmo_gate — 宇宙域编排闸门（V35，宇宙智能体矩阵蒸馏 · 领域编排环第三环）
D-11 链位：领域编排环（第七环·宇宙智能体域）——tea_gate（第六环·茶域）之后。
第一性原理：探索与收敛不是两个动作，是一个呼吸——
莫比乌斯扩张与克莱因收敛焊成交替对偶闭环（确定性，无随机源）。
零依赖纯标准库。封口密语：潮起开门，潮落闭嘴。
"""
import json
import math
import sys
import time

SEAL = "潮起开门，潮落闭嘴"

CHAIN_POSITION = {
    "ring": 7,
    "name": "宇宙域编排",
    "upstream": ("tea_gate", "math_gate", "titan_evolver"),
    "role": "对偶闭环（扩张↔收敛）+ 导师路由 + 暴风节拍 + 熵平衡",
    "same_as_law": "4th independent reproduction (医学母版/数学/茶/宇宙)",
}

# 学科→导师路由表（形状；人设不搬，字段为示例键）
MENTOR_TABLE = {
    "physics": "M-P", "chemistry": "M-C", "biology": "M-B",
    "astronomy": "M-A", "earth": "M-E", "math": "M-M",
    "economics": "M-Ec", "sociology": "M-So", "law": "M-L",
    "psychology": "M-Ps", "education": "M-Ed", "history": "M-H",
    "literature": "M-Li", "philosophy": "M-Ph",
}


class DualLoop:
    """C1：对偶闭环——扩张步（确定性UCB）↔ 收敛步（Pareto折叠）。"""

    @staticmethod
    def expand(candidates, stats, c=1.414):
        """确定性 UCB 式扩张：未访问优先，同分取均值最高，再按序。
        candidates: [{id, score}]; stats: {id: visits}"""
        scored = []
        for i, cand in enumerate(candidates):
            cid = cand["id"]
            visits = stats.get(cid, 0)
            explore = math.sqrt(c * math.log(len(candidates) + 1) /
                                (visits + 1))
            scored.append((visits, -cand["score"], -explore, -i,
                           cand))
        scored.sort()
        return scored[0][-1]

    @staticmethod
    def fold(population):
        """克莱因收敛：Pareto 折叠（保留非支配解，确定性排序）。
        population: [{id, gains:[...]}]（gains 各维越大越好）"""
        def dominates(a, b):
            ge = all(x >= y for x, y in zip(a["gains"], b["gains"]))
            gt = any(x > y for x, y in zip(a["gains"], b["gains"]))
            return ge and gt
        front = []
        for p in population:
            if not any(dominates(q, p) for q in population if q is not p):
                front.append(p)
        front.sort(key=lambda x: x["id"])
        return {"front": front, "folded": len(population) - len(front)}

    @classmethod
    def breathe(cls, candidates, stats, population):
        """一个呼吸节拍：先扩张后收敛。"""
        pick = cls.expand(candidates, stats)
        fold = cls.fold(population)
        return {"expanded": pick["id"], "folded_away": fold["folded"],
                "front": [p["id"] for p in fold["front"]], "seal": SEAL}


class MentorRouter:
    """C2：三级导师路由——学科→导师→知识星导。"""

    STARS = {"natural": "星导-自然", "social": "星导-社会"}

    GROUP = {k: "natural" for k in
             ("physics", "chemistry", "biology", "astronomy", "earth",
              "math")}
    GROUP.update({k: "social" for k in
                  ("economics", "sociology", "law", "psychology",
                   "education", "history", "literature", "philosophy")})

    @classmethod
    def route(cls, subject):
        mentor = MENTOR_TABLE.get(subject)
        if not mentor:
            return {"ok": False, "error": "unknown subject", "seal": SEAL}
        star = cls.STARS[cls.GROUP[subject]]
        return {"ok": True, "subject": subject, "mentor": mentor,
                "star_guide": star, "seal": SEAL}


class StormIteration:
    """C3：暴风迭代状态机（S0-S10，确定性波次）。"""

    WAVES = ["S0_seed", "S1", "S2", "S3", "S4", "S5", "S6", "S7",
             "S8", "S9", "S10_close"]

    def __init__(self):
        self.wave = 0
        self.log = []

    def step(self, ok=True):
        name = self.WAVES[self.wave]
        self.log.append({"wave": name, "ok": ok})
        if ok:
            self.wave = min(self.wave + 1, len(self.WAVES) - 1)
        # 失败：原地重试（不回退批次的纪律=不倒退，只停）
        return {"wave": name, "advanced": ok,
                "done": self.wave == len(self.WAVES) - 1, "seal": SEAL}


class EntropyBalance:
    """C4：熵平衡判据——簇内多样性/簇间秩序→负熵跃迁。"""

    @staticmethod
    def check(diversity, order):
        """diversity, order ∈ [0,1]。负熵跃迁：两者均高于阈值且比值有界。"""
        if not (0 <= diversity <= 1 and 0 <= order <= 1):
            return {"ok": False, "error": "out of range", "seal": SEAL}
        ratio = diversity / order if order > 0 else float("inf")
        leap = diversity >= 0.5 and order >= 0.5 and ratio <= 2.0
        return {"ok": True, "ratio": round(ratio, 4), "negative_entropy_leap": leap,
                "seal": SEAL}


class CosmoConductor:
    """总装：路由→呼吸→暴风→熵平衡 一次编排。"""

    PIPELINE = ["C2_route", "C1_breathe", "C3_storm", "C4_entropy"]

    def conduct(self, subject, candidates, stats, population,
                diversity=0.6, order=0.6):
        route = MentorRouter.route(subject)
        breath = DualLoop.breathe(candidates, stats, population)
        storm = StormIteration()
        storm.step(ok=True)
        entropy = EntropyBalance.check(diversity, order)
        return {"route": route, "breath": breath, "storm_wave": storm.log,
                "entropy": entropy, "seal": SEAL}


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "chain"
    if cmd == "chain":
        print(json.dumps(CHAIN_POSITION, ensure_ascii=False, indent=1))
    elif cmd == "mentors":
        for k, v in sorted(MENTOR_TABLE.items()):
            print(f"{k} -> {v} -> {MentorRouter.STARS[MentorRouter.GROUP[k]]}")
    else:
        print("usage: python -m holoaeon.cosmo_gate [chain|mentors]")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
