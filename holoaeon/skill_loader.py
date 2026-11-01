# -*- coding: utf-8 -*-
"""
SkillLoader —— 渐进式技能加载（W17 之二，旁挂）
================================================================================
manifest 常驻（名字 + 描述 + 标签，永远在上下文里），正文只在"确定相关"时读。
无关技能不消耗上下文；裁剪后路由命中率不允许下降（用 eval set 验证，V3-7）。

正文来源：仓库 `skills/<name>/SKILL.md`（不存在则视为无正文）。

纯标准库。
"""
from __future__ import annotations

import os
from typing import Dict, List, Optional, Tuple

from .skill import SkillRegistry, ngram_dice


class SkillLoader:
    """两级加载：manifest（常驻）+ body（按需）。"""

    def __init__(self, registry: SkillRegistry, skills_root: str = "") -> None:
        self.registry = registry
        self.skills_root = skills_root
        self._bodies: Dict[str, str] = {}
        self.manifest_reads = 0
        self.body_reads = 0

    # ------------------------------------------------------------ manifest
    def manifest(self) -> List[dict]:
        """常驻清单：只含路由所需字段，不含正文。"""
        self.manifest_reads += 1
        return [{"name": s.name, "description": s.manifest.description,
                 "tags": list(s.manifest.tags),
                 "inputs": dict(s.manifest.inputs)}
                for s in self.registry.all()]

    def manifest_text(self) -> str:
        return " ".join("%s %s %s" % (m["name"], m["description"],
                                      " ".join(m["tags"]))
                        for m in self.manifest())

    # ------------------------------------------------------------ body
    def body_path(self, name: str) -> str:
        return os.path.join(self.skills_root, name, "SKILL.md")

    def has_body(self, name: str) -> bool:
        return bool(self.skills_root) and os.path.exists(self.body_path(name))

    def body(self, name: str) -> str:
        """读正文（带进程内缓存）；只对确实相关的技能调用。"""
        if name in self._bodies:
            return self._bodies[name]
        p = self.body_path(name)
        if not self.skills_root or not os.path.exists(p):
            self._bodies[name] = ""
            return ""
        with open(p, "r", encoding="utf-8") as fh:
            text = fh.read()
        self._bodies[name] = text
        self.body_reads += 1
        return text

    # ------------------------------------------------------------ 按需路由
    def relevant(self, query: str, k: int = 3, threshold: float = 0.15
                 ) -> List[Tuple[str, float]]:
        """只用 manifest 打分挑候选；正文一次都不读。"""
        cands = self.registry.match(query, k=k)
        return [(n, sc) for n, sc in cands if sc >= threshold]

    def resolve(self, query: str, k: int = 1) -> List[dict]:
        """返回候选 + 该候选的正文（这是唯一会读正文的入口）。"""
        out = []
        for name, score in self.relevant(query, k=k):
            out.append({"name": name, "score": score,
                        "body": self.body(name),
                        "loaded": bool(self._bodies.get(name))})
        return out

    # ------------------------------------------------------------ 体检
    def stats(self) -> dict:
        return {"skills": len(self.registry.all()),
                "manifest_reads": self.manifest_reads,
                "body_reads": self.body_reads,
                "bodies_cached": len([v for v in self._bodies.values() if v]),
                "skills_root": self.skills_root}

    def routing_accuracy(self, cases: List[dict]) -> dict:
        """用 eval cases 验证：裁剪不得降低命中率。"""
        ok, total = 0, 0
        detail = []
        for case in cases:
            total += 1
            got = self.registry.best(case["input"])
            hit = got == case["reference"]
            ok += 1 if hit else 0
            detail.append({"input": case["input"], "expect": case["reference"],
                           "got": got, "ok": hit})
        return {"ok": ok, "total": total,
                "accuracy": round(ok / total, 4) if total else 0.0,
                "detail": detail}

    def body_guard(self, query: str, k: int = 3) -> dict:
        """裁剪纪律：只有候选能读正文，其余技能正文读数为 0。"""
        loaded_before = {n: n in self._bodies for n in self.registry.names()}
        picked = self.resolve(query, k=k)
        loaded_after = {n: n in self._bodies for n in self.registry.names()}
        newly = [n for n in loaded_after if loaded_after[n] and not loaded_before.get(n)]
        allowed = {p["name"] for p in picked}
        return {"query": query, "picked": sorted(allowed),
                "newly_loaded": newly,
                "violations": sorted(set(newly) - allowed)}
