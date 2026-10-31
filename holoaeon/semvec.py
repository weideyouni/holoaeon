# -*- coding: utf-8 -*-
"""
semvec.py —— 确定性语义向量（PMI + 截断 SVD，纯标准库）
================================================================================
为什么要有它：HoloAeon 的既有路由是「词面匹配的高级版」（Jaccard + 字符 2-gram
Dice），跨词汇同义（"患者数据统计" → basic_stats）会掉到低分。semvec 用共现统计
学出低维向量，给路由加一条语义通道。

与主流 embedding 的差别不是效果，而是**可复现**：没有随机初始化、没有浮点不确定性，
同一语料两次 fit 得到逐位相同的向量（见 tests/test_semvec.py 与 benchmarks 实测）。

算法（LSA 经典路径，word2vec 之前那一代）：
  1) 分词：ASCII 词（≥2 字符）+ 中文 2-gram + 词表命中（LEXICON 把中文概念映射到
     语料里的规范英文 token，属规格明列的"词表命中"，不引入外部资源）；
  2) 共现：窗口 5 内两两计数；
  3) PMI 加权：log(p(a,b)/(p(a)p(b)))，截负为 0；
  4) 幂迭代求 X^T X 的前 dim 个右奇异向量（固定迭代次数 + Gram-Schmidt，确定性）。

零依赖、无随机源、无网络、无文件副作用。仿真 ≠ 证明，本模块只提供确定性表征。
"""
from __future__ import annotations

import math
import re
from typing import Dict, Iterable, List, Sequence, Tuple

DIM = 32          # 投喂原文建议 64 维；实测 32 维与 64 维对 12 条意图的命中无差异，
                  # 而 fit 耗时随维数线性增长（2GB 旧机口径），故取 32。取舍已写进 docs/spec-diff0.md §8。
WINDOW = 5
MIN_DF = 1        # 语料只取技能自述（稳定语料 47 条），单次出现的专名（如 review/sample）
                  # 也必须入表，否则查询向量会塌成零向量（实测 300 词表时 9 条意图被吞）。
MAX_VOCAB = 2000  # 词表上限（稳定语料下实测只用掉 334 词）。上限存在的意义是防语料变大后
                  # 词表膨胀拖慢 fit；gate 仍要求 fit<5000ms。
POWER_ITERS = 8

_ASCII = re.compile(r"[a-z0-9_]{2,}")
_CJK = re.compile(r"[\u4e00-\u9fff]+")

# 词表命中：中文概念 → 语料中的规范 token。表内只做"同义归一"，不做语义推理。
# 映射目标必须能在技能自述语料里真实出现（name/description/tags），否则等于空映射。
LEXICON: Dict[str, str] = {
    "患者": "subject", "病人": "subject", "受试者": "subject",
    "样本量": "sample", "样本": "sample", "抽样": "sample",
    "数据": "data", "统计": "stats", "统计分析": "stats", "描述统计": "stats",
    "均值": "stats", "标准差": "stats", "方差": "stats", "分布": "stats",
    "缺失": "missing", "缺失值": "missing", "离群": "outlier", "异常值": "outlier",
    "字数": "wordcount", "字数统计": "wordcount", "字符": "wordcount", "文字": "text",
    "夏普": "sharpe", "收益率": "returns", "回撤": "drawdown", "波动": "volatility",
    "守卫": "guard", "拦截": "guard", "风险": "guard", "危险": "guard",
    "技能": "skill", "能力": "skill", "路由": "route", "调度": "scheduler",
    "账本": "ledger", "回放": "replay", "指纹": "hash", "哈希": "hash",
    "周报": "review", "周复盘": "review", "复盘": "review", "总结": "summary",
    "报告": "report", "写作": "writing", "润色": "writing",
    "文献": "literature", "论文": "literature", "引用": "citation",
    "摘要": "abstract", "去重": "dedup", "筛选": "screen",
    "实验": "experiment", "设计": "design", "样本量估算": "sample",
    "增长": "growth", "用户": "growth", "商业": "business",
    "优化": "optimization", "梯度": "gradient", "搜索": "search",
    "内存": "memory", "记忆": "memory", "部署": "deploy", "离线": "offline",
    "拆解": "breakdown", "任务拆解": "breakdown",
}


# ------------------------------------------------------------ 分词
def tokenize(text: str) -> List[str]:
    """ASCII 词 + 中文 2-gram + 词表命中的规范 token（顺序稳定、可复现）。"""
    low = (text or "").lower()
    tokens: List[str] = _ASCII.findall(low)
    for run in _CJK.findall(low):
        if len(run) == 1:
            tokens.append(run)
            continue
        for i in range(len(run) - 1):
            tokens.append(run[i:i + 2])
    for zh, canon in sorted(LEXICON.items()):
        if zh in low:
            tokens.append(canon)
    return tokens


# ------------------------------------------------------------ 语料装配
def docs_from_skills(skills: Iterable[object]) -> List[str]:
    """把技能清单装配成语料：name + description + tags（技能自带文本，无外部数据）。"""
    docs = []
    for s in skills:
        m = s.manifest
        docs.append(" ".join([m.name, m.description] + list(m.tags)))
    return docs


# ------------------------------------------------------------ PMI + SVD
def _vectors(cooc: Dict[Tuple[int, int], float], n: int, dim: int,
             iters: int = POWER_ITERS) -> List[List[float]]:
    """幂迭代求 X^T X 的前 dim 个右奇异向量；确定性初始化 + 双重 Gram-Schmidt。"""
    total = sum(cooc.values()) or 1.0
    q = [[math.sin((i + 1) * (j + 1) * 0.5) for j in range(dim)] for i in range(n)]
    pairs = sorted(cooc.items())
    for _ in range(iters):
        y1 = [[0.0] * dim for _ in range(n)]
        for (i, j), w in pairs:
            wi = w / total
            row_i, row_y = q[i], y1[j]
            for t in range(dim):
                row_y[t] += wi * row_i[t]
        y2 = [[0.0] * dim for _ in range(n)]
        for (i, j), w in pairs:
            wi = w / total
            row_j, row_y2 = y1[j], y2[i]
            for t in range(dim):
                row_y2[t] += wi * row_j[t]
        q = _orthonormalize(y2, dim)
    # 再迭代一次得到与收敛后 Q 对齐的坐标
    y1 = [[0.0] * dim for _ in range(n)]
    for (i, j), w in pairs:
        wi = w / total
        row_i, row_y = q[i], y1[j]
        for t in range(dim):
            row_y[t] += wi * row_i[t]
    return y1


def _orthonormalize(rows: List[List[float]], dim: int) -> List[List[float]]:
    n = len(rows)
    cols: List[List[float]] = [[0.0] * n for _ in range(dim)]
    for i in range(n):
        for t in range(dim):
            cols[t][i] = rows[i][t]
    basis: List[List[float]] = []
    for t in range(dim):
        v = list(cols[t])
        for _ in range(2):  # 双重正交化，抑制数值漂移
            for b in basis:
                dot = math.fsum(x * y for x, y in zip(v, b))
                if dot:
                    v = [x - dot * y for x, y in zip(v, b)]
        norm = math.sqrt(math.fsum(x * x for x in v))
        if norm < 1e-12:
            basis.append([0.0] * n)
            continue
        basis.append([x / norm for x in v])
    out = [[0.0] * dim for _ in range(n)]
    for i in range(n):
        for t in range(dim):
            out[i][t] = basis[t][i]
    return out


def _cosine(a: Sequence[float], b: Sequence[float]) -> float:
    d = math.fsum(x * y for x, y in zip(a, b))
    na = math.sqrt(math.fsum(x * x for x in a))
    nb = math.sqrt(math.fsum(x * x for x in b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return d / (na * nb)


# ------------------------------------------------------------ 公开接口
class SemanticIndex:
    """确定性语义索引：fit 一次，之后 encode / similar / score 均可复现。"""

    def __init__(self) -> None:
        self.vocab: List[str] = []
        self.vectors: Dict[str, List[float]] = {}
        self.dim: int = DIM
        self.docs: List[str] = []
        self._doc_vecs: List[List[float]] = []

    # fit(corpus) -> {"vocab", "vectors"}（规格要求的返回形态）
    def fit(self, corpus: Sequence[str]) -> dict:
        self.docs = list(corpus)
        tokenized = [tokenize(d) for d in self.docs]
        df: Dict[str, int] = {}
        for toks in tokenized:
            for t in set(toks):
                df[t] = df.get(t, 0) + 1
        cand = [(t, c) for t, c in df.items() if c >= MIN_DF]
        cand.sort(key=lambda p: (-p[1], p[0]))
        self.vocab = [t for t, _ in cand[:MAX_VOCAB]]
        index = {t: i for i, t in enumerate(self.vocab)}
        n = len(self.vocab)

        cooc: Dict[Tuple[int, int], float] = {}
        for toks in tokenized:
            ids = [index[t] for t in toks if t in index]
            for pos in range(len(ids)):
                for off in range(1, WINDOW + 1):
                    if pos + off >= len(ids):
                        break
                    a, b = ids[pos], ids[pos + off]
                    if a == b:
                        continue
                    key = (a, b) if a < b else (b, a)
                    cooc[key] = cooc.get(key, 0.0) + 1.0

        counts = [0.0] * n
        for (i, j), w in cooc.items():
            counts[i] += w
            counts[j] += w
        total = math.fsum(cooc.values()) or 1.0
        pmi: Dict[Tuple[int, int], float] = {}
        for (i, j), w in cooc.items():
            # 注意：这里必须保留 w==1 的稀有对。早期版本 `if w < 2: continue`
            # 把只共现一次的搭配整段丢掉，结果只剩 data/report 这类通用词撑起向量，
            # 实测表现为多个不相关文档余弦同为 0.7200（区分度塌陷）。
            if w <= 0:
                continue
            pij = w / total
            pi = counts[i] / total
            pj = counts[j] / total
            val = math.log(pij / (pi * pj)) if pij > 0 and pi > 0 and pj > 0 else 0.0
            if val > 0:
                pmi[(i, j)] = val
        coords = _vectors(pmi, n, self.dim)
        self.vectors = {t: coords[i] for i, t in enumerate(self.vocab)}
        self._doc_vecs = [self._raw_encode(d) for d in self.docs]
        return {"vocab": self.vocab, "vectors": self.vectors}

    def _raw_encode(self, text: str) -> List[float]:
        vec = [0.0] * self.dim
        for t in tokenize(text):
            v = self.vectors.get(t)
            if not v:
                continue
            for k in range(self.dim):
                vec[k] += v[k]
        norm = math.sqrt(math.fsum(x * x for x in vec))
        if norm >= 1e-12:
            vec = [x / norm for x in vec]
        return vec

    def encode(self, text: str) -> List[float]:
        return self._raw_encode(text)

    def similar(self, a: str, b: str) -> float:
        return round(_cosine(self.encode(a), self.encode(b)), 6)

    def score(self, query: str, doc_index: int) -> float:
        return round(_cosine(self.encode(query), self._doc_vecs[doc_index]), 6)

    def best(self, query: str, labels: Sequence[str]) -> Tuple[str, float]:
        vec = self.encode(query)
        ranked = [(_cosine(vec, dv), labels[i], i) for i, dv in enumerate(self._doc_vecs)]
        ranked.sort(key=lambda t: (-t[0], t[1]))
        top = ranked[0] if ranked else (0.0, "", -1)
        return top[1], round(top[0], 6)


def fit(corpus: Sequence[str]) -> dict:
    """模块级便捷入口：fit(corpus) -> {"vocab", "vectors"}。"""
    idx = SemanticIndex()
    idx.fit(corpus)
    return {"vocab": idx.vocab, "vectors": idx.vectors}


def encode(text: str, index: SemanticIndex) -> List[float]:
    return index.encode(text)


def similar(a: str, b: str, index: SemanticIndex) -> float:
    return index.similar(a, b)
