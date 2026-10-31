# HoloAeon 项目快照 V2（文档 0.9.2 / 运行态 0.9.1）

> 给其他智能体：读完这一页即可接手优化，不必先读全部源码。
> 数字现算自磁盘与内核，机器可读版见 `snapshot/project_snapshot_v2.json`。
> 全部条目 `evidence_class=simulated`：仿真 ≠ 证明，碳基终裁。

## 一 · 定位

零依赖、默认离线、确定性、带回执的多智能体认知框架：12 个原语（C1–C12） + 8 层语义守卫 + 手写 HRR 超向量 + 领域/扩展双层包体系。

## 二 · 维度（硬口径，V2 未变）

| 项 | 值 |
|---|---|
| 运行态版本 | 0.9.1（HOLOAEON-MATRIX-0.9.1） |
| 文档版本 | 0.9.2（仅升级包与文档） |
| 智能体 / 技能 / 工作流 | 25 / 47 / 9 |
| 领域包 / 扩展包 | 9 / 8（≥7 下界） |
| 原语 | 12（C1–C12 未动） |
| 单测（三套分开跑） | 34 / 21 / 5 |
| 自检组 | 25（G1–G25） |
| 代码量 | holoaeon/ 44 文件 / 12212 行 |

## 三 · 三指标（V1 黄金，不许漂移）

| 指标 | 值 |
|---|---|
| DIFF=0 | `2fc892cf9af6e755`（equal=True） |
| 篡改后哈希 | `f42c8229ee5acd73`（sensitive=True） |
| 拦截率 | 16/16（放行 4/4） |
| 足迹 | 32.58ms / 1.69MiB（物理量，不进哈希） |

## 四 · V2 新增四行（第二屏徽章来源）

| 项 | 值 | 出处 |
|---|---|---|
| mutate | 5/5 全变（`sensitive=True`） | `scripts/verax_verify.py --mutate 5` |
| semvec kfold | mean=0.9957 / std=0.0085（folds=5，limit 0.05） | `scripts/bench_semvec_kfold.py` |
| repro_core | 10 行，全绿=True，sha16=`14873af555385549` | `reports/repro_core.jsonl` |
| fail-loud | ON（3 条硬红线，不可降级） | `holoaeon/audit/verdict_policy.py` |

## 五 · semvec 语义通道（披露，不设目标值）

| 项 | 值 |
|---|---|
| 意图 / 词表 / 维度 | 12 / 334 / 32 |
| 基线 / 语义 / 混合 | 0.8333 / 0.8333 / 0.9167 |
| 语料 digest (v1) | `789b71a36bfcd66a` |
| 跨词汇锚点（12 意图） | {'hybrid_correct': 11, 'hybrid_rate': 0.9167, 'intents': 12} |

## 六 · REPRO_CORE 证据链（行级可哈希）

```
diff0_hash               pass   a9e62d66c664b385
mutation_sensitivity_v1  pass   325d28962c42e2d4
guard_block              pass   b4b313caf56181ad
guard_allow              pass   7c95f8f4d32b4528
word_count_golden        pass   27a1929a3906e700
ledger_sha               pass   462d7e6f18540d48
semvec_digest_v1         pass   dd63cbe1463cf200
mutation_selftest_v2     pass   f7f68e44f49b26e7
semvec_kfold_std         pass   5bed5676e3bccfea
footprint                info   275f0d889f37e2ee
```

## 七 · 不变量

- 维度不变：25 智能体 / 47 技能 / 9 领域包 / ≥7 扩展包（现 8）/ 34 单测 / 25 自检
- 零依赖 dependencies=[]；零联网；零密钥；零遥测
- DIFF=0 黄金 2fc892cf9af6e755 不许漂移；V1 golden 全保留
- C1–C12 对外行为不许改；新增能力只能旁挂
- assertGreaterEqual(EXTRA_PACK_ORDER, 7) 不许改回精确等值

## 八 · 已知限制

- kfold 5 折是问法风格分层，std 读作风格敏感度，不是泛化能力
- 235 条语料含规范术语导致 P@1 虚高；跨词汇以 12 意图 11/12 为准
- 篡改自检默认抽样 5 点，非穷举
- 足迹属物理量：不进哈希，随机器浮动
- 两条稳定未命中：拆解任务、设计实验样本量，未调参复赛

## 九 · 入口命令（照抄可跑）

```powershell
python scripts\launch_local.py selftest
python scripts\launch_local.py demo
python scripts\verax_verify.py --mutate 5
python scripts\bench_semvec_kfold.py --folds 5
python scripts\repro_core_emit.py --out reports\repro_core.jsonl
python scripts\repro_core_emit.py --check reports\repro_core.jsonl
python benchmarks\bench_public.py
python scripts\gitee_publish.py --repo F:\doubaowork\holoaeon --branch main
```

## 十 · V2 五包落点

| 包 | 内容 |
|---|---|
| W10 | fail-loud verdict_policy.py + spec-diff0-v0.2 §8 |
| W11 | 本快照（SNAPSHOT_V2.md + project_snapshot_v2.json） |
| W7 | 自动篡改自检 mutation.py + --mutate 5（单测 +5） |
| W8 | semvec 分层留出 bench_semvec_kfold.py + corpus v2（235） |
| W9 | REPRO_CORE repro_core_emit.py + spec-diff0-v0.2 §7 |

## 十一 · 不做

- 不新增第 18 个扩展包去锁上界；每个新扩展包自带专属测试
- 不调参把 semvec 11/12 刷成 12/12
- 不改三本 cookbook 已发布实测数字
- 不用 advice 把 red 降成 yellow
- 不为数字漂亮把 golden 改成自适应

潮起开门，潮落闭嘴。

