# HoloAeon 认知主权 · SD-Distill · 全域生活 · 全息纪元 · 代谢层 · 肾单位 · 补齐短板 · 冷热插拔赋能升级包 · RELEASES

> 版本化目录：**只增不覆盖**。每个版本一个目录入口、一份说明、一份哈希。
> 选择版本 = 选择下表的 tag；任何版本都可独立解压、独立自检、独立运行。
> 密令 **潮起开门，潮落闭嘴**

---

## 版本索引

| 版本 | Tag | 日期 | 内核包 | 认知主权包 | 自检 | 状态 |
|---|---|---|---|---|---|---|
| **v0.9.0** | `v0.9.0` | 2026-10-30 | `releases/holoaeon_v0.9.0_20261030.zip` | —（沿用 V3.1） | 内核 **24/24** | 当前 |
| v0.8.0 | `v0.8.0` | 2026-10-30 | `releases/holoaeon_v0.8.0_20261030.zip`（72 文件 / 303,727 B） | —（沿用 V3.1） | 内核 **23/23** | 历史（保留） |
| v0.7.0 | `v0.7.0` | 2026-10-30 | `releases/holoaeon_v0.7.0_20261030.zip`（66 文件 / 250,721 B） | —（沿用 V3.1） | 内核 **22/22** | 历史（保留） |
| v0.6.0 | `v0.6.0` | 2026-10-30 | `releases/holoaeon_v0.6.0_20261030.zip`（63 文件 / 201,755 B） | —（沿用 V3.1） | 内核 **21/21** | 历史（保留） |
| v0.5.0 | `v0.5.0` | 2026-10-30 | `releases/holoaeon_v0.5.0_20261030.zip`（61 文件 / 175,959 B） | —（沿用 V3.1） | 内核 **20/20** | 历史（保留） |
| v0.4.0 | `v0.4.0` | 2026-10-30 | `releases/holoaeon_v0.4.0_20261030.zip`（59 文件 / 152,485 B） | `releases/cs1331_cognitive_sovereignty_matrix_V3.1.0_20261030.zip`（41 文件 / 135,421 B） | 内核 **19/19** · 认知主权 **14/14** | 历史（保留） |
| v0.3.1 | —（未打 tag，仅本地留档） | 2026-10-30 | `holoaeon_v0.3.1_20261030.zip`（本地 F 盘，56 文件 / 128,196 B） | — | 内核 18/18 | 历史 |
| v0.3.0 | — | 2026-10-29 | `holoaeon_v0.3.0_20261029.zip`（本地 F 盘，120,521 B） | — | 内核 17/17 | 历史 |

> 说明：`v0.3.1` 与 `v0.3.0` 的发行包在打本次版本之前生成，未同步进本仓库 `releases/`；
> 它们**未被覆盖、仍在本地 F 盘留存**，可随时按需补入。本目录自 `v0.4.0` 起对所有新版本
> 强制落库。

---

## v0.9.0 · 本期内容（UPLIFT U1–U6 补齐短板 + 宿主模型桥）

### 一句话

v0.8.0 交完肾单位 P0 之后，仓库里躺着六个**已经实证**的短板；这一版不造新能力，只把六个洞
连同验证方式一起焊死：结果顺序全序化、`_fft` 纯函数化、中文匹配换字符 n-gram、CI 与
issue/PR 模板落地、徽章按实测改写、A1/A2 从 `pending` 变 `measured_with_scope`（带变异证明）、
把网络赶出核心包、十条开放问题逐条裁决。**产出物维度不变**（1331 行 / 108641 节点未破）。

### 交付清单

| # | 交付物 | 位置 | 说明 |
|---|---|---|---|
| 1 | 加固包 | `holoaeon/packs/uplift_pack.py` | 24 技能 / 7 工作流（W1 确定性 → W7 总验收）/ **0 agent** |
| 2 | 排序确定性 | `holoaeon/cluster.py` | `_canon` + `_order_key`，`real.sort(key=_order_key)` |
| 3 | `_fft` 纯函数化 | `holoaeon/hypervector.py` | 首行 `a = list(a)`；docstring 补三条约定 |
| 4 | 匹配升级 | `holoaeon/skill.py` | `0.5·Jaccard + 0.5·dice2 + 0.05·tag_hit` + 词级 3-gram 兜底 |
| 5 | CI | `.github/workflows/ci.yml` | 3.8 / 3.10 / 3.12；单测 → 自检 → 红线 → 示例 01–04 |
| 6 | 三份模板 | `.github/ISSUE_TEMPLATE/*`、`PULL_REQUEST_TEMPLATE.md` | 五立场勾选 + 两个必答问题 |
| 7 | 支持矩阵 | `docs/support-matrix.md` | 未跑格子写 `untested`，不写"预计通过" |
| 8 | 实测脚本 | `scripts/measure_a1_a2.py` | A1 双跑哈希 + **变异实验** + A2 中位披露 |
| 9 | 实测证据 | `docs/nephron_a1_a2_evidence.json` | A1 PASS / 变异 FAIL / A2 +1.83% / 机器规格 |
| 10 | 宿主桥 | `bridges/*.py`、`examples/05_live_model.py` | 三后端 + 远程三重门禁 + 7 字段审计 |
| 11 | 桥文档 | `docs/bridges.md` | 为什么必须在包外 + 本机能证与不能证 |
| 12 | 十问裁决 | `docs/nephron.md` §12 / §12.1 | O-1～O-10 六列裁决表 |
| 13 | P1 细则 | `docs/nephron-p1.md` | 打分公式 / 降级链 L0–L3 / 7 步构建 / 四判据 |
| 14 | 包文档 | `docs/uplift.md` | 六单元 / 十冲突 / 四核实 / 五缺陷 / 24 技能 |
| 15 | 自检组 | `holoaeon/selftest.py` `g24_uplift` | 43 条断言 |
| 16 | 单测 | `tests/test_holoaeon.py` `TestUpliftU16` | 3 条（总数 31 → 34） |
| 17 | 系统 README | `SYSTEM_README_v0.9.0.md` | 11 章，含验证矩阵与两条 `untested` |

### 十处冲突的择定（摘要）

| ID | 投喂字面 | 本版择定 |
|---|---|---|
| X1 | 只按 `agent_id` 排序 | 复合键 `(agent_id, 规范化记录)` |
| X2 | 6×30 轮 → 180 条结果 | 实测 6 条（首轮投递），改断言 + 补纯函数全序测试 |
| X3 | CI 三版本全绿 | 交 workflow + `untested`，不写 passing |
| X4 | 徽章写死 25 | 按实测 34，并同时修 selftest 徽章（16→24） |
| X5 | A1/A2 改 `measured` | `measured_with_scope`（宿主限定范围） |
| X6 | 需真 Ollama 的 live 回执 | 只证"无 Ollama 分支"，live 标 `untested` |
| X7 | 审计写盘 | 写盘但只记哈希 + 序号，`.gitignore` |
| X8 | `0.5·重叠个数 + 0.5·dice` | `0.5·Jaccard + 0.5·dice + 0.05·tag` |
| X9 | 英文 3-gram | 2-gram 主 + 词级 3-gram 取 max |
| X10 | 新增 `after_summary` | 不加字段，用 `summarized ∩ admitted` |

### 五处自身缺陷（写完即测，全部修掉）

| ID | 缺陷 | 教训 |
|---|---|---|
| M1 | `HOLAEON_ALLOW_REMOTE` 拼错 | fail-closed 安全但功能永久失效，两个方向都要用例 |
| M2 | `echo://local` 被网络门禁拒掉 | 离线后端不属于网络准入范围 |
| M3 | echo 回执缺 `ok` | 回执结构必须跨 mode 一致 |
| M4 | 断言 180 条（实得 6） | 投喂的实验设计也要对代码核一遍 |
| M5 | `platform.os.cpu_count()` | 不要依赖模块内部导入 |

### 明确不做

改 `Cluster` 线程语义 / 核心包联网 / 第三方依赖 / 发布自动化 / P1 执行淘汰 / echo 冒充 live。

### 验证记录

| 项 | 结果 |
|---|---|
| 单测 | `Ran 34 tests` OK |
| 自检 | `24 / 24` 组（G1–G24，G24 = 43 条断言） |
| 红线 | 34 文件零违规（`exit=0`） |
| 示例 | 01–05 全 exit 0（05 为 `skip` 分支） |
| A1 | PASS，`sha256=b48a0aa1f3743514`，`diff_at_step=None` |
| A1 变异 | 篡改一步 → FAIL，`diff_at_step=3` |
| A2 | full 中位 11.5794 ms / off 11.3708 ms → **+1.83%**（runs=30） |
| 桥 | `--check` exit 2 + 三行指引；echo `ok=True`；远程门禁四分支正确；审计 7 字段无明文 |

### 未实测（不折叠成结论）

- **A-U6-1** CI 三版本全绿：只能在 GitHub Actions 侧产生；本版只交 workflow 与 `untested` 矩阵。
- **A-U2-3** 真实 `mode="live"` 回执：本机未装 Ollama。
- A1/A2 为**宿主编排层限定范围**实测，非生产链路闭环。

### 升级路径

```
git fetch --tags && git checkout v0.9.0
python -m unittest discover -s tests      # 34
python -c "from holoaeon.selftest import run_all; assert run_all()['ok']"
python scripts/redline_scan.py            # 34 文件零违规
```

从 v0.8.0 升上来：无破坏性变更。`nephron` 的验收技能新增可选 `measured` 参数（旧调用写法仍可用，
返回结构多了 `measured_with_scope` 与 `scope_rule` 两个键）；`EXTRA_PACK_ORDER` 由 6 项变 7 项
（只追加，未改既有 key）。

---

## v0.8.0 · 本期内容（NEPHRON 肾单位层 P0 冷热插拔赋能升级包）

### 一句话

把投喂的「NEPHRON 肾单位层 P0」规格落成**只读观测的第六个扩展包**：
**产出物维度不变**（不加行、不加节点，`25 agents / 47 skills` 未破），
并且先把规格内部的 **10 处内在冲突逐条摊开、每种给两个消解方案再择一**，
再补掉 **3 处字段缺口**——最后才写码。P0 只记与回，不改与算。

### 交付清单

| # | 交付物 | 位置 | 说明 |
|---|---|---|---|
| 1 | 扩展包 | `holoaeon/packs/nephron_pack.py` | 24 技能 / 7 工作流（W1 观测 → W7 验收）/ **0 agent** |
| 2 | 设计文档 | `docs/nephron.md` | 13 章：定位 / 10 冲突与 3 修正 / 字段字典 / 理由码 / 采集开关 / 回放器 / 接口清单 / 隐私 / 测试结果 / 7 条限制 / 7 项 P1 / 10 项开放问题 |
| 3 | 记录结构 | `page_schema / page_validate / ledger_record / ledger_verify` | 41 字段（Page 10 / Slot 7 / LedgerRecord 13 / Event 4 / Manifest 7）；主键 `(tick, seq)`；只追加 |
| 4 | 事件与码 | `reason_codes / event_validate / manifest_build` | 11 类事件 · 27 码 · 10 族 · `UNKNOWN` 保留码不入表；**一个事件只许一个主码** |
| 5 | 采集开关 | `switch_policy / collect_plan / failure_injection_matrix` | 三档（默认 `off`）· 11 hook · 4 类故障 · 3 类丢弃计数；失败静默降级为不记录 |
| 6 | 回放 | `replay_window / replay_slots / replay_inputs / replay_timeline / replay_determinism` | 窗口构成 / 槽位快照（含年龄与 stale）/ 决策输入 / 变更时间线；两次回放哈希一致 |
| 7 | 隐私 | `privacy_policy / erase_operation` | 不存原文；擦除 = `ERASED:<hash>` + 追加擦除记录 + 保留计数与指纹 |
| 8 | 指纹 | `generation_fingerprint / fingerprint_check` | 权重 / 模板 / 量化 / LoRA / 检索器联合哈希（LoRA 排序归一）；失配必产事件 |
| 9 | 边界验收 | `zero_intrusion_check / non_goal_scan / acceptance_check` | 零侵入恒 `pending_human_measure`；6 条非目标扫描；A1–A8 状态机 |
| 10 | 文档回执 | `field_dictionary / audit_receipt` | 字段字典与结构同源（`match_schema=True`）；回执指纹 16 位 |
| 11 | 黄金样例 | `examples/nephron_ledger_sample.jsonl` + `examples/nephron_replay_report.md` | 7 条记录；逐 tick 窗口表 / 时间线 / 槽位 / A1–A8 状态；由脚本生成 |
| 12 | 样例生成器 | `scripts/make_nephron_sample.py` | 全部调用包内纯函数，不手写样张；解压复跑字节一致 |
| 13 | 自检断言 | `G23 nephron`（62 条） | 计数、维度、41 字段、27 码、10 冲突、写入三拒、回放四件套、确定性、指纹、擦除、验收状态机 |
| 14 | 系统 README | `SYSTEM_README_v0.8.0.md`（11 章） | 五份系统 README 并存，不覆盖 |

### 规格内 10 处冲突与消解（本版最该验收的一段）

| # | 冲突 | 采用 | 一句话理由 |
|---|---|---|---|
| N1 | 异步队列/落盘 vs 不起线程不写盘 | **B** | 包只给队列语义与丢弃计数，I/O 归宿主 |
| N2 | "任意 tick 可回放" vs 三档采样 | **B** | 只有 `full` 满足；插值补齐等于伪造账本 |
| N3 | 只追加 vs 一键擦除 | **B** | 摘要换 `ERASED:<hash>`，擦除本身成一条记录 |
| N4 | 有 `compression_ratio` vs 压缩非目标 | **B** | 字段保留但 P0 恒 `null` |
| N5 | `UNKNOWN` 兜底 vs 表内无此码 | **B** | 保留码不入表，单独计数并告警 |
| N6 | 主键 vs 时钟回跳 | **B** | 水位线拒绝追加并记 `APPEND_REJECT_CLOCK_REGRESSION` |
| N7 | 逐字节一致 vs 纯函数不可证 | **B** | 只交断言契约，恒 `pending_human_measure` |
| N8 | `raw_len` 两种单位单字段 | **B** | 锁死 token 口径，账本级声明，不加字段 |
| N9 | `window_build` 无合法码 | **B** | 正式走评审新增 `WINDOW_BUILD_COMPLETE`（R-01） |
| N10 | 要槽位快照 vs 无槽位事件源 | **B** | 旁挂周期快照 + 披露年龄，P0 **不重演槽位变化** |

三处字段缺口修正（`FIXES`）：F1 摘要前后长度改由 `page_summarize` 的 `delta{from_len,to_len}`
承载（`Page` 结构不动）；F2 `importance` 缺失只告警不改错；F3 账本只存摘要哈希与长度，
**不存摘要正文**。

### 明确不做（11 项拒绝清单 + 7 条已知限制）

拒绝：删除账本记录 / 改写历史记录 / 把采集失败抛到业务层 / 在业务逻辑内散布记录代码 /
把采样账本插值成完整账本 / 摘要阶段外送敏感字段 / 记录外部请求体明文 /
静默复用失配指纹 / 把无血统页写进主干 / 分页压缩淘汰预算控制（P1·P2） /
重演槽位变化（无事件源，P1）。

已知限制逐条写进 `docs/nephron.md`：A1 与 A2 恒未实测；槽位不重演；不能回放"模型实际
看到的文本"；`sampled/off` 不可完整回放；内容级篡改需外部锚点；`UNKNOWN` 只能计数。

**本包不执行任何观测或落盘动作**——只产判定与计划，`execution="human_manual"`，终裁留给碳基。

### 验证记录

| 项 | 方式 | 结果 |
|---|---|---|
| 内核自检 | `run_all()` | **23/23 组**（G22 52/52、**G23 62/62**、G15 `25 agents / 47 skills` 未破） |
| 内核单测 | `unittest discover -s tests` | **25 tests OK** |
| 内核红线 | `scripts/redline_scan.py` | **33 文件零违规**（含 `nephron_pack.py` 与 `make_nephron_sample.py`） |
| 黄金样例 | `make_nephron_sample.py` | 7 条记录 · `verify_ok=True` · `chain_digest` 16 位 · 两次回放哈希一致 |
| 发行包 | `make_release.py` | 72 文件 / 303,727 B / `1246269BC14CACEDA6239C32A32C52990548554EBB191476550406290FF88646` |
| 解压复跑 | 独立副本 `_verify_080` | 23/23；`VERSION=0.8.0`；`nephron 24/7/0/True/1331/108641`；样例重生成后与仓内**字节一致** |

### 本版修掉的 8 处自身缺陷（写码过程中真实踩到）

| # | 位置 | 症状 | 修正 |
|---|---|---|---|
| M1 | 三处取整 | `int(_num(x) or -1)` 把**合法主键 0**（`seq=0` / `tick=0`）吞成 `-1`，`ledger_verify` 首例误判失败 | 新增 `_int(v, dflt)`，替换 3 处共 10 个调用点 |
| M2 | `ledger_verify` | 链摘要比对是**空转**：`want` 与 `got` 同一表达式，篡改永远发现不了 | 改为真链式累加 + 外部 `anchor` 比对，并写明"内容级篡改需逐段锚点" |
| M3 | `page_validate` | `importance` 缺失被当必填错误，与 F2 冲突 | 必填循环对 `importance` 例外，改走 `warnings` |
| M4 | `ledger_record` | 残留无意义分支 `if tick == watermark and r.get("seq") is None` | 改为 `seen_keys` 主键查重（`APPEND_REJECT_DUPLICATE_PK`） |
| M5 | `G23` | 一条断言把 list 直接 append 进 `checks`（`...["append_rejects"]` 未作比较）→ `sum(checks)` 报 `int + list` | 改为与期望列表相等比较 |
| M6 | `G23` | 一处括号不匹配 `{"working": 1))` → `SyntaxError` | 拆行修正 |
| M7 | 报告生成器 | "进入为空"一律标"（首帧）"，tick 4/5/6 也标了首帧 | 仅首帧用该标签，其余用"—" |
| M8 | `make_nephron_sample.py` | 直接运行缺 `sys.path` → `ModuleNotFoundError: holoaeon` | 按 `make_release.py` 惯例插入仓库根 |

### 升级路径

1. 取 `releases/holoaeon_v0.8.0_20261030.zip`（或 `git checkout v0.8.0`）；
2. 既有代码无需改动：`EXTRA_PACK_REGISTRY` 自动多出 `nephron`，`EXTRA_PACK_ORDER` 变六项；
3. 只要账本与回放判定：拷 `holoaeon/packs/nephron_pack.py` 即可独立运行（零依赖、不联网、不落盘）；
4. 要接到真实系统：按 `docs/nephron.md` §5.2 的 11 个 hook 接入，队列与落盘由宿主实现；
5. 要人读的规范与样例：`docs/nephron.md`（13 章）+ `SYSTEM_README_v0.8.0.md`（11 章）
   + `examples/nephron_replay_report.md`。

---

## v0.7.0 · 本期内容（METAB 代谢层冷热插拔赋能升级包）

### 一句话

把「METAB 代谢层」这份治理规格落成**可判定的第五个扩展包**：
**产出物维度不变**（不加行、不加节点，`25 agents / 47 skills` 未破），
并且先把规格内部的 **8 处内在冲突逐条摊开、每种给两个消解方案再择一**，
不让"看起来都合理"的模糊条款进入实现。

### 交付清单

| # | 交付物 | 位置 | 说明 |
|---|---|---|---|
| 1 | 扩展包 | `holoaeon/packs/metab_pack.py` | 26 技能 / 8 工作流（T1 摄入 → T8 审计）/ **0 agent** |
| 2 | 设计文档 | `docs/metab.md` | 15 章：定位 / 术语 / 公理与裁决 / 8 处冲突 / 基因组 / 三态 / 生命周期 / 授权 / 消化道 / 信任半径 / 接口 / 组合 / 度量 / 反模式 / 路线 / 12 项开放问题 |
| 3 | 准入层 | `genome_schema / genome_validate / purity_ladder` | 六条染色体缺一不准入；无降级路径、黑箱未标借来均为否决 |
| 4 | 节律层 | `state_classify / state_effects / rhythm_plan` | 四问优先级 Q1>Q2>Q3>Q4；**未命中默认循环态**；依赖优先于态序 |
| 5 | 生命周期 | `lifecycle_transition / sham_report / sleep_plan / archive_package` | 假饲不可跳过；观察 ≥64 拍；断头路休眠被拒；归档缺件只能标"未完成" |
| 6 | 授权层 | `authority_layers / fail_closed_check` | 基因（季度）/ 内分泌（周）/ 反射（会话）；FC1–FC5 逐条可判 |
| 7 | 消化道 | `gut_channels / contagion_scan / lineage_record` | 结构 IR 只放哈希不放原文；跨域传染进隔离区；血统链可验、篡改按位置报告 |
| 8 | 信任与感受器 | `trust_radius / borrowed_ratio / sensor_loop / probe_baseline` | 三项必填；借来信念占比；画像收敛即降模板权重；基线重建属代谢态 |
| 9 | 组合与度量 | `combo_check / redlines / scorecard / interface_contract / generation_gate` | 白名单外不生效；四条红线；五维门禁；九行接口契约；代际校验 |
| 10 | 自检 | `antipattern_scan / audit_receipt` | 七条反模式；回执指纹 16 位；`execution="human_manual"` |
| 11 | 自检断言 | `G22 metab`（52 条） | 计数、维度、六染色体、8 冲突、定态六分支、节律、生命周期四例、血统正反、组合三态、度量两态 |
| 12 | 系统 README | `SYSTEM_README_v0.7.0.md`（11 章） | 四份系统 README 并存，不覆盖 |

### 规格内 8 处冲突与消解（本版最该验收的一段）

| # | 冲突 | 采用 | 理由 |
|---|---|---|---|
| K1 | 不可逆点 vs 可逆优于更强 | **B** | 不可逆点推到系统外，系统内仍可逆 |
| K2 | 黑箱借用级 vs 无血统不进主干 | **B** | 保留级别但限定隔离区，比删级更诚实 |
| K3 | 皮肤对接 vs 皮肤当门禁 | **A** | 只交入参，不新增皮肤规则实现 |
| K4 | 探针随时启停 vs 授权归用户 | **B** | 节奏走周级、单次走会话级 |
| K5 | 禁传原文 vs 蒸馏执行建构 | **A** | 职责分离把禁令变成结构约束 |
| K6 | 一键禁用 vs 代谢态高成本 | **A** | 止损即时、恢复可控，两步不绑死 |
| K7 | 白名单 vs 新依赖必有新组合 | **B** | 白名单是规则集（循环态），新节点仍代谢态 |
| K8 | 不可逆恒零 vs 系统外不可逆点 | **A** | 恒零只算系统内，外部单独记账 |

### 明确不做（12 项拒绝清单 + 7 条反模式）

拒绝：代替用户授权 / 默认开启新共生体 / 记住我的选择 / 自动放宽权限 / 无假饲直接生效 /
无降级路径挂载 / 断头路休眠 / 隐式外部上传 / 绕过血统账本 / 逐个放行拼高风险组合 /
抹除协作边 / 删除归档包。
反模式自检：一键全开 · 无假饲生效 · 不可逆默认路径 · 隐式外传 · 依赖外部才能启动 ·
无血统写骨架 · 逐条放行拼高风险。

**本包不执行任何摄入动作**——所有输出都是判定，`execution="human_manual"`，终裁留给碳基。

### 验证记录

| 项 | 方式 | 结果 |
|---|---|---|
| 内核自检 | `run_all()` | **22/22 组**（G21 25/25、**G22 52/52**、G15 `25/47` 未破） |
| 内核单测 | `unittest discover` | **25 tests OK** |
| 内核红线 | `redline_scan.py` | **32 文件零违规**（含 `metab_pack.py`） |
| 发行包 | `make_release.py` | 66 文件 / 250,721 B |
| 解压复跑 | 独立副本 | 22/22；`VERSION=0.7.0`；`metab 26/8/0/True/1331/108641` |

### 本版修掉的两处自身缺陷 + 一处口径

| # | 位置 | 症状 | 修正 |
|---|---|---|---|
| M1 | `g21_omnicore` | `EXTRA_PACK_ORDER[-1] == "omnicore"` 在新增第十四包后失效（G21 掉到 24/25） | 改为成员判断 `"omnicore" in EXTRA_PACK_ORDER` |
| M2 | `scorecard` | 不可逆事件非零只判 `conditional` | 判定改用 `hard_reasons`（红线前缀 + 免疫类）→ 非零即 `reject` |
| M3 | `borrowed_ratio` | 分母只取"有外部依赖的结论"，1 条借用被算成占比 1.0 | 分母改为结论总数，另出 `total` 与 `conclusions_with_external_deps` |

### 升级路径

1. 取 `releases/holoaeon_v0.7.0_20261030.zip`（或 `git checkout v0.7.0`）；
2. 既有代码无需改动：`EXTRA_PACK_REGISTRY` 自动多出 `metab`，`EXTRA_PACK_ORDER` 变五项；
3. 只要治理判定：拷 `holoaeon/packs/metab_pack.py` 即可独立运行（零依赖、不联网、不落盘）；
4. 需要人读的规范：`docs/metab.md`（15 章）+ `SYSTEM_README_v0.7.0.md`（11 章）。

---

## v0.6.0 · 本期内容（Omni-Core 认知引擎冷热插拔赋能升级包）

### 一句话

把投喂的「超级智能模式 / Omni-Core 单文件引擎」重写为**离线确定性包**：
**产出物维度不变**（不加行、不加节点，`25 agents / 47 skills` 未破），
并且**先复现、再修掉投喂代码的 5 处缺陷**——包括 3 处会直接报错或静默丢数据的真 bug。

### 交付清单

| # | 交付物 | 位置 | 说明 |
|---|---|---|---|
| 1 | 扩展包 | `holoaeon/packs/omnicore_pack.py` | 20 技能 / 6 工作流（M1 唤醒 → M6 宣告）/ **0 agent** |
| 2 | 寻址层 | `core_manifest / matrix_allocate / node_pool_plan` | 六项不变式断言全真；只产分配计划，不持有状态 |
| 3 | 节律层 | `heartbeat_pulse / breathing_budget / lifecycle_policy` | 纯函数心跳；5% 冲击用 `sha256(epoch)%100<5` 抽样 |
| 4 | 存续层 | `state_checkpoint / state_restore / degradation_plan` | 快照 `host_managed`，不写盘；指纹不符即拒收 |
| 5 | 编排通信 | `task_dispatch_plan / a2a_envelope / meridian_route` | 只产计划；信封过皮肤门；通路是行坐标链 |
| 6 | 代谢层 | `hebbian_update / far_pairs / skc_distill` | 强化→衰减→剪枝三段算术；远域配对确定性排序；SKC 关系强制反例 |
| 7 | 边界与宣告 | `skin_gate / self_declaration / whitepaper_outline / interop_map / audit_receipt` | 22 项拒绝；四段式宣告；七章白皮书结构；20 行对照表 |
| 8 | 自检 | `G21 omnicore`（25 条断言） | 计数、维度、5 处修正、拒绝清单、确定性 |
| 9 | 系统型说明 | `SYSTEM_README_v0.6.0.md` | v0.4.0 / v0.5.0 版本文档均保留 |
| 10 | 发行包 | `releases/holoaeon_v0.6.0_20261030.zip` | 63 文件 / 201,755 B；与 `SHA256SUMS.txt` 对齐 |

### 修掉的 5 处缺陷（复现 → 修正）

| # | 投喂原文 | 实测 | 改法 |
|---|---|---|---|
| C1 | `self._cells = profile` | 静默覆盖整张稀疏表，取回 `None` | `self._cells[(row, col)] = profile` |
| C2 | `self._inbox.append(msg)` | `AttributeError`（dict 无 append） | `self._inbox[(r, c)].append(msg)` |
| C3 | `route =`（空赋值） | `SyntaxError`，整文件不可加载 | `route = []` |
| C4 | `numpy` + `np.random` | 与"零依赖"矛盾、破坏复现 | 仅标准库 + 哈希抽样 |
| C5 | 守护线程 + sqlite + 不存在的 PyPI 包名 | 不满足离线确定性 | 纯函数心跳 + 宿主持久化 |

### 明确不做

```
自动登录 · 多端并发模拟请求 · 切换高匿名代理 · 代理池 · 抓取 · 爬取 · 批量下单 · 批量发帖 ·
绕过风控 · 绕过验证 · 伪造身份 · 多账号 · 养号 · 注入 DOM · 改写页面 ·
调用平台私有接口 · 破解 · 浏览器插件 · 对接流媒体平台 · 对接电商平台 · 反控算法 · 接管推荐位
```

另加两组 veto：医疗断言（诊断/处方/剂量/疗效承诺/包治/根治）、绝对结论（一定/绝对/必然）。

### 验证记录（实测）

| 验证 | 结果 |
|---|---|
| 内核自检 | **21/21**（G15 `25/47` 未破；G18 6/6；G19 17/17；G20 21/21；**G21 25/25**） |
| 单元测试 | 25 tests **OK** |
| 红线扫描 | 31 文件 **零违规** |
| 维度断言 | `addressing_unchanged=True`、rows 1331、nodes 108641、design grid 1771561 |
| 心跳可复现 | 同 epoch 两次调用 `events` 完全一致；5% 冲击在 100 个候选拍内落 2%–12% |
| 快照 | 篡改 payload 后 `accept=False`（指纹不符即拒） |
| 解压复跑 | 独立副本 21/21；`VERSION=0.6.0`；`omnicore 20/6/True/5` |

### 升级路径（从 v0.5.0 起）

1. `git checkout v0.6.0`，或解压 `releases/holoaeon_v0.6.0_20261030.zip`；
2. 既有代码无需改动：`EXTRA_PACK_REGISTRY` 自动多出 `omnicore`，`EXTRA_PACK_ORDER` 变四项；
3. 只要引擎骨架：拷 `holoaeon/packs/omnicore_pack.py` + `data/taxonomy_127.json` 即可独立运行；
4. 回滚：切回 v0.5.0；扩展包不写宿主状态，回滚即干净。

---

## v0.5.0 · 本期内容（Omni-Life 全域生活冷热插拔赋能升级包）

### 一句话

把"认知主权"从信息流下渗到衣食住行教与 SaaS 工作流：用 127 亚学科编码做**生活决策锚点**，
把"被算法降维的生活"改写成**可溯源的生活参数与人工处置清单**。**产出物维度不变**——
不加行、不加节点，母体 12 项锁数一个不动，九包 `25 agents / 47 skills` 断言未破。

### 交付清单

| # | 交付物 | 位置 | 说明 |
|---|---|---|---|
| 1 | 扩展包 | `holoaeon/packs/omnilife_pack.py` | 18 技能 / 6 工作流（L1 衣 → L6 SaaS）/ **0 agent**；`EXTRA_PACK_REGISTRY` 挂载，不进 `PACK_ORDER` |
| 2 | 生活本体 | 同上 `LIFE_DOMAINS` | 6 域锚 17 个唯一亚学科编码，全部校验落在 `data/taxonomy_127.json` |
| 3 | 皮肤层 | `high_dim_search / consumerism_blocker / price_ledger / price_review / complaint_template / material_card` | 只产搜索词、规则表、空台账、算术、话术、指标卡；`dom_injection=False` |
| 4 | 经络层 | `meridian_route / context_trigger / vault_manifest` | 导出→本地→人工引用；`api_calls=0`、`network=False` |
| 5 | 生活规划器 | `nutrition_plan / travel_route / shelter_check / learning_path / saas_plan` | 确定性：餐单结构（无剂量）、图最短路、粗算标尺、检索式、接入计划 |
| 6 | 闸门与审计 | `skin_gate / audit_receipt / daily_hebbian_schedule` | `REFUSED_OPS` 17 项命中即拒；指纹 16 位；作息不注册定时器 |
| 7 | 自检 | `G20 omnilife`（21 条断言） | 计数、维度不变、锚点零缺失、拒绝清单、确定性 |
| 8 | 系统型说明 | `SYSTEM_README_v0.5.0.md` | v0.5.0 系统快照（v0.4.0 文档保留为历史） |
| 9 | 发行包 | `releases/holoaeon_v0.5.0_20261030.zip` | 61 文件 / 175,959 B；与 `SHA256SUMS.txt` 对齐 |

### 明确不做（按名字拒绝，命中即 veto）

```
自动登录 · 多端并发模拟请求 · 模拟器并发 · 切换高匿名代理 · 代理池 · 抓取比价 · 爬取价格 ·
批量下单 · 批量发帖 · 绕过风控 · 绕过验证 · 伪造身份 · 多账号 · 养号 · 注入 DOM ·
调用平台私有接口 · 破解
```

替代路径：比价 → 本人填写的空台账 + 本地算术；权益 → 平台官方价保/客服 + 模板话术；
折叠诱导 → 平台自带"不感兴趣/屏蔽关键词"；跨 SaaS → 本人导出后本地引用。

### 验证记录（实测）

| 验证 | 结果 |
|---|---|
| 内核自检 | **20/20**（G15 `25/47` 未破；G18 6/6；G19 17/17；**G20 21/21**） |
| 单元测试 | 25 tests **OK** |
| 红线扫描 | 30 文件 **零违规** |
| 维度断言 | `addressing_unchanged=True`、`missing_anchors=[]`、rows 1331、nodes 108641 |
| 拒绝验证 | `skin_gate("多端并发模拟请求…高匿名代理")["allowed"] is False`；医疗断言同样 veto |
| 解压复跑 | 独立副本 20/20；`VERSION=0.5.0`；`omnilife 18/6/True/[]` |

### 升级路径（从 v0.4.0 起）

1. `git checkout v0.5.0`，或解压 `releases/holoaeon_v0.5.0_20261030.zip`；
2. 既有代码无需改动：`EXTRA_PACK_REGISTRY` 自动多出 `omnilife`；
3. 只要生活层就把 `holoaeon/packs/omnilife_pack.py` 与 `data/taxonomy_127.json` 一并拷入；
4. 回滚：切回 `v0.4.0` 的 zip；扩展包不写宿主状态，回滚即干净。

---

## v0.4.0 · 本期内容（SD-Distill 冷热插拔赋能升级包）

### 一句话

把"16 大域 → 127 亚学科"的知识代谢层做成**冷热插拔插件**，同时以 `DomainPack` 形态
融合进 HoloAeon 内核；**产出物维度不变**——母体 12 项锁数一个不动，九包核心
`25 agents / 47 skills` 断言未破。

### 交付清单

| # | 交付物 | 位置 | 说明 |
|---|---|---|---|
| 1 | 插件宿主 | `holoaeon/packs/…` + 认知主权 `runtime_v3/so1331_runtime/plugins.py` | `discover / cold_boot / hot_load / hot_unload / capabilities / status`；上下文隔离，能力名黑名单，MED/TCM 强制免责 |
| 2 | 插件本体 | `plugs/subdistill_v3_1/`（manifest + plugin + payload 双 JSON） | 12 能力；`Taxonomy` / `ResonanceSeed` / `TeacherBank` / `DistillationPipeline S1-S7` / `LossBank` / `CurriculumScheduler` / `AntiLabelScorer` / `validate_skc` |
| 3 | 权威数据 | `payload/taxonomy_127.json`（26,166 B）· `payload/resonance_seed_50.json`（9,659 B） | 127 项亚学科（16 域分布经断言校验）；50 组跨域共振种子**每条带反例**，置信度 <0.5 只可称隐喻 |
| 4 | 内核融合包 | `holoaeon/packs/subdistill_pack.py`（第十一包） | 15 技能 / 7 工作流 / **0 agent**；`EXTRA_PACK_REGISTRY` 挂载，不进 `PACK_ORDER` |
| 5 | 内核数据 | `data/taxonomy_127.json` | 供内核侧读取；缺失时技能降级为结构输出而不报错 |
| 6 | 双重自检 | 内核 `G19 subdistill`（17 条断言）· 认知主权 `G14 冷热插拔`（20 余条断言） | 维度等式、管线贯通、SKC 校验、非侵入性、卸载回滚 |
| 7 | 系统型说明 | `SYSTEM_README.md` | 系统边界 / 维度不变式 / 插拔契约 / 验证矩阵 / 版本纪律 |
| 8 | 发行包 | `releases/` 两个 zip + `SHA256SUMS.txt` | 版本化、不覆盖 |

### 维度不变式（写进断言，不是文档口号）

```
127 亚学科 × 10 槽位  +  61 保留行      = 1331   行
127 亚学科 × 855 节点 +  56 全局协调节点 = 108641 节点
```

域分布：MATH 10 / LOGIC 8 / CS 8 / PHYS 10 / BIO 8 / MED 8 / PHIL 8 / HIST 8 / LIT 7 /
AEST 7 / SEMI 7 / SOC 8 / TCM 8 / AI 8 / FUT 7 / SF 7 = **127**。

七项损失权重 `0.30 / 0.20 / 0.15 / 0.20 / 0.08 / 0.05 / 0.02`（和 `= 1.0`）；
课程 `C1 0.6/200 · C2 0.9/300 · C3 1.4/400 · C4 1.8/300`（epoch 和 `1200`）；
温度冲击 `p 0.05 / τ 2.5 / 2 epoch`（SHA 前 8 位十六进制取模，**确定性**触发）。

### 验证记录（实测，非推断）

| 验证 | 结果 |
|---|---|
| 内核自检 | `19/19` 组通过；`G15 agents=25 skills=47` 未被破坏；`G18 6/6`；`G19 17/17` |
| 认知主权自检 | `14/14` 组通过；`G14` 明细 `caps=12 skc=3 committed=3 digest=e8fc0978e1ec3cea` |
| 冷热插拔 | 冷装 `loaded ["subdistill"]`；热装 `mode=hot`；卸载后能力数 `0`；再热装恢复 `12` |
| 非侵入性 | 装载前后各建全新宿主跑首轮，两次 digest **逐位一致**，`round_ok=True` |
| 管线 | S2 打标覆盖 `0.6`（codes 含 `MATH-09 / AI-03 / LOGIC-04`）→ S4 关系边 → S5 配对 3 单元（`R001/R002/R009`）→ S6 SKC 3 → S7 入库 3，SKC 校验 **3/3** |
| 单元测试 | 内核 `25 tests OK` |
| 红线 | 内核 29 文件零违规；认知主权 21 文件零违规 |
| 解压复跑 | 内核包独立副本 `19/19`；认知主权包独立副本 `14/14` + 红线 0 |
| 技能旁挂 | `.user_skills/cognitive-sovereignty-1331` 内直跑 `14/14` + CLI 正常 |
| 打包幂等 | 认知主权 11 步收割连跑两次，zip **同大小同哈希** |

### 升级路径（从 v0.3.1 起）

1. `git checkout v0.4.0`（或解压 `releases/holoaeon_v0.4.0_20261030.zip`）。
2. 内核侧：无需改动既有代码，`EXTRA_PACK_REGISTRY` 自动多出一个 `subdistill`。
3. 认知主权侧：用发行包覆盖 `runtime_v3`，或保留原目录、只把 `plugs/` 与 `so1331_runtime/plugins.py` 拷入。
4. 回滚：直接切回 `v0.3.1` 对应的本地 zip；插件目录不动内核，卸载即归零。

---

## 下载与校验

```powershell
# 两个发行包与本文件的 SHA256 权威记录：releases/SHA256SUMS.txt
Get-FileHash .\releases\holoaeon_v0.4.0_20261030.zip -Algorithm SHA256
Get-FileHash .\releases\cs1331_cognitive_sovereignty_matrix_V3.1.0_20261030.zip -Algorithm SHA256
```

---

潮起开门，潮落闭嘴。
