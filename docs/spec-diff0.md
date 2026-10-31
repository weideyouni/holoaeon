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
