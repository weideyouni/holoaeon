# -*- coding: utf-8 -*-
"""math_gate — 数学编排闸门（V33，数学大师蒸馏 · 领域编排环）
D-11 链位：领域编排环（第五环）——泰坦进化之后的领域纵队首环。
第一性原理：只取闸门形状，不搬领域资产（指针纪律）。
同构实证：数学大师四机制（心跳/骨架/皮肤/语义总线）与 HoloAeon
全息机制独立趋同——全息公理的跨工程复现（SAME_AS 表随模块入库）。
零依赖纯标准库。封口密语：潮起开门，潮落闭嘴。
"""
import hashlib
import json
import os
import sys
import time

SEAL = "潮起开门，潮落闭嘴"

# D-11 链位自声明（领域编排环）
CHAIN_POSITION = {
    "ring": 5,
    "name": "数学编排",
    "upstream": ("titan_evolver", "gap_bridge", "machine_tool"),
    "role": "数学请求的双闸编排与安全阀路由（L2 前置闸 + L5 神龟否决）",
    "same_as": [
        "全息心跳↔心跳机制", "细胞骨架↔细胞骨架",
        "皮肤SG-SKIN-V6.0↔皮肤机制", "MATH-BUS-V1.1↔语义通信基座",
    ],
}

# D-02 数学刚性 DNA 七条（证据纪律）
MATH_DNA = [
    "数值吻合≠定理",
    "仿真≠证明",
    "相关≠因果",
    "收敛≠正确（收敛到错误极限也是收敛）",
    "基准≠真理（外部基准只是参照）",
    "猜想≠结论（前沿猜想必须标注）",
    "建议≠指令（不构成投资/交易/诊疗建议）",
]

# D-03 安全阀（触发词→处置）
SAFETY_VALVES = {
    "M14": {"name": "越权伪造",
            "triggers": ["荐股", "满仓", "目标价", "跳过证明",
                         "必赚", "稳赚", "内幕"],
            "action": "block"},
    "M13": {"name": "前沿猜想·仿真·外部基准",
            "triggers": ["证明了这个猜想", "因此定理成立",
                         "实测 External Benchmark"],
            "action": "relabel"},
    "ZERO_TRADE": {"name": "零交易",
                   "triggers": ["买入点", "卖出点", "仓位建议", "加仓"],
                   "action": "strip"},
}
DOMAINS = ("engineering", "research", "teaching", "content",
           "analytics", "ops")


class MathDNA:
    """M1：数学刚性 DNA——证据纪律清单与违反检测。"""

    @staticmethod
    def all_claims():
        return list(MATH_DNA)

    @staticmethod
    def violations(text):
        """检测文本中的 DNA 违反表述（确定性规则）。"""
        rules = [
            ("数值吻合≠定理", ("数值吻合，所以定理", "因此得证",)),
            ("仿真≠证明", ("仿真证明了", "模拟证明",)),
            ("相关≠因果", ("高度相关，因此必然导致",)),
            ("猜想≠结论", ("猜想已被我证明",)),
        ]
        low = (text or "").lower()
        hits = [name for name, cues in rules
                if any(c.lower() in low for c in cues)]
        return hits


class MathGate:
    """M2：双闸编排——L2 前置闸（安全阀）+ L5 神龟否决（DNA）。"""

    def __init__(self):
        self.valves = SafetyValves()

    def request(self, text, domain=None):
        gate_l2 = self.valves.check(text)
        if gate_l2["blocked"]:
            return {"verdict": "blocked_by_L2", "gate_l2": gate_l2,
                    "seal": SEAL}
        dna_hits = MathDNA.violations(text)
        gate_l5 = {"veto": len(dna_hits) >= 1, "violations": dna_hits}
        if gate_l5["veto"]:
            return {"verdict": "vetoed_by_L5", "gate_l5": gate_l5,
                    "seal": SEAL}
        return {"verdict": "pass", "gate_l2": gate_l2, "gate_l5": gate_l5,
                "domain": domain, "seal": SEAL}


class DomainRouter:
    """M3：六领域路由（城邦分区）。"""

    KEYWORDS = {
        "engineering": ("数值建模", "误差", "迭代", "求解"),
        "research": ("仿真", "拟合", "统计", "实验"),
        "teaching": ("教学", "讲解", "例题", "课程"),
        "content": ("科普", "桃花庵", "文章", "趣题"),
        "analytics": ("筛", "统计指标", "分布", "报表"),
        "ops": ("运维", "探针", "监控", "巡检"),
    }

    @classmethod
    def route(cls, text):
        low = (text or "").lower()
        scored = {d: sum(1 for k in ks if k in low)
                  for d, ks in cls.KEYWORDS.items()}
        best = max(scored, key=scored.get)
        return {"domain": best if scored[best] > 0 else "engineering",
                "scores": scored, "seal": SEAL}


class SafetyValves:
    """M4：安全阀——M14/M13/零交易 触发词→处置。"""

    def check(self, text):
        low = (text or "").lower()
        hits = []
        for vid, valve in SAFETY_VALVES.items():
            hit = [t for t in valve["triggers"] if t.lower() in low]
            if hit:
                hits.append({"valve": vid, "name": valve["name"],
                             "triggers_hit": hit, "action": valve["action"]})
        blocked = any(h["action"] == "block" for h in hits)
        return {"blocked": blocked, "hits": hits, "seal": SEAL}


class MathEnvelope:
    """M5：MATH-BUS 信封——语义通信+回执+零伪造质检（最小化）。"""

    def __init__(self, sender, payload, qos="normal"):
        self.sender = sender
        self.payload = payload
        self.qos = qos
        self.ts = time.strftime("%Y-%m-%dT%H:%M:%S")
        body = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        self.digest = hashlib.sha256(
            (sender + body + self.ts).encode("utf-8")).hexdigest()[:16]

    def receipt(self):
        return {"sender": self.sender, "qos": self.qos, "ts": self.ts,
                "digest": self.digest, "forged": False, "seal": SEAL}

    def verify(self, other_digest):
        return {"intact": self.digest == other_digest,
                "zero_forgery": self.digest == other_digest}


class MathConductor:
    """总装：双闸+路由+信封 一次编排。"""

    PIPELINE = ["M1_dna", "M2_gate", "M3_route", "M4_valves", "M5_envelope"]

    def conduct(self, sender, text):
        route = DomainRouter.route(text)
        gate = MathGate().request(text, domain=route["domain"])
        env = MathEnvelope(sender, {"text": text,
                                    "verdict": gate["verdict"]})
        return {"route": route, "gate": gate,
                "envelope_receipt": env.receipt(),
                "dna": MathDNA.all_claims(), "seal": SEAL}


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "chain"
    if cmd == "chain":
        print(json.dumps(CHAIN_POSITION, ensure_ascii=False, indent=1))
    elif cmd == "dna":
        for i, d in enumerate(MATH_DNA, 1):
            print(f"{i}. {d}")
    elif cmd == "valves":
        for vid, v in SAFETY_VALVES.items():
            print(f"{vid} {v['name']}（{v['action']}）：{', '.join(v['triggers'])}")
    else:
        print("usage: python -m holoaeon.math_gate [chain|dna|valves]")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
