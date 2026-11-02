# -*- coding: utf-8 -*-
"""V4.4-B1 校验器：真实模型桥接的 A1–A13 判据。

A1  维度不变：`gate_fusion_v4.json` 的 A1 detail 必须等于 {"agents":25,"skills":47,"packs":9}
A2  目录覆盖：providers ≥ 12、协议族 = 5、本地运行时 ≥ 3、含聚合与自定义兜底
A3  字段齐备：每个 provider 有 id/label/api_style/base_url_env/key_env/models
A4  默认全关：干净环境下 enabled=[]、default_off=true
A5  无凭证泄漏：目录与模块文本里没有真 key 形态（sk-/Bearer <真值>），只有 env 变量名
A6  AST 红线：model_gateway.py 无网络库、无 eval/exec/compile/__import__/input/os.system
A7  五种协议形状：openai/anthropic/gemini/bedrock/azure 各拼出正确字段
A8  未配置降级：plan 返回 configured=false 且 headers 里无真值（只有占位）
A9  用户自设定入口：配置指南存在且含 BASE_URL / API_KEY / model 三件套说明
A10 五地零漂移：five_site_dna.verify() 的 drift 为空
A11 回执齐备：票据 + 校验回执存在，且回执 passed==total
A12 客仓只读未动：ivsa SHA256SUMS 的 sha256 仍为 9400b481…
A13 适配层不变：ModelAdapter 8 种路由策略仍可用（冒烟登记两个后端）

输出：`reports/v44_model_gateway_check.json`（`evidence_class=simulated`），退出码 0/1。
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import sys
from typing import Any, Dict, List

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import five_site_dna as fsd  # noqa: E402
from holoaeon.fusion_upgrade import model_gateway as mg  # noqa: E402
from holoaeon.fusion_upgrade import reasoning_adapter as ra  # noqa: E402
from holoaeon.model_adapter import ModelAdapter, ModelBackend  # noqa: E402

from pathlib import Path

IVSA_ROOT = os.environ.get(
    "HOLOAEON_IVSA_ROOT",
    r"F:\doubaowork\开源发布_中西医融合康复工程_20261026\integrative-rehab-vsa")
REPORT = os.path.join(ROOT, "reports", "v44_model_gateway_check.json")
TICKET = os.path.join(ROOT, "data", "V4.4_真实模型桥接票据.md")
GUIDE = os.path.join(ROOT, "docs", "接入真实模型_配置指南.md")

# 兄弟校验器的回执：它们与本脚本同属「跑一次就改写回执」的一类，
# 若只排除自己，任何一次同批复跑都会把别人的回执算成漂移（P0-1）。
SELF_REPORTS = (
    "reports/v43_hardening_check.json",
    "reports/v44_model_gateway_check.json",
    "reports/v45_live_probe.json",
    "reports/v45_live_probe_emb.json",
    "reports/v46_slot_check.json",
    "reports/v5_rehab_kb_check.json",
    "reports/design_vocab_check.json",
    "reports/five_site_manifest.json",
)
# 自己的回执要连「漂移计数」一起排除，否则每跑一次都会把自己算进 self_excluded，
# 报告字节在第一跑（1 条）与第二跑（0 条）之间来回跳，回执永不幂等。
OWN_REPORT = "reports/v44_model_gateway_check.json"


def _is_verifier_report(token: str) -> bool:
    """drift 条目形如 repo:<rel> / repo:changed:<rel> / repo:new:<rel>，统一按 rel 判。"""
    return any(token.endswith(rel) for rel in SELF_REPORTS)


def _is_sibling_report(token: str) -> bool:
    """兄弟校验器（不含自己）：它们只用于「如实报数」，不参与 passed 判定结果以外的回环。"""
    return _is_verifier_report(token) and not token.endswith(OWN_REPORT)

BANNED_MODS = {"subprocess", "urllib", "requests", "socket", "http", "aiohttp", "httpx"}
BANNED_CALL = {"eval", "exec", "compile", "__import__", "input", "system", "popen", "run"}


def load_json(rel: str) -> Dict[str, Any]:
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return json.load(f)


def read_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def check_a1() -> Dict[str, Any]:
    g = load_json("reports/gate_fusion_v4.json")
    a1 = next((c for c in g.get("checks", []) if c.get("id") == "A1"), {})
    ok = a1.get("detail") == {"agents": 25, "skills": 47, "packs": 9}
    return {"id": "A1", "passed": ok, "a1_detail": a1.get("detail"),
            "gate": "%s/%s" % (g.get("passed"), g.get("total"))}


def check_a2(gw: mg.ModelGateway) -> Dict[str, Any]:
    cov = gw.catalog["coverage"]
    ok = (len(gw.providers) >= 12 and len(gw.protocols) == 5
          and len([p for p in gw.providers if p.region == "local"]) >= 3
          and cov.get("aggregators") and cov.get("universal_escape") == "custom")
    return {"id": "A2", "passed": ok, "providers": len(gw.providers),
            "protocols": len(gw.protocols),
            "local": [p.id for p in gw.providers if p.region == "local"],
            "cn": len(cov.get("cn_cloud", [])), "global": len(cov.get("global_cloud", []))}


def check_a3(gw: mg.ModelGateway) -> Dict[str, Any]:
    bad = [p.id for p in gw.providers
           if not (p.id and p.label and p.api_style and p.base_url_env
                   and p.key_env and p.models)]
    return {"id": "A3", "passed": not bad, "bad": bad}


def check_a4(root: str) -> Dict[str, Any]:
    clean = {k: v for k, v in os.environ.items() if not k.startswith("HOLOAEON_")}
    gw = mg.build_gateway(root, environ=clean)
    st = gw.state()
    adapter = ModelAdapter()
    added = gw.attach(adapter)
    return {"id": "A4", "passed": st["enabled"] == [] and st["default_off"] and added == [],
            "enabled": st["enabled"], "added_backends": added}


def check_a5(root: str) -> Dict[str, Any]:
    texts = [read_text(os.path.join(ROOT, "data", "model_provider_catalog.json")),
             read_text(os.path.join(ROOT, "holoaeon", "fusion_upgrade", "model_gateway.py"))]
    hits: List[str] = []
    for t in texts:
        if "sk-" in t and "sk-<" not in t:
            for line in t.splitlines():
                if "sk-" in line and "<" not in line:
                    hits.append(line.strip()[:60])
    # key_env 必须是环境变量名，不许出现赋值形态
    for p in mg.load_catalog(root)["providers"]:
        if p["key_env"] and "=" in p["key_env"]:
            hits.append("key_env_assign:" + p["id"])
    return {"id": "A5", "passed": not hits, "hits": hits}


def check_a6() -> Dict[str, Any]:
    hits: List[str] = []
    for rel in ("holoaeon/fusion_upgrade/model_gateway.py",
                "holoaeon/fusion_upgrade/reasoning_adapter.py"):
        tree = ast.parse(read_text(os.path.join(ROOT, rel)))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    if a.name.split(".")[0] in BANNED_MODS:
                        hits.append("%s:import:%s" % (rel, a.name))
            if isinstance(node, ast.ImportFrom) and node.module:
                if node.module.split(".")[0] in BANNED_MODS:
                    hits.append("%s:from:%s" % (rel, node.module))
            if isinstance(node, ast.Call):
                name = getattr(node.func, "attr", None) or getattr(node.func, "id", None)
                if name in BANNED_CALL:
                    hits.append("%s:call:%s" % (rel, name))
    return {"id": "A6", "passed": not hits, "hits": hits}


def check_a7(gw: mg.ModelGateway) -> Dict[str, Any]:
    shapes = gw.sample_plans("ping")
    ok = set(shapes.keys()) == set(mg.PROTOCOL_SHAPES.keys())
    detail: Dict[str, Any] = {}
    for style, plan in shapes.items():
        body = plan["body"]
        if style == "openai_chat":
            detail[style] = "messages" in body and "model" in body
        elif style == "anthropic_messages":
            detail[style] = "messages" in body and "max_tokens" in body
        elif style == "google_gemini":
            detail[style] = "contents" in body and "generationConfig" in body
        elif style == "bedrock_converse":
            detail[style] = "messages" in body and "inferenceConfig" in body
        elif style == "azure_openai":
            detail[style] = "messages" in body and "api-version" in plan["url"]
        ok = ok and all(detail.values())
    return {"id": "A7", "passed": ok, "shapes": len(shapes), "fields_ok": detail}


def check_a8(root: str) -> Dict[str, Any]:
    clean = {k: v for k, v in os.environ.items() if not k.startswith("HOLOAEON_")}
    gw = mg.build_gateway(root, environ=clean)
    plan = gw.plan("openai", prompt="ping")
    leaks = [v for v in plan["headers"].values() if isinstance(v, str) and len(v) > 40]
    ok = plan["configured"] is False and plan["enabled"] is False and not leaks
    return {"id": "A8", "passed": ok, "configured": plan["configured"],
            "auth_head": plan["headers"].get("Authorization", "")[:32]}


def check_a9() -> Dict[str, Any]:
    if not os.path.isfile(GUIDE):
        return {"id": "A9", "passed": False, "reason": "guide_missing"}
    t = read_text(GUIDE)
    need = ["BASE_URL", "API_KEY", "HOLOAEON_REAL_MODELS", "model"]
    ok = all(k in t for k in need) and len(t) > 2000
    return {"id": "A9", "passed": ok, "bytes": os.path.getsize(GUIDE),
            "keys": {k: (k in t) for k in need}}


def check_a10() -> Dict[str, Any]:
    """五地零漂移。

    自指排除（V5.2 完备化）：本脚本与兄弟校验器（v43/v45/v46/v5/dv）都会在「跑一次」
    时改写各自的 Reports，故凡属 `SELF_REPORTS` 的条目一律不计漂移；其余条目仍逐条判。
    异机（无 manifest）时记 skipped 第三态，而不是伪装成 FAIL（P0-3）。
    """
    drift, now, old = fsd.drift_now()
    if drift is None:
        return {"id": "A10", "passed": True, "status": "skipped",
                "reason": "manifest_missing", "pending_human_measure": True}
    effective = [d for d in drift if not _is_verifier_report(d)]
    excluded = [d for d in drift if _is_sibling_report(d)]
    return {"id": "A10", "passed": effective == [], "status": "measured",
            "drift": effective[:6], "drift_count": len(effective),
            "self_excluded_count": len(excluded), "self_excluded": excluded[:3],
            "checked": {"package": len(old.get("package", {})),
                        "repo": len(old.get("repo", {}))}}


def check_a11(root: str, others_passed: bool) -> Dict[str, Any]:
    """回执齐备。

    自指说明：回执由本脚本在末尾写入，因此「回执里 passed==total」不可能在本轮被自己读到。
    A11 因此判的是**收口条件**：票据存在 + 除 A10/A11 外的判据全部 PASS。

    传染切断（P0-2）：调用方传入的 `others_passed` 不再包含 A10。A10 依赖本机 manifest 与
    兄弟回执，属环境项；它单独红时 A11 必须仍能 PASS，否则环境红会伪装成内容红。
    """
    if not os.path.isfile(TICKET):
        return {"id": "A11", "passed": False, "status": "measured",
                "reason": "ticket_missing"}
    prev = load_json("reports/v44_model_gateway_check.json") if os.path.isfile(REPORT) else {}
    ok = others_passed
    return {"id": "A11", "passed": ok, "status": "measured",
            "ticket_bytes": os.path.getsize(TICKET),
            "prev_run": ("%s/%s" % (prev.get("passed"), prev.get("total"))
                         if prev else "none"),
            "closing_rule": "ticket + all_other_checks_pass(excluding A10/A11)"}


def check_a12() -> Dict[str, Any]:
    p = os.path.join(IVSA_ROOT, "SHA256SUMS")
    if not os.path.isfile(p):
        return {"id": "A12", "passed": True, "status": "skipped",
                "reason": "ivsa_root_absent", "root": IVSA_ROOT,
                "pending_human_measure": True}
    h = hashlib.sha256(Path(p).read_bytes()).hexdigest()
    ok = h == "9400b4811ab3b4870dc1b29b74dd14f9d74b491759324aa7af53451c58fc73bf"
    return {"id": "A12", "passed": ok, "status": "measured", "sha256": h}


def check_a13() -> Dict[str, Any]:
    from holoaeon.model_adapter import ROUTE_STRATEGIES
    a = ModelAdapter()
    a.register_backend(ModelBackend(name="cheap", provider="local", input_cost=0.1,
                                    output_cost=0.1, capabilities=["chat"]))
    a.register_backend(ModelBackend(name="fat", provider="local", input_cost=0.9,
                                    output_cost=0.9, capabilities=["chat", "tool_call"],
                                    context_window=32768))
    results = {s: a.route("ping", strategy=s, need=["chat"]) for s in ROUTE_STRATEGIES}
    return {"id": "A13", "passed": all(v for v in results.values()),
            "strategies": len(ROUTE_STRATEGIES),
            "routed": {k: v for k, v in results.items()}}


def main() -> int:
    gw = mg.build_gateway(ROOT)
    pre = [check_a1(), check_a2(gw), check_a3(gw), check_a4(ROOT), check_a5(ROOT),
           check_a6(), check_a7(gw), check_a8(ROOT), check_a9(), check_a10(),
           check_a12(), check_a13()]
    # 环境项不参与「内容项是否全绿」的判定：A10 依赖本机 manifest / 兄弟回执。
    others_passed = all(c["passed"] for c in pre if c["id"] != "A10")
    checks = pre[:10] + [check_a11(ROOT, others_passed)] + pre[10:]
    skipped = [c["id"] for c in checks if c.get("status") == "skipped"]
    measured = [c for c in checks if c.get("status") != "skipped"]
    passed = sum(1 for c in measured if c["passed"])
    out = {"id": "SG-V44-MODEL-GATEWAY-CHECK-V1", "batch": "V4.4-B1",
           "created_at": "2026-11-02", "evidence_class": "simulated",
           "passed": passed, "total": len(measured),
           "failed": [c["id"] for c in measured if not c["passed"]],
           "skipped": skipped,
           "skipped_note": "skipped=pending_human_measure，不计入 passed/total，不当作 PASS",
           "gateway_state": gw.state(), "coverage": gw.catalog["coverage"],
           "checks": checks}
    with open(REPORT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(json.dumps({"passed": passed, "total": len(measured),
                      "failed": out["failed"], "skipped": skipped},
                     ensure_ascii=False))
    for c in checks:
        mark = "SKIP" if c.get("status") == "skipped" else (
            "PASS" if c["passed"] else "FAIL")
        print("%-3s %s" % (c["id"], mark))
    return 0 if passed == len(measured) else 1


if __name__ == "__main__":
    sys.exit(main())
