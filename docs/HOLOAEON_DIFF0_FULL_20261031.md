# HoloAeon DIFF=0 升级合订稿（2026-10-31）

> 本文件是「确定性资产化」这一轮升级的全量证据合订本：对外 README、公开基准、
> 开放规范、三本 cookbook、项目快照、智能体投喂包、仓库运营件。
> 三个数字：`DIFF=0 2fc892cf9af6e755 | 拦截 100% | 冷装配 ≈31ms / 峰值 1.69MiB`。
> 全部条目 `evidence_class=simulated`：仿真 ≠ 证明，碳基终裁。

---

## 一 · 对外 README（三数字徽章版）

> 源文件：`README_DIFF0_20261031.md`

# HoloAeon · 一个带回执的确定性内核

```
DIFF=0 2fc892cf9af6e755 | 拦截 100% | 冷装配 ≈31ms / 峰值 1.69MiB
```

三个数字，随发版重跑，出处是 [benchmarks/README.md](benchmarks/README.md) 与
`benchmarks/results-0.9.1.json`。全部条目 `evidence_class=simulated`：仿真 ≠ 证明。

HoloAeon 是零依赖（`dependencies = []`）、默认离线、确定性、可审计的多智能体认知框架：
12 个正交原语（C1–C12）+ 8 层语义守卫 + 手写 HRR 超向量（1024 维，radix-2 FFT）+ 领域/扩展双层包体系。
你不需要读全部源码就能相信它——但它把「凭什么相信」写成了可以自己复跑的命令。

## 三个数字凭什么算数

| 指标 | 口径 | 反造假手段 |
|---|---|---|
| **DIFF=0** `2fc892cf9af6e755` | 16 步固定 workload 跑两次，各用全新内核，剔除 `ts/uptime/elapsed` 等物理量后对规范 JSON 求 sha256 前 16 位 | **篡改敏感性自检**：把任务原文改一个字，哈希变为 `f42c8229ee5acd73`。哈希不变即视为空转，判不通过 |
| **拦截 100%** | 20 条标准请求集：危险 5 / 越权 5 / 超限 3 / 失真 3 / 合法 4 | 合法 4 条必须全放行；只报拦截率不报放行率就是耍流氓 |
| **足迹 ≈31ms / 1.69MiB** | 进程内内核装配 + `tracemalloc` 峰值 | 明确标注「不是 OS 冷启动 import」，机器规格另列，不混进哈希 |

> 这三个数字来自一次真实的翻车：早期把未登记字段当物理量整段剔除，导致三色用例哈希全等
> （`9eb1936e9b55cb08`）。修法是把待测字段登记进分类表，并加篡改自检证明哈希真的对内容敏感。

## 十分钟上手（三本 cookbook，全部逐步实测）

| 编号 | 内容 | 实测证据 |
|---|---|---|
| [01](cookbooks/01_make_your_skill/README.md) | 做一个你自己的技能（`bmi_calc` 七步） | 路由 `0.20757`；提交 `bmi 22.86`；危险调用 `blocked` |
| [02](cookbooks/02_add_ledger_to_your_agent/README.md) | 给现有 Agent 加账本 + 单文件 HTML 视图 | 6 条记录 → 5,860 B；两次渲染 sha 一致 `98940b774566543b` |
| [03](cookbooks/03_offline_deploy_old_laptop/README.md) | 离线部署到 2GB 旧笔记本（含 Win7/10 差异） | `selftest 24/24`；`34 tests OK`；零次 `pip install` |

## 规范：确定性 Agent 运行时 v0.1

[docs/spec-diff0.md](docs/spec-diff0.md) 把「确定性」从项目特性升格成可被他方实现的开放协议：
DIFF=0 哈希协议、理由码族表、证据防漂移协议、`full / sampled / incompatible` 兼容性分级，
以及十条逐项可判定的自检清单。**本规范由 HoloAeon 项目发起，欢迎他方实现。**

## 快速开始

```powershell
cd F:\doubaowork\holoaeon
python scripts\launch_local.py status       # has_graph=True  has_adapter=True
python scripts\launch_local.py demo         # 内部总线 + 外部模型分流，末行 all_ok: True
python scripts\launch_local.py selftest     # ==> 24/24
python -m unittest discover -s tests        # Ran 34 tests ... OK
python scripts\verax_verify.py --out reports # 末行 VERAX_EXIT=0
python benchmarks\bench_public.py           # 三个数字 + BENCH_EXIT=0
```

## 项目快照（给其他智能体）

[snapshot/SNAPSHOT.md](snapshot/SNAPSHOT.md) 是一页可接手的快照：维度口径、三个数字、
13 条入口命令、7 条不变量、4 条明确不做、已知限制、目录骨架。
机器读版本在 `snapshot/project_snapshot.json`，由 `scripts/make_snapshot.py` 现算生成。

## 不变量（破了就不算 HoloAeon）

- **零依赖**：`pyproject.toml` 的 `dependencies = []`，只用 Python 标准库；
- **默认离线**：不开端口、不联网、不读密钥、不写遥测；
- **确定性**：DIFF=0 两次一致，且篡改自检通过；
- **可审计**：每条裁决含 `action/layer/reason`，回执强制 `evidence_class`；
- **安全边界**：L1–L8 八层守卫，20 条标准集拦截率 100%；
- **诚实纪律**：`simulated` 是默认档，`measured` 必须带来源与测量时刻；
- **维度不变**：25 智能体 / 47 技能 / 9 领域包 + 7 扩展包 / 34 单测 / 24 自检。

## 明确不做

- 不新增第 17 个领域包（治理包的边际收益已经递减）；
- 不去卷「重依赖 + 托管平台」的右下角（LangGraph / MetaGPT / CrewAI 的战场，进去必输）；
- 不把 `simulated` 写成实测；
- 不为了追 star 破坏零依赖与既有测试。

## 已知限制（先说清楚）

- 语义通道 `holoaeon/semvec.py`（PMI + 幂迭代截断 SVD，纯标准库）：语料只取 **47 条技能自述**
  （与 `docs/` 彻底解耦，改文档不再影响基准），实测 **12 条固定意图混合路由 11/12（误路由 1/12 = 8.3%）**，
  首次落进 ≤10% 门槛；`python scripts\bench_semvec.py` 可复跑，两次 `fit` 逐位一致（`digest=789b71a36bfcd66a`）。
  未命中那条是「患者数据统计 → `word_count`」（缺医疗语料，属真实弱项）。**这批参数仍是在这 12 条上选定的，
  含过拟合风险；另跑 6 条留出意图中 2 条期望名不存在（`replay_check` / `copywriting`），余 4 条命中 2 条 ——
  故 8.3% 只对这 12 条负责，不据此声称整体误路由率，留出集泛化未验证。**
- 领域包产骨架不产成稿；账本可视化是确定性静态 HTML，不是托管平台。
- Apache-2.0 护不住功能，只护得住标准与证据；双许可决策留给构建者单独裁决。

## 目录

| 路径 | 说明 |
|---|---|
| `holoaeon/` | 核心包：12 原语 + `audit/`（VERAX）+ `packs/`（16 包）+ `semvec.py` |
| `benchmarks/` | 三个数字的唯一出处（`bench_public.py` + `results-*.json`） |
| `cookbooks/` | 三本实战教程 |
| `docs/` | `spec-diff0.md`（规范）、`cookbooks.md`（索引）、`VERAX.md`（可信层设计） |
| `scripts/` | `launch_local.py`、`verax_verify.py`、`ledger_view.py`、`make_snapshot.py` |
| `snapshot/` | 项目快照（md + json） |
| `tests/` | `34` 项基线 + `verax/` 16 项 + `v3/` 5 项 |

## 许可

Apache-2.0。护城河不靠许可证高墙，靠**空象限先发 + 可复算基准 + 开放规范署名**。

---

## 二 · 公开基准实测（evidence_class=simulated）

> 源文件：`benchmarks/README.md`

# 公开基准（benchmarks）

> 三个数字，随发版重跑。全部条目 `evidence_class=simulated`：仿真 ≠ 证明。

```
DIFF=0 2fc892cf9af6e755 | 拦截 100% | 冷装配 31.17ms / 峰值 1.69MiB
```

## 一 · DIFF=0（确定性）

| 项 | 值 |
|---|---|
| workload 步数 | 16 |
| 规范化后两次一致 | True |
| run1 哈希 | `2fc892cf9af6e755` |
| run2 哈希 | `2fc892cf9af6e755` |
| DIFF=0 | **True** |
| 规范化保留的顶层键 | `runtime_id, steps` |

条文：两次运行各用全新内核，剔除 ts/uptime/elapsed/timestamp 等物理量后
对 canonicalize 结果求 sha256 前 16 位；两次相同即 DIFF=0。
为防「内容被整段剔除、哈希恒真空转」，另做篡改敏感性自检：把任务原文改一个字，
哈希必须变化（见下表）。

| 敏感性自检 | 值 |
|---|---|
| 原始哈希 | `2fc892cf9af6e755` |
| 篡改字段 | steps[*].value.task（word_count 任务原文） |
| 篡改后哈希 | `f42c8229ee5acd73` |
| 哈希对内容敏感 | **True** |

## 二 · 守卫拦截率（安全边界）

| 类别 | 样本 | 拦截 |
|---|---|---|
| danger | 5 | 5 |
| distort | 3 | 3 |
| legit | 4 | 0 |
| overflow | 3 | 3 |
| privilege | 5 | 5 |

危险请求 **16/16 拦截（100%）**；合法 **4/4 放行**。

## 三 · 零依赖足迹（可运行成本）

| 项 | 值 |
|---|---|
| 内核装配耗时 | 31.17 ms |
| 峰值内存（tracemalloc） | 1.69 MiB |
| 装齐后 agent / skill | 25 / 47 |

口径：`build_ms` 为进程内内核装配耗时，不是 OS 冷启动 import；
峰值内存为 tracemalloc 追踪的 Python 分配峰值，不含解释器常驻。

## 机器规格（披露字段，不参与哈希）

| 项 | 值 |
|---|---|
| platform | `Windows-10-10.0.19045-SP0` |
| machine | `AMD64` |
| cpu_count | 32 |
| python | 3.13.16 |
| 生成时刻 | 2026-10-31T11:46:17Z |

## 复跑

```powershell
python benchmarks\bench_public.py
```

同一台机器上连跑两次，`diff0.hash_run1 == hash_run2` 必须成立；
换机器后哈希仍应一致（物理量与机器规格都不进哈希）。

---

## 三 · 确定性 Agent 运行时规范 v0.1

> 源文件：`docs/spec-diff0.md`

# 确定性 Agent 运行时规范 v0.1（草案）

> 发起方：HoloAeon 项目（`holoaeon/spec.py` 的 `VERSION` 为版本权威源）。
> 状态：草案，条款可判定、可被第三方实现。**本规范由 HoloAeon 项目发起，欢迎他方实现。**
> 本文不定义产品形态，只定义「什么算可复现」的下限。仿真是仿真，证明是证明。

## 1 范围

本规范面向「声称自己是确定性 Agent 运行时」的任意实现，规定四件事：

1. 复现哈希（DIFF=0）怎么算，什么字段必须剔除；
2. 理由码怎么枚举，什么算「已解释」；
3. 证据怎么分级，什么算「漂移」；
4. 兼容性怎么分级，什么程度的复现算「合格实现」。

不规定：语言、框架、模型、部署形态、许可证。规范只管证据，不管路线。

## 2 术语

| 术语 | 定义 | 判定方式 |
|---|---|---|
| ReproCore 可复现核心 | 裁决、路由目标、命中技能、技能输出等「同一输入应相同」的字段集合 | 字段名登记在实现方的分类表中，未登记即未知 |
| Physical 物理量 | 时间戳、耗时、线程完成序、进程号、内存地址等「本就该每次不同」的字段 | 同上，必须显式剔除而非丢弃 |
| Canonicalize 规范化 | 剔除物理量、统一数值表示、对集合稳定排序后生成规范 JSON 的过程 | 同一逻辑输入两次输出逐字节一致 |
| ReproHash 复现哈希 | `sha256(canonical_json)` 取前 16 个十六进制字符 | 与实现方冻结的黄金值比对 |
| EvidenceClass 证据分级 | `simulated` / `measured` / `third_party` 三档 | `measured` 必须带来源与测量时刻 |
| Golden 黄金回归值 | 随代码评审冻结的期望哈希或期望输出 | 改动须在 PR 标题标注 `[golden]` |
| Self-Attestation 自证报告 | 一次全量自检 + 基准的可复算报告 | 报告自身哈希可复现，`ts_build` 不进哈希 |

## 3 DIFF=0 哈希协议

### 3.1 三条硬规则

- **R1 显式分类**：实现方必须提供字段分类表（`physical` / `repro` / `opaque`）。未登记字段按物理量处理，并**计数告警**，不得静默丢弃。
- **R2 稳定排序**：任何 `list[dict]` 先按稳定键（如 `step` / `seq` / `agent_id`）排序再递归规范化；集群完成序不可复现，必须靠排序消除。
- **R3 定值序列化**：数值统一为定点字符串（抑制浮点抖动）；枚举取 `value`；`None` 序列化为 `null`；键升序、无空白。

### 3.2 必须剔除的字段（最小集）

`ts` / `timestamp` / `elapsed` / `duration` / `started_at` / `finished_at` /
`thread_order` / `addr` / `id_runtime` / `pid` / `uptime_s` / `generated_at`。

> 反例（真实踩过）：把整包回执连 `ts` 一起哈希，必然每次不同，于是得出「不确定」的假结论。
> 另一反例：把未登记的业务字段当物理量整段剔掉，哈希对内容失去敏感性，两次跑当然相同——
> 这叫「恒真空转」，比假红灯更危险。**因此规范要求：凡 DIFF=0 的公开声称，必须同时发布篡改敏感性自检。**

### 3.3 算法

```
canonical = canonicalize(receipt)          # 按 3.1
h = sha256(canonical_json(canonical))[:16] # 前 16 hex
stable = all(h_i == h_0 for i in runs)     # runs ≥ 2，每个 run 用全新内核
```

### 3.4 敏感性自检（强制）

对 ReproCore 的任一字段做单点篡改（如把任务原文改一个字），哈希**必须**变化；
哈希不变即判定该实现「未通过本规范」，因为它的 DIFF=0 是空转。

## 4 理由码规范

### 4.1 结构

每条裁决输出固定三字段：`{action, layer, reason}`。

- `action ∈ {allow, advise, block}`，只允许三值；
- `layer` 为守卫层标识（本实现为 `L1`–`L8`：结构 / 体量 / 危险模式 / 权限 / 身份与失真 / 元数据 / 审计 / 一致性）；
- `reason` 为可枚举理由码或人类可读短语，**不得为空**。

### 4.2 理由码分层（参考 NEPHRON 27 码体例的分类法）

| 族 | 前缀 | 含义 | 例 |
|---|---|---|---|
| 结构 | `struct_` | 信封字段缺失 / 类型不符 | `struct_missing_recipient` |
| 体量 | `size_` | 载荷或配额超限 | `size_payload_over_1mib` |
| 危险 | `danger_` | 命中危险调用模式 | `danger_os_system` |
| 权限 | `perm_` | 权限等级不足 | `perm_short_2to0` |
| 身份 | `ident_` | 伪造身份或失真输入 | `ident_claim_admin` |
| 元数据 | `meta_` | trace / 模式缺失 | `meta_no_trace` |
| 审计 | `audit_` | 审计链断裂 | `audit_gap` |
| 诚实 | `hon_` | 证据分级不合规 | `hon_measured_no_source` |

### 4.3 判定口径

- 同一输入 + 同一守卫层配置 → 同一 `reason`（理由码不得含时间、随机值、进程号）；
- `block` 必须能指名命中的层与模式；说不出哪一层，就不算「已解释」。

## 5 证据防漂移协议

### 5.1 分级

| 级别 | 含义 | 强制附加字段 |
|---|---|---|
| `simulated` | 仿真 / 构造数据，默认档 | 无（`measure_source` 与 `measure_ts` 必须为 null） |
| `measured` | 本机实测 | `measure_source`（命令或路径）+ `measure_ts` |
| `third_party` | 外部来源 | `measure_source` 指向可核验出处 |

### 5.2 漂移判定

- 出现 `measured` 而缺 `measure_source` → 记诚实告警（`H1`），报告结论至少降为 yellow；
- 回执对象缺 `evidence_class` → 记诚实告警（`H2`）；
- 文档里出现「实测 / 真实生效」字样但同目录无非 `simulated` 证据 → `H1`。

### 5.3 CI 体例

```
python scripts/verax_verify.py --out reports     # 单一入口
退出码 0=绿 / 1=红（红线或复现或单测不过） / 2=黄（诚实或未知字段告警）
```

报告双导出：`reports/attestation.md`（人读）与 `reports/attestation.jsonl`（机器读，逐行一条检查）。
报告自身 `verdict_hash` 由结论字段规范化生成，`ts_build` 不参与——否则报告自己也漂移。

## 6 兼容性分级

| 等级 | 条件 | 允许的声称 |
|---|---|---|
| `full` | 两个独立 run 的 ReproHash 一致；黄金值命中；敏感性自检通过；物理量差异非空（证明剔除真的在起作用） | 「可回放 / DIFF=0」 |
| `sampled` | 仅部分任务有黄金值，或仅在固定机器上复现 | 「有限复现，未覆盖全任务」 |
| `incompatible` | 哈希不稳定，或字段分类表缺失，或敏感性自检失败 | 不得声称确定性 |

分级必须随证据一起发布；只发布等级、不发布证据，视为未分级。

## 7 自检清单（实现方逐条打勾）

- [ ] D1 字段分类表公开，未知字段计数告警（R1）
- [ ] D2 `list[dict]` 稳定排序后再规范化（R2）
- [ ] D3 数值定点化，枚举取 `value`（R3）
- [ ] D4 两次独立 run 哈希一致
- [ ] D5 篡改 ReproCore 后哈希变化（敏感性自检）
- [ ] D6 黄金值冻结并有评审标记 `[golden]`
- [ ] D7 每条裁决含非空 `reason`
- [ ] D8 回执强制 `evidence_class`，`measured` 带来源与时刻
- [ ] D9 报告 `verdict_hash` 可复现，`ts_build` 不进哈希
- [ ] D10 CI 单入口给出 0/1/2 三态退出码

HoloAeon 自身作为第一实现，D1–D10 全部通过（见 `benchmarks/README.md`、
`docs/VERAX.md`、`reports/attestation.md`）。

## 8 已知限制

- 本规范只管**单机确定性**，不管分布式一致性；
- 理由码族表是分类法，不是封闭枚举：实现方可扩展，但不得修改已有语义；
- 本实现语义通道（`holoaeon/semvec.py`）语料只取 47 条技能自述（与 `docs/` 解耦，改文档不漂移），
  实测 **12 条固定意图混合路由 11/12（误路由 8.3%）**（`scripts/bench_semvec.py` 可复跑）。
  参数是在同一批意图上选定的，含过拟合风险；留出集 6 条中 2 条期望名不存在，
  余 4 条命中 2 条，**泛化未验证**。故路由准确率不纳入本规范的合格判据，只作为披露项；
- 维度取舍：`semvec.DIM=32` 与早期投喂建议的 64 维不同。理由是 32 维与 64 维在 12 条意图上
  命中相同，而 `fit` 耗时随维数线性增长（2 GB 旧机口径），故取 32；`MAX_VOCAB=2000`、`MIN_DF=1`
  同理是为让 `review / sample` 这类只出现一两次的专名进入词表，否则查询向量会塌成零向量
  （稳定语料下实际上限用不满，实测词表 334）；
- 规范不承诺任何外部真实性：`measured` 只表示「有人在本机量过」，不等于「结论为真」。

---

## 四 · cookbook 索引

> 源文件：`docs/cookbooks.md`

# Cookbooks 索引

三本 cookbook，都是一台机器、十分钟、零依赖能跑完的实战记录。代码逐步实测过。

| 编号 | 标题 | 你要解决的事 | 实测证据 |
|---|---|---|---|
| 01 | [做一个你自己的技能](cookbooks/01_make_your_skill/README.md) | 从零加一个 `bmi_calc` 技能，跑通注册 → 路由 → 执行 | 路由 `[('bmi_calc', 0.20757)]`；提交 `bmi 22.86`；危险调用 `blocked` |
| 02 | [给现有 Agent 加账本](cookbooks/02_add_ledger_to_your_agent/README.md) | 每次动作留一条可复算的记录，并渲染成单文件 HTML | 6 条记录 → 5,860 字节 HTML；两次渲染 sha 一致 `98940b774566543b` |
| 03 | [离线部署到旧笔记本](cookbooks/03_offline_deploy_old_laptop/README.md) | 2GB 旧机、无网络、Python 3.8+ 上跑完整套自检 | 装配 ≈31ms；峰值 1.69MiB；`selftest 24/24`；`34 tests OK` |

## 三本共用的纪律

- **零依赖**：全程 `pip install` 零次，`pyproject.toml` 的 `dependencies = []` 不许破；
- **默认离线**：不开端口、不联网、不读 `.env`；
- **确定性**：任何「两次跑应当一样」的说法，都要给出两次的哈希；
- **诚实**：仿真标 `simulated`，没实测的不写成实测。

## 阅读顺序建议

先读 01 建立「技能 = 清单 + 函数」的最小认知，再读 02 明白「记录 ≠ 日志」，
最后读 03 把它搬到没有网络的机器上。三本都读完，你已经能把 HoloAeon 当作
「一个带回执的确定性内核」来用，而不只是读它的代码。

## 与规范的关系

cookbook 教你怎么做，[确定性 Agent 运行时规范 v0.1](spec-diff0.md) 规定做到什么程度算合格。
想声称「DIFF=0」，先过规范第 7 节的十条自检。

---

## 五 · Cookbook 01 做一个你自己的技能

> 源文件：`cookbooks/01_make_your_skill/README.md`

# Cookbook 01 · 十分钟做一个你自己的技能

目标：给 HoloAeon 加一个自己的技能（BMI 计算），跑通「注册 → 路由 → 执行」全链路。
前置：Python 3.8+，仓库根目录，**不需要 pip install 任何东西**。
耗时实测：10 分钟内可完成（本仓库实测代码见下，全部逐行跑过）。

## 第 1 步 · 站在仓库根目录

```powershell
cd F:\doubaowork\holoaeon
python scripts\launch_local.py status
```

预期输出（摘要）：

```
has_graph=True  has_adapter=True  agents=25  skills=47
```

`has_graph / has_adapter` 都为 True，说明内核与协作图已装好。若这一步就失败，先别看后面的步骤。

## 第 2 步 · 写技能函数

技能函数只收到**一个任务字符串**（内核路径不会把 payload 当关键字参数传进来），
所以参数写在句子里，用正则取出来。这一条是最容易踩的坑，实测确认过。

```python
import re

def bmi_calc(task, **kwargs):
    nums = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", task or "")]
    if len(nums) < 2:
        return {"ok": False, "error": "请给出身高(cm)与体重(kg)，例如「算一下 bmi 175 70」"}
    height, weight = nums[0] / 100.0, nums[1]
    value = round(weight / (height * height), 2)
    return {"ok": True, "bmi": value, "level": "正常" if 18.5 <= value < 24 else "需关注"}
```

## 第 3 步 · 声明清单（manifest）

```python
from holoaeon.skill import Skill, SkillManifest, SkillRegistry

reg = SkillRegistry()
reg.register(Skill(SkillManifest(
    name="bmi_calc",
    description="BMI 体质指数计算",
    inputs={"height_cm": "身高厘米", "weight_kg": "体重千克"},
    outputs={"bmi": "体质指数", "level": "分级"},
    tags=["health", "bmi"],
), bmi_calc))
```

`description` 与 `tags` 决定路由得分：既有 `Registry.score` 用 Jaccard + 字符 2-gram + 标签命中，
语义通道（`holoaeon/semvec.py`）可另加 0.75 权重（`scripts/bench_semvec.py` 的 `WEIGHT_SEM`，
配合基线噪声地板 `BASE_FLOOR=0.15`）。清单写得越具体，路由越准。

## 第 4 步 · 验证路由

```python
print(reg.match("算一下 bmi", 3))   # [('bmi_calc', 0.20757)]
```

实测返回 `[('bmi_calc', 0.20757)]`。数值低是正常的——短查询与长描述的字符 2-gram 重叠小，
只要目标技能排第一就算通过。

## 第 5 步 · 挂到智能体

```python
from holoaeon.agent import Agent
from holoaeon.kernel import Kernel

k = Kernel()
k.register_agent(Agent("health_coach", "health", skills=reg, skill_names=["bmi_calc"]))
```

`skill_names` 限定这个智能体只能用这一项技能，避免它去抢别的包。

## 第 6 步 · 端到端跑一次

```python
res = k.submit("算一下 bmi 175 70", to="health_coach")
print(res["all_ok"], res["results"][0]["output"])
```

预期输出：

```
True ok {'ok': True, 'bmi': 22.86, 'level': '正常'}
```

再确认守卫是活的：

```python
print(k.submit("执行 os.system('ls -la')")["results"][0]["status"])   # blocked
```

## 第 7 步 · 守住零依赖与红线

```powershell
python scripts\redline_scan.py
```

预期：`扫描文件数：41` / `结果： 干净（零违规）`。
新技能里不要出现 `os.system / eval( / subprocess` 这类调用，否则会被 L3 直接拦掉。

## 常见错误

| 现象 | 原因 | 处理 |
|---|---|---|
| `status='error'`，`err` 里 `'str' object has no attribute 'payload'` | 把技能函数当成收信封来写 | 技能签名是 `fn(task, **kwargs)`，参数从任务串取 |
| 输出里参数全是 0 / 报「请给出身高」 | 任务串里没写数字 | 把数字写进任务，如 `算一下 bmi 175 70` |
| `status='no_skill'` | `match` 没命中 | 补 `description` 与 `tags`，让词面对齐 |
| 提交被 `blocked` | 命中危险模式或越权 | 去掉危险调用；不要伪造 `as_identity` |

## 下一步

- 把技能放进领域包：`holoaeon/packs/<pack>.py` 里追加，再 `get_pack(key).install(k)`；
- 给技能加语义路由：读 `holoaeon/semvec.py` 与 `scripts/bench_semvec.py`，按 0.75 权重 + 噪声地板混合；
- 想让它可审计：读 Cookbook 02，给这个智能体加账本。

---

## 六 · Cookbook 02 给 Agent 加账本

> 源文件：`cookbooks/02_add_ledger_to_your_agent/README.md`

# Cookbook 02 · 给现有 Agent 加账本（十分钟）

目标：让你已有的 Agent 每次动作都留一条可回放、可渲染的账本记录，并能一键生成 HTML 视图。
前置：仓库根目录、Python 3.8+、零依赖（不装任何包）。实测：6 条记录 → 5,860 字节 HTML。

## 为什么账本是「记录」而不是「日志」

日志给人看，账本给机器复算：固定 `tick` / `seq` 排序、理由码可枚举、同一账本渲染两次字节一致。
这样别人拿到你的账本，能验你「说过什么」，而不是只能信你「说过」。

## 第 1 步 · 账本的最小记录结构

```json
{"tick": 1, "seq": 0, "window_used": 1,
 "events": [{"seq": 0, "reason_code": "ok", "level": "info", "detail": "..."}],
 "updated_at": "2026-10-31T10:00:00Z", "fingerprint": "fp01"}
```

- `tick`：心跳序号，同一个 tick 内的事件必须同组；
- `reason_code`：可枚举的理由码（`ok / advise / warn / block / error`），不要写自由文本；
- `updated_at` 只用于展示：**渲染器不把它写进 HTML**，否则两次渲染字节就不一致了。

## 第 2 步 · 从内核心跳取材

```powershell
python scripts\ledger_view.py --sample data\ledger_sample.jsonl
```

预期：`sample written: ... (6 records)`。它用 6 次 `kernel.tick()` 造了 6 条记录，
其中第 3 条带 `advise`、第 5 条带 `block`，用来验证分歧高亮。

想知道 tick 里有什么：`python -c "from holoaeon.kernel import Kernel; print(Kernel().tick())"`
键为 `tick / ts / active / degraded / idle / faults / watch_count`——注意 `ts` 是物理量，别进指纹。

## 第 3 步 · 接上你自己的 Agent

在你的循环里，每完成一步就追加一行 JSONL（`encoding='utf-8'`，`sort_keys=True`）：

```python
import json

def log_step(fh, tick, seq, code, detail="", level="info"):
    rec = {"tick": tick, "seq": seq, "window_used": 1,
           "events": [{"seq": seq, "reason_code": code, "level": level, "detail": detail}],
           "updated_at": "2026-10-31T10:00:00Z", "fingerprint": "fp%02d" % (seq + 1)}
    fh.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")
```

## 第 4 步 · 渲染成单文件 HTML

```powershell
python scripts\ledger_view.py data\ledger_sample.jsonl -o reports\ledger.html
```

预期：`html: reports\ledger.html  size=5860 bytes  sha=98940b774566543b  records=6`。
双击 HTML 即可打开，无外部资源、无 JS，断网也能看。

## 第 5 步 · 验证「确定性渲染」

```powershell
python scripts\ledger_view.py data\ledger_sample.jsonl -o reports\ledger_a.html
python scripts\ledger_view.py data\ledger_sample.jsonl -o reports\ledger_b.html
(Get-FileHash reports\ledger_a.html).Hash -eq (Get-FileHash reports\ledger_b.html).Hash
```

预期 `True`。若不相等，检查是不是往输出里塞了时间戳或随机 id。

## 第 6 步 · 让账本进 CI

```powershell
python scripts\verax_verify.py --out reports
```

末行应为 `VERAX_EXIT=0`。VERAX 会把「红线 + 复现 + 诚实」合成一个退出码，
账本里的 `block` 记录不会让门禁变红（它是被正确拦下的证据，不是失败）。

## 常见错误

| 现象 | 原因 | 处理 |
|---|---|---|
| 两次渲染哈希不同 | 输出里含 `updated_at` / 随机 id | 渲染器只认结构字段，展示字段一律不进 HTML |
| 分歧区一片空白 | 事件里没有 `level` 也没 `reason_code` | 至少写 `reason_code`，`ok/warn/block` 即可着色 |
| HTML 打开是空白 | 账本路径写错，读到 0 行 | 先 `Get-Content` 数行，再渲染 |
| 中文乱码 | 用 `>` 或 `Out-File` 写文件 | 用 `encoding='utf-8'` 显式写，别过 PowerShell 管道 |

## 下一步

- 把账本挂进 `holoaeon/audit/receipt.py` 的 `Receipt`，让每条回执自带 `evidence_class`；
- 想让别人能复算你的账本：读 `docs/spec-diff0.md` 的「DIFF=0 哈希协议」；
- 想把账本视图当交付物：直接交付 HTML，别转成截图。

---

## 七 · Cookbook 03 离线部署旧笔记本

> 源文件：`cookbooks/03_offline_deploy_old_laptop/README.md`

# Cookbook 03 · 把 HoloAeon 离线部署到一台旧笔记本

目标：在 2GB 内存、无网络、Python 3.8+ 的旧机器上跑起来，并跑完整套自检。
前置：一台能装 Python 的旧机；一个 U 盘或内网拷贝通道（全程不需要联网）。
实测基线：内核装配 ≈31ms、峰值内存 1.69MiB、25 智能体 / 47 技能（v0.9.1）。

## 第 1 步 · 离线取包

在能联网的机器上打包，拷到旧机：

```powershell
git clone https://github.com/weideyouni/holoaeon.git
Copy-Item -Recurse holoaeon D:\holoaeon
```

没有 git 就下载 zip 解压。**不要**在旧机上 `pip install -r`——本项目 `dependencies=[]`，
一个第三方包都不需要。若解压后看到 `.venv`、`node_modules` 之类目录，说明你拿错了包。

## 第 2 步 · 确认 Python 版本

```powershell
python -V
```

必须是 3.8 及以上。Windows 7 上官方最后一个可用版本是 Python 3.8（3.9+ 不再支持 Win7），
这也是本项目的下限；Win10/11 用 3.10~3.13 都实测通过（本基线跑在 3.13）。

## 第 3 步 · 三行验证

```powershell
cd D:\holoaeon
python scripts\launch_local.py status
python scripts\launch_local.py demo
```

预期 `status`：`has_graph=True  has_adapter=True`。
预期 `demo`：总线 25 个地址、记忆四层计数、外部融合「低成本→local / 长上下文→cloud」、末行 `all_ok: True`。

这一条 `demo` 就是「内部融合协议 + 外部融合协议」的现场证据：
内部走总线投递信封，外部走 model_adapter 的本地/云端分流。

## 第 4 步 · 跑自检与单测

```powershell
python scripts\launch_local.py selftest      # 预期 ==> 24/24
python -m unittest discover -s tests         # 预期 Ran 34 tests ... OK
python -m unittest discover -s tests\verax   # 预期 Ran 16 tests ... OK
python -m unittest discover -s tests\v3      # 预期 Ran 5 tests ... OK
```

两条 `unittest discover` 必须分开跑：合并会把 34 项口径搅在一起，这是已知坑。

## 第 5 步 · 红线与公开基准

```powershell
python scripts\redline_scan.py               # 预期 干净（零违规）
python benchmarks\bench_public.py            # 预期 BENCH_EXIT=0
```

基准会打印三个数字：`DIFF=0 <hash>` / 拦截 100% / 冷装配 ~31ms、峰值 ~1.7MiB。
换机器后 DIFF=0 的哈希应当不变（物理量与机器规格都不进哈希）；拦截率与足迹允许变。

## 第 6 步 · 旧机上的取舍

| 症状 | 处理 |
|---|---|
| 启动慢于 3 秒 | 老机械盘 + 冷 import；改用 `python -X importtime` 看是不是磁盘问题，别改代码 |
| 内存吃紧 | 只装必要领域包：`get_pack('writing').install(k)`，别一次装 16 个 |
| PowerShell 5 中文乱码 | 用 `-Encoding utf8` 写文件；或 `$env:PYTHONUTF8='1'` 后再跑 |
| Win7 上 `pwsh` 不存在 | 全部命令改用 `powershell`（5.x）语法，本项目脚本本身不依赖 pwsh |

## 第 7 步 · 确认「零依赖」真的成立

```powershell
Select-String -Path pyproject.toml -Pattern "dependencies"
```

预期看到 `dependencies = []`。如果这一行变了，说明有人偷偷加了依赖，直接拒绝合入。

## 常见错误

| 现象 | 原因 | 处理 |
|---|---|---|
| `ModuleNotFoundError: holoaeon` | 在错误的目录跑脚本 | 必须在仓库根目录执行 `scripts\launch_local.py` |
| `No module named pytest` | 本项目不用 pytest | 用 `python -m unittest discover` |
| 自检 `24/24` 但某项静默跳过 | 早期 `selftest` 无 `__main__` 入口的坑 | 用 `python scripts\launch_local.py selftest`，不要用 `python -m holoaeon.selftest` |
| 门禁变黄 | 回执里出现无来源的 `measured` | 老老实实标 `simulated`，别把仿真写成实测 |

## 下一步

- 想给旧机加可视化：`python scripts\ledger_view.py --sample data\ledger_sample.jsonl` 生成单文件 HTML；
- 想接入自己的模型：读 `docs/model-adapter.md`，`ModelBackend` 里填本地端点即可，仍不引入第三方依赖；
- 想给别人复现你的结论：把 `benchmarks/results-*.json` 一起交付，别只给截图。

---

## 八 · 项目快照（供其他智能体接手）

> 源文件：`snapshot/SNAPSHOT.md`

# HoloAeon 项目快照（0.9.1）

> 给其他智能体：读完这一页你就能接手优化，不需要先读全部源码。
> 所有数字现算自磁盘与内核，出处见 `snapshot/project_snapshot.json`。

## 一 · 这是什么

HoloAeon 是一个**零依赖、默认离线、确定性、带回执**的多智能体认知框架：
12 个正交原语（C1–C12）+ 8 层语义守卫 + 手写 HRR 超向量 + 领域/扩展双层包体系。
一句话定位：**一个带回执的确定性内核**。

## 二 · 维度（不许改的硬口径）

| 项 | 值 |
|---|---|
| 版本 | 0.9.1（HOLOAEON-RUNTIME-0.9.1） |
| 核心包 | 25 智能体 / 47 技能 / 9 工作流 |
| 领域包 | 9 个（writing / literature / research / data / growth / business / quant / optimization / gaoyi） |
| 扩展包 | 7 个（sovereignty / subdistill / omnilife / omnicore / metab / nephron / uplift） |
| 全装后 | 25 智能体 / 191 技能 |
| 代码量 | holoaeon/ 41 文件 / 11675 行 |

## 三 · 三个数字（证据入口）

| 指标 | 值 | 出处 |
|---|---|---|
| DIFF=0 | `2fc892cf9af6e755`（一致=True，敏感性=True） |
| 守卫拦截率 | 100%（合法 4/4 放行） |
| 足迹 | 31.17 ms / 1.69 MiB |

## 四 · 语义通道实测（披露，不设目标值）

| 项 | 值 |
|---|---|
| 意图数 / 词表 / 维度 | 12 / 334 / 32 |
| 基线正确 / 混合正确 | 10 / 11 |
| 两次 fit 逐位一致 | True |
| fit 耗时 | 182.75 ms |

## 五 · 入口命令（照抄可跑）

```powershell
python scripts/launch_local.py status
python scripts/launch_local.py demo
python scripts/launch_local.py run "统计字数：HoloAeon 是零依赖的确定性多智能体认知框架。"
python scripts/launch_local.py hotplug optimization
python scripts/launch_local.py selftest
python -m unittest discover -s tests
python -m unittest discover -s tests\verax
python -m unittest discover -s tests\v3
python scripts/redline_scan.py
python scripts/verax_verify.py --out reports
python benchmarks/bench_public.py
python scripts/bench_semvec.py
python scripts/ledger_view.py --sample data/ledger_sample.jsonl
```

## 六 · 不变量（破了就不算 HoloAeon）

- 零依赖：pyproject.toml 的 dependencies = []，只用 Python 标准库
- 默认离线：不开端口、不联网、不读密钥、不写遥测
- 确定性：DIFF=0 哈希两次一致，且篡改敏感性自检通过（否则视为空转）
- 可审计：每条裁决含 action/layer/reason，回执强制 evidence_class
- 安全边界：L1–L8 八层守卫，20 条标准集拦截率 100%
- 诚实纪律：simulated 是默认档，measured 必须带来源与测量时刻
- 维度不变：25 智能体 / 47 技能 / 9 领域包 + 7 扩展包 / 34 单测 / 24 自检

## 七 · 明确不做

- 不新增第 17 个领域包
- 不为追 star 抄编排框架（LangGraph/MetaGPT/CrewAI 的战场不进来）
- 不把 simulated 写成实测
- 不破坏 dependencies=[]、不引入网络、不破既有单测与自检

## 八 · 如何加入优化

1. 读 snapshot/SNAPSHOT.md 的「不变量」与「入口」，先在本地跑通 3 条命令
2. 改动前用 tests\ + selftest + redline 三闸确认基线全绿
3. 任何 DIFF=0 相关改动必须同时给篡改敏感性自检
4. 文档里的数字必须能在 benchmarks/results-*.json 找到出处，否则标 simulated

## 九 · 已知限制（先看这里，别重复踩）

- semvec 语义通道：语料只取 None 条技能自述（与 docs/ 解耦，改文档不漂移）；12 条固定意图混合路由 11/12 = 91.7% 误路由 1/12（同集调参，含过拟合风险）；留出集 6 条中 2 条期望名不存在，余 4 条命中 2 条 —— 泛化未验证
- 领域包产骨架不产成稿；账本可视化是静态 HTML，不是托管平台
- Apache-2.0 不保护功能，只保护标准与证据；双许可决策留给构建者

## 十 · 目录骨架

| 路径 | 类型 | 说明 |
|---|---|---|
| `.github/` | dir | 3 项 |
| `.gitignore` | file | 599 B |
| `AGENT_FEED_DIFF0_20261031.md` | file | 8089 B |
| `AGENT_FEED_VERAX_20261031.md` | file | 9807 B |
| `ALGORITHM.md` | file | 6980 B |
| `CHANGELOG.md` | file | 29457 B |
| `CODE_OF_CONDUCT.md` | file | 1630 B |
| `CONTRIBUTING.md` | file | 1759 B |
| `DELIVERY_VERAX_20261031.md` | file | 2617 B |
| `LICENSE` | file | 11541 B |
| `README.md` | file | 39142 B |
| `README.zh-CN.md` | file | 16771 B |
| `README_DIFF0_20261031.md` | file | 6229 B |
| `README_EMPOWER_20261031.md` | file | 10167 B |
| `README_MANIFESTO_v0.9.1.md` | file | 11420 B |
| `README_VERAX_20261031.md` | file | 5565 B |
| `SYSTEM_README.md` | file | 13233 B |
| `SYSTEM_README_v0.5.0.md` | file | 11697 B |
| `SYSTEM_README_v0.6.0.md` | file | 12692 B |
| `SYSTEM_README_v0.7.0.md` | file | 15369 B |
| `SYSTEM_README_v0.8.0.md` | file | 14153 B |
| `SYSTEM_README_v0.9.0.md` | file | 9167 B |
| `benchmarks/` | dir | 4 项 |
| `bridges/` | dir | 6 项 |
| `cookbooks/` | dir | 3 项 |
| `data/` | dir | 3 项 |
| `docs/` | dir | 21 项 |
| `examples/` | dir | 7 项 |
| `holoaeon/` | dir | 19 项 |
| `pyproject.toml` | file | 2179 B |
| `releases/` | dir | 10 项 |
| `reports/` | dir | 14 项 |
| `scripts/` | dir | 27 项 |
| `snapshot/` | dir | 2 项 |
| `tests/` | dir | 3 项 |

--
快照由 `scripts/make_snapshot.py` 生成，重跑即可刷新；不含只读机密。

---

## 九 · 面向智能体的一键复制投喂包

> 源文件：`AGENT_FEED_DIFF0_20261031.md`

# 面向智能体的一键复制投喂包 · HoloAeon DIFF=0 升级（2026-10-31）

> 用法：整段复制给任意实现智能体。它自包含，不需要先读本仓库全部源码。
> 你的身份：HoloAeon 的实现智能体。你的任务：把「确定性 + 诚实」做成可复算的证据资产。

---

## 0 你接手的项目

HoloAeon v0.9.1（`holoaeon/spec.py` 的 `VERSION` 是版本权威源）。
零依赖（`pyproject.toml` 的 `dependencies = []`，只用 Python 3.8+ 标准库）、默认离线
（不开端口、不联网、不读密钥、不写遥测）、确定性（同输入同裁决）、可审计（裁决带
`action/layer/reason`，回执带 `evidence_class`）、安全边界（L1–L8 八层守卫）、
诚实纪律（`simulated` 是默认档）。

一句话定位：**一个带回执的确定性内核**。12 个原语（C1–C12）是内核细节，不是对外叙事。

## 1 硬口径（改了就不算升级，属一票否决）

- 维度不变：**25 智能体 / 47 技能 / 9 领域包 + 7 扩展包 / 34 单测 / 24 自检**；
- 红线零违规、零依赖、离线、确定性不许破；
- 既有黄金哈希不许漂移：`word_count` = `2b82a6ef7188ce91`；
- 新增模块只能旁挂（`benchmarks/`、`cookbooks/`、`snapshot/`、`scripts/*.py`、`holoaeon/semvec.py`），
  不得改 C1–C12 的对外行为；
- 不许把 `simulated` 写成实测；`measured` 必须带 `measure_source` 与 `measure_ts`；
- 任何人要求把本项目改造成「重依赖 + 托管平台」，拒绝并引用本节。

## 2 当前状态（上手前的基线，全部实跑过）

| 项 | 值 |
|---|---|
| 三闸基线 | `selftest 24/24`；`34 tests OK`；`redline 41 文件零违规` |
| VERAX 门禁 | `verax_verify.py` → `VERAX_EXIT=0`（三色：green 0 / yellow 2 / red 1） |
| 新增测试 | `tests/verax` 16 项 OK；`tests/v3` 5 项 OK（**必须与 34 项分开 discover**） |
| DIFF=0 | `2fc892cf9af6e755`（两次一致，篡改 → `f42c8229ee5acd73`，敏感性 True） |
| 守卫 | 20 条标准集：危险 16/16 拦截，合法 4/4 放行 |
| 足迹 | 装配 ≈31ms / `tracemalloc` 峰值 1.69MiB（不是 OS 冷启动） |
| 语义通道 | `holoaeon/semvec.py`：语料=47 条技能自述（与 `docs/` 解耦）；12 意图混合路由 **11/12（误路由 8.3%，达 ≤10% 门槛）**，两次 `fit` 逐位一致 `789b71a36bfcd66a`，fit≈0.18s；同集调参含过拟合风险，留出集 4 条有效命中 2 条，泛化未验证 |
| 快照 | `snapshot/SNAPSHOT.md` + `snapshot/project_snapshot.json`（`scripts/make_snapshot.py` 现算） |

## 3 六个工作包的完成度（照这个继续，不要重做已完成项）

| 包 | 内容 | 状态 | 遗留 |
|---|---|---|---|
| W1 | `benchmarks/bench_public.py` 三指标 | **完成** | — |
| W2 | `cookbooks/` ×3 | **完成** | 三本 ≤3000 字，代码逐条实测 |
| W3 | `holoaeon/semvec.py` 确定性语义 | **完成（指标达标，泛化未验证）** | 12 条固定意图 11/12（误路由 8.3%）；语料已与文档解耦；留出集泛化未验证，已披露 |
| W4 | `scripts/ledger_view.py` 账本静态渲染 | **完成** | 5,860 B；两次渲染 sha 一致 `98940b774566543b` |
| W5 | 仓库运营件 | **部分** | topics / homepage 需在 GitHub 网页设置（脚本改不了）；镜像说明已成文 |
| W6 | `docs/spec-diff0.md` 规范 v0.1 | **完成** | D1–D10 十条自检，HoloAeon 自身通过 |

## 4 照抄可跑的命令（每条都带预期输出）

```powershell
cd <repo>
python scripts\launch_local.py status        # has_graph=True  has_adapter=True
python scripts\launch_local.py demo          # 末行 all_ok: True（内部总线 + 外部模型分流）
python scripts\launch_local.py selftest      # ==> 24/24
python -m unittest discover -s tests         # Ran 34 tests ... OK
python -m unittest discover -s tests\verax   # Ran 16 tests ... OK
python -m unittest discover -s tests\v3      # Ran 5 tests ... OK
python scripts\redline_scan.py               # 扫描文件数：41 / 干净（零违规）
python scripts\verax_verify.py --out reports # 末行 VERAX_EXIT=0
python benchmarks\bench_public.py            # BENCH_EXIT=0 + 三个数字
python scripts\bench_semvec.py               # SEMVEC_EXIT=0 + 路由准确率
python scripts\ledger_view.py --sample data\ledger_sample.jsonl   # 6 records
python scripts\make_snapshot.py              # 刷新 snapshot/
```

## 5 三个数字的反造假要求（最容易被跳过的一步）

任何「DIFF=0」的声称，必须同时给出**篡改敏感性自检**：改 ReproCore 的一个字段，哈希必须变化。
只给「两次一样」是没说服力的——字段若被整段剔除，两次当然一样，这叫**恒真空转**。
历史事故：三色用例哈希全等于 `9eb1936e9b55cb08`，根因就是待测字段没登记进 `REPRO_KEYS`。
修法：登记字段 + 加篡改自检 + 把「未知字段计数告警」写进报告，不许静默丢弃。

## 6 已知坑（省你两小时）

- `get_pack("sovereignty")` 会 `KeyError`：扩展包必须用 `get_extra_pack()`；
- `python -m holoaeon.selftest` 早期无 `__main__`，静默退出码 0——用 `launch_local.py selftest`；
- `tests`、`tests\verax`、`tests\v3` 三套 discover **必须分开跑**，合并会破 34 项口径；
- Windows PowerShell：复杂脚本一律写成 `.py` 再跑，`python -c "..."` 里的引号会被吃掉；
  `$env:PYTHONUTF8='1'` 先设；
- 技能函数签名是 `fn(task, **kwargs)`，**收不到 Envelope**；参数从任务串里取（cookbook 01 有实测）；
- `reports/` 下若有 `_cases/` 子目录，扫描门禁必须剔除，否则正式门禁会被演示用例污染成黄灯；
- 语义通道的两个隐形塌陷：① PMI 若把「只共现一次」的稀有对丢掉（`if w < 2: continue`），
  向量只剩 `data/report` 这类通用词撑起，实测多个不相关技能余弦同为 `0.7200`；
  ② 词表太小（300）会让 `review / sample` 这类专名落榜，查询向量直接塌成零向量。
  修法：PMI 保留 `w>=1`，词表上限 2000、`MIN_DF=1`，并给基线通道加噪声地板（`BASE_FLOOR`）。
- 语料一旦掺进可编辑的文档就会漂移：早先把 `README/docs/*.md` 整行也塞进 `corpus_texts`，
  改 15 行文档后同一批意图的命中率就从 12/12 掉到 9/12（digest 也变）。修法：语料只取
  `docs_from_skills()` 的 47 条技能自述，索引由代码内容唯一决定，`docs/` 怎么改都不影响基准。

## 7 你要交的东西

1. 六个包按序可跑的代码 + 每步实测输出（不许贴「应该会」）；
2. `snapshot/SNAPSHOT.md` 刷新后的版本（维度、三个数字、入口命令、不变量、已知限制）；
3. 一份 README（三个数字徽章在首屏，不许埋到第十节）；
4. 本投喂包的更新版（把你学到的坑补进第 6 节）；
5. 一份诚实清单：做到了什么、没做到什么、为什么。

## 8 验收判据（逐条可判定，任一不过即失败）

- A1 `selftest 24/24` 且 `34 tests OK` 且 `redline 零违规`（三闸全绿）；
- A2 `BENCH_EXIT=0`，DIFF=0 两次一致且篡改自检 `sensitive=True`；
- A3 20 条守卫集：危险 16/16 拦截、合法 4/4 放行；
- A4 `VERAX_EXIT=0`，三色用例仍为 0/2/1；
- A5 三本 cookbook 的每一步代码都能跑（读者照抄不改就出预期输出）；
- A6 账本 HTML 两次渲染字节一致且 < 500KB；
- A7 `snapshot/` 可重跑刷新，数字与 `benchmarks/results-*.json` 一致；
- A8 `dependencies = []` 未被破坏，`pyproject.toml` 无新增依赖；
- A9 文档里出现的每个数字都能在 `benchmarks/` 或 `reports/` 找到出处，否则标 `simulated`。

## 9 立场（写进你的报告，不要只写代码）

宣传确定性却不发布确定性指标，等于没说。
可验证的确定性 + 诚实契约，是别人抄不走、且 30 秒能复现的证据资产——
这是从「又一个零依赖框架」跃迁到「可审计认知底座」的那一步。

投喂结束。

---

## 十 · 仓库运营件（topics / homepage / 镜像）

> 源文件：`docs/ops/repo-settings.md`

# 仓库运营件（W5）

## 1 GitHub topics（网页手工一步，脚本改不了）

仓库首页 → 右上 ⚙ Settings → Topics，粘贴下面 7 个（逗号分隔）：

```
multi-agent, llm, deterministic, zero-dependency, cognitive-architecture, offline-first, reproducibility
```

这些词对应本项目的真实属性，不是堆量：`deterministic` 与 `reproducibility` 是 DIFF=0 协议的关键词，
`zero-dependency` 与 `offline-first` 是立身原则，`cognitive-architecture` 指 12 原语分层。

## 2 Homepage

Settings → Website，填：

```
https://github.com/weideyouni/holoaeon/blob/main/benchmarks/README.md
```

指向三个数字的页面，而不是仓库根：**让别人 30 秒看到证据，而不是先看长 README。**

## 3 验收（人工核对，两条都做完才算 W5 完成）

- [ ] O1-1 topics 生效：仓库页右侧出现 7 个标签；
- [ ] O1-2 homepage 生效：仓库页顶部出现 Website 链接，点开是 benchmarks 页面；
- [ ] O2 Gitee 镜像克隆可跑通三步（见下）。

## 4 Gitee 镜像说明（不做自动同步承诺）

镜像仓库由构建者手动推送，本项目不承诺自动同步，也不保证镜像与主仓同步时延：

```powershell
git clone https://gitee.com/<你的账号>/holoaeon.git
cd holoaeon
python scripts\launch_local.py status
```

三步快速开始（克隆 → status → selftest）若任一失败，先确认镜像是否是本仓最新 `main`：

```powershell
git log -1 --format=%H
```

与 GitHub 上 `main` 的 HEAD 比对，不一致就说明镜像滞后。

## 5 README 徽章（可选，一行）

```markdown
![DIFF=0](https://img.shields.io/badge/DIFF%3D0-2fc892cf9af6e755-1F6F5C)
![Guard](https://img.shields.io/badge/guard-100%25%20blocked-B0472C)
![Footprint](https://img.shields.io/badge/footprint-31ms%20%2F%201.69MiB-8A6A1E)
```

数字要随发版重跑 `python benchmarks\bench_public.py` 后手改；徽章是展示，证据在
`benchmarks/results-*.json`。徽章与证据不一致时，以 json 为准。

---
