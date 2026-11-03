# -*- coding: utf-8 -*-
"""V21 概念视觉锻造台（concept_visual_forge）。

把概念解剖器的结构化真值（description/mechanism/components）锻造成
"可以直接出图的系统提示词"，支持风格矩阵批量变体与三档风格化
（蓝图化 / 美术化 / 艺术化）。全部确定性规则，零 LLM 依赖，纯标准库。

能力链（八步流水线）：
  文字 forge() → 搜索 text_search() → 初级图像描述 image_desc_v1()
  → 系统提示词生成 system_prompt_gen() → 矩阵修改 matrix_modify()
  → 优化提示词 optimize_prompt() → 三档风格化 stylize()
"""
from __future__ import annotations

import json
import re
import sys
from typing import Dict, List, Optional

from .concept_anatomy import CONCEPT_MAP

# 中英混合分词（与 holoaeon 其他模块口径一致）
_CJK_WORD = re.compile(r"[a-zA-Z0-9_]+|[\u4e00-\u9fff]+")

# ---- 风格矩阵（matrix_modify 的修改维度） ----
FORGE_MATRIX: Dict[str, List[str]] = {
    "style": ["工业蓝图", "手绘线稿", "水彩", "赛博霓虹", "极简几何", "油画"],
    "layout": ["爆炸分解", "横截面", "场景陈列"],
    "palette": ["冷灰蓝", "暖米白", "高对比黑金"],
}

# ---- 质量锚点 / 负面提示词（optimize_prompt 使用） ----
_QUALITY_ANCHORS = [
    "高分辨率细节", "构图清晰", "边缘干净", "层次分明",
]
_NEGATIVE_TERMS = [
    "无文字水印", "无乱码标注", "无变形", "无多余杂物", "无残缺部件",
]

# 相关概念匹配：同义/领域映射（表外概念 → 就近概念，用于结构化描述兜底）
_RELATED_HINTS: Dict[str, List[str]] = {
    "mechanism": ["经络", "经络机制", "赫布协作场"],
    "security": ["皮肤机制"],
    "runtime": ["心跳机制"],
    "protocol": ["经络机制", "语义通信基座"],
    "architecture": ["城邦架构"],
    "verification": ["去幻觉"],
}


def text_search(concept_text: str) -> Dict:
    """第 2 步 文字搜索：CONCEPT_MAP 命中 / 表外概念结构化描述。"""
    if concept_text in CONCEPT_MAP:
        e = CONCEPT_MAP[concept_text]
        return {
            "hit": True,
            "concept": concept_text,
            "dimension": e["dimension"],
            "description": e["description"],
            "mechanism": e["mechanism"],
            "components": list(e["components"]),
        }
    # 表外概念：关键词抽取
    words = _CJK_WORD.findall(concept_text)
    # 就近相关概念（关键词交集 / 领域提示）
    related = []
    for dim, cands in _RELATED_HINTS.items():
        for c in cands:
            if c in CONCEPT_MAP:
                related.append({"concept": c, "dimension": dim,
                                "description": CONCEPT_MAP[c]["description"]})
    return {
        "hit": False,
        "concept": concept_text,
        "keywords": words,
        "related": related[:3],
        "description": "概念「%s」的非内置条目（关键词：%s）；就近概念 %d 个可参考。"
                       % (concept_text, "/".join(words[:6]) or "无", len(related)),
    }


def image_desc_v1(search: Dict) -> str:
    """第 3 步 初级图像描述：主体 + 关键元素 + 布局（不涉及风格）。"""
    if search["hit"]:
        comps = "、".join(search["components"][:6])
        return ("主体：%s。核心机制：%s。关键元素：%s。"
                "布局建议：主体居中，元素围绕排布。"
                % (search["concept"], search["mechanism"], comps))
    return ("主体：%s。构图建议：以概念名称为中心，环绕展示相关机制元素，"
            "突出结构层次。" % search["concept"])


def system_prompt_gen(desc_v1: str, style: str = "工业蓝图",
                      layout: str = "爆炸分解", palette: str = "冷灰蓝") -> str:
    """第 4 步 系统提示词生成：初级描述 + 风格/构图/色调模板。"""
    return ("系统提示词：绘制「%s」——风格：%s；构图：%s；色调：%s。"
            "画面要求：%s；%s。元素严格按概念解剖零件清单呈现。"
            % (desc_v1[:60], style, layout, palette,
               _QUALITY_ANCHORS[0], _QUALITY_ANCHORS[1]))


def matrix_modify(prompt: str) -> Dict:
    """第 5 步 矩阵修改：风格矩阵批量变体（返回矩阵规格 + 首个变体示例）。"""
    variants = []
    for style in FORGE_MATRIX["style"]:
        for layout in FORGE_MATRIX["layout"][:1]:
            for palette in FORGE_MATRIX["palette"][:1]:
                variants.append(system_prompt_gen(prompt[:40], style, layout, palette))
    return {
        "matrix": FORGE_MATRIX,
        "variant_count": len(FORGE_MATRIX["style"]) * 1 * 1,
        "variants": variants,
    }


def optimize_prompt(prompt: str) -> str:
    """第 6 步 优化系统提示词：质量锚点 + 负面提示词 + 确定性锚点。"""
    return prompt + (" 画质：%s。负面：%s、%s、%s。确定性：只画概念映射表内元素，"
                     "不添加映射表外部件。" % (_QUALITY_ANCHORS[2], _NEGATIVE_TERMS[0],
                                              _NEGATIVE_TERMS[1], _NEGATIVE_TERMS[2]))


def stylize(optimized: str) -> Dict:
    """第 7-9 步 三档风格化：蓝图化 / 美术化 / 艺术化。"""
    return {
        "blueprint": (optimized + " 成品要求：工业蓝图制图——白底细线、尺寸标注引线、"
                      "爆炸分解展开、数字编号，无阴影无装饰。"),
        "art_direction": (optimized + " 成品要求：美术设定集——主体三视图、配色标注、"
                          "材质说明、环境光参考，干净排版。"),
        "artistic": (optimized + " 成品要求：艺术创作——情绪化光影、艺术流派笔触、"
                     "氛围背景，允许适度风格化演绎。"),
    }


def forge(concept_text: str) -> Dict:
    """总入口（第 1 步 文字→全链路）。返回八步 JSON。"""
    s = text_search(concept_text)
    d1 = image_desc_v1(s)
    sp = system_prompt_gen(d1)
    mx = matrix_modify(sp)
    op = optimize_prompt(sp)
    st = stylize(op)
    return {
        "input": concept_text,
        "step2_text_search": s,
        "step3_image_desc_v1": d1,
        "step4_system_prompt": sp,
        "step5_matrix": {"matrix": mx["matrix"], "variant_count": mx["variant_count"],
                         "sample_variant": mx["variants"][0]},
        "step6_optimized": op,
        "step7_9_stylized": st,
    }


def main(argv: Optional[List[str]] = None) -> int:
    """CLI：python -m holoaeon.concept_visual_forge <概念> [--pretty]"""
    args = list(argv) if argv is not None else list(sys.argv[1:])
    if not args:
        print(json.dumps({"error": "缺概念名", "usage": "concept_visual_forge <概念>"},
                         ensure_ascii=False, indent=2))
        return 1
    concept = args[0]
    result = forge(concept)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
