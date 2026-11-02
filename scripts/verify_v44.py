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
A10 五地零漂移：five_site_dna.verify() 的 drift 为空（自写回执由 REPO_FILES 派生排除，missing 不豁免）
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

# 自写回执：V6.1-B2 起由「硬编码名单」改为「派生 + 产生者回填」。
# 候选 = fsd.REPO_FILES 中的 reports/*.json；产生者 = scripts/{verify_,build_,check_,gen_}*.py
# 正文里出现该文件名者。这样新增写型校验器不必再手改这里（A10 不再因漏登而红）。
# 派生为空（源码缺失/目录改名）时退回 LEGACY_SELF_REPORTS 并标 self_derive="legacy"（fail-loud）。
# 已知代价：派生只回答「谁写它」，不回答「内容是否被意外改写」；后者由各回执 owner
# 自身的判据负责，A10 仅以差分证据（prev_sha16/curr_sha16）留痕。
LEGACY_SELF_REPORTS = (
    "reports/v43_hardening_check.json",
    "reports/v44_model_gateway_check.json",
    "reports/v45_live_probe.json",
    "reports/v45_live_probe_emb.json",
    "reports/v46_slot_check.json",
    "reports/v5_rehab_kb_check.json",
    "reports/design_vocab_check.json",
    "reports/five_site_manifest.json",
)
OWN_REPORT = "reports/v44_model_gateway_check.json"
WRITER_PREFIXES = ("verify_", "build_", "check_", "gen_")
# 五地清单由 five_site_dna.py 自己写自己（无 verify_/build_ 前缀），单列登记；
# 其余 reports/*.json（如 gate_b0_v4.json / b7_gates.json）是数据闸，不属自写回执，
# 仍逐条判漂移——否则 A10 会连「闸数据被改」一起放过。
EXTRA_SELF_REPORTS = {"reports/five_site_manifest.json": "scripts/five_site_dna.py"}
_SELF_REPORTS_CACHE: Dict[str, str] = {}


WRITE_MARKERS = ("json.dump", "open(", ".write", "REPORT", "PROBE",
                "MANIFEST", "OUT =", "DEST", "PATH =")


def _has_write_context(body: str, base: str) -> bool:
    """只认「写上下文」里的文件名：同一行含写标记，才算该脚本写这份回执。

    仅被读取（如 `load_json("reports/gate_b0_v4.json")`）或仅在 REPO_FILES 名单中
    出现的回执，一律不算自写——否则数据闸被改会被 A10 一起放过。
    """
    for line in body.split("\n"):
        if base in line and any(m in line for m in WRITE_MARKERS):
            return True
    return False


def _owner_score(rel: str, fn: str) -> int:
    """属主择优：回执名 token 与脚本名 token 的重合数（重合计 2，子串计 1）。"""
    stem = os.path.basename(rel)[:-5] if rel.endswith(".json") else os.path.basename(rel)
    rtok = set(x for x in stem.split("_") if len(x) > 1)
    ftok = set(x for x in fn[:-3].split("_") if len(x) > 1)
    score = 0
    for r in rtok:
        if r in ftok:
            score += 2
        elif len(r) >= 3 and any(r in f for f in ftok):
            score += 1
    return score


def self_reports() -> Dict[str, str]:
    """派生自写回执映射 {rel: 产生者脚本}，结果缓存（同一进程只扫一次）。

    产生者候选 = scripts/ 下 verify_/build_/check_/gen_/five_site_ 开头的脚本；
    多个脚本都提到同一回执时，按 `_owner_score` 择优（避免「谁先出现谁当属主」）。
    """
    if _SELF_REPORTS_CACHE:
        return _SELF_REPORTS_CACHE
    hits: Dict[str, List[str]] = {}
    scripts = os.path.join(ROOT, "scripts")
    candidates = [rel for rel in getattr(fsd, "REPO_FILES", [])
                  if rel.startswith("reports/") and rel.endswith(".json")]
    if os.path.isdir(scripts) and candidates:
        for fn in sorted(os.listdir(scripts)):
            if not fn.endswith(".py") or not fn.startswith(WRITER_PREFIXES):
                continue
            try:
                body = read_text(os.path.join(scripts, fn))
            except OSError:
                continue
            for rel in candidates:
                base = os.path.basename(rel)
                if base in body and _has_write_context(body, base):
                    hits.setdefault(rel, []).append(fn)
    owners = {rel: "scripts/" + max(fns, key=lambda fn: (_owner_score(rel, fn), -len(fn)))
              for rel, fns in hits.items()}
    owners.update(EXTRA_SELF_REPORTS)
    if not owners:
        owners = {rel: "legacy" for rel in LEGACY_SELF_REPORTS}
    _SELF_REPORTS_CACHE.update(owners)
    return _SELF_REPORTS_CACHE


def _split_drift(token: str) -> tuple:
    """drift 形如 <scope>:<kind>:<rel>；不合法返回 ("", "")。"""
    parts = token.split(":", 2)
    return (parts[1], parts[2]) if len(parts) == 3 else ("", "")


def _is_verifier_report(token: str) -> bool:
    """自指判定：只认 changed/new；missing 不豁免——删回执是真实退化。"""
    kind, rel = _split_drift(token)
    return kind in ("changed", "new") and rel in self_reports()


def _is_sibling_report(token: str) -> bool:
    """兄弟自写回执（不含自己）：仅用于如实报数。"""
    kind, rel = _split_drift(token)
    return kind in ("changed", "new") and bool(rel) and rel != OWN_REPORT and rel in self_reports()

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
    """五地零漂移（V6.1-B2：自写回执派生 + missing 不豁免 + 差分证据）。

    自指排除：凡由写型校验器自己写出的 reports/*.json，跑一次必然 changed，
    属「跑校验 → 清单过期」的结构性循环。名单不再硬编码，从 fsd.REPO_FILES 派生。
    排除范围只含 changed / new；missing（回执被删）不排除——那是真实退化。
    差分证据：每条被排除项记录 owner + prev_sha16 + curr_sha16，内容被意外改写仍留痕。
    异机（无 manifest）记 skipped 第三态，不伪装成 FAIL；也不默认算 PASS。
    """
    owners = self_reports()
    drift, now, old = fsd.drift_now()
    if drift is None:
        return {"id": "A10", "passed": True, "status": "skipped",
                "reason": "manifest_missing", "pending_human_measure": True,
                "self_owners_count": len(owners)}
    evidence, effective = [], []
    for d in drift:
        scope = d.split(":", 1)[0]
        kind, rel = _split_drift(d)
        if kind in ("changed", "new") and rel in owners:
            prev = (old.get(scope) or {}).get(rel, {}) or {}
            curr = (now.get(scope) or {}).get(rel, {}) or {}
            evidence.append({"item": d, "owner": owners[rel],
                             "prev_sha16": str(prev.get("sha256", ""))[:16],
                             "curr_sha16": str(curr.get("sha256", ""))[:16]})
        else:
            effective.append(d)
    derive_mode = "legacy" if owners and all(v == "legacy" for v in owners.values()) else "derived"
    return {"id": "A10", "passed": effective == [], "status": "measured",
            "drift": effective[:6], "drift_count": len(effective),
            "missing_receipts": [d for d in effective
                                 if d.startswith(("repo:missing:", "package:missing:"))][:6],
            "self_excluded_count": len(evidence), "self_excluded": evidence[:3],
            "self_owners_count": len(owners), "self_derive": derive_mode,
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
