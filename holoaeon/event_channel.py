# -*- coding: utf-8 -*-
"""
EventChannel —— 类型化只读事件流（W18 之二，旁挂）
================================================================================
事件类型收敛到 7 种，只读、零网络；开不开通道都不改变内核输出字节。

纯标准库。
"""
from __future__ import annotations

import json
from typing import Any, Callable, Dict, List, Optional

EVENT_TYPES = (
    "run_start", "route", "skill_call", "guard_verdict",
    "interrupt", "checkpoint", "run_end",
)

assert len(EVENT_TYPES) == 7


class EventChannel:
    """订阅—发布；每条事件带自增 seq，内容只写结构字段（不含时间）。"""

    def __init__(self, types: Optional[List[str]] = None) -> None:
        unknown = set(types or []) - set(EVENT_TYPES)
        if unknown:
            raise ValueError("未知事件类型：%s" % sorted(unknown))
        self.types = list(types or EVENT_TYPES)
        self._events: List[dict] = []
        self._subs: List[Callable[[dict], Any]] = []
        self.seq = 0

    def subscribe(self, fn: Callable[[dict], Any]) -> None:
        self._subs.append(fn)

    def emit(self, etype: str, payload: Dict[str, Any]) -> dict:
        if etype not in EVENT_TYPES:
            raise ValueError("未知事件类型：%s" % etype)
        event = {"seq": self.seq, "type": etype, "payload": dict(payload)}
        self.seq += 1
        if etype in self.types:
            self._events.append(event)
        for fn in self._subs:
            fn(event)
        return event

    # ------------------------------------------------------------ 只读视图
    def events(self, etype: Optional[str] = None) -> List[dict]:
        if etype is None:
            return [dict(e) for e in self._events]
        return [dict(e) for e in self._events if e["type"] == etype]

    def counts(self) -> Dict[str, int]:
        out: Dict[str, int] = {t: 0 for t in EVENT_TYPES}
        for e in self._events:
            out[e["type"]] += 1
        return out

    def to_jsonl(self) -> str:
        return "\n".join(json.dumps(e, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":")) for e in self._events)

    def summary(self) -> dict:
        return {"events": len(self._events), "types": len(EVENT_TYPES),
                "counts": self.counts(), "network": False,
                "readonly": True}


class NullChannel(EventChannel):
    """关掉的通道：接口相同，什么也不记（开不开都不影响内核字节）。"""

    def __init__(self) -> None:
        super().__init__(types=[])

    def emit(self, etype: str, payload: Dict[str, Any]) -> dict:
        return {"seq": -1, "type": etype, "payload": {}, "dropped": True}
