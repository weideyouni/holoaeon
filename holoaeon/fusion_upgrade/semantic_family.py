# -*- coding: utf-8 -*-
"""B5 · 语义技能族（semantic skill family）可调用入口

定位：把 `data/semantic_family.json`（60 条、落 ivsa 十模块）读成确定性查询接口。
本模块只读数据，不 import ivsa，不执行任何技能，不改变九包/47 技能/25 智能体维度。

用法：
    from holoaeon.fusion_upgrade.semantic_family import Family
    fam = Family.load()
    fam.count()                       # 60
    fam.modules()                     # 十模块名（固定顺序）
    fam.by_module("检索")             # 该模块成员
    fam.route("向量检索与指纹去重")    # 按十模块锚点确定性路由（可多命中）
    fam.lookup("kangfu-knowledge-suite")
"""
from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, "data", "semantic_family.json")
SPEC = os.path.join(ROOT, "data", "semantic_modules.json")


class Family(object):
    def __init__(self, doc, spec):
        self.doc = doc
        self.spec = spec
        self.members = doc["members"]
        self.modules_list = [m["name"] for m in spec["modules"]]
        self.anchors = {m["name"]: list(m["anchors"]) for m in spec["modules"]}
        self.default_module = spec["default_module"]

    @classmethod
    def load(cls, family_path=None, spec_path=None):
        with open(family_path or DATA, "r", encoding="utf-8") as f:
            doc = json.load(f)
        with open(spec_path or SPEC, "r", encoding="utf-8") as f:
            spec = json.load(f)
        return cls(doc, spec)

    def count(self):
        return len(self.members)

    def modules(self):
        return list(self.modules_list)

    def by_module(self, name):
        if name not in self.modules_list:
            raise KeyError("未知语义模块：%s，可选：%s" % (name, self.modules_list))
        return [m for m in self.members if m["module"] == name]

    def bridge_candidates(self):
        return list(self.doc.get("bridge_candidates") or [])

    def lookup(self, skill):
        for m in self.members:
            if m["skill"] == skill:
                return dict(m)
        for b in self.bridge_candidates():
            if b["skill"] == skill:
                return dict(b)
        return None

    def route(self, text):
        """确定性路由：命中锚点即返回该模块；零命中回落到 default_module（与 ivsa route 默认一致）。"""
        text = (text or "").lower()
        out = []
        for name in self.modules_list:
            if any(a.lower() in text for a in self.anchors[name]):
                out.append(name)
        return out or [self.default_module]

    def coverage(self):
        return {n: len(self.by_module(n)) for n in self.modules_list}

    def verify(self):
        return {
            "family_id": self.doc.get("family_id"),
            "members": self.count(),
            "modules": len(self.modules_list),
            "uncovered": [n for n, c in self.coverage().items() if c == 0],
            "bridge": len(self.bridge_candidates()),
            "ok": (self.count() >= 60
                   and len(self.modules_list) == 10
                   and all(c > 0 for c in self.coverage().values())),
        }
