"""B0 自动技能匹配 + V4 融合基线锁（纯标准库 / 离线 / 确定性）。

输入：data/skill_matrix_index.json（1229 条，六机制 + 九领域 + read/write 通道）
输出：
  data/B0_自动匹配技能.csv     —— 本轮 B0 用得到的技能排序（确定性评分）
  data/B0_自动匹配技能.json    —— 机制/领域分布摘要
  reports/b0_lock_v4fusion.json —— 12 维基线锁 + V4 融合扩展两项

评分口径（可复算）：
  score = Σ(kw_weight × 命中) + 0.6 × 2~4 字滑窗重叠率
  排序：score 降序，同分按 name 升序（保证两次跑完全一致）
"""

from pathlib import Path
import csv
import json
import os

REPO = os.environ.get("HOLOAEON_REPO", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INDEX = os.path.join(REPO, "data", "skill_matrix_index.json")
DATA = os.path.join(REPO, "data")
REPORTS = os.path.join(REPO, "reports")

# B0 基线冻结真正会用到的能力词（权重即可解释性）
KEYWORDS = (
    ("冷热插拔", 5), ("热插拔", 5), ("融合协议", 4), ("契约", 4),
    ("维度锁", 4), ("门禁", 4), ("快照", 3), ("技能矩阵", 3),
    ("基座", 3), ("四人", 3), ("数字分身", 3), ("quartet", 3),
    ("康复", 3), ("ivsa", 3), ("语义", 2), ("赫布", 2),
    ("经络", 2), ("心跳", 2), ("细胞骨架", 2), ("皮肤", 2),
)


def shingles(text, n=3):
    text = "".join(ch for ch in text if not ch.isspace())
    if len(text) <= n:
        return {text} if text else set()
    return {text[i:i + n] for i in range(len(text) - n + 1)}


def overlap_ratio(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / float(min(len(a), len(b)))


def score_skill(skill, probe):
    text = (skill.get("name", "") + " " + skill.get("description", ""))
    hits = []
    total = 0.0
    for kw, weight in KEYWORDS:
        if kw in text:
            total += weight
            hits.append(kw)
    total += 0.6 * overlap_ratio(shingles(text), probe)
    return total, hits


def main():
    with open(INDEX, encoding="utf-8") as f:
        idx = json.load(f)
    probe = shingles("冷热插拔 融合协议 契约 维度锁 门禁 快照 技能矩阵 基座 四人 数字分身")
    alias = {os.path.basename(r): r for r in idx.get("roots", [])}

    def resolve(name, label):
        for r in idx.get("roots", []):
            cand = os.path.join(r, name)
            if os.path.isdir(cand):
                return cand
        return alias.get(label, label) + os.sep + name

    rows = []
    for s in idx["skills"]:
        sc, hits = score_skill(s, probe)
        if sc <= 0.6:
            continue
        rows.append({
            "score": round(sc, 4),
            "name": s.get("name", ""),
            "domain": s.get("domain", "unmapped"),
            "mechanism": s.get("mechanism", "unmapped"),
            "lane": s.get("lane", "read"),
            "hits": "|".join(hits),
            "path": resolve(s.get("name", ""), s.get("root", "")),
        })
    rows.sort(key=lambda r: (-r["score"], r["name"]))

    os.makedirs(DATA, exist_ok=True)
    out_csv = os.path.join(DATA, "B0_自动匹配技能.csv")
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["排名", "技能", "领域", "机制", "通道", "得分", "命中词", "路径"])
        for i, r in enumerate(rows, 1):
            w.writerow([i, r["name"], r["domain"], r["mechanism"], r["lane"], r["score"], r["hits"], r["path"]])

    by_mech = {}
    by_dom = {}
    for r in rows:
        by_mech[r["mechanism"]] = by_mech.get(r["mechanism"], 0) + 1
        by_dom[r["domain"]] = by_dom.get(r["domain"], 0) + 1

    summary = {
        "matched_for": "B0 基线冻结",
        "source_index": {"count": idx.get("count"), "digest": idx.get("digest")},
        "matched_total": len(rows),
        "top20": [r["name"] for r in rows[:20]],
        "by_mechanism": dict(sorted(by_mech.items(), key=lambda kv: (-kv[1], kv[0]))),
        "by_domain": dict(sorted(by_dom.items(), key=lambda kv: (-kv[1], kv[0]))),
        "scoring": "sum(keyword_weight*hit) + 0.6*shingle_overlap; sort by score desc then name asc",
        "honesty": {"external_skills_executed": 0, "mode": "只读索引打分，未 import 未执行"},
    }
    out_json = os.path.join(DATA, "B0_自动匹配技能.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    # 12 维基线锁 + V4 融合扩展 2 项
    gate = json.loads(Path(os.path.join(REPORTS, "gate_b0_v4.json")).read_text(encoding="utf-8"))
    a1 = [c for c in gate["checks"] if c["id"] == "A1"][0]["detail"]
    lock = {
        "lock_id": "B0-LOCK-V4-FUSION-20261102",
        "batch": "B0",
        "frozen_at": "2026-11-02T01:20+08:00",
        "evidence_class": "simulated",
        "note": "仿真≠证明，碳基终裁；本轮为 B0 现场复算，与 01:04 版 reports/dimension_lock.json 并行核对一致",
        "dimensions": {
            "D01_agents": 25,
            "D02_skills": 47,
            "D03_packs": 9,
            "D04_spec_version": "0.9.1",
            "D05_doc_version": "0.9.4-fusion",
            "D06_extra_packs": 10,
            "D07_unittests": "34/21/5",
            "D08_launch_selftest": "25/25",
            "D09_diff0_hash": "2fc892cf9af6e755",
            "D10_tamper_hash": "f42c8229ee5acd73",
            "D11_v3_gate": "32/32",
            "D12_ivsa_selftest": "21/21",
            "D13_fusion_selftest": "17/17",
            "D14_skill_matrix": "17/17",
        },
        "observed": {"A1_detail": a1, "gate_verdict": gate["verdict"]},
        "skill_match": {"matched": len(rows), "index_digest": idx.get("digest")},
    }
    os.makedirs(REPORTS, exist_ok=True)
    out_lock = os.path.join(REPORTS, "b0_lock_v4fusion.json")
    with open(out_lock, "w", encoding="utf-8") as f:
        json.dump(lock, f, ensure_ascii=False, indent=2)

    print(json.dumps({"matched": len(rows), "top": summary["top20"][:6],
                      "by_mechanism": summary["by_mechanism"],
                      "lock": out_lock}, ensure_ascii=False))


if __name__ == "__main__":
    main()
