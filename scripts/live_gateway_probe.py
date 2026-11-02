# -*- coding: utf-8 -*-
"""V4.5-B1 真实调用探针（scripts 层，允许联网；holoaeon 包内红线不变）。

原则
----
1. **只打本机回环**：host 必须是 127.0.0.1 / localhost / ::1，否则直接拒绝（防止误把凭证打到公网）。
2. **只打 OpenAI Chat 形状**：path 固定 `/chat/completions`，body 与 `model_gateway.plan("lmstudio")` 同形。
3. **不写 key**：本地运行时无需 key；若用户给了，也不落盘（只记 `key_present` 布尔）。
4. **回执诚实**：`evidence_class="live_local"`（不是 simulated），并记录真实 status / 耗时 / usage。

用法
----
```
python scripts/live_gateway_probe.py --model <LM Studio 里的模型 id>
python scripts/live_gateway_probe.py --model <id> --base http://127.0.0.1:1234/v1 --prompt "ping"
```
输出：`reports/v45_live_probe.json`
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from holoaeon.fusion_upgrade.model_gateway import (  # noqa: E402
    PROTOCOL_SHAPES, ProviderSpec, load_catalog,
)

REPORT = os.path.join(ROOT, "reports", "v45_live_probe.json")
LOOPBACK = {"127.0.0.1", "localhost", "::1", "0.0.0.0"}


def local_only(base: str) -> None:
    u = urllib.parse.urlparse(base)
    if u.scheme not in ("http", "https"):
        raise SystemExit("拒绝：只允许 http/https")
    if (u.hostname or "") not in LOOPBACK:
        raise SystemExit("拒绝：只允许本机回环地址，得到 host=%s" % (u.hostname,))


def pick_spec(catalog: Dict[str, Any], pid: str) -> ProviderSpec:
    for p in catalog["providers"]:
        if p["id"] == pid:
            return ProviderSpec.from_dict(p)
    raise SystemExit("目录里没有 %s" % pid)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, help="本地运行时里的模型 id（如 qwen2.5-0.5b-instruct）")
    ap.add_argument("--provider", default="lmstudio", help="目录里的本地 provider id，默认 lmstudio")
    ap.add_argument("--base", default="", help="覆盖 BASE_URL；缺省取目录默认值")
    ap.add_argument("--mode", choices=("chat", "embeddings"), default="chat",
                    help="chat=/chat/completions；embeddings=/embeddings（对话模型未就绪时用它验连通）")
    ap.add_argument("--prompt", default="用一句中文回答：HoloAeon 的这一条本地请求是否走通？")
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--out", default=REPORT)
    a = ap.parse_args()

    cat = load_catalog(ROOT)
    spec = pick_spec(cat, a.provider)
    base = (a.base or spec.default_base_url or "http://127.0.0.1:1234/v1").rstrip("/")
    local_only(base)

    if a.mode == "chat":
        url = base + "/chat/completions"
        body = {"model": a.model, "stream": False, "temperature": 0.2,
                "max_tokens": 64,
                "messages": [{"role": "user", "content": a.prompt}]}
    else:
        url = base + "/embeddings"
        body = {"model": a.model, "input": a.prompt}
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST",
                                 headers={"Content-Type": "application/json"})

    t0 = time.time()
    status, raw, err = 0, b"", ""
    try:
        with urllib.request.urlopen(req, timeout=a.timeout) as resp:
            status = resp.status
            raw = resp.read()
    except urllib.error.HTTPError as exc:
        status = exc.code
        raw = exc.read() if exc.fp else b""
        err = "HTTPError"
    except Exception as exc:                      # 连接类失败：如实记录，不伪造
        err = type(exc).__name__ + ": " + str(exc)[:120]
    ms = int((time.time() - t0) * 1000)

    parsed: Dict[str, Any] = {}
    try:
        parsed = json.loads(raw.decode("utf-8")) if raw else {}
    except Exception:
        parsed = {}

    choice = (parsed.get("choices") or [{}])[0]
    text = (choice.get("message") or {}).get("content") or ""
    usage = parsed.get("usage") or {}
    emb = (parsed.get("data") or [{}])[0]
    dim = len(emb.get("embedding") or []) if isinstance(emb, dict) else 0

    out = {
        "id": "SG-V45-LIVE-PROBE-V1",
        "batch": "V4.5-B1",
        "created_at": "2026-11-02",
        "evidence_class": "live_local",
        "network": True,
        "mode": a.mode,
        "host_scope": "loopback_only",
        "provider": spec.id,
        "api_style": spec.api_style,
        "protocol": PROTOCOL_SHAPES.get(spec.api_style, ""),
        "request": {"method": "POST", "url": url, "body_keys": sorted(body),
                    "body_sha256": hashlib.sha256(data).hexdigest(),
                    "key_present": bool(os.environ.get(spec.key_env, "").strip()),
                    "model": a.model},
        "response": {"status": status, "latency_ms": ms,
                     "raw_bytes": len(raw), "raw_sha256": hashlib.sha256(raw).hexdigest(),
                     "error": err,
                     "choices": len(parsed.get("choices") or []),
                     "embedding_dim": dim,
                     "text": text[:400],
                     "usage": {"prompt_tokens": usage.get("prompt_tokens"),
                               "completion_tokens": usage.get("completion_tokens"),
                               "total_tokens": usage.get("total_tokens")}},
        "verdict": "PASS" if status == 200 and (bool(text) or dim > 0) else "FAIL",
        "note": "真实本地回环调用：零成本、不出网；形状与 model_gateway.plan 同源。",
    }
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(json.dumps({"verdict": out["verdict"], "mode": a.mode, "status": status, "ms": ms,
                      "text_head": text[:80], "embedding_dim": dim, "usage": out["response"]["usage"]},
                     ensure_ascii=False))
    return 0 if out["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
