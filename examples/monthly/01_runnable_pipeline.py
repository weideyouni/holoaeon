# -*- coding: utf-8 -*-
"""
examples/monthly/01_runnable_pipeline.py —— 每月一个可跑示例（W19）
================================================================================
只演示 V3 新增的旁挂面：统一调用协议、五段钩子、span 树、事件流。
不依赖任何第三方库；不联网。CI 由 scripts/v3_gate.py 的 A4/A5/A10 覆盖。

用法：
    python examples\\monthly\\01_runnable_pipeline.py
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from holoaeon.audit.span_tree import SpanRecorder, SpanTree  # noqa: E402
from holoaeon.event_channel import EventChannel  # noqa: E402
from holoaeon.runnable import (  # noqa: E402
    CallConfig, GuardRunnable, HookChain, Pipeline, SkillRunnable, SinkRunnable,
)
from holoaeon.skill import SkillRegistry  # noqa: E402


def build_registry() -> SkillRegistry:
    r = SkillRegistry()

    def word_count(text: str) -> dict:
        return {"chars": len(text), "words": len(text.split())}

    r.register_fn("word_count", word_count, description="统计字数 word count",
                  tags=["text", "count"])
    return r


def main() -> int:
    reg = build_registry()
    tree = SpanTree("monthly-example")
    rec = SpanRecorder(tree)
    root = rec.span("pipeline", "run")
    ev = EventChannel()
    hooks = HookChain()
    for stage in ("admit", "route", "before_skill", "after_skill", "egress"):
        hooks.add("log-" + stage, stage,
                  lambda ctx, s=stage: ev.emit("route", {"stage": s}) or ctx)

    pipe = Pipeline([GuardRunnable(), SkillRunnable(reg.get("word_count")),
                     SinkRunnable()])
    out = pipe.call({"task": "HoloAeon V3 示例：统计这句话的字数。"},
                    CallConfig(trace=rec, hooks=hooks))
    rec.close(root, 2.0)

    print("status =", out["status"])
    print("trail  =", out["trail"])
    print("output =", out["output"])
    print("span   =", tree.summary())
    print("events =", ev.counts())
    return 0 if out["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
