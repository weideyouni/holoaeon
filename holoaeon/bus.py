# -*- coding: utf-8 -*-
"""
Bus —— HoloAeon 消息总线（通用，不域锁定）
================================================================================
提供三种通信模式，全部线程安全（RLock）：
  1. 主题订阅  pub/sub：subscribe(topic, handler) / publish(...)
  2. 消息路由  route：register_route(topic, target)，把主题映射到目标地址
  3. 直接寻址  address：register_address(agent_id, handler)，按信封 recipient 投递

与早期 ThreadBus 的区别：不做 domain 硬锁定（任意领域可用）；原生支持 Envelope；
handler 抛错会被捕获并作为失败回执返回，不会中断其他订阅者。
纯标准库。
"""
from __future__ import annotations

import threading
import time
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional

from .envelope import BROADCAST, Envelope
from .spec import BUS_ID, GATE_CLOSE, GATE_OPEN

Handler = Callable[[Envelope], Any]


class Bus:
    """通用消息总线：主题订阅 + 路由 + 直接寻址 + 全链路 trace。"""

    def __init__(self, bus_id: str = BUS_ID, *, history_limit: int = 10000):
        self.bus_id = bus_id
        self._lock = threading.RLock()
        self._subs: Dict[str, List[Handler]] = defaultdict(list)
        self._addresses: Dict[str, Handler] = {}
        self._routes: Dict[str, str] = {}
        self._messages: List[dict] = []
        self._history_limit = history_limit
        self._started = time.time()
        self._seq = 0

    # ------------------------------------------------------------ 主题订阅
    def subscribe(self, topic: str, handler: Handler) -> str:
        with self._lock:
            self._subs[topic].append(handler)
            return f"sub:{topic}:{len(self._subs[topic])}"

    def unsubscribe(self, topic: str, handler: Handler) -> bool:
        with self._lock:
            if handler in self._subs.get(topic, []):
                self._subs[topic].remove(handler)
                return True
            return False

    # ------------------------------------------------------------ 直接寻址
    def register_address(self, address: str, handler: Handler) -> None:
        with self._lock:
            self._addresses[address] = handler

    def unregister_address(self, address: str) -> None:
        with self._lock:
            self._addresses.pop(address, None)

    # ------------------------------------------------------------ 路由
    def register_route(self, topic: str, target: str) -> None:
        with self._lock:
            self._routes[topic] = target

    def route_of(self, topic: str) -> Optional[str]:
        with self._lock:
            return self._routes.get(topic)

    # ------------------------------------------------------------ 发布（主题）
    def publish(
        self,
        topic: str,
        payload: Optional[dict] = None,
        source: str = "local",
        **kwargs: Any,
    ) -> List[dict]:
        env = Envelope.create(source, BROADCAST, topic, payload, **kwargs)
        return self.send(env)

    def _record(self, env: Envelope, delivered: int) -> None:
        with self._lock:
            self._seq += 1
            self._messages.append(
                {
                    "seq": self._seq,
                    "ts": env.ts or time.time(),
                    "topic": env.topic,
                    "sender": env.sender,
                    "recipient": env.recipient,
                    "delivered": delivered,
                    "mode": env.mode,
                }
            )
            if len(self._messages) > self._history_limit:
                self._messages = self._messages[-self._history_limit:]

    # ------------------------------------------------------------ 发送（信封）
    def send(self, env: Envelope) -> List[dict]:
        """按信封投递：recipient 命中直接地址则直投；同时投递给该 topic 的订阅者。"""
        results: List[dict] = []

        # 路由：若 topic 有显式路由且 recipient 为广播，改写目标
        target = env.recipient
        if target == BROADCAST:
            routed = self.route_of(env.topic)
            if routed is not None:
                target = routed

        with self._lock:
            direct = self._addresses.get(target)
            topic_handlers = list(self._subs.get(env.topic, []))
            if target == BROADCAST:
                addrs = dict(self._addresses)
            else:
                addrs = {target: direct} if direct else {}

        # 直投（寻址）
        for addr, handler in addrs.items():
            out_env = env if addr == env.recipient else env.forward(env.sender, addr)
            results.append(self._safe_call(handler, out_env, addr))

        # 主题订阅者
        for handler in topic_handlers:
            results.append(self._safe_call(handler, env, "topic"))

        self._record(env, len([r for r in results if r.get("ok")]))
        return results

    @staticmethod
    def _safe_call(handler: Handler, env: Envelope, where: str) -> dict:
        try:
            out = handler(env)
            return {"ok": True, "where": where, "out": out}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "where": where, "err": str(exc)}

    # ------------------------------------------------------------ 门禁令牌
    def open_gate(self, secret: str) -> bool:
        return secret == GATE_OPEN

    def close_gate(self, secret: str) -> bool:
        return secret == GATE_CLOSE

    # ------------------------------------------------------------ 状态
    def heartbeat(self) -> dict:
        with self._lock:
            return {
                "bus_id": self.bus_id,
                "uptime_s": round(time.time() - self._started, 3),
                "topics": len(self._subs),
                "routes": len(self._routes),
                "addresses": len(self._addresses),
                "messages": len(self._messages),
            }

    def stats(self) -> dict:
        with self._lock:
            return {
                "topics": sorted(self._subs.keys()),
                "routes": dict(self._routes),
                "addresses": sorted(self._addresses.keys()),
                "message_count": len(self._messages),
            }
