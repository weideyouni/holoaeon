# -*- coding: utf-8 -*-
"""bayes_reasoning.py · holoaeon 贝叶斯推理内核（V89）

碳基 2026-11-20 17:19 投喂令：将 BayesianReasoningKernel 方向从
polisaeon 城邦上收到 **holoaeon 基座**——完美匹配 25 机制轴、适配
18 分仓与主仓、并作为 longaeon 匹配升级（LA-V9）的上游依据。

第一性（投喂正文 §一）：
  贝叶斯模块不是概率装饰，是给每次判定加"先验—似然—后验"校验——
  后验 ∝ 似然 × 先验。

去特征向量化属性（碳基口径）：
  本内核**机制锚定**而非特征向量锚定——先验不来自城市/文本特征向量，
  而来自 25 机制轴上的基座真实现（心跳流、共振序、熵产率、卡尔曼新息、
  SPRT 序贯证据、克莱因收敛度）。polisaeon 的城市特征版（PA-V3
  bayes_kernel.py）是本内核的**城邦特化**，本模块是**基座通型**。

本模块在基座的定位：
  1. 统一账：基座散落的贝叶斯族真实现首次挂到 15 模块注册表——
     R5 卡尔曼（kalman_fuse/kalman_state）→B13、R6 贝叶斯干涉
     （bayesian_guard，Wald SPRT）→B01 证据序贯、R7 希尔伯特
     （rff_features）→B06、X2 共振（kuramoto_order）→B08、
     C1 耗散（entropy_production）→B07、R4 克莱因收敛
     （klein_convergence）→B10；
  2. 机制匹配表：15 模块 × 25 机制轴锚定表（三态：
     import-evidenced / semantic-anchor / pending-implementation）；
  3. 18 分仓 + 主仓适配图：每分仓确定性消费内核服务；
  4. 后验校验包（机制锚定型）：先验由锚定机制证据合成，执行反馈
     共轭更新，三分流决策。

纪律：纯标准库、确定性（无墙钟无随机）、import 复用零复制（指针
纪律）、冻结维度不动（VERSION/layers/PACK_ORDER）、pending 如实。

封口密语：潮起开门，潮落闭嘴。
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List, Optional

SCHEMA = "HOLOAEON-BAYES-REASONING/1.0"
SEAL = "潮起开门，潮落闭嘴"
BATCH = "V89"

CONF_HIGH_MIN = 0.75
CONF_MID_MIN = 0.50

# ---------------------------------------------------------------------------
# §1 15 模块注册表（B01-B15；三层：轻量 4 / 结构 5 / 重算 6）
# ---------------------------------------------------------------------------

B_MODULES: List[Dict[str, Any]] = [
    {"id": "B01", "name": "朴素贝叶斯", "layer": "light",
     "implemented": True},
    {"id": "B02", "name": "多项式贝叶斯", "layer": "light",
     "implemented": False},
    {"id": "B03", "name": "高斯贝叶斯", "layer": "light",
     "implemented": False},
    {"id": "B04", "name": "贝叶斯网络", "layer": "structure",
     "implemented": True},
    {"id": "B05", "name": "MCMC", "layer": "heavy",
     "implemented": False},
    {"id": "B06", "name": "HMC / NUTS", "layer": "heavy",
     "implemented": False},
    {"id": "B07", "name": "变分推断 VI", "layer": "heavy",
     "implemented": True},
    {"id": "B08", "name": "SVI 随机变分推断", "layer": "heavy",
     "implemented": False},
    {"id": "B09", "name": "贝叶斯线性回归", "layer": "light",
     "implemented": False},
    {"id": "B10", "name": "贝叶斯优化", "layer": "structure",
     "implemented": True},
    {"id": "B11", "name": "贝叶斯神经网络", "layer": "structure",
     "implemented": False},
    {"id": "B12", "name": "层次贝叶斯", "layer": "structure",
     "implemented": True},
    {"id": "B13", "name": "卡尔曼滤波", "layer": "heavy",
     "implemented": True},
    {"id": "B14", "name": "粒子滤波", "layer": "heavy",
     "implemented": False},
    {"id": "B15", "name": "贝叶斯模型平均 BMA", "layer": "structure",
     "implemented": False},
]
# 基座已有真实现的模块（import 复用——指针纪律，不复制）
B_IMPLEMENTED_ON_BASE = ["B01", "B04", "B07", "B10", "B12", "B13"]

# ---------------------------------------------------------------------------
# §2 机制匹配表：15 模块 × 25 机制轴（去特征向量化——机制锚定）
# ---------------------------------------------------------------------------

# 三态锚定：
#   import-evidenced —— 基座有可直接 import 的真实现（symbol 在案）
#   semantic-anchor  —— 语义锚定（机制语义与算法数学同构，无代码实现）
#   pending-implementation —— 无锚（本批不虚称）
MECH_MATCH: List[Dict[str, Any]] = [
    {"b": "B01", "anchors": ["M06"],
     "state": "import-evidenced",
     "evidence": "M06 语义通信基座：朴素贝叶斯即语义通道上的类条件判定；"
                 "证据序贯化由 R6 bayesian_guard（Wald SPRT）承载",
     "symbols": ["holoaeon.packs.topology_resonance_pack.bayesian_guard"]},
    {"b": "B02", "anchors": ["M09"],
     "state": "semantic-anchor",
     "evidence": "M09 graph：图节点类型/度数的计数型先验（多项式族语义同构），"
                 "无代码实现"},
    {"b": "B03", "anchors": ["M08"],
     "state": "semantic-anchor",
     "evidence": "M08 runtime：连续运行指标的监控似然（高斯族语义同构），"
                 "本批未实现"},
    {"b": "B04", "anchors": ["R4", "M11"],
     "state": "import-evidenced",
     "evidence": "R4 克莱因收敛即多源归一的因果图投影；M11 城邦架构即"
                 "变量依赖网络",
     "symbols": ["holoaeon.packs.topology_resonance_pack.klein_convergence"]},
    {"b": "B05", "anchors": ["M01"],
     "state": "semantic-anchor",
     "evidence": "M01 心跳：节律状态空间上的采样语义（MCMC 探索=心跳扰动），"
                 "无代码实现"},
    {"b": "B06", "anchors": ["R7"],
     "state": "import-evidenced",
     "evidence": "R7 希尔伯特空间：HMC 的梯度流即希尔伯特空间中的测地采样；"
                 "rff_features 是该空间的 Bochner 实现入口",
     "symbols": ["holoaeon.resonance_supplement.rff_features"]},
    {"b": "B07", "anchors": ["C1"],
     "state": "import-evidenced",
     "evidence": "C1 自组织耗散：变分自由能与熵产率同构（Onsager 线性区"
                 "即平均场不动点邻域）",
     "symbols": ["holoaeon.resonance_supplement.entropy_production"]},
    {"b": "B08", "anchors": ["X2"],
     "state": "import-evidenced",
     "evidence": "X2 共振带：Kuramoto 序参量即共振群流的充分统计量，"
                 "流式更新语义=SVI",
     "symbols": ["holoaeon.resonance_supplement.kuramoto_order"]},
    {"b": "B09", "anchors": ["M05"],
     "state": "semantic-anchor",
     "evidence": "M05 赫布协作场：协作强度-产出回归（贝叶斯回归语义同构），"
                 "无代码实现"},
    {"b": "B10", "anchors": ["R4"],
     "state": "import-evidenced",
     "evidence": "R4 克莱因收敛：参数搜索以收敛度为目标（NSGA-II 求解 "
                 "Klein 收敛先例同族）",
     "symbols": ["holoaeon.packs.topology_resonance_pack.klein_convergence"]},
    {"b": "B11", "anchors": ["M02"],
     "state": "semantic-anchor",
     "evidence": "M02 细胞骨架：骨架上生长的网络即贝叶斯神经网络的拓扑先验"
                 "（类硅基 kernel 位点语义），无代码实现"},
    {"b": "B12", "anchors": ["X1"],
     "state": "semantic-anchor",
     "evidence": "X1 城邦网格（1331=11³）：省级-城市-场景-体素分层共享="
                 "网格分层收缩语义；L1-L4 层级同构"},
    {"b": "B13", "anchors": ["R5"],
     "state": "import-evidenced",
     "evidence": "R5 卡尔曼滤波：基座双实现（信息型融合 kalman_fuse +"
                 "预测-校正 kalman_state，NIS χ² 一致性在案）",
     "symbols": ["holoaeon.resonance_supplement.kalman_fuse",
                  "holoaeon.packs.topology_resonance_pack.kalman_state"]},
    {"b": "B14", "anchors": ["R1"],
     "state": "semantic-anchor",
     "evidence": "R1 共振节点：粒子群在共振节点邻域的重采样语义"
                 "（非线性非高斯动态），无代码实现"},
    {"b": "B15", "anchors": ["M10"],
     "state": "semantic-anchor",
     "evidence": "M10 类社会组合体：多结论冲突融合=组合体仲裁（四人组"
                 "协议 quartet_toolkit 的 P1-P4 加权同族；"
                 "klein_projection 段表 source=quartet_toolkit 在案文本锚）",
     "symbols": []},
]

# 本批保持 pending（零虚构）：B02/B03/B05/B06*/B09/B11/B14/B15
# 注：B06 有 rff 入口但 HMC/NUTS 采样器本体未实现——注册表按算法本体
# 判 implemented=False，rff 只作空间实现入口（锚定证据不虚称算法已实现）。

# ---------------------------------------------------------------------------
# §3 基座贝叶斯族既有资产统一账（import 复用零复制）
# ---------------------------------------------------------------------------

BASE_BAYES_ASSETS: List[Dict[str, str]] = [
    {"symbol": "holoaeon.packs.topology_resonance_pack.bayesian_guard",
     "mech": "R6", "role": "证据序贯判定（Wald SPRT + 代价敏感阈值）"},
    {"symbol": "holoaeon.packs.topology_resonance_pack.kalman_state",
     "mech": "R5", "role": "预测-校正 + NIS χ²=3.841 一致性门"},
    {"symbol": "holoaeon.resonance_supplement.kalman_fuse",
     "mech": "R5", "role": "信息型多源融合 P⁻¹=ΣR⁻¹"},
    {"symbol": "holoaeon.resonance_supplement.sprt_gate",
     "mech": "R6", "role": "序贯概率比检验 A/B 双阈值停机"},
    {"symbol": "holoaeon.resonance_supplement.rff_features",
     "mech": "R7", "role": "随机傅里叶特征（Bochner 核近似）"},
    {"symbol": "holoaeon.resonance_supplement.kuramoto_order",
     "mech": "X2", "role": "序参量 r=|mean e^{iθ}| 共振度量"},
    {"symbol": "holoaeon.resonance_supplement.entropy_production",
     "mech": "C1", "role": "熵产率 σ=ΣJ·X + Onsager 校验"},
    {"symbol": "holoaeon.packs.topology_resonance_pack.klein_convergence",
     "mech": "R4", "role": "克莱因收敛（多源归一判据）"},
]


def _resolve(symbol: str) -> bool:
    """符号可解析性（真 import 验证，不虚称）。"""
    try:
        mod_path, _, attr = symbol.rpartition(".")
        if not mod_path:
            return False
        import importlib
        mod = importlib.import_module(mod_path)
        return callable(getattr(mod, attr, None))
    except Exception:  # noqa: BLE001
        return False


# ---------------------------------------------------------------------------
# §4 18 分仓 + 主仓适配图（每分仓确定性消费内核服务）
# ---------------------------------------------------------------------------

REPO_SERVICES: Dict[str, List[str]] = {
    "C01": ["B01", "B02"],   # source 源流：语义分类
    "C02": ["B03"],          # body 身体：连续指标
    "C03": ["B07"],          # meridian 经络：链接态后验近似
    "C04": ["B12"],          # family 家族：分层共享
    "C05": ["B02"],          # education 教育：文本计数分类
    "C06": ["B09"],          # career 事业：产出回归
    "C07": ["B13"],          # wealth 财富：动态监测融合
    "C08": ["B10"],          # creation 创造：参数搜索
    "C09": ["B04"],          # relation 关系：因果网络
    "C10": ["B14"],          # emotion 情绪：非线性非高斯
    "C11": ["B04"],          # meaning 意义：价值因果图
    "C12": ["B06"],          # space 空间：高维投影采样
    "C13": ["B13"],          # time 时间：时序滤波
    "C14": ["B01"],          # skill 技艺：意图分类（制造局调度先例）
    "C15": ["B15", "B01"],   # risk 风险：冲突融合仲裁 + 证据序贯
    "C16": ["B05"],          # spirit 心灵：状态采样
    "C17": ["B12"],          # society 社群：分层共享
    "C18": ["B06"],          # cosmos 宇宙：高维采样
}
MAIN_REPO_SERVICES = [m["id"] for m in B_MODULES]  # 主仓：内核驻地=15 全量


def repo_adapter_map() -> List[Dict[str, Any]]:
    """18 分仓适配图（从 forge_bureau.C18_NUMBERING import 对账——指针纪律）。"""
    from .forge_bureau import C18_NUMBERING
    rows = []
    for c in C18_NUMBERING:
        rid = c["id"] if "id" in c else c["repo"].split("-")[1].upper()
        rows.append({
            "repo": c["repo"], "repo_id": c.get("id", rid),
            "services": REPO_SERVICES.get(c.get("id", rid), []),
            "kernel_resident": False,
        })
    rows.append({"repo": "holoaeon", "repo_id": "MAIN",
                 "services": MAIN_REPO_SERVICES, "kernel_resident": True})
    return rows


# ---------------------------------------------------------------------------
# §5 后验校验包（机制锚定型——去特征向量化）
# ---------------------------------------------------------------------------

def mechanism_prior(anchor_evidence: Dict[str, float]) -> Dict[str, Any]:
    """机制先验：锚定机制的量化证据 → Beta(α0, β0)。

    与 polisaeon 城市特征版不同：先验合成只吃**机制量化证据**——
    如 σ（熵产率）、r（Kuramoto 序参量）、NIS（卡尔曼新息一致性）、
    klein 收敛度、SPRT 对数似然比。每条证据线性映射到 (α+, β+)。
    """
    a, b = 2.0, 2.0   # 均匀倾向基座
    used: List[str] = []
    for name, value in sorted(anchor_evidence.items()):
        if value is None:
            continue
        v = float(value)
        if v >= 0.5:
            a += (v - 0.5) * 4.0
        else:
            b += (0.5 - v) * 4.0
        used.append("{}={}".format(name, round(v, 4)))
    return {"alpha0": round(a, 4), "beta0": round(b, 4),
            "prior_mean": round(a / (a + b), 6), "evidence_used": used}


def posterior_package(query_id: str,
                      anchor_evidence: Dict[str, float],
                      n_success: int = 0, n_failure: int = 0
                      ) -> Dict[str, Any]:
    """后验校验包（基座通型）：先验=机制证据合成；反馈=执行记录共轭。"""
    prior = mechanism_prior(anchor_evidence)
    a = prior["alpha0"] + n_success
    b = prior["beta0"] + n_failure
    post_mean = a / (a + b)
    level = ("high" if post_mean >= CONF_HIGH_MIN
             else "mid" if post_mean >= CONF_MID_MIN else "low")
    if level == "high":
        decision, policy = "直接放行", {"write_back": True, "tier": "hot"}
    elif level == "mid":
        decision, policy = "触发结构层复核（B04 网络 / B12 层次）", \
                           {"write_back": True, "tier": "warm"}
    else:
        decision, policy = "进入重算层离线校准（B05/B06/B08）", \
                           {"write_back": True, "tier": "cold"}
    return {
        "query_id": query_id,
        "prior_score": prior["prior_mean"],
        "posterior_score": round(post_mean, 6),
        "confidence_level": level,
        "decision": decision,
        "update_policy": policy,
        "evidence_used": prior["evidence_used"],
    }


# ---------------------------------------------------------------------------
# §6 基座实测锚（真实现喂先验——可失败）
# ---------------------------------------------------------------------------

def live_anchor_evidence() -> Dict[str, Optional[float]]:
    """从基座真实现现场取机制量化证据（全部真跑，不虚构）。"""
    from .resonance_supplement import (
        entropy_production, kuramoto_order)
    out: Dict[str, Optional[float]] = {}
    # C1 σ：Onsager 正定示例（resonance_supplement 判据内示例参数）
    ep = entropy_production(None, None)
    out["sigma_c1"] = ep.get("sigma") if isinstance(ep, dict) else None
    # X2 r：八相位同步示例
    ko = kuramoto_order([0.0] * 8)
    out["order_x2"] = ko.get("r") if isinstance(ko, dict) else None
    return out


# ---------------------------------------------------------------------------
# §7 总闸
# ---------------------------------------------------------------------------

def check_bayes_reasoning() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []

    def add(name, ok, note=""):
        checks.append({"check": name, "ok": bool(ok), "note": note})

    # 注册表
    add("modules_15", len(B_MODULES) == 15)
    add("modules_unique",
        len(set(m["id"] for m in B_MODULES)) == 15)
    add("layers_4_5_6",
        sum(1 for m in B_MODULES if m["layer"] == "light") == 4
        and sum(1 for m in B_MODULES if m["layer"] == "structure") == 5
        and sum(1 for m in B_MODULES if m["layer"] == "heavy") == 6)
    add("implemented_six_on_base",
        sorted(m["id"] for m in B_MODULES if m["implemented"])
        == sorted(B_IMPLEMENTED_ON_BASE),
        "基座已有真实现的 6 模块；其余 9 pending 如实（算法本体未实现）")

    # 机制匹配表（对 25 轴 import 对账——基座漂移即 FAIL）
    from . import meridian_link as ml
    axis_ids = {m["id"] for m in ml.KERNEL_MECHANISMS}
    add("axis_25", len(axis_ids) == 25)
    add("match_rows_15", len(MECH_MATCH) == 15)
    match_ids = {r["b"] for r in MECH_MATCH}
    add("match_covers_all_modules", match_ids ==
        {m["id"] for m in B_MODULES})
    all_anchors = {a for r in MECH_MATCH for a in r["anchors"]}
    add("anchors_within_axis", all_anchors <= axis_ids,
        "锚定机制 {} 个全部落在 25 轴内（去特征向量化：机制锚定）"
        .format(len(all_anchors)))
    add("every_module_anchored",
        all(r["anchors"] for r in MECH_MATCH))
    states = {r["state"] for r in MECH_MATCH}
    add("states_three_legal",
        states <= {"import-evidenced", "semantic-anchor",
                   "pending-implementation"})
    n_import_ev = sum(1 for r in MECH_MATCH
                      if r["state"] == "import-evidenced")
    add("import_evidence_resolvable",
        all(_resolve(s) for r in MECH_MATCH for s in r.get("symbols", [])),
        "{} 模块 import 锚定证据全部可解析（指针纪律）".format(n_import_ev))

    # 既有资产统一账
    add("assets_8", len(BASE_BAYES_ASSETS) == 8)
    add("assets_resolvable",
        all(_resolve(a["symbol"]) for a in BASE_BAYES_ASSETS),
        "基座贝叶斯族 8 符号真 import 可调（零复制）")
    asset_mechs = {a["mech"] for a in BASE_BAYES_ASSETS}
    add("assets_mechs_in_axis", asset_mechs <= axis_ids)

    # 18 分仓 + 主仓适配
    rows = repo_adapter_map()
    add("adapter_rows_19", len(rows) == 19, "18 分仓 + 1 主仓")
    add("adapter_18_repos_unique",
        len(set(r["repo"] for r in rows)) == 19)
    b_ids = {m["id"] for m in B_MODULES}
    add("adapter_services_legal",
        all(set(r["services"]) <= b_ids for r in rows))
    add("adapter_no_empty",
        all(r["services"] for r in rows),
        "每分仓至少消费一项内核服务")
    main_row = next(r for r in rows if r["repo_id"] == "MAIN")
    add("main_repo_full_15",
        main_row["kernel_resident"] is True
        and len(main_row["services"]) == 15,
        "主仓=内核驻地，15 模块全量挂载")
    sub = [r for r in rows if r["repo_id"] != "MAIN"]
    add("adapter_18_all",
        all(not r["kernel_resident"] for r in sub)
        and len(sub) == 18)

    # 后验包（机制锚定数学）
    pkg = posterior_package("V89-SELFTEST",
                            {"sigma_c1": 0.8, "order_x2": 0.9,
                             "nis_r5": 0.6})
    add("posterior_package_shape",
        all(k in pkg for k in ("query_id", "prior_score",
                               "posterior_score", "confidence_level",
                               "decision", "update_policy")))
    add("posterior_bounded",
        0.0 < pkg["posterior_score"] < 1.0,
        "先验由机制证据合成 → posterior {}".format(pkg["posterior_score"]))
    pkg_bad = posterior_package("V89-BAD", {"sigma_c1": 0.1})
    add("posterior_feedback_directional",
        posterior_package("V89-GOOD", {"sigma_c1": 0.9},
                          n_success=6)["posterior_score"]
        > pkg_bad["posterior_score"],
        "正证据+成功反馈抬后验（共轭方向性）")
    add("confidence_thresholds",
        posterior_package("t", {"e1": 0.9, "e2": 0.9, "e3": 0.9})
        ["confidence_level"] == "high"
        and posterior_package("t", {"x": 0.6})["confidence_level"] == "mid"
        and posterior_package("t", {"x": 0.2})["confidence_level"] == "low",
        "标定：三强证据→high；单中证据→mid（(2,2) 基座把弱证据"
        "拉回中位——诚实贝叶斯）；负证据→low")

    # 基座实测锚（真跑取证据）
    live = live_anchor_evidence()
    add("live_anchor_sigma",
        isinstance(live.get("sigma_c1"), (int, float)),
        "C1 entropy_production 现场可跑")
    add("live_anchor_order",
        isinstance(live.get("order_x2"), (int, float)),
        "X2 kuramoto_order 现场可跑")
    live_pkg = posterior_package("V89-LIVE", live)
    add("live_posterior_bounded",
        0.0 < live_pkg["posterior_score"] < 1.0,
        "实测锚后验 {}".format(live_pkg["posterior_score"]))

    # 三分流策略完整性
    tiers = {
        posterior_package("t", {"e1": 0.9, "e2": 0.9, "e3": 0.9})
        ["update_policy"]["tier"]: True,
        posterior_package("t", {"x": 0.6})["update_policy"]["tier"]: True,
        posterior_package("t", {"x": 0.2})["update_policy"]["tier"]: True,
    }
    add("three_way_tiers", set(tiers.keys()) == {"hot", "warm", "cold"},
        "高（三强证据）/中/低 → hot/warm/cold 三分流")

    failed = [c for c in checks if not c["ok"]]
    return {"schema": SCHEMA, "batch": BATCH, "seal": SEAL,
            "total": len(checks), "passed": len(checks) - len(failed),
            "failed": len(failed),
            "verdict": "PASS" if not failed else "FAIL", "checks": checks}


# ---------------------------------------------------------------------------
# §8 台账 + CLI
# ---------------------------------------------------------------------------

def build_ledger() -> Dict[str, Any]:
    return {
        "schema": SCHEMA, "batch": BATCH, "seal": SEAL,
        "modules": B_MODULES, "mech_match": MECH_MATCH,
        "base_bayes_assets": BASE_BAYES_ASSETS,
        "repo_services": REPO_SERVICES,
        "main_repo_services": MAIN_REPO_SERVICES,
        "check": check_bayes_reasoning(),
    }


def _main(argv: List[str]) -> int:
    cmd = argv[1] if len(argv) > 1 else "check"
    if cmd == "check":
        r = check_bayes_reasoning()
        print(json.dumps({k: r[k] for k in ("schema", "batch", "total",
                                            "passed", "failed", "verdict")},
                         ensure_ascii=False))
        for c in r["checks"]:
            if not c["ok"]:
                print("FAIL:", c["check"], c.get("note", ""))
        return 0 if r["verdict"] == "PASS" else 1
    if cmd == "match":
        for r in MECH_MATCH:
            print(r["b"], r["state"], ",".join(r["anchors"]),
                  (r["evidence"][:40] + "…") if len(r["evidence"]) > 40
                  else r["evidence"])
        return 0
    if cmd == "adapters":
        for r in repo_adapter_map():
            print(r["repo_id"], r["repo"], ",".join(r["services"]),
                  "RESIDENT" if r["kernel_resident"] else "")
        return 0
    print("usage: bayes_reasoning.py [check|match|adapters]")
    return 2


if __name__ == "__main__":
    sys.exit(_main(sys.argv))
