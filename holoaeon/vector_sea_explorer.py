# -*- coding: utf-8 -*-
"""
vector_sea_explorer —— 向量海能源勘探+加工+分发平台（V13+V14 全流水线）
================================================================================
用户落地完整路径（9 阶段）：

  input → ocr → snapshot → search → refine → output → salvage
  → lathe（机床加工）→ protocol_export（协议适配导出）

比喻：石油矿藏（向量海 617 技能+195 篇+10 GEMS+462 项）→ 勘探平台 → 炼油厂
（技能机床）→ 输油管道（12 种平台协议）→ 部署到任意平台。

V14-SKILL-LATHE-PROTOCOL-PLUGINS · 纯标准库、零外部依赖、确定性、离线。
mineru OCR 为外部可选依赖，缺失时降级为纯文本直通。
"""
from __future__ import annotations

import json
import sys
from typing import Any, Dict, List, Optional

from .skill_lathe import SkillLathe
from .protocol_plugins import export_skill_to_protocol, list_protocols
from .packs.vector_sea_pack import (ocr_snapshot, vector_match,
                                    tensor_coupling, wisdom_salvage,
                                    multi_modal_scan)


def _stage(seq: List[str], name: str, payload: dict) -> dict:
    """阶段登记：把一步结果并入流水线记录。"""
    seq.append(name)
    return {"stages": seq, "stage": name, "payload": payload}


def explore(input_path: str = "", text: str = "",
            corpus: Optional[list] = None, energy: float = 0.6,
            protocol: str = "mineru_optional") -> dict:
    """1-7 阶段：勘探打捞（input→ocr→snapshot→search→refine→output→salvage）。

    protocol="mineru_optional"：mineru CLI 4.0.12 为外部可选依赖，
    缺失/不可用时自动降级为纯文本直通（本函数始终走确定性文本路径）。
    """
    seq: List[str] = []
    stages: Dict[str, Any] = {}

    # 1. input：接收端（PDF/图片/文字 —— 文字直通，文件路径记录）
    src = {"input_path": str(input_path or ""), "text_len": len(str(text or ""))}
    stages["input"] = _stage(seq, "input", src)

    # 2-3. ocr + snapshot：取样快照（TF-IDF 风格词频）
    snap = ocr_snapshot(text)
    stages["ocr_snapshot"] = _stage(seq, "ocr_snapshot", snap)

    # 4. search：向量海余弦搜索（矿藏语料）
    m = vector_match(text[:64], corpus or [])
    stages["search"] = _stage(seq, "search", m)

    # 5. refine：张量向量耦合体（TVCB）精炼
    tv = tensor_coupling(snap, m["matches"], energy=energy)
    stages["refine"] = _stage(seq, "refine", tv)

    # 6-7. output + salvage：TVCB 输出 + 智慧封存
    seal = wisdom_salvage(tv["tvcb"])
    stages["output"] = _stage(seq, "output", {"tvcb": tv["tvcb"]})
    stages["salvage"] = _stage(seq, "salvage", seal)

    return {"tvcb": tv["tvcb"], "seal": seal["seal"],
            "stages": seq, "snapshot": snap, "matches": m["matches"]}


def explore_and_manufacture(input_path: str = "", text: str = "",
                            corpus: Optional[list] = None,
                            energy: float = 0.6,
                            target_protocols: Optional[list] = None) -> dict:
    """勘探+加工+导出全流程（1-7 勘探 → 8 机床 → 9 协议导出）。

    target_protocols=None 时遍历穷举全部 12 种协议。
    """
    # 1-7: 勘探
    found = explore(input_path=input_path, text=text, corpus=corpus, energy=energy)
    seq = list(found["stages"])

    # 8: 机床加工（TVCB → SkillSpec）
    lathe = SkillLathe()
    spec = lathe.turn_skill(found["tvcb"])
    if spec is None:
        return {"status": "error", "error": "energy_grade_C_dropped",
                "hint": "TVCB 能量级 C（<0.4）被机床丢弃，无法加工",
                "tvcb": found["tvcb"], "stages": seq}
    spec_clean = {k: v for k, v in spec.items() if k != "fn"}
    seq.append("lathe")

    # 9: 协议导出（遍历穷举 12 种）
    protos = list(target_protocols) if target_protocols else list_protocols()
    exports = {proto: export_skill_to_protocol(spec_clean, proto)
               for proto in protos}
    seq.append("protocol_export")

    return {
        "status": "ok",
        "tvcb": found["tvcb"],
        "skill_spec": spec_clean,
        "protocol_exports": exports,
        "protocol_count": len(exports),
        "stages": seq,
        "salvaged_at": "2026-11-03T23:05+08:00",
    }


def main(argv=None) -> int:
    """CLI 入口（pyproject holoaeon-explore）：端到端演示（9 阶段）。"""
    args = list(sys.argv[1:] if argv is None else argv)
    text = " ".join(args) if args else \
        "向量海 勘探 技能机床 协议适配 平台 智慧打捞 张量耦合 能量分级"
    print("== HoloAeon 向量海能源勘探+加工+分发平台（9 阶段流水线）==")
    result = explore_and_manufacture(text=text, energy=0.85)
    if result["status"] != "ok":
        print("流水线终止:", result["hint"])
        return 1
    print("阶段:", " → ".join(result["stages"]))
    print("TVCB:", result["tvcb"]["tvcb_id"],
          "主题:", result["tvcb"]["topic"]["primary"],
          "能量级:", result["tvcb"]["energy_grade"])
    print("SkillSpec:", result["skill_spec"]["name"])
    print("协议导出数:", result["protocol_count"])
    print("协议:", ", ".join(result["protocol_exports"].keys()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
