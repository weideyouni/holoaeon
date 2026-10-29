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
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

SkillFn = Callable[..., Any]

_TOKEN_RE = re.compile(r"[a-z0-9]+|[\u4e00-\u9fff]")


def tokenize(text: str) -> List[str]:
    """小写 token 化：英文/数字按词，中文按单字（确定性，无第三方分词）。"""
    return _TOKEN_RE.findall(text.lower())


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
    def score(self, skill: Skill, query_tokens: List[str]) -> float:
        q = set(query_tokens)
        if not q:
            return 0.0
        st = set(skill.manifest.tokens())
        overlap = len(q & st)
        if overlap == 0:
            return 0.0
        # Jaccard 词面相关 + 标签命中加权
        jaccard = overlap / len(q | st)
        tag_hit = sum(1 for t in skill.manifest.tags
                      if set(tokenize(t)) & q)
        return round(jaccard + 0.05 * tag_hit, 5)

    def match(self, query: str, k: int = 3) -> List[Tuple[str, float]]:
        """按任务描述返回 (skill_name, score) 降序，取前 k（score>0）。"""
        q = tokenize(query)
        scored = [(s.name, self.score(s, q)) for s in self.all()]
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
