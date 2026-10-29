# -*- coding: utf-8 -*-
"""
DomainPack —— HoloAeon 领域包基类
================================================================================
领域知识以"领域包"注入，引擎保持通用。一个 DomainPack 声明：
  · skills     SkillSpec：确定性工具技能（零依赖可直接运行）
  · roles      RoleSpec：角色及其技能（供 LLM 驱动 / 自动建 agent）
  · workflows  WorkflowSpec：角色协作流程（声明式）

install(kernel)：把技能注册进 kernel，按角色创建 agent，并可选地构建协作图。
真正的"生成式智能"由你通过 model_adapter 接入模型；内置技能是确定性的工具/模板，
保证离线可跑、可测试、可复现。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from ..agent import Agent
from ..skill import SkillManifest


@dataclass
class SkillSpec:
    name: str
    fn: Callable[..., Any]
    description: str = ""
    tags: List[str] = field(default_factory=list)
    inputs: Dict[str, str] = field(default_factory=dict)
    permissions: int = 0


@dataclass
class RoleSpec:
    name: str
    description: str = ""
    skills: List[str] = field(default_factory=list)


@dataclass
class WorkflowSpec:
    name: str
    steps: List[str] = field(default_factory=list)      # 角色顺序
    description: str = ""


class DomainPack:
    """领域包基类：子类覆盖 key/name/skills/roles/workflows。"""
    key: str = "generic"
    name: str = "通用领域包"
    description: str = ""
    skills: List[SkillSpec] = []
    roles: List[RoleSpec] = []
    workflows: List[WorkflowSpec] = []

    # ------------------------------------------------------------ 安装
    def install(self, kernel: Any, *, create_agents: bool = True,
                prefix: str = "") -> Dict[str, Any]:
        # 1) 注册技能
        registered = []
        for spec in self.skills:
            sname = f"{prefix}{spec.name}"
            if not kernel.skills.has(sname):
                kernel.skills.register_fn(
                    sname, spec.fn,
                    description=spec.description,
                    tags=[self.key] + spec.tags,
                    permissions=spec.permissions,
                    inputs=spec.inputs,
                )
                registered.append(sname)
        # 2) 按角色创建 agent
        created: List[str] = []
        if create_agents:
            for role in self.roles:
                aid = f"{prefix}{role.name}"
                if aid not in kernel.agents:
                    skill_names = [f"{prefix}{s}" for s in role.skills]
                    agent = Agent(
                        aid, role=role.name,
                        skills=kernel.skills,
                        skill_names=skill_names,
                        memory=kernel.memory,
                        description=role.description,
                    )
                    kernel.register_agent(agent)
                    created.append(aid)
        return {"pack": self.key, "skills": registered,
                "agents": created,
                "workflows": [w.name for w in self.workflows]}

    def describe(self) -> dict:
        return {
            "key": self.key, "name": self.name,
            "description": self.description,
            "skills": [s.name for s in self.skills],
            "roles": [r.name for r in self.roles],
            "workflows": [w.name for w in self.workflows],
        }
