# -*- coding: utf-8 -*-
"""
model_base_registry —— 大模型基座登记表（bridges 层 · 声明层）
================================================================================
定位：真实登记国内国际大模型基座的「协议形状 + 端点占位 + 环境变量占位」，
为 forge_gate 的大小模型分工提供平台侧路由依据。

纪律（与 NetDiode 一致）：
  · 零连接：本模块不发任何网络请求——「适配」= 协议形状登记 + 配置就绪检查
    （env 变量存在性），连通握手不在本层，须机构端人工授权后另行执行
  · 零虚构：品牌/协议形状全部为公开事实；不声称「已测试连通」
  · 出站白名单=空集：平台大模型内容只能经入站升级三重门进内网，不走实时 API 直连

协议形状分四类：
  openai_chat        —— OpenAI Chat Completions 兼容（国内绝大多数厂商提供）
  anthropic_messages —— Anthropic Messages 协议
  google_genai       —— Google Generative AI 协议
  local_weights      —— 开放权重，可本地部署（走 ModelAutoCouple，不走 API）
"""
from __future__ import annotations

import os
from typing import Any, Dict, List

SEAL = "潮起开门，潮落闭嘴"

# ---------------------------------------------------------------- 基座登记表
# 字段：vendor 厂商 / base 基座名 / origin 国内|国际 / protocol 协议形状
#       endpoint_env 端点环境变量占位 / key_env 密钥环境变量占位
#       local_weights 是否有可本地部署的开放权重
MODEL_BASES: List[Dict[str, Any]] = [
    # ---- 国际 ----
    {"base": "gpt", "vendor": "OpenAI", "origin": "国际",
     "protocol": "openai_chat",
     "endpoint_env": "OPENAI_BASE_URL", "key_env": "OPENAI_API_KEY",
     "local_weights": False},
    {"base": "claude", "vendor": "Anthropic", "origin": "国际",
     "protocol": "anthropic_messages",
     "endpoint_env": "ANTHROPIC_BASE_URL", "key_env": "ANTHROPIC_API_KEY",
     "local_weights": False},
    {"base": "gemini", "vendor": "Google", "origin": "国际",
     "protocol": "google_genai",
     "endpoint_env": "GEMINI_BASE_URL", "key_env": "GEMINI_API_KEY",
     "local_weights": False},
    {"base": "llama", "vendor": "Meta", "origin": "国际",
     "protocol": "local_weights",
     "endpoint_env": "", "key_env": "",
     "local_weights": True},
    {"base": "mistral", "vendor": "Mistral AI", "origin": "国际",
     "protocol": "openai_chat",
     "endpoint_env": "MISTRAL_BASE_URL", "key_env": "MISTRAL_API_KEY",
     "local_weights": True},
    {"base": "grok", "vendor": "xAI", "origin": "国际",
     "protocol": "openai_chat",
     "endpoint_env": "XAI_BASE_URL", "key_env": "XAI_API_KEY",
     "local_weights": False},
    # ---- 国内 ----
    {"base": "qwen", "vendor": "阿里·通义千问", "origin": "国内",
     "protocol": "openai_chat",
     "endpoint_env": "QWEN_BASE_URL", "key_env": "QWEN_API_KEY",
     "local_weights": True},
    {"base": "deepseek", "vendor": "深度求索", "origin": "国内",
     "protocol": "openai_chat",
     "endpoint_env": "DEEPSEEK_BASE_URL", "key_env": "DEEPSEEK_API_KEY",
     "local_weights": True},
    {"base": "glm", "vendor": "智谱 AI", "origin": "国内",
     "protocol": "openai_chat",
     "endpoint_env": "GLM_BASE_URL", "key_env": "GLM_API_KEY",
     "local_weights": True},
    {"base": "kimi", "vendor": "月之暗面", "origin": "国内",
     "protocol": "openai_chat",
     "endpoint_env": "KIMI_BASE_URL", "key_env": "KIMI_API_KEY",
     "local_weights": True},
    {"base": "ernie", "vendor": "百度·文心", "origin": "国内",
     "protocol": "openai_chat",
     "endpoint_env": "ERNIE_BASE_URL", "key_env": "ERNIE_API_KEY",
     "local_weights": False},
    {"base": "spark", "vendor": "科大讯飞·星火", "origin": "国内",
     "protocol": "openai_chat",
     "endpoint_env": "SPARK_BASE_URL", "key_env": "SPARK_API_KEY",
     "local_weights": False},
    {"base": "hunyuan", "vendor": "腾讯·混元", "origin": "国内",
     "protocol": "openai_chat",
     "endpoint_env": "HUNYUAN_BASE_URL", "key_env": "HUNYUAN_API_KEY",
     "local_weights": True},
    {"base": "minimax", "vendor": "MiniMax", "origin": "国内",
     "protocol": "openai_chat",
     "endpoint_env": "MINIMAX_BASE_URL", "key_env": "MINIMAX_API_KEY",
     "local_weights": False},
]

PROTOCOL_SHAPES = ("openai_chat", "anthropic_messages", "google_genai", "local_weights")


def classify() -> Dict[str, List[str]]:
    """按协议形状分组。"""
    groups: Dict[str, List[str]] = {p: [] for p in PROTOCOL_SHAPES}
    for b in MODEL_BASES:
        groups[b["protocol"]].append(b["base"])
    return groups


def get(base_id: str) -> Dict[str, Any]:
    for b in MODEL_BASES:
        if b["base"] == base_id:
            return b
    raise KeyError("unknown base: %r（登记表共 %d 条，零虚构不臆造）" % (base_id, len(MODEL_BASES)))


def readiness(base_id: str) -> Dict[str, Any]:
    """配置就绪检查：env 变量存在性。纯本地检查，零连接零请求。
    未配置 → not_ready（如实报告，不报错不降级）。"""
    b = get(base_id)
    if b["protocol"] == "local_weights":
        return {"base": base_id, "ready": True,
                "note": "开放权重走 bridges.site_gateway.ModelAutoCouple 本地耦合",
                "seal": SEAL}
    endpoint_set = bool(b["endpoint_env"] and os.environ.get(b["endpoint_env"]))
    key_set = bool(b["key_env"] and os.environ.get(b["key_env"]))
    ready = endpoint_set and key_set
    return {"base": base_id, "ready": ready,
            "endpoint_env": b["endpoint_env"], "endpoint_set": endpoint_set,
            "key_env": b["key_env"], "key_set": key_set,
            "note": "就绪=配置存在；连通握手须机构端人工授权另行执行（本层零连接）",
            "seal": SEAL}


def readiness_all() -> List[Dict[str, Any]]:
    return [readiness(b["base"]) for b in MODEL_BASES]


def coupling_plan() -> Dict[str, Any]:
    """耦合总案：大模型→升级/翻译通道（入站三重门）；小模型→ModelAutoCouple。
    本函数只输出方案（声明层），不执行任何连接。"""
    return {
        "seal": SEAL,
        "total_bases": len(MODEL_BASES),
        "by_origin": {
            "国内": [b["base"] for b in MODEL_BASES if b["origin"] == "国内"],
            "国际": [b["base"] for b in MODEL_BASES if b["origin"] == "国际"],
        },
        "by_protocol": classify(),
        "local_weight_bases": [b["base"] for b in MODEL_BASES if b["local_weights"]],
        "plan": {
            "platform_large": {
                "tasks": ["plugin_upgrade", "vector_upgrade", "brief_translation"],
                "channel": "入站升级三重门（类型+SHA+审批+staging），无实时直连",
                "auth": "explicit_auth 必须为 True（forge_gate.ModelSplitRules 路由）",
            },
            "local_small": {
                "tasks": ["offline_runtime", "intranet_processing",
                          "mlps3_compliance", "internal_data"],
                "channel": "bridges.site_gateway.ModelAutoCouple（ollama>lmstudio>vllm>GGUF>包）",
                "auth": "无需出站授权（本地进程内调用）",
            },
        },
        "boundary_rule": "出站白名单=空集（结构性零出站）；内外网不打通",
        "compliance_note": (
            "本框架为工程与工程管理工具，不对外提供服务，依《生成式人工智能服务管理"
            "暂行办法》第二条第三款不适用该办法。若部署方将本框架与生成式模型耦合后"
            "向境内公众提供服务，备案/登记义务由该服务提供者（部署方）承担。"
        ),
    }


def report() -> Dict[str, Any]:
    return {"seal": SEAL, "bases": MODEL_BASES,
            "classify": classify(), "readiness": readiness_all(),
            "coupling_plan": coupling_plan()}


if __name__ == "__main__":
    import json
    print(json.dumps(report(), ensure_ascii=False, indent=2))
