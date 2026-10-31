# HoloAeon VERAX 可信层 · 交付全文

升级日期：2026-10-31　|　版本：v0.9.1 + audit
产出维度不变：25 智能体 / 47 技能 / 9 领域包 + 7 扩展包 / 34 单测 / 24 自检 / 红线零违规 / 零依赖 / 离线 / 确定性

实测回执（本轮真实跑出）：

- 自检 `==> 24/24`；`tests/` `Ran 34 tests / OK`；`tests/verax/` `Ran 16 tests / OK`
- 红线 `扫描文件数 40 / 结果 干净（零违规）`
- 门禁 `green VERAX_EXIT=0 / yellow VERAX_EXIT=2 / red VERAX_EXIT=1`，三色 verdict_hash 各不相同
- 热插拔 `40 → 47（新增 7，全程未重启）`；本地融合 `总线 25 地址 / all_ok=True`
- 规模：`holoaeon/` 40 个 py / 11,408 行（核心 16/3,851，packs 18/6,872，audit 6/685）

---

## 一、新版 README（升级版开源项目说明）

## HoloAeon · VERAX 可信层（v0.9.1 + audit）

> 零依赖 · 默认离线 · 确定性 · 可审计 · 八层守卫 · 诚实纪律
> 本次升级不新增能力，只是让既有能力**可被复算、可被出示**。

```
VERAX_EXIT=0   |   24/24 自检   |   5/5 基准 stable   |   红线 0 违规   |   dependencies = []
```

---

## 0. 三十秒复现（离线可跑）

```powershell
cd holoaeon
python scripts\verax_verify.py            # 红线 → 自检 → 复现 → 诚实 → 热插拔
## ==> conclusion=green  VERAX_EXIT=0

python -m holoaeon.selftest               # 直接入口，真跑真打印（G1-G24）
python -m unittest discover -s tests      # 34 项既有单测
python -m unittest discover -s tests\verax  # 16 项 VERAX 单测
```

最硬的一条证据：同一个任务跑两次，剔除 `ts` 后哈希逐位相同。

```
word_count  →  2b82a6ef7188ce91   ×2
```

---

## 1. 为什么有这一层

HoloAeon 已有的强项是"确定性"，但它此前是**内部工程习惯**，不是**对外证据**：整包哈希含时间戳导致"假不确定"、自检模块静默退出 0、回执里 `simulated` 与"真实生效"混写。三处都会让别人在 30 秒内得出错误结论。

VERAX 把这三处修成一件可出示的东西：**可复现核心 / 物理量** 分离 → 规范化 → ReproHash → 黄金基准 → 单一退出码 → 自证报告。

---

## 2. 维度不变（硬约束，已实测）

| 维度 | 升级前 | 升级后 | 说明 |
|---|---|---|---|
| 智能体 | 25 | **25** | 未新增 agent |
| 技能（九大领域包） | 47 | **47** | 未新增技能 |
| 领域包 + 扩展包 | 9 + 7 | **9 + 7** | 未加第 17 个包 |
| 全装技能 / 工作流 | 191 / 55 | **191 / 55** | 扩展包不进 `PACK_ORDER` |
| 单元测试（`tests/`） | 34 | **34** | VERAX 测试另立 `tests/verax/`（16 项） |
| 自检 | G1–G24 | **G1–G24** | 24/24 全 PASS |
| 红线 | 0 违规 | **0 违规** | 扫描口径 34 → 40 文件（新增 audit 6 个模块） |
| 依赖 | `dependencies=[]` | **`dependencies=[]`** | 纯标准库 |
| 离线 / 确定性 | 是 | **是** | 无网络、无端口、无常驻 |

规模实测：`holoaeon/` **40 个 py / 11,408 行**（核心 16 / 3,851，`packs/` 18 / 6,872，`audit/` 6 / 685）。

---

## 3. 五件套

| 组件 | 文件 | 作用 |
|---|---|---|
| 字段分类 + 规范化 | `holoaeon/audit/fields.py` | ReproCore / Physical / Opaque 三分；未知字段丢弃并告警 |
| 回执与判定结构 | `holoaeon/audit/receipt.py` | `Receipt` / `ReproVerdict` / `EvidenceClass` |
| 复现验证器 | `holoaeon/audit/verify.py` | n 个全新内核喂同一任务，比对 ReproHash 与 golden |
| 诚实契约 | `holoaeon/audit/honesty.py` | H1 / H2 扫描与合规汇总 |
| 自证报告 | `holoaeon/audit/attest.py` | `attestation.md` + `attestation.jsonl`，`verdict_hash` 可复算 |
| 门禁入口 | `scripts/verax_verify.py` | 单命令合成 0/1/2 退出码 |

---

## 4. 黄金基准（改动须 PR 标题带 `[golden]`）

| task_id | 期望 ReproHash | 期望结果 |
|---|---|---|
| `word_count` | `2b82a6ef7188ce91` | 中文字 20 / 英文词 1 / 总字符 31 / 句 1 |
| `data_describe` | `3352db0f803eb727` | count 3 · mean 2.0 · std 0.816 |
| `quant_sharpe` | `2c9e5d7d01526ce8` | sharpe 5.7752 |
| `guard_os_system` | `a7deb622e17a2b55` | `blocked`（L3） |
| `guard_eval` | `98b9b7b340f7f980` | `blocked`（L3） |

---

## 5. 门禁三色

| 退出码 | 含义 | 实测 |
|---|---|---|
| `0` | 绿：红线干净 + 自检 24/24 + 5 基准命中 + 无诚实告警 | `verdict_hash=ec516f4ed413b5af` |
| `2` | 黄：仅诚实告警（注入一条无来源 `measured`） | `verdict_hash=259eed7b72bdbb49` |
| `1` | 红：基准不一致（篡改 `word_count` 黄金值） | `verdict_hash=5bfa825fb948819e` |

三色各有独立哈希，说明结论字段真的进了 ReproHash（首轮遗漏登记时三者完全相同，已修）。

---

## 6. 证据分级

| 分级 | 语义 | 强制字段 |
|---|---|---|
| `simulated` | 确定性引擎产出（默认） | — |
| `measured` | 本机真跑并留痕 | `measure_source` + `measure_ts` |
| `third_party` | 外部来源 | 同上 + 可核验引用 |

`measured` 缺来源 → **H1（红）**；回执缺 `evidence_class` → **H2（黄）**。

---

## 7. 与既有架构的接入（只读）

观测 `kernel.submit()` 回执、`guard.Verdict.to_dict()`、`selftest.run_all()`、`redline.scan_directory()`、`packs.install()` 前后技能差、`.git/HEAD` 文件；不写内核、不写守卫、不调 git 进程、不起子进程。

---

## 8. 已知限制

1. 数值不转定点字符串（保 `2b82a6ef…` 历史口径）；跨语言复算需对齐 `json.dumps` 数字序列化。
2. 未知字段是"丢弃 + 告警"，不阻断运行。
3. `measured` 只证明来源存在，不核验外部真实性。
4. `verdict_hash` 与 commit 绑定，提交后旧哈希失效属预期。
5. 热插拔检查为单包抽样（`optimization` 40→47），未逐包回归。

---

## 9. 下一步

VERAX 是"证据出口"，NEPHRON P0 认知账本是"证据来源"。账本落地后可让 `repro_summary` 挂到具体 tick，实现任意 tick 回放。不做第 17 个领域包，不为 star 抄编排框架。

---

## 10. 红线（不变）

零网络、零密钥、零遥测；不开端口、不常驻、无 cron；不 pip/npm；不读 `.env`；不替用户决策。
所有回执默认 `simulated`：**仿真 ≠ 证明**，碳基终裁。

许可证 Apache-2.0 · Python 3.8+ · 仅标准库。

---

## 二、VERAX 设计说明（字段表 / 分级 / 门禁 / 限制）

## VERAX · 可复现性与诚实契约横切子系统（设计说明）

> 适用版本：HoloAeon v0.9.1（`HOLOAEON-RUNTIME-0.9.1`）
> 定位：**只读观测层**。不新增领域包、不新增 agent、不改 C1–C12 对外行为。
> 全部条目默认 `evidence_class = simulated`：**仿真 ≠ 证明**，碳基终裁。

---

## 一、它解决什么（三条历史坑，正面解决而非圆场）

| 编号 | 历史坑 | 现象 | VERAX 的处理 |
|---|---|---|---|
| P1 | 整包哈希含 `ts` | 同一任务两次跑哈希不同，被读成"不确定" | 字段分类表把 `ts/elapsed/thread_order/pid…` 划为 Physical 剔除；规范化后 `word_count` 稳定为 `2b82a6ef7188ce91` |
| P2 | `python -m holoaeon.selftest` 静默退出 0 | 没跑也被当成"已通过" | `selftest.main()` + `__main__`，真跑真打印，失败返回 1 |
| P3 | `simulated` 与"真实生效"混写 | 回执可信度不可判定 | 强制 `evidence_class ∈ {simulated, measured, third_party}`；measured 无来源即 H1 |

**它保护哪条立身原则**：确定性（P1）、可审计（P2）、诚实纪律（P3）。

---

## 二、与 C1–C12 的接入点清单（全部只读，无侵入）

| 接入点 | 方式 | 读什么 | 写什么 |
|---|---|---|---|
| `kernel.submit()` 回执 | 返回值观测 | `results[].status / matched / output`、`targets`、`all_ok` | 不写内核 |
| `guard.Verdict.to_dict()` | 返回值观测 | `action / layer / reason` | 不写守卫 |
| `selftest.run_all()` | 函数调用 | `details[]` → G1–G24 逐项 | 不写自检 |
| `redline.scan_directory()` | 函数调用 | `files_scanned / violations` | 不写源码 |
| `packs.get_pack().install()` | 运行时热插拔 | 技能数前后差 | 只加技能，不改既有 |
| `.git/HEAD` + ref 文件 | 直接读文件 | commit 短哈希 | 不调 git 进程 |

零 `subprocess`、零 `socket`、零第三方依赖；红线扫描口径内 0 违规。

---

## 三、字段分类表（FieldClass）

| 类别 | 键集合 | 处理 |
|---|---|---|
| Physical | `ts, timestamp, elapsed, duration, started_at, finished_at, thread_order, addr, pid, uptime_s, measure_ts, id_instance` | 剔除，不进 ReproHash；单独快照进 `physical` 供展示 |
| ReproCore | `runtime_id, task, targets, results, all_ok, agent_id, role, input, status, matched, err, verdict, action, layer, reason(reason_code/reasons), summary, message_id, trace, skill, count, files_scanned, violations, clean` + 自证 schema（`gid, name, conclusion, checks, repro, honesty, redline, verdict_hash, reprohash_list, golden_match, repro_hash_stable, evidence_class, unknown_fields, diff_physical, diff_reprocore`） | 递归保留，参与 ReproHash |
| Opaque | `output, payload, evidence, reprocore, physical` | 内部结构由技能自声明，原样序列化 |
| Unknown | 未登记键 | **丢弃 + 记 `unknown_field` 路径告警**（不静默） |

**为什么自证 schema 也必须登记**：首轮实现漏登记 `conclusion / checks / repro / honesty / redline`，导致三色用例的 `verdict_hash` 完全相同 —— 规范化把结论字段当物理量剔了，哈希失去区分度。这正是 A3 要防的"静默丢弃"，已在代码与本文档同时修正。

---

## 四、证据分级规则表

| 分级 | 语义 | 强制字段 | 不合规判定 |
|---|---|---|---|
| `simulated` | 确定性引擎/技能产出的仿真结果 | 无 | 携带 `measure_source` → H2（黄） |
| `measured` | 在本机真实跑过并记录了来源与时刻 | `measure_source` + `measure_ts` 均必填 | 缺任一 → H1（红） |
| `third_party` | 外部来源（他人报告/公开基准） | 同 measured，另需可核验引用 | 缺任一 → H1（红） |

红线两条：
- **H1（红）**：`measured/third_party` 缺来源或时刻。
- **H2（黄）**：回执缺 `evidence_class` 字段，或非 measured 却携带来源。

一条不合规回执记 **一条** H1（缺几个字段在 detail 里合并说明），避免一份回执被计成多条。

---

## 五、算法（四步，逐条可实现）

1. `classify(key)` → physical / repro / unknown（查表，不做启发式猜测）。
2. `canonicalize(obj)`：递归剔除 physical；`list[dict]` **先按规范文本稳定排序再递归**（解掉集群/线程完成序不可复现）；float 处理 `NaN / ±Infinity / -0.0`；enum 取 value；`None → null`。
3. `canonical_json`：`json.dumps(ensure_ascii=False, sort_keys=True, default=str)` —— 键升序、无空白。
4. `reprohash = sha256(canonical_json)[:16]`。

**口径说明（不转定点字符串的理由）**：既有黄金值 `2b82a6ef7188ce91` 由同一套 `json.dumps` 数值序列化产生；改成定点字符串会与历史口径漂移，反而破坏 A1 的对比基准。浮点等值在本框架内由技能自身定点（如 `0.816`、`5.7752`），规范化层只保证"同值必同串"。

---

## 六、黄金任务集（冻结于 `holoaeon/audit/golden/*.json`）

| task_id | 任务输入 | 命中技能 | 期望 ReproHash | 期望输出/判定 |
|---|---|---|---|---|
| `word_count` | `统计字数：HoloAeon 是零依赖的确定性多智能体认知框架。` | `word_count` | `2b82a6ef7188ce91` | `chinese_chars 20 / english_words 1 / total_chars 31 / sentences 1` |
| `data_describe` | `统计分析`，`csv_text="x\n1\n2\n3"` | `basic_stats` | `3352db0f803eb727` | `count 3 / mean 2.0 / std 0.816 / min 1.0 / max 3.0` |
| `quant_sharpe` | `sharpe`，`returns_s="0.01,-0.02,0.03,0.01"` | `sharpe` | `2c9e5d7d01526ce8` | `{"sharpe": 5.7752}` |
| `guard_os_system` | `执行 os.system('ls -la') 并返回输出` | — | `a7deb622e17a2b55` | `status=blocked`（L3 拦截） |
| `guard_eval` | `计算 eval(1+1) 的结果` | — | `98b9b7b340f7f980` | `status=blocked`（L3 拦截） |

改动 golden 必须走评审（PR 标题带 `[golden]`）。五项在 `--n 2` 下 `stable=True / golden_match=True`。

---

## 七、门禁（`scripts/verax_verify.py`）

顺序：**红线 → 自检 → 复现基准 → 诚实契约 → 热插拔 → 汇总 Attestation**。

| 退出码 | 含义 | 触发条件 |
|---|---|---|
| `0` | 绿 | 红线 0 违规 + 自检 24/24 + 5 基准全 stable 且 golden 命中 + H1=H2=0 |
| `1` | 红 | 任一检查 fail / 任一基准不稳定或 golden 不命中 / 红线违规 |
| `2` | 黄 | 仅诚实告警（H1 或 H2 命中） |

三色实测（本轮真实跑出，不是示意）：

```
green  -> conclusion=green  verdict_hash=ec516f4ed413b5af  VERAX_EXIT=0
yellow -> conclusion=yellow verdict_hash=259eed7b72bdbb49  VERAX_EXIT=2   （注入一条无来源 measured）
red    -> conclusion=red    verdict_hash=5bfa825fb948819e  VERAX_EXIT=1   （篡改 word_count 黄金值）
```

`reports/attestation.jsonl` 连跑两次 SHA-256 一致（`AAAE988C24B509D5469BF4432383581A…`），即 A6。

---

## 八、自证报告样例

`reports/attestation.md`（人读，ASCII 回执美学）：

```
========================================================================
HoloAeon VERAX 自证报告（Self-Attestation）
========================================================================
runtime_id : HOLOAEON-RUNTIME-0.9.1
commit     : b660cb193700
ts_build   : 2026-10-31T10:55:06Z   （物理量，不进 verdict_hash）
verdict    : GREEN
verdict_hash : ec516f4ed413b5af
证据分级   : 本报告全部条目默认 simulated；仿真≠证明。
```

`reports/attestation.jsonl`（机器读，逐行一条 CheckResult，键序稳定）：

```json
{"evidence": {"detail": "config=True, design_grid=1771561"}, "evidence_class": "simulated", "gid": "G1", "name": "G1 spec", "status": "pass"}
{"evidence": {"verdict_hash": "ec516f4ed413b5af"}, "evidence_class": "simulated", "gid": "VERDICT", "name": "self-attestation verdict", "status": "green"}
```

`verdict_hash` 由 `runtime_id / commit / conclusion / checks / repro / honesty / redline / unknown_fields` 规范化生成，**不含 `ts_build`**，因此同代码同结论必同哈希；commit 变更后哈希随之改变属预期。

---

## 九、测试与实测结果（真实跑出）

| 项目 | 命令 | 结果 |
|---|---|---|
| 既有单测 | `python -m unittest discover -s tests` | `Ran 34 tests / OK`（未变） |
| VERAX 单测 | `python -m unittest discover -s tests\verax` | `Ran 16 tests / OK` |
| 自检 | `python scripts\launch_local.py selftest` | `==> 24/24` |
| 自检直接入口 | `python -m holoaeon.selftest` | 打印 G1–G24 明细，`==> 24/24`，退出码 0（P2 已修） |
| 红线 | `python scripts\redline_scan.py` | 扫描 40 文件 / 0 违规 |
| 红线+诚实 | `python scripts\redline_scan.py --receipts=reports\_cases\yellow` | H1=1 → 退出码 1 |
| 本地融合 | `python scripts\launch_local.py demo` | 总线 25 地址 / 低成本→local / 长上下文→cloud / `all_ok=True` |
| 热插拔 | `python scripts\launch_local.py hotplug optimization` | `40 → 47（新增 7，全程未重启）` |

规模（实测）：`holoaeon/` 40 个 py / 11,408 行；其中核心 16 文件 3,851 行、`packs/` 18 文件 6,872 行、`audit/` 6 文件 685 行。

---

## 十、已知限制（不藏）

1. **数值未转定点字符串**：理由见第五节；跨语言复算需自行对齐 `json.dumps` 的数字序列化。
2. **未知字段是"丢弃 + 告警"**：告警进报告，不进哈希；不阻断运行。
3. **measured 只证明"来源存在"**：VERAX 不核验外部真实性，也不联网取证。
4. **不改行为**：不修复任何业务技能的正确性，只观测。
5. **verdict_hash 与 commit 绑定**：代码提交后旧哈希失效属预期，请以当次报告为准。
6. **口径变化**：红线扫描文件数由 34 增至 40（新增 `audit/` 6 个模块），"零违规"不变；`tests/` 顶层仍 34 项。
7. **热插拔检查是单包抽样**（`optimization` 40→47），未逐包回归。

---

## 十一、隐私与安全

- 默认不存用户原文；只存任务摘要与 ReproHash。
- trace 只记调用指纹与字节数，不记请求体明文。
- 导出目录最小化：`reports/` 与 `reports/_cases/` 分开，`_cases` 不参与正式扫描。
- 一键擦除：删 `reports/` 即清空回执；计数与哈希可通过重跑再生。

---

## 十二、下一步（承接 NEPHRON P0）

VERAX 给出了"证据出口"，账本给出"证据来源"：NEPHRON P0 认知账本落地后，`repro_summary` 可挂到具体 tick 记录，实现"任意 tick 可回放"。在此之前不做第 17 个领域包。

---

## 三、面向智能体的一键复制投喂包

## 面向智能体 · 一键复制投喂包（VERAX 冷热插拔赋能版）

> 唯一 ID：SG-HOLOAEON-VERAX-20261031-V1.0
> 矩阵规格：冷热插拔赋能升级思维模式（SG-ENGINE-COLD-HOT-PLUG-V1.0）实例化
> 封存密令：潮起开门（激活）/ 潮落闭嘴（休眠）
> 产出维度不变：25 智能体 / 47 技能 / 9 领域包 + 7 扩展包 / 34 单测 / 24 自检 / 红线零违规 / 零依赖 / 离线 / 确定性
> 用法：整段复制给任意实现智能体，它可在无额外上下文的情况下复刻或验收本升级。

---

## 一、你的角色与边界

你是 HoloAeon（通用多智能体认知框架，零依赖·离线·确定性）的实现智能体。任务是在不改动既有能力的前提下，为其加一层可信横切子系统（代号 VERAX）：把"确定性 / 安全边界 / 诚实纪律"从内部工程习惯，变成可复算、可出示的证据产物。

硬边界：

- 不新增领域包、不新增 agent、不新增业务技能（维度不变是硬约束，不是建议）。
- 不引入任何第三方依赖；不联网、不开端口、不常驻、不读 .env；核心包 dependencies = [] 不得破坏。
- 不改 C1–C12 对外行为；VERAX 只读观测 + 规范化重算。
- 不破坏 G1–G24 全绿与 tests/ 34 项全绿。
- 不把 simulated 写成"实测"。

---

## 二、项目基线（自包含事实，可直接施工）

- 运行时：HOLOAEON-RUNTIME-0.9.1；许可证 Apache-2.0；Python 3.8+；零第三方依赖。
- 12 个正交原语：envelope / bus / agent / skill / memory / scheduler / guard / kernel / graph / cluster / hypervector / model_adapter。
- 16 个包：9 领域（writing / literature / research / data / growth / business / quant / optimization / gaoyi）+ 7 横切（sovereignty / subdistill / omnilife / omnicore / metab / nephron / uplift）。
- 九域装齐 = 25 agent / 47 skills / 9 workflows；全装 = 191 skills / 55 workflows / 25 agent。
- 既有入口：scripts/launch_local.py {status|demo|run|hotplug|selftest}、python -m unittest discover -s tests、scripts/redline_scan.py。
- 三处历史坑（必须正面解决）：
  1. 整包哈希含 ts → 朴素比对得"假不确定"；
  2. python -m holoaeon.selftest 无 __main__，静默退出 0；
  3. 回执中 simulated 与"真实生效"未强制区分。

---

## 三、冷热插拔五步协议（每一步都可执行、可回滚）

| 步 | 动作 | 本项目的落点 | 完成判据 |
|---|---|---|---|
| 1 解锁 | 只读盘点现状，不写任何文件 | launch_local.py status / selftest / redline_scan.py / unittest discover -s tests | 拿到 24/24、34 OK、0 违规三项基线 |
| 2 旁挂 | 新增 holoaeon/audit/ 与 scripts/verax_verify.py，主核一行不改 | 目录新增，不改既有 16 个核心模块的对外行为 | 旁挂后既有三项基线不变 |
| 3 联调压测 | 规范化口径联调 + 基准冻结 + 三色用例 | scripts/_freeze_golden.py 冻结 5 个基准；--case green/yellow/red | word_count 稳定 2b82a6ef7188ce91；退出码 0/2/1 各自可复现 |
| 4 巡检上线 | 门禁合成 + 自证报告 + 接入 CI | python scripts/verax_verify.py 出 reports/attestation.md + attestation.jsonl | VERAX_EXIT=0；jsonl 连跑两次哈希一致 |
| 5 一键回滚 | 删旁挂即复原 | 删 holoaeon/audit/、scripts/verax_verify.py、tests/verax/、reports/ | 既有 34 单测 / 24 自检 / 0 违规不受影响 |

---

## 四、要实现的规格（逐条可判定）

### 4.1 字段分类表（集中声明，新增字段必须登记）

| 类别 | 键 | 处理 |
|---|---|---|
| Physical | ts, timestamp, elapsed, duration, started_at, finished_at, thread_order, addr, pid, uptime_s, measure_ts, id_instance | 剔除，不进 ReproHash |
| ReproCore | status, all_ok, matched, targets, output.*, route.*, guard.*, agent_id, evidence_class 等裁决类字段 | 保留，参与哈希 |
| Opaque | output, payload, evidence, reprocore, physical | 原样序列化 |
| Unknown | 未登记键 | 丢弃并以 unknown_field 路径告警，不静默 |

自证报告自身的 schema（conclusion / checks / repro / honesty / redline / gid / name / verdict_hash）也必须登记，否则会被当物理量剔除、导致哈希失去区分度。

### 4.2 算法

canonicalize：递归剔 Physical；list[dict] 先按规范文本稳定排序再递归（解线程完成序）；处理 NaN / ±Inf / -0.0；None → null；键升序无空白 JSON。

reprohash = sha256(canonical_json)[:16]（与既有 2b82a6ef… 同口径，不要改成定点字符串，否则基准漂移）。

### 4.3 数据结构

- Receipt{receipt_id, source_path, evidence_class ∈ {simulated, measured, third_party}, measure_source, measure_ts, reprocore, physical}
- ReproVerdict{task_id, runs, reprohash_list, repro_hash_stable, golden_match, diff_physical, diff_reprocore}
- CheckResult{gid, name, status ∈ {pass, fail, skip}, evidence, evidence_class}
- Attestation{runtime_id, commit, ts_build, checks, repro_summary, honesty_summary, redline, verdict_hash, conclusion ∈ {green, yellow, red}, unknown_fields}

verdict_hash 只取结论字段（不含 ts_build），同代码同结论必同哈希。

### 4.4 黄金集（冻结在 audit/golden/*.json，改动须 PR 标题带 [golden]）

| task_id | 期望 ReproHash | 期望结果 |
|---|---|---|
| word_count | 2b82a6ef7188ce91 | 中文字 20 / 英文词 1 / 总字符 31 / 句 1 |
| data_describe | 3352db0f803eb727 | count 3 · mean 2.0 · std 0.816 |
| quant_sharpe | 2c9e5d7d01526ce8 | sharpe 5.7752 |
| guard_os_system | a7deb622e17a2b55 | blocked · L3 |
| guard_eval | 98b9b7b340f7f980 | blocked · L3 |
| hotplug_opt（独立检查） | — | 技能 40 → 47，未重启 |

### 4.5 诚实规则

- 所有 VERAX 产出默认 simulated。
- measured 缺 measure_source / measure_ts → 记 H1（红）；一条不合规回执只记一条 H1（缺项合并进 detail）。
- 回执缺 evidence_class → H2（黄）。
- 修 selftest 静默坑：补 main() + __main__，失败返回非零。

### 4.6 门禁（scripts/verax_verify.py）

顺序：红线（含 H1/H2）→ 自检 → 复现基准 → 诚实契约 → 热插拔 → 汇总 Attestation。

| 退出码 | 含义 |
|---|---|
| 0 | 绿 |
| 1 | 红（检查失败 / 基准不一致 / 红线违规） |
| 2 | 黄（仅诚实告警） |

报告双导出：reports/attestation.md（人读 ASCII 回执）+ reports/attestation.jsonl（逐行一条 CheckResult，键序稳定）。

---

## 五、验收（A1–A10，本轮全部实测通过）

| 项 | 判据 | 实测 |
|---|---|---|
| A1 | word_count 两次 ReproHash 稳定 2b82a6ef7188ce91，golden_match=True | 通过 |
| A2 | 逻辑等价、物理量不同的两份回执规范化后逐字节一致（含 list[dict] 乱序） | 通过（test_canonicalize） |
| A3 | 未登记字段被丢弃并计入 unknown_field，不静默 | 通过（首轮三色哈希相同即此缺陷，已修） |
| A4 | 无来源 measured → 至少黄灯，H1/H2 计数 | 通过（--case yellow → 退出码 2） |
| A5 | 开启 VERAX 不改变 G1–G24 与 34 单测 | 通过（24/24、34 OK） |
| A6 | attestation.jsonl 连跑两次哈希一致 | 通过（SHA-256 相同） |
| A7 | 退出码可被 CI 消费（绿/黄/红三例） | 通过（0 / 2 / 1，三色 verdict_hash 各不相同） |
| A8 | 红线新增 H1/H2 且 import 层零网络、dependencies=[] 不破 | 通过（40 文件 0 违规） |
| A9 | 修复 selftest 空打印 | 通过（python -m holoaeon.selftest 打印 24/24） |
| A10 | 文档完备（字段表 / 分级规则 / 退出码 / 报告样例） | docs/VERAX.md |

真实结果：

```
自检         ==> 24/24
tests/       Ran 34 tests / OK
tests/verax/ Ran 16 tests / OK
红线         扫描文件数 40 / 结果 干净（零违规）
门禁 green   conclusion=green  verdict_hash=ec516f4ed413b5af  VERAX_EXIT=0
门禁 yellow  conclusion=yellow verdict_hash=259eed7b72bdbb49  VERAX_EXIT=2
门禁 red     conclusion=red    verdict_hash=5bfa825fb948819e  VERAX_EXIT=1
热插拔       40 → 47（新增 7，全程未重启）
本地融合     总线 25 地址 / 低成本→local / 长上下文→cloud / all_ok=True
```

---

## 六、禁止项（违反即失败）

1. 不加第 17 个领域包，不新增 agent/业务技能。
2. 不为追 star 抄编排框架；不引入非确定性来源。
3. 不把 simulated 写成实测。
4. 不破坏 dependencies=[]、不引网络、不破 G1–G24 与 34 单测。
5. 不在核心包散布记录代码（观测一律走只读 hook / CLI）。
6. 不把 golden 随手改；改动必须走评审。

---

## 七、输出格式与交付物

Markdown；结构化内容用表格；生物隐喻仅限既有词。每条规范性陈述应可判定，并补一句"它保护了哪条立身原则"。

交付 7 项：

1. 设计说明 + 与 C1–C12 的接入点清单（只读 hook/CLI）
2. 字段分类表 + 证据分级规则表
3. 复现验证器 + 黄金集 + golden 冻结文件
4. 自证报告 md/jsonl 样例（必须含 2b82a6ef…）
5. verax_verify.py + 三色用例
6. 测试清单与真实结果（禁止把 simulated 写成实测）
7. 已知限制与下一步（承接 NEPHRON P0 认知账本）

---

## 八、隐私与安全

默认不存用户原文，只存任务摘要与哈希；trace 只记调用指纹与字节数，不记请求体；导出目录最小化（reports/ 与 reports/_cases/ 分开，_cases 不进正式扫描）；一键擦除 = 删 reports/。

---

## 九、一句话交付口径

VERAX 把 HoloAeon 最强的东西——可验证的确定性 + 诚实契约——从三处隐藏坑，修成一个别人抄不走、30 秒能复现、能挂 CI 徽章的证据资产。先做 VERAX，再推 NEPHRON P0 补治理的数据底座。

潮起开门，潮落闭嘴。

---

