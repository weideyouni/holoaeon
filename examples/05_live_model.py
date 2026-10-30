# -*- coding: utf-8 -*-
"""
examples/05_live_model —— 宿主模型桥的最小用法（无桥环境自动 skip）
================================================================================
运行：python examples/05_live_model.py
  · 无 Ollama / 无网络 → 打印 skip，退出码 0（示例不阻塞 CI）
  · 有 Ollama       → 打印 mode="live" 的五要素回执
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (ROOT, os.path.join(ROOT, "bridges")):
    if p not in sys.path:
        sys.path.insert(0, p)

from holoaeon.model_adapter import ModelAdapter, ModelBackend   # noqa: E402


def main() -> int:
    try:
        import live_client                                          # noqa: E402
        import transport                                            # noqa: E402
    except ImportError as exc:
        print("skip: bridges 不可用（%s）" % exc)
        return 0

    probe = transport.get_json("http://127.0.0.1:11434/api/tags", timeout=2.0)
    if not probe.get("ok"):
        print("skip: 本机无 Ollama（%s）—— 先跑 bridges/quickstart.py --check"
              % probe.get("error_type"))
        return 0

    adapter = ModelAdapter()
    adapter.register_backend(ModelBackend("qwen2.5:0.5b", "local", latency_ms=80))
    client = live_client.LiveModelClient(adapter=adapter, backend_name="ollama",
                                         model="qwen2.5:0.5b")
    r = client.ask("用一句话解释什么是超向量（hypervector）。", strategy="fastest")
    if not r.get("ok", True):
        print("live call failed:", r.get("error_type"), r.get("status"))
        return 0
    print("mode    :", r["mode"])          # 必须是 live，不是 simulated
    print("backend :", r["backend"])
    print("model   :", r["model"])
    print("tokens  :", r["tokens"])
    print("latency : %.1f ms" % r["latency_ms"])
    print("output  :", (r["output"] or "")[:200])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
