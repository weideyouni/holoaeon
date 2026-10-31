# 确定性 Agent 运行时规范 v0.2（草案）

> 取代 v0.1（`docs/spec-diff0.md`）的**新增条款集**。v0.1 的 §1–§7 全部继续有效，
> 本文件只写 v0.2 的增量与重排：§5 升级为行级证据协议，§7 新立 REPRO_CORE，
> §8 新立 fail-loud 硬条款，§9 汇总已知限制（含 V2 新数）。
> 全部条目 `evidence_class=simulated`：仿真 ≠ 证明，碳基终裁。

- 文档版本 `0.9.2`，运行态版本仍 `0.9.1`（见 §1.2 为什么）
- 生效日 2026-11-01
- 实现侧入口：`scripts/verax_verify.py`（门禁）、`scripts/repro_core_emit.py`（证据）、
  `scripts/bench_semvec_kfold.py`（泛化）、`holoaeon/audit/mutation.py`（篡改）

## 1 范围与 v0.2 变更

### 1.1 变更清单（只增不改）

| 编号 | 变更 | 落点 | 维度影响 |
|---|---|---|---|
| C-1 | 自检从"回归相等"升级为"生成反例"：随机单点篡改 5 处，哈希必变 | `holoaeon/audit/mutation.py` + `--mutate 5` | 单测 +5（34 不变），自检 25 不变 |
| C-2 | semvec 引入 5 个问法层的分层留出集（5×47=235），报 mean/std | `scripts/bench_semvec_kfold.py` + `data/semvec_corpus_v2.json` | 旁挂脚本，0 |
| C-3 | 三类证据 + 账本/守卫/semvec/篡改统一为逐行可哈希 JSONL | `scripts/repro_core_emit.py` + `reports/repro_core.jsonl` | 0 |
| C-4 | 三条硬红线任何命中必须 red，禁止 advice 降级 | `holoaeon/audit/verdict_policy.py` + 本文件 §8 | 0（不挂内核） |
| C-5 | 刷新 V2 快照与徽章 | `snapshot/SNAPSHOT_V2.md`、`snapshot/project_snapshot_v2.json` | 0 |

### 1.2 为什么不改 `VERSION`

`holoaeon/spec.py` 的 `VERSION` / `RUNTIME_ID` 会写进每条回执并参与 ReproHash。
改动它等于让 DIFF=0 黄金值 `2fc892cf9af6e755` 与全部 5 条 golden 同时漂移，
与"V1 黄金值不许漂移"的硬口径直接冲突。
故 V2 采用**双版本号**：运行态保持 `0.9.1`，文档/快照/徽章用 `DOC_VERSION=0.9.2`。
这条是取舍，不是遗漏：升级的是赋能包与协议，不是运行态语义。

## 2 术语

| 术语 | 定义 |
|---|---|
| 物理量 | 时间、耗时、内存、机器规格等随环境变化的量；**不进哈希** |
| 规范对象 | `canonicalize(obj)` 后的对象：剔除物理量、dict 列表稳定排序 |
| ReproHash | `sha256(canonical_json(规范对象))[:16]` |
| 黄金值 | 冻结在 `holoaeon/audit/golden/*.json` 的 `expected_reprohash` |
| 篡改点 | 规范对象上的一个标量叶子路径，改一处即一个新对象 |
| 敏感性 | 任一篡改点都让 ReproHash 改变；否则哈希对内容不敏感 |
| REPRO_CORE 行 | 一条证据：evidence / evidence_class / measure_source / measure_ts / golden_value / observed_value / verdict / verdict_hash |
| fail-loud | 确定性失败不许静默：命中硬红线必须红，且不许被建议降级 |

## 3 DIFF=0 哈希协议（沿用 v0.1 §3，值锁死）

固定 16 步 workload，两次各用全新内核，剔除物理量后规范化求 sha256 前 16 位，
两次相同即 DIFF=0。

| 项 | 冻结值 | 状态 |
|---|---|---|
| run1 / run2 | `2fc892cf9af6e755` | 2026-11-01 复算一致 |
| 篡改后（改任务原文一个字） | `f42c8229ee5acd73` | 敏感性 True |
| 规范化保留顶层键 | `runtime_id, steps` | 不变 |

## 4 理由码规范（沿用 v0.1 §4）

裁决必须带 `action / layer / reason` 三元组，理由码取自守卫八层枚举，
不允许自由文本替代码值。

## 5 证据防漂移协议（v0.2 升级为行级）

v0.1 只要求"证据带来源与时刻"，v0.2 追加三条：

- **R-1 行级可哈希**：每条证据自带 `verdict_hash`，其算法固定为
  `sha256(规范化去掉 measure_ts 与 verdict_hash 后的整行)[:16]`。
  物理量不得写入被哈希的字段（`build_ms` 这类逐次变动的量只打印不落行）。
- **R-2 独立成行**：`reports/repro_core.jsonl` 与 `reports/attestation.jsonl` 并存，
  不合并；前者是证据链，后者是裁决书。
- **R-3 复算即校验**：`python scripts\repro_core_emit.py --check reports\repro_core.jsonl`
  逐行比对哈希，任一行不一致即退出 1。

## 6 兼容性分级（沿用 v0.1 §6，追加 V2 级）

| 级 | 含义 | V2 归属 |
|---|---|---|
| A 内核兼容 | 不改 C1–C12 对外行为 | W7/W9/W10/W11 全部 |
| B 旁挂兼容 | 新增脚本/文档，内核不认识它 | W8 kfold、W10 策略模块 |
| C 破坏性 | 改原语语义或黄金值 | **V2 禁止**（无一条落入） |

## 7 REPRO_CORE 多模态证据统一协议（v0.2 新立）

把"三类证据各跑一个脚本、由 README 手抄一段"改为"一份文件、逐行可复算"。
当前实现行数 **10**（要求 ≥6）：

| evidence | golden_value | observed（2026-11-01 实测） | verdict |
|---|---|---|---|
| `diff0_hash` | `2fc892cf9af6e755` | `2fc892cf9af6e755` | pass |
| `mutation_sensitivity_v1` | `f42c8229ee5acd73` | `f42c8229ee5acd73` | pass |
| `guard_block` | `16/16` | `16/16` | pass |
| `guard_allow` | `4/4` | `4/4` | pass |
| `word_count_golden` | `2b82a6ef7188ce91` | `2b82a6ef7188ce91` | pass |
| `ledger_sha` | `98940b774566543b` | `98940b774566543b`（5,860 B / 6 记录） | pass |
| `semvec_digest_v1` | `789b71a36bfcd66a` | `789b71a36bfcd66a`（两次 fit 逐位相同） | pass |
| `mutation_selftest_v2` | `5/5` | `5/5` | pass |
| `semvec_kfold_std` | `<=0.05` | `mean=0.9957 std=0.0085 folds=5` | pass |
| `footprint` | n/a（物理量） | `agents=47 skills=47 peak=1.69MiB` | info |

条文：证据行只许有两种 verdict 取值面——`pass/fail`（有黄金值的断言）与
`info`（无黄金值、只披露）。新增 `warn` 仅用于"有阈值但允许黄灯"的项
（当前 kfold 为 pass，未触发）。

## 8 fail-loud 条款（v0.2 新立，硬约束）

### 8.1 三条硬红线

任何一条命中，裁决必须是 `red`，CI 退出码必须是 **1**（不许 2）：

| 编号 | 规则 ID | 触发条件 | 为什么不可降级 |
|---|---|---|---|
| P1 | `diff0_drift` | 任一黄金任务的 ReproHash ≠ 冻结值 | 确定性是对外承诺；漂移即承诺失效 |
| P2 | `mutation_insensitive` | 篡改自检 `changed < mutations`（任一篡改点哈希未变） | 哈希不敏感时 DIFF=0 只是恒真空转 |
| P3 | `golden_unfrozen` | 任一 golden 缺 `expected_reprohash` | 无冻结值即无参照，等于放弃断言 |

### 8.2 降级禁止

- 裁决一旦为 `red`，不允许任何 `advice` / `yellow` 覆盖；`enforce()` 只许"变红"。
- 调用方若想把 `red` 写成别的结论，`assert_no_downgrade()` 直接抛 `ValueError`。
- 策略模块 `holoaeon/audit/verdict_policy.py` **不挂内核**：它不改变任何技能行为，
  只约束"裁决怎么形成"，因此不构成维度变化。

### 8.3 自动化落地

`scripts/verax_verify.py` 第 7 步（`[7/7] 策略`）把三条规则的输入显式化：
`diff0_drift = any(golden_match is False)`、
`mutation_sensitive = mutation.sensitive`（`--mutate 0` 时视为未评估、记 True 并披露）、
`golden_frozen = 5 条 golden 全带 expected_reprohash`。
命中即 `conclusion=red`、`VERAX_EXIT=1`。

### 8.4 为什么这条属于"对齐"

确定性声称本身就是一种对齐声明：如果运行时在静默改变结果却仍报"绿"，
外部就无法区分"稳定"与"稳定地错"。故确定性失败必须 loud。

## 9 已知限制（v0.2，含 V2 新数）

- **L-1 kfold 的 std 不是泛化能力**：5 折是**问法风格分层**（原句/口语/客气/书面/
  追加话术），每折 47 条覆盖全部技能各一次；semvec 索引只在技能自述上 `fit`，
  问句从不进语料 → 无训练泄漏，但也因此 std 只反映"路由对问法风格的敏感度"。
  实测 `mean=0.9957 std=0.0085`（limit 0.05）为绿。
- **L-2 P@1 虚高来自术语同形**：235 条语料中 47 条基准问句含规范术语
  （如"夏普比率""共轭梯度法"），词面通道即可命中，故混合 P@1 达 99.57%。
  跨词汇能力以 `anchor_v1_intents` 为准：V1 12 条改写意图 **11/12=91.7%**，
  未提升、也未调参刷成 12/12（会破坏泛化诚实性）。
- **L-3 两条稳定未命中**：`拆解一下这个任务`（语义层误判同类）、
  `设计实验的样本量`（误判 `design_experiment`）。V2 不复赛调参，如实保留。
- **L-4 篡改自检的抽样规模**：默认 5 点（种子 `20261101`），不是穷举；
  它证明"抽样点必变"，不证明"所有叶子都敏感"。穷举版可跑 `--mutate N` 调大。
- **L-5 足迹是物理量**：`build≈31.67ms / peak=1.69MiB` 随机器浮动，
  不进任何哈希，仅作披露。
- **L-6 YAML 缺失**：本机 Python 无 PyYAML，任何 `.yaml` 解析都不能作为门禁前置。

## 10 V2 自检清单（实现方逐条打勾）

- [x] 三套单测分开跑：`tests` 34 OK / `tests\verax` 21 OK（16+5）/ `tests\v3` 5 OK
- [x] 自检 25/25（`launch_local.py selftest`，末行 `G25 persona_quartet — 8/8`）
- [x] DIFF=0 = `2fc892cf9af6e755`，篡改敏感性 True
- [x] `--mutate 5` → `mutations=5 changed=5 sensitive=True`
- [x] kfold 5 折跑通，std ≤ 0.05
- [x] `repro_core.jsonl` ≥6 行（实为 10 行），四字段非空，`--check` 全行一致
- [x] fail-loud 三条规则可命中并被降级禁止（策略模块 + 门禁第 7 步）
- [x] `dependencies = []` 未破；`pyproject.toml` 无新增依赖
- [x] V1 golden 全保留：5 条 reprohash + ledger sha + semvec digest(v1)
- [x] 新增数字均有出处（`benchmarks/`、`reports/`、脚本 stdout）

## 11 立场

V1 完成了「确定性 + 诚实」的可证据化。V2 要做的是「对证据本身负责」：
不让任何人靠静默黄灯逃避对齐失败，不让 semvec 靠过拟合装样子，
不让证据链靠手抄 README 漂移。确定性声称本身就是一种对齐声称。

潮起开门，潮落闭嘴。
