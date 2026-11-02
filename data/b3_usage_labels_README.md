# B3 用途二次分类 · 口径说明

`usage_id = SG-B3-SKILL-USAGE-LABELS-V1`
输入：`data/skill_matrix_index.json`（`count=1229`、`digest=9a565741e1f72ab7`）
产出：`data/skill_usage_labels.csv`（1229 行）、`data/b3_sample_verdicts.json`（抽样 40 复核）
校验：`scripts/check_skill_usage_labels.py`（U1–U7）→ `reports/b3_usage_labels_check.json`

## 一、五值语义

| 值 | 含义 | 融合中的用法 |
|---|---|---|
| K | 知识源：内容/资料/知识结构，可检索可引用 | 进知识层，不执行 |
| M | 方法学：方法/模型/算法/流程/范式 | 可被契约调用的 `skill` 候选 |
| T | 工具链：命令、脚本、部署、平台能力 | 只登记能力，不 import 不执行 |
| X | 无关：与中西医融合康复域无关 | 明确不纳入，写进票据不藏着 |
| U | 待判：证据不足 | 挂账，不猜 |

## 二、判定是两段，不是一次

1. **stage1（词面证据）**：对四类分别打分
   `score(c) = Σ(关键词权重 × 命中) + 0.6 × 2~4 字滑窗重叠率`，
   取 argmax，且 `score ≥ 0.80` 才算判定。
   —— 必须**逐条对各类打分再取最大**；若先把一类的关键词拼成一整段再算重叠率，全部条目会塌到同一类（这是本工程踩过的坑，已规避）。
2. **stage2（域证据兜底）**：索引侧 `domain` 有证据（`domain_score > 0` 且非 `unmapped`）时，按域定性表落 K/M/T/X。
3. **stage2-weak（弱证据档）**：域未归域的条目，`score ≥ 0.35` 才收，否则进 U。

实测 stage 分布：stage1 = 964、stage2 = 251、stage2-weak = 3、undecided = 1。

## 三、实测分布（以实算为准）

| 标签 | 实测 | 投喂包给的期望值 | 差 |
|---|---|---|---|
| K | 318 | 893 | −575 |
| M | 731 | 162 | +569 |
| T | 144 | 78 | +66 |
| X | 35 | 15 | +20 |
| U | 1 | 81 | −80 |
| 合计 | 1229 | 1229 | 0 |

**差异原因（不掩饰）**：投喂包的数字是"希望融合率好看"的估算，不是从索引实算的。索引 1229 条里绝大多数是可调度的方法学/矩阵类技能（M 天然占多数），K 类真实只有 318。若强行凑到 K=893，等于把方法学条目伪装成知识源——这会让 B5 语义扩容和 B7 准入全部建立在错的分母上。**因此本批以实算为准，投喂包期望值作为"待复核项"记录，不做对齐。**

## 四、抽样 40 复核

抽样规则固定：`rows 按 name 升序`，取 `idx = i*n//40`（i=0..39，n=1229），**无随机、可复现**。
判据：`agree ≥ 36/40`（90%）。实测 **agree=37、disagree=3**，三条改判均写明理由：

| 条目 | CSV 判 | 复核判 | 理由 |
|---|---|---|---|
| `asset-sunwu-war` | M | **K** | 教学/知识资产；词面命中「矩阵/模型」导致 M |
| `refinery-truth-workshop` | K | **M** | 语义真值车间=信息瓶颈保真压缩方法；命中「知识」导致 K |
| `wdrama-qc-tech-v3` | M | **T** | 技术质检=可执行检测工具；命中「流程/定位/匹配」导致 M |

三条都是 K/M/T 边界案例，不是事实错误。**边界案例记录在案，不靠回改权重硬凑 40/40**——否则等于用样本调参，第 41 条照样错。

## 五、可复跑

```
python scripts/classify_skill_usage.py            # 生成 CSV（确定性，无时间戳无随机）
python scripts/classify_skill_usage.py --check    # 复跑字节一致
python scripts/check_skill_usage_labels.py        # U1–U7 判据
python -m unittest tests_contract.test_skill_usage_labels -v
```

判据（U1–U7）：行数与序一致 / 五值合法无空 / 合计 1229 且 U ≤ 20 / stage 与 reason 合法 / 抽样 40 且 agree ≥ 36 / 复跑字节一致 / CSV 指纹与复核件登记值一致。

`evidence_class=simulated`：分类结果是离线确定性规则输出，不代表任何真实技能的运行时能力。
