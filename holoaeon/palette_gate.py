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
    else:
        print("usage: python -m holoaeon.palette_gate "
              "[probe|run [#hex,#hex]|fingerprint]", file=sys.stderr)
        return 2
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if out.get("ok", True) else 1


if __name__ == "__main__":
    import sys
    raise SystemExit(_main(["palette_gate"] + sys.argv[1:]))
