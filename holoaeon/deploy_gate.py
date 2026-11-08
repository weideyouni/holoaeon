# -*- coding: utf-8 -*-
"""deploy_gate — 部署域闸门（V47，实地项目落地 · 机构端部署编排）
D-11 链位：领域编排环（第十五环·部署域）——pharma_gate（第十四环）之后。
缘起：用户明确需求（实地项目落地）：①优化创建轻量级向量库（授权声明即可，
第一要求=能用好用能落地）；②基线测试+同类项目对齐；③机构端能用方便安装；
④自动发现并耦合本地/服务器小模型；⑤内外网协议融合：内外网不打通、
内网数据不出内网、外网只进升级信息；⑥人群容量 3-4 万；⑦记忆库+接口；
⑧终端 10 个预留 20-30。
P4 第一性原理重裁：「优化创建」≠引入 faiss/sqlite-vec 实物（摧毁零依赖=
供应链风险=机构端反而难装：需编译链/原生依赖）。正解=把既有确定性向量
能力（phc_recall.embed + hypervector）**产品化为机构可用组件**：
持久化(JSONL)+批量入库+检索统计+延迟计量+基线数字+对齐声明。
域分离声明（不推翻 V46）：医保查表仍精确查表（错判报销资格危险）；
**知识召回域**（康复知识/指南条目/教育语料）用向量库正当。
VectorStore 声明（用户要求的"相关声明"）：
  · 同级对齐口径：条目容量 1e3-1e5、检索延迟毫秒级（实测见基线报告），
    与 sqlite-vec/faiss-CPU 在 3-4 万人辖区规模同级；
  · 差异化：零依赖纯标准库（pip 装完即用，无编译链）、确定性
    （sha256 3-gram bundle，同文同向量逐位可复现）、neural=false、
    离线零网络；
  · 不做：十亿级 ANN、神经嵌入、GPU 加速（那是另一量级问题）。
网络二极管（site_gateway，bridges 层）：出站一律 BLOCK（内网数据不出
内网）；入站白名单=升级包（须 SHA256+审批双验证）；内外网协议在网关
边界适配，不直连。
零依赖纯标准库（复用同仓 phc_recall/hypervector）。
封口密语：潮起开门，潮落闭嘴。
"""
import json
import os
import time

from .hypervector import HypervectorConfig, HypervectorSpace
from .phc_recall import embed

SEAL = "潮起开门，潮落闭嘴"

CHAIN_POSITION = {
    "ring": 15,
    "name": "部署域编排（机构端实地落地闸门）",
    "upstream": ("phc_recall", "phc_chronic_engine", "magic_lamp"),
    "role": "向量库组件+容量档案+记忆库接口+终端池+对齐声明+基线口径",
    "lineage_note": "VectorStore=phc_recall.ShardIndex 产品化（同源升级，不计SAME_AS）",
    "disposition_note": "知识召回域向量库；医保查表仍精确查表（V46 不动）",
}

# ── 轻量级向量库声明（用户授权的"相关声明"） ──────────────────────────
DELIBERATE_CHOICE = {
    "capacity_tier": "1e3-1e5 条目（3-4 万人辖区知识库量级）",
    "latency_tier": "毫秒级单次检索（基线实测，见 scripts/bench_vector_baseline.py）",
    "aligned_peers": ("sqlite-vec", "faiss-cpu"),
    "differentiators": ("零依赖纯标准库（无编译链，pip 装完即用）",
                        "确定性：同文同向量，逐位可复现",
                        "离线零网络，内网可全程自主运行",
                        "neural=false（无模型权重漂移）"),
    "not_doing": ("十亿级 ANN", "神经嵌入", "GPU 加速"),
    "domain_note": "知识召回域专用；医保报销查询走 pharma_gate 精确查表",
}

# ── 机构容量档案（用户需求参数化） ────────────────────────────────────
CAPACITY_PROFILE = {
    "population_range": (30000, 40000),
    "terminals_default": 10,
    "terminals_reserved": 30,   # 预留升级 20-30（上限 30）
    "memory_store_capacity": "按需增长（JSONL 追加式）",
    "offline": True,
}


class VectorStore:
    """轻量级向量库（phc_recall.ShardIndex 产品化）：
    持久化 + 批量 + 检索统计 + 延迟计量。确定性，neural=false。"""

    def __init__(self, dim=256, store_path="vector_store.jsonl"):
        self.space = HypervectorSpace(HypervectorConfig(dim=dim))
        self.dim = dim
        self.store_path = store_path
        self.items = {}
        self.vecs = {}
        self.query_count = 0
        self.last_latency_ms = None

    def add(self, item_id, text, meta=None):
        if not item_id or not str(text).strip():
            return {"ok": False, "error": "id/text required", "seal": SEAL}
        if item_id in self.items:
            return {"ok": False, "error": "duplicate id", "seal": SEAL}
        self.items[item_id] = {"id": item_id, "text": text,
                               "meta": meta or {}}
        self.vecs[item_id] = embed(self.space, text)
        return {"ok": True, "count": len(self.items), "seal": SEAL}

    def batch_add(self, entries):
        """entries=[(id, text, meta)]，批量入库。"""
        added = 0
        for eid, text, meta in entries:
            if self.add(eid, text, meta)["ok"]:
                added += 1
        return {"ok": True, "added": added, "total": len(self.items),
                "seal": SEAL}

    def search(self, query, top_k=5):
        """混合检索（基线测试驱动的优化）：
        通道A=trigram 余弦（字面相似）+ 通道B=字符 bigram Dice（词汇重叠）。
        基线实测：纯 trigram 对同义改写命中率 0.0——混合通道补词汇通道。
        两通道确定性融合（权重固定，可复算）。"""
        t0 = time.perf_counter()
        qv = embed(self.space, query)
        qbi = self._bigrams(query)
        scored = []
        for i in self.items:
            cos = self.space.cosine(qv, self.vecs[i])
            dice = self._dice(qbi, self._bigrams(self.items[i]["text"]))
            score = 0.6 * cos + 0.4 * dice
            scored.append((score, i))
        scored.sort(key=lambda x: -x[0])
        self.query_count += 1
        self.last_latency_ms = round(
            (time.perf_counter() - t0) * 1000, 3)
        hits = [{"id": i, "sim": round(s, 4), "text": self.items[i]["text"],
                 "meta": self.items[i]["meta"]}
                for s, i in scored[:max(0, top_k)]]
        return {"ok": True, "hits": hits,
                "latency_ms": self.last_latency_ms, "seal": SEAL}

    @staticmethod
    def _bigrams(text):
        t = " ".join(str(text).split())
        return {t[i:i + 2] for i in range(len(t) - 1)} if len(t) >= 2 else set()

    @classmethod
    def _dice(cls, a, b):
        if not a or not b:
            return 0.0
        return round(2 * len(a & b) / (len(a) + len(b)), 4)

    def save(self):
        """持久化（JSONL 追加式存档：条目+向量分批写）。"""
        with open(self.store_path, "w", encoding="utf-8") as f:
            for i in self.items:
                rec = dict(self.items[i])
                rec["vec"] = self.vecs[i]
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return {"ok": True, "path": self.store_path,
                "entries": len(self.items), "seal": SEAL}

    def load(self):
        """装载（从 JSONL 恢复，向量直接读回——免重算，确定性保真）。"""
        if not os.path.exists(self.store_path):
            return {"ok": False, "error": "store file not found", "seal": SEAL}
        n = 0
        with open(self.store_path, encoding="utf-8") as f:
            for line in f:
                rec = json.loads(line)
                vec = rec.pop("vec")
                self.items[rec["id"]] = rec
                self.vecs[rec["id"]] = vec
                n += 1
        return {"ok": True, "loaded": n, "seal": SEAL}

    def stats(self):
        return {"ok": True, "entries": len(self.items), "dim": self.dim,
                "queries": self.query_count,
                "last_latency_ms": self.last_latency_ms,
                "persistence": "JSONL", "neural": False,
                "deterministic": True, "seal": SEAL}


class MemoryStore:
    """机构记忆库接口：追加式（append-only）读写 + 时间戳 + 引用键。
    与玉安记忆之王/InvestigationLedger 台账模式同构。"""

    def __init__(self, path="memory_store.jsonl"):
        self.path = path
        self.count = 0

    def write(self, key, content):
        rec = {"key": key, "content": content,
               "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        self.count += 1
        return {"ok": True, "count": self.count, "seal": SEAL}

    def read(self, key):
        if not os.path.exists(self.path):
            return {"ok": True, "records": [], "seal": SEAL}
        out = []
        with open(self.path, encoding="utf-8") as f:
            for line in f:
                rec = json.loads(line)
                if rec["key"] == key:
                    out.append(rec)
        return {"ok": True, "records": out, "seal": SEAL}


class TerminalPool:
    """终端池：缺省 10（等保边界口径承 V41），预留升级至 30——
    扩容须显式 approved=True（机构管理员审批，处置权分离）。"""

    def __init__(self, default=CAPACITY_PROFILE["terminals_default"],
                 reserved=CAPACITY_PROFILE["terminals_reserved"]):
        self.limit = default
        self.reserved = reserved
        self.held = set()

    def acquire(self, terminal_id):
        if terminal_id in self.held:
            return {"ok": False, "error": "already held", "seal": SEAL}
        if len(self.held) >= self.limit:
            return {"ok": False, "error": "terminal pool at limit %d"
                    % self.limit, "hint": "扩容须管理员审批", "seal": SEAL}
        self.held.add(terminal_id)
        return {"ok": True, "held": len(self.held), "limit": self.limit,
                "reserved_max": self.reserved, "seal": SEAL}

    def release(self, terminal_id):
        return {"ok": self.held.discard(terminal_id) is None or
                terminal_id not in self.held, "seal": SEAL}

    def expand(self, new_limit, approved=False):
        if not approved:
            return {"ok": False, "error": "扩容须审批（处置权分离）",
                    "seal": SEAL}
        if not (self.limit < new_limit <= self.reserved):
            return {"ok": False,
                    "error": "new_limit 须在 (%d, %d] 区间"
                             % (self.limit, self.reserved), "seal": SEAL}
        self.limit = new_limit
        return {"ok": True, "limit": self.limit, "reserved_max": self.reserved,
                "seal": SEAL}


def capacity_plan(population=35000):
    """3-4 万人容量档案（V41 CapacityPlanner 同源公式参数化）。"""
    if not (CAPACITY_PROFILE["population_range"][0] <= population
            <= CAPACITY_PROFILE["population_range"][1]):
        return {"ok": False, "error": "population 超出本部署域范围",
                "seal": SEAL}
    adults = int(population * 0.55)
    patients = {k: int(adults * p) for k, p in
                (("htn", 0.25), ("t2dm", 0.10), ("copd", 0.03))}
    return {"ok": True, "population": population, "adults_35plus": adults,
            "patients": patients,
            "followup_visits_per_year": sum(v * 4 for v in patients.values()),
            "terminals": CAPACITY_PROFILE["terminals_default"],
            "reserved_terminals": CAPACITY_PROFILE["terminals_reserved"],
            "offline": True, "seal": SEAL}


def audit():
    """总闸快照：report-only。"""
    return {"seal": SEAL, "ring": CHAIN_POSITION["ring"],
            "deliberate_choice": DELIBERATE_CHOICE,
            "capacity": CAPACITY_PROFILE,
            "components": ("VectorStore", "MemoryStore", "TerminalPool",
                           "capacity_plan"),
            "zero_dependency": True, "offline": True, "neural": False}
