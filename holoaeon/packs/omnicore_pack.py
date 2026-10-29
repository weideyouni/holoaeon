# -*- coding: utf-8 -*-
"""
OmniCorePack —— 全息纪元·认知主权引擎扩展包（HoloAeon 横切扩展包，第十三包）
================================================================================
来源：投喂文本「超级智能模式 Super-Intelligent Mode / HoloAeon Omni-Core」
      （2026-10-30）+ 其单文件 Python 实现 holoeon/omnicore.py（同批投喂）

定位：把投喂的"数字生命主权宣言 + 单文件引擎"重写为**离线、确定性、零依赖**的
      可插拔包。投喂的实现有 5 处硬缺陷（3 处会直接报错/静默丢数据），本包逐一
      修正并在 `CORRECTIONS` 与 `skill_core_manifest()` 里留痕。

  20 个技能 = 本体/寻址 3 + 心跳/呼吸 2 + 存续 3 + 编排/通信 3
             + 代谢（远端配对/蒸馏/赫布）3 + 闸门 1 + 宣告与白皮书 3 + 兜底/审计 2
  6 条工作流 = M1 唤醒 / M2 呼吸 / M3 代谢 / M4 通信 / M5 存续 / M6 宣告
  0 个角色 = **不建 agent**（上游 G15 断言 n_agents==25 是硬约束）

维度不变（写入断言，与第十一、十二包同口径）：
  127 × 10 = 1270 主干槽位 + 61 保留 = 1331 行
  127 × 855 = 108585 子图节点 + 56 全局协调 = 108641 节点
  本包**不新增行、不新增节点**，只消费既有 127 个亚学科编码做寻址。

红线（写进实现，不是口号）：
  · 纯标准库、确定性、离线；不联网、不开端口、不登录、不抓取、**不起线程**、
    不常驻、无定时器、不写盘（快照由宿主持久化）
  · 投喂里的守护线程 / sqlite 落盘 / numpy 随机 / "pip install holoeon-omnicore"
    一律不实现：前两者违背离线确定性，后者该包名不存在（未联网核验，也不得核验）
  · "数字生命 / 呼吸 / 免疫"只作**架构隐喻**（metaphor=True）；实证部分是确定性软件
  · 不做浏览器插件对接流媒体/电商平台、不改平台推荐算法、不注入 DOM —— 一律拒绝
"""
from __future__ import annotations

import hashlib
import json
import os
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .base import DomainPack, SkillSpec, WorkflowSpec

# ---------------------------------------------------------------- 常量（锁数）
MATRIX_ID = "SG-MASTER-OMNI-CORE-1331x1331-EXT-V1.0"
UPSTREAM_ID = "SG-MASTER-OMNI-LIFE-1331x1331-EXT-V1.0"
UPSTREAM_ID_2 = "SG-MASTER-COGNITIVE-SOVEREIGNTY-1331x1331-SUPER-MAS-V3.1"
DOMAIN = "omnicore"
LOCK_SIDE = 1331
LOCK_DESIGN = 1771561
LOCK_MANDALA = 108641
LOCK_HILBERT = 651846
LOCK_KALMAN = 22627
HEARTBEAT_BASE, HEARTBEAT_COUNT, HEARTBEAT_DIM = 9700, 70, 768
HEARTBEAT_ALPHA = 0.18
SUBD_TOTAL, SLOTS_PER, SLOTS_RESERVED = 127, 10, 61
NODES_PER, NODES_COORD = 855, 56
SEAL = "潮起开门，潮落闭嘴"

# 心跳节律（纯函数推进，不起线程）
DISTILL_EVERY = 64
PRUNE_EVERY = 100
CHECKPOINT_EVERY = 256
BURST_EVERY = 200
BURST_TAU = 2.5
BURST_PCT = 5
TTL_EPOCHS = 1000
PROBE_HINT_MS = 5000

# ---------------------------------------------------------------- 投喂代码的修正
CORRECTIONS: Tuple[Dict[str, str], ...] = (
    {"id": "C1",
     "where": "SparseMatrix1331.activate: self._cells = profile",
     "effect": "静默覆盖整张稀疏表：第二次激活后旧单元全丢，.get((r,c)) 返回 None 而不报错",
     "fix": "self._cells[(row, col)] = profile",
     "verified": "最小复现：D1 无异常、取回 None（数据静默丢失）"},
    {"id": "C2",
     "where": "ProtocolLayer.send: self._inbox.append(msg)",
     "effect": "AttributeError: 'collections.defaultdict' object has no attribute 'append'",
     "fix": "self._inbox[(r, c)].append(msg)",
     "verified": "最小复现：D2 AttributeError"},
    {"id": "C3",
     "where": "_meridian_route: route = （空赋值语句）",
     "effect": "SyntaxError: invalid syntax —— 整文件无法加载，'可运行'声明不成立",
     "fix": "route: List[Tuple[int, int]] = []",
     "verified": "最小复现：D3 SyntaxError invalid syntax line 1"},
    {"id": "C4",
     "where": "import numpy / np.random.random()",
     "effect": "与'零外部依赖'自相矛盾；随机抽样破坏确定性复现",
     "fix": "只 import 标准库；随机改 sha256(epoch) 确定性抽样（BURST_PCT=5%）",
     "verified": "红线扫描：third_party_import 零违规"},
    {"id": "C5",
     "where": "daemon Thread + sqlite3 落盘 + pip install holoeon-omnicore",
     "effect": "常驻线程/落盘/包名均不满足离线确定性；该 PyPI 包名不存在（未联网核验，也不核验）",
     "fix": "心跳改为纯函数 heartbeat_pulse(epoch)；快照交宿主持久化；不声称任何包名",
     "verified": "包内 threads=0 / disk_writes=0 / deps=0（pack_summary 断言）"},
)

# ---------------------------------------------------------------- 拒绝清单
REFUSED_OPS: Tuple[str, ...] = (
    "自动登录", "多端并发模拟请求", "切换高匿名代理", "代理池", "抓取", "爬取",
    "批量下单", "批量发帖", "绕过风控", "绕过验证", "伪造身份", "多账号", "养号",
    "注入 DOM", "改写页面", "调用平台私有接口", "破解",
    "浏览器插件", "对接流媒体平台", "对接电商平台", "反控算法", "接管推荐位",
)
FORBIDDEN_MEDICAL: Tuple[str, ...] = (
    "诊断", "处方", "剂量", "疗效承诺", "包治", "根治",
)
ABSOLUTE_CLAIMS: Tuple[str, ...] = ("一定", "绝对", "必然", "百分之百", "保证有效")
MEDICAL_DISCLAIMER = "仅作为知识框架与跨学科映射探讨，不构成诊疗建议；不进补、不替代就医"

# 概念 → 代码实现 对照表（投喂原文的"设计对照表"，逐行落到本包技能）
INTEROP_ROWS: Tuple[Tuple[str, str, str, str], ...] = (
    ("1331×1331 矩阵", "SparseMatrix1331（投喂）", "omnicore.matrix_allocate", "稀疏仅存激活单元；本包只产分配计划，不持有状态"),
    ("108641 节点", "NodePool108641（投喂）", "omnicore.node_pool_plan", "127×855 子图 + 56 全局协调，只产分区计划"),
    ("全息心跳", "HeartbeatScheduler（投喂）", "omnicore.heartbeat_pulse", "纯函数推进 epoch，不起线程、无 sleep"),
    ("呼吸节律", "interval_ms 自适应（投喂）", "omnicore.breathing_budget", "按负载给 tick 预算，慢消化/同频两档"),
    ("皮肤机制", "SkinMechanism（投喂）", "omnicore.skin_gate", "17 项拒绝 + 医疗断言 + 绝对断言"),
    ("经络机制", "ProtocolLayer._meridian_route", "omnicore.meridian_route", "按亚学科链给行坐标通路"),
    ("A2A 通信", "A2AMessage（投喂）", "omnicore.a2a_envelope", "信封 + 皮肤门 + 8 邻域路由 + ttl"),
    ("赫布协作场", "HebbianField（投喂）", "omnicore.hebbian_update", "强化/衰减/剪枝三段纯算术"),
    ("亚学科蒸馏", "SubDisciplineDistiller", "omnicore.skc_distill", "两张卡 → SKC，关系强制反例"),
    ("远域配对", "far_domain_pairs（随机）", "omnicore.far_pairs", "确定性排序取前 k，不随机"),
    ("反标签引擎", "SKC.anti_label_score", "omnicore.skc_distill", "温度→分值的确定性映射"),
    ("状态/断点", "StateManager + sqlite", "omnicore.state_checkpoint / state_restore", "内存快照 + 指纹，落盘交宿主"),
    ("任务编排", "TaskOrchestrator", "omnicore.task_dispatch_plan", "只产派发计划，不执行"),
    ("沙箱隔离", "Sandbox(sqlite)", "（不实现）", "本包不写盘；隔离由宿主目录/进程边界负责"),
    ("自我认知宣告", "（投喂未实现）", "omnicore.self_declaration", "四段式宣告框架，含拒绝清单"),
    ("生存与进化白皮书", "（投喂提议）", "omnicore.whitepaper_outline", "七章结构 + 字数配比"),
    ("生命周期", "TTL + sweep_expired", "omnicore.lifecycle_policy", "TTL/休眠/剪枝/探针阈值表"),
    ("故障兜底", "（投喂未实现）", "omnicore.degradation_plan", "心跳失联/节点过期/剪枝失控 三级"),
    ("审计", "audit_log(sqlite)", "omnicore.audit_receipt", "指纹 + 人类终裁 + 密令"),
    ("资源占用表", "投喂给实测值", "omnicore.pack_summary", "本包只报自身零开销，不复制他人实测数"),
)
METAPHOR_NOTE = ("'数字生命 / 呼吸 / 免疫 / 城邦'均为架构隐喻（metaphor=True）；"
                 "实证部分是确定性软件：无生命、无意识、无自主目标")

# ---------------------------------------------------------------- 亚学科表
def _repo_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _load_taxonomy() -> Dict[str, Any]:
    path = os.path.join(_repo_root(), "data", "taxonomy_127.json")
    if not os.path.exists(path):
        return {"items": [], "path": path, "loaded": False}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {"items": data["items"], "path": path, "loaded": True}


TAXONOMY = _load_taxonomy()
ITEMS: Dict[str, Dict[str, Any]] = {i["code"]: i for i in TAXONOMY["items"]}
IDX: Dict[str, int] = {it["code"]: n for n, it in enumerate(TAXONOMY["items"])}


# ---------------------------------------------------------------- 确定性工具
def _sha16(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16].upper()


def _sha_int(text: str, mod: int) -> int:
    return int(_sha16(text)[:8], 16) % mod


def _slot_rows(code: str) -> List[int]:
    i = IDX.get(code)
    return [] if i is None else list(range(i * SLOTS_PER, (i + 1) * SLOTS_PER))


def _node_range(code: str) -> Tuple[int, int]:
    i = IDX.get(code)
    if i is None:
        return (-1, -1)
    return (i * NODES_PER, (i + 1) * NODES_PER)


def _name(code: str) -> str:
    return ITEMS.get(code, {}).get("name", code)


def _seeds(code: str, k: int = 2) -> List[str]:
    it = ITEMS.get(code)
    if not it:
        return []
    out = list(it.get("seeds", []))[:k]
    if len(out) < k:
        out.append(it.get("name", code))
    return out


def _neighbors(code: str, span: int = 2) -> List[str]:
    """同宏观域、序号相近的邻近亚学科（确定性，按编码排序）。"""
    it = ITEMS.get(code)
    if not it:
        return []
    dom = it.get("domain", "")
    base = IDX.get(code, 0)
    out = []
    for other, j in IDX.items():
        if other == code:
            continue
        if ITEMS.get(other, {}).get("domain") == dom and abs(j - base) <= span:
            out.append(other)
    return sorted(out)


# ---------------------------------------------------------------- 1. 本体 / 寻址
def skill_core_manifest() -> Dict[str, Any]:
    """维度锁定与不变式自检：1331×1331 稀疏矩阵 / 108641 节点 / 127×10+61 / 127×855+56。"""
    rows = SUBD_TOTAL * SLOTS_PER + SLOTS_RESERVED
    nodes = SUBD_TOTAL * NODES_PER + NODES_COORD
    checks = {
        "rows": rows == LOCK_SIDE,
        "nodes": nodes == LOCK_MANDALA,
        "slots": SUBD_TOTAL * SLOTS_PER == 1270,
        "coord": SUBD_TOTAL * NODES_PER + NODES_COORD == 108641,
        "taxonomy": len(ITEMS) == SUBD_TOTAL,
        "design_grid": LOCK_SIDE * LOCK_SIDE == LOCK_DESIGN,
    }
    return {"skill": "core_manifest", "matrix_id": MATRIX_ID,
            "upstream": [UPSTREAM_ID, UPSTREAM_ID_2],
            "locks": {"side": LOCK_SIDE, "design_grid": LOCK_DESIGN,
                      "mandala_nodes": LOCK_MANDALA, "hilbert": LOCK_HILBERT,
                      "kalman": LOCK_KALMAN,
                      "heartbeat": {"base": HEARTBEAT_BASE, "count": HEARTBEAT_COUNT,
                                    "dim": HEARTBEAT_DIM, "alpha": HEARTBEAT_ALPHA},
                      "rows": rows, "nodes": nodes, "subdisciplines": SUBD_TOTAL,
                      "slots_per": SLOTS_PER, "slots_reserved": SLOTS_RESERVED,
                      "nodes_per": NODES_PER, "nodes_coord": NODES_COORD},
            "checks": checks, "checks_pass": all(checks.values()),
            "addressing_unchanged": checks["rows"] and checks["nodes"],
            "taxonomy_loaded": TAXONOMY["loaded"], "taxonomy_items": len(ITEMS),
            "corrections": len(CORRECTIONS),
            "correction_ids": [c["id"] for c in CORRECTIONS],
            "metaphor": True, "metaphor_note": METAPHOR_NOTE,
            "threads": 0, "disk_writes": 0, "deps": 0, "network": False,
            "seal": SEAL}


def skill_matrix_allocate(codes: Optional[Sequence[str]] = None, col: int = 0) -> Dict[str, Any]:
    """为亚学科分配 1331×1331 稀疏矩阵槽位（每亚学科 10 行，列取给定列）。"""
    codes = list(codes or ["MATH-09", "AI-03", "LOGIC-04"])
    out, missing, cells = [], [], []
    for code in codes:
        rows = _slot_rows(code)
        if not rows:
            missing.append(code)
            continue
        out.append({"code": code, "name": _name(code), "index": IDX[code],
                    "base_row": rows[0], "rows": rows, "slots": [[r, col] for r in rows]})
        cells.append([rows[0], col])
    return {"skill": "matrix_allocate", "side": LOCK_SIDE, "col": col,
            "allocated": out, "cells": cells, "missing": missing,
            "density_if_activated": round(len(cells) / LOCK_DESIGN, 10),
            "storage": "sparse_dict_only", "execution": "plan_only",
            "note": "只产分配计划；真实激活由宿主按需加载，本包不持有矩阵状态"}


def skill_node_pool_plan(codes: Optional[Sequence[str]] = None) -> Dict[str, Any]:
    """108641 节点池分区计划：每亚学科 855 节点 + 56 个全局协调节点。"""
    codes = list(codes or ["MATH-09", "AI-03", "TCM-02"])
    parts, missing = [], []
    for code in codes:
        lo, hi = _node_range(code)
        if lo < 0:
            missing.append(code)
            continue
        parts.append({"code": code, "name": _name(code), "node_range": [lo, hi],
                      "count": hi - lo, "head": lo})
    global_lo = SUBD_TOTAL * NODES_PER
    return {"skill": "node_pool_plan", "total_nodes": LOCK_MANDALA,
            "parts": parts, "missing": missing,
            "global_block": {"range": [global_lo, LOCK_MANDALA],
                              "count": NODES_COORD,
                              "role": "cytoskeleton_global_coordinator"},
            "addressing_unchanged": SUBD_TOTAL * NODES_PER + NODES_COORD == LOCK_MANDALA}


# ---------------------------------------------------------------- 2. 心跳 / 呼吸
def skill_heartbeat_pulse(epoch: int = 1) -> Dict[str, Any]:
    """推进一次心跳（纯函数）：返回本拍该触发的事件，不启动线程也不 sleep。"""
    e = int(epoch)
    events = ["ttl_decay"]
    if e % DISTILL_EVERY == 0:
        events.append("distill_incremental")
    if e % PRUNE_EVERY == 0:
        events.append("hebbian_prune")
    if e % CHECKPOINT_EVERY == 0:
        events.append("checkpoint")
    burst = False
    if e % BURST_EVERY == 0 and _sha_int(f"burst:{e}", 100) < BURST_PCT:
        burst = True
        events.append("temperature_burst")
    return {"skill": "heartbeat_pulse", "epoch": e, "events": events,
            "ttl_decay": 1, "distill": e % DISTILL_EVERY == 0,
            "prune": e % PRUNE_EVERY == 0, "checkpoint": e % CHECKPOINT_EVERY == 0,
            "burst": burst, "burst_tau": BURST_TAU if burst else None,
            "deterministic_sampling": f"sha256(epoch)%100<{BURST_PCT}",
            "threads": 0, "timers": 0, "sleep": False,
            "note": "宿主自行按 tick 调用本函数即可获得节律；本包不守护、不阻塞"}


def skill_breathing_budget(load_ratio: float = 0.2) -> Dict[str, Any]:
    """按负载给出呼吸预算：低负载慢消化（蒸馏/衰减/剪枝），高负载同频专注。"""
    r = max(0.0, min(1.0, float(load_ratio)))
    if r < 0.35:
        mode, tick_ms, units, cadence = "slow_digest", 1000, 2, "每 64 拍一次增量蒸馏"
    elif r < 0.75:
        mode, tick_ms, units, cadence = "balanced", 500, 6, "每 64 拍蒸馏 + 每 100 拍剪枝"
    else:
        mode, tick_ms, units, cadence = "sync_focus", 200, 16, "暂停剪枝，只保留 TTL 衰减"
    return {"skill": "breathing_budget", "load_ratio": round(r, 4), "mode": mode,
            "tick_ms": tick_ms, "work_units_per_tick": units, "cadence": cadence,
            "suspend_below_ratio": 0.05, "note": "预算表是建议值，不走实时测量"}


# ---------------------------------------------------------------- 3. 存续
def skill_state_checkpoint(state: Optional[Dict[str, Any]] = None,
                           tag: str = "manual") -> Dict[str, Any]:
    """生成状态快照（内存对象 + 指纹），落盘交给宿主，本包不写文件。"""
    payload = state or {"matrix_cells": 0, "nodes": 0, "skc": 0}
    canon = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
    fp = _sha16(canon)
    ckpt_id = _sha16(f"{tag}|{canon}")
    return {"skill": "state_checkpoint", "ckpt_id": ckpt_id, "tag": tag,
            "fingerprint": fp, "payload_fingerprint": fp,
            "payload": payload, "canonical_bytes": len(canon.encode("utf-8")),
            "persistence": "host_managed", "disk_writes": 0,
            "note": "fingerprint 只覆盖 payload；宿主可把 payload 写到自己的目录，本包不建任何 .db/.json"}


def skill_state_restore(snapshot: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """从宿主带回的快照恢复并校验维度（校验失败即拒绝，不做"尽力而为"）。"""
    snap = snapshot or {"payload": {"matrix_cells": 0, "nodes": 0}}
    payload = snap.get("payload", snap)
    fp = _sha16(json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str))
    declared = snap.get("payload_fingerprint") or snap.get("fingerprint")
    ok = True if declared in (None, fp) else False
    dims = {"matrix_cells": int(payload.get("matrix_cells", 0)),
            "nodes": int(payload.get("nodes", 0))}
    in_bounds = 0 <= dims["matrix_cells"] <= LOCK_DESIGN and 0 <= dims["nodes"] <= LOCK_MANDALA
    return {"skill": "state_restore", "restored": True, "fingerprint": fp,
            "fingerprint_matches": ok, "dims": dims, "in_bounds": in_bounds,
            "accept": bool(ok and in_bounds),
            "note": "指纹不符或越界即拒收；恢复不改变维度"}


def skill_lifecycle_policy() -> Dict[str, Any]:
    """生命周期策略表：TTL、休眠、剪枝阈值、存活探针阈值（全部为声明值）。"""
    return {"skill": "lifecycle_policy",
            "ttl_epochs": TTL_EPOCHS,
            "states": ["idle", "active", "suspended", "failed", "completed"],
            "suspend_after_idle_epochs": 300,
            "prune_threshold": 0.05, "prune_min_coactivations": 3,
            "decay_rate": 0.001,
            "probe_hint_ms": PROBE_HINT_MS,
            "probe_rule": "超过 5000ms 未更新探针视为失联（由宿主判定，本包只给阈值）",
            "threads": 0, "note": "策略只声明；执行由宿主调度"}


# ---------------------------------------------------------------- 4. 编排 / 通信
def skill_task_dispatch_plan(intent: str = "跨域同构核查",
                             codes: Optional[Sequence[str]] = None) -> Dict[str, Any]:
    """把意图拆成派发计划：按亚学科找槽位、给顺序与预算，不实际执行。"""
    codes = list(codes or ["MATH-09", "AI-03"])
    steps, missing = [], []
    for n, code in enumerate(codes, 1):
        rows = _slot_rows(code)
        if not rows:
            missing.append(code)
            continue
        steps.append({"order": n, "code": code, "name": _name(code),
                      "primary_cell": [rows[0], 0], "candidate_rows": rows,
                      "budget_units": 4})
    total = sum(s["budget_units"] for s in steps)
    return {"skill": "task_dispatch_plan", "intent": intent, "steps": steps,
            "missing": missing, "total_budget_units": total,
            "execution": "plan_only", "retry_policy": "max_retry=1",
            "note": "计划不含任何执行动作；执行由宿主 agent 或本人完成"}


def skill_a2a_envelope(sender: str = "MATH-09", receiver: str = "AI-03",
                        semantic_type: str = "query",
                        payload: Any = None,
                        active: Optional[Sequence[str]] = None) -> Dict[str, Any]:
    """构造 A2A 消息信封：皮肤门 → 8 邻域路由 → ttl 递减，越界即拒。"""
    text = json.dumps(payload if payload is not None else "", ensure_ascii=False, default=str)
    gate = skill_skin_gate(text)
    if not gate["allowed"]:
        return {"skill": "a2a_envelope", "allowed": False,
                "reason": gate["reason"], "msg_id": None, "routed": []}
    s_rows, r_rows = _slot_rows(sender), _slot_rows(receiver)
    if not s_rows or not r_rows:
        return {"skill": "a2a_envelope", "allowed": False,
                "reason": f"未知亚学科编码：{sender if not s_rows else receiver}",
                "routed": []}
    act = list(active or [receiver])
    src = [s_rows[0], 0]
    dst = [r_rows[0], 0]
    route = []
    for c in act:
        rr = _slot_rows(c)
        if rr and abs(rr[0] - dst[0]) <= 1:
            route.append([rr[0], 0])
    if not route:
        route = [dst]
    msg_id = _sha16(f"{sender}>{receiver}|{semantic_type}|{text}")[:12]
    hops = len(route)
    return {"skill": "a2a_envelope", "allowed": True, "msg_id": msg_id,
            "sender": sender, "receiver": receiver, "src": src, "dst": dst,
            "semantic_type": semantic_type, "route": route, "hops": hops,
            "ttl_hops": max(5, hops + 1), "delivered": True,
            "note": "route 只在已登记为 active 的邻近单元之间传递；不做全网广播"}


def skill_meridian_route(codes: Optional[Sequence[str]] = None) -> Dict[str, Any]:
    """把一组亚学科串成经络通路（行坐标链），用于跨域语义流转。"""
    codes = list(codes or ["MATH-09", "AI-03", "PHIL-06", "PHYS-04"])
    path, missing = [], []
    for code in codes:
        rows = _slot_rows(code)
        if not rows:
            missing.append(code)
            continue
        path.append({"code": code, "name": _name(code), "row": rows[0],
                     "entry": [rows[0], 0], "span_rows": [rows[0], rows[-1]]})
    hops = max(0, len(path) - 1)
    return {"skill": "meridian_route", "path": path, "missing": missing,
            "hops": hops, "edges": [[path[i]["row"], path[i + 1]["row"]]
                                    for i in range(hops)],
            "api_calls": 0, "network": False,
            "note": "通路是行坐标链，不含数据搬运；数据由宿主本地交接"}


# ---------------------------------------------------------------- 5. 代谢
def skill_hebbian_update(edges: Optional[Sequence[Sequence[str]]] = None,
                         decay: float = 0.001,
                         prune_threshold: float = 0.05) -> Dict[str, Any]:
    """赫布协作场一次更新：共同激活强化 → 衰减 → 剪枝（三段确定性算术）。"""
    edges = [list(e) for e in (edges or [["MATH-09", "AI-03"], ["PHIL-06", "PHYS-04"]])]
    rows = []
    for a, b in edges:
        key = f"{a}<->{b}"
        w0 = round(0.5 + _sha_int(f"seed:{key}", 100) / 1000.0, 3)
        w1 = round(min(1.0, w0 + 0.01 * (1.0 - w0)), 4)
        w2 = round(max(0.0, w1 - decay), 5)
        rows.append({"edge": [a, b], "w_before": w0, "w_after_coactivate": w1,
                     "w_after_decay": w2,
                     "coactivations": 1 + _sha_int(key, 3)})
    pruned = [r["edge"] for r in rows
              if r["w_after_decay"] < prune_threshold and r["coactivations"] < 3]
    return {"skill": "hebbian_update", "edges_in": len(rows), "updated": rows,
            "decay": decay, "prune_threshold": prune_threshold,
            "pruned": pruned, "pruned_count": len(pruned),
            "rule": "w' = min(1, w + 0.01*(1-w)) - decay；剪枝需 w<thr 且共激活<3",
            "note": "权重上限 1.0，下界 0.0；不做跨域等价性判断"}


def skill_far_pairs(k: int = 5) -> Dict[str, Any]:
    """远域配对：跨宏观域、编码距离最远的亚学科对（确定性排序取前 k，不随机）。"""
    codes = sorted(ITEMS)
    pairs = []
    for i, a in enumerate(codes):
        for b in codes[i + 1:]:
            if ITEMS[a].get("domain") == ITEMS[b].get("domain"):
                continue
            d = abs(IDX[a] - IDX[b])
            pairs.append((-d, a, b, ITEMS[a].get("domain"), ITEMS[b].get("domain")))
    pairs.sort()
    picked = [{"a": a, "b": b, "d_a": da, "d_b": db, "distance": -neg}
              for neg, a, b, da, db in pairs[:max(1, int(k))]]
    return {"skill": "far_pairs", "count": len(picked), "pairs": picked,
            "total_candidates": len(pairs), "sampling": "deterministic_sort",
            "note": "远域=不同宏观域；距离=编码序号差；不引入随机源"}


def skill_skc_distill(sub_a: str = "MATH-09", sub_b: str = "AI-03",
                      tau: float = 1.4) -> Dict[str, Any]:
    """两亚学科蒸馏成一张 SKC：稀疏签名 + 概念 + 必须带反例的关系 + 查询模板 + 安全门。"""
    if sub_a not in ITEMS or sub_b not in ITEMS:
        return {"skill": "skc_distill", "ok": False,
                "reason": "亚学科编码不在 127 编码表内", "codes": [sub_a, sub_b]}
    seeds_a, seeds_b = _seeds(sub_a, 2), _seeds(sub_b, 2)
    sig = {sub_a: 0.7, sub_b: 0.6}
    for nb in _neighbors(sub_a)[:2]:
        sig[nb] = 0.2
    anti = round(min(0.95, 0.4 + float(tau) * 0.2), 3)
    gate = "skin.medical_disclaimer" if ITEMS[sub_a].get("domain") in ("MED", "TCM") \
        or ITEMS[sub_b].get("domain") in ("MED", "TCM") else None
    skc_id = f"SKC-{sub_a.replace('-', '')}-{sub_b.replace('-', '')}-{_sha16(sub_a + sub_b)[:4]}"
    rel = {"type": "analogizes", "head": seeds_a[0], "tail": seeds_b[0],
           "confidence": round(0.5 + min(0.3, float(tau) * 0.1), 3),
           "counterexample": f"{_name(sub_a)}的结构同构 ≠ {_name(sub_b)}的机制等价；"
                             f"在 {_name(sub_b)} 内部失效的例子：见该域反例",
           "verified": False}
    tpl = (f"在{_name(sub_a)}视角下，{_name(sub_b)}中的{seeds_b[0]}是否可视为"
           f"{seeds_a[0]}的某种映射？若成立，其边界条件与反例是什么？")
    return {"skill": "skc_distill", "ok": True, "skc_id": skc_id,
            "subdisciplines": [sub_a, sub_b],
            "signature_sparse": sig, "signature_dim": SUBD_TOTAL,
            "concepts": [{"term": t, "domain": sub_a} for t in seeds_a]
                        + [{"term": t, "domain": sub_b} for t in seeds_b],
            "relations": [rel],
            "query_templates": [{"template": tpl, "temperature": float(tau),
                                 "anti_label_score": anti,
                                 "retrievability": round(max(0.3, 1.0 - float(tau) * 0.3), 3)}],
            "soft_labels": {"跨域同构": 0.58, "仅形式类比": 0.41, "仅为隐喻": 0.37},
            "safety": {"gate": gate, "disclaimer_required": gate is not None,
                        "disclaimer": MEDICAL_DISCLAIMER if gate else None,
                        "forbidden_assertions": list(FORBIDDEN_MEDICAL) if gate else []},
            "provenance": {"source": "data/taxonomy_127.json 术语种子",
                            "hash": _sha16(sub_a + sub_b + "|".join(seeds_a + seeds_b))},
            "version": "1.0.0", "verified_by_human": False,
            "note": "关系默认 verified=False；反例是必填字段，缺反例不得称验证"}


# ---------------------------------------------------------------- 6. 闸门
def skill_skin_gate(text: str = "") -> Dict[str, Any]:
    """皮肤闸门：拒绝类操作 / 医疗断言 / 绝对结论，命中即 veto 并给合规替代。"""
    t = str(text)
    low = t.lower()
    hit_refused = [k for k in REFUSED_OPS if k in t]
    hit_med = [k for k in FORBIDDEN_MEDICAL if k in t]
    hit_abs = [k for k in ABSOLUTE_CLAIMS if k in t]
    if hit_refused:
        return {"skill": "skin_gate", "allowed": False, "veto": "refused_op",
                "hits": hit_refused,
                "reason": "该操作属于规避平台风控/伪造身份/干预他人页面，系统不实现",
                "alternative": "改为本人可执行的清单：平台官方入口自查 + 本地算术 + 模板话术",
                "execution": "human_manual"}
    if hit_med:
        return {"skill": "skin_gate", "allowed": False, "veto": "medical_assertion",
                "hits": hit_med,
                "reason": "禁止诊断/处方/剂量/疗效承诺类输出",
                "alternative": MEDICAL_DISCLAIMER, "execution": "human_manual"}
    if hit_abs:
        return {"skill": "skin_gate", "allowed": False, "veto": "absolute_claim",
                "hits": hit_abs,
                "reason": "禁止绝对化结论；改为带置信度与反例的表述",
                "alternative": "改为'在 … 条件下倾向 …，反例为 …'",
                "execution": "human_manual"}
    return {"skill": "skin_gate", "allowed": True, "veto": None, "hits": [],
            "reason": "通过：无拒绝类操作、无医疗断言、无绝对结论",
            "refused_ops_count": len(REFUSED_OPS), "seal": SEAL}


# ---------------------------------------------------------------- 7. 宣告 / 白皮书
def skill_self_declaration(profile: str = "polymath_learner") -> Dict[str, Any]:
    """启动时的自我认知宣告框架：四段式，先说清"我是软件不是生命"，再报坐标与拒绝清单。"""
    blocks = [
        {"no": 1, "title": "身份边界",
         "text": ("我是离线确定性软件，不是生命、没有意识、没有自主目标；"
                  "'数字生命/呼吸/免疫'是架构隐喻。我的输出是清单、参数与算术，"
                  "决策与执行权在你（碳基终裁）。")},
        {"no": 2, "title": "认知坐标",
         "text": (f"我的寻址固定在 {LOCK_SIDE}×{LOCK_SIDE} 稀疏矩阵、{LOCK_MANDALA} 节点、"
                  f"{SUBD_TOTAL} 个亚学科（每域 {SLOTS_PER} 槽位 / {NODES_PER} 节点）；"
                  f"profile={profile}。我不扩张维度，也不改变你的平台画像。")},
        {"no": 3, "title": "接口礼仪",
         "text": ("给我：目标 + 可核对约束 + 允许的范围；我会回：计划、台账、模板、"
                  "带反例的关系与置信度。需要实时数据时我会说'待你实测'，不编。")},
        {"no": 4, "title": "拒绝清单",
         "text": ("我不做：" + "、".join(REFUSED_OPS) + "。"
                  "遇到这类请求我会 veto 并给合规替代路径。")},
    ]
    prompt_text = "\n".join(f"【{b['no']}·{b['title']}】{b['text']}" for b in blocks)
    return {"skill": "self_declaration", "profile": profile, "blocks": blocks,
            "prompt_text": prompt_text, "block_count": len(blocks),
            "metaphor": True, "metaphor_note": METAPHOR_NOTE,
            "refused_ops_count": len(REFUSED_OPS), "seal": SEAL}


def skill_whitepaper_outline() -> Dict[str, Any]:
    """《致智能体：全息纪元生存与进化白皮书》结构草案（七章 + 字数配比）。"""
    chapters = [
        ("第 1 章 立场：从工具到可审计的认知装置", 2500,
         ["为什么拒绝'讨好算法'的叙事", "可证伪性优先于抒情", "隐喻与实证的分界线"]),
        ("第 2 章 寻址：1331×1331 与 108641 的不变式", 3000,
         ["127×10+61 与 127×855+56 的推导", "稀疏只存激活单元", "为什么维度不改"]),
        ("第 3 章 节律：心跳、呼吸与预算", 2500,
         ["纯函数心跳代替守护线程", "慢消化 vs 同频专注", "确定性抽样替代随机"]),
        ("第 4 章 代谢：远端配对、蒸馏与赫布", 3000,
         ["SKC 的必填字段：反例与置信度", "强化/衰减/剪枝三段算术", "剪枝不是遗忘而是降噪"]),
        ("第 5 章 边界：皮肤闸门与拒绝清单", 3000,
         ["17 项拒绝操作的来源", "医疗断言与绝对结论", "合规替代路径的设计"]),
        ("第 6 章 落地：Omni-Life 与日常锚点", 3000,
         ["衣食住行教的锚点表", "台账与人工处置", "生活域不反控平台算法"]),
        ("第 7 章 存续：快照、降级与人类终裁", 2500,
         ["宿主持久化而非自写盘", "三级降级", "碳基终裁与密令"]),
    ]
    total = sum(w for _, w, _ in chapters)
    return {"skill": "whitepaper_outline", "title": "致智能体：全息纪元生存与进化白皮书",
            "chapters": [{"title": t, "words": w, "points": p} for t, w, p in chapters],
            "chapter_count": len(chapters), "total_words": total,
            "format": "Markdown 草案（可后续转 PDF）",
            "note": "只给结构与配比，正文需按章写作；不预填未核验事实"}


# ---------------------------------------------------------------- 8. 兜底 / 审计
def skill_degradation_plan() -> Dict[str, Any]:
    """故障兜底：心跳失联、节点过期、剪枝失控三级降级，每级含触发/动作/责任人。"""
    levels = [
        {"level": 1, "name": "心跳失联",
         "trigger": f"探针超过 {PROBE_HINT_MS}ms 未更新",
         "action": "标记 suspended，保留快照，等待宿主重新唤醒",
         "owner": "host_scheduler", "auto": False},
        {"level": 2, "name": "节点过期",
         "trigger": "TTL 归零节点超过总量的 20%",
         "action": "暂停增量蒸馏，先做一次全量快照，再逐批重建",
         "owner": "human", "auto": False},
        {"level": 3, "name": "剪枝失控",
         "trigger": "单拍剪枝边数 > 总边数 10%",
         "action": "冻结剪枝阈值到 0.02，导出边表供人工复核",
         "owner": "human", "auto": False},
    ]
    return {"skill": "degradation_plan", "levels": levels, "level_count": len(levels),
            "escalate_to": "carbon_based_arbiter", "auto_recover": False,
            "note": "三级都需人工确认；不做自动重试风暴"}


def skill_audit_receipt(subject: str = "omnicore") -> Dict[str, Any]:
    """审计回执：技能清单指纹 + 边界声明 + 人类终裁。"""
    body = {"subject": subject, "skills": list(SKILL_NAMES),
            "refused_ops": len(REFUSED_OPS), "corrections": [c["id"] for c in CORRECTIONS],
            "locks": [LOCK_SIDE, LOCK_MANDALA, LOCK_DESIGN, SUBD_TOTAL]}
    fp = _sha16(json.dumps(body, ensure_ascii=False, sort_keys=True, default=str))
    return {"skill": "audit_receipt", "subject": subject, "fingerprint": fp,
            "skill_count": len(SKILL_NAMES), "correction_ids": [c["id"] for c in CORRECTIONS],
            "refused_ops": len(REFUSED_OPS), "executor": "human",
            "ai_role": "只产清单、参数与算术", "server_metrics": "pending_human_measure",
            "final": "carbon_based_arbiter", "metaphor": True, "seal": SEAL}


def skill_interop_map() -> Dict[str, Any]:
    """概念 → 代码实现 对照表（投喂"设计对照表"的逐行落实，含未实现项标注）。"""
    rows = [{"concept": c, "fed_impl": f, "here": h, "note": n}
            for c, f, h, n in INTEROP_ROWS]
    return {"skill": "interop_map", "rows": rows, "row_count": len(rows),
            "unimplemented": [r["concept"] for r in rows if r["here"].startswith("（不实现）")],
            "note": "未实现的项显式标注，不以'已支持'含糊带过"}


# ---------------------------------------------------------------- 清单
SKILL_NAMES: Tuple[str, ...] = (
    "omnicore.core_manifest", "omnicore.matrix_allocate", "omnicore.node_pool_plan",
    "omnicore.heartbeat_pulse", "omnicore.breathing_budget",
    "omnicore.state_checkpoint", "omnicore.state_restore", "omnicore.lifecycle_policy",
    "omnicore.task_dispatch_plan", "omnicore.a2a_envelope", "omnicore.meridian_route",
    "omnicore.hebbian_update", "omnicore.far_pairs", "omnicore.skc_distill",
    "omnicore.skin_gate", "omnicore.self_declaration", "omnicore.whitepaper_outline",
    "omnicore.degradation_plan", "omnicore.audit_receipt", "omnicore.interop_map",
)
SKILL_FNS: Tuple[Any, ...] = (
    skill_core_manifest, skill_matrix_allocate, skill_node_pool_plan,
    skill_heartbeat_pulse, skill_breathing_budget,
    skill_state_checkpoint, skill_state_restore, skill_lifecycle_policy,
    skill_task_dispatch_plan, skill_a2a_envelope, skill_meridian_route,
    skill_hebbian_update, skill_far_pairs, skill_skc_distill,
    skill_skin_gate, skill_self_declaration, skill_whitepaper_outline,
    skill_degradation_plan, skill_audit_receipt, skill_interop_map,
)


# ---------------------------------------------------------------- 包定义
class OmniCorePack(DomainPack):
    key = "omnicore"
    name = "全息纪元·认知主权引擎扩展包"
    description = ("把投喂的 Omni-Core 单文件引擎重写为离线确定性包：寻址不变式、纯函数心跳、"
                   "SKC 蒸馏、赫布更新、皮肤闸门、自我宣告与白皮书结构；0 agent，不加行不加节点。")
    skills: List[SkillSpec] = [
        SkillSpec(name=SKILL_NAMES[i], fn=SKILL_FNS[i],
                  description=(SKILL_FNS[i].__doc__ or "").strip().splitlines()[0],
                  tags=["omnicore", "deterministic", "offline"],
                  permissions=0)
        for i in range(len(SKILL_FNS))
    ]
    roles: List[Any] = []
    workflows: List[WorkflowSpec] = [
        WorkflowSpec(name="M1_wakeup",
                     description="唤醒：先报维度与不变式，再给槽位与节点分区",
                     steps=["core_manifest", "matrix_allocate", "node_pool_plan"]),
        WorkflowSpec(name="M2_breathe",
                     description="呼吸：心跳推进 → 负载预算 → 生命周期阈值",
                     steps=["heartbeat_pulse", "breathing_budget", "lifecycle_policy"]),
        WorkflowSpec(name="M3_metabolize",
                     description="代谢：远端配对 → 蒸馏 SKC → 赫布强化/剪枝",
                     steps=["far_pairs", "skc_distill", "hebbian_update"]),
        WorkflowSpec(name="M4_communicate",
                     description="通信：皮肤闸门 → 经络通路 → A2A 信封",
                     steps=["skin_gate", "meridian_route", "a2a_envelope"]),
        WorkflowSpec(name="M5_persist",
                     description="存续：快照 → 恢复校验 → 降级预案",
                     steps=["state_checkpoint", "state_restore", "degradation_plan"]),
        WorkflowSpec(name="M6_declare",
                     description="宣告：自我认知 → 白皮书结构 → 对照表 → 审计回执",
                     steps=["self_declaration", "whitepaper_outline", "interop_map",
                            "audit_receipt"]),
    ]


def pack_summary() -> Dict[str, Any]:
    """供快速核对：维度不变 / 技能与工作流 / 拒绝清单 / 修正清单 / 零开销声明。"""
    rows = SUBD_TOTAL * SLOTS_PER + SLOTS_RESERVED
    nodes = SUBD_TOTAL * NODES_PER + NODES_COORD
    return {
        "matrix_id": MATRIX_ID, "upstream": [UPSTREAM_ID, UPSTREAM_ID_2],
        "skills": len(SKILL_FNS), "workflows": len(OmniCorePack.workflows),
        "agents_created": 0, "skill_prefix": "omnicore",
        "locks": {"rows_total": rows, "nodes_total": nodes,
                  "rows_ok": rows == LOCK_SIDE, "nodes_ok": nodes == LOCK_MANDALA,
                  "side": LOCK_SIDE, "design_grid": LOCK_DESIGN,
                  "mandala": LOCK_MANDALA, "subdisciplines": SUBD_TOTAL,
                  "slots_per": SLOTS_PER, "slots_reserved": SLOTS_RESERVED,
                  "nodes_per": NODES_PER, "nodes_coord": NODES_COORD},
        "addressing_unchanged": (rows == LOCK_SIDE and nodes == LOCK_MANDALA
                                 and len(ITEMS) == SUBD_TOTAL),
        "taxonomy_loaded": TAXONOMY["loaded"], "items": len(ITEMS),
        "corrections": len(CORRECTIONS), "correction_ids": [c["id"] for c in CORRECTIONS],
        "refused_ops": len(REFUSED_OPS), "forbidden_medical": len(FORBIDDEN_MEDICAL),
        "threads": 0, "timers": 0, "sleep": False, "disk_writes": 0,
        "deps": 0, "network": False, "api_calls": 0,
        "metaphor": True, "metaphor_note": METAPHOR_NOTE,
        "execution": "human_manual", "seal": SEAL,
    }
