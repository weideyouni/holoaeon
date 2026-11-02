# -*- coding: utf-8 -*-
"""B1b 同参指纹互认实验（确定性、可跨进程复跑）。

用法：
  python scripts/contract_interop.py --out reports/contract_v1_interop_a.json
  python scripts/contract_interop.py --out reports/contract_v1_interop_b.json
  python scripts/contract_interop_final.py          # 比对两次运行并落最终回执

判据：
  I1 同一 body 两次构造 → 指纹相等（跨进程由两次独立运行比对字节证明）
  I2 payload 改一个键 → 指纹不同
  I3 nonce 不进指纹 → 再加 nonce 指纹不变
  I4 全部样本 validate_v1 通过
输出不含时间戳，保证两次运行字节一致。
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from holoaeon.fusion_upgrade import contract as c

RED = {"zero_dose": True, "c0_not_efficacy": True, "emergency_120": True}


def samples():
    general = {"source": "local", "target": "gitee", "skill": "fusion_contract",
               "mechanism": "semantic_bus", "lane": "read",
               "payload": {"domain": "general", "notes": "B1b 最小样本"}}
    medical = {"source": "local", "target": "ivsa", "skill": "fusion_plan",
               "mechanism": "meridian", "lane": "read",
               "payload": {"domain": "medical", "inputs": {"case_id": "R-001"},
                           "evidence": {"sha256": "98940b774566543b"},
                           "redlines": dict(RED), "notes": "只交换契约，不搬代码"}}
    changed = json.loads(json.dumps(general))
    changed["payload"]["notes"] = "改一个键"
    with_nonce = json.loads(json.dumps(general))
    with_nonce["nonce"] = "n-20261102-01"
    return {"general": general, "medical": medical, "changed": changed, "with_nonce": with_nonce}


def run():
    raw = samples()
    docs = {}
    for name, body in raw.items():
        doc = c.build(**{k: v for k, v in body.items() if k != "payload"},
                      payload=body.get("payload"))
        if "nonce" in body:
            doc["nonce"] = body["nonce"]
        docs[name] = doc

    # I1：同参再构造一次
    again = c.build(source="local", target="gitee", skill="fusion_contract",
                    mechanism="semantic_bus", lane="read",
                    payload={"domain": "general", "notes": "B1b 最小样本"})

    rows = []
    for name in ("general", "medical", "changed", "with_nonce"):
        doc = docs[name]
        v = c.validate_v1(doc)
        rows.append({"name": name, "contract_id": doc["contract_id"],
                     "valid": v["ok"], "errors": v["errors"]})

    result = {
        "experiment": "B1b-cross-process-fingerprint",
        "dna_id": "SG-DNA-FIVE-SITE-SYNC-V1.1",
        "fingerprint_rule": "sha256(canonical(source,target,skill,mechanism,lane,payload))[:12]",
        "samples": rows,
        "same_params_equal": docs["general"]["contract_id"] == again["contract_id"],
        "payload_changed_differs": docs["general"]["contract_id"] != docs["changed"]["contract_id"],
        "nonce_not_in_fingerprint": c.fingerprint(docs["general"]) == c.fingerprint(docs["with_nonce"]),
        "all_valid": all(r["valid"] for r in rows),
    }
    return result


def main(argv):
    result = run()
    out = None
    if "--out" in argv:
        idx = argv.index("--out")
        if idx + 1 < len(argv):
            out = argv[idx + 1]
    text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
    if out:
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            f.write(text + "\n")
    print(text)
    ok = (result["same_params_equal"] and result["payload_changed_differs"]
          and result["nonce_not_in_fingerprint"] and result["all_valid"])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
