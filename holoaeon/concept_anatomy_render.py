# -*- coding: utf-8 -*-
"""V21 概念解剖器·图像渲染器系列（concept_anatomy_render）。

把 ConceptAnatomizer().anatomize() 的结构化结果渲染成"像样的图"（SVG）：
  render_explosion   爆炸图：零件沿中轴展开 + 数字编号引线 + 成品对照区
  render_annotated   标注图：横截面示意 + 引线文字标注 + 关键部位放大细节
  render_legend      图例图：维度色语义 + 层次说明 + 零件清单
  render_diagram     结构图：等距投影增强版（大画布 + 调色板 + 序号）

加载协议（插件化注册，与 packs 扩展包机制同构）：
  RENDER_REGISTRY[name] = {"fn": fn, "desc": desc}
  register_render(name, fn, desc) / load_render(name)（未注册回落 diagram）
  render(anatomy, tokens) —— 统一协议入口

纯标准库、确定性、零 LLM 依赖。
"""
from __future__ import annotations

import sys
from typing import Callable, Dict, List, Optional

# ---- 图像 Token 默认值（追加进 DESIGN_TOKENS 的 5 个图像 Token） ----
DEFAULT_TOKENS: Dict[str, object] = {
    "img_style": "diagram",      # explosion / annotated / legend / diagram
    "img_palette": "工业蓝",      # 工业蓝 / 线稿黑白 / 全息四色
    "img_axis": "vertical",      # vertical / horizontal
    "img_annotate": True,        # 引线编号开关
    "img_compare": True,         # 成品对照区开关
}

_PALETTES: Dict[str, Dict[str, str]] = {
    "工业蓝": {"bg": "#fbfdff", "text": "#1f3a5f", "line": "#2b5ea7",
              "accent": "#d97706", "comp": "#e8f1fb", "node": "#2b5ea7"},
    "线稿黑白": {"bg": "#ffffff", "text": "#111111", "line": "#333333",
               "accent": "#555555", "comp": "#f4f4f4", "node": "#111111"},
    "全息四色": {"bg": "#1a1a2e", "text": "#e0e0e0", "line": "#7a6ff0",
               "accent": "#e5484d", "comp": "#2a2a4a", "node": "#7a6ff0"},
}

W, H = 800, 480


def _palette(tokens: Dict[str, object]) -> Dict[str, str]:
    return _PALETTES.get(str(tokens.get("img_palette", "工业蓝")),
                         _PALETTES["工业蓝"])


def _extract(anatomy: Dict) -> Dict:
    """从 anatomize() 结果中兼容提取 concept / components / mechanism。"""
    concept = str(anatomy.get("concept") or "未知概念")
    mechanism = ""
    comps: List[str] = []
    inner = anatomy.get("anatomy") or {}
    for key in ("components_sorted", "components"):
        got = inner.get(key)
        if got:
            for c in got:
                if isinstance(c, dict):
                    name = c.get("name") or c.get("label")
                    if name:
                        comps.append(str(name))
                else:
                    comps.append(str(c))
            if comps:
                break
    mechanism = str(inner.get("mechanism") or
                    (anatomy.get("output") or {}).get("mechanism") or "")
    if not comps:
        comps = ["组件A", "组件B", "组件C"]
    return {"concept": concept, "components": comps, "mechanism": mechanism}


def _svg_head(pal: Dict[str, str], title: str, w: int = W, h: int = H) -> List[str]:
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" style="background:{pal["bg"]}">',
            f'<text x="24" y="32" fill="{pal["text"]}" font-size="20" '
            f'font-family="monospace" font-weight="bold">{title}</text>']


# ---- 渲染器 1：爆炸图 ----

def render_explosion(anatomy: Dict, tokens: Dict[str, object]) -> str:
    d = _extract(anatomy)
    pal = _palette(tokens)
    axis = str(tokens.get("img_axis", "vertical"))
    annotate = bool(tokens.get("img_annotate", True))
    compare = bool(tokens.get("img_compare", True))
    n = len(d["components"])
    parts = _svg_head(pal, f"概念爆炸图：{d['concept']}")
    if axis == "horizontal":
        # 沿水平轴展开
        y = 200
        step = min(120, (W - 120) // max(n, 1))
        for i, comp in enumerate(d["components"]):
            x = 100 + i * step
            parts.append(f'<rect x="{x}" y="{y-14}" width="60" height="28" rx="4" '
                         f'fill="{pal["comp"]}" stroke="{pal["line"]}" stroke-width="1.2"/>')
            if annotate:
                parts.append(f'<circle cx="{x+4}" cy="{y-10}" r="8" fill="{pal["accent"]}"/>'
                             f'<text x="{x+4}" y="{y-7}" fill="#fff" font-size="8" '
                             f'text-anchor="middle" font-family="monospace">{i+1}</text>')
            parts.append(f'<text x="{x+30}" y="{y+40}" fill="{pal["text"]}" font-size="11" '
                         f'text-anchor="middle" font-family="monospace">{comp}</text>')
            if i + 1 < n:
                parts.append(f'<line x1="{x+68}" y1="{y}" x2="{x+step}" y2="{y}" '
                             f'stroke="{pal["line"]}" stroke-dasharray="4,3"/>')
    else:
        # 沿垂直中轴展开（默认）
        cx = W // 2
        step = min(52, (H - 150) // max(n, 1))
        y0 = 70
        for i, comp in enumerate(d["components"]):
            y = y0 + i * step
            parts.append(f'<rect x="{cx-26}" y="{y-12}" width="52" height="24" rx="4" '
                         f'fill="{pal["comp"]}" stroke="{pal["line"]}" stroke-width="1.2"/>')
            if annotate:
                parts.append(f'<circle cx="{cx-16}" cy="{y-8}" r="9" fill="{pal["accent"]}"/>'
                             f'<text x="{cx-16}" y="{y-5}" fill="#fff" font-size="9" '
                             f'text-anchor="middle" font-family="monospace">{i+1}</text>')
            parts.append(f'<text x="{cx+34}" y="{y+4}" fill="{pal["text"]}" font-size="12" '
                         f'font-family="monospace">{comp}</text>')
            if i + 1 < n:
                parts.append(f'<line x1="{cx}" y1="{y+14}" x2="{cx}" y2="{y+step-14}" '
                             f'stroke="{pal["line"]}" stroke-dasharray="4,3"/>')
    if compare:
        yc = H - 58
        parts.append(f'<rect x="40" y="{yc}" width="{W-80}" height="44" rx="6" '
                     f'fill="none" stroke="{pal["line"]}" stroke-dasharray="6,4"/>')
        parts.append(f'<rect x="{W//2-70}" y="{yc+10}" width="140" height="24" rx="10" '
                     f'fill="{pal["comp"]}" stroke="{pal["node"]}" stroke-width="1.4"/>')
        parts.append(f'<text x="{W//2}" y="{yc+27}" fill="{pal["text"]}" font-size="11" '
                     f'text-anchor="middle" font-family="monospace">成品对照（组装态）</text>')
        parts.append(f'<text x="56" y="{yc-6}" fill="{pal["accent"]}" font-size="10" '
                     f'font-family="monospace">图例：① 零件沿轴分解 ② 装配回成品</text>')
    parts.append(f'<text x="24" y="{H-20}" fill="{pal["text"]}" font-size="10" '
                 f'font-family="monospace">components: {n} | axis: {axis} | '
                 f'palette: {tokens.get("img_palette")}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


# ---- 渲染器 2：标注图 ----

def render_annotated(anatomy: Dict, tokens: Dict[str, object]) -> str:
    d = _extract(anatomy)
    pal = _palette(tokens)
    n = len(d["components"])
    parts = _svg_head(pal, f"横截面标注图：{d['concept']}")
    # 主体横截面条（中部）
    bar_y = 210
    parts.append(f'<rect x="140" y="{bar_y}" width="{W-280}" height="60" rx="8" '
                 f'fill="{pal["comp"]}" stroke="{pal["line"]}" stroke-width="1.6"/>')
    parts.append(f'<text x="{W//2}" y="{bar_y+34}" fill="{pal["text"]}" font-size="13" '
                 f'text-anchor="middle" font-family="monospace">主体横截面：{d["concept"]}</text>')
    # 引线标注：左右交替
    for i, comp in enumerate(d["components"]):
        left = i % 2 == 0
        tx = 90 if left else W - 90
        lx = (W - 280) // 2 + 140 if left else W - 140 - (W - 280) // 2
        ly = bar_y + 30 + (i % 3) * 10
        parts.append(f'<line x1="{lx}" y1="{ly}" x2="{tx}" y2="{bar_y-40-(i//2)*30}" '
                     f'stroke="{pal["line"]}" stroke-width="1"/>')
        parts.append(f'<text x="{tx}" y="{bar_y-46-(i//2)*30}" fill="{pal["accent"]}" '
                     f'font-size="11" text-anchor="middle" font-family="monospace">{i+1}.{comp}</text>')
    # 放大细节框（右下）
    fx, fy, fw, fh = W - 240, 300, 210, 120
    parts.append(f'<rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" rx="6" '
                 f'fill="none" stroke="{pal["line"]}" stroke-dasharray="4,3"/>')
    parts.append(f'<text x="{fx+10}" y="{fy+20}" fill="{pal["accent"]}" font-size="10" '
                 f'font-family="monospace">放大细节：{d["components"][0] if n else ""}</text>')
    parts.append(f'<circle cx="{fx+60}" cy="{fy+70}" r="18" fill="{pal["comp"]}" '
                 f'stroke="{pal["node"]}" stroke-width="1.6"/>')
    parts.append(f'<text x="{fx+10}" y="{fy+105}" fill="{pal["text"]}" font-size="9" '
                 f'font-family="monospace">关键部件特写示意</text>')
    parts.append(f'<text x="24" y="{H-20}" fill="{pal["text"]}" font-size="10" '
                 f'font-family="monospace">annotated | components: {n}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


# ---- 渲染器 3：图例图 ----

def render_legend(anatomy: Dict, tokens: Dict[str, object]) -> str:
    d = _extract(anatomy)
    pal = _palette(tokens)
    parts = _svg_head(pal, f"图例：{d['concept']}")
    legend_items = [
        ("主件", pal["node"], "核心载体"),
        ("零件", pal["comp"], "组成部件"),
        ("标注", pal["accent"], "编号/引线"),
    ]
    y = 80
    for name, color, note in legend_items:
        parts.append(f'<rect x="60" y="{y}" width="26" height="18" rx="3" '
                     f'fill="{color}"/>')
        parts.append(f'<text x="100" y="{y+14}" fill="{pal["text"]}" font-size="12" '
                     f'font-family="monospace">{name} —— {note}</text>')
        y += 40
    # 零件清单
    parts.append(f'<text x="60" y="{y+10}" fill="{pal["accent"]}" font-size="13" '
                 f'font-family="monospace" font-weight="bold">零件清单（{len(d["components"])}）</text>')
    y += 30
    for i, comp in enumerate(d["components"]):
        parts.append(f'<text x="80" y="{y}" fill="{pal["text"]}" font-size="11" '
                     f'font-family="monospace">{i+1}. {comp}</text>')
        y += 20
        if y > H - 50:
            break
    if d["mechanism"]:
        parts.append(f'<text x="60" y="{H-26}" fill="{pal["text"]}" font-size="10" '
                     f'font-family="monospace">机制：{d["mechanism"][:60]}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


# ---- 渲染器 4：结构图（等距投影增强版） ----

def render_diagram(anatomy: Dict, tokens: Dict[str, object]) -> str:
    d = _extract(anatomy)
    pal = _palette(tokens)
    n = len(d["components"])
    parts = _svg_head(pal, f"概念结构图：{d['concept']}")
    cx, cy0 = W // 2, 100
    step = min(70, (H - 160) // max(n, 1))
    for i, comp in enumerate(d["components"]):
        y = cy0 + i * step
        # 等距方块（30° 投影感：左右各一斜线）
        parts.append(f'<rect x="{cx-18}" y="{y-18}" width="36" height="36" rx="5" '
                     f'fill="{pal["comp"]}" stroke="{pal["node"]}" stroke-width="1.3"/>')
        parts.append(f'<line x1="{cx-18}" y1="{y-18}" x2="{cx-27}" y2="{y-30}" '
                     f'stroke="{pal["node"]}" stroke-width="1"/>')
        parts.append(f'<line x1="{cx+18}" y1="{y-18}" x2="{cx+27}" y2="{y-30}" '
                     f'stroke="{pal["node"]}" stroke-width="1"/>')
        parts.append(f'<circle cx="{cx+14}" cy="{y-14}" r="9" fill="{pal["accent"]}"/>'
                     f'<text x="{cx+14}" y="{y-11}" fill="#fff" font-size="9" '
                     f'text-anchor="middle" font-family="monospace">{i+1}</text>')
        parts.append(f'<text x="{cx+40}" y="{y+4}" fill="{pal["text"]}" font-size="12" '
                     f'font-family="monospace">{comp}</text>')
        if i + 1 < n:
            parts.append(f'<line x1="{cx}" y1="{y+18}" x2="{cx}" y2="{y+step-18}" '
                         f'stroke="{pal["line"]}" stroke-dasharray="3,3"/>')
    parts.append(f'<text x="24" y="{H-20}" fill="{pal["text"]}" font-size="10" '
                 f'font-family="monospace">diagram | isometric 30° | components: {n}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


# ---- 渲染器注册表 + 加载协议 ----

RENDER_REGISTRY: Dict[str, Dict[str, object]] = {}


def register_render(name: str, fn: Callable, desc: str = "") -> None:
    """协议：注册渲染器。fn(anatomy, tokens) -> svg str"""
    RENDER_REGISTRY[name] = {"fn": fn, "desc": desc}


def load_render(name: str) -> Callable:
    """协议：加载渲染器；未注册回落 diagram（容错）。"""
    entry = RENDER_REGISTRY.get(name)
    if entry is None:
        return RENDER_REGISTRY["diagram"]["fn"]  # type: ignore
    return entry["fn"]  # type: ignore


def render(anatomy: Dict, tokens: Optional[Dict[str, object]] = None) -> str:
    """统一协议入口：anatomy（anatomize 结果）+ tokens（含 img_style）→ SVG。"""
    tk = {**DEFAULT_TOKENS, **(tokens or {})}
    fn = load_render(str(tk["img_style"]))
    return fn(anatomy, tk)


# 注册内置 4 渲染器
register_render("explosion", render_explosion,
                "爆炸图：零件沿中轴展开 + 数字编号引线 + 成品对照区")
register_render("annotated", render_annotated,
                "标注图：横截面示意 + 引线文字标注 + 放大细节")
register_render("legend", render_legend,
                "图例图：维度色语义 + 层次说明 + 零件清单")
register_render("diagram", render_diagram,
                "结构图：等距投影增强版")


def main(argv: Optional[List[str]] = None) -> int:
    """CLI：python -m holoaeon.concept_anatomy_render <概念> [--style] [--save]"""
    args = list(argv) if argv is not None else list(sys.argv[1:])
    if not args:
        print("可用渲染器：%s" % ", ".join(sorted(RENDER_REGISTRY)))
        return 1
    concept = args[0]
    style = "diagram"
    if "--style" in args:
        i = args.index("--style")
        if len(args) > i + 1:
            style = args[i + 1]
    save = None
    if "--save" in args:
        i = args.index("--save")
        if len(args) > i + 1:
            save = args[i + 1]
    from .concept_anatomy import ConceptAnatomizer
    result = ConceptAnatomizer().anatomize(concept)
    svg = render(result, {"img_style": style})
    if save:
        with open(save, "w", encoding="utf-8") as f:
            f.write(svg)
        print("已保存: %s (%d 字符, style=%s)" % (save, len(svg), style))
    else:
        print(svg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
