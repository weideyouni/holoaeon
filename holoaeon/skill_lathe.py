# -*- coding: utf-8 -*-
"""
skill_lathe —— 技能机床：TVCB → SkillSpec 转换器
================================================================================
把向量海打捞上来的张量向量耦合体（TVCB）加工成可注册的 HoloAeon 技能。

比喻：原油→成品油的炼油厂
  原油 = TVCB（从向量海打捞）
  催化剂 = 确定性张量转换（quartet 方法论内联）
  糟粕 = 低能量级（C 级）条目过滤丢弃
  成品油 = SkillSpec（kernel.register_skill / DomainPack 可注册）

V14-SKILL-LATHE-PROTOCOL-PLUGINS · 纯标准库、确定性、离线、零外部依赖。
"""
from __future__ import annotations

import hashlib
import json
import sys
from typing import Any, Dict, List, Optional


class SkillLathe:
    """技能机床：把 TVCB 加工成 SkillSpec。"""

    # 能量分级阈值（同 V13 TVCB 口径：A≥0.7 / B≥0.4 / C<0.4 丢弃）
    GRADE_A_THRESHOLD = 0.7
    GRADE_B_THRESHOLD = 0.4

    # ------------------------------------------------------------ 单件加工
    def turn_skill(self, tvcb: dict) -> Optional[dict]:
        """把一个 TVCB 加工成一个技能定义（SkillSpec 字典格式）。

        步骤：
          1. 能量分级：C 级直接丢弃（返回 None）
          2. 从 TVCB-ID 提取技能名（salvaged_<topic>_<hash4>）
          3. 从 topic+keywords 生成描述
          4. 从 idea_pattern/reusable_points 生成确定性可执行函数
          5. 组装 SkillSpec（name/fn/description/tags/inputs/permissions）
        """
        grade = str(tvcb.get("energy_grade", "C")).upper()
        if grade == "C":
            return None  # 低品位丢弃（炼油厂出渣）

        tvcb_id = str(tvcb.get("tvcb_id") or "TVCB-UNKNOWN")
        keywords = list(tvcb.get("keywords") or [])
        topic = tvcb.get("topic") or {}
        if isinstance(topic, dict):
            topic_name = str(topic.get("primary") or "general")
        else:
            topic_name = str(topic or "general")

        # 1. 技能名：salvaged_<topic>_<id尾4位>
        tail = str(tvcb_id).split("-")[-1][:4].lower() if "-" in str(tvcb_id) else "xxxx"
        skill_name = f"salvaged_{topic_name}_{tail}"

        # 2. 描述
        top_kw = keywords[:3]
        description = (
            "从向量海打捞的智慧（主题:%s，关键词:%s）"
            % (topic_name, ",".join(top_kw) if top_kw else "none")
        )

        # 3. 确定性可执行函数（闭包捕获 TVCB 字段，同一 TVCB 同一输出）
        idea_pattern = tvcb.get("idea_pattern", "")
        reusable = list(tvcb.get("reusable_points") or [])

        def salvaged_fn(**kwargs: Any) -> dict:
            return {
                "source": tvcb_id,
                "topic": topic_name,
                "keywords": keywords[:10],
                "idea_pattern": idea_pattern,
                "reusable_points": reusable,
                "query": kwargs.get("query", ""),
                "executed": True,
            }

        # 4. 组装 SkillSpec
        return {
            "name": skill_name,
            "fn": salvaged_fn,
            "description": description,
            "tags": [topic_name, f"grade_{grade}", "salvaged"],
            "inputs": {"query": "str"},
            "permissions": 0,
        }

    # ------------------------------------------------------------ 批量加工
    def batch_turn(self, tvcb_list: list) -> list:
        """批量加工：多个 TVCB → 多个 SkillSpec（fn 置 None 便于 JSON 序列化）。"""
        skills = []
        for tvcb in tvcb_list:
            spec = self.turn_skill(tvcb)
            if spec:
                spec = dict(spec)
                spec["fn"] = None
                skills.append(spec)
        return skills

    # ------------------------------------------------------------ 自检
    def selfcheck(self) -> dict:
        """机床自检：A/B 加工、C 丢弃、确定性复算。"""
        a = self.turn_skill({
            "tvcb_id": "TVCB-TEST0001", "topic": {"primary": "test"},
            "keywords": ["AI", "agent"], "idea_pattern": "pattern",
            "reusable_points": ["p1"], "energy_grade": "A",
        })
        b = self.turn_skill({
            "tvcb_id": "TVCB-TEST0002", "topic": "b",
            "keywords": [], "energy_grade": "B",
        })
        c = self.turn_skill({"tvcb_id": "TVCB-TEST0003", "energy_grade": "C"})
        a2 = self.turn_skill({
            "tvcb_id": "TVCB-TEST0001", "topic": {"primary": "test"},
            "keywords": ["AI", "agent"], "idea_pattern": "pattern",
            "reusable_points": ["p1"], "energy_grade": "A",
        })
        ok = (a is not None and b is not None and c is None
              and a["name"] == a2["name"] and a["description"] == a2["description"])
        return {"ok": ok, "grade_a": a is not None, "grade_b": b is not None,
                "grade_c_dropped": c is None,
                "deterministic": a["name"] == a2["name"],
                "sample": a["name"] if a else None}


def main(argv=None) -> int:
    """CLI 入口（pyproject holoaeon-lathe）：演示机床加工闭环。"""
    args = list(sys.argv[1:] if argv is None else argv)
    lathe = SkillLathe()
    if args and args[0].strip() == "--selfcheck":
        print("== 技能机床自检 ==")
        print(json.dumps(lathe.selfcheck(), ensure_ascii=False, indent=2))
        return 0 if lathe.selfcheck()["ok"] else 1
    print("== HoloAeon 技能机床（Skill Lathe）==")
    tvcb = {
        "tvcb_id": "TVCB-TEST0001", "topic": {"primary": "test"},
        "keywords": ["AI", "agent"], "idea_pattern": "test pattern",
        "reusable_points": ["point1"], "energy_grade": "A",
    }
    spec = lathe.turn_skill(tvcb)
    print("TVCB → SkillSpec:", spec["name"] if spec else None)
    print("描述:", spec["description"] if spec else None)
    print("标签:", spec["tags"] if spec else None)
    return 0 if spec else 1


if __name__ == "__main__":
    sys.exit(main())
