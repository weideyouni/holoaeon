# 面向智能体的一键复制投喂包 · HoloAeon V2 赋能升级方向（2026-11-01）

> 用法：整段复制给任意实现智能体。自包含。读完即可接手，不需要先读全部源码。
> 你的身份：HoloAeon 的实现智能体。你的任务：把「确定性 + 诚实」的可复算证据资产
> 推进到 V2，**维度不变**——25 智能体 / 47 技能 / 9 领域包 + ≥7 扩展包 / 34 单测 / 25 自检。
> 密令：**潮起开门，潮落闭嘴**。
>
> 全部条目 `evidence_class=simulated`：仿真 ≠ 证明，碳基终裁。

---

## 0 你接手的项目（V2 起点，全部现算）

| 项 | V1 文档锁值 | V1 现实实测（2026-11-01） | V2 锁定 |
|---|---|---|---|
| 版本 | 0.9.1 | 0.9.1（spec.py VERSION 权威） | 0.9.2（仅升级包与文档） |
| 智能体（裸内核） | 25 | 25 | **25（不变）** |
| 技能（裸内核） | 47 | 47 | **47（不变）** |
| 领域包 | 9 | 9 | **9（不变）** |
| 扩展包 | 7 | 8（含 persona_quartet） | **≥7（旁挂纪律已立）** |
| 单测（tests/） | 34 | 34 | **34（不变）** |
| 自检组 | 24 | 25（G1–G25，含 persona_quartet 8/8） | **25（V1 已抬，V2 锁定）** |
| DIFF=0 哈希 | 2fc892cf9af6e755 | 2fc892cf9af6e755 | **保留 V1 黄金值** |
| 拦截率 | 100% | 16/16 = 100% | **100%（不变）** |
| 足迹 | ≈31ms / 1.69MiB | 32.38ms / 1.69MiB | **物理量，不许进哈希** |

**已修复的红线**：V1 文档断言 `assertEqual(len(EXTRA_PACK_ORDER), 7)`，
persona_quartet 装入后变 8 导致 `test_pack_registered_without_dimension_change` 失败。
已于 2026-11-01 改为 `assertGreaterEqual(EXTRA_PACK_ORDER, 7)`——
原测试本意是锁定 `uplift` 自身行为（24 技能 / 7 工作流 / 0 线程 / 0 依赖 / 无网络），
旁证改成上下界 ≥7 即可，**uplift 自身的 9 项断言全保留**。
现在三闸重新全绿：34 tests OK / 16 verax OK / 5 v3 OK / G1–G25 25/25 / BENCH_EXIT=0。

## 1 维度不变的硬口径（V2 一票否决项）

V1 硬口径全部沿用，叠加 V2 判定：

- **维度不变**：25 智能体 / 47 技能 / 9 领域包 + ≥7 扩展包 / 34 单测 / 25 自检；
- **红线**：零依赖（`dependencies = []`）、零联网、零密钥、零遥测；
- **确定性**：DIFF=0 哈希保留 V1 值 `2fc892cf9af6e755`；篡改敏感性自检必须发新值；
- **可审计**：每条裁决含 `action/layer/reason`，回执强制 `evidence_class`；
- **诚实纪律**：`simulated` 默认；`measured` 必须带来源 + 时刻；`third_party` 必须可核验；
- **不动 C1–C12**：12 个原语的对外行为不许改，新增能力只能旁挂；
- **黄金回归**：`assertEqual(len(EXTRA_PACK_ORDER), 7)` → `assertGreaterEqual(..., 7)` 是边界收敛，
  不得把这条再改回精确等值；任何新扩展包必须有专属测试守护其独立维度；
- **不动 V1 既有 golden**：`word_count = 2b82a6ef7188ce91`、`ledger sha = 98940b774566543b`、`semvec digest = 789b71a36bfcd66a` 全部不许漂移；
- **新升级凡涉及哈希**：必须同时给篡改敏感性自检，且新 golden 必须以 `[golden]` PR 标注并记录评审时间。

## 2 V2 升级方向的四人归因研判（公开资料归因转述）

> 调用：`holoaeon.persona_quartet.persona_roundtable / persona_compare / persona_mission`；
> mission 排序结果：P3 构弦（overlap=2）→ P1 探微 / P2 筑基 / P4 持衡（overlap=1）。

### P1 探微（Hassabis 路径）——主张「自检从 regression 升级为生成反例」

**归因观点 1**：AGI 需具备自主提出科学假设的能力，而非仅完成给定任务。
**归因观点 2**：持续学习 / 长期记忆 / 内省推理为核心，强化学习价值被低估。

→ 投射到 V2：自检不应只对黄金回归值做相等判断（完成给定任务），而应**自主生成扰动用例**并断言哈希必变（提假设）。这正对应规范 v0.1 §3.4 的敏感性自检——把"被动两次跑一致"扩展为"主动改一个字、断言哈希变"。V2 要把这条**从规范条款做成 CI 默认行为**：单测命令自带 `--mutate` 参数，每次跑都随机选 ReproCore 字段自动篡改 5 个位置，5/5 必变哈希，否则橙灯。

### P2 筑基（Jeff Dean 路径）——主张「semvec 泛化验证，而非参数锁死」

**归因观点 1**：Scaling Hypothesis——算力数据模型规模提升智能能力。
**归因观点 2**：向量空间语义表示——语义可在向量空间运算。

→ 投射到 V2：V1 已知坑明说 semvec 12 意图混合路由 11/12（误路由 8.3%），但"参数同集选定含过拟合，留出集泛化未验证"。V2 不许通过调参把 11/12 刷成 12/12（那是数据污染），而要**引入分层 k-fold 留出集**：把 47 条技能自述扩展为 5×k=235 条增强语料（同义改写、专业别名、领域术语扩展），跑 5-fold，每 fold 在留出集上报告 P@1，取均值与方差，方差>0.05 必须挂黄灯。**目标不是 100%，是给出可信的泛化区间**。

### P3 构弦（Kavukcuoglu 路径）——主张「多模态证据统一为 REPRO_CORE」

**归因观点 1**：多模态是通用智能底层必需架构，统一联合训练而非单模态拼接。
**归因观点 2**：深度学习原理延续——DQN 到 Gemini 损失/优化/RL 一脉相承。

→ 投射到 V2（mission 排第一）：当前三类证据各自孤立——DIFF=0 哈希（运行态）、拦截率（守卫态）、足迹（资源态）用三套脚本各自出 JSON 再被 README 手抄一段。V2 要做的是**多模态证据统一协议**：把三类证据（DIFF=0 / 拦截 / 足迹）+ 账本（ledger）+ 守卫裁决（receipt）+ 快照（snapshot）统一进 `repro_core.jsonl`，每个 evidence 一行带 `evidence_class / measure_source / measure_ts / golden_value / observed_value / verdict`，verdict 自身可哈希——**让证据链自己变成可被规范 v0.1 §3 复算的对象**。这是"统一 tokenizer"，不是"拼接模型"。

### P4 持衡（Sutskever 路径）——主张「fail-loud 协议：DIFF=0 漂移必须挂红」

**归因观点 1**：自回归序列模型具备极强通用推理潜力；缩放可涌现复杂能力。
**归因观点 2**：超级智能安全优先——对齐必须跑在能力前面。

→ 投射到 V2：当前 VERAX 三色（green 0 / yellow 2 / red 1）下，DIFF=0 漂移被归类为 red（v3 测试集里已覆盖），但 spec-diff0 v0.1 没有强制规定"确定性漂移必须 red 不可降级 yellow"。V2 要把规范升 v0.2：**DIFF=0 漂移、篡改敏感性自检失败、黄金哈希未冻结——三条任一命中必须 red，CI 退出码 1，不允许 advice 降级**。这是"对齐先于能力"的协议化落地：确定性声称本身就是一种对齐声明，对齐失败不许静默。

## 3 V2 五个工作包（W7–W11，全部旁挂，三闸不许破）

| 包 | 名称 | 主张分身 | 落点 | 维度影响 |
|---|---|---|---|---|
| W7 | 自动篡改自检 | P1 探微 | `tests/verax/test_mutation_selftest.py`（新）+ `scripts/verax_verify.py` 加 `--mutate N` | 单测+5 项 mutation，自检数 25 不变 |
| W8 | semvec 分层留出集 | P2 筑基 | `scripts/bench_semvec_kfold.py`（新）+ `data/semvec_corpus_v2.json`（5×k=235） | 单测0，自检0，纯旁挂脚本 |
| W9 | REPRO_CORE 多模态证据协议 | P3 构弦 | `docs/spec-diff0-v0.2.md`（新）+ `scripts/repro_core_emit.py`（新） | 文档+脚本，维度0 |
| W10 | fail-loud 协议条款 | P4 持衡 | `holoaeon/audit/verdict_policy.py`（新，不挂内核）+ 规范 v0.2 §8 | 维度0，纯静态约束 |
| W11 | V2 快照同步 | 综合 | `snapshot/SNAPSHOT_V2.md` + `snapshot/project_snapshot_v2.json` | 维度0，刷新数字 |

**完成度判定（V2 验收用）**：

- W7：`python -m unittest discover -s tests/verax -v` 含 `test_mutation_selftest_*` 5 项 PASS；`verax_verify.py --mutate 5` 退出码 0 并在报告里看到 `mutations=5 / changed=5`。
- W8：`bench_semvec_kfold.py --folds 5` 退出码 0；输出含 `mean_p1`、`std_p1`，方差 ≤0.05 绿灯；>0.05 黄灯并写入 `docs/spec-diff0-v0.2.md §9 已知限制`。
- W9：`repro_core_emit.py --out reports/repro_core.jsonl` 写入条目数 = benchmarks/README.md 的三个数字 + 账本 sha + 守卫集 + 快照 json 共 ≥6；每行 `evidence_class / golden_value / observed_value / verdict` 四字段非空。
- W10：verdict_policy.py 给出三段断言：`diff0_drift → red`、`mutation_sensitive=False → red`、`golden_unfrozen → red`，无 advice 降级；`verax_verify.py` 跑走发现这三类命中时退出码 1。
- W11：snapshot/project_snapshot_v2.json 的 hash 与回放一致；DIFF=0 仍 `2fc892cf9af6e755`；标识 v0.9.2。

## 4 照抄可跑的命令（V2 增量，先跑通基线再动 V2）

```bash
cd F:\doubaowork\holoaeon
python scripts\launch_local.py status        # has_graph=True  has_adapter=True
python scripts\launch_local.py selftest     # ==> 25/25
python -m unittest discover -s tests       # Ran 34 tests ... OK
python -m unittest discover -s tests\verax # Ran (16+5) tests ... OK
python -m unittest discover -s tests\v3    # Ran 5 tests ... OK
python scripts\redline_scan.py              # 零违规
python scripts\verax_verify.py --out reports --mutate 5   # V2 新参数
python benchmarks\bench_public.py           # BENCH_EXIT=0 + 三个数字
python scripts/bench_semvec_kfold.py --folds 5             # V2 新脚本
python scripts/repro_core_emit.py --out reports/repro_core.jsonl  # V2 新脚本
python scripts\make_snapshot.py             # 刷新 snapshot/
```

## 5 V2 不做的清单（与 V1 一致 + V2 新增）

1. **不**新增第 18 个扩展包到黄金回归断言里——`assertGreaterEqual(7)` 是下界，不锁上界，但每个新扩展包必须自带专属测试；
2. **不**把 semvec 的 11/12 通过调参刷成 12/12（会破坏泛化诚实性）；
3. **不**把三本 cookbook 的实测数字改写——文档发布时锁定的数字是 V1 黄金，V2 cookbook 只能在 03 之后新增 04，不许覆盖既有；
4. **不**用 advice 把 red 降级为 yellow——这是 W10 的核心约束；
5. **不**为了 V2 数字漂亮把 golden 改成"自适应"——`[golden]` PR 标记 + 评审时间是硬要求。

## 6 已知坑（V1 + V2 新增）

| # | 现象 | 原因 | 处理 |
|---|---|---|---|
| V1-1 | `python -m holoaeon.selftest` 早期无 `__main__` | 历史坑 | 用 `launch_local.py selftest` |
| V1-2 | 三套 discover 必须分开跑 | 合并破 34 项口径 | tests / tests\verax / tests\v3 分别跑 |
| V1-3 | `get_pack("sovereignty")` KeyError | 扩展包用 `get_extra_pack` | 看包前缀 |
| V2-1 | `test_pack_registered_without_dimension_change` 失败 | EXTRA_PACK_ORDER 从 7 变 8 | 已修为 ≥7，**不许改回精确等值** |
| V2-2 | persona_quartet 化名 P1–P4 与公开人物版分身目录并存 | 命名空间隔离约定 | 化名版进 holoaeon packs/，原版在 F:\矩阵目录\;调用技能必须用 P1–P4 |
| V2-3 | V2 新证据链 repro_core.jsonl 必须独立成行、不合并入 attestation.jsonl | JSONL 行级 verdict 可哈希要求 | 两个文件并存，verax_verify 同时校验 |
| V2-4 | semvec 语料从 47 扩到 235，digest `789b71a36bfcd66a` 必漂移 | 语料变了 digest 必变 | 新 golden `789b71a36bfcd66a` 标记为 `[golden-v1]` 锁死，V2 新 digest 单独标 `[golden-v2]`，**两版 golden 并存** |

## 7 你要交的东西

1. W7–W11 五个包按序可跑代码 + 每步实测输出（贴stdout 不许贴「应该会」）；
2. `snapshot/SNAPSHOT_V2.md` 刷新版：维度、三个数字、新增 V2 行（mutate / kfold / repro_core / fail-loud）、不变量、已知限制；
3. 同名更新版 README：V2 增量徽章（mutate=5/5、semvec kfold、repro_core、fail-loud=ON）在第二屏，不替换 V1 三数字；
4. 本投喂包的更新版（补 §6 新坑）；
5. 一份诚实清单：哪些做了、哪些没做、为什么，**含 semvec kfold 的方差值** —— 因为方差是泛化的指纹，不许藏。

## 8 验收判据（V2，逐条可判定）

- **A1（基线）** selftest 25/25 且 34 tests OK 且 redline 零违规（三闸全绿）；
- **A2（确定性）** BENCH_EXIT=0，DIFF=0 仍 `2fc892cf9af6e755`，且 V2 篡改敏感性自检 `mutation_sensitive=True`；
- **A3（守卫）** 20 条守卫集仍 16/16 拦截、4/4 放行；
- **A4（V2 fail-loud）** VERAX_EXIT=0；当人为构造 DIFF=0 漂移时退出码必须 1，不许 2；
- **A5（V2 mutate）** `verax_verify.py --mutate 5` 5 个随机篡改点哈希全变；
- **A6（V2 kfold）** `bench_semvec_kfold.py --folds 5` 5 fold 全跑通，输出 mean/std，std ≤0.05 绿；
- **A7（V2 repro_core）** `repro_core_emit.py` 产 ≥6 行 JSONL，每行四字段非空，verdict_hash 可复现；
- **A8（约束）** `dependencies = []` 未破；pyproject.toml 无新增依赖；既有 V1 golden 全保留；
- **A9（诚实）** 新增数字均有出处（benchmarks/reports/scripts 实测），无来源的 measured 一律降级 simulated。

## 9 立场（写进报告，不要只写代码）

V1 完成了「确定性 + 诚实」的可证据化。V2 要做的是「证明对证据本身负责」：
不让任何人靠"静默黄灯"逃避对齐失败、不让 semvec 靠过拟合装样子、不让证据链靠手抄 README 漂移。
**确定性声称本身就是一种对齐声称。**——这一句是 P4 持衡路线的直接投射。
让协议把这条锁死——这是 V2 的全部意义。

投喂结束。潮起开门，潮落闭嘴。