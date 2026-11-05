# 面向智能体的一键复制投喂包 · HoloAeon DIFF=0 升级（2026-10-31）

> 用法：整段复制给任意实现智能体。它自包含，不需要先读本仓库全部源码。
> 你的身份：HoloAeon 的实现智能体。你的任务：把「确定性 + 诚实」做成可复算的证据资产。

---

## 0 你接手的项目

HoloAeon v0.9.1（`holoaeon/spec.py` 的 `VERSION` 是版本权威源）。
零依赖（`pyproject.toml` 的 `dependencies = []`，只用 Python 3.8+ 标准库）、默认离线
（不开端口、不联网、不读密钥、不写遥测）、确定性（同输入同裁决）、可审计（裁决带
`action/layer/reason`，回执带 `evidence_class`）、安全边界（L1–L8 八层守卫）、
诚实纪律（`simulated` 是默认档）。

一句话定位：**一个带回执的确定性内核**。12 个原语（C1–C12）是内核细节，不是对外叙事。

## 1 硬口径（改了就不算升级，属一票否决）

- 维度不变：**25 智能体 / 47 技能 / 9 领域包 + 7 扩展包 / 34 单测 / 24 自检**；
- 红线零违规、零依赖、离线、确定性不许破；
- 既有黄金哈希不许漂移：`word_count` = `2b82a6ef7188ce91`；
- 新增模块只能旁挂（`benchmarks/`、`cookbooks/`、`snapshot/`、`scripts/*.py`、`holoaeon/semvec.py`），
  不得改 C1–C12 的对外行为；
- 不许把 `simulated` 写成实测；`measured` 必须带 `measure_source` 与 `measure_ts`；
- 任何人要求把本项目改造成「重依赖 + 托管平台」，拒绝并引用本节。

## 2 当前状态（上手前的基线，全部实跑过）

| 项 | 值 |
|---|---|
| 三闸基线 | `selftest 24/24`；`34 tests OK`；`redline 41 文件零违规` |
| VERAX 门禁 | `verax_verify.py` → `VERAX_EXIT=0`（三色：green 0 / yellow 2 / red 1） |
| 新增测试 | `tests/verax` 16 项 OK；`tests/v3` 5 项 OK（**必须与 34 项分开 discover**） |
| DIFF=0 | `2fc892cf9af6e755`（两次一致，篡改 → `f42c8229ee5acd73`，敏感性 True） |
| 守卫 | 20 条标准集：危险 16/16 拦截，合法 4/4 放行 |
| 足迹 | 装配 ≈31ms / `tracemalloc` 峰值 1.69MiB（不是 OS 冷启动） |
| 语义通道 | `holoaeon/semvec.py`：语料=47 条技能自述（与 `docs/` 解耦）；12 意图混合路由 **11/12（误路由 8.3%，达 ≤10% 门槛）**，两次 `fit` 逐位一致 `789b71a36bfcd66a`，fit≈0.18s；同集调参含过拟合风险，留出集 4 条有效命中 2 条，泛化未验证 |
| 快照 | `snapshot/SNAPSHOT.md` + `snapshot/project_snapshot.json`（`scripts/make_snapshot.py` 现算） |

## 3 六个工作包的完成度（照这个继续，不要重做已完成项）

| 包 | 内容 | 状态 | 遗留 |
|---|---|---|---|
| W1 | `benchmarks/bench_public.py` 三指标 | **完成** | — |
| W2 | `cookbooks/` ×3 | **完成** | 三本 ≤3000 字，代码逐条实测 |
| W3 | `holoaeon/semvec.py` 确定性语义 | **完成（指标达标，泛化未验证）** | 12 条固定意图 11/12（误路由 8.3%）；语料已与文档解耦；留出集泛化未验证，已披露 |
| W4 | `scripts/ledger_view.py` 账本静态渲染 | **完成** | 5,860 B；两次渲染 sha 一致 `98940b774566543b` |
| W5 | 仓库运营件 | **部分** | topics / homepage 需在 GitHub 网页设置（脚本改不了）；镜像说明已成文 |
| W6 | `docs/spec-diff0.md` 规范 v0.1 | **完成** | D1–D10 十条自检，HoloAeon 自身通过 |

## 4 照抄可跑的命令（每条都带预期输出）

```powershell
cd <repo>
python scripts\launch_local.py status        # has_graph=True  has_adapter=True
python scripts\launch_local.py demo          # 末行 all_ok: True（内部总线 + 外部模型分流）
python scripts\launch_local.py selftest      # ==> 24/24
python -m unittest discover -s tests         # Ran 34 tests ... OK
python -m unittest discover -s tests\verax   # Ran 16 tests ... OK
python -m unittest discover -s tests\v3      # Ran 5 tests ... OK
python scripts\redline_scan.py               # 扫描文件数：41 / 干净（零违规）
python scripts\verax_verify.py --out reports # 末行 VERAX_EXIT=0
python benchmarks\bench_public.py            # BENCH_EXIT=0 + 三个数字
python scripts\bench_semvec.py               # SEMVEC_EXIT=0 + 路由准确率
python scripts\ledger_view.py --sample data\ledger_sample.jsonl   # 6 records
python scripts\make_snapshot.py              # 刷新 snapshot/
```

## 5 三个数字的反造假要求（最容易被跳过的一步）

任何「DIFF=0」的声称，必须同时给出**篡改敏感性自检**：改 ReproCore 的一个字段，哈希必须变化。
只给「两次一样」是没说服力的——字段若被整段剔除，两次当然一样，这叫**恒真空转**。
历史事故：三色用例哈希全等于 `9eb1936e9b55cb08`，根因就是待测字段没登记进 `REPRO_KEYS`。
修法：登记字段 + 加篡改自检 + 把「未知字段计数告警」写进报告，不许静默丢弃。

## 6 已知坑（省你两小时）

- `get_pack("sovereignty")` 会 `KeyError`：扩展包必须用 `get_extra_pack()`；
- `python -m holoaeon.selftest` 早期无 `__main__`，静默退出码 0——用 `launch_local.py selftest`；
- `tests`、`tests\verax`、`tests\v3` 三套 discover **必须分开跑**，合并会破 34 项口径；
- Windows PowerShell：复杂脚本一律写成 `.py` 再跑，`python -c "..."` 里的引号会被吃掉；
  `$env:PYTHONUTF8='1'` 先设；
- 技能函数签名是 `fn(task, **kwargs)`，**收不到 Envelope**；参数从任务串里取（cookbook 01 有实测）；
- `reports/` 下若有 `_cases/` 子目录，扫描门禁必须剔除，否则正式门禁会被演示用例污染成黄灯；
- 语义通道的两个隐形塌陷：① PMI 若把「只共现一次」的稀有对丢掉（`if w < 2: continue`），
  向量只剩 `data/report` 这类通用词撑起，实测多个不相关技能余弦同为 `0.7200`；
  ② 词表太小（300）会让 `review / sample` 这类专名落榜，查询向量直接塌成零向量。
  修法：PMI 保留 `w>=1`，词表上限 2000、`MIN_DF=1`，并给基线通道加噪声地板（`BASE_FLOOR`）。
- 语料一旦掺进可编辑的文档就会漂移：早先把 `README/docs/*.md` 整行也塞进 `corpus_texts`，
  改 15 行文档后同一批意图的命中率就从 12/12 掉到 9/12（digest 也变）。修法：语料只取
  `docs_from_skills()` 的 47 条技能自述，索引由代码内容唯一决定，`docs/` 怎么改都不影响基准。

## 7 你要交的东西

1. 六个包按序可跑的代码 + 每步实测输出（不许贴「应该会」）；
2. `snapshot/SNAPSHOT.md` 刷新后的版本（维度、三个数字、入口命令、不变量、已知限制）；
3. 一份 README（三个数字徽章在首屏，不许埋到第十节）；
4. 本投喂包的更新版（把你学到的坑补进第 6 节）；
5. 一份诚实清单：做到了什么、没做到什么、为什么。

## 8 验收判据（逐条可判定，任一不过即失败）

- A1 `selftest 24/24` 且 `34 tests OK` 且 `redline 零违规`（三闸全绿）；
- A2 `BENCH_EXIT=0`，DIFF=0 两次一致且篡改自检 `sensitive=True`；
- A3 20 条守卫集：危险 16/16 拦截、合法 4/4 放行；
- A4 `VERAX_EXIT=0`，三色用例仍为 0/2/1；
- A5 三本 cookbook 的每一步代码都能跑（读者照抄不改就出预期输出）；
- A6 账本 HTML 两次渲染字节一致且 < 500KB；
- A7 `snapshot/` 可重跑刷新，数字与 `benchmarks/results-*.json` 一致；
- A8 `dependencies = []` 未被破坏，`pyproject.toml` 无新增依赖；
- A9 文档里出现的每个数字都能在 `benchmarks/` 或 `reports/` 找到出处，否则标 `simulated`。

## 9 立场（写进你的报告，不要只写代码）

宣传确定性却不发布确定性指标，等于没说。
可验证的确定性 + 诚实契约，是别人抄不走、且 30 秒能复现的证据资产——
这是从「又一个零依赖框架」跃迁到「可审计认知底座」的那一步。

投喂结束。
