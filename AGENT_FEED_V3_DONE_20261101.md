# 一键复制投喂包 · HoloAeon V3 已完成（LangChain 工程形态落地，2026-11-01）

> **用法**：整段复制给任意实现智能体。自包含。读完即可接手，不必先读 README。
> **你的身份**：HoloAeon 的接手智能体。
> **你的任务**：不是重做 V3，而是**接手校验 + 继续往前**。V3 已落地并通过 32/32 门禁。
> 密令：潮起开门，潮落闭嘴。全部条目 `evidence_class=simulated`：仿真 ≠ 证明，碳基终裁。

## 0 当前状态（交接句）

V3 的八个工作包（W12–W19）已全部落盘并可跑；`spec.DOC_VERSION` 由 `0.9.2` 升为 `0.9.3`，
`spec.VERSION` 仍为 `0.9.1`（写进回执、参与 ReproHash，**不许动**）。
V3 门禁 32/32 PASS；三套单测 34/21/5、自检 25、25 智能体 / 47 技能 / 9 领域包全部未变；
`DIFF=0 2fc892cf9af6e755`、篡改哈希 `f42c8229ee5acd73` 未漂。

## 1 起点表（V1 / V2 / V3）

| 项 | V1 | V2 | V3 现状 |
|---|---|---|---|
| `spec.VERSION` | 0.9.1 | 0.9.1 | **0.9.1（不动）** |
| `spec.DOC_VERSION` | — | 0.9.2 | **0.9.3** |
| 智能体 / 技能 / 工作流 | 25/47/9 | 25/47/9 | **25/47/9（不变）** |
| 领域包 / 扩展包 | 9/7 | 9/8 | **9/8（≥7 下界）** |
| 单测（三套） | 34/16/5 | 34/21/5 | **34/21/5（未变）** |
| 自检 | 24 | 25 | **25（G1–G25）** |
| DIFF=0 | `2fc892cf9af6e755` | 同 | **同（未漂）** |
| 篡改哈希 | `f42c8229ee5acd73` | 同 | **同（未漂）** |
| semvec k-fold | — | 0.9957 / 0.0085 | **0.9957 / 0.0085**（文件名改为 `-0.9.3.json`） |
| V3 门禁 | — | — | **32/32 PASS**（`reports/v3_gate.json`） |

**为什么只升 DOC_VERSION**：`VERSION` 参与回执与 ReproHash，改了等于让 V1 黄金漂移；
DOC_VERSION 只影响文档/快照/徽章与 kfold 结果文件名。

## 2 已落盘的八件（带真实接口）

| 包 | 文件 | 关键接口 | 门禁 |
|---|---|---|---|
| W12 | `holoaeon/runnable.py` | `STAGES`(五段) `HookChain.add/run` `CallConfig(trace,budget,mode,hooks)` `Runnable.call/batch/__or__` `SkillRunnable/AgentRunnable/GuardRunnable/SinkRunnable/Pipeline` | A4.1–A4.4 |
| W13 | `holoaeon/audit/span_tree.py` | `Span.add/structural` `SpanTree.child/record/structure_hash/from_dict/flat/summary` `SpanRecorder` | A5.1–A5.4 |
| W14 | `holoaeon/skill_schema.py` | `schema_from_inputs` `validate` `SchemaError.fields` `call_with_repair(max_repair=2)` | A6.1–A6.5 |
| W15 | `scripts/eval_set.py` `data/eval_47.json` `scripts/eval_diff.py` | `--write/--run/--variant raw\|trunc12\|upper\|reverse\|salt\|cross`；diff 输出 improved/regressed/unchanged | A7.1–A7.3 |
| W16 | `holoaeon/interrupt.py` | `halt` `resume(store,id,decision,token)` `CHECKPOINT_TIERS`(none/step/tick) `CheckpointStore.resume_from` | A8.1–A8.5 |
| W17 | `holoaeon/skill_loader.py` `holoaeon/cache.py` | `SkillLoader.manifest/relevant/resolve/stats/routing_accuracy/body_guard`；`ByteCache.get_or_put/stats` `MemoCache` | A9.1–A9.4 |
| W18 | `holoaeon/replay_branch.py` `holoaeon/event_channel.py` | `Ledger.append/digest/snapshot` `ReplayBranch.branch_from/untouched` `compare`；`EVENT_TYPES`(7) `EventChannel` `NullChannel` | A10.1–A10.4 |
| W19 | `bridges/conformance.py` `docs/migration-from-langchain.md` `docs/deprecation.md` `examples/monthly/01_runnable_pipeline.py` | `REQUIRED_METHODS=(advertise,invoke,close)` `Bridge` `conformance(candidate)`（C1–C6） | A11.1 |

新增入口：`scripts/launch_v3.py`（本地装载 + 内外融合，末行 `ALL_OK=True`）、
`scripts/v3_gate.py`（32 项门禁，`--json` 落盘）。

## 3 实测输出（照抄可复现，不是"应该会"）

```text
$ python -m unittest discover -s tests
Ran 34 tests in 0.182s
OK

$ python -c "from holoaeon.selftest import run_all; r=run_all(); print(r['ok'], r['groups'])"
True 25

$ python benchmarks\bench_public.py --no-write
DIFF=0 2fc892cf9af6e755 | 拦截 100% | 冷装配 30.88ms / 峰值 1.69MiB
敏感性 base=2fc892cf9af6e755 tampered=f42c8229ee5acd73 sensitive=True
BENCH_EXIT=0

$ python scripts\eval_set.py --run
{"suite":"eval_47","variant":"raw","cases":47,"ok":47,"accuracy":1.0,
 "score_mean":0.4501,"score_std":0.1324,"evidence_class":"simulated"}

$ python scripts\eval_diff.py
{"left":{"variant":"raw","accuracy":1.0},"right":{"variant":"cross","accuracy":0.0},
 "common":47,"improved":[],"regressed":[47 条],"unchanged":0,"verdict":"REGRESSED"}

$ python scripts\v3_gate.py --json reports\v3_gate.json
[... 32 行 PASS ...]
{"passed":32,"total":32,"failed":[],"verdict":"PASS"}

$ python scripts\launch_v3.py
内部融合   agents=25 skills=47 graph_nodes=25
统一协议   skill=word_count status=ok trail=['guard','word_count','sink']
span 树    structure_hash=156b69db6aeafc4f（latency 不入哈希）
事件流     run_start/route/skill_call/run_end 各 1
内核复核   all_ok=True
外部融合   routes={"cheapest":"local","largest_context":"cloud"}
桥 conformance  PASS (6/6)
ALL_OK=True

$ python scripts\bench_semvec_kfold.py --folds 5
混合 P@1  mean=0.9957  std=0.0085 (limit std<=0.05)
written: benchmarks\results-semvec-kfold-0.9.3.json

$ python scripts\repro_core_emit.py --check reports\repro_core.jsonl
CHECK OK: 10 行 verdict_hash 全部复算一致

$ python scripts\_check_py38_syntax.py
parsed=122  py38_syntax_failures=0
```

## 4 三条最容易踩坏的口径（改动前必读）

1. **DOC_VERSION 会改文件名**：`bench_semvec_kfold.py` 与 `repro_core_emit.py` 都用
   `results-semvec-kfold-<DOC_VERSION>.json`。改版本号后**必须重生成**，否则快照与证据行缺 kfold。
   实测重生成后 mean/std 与 V2 完全一致（同语料、确定性）。
2. **`VERSION` 不许动**：它进回执、参与 ReproHash，动了 DIFF=0 立刻漂。
3. **34/21/5 与 25 自检不许改**：V3 的 32 项是**独立门禁**，不并入三套单测；
   `tests/v3` 仍是 5 条。想加断言就加到 `scripts/v3_gate.py`。

## 5 已知坑（V1 + V2 + V3 新增，全部真实发生过）

| # | 现象 | 处理 |
|---|---|---|
| V1-1 | `python -m holoaeon.selftest` 早期无 `__main__` | 用 `launch_local.py selftest` 或直接 `run_all()` |
| V2-1 | `assertEqual(ORDER, 7)` 因扩展包变 8 失败 | 已修为 ≥7，不许改回精确等值 |
| V2-2 | `persona_quartet` 的 P1–P4 与公开人物版并存 | 调用必须用 P1–P4 的隔离命名 |
| **V3-1** | `runnable` 与 `kernel.submit` 各建执行路径 | `Runnable.call` 内部仍走既有 `_invoke_skill`，不建第二条 |
| **V3-2** | span 树把 `latency_ms` 算进哈希 → 每次跑都漂 | `structure_hash` 只取结构字段，耗时单独存 |
| **V3-3** | schema 校验失败静默兜底 | 缺参/类型错/多余字段显式指名字段，超 2 次抛 `SchemaError` |
| **V3-4** | interrupt 令牌联网校验 → 破离线 | 令牌落 JSON 文件本地比对 |
| **V3-5** | eval 用 judge 分数裁决 | judge 只披露；裁决走确定性轨；结论标 `simulated` |
| **V3-6** | replay 分支改原账本 | 新分支独立记账，原账本 `digest` 必须逐字节不变 |
| **V3-7** | 渐进加载裁过头降命中率 | 用 `routing_accuracy` 对齐全量基线，降了就回退 |
| **V3-8** | `inspect.getsource(实例)` 报 `TypeError` | 用 `inspect.getfile(type(obj))` |
| **V3-9** | conformance 用 `"\holoaeon\" in path` 判内核 → 桥文件本身路径含 `holoaeon` 被误判 | 用内核目录**绝对前缀**比较（仓库目录也叫 holoaeon） |
| **V3-10** | 五段钩子被 Pipeline 与 Skill 各跑一次 route → 出现双 route | admit/route/egress 只在顶层 `call` 跑；嵌套步用 `_nested=True` 跳过 |
| **V3-11** | `run_all()["groups"]` 是 int 不是 list | 直接打印，别 `len()` |
| **V3-12** | eval 用 `trunc12`/`reverse` 变体验不出回归（仍 47/47） | 用 `cross` 对抗变体（把别条技能的自述当问句）才会掉到 0/47 |

## 6 验收判据（A1–A13，逐条可判定 + 现状）

| # | 判据 | 现状 |
|---|---|---|
| A1 | 25 自检 + 34 单测 + 红线零违规 | PASS（`True 25` / `Ran 34 OK`） |
| A2 | DIFF=0 仍旧黄金 + 篡改仍 sensitive | PASS（`2fc892cf9af6e755` / `True`） |
| A3 | 守卫 16/16 拦截 + 4/4 放行 | PASS |
| A4 | 技能可 `call`/`batch`；五段钩子顺序；钩子错可定位 | PASS（A4.1–A4.4） |
| A5 | span 树可导出可哈希；开关它内核字节不变 | PASS（A5.1–A5.4） |
| A6 | schema 显式报错 + 有限修复环 | PASS（A6.1–A6.5） |
| A7 | 47 条四件套；diff 能出变好/变差；judge 不裁决 | PASS（A7.1–A7.3） |
| A8 | 暂停态跨实例恢复；未批不执行；强杀续跑 DIFF=0 | PASS（A8.1–A8.5） |
| A9 | 无关技能不读正文；命中率不降；缓存逐字节同 | PASS（A9.1–A9.4） |
| A10 | 分支不改原账本；可比；事件只读零网络；开关字节不变 | PASS（A10.1–A10.4） |
| A11 | 新桥 3 方法 + conformance | PASS（6/6） |
| A12 | `dependencies = []` 未破 | PASS |
| A13 | 新数字有出处，eval 标 simulated，judge 不进裁决轨 | PASS（本文 §7） |

## 7 诚实清单（做完的 / 没做完的 / 为什么不）

**做完的**：八包代码 + 32 项门禁 + 本地装载 + 内部/外部融合 + 迁移页 5 场景 + 弃用日落表 +
月度示例 + README（英/中）+ SNAPSHOT_V3 + 本投喂包 + 新技能入库 + 三地同步。

**没做完的（如实披露，不藏）**：

1. `eval_47` 的问句来自技能自述，`raw 47/47` 是**自证**，只证明"路由不退化"，**不是质量结论**。
   真正的外部问句集尚未建立——这是 V4 的第一件事。
2. `examples/monthly` 只有 1 个示例，**没有独立 CI workflow**：GitHub 的 `.github/` 改动只能走
   MCP 且会被对齐覆盖；当前由 `v3_gate` 的 A4/A5/A10 覆盖同一链路。
3. `SkillLoader` 的"正文按需加载"只对 `skills/` 下的文档型技能有效；47 个注册表技能多为纯函数，
   无正文可裁。命中率对齐只在文档型技能上验证过。
4. 桥 conformance 的 C5 是**静态扫描**（`socket/urllib/requests/urlopen/http`），挡不住动态导入；
   C6 按文件前缀判定，跨包复制仍可能绕过。
5. checkpoint 是**单文件原子写**，不是 WAL；`os.replace` 之外被强杀最多丢 1 个 checkpoint。
6. `tests/v3` 仍是 5 条，V3 新增断言全部放在 `scripts/v3_gate.py`（32 项）——
   这是为守住"34/21/5 不变"的取舍，**不是遗漏**。
7. kfold 结果文件名随 DOC_VERSION 变为 `-0.9.3.json`，旧的 `-0.9.2.json` 留在盘上未删（并存，不覆盖）。

## 8 接手后建议的下一步（按优先级）

1. 建**外部问句集**（人不看着技能描述提问），把 `eval_47` 的 47/47 变成有信息量的数字。
2. 给 47 个技能补 `manifest.input_schema`，把 D2（反射猜参数）推进到日落条件。
3. 把 `examples/monthly` 扩到 3 个（每月一个），并把示例跑失败接入 `v3_gate`。
4. 给 `SkillLoader` 加"文档型技能覆盖率"指标，避免"看起来省了上下文"的空转。

## 9 立场（写进报告，不要只写代码）

LangChain 值得抄的是**工程形态**：统一协议、横切钩子、可恢复暂停、状态分档、trace 树、
数据集化评测、薄适配器、渐进加载。不值得抄的是**成本结构**：依赖暗礁、平台寄生、
抽象缠绕、集成稀释。HoloAeon 的差异化不在功能表，而在"同一输入必须给出同一字节"——
守住它，抄来的每一条都是加分；守不住，每一条都只是负债。

潮起开门，潮落闭嘴。投喂结束。
