# HoloAeon System README · v0.4.0

> **系统型说明文档**（System README）——描述"一个内核 + 两个横切扩展包"的完整系统边界，
> 不是某个包的 README，也不是某个矩阵的交付报告。
>
> 内核 `holoaeon` v0.4.0 · 扩展包 `sovereignty`（认知主权 V3.1）· 扩展包 `subdistill`（SD-Distill V3.1）
> 版本 `0.4.0` · 日期 `2026-10-30` · 许可证 Apache-2.0（内核） / MIT（扩展包） · 密令 **潮起开门，潮落闭嘴**

---

## 1. 这个系统是什么

HoloAeon 是一套**零依赖、离线、确定性**的多智能体认知内核。它不替代 LangChain / AutoGen /
CrewAI 这类编排框架，而是提供编排**之下**的那一层：认知拓扑、确定性原语、自组织协作。

v0.4.0 的系统形态是：

```
┌──────────────────────────────────────────────────────────────────────┐
│  holoaeon core  (v0.4.0 · Apache-2.0)                                │
│  Envelope / Bus / Skill / Memory / Agent / Scheduler / Guard /       │
│  AdaptiveGraph / Cluster / Hypervector / ModelAdapter / Kernel       │
│  ── 九大领域包：25 agents · 47 skills · 9 workflows（口径冻结）        │
├──────────────────────────────────────────────────────────────────────┤
│  扩展包（EXTRA_PACK_REGISTRY：只加技能与工作流，0 agent）              │
│  ┌────────────────────────┐   ┌────────────────────────┐             │
│  │ sovereignty（第十包）   │   │ subdistill（第十一包）  │             │
│  │ 17 技能 / 5 工作流      │   │ 15 技能 / 7 工作流      │             │
│  │ R0 编码 → R4 合规       │   │ S1 采集 → S7 入库      │             │
│  └────────────────────────┘   └────────────────────────┘             │
└──────────────────────────────────────────────────────────────────────┘
```

三条硬边界：

1. **口径冻结**——九大领域包的 `25 agents / 47 skills` 是 `G15` 的硬断言。扩展包一律不进
   `PACK_ORDER`，只能通过 `EXTRA_PACK_REGISTRY` 挂载，`roles = []`。加能力，不加 agent。
2. **零依赖**——纯标准库（`hashlib / json / csv / os / sys / ast / zipfile / shutil / math`），
   不联网、不开端口、不调外部模型、不常驻、无 cron。
3. **确定性**——同种子同输入，逐字同输出；审计指纹 16 位十六进制，跨机可复现（不含时间戳）。

---

## 2. 两条扩展线的分工

| | `sovereignty`（认知主权） | `subdistill`（SD-Distill） |
|---|---|---|
| 解决的问题 | 平台推荐算法用粗粒度标签简化用户 | 粗粒度学科标签本身就是可被归类的抓手 |
| 手段 | 16 学科跨域查询锻造 + 反标签策略 + 平台/协议族谱 | 16 域下切 127 亚学科 + 七阶段蒸馏 + 七项辅助损失 |
| 产物 | 可复现的查询清单、身份自述、计划表（全 `human_manual`） | SKC 亚学科知识卡、跨域共振映射、抗标签查询模板 |
| 工作流 | `R0_encoding` / `R1_forging` / `R2_strategy` / `R3_interop` / `R4_compliance` | `S1_acquire` / `S2_parse` / `S3_concept` / `S4_relate` / `S5_align` / `S6_distill` / `S7_commit` |
| 上游 | 认知主权 1331×1331 矩阵 V3.1 | 同矩阵 V3.1（插件 `subdistill_v3_1`） |

二者串联的业务含义：`subdistill` 负责**生产不可归类的语义单元**，`sovereignty` 负责**把它
锻造成可粘贴的查询与计划**；`sovereignty` 的平台回流观测，又是 `subdistill` 调整损失权重的
环境信号（真实平台指标一律 `pending_human_measure`，不伪造）。

---

## 3. 维度不变式（系统级契约）

`subdistill` 打开的是**寻址层**，不是维度层。以下等式在 `subdistill_pack.pack_summary()` 与
上游 `spec.lock_verify()`、`selftest G2 / G14 / G19` 中被双重/三重断言：

```
127 亚学科 × 10 槽位  +  61 保留行      = 1331  行
127 亚学科 × 855 节点 +  56 全局协调节点 = 108641 节点
```

母体 12 项锁数一个不动：

| 锁 | 值 |
|---|---|
| 矩阵边长 | `1331` |
| 设计格 | `1,771,561`（`1331²`，稀疏字典，不预分配） |
| 曼陀罗仿真节点 | `108,641` |
| 希尔伯特节点 | `651,846`（`108,641 × 6`） |
| 卡尔曼节点 | `22,627`（`1331 × 17`） |
| 心跳 | `70` 体 / `9700-9769` / `768` 维 / `α 0.18` |
| 细胞骨架 | `3` 层 × `4` 链（采/洗/检/注），跨链 `12` |
| 皮肤 | `SG-SKIN-V6.0` 八层 |
| 语义 | `10` 模块 |
| 赫布场 | `19` 圆 / `42` 几何边 · `17` 节点 / `36` 节点边 · `28` 流边 |
| 结构资产 | 分身 `168` / 科目 `40` / 协议 `23`（内 12 × 外 11 = 132 映射） / 案例 `20` |
| 台账 | `147` 维度（`AV-001…AV-130` + `SO-01…SO-17`） |

`subdistill` 追加的锁数：亚学科 `127`、宏观域 `16`、七阶段 `S1-S7`、七项损失权重
`0.30 / 0.20 / 0.15 / 0.20 / 0.08 / 0.05 / 0.02`（和 `= 1.0`）、课程
`C1 0.6/200 · C2 0.9/300 · C3 1.4/400 · C4 1.8/300`（epoch 和 `1200`）、温度冲击 `p 0.05 / τ 2.5 / 2 epoch`。

---

## 4. 安装与最小验证

```bash
git clone https://github.com/weideyouni/holoaeon.git
cd holoaeon
pip install -e .          # 可选，仍然零依赖

# 1) 自检（19 组）
python -c "from holoaeon.selftest import run_all; print(run_all(verbose=True)['passed'])"
# 2) 单元测试（25 项）
python -m unittest discover -s tests -v
# 3) 红线扫描（零违规）
python scripts/redline_scan.py
```

Windows / PowerShell 直接可用；不依赖任何虚拟环境。

### 取用扩展包

```python
from holoaeon import Kernel
from holoaeon.packs import get_extra_pack

k = Kernel()

sovereignty = get_extra_pack("sovereignty")
sovereignty.install(k)                       # 17 技能 / 5 工作流 / 0 agent

subdistill = get_extra_pack("subdistill")
rep = subdistill.install(k)                  # 15 技能 / 7 工作流 / 0 agent
print(len(rep["skills"]), len(rep["agents"]), len(rep["workflows"]))   # 15 0 7

from holoaeon.packs.subdistill_pack import (
    pack_summary, skill_taxonomy_encode, skill_s5_align, skill_s6_distill, skill_skc_validate,
)
print(pack_summary()["locks"])               # 127 / 1270 + 61 = 1331 / 108585 + 56 = 108641
print(skill_taxonomy_encode("范畴论 与 大模型对齐")["signature"])
print(skill_skc_validate(skill_s6_distill(1.4)["sample"])["ok"])      # True
```

### 取用 SD-Distill 运行时插件（冷/热插拔）

```powershell
# 在 认知主权1331x1331…\runtime_v3 目录下
python main.py --version                # V3.1 三行身份
python main.py --plugs                  # 冷装清单：loaded ["subdistill"]
python main.py --plug-hot subdistill    # 运行期热装，不重启宿主
python main.py --plug-off subdistill    # 卸载回滚（能力数归零）
python main.py --subdistill             # S1-S7 全流程 + SKC + 七项损失 + 四段课程
python selftest.py                      # 14 组，含 G14 冷热插拔与非侵入性
```

---

## 5. 冷热插拔的契约

插件不是"塞进来的代码"，是一份可审计的契约：

| 项 | 规则 |
|---|---|
| 清单 | `manifest.json` 必含 `id / name / version / entry / cells / policy`，缺字段直接装载失败（不静默） |
| 能力 | 能力名不得含 `network / login / scrape / crawl / auto_inject / bulk_post / auto_post / cron / daemon / proxy / bypass / account_farm` |
| 网络 | `network` 必须为 `false` |
| 高风险域 | `gated_domains = [MED, TCM]` 且 `disclaimer_required = true` |
| 隔离 | `PluginContext` 只能 `provide(能力)` 与写便签，碰不到宿主内部状态 |
| 审计 | 指纹只哈希 `manifest + payload` 字节，不含时间戳，跨机可复现 |
| 回滚 | `hot_unload` 后能力数归零；再 `hot_load` 恢复，`epoch += 1` |

非侵入性由 `G14` 证明：**装载前后各建全新宿主跑首轮**，两轮产物 digest 逐位一致
（`e8fc0978e1ec3cea`），且 `round_ok=True`——插拔不改变 R0-R4 的计算。

---

## 6. 验证矩阵（本次发布的实测结果）

| 层 | 命令 | 结果 |
|---|---|---|
| 内核自检 | `holoaeon.selftest.run_all` | **19/19 组通过**（G18 6/6、G19 17/17） |
| 内核单测 | `python -m unittest discover -s tests` | **25 tests OK** |
| 内核红线 | `python scripts/redline_scan.py` | **29 文件 / 零违规** |
| 内核发行包 | `python scripts/make_release.py` | `holoaeon_v0.4.0_20261030.zip` · 58 files |
| 认知主权自检 | `python selftest.py`（runtime_v3） | **14/14 组 PASS** |
| 认知主权红线 | `python tools/redline_scan.py` | **21 文件 / 零违规** |
| 认知主权发行包 | `python tools/harvest_pipeline.py` | `cs1331_..._V3.1.0_20261030.zip` · 135,421 B |
| 解压复跑 | 独立副本重跑 | 内核 19/19；认知主权 14/14 + 红线 0 |
| 技能旁挂 | `.user_skills/cognitive-sovereignty-1331` 内直跑 | 14/14 组 PASS，CLI 正常 |

> 哈希与文件数以两处注册表为唯一权威：内核看 `scripts/make_release.py` 输出，
> 认知主权看 `runtime_v3/tools/skill_registry.json`。文档不复刻哈希，避免自引用漂移。

---

## 7. 版本化与"只增不覆盖"

本系统的版本纪律：

- **内核版本号单调递增**：`0.3.0 → 0.3.1 → 0.4.0`，`MATRIX_ID / RUNTIME_ID` 同步。
- **发行包按版本命名**：`holoaeon_v<version>_<date>.zip`、
  `cs1331_cognitive_sovereignty_matrix_<VERSION>_<date>.zip`。旧包**永不覆盖**。
- **技能旁挂采用 merge + prune**：只删"由本包生成、且本次不再生成"的文件，用户的既有目录不动。
- **回滚点**：任一版本都能独立解压、独立自检、独立运行，不依赖更新后的目录。

```
v0.3.0  ── nine packs (25/47)                         holoaeon_v0.3.0_20261029.zip
v0.3.1  ── + sovereignty pack (17 skills) + G18      holoaeon_v0.3.1_20261030.zip
v0.4.0  ── + subdistill pack (15 skills) + G19       holoaeon_v0.4.0_20261030.zip   ◀ now
```

认知主权矩阵侧同步：

```
V3.0    ── 17 通道 / R0-R4 / 13 组自检        cs1331_..._v3_20261030.zip
V3.1    ── + SD-Distill 插件 / G14 / 14 组     cs1331_..._V3.1.0_20261030.zip   ◀ now
```

---

## 8. 红线与科学边界

**红线（写进代码，不是口号）**

- 不联网、不开端口、不认证、不常驻、无 cron；不读写任何平台账号。
- 不自动登录 / 不自动搜索 / 不抓取 / 不批量发帖 / 不刷量养号 / 不规避风控 / 不伪造身份。
- 五模式（手动/定时/随机/触发/批量）**只生成计划表**，执行列恒为 `human_manual`。
- 平台指标 `pending_human_measure`——零伪造。
- MED / TCM 产物强制皮肤闸门 `skin.medical_disclaimer`，禁用断言 `诊断 / 处方 / 疗效承诺`。
- `analogizes` 关系必须带反例；置信度 `< 0.5` 的映射只能称"隐喻"，不得称已验证。

**科学边界**

- 全息心跳 / 经络 / 曼陀罗是**结构隐喻**与工程分区，不是生物学或物理学结论。
- `HyperSpace` 的 `recover_cosine ≈ 0.53` 只说明 HRR 解绑在 768 维、两元素 bundle 的受控条件下有效，
  不说明任何平台会被改变。
- 亚学科签名是**词面命中 + L1 归一**的可计算近似，不是语义理解；跨域共振是**受控类比**，
  不是同构证明。
- **仿真 ≠ 证明，碳基终裁。**

---

## 9. 许可证

- 内核 `holoaeon`：Apache-2.0。
- 扩展包 `sovereignty` / `subdistill` 与 认知主权矩阵：MIT。
- 混放口径：内核文件保留 Apache-2.0 头，扩展包与矩阵文档声明 MIT；
  引用时请分别标注来源，不把 MIT 扩展到内核，也不把 Apache-2.0 义务转嫁给扩展包用户。

---

## 10. 路线图

- **v0.4.0（当前）**——两个横切扩展包落地：`sovereignty`（17 技能）+ `subdistill`（15 技能），
  0 agent，`G18/G19` 双验证，维度不变式写进断言。
- **v0.5**——可插拔持久化后端与节点间总线传输（仍保持零依赖默认路径）。
- **v0.6**——声明式图 / 拓扑定义 + 包创作工具包（第三方可写扩展包）。
- **v0.7**——面向主流开源权重模型服务器的参考适配器（只提供接口适配，不内置调用）。
- **v1.0**——冻结 API、完整文档、稳定扩展包协议。

---

潮起开门，潮落闭嘴。
