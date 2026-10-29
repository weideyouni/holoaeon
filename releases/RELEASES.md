# HoloAeon 认知主权 SD-Distill 亚学科辅助蒸馏模块 · 冷热插拔赋能升级包 · RELEASES

> 版本化目录：**只增不覆盖**。每个版本一个目录入口、一份说明、一份哈希。
> 选择版本 = 选择下表的 tag；任何版本都可独立解压、独立自检、独立运行。
> 密令 **潮起开门，潮落闭嘴**

---

## 版本索引

| 版本 | Tag | 日期 | 内核包 | 认知主权包 | 自检 | 状态 |
|---|---|---|---|---|---|---|
| **v0.4.0** | `v0.4.0` | 2026-10-30 | `releases/holoaeon_v0.4.0_20261030.zip`（59 文件 / 152,485 B） | `releases/cs1331_cognitive_sovereignty_matrix_V3.1.0_20261030.zip`（41 文件 / 135,421 B） | 内核 **19/19** · 认知主权 **14/14** | 当前 |
| v0.3.1 | —（未打 tag，仅本地留档） | 2026-10-30 | `holoaeon_v0.3.1_20261030.zip`（本地 F 盘，56 文件 / 128,196 B） | — | 内核 18/18 | 历史 |
| v0.3.0 | — | 2026-10-29 | `holoaeon_v0.3.0_20261029.zip`（本地 F 盘，120,521 B） | — | 内核 17/17 | 历史 |

> 说明：`v0.3.1` 与 `v0.3.0` 的发行包在打本次版本之前生成，未同步进本仓库 `releases/`；
> 它们**未被覆盖、仍在本地 F 盘留存**，可随时按需补入。本目录自 `v0.4.0` 起对所有新版本
> 强制落库。

---

## v0.4.0 · 本期内容（SD-Distill 冷热插拔赋能升级包）

### 一句话

把"16 大域 → 127 亚学科"的知识代谢层做成**冷热插拔插件**，同时以 `DomainPack` 形态
融合进 HoloAeon 内核；**产出物维度不变**——母体 12 项锁数一个不动，九包核心
`25 agents / 47 skills` 断言未破。

### 交付清单

| # | 交付物 | 位置 | 说明 |
|---|---|---|---|
| 1 | 插件宿主 | `holoaeon/packs/…` + 认知主权 `runtime_v3/so1331_runtime/plugins.py` | `discover / cold_boot / hot_load / hot_unload / capabilities / status`；上下文隔离，能力名黑名单，MED/TCM 强制免责 |
| 2 | 插件本体 | `plugs/subdistill_v3_1/`（manifest + plugin + payload 双 JSON） | 12 能力；`Taxonomy` / `ResonanceSeed` / `TeacherBank` / `DistillationPipeline S1-S7` / `LossBank` / `CurriculumScheduler` / `AntiLabelScorer` / `validate_skc` |
| 3 | 权威数据 | `payload/taxonomy_127.json`（26,166 B）· `payload/resonance_seed_50.json`（9,659 B） | 127 项亚学科（16 域分布经断言校验）；50 组跨域共振种子**每条带反例**，置信度 <0.5 只可称隐喻 |
| 4 | 内核融合包 | `holoaeon/packs/subdistill_pack.py`（第十一包） | 15 技能 / 7 工作流 / **0 agent**；`EXTRA_PACK_REGISTRY` 挂载，不进 `PACK_ORDER` |
| 5 | 内核数据 | `data/taxonomy_127.json` | 供内核侧读取；缺失时技能降级为结构输出而不报错 |
| 6 | 双重自检 | 内核 `G19 subdistill`（17 条断言）· 认知主权 `G14 冷热插拔`（20 余条断言） | 维度等式、管线贯通、SKC 校验、非侵入性、卸载回滚 |
| 7 | 系统型说明 | `SYSTEM_README.md` | 系统边界 / 维度不变式 / 插拔契约 / 验证矩阵 / 版本纪律 |
| 8 | 发行包 | `releases/` 两个 zip + `SHA256SUMS.txt` | 版本化、不覆盖 |

### 维度不变式（写进断言，不是文档口号）

```
127 亚学科 × 10 槽位  +  61 保留行      = 1331   行
127 亚学科 × 855 节点 +  56 全局协调节点 = 108641 节点
```

域分布：MATH 10 / LOGIC 8 / CS 8 / PHYS 10 / BIO 8 / MED 8 / PHIL 8 / HIST 8 / LIT 7 /
AEST 7 / SEMI 7 / SOC 8 / TCM 8 / AI 8 / FUT 7 / SF 7 = **127**。

七项损失权重 `0.30 / 0.20 / 0.15 / 0.20 / 0.08 / 0.05 / 0.02`（和 `= 1.0`）；
课程 `C1 0.6/200 · C2 0.9/300 · C3 1.4/400 · C4 1.8/300`（epoch 和 `1200`）；
温度冲击 `p 0.05 / τ 2.5 / 2 epoch`（SHA 前 8 位十六进制取模，**确定性**触发）。

### 验证记录（实测，非推断）

| 验证 | 结果 |
|---|---|
| 内核自检 | `19/19` 组通过；`G15 agents=25 skills=47` 未被破坏；`G18 6/6`；`G19 17/17` |
| 认知主权自检 | `14/14` 组通过；`G14` 明细 `caps=12 skc=3 committed=3 digest=e8fc0978e1ec3cea` |
| 冷热插拔 | 冷装 `loaded ["subdistill"]`；热装 `mode=hot`；卸载后能力数 `0`；再热装恢复 `12` |
| 非侵入性 | 装载前后各建全新宿主跑首轮，两次 digest **逐位一致**，`round_ok=True` |
| 管线 | S2 打标覆盖 `0.6`（codes 含 `MATH-09 / AI-03 / LOGIC-04`）→ S4 关系边 → S5 配对 3 单元（`R001/R002/R009`）→ S6 SKC 3 → S7 入库 3，SKC 校验 **3/3** |
| 单元测试 | 内核 `25 tests OK` |
| 红线 | 内核 29 文件零违规；认知主权 21 文件零违规 |
| 解压复跑 | 内核包独立副本 `19/19`；认知主权包独立副本 `14/14` + 红线 0 |
| 技能旁挂 | `.user_skills/cognitive-sovereignty-1331` 内直跑 `14/14` + CLI 正常 |
| 打包幂等 | 认知主权 11 步收割连跑两次，zip **同大小同哈希** |

### 升级路径（从 v0.3.1 起）

1. `git checkout v0.4.0`（或解压 `releases/holoaeon_v0.4.0_20261030.zip`）。
2. 内核侧：无需改动既有代码，`EXTRA_PACK_REGISTRY` 自动多出一个 `subdistill`。
3. 认知主权侧：用发行包覆盖 `runtime_v3`，或保留原目录、只把 `plugs/` 与 `so1331_runtime/plugins.py` 拷入。
4. 回滚：直接切回 `v0.3.1` 对应的本地 zip；插件目录不动内核，卸载即归零。

---

## 下载与校验

```powershell
# 两个发行包与本文件的 SHA256 权威记录：releases/SHA256SUMS.txt
Get-FileHash .\releases\holoaeon_v0.4.0_20261030.zip -Algorithm SHA256
Get-FileHash .\releases\cs1331_cognitive_sovereignty_matrix_V3.1.0_20261030.zip -Algorithm SHA256
```

---

潮起开门，潮落闭嘴。
