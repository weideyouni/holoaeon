# HoloAeon System README · v0.8.0

> **系统型说明文档（System README）** — 描述「一个内核 + 六个横切扩展包」的完整系统边界。
> 历史版本文档 `SYSTEM_README.md`（v0.4.0）、`SYSTEM_README_v0.5.0.md`、`SYSTEM_README_v0.6.0.md`、
> `SYSTEM_README_v0.7.0.md` **原样保留**，五份可对照演进。
>
> 内核 `holoaeon` v0.8.0（Apache-2.0）· `sovereignty` / `subdistill` / `omnilife` /
> `omnicore` / `metab` / `nephron` 六包（MIT）· 日期 `2026-10-30` · 密令 **潮起开门，潮落闭嘴**

---

## 1. 系统形态

```
                       ┌──────────────────────────────────────────────┐
                       │  皮肤 Skin —— 权限 / 审计 / 内容门禁 / 不可逆确认 │
                       └──────────────────────────────────────────────┘
         ┌────────────────────────┴──────────────────────────────────┐
         │            矩阵 Matrix  1331 行 × 108641 节点（维度不变式）  │
         │   亚学科槽位 127 × 10 + 61 保留行 │ 节点 127 × 855 + 56 协调  │
         └───────────────────────────────────────────────────────────┘
   心跳 Heartbeat（tick 边界）│ 经络 Meridian（通路 + 降级路由）│ 赫布协作场（权重）
                       ┌──────────────────────────────────────────────┐
                       │  细胞骨架 Skeleton —— 全局协调 / 长期一致性     │
                       └────────────────────────────────────────────────┘
   横切扩展包（只加能力，不加 agent，25 agents / 47 skills 恒定）：
     sovereignty → subdistill → omnilife → omnicore → metab → nephron
   纵切治理链：METAB 决定"能不能进"，NEPHRON 记录"进来后怎么取舍、能否回放"
```

一句话：**METAB 管入口，NEPHRON 管记账。** 前者决定能力与知识是否被允许进入系统，
后者只记录系统在有限容量里做了什么取舍，并保证这些取舍可以被事后回放。

---

## 2. 六包分工

| | `sovereignty` | `subdistill` | `omnilife` | `omnicore` | `metab` | `nephron` |
|---|---|---|---|---|---|---|
| 层 | 信息流 | 知识 | 生活 | 引擎自身 | 摄入治理 | **取舍观测** |
| 解决的问题 | 平台用粗标签简化人 | 粗标签可被归类 | 生活被降维成消费数据 | "数字生命"宣言落不成可跑代码 | 能力与知识从哪进、进多少、怎么退 | 有限容量里取舍了谁、凭什么、能否复盘 |
| 手段 | 16 学科锻造 + 反标签 | 127 亚学科 + 七阶段蒸馏 | 6 生活域锚点 + 皮肤/经络 | 寻址不变式 + 纯函数心跳 | 六染色体 + 四问定态 + 八阶段 | 只追加账本 + 41 字段 + 27 理由码 + 回放 |
| 产物 | 查询清单 / 自述 / 计划 | SKC 知识卡 / 共振表 | 参数卡 / 台账 / 路径 | 计划 / 快照 / 宣告 / 白皮书结构 | 准入判定 / 定态结论 / 缺口清单 / 拒绝理由 | 窗口构成表 / 槽位快照 / 决策输入 / 变更时间线 |
| 工作流 | R0 → R4 | S1 → S7 | L1 → L6 | M1 → M6 | T1 → T8 | **W1 → W7** |
| 技能 / agent | 17 / 0 | 15 / 0 | 18 / 0 | 20 / 0 | 26 / 0 | **24 / 0** |

---

## 3. 维度不变式（系统级契约）

```
127 × 10  亚学科槽位 + 61 保留行    = 1331 行
127 × 855 亚学科节点 + 56 全局协调  = 108641 节点
```

六个扩展包**均不新增行、不新增节点**；每个包的 `pack_summary()["addressing_unchanged"]`
都是 `True`，并在自检里被断言。`nephron` 更进一步：它连"槽位分配"都**只观察不修改**。

| 包 | 技能 | 工作流 | agent | 维度 |
|---|---|---|---|---|
| sovereignty | 17 | 5 | 0 | 不变 |
| subdistill | 15 | 7 | 0 | 不变 |
| omnilife | 18 | 6 | 0 | 不变 |
| omnicore | 20 | 6 | 0 | 不变 |
| metab | 26 | 8 | 0 | 不变 |
| **nephron** | **24** | **7** | **0** | **不变** |
| **合计** | **120** | **39** | **0** | — |

---

## 4. NEPHRON 的观测骨架（v0.8.0 的核心新增）

### 4.1 P0 的边界（先说清"不做什么"）

| 做 | 不做 |
|---|---|
| 只追加记录窗口的进 / 摘要 / 拒 / 命中 / 未命中 / 检索 / 淘汰 / 降级 / 指纹失配 / 预算越界 | 分页、压缩、淘汰、预算控制（P1/P2） |
| 回放任意已记录 tick 的窗口构成与决策输入 | 回放"模型实际看到的文本"（账本不存摘要正文） |
| 披露槽位快照与其年龄 | 重演槽位变化（无 `slot_alloc/slot_free` 事件源） |
| 交付"关闭态与开启态逐字节一致"的断言契约 | 自封该断言已通过（必须宿主实测） |

一句话判定：**它只记与回，不改与算。**

### 4.2 五个结构 / 41 字段

| 结构 | 字段数 | 主键 / 关键约束 |
|---|---|---|
| Page | 10 | `page_id` 为内容稳定哈希；`lineage_ref` 无血统必须写 `NONE`（留空即违规） |
| SlotLedgerEntry | 7 | `slot_class ∈ {trunk, reserve}`；空槽 `occupant_page` 显式 `null` |
| LedgerRecord | 13 | 主键 `(tick, seq)`；`hit_rate` 无检索为 `null`；`compression_ratio` P0 恒 `null` |
| Event | 4 | 11 类；**只允许一个主 `reason_code`** |
| WindowManifest | 7 | 进 / 摘要 / 拒三清单，每行必须带理由码 |

### 4.3 理由码（27 + 1 保留）

| 码族 | 数量 | 说明 |
|---|---|---|
| admit / summ / reject | 3 / 2 / 5 | 窗口内取舍的正面证据 |
| layer / retrieval | 3 / 2 | 通路命中与检索税 |
| evict / degrade | 3 / 3 | 淘汰与降级 |
| fingerprint / budget | 2 / 3 | 代际失配与预算越界 |
| window | 1 | `WINDOW_BUILD_COMPLETE`（评审 R-01 新增） |
| （保留） | 1 | `UNKNOWN` 不入表，单独计数并告警 |

另有三条**写入口**拒绝原因单列：`APPEND_REJECT_CLOCK_REGRESSION` /
`APPEND_REJECT_DUPLICATE_PK` / `APPEND_REJECT_SCHEMA_INVALID`。
理由码判"窗内为什么这样取舍"，拒绝原因判"这条记录为什么没写进去"——两张表不得混用。

### 4.4 回放四件套

| 输出 | 依赖 | 判定 |
|---|---|---|
| 窗口构成表 | 该 tick 的事件流 | 每次进 / 摘要 / 拒都带原码，缺码即 `issues` |
| 槽位快照 | 旁挂周期快照 | 披露 `snapshot_tick` 与 `age_ticks`，>32 标 `stale` |
| 决策输入 | 该 tick 最后一条记录 | `null` 与 `0` 严格区分 |
| 变更时间线 | 相邻 tick 的 admitted 差集 | 进出、拒绝数、指纹失配、代际变更逐 tick 对齐 |

确定性口径：归一化掉 `timestamp / ts / ingested_at / wall_clock / host / pid / elapsed_ms`
后连跑两次，哈希必须一致。

### 4.5 十处冲突的消解（本版最该验收的一段）

| # | 冲突 | 采用 | 一句话理由 |
|---|---|---|---|
| N1 | 异步队列/落盘 vs 不起线程不写盘 | B | 包给队列语义与丢弃计数，I/O 归宿主 |
| N2 | 任意 tick 可回放 vs 三档采样 | B | 只有 `full` 满足，插值补齐等于伪造账本 |
| N3 | 只追加 vs 一键擦除 | B | 摘要换 `ERASED:<hash>`，擦除本身成一条记录 |
| N4 | 有 `compression_ratio` vs 压缩非目标 | B | 字段保留但 P0 恒 `null` |
| N5 | `UNKNOWN` 兜底 vs 表内无此码 | B | 保留码不入表，单独计数并告警 |
| N6 | 主键 vs 时钟回跳 | B | 水位线拒绝追加并记拒绝原因 |
| N7 | 逐字节一致 vs 纯函数不可证 | B | 只交断言契约，恒 `pending_human_measure` |
| N8 | `raw_len` 两种单位单字段 | B | 锁死 token 口径，账本级声明 |
| N9 | `window_build` 无合法码 | B | 正式走评审新增 `WINDOW_BUILD_COMPLETE`（R-01） |
| N10 | 要槽位快照 vs 无槽位事件 | B | 旁挂周期快照 + 披露年龄，P0 不重演 |

---

## 5. 能力边界（`nephron` 的不做清单）

- **不分页、不压缩、不淘汰、不做预算控制**：这些是 P1/P2 的决策，P0 只观测。
- **不改槽位分配**：矩阵结构与 `25/47` 口径不动；`addressing_unchanged=True` 被断言。
- **不写盘、不起线程**：队列实例化与落盘刷写归宿主（`flush="host_managed"`）。
- **不存原文**：只有 `payload_digest + raw_len + delta 长度`；摘要正文不入账本。
- **不自封零侵入**：`zero_intrusion_check()` 恒返回 `pending_human_measure`，`pack_can_prove=False`。
- **不宣称性能提升**：`full` 档额外开销必须宿主实测，文档不写虚构目标值。
- **不代用户判定**：所有输出 `execution="human_manual"`，终裁 `carbon_based_arbiter`。

被名字直接拒绝的操作（`REFUSED_OPS`，11 项）包括：删除账本记录、改写历史记录、
把采集失败抛到业务层、在业务逻辑内散布记录代码、把采样账本插值成完整账本、
在摘要阶段把敏感字段外送、记录外部请求体明文、把失配指纹静默复用、把无血统页写进主干等。

---

## 6. 快速取用

```bash
# 1) 取包（三选一）
git clone https://github.com/weideyouni/holoaeon.git && cd holoaeon   # 主干（v0.8.0）
# 或 git checkout v0.8.0
# 或解压 releases/holoaeon_v0.8.0_20261030.zip

# 2) 全套自检（期望 23/23）
python -c "from holoaeon.selftest import run_all; print(run_all(verbose=True))"

# 3) 单元测试与红线
python -m unittest discover -s tests -v
python scripts/redline_scan.py

# 4) 生成 NEPHRON 黄金样例（账本 JSONL + 回放报告）
python scripts/make_nephron_sample.py

# 5) 只关心 NEPHRON 判定（零依赖，可单独拷走）
python -c "from holoaeon.packs import nephron_pack as n; print(n.pack_summary())"
```

最小调用示例（只读、不落盘）：

```
pack_summary()                        → 24 / 7 / 0 / True / 41 / 11 / 27 / 10 / 3
replay_window(ledger, tick=8, mode="full")
replay_slots(snapshots, tick=8)       → snapshot_tick / age_ticks / stale / entries
replay_inputs(ledger, tick=8)         → window_used / hit_rate=null / compression_ratio=null
replay_timeline(ledger, 0, 99)        → 逐 tick 进出与指纹失配
replay_determinism(ledger)            → 两次归一化哈希一致
zero_intrusion_check()                → pending_human_measure / pack_can_prove=False
acceptance_check()                    → pending=[A1, A2] / verdict=provisional
```

---

## 7. 验证矩阵（v0.8.0 实测）

| 项 | 方式 | 结果 |
|---|---|---|
| 内核自检 | `run_all()` | **23/23 组**（G15 `25 agents / 47 skills` 未破；**G23 nephron 62/62**） |
| 内核单测 | `unittest discover -s tests` | **25 tests OK** |
| 红线扫描 | `scripts/redline_scan.py` | **33 个源文件零违规**（含 `nephron_pack.py` 与 `make_nephron_sample.py`） |
| 黄金样例 | `scripts/make_nephron_sample.py` | 7 条记录 · `verify_ok=True` · 两次回放哈希一致 |
| 发行包 | `scripts/make_release.py` | 打包成功；文件数与字节数见 `releases/RELEASES.md` 本期记录与 `releases/SHA256SUMS.txt`（避免自引用漂移） |
| 解压复跑 | 独立副本 | 23/23；`VERSION=0.8.0`；`nephron 24/7/0/True` |
| 一致性 A1 / A2 | 宿主 CI | **未实测**（`pending_human_measure`，契约已交付） |

---

## 8. 版本梯（只增不覆盖）

| 版本 | 主题 | 形态 | 状态 |
|---|---|---|---|
| v0.4.0 | sovereignty + subdistill | 内核 + 2 包 | 历史（保留） |
| v0.5.0 | omnilife | 内核 + 3 包 | 历史（保留） |
| v0.6.0 | omnicore | 内核 + 4 包 | 历史（保留） |
| v0.7.0 | metab | 内核 + 5 包 | 历史（保留） |
| **v0.8.0** | **nephron P0** | **内核 + 6 包** | **当前** |

任何版本都可独立解压、独立自检、独立运行；旧 zip 与旧 tag 一律不覆盖。

---

## 9. 红线与科学边界

- 纯标准库、零依赖、离线、确定性、可复现；不起线程、不写盘、不联网。
- 红线扫描（AST 口径）禁止：网络库、子进程、`pip/setuptools`、`eval/exec/compile`、
  `__import__`、`input`、文件系统调用、`.env` 类敏感路径、非标准库 import。
- **仿真 ≠ 证明**：本系统的"生命体"是隐喻，可判定的只有代码与数据。
  METAB 的准入判定、NEPHRON 的账本与回放，都是**确定性软件行为**，不是生理学主张。
- **碳基终裁**：所有 `execution="human_manual"`，任何版本都不替用户做最终决定。

---

## 10. 许可证

| 部分 | 许可 | 说明 |
|---|---|---|
| 内核 `holoaeon/`（含 `selftest.py`、`spec.py`、九大领域包） | Apache-2.0 | 见 `LICENSE` |
| 横切扩展包（`sovereignty` / `subdistill` / `omnilife` / `omnicore` / `metab` / `nephron`） | MIT | 与内核不互相转嫁 |

两组许可分别标注，互不转嫁；引用本系统时请按部分分别声明。

---

## 11. 路线图

- **v0.4 – v0.7**：sovereignty / subdistill / omnilife / omnicore / metab 五包落地（已完成）。
- **v0.8（当前）**：nephron P0 —— 只读账本 + 回放；10 处冲突消解；两项验收留给宿主实测。
- **v0.9（NEPHRON P1）**：打分公式、窗口构建流程、降级链声明、成对回归判据；
  槽位变化重演（`slot_alloc/slot_free` 事件表评审）、`compression_ratio` 真正有值。
- **v0.9 – v0.10（内核）**：可插拔持久化后端与节点间总线传输；声明式图/拓扑 + 包创作工具包。
- **v1.0**：稳定认知框架，API 冻结，文档完整。

---

潮起开门，潮落闭嘴。
