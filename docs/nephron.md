# NEPHRON 肾单位层 · P0 设计说明（认知账本 + 回放器）

> 版本 `NEPHRON-P0-V1.0`（对应工程包 `holoaeon.packs.nephron_pack`，内核 v0.8.0）
> 日期 2026-10-30 · 密令 **潮起开门，潮落闭嘴**
> 本文按投喂稿 §13 六项交付物组织；结构化内容用表格；每条规范性陈述都可判定；
> 每条关键设计补一句"它保护了哪条立场"。
> 四条立场：**S1 不扩大物理上限 / S2 取舍必须留痕 / S3 代价必须显式 / S4 可逆优先**。

---

## 1. 定位与目标

NEPHRON 负责"认知容量与记忆代谢"，其核心立场是 **不扩大任何物理上限，只优化有限容量的分配，并把每次取舍记成可回放的账**。
P0 只做观测：**记录、不决策、不改行为**。它的价值不在"省了多少"，而在"事后能证明当时为什么这么取舍"。

| 项 | P0 做什么 | P0 明确不做什么 |
|---|---|---|
| 记录 | 上下文与槽位的占用、命中、压缩、淘汰、外部调用、成本与可信度估计 | — |
| 回放 | 给定任意历史 trace 重建任意 tick 的窗口构成与决策输入 | 不重建模型实际看到的文本 |
| 行为 | 关闭账本后系统输出与开启前逐字节一致（由宿主 CI 断言） | 不做分页 / 压缩 / 淘汰 / 预算控制 |

它保护了哪条立场：**S1**（观测层不扩容）与 **S2**（每次取舍都留痕）。

---

## 2. 审视与修正（投喂稿内部的 10 处冲突 + 3 处修正）

投喂稿要求"若发现歧义或内在冲突，先列出问题并给出两种消解方案，选其一继续并标注"。
以下是逐条审视结果，全部落进 `CONFLICTS`（N1–N10）与 `FIXES`（F1–F3），由 `G23` 断言条数与合法性。

### 2.1 十处冲突

| # | 冲突点 | 方案 A | 方案 B | 采用 | 理由 |
|---|---|---|---|---|---|
| **N1** | §6 要求"异步队列 + 落盘批量刷写"，与本项目红线"不起线程、不写盘"冲突 | 包内实现队列与落盘 | 包只给队列语义与丢弃计数口径，队列实例化与落盘归宿主 | **B** | 红线是硬约束；把 I/O 交给宿主后，"队列满必须丢弃并计数"仍可判定 |
| **N2** | §2"任意历史 tick 可回放"与 §6 三档开关 `sampled` 冲突（采样后账本不完整） | 三档都宣称可回放 | off / sampled 不可完整回放，只有 full 可回放；sampled 只能回放已采样 tick | **B** | 抽档靠插值补齐等于伪造账本；A3 的字面要求只有 full 能满足 |
| **N3** | §5"只追加、不可改写"与 §9"一键擦除"冲突 | 擦除 = 原地覆写或删除记录 | 擦除 = 内容摘要替换为 `ERASED:<hash>` + 账本尾部追加擦除记录 | **B** | 擦除自身成为一条可回放事件，隐私与只追加同时成立 |
| **N4** | §5.3 有 `compression_ratio` 字段，§3 却把"压缩"列为非目标 | 记录上游的压缩比（若有） | 字段保留，P0 恒为 `null` | **B** | P0 无压缩即无压缩比；不把别处的数字冒充本层观测 |
| **N5** | §7 规则允许 `UNKNOWN` 兜底，但理由码表内没有 `UNKNOWN` | 把 `UNKNOWN` 加入固定表 | `UNKNOWN` 作保留码不入表，合法但单独计数并告警 | **B** | 入表等于把"归类失败"伪装成正常码；单列计数才看得见归类能力退化 |
| **N6** | §5.3 主键 `(tick, seq)` 与 §12"时钟回跳"冲突 | 照写，允许乱序 | 设水位线：`tick` 小于已见最大值即拒绝追加，记 `APPEND_REJECT_CLOCK_REGRESSION` | **B** | 只追加要求时间轴单调；回跳必须显式拒绝并留痕 |
| **N7** | A1"逐字节一致"与"额外开销需实测"都不是纯函数可证 | 包内给出"已通过" | 只产出断言契约，状态一律 `pending_human_measure` | **B** | 声称未测过的事即造假；契约 + 待测才能让 CI 真去跑 |
| **N8** | §5.1 `raw_len` 允许"token 或字符"，但只有一个字段 | 新增 `len_unit` 字段（破坏字段一致性） | 锁死单一口径：账本级 meta 声明 `len_unit="token"`，字符口径禁用 | **B** | 同字段两种单位会让所有长度比较静默失真 |
| **N9** | §7 理由码没有覆盖 `window_build` 事件的码 | 硬塞 `LAYER_HIT_SHALLOW` 等已有码 | 按"新增需评审"正式新增 `WINDOW_BUILD_COMPLETE`（R-01），仅作用于该事件 | **B** | 规格自己写了"新增需评审"，这里就该真走一次评审并留痕 |
| **N10** | §8 要输出槽位快照，但 §5.4 的 11 类事件里没有 `slot_alloc / slot_free`，回放器无从重演槽位 | 扩展事件枚举为 13 类 | 槽位快照改为账本旁挂周期快照，P0 回放取"最近快照 ≤ tick"并披露快照年龄 | **B** | 事件表是 P0 固定项；代价是 P0 只披露年龄、不重演槽位变化（写进已知限制，不假装已重演） |

### 2.2 三处修正（字段缺口与口径）

| # | 发现 | 修正 | 影响 |
|---|---|---|---|
| **F1** | `WindowManifest.summarized` 需要 `from_len/to_len`，`Page` 无长度快照字段；加字段会破坏"字段名必须一致" | 由 `page_summarize` 事件的 `delta{from_len,to_len}` 承载，`Page` 结构不动 | 回放只读 delta 即可还原摘要前后长度；摘要正文不入账本 |
| **F2** | `importance` 标 `float` 且"只记录既有值"，但既有系统可能不提供 | 缺失按 `0.0` 记录，并在 `page_validate` 的 `warnings` 标 `importance_absent_recorded_as_zero` | 下游若用 `importance` 排序，必须同时看 `warnings`，否则会把"未知"当"最低" |
| **F3** | "回放不依赖原文"若读成"必须存摘要正文"，会与隐私最小化冲突 | 账本只存 `payload_digest + raw_len + delta 长度`；**不存摘要正文** | 隐私面最小化；代价是无法回放"模型当时看到的实际文本"（列已知限制） |

### 2.3 审视结论

投喂稿的骨架是稳的：把 P0 严格限定为只读、并用 A1 逐字节一致锁死零侵入，是它能先进主干的前提。
需要修的只有两类：**一类是"把不可能自证的事写成可自证"（N7）**，
**另一类是"结构里少了一条能连起来的边"（N10、F1）**。两类都已在实现层落成可判定条目。

它保护了哪条立场：**S2**（修正必须留痕）；N1/N7 同时服务 **S4**（不自封、不越界）。

---

## 3. 字段字典（5 个结构 / 41 字段）

字段名、类型、范围与投喂稿 §5 保持一致；下表由 `field_dictionary` 与结构定义**同源生成**，不存在两处漂移。

### 3.1 Page（10 字段）

| 字段 | 类型 | 范围 | 必填 | 备注 |
|---|---|---|---|---|
| `page_id` | string | 非空 | ✓ | 稳定哈希：内容不变则 id 不变 |
| `origin` | enum | session / hebbian / skeleton / external | ✓ | 来源层，与 `layer_residency` 同口径 |
| `payload_digest` | string | 非空，≥8 字符 | ✓ | 载荷摘要；P0 不存原文 |
| `raw_len` | int | ≥0 | ✓ | 统一按 token 计（`RAW_LEN_UNIT`），字符口径禁用（N8） |
| `form` | enum | raw / summary / fingerprint | ✓ | 进入窗口时的形态 |
| `importance` | float | 0~1 | ✓ | 只记录既有值；缺失按 0.0 并告警（F2） |
| `last_tick` | int | ≥0 | ✓ | 最后一次进入窗口的 tick |
| `hit_count` | int | ≥0 | ✓ | 被检索命中累计 |
| `lineage_ref` | string | 血统引用或 `NONE` | ✓ | 无血统必须显式 `NONE`，留空即违规（A6） |
| `fingerprint` | string | 代际指纹 | ✓ | 与记录指纹同代际 |

### 3.2 SlotLedgerEntry（7 字段）

| 字段 | 类型 | 范围 | 必填 | 备注 |
|---|---|---|---|---|
| `slot_id` | string | 非空 | ✓ | 槽位标识 |
| `slot_class` | enum | trunk / reserve | ✓ | 主干槽 / 备用槽 |
| `occupant_page` | string\|null | page_id 或 null | ✓ | 空槽必须显式 `null` |
| `allocated_tick` | int | ≥0 | ✓ | 分配时刻 |
| `fragment_flag` | bool | true / false | ✓ | 是否碎片占位 |
| `owner_symbiont` | string\|null | 共生体 id 或 null | ✓ | 与 METAB 注册表对得上 |
| `reclaimability` | enum | cold / warm / hot | ✓ | 可回收性（P0 只观察，不改） |

### 3.3 LedgerRecord（13 字段，主键 `tick + seq`）

| 字段 | 类型 | 范围 | 必填 | 备注 |
|---|---|---|---|---|
| `tick` | int | ≥0 | ✓ | 主键第一段 |
| `seq` | int | ≥0，全局单调 | ✓ | 主键第二段；同 tick 多记录按 seq 排序 |
| `window_budget` | int | ≥0 | ✓ | 记录既有预算 |
| `window_used` | int | ≥0 | ✓ | 应等于 admitted 数（见 §6.2 一致性检查） |
| `layer_residency` | map | `{working,hebbian,skeleton,external} → int` | ✓ | 四键必须齐全 |
| `hit_rate` | float\|null | 0~1 或 null | ✓ | 无检索必须 `null`，不得填 0 |
| `compression_ratio` | float\|null | P0 恒 `null` | ✓ | 填入非空即判 schema 违规（N4） |
| `evicted_pages` | int | ≥0，P0 通常 0 | ✓ | 字段必须存在，即使为 0 |
| `external_calls` | int | ≥0 | ✓ | 只记次数，不含内容 |
| `cost_estimate` | float | ≥0 | ✓ | 既有值或显式 0 |
| `confidence_estimate` | float\|null | 0~1 或 null | ✓ | 无法估计必须 `null`，不得填 1.0 |
| `events` | list\<Event\> | 可为空 | ✓ | 本记录覆盖的事件 |
| `fingerprint` | string | 代际指纹 | ✓ | 与 Page 同代际 |

### 3.4 Event（4 字段，判别联合）

| 字段 | 类型 | 范围 | 必填 | 备注 |
|---|---|---|---|---|
| `type` | enum | 11 类（见 §4.1） | ✓ | 不得扩展；新增须评审 |
| `reason_code` | string | 27 码之一或 `UNKNOWN` | ✓ | **只携带一个主码** |
| `refs` | list\<string\> | page_id / slot_id / symbiont_id | ✓ | 可为空列表，但不得缺键 |
| `delta` | map\<string,number\> | 可选量化增量 | ✗ | 摘要长度走这里（F1） |

### 3.5 WindowManifest（7 字段）

| 字段 | 类型 | 范围 | 必填 | 备注 |
|---|---|---|---|---|
| `tick` | int | ≥0 | ✓ | 所描述 tick |
| `admitted` | list | `{page_id, score, reason_code}` | ✓ | 进入窗口的页 |
| `summarized` | list | `{page_id, from_len, to_len, reason_code}` | ✓ | 被摘要的页 |
| `rejected` | list | `{page_id, reason_code}` | ✓ | 被拒的页与理由 |
| `budget_before` | int | ≥0 | ✓ | 构建前预算 |
| `budget_after` | int | ≥0 | ✓ | 构建后预算 |
| `fingerprint` | string | 代际指纹 | ✓ | 本次构建所用代际 |

它保护了哪条立场：**S3**（`null` 与 `0` 严格区分；`hit_rate` 无检索就是 null）；N4/N8 服务 **S1**（不把别处数字冒充本层观测）。

---

## 4. 理由码表（27 码 + UNKNOWN 兜底）

### 4.1 事件类型与码族对应（11 类）

| 事件类型 | 码族 | 允许的码 |
|---|---|---|
| `window_build` | window | `WINDOW_BUILD_COMPLETE`（R-01 新增） |
| `page_admit` | admit | `ADMIT_HIGH_RELEVANCE` / `ADMIT_RECENT` / `ADMIT_LINEAGE_TRUSTED` |
| `page_summarize` | summ | `SUMM_LOW_VALUE_KEEP_TRACE` / `SUMM_BUDGET_PRESSURE` |
| `page_reject` | reject | `REJECT_REDUNDANT` / `REJECT_STALE_FINGERPRINT` / `REJECT_NO_LINEAGE` / `REJECT_BUDGET_EXCEEDED` / `REJECT_TRUST_RADIUS` |
| `layer_hit` | layer | `LAYER_HIT_SHALLOW` / `LAYER_HIT_DEEP` |
| `layer_miss` | layer | `LAYER_MISS_ALL` |
| `retrieval` | retrieval | `RETRIEVAL_DEEP_TAX` / `RETRIEVAL_TIMEOUT` |
| `eviction` | evict | `EVICT_LRU` / `EVICT_LOW_IMPORTANCE` / `EVICT_BUDGET` |
| `degradation` | degrade | `DEGRADE_CONFIDENCE_FLOOR` / `DEGRADE_COST_BUDGET` / `DEGRADE_DISTURB_BUDGET` |
| `fingerprint_mismatch` | fingerprint | `FINGERPRINT_MISMATCH_STALE` / `FINGERPRINT_MISMATCH_MODEL` |
| `budget_breach` | budget | `BUDGET_BREACH_LATENCY` / `BUDGET_BREACH_COST` / `BUDGET_BREACH_DISTURBANCE` |

判定规则：

1. 每个 Event **必须且只能**携带一个主 `reason_code`；出现 `sub_reason_code` 之类第二主码即违规。
2. 码必须属于该事件类型的码族；跨族使用即 `reason_code_type_mismatch`（违规）。
3. 无法归类时用 `UNKNOWN`：合法，但必须计入 `unclassified / alarm` 计数，**禁止静默吞掉**。
4. 新增码必须走评审并在 `CODE_REVIEWS` 留痕；R-01 是本版唯一一条。

### 4.2 已归类码总表（27）

| 族 | 码 | 族 | 码 |
|---|---|---|---|
| admit | `ADMIT_HIGH_RELEVANCE` | reject | `REJECT_NO_LINEAGE` |
| admit | `ADMIT_RECENT` | reject | `REJECT_BUDGET_EXCEEDED` |
| admit | `ADMIT_LINEAGE_TRUSTED` | reject | `REJECT_TRUST_RADIUS` |
| summ | `SUMM_LOW_VALUE_KEEP_TRACE` | layer | `LAYER_HIT_SHALLOW` |
| summ | `SUMM_BUDGET_PRESSURE` | layer | `LAYER_HIT_DEEP` |
| reject | `REJECT_REDUNDANT` | layer | `LAYER_MISS_ALL` |
| reject | `REJECT_STALE_FINGERPRINT` | retrieval | `RETRIEVAL_DEEP_TAX` |
| retrieval | `RETRIEVAL_TIMEOUT` | evict | `EVICT_LRU` |
| evict | `EVICT_LOW_IMPORTANCE` | evict | `EVICT_BUDGET` |
| degrade | `DEGRADE_CONFIDENCE_FLOOR` | degrade | `DEGRADE_COST_BUDGET` |
| degrade | `DEGRADE_DISTURB_BUDGET` | fingerprint | `FINGERPRINT_MISMATCH_STALE` |
| fingerprint | `FINGERPRINT_MISMATCH_MODEL` | budget | `BUDGET_BREACH_LATENCY` |
| budget | `BUDGET_BREACH_COST` | budget | `BUDGET_BREACH_DISTURBANCE` |
| window | `WINDOW_BUILD_COMPLETE` | — | （`UNKNOWN` 保留码，不入表） |

### 4.3 采集侧拒绝原因（不属于事件，单列一张表）

| 码 | 触发条件 |
|---|---|
| `APPEND_REJECT_CLOCK_REGRESSION` | `tick` 小于已见最大 tick（时钟回跳，N6） |
| `APPEND_REJECT_DUPLICATE_PK` | `(tick, seq)` 已存在 |
| `APPEND_REJECT_SCHEMA_INVALID` | 记录未通过结构校验（含 `compression_ratio` 非空这类） |

两张表**不得混用**：拒绝原因是"写入口"的判定，理由码是"窗内取舍"的判定。

它保护了哪条立场：**S2**（连"没能归类"和"没能写入"都要留痕）；R-01 服务 **S2**。

---

## 5. 采集与开关（零侵入方案）

### 5.1 三档开关

| 档 | 语义 | 默认 | 可回放范围 | 判定 |
|---|---|---|---|---|
| `off` | 完全不记录 | **是（默认）** | `none` | 系统行为不得有任何变化 |
| `sampled` | 按采样率记录（0.01 ≤ r ≤ 1.0） | 否 | `only_sampled_ticks` | 不得宣称可回放未采样 tick（N2） |
| `full` | 逐 tick 全记录 | 否 | `all_ticks` | 只有此档满足 A3 |

`sample_rate` 越界即 `sample_rate_out_of_range`；`mode` 不在三值内即违规。

### 5.2 接入点清单（11 个 hook，零侵入）

| hook | 产出事件 | 为什么在这里 |
|---|---|---|
| `before_window_build` | `window_build` | 取预算与驻留基线 |
| `after_window_build` | `window_build` | 出完整清单（进 / 摘要 / 拒） |
| `on_page_admit` | `page_admit` | 记分与理由码 |
| `on_page_summarize` | `page_summarize` | 记 `from_len/to_len`（走 delta） |
| `on_page_reject` | `page_reject` | 记拒因（必带码） |
| `on_layer_hit` | `layer_hit` | 记浅 / 深层命中 |
| `on_layer_miss` | `layer_miss` | 记全层未命中 |
| `on_retrieval` | `retrieval` | 记检索税与超时 |
| `on_eviction` | `eviction` | P0 通常 0，但接口必须在 |
| `on_fingerprint_check` | `fingerprint_mismatch` | 失配必须留痕（A7） |
| `on_budget_check` | `budget_breach` | 记延迟 / 成本 / 打扰越界 |

接入方式：hook / wrapper / 事件订阅；**禁止**在业务逻辑内散布记录代码（违反即零侵入失败）。

### 5.3 队列与刷写契约（宿主负责，N1）

| 项 | 契约 |
|---|---|
| 队列 | 异步队列 + 批量刷写由宿主实现；本包不起线程、不写盘 |
| 队列满 | 丢弃并入 `dropped_queue_full`；主流程不得阻塞 |
| 刷写失败 | 记 `failed_write` 并继续 |
| 序列化失败 | 跳过该条并记 `failed_serialize`；禁止写半条 |
| 时钟回跳 | 拒绝追加 + `APPEND_REJECT_CLOCK_REGRESSION` |
| 采集异常 | 一律静默降级为不记录，**不得抛到业务层** |

### 5.4 故障注入矩阵（4 类）

| 故障 | 期望行为 | 禁止行为 |
|---|---|---|
| 队列满 | 丢弃 + 计数 | 阻塞主流程 |
| 写失败 | 记 `failed_write` 并继续 | 抛到业务层 |
| 序列化失败 | 跳过 + 计数 | 写半条记录 |
| 时钟回跳 | 拒追加 + 拒绝原因 | 静默插入乱序记录 |

这四项的判定口径是契约，注入测试本身由宿主执行（本包标 `contract_only`）。

它保护了哪条立场：**S4**（任何故障只能是"少记"，不能是"改行为"）；**S3**（丢弃必须被计数）。

---

## 6. 回放器方案

### 6.1 四类输出

| 输出 | 函数 | 依赖 | 判定 |
|---|---|---|---|
| 窗口构成表 | `replay_window` | 该 tick 的 LedgerRecord 事件流 | 每次进 / 摘要 / 拒都带原码；无码即 `issues` |
| 槽位快照 | `replay_slots` | 旁挂周期快照（最近 ≤ tick） | 必须披露 `snapshot_tick` 与 `age_ticks`；年龄 > 32 标 `stale` |
| 决策输入 | `replay_inputs` | 该 tick 最后一条记录 | `hit_rate` 无检索为 `null`；`compression_ratio` 为 `null` |
| 变更时间线 | `replay_timeline` | 相邻 tick admitted 集合差 | 进出、拒绝数、指纹失配、代际变更逐 tick 对齐 |

硬性要求落实：

- 回放**只依赖账本**（records + 旁挂槽位快照），不读原始会话原文；`payload_digest` 与 `delta` 足以重建。
- 两种形态：人类可读 Markdown 表格（`examples/nephron_replay_report.md`）与机器可读 JSONL（`examples/nephron_ledger_sample.jsonl`）。
- 确定性：`replay_determinism` 归一化掉 `timestamp / ts / ingested_at / wall_clock / host / pid / elapsed_ms` 后连跑两次，哈希必须一致（A4）。

### 6.2 一致性检查

| 检查 | 判据 |
|---|---|
| `window_used` vs `admitted` 数 | 不等即 `issues`（`window_used` 应等于 admitted 数） |
| 摘要必须变短 | `to_len > from_len` → `summary_not_shorter` |
| 每行都有码 | admitted / summarized / rejected 任一行缺码 → `missing_reason_code:<page_id>` |
| 账本结构 | `seq` 单调、`(tick,seq)` 唯一、`seq` 无缺口、`tick` 不倒退 → `ledger_verify` |
| 锚点 | 提供 `anchor` 时链摘要必须相符；不符即 `anchor_mismatch` |

### 6.3 黄金样例（真实产物，不是手写样张）

| 文件 | 内容 | 生成方式 |
|---|---|---|
| `examples/nephron_ledger_sample.jsonl` | 7 条记录（tick 0–6，含一次代际切换） | `python scripts/make_nephron_sample.py` |
| `examples/nephron_replay_report.md` | 逐 tick 窗口构成 / 决策输入 / 时间线 / 槽位 / A1–A8 状态 | 同上，全部来自包内纯函数 |

样例实测：`records=7`、只追加核验通过、`chain_digest` 16 位、两次回放哈希一致、A1/A2 标 `pending_human_measure`。
这份样例的作用是**验证 §3 的 41 个字段够不够用**——结论是够，但需要一个旁挂槽位快照文件（N10）。

它保护了哪条立场：**S2**（回放出来的每次取舍都带原码）；**S3**（null 与 0 不许混）。

---

## 7. 与既有机制的接入点清单

| 机制 | P0 只读方式 | 允许 | 禁止（违规判据） |
|---|---|---|---|
| 矩阵 | 观察槽位占用与类别，读备用槽状态 | 记录 `SlotLedgerEntry` | 改槽位分配、重排主干槽 = 违规 |
| 心跳 | 以 `tick` 为唯一时间轴 | 记录 tick 边界上的取舍 | 引入第二套时钟、回跳照写 = 违规 |
| 皮肤 | 复用其权限 / 审计结论作为"是否可观测"的门 | 记录被皮肤拦下的拒绝码 | 绕过皮肤自行判定 = 违规 |
| 经络 | 记录通路上命中的层（浅 / 深） | 记 `layer_hit` / `layer_miss` | 改路由、加通路 = 违规 |
| 赫布协作场 | 只读协作权重对 `origin=hebbian` 页的影响 | 记进窗口的 hebbian 页 | 改权重基线 = 违规 |
| 血统账本 | 页的 `lineage_ref` 指向其条目；无则 `NONE` | 交叉引用 | 留空、伪造引用 = 违规（A6） |
| METAB 代谢层 | 复用`可再生/降级路径`口径判断"页可不可回收" | 读基因组字段 | 代 METAB 做准入判定 = 违规 |
| 亚学科蒸馏 | 页来源可为 `skeleton`（蒸馏产物） | 记 `form` 与长度 | 把蒸馏原文写进账本 = 违规 |
| 代际指纹 | `generation_fingerprint` 的联合哈希口径 | 失配必产事件 | 失配后静默复用 = 违规（A7） |

它保护了哪条立场：**S1**（只读，不接手别人的决策权）；皮肤 / 血统两行服务 **S2**。

---

## 8. 隐私与安全（P0 即需满足）

| 规则 | 允许 | 禁止 |
|---|---|---|
| 不存原文全文 | `payload_digest + raw_len + delta 长度` | 写 `payload` 原文 |
| 需存原文 | 显式开启 + 加密仓（宿主） | 默认开启 |
| 摘要生成 | 本地摘要器 | 把敏感字段送外部模型 |
| 本地摘要不可用 | 降级为"仅存哈希 + 长度" | 联网补摘要 |
| 外部调用记录 | 调用指纹 + 字节数 | 请求体明文 |
| 账本目录 | 最小权限（宿主执行） | 全局可读 |
| 一键擦除 | 内容摘要 → `ERASED:<hash>`，保留计数与指纹，追加擦除记录 | 删除记录、改写历史、抹掉计数 |

擦除的三条禁止项由 `erase_operation` 显式返回，不是文档口号。

它保护了哪条立场：**S4**（擦除也是追加一条记录，历史不留白）；**S2**（连"没记录什么"都写成规则）。

---

## 9. 测试清单与结果

| 类别 | 用例 | 结果 |
|---|---|---|
| 结构 | 41 字段齐备、字典与结构同源一致（`match_schema`） | 通过 |
| 结构 | 无血统留空 → `lineage_ref_empty_forbidden`；`NONE` 合法且标注 | 通过（A6） |
| 结构 | `compression_ratio` 非空 → schema 违规 | 通过（N4） |
| 结构 | `importance` 缺失 → 只告警不改错 | 通过（F2） |
| 写入 | 时钟回跳 → `APPEND_REJECT_CLOCK_REGRESSION` | 通过（N6） |
| 写入 | 主键重复 → `APPEND_REJECT_DUPLICATE_PK` | 通过 |
| 写入 | 含 `updated_at` 等改写字段 → 违规 | 通过（只追加） |
| 账本 | 正常序列通过；序号缺口 / tick 倒退 / 锚点不符均判失败并定位下标 | 通过（A5） |
| 理由码 | 27 码 / 10 族；跨族使用、双主码、非数值 delta 均违规 | 通过 |
| 理由码 | `UNKNOWN` 合法但 `alarm=1`；`window_build` 用 R-01 新码 | 通过（N5/N9） |
| 清单 | 进 / 摘要 / 拒计数正确；摘要变长判 `summary_not_shorter` | 通过 |
| 开关 | 默认 off；sampled 只回放已采样 tick；rate 越界报错 | 通过（N2） |
| 故障 | 4 类故障的期望 / 禁止行为成表 | 契约通过（注入待宿主执行） |
| 回放 | 窗口 / 槽位 / 决策输入 / 时间线四件套 | 通过（A3） |
| 回放 | 两次回放归一化哈希一致 | 通过（A4） |
| 回放 | sampled 账本拒绝回放；tick 不在账本明确报 `tick_not_in_ledger` | 通过（N2） |
| 槽位 | 最近快照 ≤ tick、年龄披露、超 32 标 stale、无快照报原因 | 通过（N10） |
| 隐私 | 6 条规则含"请求体明文"禁止项 | 通过 |
| 擦除 | `ERASED:<hash>` + 保留 5 字段 + 三条禁止 | 通过（N3） |
| 指纹 | 联合哈希（LoRA 排序归一）、缺项不许出指纹、失配必产事件 | 通过（A7） |
| 边界 | 零侵入只能 `pending_human_measure`；6 条非目标扫描 | 通过（N7） |
| 验收 | A1–A8 状态机：无证据只能是 pending；失败即 `reject` | 通过 |

工程侧实测（v0.8.0）：

| 项 | 结果 |
|---|---|
| 全套自检 | **23/23 组**（`G23 nephron` 62/62；`G15` 的 `25 agents / 47 skills` 未破） |
| 单元测试 | 25 tests OK |
| 红线扫描 | 33 个源文件零违规（含新包与新脚本） |
| 黄金样例 | 7 条记录、`verify_ok=True`、两次回放哈希一致 |
| 发行包 | 解压复跑 23/23，`VERSION 0.8.0`，`nephron 24/7/0` |

---

## 10. 已知限制（诚实清单）

| # | 限制 | 影响 | 为什么不隐藏 |
|---|---|---|---|
| L1 | **A1 逐字节一致未实测** | 零侵入目前是"契约 + CI 待跑"，不是结论 | 自封零侵入等于把风险留到上线 |
| L2 | **额外开销未实测** | `full` 档真实开销未知，文档不写虚构目标值 | 投喂稿明确"需实测"，任何数字都必须是测出来的 |
| L3 | **槽位不重演** | 只能给"最近快照 ≤ tick + 年龄"，中间的槽位变化不可见 | N10 的代价；P0 无槽位事件源 |
| L4 | **无法回放模型实际看到的文本** | 只有摘要长度与哈希，无摘要正文（F3 的代价） | 隐私最小化的必然结果 |
| L5 | **sampled / off 不可完整回放** | A3 只对 full 成立 | 不抽样插值，不伪造账本 |
| L6 | **内容级篡改需外部锚点** | 仅给链摘要；无锚点时只能发现结构异常（缺口 / 重复 / 倒退） | 记录里没有 hash 字段，结构不能加 |
| L7 | **reason_code 归类的上限** | `UNKNOWN` 只能计数，无法自动归类 | 自动归类会掩盖归类能力退化 |

---

## 11. P1 待办（明确不在 P0 内）

| # | 待办 | 前置条件 | 说明 |
|---|---|---|---|
| P1-1 | 打分公式各项定义（相关度 / 新近度 / 血统可信度 / 成本） | 字段稳定（本版已完成） | 这才是"决策"，P0 不做 |
| P1-2 | 窗口构建流程（排序、截断、摘要触发条件） | P1-1 | 同上 |
| P1-3 | 降级链声明格式 | P1-1 | 与 METAB 的降级路径口径复用 |
| P1-4 | 成对回归通过判据（假饲同构的对照） | P1-1 | 对应 METAB 的假饲口径 |
| P1-5 | 槽位变化重演（`slot_alloc / slot_free` 事件或快照差分） | 事件表评审 | L3 的正式解法 |
| P1-6 | `compression_ratio` 真正有值 | 引入压缩 | 本版恒 null |
| P1-7 | 摘要正文加密回放 | 隐私仓落地 | L4 的正式解法 |

---

## 12. 开放问题（本地无法定论）

| # | 问题 | 影响面 |
|---|---|---|
| O-1 | `window_used` 与 `admitted` 数是否恒等？投喂稿未定义"同一页既可摘要又进窗"的计数口径 | §6.2 一致性检查、A3 |
| O-2 | 槽位快照的周期取多少 tick？太密占空间、太稀 `stale` 频繁 | L3、回放精度 |
| O-3 | `MAX_SNAPSHOT_AGE` 取 32 是自定默认，无实测依据 | 槽位"陈旧"判定 |
| O-4 | `UNKNOWN` 告警阈值（占比多少算归类能力异常）未定 | 理由码健康度 |
| O-5 | 账本保留期与擦除策略未定（只追加会无限增长） | 存储成本、隐私 |
| O-6 | `cost_estimate` 的单位（token / 毫秒 / 金额）未定 | S3 的可比性 |
| O-7 | 多进程/多实例写同一账本时的 `seq` 分配口径未定 | 主键唯一性、A5 |
| O-8 | `hit_rate` 的分母（检索次数还是层命中次数）未定义 | 决策输入可比性 |
| O-9 | 代际切换的账本切分策略（同一账本跨代际还是换代际新账本） | A7、时间线 |
| O-10 | 采样档是否允许"补采"（事后开启 full 回溯） | N2 的边界 |

---

## 13. 版本与落款

| 项 | 值 |
|---|---|
| 设计文档 | `docs/nephron.md`（本文） |
| 工程包 | `holoaeon/packs/nephron_pack.py`（第十五包，24 技能 / 7 工作流 / 0 agent） |
| 自检 | `holoaeon/selftest.py` 的 `G23 nephron`（62 条断言） |
| 样例 | `examples/nephron_ledger_sample.jsonl` + `examples/nephron_replay_report.md` |
| 生成器 | `scripts/make_nephron_sample.py` |
| 内核版本 | v0.8.0 |
| 立场守卫 | 每个技能返回值都带 `stance_guard`，写明它服务 S1–S4 中的哪一条 |
| 执行 | 一律 `execution="human_manual"`；终裁 `carbon_based_arbiter` |

潮起开门，潮落闭嘴。
