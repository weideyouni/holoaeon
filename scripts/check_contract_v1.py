# -*- coding: utf-8 -*-
"""B1b 冻结件校验：data/contract_v1.json 与代码常量、示例指纹三方对齐。

用法：python scripts/check_contract_v1.py   → 退出码 0/1，打印 JSON
判据：
  F1 字段/枚举/白名单与 code 常量完全一致
  F2 两条示例 validate_v1 通过且 contract_id 可复算
  F3 spec_digest 可复算（改一个字符即变）
  F4 规则表 V1–V8 齐
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from holoaeon.fusion_upgrade import contract as c

FROZEN = os.path.join(ROOT, "data", "contract_v1.json")


def main():
    checks = []

    def add(cid, ok, detail):
        checks.append({"id": cid, "ok": bool(ok), "detail": detail})

    if not os.path.isfile(FROZEN):
        add("F0", False, "missing " + FROZEN)
        print(json.dumps({"verdict": "FAIL", "checks": checks}, ensure_ascii=False, indent=2))
        return 1

    with open(FROZEN, encoding="utf-8") as f:
        spec = json.load(f)

    pairs = [("required", list(c.REQUIRED)), ("optional", list(c.OPTIONAL)),
             ("payload_keys", list(c.PAYLOAD_KEYS)), ("domains", list(c.DOMAINS)),
             ("redline_keys", list(c.REDLINE_KEYS)), ("mechanisms", list(c.MECHANISMS)),
             ("lanes", list(c.LANES)), ("budget_range", list(c.BUDGET_RANGE)),
             ("note_max", c.NOTE_MAX)]
    diff = [k for k, v in pairs if spec.get(k) != v]
    add("F1", not diff, "diff={}".format(diff))

    examples = spec.get("examples", {})
    bad = []
    for name, doc in examples.items():
        v = c.validate_v1(doc)
        if not v["ok"] or doc.get("contract_id") != c.fingerprint(doc):
            bad.append(name)
    add("F2", not bad and len(examples) == 2, "examples={} bad={}".format(len(examples), bad))

    core = {k: v for k, v in spec.items() if k not in ("spec_digest", "examples", "verify")}
    canon = json.dumps(core, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    want = hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16]
    add("F3", spec.get("spec_digest") == want,
        "declared={} recomputed={}".format(spec.get("spec_digest"), want))

    rules = [r.get("id") for r in spec.get("rules", [])]
    add("F4", rules == ["V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8"], "rules={}".format(rules))

    verdict = "PASS" if all(x["ok"] for x in checks) else "FAIL"
    print(json.dumps({"batch": "B1b", "frozen": FROZEN, "verdict": verdict,
                      "failed": [x["id"] for x in checks if not x["ok"]],
                      "checks": checks}, ensure_ascii=False, indent=2))
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
