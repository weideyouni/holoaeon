# -*- coding: utf-8 -*-
"""
SpanTree —— trace span 树（W13，旁挂）
================================================================================
每个 run 是一棵树：根 span 之下挂 agent / skill / guard 子 span。
结构可序列化、可哈希；**耗时只打印，不进哈希**（V2 R-1 既定，V3-2 复述）。

structure_hash 只取结构字段：span_id / parent / name / kind / verdict / children。
latency_ms 放在 `timings` 里，单独展示。

纯标准库。
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


def _canon(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


@dataclass
class Span:
    name: str
    kind: str = "run"
    parent: str = ""
    span_id: str = ""
    verdict: str = "ok"
    attrs: Dict[str, Any] = field(default_factory=dict)
    latency_ms: float = 0.0
    children: List["Span"] = field(default_factory=list)

    def add(self, name: str, kind: str = "skill", verdict: str = "ok",
            **attrs: Any) -> "Span":
        child = Span(name=name, kind=kind, parent=self.span_id or self.name,
                     verdict=verdict, attrs=attrs)
        child.span_id = "%s/%s#%d" % (self.span_id or self.name, name,
                                     len(self.children) + 1)
        self.children.append(child)
        return child

    def structural(self) -> dict:
        return {
            "span_id": self.span_id or self.name,
            "parent": self.parent,
            "name": self.name,
            "kind": self.kind,
            "verdict": self.verdict,
            "children": [c.structural() for c in self.children],
        }


class SpanTree:
    """一次 run 的 span 树；`structure_hash` 与耗时无关。"""

    def __init__(self, name: str = "run", run_id: str = "") -> None:
        self.root = Span(name=name, kind="run", span_id=run_id or name)
        self.run_id = self.root.span_id
        self.timings: Dict[str, float] = {}

    # ------------------------------------------------------------ 建树
    def child(self, name: str, kind: str = "skill", verdict: str = "ok",
              **attrs: Any) -> Span:
        return self.root.add(name, kind, verdict, **attrs)

    def record(self, span_id: str, latency_ms: float) -> None:
        """耗时记录：只进 timings，不进结构哈希。"""
        self.timings[span_id] = round(float(latency_ms), 3)

    # ------------------------------------------------------------ 序列化
    def to_dict(self) -> dict:
        return {"run_id": self.run_id, "tree": self.root.structural()}

    def structure_hash(self, length: int = 16) -> str:
        blob = _canon({"run_id": self.run_id, "tree": self.root.structural()})
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:length]

    def to_json(self) -> str:
        return _canon({"run_id": self.run_id, "tree": self.root.structural(),
                       "timings": self.timings})

    @staticmethod
    def from_dict(d: dict) -> "SpanTree":
        t = SpanTree()
        t.run_id = d.get("run_id", "")
        t.root = _span_from(d["tree"])
        t.timings = dict(d.get("timings", {}))
        return t

    # ------------------------------------------------------------ 视图
    def flat(self) -> List[dict]:
        out: List[dict] = []

        def walk(s: Span, depth: int) -> None:
            out.append({"span_id": s.span_id or s.name, "name": s.name,
                        "kind": s.kind, "verdict": s.verdict, "depth": depth,
                        "latency_ms": self.timings.get(s.span_id or s.name)})
            for c in s.children:
                walk(c, depth + 1)

        walk(self.root, 0)
        return out

    def summary(self) -> dict:
        flat = self.flat()
        return {
            "run_id": self.run_id,
            "spans": len(flat),
            "kinds": sorted({f["kind"] for f in flat}),
            "blocked": sum(1 for f in flat if f["verdict"] == "blocked"),
            "structure_hash": self.structure_hash(),
            "note": "latency_ms 只展示，不参与 structure_hash",
        }


def _span_from(d: dict) -> Span:
    s = Span(name=d.get("name", ""), kind=d.get("kind", "run"),
             parent=d.get("parent", ""), span_id=d.get("span_id", ""),
             verdict=d.get("verdict", "ok"))
    for c in d.get("children", []):
        s.children.append(_span_from(c))
    return s


class SpanRecorder:
    """把 SpanTree 包成可放进 CallConfig.trace 的轻量句柄。"""

    def __init__(self, tree: Optional[SpanTree] = None) -> None:
        self.tree = tree or SpanTree()

    def span(self, name: str, kind: str = "skill") -> Span:
        return self.tree.child(name, kind)

    def close(self, span: Span, latency_ms: float = 0.0,
              verdict: str = "ok") -> None:
        span.verdict = verdict
        self.tree.record(span.span_id, latency_ms)
