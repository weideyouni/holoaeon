# 面向智能体的一键复制投喂包 · HoloAeon V2 升级已落地交接（2026-11-01）

用法：整段复制给任意实现智能体。自包含。读完即可接手，不需要先读全部源码。

**你的身份**：HoloAeon 的接手智能体。
**项目当前状态**：V1（0.9.1）+ V2 赋能升级五包 **全部落地并实测**（文档版 0.9.2）。
**硬口径**：25 智能体 / 47 技能 / 9 领域包 + ≥7 扩展包（现 8）/ 34 单测 / 25 自检 / 12 原语 C1–C12 不动。
**密令**：潮起开门，潮落闭嘴。
**证据分级**：默认 `simulated`；`measured` 必须带 source + ts；`third_party` 必须可核验。仿真 ≠ 证明，碳基终裁。

---

## 0 你接手的现实（2026-11-01 本机实测，非"应该会"）

| 项 | 值 | 出处 |
|---|---|---|
| 运行态版本 | `0.9.1`（`spec.py VERSION` 权威，不许改） | `holoaeon/spec.py` |
| 文档版本 | `0.9.2`（`DOC_VERSION`，只用于升级包与文档） | 同上 |
| 智能体 / 技能 / 工作流 | 25 / 47 / 9 | `packs/__init__.py` |
| 领域包 / 扩展包 | 9 / 8 | `PACK_ORDER` / `EXTRA_PACK_ORDER` |
| 单测（三套分开跑） | 34 / 21 / 5 全 OK | `tests`、`tests\verax`、`tests\v3` |
| 自检组 | 25/25（`G25 persona_quartet — 8/8`） | `launch_local.py selftest` |
| 门禁 | `VERAX_EXIT=0`，`conclusion=green`，`verdict_hash=f2fb0236c8bbd721` | `verax_verify.py --mutate 5` |
| DIFF=0 | `2fc892cf9af6e755`（篡改 → `f42c8229ee5acd73`，sensitive=True） | `bench_public.py` |
| 守卫 | 16/16 拦截 + 4/4 放行 | 同上 |
| 足迹 | ≈31.7ms / 1.69MiB（物理量，不进哈希） | 同上 |
| 证据链 | `reports/repro_core.jsonl` **10 行（9 pass + 1 info）**，`--check` 10 行一致 | `repro_core_emit.py` |
| 语义通道 | 12 意图 / 词表 334 / 维 32 / 混合 11/12 = 91.7% | `bench_semvec.py` |
| 分层留出 | 5 折 mean=0.9957 / std=0.0085（限 0.05）；跨词汇锚点 11/12 | `bench_semvec_kfold.py` |
| 代码量 | `holoaeon/` 44 文件 / 12200 行（**代码量不是维度，允许增长**） | `snapshot/project_snapshot_v2.json` |
| 快照 | `snapshot/SNAPSHOT_V2.md` + `snapshot/project_snapshot_v2.json` | 本仓库 |

**黄金值（不许漂移）**：DIFF=0 `2fc892cf9af6e755`；word_count `2b82a6ef7188ce91`；
账本 sha `98940b774566543b`（5,860 B / 6 记录）；semvec digest `789b71a36bfcd66a`。
另 4 条 golden：`data_describe=3352db0f803eb727`、`guard_eval=98b9b7b340f7f980`、
`guard_os_system=a7deb622e17a2b55`、`quant_sharpe=2c9e5d7d01526ce8`。

---

## 1 V2 五个工作包（全部旁挂，内核 0 改动）

| 包 | 名称 | 归因分身 | 落点 | 维度影响 |
|---|---|---|---|---|
| W7 | 自动篡改自检 | 探微 | `holoaeon/audit/mutation.py` + `tests/verax/test_mutation_selftest.py`(5 用例) + `--mutate N` | 单测 34 不变（verax 16→21） |
| W8 | semvec 分层留出集 | 筑基 | `scripts/bench_semvec_kfold.py` + `scripts/build_semvec_corpus_v2.py` + `data/semvec_corpus_v2.json`(235) + `benchmarks/results-semvec-kfold-0.9.2.json` | 旁挂脚本，0 |
| W9 | REPRO_CORE 证据协议 | 构弦 | `scripts/repro_core_emit.py` + `docs/spec-diff0-v0.2.md §7` + `reports/repro_core.jsonl` | 0 |
| W10 | fail-loud 协议 | 持衡 | `holoaeon/audit/verdict_policy.py`（不挂内核）+ `docs/spec-diff0-v0.2.md §8` | 0 |
| W11 | V2 快照 | 综合 | `scripts/snapshot_v2.py` + `snapshot/SNAPSHOT_V2.md` + `snapshot/project_snapshot_v2.json` | 0 |

### 1.1 W7 要点

`leaf_paths()` 取**规范对象**全部标量叶子；`mutate_value()` 按类型确定性改（bool 取反 /
int+1 / float+0.001 / str 追加 `·` / None→`<mutated:null>`）；`mutate_selftest(obj, n=5,
seed=20261101)` 抽样逐点比对 reprohash，返回 `mutations/changed/sensitive/base_hash/details`；
**`n=0` 时 `sensitive=False`（空转保护）**。
必须只篡规范叶子——篡到 `canonicalize` 剔除的物理量，会得到"改了哈希不变"的假阴性。

### 1.2 W8 要点

47 条技能基准 × 5 个问法层（原句 / "帮我…" / "能不能…？" / "请执行：…" / 后缀"给出结果"）
= 235 条，`corpus_sha=db56e107aa1f0fa6`。每折在留出层上报 P@1，输出 `mean/std`（总体标准差），
std ≤0.05 绿、>0.05 黄。**另加跨词汇锚点**（V1 12 条改写意图）对冲"术语同形导致虚高"：
锚点 11/12 = 91.7%，未提升也未调参。
已知未命中两条：`拆解一下这个任务`、`设计实验的样本量`（后者误判 `design_experiment`）。

### 1.3 W9 要点

行级哈希：`sha256(规范化去掉 measure_ts 与 verdict_hash 后的整行)[:16]`。
10 行固定口径：`diff0_hash / mutation_sensitivity_v1 / guard_block / guard_allow /
word_count_golden / ledger_sha / semvec_digest_v1 / mutation_selftest_v2 / semvec_kfold_std /
footprint(info)`。`--check` 逐行复算，任一行不一致退出 1。
**不得并入 `attestation.jsonl`**（R-2 并存不合并）。
物理量（`build_ms`）只打印不落行——落行必致 `--check` 失败。

### 1.4 W10 要点

`POLICY_ID=HOLOAEON-VERDICT-POLICY-v0.2`，`RULE_IDS=(diff0_drift, mutation_insensitive,
golden_unfrozen)`；`evaluate()` 命中任一即 `conclusion=red, downgradable=False`；
`enforce()` 只许"变红"；`assert_no_downgrade()` 在调用方想写非 red 时抛 `ValueError`。
门禁第 7 步 `[7/7] 策略` 落地，命中即 `VERAX_EXIT=1`（**不是 2**）。

### 1.5 W11 要点

`scripts/snapshot_v2.py` 只读现算：维度 / 代码量 / 三指标 / semvec / kfold / 证据行与哈希 /
黄金值 / 不变量 / 已知限制 / 入口命令 / 不做清单 → 一份 json + 一页 md。

---

## 2 照抄可跑（本机已验证）

```powershell
Set-Location F:\doubaowork\holoaeon

# 基线三闸（必须分开跑）
python -m unittest discover -s tests
python -m unittest discover -s tests\verax
python -m unittest discover -s tests\v3
python scripts\launch_local.py selftest

# V2 四步
python scripts\verax_verify.py --mutate 5
python scripts\bench_semvec_kfold.py --folds 5
python scripts\repro_core_emit.py --out reports\repro_core.jsonl
python scripts\repro_core_emit.py --check reports\repro_core.jsonl

# 一键串链（内部融合 + 外部融合 + 四包）
python scripts\launch_local.py v2
python scripts\launch_local.py demo

# 红旗用例（A4：退出码必须是 1）
python scripts\verax_verify.py --case red

# 快照
python scripts\snapshot_v2.py

# 直传 Gitee（读 C:\Users\Administrator\.gitee_token）
python scripts\gitee_publish.py --repo F:\doubaowork\holoaeon --branch main
```

---

## 3 验收判据（A1–A9，当前状态）

| 判据 | 要求 | 状态 |
|---|---|---|
| A1 | 三闸全绿（34 / 21 / 5 + 25/25 + 红线 0 违规） | 通过 2026-11-01 实测 |
| A2 | DIFF=0 = `2fc892cf9af6e755`，mutation_sensitive=True | 通过 |
| A3 | 守卫 16/16 + 4/4 | 通过 |
| A4 | `VERAX_EXIT=0`；人为构造漂移 → 退出码 1（不许 2） | 通过（`--case red` 实跑，hits=['diff0_drift']） |
| A5 | `--mutate 5` 五点全变 | 通过（`changed=5 sensitive=True`） |
| A6 | kfold 5 折跑通，mean/std，std ≤0.05 | 通过（0.9957 / 0.0085） |
| A7 | 证据 ≥6 行、四字段非空、`--check` 可复现 | 通过（10 行全一致） |
| A8 | `dependencies=[]` 未破、无新增依赖、V1 golden 全留 | 通过 |
| A9 | 新增数字均有出处 | 通过 |

---

## 4 不做的清单（与 V1 一致 + V2 新增）

- 不新增第 18 个扩展包去锁上界；每个新扩展包必须自带专属测试。
- 不调参把 semvec 11/12 刷成 12/12。
- 不改三本 cookbook 与 V1 文档已发布实测数字；V2 只能新增章节。
- 不用 advice 把 red 降成 yellow。
- 不为数字漂亮把 golden 改成"自适应"；新 golden 必须标 `[golden-vN]` 并写评审时间。
- 不改 `VERSION`/`RUNTIME_ID`（会连带 DIFF=0 与 5 条 golden 一起漂移）。

---

## 5 已知坑（V1 + V2 新增）

| 编号 | 现象 | 处理 |
|---|---|---|
| V1-1 | `python -m holoaeon.selftest` 早期无 `__main__` | 用 `launch_local.py selftest` |
| V1-2 | 三套 discover 合并会破 34 项口径 | `tests` / `tests\verax` / `tests\v3` 分开跑 |
| V1-3 | `get_pack("sovereignty")` KeyError | 扩展包走 `get_extra_pack` |
| V2-1 | `EXTRA_PACK_ORDER` 7→8 打破 `== 7` 断言 | 已改 `>= 7`，不许改回精确等值 |
| V2-2 | `persona_quartet` 化名 P1–P4 与原版分身目录并存 | 化名版进 packs，原版在 `F:\矩阵目录`；调用用 P1–P4 |
| V2-3 | 新证据链与 `attestation.jsonl` 混淆 | 两个文件并存，各自校验，不合并 |
| V2-4 | 语料 47→235 后 semvec digest 必漂 | v1 digest 标 `[golden-v1]` 锁死，v2 另标 `[golden-v2]` 并存 |
| V2-5 | 篡改落在物理量上 → 假阴性"改了哈希不变" | 只篡 `canonicalize` 后的规范叶子 |
| V2-6 | 物理量写进被哈希字段 → `--check` 必失败 | 物理量只打印不落行 |
| V2-7 | 新证据文件被旧"诚实校验"扫成黄灯（`simulated` 带 `measure_source` 被判违规） | 按 schema 分流：同时含 `evidence/verdict_hash/golden_value` 的行算证据行，只计数不套回执规则 |
| V2-8 | `--mutate 0` 时若仍断言 sensitive，会假装通过 | `n=0` 返回 `sensitive=False`，门禁按"未评估"披露 |
| V2-9 | 快照里写 `time.gmtime()` → 两次现算字节不同，W11"回放一致"判据永远不成立 | `generated_at` 固定为常量（`HOLOAEON_SNAPSHOT_TS` 可覆盖）；两次现算 sha256 实测一致 `E06FACA61265293D` |
| V2-10 | PowerShell 里 `Set-Location` 后用 .NET `ReadAllText("README.md")`：读走进程 CWD、写走 PS 路径，把 A 仓库 README 覆盖到 B 仓库 | 读写一律绝对路径 + `Get-Content -Raw` / `[IO.File]::WriteAllText`；误覆盖用 `git checkout -- <file>` 恢复 |

---

## 6 你要交的东西

1. 五包可跑代码 + 每步**实测 stdout**（不许写"应该会"）。
2. `snapshot/SNAPSHOT_V2.md`：维度、三指标、V2 四行、不变量、已知限制。
3. 同名 README 的第二屏 V2 增量徽章（mutate / kfold / repro_core / fail-loud），**不替换 V1 三数字**。
4. 本投喂包的更新版（补 §5 新坑）。
5. 一份诚实清单：做了 / 没做 / 为什么，含 kfold 方差值（方差是泛化的指纹，不许藏）。

---

## 7 立场（写进报告，不要只写代码）

V1 完成了「确定性 + 诚实」的可证据化。V2 做的是「证明对证据本身负责」：
不让任何人靠静默黄灯逃避对齐失败，不让语义指标靠过拟合装样子，
不让证据链靠手抄 README 漂移。

确定性声称本身就是一种对齐声称。让协议把这条锁死——这是 V2 的全部意义。

投喂结束。潮起开门，潮落闭嘴。
