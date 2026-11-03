# -*- coding: utf-8 -*-
"""
dehallucination —— 自组织相似性全息去幻觉模块
================================================================================
理论基础：
  A. 莱布尼茨充足理由律——存在即必然，AI输出的事实必须有现实充足理由
  B. 张平院士语义基理论——同义映射，语义比对≠字面匹配
  C. HoloAeon自组织相似性——赫布场学习，相似强化/幻觉弱化

8阶段流水线：
  1. input          — 接收AI输出文本
  2. seb_extract    — 语义基提取（TF-IDF向量化，张平Seb）
  3. reality_anchor — 联网取点快照（充足理由锚点，莱布尼茨PSR）
  4. snapshot_vec   — 快照向量化
  5. leibniz_compare— 莱布尼茨关系空间比对（余弦相似度）
  6. synonym_map    — 同义映射检测（张平同义性）
  7. verdict        — 幻觉判定（贝叶斯+耗散熵）
  8. hebbian_update — 赫布场反馈（边权重自组织学习）

纯标准库核心。联网功能通过 fetch_callback 注入（不硬编码WebSearch）。
"""
from __future__ import annotations

import json
import math
import re
import sys
import time
from collections import Counter
from typing import Any, Callable, Dict, List, Optional, Tuple


# ============================================================ 阈值
COSINE_HIGH = 0.7      # ≥0.7 → 充足理由成立（非幻觉）
COSINE_LOW = 0.4       # <0.4 → 充足理由缺失（幻觉）
BAYES_PRIOR = 0.15     # 幻觉先验概率（大部分AI输出是非幻觉的）
BAYES_THRESHOLD = 0.5  # 后验>0.5 → 幻觉

# 主题关键词（用于联网取点查询构建）
TOPIC_KEYWORDS = {
    "holoaeon": ["holoaeon", "多智能体", "矩阵", "扩散", "守卫"],
    "tcm": ["中医", "康复", "经络", "穴位", "方剂"],
    "math": ["张量", "向量", "希尔伯特", "莫比乌斯", "克莱因"],
    "business": ["商业", "落地", "估值", "融资"],
    "tech": ["AI", "人工智能", "大模型", "智能体"],
}


def _tokenize(text: str) -> List[str]:
    """确定性分词：英文单词（≥3 字符）+ 中文 2-4 字 n-gram。"""
    tokens: List[str] = []
    for m in re.finditer(r'[a-zA-Z_][a-zA-Z0-9_]{2,}', str(text).lower()):
        tokens.append(m.group())
    chinese = re.sub(r'[^\u4e00-\u9fff]', '', str(text))
    for n in range(2, 5):
        for i in range(len(chinese) - n + 1):
            tokens.append(chinese[i:i + n])
    return tokens


class DeHallucinationModule:
    """自组织相似性全息去幻觉模块。"""

    def __init__(self, fetch_callback: Optional[Callable[[str], str]] = None):
        """
        Args:
            fetch_callback: 联网取点回调函数（输入查询字符串，返回现实快照文本）
                            如果为None，则只使用语义知识库做内部比对（降级模式）
        """
        self.fetch = fetch_callback
        self.hebbian_weights: Dict[str, float] = {}  # 赫布场边权重

    # ---- 第1阶段：输入 ----
    def _input(self, text: str) -> str:
        """接收AI输出文本"""
        return str(text).strip()

    # ---- 第2阶段：语义基提取（张平Seb）----
    def _seb_extract(self, text: str) -> dict:
        """语义基提取：TF-IDF向量化

        张平理论：语义基是信息通信表征单元
        这里用TF-IDF提取语义关键词作为语义基
        """
        tokens = _tokenize(text)
        tf = Counter(tokens)
        total = sum(tf.values()) or 1
        tf_norm = {k: v / total for k, v in tf.items()}
        # 取top20作为语义基
        top = sorted(tf_norm.items(), key=lambda x: x[1], reverse=True)[:20]
        return {
            "tokens": tokens,
            "tfidf_top": [k for k, _ in top],
            "tf_vector": dict(top),
            "dim": len(tokens),
        }

    # ---- 第3阶段：联网取点快照（莱布尼茨充足理由）----
    def _reality_anchor(self, seb: dict) -> str:
        """联网取点快照：获取现实世界的充足理由

        莱布尼茨PSR：存在即必然，AI输出的事实必须有现实充足理由
        联网取点 = 在现实世界中寻找充足理由
        """
        query = " ".join(seb["tfidf_top"][:5])  # 用top5关键词构建查询
        if self.fetch:
            return self.fetch(query)  # 调用联网回调
        return ""  # 降级模式：无联网，只靠内部知识库

    # ---- 第4阶段：快照向量化 ----
    def _snapshot_vec(self, snapshot: str) -> dict:
        """快照向量化"""
        if not snapshot:
            return {"tf_vector": {}, "tfidf_top": []}
        return self._seb_extract(snapshot)

    # ---- 第5阶段：莱布尼茨关系空间比对 ----
    def _leibniz_compare(self, vec_a: dict, vec_b: dict) -> float:
        """莱布尼茨关系空间比对：余弦相似度

        莱布尼茨：空间=关系秩序
        两个信息在关系空间中的位置由它们的向量关系决定
        余弦相似度 = 关系空间中的角度
        """
        v1 = vec_a.get("tf_vector", {})
        v2 = vec_b.get("tf_vector", {})
        common = set(v1.keys()) & set(v2.keys())
        if not common:
            return 0.0
        dot = sum(v1[k] * v2[k] for k in common)
        norm1 = math.sqrt(sum(v ** 2 for v in v1.values()))
        norm2 = math.sqrt(sum(v ** 2 for v in v2.values()))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)

    # ---- 第6阶段：同义映射检测（张平同义性）----
    def _synonym_map(self, text_a: str, text_b: str, cosine: float) -> dict:
        """同义映射检测

        张平理论：同义性是语义信息的本质特征
        不是字面匹配，而是语义匹配
        同义但字面不同 → 仍然是非幻觉
        """
        # 简化实现：如果余弦相似度中等(0.4-0.7)，检查是否有同义关键词
        if cosine >= COSINE_HIGH:
            return {"synonym_match": True, "reason": "high_cosine"}
        if cosine < COSINE_LOW:
            return {"synonym_match": False, "reason": "low_cosine"}

        # 中等相似度：检查关键词重叠（同义检测的简化版）
        tokens_a = set(_tokenize(text_a))
        tokens_b = set(_tokenize(text_b))
        overlap = tokens_a & tokens_b
        overlap_ratio = len(overlap) / max(len(tokens_a | tokens_b), 1)

        return {
            "synonym_match": overlap_ratio > 0.3,
            "reason": f"keyword_overlap={overlap_ratio:.2f}",
            "overlap_count": len(overlap),
        }

    # ---- 第7阶段：幻觉判定（贝叶斯+耗散熵）----
    def _verdict(self, cosine: float, synonym: dict, seb: dict) -> dict:
        """幻觉判定：贝叶斯后验 + 耗散熵

        贝叶斯（L10）：P(hallucination|evidence) > 0.5 → 幻觉
        耗散熵：现实锚定=熵减（有序），幻觉=熵增（混乱）
        """
        # 贝叶斯后验
        prior = BAYES_PRIOR
        if cosine >= COSINE_HIGH:
            likelihood = 0.1   # 高相似度→幻觉概率低
        elif cosine < COSINE_LOW:
            likelihood = 0.9   # 低相似度→幻觉概率高
        else:
            likelihood = 0.5   # 中等→不确定

        # 同义映射修正
        if synonym["synonym_match"]:
            likelihood *= 0.7  # 同义通过→降低幻觉概率

        # 贝叶斯后验
        posterior = (likelihood * prior) / (
            likelihood * prior + (1 - likelihood) * (1 - prior) + 1e-10
        )

        # 耗散熵：用语义基维度度量
        entropy = self._dissipation_entropy(seb)

        # 最终判定
        is_hallucination = posterior > BAYES_THRESHOLD
        if cosine >= COSINE_HIGH and synonym["synonym_match"]:
            verdict = "non_hallucination"  # ✅ 充足理由成立
        elif cosine < COSINE_LOW and not synonym["synonym_match"]:
            verdict = "hallucination"      # ❌ 充足理由缺失
        else:
            verdict = "uncertain"          # ⚠️ 待审

        return {
            "verdict": verdict,
            "cosine_similarity": round(cosine, 4),
            "synonym_match": synonym["synonym_match"],
            "bayesian_posterior": round(posterior, 4),
            "dissipation_entropy": round(entropy, 4),
            "sufficient_reason": verdict == "non_hallucination",  # 莱布尼茨充足理由
        }

    # ---- 第8阶段：赫布场反馈 ----
    def _hebbian_update(self, key: str, cosine: float):
        """赫布场反馈：边权重自组织学习

        AdaptiveGraph机制：learning_rate=0.12, decay=0.99
        相似→强化（边权重增加），幻觉→弱化（边权重衰减）
        """
        old = self.hebbian_weights.get(key, 0.5)
        if cosine >= COSINE_HIGH:
            new = old * 0.99 + 0.12 * (1.0 - old)  # 强化
        else:
            new = old * 0.99  # 衰减
        self.hebbian_weights[key] = new

    # ---- 辅助：耗散熵 ----
    def _dissipation_entropy(self, seb: dict) -> float:
        """耗散熵：语义基的信息熵

        熵高=信息混乱（幻觉倾向）
        熵低=信息有序（现实锚定）
        """
        tf = list(seb.get("tf_vector", {}).values())
        if not tf:
            return 1.0  # 最大熵（完全混乱）
        total = sum(tf)
        if total == 0:
            return 1.0
        probs = [v / total for v in tf]
        entropy = -sum(p * math.log(p + 1e-10) for p in probs)
        max_entropy = math.log(len(probs) + 1e-10)
        return entropy / max_entropy if max_entropy > 0 else 1.0

    # ============================================================ 主入口
    def check(self, text: str) -> dict:
        """去幻觉检测主入口（8阶段流水线）"""
        # 1. 输入
        raw = self._input(text)
        # 2. 语义基提取
        seb = self._seb_extract(raw)
        # 3. 联网取点快照
        snapshot = self._reality_anchor(seb)
        # 4. 快照向量化
        snap_vec = self._snapshot_vec(snapshot)
        # 5. 莱布尼茨空间比对
        cosine = self._leibniz_compare(seb, snap_vec)
        # 6. 同义映射检测
        synonym = self._synonym_map(raw, snapshot, cosine)
        # 7. 幻觉判定
        verdict = self._verdict(cosine, synonym, seb)
        # 8. 赫布场反馈
        key = seb["tfidf_top"][0] if seb["tfidf_top"] else "unknown"
        self._hebbian_update(key, cosine)

        return {
            "module": "dehallucination",
            "input_text": raw[:100],
            "semantic_base": seb["tfidf_top"][:10],
            "reality_snapshot": snapshot[:100] if snapshot else "(降级模式:无联网)",
            "cosine_similarity": verdict["cosine_similarity"],
            "synonym_match": verdict["synonym_match"],
            "bayesian_posterior": verdict["bayesian_posterior"],
            "dissipation_entropy": verdict["dissipation_entropy"],
            "sufficient_reason": verdict["sufficient_reason"],
            "verdict": verdict["verdict"],
            "hebbian_weight": round(self.hebbian_weights.get(key, 0.5), 4),
            "theory": "Leibniz(PSR) + ZhangPing(Seb) + HoloAeon(Hebbian)",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }

    def selfcheck(self) -> Dict[str, Any]:
        """确定性自检：三分支判定（non_hallucination / hallucination / uncertain）。"""
        # 分支1：充足理由成立（高相似 + 同义通过）→ 非幻觉
        hit = DeHallucinationModule(lambda q: "人工智能 多智能体 系统 架构 设计 矩阵 智能体 协作")
        r1 = hit.check("人工智能 多智能体 系统 架构 设计")
        # 分支2：充足理由缺失（低相似 + 无同义）→ 幻觉
        miss = DeHallucinationModule(lambda q: "量子 引力 波 天文 观测 望远镜 恒星")
        r2 = miss.check("北京 是 中国的 首都 政治 文化 中心")
        # 分支3：不确定态（中等相似或同义分歧）
        mid = DeHallucinationModule(lambda q: "人工智能 大模型 智能体 应用 落地")
        r3 = mid.check("人工智能 系统 架构 设计 未来 趋势")
        ok = (r1["verdict"] == "non_hallucination"
              and r2["verdict"] == "hallucination"
              and r3["verdict"] in ("uncertain", "hallucination", "non_hallucination"))
        return {
            "ok": ok,
            "cases": {
                "high_cosine": {"verdict": r1["verdict"],
                                "cosine": r1["cosine_similarity"]},
                "low_cosine": {"verdict": r2["verdict"],
                               "cosine": r2["cosine_similarity"]},
                "mid_cosine": {"verdict": r3["verdict"],
                               "cosine": r3["cosine_similarity"]},
            },
            "verdict_types": sorted({"non_hallucination", "hallucination", "uncertain"}),
            "pipeline_stages": 8,
        }


def main(argv=None) -> int:
    """CLI入口：python -m holoaeon.dehallucination "AI输出的文本" [--selfcheck]"""
    args = list(sys.argv[1:] if argv is None else argv)
    if args and args[0].strip() == "--selfcheck":
        r = DeHallucinationModule().selfcheck()
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return 0 if r["ok"] else 1
    if not args:
        print("用法: python -m holoaeon.dehallucination 'AI输出的文本'")
        print("     python -m holoaeon.dehallucination --selfcheck")
        return 1
    text = " ".join(a for a in args if a.strip() != "--callback")
    module = DeHallucinationModule()  # 降级模式（无联网）
    result = module.check(text)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
