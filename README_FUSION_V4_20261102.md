# HoloAeon · V4 冷热插拔赋能升级

> 本文是 V4 唯一入口；主 `README.md` / `README.zh-CN.md` 顶部已加指针，五地同步回执见 `vector-sea\_holoaeon_v4_five_site_receipt_20261102.json`。

> **装一个扩展包，门禁不变，能力可插拔。**
> 不合并引擎、不合并编号、不动维度锁：`25 agents / 47 skills / 9 packs` 仍是那个 `25/47/9`。

中文 | [English quickstart ↓](#english-quickstart)

---

## 这是什么

HoloAeon 是一个**可审计的多智能体编排内核**：九个领域包（写作 / 文献 / 研究 / 数据 / 增长 / 商业 / 量化 / 优化 / 高医）提供 47 个确定性技能与 25 个角色，八个横切扩展包叠加认知主权、蒸馏、生活域、全息纪元、代谢、肾单位、补齐短板与四人数字分身。

**V4 新增第 10 个扩展包 `fusion_upgrade`**，把"冷热插拔"和"内外融合协议"从文档变成**可执行、可验收入口**：

- **冷插**（九个领域包）：启动期整体装载，运行期**禁止卸载**，因为维度锁靠它撑着。
- **热插**（10 个扩展包）：任意时刻可装可卸，回滚点就是卸载本身。
- **内部融合协议**：信封 → 皮肤八层守卫 → 消息总线 → 心跳节拍 → 技能匹配 → 端到端提交，六步各给证据。
- **外部融合协议**：只做模型后端路由决策，**零网络调用**，回执一律 `simulated`。
- **两仓契约 v1**：与中西医融合康复工程（ivsa）之间只交换一条 JSON 回执，不搬代码、不共享编号。
- **十二批次计划**：每批九字段、判据可跑、禁形容词。
- **项目快照**：一条命令导出，供其他智能体读取与继续优化。

---

## 一句话升级

```bash
git clone https://github.com/weideyouni/holoaeon.git && cd holoaeon && python scripts/fusion_local.py fuse
```

看到 `内部协议：True` / `外部协议：True` / `网络调用：0`，就是升级完成。**其他一切维度不变。**

---

## 快速开始

```powershell
# Windows（编码先设，否则中文乱码）
$env:PYTHONIOENCODING="utf-8"; [Console]::OutputEncoding=[Text.Encoding]::UTF8
cd holoaeon

python scripts/verify_fusion_upgrade.py     # 融合包自检 17/17
python scripts/fusion_local.py status       # 冷热清单 + 现算锁值 25/47/9
python scripts/fusion_local.py fuse         # 内外协议全量演练
python scripts/fusion_local.py roundtrip fusion_upgrade   # 热插拔往返
python scripts/fusion_local.py contract     # 契约 / 六机制 / 12→17 通道
python scripts/fusion_local.py plan B2b     # 单批详情
python scripts/fusion_local.py snapshot out.json          # 项目快照
```

零第三方依赖：`dependencies = []`，`pip install` 零次。

---

## 架构：四层两桥

```mermaid
flowchart TB
  subgraph L1["L1 发现层 · HoloAeon (Apache-2.0)"]
    A["47 skills / 25 agents<br/>九领域包（冷插）"]
    M["六机制：心跳 · 骨架 · 皮肤 · 语义 · 赫布 · 经络"]
  end
  subgraph L2["L2 映射层 · rehab_bridge（只读映射）"]
    B["六机制 1:1 对照 6 行<br/>12→17 通道显式映射（待办 5）"]
    V["词表分域：通用闸 10 token 固定<br/>医学 24E14+12E13 按域注入"]
  end
  subgraph L3["L3 执行层 · ivsa (MPL-2.0 + CC-BY-NC-SA-4.0)"]
    C["21 组自检 · 70 体心跳 · 3×4 骨架<br/>L1–L8 皮肤双轨 · 语义十模块"]
  end
  A -->|"桥① JSON 契约 v1（6 必填+4 可选）"| B
  B -->|"桥② 同一契约（单向只读）"| C
  D["第 10 扩展包 fusion_upgrade<br/>manifest · swap · protocol · contract · plan · snapshot"]
  D -.旁挂.-> L1
```

桥上只走**一条回执**，不走代码、不走编号、不走状态。回执必带 `contract_id` + `seal`，两次调用 `seal` 必须相等。

---

## 门禁（改动后必跑，全绿才算没破维度）

| 门禁 | 命令 | 期望 | 本轮实测 |
|---|---|---|---|
| 维度锁 | `python scripts/v3_gate.py --json reports/gate.json` | 32/32，A1=25/47/9 | ✅ 32/32 |
| 单元测试 | `python -m unittest discover -s tests` | 68 OK | ✅ 68 |
| 启动自检 | `python scripts/launch_local.py selftest` | 25/25 | ✅ 25/25 |
| 技能矩阵 | `python scripts/verify_skill_matrix.py` | 17/17 | ✅ 17 |
| 红线扫描 | `python scripts/redline_scan.py` | 零违规 | ✅ 71 文件 0 违规 |
| 融合包 | `python scripts/verify_fusion_upgrade.py` | 17/17 | ✅ 17 |
| 确定性黄金 | `python scripts/repro_core_emit.py` | `2fc892cf9af6e755` / `f42c8229ee5acd73` | ✅ `fails=[]` |

---

## V2.0 十二批次

`B0 基线冻结 → B1a 契约字段 → B1b 同参互认 → B2a 六机制映射 → B2b 12→17 + 词表分域 → B3 用途分类 → B4 康复域试点 20 例 → B5 语义 19→≥60 → B6 记忆与流量 → B7 分批准入 → B8 双仓同步 → B9 收口`

合计 **15 人天**；**不许跨批并行**：一批未全绿，不许开下一批。台账见 `data/十二批台账.csv`。

---

## 契约 v1（两仓唯一合法交换形态）

| 必填 | `contract_id` · `source` · `target` · `skill` · `mechanism` · `lane` |
|---|---|
| 可选 | `payload` · `nonce` · `budget` · `note` |
| 枚举 | `mechanism` ∈ 六机制；`lane` ∈ `read` / `write` |
| 纪律 | 校验失败即退出码 1；跨仓默认 `read`；回执必带 `mode=simulated` |

---

## 六护城河

零依赖 · 离线（无网络/无密钥/无遥测） · 确定性（两次同哈希 + 篡改敏感性） · fail-loud（失败退出码 1） · 证据链（可复算） · 稀疏逻辑拓扑（1331×1331 永不预分配）

---

## 医学红线（与康复域协作时一个字不改）

零剂量；C0 不写成疗效；L4/L5 禁外推；急症 E14 转 120；三场卡带物理参数且电场卡全轮 gap、禁 rTMS 顶替；一切跨域回执标 `simulated`。仿真 ≠ 证明，**碳基终裁**。

---

## 目录结构（新增部分）

```
holoaeon/
├── holoaeon/
│   ├── fusion_upgrade/          # 新增：冷热插拔 + 内外融合协议
│   │   ├── manifest.py          # 冷/热清单（现算，每行带回滚点）
│   │   ├── swap.py              # 装 / 卸 / 往返探针
│   │   ├── protocol.py          # 内部六步 + 外部离线路由
│   │   ├── contract.py          # 契约 v1 + 六机制 + 12→17 映射
│   │   ├── plan.py              # 十二批次（九字段可校验）
│   │   ├── snapshot.py          # 项目快照
│   │   └── selftest.py          # 17 项
│   └── packs/fusion_upgrade_pack.py   # 第 10 扩展包：8 技能 / 2 角色 / 1 工作流
└── scripts/
    ├── fusion_local.py          # 本地操作台
    └── verify_fusion_upgrade.py # 验收入口（--json 可机读）
```

---

## 已知限制（如实写，不藏）

- 热卸载后调度器 `watchers_left` 非 0：调度器 watch 列表无公开移除接口，残留的是对象引用，不参与技能路由。
- 语义技能原 19 个（六机制里最薄）；B5 已扩到 60 条并落满 ivsa 十模块（检索 16 条偏重，成因与 `module_basis` 已逐条登记在 B5 票据）。
- ivsa 侧 v1.2 插件（默认关闭）尚未落地；本轮只改 HoloAeon 一个仓。
- 快照内 `gates_last_known` 是上次已知值，接收方必须按 `recheck` 现场复跑。

---

## 许可

HoloAeon 本体 **Apache-2.0**。与 ivsa（代码 MPL-2.0 / 内容 CC-BY-NC-SA-4.0）**只经契约交换，不互相拷贝代码**，因此不存在许可混用。

---

## English quickstart

```bash
git clone https://github.com/weideyouni/holoaeon.git && cd holoaeon
python scripts/verify_fusion_upgrade.py      # 17/17
python scripts/fusion_local.py fuse          # internal + external protocol, 0 network calls
python scripts/fusion_local.py status        # 25 agents / 47 skills / 9 packs — unchanged
```

**One line:** install one extra pack, keep every dimension, make capability pluggable. `evidence_class=simulated`; simulation ≠ proof.

---

潮起开门，潮落闭嘴。

## First upgrade landed — B0 baseline freeze (2026-11-02)

| gate | command | result |
|---|---|---|
| v3_gate | `python scripts/v3_gate.py --json reports/gate_b0_v4.json` | **32/32**, A1 = 25/47/9 |
| unittest | `python -m unittest discover -s tests` | **Ran 34 OK** |
| launch selftest | `python scripts/launch_local.py selftest` | **25/25** |
| skill matrix | `python scripts/verify_skill_matrix.py` | **17/17**, digest `9a565741e1f72ab7` |
| redline | `python scripts/redline_scan.py` | 71 files, **0 violations** |
| fusion | `python scripts/verify_fusion_upgrade.py` | **17/17** |
| ivsa | `cd integrative-rehab-vsa && python main.py` | **21/21** |

Golden values unchanged: `diff0=2fc892cf9af6e755`, `tamper=f42c8229ee5acd73`, `spec.VERSION=0.9.1`.

- 14-dimension lock: `reports/b0_lock_v4fusion.json`
- Ticket: `data/B0_基线票据_v4fusion.md`
- Skill auto-match (1229 → 365 candidates, deterministic, offline, zero external skills executed): `python scripts/b0_match.py` → `data/B0_自动匹配技能.csv`
- Batch progress: `data/B0_批次进度.csv` (B0–B9 complete: B7-1 signed by 潘荟丞 on 2026-11-02 with cumulative 4/15; B8 dual-repo sync green; **B9 closed out** (five-file delivery + deterministic zip))
- B4 rehab pilot: `data/rehab_pilot_20.json` + `data/B4_康复域试点票据.md` — 20 contracts (12 general / 8 medical), 4 negative probes rejected, `python scripts/check_rehab_pilot.py` (R1–R9)
- B5 semantic family: `data/semantic_family.json` + `data/semantic_modules.json` + `data/B5_语义技能族票据.md` — 60 members on the ivsa ten modules (no uncovered module, no 11th module), base 19 index entries → 16 unique + 44 expanded, 4 rehab bridge candidates registered not admitted, `python scripts/check_semantic_family.py` (S1–S9)

- B6 hebbian persistence: `data/hebbian_store.json` (6218 B, 23 edges / 28 nodes / 9 seeds, sha256 `399505b0e695…de282`) + `data/channel_quota.csv` (17 rows: 12 mapped / 5 pending, quota 1200, load 24) + `data/B6_赫布落盘票据.md`; restart proof = real child interpreter, top-k byte-identical; `python scripts/check_hebbian_store.py` (H1–H9), sidecar 51 → 61

- B7 admission: `data/admission_rules.json` (≤5/批, ≤15 累计, 4 gates, signature) + `data/admission_ledger.csv` (4 rows, decision `ADMITTED`, signer 潘荟丞 / 2026-11-02, cumulative 4/15) + `data/B7_准入票据_B7-1.md`; `python scripts/admit_batch.py --check` → `PASS, admitted=4, remaining=11`, sidecar 61 → 71

- B8 dual-repo sync: `data/ivsa_plugin_v1.2.json` (plugin `SG-B8-IVSA-V1.2-PLUGIN`, disabled by default, 6 capabilities read-only) + `SHA256SUMS` (166 files, digest `9bb48c2b5cd41920…`) + `data/dual_repo_sums.json` (ivsa 91 entries recomputed 91/91, 17-channel groups 5/4/4/4) + `data/许可分层清单.csv` (5 rows, 0 mixed) + `data/B8_双仓开源同步票据.md`; `python scripts/verify_b8_dual_sync.py` → 11/11, sidecar 71 → 82

B9 close-out is done: five files + ledger v2 + deterministic zip; `python scripts/verify_b9_closeout.py` must be V1–V12 PASS before any V2.1 work starts.
## Five-site sync DNA (刚性)

`data/FIVE_SITE_SYNC_DNA.md` + `data/five_site_dna.json` — `SG-DNA-FIVE-SITE-SYNC-V1.2`

| site | role | acceptance |
|---|---|---|
| S1 local | write source | `git rev-parse HEAD` |
| S2 Gitee | authority mirror | `git ls-remote main` |
| S3 GitHub | public align | `git ls-remote origin main` |
| S4 vector sea | archive index | `manifest.json` sha256 |
| S5 Hugging Face (`weideyouni/holoaeon`) | external mirror | hf commit sha |

Rules R1–R10 (one-way, same commit, object hash, read-only automation, stash→rebase→pop, credential discipline, dimension gate, readback-not-trust, one receipt, degrade per site) are in the DNA doc. V1.1 adds the batch chain **L1–L9**, the engineering discipline **G1–G8** (preflight before every batch, one batch one scope, no parallel batches, one commit per batch, 3 hard dimension assertions, evidence must be re-runnable, never overwrite receipts, red lines outrank schedule) and the pre-batch gate **P1–P6**. Mechanical checks:

```bash
python scripts/five_site_dna.py build      # write reports/five_site_manifest.json
python scripts/five_site_dna.py verify     # recompute + drift list (offline, no git)
python scripts/five_site_dna.py preflight  # P1-P6 gate: no batch may start unless PASS
```

## V4.1 / V4.2 三项遗留闭环（2026-11-02）

| 批次 | 内容 | 判据 | 回执 |
|---|---|---|---|
| V4.1-B1 | B8 六项插件接实际推理（能力注册表 + `ReasoningBridge`，密令启用，红线四条） | 10/10 | `reports/v41_plugin_runtime_check.json` |
| V4.1-B2 | 语义技能族 60 → 100（另立 V2 规格件，旧判据不动） | 6/6 | `reports/v41_semantic_100_check.json` |
| V4.2-B1 | 三场卡电场补齐（13 卡 = 磁 5 / 电 3 / 液 5；电场 3 张结构化补参数维度 + 检索计划） | 9/9 | `reports/v42_three_field_check.json` |

维度不变量 `agents 25 / skills 47 / packs 9` 未动；三张批次票据见 `data/V4.1_插件接推理票据.md`、`data/V4.1_语义扩容至100票据.md`、`data/V4.2_三场卡电场补齐票据.md`；`evidence_class=simulated` 全程贯穿，远端 sha 与回执字节以命令回读为准。

## V4.3-B1 工程硬化与遗留收尾（2026-11-02）

把上一轮踩到的四个坑从复盘文字改成「脚本 + 可实测判据」，并把三项未做各自推到可交代的位置。

| 批次 | 内容 | 判据 | 回执 |
|---|---|---|---|
| V4.3-B1a | **HF 镜像器** `scripts/mirror_hf.py`：只认 model 仓、`git -c core.quotepath=false` 取中文路径、git blob sha1 判等、`--check` 干跑 | H1/H4 | `reports/v43_hardening_check.json` |
| V4.3-B1b | **向量海清单器** `scripts/build_vector_sea_manifest.py`：固定「先 74、后 manifest」，带自指检测与 `--check` | H2 | 同上 |
| V4.3-B1c | **交付目录诊断器** `scripts/check_delivery_pkg.py`：PKG 漂移一条命令诊断，`--fix` 按写序重建 | H3 | 同上 |
| V4.3-B1d | **B8 接适配层** `holoaeon/fusion_upgrade/reasoning_adapter.py`：事实包进 `ModelAdapter` 路由 + simulated 用量；红线命中不进适配层、不联网 | M1–M4 | 同上 |
| V4.3-B1e | **gap 卡检索执行** `data/v43_gap_literature_probe.json`：`TF-E-01/02/03` 三卡实测检索 9 条指南/共识来源；证据等级仍 `none` | L1 | 同上 |
| V4.3-B1f | **族身份 V2** `data/semantic_family_identity_v2.json`：对外 `SG-V41-SEMANTIC-FAMILY-V2`，与族数据 `sha256=253044a0…`、100 成员硬绑定；族数据本体不动 | I1/I2 | 同上 |

合计 `verify_v43.py` **11/11 PASS**，旁挂单测 `tests_contract/test_v43.py` **9 OK**，`REPO_FILES` 115 → 125。维度不变量未动、判据未放宽、证据口径未升。

常用命令：

```bash
python scripts/mirror_hf.py --base <旧sha> --head HEAD --check   # 只看要推哪些件
python scripts/build_vector_sea_manifest.py --check               # 74 与 manifest 是否自洽
python scripts/check_delivery_pkg.py                              # 交付目录是否漂
python scripts/check_delivery_pkg.py --fix                        # 漂了就按写序重建
python scripts/verify_v43.py                                      # 11 条判据逐项实测
```

实测更正：`build_b9_closeout.py` 只**读** zip，真正打包的是 `build_b9_zip.py`，它按交付目录**全目录**压入（新增补记件会进 zip、sha 必然变化）。上一轮「zip 不含 01」的判断有误，本批已重打并核对 zip 内 01 与交付件同字节。票据见 `data/V4.3_工程硬化与遗留收尾票据.md`。

## V4.4-B1 · 真实模型桥接（2026-11-02）

接真模型这件事改成「目录化 + 开关化 + 可自设定」：不写死一家，也不偷偷联网。

| 维度 | 内容 |
|---|---|
| provider | **19 家**（8 全球 + 9 国内 + 1 聚合 + 1 自定义兜底 + 4 本地运行时） |
| 协议族 | **5 种**：`openai_chat` / `anthropic_messages` / `google_gemini` / `bedrock_converse` / `azure_openai` |
| 本地运行时 | Ollama `:11434/v1`、vLLM `:8000/v1`、llama.cpp `:8080/v1`、LM Studio `:1234/v1`（均 OpenAI 兼容，免 key） |
| 默认态 | **全关**：`enabled=[]`，适配层只剩 `fact-pack-local`，事实包封缄 `6704fb78e5cb` 不变 |
| 开启 | `HOLOAEON_REAL_MODELS=1` + 该家 `*_API_KEY` 有值（本地免 key） |
| 判据 | `python scripts\verify_v44.py` → **A1–A13，13/13 PASS** |
| 单测 | `python -m unittest tests_contract.test_v44` → **9 OK** |

新增件：`data/model_provider_catalog.json`（`SG-V44-MODEL-PROVIDER-CATALOG-V1`）、
`holoaeon/fusion_upgrade/model_gateway.py`、`docs/接入真实模型_配置指南.md`、
`scripts/verify_v44.py`、`tests_contract/test_v44.py`、票据 `data/V4.4_真实模型桥接票据.md`。
`REPO_FILES` 125 → **132**。

常用命令：

```bash
python scripts/verify_v44.py                       # A1–A13 逐条实测
python -c "from holoaeon.fusion_upgrade.model_gateway import build_gateway; print(build_gateway('.').state())"
python -c "from holoaeon.fusion_upgrade.model_gateway import build_gateway; print(build_gateway('.').sample_plans())"
```

边界（不冒充）：本仓**只拼请求、不发请求**，不内置价目表（`input_cost/output_cost=0.0` 是占位不是免费），
型号串为代表性示例、随官方版本增删，运行时以用户传入的 `model` 为准。真发请求需用户按指南注入凭证，
在**自己的运行环境**完成；医学红线（不接设备 / 不出剂量 / 不做诊断）在任何 provider 下都不变。
票据见 `data/V4.4_真实模型桥接票据.md`，用户配置入口见 `docs/接入真实模型_配置指南.md`。

## V4.5-B1 本地运行时联调（真实回环调用，零成本）

V4.4 把「请求怎么拼」做完了但一条都没真发。V4.5 在本机起真实推理服务，用真实 HTTP 调用验证
`model_gateway.plan("lmstudio")` 的同形请求能被真实服务接受——**只打回环、只打 OpenAI 形状、不落凭证**。

| 项 | 实测值（2026-11-02） |
|---|---|
| 服务 | LM Studio 本地 OpenAI 兼容服务，`lms server start` → port **1234** running |
| 端点 | `POST http://localhost:1234/v1/embeddings`，body `{"model","input"}` |
| 响应 | **200** · 4,882 ms · raw 23,316 B · **768 维向量** |
| 证据等级 | `live_local`（真实调用，不是 simulated） |
| 判据 | `python scripts\verify_v45.py` → **B1–B7，7/7 PASS** |
| 单测 | `python -m unittest tests_contract.test_v45` → **8 OK** |
| 回执 | `reports/v45_live_probe.json`（`SG-V45-LIVE-PROBE-V1`，1,080 B / sha16 `3767d37c22d6d3dd`） |

新增件：`scripts/live_gateway_probe.py`（`--mode chat|embeddings`、`LOOPBACK` 白名单硬拒公网 host、
只记 `key_present` 布尔）、`scripts/verify_v45.py`、`tests_contract/test_v45.py`、
票据 `data/V4.5_本地运行时联调票据.md`、回执 `reports/v45_live_probe.json`。`REPO_FILES` 132 → **137**。

常用命令：

```bash
python scripts/live_gateway_probe.py --model text-embedding-nomic-embed-text-v1.5 --mode embeddings
python scripts/live_gateway_probe.py --model qwen2.5-0.5b-instruct --mode chat
python scripts/verify_v45.py
```

边界（不冒充）：本批**chat 端点未真发**——本机唯一可用模型是 embedding 类，对话模型因 LM Studio
`downloadsFolder` 指向 `D:\` 盘根、`lms import` 报 `EPERM mkdir 'D:\'` 而未入索引；该修法属用户应用配置，
本仓不擅自改。云端 provider 仍未真发（无凭证与计费账户）。医学红线（不接设备 / 不出剂量 / 不做诊断）不变。
票据见 `data/V4.5_本地运行时联调票据.md`。

## V4.6-B1 扩展卡槽与协作开发指南（只声明、不接线）

V4.4 拼请求、V4.5 真发请求之后，补的是**接续结构**：后来者要加一家 provider、扩一个语义族、
提一张 gap 卡，必须知道"往哪儿加、会不会破锁数、谁点头才算数"。本批把这套位置落地成卡槽声明。

| 项 | 值 |
|---|---|
| 卡槽文件 | `data/extension_slots.json`（`SG-V46-EXTENSION-SLOTS-V1`，12 槽 / 8 类 / 4 态） |
| 只读加载器 | `holoaeon/fusion_upgrade/slot_registry.py`（无网络、无写盘、无 eval） |
| 指南 | `docs/扩展卡槽与协作开发指南.md`（五步认领法 + 三条使用路径 + 升级口子 + 故障处置） |
| 判据 | `python scripts\\verify_v46.py` → **C1–C9，9/9 PASS** |
| 单测 | `python -m unittest tests_contract.test_v46` → **9 OK** |
| 维度锁 | **25 / 47 / 9 不变**（卡槽是旁挂声明，不改锁数） |

槽分布：`occupied` 4（embeddings / chat / 五地门禁 / 飞书入口）、`open` 1（Ollama）、
`reserved` 5（vLLM-TGI / 新协议形状 / 康复域 V5 影子槽 / 插件钩子 / 端侧模型）、
`blocked` 2（语义族 V2 待定 family_id、gap 卡 tier 上调待拍板）。

新增件：`data/extension_slots.json`、`holoaeon/fusion_upgrade/slot_registry.py`、
`docs/扩展卡槽与协作开发指南.md`、`scripts/verify_v46.py`、`tests_contract/test_v46.py`、
`reports/v46_slot_check.json`、票据 `data/V4.6_扩展卡槽与协作指南票据.md`。`REPO_FILES` 137 → **145**。

边界（不冒充）：卡槽**没有**任何运行时接线，`model_gateway` 不读卡槽、`enabled` 仍为 `[]`；
`EXT-DIM-01` / `EXT-EVIDENCE-01` 保持 `blocked`，等你拍板；Ollama / vLLM 未装未测。


## V5.0-B1 · 康复域知识库全量入库（影子维度 + 证据登记解封）

用户点名：「V5.0 康复域知识库全量入库，走 `EXT-DIM-02` 影子槽 + `EXT-EVIDENCE-01` 解封」。本批只做这一件事。

**「全量入库」= 全量登记，不是全量复制。** 康复域正文留在客仓，本仓只存行数、字节、sha256 与只读指针。

入库实数（`scripts/build_v5_rehab_kb.py` 生成、`verify_v5.py` 复算）：

- ivsa `data/*.csv` **9 张表 / 300 行**（147+7+70+17+20+7+11+13+8）
- ivsa `knowledge/` **11 文件 / 645,707 B**（目录级登记，不逐篇搬字）
- 本仓康复域 **4 件**（`rehab_pilot_20.json` 20 例、`three_field_cards.json` 13 卡、`skin_lexicon_rehab.json`、`semantic_family.json`）
- 索引合计 **14 条** → `data/v5_rehab_kb.json`（`SG-V5-REHAB-KB-V1`）

卡槽变化（12 槽总数不变）：

| 槽 | 之前 | 现在 | 说明 |
|---|---|---|---|
| `EXT-DIM-02` | reserved | **occupied** | 认领为 `SG-V5-DIM-SHADOW-REHAB-V1`，只做检索排序（权重 0.1–0.3） |
| `EXT-EVIDENCE-01` | blocked | **occupied** | 解封＝开放人工核对流程；4 张 gap 卡 tier 仍 `none` |

**影子维度不是第 13 维**：`participates_in_dimension_lock=false`、`affects_diff0_hash=false`，
`reports/dimension_lock.json` 仍是 12 维度 + 7 闸，指纹 `2fc892cf9af6e755` 不变。

**解封 ≠ 上调**：`TF-M-05` / `TF-E-01/02/03` 四张 gap 卡 `tier_before = tier_after = none`，
`tier_unchanged = true`；上调必须人工逐篇拿到原文并满足「原文可获取 / 人群分期明确 / 参数完整 / 结局定义清晰」四条，
票据留具体引用，禁止批量上调。

**门禁（命令回读）**：`verify_v5` **D1–D10 11/11 PASS**；`verify_design_vocab` **D1–D8 8/8 PASS**；`test_v5` **9 OK**；`tests_contract` 168 OK；
`v3_gate` 32/32；`redline_scan` 82 文件零违规；`check_dimension_lock` 0 violation；`five_site verify` `drift=[]`。

新增：`scripts/build_v5_rehab_kb.py`、`scripts/verify_v5.py`、`tests_contract/test_v5.py`、
`data/v5_rehab_kb.json`、`docs/V5.0_康复域知识库与影子维度指南.md`、票据 `data/V5.0_康复域知识库入库票据.md`。
`REPO_FILES` 145 → **152**。

边界（不冒充）：未调用真实模型做康复域推理；未复制 ivsa 任何正文；未动 ivsa 21 组自检与医学红线；
`EXT-DIM-01` 仍 `blocked`，`EXT-PLUGIN-01` / `EXT-RUNTIME-01` 仍 `reserved`。


## V11 · 城邦架构融合 · 拓扑共振升级（V11-A→E，不改维度）

用户点名：读取 `AGENT_FEED_V11_CITY_STATE_FUSION_20261103.md` 第七章，执行 V11 城邦融合五大步
（V11-A/B/C/D/E）与 README 更新、Git 升级说明、五地同步、代码推送以及回执交付。工程维度纪律不变
（25/47/9 锁死），判据优先于 SOP 字面路径。

| 步 | 内容 | 落点 | 实测 |
|---|---|---|---|
| V11-A | 3 个 Graph 函数（曼陀罗扇出 / 莫比乌斯回边 / 克莱因收敛熔断） | `holoaeon/packs/topology_resonance_pack.py`（不碰 `graph.py`） | mandala edges=8/children=8 · mobius w=0.7/cycles=44 · klein iter=14/converged=True · 越界/自环/非图防御通过 |
| V11-B | L10 贝叶斯层 | `guard.py`（`_L10_LIKELIHOOD` + `l10_bayesian`，`Guard.__post_init__` 条件挂载）+ `spec.GuardConfig.bayesian_guard=False` | 默认 9 层不变 / 开启 10 层 / delete 拦截 / safe 放行 |
| V11-C | Runtime 四类 | 新建 `holoaeon/topology_runtime.py`（StateReducer/Checkpoint/CircuitBreaker/DissipationMonitor） | 归约/快照/熔断三态/耗散监控全绿 |
| V11-D | 2 治理技能 | `topology_resonance_pack.py`（skills 14→16） | `city_state_governance`（指纹环+熔断+退避）· `dissipation_emergence_monitor`（半窗熵涌现判定，四场景全对） |
| V11-E | 文档版本 | `spec.py` DOC_VERSION 0.9.10 → **0.9.11** | selftest 25/25 · 维度锁 0 violation（diff0=2fc892cf9af6e755 未漂移）· v3_gate 32/32 · redline 88 文件零违规 · tests 34 OK · tests_contract 184（1 例 V9 既有契约漂移：`EXTRA_PACK_ORDER` 11→12） |

红线（不改一字）：`BUILTIN_LAYERS` L1-L8 / `spec.VERSION=0.9.1` / `layers=8` / `PACK_ORDER` /
`graph.py` / `scheduler.py` / `hypervector.py` / `kernel.py submit`；新增全走 `extra_layers` 通道或全新文件。
修正两处 SOP 勘误（判据优先）：投喂包 7.6 的 `checksum()`（selftest 无此函数）改走
`scripts/check_dimension_lock.py`；投喂包 `add_edge()` 为示意，`AdaptiveGraph` 无此方法，按真实
`weights` 矩阵接口实现。

```powershell
python -m holoaeon.selftest                # 25/25
python scripts\check_dimension_lock.py     # 0 violation · diff0 未漂移
python scripts\v3_gate.py                  # 32/32
python scripts\redline_scan.py             # 88 文件 · 零违规
python -m unittest discover -s tests       # 34 OK
python -m unittest discover -s tests_contract   # 184（1 例既有契约漂移）
```

维度不变：25 / 47 / 9 与 `spec.VERSION=0.9.1`、`diff0_hash=2fc892cf9af6e755`、`tamper=f42c8229ee5acd73`
三值仍未动；`EXTRA_PACK_ORDER=12` 未再增；Guard 默认 9 层、开启 L10 后 10 层（附加层不计入 `guard_layers=8`）。


## V12 · 管家操作系统引导模块（V12-A→E，不改维度）

用户点名：按 `AGENT_FEED_V12_BUTLER_OS_BOOTSTRAP_20261103.md` 第三部分步骤 A→E，执行
V12 管家操作系统引导模块工程。工程维度纪律不变（25/47/9 锁死）、产出物不变、五地同步与推送不变、
README 三份必须更新。判据优先于 SOP 字面路径。

| 步 | 内容 | 落点 | 实测 |
|---|---|---|---|
| V12-A | 四人组执行顾问扩展包（第 13 扩展包，14 技能/5 角色/2 工作流，内联实现不 import quartet_toolkit，公开 `check_emergence`） | 新建 `holoaeon/packs/quartet_director_pack.py` | skills=14 roles=5 workflows=2 · `check_emergence(0.85,0.85,0.85,0.30)` → emergence=True order=0.5237 · install 幂等（二次空） |
| V12-B | Butler OS 引导模块（7 菜单+0 退出，懒加载 kernel）+ 双击启动入口 | 新建 `holoaeon/butler_os.py` + `holoaeon_os.bat`（chcp 65001）/ `holoaeon_os.sh` | 菜单 7 项 · 非交互 4/7 冒烟绿 · 交互管道 0 退出 · `_readline` 替代 input 规避红线 |
| V12-C | 注册第 13 扩展包 + 文档版本 | `packs/__init__.py`（import+registry+`EXTRA_PACK_ORDER` 12→13）+ `spec.py` DOC_VERSION 0.9.11 → **0.9.12** | `EXTRA_PACK_ORDER=13` · `VERSION=0.9.1` 冻结未动 |
| V12-D | 命令注册 | `pyproject.toml` `[project.scripts]` 追加 `holoaeon-os` / `holoaeon-quartet` | 四命令齐备（demo/bridge/os/quartet） |
| V12-E | 验证 + README + 回执 + 五地 | 全验证 + 三份 README V12 段 + `reports/v12_receipt.json` + 单批单提交 + 五地同步 | selftest 25/25 · unittest 68 OK · redline 90 文件 0 违规 · v3_gate 32/32 · 维度锁 0 violation · verify_v44 13/13 · contract 184（既有漂移：断言 11 实际 13） |
| V12.1 | 未决项闭环（第一性原理裁决） | contract 契约测试同步 + 新建 `holoaeon/mcp_adapter.py`（MCP stdio 最小协议子集）+ `holoaeon-mcp` 命令 + 三份 README 披露 + 单提交 | `test_10_no_new_pack` 改下界断言（PACK_ORDER==9 锁不变，EXTRA>=11 防回退）→ **contract 184 全绿** · MCP 自测 13/13（initialize/tools/list/call + 4 错误分支）· selftest 25/25 · redline 91 文件 0 违规 · 维度锁 0 violation |
| V14 | 技能机床与插件化协议适配平台（V14-A→F） | 新建 `holoaeon/skill_lathe.py`（技能机床 TVCB→SkillSpec，能量分级 A/B/C 级丢弃）+ `holoaeon/protocol_plugins.py`（12 平台协议遍历穷举导出，未知协议 ValueError）+ `holoaeon/packs/vector_sea_pack.py`（向量海第 14 扩展包 8 技能/4 角色/2 工作流，key="vector_sea"）+ `holoaeon/vector_sea_explorer.py`（9 阶段流水线 input→ocr→snapshot→search→refine→output→salvage→lathe→protocol_export）+ `EXTRA_PACK_ORDER` 13→14 + butler_os 菜单 8/9 + `pyproject` 追加 `holoaeon-explore / holoaeon-lathe` + `spec.py` DOC_VERSION 0.9.12 → **0.9.13** | `EXTRA_PACK_ORDER=14` · 协议数 12 · 端到端 skill=salvaged_test_test 导出 12 协议 · vector_sea skills=8 roles=4 workflows=2 · selftest 25/25 · unittest 68 OK · contract 184 OK · redline 95 文件 0 违规 · v3_gate 32/32 · verify_v44 13/13 · MCP 回归 13/13 · 装配快照 agents=50 skills=251 · `VERSION=0.9.1` 冻结未动 |
| V21 | 概念解剖器 · 图像增强版（V21-A→D，快照-参考-生成 + 系列工具 + 加载协议 + 视觉锻造台，不改维度） | 潘老师实测反馈"图像太弱要像样的图"→ 先规划 `docs/V21_概念解剖器_图像增强_规划.md`（四维差距诊断+双轨架构+模块二锻造台八步流水线）→ 概念验证（image_search 快照 2 标杆图 + image_edit 生成圆珠笔爆炸图示意图【编号 1-15+零件分解+成品对照】）→ 新建 `holoaeon/concept_anatomy_render.py`（4 渲染器 explosion/annotated/legend/diagram + RENDER_REGISTRY 注册表 + register_render/load_render 加载协议【未注册回落 diagram】+ 5 图像 Token img_style/img_palette/img_axis/img_annotate/img_compare）+ `concept_anatomy.py` 集成 `--img <style>`/`--save`（本地确定性出图）+ 新建 `holoaeon/concept_visual_forge.py`（八步确定性流水线：forge→text_search→image_desc_v1→system_prompt_gen→matrix_modify【6风格×3构图×3色调】→optimize_prompt【质量锚点+负面+确定性锚点】→stylize 三档【blueprint/art_direction/artistic】）+ `--forge` 八步 JSON + 新建 `tests/test_v21_render.py`（13）+ `tests/test_v21_visual_forge.py`（13）+ 包内导入全改相对导入（redline third_party_import 修复） | `EXTRA_PACK_ORDER=17` 不变 · `DOC_VERSION=0.9.16` 不变 · `VERSION=0.9.1` 冻结 · diff0=2fc892cf9af6e755 未漂移 · selftest 25/25 · unittest 全套 OK（+26 V21 tests）· redline 105 文件 0 违规 · v3_gate 32/32 · dimension_lock 0 violation · py38 253 文件 0 失败 · contract PASS · plugin runtime 10/10 · verify_v44 13/13 · 实测 4 风格出图（4196/1499/1090/2009 字符）+ --forge 双通道实测 |
| V20 | 概念解剖器 · 落地场景版（V20-A→C，V19 重设计，不改维度） | `holoaeon/concept_anatomy.py` 新增模块级 `explain(concept)→str` 大白话解释（从 CONCEPT_MAP 取真值格式化：DIMENSION_CN 维度中文名 9 类映射 / 一句话 / 靠什么实现 / N 个零件 / 怎么验证 / 去哪看源码；未知概念返"不是内置概念+可用概念列表"）+ CLI `--explain` 分支 + 文件末尾补 `__main__` 守卫（**修复 V19 已知点：python -m 直跑无输出**）+ 新建 `docs/V20_概念解剖器_使用手册.md`（非技术手册：一段话定位 + 三落地场景【新人看代码/改代码前查影响/写文档贴材料】+ 一条命令速查 + 10 概念大白话速查表）+ `docs/V19_概念解剖器_小白导学手册.md` 已知点段落同步更新（标注 V20 已修复）+ 新建 `tests/test_v20_concept_anatomy.py`（12 tests） | `EXTRA_PACK_ORDER=17` 不变 · `DOC_VERSION=0.9.16` 不变 · 10 概念 explain 全含"一句话" · `-m 经络 --explain` 实测输出非空 · selftest 25/25 · unittest 121 OK（109+12）· redline 103 文件 0 违规 · v3_gate 32/32 · verify_v44 13/13 · 维度锁 0 violation（diff0=2fc892cf9af6e755 未漂移）· contract PASS · py38 249 文件 0 失败 · plugin runtime 10/10 · `VERSION=0.9.1` 冻结未动 · 25/47/9 不变 |
| V19 | 概念解剖器 · Anatomy 创意蒸馏（V19-A→F，不改维度） | 新建 `holoaeon/concept_anatomy.py`（ConceptAnatomizer 十步工序：定维度→取真值→发明映射→列组件→规划→构建→排序→装框→激活→审计；CONCEPT_MAP 10 概念固化映射表（经络/心跳机制/细胞骨架/皮肤机制/经络机制/赫布协作场/语义通信基座/城邦架构/自组织耗散/去幻觉）；DESIGN_TOKENS 26 Token（运行时6/审计5/输出5/验证5/全息5）；等距投影 SVG 纯字符串拼接；确定性=同概念+同Token→同解剖图（时间戳默认关闭 out_timestamp=False）；深度审计四检查（重叠/穿透/一致性/确定性））+ 新建 `holoaeon/packs/concept_anatomy_pack.py`（第 17 扩展包 5 技能/3 角色/1 工作流，key="concept_anatomy"，SkillSpec 按 base.py 实际字段）+ `EXTRA_PACK_ORDER` 16→17 + butler_os 菜单 12 概念解剖 + `pyproject` 追加 `holoaeon-anatomy`（现 11 命令）+ `spec.py` DOC_VERSION 0.9.15 → **0.9.16** + 蒸馏 5 精华 D-01~D-05 + 剔除 4 糟粕 X-01~X-04（第一性原理交集=概念→确定性机制→运行验证概念，步骤3"发明对象"由 LLM 改为固化映射表查找）+ 新建 `tests/test_v19_concept_anatomy.py`（19 tests）+ `test_v12_v17_integration.py` all_extra_packs()==16→17 | `EXTRA_PACK_ORDER=17` · concept_anatomy skills=5 roles=3 workflows=1 · 10 概念全 DONE · 确定性两次一致（无 timestamp）· 穿透审计 depth 单调 0 违规 · selftest 25/25 · unittest 109 OK（含 V19 新 19 tests）· redline 103 文件 0 违规 · v3_gate 32/32 · verify_v44 13/13 · 维度锁 0 violation（diff0=2fc892cf9af6e755 未漂移，EXTRA 16→17 不触发：selftest 无 ==16 硬断言）· contract PASS · py38 语法 248 文件 0 失败 · plugin runtime 10/10 · 装配快照 agents=59 skills=267 · five_site 28/171/0 · zip 不动点 a87fa921bf963fa1 · `VERSION=0.9.1` 冻结未动 |
| V17-V18 | 玉安记忆之王执行 + V6 补丁收尾 + 集成验证（V17→V18，不改维度） | 执行 V17：`F:/doubaowork/memory_of_yuan.py`（项目外，10 记忆域 JSON `F:/doubaowork/holoaeon_memory/` + `.pth` 全域注册两处（.workbuddy 3.13.12 + sandbox site-packages 指向 `F:/doubaowork`）+ SKILL.md `holoaeon` 关键词引发，赫布场 lr=0.12 decay=0.99，memory_graph 中英混合 token 分词 edges=8≥5，不进源码树 diff0 不受影响）；V18 V6 审计收口：12 项 → 10 项已修/不适用 + 1 项已知漂移非阻断（test_holoaeon.py:316 断言 >=7）+ 1 项 CI 缺口低优先级，正式收口；新建 `tests/test_v12_v17_integration.py`（7 TestCase 22 tests 覆盖 V12-V17 六模块 + 跨模块协同：all_extra_packs()==16 / Kernel 装齐 9+16 包 submit / EXTRA_PACK_ORDER 顺序 topology_resonance→quartet_director→vector_sea→dehallucination→super_agent / butler_os 源码模块字样；V13/V14 API 名按实际函数式 API 适配） | V17 验证清单 9/9 PASS（10 域/全域加载/跨目录 seal/全息 matched=5/versions=16/edges=8/同义 holoaeon/封存 True/selftest 25/25）· 集成测试 22 OK · selftest 25/25 · golden verify 5/5（verify_all(n=2) 5 tasks True）· unittest 主 90 OK（含集成 22）+ verax 21 + v3 5 · redline 101 文件 0 违规 · v3_gate 32/32 · verify_v44 PASS · 维度锁 0 violation（diff0=2fc892cf9af6e755 未漂移）· contract PASS（PACK 9/EXTRA 16）· MCP 4/4 · `DOC_VERSION=0.9.15`（不变，V17/V18 不改源码）· `VERSION=0.9.1` 冻结未动 |
| V16 | 确定性自主调度增强 · DeepSeek Super-agent 对标蒸馏（V16-A→E） | 新建 `holoaeon/router_layer.py`（RouterLayer 确定性任务路由：task_queue deque/shared_context/dispatch_rules 按 priority 排序/worker_results/is_running，receive→_dispatch 带有序字符匹配降级链，aggregate/status CLI）+ `holoaeon/event_filter.py`（EventFilter 两级过滤：FAST_PATTERNS 14 词 + DEEP_RULES 4 条 lambda，filter 返回 passed/level/reason，batch_filter CLI）+ `holoaeon/external_watchdog.py`（ExternalWatchdog 外部只读看门狗：BASE_LINE 冻结基线，check_selftest/check_diff0/check_redline 只 observe 不执行，alert 只告警不拦截）+ `holoaeon/packs/super_agent_pack.py`（第 16 扩展包 5 技能/3 角色/1 工作流，key="super_agent"）+ `EXTRA_PACK_ORDER` 15→16 + butler_os 菜单 11 自主调度 + `pyproject` 追加 `holoaeon-router / holoaeon-watchdog`（现 10 命令）+ `spec.py` DOC_VERSION 0.9.14 → **0.9.15** + 蒸馏 5 精华 D-01~D-05 + 剔除 4 糟粕 X-01~X-04（第一性原理交集=确定性的自主调度，规则驱动非 LLM）+ golden 重冻结 3 项（V6 degraded 结构演进修复）+ 全息体系对应表 V16 更新 | `EXTRA_PACK_ORDER=16` · super_agent skills=5 roles=3 workflows=1 · 四新模块 selfcheck 全 PASS（router dispatch 4 类/event_filter L2/watchdog alerts=1）· selftest 25/25 · unittest 68 OK · contract PASS · redline 101 文件 0 违规 · v3_gate 32/32 · verify_v44 13/13 · MCP 回归 13/13（doc_version 0.9.15）· 装配快照 agents=56 skills=262 · 写型链全绿（b8 245/91 · b9 criteria=30/risks=12/ledger=12 · zip 不动点 a87fa921bf963fa1 · five_site 28/171/0 · vector_sea_manifest 195/195）· 复现 5/5 golden=True · verax yellow（H2=3 口径局限）· `VERSION=0.9.1` 冻结未动 |
| V15 | 自组织相似性全息去幻觉模块（V15-A→D） | 新建 `holoaeon/dehallucination.py`（DeHallucinationModule 8 阶段流水线 input→seb_extract→reality_anchor→snapshot_vec→leibniz_compare→synonym_map→verdict→hebbian_update，莱布尼茨 PSR×张平 Seb×赫布场，COSINE_HIGH=0.7/COSINE_LOW=0.4/BAYES_PRIOR=0.15/BAYES_THRESHOLD=0.5，联网 fetch_callback 注入缺失降级，贝叶斯+耗散熵判定）+ `holoaeon/packs/dehallucination_pack.py`（第 15 扩展包 6 技能/3 角色/1 工作流，key="dehallucination"）+ `EXTRA_PACK_ORDER` 14→15 + butler_os 菜单 10 去幻觉检测 + `pyproject` 追加 `holoaeon-dehallucinate` + `spec.py` DOC_VERSION 0.9.13 → **0.9.14** + 全息体系对应表修正（经络=自组织相似性共振 ≠ 经络机制=Bus） | `EXTRA_PACK_ORDER=15` · dehallucination skills=6 roles=3 workflows=1 · 模块自检 PASS（三分支）· 降级检测三值齐（verdict/cosine/entropy）· selftest 25/25 · unittest 68 OK · contract 184 OK · redline 97 文件 0 违规 · v3_gate 32/32 · verify_v44 13/13 · MCP 回归 13/13（doc_version 0.9.14）· 装配快照 agents=53 skills=257 · `VERSION=0.9.1` 冻结未动 |

红线（不改一字）：`BUILTIN_LAYERS` L1-L8 / `spec.VERSION=0.9.1` / `layers=8` / `PACK_ORDER` /
`graph.py` / `scheduler.py` / `hypervector.py` / `kernel.py submit`；新包只进 `EXTRA_PACK_REGISTRY` /
`EXTRA_PACK_ORDER`，不破坏 G15 的 25/47 断言。契约核查：投喂包 SKILLS/ROLES/WORKFLOWS 的 dict
写法已转 base.py dataclass 契约；ROLES 缺 skills 字段按参考包补全；验证清单第 7 项 `_check_emergence`
已公开化为 `check_emergence`。

```powershell
python -m holoaeon.selftest                # 25/25
python scripts\redline_scan.py             # 90 文件 · 零违规
python -m unittest discover -s tests       # 68 OK
python scripts\verify_v44.py               # 13/13
python -m holoaeon.butler_os 7             # 状态快照：agents=53 skills=257 DOC_VERSION=0.9.14
python -m holoaeon.butler_os 10            # 去幻觉检测（莱布尼茨PSR×张平Seb×赫布场 8 阶段流水线）
```

维度不变：25 / 47 / 9 与 `spec.VERSION=0.9.1`、`diff0_hash=2fc892cf9af6e755`、`tamper=f42c8229ee5acd73`
三值仍未动；`EXTRA_PACK_ORDER=15`（第 15 扩展包 dehallucination 旁挂，不进 PACK_ORDER）；Guard 默认 9 层、L10 默认关
（附加层不计入 `guard_layers=8`）；装配后快照 agents=46、skills=243（扩展包旁挂增量）。


## 附录 · Git 版本升级说明（V3 收口 → V11，按提交回溯）

> 口径：sha 与提交主题取自 `git log --oneline` 实测；数字类指标（条目数、字节数、sha16）
> 以对应批次 `verify_*` / `five_site_dna` 命令回读为准，不在此处硬编码猜测值。

| 阶段 | 代表提交 | 主题与产出 |
|---|---|---|
| V3 收口 | `3d359bd` / `32b2667` | LangChain 工程形态旁挂（W12–W19），32/32 门禁，维度不变 |
| 同步基建 | `92fd8b5` / `dfad361` | 五地同步 DNA V1.0→V1.1（G1–G8 + P1–P6），离线哈希校验器 |
| **V4.0 开场** | `80089b6` | 冷热插拔升级：第 10 个附加包，**25/47/9 不变**，32/32 门禁、17/17 融合自检 |
| B0 基线 | `055d202` | 基线冻结 7/7 绿、14 维锁、1229 → 365 技能自动匹配 |
| B1a | `63af1bb` | 契约字段草案 v0.1（6 必填 + 4 可选，指纹/白名单/医学红线） |
| B1b | `2c35c35` | 契约 v1 指纹互通（11 旁挂测试、跨进程字节相等、冻结 `contract_v1.json`） |
| B2a | `ec74e08` | 六机制 1:1 映射（M1–M6 检查器，`mapping_rule` 必填） |
| B2b | `76cd834` | 12→17 通道显式分组（不做算术），皮肤词表域切分（E13/E14 不外溢） |
| B3 | `91fc8b3` / `7091a86` | 1229 技能用途重分类（K/M/T/X/U 两阶段确定性，抽样 37/40）+ 向量海清单自检 |
| B4 | `310981e` | 20 个康复域试点契约（12 通科 / 8 医学，4 个负样本被拒） |
| B5 | `4c5a4a8` | 语义技能族 19 → 60（不设第 11 模块；4 个康复候选未准入） |
| B6 | `6dd5128` | 赫布权重持久化（23 边 / 28 节点，重启字节相等）+ 17 通道配额表（12 映射 / 5 待定） |
| B7-1 | `c39e75f` | 准入闸上线：≤5/批、≤15 累计、四硬闸、需签字；4 个候选 `WAITING_SIGNATURE` |
| B7-2 | `ec79c9b` / `97e0794` | 5 技能签字准入（累计 9/15）；重建 `dual_repo_sums` 保 R6 一致 |
| B7-3/4 | `969c83b` | 5 + 1 签字准入，**B7 收口 15/15**；DNA G9 排除项 9→10 |
| B8 | `06f11ad` / `1235805` / `0353613` | ivsa v1.2 插件默认关 + 双仓 `SHA256SUMS` 互认（Apache-2.0 / MPL-2.0 分层）；断 SUMS 自指 + 强制 LF |
| B9 | `c03b19d` | 五件交付 + 台账 v2 + 确定性 zip；DNA V1.2（G9 写序 / G10 密令等同签字 / P7 五地回读） |
| V2.1 | `3b0b32b` | ivsa 只读对账 R1–R7 开票，旁挂 92→101 |
| V4.3 | `4f06bc8` / `3d6f956` | 四坑固化（HF model 仓 / 中文路径 / 74→manifest 顺序 / 交付目录漂移）+ 11/11 判据 |
| V4.4 | `b85b293` | 19 家 provider 目录 + 5 协议拼装 + 默认全关 + 配置指南；A1–A13 13/13 |
| V4.5-B1 | `fb5cdef` | 真实回环调用：`/v1/embeddings` 200 / 768 维；B1–B7 7/7、8 OK |
| V4.5-B2 | `f0f1bb5` | chat 补做：`/v1/chat/completions` 200 / 41+29 tokens；卡槽放到 C 盘模型目录后 `lms import` 成功 |
| V4.6-B1 | `f0f1bb5` / `978dc10` / `6646315` | 12 卡槽 + 协作指南；C1–C9 9/9；卡槽实数勘误 14→12 后补收口 |
| V5.0-B1 | `aa88c37` | 康复域知识库全量入库（14 条登记 / ivsa 300 行）；影子维度 D_REHAB 不入锁；`EXT-EVIDENCE-01` 解封而 tier 不变；D1–D10 11/11 |
| V6.1-B4/B5 | `5e2b6d8` / `49c8b8f` / `2c9a394` | 批0 理想形态定义书 + 批1 全仓 runtime 体检（V7 批次链路固化）；B5 摘要清单重建（双仓 240 条目 · 五地清单对齐） |
| V8 批2-4 | `2fc1faf` / `4bf84df` | L9 路径闸门（`product_layer_guard`）+ 产品层三件套（frontend_adapter / demo_product / install）+ TCM 旗舰包（`tcm_rehab` 第 11 扩展包）+ 领域化解耦；`DOC_VERSION 0.9.8 → 0.9.9` |
| V9 拓扑共振包 | 本批提交（`git log -1 --format=%h` 回读） | `topology_resonance_pack.py`（8 基础数学 + 6 四人组技能）；`EXTRA_PACK_ORDER` 11→**12**；`DOC_VERSION 0.9.9 → 0.9.10` |
| V11 城邦架构融合 | 本批提交（`git log -1 --format=%h` 回读） | 3 Graph 函数 + Guard L10 贝叶斯层 + 新建 `topology_runtime.py` + 2 治理技能（skills 14→16）+ `DOC_VERSION 0.9.10 → 0.9.11`；selftest 25/25 · `diff0` 未漂移 |
| V12 管家引导 | 本批提交（`git log -1 --format=%h` 回读） | `butler_os.py`（7 菜单+0 退出）+ `quartet_director_pack.py`（第 13 扩展包 14/5/2）+ `holoaeon_os.bat/.sh` + `EXTRA_PACK_ORDER` 12→13 + `DOC_VERSION 0.9.11 → 0.9.12`；selftest 25/25 · redline 90 文件 0 违规 · verify_v44 13/13 · `diff0` 未漂移 |

**升级主线一句话**：每一批只做一件事，且**只加旁挂、不改锁数**；每批必带 `verify_*` 判据、
必带票据、必过五地同步（`drift=[]` 方可提交）。

