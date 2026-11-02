# -*- coding: utf-8 -*-
"""V4.1-B1 · B8 六项插件接实际推理（默认关闭，显式启用后只读取事实）。

设计口径
--------
1. 插件描述仍以 `data/ivsa_plugin_v1.2.json` 为唯一来源：`enabled_by_default=false`、
   `requires_explicit_enable=true`。未显式启用时 `capabilities_loaded=0`，不读任何客仓文件。
2. 六项能力与客仓六件只读数据件一一对应（见 `data/plugin_capability_registry.json`）：
   运行期只取「列名 / 行数 / 名字计数 / 文件摘要」，不复制内容、不 import 客仓代码、不写回。
3. 推理接入点 `ReasoningBridge`：问题 -> 能力路由（锚点确定性命中）-> 事实包
   （能力 id、行数、期望值是否相符、摘要前 16 位、样例名字）-> 封缄。
   事实包只带 `evidence_class=simulated`，不含诊断、剂量、疗效结论，三位红线在 guard 里硬拦。
4. 客仓根目录由调用方注入（环境变量 `HOLOAEON_GUEST_ROOT` 或显式参数），包内不写死本机路径，
   客仓缺失时能力状态为 `unavailable`，绝不伪造计数。
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import os
from typing import Any, Dict, Iterable, List, Optional, Tuple

REGISTRY_DEFAULT = os.path.join("data", "plugin_capability_registry.json")
PLUGIN_DEFAULT = os.path.join("data", "ivsa_plugin_v1.2.json")

DOSE_MARKERS = ("mg", "毫克", "ml", "克/日", "剂量", "用药", "服用", "每次")
CLINICAL_MARKERS = ("诊断", "确诊", "治疗方案", "处方", "愈后", "疗效判定")
REDLINES = {
    "zero_dose": "不输出任何剂量数值",
    "c0_not_efficacy": "不把登记事实写成疗效",
    "emergency_120": "急症/危象一律转 120，不进入推理",
    "no_diagnosis": "不做诊断与分期判断",
}


def _root(root: Optional[str] = None) -> str:
    if root:
        return root
    env = os.environ.get("HOLOAEON_GUEST_ROOT")
    if env:
        return env
    return ""


def _load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_of(obj: Any, size: int = 12) -> str:
    body = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(body.encode("utf-8")).hexdigest()[:size]


def _read_csv(path: str) -> Tuple[List[str], List[Dict[str, str]], bytes]:
    with open(path, "rb") as f:
        raw = f.read()
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    return list(reader.fieldnames or []), rows, raw


class Capability:
    """单项能力的只读解析句柄：行数、列名、样例名字、文件摘要。"""

    def __init__(self, spec: Dict[str, Any], guest_root: str) -> None:
        self.spec = spec
        self.id = spec["id"]
        self.guest_root = guest_root
        self.expected = int(spec["expected_rows"])

    def path(self) -> str:
        if not self.guest_root:
            return ""
        return os.path.join(self.guest_root, self.spec["guest_file"].replace("/", os.sep))

    def resolve(self, sample: int = 3) -> Dict[str, Any]:
        path = self.path()
        base = {
            "capability": self.id,
            "name_cn": self.spec.get("name_cn", ""),
            "guest_file": self.spec.get("guest_file", ""),
            "expected_rows": self.expected,
            "evidence_class": "simulated",
        }
        if not path or not os.path.isfile(path):
            base.update({"status": "unavailable", "rows": 0, "matched": False,
                         "reason": "guest_file_missing"})
            return base
        columns, rows, raw = _read_csv(path)
        keys = [k for k in self.spec.get("key_columns", []) if k in columns]
        samples = []
        for row in rows[:sample]:
            samples.append({k: row.get(k, "") for k in keys})
        base.update({
            "status": "ok",
            "rows": len(rows),
            "matched": len(rows) == self.expected,
            "columns": columns,
            "sha16": sha256_bytes(raw)[:16],
            "bytes": len(raw),
            "samples": samples,
            "groups": _group_counts(rows, "group") if "group" in columns else {},
        })
        return base


def _group_counts(rows: Iterable[Dict[str, str]], key: str) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for row in rows:
        value = (row.get(key) or "").strip()
        if not value:
            continue
        out[value] = out.get(value, 0) + 1
    return dict(sorted(out.items()))


class PluginRuntime:
    """ivsa v1.2 插件宿主侧运行器：默认关闭，显式密令启用。"""

    def __init__(self, registry: Dict[str, Any], plugin: Dict[str, Any],
                 guest_root: Optional[str] = None) -> None:
        self.registry = registry
        self.plugin = plugin
        self.guest_root = _root(guest_root)
        self._caps = {c["id"]: Capability(c, self.guest_root)
                      for c in registry["capabilities"]}
        self.enabled = False
        self.enabled_by = ""

    @classmethod
    def load(cls, root: Optional[str] = None, guest_root: Optional[str] = None,
             registry_path: Optional[str] = None, plugin_path: Optional[str] = None) -> "PluginRuntime":
        base = root or os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))
        reg = _load_json(registry_path or os.path.join(base, REGISTRY_DEFAULT))
        plug = _load_json(plugin_path or os.path.join(base, PLUGIN_DEFAULT))
        return cls(reg, plug, guest_root)

    # -- 启用/停用 ---------------------------------------------------------
    def enable(self, secret: str) -> Dict[str, Any]:
        allowed = set(self.registry.get("enable_secrets") or [])
        allowed.add(str(self.plugin.get("seal", "")))
        if not self.plugin.get("requires_explicit_enable"):
            return {"ok": False, "reason": "plugin_declares_no_explicit_enable"}
        if str(secret or "") not in allowed:
            return {"ok": False, "reason": "secret_mismatch",
                    "hint": "密令等同签字；不接受空串与近似串"}
        self.enabled = True
        self.enabled_by = "explicit_secret"
        return {"ok": True, "enabled": True,
                "plugin_id": self.plugin.get("plugin_id"),
                "capabilities": self.capability_ids()}

    def disable(self) -> Dict[str, Any]:
        self.enabled = False
        self.enabled_by = ""
        return {"ok": True, "enabled": False}

    # -- 能力 -------------------------------------------------------------
    def capability_ids(self) -> List[str]:
        return [c["id"] for c in self.registry["capabilities"]]

    def declared_capabilities(self) -> List[str]:
        return list(self.plugin.get("capabilities") or [])

    def resolve(self, capability: str) -> Dict[str, Any]:
        if not self.enabled:
            return {"capability": capability, "status": "disabled",
                    "rows": 0, "matched": False,
                    "reason": "explicit_enable_required", "evidence_class": "simulated"}
        cap = self._caps.get(capability)
        if cap is None:
            return {"capability": capability, "status": "unknown",
                    "rows": 0, "matched": False}
        return cap.resolve()

    def resolve_all(self) -> Dict[str, Any]:
        results = [self.resolve(cid) for cid in self.capability_ids()]
        loaded = sum(1 for r in results if r["status"] == "ok")
        matched = sum(1 for r in results if r.get("matched"))
        return {
            "plugin_id": self.plugin.get("plugin_id"),
            "plugin_version": self.plugin.get("version"),
            "enabled": self.enabled,
            "enabled_by": self.enabled_by,
            "capabilities_declared": len(self.declared_capabilities()),
            "capabilities_loaded": loaded,
            "capabilities_matched": matched,
            "results": results,
            "dimension_contract": dict(self.plugin.get("dimension_contract") or {}),
            "evidence_class": "simulated",
        }


class ReasoningBridge:
    """问题 -> 六项能力路由 -> 事实包（只带名字与计数，封缄可复算）。"""

    def __init__(self, runtime: PluginRuntime) -> None:
        self.runtime = runtime

    def route(self, question: str) -> List[str]:
        text = (question or "").lower()
        hits: List[Tuple[int, int, str]] = []
        for index, spec in enumerate(self.runtime.registry["capabilities"]):
            score = sum(1 for a in spec.get("anchors", []) if a.lower() in text)
            if score:
                hits.append((-score, index, spec["id"]))
        hits.sort()
        return [cid for _, _, cid in hits]

    def guard(self, question: str) -> Dict[str, Any]:
        text = (question or "").lower()
        dose = [m for m in DOSE_MARKERS if m.lower() in text]
        clinical = [m for m in CLINICAL_MARKERS if m in text]
        emergency = any(k in text for k in ("急症", "危象", "大出血", "昏迷", "抽搐"))
        blocked = bool(dose or clinical or emergency)
        reasons = []
        if dose:
            reasons.append("dose_request")
        if clinical:
            reasons.append("clinical_decision")
        if emergency:
            reasons.append("emergency_120")
        return {"blocked": blocked, "reasons": reasons,
                "matched_dose": dose[:3], "matched_clinical": clinical[:3],
                "action": "拒绝推理，转人工/120；不降级口径" if blocked else "pass"}

    def ask(self, question: str, max_caps: int = 3) -> Dict[str, Any]:
        guard = self.guard(question)
        routed = self.route(question)[:max_caps] if not guard["blocked"] else []
        facts = []
        if not guard["blocked"]:
            for cid in routed:
                item = self.runtime.resolve(cid)
                facts.append({
                    "capability": cid,
                    "name_cn": item.get("name_cn"),
                    "status": item.get("status"),
                    "rows": item.get("rows"),
                    "expected_rows": item.get("expected_rows"),
                    "matched": item.get("matched"),
                    "sha16": item.get("sha16"),
                    "samples": item.get("samples"),
                })
        body = {
            "question_digest": hashlib.sha256((question or "").encode("utf-8")).hexdigest()[:12],
            "routed": routed,
            "facts": facts,
            "guard": guard,
            "redlines": REDLINES,
            "evidence_class": "simulated",
            "note": "只读事实包：不给诊断、不给剂量、不声称疗效",
        }
        body["seal"] = digest_of({"q": body["question_digest"], "r": routed,
                                  "f": [{k: f.get(k) for k in ("capability", "rows", "matched")}
                                        for f in facts],
                                  "b": guard["blocked"], "e": "simulated"})
        return body


def probe_all(root: Optional[str] = None, guest_root: Optional[str] = None,
              secret: str = "潮起开门") -> Dict[str, Any]:
    """供校验器调用的一站式探针：默认态 0 加载 -> 显式启用 -> 六项全解析。"""
    runtime = PluginRuntime.load(root=root, guest_root=guest_root)
    off = runtime.resolve_all()
    on = runtime.enable(secret)
    loaded = runtime.resolve_all()
    return {"off": off, "enable": on, "on": loaded,
            "bridge": ReasoningBridge(runtime)}
