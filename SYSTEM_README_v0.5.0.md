# HoloAeon System README · v0.5.0

> **系统型说明文档（System README）** — 描述「一个内核 + 三个横切扩展包」的完整系统边界。
> 本文件为 v0.5.0 版本快照；v0.4.0 的 `SYSTEM_README.md` **原样保留**，两个版本可对照阅读。
>
> 内核 `holoaeon` v0.5.0（Apache-2.0）· `sovereignty`（认知主权）· `subdistill`（SD-Distill）
> · `omnilife`（全域生活）三包（MIT）
> 日期 `2026-10-30` · 密令 **潮起开门，潮落闭嘴**

---

## 1. 系统形态

```
┌──────────────────────────────────────────────────────────────────────────┐
│  holoaeon core  (v0.5.0 · Apache-2.0)                                    │
│  Envelope / Bus / Skill / Memory / Agent / Scheduler / Guard /           │
│  AdaptiveGraph / Cluster / Hypervector / ModelAdapter / Kernel           │
│  ── 九大领域包：25 agents · 47 skills · 9 workflows（口径冻结，G15 硬断言） │
├──────────────────────────────────────────────────────────────────────────┤
│  横切扩展包（EXTRA_PACK_REGISTRY：只加技能与工作流，0 agent，不进 PACK_ORDER）│
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐                  │
│  │ sovereignty   │  │ subdistill    │  │ omnilife      │                  │
│  │ 17 技能/5 流   │  │ 15 技能/7 流   │  │ 18 技能/6 流   │                  │
│  │ R0 → R4       │  │ S1 → S7       │  │ L1 → L6       │                  │
│  │ 信息流主权     │  │ 亚学科蒸馏     │  │ 日常生活主权   │                  │
│  └───────────────┘  └───────────────┘  └───────────────┘                  │
└──────────────────────────────────────────────────────────────────────────┘
```

三条硬边界：

1. **口径冻结** — `G15` 断言 `n_agents == 25 && n_skills == 47`。扩展包只注册技能，
   `roles = []`，一律不进 `PACK_ORDER`。加能力，不加 agent。
2. **零依赖** — 纯标准库；不联网、不开端口、不调外部模型、不常驻、无定时器。
3. **确定性** — 同输入同输出，审计指纹 16 位，跨机可复现。

---

## 2. 三包分工与串联

| | `sovereignty` | `subdistill` | `omnilife` |
|---|---|---|---|
| 作用层 | 信息流 | 知识层 | 生活层 |
| 解决的问题 | 平台用粗标签简化人 | 粗标签本身可被归类 | 生活被降维成消费数据与效率工具人 |
| 手段 | 16 学科跨域锻造 + 反标签 + 平台/协议族谱 | 16 域 → 127 亚学科 + 七阶段蒸馏 + 七项辅助损失 | 6 生活域锚定 127 编码 + 皮肤折叠 + 经络本地交接 |
| 产物 | 查询清单 / 身份自述 / 计划表 | SKC 知识卡 / 共振映射 / 抗标签模板 | 参数卡 / 处置规则 / 台账 / 路径 / 餐单结构 |
| 工作流 | R0 编码 → R4 合规 | S1 采集 → S7 入库 | L1 衣 → L6 SaaS |

串联关系：`subdistill` 生产**不可归类的语义单元** → `sovereignty` 把它们锻造成**可粘贴的
信息流查询** → `omnilife` 把同一套编码下沉到**衣食住行教**，让"生活决策"也带可溯源的锚点。
三包共用同一套 127 编码与同一套红线，彼此不重复发明锁数。

---

## 3. 维度不变式（系统级契约）

```
127 亚学科 × 10 槽位  +  61 保留行      = 1331   行
127 亚学科 × 855 节点 +  56 全局协调节点 = 108641 节点
```

母体 12 项锁数一个不动：`1331` 边长 · `1,771,561` 设计格（稀疏） · `108,641` 曼陀罗节点 ·
`651,846` 希尔伯特 · `22,627` 卡尔曼 · 心跳 `70 / 9700-9769 / 768 维 / α 0.18` ·
细胞骨架 `3 层 × 4 链 / 跨链 12` · 皮肤 `SG-SKIN-V6.0` 八层 · 语义 `10` 模块 ·
赫布 `19 圆 / 17 节点 / 28 流边` · 结构资产 `168 / 40 / 23 / 20` · 台账 `147` 维度。

`omnilife` 的定位是**寻址层的消费者**：它把 6 个生活域挂到 17 个唯一亚学科锚点上
（`wardrobe`: SEMI-04/05 · AEST-05 · BIO-07；`nutrition`: MED-05 · TCM-01/03 · PHYS-03；
`shelter`: PHYS-03 · SOC-04 · AEST-04；`mobility`: MATH-08 · HIST-06 · SOC-04；
`learning`: LOGIC-04 · AI-03 · SOC-06；`saas`: CS-03 · AI-05 · SOC-03），
**不加行、不加节点**，`pack_summary()["addressing_unchanged"]` 与 `missing_anchors == []`
在 `G20` 中断言。

---

## 4. 能力边界（Omni-Life 的"不做"清单）

投喂设计里有一部分动作属于**规避平台风控与伪造身份**，本系统一律不实现，并按名字拒绝。
`REFUSED_OPS` 共 17 项，命中即 `skill_skin_gate()["allowed"] = False`：

```
自动登录 · 多端并发模拟请求 · 模拟器并发 · 切换高匿名代理 · 代理池 · 抓取比价 ·
爬取价格 · 批量下单 · 批量发帖 · 绕过风控 · 绕过验证 · 伪造身份 · 多账号 · 养号 ·
注入 DOM · 调用平台私有接口 · 破解
```

替代路径（系统真正提供的东西）：

| 需求 | 系统给什么 | 谁执行 |
|---|---|---|
| 比价 | `price_ledger` 空台账（平台 / 价格 / 券 / 时间 / 截图列） | 本人在各平台各查一次，手抄或截图 |
| 判断价差 | `price_review` 对**本人登记值**做离散度计算，`>=15%` 标 `worth_human_check` | 本地算术，不推断"杀熟" |
| 主张权益 | `complaint_template` 话术 + 平台官方价保/客服入口 | 本人提交；不自称官方、不代提交 |
| 折叠诱导 | `consumerism_blocker` 规则表（焦虑/稀缺/冲动/攀比四类 11 条） | 本人用平台自带"不感兴趣/屏蔽关键词" |
| 跨 SaaS 关联 | `meridian_route` 交接单（导出 → 本地 → 引用） | 本人操作；`api_calls=0`、`network=False` |
| 生活参数 | `context_trigger` 规则命中 → 建议，不写设备 | 本人手动设置 |
| 健康饮食 | `nutrition_plan` 餐单**结构**（无剂量、无诊断、无疗效） | 本人复核；不适即就医 |

一句边界：**软件只产清单与算术，物理世界与平台账号上的动作由碳基本人做。**

---

## 5. 快速取用

```python
from holoaeon import Kernel
from holoaeon.packs import get_extra_pack

k = Kernel()
for key in ("sovereignty", "subdistill", "omnilife"):
    rep = get_extra_pack(key).install(k)
    print(key, len(rep["skills"]), len(rep["agents"]), len(rep["workflows"]))
# sovereignty 17 0 5 / subdistill 15 0 7 / omnilife 18 0 6

from holoaeon.packs.omnilife_pack import (
    pack_summary, skill_high_dim_search, skill_price_ledger, skill_skin_gate,
    skill_nutrition_plan, skill_travel_route,
)
print(pack_summary()["addressing_unchanged"])                       # True

q = skill_high_dim_search(["wardrobe"], "autumn_study_wear", ["无logo符号干扰"])
print(q["query"])   # 精梳棉 无标识 罗纹领口 透气 无logo符号干扰 秋季 静坐学习 长袖 卫衣

print(skill_price_ledger()["concurrent_probe"], skill_price_ledger()["proxy_switch"])  # False False
print(skill_skin_gate("帮我多端并发模拟请求比价")["allowed"])        # False
print(skill_nutrition_plan()["dose_any"])                           # False
print(skill_travel_route()["path"])                                 # ['住处','图书馆','老街','旧书店']
```

三个扩展包都可 `install(k)` 后直接用内核的 `kernel.skills.call(...)` 调用；
卸载即重新 `Kernel()`，扩展包不写任何宿主状态（无全局缓存、无时间戳落盘）。

---

## 6. 验证矩阵（v0.5.0 实测）

| 层 | 命令 | 结果 |
|---|---|---|
| 内核自检 | `run_all()` | **20/20 组通过**（G15 25/47 未破、G18 6/6、G19 17/17、**G20 21/21**） |
| 内核单测 | `python -m unittest discover -s tests` | **25 tests OK** |
| 内核红线 | `python scripts/redline_scan.py` | **30 文件 / 零违规** |
| 发行包 | `python scripts/make_release.py` | `holoaeon_v0.5.0_20261030.zip`（见 `releases/SHA256SUMS.txt`） |
| 解压复跑 | 独立副本重跑 | 20/20，`addressing_unchanged=True`，锚点零缺失 |

权威记录只认两处：内核 `make_release.py` 输出、认知主权 `runtime_v3/tools/skill_registry.json`。
文档不复刻哈希，避免自引用漂移。

---

## 7. 版本梯（只增不覆盖）

```
v0.3.0  ─ 九包（25/47）                              holoaeon_v0.3.0_20261029.zip
v0.3.1  ─ + sovereignty（17 技能）+ G18             holoaeon_v0.3.1_20261030.zip
v0.4.0  ─ + subdistill（15 技能）+ G19              releases/holoaeon_v0.4.0_20261030.zip
v0.5.0  ─ + omnilife（18 技能）+ G20                releases/holoaeon_v0.5.0_20261030.zip  ◀ now
```

认知主权矩阵侧：`V3.0 → V3.1`（SD-Distill 插件 + `G14`）两版并存，旧 zip 未覆盖。

任一版本都能独立解压、独立自检、独立运行；`releases/RELEASES.md` 是版本索引，
`releases/SHA256SUMS.txt` 是校验权威。

---

## 8. 红线与科学边界

**红线**

- 不联网、不开端口、不认证、不常驻、无 cron；不读写任何平台账号。
- 不自动登录 / 不自动搜索 / 不抓取 / 不批量下单 / 不批量发帖 / 不刷量 / 不规避风控 / 不伪造身份。
- 价格与标签一律 `pending_human_measure`；零伪造平台数据。
- MED / TCM 产物强制免责；禁 `诊断 / 处方 / 剂量 / 疗效承诺 / 包治 / 根治`。
- 一切执行列恒为 `human_manual`，终裁 `carbon_based_arbiter`。

**科学边界**

- 生活域锚点是**知识分区**，不是"用 127 矩阵的算力反控 SaaS"的字面能力；
  本系统不改变任何平台的推荐算法，也不声称能改变。
- `shelter_check` 的日照/通风系数是公开常识的**粗算标尺**（`coarse_proxy`），非建筑物理仿真。
- `nutrition_plan` 是餐单**结构**建议，不是辨证结论；证型须本人自述或执业医师判断。
- `travel_route` 在用户给定图上求最短路，与真实路况无关。
- 仿真 ≠ 证明，碳基终裁。

---

## 9. 许可证

- 内核 `holoaeon`：Apache-2.0。
- 扩展包 `sovereignty` / `subdistill` / `omnilife` 与认知主权矩阵：MIT。
- 混放口径：内核文件保留 Apache-2.0 头；扩展包与矩阵文档声明 MIT；引用时分别标注，
  不把 MIT 扩展到内核，也不把 Apache-2.0 义务转嫁给扩展包用户。

---

## 10. 路线图

- **v0.5.0（当前）** — 三个横切扩展包：信息流 / 知识 / 生活三层打通，0 agent，G18–G20 三验。
- **v0.6** — 可插拔持久化后端与节点间总线传输（默认路径仍零依赖）。
- **v0.7** — 声明式图/拓扑定义 + 包创作工具包（第三方可写扩展包）。
- **v0.8** — 面向主流开源权重模型服务器的参考适配器（只做接口适配，不内置调用）。
- **v1.0** — 冻结 API、完整文档、稳定扩展包协议。

---

潮起开门，潮落闭嘴。
