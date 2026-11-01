# B0 基线票据 · V4 冷热插拔赋能升级（十二批次第 1 次升级）

- 批次：**B0 基线冻结**（十二批次中的第 1 次升级 = 第一次升级）
- 主张分身：P2 筑基（先立契约与闸门地基，再谈融合）
- 冻结时间：2026-11-02 01:05–01:25（+08:00）
- 现场复算人：MainAgent（本地 `WIN-PIB9JHIKQ43`，Python 3.13.16，PowerShell）
- 证据等级：全部 `evidence_class=simulated`　仿真 ≠ 证明，碳基终裁
- 密令：潮起开门，潮落闭嘴

---

## 一、完美判据（SOP-1：7/7 全绿 + 维度锁 JSON 存在 + 两侧可读到锁）

| # | 闸 | 命令 | 实测 | 验收点 |
|---|---|---|---|---|
| G1 | v3_gate | `python scripts/v3_gate.py --json reports/gate_b0_v4.json` | **32/32 PASS** | A1 detail = `{agents:25, skills:47, packs:9}` |
| G2 | unittest | `python -m unittest discover -s tests` | **Ran 34 OK** | 三套 34/21/5 未减 |
| G3 | launch 自检 | `python scripts/launch_local.py selftest` | **25/25** | G25 persona_quartet 8/8 |
| G4 | 技能矩阵 | `python scripts/verify_skill_matrix.py` | **passed=17，verdict=PASS** | `matrix_id=SG-MATRIX-SKILL-HOLOAEON-V3.0`，`digest=9a565741e1f72ab7` |
| G5 | 红线扫描 | `python scripts/redline_scan.py` | **67 文件，零违规** | 无 import 越界、无 eval/exec |
| G6 | 融合自检 | `python scripts/verify_fusion_upgrade.py` | **17/17** | 第 10 扩展包装卸/协议/契约全绿 |
| G7 | ivsa 执行层 | `cd …\integrative-rehab-vsa; python main.py` | **21/21 组 PASS，断言 21/21** | 医学红线声明完整 |

**7/7 全绿 → 判据通过。**

### 黄金值复算（确定性证据链）

```
[1/3] DIFF=0  run1=2fc892cf9af6e755  run2=2fc892cf9af6e755  equal=True
敏感性  base=2fc892cf9af6e755  tampered=f42c8229ee5acd73  sensitive=True
fails=[] warns=[] REPRO_EXIT=0
```

`python scripts/check_dimension_lock.py` → `[PASS] dimension_lock.json 12 维度 + 7 闸 + 0 violation 全部一致`
`diff0_hash=2fc892cf9af6e755 tamper=f42c8229ee5acd73 spec_version=0.9.1`

---

## 二、V4 基线锁（14 维，12 维原锁 + 融合扩展 2 项）

| 维度 | 锁定值 | 来源 | 可否变 |
|---|---|---|---|
| D01 agents | **25** | v3_gate A1 | 否 |
| D02 skills | **47** | v3_gate A1 | 否 |
| D03 packs（核心九包） | **9** | v3_gate A1 | 否 |
| D04 spec.VERSION | **0.9.1** | spec.py | 否（写进回执，动了黄金值漂移） |
| D05 DOC_VERSION | **0.9.4-fusion** | fusion manifest | 可随 V4 系列推进，单列不混 0.9.1 |
| D06 EXTRA_PACK_ORDER | **10** | packs `__init__` | 可加（旁挂，不进 A1） |
| D07 单测三套 | **34/21/5** | tests | 只许加不许减 |
| D08 launch 自检 | **25/25** | G1–G25 | 只许加不许减 |
| D09 diff0_hash | **2fc892cf9af6e755** | bench_public | 否 |
| D10 tamper_hash | **f42c8229ee5acd73** | 敏感性 | 否 |
| D11 v3_gate | **32/32** | gate_b0_v4.json | 只许加不许减 |
| D12 ivsa 自检 | **21/21** | main.py | 否 |
| D13 融合自检 | **17/17** | verify_fusion_upgrade | 只许加不许减 |
| D14 技能矩阵 | **17/17** | verify_skill_matrix | 只许加不许减 |

机读锁文件：`reports/b0_lock_v4fusion.json`（`lock_id=B0-LOCK-V4-FUSION-20261102`）。
仓库内另有一份 01:04 产出的 `reports/dimension_lock.json`（`lock_id=B0-LOCK-V2.0-REHAB-FUSION`）与本票据**并行，逐项核对一致**；本票据不覆盖它，只做增补。

---

## 三、自动匹配技能（B0 本轮用得到的候选池）

- 索引来源：`data/skill_matrix_index.json`（`count=1229`，`digest=9a565741e1f72ab7`，五根去重后指纹）
- 打分口径：`Σ(关键词权重×命中) + 0.6×2~4 字滑窗重叠率`，按 score 降序、同分按 name 升序（两次跑完全一致）
- 命中池 **365** 条（阈值 > 0.6），生成器 `scripts/b0_match.py`（纯标准库、离线、确定性）
- 产物：`data/B0_自动匹配技能.csv`（365 行，含绝对路径）、`data/B0_自动匹配技能.json`（分布摘要）

**Top 8（可直接用于 B0/B1a）**

| 排名 | 技能 | 机制 | 得分 | 命中词 |
|---|---|---|---|---|
| 1 | avatar-person-quartet-1331 | hebbian_field | 21.0444 | 四人/数字分身/quartet/语义/赫布/经络/心跳/骨架/皮肤 |
| 2 | slv2-matrix-base-1331x131 | hebbian_field | 15.0444 | 契约/基座/语义/心跳/骨架/皮肤 |
| 3 | silicon-bridge-code-framework | cytoskeleton | 14.0444 | 冷热插拔/热插拔/契约 |
| 4 | qilu-holo-avatar-matrix | hebbian_field | 13.0889 | 冷热插拔/热插拔/数字分身 |
| 5 | shuzi-fenshen-sidecar-deploy | cytoskeleton | 13.0889 | 冷热插拔/热插拔/数字分身 |
| 6 | coldhot-upgrade-package-harvest | holographic_heartbeat | 13.0444 | 冷热插拔/热插拔 |
| 7 | holoaeon-v2-empower-upgrade | holographic_heartbeat | 13.0444 | 冷热插拔/热插拔/赋能升级 |
| 8 | shengui-shenma-dual-system-base-super-matrix | hebbian_field | 13.0444 | 基座/矩阵/语义 |

机制分布：`hebbian_field 193 / skin_v6 77 / holographic_heartbeat 51 / cytoskeleton 35 / semantic_bus 6 / unmapped 2 / meridian 1`。
诚实注：**本轮只读索引打分，未 import、未执行任何外部技能**（`external_skills_executed=0`）。候选池 ≠ 准入库；准入仍走 B7 每批 ≤5 + 人工签字。

---

## 四、B0 做了什么 / 没做什么

**做了**
1. 七闸现场重跑并留档（`reports/gate_b0_v4.json`、`reports/repro_core.jsonl`）。
2. 14 维锁落成机读 JSON，可被 `check_dimension_lock.py` 复算。
3. 1229 → 365 的确定性技能候选池，带绝对路径与命中词，供 B1a 直接挑。
4. 与既有 B0 票据交叉核对，确认同一组数字（无版本歧义）。

**没做（留给后续批次，不假装完成）**
- B1a 契约字段草案文档（下一批，产出 `contract_v1_draft.md`）
- B3 用途二次分类 1229 行、B4 试点 20 例、B5 语义 19→≥60、B6 赫布落盘、B7 准入签字、B8 ivsa v1.2 插件
- 未动 `spec.VERSION`、未动九核心包、未拷 ivsa 任何代码

---

## 五、下一批入口条件（B1a 契约字段草案·P2）

开批前置：本票据 7/7 仍绿 + `b0_lock_v4fusion.json` 未被改动（哈希一致）+ 无人跨批并行。
B1a 完美判据：`REQUIRED`(6) + `OPTIONAL`(4) 全列出、每字段有类型与示例、`contract.validate()` 返回 ok、评审通过。

---

## 六、签收

- 判据：**7/7 全绿 · 14 维锁齐 · 两侧可读锁文件 → 通过**
- 未闭合风险：折叠式风险清单见 `03_内外融合协议与冷热插拔SOP.md` §9；热卸载残留 27 个 watch（调度器无公开移除接口，已知坑 V4-9）
- 封缄：潮起开门，潮落闭嘴。
