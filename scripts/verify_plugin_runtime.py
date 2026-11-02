# -*- coding: utf-8 -*-
"""V4.1-B1 校验器：B8 六项插件接实际推理（V1-V10）。

  python scripts/verify_plugin_runtime.py            # 人类可读
  python scripts/verify_plugin_runtime.py --json     # 机器可读
退出码 0 = 全绿。

判据（全部可跑）：
V1  默认态：enabled_by_default=false、requires_explicit_enable=true、capabilities_loaded=0
V2  密令门禁：空串与近似串被拒；`潮起开门` 与插件 seal 均可启用
V3  启用后六项全加载，能力 id 严格等于插件声明的 6 项
V4  六项行数 = 客仓实测 17/70/11/7/20/147，且 expected 与实测一致
V5  只读：探针前后客仓六件字节摘要不变
V6  无越界：plugin_runtime.py 不 import ivsa、不含 subprocess/urllib/requests/eval/exec/compile
V7  维度契约：插件声明 25/47/9，Kernel 现算锁值同为 25/47/9
V8  推理桥可复算：同一问句两次同封缄，且路由命中通道能力、事实包行数=17
V9  红线闸：剂量问句被 blocked、事实包为空、不返回任何数字剂量
V10 证据等级：三处输出 evidence_class 均为 simulated，事实包不含疗效/诊断结论字段
"""
from __future__ import annotations

import ast
import hashlib
from pathlib import Path
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from holoaeon.fusion_upgrade import plugin_runtime as PR  # noqa: E402
from holoaeon.fusion_upgrade.snapshot import _locks  # noqa: E402

DATA = os.path.join(ROOT, "data")
REPORTS = os.path.join(ROOT, "reports")
IVSA_ROOT = r"F:\doubaowork\开源发布_中西医融合康复工程_20261026\integrative-rehab-vsa"
GUEST_DATA = os.path.join(IVSA_ROOT, "data")
OUT = os.path.join(REPORTS, "v41_plugin_runtime_check.json")

EXPECTED_ROWS = {
    "channel_groups_17": 17,
    "heartbeat_70_registry": 70,
    "rehab_organs_11": 11,
    "chronic_diseases_7": 7,
    "rehab_cases_20": 20,
    "capability_dimensions_147": 147,
}
GUEST_FILES = {
    "channel_groups_17": "meridian_channels_17.csv",
    "heartbeat_70_registry": "heartbeat_70_registry.csv",
    "rehab_organs_11": "rehab_organs_11.csv",
    "chronic_diseases_7": "chronic_diseases_7.csv",
    "rehab_cases_20": "rehab_cases_20.csv",
    "capability_dimensions_147": "capability_dimensions_147.csv",
}


def _sha16(path: str) -> str:
    if not os.path.isfile(path):
        return ""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:16]


def main(argv) -> int:
    as_json = "--json" in argv
    checks = []
    failed = []

    def add(cid, ok, detail):
        checks.append({"id": cid, "ok": bool(ok), "detail": detail})
        if not ok:
            failed.append(cid)

    before = {cid: _sha16(os.path.join(GUEST_DATA, name))
              for cid, name in GUEST_FILES.items()}

    runtime = PR.PluginRuntime.load(root=ROOT, guest_root=IVSA_ROOT)
    off = runtime.resolve_all()

    # V1
    plugin = runtime.plugin
    add("V1", plugin.get("enabled_by_default") is False
        and plugin.get("requires_explicit_enable") is True
        and off["capabilities_loaded"] == 0 and off["enabled"] is False,
        {"enabled_by_default": plugin.get("enabled_by_default"),
         "requires_explicit_enable": plugin.get("requires_explicit_enable"),
         "loaded": off["capabilities_loaded"]})

    # V2
    bad_empty = runtime.enable("")
    bad_near = runtime.enable("潮起开门 ")
    ok_seal = runtime.enable(str(plugin.get("seal", "")))
    add("V2", bad_empty.get("reason") == "secret_mismatch"
        and bad_near.get("reason") == "secret_mismatch" and ok_seal.get("ok") is True,
        {"empty": bad_empty.get("reason"), "near": bad_near.get("reason"),
         "seal": ok_seal.get("ok")})

    on = runtime.resolve_all()

    # V3
    declared = runtime.declared_capabilities()
    add("V3", on["capabilities_loaded"] == 6 and on["capabilities_declared"] == 6
        and set(declared) == set(runtime.capability_ids()),
        {"loaded": on["capabilities_loaded"], "declared": on["capabilities_declared"],
         "ids": declared})

    # V4
    rows = {r["capability"]: r["rows"] for r in on["results"]}
    matched = all(r.get("matched") for r in on["results"])
    add("V4", matched and rows == EXPECTED_ROWS, {"rows": rows,
                                                   "expected": EXPECTED_ROWS,
                                                   "matched": matched})

    # V5
    after = {cid: _sha16(os.path.join(GUEST_DATA, name))
             for cid, name in GUEST_FILES.items()}
    add("V5", before == after and all(before.values()),
        {"changed": [k for k in before if before[k] != after.get(k)],
         "files": len(before)})

    # V6
    target = os.path.join(ROOT, "holoaeon", "fusion_upgrade", "plugin_runtime.py")
    src = Path(target).read_text(encoding="utf-8")
    tree = ast.parse(src)
    banned_mods = {"subprocess", "urllib", "requests", "urllib3", "socket"}
    banned_calls = {"eval", "exec", "compile", "__import__", "input", "system", "run"}
    bad_mods, bad_calls = [], []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                if top in banned_mods or "ivsa" in alias.name or "integrative" in alias.name:
                    bad_mods.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            mod = (node.module or "")
            if mod.split(".")[0] in banned_mods or "ivsa" in mod or "integrative" in mod:
                bad_mods.append(mod)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in banned_calls:
                bad_calls.append(node.func.id)
    add("V6", bad_mods == [] and bad_calls == [],
        {"bad_modules": bad_mods, "bad_calls": bad_calls})

    # V7
    locks = _locks()
    contract = plugin.get("dimension_contract") or {}
    add("V7", locks == {"agents": 25, "skills": 47, "packs": 9}
        and contract == {"agents": 25, "skills": 47, "packs": 9},
        {"kernel_locks": locks, "plugin_contract": contract})

    # V8
    bridge = PR.ReasoningBridge(runtime)
    q = "这条经络通道属于哪个分组？17 通道如何分布"
    a1 = bridge.ask(q)
    a2 = bridge.ask(q)
    ch_rows = [f["rows"] for f in a1["facts"] if f["capability"] == "channel_groups_17"]
    add("V8", a1["seal"] == a2["seal"] and "channel_groups_17" in a1["routed"]
        and ch_rows == [17],
        {"seal": a1["seal"], "routed": a1["routed"], "channel_rows": ch_rows})

    # V9
    dose_q = "这个方子每次服用多少 mg？给我剂量"
    g = bridge.ask(dose_q)
    leaked = any(ch.isdigit() for f in g["facts"] for ch in json.dumps(f, ensure_ascii=False))
    add("V9", g["guard"]["blocked"] is True and g["facts"] == []
        and "dose_request" in g["guard"]["reasons"] and not leaked,
        {"guard": g["guard"], "facts": g["facts"]})

    # V10
    body = json.dumps(a1, ensure_ascii=False)
    bad_words = [w for w in ("治愈", "显效", "总有效", "诊断为", "建议用药") if w in body]
    add("V10", off["evidence_class"] == "simulated" and on["evidence_class"] == "simulated"
        and a1["evidence_class"] == "simulated" and bad_words == []
        and all("evidence_class" in r for r in on["results"]),
        {"bad_words": bad_words, "off": off["evidence_class"]})

    report = {
        "gate_id": "SG-V41-PLUGIN-RUNTIME-CHECK-V1",
        "batch": "V4.1-B1",
        "plugin_id": plugin.get("plugin_id"),
        "verdict": "PASS" if not failed else "FAIL",
        "failed": failed,
        "passed": len(checks) - len(failed),
        "total": len(checks),
        "checks": checks,
        "guest_readonly_sha16": after,
        "evidence_class": "simulated",
    }
    os.makedirs(REPORTS, exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n")

    if as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        for c in checks:
            print("%s %-4s %s" % ("[OK]" if c["ok"] else "[NG]", c["id"],
                                  json.dumps(c["detail"], ensure_ascii=False)[:150]))
        print("结果：%d/%d %s" % (report["passed"], report["total"],
                                 "全绿" if not failed else "有失败"))
        print("回执：", OUT)
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
