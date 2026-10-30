# -*- coding: utf-8 -*-
"""
Host bridge · live_client —— 把 ModelAdapter 的路由决策变成一次真实调用
================================================================================
它只做三件事：
  1) 问 ModelAdapter 该用哪个后端（route / format_messages 全部复用，不另造口径）；
  2) 让 transport 把请求发出去；
  3) 把回执如实标成 mode="live"（与 simulated 严格区分），并追加一条审计。

审计（bridges/.live_audit.jsonl）只记：
  seq / backend / model / prompt_sha16 / response_sha16 / latency_ms / tokens
  —— 不记明文 prompt、不记 key、不记完整响应。这与 nephron 的隐私立场一致。

它保护了哪条立场：代价显式 + 宿主边界 —— 非确定的部分（延迟、模型自由发挥）
被隔离在桥里并留痕，核心包仍然确定。
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from typing import Dict, List, Optional

from holoaeon.envelope import Envelope
from holoaeon.model_adapter import ModelAdapter

try:                                   # 支持 `python bridges/quickstart.py` 直接运行
    from . import backends, transport
except ImportError:                    # pragma: no cover
    import backends, transport         # type: ignore

AUDIT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".live_audit.jsonl")


def _sha16(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()[:16]


class LiveModelClient:
    """一次构造 = 一个后端目标；目标不合规会在构造阶段被拒（fail-closed）。"""

    def __init__(self, adapter: Optional[ModelAdapter] = None,
                 backend_name: str = "ollama",
                 base_url: Optional[str] = None,
                 model: str = "qwen2.5:0.5b",
                 allow_remote: bool = False,
                 allowlist: Optional[List[str]] = None,
                 audit_path: Optional[str] = None,
                 timeout: float = 120.0):
        self.adapter = adapter or ModelAdapter()
        self.backend = backends.get_backend(backend_name, base_url)
        self.model = model
        self.timeout = timeout
        self.audit_path = audit_path or AUDIT_PATH

        verdict = backends.check_target(self.backend.base_url, allow_remote, allowlist)
        if not verdict["ok"]:
            raise ValueError("bridge target rejected: %s host=%s hint=%s"
                             % (verdict["reason"], verdict.get("host", ""),
                                verdict.get("hint", "")))
        self.target = verdict

    # ---------------------------------------------------------------- 主入口
    def ask(self, task: str, strategy: str = "cheapest") -> Dict:
        if self.backend.name == "echo":
            return {"mode": "echo", "ok": True, "output": task, "backend": "echo",
                    "model": "echo", "tokens": {"prompt_tokens": None,
                                                "completion_tokens": None},
                    "latency_ms": 0.0,
                    "note": "离线自检后端：未发生任何网络调用"}

        env = Envelope.create("bridge", "model", "task", {"task": task})
        routed = None
        try:
            routed = self.adapter.route(task, strategy=strategy)
        except ValueError:
            routed = None
        model = routed or self.model
        fmt = self.adapter.format_messages(model, env, masking="openai_chat")
        messages = fmt.get("messages") or [{"role": "user", "content": task}]
        payload = backends.build_payload(self.backend, messages, model)

        started = time.perf_counter()
        res = transport.post_json(self.backend.chat_url(), payload,
                                  timeout=self.timeout,
                                  headers=self.backend.headers())
        latency_ms = round((time.perf_counter() - started) * 1000, 2)

        if not res.get("ok"):
            return {"mode": "live", "ok": False, "error_type": res.get("error_type"),
                    "status": res.get("status"), "detail": res.get("detail"),
                    "backend": self.backend.name, "model": model,
                    "latency_ms": latency_ms,
                    "note": "桥已如实回报失败；未重试、未伪造输出"}

        parsed = backends.parse_response(self.backend, res.get("data") or {})
        out = parsed.get("output") or ""
        tokens = {"prompt_tokens": parsed.get("prompt_tokens"),
                  "completion_tokens": parsed.get("completion_tokens")}
        if tokens["prompt_tokens"] is not None and model in self.adapter.backends:
            self.adapter.record_usage(model, int(tokens["prompt_tokens"]),
                                      int(tokens["completion_tokens"] or 0))

        receipt = {"mode": "live", "ok": True, "output": out,
                   "backend": self.backend.name, "model": model,
                   "tokens": tokens, "latency_ms": latency_ms,
                   "response_bytes": res.get("bytes")}
        self._audit(task, out, receipt)
        return receipt

    # ---------------------------------------------------------------- 审计
    def _audit(self, task: str, output: str, receipt: Dict) -> Dict:
        seq = 1
        try:
            if os.path.exists(self.audit_path):
                with open(self.audit_path, "r", encoding="utf-8") as fh:
                    seq = sum(1 for line in fh if line.strip()) + 1
            line = {"seq": seq, "backend": receipt["backend"], "model": receipt["model"],
                    "prompt_sha16": _sha16(task), "response_sha16": _sha16(output),
                    "latency_ms": receipt["latency_ms"],
                    "tokens": receipt["tokens"]}
            with open(self.audit_path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(line, ensure_ascii=False) + "\n")
            return {"ok": True, "seq": seq, "path": self.audit_path}
        except OSError as exc:          # 审计写失败不影响回执
            return {"ok": False, "error": str(exc), "seq": None}
