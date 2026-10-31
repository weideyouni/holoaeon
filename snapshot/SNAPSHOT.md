# HoloAeon 项目快照（0.9.1）

> 给其他智能体：读完这一页你就能接手优化，不需要先读全部源码。
> 所有数字现算自磁盘与内核，出处见 `snapshot/project_snapshot.json`。

## 一 · 这是什么

HoloAeon 是一个**零依赖、默认离线、确定性、带回执**的多智能体认知框架：
12 个正交原语（C1–C12）+ 8 层语义守卫 + 手写 HRR 超向量 + 领域/扩展双层包体系。
一句话定位：**一个带回执的确定性内核**。

## 二 · 维度（不许改的硬口径）

| 项 | 值 |
|---|---|
| 版本 | 0.9.1（HOLOAEON-RUNTIME-0.9.1） |
| 核心包 | 25 智能体 / 47 技能 / 9 工作流 |
| 领域包 | 9 个（writing / literature / research / data / growth / business / quant / optimization / gaoyi） |
| 扩展包 | 7 个（sovereignty / subdistill / omnilife / omnicore / metab / nephron / uplift） |
| 全装后 | 25 智能体 / 191 技能 |
| 代码量 | holoaeon/ 41 文件 / 11675 行 |

## 三 · 三个数字（证据入口）

| 指标 | 值 | 出处 |
|---|---|---|
| DIFF=0 | `2fc892cf9af6e755`（一致=True，敏感性=True） |
| 守卫拦截率 | 100%（合法 4/4 放行） |
| 足迹 | 31.66 ms / 1.69 MiB |

## 四 · 语义通道实测（披露，不设目标值）

| 项 | 值 |
|---|---|
| 意图数 / 词表 / 维度 | 12 / 334 / 32 |
| 基线正确 / 混合正确 | 10 / 11 |
| 两次 fit 逐位一致 | True |
| fit 耗时 | 185.49 ms |

## 五 · 入口命令（照抄可跑）

```powershell
python scripts/launch_local.py status
python scripts/launch_local.py demo
python scripts/launch_local.py run "统计字数：HoloAeon 是零依赖的确定性多智能体认知框架。"
python scripts/launch_local.py hotplug optimization
python scripts/launch_local.py selftest
python -m unittest discover -s tests
python -m unittest discover -s tests\verax
python -m unittest discover -s tests\v3
python scripts/redline_scan.py
python scripts/verax_verify.py --out reports
python benchmarks/bench_public.py
python scripts/bench_semvec.py
python scripts/ledger_view.py --sample data/ledger_sample.jsonl
```

## 六 · 不变量（破了就不算 HoloAeon）

- 零依赖：pyproject.toml 的 dependencies = []，只用 Python 标准库
- 默认离线：不开端口、不联网、不读密钥、不写遥测
- 确定性：DIFF=0 哈希两次一致，且篡改敏感性自检通过（否则视为空转）
- 可审计：每条裁决含 action/layer/reason，回执强制 evidence_class
- 安全边界：L1–L8 八层守卫，20 条标准集拦截率 100%
- 诚实纪律：simulated 是默认档，measured 必须带来源与测量时刻
- 维度不变：25 智能体 / 47 技能 / 9 领域包 + 7 扩展包 / 34 单测 / 24 自检

## 七 · 明确不做

- 不新增第 17 个领域包
- 不为追 star 抄编排框架（LangGraph/MetaGPT/CrewAI 的战场不进来）
- 不把 simulated 写成实测
- 不破坏 dependencies=[]、不引入网络、不破既有单测与自检

## 八 · 如何加入优化

1. 读 snapshot/SNAPSHOT.md 的「不变量」与「入口」，先在本地跑通 3 条命令
2. 改动前用 tests\ + selftest + redline 三闸确认基线全绿
3. 任何 DIFF=0 相关改动必须同时给篡改敏感性自检
4. 文档里的数字必须能在 benchmarks/results-*.json 找到出处，否则标 simulated

## 九 · 已知限制（先看这里，别重复踩）

- semvec 语义通道：语料只取 47 条技能自述（与 docs/ 解耦，改文档不漂移）；12 条固定意图混合路由 11/12 = 91.7% 误路由 1/12（同集调参，含过拟合风险）；留出集 6 条中 2 条期望名不存在，余 4 条命中 2 条 —— 泛化未验证
- 领域包产骨架不产成稿；账本可视化是静态 HTML，不是托管平台
- Apache-2.0 不保护功能，只保护标准与证据；双许可决策留给构建者

## 十 · 目录骨架

| 路径 | 类型 | 说明 |
|---|---|---|
| `.github/` | dir | 3 项 |
| `.gitignore` | file | 788 B |
| `AGENT_FEED_DIFF0_20261031.md` | file | 8089 B |
| `AGENT_FEED_VERAX_20261031.md` | file | 9807 B |
| `ALGORITHM.md` | file | 6980 B |
| `CHANGELOG.md` | file | 29457 B |
| `CODE_OF_CONDUCT.md` | file | 1630 B |
| `CONTRIBUTING.md` | file | 1759 B |
| `DELIVERY_VERAX_20261031.md` | file | 2617 B |
| `LICENSE` | file | 11541 B |
| `README.md` | file | 39142 B |
| `README.zh-CN.md` | file | 16771 B |
| `README_DIFF0_20261031.md` | file | 6229 B |
| `README_EMPOWER_20261031.md` | file | 10167 B |
| `README_MANIFESTO_v0.9.1.md` | file | 11420 B |
| `README_VERAX_20261031.md` | file | 5565 B |
| `SYSTEM_README.md` | file | 13233 B |
| `SYSTEM_README_v0.5.0.md` | file | 11697 B |
| `SYSTEM_README_v0.6.0.md` | file | 12692 B |
| `SYSTEM_README_v0.7.0.md` | file | 15369 B |
| `SYSTEM_README_v0.8.0.md` | file | 14153 B |
| `SYSTEM_README_v0.9.0.md` | file | 9167 B |
| `benchmarks/` | dir | 4 项 |
| `bridges/` | dir | 6 项 |
| `cookbooks/` | dir | 3 项 |
| `data/` | dir | 3 项 |
| `docs/` | dir | 21 项 |
| `examples/` | dir | 7 项 |
| `holoaeon/` | dir | 19 项 |
| `pyproject.toml` | file | 2179 B |
| `releases/` | dir | 10 项 |
| `reports/` | dir | 14 项 |
| `scripts/` | dir | 28 项 |
| `snapshot/` | dir | 2 项 |
| `tests/` | dir | 3 项 |

--
快照由 `scripts/make_snapshot.py` 生成，重跑即可刷新；不含只读机密。
