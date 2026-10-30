# NEPHRON P1 判定细则 · 窗口构建与降级链

> 版本：v0.9.0 ｜ 前置：v0.8.0 的 P0 字段已冻结（41 字段 / 11 类事件 / 27 理由码）
> 依赖裁决：O-1（`window_used` 恒等口径）、O-6（`cost_estimate` 单位 ms）、O-8（`hit_rate` 分母）
> 实测基线：`scripts/measure_a1_a2.py` → A1 PASS、A2 full 档 +1.64%（`docs/nephron_a1_a2_evidence.json`）

P1 才开始"做决策"：P0 只记录，P1 决定一个页以什么形态进窗、按什么顺序、越界时降级到哪一级。
**P1 仍不淘汰任何页** —— 淘汰属 P2。本文件里每条规则都必须能被一条断言判真假。

---

## 1. 打分公式（四项，全部确定性）

对每个候选页 `p`，窗口构建前计算：

| 项 | 符号 | 定义 | 取值域 | 数据来源 |
|---|---|---|---|---|
| 相关度 | `rel(p)` | 查询与页的字符 2-gram Dice（与 `skill.py` 的 `ngram_dice` 同一实现） | [0,1] | 页的 `payload_digest` 对应的结构化摘要 |
| 新近度 | `rec(p)` | `1 - min(1, (tick - p.last_tick) / H)`，`H = 2×槽位快照周期 = 32` | [0,1] | `Page.last_tick` |
| 血统可信度 | `lin(p)` | 有血统且哈希链可验 = 1.0；有血统但未验 = 0.6；`lineage_ref="NONE"` = 0.0 | {0,0.6,1} | `Page.lineage_ref` + 血统账本 |
| 成本 | `cost(p)` | `p.raw_len / 1000`（千 token 计），单位与 `cost_estimate`（ms）分开记，不混算 | ≥0 | `Page.raw_len` |

综合分（权重固定，不做自适应——自适应会让两次构建不可比）：

```
score(p) = 0.40·rel + 0.25·rec + 0.25·lin + 0.10·(1 - min(1, cost(p)/4))
```

判定性：给定同一账本与同一配置，两次计算出的 `score(p)` 必须逐位相同（浮点按 6 位四舍五入后比较）。

---

## 2. 降级链与触发条件

每一页在窗口构建中最多降一级，降到下一级后重新评估是否触底。**每一次降级必须写一条 `degradation` 事件**，不得静默。

| 级别 | 形态 `form` | 进入该级的触发条件 | 理由码 | 退化后果 |
|---|---|---|---|---|
| L0 | `raw`（全文） | 预算充足 且 `lin(p)=1.0` 且 `rel ≥ 0.5` | `ADMIT_HIGH_RELEVANCE` | 无 |
| L1 | `summary` | 预算压力：`window_used + len(p) > window_budget` | `SUMM_BUDGET_PRESSURE` | 丢细节、保骨架 |
| L2 | `fingerprint` | 摘要不可用（本地摘要器缺席）或 `rel < 0.2` 且 `rec ≥ 0.5` | `SUMM_LOW_VALUE_KEEP_TRACE` | 只剩指纹，可判"这条来过" |
| L3 | `drop`（不进窗） | `lin(p)=0.0`（无血统）｜指纹失配｜预算仍超 | `REJECT_NO_LINEAGE` / `REJECT_STALE_FINGERPRINT` / `REJECT_BUDGET_EXCEEDED` | 完全不进窗，但**仍留在账本** |

三条硬规则（任一违反即该次窗口构建判 REJECT）：

1. **不跳级**：L0 不许直接到 L2/L3 而不写中间级事件（允许 L0→L1→L3 这样的连续两级，但每级都要留痕）。
2. **不静默**：任何形态变化必须有对应的 `degradation` 或 `page_summarize` / `page_reject` 事件。
3. **不伪造**：`form` 一旦记为 `fingerprint`，该页在本 tick 不许再被计为 `raw` 的 token 占用量。

---

## 3. 窗口构建流程（7 步，顺序不可调）

1. 收集候选：本 tick 可达的 `working / hebbian / skeleton / external` 四层页。
2. 过滤：`fingerprint` 与当前代际不符者 → `fingerprint_mismatch` 事件，直接出局（A7）。
3. 打分：按 §1 计算，`score` 写入 `WindowManifest.admitted[].score`。
4. 排序：`(-score, page_id)` 双键，保证同分时按 id 稳定。
5. 装填：累加 `raw_len`，触及 `window_budget` 时进入降级链（§2）。
6. 记账：写 `window_build` 事件 + `WindowManifest`；`window_used` 与 `admitted` 数**恒等**（O-1）。
7. 收尾：`compression_ratio = 窗口内 raw_len 之和 / 原始 raw_len 之和`；无摘要发生时置 `null` 而不是 1.0。

判定性：第 4 步的排序必须是全序；第 6 步的恒等必须能被 `window_used == len(admitted)` 一条断言验证。

---

## 4. 成对回归：PASS 的四条判据

任意两次窗口构建（基线 B 与候选 C，同一 workload、同一代际指纹）对比：

| # | 判据 | 判定方式 | 违反后果 |
|---|---|---|---|
| ① | 预算占用不增 | `C.window_used ≤ B.window_used` | REJECT |
| ② | `hit_rate` 不降 | `C.hit_rate ≥ B.hit_rate`（`None` 视为不参与比较，两边都 `None` 时本条跳过并记 `skipped`） | REJECT |
| ③ | admitted 重合度 ≥ 基线 − ε（ε = 0.05） | `|A∩B| / |A∪B| ≥ B_jaccard − 0.05`，`A` 为候选 admitted 的 page_id 集 | REJECT |
| ④ | 全部决策可由账本解释 | 回放器对该 tick 的 `UNKNOWN` 计数 **= 0** | REJECT |

四条**全过**才 PASS；任一不过即 REJECT，并输出差异三件套（§5）。判据 ② 的"跳过"必须写进报告：
跳过不等于通过（`skipped` 单独计数，并在结论里显式列出）。

---

## 5. 差异三件套

REJECT 时**必须**同时产出三件，缺一件即该次对比无效：

| 件 | 内容 | 形态 |
|---|---|---|
| `diff_manifest` | 两个 `WindowManifest` 的逐页差异：进出、形态变化、理由码变化 | 表（人读）+ JSONL（机读） |
| `diff_score` | 分数差异：`Δ = sum(score_C - score_B)`、`max_gain`、`max_loss`（各带 page_id） | 同上 |
| `diff_reason_codes` | 理由码分布差异：`{code: {before, after, delta}}`，`UNKNOWN` 单列 | 同上 |

---

## 6. 与既有机制的接口

| 机制 | P1 的用法 | P1 不做的事 |
|---|---|---|
| 矩阵 | 只在备用槽位里装填；主干槽位改动属代谢态 | 不重排主干槽位 |
| 心跳 | 打分与装填在 tick 边界内完成；不跨 tick 累积 | 不引入新屏障 |
| 皮肤 | 降级到 `drop` 不越过权限门；`REJECT_TRUST_RADIUS` 由皮肤给出 | 不自行放宽信任半径 |
| 经络 | 降级路由走既有降级路径，不新开通路 | 不断头路 |
| 赫布协作场 | `hebbian` 层页的 `lin` 与协作权重无关（权重不是血统） | 不用协作权重替代血统 |
| 血统账本 | `lin(p)` 的唯一来源；`NONE` 一律 0 | 不给无血统页"临时可信" |
| 代际 | 任一页指纹失配即出局；代际切换换新账本文件（O-9） | 不跨代际拼分数 |

---

## 7. 待实测项（P1 内不得标"通过"）

| # | 项 | 为什么现在不能标 |
|---|---|---|
| P1-M1 | 权重 0.40/0.25/0.25/0.10 是否合理 | 没有真实 workload 的成对回归数据；只能先冻结，再用回归结果反推 |
| P1-M2 | `cost(p)` 归一化除数 4（千 token） | 依赖真实窗口规模，本仓库无生产负载 |
| P1-M3 | 重合度 ε=0.05 的松紧 | 同上；ε 变了结论会翻转 |
| P1-M4 | 降级链在真实预算压力下的触发频率 | P0 无生产 writer，测不出 |

这四项在实现里必须显式标 `unmeasured`，**不得**在文档或回执里写成"已验证"。
潮起开门，潮落闭嘴。
