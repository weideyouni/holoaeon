# -*- coding: utf-8 -*-
"""B3 用途二次分类：1229 条技能 → K/M/T/X/U 五值 → data/skill_usage_labels.csv

用法：
  python scripts/classify_skill_usage.py            # 生成 CSV + 分布回执
  python scripts/classify_skill_usage.py --check    # 复跑字节一致性

判定口径（确定性，无随机、无时间戳）：
  stage1 逐类打分：score(c) = Σ(关键词权重 × 命中) + 0.6 × 2~4 字滑窗重叠率
         —— 逐条对各标签打分再取最大，绝不用"整类文本聚合"打分（那样所有条目会塌到同一类）。
         argmax 且 max >= TH 才算判定；否则进 stage2。
  stage2 兜底：按索引侧 domain / mechanism 查表定性；仍无依据则标 U（待判）。
  U 上限：判据要求待判 <= 20，超出即视为分类器失效而不是"数据太怪"。

标签语义：
  K 知识源：提供内容/资料/知识结构，可被检索与引用
  M 方法学：提供方法/模型/算法/流程/范式，可被调用为"怎么做"
  T 工具链：提供可执行的命令、脚本、部署与平台能力
  X 无关：与中西医融合康复域无关，明确不纳入
  U 待判：证据不足，挂账不猜
"""
import csv
import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "data", "skill_matrix_index.json")
CSV_OUT = os.path.join(ROOT, "data", "skill_usage_labels.csv")
HEADER = ["name", "domain", "mechanism", "lane", "label", "score", "stage", "reason"]

TH = 0.80
TH_WEAK = 0.35   # 弱证据档：仅用于索引域未归域的条目，低于此判 U 挂账

# 关键词权重：域名词面证据，不做同义词扩张，避免误伤
KW = {
    "K": {"知识": 1.2, "导学": 1.0, "学派": 0.9, "医案": 0.9, "文献": 1.0, "教材": 1.0,
          "经典": 1.0, "讲稿": 0.9, "讲义": 0.9, "传承": 0.8, "综述": 0.8, "词条": 0.8,
          "方剂": 0.7, "本草": 0.7, "内经": 0.8, "伤寒": 0.8, "百科": 0.8, "典籍": 0.8,
          "ontology": 1.0, "知识库": 1.2, "索引": 0.6, "图谱": 0.8, "概览": 0.8,
          "archive": 0.8, "corpus": 0.8, "timeline": 0.6, "规范": 0.7},
    "M": {"方法": 1.2, "方法论": 1.2, "框架": 1.0, "矩阵": 0.9, "体系": 0.9, "机制": 1.0,
          "模型": 1.0, "算法": 1.0, "算子": 1.0, "流程": 1.0, "sop": 1.0, "协议": 0.9,
          "策略": 0.9, "推理": 0.9, "范式": 1.0, "拆解": 0.8, "定位": 0.6, "解析": 0.7,
          "判定": 0.8, "分类": 0.6, "建模": 0.8, "调度": 0.8, "校准": 0.7, "打分": 0.7,
          "design": 0.6, "analysis": 0.6, "pipeline": 0.9, "迭代": 0.7, "打磨": 0.6,
          "车间": 1.0, "匹配": 0.7, "收敛": 0.8, "调度": 0.8},
    "T": {"工具": 1.2, "脚本": 1.2, "cli": 1.2, "命令": 1.0, "操作": 1.0, "基准": 1.2,
          "引导": 0.9, "适配": 1.0, "安装": 1.0, "部署": 1.2, "路由": 1.0, "api": 1.0,
          "mcp": 1.0, "打包": 0.9, "上传": 0.8, "下载": 0.8, "渲染": 0.8, "docker": 1.2,
          "向量库": 0.9, "bridge": 0.9, "热插拔": 0.9, "网关": 0.9, "codec": 0.9,
          "sidecar": 0.9, "harness": 0.9, "质检": 1.2, "检测": 0.6, "读取": 0.7, "编辑": 0.7,
          "交由": 0.8, "自动化": 0.6},
    "X": {"娱乐": 1.0, "星座": 1.0, "彩票": 1.0, "游戏攻略": 1.0, "八卦": 1.0, "影视": 0.8,
          "小说": 0.8, "美食": 0.8, "旅游": 0.8, "穿搭": 0.8, "美妆": 0.8, "宠物": 0.6,
          "股票": 0.6, "量化交易": 0.8, "招聘": 0.6, "房产": 0.6,
          # 农业/养殖/园艺类：与中西医融合康复域无关，属明确不纳入（写进票据，不藏着）
          "养殖": 1.0, "鱼塘": 1.0, "鹅": 0.8, "藻": 0.8, "朴门": 1.0, "果园": 0.8,
          "化肥": 0.8, "农药": 0.8, "蚯蚓": 0.8, "梯级水系": 0.8,
          # 纯想象/猎奇场景：不属于康复域
          "虫洞": 1.0, "星际": 0.8, "探险": 0.8, "趣味": 0.6},
}

# stage2 兜底：索引侧既有字段 → 标签（依据单一，不叠加猜测）
DOMAIN_FALLBACK = {
    "literature": "K", "gaoyi": "K",
    "research": "M", "optimization": "M", "quant": "M",
    "data": "T", "growth": "T",
    "writing": "X", "business": "X",
    "unmapped": "U",
}
MECH_FALLBACK = {
    "meridian": "M", "cytoskeleton": "M",
    "semantic_bus": "T", "skin_v6": "M", "holographic_heartbeat": "M",
    "hebbian_field": "M", "unmapped": "U",
}


def shingles(text, lo=2, hi=4):
    out = set()
    for i in range(len(text)):
        for n in range(lo, hi + 1):
            if i + n <= len(text):
                out.add(text[i:i + n])
    return out


def overlap_rate(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / float(len(a))


def score_all(text, ref_shingles):
    sc = {}
    low = text.lower()
    for label, kws in KW.items():
        s = 0.0
        for w, weight in kws.items():
            if w in low:
                s += weight
        s += 0.6 * overlap_rate(shingles(text), ref_shingles[label])
        sc[label] = round(s, 4)
    return sc


def refs_by_label():
    return {label: shingles("".join(kws.keys())) for label, kws in KW.items()}


def classify(rec, ref):
    text = (rec.get("name", "") + " " + rec.get("description", "")).strip()
    sc = score_all(text, ref)
    order = ["K", "M", "T", "X"]
    best = max(order, key=lambda k: (sc[k], -order.index(k)))
    if sc[best] >= TH:
        return best, sc[best], "stage1", "kw+shingle argmax={} score={}".format(best, sc[best])
    d = DOMAIN_FALLBACK.get(rec.get("domain"), "U")
    has_domain_evidence = (rec.get("domain_score") or 0) > 0 and rec.get("domain") != "unmapped"
    if d != "U" and has_domain_evidence:
        return d, sc[best], "stage2", "domain 定性={}（索引域有证据，score={}）".format(
            d, rec.get("domain_score"))
    if sc[best] >= TH_WEAK:
        return best, sc[best], "stage2-weak", "弱证据 argmax={} score={}（域未归域，仅词面）".format(
            best, sc[best])
    return "U", sc[best], "undecided", "domain={} mechanism={} 证据不足（score={}<{}）".format(
        rec.get("domain"), rec.get("mechanism"), sc[best], TH_WEAK)


def build():
    with open(INDEX, encoding="utf-8") as f:
        idx = json.load(f)
    ref = refs_by_label()
    rows = []
    for rec in idx["skills"]:
        label, score, stage, reason = classify(rec, ref)
        rows.append({"name": rec.get("name", ""), "domain": rec.get("domain", ""),
                     "mechanism": rec.get("mechanism", ""), "lane": rec.get("lane", ""),
                     "label": label, "score": "{:.4f}".format(score), "stage": stage,
                     "reason": reason})
    counts = {"K": 0, "M": 0, "T": 0, "X": 0, "U": 0}
    for r in rows:
        counts[r["label"]] += 1
    digest = hashlib.sha256(
        json.dumps(rows, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()[:16]
    return rows, counts, digest


def csv_text(rows):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=HEADER, lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow(r)
    return buf.getvalue()


def main(argv):
    rows, counts, digest = build()
    text = csv_text(rows)
    if "--check" in argv:
        if not os.path.isfile(CSV_OUT):
            print(json.dumps({"verdict": "FAIL", "reason": "missing"}, ensure_ascii=False))
            return 1
        with open(CSV_OUT, encoding="utf-8") as f:
            same = f.read() == text
        print(json.dumps({"verdict": "PASS" if same else "FAIL", "byte_consistent": same,
                          "digest": digest, "counts": counts}, ensure_ascii=False))
        return 0 if same else 1
    with open(CSV_OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(json.dumps({"out": CSV_OUT, "rows": len(rows), "counts": counts,
                      "digest": digest, "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
