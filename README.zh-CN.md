<div align="center">

# HoloAeon

### 零依赖、生物启发的通用多智能体认知框架

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-green.svg)](https://www.python.org/)
[![Dependencies](https://img.shields.io/badge/dependencies-0-success.svg)](pyproject.toml)
[![Tests](https://img.shields.io/badge/tests-34%20passed-success.svg)](#-测试)
[![SelfTest](https://img.shields.io/badge/selftest-24%2F24-success.svg)](#-测试)

<sub>徽章是**本机实测值**（Python 3.13.16 / Windows）。CI 已写在 `.github/workflows/ci.yml`，但**尚未在 GitHub 上实跑过**——见 [`docs/support-matrix.md`](docs/support-matrix.md)，未跑过的格子一律写 `untested`，不按推测填"通过"。</sub>

[English](README.md) · [中文](README.zh-CN.md)

</div>

---

HoloAeon 是一套**纯标准库、全离线、确定性**的多智能体认知框架，可构建在任意大模型之上。
它自底向上提供一组分层原语——信封、消息总线、智能体、技能、记忆、心跳调度器、安全守卫、
自适应协作图、并行 Actor 集群、超向量表示与模型适配层——并内置**九个开箱即用的领域包**，
覆盖知识工作者的全部日常工作，其中包含一个确定性的**优化与自组织搜索**能力层
（见 [ALGORITHM.md](ALGORITHM.md)）。

> **命名**：*Holo*（整体、全息）+ *Aeon*（诺斯替宇宙观中从至高本源流出的高维永恒生命体）。
> 寓意系统的每个局部都携带整体的部分摘要，结构在不同尺度上自组织涌现。

> **关于生物词汇**："心跳""皮肤""细胞骨架""经络""赫布协作场"等名称均为
> **认知架构隐喻**，用于描述多智能体系统的同步、边界、路由、支撑与自组织机制，并非生物学
> 意义上的器官或医学结构。文末附有精确的[隐喻 → 工程概念映射表](#-隐喻--工程概念映射表)。

---

## 为什么选择 HoloAeon

多数智能体框架直接从高层开始（"给我一组智能体"），却隐藏了最基础的原语。HoloAeon
**自底向上**构建，每个高层机制都是小型、可检视、可测试部件的组合。

| 原则 | 实际含义 |
|---|---|
| **零依赖** | 仅使用 Python 标准库，`pip install` 不安装任何东西，`dependencies = []`。 |
| **默认离线** | 无网络调用、无内置密钥、无遥测，可在物理隔离的机器上运行。 |
| **确定性** | 相同输入产生相同输出，可复现（`DIFF=0`）。 |
| **逻辑、稀疏拓扑** | 大矩阵是*逻辑*坐标空间，构造时绝不预分配，节点稀疏激活。 |
| **正交机制** | 每层职责单一，同步、路由、安全、学习互不重叠。 |
| **模型无关** | 专用适配层让框架可对接任意本地、私有或云端模型。 |

---

## 架构总览

```
┌─────────────────────────────────────────────────────────────┐
│                      应用 / 用户                              │
├─────────────────────────────────────────────────────────────┤
│  领域包  writing · literature · research · data               │
│          growth · business · quant · optimization             │
├─────────────────────────────────────────────────────────────┤
│                        Kernel（门面）                         │
│        submit · collab · choose_agent · tick · health         │
│   冷/热插拔 · 内部融合 · 外部融合                              │
├──────────────┬──────────────────────────────────────────────┤
│  Scheduler   │  Guard（L1–L8）       Memory（三层）           │
│  心跳        │  边界与安全           working / long / archive │
├──────────────┴──────────────────────────────────────────────┤
│            Adaptive Graph（六边形、赫布）                     │
│   最短路 · 瓶颈 · fan-in · 自组织 · 根因 · 环检测              │
├─────────────────────────────────────────────────────────────┤
│    Bus（主题 / 寻址 / 路由）  ·  Envelope                      │
├─────────────────────────────────────────────────────────────┤
│  Agent + Skill Registry      Hypervector Space（HRR）         │
├─────────────────────────────────────────────────────────────┤
│  Actor Cluster（并行）          Model Adapter（任意 LLM）     │
└─────────────────────────────────────────────────────────────┘
```

---

## 核心原语

### `Envelope` —— 统一消息
所有通信都是自包含的信封，含发送者、接收者、主题、负载、元数据、追踪链与 `mode` 标记
（默认为 `simulated`）。支持 `create`、`broadcast`、`reply`、`forward`、访问节点追踪与
字典往返。

### `Bus` —— 消息总线
线程安全的总线，三种投递模式：
- **发布/订阅**——每个主题多个订阅者；
- **直接寻址**——`register_address("id", handler)`；
- **路由**——把某主题的广播改写到指定地址。

处理函数异常会被转成结构化失败回执，不会导致总线崩溃。

### `Skill` 与 `SkillRegistry`
技能是带清单（描述、标签、输入输出）的确定性可调用对象。注册表用 token 重叠与标签权重，
把自然语言请求匹配到技能，并返回排序候选。

### `Memory` —— 三层记忆
| 层 | 角色 |
|---|---|
| `working` | 当前任务上下文，容量小，可在 `consolidate` 时提升 |
| `longterm` | 跨任务知识，带强度与标签 |
| `archive` | 稳定事实与参考资料 |

提供 `put/get/recall`（token 相关）、`consolidate`、`decay` 与 JSON 持久化，线程安全。

### `Agent`
智能体拥有档案、技能注册表与受限技能集。它判断哪个技能匹配请求，以**签名感知的参数绑定**
（按参数名匹配，做 int/float 转换）调用技能，并返回结构化结果。还提供 `suggest`、
`snapshot`、`reply_to`。

---

## 核心机制

### `Scheduler` —— 心跳
周期性同步信号。每个 tick 完成存活检测、上下文刷新、状态快照、一致性校验、权重衰减/增强、
异常节点隔离与重新选举。默认配置为 70 个心跳体、固定号段、768 维状态向量、指数平滑
（α = 0.18），全部可配置。

### `Guard` —— 安全边界（L1–L8）
分层的**语义级**边界控制器。它依据权限、结构合法性与危险模式检测（如 `os.system`、
`eval`、凭证读取）放行或拦截信封。每个决策是带层级与原因的 `Verdict`，并可选写入审计日志。

### `AdaptiveGraph` —— 协作图
智能体放置在**六边形晶格**上（radius=2 密铺产生 19 个位置）。图支持：
- **Dijkstra 最短路**，以先验流边为引导；
- **负载施加、fan-in 与瓶颈检测**；
- **环检测**（六边形密铺天然含环）；
- **赫布步进**——共激活节点强化共享边；
- **自组织**——状态相似的节点生长弱连接；
- **根因分析**——从瓶颈反向追溯最重入边。

### `Cluster` —— 并行 Actor
集群把智能体包装为带邮箱的 Actor，在屏障后并发运行多个任务，报告 `ok`、`faults`、
`consistent`、耗时与逐任务结果。支持一级转发以实现弹性路由。

### `HypervectorSpace` —— 超向量表示
自包含的全息缩减表示（HRR），建立在**手写 radix-2 Cooley–Tukey FFT** 之上（不用 NumPy）。
提供 `make`、`bind`（圆卷积）、`unbind`（近似逆）、`bundle`（相加）、`permute` 与
`cosine` 相似度，适用于快速、鲁棒的联想记忆与类比绑定。

### `ModelAdapter` —— 一个接口对接任意模型
注册模型后端（本地、私有、云端），含成本、上下文窗口、延迟与模态。适配器按 **8 种策略**
（最便宜、最大上下文、最低延迟、模态匹配……）路由，跨 **10 种掩码/消息格式**格式化消息，
并记录 **8 项用量指标**用于成本与容量追踪。

---

## 九大领域包

HoloAeon 内置九个包，覆盖知识工作的全部谱系。全部安装后共 **25 个智能体、47 个技能、
9 个端到端工作流**。

| 包 | 典型能力 | 角色 |
|---|---|---|
| **writing** | 提纲、字数统计、可读性、结构检查 | planner, drafter, editor |
| **literature** | 检索规划、阅读笔记、质量评审 | searcher, reader, reviewer |
| **research** | 研究设计、样本量、假设、分析计划 | designer, executor, analyzer |
| **data** | 清洗、描述统计、画像、报告 | cleaner, analyst, reporter |
| **growth** | SMART 目标、习惯规划、周复盘 | goal coach, habit coach, review coach |
| **business** | 商业模式画布、KPI、单位经济、风险 | strategist, operator, risk manager |
| **quant** | 收益、夏普、回撤、风险指标 | analyst, researcher, risk |
| **optimization** | 黄金分割、梯度下降、牛顿、共轭梯度、单纯形、惩罚、遗传算法 | line searcher, gradient solver, global solver |
| **gaoyi** | 自然语言→HASM 编译、虚拟机执行、汇编回放（确定性意图路由） | gaoyi translator |

每个包都是自包含的 `DomainPack`，可独立安装。优化包只在**内置安全 benchmark** 上运行，
绝不计算任意表达式。完整算法映射见 [ALGORITHM.md](ALGORITHM.md)。**gaoyi（高译）** 包把
自然语言请求确定性编译为本项目自定义的 HASM 汇编并由内置虚拟机执行；HASM 不是真实 CPU
指令集，识别不到的意图如实报 `UNKNOWN`，不猜测。

### 横切扩展包（第十至第十六包）

这些包**故意不进入 `PACK_ORDER`**：只加能力、不加 agent，因此上面九包口径
（25 智能体 / 47 技能）保持不变。通过 `get_extra_pack(key)` 取用，由
G18 / G19 / G20 / G21 / G22 / G23 / G24 单独验证。

| 扩展包 | 新增能力 | 技能 | 角色 | 工作流 |
|---|---|---|---|---|
| **sovereignty** | 反算法认知塑形：16 学科查询锻造、反标签策略、23 协议族、10 平台族 × 13 职责 | 17 | 0 | 5（R0–R4） |
| **subdistill** | SD-Distill 亚学科辅助蒸馏：16 域 → 127 亚学科 → SKC 知识卡、七阶段管线、七项辅助损失、温度课程 | 15 | 0 | 7（S1–S7） |
| **omnilife** | 全域生活主权：衣 / 食 / 住 / 行 / 教 / SaaS 六域，全部锚定 127 亚学科编码；皮肤层折叠诱导话术、经络层本地交接、确定性生活规划器 | 18 | 0 | 6（L1–L6） |
| **omnicore** | 全息纪元认知引擎重写：寻址不变式、纯函数心跳、SKC 蒸馏、赫布更新、皮肤闸门、自我宣告、白皮书结构 | 20 | 0 | 6（M1–M6） |
| **metab** | 代谢层治理：六染色体基因组准入、四问定态、八阶段生命周期、三层授权（fail-closed）、消化道双通道、信任半径、组合白名单、度量红线 | 26 | 0 | 8（T1–T8） |
| **nephron** | 肾单位层 P0（只读观测）：只追加认知账本、窗口构成表、理由码、零侵入钩子、回放（窗口 / 槽位 / 决策输入 / 时间线）、代际指纹、隐私擦除 | 24 | 0 | 7（W1–W7） |
| **uplift** | 补齐短板升级包 U1–U6：排序键全序、纯函数契约、回归口径账、CI 契约、模板/徽章/支持矩阵一致性、A1/A2 实测判定（含变异证明）、字符 n-gram 混合分、宿主桥边界与远程门禁、O-1～O-10 裁决、P1 四判据门禁 | 24 | 0 | 7（W1–W7） |

`subdistill` 保持母矩阵维度**严格不变**，并在代码里断言：

```
127 × 10 亚学科槽位 + 61 保留行   = 1331 行
127 × 855 亚学科节点 + 56 全局协调 = 108641 节点
```

`omnilife` **不新增行、不新增节点**——只是消费同一套 127 编码做生活域锚点，
由 `pack_summary()["addressing_unchanged"]` 断言。它对"软件能在现实世界做什么"划了硬线：

- 比价只是**给本人填写的空台账**（`concurrent_probe=False`、`proxy_switch=False`），
  多端并发探测、代理切换、抓取比价按名字直接拒绝；
- 诱导折叠只输出**平台自带“不感兴趣/屏蔽关键词”处置规则**，不做 DOM 注入（`dom_injection=False`）；
- 跨 SaaS 路由是**本人导出 → 本地归档 → 人工引用**的交接单（`api_calls=0`、`network=False`）；
- 餐单带 `dose_any=False`、`individual_medical_advice=False` 与固定免责声明；
  出行在本人给的权重图上跑最短路，不取实时路况。

`omnicore` 把投喂的"单文件数字生命引擎"重写为普通确定性软件。
**先复现、再修掉投喂代码的 5 处缺陷**（写进 `CORRECTIONS`，由 G21 断言）：
`self._cells = profile` 静默覆盖整张稀疏表；`defaultdict` 上调 `.append`；
空赋值 `route =` 导致 `SyntaxError`；`numpy` + `np.random` 与"零依赖"自相矛盾；
守护线程 + sqlite 落盘 + 不存在的 PyPI 包名。重写保留设计意图、丢掉不可核验部分：

- 心跳是**纯函数** `heartbeat_pulse(epoch)`：无线程、无 sleep、无定时器；
- 快照 `persistence="host_managed"`，本包**不写盘**；
- 5% 温度冲击用 `sha256(epoch) % 100 < 5` 替代随机源，可复现；
- "数字生命 / 呼吸 / 免疫 / 城邦"一律标 `metaphor=True`，实证部分只是确定性软件；
- 对接流媒体/电商推荐位的浏览器插件一律拒绝。

`metab` 把一份治理规格变成**可判定**的检查层，它本身不执行任何摄入动作，
只回答四件事：准不准入、归哪一态、缺什么、凭什么拒绝。26 个技能每一条都给出判定并注明所服务的公理：

- 准入须**六条染色体齐备**（表型 / 纯度 / 血统 / 毒性 / 耗能 / 节律）；
  缺降级路径、缺注意力打扰配额都直接否决；
- 定态用四问、优先级固定；**四问皆不命中时默认取更保守的循环态，绝不默认呼吸态**；
- 规格里 8 处内在冲突逐条列出、每种给两个消解方案并择一落库（`CONFLICTS` K1–K8）：
  不可逆点被推到系统外（K1），"一键禁用"明确为停效并切备用路径而非骨架回滚（K6）；
- 血统是可验的哈希链，篡改节点按位置报告，整链判不可信；
- 组合安全走白名单：**未知配对不生效**，含放大关系的组合须整体评审。

`nephron` 是**只读观测**的肾单位层（P0 阶段）。它记录窗口做过什么——进 / 摘要 / 拒 /
命中 / 未命中 / 检索 / 淘汰 / 降级 / 指纹失配 / 预算越界——并能事后回放任意已记录的 tick。
**它不做任何决策**：不分页、不压缩、不淘汰、不做预算控制。规格里 10 处内在冲突逐条列出、
每种给两个消解方案并择一落库（`CONFLICTS` N1–N10），另有 3 处字段缺口修正（`FIXES` F1–F3）：

- "异步队列 + 批量刷写"**不在包内实现**：包只给队列语义与丢弃计数
  （`dropped_queue_full / failed_write / failed_serialize`），线程与落盘归宿主（N1）；
- `sampled` 与 `off` 档账本**不可完整回放**，只有 `full` 满足"任意历史 tick"（N2）——
  对采样做插值等于伪造账本；
- 擦除把摘要替换为 `ERASED:<hash>` 并**追加一条擦除记录**，隐私与只追加同时成立（N3）；
- `compression_ratio` 在 P0 恒为 `null`（N4）；`UNKNOWN` 是保留码，单独计数并告警，
  绝不静默吞掉（N5）；
- 时钟回跳在写入口**直接拒绝**（N6）；`raw_len` 锁死 token 口径（N8）；
- `WINDOW_BUILD_COMPLETE` 由评审 R-01 新增，给 `window_build` 一个合法码（N9）；
- 槽位回放读**旁挂快照**并披露快照年龄（N10）：P0 **不重演槽位变化**，明说而不假装。

`uplift` 是**加固包**，对象不是新能力，而是 v0.8.0 留下的六个洞。十处规格冲突逐条裁掉
（`CONFLICTS` X1–X10），每处都写明字面为什么要让步：

- 只按 `agent_id` 排序在同一 agent 多记录时仍有并列，故键改为
  `(agent_id, 记录规范化指纹)`，并用纯函数测试证明修复不是安慰剂（X1）；
- 投喂的「6 agent × 30 轮」实测只产出 **6 条**结果（`run()` 只首轮投递任务、`rounds`
  只驱动屏障），所以改的是断言而不是语义（X2）；
- CI 徽章无法在本地挣到：workflow 照交，矩阵写 `untested`，README 明说「尚未在 GitHub 实跑」（X3）；
- 徽章按实测写（**34 单测 / 24 组自检**），包括此前没人发现过期的自检徽章（X4）；
- A1/A2 改为 `measured_with_scope`——宿主编排层实测，不是生产钩子闭环（X5）；
- `echo` 永不冒充 `live`；无 Ollama 的机器上真实 `mode="live"` 回执照旧标 `untested`（X6）；
- 宿主桥保留它本就用来隔离的非确定性，审计只留哈希与计数，不留明文（X7）；
- 混合分保持量纲自洽：`0.5·Jaccard + 0.5·dice + 0.05·tag`（X8）；
- **没有**新增 `after_summary` 字段——`summarized ∩ admitted` 语义等价，不破 41 字段冻结（X10）。

另有作者自己犯、自己抓到的五处缺陷（`DEFECTS` M1–M5）：拼错一个字母导致远程开关永久失效、
离线后端被自家网络门禁拒掉、回执少一个 `ok` 键、断言建立在错误 workload 前提上、
`platform.os` 的偷懒写法。

两项声明不再写成裸 "pass"，也不允许被写成 pass：账本关闭态与开启态逐字节一致（`A1`）、
`full` 档真实开销（`A2`）。自 v0.9.0 起它们为 `measured_with_scope`——由
`scripts/measure_a1_a2.py` 在宿主编排层实测（`A1 = PASS`，`sha256=b48a0aa1f3743514`；
`A2` 中位额外开销 **1.83%**，off 11.3708 ms / full 11.5794 ms，30 次），并明写这不等于
生产钩子闭环。判定本身也要受审：**变异测试**改动一步输出后，判定必须翻成
`FAIL (diff_at_step=3)`——没有变异证明，就不许说判定有效。证据：
`docs/nephron_a1_a2_evidence.json`。
黄金样例（`examples/nephron_ledger_sample.jsonl` + `examples/nephron_replay_report.md`，
由 `scripts/make_nephron_sample.py` 生成）用来证明 41 个字段足以完成回放。
完整规范见 [`docs/nephron.md`](docs/nephron.md) 与 [`docs/uplift.md`](docs/uplift.md)。

### 宿主模型桥 `bridges/`——网络被赶出核心包

核心包守三条：零第三方依赖、离线可跑、确定性。真实模型调用总要破坏后两条，所以它在包外：

```
holoaeon/   零网络 / 零依赖 / 确定性      ← 红线扫描盯着这里
bridges/    ollama / openai 兼容 / echo   ← 宿主侧，允许联网
```

与既有的「线程归宿主」（N1）、`host_managed` 快照同源。密钥只从 `HOLOAEON_API_KEY` 读；
任何非本机地址必须 `HOLOAEON_ALLOW_REMOTE=1` **且** 显式 flag **且** 白名单三者齐全，
否则构造即拒。`echo` 是离线自检后端，绝不冒充 `live`。审计只记
`seq / backend / model / prompt_sha16 / response_sha16 / latency_ms / tokens`。
详见 [`docs/bridges.md`](docs/bridges.md)。

七个包均离线、确定性、零依赖。`subdistill` 随包提供 `data/taxonomy_127.json` 的 127 项
亚学科编码表，对每个 MED/TCM 产物强制医学免责闸门；`analogizes` 关系必须带反例，
否则只能称“隐喻”，不得称已验证。`metab` 的完整规范见 [`docs/metab.md`](docs/metab.md)。

---

## 快速开始

### 环境要求
仅需 Python 3.8+。直接使用包无需 `pip install`。

### 方式一：克隆使用
```bash
git clone https://github.com/weideyouni/holoaeon.git
cd holoaeon
python examples/01_basic_matrix.py
```

### 方式二：可安装（仍零依赖）
```bash
pip install -e .
```

### 最小示例
```python
from holoaeon import Kernel
from holoaeon.agent import Agent

k = Kernel()
k.skills.register_fn("echo", lambda task: "echo:" + task,
                     description="echo the text")
k.register_agent(Agent("a1", "echoer"))

result = k.submit("please echo hello")
print(result["results"][0]["output"])   # echo:please echo hello
```

### 安装领域包
```python
from holoaeon import Kernel
from holoaeon.packs import DataPack

k = Kernel()
DataPack().install(k)

stats = k.submit("basic stats", to="data_analyst",
                 args={"csv_text": "a,b\n1,10\n2,20\n3,30"})
print(stats["results"][0]["output"])
```

---

## 本地启动器 —— 冷/热插拔与内/外部融合

一个可执行入口，在本机演示框架的可插拔性与融合协议：

```bash
python scripts/launch_local.py status                 # 健康快照
python scripts/launch_local.py demo                   # 内外部融合全链路
python scripts/launch_local.py run "任务文本"          # 提交任务（自动选 agent）
python scripts/launch_local.py hotplug optimization   # 运行时加载包，不重启
python scripts/launch_local.py selftest               # 24 组自检
```

- **冷插拔**：启动时 `bootstrap()` 安装全部领域包、绑定内部协作图、注册外部模型后端。
- **热插拔**：系统运行中不重启即可安装新包（`hotplug` 命令当场新增 7 个技能）。
- **内部融合**：组件在进程内经信封/总线通信、由图编排、共享记忆、心跳同步，全程在守卫之后。
- **外部融合**：`ModelAdapter` 注册本地与云端后端并做离线路由决策（低成本→本地，
  长上下文→云端）。

---

## 部署形态

HoloAeon 的设计可从单台笔记本扩展到分布式集群：

| 形态 | 映射方式 |
|---|---|
| **个人笔记本** | 进程内运行 `Kernel`，`ModelAdapter` 指向本地模型，完全离线。 |
| **本地 / 私有服务器** | 把智能体作为长驻 Actor 部署在 `Guard` 之后，记忆与数据保持在信任边界内。 |
| **云端 / 分布式** | 跨节点运行 `Cluster`，用 `Bus` 做节点间路由，经适配器路由到云端模型——每条消息仍过守卫并标记 mode。 |

三种形态使用相同的原语组合，仅部署边界不同。

---

## 项目结构

```
holoaeon/
├── spec.py            # 身份、配置 dataclass、锁数校验
├── envelope.py        # 统一消息信封
├── bus.py             # 发布/订阅、寻址、路由
├── skill.py           # 技能清单与注册表、匹配
├── memory.py          # 三层记忆
├── agent.py           # 智能体原语、签名感知技能调用
├── scheduler.py       # 心跳调度器
├── guard.py           # L1–L8 安全边界
├── kernel.py          # 顶层门面
├── graph.py           # 自适应六边形协作图
├── cluster.py         # 并行 Actor 集群
├── hypervector.py     # HRR + 手写 FFT
├── model_adapter.py   # 任意 LLM 适配层
├── redline.py         # AST 红线扫描器
├── selftest.py        # G1–G24 自检套件
└── packs/             # 九大领域包（含 optimization.py、gaoyi_pack.py）+ 横切扩展包（sovereignty_pack.py、subdistill_pack.py、omnilife_pack.py、omnicore_pack.py、metab_pack.py、nephron_pack.py）
examples/              # 四个可运行示例
tests/                 # unittest 套件
scripts/               # 红线扫描与本地启动器
docs/                  # 深度文档
ALGORITHM.md           # 认知优化与自组织搜索
```

---

## 隐喻 → 工程概念映射表

| 隐喻 | 工程概念 |
|---|---|
| 心跳 | 周期性调度器 tick，用于同步、快照与健康检查 |
| 皮肤 | 分层安全守卫 / 边界控制器 |
| 经络 | 语义路由网络，连接任务、工具、记忆与模型 |
| 细胞骨架 | 结构支撑：生命周期、持久化、注册表、恢复 |
| 赫布协作场 | 基于共激活的权重自适应（自组织连接） |
| 共振 | 智能体通过共享状态与相关性动态对齐 |
| 全息 | 每个局部节点携带全局状态的部分摘要 |

这些仅为组织隐喻，实证机制全部以普通、确定性的软件实现。

---

## 测试

```bash
# 自检套件（G1–G24）
python -c "from holoaeon.selftest import run_all; print(run_all(verbose=True))"

# 单元测试
python -m unittest discover -s tests -v

# 红线扫描（网络 / 依赖 / 危险调用检查）
python scripts/redline_scan.py
```

当前状态：**24/24 自检组通过**、**34 个单元测试通过**、红线扫描对全部源文件报告
**零违规**。

---

## 与其他框架的关系

HoloAeon 不试图替代 LangChain、LlamaIndex、AutoGen、CrewAI、Semantic Kernel 等项目。
它聚焦于编排之下的一层——**认知拓扑、确定性原语与自组织协作**。它可作为：
- 上层认知协议；
- 多智能体矩阵协调器；
- 语义通信总线；
- 自组织协作试验台；
- 应用的模型无关认知底座。

---

## 路线图

- **v0.1**——核心原语、机制、七大领域包、自检与文档。
- **v0.2**——优化与自组织搜索层、本地启动器、冷/热插拔、内/外部融合协议。
- **v0.3**——高译（GaoYi）包：自然语言确定性编译为 HASM 并由内置虚拟机执行意图路由（九大领域包）。
- **v0.4**——两个横切扩展包：**sovereignty**（认知主权：17 技能、0 agent、R0–R4）与
  **subdistill**（SD-Distill：127 亚学科、七阶段蒸馏、七项辅助损失、C1–C4 温度课程）；
  九包核心的 25 智能体 / 47 技能口径保持不变。
- **v0.5**——第三个横切扩展包：**omnilife**（全域生活主权：衣 / 食 / 住 / 行 / 教 / SaaS，
  18 技能、0 agent、L1–L6）；不新增行与节点，设计上拒绝并发探测、代理切换与 DOM 注入。
- **v0.6**——第四个横切扩展包：**omnicore**（把投喂的 Omni-Core 引擎重写为确定性软件；
  20 技能、0 agent、M1–M6）。复现并修掉投喂代码 5 处缺陷；纯函数心跳、快照交宿主持久化、
  全篇 `metaphor=True`。
- **v0.7**——第五个横切扩展包：**metab**（把 METAB 代谢层落成可判定治理层；26 技能、
  0 agent、T1–T8）。六染色体准入、四问定态、八阶段生命周期、三层授权、消化道双通道、
  信任半径、组合白名单；规格内 8 处冲突逐条消解。
- **v0.8**——第六个横切扩展包：**nephron**（肾单位层 P0：只追加认知账本与回放；24 技能、
  0 agent、W1–W7）。只读观测，不分页 / 不压缩 / 不淘汰 / 不做预算控制；规格内 10 处冲突
  逐条消解（N1–N10），两项验收声明在发布时恒为 `pending_human_measure`。
- **v0.9**——第七个横切扩展包：**uplift**（U1–U6 补齐短板；24 技能、0 agent、W1–W7）。
  排序键全序、`_fft` 纯函数化、字符 n-gram 混合分、CI 与 issue/PR 模板、徽章与支持矩阵口径
  对齐、A1/A2 转 `measured_with_scope`（带变异证明）、宿主模型桥 `bridges/`、O-1～O-10
  裁决；十处冲突消解（X1–X10）、五处自身缺陷登记（M1–M5）。
- **v0.10**——可插拔持久化后端与节点间总线传输。
- **v0.11**——声明式图/拓扑定义与包创作工具包。
- **v1.0**——稳定认知框架，API 冻结，文档完整。

---

## 贡献

欢迎提交 Issue 与 Pull Request。提交前请阅读 `docs/` 中的相关文档，并确保自检、单元测试
与红线扫描全部通过。提交 PR 时请包含改动说明、受影响模块、测试/示例与文档更新。参见
[CONTRIBUTING.md](CONTRIBUTING.md)。

---

## 开源协议

基于 **Apache License 2.0** 开源。在保留版权与协议声明的前提下，可自由使用、修改、分发与
商业化。参见 [LICENSE](LICENSE)。

---

## 免责声明

本项目中的生物与宇宙词汇均为隐喻，仅用于描述多智能体软件的同步、边界、路由、支撑与自组织
机制，不构成医学、生物学或临床建议，也不声称对真实器官、生理结构或超自然实体建模。所有
仿真回执均标记 `simulated`；**仿真不等于证明**，人类判断始终是最终权威。
