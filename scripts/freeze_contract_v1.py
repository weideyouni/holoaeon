# -*- coding: utf-8 -*-
"""B1b 冻结契约 v1：把字段口径写成机读文件 data/contract_v1.json。

用法：python scripts/freeze_contract_v1.py
判据：退出码 0 = 冻结文件已写出，且文件内两条示例的 contract_id 与复算一致。
不写时间戳，保证同日复跑字节一致。
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from holoaeon.fusion_upgrade import contract as c

OUT = os.path.join(ROOT, "data", "contract_v1.json")
RED = {"zero_dose": True, "c0_not_efficacy": True, "emergency_120": True}


def spec_core():
    return {
        "version": "v1",
        "frozen_at": "2026-11-02",
        "batch": "B1b",
        "evidence_class": "simulated",
        "required": list(c.REQUIRED),
        "optional": list(c.OPTIONAL),
        "payload_keys": list(c.PAYLOAD_KEYS),
        "domains": list(c.DOMAINS),
        "redline_keys": list(c.REDLINE_KEYS),
        "mechanisms": list(c.MECHANISMS),
        "lanes": list(c.LANES),
        "budget_range": list(c.BUDGET_RANGE),
        "note_max": c.NOTE_MAX,
        "fingerprint_rule": "sha256(canonical(source,target,skill,mechanism,lane,payload))[:12]",
        "rules": [
            {"id": "V1", "text": "6 必填任一缺失即 invalid"},
            {"id": "V2", "text": "mechanism 不在六值 / lane 不在 read|write 即 invalid"},
            {"id": "V3", "text": "payload 出现白名单外键 / domain 越界即 invalid"},
            {"id": "V4", "text": "domain=medical 时 redlines 三布尔必须齐且为 true"},
            {"id": "V5", "text": "重算指纹与声明 contract_id 不等即 invalid"},
            {"id": "V6", "text": "budget 必须是 0–100 整数"},
            {"id": "V7", "text": "note / payload.notes 超 200 字或出现剂量·用药词即 invalid"},
            {"id": "V8", "text": "顶层出现 10 字段外的键即 invalid"},
        ],
    }


def sample_general():
    return c.build(source="local", target="gitee", skill="fusion_contract",
                   mechanism="semantic_bus", lane="read",
                   payload={"domain": "general", "notes": "B1b 最小样本"}, budget=1)


def sample_medical():
    return c.build(source="local", target="ivsa", skill="fusion_plan",
                   mechanism="meridian", lane="read",
                   payload={"domain": "medical", "inputs": {"case_id": "R-001"},
                            "evidence": {"sha256": "98940b774566543b"},
                            "redlines": dict(RED), "notes": "只交换契约，不搬代码"},
                   nonce="n-20261102-01", budget=2)


def main():
    core = spec_core()
    canon = json.dumps(core, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    core["spec_digest"] = hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16]

    docs = {"general": sample_general(), "medical": sample_medical()}
    bad = [k for k, d in docs.items() if not c.validate_v1(d)["ok"]]
    core["examples"] = docs
    core["verify"] = {"examples_valid": not bad, "examples_bad": bad,
                      "checker": "scripts/check_contract_v1.py"}

    text = json.dumps(core, ensure_ascii=False, indent=2, sort_keys=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(text + "\n")
    print(json.dumps({"out": OUT, "spec_digest": core["spec_digest"],
                      "examples_valid": not bad, "bad": bad}, ensure_ascii=False))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
