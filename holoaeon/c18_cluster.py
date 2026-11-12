# -*- coding: utf-8 -*-
"""
C18Cluster —— Node-19 仓库集群基座件（V55 · ring19 集群域）
================================================================================
源声明（诚实边界）：
  · 素材源 = 碳基 2026-11-12 投喂两份外部 AI 蓝图（V3·18仓升级工程包 +
    LINK-01 全息连通包）。本模块为四人组第一性原理扬弃后的**可测子集**，
    不是照搬——扬弃裁决全记录见投喂包第 2 节。
  · 知己知彼侦察实录（grep 实证）：素材要"新建"的核心机制**全部已在 N19
    收口**——心跳→butler_os/bus、经络→fusion_upgrade(meridian)、卡尔曼→
    concept_anatomy、贝叶斯→butler_os、布赫场→concept_anatomy/craft_gate、
    莫比乌斯→mobius_vortex、克莱因→klein_projection、语义→semvec、
    总线→bus/event_channel、契约→fusion_upgrade.contract。
    因此 18 仓=**N19 机制的正交投影**（派生装配，指针纪律），不从零重建。
  · 扬弃（弃）实录：素材"78 梅塔特隆主干边 / 108641 共振带索引 / 每仓 20
    项维度瀑布清单 / 20 步严格按序"均为纸面描述无实测代码——108641 在
    N19 语境是"当前语言模式"数字（玉安记忆之王记忆），不是共振带索引，
    素材挪用数字不诚实，弃。"每仓 20 项"弃为"领域问题+同构骨架+验证脚本"
    三件，其余为 N19 共享机制（指针）。
  · 生克系数 = 常量 + 可标定声明（素材原文"建议初值，可标定"如实保留）。

张量向量耦合（不变）：集群指纹轴 = hypervector.make("c18:" + repo_id)；
仓向量 = bundle(相位轴, 领域问题 token 轴)——与 V52/V53/V54 同族编码。
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .hypervector import HypervectorSpace

# ---------------------------------------------------------------- 链位
CHAIN_POSITION = {
    "ring": 19,
    "layer": "operator",
    "domain": "集群·仓库集群基座（Node-19 正交投影）",
    "batch": "V55",
    "upstream": [
        "N19 holoaeon（唯一归零锚·唯一全局观测者·32ee152 收口态）",
        "hypervector（Hyperspace 张量轴载体·V51-V54 同层）",
        "fusion_upgrade.contract（仓间契约先例·meridian）",
        "bus/event_channel（跨仓事件总线先例）",
    ],
}

SEAL = "潮起开门，潮落闭嘴"

GITHUB_ORG = "weideyouni"          # GitHub 账号（N19=holoaeon 同账号）
N19_REPO = "holoaeon"              # 第 19 号基座仓（已完成，只扩展不重构）

# ---------------------------------------------------------------- 18 仓注册表
# 取素材领域本体（每仓 9 字段精简——非 20 项瀑布），弃虚构数字。
# question=第一性原理问题；turtle/horse=神龟神马分工（素材 YAML 规范模块化）。
C18_NUMBERING: List[Dict[str, str]] = [
    {"id": "C01", "repo": "holoaeon-c01-source", "domain": "本源",
     "question": "我是谁、如何归零",
     "phase_main": "土", "phase_sub": "水", "role": "归零枢纽",
     "turtle": "保存本源记忆与身份基线（归零锚定、土相承载）",
     "horse": "生成身份可能性与意义路径（四相位流动）"},
    {"id": "C02", "repo": "holoaeon-c02-body", "domain": "身体",
     "question": "身体如何被感知与调节",
     "phase_main": "水", "phase_sub": "土", "role": "藏与承载",
     "turtle": "保存健康基线与慢病管理记录",
     "horse": "推演健康趋势与恢复路径"},
    {"id": "C03", "repo": "holoaeon-c03-meridian", "domain": "经络",
     "question": "信息如何传导、阻塞如何发现",
     "phase_main": "枢纽", "phase_sub": "水", "role": "传导枢纽",
     "turtle": "记录通道通畅度与驻波阻塞点",
     "horse": "推演疏通与共振修复方案"},
    {"id": "C04", "repo": "holoaeon-c04-family", "domain": "家庭",
     "question": "亲缘如何影响个体稳态",
     "phase_main": "土", "phase_sub": "火", "role": "亲缘承载",
     "turtle": "保存家族历史与代际模式",
     "horse": "推演沟通与修复策略"},
    {"id": "C05", "repo": "holoaeon-c05-education", "domain": "教育",
     "question": "知识如何内化与转化",
     "phase_main": "木", "phase_sub": "火", "role": "生发",
     "turtle": "保存学习轨迹与能力基线",
     "horse": "推演学习路径与知识缺口"},
    {"id": "C06", "repo": "holoaeon-c06-career", "domain": "职业",
     "question": "能力如何发展与变现",
     "phase_main": "火", "phase_sub": "金", "role": "发散与成果",
     "turtle": "保存履历与长期目标",
     "horse": "推演转型与机会窗口"},
    {"id": "C07", "repo": "holoaeon-c07-wealth", "domain": "财富",
     "question": "资源如何流动与配置",
     "phase_main": "金", "phase_sub": "土", "role": "收敛与积累",
     "turtle": "保存资产基线与风险记录",
     "horse": "推演配置与对冲策略"},
    {"id": "C08", "repo": "holoaeon-c08-creation", "domain": "创造",
     "question": "创造如何被激发与沉淀",
     "phase_main": "木", "phase_sub": "火", "role": "生发爆发",
     "turtle": "保存作品库与风格基线",
     "horse": "推演跨界组合与新表达"},
    {"id": "C09", "repo": "holoaeon-c09-relation", "domain": "关系",
     "question": "人际网络如何演化",
     "phase_main": "火", "phase_sub": "土", "role": "交联",
     "turtle": "保存信任基线与互动记录",
     "horse": "推演协作机会与修复策略"},
    {"id": "C10", "repo": "holoaeon-c10-emotion", "domain": "情感",
     "question": "情绪如何被识别与转化",
     "phase_main": "火", "phase_sub": "水", "role": "波动",
     "turtle": "保存情绪基线与触发模式",
     "horse": "推演调节与转化路径"},
    {"id": "C11", "repo": "holoaeon-c11-meaning", "domain": "意义",
     "question": "这件事对我意味着什么",
     "phase_main": "枢纽", "phase_sub": "木", "role": "意义枢纽",
     "turtle": "保存价值基线与意义锚点",
     "horse": "推演意义重构与方向调整"},
    {"id": "C12", "repo": "holoaeon-c12-space", "domain": "空间",
     "question": "环境如何影响身心",
     "phase_main": "土", "phase_sub": "金", "role": "场域承载",
     "turtle": "保存居住历史与环境偏好",
     "horse": "推演迁移与场域优化"},
    {"id": "C13", "repo": "holoaeon-c13-time", "domain": "时间",
     "question": "节律与历史如何影响当下",
     "phase_main": "水", "phase_sub": "木", "role": "节律之藏",
     "turtle": "保存历史轨迹与周期记录",
     "horse": "推演时机选择与周期转折"},
    {"id": "C14", "repo": "holoaeon-c14-skill", "domain": "技艺",
     "question": "技能如何被掌握与复用",
     "phase_main": "金", "phase_sub": "水", "role": "方法收敛",
     "turtle": "保存工具库与方法基线",
     "horse": "推演技能组合与跨界迁移"},
    {"id": "C15", "repo": "holoaeon-c15-risk", "domain": "风险",
     "question": "创伤与风险如何识别修复",
     "phase_main": "水", "phase_sub": "金", "role": "风险之藏",
     "turtle": "保存创伤记录与修复基线",
     "horse": "推演预警信号与应对策略"},
    {"id": "C16", "repo": "holoaeon-c16-spirit", "domain": "灵性",
     "question": "修行与觉悟如何被理解",
     "phase_main": "木", "phase_sub": "水", "role": "生发与归藏",
     "turtle": "保存修行历史与觉悟节点",
     "horse": "推演意识扩展与内在整合"},
    {"id": "C17", "repo": "holoaeon-c17-society", "domain": "社会",
     "question": "个体如何与制度文化互动",
     "phase_main": "金", "phase_sub": "火", "role": "制度收敛",
     "turtle": "保存参与历史与制度认知",
     "horse": "推演公共表达与协作路径"},
    {"id": "C18", "repo": "holoaeon-c18-cosmos", "domain": "宇宙",
     "question": "个体如何理解宏观秩序",
     "phase_main": "总枢", "phase_sub": "全息镜像根", "role": "全局镜像",
     "turtle": "保存自然观察与秩序感",
     "horse": "推演宏观关联与系统视角"},
]

# ---------------------------------------------------------------- 五行生克
# 常量+可标定声明（素材原文"建议初值，可标定"如实保留——标定改这里）。
# 系数定义在下方（含 V55 补全的"被生"档）。
# 五行相生环：木→火→土→金→水→木
SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
# 五行相克环：木克土、土克水、水克火、火克金、金克木
KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

PHASES = ("木", "火", "土", "金", "水")
HUB_IDS = ("C03", "C11", "C18")        # 枢纽仓（素材相位表穷举口径）

# 诚实声明：素材系数四档（相生/同气/相克/反克）未覆盖**被生方向**
# （如 土→火 实为"火生土"的反向）——V55 补第五档"被生"，系数与相生
# 同级（生克亲和本身对称，方向只影响传播符号），显式声明不隐瞒。
PHASE_GAIN = {"相生": 1.2, "被生": 1.2, "同气": 1.0, "相克": 0.6, "反克": 0.3}
PHASE_COUPLING = {"相生": 0.8, "被生": 0.8, "同气": 0.6, "相克": 0.4,
                  "反克": 0.2, "枢纽": 1.0}


def phase_relation(a: str, b: str) -> str:
    """主相位→主相位关系（五行生克推导——有向，穷举可测）。

    关系五档：同气 / 相生（a 生 b）/ 被生（b 生 a）/ 相克（a 克 b）/
    反克（b 克 a）。任意五行对必落其一（生克环全覆盖 10 个无序对）。
    """
    if a == b:
        return "同气"
    if a not in PHASES or b not in PHASES:
        return "枢纽"
    if SHENG[a] == b:
        return "相生"
    if SHENG[b] == a:
        return "被生"
    if KE[a] == b:
        return "相克"
    if KE[b] == a:
        return "反克"
    return "无关"     # 不可达（穷举证明），保留作防御性返回
# 四类合法边（素材字段口径——缺字段非法边）。
EDGE_TYPES = ("skeleton", "resonance", "semantic", "event")
EDGE_REQUIRED_FIELDS = (
    "edge_id", "source", "target", "edge_type", "layer",
    "phase_relation", "resonance_strength", "turtle_state",
    "horse_state", "ttl_ticks", "decay_rate", "rollback_token",
)


def validate_edge(edge: Dict[str, Any]) -> Dict[str, Any]:
    """边校验：类型合法+必填字段齐+衰减/回滚硬约束。"""
    problems: List[str] = []
    if edge.get("edge_type") not in EDGE_TYPES:
        problems.append("edge_type 非四类合法边: %r" % edge.get("edge_type"))
    for f in EDGE_REQUIRED_FIELDS:
        if f not in edge:
            problems.append("缺字段: %s" % f)
    ttl = edge.get("ttl_ticks")
    if not isinstance(ttl, int) or ttl < 12:
        problems.append("ttl_ticks 硬约束 ≥12: %r" % ttl)
    dr = edge.get("decay_rate")
    if not isinstance(dr, (int, float)) or not (0 < dr < 1):
        problems.append("decay_rate 须 (0,1): %r" % dr)
    if not edge.get("rollback_token"):
        problems.append("rollback_token 空（连通必须可回滚）")
    ids = {c["id"] for c in C18_NUMBERING} | {"N19"}
    if edge.get("source") not in ids or edge.get("target") not in ids:
        problems.append("端点不在 19 仓编号域")
    return {"ok": not problems, "problems": problems}


# ---------------------------------------------------------------- 耦合矩阵
# 工程裁决（第一性原理）：初始耦合矩阵 = **无向亲和**（与素材边 Schema
# 里 resonance 无向边、resonance_strength 标量一致）——克对统一 0.4、
# 生对统一 0.8、同气 0.6、枢纽 1.0。有向差异（相生1.2/被生1.2/同气1.0/
# 相克0.6/反克0.3）保留在 PHASE_GAIN 传播增益档（事件传播用，非耦合用）。
AFFINITY = {"生": 0.8, "同": 0.6, "克": 0.4, "枢纽": 1.0}


def phase_affinity(a: str, b: str) -> str:
    """无向相位亲和（耦合矩阵用）：生/同/克/枢纽——对称。"""
    if a == b:
        return "同"
    if a not in PHASES or b not in PHASES:
        return "枢纽"
    if SHENG[a] == b or SHENG[b] == a:
        return "生"
    if KE[a] == b or KE[b] == a:
        return "克"
    return "枢纽"      # 不可达（生克环全覆盖）


class CouplingMatrix:
    """19×19 初始耦合矩阵：五行生克确定性推导（弃素材 78 边虚构映射）。

    规则（穷举可验证，对称）：
      · N19 与所有仓：1.0（唯一锚全连接——素材"枢纽强化"的诚实化）；
      · 枢纽仓（C03/C11/C18）与所有仓：AFFINITY["枢纽"]；
      · 其余 (i,j)：主相位无向亲和 → AFFINITY[关系]；
      · 对角线 = 0（自耦合无意义）。
    """

    def __init__(self, numbering: Optional[Sequence[Dict[str, str]]] = None):
        self.numbering = list(numbering or C18_NUMBERING)
        self.ids = [c["id"] for c in self.numbering] + ["N19"]

    def value(self, a: str, b: str) -> float:
        if a == b:
            return 0.0
        if a == "N19" or b == "N19":
            return 1.0
        ea = next(c for c in self.numbering if c["id"] == a)
        eb = next(c for c in self.numbering if c["id"] == b)
        if a in HUB_IDS or b in HUB_IDS:
            return AFFINITY["枢纽"]
        return AFFINITY[phase_affinity(ea["phase_main"], eb["phase_main"])]

    def matrix(self) -> Dict[str, Dict[str, float]]:
        return {a: {b: round(self.value(a, b), 4) for b in self.ids}
                for a in self.ids}

    def validate(self) -> Dict[str, Any]:
        m = self.matrix()
        problems: List[str] = []
        if len(m) != 19 or any(len(row) != 19 for row in m.values()):
            problems.append("矩阵非 19×19")
        for a, row in m.items():
            if row.get(a) != 0.0:
                problems.append("%s 对角非 0" % a)
        # 对称性：初始耦合按对称对（素材未明确方向性——初始对称可测）
        for a in self.ids:
            for b in self.ids:
                if a < b and m[a][b] != m[b][a]:
                    problems.append("(%s,%s) 非对称" % (a, b))
        n19_row = [m["N19"][b] for b in self.ids if b != "N19"]
        if any(v != 1.0 for v in n19_row):
            problems.append("N19 锚未全连接")
        return {"ok": not problems, "problems": problems[:10],
                "size": len(m)}


# ---------------------------------------------------------------- 复用映射
# 知己知彼表：素材要"新建"的机制 → N19 在仓真实模块（grep 实证）。
# 第一性原理落实：18 仓=投影装配，不从零重建。
REUSE_MAP: Dict[str, str] = {
    "心跳调度": "butler_os / bus（心跳与节拍先例）",
    "经络传导": "fusion_upgrade（meridian 契约机制·V51R 同构）",
    "卡尔曼滤波": "concept_anatomy（状态轨迹先例）",
    "贝叶斯反演": "butler_os / dehallucination（先验反演先例）",
    "布赫场": "concept_anatomy / craft_gate（协作场先例）",
    "莫比乌斯翻转": "mobius_vortex（V26 收口件）",
    "克莱因收敛": "klein_projection（V27 收口件）",
    "曼陀罗扩张": "klein_projection / concept_anatomy（一拖八先例）",
    "语义通信": "semvec（V22+ 确定性分词·张量轴）",
    "事件总线": "bus / event_channel（跨仓事件先例）",
    "升级契约": "fusion_upgrade.contract（只交换回执不换代码）",
    "张量载体": "hypervector（HypervectorSpace·V51-V54 同层）",
}


# ---------------------------------------------------------------- 集群张量
class ClusterTensor:
    """集群张量：仓向量 = bundle(相位轴, 领域问题 token 轴)。

    与 V52 StyleTensor / V53 PaletteTensor 同族编码（张量耦合不变）。
    检索：cosine（两仓问题+相位亲和度——同构不同质的量化窗）。
    """

    def __init__(self, space: Optional[HypervectorSpace] = None):
        self.space = space or HypervectorSpace()

    def encode_cang(self, cang: Dict[str, str]) -> List[float]:
        cat_axis = self.space.make("phase:" + cang["phase_main"])
        q_axis = self.space.make("q:" + cang["question"])
        acc = [a + b for a, b in zip(cat_axis, q_axis)]
        norm = math.sqrt(sum(x * x for x in acc))
        return [x / norm for x in acc] if norm else acc

    def encode_all(self) -> Dict[str, List[float]]:
        return {c["id"]: self.encode_cang(c) for c in C18_NUMBERING}

    def similarity(self, a: Dict[str, str], b: Dict[str, str]) -> float:
        va, vb = self.encode_cang(a), self.encode_cang(b)
        return self.space.cosine(va, vb)


# ---------------------------------------------------------------- 总闸
class ClusterGate:
    """ring19 集群总闸：注册表完整性 + 矩阵穷举 + 边 Schema + 分化度。"""

    def __init__(self, numbering: Optional[Sequence[Dict[str, str]]] = None):
        self.numbering = list(numbering or C18_NUMBERING)
        self.matrix = CouplingMatrix(self.numbering)
        self.tensor = ClusterTensor()

    def self_check(self) -> dict:
        checks: Dict[str, dict] = {}
        ids = [c["id"] for c in self.numbering]
        # ① 注册表穷举
        checks["numbering"] = {
            "ok": len(ids) == 18 and ids == ["C%02d" % i for i in
                                             range(1, 19)],
            "count": len(ids),
        }
        # ② 相位穷举（素材口径：木3火3土3金3水3+3枢纽）
        mains = [c["phase_main"] for c in self.numbering]
        n_per = {p: sum(1 for m in mains if m == p) for p in PHASES}
        n_hub = sum(1 for m in mains if m not in PHASES)
        checks["phases"] = {
            "ok": all(n_per[p] == 3 for p in PHASES) and n_hub == 3,
            "dist": {**n_per, "枢纽/总枢": n_hub},
        }
        # ③ 矩阵 19×19 穷举
        checks["matrix"] = self.matrix.validate()
        # ④ 边 Schema 样例（skeleton 合法边 + 非法边各一）
        good = {"edge_id": "e_000001", "source": "C02", "target": "C10",
                "edge_type": "resonance", "layer": "L2",
                "phase_relation": phase_relation("水", "火"),
                "resonance_strength": 0.87, "turtle_state": "baseline_locked",
                "horse_state": "pathway_exploring", "ttl_ticks": 12,
                "decay_rate": 0.85, "rollback_token": "rb_v55_0001"}
        bad = dict(good, ttl_ticks=6, rollback_token="")
        checks["edge_schema"] = {
            "ok": validate_edge(good)["ok"] and
                  (not validate_edge(bad)["ok"]) and
                  validate_edge(good)["ok"],
        }
        # ⑤ 分化度（S5 反向指标：仓向量两两 cosine 均值 ≤0.70——同构不同质）
        vecs = self.tensor.encode_all()
        pairs = [(a, b) for i, a in enumerate(ids) for b in ids[i + 1:]]
        sims = [self.tensor.space.cosine(vecs[a], vecs[b])
                for a, b in pairs]
        mean_sim = round(sum(sims) / len(sims), 4) if sims else 0.0
        checks["diversity"] = {
            "ok": mean_sim <= 0.70, "mean_similarity": mean_sim,
            "pairs": len(pairs),
            "note": "S5 反向指标（素材口径）——同构而不同质",
        }
        ok_all = all(c["ok"] for c in checks.values())
        return {"ok": ok_all, "checks": checks,
                "chain_position": CHAIN_POSITION, "seal": SEAL}

    def repo_urls(self) -> Dict[str, str]:
        out = {c["id"]: "https://github.com/%s/%s" % (GITHUB_ORG, c["repo"])
               for c in self.numbering}
        out["N19"] = "https://github.com/%s/%s" % (GITHUB_ORG, N19_REPO)
        return out


# ---------------------------------------------------------------- 工具/CLI

def _now_iso() -> str:
    import datetime
    return datetime.datetime.now().isoformat(timespec="seconds")


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def fingerprint() -> dict:
    return {
        "module": "c18_cluster",
        "ring": CHAIN_POSITION["ring"],
        "batch": CHAIN_POSITION["batch"],
        "domain": CHAIN_POSITION["domain"],
        "sha256": _sha256("c18-cluster-v1:" + SEAL),
        "seal": SEAL,
    }


def probe() -> dict:
    """轻量探针：不依赖外部数据（内置注册表）。"""
    g = ClusterGate()
    sc = g.self_check()
    return {"ok": sc["ok"], "cang_count": len(g.numbering),
            "matrix_size": len(g.matrix.matrix()),
            "mean_similarity": sc["checks"]["diversity"]["mean_similarity"],
            "seal": SEAL}


def _main(argv: List[str]) -> int:
    import sys
    cmd = argv[1] if len(argv) > 1 else "probe"
    if cmd == "probe":
        out = probe()
    elif cmd == "fingerprint":
        out = fingerprint()
    elif cmd == "repos":
        out = ClusterGate().repo_urls()
    elif cmd == "run":
        out = ClusterGate().self_check()
    else:
        print("usage: python -m holoaeon.c18_cluster "
              "[probe|fingerprint|repos|run]", file=sys.stderr)
        return 2
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if out.get("ok", True) else 1


if __name__ == "__main__":
    import sys
    raise SystemExit(_main(["c18_cluster"] + sys.argv[1:]))
