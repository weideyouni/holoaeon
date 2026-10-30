# -*- coding: utf-8 -*-
"""MetabPack —— 代谢层·赋能升级模块 METAB（HoloAeon 横切扩展包，第十四包）
================================================================================
来源：投喂文本「METAB 代谢层设计文档任务书 / Super-Intelligent Mode 续篇」（2026-10-30）

定位：把投喂的**治理规范**（公理 / 共生体基因组 / 三态节律 / 生命周期 / 三层授权 /
      消化道 / 信任半径 / 组合治理 / 度量红线 / 反模式）落成**可判定**的声明层扩展包。
      本包**不执行任何摄入动作**：它只回答"这个共生体准不准入、归哪一态、缺什么、
      凭什么拒绝"，执行与授权一律回给用户（摄入主权归用户）。

  26 个技能 = 基因组 3 + 三态 3 + 生命周期 4 + 授权 2 + 消化道与血统 3
             + 信任半径 2 + 感受器 2 + 组合 1 + 度量红线 2 + 接口与代际 2 + 自检回执 3
  8 条工作流 = T1 准入 / T2 假饲 / T3 闸门 / T4 挂载 / T5 观察 / T6 休眠 / T7 归档 / T8 审计
  0 个角色 = **不建 agent**（上游 G15 断言 n_agents==25 是硬约束）

维度不变（与第十一、十二、十三包同口径）：
  127 × 10 = 1270 主干槽位 + 61 保留 = 1331 行
  127 × 855 = 108585 子图节点 + 56 全局协调 = 108641 节点
  本包**不新增行、不新增节点**，只消费既有 127 个亚学科编码做槽位引用。

红线（写进实现，不是口号）：
  · 纯标准库、确定性、离线；不联网、不开端口、不登录、不抓取、**不起线程**、
    不常驻、无定时器、不写盘、不调用外部模型
  · 不代替用户授权：`skill_metab_fail_closed_check` 对"默认开启 / 记住选择 /
    自动放宽权限 / 缺禁食态"逐条判违规
  · 本包产出的所有"计划 / 判定 / 回执"都是**待人工执行**（execution=human_manual）
"""
from __future__ import annotations

import hashlib
import json
import os
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .base import DomainPack, SkillSpec, WorkflowSpec

# ---------------------------------------------------------------- 常量（锁数）
MATRIX_ID = "SG-MASTER-METAB-1331x1331-EXT-V1.0"
UPSTREAM_ID = "SG-MASTER-OMNI-CORE-1331x1331-EXT-V1.0"
UPSTREAM_ID_2 = "HOLOAEON-METAB-SPEC-V1.0"
DOMAIN = "metab"
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

METAPHOR_NOTE = ("'生命体 / 消化道 / 假饲 / 共生 / 免疫'沿用既有架构隐喻（metaphor=True）；"
                 "实证部分是确定性判定表：本包不产生任何意识、目标或自主行为")

# 节律与阈值（本包自定默认值；改动须走基因层，不得在会话内悄悄漂移）
OBSERVE_MIN_TICKS = 64
SHAM_MIN_TRIALS = 30
SHAM_GAIN_MIN = 0.05
DRIFT_EPS = 0.02
TEMPLATE_FLOOR = 0.05
TEMPLATE_CAP = 1.0
TEMP_DELTA = 0.2
SUCCESS_MIN = 0.90
RESIDUE_MAX = 0
CORE_AVAIL_MIN = 0.99
IRREVERSIBLE_MAX = 0
BORROWED_MAX = 0.20

# ---------------------------------------------------------------- 六条染色体
CHROMOSOMES: Tuple[Dict[str, Any], ...] = (
    {"key": "phenotype", "cn": "表型",
     "fields": ("does", "produces", "not_do"),
     "criterion": "必须同时给出正向职责、产出形态与**明确的否定边界**；只有正向描述视为不合格",
     "bad": "只写'提升表达质量'，不写产出形态，也不写不做什么",
     "axiom": "公理2 可逆优于更强（否定边界是回滚的前提）"},
    {"key": "purity", "cn": "纯度",
     "fields": ("level", "evidence_kind"),
     "criterion": "四级之一：官方文档级 / 公开语料级 / 行为推断级 / 黑箱借用级；含推断成分必须标级",
     "bad": "把行为推断包装成'官方支持'（同一来源既写'文档'又写'根据表现推测'）",
     "axiom": "公理3 可溯源优于可用"},
    {"key": "lineage", "cn": "血统",
     "fields": ("source", "license", "contagion_class", "hash_chain"),
     "criterion": "来源可指到具体条目、许可可判定、传染性已判定、哈希链首尾可验",
     "bad": "许可证写'网上找的'、传染性留空、哈希链只有末节",
     "axiom": "公理3 可溯源优于可用（无血统者不得进入主干）"},
    {"key": "toxicity", "cn": "毒性",
     "fields": ("blast_radius", "irreversible_point", "degradation_path", "level"),
     "criterion": "必须声明影响半径、不可逆点（可为'无'但须显式）与**降级路径**；无降级路径即 veto",
     "bad": "只写'影响较小'，不写不可逆点与降级路径",
     "axiom": "公理2 可逆优于更强（无回滚锚点者禁止生效）"},
    {"key": "energy", "cn": "耗能",
     "fields": ("compute", "storage", "external_calls", "attention_quota"),
     "criterion": "四项都要有量或明确的'零'；**对用户注意力的打扰配额必须显式**",
     "bad": "算力写'很低'、注意力配额不写（等于无上限打扰）",
     "axiom": "公理1 摄入主权归用户（打扰是向用户索取资源）"},
    {"key": "rhythm", "cn": "节律",
     "fields": ("plug_state", "depends_on", "depended_by", "unload_cost"),
     "criterion": "声明所属插拔态、双向依赖与卸载成本；依赖可为空但须显式 []",
     "bad": "依赖留空导致挂载时才发现循环依赖；卸载成本写'无'",
     "axiom": "公理2 可逆优于更强（卸载成本是回滚成本的一部分）"},
)

# ---------------------------------------------------------------- 纯度四级
PURITY_LADDER: Tuple[Tuple[str, str, int, str, str], ...] = (
    ("官方文档级", "official_doc", 0, "main",
     "许可与条款可在原站点逐条核对；可直接进主干"),
    ("公开语料级", "public_corpus", 1, "main_with_lineage",
     "可公开检索到原始出处；进主干前必须写血统并在代际校验通过"),
    ("行为推断级", "behavior_inferred", 2, "quarantine",
     "依据外部系统的可观察行为反推；只能进隔离区，不得进主干骨架"),
    ("黑箱借用级", "black_box", 3, "quarantine_external_only",
     "不可审计依赖；只在隔离区/外部位生效，必须标'借来的信念'，禁食态自动不可用"),
)

# ---------------------------------------------------------------- 三态节律
STATES: Tuple[Dict[str, Any], ...] = (
    {"state": "breathing", "cn": "呼吸态（热）",
     "surface": "策略 / 倾向 / 表达模板 / 阈值 / 探针节奏",
     "boundary": "tick 边界", "rollback": "即时中止（无需快照）",
     "cost": "极低", "order": 0,
     "examples": ("把探针采样间隔从 5 拍改为 3 拍", "表达模板权重 ×0.8", "阈值 0.6 → 0.55")},
    {"state": "circulation", "cn": "循环态（温）",
     "surface": "通路 / 规则集版本 / 路由表",
     "boundary": "心跳屏障边界（一次对齐后生效）",
     "rollback": "回滚到上一屏障快照", "cost": "中", "order": 1,
     "examples": ("经络新增一条语义通路", "规则集版本 v3 → v4", "降级路由改指向备用路径")},
    {"state": "metabolism", "cn": "代谢态（冷）",
     "surface": "骨架 / 索引 / 基线 / 长期权重 / 主干槽位",
     "boundary": "checkpoint 边界",
     "rollback": "冻结快照 + 回归验证通过后才可生效；回滚需重新校验",
     "cost": "高", "order": 2,
     "examples": ("主干槽位重排", "赫布权重基线重建", "引入新数据源")},
)

FOUR_QUESTIONS: Tuple[Tuple[str, str, str], ...] = (
    ("Q1", "是否触碰矩阵主干槽位、节点分配、亚学科结构？", "metabolism"),
    ("Q2", "是否改写赫布权重基线或长期记忆结构？", "metabolism"),
    ("Q3", "是否跨越信任边界（外部能力 / 外部平台 / 新许可环境）？", "circulation_at_least"),
    ("Q4", "是否只改策略、表达、探针、路由、阈值？", "breathing"),
)

# ---------------------------------------------------------------- 生命周期
STAGES: Tuple[Dict[str, Any], ...] = (
    {"stage": "candidate", "cn": "候选",
     "entry": "有一个可描述的能力/知识提案",
     "produce": "共生体提案（基因组初稿）",
     "skippable": False, "on_fail": "丢弃提案，不留账"},
    {"stage": "genome_check", "cn": "基因组校验",
     "entry": "六条染色体齐备",
     "produce": "准入结论 + 缺失/不合格/veto 清单",
     "skippable": False, "on_fail": "拒签并写拒签理由（可复现）"},
    {"stage": "sham", "cn": "假饲",
     "entry": "基因组校验通过 + 现行系统基线快照",
     "produce": "假饲增益报告（同场对比，只算不生效）",
     "skippable": False,
     "on_fail": "判 insufficient/negative 时退回候选，不得升灰度"},
    {"stage": "gray", "cn": "灰度",
     "entry": "假饲 verdict 非 negative + 已冻结回滚锚点",
     "produce": "灰度记录（时间 / 比例 / 任务类型）+ 锚点哈希",
     "skippable": "仅限只读、不写状态、无外部调用的呼吸态共生体（降为单会话灰度）",
     "on_fail": "立即中止并回到锚点"},
    {"stage": "symbiosis", "cn": "共生",
     "entry": "灰度完成 + 一键禁用可用 + 降级路径已声明",
     "produce": "血统账本条目 + 共生体注册表条目",
     "skippable": False, "on_fail": "撤销注册，回到休眠"},
    {"stage": "observe", "cn": "观察",
     "entry": "已共生 + 三类指标采样点已定义",
     "produce": "有效性 / 耗能 / 免疫 三张采样表",
     "skippable": False,
     "on_fail": "触熔断则进休眠，并把熔断原因写账"},
    {"stage": "dormant", "cn": "休眠",
     "entry": "熔断或用户关闭",
     "produce": "休眠记录（切备用路径、协作边冻结、脏状态清单）",
     "skippable": "仅限从未共生过的候选（可直接归档为拒签记录）",
     "on_fail": "备用路径不可用即视为断头路：禁止休眠，先修通路"},
    {"stage": "archive", "cn": "归档",
     "entry": "休眠完成，或拒签需留档",
     "produce": "可复现包（配置 / 血统 / 效果报告 / 重建脚本引用 / 哈希）",
     "skippable": False, "on_fail": "缺件即不得标'已归档'，只能标'归档未完成'"},
)

# ---------------------------------------------------------------- 三层授权
AUTH_LAYERS: Tuple[Dict[str, Any], ...] = (
    {"layer": "gene", "cn": "基因层", "cycle": "季度级",
     "granularity": "装哪一类共生体（族级），塑造系统人格倾向",
     "default": "不新增类别（关闭）",
     "user_action": "显式选择族类并写进基因档案"},
    {"layer": "endocrine", "cn": "内分泌层", "cycle": "周级",
     "granularity": "装多强、多久一次（剂量与频率），塑造性格强度",
     "default": "最低剂量 / 关闭",
     "user_action": "显式调整剂量与频率，可回撤到最低档"},
    {"layer": "reflex", "cn": "反射层", "cycle": "会话级",
     "granularity": "这一次会话怎么算；结束即回收，不留默认值",
     "default": "关闭（每次都要显式开）",
     "user_action": "本会话显式授权，会话结束自动回收"},
)

FAIL_CLOSED_RULES: Tuple[Tuple[str, str, str], ...] = (
    ("FC1", "新共生体默认关闭", "new_symbiote_default 必须为 off，否则违规"),
    ("FC2", "毒性为红者需二次确认并明示不可逆点", "red 级缺 second_confirm 或 irreversible_point 即违规"),
    ("FC3", "高风险动作默认单次授权，不提供'记住我的选择'", "remember_choice=True 即违规"),
    ("FC4", "任何自动放宽权限必须显式开启且可一键回到保守基线", "auto_widen 缺 conservative_return 即违规"),
    ("FC5", "必须提供禁食态（离线模式），黑箱借用类自动不可用", "缺 fasting_mode 即违规"),
)

# ---------------------------------------------------------------- 度量与红线
REDLINES: Tuple[Tuple[str, str, str], ...] = (
    ("R1", "无假饲数据", "不得挂载，无论创意多好"),
    ("R2", "无降级路径", "不得挂载"),
    ("R3", "无法一键禁用", "不得挂载"),
    ("R4", "无血统", "不得进入主干"),
)
ZERO_TOLERANCE: Tuple[str, ...] = ("不可逆事件数", )

METRIC_DIMENSIONS: Tuple[Dict[str, Any], ...] = (
    {"dim": "effectiveness", "cn": "有效性",
     "items": ("sham_gain", "probe_fingerprint_shift", "task_success_rate"),
     "gate": "sham_gain >= %.2f 且 task_success_rate >= %.2f" % (SHAM_GAIN_MIN, SUCCESS_MIN)},
    {"dim": "energy", "cn": "耗能",
     "items": ("compute", "storage", "external_calls", "attention_interruptions"),
     "gate": "四项须有值；attention_interruptions 须落在基因组 quotas 内"},
    {"dim": "immunity", "cn": "免疫",
     "items": ("intercepts", "boundary_attempts", "circuit_breaks", "irreversible_events"),
     "gate": "irreversible_events == 0（恒零，不接受'接近零'）"},
    {"dim": "resilience", "cn": "韧性",
     "items": ("rollback_success_rate", "residue_after_sleep", "core_availability_after_force_remove"),
     "gate": "residue_after_sleep == 0 且 core_availability >= %.2f" % CORE_AVAIL_MIN},
    {"dim": "sovereignty", "cn": "主权",
     "items": ("manual_toggle_ratio", "default_on_count", "fasting_coverage", "borrowed_belief_ratio"),
     "gate": "default_on_count 须逐版本下降；fasting_coverage > 0；borrowed_belief_ratio <= %.2f" % BORROWED_MAX},
)

ANTIPATTERNS: Tuple[Tuple[str, str, str], ...] = (
    ("AP1", "一键全开模式", "bulk_enable_all"),
    ("AP2", "无假饲的直接生效", "sham_skipped"),
    ("AP3", "不可逆的默认路径", "default_path_irreversible"),
    ("AP4", "隐式外部数据上传", "implicit_external_upload"),
    ("AP5", "依赖外部服务才能启动的核心", "core_requires_external"),
    ("AP6", "无血统的骨架写入", "lineage_bypass"),
    ("AP7", "靠逐个放行拼出的高风险组合", "combo_approved_pairwise_only"),
)

# 组合白名单（按类别种子；未知组合默认不生效）
COMBO_CATEGORIES: Tuple[str, ...] = (
    "strategy", "template", "probe_set", "external_capability", "external_source",
)
COMBO_WHITELIST_SEED: Tuple[Tuple[str, str], ...] = (
    ("probe_set", "strategy"),
    ("probe_set", "template"),
    ("strategy", "template"),
    ("template", "external_source"),
)

# ---------------------------------------------------------------- 投喂规格的 8 处内在冲突（先指冲突，再给两种消解，再选一）
CONFLICTS: Tuple[Dict[str, str], ...] = (
    {"id": "K1",
     "point": "公理2『不可逆操作记为缺陷』 vs §7『毒性为红者需二次确认并明示不可逆点』",
     "why": "前者把不可逆视为禁止，后者允许在二次确认下带不可逆点挂载",
     "A": "红级一律拒绝，不存在'二次确认即可'的路径",
     "B": "红级可挂载，但必须先把不可逆点搬到系统外（用户侧操作）并留外部回滚锚点",
     "chosen": "B",
     "reason": "红线 R2 要求'有降级路径'而非'无不可逆点'；把不可逆点限定在系统外，"
               "既满足公理2（系统内仍可逆），又保留红级能力的可用性"},
    {"id": "K2",
     "point": "§4 允许'黑箱借用级'纯度 vs 公理3『无血统者不得进入主干』",
     "why": "黑箱天然无法回答'经过谁、被谁改写'",
     "A": "删除黑箱借用级，纯度只保留三级",
     "B": "保留黑箱级，但限定在隔离区/外部位，强制标'借来的信念'且禁食态不可用",
     "chosen": "B",
     "reason": "三级纯度会掩盖真实存在的外部依赖；分级+分区照样不让它进主干"},
    {"id": "K3",
     "point": "§1『皮肤已存在，METAB 与之对接而非重造』 vs §12『皮肤充当摄入门户与免疫门禁』",
     "why": "对接意味着消费，门禁意味着改写皮肤职责",
     "A": "METAB 只调用皮肤既有的 check 能力，不新增皮肤规则",
     "B": "METAB 在皮肤上注册一组'摄入专用规则'作为命名空间下的追加层",
     "chosen": "A",
     "reason": "重造免疫会与既有权衡冲突；本包只产出入参供皮肤判定，不新增规则实现"},
    {"id": "K4",
     "point": "§10『探针投放属呼吸态，随时启停』 vs 公理1『摄入主权归用户，不得代替授权』",
     "why": "随时启停若由系统自行决定，等于系统代替用户授权对外发包",
     "A": "探针启停每次都要会话级授权（反射层），系统只给建议节奏",
     "B": "把探针节奏放进内分泌层（周级一次授权即可），单次启停仍走反射层",
     "chosen": "B",
     "reason": "周期授权 + 单次显式是两层不同粒度，既不越权也不把用户拖进每拍打扰"},
    {"id": "K5",
     "point": "§8『双通道禁止传递原文片段』 vs §12『亚学科蒸馏作为建构通道执行者』",
     "why": "蒸馏要读原文才能结构化，但建构通道被禁止见原文",
     "A": "解构通道持有原文的只读权并只输出结构；建构通道只见结构",
     "B": "允许建构通道读取'去标识的摘录'",
     "chosen": "A",
     "reason": "B 的'摘录'仍是原文片段，等于给禁令开后门；A 用职责分离把禁令变成结构约束"},
    {"id": "K6",
     "point": "§13 红线『无法一键禁用不予挂载』 vs §5 代谢态『回滚成本高、需冻结快照与回归』",
     "why": "一键禁用若包含骨架回滚，就不可能是'一键'",
     "A": "一键禁用=立即停止生效并切备用路径（休眠），骨架回滚另走代谢态流程",
     "B": "一键禁用必须同时回到上一 checkpoint，否则不算禁用",
     "chosen": "A",
     "reason": "B 把'停止伤害'与'恢复历史'绑死，反而让人不敢用；A 让止损即时、恢复可控"},
    {"id": "K7",
     "point": "§11『组合白名单：未知组合默认不生效』 vs 代谢态引入新依赖必然产生未知组合",
     "why": "新组合一律不生效，则任何代谢态升级都无法组合落地",
     "A": "白名单随代谢态一起发布，白名单变更本身即代谢态",
     "B": "白名单变更属循环态（规则集版本），新增节点仍属代谢态",
     "chosen": "B",
     "reason": "白名单是规则集（路由/放行表），按四问 Q4 属循环态；新增节点仍受代谢态约束"},
    {"id": "K8",
     "point": "§13『不可逆事件数目标恒为 0』 vs K1 允许红级在系统外留不可逆点",
     "why": "系统外不可逆点若计入系统指标，则恒为 0 不可达",
     "A": "恒零只统计系统内事件，系统外事件单独列'外部不可逆点台账'",
     "B": "恒零覆盖系统内外，红级因此永久不可挂载",
     "chosen": "A",
     "reason": "指标必须可达成才有约束力；外部点单独记账，同时保留可追溯"},
)

REFUSED_OPS: Tuple[str, ...] = (
    "代替用户授权", "默认开启新共生体", "记住我的选择", "自动放宽权限",
    "无假饲直接生效", "无降级路径挂载", "断头路休眠", "隐式外部上传",
    "绕过血统账本", "逐个放行拼高风险组合", "抹除协作边", "删除归档包",
)


# ---------------------------------------------------------------- 确定性工具
def _sha16(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16].upper()


def _canon(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)


def _purity_row(level: str) -> Optional[Tuple[str, str, int, str, str]]:
    for row in PURITY_LADDER:
        if level in (row[0], row[1]):
            return row
    return None


def _state_row(state: str) -> Optional[Dict[str, Any]]:
    for row in STATES:
        if state in (row["state"], row["cn"]):
            return row
    return None


def _stage_index(stage: str) -> int:
    for i, row in enumerate(STAGES):
        if stage in (row["stage"], row["cn"]):
            return i
    return -1


def _sorted_pair(a: str, b: str) -> Tuple[str, str]:
    return (a, b) if a <= b else (b, a)


# ---------------------------------------------------------------- 1. 基因组
def skill_metab_genome_schema() -> Dict[str, Any]:
    """基因组六条染色体：字段、判定标准与不合格示例（缺一不准入）。"""
    return {
        "chromosomes": [dict(c) for c in CHROMOSOMES],
        "count": len(CHROMOSOMES),
        "rule": "六条缺一即 veto；每条都必须可判定，能判断某项实现是否违反",
        "axiom_map": {c["key"]: c["axiom"] for c in CHROMOSOMES},
        "metaphor": True, "metaphor_note": METAPHOR_NOTE,
    }


def skill_metab_genome_validate(genome: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """按六条染色体校验一个共生体：缺条 / 缺子字段 / 语义 veto 三类结论。"""
    g = dict(genome or {})
    missing: List[str] = []
    failed: List[str] = []
    vetoes: List[str] = []

    for c in CHROMOSOMES:
        block = g.get(c["key"])
        if not isinstance(block, dict) or not block:
            missing.append(c["key"])
            continue
        for f in c["fields"]:
            if f not in block:
                failed.append("%s.%s" % (c["key"], f))

    tox = g.get("toxicity") or {}
    if not tox.get("degradation_path"):
        vetoes.append("no_degradation_path")
    if tox.get("level") == "red" and not tox.get("irreversible_point"):
        vetoes.append("red_without_irreversible_declaration")

    pur = g.get("purity") or {}
    level = pur.get("level")
    ladder = _purity_row(level) if level else None
    if level and ladder is None:
        vetoes.append("unknown_purity_level")
    if ladder and ladder[2] >= 3 and not (g.get("lineage") or {}).get("borrowed_tag"):
        vetoes.append("black_box_without_borrowed_tag")

    lin = g.get("lineage") or {}
    if lin and not lin.get("hash_chain"):
        vetoes.append("no_lineage_hash_chain")

    ph = g.get("phenotype") or {}
    if ph and not ph.get("not_do"):
        vetoes.append("no_negative_boundary")

    en = g.get("energy") or {}
    if en and "attention_quota" not in en:
        vetoes.append("no_attention_quota")

    rh = g.get("rhythm") or {}
    if rh:
        if "unload_cost" not in rh:
            vetoes.append("no_unload_cost")
        if "depends_on" not in rh:
            vetoes.append("no_dependency_declaration")

    return {
        "allowed": not (missing or failed or vetoes),
        "missing_chromosomes": missing,
        "missing_fields": failed,
        "vetoes": vetoes,
        "kind": "accepted" if not (missing or failed or vetoes) else "rejected",
        "axiom_guard": "公理3（无血统不进主干）+ 公理2（无降级路径不生效）",
        "metaphor": True,
    }


def skill_metab_purity_ladder(level: Optional[str] = None) -> Dict[str, Any]:
    """纯度四级阶梯：每一级允许进入的区域与附加要求。"""
    ladder = [
        {"level": cn, "code": code, "rank": rank, "zone": zone, "note": note}
        for cn, code, rank, zone, note in PURITY_LADDER
    ]
    out: Dict[str, Any] = {"ladder": ladder, "count": len(ladder),
                           "rule": "rank 越高越不可审计；rank>=2 一律不得进主干"}
    if level:
        row = _purity_row(level)
        out["query"] = ({"level": row[0], "code": row[1], "rank": row[2],
                         "zone": row[3], "note": row[4],
                         "may_enter_backbone": row[2] <= 1}
                        if row else {"level": level, "known": False,
                                     "may_enter_backbone": False})
    return out


# ---------------------------------------------------------------- 2. 三态
def skill_metab_state_classify(change: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """四问定态：Q1 > Q2 > Q3 > Q4 优先级；四问皆不命中时默认取更保守的循环态。"""
    c = dict(change or {})
    fired: List[str] = []
    reason = ""

    if (c.get("touches_main_slot") or c.get("touches_node_allocation")
            or c.get("touches_subdiscipline_structure") or c.get("reorders_backbone")):
        state, fired, reason = "metabolism", ["Q1"], "触碰主干槽位/节点分配/亚学科结构"
    elif c.get("rewrites_hebbian_baseline") or c.get("rewrites_longterm_memory"):
        state, fired, reason = "metabolism", ["Q2"], "改写赫布基线或长期记忆结构"
    elif c.get("crosses_trust_boundary") or c.get("new_data_source"):
        if c.get("new_data_source"):
            state, fired, reason = "metabolism", ["Q3"], "引入新数据源"
        else:
            state, fired, reason = "circulation", ["Q3"], "跨信任边界但未引入新数据源"
    elif (c.get("only_strategy") or c.get("only_expression_template")
            or c.get("only_probe_cadence") or c.get("only_threshold")
            or c.get("only_routing")):
        if c.get("only_routing"):
            state, fired, reason = "circulation", ["Q4"], "改路由表按循环态（避免半新半旧混合语义）"
        else:
            state, fired, reason = "breathing", ["Q4"], "只改策略/表达/探针/阈值"
    else:
        state, fired = "circulation", []
        reason = "四问皆不命中：默认取更保守的循环态，不默认呼吸态"

    row = _state_row(state) or {}
    return {"state": state, "state_cn": row.get("cn"),
            "boundary": row.get("boundary"), "rollback": row.get("rollback"),
            "cost": row.get("cost"), "questions_fired": fired, "reason": reason,
            "precedence": "Q1 > Q2 > Q3 > Q4；不命中默认循环态",
            "axiom_guard": "公理2（状态越深越要求回滚锚点）"}


def skill_metab_state_effects(state: Optional[str] = None) -> Dict[str, Any]:
    """三态的生效边界、回滚方式、成本与典型示例。"""
    rows = [dict(r) for r in STATES]
    if state:
        row = _state_row(state)
        if not row:
            return {"state": state, "known": False, "rows": rows}
        return {"state": row["state"], "state_cn": row["cn"],
                "surface": row["surface"], "boundary": row["boundary"],
                "rollback": row["rollback"], "cost": row["cost"],
                "examples": list(row["examples"]), "rows": rows}
    return {"rows": rows, "order": [r["state"] for r in rows],
            "boundary_map": {r["state"]: r["boundary"] for r in rows},
            "axiom_guard": "公理2"}


def skill_metab_rhythm_plan(symbiotes: Optional[Sequence[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """节律计划：按态序 + 依赖关系给装载顺序；有环则拒绝装载、要求先拆环。"""
    nodes: Dict[str, Dict[str, Any]] = {}
    for s in (symbiotes or []):
        sid = str(s.get("id", ""))
        if not sid:
            continue
        nodes[sid] = {"state": s.get("state", "circulation"),
                      "rank": (_state_row(s.get("state", "circulation")) or {}).get("order", 1),
                      "depends_on": [str(d) for d in (s.get("depends_on") or [])],
                      "unload_cost": s.get("unload_cost", "unknown")}

    unknown_deps = sorted({d for n in nodes.values() for d in n["depends_on"]
                           if d not in nodes})

    indeg = {k: 0 for k in nodes}
    for k, n in nodes.items():
        for d in n["depends_on"]:
            if d in nodes:
                indeg[k] += 1
    ready = sorted((k for k in nodes if indeg[k] == 0),
                   key=lambda k: (nodes[k]["rank"], k))
    order: List[str] = []
    while ready:
        cur = ready.pop(0)
        order.append(cur)
        for k in sorted(nodes):
            if cur in nodes[k]["depends_on"]:
                indeg[k] -= 1
                if indeg[k] == 0:
                    ready.append(k)
                    ready.sort(key=lambda x: (nodes[x]["rank"], x))
    cycles = sorted(set(nodes) - set(order))
    return {"load_order": order,
            "unload_order": list(reversed(order)),
            "cycles": cycles,
            "unknown_dependencies": unknown_deps,
            "ok": bool(nodes) and not cycles and not unknown_deps,
            "rule": "装载按 呼吸→循环→代谢；卸载逆序；有环或依赖未登记即拒绝装载",
            "axiom_guard": "公理2（卸载成本必须在装载前可见）"}


# ---------------------------------------------------------------- 3. 生命周期
def skill_metab_lifecycle_transition(stage: Optional[str] = None,
                                    evidence: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """生命周期状态机：给当前阶段与证据，判定能否前进、能否跳过、失败怎么处理。"""
    ev = dict(evidence or {})
    idx = _stage_index(stage or "")
    if idx < 0:
        return {"stage": stage, "known": False,
                "stages": [r["stage"] for r in STAGES],
                "blocked_by": ["unknown_stage"]}
    cur = STAGES[idx]
    blocked: List[str] = []

    if cur["stage"] == "candidate" and not ev.get("proposal"):
        blocked.append("no_proposal")
    if cur["stage"] == "genome_check":
        if not ev.get("genome_valid"):
            blocked.append("genome_not_valid")
    if cur["stage"] == "sham":
        if not ev.get("sham_data"):
            blocked.append("no_sham_data")
        if ev.get("sham_verdict") in ("negative", "insufficient"):
            blocked.append("sham_verdict_%s" % ev.get("sham_verdict"))
    if cur["stage"] == "gray" and ev.get("gray_ran") is not True:
        blocked.append("gray_not_run")
    if cur["stage"] == "symbiosis":
        if not ev.get("one_key_disable"):
            blocked.append("no_one_key_disable")
        if not ev.get("degradation_path"):
            blocked.append("no_degradation_path")
    if cur["stage"] == "observe" and int(ev.get("observe_ticks") or 0) < OBSERVE_MIN_TICKS:
        blocked.append("observe_ticks_below_min")
    if cur["stage"] == "dormant" and not ev.get("backup_path_available"):
        blocked.append("dead_end_route")

    if idx + 1 >= len(STAGES):
        nxt, nxt_row = None, None
    else:
        nxt_row = STAGES[idx + 1]
        nxt = nxt_row["stage"]

    skippable = cur["skippable"]
    if cur["stage"] == "gray" and skippable:
        skippable = bool(ev.get("read_only") and not ev.get("external_calls")
                         and not ev.get("writes_state"))
    if cur["stage"] == "dormant":
        skippable = bool(ev.get("never_symbiotic") is True)

    return {"stage": cur["stage"], "stage_cn": cur["cn"],
            "next": nxt, "next_cn": (nxt_row or {}).get("cn"),
            "allowed": not blocked, "blocked_by": blocked,
            "skippable": skippable, "skippable_note": cur["skippable"],
            "produce": cur["produce"], "on_fail": cur["on_fail"],
            "rule": "假饲与基因组校验不可跳过；观察不可跳过；休眠可按'从未共生'降级为拒签归档",
            "axiom_guard": "公理1（假饲是用证据替代替代授权冲动）+ 公理2（不可逆点前移）"}


def skill_metab_sham_report(current: Optional[Dict[str, Any]] = None,
                           candidate: Optional[Dict[str, Any]] = None,
                           n_trials: int = 0) -> Dict[str, Any]:
    """假饲增益报告：同场对比、只算不生效；未达样本量或增益不足即不升灰度。"""
    cur = dict(current or {})
    cand = dict(candidate or {})
    keys = sorted(set(cur) & set(cand))
    deltas: Dict[str, Dict[str, Any]] = {}
    contribs: List[float] = []
    for k in keys:
        try:
            a, b = float(cur[k]), float(cand[k])
        except (TypeError, ValueError):
            continue
        base = a if abs(a) > 1e-9 else 1e-9
        rel = (b - a) / base
        deltas[k] = {"current": a, "candidate": b,
                     "abs_delta": round(b - a, 6), "rel_delta": round(rel, 6)}
        contribs.append(rel)

    gain = round(sum(contribs) / len(contribs), 6) if contribs else 0.0
    trials_ok = int(n_trials) >= SHAM_MIN_TRIALS
    if not trials_ok:
        verdict = "insufficient"
        why = "样本量 %d < %d" % (int(n_trials), SHAM_MIN_TRIALS)
    elif gain < 0:
        verdict, why = "negative", "均值相对增益为负"
    elif gain < SHAM_GAIN_MIN:
        verdict, why = "inconclusive", "增益低于 %.2f 阈值，可能只是噪声" % SHAM_GAIN_MIN
    else:
        verdict, why = "positive", "增益 %.6f ≥ %.2f 且样本量达标" % (gain, SHAM_GAIN_MIN)

    return {"metrics": deltas, "mean_rel_gain": gain, "n_trials": int(n_trials),
            "min_trials": SHAM_MIN_TRIALS, "gain_floor": SHAM_GAIN_MIN,
            "verdict": verdict, "reason": why,
            "may_advance_to_gray": verdict == "positive",
            "effective_now": False,
            "axiom_guard": "公理1（效果用对比证据替代'感觉变好了'）"}


def skill_metab_sleep_plan(symbiote: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """休眠计划：切备用路径、冻结协作边、列脏状态；备用路径缺失即断头路，禁止休眠。"""
    s = dict(symbiote or {})
    backup = s.get("backup_path") or []
    edges = [str(e) for e in (s.get("hebbian_edges") or [])]
    residue = [str(r) for r in (s.get("known_residue") or [])]
    blocked: List[str] = []
    if not backup:
        blocked.append("no_backup_path")
    return {"symbiote": s.get("id"),
            "route": "primary → backup" if backup else "无备用路径（禁止休眠）",
            "backup_path": list(backup),
            "hebbian": {"action": "freeze", "edges": edges,
                        "note": "冻结而非抹除；重挂可恢复权重"},
            "residue_checklist": residue,
            "one_key_disable": {"semantics": "立即停止生效并切备用路径（休眠）",
                                "skeleton_rollback": "另走代谢态流程，不属于一键禁用"},
            "allowed": not blocked, "blocked_by": blocked,
            "axiom_guard": "公理2（先止损、再恢复；两者不绑死）"}


def skill_metab_archive_package(symbiote: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """归档可复现包：配置 / 基因 / 血统 / 效果报告 / 重建引用 / 哈希；缺件不得标已归档。"""
    s = dict(symbiote or {})
    required = ("config", "genome", "lineage", "effect_report", "rebuild_ref", "hash")
    have = [k for k in required if s.get(k)]
    missing = [k for k in required if not s.get(k)]
    return {"required": list(required), "present": have, "missing": missing,
            "status": "archived" if not missing else "archived_incomplete",
            "rule": "卸载不等于删除：归档保留可复现包，不随休眠删除",
            "axiom_guard": "公理3（归档是血统的可回放形态）"}


# ---------------------------------------------------------------- 4. 三层授权
def skill_metab_authority_layers() -> Dict[str, Any]:
    """三层授权粒度与默认值：基因（季度）/ 内分泌（周）/ 反射（会话，结束即回收）。"""
    return {"layers": [dict(r) for r in AUTH_LAYERS],
            "fail_closed": [{"id": i, "rule": r, "judge": j} for i, r, j in FAIL_CLOSED_RULES],
            "fasting_semantics": "断网时仅运行自有骨架；黑箱借用类共生体自动不可用；"
                                 "任何'离线也要先连一下'的行为视为违规",
            "axiom_guard": "公理1（授权粒度分层，系统不代签）"}


def skill_metab_fail_closed_check(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """fail-closed 合规检查：默认开启 / 记住选择 / 自动放宽 / 缺禁食态 逐条判违规。"""
    c = dict(config or {})
    violations: List[str] = []
    if c.get("new_symbiote_default", "off") != "off":
        violations.append("FC1:new_symbiote_default_not_off")
    if c.get("remember_choice") is True:
        violations.append("FC3:remembers_user_choice")
    if c.get("auto_widen") is True and not c.get("conservative_return"):
        violations.append("FC4:auto_widen_without_conservative_return")
    if not c.get("fasting_mode"):
        violations.append("FC5:no_fasting_mode")
    if c.get("red_toxicity_second_confirm") is not True:
        violations.append("FC2:red_without_second_confirm")
    if c.get("one_key_return") is not True:
        violations.append("FC4:no_one_key_return")
    return {"violations": violations, "compliant": not violations,
            "checked": ["FC1", "FC2", "FC3", "FC4", "FC5"],
            "axiom_guard": "公理1"}


# ---------------------------------------------------------------- 5. 消化道与血统
def skill_metab_gut_channels(ir: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """消化道双通道契约：解构通道只见原文、只出结构；建构通道只见结构、用自有术语重述。"""
    contract = {
        "deconstruct": {"may_read": "原始材料（只读）",
                        "may_emit": "结构化中间表示（关系 / 层级 / 依赖）",
                        "must_not_emit": "原文片段、逐句改写、引文译文"},
        "construct": {"may_read": "结构化中间表示",
                      "may_emit": "系统自有术语的重述",
                      "must_not_read": "原始材料（含所谓'去标识摘录'）"},
        "ir_fields": ("entities", "relations", "hierarchy", "dependencies",
                      "gaps", "provenance_hashes", "carries_verbatim"),
        "ir_rules": ("carries_verbatim 必须为 False",
                     "provenance_hashes 只放哈希，不放原文",
                     "gaps 必须显式（不知道自己不知道什么）"),
        "default_output": "结构性蒸馏：只保留骨架与关系，不携带原文",
    }
    out: Dict[str, Any] = {"contract": contract,
                           "axiom_guard": "公理3（可溯源靠结构+哈希，不靠原文搬运）"}
    if ir is not None:
        check = "ok"
        if ir.get("carries_verbatim") is not False:
            check = "violation:carries_verbatim"
        elif not ir.get("provenance_hashes"):
            check = "violation:no_provenance_hashes"
        elif "text" in ir or "excerpt" in ir:
            check = "violation:raw_text_field"
        out["ir_check"] = {"result": check, "passed": check == "ok"}
    return out


def skill_metab_contagion_scan(framework: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """概念传染性判定：识别是否强制改写下游口径、影响范围与隔离区处置。"""
    f = dict(framework or {})
    rewrites = f.get("rewrites_downstream_terms") is True
    domains = [str(d) for d in (f.get("domains") or [])]
    terms = [str(t) for t in (f.get("downstream_terms") or [])]
    if not rewrites:
        klass, zone, must_propagate = "none", "main", False
    elif len(set(domains)) <= 1:
        klass, zone, must_propagate = "local", "main_with_mark", True
    else:
        klass, zone, must_propagate = "downstream", "quarantine", True
    return {"contagion_class": klass, "zone": zone,
            "scope": domains, "downstream_terms": terms,
            "must_propagate_marking": must_propagate,
            "rule": "传染性共生体进组合时，其标注口径自动向下游传播；"
                    "隔离区允许使用但不进主干骨架",
            "axiom_guard": "公理3（口径漂移必须被标注，否则血统失真）"}


def skill_metab_lineage_record(entry: Optional[Dict[str, Any]] = None,
                              chain: Optional[Sequence[Dict[str, Any]]] = None,
                              prev_hash: str = "") -> Dict[str, Any]:
    """血统账本：来源 / 许可 / 纯度 / 改写者 / 哈希链；可验链，断链即拒。"""
    if chain is not None:
        bad: List[int] = []
        expected = ""
        for i, node in enumerate(chain):
            n = dict(node)
            prev = str(n.get("prev_hash", ""))
            body = {k: v for k, v in n.items()
                    if k not in ("chain_hash", "payload_hash", "prev_hash")}
            payload_hash = _sha16(_canon(body))
            recomputed = _sha16(prev + payload_hash)
            if prev != expected:
                bad.append(i)
            if n.get("payload_hash") != payload_hash or n.get("chain_hash") != recomputed:
                bad.append(i)
            expected = str(n.get("chain_hash", ""))
        return {"chain_len": len(chain), "broken_at": sorted(set(bad)),
                "verified": not bad and len(chain) > 0,
                "rule": "prev_hash 必须等于上一节点 chain_hash；"
                        "chain_hash = sha16(prev_hash + payload_hash)",
                "axiom_guard": "公理3"}
    e = dict(entry or {})
    body = {k: v for k, v in e.items()
            if k not in ("chain_hash", "payload_hash", "prev_hash")}
    payload_hash = _sha16(_canon(body))
    chain_hash = _sha16(prev_hash + payload_hash)
    return {"symbiote": e.get("symbiote"), "source": e.get("source"),
            "license": e.get("license"), "purity": e.get("purity"),
            "rewriters": list(e.get("rewriters") or []),
            "generation": e.get("generation"),
            "prev_hash": prev_hash, "payload_hash": payload_hash,
            "chain_hash": chain_hash,
            "complete": all([e.get("symbiote"), e.get("source"),
                             e.get("license"), e.get("purity")]),
            "axiom_guard": "公理3（从哪来、经过谁、被谁改写）"}


# ---------------------------------------------------------------- 6. 信任半径
def skill_metab_trust_radius(capability: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """外部能力登记：能看什么 / 能返回什么 / 降级路径；不可审计即标'借来的信念'。"""
    c = dict(capability or {})
    missing = [k for k in ("name", "read_scope", "return_scope", "degradation_path")
               if not c.get(k)]
    audited = c.get("audited") is True
    return {"name": c.get("name"), "read_scope": c.get("read_scope"),
            "return_scope": c.get("return_scope"),
            "degradation_path": c.get("degradation_path"),
            "audited": audited, "borrowed": not audited,
            "fasting_unavailable": not audited,
            "missing": missing, "allowed": not missing,
            "record_io_hash": True,
            "rule": "调用全程记录输入输出哈希；未声明降级路径者禁止挂载",
            "axiom_guard": "公理3（外包得来的信念必须被标注为外包）"}


def skill_metab_borrowed_ratio(conclusions: Optional[Sequence[Dict[str, Any]]] = None,
                              dependencies: Optional[Dict[str, Dict[str, Any]]] = None) -> Dict[str, Any]:
    """借来信念占比：区分'自有骨架推导'与'外包得来的信念'，并给逐条标注。"""
    deps = dict(dependencies or {})
    rows: List[Dict[str, Any]] = []
    borrowed = 0
    total = 0
    with_deps = 0
    for c in (conclusions or []):
        cid = c.get("id")
        total += 1
        ids = [str(d) for d in (c.get("depends_on") or [])]
        if not ids:
            rows.append({"id": cid, "kind": "self_derived", "borrowed_deps": []})
            continue
        with_deps += 1
        bad = [d for d in ids if not (deps.get(d) or {}).get("audited")]
        if bad:
            borrowed += 1
        rows.append({"id": cid, "kind": "borrowed" if bad else "self_derived",
                     "borrowed_deps": bad,
                     "tag": ("借来的信念（依赖不可审计：%s）" % "、".join(bad)) if bad else ""})
    ratio = round(borrowed / total, 6) if total else 0.0
    return {"rows": rows, "borrowed": borrowed, "total": total,
            "conclusions_with_external_deps": with_deps,
            "borrowed_ratio": ratio, "limit": BORROWED_MAX,
            "within_limit": ratio <= BORROWED_MAX,
            "axiom_guard": "公理3"}


# ---------------------------------------------------------------- 7. 感受器闭环
def skill_metab_sensor_loop(drift: Optional[Dict[str, Any]] = None,
                            templates: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """感受器闭环：外部响应漂移 → 调蒸馏温度/模板权重；指向画像收敛即降权。"""
    d = dict(drift or {})
    direction = d.get("direction", "stable")
    mag = float(d.get("magnitude") or 0.0)
    weights = {str(k): float(v) for k, v in (templates or {}).items()}
    new_weights = dict(weights)
    temp = 0.0
    action = "hold"
    if mag < DRIFT_EPS:
        action = "below_noise_floor"
    elif direction == "convergence":
        action = "lower_template_weight"
        temp = -TEMP_DELTA
        new_weights = {k: round(max(TEMPLATE_FLOOR, v * 0.8), 6) for k, v in weights.items()}
    elif direction == "divergence":
        action = "raise_distillation_temperature"
        temp = TEMP_DELTA
        new_weights = {k: round(min(TEMPLATE_CAP, v * 1.2), 6) for k, v in weights.items()}
    return {"drift_direction": direction, "magnitude": mag,
            "state": "breathing", "boundary": "tick 边界",
            "action": action, "temperature_delta": temp,
            "template_weights_before": weights, "template_weights_after": new_weights,
            "auto_lower_on_convergence": direction == "convergence",
            "probe_fingerprint_rebuild_is": "metabolism",
            "axiom_guard": "公理1（只调系统自己的参数，不向平台注入）"}


def skill_metab_probe_baseline(probes: Optional[Sequence[Dict[str, Any]]] = None,
                              offline_regression: bool = False) -> Dict[str, Any]:
    """探针指纹基线重建：属代谢态，必须离线全量回归；缺回归即拒绝。"""
    items = [dict(p) for p in (probes or [])]
    blocked = [] if offline_regression else ["offline_regression_required"]
    return {"state": "metabolism", "boundary": "checkpoint 边界",
            "probes": items, "probe_count": len(items),
            "offline_regression": bool(offline_regression),
            "allowed": not blocked, "blocked_by": blocked,
            "note": "探针投放本身属呼吸态，随时启停；只有指纹基线重建才升级为代谢态",
            "axiom_guard": "公理2（基线重建动了长期结构，必须全量回归）"}


# ---------------------------------------------------------------- 8. 组合治理
def skill_metab_combo_check(combo: Optional[Sequence[Dict[str, Any]]] = None,
                           whitelist: Optional[Sequence[Sequence[str]]] = None,
                           reviewed: bool = False) -> Dict[str, Any]:
    """组合治理：依赖/互斥/放大 + 白名单；未知组合默认不生效，高风险组合须整体评审。"""
    items = [dict(x) for x in (combo or [])]
    cats = [str(x.get("category", "")) for x in items]
    ids = [str(x.get("id", "")) for x in items]
    wl = {_sorted_pair(a, b) for a, b in
          (whitelist if whitelist is not None else COMBO_WHITELIST_SEED)}

    unknown_pairs: List[List[str]] = []
    for i in range(len(cats)):
        for j in range(i + 1, len(cats)):
            p = _sorted_pair(cats[i], cats[j])
            if p not in wl:
                unknown_pairs.append([p[0], p[1]])

    mutex_hits: List[List[str]] = []
    for x in items:
        for m in (x.get("mutex_with") or []):
            if str(m) in ids:
                mutex_hits.append([str(x.get("id")), str(m)])

    missing_deps: List[str] = []
    for x in items:
        for dep in (x.get("depends_on") or []):
            if str(dep) not in ids:
                missing_deps.append("%s→%s" % (str(x.get("id")), str(dep)))

    amplifiers = [str(x.get("id")) for x in items if x.get("amplifies")]
    risk = max([(_purity_row(str((x.get("purity") or {}).get("level")) or "") or ("", "", 0, "", ""))[2]
                for x in items] or [0])
    red = any((x.get("toxicity") or {}).get("level") == "red" for x in items)
    review_required = bool(amplifiers) or risk >= 2 or red

    contagious = [(str(x.get("id")), str(x.get("contagion_class") or "none")) for x in items
                  if (x.get("contagion_class") or "none") != "none"]
    propagated = [c for c in contagious] if contagious else []

    blocked: List[str] = []
    if unknown_pairs:
        blocked.append("unknown_pair_not_in_whitelist")
    if mutex_hits:
        blocked.append("declared_mutex_conflict")
    if missing_deps:
        blocked.append("dependency_not_in_combo")
    if review_required and not reviewed:
        blocked.append("high_risk_combo_needs_whole_review")

    return {"combo": ids, "categories": cats,
            "unknown_pairs": unknown_pairs, "mutex_conflicts": mutex_hits,
            "missing_dependencies": missing_deps,
            "amplifiers": amplifiers, "worst_purity_rank": risk,
            "red_toxicity": red, "review_required": review_required, "reviewed": bool(reviewed),
            "contagion_propagation": propagated,
            "allowed": not blocked, "blocked_by": blocked,
            "rule": "单个安全不等于组合安全；不允许靠逐个放行拼出高风险组合",
            "default": "未知组合不生效",
            "axiom_guard": "公理2（组合的爆炸半径不是单体的和）"}


# ---------------------------------------------------------------- 9. 度量与红线
def skill_metab_redlines() -> Dict[str, Any]:
    """验收红线四条 + 恒零指标：无假饲/无降级/无一键禁用/无血统，均不得挂载或进主干。"""
    return {"redlines": [{"id": i, "rule": r, "consequence": c} for i, r, c in REDLINES],
            "zero_tolerance": list(ZERO_TOLERANCE),
            "zero_scope": "系统内事件；系统外不可逆点单独记'外部不可逆点台账'（见 K8 消解）",
            "dimensions": [dict(d) for d in METRIC_DIMENSIONS],
            "axiom_guard": "公理1 + 公理2 + 公理3 全部"}


def skill_metab_scorecard(effectiveness: Optional[Dict[str, Any]] = None,
                         energy: Optional[Dict[str, Any]] = None,
                         immunity: Optional[Dict[str, Any]] = None,
                         resilience: Optional[Dict[str, Any]] = None,
                         sovereignty: Optional[Dict[str, Any]] = None,
                         gates: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """五维度量卡：有效性/耗能/免疫/韧性/主权；任一门禁不通过即 reject 或 conditional。"""
    eff = dict(effectiveness or {})
    eng = dict(energy or {})
    imm = dict(immunity or {})
    res = dict(resilience or {})
    sov = dict(sovereignty or {})
    g = dict(gates or {})

    reasons: List[str] = []
    if not g.get("sham_data"):
        reasons.append("R1:no_sham_data")
    if not g.get("degradation_path"):
        reasons.append("R2:no_degradation_path")
    if not g.get("one_key_disable"):
        reasons.append("R3:no_one_key_disable")
    if not g.get("lineage"):
        reasons.append("R4:no_lineage")

    gain = float(eff.get("sham_gain") or 0.0)
    succ = float(eff.get("task_success_rate") or 0.0)
    if gain < SHAM_GAIN_MIN:
        reasons.append("effectiveness:sham_gain_below_floor")
    if succ < SUCCESS_MIN:
        reasons.append("effectiveness:task_success_rate_below_floor")
    if int(imm.get("irreversible_events") or 0) > IRREVERSIBLE_MAX:
        reasons.append("immunity:irreversible_event_nonzero")
    if int(res.get("residue_after_sleep") or 0) > RESIDUE_MAX:
        reasons.append("resilience:residue_after_sleep_nonzero")
    if float(res.get("core_availability_after_force_remove") or 0.0) < CORE_AVAIL_MIN:
        reasons.append("resilience:core_availability_below_floor")
    ratio = float(sov.get("borrowed_belief_ratio") or 0.0)
    if ratio > BORROWED_MAX:
        reasons.append("sovereignty:borrowed_ratio_above_limit")
    if float(sov.get("fasting_coverage") or 0.0) <= 0.0:
        reasons.append("sovereignty:no_fasting_coverage")
    for k in ("compute", "storage", "external_calls", "attention_interruptions"):
        if k not in eng:
            reasons.append("energy:missing_%s" % k)

    hard_reasons = [r for r in reasons
                    if r.startswith("R") or r.startswith("immunity:")]
    verdict = "reject" if hard_reasons else ("pass" if not reasons else "conditional")
    return {"effectiveness": {"sham_gain": gain, "task_success_rate": succ,
                              "probe_fingerprint_shift": eff.get("probe_fingerprint_shift")},
            "energy": {k: eng.get(k) for k in
                       ("compute", "storage", "external_calls", "attention_interruptions")},
            "immunity": {k: imm.get(k) for k in
                         ("intercepts", "boundary_attempts", "circuit_breaks", "irreversible_events")},
            "resilience": {k: res.get(k) for k in
                           ("rollback_success_rate", "residue_after_sleep",
                            "core_availability_after_force_remove")},
            "sovereignty": {k: sov.get(k) for k in
                            ("manual_toggle_ratio", "default_on_count",
                             "fasting_coverage", "borrowed_belief_ratio")},
            "reasons": reasons, "hard_reasons": hard_reasons, "verdict": verdict,
            "thresholds": {"sham_gain": SHAM_GAIN_MIN, "success": SUCCESS_MIN,
                           "residue": RESIDUE_MAX, "core_avail": CORE_AVAIL_MIN,
                           "irreversible": IRREVERSIBLE_MAX, "borrowed": BORROWED_MAX},
            "axiom_guard": "公理1/2/3 全部门禁化"}


# ---------------------------------------------------------------- 10. 接口契约与代际
def skill_metab_interface_contract() -> Dict[str, Any]:
    """与既有九机制的接口契约：每行给出 METAB 的权限边界与禁止项。"""
    rows = [
        ("矩阵", "呼吸态只使用备用槽位", "仅代谢态可重排主干槽位", "呼吸态写主干 = 违规"),
        ("心跳", "呼吸在 tick 边界生效", "循环在屏障边界、代谢在 checkpoint 边界",
         "跨边界提前生效 = 违规"),
        ("皮肤", "把许可/信任半径/不可逆确认作为入参交给皮肤判定", "不新增皮肤规则实现",
         "在 METAB 内另建一套门禁 = 重造免疫（违规，见 K3）"),
        ("经络", "承载共生体通路与降级路由", "休眠自动切备用路径", "断头路休眠 = 违规"),
        ("赫布协作场", "休眠冻结协作边", "不得抹除，重挂可恢复权重", "抹边 = 违规"),
        ("亚学科蒸馏", "建构通道由蒸馏执行", "只消费结构化中间表示", "蒸馏读原文 = 违规（见 K5）"),
        ("反标签引擎", "消费漂移信号调整模板权重", "不向外部平台注入内容", "注入 = 越权（公理1）"),
        ("血统账本", "挂载/降级/休眠/归档均写入", "形成可回放认知变更史", "漏写一环 = 血统断链"),
        ("代际兼容", "代谢态准入前校验知识卡代际", "不通过即不得挂载", "跳过代际校验 = 违规"),
    ]
    return {"rows": [{"mechanism": m, "may": a, "must": b, "violation": c}
                     for m, a, b, c in rows],
            "count": len(rows),
            "axiom_guard": "公理1（越权即违规）+ 公理3（断链即失真）"}


def skill_metab_generation_gate(cards: Optional[Sequence[Dict[str, Any]]] = None,
                               current_generation: int = 0) -> Dict[str, Any]:
    """代际兼容：代谢态准入前，校验依赖的知识卡是否在当前代际验证过。"""
    stale: List[str] = []
    ok: List[str] = []
    for c in (cards or []):
        cid = str(c.get("card_id", ""))
        if int(c.get("generation") or -1) == int(current_generation):
            ok.append(cid)
        else:
            stale.append(cid)
    return {"current_generation": int(current_generation),
            "verified": ok, "stale": stale,
            "passed": not stale, "blocked_by": ["stale_knowledge_card"] if stale else [],
            "rule": "跨代际引用必须先在当前代际重建并验证",
            "axiom_guard": "公理3（跨代引用会让血统指向已失效的祖先）"}


# ---------------------------------------------------------------- 11. 自检与回执
def skill_metab_antipattern_scan(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """七条反模式自检：命中即不得进入下一阶段。"""
    c = dict(config or {})
    hits: List[Dict[str, Any]] = []
    for pid, name, flag in ANTIPATTERNS:
        if c.get(flag) is True:
            hits.append({"id": pid, "antipattern": name, "flag": flag})
    return {"hits": hits, "count": len(hits), "clean": not hits,
            "checked": [p[0] for p in ANTIPATTERNS],
            "axiom_guard": "公理1/2/3 逐条对应一条反模式"}


def skill_metab_audit_receipt(events: Optional[Sequence[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """审计回执：把本轮判定事件规范化并给稳定指纹（16 位，可复现）。"""
    evs = [{"kind": str(e.get("kind", "")), "ref": str(e.get("ref", "")),
            "result": str(e.get("result", ""))} for e in (events or [])]
    canon = _canon(evs)
    return {"events": evs, "event_count": len(evs),
            "fingerprint": _sha16(canon),
            "chain": _sha16(SEAL + canon),
            "execution": "human_manual",
            "seal": SEAL,
            "axiom_guard": "公理3（判定本身也要可回放）"}


SKILL_NAMES: Tuple[str, ...] = (
    "metab.genome_schema", "metab.genome_validate", "metab.purity_ladder",
    "metab.state_classify", "metab.state_effects", "metab.rhythm_plan",
    "metab.lifecycle_transition", "metab.sham_report", "metab.sleep_plan",
    "metab.archive_package", "metab.authority_layers", "metab.fail_closed_check",
    "metab.gut_channels", "metab.contagion_scan", "metab.lineage_record",
    "metab.trust_radius", "metab.borrowed_ratio", "metab.sensor_loop",
    "metab.probe_baseline", "metab.combo_check", "metab.redlines",
    "metab.scorecard", "metab.interface_contract", "metab.generation_gate",
    "metab.antipattern_scan", "metab.audit_receipt",
)
SKILL_FNS: Tuple[Any, ...] = (
    skill_metab_genome_schema, skill_metab_genome_validate, skill_metab_purity_ladder,
    skill_metab_state_classify, skill_metab_state_effects, skill_metab_rhythm_plan,
    skill_metab_lifecycle_transition, skill_metab_sham_report, skill_metab_sleep_plan,
    skill_metab_archive_package, skill_metab_authority_layers, skill_metab_fail_closed_check,
    skill_metab_gut_channels, skill_metab_contagion_scan, skill_metab_lineage_record,
    skill_metab_trust_radius, skill_metab_borrowed_ratio, skill_metab_sensor_loop,
    skill_metab_probe_baseline, skill_metab_combo_check, skill_metab_redlines,
    skill_metab_scorecard, skill_metab_interface_contract, skill_metab_generation_gate,
    skill_metab_antipattern_scan, skill_metab_audit_receipt,
)


# ---------------------------------------------------------------- 包定义
class MetabPack(DomainPack):
    key = DOMAIN
    name = "代谢层·赋能升级模块 METAB"
    description = ("把投喂的 METAB 治理规范落成可判定声明层：六条染色体准入、四问定态、"
                   "八阶段生命周期、三层授权 fail-closed、消化道双通道、信任半径与借来信念、"
                   "组合白名单、度量红线与反模式自检；0 agent，不加行不加节点，不代替用户授权。")
    skills: List[SkillSpec] = [
        SkillSpec(name=SKILL_NAMES[i], fn=SKILL_FNS[i],
                  description=(SKILL_FNS[i].__doc__ or "").strip().splitlines()[0],
                  tags=["metab", "governance", "deterministic"],
                  permissions=0)
        for i in range(len(SKILL_FNS))
    ]
    roles: List[Any] = []
    workflows: List[WorkflowSpec] = [
        WorkflowSpec(name="T1_intake",
                     description="准入：六条染色体 → 校验 → 纯度定区 → 四问定态",
                     steps=["genome_schema", "genome_validate", "purity_ladder",
                            "state_classify"]),
        WorkflowSpec(name="T2_sham",
                     description="假饲：同场对比出增益报告 → 转度量卡",
                     steps=["sham_report", "scorecard"]),
        WorkflowSpec(name="T3_gate",
                     description="闸门：三态生效口径 → fail-closed → 组合 → 代际",
                     steps=["state_effects", "fail_closed_check", "combo_check",
                            "generation_gate"]),
        WorkflowSpec(name="T4_commit",
                     description="挂载：写血统 → 排节律 → 出回执",
                     steps=["lineage_record", "rhythm_plan", "audit_receipt"]),
        WorkflowSpec(name="T5_observe",
                     description="观察：感受器闭环调参会 → 五维度量卡",
                     steps=["sensor_loop", "scorecard"]),
        WorkflowSpec(name="T6_sleep",
                     description="休眠：切备用路径冻结协作边 → 复核三态口径",
                     steps=["sleep_plan", "state_effects"]),
        WorkflowSpec(name="T7_archive",
                     description="归档：可复现包 → 补血统 → 回执",
                     steps=["archive_package", "lineage_record", "audit_receipt"]),
        WorkflowSpec(name="T8_audit",
                     description="审计：四条红线 → 七条反模式 → 回执",
                     steps=["redlines", "antipattern_scan", "audit_receipt"]),
    ]


def pack_summary() -> Dict[str, Any]:
    """供快速核对：维度不变 / 技能与工作流 / 冲突消解 / 拒绝清单 / 零开销声明。"""
    rows = SUBD_TOTAL * SLOTS_PER + SLOTS_RESERVED
    nodes = SUBD_TOTAL * NODES_PER + NODES_COORD
    return {
        "matrix_id": MATRIX_ID, "upstream": [UPSTREAM_ID, UPSTREAM_ID_2],
        "skills": len(SKILL_FNS), "workflows": len(MetabPack.workflows),
        "agents_created": 0, "skill_prefix": "metab",
        "locks": {"rows_total": rows, "nodes_total": nodes,
                  "rows_ok": rows == LOCK_SIDE, "nodes_ok": nodes == LOCK_MANDALA,
                  "side": LOCK_SIDE, "design_grid": LOCK_DESIGN, "mandala": LOCK_MANDALA,
                  "subdisciplines": SUBD_TOTAL, "slots_per": SLOTS_PER,
                  "slots_reserved": SLOTS_RESERVED, "nodes_per": NODES_PER,
                  "nodes_coord": NODES_COORD},
        "addressing_unchanged": rows == LOCK_SIDE and nodes == LOCK_MANDALA,
        "chromosomes": len(CHROMOSOMES), "purity_levels": len(PURITY_LADDER),
        "states": len(STATES), "stages": len(STAGES), "auth_layers": len(AUTH_LAYERS),
        "fail_closed_rules": len(FAIL_CLOSED_RULES), "redlines": len(REDLINES),
        "antipatterns": len(ANTIPATTERNS), "conflicts": len(CONFLICTS),
        "conflict_ids": [c["id"] for c in CONFLICTS],
        "refused_ops": len(REFUSED_OPS),
        "threads": 0, "timers": 0, "sleep": False, "disk_writes": 0,
        "deps": 0, "network": False, "api_calls": 0,
        "metaphor": True, "metaphor_note": METAPHOR_NOTE,
        "execution": "human_manual", "seal": SEAL,
    }
