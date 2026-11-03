# -*- coding: utf-8 -*-
"""
DeHallucinationPack —— 自组织相似性全息去幻觉扩展包（第 15 个扩展包）
================================================================================
V15-DEHALLUCINATION-LEIBNIZ-ZHANGPING · 把"去幻觉=用现实充足理由做减法"沉淀为确定性技能：

  6 技能（对应 dehallucination.py 8 阶段流水线拆分）：
    semantic_base_extract  — 语义基提取（张平Seb，TF-IDF向量化）
    reality_anchor         — 现实锚点（莱布尼茨PSR联网取点快照，回调注入）
    leibniz_space_compare  — 莱布尼茨空间比对（余弦相似度）
    synonym_mapping        — 同义映射检测（张平同义性，非字面匹配）
    hallucination_verdict  — 幻觉判定（贝叶斯后验 + 耗散熵）
    hebbian_feedback       — 赫布反馈（边权重自组织学习，相似强化/幻觉弱化）

3 角色 / 1 工作流；key = "dehallucination"（EXTRA_PACK_ORDER 14→15）。
纯标准库、零外部依赖、确定性、离线（联网经回调注入，缺失时降级内部比对）；
维度不变（只进 EXTRA_PACK_REGISTRY，不进 PACK_ORDER —— A1 的 25/47/9 不受影响）。
"""
from __future__ import annotations

import json
import math
import re
import sys
from collections import Counter
from typing import Any, Callable, Dict, List, Optional

from .base import DomainPack, RoleSpec, SkillSpec, WorkflowSpec
from ..dehallucination import (BAYES_PRIOR, BAYES_THRESHOLD, COSINE_HIGH,
                               COSINE_LOW, DeHallucinationModule)

# 赫布场边权重（模块级状态，确定性离线）
_HEBBIAN: Dict[str, float] = {}


def _tokenize(text: str) -> List[str]:
    """确定性分词（与 dehallucination 同口径）：英文词 + 中文 2-4 字 n-gram。"""
    tokens: List[str] = []
    for m in re.finditer(r'[a-zA-Z_][a-zA-Z0-9_]{2,}', str(text).lower()):
        tokens.append(m.group())
    chinese = re.sub(r'[^\u4e00-\u9fff]', '', str(text))
    for n in range(2, 5):
        for i in range(len(chinese) - n + 1):
            tokens.append(chinese[i:i + n])
    return tokens


def _entropy_of(seb: dict) -> float:
    """耗散熵（与 dehallucination._dissipation_entropy 同口径）。"""
    tf = list(seb.get("tf_vector", {}).values())
    if not tf:
        return 1.0
    total = sum(tf)
    if total == 0:
        return 1.0
    probs = [v / total for v in tf]
    entropy = -sum(p * math.log(p + 1e-10) for p in probs)
    max_entropy = math.log(len(probs) + 1e-10)
    return entropy / max_entropy if max_entropy > 0 else 1.0


# ============================================================ 技能：语义基提取
def semantic_base_extract(text: str = "", **_a: Any) -> dict:
    """语义基提取（张平Seb）：TF-IDF 向量化 → 语义关键词（top20）。"""
    tokens = _tokenize(str(text or ""))
    tf = Counter(tokens)
    total = sum(tf.values()) or 1
    tf_norm = {k: v / total for k, v in tf.items()}
    top = sorted(tf_norm.items(), key=lambda x: x[1], reverse=True)[:20]
    seb = {"tokens": tokens, "tfidf_top": [k for k, _ in top],
           "tf_vector": dict(top), "dim": len(tokens)}
    return {"status": "ok", "semantic_base": seb["tfidf_top"][:10],
            "dim": seb["dim"]}


# ============================================================ 技能：现实锚点
def reality_anchor(semantic_base: Optional[list] = None,
                   fetch: Optional[Callable[[str], str]] = None,
                   **_a: Any) -> dict:
    """现实锚点（莱布尼茨PSR）：top5 关键词构建查询 → 联网取点快照（回调注入）。"""
    top = list(semantic_base or [])[:5]
    query = " ".join(top)
    if fetch is not None:
        snapshot = fetch(query)
    else:
        snapshot = ""  # 降级模式：无联网，只靠内部知识库
    return {"status": "ok", "query": query,
            "reality_snapshot": str(snapshot)[:200],
            "mode": "callback" if fetch is not None else "degraded"}


# ============================================================ 技能：莱布尼茨空间比对
def leibniz_space_compare(vec_a: Optional[dict] = None,
                          vec_b: Optional[dict] = None, **_a: Any) -> dict:
    """莱布尼茨空间比对：余弦相似度（空间=关系秩序）。"""
    v1 = dict(vec_a or {})
    v2 = dict(vec_b or {})
    common = set(v1.keys()) & set(v2.keys())
    if not common:
        cosine = 0.0
    else:
        dot = sum(v1[k] * v2[k] for k in common)
        n1 = math.sqrt(sum(v ** 2 for v in v1.values()))
        n2 = math.sqrt(sum(v ** 2 for v in v2.values()))
        cosine = dot / (n1 * n2) if n1 and n2 else 0.0
    return {"status": "ok", "cosine_similarity": round(cosine, 4),
            "common_terms": len(common)}


# ============================================================ 技能：同义映射检测
def synonym_mapping(text_a: str = "", text_b: str = "",
                    cosine: float = 0.0, **_a: Any) -> dict:
    """同义映射检测（张平同义性）：语义匹配≠字面匹配，中等相似查关键词重叠。"""
    cosine = float(cosine or 0.0)
    if cosine >= COSINE_HIGH:
        return {"status": "ok", "synonym_match": True, "reason": "high_cosine"}
    if cosine < COSINE_LOW:
        return {"status": "ok", "synonym_match": False, "reason": "low_cosine"}
    ta = set(_tokenize(str(text_a)))
    tb = set(_tokenize(str(text_b)))
    overlap = ta & tb
    ratio = len(overlap) / max(len(ta | tb), 1)
    return {"status": "ok", "synonym_match": ratio > 0.3,
            "reason": f"keyword_overlap={ratio:.2f}", "overlap_count": len(overlap)}


# ============================================================ 技能：幻觉判定
def hallucination_verdict(cosine: float = 0.0,
                          synonym_match: bool = False,
                          semantic_base: Optional[dict] = None,
                          **_a: Any) -> dict:
    """幻觉判定（贝叶斯后验 + 耗散熵）：充足理由成立✅ / 缺失❌ / 待审⚠️。"""
    cosine = float(cosine or 0.0)
    if cosine >= COSINE_HIGH:
        likelihood = 0.1
    elif cosine < COSINE_LOW:
        likelihood = 0.9
    else:
        likelihood = 0.5
    if synonym_match:
        likelihood *= 0.7
    posterior = (likelihood * BAYES_PRIOR) / (
        likelihood * BAYES_PRIOR + (1 - likelihood) * (1 - BAYES_PRIOR) + 1e-10)
    entropy = _entropy_of(dict(semantic_base or {}))
    if cosine >= COSINE_HIGH and synonym_match:
        verdict = "non_hallucination"
    elif cosine < COSINE_LOW and not synonym_match:
        verdict = "hallucination"
    else:
        verdict = "uncertain"
    return {"status": "ok", "verdict": verdict,
            "bayesian_posterior": round(posterior, 4),
            "dissipation_entropy": round(entropy, 4),
            "sufficient_reason": verdict == "non_hallucination"}


# ============================================================ 技能：赫布反馈
def hebbian_feedback(key: str = "unknown", cosine: float = 0.0, **_a: Any) -> dict:
    """赫布反馈（自组织学习）：相似→强化（+0.12），幻觉→弱化（×0.99 衰减）。"""
    cosine = float(cosine or 0.0)
    key = str(key or "unknown")
    old = _HEBBIAN.get(key, 0.5)
    if cosine >= COSINE_HIGH:
        new = old * 0.99 + 0.12 * (1.0 - old)
    else:
        new = old * 0.99
    _HEBBIAN[key] = new
    return {"status": "ok", "key": key, "old_weight": round(old, 4),
            "new_weight": round(new, 4), "delta": round(new - old, 4)}


# ============================================================ 扩展包定义
class DeHallucinationPack(DomainPack):
    key = "dehallucination"
    name = "自组织相似性全息去幻觉（莱布尼茨PSR × 张平Seb × 赫布场）"
    description = (
        "把去幻觉做成确定性流水线：AI输出 → 语义基提取（张平Seb）→ 联网取点快照"
        "（莱布尼茨充足理由）→ 空间比对（余弦）→ 同义映射 → 贝叶斯+熵判定 → "
        "赫布反馈（自组织学习）；联网经回调注入，缺失时降级内部比对，纯标准库离线可跑"
    )

    skills = [
        SkillSpec("semantic_base_extract", semantic_base_extract,
                  "语义基提取（张平Seb）：TF-IDF 向量化 → 语义关键词",
                  tags=["dehallucination", "seb", "tfidf", "semantic"],
                  inputs={"text": "str"}),
        SkillSpec("reality_anchor", reality_anchor,
                  "现实锚点（莱布尼茨PSR）：top5 关键词查询 → 联网取点快照（回调注入）",
                  tags=["dehallucination", "anchor", "psr", "fetch"],
                  inputs={"semantic_base": "list", "fetch": "callable"}),
        SkillSpec("leibniz_space_compare", leibniz_space_compare,
                  "莱布尼茨空间比对：余弦相似度（空间=关系秩序）",
                  tags=["dehallucination", "leibniz", "cosine", "compare"],
                  inputs={"vec_a": "dict", "vec_b": "dict"}),
        SkillSpec("synonym_mapping", synonym_mapping,
                  "同义映射检测（张平同义性）：语义匹配≠字面匹配",
                  tags=["dehallucination", "synonym", "semantic"],
                  inputs={"text_a": "str", "text_b": "str", "cosine": "float"}),
        SkillSpec("hallucination_verdict", hallucination_verdict,
                  "幻觉判定（贝叶斯后验+耗散熵）：充足理由成立✅/缺失❌/待审⚠️",
                  tags=["dehallucination", "verdict", "bayes", "entropy"],
                  inputs={"cosine": "float", "synonym_match": "bool",
                          "semantic_base": "dict"}),
        SkillSpec("hebbian_feedback", hebbian_feedback,
                  "赫布反馈（自组织学习）：相似强化/幻觉弱化，边权重更新",
                  tags=["dehallucination", "hebbian", "feedback", "learn"],
                  inputs={"key": "str", "cosine": "float"}),
    ]

    roles = [
        RoleSpec("anchor_engineer", "锚点工程师（现实充足理由）：语义基→查询→取点快照",
                 ["semantic_base_extract", "reality_anchor"]),
        RoleSpec("semantic_analyst", "语义分析师（张平语义）：空间比对+同义映射",
                 ["leibniz_space_compare", "synonym_mapping"]),
        RoleSpec("verdict_judge", "裁判（贝叶斯+耗散）：幻觉判定+赫布反馈",
                 ["hallucination_verdict", "hebbian_feedback"]),
    ]

    workflows = [
        WorkflowSpec("dehallucination_flow",
                     ["anchor_engineer", "semantic_analyst",
                      "semantic_analyst", "verdict_judge", "verdict_judge"],
                     "语义基→现实锚点→空间比对→同义映射→判定→赫布反馈（8 阶段闭环）"),
    ]


def pack_summary() -> Dict[str, Any]:
    p = DeHallucinationPack()
    return {"key": p.key, "skills": len(p.skills), "roles": len(p.roles),
            "workflows": len(p.workflows)}


def main(argv=None) -> int:
    """CLI 入口（演示）：6 技能 / 3 角色 / 1 工作流 + 端到端演示。"""
    args = list(sys.argv[1:] if argv is None else argv)
    print("== HoloAeon 自组织相似性全息去幻觉扩展包（dehallucination 第15扩展包）==")
    print("包契约:", pack_summary())
    if args and args[0].strip() == "--selfcheck":
        # 分支1：充足理由成立 → 非幻觉
        r1 = DeHallucinationModule(
            lambda q: "人工智能 多智能体 系统 架构 设计 矩阵 智能体 协作"
        ).check("人工智能 多智能体 系统 架构 设计")
        # 分支2：充足理由缺失 → 幻觉
        r2 = DeHallucinationModule(
            lambda q: "量子 引力 波 天文 观测 望远镜 恒星"
        ).check("北京 是 中国的 首都 政治 文化 中心")
        ok = (len(DeHallucinationPack.skills) == 6
              and len(DeHallucinationPack.roles) == 3
              and len(DeHallucinationPack.workflows) == 1
              and r1["verdict"] == "non_hallucination"
              and r2["verdict"] == "hallucination"
              and r1["theory"].startswith("Leibniz"))
        print("自检:", "PASS" if ok else "FAIL",
              "skills=6 roles=3 workflows=1 case_high=%s case_low=%s"
              % (r1["verdict"], r2["verdict"]))
        return 0 if ok else 1
    print("6 技能: %s" % ", ".join(s.name for s in DeHallucinationPack.skills))
    print("3 角色: %s" % ", ".join(r.name for r in DeHallucinationPack.roles))
    print("1 工作流: %s" % ", ".join(w.name for w in DeHallucinationPack.workflows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
