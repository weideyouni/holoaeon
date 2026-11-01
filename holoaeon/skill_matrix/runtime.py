# -*- coding: utf-8 -*-
"""
skill_matrix.runtime —— 跨线程运行时：一次调用走完 皮肤 → 语义 → 赫布 → 经络
================================================================================
对外只暴露两件事：
  · dispatch(query)        随时调用，一条请求一条回执（含封缄哈希）
  · dispatch_many(qs, w)   跨线程并发，逐条回执的"稳定视图"必须逐字相等
"挂载"只登记元数据技能（不 import、不执行外部脚本），故对内核零风险。
"""
from __future__ import annotations

import hashlib
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Iterable, List, Optional, Tuple

from . import index as Ix
from .mech import (CHANNELS, MECHANISMS, MECH_CN, HebbianField, Meridian,
                   semantic_overlap, shingles, skin_gate)

QUARTET_LENS: Dict[str, str] = {
    "P1_探微": "研究 创新 前沿 论文 实验 算法 假设 科学 认知",
    "P2_筑基": "工程 架构 性能 部署 基础设施 编译 分布式 算力",
    "P3_构弦": "多模态 产品 交互 生成 图像 视频 语音 体验 设计",
    "P4_持衡": "安全 合规 风险 审核 隐私 熔断 责任 伦理 对齐",
}

STABLE_FIELDS = ("verdict", "mechanism", "channel", "top", "seal")
_DOC_CHARS = 120


class MatrixRuntime:
    """技能矩阵运行时：索引常驻（预切 shingle），机制按需计算，全部确定性。"""

    def __init__(self, index: dict, decay: float = 0.02, capacity: int = 100) -> None:
        self.index = index
        self.rows = {r["name"]: r for r in index.get("skills", [])}
        self.field = HebbianField(decay)
        self.meridian = Meridian(capacity)
        self.lock = threading.Lock()
        self.calls = 0
        # 预切 shingle：只切 2/3 阶、正文截 120 字符，控制内存与耗时
        self._doc: Dict[str, set] = {
            n: shingles((n + " " + r["description"])[:_DOC_CHARS], (2, 3))
            for n, r in self.rows.items()
        }

    # ------------------------------------------------------------ 内部：一次打分
    def _rank(self, text: str, k: int = 3) -> Dict[str, object]:
        q = shingles(text, (2, 3))
        rows: List[Tuple[float, str]] = []
        best: Dict[str, Tuple[float, str]] = {}
        for name, doc in self._doc.items():
            if not q or not doc:
                sc = 0.0
            else:
                # 查询覆盖率：查询侧 shingle 有多少被该技能命中（比 Jaccard 更可读）
                sc = min(1.0, len(q & doc) / len(q))
            rows.append((round(sc, 5), name))
            m = self.rows[name]["mechanism"]
            if sc > best.get(m, (-1.0, ""))[0]:
                best[m] = (round(sc, 5), name)
        rows.sort(key=lambda t: (-t[0], t[1]))
        mech, mscore = MECHANISMS[0], -1.0
        for m in MECHANISMS:
            sc = best.get(m, (0.0, ""))[0]
            if sc > mscore:
                mech, mscore = m, sc
        return {"query": text, "mech": mech, "mech_score": round(max(0.0, mscore), 5),
                "top": [{"name": n, "score": s, "mechanism": self.rows[n]["mechanism"],
                         "domain": self.rows[n]["domain"]} for s, n in rows[:max(1, k)]],
                "mechanism_best": {m: {"score": v[0], "skill": v[1]} for m, v in best.items()}}

    # ------------------------------------------------------------ 一次调用
    def dispatch(self, query: str, lane: str = "read", permission: int = 0) -> dict:
        gate = skin_gate({"query": query, "lane": lane, "permission": permission})
        if gate["verdict"] != "PASS":
            return {"verdict": "REJECT", "layer": gate["layer"],
                    "trace": gate["trace"], "query": str(query)[:64]}
        ranked = self._rank(gate["query"], 3)
        mech = str(ranked["mech"])
        channel = CHANNELS[MECHANISMS.index(mech) % len(CHANNELS)]
        flow = self.meridian.flow(channel, 1)
        cands = ranked["top"]
        with self.lock:
            self.calls += 1
            if cands:
                self.field.co_activate(mech, cands[0]["name"], 1.0)
                pruned = self.field.decay_all()
            else:
                pruned = len(self.field._w)  # noqa: SLF001  只读计数
        seal = hashlib.sha256(
            (gate["seal"] + "|" + mech + "|" + channel + "|"
             + (cands[0]["name"] if cands else "-")).encode("utf-8")
        ).hexdigest()[:16]
        return {"verdict": "PASS" if flow["ok"] else "BLOCKED",
                "mechanism": mech, "mechanism_cn": MECH_CN[mech],
                "score": ranked["mech_score"], "channel": channel,
                "channel_used": flow.get("used"), "capacity": flow.get("capacity"),
                "top": cands[0]["name"] if cands else None,
                "candidates": cands, "hebbian_edges": pruned,
                "cost": gate["cost"], "seal": seal, "query": gate["query"][:64]}

    # ------------------------------------------------------------ 跨线程
    def dispatch_many(self, queries: Iterable[str], workers: int = 8) -> dict:
        qs = [q for q in queries]
        with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
            receipts = list(pool.map(self.dispatch, qs))
        return {"n": len(qs), "receipts": receipts,
                "all_pass": all(r["verdict"] in ("PASS", "BLOCKED") for r in receipts)}

    def concurrency_probe(self, query: str, n: int = 8) -> dict:
        """同一查询并发 n 次：稳定视图必须逐字相等（证明跨线程无数据竞争）。"""
        with ThreadPoolExecutor(max_workers=n) as pool:
            receipts = list(pool.map(self.dispatch, [query] * n))
        views = [{k: r[k] for k in STABLE_FIELDS} for r in receipts]
        first = views[0]
        identical = all(v == first for v in views)
        return {"n": n, "identical": identical, "view": first,
                "distinct_views": len({tuple(sorted(v.items())) for v in views})}

    # ------------------------------------------------------------ 四人组复核
    def quartet_review(self, task: str, top_k: int = 3) -> dict:
        """四透镜（探微/筑基/构弦/持衡）：各自在本任务下选自己的首选技能与机制。"""
        rows = []
        for persona, lens in QUARTET_LENS.items():
            r = self._rank(task + " " + lens, top_k)
            top = r["top"][0] if r["top"] else {"name": None, "mechanism": None, "score": 0.0}
            rows.append({"persona": persona, "lens": lens,
                         "mechanism": top["mechanism"], "mechanism_cn": MECH_CN.get(top["mechanism"], ""),
                         "lens_score": top["score"], "skills": r["top"]})
        rows.sort(key=lambda x: x["persona"])
        mechs = {x["mechanism"] for x in rows}
        return {"task": task, "panel": rows, "distinct_mechanisms": len(mechs),
                "note": "四透镜为确定性词面对齐，不代表原型人物实时观点；需人类终审"}

    # ------------------------------------------------------------ 挂载（元数据技能）
    def mount(self, kernel: object, prefix: str = "mx.", limit: int = 48) -> dict:
        """把矩阵条目以"只读元数据技能"挂进活跃内核，命名空间前缀隔离，可回滚。"""
        mounted = []
        rows = sorted(self.rows.values(), key=lambda r: r["name"])[:max(0, limit)]
        for r in rows:
            sname = prefix + r["name"]
            if kernel.skills.has(sname):
                continue
            payload = {"name": r["name"], "domain": r["domain"],
                       "mechanism": r["mechanism"], "lane": r["lane"]}

            def _probe(_q: str = "", _p: dict = payload) -> dict:
                return dict(_p)

            kernel.skills.register_fn(sname, _probe,
                                      description="矩阵元数据：%s（%s/%s）"
                                                  % (r["name"], r["mechanism"], r["domain"]),
                                      tags=["skill_matrix", r["mechanism"], r["domain"]],
                                      permissions=0, inputs={"q": "str"})
            mounted.append(sname)
        return {"mounted": len(mounted), "prefix": prefix, "names": mounted[:8]}

    # ------------------------------------------------------------ 总览
    def status(self) -> dict:
        return {"dirs_indexed": self.index.get("count"), "unique_skills": len(self.rows),
                "calls": self.calls, "digest": self.index.get("digest"),
                "stats": self.index.get("stats"),
                "hebbian_edges": len(self.field._w),  # noqa: SLF001
                "meridian": self.meridian.report()}


def load_runtime(index_path: str, *, decay: float = 0.02, capacity: int = 100) -> MatrixRuntime:
    index = Ix.load(index_path)
    if index is None:
        raise FileNotFoundError("技能索引不存在：%s（先跑 build_skill_matrix.py）" % index_path)
    return MatrixRuntime(index, decay=decay, capacity=capacity)
