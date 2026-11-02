# -*- coding: utf-8 -*-
"""V4.4 · 真实模型桥接（离线拼请求，不联网）

设计约束（与仓库红线一致）
--------------------------------
1. 本模块**不发请求**、不 import 任何网络库、不读密钥值，只做「登记 + 拼请求 + 出配置清单」。
2. 默认全关：`HOLOAEON_REAL_MODELS=1` 且对应 provider 的 key 环境变量有值，才把该后端置为 enabled。
3. 任何输出里的凭证位一律是占位符（`<HOLOAEON_XXX_API_KEY>`），绝不出现真实 key。
4. 目录来自 `data/model_provider_catalog.json`：19 家 / 5 种协议 / 4 个本地运行时 / 1 个自定义兜底。

与 `ModelAdapter` 的关系
------------------------
`ModelGateway.attach(adapter)` 会把**已启用**的 provider 注册成 `ModelBackend`（capabilities 取自目录），
`ModelAdapter` 原有的 8 种路由策略与用量记账不变；未启用时一个后端都不注册，适配层保持只剩本地事实包。
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

SWITCH_ENV = "HOLOAEON_REAL_MODELS"
SWITCH_ON = "1"
CATALOG_REL = os.path.join("data", "model_provider_catalog.json")

# 每种协议族的最小请求形状（只拼字段，不发请求）
PROTOCOL_SHAPES = {
    "openai_chat": "messages[] + model",
    "anthropic_messages": "system + messages[] + max_tokens",
    "google_gemini": "contents[] + generationConfig",
    "bedrock_converse": "messages[] + inferenceConfig",
    "azure_openai": "messages[] + api-version + deployment",
}


def load_catalog(root: str) -> Dict[str, Any]:
    path = os.path.join(root, CATALOG_REL)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@dataclass
class ProviderSpec:
    id: str
    label: str
    region: str
    api_style: str
    base_url_env: str
    key_env: str
    default_base_url: str = ""
    models: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    modalities: List[str] = field(default_factory=list)
    notes: str = ""

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ProviderSpec":
        return cls(id=d["id"], label=d.get("label", d["id"]), region=d.get("region", "any"),
                   api_style=d.get("api_style", "openai_chat"),
                   base_url_env=d.get("base_url_env", ""), key_env=d.get("key_env", ""),
                   default_base_url=d.get("default_base_url", ""),
                   models=list(d.get("models", [])), capabilities=list(d.get("capabilities", [])),
                   modalities=list(d.get("modalities", [])), notes=d.get("notes", ""))

    def snapshot(self) -> Dict[str, Any]:
        return {"id": self.id, "label": self.label, "region": self.region,
                "api_style": self.api_style, "models": self.models,
                "capabilities": self.capabilities, "modalities": self.modalities}


class ModelGateway:
    """登记 + 状态 + 拼请求；不联网。"""

    def __init__(self, catalog: Dict[str, Any], environ: Optional[Dict[str, str]] = None) -> None:
        self.catalog = catalog
        self.environ = dict(os.environ if environ is None else environ)
        self.protocols = {p["id"]: p for p in catalog.get("protocols", [])}
        self.providers: List[ProviderSpec] = [ProviderSpec.from_dict(p)
                                              for p in catalog.get("providers", [])]
        self.by_id: Dict[str, ProviderSpec] = {p.id: p for p in self.providers}

    # ---------------------------------------------------------------- 状态
    def _switch_on(self) -> bool:
        return self.environ.get(SWITCH_ENV, "") == SWITCH_ON

    def _key_present(self, spec: ProviderSpec) -> bool:
        # 只看「有没有」，不取内容；本地运行时允许为空
        if spec.region == "local":
            return True
        return bool(self.environ.get(spec.key_env, "").strip())

    def configured(self) -> List[str]:
        return [p.id for p in self.providers if self._key_present(p)]

    def enabled(self) -> List[str]:
        if not self._switch_on():
            return []
        return [p.id for p in self.providers if self._key_present(p)]

    def state(self) -> Dict[str, Any]:
        return {"catalog_id": self.catalog.get("id"),
                "switch": SWITCH_ENV, "switch_on": self._switch_on(),
                "providers": len(self.providers), "protocols": len(self.protocols),
                "configured": self.configured(), "enabled": self.enabled(),
                "local_runtimes": [p.id for p in self.providers if p.region == "local"],
                "default_off": not self._switch_on()}

    # ---------------------------------------------------------------- 拼请求
    def _base_url(self, spec: ProviderSpec) -> str:
        return (self.environ.get(spec.base_url_env, "").strip()
                or spec.default_base_url or "https://<你的网关>/v1")

    def _placeholder(self, spec: ProviderSpec) -> str:
        if spec.region == "local":
            return "<本地运行时通常无需 key>"
        if self._key_present(spec):
            return "<已由环境变量 %s 注入>" % spec.key_env
        return "<%s>" % spec.key_env

    def plan(self, provider_id: str, model: Optional[str] = None,
             prompt: str = "", system: Optional[str] = None) -> Dict[str, Any]:
        if provider_id not in self.by_id:
            raise KeyError("目录里没有该 provider：%s" % provider_id)
        spec = self.by_id[provider_id]
        style = spec.api_style
        mdl = model or (spec.models[0] if spec.models else "<model>")
        url = self._base_url(spec)
        headers = {"Content-Type": "application/json",
                   "Authorization": "Bearer " + self._placeholder(spec)}

        if style == "openai_chat":
            body = {"model": mdl, "messages": [{"role": "user", "content": prompt}],
                    "stream": False}
        elif style == "anthropic_messages":
            body = {"model": mdl, "max_tokens": 1024,
                    "messages": [{"role": "user", "content": prompt}]}
            if system:
                body["system"] = system
            headers["x-api-key"] = self._placeholder(spec)
            headers["anthropic-version"] = "2023-06-01"
        elif style == "google_gemini":
            body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.2}}
            url = url.rstrip("/") + "/models/" + mdl + ":generateContent"
            headers["x-goog-api-key"] = self._placeholder(spec)
        elif style == "bedrock_converse":
            body = {"modelId": mdl,
                    "messages": [{"role": "user", "content": [{"text": prompt}]}],
                    "inferenceConfig": {"maxTokens": 1024}}
        elif style == "azure_openai":
            body = {"messages": [{"role": "user", "content": prompt}], "max_tokens": 1024}
            url = url.rstrip("/") + "/chat/completions?api-version=2024-10-21"
            headers["api-key"] = self._placeholder(spec)
        else:
            raise ValueError("未知协议族：%s" % style)

        return {"provider": spec.id, "label": spec.label, "api_style": style,
                "protocol": PROTOCOL_SHAPES.get(style, ""),
                "url": url, "headers": headers, "body": body,
                "model": mdl,
                "configured": self._key_present(spec),
                "enabled": spec.id in self.enabled(),
                "network": False,
                "note": "本仓只拼请求；真正发送请在你的运行时/网关侧完成。"}

    def sample_plans(self, prompt: str = "ping") -> Dict[str, Any]:
        """各协议族各取一家，验形状；不联网。"""
        picked: Dict[str, str] = {}
        for p in self.providers:
            picked.setdefault(p.api_style, p.id)
        return {style: self.plan(pid, prompt=prompt) for style, pid in picked.items()}

    # ---------------------------------------------------------------- 接适配层
    def attach(self, adapter: Any) -> List[str]:
        """只注册已启用的 provider；未启用时返回空列表，适配层不动。"""
        from ..model_adapter import ModelBackend  # 延迟导入，避免顶层环依赖
        added: List[str] = []
        for pid in self.enabled():
            spec = self.by_id[pid]
            adapter.register_backend(ModelBackend(
                name="gw:" + spec.id, provider=spec.id, family="chat",
                context_window=32768 if "long_context" in spec.capabilities else 8192,
                latency_ms=50 if spec.region == "local" else 800,
                input_cost=0.0 if spec.region == "local" else 0.0,
                output_cost=0.0,
                capabilities=list(spec.capabilities),
                modalities=list(spec.modalities) or ["text"]))
            added.append("gw:" + spec.id)
        return added

    def probe(self) -> Dict[str, Any]:
        return {"state": self.state(),
                "coverage": self.catalog.get("coverage", {}),
                "shapes": self.sample_plans(),
                "enable_rule": self.catalog.get("enable_rule", {})}


def build_gateway(root: str, environ: Optional[Dict[str, str]] = None) -> ModelGateway:
    return ModelGateway(load_catalog(root), environ=environ)
