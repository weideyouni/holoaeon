# -*- coding: utf-8 -*-
"""
mcp_adapter —— Model Context Protocol (MCP) stdio 桥接适配器（V12.1 · 未决项闭环；V50 双版本）
================================================================================
把 HoloAeon 确定性管家引擎暴露为 MCP 服务器（stdio 传输，JSON-RPC 2.0 信封），
使任意 MCP 客户端（Claude Desktop / 豆包 / Cursor 等）可将管家引擎作为工具调用。

实现双版本协议子集（MCP **2024-11-05 与 2026-07-28 双规范**，V50 升级）：
  · initialize        —— 握手（legacy 兼容分支，protocolVersion / capabilities / serverInfo）
  · server/discover   —— 无状态能力发现（2026-07-28 新 RPC，客户端可选用，非必需）
  · ping              —— 心跳
  · tools/list        —— 暴露 3 个管家工具（task 通用提交 / status 状态快照 / quartet 四人组涌现）
  · tools/call        —— 转译参数 → frontend_adapter.handle_request（或直达便捷工具）→ JSON-RPC result
  · notifications/*   —— 通知帧静默吞掉（不回响应，JSON-RPC 通知语义）

V50 双版本依据（2026-11-09 官方核实：modelcontextprotocol.io SEP-2575）：
  · 2026-07-28 规范转无状态核心：initialize/initialized 握手移除（SEP-2575）、
    Mcp-Session-Id 移除（SEP-2567）、clientInfo/protocolVersion 走每请求 _meta、
    新增 server/discover RPC；治理已移交 Linux Foundation 旗下 AAIF。
  · 官方双版本路径（SEP-2575 原文）："a server that wishes to support both old and
    new clients MAY do so — continue to implement the old initialize RPC to handle
    legacy clients, while also exposing the new stateless RPCs for updated clients."
  · 本实现本就逐行独立处理（无会话状态、无 session ID、`session` 字面量 0 次），
    与新规范方向同构；V50 显式化：无握手直通 + server/discover + 通知帧静默。
  · stdio 传输选型在新规范下依然正确（离线兼容，不破坏零网络特性）。
  · _meta 中的 clientInfo 为纯登记信息，本实现不依赖、不解析（每请求自包含）。

零依赖（纯标准库）、无网络、无 GPU；与 V12 butler_os 同构——同一契约，不同运输层
（butler=本地菜单 / mcp=标准协议）。工程维度纪律不变（25/47/9，EXTRA_PACK_ORDER 不变）。
"""
from __future__ import annotations

import json
import sys

from .frontend_adapter import build_kernel, handle_request
from .spec import VERSION, RUNTIME_ID, MODE_SIMULATED, DOC_VERSION

# legacy 协商应答值（2024-11-05 客户端 initialize 握手用）
PROTOCOL_VERSION = "2024-11-05"
# 双版本支持声明（server/discover 返回；2026-07-28 为无状态规范）
SUPPORTED_PROTOCOL_VERSIONS = ("2024-11-05", "2026-07-28")
SERVER_NAME = "holoaeon-mcp"

TOOL_SCHEMA = {
    "holoaeon.task": {
        "description": "向 HoloAeon 确定性管家引擎提交一个任务。task=任务文本，to=目标领域包 key（省略=全域），args=附加参数，permission=权限位（默认 0）。返回 status/all_ok/results/receipt。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "任务文本（必填）"},
                "to": {"type": ["string", "null"], "description": "目标领域包 key，省略表示全域"},
                "args": {"type": "object", "description": "附加参数（可选）"},
                "permission": {"type": "integer", "description": "权限位，默认 0"},
            },
            "required": ["task"],
        },
    },
    "holoaeon.status": {
        "description": "管家引擎状态快照：runtime_id / VERSION / DOC_VERSION / agents / skills / guard_layers / submitted / blocked / memory。",
        "inputSchema": {"type": "object", "properties": {}},
    },
    "holoaeon.quartet": {
        "description": "四人组涌现检查：P2×P3≥0.7 ∧ P1≥0.6 ∧ P4≤0.4 ∧ order>0.30 → emergence=True。示例 (0.85,0.85,0.85,0.30) → order≈0.5237。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "p1": {"type": "number", "description": "P1 视野分 0-1"},
                "p2": {"type": "number", "description": "P2 构弦分 0-1"},
                "p3": {"type": "number", "description": "P3 持衡分 0-1"},
                "p4": {"type": "number", "description": "P4 筑基分 0-1"},
            },
            "required": ["p1", "p2", "p3", "p4"],
        },
    },
}


def _dispatch(method: str, params: dict) -> dict:
    """MCP 工具调用分派：task 走 handle_request（同一契约），status/quartet 为便捷直算。"""
    if method == "holoaeon.task":
        return handle_request({
            "task": params.get("task", ""),
            "to": params.get("to"),
            "args": params.get("args") or {},
            "permission": int(params.get("permission", 0)),
        })
    if method == "holoaeon.status":
        kernel = build_kernel()
        snap = kernel.snapshot()
        return {
            "status": "ok",
            "all_ok": True,
            "receipt": {
                "runtime_id": snap["runtime_id"],
                "version": VERSION,
                "doc_version": DOC_VERSION,
                "mode": MODE_SIMULATED,
                "agents": len(snap["agents"]),
                "skills": len(snap["skills"]),
                "guard_layers": 8,
                "submitted": snap["submitted"],
                "blocked": snap["blocked"],
                "memory": snap["memory"],
            },
        }
    if method == "holoaeon.quartet":
        from .packs.quartet_director_pack import check_emergence
        r = check_emergence(
            float(params["p1"]), float(params["p2"]),
            float(params["p3"]), float(params["p4"]),
        )
        return {"status": "ok", "all_ok": bool(r["emergence"]),
                "results": [r],
                "receipt": {"check": "quartet_director.check_emergence"}}
    return {"status": "error", "error": "unknown_tool", "detail": method}


def _handle_line(raw: str):
    """单行 JSON-RPC 2.0 请求 → 响应 dict；通知帧（无 id）返回 None（不写响应）。"""
    try:
        msg = json.loads(raw)
    except ValueError:
        return {"jsonrpc": "2.0", "id": None,
                "error": {"code": -32700, "message": "Parse error"}}
    if not isinstance(msg, dict):
        return {"jsonrpc": "2.0", "id": None,
                "error": {"code": -32600, "message": "Invalid Request"}}
    method = msg.get("method")
    msg_id = msg.get("id")
    params = msg.get("params") or {}

    # JSON-RPC 通知帧（无 id）：静默吞掉，不回响应（含旧客户端 initialized 通知）
    if msg_id is None and isinstance(method, str):
        return None

    if method == "initialize":
        # legacy 兼容分支（2024-11-05 客户端握手；SEP-2575 官方双版本路径 MAY 保留）
        return {"jsonrpc": "2.0", "id": msg_id, "result": {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": SERVER_NAME, "version": VERSION},
        }}
    if method == "server/discover":
        # 2026-07-28 无状态规范新 RPC：能力发现（客户端可选用，非必需）
        return {"jsonrpc": "2.0", "id": msg_id, "result": {
            "protocolVersions": list(SUPPORTED_PROTOCOL_VERSIONS),
            "capabilities": {"tools": {}},
            "serverInfo": {"name": SERVER_NAME, "version": VERSION},
            "stateless": True,
        }}
    if method == "ping":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {}}
    if method == "tools/list":
        tools = [{"name": n, "description": s["description"],
                  "inputSchema": s["inputSchema"]}
                 for n, s in TOOL_SCHEMA.items()]
        return {"jsonrpc": "2.0", "id": msg_id,
                "result": {"tools": tools}}
    if method == "tools/call":
        name = params.get("name")
        if name not in TOOL_SCHEMA:
            return {"jsonrpc": "2.0", "id": msg_id,
                    "error": {"code": -32602,
                              "message": "Unknown tool: %s" % name}}
        try:
            payload = _dispatch(name, params.get("arguments") or {})
        except Exception as exc:  # fail-loud：工具异常 → JSON-RPC error
            return {"jsonrpc": "2.0", "id": msg_id,
                    "error": {"code": -32603, "message": str(exc)}}
        return {"jsonrpc": "2.0", "id": msg_id, "result": {
            "content": [{"type": "text",
                         "text": json.dumps(payload, ensure_ascii=False)}],
            "isError": False,
        }}
    return {"jsonrpc": "2.0", "id": msg_id,
            "error": {"code": -32601,
                      "message": "Method not found: %s" % method}}


def main(argv=None) -> int:
    """stdio 传输：逐行读 stdin（每行一个 JSON-RPC 请求），逐行写 stdout。
    通知帧（无 id）不产生输出行（JSON-RPC 通知语义）。"""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        resp = _handle_line(line)
        if resp is None:
            continue
        sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
        sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
