# HoloAeon · 一个带回执的确定性内核

```
DIFF=0 2fc892cf9af6e755 | 拦截 100% | 冷装配 ≈31ms / 峰值 1.69MiB
```

三个数字，随发版重跑，出处是 [benchmarks/README.md](benchmarks/README.md) 与
`benchmarks/results-0.9.1.json`。全部条目 `evidence_class=simulated`：仿真 ≠ 证明。

HoloAeon 是零依赖（`dependencies = []`）、默认离线、确定性、可审计的多智能体认知框架：
12 个正交原语（C1–C12）+ 8 层语义守卫 + 手写 HRR 超向量（1024 维，radix-2 FFT）+ 领域/扩展双层包体系。
你不需要读全部源码就能相信它——但它把「凭什么相信」写成了可以自己复跑的命令。

## 三个数字凭什么算数

| 指标 | 口径 | 反造假手段 |
|---|---|---|
| **DIFF=0** `2fc892cf9af6e755` | 16 步固定 workload 跑两次，各用全新内核，剔除 `ts/uptime/elapsed` 等物理量后对规范 JSON 求 sha256 前 16 位 | **篡改敏感性自检**：把任务原文改一个字，哈希变为 `f42c8229ee5acd73`。哈希不变即视为空转，判不通过 |
| **拦截 100%** | 20 条标准请求集：危险 5 / 越权 5 / 超限 3 / 失真 3 / 合法 4 | 合法 4 条必须全放行；只报拦截率不报放行率就是耍流氓 |
| **足迹 ≈31ms / 1.69MiB** | 进程内内核装配 + `tracemalloc` 峰值 | 明确标注「不是 OS 冷启动 import」，机器规格另列，不混进哈希 |

> 这三个数字来自一次真实的翻车：早期把未登记字段当物理量整段剔除，导致三色用例哈希全等
> （`9eb1936e9b55cb08`）。修法是把待测字段登记进分类表，并加篡改自检证明哈希真的对内容敏感。

## 十分钟上手（三本 cookbook，全部逐步实测）

| 编号 | 内容 | 实测证据 |
|---|---|---|
| [01](cookbooks/01_make_your_skill/README.md) | 做一个你自己的技能（`bmi_calc` 七步） | 路由 `0.20757`；提交 `bmi 22.86`；危险调用 `blocked` |
| [02](cookbooks/02_add_ledger_to_your_agent/README.md) | 给现有 Agent 加账本 + 单文件 HTML 视图 | 6 条记录 → 5,860 B；两次渲染 sha 一致 `98940b774566543b` |
| [03](cookbooks/03_offline_deploy_old_laptop/README.md) | 离线部署到 2GB 旧笔记本（含 Win7/10 差异） | `selftest 24/24`；`34 tests OK`；零次 `pip install` |

## 规范：确定性 Agent 运行时 v0.1

[docs/spec-diff0.md](docs/spec-diff0.md) 把「确定性」从项目特性升格成可被他方实现的开放协议：
DIFF=0 哈希协议、理由码族表、证据防漂移协议、`full / sampled / incompatible` 兼容性分级，
以及十条逐项可判定的自检清单。**本规范由 HoloAeon 项目发起，欢迎他方实现。**

## 快速开始

```powershell
cd F:\doubaowork\holoaeon
python scripts\launch_local.py status       # has_graph=True  has_adapter=True
python scripts\launch_local.py demo         # 内部总线 + 外部模型分流，末行 all_ok: True
python scripts\launch_local.py selftest     # ==> 24/24
python -m unittest discover -s tests        # Ran 34 tests ... OK
python scripts\verax_verify.py --out reports # 末行 VERAX_EXIT=0
python benchmarks\bench_public.py           # 三个数字 + BENCH_EXIT=0
```

## 项目快照（给其他智能体）

[snapshot/SNAPSHOT.md](snapshot/SNAPSHOT.md) 是一页可接手的快照：维度口径、三个数字、
13 条入口命令、7 条不变量、4 条明确不做、已知限制、目录骨架。
机器读版本在 `snapshot/project_snapshot.json`，由 `scripts/make_snapshot.py` 现算生成。

## 不变量（破了就不算 HoloAeon）

- **零依赖**：`pyproject.toml` 的 `dependencies = []`，只用 Python 标准库；
- **默认离线**：不开端口、不联网、不读密钥、不写遥测；
- **确定性**：DIFF=0 两次一致，且篡改自检通过；
- **可审计**：每条裁决含 `action/layer/reason`，回执强制 `evidence_class`；
- **安全边界**：L1–L8 八层守卫，20 条标准集拦截率 100%；
- **诚实纪律**：`simulated` 是默认档，`measured` 必须带来源与测量时刻；
- **维度不变**：25 智能体 / 47 技能 / 9 领域包 + 7 扩展包 / 34 单测 / 24 自检。

## 明确不做

- 不新增第 17 个领域包（治理包的边际收益已经递减）；
- 不去卷「重依赖 + 托管平台」的右下角（LangGraph / MetaGPT / CrewAI 的战场，进去必输）；
- 不把 `simulated` 写成实测；
- 不为了追 star 破坏零依赖与既有测试。

## 已知限制（先说清楚）

- 语义通道 `holoaeon/semvec.py`（PMI + 幂迭代截断 SVD，纯标准库）在 12 条意图上
  混合路由 9/12 正确：跨词汇同义（「患者数据统计」→ `basic_stats`）由错转对，
  但短词意图（样本量、周报）引入噪声。**未达到 ≤10% 误路由率的目标，如实披露。**
- 领域包产骨架不产成稿；账本可视化是确定性静态 HTML，不是托管平台。
- Apache-2.0 护不住功能，只护得住标准与证据；双许可决策留给构建者单独裁决。

## 目录

| 路径 | 说明 |
|---|---|
| `holoaeon/` | 核心包：12 原语 + `audit/`（VERAX）+ `packs/`（16 包）+ `semvec.py` |
| `benchmarks/` | 三个数字的唯一出处（`bench_public.py` + `results-*.json`） |
| `cookbooks/` | 三本实战教程 |
| `docs/` | `spec-diff0.md`（规范）、`cookbooks.md`（索引）、`VERAX.md`（可信层设计） |
| `scripts/` | `launch_local.py`、`verax_verify.py`、`ledger_view.py`、`make_snapshot.py` |
| `snapshot/` | 项目快照（md + json） |
| `tests/` | `34` 项基线 + `verax/` 16 项 + `v3/` 5 项 |

## 许可

Apache-2.0。护城河不靠许可证高墙，靠**空象限先发 + 可复算基准 + 开放规范署名**。
