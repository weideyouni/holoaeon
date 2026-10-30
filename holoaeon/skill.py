# -*- coding: utf-8 -*-
"""
Skill —— HoloAeon 技能契约与注册（含自动匹配）
================================================================================
一个 Skill 是一个带【契约(manifest)】的可调用能力：声明输入/输出、所需权限、标签
与验证阈值。Agent 通过 SkillRegistry 发现并调用技能，而不直接依赖具体实现。

自动匹配 match(query)：根据任务描述（文本）按确定性的 token 重叠 + 标签命中评分，
返回最相关的技能候选——这是"自动匹配技能"的基础原语（纯词面，不依赖外部模型）。
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

SkillFn = Callable[..., Any]

_TOKEN_RE = re.compile(r"[a-z0-9]+|[\u4e00-\u9fff]")


def tokenize(text: str) -> List[str]:
    """小写 token 化：英文/数字按词，中文按单字（确定性，无第三方分词）。"""
    return _TOKEN_RE.findall(text.lower())


def _normalize(text: str) -> str:
    """匹配前的归一化：小写 + 去空白（确定性，无第三方处理）。"""
    return re.sub(r"\s+", "", text.lower())


def _ngrams(text: str, n: int) -> Counter:
    s = _normalize(text)
    if len(s) < n:
        return Counter([s]) if s else Counter()
    return Counter(s[i:i + n] for i in range(len(s) - n + 1))


def _dice(ca: Counter, cb: Counter) -> float:
    """多重集合 Dice = 2·|A∩B| / (|A|+|B|)；分母为 0 时返回 0.0。"""
    total = sum(ca.values()) + sum(cb.values())
    if total == 0:
        return 0.0
    inter = sum(min(v, cb[k]) for k, v in ca.items())
    return 2.0 * inter / total


def ngram_dice(query: str, text: str, n: int = 2) -> float:
    """字符 n-gram Dice 系数（默认 2-gram）。

    · 归一化：小写 + 去空白；
    · 长度 < n 时退化为"相等即 1.0，否则 0.0"；
    · 纯函数：不修改入参，同输入同输出（无随机源、无外部模型）。
    """
    qa, tb = _normalize(query), _normalize(text)
    if len(qa) < n or len(tb) < n:
        return 1.0 if qa == tb and qa else 0.0
    return round(_dice(_ngrams(query, n), _ngrams(text, n)), 5)


def _word_ngram_dice(query: str, text: str, n: int = 3) -> float:
    """英文词级 n-gram Dice 兜底：仅当任一侧含空白（可分词）时参与取大。"""
    qw, tw = query.lower().split(), text.lower().split()
    if len(qw) < n or len(tw) < n:
        return 0.0
    return round(_dice(Counter(tuple(qw[i:i + n]) for i in range(len(qw) - n + 1)),
                       Counter(tuple(tw[i:i + n]) for i in range(len(tw) - n + 1))), 5)


@dataclass
class SkillManifest:
    name: str
    description: str = ""
    inputs: Dict[str, str] = field(default_factory=dict)
    outputs: Dict[str, str] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    permissions: int = 0                  # 0 只读 ... 4 高危（与守卫一致）
    verify_threshold: float = 1.0
    deterministic: bool = True

    def tokens(self) -> List[str]:
        words = tokenize(self.name + " " + self.description)
        for t in self.tags:
            words.extend(tokenize(t))
        return words


class Skill:
    """带契约的技能：可直接 run，也可由 Agent 经 registry 调用。"""

    def __init__(self, manifest: SkillManifest, fn: Optional[SkillFn] = None):
        self.manifest = manifest
        self._fn = fn

    def run(self, *args: Any, **kwargs: Any) -> Any:
        if self._fn is None:
            raise RuntimeError(f"技能 '{self.manifest.name}' 未绑定实现")
        return self._fn(*args, **kwargs)

    @property
    def name(self) -> str:
        return self.manifest.name

    def describe(self) -> dict:
        m = self.manifest
        return {
            "name": m.name,
            "description": m.description,
            "inputs": m.inputs,
            "outputs": m.outputs,
            "tags": m.tags,
            "permissions": m.permissions,
        }


class SkillRegistry:
    """技能注册表：注册/查找/列举/自动匹配。"""

    def __init__(self) -> None:
        self._skills: Dict[str, Skill] = {}

    def register(self, skill: Skill) -> Skill:
        if skill.name in self._skills:
            raise ValueError(f"技能已存在：{skill.name}")
        self._skills[skill.name] = skill
        return skill

    def register_fn(
        self,
        name: str,
        fn: SkillFn,
        description: str = "",
        tags: Optional[List[str]] = None,
        permissions: int = 0,
        **kwargs: Any,
    ) -> Skill:
        manifest = SkillManifest(
            name=name, description=description, tags=tags or [],
            permissions=permissions, **kwargs
        )
        return self.register(Skill(manifest, fn))

    def get(self, name: str) -> Skill:
        if name not in self._skills:
            raise KeyError(f"未注册技能：{name}")
        return self._skills[name]

    def has(self, name: str) -> bool:
        return name in self._skills

    def names(self) -> List[str]:
        return sorted(self._skills.keys())

    def all(self) -> List[Skill]:
        return [self._skills[k] for k in sorted(self._skills)]

    # ------------------------------------------------------------ 自动匹配
    def _skill_text(self, skill: Skill) -> str:
        m = skill.manifest
        return " ".join([m.name, m.description] + list(m.tags))

    def score(self, skill: Skill, query_tokens: List[str],
              query_text: str = "") -> float:
        """混合分 = 0.5·Jaccard(词面) + 0.5·Dice(字符 2-gram) + 0.05·标签命中。

        词面项保留既有量纲（Jaccard 而非重叠个数）；字符项补中文无分词与单词形变。
        两项都为 0 才返回 0——形变词（statistik / statistics）词面 0 但字符项非 0。
        """
        q = set(query_tokens)
        if not q:
            return 0.0
        st = set(skill.manifest.tokens())
        overlap = len(q & st)
        jaccard = overlap / len(q | st) if overlap else 0.0
        text = self._skill_text(skill)
        dice = ngram_dice(query_text, text, 2) if query_text else 0.0
        if query_text and (" " in query_text or " " in text):
            dice = max(dice, _word_ngram_dice(query_text, text, 3))
        if jaccard == 0.0 and dice == 0.0:
            return 0.0
        tag_hit = sum(1 for t in skill.manifest.tags if set(tokenize(t)) & q)
        return round(0.5 * jaccard + 0.5 * dice + 0.05 * tag_hit, 5)

    def match(self, query: str, k: int = 3) -> List[Tuple[str, float]]:
        """按任务描述返回 (skill_name, score) 降序，取前 k（score>0）。"""
        q = tokenize(query)
        scored = [(s.name, self.score(s, q, query)) for s in self.all()]
        scored = [(n, sc) for n, sc in scored if sc > 0]
        scored.sort(key=lambda t: (-t[1], t[0]))
        return scored[:k]

    def best(self, query: str) -> Optional[str]:
        m = self.match(query, k=1)
        return m[0][0] if m else None

    def verify(self) -> dict:
        dup = len(self.names()) != len(self._skills)
        return {"count": len(self._skills), "no_duplicates": not dup,
                "names": self.names()}
