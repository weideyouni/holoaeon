# 从 LangChain 迁移到 HoloAeon（V3 工程形态）

> 本文覆盖五个高频场景：单 agent / 工具调用 / 多 agent 协作 / 记忆 / 评测。
> 每个场景给出**可跑的 HoloAeon 写法**，并说明"为什么这样写不破坏确定性"。
> 所有结论 `evidence_class=simulated`：仿真 ≠ 证明，碳基终裁。

## 0. 一句话对照

LangChain 给的是"万物皆可 call + 可插桩 + 可暂停 + 可评测"的**工程形态**；
HoloAeon 保留这套形态，但把它的**成本结构**（传递依赖、平台寄生、抽象缠绕）剥掉，
换成"零依赖 / 离线 / 确定性 / fail-loud / 证据链 / 稀疏逻辑拓扑"。

## 1. 单 agent：`Agent` + `Envelope`

LangChain 侧是 `Runnable.invoke(input)`；HoloAeon 侧是信封进、结果出。

```python
from holoaeon.kernel import Kernel
from holoaeon.packs import PACK_ORDER, get_pack

k = Kernel()
for key in PACK_ORDER:
    get_pack(key).install(k)

out = k.submit("统计字数，这是一句用于演示的文本")
print(out["all_ok"], out["results"][0]["status"], out["results"][0]["output"])
```

差异点：`k.submit` 返回的是**结构化回执**（agent_id / status / matched / output），
不是一段拼接字符串——后面的证据链、span 树、评测都靠这些字段，而不是靠文本解析。

## 2. 工具调用：`SkillRunnable` + 五段钩子

LangChain 侧是 `@tool` + `ToolNode`；HoloAeon 侧是"技能包成 Runnable，钩子横切"。

```python
from holoaeon.runnable import CallConfig, HookChain, Pipeline, SkillRunnable, GuardRunnable, SinkRunnable

skill = k.skills.get("word_count")
hooks = HookChain()
hooks.add("audit", "before_skill", lambda ctx: print("call", ctx["node"]) or ctx)
hooks.add("audit", "after_skill",  lambda ctx: print("done") or ctx)

pipe = Pipeline([GuardRunnable(k.guard), SkillRunnable(skill), SinkRunnable()])
print(pipe.call({"task": "统计字数：Hello HoloAeon"}, CallConfig(hooks=hooks)))
```

要点：
- 钩子只有五段（admit → route → before_skill → after_skill → egress），**顺序写死**；
- 钩子内抛错会被包成 `HookError(stage, hook, cause)`，错误定位到具体钩子，不静默；
- `Runnable.call` 内部仍走 `Agent._invoke_skill`，**没有第二条执行路径**（V3-1）。

## 3. 多 agent 协作：`Kernel.submit(to=...)` + `collab`

LangChain 侧是 supervisor / handoff；HoloAeon 侧是地址 + 协作图 + 信封 trace。

```python
targets = [a for a in k.agents if a.endswith(".router")][:1]
out = k.submit("做一份周报结构", to=targets[0] if targets else None)
print(out["targets"], out["all_ok"])

collab = k.collab("多智能体协作拆解一个季度复盘", k.agents.keys())
print([r["agent_id"] for r in collab["results"]][:5])
```

要点：协作图上每个 agent 是一个节点（`graph.snapshot()["nodes"]`），
信封的 `trace` 记录走过的节点——这就是 LangGraph 的"边"，只是不引入新依赖。

## 4. 记忆：`Memory` 三档（working / longterm / archive）

LangChain 侧是 `ConversationBufferMemory` 一族；HoloAeon 侧是显式三档 + 可快照。

```python
from holoaeon.memory import Memory
m = Memory()
m.put("k1", {"note": "第一条"}, kind="working", tags=["demo"])
m.put("k2", {"note": "长期"}, kind="longterm", tags=["demo"])
print(m.stats(), m.get("k1"))
```

要点：档位是**显式参数**，不是隐式策略；`stats()` 可进证据行，
避免"记忆看起来生效了但取不出来"这类不可诊断失败。

## 5. 评测：`eval_set` 确定性轨 + `eval_diff` 双轨

LangChain 侧是 LangSmith 托管数据集；HoloAeon 侧是**离线可复算**的 47 条集。

```bash
python scripts\eval_set.py --write          # 生成 data\eval_47.json（47 条四件套）
python scripts\eval_set.py --run            # 确定性轨：routing@1
python scripts\eval_diff.py                 # 双轨 diff：raw vs cross（对抗变体）
python scripts\v3_gate.py                   # 32 项 V3 门禁
python scripts\launch_v3.py                 # 本地装载 + 内外融合
```

要点：
- scorer 是**确定性规则**（路由是否回到原技能），judge 分数只披露不裁决（V3-5）；
- 本集是"技能自述路由自证"：`raw` 准确率 47/47 只证明**路由不退化**，
  不能当质量结论——对抗变体 `cross` 会掉到 0/47，用来证明 diff 真的能抓回归；
- 评测结论一律 `evidence_class=simulated`。

## 6. 与 LangChain 的取舍表

| 维度 | LangChain 做法 | HoloAeon V3 做法 | 取舍原因 |
|---|---|---|---|
| 统一调用 | `Runnable` + LCEL `\|` | `Runnable.call` + `Pipeline` | 同一形态，零依赖实现 |
| 横切 | middleware / callback | 五段 `HookChain` | 段数写死，错误可定位 |
| 追踪 | LangSmith / callbacks | `SpanTree` + `structure_hash` | 离线、可哈希、耗时不入哈希 |
| 暂停 | `interrupt` + checkpointer | `interrupt` + 三档 checkpoint | 令牌离线，跨进程恢复 |
| 评测 | 托管数据集 + judge | `eval_47` + 双轨 diff | 可复算，judge 不裁决 |
| 适配 | 几十个 partner 包 | 3 方法 `Bridge` + conformance | 不稀释单点质量 |

**不抄的**：为接一个服务破零依赖；同时维护两套入口；把观测寄生于闭源平台；
默认封装过厚导致失败不可诊断；为集成广度稀释单点质量；把 judge 当唯一证据；
为了让 trace 好看把物理量写进哈希。

## 7. 回滚与弃用

迁移期允许两套入口并存，但**每一条都有日落条件**：见
[`docs/deprecation.md`](deprecation.md)。超过日落条件仍未收敛，`fail-loud`
会把这件事变成红灯，而不是"以后再清理"。
