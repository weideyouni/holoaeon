"""三种"编译模式"：把界面源码当电路网表来处理。

借 EDA / VHDL 的三段式做确定性映射，便于把"设计评审"变成可复算流程：
- elaborate（分析/elaboration）：把 HTML 与样式声明展开成元件与端口。
- simulate（仿真）：跑 detectors，得到带分级的命中波形。
- netlist（综合/网表）：把"规则 → 经络通道"的边收敛成一张可复核的网表。

三段都只读文本、纯函数、无随机、无网络、无模型调用。
"""

from __future__ import annotations

import re
from typing import Dict, List, Sequence

from . import detectors as dv_detectors
from .detectors import Finding

COMPILE_MODES = (
    ("elaborate", "展开：源码 → 元件/端口清单", "对应 VHDL 的 elaboration"),
    ("simulate", "仿真：元件清单 → P0–P3 命中", "对应 testbench 跑波形"),
    ("netlist", "综合：命中 → 规则/通道网表", "对应 netlist / 综合结果"),
)

_TAG = re.compile(r"<([a-zA-Z][a-zA-Z0-9]*)([^>]*)>")
_ATTR = re.compile(r"([a-zA-Z_:][-a-zA-Z0-9_:.]*)\s*=\s*\"([^\"]*)\"")
_DECL = re.compile(r"([a-zA-Z-]+)\s*:\s*([^;{}]+);")


def elaborate(text: str) -> Dict[str, object]:
    """展开为元件与端口：每个标签一个元件，属性与样式声明各算一个端口。"""
    components: List[Dict[str, object]] = []
    ports = 0
    for m in _TAG.finditer(text):
        tag = m.group(1).lower()
        attrs = m.group(2) or ""
        names = [a[0] for a in _ATTR.findall(attrs)]
        decls = [d[0] for d in _DECL.findall(attrs)]
        port_count = len(names) + len(decls)
        ports += port_count
        components.append({"kind": tag, "ports": port_count})
    return {
        "mode": "elaborate",
        "components": len(components),
        "ports": ports,
        "kinds": sorted({c["kind"] for c in components}),
    }


def simulate(text: str) -> Dict[str, object]:
    """跑一遍确定性检测，返回分级统计与"先修清单"。"""
    hits: List[Finding] = dv_detectors.scan(text)
    by_sev = {s: 0 for s in dv_detectors.SEVERITY_ORDER}
    for h in hits:
        by_sev[h.severity] += 1
    ordered = dv_detectors.rank(hits)
    return {
        "mode": "simulate",
        "findings": len(hits),
        "by_severity": by_sev,
        "first_fix": ordered[0].rule if ordered else "",
        "verdict": "FAIL" if by_sev["P0"] else ("WARN" if hits else "PASS"),
        "rules_hit": sorted({h.rule for h in hits}),
    }


def netlist(findings: Sequence[Finding]) -> Dict[str, object]:
    """把命中收敛成"规则 → 通道"网表边，边权为命中次数。"""
    edges: Dict[str, int] = {}
    nodes = set()
    for f in findings:
        key = "%s>%s" % (f.rule, f.channel)
        edges[key] = edges.get(key, 0) + 1
        nodes.add(f.rule)
        nodes.add(f.channel)
    return {
        "mode": "netlist",
        "nodes": len(nodes),
        "edges": len(edges),
        "weights": dict(sorted(edges.items())),
    }


def compile_text(text: str) -> Dict[str, object]:
    """三模式串起来跑一遍，返回完整"编译结果"。"""
    el = elaborate(text)
    sim = simulate(text)
    nl = netlist(dv_detectors.scan(text))
    return {"elaborate": el, "simulate": sim, "netlist": nl}
