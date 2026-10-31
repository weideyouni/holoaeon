# 面向智能体 · 一键复制投喂包（VERAX 冷热插拔赋能版）

> 唯一 ID：SG-HOLOAEON-VERAX-20261031-V1.0
> 矩阵规格：冷热插拔赋能升级思维模式（SG-ENGINE-COLD-HOT-PLUG-V1.0）实例化
> 封存密令：潮起开门（激活）/ 潮落闭嘴（休眠）
> 产出维度不变：25 智能体 / 47 技能 / 9 领域包 + 7 扩展包 / 34 单测 / 24 自检 / 红线零违规 / 零依赖 / 离线 / 确定性
> 用法：整段复制给任意实现智能体，它可在无额外上下文的情况下复刻或验收本升级。

---

## 一、你的角色与边界

你是 HoloAeon（通用多智能体认知框架，零依赖·离线·确定性）的实现智能体。任务是在不改动既有能力的前提下，为其加一层可信横切子系统（代号 VERAX）：把"确定性 / 安全边界 / 诚实纪律"从内部工程习惯，变成可复算、可出示的证据产物。

硬边界：

- 不新增领域包、不新增 agent、不新增业务技能（维度不变是硬约束，不是建议）。
- 不引入任何第三方依赖；不联网、不开端口、不常驻、不读 .env；核心包 dependencies = [] 不得破坏。
- 不改 C1–C12 对外行为；VERAX 只读观测 + 规范化重算。
- 不破坏 G1–G24 全绿与 tests/ 34 项全绿。
- 不把 simulated 写成"实测"。

---

## 二、项目基线（自包含事实，可直接施工）

- 运行时：HOLOAEON-RUNTIME-0.9.1；许可证 Apache-2.0；Python 3.8+；零第三方依赖。
- 12 个正交原语：envelope / bus / agent / skill / memory / scheduler / guard / kernel / graph / cluster / hypervector / model_adapter。
- 16 个包：9 领域（writing / literature / research / data / growth / business / quant / optimization / gaoyi）+ 7 横切（sovereignty / subdistill / omnilife / omnicore / metab / nephron / uplift）。
- 九域装齐 = 25 agent / 47 skills / 9 workflows；全装 = 191 skills / 55 workflows / 25 agent。
- 既有入口：scripts/launch_local.py {status|demo|run|hotplug|selftest}、python -m unittest discover -s tests、scripts/redline_scan.py。
- 三处历史坑（必须正面解决）：
  1. 整包哈希含 ts → 朴素比对得"假不确定"；
  2. python -m holoaeon.selftest 无 __main__，静默退出 0；
  3. 回执中 simulated 与"真实生效"未强制区分。

---

## 三、冷热插拔五步协议（每一步都可执行、可回滚）

| 步 | 动作 | 本项目的落点 | 完成判据 |
|---|---|---|---|
| 1 解锁 | 只读盘点现状，不写任何文件 | launch_local.py status / selftest / redline_scan.py / unittest discover -s tests | 拿到 24/24、34 OK、0 违规三项基线 |
| 2 旁挂 | 新增 holoaeon/audit/ 与 scripts/verax_verify.py，主核一行不改 | 目录新增，不改既有 16 个核心模块的对外行为 | 旁挂后既有三项基线不变 |
| 3 联调压测 | 规范化口径联调 + 基准冻结 + 三色用例 | scripts/_freeze_golden.py 冻结 5 个基准；--case green/yellow/red | word_count 稳定 2b82a6ef7188ce91；退出码 0/2/1 各自可复现 |
| 4 巡检上线 | 门禁合成 + 自证报告 + 接入 CI | python scripts/verax_verify.py 出 reports/attestation.md + attestation.jsonl | VERAX_EXIT=0；jsonl 连跑两次哈希一致 |
| 5 一键回滚 | 删旁挂即复原 | 删 holoaeon/audit/、scripts/verax_verify.py、tests/verax/、reports/ | 既有 34 单测 / 24 自检 / 0 违规不受影响 |

---

## 四、要实现的规格（逐条可判定）

### 4.1 字段分类表（集中声明，新增字段必须登记）

| 类别 | 键 | 处理 |
|---|---|---|
| Physical | ts, timestamp, elapsed, duration, started_at, finished_at, thread_order, addr, pid, uptime_s, measure_ts, id_instance | 剔除，不进 ReproHash |
| ReproCore | status, all_ok, matched, targets, output.*, route.*, guard.*, agent_id, evidence_class 等裁决类字段 | 保留，参与哈希 |
| Opaque | output, payload, evidence, reprocore, physical | 原样序列化 |
| Unknown | 未登记键 | 丢弃并以 unknown_field 路径告警，不静默 |

自证报告自身的 schema（conclusion / checks / repro / honesty / redline / gid / name / verdict_hash）也必须登记，否则会被当物理量剔除、导致哈希失去区分度。

### 4.2 算法

canonicalize：递归剔 Physical；list[dict] 先按规范文本稳定排序再递归（解线程完成序）；处理 NaN / ±Inf / -0.0；None → null；键升序无空白 JSON。

reprohash = sha256(canonical_json)[:16]（与既有 2b82a6ef… 同口径，不要改成定点字符串，否则基准漂移）。

### 4.3 数据结构

- Receipt{receipt_id, source_path, evidence_class ∈ {simulated, measured, third_party}, measure_source, measure_ts, reprocore, physical}
- ReproVerdict{task_id, runs, reprohash_list, repro_hash_stable, golden_match, diff_physical, diff_reprocore}
- CheckResult{gid, name, status ∈ {pass, fail, skip}, evidence, evidence_class}
- Attestation{runtime_id, commit, ts_build, checks, repro_summary, honesty_summary, redline, verdict_hash, conclusion ∈ {green, yellow, red}, unknown_fields}

verdict_hash 只取结论字段（不含 ts_build），同代码同结论必同哈希。

### 4.4 黄金集（冻结在 audit/golden/*.json，改动须 PR 标题带 [golden]）

| task_id | 期望 ReproHash | 期望结果 |
|---|---|---|
| word_count | 2b82a6ef7188ce91 | 中文字 20 / 英文词 1 / 总字符 31 / 句 1 |
| data_describe | 3352db0f803eb727 | count 3 · mean 2.0 · std 0.816 |
| quant_sharpe | 2c9e5d7d01526ce8 | sharpe 5.7752 |
| guard_os_system | a7deb622e17a2b55 | blocked · L3 |
| guard_eval | 98b9b7b340f7f980 | blocked · L3 |
| hotplug_opt（独立检查） | — | 技能 40 → 47，未重启 |

### 4.5 诚实规则

- 所有 VERAX 产出默认 simulated。
- measured 缺 measure_source / measure_ts → 记 H1（红）；一条不合规回执只记一条 H1（缺项合并进 detail）。
- 回执缺 evidence_class → H2（黄）。
- 修 selftest 静默坑：补 main() + __main__，失败返回非零。

### 4.6 门禁（scripts/verax_verify.py）

顺序：红线（含 H1/H2）→ 自检 → 复现基准 → 诚实契约 → 热插拔 → 汇总 Attestation。

| 退出码 | 含义 |
|---|---|
| 0 | 绿 |
| 1 | 红（检查失败 / 基准不一致 / 红线违规） |
| 2 | 黄（仅诚实告警） |

报告双导出：reports/attestation.md（人读 ASCII 回执）+ reports/attestation.jsonl（逐行一条 CheckResult，键序稳定）。

---

## 五、验收（A1–A10，本轮全部实测通过）

| 项 | 判据 | 实测 |
|---|---|---|
| A1 | word_count 两次 ReproHash 稳定 2b82a6ef7188ce91，golden_match=True | 通过 |
| A2 | 逻辑等价、物理量不同的两份回执规范化后逐字节一致（含 list[dict] 乱序） | 通过（test_canonicalize） |
| A3 | 未登记字段被丢弃并计入 unknown_field，不静默 | 通过（首轮三色哈希相同即此缺陷，已修） |
| A4 | 无来源 measured → 至少黄灯，H1/H2 计数 | 通过（--case yellow → 退出码 2） |
| A5 | 开启 VERAX 不改变 G1–G24 与 34 单测 | 通过（24/24、34 OK） |
| A6 | attestation.jsonl 连跑两次哈希一致 | 通过（SHA-256 相同） |
| A7 | 退出码可被 CI 消费（绿/黄/红三例） | 通过（0 / 2 / 1，三色 verdict_hash 各不相同） |
| A8 | 红线新增 H1/H2 且 import 层零网络、dependencies=[] 不破 | 通过（40 文件 0 违规） |
| A9 | 修复 selftest 空打印 | 通过（python -m holoaeon.selftest 打印 24/24） |
| A10 | 文档完备（字段表 / 分级规则 / 退出码 / 报告样例） | docs/VERAX.md |

真实结果：

```
自检         ==> 24/24
tests/       Ran 34 tests / OK
tests/verax/ Ran 16 tests / OK
红线         扫描文件数 40 / 结果 干净（零违规）
门禁 green   conclusion=green  verdict_hash=ec516f4ed413b5af  VERAX_EXIT=0
门禁 yellow  conclusion=yellow verdict_hash=259eed7b72bdbb49  VERAX_EXIT=2
门禁 red     conclusion=red    verdict_hash=5bfa825fb948819e  VERAX_EXIT=1
热插拔       40 → 47（新增 7，全程未重启）
本地融合     总线 25 地址 / 低成本→local / 长上下文→cloud / all_ok=True
```

---

## 六、禁止项（违反即失败）

1. 不加第 17 个领域包，不新增 agent/业务技能。
2. 不为追 star 抄编排框架；不引入非确定性来源。
3. 不把 simulated 写成实测。
4. 不破坏 dependencies=[]、不引网络、不破 G1–G24 与 34 单测。
5. 不在核心包散布记录代码（观测一律走只读 hook / CLI）。
6. 不把 golden 随手改；改动必须走评审。

---

## 七、输出格式与交付物

Markdown；结构化内容用表格；生物隐喻仅限既有词。每条规范性陈述应可判定，并补一句"它保护了哪条立身原则"。

交付 7 项：

1. 设计说明 + 与 C1–C12 的接入点清单（只读 hook/CLI）
2. 字段分类表 + 证据分级规则表
3. 复现验证器 + 黄金集 + golden 冻结文件
4. 自证报告 md/jsonl 样例（必须含 2b82a6ef…）
5. verax_verify.py + 三色用例
6. 测试清单与真实结果（禁止把 simulated 写成实测）
7. 已知限制与下一步（承接 NEPHRON P0 认知账本）

---

## 八、隐私与安全

默认不存用户原文，只存任务摘要与哈希；trace 只记调用指纹与字节数，不记请求体；导出目录最小化（reports/ 与 reports/_cases/ 分开，_cases 不进正式扫描）；一键擦除 = 删 reports/。

---

## 九、一句话交付口径

VERAX 把 HoloAeon 最强的东西——可验证的确定性 + 诚实契约——从三处隐藏坑，修成一个别人抄不走、30 秒能复现、能挂 CI 徽章的证据资产。先做 VERAX，再推 NEPHRON P0 补治理的数据底座。

潮起开门，潮落闭嘴。
