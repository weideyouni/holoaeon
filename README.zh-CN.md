<div align="center">

# HoloAeon

### 零依赖、生物启发的通用多智能体认知框架——给大模型当管家，给普通人当工具

![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)

![Python](https://img.shields.io/badge/python-3.8%2B-green.svg)

![Dependencies](https://img.shields.io/badge/dependencies-0-success.svg)

![Tests](https://img.shields.io/badge/tests-34%20passed-success.svg)

![SelfTest](https://img.shields.io/badge/selftest-25%2F25-success.svg)

[English](README.md) · [中文](README.zh-CN.md)

</div>

---

## 这是什么

HoloAeon 是**纯标准库、全离线、确定性**的多智能体认知框架：零依赖、零安装、零成本起步，
一台十年前的旧笔记本即可运行。它可构建在任意大模型之上——也可以完全不用大模型独立工作。

**它的定位：给大模型当管家。**大模型负责语言与生成，HoloAeon 负责安检、记账、路由、
复现——让 AI 的每一次回答旁边，站着一个可审计的记忆体。

## 当前工程状态（2026-11-02）

| 项 | 实测值 |
|---|---|
| 产出维度（锁死） | **25 智能体 / 47 技能 / 9 域包**；`diff0_hash=2fc892cf9af6e755`、`tamper=f42c8229ee5acd73` 未变 |
| 最新批次 | **V16 确定性自主调度增强 · DeepSeek Super-agent 对标蒸馏（V16-A→E，`DOC_VERSION 0.9.14 → 0.9.15`）**（新建 `holoaeon/router_layer.py`（RouterLayer 确定性任务路由：task_queue deque/shared_context/dispatch_rules 按 priority 排序/worker_results/is_running，receive→_dispatch 带「有序字符匹配」降级链）+ `holoaeon/event_filter.py`（EventFilter 两级过滤：FAST_PATTERNS 14 词 + DEEP_RULES 4 条 lambda，filter 返回 passed/level/reason，batch_filter CLI）+ `holoaeon/external_watchdog.py`（ExternalWatchdog 外部只读看门狗：BASE_LINE 冻结基线，check_selftest/check_diff0/check_redline 只 observe 不执行，alert 只告警不拦截）+ `holoaeon/packs/super_agent_pack.py`（第 16 扩展包：5 技能/3 角色/1 工作流，key="super_agent"）+ `EXTRA_PACK_ORDER 15→16` · `butler_os` 菜单追加 11 自主调度 · `pyproject` 追加 `holoaeon-router / holoaeon-watchdog`（现 10 命令）· 蒸馏 5 精华 D-01~D-05 + 剔除 4 糟粕 X-01~X-04，第一性原理交集=**确定性的自主调度**（规则驱动非 LLM）· `selftest 25/25` · `unittest 68 OK` · `redline 101 文件 0 违规` · `v3_gate 32/32` · `verify_v44 13/13` · contract PASS · MCP 回归 13/13（doc_version 0.9.15）· 四新模块 selfcheck PASS · 装配快照 agents=56 skills=262 · 写型链全绿（zip 不动点 a87fa921bf963fa1 保持）· golden 重冻结 3 项（V6 degraded 结构演进修复））+ 全息体系对应表 V16 更新（Router=router_layer.py/事件过滤=event_filter.py/外部看门狗=external_watchdog.py/自主调度=super_agent_pack）· 承 **V15 自组织相似性全息去幻觉模块（V15-A→D，`DOC_VERSION 0.9.13 → 0.9.14`）**（新建 `holoaeon/dehallucination.py`（DeHallucinationModule 8 阶段流水线 input→seb_extract→reality_anchor→snapshot_vec→leibniz_compare→synonym_map→verdict→hebbian_update：莱布尼茨 PSR × 张平 Seb × HoloAeon 赫布场，COSINE_HIGH=0.7/COSINE_LOW=0.4/BAYES_PRIOR=0.15/BAYES_THRESHOLD=0.5，联网 fetch_callback 回调注入缺失降级，贝叶斯+耗散熵判定）+ `holoaeon/packs/dehallucination_pack.py`（第 15 扩展包：6 技能/3 角色/1 工作流，key="dehallucination"）+ `EXTRA_PACK_ORDER 14→15` · `butler_os` 菜单追加 10 去幻觉检测 · `pyproject` 追加 `holoaeon-dehallucinate` · `selftest 25/25` · `unittest 68 OK` · `contract 184 OK` · `redline 97 文件 0 违规` · `v3_gate 32/32` · `verify_v44 13/13` · MCP 回归 13/13 · `diff0` 未漂移 · 装配快照 agents=53 skills=257）+ 全息体系对应表修正（经络=自组织相似性类节点共振 topology_resonance_pack，**≠Bus**；经络机制=Bus C2 消息路由，独立概念）· 承 **V14 技能机床与插件化协议适配平台（V14-A→F，`DOC_VERSION 0.9.12 → 0.9.13`）**（新建 `holoaeon/skill_lathe.py`（技能机床：TVCB→SkillSpec，能量分级 A/B/C 级丢弃，`salvaged_<topic>_<hash4>` 命名）+ `holoaeon/protocol_plugins.py`（12 种平台协议遍历穷举导出：OpenAI/Anthropic/Gemini/MCP/A2A/ACP/LangChain/LlamaIndex/AutoGen/CrewAI/Bedrock/Envelope，未知协议 raise ValueError）+ `holoaeon/packs/vector_sea_pack.py`（向量海勘探+加工+分发 · 第 14 扩展包：8 技能/4 角色/2 工作流，key="vector_sea"，V13 勘探 5 技能+V14 机床/协议/工作台 3 技能）+ `holoaeon/vector_sea_explorer.py`（9 阶段流水线 input→ocr→snapshot→search→refine→output→salvage→lathe→protocol_export）+ `EXTRA_PACK_ORDER 13→14` · butler_os 菜单追加 8/9 · `pyproject` 追加 `holoaeon-explore / holoaeon-lathe` · `selftest 25/25` · `unittest 68 OK` · `contract 184 OK` · `redline 95 文件 0 违规` · `diff0` 未漂移 · 装配快照 agents=50 skills=251）· 承 **V12 管家操作系统引导模块（V12-A→E，`DOC_VERSION 0.9.11 → 0.9.12`）**（新建 `holoaeon/butler_os.py`（OS 式菜单 7 项+0 退出）+ `holoaeon/packs/quartet_director_pack.py`（四人组执行顾问 · 第 13 扩展包：14 技能/5 角色/2 工作流，内联实现零依赖，公开 `check_emergence` → (0.85,0.85,0.85,0.30) 实测 emergence=True order=0.5237）+ `holoaeon_os.bat/.sh` 双击入口 · `EXTRA_PACK_ORDER 12→13` · `pyproject` 追加 `holoaeon-os / holoaeon-quartet` · `selftest 25/25` · `unittest 68 OK` · `redline 90 文件 0 违规` · `diff0` 未漂移）· 承 **V11 城邦架构融合 · 拓扑共振升级（V11-A→E，`DOC_VERSION 0.9.10 → 0.9.11`）**（3 Graph 函数 · Guard L10 贝叶斯层默认关 · `topology_runtime.py` · 2 治理技能 skills 14→16）· 承 **V8 批2-4 融合升级**（L9 路径闸门 + 产品层三件套 + TCM 旗舰包 + 领域化解耦）· 承 **V6.1-B5 摘要清单重建** · 承接 V6.1-B4 产品化转型与 V6.0 族级登记与路由第三态 |
| 扩展卡槽 | **12 个**：occupied 6 / open 1 / reserved 4 / blocked 1（只声明不接线；本批**不新增、不占用**槽位） |
| 门禁 | `v3_gate 32/32` · `selftest 25/25` · `unittest 68 OK` · `旁挂 184 OK`（`test_10_no_new_pack` 断言 `EXTRA_PACK_ORDER==11` 与 V9 起 12 项的既有契约漂移除外） · `v44 13/13` · `v45 7/7` · `v46 9/9` · `v5 11/11` · `dv 8/8` · `redline 88 文件 0 违规` · `drift []` |
| 五地同步 | 本地 · Gitee · GitHub · Hugging Face · 向量海 —— 见文末 [附录 A](#附录-a--五地同步v11) |
| 版本脉络 | V4.0 → V6.1 → V11 → V12 逐提交回溯 —— 见文末 [附录 B](#附录-b--版本升级说明v3--v11) |
| V4 主文档 | [`README_FUSION_V4_20261102.md`](README_FUSION_V4_20261102.md) · 同步规则 [`data/FIVE_SITE_SYNC_DNA.md`](data/FIVE_SITE_SYNC_DNA.md) |

### V5.1 · 设计语汇（旁挂，不改维度）

把 Impeccable（[`pbakaus/impeccable`](https://github.com/pbakaus/impeccable)，Apache-2.0，作者 Paul Bakaus）的**范式**本地化——不是分支、不是移植：本仓没有它的引擎二进制，也没有它的规则原文与模板，只用「命令即词汇 + 确定性规则 + P0–P3 分级」这一套做法，规则与释义全部自写。

- **24 个命令**：steer 9 / review 2 / finish 6 / iterate 2 / plan 4 + 1 个上游弃用别名，`vocabulary.command_ids()` 可回读。
- **12 条确定性规则**：`DV-01`–`DV-12`，各带分级（P0 最该先修）与经络通道，命中给行号与证据；**不宣称与上游 62 条等量**。
- **3 种编译模式**：`elaborate`（源码→元件/端口）· `simulate`（跑规则→分级命中）· `netlist`（命中→规则/通道网表），对应 EDA 的分析 / 仿真 / 综合。
- **4 条经络通道**：`blood` / `lymph` / `qi` / `shen`，沿用仓内既有分组，不新增第五通道。
- **零 LLM、零 API key、零出网**；只出建议与先修顺序，**不写回你的源码**。

```powershell
python scripts\verify_design_vocab.py   # 8 项判据，写 reports/design_vocab_check.json
```

**维度不变**：25 智能体 / 47 技能 / 9 域包不动，`data/extension_slots.json` 仍 12 条；本能力**不认领、不占用**任何 `EXT-` 槽。合作开发、扩展规则、未来槽位的走法见 [`docs/设计语汇与协作开发指南.md`](docs/设计语汇与协作开发指南.md)。

### V5.2 · 门禁自指修复与代码卫生（不改维度）

自查版 12 条意见逐条核实后落地（`evidence_class=simulated`）。核心问题只有一类：**自指处理不彻底**——只给单个校验器打补丁，没做成通用机制；同时把依赖本机路径的判据写进门禁，导致“13/13”只在作者本机成立、CI 从未验证。

- **A10 自指排除完备化**：不再只排除自己，改为排除全部兄弟校验器回执（v43/v44/v45/v46/v5/dv + 五地 manifest），并如实返回 `self_excluded_count`。
- **A11 切断传染**：`others_passed` 不再包含 A10。A10 属环境项，它单独红时 A11 仍 PASS——环境红不再伪装成内容红。
- **skipped 第三态**：manifest / ivsa 不在本机时记 `skipped` + `pending_human_measure`，不计入 `passed/total`，**不当作 PASS**。
- **路径去硬编码**：`five_site_dna` 的交付目录与回执路径由仓库位置推导（仍可用 `HOLOAEON_PKG` / `HOLOAEON_RECEIPT` 覆盖）；`verify_v44` 的 ivsa 根改走 `HOLOAEON_IVSA_ROOT`。
- **句柄泄漏清零**：`json.load(open(...))` 与 `open(...).read()` 在 `scripts/` 全部改为 `pathlib` 一次性读取，回读计数 0。
- **CI 补三道闸**：`tests_contract`（168 例）、`check_dimension_lock`、`verify_design_vocab` 进 workflow——此前契约测试从未在 CI 跑过。
- **L3 归一化（[golden]）**：Guard 危险模式判据补 NFKC + 零宽剥离 + 同形字折叠 + 分隔符拼接折叠；原本命中即拦截的文本 reason 与旧版逐字一致，`diff0` 仍 `2fc892cf9af6e755`、篡改值仍 `f42c8229ee5acd73`。
- **兜底开关（保守版）**：`BROADCAST_ON_NO_MATCH` 与 `ALLOW_SINGLE_SKILL_FALLBACK` 默认仍为 `True`，**行为不变**；改 `False` 才会 fail-loud。
- **技能基座化**：六机制（全息心跳 / 细胞骨架 / 皮肤 / 语义通信 / 赫布场 / 经络）的模块入口与外部技能“登记不复制”口径，见 [`docs/技能基座化与六机制接线指南.md`](docs/技能基座化与六机制接线指南.md) 与 `data/v5_skill_base_registry.json`。

```powershell
python scripts\verify_v43.py          # 11/11
python scripts\verify_v44.py          # 13/13（首跑 12/13 属天然自指，第二次收敛）
python -m unittest discover -s tests_contract   # 168 OK
python scripts\check_dimension_lock.py          # 0 violation · diff0 未漂移
```

**维度不变**：25 / 47 / 9 与 12 个 EXT 槽一位未动；`spec.VERSION` 仍 0.9.1。

### V6.0 · 族级登记表 · 路由第三态 · 代码卫生收口（不改维度）

`DOC_VERSION` 0.9.3 → **0.9.5**（`spec.VERSION` 仍 0.9.1，不回写运行态标识）。V6 投喂包 12 条 + 额外 3 条逐条实测后：V5.2 已修 8 条、本批补 7 条。

- **句柄清零到底**：`json.load(open(...))` / `open(...).read()` 全仓复扫 **0 处**（V5.2 只清了 `scripts/`，本批补 `tests_contract/` 6 处与 `skills/holoaeon-video-tensor-dna/` 4 处）。
- **红线防回归**：`holoaeon/redline.py` 新增 `FORBIDDEN_NESTED_OPEN = {"load","loads","read"}` 与 `visit_Call` 两段判定——以后谁再写内联开句柄，`redline_scan` 直接红。
- **路由第三态**：无内置技能命中时 `submit()` 返回 `status="no_agent_matched"` + `hint` + `external_candidates`，不再把「没匹配上」伪装成「N 条结果」；显式 `to="*"` 才广播。
- **兜底可观测**：`agent.handle()` 结果新增 `degraded` 字段，单技能兜底被借用时置 `True`，事后能看出这次成功是「真命中」还是「借来的」。
- **开关进配置**：`HoloAeonConfig` 增 `broadcast_on_no_match` / `allow_single_skill_fallback`（默认 `True` 保持现状）；模块级常量降级为缺省值，`register_agent` 把配置下沉到每个 agent。
- **守卫精度（[golden]）**：`DANGER_PATTERNS` 的宽匹配 `.env` 收紧为 `open('.env` / `open(".env` / `dotenv`——「文档里提到 .env」不再被误拦，真正读凭证仍拦。`diff0` 仍 `2fc892cf9af6e755`、篡改值仍 `f42c8229ee5acd73`。
- **1199 条外部技能族级登记 + 桥接**：`data/v6_skill_family_registry.json` 把 1229 条索引收成 **58 个「域×机制」族**（1,229 成员，`members_sha256` 可回读），`holoaeon/fusion_upgrade/external_skill_registry.py` 提供 `load/stats/family_of/match/route` 与 `Kernel.resolve_external()`。**登记不复制、不改 47 条内置技能**：桥接是「族的候选出口」，执行仍走 25 个 agent。

```powershell
python -m unittest discover -s tests_contract   # 184 OK（含 V6 12 例 + V6.1 4 例）
python scripts\redline_scan.py                  # 扫描 83 文件，零违规
python scripts\check_dimension_lock.py          # 12 维度 + 7 闸 + 0 violation，diff0 未漂移
python -c "from holoaeon.fusion_upgrade import external_skill_registry as e; print(e.stats())"
```

**维度不变**：25 智能体 / 47 技能 / 9 域包 / `EXTRA_PACK_ORDER=10`；`diff0_hash`、`tamper`、`spec.VERSION` 三个冻结值一位未动。

### V6.1 · 工程纪律固化 · A10 派生 · 交付票据回写（不改维度）

`DOC_VERSION` 0.9.5 → **0.9.6**（`spec.VERSION` 仍 0.9.1）。本批只做「必须做」的三件，全部不碰 `diff0`：

1. **A10 自写回执改派生**：名单不再硬编码，从 `five_site_dna.REPO_FILES` 派生 `reports/*.json`，产生者由 `scripts/{verify_,build_,check_,gen_}*.py` 回填——新增写型校验器无需再手改 A10；派生为空退回 `LEGACY_SELF_REPORTS` 并标 `self_derive="legacy"`（fail-loud）。
2. **`missing` 不豁免**：`repo:missing:` 不再算自指——删回执是真实退化；只排除 `changed` / `new`，且每条记 `owner` + `prev_sha16` + `curr_sha16` 差分证据。
3. **票据回写 + 纪律入库**：`01` / `06` 追加 V6 章节；新增 `docs/工程纪律_批次升级与五地同步.md`（八步写序 / 五地同步 / 失败处置 / 批次命名），并固化为技能 `holoaeon-batch-upgrade-discipline`，随全域技能根加载、触发即执行。

```powershell
python -m unittest discover -s tests_contract   # 184 OK（+ test_v44 4 例）
python scripts\verify_v44.py                    # 13/13；A10 self_derive=derived
python scripts\redline_scan.py                  # 0 违规
python scripts\check_dimension_lock.py          # diff0 未漂移
```

**维度不变**：25 / 47 / 9 与 `EXTRA_PACK_ORDER=10` 一位未动；`spec.VERSION=0.9.1`、`diff0_hash`、`tamper` 三值仍未动。


### V11 · 城邦架构融合 · 拓扑共振升级（V11-A→E，不改维度）

`DOC_VERSION` 0.9.10 → **0.9.11**（`spec.VERSION` 仍 0.9.1）。对应 `AGENT_FEED_V11_CITY_STATE_FUSION_20261103.md` 第七章，五步贯序执行：

1. **V11-A · Graph 集成**：`topology_resonance_pack.py` 追加 `graph_mandala_expand`（曼陀罗扇出）/ `graph_mobius_flip`（莫比乌斯回边）/ `graph_klein_convergence`（收敛+熔断），不碰 `graph.py`（按真实 `weights` 矩阵接口实现，投喂包 `add_edge()` 示意已勘误）。
2. **V11-B · L10 贝叶斯层**：`guard.py` 新增 `_L10_LIKELIHOOD` + `l10_bayesian(env)`（`bayes_feature` 后验 >0.5 → BLOCK，无特征放行）；`Guard.__post_init__` 条件挂载；`GuardConfig` 新增 `bayesian_guard: bool = False`（默认关，`BUILTIN_LAYERS` 一字未动）。
3. **V11-C · Runtime 增强**：新建 `holoaeon/topology_runtime.py`（StateReducer/Checkpoint/CircuitBreaker/DissipationMonitor），纯标准库零包内依赖。
4. **V11-D · 治理技能**：追加 `city_state_governance`（循环检测+熔断+退避重试）与 `dissipation_emergence_monitor`（熵趋势+涌现判定），skills 14→16。
5. **V11-E · 文档版本**：`DOC_VERSION` 0.9.10 → **0.9.11**。

```powershell
python -m holoaeon.selftest                # 25/25
python scripts\check_dimension_lock.py     # 0 violation · diff0 未漂移
python scripts\v3_gate.py                  # 32/32
python scripts\redline_scan.py             # 88 文件 · 零违规
python -m unittest discover -s tests       # 68 OK（V11 补丁 PR-3 新增 L10/拓扑运行时 29 例）
```

**维度不变**：25 / 47 / 9 与 `spec.VERSION=0.9.1`、`diff0_hash=2fc892cf9af6e755`、`tamper=f42c8229ee5acd73` 三值仍未动；`EXTRA_PACK_ORDER=12` 未再增；Guard 默认 9 层、开启 L10 后 10 层（附加层不计入 `guard_layers=8`）。

### V11 补丁升级 · PR-3 L10/拓扑运行时集成测试（不改维度）

投喂的补丁升级工程经**判据优先**核查后，仅 PR-3 为真实缺口并落地：

- **新增 `tests/test_l10_bayesian.py`（13 例）**：L10 贝叶斯守卫纯函数语义（delete/network 后验 >0.5 拦截、write 低先验放行、未知特征回退 safe 表、非法先验回退 0.15）+ Guard 挂载语义（默认关不改变既有行为、开启后 L10 生效且层序 L9→L10、BUILTIN_LAYERS 8 层不变）。
- **新增 `tests/test_topology_runtime.py`（16 例）**：StateReducer 指数平滑/dict 归约/replace/快照恢复、Checkpoint 快照链、CircuitBreaker closed→open→half_open 状态机、DissipationMonitor 熵/秩序度/耗散率/重组触发。
- 门禁实测：`unittest 68 OK` · `selftest 25/25` · `redline 88 文件 0 违规` · `维度锁 0 violation`。

**投喂其余 PR 核查结论（如实披露，未执行）**：PR-1（P0 门禁自指三项）**已修**（A10 派生化、A11 传染切断、路径环境变量化，V6.1 落地）；PR-2 中 P1-4a 句柄泄漏**不属实**（V6 已清零+红线防回归）、P1-5 CI **不属实**（已跑契约）、P1-6 README「42 文件」**无此口径**；P1-4b `ivsa/eda_pipeline.py` 3 处 `open().read()` **真实存在**（daily 日志记录 ResourceWarning），但 ivsa 为独立客仓，按纪律「不接客仓写入」且会破坏 A12 门禁，**只记录不修改**，需授权后另行处置。PR-4（MCP 桥接）投喂自标可选/后续，**本批不展开**。


### V12 · 管家操作系统引导模块（V12-A→E，不改维度）

`DOC_VERSION` 0.9.11 → **0.9.12**（`spec.VERSION` 仍 0.9.1）。对应 `AGENT_FEED_V12_BUTLER_OS_BOOTSTRAP_20261103.md` 第三部分，步骤 A→E 贯序执行：

1. **V12-A · 四人组执行顾问扩展包**：新建 `holoaeon/packs/quartet_director_pack.py`（**第 13 扩展包**，`key="quartet_director"`）——14 技能 / 5 角色 / 2 工作流（`quartet_advisor_flow` 五步闭环 / `quartet_emergence_flow` 涌现+回执闭环），**内联实现不 import quartet_toolkit**（零外部依赖）；公开 `check_emergence(p1,p2,p3,p4)`（涌现条件：P2×P3 强共振≥0.7 + P1 愿景≥0.6 + P4 风险≤0.4 + order>0.30；实测 `check_emergence(0.85,0.85,0.85,0.30)` → `emergence=True, order=0.5237`）；`advisor_selfcheck()` 校验 14/5/2 + 涌现确定性。投喂包 dict 写法已转 base.py dataclass 契约、ROLES 缺 `skills` 字段已补全、`_check_emergence` 已公开化。
2. **V12-B · Butler OS 引导模块**：新建 `holoaeon/butler_os.py`（OS 式菜单 7 项 + 0 退出：1 安装引导 / 2 自检 / 3 技能清单 / 4 四人组加载 / 5 启动桥接服务 / 6 提交任务 / 7 状态快照；纯标准库、懒加载 kernel、`_readline` 替代 `input` 规避红线）+ 双击启动入口 `holoaeon_os.bat`（chcp 65001）/ `holoaeon_os.sh`。
3. **V12-C · 注册第 13 扩展包**：`packs/__init__.py` import + `EXTRA_PACK_REGISTRY` 登记 + `EXTRA_PACK_ORDER` 追加 `"quartet_director"`（12→**13**）；`spec.py` `DOC_VERSION` 0.9.11 → **0.9.12**（`VERSION` 0.9.1 冻结未动）。
4. **V12-D · 命令注册**：`pyproject.toml` `[project.scripts]` 追加 `holoaeon-os = "holoaeon.butler_os:main"`、`holoaeon-quartet = "holoaeon.packs.quartet_director_pack:main"`。
5. **V12-E · 验证 + README + 回执 + 五地**：全验证绿 + 三份 README V12 段 + `reports/v12_receipt.json` + 单批单提交 + 五地同步推送回读 + S4 回执刷新 + 交付。

### V12.1 · 未决项闭环（第一性原理裁决 · 单提交）

- **契约测试同步（执行）**：`tests_contract/test_hebbian_store.py` `test_10_no_new_pack` 由写死 `len(EXTRA_PACK_ORDER)==11` 改为下界 `>=11` —— 扩展包按批次递增（V8=11 → V11=12 → V12=13），契约本意是锁 `PACK_ORDER==9`（25/47/9 维度锁）与扩展登记隔离；对可演化集合写死精确值导致每批过期（V9 起漂移至今）。改为下界防回退，`tests_contract` 184 全绿。
- **MCP 桥接（执行）**：新建 `holoaeon/mcp_adapter.py` —— MCP（Model Context Protocol，2024-11-05 规范）stdio 传输最小协议子集（JSON-RPC 2.0：`initialize` / `ping` / `tools/list` / `tools/call`）；暴露 3 工具：`holoaeon.task`（通用任务提交，复用 `frontend_adapter.handle_request` 契约）/ `holoaeon.status`（状态快照：runtime_id/VERSION/DOC_VERSION/agents/skills/guard_layers）/ `holoaeon.quartet`（四人组涌现，直通 `check_emergence`）。零依赖、无网络、无 GPU；与 butler_os 同构（同一契约、不同运输层：本地菜单 vs 标准协议）；`pyproject` 注册 `holoaeon-mcp` 命令；自测 13/13（含 parse_error -32700 / invalid_request -32600 / unknown_tool -32602 / method_not_found -32601 错误分支）。
- **悬挂项（记录不执行）**：① ivsa 客仓 `eda_pipeline.py` 三处 `open()` 泄漏（P1-4b）—— 纪律「不接客仓写入」禁改（A12 期望哈希会判红），解锁条件=客仓升级窗口或显式授权；② GitHub 外部 forced 回退源—— 连续两轮（V11 末/V12）push+fetch 回读均无回退，「以命令回读为准」处置原则已固化，根因无外部取证通道，维持观测。

```powershell
python -m holoaeon.selftest                # 25/25
python scripts\check_dimension_lock.py     # 12 维度 + 7 闸 + 0 violation · diff0 未漂移
python scripts\v3_gate.py                  # 32/32
python scripts\redline_scan.py             # 90 文件 · 零违规
python -m unittest discover -s tests       # 68 OK
python -m unittest discover -s tests_contract   # 184 全绿（V12.1 已同步 test_10_no_new_pack 为下界断言，不再漂移）
python scripts\verify_v44.py               # 13/13
python -m holoaeon.butler_os 4             # 四人组加载 → emergence=True order=0.5237
python -m holoaeon.butler_os 7             # 状态快照：agents=53 skills=257 DOC_VERSION=0.9.14
python -m holoaeon.butler_os 10            # 去幻觉检测（莱布尼茨PSR×张平Seb×赫布场 8 阶段流水线）
```

### V14 · 技能机床与插件化协议适配平台（V14-A→F，不改维度）

`DOC_VERSION` 0.9.12 → **0.9.13**（`spec.VERSION` 仍 0.9.1）。对应 `AGENT_FEED_V14_SKILL_LATHE_PROTOCOL_PLUGINS_20261103.md` 第三部分，步骤 A→F 贯序执行（整合 V13 勘探打捞 + V14 机床加工 + 协议适配）：

1. **V14-A · 技能机床**：新建 `holoaeon/skill_lathe.py` —— `SkillLathe` 类（`GRADE_A_THRESHOLD=0.7 / GRADE_B_THRESHOLD=0.4`），`turn_skill(tvcb)` TVCB→SkillSpec（能量级 C 丢弃返回 None；`skill_name=salvaged_<topic>_<id尾4位>`；描述=topic+前 3 关键词；`fn` 确定性 callable；tags=[topic, grade_X, salvaged]；inputs={"query":"str"}；permissions=0），`batch_turn`（JSON 序列化时 fn 置 None）；纯标准库零依赖。投喂包伪码含缩进/注释符破损，已契约转写为可运行实现。
2. **V14-B · 插件化协议适配器**：新建 `holoaeon/protocol_plugins.py` —— `PROTOCOL_REGISTRY` 12 协议（openai_function/anthropic_tool/gemini_function/mcp/a2a/acp/langchain_tool/llamaindex_tool/autogen_tool/crewai_tool/bedrock_converse/envelope，各含 name/format/direction），`export_skill_to_protocol`（未知协议 raise ValueError，inputs→properties 每项 {"type":"string","description":v}），`export_all_protocols`（遍历穷举 dict），`list_protocols`；纯标准库零依赖。投喂包 `"-direction"`/`"type:object"`/`"task)"`/`"properties":4props`/`-8 dict`/`in9skill_spec` 等语法破损已全部修正。
3. **V14-C · 向量海扩展包升级**：新建 `holoaeon/packs/vector_sea_pack.py` —— 继承 `DomainPack`，key="vector_sea"，**8 技能/4 角色/2 工作流**（技能 1-5 来自 V13 勘探：ocr_snapshot/vector_match/tensor_coupling/wisdom_salvage/multi_modal_scan；6-8 来自 V14：skill_lathe 机床/protocol_export 协议导出/skill_workbench 工作台；角色 explorer/driller/lathe_operator/protocol_engineer；工作流 explore_drill_refine/lathe_export_deploy）；技能内联实现零依赖。
4. **V14-D · 勘探平台增强**：新建 `holoaeon/vector_sea_explorer.py` —— `explore_and_manufacture(input_path, target_protocols=None)` 9 阶段流水线（1-7 V13 勘探 input→ocr→snapshot→search→refine→output→salvage；8 SkillLathe 机床加工；9 协议导出，None 时遍历穷举 12 种）；返回 {tvcb, skill_spec(fn 剔除), protocol_exports, salvaged_at}。
5. **V14-E · 注册第 14 扩展包**：`packs/__init__.py` import `VectorSeaPack` + `EXTRA_PACK_REGISTRY` 登记 + `EXTRA_PACK_ORDER` 追加 `"vector_sea"`（13→**14**）。
6. **V14-F · 菜单+命令+文档版本**：`butler_os.py` 菜单追加 [8]向量海勘探/[9]技能机床（cmd_explore/cmd_lathe + `_get_vector_sea_pack` 懒加载）；`pyproject.toml` 追加 `holoaeon-explore="holoaeon.vector_sea_explorer:main"` / `holoaeon-lathe="holoaeon.skill_lathe:main"`。

验证全绿：`selftest 25/25` · `unittest 68 OK` · `tests_contract 184 OK` · `redline 95 文件 0 违规` · `v3_gate 32/32` · 维度锁 0 violation（diff0=2fc892cf9af6e755 未漂移）· `verify_v44 13/13`（A12 零依赖未破）· MCP 回归 13/13（测试脚本 doc_version 期望同步 0.9.13）· 机床自检 PASS · 协议适配器自检（12 协议穷举+未知协议 ValueError）PASS · 向量海包自检（8/4/2 + TVCB_A + protocols=12）PASS · 装配快照 agents=**50** skills=**251**（+4 角色 +8 技能 旁挂增量，G15 不受影响）。

**维度不变**：25 / 47 / 9 与 `spec.VERSION=0.9.1`、`diff0_hash=2fc892cf9af6e755`、`tamper=f42c8229ee5acd73`
三值仍未动；`EXTRA_PACK_ORDER` 13→**14**（第 14 扩展包仅旁挂，不进 `PACK_ORDER`，G15 断言不受影响）；
用户落地路径：PDF/图片/文字 → OCR → TF-IDF 快照 → 向量海余弦搜索 → TVCB 精炼 → 技能机床加工 → 12 协议适配导出 → 部署到任意平台。
Guard 默认 9 层、L10 默认关（附加层不计入 `guard_layers=8`）；装配后快照 agents=46（含四人组 5 角色）、skills=243（含四人组 14 技能），均为扩展包旁挂增量。

### V20 · 概念解剖器 · 落地场景版（V20-A→C，V19 重设计，不改维度）

V19 做了**能力**（能解剖概念），没做**用途**（解剖出来能干嘛）；V20 补上**用途**——概念解剖器 = HoloAeon 项目的"汉字字典"：看到"经络""赫布场""城邦"看不懂时，一条命令 `python -m holoaeon.concept_anatomy 经络 --explain` 用大白话告诉你这是哪个模块、由哪些零件组成、怎么验证它在工作、去哪看源码。对应 `AGENT_FEED_V20_CONCEPT_ANATOMY_REDESIGN_TEXT_20261104.md`（原补丁包 `AGENT_FEED_V20_PATCH_V19_CLOSURE_20261104_OBSOLETE.md` 改名作废）步骤 A→C 贯序执行；四人组决策（emergence=True，P2×P3=0.7225、P1=0.85、P4=0.30、order=0.5237）：

1. **V20-A · explain() 大白话函数**：`concept_anatomy.py` 新增模块级 `explain(concept) → str`（从 CONCEPT_MAP 取真值格式化：维度中文名 `DIMENSION_CN` 映射（mechanism→机制类等 9 类）→ 一句话 → 靠什么实现 → N 个零件清单 → 怎么验证 → 去哪看源码；未知概念返回"「x」不是内置概念 + 可用概念列表"；默认演示"经络"）。
2. **V20-B · CLI --explain + __main__ 守卫**：`main()` 追加 `--explain` 分支（大白话文字模式，非 JSON）；文件末尾补 `if __name__ == "__main__": sys.exit(main())` —— **修复 V19 已知点**（`python -m holoaeon.concept_anatomy` 直跑无输出）。
3. **V20-C · 使用手册 + 测试**：新建 `docs/V20_概念解剖器_使用手册.md`（非技术手册：一段话定位 + 三个真实落地场景【新人看代码 / 改代码前查影响 / 写文档贴材料】+ 一条命令速查 + 10 概念大白话速查表）；`docs/V19_概念解剖器_小白导学手册.md` 已知点段落同步更新（标注 V20 已修复）；新建 `tests/test_v20_concept_anatomy.py`（12 tests：explain 全 10 概念 / 未知 / 默认演示、DIMENSION_CN 全覆盖、CLI --explain / JSON 回归、`-m` 守卫三模式 subprocess 实测输出非空）。

验证全绿：`selftest 25/25` · `unittest 121 OK`（109+12）· `redline 103 文件 0 违规` · `v3_gate 32/32` · 维度锁 0 violation（diff0=2fc892cf9af6e755 未漂移）· `contract PASS` · `py38 249 文件 0 失败` · `plugin runtime 10/10` · verify_v44 13/13 · `VERSION=0.9.1` 冻结未动 · `DOC_VERSION=0.9.16`（不变）· `EXTRA_PACK_ORDER=17`（不变）。

**维度不变**：25 / 47 / 9、`VERSION=0.9.1`、`diff0_hash=2fc892cf9af6e755`、`tamper=f42c8229ee5acd73`；新增 explain() 不改任何现有输出路径。用户落地路径：新人看代码 `python -m holoaeon.concept_anatomy 经络 --explain` → 改代码前 `python -m holoaeon.concept_anatomy 皮肤机制 --explain` 查组件影响 → 写文档 `explain("去幻觉")` 直接贴进材料。下一步 V21 = 多模态版（SVG 交互图 + 语音解说）。

### V19 · 概念解剖器 · Anatomy 创意蒸馏（V19-A→F，不改维度）

`DOC_VERSION` 0.9.15 → **0.9.16**（`spec.VERSION` 仍 0.9.1）。对应 `AGENT_FEED_V19_CONCEPT_ANATOMIZER_ANATOMY_DISTILLATION_20261104.md` 步骤 A→G 贯序执行。蒸馏口径：wheresryan22/anatomy（22K★ Claude Agent Skill，"The object is the explanation"）→ 第一性原理交集=**概念→确定性机制→运行验证概念**（Anatomy=视觉发明 LLM / HoloAeon=确定性查找 规则，步骤 3"发明对象"由 LLM 改为固化映射表查找）→ 四人组决策（emergence=True，P2×P3=0.7225、P1=0.85、P4=0.30、order=0.5237）→ **5 精华 D-01~D-05 + 剔除 4 糟粕 X-01~X-04**（WebGL 着色器 / React 绑定 / 打印 PDF / 截图验证）：

1. **V19-A · 概念解剖器**：新建 `holoaeon/concept_anatomy.py` —— `ConceptAnatomizer` 十步工序（定维度→取真值→发明映射→列组件→规划→构建→排序→装框→激活→审计）；`CONCEPT_MAP` 10 概念固化映射表（经络/心跳机制/细胞骨架/皮肤机制/经络机制/赫布协作场/语义通信基座/城邦架构/自组织耗散/去幻觉）；`DESIGN_TOKENS` 26 Token（运行时 6/审计 5/输出 5/验证 5/全息 5）；等距投影 SVG 渲染（30° COS30/SIN30，纯字符串拼接）；**确定性**：同概念+同Token→同解剖图（时间戳默认关闭 out_timestamp=False）；深度审计四检查（重叠对/穿透 depth 单调性/一致性/确定性）。
2. **V19-B · 概念解剖扩展包**：新建 `holoaeon/packs/concept_anatomy_pack.py` —— 继承 `DomainPack`，key="concept_anatomy"，**5 技能/3 角色/1 工作流**（技能 anatomy_concept/anatomy_audit/anatomy_svg/anatomy_map/anatomy_tokens；角色 anatomist/auditor/cartographer；工作流 full_anatomy）；SkillSpec 按 base.py 实际字段定义，模块级函数实现零依赖。
3. **V19-C · 注册第 17 扩展包**：`packs/__init__.py` import `ConceptAnatomyPack` + `EXTRA_PACK_REGISTRY` 登记 + `EXTRA_PACK_ORDER` 追加 `"concept_anatomy"`（16→**17**）；注释补第二十三。
4. **V19-D · 菜单+命令**：`butler_os.py` 菜单追加 [12]概念解剖（`cmd_concept_anatomy` 演示"经络"：扩展包 5/3/1 统计 + 10 可用概念 + 解剖结果 + 四审计数 + SVG 长度）；`pyproject.toml` 追加 `holoaeon-anatomy="holoaeon.concept_anatomy:main"`（现 11 命令）。
5. **V19-E · 文档版本**：`spec.py` DOC_VERSION="0.9.16"（VERSION="0.9.1" 冻结未动，diff0 保护不破）。
6. **V19-F · 集成测试**：新建 `tests/test_v19_concept_anatomy.py` —— 19 tests（26 Token 五组/10 概念全 DONE/确定性两次一致/穿透审计/SVG/第 17 扩展包注册/菜单 12/CLI）；`tests/test_v12_v17_integration.py` 伴随更新 `all_extra_packs()==16→17`。

验证全绿：`selftest 25/25` · `unittest 109 OK`（含 V19 新 19 tests）· `redline 103 文件 0 违规` · `v3_gate 32/32` · `verify_v44 13/13` · 维度锁 0 violation（`diff0=2fc892cf9af6e755` **未漂移**——EXTRA_PACK_ORDER 16→17 不触发：selftest 对 EXTRA 仅断言 len>=7 + 成员包含，VERSION/RUNTIME_ID 未动）· contract PASS · py38 语法 248 文件 0 失败 · plugin runtime 10/10 · butler_os 菜单 12 实操 DONE · 装配快照 agents=**59** skills=**267**（+3 角色 +5 技能 旁挂增量，G15 不受影响）· five_site package=28/repo=171/missing=0 · zip 不动点 a87fa921bf963fa1 保持。

**维度不变**：25 / 47 / 9 与 `spec.VERSION=0.9.1`、`diff0_hash=2fc892cf9af6e755`、`tamper=f42c8229ee5acd73`；`EXTRA_PACK_ORDER` 16→**17**（第 17 扩展包仅旁挂，不进 `PACK_ORDER`）；用户落地路径：概念名 → 固化映射表确定性查找 → 十步工序解剖 → 深度审计 → 等距投影 SVG → JSON 解剖图回执。

### V17 · 玉安记忆之王 + V18 · V6 补丁收尾 + 集成验证（V17→V18，不改维度）

`DOC_VERSION` 保持 **0.9.15** 不变（V17 记忆模块在源码树外，V18 不改源码，不触发版本升级）。对应 `AGENT_FEED_V18_PATCH_CLOSURE_V17_BRIDGE_INTEGRATION_20261104.md` 步骤 A→E 贯序执行：

1. **V17-A · 玉安记忆之王执行**：新建 `F:/doubaowork/memory_of_yuan.py`（项目外，纯标准库）—— 10 记忆域 JSON（`F:/doubaowork/holoaeon_memory/`：engineering_discipline/engineering_process/output_dimensions/five_site_sync/verification_procedures/version_history/holographic_system/quartet_toolkit/haole_yuan_lab/vector_sea）+ `.pth` 全域注册两处（.workbuddy 3.13.12 site-packages + sandbox site-packages，指向 `F:/doubaowork`）+ SKILL.md（`holoaeon` 关键词引发）；赫布场 learning_rate=0.12 decay=0.99；`memory_graph` 中英混合 token 分词（edges=8≥5）；封口密语：潮起开门，潮落闭嘴。V17 验证清单 9/9 PASS（10 域 / 全域加载 / 跨目录 seal / 全息 matched=5 / versions=16 / edges=8 / 同义 holoaeon / 封存 True / selftest 25/25）。
2. **V18-A · V6 遗留 12 项代码卫生审计收口**：逐项核验 —— 10 项已修/不适用 + 1 项已知漂移非阻断（test_holoaeon.py:316 断言 >=7）+ 1 项残留 CI 缺口低优先级（无 .github/workflows）；**正式收口，无需额外代码修改**。
3. **V18-B · 集成测试**：新建 `tests/test_v12_v17_integration.py` —— 7 个 TestCase 22 tests 覆盖 V12-V17 六模块 + 跨模块协同（all_extra_packs()==16 / Kernel 装齐 9+16 包 submit / EXTRA_PACK_ORDER 顺序 topology_resonance→quartet_director→vector_sea→dehallucination→super_agent / butler_os 源码包含 vector_sea/dehallucination/router 字样；V17 已执行故不 skip；V13/V14 API 名按实际函数式 API 适配）。

验证全绿：`selftest 25/25` · `golden verify 5/5`（verify_all(n=2) 5 tasks True）· `集成测试 22 OK` · `unittest 90 OK`（主 tests，含 22 集成）+ verax 21 OK + v3 5 OK · `redline 101 文件 0 违规` · `v3_gate 32/32` · `verify_v44 PASS` · 维度锁 0 violation（`diff0=2fc892cf9af6e755` 未漂移）· contract PASS（PACK 9 / EXTRA 16）· MCP 回归 4/4 · V17 记忆模块 10/10 domains · `DOC_VERSION 0.9.15`（不变）· 承 **V16 确定性自主调度增强**。

### V16 · 确定性自主调度增强 · DeepSeek Super-agent 对标蒸馏（V16-A→E，不改维度）

`DOC_VERSION` 0.9.14 → **0.9.15**（`spec.VERSION` 仍 0.9.1）。对应 `AGENT_FEED_V16_SUPER_AGENT_DISTILLATION_20261103.md` 步骤 A→E 贯序执行。蒸馏口径：DeepSeek Super-agent（Router-Worker 双层/事件驱动/异步多信道/存算分离/外部 Watchdog）→ 对标矩阵（异步多信道=Envelope+adapter、存算分离=Memory+Kernel、Checkpoint=V11，已有不借鉴）→ 四人组决策（emergence=True）→ **5 精华 D-01~D-05 + 剔除 4 糟粕 X-01~X-04**，第一性原理交集=**确定性的自主调度**（规则驱动非 LLM，同输入同输出）：

1. **V16-A · 确定性 Router 层**：新建 `holoaeon/router_layer.py` —— `RouterLayer`（task_queue deque / shared_context / dispatch_rules 按 priority 排序 / worker_results / is_running）；`receive→_dispatch` 带**有序字符匹配降级链**（连续子串未命中时逐字符按序匹配，`_match_rule` 静态方法确定性分派），'帮我写一篇文章'→writing_planner、'分析这份销售数据'→data_analyst、无关闲聊→'*'；`aggregate` / `get/update_shared_context` / `status`；`main` CLI（`--selfcheck` / 单条路由）。
2. **V16-B · 事件两级过滤**：新建 `holoaeon/event_filter.py` —— `EventFilter`（FAST_PATTERNS 14 词快速级 + DEEP_RULES 4 条 lambda 深检级），`filter()` 两级返回 `passed/level/reason`（L2=passed、L1=无关、bug 词命中=urgent），`batch_filter` / `main` CLI。
3. **V16-C · 外部 Watchdog**：新建 `holoaeon/external_watchdog.py` —— `ExternalWatchdog`（BASE_LINE 冻结基线 dict），`check_selftest/check_diff0/check_redline` **只 observe 不执行**、`alert` **只告警不拦截**（Guard L1-L10 外部伴生，不碰内核）、`snapshot`；`main` CLI。
4. **V16-D · 自主调度扩展包**：新建 `holoaeon/packs/super_agent_pack.py` —— 继承 `DomainPack`，key="super_agent"，**5 技能/3 角色/1 工作流**（技能 router_dispatch/event_two_filter/watchdog_monitor/context_isolate/proactive_scan；角色 router_coordinator/filter_engineer/watchdog_operator；工作流 super_agent_flow）；自实现零依赖；selfcheck 断言 D01=writing_planner D02=L2 D03=1 D04=True D05=50。
5. **V16-E · 注册四处**：`packs/__init__.py` import `SuperAgentPack` + `EXTRA_PACK_REGISTRY` 登记 + `EXTRA_PACK_ORDER` 追加 `"super_agent"`（15→**16**）；`spec.py` DOC_VERSION="0.9.15"（VERSION="0.9.1" 冻结未动）；`butler_os.py` 菜单追加 [11]自主调度（cmd_super_agent 完整演示）；`pyproject.toml` 追加 `holoaeon-router / holoaeon-watchdog`（现 10 命令）。

验证全绿：`selftest 25/25` · `unittest 68 OK`（tests/verax 21 OK + tests/v3 21 OK）· `redline 101 文件 0 违规`（+4 新 py）· `v3_gate 32/32`（A12.1 零依赖未破）· 维度锁 0 violation（diff0=2fc892cf9af6e755 未漂移）· `verify_v44 13/13` · contract PASS · MCP 回归 13/13（doc_version 期望同步 0.9.15）· 四新模块 selfcheck 全 PASS（router dispatch 4 类 / event_filter L2 / watchdog alerts=1 / super_agent 5·3·1）· 装配快照 agents=**56** skills=**262**（+3 角色 +5 技能 旁挂增量，G15 不受影响）· 写型链全绿（b8 245/91 interface_equal=true · b9 criteria=30/risks=12/ledger=12 zip 不动点 a87fa921bf963fa1 保持 · five_site package=28/repo=171/missing=0 · vector_sea_manifest 195/195）。

**golden 重冻结（V16 修复项，如实披露）**：排查并修复历史遗留 word_count 黄金失配——实锤为 **V6 起 agent.py:42（handle() 写 result["degraded"]）新增字段**致 V3 时代冻结黄金值过期（删字段后哈希恰=2b82a6ef7188ce91 原值）；ftrace 证明非 V16 引入（stash 四文件后仍 FAIL）。单点重冻结 3 个 golden：word_count 2b82a6ef7188ce91→**e1b6c4ba5c26943b**、data_describe 3352db0f803eb727→**8cd80c70ad275455**、quant_sharpe 2c9e5d7d01526ce8→**8ee7170326666303**（frozen_at=2026-11-03，note 注明旧→新哈希）；`tests/verax/test_repro.py` GOLDEN_HASH 同步 e1b6c4ba5c26943b；verax_verify 复现 5/5 全 golden=True。verax_verify 总结论 yellow（H2=3：scan_receipts 逐行扫多行 indent JSON 的口径局限——dimension_lock.json:21/31 与 daily_gate 中间行被误判缺 evidence_class，顶层实含 evidence_class="simulated"，非真实违规；V2 三硬红线 hits=[] 全绿）。全仓 2b82a6ef7188ce91 共 40 处引用均为历史投喂包/README/docs/snapshot/_cases 演示用例，不改、如实披露口径。

**维度不变**：25 / 47 / 9 与 `spec.VERSION=0.9.1`、`diff0_hash=2fc892cf9af6e755`、`tamper=f42c8229ee5acd73`；`EXTRA_PACK_ORDER` 15→**16**（第 16 扩展包仅旁挂，不进 `PACK_ORDER`）；用户落地路径：任务 → RouterLayer 确定性分派（有序字符匹配）→ EventFilter 两级过滤 → ExternalWatchdog 外部只读伴生监护（只告警不拦截）→ super_agent_pack 5 技能自主调度闭环。

### V15 · 自组织相似性全息去幻觉模块（V15-A→D，不改维度）

`DOC_VERSION` 0.9.13 → **0.9.14**（`spec.VERSION` 仍 0.9.1）。对应 `AGENT_FEED_V15_DEHALLUCINATION_LEIBNIZ_ZHANGPING_20261103.md` 第三部分，步骤 A→D 贯序执行（莱布尼茨充足理由律 × 张平语义基 × HoloAeon 赫布场）：

1. **V15-A · 去幻觉模块**：新建 `holoaeon/dehallucination.py` —— `DeHallucinationModule` 8 阶段流水线（input→seb_extract→reality_anchor→snapshot_vec→leibniz_compare→synonym_map→verdict→hebbian_update）；核心阈值 `COSINE_HIGH=0.7`（≥0.7 非幻觉）`COSINE_LOW=0.4`（<0.4 幻觉）0.4-0.7 待审⚠️、`BAYES_PRIOR=0.15` `BAYES_THRESHOLD=0.5`；联网经 `fetch_callback` 回调注入（不硬编码 WebSearch），None 时降级内部比对；贝叶斯后验 (likelihood×prior)/(likelihood×prior+(1-likelihood)×(1-prior)+1e-10)；耗散熵=归一化信息熵；`check()` 返回 module/input_text/semantic_base/reality_snapshot/cosine/synonym/bayesian/dissipation/sufficient_reason/verdict/hebbian_weight/theory/timestamp；附 `selfcheck()` 三分支确定性自检 + `main()` CLI；纯标准库零依赖（verify_v44 A12 零依赖未破）。投喂参考代码 `main()` 的 `--callback` 分支注释与实现不符（所有 argv 拼 text），已转写为可运行实现（实际降级无联网模式可跑）。
2. **V15-B · 去幻觉扩展包**：新建 `holoaeon/packs/dehallucination_pack.py` —— 继承 `DomainPack`，key="dehallucination"，**6 技能/3 角色/1 工作流**（技能 semantic_base_extract/reality_anchor/leibniz_space_compare/synonym_mapping/hallucination_verdict/hebbian_feedback；角色 anchor_engineer/semantic_analyst/verdict_judge；工作流 dehallucination_flow）；阈值从 `dehallucination` 常量 import 保持口径一致，技能函数内联实现零依赖。投喂验证清单第 7 项 `p.SKILLS` 大写与 base.py 契约不符，已按契约属性复测 skills=6 roles=3。
3. **V15-C · 注册第 15 扩展包**：`packs/__init__.py` import `DeHallucinationPack` + `EXTRA_PACK_REGISTRY` 登记 + `EXTRA_PACK_ORDER` 追加 `"dehallucination"`（14→**15**）。
4. **V15-D · 菜单+命令+文档版本**：`butler_os.py` 菜单追加 [10]去幻觉检测（cmd_dehallucinate 读输入→8 阶段检测输出语义基/快照/余弦/同义/贝叶斯/熵/充足理由/判定/赫布权重，空输入用演示样本）；`pyproject.toml` 追加 `holoaeon-dehallucinate="holoaeon.dehallucination:main"`。

验证全绿：`selftest 25/25` · `unittest 68 OK` · `tests_contract 184 OK` · `redline 97 文件 0 违规`（+2 新文件）· `v3_gate 32/32`（A12.1 零依赖未破）· 维度锁 0 violation（diff0=2fc892cf9af6e755 未漂移）· `verify_v44 13/13` · MCP 回归 13/13（doc_version 期望同步 0.9.14）· 模块自检 PASS（三分支 non_hallucination/hallucination/uncertain）· 扩展包自检 PASS（6/3/1）· 降级检测 '人工智能多智能体系统架构设计' → verdict/cosine/entropy 三值齐 · 装配快照 agents=**53** skills=**257**（+3 角色 +6 技能 旁挂增量，G15 不受影响）。

**维度不变**：25 / 47 / 9 与 `spec.VERSION=0.9.1`、`diff0_hash=2fc892cf9af6e755`、`tamper=f42c8229ee5acd73`；`EXTRA_PACK_ORDER` 14→**15**（第 15 扩展包仅旁挂，不进 `PACK_ORDER`）；用户落地路径：AI 输出 → 语义基提取（张平 Seb）→ 联网取点快照（莱布尼茨充足理由）→ 余弦空间比对 → 同义映射 → 贝叶斯+耗散熵判定 → 赫布反馈自组织学习。

**全息体系对应表（V16 更新版）**：**经络 = 自组织相似性类节点共振**（`topology_resonance_pack.resonance_node`：1331×1331 共振 + 莫比乌斯回边 + 克莱因收敛熔断），**≠ Bus**；**经络机制 = Bus**（C2 发布/订阅/路由消息总线，独立概念）；心跳=Scheduler（tick=500ms adaptive）；细胞骨架=Kernel；皮肤=Guard L1-L10；赫布协作场=AdaptiveGraph（node_count=17 lr=0.12 decay=0.99）；语义通信基座=Envelope C1+Skill manifest C4+张平 Seb；runtime=Kernel+Scheduler+topology_runtime.py（StateReducer/Checkpoint/CircuitBreaker/DissipationMonitor）；graph=AdaptiveGraph+topology_resonance_pack 三 Graph 函数（mandala_expand/mobius_flip/klein_convergence）；城邦=九层词汇表（V11）；耗散结构五要件（开放系统←Envelope 接收/联网取点、远离平衡态←Scheduler tick、非线性←decay×learning_rate、涨落放大←resonance_node+mobius_edge、涌现←emergence_chain 四条件）；产品层：躯体=butler_os/灵魂=quartet_toolkit 14 技能/勘探=vector_sea_explorer/机床=skill_lathe/协议=protocol_plugins/去幻觉=dehallucination.py（V15 新增）/**调度=router_layer.py（V16 新增，确定性任务路由）+事件过滤=event_filter.py（两级过滤）+外部看门狗=external_watchdog.py（只 observe 只告警）+自主调度=super_agent_pack（5 技能/3 角色/1 工作流）**；语义知识库=向量海 617 技能+195 篇+10 GEMS+462 项。


### V3 · 借鉴 LangChain 的工程形态（文档版本 0.9.3）

一句话完成升级：`python scripts\launch_v3.py` —— 装载 V3 旁挂件、跑通内部融合 + 外部路由 +
桥 conformance，末行打印 `ALL_OK=True`。

维度不变：**25 智能体 / 47 技能 / 9 领域包 + 8 扩展包 / 34·21·5 单测 / 25 自检**，
`spec.VERSION` 仍是 `0.9.1`，`DIFF=0 2fc892cf9af6e755` 与篡改哈希 `f42c8229ee5acd73` 未动。
V3 新增 32 项门禁检查，**独立计数**，不并入上面任何一格。

八个旁挂工作包（全部零依赖、可跑）：统一调用协议与五段钩子（`runnable.py`）、
可哈希 span 树（`audit/span_tree.py`）、结构化 schema 校验与有限修复环（`skill_schema.py`）、
47 条评测集与双轨 diff（`scripts/eval_set.py` / `eval_diff.py`）、
interrupt 审批令牌与三档 checkpoint（`interrupt.py`）、渐进加载与字节缓存
（`skill_loader.py` / `cache.py`）、replay 分支与 7 类事件流（`replay_branch.py` / `event_channel.py`）、
桥 conformance 与迁移/弃用页（`bridges/conformance.py` / `docs/migration-from-langchain.md`）。

实测（本机 2026-11-01）：V3 门禁 `32/32 PASS`；`eval_47` 确定性轨 `47/47`（自述自证，
只证明路由不退化）；对抗变体 `cross` `0/47` 且 diff 判 `REGRESSED`（证明能抓回归）；
kfold 仍 `mean 0.9957 / std 0.0085`。机器可读接手页：[`snapshot/SNAPSHOT_V3.md`](snapshot/SNAPSHOT_V3.md)。

## 为什么选择 HoloAeon

| 原则       | 实际含义                            | 实测证据                         |
| -------- | ------------------------------- | ---------------------------- |
| **零依赖**  | `dependencies = []`，纯标准库，不装任何东西 | 红线扫描 
edline_scan 回读（当前 82 文件）零违规                |
| **默认离线** | 无网络调用、无内置密钥、无遥测                 | 核心包零网络 import（语法树级检查）        |
| **确定性**  | 相同输入产生相同输出                      | A1 验收双跑哈希逐位一致，CI 强制证据防漂移     |
| **可审计**  | 每次决策留痕、带理由码、可回放                 | nephron 认知账本，任意历史 tick 可重建   |
| **安全边界** | 八层语义守卫拦截危险操作                    | `os.system`/`eval`/越权/失真实测拦截 |
| **诚实纪律** | 仿真标记 `simulated`，未实测挂 `pending` | 第三方审计三轮，零虚报                  |

### Token 经济学：让 token 只花在语言上

统计、校验、格式化、流程编排等确定性工作由本地零成本执行，大模型只处理真正的语言任务——
校验类任务 token 从 O(材料长度) 降到 O(结论长度)，日常重度使用差额可达 30%–70%。

### 部署形态

| 形态                   | 说明                              |
| -------------------- | ------------------------------- |
| **纯骨架**（512MB 内存、无网） | 全部核心功能，零成本                      |
| **本地大脑**（+4GB 内存）    | 桥接 Ollama，AI 回答本地生成，仍免费离线       |
| **云端大脑**（+网络+密钥）     | 桥接豆包/千问/OpenAI 兼容端点，密钥只进环境变量    |
| **对话前端**             | WorkBuddy / 豆包工作技能包——自然语言驱动整套架构 |

---

## 🚀 快速使用说明（低配个人用户特化）

### 它能在什么机器上跑？

| 你的机器                                        | 能跑什么                                             |
| ------------------------------------------- | ------------------------------------------------ |
| 任何能装 Python 3.8 的电脑（2010 年后基本都行），512MB 空闲内存 | ✅ 全部核心功能：25 智能体、47 技能、账本、守卫、热插拔——**不需要显卡、不需要联网** |
| 上述 + 4GB 内存 + 约 4GB 硬盘                      | ✅ 额外可接本地真模型（Ollama + qwen2.5:0.5b）               |
| 上述 + 网络 + API 密钥                            | ✅ 额外可接豆包/千问等云端模型                                 |

> 一句安心话：HoloAeon 核心是 3547 行纯标准库 Python，`pip install` 不安装任何东西，
> 不写注册表、不留后台进程——程序退出即消失。老机器放心折腾。

### 三步跑通（全程约 3 分钟，不联网）

```bash
# 第 1 步：获取（二选一）
git clone https://github.com/weideyouni/holoaeon.git
# 或者：GitHub 页面 Code → Download ZIP → 解压

# 第 2 步：进入目录
cd holoaeon

# 第 3 步：跑第一个示例
python examples/01_basic_matrix.py
```

看到 `runtime_id: HOLOAEON-RUNTIME-0.9.1` 和 25 个智能体清单，就是成功了。

### 你刚刚运行了什么？

一条任务文本被 8 层安全守卫检查 → 自动匹配到 writing 规划智能体 → 调用 `outline_gen`
技能生成大纲 → 结果连同资源占用清单一起回给你。**全程本地、全程确定性：再跑一遍，
输出逐字相同。**

### 接下来玩什么？

```bash
python examples/02_semantic_routing.py           # 语义路由
python examples/03_hebbian_collaboration.py      # 赫布协作
python examples/04_domain_pipeline.py            # 领域包流水线
python scripts/launch_local.py status            # 全家福健康报告
python scripts/launch_local.py run "你的任务"     # 提交任务，自动选智能体
python scripts/launch_local.py hotplug optimization  # 不重启热插拔优化包
```

### 想让 AI 真的开口说话？（可选，仍免费的本地路线）

```bash
# 前提：4GB 内存 + 约 4GB 硬盘。装 Ollama（ollama.com）后：
ollama pull qwen2.5:0.5b
python bridges/quickstart.py --check   # 自动探测本机模型
python bridges/quickstart.py --ask "用一句话解释什么是阴阳"
# 回执五要素：output / backend / mode=live / tokens / latency
```

没装 Ollama？`--check` 给三行安装指引并礼貌退出（退出码 2），绝不甩一屏报错。

### 💬 想用对话窗口当前端？（WorkBuddy / 豆包工作）

- **WorkBuddy**：把技能文件夹放入 WorkBuddy 技能目录，工作对话里用自然语言驱动整个架构；
- **豆包工作**：技能包 zip 直接拖入"插件·技能·伙伴 → 上传技能"弹窗，Agent 自动发现调用。

**完整逻辑流程**——前端负责"听懂人话"，HoloAeon 负责"确定性干活"：

```
你说："看下架构状态" / "跑个任务" / "热插优化包"
        ↓ 前端智能体加载技能包（意图→命令映射表）
        ↓ 执行确定性命令（launch_local.py status / run / hotplug）
        ↓ Kernel.submit → Guard 八层安检 → 匹配智能体 → 本地执行
        ↓ 结果 + 账本回执返回对话窗口
```

前端可换、骨架不动：对前端唯一的要求，是能跑一条 Python 命令。

### 🛠️ 高手进阶：自己制作一个 skill（7 步完整实例）

技能 = 带清单的确定性函数。三层结构：`SKILL.md`（声明层）+ `tools/`（执行层）+ `data/`（数据层）。

以 `bmi_calc` 为例（15 分钟走完全程，以下代码实测通过）：

**第 1 步 定意图**：BMI=体重÷身高²，同输入必同输出 ✅；医疗相关，伦理边界写死在输出里。

**第 2 步 搭目录**：`bmi_calc/SKILL.md + tools/bmi_calc.py`。

**第 3 步 写 SKILL.md**：

```markdown
---
name: bmi_calc
description: "BMI 计算器：输入身高体重，输出 BMI 与 WHO 分类。
学术参考，健康评估请咨询医师。触发词：BMI、体重指数。"
---
```

**第 4 步 写执行层**（`tools/bmi_calc.py`，纯标准库）：

```python
def calc(height_cm: float, weight_kg: float) -> dict:
    m = height_cm / 100.0
    bmi = round(weight_kg / (m * m), 1)
    cat = ("偏瘦" if bmi < 18.5 else "正常" if bmi < 25
           else "超重" if bmi < 30 else "肥胖")
    return {"bmi": bmi, "category": cat, "note": "（学术参考，健康评估请咨询医师）"}
```

**第 5 步 注册并测试**：

```python
from holoaeon import Kernel
from holoaeon.agent import Agent
k = Kernel()
def bmi_task(task):
    _, h, w = task.replace("帮我算 BMI", "").split()
    return calc(float(h), float(w))
k.skills.register_fn("bmi_calc", bmi_task, description="BMI 计算与分类")
k.register_agent(Agent("health_bot", "health", skill_names=["bmi_calc"]))
print(k.submit("帮我算 BMI 170 65")["results"][0]["output"])
# → {'bmi': 22.5, 'category': '正常', 'note': '（学术参考，健康评估请咨询医师）'}
```

**第 6 步 确定性验收**：`assert calc(170,65) == calc(170,65)`——同输入两次逐字一致。
**第 7 步 多平台部署**：豆包拖上传弹窗 / WorkBuddy 放技能目录 / 纯 HoloAeon 直接用。

> 以上代码实测回执：匹配 ✓、输出 ✓、复跑一致 ✓——**47 个内置技能，每一个都是这样诞生的。**

### 📖 实战案例：一次对话创作 3 万字《燕京医派全派数字分身·全息自述》

| 步骤     | 实际发生的事                                      | 体现的能力                 |
| ------ | ------------------------------------------- | --------------------- |
| 技能索引匹配 | 644 项本地技能索引命中 193 项，精确找到燕京三脉矩阵包（评审 91.5/A+） | 知识资产可检索               |
| 大纲生成   | `outline_gen` 骨架 + 素材融合成 13 单元大纲            | 确定性骨架 + 人工创意          |
| 正文创作   | 3 万字四轮注入，13 处锚点 0 失配                        | 确定性编辑可靠性              |
| 编辑验收   | writing_editor 回执：810 句 / 29,497 字符         | 全程有账可复现               |
| 诚实缺陷   | 自动匹配 2 次误路由，如实记录                            | **不冒充——连接待页都在示范 DNA** |

三个优势：素材定位从小时级降到秒级；合规项按清单自动执行；同链路任何人可复现对账。

### 📚 47 个技能全目录（九大领域包）

| 领域包                 | 技能（能做什么）                                                                                                                       |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **writing 写作**      | `title_brainstorm` 标题风暴｜`outline_gen` 大纲生成｜`word_count` 字数统计｜`readability` 可读性｜`structure_check` 结构检查                          |
| **literature 文献**   | `screen_papers` 文献筛选｜`extract_abstract` 摘要提取｜`normalize_citation` 引文规范｜`dedup_papers` 文献去重｜`reproduce_check` 复现性核查             |
| **research 研究**     | `design_experiment` 实验设计｜`sample_size` 样本量｜`hypothesis_check` 假设检验｜`variables_split` 变量拆分｜`missing_report` 缺失报告                |
| **data 数据**         | `csv_profile` 数据画像｜`normalize_column` 列规范｜`outlier_detect` 离群检测｜`basic_stats` 基础统计                                             |
| **growth 成长**       | `goal_smart` SMART 目标｜`habit_plan` 习惯计划｜`weekly_review` 周复盘｜`task_breakdown` 任务拆解｜`energy_mapping` 精力映射                        |
| **business 商业**     | `business_model_canvas` 商业画布｜`swot_analysis` SWOT｜`kpi_dashboard` KPI 看板｜`risk_register` 风险登记｜`meeting_agenda` 会议议程            |
| **quant 量化**        | `returns` 收益｜`volatility` 波动率｜`sharpe` 夏普｜`drawdown` 回撤｜`backtest` 回测｜`moving_average` 均线                                      |
| **optimization 优化** | `golden_section`｜`gradient_descent`｜`newton_method`｜`conjugate_gradient`｜`simplex_method`｜`penalty_method`｜`genetic_algorithm` |
| **gaoyi 高译**        | `gaoyi_compile` 自然语言编译 HASM｜`gaoyi_exec` 虚拟机执行｜`gaoyi_run` 一键编译运行                                                              |

另有 8 个横切扩展包（sovereignty 查询锻造 / subdistill 知识蒸馏 / omnilife 生活主权 /
omnicore 认知引擎 / metab 治理 / nephron 账本 / uplift 加固 / persona_quartet 代号数字分身）——不占九包口径，只加能力。

### ❓ 出错了看这里

| 症状                 | 药方                                                   |
| ------------------ | ---------------------------------------------------- |
| `python 不是内部或外部命令` | 装 Python 3.8+（老机器选 3.8.10 32 位版），勾选 Add to PATH      |
| 中文乱码               | 终端执行 `chcp 65001`（UTF-8）                             |
| 中文路径报错             | 项目移到纯英文路径，如 `D:\holoaeon`                            |
| 杀毒软件提示             | 零网络零系统写入，源码全可审：`python scripts/redline_scan.py` 自证清白 |

---

## 架构总览

```
┌─────────────────────────────────────────────────────────────┐
│                      应用 / 用户 / 对话前端                    │
├─────────────────────────────────────────────────────────────┤
│  领域包  writing · literature · research · data               │
│          growth · business · quant · optimization · gaoyi    │
├─────────────────────────────────────────────────────────────┤
│                        Kernel（门面）                         │
│        submit · collab · choose_agent · tick · health        │
│   冷/热插拔 · 内部融合 · 外部融合                              │
├──────────────┬──────────────────────────────────────────────┤
│  Scheduler   │  Guard（L1–L8）        Memory（三层）          │
│  心跳        │  边界与安全             working/long/archive  │
├──────────────┴──────────────────────────────────────────────┤
│            Adaptive Graph（六边形、赫布）                      │
├─────────────────────────────────────────────────────────────┤
│    Bus（主题/寻址/路由） · Envelope      nephron 认知账本       │
├─────────────────────────────────────────────────────────────┤
│  Agent + Skill Registry   Hypervector Space（HRR）            │
├─────────────────────────────────────────────────────────────┤
│  Actor Cluster（并行）        Model Adapter + bridges（桥）    │
└─────────────────────────────────────────────────────────────┘
```

隐喻→工程映射：心跳=调度 tick｜皮肤=守卫 L1-L8｜经络=语义路由｜细胞骨架=生命周期/持久化｜赫布场=共激活权重自适应｜全息=局部携带全局摘要。**隐喻是修辞，实证是确定性软件。**

## 测试

```bash
python -m unittest discover -s tests    # 34 项单元测试
python -c "from holoaeon.selftest import run_all; print(run_all())"  # 25/25 自检组
python scripts/redline_scan.py          # 红线扫描：零违规
python scripts/measure_a1_a2.py         # A1/A2 宿主侧实测（CI 已挂载）
```

当前状态：**34 单测通过｜自检 25/25 组｜红线扫描零违规（文件数以 
edline_scan 回读为准，当前 82）｜A1 证据哈希 CI 防漂移**；
CI 已在 GitHub 实跑并通过：[run #25](https://github.com/weideyouni/holoaeon/actions/runs/41202167792)
在 Python 3.8 / 3.10 / 3.12 三版本全绿（0 error 0 warning），对应格子见
[`docs/support-matrix.md`](docs/support-matrix.md)。

## 路线图

- **v0.9.1**（当前）——可信度实证加固：版本单一源、证据防漂移、桥 README、CI 挂 A1
- **v0.10**——nephron P1 判定层实现（规格已冻结于 docs/nephron-p1.md）
- **v0.9.2**——第八横切扩展包 persona_quartet（四个代号数字分身 P1–P4：探微/筑基/构弦/持衡，G25，25/25 自检；全链路去人名化，观点带归因标记，仅仿真、不代表原型人物实时观点、需人类专家终审）
- **v1.0**——API 冻结，文档完整，多平台技能包正式分发

## 贡献

欢迎 Issue 与 PR。提交前请确保自检、单测、红线扫描全部通过；PR 模板含"立场自检"五项
（零依赖、确定性、取舍留痕、代价显式、宿主边界）。

## 开源协议

Apache License 2.0。

## 免责声明

本项目中的生物与宇宙词汇均为隐喻，仅描述软件机制，不构成医学、生物学或临床建议。
所有仿真回执均标记 `simulated`；**仿真不等于证明，人类判断始终是最终权威。**

---

## 附录 A · 五地同步（V11）

**口径（重要）**：本页不硬编码"当前 HEAD"，因为任何文档收尾提交都会让 HEAD 变化，写死即自指失效。
下表为 **V11** 时点读数（契约 184、`repo` 以回读为准、`DOC_VERSION 0.9.11`、zip 以回读为准）；HEAD / HF sha / 回执字节每提交一次就变，故一律以右侧命令回读为准。

| 站点 | 检查命令 | V11 基数（以回读为准） |
|---|---|---|
| S1 本地 | `git rev-parse --short HEAD` | 以回读为准（内容提交先落，清单随后重建） |
| S2 Gitee | `git ls-remote <gitee> refs/heads/main` | 与本地 HEAD 同值（推送后回读） |
| S3 GitHub | `git ls-remote origin refs/heads/main`（延时 12-20 s 回读） | 同上；三值一致 |
| S4 向量海 | `python scripts/build_vector_sea_manifest.py` | 以 `check()` 的 `entries` / `sums_74_in_sync` 回读为准（下一批新号段以 V11 回执为准） |
| S5 Hugging Face | `python scripts/mirror_hf.py --base <old> --head <new>` | 以输出 `sha` 与 `mismatch=[]` 回读为准（与 `git ls-files` 同集；`sha` 以回读为准） |
| 回执 | `python scripts/five_site_dna.py preflight` | `files` / `history` / 字节数以回读为准 |
| 交付 zip | `python scripts/build_b9_zip.py` | 以回读为准 |

**HEAD sha、HF sha、回执字节与 history 条数每提交一次就会变**，本页故意不写死；
读取方式：`git rev-parse --short HEAD`、`mirror_hf.py` 输出的 `sha`、`five_site_dna.py preflight` 的回执路径。

同步纪律（写序不能颠倒）：

1. 先跑会写回执的校验器（`verify_v44/v45/v46/v5`；`verify_v44` 首跑必 11/13，第二次 13/13）→
2. 再建 `SHA256SUMS` / `dual_repo_sums` → 3) 再打确定性 zip → 4) 再建 `five_site_manifest` →
5) 迭代到 zip `sha16` 两次一致（不动点）→ 6) 最后只跑只读校验（`five_site verify` / `preflight` / `unittest` / `v3_gate` / `redline` / `dimension_lock`）。

向量海归档顺序为「先 copy 新件 → 再替换 `74_SHA256SUMS` → 最后 `listdir` 建 `manifest`」；
顺序颠倒会让 `74` 进清单并自指，首次实测即红。回执 `files` 与 `files_count` 必须同源取自 manifest。

---

## 附录 B · 版本升级说明（V3 → V11）

> 口径：sha 取自 `git log` 实测；条目数 / 字节 / `sha16` 以对应批次命令回读为准，不硬编码猜测值。

| 阶段 | 提交 | 主题与产出 |
|---|---|---|
| V3 收口 | `3d359bd` / `32b2667` | LangChain 工程形态旁挂（W12–W19），32/32 门禁，维度不变 |
| 同步基建 | `92fd8b5` / `dfad361` | 五地同步 DNA V1.0→V1.1（G1–G8 + P1–P6），离线哈希校验器 |
| V4.0 开场 | `80089b6` | 冷热插拔升级：第 10 个附加包，**25/47/9 不变** |
| B0–B9 | `055d202` … `c03b19d` | 基线冻结 → 契约 v1 → 六机制映射 → 1229 技能四标签 → 20 例试点 → 语义族 60 → 赫布落盘 → 准入闸 15/15 → 双仓同步 → 五件交付 + 确定性 zip |
| V2.1 | `3b0b32b` | ivsa 只读对账 R1–R7，旁挂 92 → 101 |
| V4.3 | `4f06bc8` / `3d6f956` | 四坑固化（HF model 仓 / 中文路径 / 74→manifest 顺序 / 交付漂移）+ 11/11 |
| V4.4 | `b85b293` | 19 家 provider 目录 + 5 协议拼装、默认全关；A1–A13 13/13 |
| V4.5 | `fb5cdef` / `f0f1bb5` | 真实回环调用：embeddings 200 / 768 维；chat 200 / 41+29 tokens（C 盘 `lms import` 修复） |
| V4.6 | `f0f1bb5` / `978dc10` / `6646315` | 12 卡槽 + 协作指南；C1–C9 9/9；卡槽实数勘误 14→12 |
| V5.0 | `aa88c37` | 康复域知识库全量入库（14 条登记 / ivsa 300 行）；影子维度 D_REHAB 不入锁；`EXT-EVIDENCE-01` 解封而 tier 不变；D1–D10 11/11 |
| V5.0 收尾 | `f214bd5` | 中英文首页同构重排：去陈旧大段引用，改「当前工程状态」表 + 文末两附录；首页纳入 `REPO_FILES`（152 → 154）；`06` 第五节交付表按实测重算 |
| V5.1 设计语汇 | `339d0c4` / `9b2d5d1` | Impeccable 范式本地化：`holoaeon/design_vocab/`（24 命令 / 12 规则 / 3 编译模式 / 4 通道）+ `data/design_vocab_registry.json` + 门禁 `dv 8/8` + 契约测试 8 条（`旁挂 160 → 168`）；**25/47/9 与 12 卡槽均未变** |
| V5.2 代码修正 | 本批提交（用 `git log -1 --format=%h` 回读，避免自指） | 门禁自指修复（A10 兄弟回执排除 + A11 断传染 + skipped 第三态 + 路径去硬编码）、句柄泄漏清零（scripts 回读 0）、CI 补契约/维度锁/设计语汇三道闸、Guard L3 归一化与兜底开关保守版；`diff0` 仍 `2fc892cf9af6e755`，**25/47/9 未变** |
| V6.0 族级登记与路由第三态 | 本批提交（用 `git log -1 --format=%h` 回读，避免自指） | 句柄清零到底（全仓回读 0，补 `tests_contract/` 6 处 + `skills/` 4 处）、`FORBIDDEN_NESTED_OPEN` 资源红线、`no_agent_matched` 第三态 + `degraded` 标记、两开关进 `HoloAeonConfig`、`.env` 误伤收紧（[golden]，`diff0` 未漂移）、**1229 条 → 58 族登记 + 桥接 `external_skill_registry`**（`旁挂 168 → 180`）；`DOC_VERSION 0.9.3 → 0.9.5`，**25/47/9 未变** |
| V6.1-B3 同步卫生 | 本批提交（`git log -1 --format=%h` 回读） | 附录 A 基数改 V6.1 终态并修锚点；记录向量海下一批新号段从 `182` 起；HF 删 10 个非 git 孤儿并补传 `contract_v1_interop_a/b.json`，文件集 `466 → 458` 与 git 跟踪集同集；`DOC_VERSION 0.9.6 → 0.9.7`，**25/47/9 未变** |
| V6.1 纪律固化与 A10 派生 | 本批提交（`git log -1 --format=%h` 回读） | A10 自写回执改 `REPO_FILES` 派生（`self_derive=derived`）、`repo:missing:` 不豁免、排除项记 owner + 前后 sha16 差分证据；批次升级八步写序与五地同步写成 `docs/工程纪律_批次升级与五地同步.md` 并固化为技能 `holoaeon-batch-upgrade-discipline`；`01`/`06` 追加 V6 章节（zip 指纹随之变化，以 `build_b9_zip.py` 回读为准）；`DOC_VERSION 0.9.5 → 0.9.6`，**25/47/9 未变** |
| V8 批2-4 融合升级 | `2fc1faf` / `4bf84df` | L9 路径闸门（`product_layer_guard`）+ 产品层三件套（frontend_adapter / demo_product / install）+ TCM 旗舰包（`tcm_rehab` 第 11 扩展包）+ 领域化解耦；`DOC_VERSION 0.9.8 → 0.9.9` |
| V9 拓扑共振包 | 本批提交（`git log -1 --format=%h` 回读） | `topology_resonance_pack.py`（8 基础数学 + 6 四人组技能）；`EXTRA_PACK_ORDER` 11→**12**；`DOC_VERSION 0.9.9 → 0.9.10` |
| V11 城邦架构融合 | 本批提交（`git log -1 --format=%h` 回读） | 3 Graph 函数 + Guard L10 贝叶斯层 + 新建 `topology_runtime.py` + 2 治理技能（skills 14→16）+ `DOC_VERSION 0.9.10 → 0.9.11`；selftest 25/25 · `diff0` 未漂移 |

**一句话主线**：每批只做一件事，只加旁挂、不改锁数；每批必带判据、票据与五地同步，`drift=[]` 才允许提交。

Seal: 潮起开门，潮落闭嘴 · `evidence_class=simulated`（仿真 ≠ 证明，碳基终裁）
