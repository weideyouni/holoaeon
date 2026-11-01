# -*- coding: utf-8 -*-
"""冷热插拔清单：从两套注册表现算出"哪些包只能冷插、哪些可热插拔"。

判定规则（写死，不做推断）：
  · 进 PACK_ORDER 的九个领域包 → cold：启动期安装，受 A1（25/47/9）维度锁保护，
    运行期只允许"整体装载"，不允许单包卸载。
  · 进 EXTRA_PACK_ORDER 的扩展包     → hot：可运行期安装/卸载，回滚点就是卸载本身。
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List


def canonical(obj: Any) -> str:
    """确定性序列化：键排序 + 紧凑分隔符 + 不转义中文。"""
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest_of(obj: Any, n: int = 16) -> str:
    return hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()[:n]


def _row(pack: Any, kind: str, order: int) -> Dict[str, Any]:
    plug = "cold" if kind == "core" else "hot"
    row = {
        "order": order,
        "key": pack.key,
        "name": pack.name,
        "kind": kind,
        "plug": plug,
        "skills": [s.name for s in pack.skills],
        "roles": [r.name for r in pack.roles],
        "workflows": [w.name for w in pack.workflows],
        "skill_count": len(pack.skills),
        "role_count": len(pack.roles),
        "deps": [],                     # 六护城河之一：零第三方依赖
        "rollback": ("reinstall_core_snapshot" if kind == "core" else "hot_uninstall:%s" % pack.key),
        "dimension_lock": ("A1:25/47/9" if kind == "core" else "A1 不受影响（旁挂）"),
    }
    row["digest"] = digest_of({"key": row["key"], "skills": row["skills"],
                               "roles": row["roles"]})
    return row


def scan() -> List[Dict[str, Any]]:
    """枚举全部包（核心 9 + 扩展 N），返回清单行。延迟导入避免包初始化循环。"""
    from ..packs import (EXTRA_PACK_ORDER, PACK_ORDER, get_extra_pack,
                         get_pack)
    rows: List[Dict[str, Any]] = []
    for i, key in enumerate(PACK_ORDER):
        rows.append(_row(get_pack(key), "core", i))
    for i, key in enumerate(EXTRA_PACK_ORDER):
        rows.append(_row(get_extra_pack(key), "extra", i))
    return rows


def manifest() -> Dict[str, Any]:
    rows = scan()
    core = [r for r in rows if r["kind"] == "core"]
    extra = [r for r in rows if r["kind"] == "extra"]
    return {
        "fusion_id": "SG-FUSION-UPGRADE-HOLOAEON-V4.0",
        "counts": {"total": len(rows), "core": len(core), "extra": len(extra),
                   "cold": len(core), "hot": len(extra),
                   "skills": sum(r["skill_count"] for r in rows),
                   "roles": sum(r["role_count"] for r in rows)},
        "rows": rows,
        "digest": digest_of([{k: r[k] for k in ("key", "kind", "skills", "roles")}
                             for r in rows]),
    }


def cold_hot(view: str = "") -> Dict[str, Any]:
    """按 view 过滤：cold / hot / 空（全量）。"""
    m = manifest()
    rows = m["rows"]
    if view in ("cold", "hot"):
        rows = [r for r in rows if r["plug"] == view]
    elif view in ("core", "extra"):
        rows = [r for r in rows if r["kind"] == view]
    return {"view": view or "all", "count": len(rows),
            "rows": [{"key": r["key"], "plug": r["plug"], "skills": r["skill_count"],
                      "roles": r["role_count"], "rollback": r["rollback"]} for r in rows],
            "digest": m["digest"]}
