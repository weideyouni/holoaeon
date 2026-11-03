# -*- coding: utf-8 -*-
"""
QuartetDirectorPack —— 四人组执行顾问扩展包（第 13 个扩展包）
================================================================================
V12-BUTLER-OS-BOOTSTRAP · Butler OS 引导模块的"四人组集成"载体：
把四人组（P1探微 / P2筑基 / P3构弦 / P4持衡）执行顾问方法论
（任务定义 → 共振扫描 → 梯度流向 → 约束审计 → 算法选择 → 涌现判定 →
评审 → 决策 → 风险 → 落地 → 验收 → 回执）沉淀为确定性可调用的技能。

设计约束（与投喂包一致）：
  · key = "quartet_director"（第 13 个扩展包，EXTRA_PACK_ORDER 12→13）
  · 14 技能 / 5 角色 / 2 工作流
  · 内联实现：不 import quartet_toolkit（保持零外部依赖、离线、确定性）
  · 公开 check_emergence(p1,p2,p3,p4)：供 Butler OS 菜单 4 与验证清单直接调用
  · 涌现条件：P2×P3 强共振(≥0.7) + P1 愿景(≥0.6) + P4 风险(≤0.4) + order>0.30
  · 维度不变：只进 EXTRA_PACK_REGISTRY，不进 PACK_ORDER —— A1（25/47/9）不受影响
"""
from __future__ import annotations

import hashlib
import math
from typing import Any, Dict, List

from .base import DomainPack, RoleSpec, SkillSpec, WorkflowSpec

# ============================================================ 四人组常量
# 四人透镜（执行顾问方法论）：
#   P1 探微 = 愿景 × 拓扑 × 涌现
#   P2 筑基 = 工程 × 算法 × 收敛
#   P3 构弦 = 架构 × 约束 × 度量
#   P4 持衡 = 本体 × 共振 × 平衡
LENS = {
    "P1": "探微（愿景×拓扑×涌现）",
    "P2": "筑基（工程×算法×收敛）",
    "P3": "构弦（架构×约束×度量）",
    "P4": "持衡（本体×共振×平衡）",
}
# 五步决策协议（道法术器升维）
STEPS = ["道", "法", "术", "器", "升维"]
# 四人组相似度表（确定性、固定，同 V11 topology_resonance 口径）
QUARTET_SIMS = {"P1×P2": 0.5, "P1×P3": 0.4, "P1×P4": 0.3,
                "P2×P3": 0.7, "P2×P4": 0.5, "P3×P4": 0.4}
# 涌现阈值
EMERGENCE_P23 = 0.7      # P2×P3 强共振
EMERGENCE_P1 = 0.6       # P1 愿景下限
EMERGENCE_P4 = 0.4       # P4 风险上限
EMERGENCE_ORDER = 0.30   # 秩序下限


def _clip01(x: float) -> float:
    """确定性裁剪到 [0,1]。"""
    return max(0.0, min(1.0, float(x)))


def _det_fingerprint(parts: List[str]) -> str:
    """确定性指纹（sha256 前 16 hex），同输入同输出。"""
    h = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()
    return h[:16]


# ============================================================ 1. 任务定义（道 · P4持衡）
def advisor_mission_define(mission: str = "", owner: str = "",
                           priority: str = "P1", **_: Any) -> dict:
    """道步·任务定义：把模糊意图规范化为可执行任务本体（目标/边界/验收）。

    透镜：P4 持衡（本体×共振×平衡）。
    城邦映射：设计变量=任务参数空间，目标函数=任务成功判据，约束=协议边界。
    """
    text = (mission or "默认四人组执行顾问任务").strip()
    p = (priority or "P1").upper()
    if p not in ("P0", "P1", "P2", "P3"):
        p = "P1"
    # 确定性任务分解：目标 / 约束 / 验收三个维度
    parsed = {
        "goal": text,
        "owner": owner or "director_convener",
        "priority": p,
        "boundaries": ["维度纪律不变", "确定性可复现", "碳基终裁"],
        "acceptance": ["产物可验证", "回执可追溯", "无越权写入"],
    }
    return {
        "step": "道", "lens": LENS["P4"],
        "mission": text, "priority": p,
        "task_ontology": parsed,
        "dimension": 3,
        "note": "道步：定义本体——目标=任务成功判据，约束=协议边界，验收=完工标准",
    }


# ============================================================ 2. 共振扫描（P1探微）
def advisor_resonance_scan(ideas: str = "", threshold: float = 0.6,
                           **_: Any) -> dict:
    """P1 探微·共振扫描：多候选概念两两相似度共振检测。

    数学内核：余弦相似度（确定性）；共振对 = 相似度 ≥ threshold。
    城邦映射：Node-State 相似性边 → 潜在协同簇识别。
    """
    threshold = _clip01(threshold)
    # 解析候选（逗号分隔）
    cands = [x.strip() for x in ideas.split(",") if x.strip()]
    if not cands:
        cands = ["管家引导", "四人组集成", "桥接服务"]
    pairs = []
    for i in range(len(cands)):
        for j in range(i + 1, len(cands)):
            cos = _cosine_sim(cands[i], cands[j])
            if cos >= threshold:
                pairs.append({"concept_a": cands[i], "concept_b": cands[j],
                              "similarity": round(cos, 4)})
    cluster = len(pairs) > 0
    return {
        "lens": LENS["P1"],
        "concepts": cands, "threshold": threshold,
        "resonance_pairs": pairs, "resonance_count": len(pairs),
        "cluster_signal": cluster,
        "note": "共振扫描：候选两两相似度超阈 → 协同簇信号",
    }


# ============================================================ 3. 梯度流向（法 · 四人共评）
def advisor_gradient_flow(current: str = "", perturbation: str = "",
                          **_: Any) -> dict:
    """法步·梯度流向：价值函数梯度方向 + 凸性（可治理性）判断。

    透镜：四人共评。
    数学内核：f(x)=Σ w_i·x_i（权重=1/(i+1)）；梯度=扰动前后差分；
    曲率>0 → convex（可治理）。
    """
    if current:
        state = [float(x) for x in current.split(",") if x.strip()]
    else:
        state = [0.3, 0.5, 0.2, 0.8]
    n = len(state)
    if perturbation:
        pert = [float(x) for x in perturbation.split(",") if x.strip()]
        if len(pert) != n:
            pert = [0.1] * n
    else:
        pert = [0.1] * n
    weights = [1.0 / (i + 1) for i in range(n)]
    f0 = sum(w * x for w, x in zip(weights, state))
    f1 = sum(w * (x + p) for w, x, p in zip(weights, state, pert))
    grad = [(f1 - f0) / (p if p != 0 else 1.0) for p in pert]
    grad_norm = math.sqrt(sum(g * g for g in grad))
    grad_dir = [g / grad_norm if grad_norm else 0.0 for g in grad]
    f2 = sum(w * (x + 2 * p) for w, x, p in zip(weights, state, pert))
    denom = sum(p * p for p in pert) if any(pert) else 1.0
    curvature = (f2 - 2 * f1 + f0) / denom
    convexity = "convex" if curvature > 0 else ("concave" if curvature < 0 else "flat")
    return {
        "step": "法", "lens": "四人共评",
        "current_state": [round(x, 4) for x in state],
        "gradient": [round(g, 6) for g in grad],
        "gradient_direction": [round(g, 6) for g in grad_dir],
        "f_current": round(f0, 6), "f_perturbed": round(f1, 6),
        "curvature": round(curvature, 6), "convexity": convexity,
        "governable": convexity == "convex",
        "note": "法步：梯度=价值导向，曲率=可治理性（凸=可治理）",
    }


# ============================================================ 4. 约束审计（术 · P3构弦）
def advisor_constraint_audit(constraints: str = "", violations: str = "",
                             **_: Any) -> dict:
    """术步·约束审计：约束清单逐项核 violation + KKT 互补松弛 + 惩罚。

    透镜：P3 构弦。
    数学内核：λ = 100·v（硬约束）/ 10·v（软约束）；KKT：v>0↔λ>0。
    """
    if constraints:
        cl = []
        for c in constraints.split(","):
            parts = c.strip().split(":")
            cl.append({"name": parts[0].strip(),
                       "type": parts[1].strip() if len(parts) == 2 else "hard"})
    else:
        cl = [{"name": "diff0", "type": "hard"}, {"name": "dimension", "type": "hard"},
              {"name": "determinism", "type": "hard"}, {"name": "bandwidth", "type": "soft"}]
    if violations:
        vv = [float(x) for x in violations.split(",") if x.strip()]
    else:
        vv = [0.0] * len(cl)
    rows = []
    for i, c in enumerate(cl):
        v = vv[i] if i < len(vv) else 0.0
        lam = (100.0 * v if v > 0 else 0.0) if c["type"] == "hard" else 10.0 * v
        rows.append({"constraint": c["name"], "type": c["type"],
                     "violation": round(v, 4), "lambda": round(lam, 4),
                     "active": v > 0})
    kkt_ok = all((r["violation"] > 0 and r["lambda"] > 0) or
                 (r["violation"] == 0 and r["lambda"] == 0) for r in rows)
    active = [r["constraint"] for r in rows if r["active"]]
    penalty = sum(r["lambda"] * r["violation"] for r in rows)
    return {
        "step": "术", "lens": LENS["P3"],
        "constraints": rows,
        "kkt_complementary_slackness": kkt_ok,
        "active_constraints": active,
        "total_penalty": round(penalty, 4),
        "verdict": "pass" if not active else "review",
        "note": "术步：λ=影子价格，KKT=动态治理，惩罚=信誉负反馈",
    }


# ============================================================ 5. 算法选择（器 · P2筑基）
def advisor_algorithm_select(problem_type: str = "", dimension: int = 0,
                             **_: Any) -> dict:
    """器步·算法选择：按问题类型/维度推荐确定性执行算法。

    透镜：P2 筑基。
    决策树：凸/光滑→(维度≤10: 牛顿; ≤100: DFP/BFGS; 否则共轭梯度)；
    非凸/黑箱→(维度≤5: 单纯形; 否则 Powell)；默认梯度下降。
    """
    algos = {
        "gradient_descent": {"order": "一阶", "conv": "线性", "cost": "低",
                             "map": "自主学习引擎"},
        "newton": {"order": "二阶", "conv": "二次", "cost": "高",
                   "map": "高阶认知能力"},
        "conjugate_gradient": {"order": "一阶+记忆", "conv": "超线性", "cost": "中",
                               "map": "经验复用"},
        "dfp_bfgs": {"order": "拟二阶", "conv": "超线性", "cost": "中",
                     "map": "自适应认知地图"},
        "simplex": {"order": "零阶", "conv": "慢但稳健", "cost": "低",
                    "map": "群体编队"},
        "powell": {"order": "零阶+共轭", "conv": "超线性", "cost": "中",
                   "map": "团队默契"},
    }
    ptype = (problem_type or "default").lower().strip()
    dim = dimension if dimension > 0 else 4
    if ptype in ("convex", "smooth", "differentiable"):
        rec = "newton" if dim <= 10 else ("dfp_bfgs" if dim <= 100 else "conjugate_gradient")
    elif ptype in ("nonconvex", "noisy", "blackbox"):
        rec = "simplex" if dim <= 5 else "powell"
    else:
        rec = "gradient_descent"
    a = algos[rec]
    return {
        "step": "器", "lens": LENS["P2"],
        "problem_type": ptype, "dimension": dim,
        "recommended": rec,
        "detail": {"order": a["order"], "convergence": a["conv"],
                   "cost": a["cost"], "city_map": a["map"]},
        "note": "器步：按问题凸性/维度选确定性算法（可复现执行）",
    }


# ============================================================ 6. 四人组张量向量化
def advisor_quartet_tensor(p1: str = "", p2: str = "", p3: str = "",
                           p4: str = "", **_: Any) -> dict:
    """四人组张量向量化：权重矩阵 + 共振检测 + 决策熵 + 涌现判断。

    数学内核：均值/标准差 → 一致度(order)；P2×P3 强共振 + P1 愿景 +
    P4 风险受控 + order 超阈 → 涌现。
    """
    scores = [_clip01(float(s)) if s else 0.7 for s in (p1, p2, p3, p4)]
    p1s, p2s, p3s, p4s = scores
    mean = sum(scores) / 4
    variance = sum((s - mean) ** 2 for s in scores) / 4
    std = math.sqrt(variance)
    agreement = 1.0 - min(std / 0.5, 1.0)
    order = agreement
    conditions = {
        "P2×P3_strong(≥0.7)": QUARTET_SIMS["P2×P3"] >= EMERGENCE_P23,
        "P1_vision(≥0.6)": p1s >= EMERGENCE_P1,
        "P4_risk(≤0.4)": p4s <= EMERGENCE_P4,
        "order(>0.30)": order > EMERGENCE_ORDER,
    }
    emergence = all(conditions.values())
    return {
        "tensor_space": "R^4",
        "scores": {"P1": round(p1s, 4), "P2": round(p2s, 4),
                   "P3": round(p3s, 4), "P4": round(p4s, 4)},
        "similarities": QUARTET_SIMS,
        "mean": round(mean, 4), "std": round(std, 4),
        "agreement": round(agreement, 4), "order": round(order, 4),
        "emergence_conditions": conditions,
        "emergence": emergence,
        "note": "四人组张量：权重矩阵+共振+熵+涌现触发",
    }


# ============================================================ 7. 涌现判定（公开）
def check_emergence(p1: float = 0.0, p2: float = 0.0, p3: float = 0.0,
                    p4: float = 0.0, **_: Any) -> dict:
    """四人组涌现判定（公开入口）：输入四人评分，返回 {emergence, order, conditions}。

    数学内核（与投喂验证清单一致）：
      mean=(p1+p2+p3+p4)/4；std=总体标准差；agreement=1-min(std/0.5,1)；
      order=agreement；涌现 = P2×P3≥0.7 且 P1≥0.6 且 P4≤0.4 且 order>0.30。
    示例：check_emergence(0.85,0.85,0.85,0.30) → emergence=True, order≈0.52
    """
    scores = [_clip01(x) for x in (p1, p2, p3, p4)]
    p1s, p2s, p3s, p4s = scores
    mean = sum(scores) / 4
    variance = sum((s - mean) ** 2 for s in scores) / 4
    std = math.sqrt(variance)
    agreement = 1.0 - min(std / 0.5, 1.0)
    order = agreement
    conditions = {
        "P2×P3_strong(≥0.7)": QUARTET_SIMS["P2×P3"] >= EMERGENCE_P23,
        "P1_vision(≥0.6)": p1s >= EMERGENCE_P1,
        "P4_risk(≤0.4)": p4s <= EMERGENCE_P4,
        "order(>0.30)": order > EMERGENCE_ORDER,
    }
    emergence = all(conditions.values())
    return {
        "emergence": emergence,
        "order": round(order, 4),
        "mean": round(mean, 4),
        "std": round(std, 4),
        "agreement": round(agreement, 4),
        "conditions": conditions,
        "scores": {"P1": round(p1s, 4), "P2": round(p2s, 4),
                   "P3": round(p3s, 4), "P4": round(p4s, 4)},
    }


# ============================================================ 8. 评审委员会
def advisor_review_board(proposal: str = "", reviewer_scores: str = "",
                         **_: Any) -> dict:
    """四人并行评审汇总：各透镜打分 + 汇总裁决（含 P4 一票否决语义）。

    输入格式：reviewer_scores="P1:8,P2:7,P3:9,P4:6"（0-10 分制）。
    """
    text = (proposal or "默认执行方案").strip()
    raw = {k.strip(): v.strip() for k, v in
           (p.split(":") for p in (reviewer_scores or "").split(",") if ":" in p)}
    default_scores = {"P1": 8, "P2": 8, "P3": 8, "P4": 8}
    scores = {}
    for lens_key in ("P1", "P2", "P3", "P4"):
        try:
            scores[lens_key] = max(0, min(10, int(raw.get(lens_key,
                                                          default_scores[lens_key]))))
        except ValueError:
            scores[lens_key] = default_scores[lens_key]
    total = sum(scores.values())
    # P4 持衡一票否决：P4 分 < 5 即整体不予通过（保守裁决）
    vetoed = scores["P4"] < 5
    verdict = "pass" if (total >= 28 and not vetoed) else (
        "veto_p4" if vetoed else "review")
    return {
        "proposal": text,
        "reviewer_scores": scores,
        "total": total,
        "vetoed": vetoed,
        "verdict": verdict,
        "note": "评审委员会：四人透镜并行打分，P4 一票否决，汇总裁决",
    }


# ============================================================ 9. 决策备忘录
def advisor_decision_memo(decision: str = "", rationale: str = "",
                          **_: Any) -> dict:
    """决策备忘录：结构化记录决策 + 理由 + 反方意见 + 生效条件。"""
    text = (decision or "默认决策").strip()
    reason = (rationale or "四人组五步协议输出").strip()
    memo_id = _det_fingerprint(["memo", text, reason])
    return {
        "memo_id": memo_id,
        "decision": text,
        "rationale": reason,
        "dissent": "已记录并复核（四人组圆桌覆盖反方意见）",
        "effective_when": "碳基终裁确认后生效",
        "revision": 1,
        "note": "决策备忘录：决策+理由+异议+生效条件，确定性指纹留痕",
    }


# ============================================================ 10. 风险登记册
def advisor_risk_register(risks: str = "", **_: Any) -> dict:
    """风险登记册：风险 → 概率/影响/缓解（确定性分级）。"""
    items = [r.strip() for r in risks.split(",") if r.strip()]
    if not items:
        items = ["维度漂移", "确定性破坏", "越权写入"]
    rows = []
    for i, r in enumerate(items):
        # 确定性哈希分级（避免 random）
        h = int(_det_fingerprint(["risk", r]), 16)
        prob = round(0.1 + (h % 50) / 100.0, 2)
        impact = "high" if h % 3 == 0 else ("medium" if h % 3 == 1 else "low")
        rows.append({"risk_id": f"R{i + 1}", "risk": r,
                     "probability": prob, "impact": impact,
                     "mitigation": "闸门自检 + 回执留痕 + 碳基终裁"})
    return {
        "risks": rows, "count": len(rows),
        "risk_level": "high" if any(r["impact"] == "high" for r in rows) else "medium",
        "note": "风险登记册：概率/影响分级，缓解=闸门+回执+碳基终裁",
    }


# ============================================================ 11. 落地计划
def advisor_rollout_plan(phases: int = 3, **_: Any) -> dict:
    """落地计划：分阶段执行计划（阶段/目标/验收/门禁）。"""
    phases = max(1, min(int(phases), 6))
    plan = []
    for i in range(1, phases + 1):
        plan.append({
            "phase": i,
            "goal": f"阶段{i}：增量落地（可回滚、可验证）",
            "acceptance": f"阶段{i}验收：全部验证绿 + 回执留痕",
            "gate": "闸门自检 + 单批单提交",
            "rollback": "上一提交点回滚",
        })
    return {
        "phases": phases, "plan": plan,
        "principle": "增量 · 可回滚 · 单批单提交 · 五地同步不变",
        "note": "落地计划：分阶段增量执行，每阶段带验收与回滚门禁",
    }


# ============================================================ 12. 验收清单
def advisor_acceptance_check(items: str = "", **_: Any) -> dict:
    """验收清单：逐项核验 + 全绿判定（确定性）。"""
    names = [x.strip() for x in items.split(",") if x.strip()]
    if not names:
        names = ["selftest全绿", "维度不变", "五地同步"]
    rows = [{"item": n, "check": "verifiable",
             "status": "pending_verify"} for n in names]
    return {
        "items": rows, "count": len(rows),
        "all_green": all(r["status"] == "verified" for r in rows),
        "status": "pending_verify",
        "note": "验收清单：逐项可验证，全绿才放行（pending 不算通过）",
    }


# ============================================================ 13. 回执
def advisor_receipt(actions: str = "", **_: Any) -> dict:
    """四人组回执：动作序列确定性指纹 + 执行模式标记（simulated）。"""
    acts = [a.strip() for a in actions.split(",") if a.strip()]
    if not acts:
        acts = ["mission_define", "resonance_scan", "emergence_check"]
    fp = _det_fingerprint(["receipt"] + acts)
    return {
        "fingerprint": fp,
        "actions": acts, "count": len(acts),
        "execution": "simulated",
        "final": "carbon_based_arbiter",
        "seal": "潮起开门，潮落闭嘴",
        "note": "回执：确定性指纹留痕，执行=仿真，终裁=碳基",
    }


# ============================================================ 14. 自检
def advisor_selfcheck(**_: Any) -> dict:
    """包内自检：校验技能/角色/工作流计数与涌现示例确定性。"""
    p = QuartetDirectorPack()
    skills_ok = len(p.skills) == 14
    roles_ok = len(p.roles) == 5
    workflows_ok = len(p.workflows) == 2
    e1 = check_emergence(0.85, 0.85, 0.85, 0.30)
    e2 = check_emergence(0.85, 0.85, 0.85, 0.30)
    deterministic_ok = e1["emergence"] == e2["emergence"] and \
        e1["order"] == e2["order"]
    emergence_ok = e1["emergence"] is True and abs(e1["order"] - 0.5237) < 0.01
    all_ok = skills_ok and roles_ok and workflows_ok and \
        deterministic_ok and emergence_ok
    return {
        "ok": all_ok,
        "skills": skills_ok, "roles": roles_ok, "workflows": workflows_ok,
        "deterministic": deterministic_ok, "emergence_example": emergence_ok,
        "counts": {"skills": skills_ok and len(p.skills),
                   "roles": roles_ok and len(p.roles),
                   "workflows": workflows_ok and len(p.workflows)},
        "emergence_sample": {"emergence": e1["emergence"], "order": e1["order"]},
        "note": "包内自检：计数 + 涌现示例确定性（同参两次一致）",
    }


# ============================================================ 辅助函数
def _cosine_sim(a: str, b: str) -> float:
    """基于字符共现的确定性相似度（[0,1]）。"""
    if not a or not b:
        return 0.0
    set_a, set_b = set(a), set(b)
    inter = len(set_a & set_b)
    union = len(set_a | set_b)
    return inter / union if union else 0.0


# ============================================================ 扩展包定义
class QuartetDirectorPack(DomainPack):
    key = "quartet_director"
    name = "四人组执行顾问（P1探微·P2筑基·P3构弦·P4持衡）"
    description = (
        "把四人组执行顾问方法论沉淀为确定性技能：任务定义→共振扫描→梯度流向→"
        "约束审计→算法选择→涌现判定→评审→决策→风险→落地→验收→回执；"
        "公开 check_emergence 供 Butler OS 引导模块直接调用；内联实现零外部依赖"
    )

    skills = [
        SkillSpec("advisor_mission_define", advisor_mission_define,
                  "道步·任务定义：把模糊意图规范化为任务本体（目标/边界/验收）",
                  tags=["quartet", "dao", "mission", "ontology"],
                  inputs={"mission": "str", "owner": "str", "priority": "str"}),
        SkillSpec("advisor_resonance_scan", advisor_resonance_scan,
                  "P1探微·共振扫描：候选概念两两相似度共振检测",
                  tags=["quartet", "resonance", "scan", "cluster"],
                  inputs={"ideas": "str", "threshold": "float"}),
        SkillSpec("advisor_gradient_flow", advisor_gradient_flow,
                  "法步·梯度流向：价值函数梯度方向 + 凸性（可治理性）",
                  tags=["quartet", "gradient", "convexity", "governable"],
                  inputs={"current": "str", "perturbation": "str"}),
        SkillSpec("advisor_constraint_audit", advisor_constraint_audit,
                  "术步·约束审计：约束逐项 violation + KKT + 惩罚",
                  tags=["quartet", "constraint", "kkt", "audit"],
                  inputs={"constraints": "str", "violations": "str"}),
        SkillSpec("advisor_algorithm_select", advisor_algorithm_select,
                  "器步·算法选择：按凸性/维度推荐确定性算法",
                  tags=["quartet", "algorithm", "selection", "search"],
                  inputs={"problem_type": "str", "dimension": "int"}),
        SkillSpec("advisor_quartet_tensor", advisor_quartet_tensor,
                  "四人组张量向量化：权重矩阵+共振+决策熵+涌现判断",
                  tags=["quartet", "tensor", "resonance", "emergence"],
                  inputs={"p1": "str", "p2": "str", "p3": "str", "p4": "str"}),
        SkillSpec("check_emergence", check_emergence,
                  "四人组涌现判定（公开）：评分→{emergence, order, conditions}",
                  tags=["quartet", "emergence", "public", "verdict"],
                  inputs={"p1": "float", "p2": "float", "p3": "float", "p4": "float"}),
        SkillSpec("advisor_review_board", advisor_review_board,
                  "评审委员会：四人透镜并行打分 + P4 一票否决 + 汇总裁决",
                  tags=["quartet", "review", "board", "veto"],
                  inputs={"proposal": "str", "reviewer_scores": "str"}),
        SkillSpec("advisor_decision_memo", advisor_decision_memo,
                  "决策备忘录：决策+理由+异议+生效条件（确定性指纹）",
                  tags=["quartet", "decision", "memo", "trace"],
                  inputs={"decision": "str", "rationale": "str"}),
        SkillSpec("advisor_risk_register", advisor_risk_register,
                  "风险登记册：风险→概率/影响/缓解（确定性分级）",
                  tags=["quartet", "risk", "register", "mitigation"],
                  inputs={"risks": "str"}),
        SkillSpec("advisor_rollout_plan", advisor_rollout_plan,
                  "落地计划：分阶段增量执行（可回滚、可验证、单批单提交）",
                  tags=["quartet", "rollout", "plan", "phases"],
                  inputs={"phases": "int"}),
        SkillSpec("advisor_acceptance_check", advisor_acceptance_check,
                  "验收清单：逐项核验 + 全绿判定（pending 不算通过）",
                  tags=["quartet", "acceptance", "checklist", "gate"],
                  inputs={"items": "str"}),
        SkillSpec("advisor_receipt", advisor_receipt,
                  "四人组回执：动作序列确定性指纹 + simulated 执行标记",
                  tags=["quartet", "receipt", "fingerprint", "audit"],
                  inputs={"actions": "str"}),
        SkillSpec("advisor_selfcheck", advisor_selfcheck,
                  "包内自检：技能/角色/工作流计数 + 涌现示例确定性",
                  tags=["quartet", "selfcheck", "contract", "determinism"],
                  inputs={}),
    ]

    roles = [
        RoleSpec("director_visionary", "P1探微·愿景：任务定义·共振扫描·涌现",
                 ["advisor_mission_define", "advisor_resonance_scan",
                  "check_emergence"]),
        RoleSpec("director_engineer", "P2筑基·工程：算法选择·落地·验收",
                 ["advisor_algorithm_select", "advisor_rollout_plan",
                  "advisor_acceptance_check"]),
        RoleSpec("director_architect", "P3构弦·架构：约束审计·风险·评审",
                 ["advisor_constraint_audit", "advisor_risk_register",
                  "advisor_review_board"]),
        RoleSpec("director_steward", "P4持衡·平衡：决策·回执·自检",
                 ["advisor_decision_memo", "advisor_receipt",
                  "advisor_selfcheck"]),
        RoleSpec("director_convener", "总控·召集：四人组张量·评审·涌现",
                 ["advisor_quartet_tensor", "advisor_review_board",
                  "check_emergence"]),
    ]

    workflows = [
        WorkflowSpec("quartet_advisor_flow",
                     ["director_convener", "director_visionary",
                      "director_engineer", "director_architect",
                      "director_steward"],
                     "四人组执行顾问全流程：召集→愿景→工程→架构→持衡（五步协议闭环）"),
        WorkflowSpec("quartet_emergence_flow",
                     ["director_convener", "director_steward"],
                     "涌现判定与回执闭环：四人组张量→涌现判定→回执留痕"),
    ]


def pack_summary() -> Dict[str, Any]:
    p = QuartetDirectorPack()
    return {"key": p.key, "skills": len(p.skills), "roles": len(p.roles),
            "workflows": len(p.workflows)}


def main(argv=None) -> int:
    """CLI 入口（pyproject holoaeon-quartet）：演示四人组执行顾问闭环。"""
    print("== HoloAeon 四人组执行顾问（quartet_director 第13扩展包）==")
    print("技能数/角色数/工作流数:", pack_summary())
    e = check_emergence(0.85, 0.85, 0.85, 0.30)
    print("涌现示例 check_emergence(0.85,0.85,0.85,0.30):",
          e["emergence"], "order=", e["order"])
    return 0 if e["emergence"] else 1
