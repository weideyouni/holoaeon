"""稳定语料探针：只在技能自述上建索引（与 docs/ 文档无关），网格扫 vocab×weight×floor。
一次性诊断脚本，不入交付物。"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import holoaeon.semvec as sv  # noqa: E402
from holoaeon.kernel import Kernel  # noqa: E402
from holoaeon.semvec import SemanticIndex, _cosine, docs_from_skills, tokenize as base_tokenize  # noqa: E402
from holoaeon.packs import PACK_ORDER, get_pack  # noqa: E402

INTENTS = [
    ("统计字数：HoloAeon 是零依赖的确定性多智能体认知框架。", "word_count"),
    ("患者数据统计", "basic_stats"),
    ("给这列数据算均值和标准差", "basic_stats"),
    ("计算夏普比率", "sharpe"),
    ("计算收益率", "returns"),
    ("最大回撤是多少", "drawdown"),
    ("读一下这篇论文的摘要", "extract_abstract"),
    ("筛一下相关文献", "screen_papers"),
    ("去重论文列表", "dedup_papers"),
    ("写周报总结", "weekly_review"),
    ("拆解一下这个任务", "task_breakdown"),
    ("设计实验的样本量", "sample_size"),
]


def build_kernel():
    k = Kernel()
    for key in PACK_ORDER:
        get_pack(key).install(k)
    return k


def route(k, index, query, weight, floor):
    skills = k.skills.all()
    q_tokens = base_tokenize(query)
    q_vec = index.encode(query)
    base_raw, sem_raw = [], []
    for s in skills:
        base_raw.append(k.skills.score(s, q_tokens, query))
        sem_raw.append(_cosine(q_vec, index.encode(" ".join(
            [s.manifest.name, s.manifest.description] + list(s.manifest.tags)))))
    bmin, bmax = min(base_raw), max(base_raw)
    smin, smax = min(sem_raw), max(sem_raw)
    bspan = (bmax - bmin) or 1.0
    sspan = (smax - smin) or 1.0
    peak = bmax
    scale = min(1.0, peak / floor) if floor > 0 else 1.0
    scored = []
    for s, b, se in zip(skills, base_raw, sem_raw):
        bn = (b - bmin) / bspan
        sn = (se - smin) / sspan
        mix = (1.0 - weight) * scale * bn + weight * sn
        scored.append((round(mix, 6), round(sn, 6), round(bn, 6), s.manifest.name))
    scored.sort(key=lambda t: (-t[0], -t[1], -t[2], t[3]))
    return scored[0][3]


def main():
    k = build_kernel()
    docs = docs_from_skills(k.skills.all())
    print("stable corpus docs = %d" % len(docs))
    for vocab in (300, 800, 1200, 2000):
        sv.MAX_VOCAB = vocab
        idx = SemanticIndex()
        idx.fit(docs)
        for weight in (0.6, 0.7, 0.75, 0.8):
            for floor in (0.10, 0.15, 0.20):
                hits = sum(1 for q, want in INTENTS if route(k, idx, q, weight, floor) == want)
                print("vocab=%-5d w=%.2f floor=%.2f -> %2d/12" % (vocab, weight, floor, hits))


if __name__ == "__main__":
    main()
