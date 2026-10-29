# -*- coding: utf-8 -*-
"""
ModelAdapter —— HoloAeon 模型适配（任意 Agent 用任意模型）
================================================================================
ModelAdapter 是一层【登记 + 路由 + 映射】的横切适配层：
  · 后端登记 ModelBackend：任意 provider/model（本地/私有/云端），声明上下文窗口、
    能力、模态、成本
  · 路由策略 ROUTE_STRATEGIES（8 种）：按任务特征/约束选模型
  · 消息映射 MASKING_TYPES（10 种）：把统一 Envelope 映射为各模型的消息格式
  · 用量指标 USAGE_METRICS（8 个）：tokens/延迟/成本等（simulated）

本模块不启动网关、不连真实供应商、不发起网络请求；只做确定性的登记与映射，
真实调用由你自行接入（见 docs/model-adapter.md）。纯标准库。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .envelope import Envelope
from .spec import ModelAdapterConfig

# 8 种路由策略
ROUTE_STRATEGIES = (
    "cheapest", "largest_context", "fastest", "capability_match",
    "round_robin", "load_balance", "modality_match", "fallback",
)
# 10 种消息格式映射
MASKING_TYPES = (
    "openai_chat", "anthropic", "gemini", "llama", "completion",
    "embedding", "function_call", "vision", "tool_use", "batch",
)
# 8 个用量指标
USAGE_METRICS = (
    "prompt_tokens", "completion_tokens", "total_tokens",
    "latency_ms", "input_cost", "output_cost", "total_cost", "requests",
)


@dataclass
class ModelBackend:
    name: str
    provider: str
    family: str = "chat"                    # chat | completion | embedding
    context_window: int = 8192
    latency_ms: int = 500
    input_cost: float = 0.0                 # 每 1k tokens
    output_cost: float = 0.0
    capabilities: List[str] = field(default_factory=list)
    modalities: List[str] = field(default_factory=lambda: ["text"])
    load: float = 0.0

    def snapshot(self) -> dict:
        return {"name": self.name, "provider": self.provider,
                "family": self.family, "context_window": self.context_window,
                "capabilities": self.capabilities,
                "modalities": self.modalities, "load": round(self.load, 3)}


@dataclass
class ModelAdapter:
    """模型适配：登记 + 路由 + 消息映射 + 用量（simulated）。"""
    config: ModelAdapterConfig = field(default_factory=ModelAdapterConfig)

    def __post_init__(self) -> None:
        self.backends: Dict[str, ModelBackend] = {}
        self._rr = 0
        self.usage: Dict[str, Dict[str, float]] = {}

    # ------------------------------------------------------------ 登记
    def register_backend(self, backend: ModelBackend) -> ModelBackend:
        self.backends[backend.name] = backend
        self.usage[backend.name] = {m: 0.0 for m in USAGE_METRICS}
        return backend

    def names(self) -> List[str]:
        return sorted(self.backends.keys())

    # ------------------------------------------------------------ 路由（8 策略）
    def route(self, task: str, *, strategy: str = "cheapest",
              need: Optional[List[str]] = None,
              need_modality: Optional[str] = None,
              max_cost: Optional[float] = None) -> Optional[str]:
        if strategy not in ROUTE_STRATEGIES:
            raise ValueError(f"未知路由策略：{strategy}")
        cands = list(self.backends.values())
        if not cands:
            return None
        if need:
            cands = [b for b in cands if all(c in b.capabilities for c in need)]
        if need_modality:
            cands = [b for b in cands if need_modality in b.modalities]
        if max_cost is not None:
            cands = [b for b in cands
                     if b.input_cost + b.output_cost <= max_cost]
        if not cands:
            cands = list(self.backends.values())  # 回退（fallback）

        if strategy == "cheapest":
            b = min(cands, key=lambda x: x.input_cost + x.output_cost)
        elif strategy == "largest_context":
            b = max(cands, key=lambda x: x.context_window)
        elif strategy == "fastest":
            b = min(cands, key=lambda x: x.latency_ms)
        elif strategy == "capability_match":
            b = max(cands, key=lambda x: len(x.capabilities))
        elif strategy == "round_robin":
            b = cands[self._rr % len(cands)]; self._rr += 1
        elif strategy == "load_balance":
            b = min(cands, key=lambda x: x.load)
        elif strategy == "modality_match":
            b = max(cands, key=lambda x: len(x.modalities))
        else:
            b = sorted(cands, key=lambda x: x.name)[0]
        return b.name

    # ------------------------------------------------------------ 消息映射（10）
    def format_messages(self, backend_name: str, env: Envelope,
                        masking: str = "openai_chat") -> dict:
        if masking not in MASKING_TYPES:
            raise ValueError(f"未知消息映射：{masking}")
        task = env.payload.get("task", "")
        if masking == "openai_chat":
            return {"model": backend_name,
                    "messages": [{"role": "user", "content": task}]}
        if masking == "anthropic":
            return {"model": backend_name, "max_tokens": 1024,
                    "messages": [{"role": "user", "content": task}]}
        if masking == "gemini":
            return {"contents": [{"parts": [{"text": task}]}]}
        if masking == "llama":
            return {"model": backend_name, "prompt": task, "stream": False}
        if masking == "completion":
            return {"model": backend_name, "prompt": task}
        if masking == "embedding":
            return {"model": backend_name, "input": task}
        if masking == "function_call":
            return {"model": backend_name, "messages": [
                {"role": "user", "content": task}], "tool_choice": "auto"}
        if masking == "vision":
            return {"model": backend_name, "messages": [
                {"role": "user", "content": [{"type": "text", "text": task}]}]}
        if masking == "tool_use":
            return {"model": backend_name, "tools": [],
                    "messages": [{"role": "user", "content": task}]}
        return {"batch": [{"model": backend_name, "prompt": task}]}

    # ------------------------------------------------------------ 用量（模拟）
    def record_usage(self, backend_name: str, prompt_tokens: int,
                     completion_tokens: int = 0) -> dict:
        b = self.backends[backend_name]
        u = self.usage[backend_name]
        u["prompt_tokens"] += prompt_tokens
        u["completion_tokens"] += completion_tokens
        u["total_tokens"] += prompt_tokens + completion_tokens
        u["input_cost"] += prompt_tokens / 1000 * b.input_cost
        u["output_cost"] += completion_tokens / 1000 * b.output_cost
        u["total_cost"] = u["input_cost"] + u["output_cost"]
        u["requests"] += 1
        return dict(u)

    def usage_report(self) -> dict:
        return {name: {k: round(v, 5) for k, v in u.items()}
                for name, u in self.usage.items()}

    def snapshot(self) -> dict:
        return {"backends": len(self.backends),
                "route_strategies": len(ROUTE_STRATEGIES),
                "masking_types": len(MASKING_TYPES),
                "usage_metrics": len(USAGE_METRICS),
                "backend_names": self.names()}
