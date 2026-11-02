# -*- coding: utf-8 -*-
"""B8 只读校验器：V1–V10 逐条断言，落 reports/b8_dual_sync_check.json。

用法：
  python scripts/verify_b8_dual_sync.py
"""
from __future__ import annotations

import ast
import csv
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from holoaeon.fusion_upgrade import dual_sync as DS  # noqa: E402

IVSA_ROOT = r"F:\doubaowork\开源发布_中西医融合康复工程_20261026\integrative-rehab-vsa"
DATA = os.path.join(ROOT, "data")
REPORTS = os.path.join(ROOT, "reports")
PKG = os.path.join(ROOT, "holoaeon", "fusion_upgrade")


def _load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    desc = _load(os.path.join(DATA, "ivsa_plugin_v1.2.json"))
    doc = _load(os.path.join(DATA, "dual_repo_sums.json"))
    with open(os.path.join(DATA, "许可分层清单.csv"), "r", encoding="utf-8", newline="") as f:
        layers = list(csv.DictReader(f))
    sums_text = ""
    sums_path = os.path.join(ROOT, "SHA256SUMS")
    if os.path.isfile(sums_path):
        with open(sums_path, "r", encoding="utf-8") as f:
            sums_text = f.read()
    ivsa_text = ""
    ivsa_sums = os.path.join(IVSA_ROOT, "SHA256SUMS")
    if os.path.isfile(ivsa_sums):
        with open(ivsa_sums, "r", encoding="utf-8") as f:
            ivsa_text = f.read()

    checks = []

    def add(cid, ok, detail):
        checks.append({"id": cid, "ok": bool(ok), "detail": detail})

    add("V1", desc.get("plugin_id") == DS.PLUGIN_ID and desc.get("version") == "1.2"
        and desc.get("enabled_by_default") is False
        and desc.get("requires_explicit_enable") is True,
        {"plugin_id": desc.get("plugin_id"), "enabled_by_default": desc.get("enabled_by_default")})

    off = DS.load_plugin()
    on = DS.load_plugin(enable=True)
    add("V2", off["state"] == "disabled" and off["capabilities_loaded"] == 0
        and on["state"] == "enabled" and on["capabilities_loaded"] == len(DS.CAPABILITIES),
        {"off": off["state"], "on_loaded": on["capabilities_loaded"]})

    add("V3", desc.get("dimension_contract") == {"agents": 25, "skills": 47, "packs": 9},
        desc.get("dimension_contract"))

    v = DS.verify_sums(ROOT, sums_text) if sums_text else {"ok": False, "checked": 0}
    v["extra"] = []  # 同仓受管目录已全量入清单，extra 仅用于跨仓
    add("V4", v["ok"] and v["checked"] >= 150 and not v["missing"] and not v["bad_sha256"],
        {"checked": v["checked"], "missing": len(v["missing"]), "bad": len(v["bad_sha256"])})

    iv = DS.verify_sums(IVSA_ROOT, ivsa_text) if ivsa_text else {"ok": False, "checked": 0}
    add("V5", iv["ok"] and iv["checked"] >= 90 and not iv["missing"] and not iv["bad_sha256"],
        {"checked": iv["checked"], "missing": len(iv["missing"]), "bad": len(iv["bad_sha256"])})

    iface = DS.interface_check(os.path.join(ROOT, DS.INTERFACE["holo"]),
                               os.path.join(IVSA_ROOT, DS.INTERFACE["ivsa"]))
    add("V6", iface["equal"] and iface["total_holo"] == 17 and len(iface["groups_ivsa"]) == 4,
        {"groups": iface["groups_holo_mapped"], "total": iface["total_holo"]})

    mixed = DS.license_mixed(layers)
    add("V7", len(layers) >= 5 and not mixed
        and {r["license"] for r in layers} <= {"Apache-2.0", "MPL-2.0", "data-only"},
        {"rows": len(layers), "mixed": mixed})

    bad_imports = []
    for dirpath, _dirs, names in os.walk(PKG):
        for name in names:
            if not name.endswith(".py"):
                continue
            path = os.path.join(dirpath, name)
            with open(path, "r", encoding="utf-8") as f:
                src = f.read()
            for node in ast.walk(ast.parse(src)):
                mods = []
                if isinstance(node, ast.Import):
                    mods = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    mods = [node.module]
                for m in mods:
                    if "ivsa" in m.lower() or "integrative" in m.lower():
                        bad_imports.append(os.path.relpath(path, ROOT) + ":" + m)
    add("V8", not bad_imports, {"ivsa_imports": bad_imports})

    recomputed = DS.sums_digest([l for l in sums_text.splitlines() if l.strip()])
    add("V9", recomputed == doc["holoaeon"]["sums_sha256"]
        and DS.parse_sums(sums_text) and len(DS.parse_sums(sums_text)) == doc["holoaeon"]["entries"],
        {"recomputed": recomputed, "recorded": doc["holoaeon"]["sums_sha256"]})

    names = {n for _d, n in DS.parse_sums(sums_text)}
    add("V10", "SHA256SUMS" not in names and "data/dual_repo_sums.json" not in names,
        {"self_ref": sorted(n for n in names if n in DS.SUMS_EXCLUDES)})

    try:
        DS.resolve_capability("not_a_capability")
        rejected = False
    except KeyError:
        rejected = True
    add("V11", rejected, {"unknown_capability_rejected": rejected})

    passed = sum(1 for c in checks if c["ok"])
    total = len(checks)
    result = {
        "check_id": "SG-B8-DUAL-SYNC-CHECK-V1",
        "batch": DS.BATCH,
        "evidence_class": DS.EVIDENCE_CLASS,
        "passed": passed,
        "total": total,
        "failed": [c["id"] for c in checks if not c["ok"]],
        "checks": checks,
        "verdict": "PASS" if passed == total else "FAIL",
    }
    with open(os.path.join(REPORTS, "b8_dual_sync_check.json"), "w", encoding="utf-8",
              newline="\n") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps({"verdict": result["verdict"], "passed": passed, "total": total,
                      "failed": result["failed"]}, ensure_ascii=False))
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
