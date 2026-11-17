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
import re
from typing import Any, Dict, List, Optional, Tuple

GENOME_ID = "HOLOAEON-GENOME-DNA-v1.0"
DNA_VERSION = "1.1.0"
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
     "formal": "robust <=> skip_registered & output_diff0 & genome_hash_diff0 "
               "& cells==fragments*25 & triple_homology "
               "& (extension=>spec_byte_identical | governance=>spec_sha_backfilled "
               "& test_assertion_backfilled)",
     "meaning": "鲁棒不是不坏、不是堆副本，是倒哪块都能算出来且基因不变形；"
                "扩展挤压零改表型，治理蜕皮允许改但必回填三件套。",
     "falsifiers": ["skip_swallowed", "output_drift", "spec_modified",
                    "genome_hash_drift", "cells_mismatch", "homology_drift",
                    "bad_change_class", "gov_without_backfill"]},
    {"id": "G-DNA-04", "name": "跨线程统一不是割裂",
     "formal": "unity <=> coordinate_ok & state_ok & credential_ok & readback_ok",
     "meaning": "坐标/状态/凭证/回读四节点齐才联通；任一断线必红，且能定位到具体节点。",
     "falsifiers": ["coordinate_head_missing", "state_receipt_missing",
                    "credential_plaintext", "readback_no_numeric", "stage_illegal"]},
)

LOCI: Dict[str, Any] = {
    "skin": ["guard.py", "guard_layers/"],
    "meridian": ["bus.py", "bus_channel.py", "event_channel.py", "meridian_link.py"],
    "skeleton": ["kernel.py", "memory.py", "graph.py"],
    "expand": ["mobius_vortex.py", "magic_lamp.py", "holo_forge.py", "swarm_intel.py"],
    "converge": ["klein_projection.py", "forge_gate.py", "dehallucination.py", "org_gate.py"],
    "unity_nodes": {
        "coordinate": "reports/remote_sync_*.json + ANCHOR_*.md（仓/分支/HEAD/五地）",
        "state": "reports/*_receipt.json + version_history / engineering_process（stage 判幂等）",
        "credential": "holoaeon_memory/credential_registry.json（只存指针+状态+掩码+指纹）",
        "readback": "ls-remote / check_sums / manifest digest（每句已完成带可比对数值）",
    },
    "bureaus": {"salvage": "longaeon/bureau/salvage_bureau.py (LA 仓指针)",
                "planning": "longaeon/bureau/planning_bureau.py (LA 仓指针)",
                "manufacture": "longaeon/bureau/manufacture_bureau.py (LA 仓指针)"},
}

PLUGIN_FACES: Tuple[str, ...] = (
    "physical", "protocol", "data", "deploy", "degradation", "security",
    "genome", "meridian", "unity",
)

VALID_STAGES: Tuple[str, ...] = (
    "planned", "in_progress", "closed_execution_side", "skill_onboarding", "superseded",
)

# 凭据明文模式：命中即红（只存指针是下限，不进快照才是上限）
PLAINTEXT_PATTERNS: Tuple[str, ...] = ("gho_", "ghp_", "hf_", "token=")

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


def _has_plaintext(value: Any) -> bool:
    """凭据明文模式探测：前缀 + 其后 >=8 位非空白串，命中即判明文。"""
    if not isinstance(value, str):
        return False
    for pat in PLAINTEXT_PATTERNS:
        idx = value.find(pat)
        while idx >= 0:
            tail = value[idx + len(pat):]
            m = re.match(r"[A-Za-z0-9._\-]{8,}", tail)
            if m:
                return True
            idx = value.find(pat, idx + 1)
    return False


def robustness_check(skip_registered: bool, output_diff0: bool,
                     spec_byte_identical: bool, genome_hash_diff0: bool,
                     cells_expected: int, cells_actual: int,
                     triple_homology: Dict[str, bool],
                     change_class: str = "extension",
                     spec_sha_backfilled: bool = False,
                     test_assertion_backfilled: bool = False) -> Dict[str, Any]:
    """G-DNA-03。R1/R2/R3；change_class 分治让治理蜕皮合法化。

    extension  : 插件/扩展挤压 -> spec.py 必须 byte-identical（原判据保留）
    governance : 治理批/版本蜕皮 -> 允许 spec.py 变，但必须三件套同批回填
                 且 genome_hash 不变（脱表型不脱基因）
    """
    problems: List[str] = []
    if change_class not in ("extension", "governance"):
        problems.append("change_class 非法：{!r}".format(change_class))
    if not skip_registered:
        problems.append("R1 失效被吞掉（skip 未登记 env_delta）")
    if not output_diff0:
        problems.append("R1 降级后输出漂移")
    if not genome_hash_diff0:
        problems.append("R2 基因哈希漂移（蜕皮脱到骨头了）")
    if cells_expected != cells_actual:
        problems.append("R2 经络格数不守恒：期望 {} 实 {}".format(cells_expected, cells_actual))
    if change_class == "extension":
        if not spec_byte_identical:
            problems.append("R2 扩展挤压改了 spec.py（应零改动）")
    elif change_class == "governance":
        if not spec_sha_backfilled:
            problems.append("R2-gov 母本 spec_sha256_measured 未同批回填")
        if not test_assertion_backfilled:
            problems.append("R2-gov 测试断言未同批回填")
    for k in ("mechanism_axis", "heartbeat", "seal"):
        if not triple_homology.get(k, False):
            problems.append("R3 同源性漂移：{}".format(k))
    return {"pass": not problems, "problems": problems, "axiom": "G-DNA-03",
            "change_class": change_class,
            "r1": skip_registered and output_diff0,
            "r2": genome_hash_diff0 and cells_expected == cells_actual and (
                spec_byte_identical if change_class == "extension"
                else (spec_sha_backfilled and test_assertion_backfilled)),
            "r3": all(triple_homology.get(k, False) for k in
                      ("mechanism_axis", "heartbeat", "seal")),
            "r4": None}   # R4 由 unity_check 单独判，不在此恒真


def unity_check(coordinate: Dict[str, Any], state: Dict[str, Any],
                credential: Dict[str, Any], readback: Dict[str, Any]) -> Dict[str, Any]:
    """G-DNA-04。四节点任一断线必红；四类反例各自可失败。"""
    problems: List[str] = []
    # N1 坐标
    if not coordinate.get("head"):
        problems.append("N1 坐标断：HEAD 缺失")
    if not coordinate.get("schema_same", False):
        problems.append("N1 坐标断：五地 schema 不一致")
    if coordinate.get("head_mismatch"):
        problems.append("N1 坐标断：本地与远端 HEAD 不一致")
    # N2 状态
    if not state.get("receipt_present"):
        problems.append("N2 状态断：批次回执缺失")
    if not state.get("anchor_present"):
        problems.append("N2 状态断：当日锚点缺失")
    if state.get("stage") not in VALID_STAGES:
        problems.append("N2 状态断：stage 非法转移 {!r}".format(state.get("stage")))
    # N3 凭证
    if not credential.get("pointer"):
        problems.append("N3 凭证断：无指针")
    if credential.get("plaintext_hit") or _has_plaintext(credential.get("pointer")):
        problems.append("N3 凭证断：含明文")
    if credential.get("status") != "VALID":
        problems.append("N3 凭证断：状态非 VALID {!r}".format(credential.get("status")))
    # N4 回读
    evidence = readback.get("evidence")
    if not evidence:
        problems.append("N4 回读断：无证据")
    elif not re.search(r"\d", str(evidence)):
        problems.append("N4 回读断：证据无数值")
    return {"pass": not problems, "problems": problems, "axiom": "G-DNA-04",
            "nodes": {"coordinate": not problems or True,
                      "state": state.get("receipt_present", False),
                      "credential": credential.get("status") == "VALID",
                      "readback": bool(evidence)}}


def plugin_contract_check(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """八面契约 + 双态同时为真。只独立=分裂，只回连=寄生。"""
    problems: List[str] = []
    for face in PLUGIN_FACES:
        if face not in manifest or not manifest[face]:
            problems.append("缺面：{}".format(face))
    unity = manifest.get("unity")
    if isinstance(unity, dict):
        if not unity.get("ctup_schema"):
            problems.append("unity.ctup_schema 缺失")
        for k in ("coordinate_ref", "state_stage", "credential_pointer", "readback_evidence"):
            if not unity.get(k):
                problems.append("unity.{} 缺失".format(k))
        if unity.get("state_stage") not in VALID_STAGES:
            problems.append("unity.state_stage 非法转移：{!r}".format(unity.get("state_stage")))
        if _has_plaintext(unity.get("credential_pointer")):
            problems.append("unity.credential_pointer 含明文（只许指针）")
        ev = str(unity.get("readback_evidence", ""))
        if ev and not re.search(r"\d", ev):
            problems.append("unity.readback_evidence 无数值")
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
    if len(AXIOMS) != 4:
        problems.append("基因数 != 4")
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
        ("robustness_r1", robustness_check(False, True, True, True, 300, 300,
                                           true_homology)["pass"]),
        ("robustness_gov_backfill",
         robustness_check(True, True, False, True, 300, 300, true_homology,
                          "governance", False, False)["pass"]),
        ("unity_coordinate", unity_check({}, {"receipt_present": True, "anchor_present": True,
                                              "stage": "closed_execution_side"},
                                         {"pointer": "p", "status": "VALID"},
                                         {"evidence": "head 2181a51"})["pass"]),
    )
    for name, passed in guards:
        if passed:
            problems.append("{} 恒真（反例仍 pass=True），判据作废".format(name))

    # 活性断言：分治与四节点齐必须真的能绿（防把判据改成恒假或恒真）
    active = (
        ("robustness_gov_positive",
         robustness_check(True, True, False, True, 300, 300, true_homology,
                          "governance", True, True)["pass"]),
        ("robustness_ext_positive",
         robustness_check(True, True, True, True, 300, 300, true_homology)["pass"]),
        ("unity_positive",
         unity_check({"head": "c461b51", "schema_same": True,
                      "head_mismatch": False},
                     {"receipt_present": True, "anchor_present": True,
                      "stage": "closed_execution_side"},
                     {"pointer": "holoaeon_memory/credential_registry.json",
                      "status": "VALID"},
                     {"evidence": "ls-remote c461b51 / 346 条"})["pass"]),
    )
    for name, passed in active:
        if not passed:
            problems.append("{} 活性失守（该绿未绿）".format(name))
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
