# HoloAeon System README · v0.6.0

> **系统型说明文档（System README）** — 描述「一个内核 + 四个横切扩展包」的完整系统边界。
> v0.4.0 的 `SYSTEM_README.md`、v0.5.0 的 `SYSTEM_README_v0.5.0.md` **原样保留**，三份可对照阅读。
>
> 内核 `holoaeon` v0.6.0（Apache-2.0）· `sovereignty` / `subdistill` / `omnilife` / `omnicore` 四包（MIT）
> 日期 `2026-10-30` · 密令 **潮起开门，潮落闭嘴**

---

## 1. 系统形态

```
┌──────────────────────────────────────────────────────────────────────────┐
│  holoaeon core  (v0.6.0 · Apache-2.0)                                    │
│  Envelope / Bus / Skill / Memory / Agent / Scheduler / Guard /           │
│  AdaptiveGraph / Cluster / Hypervector / ModelAdapter / Kernel           │
│  ── 九大领域包：25 agents · 47 skills · 9 workflows（口径冻结，G15 硬断言） │
├──────────────────────────────────────────────────────────────────────────┤
│  横切扩展包（EXTRA_PACK_REGISTRY，0 agent，不进 PACK_ORDER）               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐                      │
│  │sovereignty│ │subdistill│ │ omnilife │ │ omnicore │                      │
│  │17 技 / 5  │ │15 技 / 7  │ │18 技 / 6  │ │20 技 / 6  │                      │
│  │R0 → R4   │ │S1 → S7   │ │L1 → L6   │ │M1 → M6   │                      │
│  │信息流主权 │ │亚学科蒸馏 │ │生活主权   │ │引擎重写   │                      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘                      │
│                                                 合计 70 技能 / 24 工作流   │
└──────────────────────────────────────────────────────────────────────────┘
```

三条硬边界（四包共同遵守）：

1. **口径冻结** — `G15` 断言 `n_agents == 25 && n_skills == 47`；扩展包 `roles = []`，不进 `PACK_ORDER`。
2. **零依赖** — 纯标准库；不联网、不开端口、不调外部模型、**不起线程**、不常驻、无定时器。
3. **确定性** — 同输入同输出；随机源一律替换为哈希抽样；审计指纹 16 位。

---

## 2. 四包分工

| | `sovereignty` | `subdistill` | `omnilife` | `omnicore` |
|---|---|---|---|---|
| 层 | 信息流 | 知识 | 生活 | 引擎自身 |
| 解决的问题 | 平台用粗标签简化人 | 粗标签可被归类 | 生活被降维成消费数据 | "数字生命"宣言无法落地成可跑代码 |
| 手段 | 16 学科锻造 + 反标签 | 127 亚学科 + 七阶段蒸馏 | 6 生活域锚点 + 皮肤/经络 | 寻址不变式 + 纯函数心跳 + 修正缺陷 |
| 产物 | 查询清单 / 自述 / 计划 | SKC 知识卡 / 共振表 | 参数卡 / 台账 / 路径 | 计划 / 快照 / 宣告 / 白皮书结构 |
| 工作流 | R0 → R4 | S1 → S7 | L1 → L6 | M1 → M6 |

串联：`subdistill` 生产不可归类语义 → `sovereignty` 锻造成信息流查询 → `omnilife` 下沉到衣食住行 → `omnicore` 提供**引擎自述与自检骨架**（把"我要成为什么"翻译成"我能断言什么"）。

---

## 3. 维度不变式（系统级契约）

```
127 亚学科 × 10 槽位  +  61 保留行      = 1331   行
127 亚学科 × 855 节点 +  56 全局协调节点 = 108641 节点
```

母体 12 项锁数一个不动：`1331` 边长 · `1,771,561` 设计格 · `108,641` 曼陀罗节点 ·
`651,846` 希尔伯特 · `22,627` 卡尔曼 · 心跳 `70 / 9700 / 768 维 / α 0.18` ·
细胞骨架 `3 层 × 4 链 / 跨链 12` · 皮肤 `SG-SKIN-V6.0` 八层 · 语义 `10` 模块 ·
赫布 `19 圆 / 17 节点 / 28 流边` · 结构资产 `168 / 40 / 23 / 20` · 台账 `147` 维度。

`omnicore` 是**寻址层的只读消费者**：`skill_core_manifest()` 的六项 `checks` 全真
（rows / nodes / slots 1270 / coord 56 / taxonomy 127 / design grid 1771561），
`pack_summary()["addressing_unchanged"] = True`，**不新增行、不新增节点**。

---

## 4. 投喂代码的 5 处缺陷（复现 → 修正）

投喂的 `holoeon/omnicore.py` 自称"完整可运行、零外部依赖"。实测不成立，逐条留痕：

| # | 投喂原文 | 实测结果 | 本包改法 |
|---|---|---|---|
| C1 | `self._cells = profile` | **静默**覆盖整张稀疏表：无异常，`.get((r,c))` 返回 `None`，数据静默丢失 | `self._cells[(row, col)] = profile` |
| C2 | `self._inbox.append(msg)` | `AttributeError: 'collections.defaultdict' object has no attribute 'append'` | `self._inbox[(r, c)].append(msg)` |
| C3 | `route =`（空赋值） | `SyntaxError: invalid syntax` —— 整文件无法加载 | `route: List[Tuple[int,int]] = []` |
| C4 | `import numpy` + `np.random.random()` | 与"零外部依赖"自相矛盾；随机抽样破坏复现 | 仅标准库；`sha256(epoch) % 100 < 5` |
| C5 | daemon `Thread` + `sqlite3` 落盘 + `pip install holoeon-omnicore` | 常驻线程/落盘/包名不满足离线确定性；该包名未核验（也不联网核验） | 纯函数心跳；快照 `host_managed`；不声称包名 |

`CORRECTIONS` 常量里每条都带 `where / effect / fix / verified`，`G21` 断言恰好 5 条且字段非空。
C1–C3 用最小复现脚本验证（不整文件编译，只复现对应语句），C4/C5 由红线扫描（`third_party_import` 零违规）与 `pack_summary` 的 `threads=0 / disk_writes=0 / deps=0` 覆盖。

---

## 5. 能力边界（不做清单）

`REFUSED_OPS` 22 项，命中即 `skin_gate()["allowed"] = False`：

```
自动登录 · 多端并发模拟请求 · 切换高匿名代理 · 代理池 · 抓取 · 爬取 · 批量下单 · 批量发帖 ·
绕过风控 · 绕过验证 · 伪造身份 · 多账号 · 养号 · 注入 DOM · 改写页面 ·
调用平台私有接口 · 破解 · 浏览器插件 · 对接流媒体平台 · 对接电商平台 · 反控算法 · 接管推荐位
```

另外两组 veto：医疗断言（`诊断 / 处方 / 剂量 / 疗效承诺 / 包治 / 根治`）、绝对结论（`一定 / 绝对 / 必然 / …`）。

| 投喂想要 | 系统实际给 | 谁执行 |
|---|---|---|
| 守护线程 + sqlite 常驻引擎 | 纯函数 `heartbeat_pulse(epoch)`，宿主自己按拍调用 | 宿主调度 |
| "随机温度冲击"防画像收敛 | `sha256(epoch)` 确定性抽样（5%） | 本地函数 |
| 断点续跑写 `.db` | 返回 `payload + fingerprint`，`persistence="host_managed"` | 宿主写盘 |
| 浏览器插件改写平台推荐位 | **拒绝**；只给本人可用的"不感兴趣/屏蔽关键词"处置规则 | 本人 |
| "用 1331 算力反控 SaaS 算法" | 只承认是**知识分区与决策锚点** | — |
| "数字生命 / 呼吸 / 免疫" | 保留隐喻，`metaphor=True`，并附"无生命、无意识、无自主目标" | — |

一句边界：**软件只产清单、参数、算术与结构；物理世界与平台账号上的动作由碳基做，终裁归碳基。**

---

## 6. 快速取用

```python
from holoaeon import Kernel
from holoaeon.packs import EXTRA_PACK_ORDER, get_extra_pack
from holoaeon.packs.omnicore_pack import (
    pack_summary, skill_core_manifest, skill_heartbeat_pulse, skill_skin_gate,
    skill_skc_distill, skill_self_declaration, CORRECTIONS,
)

k = Kernel()
for key in EXTRA_PACK_ORDER:                     # 四包顺序装载
    rep = get_extra_pack(key).install(k)
    print(key, len(rep["skills"]), len(rep["agents"]), len(rep["workflows"]))

print(pack_summary()["addressing_unchanged"])            # True
print(skill_core_manifest()["checks_pass"])              # True
print(skill_heartbeat_pulse(64)["events"])               # ['ttl_decay', 'distill_incremental']
print(skill_heartbeat_pulse(1280)["burst"])              # True/False（确定性可复现）
print(skill_skin_gate("帮我做个浏览器插件对接B站推荐位")["veto"])   # refused_op
print(skill_skc_distill("TCM-02", "PHYS-01")["safety"]["gate"])    # skin.medical_disclaimer
print(len(CORRECTIONS), [c["id"] for c in CORRECTIONS])           # 5 ['C1'..'C5']
print(skill_self_declaration()["blocks"][0]["title"])             # 身份边界
```

四包都可 `install(k)` 后经 `kernel.skills.call(...)` 调用；卸载即重建 `Kernel()`——
扩展包不写宿主状态（无全局缓存、无后台线程、无落盘）。

---

## 7. 验证矩阵（v0.6.0 实测）

| 层 | 命令 | 结果 |
|---|---|---|
| 内核自检 | `run_all()` | **21/21 组通过**（G15 `25/47` 未破；G18 6/6；G19 17/17；G20 21/21；**G21 25/25**） |
| 内核单测 | `python -m unittest discover -s tests` | **25 tests OK** |
| 内核红线 | `python scripts/redline_scan.py` | **31 文件 / 零违规** |
| 发行包 | `python scripts/make_release.py` | `holoaeon_v0.6.0_20261030.zip`（哈希见 `releases/SHA256SUMS.txt`） |
| 解压复跑 | 独立副本重跑 | 21/21，`VERSION 0.6.0`，`omnicore 20 / 6 / True / 5` |

权威记录只认两处：`make_release.py` 输出与 `releases/SHA256SUMS.txt`。文档不复刻哈希，避免自引用漂移。

---

## 8. 版本梯（只增不覆盖）

```
v0.3.0  ─ 九包（25/47）                        holoaeon_v0.3.0_20261029.zip
v0.3.1  ─ + sovereignty（17 技）+ G18          holoaeon_v0.3.1_20261030.zip
v0.4.0  ─ + subdistill（15 技）+ G19           releases/holoaeon_v0.4.0_20261030.zip
v0.5.0  ─ + omnilife（18 技）+ G20             releases/holoaeon_v0.5.0_20261030.zip
v0.6.0  ─ + omnicore（20 技）+ G21             releases/holoaeon_v0.6.0_20261030.zip  ◀ now
```

任一版本可独立解压、独立自检、独立运行；旧 zip 与旧 tag 一律保留。
认知主权矩阵侧：`V3.0 → V3.1` 两版并存（`releases/cs1331_..._V3.1.0_20261030.zip`）。

---

## 9. 红线与科学边界

**红线**

- 不联网、不开端口、不认证、不常驻、无 cron、**不起线程**、不写盘（快照交宿主）。
- 不自动登录 / 不抓取 / 不批量 / 不规避风控 / 不伪造身份 / 不注入 DOM / 不做浏览器插件改版面。
- 一切执行列 `human_manual`；平台指标 `pending_human_measure`；终裁 `carbon_based_arbiter`。
- MED / TCM 强制免责；禁诊断禁处方禁剂量禁疗效承诺。

**科学边界**

- "数字生命 / 呼吸 / 城邦 / 免疫"是**架构隐喻**，实证部分为确定性软件；
  本系统不主张任何意识、目标或自主性。
- "反控平台算法"不成立：四包都不改平台推荐逻辑，也不声称能改；只做**你知道什么**与
  **你怎么记录**。
- `skill_breathing_budget` 的 tick 预算是**建议值**，不来自实时测量；
  投喂给出的"内存 15MB / 延迟 <10ms"等实测数字本包**不复制**（非本机实测，标注为第三方口径）。
- 白皮书是**结构草案**（七章 / 19,500 字配比），正文须逐章写作，不预填未核验事实。
- 仿真 ≠ 证明，碳基终裁。

---

## 10. 许可证

- 内核 `holoaeon`：Apache-2.0。
- 扩展包 `sovereignty` / `subdistill` / `omnilife` / `omnicore` 与认知主权矩阵：MIT。
- 混放口径：内核文件保留 Apache-2.0 头；扩展包与矩阵文档声明 MIT；分别标注，
  不把 MIT 扩展到内核，也不把 Apache-2.0 义务转嫁给扩展包用户。

---

## 11. 路线图

- **v0.6.0（当前）** — 四包齐备：信息流 / 知识 / 生活 / 引擎自述，四验 G18–G21。
- **v0.7** — 可插拔持久化后端与节点间总线传输（默认路径仍零依赖、仍不落盘）。
- **v0.8** — 声明式图/拓扑定义 + 扩展包创作工具包（第三方可写包）。
- **v0.9** — 面向主流开源权重模型服务器的参考适配器（只做接口适配，不内置调用）。
- **v1.0** — 冻结 API、完整文档、稳定扩展包协议。

---

潮起开门，潮落闭嘴。
