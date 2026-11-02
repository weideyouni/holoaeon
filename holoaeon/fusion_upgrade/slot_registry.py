"""扩展卡槽注册表（V4.6，只读声明层）。

设计约束：
- 只读：本模块不修改任何状态，不接线、不发请求、不写文件。
- 不改变维度锁：卡槽是旁挂声明，25 智能体 / 47 技能 / 9 包这三个数不由卡槽改动。
- 无网络：模块内不 import urllib / socket / http 等（仓内 AST 红线）。

对外只暴露：load(root) / validate(payload) / summary(payload)。
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List

SLOT_FILE = os.path.join("data", "extension_slots.json")

SLOT_ID_PREFIX = "EXT-"

KINDS = (
    "provider",
    "protocol",
    "dimension_shadow",
    "evidence",
    "plugin_hook",
    "runtime",
    "gate",
    "doc_channel",
)

STATUSES = ("open", "reserved", "occupied", "blocked")

REQUIRED_FIELDS = ("slot_id", "kind", "name", "status", "owner", "contract", "next_action")

DIMENSION_LOCK = {"agents": 25, "skills": 47, "packs": 9}

# 允许出现在 contract 的本地地址前缀；任何公网 host 都不允许写进卡槽声明。
LOCAL_PREFIXES = ("http://localhost", "http://127.0.0.1", "http://[::1]", "http://0.0.0.0")


def slot_path(root: str) -> str:
    """返回卡槽文件绝对路径。"""
    return os.path.join(root, SLOT_FILE.replace("/", os.sep))


def load(root: str) -> Dict[str, Any]:
    """读取卡槽声明（只读，不缓存、不写回）。"""
    path = slot_path(root)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _has_public_url(text: str) -> bool:
    """文本里出现 http(s) 且不是本地前缀 → 视为公网地址。"""
    low = text.lower()
    if "http://" not in low and "https://" not in low:
        return False
    return not any(p in low for p in LOCAL_PREFIXES)


def validate(payload: Dict[str, Any]) -> List[str]:
    """校验卡槽声明，返回错误列表（空列表 = 全部通过）。"""
    errors: List[str] = []

    if payload.get("id") != "SG-V46-EXTENSION-SLOTS-V1":
        errors.append("id 不是 SG-V46-EXTENSION-SLOTS-V1")

    lock = payload.get("lock") or {}
    for key, want in DIMENSION_LOCK.items():
        if lock.get(key) != want:
            errors.append("维度锁被改动：%s=%r（应为 %d）" % (key, lock.get(key), want))

    kinds = payload.get("slot_kinds") or []
    if sorted(kinds) != sorted(KINDS):
        errors.append("slot_kinds 与代码白名单不一致")

    statuses = payload.get("status_enum") or []
    if sorted(statuses) != sorted(STATUSES):
        errors.append("status_enum 与代码白名单不一致")

    if not payload.get("claim_flow"):
        errors.append("缺少 claim_flow（认领流程）")

    slots = payload.get("slots") or []
    if not slots:
        errors.append("slots 为空")

    seen = set()
    for i, s in enumerate(slots):
        tag = s.get("slot_id") or ("#%d" % i)
        for field in REQUIRED_FIELDS:
            if not s.get(field):
                errors.append("%s 缺字段 %s" % (tag, field))
        sid = s.get("slot_id") or ""
        if not sid.startswith(SLOT_ID_PREFIX):
            errors.append("%s 未按 EXT- 前缀编号" % tag)
        if sid in seen:
            errors.append("%s 重复" % sid)
        seen.add(sid)
        if s.get("kind") not in KINDS:
            errors.append("%s kind 非法：%r" % (tag, s.get("kind")))
        if s.get("status") not in STATUSES:
            errors.append("%s status 非法：%r" % (tag, s.get("status")))
        for field in ("contract", "next_action", "notes"):
            text = s.get(field) or ""
            if _has_public_url(text):
                errors.append("%s 的 %s 出现公网地址" % (tag, field))
            if "sk-" in text:
                errors.append("%s 的 %s 出现疑似凭证" % (tag, field))

    return errors


def summary(payload: Dict[str, Any]) -> Dict[str, Any]:
    """统计各状态与各类型的槽数，便于票据引用。"""
    by_status: Dict[str, int] = {k: 0 for k in STATUSES}
    by_kind: Dict[str, int] = {k: 0 for k in KINDS}
    for s in payload.get("slots") or []:
        st = s.get("status")
        kd = s.get("kind")
        if st in by_status:
            by_status[st] += 1
        if kd in by_kind:
            by_kind[kd] += 1
    return {
        "total": len(payload.get("slots") or []),
        "by_status": by_status,
        "by_kind": by_kind,
        "lock": dict(DIMENSION_LOCK),
    }


def open_slots(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """列出仍开放的槽（供开发者认领）。"""
    return [s for s in (payload.get("slots") or []) if s.get("status") == "open"]
