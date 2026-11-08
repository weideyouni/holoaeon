# -*- coding: utf-8 -*-
"""phc_recall — 公共卫生召回层（V42，实战1号轻量化加速 · 向量记忆分片索引）
D-11 链位：公共卫生域（第十一环）附属召回层——phc_chronic_engine 的加速件。
缘起：千问侧建议（对外智能体，无 holoaeon 底层认知）称需"装轻量向量库"；
四人组扬弃裁决——方向对（向量记忆层+三段链路），但 holoaeon 已有硬核资产：
hypervector.py（VSA/HDC：make/bundle/cosine，sha256 确定性派生，纯标准库）。
故零新依赖：不引入 sqlite-vec/ZVec/turbovec/LEANN/重型库（破坏零依赖纪律），
只补「知识条目分片索引层」这一缺口。
取（形状）：结构化过滤→向量召回→规则校验三段链路；入库预计算；六系统分片
子索引；版本化同步（联网只更新索引不改推理逻辑）。
弃（X-items）：外部向量库选型；重型库；把向量库当独立数据库而非记忆层。
关联声明：三段链路与 klein_projection「投影→评估→吸纳」节拍同构——
仅记关联，不计入 SAME_AS 趋同（诚实处理，避免混记）。
处置权分离·医学版（承 V41）：召回结果=候选集+引用来源，零处方零剂量，
决策权归执业医师。
零依赖纯标准库（复用同仓 hypervector）。封口密语：潮起开门，潮落闭嘴。
"""
from .hypervector import HypervectorConfig, HypervectorSpace

SEAL = "潮起开门，潮落闭嘴"

CHAIN_POSITION = {
    "ring": 11,
    "layer": "recall（附属召回层）",
    "name": "公共卫生召回层（实战1号轻量化加速）",
    "upstream": ("hypervector", "phc_chronic_engine", "magic_lamp"),
    "role": "知识条目本体+六系统分片+预计算嵌入+三段链路+版本化同步",
    "lineage_note": "三段链路≈klein投影-评估-吸纳节拍：关联声明，不计SAME_AS",
    "disposition_note": "候选集+引用，零处方零剂量，医师终审",
}

# 知识条目本体（千问建议的"慢病康复知识本体"落到确定性 schema）：
# 病/证候/西药/中成药/康复干预/红旗症状/医保条目 —— 七类。
ITEM_KINDS = ("disease", "syndrome", "drug_w", "drug_tcm",
              "rehab", "redflag", "insurance")

# 分片键：与 phc_chronic_engine.SIX_SYSTEM_ATLAS 六系统对齐 + A类公卫包
SHARDS = ("nervous", "cardio_cerebro", "endocrine", "immune",
          "malignancy", "ortho", "phc_a")


def validate_item(item):
    """本体校验：kind 必须七类之一，system 必须分片键之一，text 非空。"""
    if not isinstance(item, dict):
        return {"ok": False, "error": "item must be dict", "seal": SEAL}
    for k in ("id", "kind", "system", "text"):
        if k not in item:
            return {"ok": False, "error": "missing field: %s" % k,
                    "seal": SEAL}
    if item["kind"] not in ITEM_KINDS:
        return {"ok": False, "error": "kind not in ITEM_KINDS", "seal": SEAL}
    if item["system"] not in SHARDS:
        return {"ok": False, "error": "system not in SHARDS", "seal": SEAL}
    if not str(item["text"]).strip():
        return {"ok": False, "error": "empty text", "seal": SEAL}
    return {"ok": True, "seal": SEAL}


def _trigrams(text, n=3):
    t = " ".join(str(text).split())
    if len(t) < n:
        return [t] if t else []
    return [t[i:i + n] for i in range(len(t) - n + 1)]


def embed(space, text):
    """确定性嵌入：字符 3-gram → make（sha256 派生）→ bundle。
    零模型零推理（neural=false），同文必同向量（可复算）。"""
    grams = _trigrams(text)
    if not grams:
        return [0.0] * space.dim
    return space.bundle([space.make(g) for g in grams])


class ShardIndex:
    """六系统分片索引：入库预计算向量（检索时零重复计算——千问性能建议
    的确定性落地）；search=先结构化过滤后余弦召回。"""

    def __init__(self, dim=256):
        self.space = HypervectorSpace(HypervectorConfig(dim=dim))
        self.dim = dim
        self.items = {}   # id -> item
        self.vecs = {}    # id -> 预计算向量

    def add(self, item):
        v = validate_item(item)
        if not v["ok"]:
            return v
        self.items[item["id"]] = dict(item)
        self.vecs[item["id"]] = embed(self.space, item["text"])
        return {"ok": True, "id": item["id"], "precomputed": True,
                "seal": SEAL}

    def _filter(self, kind=None, system=None):
        for iid, it in self.items.items():
            if kind is not None and it["kind"] != kind:
                continue
            if system is not None and it["system"] != system:
                continue
            yield iid

    def search(self, query, kind=None, system=None, top_k=5):
        """三段链路之前两段：结构化过滤 → 向量召回 top_k。
        返回候选集（含相似度与来源引用），不做任何处置决策。"""
        qv = embed(self.space, query)
        scored = []
        for iid in self._filter(kind, system):
            sim = self.space.cosine(qv, self.vecs[iid])
            scored.append((sim, iid))
        scored.sort(key=lambda x: -x[0])
        hits = [{"id": iid, "sim": round(sim, 4),
                 "kind": self.items[iid]["kind"],
                 "system": self.items[iid]["system"],
                 "text": self.items[iid]["text"],
                 "meta": self.items[iid].get("meta", {})}
                for sim, iid in scored[:max(0, top_k)]]
        return {"ok": True, "query": str(query)[:80], "hits": hits,
                "scanned": len(scored), "seal": SEAL}


class RuleGate:
    """第三段：规则校验（承 V41 红线）。红旗命中→转诊提示；
    医保属性仅作标记；输出零处方零剂量。"""

    REDFLAG_ACTION = "命中红旗症状→建议转诊上级医院（提示，非诊断）"

    @classmethod
    def check(cls, hits):
        flags = [h for h in hits if h["kind"] == "redflag"]
        insurance = [h["id"] for h in hits
                     if h["kind"] == "insurance"]
        return {"ok": True,
                "redflag": [h["id"] for h in flags],
                "action": cls.REDFLAG_ACTION if flags else "无红旗命中",
                "insurance_refs": insurance,
                "zero_prescription": True, "seal": SEAL}


class SyncLedger:
    """版本化同步台账：联网时只更新索引与元数据，不改核心推理逻辑；
    每次更新记录来源/版本/生效日期/同步时间（千问建议的确定性落地）。"""

    def __init__(self):
        self.records = []

    def record(self, source, version, effective_date):
        import time as _t
        self.records.append({"source": source, "version": version,
                             "effective_date": effective_date,
                             "last_sync": _t.strftime("%Y-%m-%d"),
                             "seal": SEAL})
        return {"ok": True, "count": len(self.records), "seal": SEAL}

    def manifest(self):
        return {"records": list(self.records),
                "policy": "联网只更新索引，推理逻辑零变更", "seal": SEAL}


def recall_pipeline(index, query, kind=None, system=None, top_k=5):
    """全链路：结构化过滤→向量召回→规则校验→候选集。
    可解释（每条带来源引用），可追溯，零处方，医师终审。"""
    step1 = index.search(query, kind=kind, system=system, top_k=top_k)
    step2 = RuleGate.check(step1["hits"])
    return {"ok": True, "candidates": step1["hits"],
            "rule_gate": step2,
            "disclaimer": "候选集仅供医师参考，非诊断非处方",
            "decision": "执业医师终审", "seal": SEAL}


def audit():
    """总闸：召回层状态快照，report-only。"""
    return {"seal": SEAL, "ring": CHAIN_POSITION["ring"],
            "layer": CHAIN_POSITION["layer"],
            "item_kinds": list(ITEM_KINDS), "shards": list(SHARDS),
            "zero_dependency": "复用同仓 hypervector，零新依赖",
            "zero_network": True, "zero_prescription": True,
            "neural": False}
