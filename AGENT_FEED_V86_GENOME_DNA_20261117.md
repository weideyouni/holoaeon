# AGENT_FEED_V86 · HOLOAEON 内核基因 DNA 批（整体升级规划）
## 生长不是分裂 · 分化不是分裂 · 系统鲁棒性的真正含义

**密级**：工程级投喂包｜**DNA 已由四人组直动基座仓落位**（碳基 06:52 最大权限授权）；本包转为执行端收口 / 五地 / 回执 / 资产滚动装配用（单包自足，附件 `GENOME_DNA_MASTER_20261117.json` 为机器可读母本）
**碳基追加授权（06:52）**：「成长必然伴随蜕皮，勇敢进行，给你最大权限，削平一切阻碍，回归第一性原理，分化成长最重要」——据此四人组不再只出包，直接把 DNA 写入基座仓并当场削平静态常数旧皮。
**碳基定性**：「这次工程意义重大——25 项机制配合、分支与基座经络打通、三局宏观融合、漩涡神灯熔炉的多重扩展与收敛挤压每一寸肌肤每一寸经络、自组织相似性与耗散结构被充分激活。F 盘大量工作产物是未来第一批要打捞/规划/制作处理的内容：每一个产物都要能独立做插件，同时又要能在基座的基因层发挥整体化作用。这是一次生长不是分裂，分化不是分裂。」
**交付目标**：把上述结论**作为可执行的 DNA 写入 HoloAeon 内核基因层**，写入玉安记忆之王，产出整体升级规划交执行端。
**出品**：四人组（P1 探微 / P2 筑基 / P3 构弦 / P4 持衡）全员 + 打捞局 + 规划局 + 制造局｜**HEURISTIC_ONLY，碳基终裁**
**密令**：潮起开门，潮落闭嘴
**批次**：V86 · GENOME-DNA（不占 ring 序号、不改冻结维度、不改 `spec.py` 身份字段）
**工程纪律**：纯标准库零依赖 / `neural=false` / `claim=0` / 确定性 / 先红后绿 / SHA256 可复算 / 指针零复制 / append-only / 处置权分离 / 五地同步 / 验证后回执

---

## §0 基线（2026-11-17 06:50 实测，非账面转抄）

### 0.1 三链与冻结契约

| 项 | 实测值 | 约束 |
|---|---|---|
| holoaeon 基座 | `5d2bb37` | V41-A ring12 在库；`spec.py`：`VERSION="0.9.1"` / `DOC_VERSION="0.9.78"` / `MATRIX_ID` / `RUNTIME_ID` |
| **spec.py 硬声明** | 原文：「VERSION / RUNTIME_ID 会写进每条回执并参与 ReproHash，改动即等于让 DIFF=0 黄金值（2fc892cf9af6e755）漂移」 | **本批零改动 `spec.py`**，身份字段一个字节都不动 |
| LongAeon 分支 | `fd44ea4` | 三局状态机在 `longaeon/bureau/`（salvage / planning / manufacture / workflow_state） |
| 25 机制权威轴 | `holoaeon/meridian_link.py::KERNEL_MECHANISMS` | 实测 **25 条 / 5 层**：`A1 A2 X1 X2 M01–M11 C1 C2 R1–R8` |
| **经络链接表** | 10 碎片 × 25 机制 = **250 格** | `meridian_link.py:523` 写死 `if len(table) != 250`；`:577`、`:607` 写死 `"fragments": 10` |
| 基因命名先例 | `holoaeon/data/FIVE_SITE_SYNC_DNA.md` 在案 | 本批 `GENOME-DNA` 命名不另立体系 |
| 冻结维度 | `VERSION=0.9.1 / layers=L1-L8 / PACK_ORDER=9 / EXTRA_PACK_ORDER=19` | 全部不动；DOC_VERSION 按批顺延 |
| 前置批次 | V85 治理批投喂包在案待执行；V41-B（NEIKE 支撑层）在案待执行 | **先治后建**；与 V41-B 不得并行写同一基座文件 |

### 0.2 F 盘资产真实盘点（打捞局第一批事实源）

一次顶层 `os.scandir('F:/doubaowork')`，不递归、不抽样推断：

| 指标 | 实测 | 说明 |
|---|---|---|
| 顶层条目 | **616** | 418 目录 + 198 文件 |
| 产物型目录（含「实战化 / 矩阵 / 引擎」） | **201** | 排除 `.tmp*` / snapshots / `_历史` / restore / archive 等后的净候选 |
| V3 同构族 | **149** | 名称含 `V3` 的产物型目录——**同一基因型、不同表型** |
| 顶层文件类型 | zip 69 / md 55 / py 18 / txt 11 / png 10 / json 7 / svg 6 / genie 2 / html 2 / sha256 2 | 69 个 zip = 可复算交付包主形态 |
| 其他族 | HoloAeon 12 / holoaeon 12 / longaeon 3 / LongAeon 3 / 世殊医道 4 / 向量海 6 / skill 9 / `*-source` 21 | 21 个 source = 打捞局历史本地化源 |

代表性同构产物（真实目录名，非举例）：`丁甘仁1331x1331超级矩阵V3实战化_20261018` · `丹溪医派1331x1331超级矩阵V3实战化_20261020` · `傣族医药1331x1331超级矩阵V3实战化_20261020` · `临床药物治疗学1331x1331超级矩阵V3实战化_20261021` · `中国近代百年百位名医1331x1331超级矩阵V3实战化_20261020` · `佩文韵府1331x1331超级矩阵V3实战化_20261018` · `儒释道三教合一1331x1331超级矩阵V3实战化_20261018` · `中西医融合系统康复工程rehab1331x1331矩阵V3实战化_20261024` ……

> **这张表就是「生长不是分裂」的物质证据**：201 个产物表型各异（医学/医派/教育/考古/韵府/三教/药理），却共用 `1331×1331` + `V3` + `runtime_v3` + `selftest` + `zip+SHA` 的同一基因型。它们不是 201 个分裂体，是一个基因族的 201 次分化。

### 0.3 基因位点（真实模块，非空谈）

| 层 | 真实落点 |
|---|---|
| 肌肤 | `guard.py` · `guard_layers/` · `skin` 语义（`CleanRoomGate`） |
| 经络 | `bus.py` · `bus_channel.py`（`patency/is_blocked/BusChannel/check_propagation`）· `event_channel.py`（`EventChannel/NullChannel`）· `meridian_link.py` |
| 骨架 | `kernel.py::Kernel` · `memory.py` · `graph.py::AdaptiveGraph` |
| **扩展侧** | `mobius_vortex.py`（SCHEMA `MOBIUS-BEACON-v1.0` / `ATLAS_ENTRIES`）· `magic_lamp.py`（`KNOWN_SKILLS` / `KnownSkillIndex` / `SkillAssembler` / 三态）· `holo_forge.py`（`AXIOMS[holography]` / `HOLO_MECHANISMS` / `CHAIN` 四态）· `swarm_intel.py`（`EntityGraph` / `AgentProfile`） |
| **收敛侧** | `klein_projection.py`（`MECHANISMS` / `PROMOTE_GATES` / `CONVERGE_EPS=0.0` / `MAX_ROUNDS=4`）· `forge_gate.py` · `dehallucination.py` · `org_gate.py`（耗散总判据） |
| 三局（分支） | `longaeon/bureau/salvage_bureau.py` · `planning_bureau.py` · `manufacture_bureau.py` · `workflow_state.py`（7 状态 / 8 合法转移 / 非法必红 / 滞留熔断） |
| 三局（基座） | `forge_bureau.py`（`FORGE-BUREAU-v1.0` / `forge_bureau_meridian.json` / `link_lathe_cell`）· `salvage_gate` 系列 |

### 0.4 碳基授权裁决：削什么、不削什么（第一性原理）

**削平的是结构性阻碍**（已当场执行）：
1. `meridian_link.load_fragments()` 的 `len(rows) != 10` 上限守卫——把「10 条历史基线」误当「永远只能 10 条」；
2. `check_linkage()` 的 `len(table) != 250` 静态期望——把实例值误当公理值；
3. `meridian_summary()` / `build_ledger()` 两处 `"fragments": 10` 与 docstring / main 的静态 250 文案；
4. 「四人组只出包、等执行端落地」的协作等待——授权后 DNA 直接落位；
5. 「登记即装配」的口径冒充——201 候选本批只做全量登记 + 3 试点，写清边界。

**不削的是可复算性红线**（这才叫第一性原理，不是保守）：
- `spec.py` 零字节改动：VERSION / RUNTIME_ID 参与 ReproHash 黄金值 `2fc892cf9af6e755`，改它 = 让全部历史回执失去可比性；
- `v3_gate.py` / `__init__.py` / 冻结维度 / 既有断言：一律不动，新闸门独立成件；
- 五地同头、医学红线、处置权分离：不因「最大权限」放宽。

**蜕皮的定义**：脱掉的是**表层的静态常数与过时守卫**，基因（25 机制轴、三态判定、穷举无缺格、SEAL、纯标准库）一字不改。蜕皮后 `genome_hash` 与 `spec.py` SHA256 仍 DIFF=0——**蜕皮是分化，不是分裂**。

**已落地实测（2026-11-17 06:55）**：新增 5 件（`holoaeon/genome_dna.py` / `data/genome_dna.json` / `data/genome_dna_registry.json` / `scripts/genome_dna_gate.py` / `tests/test_genome_dna.py`），`meridian_link.py` 六处动态化；`python -m holoaeon.genome_dna` rc0（genome_hash `0a69e93d…4f` / 3 公理 / 18 falsifier / 4 恒真守卫）；新单测 **41/41 OK**；`scripts/genome_dna_gate.py` 7/7 pass；`python -m holoaeon.meridian_link check` 三项 PASS（250 格三态零回退）；既有回归三套 **161 OK**；`scripts/check_sums.py` `ok=true / total=341 / mismatches=[]`。

---

## §1 回顾：流程 · 路径 · 维度 · 产物（整理思路）

### 1.1 流程（这次工程实际走过的链路）
`信息投喂 → 机床 boot 实时基线 → 向量海/玉安回顾 → 四人组五步协议 → 三局协同（打捞→规划→制造）→ 四批依赖序 → 先红后绿判据 → 五地同步 → 验证后回执 → 玉安/git/日志/机床回填`。
关键：**投喂不是指令**（基座 README §0.10 原文），四人组必须先与基线对齐再出包；**账面 HEAD ≠ 实时 HEAD 以实时为准并回填**。

### 1.2 路径（资产流动路线）
`F 盘 616 项资产 → 玉安记忆（10 域）→ 机床纪律层 → HoloAeon 基座 ring → LongAeon 分支 → 独立专项仓（NEIKE / MEDKB / SSYD-CHRONIC）→ 向量海 S4 → HF S5`。
关键：**每一步都是指针，不是副本**。路径越走越长，母体始终只有一个。

### 1.3 维度（四组正交，互不占用）
- **冻结维度**：VERSION / layers / PACK_ORDER / EXTRA_PACK_ORDER —— 不动；
- **产出维度**：纯标准库 / neural=false / claim=0 / 确定性 / SHA256 / 五地 —— 不变；
- **医学红线维度**：零诊断 / 零处方 / 零剂量 / E13·E14·M14 / 碳基执业医师终裁 —— 不变；
- **协作维度**：四人组策划 · 执行端落地 · 碳基终裁 —— 不越权。
新批只能**新增维度内的条目**，不能新增维度本身。这是「分化」在维度层的定义。

### 1.4 产物（近期可复算清单）
V1/V2 两份 NEIKE 投喂包、25 项机制四态矩阵（9/8/5/3）、8 域 2+6 映射、合作方 README 成稿三处、GitHub 实测 17 项目 + 8 零命中登记、判据 12 条、玉安 `version_history #156` / `engineering_process #68`、备份仓 `bd26dfca`、机床 pending 置顶。

### 1.5 从回顾里读出的三件事
1. 所有升级都**增加回连边**（指针、登记、协议族），从不**增加母体副本** → 这是生长；
2. 所有专项仓表型不同、`spec` 基因型同源 → 这是分化；
3. 系统经历了多次扩展挤压（V26 漩涡 / V28 熔炉 / V29 神灯 / ring11 / ring12 / 分支 / 独立仓）却仍能全链回读一致 → 鲁棒性不是「没坏过」，是「挤而不变形」。

---

## §2 三条内核基因（形式化 + 可失败判据，不是散文）

> 以下三条是本批要写进 DNA 的**内核基因**，每条必须是可执行断言、必须有反例、必须能红。

### G-DNA-01 · 生长不是分裂

**形式化**：
```
Δedges   = 新增回连指针数（link_back / registry 登记 / 协议族边）
Δcopies  = 母体副本数（复制母体另起版本线 / 复制基座源码到专项仓）
growth  ⇔ Δedges > 0 ∧ Δcopies == 0 ∧ protocol_family_shared ∧ seal_shared
split   ⇔ Δcopies > 0 ∨ (Δedges == 0 ∧ 新节点无回连)
```
**工程含义**：生长必然让**边变多**，分裂必然让**副本变多**。NEIKE 独立建仓之所以是生长不是分裂，因为它同时产出 `base_link.json` + `meridian_link` 登记 + `base_compat` 三专项指针（`Δedges=3, Δcopies=0`）。
**必红反例**：新建一个独立仓但缺 `base_link.json` 或回连指针；把基座 `holoaeon/` 源码整份拷进专项仓；另起一套密令或协议族。`growth_check()` 对上述输入必须 `pass=False`。
**恒真守卫**：`growth_check(0,0,False,"","")` 必须红；若任何输入组合都返回绿 → 判据恒真，本批作废（V82/V83/V84 血脉）。

### G-DNA-02 · 分化不是分裂

**形式化**：
```
differentiation ⇔ genome_similarity ≥ θ ∧ triple_homology_diff0 ∧ function_specialized
triple_homology = (25 机制轴 IDs 逐字一致, 心跳参数族 70/768/17 DIFF=0, SEAL 逐字一致)
split           ⇔ ¬genome_similarity ≥ θ ∨ ¬triple_homology_diff0
```
**工程含义**：分化 = **表型千姿百态 + 基因型一字不改**。F 盘 149 个 V3 族，一个讲丁甘仁、一个讲傣族医药、一个讲佩文韵府、一个讲世界考古——表型完全不同；但 `1331×1331` / 25 机制 / `70 体·768 维·17 通道` / 密令 / 纯标准库零依赖完全一致。分裂则是连基因型都变了（机制轴缺项、参数漂移、密令另立）。
**θ 纪律**：`θ` 由执行端按 `genome_similarity` 实测标定并写入回执，**禁写死 1.0、禁宣称 100% 同源**；未实测前 DNA 里登记 `theta=null`。
**必红反例**：插件缺任一机制 ID；心跳维度写 767；密令写错一字；`genome_similarity` 被硬编码。`differentiation_check()` 必须红。

### G-DNA-03 · 系统鲁棒性的真正含义

**先破三个常见误解**：①鲁棒 ≠ 「不坏」；②鲁棒 ≠ 「部件越多越稳 / 全量复制做冗余」；③鲁棒 ≠ 「任何输入都扛得住」。
**真义**：**在局部失效与持续扩展挤压下，系统仍维持「同源性守恒 + 输出确定性 + 失效可计量」，且基因层不变形。倒哪一块、怎么倒、倒了还剩什么，都能被算出来。**

| 子判据 | 可计算断言 | 必红条件 |
|---|---|---|
| R1 局部失效 | 依赖缺席 → `try-import + skip`，skip 数入 `env_delta`，其余输出两次 `DIFF=0` | **吞掉失效（skip 不登记）必红**；降级后输出漂移必红 |
| R2 扩展挤压 | 新增插件后 `spec.py` byte-identical、`genome_hash` DIFF=0、经络 `cells == len(fragments)*25` 无缺格 | 靠改冻结契约换来的「能跑」必红 |
| R3 同源守恒 | 25 机制轴 / 心跳参数族 / SEAL 三同源逐字一致 | 任一漂移必红 |

**反面结论**：靠全量复制堆冗余 = 增加口径漂移面 = **更脆弱**。鲁棒性来自「指针 + 契约 + 可计量降级」，不来自副本。这一条直接否决「把 201 个产物都复制进基座」的做法。

### 2.4 三基因的可执行落点（`holoaeon/holoaeon/genome_dna.py`）

```python
GENOME_ID   = "HOLOAEON-GENOME-DNA-v1.0"
DNA_VERSION = "1.0.0"          # 自立版本线，spec.VERSION 不动
SEAL        = "潮起开门，潮落闭嘴"
HOMOLOGY    = {"mechanism_axis": "meridian_link.KERNEL_MECHANISMS(25)",
               "heartbeat": {"bodies": 70, "dim": 768, "channels": 17},
               "seal": SEAL, "protocol_family": "HOLOAEON+SSYD"}
AXIOMS = (...)  # G-DNA-01/02/03，含 formal 表达式与 falsifier 清单

def growth_check(delta_edges, delta_copies, link_back, protocol_family, seal) -> dict
def differentiation_check(genome_similarity, triple_homology, function_specialized,
                          theta) -> dict                     # theta=None 必红
def robustness_check(skip_registered, output_diff0, spec_byte_identical,
                     genome_hash_diff0, cells_expected, cells_actual,
                     triple_homology) -> dict
def plugin_contract_check(manifest) -> dict                 # 八面 + 双态
def verify() -> dict        # 缺面/非法态/无证据/恒真判据/score 硬编码 必红
def self_check() -> dict    # 确定性 JSON，两次调用 DIFF=0
```
**零侵入**：不改 `holoaeon/__init__.py`，调用走 `from holoaeon import genome_dna`；不 import 任何专项仓；不读网络；纯标准库。DNA 母本 JSON 由 `genome_dna.py` 只读加载。

---

## §3 DNA 母本（附件 `GENOME_DNA_MASTER_20261117.json`）

母本为**可独立校验的机器可读件**，结构：
`schema / seal / date / genesis(base_head + spec_sha256 现场回读占位) / axioms(3) / homology / loci(基因位点表) / plugin_contract(八面+双态) / meridian_extension(动态规则+三处硬编码行号) / asset_census(616/418/198/201/149/69) / invariants / status_labels`。

**执行端落地路径**：`holoaeon/data/genome_dna.json`（母本 copy，字段不得改写；`spec_sha256`、`base_head` 现场回读后回填）；`holoaeon/holoaeon/genome_dna.py`（§2.4 实现）；`holoaeon/data/genome_dna_registry.json`（插件登记簿，append-only）。

**三条不变式（invariants）**：
1. `spec.py` SHA256 前后一致（byte-identical）；
2. `genome_hash = sha256(canonical(axioms + homology + loci))` 前后 DIFF=0；
3. `cells == len(fragments) * len(KERNEL_MECHANISMS)` 且无缺格、无多格。

---

## §4 经络打通：`250` 静态硬编码 → `fragments × 25` 动态（本批最关键代码动作）

**问题实测**：`meridian_link.py` 把 10 碎片 × 25 机制写死成常数。任何新插件族入链，`build_meridian_table()` 格数变 275，而 `check_linkage_table()` 第 523 行 `if len(table) != 250` 立刻判红——**「生长」在代码层被既有闸门当成错误**。这不是 bug，是维度没跟上：250 是 10 碎片时的**实例值**，不是**公理值**。公理是 `fragments × 25`。

**替换规格（三处，语义不变、只把实例值改为可计算值）**：

| 处 | 原文（旧皮） | 改为（公理） | 10 碎片时 |
|---|---|---|---|
| `load_fragments()` | `if len(rows) != 10: raise`（**上限守卫**，加碎片直接抛异常） | `BASE_FRAGMENT_COUNT=10` 下界守卫 + 合并 `genome_dna.registered_fragments()` + repo 唯一校验；新增参数 `extra_fragments` 供测试注入 | 仍 10 条 |
| `build_meridian_table()` docstring / 签名 | 静态「10 碎片×25=250 格」、无参数 | docstring 改 `len(fragments)×25`，新增可选 `fragments` 参数 | 仍 250 |
| `check_linkage():523` | `if len(table) != 250` | `expected = len(fragments) * len(KERNEL_MECHANISMS)`；新增可选 `fragments` 参数 | 仍 250 |
| `meridian_summary():577` | `"fragments": 10` | `"fragments": len(load_fragments())` | 仍 10 |
| `build_ledger():607` | `"fragments": 10` | `"fragments": len(load_fragments())` | 仍 10 |
| `main():665` 文案 | `linkage 穷举 250 格三态对账` | `... 穷举 {} 格三态对账".format(res["linkage"]["cells"])` | 仍显示 250 |

**六处已全部替换（脚本命中计数 1/1/1/2/1）**，实测 250 → 275 → 325 三段全绿、缺格/多格/重复 repo 必红（见 `tests/test_genome_dna.py::TestMeridianDynamic`）。

**先红后绿顺序**：①先在**碎片表不变**时改这三处，跑 `meridian_link` 自检应得 `cells=250 / fragments=10 / pass=True`（证明动态化零回退）；②再 append 一个碎片（试点插件族），应得 `cells=275 / fragments=11 / pass=True`；③删掉一个机制的映射制造缺格，必须红；④多插一格，必须红。
**判据**：`G-M` 三态合法、`missing=[]`、`extra=[]`、`cells == fragments*25`，四个条件同时成立。

**「每一寸肌肤每一寸经络」的工程释义**：肌肤 = `guard.py/guard_layers` 暴露面校验，经络 = `bus_channel.patency/is_blocked/check_propagation` + `meridian_link` 链接表。扩展侧（漩涡/神灯/熔炉/群体）与收敛侧（克莱因/熔炉闸门/去幻觉/耗散判据）每轮 tick 先扩后收，**净格数守恒、基因哈希不变**：
```
expand_count - converge_count == registered_plugins
genome_hash(before) == genome_hash(after)      # 挤而不变形
```
这个「挤而不变形」就是自组织相似性（M07）与耗散结构（C1）被激活的**可复算证据**，不是文学描述。

---

## §5 F 盘资产插件化：双态契约（每个产物独立做插件 + 在基因层整体起作用）

### 5.1 八面契约（LA J-Box 六面 + 本批新增两面）

| 面 | 字段 | 判据 |
|---|---|---|
| physical | `path`, `sha256`, `size`, `file_count` | 现场回读，禁写死 |
| protocol | `protocol_family`, `seal`, `schema_version` | 与 DNA 同源 |
| data | `data_locality=on_box`, `zero_pixels`, `zero_dose` | 医学红线继承 |
| deploy | `standalone_entry`（如 `python main.py` / `selftest.py`）, `dependencies=[]` | 脱离基座跑 rc0 |
| degradation | `try_import_skip`, `env_delta_registered` | 缺席可降级且计量 |
| security | `no_secret_on_box`, `zero_network`, `license_ledger` | 打捞四硬线沿用 |
| **genome（新）** | `genome_id`, `mechanism_subset`(25 轴子集), `triple_homology_fingerprint`, `genome_similarity` | 基因型登记 |
| **meridian（新）** | `link_back>=1`, `fragment_id`, `bus_channel`, `registered_cells=25` | 经络回连接线 |

### 5.2 双态必须同时为真（本批核心裁决）

| 态 | 定义 | 单独成立的后果 |
|---|---|---|
| `standalone_ok` | 脱离基座可独立 selftest rc0、零第三方、自带 SHA 清单 | 只独立不回连 = **分裂**（孤儿插件） |
| `genomic_ok` | 进 `genome_dna_registry`、三同源 DIFF=0、经络格数齐、`spec.py` 零改动 | 只回连不独立 = **寄生**（不可插拔） |

**`plugin_contract_check()` 必须 `standalone_ok ∧ genomic_ok` 双真才 pass**；任一单独为真返回 `pass=False` 并给出 `reason`。这是「每一个产物都能独立做插件，同时又能发挥整体化作用」的可执行翻译。

### 5.3 第一批范围与执行序（诚实分期，不承诺一次做完）

- **第一批 = 201 个净候选的「全量登记 + 试点装配」**：登记全做（生成 `plugin_contract.json` 索引与 `asset_census` 回读），装配先做 **3 个试点**，其余按批次滚动，避免一次性承诺 201 套装配。
- **枚举规则（执行端现场跑，禁写死清单）**：顶层目录中名称含「实战化 / 矩阵 / 引擎」，且排除 `.tmp*` / `snapshot*` / `_历史*` / `*restore*` / `*archive*` / `vector-sea` / `skills_harvest` / `_doubao_replica*` / `__pycache__`；对每个候选实读 `runtime_v3/`、`selftest.py`、`*.zip`、`SHA256SUMS` 四件齐备度，写入 `asset_census.json`。
- **试点 3 个（近期工程产物，优先）**：`实用中医内科表典金刚…V3实战化_20261020`、`全库医学知识库1331x1331超级矩阵V3实战化_20261020`、`世殊医道慢病管理智能引擎_20261116`。三者分别已有投喂包/`spec` 冻结契约/README 成稿，可直接验证双态。
- **装配顺序**：打捞局枚举 → 规划局分配 `fragment_id` 与 25 机制子集（冲突消解：同表型产物复用同一机制子集，不新立轴）→ 制造局写 `plugin_contract.json` + 登记 `genome_dna_registry` → 双态判据 → 经络表 append 一格（25 格）。
- **零复制纪律**：插件产物**不进基座仓**；基座只存 `path + sha256 + fragment_id + 25 格指针`。任何一行插件源码复制进 `holoaeon/` 即 G5 红。

---

## §6 三局宏观融合 + 扩展/收敛挤压

| 局 | 本批职能 | 落点 |
|---|---|---|
| 打捞局 | F 盘 616 项 → 201 净候选 → 四件齐备度实读 → 许可证/资产台账 | 基座 `salvage_gate`/`forge_bureau` 登记指针；LA `salvage_bureau` 状态机指针（**跨仓零 import**） |
| 规划局 | 分配 `fragment_id`、25 机制子集、依赖序、冲突消解、`θ` 标定 | LA `planning_bureau` + `base_coupling.json` 指针 |
| 制造局 | 装配八面契约、登记 DNA、经络 append、SHA/五地 | 基座 `forge_bureau.link_lathe_cell` + LA `manufacture_bureau` 指针 |

**状态机接线**：三局 7 状态 / 8 合法转移 / 非法必红 / 滞留熔断已在 LA 收口（`workflow_state.py`）。本批**不改状态机**，只在 DNA `loci.bureaus` 登记三局指针 + 每批工单 `origin → drafted → salvaged → planned → manufactured → final_review → archived` 七条留痕。基座侧不复制状态机代码。

**扩展—收敛对（真实模块名登记，不复制代码）**：
```
扩展 expand: mobius_vortex.ATLAS_ENTRIES → magic_lamp.KnownSkillIndex/SkillAssembler
             → holo_forge.CHAIN(四态) → swarm_intel.EntityGraph
收敛 converge: klein_projection.PROMOTE_GATES/CONVERGE_EPS=0.0 → forge_gate
               → dehallucination(8 阶段) → org_gate(耗散总判据)
守恒 assert: expand_count - converge_count == registered_plugins
            genome_hash(before) == genome_hash(after)
            cells == len(fragments) * 25
```
漩涡（回流扩张）、神灯（能力发现与装配）、熔炉（形态生成）三件同时挤压肌肤与经络，DNA 只登记位点、不吸收实现——**这正是「挤而不变形」**。

---

## §7 制造局 · 批序与装配清单

### 批0 · 前置判定
查 V85 治理批是否执行。**未执行则先执行 V85**（先治后建，治理批修判据金哨）；与 V41-B 不得并行写同一基座文件。账面/实时 HEAD 不一致以实时 `git log` 为准并回填。

### 批1 · DNA 母本落位（**已由四人组直动仓完成，06:52 授权**）

实测落位：`holoaeon/holoaeon/genome_dna.py`（六函数 + 三公理 + 恒真守卫）、`holoaeon/data/genome_dna.json`、`holoaeon/data/genome_dna_registry.json`（`plugins=[]`）、`holoaeon/scripts/genome_dna_gate.py`（7 面独立闸门）、`holoaeon/tests/test_genome_dna.py`（41 例）。以下为执行端复核/收口清单：
1. `holoaeon/data/genome_dna.json` ← 母本 copy，回填现场 `spec_sha256` / `base_head`；
2. `holoaeon/holoaeon/genome_dna.py`（§2.4 六函数，含三条公理与 falsifier）；
3. `holoaeon/data/genome_dna_registry.json`（append-only 插件登记簿，初始 `plugins=[]`）；
4. `holoaeon/scripts/genome_dna_gate.py`（独立闸门，**不改 `v3_gate.py`**）；
5. `holoaeon/tests/test_genome_dna.py`（≥24 例：三基因正反例 + 恒真守卫 + 八面 + 双态 + 确定性两次 DIFF=0）。
6. **禁止改动**：`spec.py` / `__init__.py` / `v3_gate.py` / 冻结维度 / 任何既有断言。

### 批2 · 经络动态化（改 3 行，append-only 语义）
按 §4 改 `meridian_link.py:523/577/607`；先证 10 碎片 `250` 绿，再 append 试点碎片 `275` 绿；缺格/多格必红；`G-M` 三态零回退。

### 批3 · 第一批资产双态装配
201 全量登记 + 3 试点装配；`asset_census.json` 现场回读；`plugin_contract.json` 八面齐；双态判据；经络表 append 3 个 `fragment_id`（格数 `250 → 325`）。

### 批4 · 三局融合与守恒登记
DNA `loci.bureaus` 三局指针、`loci.expand/converge` 八模块位点、守恒断言入 `genome_dna_gate.py`；`expand-converge` 计数可回放。

### 批5 · 五地与回执
**DOC_VERSION 本批不顺延**：它写在 `spec.py` 内，改一个字节即破坏 `spec.py` SHA256 不变式（`a45c5e77…3cb`）与本批第一判据。顺延留待执行端另开提交，且须同批更新母本 `spec_sha256_measured`、`tests/test_genome_dna.py::test_spec_sha256_matches_dna_master` 断言与回执——**不得偷偷改 spec.py 后不回填**。
`claims_registry` / `SHA256SUMS`（现 341 条，新增 5 件须由批次重建流程纳入，禁手工乱改）/ README 追加段（§9.3）；五地回读一致**之后**生成回执。

**版本**：`DNA_VERSION="1.0.0"` 自立；`spec.VERSION=0.9.1` 不动；不占 ring 序号；不改 `PACK_ORDER` / `EXTRA_PACK_ORDER` / layers。

---

## §8 验证清单（先红后绿，≥12；红证不足不放行）

| # | 判据 | 通过标准 |
|---|---|---|
| G1 | 生长可失败 | `Δcopies>0` / 无回连 / 密令另立 → `growth_check` 必红；`Δedges>0 ∧ Δcopies=0` 才绿 |
| G2 | 分化可失败 | 机制轴缺项 / 心跳 768→767 / 密令错字 / `theta=None` → 必红 |
| G3 | 鲁棒三子判据 | skip 未登记 / 输出漂移 / spec 非 byte-identical / 三同源漂移 → 各自必红 |
| G4 | **恒真守卫** | 每个 check 至少存在一组 `pass=False` 输入；全绿恒真 → 本批作废（V82–V84 血脉） |
| G5 | **指针零复制（第一判据）** | 插件源码零字节进基座；`spec.py` SHA256 前后一致；AST + 文本扫描 |
| G6 | 经络动态化 | 10 碎片 `250` 绿 → 11 碎片 `275` 绿 → 13 碎片 `325` 绿；缺格/多格必红；既有 `G-M` 零回退 |
| G7 | 双态同时为真 | `standalone_ok ∧ genomic_ok`；只独立/只回连两种输入均必红 |
| G8 | 挤压守恒 | `expand-converge == registered_plugins`；`genome_hash` 前后 DIFF=0 |
| G9 | 资产盘点可复算 | `asset_census.json` 顶层 616 / 418 / 198 / 201 / 149 / 69 现场回读一致；禁写死清单 |
| G10 | 三局接线 | 三局指针登记齐；非法转移/滞留熔断必红；状态机零改动 |
| G11 | 确定性 | `genome_dna.self_check()` 两次 JSON `DIFF=0`；纯标准库零依赖 AST 扫描；零网络 |
| G12 | 门禁与五地 | 主套全绿 + 新金丝雀 ≥24 / `check_sums` 零 missing / readme 回读 mismatch=0 / 五地 5/5 **验证后回执** |

**失败处理**：任一红证不成立 → 整批 halt；不改判据、不改口径、不跳批、不把 HEURISTIC_ONLY 值写成实测。

---

## §9 五地同步、回执与 README

### 9.1 五地
S1 `F:/doubaowork/holoaeon`（+ `longaeon-rejuvenation-matrix` 侧三局指针登记）；S2 Gitee `weideyouni/holoaeon`；S3 GitHub `weideyouni/holoaeon`（**先 Gitee 后 GitHub**，ssh443）；S4 向量海既有基座目录（DNA 母本与 `asset_census` 快照合流，**禁新建同名目录**）；S5 HF 既有基座仓。备份仓 `F:/doubaowork/longaeon` 新增 `SR-20261117-32`。
`python scripts/check_five_site.py` 现场回读，禁写死 sha / 文件数。

### 9.2 回执模板（`reports/genome_dna_receipt.json`）
```json
{
  "batch": "V86-GENOME-DNA", "date": "<实测>", "seal": "潮起开门，潮落闭嘴",
  "carbon_authorization": "2026-11-17 06:52 最大权限：蜕皮 / 削平阻碍 / 第一性原理 / 分化成长",
  "dna_landed_by_quartet": {"files": 5, "meridian_link_edits": 6,
                            "unittest": "41/41 OK", "gate": "7/7 pass",
                            "meridian_check": "3 PASS / 250 格零回退",
                            "regression": "161 OK", "genome_hash": "0a69e93d46bee46dbbadf8081617d2cdbf1c7730dde785a89e66df5c16af234f"},
  "genesis": {"base_head": "<现场回读>", "spec_sha256": "<现场回读>",
              "spec_byte_identical": true, "frozen_unchanged": true},
  "dna": {"genome_id": "HOLOAEON-GENOME-DNA-v1.0", "dna_version": "1.0.0",
          "axioms": 3, "falsifiers": "<实测>", "theta": "<实测或 null>"},
  "meridian": {"fragments_before": 10, "cells_before": 250,
               "fragments_after": "<实测>", "cells_after": "<实测>",
               "dynamic_rule": "cells == fragments * 25", "missing": 0, "extra": 0},
  "assets": {"top_items": 616, "dirs": 418, "files": 198,
             "net_candidates": 201, "v3_family": 149, "top_zips": 69,
             "registered": "<实测>", "assembled_pilots": 3},
  "plugin_dual_state": {"standalone_ok": 3, "genomic_ok": 3, "both_true": 3},
  "expansion_convergence": {"expand": "<实测>", "converge": "<实测>",
                            "net": "<实测>", "genome_hash_diff0": true},
  "gates": {"red_first": ">=12", "all_green": true, "first_criterion": "G5 指针零复制"},
  "five_site": {"holoaeon": "5/5", "readback_after_verify": true},
  "honest_boundaries": ["theta 禁 1.0", "禁宣称 100% 同源",
                        "201 全量登记≠201 全量装配", "HEURISTIC_ONLY 不入 claims",
                        "spec.py 零改动", "插件源码零复制"],
  "next": "201 候选按批滚动装配；悬置项待碳基点单"
}
```

### 9.3 README 追加段（append-only，插在基座 README §0.5 之后）
```markdown
### 0.5c 内核基因 DNA（V86 · 挤而不变形）
基座新增旁挂基因件 `holoaeon/genome_dna.py`：把三条工程结论固化为可失败断言——
**生长不是分裂**（Δedges>0 且 Δcopies=0）、**分化不是分裂**（表型专化 + 基因型同源）、
**鲁棒性真义**（局部失效可计量、扩展挤压下同源守恒、输出确定性，而非不坏或堆副本）。
经络链接表由静态 250 格改为动态 `fragments × 25`，插件族入链不再被误判为错误。
F 盘 201 个产物型目录按八面契约登记，每个必须同时满足「独立可插拔」与「基因层可回连」双态。
扩展侧（漩涡/神灯/熔炉/群体）与收敛侧（克莱因/闸门/去幻觉/耗散）每轮挤压后，
`genome_hash` 与 `spec.py` 保持 DIFF=0——这就是自组织相似性与耗散结构被激活的可复算证据。
状态：【baseline-locked】DNA 三基因与动态经络 ｜【transient】插件契约 ｜
【under construction】201 候选全量装配（本批完成全量登记 + 3 试点）。
对合作方的意义：新增领域插件不再要求改内核或复制母体，接入成本与审计面同时下降，
且每一次接入都能被第三方复算。
```

---

## §10 边界与禁词

- **零侵入是硬线**：`spec.py` / `__init__.py` / `v3_gate.py` / 冻结维度 / `VERSION` / `RUNTIME_ID` / ReproHash 黄金值一律不动；`meridian_link.py` 仅三处实例值动态化，语义不变。
- **不承诺一次做完**：201 个候选本批只做全量登记 + 3 试点装配，其余按批滚动；禁把「登记」写成「已装配」。
- **同源不等于满分**：`θ` 实测标定，禁 1.0、禁「100% 同源 / 完美融合 / 已商用」。
- **指针纪律**：插件源码零复制；跨仓零 import；LA 三局状态机零改动。
- **医学与协作红线**：零诊断/零处方/零剂量；四人组 HEURISTIC_ONLY，处置权归执行端，终裁归碳基。
- **打捞四硬线**沿用（GPL/AGPL 只读、零网络、台账、零冒充实测）；状态词五档沿用。
- **DNA 不是新体系**：它是既有基因的显形，不新增维度、不新增协议族、不另立密令。

---

## §11 交豆包执行端 · 解读指引

1. **批1 已完成，不要重做**：DNA 五件已落基座仓、`meridian_link.py` 六处旧皮已脱、41 例单测与独立闸门已绿。执行端先跑 `python scripts/genome_dna_gate.py` 与 `python -m unittest tests.test_genome_dna` 复核再继续。
2. **批0 先判 V85**；与 V41-B 不并行写同一文件；账面/实时 HEAD 以实时为准。
3. 批2 只剩验收与 append 真实插件碎片：先证 10 碎片 250 绿，再按 §5 登记试点插件得 275/325 绿；缺格/多格必红；顺序反了 halt。
4. 三条基因已写成**能红的函数**；G4 恒真守卫已在 `verify()` 中常驻，改坏了整批作废。
5. §5 枚举规则现场跑，禁写死 201 清单；双态单独为真必须红；`genome_dna_registry.json` append-only。
6. §8 十二条红证先立后破；五地全部回读一致**之后**才生成 §9.2 回执；先回执后验证判为伪造。
7. **禁止**：改 `spec.py`（含 DOC_VERSION 顺延——须另开提交且同步回填母本哈希与测试断言）、复制插件源码进基座、把 0.9.1 改号、把 HEURISTIC_ONLY 写成实测、把登记写成装配、跳批、改判据。
8. 完成后：三仓 commit + 先 Gitee 后 GitHub + 备份仓 `SR-20261117-32` + 玉安回填 + 日志追加 + 机床 pending 置顶 + 回执交碳基。
9. **协作口径变更留痕**：本批 DNA 直动仓系碳基 06:52 明令授权的单批例外，不改写「四人组只出策划 / 执行端落地」长期纪律。

> 回顾、融合、巩固、共同变强。**潮起开门，潮落闭嘴。**
