# -*- coding: utf-8 -*-
"""
protocol_plugins —— 插件化协议适配器
================================================================================
遍历穷举所有平台型适配协议，让 HoloAeon 技能可被任意平台调用。

支持协议（12 种）：
  OpenAI Function Calling / Anthropic Tool Use / Google Gemini Function Call
  MCP / A2A / ACP / LangChain Tool / LlamaIndex Tool / AutoGen Tool
  CrewAI Tool / Bedrock Converse / HoloAeon Envelope (native)

设计：PROTOCOL_REGISTRY 声明式注册；export_skill_to_protocol(skill_spec, proto)
将 SkillSpec 转译为目标协议 JSON；export_all_protocols 遍历穷举全量导出。

V14-SKILL-LATHE-PROTOCOL-PLUGINS · 纯标准库、零依赖、确定性、离线。
"""
from __future__ import annotations

import json
import sys
from typing import Any, Dict, List


# ------------------------------------------------------------ 协议注册表
PROTOCOL_REGISTRY: Dict[str, dict] = {
    "openai_function": {
        "name": "OpenAI Function Calling",
        "format": {"type": "function",
                   "function": {"name": "...", "description": "...",
                                "parameters": {"type": "object", "properties": {}}}},
        "direction": "outbound",
    },
    "anthropic_tool": {
        "name": "Anthropic Tool Use",
        "format": {"name": "...", "description": "...",
                   "input_schema": {"type": "object", "properties": {}}},
        "direction": "outbound",
    },
    "gemini_function": {
        "name": "Google Gemini Function Call",
        "format": {"name": "...", "description": "...",
                   "parameters": {"type": "object", "properties": {}}},
        "direction": "outbound",
    },
    "mcp": {
        "name": "Model Context Protocol",
        "format": {"tool": {"name": "...", "description": "...",
                            "inputSchema": {"type": "object", "properties": {}}}},
        "direction": "bidirectional",
    },
    "a2a": {
        "name": "Agent-to-Agent Protocol",
        "format": {"from": "...", "to": "...", "task": "...", "args": {}},
        "direction": "bidirectional",
    },
    "acp": {
        "name": "Agent Communication Protocol",
        "format": {"sender": "...", "recipient": "...", "message": {}},
        "direction": "bidirectional",
    },
    "langchain_tool": {"name": "LangChain Tool",
                        "format": {"name": "...", "func": "..."}},
    "llamaindex_tool": {"name": "LlamaIndex Tool",
                         "format": {"name": "...", "fn": "..."}},
    "autogen_tool": {"name": "AutoGen Tool",
                      "format": {"name": "...", "func": "..."}},
    "crewai_tool": {"name": "CrewAI Tool",
                     "format": {"name": "...", "func": "..."}},
    "bedrock_converse": {"name": "AWS Bedrock Converse",
                          "format": {"tool": {"name": "...",
                                              "inputSchema": {}}}},
    "envelope": {"name": "HoloAeon Envelope (native)",
                 "format": {"sender": "...", "topic": "...",
                            "recipient": "...", "payload": {}}},
}


def list_protocols() -> List[str]:
    """列出所有支持协议 key。"""
    return list(PROTOCOL_REGISTRY.keys())


def protocol_names() -> Dict[str, str]:
    """协议 key → 展示名。"""
    return {k: v.get("name", k) for k, v in PROTOCOL_REGISTRY.items()}


# ------------------------------------------------------------ 导出核心
def export_skill_to_protocol(skill_spec: dict, protocol: str) -> dict:
    """把一个 SkillSpec 导出为指定协议的 JSON 格式。"""
    if protocol not in PROTOCOL_REGISTRY:
        raise ValueError(
            "未知协议: %s，可选: %s" % (protocol, list(PROTOCOL_REGISTRY.keys()))
        )
    name = str(skill_spec.get("name") or "unknown")
    desc = str(skill_spec.get("description") or "")
    inputs = skill_spec.get("inputs") or {}
    props = {}
    for k, v in inputs.items():
        props[k] = {"type": "string", "description": str(v)}

    if protocol == "openai_function":
        return {"type": "function",
                "function": {"name": name, "description": desc,
                             "parameters": {"type": "object",
                                            "properties": props}}}
    if protocol == "anthropic_tool":
        return {"name": name, "description": desc,
                "input_schema": {"type": "object", "properties": props}}
    if protocol == "gemini_function":
        return {"name": name, "description": desc,
                "parameters": {"type": "object", "properties": props}}
    if protocol == "mcp":
        return {"tool": {"name": name, "description": desc,
                         "inputSchema": {"type": "object",
                                         "properties": props}}}
    if protocol == "a2a":
        return {"from": "holoaeon", "to": "*", "task": desc, "args": inputs}
    if protocol == "acp":
        return {"sender": "holoaeon", "recipient": "*",
                "message": {"task": desc, "inputs": inputs}}
    if protocol == "envelope":
        return {"sender": "holoaeon", "topic": name, "recipient": "*",
                "payload": {"description": desc, "inputs": inputs}}
    # langchain/llamaindex/autogen/crewai/bedrock：通用 callable 格式
    return {"name": name, "description": desc,
            "func": "callable", "inputs": inputs}


def export_all_protocols(skill_spec: dict) -> Dict[str, dict]:
    """遍历穷举：把一个 SkillSpec 导出为所有协议格式。"""
    return {proto: export_skill_to_protocol(skill_spec, proto)
            for proto in PROTOCOL_REGISTRY}


# ------------------------------------------------------------ 自检
def selfcheck() -> dict:
    """适配器自检：12 协议数、穷举导出覆盖、错误分支。"""
    spec = {"name": "salvaged_test_0001", "description": "demo",
            "inputs": {"query": "str"}}
    protos = list_protocols()
    exports = export_all_protocols(spec)
    unknown_raises = False
    try:
        export_skill_to_protocol(spec, "no_such_protocol")
    except ValueError:
        unknown_raises = True
    ok = (len(protos) == 12 and len(exports) == 12
          and set(protos) == set(PROTOCOL_REGISTRY) and unknown_raises)
    return {"ok": ok, "protocol_count": len(protos),
            "exported": list(exports.keys()), "unknown_raises": unknown_raises}


def main(argv=None) -> int:
    """CLI 入口（演示）：协议清单 + 一个示例导出的遍历穷举。"""
    args = list(sys.argv[1:] if argv is None else argv)
    if args and args[0].strip() == "--selfcheck":
        print("== 协议适配器自检 ==")
        print(json.dumps(selfcheck(), ensure_ascii=False, indent=2))
        return 0 if selfcheck()["ok"] else 1
    print("== HoloAeon 插件化协议适配器（12 协议遍历穷举）==")
    print("协议:", list_protocols())
    spec = {"name": "salvaged_test_0001", "description": "demo",
            "inputs": {"query": "str"}}
    exports = export_all_protocols(spec)
    print("穷举导出协议数:", len(exports))
    for proto, payload in exports.items():
        print("  %s → %s" % (proto, json.dumps(payload, ensure_ascii=False)[:80]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
