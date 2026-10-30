# -*- coding: utf-8 -*-
"""
Host bridge · quickstart —— 普通人五分钟路径
================================================================================
    python bridges/quickstart.py --check
    python bridges/quickstart.py --ask "用一句话解释什么是超向量"
    python bridges/quickstart.py --ask "..." --backend openai_compat --base-url http://127.0.0.1:8080

--check 无 Ollama 时打印三行指引并以退出码 2 结束（不抛 traceback）。
"""
from __future__ import annotations

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    from . import backends, transport, live_client    # 包内运行
except ImportError:
    import backends, transport, live_client           # 脚本方式运行

GUIDE = """未检测到本机 Ollama。
  1) 安装：https://ollama.com  （Windows 装完自动常驻 127.0.0.1:11434）
  2) 拉一个小模型：ollama pull qwen2.5:0.5b
  3) 再跑一次：python bridges/quickstart.py --check
也可以改用任意 OpenAI 兼容端点：--backend openai_compat --base-url http://127.0.0.1:8080"""


def do_check(backend_name: str, base_url: str) -> int:
    b = backends.get_backend(backend_name, base_url or None)
    if b.name == "echo":
        print("echo 后端常驻可用（不联网）")
        return 0
    url = b.tags_url()
    if not url:
        print("该后端没有探活路径：%s" % b.name)
        return 2
    res = transport.get_json(url, timeout=5.0, headers=b.headers())
    if not res.get("ok"):
        print(GUIDE)
        print("探测 %s → %s" % (url, res.get("error_type")))
        return 2
    data = res.get("data") or {}
    entries = data.get("models") or data.get("data") or []
    names = [e.get("name") or e.get("id") for e in entries if isinstance(e, dict)]
    print("可用模型（%d）：%s" % (len(names), ", ".join(n for n in names if n) or "（空）"))
    return 0 if names else 2


def do_ask(args) -> int:
    client = live_client.LiveModelClient(
        backend_name=args.backend, base_url=args.base_url or None,
        model=args.model, allow_remote=args.allow_remote,
        allowlist=(args.allowlist.split(",") if args.allowlist else None))
    r = client.ask(args.ask)
    if not r.get("ok", True):
        print("调用失败：%s status=%s" % (r.get("error_type"), r.get("status")))
        print("detail:", (r.get("detail") or "")[:300])
        print("回执：mode=%s backend=%s latency=%.1f ms"
              % (r.get("mode"), r.get("backend"), r.get("latency_ms", 0)))
        return 2
    print("mode    :", r["mode"])
    print("backend :", r["backend"])
    print("model   :", r["model"])
    print("tokens  :", r["tokens"])
    print("latency : %.1f ms" % r["latency_ms"])
    print("output  :", (r["output"] or "")[:400])
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="HoloAeon 宿主模型桥 quickstart")
    ap.add_argument("--check", action="store_true", help="探活并列出可用模型")
    ap.add_argument("--ask", default="", help="发一个问题")
    ap.add_argument("--backend", default="ollama",
                    choices=["ollama", "openai_compat", "echo"])
    ap.add_argument("--base-url", default="")
    ap.add_argument("--model", default="qwen2.5:0.5b")
    ap.add_argument("--allow-remote", action="store_true")
    ap.add_argument("--allowlist", default="")
    args = ap.parse_args()
    if args.check:
        return do_check(args.backend, args.base_url)
    if args.ask:
        return do_ask(args)
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
