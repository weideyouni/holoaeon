# -*- coding: utf-8 -*-
"""
Runnable —— 统一调用协议 + 横切钩子链（W12，旁挂，不挂内核）
================================================================================
LangChain 值得抄的第一件事：万物皆可 call。这里给 Skill / Agent / Guard / Sink
一个统一面 `call(request, config)`，并允许用 `|` 组管道；执行仍然走既有
`Agent._invoke_skill` / `Kernel.submit`，**不新建第二条执行路径**（V3-1）。

五段钩子：admit → route → before_skill → after_skill → egress。
钩子抛错必须能定位到具体钩子（HookError 带 stage + hook name），不许静默。

纯标准库。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .agent import Agent
from .envelope import Envelope
from .guard import Guard
from .skill import Skill

STAGES = ("admit", "route", "before_skill", "after_skill", "egress")


class HookError(RuntimeError):
    """钩子内抛出的错误：保留 stage 与 hook 名，便于定位到具体钩子。"""

    def __init__(self, stage: str, hook: str, cause: Exception):
        super().__init__("hook '%s' failed at stage '%s': %s" % (hook, stage, cause))
        self.stage = stage
        self.hook = hook
        self.cause = cause


@dataclass
class Hook:
    name: str
    stage: str
    fn: Callable[[dict], Any]

    def __post_init__(self) -> None:
        if self.stage not in STAGES:
            raise ValueError("未知钩子段：%s（允许 %s）" % (self.stage, list(STAGES)))


class HookChain:
    """按五段顺序执行钩子；同名钩子在同段内按注册顺序执行。"""

    def __init__(self) -> None:
        self._hooks: List[Hook] = []

    def add(self, name: str, stage: str, fn: Callable[[dict], Any]) -> "HookChain":
        self._hooks.append(Hook(name, stage, fn))
        return self

    def hooks(self, stage: str) -> List[Hook]:
        return [h for h in self._hooks if h.stage == stage]

    def run(self, stage: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        ctx["stage"] = stage
        for h in self.hooks(stage):
            try:
                out = h.fn(ctx)
            except Exception as exc:  # noqa: BLE001
                raise HookError(stage, h.name, exc) from exc
            if isinstance(out, dict):
                ctx = out
        return ctx

    def dump(self) -> List[dict]:
        return [{"name": h.name, "stage": h.stage, "order": i}
                for i, h in enumerate(self._hooks)]


@dataclass
class CallConfig:
    """一次调用的横切配置：trace 句柄 / 预算 / 模式 / 钩子。"""

    trace: Any = None
    budget: Dict[str, Any] = field(default_factory=dict)
    mode: str = "sync"
    hooks: Optional[HookChain] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def spend(self, key: str = "calls", n: int = 1) -> None:
        if not self.budget:
            return
        if key not in self.budget:
            self.budget[key] = 0
        self.budget[key] += n
        if "max_" + key in self.budget and self.budget[key] > self.budget["max_" + key]:
            raise RuntimeError("预算超限：%s=%d > %d"
                               % (key, self.budget[key], self.budget["max_" + key]))


class Runnable:
    """统一调用面。子类只实现 `_call`，五段钩子由基类保证。"""

    kind = "runnable"

    def __init__(self, name: str = "") -> None:
        self.name = name or self.kind

    def _call(self, request: Dict[str, Any], config: CallConfig,
              ctx: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def call(self, request: Dict[str, Any],
             config: Optional[CallConfig] = None,
             _nested: bool = False) -> Dict[str, Any]:
        cfg = config or CallConfig()
        ctx = {"request": request, "config": cfg, "node": self.name}
        if cfg.hooks and not _nested:
            cfg.hooks.run("admit", ctx)
            ctx["request"] = ctx.get("request", request)
            if self.kind not in ("guard", "sink"):
                cfg.hooks.run("route", ctx)
        out = self._call(ctx["request"], cfg, ctx)
        if cfg.hooks and not _nested:
            cfg.hooks.run("egress", ctx)
        return out

    def batch(self, requests: List[Dict[str, Any]],
              config: Optional[CallConfig] = None) -> List[Dict[str, Any]]:
        """同一实现即可批量：逐条 call（同步确定性，无并发随机性）。"""
        return [self.call(r, config) for r in requests]

    def __or__(self, other: "Runnable") -> "Pipeline":
        left = self if isinstance(self, Pipeline) else Pipeline([self])
        return Pipeline(left.steps + [other])

    def dump(self) -> dict:
        return {"kind": self.kind, "name": self.name}


class SkillRunnable(Runnable):
    """把一个 Skill 包成 Runnable：传参仍走 Agent._invoke_skill（与内核同一条路）。"""

    kind = "skill"

    def __init__(self, skill: Skill, name: str = "") -> None:
        super().__init__(name or skill.name)
        self.skill = skill

    def _call(self, request: Dict[str, Any], config: CallConfig,
              ctx: Dict[str, Any]) -> Dict[str, Any]:
        if config.hooks:
            config.hooks.run("before_skill", ctx)
        payload = ctx.get("payload")
        if payload is None:
            payload = dict(request)
            payload.setdefault("task", request.get("task", ""))
        config.spend()
        try:
            output = Agent._invoke_skill(self.skill, payload)
            status = "ok"
        except Exception as exc:  # noqa: BLE001
            output, status = None, "error"
            res = {"status": "error", "matched": self.name,
                   "output": None, "err": str(exc)}
        else:
            res = {"status": status, "matched": self.name, "output": output}
        ctx["result"] = res
        if config.hooks:
            config.hooks.run("after_skill", ctx)
        return ctx.get("result", res)

    def dump(self) -> dict:
        d = super().dump()
        d["manifest"] = self.skill.manifest.name
        return d


class AgentRunnable(Runnable):
    """把一个 Agent 包成 Runnable：内部仍调 agent.handle(env)。"""

    kind = "agent"

    def __init__(self, agent: Agent, name: str = "") -> None:
        super().__init__(name or agent.agent_id)
        self.agent = agent

    def _call(self, request: Dict[str, Any], config: CallConfig,
              ctx: Dict[str, Any]) -> Dict[str, Any]:
        if config.hooks:
            config.hooks.run("before_skill", ctx)
        config.spend()
        env = Envelope.create("runnable", self.agent.agent_id, "task",
                              dict(request), metadata=dict(config.metadata))
        res = self.agent.handle(env)
        ctx["result"] = res
        if config.hooks:
            config.hooks.run("after_skill", ctx)
        return ctx.get("result", res)

    def dump(self) -> dict:
        d = super().dump()
        d["role"] = self.agent.role
        return d


class GuardRunnable(Runnable):
    """守卫作为管道节点：block 时短路（返回 blocked），不抛异常。"""

    kind = "guard"

    def __init__(self, guard: Optional[Guard] = None, name: str = "guard") -> None:
        super().__init__(name)
        self.guard = guard or Guard()

    def _call(self, request: Dict[str, Any], config: CallConfig,
              ctx: Dict[str, Any]) -> Dict[str, Any]:
        env = Envelope.create("runnable", "guard", "task", dict(request))
        verdict = self.guard.inspect(env)
        if verdict.action == "block":
            ctx["blocked"] = True
            return {"status": "blocked", "matched": "guard",
                    "verdict": verdict.to_dict(), "output": None}
        ctx["verdict"] = verdict.to_dict()
        return {"status": "ok", "matched": "guard",
                "verdict": verdict.to_dict(), "output": request}


class SinkRunnable(Runnable):
    """终点：收集输出（只做记录，不落盘、不联网）。"""

    kind = "sink"

    def __init__(self, name: str = "sink") -> None:
        super().__init__(name)
        self.items: List[Any] = []

    def _call(self, request: Dict[str, Any], config: CallConfig,
              ctx: Dict[str, Any]) -> Dict[str, Any]:
        self.items.append(request.get("output", request))
        return {"status": "ok", "matched": self.name,
                "output": request.get("output", request), "collected": len(self.items)}


class Pipeline(Runnable):
    """`a | b | c`：前一节点输出作为后一节点输入（字符串直接作 task）。"""

    kind = "pipeline"

    def __init__(self, steps: List[Runnable], name: str = "") -> None:
        super().__init__(name or " -> ".join(s.name for s in steps))
        if not steps:
            raise ValueError("管道至少需要一个节点")
        self.steps = list(steps)

    def _call(self, request: Dict[str, Any], config: CallConfig,
              ctx: Dict[str, Any]) -> Dict[str, Any]:
        current: Dict[str, Any] = dict(request)
        trail: List[str] = []
        for step in self.steps:
            out = step.call(current, config, _nested=True)
            trail.append(step.name)
            if out.get("status") == "blocked":
                return {"status": "blocked", "matched": step.name,
                        "output": None, "trail": trail,
                        "verdict": out.get("verdict")}
            output = out.get("output")
            if isinstance(output, dict):
                current = dict(output)
            else:
                current = {"task": "" if output is None else str(output),
                           "output": output}
        return {"status": "ok", "matched": self.name,
                "output": current.get("output", current), "trail": trail}

    def dump(self) -> dict:
        return {"kind": self.kind, "name": self.name,
                "steps": [s.dump() for s in self.steps]}
