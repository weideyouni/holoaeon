# 更新日志

本项目遵循 [Keep a Changelog](https://keepachangelog.com/) 格式，
并遵循语义化版本（Semantic Versioning）。

## [0.4.0] - 2026-10-30

### 新增

- **SD-Distill 亚学科辅助蒸馏扩展包**（`holoaeon/packs/subdistill_pack.py`），第十一个包，
  经 `EXTRA_PACK_REGISTRY` 挂载（不进 `PACK_ORDER`）：
  - 16 宏观域下切 **127 亚学科**，随包提供 `data/taxonomy_127.json`（127 项编码 + 术语种子）；
  - 15 个技能：分类 3（`taxonomy_encode / nearest / far_pairs`）+ 教师卡 1 + 七阶段 5 可见阶段技能
    （`s1_acquire / s2_parse / s3_concept / s4_relate / s5_align / s6_distill / s7_commit`）
    + 七项损失 1 + 温度课程 1 + 反标签 1 + SKC 校验 1；
  - 7 条工作流：`S1_acquire → S2_parse → S3_concept → S4_relate → S5_align → S6_distill → S7_commit`；
  - 0 个角色：`roles = []`，不新增 agent。
- **维度不变式**：`127 × 10 + 61 = 1331` 行、`127 × 855 + 56 = 108641` 节点，写进
  `pack_summary()` 并在 `G19` 中断言；母体 12 项锁数一个不动。
- **安全闸门**：MED / TCM 产物强制 `skin.medical_disclaimer` 与免责声明；`analogizes`
  关系必须带反例；禁用断言 `诊断 / 处方 / 疗效承诺` 由 `skc_validate` 拦截。
- **系统型说明文档** `SYSTEM_README.md`：描述"内核 + 两个扩展包"的系统边界、维度不变式、
  冷热插拔契约、验证矩阵与版本纪律。

### 变更

- `spec.py`：`VERSION 0.3.1 → 0.4.0`，`MATRIX_ID / RUNTIME_ID` 同步为 `0.4.0`。
- `packs/__init__.py`：`EXTRA_PACK_REGISTRY` 增加 `subdistill`，`EXTRA_PACK_ORDER`
  变为 `["sovereignty", "subdistill"]`。
- `selftest.py`：G18 改为只对 `sovereignty` 包计数（避免扩展包数量增长打穿 `17/0/5` 断言），
  新增 `G19 subdistill`（17 条断言）。
- `README.md` / `README.zh-CN.md`：新增"横切扩展包（第十、第十一包）"章节，自检口径更新为 19/19。

### 质量保障

- 自检套件扩展为 **G1–G19（19/19 通过）**；
- 单元测试保持 25 个（全部通过）；
- 红线扫描保持零违规；
- 发行包解压复跑：19/19 通过，`taxonomy_loaded=True`、`items=127`。

## [0.3.1] - 2026-10-30

### 新增

- **认知主权扩展包**（`holoaeon/packs/sovereignty_pack.py`），第十个包，经
  `EXTRA_PACK_REGISTRY` 挂载（不进 `PACK_ORDER`）：
  - 17 个技能 = 17 条认知主权通道（`SO-01…SO-17`）；
  - 5 条工作流：`R0_encoding / R1_forging / R2_strategy / R3_interop / R4_compliance`；
  - 0 个角色；平台侧指标一律 `pending_human_measure`，执行列恒为 `human_manual`。

### 质量保障

- 自检套件扩展为 G1–G18（18/18 通过），新增 `G18 sovereignty`（6 条断言）；
- 红线扫描保持零违规；九包核心 `25 agents / 47 skills` 断言未被破坏。

## [0.3.0] - 2026-10-29

### 新增

- **高译（GaoYi）领域包**（`holoaeon/packs/gaoyi_pack.py`），第九个领域包，全域加载
  - 编译器：自然语言按确定性关键词计分（长度加权、同分取表序）匹配意图，编译为自定义汇编 HASM；
  - 汇编器：HASM 文本可反汇编回读，注释剥离正确处理引号内的 `;/#`；
  - 虚拟机：GaoyiVm 逐条执行 HASM，`.submit` 时调用内核，目标 agent 不在场时自动安装全部包；
  - 意图表覆盖全部 8 个既有包的 44 个技能；
  - 新增 1 个角色（gaoyi_translator）、3 个技能（gaoyi_compile/gaoyi_run/gaoyi_exec）、1 个工作流（gaoyi_pipeline）；
  - 全量安装后规模：25 个智能体、47 个技能、9 个工作流。

### 诚实性

- HASM 为本项目自定义指令集，**非真实 CPU 汇编**；
- 识别失败如实报 `UNKNOWN`，不猜测。

### 质量保障

- 自检套件扩展为 G1–G17（17/17 通过），新增高译编译/执行/UNKNOWN/往返专项；
- 单元测试扩展为 25 个（全部通过）；
- 红线扫描保持零违规。

## [0.2.0] - 2026-10-29

### 新增

- **优化与自组织搜索能力层**（`holoaeon/packs/optimization.py`，详见 [ALGORITHM.md](ALGORITHM.md)）
  - 黄金分割法（区间消去）；
  - 梯度下降（中心差分数值梯度）；
  - 牛顿法（二阶曲率加速）；
  - 共轭梯度法（求解对称正定方程组，正确实现 A-共轭）；
  - 表格单纯形法（线性规划顶点游走）；
  - 惩罚函数法（约束二次惩罚，步长随 μ 自适应）；
  - 遗传算法（选择/交叉/变异，固定种子确定性）。
- **第八个领域包 optimization**
  - 新增 3 个角色（line_searcher/gradient_solver/global_solver）、7 个技能、1 个工作流；
  - 全量安装后规模：24 个智能体、44 个技能、8 个工作流。
- **本地启动器**（`scripts/launch_local.py`）
  - 冷/热插拔、内部融合协议、外部融合协议；
  - 子命令 status/demo/run/hotplug/selftest。

### 修正

- 明确**共轭 ≠ 正交**：共轭方向相对矩阵 A 定义（p_iᵀ A p_j=0）；
- 不采用"靠皮肤分割获得凸性"的说法（凸性是目标函数本身的性质）。

### 质量保障

- 自检套件扩展为 G1–G16（16/16 通过）；
- 单元测试扩展为 24 个（全部通过）；
- 红线扫描保持零违规。

## [0.1.0] - 2026-10-29

### 新增

- **核心原语**
  - `Envelope`：统一消息信封，支持 create/broadcast/reply/forward 与字典往返；
  - `Bus`：线程安全总线，支持发布订阅、直接寻址与路由；
  - `Skill` / `SkillRegistry`：技能清单、注册与自然语言匹配；
  - `Memory`：三层记忆（working/longterm/archive），支持巩固、衰减与持久化；
  - `Agent`：智能体原语，签名感知的技能调用与参数类型转换。
- **核心机制**
  - `Scheduler`：心跳调度器（70 体、768 维、α=0.18）；
  - `Guard`：L1–L8 安全边界，危险模式与权限检查；
  - `Kernel`：顶层门面，支持 submit/collab/choose_agent/health；
  - `AdaptiveGraph`：六边形协作图，Dijkstra、瓶颈、赫布学习、自组织、根因；
  - `Cluster`：并行 Actor 集群，支持屏障同步与转发；
  - `HypervectorSpace`：HRR 超向量与手写 radix-2 FFT；
  - `ModelAdapter`：任意模型适配层，8 路由策略、10 消息格式、8 用量指标。
- **七大领域包**
  - writing / literature / research / data / growth / business / quant；
  - 合计 21 个智能体、37 个技能、7 个工作流。
- **质量保障**
  - 自检套件 G1–G15（15/15 通过）；
  - 单元测试 17 个（全部通过）；
  - 基于 AST 的红线扫描器（零违规）。
- **文档**
  - 中英文 README；
  - docs 架构与各机制文档；
  - CONTRIBUTING / CODE_OF_CONDUCT / CHANGELOG。

### 设计原则

- 零第三方依赖、纯标准库；
- 全离线、确定性、可复现（DIFF=0）；
- 逻辑稀疏拓扑，构造时不预分配；
- 机制正交、模型无关；
- 生物/宇宙词汇仅作隐喻。
