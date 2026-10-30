# HoloAeon System README · v0.9.0

> 面向"取用者"而非"阅读者"的系统级说明：**这个系统现在是什么、怎么跑、能证什么、不能证什么。**
> 版本：`0.9.0` ｜ `HOLOAEON-MATRIX-0.9.0` ｜ `HOLOAEON-RUNTIME-0.9.0` ｜ 日期 2026-10-30
> 密令 **潮起开门，潮落闭嘴**

---

## 1. 系统形态

HoloAeon 是一个**零第三方依赖、离线可跑、确定性优先**的多智能体认知框架。它把自己隐喻为"生命体"，
每个器官都是一个可判定的模块：

| 器官 | 子系统 | 在代码里的落点 |
|---|---|---|
| 矩阵 | 智能体与知识单元拓扑（127 亚学科 × 10 槽 + 61 备用） | `packs/`、`data/taxonomy_127.json` |
| 心跳 | 全局时钟与存活探针 | `scheduler.py` |
| 皮肤 | 边界安全（权限 / 审计 / 门禁 / 不可逆确认） | `guard.py` |
| 经络 | 单元间语义通路与降级路由 | `bus.py` |
| 细胞骨架 | 全局协调与长期一致性 | `kernel.py`、`cluster.py` |
| 赫布协作场 | 协作权重（成功强化 / 无效衰减剪枝） | `graph.py` |
| 血统账本 | 来源 / 改写路径 / 哈希链 | `packs/*_pack.py`（各包内建审计） |
| METAB | 能力与知识进入系统的唯一受治理通道 | `packs/metab_pack.py` |
| NEPHRON | 认知容量与记忆代谢（只读观测 P0） | `packs/nephron_pack.py` |
| UPLIFT | 加固层：把前九个器官的漏洞焊死 | `packs/uplift_pack.py` |

v0.9.0 的新增不是"再长一个器官"，而是**修桥**：UPLIFT 把 v0.8.0 遗留的六个实证短板（S1–S6）连同
验证方式一起收进可判定技能，并在包外补了一条宿主模型桥。

## 2. 七包分工

九个领域包（`PACK_ORDER`，25 agents / 47 skills 不变）+ 七个横切扩展包（`EXTRA_PACK_ORDER`，
全部 0 agent、不加行、不加节点）：

| 扩展包 | 一句话职责 | 技能 | 工作流 |
|---|---|---|---|
| `sovereignty` | 认知主权：反标签、抗算法塑形 | 17 | 5 |
| `subdistill` | 亚学科蒸馏：16 域 → 127 亚学科 → 知识卡 | 15 | 7 |
| `omnilife` | 全域生活：衣 / 食 / 住 / 行 / 教 / SaaS | 18 | 6 |
| `omnicore` | 认知引擎重写：寻址不变式 / 纯函数心跳 | 20 | 6 |
| `metab` | 代谢治理：基因组准入 / 三态 / 三层授权 | 26 | 8 |
| `nephron` | 肾单位 P0：只读账本 + 回放 | 24 | 7 |
| `uplift` | U1–U6 加固 + 宿主桥 | 24 | 7 |

## 3. 维度不变式（系统级契约）

```
127 × 10 亚学科槽位 + 61 保留行        = 1331 行
127 × 855 亚学科节点 + 56 全局协调      = 108641 节点
```

七个扩展包的 `pack_summary()["addressing_unchanged"]` 全部返回 `True`；`uplift` 的
`skill_uplift_dimension_invariant` 把这条不变式做成可判定技能。**修桥不长新器官**：新增能力只能
落在既有 1331 × 108641 的格子里。

**它保护了哪条立场**：用户锁定的"产出物维度不变"。任何需要加行的设计在本系统里都是违约。

## 4. v0.9.0 的核心新增：U1–U6 加固

### 4.1 六个短板与六处修复

| 短板 | 实证 | 修复 | 验证 |
|---|---|---|---|
| S1 结果顺序非确定 | `_report()` 无排序；`_fft` 就地改入参 | 复合键 `(agent_id, 规范化记录)`；`a = list(a)` | 反转输入重排同序；变异版出现 12 种顺序 |
| S6 零 CI / 徽章口径不一 | 无 workflow；徽章 24/16 与实测 34/24 不符 | CI 矩阵 + 三模板 + 支持矩阵 + 徽章实测化 | `untested` 显式标注 |
| S3 A1/A2 恒 pending | `docs/nephron.md` L1/L2 | `scripts/measure_a1_a2.py` | A1 PASS + 变异 FAIL + A2 披露 |
| S5 中文召回弱 | `skill.py` 单字切分 | 字符 2-gram Dice + 词级 3-gram 兜底 | 两条用例 + 千次一致 |
| S2 无真实模型通路 | `model_adapter.py` 全 simulated | `bridges/`（包外） | echo 装配 + 远程门禁 + 无 Ollama 分支 |
| S4 十问未裁决 | `§12` | O-1～O-10 裁决表 + P1 细则 | 十条全 `chosen` |

### 4.2 五条铁律（违反即整包失败）

1. 零第三方依赖，仅标准库；
2. `holoaeon/` 内禁止 import 网络模块（红线扫描 34 文件零违规为证）；
3. 确定性优先，时间戳等外部因素归一化；
4. **没实测过的事不得写 pass / 通过**；
5. 每条关键设计标注"它保护了哪条立场"。

### 4.3 十处冲突与五处自身缺陷

`CONFLICTS` X1–X10（投喂稿与代码/口径的字面冲突，逐条给出择定与理由）、
`DEFECTS` M1–M5（本轮自己写错又自己抓到的：拼错 env 名、离线后端被自家门禁拒、回执缺 `ok`、
断言建立在错误 workload 前提、`platform.os` 偷懒）。全部登记在 `docs/uplift.md`。

## 5. 能力边界（明确不做的）

| 不做 | 理由 |
|---|---|
| 改 `Cluster` 线程语义 | U1 非目标；只减不确定性，不改并发模型 |
| 核心包联网 / 引入依赖 | 零依赖与离线是可选用的前提 |
| P1 真执行淘汰 | P1 只做判定细则，淘汰属 P2 |
| 用 echo / simulated 冒充 live | 这正是"不被 AI 忽悠"要防的事 |
| 新增 `after_summary` 字段 | 会破 41 字段冻结，改用 `summarized ∩ admitted` |
| 发布自动化 | 发行仍手动，zip + tag + SHA256SUMS 三重留痕 |

## 6. 快速取用

```bash
# 1) 取包（三选一）
git clone https://github.com/weideyouni/holoaeon.git
# 或 git checkout v0.9.0
# 或解压 releases/holoaeon_v0.9.0_20261030.zip

# 2) 全套自检（期望 24/24）
python -c "from holoaeon.selftest import run_all; r=run_all(verbose=True); assert r['ok']"

# 3) 单元测试与红线（期望 34 OK / 34 文件零违规）
python -m unittest discover -s tests -v
python scripts/redline_scan.py

# 4) A1/A2 实测（含变异证明）
python scripts/measure_a1_a2.py --runs 30 --write docs/nephron_a1_a2_evidence.json

# 5) 宿主桥（无 Ollama 会打印三行指引并退出 2，这是预期分支）
python bridges/quickstart.py --check

# 6) 只关心加固判定（零依赖，可单独拷走）
python -c "from holoaeon.packs.uplift_pack import pack_summary as p; print(p())"
```

## 7. 验证矩阵（v0.9.0 实跑）

| 项 | 结果 | 证据 |
|---|---|---|
| 单测 | **34 tests OK** | `python -m unittest discover -s tests` |
| 自检 | **24 / 24 组**（G1–G24） | `run_all()`，含 G24 uplift 43 条断言 |
| 红线 | **34 文件零违规** | `scripts/redline_scan.py` exit 0 |
| 示例 | `01`–`05` 全部 exit 0（`05` 为 `skip` 分支） | 逐个实跑 |
| A1 | **PASS**，`sha256=b48a0aa1f3743514`（off/full 同哈希，16 步） | `docs/nephron_a1_a2_evidence.json` |
| A1 变异 | 篡改一步输出 → **FAIL `diff_at_step=3`** | 同上 `mutation_proof` |
| A2 | full 中位 **11.5794 ms** / off **11.3708 ms** → **+1.83%**（runs=30） | 同上；不等阈值，只披露 |
| 桥（本机无 Ollama） | `--check` exit 2 + 三行指引；`05` skip exit 0；`echo` ok=True；远程门禁四分支正确 | `docs/bridges.md` |

**未实测（不得折叠成结论）**：A-U6-1（CI 三版本全绿，只能在 GitHub 侧产生）、
A-U2-3（真实 `mode="live"` 回执，本机无 Ollama）。见 `docs/support-matrix.md` 的 `untested` 格子。

## 8. 版本梯（只增不覆盖）

| 版本 | 主题 | 自检 |
|---|---|---|
| v0.9.0 | **UPLIFT U1–U6 加固 + 宿主桥** | 24/24 |
| v0.8.0 | NEPHRON 肾单位层 P0 | 23/23 |
| v0.7.0 | METAB 代谢层 | 22/22 |
| v0.6.0 | Omni-Core 认知引擎 | 21/21 |
| v0.5.0 | Omni-Life 全域生活 | 20/20 |
| v0.4.0 | 认知主权 + SD-Distill | 19/19 |

每个版本：`releases/holoaeon_v<ver>_<date>.zip` + `SHA256SUMS.txt` 一行 + `RELEASES.md` 一节 + git tag。
旧包一律保留，可独立解压、独立自检、独立运行。

## 9. 红线与科学边界

- 包内不联网、不起守护线程、不写盘（`pack_summary()` 的 `threads / timers / disk_writes / deps /
  api_calls` 恒为 0，`network` 恒为 `False`）；
- 桥在包外，允许联网；密钥只从环境变量读；审计只留哈希与计数；
- **隐喻不等于证明**：矩阵 / 心跳 / 皮肤 / 经络 / 赫布 / 肾单位 / 代谢都是工程隐喻，
  代码做到的是**确定性、可回放、可判定**，不是生物学；
- **仿真 ≠ 证明，碳基终裁**：所有判定最终由人验收，自动化只提供证据。

## 10. 许可证

内核 `holoaeon/` 采用 Apache-2.0；扩展包与认知主权矩阵采用 MIT，二者**不互相转嫁**。
第三方若只用扩展包的判定技能，可只取 `packs/*_pack.py` 与其对应文档。

## 11. 路线图

- **v0.9**（本版）——U1–U6 加固、宿主模型桥、A1/A2 实测化、O-1～O-10 裁决。
- **v0.10**——可插拔持久化后端与节点间总线传输。
- **v0.11**——声明式图 / 拓扑定义与包创作工具包。
- **v1.0**——API 冻结 + 文档完整 + 生产级 hook 闭环（届时 A1/A2 可由 `measured_with_scope`
  升为 `measured`，条件是 P0 的 writer 真正落在宿主侧）。

---

潮起开门，潮落闭嘴
