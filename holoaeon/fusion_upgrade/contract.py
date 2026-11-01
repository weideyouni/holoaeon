# -*- coding: utf-8 -*-
"""两仓 JSON 契约 v1：HoloAeon（发现层）↔ ivsa（执行层）唯一合法的交换形态。

契约只交换"一条完整回执"，不交换代码、不共享编号空间：
  · 6 个必填字段：contract_id / source / target / skill / mechanism / lane
  · 4 个可选字段：payload / nonce / budget / note
  · mechanism 必须落在六机制枚举内；lane 只能是 read / write
  · 任何回执都带 mode=simulated 与 evidence_class=simulated（仿真≠证明）
"""
from __future__ import annotations

from typing import Any, Dict, List

from .manifest import digest_of

REQUIRED = ("contract_id", "source", "target", "skill", "mechanism", "lane")
OPTIONAL = ("payload", "nonce", "budget", "note")
MECHANISMS = ("holographic_heartbeat", "cytoskeleton", "skin_v6",
              "semantic_bus", "hebbian_field", "meridian")
LANES = ("read", "write")

# 六机制对照：同参同构的地方写"可对齐"，不同的一律写"只映射"
PAIRS: List[Dict[str, Any]] = [
    {"mechanism": "holographic_heartbeat", "cn": "全息心跳",
     "holo": "SHAKE-256 展开 768 维双极向量 + 逐位叠加取符号；相位=位次%12；1229 技能侧 241 条",
     "ivsa": "70 体注册表 / 号段 8700–8769 / 768 维 / α=0.18",
     "same": ["dim=768"], "diff": ["主体数 70 vs 1229", "号段 vs 技能名"],
     "bridge": "只做映射表：技能→机制归属；编号不许互推"},
    {"mechanism": "cytoskeleton", "cn": "细胞骨架",
     "holo": "度/载荷/主干排序 + 逐节点抽除算连通分量增量；209 条",
     "ivsa": "3 层 × 4 链（采/洗/检/注）+ 12 跨链",
     "same": ["分层结构"], "diff": ["度量对象 vs 业务流程"],
     "bridge": "度量口径映射到 12 跨链的健康检查，不替换流程"},
    {"mechanism": "skin_v6", "cn": "皮肤八层",
     "holo": "SG-SKIN-V6.0 八层 fail-closed，通用闸固定 10 个红线 token；368 条",
     "ivsa": "L1–L8，L5 双轨仲裁：24 E14（越权/急症）+ 12 E13（失真/毒烈）",
     "same": ["八层同名同序", "L5 仲裁位"], "diff": ["词表 10 token vs 36 条医学规则"],
     "bridge": "通用闸不放医学词表；医学词表按域注入，避免误熔断"},
    {"mechanism": "semantic_bus", "cn": "语义通信底座",
     "holo": "2/3/4 阶 shingle + 空白切词混合打分；信封 encode/decode 往返指纹；仅 19 条技能",
     "ivsa": "语义总线十模块",
     "same": ["信封/指纹机制"], "diff": ["19 vs 十模块", "最薄一侧是 HoloAeon"],
     "bridge": "用十模块反向补齐 19，不引入第十一模块"},
    {"mechanism": "hebbian_field", "cn": "赫布协作场",
     "holo": "w += δ(0.99−w) 收敛 0.99 / 按比例衰减 / Dijkstra；315 条",
     "ivsa": "生命之花 19 圆 / 17 通道节点 / lr 0.12 / decay 0.99",
     "same": ["decay=0.99", "共激活强化形式"], "diff": ["状态主体：技能共现 vs 器官协同"],
     "bridge": "同一公式两套权重表；落盘格式分开，不共享存储"},
    {"mechanism": "meridian", "cn": "经络机制",
     "holo": "12 通道 LC01–LC12 + 预算 + 淤堵 + 再平衡；仅 4 条技能",
     "ivsa": "17 通道（气5/血4/神4/淋巴4）/ 11 器官 / 三级 / 四探针 / 四级治疗",
     "same": ["预算-淤堵-再平衡语义"], "diff": ["12 vs 17", "技能侧几乎空"],
     "bridge": "12→17 只写显式分组映射表，4/12 未映射目标登记为待办"},
]

_GROUPS = {"气": 5, "血": 4, "神": 4, "淋巴": 4}


def channel_map() -> Dict[str, Any]:
    """12 条 LC 通道 → ivsa 17 通道的**显式**分组映射（禁止算术推导）。"""
    rows: List[Dict[str, Any]] = []
    plan = ([("气", 5), ("血", 4), ("神", 3), ("淋巴", 0)])
    lc = 1
    for group, take in plan:
        for _ in range(take):
            rows.append({"lc": "LC%02d" % lc, "group": group, "target_group": group,
                         "status": "mapped",
                         "rule": "显式分组映射；同一 LC 不跨组"})
            lc += 1
    targets = sum(_GROUPS.values())
    mapped = len(rows)
    pending = targets - mapped
    return {"rows": rows, "mapped": mapped, "targets": targets, "pending": pending,
            "pending_detail": {"神": _GROUPS["神"] - 3, "淋巴": _GROUPS["淋巴"]},
            "no_arithmetic": True,
            "digest": digest_of(rows)}


def pairs() -> Dict[str, Any]:
    ok = (len(PAIRS) == 6 and [p["mechanism"] for p in PAIRS] == list(MECHANISMS))
    return {"ok": ok, "rows": len(PAIRS), "mechanisms": [p["mechanism"] for p in PAIRS],
            "digest": digest_of([{k: p[k] for k in ("mechanism", "same", "diff")} for p in PAIRS])}


def validate(doc: Dict[str, Any]) -> Dict[str, Any]:
    missing = [k for k in REQUIRED if not str(doc.get(k, "") or "").strip()]
    unknown = [k for k in doc.keys() if k not in REQUIRED + OPTIONAL]
    errors: List[str] = []
    mech = doc.get("mechanism")
    if mech and mech not in MECHANISMS:
        errors.append("mechanism 不在六机制枚举内：%s" % mech)
    lane = doc.get("lane")
    if lane and lane not in LANES:
        errors.append("lane 只能是 read/write：%s" % lane)
    if "budget" in doc and not isinstance(doc["budget"], (int, float)):
        errors.append("budget 必须是数值")
    return {"ok": not missing and not unknown and not errors,
            "missing": missing, "unknown": unknown, "errors": errors,
            "required": list(REQUIRED), "optional": list(OPTIONAL)}


def make(source: str, target: str, skill: str, mechanism: str,
         lane: str = "read", **extra: Any) -> Dict[str, Any]:
    doc: Dict[str, Any] = {"source": source, "target": target, "skill": skill,
                           "mechanism": mechanism, "lane": lane}
    for key in OPTIONAL:
        if key in extra:
            doc[key] = extra[key]
    doc["contract_id"] = "CT-" + digest_of({k: doc[k] for k in REQUIRED[1:] if k in doc}, 12)
    return doc


def receipt(doc: Dict[str, Any], verdict: str = "pass") -> Dict[str, Any]:
    check = validate(doc)
    rec = {"contract_id": doc.get("contract_id", ""), "verdict": verdict,
           "valid": check["ok"], "missing": check["missing"],
           "mode": "simulated", "evidence_class": "simulated",
           "note": "只读契约回执：不改对端代码、不执行外部技能、不声称临床效果"}
    rec["seal"] = digest_of({"c": rec["contract_id"], "v": verdict,
                             "ok": check["ok"], "m": doc.get("mechanism")})
    return rec
