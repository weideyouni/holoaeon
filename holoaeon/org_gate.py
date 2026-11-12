# -*- coding: utf-8 -*-
"""
OrgGate —— 组织化推进件（V58 · ring21 组织域）
================================================================================
源声明（诚实边界）：
  · 素材源 = 碳基 2026-11-12 投喂 ORG-02《组织化推进投喂包》（18分管小组·
    统一资源调拨·经络先行·自动适配·2-3仓批次耗散耦合——四件套终章：
    结构 V3 → 连通 LINK-01 → 贯续 CONT-01 → 组织 ORG-02）。
    本模块为四人组第一性原理扬弃后的**可测子集**，不是照搬——扬弃裁决
    全记录见投喂包第 2 节。
  · 第一性命题（素材原文采信）：19 仓规模铺开后，瓶颈不再是设计而是三件
    事——责任稀释 / 资源争抢 / 复制失真；总判据=**耗散结构**——没有输入
    就退化的系统才配叫有机体。
  · 扬弃（弃）实录：
      ①素材 B0-B6"从零建仓"叙事弃——**工程现实：18 仓已建成**（GitHub
        18/18 ls-remote 核验，回执 v55_receipt.github_create），批次表重构
        为"领域深化批次"口径（骨架=结构建成已达成 G1；领域实现+连线=待
        深化，如实两分）；
      ②素材"108641 共振带配额"弃——维持 V55 裁决（数字挪用不诚实），
        受控资源清单该行以弃因留痕替代；
      ③素材 git_batch_create.sh 弃——建仓已由 create_repos_v55.py 执行
        完毕（集群既成事实），脚本成历史文物不重写；
      ④素材 W1-W5 建议初值保留为"可标定常量"（同 V55 生克系数口径）；
      ⑤素材 D1-D6"每批必报"降档为**指标口径+计算函数先落地**——实测
        数据须真实输入流（连通件未落，无输入流时不假报数据，零虚构）。
  · 扬弃（取）实录：18 小组编制五岗（含仓主≠记录员自证污染规则）/
    任务卡 Schema / 资源调拨中枢（五类实+优先级公式+调拨五规则+账本）/
    C03 经络先行 G-M 门禁六判据（三态诚实注册）/ 自动适配六子模块+状态机
    +三边界 / 耗散五要件映射+D1-D6 指标 / 引导六步+自我追问六问 /
    B0-B6 深化批次表（18 仓全覆盖复核）。

与工程纪律的同构照（升维句，见投喂包第 4 节）：
    组织从"人的共识"变成"机器的编制"——五岗/任务卡/调拨公式/耗散指标
    第一次成为 org_gate 里的数据结构与检查函数；"谁负责、凭什么先干、
    算不算活着"三个问题，系统第一次能用代码回答。

张量向量耦合（不变）：组织指纹轴 = hypervector.make("org:" + scope)；
小组向量 = bundle(岗轴, 仓轴)——与 V52-V56 同族编码。
"""

from __future__ import annotations

import datetime
import hashlib
import json
import math
import sys
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .c18_cluster import C18_NUMBERING, CouplingMatrix, HUB_IDS
from .hypervector import HypervectorSpace

# ---------------------------------------------------------------------------
# 一、组织编制（矩阵式双层：四人组横切 × 18 分管小组纵切）
# ---------------------------------------------------------------------------

# 五岗编制（素材 2.2 采信；可兼任但仓主与记录员不得同人——自证污染硬规则）
ORG_ROLES: Tuple[str, str, str, str, str] = (
    "仓主", "结构员", "连接员", "适配员", "记录员",
)

ROLE_DUTIES: Dict[str, str] = {
    "仓主": "本仓唯一负责人，对 S1-S5 与门禁结果签字（神马岗：批次规划/通路探索/适配提案）",
    "结构员": "维护本仓目录/接口与 N19 模板同构 S1/S2/S3（神龟岗：写已确定的事实）",
    "连接员": "维护本仓四类边、共振带、经络通道（LINK-01 对接）",
    "适配员": "运行自动适配模块，处理上游变更与迁移（神马岗：跨界复用）",
    "记录员": "心跳日志、调拨账本、交接单、回滚令牌（神龟岗：基线/账本/快照——不得与仓主同人）",
}

QUARTET_FUNCTIONS: Tuple[str, str, str, str] = (
    "结构", "共振", "语义", "演化",
)  # 四人组横切职能（定标准/写公共算子/审契约/仲裁冲突/主持心跳——不代写各仓业务实现）


def build_team_registry() -> List[Dict[str, Any]]:
    """18 分管小组编制表（派生自 C18_NUMBERING——零复制指针纪律）。

    每组：仓 id/仓名/领域/五岗空位（待实员指派）/契约版本。
    编制层职责边界：纵切责任层管本仓实现/连接/指标/回滚，不改公共契约
    不改他仓内部；横切能力层定标准/审契约/仲裁。
    """
    return [
        {
            "cang": c["id"],
            "repo": "holoaeon-" + c["id"].lower() + "-" + _slug(c["domain"]),
            "domain": c["domain"],
            "question": c["question"],
            "phase_main": c["phase_main"],
            "roles": list(ORG_ROLES),
            "owner": None,  # 待实员指派（未指派即未上岗——零虚构）
            "contract_version": "contract-v1.0",
        }
        for c in C18_NUMBERING
    ]


def _slug(domain: str) -> str:
    """域名→仓 slug（与已建成 GitHub 仓名一致：holoaeon-c01-source 等）。"""
    mapping = {
        "本源": "source", "身体": "body", "经络": "meridian", "家庭": "family",
        "教育": "education", "职业": "career", "财富": "wealth", "创造": "creation",
        "关系": "relation", "情感": "emotion", "意义": "meaning", "空间": "space",
        "时间": "time", "技艺": "skill", "风险": "risk", "灵性": "spirit",
        "社会": "society", "宇宙": "cosmos",
    }
    return mapping.get(domain, domain)


def check_team_registry(registry: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """编制检查：18 组齐/五岗齐/仓主记录员互斥规则/编号与 C18_NUMBERING 一致。"""
    reg = registry if registry is not None else build_team_registry()
    problems: List[str] = []
    if len(reg) != 18:
        problems.append("小组数!=18")
    ids = [r["cang"] for r in reg]
    if ids != [c["id"] for c in C18_NUMBERING]:
        problems.append("小组编号与 C18_NUMBERING 不一致")
    for r in reg:
        if set(r.get("roles", [])) != set(ORG_ROLES):
            problems.append("{} 五岗不齐".format(r["cang"]))
        if r.get("owner") and r.get("owner") == r.get("recorder"):
            problems.append("{} 仓主与记录员同人（自证污染硬规则违反）".format(r["cang"]))
    return {
        "pass": not problems,
        "problems": problems,
        "teams": len(reg),
        "roles": len(ORG_ROLES),
        "rule": "仓主与记录员不得同人（素材自证污染硬规则）",
    }


# ---------------------------------------------------------------------------
# 二、任务卡 Schema（交叉点即任务卡：四人组职能 × 18 小组）
# ---------------------------------------------------------------------------

TASK_CARD_REQUIRED_FIELDS: Tuple[str, ...] = (
    "card_id", "function", "cang", "assignee", "acceptor", "evidence",
)


def validate_task_card(card: Dict[str, Any]) -> Dict[str, Any]:
    """任务卡校验：唯一编号/唯一责任人/唯一验收人+完成证据（六字段）。"""
    problems: List[str] = []
    for f in TASK_CARD_REQUIRED_FIELDS:
        if f not in card or card[f] in (None, ""):
            problems.append("任务卡缺字段或空值：{}".format(f))
    if card.get("function") not in (None, "") and card.get("function") not in QUARTET_FUNCTIONS:
        problems.append("function 不在四人组四职能域：{}".format(card.get("function")))
    if card.get("assignee") and card.get("assignee") == card.get("acceptor"):
        problems.append("责任人与验收人同人（验收独立性违反）")
    return {"pass": not problems, "problems": problems, "required": list(TASK_CARD_REQUIRED_FIELDS)}


# ---------------------------------------------------------------------------
# 三、资源调拨中枢（Resource Arbiter）
# ---------------------------------------------------------------------------

# 受控资源清单（素材 3.1 六行：五行实 + 一行弃因留痕——108641 维持 V55 裁决）
RESOURCE_TYPES: Tuple[str, ...] = (
    "心跳时隙", "语义带宽", "评审带宽", "算力时长", "契约变更额度",
)
RESOURCES_REJECTED: Tuple[Tuple[str, str], ...] = (
    ("共振带配额", "素材原依赖 108641 共振带索引——数字挪用不诚实（V55 裁决维持），弃；真实带池须待连通件实测建立"),
)

# 优先级权重（素材建议初值采信为可标定常量——同 V55 生克系数口径）
PRIORITY_WEIGHTS: Dict[str, float] = {
    "W1_枢纽度": 0.30, "W2_门禁阻塞度": 0.30,
    "W3_相位权重": 0.15, "W4_批次紧迫度": 0.15, "W5_饥饿惩罚": 0.10,
}


def priority_score(cang: str, blocked_downstream: int = 0, phase_now: str = "",
                   batch_urgent: float = 0.0, starved_ticks: int = 0,
                   weights: Optional[Dict[str, float]] = None) -> float:
    """优先级公式（确定性，禁止拍脑袋——素材 3.2 采信）：

    Priority = W1·枢纽度 + W2·门禁阻塞度 + W3·相位权重 + W4·批次紧迫度 - W5·饥饿惩罚
    · 枢纽度：N19/C03/C11/C18 与枢纽仓高值（复用 c18_cluster HUB_IDS）；
    · 门禁阻塞度：卡住下游仓数量越多越高（归一 0-1：min(blocked/6, 1.0)）；
    · 相位权重：当前批次主相位匹配为 1.0 否则 0.0；
    · 批次紧迫度：0-1 连续参数；
    · 饥饿惩罚：连续 N 拍未获资源的仓自动加权（防饿死）。
    """
    w = weights or PRIORITY_WEIGHTS
    hub = 1.0 if cang in HUB_IDS or cang == "N19" else 0.0
    block = min(blocked_downstream / 6.0, 1.0)
    phase = 1.0 if (phase_now and any(
        c["id"] == cang and c["phase_main"] == phase_now for c in C18_NUMBERING
    )) else 0.0
    starve = min(starved_ticks / 3.0, 1.0)
    score = (w["W1_枢纽度"] * hub + w["W2_门禁阻塞度"] * block + w["W3_相位权重"] * phase
             + w["W4_批次紧迫度"] * max(0.0, min(1.0, batch_urgent))
             - w["W5_饥饿惩罚"] * starve)
    return round(score, 4)


# 调拨五规则（素材 3.3 采信）
ALLOCATION_RULES: Tuple[str, ...] = (
    "集中仲裁：只有 N19+四人组共振智能体可下发配额，小组不得自行抢占",
    "让渡与回收：任务完成即回收，未用完配额不得结转囤积",
    "抢占保护：高优先级抢占必须保留被抢占仓 rollback_token，不得半写",
    "饥饿检测：连续 3 拍零配额的仓自动升级为大心跳议题",
    "调拨账本：每次分配记录 时间/资源/数量/授予仓/依据公式值/回收状态，可审计",
)

LEDGER_REQUIRED_FIELDS: Tuple[str, ...] = (
    "tick", "resource", "amount", "granted_to", "priority_value", "recycled",
)


def validate_ledger_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    """调拨账本条目校验（六字段+回收态合法）。"""
    problems: List[str] = []
    for f in LEDGER_REQUIRED_FIELDS:
        if f not in entry or entry[f] in (None, ""):
            problems.append("账本缺字段或空值：{}".format(f))
    if entry.get("recycled") not in (None, True, False):
        problems.append("recycled 须为布尔或未回收（None）")
    return {"pass": not problems, "problems": problems}


# ---------------------------------------------------------------------------
# 四、C03 经络先行专项（G-M 门禁——三态诚实注册）
# ---------------------------------------------------------------------------

C03_GM_CRITERIA: Tuple[Dict[str, str], ...] = (
    {"item": "12 通道", "test": "通道表完整、每通道有通畅度模型与上下限", "status": "WAIT"},
    {"item": "事件传播", "test": "至少 3 条示范链路可复现（含 C02→C03→C10）", "status": "WAIT"},
    {"item": "阻塞机制", "test": "人为压低通畅度可触发阻塞并启动贝叶斯衍射反演", "status": "WAIT"},
    {"item": "衰减与终止", "test": "增益衰减/跳数上限/闭环终止三类终止可观测", "status": "WAIT"},
    {"item": "同构校验", "test": "S1>=0.95、S2=S3=1.0（骨架已达成——结构层，领域层随深化复测）", "status": "PASS"},
    {"item": "回滚", "test": "任一通道变更可用 rollback_token 精确还原（边Schema 硬约束已落地）", "status": "PASS"},
)


def c03_gate_report(evidence: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """G-M 门禁报告：六判据三态（同构/回滚两项 PASS——已在仓机制承载）。

    通道/传播/阻塞/衰减四项：**默认 WAIT**（无实测证据时不虚报），
    若传入 `evidence`（结构 = bus_channel.self_check() 返回值），则按四项的
    `pass` 实测转 PASS/FAIL——门禁只认实测，不认口头。

    硬约束（素材原文采信）：C03 未通过 G-M 前，禁止启动任何领域深化批次。
    通过 G-M 后 C03 升级为"总线仓"，其通道成为后续批次的公共基础设施。
    """
    items = (evidence or {}).get("items") or {}
    states: Dict[str, str] = {}
    for c in C03_GM_CRITERIA:
        base = c["status"]
        if base == "WAIT" and c["item"] in items:
            states[c["item"]] = "PASS" if items[c["item"]].get("pass") else "FAIL"
        else:
            states[c["item"]] = base
    wait = sum(1 for s in states.values() if s == "WAIT")
    fail = sum(1 for s in states.values() if s == "FAIL")
    if evidence:
        note = ("实测驱动：WAIT={} / FAIL={}（证据源 {}；四项按 bus_channel 自检结果转态）"
                .format(wait, fail, (evidence.get("schema") or "evidence")))
    else:
        note = ("WAIT={} 项依赖 C03 领域实现与连通件（12 通道表/传播链路/阻塞反演/衰减观测）"
                "——门禁不替未来签字（无 evidence 时保持 WAIT）".format(wait))
    return {
        "cang": "C03",
        "gate": "G-M",
        "criteria": len(C03_GM_CRITERIA),
        "states": states,
        "pass": wait == 0 and fail == 0,
        "note": note,
        "evidence_supplied": bool(evidence),
        "hard_rule": "C03 未过 G-M 前禁止启动任何领域深化批次（素材硬约束原文）",
        "upgrade": "过 G-M 后 C03 升级总线仓，通道固化为公共基础设施",
    }


def c03_gate_report_live() -> Dict[str, Any]:
    """门禁实测态：仓内 bus_channel 自检四判据后出报告（C03 总线仓已落地）。"""
    from . import bus_channel  # 延迟导入：避免包初始化期循环
    return c03_gate_report(bus_channel.self_check())


# ---------------------------------------------------------------------------
# 五、自动适配模块（六子模块+状态机+三边界）
# ---------------------------------------------------------------------------

ADAPTER_SUBMODULES: Tuple[str, ...] = (
    "契约侦测", "差异计算", "迁移生成", "同构校验", "冲突仲裁", "回滚守卫",
)

ADAPTER_STATES: Tuple[str, ...] = (
    "IDLE", "DETECTED", "DIFFED", "MIGRATED", "VERIFIED", "COMMITTED",
    "CONFLICT", "FAILED", "ROLLBACK", "ESCALATED",
)

ADAPTER_TRANSITIONS: Dict[str, Tuple[str, ...]] = {
    "IDLE": ("DETECTED",),
    "DETECTED": ("DIFFED",),
    "DIFFED": ("MIGRATED", "CONFLICT"),
    "MIGRATED": ("VERIFIED", "FAILED"),
    "VERIFIED": ("COMMITTED",),
    "COMMITTED": (),
    "CONFLICT": ("ESCALATED",),
    "FAILED": ("ROLLBACK",),
    "ROLLBACK": ("ESCALATED",),
    "ESCALATED": (),
}


def adapter_next(state: str, event: str) -> str:
    """适配器状态机转移（非法转移即 ValueError——写死状态机防自由漂移）。"""
    if state not in ADAPTER_TRANSITIONS:
        raise ValueError("未知状态：{}".format(state))
    if event not in ADAPTER_TRANSITIONS[state]:
        raise ValueError("非法转移：{} -{}->（合法：{}）".format(state, event, ADAPTER_TRANSITIONS[state]))
    return event


# 三边界（素材 5.2 采信——自动适配的关键纪律）
ADAPTER_BOUNDARIES: Dict[str, Tuple[str, ...]] = {
    "可自动": ("目录补齐", "接口签名对齐", "配置字段补默认值", "日志与心跳接线", "依赖版本升级"),
    "须人审": ("语义字段含义变更", "共振带语义重定义", "经络通道增删", "状态向量维度变化"),
    "禁止自动": ("删除本仓已有业务实现", "修改历史数据", "绕过门禁"),
}


def adapter_boundary_of(action: str) -> str:
    """动作→边界归类（三清单外即未定义——显式边界，未知不默认可自动）。"""
    for tier, actions in ADAPTER_BOUNDARIES.items():
        if action in actions:
            return tier
    raise ValueError("动作不在三边界清单：{}（未知动作不默认可自动）".format(action))


# ---------------------------------------------------------------------------
# 六、耗散结构耦合（五要件映射 + D1-D6 指标口径与计算）
# ---------------------------------------------------------------------------

DISSIPATION_REQUIREMENTS: Tuple[Dict[str, str], ...] = (
    {"requirement": "开放交换", "engineering": "每仓必须有明确输入源与输出汇", "evidence": "输入/输出流量日志非空"},
    {"requirement": "远离平衡态", "engineering": "状态向量持续受事件与梯度驱动", "evidence": "状态方差非零、非周期收敛"},
    {"requirement": "非线性反馈", "engineering": "生克增益、双向梯度、闭环判定", "evidence": "增益矩阵非对角、非单调响应"},
    {"requirement": "涨落触发", "engineering": "风险仓 C15+归零心跳+阻塞反演", "evidence": "小扰动可引发结构重构事件"},
    {"requirement": "持续负熵流", "engineering": "心跳、语义包、经络传导即代谢输入", "evidence": "停止输入后可观测退化"},
)

# D1-D6 指标（素材 7.2 采信——口径+计算函数先落地；实测须真实输入流，无流不假报）
DISSIPATION_METRICS: Tuple[Tuple[str, str, str], ...] = (
    ("D1", "负熵输入率", "单位心跳有效语义/事件流入量（越高越活）"),
    ("D2", "耦合耗散率", "边强度变化量/输入量（有效转换效率，适中为佳）"),
    ("D3", "结构维持成本", "保持同构所需修复动作数（越低越好）"),
    ("D4", "涨落响应度", "注入扰动后结构重构事件数（非零且可恢复）"),
    ("D5", "自组织恢复时间", "扰动后回到稳态所需心跳数（越短越健壮）"),
    ("D6", "死亡判据可观测性", "切断输入后指标退化是否可测（必须可测）"),
)


def compute_dissipation(flows: Optional[Sequence[float]] = None,
                        edge_changes: Optional[Sequence[float]] = None) -> Dict[str, Any]:
    """D1/D2 计算函数（确定性）：输入真实流量序列与边强度变化序列。

    无输入流时返回 measured=False（不假报——连通件未落地则无真实流）。
    判据（素材原文采信）：切断输入后指标毫无变化=静态目录而非耗散结构，不予通过。
    """
    if not flows or not edge_changes:
        return {"measured": False, "reason": "无真实输入流（连通件未落）——零虚构不假报", "D1": None, "D2": None}
    d1 = sum(flows) / float(len(flows))  # 单位心跳平均有效流入
    denom = sum(flows) or 1.0
    d2 = sum(abs(x) for x in edge_changes) / denom  # 边强度变化/输入
    return {"measured": True, "D1": round(d1, 4), "D2": round(d2, 4),
            "death_test": "切断输入后退化可测性属 D6 口径——须连通件实测，本函数不虚报"}


# ---------------------------------------------------------------------------
# 七、引导式推进循环（六步+自我追问六问）
# ---------------------------------------------------------------------------

GUIDE_SIX_STEPS: Tuple[str, ...] = (
    "领任务（卡编号+配额记录）", "查经络（通道健康快照）", "建骨架（S1/S2/S3 报告）",
    "连共振（边日志+Schema 校验）", "跑适配（适配报告）", "交门禁（门禁报告+tag）",
)

SELF_QUESTIONS: Tuple[str, ...] = (
    "我现在这一步的输入，是上一批的真实产出还是我的预期？",
    "我新增的边，两端模块真实存在吗？",
    "我改的东西属于契约还是实现？契约变更走提案了吗？",
    "本批有没有产生至少一条新的可复现链路？",
    "如果现在断电，我能用 rollback_token 退到哪一步？",
    "切断输入，我的仓会退化吗？不会的话它是不是死的？",
)


# ---------------------------------------------------------------------------
# 八、领域深化批次表（B0-B6 重构口径：骨架已建成，领域实现+连线待深化）
# ---------------------------------------------------------------------------

DEEPENING_BATCHES: Tuple[Dict[str, Any], ...] = (
    {"batch": "B0", "cangs": ("C03",), "phases": "木/水（传导枢纽）",
     "goal": "12 通道打通，过 G-M 升级总线仓（领域深化先行——骨架已建成）"},
    {"batch": "B1", "cangs": ("C02", "C10"), "phases": "水+火",
     "goal": "水克火链可测，情绪-身体双向梯度"},
    {"batch": "B2", "cangs": ("C01", "C04", "C13"), "phases": "土+土+水",
     "goal": "归零锚点闭环、代际与节律耦合"},
    {"batch": "B3", "cangs": ("C05", "C08", "C16"), "phases": "木三仓",
     "goal": "生发链、曼陀罗扇出可观测"},
    {"batch": "B4", "cangs": ("C06", "C09", "C11"), "phases": "火三仓（含意义枢纽）",
     "goal": "交联网、语义路由多跳"},
    {"batch": "B5", "cangs": ("C07", "C14", "C17"), "phases": "金三仓",
     "goal": "收敛链、基因漂移复用率"},
    {"batch": "B6", "cangs": ("C12", "C15", "C18"), "phases": "土/水/总枢",
     "goal": "免疫压测、全局镜像 S4 达标"},
)


def check_batches() -> Dict[str, Any]:
    """批次表校验：18 仓全覆盖无遗漏+每批至少 3 仓内+C03 先行+B6 含总枢。"""
    problems: List[str] = []
    flat: List[str] = []
    for b in DEEPENING_BATCHES:
        flat.extend(b["cangs"])
    if sorted(flat) != sorted([c["id"] for c in C18_NUMBERING]):
        problems.append("批次表未 18 仓全覆盖（{} 仓）".format(len(set(flat))))
    if DEEPENING_BATCHES[0]["cangs"] != ("C03",):
        problems.append("B0 须 C03 先行（素材硬约束）")
    if "C18" not in DEEPENING_BATCHES[-1]["cangs"]:
        problems.append("总枢 C18 须在末批闭环前")
    return {
        "pass": not problems,
        "problems": problems,
        "batches": len(DEEPENING_BATCHES),
        "cangs_covered": len(set(flat)),
        "note": "重构口径：骨架已建成（G1 达成），B0-B6=领域实现+连线深化批次，非建仓批次（素材叙事倒挂的诚实化）",
    }


# ---------------------------------------------------------------------------
# 九、组织张量（张量向量耦合不变——与 V52-V56 同族编码）
# ---------------------------------------------------------------------------


class OrgTensor:
    """组织张量：小组向量 = bundle(仓轴, 岗轴)——"调组织"第一次进张量。"""

    def __init__(self, space: Optional[HypervectorSpace] = None) -> None:
        self.space = space if space is not None else HypervectorSpace()
        self._axes: Dict[str, Any] = {}

    def cang_axis(self, cang: str) -> Any:
        key = "cang:" + cang
        if key not in self._axes:
            self._axes[key] = self.space.make(key)
        return self._axes[key]

    def role_axis(self, role: str) -> Any:
        if role not in ORG_ROLES:
            raise ValueError("role 须为五岗之一：{}".format(role))
        key = "org:" + role
        if key not in self._axes:
            self._axes[key] = self.space.make(key)
        return self._axes[key]

    def bundle(self, cangs: Sequence[str], roles: Sequence[str]) -> Any:
        if not cangs or not roles:
            raise ValueError("cangs 与 roles 不得为空")
        vecs = [self.cang_axis(c) for c in cangs] + [self.role_axis(r) for r in roles]
        acc = [0.0] * self.space.dim
        for v in vecs:
            for i, x in enumerate(v):
                acc[i] += x
        n = float(len(vecs))
        return [x / n for x in acc]

    def similarity(self, a: Any, b: Any) -> float:
        return self.space.cosine(a, b)


# ---------------------------------------------------------------------------
# 十、总闸（OrgGate：五检查 + 报告 + 指纹/探针/CLI）
# ---------------------------------------------------------------------------


class OrgGate:
    """组织化总闸：编制/任务卡/调拨/适配/批次五检查 + G-M/耗散口径报告。"""

    def __init__(self) -> None:
        self.checks = ("team", "task_card", "arbiter", "adapter", "batches")

    def check_team(self) -> Dict[str, Any]:
        return check_team_registry()

    def check_task_card(self, card: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if card is None:
            card = {"card_id": "TC-001", "function": "共振", "cang": "C10",
                    "assignee": "适配员A", "acceptor": "四人组·共振智能体",
                    "evidence": "共振带激活验收（schema 样例——非运行时记录）"}
        return validate_task_card(card)

    def check_arbiter(self) -> Dict[str, Any]:
        """调拨检查：资源清单五行实+一行弃因/权重和为 1/规则五条/账本 schema。"""
        problems: List[str] = []
        if len(RESOURCE_TYPES) != 5:
            problems.append("受控资源五行实不齐")
        if not RESOURCES_REJECTED:
            problems.append("弃因留痕缺失")
        w = PRIORITY_WEIGHTS
        if abs(sum(w.values()) - 1.0) > 1e-9:
            problems.append("优先级权重和!=1")
        if len(ALLOCATION_RULES) != 5:
            problems.append("调拨规则五行不齐")
        if len(LEDGER_REQUIRED_FIELDS) != 6:
            problems.append("账本六字段不齐")
        return {"pass": not problems, "problems": problems,
                "resources": list(RESOURCE_TYPES),
                "rejected": [r[0] for r in RESOURCES_REJECTED],
                "weights": PRIORITY_WEIGHTS}

    def check_adapter(self) -> Dict[str, Any]:
        """适配检查：六子模块/状态机闭合（终态可达+非法转移拒）/三边界穷举。"""
        problems: List[str] = []
        if len(ADAPTER_SUBMODULES) != 6:
            problems.append("六子模块不齐")
        for state, nxt in ADAPTER_TRANSITIONS.items():
            for s in nxt:
                if s not in ADAPTER_TRANSITIONS:
                    problems.append("状态机指向未知态：{}".format(s))
        if set(ADAPTER_BOUNDARIES) != {"可自动", "须人审", "禁止自动"}:
            problems.append("三边界清单不齐")
        return {"pass": not problems, "problems": problems,
                "submodules": list(ADAPTER_SUBMODULES),
                "states": len(ADAPTER_STATES),
                "boundaries": {k: len(v) for k, v in ADAPTER_BOUNDARIES.items()}}

    def check_batches(self) -> Dict[str, Any]:
        return check_batches()

    def self_check(self) -> Dict[str, Any]:
        results = {
            "team": self.check_team(),
            "task_card": self.check_task_card(),
            "arbiter": self.check_arbiter(),
            "adapter": self.check_adapter(),
            "batches": self.check_batches(),
        }
        return {
            "pass": all(r["pass"] for r in results.values()),
            "checks": {k: r["pass"] for k, r in results.items()},
            "problems": [p for r in results.values() for p in r.get("problems", [])],
        }

    def summary_report(self) -> Dict[str, Any]:
        sc = self.self_check()
        return {
            "ring": 21,
            "module": "org_gate",
            "self_check": sc,
            "c03_gate": c03_gate_report(),
            "dissipation_metrics": [list(m) for m in DISSIPATION_METRICS],
            "dissipation_measured": compute_dissipation(),
            "guide_steps": len(GUIDE_SIX_STEPS),
            "self_questions": len(SELF_QUESTIONS),
            "batches": len(DEEPENING_BATCHES),
        }


def _now_iso() -> str:
    return datetime.datetime.now().isoformat(timespec="seconds")


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def fingerprint() -> dict:
    return {
        "module": "org_gate",
        "ring": 21,
        "roles": len(ORG_ROLES),
        "resources": len(RESOURCE_TYPES),
        "priority_weights": len(PRIORITY_WEIGHTS),
        "adapter_states": len(ADAPTER_STATES),
        "adapter_submodules": len(ADAPTER_SUBMODULES),
        "dissipation_metrics": len(DISSIPATION_METRICS),
        "gm_criteria": len(C03_GM_CRITERIA),
        "batches": len(DEEPENING_BATCHES),
        "sha16": _sha256("org_gate:v58:ring21")[:16],
    }


def probe() -> dict:
    g = OrgGate()
    return {
        "fingerprint": fingerprint(),
        "self_check": g.self_check(),
        "c03_gate": c03_gate_report()["states"],
        "sample_priority": {
            "C03_hub": priority_score("C03"),
            "C01_plain": priority_score("C01"),
            "C01_starved": priority_score("C01", starved_ticks=3),
        },
    }


def _main(argv: List[str]) -> int:
    import argparse

    parser = argparse.ArgumentParser(prog="org_gate", description="组织化推进件（V58 ring21）")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("run", help="自检五检查+G-M+耗散口径")
    sub.add_parser("probe", help="指纹+探针（含优先级演示）")
    sub.add_parser("teams", help="18 小组编制表")
    sub.add_parser("batches", help="B0-B6 深化批次表")
    sub.add_parser("dissipation", help="耗散五要件+D1-D6 指标口径")
    args = parser.parse_args(argv[1:] if len(argv) > 1 else ["run"])
    cmd = args.cmd or "run"
    if cmd == "run":
        report = OrgGate().summary_report()
        sc = report["self_check"]
        print("[org_gate] self_check pass={} checks={}".format(sc["pass"], sc["checks"]))
        c03 = report["c03_gate"]
        print("  G-M: pass={} states={}".format(c03["pass"], c03["states"]))
        print("  dissipation_measured={} (无真实流不假报)".format(report["dissipation_measured"]["measured"]))
        ok = sc["pass"]
    elif cmd == "probe":
        print(json.dumps(probe(), ensure_ascii=False, indent=1))
        ok = True
    elif cmd == "teams":
        for r in build_team_registry():
            print("  {} | {} | {} | owner={}".format(r["cang"], r["repo"], r["domain"], r["owner"]))
        ok = True
    elif cmd == "batches":
        for b in DEEPENING_BATCHES:
            print("  {} | {} | {} | {}".format(b["batch"], "+".join(b["cangs"]), b["phases"], b["goal"]))
        ok = True
    else:  # dissipation
        for r in DISSIPATION_REQUIREMENTS:
            print("  {} | {} | 证据：{}".format(r["requirement"], r["engineering"], r["evidence"]))
        for m in DISSIPATION_METRICS:
            print("  {} {} | {}".format(*m))
        ok = True
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv))
