# HoloAeon · VERAX 可信层（v0.9.1 + audit）

> 零依赖 · 默认离线 · 确定性 · 可审计 · 八层守卫 · 诚实纪律
> 本次升级不新增能力，只是让既有能力**可被复算、可被出示**。

```
VERAX_EXIT=0   |   24/24 自检   |   5/5 基准 stable   |   红线 0 违规   |   dependencies = []
```

---

## 0. 三十秒复现（离线可跑）

```powershell
cd holoaeon
python scripts\verax_verify.py            # 红线 → 自检 → 复现 → 诚实 → 热插拔
# ==> conclusion=green  VERAX_EXIT=0

python -m holoaeon.selftest               # 直接入口，真跑真打印（G1-G24）
python -m unittest discover -s tests      # 34 项既有单测
python -m unittest discover -s tests\verax  # 16 项 VERAX 单测
```

最硬的一条证据：同一个任务跑两次，剔除 `ts` 后哈希逐位相同。

```
word_count  →  2b82a6ef7188ce91   ×2
```

---

## 1. 为什么有这一层

HoloAeon 已有的强项是"确定性"，但它此前是**内部工程习惯**，不是**对外证据**：整包哈希含时间戳导致"假不确定"、自检模块静默退出 0、回执里 `simulated` 与"真实生效"混写。三处都会让别人在 30 秒内得出错误结论。

VERAX 把这三处修成一件可出示的东西：**可复现核心 / 物理量** 分离 → 规范化 → ReproHash → 黄金基准 → 单一退出码 → 自证报告。

---

## 2. 维度不变（硬约束，已实测）

| 维度 | 升级前 | 升级后 | 说明 |
|---|---|---|---|
| 智能体 | 25 | **25** | 未新增 agent |
| 技能（九大领域包） | 47 | **47** | 未新增技能 |
| 领域包 + 扩展包 | 9 + 7 | **9 + 7** | 未加第 17 个包 |
| 全装技能 / 工作流 | 191 / 55 | **191 / 55** | 扩展包不进 `PACK_ORDER` |
| 单元测试（`tests/`） | 34 | **34** | VERAX 测试另立 `tests/verax/`（16 项） |
| 自检 | G1–G24 | **G1–G24** | 24/24 全 PASS |
| 红线 | 0 违规 | **0 违规** | 扫描口径 34 → 40 文件（新增 audit 6 个模块） |
| 依赖 | `dependencies=[]` | **`dependencies=[]`** | 纯标准库 |
| 离线 / 确定性 | 是 | **是** | 无网络、无端口、无常驻 |

规模实测：`holoaeon/` **40 个 py / 11,408 行**（核心 16 / 3,851，`packs/` 18 / 6,872，`audit/` 6 / 685）。

---

## 3. 五件套

| 组件 | 文件 | 作用 |
|---|---|---|
| 字段分类 + 规范化 | `holoaeon/audit/fields.py` | ReproCore / Physical / Opaque 三分；未知字段丢弃并告警 |
| 回执与判定结构 | `holoaeon/audit/receipt.py` | `Receipt` / `ReproVerdict` / `EvidenceClass` |
| 复现验证器 | `holoaeon/audit/verify.py` | n 个全新内核喂同一任务，比对 ReproHash 与 golden |
| 诚实契约 | `holoaeon/audit/honesty.py` | H1 / H2 扫描与合规汇总 |
| 自证报告 | `holoaeon/audit/attest.py` | `attestation.md` + `attestation.jsonl`，`verdict_hash` 可复算 |
| 门禁入口 | `scripts/verax_verify.py` | 单命令合成 0/1/2 退出码 |

---

## 4. 黄金基准（改动须 PR 标题带 `[golden]`）

| task_id | 期望 ReproHash | 期望结果 |
|---|---|---|
| `word_count` | `2b82a6ef7188ce91` | 中文字 20 / 英文词 1 / 总字符 31 / 句 1 |
| `data_describe` | `3352db0f803eb727` | count 3 · mean 2.0 · std 0.816 |
| `quant_sharpe` | `2c9e5d7d01526ce8` | sharpe 5.7752 |
| `guard_os_system` | `a7deb622e17a2b55` | `blocked`（L3） |
| `guard_eval` | `98b9b7b340f7f980` | `blocked`（L3） |

---

## 5. 门禁三色

| 退出码 | 含义 | 实测 |
|---|---|---|
| `0` | 绿：红线干净 + 自检 24/24 + 5 基准命中 + 无诚实告警 | `verdict_hash=ec516f4ed413b5af` |
| `2` | 黄：仅诚实告警（注入一条无来源 `measured`） | `verdict_hash=259eed7b72bdbb49` |
| `1` | 红：基准不一致（篡改 `word_count` 黄金值） | `verdict_hash=5bfa825fb948819e` |

三色各有独立哈希，说明结论字段真的进了 ReproHash（首轮遗漏登记时三者完全相同，已修）。

---

## 6. 证据分级

| 分级 | 语义 | 强制字段 |
|---|---|---|
| `simulated` | 确定性引擎产出（默认） | — |
| `measured` | 本机真跑并留痕 | `measure_source` + `measure_ts` |
| `third_party` | 外部来源 | 同上 + 可核验引用 |

`measured` 缺来源 → **H1（红）**；回执缺 `evidence_class` → **H2（黄）**。

---

## 7. 与既有架构的接入（只读）

观测 `kernel.submit()` 回执、`guard.Verdict.to_dict()`、`selftest.run_all()`、`redline.scan_directory()`、`packs.install()` 前后技能差、`.git/HEAD` 文件；不写内核、不写守卫、不调 git 进程、不起子进程。

---

## 8. 已知限制

1. 数值不转定点字符串（保 `2b82a6ef…` 历史口径）；跨语言复算需对齐 `json.dumps` 数字序列化。
2. 未知字段是"丢弃 + 告警"，不阻断运行。
3. `measured` 只证明来源存在，不核验外部真实性。
4. `verdict_hash` 与 commit 绑定，提交后旧哈希失效属预期。
5. 热插拔检查为单包抽样（`optimization` 40→47），未逐包回归。

---

## 9. 下一步

VERAX 是"证据出口"，NEPHRON P0 认知账本是"证据来源"。账本落地后可让 `repro_summary` 挂到具体 tick，实现任意 tick 回放。不做第 17 个领域包，不为 star 抄编排框架。

---

## 10. 红线（不变）

零网络、零密钥、零遥测；不开端口、不常驻、无 cron；不 pip/npm；不读 `.env`；不替用户决策。
所有回执默认 `simulated`：**仿真 ≠ 证明**，碳基终裁。

许可证 Apache-2.0 · Python 3.8+ · 仅标准库。
