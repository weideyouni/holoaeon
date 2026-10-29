# -*- coding: utf-8 -*-
"""
Memory —— HoloAeon 记忆存储与持久化
================================================================================
三层记忆（对应早期"工作/长期/基因组"记忆，名称中性化）：
  working   工作记忆：当前任务上下文，容量小，可被 consolidate 提升
  longterm  长期记忆：跨任务沉淀，带强度与标签
  archive   归档/知识库：稳定事实与参考，可检索

提供：put/get/recall（按 token 相关）、consolidate（working→longterm）、
decay（强度衰减）、以及 JSON 持久化（to_dict/load）。线程安全。
纯标准库。
"""
from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .skill import tokenize

WORKING = "working"
LONGTERM = "longterm"
ARCHIVE = "archive"
KINDS = (WORKING, LONGTERM, ARCHIVE)

# 各层默认容量（工作记忆刻意较小）
DEFAULT_CAPACITY = {WORKING: 256, LONGTERM: 100000, ARCHIVE: 1000000}


@dataclass
class MemoryItem:
    key: str
    value: Any
    kind: str = WORKING
    tags: List[str] = field(default_factory=list)
    ts: float = 0.0
    strength: float = 1.0

    def to_dict(self) -> dict:
        return {"key": self.key, "value": self.value, "kind": self.kind,
                "tags": list(self.tags), "ts": self.ts,
                "strength": round(self.strength, 5)}

    @staticmethod
    def from_dict(d: dict) -> "MemoryItem":
        return MemoryItem(key=d["key"], value=d["value"], kind=d.get("kind", WORKING),
                          tags=list(d.get("tags", [])), ts=d.get("ts", 0.0),
                          strength=d.get("strength", 1.0))


class Memory:
    """三层记忆：存取/检索/巩固/衰减/持久化。"""

    def __init__(self, capacity: Optional[Dict[str, int]] = None):
        self.capacity = dict(DEFAULT_CAPACITY)
        if capacity:
            self.capacity.update(capacity)
        self._store: Dict[str, MemoryItem] = {}
        self._lock = threading.RLock()

    # ------------------------------------------------------------ 存取
    def put(self, key: str, value: Any, kind: str = WORKING,
            tags: Optional[List[str]] = None, strength: float = 1.0) -> None:
        if kind not in KINDS:
            raise ValueError(f"未知记忆类型：{kind}")
        with self._lock:
            self._store[key] = MemoryItem(
                key=key, value=value, kind=kind,
                tags=list(tags or []), ts=time.time(), strength=strength
            )
            self._enforce_capacity(kind)

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            item = self._store.get(key)
            return item.value if item else default

    def _enforce_capacity(self, kind: str) -> None:
        items = [it for it in self._store.values() if it.kind == kind]
        over = len(items) - self.capacity[kind]
        if over > 0:
            items.sort(key=lambda it: (it.strength, it.ts))
            for it in items[:over]:
                self._store.pop(it.key, None)

    # ------------------------------------------------------------ 检索
    def recall(self, query: str, k: int = 5, kind: Optional[str] = None) -> List[dict]:
        """按 token 重叠 + 标签命中对记忆打分，返回前 k。"""
        q = set(tokenize(query))
        scored = []
        with self._lock:
            items = list(self._store.values())
        for it in items:
            if kind is not None and it.kind != kind:
                continue
            text = set(tokenize(str(it.key) + " " + " ".join(it.tags)
                                + " " + str(it.value)[:200]))
            overlap = len(q & text)
            if overlap:
                score = overlap / max(1, len(q | text)) + 0.1 * it.strength
                scored.append((score, it))
        scored.sort(key=lambda t: -t[0])
        return [it.to_dict() for _, it in scored[:k]]

    # ------------------------------------------------------------ 巩固 / 衰减
    def consolidate(self, min_strength: float = 0.3) -> int:
        """把足够强的工作记忆提升为长期记忆。返回提升条数。"""
        moved = 0
        with self._lock:
            for it in list(self._store.values()):
                if it.kind == WORKING and it.strength >= min_strength:
                    it.kind = LONGTERM
                    moved += 1
        return moved

    def decay(self, rate: float = 0.01) -> None:
        """对长期/工作记忆做强度衰减（归档不衰减）。"""
        with self._lock:
            for it in self._store.values():
                if it.kind in (WORKING, LONGTERM):
                    it.strength = max(0.0, it.strength - rate)

    def stats(self) -> dict:
        with self._lock:
            counts = {k: 0 for k in KINDS}
            for it in self._store.values():
                counts[it.kind] += 1
            return {"total": len(self._store), **counts}

    # ------------------------------------------------------------ 持久化
    def to_dict(self) -> dict:
        with self._lock:
            return {"items": [it.to_dict() for it in self._store.values()]}

    def dump(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @staticmethod
    def load(path: str) -> "Memory":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        mem = Memory()
        for d in data.get("items", []):
            item = MemoryItem.from_dict(d)
            mem._store[item.key] = item
        return mem
