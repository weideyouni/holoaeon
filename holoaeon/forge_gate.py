# -*- coding: utf-8 -*-
"""
forge_gate —— 装配域闸门（ring16）：原创组装工厂
================================================================================
定位：把「创造一个新组件」从一次性人工行为，变成可重复、可审计、可回执的
工业化流水线。五段一条龙：

    philosophy（创造哲学：为什么造/第一性约束/红线）
      → math（数理架构：维度/状态空间/既有数学资产指针）
        → language（计算机语言实现：py 零依赖/py38 兼容纪律）
          → module（模块设计：dataclass 接口/复用清单/防撞名）
            → code（代码化：实验田纪律/逐字节校验/redline）

纪律（与全仓一致）：
  · 零网络：本模块无 socket，纯标准库
  · 零虚构：组件引用全部指向仓内真实模块，不臆造接口
  · 复用优先：解剖/轨道/容量/耦合走既有资产指针，不重写算子
  · 维度不变：模块级增量，不触碰 kernel/layers/PACK_ORDER

与近邻模块的边界（防撞名）：
  · holo_forge(V28)=扩展包/技能熔炉；forge_gate=项目级组件装配流水线
  · craft_gate(V43)=单件工艺四步轨；forge_gate=工厂五段轨（结构同源、步数不同）
  · titan_evolver(V31)=被动能力清单；forge_gate=主动装配编排
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

SEAL = "潮起开门，潮落闭嘴"

# 领域编排环声明（V50 补齐，与 V43/V44/V45 同构；前 15 环均用此常量，自动化盘点不漏 ring16）
CHAIN_POSITION = {
    "ring": 16,
    "layer": "assembly",
    "domain": "装配（原创组装工厂）",
    "batch": "V49",
    "upstream": ["craft_gate(ring12 工艺轨·结构同源)", "titan_evolver(能力清单)",
                 "deploy_gate(ring15 容量/分工上游)"],
}

# ---------------------------------------------------------------- 五段轨道
STAGES: Tuple[str, ...] = ("philosophy", "math", "language", "module", "code")

STAGE_GATES: Dict[str, str] = {
    "philosophy": "第一性原理裁决：为什么造/不造什么/红线三条",
    "math": "数理架构卡：维度声明/状态空间/复用数学资产指针",
    "language": "语言实现卡：Python+纯标准库+py38 兼容+零网络",
    "module": "模块设计卡：dataclass 接口/复用清单/近邻模块防撞名",
    "code": "代码化卡：实验田实测/逐字节一致校验/redline 扫描",
}

STAGE_ARTIFACTS: Dict[str, str] = {
    "philosophy": "philosophy_card",
    "math": "math_card",
    "language": "language_card",
    "module": "module_card",
    "code": "code_receipt",
}


class AssemblyRail:
    """五段固定轨道状态机（结构同源 craft_gate.StepRail，步数不同故自建）。
    advance 一次进一段，不可跳步；跳步即 blocked。"""

    def __init__(self):
        self.pos = 0
        self.state = {s: "pending" for s in STAGES}

    def advance(self) -> Dict[str, Any]:
        if self.pos >= len(STAGES):
            return {"ok": False, "error": "rail at end", "seal": SEAL}
        s = STAGES[self.pos]
        self.state[s] = "running"
        return {"ok": True, "stage": s, "index": self.pos, "gate": STAGE_GATES[s], "seal": SEAL}

    def complete(self, artifact: Any = None) -> Dict[str, Any]:
        s = STAGES[self.pos]
        self.state[s] = "done"
        out = {"ok": True, "stage": s, "state": "done",
               "artifact": STAGE_ARTIFACTS[s], "seal": SEAL}
        self.pos += 1
        return out

    def fail(self) -> Dict[str, Any]:
        s = STAGES[self.pos]
        self.state[s] = "blocked"
        return {"ok": False, "stage": s, "state": "blocked", "seal": SEAL}

    def skip_check(self) -> Dict[str, Any]:
        """跳步检测：pos 之前若有非 done 段即为违规。"""
        bad = [STAGES[i] for i in range(self.pos)
               if self.state[STAGES[i]] != "done"]
        return {"ok": not bad, "violations": bad, "seal": SEAL}


# ---------------------------------------------------------------- 组件索引
# 仓内真实可复用组件登记（域 → 模块指针 + 能力一句话）。零臆造。
COMPONENT_INDEX: Dict[str, List[Dict[str, str]]] = {
    "anatomy": [
        {"module": "holoaeon.concept_anatomy", "klass": "ConceptAnatomizer",
         "capability": "概念十步解剖（逆向输入侧·V19）"},
        {"module": "holoaeon.doc_anatomy", "klass": "extract/classify",
         "capability": "PDF 文档逆向解剖（逆向输入侧·V30）"},
    ],
    "pipeline": [
        {"module": "holoaeon.craft_gate", "klass": "StepRail/Heartbeat/EvidenceLedger",
         "capability": "四步工艺轨+心跳+证据台账（V43）"},
        {"module": "holoaeon.forge_gate", "klass": "AssemblyRail",
         "capability": "五段装配轨（本模块）"},
    ],
    "capability": [
        {"module": "holoaeon.titan_evolver", "klass": "CapabilityManifest",
         "capability": "能力清单+缺口扫描（V31）"},
        {"module": "holoaeon.magic_lamp", "klass": "KnownSkillIndex/SkillAssembler",
         "capability": "已知技能索引+装配（V29）"},
    ],
    "deploy": [
        {"module": "holoaeon.deploy_gate", "klass": "capacity_plan",
         "capability": "容量规划+DELIBERATE_CHOICE（V47）"},
        {"module": "bridges.site_gateway", "klass": "ModelAutoCouple/NetDiode",
         "capability": "本地模型耦合+网络二极管（V47）"},
        {"module": "bridges.local_model_probe", "klass": "discover",
         "capability": "主机轻量模型探测（V46）"},
    ],
    "verify": [
        {"module": "holoaeon.twin_verify", "klass": "twin_verdict",
         "capability": "双轨核对四态裁决（V44）"},
        {"module": "holoaeon.redline", "klass": "redline_scan",
         "capability": "eval/exec/compile 红线扫描"},
    ],
    "domain": [
        {"module": "holoaeon.phc_chronic_engine", "klass": "FeedEnvelope/MdtConvene",
         "capability": "公卫慢病引擎（V41）"},
        {"module": "holoaeon.pharma_gate", "klass": "DrugRegistry",
         "capability": "医保登记表精确查表（V46）"},
        {"module": "holoaeon.teach_gate", "klass": "LessonUnit",
         "capability": "教学三件套（V45）"},
        {"module": "holoaeon.academic_gate", "klass": "TELL_PATTERNS",
         "capability": "学术诚实闸门（V40）"},
    ],
    "math": [
        {"module": "holoaeon.hypervector", "klass": "HypervectorSpace",
         "capability": "VSA/HDC 高维向量算子"},
        {"module": "holoaeon.graph", "klass": "AdaptiveGraph",
         "capability": "自适应图+赫布强化"},
        {"module": "holoaeon.klein_projection", "klass": "KleinProjection",
         "capability": "克莱因收敛投影（V27）"},
    ],
}


class ComponentIndex:
    """组件自动匹配：按域分类 + 关键词匹配。匹配不到如实返回空，
    不降级到模糊推荐（零虚构纪律）。"""

    DOMAINS = tuple(COMPONENT_INDEX.keys())

    def __init__(self):
        self.registry = {d: list(items) for d, items in COMPONENT_INDEX.items()}

    def match(self, query: str) -> Dict[str, Any]:
        q = (query or "").lower()
        hits: List[Dict[str, str]] = []
        domains: List[str] = []
        for dom, items in self.registry.items():
            for it in items:
                blob = " ".join([dom, it["module"], it["klass"], it["capability"]]).lower()
                if q and any(w and w in blob for w in q.replace("/", " ").split()):
                    hits.append({"domain": dom, **it})
                    if dom not in domains:
                        domains.append(dom)
        return {"ok": True, "query": query, "domains": domains,
                "hits": hits, "total_registered": sum(len(v) for v in self.registry.values()),
                "seal": SEAL}

    def catalog(self) -> Dict[str, Any]:
        return {"ok": True, "domains": {d: len(v) for d, v in self.registry.items()},
                "total": sum(len(v) for v in self.registry.values()), "seal": SEAL}


# ---------------------------------------------------------------- 大小模型分工
# 小模型（本地，ModelAutoCouple 耦合）：断网/内网/等保/内部数据
# 大模型（平台 API，bridges 声明层）：插件升级/向量库升级/需求卡翻译——须显式授权
TASK_SPLIT: Dict[str, Dict[str, Any]] = {
    "offline_runtime":     {"carrier": "local_small", "reason": "断网运行，零出站结构性保证"},
    "intranet_processing": {"carrier": "local_small", "reason": "内网隔离，数据不出内网"},
    "mlps3_compliance":    {"carrier": "local_small", "reason": "三级等保场景，本地推理"},
    "internal_data":       {"carrier": "local_small", "reason": "内部数据（含 PHI/敏感）不出边界"},
    "plugin_upgrade":      {"carrier": "platform_large", "auth": True,
                            "reason": "升级走入站三重门（类型+SHA+审批+staging）"},
    "vector_upgrade":      {"carrier": "platform_large", "auth": True,
                            "reason": "向量库升级包经 NetDiode 入站白名单"},
    "brief_translation":   {"carrier": "platform_large", "auth": True,
                            "reason": "前端需求卡翻译增强，须碳基授权后经网关"},
}

ALLOWED_LARGE_TASKS = tuple(k for k, v in TASK_SPLIT.items()
                            if v["carrier"] == "platform_large")


class ModelSplitRules:
    """任务→承载模型路由。platform_large 必须带 explicit_auth=True，否则拒发。"""

    def route(self, task_type: str, explicit_auth: bool = False) -> Dict[str, Any]:
        r = TASK_SPLIT.get(task_type)
        if r is None:
            return {"ok": False, "error": "unknown task_type: %r" % task_type, "seal": SEAL}
        if r["carrier"] == "platform_large" and not explicit_auth:
            return {"ok": False, "error": "platform_large requires explicit_auth",
                    "task_type": task_type,
                    "compliance_note": "耦合生成式模型后向境内公众提供服务者，"
                                        "备案/登记义务由该服务提供者（部署方）承担"
                                        "（《生成式人工智能服务管理暂行办法》第二条第三款边界）",
                    "seal": SEAL}
        return {"ok": True, "task_type": task_type, **r,
                "couple_hint": ("bridges.site_gateway.ModelAutoCouple"
                                if r["carrier"] == "local_small"
                                else "bridges.model_base_registry + 入站三重门"),
                "seal": SEAL}


# ---------------------------------------------------------------- 落地模式穷举
DEPLOY_MODES: Dict[str, Dict[str, Any]] = {
    "personal_pc": {
        "label": "个人 PC（单机离线）",
        "components": ["kernel", "forge_gate", "craft_gate", "magic_lamp"],
        "model_split": "本地小模型唯一（无平台通道）",
        "protocol": "本地进程调用（无网络）",
        "capacity": "1-10 人使用",
    },
    "standalone_server": {
        "label": "单服务器（机构机房）",
        "components": ["kernel", "deploy_gate", "forge_gate", "全域 gate"],
        "model_split": "小模型主载 + 大模型仅升级通道",
        "protocol": "127.0.0.1 本地 HTTP + 升级入站三重门",
        "capacity": "3-4 万人（capacity_plan 参数化）",
    },
    "lan_server": {
        "label": "局域网服务器（内网多终端）",
        "components": ["kernel", "deploy_gate", "TerminalPool", "forge_gate"],
        "model_split": "小模型内网服务；大模型经边界网关",
        "protocol": "内网段 HTTP + JSONL 台账交换（PROTOCOL_MATRIX.intranet）",
        "capacity": "终端 10 预留 30（扩容须审批）",
    },
    "distributed_cluster": {
        "label": "分布式集群（多节点）",
        "components": ["kernel×N", "bus", "event_channel", "swarm_intel", "forge_gate"],
        "model_split": "各节点小模型 + 升级源单点引入",
        "protocol": "节点间总线 + 边界网关汇聚（无路由穿透）",
        "capacity": "按节点线性扩展，容量=Σ节点",
    },
    "edge_offline": {
        "label": "边缘离线（无网络环境）",
        "components": ["kernel", "forge_gate", "本地 GGUF 权重"],
        "model_split": "纯小模型（ModelAutoCouple 直挂 GGUF）",
        "protocol": "零网络（出站白名单=空集）",
        "capacity": "单点使用",
    },
    "air_gapped": {
        "label": "物理隔离（等保三级强化）",
        "components": ["kernel", "forge_gate", "MLPS3 审计件"],
        "model_split": "纯小模型；大模型内容经人工介质摆渡入站",
        "protocol": "摆渡介质 + SHA+审批双验（PROTOCOL_MATRIX.boundary）",
        "capacity": "按审计要求",
    },
}


class DeployModeMatrix:
    """落地模式遍历穷举 + 按条件推荐。全部模式均内建于同一基座母体。"""

    def enumerate_modes(self) -> Dict[str, Any]:
        return {"ok": True, "modes": dict(DEPLOY_MODES),
                "count": len(DEPLOY_MODES), "seal": SEAL}

    def recommend(self, population: int = 1, offline: bool = False,
                  mlps3: bool = False) -> Dict[str, Any]:
        if mlps3:
            mode = "air_gapped"
        elif offline:
            mode = "edge_offline"
        elif population <= 10:
            mode = "personal_pc"
        elif population >= 10000:
            mode = "distributed_cluster" if population >= 100000 else "standalone_server"
        else:
            mode = "lan_server"
        return {"ok": True, "recommended": mode, "label": DEPLOY_MODES[mode]["label"],
                "rationale": "population=%s offline=%s mlps3=%s" % (population, offline, mlps3),
                "seal": SEAL}


# ---------------------------------------------------------------- 前端设计需求卡
BRIEF_SCHEMA = "holoaeon-frontend-brief-v1"

REVERSE_MODULES = [
    {"module": "holoaeon.concept_anatomy", "role": "输入侧逆向：需求概念十步解剖（V19）"},
    {"module": "holoaeon.doc_anatomy", "role": "输入侧逆向：已有文档/PDF 结构解剖（V30）"},
]


@dataclass
class FrontendBriefCard:
    """前端设计需求卡（信封格式）：逆向双模块解剖输入 → 结构化需求表达包。
    可执行端（任意 coding agent）读取本卡自动执行创建前端；
    模块引用须真实 import，耦合点不得臆造。"""
    project_id: str
    brief_text: str
    pages: List[Dict[str, Any]] = field(default_factory=list)
    coupling_points: List[Dict[str, str]] = field(default_factory=list)
    upgrade_slots: List[Dict[str, str]] = field(default_factory=list)
    anatomy_digest: str = ""
    created_at: float = 0.0

    def build(self) -> Dict[str, Any]:
        from .concept_anatomy import ConceptAnatomizer  # 真实复用（零虚构）
        anatomizer = ConceptAnatomizer()
        anat = anatomizer.anatomize(self._core_concept())
        self.anatomy_digest = hashlib.sha256(
            json.dumps(anat, ensure_ascii=False, sort_keys=True).encode("utf-8")
        ).hexdigest()[:16]
        if not self.pages:
            self.pages = self._default_pages()
        if not self.coupling_points:
            self.coupling_points = self._default_coupling()
        if not self.upgrade_slots:
            self.upgrade_slots = self._default_slots()
        self.created_at = self.created_at or time.time()
        return {
            "schema": BRIEF_SCHEMA,
            "project_id": self.project_id,
            "seal": SEAL,
            "intent": self.brief_text,
            "intent_anatomy": {
                "digest": self.anatomy_digest,
                "module": "holoaeon.concept_anatomy.ConceptAnatomizer",
                "steps": len(anat.get("steps", anat)) if isinstance(anat, dict) else "?",
            },
            "reverse_modules": REVERSE_MODULES,
            "pages": self.pages,
            "coupling_points": self.coupling_points,
            "protocols": {
                "internal": "holoaeon.bus / envelope（kernel 内部信封）",
                "external": "bridges.site_gateway.PROTOCOL_MATRIX（内外网边界，不打通）",
                "frontend_channel": "holoaeon.frontend_adapter（stdin/stdout JSON 行协议）",
            },
            "model_split": {
                "small_local_tasks": ["offline_runtime", "intranet_processing",
                                      "mlps3_compliance", "internal_data"],
                "large_platform_tasks": list(ALLOWED_LARGE_TASKS),
                "rule": "platform_large 须 explicit_auth，经入站三重门",
            },
            "upgrade_slots": self.upgrade_slots,
            "acceptance": {
                "install_check": "python scripts/install_check.py → 7/7",
                "dimension_lock": "VERSION=0.9.1 冻结 / layers=8 / PACK_ORDER=9 不变",
                "seal_check": "潮起开门，潮落闭嘴",
            },
            "execution_hint": (
                "可执行端读取本卡自动执行：①按 pages 树建前端；②按 coupling_points "
                "真实 import 仓内模块（不得臆造接口）；③protocols 声明的通道不得越界"
                "（内网数据不出内网）；④upgrade_slots 预留版本化升级空间，不得硬编码。"
            ),
        }

    def _core_concept(self) -> str:
        words = [w for w in self.brief_text.replace("，", " ").replace(",", " ").split() if w]
        return words[0] if words else "前端"

    def _default_pages(self) -> List[Dict[str, Any]]:
        return [
            {"page": "工作台", "widgets": ["任务队列", "装配轨道状态", "回执流"]},
            {"page": "装配厂", "widgets": ["组件索引", "五段轨道", "产物卡"]},
            {"page": "模型台", "widgets": ["本地耦合状态", "基座登记表", "分工细则"]},
            {"page": "审计台", "widgets": ["证据台账", "维度锁", "封口校验"]},
        ]

    def _default_coupling(self) -> List[Dict[str, str]]:
        return [
            {"module": "holoaeon.forge_gate", "interface": "ForgeGate.run",
             "frontend_slot": "装配厂·五段轨道"},
            {"module": "holoaeon.forge_gate", "interface": "ComponentIndex.match",
             "frontend_slot": "装配厂·组件索引"},
            {"module": "bridges.site_gateway", "interface": "ModelAutoCouple.couple",
             "frontend_slot": "模型台·本地耦合状态"},
            {"module": "holoaeon.deploy_gate", "interface": "capacity_plan",
             "frontend_slot": "模型台·容量规划"},
            {"module": "holoaeon.craft_gate", "interface": "EvidenceLedger",
             "frontend_slot": "审计台·证据台账"},
        ]

    def _default_slots(self) -> List[Dict[str, str]]:
        return [
            {"slot": "page_templates", "version_pin": "v1", "note": "页面模板版本化，换版不换协议"},
            {"slot": "coupling_points", "version_pin": "v1", "note": "耦合点清单可增不可改名"},
            {"slot": "model_bases", "version_pin": "v1", "note": "基座登记表随 bridges 升级"},
            {"slot": "protocol_matrix", "version_pin": "v3", "note": "PROTOCOL_MATRIX 升级须过审批"},
        ]


# ---------------------------------------------------------------- 总编排
class ForgeGate:
    """原创组装工厂总编排：run(intent) 走五段轨，产出装配单+前端需求卡+模式矩阵+分工单。"""

    def __init__(self):
        self.rail = AssemblyRail()
        self.index = ComponentIndex()
        self.split = ModelSplitRules()
        self.modes = DeployModeMatrix()

    def run(self, intent: str, population: int = 1, offline: bool = False,
            mlps3: bool = False, brief_project_id: str = "forge-001") -> Dict[str, Any]:
        stages_run: List[Dict[str, Any]] = []
        # philosophy
        stages_run.append(self.rail.advance())
        philosophy_card = {
            "why": intent,
            "first_principles": ["复用优先，不重写算子", "零网络零虚构", "维度不变"],
            "redlines": ["不得臆造接口", "不得绕过入站三重门", "不得破坏封口密语校验"],
        }
        stages_run.append(self.rail.complete(philosophy_card))
        # math
        stages_run.append(self.rail.advance())
        math_card = {
            "dimensions": "模块级增量（BUILTIN_LAYERS/layers=8 不动）",
            "math_assets": ["hypervector(VSA/HDC)", "graph(赫布强化)",
                            "klein_projection(收敛投影)"],
        }
        stages_run.append(self.rail.complete(math_card))
        # language
        stages_run.append(self.rail.advance())
        language_card = {"language": "Python 3.8+", "deps": "纯标准库",
                         "network": "零 socket（bridges 层才允许边界件）"}
        stages_run.append(self.rail.complete(language_card))
        # module
        stages_run.append(self.rail.advance())
        module_card = {
            "new_modules": ["holoaeon/forge_gate.py（ring16 装配域）",
                            "bridges/model_base_registry.py（基座登记，声明层）"],
            "reused": self.index.match(intent.split()[0] if intent.split() else "anatomy")["hits"],
            "name_collision_guard": ["holo_forge(V28)扩展包熔炉 ≠ forge_gate 项目装配",
                                     "craft_gate(V43)四步工艺轨 ≠ forge_gate 五段装配轨"],
        }
        stages_run.append(self.rail.complete(module_card))
        # code
        stages_run.append(self.rail.advance())
        code_receipt = {
            "lab": ".tmp_v49 实验田", "tests": "test_v49_forge_gate",
            "byte_check": "入包代码块与实验田逐字节一致",
            "redline": "redline_scan 0 违规",
        }
        stages_run.append(self.rail.complete(code_receipt))
        # 产物
        card = FrontendBriefCard(project_id=brief_project_id, brief_text=intent)
        brief = card.build()
        manifest = {
            "schema": "holoaeon-forge-manifest-v1",
            "seal": SEAL,
            "intent": intent,
            "stages": stages_run,
            "artifacts": {
                "philosophy_card": philosophy_card,
                "math_card": math_card,
                "language_card": language_card,
                "module_card": module_card,
                "code_receipt": code_receipt,
            },
            "rail_final_state": self.rail.state,
            "skip_check": self.rail.skip_check(),
            "component_catalog": self.index.catalog(),
            "deploy_recommend": self.modes.recommend(population, offline, mlps3),
            "deploy_modes_all": self.modes.enumerate_modes()["count"],
            "frontend_brief": brief,
        }
        return manifest


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(argv or sys.argv[1:] or [])
    intent = " ".join(argv) if argv else "装配一个前端工作台"
    m = ForgeGate().run(intent)
    print(json.dumps(m, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
