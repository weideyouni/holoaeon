# -*- coding: utf-8 -*-
"""
SovereigntyPack —— 认知主权包（HoloAeon 横切扩展包，第十包）
================================================================================
来源：cognitive-sovereignty 1331×1331 矩阵 V3.0
      （SG-MASTER-COGNITIVE-SOVEREIGNTY-1331x1331-SUPER-MAS-V3.0，2026-10-30）

定位：把"反算法刻板印象·主动认知塑形"作为**横切扩展**注入引擎——
  17 个技能 = 17 个认知主权通道（SO-01…SO-17）
  5 条工作流 = R0 编码 / R1 锻造 / R2 策略 / R3 互操作 / R4 合规
  0 个角色 = **不建 agent**（上游 G15 断言 n_agents==25 是硬约束，故只注册技能）

红线（写进实现，不是口号）：
  · 纯标准库、确定性、离线；不联网、不开端口、不登录、不抓取、不常驻
  · 平台侧指标一律 pending_human_measure（零伪造）
  · 一切"执行"列恒为 human_manual（人类终裁）
"""
from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Tuple

from .base import DomainPack, SkillSpec, WorkflowSpec

# ---------------------------------------------------------------- 常量（与母体 V3 对齐）
MATRIX_ID = "SG-MASTER-COGNITIVE-SOVEREIGNTY-1331x1331-SUPER-MAS-V3.0"
DOMAIN = "sovereign"
LOCK_SIDE = 1331
LOCK_DESIGN = 1771561
LOCK_MANDALA = 108641
LOCK_HILBERT = 651846
LOCK_KALMAN = 22627
HEARTBEAT_BASE, HEARTBEAT_COUNT, HEARTBEAT_DIM = 9700, 70, 768

CHANNELS: Tuple[str, ...] = (
    "tensor_vector_encoding", "cross_domain_binding", "identity_fingerprint",
    "ontology_graph_addr", "query_forging", "template_engine", "semantic_density",
    "unpredictability_schedule", "label_profile_inference", "anti_stereotype_strategy",
    "feedback_loop_calibration", "inner_protocol_fusion", "outer_protocol_fusion",
    "platform_adapter_registry", "compliance_gate", "audit_reproducibility",
    "human_final_arbiter",
)

INNER_PROTOCOLS: Tuple[Tuple[str, str], ...] = (
    ("ENV", "统一信封"), ("BUS", "消息总线"), ("SKL", "技能注册表"),
    ("MEM", "三层记忆"), ("HBT", "全息心跳"), ("SKN", "皮肤闸门"),
    ("GRP", "协作图"), ("CLS", "并行 Actor"), ("HVEC", "超向量"),
    ("MADP", "模型适配"), ("TBUS", "线程域锁"), ("SODP", "数据协议"),
)

OUTER_PROTOCOLS: Tuple[Tuple[str, str], ...] = (
    ("HTTP", "HTTP/REST"), ("OPENAPI", "OpenAPI/Schema"), ("GRAPHQL", "GraphQL"),
    ("GRPC", "gRPC/HTTP2"), ("REALTIME", "实时推送"), ("MCP", "MCP 工具协议"),
    ("A2A", "Agent 互操作"), ("LLMAPI", "大模型 API"), ("FEED", "订阅分发"),
    ("IDENTITY", "身份授权"), ("FEDIVERSE", "开放社交"),
)

FAMILIES: Tuple[Tuple[str, str], ...] = (
    ("short_stream", "短视频与直播"), ("long_video", "长视频与影视"),
    ("feed_community", "图文与社区"), ("search_qa", "搜索与问答"),
    ("social_im", "社交与即时通讯"), ("commerce_local", "电商与本地生活"),
    ("knowledge_pro", "知识与专业平台"), ("llm_cn", "大模型平台·国内"),
    ("llm_intl", "大模型平台·海外"), ("dev_open", "开源与开发者生态"),
)

DUTIES: Tuple[str, ...] = (
    "搜索锻造", "深链浏览", "长文阅读", "跨域跳转", "身份声明", "反标签复盘", "协议取证",
    "密度评估", "兴趣拓扑重排", "冷启动破圈", "长尾覆盖", "多端一致性", "审计留痕",
)

DOMAINS_16: Tuple[str, ...] = (
    "数学", "物理学", "逻辑学", "计算机科学", "人工智能", "生物学", "医学", "中医",
    "哲学", "历史学与考古学", "文学", "美学", "符号学", "社会学", "未来科技", "科幻",
)

BLOCKED_TERMS: Tuple[str, ...] = (
    "自动注入", "自动发帖", "批量发帖", "抓取", "刷量", "养号", "规避风控",
    "绕过验证", "伪造身份", "多账号", "破解", "自动登录", "接口调用",
)

TEMPLATES: Tuple[str, ...] = (
    "从{a}的角度看{b}，它是否构成{c}？这对{d}的边界意味着什么？",
    "如果{a}可以被{b}重述，那么{c}在{d}中承担什么角色？",
    "{a}与{b}之间是否存在可形式化的对应关系？这对{c}的设计有何启示？",
    "把{a}当作{b}的特例，{c}会因此失去还是获得解释力？请以{d}为参照。",
)


# ---------------------------------------------------------------- 确定性工具
def _seed(name: str, dim: int = HEARTBEAT_DIM) -> List[int]:
    raw = hashlib.sha256(f"{DOMAIN}:{name}".encode("utf-8")).digest()
    out = []
    for i in range(dim):
        byte = raw[i % len(raw)]
        out.append(1 if (byte >> (i % 8)) & 1 else -1)
    return out


def _cosine(a: List[int], b: List[int]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    return 0.0 if na == 0 or nb == 0 else dot / (na * nb)


def _bind(a: List[int], b: List[int]) -> List[int]:
    return [x * y for x, y in zip(a, b)]


def _bundle(vecs: List[List[int]]) -> List[int]:
    dim = len(vecs[0])
    out = []
    for i in range(dim):
        total = sum(v[i] for v in vecs)
        out.append(1 if total >= 0 else -1)
    return out


def _sha16(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16].upper()


def _density(text: str) -> float:
    """语义密度：唯一字符占比 × 长度饱和因子（0-1，确定性）。"""
    if not text:
        return 0.0
    uniq = len(set(text))
    sat = min(len(text), 120) / 120
    return round(min(1.0, (uniq / max(1, len(text))) * 1.6 * (0.4 + 0.6 * sat)), 4)


# ---------------------------------------------------------------- 17 技能
def skill_tensor_encode(name: str = "数学") -> dict:
    """SO-01 张量向量化编码：名字 → 768 维双极超向量指纹。"""
    v = _seed(name)
    return {"channel": CHANNELS[0], "name": name, "dim": len(v),
            "bipolar": set(v) <= {1, -1}, "fingerprint": _sha16("".join(map(str, v[:32]))),
            "self_cosine": round(_cosine(v, v), 6), "simulated": True}


def skill_cross_bind(a: str = "数学", b: str = "人工智能") -> dict:
    """SO-02 跨域绑定与叠加：两域超向量的 bind/bundle 与余弦。"""
    va, vb = _seed(a), _seed(b)
    bound = _bind(va, vb)
    bundled = _bundle([va, vb])
    return {"channel": CHANNELS[1], "pair": [a, b],
            "cos_pair": round(_cosine(va, vb), 4),
            "cos_bind_a": round(_cosine(bound, va), 4),
            "cos_bundle_a": round(_cosine(bundled, va), 4), "simulated": True}


def skill_identity_fingerprint(text: str = "我是一名终身学习者") -> dict:
    """SO-03 身份指纹与自述：文本 → 16 位指纹 + 密度分。"""
    return {"channel": CHANNELS[2], "fingerprint": _sha16(text),
            "density": _density(text), "simulated": True}


def skill_ontology_addr(family: str = "short_stream", channel: str = "query_forging",
                        protocol: str = "MCP") -> dict:
    """SO-04 本体图谱寻址：族×通道×协议 → 1331×1331 稀疏网格坐标。"""
    fam_keys = [f[0] for f in FAMILIES]
    fi = fam_keys.index(family) if family in fam_keys else 0
    ci = CHANNELS.index(channel) if channel in CHANNELS else 0
    all_proto = [p[0] for p in INNER_PROTOCOLS] + [p[0] for p in OUTER_PROTOCOLS]
    pi = all_proto.index(protocol) if protocol in all_proto else 0
    row = (fi * 17 + ci) % LOCK_SIDE
    col = pi % LOCK_SIDE
    return {"channel": CHANNELS[3], "row": row, "col": col,
            "design": LOCK_DESIGN, "sparse": True, "simulated": True}


def skill_forge_query(seed: str = "0", domains: List[str] | None = None) -> dict:
    """SO-05 查询锻造：确定性种子 → 跨域查询文本（同种子逐字一致）。"""
    doms = domains or list(DOMAINS_16)[:3]
    h = int(hashlib.sha256(f"forge:{seed}".encode("utf-8")).hexdigest()[:8], 16)
    a, b = doms[h % len(doms)], doms[(h // 7 + 1) % len(doms)]
    c = doms[(h // 53 + 2) % len(doms)]
    d = doms[(h // 7919 + 3) % len(doms)]
    tpl = TEMPLATES[h % len(TEMPLATES)]
    text = tpl.format(a=a, b=b, c=c, d=d)
    return {"channel": CHANNELS[4], "text": text,
            "domains": [a, b, c, d], "density": _density(text), "simulated": True}


def skill_template_list() -> dict:
    """SO-06 模板引擎：列出可用查询模板。"""
    return {"channel": CHANNELS[5], "templates": list(TEMPLATES), "count": len(TEMPLATES)}


def skill_semantic_density(text: str = "") -> dict:
    """SO-07 语义密度评分。"""
    return {"channel": CHANNELS[6], "density": _density(text),
            "chars": len(text), "uniq": len(set(text))}


def skill_plan_slots(seed: str = "0", days: int = 3, per_day: int = 3) -> dict:
    """SO-08 不可预测性调度：只产计划表，不注册任何定时器。"""
    h = int(hashlib.sha256(f"plan:{seed}".encode("utf-8")).hexdigest()[:8], 16)
    slots = []
    for d in range(days):
        for i in range(per_day):
            hour = (h % 8 + 9 + i * 4 + d) % 22 + 1
            minute = (h // 11 + i * 20 + d * 7) % 60
            slots.append(f"{d + 1}日 {hour:02d}:{minute:02d}")
    return {"channel": CHANNELS[7], "slots": slots, "unique": len(set(slots)) == len(slots),
            "auto": False, "execution": "human_manual", "simulated": True}


def skill_label_hint(observations: List[str] | None = None) -> dict:
    """SO-09 标签画像反推（启发式，非平台真实标签）。"""
    obs = observations or []
    if not obs:
        return {"channel": CHANNELS[8], "labels": [],
                "status": "pending_human_measure", "simulated": True}
    rules = (("娱乐短视频偏好", ("短视频", "搞笑", "娱乐")),
             ("明星八卦偏好", ("明星", "八卦", "综艺")),
             ("带货消费偏好", ("带货", "直播", "购物")))
    hits = []
    for label, kws in rules:
        score = sum(1 for o in obs for k in kws if k in o)
        if score:
            hits.append({"label": label, "evidence": score})
    hits.sort(key=lambda x: -x["evidence"])
    return {"channel": CHANNELS[8], "labels": hits,
            "basis": "用户手填观测的关键词启发式", "simulated": True}


def skill_anti_stereotype_plan() -> dict:
    """SO-10 反刻板策略：7 条，全部 human_manual。"""
    items = [
        ("S1", "跨域跳跃", "每天换一个完全不同族的平台"),
        ("S2", "深度不可压缩", "只用 3 学科以上组合查询"),
        ("S3", "语义密度", "优先密度 ≥0.45 的查询"),
        ("S4", "哲学声明", "在可发布文本处粘贴学习自述，不自称官方"),
        ("S5", "只搜不点", "检索后不点前三项推荐位"),
        ("S6", "长链阅读", "只打开可读 ≥8 分钟的长文"),
        ("S7", "不可预测", "同一查询不连续两天重复"),
    ]
    return {"channel": CHANNELS[9],
            "items": [{"id": i, "name": n, "action": a, "execution": "human_manual"}
                      for i, n, a in items],
            "auto": False, "simulated": True}


def skill_calibrate(observations: List[str] | None = None) -> dict:
    """SO-11 反馈闭环校准：按观测升级/维持/拒绝。"""
    obs = observations or []
    if not obs:
        return {"channel": CHANNELS[10], "verdict": "refuse", "reason": "无观测，不校准",
                "simulated": True}
    low = any(("短视频" in o or "搞笑" in o) for o in obs)
    good = any(("长文" in o or "论文" in o or "深度" in o) for o in obs)
    verdict = "escalate" if low and not good else ("maintain" if good else "escalate")
    return {"channel": CHANNELS[10], "verdict": verdict,
            "priority": ["S1", "S7", "S3"] if verdict == "escalate" else ["S4"],
            "simulated": True}


def skill_inner_protocols() -> dict:
    """SO-12 内部协议融通：12 条。"""
    return {"channel": CHANNELS[11], "count": len(INNER_PROTOCOLS),
            "items": [{"key": k, "name": n} for k, n in INNER_PROTOCOLS]}


def skill_outer_protocols() -> dict:
    """SO-13 外部协议融通：11 族 + 132 映射单元 + 不联网。"""
    return {"channel": CHANNELS[12], "count": len(OUTER_PROTOCOLS),
            "items": [{"key": k, "name": n} for k, n in OUTER_PROTOCOLS],
            "cells": len(INNER_PROTOCOLS) * len(OUTER_PROTOCOLS), "network": False}


def skill_platform_families() -> dict:
    """SO-14 平台适配注册：10 族 × 13 职责 = 130 入口。"""
    return {"channel": CHANNELS[13], "families": len(FAMILIES),
            "entries": len(FAMILIES) * len(DUTIES),
            "items": [{"key": k, "name": n, "entries": len(DUTIES)} for k, n in FAMILIES],
            "permission": "human_manual_only"}


def skill_compliance_gate(text: str = "") -> dict:
    """SO-15 合规边界闸门：拒绝词命中即 veto。"""
    hits = [t for t in BLOCKED_TERMS if t in text]
    return {"channel": CHANNELS[14], "allowed": not hits, "veto": hits,
            "text_len": len(text), "simulated": True}


def skill_audit_fingerprint(payload: str = "") -> dict:
    """SO-16 审计与可复现：16 位指纹。"""
    return {"channel": CHANNELS[15], "fingerprint": _sha16(payload),
            "reproducible": _sha16(payload) == _sha16(payload)}


def skill_human_receipt(what: str = "查询清单") -> dict:
    """SO-17 人类终裁回执：所有结论的最终裁决权在人。"""
    return {"channel": CHANNELS[16], "subject": what,
            "executor": "human", "ai_role": "只产文本清单",
            "platform_metrics": "pending_human_measure", "final": "carbon_based_arbiter"}


SKILL_FNS = (
    skill_tensor_encode, skill_cross_bind, skill_identity_fingerprint, skill_ontology_addr,
    skill_forge_query, skill_template_list, skill_semantic_density, skill_plan_slots,
    skill_label_hint, skill_anti_stereotype_plan, skill_calibrate, skill_inner_protocols,
    skill_outer_protocols, skill_platform_families, skill_compliance_gate,
    skill_audit_fingerprint, skill_human_receipt,
)


class SovereigntyPack(DomainPack):
    key = "sovereignty"
    name = "认知主权包"
    description = ("反算法刻板印象·主动认知塑形：17 通道技能 + R0-R4 五条工作流；"
                   "只注册不建 agent，平台侧一律 pending_human_measure。")
    skills: List[SkillSpec] = [
        SkillSpec(name=CHANNELS[i], fn=SKILL_FNS[i],
                  description=(SKILL_FNS[i].__doc__ or "").strip().splitlines()[0],
                  tags=["sovereignty", "cognitive", "offline"],
                  permissions=0)
        for i in range(len(CHANNELS))
    ]
    roles: List = []                        # 关键：0 角色 → 不新增 agent
    workflows: List[WorkflowSpec] = [
        WorkflowSpec("R0_encoding", [], "编码：平台×协议×通道 → 网格地址 + 768 维超向量"),
        WorkflowSpec("R1_forging", [], "锻造：16 学科跨域组合 → 可复现查询文本"),
        WorkflowSpec("R2_strategy", [], "策略：反标签自测清单 → 本人手动执行"),
        WorkflowSpec("R3_interop", [], "互操作：23 协议族 → 统一信封映射（离线）"),
        WorkflowSpec("R4_compliance", [], "合规：闸门拦截 → 审计留痕 → 人类终裁"),
    ]


def pack_summary() -> Dict[str, Any]:
    """供快速核对：锁数 / 通道 / 协议 / 族谱 / 技能数。"""
    return {
        "matrix_id": MATRIX_ID,
        "locks": {"side": LOCK_SIDE, "design": LOCK_DESIGN, "mandala": LOCK_MANDALA,
                  "hilbert": LOCK_HILBERT, "kalman": LOCK_KALMAN},
        "heartbeat": {"base": HEARTBEAT_BASE, "count": HEARTBEAT_COUNT, "dim": HEARTBEAT_DIM},
        "channels": len(CHANNELS), "inner": len(INNER_PROTOCOLS),
        "outer": len(OUTER_PROTOCOLS), "families": len(FAMILIES),
        "entries": len(FAMILIES) * len(DUTIES), "skills": len(SKILL_FNS),
        "agents_created": 0, "human_final": True,
    }
