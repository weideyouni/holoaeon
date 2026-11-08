# -*- coding: utf-8 -*-
"""bench_vector_baseline — 轻量级向量库基线测试（V47）
用户需求：先做基线测试。确定性语料+实测数字（零虚构：本脚本输出的
数字即投喂包 §基线报告数字的来源）。跑法：
  python scripts/bench_vector_baseline.py
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holoaeon.deploy_gate import VectorStore  # noqa: E402

# 确定性语料：6 系统 × 10 句式模板 = 60 条知识句（零随机）
TEMPLATES = [
    "{s}患者应定期复查相关指标并做好记录",
    "{s}的日常管理包括生活方式干预与依从性教育",
    "{s}稳定期以常规随访为主，控制不满意时加密随访频次",
    "{s}合并多种慢病时须综合评估并整合随访安排",
    "{s}的健康指导应个体化，结合患者实际条件",
    "{s}急性加重的识别与及时转诊是管理关键环节",
    "{s}康复训练应循序渐进并定期评估效果",
    "{s}患者的自我监测与自我管理能力决定长期效果",
    "{s}的中医药调理可融入全流程健康管理",
    "{s}高危人群的早期筛查有助于延缓疾病进展",
]
SYSTEMS = ("高血压", "2型糖尿病", "慢阻肺病", "冠心病", "脑卒中后遗症",
           "骨质疏松")

# 同义改写查询（测语义召回——不是字面匹配；诚实边界：字面通道天花板）
PARAPHRASE_QUERIES = {
    "高血压": "血压高的病人平时要注意什么，定期量血压记下来",
    "2型糖尿病": "血糖高的人日常怎么管，生活上怎么干预",
    "脑卒中后遗症": "中风后半边身子不利索，怎么做恢复锻炼",
}

# 字面查询对照组（positive control：通道本身有效性验证）
LITERAL_QUERIES = {
    "高血压": "高血压患者应定期复查相关指标并做好记录",
    "慢阻肺病": "慢阻肺病急性加重的识别与及时转诊是管理关键环节",
    "骨质疏松": "骨质疏松的康复训练应循序渐进并定期评估效果",
}


def build_corpus():
    entries = []
    for si, sys_name in enumerate(SYSTEMS):
        for ti, tpl in enumerate(TEMPLATES):
            eid = "k%02d_%02d" % (si, ti)
            entries.append((eid, tpl.format(s=sys_name),
                            {"system": sys_name}))
    return entries


def _hit(store, queries, top_k=5):
    lat, top1, top5 = [], 0, 0
    for sys_name, q in queries.items():
        res = store.search(q, top_k=top_k)
        lat.append(res["latency_ms"])
        ids = [h["meta"].get("system") for h in res["hits"]]
        top1 += 1 if ids and ids[0] == sys_name else 0
        top5 += 1 if sys_name in ids else 0
    return lat, top1, top5, len(queries)


def main():
    store = VectorStore(dim=256)
    entries = build_corpus()

    t0 = time.perf_counter()
    r = store.batch_add(entries)
    add_ms = round((time.perf_counter() - t0) * 1000, 1)

    lat_l, t1_l, t5_l, n_l = _hit(store, LITERAL_QUERIES)
    lat_p, t1_p, t5_p, n_p = _hit(store, PARAPHRASE_QUERIES)

    report = {
        "corpus_entries": r["added"],
        "add_batch_ms": add_ms,
        "dim": 256,
        "literal_group": {
            "queries": n_l,
            "top1_hit_rate": round(t1_l / n_l, 4),
            "top5_hit_rate": round(t5_l / n_l, 4),
            "avg_latency_ms": round(sum(lat_l) / n_l, 3),
            "note": "字面查询对照组（positive control）",
        },
        "paraphrase_group": {
            "queries": n_p,
            "top1_hit_rate": round(t1_p / n_p, 4),
            "top5_hit_rate": round(t5_p / n_p, 4),
            "avg_latency_ms": round(sum(lat_p) / n_p, 3),
            "note": "同义改写组——字面混合通道的诚实天花板：跨词汇语义"
                    "召回需共现统计语料(semvec 路线)或 bridges 层神经旁挂",
        },
        "channel": "hybrid=0.6*trigram_cos + 0.4*bigram_dice",
        "deterministic": True,
        "note": "确定性语料（模板×系统，零随机）；混合通道为基线驱动优化"
                "（纯 trigram 同义组 Top5=0.0）",
    }
    import json
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


if __name__ == "__main__":
    main()
