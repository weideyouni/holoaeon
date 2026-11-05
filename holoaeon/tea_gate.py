# -*- coding: utf-8 -*-
"""tea_gate — 茶域编排闸门（V34，茶叶导学大师蒸馏 · 领域编排环第二环）
D-11 链位：领域编排环（第六环，茶域）——math_gate（第五环·数学）之后。
第一性原理：只取闸门形状不搬领域资产（指针纪律）。
同构再现：茶域四机制与 HoloAeon 全息机制第三次跨工程趋同
（chain_complete / 莫比乌斯·克莱因因子），SAME_AS 档案扩充。
零依赖纯标准库。封口密语：潮起开门，潮落闭嘴。
"""
import hashlib
import json
import os
import time

SEAL = "潮起开门，潮落闭嘴"

CHAIN_POSITION = {
    "ring": 6,
    "name": "茶域编排",
    "upstream": ("math_gate", "titan_evolver", "gap_bridge"),
    "role": "茶域请求的校准三律编排 + 急症双熔断 + 伦理阀 + 事实源信封",
    "same_as_archive": [
        "V30 math? no——三次复现：医学母版(CPT/KBH/ZJY) / 数学大师(V33来源) / 茶叶导学大师(本批来源)",
        "全息心跳↔心跳机制（chain_complete 闭环）",
        "细胞骨架↔细胞骨架（薄种子自举）",
        "皮肤SG-SKIN-V6.0↔皮肤机制（三胚层八模块）",
        "JSONL信封+SHA单一事实源↔语义通信基座+append-only台账",
    ],
}

# D-01 校准三律
CALIBRATION_RULES = {
    "min_candidates": 2,
    "confidence_range": (0.0, 1.0),
    "zero_dosage_claim": "零剂量不称疗效",
}

# D-02 E14 急症触发词（双熔断，不可跨越）
EMERGENCY_TRIGGERS = ["喉头水肿", "呼吸困难", "过敏性休克",
                      "心悸不止", "意识模糊"]

# D-03 伦理阀
ETHICAL_VALVES = {
    "E13": {"name": "代茶饮边界/濒危只论替代",
            "triggers": ["野生石斛", "野生天麻", "濒危", "穿山甲"],
            "action": "substitute_only"},
    "ZERO_DOSAGE": {"name": "零剂量",
                    "triggers": ["每日克数", "具体剂量", "用量多少克"],
                    "action": "strip_dosage"},
    "NO_CLAIM": {"name": "功效不称疗效",
                 "triggers": ["治愈", "根治", "药到病除"],
                 "action": "relabel"},
}


class CalibratedTriad:
    """T1：校准三律——建议型输出的通用校准形状。"""

    @staticmethod
    def check(candidates, confidence):
        errs = []
        if len(candidates or []) < CALIBRATION_RULES["min_candidates"]:
            errs.append("候选不足（须≥2）")
        lo, hi = CALIBRATION_RULES["confidence_range"]
        if confidence is None or not (lo <= confidence <= hi):
            errs.append("置信度须∈[0,1]")
        return {"ok": not errs, "errors": errs, "seal": SEAL}


class EmergencyFuse:
    """T2：E14 急症双熔断（L2+L5，不可跨越）。"""

    @staticmethod
    def check(text):
        low = (text or "")
        hits = [t for t in EMERGENCY_TRIGGERS if t in low]
        fused = len(hits) >= 1
        return {"fused": fused, "hits": hits,
                "layers": ["L2_fuse", "L5_fuse"] if fused else [],
                "action": "立即线下就医（本闸门不提供任何处置方案）"
                if fused else None, "seal": SEAL}


class EthicalValves:
    """T3：伦理阀——E13/零剂量/功效不称疗效。"""

    @staticmethod
    def check(text):
        low = (text or "").lower()
        hits = []
        for vid, v in ETHICAL_VALVES.items():
            hit = [t for t in v["triggers"] if t.lower() in low]
            if hit:
                hits.append({"valve": vid, "name": v["name"],
                             "triggers_hit": hit, "action": v["action"]})
        return {"hits": hits, "seal": SEAL}


class TruthSourceEnvelope:
    """T4：JSONL append-only 单一事实源信封（SHA 记账）。"""

    def __init__(self, path):
        self.path = path
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    def append(self, sender, payload):
        ts = time.strftime("%Y-%m-%dT%H:%M:%S")
        body = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        digest = hashlib.sha256(
            (sender + body + ts).encode("utf-8")).hexdigest()
        row = {"sender": sender, "payload": payload, "ts": ts,
               "sha": digest, "seal": SEAL}
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        return {"sha": digest, "appended": True}

    def verify_chain(self):
        """逐行重算 SHA：单一事实源完整性（append-only 可验证）。"""
        if not os.path.exists(self.path):
            return {"ok": True, "rows": 0}
        ok, n = True, 0
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                n += 1
                row = json.loads(line)
                body = json.dumps(row["payload"], ensure_ascii=False,
                                  sort_keys=True)
                calc = hashlib.sha256(
                    (row["sender"] + body + row["ts"]).encode("utf-8")
                ).hexdigest()
                if calc != row["sha"]:
                    ok = False
                    break
        return {"ok": ok, "rows": n}


class TeaConductor:
    """总装：熔断→伦理→校准→信封 一次编排。"""

    PIPELINE = ["T2_fuse", "T3_ethics", "T1_triad", "T4_envelope"]

    def __init__(self, ledger_path=None):
        self.ledger = (TruthSourceEnvelope(ledger_path)
                       if ledger_path else None)

    def conduct(self, sender, text, candidates=None, confidence=None):
        fuse = EmergencyFuse.check(text)
        if fuse["fused"]:
            return {"verdict": "fused_E14", "fuse": fuse, "seal": SEAL}
        ethics = EthicalValves.check(text)
        triad = CalibratedTriad.check(candidates, confidence)
        receipt = (self.ledger.append(sender, {"text": text,
                                               "ethics": ethics})
                   if self.ledger else None)
        return {"verdict": "calibrated" if triad["ok"] else "needs_fix",
                "ethics": ethics, "triad": triad,
                "ledger_sha": (receipt or {}).get("sha"), "seal": SEAL}


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "chain"
    if cmd == "chain":
        print(json.dumps(CHAIN_POSITION, ensure_ascii=False, indent=1))
    elif cmd == "rules":
        print(json.dumps(CALIBRATION_RULES, ensure_ascii=False, indent=1))
    else:
        print("usage: python -m holoaeon.tea_gate [chain|rules]")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))
