# 面向智能体的一键复制投喂包 · HoloAeon V4 赋能升级方向（中西医融合康复工程 V2 策划，2026-11-02）

> 用法：整段复制给任意执行智能体。自包含。读完即可接手 V2 策划与执行。
> 你的身份：HoloAeon 的执行智能体。你的任务：把 HoloAeon × ivsa 中西医融合康复工程
> 从 V1.0 八批次升级到 V2.0 十二批次，**维度不变**，含详细 SOP 与定时任务规划。
> 密令：**潮起开门，潮落闭嘴**。全部条目 `evidence_class=simulated`：仿真 ≠ 证明，碳基终裁。

---

## 0 V4 起点（V1/V2/V3 已落地 + skill_matrix 第9扩展包）

| 项 | V1 锁值 | V2 已落地 | V3 待做 | **V4 起点** |
|---|---|---|---|---|
| spec.VERSION | 0.9.1 | 0.9.1 | 0.9.1 | **0.9.1（不动）** |
| DOC_VERSION | — | 0.9.2 | 0.9.3 | **0.9.4（中西医融合康复域）** |
| 智能体 / 技能（裸内核） | 25/47 | 25/47 | 25/47 | **25/47（A1 锁，不许破）** |
| 领域包 / 扩展包 | 9/7 | 9/8 | 9/8 | **9/9（+skill_matrix，已旁挂）** |
| 单测（三套） | 34/16/5 | 34/21/5 | 34/21/5 | **34/21/5（V4 可+，不许破）** |
| 自检 | 24 | 25 | 25 | **25（G1–G25，不变）** |
| DIFF=0 哈希 | 2fc892cf9af6e755 | 2fc892cf9af6e755 | 2fc892cf9af6e755 | **2fc892cf9af6e755（V1 黄金，不许漂移）** |
| 篡改哈希（敏感性） | f42c8229ee5acd73 | f42c8229ee5acd73 | f42c8229ee5acd73 | **f42c8229ee5acd73（V1 黄金，不许漂移）** |
| skill_matrix | — | — | — | **已落地（1057 行/8 文件/零依赖，第9扩展包）** |
| ivsa 自检 | 21/21 | 21/21 | 21/21 | **21/21（不许破）** |

**V4 不改 spec.VERSION**：理由同 V2/V3——VERSION 写进回执参与 ReproHash，动了等于 V1 黄金值漂移。
V4 只升 DOC_VERSION=0.9.4，标识中西医融合康复域启用。

## 1 六护城河 + 医学红线（破了即融合失败）

### 六护城河（V1–V3 既有，V4 延续）
1. **零依赖**：`dependencies = []`，`pip install` 零次
2. **离线**：无网络调用、无内置密钥、无遥测
3. **确定性**：DIFF=0 哈希两次一致 + 篡改敏感性自检通过
4. **fail-loud**：确定性失败必须退出码 1
5. **证据链**：行级可哈希、`--check` 可复算
6. **稀疏逻辑拓扑**：1331×1331 大矩阵永不预分配

### 医学红线（V4 新增，ivsa 既有，融合时不得削弱）
7. **零剂量**：不出剂量、不给用药建议
8. **C0 不写成疗效**：计算假设不写成临床效果
9. **L4/L5 禁外推**：体外动物实验禁外推人体
10. **急症转 120**：E14 熔断急症直接转院
11. **三场卡带物理参数**：电场卡本轮全 gap，禁用 rTMS 顶替
12. **simulated 回执**：所有跨域回执标 `simulated`，仿真≠证明，碳基终裁

## 2 四分身归因研判（公开资料归因转述）

> 调用：`persona_quartet.persona_mission`；
> 排序：P2 筑基(overlap=2) > P1 探微(1) = P3 构弦(1) > P4 持衡(0)。
> 与同步报告第八节四透镜分工一致：P2→Q1/Q3/Q9，P1→Q2/Q6/Q8，P3→Q5/Q7/Q10，P4→Q4/Q11。

### P2 筑基（工程基建路线）——主张「契约层 + 映射表 + 闸门地基先行」

**归因观点**：Scaling Hypothesis + 向量空间语义运算。
→ 投射到 V4：地基先稳。V2 策划第一批必须是 B0 基线冻结 + B1 只读契约——
"两仓互不认识对方代码，但能经 JSON 契约交换一条完整回执"。这是分布式系统工程师本能：
**先立契约，再谈融合**。P2 主导 Q1（批次切法）/Q3（映射唯一方案）/Q9（完美判据可测定义）。

### P1 探微（科学假设验证路线）——主张「先核查再策划 + 反证驱动」

**归因观点**：AGI 需自主提出科学假设 + 持续学习/内省推理。
→ 投射到 V4：先验证同步报告每个数字，再谈策划。抽验 3 个数字（v3_gate A1、main.py 21/21、
索引 digest 9a565741e1f72ab7），三个都对才进入策划。P1 主导 Q2（最小完美批次）/Q6（12→17 通道映射）/Q8（K 类 893 入选门槛）。

### P3 构弦（统一架构路线）——主张「三层一桥 + 语义十模块补齐」

**归因观点**：多模态统一联合训练 + DL 原理延续。
→ 投射到 V4：三层一桥架构成立（HoloAeon 发现层 → JSON 契约 → rehab_bridge 映射层 → JSON 契约 → ivsa 执行层）。
语义底座 19 → ≥60，用 ivsa 十模块反向补齐 HoloAeon。P3 主导 Q5（语义扩容目标）/Q7（六大战域与九领域映射）/Q10（双仓形态）。

### P4 持衡（对齐优先路线）——主张「风险终审 + 医学越界拦截」

**归因观点**：超对齐 + 安全先于能力。
→ 投射到 V4：医学词表分域加载（通用闸 10 token，医学 24E14+12E13 按域注入）；
许可冲突拦截（MIT vs MPL 2.0，两仓不互拷代码）；自动执行放大拦截（桥默认 simulated）。
P4 主导 Q4（皮肤词表分域）/Q11（执行与终审签字）。

## 3 V4 整体规划：V2.0 十二批次（替代 V1.0 八批次）+ 工程工作量

> V1.0 八批次太粗（每批做不到"每批都有可测完美判据"）。V2.0 拆成十二批，每批更小更可测。
> 切分依据：**契约→映射→分类→试点→扩容→记忆→准入→同步**八段，前两段各拆两批，后六段各一批。

| 批次 | 主题 | 主张分身 | 输入 | 产出 | 工时 | 累计 |
|---|---|---|---|---|---|---|
| **B0** | 基线冻结 | P2 | 两仓现态 | B0_基线票据.md + 12 维度锁 | 0.5 天 | 0.5 |
| **B1a** | 契约字段草案 | P2 | B0 票据 | contract_v1_draft.md（6 必填+4 可选） | 0.5 天 | 1.0 |
| **B1b** | 同参指纹互认实验 | P2 | B1a 草案 | contract_v1.json + 契约单测≥6 项 | 1 天 | 2.0 |
| **B2a** | 六机制 1:1 映射表 | P3 | 契约 v1 | mechanism_map.json（6 行） | 0.5 天 | 2.5 |
| **B2b** | 12→17 通道映射 + 词表分域 | P4 | B2a | channel_map.csv（12 行）+ 词表分域规则 | 1 天 | 3.5 |
| **B3** | 用途二次分类（K 知识源 893 / M 方法学 162 / T 工具链 78 / X 无关 15 / 待判 81） | P1 | 索引 1229 | 用途四标签.csv（1229 行）+ 抽样 40 | 2 天 | 5.5 |
| **B4** | 康复域试点 20 例 | P1 | B2+B3 | 试点20例_票据.md + 20 条 simulated 回执 | 2 天 | 7.5 |
| **B5** | 语义技能族扩容 19→≥60 | P3 | B3 K 类 | 语义技能≥60 + 十模块覆盖表 | 2 天 | 9.5 |
| **B6** | 记忆与流量（赫布落盘+通道配额） | P2 | B4 回执 | 落盘文件 + 重启一致测试 + 通道负载表 | 2 天 | 11.5 |
| **B7** | 分批准入（每批≤5，累计≤15） | P4 | B4+B5+B6 | 准入票据_B7-N.md | 持续每批 0.5 天 | 12.0+ |
| **B8** | 双仓开源同步 | P3 | 全链 | ivsa v1.2 插件默认关闭 + 双仓 SHA256SUMS 互认 | 2 天 | 14.0 |
| **B9** | V2 策划收口 + 五份交付物 | 综合 | 全链 | 融合总策划_v2.md + 台账_v2.csv + 判据.md + 风险.md + 四透镜.md | 1 天 | 15.0 |

**总工时**：B0–B9 合计 **15 人天**（B7 持续推进不计入）。按每周一批计，前十一批约 **11 周**。
**多次升级路径**：V2.0（本轮 12 批）→ V2.1（B7 持续准入 + 语义扩容到 100）→ V2.2（三场卡电场补齐 + 真实模型桥接）→ V3.0（康复域知识库全量入库）。

## 4 详细 SOP（面对执行智能体，逐步可跑）

### SOP-1 · B0 基线冻结（0.5 天）

```bash
# 第1步：跑齐 HoloAeon 4 道闸
cd F:\doubaowork\holoaeon
python scripts/v3_gate.py --json reports/b0_holoaeon_gate.json   # 32/32 PASS, A1=25/47/9
python -m unittest discover -s tests                              # 34 OK
python scripts/verify_skill_matrix.py                             # 17/17
python scripts/redline_scan.py                                    # 零违规

# 第2步：跑齐 ivsa 3 道闸
cd F:\doubaowork\开源发布_中西医融合康复工程_20261026\integrative-rehab-vsa
python main.py                                                    # 21/21 PASS
python -m unittest discover -s tests                              # 16 OK
python scripts/redline_scan.py                                    # violations=0

# 第3步：写 B0_基线票据.md（含 7 道闸输出 + 12 维度锁表）
# 第4步：写 dimension_lock.json，两侧单测各加一条断言读它
```
**完美判据**：7/7 全绿 + 12 维度锁 JSON 存在 + 两侧单测读到锁文件。

### SOP-2 · B1a 契约字段草案（0.5 天）

```bash
# 定义 JSON 契约字段（6 必填 + 4 可选）
# 必填：query, mech, top, channel, seal, domain_tag
# 可选：persona, evidence_class, measure_ts, trace_id
# 写成 docs/contract_v1_draft.md，先文档不写代码
```
**完美判据**：字段草案 6+4 全列出 + 每个字段有类型与示例 + 文档评审通过。

### SOP-3 · B1b 同参指纹互认实验（1 天）

```bash
# 实验：HoloAeon SHAKE-256 → 768 维 vs ivsa 768 维，同参（α=0.18）是否产同一摘要
python scripts/contract_fingerprint_test.py --dim 768 --alpha 0.18
# 预期：两侧摘要前 16 位一致（同参互认成立）
# 写 contract_v1.json + 契约单测 ≥6 项
python -m unittest tests/test_contract.py                          # ≥6 OK
```
**完美判据**：同参互认实验通过 + 契约单测 ≥6 项 OK + contract_v1.json 存在。

### SOP-4 · B2a 六机制 1:1 映射表（0.5 天）

```bash
# 写 mechanism_map.json（6 行：心跳/骨架/皮肤/语义/赫布/经络）
# 每行：{holoaeon_mech, ivsa_mech, params_shared, mapping_rule}
python scripts/gen_mechanism_map.py --out data/mechanism_map.json
python -m unittest tests/test_mechanism_map.py                     # 断言映射表长度==6
```
**完美判据**：映射表 6 行 + 单测断言长度 6 + 每行有 mapping_rule。

### SOP-5 · B2b 12→17 通道映射 + 词表分域（1 天）

```bash
# 写 channel_map.csv（12 行：LC01-LC12 → 1-2 个 17 通道）
python scripts/gen_channel_map.py --out data/channel_map.csv
# 写词表分域规则：通用闸 10 token，医学 24E14+12E13 按域注入
python scripts/gen_skin_lexicon.py --domain rehab --out data/skin_lexicon_rehab.json
python -m unittest tests/test_channel_map.py                       # 断言长度==12
python -m unittest tests/test_skin_lexicon.py                      # 断言通用闸无 E13/E14
```
**完美判据**：通道映射 12 行 + 通用闸断言无 E13/E14 + 词表分域规则存在。

### SOP-6 · B3 用途二次分类（2 天）

```bash
# 逐条 dispatch 打分，落 K/M/T/X
python scripts/classify_usage.py --index data/skill_matrix_index.json --out data/usage_labels.csv
# 抽样 40 条人工复核
python scripts/sample_usage.py --n 40 --out reports/b3_sample_40.md
# 待判 81 → ≤20
python -m unittest tests/test_usage_labels.py                      # 断言 1229 行全有值
```
**完美判据**：1229 行全有值 + 抽样 40 条复核通过 + 待判 ≤20。

### SOP-7 · B4 康复域试点 20 例（2 天）

```bash
# 20 例康复用例跑通"发现→映射→ivsa 只读回执"
python scripts/run_pilot_20.py --cases data/pilot_cases_20.json --out reports/b4_pilot_20.md
# 每例出 simulated 回执
python -m unittest tests/test_pilot_20.py                          # 断言 20/20 simulated
```
**完美判据**：20/20 simulated 回执 + 双仓 7 闸绿 + 回执含 evidence_class。

### SOP-8 · B5 语义技能族扩容 19→≥60（2 天）

```bash
# 新增技能必须落十模块之一，禁止造第十一模块
python scripts/expand_semantic.py --target 60 --out holoaeon/packs/rehab_semantic_pack.py
python -m unittest tests/test_semantic_expansion.py                # 断言 ≥60 且十模块全覆盖
```
**完美判据**：语义技能 ≥60 + 十模块全覆盖 + 无第十一模块。

### SOP-9 · B6 记忆与流量（2 天）

```bash
# 赫布权重落盘（memory L2）+ 重启一致测试
python scripts/hebbian_persist.py --out data/hebbian_weights.json
python scripts/test_restart_consistency.py                         # 断言重启前后 top-k 逐字相等
# 12→17 通道配额对表
python scripts/gen_channel_quota.py --out data/channel_quota.csv
```
**完美判据**：重启前后 top-k 逐字相等 + 通道负载表存在 + 落盘文件存在。

### SOP-10 · B7 分批准入（持续，每批 0.5 天）

```bash
# 每批 ≤5 技能过四硬闸 + 人工复核
python scripts/admit_batch.py --batch B7-1 --skills skill_a,skill_b,skill_c --out reports/B7-1.md
# 四硬闸：v3_gate / unittest / verify_skill_matrix / redline_scan
# 人工签字后才进执行层
```
**完美判据**：每批 4 硬闸绿 + 人工签字 + 准入票据存在。

### SOP-11 · B8 双仓开源同步（2 天）

```bash
# ivsa v1.2 插件默认关闭
python scripts/pack_ivsa_plugin.py --default-off --out releases/ivsa_v1.2.zip
# 双仓 SHA256SUMS 互认
python scripts/dual_repo_hash.py --holoaeon F:\doubaowork\holoaeon --ivsa F:\doubaowork\开源发布_中西医融合康复工程_20261026\integrative-rehab-vsa
```
**完美判据**：插件默认关闭 + 双仓哈希互认 + 许可分层无冲突。

### SOP-12 · B9 V2 策划收口（1 天）

```bash
# 五份交付物齐
# 1. 融合总策划_v2.md（12 批九字段）
# 2. 批次台账_v2.csv（一行一批）
# 3. 完美融合判据.md（每批判据可跑命令+通过线）
# 4. 风险与回滚登记.md（每条风险触发迹象+拦法+回滚）
# 5. 四透镜评审意见.md（四人各一段）
```
**完美判据**：五份齐 + 每批九字段满 + 每条判据可跑 + 无形容词判据。

## 5 定时任务规划（自动化批次推进）

> 用 WorkBuddy automation_update 工具创建。每个定时任务自包含（未来运行无会话上下文）。

### AT-1 · 每日基线闸门自检（recurring, 每日 09:00）

**任务**：跑 HoloAeon 4 道闸 + ivsa 3 道闸，7/7 全绿则继续当日批次工作；任一红则停工报障。
**rrule**：`FREQ=DAILY;BYHOUR=9;BYMINUTE=0`
**prompt**：
```
cd F:\doubaowork\holoaeon && python scripts/v3_gate.py --json reports/daily_gate.json && python -m unittest discover -s tests && python scripts/verify_skill_matrix.py && python scripts/redline_scan.py
然后 cd F:\doubaowork\开源发布_中西医融合康复工程_20261026\integrative-rehab-vsa && python main.py && python -m unittest discover -s tests && python scripts/redline_scan.py
7 道闸全绿则输出"今日基线 OK，可推进批次"；任一红则输出"基线红，停工报障"并列出哪道闸红。
```

### AT-2 · 每周批次推进检查（recurring, 每周一 10:00）

**任务**：检查上一批是否全绿（7 闸 + 12 维度锁 + 九字段满）；全绿则提示开下一批；未绿则提示补。
**rrule**：`FREQ=WEEKLY;BYDAY=MO;BYHOUR=10;BYMINUTE=0`
**prompt**：
```
检查 F:\doubaowork\holoaeon\reports\ 当前批次票据是否齐（九字段满+7闸绿+12维度锁未变）。
全绿则提示"可开下一批"，并列出下一批 SOP 步骤；未绿则提示"补完再开下一批"，并列出缺什么。
当前批次号读 reports/current_batch.txt。
```

### AT-3 · 每月 V2 策划进度报告（recurring, 每月 1 日 08:00）

**任务**：生成月度进度报告（已完成批次/进行中/待启动/风险/下月计划）。
**rrule**：`FREQ=MONTHLY;BYMONTHDAY=1;BYHOUR=8;BYMINUTE=0`
**prompt**：
```
读 F:\doubaowork\holoaeon\reports\ 所有批次票据，生成月度进度报告：
已完成批次清单（编号/主题/完成日期/工时）、进行中批次、待启动批次、风险登记、下月计划。
报告写到 reports\monthly_progress_YYYYMM.md 并上传到云端资料库空间 L0iHvPPzXwSZuSUaN6KcMX。
```

### AT-4 · 一次性：B0 基线冻结提醒（once, 2026-11-03 09:00）

**任务**：提醒启动 B0 基线冻结。
**scheduledAt**：`2026-11-03T09:00`
**prompt**：
```
今日启动 V2.0 十二批次第 B0 批：基线冻结。按 SOP-1 跑齐 7 道闸，写 B0_基线票据.md + dimension_lock.json。
完成后写 reports/current_batch.txt = "B1a"。
```

## 6 反模式 + 已知坑

### 反模式（V4 不抄）
1. **不合并两套引擎**（不搬 meridian_mechanism.py，不搬 mech.py）
2. **不合并编号空间**（70 ≢ 1229，17 ≢ 12，只做映射表）
3. **不把 1229 全量注册进 kernel.skills**（A1 锁不可动）
4. **不动 ivsa 21 组自检与医学红线**
5. **不接设备、不出剂量、不做诊断**
6. **不为融合率硬塞 X 类 15 个**
7. **不许跨批并行**（一批未全绿，不许开下一批）

### 已知坑（V4 新增）
| # | 现象 | 原因 | 处理 |
|---|---|---|---|
| V4-1 | v3_gate.py --json 裸 --json 报错 | 必须带值 | `--json <path>` |
| V4-2 | 全量扫索引 40-60 秒 | 1229 条 | 前台超时转后台任务 |
| V4-3 | skill_matrix 装入后 EXTRA_PACK_ORDER=9 | 第9扩展包旁挂 | 裸内核仍 25/47，A1 未破；assertGreaterEqual(7) 仍通过 |
| V4-4 | 皮肤词表若并通用闸则误熔断 | 医学词表污染 | 通用闸 10 token 固定，医学按域注入 |
| V4-5 | 12→17 通道若算术推导则冲突 | channel=idx%17 错 | 映射表 12 行写死，禁止算术 |
| V4-6 | 赫布权重不落盘则重启即失 | 只在进程内存 | B6 落盘 + 重启一致测试 |
| V4-7 | 语义底座仅 19（1.5%） | 最薄 | B5 扩到 ≥60，落十模块之一 |

## 7 验收判据（V4，逐条可判定）

- **A1（基线）** HoloAeon 4 闸 + ivsa 3 闸 = 7/7 全绿；12 维度锁未变；
- **A2（确定性）** DIFF=0 仍 `2fc892cf9af6e755`；spec.VERSION 仍 0.9.1；
- **A3（契约）** B1b 同参互认实验通过；契约单测 ≥6 项 OK；contract_v1.json 存在；
- **A4（映射）** B2a 映射表 6 行 + B2b 通道映射 12 行 + 词表分域规则存在；通用闸无 E13/E14；
- **A5（分类）** B3 1229 行全有值 + 抽样 40 通过 + 待判 ≤20；
- **A6（试点）** B4 20/20 simulated 回执 + 双仓 7 闸绿；
- **A7（扩容）** B5 语义技能 ≥60 + 十模块全覆盖 + 无第十一模块；
- **A8（记忆）** B6 重启前后 top-k 逐字相等 + 通道负载表存在；
- **A9（准入）** B7 每批 4 硬闸绿 + 人工签字 + 准入票据；
- **A10（同步）** B8 插件默认关闭 + 双仓哈希互认 + 许可无冲突；
- **A11（收口）** B9 五份交付物齐 + 每批九字段满 + 每条判据可跑 + 无形容词；
- **A12（定时）** AT-1 每日闸门自检运行 + AT-2 每周批次推进检查运行 + AT-3 每月进度报告生成；
- **A13（约束）** dependencies=[] 未破；六护城河零违反；医学红线零违反；V1/V2/V3 既有 golden 全保留。

## 8 立场（写进报告，不要只写代码）

V1.0 八批次太粗，因为你要的是"每批完美融合"，八批做不到"每批都有可测的完美判据"。
V2.0 十二批次把契约层与映射层各拆两批，让"完美判据"落到每批都能 7 闸全绿 + 九字段满。
**融合的诚实性在于敢写"这个不用"——X 类 15 个明确不纳入，写进票据而不是藏着。**

四分身归因综合投射：P2 筑基的地基先行（契约+映射+闸门）+ P1 探微的先核查再策划（抽验三数字）+
P3 构弦的三层一桥（语义十模块补齐）+ P4 持衡的风险终审（医学词表分域+许可冲突拦截）——
四派路线在"维度不变 + 医学红线 + 碳基终裁"这一点上收敛。

**1229 个技能 100% "纳入"基座，但永远不是 100% "执行"。** 这不是妥协，
这是保住两个项目各自维度锁的唯一走法。HoloAeon 的可信度建立在"47 个技能全部过闸"，
ivsa 的可信度建立在"21 组自检 + 零剂量 + C0 不写成疗效"。
任何一方为了"看起来融合得更彻底"去破坏自己的锁，都会让整套东西从"可审计"退化成"看起来很大"。

投喂结束。潮起开门，潮落闭嘴。