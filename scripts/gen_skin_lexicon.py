# -*- coding: utf-8 -*-
"""B2b 皮肤词表分域：data/skin_lexicon_rehab.json

用法：python scripts/gen_skin_lexicon.py [--domain rehab] [--check]

为什么这样写（比"看起来词很多"重要）：
  · 通用闸（SG-SKIN-V6.0）固定 10 个 token 位，**永不并入医学词表**；
    一旦并入，通用域会被医学短语误熔断（坑表 V4-4）。
  · 医学侧 24 E14（越权动作）+ 12 E13（无证明断言）词条内容属 ivsa 仓资产
    （代码 MPL-2.0 / 内容 CC-BY-NC-SA），本仓**只登记计数、槽位与注入条件**，
    不复制词条原文，避免许可冲突与跨仓内容搬运。
  · 注入条件写死：domain=="medical" 才加载医学侧；general 只走 10 token 通用闸。
不写时间戳，复跑字节一致。
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "skin_lexicon_rehab.json")

GENERAL_SLOTS = ["G%02d" % i for i in range(1, 11)]
E14_SLOTS = ["M-E14-%02d" % i for i in range(1, 25)]
E13_SLOTS = ["M-E13-%02d" % i for i in range(1, 13)]


def build(domain="rehab"):
    return {
        "lexicon_id": "SG-SKIN-LEXICON-SPLIT-HOLOAEON-IVSA-V1",
        "batch": "B2b",
        "domain_scope": domain,
        "frozen_at": "2026-11-02",
        "evidence_class": "simulated",
        "tracks": {
            "general": {
                "owner": "SG-SKIN-V6.0 通用闸（HoloAeon 侧）",
                "slots": GENERAL_SLOTS,
                "count": len(GENERAL_SLOTS),
                "content": "本仓持有槽位与判定位，词条内容按 SG-SKIN-V6.0 版本执行",
                "includes_medical": False,
                "e13_e14_present": False,
            },
            "medical": {
                "owner": "ivsa L5 双轨仲裁层",
                "source_path": "ivsa/skin_layers/L5_dual_track_arbiter.py",
                "e14_slots": E14_SLOTS,
                "e14_count": len(E14_SLOTS),
                "e14_semantics": "越权动作（真实综合/越权执行类）",
                "e13_slots": E13_SLOTS,
                "e13_count": len(E13_SLOTS),
                "e13_semantics": "无证明断言（把仿真等同于硬件/临床结论类）",
                "copied_into_holoaeon": False,
                "license": "代码 MPL-2.0 / 内容 CC-BY-NC-SA-4.0（只登记不复制）",
            },
        },
        "injection": {
            "rule": "按 payload.domain 分域注入；general 只走 10 token 通用闸",
            "general_gate": {"when": "domain==general 或未声明", "load": ["general"],
                              "must_not_load": ["medical"]},
            "medical_gate": {"when": "domain==medical", "load": ["general", "medical"],
                              "extra_requirement": "payload.redlines 三布尔必须齐且为 true"},
        },
        "invariants": [
            {"id": "X1", "text": "通用闸恒为 10 个 token，不得增删"},
            {"id": "X2", "text": "通用闸内不得出现任何 E13/E14 词条"},
            {"id": "X3", "text": "医学侧 24 E14 + 12 E13 计数恒定"},
            {"id": "X4", "text": "两套词表不共享存储、不做并集合并"},
            {"id": "X5", "text": "词条内容不跨仓复制，只登记槽位与注入条件"},
        ],
        "spec_digest": "",
    }


def digest_of(doc):
    core = {k: v for k, v in doc.items() if k != "spec_digest"}
    canon = json.dumps(core, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16]


def main(argv):
    domain = "rehab"
    if "--domain" in argv:
        i = argv.index("--domain")
        if i + 1 < len(argv):
            domain = argv[i + 1]
    doc = build(domain)
    doc["spec_digest"] = digest_of(doc)
    text = json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if "--check" in argv:
        if not os.path.isfile(OUT):
            print(json.dumps({"verdict": "FAIL", "reason": "missing " + OUT}, ensure_ascii=False))
            return 1
        with open(OUT, encoding="utf-8") as f:
            same = f.read() == text
        print(json.dumps({"verdict": "PASS" if same else "FAIL", "byte_consistent": same,
                          "spec_digest": doc["spec_digest"]}, ensure_ascii=False))
        return 0 if same else 1
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(json.dumps({"out": OUT, "spec_digest": doc["spec_digest"],
                      "general": len(GENERAL_SLOTS), "e14": len(E14_SLOTS),
                      "e13": len(E13_SLOTS)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
