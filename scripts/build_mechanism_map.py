# -*- coding: utf-8 -*-
"""B2a 六机制 1:1 映射表构建：data/mechanism_map.json

用法：
  python scripts/build_mechanism_map.py
  python scripts/build_mechanism_map.py --check     # 只比对，不落盘（供校验器调用）

口径（写在文件里，不靠记忆）：
  · 1:1 = 一个机制对一行，六机制恰好六行；不许一对多、不许多对一
  · 单向 = holoaeon 侧归属 → ivsa 侧机制，只做归属映射；编号、主体、号段一律不互推
  · 每行必有 mapping_rule（即"可以怎么用"），没有规则的行等于没映射
  · evidence_class=simulated：仿真≠证明，碳基终裁
不写时间戳，复跑字节一致。
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from holoaeon.fusion_upgrade import contract as c

OUT = os.path.join(ROOT, "data", "mechanism_map.json")

DIRECTION = "one-way: holoaeon→ivsa（只映射归属，不互推编号/主体/号段）"


def rows():
    out = []
    for i, p in enumerate(c.PAIRS, 1):
        out.append({
            "id": "MM-%02d" % i,
            "mechanism": p["mechanism"],
            "cn": p["cn"],
            "holo_side": p["holo"],
            "ivsa_side": p["ivsa"],
            "same": list(p["same"]),
            "diff": list(p["diff"]),
            "mapping_rule": p["bridge"],
            "direction": DIRECTION,
            "cardinality": "1:1",
            "status": "mapped",
            "evidence_class": "simulated",
        })
    return out


def digest_of(rows_list):
    canon = json.dumps(rows_list, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16]


def build():
    rs = rows()
    return {
        "map_id": "SG-MECHANISM-MAP-HOLOAEON-IVSA-V1",
        "batch": "B2a",
        "frozen_at": "2026-11-02",
        "evidence_class": "simulated",
        "cardinality": "1:1",
        "direction": DIRECTION,
        "mechanisms": list(c.MECHANISMS),
        "rows": rs,
        "row_count": len(rs),
        "map_digest": digest_of(rs),
        "rules": [
            {"id": "M1", "text": "六机制恰好六行，机制名与 contract.MECHANISMS 同序"},
            {"id": "M2", "text": "每行 mapping_rule 非空且 >= 6 字，否则视为未映射"},
            {"id": "M3", "text": "direction 全局单向，禁止双向/回写"},
            {"id": "M4", "text": "map_digest 可复算，改一个字符即变"},
            {"id": "M5", "text": "每行 same / diff 至少各一条，差异必须写出来"},
            {"id": "M6", "text": "行内容与 contract.PAIRS 逐字段一致，禁止文档与代码各写一套"},
        ],
        "non_goals": [
            "不合并编号空间（70 ≢ 1229、17 ≢ 12）",
            "不做通道映射（12→17 属 B2b）",
            "不搬运 meridian_mechanism.py / mech.py 代码",
        ],
    }


def main(argv):
    doc = build()
    text = json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=True)
    if "--check" in argv:
        if not os.path.isfile(OUT):
            print(json.dumps({"verdict": "FAIL", "reason": "missing " + OUT}, ensure_ascii=False))
            return 1
        with open(OUT, encoding="utf-8") as f:
            cur = json.load(f)
        same = cur == doc
        print(json.dumps({"verdict": "PASS" if same else "FAIL", "byte_consistent": same,
                          "map_digest": doc["map_digest"]}, ensure_ascii=False))
        return 0 if same else 1
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(text + "\n")
    print(json.dumps({"out": OUT, "row_count": doc["row_count"],
                      "map_digest": doc["map_digest"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
