# V3 落点 ↔ 门禁对照表

> 读这份表就不用逐个翻源码找"哪条断言在管我"。

| 门禁 | 断言内容 | 落点文件 | 复算命令 |
|---|---|---|---|
| A1 | 25 智能体 / 47 技能 / 9 领域包 | `holoaeon/packs`、`selftest.py`、`tests/test_holoaeon.py` | `v3_gate.py`、`unittest discover` |
| A4.1 | `call` 与 `batch` 同一实现 | `holoaeon/runnable.py` | `v3_gate.py` |
| A4.2 | 五段钩子顺序固定 | 同上（`Runnable.call` + `Pipeline._call`） | 同上 |
| A4.3 | 管道可 `dump` 成可读结构 | 同上（`Pipeline.dump`） | 同上 |
| A4.4 | 钩子抛错定位到具体钩子 | 同上（`HookError(stage, hook, cause)`） | 同上 |
| A5.1 | 耗时不进结构哈希 | `holoaeon/audit/span_tree.py` | 同上 |
| A5.2 | 结构变则哈希变 | 同上 | 同上 |
| A5.3 | 可序列化可回放 | 同上（`to_dict/from_dict`） | 同上 |
| A5.4 | 开关 span 树内核字节不变 | `reprohash` + `Kernel.submit` | 同上 |
| A6.1–A6.3 | 缺参 / 类型错 / 多余字段指名 | `holoaeon/skill_schema.py` | 同上 |
| A6.4 | 有限修复环可自愈 | 同上（`call_with_repair`） | 同上 |
| A6.5 | 修复超限抛错 | 同上（`max_repair=2`） | 同上 |
| A7.1 | 47 条四件套（input/reference/scorer/evidence_class） | `data/eval_47.json`、`scripts/eval_set.py` | `eval_set.py --write` |
| A7.2 | 双轨 diff 能抓回归 | `scripts/eval_diff.py` | `eval_diff.py --variant cross` |
| A7.3 | judge 只披露不裁决 | `scripts/eval_set.py`（`scorer=routing@1`） | `eval_set.py --run` |
| A8.1 | 暂停态跨实例恢复 | `holoaeon/interrupt.py`（`InterruptStore`） | `v3_gate.py` |
| A8.2 | 获批后可执行 | 同上（`resume`） | 同上 |
| A8.3 | 令牌错不执行 | 同上 | 同上 |
| A8.4 | 三档各写清保证与代价 | 同上（`CHECKPOINT_TIERS`） | 同上 |
| A8.5 | 强杀续跑 DIFF=0 | 同上（`CheckpointStore.resume_from`） | 同上 |
| A9.1 | manifest 常驻不读正文 | `holoaeon/skill_loader.py` | 同上 |
| A9.2 | 只有候选读正文 | 同上（`body_guard`） | 同上 |
| A9.3 | 裁剪不降命中率 | 同上（`routing_accuracy`） | 同上 |
| A9.4 | 缓存逐字节相同 | `holoaeon/cache.py` | 同上 |
| A10.1 | 分支不改原账本 | `holoaeon/replay_branch.py` | 同上 |
| A10.2 | 两支可比 | 同上（`compare`） | 同上 |
| A10.3 | 事件 7 种、只读零网络 | `holoaeon/event_channel.py` | 同上 |
| A10.4 | 开关通道内核字节不变 | 同上 + `Kernel.submit` | 同上 |
| A11.1 | 新桥 3 方法 + conformance 6/6 | `bridges/conformance.py` | 同上 |
| A12.1 | `dependencies = []` 未破 | `pyproject.toml` | 同上 |
| A13 | 新数字有出处、结论 simulated | `HONESTY_V3_20261101.md` | 人工复核 |

## 相关文档

- `snapshot/SNAPSHOT_V3.md` — 一页接手页（维度 / 三数字 / 新增面 / 限制 / 命令）。
- `AGENT_FEED_V3_DONE_20261101.md` — 一键复制投喂包（含实测 stdout 与坑表）。
- `docs/migration-from-langchain.md` — 5 个迁移场景的可跑写法。
- `docs/deprecation.md` — 并存项的日落条件（D1–D8）。
- `examples/monthly/01_runnable_pipeline.py` — 月度可跑示例。
