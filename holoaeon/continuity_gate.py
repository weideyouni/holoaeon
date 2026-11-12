# -*- coding: utf-8 -*-
"""
ContinuityGate —— 贯续性门禁件（V56 · ring20 贯续域）
================================================================================
源声明（诚实边界）：
  · 素材源 = 碳基 2026-11-12 投喂 CONT-01《HoloAeon 全息基座建设·贯续性
    总控指南》（结构包 V3 → 连通包 LINK-01 → 贯续包 CONT-01 三件套终章）。
    本模块为四人组第一性原理扬弃后的**可测子集**，不是照搬——扬弃裁决
    全记录见投喂包第 2 节。
  · 核心命题（素材原文采信）：结构可以一次设计完，连通可以一次写出来，
    但**有机体只能一次一次长出来**——贯续性就是"长"的秩序。
  · 三条贯续（素材第一性拆解，采信）：
      时间贯续（时序不乱）——任何一步的输入必须是上一步的真实产出，
        而不是"预期产出"；先建共振边后建模块的倒挂即断裂。
      结构贯续（同构不漂）——同构性必须机器校验，不能靠人记得。
      证据贯续（可追可回）——触发者/时间/输入快照/输出差异/rollback_token
        必须留痕；没有证据链的系统出问题只能整体回滚。
  · 扬弃（弃）实录：①素材"建议工期"（3 天-2 周/期）弃——工程节拍以批次
    （V-series）为准，日历工期非可测物，八期卡不设工期字段（如实声明）；
    ②素材 git_batch_create.sh（bash）弃——V55 已有 create_repos_v55.py
    （Python，幂等+可回滚+dry-run），bash 重写是倒退；③素材"心跳三段式
    调度器最小版"弃——scheduler.py 是 README 声明 untouchable 四模块之一，
    新建调度器违冻结维度；心跳只做门禁侧节拍口径引用（bus/craft_gate
    先例）；④78 梅塔特隆边/108641/每仓 20 项瀑布——维持 V55 弃裁决
    （数字挪用不诚实）；⑤素材七天天清单 D5"真实创建 C03 仓"弃——外部
    不可逆动作须碳基确认（create_repos_v55.py --apply 在档待批）。
  · 扬弃（取）实录：三贯续判据/四问一句话判据/B1-B10 断裂点清单/G0-G7
    门禁三态化/交接单 Schema/八期次序/M0 契约冻结实体化（反向提取自仓，
    非新定契约——CONT-01 忠告一落地：先把已存在的事实写成契约）。

贯续性与工程纪律的同构照（升维句，见投喂包第 4 节）：
    断线恢复协议、冻结维度、回执三账这些每天在用的工程纪律，第一次
    成为 continuity_gate 里的检查函数——系统用门禁检验自己的生长。

张量向量耦合（不变）：贯续指纹轴 = hypervector.make("cont:" + state)；
批次链向量 = bundle(批次轴, 门禁状态轴)——与 V52-V55 同族编码。
"""

from __future__ import annotations

import datetime
import hashlib
import json
import math
import sys
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .c18_cluster import (
    C18_NUMBERING,
    EDGE_REQUIRED_FIELDS,
    CouplingMatrix,
    phase_relation,
    validate_edge,
)
from .hypervector import HypervectorSpace

# ---------------------------------------------------------------------------
# 一、贯续常量（三条贯续 + 四问判据 + 八期次序）
# ---------------------------------------------------------------------------

CONTINUITY_AXES: Tuple[str, str, str] = ("temporal", "structural", "evidential")

CONTINUITY_AXIS_DESC: Dict[str, str] = {
    "temporal": "时间贯续（时序不乱）：任何一步的输入必须是上一步的真实产出，而非预期产出",
    "structural": "结构贯续（同构不漂）：同构性必须机器校验（复用在仓机制实测），不靠人记得",
    "evidential": "证据贯续（可追可回）：每次连通/共演化/重构须留触发者/时间/输入快照/rollback_token",
}

# 素材"一句话判据"四问（采信原文语义，逐问绑定机器侧答案）
FOUR_QUESTIONS: Tuple[str, str, str, str] = (
    "现在处于哪一期",
    "上一期交付了什么",
    "这一期凭什么开始",
    "出问题退到哪一步",
)

# 八期次序（M0-M7 顺序不可打乱——每期内部任务可并行，次序本身是门禁）
PHASE_ORDER: Tuple[str, str, str, str, str, str, str, str] = (
    "M0", "M1", "M2", "M3", "M4", "M5", "M6", "M7",
)

# 八期任务卡（弃素材"建议工期"——工程节拍以批次为准，如实声明不设工期字段）
PHASES: List[Dict[str, str]] = [
    {
        "phase": "M0", "name": "契约冻结期",
        "goal": "把'不许改的东西'钉死（反向提取基座既有契约成文件，非新定契约）",
        "gate": "G0 契约清单成文件且 frozen",
        "rollback": "无（起点）",
        "anchor": "contract-v1.0：后续每期产出写明依赖的契约版本",
    },
    {
        "phase": "M1", "name": "骨架建库期",
        "goal": "C01-C18 真实存在且与 N19 结构同构（脚本化，禁手工）",
        "gate": "G1 仓注册表完备+同构校验达标（S1>=0.95/S2=S3=1.0 素材口径）",
        "rollback": "R1（模板 commit 打 tag 可整批重置）",
        "anchor": "每仓首次 commit 带 contract-v1.0 标记",
    },
    {
        "phase": "M2", "name": "最小连通期",
        "goal": "第一条真实可查带完整 Schema 的跨仓边（先证明能连，再谈连得好）",
        "gate": "G2 示范链路日志可复现+删边降级不崩溃",
        "rollback": "R2",
        "anchor": "示范链路固化为回归用例（素材口径 test_link_c02_c03_c10）",
    },
    {
        "phase": "M3", "name": "五层齐备期",
        "goal": "L3/L4/L5 落地，五层贯通",
        "gate": "G3 五层贯通冒烟测试通过",
        "rollback": "R3",
        "anchor": "五层贯通用例进 CI 必跑集",
    },
    {
        "phase": "M4", "name": "共演化期",
        "goal": "共演化算子生效，双向性硬规则可观测",
        "gate": "G4 单向连接测试在既定心跳内自动断边",
        "rollback": "R4",
        "anchor": "共演化事件全进 ledger 带 rollback_token",
    },
    {
        "phase": "M5", "name": "全息验证期",
        "goal": "把'我认为像'换成'指标说像'",
        "gate": "G5 S1-S5 全部由脚本产出且达标",
        "rollback": "R5",
        "anchor": "指标基线落盘 metrics_baseline，劣化即阻断合并",
    },
    {
        "phase": "M6", "name": "免疫压测期",
        "goal": "断仓/降级/回滚/混沌演练（有机体的标志是受伤不死）",
        "gate": "G6 七项演练全部通过并留日志",
        "rollback": "R6",
        "anchor": "演练脚本固化 chaos/ 目录，大版本发布前必跑",
    },
    {
        "phase": "M7", "name": "固化开源期",
        "goal": "让别人能接手才算完成（文档三件套+CI 固化+发布）",
        "gate": "G7 新人 30 分钟只看 README 跑起一仓+一次跨仓调用",
        "rollback": "无（终态）",
        "anchor": "v1.0.0 成为后续所有升级的比较基准",
    },
]

# 门禁状态三态（零虚构核心设计：未落地的门禁诚实返回 WAIT，不虚构 PASS）
GATE_STATES: Tuple[str, str, str] = ("PASS", "WAIT", "FAIL")

# ---------------------------------------------------------------------------
# 二、B1-B10 断裂点清单（素材第六节采信，逐条映射在仓先例——机器可验）
# ---------------------------------------------------------------------------

BREAKPOINTS: List[Dict[str, str]] = [
    {
        "id": "B1",
        "symptom": "手工建仓建目录，第 7 个仓开始结构漂移",
        "fix": "一切建库建目录必须脚本化，禁止手工",
        "precedent": "create_repos_v55.py + scaffold_c18.py（V55 在档，18/18 独立可运行已验收）",
    },
    {
        "id": "B2",
        "symptom": "先连后建——共振边指向不存在的模块",
        "fix": "门禁强制'模块存在性校验'（import 实测）",
        "precedent": "V55 REUSE_MAP 4 例 import 实测（素材要新建的机制全在仓内可导入）",
    },
    {
        "id": "B3",
        "symptom": "契约口头化，字段名各写各的",
        "fix": "M0 冻结 + CI 校验 Schema",
        "precedent": "本模块 export_m0_contract()（反向提取冻结契约成文件）",
    },
    {
        "id": "B4",
        "symptom": "接口悄悄漂移，三个月后 S2 崩",
        "fix": "同构校验进 CI 必跑，劣化即阻断",
        "precedent": "主套 unittest discover + redline_scan.py（V50 实测 129 文件 0 违规）",
    },
    {
        "id": "B5",
        "symptom": "无节拍广播，系统震荡/循环依赖",
        "fix": "三段式心跳写死，禁自由广播",
        "precedent": "bus.py / craft_gate.py 心跳先例（复用引用；scheduler.py 为 untouchable，不新建调度器）",
    },
    {
        "id": "B6",
        "symptom": "单向连接堆积，看着连着实死边",
        "fix": "双向硬规则+自动衰减断边",
        "precedent": "c18_cluster EDGE 硬约束 ttl>=12 + decay∈(0,1) + rollback 非空",
    },
    {
        "id": "B7",
        "symptom": "同质化塌缩，19 仓变成 19 份拷贝",
        "fix": "反同质化+内容分化反向指标",
        "precedent": "V55 S5 实测 18 仓问题向量两两 cosine 0.0603（<=0.70 达标）",
    },
    {
        "id": "B8",
        "symptom": "无回滚令牌，出问题只能整体重置",
        "fix": "每次连通操作强制签发 rollback_token",
        "precedent": "c18_cluster.validate_edge 硬约束 rollback_token 非空（V55 落地）",
    },
    {
        "id": "B9",
        "symptom": "指标自证——'我觉得达标'",
        "fix": "指标必须脚本产出 JSON，人只读不改",
        "precedent": "回执三账惯例（reports/v5x_receipt.json 逐批脚本产出）",
    },
    {
        "id": "B10",
        "symptom": "文档滞后，未来的自己看不懂",
        "fix": "文档与代码同 PR，缺文档不合并",
        "precedent": "readme_claims_check.py 仓外闸（V46 实测 PASS/mismatch=0）",
    },
]

BREAKPOINT_IDS: Tuple[str, ...] = tuple(b["id"] for b in BREAKPOINTS)

# ---------------------------------------------------------------------------
# 三、M0 契约冻结（反向提取——CONT-01 忠告一落地：先反向提取既有契约，
#     不是先定契约再改基座；只扩展不重构）
# ---------------------------------------------------------------------------

CONTRACT_VERSION = "contract-v1.0"

# 冻结维度（README 声明的 untouchable 口径——反向提取，非新定）
UNTOUCHABLE_MODULES: Tuple[str, str, str, str] = (
    "graph", "scheduler", "hypervector", "kernel.submit",
)

DIMENSION_FREEZE: Dict[str, Any] = {
    "VERSION": "0.9.1",
    "MATRIX_ID": "HOLOAEON-MATRIX-0.9.1",
    "BUILTIN_LAYERS": "L1-L8（8 层；guard_layers=8）",
    "PACK_ORDER": 9,
    "EXTRA_PACK_ORDER": 19,
    "dimensions": 12,
    "untouchable_modules": list(UNTOUCHABLE_MODULES),
}


def export_m0_contract() -> Dict[str, Any]:
    """反向提取基座既有契约（M0 动作清单的机器化子集）。

    只提取，不新定：编号表/相位/边Schema 全部 import 自 c18_cluster
    （V55 已落仓收口），维度冻结清单取 README 声明口径。frozen=True——
    一经冻结，变更必须走提案->归零心跳审议->版本号+1->全仓同步，
    禁止就地修改（素材契约变更流程口径采信）。
    """
    elements = ("木", "火", "土", "金", "水")
    wuxing_pairs: List[Dict[str, str]] = [
        {"a": a, "b": b, "relation": phase_relation(a, b)}
        for a in elements
        for b in elements
    ]
    return {
        "contract_version": CONTRACT_VERSION,
        "frozen": True,
        "provenance": "反向提取自仓（非新定契约）——CONT-01 忠告一落地：先写已存在的事实，只扩展不重构",
        "numbering": {
            "count": len(C18_NUMBERING),
            "ids": [e["id"] for e in C18_NUMBERING] + ["N19"],
            "fields": 9,
        },
        "wuxing_phase": {
            "tiers": 5,
            "pairs": wuxing_pairs,
            "note": "五档穷举 25 对无'无关'（含补全素材缺的被生方向）",
        },
        "edge_schema": {
            "required_fields": list(EDGE_REQUIRED_FIELDS),
            "hard_constraints": "ttl>=12 + decay∈(0,1) + rollback_token 非空（c18_cluster.validate_edge）",
        },
        "dimension_freeze": DIMENSION_FREEZE,
        "heartbeat_note": "心跳四级命名与三段式节拍为口径引用（复用 bus/craft_gate 先例）；"
                          "scheduler.py 属 untouchable，本契约不新建调度器",
    }


def check_contract(contract: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """契约贯续检查（G0 门禁）：契约成文件、frozen、四要素齐（编号/相位/边Schema/维度）。"""
    c = contract if contract is not None else export_m0_contract()
    problems: List[str] = []
    if not c.get("frozen"):
        problems.append("frozen!=True：契约未冻结")
    if c.get("numbering", {}).get("count") != 18:
        problems.append("编号表仓数!=18")
    if len(c.get("wuxing_phase", {}).get("pairs", [])) != 25:
        problems.append("五行穷举对数!=25")
    if len(c.get("edge_schema", {}).get("required_fields", [])) != len(EDGE_REQUIRED_FIELDS):
        problems.append("边Schema必填字段数不齐")
    if not c.get("dimension_freeze"):
        problems.append("维度冻结清单缺失")
    return {
        "pass": not problems,
        "problems": problems,
        "contract_version": c.get("contract_version", ""),
        "items": ["frozen", "numbering19", "wuxing25", "edge_schema", "dimension_freeze"],
    }


# ---------------------------------------------------------------------------
# 四、时间贯续（时序不乱——每步输入=上步真实产出）
# ---------------------------------------------------------------------------


def make_batch(batch: str, base_head: str, receipt_head: str) -> Dict[str, str]:
    return {"batch": batch, "base_head": base_head, "receipt_head": receipt_head}


# 真实批次链（回执对账实录：每批 base=上批 receipt——V51 起 base 为 V50 收口 9657456）
REAL_BATCH_CHAIN: List[Dict[str, str]] = [
    make_batch("V51", "9657456", "cfafdbd"),
    make_batch("V51R", "cfafdbd", "fd31369"),
    make_batch("V52", "fd31369", "4a1d2d8"),
    make_batch("V53", "4a1d2d8", "54ab736"),
    make_batch("V54", "54ab736", "32ee152"),
    make_batch("V55", "32ee152", "6e1752e"),
]


def check_temporal(chain: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
    """时间贯续：相邻批次 b[i].base_head == b[i-1].receipt_head（每期输入=上期真实产出）。

    素材 B2'先连后建'的时序倒挂在批次口径即断链——上期回执未收口，
    下期不得开工。
    """
    ch = chain if chain is not None else REAL_BATCH_CHAIN
    problems: List[str] = []
    for i in range(1, len(ch)):
        prev_receipt = ch[i - 1]["receipt_head"]
        base = ch[i]["base_head"]
        if base != prev_receipt:
            problems.append(
                "时序断裂：{}.base_head={} != {}.receipt_head={}".format(
                    ch[i]["batch"], base, ch[i - 1]["batch"], prev_receipt
                )
            )
    for i, b in enumerate(ch):
        if not b.get("batch") or not b.get("base_head") or not b.get("receipt_head"):
            problems.append("批次字段缺失：第 {} 位".format(i))
    return {
        "pass": not problems,
        "batches": len(ch),
        "problems": problems,
        "rule": "相邻批次 base_head == 上批 receipt_head（B2 时序倒挂门禁）",
    }


def answer_four_questions(chain: Optional[List[Dict[str, str]]] = None) -> Dict[str, str]:
    """素材'一句话判据'四问——四问都能用文件回答，贯续性成立（本函数给出机器侧答案）。"""
    ch = chain if chain is not None else REAL_BATCH_CHAIN
    cur = ch[-1]
    prev = ch[-2] if len(ch) >= 2 else None
    answers = {
        "现在处于哪一期": "V55 收口态之后（V55 主批+回执 {} 已冻结）".format(cur["receipt_head"]),
        "上一期交付了什么": (
            "{} 回执 {}（base={} 起）".format(prev["batch"], prev["receipt_head"], prev["base_head"])
            if prev else "起点（V50 收口）"
        ),
        "这一期凭什么开始": "base_head={}（=上期真实产出，非预期产出）".format(cur["base_head"]),
    }
    answers["出问题退到哪一步"] = (
        "退到回执 {}（上批收口态）——单批粒度回滚（V55 边Schema rollback_token 同口径）".format(prev["receipt_head"])
        if prev else "起点"
    )
    return answers


# ---------------------------------------------------------------------------
# 五、结构贯续（同构不漂——复用而非复制：import 同一对象，机器校验）
# ---------------------------------------------------------------------------


def check_structural() -> Dict[str, Any]:
    """结构贯续：复用 c18_cluster 实测（V55 已收口件完好），不复制一份'影子结构'。

    判据：18 仓编号完整+耦合矩阵自校验通过+validate_edge 硬约束照旧。
    （与素材 S1/S2/S3 口径联动——同构劣化即阻断，由主套 discover 承担。）
    """
    problems: List[str] = []
    if len(C18_NUMBERING) != 18:
        problems.append("编号表仓数!=18")
    matrix = CouplingMatrix()
    mcheck = matrix.validate()
    if not mcheck.get("ok", False):
        problems.append("耦合矩阵自校验失败：{}".format(mcheck.get("problems", [])))
    edge_probe = {
        "edge_id": "E-STRUCT-PROBE-001", "source": "C01", "target": "C03",
        "edge_type": "skeleton", "layer": "L1",
        "phase_relation": phase_relation("木", "火"),
        "resonance_strength": 0.8, "turtle_state": "保存", "horse_state": "推演",
        "ttl_ticks": 12, "decay_rate": 0.5, "rollback_token": "rb-structural-probe",
    }
    eres = validate_edge(edge_probe)
    if not eres.get("ok", False):
        problems.append("validate_edge 硬约束失效：{}".format(eres.get("problems", [])))
    return {
        "pass": not problems,
        "problems": problems,
        "reused_from": "c18_cluster（import 同一对象——零复制，指针纪律）",
        "items": ["numbering18", "matrix_validate", "edge_schema_hard_constraints"],
    }


# ---------------------------------------------------------------------------
# 六、证据贯续（可追可回——回执要素：触发批次/时间/输入快照/测试结果；
#     素材"回滚令牌"口径由边Schema 硬约束承担（结构检查实测），不重复入回执必填）
# ---------------------------------------------------------------------------

RECEIPT_REQUIRED_FIELDS: Tuple[str, ...] = (
    "batch", "status", "date", "head", "tests",
)


def check_evidential(receipt: Dict[str, Any]) -> Dict[str, Any]:
    """证据贯续：回执要素齐（触发批次/时间/输入快照 head/测试结果）——真实回执全过。"""
    problems: List[str] = []
    for f in RECEIPT_REQUIRED_FIELDS:
        if f not in receipt or receipt[f] in (None, "", []):
            problems.append("回执缺字段或空值：{}".format(f))
    return {
        "pass": not problems,
        "problems": problems,
        "required": list(RECEIPT_REQUIRED_FIELDS),
        "note": "素材四要素映射：trigger->batch / 时间->date / 输入快照->head(+prev_head_short 对账) / "
                "rollback->c18_cluster.validate_edge 硬约束（结构检查承担，不在回执重复必填）",
    }


# ---------------------------------------------------------------------------
# 七、Go/No-Go 门禁（G0-G7 八问可测化——三态诚实：未落地返回 WAIT 不虚构 PASS）
# ---------------------------------------------------------------------------


def _gate(name: str, question: str, state: str, evidence: str) -> Dict[str, str]:
    return {"gate": name, "question": question, "state": state, "evidence": evidence}


def gate_report() -> List[Dict[str, str]]:
    """G0-G7 门禁报告。核心设计：状态三态（PASS/WAIT/FAIL）——零虚构。

    未落地的门禁（跨仓事件日志/五层贯通/共演化算子/压测）诚实 WAIT，
    待对应批次（V57+ 连通件）落地后翻绿——门禁不替未来签字。
    """
    c = check_contract()
    s = check_structural()
    g0 = "PASS" if c["pass"] else "FAIL"
    g1 = "PASS" if s["pass"] else "FAIL"
    return [
        _gate(
            "G0", "所有不可变项是否已成文件并冻结？", g0,
            "export_m0_contract frozen=True（编号/相位/边Schema/维度四要素齐）"
            if g0 == "PASS" else str(c["problems"]),
        ),
        _gate(
            "G1", "18 仓是否真实存在且同构达标？", g1,
            "c18_cluster 注册表 18+1 完好（V55 收口）；远端建仓须碳基确认 create_repos_v55.py --apply"
            if g1 == "PASS" else str(s["problems"]),
        ),
        _gate(
            "G2", "是否有一条可复现的真实跨仓日志？", "WAIT",
            "连通件待产（V57 候选：event_propagator 实测化）——门禁不替未来签字",
        ),
        _gate(
            "G3", "五层是否都有可查痕迹？", "WAIT",
            "L1/L2 口径在 V55 边Schema；L3-L5 连通件未落，诚实 WAIT",
        ),
        _gate(
            "G4", "单向连接是否会被自动清理？", "WAIT",
            "双向硬规则属连通/共演化件（V57+ 候选），未落不虚报",
        ),
        _gate(
            "G5", "五项指标是否全部由脚本产出且达标？", "WAIT",
            "S5 已实测 0.0603（V55）；S1-S4 全息验证件未落——脚本产出指标部分达成",
        ),
        _gate(
            "G6", "断仓降级回滚是否全部演练通过？", "WAIT",
            "免疫压测件未产（M6 属后期批次），诚实 WAIT",
        ),
        _gate(
            "G7", "陌生人能否 30 分钟跑起来？", "WAIT",
            "install_check.py 7/7 PASS 在档（V50 实测）——'一仓+跨仓调用'全链路待连通件，WAIT",
        ),
    ]


# ---------------------------------------------------------------------------
# 八、交接单 Schema（四人组交接贯续——下游未签收上游交接单不得开工）
# ---------------------------------------------------------------------------

HANDOVER_REQUIRED_FIELDS: Tuple[str, ...] = (
    "期", "角色", "本期输入", "本期产出", "未完成任务", "已知风险",
    "下游依赖方", "回滚点", "契约版本",
)


def validate_handover(handover: Dict[str, Any]) -> Dict[str, Any]:
    """交接单校验：九字段齐（素材第九节 schema 采信）+契约版本匹配。"""
    problems: List[str] = []
    for f in HANDOVER_REQUIRED_FIELDS:
        if f not in handover or handover[f] in (None, "", []):
            problems.append("交接单缺字段或空值：{}".format(f))
    if handover.get("契约版本") not in (None, "") and handover.get("契约版本") != CONTRACT_VERSION:
        problems.append("契约版本不匹配：{}（当前冻结 {}）".format(
            handover.get("契约版本"), CONTRACT_VERSION))
    return {
        "pass": not problems,
        "problems": problems,
        "required": list(HANDOVER_REQUIRED_FIELDS),
    }


def sample_handover() -> Dict[str, Any]:
    """素材示例交接单（共振智能体 M2）的 schema 样例——样例用途，非运行时记录（诚实标注）。"""
    return {
        "期": "M2",
        "角色": "共振智能体",
        "本期输入": [CONTRACT_VERSION, "metatron_edges_78.json"],
        "本期产出": ["resonance_activator.py", "coupling_matrix_19x19.json"],
        "未完成任务": ["共振带持久化未做，仅内存态"],
        "已知风险": ["共振带重启后丢失，需 M3 补持久化"],
        "下游依赖方": "语义智能体(L4 需读耦合矩阵)",
        "回滚点": "R2",
        "契约版本": CONTRACT_VERSION,
    }


# ---------------------------------------------------------------------------
# 九、贯续张量（张量向量耦合不变——与 V52-V55 同族编码）
# ---------------------------------------------------------------------------


class ContinuityTensor:
    """贯续张量：批次链轴 bundle + 门禁状态轴（pass/wait 二态编码）——'调贯续'第一次进张量。"""

    def __init__(self, space: Optional[HypervectorSpace] = None) -> None:
        self.space = space if space is not None else HypervectorSpace()
        self._axes: Dict[str, Any] = {}

    def batch_axis(self, batch_id: str) -> Any:
        key = "batch:" + batch_id
        if key not in self._axes:
            self._axes[key] = self.space.make(key)
        return self._axes[key]

    def state_axis(self, state: str) -> Any:
        if state not in ("pass", "wait"):
            raise ValueError("state 须为 pass|wait，Got: {}".format(state))
        key = "cont:" + state
        if key not in self._axes:
            self._axes[key] = self.space.make(key)
        return self._axes[key]

    def bundle(self, batch_ids: Sequence[str], states: Sequence[str]) -> Any:
        if not batch_ids or not states:
            raise ValueError("batch_ids 与 states 不得为空")
        vecs = [self.batch_axis(b) for b in batch_ids] + [self.state_axis(s) for s in states]
        acc = [0.0] * self.space.dim
        for v in vecs:
            for i, x in enumerate(v):
                acc[i] += x
        n = float(len(vecs))
        return [x / n for x in acc]

    def similarity(self, a: Any, b: Any) -> float:
        return self.space.cosine(a, b)


# ---------------------------------------------------------------------------
# 十、总闸（ContinuityGate：五检查 + 门禁报告 + 指纹/探针/CLI）
# ---------------------------------------------------------------------------


class ContinuityGate:
    """贯续性总闸：契约/时间/结构/证据/交接单五检查 + G0-G7 门禁报告。"""

    def __init__(self) -> None:
        self.checks = ("contract", "temporal", "structural", "evidential", "handover")

    def check_contract(self) -> Dict[str, Any]:
        return check_contract()

    def check_temporal(self, chain: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        return check_temporal(chain)

    def check_structural(self) -> Dict[str, Any]:
        return check_structural()

    def check_evidential(self, receipt: Dict[str, Any]) -> Dict[str, Any]:
        return check_evidential(receipt)

    def check_handover(self, handover: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return validate_handover(handover if handover is not None else sample_handover())

    def gates(self) -> List[Dict[str, str]]:
        return gate_report()

    def self_check(self) -> Dict[str, Any]:
        results = {
            "contract": self.check_contract(),
            "temporal": self.check_temporal(),
            "structural": self.check_structural(),
            "handover": self.check_handover(),
        }
        return {
            "pass": all(r["pass"] for r in results.values()),
            "checks": {k: r["pass"] for k, r in results.items()},
            "problems": [p for r in results.values() for p in r.get("problems", [])],
        }

    def summary_report(self) -> Dict[str, Any]:
        sc = self.self_check()
        return {
            "ring": 20,
            "module": "continuity_gate",
            "axes": list(CONTINUITY_AXES),
            "self_check": sc,
            "gates": self.gates(),
            "breakpoints": list(BREAKPOINT_IDS),
            "contract_version": CONTRACT_VERSION,
        }


def _now_iso() -> str:
    return datetime.datetime.now().isoformat(timespec="seconds")


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def fingerprint() -> dict:
    return {
        "module": "continuity_gate",
        "ring": 20,
        "axes": len(CONTINUITY_AXES),
        "phases": len(PHASES),
        "breakpoints": len(BREAKPOINTS),
        "gates": 8,
        "handover_fields": len(HANDOVER_REQUIRED_FIELDS),
        "contract_version": CONTRACT_VERSION,
        "sha16": _sha256("continuity_gate:v56:ring20")[:16],
    }


def probe() -> dict:
    g = ContinuityGate()
    return {
        "fingerprint": fingerprint(),
        "self_check": g.self_check(),
        "gate_states": {x["gate"]: x["state"] for x in g.gates()},
    }


def _main(argv: List[str]) -> int:
    import argparse

    parser = argparse.ArgumentParser(prog="continuity_gate", description="贯续性门禁件（V56 ring20）")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("run", help="自检五检查+门禁报告")
    sub.add_parser("contract", help="导出 M0 冻结契约（JSON）")
    sub.add_parser("gates", help="G0-G7 门禁报告（三态诚实）")
    sub.add_parser("probe", help="指纹+探针")
    sub.add_parser("breakpoints", help="B1-B10 断裂点清单")
    args = parser.parse_args(argv[1:] if len(argv) > 1 else ["run"])
    cmd = args.cmd or "run"
    if cmd == "run":
        report = ContinuityGate().summary_report()
        sc = report["self_check"]
        print("[continuity_gate] self_check pass={} checks={}".format(sc["pass"], sc["checks"]))
        for g in report["gates"]:
            print("  {}: {} ({})".format(g["gate"], g["state"], g["question"]))
        ok = sc["pass"]
    elif cmd == "contract":
        print(json.dumps(export_m0_contract(), ensure_ascii=False, indent=1))
        ok = True
    elif cmd == "gates":
        for g in gate_report():
            print("  {}: {} | {}".format(g["gate"], g["state"], g["evidence"]))
        ok = True
    elif cmd == "probe":
        print(json.dumps(probe(), ensure_ascii=False, indent=1))
        ok = True
    else:  # breakpoints
        for b in BREAKPOINTS:
            print("  {} | {} | 先例：{}".format(b["id"], b["symptom"], b["precedent"]))
        ok = True
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv))
