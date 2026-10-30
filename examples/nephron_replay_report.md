# NEPHRON P0 回放报告（黄金样例）

> 本报告由 `python scripts/make_nephron_sample.py` 生成，内容全部来自 `holoaeon.packs.nephron_pack` 的纯函数；不是手写样张。

## 1. 账本概况

| 项 | 值 |
|---|---|
| 记录数 | 7 |
| tick 区间 | 0 – 6 |
| 链摘要 | `DE0A340FAAE1DBAC` |
| 只追加核验 | 通过（seq 单调 / 主键唯一 / 无缺口 / tick 不倒退） |
| 代际指纹 | `28D75E51C85BC6A8`（tick 0–5 同代际，tick 6 故意换代际） |
| 字段字典条目 | 41（与结构定义一致：True） |
| 回放确定性 | 通过（`B067A3F919AA5225` == `B067A3F919AA5225`） |

## 2. 逐 tick 窗口构成表

### tick 0

| 进（page_id / score / 理由码） | 摘要（page_id / from→to / 理由码） | 拒（page_id / 理由码） |
|---|---|---|
| p-100 / 0.62 / `ADMIT_RECENT`<br>p-101 / 0.58 / `ADMIT_RECENT`<br>p-102 / 0.51 / `ADMIT_LINEAGE_TRUSTED`<br>p-103 / 0.77 / `ADMIT_HIGH_RELEVANCE` | — | p-104 / `REJECT_REDUNDANT` |

决策输入：预算 8 → 使用 4；四层驻留 working=2/hebbian=1/skeleton=1/external=0；命中率 null（本 tick 无检索）；代价 0.0；置信度 null。

### tick 1

| 进（page_id / score / 理由码） | 摘要（page_id / from→to / 理由码） | 拒（page_id / 理由码） |
|---|---|---|
| p-101 / 0.60 / `ADMIT_RECENT`<br>p-102 / 0.55 / `ADMIT_LINEAGE_TRUSTED`<br>p-105 / 0.49 / `ADMIT_RECENT`<br>p-103 / 0.74 / `ADMIT_HIGH_RELEVANCE` | — | p-106 / `REJECT_STALE_FINGERPRINT` |

决策输入：预算 8 → 使用 4；四层驻留 working=1/hebbian=2/skeleton=1/external=0；命中率 0.5；代价 0.1；置信度 0.8。

### tick 2

| 进（page_id / score / 理由码） | 摘要（page_id / from→to / 理由码） | 拒（page_id / 理由码） |
|---|---|---|
| p-102 / 0.58 / `ADMIT_LINEAGE_TRUSTED`<br>p-101 / 0.57 / `ADMIT_RECENT`<br>p-107 / 0.71 / `ADMIT_HIGH_RELEVANCE` | p-100 / 900→120 / `SUMM_BUDGET_PRESSURE` | p-105 / `REJECT_BUDGET_EXCEEDED` |

决策输入：预算 8 → 使用 3；四层驻留 working=1/hebbian=1/skeleton=1/external=0；命中率 0.66；代价 0.3；置信度 0.7。

### tick 3

| 进（page_id / score / 理由码） | 摘要（page_id / from→to / 理由码） | 拒（page_id / 理由码） |
|---|---|---|
| p-101 / 0.59 / `ADMIT_RECENT`<br>p-102 / 0.60 / `ADMIT_LINEAGE_TRUSTED`<br>p-107 / 0.69 / `ADMIT_HIGH_RELEVANCE`<br>p-108 / 0.44 / `ADMIT_RECENT` | — | p-109 / `REJECT_NO_LINEAGE` |

决策输入：预算 8 → 使用 4；四层驻留 working=2/hebbian=1/skeleton=1/external=0；命中率 0.5；代价 0.1；置信度 0.75。

### tick 4

| 进（page_id / score / 理由码） | 摘要（page_id / from→to / 理由码） | 拒（page_id / 理由码） |
|---|---|---|
| p-102 / 0.61 / `ADMIT_LINEAGE_TRUSTED`<br>p-107 / 0.66 / `ADMIT_HIGH_RELEVANCE`<br>p-101 / 0.58 / `ADMIT_RECENT` | — | — |

决策输入：预算 8 → 使用 3；四层驻留 working=1/hebbian=1/skeleton=1/external=0；命中率 0.75；代价 0.05；置信度 0.82。

### tick 5

| 进（page_id / score / 理由码） | 摘要（page_id / from→to / 理由码） | 拒（page_id / 理由码） |
|---|---|---|
| p-102 / 0.63 / `ADMIT_LINEAGE_TRUSTED`<br>p-107 / 0.70 / `ADMIT_HIGH_RELEVANCE` | — | p-111 / `REJECT_TRUST_RADIUS` |

决策输入：预算 8 → 使用 2；四层驻留 working=1/hebbian=0/skeleton=1/external=0；命中率 null（本 tick 无检索）；代价 0.0；置信度 0.6。

### tick 6

| 进（page_id / score / 理由码） | 摘要（page_id / from→to / 理由码） | 拒（page_id / 理由码） |
|---|---|---|
| — | — | p-102 / `REJECT_STALE_FINGERPRINT` |

决策输入：预算 8 → 使用 1；四层驻留 working=1/hebbian=0/skeleton=0/external=0；命中率 null（本 tick 无检索）；代价 0.0；置信度 null。

## 3. 变更时间线（相邻 tick 差异）

| tick | 进入 | 离开 | 拒绝数 | 指纹失配 | 代际变更 |
|---|---|---|---|---|---|
| 0 | （首帧） | — | 1 | 0 | 否 |
| 1 | p-105 | p-100 | 1 | 0 | 否 |
| 2 | p-107 | p-103、p-105 | 1 | 0 | 否 |
| 3 | p-108 | — | 1 | 0 | 否 |
| 4 | — | p-108 | 0 | 0 | 否 |
| 5 | — | p-101 | 1 | 0 | 否 |
| 6 | — | p-102、p-107 | 1 | 1 | 是 |

## 4. 槽位快照（最近快照 ≤ tick）

| 查询 tick | 快照 tick | 年龄 | 陈旧 | 条目数 | 说明 |
|---|---|---|---|---|---|
| 2 | 0 | 2 | 否 | 3 | `replay_scope=snapshot_only`（P0 不重演槽位变化） |
| 6 | 4 | 2 | 否 | 4 | `replay_scope=snapshot_only`（P0 不重演槽位变化） |
| 40 | 4 | 36 | 是 | 4 | `replay_scope=snapshot_only`（P0 不重演槽位变化） |

## 5. 验收状态（A1–A8）

| 编号 | 结论 | 本包能否自证 | 状态 |
|---|---|---|---|
| A1 | 关闭态与开启态系统输出逐字节一致（CI 断言） | false | `pending_human_measure` |
| A2 | 采集异常不影响主流程 | contract_only | `pending_human_measure` |
| A3 | 任意历史 tick 可回放且窗口构成可解释 | true | `pass` |
| A4 | 回放确定性：两次回放输出哈希一致 | true | `pass` |
| A5 | 账本只追加，无改写与删除路径 | true | `pass` |
| A6 | 无血统页显式 lineage_ref="NONE" | true | `pass` |
| A7 | 指纹失配必产 fingerprint_mismatch 事件 | true | `pass` |
| A8 | 文档完备（字段字典 / 理由码 / 开关 / 回放教程 / 隐私） | true | `pass` |

待人工实测：A1、A2；总判定 `provisional`。

---

潮起开门，潮落闭嘴。
