# -*- coding: utf-8 -*-
"""
HoloAeon —— 通用多智能体认知内核的规格与配置
================================================================================
HoloAeon 把"任意任务"组织成一张【逻辑协作矩阵】，并把它投影为一张【自适应协作图】，
由一个统一的节拍（scheduler tick）驱动，由边界守卫（guard）守护，由内核（kernel）装配。

设计原则（与早期"垂直业务母体"的关键区别）：
  1. 规模是【参数】，不是魔法数字。rows/cols/capacity 都可配置，默认值仅因谱系而保留。
  2. 矩阵是【逻辑拓扑】，默认稀疏实例化——构造时绝不预分配 rows×cols 个对象。
  3. 引擎通用、领域知识以"领域包(packs)"注入；本文件不含任何特定业务术语。
  4. 纯标准库、零第三方依赖、确定性可复现（同序列重放结果一致）。

术语对照（生物隐喻 → 工程概念，详见 docs/concepts.md）：
  全息心跳   → Scheduler（时钟/调度）
  皮肤       → Guard（守卫/策略边界）
  经络       → Router（消息路由）
  语义通信座 → Envelope + Bus + Skill manifest
  细胞骨架   → Kernel + Memory（内核/存储）
  赫布协作场 → AdaptiveGraph（自适应协作图）
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple

# ============================================================ 身份
PKG_NAME = "holoaeon"
PACKAGE_NAME = PKG_NAME
VERSION = "0.9.1"
MATRIX_ID = "HOLOAEON-MATRIX-0.9.1"
RUNTIME_ID = "HOLOAEON-RUNTIME-0.9.1"
PROTOCOL_ID = "HOLOAEON-DATAPROTO v1.0"
BUS_ID = "HOLOAEON-BUS-v1.0"
DATE = "2026-10-30"

# 门禁令牌（本地边界演示用；非安全密钥，不应在真实部署中当作鉴权）
GATE_OPEN = "holoaeon-gate-open"
GATE_CLOSE = "holoaeon-gate-close"

# 所有运行回执的模式标记：simulated 表示本地确定性仿真，不代表真实外部作用已发生
MODE_SIMULATED = "simulated"
MODE_LIVE = "live"

# 内核能力（横切，正交）；数量与名称用于健康自检
CAPABILITIES = (
    ("C1", "envelope", "统一信封 / 消息原语"),
    ("C2", "bus", "发布/订阅/路由消息总线"),
    ("C3", "agent", "智能体原语（role + inbox + step）"),
    ("C4", "skill", "技能契约与注册"),
    ("C5", "memory", "记忆存储与持久化"),
    ("C6", "scheduler", "时钟/节拍（健康检查+快照）"),
    ("C7", "guard", "守卫/策略边界"),
    ("C8", "kernel", "内核（生命周期/装配/恢复）"),
    ("C9", "graph", "自适应协作图（投影/路由/根因）"),
    ("C10", "cluster", "多线程 Actor 邮箱集群"),
    ("C11", "hypervector", "VSA/HDC 超维表示（可选）"),
    ("C12", "model_adapter", "模型适配（任意 Agent 用任意模型，可选）"),
)
CAPABILITY_COUNT = len(CAPABILITIES)

# 七大基础通用业务包（领域知识以数据/配置注入，引擎不绑定）。
# 另有两个横切扩展包：optimization（优化求解）、gaoyi（高译），合计九大领域包（见 packs/__init__.py）。
DOMAIN_PACKS = (
    ("writing", "文字创作", "小说/文案/剧本/新媒体/打磨"),
    ("literature", "文献梳理", "检索/筛选/综述/引用图谱/溯源"),
    ("research", "科研", "假设/实验设计/分析/论文/复现"),
    ("data", "数据处理", "清洗/分析/可视化/报表/管线"),
    ("growth", "个人成长", "目标/习惯/学习/复盘/健康"),
    ("business", "企业运营", "流程/管理/运营/协同/决策"),
    ("quant", "量化分析", "指标/建模/回测/风险/归因"),
)
DOMAIN_PACK_COUNT = len(DOMAIN_PACKS)


# ============================================================ 配置数据类
@dataclass
class MatrixConfig:
    """逻辑协作矩阵（不预分配；稀疏实例化）。

    rows: 角色/能力簇/语义域/智能体族群；
    cols: 上下文窗口/记忆槽位/语义通道/推理阶段；
    单元 (r,c) 是一个可被激活的逻辑节点，未激活即不存在。
    """
    rows: int = 1331
    cols: int = 1331
    sparse: bool = True
    node_capacity: int = 108641     # 逻辑节点容量（可配置；默认值因谱系保留）

    @property
    def design_grid(self) -> int:
        """设计网格大小（仅用于容量/自洽说明，从不实际分配）。"""
        return self.rows * self.cols


@dataclass
class SchedulerConfig:
    """时钟/节拍（原"全息心跳"）。"""
    tick_interval_ms: int = 500
    sync_mode: str = "adaptive"          # fixed | adaptive
    snapshot_enabled: bool = True
    body_count: int = 70                 # 健康体数量
    id_base: int = 8700                  # 号段基（id_base .. id_base+body_count-1）
    state_dim: int = 768                 # 状态向量维度
    alpha: float = 0.18                  # 指数平滑系数

    @property
    def id_top(self) -> int:
        return self.id_base + self.body_count - 1


@dataclass
class GuardConfig:
    """守卫/策略边界（原"皮肤"）。"""
    layers: int = 8                      # L1-L8 串联守卫
    default_action: str = "block"        # allow | advise | block
    audit_enabled: bool = True
    # 输入校验：越权 / 失真双轨（对应早期 E14/E13，名称中性化）
    block_unauthorized: bool = True
    block_garbled: bool = True


@dataclass
class AdaptiveGraphConfig:
    """自适应协作图（原"赫布协作场"）。"""
    node_count: int = 17                 # 图节点（= 通道数）
    learning_rate: float = 0.12
    decay: float = 0.99
    clip: float = 1.0
    geometry_radius: int = 2             # 六边形邻域半径（radius=2 → 19 圆）
    congestion_threshold: float = 0.5
    block_threshold: float = 0.8


@dataclass
class HypervectorConfig:
    """VSA/HDC 超维表示（可选）。"""
    dim: int = 1024
    enabled: bool = True
    # HRR 圆周卷积（Cooley-Tukey FFT，dim 取 2 的幂）；permutation 为循环移位
    binding: str = "hrr"                 # hrr | permutation


@dataclass
class ModelAdapterConfig:
    """模型适配（横切，可选；登记式，不启动网关/不连真实供应商）。"""
    enabled: bool = True
    gateway_host: str = "127.0.0.1"
    gateway_port: int = 3425
    route_strategies: int = 8
    masking_types: int = 10
    usage_metrics: int = 8


@dataclass
class HoloAeonConfig:
    """顶层配置聚合。一切规模参数都可在构造时覆盖。"""
    matrix: MatrixConfig = field(default_factory=MatrixConfig)
    scheduler: SchedulerConfig = field(default_factory=SchedulerConfig)
    guard: GuardConfig = field(default_factory=GuardConfig)
    graph: AdaptiveGraphConfig = field(default_factory=AdaptiveGraphConfig)
    hypervector: HypervectorConfig = field(default_factory=HypervectorConfig)
    model_adapter: ModelAdapterConfig = field(default_factory=ModelAdapterConfig)
    domain: str = "generic"               # generic | writing | literature | ...
    deterministic: bool = True

    def with_domain(self, domain: str) -> "HoloAeonConfig":
        self.domain = domain
        return self


# 默认配置（单例式便捷入口）
DEFAULT_CONFIG = HoloAeonConfig()


# ============================================================ 自洽校验
def config_verify(cfg: HoloAeonConfig = DEFAULT_CONFIG) -> bool:
    """配置自洽校验：任何一处不符即失败（不依赖外部环境）。"""
    m, s, g, gr = cfg.matrix, cfg.scheduler, cfg.guard, cfg.graph
    hv, ma = cfg.hypervector, cfg.model_adapter
    checks = [
        # 逻辑矩阵规模为正，稀疏默认开启
        m.rows > 0 and m.cols > 0 and m.node_capacity > 0,
        m.design_grid == m.rows * m.cols,
        m.sparse is True,
        # 健康体号段自洽
        s.body_count > 0 and s.id_top == s.id_base + s.body_count - 1,
        s.state_dim > 0 and 0.0 < s.alpha < 1.0,
        s.sync_mode in ("fixed", "adaptive"),
        # 守卫
        g.layers > 0 and g.default_action in ("allow", "advise", "block"),
        # 自适应图
        gr.node_count > 0 and 0.0 < gr.learning_rate and 0.0 < gr.decay <= 1.0,
        0.0 <= gr.congestion_threshold <= gr.block_threshold <= 1.0,
        # 超维
        hv.dim > 0 and hv.binding in ("hrr", "permutation"),
        # 模型适配
        ma.gateway_port > 0 and ma.route_strategies > 0,
        # 能力清单与领域包数量
        CAPABILITY_COUNT == 12,
        DOMAIN_PACK_COUNT == 7,
        cfg.deterministic is True,
    ]
    return all(checks)


def lock_check(cfg: HoloAeonConfig = DEFAULT_CONFIG) -> dict:
    """返回关键规模参数（逻辑值，非实际分配）。"""
    return {
        "pkg": PKG_NAME,
        "version": VERSION,
        "matrix_rows": cfg.matrix.rows,
        "matrix_cols": cfg.matrix.cols,
        "design_grid": cfg.matrix.design_grid,
        "node_capacity": cfg.matrix.node_capacity,
        "sparse": cfg.matrix.sparse,
        "scheduler_bodies": cfg.scheduler.body_count,
        "scheduler_id_range": [cfg.scheduler.id_base, cfg.scheduler.id_top],
        "state_dim": cfg.scheduler.state_dim,
        "guard_layers": cfg.guard.layers,
        "graph_nodes": cfg.graph.node_count,
        "hv_dim": cfg.hypervector.dim,
        "capabilities": CAPABILITY_COUNT,
        "domain_packs": DOMAIN_PACK_COUNT,
        "domain": cfg.domain,
    }


if __name__ == "__main__":
    assert config_verify(), "HoloAeon 配置自洽校验失败"
    print("HoloAeon spec 自洽通过：", MATRIX_ID, PROTOCOL_ID, "deterministic=true")
    print("默认规模（逻辑/稀疏，不预分配）：", lock_check())
