# -*- coding: utf-8 -*-
"""领域包：文字创作（writing）。确定性工具技能 + 角色 + 工作流。"""
from __future__ import annotations

import re
from typing import List

from .base import DomainPack, RoleSpec, SkillSpec, WorkflowSpec
from ..skill import tokenize

_SENT_SPLIT = re.compile(r"[.!?。！？]+")


def word_count(text: str) -> dict:
    """统计中文字数、英文词数、总字符、句数。"""
    cn = len(re.findall(r"[\u4e00-\u9fff]", text))
    en_words = len(re.findall(r"[a-zA-Z]+", text))
    sents = [s for s in _SENT_SPLIT.split(text) if s.strip()]
    return {"chinese_chars": cn, "english_words": en_words,
            "total_chars": len(text), "sentences": max(1, len(sents))}


def readability(text: str) -> dict:
    """可读性指标：平均句长（词/字）、平均词长。"""
    wc = word_count(text)
    sents = wc["sentences"]
    words = wc["chinese_chars"] + wc["english_words"]
    en_tokens = re.findall(r"[a-zA-Z]+", text)
    avg_word = round(sum(len(w) for w in en_tokens) / len(en_tokens), 2) if en_tokens else 0
    return {"avg_sentence_length": round(words / sents, 2),
            "avg_english_word_length": avg_word}


def outline_gen(topic: str) -> dict:
    """生成结构化大纲模板（确定性骨架；接 LLM 后可填充）。"""
    return {"topic": topic, "outline": [
        "一、引言：背景与问题",
        "二、现状/冲突",
        "三、核心观点（分 3 点）",
        "四、案例/证据",
        "五、结论与行动",
    ]}


def title_brainstorm(topic: str) -> dict:
    """基于主题生成标题候选模板。"""
    t = topic.strip()
    return {"topic": t, "titles": [
        f"{t}：从入门到精通",
        f"关于{t}，你需要知道的 5 件事",
        f"重新理解{t}",
        f"{t}的底层逻辑",
        f"我用{t}解决了一个真问题",
    ]}


def structure_check(text: str) -> dict:
    """结构检查：是否有开头/分段/结尾。"""
    paras = [p for p in text.split("\n") if p.strip()]
    return {"paragraphs": len(paras),
            "has_opening": len(paras) > 0,
            "has_body": len(paras) > 1,
            "has_closing": len(paras) > 2}


class WritingPack(DomainPack):
    key = "writing"
    name = "文字创作"
    description = "小说/文案/剧本/新媒体：从选题、大纲、初稿到打磨。"
    skills = [
        SkillSpec("word_count", word_count, "字数/词数/句数统计",
                  ["count", "stats"], {"text": "str"}),
        SkillSpec("readability", readability, "可读性指标",
                  ["edit", "quality"], {"text": "str"}),
        SkillSpec("outline_gen", outline_gen, "生成结构大纲",
                  ["plan", "outline"], {"topic": "str"}),
        SkillSpec("title_brainstorm", title_brainstorm, "标题候选",
                  ["title", "ideation"], {"topic": "str"}),
        SkillSpec("structure_check", structure_check, "结构检查",
                  ["edit", "structure"], {"text": "str"}),
    ]
    roles = [
        RoleSpec("writing_planner", "选题与大纲",
                 ["outline_gen", "title_brainstorm"]),
        RoleSpec("writing_drafter", "撰写初稿",
                 ["outline_gen"]),
        RoleSpec("writing_editor", "润色与质量检查",
                 ["word_count", "readability", "structure_check"]),
    ]
    workflows = [
        WorkflowSpec("creation_pipeline",
                     ["writing_planner", "writing_drafter", "writing_editor"],
                     "策划→撰稿→编辑"),
    ]
