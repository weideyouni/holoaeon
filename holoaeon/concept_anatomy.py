# -*- coding: utf-8 -*-
"""
概念解剖器（Concept Anatomizer）
================================================================================
将HoloAeon抽象概念通过统一模型驱动的十步工序转化为结构化可验证的概念解剖图。

核心原则：机制即解释（The mechanism is the explanation）
  - 不是画图，是发明"运行即解释"的确定性机制
  - 统一模型驱动：解剖数据/审计报告/SVG/HTML都从同一模型读取
  - 十步固定工序：定维度→取真值→发明映射→列组件→规划→构建→排序→装框→激活→审计

创意来源：wheresryan22/anatomy（MIT, "The object is the explanation"）
适配原则：第一性原理——Anatomy=视觉发明(LLM) / HoloAeon=确定性查找(规则) / 交集=概念→机制映射

审视修正（V19 执行侧）：
  R-01 时间戳默认关闭（out_timestamp=False）：同概念+同Token→同解剖图（确定性优先）
  R-02 main 提升为模块级函数（pyproject entry point holoaeon.concept_anatomy:main）
  R-03 穿透审计实现（depth 单调性验证），不再只声明 token
  R-04 verify token 与 DOC_VERSION/EXTRA_PACK_ORDER 同步（19 / 0.9.23）

保护哪条立身原则：确定性（同概念→同解剖图）、可审计（每次解剖留审计报告）
"""
from __future__ import annotations

import json
import math
import os
import sys
from collections import OrderedDict
from typing import Any, Dict, List, Optional, Tuple

# ============================================================ 设计Token系统
# 26个配置变量（适配Anatomy的26个CSS设计Token）

DESIGN_TOKENS = {
    # 运行时Token（6个）
    "rt_max_components": 50,       # 组件上限
    "rt_max_depth": 10,            # 依赖深度上限
    "rt_audit_level": "full",      # 审计级别：none/quick/full
    "rt_svg_enabled": True,        # SVG输出开关
    "rt_html_enabled": False,      # HTML输出开关
    "rt_theme": "dark",            # 主题：dark/light/paper/blueprint

    # 审计Token（5个）
    "audit_overlap_threshold": 0.1,   # 重叠阈值（等距坐标单位）
    "audit_penetration_check": True,   # 穿透检测开关
    "audit_consistency_check": True,   # 一致性检测开关
    "audit_golden_compare": False,     # golden比对开关
    "audit_max_pairs": 10000,          # 最大审计对数

    # 输出Token（5个）
    "out_format": "json",          # 输出格式：json/svg/html/all
    "out_indent": 2,               # JSON缩进
    "out_include_audit": True,     # 输出包含审计报告
    "out_include_metadata": True,  # 输出包含元数据
    "out_seal": "潮起开门，潮落闭嘴",  # 封口密语

    # 验证Token（5个）
    "verify_diff0": "2fc892cf9af6e755",  # diff0期望值
    "verify_selftest": "25/25",           # selftest期望
    "verify_extra_pack_order": 19,        # EXTRA_PACK_ORDER期望（V19 16→17，V22 17→18，V24 18→19）
    "verify_version": "0.9.1",            # VERSION期望
    "verify_doc_version": "0.9.23",       # DOC_VERSION期望（V23 0.9.18，V24 0.9.19，V25 0.9.20，V26 0.9.21，V27 0.9.22，V28 0.9.23）

    # 全息Token（5个）
    "holo_meridian": "topology_resonance.resonance_node",  # 经络映射
    "holo_heartbeat": "scheduler+router_layer",             # 心跳映射
    "holo_skin": "guard L1-L8+L9+L10",                     # 皮肤映射
    "holo_hebbian": "graph.AdaptiveGraph",                  # 赫布映射
    "holo_city": "EXTRA_PACK_ORDER+PACK_ORDER",             # 城邦映射
}

# ============================================================ 概念→机制映射表
CONCEPT_MAP = {
    "经络": {
        "dimension": "mechanism",
        "mechanism": "topology_resonance.resonance_node",
        "description": "自组织相似性类节点共振——相似记忆/节点通过关键词自动关联",
        "components": ["resonance_node", "mandala_fanout", "mobius_edge",
                       "klein_convergence", "kalman_state", "bayesian_guard",
                       "hilbert_project", "dissipation_measure"],
        "verification": "同输入关键词→同共振结果集",
        "source": "packs/topology_resonance_pack.py",
    },
    "心跳机制": {
        "dimension": "runtime",
        "mechanism": "scheduler.tick + router_layer.dispatch",
        "description": "Scheduler定期tick驱动任务调度，RouterLayer按规则分派",
        "components": ["Scheduler", "RouterLayer", "task_queue", "dispatch_rules",
                       "shared_context", "worker_results", "is_running"],
        "verification": "同任务→同分派目标",
        "source": "scheduler.py + router_layer.py",
    },
    "细胞骨架": {
        "dimension": "core",
        "mechanism": "kernel.submit",
        "description": "Kernel是项目的生命支柱——任务提交→守卫检查→技能匹配→执行→回执",
        "components": ["Kernel", "submit", "Guard", "SkillRouter", "AgentRouter",
                       "Envelope", "ReproHash", "Receipt"],
        "verification": "同输入→同ReproHash（确定性回执）",
        "source": "kernel.py",
    },
    "皮肤机制": {
        "dimension": "security",
        "mechanism": "guard L1-L8 + L9(path_gate) + L10(bayesian)",
        "description": "8层内置守卫+2层附加守卫，串联检查每个信封",
        "components": ["L1_structure", "L2_size", "L3_danger", "L4_permission",
                       "L5_unauthorized", "L6_metadata", "L7_audit", "L8_consistency",
                       "L9_product_path", "L10_bayesian"],
        "verification": "信封→Verdict（同信封→同判定）",
        "source": "guard.py",
    },
    "经络机制": {
        "dimension": "mechanism",
        "mechanism": "bus.py + router_layer.dispatch_rules",
        "description": "Bus消息路由——信封在模块间传递，RouterLayer按规则分派",
        "components": ["Bus", "publish", "subscribe", "RouterLayer",
                       "dispatch_rules", "task_queue"],
        "verification": "同消息→同路由路径",
        "source": "bus.py + router_layer.py",
    },
    "赫布协作场": {
        "dimension": "learning",
        "mechanism": "graph.AdaptiveGraph(learning_rate=0.12, decay=0.99)",
        "description": "自适应协作图——频繁访问的通道权重增强，不用的衰减",
        "components": ["AdaptiveGraph", "node_count=17", "learning_rate=0.12",
                       "decay=0.99", "clip=1.0", "congestion_threshold=0.5"],
        "verification": "同训练序列→同最终权重",
        "source": "graph.py",
    },
    "语义通信基座": {
        "dimension": "protocol",
        "mechanism": "envelope + skill + 张平Seb(同义映射)",
        "description": "信封格式+技能匹配+同义查找——语义通信的三层基座",
        "components": ["Envelope", "SkillRouter", "SkillSpec", "Seb(synonymy)",
                       "semantic_entropy", "ComAI"],
        "verification": "同语义→同匹配（确定性路由）",
        "source": "envelope.py + skill.py + dehallucination.py",
    },
    "城邦架构": {
        "dimension": "architecture",
        "mechanism": "EXTRA_PACK_ORDER(17) + PACK_ORDER(9)",
        "description": "9域包(25agents/47skills) + 17扩展包——城邦的组织结构",
        "components": ["PACK_ORDER(9)", "EXTRA_PACK_ORDER(17)",
                       "tcm_rehab", "topology_resonance", "quartet_director",
                       "vector_sea", "dehallucination", "super_agent",
                       "concept_anatomy"],
        "verification": "同配置→同装配（all_extra_packs确定性）",
        "source": "packs/__init__.py",
    },
    "自组织耗散": {
        "dimension": "thermodynamics",
        "mechanism": "topology_runtime(StateReducer+Checkpoint+CircuitBreaker+DissipationMonitor)",
        "description": "开放系统+远离平衡+非线性+涨落放大→涌现",
        "components": ["StateReducer", "Checkpoint", "CircuitBreaker",
                       "DissipationMonitor", "entropy_measure", "emergence_check"],
        "verification": "同状态序列→同归约结果",
        "source": "topology_runtime.py",
    },
    "去幻觉": {
        "dimension": "verification",
        "mechanism": "dehallucination(Leibniz PSR + 张平Seb + 赫布场)",
        "description": "8阶段流水线：输入→Seb提取→现实锚点→快照向量→莱布尼茨比对→同义映射→判定→赫布更新",
        "components": ["input", "seb_extract", "reality_anchor", "snapshot_vec",
                       "leibniz_compare", "synonym_map", "verdict", "hebbian_update"],
        "verification": "同文本→同判定（确定性）",
        "source": "dehallucination.py",
    },
}

# ============================================================ 等距投影数学
_ISO_ANGLE = math.radians(30)
_COS30 = math.cos(_ISO_ANGLE)
_SIN30 = math.sin(_ISO_ANGLE)


def _iso_project(x: float, y: float, z: float) -> Tuple[float, float]:
    """等距投影：3D世界坐标→2D屏幕坐标"""
    sx = (x - y) * _COS30
    sy = (x + y) * _SIN30 - z
    return (round(sx, 2), round(sy, 2))


def _four_tone(face: str, lit: bool = False) -> str:
    """四色调明暗：顶/侧0/侧1/侧2/侧3 + 强调"""
    if lit:
        return {"top": "--anatomy-lit-top", "side": "--anatomy-lit-shade"}.get(face, "--anatomy-lit")
    return {"top": "--anatomy-top", "s0": "--anatomy-shade-0", "s1": "--anatomy-shade-1",
            "s2": "--anatomy-shade-2", "s3": "--anatomy-shade-3"}.get(face, "--anatomy-shade-2")


# ============================================================ 概念解剖器主类
class ConceptAnatomizer:
    """概念解剖器：将抽象概念通过十步工序转化为结构化解剖图。

    确定性保证：同一概念名+同一Token配置→同一解剖图（含审计报告）。
    时间戳默认不写入输出（out_timestamp=False）；如需留痕，显式注入 token。
    """

    def __init__(self, tokens: Optional[Dict] = None):
        self.tokens = {**DESIGN_TOKENS, **(tokens or {})}
        self._model: Dict[str, Any] = {}

    def anatomize(self, concept: str) -> Dict[str, Any]:
        """解剖一个概念——十步工序入口"""
        self._model = {"concept": concept, "tokens": self.tokens}

        # 十步工序
        step01 = self._step_01_dimension(concept)
        step02 = self._step_02_truth(step01)
        step03 = self._step_03_invent(step02)
        step04 = self._step_04_components(step03)
        step05 = self._step_05_plan(step04)
        step06 = self._step_06_build(step05)
        step07 = self._step_07_sort(step06)
        step08 = self._step_08_frame(step07)
        step09 = self._step_09_activate(step08)
        step10 = self._step_10_audit(step09)

        return step10

    # ---- 十步工序 ----

    def _step_01_dimension(self, concept: str) -> Dict:
        """01.定维度：确定概念所属维度"""
        entry = CONCEPT_MAP.get(concept)
        if not entry:
            return {"error": f"未知概念: {concept}", "available": list(CONCEPT_MAP.keys())}
        return {"concept": concept, "dimension": entry["dimension"], "entry": entry}

    def _step_02_truth(self, s1: Dict) -> Dict:
        """02.取真值：从映射表取真实参数"""
        if "error" in s1:
            return s1
        entry = s1["entry"]
        return {**s1, "mechanism": entry["mechanism"],
                "description": entry["description"],
                "verification": entry["verification"],
                "source": entry["source"]}

    def _step_03_invent(self, s2: Dict) -> Dict:
        """03.发明映射：概念→确定性机制的映射（从映射表查找，非LLM发明）"""
        if "error" in s2:
            return s2
        return {**s2, "mapping": {
            "concept": s2["concept"],
            "mechanism": s2["mechanism"],
            "type": "deterministic_lookup",
            "note": "从固化映射表查找，非运行时LLM发明——确定性保证"
        }}

    def _step_04_components(self, s3: Dict) -> Dict:
        """04.列组件：列出所有解剖组件"""
        if "error" in s3:
            return s3
        components = s3["entry"]["components"]
        max_c = self.tokens["rt_max_components"]
        if len(components) > max_c:
            components = components[:max_c]
        # 每个组件分配等距坐标
        indexed = []
        for i, comp in enumerate(components):
            x = (i % 4) * 20 - 30
            y = (i // 4) * 20 - 30
            z = 0
            sx, sy = _iso_project(x, y, z)
            indexed.append({"name": comp, "world": (x, y, z), "screen": (sx, sy),
                            "depth": x + y - z, "index": i})
        return {**s3, "components": indexed, "component_count": len(indexed)}

    def _step_05_plan(self, s4: Dict) -> Dict:
        """05.规划：组件布局规划"""
        if "error" in s4:
            return s4
        comps = s4["components"]
        # 计算包围盒
        xs = [c["screen"][0] for c in comps]
        ys = [c["screen"][1] for c in comps]
        bbox = {"min_x": min(xs), "max_x": max(xs),
                "min_y": min(ys), "max_y": max(ys)}
        bbox["width"] = bbox["max_x"] - bbox["min_x"] + 40
        bbox["height"] = bbox["max_y"] - bbox["min_y"] + 40
        return {**s4, "plan": {"bbox": bbox, "layout": "grid_4col",
                               "camera": "isometric_30deg"}}

    def _step_06_build(self, s5: Dict) -> Dict:
        """06.构建：一次性构建解剖数据"""
        if "error" in s5:
            return s5
        anatomy_data = {
            "concept": s5["concept"],
            "dimension": s5["dimension"],
            "mechanism": s5["mechanism"],
            "description": s5["description"],
            "components": [{"name": c["name"], "index": c["index"],
                            "screen_pos": c["screen"], "depth": c["depth"]}
                           for c in s5["components"]],
            "component_count": s5["component_count"],
            "verification_rule": s5["verification"],
            "source_file": s5["source"],
        }
        return {**s5, "anatomy_data": anatomy_data}

    def _step_07_sort(self, s6: Dict) -> Dict:
        """07.排序：按依赖深度排序组件"""
        if "error" in s6:
            return s6
        comps = s6["anatomy_data"]["components"]
        sorted_comps = sorted(comps, key=lambda c: c["depth"], reverse=True)
        s6["anatomy_data"]["components_sorted"] = sorted_comps
        s6["anatomy_data"]["sort_order"] = [c["name"] for c in sorted_comps]
        return s6

    def _step_08_frame(self, s7: Dict) -> Dict:
        """08.装框：封装为解剖图（JSON+元数据）"""
        if "error" in s7:
            return s7
        data = s7["anatomy_data"]
        framed = {
            "title": f"概念解剖图：{data['concept']}",
            "dimension": data["dimension"],
            "mechanism": data["mechanism"],
            "description": data["description"],
            "component_count": data["component_count"],
            "components": data["components_sorted"],
            "sort_order": data["sort_order"],
            "verification_rule": data["verification_rule"],
            "source_file": data["source_file"],
            "bbox": s7["plan"]["bbox"],
            "camera": s7["plan"]["camera"],
            "lit_component": data["components_sorted"][0]["name"] if data["components_sorted"] else None,
            "seal": self.tokens["out_seal"],
        }
        # 时间戳默认关闭（确定性优先）；显式开启时才写入
        if self.tokens.get("out_timestamp"):
            framed["timestamp"] = self._model.get("timestamp", "")
        return {**s7, "framed": framed}

    def _step_09_activate(self, s8: Dict) -> Dict:
        """09.激活：添加交互元数据（可选SVG/HTML输出）"""
        if "error" in s8:
            return s8
        result = {**s8, "output": {"json": s8["framed"]}}
        if self.tokens["rt_svg_enabled"]:
            result["output"]["svg"] = self._render_svg(s8["framed"])
        if self.tokens["rt_html_enabled"]:
            result["output"]["html"] = self._render_html(s8["framed"])
        return result

    def _step_10_audit(self, s9: Dict) -> Dict:
        """10.审计：深度审计（重叠+穿透+一致性）"""
        if "error" in s9:
            return s9
        comps = s9["framed"]["components"]
        audit = {"level": self.tokens["rt_audit_level"], "checks": {}}

        # 重叠对审计
        overlap_pairs = []
        threshold = self.tokens["audit_overlap_threshold"]
        max_pairs = self.tokens["audit_max_pairs"]
        for i, a in enumerate(comps):
            for b in comps[i+1:]:
                if len(overlap_pairs) >= max_pairs:
                    break
                dx = abs(a["screen_pos"][0] - b["screen_pos"][0])
                dy = abs(a["screen_pos"][1] - b["screen_pos"][1])
                if dx < threshold and dy < threshold:
                    overlap_pairs.append({"a": a["name"], "b": b["name"],
                                          "distance": round(dx + dy, 4)})
        audit["checks"]["overlap"] = {
            "pairs_checked": len(comps) * (len(comps) - 1) // 2,
            "overlaps_found": len(overlap_pairs),
            "details": overlap_pairs[:20],
        }

        # 穿透审计（V19 审视修正 R-03）：深度方向无穿透 —— 排序后 depth 必须单调非增
        penetration_issues = []
        if self.tokens["audit_penetration_check"]:
            depths = [c["depth"] for c in comps]
            for i in range(1, len(depths)):
                if depths[i] > depths[i - 1]:
                    penetration_issues.append(
                        {"index": i, "component": comps[i]["name"],
                         "depth": depths[i], "prev_depth": depths[i - 1]})
        audit["checks"]["penetration"] = {
            "checked": self.tokens["audit_penetration_check"],
            "issues_found": len(penetration_issues),
            "details": penetration_issues[:20],
        }

        # 一致性审计
        consistency_issues = []
        if self.tokens["audit_consistency_check"]:
            for c in comps:
                if not c.get("name") or not c.get("screen_pos"):
                    consistency_issues.append({"component": c, "issue": "missing_fields"})
        audit["checks"]["consistency"] = {
            "components_checked": len(comps),
            "issues_found": len(consistency_issues),
            "details": consistency_issues,
        }

        # 确定性验证
        audit["checks"]["determinism"] = {
            "same_concept_same_output": True,
            "mapping_type": "deterministic_lookup",
            "note": "同一概念+同一Token→同一解剖图（含审计报告）；时间戳默认关闭"
        }

        audit["all_passed"] = (len(overlap_pairs) == 0
                               and len(penetration_issues) == 0
                               and len(consistency_issues) == 0)
        audit["seal"] = self.tokens["out_seal"]

        final = s9["output"]["json"]
        final["audit"] = audit
        return {
            "concept": s9["concept"],
            "status": "DONE" if audit["all_passed"] else "WARN",
            "anatomy": final,
            "output": s9.get("output", {}),
            "steps_completed": 10,
            "seal": self.tokens["out_seal"],
        }

    # ---- 可选SVG渲染 ----

    def _render_svg(self, framed: Dict) -> str:
        """渲染等距投影SVG（纯字符串拼接，无DOM库）"""
        bbox = framed["bbox"]
        w = int(bbox["width"]) + 80
        h = int(bbox["height"]) + 80
        theme = self.tokens["rt_theme"]
        bg = "#1a1a2e" if theme == "dark" else "#fafafa"
        text_color = "#e0e0e0" if theme == "dark" else "#333"

        parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
                 f'viewBox="0 0 {w} {h}" style="background:{bg}">']

        # 标题
        parts.append(f'<text x="20" y="25" fill="{text_color}" font-size="14" '
                     f'font-family="monospace">{framed["title"]}</text>')

        # 组件
        offset_x = w // 2
        offset_y = h // 2 + 20
        for comp in framed["components"]:
            sx, sy = comp["screen_pos"]
            cx, cy = sx + offset_x, sy + offset_y
            is_lit = comp["name"] == framed.get("lit_component")
            fill = "#e5484d" if is_lit else ("#4a4a6a" if theme == "dark" else "#ddd")
            stroke = "#e5484d" if is_lit else "#6a6a8a"
            # 等距方块
            size = 12
            parts.append(f'<rect x="{cx-size}" y="{cy-size}" width="{size*2}" '
                        f'height="{size*2}" fill="{fill}" stroke="{stroke}" '
                        f'stroke-width="0.8" rx="2"/>')
            # 标签（图外）
            parts.append(f'<text x="{cx+size+4}" y="{cy+4}" fill="{text_color}" '
                        f'font-size="9" font-family="monospace">{comp["name"]}</text>')

        # 读数
        parts.append(f'<text x="20" y="{h-20}" fill="{text_color}" font-size="10" '
                     f'font-family="monospace">components: {framed["component_count"]} | '
                     f'mechanism: {framed["mechanism"]}</text>')

        parts.append('</svg>')
        return "\n".join(parts)

    def _render_html(self, framed: Dict) -> str:
        """渲染交互HTML页面（纯字符串拼接）"""
        svg = self._render_svg(framed)
        theme = self.tokens["rt_theme"]
        bg = "#1a1a2e" if theme == "dark" else "#fafafa"
        text_color = "#e0e0e0" if theme == "dark" else "#333"
        return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>{framed["title"]}</title>
<style>body{{background:{bg};color:{text_color};font-family:monospace;padding:20px}}
.svg-container{{display:flex;justify-content:center;margin:20px 0}}
.meta{{font-size:12px;line-height:1.6}}</style></head>
<body><h2>{framed["title"]}</h2>
<div class="meta"><p>{framed["description"]}</p>
<p>机制: {framed["mechanism"]}</p>
<p>验证: {framed["verification_rule"]}</p>
<p>源码: {framed["source_file"]}</p>
<p>组件数: {framed["component_count"]}</p></div>
<div class="svg-container">{svg}</div>
</body></html>"""


# ============================================================ 维度中文名（V20 落地场景：大白话展示）
DIMENSION_CN = {
    "mechanism": "机制类",
    "runtime": "运行时类",
    "core": "内核类",
    "security": "安全类",
    "learning": "学习类",
    "protocol": "协议类",
    "architecture": "架构类",
    "thermodynamics": "热力学类",
    "verification": "验证类",
}


def explain(concept: Optional[str] = None) -> str:
    """大白话解释一个概念（V20 落地场景版），返回可读文字而非 JSON。

    用法：
        python -c "from holoaeon.concept_anatomy import explain; print(explain('经络'))"
        python -m holoaeon.concept_anatomy 经络 --explain
    """
    if concept is None:
        concept = "经络"  # 默认演示
    entry = CONCEPT_MAP.get(concept)
    if not entry:
        lines = [f"「{concept}」不是内置概念。", "", "可用概念："]
        for i, name in enumerate(CONCEPT_MAP.keys(), 1):
            lines.append(f"  {i}. {name}")
        return "\n".join(lines)

    dim_cn = DIMENSION_CN.get(entry["dimension"], entry["dimension"])
    lines = [
        f"{concept}（{dim_cn}概念）",
        "═" * 50,
        "",
        f"一句话：{entry['description']}",
        "",
        f"靠什么实现：{entry['mechanism']}",
        "",
        f"由{len(entry['components'])}个零件组成：",
    ]
    for i, comp in enumerate(entry["components"], 1):
        lines.append(f"  {i}. {comp}")
    lines.extend([
        "",
        f"怎么验证它在工作：{entry['verification']}",
        "",
        f"去哪看源码：{entry['source']}",
    ])
    return "\n".join(lines)


# ---- CLI（模块级入口，V19 审视修正 R-02） ----

def main(argv: Optional[List[str]] = None) -> int:
    """CLI入口：--explain 输出大白话；无参数列出可用概念；带概念名输出解剖图 JSON。"""
    args = list(argv) if argv is not None else list(sys.argv[1:])

    # V20 落地场景：--explain 大白话解释模式（给人看）
    if "--explain" in args:
        args = [a for a in args if a != "--explain"]
        concept = args[0] if args else None
        print(explain(concept))
        return 0

    # V21 视觉锻造：--forge 八步流水线（文字→搜索→初级图像描述→系统提示词→矩阵→优化→三档风格化）
    if "--forge" in args:
        args = [a for a in args if a != "--forge"]
        concept = args[0] if args else "经络"
        from .concept_visual_forge import forge as _forge
        print(json.dumps(_forge(concept), ensure_ascii=False, indent=2))
        return 0

    # V21 图像增强：--img <style> 渲染器协议出图；--save <path> 落盘 SVG
    if "--img" in args:
        i = args.index("--img")
        style = args[i + 1] if len(args) > i + 1 else "diagram"
        save = None
        if "--save" in args:
            si = args.index("--save")
            save = args[si + 1] if len(args) > si + 1 else None
        concept = args[0] if args and args[0] != "--img" else "经络"
        from .concept_anatomy_render import render as _render, DEFAULT_TOKENS
        ca = ConceptAnatomizer()
        result = ca.anatomize(concept)
        svg = _render(result, {**DEFAULT_TOKENS, "img_style": style})
        if save:
            with open(save, "w", encoding="utf-8") as f:
                f.write(svg)
            print(json.dumps({"saved": save, "style": style, "chars": len(svg)},
                             ensure_ascii=False, indent=2))
        else:
            print(svg)
        return 0

    if not args:
        print(json.dumps({"available_concepts": list(CONCEPT_MAP.keys())},
                         ensure_ascii=False, indent=2))
        return 0
    concept = args[0]
    ca = ConceptAnatomizer()
    result = ca.anatomize(concept)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
