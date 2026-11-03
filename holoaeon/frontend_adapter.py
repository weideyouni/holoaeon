# -*- coding: utf-8 -*-
"""
frontend_adapter —— 大模型对话界面 ↔ holoaeon kernel 桥接适配器（批3 · 产品层）
================================================================================
职责：把任意对话前端（豆包/WorkBuddy/千问/元宝，或任何能执行本进程的终端）
变成 holoaeon 的驱动界面：

  stdin 一行 JSON  →  {"task": "...", "to": "...", "args": {...}, "metadata": {...}, "permission": 0}
  stdout 一行 JSON →  {"status": "...", "results": [...], "all_ok": true/false, "receipt": {...}}

特性：
  · 零依赖（纯标准库）、无网络、无 GPU —— 老机器可跑
  · 启动即自动装配：九大领域包 + 全部扩展包（含 L9 挂载后的 fusion_upgrade）
  · 确定性：同一输入 → 同一输出结构（receipt 含 runtime_id）
  · L9 路径闸门默认开启：前端可携带 path_requested / allowed_paths / path_mode，
    写操作必须带 path_write_authorized=True，否则被守卫拦截（防"千问乱动源码"类事故）

用法：
  echo '{"task":"hello","to":"*"}' | python -m holoaeon.frontend_adapter
  python -m holoaeon.frontend_adapter < req.json > resp.json
"""
from __future__ import annotations

import json
import sys

from .kernel import Kernel
from .packs import PACK_ORDER, EXTRA_PACK_ORDER, get_pack, get_extra_pack
from .spec import VERSION, RUNTIME_ID, MODE_SIMULATED


def build_kernel() -> Kernel:
    """一次性装配内核：九大领域包 + 全部扩展包。不复用、不污染外部状态。"""
    k = Kernel()
    for key in PACK_ORDER:
        get_pack(key).install(k)
    for key in EXTRA_PACK_ORDER:
        get_extra_pack(key).install(k)
    return k


def handle_request(req: dict) -> dict:
    task = str(req.get("task", ""))
    to = req.get("to")
    args = req.get("args") or {}
    metadata = req.get("metadata") or {}
    permission = int(req.get("permission", 0))
    if not task:
        return {"status": "error", "error": "missing_task",
                "hint": "请求必须含 task 字段"}

    # 产品层路径闸门：把 args 中以 path_ 开头的字段提升进 metadata，
    # 使对话界面（豆包/千问/元宝）传来的路径请求真实经过 L9（写必须显式授权）
    path_fields = {k: v for k, v in (args or {}).items()
                   if k.startswith("path_")}
    metadata = {**(metadata or {}), **path_fields}

    kernel = build_kernel()
    try:
        result = kernel.submit(
            task, to,
            args=args,
            metadata=metadata,
            permission=permission,
        )
    except Exception as exc:  # fail-loud：答不出的明确报错
        return {"status": "error", "error": type(exc).__name__,
                "detail": str(exc),
                "runtime_id": RUNTIME_ID, "version": VERSION,
                "mode": MODE_SIMULATED}
    return {
        "status": result.get("status", "ok"),
        "all_ok": bool(result.get("all_ok", True)),
        "results": result.get("results", []),
        "targets": result.get("targets", []),
        "hint": result.get("hint"),
        "receipt": {
            "runtime_id": RUNTIME_ID,
            "version": VERSION,
            "mode": MODE_SIMULATED,
            "agents": len(kernel.agents),
            "skills": len(kernel.skills.names()),
            "submitted": kernel.submitted,
        },
    }


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    # 支持命令行直呼（demo 友好）：python -m holoaeon.frontend_adapter "任务文本"
    if len(argv) >= 1 and not argv[0].lstrip().startswith("{"):
        req = {"task": " ".join(argv), "to": None}
    else:
        raw = sys.stdin.read() if not argv else argv[0]
        try:
            req = json.loads(raw)
        except ValueError as exc:
            print(json.dumps({"status": "error", "error": "invalid_json",
                              "detail": str(exc)}, ensure_ascii=False))
            return 1
    resp = handle_request(req)
    print(json.dumps(resp, ensure_ascii=False, indent=None))
    return 0 if resp.get("status") != "error" else 2


if __name__ == "__main__":
    sys.exit(main())
