# -*- coding: utf-8 -*-
"""fusion_upgrade 自身确定性自检：不依赖本机路径、不联网、可离线复跑。"""
from __future__ import annotations

import json
from typing import Any, Dict, List

from ..kernel import Kernel
from . import contract, plan
from . import manifest as mf
from . import protocol, snapshot, swap


def _check(results: List[Dict[str, Any]], name: str, ok: bool,
           detail: Any = None) -> None:
    results.append({"check": name, "ok": bool(ok), "detail": detail})


def _fresh(**kwargs: Any) -> Kernel:
    from ..packs import get_extra_pack

    k = Kernel()
    get_extra_pack("fusion_upgrade").install(k)
    return k


def run() -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []

    man1 = mf.manifest()
    man2 = mf.manifest()
    _check(results, "清单可复算", man1["digest"] == man2["digest"], man1["digest"])
    _check(results, "核心九包", man1["counts"]["core"] == 9, man1["counts"]["core"])
    _check(results, "扩展包≥10且含本包", man1["counts"]["extra"] >= 10
           and any(r["key"] == "fusion_upgrade" for r in man1["rows"]),
           man1["counts"]["extra"])
    _check(results, "冷热分布与注册表一致",
           man1["counts"]["cold"] == 9 and man1["counts"]["hot"] == man1["counts"]["extra"],
           {"cold": man1["counts"]["cold"], "hot": man1["counts"]["hot"]})

    k = Kernel()
    inst = swap.hot_install(k, "fusion_upgrade")
    from ..packs.fusion_upgrade_pack import FUSION_SKILLS
    _check(results, "热插拔新增全部技能与 2 角色",
           inst.get("ok") and len(inst["added_skills"]) == len(FUSION_SKILLS)
           and len(inst["added_agents"]) == 2,
           {"skills": inst.get("added_skills"), "agents": inst.get("added_agents")})

    rt = swap.probe_roundtrip(Kernel(), "fusion_upgrade")
    _check(results, "往返恢复原状", rt.get("ok") and rt["identical_names"],
           {"baseline": rt.get("baseline"), "restored": rt.get("restored")})

    refused = swap.hot_uninstall(_fresh(), "gaoyi")
    _check(results, "核心包拒绝卸载", refused.get("ok") is False
           and refused.get("reason") == "core_pack_protected", refused.get("reason"))

    kk = _fresh()
    inner = protocol.internal_fuse(kk)
    _check(results, "内部协议六步全通", inner["ok"] and len(inner["steps"]) == 6,
           [s["step"] for s in inner["steps"] if not s["ok"]])
    outer = protocol.external_fuse(kk)
    _check(results, "外部协议零网络", outer["ok"] and outer["network_calls"] == 0,
           outer.get("routes"))

    good = contract.make("holoaeon", "ivsa", "matrix_dispatch", "skin_v6", "read")
    bad = {"source": "holoaeon", "mechanism": "unknown_mech"}
    _check(results, "契约正例通过", contract.validate(good)["ok"], good["contract_id"])
    _check(results, "契约缺字段被拒",
           contract.validate(bad)["ok"] is False
           and len(contract.validate(bad)["missing"]) >= 3,
           contract.validate(bad)["missing"])
    r1 = contract.receipt(good)
    r2 = contract.receipt(good)
    _check(results, "回执封缄可复算", r1["seal"] == r2["seal"] and r1["mode"] == "simulated",
           r1["seal"])

    pr = contract.pairs()
    _check(results, "六机制对照 6 行", pr["ok"] and pr["rows"] == 6, pr["mechanisms"])

    ch = contract.channel_map()
    _check(results, "12→17 显式映射",
           ch["mapped"] == 12 and ch["targets"] == 17 and ch["pending"] == 5
           and ch["no_arithmetic"], {"mapped": ch["mapped"], "pending": ch["pending"]})

    pv = plan.validate()
    _check(results, "十二批九字段写满", pv["ok"] and pv["batches"] == 12,
           pv["problems"][:2])
    ps = plan.summary()
    _check(results, "总工时 15 人天", ps["total_hours"] == 15.0, ps["total_hours"])

    snap = snapshot.build()
    try:
        json.dumps(snap, ensure_ascii=False)
        serializable = True
    except (TypeError, ValueError):
        serializable = False
    _check(results, "快照可序列化且锁值现算",
           serializable and snap["locks"]["agents"] == 25
           and snap["locks"]["skills"] == 47 and snap["locks"]["packs"] == 9,
           snap["locks"])

    passed = sum(1 for r in results if r["ok"])
    return {"fusion_id": "SG-FUSION-UPGRADE-HOLOAEON-V4.0",
            "ok": passed == len(results), "passed": passed, "total": len(results),
            "checks": results,
            "evidence_class": "simulated"}
