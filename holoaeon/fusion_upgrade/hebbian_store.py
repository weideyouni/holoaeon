# -*- coding: utf-8 -*-
"""B6 · 赫布权重落盘（memory L2）可调用入口

定位：把运行期 `HebbianField` 的边权重冻结成确定性 JSON，重启后原样复原，
      并给出「重启前后 top-k 逐字相等」的自证材料。只读写本地文件，
      不 import ivsa、不启网络、不新增扩展包，不动 25/47/9 维度。

用法：
    from holoaeon.fusion_upgrade.hebbian_store import (STORE_ID, REPLAY_QUERIES,
                                                       replay_into, snapshot,
                                                       save, load, verify,
                                                       restore, topk, topk_text)
    runtime → replay_into(runtime) → snapshot(runtime.field, meta, seeds) → save(doc, path)
    重启后：load(path) → verify(doc) → restore(doc, fresh_field) → topk_text(fresh_field, seeds)

约定：权重一律 round 到 5 位小数；边键取字典序较小者在前；落盘前对
      「sha256 置空后的规范化字节」自哈希，校验时用同法复算。
"""
from __future__ import annotations

import hashlib
import json
import os

STORE_ID = "SG-B6-HEBBIAN-STORE-V1"
REPLAY_ID = "SG-B6-REPLAY-SET-V1"
BATCH = "B6"
DECAY = 0.02
CAP = 0.99
PRUNE_BELOW = 0.01
ROUND = 5
TOP_K = 3

# 固定回放集（24 条，写死顺序；改一条即改 digest，故不许随手增删）
REPLAY_QUERIES = (
    "康复 训练 方案 评估",
    "中西医 融合 康复 路径",
    "经络 穴位 气血 通路",
    "赫布 协作场 权重 衰减",
    "语义 总线 模块 路由",
    "技能 矩阵 索引 匹配",
    "肌骨 康复 分期 目标",
    "神经 康复 步态 训练",
    "心肺 康复 负荷 监测",
    "疼痛 管理 非药物 手段",
    "去重 指纹 相似 度量",
    "嵌入 向量 检索 排序",
    "时序 节律 窗口 对齐",
    "聚类 分群 稳定 边界",
    "注入 通道 配额 预算",
    "运维 观测 熔断 回滚",
    "冷 热 插拔 回滚 点",
    "契约 校验 指纹 互认",
    "用途 标签 分类 抽样",
    "试点 回执 证据 等级",
    "红 线 复核 零 违规",
    "全息 心跳 节拍 稳定",
    "细胞骨架 鲁棒 冗余",
    "皮肤 网 关 权限 校验",
)


# ------------------------------------------------------------------ 规范化与自哈希
def canonical(doc):
    """规范化字节：键排序、无空格分隔、UTF-8 原字符。"""
    return json.dumps(doc, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(doc):
    """自指摘要：把 sha256 字段置空后取规范化字节的 sha256。"""
    body = dict(doc)
    body["sha256"] = ""
    return hashlib.sha256(canonical(body).encode("utf-8")).hexdigest()


def seal(doc):
    """填好 sha256 的副本（不改入参）。"""
    out = dict(doc)
    out["sha256"] = digest(doc)
    return out


# ------------------------------------------------------------------ 回放（确定性）
def replay_into(runtime, queries=REPLAY_QUERIES):
    """对固定回放集逐条 dispatch：共激活落进赫布场、流量落进经络。

    返回通道负载与边数；不做任何随机、不读时钟。
    """
    load = {}
    mechanics = {}
    for q in queries:
        r = runtime.dispatch(q)
        ch = r.get("channel")
        load[ch] = load.get(ch, 0) + 1
        m = r.get("mechanism")
        mechanics[m] = mechanics.get(m, 0) + 1
    return {
        "replay_id": REPLAY_ID,
        "steps": len(queries),
        "load": {k: load[k] for k in sorted(load)},
        "mechanism_hits": {k: mechanics[k] for k in sorted(mechanics)},
        "edges": len(runtime.field._w),  # noqa: SLF001  只读计数
        "capacity": runtime.meridian.capacity,
    }


# ------------------------------------------------------------------ 冻结 / 复原
def snapshot(field, meta, seeds, k=TOP_K):
    """把边权重冻成可复算的 store 文档（含 top-k 基线，用于重启比对）。"""
    edges = []
    for (a, b), w in sorted(field._w.items()):  # noqa: SLF001  只读遍历
        edges.append({"a": a, "b": b, "w": round(float(w), ROUND)})
    nodes = sorted({e["a"] for e in edges} | {e["b"] for e in edges})
    doc = {
        "store_id": STORE_ID,
        "replay_id": REPLAY_ID,
        "batch": BATCH,
        "evidence_class": "simulated",
        "policy": {
            "decay": DECAY,
            "cap": CAP,
            "prune_below": PRUNE_BELOW,
            "round": ROUND,
            "key_order": "lexicographic_min_first",
            "top_k": int(k),
        },
        "meta": dict(meta),
        "edge_count": len(edges),
        "node_count": len(nodes),
        "nodes": nodes,
        "edges": edges,
        "topk": topk_doc(field, seeds, k),
        "sha256": "",
    }
    return seal(doc)


def topk_doc(field, seeds, k=TOP_K):
    """每条种子的 top-k 邻居（同分按名字排序，确定性）。"""
    rows = []
    for s in seeds:
        rows.append({"seed": s, "k": int(k),
                     "neighbors": [{"name": n, "w": round(float(w), ROUND)}
                                   for n, w in field.neighbors(s, k)]})
    return {"seeds": list(seeds), "k": int(k), "rows": rows}


def topk_text(field, seeds, k=TOP_K):
    """逐字比对用的文本视图：seed / 邻居 / 权重 三列制表符分隔。"""
    lines = []
    for row in topk_doc(field, seeds, k)["rows"]:
        for nb in row["neighbors"]:
            lines.append("%s\t%s\t%.5f" % (row["seed"], nb["name"], nb["w"]))
        if not row["neighbors"]:
            lines.append("%s\t-\t0.00000" % row["seed"])
    return "\n".join(lines)


def pick_seeds(field, mechanisms, extra=6):
    """种子 = 六机制名 + 度数最高的前 extra 个节点（同度按名字），去重后固定顺序。"""
    deg = {}
    for (a, b) in field._w:  # noqa: SLF001  只读遍历
        deg[a] = deg.get(a, 0) + 1
        deg[b] = deg.get(b, 0) + 1
    hot = sorted(deg, key=lambda n: (-deg[n], n))[:extra]
    seeds = list(sorted(mechanisms))
    for n in hot:
        if n not in seeds:
            seeds.append(n)
    return seeds


def save(doc, path):
    """写盘（LF 换行、UTF-8 无 BOM、缩进 2）。"""
    d = os.path.dirname(os.path.abspath(path))
    if not os.path.isdir(d):
        os.makedirs(d)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=False) + "\n")
    return os.path.getsize(path)


def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def verify(doc):
    """复算自哈希并对边表做结构检查。"""
    expect = digest(doc)
    edges = doc.get("edges") or []
    keys = [(e["a"], e["b"]) for e in edges]
    return {
        "store_id": doc.get("store_id"),
        "sha256": doc.get("sha256"),
        "recomputed": expect,
        "hash_ok": expect == doc.get("sha256"),
        "edge_count": doc.get("edge_count"),
        "edges_len": len(edges),
        "count_ok": doc.get("edge_count") == len(edges),
        "key_order_ok": keys == sorted(keys),
        "weights_ok": all(0.0 < e["w"] <= CAP for e in edges),
        "ok": (expect == doc.get("sha256")
               and doc.get("store_id") == STORE_ID
               and doc.get("edge_count") == len(edges)
               and keys == sorted(keys)
               and all(0.0 < e["w"] <= CAP for e in edges)),
    }


def restore(doc, field):
    """把 edges 原样灌回一个空赫布场（不改 decay 之外的任何语义）。"""
    field._w = {}  # noqa: SLF001  复原即覆盖
    for e in doc.get("edges") or []:
        k = field._key(e["a"], e["b"])
        field._w[k] = round(float(e["w"]), ROUND)
    return len(field._w)


def topology(doc):
    """只给结构面（节点度、边密度），不参与验收数字。"""
    nodes = doc.get("nodes") or []
    edges = doc.get("edges") or []
    deg = {}
    for e in edges:
        deg[e["a"]] = deg.get(e["a"], 0) + 1
        deg[e["b"]] = deg.get(e["b"], 0) + 1
    return {
        "nodes": len(nodes),
        "edges": len(edges),
        "max_degree": max(deg.values()) if deg else 0,
        "density": round(len(edges) / max(1, len(nodes) * (len(nodes) - 1) / 2.0), 6),
    }
