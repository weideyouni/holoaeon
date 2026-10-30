# -*- coding: utf-8 -*-
"""
Host bridge · transport —— 最小的 JSON over HTTP 传输层
================================================================================
唯一职责：把 dict 发出去、把 dict 收回来。所有异常在这里被转成结构化结果，
调用方永远不需要 try/except 网络错误。

不做什么：
  · 不做重试风暴（最多一次由调用方决定）
  · 不做重定向跟随（urllib 默认行为交给它自己）
  · 不写日志（审计在 live_client 里，只记哈希）
  · 不读取除 HOLOAEON_API_KEY 之外的任何环境变量（密钥读取在 backends）

它保护了哪条立场：宿主边界 —— 网络只存在于 bridges/，核心包 holoaeon/ 永不 import 本模块。
"""
from __future__ import annotations

import json
import socket
import urllib.error
import urllib.request

DEFAULT_TIMEOUT = 120.0


def post_json(url: str, payload: dict, timeout: float = DEFAULT_TIMEOUT,
              headers: dict = None) -> dict:
    """POST JSON，返回 {"ok": bool, ...}；永不抛出网络异常。"""
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            code = getattr(resp, "status", 200)
    except urllib.error.HTTPError as exc:            # 服务端返回非 200
        detail = ""
        try:
            detail = exc.read().decode("utf-8", "replace")[:400]
        except Exception:                             # noqa: BLE001
            pass
        return {"ok": False, "error_type": "http_error", "status": exc.code,
                "detail": detail or str(exc)}
    except urllib.error.URLError as exc:              # 连接失败 / DNS / 拒绝
        r = getattr(exc, "reason", exc)
        kind = "timeout" if isinstance(r, (socket.timeout, TimeoutError)) else "connect"
        return {"ok": False, "error_type": kind, "status": None, "detail": str(r)}
    except (ValueError, OSError) as exc:
        kind = "timeout" if isinstance(exc, (socket.timeout, TimeoutError)) else "connect"
        return {"ok": False, "error_type": kind, "status": None, "detail": str(exc)}

    try:
        data = json.loads(raw.decode("utf-8", "replace"))
    except ValueError:
        return {"ok": False, "error_type": "bad_json", "status": code,
                "detail": raw[:200].decode("utf-8", "replace")}
    if code != 200:
        return {"ok": False, "error_type": "http_error", "status": code,
                "detail": str(data)[:400]}
    return {"ok": True, "status": code, "data": data,
            "bytes": len(raw)}


def get_json(url: str, timeout: float = 5.0, headers: dict = None) -> dict:
    """GET JSON（仅用于本机探活，如 Ollama /api/tags）。"""
    req = urllib.request.Request(url, method="GET")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            code = getattr(resp, "status", 200)
    except urllib.error.HTTPError as exc:
        return {"ok": False, "error_type": "http_error", "status": exc.code,
                "detail": str(exc)[:200]}
    except urllib.error.URLError as exc:
        r = getattr(exc, "reason", exc)
        kind = "timeout" if isinstance(r, (socket.timeout, TimeoutError)) else "connect"
        return {"ok": False, "error_type": kind, "status": None, "detail": str(r)}
    except (ValueError, OSError) as exc:
        return {"ok": False, "error_type": "connect", "status": None, "detail": str(exc)}
    try:
        data = json.loads(raw.decode("utf-8", "replace"))
    except ValueError:
        return {"ok": False, "error_type": "bad_json", "status": code, "detail": ""}
    return {"ok": code == 200, "status": code, "data": data}
