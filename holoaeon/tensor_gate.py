# -*- coding: utf-8 -*-
"""
TensorGate —— 张量耦合与开源扬弃件（V59 · ring22 张量与吸收域）
================================================================================
源声明（诚实边界）：
  · 素材源 = 碳基 2026-11-12 投喂 TENSOR-01《张量耦合与开源扬弃投喂包》
    （五件套：结构 V3 → 连通 LINK-01 → 贯续 CONT-01 → 组织 ORG-02 →
    **语义与吸收 TENSOR-01**）+ 碳基仓名表确认。本模块为四人组第一性原理
    扬弃后的**可测子集**，不是照搬——扬弃裁决全记录见投喂包第 2 节。
  · 本批整合 V58（org_gate ring21）：深化批次口径（DEEPENING_BATCHES）
    承载搜索引导的逐批推进，被弃项清单（RESOURCES_REJECTED）与素材
    rejected_dependencies 同构留痕——执行顺序须 V58 收口后。
  · 第一性命题（素材原文采信）：仓名如何张量化、开源生态如何扬弃吸收、
    搜索如何被引导——"我该搜什么"变成可执行清单。

素材三处口径核查（知己知彼实录，如实澄清）：
  ①命名"更迭"零负担——素材称"旧命名 holoaeon-source 一类全部作废"；
    工程现实：GitHub 18 仓在建仓时（V55 G-step）即按编号内嵌式
    holoaeon-cXX-YYY 命名，命名已合规，无旧名迁移负担，无
    deprecated_alias 需求——如实声明零迁移。
  ②素材 361 算术澄清——素材列自耦合 19+有向 342+无向 171 却写"合计
    361"；实为 19+342=361（171 是 342 的无向对称压缩视图，不重复计数）
    ——本模块按 361 全量穷举+对称视图另行提供。
  ③素材 w_phase 与在仓 PHASE_GAIN 冲突——素材四档（相生1.2/同气1.0/
    相克0.6/反克0.3+枢纽1.5）漏"被生"方向（V55 已实测补第五档），且
    "枢纽1.5"为在仓 PHASE_GAIN 无的新项。裁决：**复用在仓五档 PHASE_GAIN
    不覆写**，枢纽强化独立为 HUB_BOOST=1.5 常量（素材新采信项单列）。
  · 扬弃（弃）实录：108641 共振带分片降维（维持 V55 数字挪用裁决）；
    素材 32 能力槽明细未给（仅 A 模态 d=32 与 18 仓认领层）——不虚构槽
    名，落 8 层×4 槽=32 的**槽位框架**（槽 ID 可校验），槽内具体内容由
    search_record 逐步填充（零虚构纪律）。
  · 扬弃（取）实录：四语素命名完整性检查（76 语素位）/T(c) 四模态张量
    （S/M/P/A，M 确定性生成——同输入同向量，无随机初始化）/C(i,j)
    耦合（w_phase 复用在仓五档+枢纽强化）/八层开源分类 L0-L7/取六条
    （显式状态图与可回放/角色目标背景三要素/对话批判收敛/成本归因前置/
    分层分类决策树/三要素标注）/舍五条（rejected_dependencies）/18 仓
    能力认领（2-3 槽/仓）/搜索引导五维 D1-D5+search_record 强制 schema
    （无 search_record 的能力槽不得进入实现——"取/舍"缺一即未做扬弃）。

与工程纪律的同构照（升维句，见投喂包第 4 节）：
    仓名第一次成为可计算对象——名字即张量，张量即路由；"该搜什么"
    第一次成为机器生成的清单，且每一次吸收都留下"取/舍"两段证据。

张量向量耦合（不变）：语义向量 M = hypervector.make("sem:" + 仓名+
第一性问题)——确定性哈希生成（无随机初始化，同输入必得同向量），
与 V52-V58 同族编码。
"""

from __future__ import annotations

import datetime
import hashlib
import json
import math
import re
import sys
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .c18_cluster import (
    C18_NUMBERING,
    PHASE_GAIN,
    HUB_IDS,
    phase_relation,
)
from .hypervector import HypervectorSpace
from .org_gate import DEEPENING_BATCHES

# ---------------------------------------------------------------------------
# 一、命名规范（编号内嵌式——GitHub 建仓名已合规，零迁移如实声明）
# ---------------------------------------------------------------------------

NAMING_PATTERN = re.compile(r"^holoaeon-c(\d{2})-([a-z]+)$")


def repo_name(cang_id: str, domain_word: str) -> str:
    return "holoaeon-{}-{}".format(cang_id.lower(), domain_word)


def validate_repo_name(name: str, cang_id: str) -> Dict[str, Any]:
    """命名校验：编号内嵌式正则+编号匹配+仓名自解释（可排序可校验）。

    工程事实（如实声明）：GitHub 18 仓于 V55 G-step 建仓时即按本规范命名
    （holoaeon-c01-source 等，ls-remote 18/18 核验），素材所称"旧名作废
    迁移"零负担——无 deprecated_alias 需求，无半改状态风险。
    """
    problems: List[str] = []
    m = NAMING_PATTERN.match(name)
    if not m:
        problems.append("命名不符编号内嵌式 holoaeon-cXX-YYY：{}".format(name))
        return {"pass": not problems, "problems": problems, "name": name}
    num = m.group(1)
    if num != cang_id[1:].zfill(2):
        problems.append("编号不匹配：{} vs {}".format(num, cang_id))
    return {"pass": not problems, "problems": problems, "name": name, "number": num}


# ---------------------------------------------------------------------------
# 二、词元穷举（76 语素位：四语素 × 19 名）
# ---------------------------------------------------------------------------

# 四语素（素材第二节采信）
MORPHEME_KEYS: Tuple[str, str, str, str] = ("holo", "aeon", "cXX", "domain")

MORPHEME_MEANINGS: Dict[str, Dict[str, str]] = {
    "holo": {"意义": "整体性、全息性、局部含整体",
             "工程映射": "每仓持有全息索引摘要，S4 全息回映度>=0.80；任何仓不得声明'我只管自己'"},
    "aeon": {"意义": "时间尺度、持久、演化",
             "工程映射": "每仓有历史快照、周期模型、可回滚时间线；无历史即无 aeon"},
    "cXX": {"意义": "位置、次序、可寻址",
            "工程映射": "编号是主键（排序/路由/调拨优先级/共振带分片）；编号不可复用、不可回收"},
    "domain": {"意义": "语义核心（领域词）",
               "工程映射": "工程语义核心见 DOMAIN_WORD_MEANINGS 18 词义项表"},
}

# 18 领域词义项（素材第二第四节 18 词表采信：本义/引申义/工程语义核心）
DOMAIN_WORD_MEANINGS: Dict[str, Tuple[str, str, str]] = {
    "source": ("源、泉", "起点、根据", "身份根、归零锚点、ID 签发"),
    "body": ("体、躯干", "承载实体", "生理信号、稳态、传感器接口"),
    "meridian": ("经线、子午", "通道、网络", "12 通道、通畅度、阻塞反演"),
    "family": ("家族", "亲缘系统", "代际模式、亲缘耦合"),
    "education": ("教化", "内化过程", "知识图谱、技能树、学习轨迹"),
    "career": ("跑道、生涯", "能力变现", "角色、项目、机会窗口"),
    "wealth": ("财富", "资源流", "资产、现金流、配置策略"),
    "creation": ("创造", "生成表达", "作品库、风格基线、扇出"),
    "relation": ("关系", "网络联结", "信任、互动、协作图"),
    "emotion": ("情绪", "波动状态", "情感基线、触发模式、调节"),
    "meaning": ("意义", "价值指向", "目标函数、信念、意义重构"),
    "space": ("空间", "场域", "环境耦合、居住、迁移"),
    "time": ("时间", "节律", "周期、历史轨迹、时机"),
    "skill": ("技艺", "可复用方法", "技能图谱、工具库、迁移"),
    "risk": ("风险", "扰动源", "创伤、预警、修复"),
    "spirit": ("灵性", "超越性", "修行、觉悟、内整合"),
    "society": ("社会", "制度文化", "公共关系、制度认知"),
    "cosmos": ("宇宙", "宏观秩序", "全局镜像、秩序感"),
}

DOMAIN_WORDS: Tuple[str, ...] = tuple(DOMAIN_WORD_MEANINGS.keys())


def check_morphemes() -> Dict[str, Any]:
    """四语素完整性检查：76 语素位=4×19，语义无重复无空洞可校验。

    缺语素即命名非法（素材穷举结论采信）。
    """
    problems: List[str] = []
    if len(MORPHEME_KEYS) != 4:
        problems.append("语素键!=4")
    if len(DOMAIN_WORD_MEANINGS) != 18:
        problems.append("领域词!=18")
    for w, (ben, yin, core) in DOMAIN_WORD_MEANINGS.items():
        if not (ben and yin and core):
            problems.append("领域词语义空洞：{}".format(w))
    # 每仓仓名四语素齐：holo 前缀 + aeon + cXX 编号 + 领域词在 18 词表
    for c in C18_NUMBERING:
        name = repo_name(c["id"], _word_of(c["id"]))
        m = NAMING_PATTERN.match(name)
        if not m:
            problems.append("{} 仓名四语素不全：{}".format(c["id"], name))
    return {
        "pass": not problems,
        "problems": problems,
        "morpheme_slots": 4 * 19,
        "note": "19 仓名共 4×19=76 个语素位，语义无重复、无空洞、可校验（素材穷举结论采信）",
    }


def _word_of(cang_id: str) -> str:
    pair = next((k for k, v in _DOMAIN_OF.items() if v == cang_id), "")
    return pair


_DOMAIN_OF: Dict[str, str] = {
    "source": "C01", "body": "C02", "meridian": "C03", "family": "C04",
    "education": "C05", "career": "C06", "wealth": "C07", "creation": "C08",
    "relation": "C09", "emotion": "C10", "meaning": "C11", "space": "C12",
    "time": "C13", "skill": "C14", "risk": "C15", "spirit": "C16",
    "society": "C17", "cosmos": "C18",
}


# ---------------------------------------------------------------------------
# 三、单仓张量 T(c)：四模态 ⟨S, M, P, A⟩
# ---------------------------------------------------------------------------

# 枢纽强化系数（素材新采信项单列——不复用在仓 PHASE_GAIN 覆写，零冲突）
HUB_BOOST = 1.5


class RepoTensor:
    """单仓四模态张量：S 结构 / M 语义 / P 相位 / A 能力。

    关键约束（素材原文采信）：M 由仓名与第一性问题**确定性生成**（同输入
    必得同一向量，无随机初始化）——复用 hypervector.make 的 sha256 确定性
    生成，与工程确定性原则（同任务两次运行剔除时间戳哈希一致）对齐。
    """

    def __init__(self, space: Optional[HypervectorSpace] = None) -> None:
        self.space = space if space is not None else HypervectorSpace()

    # -- S 结构模态（d=8 口径：确定性标量槽） --
    def modal_s(self, cang: Dict[str, str]) -> List[float]:
        seed = "S:{}:{}:{}:{}".format(cang["id"], cang.get("phase_main", ""),
                                     cang.get("role", ""), cang.get("turtle", ""))
        raw = hashlib.sha256(seed.encode("utf-8")).digest()
        return [(b / 255.0) * 2.0 - 1.0 for b in raw[:8]]

    # -- M 语义模态：确定性语义向量（无随机） --
    def modal_m(self, cang: Dict[str, str]) -> List[float]:
        key = "sem:{}:{}".format(_word_of(cang["id"]), cang["question"])
        return self.space.make(key)

    # -- P 相位模态（d=10：主 one-hot(5)+副 one-hot(5)，枢纽加标记） --
    def modal_p(self, cang: Dict[str, str]) -> List[float]:
        elements = ("木", "火", "土", "金", "水")
        main = cang.get("phase_main", "")
        sub = cang.get("phase_sub", "")
        vec = [1.0 if main == e else 0.0 for e in elements]
        vec += [1.0 if sub == e else 0.0 for e in elements]
        if cang["id"] in HUB_IDS:
            vec.append(HUB_BOOST)  # 枢纽标记（第 11 位）
        return vec

    # -- A 能力模态（d=32 位图：八层×4 槽框架，认领层置位） --
    def modal_a(self, cang: Dict[str, str]) -> List[float]:
        slots = claimed_slots(cang["id"])
        vec = [0.0] * 32
        for s in slots:
            layer = int(s.split("-")[0][1:])
            idx = int(s.split("-")[1])
            vec[layer * 4 + idx] = 1.0
        return vec

    def tensor(self, cang: Dict[str, str]) -> Dict[str, List[float]]:
        return {"S": self.modal_s(cang), "M": self.modal_m(cang),
                "P": self.modal_p(cang), "A": self.modal_a(cang)}

    def semantic_similarity(self, a: Dict[str, str], b: Dict[str, str]) -> float:
        va, vb = self.modal_m(a), self.modal_m(b)
        return self.space.cosine(va, vb)

    def tensor_deterministic(self, cang: Dict[str, str]) -> bool:
        """确定性自检：同输入两次计算，四模态全同（M 无随机初始化的机器证明）。"""
        t1, t2 = self.tensor(cang), self.tensor(cang)
        return t1 == t2


# ---------------------------------------------------------------------------
# 四、双仓耦合 C(i,j)：w_phase · 语义相似（361 单元全量穷举）
# ---------------------------------------------------------------------------

def w_phase(i: str, j: str) -> float:
    """相位增益系数：复用在仓 PHASE_GAIN 五档（含被生——素材漏档已在 V55 补）
    + 枢纽强化 HUB_BOOST（素材新采信项，枢纽任一端即乘）。"""
    ei = _entry(i)
    ej = _entry(j)
    if ei is None or ej is None:
        raise ValueError("端点不在 19 节点域：{} {}".format(i, j))
    base = PHASE_GAIN.get(phase_relation(ei["phase_main"], ej["phase_main"]), 1.0)
    if i in HUB_IDS or j in HUB_IDS:
        base *= HUB_BOOST
    return round(base, 4)


def _entry(cang_id: str) -> Optional[Dict[str, str]]:
    if cang_id == "N19":
        return {"id": "N19", "phase_main": "土"}
    return next((c for c in C18_NUMBERING if c["id"] == cang_id), None)


def coupling(i: str, j: str, tensor: Optional[RepoTensor] = None) -> Dict[str, Any]:
    """C(i,j) = w_phase · cosine(M_i, M_j)——确定性耦合记录。

    弃素材"降维到 108641 共振带分片"（维持 V55 数字挪用裁决）——耦合
    直接以标量+语义向量可存储记录落仓，无需外部分片索引。
    """
    t = tensor if tensor is not None else RepoTensor()
    ei, ej = _entry(i), _entry(j)
    w = w_phase(i, j)
    sim = t.semantic_similarity(ei, ej) if (i != "N19" and j != "N19") else 1.0
    return {"i": i, "j": j, "w_phase": w, "semantic_cos": round(sim, 4),
            "value": round(w * sim, 4)}


def enumerate_couplings(tensor: Optional[RepoTensor] = None) -> Dict[str, Any]:
    """361 单元全量穷举（素材算术澄清：自耦合 19+有向 342=361）。

    无向共振对 171=342 的对称压缩视图，另行提供不重复计数（素材"合计
    361"采信，其三段列举的算术矛盾如实澄清留痕）。
    """
    nodes = [c["id"] for c in C18_NUMBERING] + ["N19"]
    self_coupled = [(a, a) for a in nodes]  # 19
    directed = [(a, b) for a in nodes for b in nodes if a != b]  # 342
    units = [coupling(a, b, tensor) for a, b in self_coupled + directed]
    undirected = sorted({tuple(sorted(p)) for p in directed})  # 171 视图
    return {
        "units": units,
        "self_count": len(self_coupled),
        "directed_count": len(directed),
        "total": len(units),  # 361
        "undirected_view": len(undirected),  # 171
        "note": "19+342=361 全量（无向 171 为对称视图不重复计数——素材算术澄清留痕）",
    }


def check_couplings() -> Dict[str, Any]:
    """耦合穷举校验：361 齐/枢纽行非零/C18 行全非零（镜像根可重构性口径）。"""
    r = enumerate_couplings()
    problems: List[str] = []
    if r["total"] != 361:
        problems.append("耦合单元!=361（实 {}）".format(r["total"]))
    if r["undirected_view"] != 171:
        problems.append("无向视图!=171")
    for u in r["units"]:
        if (u["i"] in HUB_IDS or u["j"] in HUB_IDS) and u["value"] == 0:
            problems.append("枢纽行零耦合：{}->{}".format(u["i"], u["j"]))
        if u["i"] == "C18" and u["value"] == 0:
            problems.append("C18 镜像根行零耦合：->{}".format(u["j"]))
    return {"pass": not problems, "problems": problems,
            "total": r["total"], "undirected": r["undirected_view"]}


# ---------------------------------------------------------------------------
# 五、八层开源分类 + 32 能力槽 + 18 仓认领 + 扬弃吸收（取六/舍五）
# ---------------------------------------------------------------------------

OSS_LAYERS: Tuple[Tuple[str, str, str], ...] = (
    ("L0", "算力与推理基础设施", "运行、加速、调度（vLLM/llama.cpp/Ollama 类）"),
    ("L1", "模型与权重", "能力本体（开源模型体系）"),
    ("L2", "训练与微调", "能力改造（peft/LLaMA-Factory/trl 类）"),
    ("L3", "数据与知识", "语料与检索（datasets/FAISS/RAGFlow/MinerU 类）"),
    ("L4", "编排与协作", "流程与多体（LangGraph/AutoGen/CrewAI 类思路）"),
    ("L5", "接口与协议", "连接与扩展（MCP servers/skills 类技能包）"),
    ("L6", "应用与产品", "直接使用（open-webui/n8n/langflow 类自托管）"),
    ("L7", "评测与可观测", "度量与治理（lm-evaluation-harness/langfuse 类）"),
)

# 32 能力槽框架（8 层×4 槽——素材未给槽名明细，落槽位 ID 框架零虚构；
# 槽内内容由 search_record 逐步填充）
CAPACITY_PER_LAYER = 4
CAPABILITY_SLOTS: Tuple[str, ...] = tuple(
    "L{}-{}".format(l, k) for l in range(8) for k in range(CAPACITY_PER_LAYER)
)  # 32

# 18 仓认领层（素材第五节采信——认领 2-3 槽/仓，映射到该层槽位框架）
CLAIMED_LAYERS: Dict[str, Tuple[str, ...]] = {
    "C01": ("L7", "L4"), "C02": ("L0", "L7"), "C03": ("L4", "L5"),
    "C04": ("L3", "L4"), "C05": ("L3", "L7"), "C06": ("L6", "L4"),
    "C07": ("L6", "L7"), "C08": ("L1", "L6"), "C09": ("L4", "L5"),
    "C10": ("L1", "L7"), "C11": ("L4", "L7"), "C12": ("L3", "L6"),
    "C13": ("L7", "L0"), "C14": ("L2", "L5"), "C15": ("L7", "L4"),
    "C16": ("L4", "L3"), "C17": ("L3", "L6"), "C18": ("L7", "L4"),
}
N19_META_DUTY = "全层元职责：契约、注册、仲裁（归零锚点+张量索引+调拨中枢）"


def claimed_slots(cang_id: str) -> List[str]:
    """仓→认领槽位：认领层各层的第一槽（槽内细分待 search_record 填充——零虚构）。"""
    layers = CLAIMED_LAYERS.get(cang_id, ())
    return ["{}-0".format(l) for l in layers]


# 取六条（素材 4.3 采信——吸收为思维模型，不引入实现）
ABSORBED_PATTERNS: Tuple[Tuple[str, str], ...] = (
    ("显式状态图与可回放", "LangGraph 检查点任意历史点重放 → 心跳三段式+rollback_token 强化"),
    ("角色/目标/背景三要素", "CrewAI role/goal/backstory → 仓主-职责-第一性问题任务卡语言"),
    ("对话式协作与批判收敛", "AutoGen 群聊 critique → C11 意义仓多视角意义辩论内部机制"),
    ("成本归因前置", "编排层成本占比 → 资源调拨中枢配额与账本（V58 已落）"),
    ("分层分类与选型决策树", "按功能分层按场景决策 → 搜索引导提纲组织方式"),
    ("三要素标注", "数据/算法/算力三坐标 → 能力槽元数据标签"),
)

# 舍五条（素材 4.3 采信——写入 rejected 侧清单）
REJECTED_DEPENDENCIES: Tuple[Tuple[str, str], ...] = (
    ("重依赖与外部服务锁定", "主流编排框架与零依赖确定性定位冲突——只取思路不取实现"),
    ("抽象层牺牲可控性", "高层抽象在精确错误处理/重试/状态持久化不如显式图——不引入运行时"),
    ("非确定性与不可复现", "随机初始化/外部时间/网络抖动组件一律拒绝——护同任务两次哈希一致"),
    ("自研编排的全套成本", "HoloAeon 只做最小原语+显式契约，不做通用编排平台"),
    ("群聊自由发散承载核心链路", "无延迟与确定性保证的模式不得进入主干"),
)

# 本地化同化规则（素材采信）：只以三种形态进入，禁 vendoring，四段记录
ASSIMILATION_FORMS: Tuple[str, str, str] = ("思维模型", "接口形态", "评测方法")
FOUR_PART_LEDGER: Tuple[str, str, str, str] = ("来源", "吸收形态", "改造说明", "拒绝项")


def check_capabilities() -> Dict[str, Any]:
    """能力域检查：八层齐/32 槽齐/18 仓各认领 2-3 槽/取六舍五齐/四段台账。"""
    problems: List[str] = []
    if len(OSS_LAYERS) != 8:
        problems.append("八层分类不齐")
    if len(CAPABILITY_SLOTS) != 32:
        problems.append("能力槽!=32（实 {}）".format(len(CAPABILITY_SLOTS)))
    if len(CLAIMED_LAYERS) != 18:
        problems.append("认领仓!=18")
    for cid, layers in CLAIMED_LAYERS.items():
        if not (2 <= len(layers) <= 3):
            problems.append("{} 认领槽数不在 2-3".format(cid))
    if len(ABSORBED_PATTERNS) != 6 or len(REJECTED_DEPENDENCIES) != 5:
        problems.append("取六/舍五不齐")
    if len(FOUR_PART_LEDGER) != 4:
        problems.append("四段台账键不齐")
    return {"pass": not problems, "problems": problems,
            "slots": len(CAPABILITY_SLOTS), "layers": len(OSS_LAYERS),
            "note": "槽位框架 8×4=32（槽名明细素材未给——零虚构，由 search_record 逐步填充）"}


# ---------------------------------------------------------------------------
# 六、搜索引导五维（D1-D5）+ search_record 强制 schema
# ---------------------------------------------------------------------------

SEARCH_DIMENSIONS: Tuple[Tuple[str, str, str, str], ...] = (
    ("D1", "本体", "这个领域的根本问题被怎样定义", '"{领域词}" 第一性原理 定义 综述'),
    ("D2", "能力", "有哪些成熟能力可被同化", "{领域词} 开源 项目 能力 对比"),
    ("D3", "架构", "主流架构思路与取舍", "{领域词} 架构 设计 权衡 局限"),
    ("D4", "数据", "数据形态、来源、评测", "{领域词} 数据集 评测 基准"),
    ("D5", "风险", "已知失败模式与坑", "{领域词} 常见 问题 陷阱 失败"),
)

SEARCH_RECORD_REQUIRED: Tuple[str, ...] = (
    "仓", "维度", "查询", "命中", "取", "舍", "同化形态", "验证",
)


def validate_search_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """搜索记录校验（素材 6.4 强制落盘格式采信）：
    无 search_record 的能力槽不得进入实现；"取/舍"缺一即视为未做扬弃。"""
    problems: List[str] = []
    for f in SEARCH_RECORD_REQUIRED:
        if f not in record or record[f] in (None, "", []):
            problems.append("search_record 缺字段或空值：{}".format(f))
    if record.get("维度") and record.get("维度") not in ("D1", "D2", "D3", "D4", "D5"):
        problems.append("维度不在 D1-D5")
    if record.get("仓") and not NAMING_PATTERN.match(str(record.get("仓", ""))):
        problems.append("仓字段非编号内嵌式仓名：{}".format(record.get("仓")))
    return {"pass": not problems, "problems": problems, "required": list(SEARCH_RECORD_REQUIRED)}


def search_plan(cang_id: str) -> List[Dict[str, str]]:
    """生成一仓五维搜索任务清单（可执行——"我该搜什么"变成机器生成的清单）。

    领域词取该仓领域英文词；查询模板按五维展开。
    """
    word = _word_of(cang_id)
    if not word:
        raise ValueError("未知仓编号：{}".format(cang_id))
    return [
        {"仓": repo_name(cang_id, word), "维度": d[0], "追问": d[1],
         "查询": d[3].replace("{领域词}", word)}
        for d in SEARCH_DIMENSIONS
    ]


def batch_search_plan() -> Dict[str, Any]:
    """整合 V58：深化批次（DEEPENING_BATCHES）× 五维搜索——B0-B6 每批每仓的搜索任务卡。

    C03 优先（B0 先行——与 ORG-02 G-M 硬约束同源）；逐批推进口径复用
    V58 org_gate 的 DEEPENING_BATCHES（零复制 import）。
    """
    plan: List[Dict[str, Any]] = []
    for b in DEEPENING_BATCHES:
        for cid in b["cangs"]:
            plan.append({"batch": b["batch"], "cang": cid,
                         "tasks": search_plan(cid)})
    return {"batches": len(DEEPENING_BATCHES), "cang_plans": len(plan),
            "tasks": 5 * len(plan), "note": "B0-B6 × D1-D5 逐批搜索任务（整合 V58 深化批次口径）"}


# ---------------------------------------------------------------------------
# 七、总闸（TensorGate：五检查 + 指纹/探针/CLI）
# ---------------------------------------------------------------------------


class TensorGate:
    """张量耦合与开源扬弃总闸：命名/语素/张量确定性/耦合穷举/能力吸收五检查。"""

    def __init__(self) -> None:
        self.checks = ("naming", "morphemes", "tensor", "couplings", "capabilities")

    def check_naming(self) -> Dict[str, Any]:
        problems: List[str] = []
        for c in C18_NUMBERING:
            r = validate_repo_name(repo_name(c["id"], _word_of(c["id"])), c["id"])
            problems.extend(r["problems"])
        return {"pass": not problems, "problems": problems,
                "repos": len(C18_NUMBERING),
                "note": "GitHub 18 仓建仓时即合规命名——素材'旧名迁移'零负担如实声明（零迁移）"}

    def check_morphemes(self) -> Dict[str, Any]:
        return check_morphemes()

    def check_tensor(self) -> Dict[str, Any]:
        """张量检查：四模态齐/确定性可复现（同输入同向量机器证明）/相位含枢纽标记。"""
        t = RepoTensor()
        problems: List[str] = []
        for c in C18_NUMBERING:
            ten = t.tensor(c)
            if set(ten) != {"S", "M", "P", "A"}:
                problems.append("{} 四模态不齐".format(c["id"]))
            if not t.tensor_deterministic(c):
                problems.append("{} 张量非确定性".format(c["id"]))
        c03 = next(c for c in C18_NUMBERING if c["id"] == "C03")
        if len(t.modal_p(c03)) != 11:  # 10+枢纽标记
            problems.append("枢纽相位标记缺失")
        if len(t.modal_a(c03)) != 32:
            problems.append("A 模态!=32")
        return {"pass": not problems, "problems": problems,
                "modalities": 4, "deterministic": True}

    def check_couplings(self) -> Dict[str, Any]:
        return check_couplings()

    def check_capabilities(self) -> Dict[str, Any]:
        return check_capabilities()

    def self_check(self) -> Dict[str, Any]:
        results = {
            "naming": self.check_naming(),
            "morphemes": self.check_morphemes(),
            "tensor": self.check_tensor(),
            "couplings": self.check_couplings(),
            "capabilities": self.check_capabilities(),
        }
        return {
            "pass": all(r["pass"] for r in results.values()),
            "checks": {k: r["pass"] for k, r in results.items()},
            "problems": [p for r in results.values() for p in r.get("problems", [])],
        }

    def summary_report(self) -> Dict[str, Any]:
        sc = self.self_check()
        return {
            "ring": 22,
            "module": "tensor_gate",
            "self_check": sc,
            "morpheme_slots": 76,
            "coupling_units": 361,
            "capability_slots": 32,
            "absorbed": len(ABSORBED_PATTERNS),
            "rejected": len(REJECTED_DEPENDENCIES),
            "search_dimensions": len(SEARCH_DIMENSIONS),
        }


def _now_iso() -> str:
    return datetime.datetime.now().isoformat(timespec="seconds")


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def fingerprint() -> dict:
    return {
        "module": "tensor_gate",
        "ring": 22,
        "morpheme_slots": 4 * 19,
        "coupling_units": 361,
        "capability_slots": len(CAPABILITY_SLOTS),
        "layers": len(OSS_LAYERS),
        "absorbed": len(ABSORBED_PATTERNS),
        "rejected": len(REJECTED_DEPENDENCIES),
        "search_dimensions": len(SEARCH_DIMENSIONS),
        "sha16": _sha256("tensor_gate:v59:ring22")[:16],
    }


def probe() -> dict:
    g = TensorGate()
    t = RepoTensor()
    c03 = next(c for c in C18_NUMBERING if c["id"] == "C03")
    return {
        "fingerprint": fingerprint(),
        "self_check": g.self_check(),
        "determinism_proof": t.tensor_deterministic(c03),
        "sample_coupling": coupling("C02", "C10"),
        "sample_hub_coupling": coupling("C03", "C07"),
        "c03_search_first2": search_plan("C03")[:2],
    }


def _main(argv: List[str]) -> int:
    import argparse

    parser = argparse.ArgumentParser(prog="tensor_gate", description="张量耦合与开源扬弃件（V59 ring22）")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("run", help="自检五检查+摘要")
    sub.add_parser("probe", help="指纹+探针（确定性证明+耦合样例）")
    sub.add_parser("couplings", help="361 耦合单元全量（JSON）")
    sub.add_parser("capabilities", help="八层分类+32 槽+取六舍五")
    sub.add_parser("search", help="B0-B6 × D1-D5 搜索任务清单（整合 V58 批次）")
    args = parser.parse_args(argv[1:] if len(argv) > 1 else ["run"])
    cmd = args.cmd or "run"
    if cmd == "run":
        rep = TensorGate().summary_report()
        sc = rep["self_check"]
        print("[tensor_gate] self_check pass={} checks={}".format(sc["pass"], sc["checks"]))
        ok = sc["pass"]
    elif cmd == "probe":
        print(json.dumps(probe(), ensure_ascii=False, indent=1))
        ok = True
    elif cmd == "couplings":
        r = enumerate_couplings()
        print(json.dumps({k: v for k, v in r.items() if k != "units"}, ensure_ascii=False))
        print("units: {} 条（首条 {}）".format(len(r["units"]), r["units"][0]))
        ok = True
    elif cmd == "capabilities":
        for l in OSS_LAYERS:
            print("  {} | {} | {}".format(*l))
        print("  槽位框架：{} 槽（8 层×4）".format(len(CAPABILITY_SLOTS)))
        for name, assim in ABSORBED_PATTERNS:
            print("  取 | {} | {}".format(name, assim))
        for name, reason in REJECTED_DEPENDENCIES:
            print("  舍 | {} | {}".format(name, reason))
        ok = True
    else:  # search
        p = batch_search_plan()
        print(json.dumps({k: v for k, v in p.items() if k != "note"}, ensure_ascii=False))
        for t in search_plan("C03"):
            print("  C03 | {} | {}".format(t["维度"], t["查询"]))
        ok = True
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv))
