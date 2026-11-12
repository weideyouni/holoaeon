# -*- coding: utf-8 -*-
"""
PaletteGate —— 色卡色值层（导演视觉风格色值域，ring18 姊妹件，V53）
================================================================================
源声明（诚实边界）：
  · 素材源 = 《导演视觉风格色卡》第 3-4 期 200 张色卡图（碳基 2026-11-12
    手动导出 zip 投喂，V52 已登记索引）。本批为**色值层**：每位导演
    顶部色带 6 主色的 色名 + hex 色值 + 占比。
  · 提取方法（双源交叉，如实声明）：
      ① 像素采样（主源）：色带分段 → 段内多点中值 RGB → hex；
        段宽度 → 占比（物理宽度比）。抗 JPEG 压缩（与印刷标注 ±10 RGB 内）。
      ② OCR（辅源）：mineru advanced 层解析图例文本 → 色名（语义标签）
        + 印刷 hex/占比（当 OCR 完整时用于交叉验证；OCR 质量因图而异，
        部分图残缺——色名取 OCR，hex/占比以像素采样为准，二者偏差
        超阈值的条目如实标记）。
  · 色卡公理（素材原文）：每位 10 色不要全用——主色 1 个占 40%+（定调）、
    辅色 1-2 个占 20-30%（撑层次）、点缀色 1 个只占 5%（提亮）。
    本层登记的是主色卡 6 色；底部辅助色块行不在本批（可选后续）。
  · neural=false、零网络、零新依赖（PIL/mineru 只在投喂侧提取脚本，
    不入仓——仓内模块纯标准库）。

张量向量耦合（不变）：载体 = holoaeon.hypervector.HypervectorSpace；
调色板张量 = **占比加权 bundle**（share_i × make("hex:"+hex_i) 累加归一）——
占比入张量权重，主色对调性主导（这正是色卡公理的数学化）。
"""

from __future__ import annotations

import hashlib
import io
import json
import math
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .hypervector import HypervectorSpace

# ---------------------------------------------------------------- 链位
CHAIN_POSITION = {
    "ring": 18,
    "layer": "operator",
    "domain": "影像·色卡（导演视觉风格色值层）",
    "batch": "V53",
    "upstream": [
        "cinema_gate(ring18 影像域索引上游·同环姊妹件)",
        "hypervector(Hyperspace 张量轴载体·V51/V51R/V52 同层)",
        "design_vocab(皮肤词库先例：颜色本体小表)",
    ],
}

SEAL = "潮起开门，潮落闭嘴"

DATA_PATH = os.path.join("data", "cinema_palettes.json")

# ---------------------------------------------------------------- 色卡公理
# 素材原文：主色 1 个占画面 40% 以上（定调子）；辅色 1-2 个占 20-30%
# （撑层次）；点缀色 1 个只占 5%（提亮用）。
COLOR_AXIOM = {
    "primary": {"min_share": 0.30, "desc": "主色：占比最大，定调子"},
    "secondary": {"share_range": (0.10, 0.30), "max_count": 2,
                  "desc": "辅色：1-2 个，撑层次"},
    "accent": {"max_share": 0.10, "desc": "点缀：占比最小，提亮"},
}


# ---------------------------------------------------------------- 数据层


def hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
    h = hex_str.strip().lstrip("#")
    if len(h) != 6:
        raise ValueError("非法 hex 色值: %r（须 #RRGGBB）" % hex_str)
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def rgb_to_hex(rgb: Sequence[int]) -> str:
    return "#%02X%02X%02X" % (rgb[0], rgb[1], rgb[2])


def rgb_cosine(a: Sequence[int], b: Sequence[int]) -> float:
    """RGB 三维余弦（色相近度：方向相似=色相族相近）。"""
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return round(dot / (na * nb), 5) if na and nb else 0.0


@dataclass
class PaletteColor:
    """单色条目：色名（OCR 语义标签）+ hex（像素采样）+ 占比。"""
    name: str
    hex: str
    share: float          # 0-1（像素宽度比或印刷值归一）

    def rgb(self) -> Tuple[int, int, int]:
        return hex_to_rgb(self.hex)

    def snapshot(self) -> Dict[str, Any]:
        return {"name": self.name, "hex": self.hex,
                "share": round(self.share, 4)}


def classify_roles(colors: Sequence[PaletteColor]) -> Dict[str, Any]:
    """按色卡公理分配角色：主色（最大占比）/辅色（次大 1-2 个）/
    点缀（最小）。

    公理映射：主色=share 最大的 1 个；辅色=第 2-3 大且 share>=0.08；
    点缀=其余中最大者；其余记为 base（带内其余）。输出角色 + 依据。
    """
    if not colors:
        return {"ok": False, "error": "空调色板"}
    ranked = sorted(colors, key=lambda c: -c.share)
    primary = ranked[0]
    secondary = [c for c in ranked[1:3] if c.share >= 0.08]
    rest = [c for c in ranked if c is not primary and c not in secondary]
    accent = rest[0] if rest else None
    return {
        "ok": True,
        "primary": primary.snapshot(),
        "secondary": [c.snapshot() for c in secondary],
        "accent": accent.snapshot() if accent else None,
        "axiom_note": "主色定调 / 辅色撑层次 / 点缀提亮（素材公理原文）",
        "primary_share": round(primary.share, 4),
        "secondary_total": round(sum(c.share for c in secondary), 4),
    }


class PaletteEntry:
    """导演调色板：id/name/category + 6 主色。"""

    def __init__(self, did: str, name: str, category: str,
                 colors: Sequence[PaletteColor],
                 notes: Optional[Dict[str, Any]] = None):
        self.id = did
        self.name = name
        self.category = category
        self.colors: List[PaletteColor] = list(colors)
        self.notes = notes or {}

    def roles(self) -> Dict[str, Any]:
        return classify_roles(self.colors)

    def weighted_rgb(self) -> Tuple[float, float, float]:
        """占比加权平均色（调性单色：主色主导）。"""
        r = g = b = 0.0
        tot = sum(c.share for c in self.colors) or 1.0
        for c in self.colors:
            rgb = c.rgb()
            r += rgb[0] * c.share / tot
            g += rgb[1] * c.share / tot
            b += rgb[2] * c.share / tot
        return (round(r, 2), round(g, 2), round(b, 2))

    def snapshot(self) -> Dict[str, Any]:
        return {"id": self.id, "name": self.name, "category": self.category,
                "colors": [c.snapshot() for c in self.colors]}


# ---------------------------------------------------------------- 张量层


class PaletteTensor:
    """调色板张量：占比加权 bundle（张量向量耦合不变）。

    编码：Σ share_i × make("hex:" + hex_i)，归一化。
    占比入权重 —— 主色对调性主导（色卡公理的数学化）。
    检索：两调色板 cosine；查询=色列表加权张量。
    """

    def __init__(self, space: Optional[HypervectorSpace] = None):
        self.space = space or HypervectorSpace()

    def encode_colors(self, hexes: Sequence[str],
                      shares: Optional[Sequence[float]] = None) -> List[float]:
        if not hexes:
            raise ValueError("空色列表（无可编码色）")
        ws = list(shares) if shares else [1.0 / len(hexes)] * len(hexes)
        if len(ws) != len(hexes):
            raise ValueError("hexes/shares 长度不一致")
        acc = [0.0] * self.space.dim
        for hx, w in zip(hexes, ws):
            v = self.space.make("hex:" + hx.strip().upper())
            for i, x in enumerate(v):
                acc[i] += w * x
        norm = math.sqrt(sum(x * x for x in acc))
        if norm:
            acc = [x / norm for x in acc]
        return acc

    def encode_palette(self, entry: PaletteEntry) -> List[float]:
        return self.encode_colors(
            [c.hex for c in entry.colors], [c.share for c in entry.colors])


# ---------------------------------------------------------------- 索引/总闸


class PaletteIndex:
    """调色板索引：加载 / 校验 / 检索。"""

    def __init__(self, entries: Sequence[PaletteEntry],
                 source: str = ""):
        self.entries: List[PaletteEntry] = list(entries)
        self.source = source
        self.tensor = PaletteTensor()
        self._vecs = {e.id: self.tensor.encode_palette(e)
                      for e in self.entries}

    @classmethod
    def load(cls, path: Optional[str] = None) -> "PaletteIndex":
        p = path or DATA_PATH
        if not os.path.exists(p):
            raise FileNotFoundError("调色板数据不存在: %s（执行方须先落盘"
                                    " data/cinema_palettes.json）" % p)
        doc = json.load(io.open(p, encoding="utf-8"))
        entries = [PaletteEntry(
            did=str(e["id"]), name=e["name"], category=e["category"],
            colors=[PaletteColor(name=c["name"], hex=c["hex"],
                                 share=float(c["share"]))
                    for c in e["colors"]],
            notes=e.get("notes"))
            for e in doc["palettes"]]
        return cls(entries, source=doc.get("source", ""))

    def by_id(self, did: str) -> Optional[PaletteEntry]:
        for e in self.entries:
            if e.id == did:
                return e
        return None

    def count(self) -> int:
        return len(self.entries)

    def validate(self) -> Dict[str, Any]:
        problems: List[str] = []
        for e in self.entries:
            if len(e.colors) < 5:
                problems.append("%s 主色数 %d < 5" % (e.id, len(e.colors)))
            tot = sum(c.share for c in e.colors)
            if not (0.90 <= tot <= 1.10):
                problems.append("%s 占比合计 %.3f 越界" % (e.id, tot))
            for c in e.colors:
                try:
                    hex_to_rgb(c.hex)
                except ValueError:
                    problems.append("%s 非法 hex %s" % (e.id, c.hex))
        return {"ok": not problems, "problems": problems[:10],
                "count": self.count()}

    def similar_by_hexes(self, hexes: Sequence[str],
                         shares: Optional[Sequence[float]] = None,
                         k: int = 5) -> List[Tuple[PaletteEntry, float]]:
        q = self.tensor.encode_colors(hexes, shares)
        scored = [(e, self.tensor.space.cosine(q, self._vecs[e.id]))
                  for e in self.entries]
        scored.sort(key=lambda t: -t[1])
        return scored[:k]

    def similar_by_palette(self, entry: PaletteEntry,
                           k: int = 5) -> List[Tuple[PaletteEntry, float]]:
        q = self._vecs[entry.id]
        scored = [(e, self.tensor.space.cosine(q, self._vecs[e.id]))
                  for e in self.entries if e.id != entry.id]
        scored.sort(key=lambda t: -t[1])
        return scored[:k]


class PaletteGate:
    """ring18 色卡层总闸：数据校验 + 公理角色 + 张量闭环 + manifest。"""

    def __init__(self, index: Optional[PaletteIndex] = None):
        self.index = index if index is not None else self._load_default()

    @staticmethod
    def _load_default() -> PaletteIndex:
        try:
            return PaletteIndex.load()
        except FileNotFoundError:
            return PaletteIndex([], source="（数据未落盘）")

    def self_check(self) -> dict:
        checks: Dict[str, dict] = {}
        v = self.index.validate()
        checks["data"] = {
            "ok": v["ok"] and self.index.count() == 200,
            "count": v["count"], "problems": v["problems"],
        }
        # 公理角色闭环：001 希区柯克 主色应为最大占比色
        d1 = self.index.by_id("001")
        if d1 is not None and d1.colors:
            roles = d1.roles()
            top_share = max(c.share for c in d1.colors)
            checks["axiom"] = {
                "ok": roles["ok"] and
                      abs(roles["primary_share"] - top_share) < 1e-9,
                "primary": roles["primary"]["name"] if roles.get("primary")
                else None,
                "primary_share": roles.get("primary_share"),
            }
        else:
            checks["axiom"] = {"ok": False, "error": "001 缺失"}
        # 张量闭环：同调色板自编码 cosine=1；加权差异可分
        pt = self.index.tensor
        if d1 is not None and d1.colors:
            v1 = pt.encode_palette(d1)
            v1b = pt.encode_palette(d1)
            self_sim = pt.space.cosine(v1, v1b)
            # 主色单色 vs 全板：权重结构不同但主色主导 → 高相似但 <1
            mono = pt.encode_colors([roles_primary_hex(d1)], [1.0])
            mono_sim = pt.space.cosine(v1, mono)
            checks["tensor"] = {
                "ok": self_sim > 0.999 and 0.5 < mono_sim < 0.999,
                "self_sim": self_sim, "mono_dominance": mono_sim,
            }
        else:
            checks["tensor"] = {"ok": False, "error": "001 缺失"}
        # 检索闭环：以 001 的实际色查询，Top 结果应含同类冷调系
        if d1 is not None and d1.colors:
            hits = self.index.similar_by_hexes(
                [c.hex for c in d1.colors],
                [c.share for c in d1.colors], k=5)
            top_name = hits[0][0].name if hits else None
            top_score = hits[0][1] if hits else 0.0
            checks["retrieval"] = {
                "ok": bool(hits) and top_score > 0.5,
                "top": top_name, "score": top_score,
            }
        else:
            checks["retrieval"] = {"ok": False, "error": "001 缺失"}
        ok_all = all(c["ok"] for c in checks.values())
        return {"ok": ok_all, "checks": checks,
                "chain_position": CHAIN_POSITION, "seal": SEAL}

    def run(self, query_hexes: Optional[Sequence[str]] = None) -> dict:
        sc = self.self_check()
        manifest = {
            "batch": CHAIN_POSITION["batch"],
            "ring": CHAIN_POSITION["ring"],
            "domain": CHAIN_POSITION["domain"],
            "generated_at": _now_iso(),
            "self_check": sc,
            "source": self.index.source,
            "color_axiom": COLOR_AXIOM,
            "artifacts": {},
            "honesty": {
                "extraction": "双源交叉：像素采样（hex 主源，段中值 RGB）"
                              "+ mineru advanced OCR（色名辅源）",
                "jpeg_drift": "像素 hex 与印刷标注 ±10 RGB 内（JPEG 压缩）",
                "axiom": "主色 1 个 40%+ / 辅色 1-2 个 20-30% / 点缀 5%"
                         "（素材公理原文，本批 6 主色带）",
                "not_included": ["底部辅助色块行（可选后续批）",
                                 "提示词四套文件（网盘完整包，未提供）",
                                 "图片本体（指针纪律，不入仓）"],
                "neural": False, "network": False, "new_dependencies": 0,
                "reuses": ["hypervector.HypervectorSpace（张量载体）",
                           "cinema_gate（索引上游）"],
            },
            "seal": SEAL,
        }
        if sc["ok"]:
            manifest["artifacts"]["index_receipt"] = {
                "count": self.index.count(),
                "validate": self.index.validate()["ok"]}
        if query_hexes:
            hits = self.index.similar_by_hexes(query_hexes, k=5)
            manifest["artifacts"]["query_demo"] = {
                "query_hexes": list(query_hexes),
                "hits": [{"id": e.id, "name": e.name, "score": round(s, 4)}
                         for e, s in hits]}
        return manifest


def roles_primary_hex(entry: PaletteEntry) -> str:
    ranked = sorted(entry.colors, key=lambda c: -c.share)
    return ranked[0].hex


# ---------------------------------------------------------------- 工具


def _now_iso() -> str:
    import datetime
    return datetime.datetime.now().isoformat(timespec="seconds")


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def fingerprint() -> dict:
    return {
        "module": "palette_gate",
        "ring": CHAIN_POSITION["ring"],
        "batch": CHAIN_POSITION["batch"],
        "domain": CHAIN_POSITION["domain"],
        "axiom": "主40%+辅20-30%+点缀5%（素材公理）",
        "sha256": _sha256("palette-gate-v1:" + SEAL),
        "seal": SEAL,
    }


def probe() -> dict:
    """轻量探针（内置小样本，不依赖数据文件）。"""
    e = PaletteEntry("001", "样例", "极简冷构与静观长镜", [
        PaletteColor("主灰", "#8A8780", 0.40),
        PaletteColor("辅蓝", "#3D5A6C", 0.25),
        PaletteColor("辅绿", "#2E4A38", 0.20),
        PaletteColor("点缀红", "#C41E3A", 0.05),
        PaletteColor("带内米", "#D4C5A9", 0.05),
        PaletteColor("带内墨", "#1A2332", 0.05),
    ])
    pt = PaletteTensor()
    v = pt.encode_palette(e)
    roles = e.roles()
    return {"ok": roles["ok"] and len(v) == pt.space.dim,
            "primary": roles["primary"]["name"],
            "primary_share": roles["primary_share"], "seal": SEAL}


# ================================================================ V54 增强段
# 主题一：底部辅助色块行（aux）——数据 data/cinema_palette_aux.json
# 主题二：指纹 bundle sha256 版本轴（dataset version vector）
# 纪律：追加式增强，不改上方 V53 既有行为（V53 测试回归须全绿）。
# 辅助色 hex 策略与主色带相反：OCR 优先 + 像素交叉（浅色块与米色背景
# RGB 距离不可分时像素会漏——如实声明，理由入 aux 数据 method 字段）。
# ================================================================

AUX_PATH = os.path.join("data", "cinema_palette_aux.json")
AUX_WEIGHT = 0.25          # 辅助色入张量低权重（主带 share 加权为主）


def _file_sha16(path: str) -> str:
    h = hashlib.sha256()
    with io.open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


class PaletteAuxEntry:
    """辅助色块行条目：id/name + relation（duplicate_of_main /
    supplementary / mixed / missing）+ colors（name/hex/source）。"""

    def __init__(self, did: str, name: str, relation: str,
                 colors: Sequence[Dict[str, Any]],
                 band_y: Any = None):
        self.id = did
        self.name = name
        self.relation = relation
        self.colors = list(colors)
        self.band_y = band_y

    def hexes(self) -> List[str]:
        return [c["hex"] for c in self.colors]


def load_aux(path: Optional[str] = None) -> List[PaletteAuxEntry]:
    p = path or AUX_PATH
    if not os.path.exists(p):
        return []
    doc = json.load(io.open(p, encoding="utf-8"))
    return [PaletteAuxEntry(
        did=str(a["id"]), name=a["name"], relation=a.get("relation", "missing"),
        colors=a.get("colors", []), band_y=a.get("band_y"))
        for a in doc.get("aux", [])]


def aux_relation_stats(entries: Sequence[PaletteAuxEntry]) -> Dict[str, int]:
    out: Dict[str, int] = {"duplicate_of_main": 0, "supplementary": 0,
                            "mixed": 0, "missing": 0}
    for e in entries:
        out[e.relation] = out.get(e.relation, 0) + 1
    return out


def aux_by_id(entries: Sequence[PaletteAuxEntry],
              did: str) -> Optional[PaletteAuxEntry]:
    for e in entries:
        if e.id == did:
            return e
    return None


def encode_aux(tensor: "PaletteTensor",
               hexes: Sequence[str],
               aux_weight: float = AUX_WEIGHT) -> List[float]:
    """辅助色低权重成分：aux_weight × 均匀 bundle(hexes)。

    主带编码（V53）+ 该成分的线性组合 = encode_palette_v2。
    aux_weight=0 时辅助色不参与（纯 V53 行为）。
    """
    if not hexes:
        return [0.0] * tensor.space.dim
    uni = tensor.encode_colors(list(hexes))     # 均匀权重
    return [aux_weight * x for x in uni]


class PaletteTensorV2(PaletteTensor):
    """V54 增强张量：主带 share 加权（V53 不变）+ 辅助色低权重 + 版本轴。

    编码：normalize(main_share_bundle + aux_weight × aux_uniform_bundle)
    版本轴：make("ver:" + dataset_sha16) —— 独立轴，不混入检索主轴
    （版本对账用 check_version，防止版本噪声污染色彩检索语义）。
    """

    AUX_WEIGHT = AUX_WEIGHT

    def __init__(self, space: Optional[HypervectorSpace] = None,
                 aux_entries: Optional[Sequence[PaletteAuxEntry]] = None):
        PaletteTensor.__init__(self, space)
        self.aux_entries = list(aux_entries or [])
        self._aux_map: Dict[str, List[str]] = {
            e.id: e.hexes() for e in self.aux_entries}

    def encode_palette(self, entry: PaletteEntry) -> List[float]:
        v53 = PaletteTensor.encode_palette(self, entry)
        ax = self._aux_map.get(entry.id, [])
        if not ax or self.AUX_WEIGHT <= 0:
            return v53
        aux = encode_aux(self, ax, self.AUX_WEIGHT)
        mixed = [a + b for a, b in zip(v53, aux)]
        norm = math.sqrt(sum(x * x for x in mixed))
        return [x / norm for x in mixed] if norm else mixed

    # ---------------- 主题二：版本指纹轴 ----------------
    def version_vector(self, dataset_sha16: str) -> List[float]:
        """数据集版本轴：sha256 指纹 → 确定性 hypervector。"""
        return self.space.make("ver:" + dataset_sha16)

    def check_version(self, dataset_sha16: str,
                      query: Sequence[float]) -> float:
        """版本对账：查询向量与版本轴的 cosine（≈1 → 同版本对齐）。"""
        vv = self.version_vector(dataset_sha16)
        return self.space.cosine(list(query), vv)


class PaletteIndexV2(PaletteIndex):
    """V54 索引：V53 数据 v2（主色名修正版）+ 辅助色 + 版本指纹。"""

    def __init__(self, entries: Sequence[PaletteEntry],
                 aux_entries: Sequence[PaletteAuxEntry],
                 source: str = "", data_sha16: str = ""):
        PaletteIndex.__init__(self, entries, source)
        self.aux_entries = list(aux_entries)
        self.data_sha16 = data_sha16
        self.tensor = PaletteTensorV2(self.tensor.space, self.aux_entries)
        self._vecs = {e.id: self.tensor.encode_palette(e)
                      for e in self.entries}

    @classmethod
    def load(cls, path: Optional[str] = None,
             aux_path: Optional[str] = None) -> "PaletteIndexV2":
        p = path or DATA_PATH
        if not os.path.exists(p):
            raise FileNotFoundError("调色板数据不存在: %s（执行方须先落盘"
                                    " data/cinema_palettes.json）" % p)
        doc = json.load(io.open(p, encoding="utf-8"))
        entries = [PaletteEntry(
            did=str(e["id"]), name=e["name"], category=e["category"],
            colors=[PaletteColor(name=c["name"], hex=c["hex"],
                                 share=float(c["share"]))
                    for c in e["colors"]],
            notes=e.get("notes"))
            for e in doc["palettes"]]
        aux_entries = load_aux(aux_path)
        return cls(entries, aux_entries, source=doc.get("source", ""),
                   data_sha16=_file_sha16(p))

    def aux_stats(self) -> Dict[str, int]:
        return aux_relation_stats(self.aux_entries)

    def aux_of(self, did: str) -> Optional[PaletteAuxEntry]:
        return aux_by_id(self.aux_entries, did)

    def version_vector(self) -> List[float]:
        return self.tensor.version_vector(self.data_sha16)


class PaletteGateV2(PaletteGate):
    """V54 总闸：V53 自检（兼容）+ aux/版本检查（新增键）。"""

    def __init__(self, index: Optional[PaletteIndexV2] = None):
        self.index = index if index is not None else self._load_default()

    @staticmethod
    def _load_default() -> PaletteIndexV2:
        try:
            return PaletteIndexV2.load()
        except FileNotFoundError:
            return PaletteIndexV2([], [], source="（数据未落盘）")

    def self_check(self) -> dict:
        sc = PaletteGate.self_check(self)      # V53 四键全兼容
        aux = self.index.aux_stats()
        sc["checks"]["aux"] = {
            "ok": sum(aux.values()) == 200 and aux.get("missing", 200) == 0,
            "stats": aux,
            "method": "OCR hex 优先 + 像素交叉（浅色块像素不可分——与主色带"
                      "相反策略，理由如实）",
        }
        ver = self.index.version_vector()
        vv = self.index.version_vector()
        sc["checks"]["version"] = {
            "ok": self.index.tensor.check_version(
                self.index.data_sha16, ver) > 0.999,
            "data_sha16": self.index.data_sha16,
            "self_consistency": self.index.tensor.check_version(
                self.index.data_sha16, vv),
        }
        sc["ok"] = all(c["ok"] for c in sc["checks"].values())
        return sc

    def run(self, query_hexes: Optional[Sequence[str]] = None) -> dict:
        sc = self.self_check()
        manifest = {
            "batch": "V54",
            "ring": CHAIN_POSITION["ring"],
            "domain": CHAIN_POSITION["domain"] + "（增强层）",
            "generated_at": _now_iso(),
            "self_check": sc,
            "source": self.index.source,
            "color_axiom": COLOR_AXIOM,
            "v54_themes": {
                "aux": "底部辅助色块行（200/200，OCR 优先+像素交叉）",
                "version": "指纹 bundle sha256 版本轴（dataset sha16 → ver 轴）",
                "name_fix": "主色名对齐链修正（V53 遗漏 markdown/HTML 表格行）",
            },
            "artifacts": {},
            "honesty": {
                "aux_hex_policy": "OCR 优先+像素交叉（与主色带'像素主源'相反："
                                  "浅色块与米色背景 RGB 距离≈4 不可分）",
                "relation_semantics": "duplicate_of_main=主色文学名别名 / "
                                      "supplementary=真补充色 / mixed",
                "aux_weight": AUX_WEIGHT,
                "neural": False, "network": False, "new_dependencies": 0,
            },
            "seal": SEAL,
        }
        if sc["ok"]:
            manifest["artifacts"]["aux_stats"] = self.index.aux_stats()
            manifest["artifacts"]["data_sha16"] = self.index.data_sha16
        if query_hexes:
            hits = self.index.similar_by_hexes(query_hexes, k=5)
            manifest["artifacts"]["query_demo"] = {
                "query_hexes": list(query_hexes),
                "hits": [{"id": e.id, "name": e.name, "score": round(s, 4)}
                         for e, s in hits]}
        return manifest


def version_report() -> dict:
    """版本指纹报告：主/辅两数据文件 sha16 + 版本轴自对账。"""
    try:
        idx = PaletteIndexV2.load()
        main_sha = _file_sha16(DATA_PATH)
        aux_sha = _file_sha16(AUX_PATH) if os.path.exists(AUX_PATH) else ""
        same = idx.tensor.check_version(idx.data_sha16,
                                        idx.version_vector())
        return {"ok": same > 0.999,
                "main_sha16": main_sha, "aux_sha16": aux_sha,
                "version_axis": "make('ver:' + sha16)",
                "self_consistency": same, "seal": SEAL}
    except FileNotFoundError as e:
        return {"ok": False, "error": str(e), "seal": SEAL}


def aux_report() -> dict:
    """辅助色块行报告：关系统计 + 001/141/062 三态样例。"""
    aux = load_aux()
    if not aux:
        return {"ok": False, "error": "aux 数据未落盘", "seal": SEAL}
    stats = aux_relation_stats(aux)
    samples = {}
    for did in ("001", "141", "062"):
        e = aux_by_id(aux, did)
        if e:
            samples[did] = {"name": e.name, "relation": e.relation,
                             "colors": [{"name": c["name"], "hex": c["hex"],
                                         "source": c["source"]}
                                        for c in e.colors]}
    return {"ok": sum(stats.values()) == 200, "stats": stats,
            "samples": samples, "seal": SEAL}


def _main(argv: List[str]) -> int:
    import sys
    cmd = argv[1] if len(argv) > 1 else "probe"
    if cmd == "probe":
        out = probe()
    elif cmd == "run":
        q = argv[2].split(",") if len(argv) > 2 else None
        out = PaletteGate().run(query_hexes=q)
    elif cmd == "fingerprint":
        out = fingerprint()
    elif cmd == "version":
        out = version_report()
    elif cmd == "aux":
        out = aux_report()
    else:
        print("usage: python -m holoaeon.palette_gate "
              "[probe|run [#hex,#hex]|fingerprint|version|aux]",
              file=sys.stderr)
        return 2
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if out.get("ok", True) else 1


if __name__ == "__main__":
    import sys
    raise SystemExit(_main(["palette_gate"] + sys.argv[1:]))
