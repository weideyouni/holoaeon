# -*- coding: utf-8 -*-
"""HoloAeon 内核基因 DNA（V86 · 旁挂件，零侵入 spec.py）。

三条内核基因固化为**可失败断言**，不是散文：
  G-DNA-01 生长不是分裂：Δedges>0 ∧ Δcopies=0 → growth；Δcopies>0 → split
  G-DNA-02 分化不是分裂：表型专化 ∧ 基因型同源（三同源 DIFF=0）→ differentiation
  G-DNA-03 鲁棒性真义：局部失效可计量 ∧ 扩展挤压下同源守恒 ∧ 输出确定性

纪律：纯标准库 / 零网络 / 零第三方 / 确定性（self_check 两次 DIFF=0）/
      spec.py 零改动 / 插件源码零复制 / 跨仓零 import / neural=false / claim=0。
封存密令：潮起开门，潮落闭嘴
"""
from __future__ import annotations

import hashlib
import json
import os
from typing import Any, Dict, List, Optional, Tuple

GENOME_ID = "HOLOAEON-GENOME-DNA-v1.0"
DNA_VERSION = "1.0.0"
SCHEMA = "HOLOAEON-GENOME-REGISTRY-v1.0"
SEAL = "潮起开门，潮落闭嘴"

# 25 项机制轴：语义抄录自 holoaeon.meridian_link.KERNEL_MECHANISMS，
# 零 import（避免循环依赖，也守「跨仓语义抄录零 import」纪律）。
MECHANISM_AXIS: Tuple[str, ...] = (
    "A1", "A2", "X1", "X2",
    "M01", "M02", "M03", "M04", "M05", "M06", "M07", "M08", "M09", "M10", "M11",
    "C1", "C2",
    "R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8",
)

HOMOLOGY: Dict[str, Any] = {
    "mechanism_axis": list(MECHANISM_AXIS),
    "heartbeat": {"bodies": 70, "dim": 768, "channels": 17},
    "seal": SEAL,
    "protocol_family": ["HOLOAEON", "SSYD"],
}

AXIOMS: Tuple[Dict[str, Any], ...] = (
    {"id": "G-DNA-01", "name": "生长不是分裂",
     "formal": "growth <=> dEdges>0 & dCopies==0 & link_back>=1 & family_shared & seal_shared; "
               "split <=> dCopies>0 | (dEdges==0 & link_back==0)",
     "meaning": "生长增加回连边，分裂增加母体副本。",
     "falsifiers": ["dCopies>0", "link_back==0", "seal_mismatch", "family_mismatch",
                    "dEdges==0"]},
    {"id": "G-DNA-02", "name": "分化不是分裂",
     "formal": "differentiation <=> genome_similarity>=theta & triple_homology_diff0 "
               "& function_specialized & theta is not None",
     "meaning": "分化 = 表型千姿百态 + 基因型一字不改。",
     "falsifiers": ["theta_is_None", "similarity_below_theta", "mechanism_axis_missing",
                    "heartbeat_dim_drift", "seal_mismatch", "not_specialized",
                    "genome_similarity_hardcoded"]},
    {"id": "G-DNA-03", "name": "系统鲁棒性的真正含义",
     "formal": "robust <=> skip_registered & output_diff0 & spec_byte_identical "
               "& genome_hash_diff0 & cells==fragments*25 & triple_homology",
     "meaning": "鲁棒不是不坏、不是堆副本，是倒哪块都能算出来且基因不变形。",
     "falsifiers": ["skip_swallowed", "output_drift", "spec_modified",
                    "genome_hash_drift", "cells_mismatch", "homology_drift"]},
)

LOCI: Dict[str, Any] = {
    "skin": ["guard.py", "guard_layers/"],
    "meridian": ["bus.py", "bus_channel.py", "event_channel.py", "meridian_link.py"],
    "skeleton": ["kernel.py", "memory.py", "graph.py"],
    "expand": ["mobius_vortex.py", "magic_lamp.py", "holo_forge.py", "swarm_intel.py"],
    "converge": ["klein_projection.py", "forge_gate.py", "dehallucination.py", "org_gate.py"],
    "bureaus": {"salvage": "longaeon/bureau/salvage_bureau.py (LA 仓指针)",
                "planning": "longaeon/bureau/planning_bureau.py (LA 仓指针)",
                "manufacture": "longaeon/bureau/manufacture_bureau.py (LA 仓指针)"},
}

PLUGIN_FACES: Tuple[str, ...] = (
    "physical", "protocol", "data", "deploy", "degradation", "security",
    "genome", "meridian",
)

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_REGISTRY_PATH = os.path.join(_ROOT, "data", "genome_dna_registry.json")
_DNA_PATH = os.path.join(_ROOT, "data", "genome_dna.json")


# --------------------------------------------------------------------------
# 三基因：每条都必须能红
# --------------------------------------------------------------------------

def growth_check(delta_edges: int, delta_copies: int, link_back: int,
                 protocol_family: str, seal: str) -> Dict[str, Any]:
    """G-DNA-01。返回 pass/verdict/problems；反例必须 pass=False。"""
    problems: List[str] = []
    for label, v in (("delta_edges", delta_edges), ("delta_copies", delta_copies),
                     ("link_back", link_back)):
        if not isinstance(v, int) or isinstance(v, bool) or v < 0:
            problems.append("{} 必须是非负整数（实 {!r}）".format(label, v))
    if seal != SEAL:
        problems.append("seal 不同源")
    if protocol_family not in HOMOLOGY["protocol_family"]:
        problems.append("protocol_family 不在基因族内：{!r}".format(protocol_family))

    if problems:
        return {"pass": False, "verdict": "invalid", "problems": problems,
                "axiom": "G-DNA-01"}
    if delta_copies > 0:
        return {"pass": False, "verdict": "split", "problems": ["Δcopies>0：母体副本增加"],
                "axiom": "G-DNA-01"}
    if delta_edges == 0 and link_back == 0:
        return {"pass": False, "verdict": "split", "problems": ["新节点无回连指针"],
                "axiom": "G-DNA-01"}
    if delta_edges <= 0 or link_back < 1:
        return {"pass": False, "verdict": "invalid",
                "problems": ["未构成生长：Δedges={} / link_back={}".format(delta_edges, link_back)],
                "axiom": "G-DNA-01"}
    return {"pass": True, "verdict": "growth", "problems": [], "axiom": "G-DNA-01",
            "delta_edges": delta_edges, "delta_copies": delta_copies,
            "link_back": link_back}


def differentiation_check(genome_similarity: Optional[float],
                          triple_homology: Dict[str, bool],
                          function_specialized: bool,
                          theta: Optional[float]) -> Dict[str, Any]:
    """G-DNA-02。theta 未标定（None）必红；禁写死 1.0。"""
    problems: List[str] = []
    if theta is None:
        problems.append("theta 未实测标定（禁写死 / 禁默认 1.0）")
    elif not (0.0 < theta < 1.0):
        problems.append("theta 越界（须 0<theta<1.0，禁 1.0）：{!r}".format(theta))
    if genome_similarity is None:
        problems.append("genome_similarity 缺失")
    elif theta is not None and genome_similarity < theta:
        problems.append("genome_similarity 低于 theta")
    required = ("mechanism_axis", "heartbeat", "seal")
    for k in required:
        if not triple_homology.get(k, False):
            problems.append("三同源失守：{}".format(k))
    if not function_specialized:
        problems.append("表型未专化（不构成分化）")
    return {"pass": not problems, "verdict": "differentiation" if not problems else "split",
            "problems": problems, "axiom": "G-DNA-02", "theta": theta,
            "genome_similarity": genome_similarity}


def robustness_check(skip_registered: bool, output_diff0: bool,
                     spec_byte_identical: bool, genome_hash_diff0: bool,
                     cells_expected: int, cells_actual: int,
                     triple_homology: Dict[str, bool]) -> Dict[str, Any]:
    """G-DNA-03。三个子判据 R1/R2/R3 任一失守即红。"""
    problems: List[str] = []
    if not skip_registered:
        problems.append("R1 失效被吞掉（skip 未登记 env_delta）")
    if not output_diff0:
        problems.append("R1 降级后输出漂移")
    if not spec_byte_identical:
        problems.append("R2 靠改冻结契约换能跑（spec.py 非 byte-identical）")
    if not genome_hash_diff0:
        problems.append("R2 扩展挤压后基因哈希漂移")
    if cells_expected != cells_actual:
        problems.append("R2 经络格数不守恒：期望 {} 实 {}".format(cells_expected, cells_actual))
    for k in ("mechanism_axis", "heartbeat", "seal"):
        if not triple_homology.get(k, False):
            problems.append("R3 同源性漂移：{}".format(k))
    return {"pass": not problems, "problems": problems, "axiom": "G-DNA-03",
            "r1": skip_registered and output_diff0,
            "r2": spec_byte_identical and genome_hash_diff0 and cells_expected == cells_actual,
            "r3": all(triple_homology.get(k, False) for k in
                      ("mechanism_axis", "heartbeat", "seal"))}


def plugin_contract_check(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """八面契约 + 双态同时为真。只独立=分裂，只回连=寄生。"""
    problems: List[str] = []
    for face in PLUGIN_FACES:
        if face not in manifest or not manifest[face]:
            problems.append("缺面：{}".format(face))
    standalone = bool(manifest.get("standalone_ok"))
    genomic = bool(manifest.get("genomic_ok"))
    if standalone and not genomic:
        problems.append("分裂：只独立不回连（孤儿插件）")
    if genomic and not standalone:
        problems.append("寄生：只回连不独立（不可插拔）")
    if not standalone and not genomic:
        problems.append("双态皆假")
    link_back = manifest.get("meridian", {}).get("link_back", 0) if isinstance(
        manifest.get("meridian"), dict) else 0
    if genomic and link_back < 1:
        problems.append("meridian.link_back < 1")
    return {"pass": not problems, "problems": problems, "faces": len(PLUGIN_FACES),
            "standalone_ok": standalone, "genomic_ok": genomic,
            "dual_state_ok": standalone and genomic and not problems}


# --------------------------------------------------------------------------
# 基因组哈希与自校验
# --------------------------------------------------------------------------

def genome_hash() -> str:
    """canonical(AXIOMS + HOMOLOGY + LOCI) 的 SHA256；扩展挤压前后必须 DIFF=0。"""
    canonical = {"axioms": list(AXIOMS), "homology": HOMOLOGY, "loci": LOCI}
    raw = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def verify() -> Dict[str, Any]:
    """缺面/非法态/恒真判据必红。"""
    problems: List[str] = []
    if len(AXIOMS) != 3:
        problems.append("基因数 != 3")
    if len(MECHANISM_AXIS) != 25 or len(set(MECHANISM_AXIS)) != 25:
        problems.append("25 机制轴不自洽")
    for a in AXIOMS:
        if not a.get("falsifiers"):
            problems.append("{} 缺 falsifier".format(a["id"]))
    # SEAL 漂移对账：与 DNA 母本 data/genome_dna.json 的 seal 字段比对。
    # V86 批3 修正——原先写成 `SEAL != "潮起开门，潮落闭嘴"`（常量对常量，
    # 恒假死守卫），被 A14 恒真金哨如实抓出。改成读母本后：改母本 seal 即红。
    seal_master_path = os.path.join(_ROOT, "data", "genome_dna.json")
    try:
        with open(seal_master_path, "r", encoding="utf-8") as fh:
            _master = json.load(fh)
        if _master.get("seal") != SEAL:
            problems.append("SEAL 与母本不一致：{!r} != {!r}"
                            .format(SEAL, _master.get("seal")))
    except FileNotFoundError:
        problems.append("DNA 母本缺失：{}".format(seal_master_path))
    except (OSError, ValueError) as exc:
        problems.append("DNA 母本不可解析：{}: {}".format(type(exc).__name__, exc))

    # 恒真守卫：每个 check 至少存在一组 pass=False 输入（V82/V83/V84 血脉）
    true_homology = {"mechanism_axis": True, "heartbeat": True, "seal": True}
    guards = (
        ("growth_check", growth_check(1, 1, 1, "HOLOAEON", SEAL)["pass"]),
        ("differentiation_check",
         differentiation_check(0.9, true_homology, True, None)["pass"]),
        ("robustness_check",
         robustness_check(False, True, True, True, 250, 250, true_homology)["pass"]),
        ("plugin_contract_check", plugin_contract_check({"standalone_ok": True})["pass"]),
    )
    for name, passed in guards:
        if passed:
            problems.append("{} 恒真（反例仍 pass=True），判据作废".format(name))
    return {"pass": not problems, "problems": problems,
            "axioms": len(AXIOMS), "mechanisms": len(MECHANISM_AXIS),
            "falsifiers": sum(len(a["falsifiers"]) for a in AXIOMS),
            "guards": len(guards)}


def self_check() -> Dict[str, Any]:
    """确定性 JSON：两次调用 DIFF=0。"""
    v = verify()
    return {
        "schema": GENOME_ID, "dna_version": DNA_VERSION, "seal": SEAL,
        "genome_hash": genome_hash(), "axioms": [a["id"] for a in AXIOMS],
        "mechanism_axis_size": len(MECHANISM_AXIS), "faces": len(PLUGIN_FACES),
        "verify": v, "spec_touched": False, "neural": False, "claim": 0,
    }


# --------------------------------------------------------------------------
# 经络碎片登记（供 meridian_link.load_fragments 合并；零复制历史 B 榜）
# --------------------------------------------------------------------------

def registered_fragments(path: Optional[str] = None) -> List[Dict[str, Any]]:
    """从 DNA 注册表读取**双态同时为真**的插件，转成经络碎片 row。

    历史 B 榜 10 条保持 append-only 不动；新增碎片只从注册表来。
    path 参数仅供测试注入临时注册表，生产调用恒用默认路径。
    """
    p = path or _REGISTRY_PATH
    if not os.path.isfile(p):
        return []
    with open(p, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if data.get("schema") != SCHEMA:
        raise ValueError("注册表 schema 非 {}：{!r}".format(SCHEMA, data.get("schema")))
    rows: List[Dict[str, Any]] = []
    seen = set()
    for item in data.get("plugins", []):
        if not (item.get("standalone_ok") and item.get("genomic_ok")):
            continue
        repo = item.get("repo")
        if not repo or repo in seen:
            raise ValueError("插件 repo 缺失或重复：{!r}".format(repo))
        if item.get("verify_status") != "unverified":
            raise ValueError("插件 verify_status 非 unverified（诚实口径）：{}".format(repo))
        if item.get("leg") not in ("编排", "总线", "可观测"):
            raise ValueError("插件 leg 非法：{} -> {!r}".format(repo, item.get("leg")))
        seen.add(repo)
        rows.append({"repo": repo, "rank": item.get("rank"),
                     "leg": item.get("leg"), "essence": item.get("essence"),
                     "verify_status": "unverified", "origin": "genome_dna_registry"})
    return rows


def main() -> int:
    out = self_check()
    print(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if out["verify"]["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
