# -*- coding: utf-8 -*-
"""V4.6 校验：扩展卡槽 + 协作开发/按流程使用说明 + 升级空间。

C1 卡槽声明存在且 schema 合规（validate 无错误）
C2 槽 id 唯一、全部 EXT- 前缀、kind/status 在白名单内
C3 每个槽都有 owner / contract / next_action（无人认领必须显式写"未认领"）
C4 维度锁未变：25 智能体 / 47 技能 / 9 包（卡槽不得改锁数）
C5 卡槽只声明不接线：干净环境 gateway enabled=[]，且槽文件无 credential 字样
C6 文档齐：协作开发指南存在，且每个槽 id 都被文档提到（不留空槽无人知）
C7 无公网地址：槽声明的 contract/next_action/notes 不得出现非本地 http(s)
C8 模块红线：slot_registry.py 不 import 网络/子进程模块、不用 eval/exec（AST 静态检查）
C9 五地清单覆盖：卡槽与说明文档已登记在 REPO_FILES（防"文件写了但没进清单"）

只读；不写任何文件。退出码 0/1。
"""
from __future__ import annotations

import ast
import json
import os
import sys
from typing import Any, Dict, List

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from holoaeon.fusion_upgrade import slot_registry as sr  # noqa: E402
from holoaeon.fusion_upgrade.model_gateway import build_gateway  # noqa: E402

DOCS = os.path.join(ROOT, "docs", "扩展卡槽与协作开发指南.md")
MODULE = os.path.join(ROOT, "holoaeon", "fusion_upgrade", "slot_registry.py")
FORBIDDEN_IMPORTS = {"urllib", "urllib3", "requests", "socket", "http", "aiohttp",
                     "httpx", "subprocess", "http.client"}
FORBIDDEN_CALLS = {"eval", "exec", "compile", "__import__", "os.system", "popen"}


def main() -> int:
    checks: List[Dict[str, Any]] = []

    def add(cid: str, ok: bool, detail: Any) -> None:
        checks.append({"id": cid, "passed": bool(ok), "detail": detail})

    payload: Dict[str, Any] = {}
    try:
        payload = sr.load(ROOT)
    except Exception as exc:  # noqa: BLE001
        payload = {}
        err_note = repr(exc)
    else:
        err_note = ""

    errors = sr.validate(payload) if payload else ["卡槽文件缺失或不可解析: " + err_note]
    add("C1", not errors, {"errors": errors, "path": os.path.relpath(sr.slot_path(ROOT), ROOT)})

    slots = payload.get("slots") or []
    ids = [s.get("slot_id") for s in slots]
    add("C2", bool(slots) and len(ids) == len(set(ids)
                                     ) and all(str(i).startswith("EXT-") for i in ids),
        {"count": len(slots), "unique": len(set(ids))})

    missing = [s.get("slot_id") for s in slots
               if not (s.get("owner") and s.get("contract") and s.get("next_action"))]
    add("C3", not missing, {"missing": missing, "owners_unclaimed": sum(
        1 for s in slots if s.get("owner") == "未认领")})

    lock = payload.get("lock") or {}
    add("C4", lock.get("agents") == 25 and lock.get("skills") == 47 and lock.get("packs") == 9,
        {"lock": {k: lock.get(k) for k in ("agents", "skills", "packs")}})

    clean = {k: v for k, v in os.environ.items() if not k.startswith("HOLOAEON_")}
    gw = build_gateway(ROOT, environ=clean)
    blob = json.dumps(payload, ensure_ascii=False)
    add("C5", gw.state()["enabled"] == [] and "sk-" not in blob and "api_key\":" not in blob,
        {"enabled_clean": gw.state()["enabled"]})

    doc_ok = os.path.isfile(DOCS)
    doc_text = ""
    if doc_ok:
        with open(DOCS, encoding="utf-8") as f:
            doc_text = f.read()
    uncovered = [i for i in ids if i not in doc_text]
    add("C6", doc_ok and not uncovered,
        {"doc": os.path.relpath(DOCS, ROOT) if doc_ok else None,
         "chars": len(doc_text), "uncovered_slots": uncovered})

    pub = []
    for s in slots:
        for field in ("contract", "next_action", "notes"):
            text = s.get(field) or ""
            if sr._has_public_url(text):
                pub.append("%s.%s" % (s.get("slot_id"), field))
    add("C7", not pub, {"public_url_fields": pub})

    bad_imports: List[str] = []
    bad_calls: List[str] = []
    with open(MODULE, "rb") as f:
        tree = ast.parse(f.read().decode("utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name.split(".")[0] in FORBIDDEN_IMPORTS:
                    bad_imports.append(a.name)
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] in FORBIDDEN_IMPORTS:
                bad_imports.append(node.module or "")
        elif isinstance(node, ast.Call):
            fn = node.func
            name = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", "")
            if name in FORBIDDEN_CALLS:
                bad_calls.append(name)
    add("C8", not bad_imports and not bad_calls,
        {"bad_imports": bad_imports, "bad_calls": bad_calls,
         "module": os.path.relpath(MODULE, ROOT)})

    import five_site_dna as dna  # noqa: E402
    need = ["data/extension_slots.json",
            "holoaeon/fusion_upgrade/slot_registry.py",
            "docs/扩展卡槽与协作开发指南.md",
            "scripts/verify_v46.py",
            "tests_contract/test_v46.py"]
    absent = [p for p in need if p not in dna.REPO_FILES]
    add("C9", not absent, {"missing_in_manifest": absent, "repo_files": len(dna.REPO_FILES)})

    passed = sum(1 for c in checks if c["passed"])
    out = {"id": "SG-V46-SLOT-CHECK-V1", "passed": passed, "total": len(checks),
           "failed": [c["id"] for c in checks if not c["passed"]],
           "verdict": "PASS" if passed == len(checks) else "FAIL",
           "summary": sr.summary(payload) if payload else {},
           "checks": checks}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    if "--json" in sys.argv:
        dest = sys.argv[sys.argv.index("--json") + 1]
        dest = dest if os.path.isabs(dest) else os.path.join(ROOT, dest)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w", encoding="utf-8", newline="\n") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
            f.write("\n")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
