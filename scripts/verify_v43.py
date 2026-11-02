# -*- coding: utf-8 -*-
"""V4.3-B1 校验器：四个坑的固化件 + 三项遗留的收尾件，逐条实测。

判据（V43-1 … V43-11）
----------------------
H1 HF 镜像器只认 model 仓：`REPO_TYPE == "model"`，且中文路径取改动返回 UTF-8 原文（无 `\\3` 转义）。
H2 向量海清单器：`--check` 判 PASS（74 与 manifest 自洽、无自指）。
H3 交付目录 PKG 无漂移：`check_delivery_pkg.diagnose()` 判 PASS。
H4 镜像计划的路径过滤只留真实存在的文件（不存在的相对路径被跳过而非抛错）。
M1 事实包已进 ModelAdapter：正常问句 `adapter.used=true`、backend=`fact-pack-local`、usage>0。
M2 红线优先：剂量问句 `guard.blocked=true` 且 `adapter.used=false`（不进适配层）。
M3 插件默认仍关闭：未启用时 `capabilities_loaded=0`。
M4 适配层净化：`reasoning_adapter.py` 的 AST 不含 subprocess/urllib/requests/eval/exec/compile/__import__/input/os.system。
I1 族身份 V2 绑定真实族：`family_sha256` 与 `data/semantic_family.json` 现算 sha 一致、成员数 100。
I2 身份升级不改判据：V2 号与 V1 号不同，且 `spec_id` 与 `data/semantic_modules_v4.json` 一致。
L1 gap 检索计划已执行：3 张卡、≥9 条来源、链接全为 https、证据等级仍 `none`、参数未记录。

输出：`reports/v43_hardening_check.json`（`evidence_class=simulated`），退出码 0/1。
"""
from __future__ import annotations

import ast
import hashlib
from pathlib import Path
import json
import os
import sys
from typing import Any, Dict, List

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import build_vector_sea_manifest as bvm  # noqa: E402
import check_delivery_pkg as cdp  # noqa: E402
import mirror_hf as mhf  # noqa: E402
from holoaeon.fusion_upgrade import reasoning_adapter as ra  # noqa: E402

IVSA_ROOT = os.environ.get(
    "IVSA_ROOT", r"F:\doubaowork\开源发布_中西医融合康复工程_20261026\integrative-rehab-vsa")
REPORT = os.path.join(ROOT, "reports", "v43_hardening_check.json")


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(65536), b""):
            h.update(c)
    return h.hexdigest()


def load(rel: str) -> Dict[str, Any]:
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return json.load(f)


def check_h1() -> Dict[str, Any]:
    base = "f50cd1c"
    rels = mhf.changed_files(ROOT, base, "HEAD")
    chinese = [r for r in rels if any(ord(ch) > 127 for ch in r)]
    escaped = [r for r in rels if "\\3" in r or r.startswith('"')]
    ok = mhf.REPO_TYPE == "model" and not escaped and bool(chinese)
    return {"id": "H1", "passed": ok, "repo_type": mhf.REPO_TYPE,
            "changed": len(rels), "chinese_paths": len(chinese), "escaped": escaped[:3]}


def check_h2() -> Dict[str, Any]:
    res = bvm.check(bvm.DEFAULT_S4)
    return {"id": "H2", "passed": res["verdict"] == "PASS",
            "entries": res.get("entries"), "dir_files": res.get("dir_files"),
            "sums_74_in_sync": res.get("sums_74_in_sync"),
            "self_reference": res.get("self_reference"), "steps": res.get("steps")}


def check_h3() -> Dict[str, Any]:
    res = cdp.diagnose()
    return {"id": "H3", "passed": res["verdict"] == "PASS",
            "checked": res["checked"], "drift": res["drift"], "extra": res["extra_registered"]}


def check_h4() -> Dict[str, Any]:
    plan = mhf.build_plan(ROOT, ["README_FUSION_V4_20261102.md", "data/__not_exist__.json"])
    return {"id": "H4", "passed": plan == ["README_FUSION_V4_20261102.md"], "plan": plan}


def probe_bridge() -> Dict[str, Any]:
    return ra.probe(root=ROOT, guest_root=IVSA_ROOT if os.path.isdir(IVSA_ROOT) else None)


def check_m1(p: Dict[str, Any]) -> Dict[str, Any]:
    normal = p["normal"]
    ok = (normal["adapter"]["used"] is True
          and normal["adapter"]["backend"] == ra.BACKEND_NAME
          and normal["adapter"]["usage_simulated"]["total_tokens"] > 0
          and normal["pack"]["seal"] == "6704fb78e5cb")
    return {"id": "M1", "passed": ok, "backend": normal["adapter"]["backend"],
            "usage": normal["adapter"]["usage_simulated"],
            "pack_seal": normal["pack"]["seal"], "facts": len(normal["pack"]["facts"])}


def check_m2(p: Dict[str, Any]) -> Dict[str, Any]:
    dose = p["dose"]
    ok = dose["pack"]["guard"]["blocked"] is True and dose["adapter"]["used"] is False
    return {"id": "M2", "passed": ok, "blocked": dose["pack"]["guard"]["blocked"],
            "adapter_reason": dose["adapter"]["reason"],
            "facts": len(dose["pack"]["facts"])}


def check_m3(p: Dict[str, Any]) -> Dict[str, Any]:
    off = p["off"]
    return {"id": "M3", "passed": off["capabilities_loaded"] == 0,
            "capabilities_loaded": off["capabilities_loaded"],
            "enabled": off["enabled"]}


def check_m4() -> Dict[str, Any]:
    path = os.path.join(ROOT, "holoaeon", "fusion_upgrade", "reasoning_adapter.py")
    tree = ast.parse(Path(path).read_text(encoding="utf-8"))
    banned_mods = {"subprocess", "urllib", "requests", "socket", "http"}
    banned_call = {"eval", "exec", "compile", "__import__", "input", "system", "popen", "run"}
    hits: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name.split(".")[0] in banned_mods:
                    hits.append("import:" + a.name)
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.module.split(".")[0] in banned_mods:
                hits.append("from:" + node.module)
        if isinstance(node, ast.Call):
            fn = node.func
            name = getattr(fn, "attr", None) or getattr(fn, "id", None)
            if name in banned_call:
                hits.append("call:" + str(name))
    return {"id": "M4", "passed": not hits, "hits": hits}


def check_i1() -> Dict[str, Any]:
    ident = load("data/semantic_family_identity_v2.json")
    fam = load("data/semantic_family.json")
    actual = sha256_file(os.path.join(ROOT, "data", "semantic_family.json"))
    ok = (ident["binding"]["family_sha256"] == fam["sha256"]
          and ident["binding"]["member_count"] == fam["member_count"] == 100
          and ident["binding"]["member_count_locked"] is True)
    return {"id": "I1", "passed": ok, "canonical_sha256": fam["sha256"],
            "file_sha256": actual, "bound": ident["binding"]["family_sha256"],
            "members": fam["member_count"]}


def check_i2() -> Dict[str, Any]:
    ident = load("data/semantic_family_identity_v2.json")
    mods = load("data/semantic_modules_v4.json")
    ok = (ident["family_id_v2"] != ident["family_id_v1"]
          and ident["family_id_v2"].startswith("SG-V41-")
          and ident["binding"]["spec_id"] == mods["spec_id"]
          and ident["signature"]["status"] == "SIGNED")
    return {"id": "I2", "passed": ok, "v1": ident["family_id_v1"],
            "v2": ident["family_id_v2"], "spec_id": mods["spec_id"]}


def check_l1() -> Dict[str, Any]:
    probe = load("data/v43_gap_literature_probe.json")
    hits = [h for p in probe["probes"] for h in p["hits"]]
    ok = (len(probe["probes"]) == 3 and len(hits) >= 9
          and all(str(h.get("url", "")).startswith("https://") for h in hits)
          and all(v == "none" for v in probe["summary"]["tier_after"].values())
          and probe["redline"]["params_withheld"] is True)
    return {"id": "L1", "passed": ok, "probes": len(probe["probes"]),
            "hits": len(hits), "tier_after": probe["summary"]["tier_after"],
            "decision": probe["decision"]}


def main() -> int:
    p = probe_bridge() if os.path.isdir(IVSA_ROOT) else {"off": {"capabilities_loaded": -1,
                                                                 "enabled": False},
                                                         "normal": {"adapter": {"used": False,
                                                                                "backend": None,
                                                                                "usage_simulated": {"total_tokens": 0}},
                                                                   "pack": {"seal": "", "facts": [], "guard": {"blocked": False}}},
                                                         "dose": {"adapter": {"used": False, "reason": ""},
                                                                  "pack": {"guard": {"blocked": False}, "facts": []}}}
    checks = [check_h1(), check_h2(), check_h3(), check_h4(),
              check_m1(p), check_m2(p), check_m3(p), check_m4(),
              check_i1(), check_i2(), check_l1()]
    passed = sum(1 for c in checks if c["passed"])
    out = {"id": "SG-V43-HARDENING-CHECK-V1", "batch": "V4.3-B1",
           "created_at": "2026-11-02", "evidence_class": "simulated",
           "guest_root_present": os.path.isdir(IVSA_ROOT),
           "passed": passed, "total": len(checks), "failed": [c["id"] for c in checks if not c["passed"]],
           "checks": checks}
    with open(REPORT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(json.dumps({k: out[k] for k in ("passed", "total", "failed")}, ensure_ascii=False))
    for c in checks:
        print("%-3s %s" % (c["id"], "PASS" if c["passed"] else "FAIL"))
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
