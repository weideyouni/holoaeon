# -*- coding: utf-8 -*-
"""V5.0 康复域知识库全量入库（只读索引，不复制正文）。

输入（全部只读）：
- 客仓 ivsa `data/*.csv`（9 张康复域表）+ `knowledge/` 目录清单
- 本仓康复域既有件：rehab_pilot_20.json / three_field_cards.json / skin_lexicon_rehab.json

输出：data/v5_rehab_kb.json（SG-V5-REHAB-KB-V1）
约束：不改 ivsa 任何文件、不改 25/47/9、不裁正文、不把 ivsa 词条正文搬进本仓（只存 rows/bytes/sha256/路径）。
"""
import csv
import hashlib
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IVSA = r"F:\doubaowork\开源发布_中西医融合康复工程_20261026\integrative-rehab-vsa"
OUT = os.path.join(ROOT, "data", "v5_rehab_kb.json")

REDLINE = {
    "zero_dose": "不写剂量、不给参数",
    "no_diagnosis": "不做诊断、不出结论",
    "no_device": "不接设备、不启动网关",
    "emergency_120": "急症转 120",
    "no_original_text": "只存索引与哈希，不复制客仓正文",
    "no_efficacy_claim": "仿真 ≠ 证明，不外推疗效",
}


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(65536), b""):
            h.update(c)
    return h.hexdigest()


def csv_meta(p):
    with open(p, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    return {"rows": max(0, len(rows) - 1), "header": rows[0] if rows else [],
            "bytes": os.path.getsize(p), "sha256": sha256(p)}


entries = []

# 1) 客仓数据表（只读引用）
data_dir = os.path.join(IVSA, "data")
for name in sorted(os.listdir(data_dir)):
    p = os.path.join(data_dir, name)
    if not os.path.isfile(p) or not name.lower().endswith(".csv"):
        continue
    m = csv_meta(p)
    entries.append({
        "entry_id": "KB-IVSA-DATA-" + name.split("_")[0].upper(),
        "layer": "ivsa_data",
        "source": "ivsa/data/" + name,
        "access": "read_only",
        "rows": m["rows"],
        "bytes": m["bytes"],
        "sha256": m["sha256"],
        "header_columns": len(m["header"]),
        "copied": False,
        "note": "只登记行数与哈希；正文留在客仓，本仓不含其文字。",
    })

# 2) 客仓知识目录（目录级清单，不逐篇复制）
kdir = os.path.join(IVSA, "knowledge")
kfiles, kbytes = 0, 0
subdirs = []
for dp, dns, fns in os.walk(kdir):
    rel = os.path.relpath(dp, kdir).replace(os.sep, "/")
    if rel == ".":
        subdirs = sorted(dns)
    kfiles += len(fns)
    kbytes += sum(os.path.getsize(os.path.join(dp, f)) for f in fns)
entries.append({
    "entry_id": "KB-IVSA-KNOWLEDGE",
    "layer": "ivsa_knowledge",
    "source": "ivsa/knowledge/",
    "access": "read_only",
    "files": kfiles,
    "bytes": kbytes,
    "subdirs": subdirs,
    "copied": False,
    "note": "目录级清单；正文不外借，避免医学文字被二次误用。",
})

# 3) 本仓康复域既有件
own = [
    ("KB-HOLO-REHAB-PILOT", "data/rehab_pilot_20.json", "康复域试点 20 例（只映射不调用）"),
    ("KB-HOLO-THREE-FIELD", "data/three_field_cards.json", "三场卡 13 张（含 4 张 gap）"),
    ("KB-HOLO-SKIN-REHAB", "data/skin_lexicon_rehab.json", "皮肤词表康复域分域"),
    ("KB-HOLO-SEMANTIC", "data/semantic_family.json", "语义族（康复域候选未准入者不并入）"),
]
for eid, rel, note in own:
    p = os.path.join(ROOT, rel.replace("/", os.sep))
    if not os.path.isfile(p):
        continue
    entries.append({
        "entry_id": eid,
        "layer": "holoaeon",
        "source": rel,
        "access": "read_only",
        "bytes": os.path.getsize(p),
        "sha256": sha256(p),
        "copied": True,
        "note": note,
    })

totals = {"entries": len(entries),
          "ivsa_rows": sum(e.get("rows", 0) for e in entries if e["layer"] == "ivsa_data"),
          "ivsa_knowledge_files": kfiles,
          "holoaeon_entries": sum(1 for e in entries if e["layer"] == "holoaeon")}

payload = {
    "id": "SG-V5-REHAB-KB-V1",
    "batch": "V5.0-B1",
    "created_at": "2026-11-02",
    "version": "1.0",
    "principle": "全量入库 = 全量登记（行数/字节/哈希/红线），不是全量复制；正文留在客仓，本仓只做索引与门禁。",
    "scope": "康复域：ivsa 9 张数据表 + knowledge 目录 + 本仓 4 件康复域既有件",
    "lock": {"agents": 25, "skills": 47, "packs": 9,
             "note": "入库不改锁数；新增内容以索引形式旁挂。"},
    "shadow_dimension": {
        "id": "SG-V5-DIM-SHADOW-REHAB-V1",
        "slot": "EXT-DIM-02",
        "name": "D_REHAB 康复域影子维度",
        "participates_in_dimension_lock": False,
        "affects_diff0_hash": False,
        "usage": "仅用于康复域检索排序与命中解释；不进 D01–D14，不改指纹。",
        "weight_policy": "只做排序权重 0.1–0.3，禁止用它改写既有 12 维度结论。"
    },
    "evidence_register": {
        "id": "SG-V5-EVIDENCE-REGISTER-V1",
        "slot": "EXT-EVIDENCE-01",
        "tier_unchanged": True,
        "cards": [
            {"card_id": "TF-M-05", "field": "magnetic", "tier_before": "none", "tier_after": "none",
             "status": "awaiting_manual_review",
             "review_requires": ["原文可获取", "人群/分期明确", "参数完整", "结局定义清晰"]},
            {"card_id": "TF-E-01", "field": "electric", "tier_before": "none", "tier_after": "none",
             "status": "awaiting_manual_review",
             "review_requires": ["原文可获取", "人群/分期明确", "参数完整", "结局定义清晰"]},
            {"card_id": "TF-E-02", "field": "electric", "tier_before": "none", "tier_after": "none",
             "status": "awaiting_manual_review",
             "review_requires": ["原文可获取", "人群/分期明确", "参数完整", "结局定义清晰"]},
            {"card_id": "TF-E-03", "field": "electric", "tier_before": "none", "tier_after": "none",
             "status": "awaiting_manual_review",
             "review_requires": ["原文可获取", "人群/分期明确", "参数完整", "结局定义清晰"]},
        ],
        "note": "解封 = 允许人工逐篇核对流程；未核对前 tier 一律 none，禁止批量上调。"
    },
    "redlines": REDLINE,
    "totals": totals,
    "entries": entries,
}

with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)
    f.write("\n")

print(json.dumps({"out": OUT, "bytes": os.path.getsize(OUT), "totals": totals}, ensure_ascii=False))
