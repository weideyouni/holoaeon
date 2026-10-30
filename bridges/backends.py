# -*- coding: utf-8 -*-
"""
Host bridge · backends —— 后端声明与载荷构造
================================================================================
三种后端：
  · OLLAMA        —— 本机 127.0.0.1:11434，无需 key，POST /api/chat
  · OPENAI_COMPAT —— OpenAI 兼容端点（llamafile / LM Studio / vLLM / 云端），
                     POST /v1/chat/completions，key 从环境变量读取
  · ECHO          —— 离线自检后端：不发网络请求，原样回显。用于验证桥的
                     装配逻辑本身（无模型机器也能跑通管线，但会明确标 mode="echo"）

地址策略（fail-closed）：
  · 默认只允许 127.0.0.1 / localhost / ::1；
  · 任何其他主机必须在构造阶段显式传 allow_remote=True，且主机名在白名单内；
  · 环境变量 HOLOAEON_ALLOW_REMOTE=1 只是"解锁开关"，不能替代白名单。

它保护了哪条立场：宿主边界 + 代价显式 —— 密钥只在内存中传给请求头，不落盘、不进审计。
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from urllib.parse import urlparse

LOCAL_HOSTS = ("127.0.0.1", "localhost", "::1")
KEY_ENV = "HOLOAEON_API_KEY"
REMOTE_ENV = "HOLOAEON_ALLOW_REMOTE"


def is_local(url: str) -> bool:
    if (urlparse(url).scheme or "").lower() == "echo":
        return True                          # 离线后端：根本不发请求
    host = (urlparse(url).hostname or "").lower()
    return host in LOCAL_HOSTS


def check_target(url: str, allow_remote: bool,
                 allowlist: Optional[List[str]] = None) -> Dict:
    """地址准入：默认只放行本机；远程需开关 + 白名单双确认。"""
    parsed = urlparse(url)
    if (parsed.scheme or "").lower() == "echo":
        return {"ok": True, "reason": "OFFLINE_BACKEND", "host": ""}
    host = (parsed.hostname or "").lower()
    if not host:
        return {"ok": False, "reason": "NO_HOST", "host": ""}
    if host in LOCAL_HOSTS:
        return {"ok": True, "reason": "LOCAL", "host": host}
    if os.environ.get(REMOTE_ENV) != "1":
        return {"ok": False, "reason": "REMOTE_LOCKED",
                "host": host,
                "hint": "远程主机需同时设置 %s=1 且提供 allowlist" % REMOTE_ENV}
    if not allow_remote:
        return {"ok": False, "reason": "REMOTE_NOT_CONFIRMED", "host": host,
                "hint": "构造客户端时需显式 allow_remote=True"}
    if not allowlist or host not in [h.lower() for h in allowlist]:
        return {"ok": False, "reason": "REMOTE_NOT_ALLOWLISTED", "host": host}
    return {"ok": True, "reason": "REMOTE_ALLOWED", "host": host}


@dataclass
class Backend:
    name: str                      # ollama | openai_compat | echo
    base_url: str
    needs_key: bool = False
    local_by_default: bool = True
    chat_path: str = ""
    tags_path: str = ""
    extra: Dict = field(default_factory=dict)

    def chat_url(self) -> str:
        return self.base_url.rstrip("/") + self.chat_path

    def tags_url(self) -> str:
        return self.base_url.rstrip("/") + self.tags_path if self.tags_path else ""

    def headers(self) -> Dict[str, str]:
        if not self.needs_key:
            return {}
        key = os.environ.get(KEY_ENV, "")
        return {"Authorization": "Bearer " + key} if key else {}

    def snapshot(self) -> Dict:
        return {"name": self.name, "base_url": self.base_url,
                "needs_key": self.needs_key,
                "key_present": bool(self.headers()),
                "local": is_local(self.base_url)}


DEFAULTS = {
    "ollama": Backend("ollama", "http://127.0.0.1:11434",
                      chat_path="/api/chat", tags_path="/api/tags"),
    "openai_compat": Backend("openai_compat", "http://127.0.0.1:8080",
                             needs_key=False, chat_path="/v1/chat/completions",
                             tags_path="/v1/models"),
    "echo": Backend("echo", "echo://local", chat_path="", tags_path=""),
}


def get_backend(name: str, base_url: Optional[str] = None) -> Backend:
    if name not in DEFAULTS:
        raise ValueError("未知后端：%s（可选 %s）" % (name, "/".join(sorted(DEFAULTS))))
    b = DEFAULTS[name]
    if base_url:
        b = Backend(b.name, base_url, b.needs_key, b.local_by_default,
                    b.chat_path, b.tags_path, dict(b.extra))
    return b


def build_payload(backend: Backend, messages: List[Dict], model: str,
                  temperature: float = 0.0) -> Dict:
    """把 openai_chat 形态的消息映射成各后端的载荷（确定性、无副作用）。"""
    if backend.name == "ollama":
        return {"model": model, "messages": messages, "stream": False,
                "options": {"temperature": temperature}}
    if backend.name == "openai_compat":
        return {"model": model, "messages": messages, "temperature": temperature,
                "stream": False}
    return {"model": model, "messages": messages}


def parse_response(backend: Backend, data: Dict) -> Dict:
    """从各后端回执里抽出 output 与 token 计数；字段缺失时返回 None 而不是猜 0。"""
    if backend.name == "ollama":
        msg = (data.get("message") or {})
        return {"output": msg.get("content"),
                "prompt_tokens": data.get("prompt_eval_count"),
                "completion_tokens": data.get("eval_count"),
                "model": data.get("model")}
    if backend.name == "openai_compat":
        choices = data.get("choices") or [{}]
        msg = (choices[0].get("message") or {})
        usage = data.get("usage") or {}
        return {"output": msg.get("content"),
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
                "model": data.get("model")}
    return {"output": str(data.get("echo", "")), "prompt_tokens": None,
            "completion_tokens": None, "model": "echo"}
