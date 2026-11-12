# -*- coding: utf-8 -*-
"""
meridian_link —— 经络链接模块（V62 · ring23 patch2 搜索网与打捞域·经络链接批）
================================================================================
源声明（诚实边界）：
  · 素材源 = 碳基 2026-11-12 三轮指令：①"将已经吸纳的新的项目碎片组合体在其
    对应的仓库建立经络链接，注意包括但不限于全息性、自组织相似性、耗散结构、
    共振态等所有机制，要求完全匹配基座的所有已存机制，遍历穷举表里相应的
    细致链接"；②纠偏"查询向量海文件架构，将本项目内核机制遍历穷举列出作为
    信息补充——你没有理解细致链接的意义"；③手工三轮补充机制清单（合计
    17 条点名）。碳基点名即口径——但本模块的机制轴**不以手抄为准**，以仓内
    内核机制注册表为基座（klein/titan M01-M11 + concept_anatomy CONCEPT_MAP +
    topology_resonance 八组件与常量 + holo_forge HOLO_MECHANISMS），import
    对账完全匹配（check_registry 五源一致才 PASS）。
  · 碎片源 = data/searchnet_d03_b.json（V61 落盘 B 榜 10 条——已吸纳项目碎片
    组合体，全员 unverified；essence 仅 kafka 一条实录，其余 9 条如实 null——
    复用 salvage_gate.load_d03_b 零复制）。
  · 本模块为四人组第一性原理扬弃后的**可测子集**，不是照搬——扬弃裁决全记录
    见投喂包第 1 节。

内核机制穷举注册表（25 位，五源 import 对账）：
  · 公理层 2 位：全息（P01 局部包含整体）/万物互联（P02 契约即接口）
    ——锚 titan_evolver.AXIOMS + holo_forge.AXIOMS；
  · 矩阵层 2 位：1331×1331 节点矩阵（LOGICAL_POSITIONS=1,771,561 逻辑位置）/
    108641 活跃节点共振（ACTIVE_NODES 与 EMERGENCE_THRESHOLD——共振对数
    超阈值则涌现）——锚 packs/topology_resonance_pack 常量；
  · 核心机制层 11 位：M01 心跳/M02 细胞骨架/M03 皮肤/M04 经络/M05 赫布协作场/
    M06 语义通信基座/M07 自组织相似性/M08 runtime/M09 graph/M10 类社会组合体/
    M11 城邦架构——锚 klein_projection.MECHANISMS（关键词表原表直用）+
    titan_evolver.MECHANISMS（角色表）+ holo_forge.HOLO_MECHANISMS（名称变体）；
  · 耗散验证层 2 位：自组织耗散（开放系统+远离平衡+非线性+涨落放大→涌现，
    topology_runtime）/去幻觉（Leibniz PSR+张平Seb+赫布场，dehallucination）
    ——锚 concept_anatomy.CONCEPT_MAP；
  · 经络子机制层 8 位：共振节点/曼陀罗一拖八/莫比乌斯扩张/克莱因收敛/卡尔曼
    滤波/贝叶斯干涉（在仓实名贝叶斯守卫 bayesian_guard）/希尔伯特空间/耗散度量
    ——锚 packs/topology_resonance_pack 八函数。

知己知彼实录（口径核查，如实澄清）：
  ①碳基三轮点名 17 机制全部落位（NAMED_BY_CARBON 固化对账，check_named
    固化测试）——点名是校验子集不是轴本身，"包括但不限于"由 import 对账
    兜底（皮肤/runtime/graph/类社会组合体/城邦/去幻觉/耗散度量/万物互联
    八位未点名但在轴——完全匹配基座所有已存机制）。
  ②名称异形对账——holo_forge 用"经络机制/自组织相似性类节点共振"，klein
    用"经络/自组织相似性"（NAME_VARIANTS 映射留痕，同一机制不同书写形）；
    碳基"贝叶斯干涉"在仓实名"贝叶斯守卫（bayesian_guard）/guard L10 贝叶斯
    层/org_gate G-M 阻塞贝叶斯衍射反演"——同族异名如实登记。
  ③"108641 共振带配额"维持 V55 弃裁决（数字挪用不诚实——tensor_gate/
    org_gate 两处留痕在案）；本轴按"活跃节点共振/涌现阈值"口径注册
    （topology_resonance ACTIVE_NODES=108641 与 EMERGENCE_THRESHOLD=108641
    常量在案，c18_cluster 已澄清 N19 语境是"当前语言模式"数字非共振带索引）。
  ④B 榜落盘字段无 desc/topics（V61 实录口径）——链接证据三源=repo 名（英文
    键匹配）+leg 三腿（中文键匹配）+essence（中文键匹配，仅 kafka 在案）；
    essence 为 null 的碎片其无命中格=pending-evidence（V56 WAIT 三态先例——
    证据不足不下定论），kafka（essence 在案）无命中格=unlinked（全证据实测）。

细致链接判定（三态）：
  · linked           —— 至少一键命中，证据留痕 [键, 证据源] 逐条可复算；
  · pending-evidence —— 无命中且碎片 essence 为 null（desc/essence 到场后
                        判定可能翻转，如实挂起不虚报）；
  · unlinked         —— 无命中且碎片 essence 在案（全证据实测无链接，确定性）。

扬弃（弃）实录：不替碎片补 取/舍 字段（链接表≠search_record——吸纳完成须
  另走 search_record 八字段，V59 纪律不越权）；不虚报 linked（无证据即
  pending/unlinked）；不采"共振带配额"口径（V55 裁决维持）；不新建通道
  （链接经 C03 既有总线仓口径，G-M 门禁对账——org_gate 硬约束"C03 未过
  G-M 前禁止启动任何领域深化批次"如实携带）；扩展键禁含碎片名（只有能力
  词，每条附语义出处注记）。
扬弃（取）实录：机制轴 import 对账完全匹配（klein/titan/holo_forge/
  CONCEPT_MAP/topology_resonance 五源一致才 PASS）；碳基点名 17 条固化
  测试；三态链接判定+证据留痕；250 格（10 碎片×25 机制）穷举无缺格；
  经络路径=碎片→D03→C03 总线仓→机制→锚模块；klein 关键词原表 import
  直用零复制（指针纪律）。

与工程纪律的同构照（升维句，见投喂包第 1 节）：
    碎片第一次被接进经络而不是被收藏——每一格（碎片×机制）都有确定性判定
    与证据；机制轴与基座注册表 import 对账，基座一变链接表自动显形为过期；
    穷举不许跳格——判定可以是没有链接，但不许没有判定。
"""
from __future__ import annotations

import io
import json
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

from .klein_projection import MECHANISMS as KLEIN_MECHANISMS
from .titan_evolver import MECHANISMS as TITAN_MECHANISMS, AXIOMS as TITAN_AXIOMS
from .holo_forge import HOLO_MECHANISMS
from .concept_anatomy import CONCEPT_MAP
from .packs.topology_resonance_pack import (
    MATRIX_ROWS,
    MATRIX_COLS,
    LOGICAL_POSITIONS,
    ACTIVE_NODES,
    EMERGENCE_THRESHOLD,
    RESONANCE_THRESHOLD,
    DISSIPATION_ENTROPY_MAX,
    MANDALA_TOTAL,
    resonance_node,
    mandala_fanout,
    mobius_edge,
    klein_convergence,
    kalman_state,
    bayesian_guard,
    hilbert_project,
    dissipation_measure,
)
from .org_gate import c03_gate_report
from .salvage_gate import load_d03_b

SEAL = "潮起开门，潮落闭嘴"
SCHEMA_VERSION = "MERIDIAN-LINK-v1.0"
DATA_OUT_NAME = "searchnet_d03_meridian.json"

# ---------------------------------------------------------------------------
# 一、内核机制穷举注册表（25 位——五源 import 对账）
# ---------------------------------------------------------------------------

# klein 原表关键词直用（指针纪律——import 不复制；M01-M11 的英文键基座）
_KLEIN_KEYS: Dict[str, Tuple[str, ...]] = {
    m["id"]: tuple(m["keywords"]) for m in KLEIN_MECHANISMS
}

# V62 语义扩展键（中文键匹配 leg/essence，英文键匹配 repo 名；每层注记语义
# 出处；禁含碎片名——只有能力词。"trac"=D03 扩展词 distributed tracing/
# trace propagation（V61 P2 在案）；"apm/monitor"=scheduler 存活检测与健康
# 判定职能（链路可观测腿的机制落点）；M04 中文键=D03 意图"消息路由/链路"）
_EXT_KEYS: Dict[str, Tuple[str, ...]] = {
    "M01": ("可观测", "监控", "巡检", "节拍", "apm", "monitor"),
    "M02": ("骨架", "装配", "构建"),
    "M03": ("守卫", "校验", "过滤"),
    "M04": ("总线", "消息路由", "路由", "链路", "事件", "消息", "trac"),
    "M05": ("强化", "共现", "信任权重"),
    "M06": ("协议", "语义", "信封"),
    "M07": ("自组织", "相似"),
    "M08": ("编排", "工作流", "调度"),
    "M09": ("图谱", "邻接"),
    "M10": ("分工", "角色", "社会"),
    "M11": ("台账", "登记", "归档", "日志"),
}

_AXIOM_KEYS: Dict[str, Tuple[str, ...]] = {
    "A1": ("holo", "holograph", "全息"),
    "A2": ("linkage", "interconnect", "万物互联"),
}

_MATRIX_KEYS: Dict[str, Tuple[str, ...]] = {
    "X1": ("1331", "matrix", "节点矩阵"),
    "X2": ("108641", "active-node", "活跃节点"),
}

_CONCEPT_KEYS: Dict[str, Tuple[str, ...]] = {
    "C1": ("dissip", "entropy", "耗散", "熵", "熔断"),
    "C2": ("hallucin", "grounded", "幻觉"),
}

_SUB_KEYS: Dict[str, Tuple[str, ...]] = {
    "R1": ("resonance", "emergence", "共振", "涌现"),
    "R2": ("fanout", "mandala", "一拖八", "扩散"),
    "R3": ("mobius", "回流", "扩张"),
    "R4": ("converg", "pareto", "nsga", "收敛", "蒸馏"),
    "R5": ("kalman", "estimat", "滤波", "估计"),
    "R6": ("bayes", "posterior", "prior", "贝叶斯", "干涉", "衍射"),
    "R7": ("hilbert", "希尔伯特"),
    "R8": ("dissip", "entropy", "耗散", "熵"),
}


def _core(mid: str, name: str, en: str, anchors: Tuple[str, ...],
          note: str) -> Dict[str, Any]:
    """核心机制层条目：键 = klein 原表（import 直用）+ V62 语义扩展。"""
    return {"id": mid, "layer": "核心机制", "name": name, "en": en,
            "anchors": anchors, "note": note,
            "keys": _KLEIN_KEYS[mid] + _EXT_KEYS[mid],
            "keys_base": "klein_projection.MECHANISMS.keywords（原表 import 直用）",
            "keys_ext": "V62 语义扩展：" + "、".join(_EXT_KEYS[mid])}


KERNEL_MECHANISMS: Tuple[Dict[str, Any], ...] = (
    # —— 公理层（2）——
    {"id": "A1", "layer": "公理", "name": "全息", "en": "holography",
     "anchors": ("titan_evolver.AXIOMS[P01]", "holo_forge.AXIOMS[holography]",
                 "scheduler（全息投影：局部可观测整体）"),
     "note": "局部包含整体（titan P01 原文：一条能力的缺口即全局演进方向的线索）",
     "keys": _AXIOM_KEYS["A1"]},
    {"id": "A2", "layer": "公理", "name": "万物互联", "en": "universal_linkage",
     "anchors": ("titan_evolver.AXIOMS[P02]", "holo_forge.AXIOMS[universal_linkage]"),
     "note": "契约即接口（titan P02 原文：候选只需可判定的元数据即可入链）",
     "keys": _AXIOM_KEYS["A2"]},
    # —— 矩阵层（2）——
    {"id": "X1", "layer": "矩阵", "name": "1331×1331 节点矩阵", "en": "node_matrix",
     "anchors": ("topology_resonance_pack.MATRIX_ROWS/MATRIX_COLS",
                 "LOGICAL_POSITIONS=1,771,561"),
     "note": "1331=11³；1331×1331=11⁶=1,771,561 逻辑位置（蓝图 L2 矩阵层）",
     "keys": _MATRIX_KEYS["X1"]},
    {"id": "X2", "layer": "矩阵", "name": "108641 活跃节点共振", "en": "active_resonance",
     "anchors": ("topology_resonance_pack.ACTIVE_NODES=108641",
                 "EMERGENCE_THRESHOLD=108641（共振对数超阈值→涌现）"),
     "note": "活跃节点/涌现阈值口径（V55“共振带配额”弃裁决维持——数字挪用不诚实，"
             "本条按常量在案口径注册）",
     "keys": _MATRIX_KEYS["X2"]},
    # —— 核心机制层（11，klein/titan 双表同源）——
    _core("M01", "心跳", "heartbeat",
          ("klein_projection.MECHANISMS[M01]", "titan_evolver.MECHANISMS[M01]",
           "scheduler（原“全息心跳”）", "bus.Bus.heartbeat（craft_gate ORGAN_MAP）"),
          "定时节拍与存活检测/健康判定（scheduler 职能——链路可观测腿的机制落点）"),
    _core("M02", "细胞骨架", "cytoskeleton",
          ("klein_projection.MECHANISMS[M02]", "titan_evolver.MECHANISMS[M02]",
           "kernel（自述原“细胞骨架”）", "craft_gate.StepRail"),
          "装配骨与固定轨道：agent/scaffold/assemble（骨架职能）"),
    _core("M03", "皮肤", "skin",
          ("klein_projection.MECHANISMS[M03]", "titan_evolver.MECHANISMS[M03]",
           "guard（自述原“皮肤”，L1-L10）", "craft_gate.CleanRoomGate"),
          "暴露面控制与校验：guard/filter/validate/sanitize/schema"),
    _core("M04", "经络", "meridian",
          ("klein_projection.MECHANISMS[M04]", "titan_evolver.MECHANISMS[M04]",
           "bus + router_layer（CONCEPT_MAP 经络机制）",
           "concept_anatomy.holo_meridian→topology_resonance.resonance_node",
           "craft_gate.MERIDIAN_MAP"),
          "消息路由与链路传导：route/channel/dispatch/bus/pipeline（D03 意图“消息路由、链路可观测”的本位机制；扩展词 distributed tracing 在案）"),
    _core("M05", "赫布协作场", "hebbian",
          ("klein_projection.MECHANISMS[M05]", "titan_evolver.MECHANISMS[M05]",
           "graph.AdaptiveGraph（自述原“赫布协作场”，hebbian_step）"),
          "共现强化：weight/reinforce/coactivate/hebb/trust"),
    _core("M06", "语义通信基座", "semantic_bus",
          ("klein_projection.MECHANISMS[M06]", "titan_evolver.MECHANISMS[M06]",
           "envelope + skill + 张平Seb（CONCEPT_MAP）", "bus（Envelope，V3）"),
          "信封/协议/编解码：envelope/message/protocol/codec/json"),
    _core("M07", "自组织相似性", "similarity",
          ("klein_projection.MECHANISMS[M07]", "titan_evolver.MECHANISMS[M07]",
           "dehallucination（自组织相似性全息去幻觉）",
           "向量海 runtime selforg_similarity.py（指针登记）",
           "topology_resonance 核心哲学"),
          "相似聚类与共振打分：cluster/resonance/similarity/embedding/vector"),
    _core("M08", "runtime", "runtime",
          ("klein_projection.MECHANISMS[M08]", "titan_evolver.MECHANISMS[M08]",
           "router_layer + scheduler（CONCEPT_MAP 心跳机制双锚）"),
          "运行时编排：runtime/loop/scheduler/orchestrat/worker（D03 意图“编排”的本位机制）"),
    _core("M09", "graph", "graph",
          ("klein_projection.MECHANISMS[M09]", "titan_evolver.MECHANISMS[M09]",
           "graph.AdaptiveGraph 邻接表", "swarm_intel.EntityGraph"),
          "图结构：graph/node/edge/adjacency/rag/entity"),
    _core("M10", "类社会组合体", "society",
          ("klein_projection.MECHANISMS[M10]", "titan_evolver.MECHANISMS[M10]",
           "swarm_intel（agent 群体+社交演化记录）"),
          "角色分工与涌现：role/division/emergent/society/cooperation"),
    _core("M11", "城邦架构", "citystate",
          ("klein_projection.MECHANISMS[M11]", "titan_evolver.MECHANISMS[M11]",
           "packs（PACK_ORDER=9 域包+EXTRA_PACK_ORDER 扩展包）",
           "craft_gate MERIDIAN_MAP 台账"),
          "登记簿与归档：registry/ledger/archive/index（可观测数据的台账面）"),
    # —— 耗散验证层（2，CONCEPT_MAP 独有概念）——
    {"id": "C1", "layer": "耗散验证", "name": "自组织耗散", "en": "selforg_dissipation",
     "anchors": ("concept_anatomy.CONCEPT_MAP[自组织耗散]",
                 "topology_runtime（StateReducer+Checkpoint+CircuitBreaker+DissipationMonitor）",
                 "org_gate（总判据=耗散结构：没有输入就退化的系统才配叫有机体）",
                 "topology_resonance_pack.dissipation_measure"),
     "note": "开放系统+远离平衡+非线性+涨落放大→涌现（CONCEPT_MAP 原文）",
     "keys": _CONCEPT_KEYS["C1"]},
    {"id": "C2", "layer": "耗散验证", "name": "去幻觉", "en": "dehallucination",
     "anchors": ("concept_anatomy.CONCEPT_MAP[去幻觉]", "dehallucination.py",
                 "academic_gate（V40 学术笔痕闸门同族）"),
     "note": "8 阶段流水线：Leibniz PSR+张平Seb+赫布场+耗散熵判定",
     "keys": _CONCEPT_KEYS["C2"]},
    # —— 经络子机制层（8，topology_resonance 八函数）——
    {"id": "R1", "layer": "经络子机制", "name": "共振节点", "en": "resonance_node",
     "anchors": ("topology_resonance_pack.resonance_node",
                 "RESONANCE_THRESHOLD=0.75（余弦相似度超值则共振）"),
     "note": "1331×1331 共振节点检测：共振=余弦相似度×负载均衡因子，超阈值→涌现",
     "keys": _SUB_KEYS["R1"]},
    {"id": "R2", "layer": "经络子机制", "name": "曼陀罗一拖八", "en": "mandala_fanout",
     "anchors": ("topology_resonance_pack.mandala_fanout",
                 "MANDALA_TOTAL=9（1 中心+8 方位）"),
     "note": "曼陀罗扩散：1 拖 8 方位分发",
     "keys": _SUB_KEYS["R2"]},
    {"id": "R3", "layer": "经络子机制", "name": "莫比乌斯扩张", "en": "mobius_edge",
     "anchors": ("topology_resonance_pack.mobius_edge", "mobius_vortex（状态回流环 V26）"),
     "note": "莫比乌斯边/回流：执行面走一圈回到总侧面（呼吸循环的扩张侧）",
     "keys": _SUB_KEYS["R3"]},
    {"id": "R4", "layer": "经络子机制", "name": "克莱因收敛", "en": "klein_convergence",
     "anchors": ("topology_resonance_pack.klein_convergence",
                 "klein_projection（全息投影吸纳 V27）",
                 "向量海 runtime klein_nsga2.py（指针登记）"),
     "note": "非支配排序截取最小充分集（呼吸循环的收敛侧；NSGA-II 可计算）",
     "keys": _SUB_KEYS["R4"]},
    {"id": "R5", "layer": "经络子机制", "name": "卡尔曼滤波", "en": "kalman_state",
     "anchors": ("topology_resonance_pack.kalman_state",),
     "note": "观测状态估计：卡尔曼滤波状态机",
     "keys": _SUB_KEYS["R5"]},
    {"id": "R6", "layer": "经络子机制", "name": "贝叶斯干涉", "en": "bayesian_guard",
     "anchors": ("topology_resonance_pack.bayesian_guard", "guard.L10（贝叶斯层）",
                 "org_gate G-M 阻塞机制（贝叶斯衍射反演）"),
     "note": "碳基称“贝叶斯干涉”，在仓实名贝叶斯守卫/L10 贝叶斯层/贝叶斯衍射"
             "反演——同族异名如实登记",
     "keys": _SUB_KEYS["R6"]},
    {"id": "R7", "layer": "经络子机制", "name": "希尔伯特空间", "en": "hilbert_project",
     "anchors": ("topology_resonance_pack.hilbert_project",
                 "蓝图 L2 希尔伯特算力（hilbert_scm，本地构建物排 include——指针登记）"),
     "note": "希尔伯特投影（辅助函数）：高维空间的正交投影",
     "keys": _SUB_KEYS["R7"]},
    {"id": "R8", "layer": "经络子机制", "name": "耗散度量", "en": "dissipation_measure",
     "anchors": ("topology_resonance_pack.dissipation_measure",
                 "DISSIPATION_ENTROPY_MAX=0.95（熵超值触发自组织重组）"),
     "note": "耗散熵度量（辅助函数）：任务流的熵观测",
     "keys": _SUB_KEYS["R8"]},
)

# 名称变体映射（holo_forge HOLO_MECHANISMS 的异形名 → 注册表 id——同一机制
# 不同书写形，如实留痕不合并词条）
NAME_VARIANTS: Dict[str, str] = {
    "心跳机制": "M01", "细胞骨架": "M02", "皮肤机制": "M03", "经络机制": "M04",
    "赫布协作场": "M05", "语义通信基座": "M06", "自组织相似性类节点共振": "M07",
    "runtime": "M08", "graph": "M09", "类社会组合体": "M10", "城邦架构": "M11",
}

# CONCEPT_MAP 概念 → 注册表 id（concept_anatomy 十概念全覆盖映射）
CONCEPT_COVERAGE: Dict[str, str] = {
    "经络": "M04", "心跳机制": "M01", "细胞骨架": "M02", "皮肤机制": "M03",
    "经络机制": "M04", "赫布协作场": "M05", "语义通信基座": "M06",
    "城邦架构": "M11", "自组织耗散": "C1", "去幻觉": "C2",
}

# 碳基三轮点名（2026-11-12）→ 注册表 id——点名是校验子集不是轴本身
NAMED_BY_CARBON: Tuple[Tuple[str, str], ...] = (
    # 第一轮（需求原文"包括但不限于"）
    ("全息性", "A1"), ("自组织相似性", "M07"), ("耗散结构", "C1"), ("共振态", "R1"),
    # 第二轮（手工补充十条）
    ("细胞骨架机制", "M02"), ("全息心跳机制", "M01"), ("语义通信基座", "M06"),
    ("经络", "M04"), ("赫布协作", "M05"), ("希尔伯特空间", "R7"),
    ("莫比乌斯扩张", "R3"), ("克莱因收敛", "R4"), ("曼陀罗一拖八", "R2"),
    ("卡尔曼滤波", "R5"),
    # 第三轮（三条补充）
    ("1331*1331 节点", "X1"), ("108641 共振", "X2"), ("贝叶斯干涉", "R6"),
)

# 经络子机制函数锚（八函数可调用性对账）
SUB_MECH_FUNCS: Dict[str, Any] = {
    "R1": resonance_node, "R2": mandala_fanout, "R3": mobius_edge,
    "R4": klein_convergence, "R5": kalman_state, "R6": bayesian_guard,
    "R7": hilbert_project, "R8": dissipation_measure,
}

_VALID_LAYERS = ("公理", "矩阵", "核心机制", "耗散验证", "经络子机制")


# ---------------------------------------------------------------------------
# 二、碎片装载（复用 salvage_gate.load_d03_b 零复制）与证据口径
# ---------------------------------------------------------------------------

VALID_LEGS = ("编排", "总线", "可观测")


def load_fragments() -> List[Dict[str, Any]]:
    """装载已吸纳项目碎片组合体（B 榜 10 条——load_d03_b 零复制复用）。"""
    data = load_d03_b()
    rows = data.get("results", [])
    if len(rows) != 10:
        raise ValueError("B 榜碎片!=10 条（实 {}）".format(len(rows)))
    for r in rows:
        if r.get("leg") not in VALID_LEGS:
            raise ValueError("碎片 leg 非法：{} -> {!r}".format(r.get("repo"), r.get("leg")))
        if r.get("verify_status") != "unverified":
            raise ValueError("碎片 verify_status 非 unverified（诚实口径）：{}"
                             .format(r.get("repo")))
    return rows


def _is_ascii(s: str) -> bool:
    return all(ord(ch) < 128 for ch in s)


def _evidence_texts(row: Dict[str, Any]) -> Dict[str, str]:
    """碎片证据三源（V61 落盘字段口径如实）：repo 名（英文键域）/
    leg（中文键域）/essence（中文键域，仅 kafka 在案其余 null）。"""
    return {"name": (row.get("repo") or "").lower(),
            "leg": row.get("leg") or "",
            "essence": row.get("essence") or ""}


def link_cell(row: Dict[str, Any], mech: Dict[str, Any]) -> Dict[str, Any]:
    """细致链接判定（三态）：键命中→linked（证据留痕）；无命中且 essence
    为 null→pending-evidence（V56 WAIT 先例）；无命中且 essence 在案→
    unlinked（全证据实测）。英文键匹配 repo 名（大小写不敏感子串），
    中文键匹配 leg/essence（子串）。"""
    texts = _evidence_texts(row)
    evidence: List[List[str]] = []
    for key in mech["keys"]:
        if _is_ascii(key):
            if key and key in texts["name"]:
                evidence.append([key, "name"])
        else:
            if key and (key in texts["leg"] or key in texts["essence"]):
                src = "leg" if key in texts["leg"] else "essence"
                evidence.append([key, src])
    if evidence:
        state = "linked"
    elif not texts["essence"]:
        state = "pending-evidence"
    else:
        state = "unlinked"
    return {"repo": row.get("repo"), "rank": row.get("rank"),
            "mech": mech["id"], "mech_name": mech["name"], "layer": mech["layer"],
            "state": state, "evidence": evidence}


def build_meridian_table() -> List[Dict[str, Any]]:
    """穷举构建经络链接表：10 碎片×25 机制=250 格，无跳格（判定可以是
    没有链接，但不许没有判定）。纯函数——同输入同输出（确定性纪律）。"""
    fragments = load_fragments()
    return [link_cell(row, mech)
            for row in fragments
            for mech in KERNEL_MECHANISMS]


# ---------------------------------------------------------------------------
# 三、完全匹配校验（基座 import 对账 + 碳基点名对账 + 穷举对账）
# ---------------------------------------------------------------------------

def check_registry() -> Dict[str, Any]:
    """机制轴完全匹配校验：25 位/层计数/核心 11 位与 klein+titan 双表逐项
    一致/holo_forge 异形名全覆盖/CONCEPT_MAP 十概念全覆盖/矩阵常量在案/
    八子机制函数可调用。基座注册表一变（新增/改名/删减），本检查即 FAIL
    ——链接表自动显形为过期，完全匹配不靠手 Claim 靠 import。"""
    problems: List[str] = []
    if len(KERNEL_MECHANISMS) != 25:
        problems.append("机制轴!=25 位（实 {}）".format(len(KERNEL_MECHANISMS)))
    layers: Dict[str, int] = {}
    for m in KERNEL_MECHANISMS:
        layers[m["layer"]] = layers.get(m["layer"], 0) + 1
        if m["layer"] not in _VALID_LAYERS:
            problems.append("非法层：{}（{}）".format(m["id"], m["layer"]))
        if not m.get("keys"):
            problems.append("机制无链接键：{}".format(m["id"]))
    for layer, want in (("公理", 2), ("矩阵", 2), ("核心机制", 11),
                        ("耗散验证", 2), ("经络子机制", 8)):
        if layers.get(layer) != want:
            problems.append("层计数 {}!={}（实 {}）".format(layer, want, layers.get(layer)))
    # 核心 11 位与 klein/titan 双表逐项一致（id+name）
    core = [m for m in KERNEL_MECHANISMS if m["layer"] == "核心机制"]
    for src_name, src in (("klein", KLEIN_MECHANISMS), ("titan", TITAN_MECHANISMS)):
        if [(m["id"], m["name"]) for m in core] != [(m["id"], m["name"]) for m in src]:
            problems.append("核心 11 位与 {} 表不一致（基座漂移）".format(src_name))
    # 核心 11 位键 ⊇ klein 原表键（指针纪律——import 直用不删减）
    klein_key_map = {m["id"]: tuple(m["keywords"]) for m in KLEIN_MECHANISMS}
    for m in core:
        base = klein_key_map[m["id"]]
        if tuple(m["keys"])[:len(base)] != base:
            problems.append("机制 {} 键基座不含 klein 原表键（指针纪律破坏）".format(m["id"]))
    # holo_forge 异形名全覆盖
    ids = {m["id"] for m in KERNEL_MECHANISMS}
    for vname in HOLO_MECHANISMS:
        if NAME_VARIANTS.get(vname) not in ids:
            problems.append("holo_forge 机制名无覆盖：{}".format(vname))
    # CONCEPT_MAP 十概念全覆盖
    for cname in CONCEPT_MAP:
        if CONCEPT_COVERAGE.get(cname) not in ids:
            problems.append("CONCEPT_MAP 概念无覆盖：{}".format(cname))
    # 矩阵常量在案（import 对账）
    if (MATRIX_ROWS, MATRIX_COLS, LOGICAL_POSITIONS) != (1331, 1331, 1771561):
        problems.append("矩阵常量漂移：{}×{}={}".format(MATRIX_ROWS, MATRIX_COLS, LOGICAL_POSITIONS))
    if ACTIVE_NODES != 108641 or EMERGENCE_THRESHOLD != 108641:
        problems.append("活跃节点/涌现阈值常量漂移：{}/{}".format(ACTIVE_NODES, EMERGENCE_THRESHOLD))
    if RESONANCE_THRESHOLD != 0.75 or DISSIPATION_ENTROPY_MAX != 0.95:
        problems.append("共振/耗散阈值常量漂移")
    if MANDALA_TOTAL != 9:
        problems.append("曼陀罗总数常量漂移：{}".format(MANDALA_TOTAL))
    # 八子机制函数可调用
    for sid, fn in SUB_MECH_FUNCS.items():
        if not callable(fn):
            problems.append("子机制函数不可调用：{}".format(sid))
    # 公理双锚在案
    if len(TITAN_AXIOMS) != 2:
        problems.append("titan 公理!=2（实 {}）".format(len(TITAN_AXIOMS)))
    return {"pass": not problems, "problems": problems,
            "mechanisms": len(KERNEL_MECHANISMS), "layers": layers,
            "sources": ("klein_projection.MECHANISMS", "titan_evolver.MECHANISMS",
                        "holo_forge.HOLO_MECHANISMS", "concept_anatomy.CONCEPT_MAP",
                        "topology_resonance_pack（八函数+常量）"),
            "note": "完全匹配不靠手 Claim 靠 import——基座注册表漂移即 FAIL"}


def check_named() -> Dict[str, Any]:
    """碳基三轮点名 17 条对账：每条落位注册表（点名是校验子集不是轴本身，
    "包括但不限于"由 check_registry 兜底）。"""
    problems: List[str] = []
    ids = {m["id"] for m in KERNEL_MECHANISMS}
    for label, mid in NAMED_BY_CARBON:
        if mid not in ids:
            problems.append("碳基点名无落位：{}->{}".format(label, mid))
    if len(NAMED_BY_CARBON) != 17:
        problems.append("点名条目!=17（实 {}）".format(len(NAMED_BY_CARBON)))
    covered = {mid for _, mid in NAMED_BY_CARBON}
    if len(covered) != 17:
        problems.append("点名覆盖去重后!=17（实 {}）".format(len(covered)))
    return {"pass": not problems, "problems": problems,
            "named": len(NAMED_BY_CARBON), "distinct": len(covered),
            "rounds": "三轮：4（需求原文）+10（手工补充）+3（补充）",
            "note": "17/25 点名在轴；余 8 位（万物互联/皮肤/runtime/graph/"
                    "类社会组合体/城邦架构/去幻觉/耗散度量）由 import 对账兜底"}


def check_linkage(table: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """穷举对账：250 格无缺格/三态合法/pending 仅限 essence null 碎片/
    unlinked 仅限 essence 在案碎片/linked 证据非空且逐格可复算。"""
    problems: List[str] = []
    if table is None:
        table = build_meridian_table()
    fragments = load_fragments()
    essence_map = {r["repo"]: bool(r.get("essence")) for r in fragments}
    want_pairs = {(r["repo"], m["id"]) for r in fragments for m in KERNEL_MECHANISMS}
    got_pairs = {(c["repo"], c["mech"]) for c in table}
    if len(table) != 250:
        problems.append("链接表!=250 格（实 {}）".format(len(table)))
    missing = want_pairs - got_pairs
    if missing:
        problems.append("缺格 {} 处：{}".format(len(missing), sorted(missing)[:3]))
    extra = got_pairs - want_pairs
    if extra:
        problems.append("多格 {} 处：{}".format(len(extra), sorted(extra)[:3]))
    for c in table:
        if c["state"] not in ("linked", "pending-evidence", "unlinked"):
            problems.append("非法态：{}×{}".format(c["repo"], c["mech"]))
        if c["state"] == "linked" and not c["evidence"]:
            problems.append("linked 无证据：{}×{}".format(c["repo"], c["mech"]))
        if c["state"] == "linked":
            for kv in c["evidence"]:
                if len(kv) != 2 or kv[1] not in ("name", "leg", "essence"):
                    problems.append("证据源非法：{}×{}".format(c["repo"], c["mech"]))
        has_ess = essence_map.get(c["repo"])
        if c["state"] == "pending-evidence" and has_ess:
            problems.append("pending 但 essence 在案（应 unlinked）：{}×{}"
                            .format(c["repo"], c["mech"]))
        if c["state"] == "unlinked" and not has_ess:
            problems.append("unlinked 但 essence 缺（应 pending）：{}×{}"
                            .format(c["repo"], c["mech"]))
    # linked 证据逐格可复算（重跑判定比对）
    mech_map = {m["id"]: m for m in KERNEL_MECHANISMS}
    frag_map = {r["repo"]: r for r in fragments}
    for c in table:
        if c["state"] == "linked":
            again = link_cell(frag_map[c["repo"]], mech_map[c["mech"]])
            if again["evidence"] != c["evidence"]:
                problems.append("证据不可复算：{}×{}".format(c["repo"], c["mech"]))
    counts: Dict[str, int] = {"linked": 0, "pending-evidence": 0, "unlinked": 0}
    for c in table:
        counts[c["state"]] += 1
    return {"pass": not problems, "problems": problems, "cells": len(table),
            "counts": counts,
            "note": "判定可以是没有链接，但不许没有判定（穷举无跳格）"}


def meridian_summary(table: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """经络汇总：每机制链接数/每碎片链接数/C03 总线仓与 G-M 门禁对账。"""
    if table is None:
        table = build_meridian_table()
    by_mech: Dict[str, int] = {}
    by_frag: Dict[str, int] = {}
    for c in table:
        if c["state"] == "linked":
            by_mech[c["mech"]] = by_mech.get(c["mech"], 0) + 1
            by_frag[c["repo"]] = by_frag.get(c["repo"], 0) + 1
    gm = c03_gate_report()
    return {
        "cang": "holoaeon-c03-meridian",
        "dim": "D03",
        "fragments": 10, "mechanisms": len(KERNEL_MECHANISMS), "cells": len(table),
        "linked_total": sum(by_mech.values()),
        "by_mechanism": {m["id"]: {"name": m["name"], "linked": by_mech.get(m["id"], 0)}
                         for m in KERNEL_MECHANISMS},
        "by_fragment": by_frag,
        "gm_gate": {"gate": "G-M", "pass": gm["pass"],
                    "wait_items": [k for k, v in gm["states"].items() if v == "WAIT"],
                    "hard_rule": gm["hard_rule"]},
        "note": "经络先行：链接表落 C03 总线仓台账；C03 未过 G-M 前禁止启动"
                "任何领域深化批次（org_gate 硬约束如实携带）",
    }


# ---------------------------------------------------------------------------
# 四、链接台账落盘（对应仓库 C03 的经络链接 JSON）
# ---------------------------------------------------------------------------

def build_ledger() -> Dict[str, Any]:
    """构建经络链接台账（确定性——不含墙钟时间，日期用声明值）。"""
    table = build_meridian_table()
    summary = meridian_summary(table)
    return {
        "project": "HoloAeon SEARCHNET-01 D03 MERIDIAN-LINK",
        "dim_id": "D03",
        "cang": "holoaeon-c03-meridian",
        "batch": "V62-MERIDIAN-LINK",
        "date": "2026-11-12",
        "schema": SCHEMA_VERSION,
        "source": "碳基三轮指令（建立经络链接/内核机制穷举信息补充/手工补充 17 条点名）"
                  "+ B 榜 10 条（V61 落盘 data/searchnet_d03_b.json，全员 unverified）",
        "fragments": 10, "mechanisms": len(KERNEL_MECHANISMS), "cells": len(table),
        "mechanism_axis": [{"id": m["id"], "layer": m["layer"], "name": m["name"],
                            "en": m["en"]} for m in KERNEL_MECHANISMS],
        "table": table,
        "summary": summary,
        "seal": SEAL,
    }


def write_ledger(path: Optional[str] = None) -> str:
    """台账落盘（默认 data/searchnet_d03_meridian.json——C03 对应仓链接台账）。"""
    if path is None:
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "data", DATA_OUT_NAME)
    ledger = build_ledger()
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(ledger, fh, ensure_ascii=False, indent=1)
    return path


# ---------------------------------------------------------------------------
# 五、总闸与 CLI
# ---------------------------------------------------------------------------

def check_all() -> Dict[str, Any]:
    """总闸三检查：机制轴完全匹配/碳基点名对账/穷举链接对账。"""
    return {"schema": SCHEMA_VERSION, "seal": SEAL,
            "registry": check_registry(),
            "named": check_named(),
            "linkage": check_linkage(),
            "pass": (check_registry()["pass"] and check_named()["pass"]
                     and check_linkage()["pass"])}


def _print_check(result: Dict[str, Any], title: str) -> None:
    ok = result.get("pass")
    print("[{}] {} {}".format("PASS" if ok else "FAIL", title,
                              "" if ok else "-> " + "; ".join(result.get("problems", [])[:4])))


def _main(argv: Optional[List[str]] = None) -> int:
    prog = argv[0] if argv else "meridian_link"
    args = list(argv[1:]) if argv else sys.argv[1:]
    if not args or args[0] not in ("check", "table", "summary", "ledger"):
        print("usage: {} check|table|summary|ledger [--out PATH]".format(prog))
        return 1
    cmd = args[0]
    out = None
    if "--out" in args:
        i = args.index("--out")
        if i + 1 >= len(args):
            print("--out 需要路径参数")
            return 1
        out = args[i + 1]
    if cmd == "check":
        res = check_all()
        _print_check(res["registry"], "registry 完全匹配（五源 import 对账）")
        _print_check(res["named"], "named 碳基点名 17 条对账")
        _print_check(res["linkage"], "linkage 穷举 250 格三态对账")
        return 0 if res["pass"] else 1
    if cmd == "table":
        table = build_meridian_table()
        for c in table:
            if c["state"] == "linked":
                ev = "; ".join("{}({})".format(k, s) for k, s in c["evidence"])
                print("{:<38} {:<4} {:<18} linked   {}".format(
                    c["repo"], c["mech"], c["mech_name"], ev))
        print("cells={} linked={} pending={} unlinked={}".format(
            len(table),
            sum(1 for c in table if c["state"] == "linked"),
            sum(1 for c in table if c["state"] == "pending-evidence"),
            sum(1 for c in table if c["state"] == "unlinked")))
        if out:
            p = write_ledger(out)
            print("ledger -> {}".format(p))
        return 0
    if cmd == "summary":
        s = meridian_summary()
        print("cang={} dim={} fragments={} mechanisms={} cells={} linked={}".format(
            s["cang"], s["dim"], s["fragments"], s["mechanisms"], s["cells"], s["linked_total"]))
        for mid, info in s["by_mechanism"].items():
            if info["linked"]:
                print("  {:<4} {:<14} linked={}".format(mid, info["name"], info["linked"]))
        print("gm_gate pass={} wait={}".format(s["gm_gate"]["pass"], len(s["gm_gate"]["wait_items"])))
        print("hard_rule: {}".format(s["gm_gate"]["hard_rule"]))
        return 0
    if cmd == "ledger":
        p = write_ledger(out)
        ledger = build_ledger()
        chk = check_linkage()
        print("ledger -> {} cells={} linkage_pass={}".format(p, ledger["cells"], chk["pass"]))
        return 0 if chk["pass"] else 1
    return 1


if __name__ == "__main__":
    raise SystemExit(_main(["meridian_link"] + sys.argv[1:]))
