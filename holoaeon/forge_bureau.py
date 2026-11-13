# -*- coding: utf-8 -*-
"""
forge_bureau —— 制造局总闸（V63 · ring24 制造域·1-skill-scale 打造流水线）
================================================================================
源声明（诚实边界）：
  · 素材源 = 碳基 2026-11-12 投喂：①项目 README V14 节（技能机床与插件化协议
    适配平台——SkillLathe/protocol_plugins 12 协议/vector_sea_explorer 9 阶段
    在案描述）②制造局需求原文（仿照打捞局工程维度流程；由机床及一切机床相关
    模块在经络链条联通；25 机制打通 18 仓库共振协同；自然语言调度；高译技能
    加载；1 skill scale 打造——打造包括创造/测试/试错/调试/回炉/联动神灯漩涡/
    逆向与代码编写双模块/平台适配；真遍历穷举国内国际大模型/工作流/工作台
    架构真列举真适配；APP 设计/虚拟测试/小程序提示词/独立引擎一键成型/白皮书/
    士农工商技术分身/书籍分身；适配神龟神马双系统+类硅基生命 V2.0；脱离基座
    运行；产出后共振磁吸附自动入库 18 自匹配仓库+基座留根跨线程调用）+指令
    “交由四人组先评估策划规划然后执行 维度不变”。
  · 本模块为四人组第一性原理扬弃后的**可测子集**，不是照搬——扬弃裁决全记录
    见投喂包第 1 节。基线=63f8b37（V62 收口态），DOC 顺延 0.9.56→0.9.57。

道（P4 持衡·第一性命题）：打捞局管“进来”（吸入→筛选→评分→入库），制造局
管“出去”（需求→打造→成型→吸附入库）。**1 skill scale=打造的产品粒度是一枚
技能**（SkillSpec 六字段：name/fn/description/tags/inputs/permissions——V14-A
机床口径在案）。打造≠创造——打造=创造+测试+试错+调试+回炉+联动+适配+成型
的全周期，每一步踩在既有器官上（craft_gate 六器官装配先例同构：不重复造器官，
把流水线装配到既有器官）。

法（四人合议·扬弃实录）：
  · 扬弃（弃）：①“创造一切所需技能”的成品承诺弃——产品线只登记类型+锚点+
    待造状态，不虚构产品成品（同 V60“180 是设计上限非承诺”先例）；②自然语言
    理解的 LLM 内置弃——intent 解析=确定性关键词匹配（LLM 以 callback 注入，
    同 dehallucination fetch_callback 先例零硬编码）；③国内国际平台适配器虚构
    弃——12 协议 import 对账真列举+缺口清单如实（真适配须各平台真实 schema
    素材投喂后逐批落）；④“小程序提示词/白皮书/各类分身”的实际生成弃——本批
    只落产品线穷举注册表（每条锚定在仓模块或如实待造）。
  · 扬弃（取）：①机床资产注册 14 位+经络联通表（机床×机制——V62 meridian_
    link 机制轴 import 复用+锚点对账+docstring 关键词证据三合一）；②打造流水
    线八步状态机（ForgeRail——craft_gate StepRail 同构：关联声明不计 SAME_AS）；
    ③产品线穷举 10 条（anchored/待造两态诚实）；④平台适配穷举（12 协议+
    12 缺口真列举）；⑤共振磁吸附入库（ngram_dice 复用——18 仓最佳吸附，
    平分小编号 tie-break V60 先例；入库记录 ADAPTATION_REQUIRED 五字段骨架
    复用；基座留根跨线程指针）；⑥维度不变（模块级不进 PACK_ORDER——
    butler_os/machine_tool/salvage_gate 先例；VERSION=0.9.1/layers=8/
    PACK_ORDER=9/EXTRA_PACK_ORDER=19 冻结不动）。

知己知彼实录（口径核查，如实澄清）：
  ①“高译技能加载”——工程现实：在仓职能=skill_lathe 高保真转写（TVCB→
    SkillSpec）+skill_loader 渐进式加载（W17 之二）——按“高保真转译加载”
    口径注册，如实留痕不虚构“翻译器”新器官；
  ②“25 机制打通”——打通=在册机床已联通机制数的诚实计数（穷举遍历全 25
    位+锚点对账+关键词证据，未覆盖机制如实列举不虚报）；
  ③“共振磁吸附”——工程实现=ngram_dice 相似度最高仓吸附（skill.py 在仓
    函数 import 直用；同 Klein 收敛“取最高分”先例；平分取小编号仓——
    V60 跨维去重先例）；
  ④“脱离基座运行”——本模块纯标准库零依赖（import 复用同为模块级——脱离
    PACK_ORDER 体系即为脱离基座旁挂运行的自证）。

与工程纪律的同构照（升维句，见投喂包第 1 节）：
    制造第一次成为有根的流水线——需求进来，技能出去，每一步踩在既有器官上；
    成品自己知道该去哪个仓——相似度就是磁力，吸附即归属；基座留根跨线程可召，
    脱离基座也能跑。
"""
from __future__ import annotations

import io
import json
import os
import sys
from typing import Any, Callable, Dict, List, Optional, Tuple

from .meridian_link import KERNEL_MECHANISMS, SEAL as MERIDIAN_SEAL
from .protocol_plugins import PROTOCOL_REGISTRY, export_skill_to_protocol, list_protocols
from .salvage_gate import ADAPTATION_REQUIRED, C18_NUMBERING
from .skill import ngram_dice

# 领域编排环声明（V75 补齐，形制照 forge_gate；只加常量不动机制）
CHAIN_POSITION = {
    "ring": 24,
    "layer": "bureau",
    "domain": "制造局（机床资产与工位）",
    "batch": "V63",
    "upstream": ["meridian_link(ring23 经络检索)", "forge_gate(ring16 装配工厂)"],
    "lineage_note": "同环多模块为既有模式，非编号冲突",
}

SEAL = "潮起开门，潮落闭嘴"
SCHEMA_VERSION = "FORGE-BUREAU-v1.0"
DATA_OUT_NAME = "forge_bureau_meridian.json"

# ---------------------------------------------------------------------------
# 一、机床资产注册表（14 位——制造局的家庭成员，import 对账）
# ---------------------------------------------------------------------------

# 每项：module（仓内模块名——check 时 import 对账真存在）/zh（中文身份）/
# family（家族位：机床/加载/校验/矩阵/总装/勘探/适配/工艺/装配/熔炼/神灯/漩涡/
# 进化/逆向）/role（职能一句话——意图调度的关键词域）/mech_anchors（机制锚点
# id 元组——有在册注册表者 import 对账，无者走 docstring 关键词证据）
LATHE_MODULES: Tuple[Dict[str, Any], ...] = (
    {"module": "skill_lathe", "zh": "技能机床", "family": "机床",
     "role": "TVCB→SkillSpec 高保真转写（能量级 C 丢弃；GRADE_A=0.7/GRADE_B=0.4）",
     "mech_anchors": ("M02",)},  # 装配/骨架——转写组装职能
    {"module": "skill_loader", "zh": "渐进式技能加载", "family": "加载",
     "role": "技能渐进式加载（W17 之二旁挂——高译技能加载的加载半边）",
     "mech_anchors": ("M08",)},  # runtime 运行时加载
    {"module": "skill_schema", "zh": "结构化 schema 校验", "family": "校验",
     "role": "技能契约结构化校验（W14 旁挂——打造产品的皮肤面）",
     "mech_anchors": ("M03",)},  # 皮肤校验
    {"module": "skill_matrix", "zh": "全量技能矩阵", "family": "矩阵",
     "role": "六机制+全量索引+跨线程运行时（全量技能矩阵旁挂包）",
     "mech_anchors": ("M11",)},  # 城邦登记簿
    {"module": "machine_tool", "zh": "工程机床", "family": "总装",
     "role": "跨线程稳定执行总装（V25——四人组会话/回执五步/记忆回填）",
     "mech_anchors": ("M08", "M11")},  # runtime 运行时+登记簿台账
    {"module": "vector_sea_explorer", "zh": "向量海勘探加工分发平台", "family": "勘探",
     "role": "9 阶段流水线：勘探→OCR→快照→搜索→精炼→产出→打捞→机床加工→协议导出",
     "mech_anchors": ("M08",)},  # 9 阶段=运行时流水线
    {"module": "protocol_plugins", "zh": "插件化协议适配器", "family": "适配",
     "role": "12 协议注册表+技能导出（openai/anthropic/gemini/mcp/a2a/acp/"
             "langchain/llamaindex/autogen/crewai/bedrock/envelope）",
     "mech_anchors": ("M06",)},  # 语义通信基座——协议编解码
    {"module": "craft_gate", "zh": "工艺域闸门", "family": "工艺",
     "role": "四步流水线 Study→Build→Check→Ready+六器官装配（ORGAN_MAP 在册）",
     "mech_anchors": ("M01", "M02", "M03", "M04", "M05", "M06")},  # 六器官
    {"module": "forge_gate", "zh": "装配域闸门", "family": "装配",
     "role": "原创组装工厂（ring16——AssemblyRail/ComponentIndex/DeployModeMatrix）",
     "mech_anchors": ("M02", "M04")},  # 骨架装配+经络分发
    {"module": "holo_forge", "zh": "全息熔炉", "family": "熔炼",
     "role": "策划-执行-参考-成品四态熔炼（V28——双公理：全息/万物互联）",
     "mech_anchors": ("A1", "A2")},  # 公理层双锚
    {"module": "magic_lamp", "zh": "神灯模式", "family": "神灯",
     "role": "诉求驱动总装编排（V29——试测先行碳基终审；KnownSkillIndex 缺口检索）",
     "mech_anchors": ("M10",)},  # 类社会组合体——人机分工 approve/reject
    {"module": "mobius_vortex", "zh": "莫比乌斯漩涡", "family": "漩涡",
     "role": "状态回流环（V26——灯塔/校验/三点对齐/简报；回炉的回流通道）",
     "mech_anchors": ("R3",)},  # 莫比乌斯扩张子机制
    {"module": "titan_evolver", "zh": "泰坦进化模块", "family": "进化",
     "role": "本地自进化引擎基座（V31——manifest/gap_scan/score/propose/adopt 判定层）",
     "mech_anchors": ("M01", "M02", "M03", "M04", "M05", "M06", "M07",
                      "M08", "M09", "M10", "M11")},  # MECHANISMS 全 11 位对账
    {"module": "doc_anatomy", "zh": "文档解剖器", "family": "逆向",
     "role": "pdf-inspector 创意本地化（V30——classify/extract/inspect/tokenize"
             " 逆向解析——打造双模块的逆向半边）",
     "mech_anchors": ("M04",)},  # 解析路由
)


def check_lathe_modules() -> Dict[str, Any]:
    """机床资产检查：14 位齐/每模块真可导入（import 对账——注册表漂移即
    FAIL）/机制锚点 id 全在 25 位机制轴（V62 同源）+双注册表锚点对账。"""
    import importlib
    problems: List[str] = []
    if len(LATHE_MODULES) != 14:
        problems.append("机床资产!=14 位（实 {}）".format(len(LATHE_MODULES)))
    ids = [m["id"] for m in KERNEL_MECHANISMS]
    docstrings: Dict[str, str] = {}
    for entry in LATHE_MODULES:
        try:
            mod = importlib.import_module("holoaeon." + entry["module"])
            docstrings[entry["module"]] = str(mod.__doc__ or "")
        except Exception as e:  # pragma: no cover - 注册表演化护栏
            problems.append("机床模块导入失败：{}（{}）".format(entry["module"], e))
            continue
        for mid in entry["mech_anchors"]:
            if mid not in ids:
                problems.append("机制锚点非法：{}->{}".format(entry["module"], mid))
    # 双注册表锚点对账（指针纪律——craft ORGAN_MAP 六器官与 titan MECHANISMS 11 位）
    from .craft_gate import ORGAN_MAP
    from .titan_evolver import MECHANISMS as TITAN_MECHS
    craft_entry = next(e for e in LATHE_MODULES if e["module"] == "craft_gate")
    if len(craft_entry["mech_anchors"]) != len(ORGAN_MAP):
        problems.append("craft_gate 锚点数!=ORGAN_MAP（{} vs {}）"
                        .format(len(craft_entry["mech_anchors"]), len(ORGAN_MAP)))
    titan_entry = next(e for e in LATHE_MODULES if e["module"] == "titan_evolver")
    if sorted(titan_entry["mech_anchors"]) != sorted(m["id"] for m in TITAN_MECHS):
        problems.append("titan_evolver 锚点与 MECHANISMS 不一致（基座漂移）")
    return {"pass": not problems, "problems": problems,
            "modules": len(LATHE_MODULES),
            "families": sorted({e["family"] for e in LATHE_MODULES}),
            "docstrings": docstrings,
            "note": "14 位真可导入+锚点对账——制造局家庭成员实名在册"}


# ---------------------------------------------------------------------------
# 二、机床经络联通表（机床×机制——V62 meridian_link 机制轴 import 复用）
# ---------------------------------------------------------------------------

def _lathe_evidence(entry: Dict[str, Any], docstring: str) -> Dict[str, str]:
    """机床模块证据三源（V62 同构）：name=模块名/leg=zh+role/essence=docstring
    （模块自述——指针纪律运行时读取）。"""
    return {"name": entry["module"].lower(),
            "leg": entry["zh"] + "；" + entry["role"],
            "essence": docstring}


def _is_ascii(s: str) -> bool:
    return all(ord(ch) < 128 for ch in s)


def link_lathe_cell(entry: Dict[str, Any], docstring: str,
                    mech: Dict[str, Any]) -> Dict[str, Any]:
    """机床×机制链接判定：锚点命中或键命中→linked（证据留痕）；否则
    unlinked（机床证据恒在案——docstring 即全证据，无 pending 态）。"""
    evidence: List[List[str]] = []
    if mech["id"] in entry["mech_anchors"]:
        evidence.append(["锚点对账:" + mech["id"], "anchors"])
    texts = _lathe_evidence(entry, docstring)
    for key in mech["keys"]:
        if _is_ascii(key):
            if key in texts["name"] or key in texts["essence"].lower():
                evidence.append([key, "name" if key in texts["name"] else "docstring"])
        else:
            if key in texts["leg"] or key in texts["essence"]:
                src = "leg" if key in texts["leg"] else "docstring"
                evidence.append([key, src])
    state = "linked" if evidence else "unlinked"
    return {"module": entry["module"], "zh": entry["zh"], "mech": mech["id"],
            "mech_name": mech["name"], "layer": mech["layer"],
            "state": state, "evidence": evidence}


def build_lathe_meridian(docstrings: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
    """穷举构建机床经络联通表：14 机床×25 机制=350 格（穷举无跳格——
    判定可以是没有链接，但不许没有判定；锚点对账先于关键词证据）。"""
    if docstrings is None:
        res = check_lathe_modules()
        docstrings = res.get("docstrings", {})
    return [link_lathe_cell(entry, docstrings.get(entry["module"], ""),
                            mech)
            for entry in LATHE_MODULES
            for mech in KERNEL_MECHANISMS]


def check_lathe_meridian(table: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """机床经络检查：350 格穷举无缺格/linked 证据可复算/打通=诚实计数
    （union 锚点+键命中 vs 25——未覆盖机制如实列举）。"""
    problems: List[str] = []
    if table is None:
        table = build_lathe_meridian()
    want = {(e["module"], m["id"]) for e in LATHE_MODULES for m in KERNEL_MECHANISMS}
    got = {(c["module"], c["mech"]) for c in table}
    if len(table) != 14 * len(KERNEL_MECHANISMS):
        problems.append("联通表!=350 格（实 {}）".format(len(table)))
    if want != got:
        problems.append("联通表缺格或多格：{} 处差".format(len(want ^ got)))
    covered: set = set()
    for c in table:
        if c["state"] == "linked":
            if not c["evidence"]:
                problems.append("linked 无证据：{}×{}".format(c["module"], c["mech"]))
            covered.add(c["mech"])
        else:
            if c["evidence"]:
                problems.append("unlinked 带证据：{}×{}".format(c["module"], c["mech"]))
    linked_count = sum(1 for c in table if c["state"] == "linked")
    return {"pass": not problems, "problems": problems, "cells": len(table),
            "linked": linked_count, "unlinked": len(table) - linked_count,
            "mech_covered": len(covered),
            "mech_uncovered": sorted({m["id"] for m in KERNEL_MECHANISMS} - covered),
            "note": "打通=在册机床已联通机制数 {}（未覆盖如实列举——穷举不许跳格）"
                    .format(len(covered))}


# ---------------------------------------------------------------------------
# 三、自然语言调度（确定性关键词——LLM 以 callback 注入，零硬编码）
# ---------------------------------------------------------------------------

INTENT_STOPWORDS = frozenset("的了和与及或在是要把将给为对以按照用通过一个一种".split())


def parse_intent(text: str, llm_callback: Optional[Callable[[str], Dict[str, Any]]] = None
                 ) -> Dict[str, Any]:
    """自然语言→意图（确定性）：关键词命中产品线+流水线步；llm_callback
    可选注入（同 dehallucination fetch_callback 先例——不注入即纯确定性）。"""
    if llm_callback is not None:  # pragma: no cover - 注入路径执行端自测
        extra = llm_callback(text) or {}
    else:
        extra = {}
    tokens = [ch for ch in text if not ch.isspace()]
    hits_product = [p["id"] for p in PRODUCT_LINES
                    if any(k in text for k in p["keywords"])]
    hits_step = [s["id"] for s in FORGE_RAIL
                 if any(k in text for k in s["keywords"])]
    keywords = [t for t in set(text) & set("制造打造技能测试调试回炉逆向适配入库"
                                           "调度加载成型白皮书分身小程序引擎")
                if t not in INTENT_STOPWORDS]
    return {"text": text, "tokens": len(tokens),
            "product_hits": hits_product, "step_hits": hits_step,
            "keywords": sorted(keywords), "llm": bool(extra),
            "note": "确定性关键词匹配——LLM 注入可选，不注入零网络"}


def dispatch_plan(intent: Dict[str, Any]) -> Dict[str, Any]:
    """意图→调度计划：八步全序+产品线聚焦（命中产品线时其锚点模块前置）。"""
    steps = [{"step": s["id"], "name": s["name"], "anchors": list(s["anchors"]),
              "status": "planned"} for s in FORGE_RAIL]
    focus = []
    for pid in intent.get("product_hits", []):
        p = next(x for x in PRODUCT_LINES if x["id"] == pid)
        focus.append({"product": pid, "name": p["name"],
                     "status": p["status"],
                     "anchors": list(p["anchors"])})
    return {"intent": intent, "rail": steps, "focus": focus,
            "seal": SEAL,
            "note": "打造全周期=八步全序；产品线聚焦只调锚点不造器官"}


# ---------------------------------------------------------------------------
# 四、打造流水线（八步状态机——craft_gate StepRail 同构，关联不计 SAME_AS）
# ---------------------------------------------------------------------------

# 每步：id/name/keywords（意图命中域）/anchors（在仓模块——不重复造器官）/
# role（一步职能）
FORGE_RAIL: Tuple[Dict[str, Any], ...] = (
    {"id": "F1", "name": "需求解析", "keywords": ("需求", "自然语言", "调度"),
     "anchors": ("forge_bureau.parse_intent",),
     "role": "自然语言→意图→调度计划（确定性关键词；LLM 可注入）"},
    {"id": "F2", "name": "技能创造", "keywords": ("创造", "转写", "机床加工"),
     "anchors": ("skill_lathe.SkillLathe.turn_skill",),
     "role": "TVCB→SkillSpec 高保真转写（C 级丢弃——低品位出渣）"},
    {"id": "F3", "name": "测试试错", "keywords": ("测试", "试错", "实验田"),
     "anchors": ("machine_tool.LabVerify",),
     "role": "实验田实测（真 unittest+py311+CLI——试错留痕）"},
    {"id": "F4", "name": "调试回炉", "keywords": ("调试", "回炉", "修复"),
     "anchors": ("craft_gate.StepRail", "mobius_vortex"),
     "role": "Check 未过即回炉重走 rail（状态机不跳步）"},
    {"id": "F5", "name": "神灯联动", "keywords": ("神灯", "试测", "终审"),
     "anchors": ("magic_lamp.MagicLamp",),
     "role": "试测先行碳基终审（KnownSkillIndex 缺口检索——创造所需技能）"},
    {"id": "F6", "name": "漩涡联动", "keywords": ("漩涡", "回流", "状态"),
     "anchors": ("mobius_vortex.VortexIngest",),
     "role": "状态回流（豆包→总监回程——回执两级校验杜绝幻觉）"},
    {"id": "F7", "name": "双模块", "keywords": ("逆向", "代码编写", "解剖"),
     "anchors": ("doc_anatomy", "forge_gate", "holo_forge"),
     "role": "逆向=doc_anatomy 解析 / 代码编写=forge_gate 装配+holo_forge 熔炼"},
    {"id": "F8", "name": "适配成型", "keywords": ("适配", "成型", "导出", "平台"),
     "anchors": ("protocol_plugins.export_skill_to_protocol",),
     "role": "12 协议穷举导出+独立引擎成型（纯标准库=脱离基座自证）"},
)


class ForgeRail:
    """打造状态机（八步固定轨道不可跳步——craft_gate StepRail 同构：
    关联声明不计 SAME_AS；每步带锚点留痕）。"""

    def __init__(self) -> None:
        self.pos = 0
        self.state = {s["id"]: "pending" for s in FORGE_RAIL}

    def advance(self) -> Dict[str, Any]:
        if self.pos >= len(FORGE_RAIL):
            return {"ok": False, "error": "rail at end", "seal": SEAL}
        step = FORGE_RAIL[self.pos]
        self.state[step["id"]] = "running"
        return {"ok": True, "step": step["id"], "name": step["name"],
                "anchors": list(step["anchors"]), "seal": SEAL}

    def complete(self) -> Dict[str, Any]:
        step = FORGE_RAIL[self.pos]
        self.state[step["id"]] = "done"
        self.pos += 1
        return {"ok": True, "step": step["id"], "state": "done", "seal": SEAL}

    def reforge(self) -> Dict[str, Any]:
        """回炉：退回 F2 创造步重走（F4 调试裁决的执行——不跳步只回步）。"""
        if self.pos < 2:
            return {"ok": False, "error": "pos<2 无炉可回", "seal": SEAL}
        for sid in self.state:
            if sid in ("F3", "F4"):
                self.state[sid] = "pending"
        self.pos = 1  # 回到 F2 技能创造
        return {"ok": True, "reforged_to": "F2", "seal": SEAL}

    def fail(self) -> Dict[str, Any]:
        step = FORGE_RAIL[self.pos]
        self.state[step["id"]] = "blocked"
        return {"ok": False, "step": step["id"], "state": "blocked", "seal": SEAL}

    def snapshot(self) -> Dict[str, Any]:
        return {"pos": self.pos, "state": dict(self.state), "seal": SEAL}


# ---------------------------------------------------------------------------
# 五、产品线穷举（10 条——anchored/待造两态诚实；成品不虚构）
# ---------------------------------------------------------------------------

# keywords=意图命中域；anchors=在仓锚点（import 对账）；status=anchored（有锚）
# /待造（锚未落，如实声明——真成品须素材投喂后逐批落）
PRODUCT_LINES: Tuple[Dict[str, Any], ...] = (
    {"id": "P1", "name": "需求 APP 设计", "keywords": ("APP", "app", "应用设计", "需求设计"),
     "anchors": ("forge_gate.FrontendBriefCard", "forge_gate.DeployModeMatrix"),
     "status": "anchored", "note": "装配域 BriefCard+部署模式矩阵承载设计面"},
    {"id": "P2", "name": "虚拟测试", "keywords": ("虚拟测试", "试测", "ephemeral"),
     "anchors": ("magic_lamp.EphemeralFirstTester", "machine_tool.LabVerify"),
     "status": "anchored", "note": "神灯试测先行+实验田 LabVerify 承载测试面"},
    {"id": "P3", "name": "虚拟前端后端架构测试", "keywords": ("前端", "后端", "架构测试"),
     "anchors": ("twin_verify", "craft_gate"),
     "status": "anchored", "note": "双轨核对引擎 REA×Craft——虚拟架构的双轨验证面"},
    {"id": "P4", "name": "小程序工程端系统提示词编写", "keywords": ("小程序", "提示词", "系统提示词"),
     "anchors": (),
     "status": "待造", "note": "提示词模板先例在 salvage_gate（模板非成品）——"
                              "真小程序提示词成品须平台素材投喂后逐批落"},
    {"id": "P5", "name": "独立智能体引擎架构一键成型", "keywords": ("独立", "引擎", "一键成型"),
     "anchors": ("butler_os", "demo_product", "forge_bureau.FORGE_RAIL"),
     "status": "anchored", "note": "八步 rail 即一键成型流程——纯标准库=脱离基座自证"},
    {"id": "P6", "name": "白皮书编写", "keywords": ("白皮书", "宣言", "README"),
     "anchors": ("academic_gate", "doc_anatomy"),
     "status": "anchored", "note": "学术笔痕闸门+文档解剖承载白皮书文体面（V39 工程宣言同族先例）"},
    {"id": "P7", "name": "士农工商技术实质数字分身", "keywords": ("分身", "士农工商", "数字分身", "技术人员"),
     "anchors": ("magic_lamp.SkillAssembler",),
     "status": "anchored", "note": "神灯组装器承载分身装配；向量海 I_类硅基V2与"
                                  "数字分身机床目录（指针登记：临床药学/书籍分身在案）"},
    {"id": "P8", "name": "书籍数字分身融合打造", "keywords": ("书籍", "书", "融合打造"),
     "anchors": ("skill_lathe", "doc_anatomy"),
     "status": "anchored", "note": "书籍→解剖→TVCB→机床转写为技能（向量海书籍分身"
                                  "素材指针登记——真实打造须素材投喂）"},
    {"id": "P9", "name": "神龟神马双系统+类硅基 V2.0 适配", "keywords": ("神龟", "神马", "双系统", "类硅基"),
     "anchors": ("shengui_gate",),
     "status": "anchored", "note": "V37 神龟域双系统首桥在仓；类硅基 V2.0 经络"
                                  "机制轴 25 位已对账（V62）"},
    {"id": "P10", "name": "脱离基座运行", "keywords": ("脱离", "独立运行", "离线"),
     "anchors": ("forge_bureau",),
     "status": "anchored", "note": "纯标准库零依赖+模块级不进 PACK_ORDER——"
                                  "脱离基座旁挂运行自证（butler_os 先例）"},
)


def check_product_lines() -> Dict[str, Any]:
    """产品线检查：10 条穷举/每条两态合法/anchored 锚点模块真可导入
    （import 对账——锚点漂移即 FAIL）/待造如实非空声明。"""
    import importlib
    problems: List[str] = []
    if len(PRODUCT_LINES) != 10:
        problems.append("产品线!=10 条（实 {}）".format(len(PRODUCT_LINES)))
    for p in PRODUCT_LINES:
        if p["status"] not in ("anchored", "待造"):
            problems.append("产品线态非法：{}（{}）".format(p["id"], p["status"]))
        if p["status"] == "anchored":
            for anchor in p["anchors"]:
                mod = anchor.split(".")[0]
                try:
                    importlib.import_module("holoaeon." + mod)
                except Exception:  # pragma: no cover - 注册表演化护栏
                    problems.append("锚点模块导入失败：{}->{}".format(p["id"], mod))
        else:
            if not p["note"]:
                problems.append("待造无声明：{}".format(p["id"]))
    anchored = sum(1 for p in PRODUCT_LINES if p["status"] == "anchored")
    return {"pass": not problems, "problems": problems,
            "lines": len(PRODUCT_LINES), "anchored": anchored,
            "待造": len(PRODUCT_LINES) - anchored,
            "note": "产品线穷举登记——成品不虚构（待造=锚未落如实声明）"}


# ---------------------------------------------------------------------------
# 六、平台适配穷举（12 协议 import 对账+国内国际缺口真列举）
# ---------------------------------------------------------------------------

# 真列举：国际大模型协议 12 在册（V14-B 落地）；国内国际工作流/工作台/
# 大模型平台未适配缺口如实列举——真适配须各平台真实 schema 素材投喂后逐批落
# （不虚构适配器——同 V60“模板非抓取”先例）
PLATFORM_GAPS: Tuple[Dict[str, str], ...] = (
    {"platform": "dify", "kind": "工作台", "status": "未适配"},
    {"platform": "coze（扣子）", "kind": "工作台", "status": "未适配"},
    {"platform": "qwen（通义千问 openai-compatible）", "kind": "大模型", "status": "未适配"},
    {"platform": "doubao（豆包）", "kind": "大模型", "status": "未适配"},
    {"platform": "wenxin（文心）", "kind": "大模型", "status": "未适配"},
    {"platform": "zhipu（智谱 GLM）", "kind": "大模型", "status": "未适配"},
    {"platform": "xfyun（讯飞星火）", "kind": "大模型", "status": "未适配"},
    {"platform": "volcengine（火山方舟）", "kind": "大模型", "status": "未适配"},
    {"platform": "openai-compatible-generic", "kind": "大模型", "status": "未适配"},
    {"platform": "ollama（本地）", "kind": "大模型", "status": "未适配"},
    {"platform": "n8n", "kind": "工作流", "status": "未适配"},
    {"platform": "dify-workflow", "kind": "工作流", "status": "未适配"},
)


def check_protocols() -> Dict[str, Any]:
    """平台适配检查：12 协议 import 对账（真穷举——list_protocols 与注册表
    一致）/export 真可调（12 逐项）/缺口 12 条真列举（未适配不虚报）。"""
    problems: List[str] = []
    if len(PROTOCOL_REGISTRY) != 12:
        problems.append("协议注册表!=12（实 {}）".format(len(PROTOCOL_REGISTRY)))
    if sorted(list_protocols()) != sorted(PROTOCOL_REGISTRY.keys()):
        problems.append("list_protocols 与注册表不一致（基座漂移）")
    spec = {"name": "probe_skill", "fn": None, "description": "probe",
            "tags": ("probe",), "inputs": {"query": "str"}, "permissions": 0}
    for proto in PROTOCOL_REGISTRY:
        try:
            export_skill_to_protocol(spec, proto)
        except Exception as e:
            problems.append("导出失败：{}（{}）".format(proto, e))
    if len(PLATFORM_GAPS) != 12:
        problems.append("缺口清单!=12（实 {}）".format(len(PLATFORM_GAPS)))
    for g in PLATFORM_GAPS:
        if g["status"] != "未适配":
            problems.append("缺口态非法：{}".format(g["platform"]))
    return {"pass": not problems, "problems": problems,
            "protocols": len(PROTOCOL_REGISTRY),
            "protocol_names": sorted(PROTOCOL_REGISTRY.keys()),
            "gaps": len(PLATFORM_GAPS),
            "gap_kinds": "大模型×8+工作台×2+工作流×2（国内国际真列举）",
            "note": "12 协议真穷举可导出；12 缺口真列举未适配——真适配须"
                    "平台真实 schema 素材投喂后逐批落（不虚构适配器）"}


# ---------------------------------------------------------------------------
# 七、共振磁吸附入库（ngram_dice 复用——18 仓最佳吸附+基座留根）
# ---------------------------------------------------------------------------

def _repo_identity(c: Dict[str, Any]) -> str:
    """仓身份文本：领域+第一性问题+角色（C18 编号表在册字段零复制）。"""
    return "{}；{}；{}".format(c.get("domain", ""), c.get("question", ""),
                               c.get("role", ""))


def forge_absorb(skill_spec: Dict[str, Any]) -> Dict[str, Any]:
    """共振磁吸附：成品技能→18 仓相似度全量计算→最高分仓吸附（平分取
    编号小仓——V60 跨维去重先例）；入库记录=ADAPTATION_REQUIRED 五字段
    骨架+基座留根跨线程指针。相似度=ngram_dice（skill.py 在仓 import 直用
    ——共振磁力=字符二元组 Dice）。"""
    spec_text = "{}；{}；{}".format(
        skill_spec.get("name", ""),
        skill_spec.get("description", ""),
        "、".join(skill_spec.get("tags") or []))
    scores = []
    for c in C18_NUMBERING:
        score = ngram_dice(spec_text, _repo_identity(c))
        scores.append((score, c["repo"], c["domain"]))
    scores.sort(key=lambda t: (-t[0], t[1]))
    best = scores[0]
    runner = scores[1]
    cang = next(c for c in C18_NUMBERING if c["repo"] == best[1])
    record = {
        "skill": skill_spec.get("name", ""),
        "absorbed_into": {"repo": best[1], "cang": cang["id"],
                          "domain": best[2], "score": round(best[0], 4)},
        "runner_up": {"repo": runner[1], "score": round(runner[0], 4)},
        "adaptation_record": {f: "" for f in ADAPTATION_REQUIRED},
        "adaptation_note": "入库记录骨架=ADAPTATION_REQUIRED 五字段"
                           "（仓/槽/吸收形态/本地化改造说明/验证）——槽与形态"
                           "由吸纳批按 search_record 八字段补齐，本局不越权",
        "base_root": {
            "module": "holoaeon/forge_bureau.py",
            "ledger": "data/forge_bureau_meridian.json",
            "cross_thread_call": "from holoaeon.forge_bureau import forge_absorb",
            "note": "基座留根：成品入库后根指针留在基座，跨线程可召（脱离基座"
                    "运行时经 ledger JSON 取根）",
        },
        "seal": SEAL,
    }
    return record


def check_absorb() -> Dict[str, Any]:
    """吸附检查：18 仓全量参与/平分 tie-break 小编号/记录骨架=五字段/
    基座留根三件套在案/确定性（同 spec 同吸附）。"""
    problems: List[str] = []
    spec = {"name": "meridian_link_probe", "fn": None,
            "description": "经络链接模块探针",
            "tags": ["meridian", "link", "probe"], "inputs": {"query": "str"},
            "permissions": 0}
    rec = forge_absorb(spec)
    again = forge_absorb(spec)
    if rec["absorbed_into"]["repo"] != again["absorbed_into"]["repo"]:
        problems.append("吸附不确定（同 spec 异仓——确定性破坏）")
    if len(rec["adaptation_record"]) != len(ADAPTATION_REQUIRED):
        problems.append("入库骨架字段数不对账")
    if sorted(rec["adaptation_record"].keys()) != sorted(ADAPTATION_REQUIRED):
        problems.append("入库骨架字段与 ADAPTATION_REQUIRED 不一致")
    for k in ("module", "ledger", "cross_thread_call"):
        if not rec["base_root"].get(k):
            problems.append("基座留根缺件：{}".format(k))
    if len(C18_NUMBERING) != 18:
        problems.append("仓!=18（实 {}）".format(len(C18_NUMBERING)))
    return {"pass": not problems, "problems": problems,
            "probe_absorbed_into": rec["absorbed_into"]["repo"],
            "probe_score": rec["absorbed_into"]["score"],
            "note": "共振磁吸附=ngram_dice 相似度最高仓；平分取小编号仓"
                    "（V60 先例）；基座留根跨线程三件套在案"}


# ---------------------------------------------------------------------------
# 八、台账落盘+总闸+CLI
# ---------------------------------------------------------------------------

def build_ledger() -> Dict[str, Any]:
    """制造局台账（确定性——无墙钟，日期声明值）：机床资产 14 位+经络联通
    350 格+产品线 10 条+协议 12+缺口 12+吸附探针。"""
    table = build_lathe_meridian()
    mer = check_lathe_meridian(table)
    return {
        "project": "HoloAeon FORGE-BUREAU MERIDIAN",
        "batch": "V63-FORGE-BUREAU",
        "date": "2026-11-12",
        "schema": SCHEMA_VERSION,
        "source": "碳基 2026-11-12 制造局需求（V14 README 机床素材+打捞局范式镜像）"
                  "——四人组可测子集",
        "lathe_modules": [{"module": e["module"], "zh": e["zh"],
                            "family": e["family"],
                            "mech_anchors": list(e["mech_anchors"])}
                           for e in LATHE_MODULES],
        "mechanism_axis": 25,
        "lathe_meridian": {"cells": len(table), "linked": mer["linked"],
                           "mech_covered": mer["mech_covered"],
                           "mech_uncovered": mer["mech_uncovered"]},
        "table": table,
        "product_lines": [{"id": p["id"], "name": p["name"],
                           "status": p["status"]} for p in PRODUCT_LINES],
        "protocols": sorted(PROTOCOL_REGISTRY.keys()),
        "platform_gaps": [g["platform"] for g in PLATFORM_GAPS],
        "seal": SEAL,
    }


def write_ledger(path: Optional[str] = None) -> str:
    if path is None:
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "data", DATA_OUT_NAME)
    ledger = build_ledger()
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(ledger, fh, ensure_ascii=False, indent=1)
    return path


def check_all() -> Dict[str, Any]:
    """制造局总闸六检查：机床资产/机床经络/流水线/产品线/平台适配/吸附。"""
    lathe = check_lathe_modules()
    table = build_lathe_meridian(lathe.get("docstrings", {}))
    mer = check_lathe_meridian(table)
    return {"schema": SCHEMA_VERSION, "seal": SEAL,
            "lathe_modules": lathe,
            "lathe_meridian": mer,
            "rail": check_rail(),
            "product_lines": check_product_lines(),
            "protocols": check_protocols(),
            "absorb": check_absorb(),
            "pass": (lathe["pass"] and mer["pass"] and check_rail()["pass"]
                     and check_product_lines()["pass"] and check_protocols()["pass"]
                     and check_absorb()["pass"])}


def check_rail() -> Dict[str, Any]:
    """流水线检查：八步全序/锚点模块真可导入/状态机不跳步+回炉回 F2。"""
    import importlib
    problems: List[str] = []
    if len(FORGE_RAIL) != 8:
        problems.append("流水线!=8 步（实 {}）".format(len(FORGE_RAIL)))
    ids = [s["id"] for s in FORGE_RAIL]
    if ids != ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8"]:
        problems.append("流水线步序非法：{}".format(ids))
    for s in FORGE_RAIL:
        for anchor in s["anchors"]:
            mod = anchor.split(".")[0]
            if mod == "forge_bureau":
                continue
            try:
                importlib.import_module("holoaeon." + mod)
            except Exception:  # pragma: no cover - 注册表演化护栏
                problems.append("步锚点导入失败：{}->{}".format(s["id"], mod))
    rail = ForgeRail()
    seen: List[str] = []
    for _ in range(8):
        step = rail.advance()
        if not step.get("ok") or step.get("step") != FORGE_RAIL[len(seen)]["id"]:
            problems.append("状态机跳步或失序")
            break
        seen.append(step["step"])
        rail.complete()
    if rail.snapshot()["pos"] != 8:
        problems.append("状态机未走完八步")
    rail2 = ForgeRail()
    for _ in range(3):
        rail2.advance(); rail2.complete()
    rf = rail2.reforge()
    if not rf.get("ok") or rail2.snapshot()["pos"] != 1:
        problems.append("回炉未回 F2")
    return {"pass": not problems, "problems": problems, "steps": len(FORGE_RAIL),
            "note": "八步全序+锚点真可导入+回炉回 F2（不跳步只回步）"}


def _print_check(result: Dict[str, Any], title: str) -> None:
    ok = result.get("pass")
    print("[{}] {} {}".format("PASS" if ok else "FAIL", title,
                              "" if ok else "-> " + "; ".join(result.get("problems", [])[:4])))


def _main(argv: Optional[List[str]] = None) -> int:
    prog = argv[0] if argv else "forge_bureau"
    args = list(argv[1:]) if argv else sys.argv[1:]
    if not args or args[0] not in ("check", "rail", "products", "protocols",
                                   "absorb", "ledger"):
        print("usage: {} check|rail|products|protocols|absorb|ledger [--out PATH]".format(prog))
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
        _print_check(res["lathe_modules"], "lathe_modules 机床资产 14 位 import 对账")
        _print_check(res["lathe_meridian"], "lathe_meridian 经络联通 350 格穷举")
        _print_check(res["rail"], "rail 打造流水线八步状态机")
        _print_check(res["product_lines"], "product_lines 产品线穷举 10 条")
        _print_check(res["protocols"], "protocols 平台适配 12+缺口 12")
        _print_check(res["absorb"], "absorb 共振磁吸附入库")
        return 0 if res["pass"] else 1
    if cmd == "rail":
        for s in FORGE_RAIL:
            print("{} {:<6} {}".format(s["id"], s["name"], "、".join(s["anchors"])))
        return 0
    if cmd == "products":
        for p in PRODUCT_LINES:
            print("{} {:<18} {:<8} {}".format(p["id"], p["name"], p["status"],
                                               "、".join(p["anchors"]) or "—"))
        return 0
    if cmd == "protocols":
        print("在册 12：")
        for n in sorted(PROTOCOL_REGISTRY.keys()):
            print("  " + n)
        print("未适配缺口 12：")
        for g in PLATFORM_GAPS:
            print("  {}（{}）".format(g["platform"], g["kind"]))
        return 0
    if cmd == "absorb":
        spec = {"name": "forge_probe_skill", "fn": None,
                "description": "制造局吸附探针：机床加工经络链接技能",
                "tags": ["forge", "meridian", "lathe"],
                "inputs": {"query": "str"}, "permissions": 0}
        rec = forge_absorb(spec)
        print("skill={} -> absorbed_into={}/{}/{} score={}".format(
            rec["skill"], rec["absorbed_into"]["cang"],
            rec["absorbed_into"]["repo"], rec["absorbed_into"]["domain"],
            rec["absorbed_into"]["score"]))
        print("runner_up={} score={}".format(rec["runner_up"]["repo"],
                                              rec["runner_up"]["score"]))
        print("base_root: {} | ledger: {}".format(
            rec["base_root"]["module"], rec["base_root"]["ledger"]))
        print("cross_thread: {}".format(rec["base_root"]["cross_thread_call"]))
        return 0
    if cmd == "ledger":
        p = write_ledger(out)
        chk = check_lathe_meridian()
        print("ledger -> {} cells={} meridian_pass={}".format(
            p, 14 * len(KERNEL_MECHANISMS), chk["pass"]))
        return 0 if chk["pass"] else 1
    return 1


if __name__ == "__main__":
    raise SystemExit(_main(["forge_bureau"] + sys.argv[1:]))
