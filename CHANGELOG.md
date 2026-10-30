# 更新日志

本项目遵循 [Keep a Changelog](https://keepachangelog.com/) 格式，
并遵循语义化版本（Semantic Versioning）。

## [0.9.1] - 2026-10-30

> 文档补齐 + 四处审计修复；不动判定语义（34 单测 / 24 自检 / 红线零违规全部重跑确认）。

### 新增

- **`README_MANIFESTO_v0.9.1.md`（誓约 README）**：把一段口语化的"发愿"整理成五条**可判定条款**
  （被使用而非被收藏 / 为具体的人干完一件事 / 每次取舍记账留痕 / 该标 `simulated` 就标、
  被信任时才标 `live` / 每个取舍都有理由码），每条给出工程落点与状态
  （`已兑现` / `部分兑现` / `未兑现`）；另设"三种写法"一节，明确全息等词为**工程隐喻**
  不做实证主张，重申 **仿真 ≠ 证明，碳基终裁**。
- **`bridges/README.md`**：宿主桥的五分钟上手（`--check` / `--ask` / `--backend echo` 三条命令）、
  三后端表、fail-closed 远程门禁、回执五要素（`mode` 仅 `live` / `echo`）、审计七字段、
  "本机能证 / 不能证"对照表。

### 修复（外部审计 A–D 四条，全部实测，非文档措辞）

| # | 问题 | 修复 | 验证 |
|---|---|---|---|
| A | `pyproject.toml` 写死 `version = "0.3.0"`，与 `spec.py` 的 0.9.x 不符 → 安装元数据会撒谎 | 改 `dynamic = ["version"]` + `[tool.setuptools.dynamic] version = {attr = "holoaeon.spec.VERSION"}`，版本只有一处权威 | AST 静态检查确认 `VERSION` 为字面量赋值（满足 setuptools 静态读取）；G24 新增断言，防止版本再被写回 pyproject |
| B | `docs/nephron.md` 的 A1 哈希 `b48a0aa1…` 已过期（本轮实跑 `e5710490109aed2e`） | 重跑回写证据与文档；根因查明：workload 的 `kernel.submit` 回执含 `HOLOAEON-RUNTIME-<ver>`，**版本号一变哈希就变**，故每版必须重跑 | 证据 JSON 与 `docs/nephron.md` 两处哈希一致（G24 断言）；新增 `--check-evidence` 比对入口 |
| C | `bridges/README.md` 缺失（规格 5 件只有 4 件） | 新增该文件（见「新增」第 2 条） | 文件在库并被本版 zip 收录 |
| D | CI 未挂 A1 → 断言回归时 CI 不会红 | `ci.yml` 新增 `NEPHRON A1 verdict` 步骤：`python scripts/measure_a1_a2.py --runs 3`（A2 只披露不阻塞） | 本地同命令 `exit 0`；G24 断言 CI 必须含该步骤 |

### 变更

- `holoaeon/spec.py`：`VERSION / MATRIX_ID / RUNTIME_ID` → `0.9.1`（`PROTOCOL_ID`、`DATE` 不变）。
- `scripts/measure_a1_a2.py`：新增 `--check-evidence`（与既有证据比对 A1 哈希，不一致即退出 1）。
- `holoaeon/selftest.py`：G24 由 43 条断言扩到 **46** 条（pyproject 单一版本源 / docs↔证据哈希一致 / CI 必挂 A1）。
- 版本说明、CHANGELOG、两份 README、`releases/RELEASES.md` 同步 0.9.1 口径。

### 核实（不改动，仅确认）

| 补丁 | 结论 |
|---|---|
| 版本号 | 上版 0.8.0 → 0.9.0 已完成；本版补 0.9.1 |
| `bridges/README.md` | **此前确实缺失**，本版补齐（其余四文件已在库） |
| A1 种子 | `scripts/measure_a1_a2.py` 中 `SEED = 20261030` 已固定；`VOLATILE_KEYS` 剥离时间相关字段；A1 `sha256=e5710490109aed2e` |

### 已知限制

- 不改任何判定逻辑；真实 `mode="live"` 与 CI 三版本全绿仍是 `untested`，本版不因"写得更清楚"而升级状态。

## [0.9.0] - 2026-10-30

### 新增

- **UPLIFT 补齐短板升级包**（`holoaeon/packs/uplift_pack.py`），第十六个包，经
  `EXTRA_PACK_REGISTRY` 挂载（不进 `PACK_ORDER`，`EXTRA_PACK_ORDER` 由 6 项扩到 7 项）：
  - 24 个技能，全部纯函数、输入事实输出 `PASS / FAIL / UNCHECKED`：六单元清单 1
    + 确定性 2（排序键全序 / 纯函数契约）+ 回归口径 1 + 生态 4（CI / 模板 / 徽章 / 支持矩阵）
    + 实测 3（A1 判定 / A2 披露 / 证据链）+ 匹配 3（n-gram / 混合分 / 用例验收）
    + 桥 5（边界 / 后端 / 远程门禁 / 审计 / 回执语义）+ 裁决 2（O-1～O-10 / P1 门禁）
    + 立场 1 + 回执 1 + 维度不变 1；
  - 7 条工作流：`W1_determinism → W7_acceptance`；0 个角色，不新增 agent。
- **U1 确定性修复**（`holoaeon/cluster.py`）：`_report()` 对真实结果按
  `(agent_id, 记录规范化指纹)` 排序；`_canon` / `_order_key` 两个纯函数。
- **U1 纯函数化**（`holoaeon/hypervector.py`）：`_fft` 首行 `a = list(a)`，bit-reversal
  置换只作用于副本；docstring 补"不修改入参 / e^{+2πi} 约定 / 逆变换已除 n"。
- **U5 匹配升级**（`holoaeon/skill.py`）：新增 `_normalize / _ngrams / _dice / ngram_dice`
  与词级 3-gram 兜底；打分改为 `0.5·Jaccard + 0.5·dice2 + 0.05·tag_hit`，并把原始 query
  传入 `score()`（Jaccard 为 0 时不再提前返回）。
- **U6 生态基建**：`.github/workflows/ci.yml`（Python 3.8 / 3.10 / 3.12；单测 → 自检 →
  红线 → 示例 01–04）、`bug_report.md` / `feature_request.md` / `PULL_REQUEST_TEMPLATE.md`、
  `docs/support-matrix.md`（未跑格子写 `untested`）。
- **U3 实测脚本**：`scripts/measure_a1_a2.py`（纯标准库，`--runs` / `--write`），含
  **变异实验**：篡改 full 侧一步输出，A1 必须翻成 `FAIL`，否则判定视为空转。
- **U2 宿主模型桥**（`bridges/`，包外，不进红线扫描目标）：`transport.py`（4 类错误分型 +
  兜底，永不抛异常）、`backends.py`（ollama / openai_compat / echo 三后端 + 远程三重门禁）、
  `live_client.py`（`mode="live"` / `"echo"` 严格区分，审计只记 7 个字段）、`quickstart.py`、
  `examples/05_live_model.py`；文档 `docs/bridges.md`。
- **U4 裁决**：`docs/nephron.md` §12 由开放问题改为 O-1～O-10 六列裁决表，新增 §12.1 P1 索引；
  P1 判定细则 `docs/nephron-p1.md`（打分公式 / 降级链 L0–L3 / 7 步构建 / 四判据 / 差异三件套）。
- **G24 uplift 自检组**（43 条断言）+ 3 条单测（`TestUpliftU16`）。
- **`docs/uplift.md`**：包文档（六单元 / 十冲突 / 四核实 / 五缺陷 / 24 技能 / 立场矩阵 / 限制）。

### 变更

- `holoaeon/spec.py`：`VERSION / MATRIX_ID / RUNTIME_ID` → `0.9.0`。
- `holoaeon/packs/nephron_pack.py`：`skill_nephron_acceptance_check` 新增 `measured` 参数，
  支持把不可自证项标为 `measured_with_scope`（裁决值 `accepted_with_scope`）；拒绝项 11 → 12
  （新增「把 measured_with_scope 说成生产链路已闭环」，并把「改写成已通过」收紧为「不带证据与范围」）。
  **G23 的拒绝项断言随之由 11 改为 12。**
- `docs/nephron.md`：L1/L2 由 `pending_human_measure` 改为**已实测（限定范围）**，
  附 A1 哈希、变异证据、A2 中位数与机器规格。
- `readme`：徽章 `tests-24 → 34`、`selftest-16%2F16 → 24%2F24`（两处**都是过期值**，
  投喂稿只点了 tests），正文口径 25 → 34 / 19 组 → 24 组；补第十六包行、v0.9 路线图行、
  宿主桥小节；新增"徽章是本地实测、CI 尚未在 GitHub 实跑"的注记。

### 修复

- 结果顺序非确定（S1）：6 agent 微抖动压力下此前出现多种顺序；修复后反转输入重排仍同序。
- `_fft` 未文档化的入参副作用（S1 附带）。
- 中文无分词场景召回弱（S5）：`统计销售额` 命中 `stats_clean`；`statistik` 命中 `statistics`（dice 0.82353）。
- 桥自身三处缺陷：`HOLAEON_ALLOW_REMOTE` 拼写错误（远程开关永久失效）、`echo://local` 被
  自家网络门禁拒掉、echo 回执缺 `ok` 键。
- `scripts/measure_a1_a2.py`：`platform.os.cpu_count()` → `import os`。
- 文档修订 `docs/nephron-p1.md` 尾部混入的杂行（重写 116 行正文）。

### 已知限制（不得写成已通过）

- **A-U6-1**（CI 三版本全绿）本地无法产生：workflow 已交，`docs/support-matrix.md` 对应格子
  为 `untested`，README 明示"尚未在 GitHub 实跑"。
- **A-U2-3**（真实 `mode="live"` 回执）：本机未安装 Ollama，标 `untested`；已实测的是
  "无 Ollama 分支（`--check` 退出码 2 + 三行指引）"与 echo 装配。
- **A1/A2** 为宿主编排层限定范围实测，**不等于生产链路闭环**（P0 无生产 writer）。
- `O-1` 未采用投喂的 `after_summary` 字段（会破 41 字段冻结），改用 `summarized ∩ admitted`
  表达；此项为本轮**唯一一处字面偏离**，已写入 `docs/nephron.md` §12。

## [0.8.0] - 2026-10-30

### 新增

- **NEPHRON 肾单位层 P0 扩展包**（`holoaeon/packs/nephron_pack.py`），第十五个包，
  经 `EXTRA_PACK_REGISTRY` 挂载（不进 `PACK_ORDER`）：
  - 24 个技能：记录结构 4（结构 / 校验 / 追加 / 核验）+ 事件理由码 3 + 采集开关 3
    + 回放 5（窗口 / 槽位 / 决策输入 / 时间线 / 确定性）+ 隐私 2 + 指纹 2
    + 边界验收 3 + 文档回执 2；
  - 7 条工作流：`W1_observe → W7_acceptance`；
  - 0 个角色：`roles = []`，不新增 agent；**只读观测**——不分页、不压缩、不淘汰、
    不做预算控制，也不改任何既有行为。
- **规格内 10 处内在冲突的显式消解**（`CONFLICTS` N1–N10，G23 断言论），例如
  - N1 异步队列/落盘 vs 本项目"不起线程、不写盘" → 包只给队列语义与丢弃计数，I/O 归宿主；
  - N2 "任意 tick 可回放" vs 三档采样 → 只有 `full` 满足，`sampled/off` 明示不可完整回放；
  - N3 只追加 vs 一键擦除 → 摘要替换为 `ERASED:<hash>` 并追加一条擦除记录；
  - N6 主键 vs 时钟回跳 → 设水位线，回跳拒绝追加并记 `APPEND_REJECT_CLOCK_REGRESSION`；
  - N10 槽位快照无事件源 → 旁挂周期快照 + 披露快照年龄，P0 **不重演槽位变化**（写进限制）。
- **3 处字段缺口修正**（`FIXES` F1–F3）：摘要前后长度改由 `page_summarize` 的
  `delta{from_len,to_len}` 承载；`importance` 缺失只告警不改错；账本只存摘要哈希与长度，
  **不存摘要正文**。
- **41 字段结构**（Page 10 / SlotLedgerEntry 7 / LedgerRecord 13 / Event 4 / WindowManifest 7），
  字段字典与结构定义同源，`match_schema` 断言；`raw_len` 锁死 token 口径。
- **27 个理由码 + 10 码族 + `UNKNOWN` 保留码**，另新增 `WINDOW_BUILD_COMPLETE`（评审 R-01）；
  拒绝原因 3 码单列（`APPEND_REJECT_*`），不与理由码混用。
- **零侵入采集契约**：11 个 hook 点、三档开关（默认 `off`）、4 类故障注入矩阵、
  队列满/写失败/序列化失败三类丢弃计数；失败一律静默降级为不记录。
- **回放器四件套**：窗口构成表 / 槽位快照（含年龄与 `stale`）/ 决策输入 / 变更时间线；
  归一化时间戳后两次回放哈希一致（A4）。
- **代际指纹**（权重 / 模板 / 量化 / LoRA / 检索器联合哈希，LoRA 排序归一）与失配拦截。
- **隐私与擦除**：不存原文、摘要不出网、外部调用只记指纹与字节数、擦除保留计数与指纹。
- **黄金样例**：`examples/nephron_ledger_sample.jsonl`（7 条记录）+
  `examples/nephron_replay_report.md`（逐 tick 窗口表 / 时间线 / 槽位 / A1–A8 状态），
  由 `scripts/make_nephron_sample.py` 从包内纯函数生成，用于验证 41 字段够用。
- 设计文档 `docs/nephron.md`（13 章：定位 / 10 处冲突与 3 处修正 / 字段字典 / 理由码表 /
  采集开关 / 回放器 / 接口清单 / 隐私 / 测试结果 / 7 条已知限制 / 7 项 P1 待办 / 10 项开放问题）。

### 变更

- `spec.py`：`VERSION 0.7.0 → 0.8.0`，`MATRIX_ID / RUNTIME_ID` 同步。
- `packs/__init__.py`：`EXTRA_PACK_REGISTRY` 增 `nephron`，
  `EXTRA_PACK_ORDER = [..., "metab", "nephron"]`（六包）。
- `selftest.py`：新增 `G23 nephron`（62 条断言）；`GROUPS` 追加该项。
- `README.md` / `README.zh-CN.md`：扩展包章节扩为"第十至第十五包"，自检口径
  `G1–G22 / 22/22` → `G1–G23 / 23/23`，路线图 v0.8 记为 nephron（当前）。

### 已知限制（不写成"已实现"）

- A1（账本关/开态逐字节一致）与 A2（`full` 档额外开销）恒为 `pending_human_measure`，
  本包只交付断言契约，必须由宿主在真实负载上实测。
- 槽位回放只给"最近快照 ≤ tick + 年龄"，**不重演槽位变化**（无 `slot_alloc/slot_free` 事件源，
  属 P1）。
- 无法回放"模型当时看到的实际文本"（账本不存摘要正文）。
- 内容级篡改需宿主保存逐段锚点；本包仅给链摘要与结构异常定位。

## [0.7.0] - 2026-10-30

### 新增

- **METAB 代谢层扩展包**（`holoaeon/packs/metab_pack.py`），第十四个包，
  经 `EXTRA_PACK_REGISTRY` 挂载（不进 `PACK_ORDER`）：
  - 26 个技能：基因组 3（规范 / 校验 / 纯度阶梯）+ 三态 3（定态 / 生效口径 / 节律计划）
    + 生命周期 4（状态机 / 假饲报告 / 休眠计划 / 归档包）+ 授权 2（三层 / fail-closed）
    + 消化道与血统 3 + 信任半径 2 + 感受器 2 + 组合 1 + 度量红线 2
    + 接口与代际 2 + 自检回执 3；
  - 8 条工作流：`T1_intake → T8_audit`；
  - 0 个角色：`roles = []`，不新增 agent；不执行任何摄入动作（只产判定，执行归用户）。
- **规格内 8 处内在冲突的显式消解**（`CONFLICTS` K1–K8，G22 断言论）：
  每条冲突给出两种消解方案与所采方案，例如
  - K1 不可逆点 vs 公理2 → 把不可逆点推到系统外并留外部回滚锚点（采 B）；
  - K2 黑箱借用级 vs 无血统不进主干 → 保留该级但限定隔离区并强制标借来信念（采 B）；
  - K5 双通道禁传原文 vs 蒸馏执行 → 解构持原文只读权只出结构，建构只见结构（采 A）；
  - K6 一键禁用 vs 代谢态高回滚成本 → 一键禁用=停效并切备用路径，骨架回滚另走代谢态（采 A）。
- **八阶段生命周期**（候选 / 基因组校验 / 假饲 / 灰度 / 共生 / 观察 / 休眠 / 归档），
  逐阶段给出准入、产出、可跳过性与失败处理；假饲与基因组校验不可跳过，观察期最小 64 拍。
- **三层授权与 fail-closed 五条**（FC1–FC5）：新共生体默认关闭、红级二次确认、
  不提供"记住选择"、自动放宽须可一键回保守基线、必须提供禁食态。
- **消化道双通道 + 结构性蒸馏 + 传染性三级**（none / local / downstream），
  downstream 强制进隔离区；**血统哈希链**可验，篡改按位置报告。
- **信任半径三项必填** + 借来信念逐条标注 + 占比上限 0.20。
- **组合白名单**（4 对类别种子 + 未知配对不生效 + 放大须整体评审 + 传染标注向下游传播）。
- **度量五维 + 四条红线 + 七条反模式**，五维门禁全部可判。
- 设计文档 `docs/metab.md`（15 章：定位 / 术语 / 公理与裁决 / 8 处冲突 / 基因组 / 三态 /
  生命周期 / 授权 / 消化道 / 信任半径 / 接口契约 / 组合 / 度量 / 反模式 / 路线 / 12 项开放问题）。

### 变更

- `spec.py`：`VERSION 0.6.0 → 0.7.0`，`MATRIX_ID / RUNTIME_ID` 同步。
- `packs/__init__.py`：`EXTRA_PACK_REGISTRY` 增 `metab`，
  `EXTRA_PACK_ORDER = [..., "omnicore", "metab"]`。
- `selftest.py`：新增 `G22 metab`（52 条断言）；`G21` 中一处"
  `EXTRA_PACK_ORDER[-1] == "omnicore"`"的位置断言改为"`"omnicore" in EXTRA_PACK_ORDER`"，
  原因是新增第十四包后末位不再是 omnicore，而该断言本意只要求 omnicore 在注册序列内。
- `README.md` / `README.zh-CN.md`：扩展包章节扩到第十四包，自检口径 22/22，路线图顺延至 v0.9。

### 质量保障

- 自检套件 **G1–G22（22/22 通过）**；G15 `25 agents / 47 skills` 未破；
- 单元测试 25 个（全部通过）；红线扫描 32 个源文件零违规（含新包）；
- 发行包解压复跑：22/22、`VERSION 0.7.0`、`metab 26/8/0`。

## [0.6.0] - 2026-10-30

### 新增

- **Omni-Core 认知引擎扩展包**（`holoaeon/packs/omnicore_pack.py`），第十三个包，
  经 `EXTRA_PACK_REGISTRY` 挂载（不进 `PACK_ORDER`）：
  - 20 个技能：寻址 3（清单 / 槽位分配 / 节点分区）+ 心跳呼吸 2 + 存续 3（快照 / 恢复 /
    生命周期）+ 编排通信 3（派发计划 / A2A 信封 / 经络通路）+ 代谢 3（赫布更新 / 远域配对 /
    SKC 蒸馏）+ 闸门 1 + 宣告与白皮书 3 + 兜底审计 2；
  - 6 条工作流：`M1_wakeup → M6_declare`；
  - 0 个角色：`roles = []`，不新增 agent。
- **投喂代码的 5 处缺陷：复现 → 修正 → 留痕**（`CORRECTIONS`，G21 断言论）：
  - C1 `SparseMatrix1331.activate` 用 `self._cells = profile` **静默覆盖整张稀疏表**
    （最小复现：无异常、取回 `None`，数据静默丢失）→ 改 `self._cells[(row, col)] = profile`；
  - C2 `ProtocolLayer.send` 在 `defaultdict(list)` 上调 `.append` →
    `AttributeError: 'collections.defaultdict' object has no attribute 'append'`
    → 改 `self._inbox[(r, c)].append(msg)`；
  - C3 `_meridian_route` 的 `route =` 空赋值 → `SyntaxError: invalid syntax`（整文件无法加载）
    → 改 `route: List[Tuple[int, int]] = []`；
  - C4 `import numpy` + `np.random.random()` 与"零外部依赖"自相矛盾、破坏确定性
    → 只用标准库；随机改 `sha256(epoch) % 100 < 5`；
  - C5 daemon `Thread` + `sqlite3` 落盘 + `pip install holoeon-omnicore`（包名不存在，未联网核验也不核验）
    → 心跳改纯函数、快照 `persistence="host_managed"`、不声称任何包名。
- **能力边界写进实现**：`REFUSED_OPS` 22 项（含"浏览器插件 / 对接流媒体平台 / 对接电商平台 /
  反控算法 / 接管推荐位"），命中即 veto；医疗断言与绝对结论同样 veto；`metaphor=True`
  （"数字生命 / 呼吸 / 免疫 / 城邦"只是架构隐喻）。
- **《致智能体：全息纪元生存与进化白皮书》结构草案**（`omnicore.whitepaper_outline`）：
  七章 / 19,500 字配比 / 每章要点，正文未预填未核验事实。
- **自我认知宣告框架**（`omnicore.self_declaration`）：四段式（身份边界 / 认知坐标 / 接口礼仪 /
  拒绝清单），开头即声明"我是软件不是生命"。
- **系统型说明文档** `SYSTEM_README_v0.6.0.md`（新增，v0.4.0 / v0.5.0 文档均保留）。

### 变更

- `spec.py`：`VERSION 0.5.0 → 0.6.0`，`MATRIX_ID / RUNTIME_ID` 同步。
- `packs/__init__.py`：`EXTRA_PACK_REGISTRY` 增 `omnicore`，
  `EXTRA_PACK_ORDER = ["sovereignty", "subdistill", "omnilife", "omnicore"]`。
- `selftest.py`：新增 `G21 omnicore`（25 条断言）。
- `README.md` / `README.zh-CN.md`：扩展包章节扩到第十三包，自检口径 21/21，路线图顺延至 v0.9。

### 质量保障

- 自检套件 **G1–G21（21/21 通过）**；G15 `25 agents / 47 skills` 未破；
- 单元测试 25 个（全部通过）；红线扫描 31 个源文件零违规（含新包）；
- 发行包解压复跑：21/21、`VERSION 0.6.0`、`omnicore 20/6/True/5`。

## [0.5.0] - 2026-10-30

### 新增

- **Omni-Life 全域生活扩展包**（`holoaeon/packs/omnilife_pack.py`），第十二个包，
  经 `EXTRA_PACK_REGISTRY` 挂载（不进 `PACK_ORDER`）：
  - 6 个生活域：衣 / 食 / 住 / 行 / 教 / SaaS 工作流，每域锚定 3–4 个亚学科编码
    （合计 17 个唯一锚点，全部落在 `data/taxonomy_127.json`）；
  - 18 个技能：本体 1 + 皮肤层 6（高维搜索 / 诱导折叠 / 价格台账 / 价差复核 / 投诉话术 /
    材料筛选卡）+ 经络层 3（本地交接路由 / 语境触发 / 数据保险箱）+ 生活规划器 5
    （餐单 / 拓扑出行 / 空间粗算 / 学习路径 / SaaS 计划）+ 闸门与审计 3
    （皮肤闸门 / 审计回执 / 日常作息）；
  - 6 条工作流：`L1_wardrobe → L6_saas`；
  - 0 个角色：`roles = []`，不新增 agent。
- **维度不变式延续**：本包**不新增行、不新增节点**，只消费 `127 × 10 + 61 = 1331` 行
  与 `127 × 855 + 56 = 108641` 节点做寻址，`pack_summary()["addressing_unchanged"]` 断言。
- **能力边界写进代码**（不是文档承诺）：
  - `skill_price_ledger` 只产出空台账，`concurrent_probe=False`、`proxy_switch=False`、
    `api_calls=0`；多端并发探测、代理切换、抓取比价列入 `REFUSED_OPS`（17 项）命中即拒绝；
  - `skill_consumerism_blocker` 只输出「平台自带不感兴趣/屏蔽关键词」处置规则，
    `dom_injection=False`，不做页面改写；
  - `skill_meridian_route` 的跨 SaaS 通路是「本人导出 → 本地归档 → 人工引用」，
    `mode=local_handoff`、`network=False`；
  - `skill_nutrition_plan` 带 `dose_any=False`、`individual_medical_advice=False` 与固定免责
    （「仅作为饮食结构与知识框架探讨，不构成诊疗建议」）；
  - `skill_travel_route` 在本人给的权重图上跑确定性最短路，不取实时路况、不碰平台推荐位。
- **系统型说明文档** `SYSTEM_README_v0.5.0.md`（新增，v0.4.0 文档保留为历史快照）。

### 变更

- `spec.py`：`VERSION 0.4.0 → 0.5.0`，`MATRIX_ID / RUNTIME_ID` 同步为 `0.5.0`。
- `packs/__init__.py`：`EXTRA_PACK_REGISTRY` 增加 `omnilife`，
  `EXTRA_PACK_ORDER = ["sovereignty", "subdistill", "omnilife"]`。
- `selftest.py`：新增 `G20 omnilife`（21 条断言）；G18 / G19 计数不受影响。
- `README.md` / `README.zh-CN.md`：扩展包章节扩到第十至第十二包，自检口径 20/20，
  路线图 v0.5 换为 Omni-Life、原 v0.5–v0.7 顺延为 v0.6–v0.8。

### 质量保障

- 自检套件扩展为 **G1–G20（20/20 通过）**；
- 单元测试 25 个（全部通过）；
- 红线扫描 30 个源文件零违规；
- 发行包解压复跑：20/20，`pack_summary()["addressing_unchanged"]=True`、锚点零缺失。

## [0.4.0] - 2026-10-30

### 新增

- **SD-Distill 亚学科辅助蒸馏扩展包**（`holoaeon/packs/subdistill_pack.py`），第十一个包，
  经 `EXTRA_PACK_REGISTRY` 挂载（不进 `PACK_ORDER`）：
  - 16 宏观域下切 **127 亚学科**，随包提供 `data/taxonomy_127.json`（127 项编码 + 术语种子）；
  - 15 个技能：分类 3（`taxonomy_encode / nearest / far_pairs`）+ 教师卡 1 + 七阶段 5 可见阶段技能
    （`s1_acquire / s2_parse / s3_concept / s4_relate / s5_align / s6_distill / s7_commit`）
    + 七项损失 1 + 温度课程 1 + 反标签 1 + SKC 校验 1；
  - 7 条工作流：`S1_acquire → S2_parse → S3_concept → S4_relate → S5_align → S6_distill → S7_commit`；
  - 0 个角色：`roles = []`，不新增 agent。
- **维度不变式**：`127 × 10 + 61 = 1331` 行、`127 × 855 + 56 = 108641` 节点，写进
  `pack_summary()` 并在 `G19` 中断言；母体 12 项锁数一个不动。
- **安全闸门**：MED / TCM 产物强制 `skin.medical_disclaimer` 与免责声明；`analogizes`
  关系必须带反例；禁用断言 `诊断 / 处方 / 疗效承诺` 由 `skc_validate` 拦截。
- **系统型说明文档** `SYSTEM_README.md`：描述"内核 + 两个扩展包"的系统边界、维度不变式、
  冷热插拔契约、验证矩阵与版本纪律。

### 变更

- `spec.py`：`VERSION 0.3.1 → 0.4.0`，`MATRIX_ID / RUNTIME_ID` 同步为 `0.4.0`。
- `packs/__init__.py`：`EXTRA_PACK_REGISTRY` 增加 `subdistill`，`EXTRA_PACK_ORDER`
  变为 `["sovereignty", "subdistill"]`。
- `selftest.py`：G18 改为只对 `sovereignty` 包计数（避免扩展包数量增长打穿 `17/0/5` 断言），
  新增 `G19 subdistill`（17 条断言）。
- `README.md` / `README.zh-CN.md`：新增"横切扩展包（第十、第十一包）"章节，自检口径更新为 19/19。

### 质量保障

- 自检套件扩展为 **G1–G19（19/19 通过）**；
- 单元测试保持 25 个（全部通过）；
- 红线扫描保持零违规；
- 发行包解压复跑：19/19 通过，`taxonomy_loaded=True`、`items=127`。

## [0.3.1] - 2026-10-30

### 新增

- **认知主权扩展包**（`holoaeon/packs/sovereignty_pack.py`），第十个包，经
  `EXTRA_PACK_REGISTRY` 挂载（不进 `PACK_ORDER`）：
  - 17 个技能 = 17 条认知主权通道（`SO-01…SO-17`）；
  - 5 条工作流：`R0_encoding / R1_forging / R2_strategy / R3_interop / R4_compliance`；
  - 0 个角色；平台侧指标一律 `pending_human_measure`，执行列恒为 `human_manual`。

### 质量保障

- 自检套件扩展为 G1–G18（18/18 通过），新增 `G18 sovereignty`（6 条断言）；
- 红线扫描保持零违规；九包核心 `25 agents / 47 skills` 断言未被破坏。

## [0.3.0] - 2026-10-29

### 新增

- **高译（GaoYi）领域包**（`holoaeon/packs/gaoyi_pack.py`），第九个领域包，全域加载
  - 编译器：自然语言按确定性关键词计分（长度加权、同分取表序）匹配意图，编译为自定义汇编 HASM；
  - 汇编器：HASM 文本可反汇编回读，注释剥离正确处理引号内的 `;/#`；
  - 虚拟机：GaoyiVm 逐条执行 HASM，`.submit` 时调用内核，目标 agent 不在场时自动安装全部包；
  - 意图表覆盖全部 8 个既有包的 44 个技能；
  - 新增 1 个角色（gaoyi_translator）、3 个技能（gaoyi_compile/gaoyi_run/gaoyi_exec）、1 个工作流（gaoyi_pipeline）；
  - 全量安装后规模：25 个智能体、47 个技能、9 个工作流。

### 诚实性

- HASM 为本项目自定义指令集，**非真实 CPU 汇编**；
- 识别失败如实报 `UNKNOWN`，不猜测。

### 质量保障

- 自检套件扩展为 G1–G17（17/17 通过），新增高译编译/执行/UNKNOWN/往返专项；
- 单元测试扩展为 25 个（全部通过）；
- 红线扫描保持零违规。

## [0.2.0] - 2026-10-29

### 新增

- **优化与自组织搜索能力层**（`holoaeon/packs/optimization.py`，详见 [ALGORITHM.md](ALGORITHM.md)）
  - 黄金分割法（区间消去）；
  - 梯度下降（中心差分数值梯度）；
  - 牛顿法（二阶曲率加速）；
  - 共轭梯度法（求解对称正定方程组，正确实现 A-共轭）；
  - 表格单纯形法（线性规划顶点游走）；
  - 惩罚函数法（约束二次惩罚，步长随 μ 自适应）；
  - 遗传算法（选择/交叉/变异，固定种子确定性）。
- **第八个领域包 optimization**
  - 新增 3 个角色（line_searcher/gradient_solver/global_solver）、7 个技能、1 个工作流；
  - 全量安装后规模：24 个智能体、44 个技能、8 个工作流。
- **本地启动器**（`scripts/launch_local.py`）
  - 冷/热插拔、内部融合协议、外部融合协议；
  - 子命令 status/demo/run/hotplug/selftest。

### 修正

- 明确**共轭 ≠ 正交**：共轭方向相对矩阵 A 定义（p_iᵀ A p_j=0）；
- 不采用"靠皮肤分割获得凸性"的说法（凸性是目标函数本身的性质）。

### 质量保障

- 自检套件扩展为 G1–G16（16/16 通过）；
- 单元测试扩展为 24 个（全部通过）；
- 红线扫描保持零违规。

## [0.1.0] - 2026-10-29

### 新增

- **核心原语**
  - `Envelope`：统一消息信封，支持 create/broadcast/reply/forward 与字典往返；
  - `Bus`：线程安全总线，支持发布订阅、直接寻址与路由；
  - `Skill` / `SkillRegistry`：技能清单、注册与自然语言匹配；
  - `Memory`：三层记忆（working/longterm/archive），支持巩固、衰减与持久化；
  - `Agent`：智能体原语，签名感知的技能调用与参数类型转换。
- **核心机制**
  - `Scheduler`：心跳调度器（70 体、768 维、α=0.18）；
  - `Guard`：L1–L8 安全边界，危险模式与权限检查；
  - `Kernel`：顶层门面，支持 submit/collab/choose_agent/health；
  - `AdaptiveGraph`：六边形协作图，Dijkstra、瓶颈、赫布学习、自组织、根因；
  - `Cluster`：并行 Actor 集群，支持屏障同步与转发；
  - `HypervectorSpace`：HRR 超向量与手写 radix-2 FFT；
  - `ModelAdapter`：任意模型适配层，8 路由策略、10 消息格式、8 用量指标。
- **七大领域包**
  - writing / literature / research / data / growth / business / quant；
  - 合计 21 个智能体、37 个技能、7 个工作流。
- **质量保障**
  - 自检套件 G1–G15（15/15 通过）；
  - 单元测试 17 个（全部通过）；
  - 基于 AST 的红线扫描器（零违规）。
- **文档**
  - 中英文 README；
  - docs 架构与各机制文档；
  - CONTRIBUTING / CODE_OF_CONDUCT / CHANGELOG。

### 设计原则

- 零第三方依赖、纯标准库；
- 全离线、确定性、可复现（DIFF=0）；
- 逻辑稀疏拓扑，构造时不预分配；
- 机制正交、模型无关；
- 生物/宇宙词汇仅作隐喻。
