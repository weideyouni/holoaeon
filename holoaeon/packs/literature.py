# -*- coding: utf-8 -*-
"""领域包：文献梳理（literature）。检索/筛选/阅读/综述/引用图谱。"""
from __future__ import annotations

import re
from collections import Counter
from typing import List

from .base import DomainPack, RoleSpec, SkillSpec, WorkflowSpec
from ..skill import tokenize

_STOP = set("the a an of and or to in on for with is are was were be by this that "
            "it as at from we our their his her its 与 和 的 了 在 是 及".split())
_SENT = re.compile(r"[.!?。！？]+")


def keyword_extract(text: str, topk: int = 8) -> dict:
    """词频关键词（去停用词，单字中文不计）。"""
    toks = [t for t in tokenize(text) if t not in _STOP and len(t) > 1]
    common = Counter(toks).most_common(topk)
    return {"keywords": [{"word": w, "freq": c} for w, c in common]}


def extract_abstract(text: str, sentences: int = 2) -> dict:
    """取前 N 句作为摘要（抽取式，确定性）。"""
    parts = [s.strip() for s in _SENT.split(text) if s.strip()]
    return {"abstract": ". ".join(parts[:sentences]),
            "sentence_count": len(parts)}


def normalize_citation(text: str) -> dict:
    """把引用条目规范化为 author/year/title 的近似结构（确定性启发式）。"""
    year = re.findall(r"(19|20)\d{2}", text)
    year_full = (year[0] + re.search(r"((?:19|20)\d{2})", text).group()[2:]
                 ) if year and re.search(r"((?:19|20)\d{2})", text) else ""
    first = text.split(",")[0].strip()
    return {"raw": text, "author": first, "year": year_full,
            "title": text[:80]}


def dedup_papers(entries: str) -> dict:
    """按标题归一化去重（entries 为每行一条：标题<TAB>来源）。"""
    seen, unique = set(), []
    for line in entries.splitlines():
        if not line.strip():
            continue
        title = line.split("\t")[0].strip().lower()
        key = re.sub(r"\s+", " ", title)
        if key not in seen:
            seen.add(key)
            unique.append(line.strip())
    return {"input": len([l for l in entries.splitlines() if l.strip()]),
            "unique": len(unique), "entries": unique}


def screen_papers(entries: str, keywords: str) -> dict:
    """按关键词筛选（任一命中即保留）。"""
    kws = [k.lower().strip() for k in keywords.split(",") if k.strip()]
    kept = []
    for line in entries.splitlines():
        low = line.lower()
        if any(k in low for k in kws):
            kept.append(line.strip())
    return {"keywords": kws, "matched": len(kept), "entries": kept}


class LiteraturePack(DomainPack):
    key = "literature"
    name = "文献梳理"
    description = "文献检索、筛选、去重、摘要、关键词与引用图谱。"
    skills = [
        SkillSpec("keyword_extract", keyword_extract, "关键词提取",
                  ["keywords", "nlp"], {"text": "str"}),
        SkillSpec("extract_abstract", extract_abstract, "抽取式摘要",
                  ["summary", "abstract"], {"text": "str"}),
        SkillSpec("normalize_citation", normalize_citation, "引用规范化",
                  ["citation"], {"text": "str"}),
        SkillSpec("dedup_papers", dedup_papers, "文献去重",
                  ["dedup", "screen"], {"entries": "str"}),
        SkillSpec("screen_papers", screen_papers, "文献筛选",
                  ["screen", "filter"], {"entries": "str", "keywords": "str"}),
    ]
    roles = [
        RoleSpec("lit_searcher", "检索与筛选",
                 ["screen_papers", "dedup_papers"]),
        RoleSpec("lit_reader", "精读与摘要",
                 ["extract_abstract", "keyword_extract"]),
        RoleSpec("lit_reviewer", "综述与引用",
                 ["normalize_citation", "keyword_extract"]),
    ]
    workflows = [
        WorkflowSpec("review_pipeline",
                     ["lit_searcher", "lit_reader", "lit_reviewer"],
                     "检索→精读→综述"),
    ]
