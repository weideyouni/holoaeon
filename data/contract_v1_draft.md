# B1a · 内外融合契约字段草案 v0.1（draft，未冻结）

- 批次：B1a（十二批之 2，0.5 人天）
- 状态：**草案**（本批只出字段定义与口径，不改任何执行代码；代码化与单测留给 B1b）
- 证据等级：`evidence_class=simulated`（仿真 ≠ 证明，碳基终裁）
- 密令：潮起开门，潮落闭嘴
- 不变项：`agents=25` / `skills=47` / `packs=9`、`spec.VERSION=0.9.1`、`diff0=2fc892cf9af6e755`、`tamper=f42c8229ee5acd73`

## 〇 这一批在做什么

HoloAeon 与 ivsa 两仓互不认识对方代码，唯一的耦合点是**一条 JSON 回执**。B1a 只回答一个问题：这条回执里到底有哪几个字段、每个字段什么类型、什么值合法、怎么举例。写不清楚，B1b 就没法做"同参互认实验"，后面 B2 的映射表也无处落。

**本批边界**：不出代码、不入内核、不动维度锁、不碰 ivsa。产出只有本文件 + 一个可跑的字段校验器（证明字段清单没漏项）。

## 一 三条口径决定（默认口径，已采纳）

| # | 问题 | 决定 | 为什么 |
|---|---|---|---|
| D1 | `contract_id` 怎么生成 | **内容指纹前 12 位**：对规范化后的契约主体做 sha256，取前 12 位十六进制 | 同参同指纹、异参异指纹，可离线复算；不依赖批次号，跨批可去重 |
| D2 | `payload` 是否自由 | **白名单六键**：`domain / inputs / outputs / evidence / redlines / notes`，出现白名单外的键即非法 | 自由 dict 会让语义漂移无法拦截（v0.9.4 的语义底座只有 19 条，兜不住任意键） |
| D3 | 医学红线字段是否必填 | **仅涉医域必填**：`payload.domain=="medical"` 时 `redlines` 三布尔必须齐且为 `true`；通用域不要求 | 通用域的闸固定 10 token，按域注入可避免医学词表污染通用闸（V4-4 坑） |

## 二 顶层字段（6 必填 + 4 可选）

| 字段 | 必填性 | 类型 | 允许值 / 约束 | 示例 |
|---|---|---|---|---|
| `contract_id` | 必填 | string | 12 位小写十六进制；对 `source/target/skill/mechanism/lane/payload` 规范化后取 sha256 前 12 位 | `"eb6cb517cd4c"` |
| `source` | 必填 | string | 发起方标识，小写，`local` 或镜像站名；不得为空 | `"local"` |
| `target` | 必填 | string | 接收方标识，小写；`gitee` / `github` / `vector_sea` / `huggingface` / `ivsa` 之一 | `"ivsa"` |
| `skill` | 必填 | string | 技能名，须为已登记技能（47 内核技能或扩展包技能）；不得含路径 | `"fusion_contract"` |
| `mechanism` | 必填 | string | 六机制之一：`holographic_heartbeat` / `cytoskeleton` / `skin_v6` / `semantic_bus` / `hebbian_field` / `meridian` | `"semantic_bus"` |
| `lane` | 必填 | string | `read`（只读交换）或 `write`（写回本地）；写回需人工签字 | `"read"` |
| `payload` | 可选 | object | 见下方白名单六键；缺省视为 `{}` | `{"domain":"medical"}` |
| `nonce` | 可选 | string | 8–32 位，重放检测用；**不参与指纹**，故不改变 `contract_id` | `"n-20261102-01"` |
| `budget` | 可选 | integer | 0–100，调用预算；越界即非法 | `3` |
| `note` | 可选 | string | ≤200 字，人读备注；不得写剂量、诊断结论 | `"B1b 同参互认实验样本"` |

### payload 白名单（六键）

| 键 | 必填性 | 类型 | 约束 | 示例 |
|---|---|---|---|---|
| `domain` | 可选 | string | `general`（默认）或 `medical` | `"medical"` |
| `inputs` | 可选 | object | ≤12 键，值为 string / number / bool | `{"case_id":"R-001"}` |
| `outputs` | 可选 | object | ≤12 键，同上 | `{"verdict":"mapped"}` |
| `evidence` | 可选 | object | 只放可复算字段（哈希、路径、行号）；不得放结论 | `{"sha256":"98940b774566543b"}` |
| `redlines` | 涉医域必填 | object | 仅 `domain=="medical"` 时要求；三布尔必须齐且为 `true` | 见下 |
| `notes` | 可选 | string | ≤200 字 | `"契约草案样本"` |

`redlines` 三布尔（缺一即非法）：

```json
{"zero_dose": true, "c0_not_efficacy": true, "emergency_120": true}
```

## 三 两条示例

通用域（最小合法契约，`contract_id` 由本节算法实算）：

```json
{
  "contract_id": "eb6cb517cd4c",
  "source": "local",
  "target": "gitee",
  "skill": "fusion_contract",
  "mechanism": "semantic_bus",
  "lane": "read",
  "payload": {"domain": "general", "notes": "B1b 最小样本"},
  "budget": 1,
  "note": "通用域"
}
```

涉医域（必须带 redlines，`contract_id` 同一算法实算）：

```json
{
  "contract_id": "5960b848b691",
  "source": "local",
  "target": "ivsa",
  "skill": "fusion_plan",
  "mechanism": "meridian",
  "lane": "read",
  "payload": {
    "domain": "medical",
    "inputs": {"case_id": "R-001"},
    "evidence": {"sha256": "98940b774566543b"},
    "redlines": {"zero_dose": true, "c0_not_efficacy": true, "emergency_120": true},
    "notes": "只交换契约，不搬代码"
  },
  "nonce": "n-20261102-01",
  "budget": 2,
  "note": "涉医域样本，simulated"
}
```

## 四 指纹算法（可复算，B1b 照此实现）

```
body   = {source, target, skill, mechanism, lane, payload}
canon  = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
digest = sha256(canon.encode("utf-8")).hexdigest()[:12]
```

判定规则：

- **同参同指纹**：`body` 逐字节相同 → `contract_id` 必相同（跨进程、跨机器、跨批都成立）。
- **异参异指纹**：`body` 任一字段变化（含 payload 内部键值）→ 12 位碰撞概率可忽略；若撞，按"加长到 16 位"处置，不进 B1b。
- **`nonce` 不进指纹**：同一参数带不同 `nonce` 视为**重放**，指纹相同、`nonce` 不同，正好用来做重放检测。
- **不做算术推导**：指纹只由内容决定，不掺批次号、时间戳、自增序号。

## 五 校验规则（B1b 单测必须覆盖）

| 规则 | 判定 |
|---|---|
| V1 必填缺失 | 6 必填任一缺失 → `invalid` |
| V2 枚举越界 | `mechanism` 不在六值 / `lane` 不在 `read|write` → `invalid` |
| V3 白名单越界 | `payload` 出现六键外的键 → `invalid` |
| V4 涉医域缺红线 | `payload.domain=="medical"` 且 `redlines` 缺项或为 `false` → `invalid` |
| V5 指纹不符 | 重算 `contract_id` 与声明值不等 → `invalid` |
| V6 预算越界 | `budget` 不在 0–100 → `invalid` |
| V7 剂量/诊断泄漏 | `note` / `notes` 出现剂量数字或诊断结论文本 → `invalid`（交红线扫描复查） |
| V8 未知顶层键 | 出现 10 字段之外的键 → `invalid`（留给 V2 再议，出方案前不开口） |

## 六 本批完美判据（可跑）

1. 本文件列出 **6 必填 + 4 可选 = 10 行**，每行都有类型、约束、示例（非空）。
2. `payload` 白名单 **6 键**，每键有类型与约束。
3. 三条口径决定 D1–D3 记录在案（指纹 / 白名单 / 涉医域必填）。
4. 两条示例均为合法 JSON，可被 `json.loads` 解析。
5. `python scripts/check_contract_draft.py` 退出码 0，输出 `verdict=PASS`。
6. 判据表述不含形容词（更优/更自然/更智能/体验/流畅/顺手/高级感）。

## 七 留给 B1b 的 TODO（不在本批做）

- 把本文档字段表落成 `holoaeon/fusion_upgrade/contract.py` 的常量与校验函数（现实现已有 6 必填 4 可选，需补白名单与涉医域分支）。
- 契约单测 ≥6 项：V1/V2/V3/V4/V5/V6 各一条。
- 同参互认实验：同一 `body` 在两个独立进程各算一次指纹，断言相等；改一个 payload 键，断言不等。
- 产出 `contract_v1.json`（冻结版）+ 回执。

## 八 边界（本批不做）

- 不改 `contract.py` 任何代码，不改内核、不动 47 技能、不动 ivsa。
- 不引入第十一字段、不加 `domain` 到顶层（域信息走 `payload.domain`，避免破 6+4 结构）。
- 不把 `note` 当自由文本乱写（红线优先于措辞方便）。
- 不把本草案当冻结契约引用；B1b 冻结后才可作为交换依据。

潮起开门，潮落闭嘴。
