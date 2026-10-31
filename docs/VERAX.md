# VERAX · 可复现性与诚实契约横切子系统（设计说明）

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
