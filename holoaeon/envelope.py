# -*- coding: utf-8 -*-
"""
Envelope —— HoloAeon 统一信封 / 消息原语
================================================================================
所有 agent 之间、agent 与总线/工具/外部后端之间的通信都封装为一个 Envelope。
统一信封让路由、守卫、审计、trace、重试与序列化都有一个确定的落点。

字段：
  message_id    全局唯一（确定性，由 sender + seq 派生，也可显式指定）
  sender        发送者标识（agent_id / "main" / 工具名）
  recipient     目标标识（agent_id / topic；"*" 表示广播）
  topic         主题（路由键）
  payload       消息体（任意可序列化数据；约定为 dict）
  conversation  会话 id（同一会话的消息共享）
  task          任务 id（同一任务的协作消息共享）
  metadata      附加元数据（优先级/置信度/重试/标签等）
  trace         已经过的节点序列（每次转发追加，用于全链路追踪与环路检测）
  mode          simulated | live（默认 simulated）
  ts            创建时间（epoch 秒；可注入以便确定性测试）
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

from .spec import MODE_SIMULATED

BROADCAST = "*"


@dataclass
class Envelope:
    message_id: str
    sender: str
    recipient: str
    topic: str
    payload: Dict[str, Any] = field(default_factory=dict)
    conversation: str = "default"
    task: str = "default"
    metadata: Dict[str, Any] = field(default_factory=dict)
    trace: List[str] = field(default_factory=list)
    mode: str = MODE_SIMULATED
    ts: float = 0.0

    # ------------------------------------------------------------ 工厂
    @staticmethod
    def create(
        sender: str,
        recipient: str,
        topic: str,
        payload: Optional[Dict[str, Any]] = None,
        *,
        conversation: str = "default",
        task: str = "default",
        metadata: Optional[Dict[str, Any]] = None,
        message_id: Optional[str] = None,
        mode: str = MODE_SIMULATED,
        ts: Optional[float] = None,
    ) -> "Envelope":
        mid = message_id or f"{sender}:{uuid.uuid4().hex[:10]}"
        return Envelope(
            message_id=mid,
            sender=sender,
            recipient=recipient,
            topic=topic,
            payload=dict(payload or {}),
            conversation=conversation,
            task=task,
            metadata=dict(metadata or {}),
            trace=[sender],
            mode=mode,
            ts=time.time() if ts is None else ts,
        )

    @staticmethod
    def broadcast(
        sender: str,
        topic: str,
        payload: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> "Envelope":
        return Envelope.create(sender, BROADCAST, topic, payload, **kwargs)

    # ------------------------------------------------------------ 派生
    def reply(
        self,
        sender: str,
        payload: Optional[Dict[str, Any]] = None,
        *,
        topic: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "Envelope":
        """对本信封回信：沿用 conversation/task，sender 变为回信者，recipient 回到原发件人。"""
        child = Envelope.create(
            sender=sender,
            recipient=self.sender,
            topic=topic or self.topic,
            payload=payload,
            conversation=self.conversation,
            task=self.task,
            metadata={**self.metadata, **(metadata or {})},
            mode=self.mode,
        )
        child.trace = list(self.trace) + [sender]
        return child

    def forward(
        self,
        sender: str,
        recipient: str,
        *,
        topic: Optional[str] = None,
        annotate: Optional[Dict[str, Any]] = None,
    ) -> "Envelope":
        """转发到下一个节点（路由/中继）：追加 trace，可叠加元数据。"""
        child = Envelope.create(
            sender=sender,
            recipient=recipient,
            topic=topic or self.topic,
            payload=self.payload,
            conversation=self.conversation,
            task=self.task,
            metadata={**self.metadata, **(annotate or {})},
            mode=self.mode,
            message_id=self.message_id,
        )
        child.trace = list(self.trace) + [sender]
        return child

    def visited(self, node: str) -> bool:
        return node in self.trace

    # ------------------------------------------------------------ 序列化
    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "recipient": self.recipient,
            "topic": self.topic,
            "payload": self.payload,
            "conversation": self.conversation,
            "task": self.task,
            "metadata": self.metadata,
            "trace": list(self.trace),
            "mode": self.mode,
            "ts": self.ts,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Envelope":
        return Envelope(
            message_id=d["message_id"],
            sender=d["sender"],
            recipient=d["recipient"],
            topic=d["topic"],
            payload=dict(d.get("payload", {})),
            conversation=d.get("conversation", "default"),
            task=d.get("task", "default"),
            metadata=dict(d.get("metadata", {})),
            trace=list(d.get("trace", [])),
            mode=d.get("mode", MODE_SIMULATED),
            ts=d.get("ts", 0.0),
        )


def envelope_batch(
    sender: str,
    recipients: Sequence[str],
    topic: str,
    payload: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> List[Envelope]:
    """为一组目标各生成一个信封（共享会话/任务，message_id 各自唯一）。"""
    return [Envelope.create(sender, r, topic, payload, **kwargs) for r in recipients]
