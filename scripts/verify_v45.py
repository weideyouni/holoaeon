# -*- coding: utf-8 -*-
"""V4.5-B1 校验：本地运行时联调（真实回环调用）。

B1 回执存在且 `evidence_class=live_local`（真实调用，不是 simulated）
B2 只打本机回环：URL host ∈ {127.0.0.1, localhost, ::1}
B3 HTTP 200，且按 mode 有实质载荷（chat→choices≥1；embeddings→向量维>0）
B4 载荷非空（chat→text 非空；embeddings→dim>0）
B5 无凭证泄漏（回执里没有 sk- / Bearer 真值）
B6 形状同源：回执 body 的核心键 ⊆ model_gateway.plan 的 body 键（chat）/ 本地链路键（embeddings）
B7 默认全关未破：干净环境下 gateway enabled=[]（防"联调把开关打开了"）

只读，不写文件（回执由 live_gateway_probe.py 产生），退出码 0/1。
"""
from __future__ import annotations

import json
import os
import sys
import urllib.parse
from typing import Any, Dict, List

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from holoaeon.fusion_upgrade.model_gateway import build_gateway  # noqa: E402

PROBE = os.path.join(ROOT, "reports", "v45_live_probe.json")
LOOPBACK = {"127.0.0.1", "localhost", "::1"}
CORE_CHAT = {"model", "messages", "stream"}
CORE_EMB = {"model", "input"}


def load(path: str) -> Dict[str, Any]:
    if not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    d = load(PROBE)
    req = d.get("request", {})
    res = d.get("response", {})
    mode = d.get("mode") or "chat"
    host = urllib.parse.urlparse(req.get("url", "")).hostname
    dim = int(res.get("embedding_dim") or 0)
    text = res.get("text") or ""

    checks: List[Dict[str, Any]] = []

    def add(cid: str, ok: bool, detail: Any) -> None:
        checks.append({"id": cid, "passed": bool(ok), "detail": detail})

    add("B1", bool(d) and d.get("evidence_class") == "live_local",
        {"present": bool(d), "evidence_class": d.get("evidence_class"), "mode": mode})
    add("B2", host in LOOPBACK, {"host": host})

    if mode == "embeddings":
        add("B3", res.get("status") == 200 and dim > 0,
            {"status": res.get("status"), "embedding_dim": dim})
        add("B4", dim > 0, {"embedding_dim": dim, "text_chars": len(text)})
        core = CORE_EMB
        plan_keys = sorted(set(req.get("body_keys") or []) & CORE_EMB)
        add("B6", CORE_EMB <= set(req.get("body_keys") or []),
            {"probe_body_keys": req.get("body_keys"), "required": sorted(CORE_EMB),
             "matched": plan_keys})
    else:
        add("B3", res.get("status") == 200 and (res.get("choices") or 0) >= 1,
            {"status": res.get("status"), "choices": res.get("choices")})
        add("B4", bool(text) and (res.get("usage", {}).get("total_tokens") or 0) > 0,
            {"text_chars": len(text), "usage": res.get("usage")})
        clean_tmp = {k: v for k, v in os.environ.items() if not k.startswith("HOLOAEON_")}
        gw_tmp = build_gateway(ROOT, environ=clean_tmp)
        plan = gw_tmp.plan("lmstudio", model=req.get("model") or "x", prompt="ping")
        add("B6", CORE_CHAT <= (set(req.get("body_keys") or []) & set(plan["body"])),
            {"probe_body_keys": req.get("body_keys"), "plan_body_keys": sorted(plan["body"]),
             "core_matched": sorted(CORE_CHAT & set(req.get("body_keys") or []) & set(plan["body"]))})

    blob = json.dumps(d, ensure_ascii=False)
    leaked = [k for k in ("sk-", "Bearer ") if k in blob]
    add("B5", not leaked, {"leak_tokens": leaked})

    clean = {k: v for k, v in os.environ.items() if not k.startswith("HOLOAEON_")}
    gw = build_gateway(ROOT, environ=clean)
    add("B7", gw.state()["enabled"] == [], {"enabled_clean": gw.state()["enabled"]})

    passed = sum(1 for c in checks if c["passed"])
    print(json.dumps({"id": "SG-V45-LIVE-CHECK-V1", "passed": passed, "total": len(checks),
                      "failed": [c["id"] for c in checks if not c["passed"]],
                      "verdict": "PASS" if passed == len(checks) else "FAIL",
                      "checks": checks}, ensure_ascii=False, indent=2))
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
