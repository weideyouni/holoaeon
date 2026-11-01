# -*- coding: utf-8 -*-
"""面向其他智能体的项目快照：自包含、可解析、带口径与诚实声明。

原则：能现算的现算（锁值、清单摘要、计划摘要），不能现算的只写"上次已知 + 复跑命令"，
绝不把历史数字伪装成当前实测。
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict

from .manifest import digest_of

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INDEX_PATH = os.path.join(_ROOT, "data", "skill_matrix_index.json")


def _locks() -> Dict[str, Any]:
    """现算核心维度：在空内核上装九个领域包，数 agent/skill。"""
    from ..kernel import Kernel
    from ..packs import PACK_ORDER, all_packs

    k = Kernel()
    for pack in all_packs():
        pack.install(k)
    return {"agents": len(k.agents), "skills": len(k.skills.names()),
            "packs": len(PACK_ORDER)}


def _index() -> Dict[str, Any]:
    if not os.path.isfile(INDEX_PATH):
        return {"present": False, "path": INDEX_PATH}
    with open(INDEX_PATH, "r", encoding="utf-8") as fh:
        idx = json.load(fh)
    stats = idx.get("stats", {}) or {}
    return {"present": True, "count": idx.get("count"), "digest": idx.get("digest"),
            "by_mechanism": stats.get("by_mechanism"),
            "by_domain": stats.get("by_domain"), "unmapped": stats.get("unmapped"),
            "roots": idx.get("roots")}


def _quartet() -> Dict[str, Any]:
    try:
        from ..packs.persona_quartet_pack import persona_mission
        m = persona_mission("将 1229 个技能分 10-20 批次完美融合进 HoloAeon 与中西医融合康复工程，保持两边原维度，先策划后执行")
        return {"rank": [{"persona": r["persona"], "name": r["name"],
                          "overlap": r.get("overlap")} for r in m.get("rank", [])],
                "top": m.get("rank", [{}])[0].get("persona")}
    except Exception as exc:                       # 快照不许因一个子项失败而整体失败
        return {"rank": [], "error": str(exc)}


def build() -> Dict[str, Any]:
    from ..spec import DOC_VERSION, VERSION
    from . import FUSION_DOC_VERSION, FUSION_ID, FUSION_PROTOCOL
    from . import contract, plan
    from . import manifest as mf

    man = mf.manifest()
    snap = {
        "as_of": "2026-11-02",
        "fusion": {"id": FUSION_ID, "doc_version": FUSION_DOC_VERSION,
                   "protocol": FUSION_PROTOCOL, "evidence_class": "simulated"},
        "version": {"runtime": VERSION, "doc": DOC_VERSION,
                    "policy": "运行态 VERSION 不动（写进回执参与 ReproHash）；融合版本单列"},
        "locks": _locks(),
        "manifest": {"core": man["counts"]["core"], "extra": man["counts"]["extra"],
                     "skills": man["counts"]["skills"], "digest": man["digest"]},
        "index": _index(),
        "contract": {"pairs": contract.pairs()["rows"],
                     "mechanisms": list(contract.MECHANISMS),
                     "channels": {k: contract.channel_map()[k]
                                  for k in ("mapped", "targets", "pending")}},
        "plan": plan.summary(),
        "quartet": _quartet(),
        "gates_last_known": {
            "holoaeon_v3_gate": "32/32 PASS, A1=25/47/9",
            "holoaeon_unittest": "34 OK",
            "holoaeon_selftest": "25/25",
            "holoaeon_redline": "0 violations",
            "ivsa_main": "21/21 PASS",
            "ivsa_unittest": "16 OK",
            "ivsa_redline": "hits=56 safe=56 violations=0",
            "note": "本组为上次已知值；接收方须按 recheck 现场复跑",
        },
        "recheck": [
            "python scripts/v3_gate.py --json reports/gate.json",
            "python -m unittest discover -s tests",
            "python scripts/verify_fusion_upgrade.py",
            "cd ../开源发布_中西医融合康复工程_20261026/integrative-rehab-vsa && python main.py",
        ],
        "honesty": {"network_calls": 0, "third_party_deps": 0,
                    "external_skills_executed": 0,
                    "note": "1229 外部技能只读 SKILL.md 头部，从未 import/run"},
        "attribution_note": "四人组为公开资料归因仿真转述，不代表原型人物实时观点；需人类终审；仿真≠证明",
        "seal": "",
    }
    snap["seal"] = digest_of({k: snap[k] for k in ("locks", "manifest", "plan")})
    return snap


def write(path: str = "") -> Dict[str, Any]:
    snap = build()
    target = path or os.path.join(_ROOT, "data", "fusion_snapshot.json")
    with open(target, "w", encoding="utf-8") as fh:
        json.dump(snap, fh, ensure_ascii=False, indent=1)
    return {"ok": True, "path": target, "bytes": os.path.getsize(target),
            "seal": snap["seal"]}
