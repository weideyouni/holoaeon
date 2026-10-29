# -*- coding: utf-8 -*-
"""
SubdistillPack —— SD-Distill 亚学科辅助蒸馏包（HoloAeon 横切扩展包，第十一包）
================================================================================
来源：cognitive-sovereignty 1331×1331 矩阵 V3.1
      （SG-MASTER-COGNITIVE-SOVEREIGNTY-1331x1331-SUPER-MAS-V3.1，2026-10-30）

定位：把 16 大学科继续下切为 127 个亚学科，用"辅助教师 + 七阶段蒸馏"把材料炼成
      亚学科知识卡（SKC）、跨域共振映射与抗标签查询模板，供查询锻造与反标签调用。

  14 个技能 = 分类 3 + 教师 1 + 管线 7（S1-S7）+ 损失 1 + 课程 1 + 反标签 1 + SKC 校验 1
  7 条工作流 = S1 采集 → S7 验证入库
  0 个角色 = 不建 agent（上游 G15 断言 n_agents==25 是硬约束）

维度不变（写入断言）：
  127 × 10 = 1270 主干槽位 + 61 保留 = 1331 行
  127 × 855 = 108585 子图节点 + 56 全局协调 = 108641 节点

红线：纯标准库、确定性、离线；不联网、不登录、不抓取、不常驻；
      MED/TCM 必须挂免责声明；analogizes 必带反例；平台指标 pending_human_measure。
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from typing import Any, Dict, List, Tuple

from .base import DomainPack, SkillSpec, WorkflowSpec

# ---------------------------------------------------------------- 常量
MATRIX_ID = "SG-MASTER-COGNITIVE-SOVEREIGNTY-1331x1331-SUPER-MAS-V3.1"
DOMAIN = "subdistill"
SUBD_TOTAL = 127
SUBD_DOMAINS = 16
LOCK_SIDE = 1331
LOCK_MANDALA = 108641
SLOTS_PER = 10
SLOTS_RESERVED = 61
NODES_PER = 855
NODES_COORD = 56
HEARTBEAT_BASE, HEARTBEAT_COUNT, HEARTBEAT_DIM = 9700, 70, 768
STAGES = ("S1_acquire", "S2_parse", "S3_concept", "S4_relate",
          "S5_align", "S6_distill", "S7_commit")
LOSS_WEIGHTS = {"alpha": 0.30, "beta": 0.20, "gamma": 0.15, "delta": 0.20,
                "epsilon": 0.08, "zeta": 0.05, "eta": 0.02}
CURRICULUM = (("C1_root", 0.6, 200), ("C2_neighbor", 0.9, 300),
              ("C3_far", 1.4, 400), ("C4_multi", 1.8, 300))
BURST = {"probability": 0.05, "tau": 2.5, "duration_epochs": 2}
RELATION_TYPES = ("is_a", "part_of", "maps_to", "contradicts", "analogizes", "constrains")
GATED_DOMAINS = ("MED", "TCM")
FORBIDDEN_ASSERTIONS = ("诊断", "处方", "疗效承诺")
DISCLAIMER = "仅作为知识框架与跨学科映射探讨，不构成诊疗建议"
SEAL = "潮起开门，潮落闭嘴"


# ---------------------------------------------------------------- 数据装载
def _repo_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _load_taxonomy() -> Dict[str, Any]:
    path = os.path.join(_repo_root(), "data", "taxonomy_127.json")
    if not os.path.exists(path):
        return {"items": [], "domains": [], "path": "", "loaded": False}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {"items": data["items"], "domains": data["domains"], "path": path, "loaded": True}


TAXONOMY = _load_taxonomy()
ITEMS: Dict[str, Dict[str, Any]] = {i["code"]: i for i in TAXONOMY["items"]}


def _sha16(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16].upper()


def _cos(a: Dict[str, float], b: Dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(v * b.get(k, 0.0) for k, v in a.items())
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    return 0.0 if na == 0 or nb == 0 else dot / (na * nb)


def _vocab(code: str) -> List[str]:
    it = ITEMS[code]
    return list(it["seeds"]) + [p for p in it["name"].split("与") if p] + [it["name"]]


def _encode(text: str) -> Dict[str, float]:
    raw: Dict[str, float] = {}
    for code in sorted(ITEMS):
        s = 0.0
        for v in _vocab(code):
            if v and v in text:
                s += 0.6 if v == ITEMS[code]["name"] else 1.0
        if s > 0:
            raw[code] = s
    if not raw:
        return {}
    tot = sum(raw.values())
    return {c: round(s / tot, 6) for c, s in sorted(raw.items())}


def _entropy(dist: Dict[str, float]) -> float:
    tot = sum(dist.values())
    if tot <= 0:
        return 0.0
    h = 0.0
    for v in dist.values():
        p = v / tot
        if p > 0:
            h -= p * math.log(p)
    return round(h, 6)


# ---------------------------------------------------------------- 3 分类技能
def skill_taxonomy_encode(text: str = "范畴论 与 大模型对齐") -> dict:
    """SD-D1 亚学科签名：文本 → 127 维稀疏签名（L1 归一）。"""
    sig = _encode(text)
    return {"skill": "taxonomy_encode", "dim": SUBD_TOTAL, "items": len(ITEMS),
            "signature": sig, "nonzero": len(sig),
            "top": sorted(sig, key=lambda k: (-sig[k], k))[:3],
            "loaded": TAXONOMY["loaded"], "simulated": True}


def skill_taxonomy_nearest(code: str = "MATH-09", k: int = 5) -> dict:
    """SD-D2 邻近亚学科：同域优先 + 签名余弦（C2 阶段用）。"""
    if code not in ITEMS:
        return {"skill": "taxonomy_nearest", "code": code, "neighbors": [],
                "error": "未知亚学科编码"}
    base = _encode(ITEMS[code]["name"] + " " + " ".join(ITEMS[code]["seeds"]))
    rows = []
    for other in sorted(ITEMS):
        if other == code:
            continue
        sig = _encode(ITEMS[other]["name"] + " " + " ".join(ITEMS[other]["seeds"]))
        rows.append((round(_cos(base, sig), 6),
                     1 if ITEMS[other]["domain"] == ITEMS[code]["domain"] else 0, other))
    rows.sort(key=lambda t: (-t[0], -t[1], t[2]))
    return {"skill": "taxonomy_nearest", "code": code,
            "neighbors": [{"code": c, "cos": v, "same_domain": bool(s)} for v, s, c in rows[:k]],
            "simulated": True}


def skill_taxonomy_far_pairs(min_cos: float = 0.02, limit: int = 100) -> dict:
    """SD-D3 远域配对：跨宏观域且余弦低于阈值（C3/C4 阶段用）。"""
    sigs = {c: _encode(ITEMS[c]["name"] + " " + " ".join(ITEMS[c]["seeds"]))
            for c in sorted(ITEMS)}
    out = []
    codes = sorted(ITEMS)
    for i, a in enumerate(codes):
        for b in codes[i + 1:]:
            if ITEMS[a]["domain"] == ITEMS[b]["domain"]:
                continue
            c = _cos(sigs[a], sigs[b])
            if c <= min_cos:
                out.append({"a": a, "b": b, "cos": round(c, 6)})
    out.sort(key=lambda d: (d["cos"], d["a"], d["b"]))
    return {"skill": "taxonomy_far_pairs", "count": len(out),
            "pairs": out[:limit], "min_cos": min_cos, "simulated": True}


# ---------------------------------------------------------------- 1 教师技能
def skill_teacher_card(code: str = "MATH-09") -> dict:
    """SD-D3 辅助教师卡：语料锚点/概念卡/关系模板/提问范式/反例/置信度。"""
    if code not in ITEMS:
        return {"skill": "teacher_card", "code": code, "error": "未知亚学科编码"}
    it = ITEMS[code]
    gated = it["domain"] in GATED_DOMAINS
    return {"skill": "teacher_card", "code": code, "name": it["name"],
            "corpus_anchors": [f"{it['domain_cn']}/{it['name']}/ch{i:02d}" for i in (1, 2, 3)],
            "concept_cards": 60 + 7 * len(it["seeds"]),
            "question_paradigms": [
                f"把 {{{it['seeds'][0]}}} 视为 {{{it['domain_cn']}}} 中的对象，其对应什么？",
                f"{it['name']} 在远域视角下是否构成同构？",
            ],
            "counterexamples": ["跨域同构 ≠ 物理等价（必须先给反例）"],
            "confidence": 0.86 if not gated else 0.78,
            "teacher_type": "TemplateTeacher",
            "safety_gate": "skin.medical_disclaimer" if gated else None,
            "disclaimer_required": gated, "simulated": True}


# ---------------------------------------------------------------- 7 管线技能
DEMO_LINES = [
    "# 范畴论与同调",
    "## 伴随函子的单位与余单位",
    "# 大模型与对齐",
    "## 偏好优化的对偶权衡",
    "# 证明论与类型论",
    "## 构造性证明与不可判定性",
]


def _depth(line: str) -> Tuple[int, str]:
    s = line.lstrip()
    if s.startswith("#"):
        return len(s) - len(s.lstrip("#")), s.lstrip("#").strip()
    return 1, s


def skill_s1_acquire(lines: List[str] | None = None) -> dict:
    """SD-S1 采集：材料目录 → 语料池（只算哈希与规模）。"""
    ls = [ln for ln in (lines or DEMO_LINES) if ln.strip()]
    return {"skill": STAGES[0], "lines": len(ls), "chars": sum(len(x) for x in ls),
            "hash": _sha16("\n".join(ls)), "network": False, "simulated": True}


def skill_s2_parse(lines: List[str] | None = None) -> dict:
    """SD-S2 结构化：目录层级 → 概念树骨架 + 亚学科打标。"""
    ls = [ln for ln in (lines or DEMO_LINES) if ln.strip()]
    nodes = []
    for ln in ls:
        d, text = _depth(ln)
        top = sorted(_encode(text), key=lambda k: (-_encode(text)[k], k))[:2]
        nodes.append({"term": text, "depth": d, "subdisciplines": top,
                      "primary": top[0] if top else None})
    classified = sum(1 for n in nodes if n["primary"])
    return {"skill": STAGES[1], "nodes": len(nodes), "classified": classified,
            "coverage": round(classified / max(len(nodes), 1), 4),
            "codes": sorted({n["primary"] for n in nodes if n["primary"]}),
            "simulated": True}


def skill_s3_concept(lines: List[str] | None = None) -> dict:
    """SD-S3 概念抽取：叶节点 → 概念节点（含来源与反例位）。"""
    ls = [ln for ln in (lines or DEMO_LINES) if ln.strip()]
    concepts = []
    for ln in ls:
        d, text = _depth(ln)
        top = sorted(_encode(text), key=lambda k: (-_encode(text)[k], k))[:1]
        concepts.append({"term": text, "depth": d,
                         "subdiscipline": top[0] if top else None,
                         "counterexamples": ["跨域类比须带反例"]})
    return {"skill": STAGES[2], "concepts": len(concepts), "sample": concepts[:3],
            "simulated": True}


def skill_s4_relate(lines: List[str] | None = None) -> dict:
    """SD-S4 关系抽取：父子 part_of + 归属 is_a。"""
    ls = [ln for ln in (lines or DEMO_LINES) if ln.strip()]
    nodes = [(_depth(ln)[0], _depth(ln)[1]) for ln in ls]
    edges = []
    for i, (d, t) in enumerate(nodes):
        for pd, pt in reversed(nodes[:i]):
            if pd < d:
                edges.append({"type": "part_of", "head": t, "tail": pt, "confidence": 0.92})
                break
    return {"skill": STAGES[3], "edges": len(edges),
            "types": sorted({e["type"] for e in edges}), "simulated": True}


def skill_s5_align(text: str = "范畴论与同调 大模型与对齐") -> dict:
    """SD-S5 跨域对齐：两码同现 → 共振映射单元（带反例否决）。"""
    codes = sorted(_encode(text))
    units = []
    for i, a in enumerate(codes):
        for b in codes[i + 1:]:
            if ITEMS[a]["domain"] == ITEMS[b]["domain"]:
                continue
            units.append({"a": a, "b": b, "type": "analogizes", "confidence": 0.6,
                          "counterexample": f"{ITEMS[a]['name']} ≠ {ITEMS[b]['name']}",
                          "verified": False})
    return {"skill": STAGES[4], "unit_count": len(units), "units": units, "codes": codes,
            "rule": "置信度<0.5 只可称隐喻", "simulated": True}


def skill_s6_distill(tau: float = 1.4) -> dict:
    """SD-S6 蒸馏：温度调度 → SKC（软标签 + 抗标签查询模板）。"""
    codes = sorted(_encode("范畴论与同调 大模型与对齐 证明论与类型论"))
    skcs = []
    for idx, code in enumerate(codes):
        it = ITEMS[code]
        gated = it["domain"] in GATED_DOMAINS
        soft = {"跨域同构": round(0.58 if tau <= 1.4 else 0.42, 4),
                "形式化可行": round(0.41 if tau <= 1.4 else 0.33, 4),
                "仅为隐喻": round(0.37 if tau <= 1.4 else 0.25, 4)}
        skcs.append({
            "skc_id": f"SKC-{code.replace('-', '')}-{idx + 1:04d}",
            "subdisciplines": [code], "signature_dim": SUBD_TOTAL,
            "signature_sparse": {code: 0.62},
            "concepts": [{"term": it["seeds"][0], "domain": code,
                          "definition": "教师库种子概念", "examples": [],
                          "counterexamples": ["跨域类比须带反例"]}],
            "relations": [{"type": "analogizes", "head": it["seeds"][0],
                           "tail": "远域对应物", "confidence": 0.55}],
            "query_templates": [{"template":
                                 f"在{{{it['name']}}}视角下，{{远域概念}}是否可视为"
                                 f"一对{{{it['seeds'][0]}}}？反例是什么？",
                                 "temperature": tau,
                                 "anti_label_score": 0.83, "retrievability": 0.69}],
            "soft_labels": soft,
            "provenance": [{"source": "目录骨架 + 教师库", "hash": _sha16(code)}],
            "safety": ({"gate": "skin.medical_disclaimer", "disclaimer_required": True,
                        "forbidden_assertions": list(FORBIDDEN_ASSERTIONS), "note": DISCLAIMER}
                       if gated else
                       {"gate": "skin.programmatic_analogy", "disclaimer_required": False,
                        "forbidden_assertions": list(FORBIDDEN_ASSERTIONS),
                        "note": "跨域类比必须带反例"}),
            "version": "0.1.0", "heartbeat_epoch": 0,
        })
    return {"skill": STAGES[5], "skcs": len(skcs), "tau": tau,
            "sample": skcs[0] if skcs else None, "simulated": True}


def skill_s7_commit(skcs: int = 3, blocked: int = 0) -> dict:
    """SD-S7 验证入库：皮肤门 + 去重 + 心跳纪元 + 平台指标 pending。"""
    committed = max(skcs - blocked, 0)
    return {"skill": STAGES[6], "in": skcs, "blocked": blocked, "committed": committed,
            "dedup": max(skcs - committed - blocked, 0),
            "epoch": 1, "platform_metrics": "pending_human_measure",
            "human_final": True, "simulated": True}


# ---------------------------------------------------------------- 1 损失技能
def skill_losses(measured: Dict[str, Any] | None = None) -> dict:
    """SD-L 七项辅助损失：保真/关系/跨域/新颖/可检索/安全/成本加权。"""
    m = measured or {"covered": 9, "total": 12, "tp": 7, "fp": 2, "fn": 1,
                     "mappable_p": 0.6, "max_hist_cos": 0.3, "retrievability": 0.7,
                     "gate_hits": 0, "tokens": 1200, "latency_ms": 40.0}
    fid = 1 - m["covered"] / max(m["total"], 1)
    prec = m["tp"] / max(m["tp"] + m["fp"], 1)
    rec = m["tp"] / max(m["tp"] + m["fn"], 1)
    f1 = 0.0 if prec + rec == 0 else 2 * prec * rec / (prec + rec)
    rel = 1 - f1
    cross = -math.log(1 - min(max(m["mappable_p"], 1e-6), 1 - 1e-6))
    novel = -_entropy({"a": 0.5, "b": 0.3, "c": 0.2}) + 0.5 * m["max_hist_cos"]
    retr = 1 - min(max(m["retrievability"], 0.0), 1.0)
    safe = min(1.0, m["gate_hits"] * 0.5)
    cost = min(1.0, m["tokens"] / 4096 * 0.6 + m["latency_ms"] / 2000 * 0.4)
    parts = {"alpha_fid": round(fid, 6), "beta_rel": round(rel, 6),
             "gamma_cross": round(cross, 6), "delta_novel": round(novel, 6),
             "epsilon_retr": round(retr, 6), "zeta_safe": round(safe, 6),
             "eta_cost": round(cost, 6)}
    total = (LOSS_WEIGHTS["alpha"] * fid + LOSS_WEIGHTS["beta"] * rel
             + LOSS_WEIGHTS["gamma"] * cross + LOSS_WEIGHTS["delta"] * novel
             + LOSS_WEIGHTS["epsilon"] * retr + LOSS_WEIGHTS["zeta"] * safe
             + LOSS_WEIGHTS["eta"] * cost)
    return {"skill": "losses", "parts": parts, "total": round(total, 6),
            "weights": LOSS_WEIGHTS, "adaptive_weights": True, "simulated": True}


# ---------------------------------------------------------------- 1 课程技能
def skill_curriculum(epoch: int = 0) -> dict:
    """SD-C 温度课程：C1 0.6 / C2 0.9 / C3 1.4 / C4 1.8 + 确定性温度冲击。"""
    bounds, acc = [], 0
    for name, tau, ep in CURRICULUM:
        acc += ep
        bounds.append((acc, name, tau, ep))
    e = max(int(epoch), 0) % acc
    cur = {"name": bounds[-1][1], "tau": bounds[-1][2], "epochs": bounds[-1][3]}
    for bound, name, tau, ep in bounds:
        if e < bound:
            cur = {"name": name, "tau": tau, "epochs": ep, "window": [bound - ep, bound - 1]}
            break
    h = int(_sha16(f"sd:{e}")[:8], 16)
    cur["epoch"] = e
    cur["burst"] = h % 100 < int(BURST["probability"] * 100)
    cur["total_epochs"] = acc
    cur["simulated"] = True
    return cur


# ---------------------------------------------------------------- 1 反标签技能
def skill_antilabel(queries: List[str] | None = None) -> dict:
    """SD-A 反标签指标：标签熵 / 主导权重 / 跳跃度 / 不可压缩度。"""
    qs = queries or ["范畴论 与 大模型对齐", "经络 与 生物物理 相干态"]
    sigs = [_encode(q) for q in qs]
    prof: Dict[str, float] = {}
    for sig in sigs:
        for k, v in sig.items():
            prof[k] = prof.get(k, 0.0) + v
    tot = sum(prof.values()) or 1.0
    jumps = [1 - _cos(sigs[i], sigs[i + 1]) for i in range(len(sigs) - 1)] or [0.0]
    return {"skill": "antilabel", "tag_entropy": _entropy(prof),
            "dominant_weight": round(max(prof.values(), default=0.0) / tot, 6),
            "jump_score": round(sum(jumps) / len(jumps), 6),
            "incompressibility": round(1 - max((_cos(s, prof and sigs[0]) for s in sigs),
                                               default=0.0), 6),
            "subdisciplines_touched": len(prof),
            "macro_domains_touched": len({k.split("-")[0] for k in prof}),
            "simulated": True}


# ---------------------------------------------------------------- 1 校验技能
def skill_skc_validate(skc: Dict[str, Any] | None = None) -> dict:
    """SD-V SKC 校验：必填字段 / 关系类型 / 反例 / 医学免责 / 禁用断言。"""
    skc = skc or skill_s6_distill(1.4)["sample"]
    errs = []
    for k in ("skc_id", "subdisciplines", "signature_dim", "signature_sparse",
              "concepts", "relations", "query_templates", "soft_labels",
              "provenance", "safety", "version", "heartbeat_epoch"):
        if k not in skc:
            errs.append(f"缺字段 {k}")
    if skc.get("signature_dim") not in (None, SUBD_TOTAL):
        errs.append("signature_dim 应为 127")
    for r in skc.get("relations", []):
        if r.get("type") not in RELATION_TYPES:
            errs.append(f"未知关系类型 {r.get('type')}")
    if any(str(d).split("-")[0] in GATED_DOMAINS for d in skc.get("subdisciplines", [])):
        if skc.get("safety", {}).get("disclaimer_required") is not True:
            errs.append("MED/TCM 未强制免责声明")
    blob_parts = [json.dumps(skc.get("concepts", []), ensure_ascii=False),
                  json.dumps(skc.get("relations", []), ensure_ascii=False),
                  json.dumps(skc.get("query_templates", []), ensure_ascii=False)]
    for bad in FORBIDDEN_ASSERTIONS:              # 只扫内容字段，扫 safety 会自伤规则本表
        if any(bad in part for part in blob_parts):
            errs.append(f"出现禁用断言词 {bad}")
    return {"skill": "skc_validate", "ok": not errs, "errors": errs}


SKILL_FNS = (
    skill_taxonomy_encode, skill_taxonomy_nearest, skill_taxonomy_far_pairs,
    skill_teacher_card,
    skill_s1_acquire, skill_s2_parse, skill_s3_concept, skill_s4_relate,
    skill_s5_align, skill_s6_distill, skill_s7_commit,
    skill_losses, skill_curriculum, skill_antilabel, skill_skc_validate,
)

SKILL_NAMES = (
    "subdistill.taxonomy_encode", "subdistill.taxonomy_nearest",
    "subdistill.taxonomy_far_pairs", "subdistill.teacher_card",
    "subdistill.s1_acquire", "subdistill.s2_parse", "subdistill.s3_concept",
    "subdistill.s4_relate", "subdistill.s5_align", "subdistill.s6_distill",
    "subdistill.s7_commit", "subdistill.losses", "subdistill.curriculum",
    "subdistill.antilabel", "subdistill.skc_validate",
)


class SubdistillPack(DomainPack):
    key = "subdistill"
    name = "SD-Distill 亚学科辅助蒸馏包"
    description = ("16 域 → 127 亚学科：分类/教师/七阶段蒸馏/七项损失/温度课程/反标签指标；"
                   "0 角色，不建 agent，MED·TCM 强制免责。")
    skills: List[SkillSpec] = [
        SkillSpec(name=SKILL_NAMES[i], fn=SKILL_FNS[i],
                  description=(SKILL_FNS[i].__doc__ or "").strip().splitlines()[0],
                  tags=["subdistill", "distillation", "offline"],
                  permissions=0)
        for i in range(len(SKILL_FNS))
    ]
    roles: List = []                        # 关键：0 角色 → 不新增 agent
    workflows: List[WorkflowSpec] = [
        WorkflowSpec("S1_acquire", [], "采集：教材目录/论文/课程 → 语料池（只算哈希）"),
        WorkflowSpec("S2_parse", [], "结构化：目录层级 → 概念树骨架 + 亚学科打标"),
        WorkflowSpec("S3_concept", [], "概念抽取：叶节点 → 概念节点（带来源/反例位）"),
        WorkflowSpec("S4_relate", [], "关系抽取：part_of / is_a 等六类关系"),
        WorkflowSpec("S5_align", [], "跨域对齐：两码同现 → 共振映射（反例否决）"),
        WorkflowSpec("S6_distill", [], "蒸馏：温度调度 → SKC + 软标签 + 抗标签模板"),
        WorkflowSpec("S7_commit", [], "入库：皮肤门 + 去重 + 心跳纪元 + 人类终裁"),
    ]


def pack_summary() -> Dict[str, Any]:
    """供快速核对：亚学科 / 槽位 / 节点 / 阶段 / 损失 / 技能数。"""
    return {
        "matrix_id": MATRIX_ID,
        "locks": {"subdisciplines": SUBD_TOTAL, "domains": SUBD_DOMAINS,
                  "slots": SUBD_TOTAL * SLOTS_PER, "reserved": SLOTS_RESERVED,
                  "rows_total": SUBD_TOTAL * SLOTS_PER + SLOTS_RESERVED,
                  "nodes": SUBD_TOTAL * NODES_PER, "coord": NODES_COORD,
                  "nodes_total": SUBD_TOTAL * NODES_PER + NODES_COORD},
        "rows_ok": SUBD_TOTAL * SLOTS_PER + SLOTS_RESERVED == LOCK_SIDE,
        "nodes_ok": SUBD_TOTAL * NODES_PER + NODES_COORD == LOCK_MANDALA,
        "heartbeat": {"base": HEARTBEAT_BASE, "count": HEARTBEAT_COUNT, "dim": HEARTBEAT_DIM},
        "stages": len(STAGES), "losses": len(LOSS_WEIGHTS),
        "curriculum": len(CURRICULUM), "skills": len(SKILL_FNS),
        "taxonomy_loaded": TAXONOMY["loaded"], "items": len(ITEMS),
        "agents_created": 0, "network": False, "gated_domains": list(GATED_DOMAINS),
        "seal": SEAL,
    }
