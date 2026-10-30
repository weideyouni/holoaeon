# UPLIFT · 补齐短板赋能升级包（U1–U6）

> 版本：v0.9.0 ｜ 包 key：`uplift` ｜ 矩阵：`SG-MASTER-UPLIFT-1331x1331-EXT-V1.0`
> 上游：`SG-MASTER-NEPHRON-1331x1331-EXT-V1.0` + `HOLOAEON-UPLIFT-SPEC-U1U6-V1.0`
> 密令：潮起开门，潮落闭嘴

---

## 1. 这包是什么

v0.8.0 的 nephron P0 交完之后，仓库里躺着六个已经实证的短板（S1–S6）。UPLIFT 把它们的修复**连同验证方式**一起收进一个可判定的扩展包：24 个技能全部是纯函数，输入事实、输出 `PASS / FAIL / UNCHECKED`。

它不是"新器官"，是**修桥**：0 agent、不加行、不加节点，维度不变式原样成立（1331 行 / 108641 节点）。

**它保护了哪条立场**：取舍留痕 + 代价显式——十个冲突逐条摊开，未实测的项一律写 `untested`。

## 2. 六单元与投喂指定顺序

| 顺序 | 单元 | 对应短板 | 实证（代码级） | 维度 |
|---|---|---|---|---|
| 1 | U1 确定性修复 | S1 | `cluster.py::_report()` 过滤 `__forward__` 后无排序；`_fft` 就地置换入参 | 正确性 |
| 2 | U6 生态基建 | S6 | 无 CI、无模板；徽章 `tests-24` / `selftest-16%2F16` 与实测不符 | 生态成熟度 |
| 3 | U3 实测闭环 | S3 | `docs/nephron.md` L1/L2 恒为 `pending_human_measure` | 生产就绪 |
| 4 | U5 匹配升级 | S5 | `skill.py` 中文按单字切分，仅 Jaccard + 标签权重 | 技术定位 |
| 5 | U2 宿主模型桥 | S2 | `model_adapter.py` 全篇 simulated | 生产就绪 |
| 6 | U4 裁决 + P1 | S4 | `§12` 十条开放问题未裁定；P1 细则缺失 | 技术定位 |

顺序理由：先锁正确性 → 再铺基建（CI 是后续一切实测的载体）→ 拿到实测基线 → 升匹配 → 接真实模型 → **最后**写 P1（P1 依赖前五项的字段与基线）。

## 3. 十处审视与修正（X1–X10）

投喂稿被当作**待审稿**而不是图纸。十处里没有一处是"投喂说得对但我不想做"，全部是字面与代码/口径的冲突。

| ID | 冲突点 | 择定 | 理由（一句话） |
|---|---|---|---|
| X1 | 只按 `agent_id` 排序 | B：`(agent_id, 记录规范化指纹)` | 同 agent 多记录会并列，并列处仍按出队序——半个修复 |
| X2 | "6 agent × 30 轮 → 180 条" | B：线程级断言 6 条序列一致 + 纯函数全序测试 | `run()` 只在首轮投递任务，改语义撞 U1.2 非目标 |
| X3 | 要求 CI 三版本全绿 | B：交 workflow + `untested` | 本机无 Actions 执行器；投喂自己也禁止未跑就写 passing |
| X4 | 徽章写死 25 | B：写实测 34，并修 selftest 徽章 | 徽章与实测不符就是系统性撒谎；两处都过期 |
| X5 | A1/A2 改 `measured` | B：`measured_with_scope` | 改状态合法，改口径不合法：P0 无生产 writer |
| X6 | 需真 Ollama 出 `mode=live` | B：实测"无 Ollama 分支"，live 标 `untested` | echo 冒充 live 正是本项目要防的"被 AI 忽悠" |
| X7 | 审计写盘 vs 确定性 | B：只记哈希 + 序号，`.gitignore` | 桥的意义是把非确定隔离并留痕，但留痕不留明文 |
| X8 | `0.5·重叠个数 + 0.5·dice` | B：`0.5·Jaccard + 0.5·dice2 + 0.05·tag_hit` | 量纲不齐会让短查询虚高，且破坏既有 25 条单测 |
| X9 | 英文 3-gram 兜底 | B：2-gram 主 + 词级 3-gram 取 max | 取 max 不改已命中结果，只在形变时兜底 |
| X10 | O-1 新增 `after_summary` 字段 | B：不加字段，用 `summarized ∩ admitted` 表达 | 字段一动，字典/样例/回放器全返工，撞维度不变 |

## 4. 四处核实（F1–F4）

| ID | 核实内容 | 结论 |
|---|---|---|
| F1 | `assert r['ok'] and r['failed']==0` 是否可用 | `run_all()` 确返 `groups/passed/failed/ok/details`，投喂写法可用 |
| F2 | 错误分型只写三类 | 补 `bad_json` + 兜底，共 4 类 + 1 兜底，桥永不抛异常 |
| F3 | `--check` 对 echo 无探活路径 | echo 直接判可用，退出码 0（离线后端无网可探） |
| F4 | 示例 05 无桥会抛异常 | 捕获后统一 `skip` 退出 0，不阻塞 CI |

## 5. 本轮自身缺陷（M1–M5）

写码当天被抓到并修掉的五处，全部登记，因为**同类缺陷下次还会犯**：

| ID | 缺陷 | 被抓方式 | 修法 | 教训 |
|---|---|---|---|---|
| M1 | `REMOTE_ENV` 拼成 `HOLAEON_ALLOW_REMOTE` | 远程放行用例仍被拒 | 改回 `HOLOAEON_ALLOW_REMOTE` | 开关拼错时 fail-closed 安全，但功能永久失效——两个方向都要用例 |
| M2 | `echo://local` 被准入判为远程拒绝 | echo 装配 `ValueError` | `scheme=echo` → `OFFLINE_BACKEND` | 离线后端不属于网络准入范围 |
| M3 | echo 回执缺 `ok` 键 | 探针 `KeyError` | 补 `ok=True` | 回执结构要跨 mode 一致 |
| M4 | T-U1-A 断言 180 条 | 实得 6 | 改断言 6 + 纯函数补测 | 投喂的实验设计也要对代码核一遍 |
| M5 | `platform.os.cpu_count()` | 代码复核 | `import os` | 不要依赖模块内部导入 |

## 6. 技能表（24）

| # | 技能 | 判定什么 | 输出 |
|---|---|---|---|
| 1 | `uplift.unit_registry` | 六单元与执行顺序是否与投喂一致 | `order_matches_spec` |
| 2 | `uplift.order_key_check` | 排序键是否在内容上单射、反转输入后是否同序 | `key_injective_on_content` |
| 3 | `uplift.purity_contract` | 哪些函数承诺不改入参、如何验证 | 契约表 |
| 4 | `uplift.regression_ledger` | 修复前后口径与徽章是否对齐 | `badge_consistent` |
| 5 | `uplift.ci_spec` | CI 矩阵/步骤/失败语义 | `pack_can_prove=False` |
| 6 | `uplift.template_check` | 三模板必填小节是否齐 | `missing[]` |
| 7 | `uplift.badge_consistency` | 徽章数值 = 实测值 + 有 CI 注记 | `PASS/FAIL` |
| 8 | `uplift.support_matrix` | 只允许 `measured/untested` | `invalid_status[]` |
| 9 | `uplift.measure_a1_verdict` | A1 判定是否带范围声明与变异证明 | `measured_with_scope` |
| 10 | `uplift.measure_a2_disclosure` | 中位/机器规格是否齐、阈值是否显式 `none` | `fabricated_target` |
| 11 | `uplift.evidence_chain` | 脚本/种子/日期/A1/A2/范围 六件 | `missing[]` |
| 12 | `uplift.ngram_dice` | 与 `skill.py` 同算法的字符 n-gram Dice | `dice` |
| 13 | `uplift.hybrid_score_parts` | 0.5/0.5/0.05 权重与重算 | `score` |
| 14 | `uplift.matching_acceptance` | 两条必测用例是否按预期命中 | `cases[]` |
| 15 | `uplift.bridge_boundary` | 桥是否在包外、核心是否无网络 | `PASS/FAIL` |
| 16 | `uplift.backend_registry` | 三后端默认地址与 key 来源 | 表 |
| 17 | `uplift.remote_gate` | 本机放行 / 远程三重确认 | 理由码 |
| 18 | `uplift.audit_policy` | 审计 7 字段，禁明文与密钥 | `leaked_fields[]` |
| 19 | `uplift.live_receipt_schema` | live/echo/simulated 三态词表 | 表 |
| 20 | `uplift.adjudication` | O-1～O-10 裁决 | `all_decided` |
| 21 | `uplift.p1_gate` | 预算/hit_rate/重合度/零 UNKNOWN 四判据 | `PASS/REJECT` |
| 22 | `uplift.stance_matrix` | 五立场是否各≥2 处可判定落实 | `each_has_two_checks` |
| 23 | `uplift.audit_receipt` | 六单元回执 + 16 位指纹 + 密令 | `all_six` |
| 24 | `uplift.dimension_invariant` | 1331 行 / 108641 节点不新增 | `PASS` |

工作流 7 条：`W1_determinism` / `W2_ecosystem` / `W3_measurement` / `W4_matching` / `W5_host_bridge` / `W6_adjudication` / `W7_acceptance`。

## 7. 立场矩阵

| 立场 | 落点 1 | 落点 2 |
|---|---|---|
| 零依赖 | CI 无 `pip install` | 红线扫描 import 白名单 |
| 确定性 | T-U1-A / 全序纯函数断言 | A-U5-3 千次逐位一致 |
| 取舍留痕 | X1–X10 + M1–M5 | O-1～O-10 裁决表 |
| 代价显式 | A1/A2 带范围 | CI / live 标 `untested` |
| 宿主边界 | `bridges/` 在包外 | 密钥只从 env 读；echo 与 live 分离 |

## 8. 明确不做（NG1–NG6）

改 `Cluster` 线程语义 / 核心包引入网络 / 引入第三方依赖 / 发布自动化 / P1 真执行淘汰 / 用 echo 冒充 live。

## 9. 拒绝操作（8 条）

把未实跑的 CI 说成 passing、把脚本级实测说成生产闭环、用 echo 或 simulated 冒充 `mode=live`、把审计塞入明文 prompt 或密钥、在 `holoaeon/` 内 import 网络模块、为通过测试改断言、把 X1–X10 的择定改回投喂字面而不说明、新增 `after_summary` 字段、跳过 A1 变异证明就宣布判定有效。

## 10. 验收状态

| 组 | 项数 | 本地实测 | 无法本地代证 |
|---|---|---|---|
| A-U1-1..4 | 4 | 全部 PASS | — |
| A-U6-1..4 | 4 | 3 项 PASS | A-U6-1（CI 三版本全绿）= `untested` |
| A-U3-1..4 | 4 | 全部 PASS（限定范围） | — |
| A-U5-1..4 | 4 | 全部 PASS | — |
| A-U2-1..6 | 6 | 5 项 PASS | A-U2-3（真 `mode=live`）= `untested` |

22 项验收里 **20 项本地实测、2 项标注 `untested`**。不写"全部通过"。

## 11. 快速取用

```
python -m unittest discover -s tests            # 34 tests OK
python -c "from holoaeon.selftest import run_all; print(run_all()['passed'])"
python scripts/redline_scan.py                  # 34 文件零违规
python scripts/measure_a1_a2.py --runs 30       # A1 PASS + 变异 FAIL + A2 披露
python -c "from holoaeon.packs.uplift_pack import pack_summary as p; print(p()['skills'])"
```

## 12. 已知限制

1. A-U6-1 只能在 GitHub 侧产生；本仓库只交 workflow 与 `untested` 矩阵。
2. A-U2-3 需本机装有 Ollama；本机未装，`mode=live` 未实测（`--check` 分支与 echo 装配已实测）。
3. A1/A2 为「宿主编排层限定范围」实测，非生产链路闭环。
4. `docs/support-matrix.md` 的非 3.13 行列全部 `untested`。

---


潮起开门，潮落闭嘴
