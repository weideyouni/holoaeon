# -*- coding: utf-8 -*-
"""
Agent —— HoloAeon 智能体原语
================================================================================
一个 Agent 拥有：身份(agent_id)、角色(role)、一组技能(skills)、可选记忆，以及一个
可注入的决策函数 decide。默认决策根据收到的任务描述【自动匹配技能】（见 skill.match），
再调用该技能产生结果；decide 可被替换以接入任意模型/策略（与 model_adapter 配合）。

Agent 可作为 Bus 的直接地址 handler（handle(env)），也可在 cluster 中通过 inbox 工作。
纯标准库。
"""
from __future__ import annotations

import inspect
import time
from typing import Any, Callable, Dict, List, Optional

from .envelope import Envelope
from .memory import Memory
from .skill import SkillRegistry

DecideFn = Callable[["Agent", Envelope], Optional[str]]

# 兜底开关（V5.2 保守版）：默认 True 保持既有行为；改为 False 时「无命中」不再强行
# 借用唯一技能，而是显式返回 None（fail-loud），由上层决定怎么处置。
ALLOW_SINGLE_SKILL_FALLBACK = True


def _default_decide(agent: "Agent", env: Envelope) -> Optional[str]:
    """默认决策：payload 显式指定 skill 优先；否则按任务描述自动匹配（限定自身技能）；
    都不命中且 agent 仅有一个可用技能时，按开关决定是否回退到该技能。"""
    explicit = env.payload.get("skill") or env.metadata.get("skill")
    if explicit and agent.skills.has(explicit):
        return explicit
    query = env.payload.get("task") or env.payload.get("query") or env.topic
    candidates = agent.suggest(str(query), k=1)
    if candidates:
        return candidates[0][0]
    avail = agent.available_skills()
    flag = getattr(agent, "_cfg_allow_single_fallback", ALLOW_SINGLE_SKILL_FALLBACK)
    if flag and len(avail) == 1:
        agent._last_fallback = True   # handle() 据此写 result["degraded"]
        return avail[0]
    return None


class Agent:
    """通用智能体：身份 + 角色 + 技能 + 记忆 + 可注入决策。"""

    def __init__(
        self,
        agent_id: str,
        role: str = "generalist",
        skills: Optional[SkillRegistry] = None,
        *,
        skill_names: Optional[List[str]] = None,
        decide: Optional[DecideFn] = None,
        memory: Optional[Memory] = None,
        description: str = "",
    ):
        self.agent_id = agent_id
        self.role = role
        self.skills = skills or SkillRegistry()
        self.skill_names = list(skill_names or [])
        self.decide = decide or _default_decide
        self.memory = memory
        self.description = description
        self._created = time.time()
        self.calls = 0
        self.failures = 0
        # 兜底痕迹：_default_decide 借用唯一技能时置位，handle() 落成 degraded 字段
        self._last_fallback = False
        # 由 kernel 按 cfg.allow_single_skill_fallback 注入（缺省沿用模块级常量）
        self._cfg_allow_single_fallback = ALLOW_SINGLE_SKILL_FALLBACK

    # ------------------------------------------------------------ 可用技能
    def available_skills(self) -> List[str]:
        if self.skill_names:
            return [n for n in self.skill_names if self.skills.has(n)]
        return self.skills.names()

    def suggest(self, query: str, k: int = 3) -> List[tuple]:
        """对给定任务，返回该 agent 视角下的技能匹配候选（限定自身技能）。"""
        q = query
        if self.skill_names:
            sub = SkillRegistry()
            for n in self.skill_names:
                if self.skills.has(n):
                    sub.register(self.skills.get(n))
            return sub.match(q, k=k)
        return self.skills.match(q, k=k)

    # ------------------------------------------------------------ 处理
    def handle(self, env: Envelope) -> Dict[str, Any]:
        """处理一个信封：自动匹配技能 → 调用 → 返回结果（不直接回信，由 kernel 编排）。"""
        self.calls += 1
        result: Dict[str, Any] = {
            "agent_id": self.agent_id, "role": self.role,
            "input": env.payload, "ts": time.time(),
        }
        try:
            skill_name = self.decide(self, env)
            if not skill_name:
                result.update(status="no_skill", matched=None, output=None)
                self.failures += 1
                return result
            skill = self.skills.get(skill_name)
            output = self._invoke_skill(skill, env.payload)
            result.update(status="ok", matched=skill_name, output=output,
                          degraded=bool(self._last_fallback))
            self._last_fallback = False
            if self.memory is not None:
                self.memory.put(f"{self.agent_id}:{self.calls}",
                                {"skill": skill_name, "output": output},
                                kind="working", tags=[skill_name])
            return result
        except Exception as exc:  # noqa: BLE001
            self.failures += 1
            result.update(status="error", matched=None, output=None, err=str(exc))
            return result

    @staticmethod
    def _coerce(value: Any, annotation: Any) -> Any:
        """按参数注解做轻量类型转换（int/float），失败则原样返回。"""
        if annotation in (int, float) and isinstance(value, str):
            try:
                return annotation(value)
            except (TypeError, ValueError):
                return value
        return value

    @staticmethod
    def _invoke_skill(skill: Any, payload: dict) -> Any:
        """按技能函数签名健壮地传参：
        1) payload 显式 args 优先；
        2) 按参数名从 payload 直接匹配（text/csv_text/returns_s…），做类型转换；
        3) task/query 参数或唯一位置参数以任务文本填充；
        4) 有默认值的参数可省略；无参函数直接调用。
        """
        explicit = dict(payload.get("args", {}))
        if explicit:
            return skill.run(**explicit)
        task = payload.get("task")
        if task is None:
            task = payload.get("query")
        # 检查【底层实现函数】的签名（Skill.run 只有 *args/**kwargs，无法反映参数）
        target = getattr(skill, "_fn", None)
        if target is None:
            return skill.run()
        try:
            sig = inspect.signature(target)
            params = [p for p in sig.parameters.values()
                      if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)]
        except (TypeError, ValueError):
            params = []
        if not params:
            return skill.run()

        kwargs: Dict[str, Any] = {}
        unfilled: List[Any] = []
        for p in params:
            if p.name in payload and p.name not in ("task", "query"):
                kwargs[p.name] = Agent._coerce(value=payload[p.name],
                                               annotation=p.annotation)
            elif p.name in ("task", "query") and task is not None:
                kwargs[p.name] = task
            elif p.default is not inspect.Parameter.empty:
                continue  # 有默认值，省略
            else:
                unfilled.append(p)
        # 唯一无默认值的位置参数：用 task 填充
        if len(unfilled) == 1 and task is not None:
            kwargs[unfilled[0].name] = Agent._coerce(value=task,
                                                     annotation=unfilled[0].annotation)
        return skill.run(**kwargs)

    def run_task(self, task: str, **kwargs: Any) -> Dict[str, Any]:
        """便捷入口：直接以任务文本构造信封并处理。"""
        env = Envelope.create("main", self.agent_id, self.role,
                              {"task": task, **kwargs})
        return self.handle(env)

    def reply_to(self, env: Envelope) -> Envelope:
        """处理并把结果包成回信信封。"""
        res = self.handle(env)
        return env.reply(self.agent_id, {"result": res})

    # ------------------------------------------------------------ 视图
    def snapshot(self) -> dict:
        return {
            "agent_id": self.agent_id, "role": self.role,
            "description": self.description,
            "skills": self.available_skills(),
            "calls": self.calls, "failures": self.failures,
            "uptime_s": round(time.time() - self._created, 3),
        }
