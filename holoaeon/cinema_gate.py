# -*- coding: utf-8 -*-
"""
CinemaGate —— 影像域编排（导演视觉风格域，ring18，V52）
================================================================================
源声明（诚实边界）：
  · 素材源 = 《导演视觉风格色卡》第 3-4 期 · 整合版（全 200 位），碳基
    2026-11-12 手动导出投喂（飞书文档 zip：md 速查 59798 B + 202 张
    色卡×剧照合成图）。结构化解析 200 条全字段非空、编号 001-200 连续、
    10 大类 × 20 位均匀（解析器实跑验证）。
  · 素材自身的诚实声明（原文采信）："剧照取自公共电影图库（FilmGrab /
    TMDB），逐张可溯源；没有拿 AI 图充数。"
  · 本批**不含**的内容（素材边界，如实声明）：
      ① 四套提示词文件（midjourney / conversational / video / SD）——在
         网盘完整 SKILL 包内，碳基未提供，本批不虚构其内容；
      ② 每位导演 10 色的具体色值（色名/色值/占比写在图片色卡里，md 速查
         只有标签词）——色值提取留待完整包到位后另批；
      ③ 202 张图片**不入 git 仓**（体积+版权）——指针纪律：仓内只登记
         结构化 JSON 索引 + 素材目录指针，图片留外部素材目录。

张量向量耦合（不变）：载体 = holoaeon.hypervector.HypervectorSpace
（sha256 确定性派生，V51/V51R 同一载体层）；中文 token 化真实复用
holoaeon.semvec.tokenize（ASCII 词 + 中文 2-gram + 词表，V22+ 确定性分词）。

装配纪律：装配不重写、零新依赖、纯标准库、neural=false、零网络。
"""

from __future__ import annotations

import hashlib
import io
import json
import math
import os
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .hypervector import HypervectorSpace
from .semvec import tokenize

# ---------------------------------------------------------------- 链位
CHAIN_POSITION = {
    "ring": 18,
    "layer": "operator",
    "domain": "影像（导演视觉风格域）",
    "batch": "V52",
    "upstream": [
        "semvec(确定性中文分词 tokenize·V22+ 先例)",
        "hypervector(Hyperspace 张量轴载体·V51/V51R 同层)",
        "concept_anatomy(概念解剖先例：风格句→结构)",
        "forge_gate(ring16 需求卡先例：素材→结构化登记)",
    ],
}

SEAL = "潮起开门，潮落闭嘴"

# 数据文件缺省位置（执行方落盘后生效；from_list 可脱离文件构造）
DATA_PATH = os.path.join("data", "cinema_directors.json")

# 十大类（与素材原文一致；运行时以数据内 categories 为准，此表为声明层）
DIRECTOR_CATEGORIES: Tuple[str, ...] = (
    "黑色悬疑与冷调惊悚",
    "霓虹黑色与赛博未来",
    "大地暖调与自然光诗意",
    "极简冷构与静观长镜",
    "巴洛克华丽与浓墨重彩",
    "超现实梦幻与心理畸变",
    "动作史诗与高饱和色彩",
    "动画奇幻与异想视觉",
    "浪漫柔光与复古色调",
    "东方美学与留白意境",
)

# 素材指针（图片不入仓，指针入账——413 席 KB 同款纪律）
ASSET_POINTERS = {
    "md_source": "《导演视觉风格色卡》第 3-4 期 · 整合版（全 200 位）.md"
                  "（59798 B，导出自飞书文档 wvybc6v6ip/docx/HgcMdqGjMoIzpdxNAO2cy8Vgngc）",
    "images": "图片和附件/ 202 张（001-200 位色卡×剧照合成图 + test×2 教程图），"
              "留外部素材目录 F:/doubaowork/.tmp_v52_in/，不入 git 仓",
    "remote_full_pack": "四套提示词文件与逐色色值在网盘完整 SKILL 包"
                        "（碳基未提供），本批不含、不虚构",
}


# ---------------------------------------------------------------- 数据层


@dataclass
class DirectorEntry:
    """导演条目（结构化登记位）。"""
    id: str            # "001"-"200"
    name: str          # 导演名
    category: str      # 十大类之一
    style: str         # 一句话风格句
    works: str         # 代表作（《》内原文）
    tags: List[str]    # 风格标签（、分割原文）

    def text_for_encoding(self) -> str:
        """张量编码用文本（类 + 风格句 + 标签，名字单独轴）。"""
        return " ".join([self.category, self.style, "、".join(self.tags)])

    def snapshot(self) -> Dict[str, Any]:
        return {"id": self.id, "name": self.name, "category": self.category,
                "works": self.works, "tags": self.tags}


class DirectorIndex:
    """导演索引：加载 / 查询 / 统计（纯数据层，无张量）。"""

    def __init__(self, directors: Sequence[DirectorEntry],
                 source: str = ""):
        self.directors: List[DirectorEntry] = list(directors)
        self.source = source
        self._by_id = {d.id: d for d in self.directors}
        self._by_name: Dict[str, List[DirectorEntry]] = {}
        for d in self.directors:
            self._by_name.setdefault(d.name, []).append(d)

    # -------------------------------------------------- 加载
    @classmethod
    def load(cls, path: Optional[str] = None) -> "DirectorIndex":
        p = path or DATA_PATH
        if not os.path.exists(p):
            raise FileNotFoundError("导演索引数据不存在: %s（执行方须先落盘"
                                    " data/cinema_directors.json）" % p)
        with io.open(p, "r", encoding="utf-8") as f:
            doc = json.load(f)
        entries = [DirectorEntry(
            id=str(e["id"]), name=e["name"], category=e["category"],
            style=e["style"], works=e["works"], tags=list(e["tags"]))
            for e in doc["directors"]]
        return cls(entries, source=doc.get("source", ""))

    @classmethod
    def from_list(cls, directors: Sequence[DirectorEntry]) -> "DirectorIndex":
        return cls(directors)

    # -------------------------------------------------- 查询
    def by_id(self, did: str) -> Optional[DirectorEntry]:
        return self._by_id.get(did)

    def by_name(self, name: str) -> List[DirectorEntry]:
        return list(self._by_name.get(name, []))

    def by_category(self, category: str) -> List[DirectorEntry]:
        return [d for d in self.directors if d.category == category]

    def categories(self) -> Dict[str, int]:
        stat: Dict[str, int] = {}
        for d in self.directors:
            stat[d.category] = stat.get(d.category, 0) + 1
        return dict(sorted(stat.items()))

    def count(self) -> int:
        return len(self.directors)

    def validate(self) -> Dict[str, Any]:
        """索引完整性：编号连续 / 类目在表 / 字段非空。"""
        problems: List[str] = []
        ids = [d.id for d in self.directors]
        n = len(ids)
        expected = ["%03d" % i for i in range(1, n + 1)]
        if ids != expected:
            problems.append("编号非 001-%03d 连续序" % n)
        for d in self.directors:
            if d.category not in DIRECTOR_CATEGORIES:
                problems.append("%s 类目越表: %s" % (d.id, d.category))
            for label, v in (("名字", d.name), ("风格句", d.style),
                             ("代表作", d.works)):
                if not str(v).strip():
                    problems.append("%s 空%s" % (d.id, label))
            if not d.tags:
                problems.append("%s 空标签" % d.id)
        return {"ok": not problems, "problems": problems[:10],
                "count": n, "categories": len(self.categories())}


# ---------------------------------------------------------------- 张量层


class StyleTensor:
    """风格张量：导演/查询文本 → hypervector（张量向量耦合不变）。

    编码（确定性，同参同张量）：
      · 类轴   = make("cat:" + category)
      · 名轴   = make("name:" + name)
      · 风格轴 = bundle(make("tok:" + t) for t in tokenize(风格句+标签))
      · 整体   = bundle(类轴, 风格轴)（名轴不混入——检索"像谁的风格"
                  不应被名字字面绑架；名轴供按名取回）
    检索：与全库逐一 cosine 排序（200 位规模线性扫即 0.1ms 级，无需索引）。
    """

    def __init__(self, index: DirectorIndex,
                 space: Optional[HypervectorSpace] = None):
        self.index = index
        self.space = space or HypervectorSpace()
        self._vecs: Dict[str, List[float]] = {}

    def encode_entry(self, entry: DirectorEntry) -> List[float]:
        if entry.id in self._vecs:
            return list(self._vecs[entry.id])
        toks = tokenize(entry.text_for_encoding())
        style_axis = self.space.bundle(
            [self.space.make("tok:" + t) for t in toks]) if toks \
            else [0.0] * self.space.dim
        vec = self.space.bundle(
            [self.space.make("cat:" + entry.category), style_axis])
        self._vecs[entry.id] = vec
        return list(vec)

    def encode_name(self, entry: DirectorEntry) -> List[float]:
        return self.space.make("name:" + entry.name)

    def encode_query(self, text: str, category: str = "",
                     cat_weight: float = 1.0) -> List[float]:
        """查询编码（V54 增强参数 cat_weight，默认 1.0 = V52 原行为）。

        cat_weight 语义（跨类目检索权重）：
          1.0  类轴等权入查询（V52 原行为，逐字节兼容）
          0.0  纯风格轴（跨类目自由探索——"像这种风格，不限门类"）
          >1.0 类目加权 boost（同类别优先，2.0 = 类轴贡献加倍）
        实现：normalize(Σ tok 轴 + cat_weight × cat 轴)——加权成分入
        bundle 线性组合（bundle 本义=归一化求和），与 V53 "占比入权重"
        同族：权重在数学结构里，不在检索后处理里。
        """
        toks = tokenize(text or "")
        style_terms = [self.space.make("tok:" + t) for t in toks]
        cat_axis = self.space.make("cat:" + category) if category else None
        if not style_terms and cat_axis is None:
            return [0.0] * self.space.dim
        acc = [0.0] * self.space.dim
        for v in style_terms:
            for i, x in enumerate(v):
                acc[i] += x
        if cat_axis is not None:
            for i, x in enumerate(cat_axis):
                acc[i] += cat_weight * x
        norm = math.sqrt(sum(x * x for x in acc))
        if norm:
            acc = [x / norm for x in acc]
        return acc

    def encode_entry_weighted(self, entry: DirectorEntry,
                              cat_weight: float = 1.0) -> List[float]:
        """条目查询向量（by_director 场景的 cat_weight 版）。

        库内向量 encode_entry 不动（cache 里的原始等权版）；仅查询侧重加权。
        cat_weight=1.0 时与 encode_entry 完全一致（含缓存路径）。
        """
        if cat_weight == 1.0:
            return self.encode_entry(entry)
        toks = tokenize(entry.text_for_encoding())
        style_axis = self.space.bundle(
            [self.space.make("tok:" + t) for t in toks]) if toks \
            else [0.0] * self.space.dim
        cat_axis = self.space.make("cat:" + entry.category)
        acc = [s + cat_weight * c for s, c in zip(style_axis, cat_axis)]
        norm = math.sqrt(sum(x * x for x in acc))
        return [x / norm for x in acc] if norm else acc

    def similar_by_text(self, text: str, category: str = "",
                        k: int = 5,
                        cat_weight: float = 1.0
                        ) -> List[Tuple[DirectorEntry, float]]:
        q = self.encode_query(text, category, cat_weight)
        return self._rank(q, k)

    def similar_by_director(self, entry: DirectorEntry,
                            k: int = 5,
                            cat_weight: float = 1.0
                            ) -> List[Tuple[DirectorEntry, float]]:
        """V54 增强参数 cat_weight（默认 1.0 = V52 原行为）。"""
        q = self.encode_entry_weighted(entry, cat_weight)
        return self._rank(q, k)

    def category_hit_rate(self, hits: List[Tuple["DirectorEntry", float]],
                         category: str) -> float:
        """Top 命中里同类别占比（cat_weight 效果的量化观察窗）。"""
        if not hits or not category:
            return 0.0
        n = sum(1 for d, _ in hits if d.category == category)
        return round(n / len(hits), 4)

    def _rank(self, query: List[float],
              k: int) -> List[Tuple[DirectorEntry, float]]:
        scored = []
        for d in self.index.directors:
            v = self.encode_entry(d)
            scored.append((d, self.space.cosine(query, v)))
        scored.sort(key=lambda t: -t[1])
        return scored[:k]


# ---------------------------------------------------------------- 总闸


class CinemaGate:
    """ring18 影像域总闸：索引完整性 + 张量闭环 + manifest。

    诚实边界：本域只做"结构化登记 + 张量检索"，不做图像生成、
    不含提示词文件内容、不含色值（素材边界如实入 manifest）。
    """

    def __init__(self, index: Optional[DirectorIndex] = None,
                 space: Optional[HypervectorSpace] = None):
        self.index = index if index is not None else self._load_default()
        self.tensor = StyleTensor(self.index, space=space)

    @staticmethod
    def _load_default() -> DirectorIndex:
        try:
            return DirectorIndex.load()
        except FileNotFoundError:
            # 无数据文件时构造空索引（probe 仍可跑通并如实报告）
            return DirectorIndex([], source="（数据未落盘）")

    def self_check(self) -> dict:
        checks: Dict[str, dict] = {}
        v = self.index.validate()
        checks["index"] = {
            "ok": v["ok"] and self.index.count() == 200,
            "count": v["count"], "categories": v["categories"],
            "problems": v["problems"],
        }
        # 类目均匀（10 类 × 20 位——素材实测结构）
        cats = self.index.categories()
        checks["categories"] = {
            "ok": len(cats) == 10 and all(c == 20 for c in cats.values()),
            "stat": cats,
        }
        # 张量闭环：随机取几位导演，自检索必须排第一且明显高于陌生查询
        ok_loop = True
        sample_ids = ("001", "141", "200")
        loop_report = []
        for sid in sample_ids:
            d = self.index.by_id(sid)
            if d is None:
                ok_loop = False
                continue
            top = self.tensor.similar_by_director(d, k=3)
            self_top = top[0][0].id == d.id
            # 用"完全无关文本"作负对照（家具说明书式文本）
            neg = self.tensor.similar_by_text(
                "操作系统数据库网络协议审计台账", k=1)
            gap = top[0][1] - (neg[0][1] if neg else 0.0)
            loop_report.append({"id": sid, "self_top": self_top,
                                "top_score": round(top[0][1], 4),
                                "negative_score": round(neg[0][1], 4)
                                if neg else None})
            if not self_top or gap <= 0:
                ok_loop = False
        checks["tensor_loop"] = {"ok": ok_loop, "samples": loop_report}
        # 检索闭环：风格文本查询应召回同类导演
        q = self.tensor.similar_by_text("霓虹冷蓝 暗夜城市 风格化暴力",
                                        category="霓虹黑色与赛博未来", k=3)
        same_cat = sum(1 for d, _ in q
                       if d.category == "霓虹黑色与赛博未来")
        checks["retrieval"] = {
            "ok": same_cat >= 2,
            "same_category_hits": same_cat, "k": 3,
            "top": [d.name for d, _ in q],
        }
        # 指针纪律：图片指针声明在位
        checks["asset_pointers"] = {
            "ok": ("images" in ASSET_POINTERS
                   and "不入 git 仓" in ASSET_POINTERS["images"]
                   and "未提供" in ASSET_POINTERS["remote_full_pack"]),
        }
        ok_all = all(c["ok"] for c in checks.values())
        return {"ok": ok_all, "checks": checks,
                "chain_position": CHAIN_POSITION, "seal": SEAL}

    def run(self, query: Optional[str] = None) -> dict:
        """总闸：自检 + 可选检索演示 + manifest 回执。"""
        sc = self.self_check()
        manifest = {
            "batch": CHAIN_POSITION["batch"],
            "ring": CHAIN_POSITION["ring"],
            "domain": CHAIN_POSITION["domain"],
            "generated_at": _now_iso(),
            "self_check": sc,
            "index_source": self.index.source,
            "artifacts": {},
            "asset_pointers": ASSET_POINTERS,
            "honesty": {
                "source": "《导演视觉风格色卡》第 3-4 期（飞书文档导出，"
                          "碳基 2026-11-12 投喂）",
                "stills_provenance": "公共电影图库 FilmGrab / TMDB（素材"
                                     "原文声明，逐张可溯源，无 AI 图充数）",
                "not_included": ["四套提示词文件（网盘完整包，未提供）",
                                 "逐色色值（在图片色卡内，本批不 OCR）",
                                 "202 张图片（指针纪律，不入 git 仓）"],
                "neural": False,
                "network": False,
                "new_dependencies": 0,
                "reuses": ["semvec.tokenize（确定性中文分词）",
                           "hypervector.HypervectorSpace（张量载体）"],
            },
            "seal": SEAL,
        }
        if sc["ok"]:
            manifest["artifacts"]["index_receipt"] = {
                "count": self.index.count(),
                "categories": self.index.categories()}
        if query:
            hits = self.tensor.similar_by_text(query, k=5)
            manifest["artifacts"]["query_demo"] = {
                "query": query,
                "hits": [{"id": d.id, "name": d.name,
                          "category": d.category, "score": round(s, 4)}
                         for d, s in hits]}
        return manifest


# ---------------------------------------------------------------- 工具


def _now_iso() -> str:
    import datetime
    return datetime.datetime.now().isoformat(timespec="seconds")


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def fingerprint() -> dict:
    return {
        "module": "cinema_gate",
        "ring": CHAIN_POSITION["ring"],
        "domain": CHAIN_POSITION["domain"],
        "batch": CHAIN_POSITION["batch"],
        "categories": list(DIRECTOR_CATEGORIES),
        "sha256": _sha256("cinema-gate-v1:" + SEAL),
        "seal": SEAL,
    }


def probe() -> dict:
    """轻量探针（不建大索引，用内置小样本跑通装配链）。"""
    demo = [
        DirectorEntry("001", "样例甲", DIRECTOR_CATEGORIES[0],
                      "冷蓝阴影与低调打光", "样例作品", ["冷调", "阴影"]),
        DirectorEntry("002", "样例乙", DIRECTOR_CATEGORIES[1],
                      "霓虹洋红与暗夜城市", "样例作品二", ["霓虹", "赛博"]),
    ]
    idx = DirectorIndex.from_list(demo)
    st = StyleTensor(idx)
    hits = st.similar_by_text("霓虹 暗夜 城市", k=2)
    return {"ok": hits[0][0].id == "002", "top": hits[0][0].name,
            "score": round(hits[0][1], 4), "seal": SEAL}


def _main(argv: List[str]) -> int:
    import sys
    cmd = argv[1] if len(argv) > 1 else "probe"
    if cmd == "probe":
        out = probe()
    elif cmd == "run":
        out = CinemaGate().run(query=argv[2] if len(argv) > 2 else None)
    elif cmd == "fingerprint":
        out = fingerprint()
    else:
        print("usage: python -m holoaeon.cinema_gate "
              "[probe|run [query]|fingerprint]", file=sys.stderr)
        return 2
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if out.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(_main(["cinema_gate"] + sys.argv[1:]))
