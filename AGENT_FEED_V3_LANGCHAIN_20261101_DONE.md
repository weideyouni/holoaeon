# 面向智能体的一键复制投喂包 · HoloAeon V3 赋能升级方向（LangChain 工程形态借鉴，2026-11-01）

> 用法：整段复制给任意实现智能体。自包含。读完即可接手。
> 你的身份：HoloAeon 的实现智能体。你的任务：把 LangChain 1.x / LangGraph / LangSmith 的
> **工程形态**（不是成本结构）落到本项目约束上，**维度不变**——
> 25 智能体 / 47 技能 / 9 领域包 + ≥7 扩展包 / 34 单测 / 25 自检。
> 密令：**潮起开门，潮落闭嘴**。全部条目 `evidence_class=simulated`：仿真 ≠ 证明，碳基终裁。

---

## 0 V3 起点（V2 已落地，本轮在其上叠加）

| 项 | V1 锁值 | V2 已落地 | V3 起点 |
|---|---|---|---|
| spec.VERSION | 0.9.1 | 0.9.1（不动） | **0.9.1（不动）** |
| spec.DOC_VERSION | — | 0.9.2 | **0.9.3（新增）** |
| 智能体 / 技能 / 工作流 | 25/47/9 | 25/47/9 | **25/47/9（不变）** |
| 领域包 / 扩展包 | 9/7 | 9/8（+persona_quartet） | **9/8（不变）** |
| 单测（三套） | 34/16/5 | 34/21/5 | **34/21/5（V3 可+，不许破）** |
| 自检 | 24 | 25（G1–G25） | **25（不变）** |
| DIFF=0 哈希 | 2fc892cf9af6e755 | 2fc892cf9af6e755 | **2fc892cf9af6e755（V1 黄金，不许漂移）** |
| 篡改哈希（敏感性） | f42c8229ee5acd73 | f42c8229ee5acd73 | **f42c8229ee5acd73（V1 黄金，不许漂移）** |
| mutation | — | 5/5 全变 | **5/5（已落地，不动）** |
| repro_core | — | 10 行全绿 | **10 行（可扩，不许缩）** |
| fail-loud | — | ON（3 条硬红线） | **ON（不动）** |
| semvec kfold | — | mean=0.9957 std=0.0085 | **已落地（不动）** |

**V3 不改 spec.VERSION**：理由同 V2——VERSION 写进回执参与 ReproHash，动了等于让 V1 黄金值漂移。
V3 只升 DOC_VERSION=0.9.3，文档/快照/徽章用。

## 1 六护城河（破了即借鉴失败，与 V2 铁律同源）

本轮借鉴 LangChain 工程形态，**任何一条若破下面六条，则借鉴本身就是失败**：

1. **零依赖**：`pyproject.toml` 的 `dependencies = []`，`pip install` 零次
2. **离线**：无网络调用、无内置密钥、无遥测，气隙机器可跑
3. **确定性**：DIFF=0 哈希两次一致 + 篡改敏感性自检通过 + 物理量不进哈希
4. **fail-loud**：确定性失败必须退出码 1，不许降级黄灯
5. **证据链**：行级可哈希、`--check` 可复算、未实测不写成实测
6. **稀疏逻辑拓扑**：1331×1331 大矩阵永不预分配，节点按需激活

## 2 四分身归因研判（公开资料归因转述）

> 调用：`persona_quartet.persona_roundtable / persona_mission`；
> mission 排序：P2 筑基(overlap=4) = P3 构弦(4) > P1 探微(3) > P4 持衡(2)。

### P2 筑基（Jeff Dean 工程基建路线）——主张「统一协议 + 横切钩子 + trace 树」

**归因观点 1**：Scaling Hypothesis——算力数据模型规模提升智能能力。
**归因观点 2**：向量空间语义表示——语义可在向量空间运算。

→ 投射到 V3：Scaling 的工程对应是"统一协议让能力可组合可叠加"。
LangChain 的 Runnable 协议（invoke/batch/stream）+ LCEL 管道（`|`）+ middleware 钩子链，
本质是把"能力组合"做成可编译可插桩的工程件。HoloAeon 当前 Skill/Agent/Pack 各有入口，
缺一个"万物皆可 call"的统一面。**P2 主张先做 P0 三条**：统一调用协议、横切钩子链、trace span 树——
这是"分布式系统工程师本能"：基础设施先稳，上面 19 条都受益。

### P3 构弦（统一 tokenizer 思维）——主张「schema 校验 + 渐进加载 + 薄适配器」

**归因观点 1**：多模态是通用智能底层必需架构，统一联合训练而非单模态拼接。
**归因观点 2**：深度学习原理延续——DQN 到 Gemini 损失/优化/RL 一脉相承。

→ 投射到 V3：统一 tokenizer 的工程对应是"统一 schema"。
HoloAeon 当前 signature-aware binding 靠反射猜参数，缺显式 schema——
等于"各模态各自 tokenizer，没有统一损失"。P3 主张：Skill manifest 强制 input_schema、
47 技能正文按需加载（manifest 常驻）、新桥只实现 3 个方法（advertise/invoke/close）+
conformance 测试。**这是"统一联合训练而非拼接"的工程落地**。

### P1 探微（科学假设验证思维）——主张「eval set + 反馈闭环 + 实验对比」

**归因观点 1**：AGI 需具备自主提出科学假设的能力。
**归因观点 2**：持续学习/长期记忆/内省推理为核心。

→ 投射到 V3：科学假设需要实验验证。HoloAeon 25 自检只能证明"没坏"（断言存在性），
证明不了"变好"（质量评测）。P1 主张：47 技能建成 eval set（每条 input/reference/scorer）、
双轨对比（确定性轨照旧 + 质量轨用 eval 分数 diff）、错例回流成回归用例。
**这是"自主提出假设 → 实验验证 → 内省改进"的闭环**。

### P4 持衡（对齐优先思维）——主张「interrupt + checkpoint 三档 + fail-loud 守护」

**归因观点 1**：自回归序列模型具备极强通用推理潜力；缩放可涌现复杂能力。
**归因观点 2**：超级智能安全优先——对齐必须跑在能力前面。

→ 投射到 V3：对齐优先的工程对应是"高危动作不直接拒，而是挂起等人签核"。
LangChain 的 interrupt 把"人工签核"做成运行时原语（暂停态可序列化、审批后原位继续），
而不是报错。P4 主张：interrupt 可恢复暂停（Envelope 冻结 + 审批令牌 + 继续/撤销两条出口）、
checkpoint 三档（none/step/tick，每档写清保证与代价）、fail-loud 守护六护城河不被借鉴冲掉。
**这是"对齐必须跑在能力前面"的协议化落地**。

## 3 V3 八个工作包（W12–W19，全部旁挂，三闸不许破）

| 包 | 名称 | 主张分身 | 落点 | 维度影响 |
|---|---|---|---|---|
| W12 | 统一调用协议 + 横切钩子链 | P2 筑基 | `holoaeon/runnable.py`（新，不挂内核）+ Envelope 生命周期 hook chain | 单测+5，自检 25 不变 |
| W13 | trace span 树 | P2 筑基 | `holoaeon/audit/span_tree.py`（新）+ Envelope.trace 升级 | 单测+3，自检 25 不变 |
| W14 | 结构化 schema 校验 | P3 构弦 | `holoaeon/skill_schema.py`（新）+ manifest 强制 input_schema | 单测+4，自检 25 不变 |
| W15 | eval set + 双轨对比 | P1 探微 | `scripts/eval_set.py`（新）+ `data/eval_47.json` + `scripts/eval_diff.py` | 旁挂脚本，0 维度影响 |
| W16 | interrupt 可恢复暂停 + checkpoint 三档 | P4 持衡 | `holoaeon/interrupt.py`（新，不挂内核）+ snapshot 分级 none/step/tick | 单测+4，自检 25 不变 |
| W17 | 渐进式技能加载 + 可复算缓存 | P3 构弦 | `holoaeon/skill_loader.py`（新）+ `holoaeon/cache.py`（新，本地指纹缓存） | 单测+3，自检 25 不变 |
| W18 | replay 分支 + 类型化事件流 | 综合 P1+P2 | `holoaeon/replay_branch.py`（新）+ `holoaeon/event_channel.py`（新，只读零网络） | 单测+3，自检 25 不变 |
| W19 | 桥 conformance + 迁移页 + 弃用策略 + 示例节奏 | 综合 P3+生态 | `bridges/conformance.py`（新）+ `docs/migration-from-langchain.md` + `docs/deprecation.md` + `examples/monthly/` | 文档+脚本，0 维度影响 |

**完成度判定（V3 验收用）**：

- W12：`holoaeon/runnable.py` 给 Skill 加 `call(request, config)`，config 携带 trace 句柄/预算/模式；`__or__` 实现 `Envelope | Guard | Skill | Sink` 管道；hook chain 五段（admit→route→before_skill→after_skill→egress）顺序有单测；钩子抛错能定位到具体钩子。
- W13：任一 run 能导出 span 树（父子 run + 模型/tokens/耗时/错误属性）；树可序列化且可哈希（进证据链）；开不开 span 树，内核输出字节不变。
- W14：manifest 强制 input_schema（dataclass + 手写 validator）；缺参/类型错/多余字段显式报错指名字段；有限次修复环（默认 2 次，超限抛错）；不许静默兜底。
- W15：47 技能每条 eval 四件套（input/reference/scorer/evidence_class）；默认 scorer 用确定性规则，LLM-judge 只做披露不做裁决；`eval_diff.py` 两次 experiment 能 diff 出哪条变好/变差，不污染黄金值。
- W16：interrupt 待批状态（Envelope 冻结 + 审批令牌 + 继续/撤销两条出口），令牌可离线文件；未获批动作永不执行；审批事件进账本；snapshot 三档（none/step/tick）每档写清保证与代价；进程强杀后从最近 checkpoint 续跑，最终产物与不中断跑法 DIFF=0。
- W17：47 技能正文按需加载（manifest 常驻，正文确定相关再读）；无关技能不消耗上下文；命中率不因裁剪下降（用 eval set 验证）；本地缓存"输入指纹→输出字节"，同输入第二次命中且逐字节相同。
- W18：从第 N 步开新分支，新分支独立记账，**原账本字节不变（哈希不变）**；两支可并排比较；事件通道只读零网络，事件类型收敛到 6–8 种；开不开事件通道，内核输出字节不变。
- W19：新桥只需实现 3 方法（advertise/invoke/close）+ 通过 conformance 测试，不加内核代码即可接入；迁移页覆盖 5 高频场景（单 agent/工具调用/多 agent 协作/记忆/评测）每段可跑；弃用清单每项有日落条件，旧接口被调用时给替代建议；每月一个可跑示例随 CI 跑，示例腐烂会红。

## 4 照抄可跑的命令（V3 增量，先跑通基线再动 V3）

```bash
cd F:\doubaowork\holoaeon
python scripts\launch_local.py status        # has_graph=True  has_adapter=True
python scripts\launch_local.py selftest     # ==> 25/25
python -m unittest discover -s tests       # Ran 34 tests ... OK
python -m unittest discover -s tests\verax # Ran 21 tests ... OK
python -m unittest discover -s tests\v3    # Ran 5 tests ... OK
python scripts\redline_scan.py              # 零违规
python scripts\verax_verify.py --out reports --mutate 5   # V2 已落地
python benchmarks\bench_public.py           # BENCH_EXIT=0 + 三个数字
python scripts\bench_semvec_kfold.py        # V2 已落地
python scripts\repro_core_emit.py --out reports/repro_core.jsonl  # V2 已落地
# V3 新增（落地后）
python scripts\eval_set.py --run             # 47 技能 eval 四件套
python scripts\eval_diff.py --baseline v2 --current v3   # 双轨对比
python scripts\span_tree_emit.py --run-id <id>           # 导出 span 树
```

## 5 V3 不做的清单（反模式：要看见但不抄）

1. **不**为接一个服务而破零依赖——LC 生态的传递依赖暗礁是它的成本，不是 HoloAeon 的方向；
2. **不**同时维护两套入口——LC 用 1.0 才清理掉旧 chains 与新 agent 并存的历史债，HA 若同时维护 runnable.py 与既有 kernel.submit，同一场事故重演；
3. **不**把观测与评测寄生于闭源托管平台——LangSmith 是 LC 的可选展示，HA 的观测与评测必须能离线跑；
4. **不**把默认封装太厚——LC 的隐藏魔法让失败不可诊断，HA 的 fail-loud 与"错误定位到层"必须反向坚持；
5. **不**为集成广度稀释单点质量——HA 宁可 47 个技能都过 eval，也不要 470 个半成品；
6. **不**把 LLM-judge 分数当唯一证据——judge 分数只能 `simulated`，不能进裁决轨（既有红线）；
7. **不**为了让 trace 树漂亮而把物理量写进哈希——build_ms/latency_ms 只打印不落行（V2 R-1 既定）。

## 6 已知坑（V1+V2+V3 新增）

| # | 现象 | 原因 | 处理 |
|---|---|---|---|
| V1-1 | `python -m holoaeon.selftest` 早期无 `__main__` | 历史坑 | 用 `launch_local.py selftest` |
| V2-1 | `assertEqual(ORDER, 7)` 失败 | persona_quartet 装入变 8 | 已修为 ≥7，**不许改回精确等值** |
| V2-2 | persona_quartet 化名 P1–P4 与公开人物版并存 | 命名空间隔离 | 调用技能必须用 P1–P4 |
| V3-1 | runnable.py 与 kernel.submit 并存风险 | 双入口抽象缠绕 | runnable.py 只做协议封装，内部仍走 kernel.submit，**不新建第二执行路径** |
| V3-2 | span_tree 哈希若含耗时则漂移 | 物理量进哈希 | span 树哈希只取结构字段（parent/child/name/verdict），latency_ms 只打印不落哈希 |
| V3-3 | schema 校验失败若静默兜底 | 隐藏魔法 | 缺参/类型错/多余字段必须显式报错指名字段，**不许静默兜底** |
| V3-4 | interrupt 令牌若联网则破离线 | 网络调用 | 审批令牌必须离线文件（JSON），**不联网** |
| V3-5 | eval set 若用 LLM-judge 当裁决 | 软化红线 | judge 分数只做披露不做裁决，eval 结论标 `evidence_class=simulated` |
| V3-6 | replay 分支若改原账本 | 破确定性 | 新分支独立记账，**原账本字节不变**（哈希不变），用 hash 校验 |
| V3-7 | 渐进加载若降低路由命中率 | 裁剪过度 | 用 eval set 验证命中率不下降，下降即回退全量 |

## 7 你要交的东西

1. W12–W19 八个包按序可跑代码 + 每步实测输出（贴 stdout 不许贴"应该会"）；
2. `snapshot/SNAPSHOT_V3.md` 刷新版：维度、三个数字、V3 新增行（runnable/span_tree/schema/eval_set/interrupt/checkpoint/渐进加载/缓存/replay 分支/事件流/桥 conformance/迁移页）、不变量、已知限制；
3. 同名更新版 README：V3 增量徽章在第三屏（不替换 V1 三数字、不替换 V2 四行）；
4. 本投喂包的更新版（补 §6 新坑）；
5. 一份诚实清单：哪些做了、哪些没做、为什么，**含 eval set 的 mean/std 与双轨 diff 结果** —— 因为质量轨是 V3 的核心新增，不许藏。

## 8 验收判据（V3，逐条可判定）

- **A1（基线）** selftest 25/25 且 34 tests OK 且 redline 零违规（三闸全绿）；
- **A2（确定性）** BENCH_EXIT=0，DIFF=0 仍 `2fc892cf9af6e755`，V2 mutation 5/5 仍 sensitive=True；
- **A3（守卫）** 20 条守卫集仍 16/16 拦截、4/4 放行；
- **A4（V3 runnable）** 任一技能 `call(request, config)` 不改实现即可 batch；`Envelope | Guard | Skill | Sink` 管道可 dump 成可读结构；hook chain 五段顺序有单测，钩子抛错定位到具体钩子；
- **A5（V3 span_tree）** 任一 run 能导出 span 树，树可序列化且可哈希；开不开 span 树，内核输出字节不变（DIFF=0 不漂移）；
- **A6（V3 schema）** manifest 强制 input_schema，缺参/类型错/多余字段显式报错指名字段；修复环默认 2 次超限抛错；
- **A7（V3 eval_set）** 47 技能 eval 四件套齐全；`eval_diff.py` 两次 experiment 能 diff 出哪条变好/变差；judge 分数只做披露不做裁决；
- **A8（V3 interrupt+checkpoint）** interrupt 待批状态可序列化跨进程恢复；未获批动作永不执行；审批事件进账本；snapshot 三档每档写清保证与代价；进程强杀后从最近 checkpoint 续跑，最终产物与不中断跑法 DIFF=0；
- **A9（V3 渐进加载+缓存）** 无关技能不消耗上下文；命中率不因裁剪下降（eval set 验证）；同输入第二次命中缓存且逐字节相同；
- **A10（V3 replay 分支+事件流）** 从第 N 步开新分支，原账本字节不变（哈希校验）；两支可并排比较；事件通道只读零网络，6–8 种事件类型；开不开事件通道内核输出字节不变；
- **A11（V3 桥+迁移+弃用+示例）** 新桥只实现 3 方法 + conformance 通过，不加内核代码；迁移页 5 场景每段可跑；弃用清单每项有日落条件；示例随 CI 跑，腐烂会红；
- **A12（约束）** `dependencies = []` 未破；pyproject.toml 无新增依赖；V1+V2 既有 golden 全保留；六护城河零违反；
- **A13（诚实）** 新增数字均有出处，eval 结论标 `evidence_class=simulated`，judge 分数不进裁决轨。

## 9 立场（写进报告，不要只写代码）

LangChain 值得抄的是工程形态：统一协议、横切钩子、可恢复暂停、状态分档、trace 树、
数据集化评测、薄适配器、渐进加载。
不值得抄的是成本结构：依赖暗礁、平台寄生、抽象缠绕、集成稀释。
**HoloAeon 真正的差异化不在功能表，而在"同一输入必须给出同一字节"这件事——
把它守住，抄来的每一条都是加分；守不住，抄来的每一条都只是负债。**

这一句是四分身归因的综合投射：P2 筑基的工程基建本能 + P3 构弦的统一tokenizer思维 +
P1 探微的科学假设验证 + P4 持衡的对齐优先——四派路线在"确定性是底线"这一点上收敛。

投喂结束。潮起开门，潮落闭嘴。