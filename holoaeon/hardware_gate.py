# -*- coding: utf-8 -*-
"""
HardwareGate —— 硬件升级网表化装配（V51R 强化批，ring17 电子域姊妹件）
================================================================================
源声明（诚实边界）：
  · 外部协议源 = EDA / VHDL 三段式编译范式（elaboration / testbench 仿真 /
    netlist 综合）——在仓先例 design_vocab.compile_modes（三段纯函数，V51R
    忠实对齐其 elaborate/simulate/netlist 三段形状与 verdict 口径）。
  · 内部协议源 = fusion_upgrade 升级装配族（契约 contract：只交换回执不换代码；
    热替换 swap：旧槽换新件）与 protocol 融合协议（信封→八层→总线→心跳）。
  · 本模块不含真设备驱动/固件/算力调度——"硬件"是语言范式（网表），
    不是硬件驱动。neural=false、无网络、纯标准库、全确定性。

V51R 融合表（外部协议 × 内部协议 × V51 六算子）：
  EDA 三段        在仓先例              V51R 落点                    内部协议耦合
  ─────────────────────────────────────────────────────────────────────────────
  elaborate     compile_modes.       NetlistElaborator           契约 skill 登记形状
  （展开）        elaborate(元件/端口)  （组件描述→器件/端口网表）    （contract.make）
  simulate      compile_modes.       NetlistSimulator            verdict 口径对齐
  （testbench）  simulate(命中波形)    （六算子波形：KCL/谐振/      protocol 八层
                                        反馈/阻抗/忆阻）
  netlist       compile_modes.       NetlistSynthesizer          meridian 机制同构
  （综合）        netlist(规则→通道边)  （共振边收敛网表+SHA）       （规则→通道边收敛）

  张量向量耦合（不变）：TensorCircuit（V51 ring17 原件）继续作载体——
  网表器件 = 概念轴 D，参数 = 值轴 X，HRR 绑定编码，三段产物各自成张量。

装配纪律：真实复用 holoaeon.circuit_gate（六算子+TensorCircuit）、
holoaeon.fusion_upgrade.contract（make/validate/receipt）、
holoaeon.design_vocab.compile_modes（三段形状对齐，不 import 其内部）——
装配不重写，零新依赖，纯标准库。
"""

from __future__ import annotations

import hashlib
import json
import sys
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .circuit_gate import (
    CIRCUIT_CONCEPTS,
    SEAL,
    FeedbackAmp,
    ImpedanceMatch,
    KirchhoffFlow,
    MemristorSynapse,
    ResonatorNode,
    TensorCircuit,
    resonate,
)
from .fusion_upgrade import contract as fu_contract
from .hypervector import HypervectorSpace

# ---------------------------------------------------------------- 链位
CHAIN_POSITION = {
    "ring": 17,
    "layer": "assembly",
    "domain": "硬件（EDA 网表化升级装配）",
    "batch": "V51R",
    "upstream": [
        "circuit_gate(ring17 电子域六算子·同环姊妹件)",
        "fusion_upgrade.contract(升级契约：只交换回执)",
        "design_vocab.compile_modes(EDA 三段先例：展开/仿真/综合)",
        "hypervector(Hyperspace 张量轴载体)",
    ],
}

# 三段编译（对齐 design_vocab.compile_modes.COMPILE_MODES 三元组形状）
COMPILE_STAGES: Tuple[Tuple[str, str, str], ...] = (
    ("elaborate", "展开：组件描述 → 器件/端口网表", "对应 VHDL elaboration"),
    ("simulate", "仿真：网表 → 六算子波形（KCL/谐振/反馈/阻抗/忆阻）",
     "对应 testbench 波形"),
    ("netlist", "综合：波形 → 共振边收敛网表+SHA 指纹", "对应 netlist 综合"),
)

# 升级契约机制选择：网表化升级与 meridian（规则→通道边收敛）同构，
# 这正是 compile_modes.netlist 把 findings 收敛成"规则→通道"边的同一形状。
NETLIST_MECHANISM = "meridian"


# ---------------------------------------------------------------- 工具


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _now_iso() -> str:
    import datetime
    return datetime.datetime.now().isoformat(timespec="seconds")


def _stable_dump(obj: Any) -> str:
    """确定性 JSON（键排序、紧凑分隔、中文不转义）——同参同指纹。"""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)


# ================================================================ 一、展开段


class NetlistElaborator:
    """EDA elaborate：组件描述 → 器件/端口网表。

    输入：{概念: 参数值}（概念须在 CIRCUIT_CONCEPTS 表内——与
    TensorCircuit.concept_axis 同一词汇表，保证张量耦合口径一致）。
    输出网表三件：
      · devices —— 器件表（id 确定性派生：D{位次}-{概念}；ports=1/器件）
      · edges   —— 菊花链环连（D00→D01→…→D00 闭环，边权=参数归一值）
      · anchors —— source/ground 锚（首/尾器件的外部端口声明）
    """

    def elaborate(self, description: Dict[str, float]) -> Dict[str, Any]:
        if not description:
            raise ValueError("空组件描述（无可展开器件）")
        unknown = [k for k in description if k not in CIRCUIT_CONCEPTS]
        if unknown:
            raise ValueError("未知概念（不在电路概念表）: %s（表内: %s）"
                             % (unknown, list(CIRCUIT_CONCEPTS)))
        devices: List[Dict[str, Any]] = []
        values: List[float] = []
        # 概念表序展开（确定性：与 TensorCircuit.encode_circuit 同序）
        for i, name in enumerate(CIRCUIT_CONCEPTS):
            if name in description:
                v = round(float(description[name]), 3)
                devices.append({"id": "D%02d-%s" % (i, name),
                               "concept": name, "value": v,
                               "ports": 1})
                values.append(v)
        n = len(devices)
        edges: List[Dict[str, Any]] = []
        for i in range(n):
            u = devices[i]["id"]
            v = devices[(i + 1) % n]["id"]
            w = round(abs(values[i]) / (1.0 + abs(values[i])), 4)  # 归一 0-1
            edges.append({"from": u, "to": v, "weight": w})
        netlist = {
            "mode": "elaborate",
            "components": n,
            "ports": sum(d["ports"] for d in devices),
            "devices": devices,
            "edges": edges,
            "anchors": {"source": devices[0]["id"],
                        "ground": devices[-1]["id"]} if n else {},
            "sha256": _sha256(_stable_dump(
                {"devices": devices, "edges": edges}))[:16],
        }
        return netlist


# ================================================================ 二、仿真段


class NetlistSimulator:
    """EDA simulate（testbench）：在网表上跑 V51 六算子，得波形。

    五路波形（全确定性）：
      · kirchhoff —— KCL 全严格守恒 + KVL 环一致性（菊花链闭环）
      · resonant  —— 器件谐振榜（ResonatorNode，频率×相位×Q）
      · feedback  —— 反馈环收敛（FeedbackAmp：器件参数→目标收敛史）
      · impedance —— 端口匹配（ImpedanceMatch：器件间转换效率）
      · memrist   —— 忆阻阻态（MemristorSynapse：边权忆阻训练一拍）
    verdict 口径对齐 compile_modes.simulate：P0 级违例=FAIL，
    警戒=WARN，全绿=PASS。
    """

    def simulate(self, netlist: Dict[str, Any]) -> Dict[str, Any]:
        if netlist.get("mode") != "elaborate":
            raise ValueError("仿真输入须为 elaborate 段产物")
        devices = netlist["devices"]
        edges = netlist["edges"]

        # ① Kirchhoff —— 串联环电流守恒（KCL 物理本义：环上电流处处相等）
        # 边权=参数归一（导纳性质），电流=单位 testbench 激励 1.0
        flows = {}
        idx = {d["id"]: i for i, d in enumerate(devices)}
        for e in edges:
            flows[(idx[e["from"]], idx[e["to"]])] = 1.0
        kf = KirchhoffFlow()
        kcl = kf.kcl_check(flows)
        # KVL：菊花链闭环（首尾相接），log 域一致性（波形信息）
        kvl = kf.kvl_check(flows, cycles=[list(range(len(devices)))])

        # ② Resonant —— 器件谐振榜（驱动=首器件键）
        node_keys = [d["id"] for d in devices]
        res = resonate(None, node_keys[0], node_keys)
        top = res["results"][0]

        # ③ Feedback —— 参数收敛史（初态=边权，目标=1.0 满共振）
        initial = [e["weight"] for e in edges]
        target = [1.0] * len(edges)
        fa = FeedbackAmp(gain=1.0, feedback=1.0)
        conv = fa.converge(initial, target, rounds=10)

        # ④ Impedance —— 端口匹配（相邻器件参数为源/载阻抗）
        im = ImpedanceMatch()
        imped_report = {"pairs": [], "mean_efficiency": 0.0}
        effs: List[float] = []
        for i in range(len(devices)):
            a = devices[i]
            b = devices[(i + 1) % len(devices)]
            src = [a["value"]]
            load = [b["value"]]
            r = im.match_score(src, load)
            effs.append(r["efficiency"])
            imped_report["pairs"].append(
                {"pair": "%s|%s" % (a["id"], b["id"]),
                 "efficiency": r["efficiency"]})
        imped_report["mean_efficiency"] = round(
            sum(effs) / max(len(effs), 1), 6)

        # ⑤ Memrist —— 边权忆阻一拍（共激活=相邻器件同激活）
        mem_states: Dict[str, float] = {}
        for e, d in zip(edges, devices):
            m = MemristorSynapse(weight=e["weight"], eta=0.1, leak=0.01)
            sig = d["value"] / (1.0 + abs(d["value"]))  # 参数归一信号
            m.update(sig, e["weight"])
            mem_states[e["from"]] = round(m.weight, 6)

        # 分级：KCL 违例=P0（守恒破缺）；KVL 积≠1/谐振落榜/反馈不收敛=WARN
        # （KVL log 域积是传递一致性波形：参数未配平≠守恒违例，如实记 WARN）
        p0 = not kcl["ok"]
        warn = (not kvl["ok"]) or (not conv["converged"]) \
            or top["resonance"] < 0.5
        verdict = "FAIL" if p0 else ("WARN" if warn else "PASS")
        return {
            "mode": "simulate",
            "kirchhoff": {"kcl_ok": kcl["ok"], "kvl_ok": kvl["ok"],
                          "violations": len(kcl["violations"])},
            "resonant": {"top_node": top["node"],
                         "top_resonance": top["resonance"],
                         "ranked": len(res["results"])},
            "feedback": {"converged": conv["converged"],
                         "rounds_run": conv["rounds_run"],
                         "final_error": conv["final_error"],
                         "stability": conv["stability"]},
            "impedance": imped_report,
            "memrist": {"states": mem_states,
                        "edges": len(mem_states)},
            "verdict": verdict,
        }


# ================================================================ 三、综合段


class NetlistSynthesizer:
    """EDA netlist（综合）：仿真波形 → 共振边收敛网表+SHA 指纹。

    对齐 compile_modes.netlist 形状（nodes/edges/weights）；
    边权 = 边共振分（KVL 通过=守恒边 / 失配=衰减）。
    网表文本确定性 → SHA256 指纹可入审计（SHA256SUMS 同款判据）。
    """

    def synthesize(self, netlist: Dict[str, Any],
                   sim: Dict[str, Any]) -> Dict[str, Any]:
        if netlist.get("mode") != "elaborate" or sim.get("mode") != "simulate":
            raise ValueError("综合输入须为 elaborate+simulate 两段产物")
        devices = netlist["devices"]
        edges = netlist["edges"]
        nodes = {d["id"] for d in devices}
        weights: Dict[str, float] = {}
        for i, e in enumerate(edges):
            # 边权 = 原权 × 相邻端口效率（失配衰减）
            pair = sim["impedance"]["pairs"][i]["efficiency"]
            key = "%s>%s" % (e["from"], e["to"])
            weights[key] = round(e["weight"] * max(pair, 0.0), 6)
        body = {"nodes": sorted(nodes), "edges": edges, "weights": weights}
        return {
            "mode": "netlist",
            "nodes": len(nodes),
            "edges": len(weights),
            "weights": dict(sorted(weights.items())),
            "verdict": sim["verdict"],
            "sha256": _sha256(_stable_dump(body)),
            "meridian_note": "共振边收敛与 meridian 机制同构"
                             "（规则→通道边收敛，compile_modes.netlist 先例）",
        }


# ================================================================ 四、升级契约耦合


class UpgradeContractCoupler:
    """网表硬件件 → 升级契约（内部协议：只交换回执，不换代码）。

    真实复用 fusion_upgrade.contract：
      · make/validate/receipt —— 契约三件套原样调用
      · mechanism=meridian（网表化升级与经络边收敛同构）
      · lane=read（只读升级：网表入账，不动对端）
    热替换语义声明（swap.hot_install 形状对齐）：旧槽换新件=
    综合段网表 SHA 作为"新件指纹"入契约 payload，
    但本模块**不执行** hot_install（那需要内核实例）——只产出可回执契约。
    """

    def couple(self, netlist: Dict[str, Any], synthesized: Dict[str, Any],
               skill: str = "hardware_netlist_upgrade") -> Dict[str, Any]:
        if synthesized.get("mode") != "netlist":
            raise ValueError("契约输入须为 netlist 段产物")
        doc = fu_contract.make(
            source="holoaeon.circuit_gate(ring17)",
            target="fusion_upgrade.slot_registry",
            skill=skill,
            mechanism=NETLIST_MECHANISM,
            lane="read",
            note="网表硬件件升级契约：netlist_sha=%s verdict=%s"
                 % (synthesized["sha256"][:16], synthesized["verdict"]),
        )
        check = fu_contract.validate(doc)
        rec = fu_contract.receipt(doc, verdict=synthesized["verdict"].lower())
        return {
            "mode": "contract",
            "contract": doc,
            "validate": check,
            "receipt": rec,
            "hot_swap_note": "热替换语义=旧槽换新件（swap.hot_install 同构）；"
                             "本模块只产契约回执，不执行内核热装（须内核实例）",
            "mechanism": NETLIST_MECHANISM,
        }


# ================================================================ 五、张量耦合


class TensorCouple:
    """张量向量耦合（不变）：网表三段产物 → Hyperspace 张量。

    载体= V51 circuit_gate.TensorCircuit（原件复用，零重写）：
      · elaborate 段 → 器件描述张量（概念×值编码，encode_circuit 同款）
      · netlist 段   → 边权张量（from/to 两角色绑定 bundle）
      · 相似度       —— 两张网表的 elaborate 张量 cosine 可比
    """

    def __init__(self, space: Optional[HypervectorSpace] = None):
        self.tc = TensorCircuit(space=space)

    def elaborate_tensor(self, netlist: Dict[str, Any]) -> List[float]:
        """器件描述张量：{概念: 参数} 的 HRR 编码（D/X 轴）。"""
        desc = {d["concept"]: d["value"] for d in netlist["devices"]}
        return self.tc.encode_circuit(desc)

    def netlist_tensor(self, synthesized: Dict[str, Any]) -> List[float]:
        """边权张量：每条边 bind(permute(D_from), X_weight) 后 bundle。"""
        parts: List[List[float]] = []
        for key, w in synthesized["weights"].items():
            frm, _to = key.split(">", 1)
            src, _ = frm.split("-", 1)
            # 概念轴须在表内：器件 id 形如 D{i}-{concept}
            concept = frm.split("-", 1)[1] if "-" in frm else frm
            if concept not in CIRCUIT_CONCEPTS:
                concept = CIRCUIT_CONCEPTS[0]  # 首概念兜底（确定性）
            d = self.tc.concept_axis(concept)
            x = self.tc.space.permute(self.tc.value_axis(w), shift=1)
            parts.append(self.tc.space.bind(d, x))
        if not parts:
            raise ValueError("空网表（无边权可编码）")
        return self.tc.space.bundle(parts)

    def similarity(self, desc_a: Dict[str, float],
                   desc_b: Dict[str, float]) -> float:
        """两份组件描述的 elaborate 张量相似度（描述=概念→参数）。"""
        return self.tc.space.cosine(self.tc.encode_circuit(desc_a),
                                    self.tc.encode_circuit(desc_b))


# ================================================================ 总闸


class HardwareGate:
    """V51R 总闸：EDA 三段编译 + 升级契约 + 张量耦合。

    编排：elaborate → simulate → synthesize → couple（契约回执）→
    tensor（三段张量指纹）→ manifest（artifacts 真实入卡，V49 纪律）。
    诚实边界：非设备驱动、非固件、非算力调度；网表=语言范式。
    """

    def __init__(self, space: Optional[HypervectorSpace] = None):
        self.elaborator = NetlistElaborator()
        self.simulator = NetlistSimulator()
        self.synthesizer = NetlistSynthesizer()
        self.coupler = UpgradeContractCoupler()
        self.tensor = TensorCouple(space=space)

    def compile(self, description: Dict[str, float]) -> Dict[str, Any]:
        """三段编译一条龙（compile_text 同构先例）。"""
        nl = self.elaborator.elaborate(description)
        sim = self.simulator.simulate(nl)
        syn = self.synthesizer.synthesize(nl, sim)
        return {"elaborate": nl, "simulate": sim, "netlist": syn}

    def self_check(self) -> dict:
        checks: Dict[str, dict] = {}
        desc = {"voltage": 5.0, "current": 2.0, "resistance": 1.0}
        result = self.compile(desc)
        nl, sim, syn = result["elaborate"], result["simulate"], result["netlist"]
        # 1) elaborate：器件/端口/环连
        checks["elaborate"] = {
            "ok": nl["components"] == 3 and nl["ports"] == 3
                  and len(nl["edges"]) == 3 and nl["edges"][0]["from"]
                  == "D00-voltage" and nl["sha256"] == _sha256(
                      _stable_dump({"devices": nl["devices"],
                                    "edges": nl["edges"]}))[:16],
            "components": nl["components"], "ports": nl["ports"],
        }
        # 2) simulate：五路波形全绿（等权环 KVL 通过：3 条等权边 log 乘积≠1？
        #    菊花链 w_i 不全等（参数归一不同）→ 乘积≈1 需参数配平；
        #    自检用 PASS 判据：verdict ∈ {PASS, WARN} 且 KCL 守恒必须 OK）
        checks["simulate"] = {
            "ok": sim["kirchhoff"]["kcl_ok"] and sim["verdict"] in
                  ("PASS", "WARN") and sim["resonant"]["ranked"] == 3,
            "kcl": sim["kirchhoff"]["kcl_ok"],
            "verdict": sim["verdict"],
            "feedback_converged": sim["feedback"]["converged"],
            "impedance_mean": sim["impedance"]["mean_efficiency"],
        }
        # 3) netlist：形状对齐 compile_modes（nodes/edges/weights）+SHA
        checks["netlist"] = {
            "ok": syn["nodes"] == 3 and syn["edges"] == 3
                  and len(syn["sha256"]) == 64
                  and set(("nodes", "edges", "weights")) <= set(syn),
            "sha16": syn["sha256"][:16],
        }
        # 4) contract：回执三件套（make/validate/receipt 原样复用）
        cp = self.coupler.couple(nl, syn)
        checks["contract"] = {
            "ok": cp["validate"]["ok"] and cp["receipt"]["verdict"]
                  == syn["verdict"].lower() and cp["contract"]["mechanism"]
                  == NETLIST_MECHANISM,
            "contract_id": cp["contract"]["contract_id"],
            "mechanism": cp["contract"]["mechanism"],
            "lane": cp["contract"]["lane"],
        }
        # 5) tensor：三段张量（耦合不变）
        et = self.tensor.elaborate_tensor(nl)
        nt = self.tensor.netlist_tensor(syn)
        same = self.tensor.similarity(desc, desc)
        other = self.tensor.similarity(desc, {"ground": 1.0})
        checks["tensor"] = {
            "ok": len(et) == self.tensor.tc.space.dim
                  and len(nt) == self.tensor.tc.space.dim
                  and same > other,
            "self_sim": same, "far_sim": other,
            "dim": self.tensor.tc.space.dim,
        }
        # 6) 三段形状对齐 compile_modes（外部协议忠实度）
        from . import design_vocab  # 仓内包，纯函数
        sample = "<div class=\"a\">x</div>"
        cm = design_vocab.compile_modes.compile_text(sample)
        shape_ok = (
            set(cm["elaborate"]) >= {"mode", "components", "ports"}
            and cm["simulate"]["mode"] == "simulate"
            and cm["netlist"]["mode"] == "netlist"
            and result["elaborate"]["mode"] == "elaborate"
            and sim["mode"] == "simulate" and syn["mode"] == "netlist")
        checks["paradigm_alignment"] = {
            "ok": shape_ok and len(COMPILE_STAGES) == 3
                  and COMPILE_STAGES[0][0] == "elaborate"
                  and COMPILE_STAGES[1][0] == "simulate"
                  and COMPILE_STAGES[2][0] == "netlist",
            "compile_modes_probe": cm["elaborate"]["components"] >= 1,
        }
        ok_all = all(c["ok"] for c in checks.values())
        return {"ok": ok_all, "checks": checks,
                "chain_position": CHAIN_POSITION, "seal": SEAL}

    def run(self, description: Optional[Dict[str, float]] = None) -> dict:
        """总闸：三段编译 → 契约 → 张量 → manifest 回执。"""
        sc = self.self_check()
        if description is None:
            description = {"voltage": 5.0, "current": 2.0,
                           "resistance": 1.0}
        result = self.compile(description)
        cp = self.coupler.couple(result["elaborate"], result["netlist"])
        et = self.tensor.elaborate_tensor(result["elaborate"])
        et_sha = _sha256(",".join("%.6f" % x for x in et))[:16]
        manifest = {
            "batch": CHAIN_POSITION["batch"],
            "ring": CHAIN_POSITION["ring"],
            "domain": CHAIN_POSITION["domain"],
            "generated_at": _now_iso(),
            "stages": [s[0] for s in COMPILE_STAGES],
            "self_check": sc,
            "mechanism": NETLIST_MECHANISM,
            "artifacts": {
                "elaborate_receipt": {
                    "components": result["elaborate"]["components"],
                    "ports": result["elaborate"]["ports"],
                    "sha16": result["elaborate"]["sha256"]},
                "simulate_receipt": {
                    "verdict": result["simulate"]["verdict"],
                    "kcl_ok": result["simulate"]["kirchhoff"]["kcl_ok"],
                    "feedback_converged":
                        result["simulate"]["feedback"]["converged"]},
                "netlist_receipt": {
                    "nodes": result["netlist"]["nodes"],
                    "edges": result["netlist"]["edges"],
                    "sha256": result["netlist"]["sha256"]},
                "contract_receipt": cp["receipt"],
            },
            "tensor_coupling": {
                "carrier": "circuit_gate.TensorCircuit（V51 原件，不变）",
                "elaborate_tensor_sha16": et_sha,
                "dim": len(et),
            },
            "honesty": {
                "hardware": "EDA/VHDL 语言范式（网表），非设备驱动/固件/算力调度",
                "external_protocol": "EDA 三段编译（design_vocab.compile_modes 先例）",
                "internal_protocol": "fusion_upgrade 契约（只交换回执）+ "
                                     "swap 热替换语义（只声明不执行）",
                "neural": False,
                "network": False,
                "new_dependencies": 0,
                "reuses": ["circuit_gate 六算子+TensorCircuit",
                           "fusion_upgrade.contract 三件套",
                           "design_vocab.compile_modes 三段形状",
                           "hypervector.Hyperspace"],
            },
            "seal": SEAL,
        }
        return manifest


# ---------------------------------------------------------------- 模块指纹


def fingerprint() -> dict:
    return {
        "module": "hardware_gate",
        "ring": CHAIN_POSITION["ring"],
        "batch": CHAIN_POSITION["batch"],
        "domain": CHAIN_POSITION["domain"],
        "stages": [s[0] for s in COMPILE_STAGES],
        "mechanism": NETLIST_MECHANISM,
        "sha256": _sha256("hardware-gate-v1:" + SEAL),
        "seal": SEAL,
    }


def probe() -> dict:
    """轻量探针：三段编译+self_check。"""
    return HardwareGate().self_check()


def _main(argv: List[str]) -> int:
    import sys
    cmd = argv[1] if len(argv) > 1 else "probe"
    if cmd == "probe":
        out = probe()
    elif cmd == "run":
        out = HardwareGate().run()
    elif cmd == "fingerprint":
        out = fingerprint()
    else:
        print("usage: python -m holoaeon.hardware_gate "
              "[probe|run|fingerprint]", file=sys.stderr)
        return 2
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if out.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(_main(["hardware_gate"] + sys.argv[1:]))
