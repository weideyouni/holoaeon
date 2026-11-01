---
name: holoaeon-v3-langchain-form
description: "HoloAeon V3 的『LangChain 工程形态借鉴』旁挂范式（SG-UPGRADE-HOLOAEON-V3-20261101）。当你要接手/校验/继续推进 HoloAeon V3——跑 32 项 V3 门禁、检查维度不变（25 智能体/47 技能/9 领域包/34·21·5 单测/25 自检）、确认 DIFF=0 黄金未漂、验证 runnable/span_tree/schema/eval_set/interrupt/渐进加载/replay/事件流/桥 conformance 八包是否可跑，或要把同一套『统一协议 + 横切钩子 + 可恢复暂停 + 数据集化评测 + 薄适配器』搬到别的确定性项目时使用。触发词：HoloAeon V3、V3 门禁、v3_gate、launch_v3、eval_47、LangChain 工程形态、维度不变、旁挂升级。"
---

# HoloAeon V3 旁挂范式（LangChain 工程形态）

> 用途：把 LangChain 1.x / LangGraph / LangSmith 的**工程形态**（不是成本结构）落到一个
> 已冻结维度的确定性项目上：25 智能体 / 47 技能 / 9 领域包 + 8 扩展包 / 34·21·5 单测 / 25 自检，
> 一个数字都不许动。新增能力全部**旁挂**：新模块不挂内核、新断言不进主套、新证据独立成行。
> 密令：潮起开门，潮落闭嘴。全部结论 `evidence_class=simulated`：仿真 ≠ 证明，碳基终裁。

## 一 什么时候用

- 要**接手** HoloAeon V3：先跑门禁，再读快照，不要先读源码。
- 要**改** V3 的任一包：先读对应文件现状，再改，改完必跑 `v3_gate`。
- 要把这套范式**移植**到另一个"维度已冻结"的项目：照五段式 + 下方铁律做。

不适用：从零设计一个多智能体框架；要引入第三方依赖的集成；要改黄金值本身的场景。

## 二 五段式（V2 范式在 V3 上的具体投影）

| 段 | V2 说法 | V3 落点 | 判据 |
|---|---|---|---|
| 探微 | 自检生成反例 | `span_tree` 结构哈希 + `v3_gate` 反例（改结构哈希必变、改耗时不变） | A5.1 / A5.2 |
| 筑基 | 指标从点到区间 | `eval_47` + 双轨 diff（`raw` vs 对抗变体 `cross`） | A7.1–A7.3 |
| 构弦 | 证据统一成行级可哈希 | `repro_core.jsonl` 仍 10 行；V3 新增门禁开 `reports/v3_gate.json` | A13 |
| 持衡 | fail-loud 不可降级 | `interrupt` 令牌 + `schema` 显式报错 + 既有三条红线 | A6 / A8 |
| 综合 | 快照 + 投喂包 | `snapshot/SNAPSHOT_V3.md` + `AGENT_FEED_V3_DONE_20261101.md` | 现算、可回放 |

## 三 六条铁律（破一条即升级失败）

1. **维度不变**：25 / 47 / 9 / 8 / 34·21·5 / 25 全部不动；扩展包只写下界 `>= 7`。
2. **黄金值锁死**：`DIFF=0 2fc892cf9af6e755`、篡改 `f42c8229ee5acd73`、kfold `0.9957/0.0085` 不许漂。
3. **`spec.VERSION` 不动**（进回执、参与 ReproHash）；只升 `DOC_VERSION`。
4. **物理量不进哈希**：`latency_ms` / `build_ms` / `ts` 只打印。
5. **单一执行路径**：`Runnable.call` 内部仍走既有 `_invoke_skill`，不建第二条。
6. **单一裁决轨**：LLM-judge 分数只披露；是否回归只由确定性轨决定。

## 四 一键校验（照这个顺序跑）

```bash
python -m unittest discover -s tests                      # 34 OK
python -c "from holoaeon.selftest import run_all; r=run_all(); print(r['ok'], r['groups'])"   # True 25
python benchmarks\bench_public.py --no-write               # DIFF=0 2fc892cf9af6e755
python scripts\v3_gate.py --json reports\v3_gate.json      # 32/32 PASS
python scripts\launch_v3.py                                # ALL_OK=True（内外融合）
python scripts\eval_set.py --run                           # 确定性轨
python scripts\eval_diff.py                                # 双轨 diff（raw vs cross）
python scripts\repro_core_emit.py --check reports\repro_core.jsonl
python scripts\_check_py38_syntax.py                       # parsed=122 failures=0
```

退出码口径：`v3_gate` 任一 FAIL → 1；`bench_public` → `BENCH_EXIT=0`；
`launch_v3` → `ALL_OK=True` 才是 0。

## 五 八包的最小可用接口（写代码按这个调，改前先读文件）

- `runnable`：`STAGES`（admit→route→before_skill→after_skill→egress，顺序写死）；
  `HookChain.add(name, stage, fn)`；`CallConfig(trace, budget, mode, hooks, metadata)`；
  `Runnable.call(request, config)` / `batch` / `__or__`；`SkillRunnable / AgentRunnable /
  GuardRunnable / SinkRunnable / Pipeline`。
- `span_tree`：`SpanTree.child/record/structure_hash/from_dict/summary`；
  `structure_hash` 只含 `span_id/parent/name/kind/verdict/children`。
- `skill_schema`：`schema_from_inputs(inputs)`（`?` 结尾为可选）、`validate`、
  `call_with_repair(fn, schema, payload, repair, max_repair=2)` → `(result, meta)`。
- `eval_set`：`--write/--run/--variant raw|trunc12|upper|reverse|salt|cross`；`scorer=routing@1`。
  只有 `cross` 会真正掉点（把别条技能自述当问句），用来自证"diff 能抓回归"。
- `interrupt`：`halt(action, frozen, dir)` → `Interrupt`；`resume(store, id, decision, token)`；
  `CheckpointStore(dir, tier).write/latest/resume_from(total_steps)`；三档 `none/step/tick`。
- `skill_loader`：`manifest()`（只读自述不读正文）、`relevant/resolve`、`body_guard()`（证未越界）、
  `routing_accuracy(cases)`（对齐全量基线）。
- `cache`：`fingerprint(obj)`、`ByteCache.get_or_put`、`MemoCache`。
- `replay_branch`：`Ledger.append/digest/snapshot`、`ReplayBranch.branch_from(n)/untouched`、
  `compare(left, right)`（原账本 `digest` 必须不变）。
- `event_channel`：`EVENT_TYPES`（7 种）、`EventChannel.subscribe/emit/counts/summary`、
  `NullChannel`（关掉接口不变）。
- `bridges.conformance`：`REQUIRED_METHODS=("advertise","invoke","close")`、`Bridge`、
  `conformance(candidate)` → C1–C6（含 C5 静态离线扫描、C6 内核目录前缀判定）。

## 六 最容易踩的坑（挑最贵的说，全表见 references）

| # | 现象 | 处理 |
|---|---|---|
| V3-2 | span 树把耗时算进哈希 → 每次跑都漂 | 结构哈希只取结构字段 |
| V3-6 | replay 分支改了原账本 | 新分支独立记账，原 `digest` 逐字节不变 |
| V3-9 | conformance 用 `"\holoaeon\" in path` 判内核 → 误判桥为内核 | 用内核目录**绝对前缀**（仓库目录也叫 holoaeon） |
| V3-10 | 五段钩子出现双 route | admit/route/egress 只在顶层 `call` 跑，嵌套步 `_nested=True` |
| V3-12 | 用 `trunc12`/`reverse` 变体验不出回归 | 用 `cross` 对抗变体 |
| D-1 | 改 `DOC_VERSION` 后 kfold 结果文件名变了 | 重跑 `bench_semvec_kfold.py`，核对 mean/std 未漂 |

改完任何模块，**必须先跑 `v3_gate` 再谈结论**——`Write` 漏括号这类语法错，只有真跑才暴露。

## 七 交付口径

- 证据先于叙事：32/32、34/21/5、25、两份黄金哈希写在第一屏。
- 每份"没做"的事都要写进诚实清单，并写清为什么（`HONESTY_V3_20261101.md`）。
- 收尾必做：提交 → Gitee 权威 → GitHub 服务端对齐 → HF 镜像 → 飞书入口 → 向量海入库 → 回读校验。

细节见 `references/file-map.md`（每个落点对应哪个门禁）与
`references/gates-and-pitfalls.md`（A1–A13 与 V3-1..V3-12 全表）。

潮起开门，潮落闭嘴。
