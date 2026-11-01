# -*- coding: utf-8 -*-
"""运行期热插拔与回滚：只动扩展包，核心九包一律拒绝卸载。

设计约束（与维度锁一致）：
  · 卸载核心包 → 直接拒绝（core_pack_protected），因为 A1 断言 25/47/9 由它撑着。
  · 卸载扩展包 → 逐个移除"标签首项等于该包 key"的技能、该包声明的角色 agent，
    并注销总线地址；调度器 watch 列表无公开移除接口，残留引用如实上报，不假装清干净。
"""
from __future__ import annotations

from typing import Any, Dict, List

from .manifest import digest_of


def _view(kernel: Any) -> Dict[str, Any]:
    return {"skills": kernel.skills.names(), "agents": sorted(kernel.agents.keys())}


def _watchers(scheduler: Any) -> int:
    """扫描 scheduler 实例上所有列表型属性，统计 watch 条目数（不依赖私有名）。"""
    total = 0
    for name, value in vars(scheduler).items():
        if "watch" in name and isinstance(value, list):
            total += len(value)
    return total


def hot_install(kernel: Any, key: str) -> Dict[str, Any]:
    """运行期安装一个扩展包；核心包拒绝。"""
    from ..packs import PACK_ORDER, get_extra_pack

    before = _view(kernel)
    if key in PACK_ORDER:
        return {"ok": False, "reason": "core_pack_protected", "key": key,
                "hint": "核心九包只能在启动期整体装载，卸载会破 A1 25/47/9"}
    try:
        pack = get_extra_pack(key)
    except KeyError as exc:
        return {"ok": False, "reason": "unknown_pack", "key": key, "detail": str(exc)}

    info = pack.install(kernel)
    after = _view(kernel)
    receipt = {
        "ok": True, "action": "install", "key": key,
        "added_skills": sorted(set(after["skills"]) - set(before["skills"])),
        "added_agents": sorted(set(after["agents"]) - set(before["agents"])),
        "before": {"skills": len(before["skills"]), "agents": len(before["agents"])},
        "after": {"skills": len(after["skills"]), "agents": len(after["agents"])},
        "install_report": info,
    }
    receipt["seal"] = digest_of(receipt)
    return receipt


def hot_uninstall(kernel: Any, key: str) -> Dict[str, Any]:
    """运行期卸载一个扩展包，返回"移除了什么、残留了什么"。"""
    from ..packs import PACK_ORDER, get_extra_pack

    before = _view(kernel)
    if key in PACK_ORDER:
        return {"ok": False, "reason": "core_pack_protected", "key": key}

    pack = get_extra_pack(key)
    wanted_skills = {s.name for s in pack.skills}
    wanted_agents = {r.name for r in pack.roles}

    removed_skills: List[str] = []
    store = getattr(kernel.skills, "_skills", None)
    if isinstance(store, dict):
        for name in list(store.keys()):
            skill = store[name]
            tags = getattr(getattr(skill, "manifest", None), "tags", []) or []
            if name in wanted_skills and tags and tags[0] == key:
                store.pop(name, None)
                removed_skills.append(name)

    removed_agents: List[str] = []
    for aid in sorted(wanted_agents):
        if aid in kernel.agents:
            try:
                kernel.bus.unregister_address(aid)
            except (KeyError, ValueError, AttributeError):
                pass
            kernel.agents.pop(aid, None)
            removed_agents.append(aid)

    after = _view(kernel)
    receipt = {
        "ok": True, "action": "uninstall", "key": key,
        "removed_skills": removed_skills, "removed_agents": removed_agents,
        "leftover_skills": sorted(set(wanted_skills) & set(after["skills"])),
        "watchers_left": _watchers(kernel.scheduler),
        "before": {"skills": len(before["skills"]), "agents": len(before["agents"])},
        "after": {"skills": len(after["skills"]), "agents": len(after["agents"])},
        "note": "调度器 watch 列表无公开移除接口：残留的是对象引用，不参与技能路由",
    }
    receipt["seal"] = digest_of(receipt)
    return receipt


def probe_roundtrip(kernel: Any, key: str) -> Dict[str, Any]:
    """热插拔往返一致性：装 → 卸 → 与基线逐名比对。"""
    base = _view(kernel)
    inst = hot_install(kernel, key)
    if not inst.get("ok"):
        return {"ok": False, "stage": "install", "detail": inst}
    uninst = hot_uninstall(kernel, key)
    if not uninst.get("ok"):
        return {"ok": False, "stage": "uninstall", "detail": uninst}
    final = _view(kernel)
    same_skills = final["skills"] == base["skills"]
    same_agents = final["agents"] == base["agents"]
    receipt = {
        "ok": bool(same_skills and same_agents), "key": key,
        "baseline": {"skills": len(base["skills"]), "agents": len(base["agents"])},
        "peak": inst["after"], "restored": {"skills": len(final["skills"]),
                                            "agents": len(final["agents"])},
        "identical_names": bool(same_skills and same_agents),
        "delta_skills": sorted(set(final["skills"]) ^ set(base["skills"])),
        "watchers_left": uninst["watchers_left"],
    }
    receipt["seal"] = digest_of(receipt)
    return receipt
