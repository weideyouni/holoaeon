# -*- coding: utf-8 -*-
"""
gap_adapters —— 12 协议缺口逐条落地（V64 · 挂账清零批）
================================================================================
挂账原文（V63 回执 protocols）：在册 12（a2a / acp / anthropic_tool /
autogen_tool / bedrock_converse / crewai_tool / envelope / gemini_function /
langchain_tool / llamaindex_tool / mcp / openai_function），
缺口 12：dify / coze / qwen / doubao / wenxin / zhipu / xfyun / volcengine /
          openai-compatible-generic / ollama / n8n / dify-workflow。

本批结果（V66 收口后 **12 adapted + 0 gap**，V64 时点为 11 adapted + 1 gap）：
  · 7 条凭本地向量海素材 100_model_provider_catalog.json 直接落地
    （qwen / doubao / volcengine〔同源别名〕/ wenxin / zhipu / ollama /
     openai-compatible-generic）；
  · 4 条凭官方文档落地（xfyun / dify / coze / n8n）——文档 URL 逐条登记在
    evidence 里，抓取时点 2026-11-12；全部标 schema_verified=False（未联网握手）；
  · 1 条（dify-workflow）由 V66 补齐：V64 时 docs.dify.ai 的 workflow API 页
    与 openapi spec 均取回失败，故如实留 gap；V66 改为直读 Dify 主仓源码
    api/controllers/service_api/app/workflow.py，拿到端点 /workflows/run、
    请求体 {inputs, response_mode, user}、响应模型与错误码，证据等级
    source_code_read。缺口清零，**不是**靠推断补的。

关键区分（这是本批的口径要点）：
  · 「模型形状」5 种（provider 目录原文）：openai_chat / anthropic_messages /
    google_gemini / bedrock_converse / azure_openai；
  · 「平台形状」4 种（工作台/工作流自有，与模型形状不同族）：
    dify_chat / dify_workflow / coze_chat / n8n_api。
  所以 xfyun 属模型形状（OpenAI 兼容），dify/coze/n8n 属平台形状——
  不能把工作台硬塞进 openai_chat 就算「适配了」。

零网络纪律：本模块不联网、不校验可用性；启用规则同 provider 目录
（HOLOAEON_REAL_MODELS=1 + 各平台 key_env 有值，默认全 disabled）。
"""
from __future__ import annotations

import io
import json
import os
from typing import Any, Dict, List, Optional

SEAL = "潮起开门，潮落闭嘴"
SCHEMA_VERSION = "PROTOCOL-GAP-ADAPTERS-v1.0"
DATA_OUT_NAME = "protocol_gap_adapters.json"
FETCHED_AT = "2026-11-12"

# 模型形状 5 种（provider 目录 protocols 段原文）
MODEL_SHAPES: tuple = (
    {"id": "openai_chat", "label": "OpenAI Chat Completions", "shape": "messages[] + model"},
    {"id": "anthropic_messages", "label": "Anthropic Messages", "shape": "system + messages[] + max_tokens"},
    {"id": "google_gemini", "label": "Google Gemini generateContent", "shape": "contents[] + generationConfig"},
    {"id": "bedrock_converse", "label": "AWS Bedrock Converse", "shape": "messages[] + inferenceConfig"},
    {"id": "azure_openai", "label": "Azure OpenAI (deployment)", "shape": "deployment 替代 model + api-version"},
)

# 平台形状 4 种（工作台/工作流自有形状，本批按官方文档/源码登记）
PLATFORM_SHAPES: tuple = (
    {"id": "dify_chat", "label": "Dify 对话应用", "shape": "inputs + query + response_mode + conversation_id + user"},
    {"id": "dify_workflow", "label": "Dify 工作流编排",
     "shape": "inputs + response_mode(省略=blocking) + user → /workflows/run"},
    {"id": "coze_chat", "label": "Coze 发起对话 V3", "shape": "bot_id + user_id + stream + additional_messages[]"},
    {"id": "n8n_api", "label": "n8n Public REST API", "shape": "X-N8N-API-KEY + /api/v1 资源端点"},
)

ALL_SHAPES = tuple(list(MODEL_SHAPES) + list(PLATFORM_SHAPES))

# 12 缺口逐条（provider_id = 向量海 provider 目录中的真实条目；None = 目录没有）
GAPS: tuple = (
    {
        "id": "qwen", "label": "阿里通义千问", "kind": "大模型", "provider_id": "qwen",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "base_url_env": "HOLOAEON_QWEN_BASE_URL", "key_env": "HOLOAEON_QWEN_API_KEY",
        "models": ["qwen-max", "qwen-plus", "qwen-turbo"], "status": "adapted", "shape": "openai_chat",
        "evidence": "provider 目录 qwen 条：DashScope 兼容模式即 OpenAI 形状",
        "source_url": "vector-sea/holoaeon-v4-cold-hot-plug/100_model_provider_catalog.json",
    },
    {
        "id": "doubao", "label": "火山方舟 豆包", "kind": "大模型", "provider_id": "doubao",
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "base_url_env": "HOLOAEON_DOUBAO_BASE_URL", "key_env": "HOLOAEON_DOUBAO_API_KEY",
        "models": ["doubao-pro", "doubao-lite", "<endpoint id>"], "status": "adapted", "shape": "openai_chat",
        "evidence": "provider 目录 doubao 条：方舟 v3 即 OpenAI 兼容端点",
        "source_url": "vector-sea/holoaeon-v4-cold-hot-plug/100_model_provider_catalog.json",
    },
    {
        "id": "volcengine", "label": "火山引擎方舟（同源别名）", "kind": "大模型",
        "provider_id": "doubao", "alias_of": "doubao",
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "base_url_env": "HOLOAEON_DOUBAO_BASE_URL", "key_env": "HOLOAEON_DOUBAO_API_KEY",
        "models": ["<endpoint id>"], "status": "adapted", "shape": "openai_chat",
        "evidence": "volcengine 与 doubao 同属火山方舟同一端点族，复用 doubao 条目（别名登记，不另造凭据变量）",
        "source_url": "vector-sea/holoaeon-v4-cold-hot-plug/100_model_provider_catalog.json",
    },
    {
        "id": "wenxin", "label": "百度文心千帆", "kind": "大模型", "provider_id": "baidu_qianfan",
        "base_url": "https://qianfan.baidubce.com/v2",
        "base_url_env": "HOLOAEON_QIANFAN_BASE_URL", "key_env": "HOLOAEON_QIANFAN_API_KEY",
        "models": ["ernie", "ernie-speed"], "status": "adapted", "shape": "openai_chat",
        "evidence": "provider 目录 baidu_qianfan 条：v2 提供 OpenAI 兼容",
        "source_url": "vector-sea/holoaeon-v4-cold-hot-plug/100_model_provider_catalog.json",
    },
    {
        "id": "zhipu", "label": "智谱 GLM", "kind": "大模型", "provider_id": "zhipu",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "base_url_env": "HOLOAEON_ZHIPU_BASE_URL", "key_env": "HOLOAEON_ZHIPU_API_KEY",
        "models": ["glm-4", "glm-4-flash"], "status": "adapted", "shape": "openai_chat",
        "evidence": "provider 目录 zhipu 条：OpenAI 兼容",
        "source_url": "vector-sea/holoaeon-v4-cold-hot-plug/100_model_provider_catalog.json",
    },
    {
        "id": "ollama", "label": "Ollama（本地运行时）", "kind": "本地运行时", "provider_id": "ollama",
        "base_url": "http://localhost:11434/v1",
        "base_url_env": "HOLOAEON_OLLAMA_BASE_URL", "key_env": "HOLOAEON_OLLAMA_API_KEY",
        "models": ["llama3", "qwen2.5", "<本地已拉取模型>"], "status": "adapted", "shape": "openai_chat",
        "evidence": "provider 目录 ollama 条：本地默认不需要 key（key_env 可留空）",
        "source_url": "vector-sea/holoaeon-v4-cold-hot-plug/100_model_provider_catalog.json",
    },
    {
        "id": "openai-compatible-generic", "label": "通用 OpenAI 兼容网关", "kind": "网关", "provider_id": "custom",
        "base_url": "https://<你的网关>/v1",
        "base_url_env": "HOLOAEON_CUSTOM_BASE_URL", "key_env": "HOLOAEON_CUSTOM_API_KEY",
        "models": ["<你的型号>"], "status": "adapted", "shape": "openai_chat",
        "evidence": "provider 目录 custom 条：只要网关说 OpenAI 形状，本仓就能拼对请求",
        "source_url": "vector-sea/holoaeon-v4-cold-hot-plug/100_model_provider_catalog.json",
    },
    {
        "id": "xfyun", "label": "讯飞星火", "kind": "大模型", "provider_id": None,
        "base_url": "https://spark-api-open.xf-yun.com/v1",
        "base_url_env": "HOLOAEON_XFYUN_BASE_URL", "key_env": "HOLOAEON_XFYUN_API_KEY",
        "models": ["4.0Ultra", "generalv3.5", "max-32k", "generalv3", "pro-128k", "lite"],
        "status": "adapted", "shape": "openai_chat",
        "evidence": ("讯飞官方 HTTP 文档：请求地址 https://spark-api-open.xf-yun.com/v1/chat/completions，"
                     "请求头 Authorization: Bearer <APIPassword>，且明确「兼容 openAI SDK」"
                     "（base_url 配 https://spark-api-open.xf-yun.com/v1/）"),
        "source_url": "https://www.xfyun.cn/doc/spark/HTTP调用文档.html",
    },
    {
        "id": "dify", "label": "Dify 应用平台", "kind": "工作台", "provider_id": None,
        "base_url": "https://api.dify.ai/v1",
        "base_url_env": "HOLOAEON_DIFY_BASE_URL", "key_env": "HOLOAEON_DIFY_API_KEY",
        "models": ["<应用内配置>"], "status": "adapted", "shape": "dify_chat",
        "endpoint": "/chat-messages",
        "evidence": ("Dify 官方《API 集成》：对话应用 POST /v1/chat-messages，"
                     "body={inputs, query, response_mode, conversation_id, user}；"
                     "文本生成 POST /v1/completion-messages；鉴权 Bearer <app key>"),
        "source_url": "https://docs.dify.ai/zh-hans/guides/application-publishing/developing-with-apis",
    },
    {
        "id": "coze", "label": "Coze 扣子平台", "kind": "工作台", "provider_id": None,
        "base_url": "https://api.coze.cn/v3",
        "base_url_env": "HOLOAEON_COZE_BASE_URL", "key_env": "HOLOAEON_COZE_API_KEY",
        "models": ["<智能体内配置>"], "status": "adapted", "shape": "coze_chat",
        "endpoint": "/chat",
        "evidence": ("Coze 官方《发起对话》V3：POST https://api.coze.cn/v3/chat（可带 conversation_id 查询参数），"
                     "body={bot_id, user_id, stream, auto_save_history, additional_messages[]}；鉴权 Bearer pat_…"),
        "source_url": "https://www.coze.cn/open/docs/developer_guides/chat_v3",
    },
    {
        "id": "n8n", "label": "n8n 工作流", "kind": "工作流", "provider_id": None,
        "base_url": "https://{instance}.app.n8n.cloud/api/v1",
        "base_url_env": "HOLOAEON_N8N_BASE_URL", "key_env": "HOLOAEON_N8N_API_KEY",
        "models": [], "status": "adapted", "shape": "n8n_api",
        "endpoint": "/workflows",
        "evidence": ("n8n 官方 Public REST API：Server https://{instance}.app.n8n.cloud/api/v1（自建为 <host>/api/v1），"
                     "鉴权头 X-N8N-API-KEY，资源端点族 /workflows /executions /credentials 等；"
                     "工作流触发侧走 webhook（POST <host>/webhook/<path>）"),
        "source_url": "https://docs.n8n.io/api/api-reference/",
    },
    {
        "id": "dify-workflow", "label": "Dify 工作流编排", "kind": "工作流", "provider_id": None,
        "base_url": "https://api.dify.ai/v1",
        "base_url_env": "HOLOAEON_DIFY_BASE_URL", "key_env": "HOLOAEON_DIFY_API_KEY",
        "models": [], "status": "adapted", "shape": "dify_workflow",
        "endpoint": "/workflows/run",
        "request_body": {
            "inputs": "object，键名映射到开始节点声明的字段",
            "response_mode": "blocking | streaming；省略时按 blocking 跑",
            "user": "string，终端用户标识（服务端 required=True，缺失即 400）",
            "files": "可选，多模态输入（先走 /files/upload 再引用）",
        },
        "response_fields": ["id", "workflow_id", "status", "inputs", "outputs", "error",
                            "total_steps", "total_tokens", "created_at", "finished_at",
                            "elapsed_time"],
        "error_codes": {
            "400": ["not_workflow_app", "provider_not_initialize", "provider_quota_exceeded",
                    "model_currently_not_support", "completion_request_error", "invalid_param"],
            "403": ["forbidden", "trigger_workflow_service_mode_unavailable"],
            "429": ["too_many_requests", "rate_limit_error"],
            "500": ["internal_server_error"],
        },
        "precondition": ("app_mode 必须为 WORKFLOW（否则 NotWorkflowAppError）；"
                         "Trigger 入口类工作流禁止经 Web App / Service API / OpenAPI / MCP 调用；"
                         "工作流必须已发布"),
        "evidence": (
            "Dify 主仓源码取证（非二手博客）：api/controllers/service_api/app/workflow.py 中 "
            "@service_api_ns.route('/workflows/run') → class WorkflowRunApi(Resource).post，"
            "并另有 @service_api_ns.route('/workflows/<string:workflow_id>/run')；"
            "请求体 WorkflowRunPayload 继承 WorkflowRunPayloadBase，response_mode 为 "
            "Literal['blocking','streaming'] | None（省略即 blocking）；"
            "响应模型 WorkflowRunResponse（status 为 PAUSED 时 outputs 被清空）；"
            "装饰器链 validate_app_token + expect_with_user 决定鉴权与 user 必填；"
            "'Cannot be executed without a published workflow'"
        ),
        "source_url": ("https://raw.githubusercontent.com/langgenius/dify/main/"
                       "api/controllers/service_api/app/workflow.py"),
        # V67：契约由「读到的」推进到「本机回环跑通的」——
        # 仍不是 Dify 官方实例（无实例无 token），故 verification 同时标两段。
        "verification": "source_code_read+local_contract_loopback",
        "loopback": {
            "verified_at": "2026-11-12",
            "scope": "local_contract_loopback（本机 http.server 模拟，非 Dify 官方实例）",
            "checks": 15,
            "passed": 15,
            "what_it_proves": [
                "POST /v1/workflows/run 路径与 Bearer 鉴权头形式正确",
                "请求体恰为 inputs/response_mode/user 三键，缺省 response_mode=blocking",
                "响应 11 字段齐全且 status=succeeded、outputs 可解析",
                "缺 user → 400 invalid_param（对应源码 expect_with_user(required=True)）",
                "stream=True 时 body 的 response_mode 变为 streaming",
            ],
            "what_it_does_not_prove": (
                "Dify 官方服务可用性、真实工作流编排结果、真实配额与错误码触发——"
                "需真实例与 app token，本仓零网络纪律下不验"
            ),
            "reproduce": "python F:\\doubaowork\\holoaeon_lathe\\v67_dify_loopback.py（仓外，不入库）",
        },
    },
)

ENABLE_RULE: Dict[str, Any] = {
    "env_switch": "HOLOAEON_REAL_MODELS",
    "enable_value": "1",
    "per_platform": "该平台 key_env 有值（本地运行时如 ollama 允许 key_env 为空）",
    "default_state": "全部 disabled",
    "no_network_in_repo": True,
    "schema_verified": False,
    "why_not_verified": "本仓零网络纪律：只做「请求拼得对」，不做联网握手可用性校验",
}


# ---------------------------------------------------------------------------
# 一、请求拼装（按形状分派；gap 不假拼）
# ---------------------------------------------------------------------------

def openai_chat_request(model: str, messages: List[Dict[str, str]],
                        temperature: float = 0.2, stream: bool = False) -> Dict[str, Any]:
    if not model:
        raise ValueError("model 不能为空")
    if not messages:
        raise ValueError("messages 不能为空")
    return {"model": model, "messages": list(messages),
            "temperature": float(temperature), "stream": bool(stream)}


def get_platform(pid: str) -> Dict[str, Any]:
    for g in GAPS:
        if g["id"] == pid:
            return g
    raise KeyError("未登记的缺口平台：{}".format(pid))


def build_request(pid: str, model: str = "", messages: Optional[List[Dict[str, str]]] = None,
                  temperature: float = 0.2, stream: bool = False,
                  extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """按平台状态与形状拼请求。adapted 出可发送结构；gap 掷明确错误（不假拼）。"""
    p = get_platform(pid)
    if p["status"] != "adapted":
        raise ValueError("{} 仍是缺口（{}）——缺：{}".format(pid, p["kind"], p.get("missing")))
    shape = p["shape"]
    base = (p["base_url"] or "").rstrip("/")
    out: Dict[str, Any] = {"platform": pid, "shape": shape, "base_url_env": p["base_url_env"],
                           "key_env": p["key_env"], "schema_verified": False}
    if shape == "openai_chat":
        body = openai_chat_request(model, messages or [], temperature, stream)
        out.update({"method": "POST", "url": base + "/chat/completions",
                    "headers_hint": {"Authorization": "Bearer ${}".format(p["key_env"])},
                    "body": body})
        return out
    if shape == "dify_chat":
        body = {"inputs": dict((extra or {}).get("inputs") or {}),
                "query": (extra or {}).get("query", ""),
                "response_mode": "streaming" if stream else "blocking",
                "conversation_id": (extra or {}).get("conversation_id", ""),
                "user": (extra or {}).get("user", "holoaeon")}
        if not body["query"]:
            raise ValueError("dify_chat 需要 extra['query']")
        out.update({"method": "POST", "url": base + p["endpoint"],
                    "headers_hint": {"Authorization": "Bearer ${}".format(p["key_env"])},
                    "body": body})
        return out
    if shape == "dify_workflow":
        inputs = dict((extra or {}).get("inputs") or {})
        mode = (extra or {}).get("response_mode")
        if mode is None:
            mode = "streaming" if stream else "blocking"
        if mode not in ("blocking", "streaming"):
            raise ValueError("dify_workflow 的 response_mode 只能是 blocking/streaming")
        body: Dict[str, Any] = {"inputs": inputs, "response_mode": mode,
                                "user": (extra or {}).get("user", "holoaeon")}
        files = list((extra or {}).get("files") or [])
        if files:
            body["files"] = files   # 先经 POST /files/upload 拿到的 file 对象
        out.update({"method": "POST", "url": base + p["endpoint"],
                    "headers_hint": {"Authorization": "Bearer ${}".format(p["key_env"])},
                    "stream": mode == "streaming",
                    "body": body,
                    "note": ("Service API 只服务已发布的 Workflow 类型应用；"
                             "Trigger 入口工作流会被 403 trigger_workflow_service_mode_unavailable 拒绝")})
        return out
    if shape == "coze_chat":
        msg = list((extra or {}).get("additional_messages") or [])
        if not msg:
            raise ValueError("coze_chat 需要 extra['additional_messages']")
        body = {"bot_id": (extra or {}).get("bot_id", ""),
                "user_id": (extra or {}).get("user_id", "holoaeon"),
                "stream": bool(stream), "auto_save_history": True,
                "additional_messages": msg}
        if not body["bot_id"]:
            raise ValueError("coze_chat 需要 extra['bot_id']")
        out.update({"method": "POST", "url": base + p["endpoint"],
                    "headers_hint": {"Authorization": "Bearer ${}".format(p["key_env"])},
                    "body": body})
        return out
    if shape == "n8n_api":
        action = (extra or {}).get("action", "list_workflows")
        if action == "list_workflows":
            out.update({"method": "GET", "url": base + "/workflows",
                        "headers_hint": {"X-N8N-API-KEY": "${}".format(p["key_env"])}, "body": None})
        elif action == "activate_workflow":
            wid = (extra or {}).get("workflow_id", "")
            if not wid:
                raise ValueError("activate_workflow 需要 extra['workflow_id']")
            out.update({"method": "POST", "url": "{}/workflows/{}/activate".format(base, wid),
                        "headers_hint": {"X-N8N-API-KEY": "${}".format(p["key_env"])}, "body": {}})
        elif action == "trigger_webhook":
            path = (extra or {}).get("webhook_path", "")
            if not path:
                raise ValueError("trigger_webhook 需要 extra['webhook_path']")
            host = (extra or {}).get("webhook_base", "https://<host>").rstrip("/")
            out.update({"method": "POST", "url": "{}/webhook/{}".format(host, path.lstrip("/")),
                        "headers_hint": {}, "body": dict((extra or {}).get("payload") or {})})
        else:
            raise ValueError("未知 n8n action：{}".format(action))
        return out
    raise NotImplementedError("形状 {} 的拼装器尚未落地".format(shape))


# ---------------------------------------------------------------------------
# 二、两态盘点
# ---------------------------------------------------------------------------

def check_gaps() -> Dict[str, Any]:
    problems: List[str] = []
    adapted = [g for g in GAPS if g["status"] == "adapted"]
    gaps = [g for g in GAPS if g["status"] == "gap"]
    shape_ids = {s["id"] for s in ALL_SHAPES}
    for g in adapted:
        if not g.get("base_url") or not g.get("key_env") or not g.get("base_url_env"):
            problems.append("adapted 项 {} 缺 base_url/key_env/base_url_env".format(g["id"]))
        if g.get("shape") not in shape_ids:
            problems.append("adapted 项 {} 形状不在在册形状内".format(g["id"]))
        if not g.get("evidence") or not g.get("source_url"):
            problems.append("adapted 项 {} 无证据或来源 URL".format(g["id"]))
        if g["kind"] in ("大模型", "本地运行时", "网关") and g.get("shape") != "openai_chat":
            problems.append("模型类 adapted 项 {} 形状不是 openai_chat".format(g["id"]))
        if g["kind"] in ("工作台", "工作流") and g.get("shape") == "openai_chat":
            problems.append("工作台类 adapted 项 {} 被硬塞进 openai_chat".format(g["id"]))
    for g in gaps:
        if not g.get("missing"):
            problems.append("gap 项 {} 未写明缺什么".format(g["id"]))
    if len(GAPS) != 12:
        problems.append("缺口总数 != 12（实 {}）".format(len(GAPS)))
    return {
        "schema": SCHEMA_VERSION,
        "total": len(GAPS),
        "adapted": len(adapted),
        "gaps": len(gaps),
        "adapted_list": [g["id"] for g in adapted],
        "gap_list": [g["id"] for g in gaps],
        "model_shapes": len(MODEL_SHAPES),
        "platform_shapes": len(PLATFORM_SHAPES),
        "problems": problems,
        "verdict": "PASS" if not problems else "FAIL",
    }


def build_ledger() -> Dict[str, Any]:
    return {
        "schema": SCHEMA_VERSION,
        "batch": "V66-RESONANCE-PACK-BODYWORK",
        "dom": "12 协议缺口逐条落地（V66 起 12 adapted / 0 gap）",
        "hangover_origin": ("V63 receipt：在册 12 / 缺口 12（回执 adapted_list 误填缺口清单）；"
                            "V64 落 11 adapted + 1 gap；V66 读 Dify 主仓源码补齐最后 1 条"),
        "catalog_source": ("vector-sea/holoaeon-v4-cold-hot-plug/100_model_provider_catalog.json"
                           "（SG-V44-MODEL-PROVIDER-CATALOG-V1，22 providers / 5 模型形状）"),
        "doc_sources": [{"platform": g["id"], "url": g.get("source_url"),
                         "fetched_at": FETCHED_AT} for g in GAPS
                        if str(g.get("source_url", "")).startswith("http")],
        "model_shapes": list(MODEL_SHAPES),
        "platform_shapes": list(PLATFORM_SHAPES),
        "platforms": list(GAPS),
        "enable_rule": ENABLE_RULE,
        "check": check_gaps(),
        "seal": SEAL,
    }


def write_ledger(path: Optional[str] = None) -> str:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = path or os.path.join(root, "data", DATA_OUT_NAME)
    io.open(out, "w", encoding="utf-8", newline="\n").write(
        json.dumps(build_ledger(), ensure_ascii=False, indent=1) + "\n")
    return out


def main(argv: Optional[List[str]] = None) -> int:
    import sys
    argv = list(argv if argv is not None else sys.argv[1:])
    if not argv:
        print("用法：python -m holoaeon.gap_adapters check | ledger")
        return 1
    if argv[0] == "check":
        rep = check_gaps()
        print(json.dumps(rep, ensure_ascii=False, indent=1))
        return 0 if rep["verdict"] == "PASS" else 1
    if argv[0] == "ledger":
        print("台账已写：{}".format(write_ledger()))
        return 0
    print("未知命令：{}".format(argv[0]))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
