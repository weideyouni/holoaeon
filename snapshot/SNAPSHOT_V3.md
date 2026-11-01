# SNAPSHOT V3 — HoloAeon 0.9.3（文档版本）

> 给其他智能体接手用的一页快照。**先读本页，再读 `AGENT_FEED_V3_DONE_20261101.md`。**
> 生成时间：2026-11-01（固定常量，不用 `time.gmtime()`，保证两次现算字节可复现）。
> 所有结论 `evidence_class=simulated`：仿真 ≠ 证明，碳基终裁。

## 1 维度（V1 → V2 → V3 全程不变）

| 项 | 值 | 断言位置 |
|---|---|---|
| 智能体 | **25** | `holoaeon/selftest.py` G15 / `tests/test_holoaeon.py` |
| 技能 | **47** | 同上 + `scripts/snapshot_v2.py` |
| 工作流 | **9** | `spec.PACK_ORDER` 派生 |
| 领域包 | **9** | `PACK_ORDER` |
| 扩展包 | **8**（≥7 下界） | `EXTRA_PACK_ORDER`（含 `persona_quartet`） |
| 原语 | **12** | `spec.CAPABILITIES` |
| 单测 | **34 / 21 / 5** | core / verax / v3 三套 |
| 自检 | **25**（G1–G25） | `selftest.run_all()["groups"] == 25` |

**V3 新增的 32 项门禁检查不计入上面任何一格**——它在 `scripts/v3_gate.py` 里独立计数，
理由：维度不变优先于"多几行断言"。`tests/v3` 仍是 5 条，未改动。

## 2 三个头牌数字（现算，不手抄）

| 指标 | 值 | 出处 |
|---|---|---|
| DIFF=0 哈希 | `2fc892cf9af6e755` | `benchmarks/bench_public.py --no-write` |
| 篡改敏感性 | `f42c8229ee5acd73` / `sensitive=True` | 同上 |
| 守卫 | 拦截 `16/16 = 100%`，合法放行 `4/4` | 同上 |
| 足迹 | `build≈31ms` / `peak=1.69MiB`（物理量，不进哈希） | 同上 |
| semvec k-fold | `mean 0.9957 / std 0.0085`（limit 0.05） | `benchmarks/results-semvec-kfold-0.9.3.json` |
| 证据行 | `10` 行，`verdict_hash` 全部复算一致 | `reports/repro_core.jsonl` |

## 3 V3 新增面（八个工作包，全部旁挂）

| 包 | 落点 | 状态 | 门禁 |
|---|---|---|---|
| W12 统一调用协议 | `holoaeon/runnable.py` | 可跑 | A4.1–A4.4 |
| W13 span 树 | `holoaeon/audit/span_tree.py` | 可跑 | A5.1–A5.4 |
| W14 结构化 schema | `holoaeon/skill_schema.py` | 可跑 | A6.1–A6.5 |
| W15 eval set + 双轨 | `scripts/eval_set.py` / `data/eval_47.json` / `scripts/eval_diff.py` | 可跑 | A7.1–A7.3 |
| W16 interrupt + checkpoint | `holoaeon/interrupt.py` | 可跑 | A8.1–A8.5 |
| W17 渐进加载 + 缓存 | `holoaeon/skill_loader.py` / `holoaeon/cache.py` | 可跑 | A9.1–A9.4 |
| W18 replay 分支 + 事件流 | `holoaeon/replay_branch.py` / `holoaeon/event_channel.py` | 可跑 | A10.1–A10.4 |
| W19 桥 conformance | `bridges/conformance.py` + `docs/migration-from-langchain.md` + `docs/deprecation.md` + `examples/monthly/` | 可跑 | A11.1 |

**V3 门禁：32/32 PASS**（`reports/v3_gate.json`，`verdict=PASS`）。

## 4 不变量（破了就是升级失败）

1. `spec.VERSION = "0.9.1"` 不动（写进回执、参与 ReproHash）；只升 `DOC_VERSION = "0.9.3"`。
2. `DIFF=0 2fc892cf9af6e755` / `f42c8229ee5acd73` 不漂。
3. 三套单测 34/21/5、自检 25、25/47/9 不变。
4. 零依赖（`pyproject.toml` `dependencies = []`）、离线、无遥测。
5. 物理量不进哈希：`latency_ms` / `build_ms` / `ts` 只打印。
6. 单一执行路径：`Runnable.call` 内部仍走 `Agent._invoke_skill`，不新建第二条。

## 5 新增代码规模

- 内核包 `holoaeon/**/*.py`：**52 文件 / 13,336 行**（V2 为 44 / 12,212；新增 8 个模块）。
- 旁挂脚本：`v3_gate.py`、`launch_v3.py`、`eval_set.py`、`eval_diff.py`；
  桥：`bridges/conformance.py`；示例：`examples/monthly/01_runnable_pipeline.py`。

## 6 已知限制（诚实披露）

- `eval_47` 的问句来自技能自述本身，`raw` 准确率 `47/47` 属**自证**，只能证明"路由不退化"，
  不能当质量结论；`cross` 对抗变体掉到 `0/47`，用来证明 diff 确实能抓回归。
- `SkillLoader` 的正文按需加载目前只覆盖 `skills/` 下的文档型技能；47 个注册表技能
  多数是纯函数，无正文可裁——"命中率不降"仅在文档型技能上验证。
- 桥 conformance 的 C5（离线）是**静态扫描** `socket/urllib/requests/urlopen/http`，
  挡不住动态导入；C6（不改内核）按文件前缀判定，跨包复制仍可能绕过。
- `interrupt` 的 checkpoint 为**单文件原子写**，不是 WAL；进程在 `os.replace` 之外
  被强杀最多丢一个 checkpoint（已用 10 步裁一半的用例验证续跑 DIFF=0）。
- `examples/monthly` 目前 1 个示例，由 `v3_gate` 的 A4/A5/A10 覆盖同链路，
  **未**新增独立 CI workflow（改 `.github/` 需 MCP，且会被同步覆盖）。

## 7 入口命令（照抄可跑）

```bash
python -m unittest discover -s tests                     # 34 OK
python -c "from holoaeon.selftest import run_all; r=run_all(); print(r['ok'], r['groups'])"   # True 25
python benchmarks\bench_public.py --no-write              # DIFF=0 2fc892cf9af6e755
python scripts\eval_set.py --write                        # data\eval_47.json（47 条）
python scripts\eval_set.py --run                          # 确定性轨 routing@1
python scripts\eval_diff.py                               # 双轨 diff（raw vs cross）
python scripts\v3_gate.py --json reports\v3_gate.json     # 32/32 PASS
python scripts\launch_v3.py                               # 本地装载 + 内外融合 ALL_OK
python scripts\repro_core_emit.py --check reports\repro_core.jsonl
python scripts\_check_py38_syntax.py                      # parsed=122 failures=0
```

## 8 不做清单（要看见但不抄 LangChain 的成本结构）

不为接一个服务破零依赖；不同时维护两套入口；不把观测/评测寄生于闭源平台；
不把默认封装太厚；不为集成广度稀释单点质量；不把 LLM-judge 当唯一证据；
不让 trace 树把物理量带进哈希。

潮起开门，潮落闭嘴。
