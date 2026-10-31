# -*- coding: utf-8 -*-
"""
persona_quartet_pack —— 四人全维度数字分身（Persona Quartet）
================================================================================
定位：HoloAeon 的第 17 个横切扩展包（EXTRA_PACK，不进 PACK_ORDER，不改 G15 计数）。
四位主体：探微(P1) / 筑基(P2) / 构弦(P3)
         / 持衡(P4)。
内容：蒸馏版七维度知识目录（公开论文/访谈/项目档案/行业史料 → 公开资料归因转述），
四技能：persona_view（单分身）/ persona_roundtable（四人圆桌）/ persona_compare
（维度横向对比）/ persona_mission（任务模拟打分）。
诚实性声明：本包为确定性知识工具，全部内容为公开资料归因仿真转述，不代表原型人物实时
观点，不能替代真人决策，不提供临床诊疗/用药/投资依据；所有推演结果需人类专家终审。
仿真≠证明；碳基终裁。纯标准库、零依赖、离线可跑。
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from .base import DomainPack, RoleSpec, SkillSpec, WorkflowSpec

PERSONA_QUARTET_ID = "SG-PERSON-QUARTET-1331x1331-SUPER-MAS-V3.0"
ATTRIBUTION_NOTE = "公开资料归因仿真转述，不代表原型人物实时观点；需人类专家终审；仿真≠证明"

DIMS = ("基础画像", "业务能力", "学科架构", "核心学术观点", "技术路径谱系", "落地场景", "约束边界")

# 蒸馏目录：四主体 × 七维度（每维 2-3 条；观点自带归因标记）
CATALOG: Tuple[Dict[str, Any], ...] = (
    {
        "id": "P1", "name": "探微(P1)",
        "role": "DeepMind创始人/Alphabet首席科学家/2024诺贝尔化学奖（AlphaFold）",
        DIMS[0]: ["国际象棋神童；剑桥计算机科学；UCL认知神经科学PhD",
                 "DeepMind 2010创立，2014被谷歌收购；Isomorphic Labs负责人"],
        DIMS[1]: ["前沿AI实验室顶层战略与跨学科科研团队组织",
                 "RL+科学发现大项目从0到1统筹(AlphaGo/AlphaFold)",
                 "AGI长期方向研判；AI+生命科学跨界落地"],
        DIMS[2]: ["计算机科学+认知神经科学+博弈论+分子生物学/生物物理+游戏设计理论",
                 "底层认知记忆/想象力神经机制；AI层深度强化学习/自博弈/MCTS/多模态",
                 "科学计算层蛋白质构象/生物大分子/基因组建模/AI for Science"],
        DIMS[3]: ["AGI需具备自主提出科学假设的能力（归因：公开表述）",
                 "持续学习/长期记忆/内省推理为核心，强化学习价值被低估（归因：公开访谈）",
                 "AI是生物学极佳描述语言；数字生物学革命缩短药物研发周期（归因：公开论文/演讲）",
                 "游戏是天然智能训练沙盘（归因：公开演讲）"],
        DIMS[4]: ["DQN Atari端到端 → AlphaGo/MCTS+自博弈 → AlphaZero无人类数据",
                 "AlphaFold进化信息+注意力+结构先验 → 蛋白质组/基因组建模",
                 "Gemini多模态；Isomorphic Labs新药分子发现"],
        DIMS[5]: ["蛋白质结构数据库/致病机理/新药靶点筛选/抗生素研发",
                 "科学猜想生成/模拟实验/计算生物学；复杂规划与战略推演"],
        DIMS[6]: ["仿真仅做思路推演，不提供临床诊疗/用药建议；需人类专家终审"],
    },
    {
        "id": "P2", "name": "筑基(P2)",
        "role": "谷歌元老/Google Brain联合创始人/TensorFlow·TPU·MapReduce/Bigtable/Spanner核心设计者/Discovery Loop创办人",
        DIMS[0]: ["明尼苏达大学、华盛顿大学；早年参与HIV流行病学建模",
                 "谷歌27年，构建分布式计算基础设施与机器学习工程底座"],
        DIMS[1]: ["超大规模分布式系统架构与云计算基础设施",
                 "机器学习框架/专用AI算力TPU工程落地；算力调度与能耗效率",
                 "自动化科学发现全流程平台设计"],
        DIMS[2]: ["分布式系统&OS+计算机体系结构+机器学习工程+大规模数据处理+科学计算自动化",
                 "并行计算/分布式存储/容错/芯片软硬协同；张量计算/大规模训练集群"],
        DIMS[3]: ["Scaling Hypothesis：算力数据模型规模提升智能能力（归因：公开技术报告）",
                 "向量空间语义表示：语义可在向量空间运算（归因：公开论文/演讲）",
                 "AI基础设施是通用智能基石；软硬协同同等重要（归因：公开访谈）",
                 "自动化科学发现与可持续计算（归因：公开项目/访谈）"],
        DIMS[4]: ["MapReduce/GFS/BigTable/Spanner → Google Brain/TensorFlow",
                 "TPU专用张量处理器软硬协同 → Gemini工程体系",
                 "Discovery Loop闭环自动化科研：假设-实验-分析迭代"],
        DIMS[5]: ["云计算/大数据平台/分布式存储计算；AI算力集群与训练平台",
                 "芯片-软件协同/算力调度/能耗优化；自动化科研实验室"],
        DIMS[6]: ["偏工程-系统视角；前沿生物方向非其主攻领域；需人类专家终审"],
    },
    {
        "id": "P3", "name": "构弦(P3)",
        "role": "Google DeepMind高级副总裁/首席AI架构师；DQN/AlphaGo/WaveNet/BYOL/Gemini核心作者之一",
        DIMS[0]: ["航空工程本科+硕士；NYU计算机科学PhD(深度学习实验室)",
                 "2012年加入DeepMind；DeepMind日常运营负责人"],
        DIMS[1]: ["多赛道模型并行迭代(Gemini Flash/Pro)；深度学习架构/视觉表征/RL/多模态工程实现",
                 "自监督表示学习/语音生成(WaveNet)/空间变换网络",
                 "模型产品化交付/开发者接口/多模态落地部署"],
        DIMS[2]: ["深度学习(CNN/表征学习)+强化学习+多模态感知+信号处理+航空工程系统思维",
                 "底层无监督/自监督特征提取/稀疏编码/视觉层级表示",
                 "统一多模态：文本-图像-音频-视频共用一套底层模型架构"],
        DIMS[3]: ["多模态是通用智能底层必需架构，统一联合训练而非单模态拼接（归因：公开论文/访谈）",
                 "深度学习原理延续：DQN到Gemini损失/优化/RL一脉相承（归因：公开技术演讲）",
                 "并行多版本迭代策略：Flash快速迭代+Pro前沿能力（归因：公开产品发布口径）",
                 "BYOL自监督无负样本学习表征，减少标注依赖（归因：公开论文）"],
        DIMS[4]: ["PSD稀疏分解/层级卷积特征 → DQN/WaveNet → BYOL自监督",
                 "Gemini原生多模态：统一tokenizer/跨模态训练损失",
                 "多分支模型工程迭代，平衡推理速度/成本/能力"],
        DIMS[5]: ["原生多模态大模型产品/开发者API/多模态文档解析",
                 "语音合成/音频生成；RL智能体/机器人感知决策；科学图像解析"],
        DIMS[6]: ["侧重模型架构与工程执行；需人类专家终审"],
    },
    {
        "id": "P4", "name": "持衡(P4)",
        "role": "AlexNet/Seq2Seq共同发明者；OpenAI联合创始人/前首席科学家；Safe Superintelligence(SSI)创始人",
        DIMS[0]: ["多伦多大学；深度学习先驱门下；Google Brain时期完成Seq2Seq",
                 "主导GPT-3/GPT-4研发与超对齐(Superalignment)项目"],
        DIMS[1]: ["神经网络架构创新/序列建模/自回归大模型路线设计",
                 "超级智能安全对齐/超对齐理论；前沿AGI安全风险分析",
                 "基础大模型预训练路线/推理能力建模"],
        DIMS[2]: ["深度神经网络+序列建模+自然语言表示学习+AGI安全/对齐理论+认知计算",
                 "底层CNN/循环序列模型/编解码架构；自回归Transformer/预训练-微调/思维推理",
                 "安全域：超级智能对齐/奖励建模/监督与可控制理论"],
        DIMS[3]: ["自回归序列模型具备极强通用推理潜力；缩放可涌现复杂能力（归因：公开论文/访谈）",
                 "超级智能安全优先：对齐必须跑在能力前面（归因：公开访谈/项目声明）",
                 "超对齐：解决人类难以直接监督超人类智能的可扩展对齐方法（归因：公开项目声明）",
                 "神经网络可学习世界的隐式模型（归因：公开访谈）"],
        DIMS[4]: ["AlexNet → Seq2Seq编解码 → GPT-2→GPT-3→GPT-4 自回归路线",
                 "超对齐项目 → SSI安全超级智能实验室（单一目标）"],
        DIMS[5]: ["大语言模型/代码生成/机器翻译/复杂推理",
                 "AGI安全评估/对齐测试平台/风险推演仿真；安全协议设计"],
        DIMS[6]: ["重点大模型架构+AGI安全；不代表SSI内部未公开技术细节；需人类专家终审"],
    },
)


def _shingles(text: str) -> set:
    out: set = set()
    for t in [x for x in text.replace("，", ",").split(",") if x]:
        for n in (2, 3, 4):
            for i in range(max(0, len(t) - n + 1)):
                out.add(t[i:i + n])
    return out


def _overlap(text: str, items: List[str]) -> int:
    sh = _shingles(text)
    return sum(1 for it in items if any(s in it for s in sh))


def _view(persona_id: str) -> dict:
    for p in CATALOG:
        if p["id"] == persona_id:
            return {"id": p["id"], "name": p["name"], "role": p["role"],
                    "dimensions": {d: p[d] for d in DIMS},
                    "attribution_note": ATTRIBUTION_NOTE}
    return {"error": f"未知分身 {persona_id}；可选 {[p['id'] for p in CATALOG]}"}


# ============================================================ 技能函数
def persona_view(persona: str) -> dict:
    """单分身七维度视图（公开资料归因转述）。"""
    return _view(persona)


def persona_roundtable(topic: str) -> dict:
    """四人圆桌：每人 2 条相关观点（归因对比，非真人对话）。"""
    t = topic or "通用智能路线"
    rows = []
    for p in CATALOG:
        opinions = p[DIMS[3]]
        scored = sorted(opinions, key=lambda o: _overlap(t, [o]), reverse=True)
        rows.append({"persona": p["id"], "name": p["name"],
                     "opinions": scored[:2]})
    return {"topic": t, "rows": rows, "attribution_note": ATTRIBUTION_NOTE}


def persona_compare(dimension: str) -> dict:
    """维度横向对比：跨四人同维度条目。"""
    dim = dimension or DIMS[3]
    if dim not in DIMS:
        return {"error": f"未知维度 {dim}；可选 {list(DIMS)}"}
    return {"dimension": dim,
            "rows": [{"persona": p["id"], "name": p["name"], "items": p[dim]}
                     for p in CATALOG],
            "attribution_note": ATTRIBUTION_NOTE}


def persona_mission(task: str) -> dict:
    """任务模拟：四位分身方案按任务相关度排序（确定性打分）。"""
    t = task or "AGI安全与多模态融合方案"
    scored = []
    for p in CATALOG:
        items = p[DIMS[4]] + p[DIMS[3]]
        scored.append({"persona": p["id"], "name": p["name"],
                       "overlap": _overlap(t, items),
                       "path": p[DIMS[4]]})
    scored.sort(key=lambda x: (-x["overlap"], x["persona"]))
    return {"task": t, "rank": scored, "attribution_note": ATTRIBUTION_NOTE}


# ============================================================ 领域包
class PersonaQuartetPack(DomainPack):
    """四人全维度数字分身包：蒸馏目录 + 四技能 + 四角色 + 圆桌工作流。"""
    key = "persona_quartet"
    name = "四人全维度数字分身"
    description = ("四位AI人物（探微/筑基/构弦/持衡）七维度知识目录与确定性推演；"
                   "公开资料归因仿真，不代表原型人物实时观点，需人类专家终审。")

    def __init__(self) -> None:
        self.skills = [
            SkillSpec("persona_quartet.persona_view", persona_view, "单分身七维度视图",
                      ["分身", "persona", "探微", "筑基", "构弦", "持衡"],
                      {"persona": "str"}),
            SkillSpec("persona_quartet.persona_roundtable", persona_roundtable, "四人圆桌观点归因对比",
                      ["圆桌", "roundtable", "辩论", "对比推演"],
                      {"topic": "str"}),
            SkillSpec("persona_quartet.persona_compare", persona_compare, "跨四人同维度横向对比",
                      ["对比", "compare", "横向", "维度对比"],
                      {"dimension": "str"}),
            SkillSpec("persona_quartet.persona_mission", persona_mission, "任务模拟：四分身方案排序",
                      ["模拟", "mission", "方案推演", "任务"],
                      {"task": "str"}),
        ]
        self.roles = [
            RoleSpec("p1_agent", "探微分身", ["persona_quartet.persona_view"]),
            RoleSpec("p2_agent", "筑基分身", ["persona_quartet.persona_view"]),
            RoleSpec("p3_agent", "构弦分身", ["persona_quartet.persona_view"]),
            RoleSpec("p4_agent", "持衡分身", ["persona_quartet.persona_view"]),
            RoleSpec("persona_lead", "分身矩阵总控",
                     ["persona_quartet.persona_roundtable",
                      "persona_quartet.persona_compare",
                      "persona_quartet.persona_mission"]),
        ]
        self.workflows = [
            WorkflowSpec("persona_quartet_flow",
                         ["p1_agent", "p2_agent", "p3_agent",
                          "p4_agent", "persona_lead"],
                         "单分身视图→四人圆桌→维度对比→任务模拟（全归因标注，终审）"),
        ]


# 供测试直接调用
def selftest_check() -> Tuple[bool, str]:
    ok = (len(CATALOG) == 4
          and all(set(p.keys()) >= set(DIMS) for p in CATALOG)
          and persona_mission("分布式算力与自动化科研平台")["rank"][0]["persona"] == "P2"
          and "P1" in str(persona_roundtable("数字生物学")["rows"][0]))
    return ok, f"catalog={len(CATALOG)} dims={len(DIMS)}"
