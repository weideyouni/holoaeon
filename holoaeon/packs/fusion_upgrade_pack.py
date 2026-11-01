# -*- coding: utf-8 -*-
"""
FusionUpgradePack —— 冷热插拔赋能升级扩展包（第 10 个扩展包，不进 PACK_ORDER）
================================================================================
把"冷/热插拔 + 内部融合协议 + 外部融合协议 + 两仓契约 + 十二批计划 + 项目快照"
变成内核里可直接调用的确定性技能。

维度不变：只进 EXTRA_PACK_REGISTRY，不进 PACK_ORDER —— A1（25/47/9）不受影响。
"""
from __future__ import annotations

import json
from typing import Any, Dict

from .base import DomainPack, RoleSpec, SkillSpec, WorkflowSpec

FUSION_SKILLS = ("fusion_manifest", "fusion_hotplug", "fusion_internal",
                 "fusion_external", "fusion_fuse", "fusion_contract",
                 "fusion_plan", "fusion_snapshot")


def _sandbox(with_self: bool = True) -> Any:
    """一次性沙箱内核：九个领域包 + 本扩展包（不复用、不污染真实内核）。"""
    from ..kernel import Kernel
    from ..packs import PACK_ORDER, get_extra_pack, get_pack

    k = Kernel()
    for key in PACK_ORDER:
        get_pack(key).install(k)
    if with_self:
        get_extra_pack("fusion_upgrade").install(k)
    return k


# ---------------------------------------------------------------- 八技能实现
def fusion_manifest(view: str = "", **_: Any) -> dict:
    from ..fusion_upgrade import manifest as mf

    if view:
        return mf.cold_hot(view)
    m = mf.manifest()
    return {"counts": m["counts"], "digest": m["digest"],
            "cold": [r["key"] for r in m["rows"] if r["plug"] == "cold"],
            "hot": [r["key"] for r in m["rows"] if r["plug"] == "hot"]}


def fusion_hotplug(key: str = "fusion_upgrade", action: str = "roundtrip",
                   **_: Any) -> dict:
    """运行期热插拔演示：在沙箱核心里装/卸，返回前后计数与回执。"""
    from ..fusion_upgrade import swap

    k = _sandbox(with_self=False)
    if action == "install":
        return swap.hot_install(k, key)
    if action == "uninstall":
        return swap.hot_uninstall(k, key)
    return swap.probe_roundtrip(k, key)


def fusion_internal(_q: str = "", **_: Any) -> dict:
    from ..fusion_upgrade import protocol

    return protocol.internal_fuse(_sandbox())


def fusion_external(_q: str = "", **_: Any) -> dict:
    from ..fusion_upgrade import protocol

    return protocol.external_fuse(_sandbox())


def fusion_fuse(_q: str = "", **_: Any) -> dict:
    """内外协议一并跑：任一侧不通过即整体不通过。"""
    from ..fusion_upgrade import protocol

    return protocol.fuse(_sandbox())


def fusion_contract(doc_json: str = "", **_: Any) -> dict:
    """校验一条契约（传 JSON 字符串）；不传则返回 schema 与一张样例。"""
    from ..fusion_upgrade import contract

    if doc_json:
        try:
            doc = json.loads(doc_json)
        except ValueError as exc:
            return {"ok": False, "error": "invalid_json", "detail": str(exc)}
        return {"validate": contract.validate(doc), "receipt": contract.receipt(doc)}
    sample = contract.make("holoaeon", "ivsa", "matrix_dispatch", "skin_v6", "read")
    return {"required": list(contract.REQUIRED), "optional": list(contract.OPTIONAL),
            "mechanisms": list(contract.MECHANISMS), "lanes": list(contract.LANES),
            "sample": sample, "sample_receipt": contract.receipt(sample)}


def fusion_plan(batch: str = "", **_: Any) -> dict:
    from ..fusion_upgrade import plan

    if batch:
        return plan.get(batch)
    return {"summary": plan.summary(), "validate": plan.validate()}


def fusion_snapshot(path: str = "", write: bool = False, **_: Any) -> dict:
    from ..fusion_upgrade import snapshot

    if write:
        return snapshot.write(path)
    snap = snapshot.build()
    return {"seal": snap["seal"], "locks": snap["locks"], "plan": snap["plan"],
            "index": {"count": snap["index"].get("count"),
                      "digest": snap["index"].get("digest")},
            "quartet_top": snap["quartet"].get("top")}


class FusionUpgradePack(DomainPack):
    key = "fusion_upgrade"
    name = "冷热插拔赋能升级（内外融合协议）"
    description = ("把冷/热插拔、内部融合协议、外部融合协议、两仓契约、十二批计划与项目快照"
                   "做成可调用技能；旁挂注册，不改 25/47/9")

    skills = [
        SkillSpec("fusion_manifest", fusion_manifest,
                  "冷热插拔清单：哪些包只能启动期装、哪些可运行期插拔、回滚点在哪",
                  tags=["fusion", "manifest", "hotplug"], inputs={"view": "str"}),
        SkillSpec("fusion_hotplug", fusion_hotplug,
                  "运行期热插拔演示（install/uninstall/roundtrip），返回前后计数与封缄回执",
                  tags=["fusion", "hotplug", "swap"], inputs={"key": "str", "action": "str"}),
        SkillSpec("fusion_internal", fusion_internal,
                  "内部融合协议自检：信封→守卫→总线→节拍→技能匹配，六步给证据",
                  tags=["fusion", "protocol", "internal"], inputs={}),
        SkillSpec("fusion_external", fusion_external,
                  "外部融合协议自检：模型后端只做路由决策，零网络调用",
                  tags=["fusion", "protocol", "external"], inputs={}),
        SkillSpec("fusion_fuse", fusion_fuse,
                  "内外协议合并回执：任一侧不通过即整体不通过",
                  tags=["fusion", "protocol"], inputs={}),
        SkillSpec("fusion_contract", fusion_contract,
                  "两仓 JSON 契约 v1 校验：6 必填 + 4 可选 + 六机制枚举 + read/write",
                  tags=["fusion", "contract"], inputs={"doc_json": "str"}),
        SkillSpec("fusion_plan", fusion_plan,
                  "V2.0 十二批次计划查询与九字段校验",
                  tags=["fusion", "plan"], inputs={"batch": "str"}),
        SkillSpec("fusion_snapshot", fusion_snapshot,
                  "项目快照：现算锁值 + 清单摘要 + 计划摘要 + 四透镜排序，供其他智能体读取",
                  tags=["fusion", "snapshot"], inputs={"path": "str", "write": "bool"}),
    ]

    roles = [
        RoleSpec("fusion_engineer", "融合工程：清单、热插拔、契约",
                 ["fusion_manifest", "fusion_hotplug", "fusion_contract"]),
        RoleSpec("fusion_guardian", "融合守护：内外协议、计划、快照",
                 ["fusion_internal", "fusion_external", "fusion_plan", "fusion_snapshot"]),
    ]

    workflows = [
        WorkflowSpec("fusion_upgrade_flow", ["fusion_engineer", "fusion_guardian"],
                     "工程先装/卸一次并校契约 → 守护跑内外协议并出快照"),
    ]


def pack_summary() -> Dict[str, Any]:
    p = FusionUpgradePack()
    return {"key": p.key, "skills": len(p.skills), "roles": len(p.roles),
            "workflows": len(p.workflows), "skill_names": list(FUSION_SKILLS)}
