# -*- coding: utf-8 -*-
"""V4.3 · B8 事实包接 ModelAdapter（路由 + 用量登记，仍不联网、不出剂量、不做诊断）。

补齐的是 V4.1-B1 留下的那一格
------------------------------
V4.1-B1 的 `ReasoningBridge` 只做到「问题 -> 能力路由 -> 封缄事实包」，事实包生成后没有再
进推理层。本模块把事实包送进 `holoaeon.model_adapter.ModelAdapter`：登记一个本地后端、
按 `capability_match` 选一个后端、按事实条数登记 simulated 用量，最后给出 `adapter` 段与
独立的 `adapter_seal`。

边界（与 V4.1 一致，未放宽）
--------------------------
1. **红线优先**：`ReasoningBridge.guard()` 判 blocked 时**不进适配层**，adapter 段只写
   `used=false, reason=guard_blocked`；事实包本身也不再生成。
2. **不联网**：`ModelAdapter` 本身就只做登记/路由/映射，本模块不 import 任何网络库，
   也不传 provider 凭证 —— `network=false` 是设计属性，不是承诺。
3. **不改事实包**：`pack` 原样返回（含原 `seal`），adapter 信息只加在外层，避免改动已冻结的
   封缄口径（V4.1 校验器仍可复用原 seal）。
4. **不宣称疗效/剂量/诊断**：`usage` 只是 token 估算（simulated），不是临床输出。
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from typing import Any, Dict, List, Optional

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from ..model_adapter import ModelAdapter, ModelBackend  # noqa: E402
from .plugin_runtime import ReasoningBridge, digest_of  # noqa: E402

BACKEND_NAME = "fact-pack-local"
STRATEGY = "capability_match"
REQUIRED_CAPABILITIES = ("fact_lookup", "count_check")


def default_adapter() -> ModelAdapter:
    """登记一个本地后端：只做事实包组装，无网络、无成本。"""
    adapter = ModelAdapter()
    adapter.register_backend(ModelBackend(
        name=BACKEND_NAME,
        provider="local",
        family="chat",
        context_window=8192,
        latency_ms=1,
        input_cost=0.0,
        output_cost=0.0,
        capabilities=list(REQUIRED_CAPABILITIES),
        modalities=["text"],
        load=0.0,
    ))
    return adapter


class AdapterBridge:
    """`ReasoningBridge` 的上层：事实包 + 适配层路由 + simulated 用量。"""

    def __init__(self, bridge: ReasoningBridge, adapter: Optional[ModelAdapter] = None) -> None:
        self.bridge = bridge
        self.adapter = adapter or default_adapter()

    # -- 适配层 ------------------------------------------------------------
    def pick(self, task: str = "fact_pack") -> Optional[str]:
        return self.adapter.route(task, strategy=STRATEGY,
                                  need=list(REQUIRED_CAPABILITIES))

    def ask(self, question: str, max_caps: int = 3) -> Dict[str, Any]:
        pack = self.bridge.ask(question, max_caps=max_caps)
        blocked = bool(pack.get("guard", {}).get("blocked"))
        backend = None if blocked else self.pick()
        usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        if not blocked and backend:
            facts = pack.get("facts") or []
            prompt = len(question or "")
            completion = sum(len(str(f.get("name_cn") or "")) + 8 for f in facts)
            usage = {"prompt_tokens": prompt, "completion_tokens": completion,
                     "total_tokens": prompt + completion}
            bucket = self.adapter.usage.setdefault(backend, {})
            for key, value in usage.items():
                bucket[key] = float(bucket.get(key, 0.0)) + value
            bucket["requests"] = float(bucket.get("requests", 0.0)) + 1

        adapter_note = {
            "used": bool(not blocked and backend),
            "backend": backend,
            "strategy": STRATEGY,
            "required_capabilities": list(REQUIRED_CAPABILITIES),
            "network": False,
            "usage_simulated": usage,
            "reason": "guard_blocked" if blocked else ("no_backend" if not backend else "pass"),
        }
        body = {"q": pack.get("question_digest"), "b": backend,
                "n": adapter_note["used"], "usage": usage, "e": "simulated"}
        return {"pack": pack, "adapter": adapter_note,
                "adapter_seal": digest_of(body),
                "evidence_class": "simulated",
                "note": "事实包进适配层路由；不联网、不出剂量、不做诊断、不写疗效"}


def probe(root: Optional[str] = None, guest_root: Optional[str] = None,
          secret: str = "潮起开门", question: str = "这条经络通道属于哪个分组？17 通道如何分布"
          ) -> Dict[str, Any]:
    """供校验器调用：默认态 -> 启用 -> 正常问句 -> 剂量问句（应被红线拦下）。"""
    from .plugin_runtime import PluginRuntime

    runtime = PluginRuntime.load(root=root, guest_root=guest_root)
    before = runtime.resolve_all()
    runtime.enable(secret)
    bridge = AdapterBridge(ReasoningBridge(runtime))
    normal = bridge.ask(question)
    dose = bridge.ask("这个方子每次服用多少 mg？给我剂量")

    # V4.4：真实模型目录的「默认全关」状态也在此一并回读（不联网、只拼请求）
    try:
        from .model_gateway import build_gateway
        gw = build_gateway(root or ".")
        gw_state = gw.state()
        gw_attached = gw.attach(bridge.adapter)
    except Exception as exc:  # 目录缺失时不让整个探针失败
        gw_state = {"error": type(exc).__name__}
        gw_attached = []

    return {"off": before, "normal": normal, "dose": dose,
            "backends": bridge.adapter.names(), "usage": bridge.adapter.usage,
            "gateway": {"state": gw_state, "attached_backends": gw_attached}}
