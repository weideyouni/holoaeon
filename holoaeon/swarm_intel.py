# -*- coding: utf-8 -*-
"""
HoloAeon 群体智能引擎（Swarm Intelligence Engine）
================================================================================
蒸馏自 MiroFish (666ghj/MiroFish, AGPL-3.0) 的五阶段流水线创意，
用 HoloAeon 确定性原语重新实现。零 LLM 依赖、零外部服务、纯标准库。

许可证纪律（AGPL-3.0 合规）：
  本模块为**重新实现的原创代码**，只借鉴 MiroFish 的流水线创意与数据结构方法论
  （思想-表达二分法），未复制其任何源代码行。

五阶段流水线（创意 → 确定性实现）：
  1. seed_to_graph      种子文本 → 实体提取 → 邻接表图（替代 GraphRAG + Zep Cloud）
  2. persona_synthesize 图实体 → 规则 Persona 生成（替代 LLM Persona 生成）
  3. parallel_simulate  Agent 群体 → 双路并行模拟 → action 记录（替代 OASIS）
  4. report_generate    action 统计 → 涌现模式 → 结构化报告（替代 ReportAgent + LLM）
  5. deep_interact      agent inbox 查询 → 规则响应（替代 IPC + LLM interview）

自组织机制映射（11/11）：
  心跳机制     → five_stage_pipeline 每阶段一个 tick
  细胞骨架机制 → PersonaArchitect 装配 agent 实例
  皮肤机制     → god_view_inject 注入事件（含 Guard 式过滤）
  经络机制     → seed_to_graph 图路由 + deep_interact inbox
  赫布协作场   → parallel_simulate 主路径/验证路径双路
  语义通信基座 → AgentAction 封装为 Envelope
  自组织相似性 → report_generate 多 agent 行动共振模式提取
  runtime      → SwarmOrchestrator 运行时状态管理
  graph        → EntityGraph 邻接表
  类社会组合体 → agent 群体 + 社交演化记录
  城邦架构     → 多个 SimulationRun = 多个城邦

确定性纪律（本模块对投喂稿的关键修正）：
  * 不使用内置 hash()（字符串哈希受 PYTHONHASHSEED 随机化影响，跨进程不稳定），
    一律改用 zlib.crc32 / hashlib.sha256，保证同输入同输出。
  * 不使用 random 全局状态，rng 一律以确定性种子构造。

密令：潮起开门，潮落闭嘴。evidence_class=simulated，仿真≠证明，碳基终裁。
"""
from __future__ import annotations

import hashlib
import json
import random
import re
import sys
import time
import zlib
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


# ============================================================ 数据结构

class Stage(str, Enum):
    """五阶段枚举（心跳机制映射：每阶段一个 tick）。"""
    GRAPH = "graph"
    WORLD = "world"
    SIMULATE = "simulate"
    REPORT = "report"
    INTERACT = "interact"


def _stable_seed(*parts: Any) -> int:
    """跨进程稳定的确定性种子（替代内置 hash()）。"""
    key = "|".join(str(p) for p in parts).encode("utf-8")
    return zlib.crc32(key) & 0x7FFFFFFF


def _stable_hex(text: str, n: int = 12) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:n]


@dataclass
class EntityNode:
    """图实体节点（graph 机制）。"""
    uuid: str
    name: str
    entity_type: str
    summary: str = ""
    attributes: Dict[str, Any] = field(default_factory=dict)
    related_edges: List[Dict[str, Any]] = field(default_factory=list)

    def get_entity_type(self) -> str:
        return self.entity_type or "Entity"

    def to_dict(self) -> Dict[str, Any]:
        return {"uuid": self.uuid, "name": self.name,
                "entity_type": self.entity_type, "summary": self.summary}


@dataclass
class EntityGraph:
    """实体关系图（邻接表；替代 Zep Cloud GraphRAG）。"""
    graph_id: str
    nodes: Dict[str, EntityNode] = field(default_factory=dict)
    edges: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        return len(self.edges)

    @property
    def entity_types(self) -> List[str]:
        return sorted({n.entity_type for n in self.nodes.values() if n.entity_type})

    def add_node(self, node: EntityNode) -> None:
        self.nodes[node.uuid] = node

    def add_edge(self, source_uuid: str, target_uuid: str, name: str, fact: str = "") -> None:
        self.edges.append({"source_node_uuid": source_uuid,
                           "target_node_uuid": target_uuid,
                           "name": name, "fact": fact})
        if source_uuid in self.nodes:
            self.nodes[source_uuid].related_edges.append(
                {"edge_name": name, "direction": "outgoing", "fact": fact})
        if target_uuid in self.nodes:
            self.nodes[target_uuid].related_edges.append(
                {"edge_name": name, "direction": "incoming", "fact": fact})

    def to_dict(self) -> Dict[str, Any]:
        return {
            "graph_id": self.graph_id,
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "entity_types": self.entity_types,
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": self.edges,
        }


@dataclass
class AgentProfile:
    """Agent Persona（细胞骨架机制：Kernel 据此装配 agent）。"""
    user_id: int
    name: str
    bio: str
    persona: str
    entity_type: str = "Entity"
    age: Optional[int] = None
    gender: Optional[str] = None
    mbti: Optional[str] = None
    profession: Optional[str] = None
    interested_topics: List[str] = field(default_factory=list)
    source_entity_uuid: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id, "name": self.name, "bio": self.bio,
            "persona": self.persona, "entity_type": self.entity_type,
            "age": self.age, "gender": self.gender, "mbti": self.mbti,
            "profession": self.profession,
            "interested_topics": self.interested_topics,
        }


@dataclass
class AgentAction:
    """Agent 行动记录（语义通信基座：封装为 Envelope）。"""
    round_num: int
    timestamp: str
    agent_id: int
    agent_name: str
    action_type: str
    action_args: Dict[str, Any] = field(default_factory=dict)
    result: Optional[str] = None
    success: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "round_num": self.round_num, "timestamp": self.timestamp,
            "agent_id": self.agent_id, "agent_name": self.agent_name,
            "action_type": self.action_type, "action_args": self.action_args,
            "result": self.result, "success": self.success,
        }

    def to_envelope(self) -> Dict[str, Any]:
        return {"from": self.agent_id, "type": "action",
                "payload": self.to_dict(), "timestamp": self.timestamp}


@dataclass
class RoundSummary:
    """每轮摘要（自组织相似性：共振模式提取的输入）。"""
    round_num: int
    actions: List[AgentAction] = field(default_factory=list)
    active_agents: List[int] = field(default_factory=list)
    action_type_counts: Dict[str, int] = field(default_factory=dict)

    @property
    def total_actions(self) -> int:
        return len(self.actions)

    def to_dict(self) -> Dict[str, Any]:
        return {"round_num": self.round_num,
                "total_actions": self.total_actions,
                "active_agents_count": len(self.active_agents),
                "action_type_counts": self.action_type_counts}


@dataclass
class SimulationRunState:
    """模拟运行状态（runtime 机制 + 城邦架构：一 Run 即一城邦）。"""
    simulation_id: str
    current_stage: Stage = Stage.GRAPH
    current_round: int = 0
    total_rounds: int = 0
    profiles: List[AgentProfile] = field(default_factory=list)
    rounds: List[RoundSummary] = field(default_factory=list)
    all_actions: List[AgentAction] = field(default_factory=list)
    graph: Optional[EntityGraph] = None
    report: Optional[Dict[str, Any]] = None
    started_at: str = ""
    completed_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "simulation_id": self.simulation_id,
            "current_stage": self.current_stage.value,
            "current_round": self.current_round,
            "total_rounds": self.total_rounds,
            "profile_count": len(self.profiles),
            "round_count": len(self.rounds),
            "total_actions": len(self.all_actions),
            "graph": self.graph.to_dict() if self.graph else None,
            "report": self.report,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }


# ============================================================ Stage 1: 种子→图

class SeedToGraph:
    """种子文本 → 实体关系图（经络机制：图路由）。替代 GraphRAG + Zep，零 LLM。"""

    ENTITY_TYPE_KEYWORDS: Dict[str, List[str]] = {
        "person": ["人", "者", "员", "生", "家", "师", "官", "长", "导", "工", "匠", "民", "男", "女"],
        "organization": ["公司", "机构", "组织", "部门", "委员会", "局", "院", "校", "所", "中心", "团", "队"],
        "location": ["省", "市", "县", "区", "镇", "村", "街", "路", "国", "洲", "山", "河", "湖", "海", "岛"],
        "event": ["事件", "事故", "会议", "活动", "运动", "战争", "革命", "改革", "发布", "出台", "爆发"],
        "concept": ["理论", "主义", "思想", "观点", "理念", "模式", "方法", "技术", "系统", "框架", "标准"],
        "time": ["年", "月", "日", "时", "期", "代", "世纪", "季度", "周", "今天", "昨天", "明天"],
        "document": ["报告", "文件", "文章", "论文", "书", "法规", "法律", "条例", "规定", "方案", "计划"],
    }

    RELATION_KEYWORDS: Dict[str, List[str]] = {
        "belongs_to": ["属于", "隶属", "下辖"],
        "located_in": ["位于", "地处"],
        "participated_in": ["参与", "参加", "出席"],
        "created": ["创建", "创立", "成立", "建立", "创办"],
        "caused": ["导致", "引发", "造成", "促使"],
        "opposed": ["反对", "抵制", "抗议"],
        "supported": ["支持", "赞同", "拥护"],
        "reported_by": ["报道", "刊登", "发布"],
    }

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """标点切句 + CJK bigram（ASCII 逐字符，短 token 后续按长度过滤）。"""
        tokens: List[str] = []
        for sent in re.split(r"[，。！？；,;!?.\s]+", text):
            sent = sent.strip()
            if not sent:
                continue
            cjk = ""
            for ch in sent:
                if "\u4e00" <= ch <= "\u9fff":
                    cjk += ch
                else:
                    if len(cjk) > 1:
                        tokens.extend(cjk[i:i + 2] for i in range(len(cjk) - 1))
                    elif cjk:
                        tokens.append(cjk)
                    cjk = ""
                    if ord(ch) < 128 and ch.isalnum():
                        tokens.append(ch)
            if len(cjk) > 1:
                tokens.extend(cjk[i:i + 2] for i in range(len(cjk) - 1))
            elif cjk:
                tokens.append(cjk)
        return tokens

    @classmethod
    def extract_entities(cls, text: str, max_entities: int = 50) -> List[EntityNode]:
        freq: Dict[str, int] = defaultdict(int)
        for t in cls._tokenize(text):
            freq[t] += 1
        entities: List[EntityNode] = []
        seen = set()
        for token, count in sorted(freq.items(), key=lambda x: (-x[1], x[0])):
            if len(token) < 2 or token in seen:
                continue
            etype = "concept"
            for candidate, keywords in cls.ENTITY_TYPE_KEYWORDS.items():
                if any(kw in token for kw in keywords):
                    etype = candidate
                    break
            entities.append(EntityNode(
                uuid=_stable_hex(token, 16), name=token, entity_type=etype,
                summary="%s: %s (freq=%d)" % (etype, token, count)))
            seen.add(token)
            if len(entities) >= max_entities:
                break
        return entities

    @classmethod
    def extract_relations(cls, text: str, entities: List[EntityNode]) -> List[Dict[str, Any]]:
        entity_map = {e.name: e for e in entities}
        relations: List[Dict[str, Any]] = []
        for sent in re.split(r"[，。！？；,;!?.\n]+", text):
            sent = sent.strip()
            if not sent or len(sent) < 3:
                continue
            found = [e for name, e in entity_map.items() if name in sent]
            if len(found) < 2:
                continue
            for rel_type, keywords in cls.RELATION_KEYWORDS.items():
                if any(kw in sent for kw in keywords):
                    for i in range(len(found) - 1):
                        relations.append({"source_uuid": found[i].uuid,
                                          "target_uuid": found[i + 1].uuid,
                                          "name": rel_type, "fact": sent[:200]})
                    break
        return relations

    @classmethod
    def build_graph(cls, text: str, graph_id: str = "", max_entities: int = 50) -> EntityGraph:
        graph_id = graph_id or "swarm_%s" % _stable_hex(text[:100])
        entities = cls.extract_entities(text, max_entities=max_entities)
        graph = EntityGraph(graph_id=graph_id)
        for e in entities:
            graph.add_node(e)
        for r in cls.extract_relations(text, entities):
            graph.add_edge(r["source_uuid"], r["target_uuid"], r["name"], r.get("fact", ""))
        return graph


# ============================================================ Stage 2: Persona

class PersonaArchitect:
    """规则版 Persona 生成（细胞骨架机制）。"""

    MBTI_TYPES = ["INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP",
                  "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP"]

    PERSONA_TEMPLATES: Dict[str, Dict[str, Any]] = {
        "person": {"bio_tpl": "{name}是一个积极参与讨论的个体。",
                   "persona_tpl": "{name}是一个{entity_type}，关注社会议题，善于表达观点。",
                   "age_range": (18, 60), "gender": "male", "profession": "公众参与者",
                   "topics": ["社会议题", "公共事务", "信息传播"]},
        "organization": {"bio_tpl": "{name}的官方账号，发布机构信息。",
                         "persona_tpl": "{name}是一个机构实体，发布官方立场和公告，语言严谨。",
                         "age_range": (30, 30), "gender": "other", "profession": "机构",
                         "topics": ["官方公告", "机构动态", "公共政策"]},
        "location": {"bio_tpl": "{name}，地理实体。",
                     "persona_tpl": "{name}是一个地理位置，影响当地社会动态。",
                     "age_range": (30, 30), "gender": "other", "profession": "地理标识",
                     "topics": ["地方事务", "区域动态"]},
        "event": {"bio_tpl": "事件：{name}。",
                  "persona_tpl": "{name}是一个社会事件，引发公众关注和讨论。",
                  "age_range": (30, 30), "gender": "other", "profession": "事件",
                  "topics": ["事件进展", "公众反应", "媒体报道"]},
        "concept": {"bio_tpl": "概念：{name}。",
                    "persona_tpl": "{name}是一个抽象概念/理论，影响公众认知和讨论框架。",
                    "age_range": (30, 30), "gender": "other", "profession": "概念",
                    "topics": ["理论讨论", "概念传播"]},
        "time": {"bio_tpl": "时间节点：{name}。",
                 "persona_tpl": "{name}是一个时间标记，关联特定历史事件或周期。",
                 "age_range": (30, 30), "gender": "other", "profession": "时间",
                 "topics": ["历史回顾", "周期分析"]},
        "document": {"bio_tpl": "文献：{name}。",
                     "persona_tpl": "{name}是一份文件/报告，包含官方信息或分析结论。",
                     "age_range": (30, 30), "gender": "other", "profession": "文献",
                     "topics": ["文件内容", "政策解读"]},
    }

    @classmethod
    def generate(cls, entity: EntityNode, user_id: int = 0) -> AgentProfile:
        etype = entity.entity_type or "concept"
        tpl = cls.PERSONA_TEMPLATES.get(etype, cls.PERSONA_TEMPLATES["concept"])
        rng = random.Random(_stable_seed("persona", entity.uuid))
        lo, hi = tpl["age_range"]
        age = rng.randint(lo, hi) if lo != hi else lo
        return AgentProfile(
            user_id=user_id, name=entity.name,
            bio=tpl["bio_tpl"].format(name=entity.name),
            persona=tpl["persona_tpl"].format(name=entity.name, entity_type=etype),
            entity_type=etype, age=age, gender=tpl["gender"],
            mbti=rng.choice(cls.MBTI_TYPES), profession=tpl["profession"],
            interested_topics=list(tpl["topics"]), source_entity_uuid=entity.uuid)

    @classmethod
    def generate_batch(cls, graph: EntityGraph) -> List[AgentProfile]:
        return [cls.generate(node, user_id=idx)
                for idx, node in enumerate(graph.nodes.values())]


# ============================================================ Stage 3: 并行模拟

class ParallelSimulator:
    """双路并行模拟（赫布协作场：主路径 + 验证路径）。替代 OASIS。"""

    ACTION_TYPES = ["CREATE_POST", "LIKE_POST", "REPLY_POST", "REPOST", "FOLLOW_USER",
                    "CREATE_COMMENT", "UPVOTE", "DOWNVOTE", "SHARE", "VIEW"]

    TYPE_PREFS: Dict[str, List[str]] = {
        "person": ["CREATE_POST", "REPLY_POST", "LIKE_POST", "REPOST"],
        "organization": ["CREATE_POST", "SHARE"],
        "event": ["CREATE_POST", "SHARE", "VIEW"],
        "concept": ["CREATE_COMMENT", "UPVOTE", "DOWNVOTE"],
        "document": ["SHARE", "VIEW"],
    }

    def __init__(self, profiles: List[AgentProfile], total_rounds: int = 10):
        self.profiles = profiles
        self.total_rounds = total_rounds
        self.rounds: List[RoundSummary] = []
        self.all_actions: List[AgentAction] = []
        self.verification_log: List[Dict[str, Any]] = []

    def _agent_step(self, profile: AgentProfile, round_num: int) -> AgentAction:
        rng = random.Random(_stable_seed("act", profile.user_id, round_num))
        prefs = self.TYPE_PREFS.get(profile.entity_type, self.ACTION_TYPES[:4])
        action_type = rng.choice(prefs)
        return AgentAction(
            round_num=round_num,
            timestamp="round_%d_agent_%d" % (round_num, profile.user_id),
            agent_id=profile.user_id, agent_name=profile.name,
            action_type=action_type,
            action_args={"entity_type": profile.entity_type, "mbti": profile.mbti or "ISTJ"},
            result="%s by %s" % (action_type, profile.name), success=True)

    def simulate_round(self, round_num: int) -> RoundSummary:
        actions = []
        active = []
        counts: Dict[str, int] = defaultdict(int)
        for profile in self.profiles:
            action = self._agent_step(profile, round_num)
            actions.append(action)
            self.all_actions.append(action)
            active.append(profile.user_id)
            counts[action.action_type] += 1
        summary = RoundSummary(round_num=round_num, actions=actions,
                               active_agents=active, action_type_counts=dict(counts))
        self.rounds.append(summary)
        return summary

    def verify_round(self, round_num: int) -> bool:
        """验证路径：该轮每个 active agent 都有且仅有对应 action。"""
        if round_num >= len(self.rounds):
            return False
        summary = self.rounds[round_num]
        action_agents = {a.agent_id for a in summary.actions}
        ok = len(action_agents) == len(summary.active_agents) and summary.total_actions > 0
        self.verification_log.append({"round": round_num, "ok": ok,
                                      "agents": len(action_agents)})
        return ok

    def run(self) -> List[RoundSummary]:
        for r in range(1, self.total_rounds + 1):
            self.simulate_round(r)
            self.verify_round(r)
        return self.rounds


# ============================================================ Stage 4: 报告

class ReportSynthesizer:
    """确定性报告生成（自组织相似性：共振模式提取）。替代 ReportAgent + LLM。"""

    @classmethod
    def generate(cls, actions: List[AgentAction], rounds: List[RoundSummary],
                 profiles: List[AgentProfile]) -> Dict[str, Any]:
        total_actions = len(actions)
        type_dist: Dict[str, int] = defaultdict(int)
        agent_counts: Dict[int, int] = defaultdict(int)
        for a in actions:
            type_dist[a.action_type] += 1
            agent_counts[a.agent_id] += 1

        name_of = {p.user_id: p.name for p in profiles}
        top = sorted(agent_counts.items(), key=lambda x: (-x[1], x[0]))[:5]
        opinion_leaders = [{"agent_id": aid, "action_count": cnt,
                            "name": name_of.get(aid, "agent_%d" % aid)}
                           for aid, cnt in top]

        trend = []
        for r in rounds:
            dominant = "none"
            if r.action_type_counts:
                dominant = max(r.action_type_counts.items(),
                               key=lambda kv: (kv[1], kv[0]))[0]
            trend.append({"round": r.round_num, "total_actions": r.total_actions,
                          "dominant_type": dominant})

        emergent = []
        for atype, count in sorted(type_dist.items(), key=lambda kv: (-kv[1], kv[0])):
            ratio = count / max(total_actions, 1)
            if ratio > 0.4:
                emergent.append({"pattern": "%s主导" % atype, "ratio": round(ratio, 3),
                                 "interpretation": "群体行为以%s为主，占比%.0f%%" % (atype, ratio * 100)})

        return {
            "summary": {"total_rounds": len(rounds), "total_actions": total_actions,
                        "total_agents": len(profiles),
                        "agent_types": sorted({p.entity_type for p in profiles})},
            "action_distribution": dict(type_dist),
            "opinion_leaders": opinion_leaders,
            "trend": trend,
            "emergent_signals": emergent,
            "conclusion": ("经过%d轮模拟，%d个agent产生%d个行动。%s"
                           % (len(rounds), len(profiles), total_actions,
                              "涌现%d个主导模式。" % len(emergent) if emergent
                              else "未检测到明显主导模式。")),
        }


# ============================================================ Stage 5: 深度交互

class DeepInteractor:
    """深度交互（经络机制：agent inbox 接收查询）。替代 IPC + LLM interview。"""

    RESPONSE_TEMPLATES: Dict[str, str] = {
        "person": "作为{name}（{profession}），我对「{prompt}」的看法是：基于我的{mbti}性格，我会从{topics}角度来分析。",
        "organization": "作为{name}的官方账号，对于「{prompt}」，我们的立场是：这符合我们的{profession}职能范围，我们将按既定流程处理。",
        "event": "事件「{name}」对「{prompt}」的影响：此事件可能引发公众关注，影响范围取决于事件规模与传播速度。",
        "concept": "概念「{name}」与「{prompt}」的关系：这是{entity_type}层面的关联，需要从理论框架分析。",
        "default": "作为{name}（类型{entity_type}），对「{prompt}」的回应：我从{profession}角度进行回应。",
    }

    @classmethod
    def interview(cls, profile: AgentProfile, prompt: str) -> Dict[str, Any]:
        tpl = cls.RESPONSE_TEMPLATES.get(profile.entity_type, cls.RESPONSE_TEMPLATES["default"])
        response = tpl.format(
            name=profile.name, profession=profile.profession or "参与者",
            mbti=profile.mbti or "ISTJ", entity_type=profile.entity_type,
            topics=", ".join(profile.interested_topics[:2]) or "相关议题",
            prompt=prompt)
        return {"success": True, "agent_id": profile.user_id, "agent_name": profile.name,
                "entity_type": profile.entity_type, "prompt": prompt,
                "response": response,
                "timestamp": "interview_%d_%d" % (profile.user_id, _stable_seed("iv", prompt) % 10000)}

    @classmethod
    def interview_all(cls, profiles: List[AgentProfile], prompt: str) -> List[Dict[str, Any]]:
        return [cls.interview(p, prompt) for p in profiles]


# ============================================================ 编排器

class SwarmOrchestrator:
    """群体智能引擎编排器（runtime + 城邦架构：一 SimulationRun = 一城邦）。"""

    def __init__(self):
        self.simulations: Dict[str, SimulationRunState] = {}

    def run_pipeline(self, seed_text: str, total_rounds: int = 10,
                     simulation_id: str = "") -> SimulationRunState:
        sim_id = simulation_id or "sim_%s" % _stable_hex(seed_text[:50])
        state = SimulationRunState(simulation_id=sim_id, total_rounds=total_rounds,
                                   started_at=str(int(time.time())))

        state.current_stage = Stage.GRAPH          # tick 1
        state.graph = SeedToGraph.build_graph(seed_text, graph_id=sim_id)

        state.current_stage = Stage.WORLD          # tick 2
        state.profiles = PersonaArchitect.generate_batch(state.graph)

        state.current_stage = Stage.SIMULATE       # tick 3
        simulator = ParallelSimulator(state.profiles, total_rounds)
        state.rounds = simulator.run()
        state.all_actions = simulator.all_actions
        state.current_round = total_rounds

        state.current_stage = Stage.REPORT         # tick 4
        state.report = ReportSynthesizer.generate(state.all_actions, state.rounds, state.profiles)

        state.current_stage = Stage.INTERACT       # tick 5
        state.completed_at = str(int(time.time()))
        self.simulations[sim_id] = state
        return state

    def interact(self, simulation_id: str, agent_id: int, prompt: str) -> Dict[str, Any]:
        state = self.simulations.get(simulation_id)
        if not state:
            return {"success": False, "error": "simulation not found"}
        match = next((p for p in state.profiles if p.user_id == agent_id), None)
        if match is None:
            return {"success": False, "error": "agent not found"}
        return DeepInteractor.interview(match, prompt)

    def god_view_inject(self, simulation_id: str, event: Dict[str, Any]) -> Dict[str, Any]:
        """God View 注入（皮肤机制：注入前过滤非法载荷）。"""
        state = self.simulations.get(simulation_id)
        if not state:
            return {"success": False, "error": "simulation not found"}
        if not isinstance(event, dict) or not event:
            return {"success": False, "error": "invalid event payload (skin guard)"}
        injected = AgentAction(
            round_num=state.current_round + 1,
            timestamp="god_view_inject_%d" % int(time.time()),
            agent_id=-1, agent_name="GOD_VIEW", action_type="EVENT_INJECTION",
            action_args=dict(event), result="injected: %s" % event.get("type", "unknown"),
            success=True)
        state.all_actions.append(injected)
        return {"success": True, "injected": injected.to_dict(),
                "action_total": len(state.all_actions)}

    def list_simulations(self) -> List[Dict[str, Any]]:
        return [{"simulation_id": s.simulation_id, "stage": s.current_stage.value,
                 "rounds": s.current_round, "actions": len(s.all_actions),
                 "agents": len(s.profiles)} for s in self.simulations.values()]


# ============================================================ 扩展包技能入口（模块级函数）

DEFAULT_SEED = ("北京邮电大学发生了一起学生事件，引发了社会广泛关注。"
                "学校发布了官方声明，学生们在社交媒体上讨论热烈。"
                "媒体报道了事件的经过，专家分析了事件的影响。")


def swarm_seed_to_graph(seed_text: str = DEFAULT_SEED, max_entities: int = 30, **_a: Any) -> dict:
    """种子建图：文本→实体+关系邻接表（确定性，零 LLM）。"""
    g = SeedToGraph.build_graph(str(seed_text), max_entities=int(max_entities))
    return {"status": "ok", "graph_id": g.graph_id, "node_count": g.node_count,
            "edge_count": g.edge_count, "entity_types": g.entity_types}


def swarm_persona_synthesize(seed_text: str = DEFAULT_SEED, max_entities: int = 30, **_a: Any) -> dict:
    """角色合成：图实体→规则 Persona。"""
    g = SeedToGraph.build_graph(str(seed_text), max_entities=int(max_entities))
    profiles = PersonaArchitect.generate_batch(g)
    return {"status": "ok", "profile_count": len(profiles),
            "sample": [profiles[0].to_dict()] if profiles else []}


def swarm_parallel_simulate(seed_text: str = DEFAULT_SEED, rounds: int = 5, **_a: Any) -> dict:
    """并行模拟：双路（主路径 + 验证路径）。"""
    g = SeedToGraph.build_graph(str(seed_text), max_entities=20)
    profiles = PersonaArchitect.generate_batch(g)
    sim = ParallelSimulator(profiles, total_rounds=int(rounds))
    sim.run()
    ok = all(x["ok"] for x in sim.verification_log) if sim.verification_log else False
    return {"status": "ok", "rounds": len(sim.rounds), "actions": len(sim.all_actions),
            "verification_all_ok": ok}


def swarm_report_generate(seed_text: str = DEFAULT_SEED, rounds: int = 5, **_a: Any) -> dict:
    """报告生成：action 统计→涌现模式→结构化报告。"""
    g = SeedToGraph.build_graph(str(seed_text), max_entities=20)
    profiles = PersonaArchitect.generate_batch(g)
    sim = ParallelSimulator(profiles, total_rounds=int(rounds))
    sim.run()
    rep = ReportSynthesizer.generate(sim.all_actions, sim.rounds, profiles)
    return {"status": "ok", "summary": rep["summary"],
            "emergent_count": len(rep["emergent_signals"]),
            "conclusion": rep["conclusion"]}


def swarm_deep_interact(seed_text: str = DEFAULT_SEED, prompt: str = "你对这件事怎么看？", **_a: Any) -> dict:
    """深度交互：采访 0 号 agent。"""
    orch = SwarmOrchestrator()
    state = orch.run_pipeline(str(seed_text), total_rounds=3)
    if not state.profiles:
        return {"status": "WARN", "error": "no agents generated"}
    r = orch.interact(state.simulation_id, state.profiles[0].user_id, str(prompt))
    return {"status": "ok", "agent_name": r.get("agent_name"),
            "response": r.get("response")}


# ============================================================ CLI

def main(argv: Optional[List[str]] = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    if not args:
        print("用法: python -m holoaeon.swarm_intel <seed_text> [rounds]")
        print("      python -m holoaeon.swarm_intel --demo")
        return 0
    if args[0] == "--demo":
        seed, rounds = DEFAULT_SEED, 5
    else:
        seed = args[0]
        rounds = int(args[1]) if len(args) > 1 else 10

    orch = SwarmOrchestrator()
    state = orch.run_pipeline(seed, total_rounds=rounds)
    print("\n" + "=" * 60)
    print("群体智能模拟完成: %s" % state.simulation_id)
    print("=" * 60)
    print("阶段: %s" % state.current_stage.value)
    print("实体数: %d" % (state.graph.node_count if state.graph else 0))
    print("Agent数: %d" % len(state.profiles))
    print("总行动数: %d" % len(state.all_actions))
    print("模拟轮数: %d" % state.current_round)
    print("\n--- 报告 ---")
    if state.report:
        print(json.dumps(state.report, ensure_ascii=False, indent=2))
    print("\n--- 深度交互示例 ---")
    if state.profiles:
        r = orch.interact(state.simulation_id, state.profiles[0].user_id, "你对这次事件的看法？")
        print(json.dumps(r, ensure_ascii=False, indent=2))
    print("\n潮起开门，潮落闭嘴。evidence_class=simulated，仿真≠证明，碳基终裁。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
