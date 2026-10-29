# -*- coding: utf-8 -*-
"""
Kernel —— HoloAeon 内核（原"细胞骨架"）
================================================================================
Kernel 是顶层门面（facade）与结构支撑：持有并装配
  Bus（总线）、SkillRegistry（技能）、Memory（记忆）、
  Scheduler（时钟）、Guard（守卫）、可选的 AdaptiveGraph（协作图）与
  ModelAdapter（模型适配）；并维护 Agent 注册表与生命周期。

核心入口 submit(task, to=None)：
  构造信封 → Guard 检查 → 选择 agent（指定/自动/广播）→ 处理 → 记忆 → 汇总。
协作入口 collab(task, order)：按 agent 顺序流水线传递（前一输出作为后一输入）。
纯标准库。
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Sequence, Union

from .agent import Agent
from .bus import Bus
from .envelope import Envelope
from .guard import Guard
from .memory import Memory
from .scheduler import Scheduler
from .skill import SkillRegistry
from .spec import (
    DEFAULT_CONFIG,
    RUNTIME_ID,
    HoloAeonConfig,
)


class Kernel:
    """HoloAeon 内核：装配各组件，管理 agent 与任务。"""

    def __init__(self, config: Optional[HoloAeonConfig] = None):
        self.cfg = config or DEFAULT_CONFIG
        self.bus = Bus()
        self.skills = SkillRegistry()
        self.memory = Memory()
        self.scheduler = Scheduler(self.cfg.scheduler)
        self.guard = Guard(self.cfg.guard)
        self.agents: Dict[str, Agent] = {}
        self.graph: Any = None
        self.adapter: Any = None
        self._started = time.time()
        self.submitted = 0
        self.blocked = 0

    # ------------------------------------------------------------ 组件注入
    def attach_graph(self, graph: Any) -> None:
        self.graph = graph

    def attach_adapter(self, adapter: Any) -> None:
        self.adapter = adapter

    # ------------------------------------------------------------ Agent 注册
    def register_agent(self, agent: Agent, *, connect_bus: bool = True) -> Agent:
        if agent.agent_id in self.agents:
            raise ValueError(f"agent 已存在：{agent.agent_id}")
        # 共享内核的技能/记忆（若 agent 未自带）
        if agent.skills is not None and not agent.skills.names():
            agent.skills = self.skills
        if agent.memory is None:
            agent.memory = self.memory
        self.agents[agent.agent_id] = agent
        self.scheduler.watch_add(agent)
        if connect_bus:
            self.bus.register_address(agent.agent_id, agent.handle)
        return agent

    def get_agent(self, agent_id: str) -> Agent:
        return self.agents[agent_id]

    def choose_agent(self, task: str) -> Optional[str]:
        """自动选择 agent：按各 agent 对任务的技能匹配分数取最高。"""
        best, best_score = None, 0.0
        for aid, agent in self.agents.items():
            cand = agent.suggest(task, k=1)
            if cand and cand[0][1] > best_score:
                best, best_score = aid, cand[0][1]
        return best

    # ------------------------------------------------------------ 任务提交
    def submit(
        self,
        task: str,
        to: Optional[Union[str, Sequence[str]]] = None,
        *,
        args: Optional[dict] = None,
        metadata: Optional[dict] = None,
        permission: int = 0,
    ) -> dict:
        """提交任务：to 为 agent_id / agent_id 列表 / None（自动选择）。
        args 为额外技能参数（如 text/csv_text），与 task 一并进入 payload。"""
        self.submitted += 1
        targets = self._resolve_targets(task, to)
        results: List[dict] = []
        for aid in targets:
            env = Envelope.create(
                "main", aid, "task", {"task": task, **(args or {})},
                metadata={**(metadata or {}), "permission": permission},
            )
            verdict = self.guard.inspect(env)
            if verdict.action == "block":
                self.blocked += 1
                results.append({"agent_id": aid, "status": "blocked",
                                "verdict": verdict.to_dict()})
                continue
            res = self.agents[aid].handle(env)
            results.append(res)
        self.memory.put(f"task:{self.submitted}",
                        {"task": task, "results": results},
                        kind="longterm", tags=["task"])
        return {
            "runtime_id": RUNTIME_ID,
            "task": task, "targets": targets,
            "results": results,
            "all_ok": all(r.get("status") == "ok" for r in results) and bool(results),
        }

    def _resolve_targets(self, task: str,
                         to: Optional[Union[str, Sequence[str]]]) -> List[str]:
        if to is None:
            chosen = self.choose_agent(task)
            return [chosen] if chosen else list(self.agents.keys())
        if isinstance(to, str):
            return [to]
        return list(to)

    # ------------------------------------------------------------ 协作流水线
    def collab(self, task: str, order: Sequence[str]) -> dict:
        """按 agent 顺序流水线：前一输出作为后一输入。"""
        current = task
        steps = []
        for aid in order:
            agent = self.agents[aid]
            res = agent.run_task(current)
            steps.append({"agent_id": aid, "status": res.get("status"),
                          "matched": res.get("matched")})
            if res.get("status") == "ok":
                current = str(res.get("output"))
            else:
                break
        return {"task": task, "order": list(order), "steps": steps,
                "final": current,
                "completed": len(steps) == len(order)}

    # ------------------------------------------------------------ 节拍
    def tick(self) -> dict:
        return self.scheduler.tick()

    # ------------------------------------------------------------ 视图
    def snapshot(self) -> dict:
        return {
            "runtime_id": RUNTIME_ID,
            "uptime_s": round(time.time() - self._started, 3),
            "agents": list(self.agents.keys()),
            "skills": self.skills.names(),
            "submitted": self.submitted,
            "blocked": self.blocked,
            "memory": self.memory.stats(),
            "scheduler": self.scheduler.health(),
            "guard": self.guard.stats(),
            "has_graph": self.graph is not None,
            "has_adapter": self.adapter is not None,
        }

    def health(self) -> dict:
        return self.snapshot()
