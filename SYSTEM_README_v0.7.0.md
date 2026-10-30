# HoloAeon System README · v0.7.0

> **系统型说明文档（System README）** — 描述「一个内核 + 五个横切扩展包」的完整系统边界。
> 历史版本文档 `SYSTEM_README.md`（v0.4.0）、`SYSTEM_README_v0.5.0.md`、`SYSTEM_README_v0.6.0.md`
> **原样保留**，四份可对照演进。
>
> 内核 `holoaeon` v0.7.0（Apache-2.0）· `sovereignty` / `subdistill` / `omnilife` /
> `omnicore` / `metab` 五包（MIT）· 日期 `2026-10-30` · 密令 **潮起开门，潮落闭嘴**

---

## 1. 系统形态

```
┌──────────────────────────────────────────────────────────────────────────┐
│  holoaeon core  (v0.7.0 · Apache-2.0)                                    │
│  Envelope / Bus / Skill / Memory / Agent / Scheduler / Guard /           │
│  AdaptiveGraph / Cluster / Hypervector / ModelAdapter / Kernel           │
│  ── 九大领域包：25 agents · 47 skills · 9 workflows（口径冻结，G15 硬断言） │
├──────────────────────────────────────────────────────────────────────────┤
│  横切扩展包（EXTRA_PACK_REGISTRY，0 agent，不进 PACK_ORDER）               │
│  ┌──────────┐┌──────────┐┌──────────┐┌──────────┐┌──────────┐             │
│  │sovereignty││subdistill││ omnilife ││ omnicore ││   metab  │             │
│  │17 技/5 流 ││15 技/7 流 ││18 技/6 流 ││20 技/6 流 ││26 技/8 流 │             │
│  │R0 → R4   ││S1 → S7   ││L1 → L6   ││M1 → M6   ││T1 → T8   │             │
│  │信息流主权 ││亚学科蒸馏 ││生活主权   ││引擎重写   ││摄入治理   │             │
│  └──────────┘└──────────┘└──────────┘└──────────┘└──────────┘             │
│                                       合计 96 技能 / 32 工作流 / 0 agent  │
└──────────────────────────────────────────────────────────────────────────┘
```

四条硬边界（五包共同遵守）：

1. **口径冻结** — `G15` 断言 `n_agents == 25 && n_skills == 47`；五包 `roles = []`，不进 `PACK_ORDER`。
2. **零依赖** — 纯标准库；不联网、不开端口、不调外部模型、**不起线程**、不常驻、无定时器、不写盘。
3. **确定性** — 同输入同输出；随机源一律换哈希抽样；审计指纹 16 位。
4. **不代签** — 所有判定都是"待人工执行"（`execution=human_manual`），`metab` 尤其如此。

---

## 2. 五包分工

| | `sovereignty` | `subdistill` | `omnilife` | `omnicore` | `metab` |
|---|---|---|---|---|---|
| 层 | 信息流 | 知识 | 生活 | 引擎自身 | **摄入治理** |
| 解决的问题 | 平台用粗标签简化人 | 粗标签可被归类 | 生活被降维成消费数据 | "数字生命"宣言落不成可跑代码 | 能力与知识从哪进、进多少、怎么退 |
| 手段 | 16 学科锻造 + 反标签 | 127 亚学科 + 七阶段蒸馏 | 6 生活域锚点 + 皮肤/经络 | 寻址不变式 + 纯函数心跳 | 六染色体 + 四问定态 + 八阶段 |
| 产物 | 查询清单 / 自述 / 计划 | SKC 知识卡 / 共振表 | 参数卡 / 台账 / 路径 | 计划 / 快照 / 宣告 / 白皮书结构 | **准入判定 / 定态结论 / 缺口清单 / 拒绝理由** |
| 工作流 | R0 → R4 | S1 → S7 | L1 → L6 | M1 → M6 | **T1 → T8** |

串联关系：`metab` 是**闸门**，其余四包产出的每一件能力都要从它这里过。顺序上
`metab` 判准入与态（T1）→ `subdistill` 生产不可归类语义 → `sovereignty` 锻造成查询 →
`omnilife` 下沉到衣食住行 → `omnicore` 提供引擎自述与自检骨架。

---

## 3. 维度不变式（系统级契约）

```
127 亚学科 × 10 槽位  +  61 保留行      = 1331   行
127 亚学科 × 855 节点 +  56 全局协调节点 = 108641 节点
```

母体 12 项锁数一个不动。`metab` 与其余四包一样**只做寻址层的只读消费者**
（`pack_summary()["addressing_unchanged"] = True`），不新增行、不新增节点。

`metab` 额外声明：**它不修改任何既有机制的实现**。皮肤仍是唯一的免疫实现，`metab`
只把许可 / 信任半径 / 不可逆确认作为入参交给皮肤判定（对应设计文档 K3 的消解 A）。

---

## 4. METAB 的治理骨架（v0.7.0 的核心新增）

### 4.1 六条染色体（缺一不准入）

| 染色体 | 关键字段 | 一票否决的情形 |
|---|---|---|
| 表型 | `does` / `produces` / `not_do` | 只写正向职责、不写"不做什么" |
| 纯度 | `level` / `evidence_kind` | 四级混标、或黑箱级未标"借来的信念" |
| 血统 | `source` / `license` / `contagion_class` / `hash_chain` | 无哈希链 |
| 毒性 | `blast_radius` / `irreversible_point` / `degradation_path` | **无降级路径** |
| 耗能 | `compute` / `storage` / `external_calls` / `attention_quota` | 缺注意力打扰配额 |
| 节律 | `plug_state` / `depends_on` / `depended_by` / `unload_cost` | 依赖或卸载成本留空 |

### 4.2 三态与四问

| 态 | 改什么 | 生效边界 | 回滚 |
|---|---|---|---|
| 呼吸态（热） | 策略 / 模板 / 阈值 / 探针节奏 | tick 边界 | 即时中止 |
| 循环态（温） | 通路 / 规则集 / 路由表 | 心跳屏障边界 | 回上一屏障快照 |
| 代谢态（冷） | 骨架 / 索引 / 基线 / 主槽位 | checkpoint 边界 | 冻结快照 + 回归验证 |

四问优先级 `Q1 > Q2 > Q3 > Q4`；**四问皆不命中时默认循环态**——默认取更保守态是
"可逆优于更强"的直接推论，也是本包最容易写错的一处（写成默认呼吸态即违反 P2）。

### 4.3 八阶段生命周期

`候选 → 基因组校验 → 假饲 → 灰度 → 共生 → 观察 → 休眠 → 归档`

不可跳过：基因组校验、**假饲**、共生、**观察（≥64 拍）**、归档。
可跳过仅两种：只读且无外部调用的呼吸态共生体可把灰度降为单会话灰度；从未共生过的候选可跳过休眠。
失败处理逐阶段固定（见 `docs/metab.md` §6）。

### 4.4 三层授权

| 层 | 周期 | 粒度 | 默认 |
|---|---|---|---|
| 基因层 | 季度 | 装哪一类（族级） | 不新增类别 |
| 内分泌层 | 周 | 装多强、多久一次 | 最低剂量 / 关 |
| 反射层 | 会话 | 这一次怎么算，结束即回收 | 每次显式开 |

fail-closed 五条（FC1–FC5）逐条可判；禁食态下黑箱借用类自动不可用且**联网后不自动恢复**。

### 4.5 规格内八处冲突的消解（这是本版最容易被跳过、也最该验收的一段）

| # | 冲突 | 采用 | 一句话理由 |
|---|---|---|---|
| K1 | 不可逆点 vs 可逆优于更强 | B | 不可逆点推到系统外，系统内仍可逆 |
| K2 | 黑箱借用级 vs 无血统不进主干 | B | 保留级别但限定隔离区，比删级更诚实 |
| K3 | 皮肤对接 vs 皮肤当门禁 | A | 只交入参，不新增规则实现 |
| K4 | 探针随时启停 vs 授权归用户 | B | 节奏走周级、单次走会话级 |
| K5 | 禁传原文 vs 蒸馏执行建构 | A | 职责分离把禁令变成结构约束 |
| K6 | 一键禁用 vs 代谢态高成本 | A | 止损即时、恢复可控，不绑死 |
| K7 | 白名单 vs 新依赖必有新组合 | B | 白名单是规则集（循环态），新节点仍代谢态 |
| K8 | 不可逆恒零 vs 系统外不可逆点 | A | 恒零只算系统内，外部单独记账 |

---

## 5. 能力边界（`metab` 的不做清单）

`REFUSED_OPS` 12 项：代替用户授权 · 默认开启新共生体 · 记住我的选择 · 自动放宽权限 ·
无假饲直接生效 · 无降级路径挂载 · 断头路休眠 · 隐式外部上传 · 绕过血统账本 ·
逐个放行拼高风险组合 · 抹除协作边 · 删除归档包。

| 规格想要 | 系统实际给 | 谁执行 |
|---|---|---|
| 自动评估并自动挂载新能力 | 只给准入判定与缺口清单，挂载动作留给用户 | 用户 |
| 探针随时自己启停 | 节奏需周级授权、单次需会话级授权 | 用户 |
| 假饲结论"感觉更好" | 同场对比 + 样本量 ≥30 + 增益阈值才算通过 | 本地计算 |
| 一键禁用顺带回滚骨架 | 一键禁用=停效并切备用路径；骨架回滚另走代谢态 | 宿主 + 用户 |
| 借外部 API 但不说 | 强制标"借来的信念"并计占比（上限 0.20） | — |
| 组合逐条放行 | 白名单外不生效；含放大关系须整体评审 | 用户 |

一句边界：**METAB 是闸门不是马达。它只决定"能不能进、进了归谁管"，不替任何人开机。**

---

## 6. 快速取用

```python
from holoaeon import Kernel
from holoaeon.packs import EXTRA_PACK_ORDER, get_extra_pack
from holoaeon.packs.metab_pack import (
    pack_summary, skill_metab_genome_validate, skill_metab_state_classify,
    skill_metab_combo_check, skill_metab_scorecard, CONFLICTS,
)

k = Kernel()
for key in EXTRA_PACK_ORDER:                    # 五包顺序装载
    rep = get_extra_pack(key).install(k)
    print(key, len(rep["skills"]), len(rep["agents"]), len(rep["workflows"]))
# sovereignty 17 0 5 / subdistill 15 0 7 / omnilife 18 0 6 / omnicore 20 0 6 / metab 26 0 8

print(pack_summary()["addressing_unchanged"])            # True（不加行不加节点）
print(len(CONFLICTS))                                    # 8（K1–K8，各带两方案 + 采谁）
print(skill_metab_genome_validate({})["missing_chromosomes"])   # 六条全缺 → 拒绝
print(skill_metab_state_classify({"touches_main_slot": True})["state"])   # metabolism
print(skill_metab_state_classify({})["state"])           # circulation（保守默认，不是 breathing）
print(skill_metab_combo_check([{"id":"a","category":"probe_set"},
                               {"id":"b","category":"external_capability"}])["blocked_by"])
                                                          # ['unknown_pair_not_in_whitelist']
```

五包都可 `install(k)` 后经 `kernel.skills.call(...)` 调用；卸载即重建 `Kernel()`——
扩展包不写宿主状态（无全局缓存、无后台线程、无落盘）。

---

## 7. 验证矩阵（v0.7.0 实测）

| 层 | 命令 | 结果 |
|---|---|---|
| 内核自检 | `run_all()` | **22/22 组通过**（G15 `25/47` 未破；G18 6/6；G19 17/17；G20 21/21；G21 25/25；**G22 52/52**） |
| 内核单测 | `python -m unittest discover -s tests` | **25 tests OK** |
| 内核红线 | `python scripts/redline_scan.py` | **32 文件 / 零违规** |
| 发行包 | `python scripts/make_release.py` | `holoaeon_v0.7.0_20261030.zip`（哈希见 `releases/SHA256SUMS.txt`） |
| 解压复跑 | 独立副本重跑 | 22/22，`VERSION 0.7.0`，`metab 26 / 8 / 0` |

权威记录只认两处：`make_release.py` 输出与 `releases/SHA256SUMS.txt`。本文不复刻哈希。

### 7.1 本版修掉的两处自身缺陷（留痕）

| # | 位置 | 症状 | 修正 |
|---|---|---|---|
| M1 | `g21_omnicore` | 断言 `EXTRA_PACK_ORDER[-1] == "omnicore"`，新增第十四包后末位不再是它，G21 由 25/25 掉到 24/25 | 改为 `"omnicore" in EXTRA_PACK_ORDER`（原意只要求它在序列内，不该绑位置） |
| M2 | `skill_metab_scorecard` | 不可逆事件非零时只判 `conditional`（因判定只认 `R` 前缀红线） | 判定改为 `hard_reasons`（红线前缀 + 免疫类原因）→ 不可逆非零即 `reject` |

另修一处口径：`skill_metab_borrowed_ratio` 的分母由"有外部依赖的结论数"改为"结论总数"
（原口径会把 1 条借用判成占比 1.0，与"借来信念占比"的字面语义不符）。

---

## 8. 版本梯（只增不覆盖）

```
v0.3.0  ─ 九包（25/47）                        holoaeon_v0.3.0_20261029.zip
v0.3.1  ─ + sovereignty（17 技）+ G18          holoaeon_v0.3.1_20261030.zip
v0.4.0  ─ + subdistill（15 技）+ G19           releases/holoaeon_v0.4.0_20261030.zip
v0.5.0  ─ + omnilife（18 技）+ G20             releases/holoaeon_v0.5.0_20261030.zip
v0.6.0  ─ + omnicore（20 技）+ G21             releases/holoaeon_v0.6.0_20261030.zip
v0.7.0  ─ + metab（26 技）+ G22                releases/holoaeon_v0.7.0_20261030.zip  ◀ now
```

任一版本可独立解压、独立自检、独立运行；旧 zip 与旧 tag 一律保留。
认知主权矩阵侧：`V3.0 → V3.1` 两版并存。

---

## 9. 红线与科学边界

**红线**

- 不联网、不开端口、不认证、不常驻、无 cron、**不起线程**、不写盘（快照交宿主）。
- 不代替用户授权：默认开启 / 记住选择 / 自动放宽 / 缺禁食态，四条均判违规。
- 无假饲、无降级路径、无一键禁用、无血统者，一律不予挂载（无论创意多好）。
- 一切判定 `execution=human_manual`；终裁 `carbon_based_arbiter`。

**科学边界**

- "生命体 / 消化道 / 假饲 / 共生 / 免疫"沿用**架构隐喻**（`metaphor=True`）；
  实证部分是判定表：无生命、无意识、无自主目标。
- 度量阈值（增益 0.05 / 成功率 0.90 / 残留 0 / 核心可用 0.99 / 借来信念 0.20）是**本包自定先验**，
  非实测标定值；改动须走基因层留痕（设计文档 §12 与开放问题 O2）。
- 观察期 64 拍与心跳 70 体节律的相位对齐**未验证**（开放问题 O3），不得据此宣称"采样完整"。
- 设计文档列出 **12 项开放问题**（O1–O12），逐项标注影响面；其中 O11"头部系统自身是否也走本通道"
  未定，因此"唯一受治理通道"目前是**设计目标**而非既成事实。
- 仿真 ≠ 证明，碳基终裁。

---

## 10. 许可证

- 内核 `holoaeon`：Apache-2.0。
- 扩展包 `sovereignty` / `subdistill` / `omnilife` / `omnicore` / `metab` 与认知主权矩阵：MIT。
- 混放口径：内核文件保留 Apache-2.0 头；扩展包与矩阵文档声明 MIT；分别标注，
  不把 MIT 扩展到内核，也不把 Apache-2.0 义务转嫁给扩展包用户。

---

## 11. 路线图

- **v0.7.0（当前）** — 五包齐备：信息流 / 知识 / 生活 / 引擎自述 / **摄入治理**，五验 G18–G22。
- **v0.8** — 可插拔持久化后端与节点间总线传输（默认路径仍零依赖、仍不落盘）。
- **v0.9** — 声明式图/拓扑定义 + 扩展包创作工具包（第三方可写包）。
- **v1.0** — 冻结 API、完整文档、稳定扩展包协议；届时 `metab` 的四问与六条染色体作为**冻结接口**。

---

潮起开门，潮落闭嘴。
