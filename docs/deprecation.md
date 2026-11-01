# 弃用与日落策略（V3）

> 原则：允许并存，但**每一条并存都有日落条件**；条件到期未收敛，按 fail-loud
> 处理（红灯，退出码 1），不许靠"以后再清理"拖着。
> 所有条目 `evidence_class=simulated`。

## 日落条件表

| # | 旧接口 / 旧做法 | 替代 | 日落条件（满足任一即必须收敛） | 现状 |
|---|---|---|---|---|
| D1 | 直接 `kernel.submit(task)` 当唯一入口 | `Runnable.call(request, config)` | 6 个月内 `runnable` 覆盖全部示例与文档入口，且 `kernel.submit` 仅作为内部执行路径 | 并存（有意） |
| D2 | `Agent._invoke_skill` 靠反射猜参数 | `manifest.input_schema` + `validate` | 47/47 技能 manifest 声明 inputs 后，反射仅作兜底 | 未到期（47 条中仅部分声明） |
| D3 | 全量加载 47 份技能正文 | `SkillLoader`（manifest 常驻 + 正文按需） | 连续 3 次发布中 eval 命中率不低于全量基线 | 已启用，条件持续监控 |
| D4 | 手抄三指标进 README | `reports/repro_core.jsonl` + `--check` | 自 V2 起 README 数字必须来自证据行 | 已完成（V2） |
| D5 | 一次性脚本硬编码路径 | 参数化脚本（`--transcript/--out/...`） | 任一脚本被第二个项目复用即必须参数化 | 部分完成（视频张量技能已参数化） |
| D6 | 追踪/评测依赖托管平台 | `span_tree` + `eval_47` 离线跑 | 无网络机器能跑完整评测即为达标 | 已完成（V3） |
| D7 | LLM-judge 当裁决 | judge 只披露，裁决走确定性轨 | 永不日落（红线） | 永久 |
| D8 | 双入口（`runnable` 与 `kernel.submit` 各建执行路径） | 单一执行路径 | 一旦出现第二执行路径必须立即移除 | 未发生（V3-1 已锁） |

## 弃用动作的三条硬约束

1. **不许静默降级**：旧接口在被调用时返回 `{"deprecated": true, "replacement": "..."}`
   或直接抛错，二选一，不许"能跑但不提示"。
2. **不许改黄金值**：弃用改造不得触碰 `DIFF=0 2fc892cf9af6e755` 与篡改哈希
   `f42c8229ee5acd73`；一旦改动，按 fail-loud 红灯处理。
3. **必须留证据**：每次弃用收敛都要在 `reports/` 留一行可复算记录
   （`measure_source / golden_value / observed_value / verdict_hash`）。

## 判定方式

```bash
python scripts\v3_gate.py            # A12 检查零依赖未破；A1 检查 25/47/9 不变
python scripts\repro_core_emit.py --check reports\repro_core.jsonl
```

日落条件本身不自动执行——它是**人工复核清单**；机器只负责把"破了红线"这件事
变成红灯（退出码 1），不负责替人做决策。
