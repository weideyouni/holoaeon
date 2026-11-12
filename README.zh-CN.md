<div align="center">

# HoloAeon

### 零依赖、生物启发的通用多智能体认知框架——给大模型当管家，给普通人当工具

![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)

![Python](https://img.shields.io/badge/python-3.8%2B-green.svg)

![Dependencies](https://img.shields.io/badge/dependencies-0-success.svg)

![Tests](https://img.shields.io/badge/tests-1016%2B11%2B21%20passed-success.svg)

![SelfTest](https://img.shields.io/badge/selftest-25%2F25-success.svg)

[English](README.md) · [中文](README.zh-CN.md)

</div>

---

## 这是什么

HoloAeon 是**纯标准库、全离线、确定性**的多智能体认知框架：零依赖、零安装、零成本起步，
一台十年前的旧笔记本即可运行。它可构建在任意大模型之上——也可以完全不用大模型独立工作。

**它的定位：给大模型当管家。**大模型负责语言与生成，HoloAeon 负责安检、记账、路由、
复现——让 AI 的每一次回答旁边，站着一个可审计的记忆体。

## 工程宣言

> 版本 V3 ｜ 宣言发布 2026-11-07（V39 快照，已由回读取代）｜ 当前 DOC / HEAD 一律回读、不写死：`python -m holoaeon.selftest` · `git rev-parse --short HEAD` ｜ 证据等级 `measured`（本仓本机实跑）｜ 仿真 ≠ 证明 ｜ 碳基终裁 ｜ 密令：潮起开门，潮落闭嘴

## 一、项目宣言

**医学是整体观、系统观——所以它的工具也必须是。**

九年前，一位刚晋升的乳腺外科副主任医师发现：循证医学与精准医学的版图里，康复医学、中医药与中国民族医药是不可或缺的有益补充；而康复指导——这个最能体现整体观的环节——恰恰最缺工程化支撑。于是他转身走进了恶性肿瘤系统康复工程，又在七年后把这套医学的整体观，蒸馏成了一个软件框架。

**给大模型当管家，给普通人当工具。**

我们不造又一个会说话的 AI。我们造的是站在 AI 旁边的那个**可审计的记忆体**：大模型负责语言与生成，HoloAeon 负责安检、记账、路由、复现。病房里的戒律被原样带进了代码：**任何一个不能被复核的判断，都不配进入人体；任何一个不能被复算的数字，都不配写进 README。**

HoloAeon 纯标准库、全离线、确定性。零依赖、零安装、零成本起步，一台十年前的旧笔记本即可运行。它不承诺"智能"，它承诺**可检验**。

---

## 二、项目公理（八条 · 哲学一句 + 细则 + 违约判据）

公理不是口号，是可以跑命令验证的条款。每条分三层：**哲学一句**（为什么）· **细则**（怎么做）· **违约判据**（什么时候算破戒）。任何一条违约，门禁就红。

### A1 · 每个数字都能复算

> **哲学**：真理只有一种形态——可检验。不可复算的漂亮数字，是尚未穿帮的谎言。医学上它叫"可溯源"，工程上它叫"可复算"，二者是同一条戒律的两种写法。

- 细则：README 每个实测值必须给出对应复算命令（见本文末「数字—命令对照表」）；`SHA256SUMS` 全清单逐条可重算
- 细则：`check_sums` 复算闸**只阻断不重建**——重建是批次动作；自动重建会掩盖"哪一批改的"
- 细则：徽章、门禁行、回执三处数字同源；时点快照文字一律改「以命令回读为准」
- 违约判据：`python scripts\check_sums.py .` 出现任一 `mismatch`，README 的「drift []」宣称即失效

### A2 · 确定性

> **哲学**：相同输入必得相同输出——这是科学共同体得以对话的最低语言。漂移不是"版本差异"，是事故；偶然正确的系统，比稳定的错误更危险。

- 细则：diff0 双层级显式——`2fc892cf9af6e755`（V1 规格黄金冻结）/ `6d119b2a9f2df687`（bench 16 步实测判据）；**层级不同，不是矛盾，永不互比**
- 细则：弃内置随机源（`hash()` → `crc32` / `sha256` 派生），跨进程同输入同输出；时间戳默认关闭
- 违约判据：`benchmarks\bench_public.py` 的 `DIFF≠0`，或任何"这次跑出来不一样"的解释

### A3 · 零依赖

> **哲学**：门槛即排斥。需要先配环境的路径，事实上已经把大多数人挡在门外——普惠不是降价，是拆除门槛。

- 细则：纯标准库、零网络、零密钥、零 GPU；解压即跑，自检即证
- 细则：包内禁 `subprocess`、禁第三方 import；判定层与执行层硬性分层
- 违约判据：红线扫描任一违规；任何"先装个什么才能跑"的前置

### A4 · 仿真 ≠ 证明

> **哲学**：把仿真当能力上报，是这个行业最体面的自欺。诚实不是美德，是基础设施——一旦被污染，建立其上的一切结论同步作废。

- 细则：三级证据标注 `simulated` / `measured` / `untested`，禁止互相顶替
- 细则：**愿景、路线图与已兑现能力硬隔离**；未兑现项公开列表，不折叠成"通过"
- 违约判据：任何 `echo` 冒充 `live`、仿真回执标成实测、愿景写成能力

### A5 · 处置权在人类

> **哲学**：机器可以无限接近判断，但判断的重量只能由人承担。熔断的终点不是"更聪明的机器处方"，是把人请回决策席。

- 细则：闸只报告与阻断，不自动执行处置；急症双熔断（L2+L5）终点是**就医指引**
- 细则：泰坦进化止于提案，合入须人一键 approve；零剂量不称疗效、濒危只论替代
- 违约判据：任何"自动执行了本应由人拍板的动作"

### A6 · 取舍留痕

> **哲学**：没有回放能力的优化，事后无法归因，只能算说法。每一次扬弃都值得被自己回放——记忆不许删除，只许追加。

- 细则：append-only（玉安记忆 / 五地台账 / 信封链），逐行 SHA 可验，断点续跑，不依赖原始会话
- 细则：每次淘汰与降级携带理由码；`UNKNOWN` 单独计数并告警，禁止静默吞掉
- 违约判据：任何"改了但没留痕"、任何删除历史记录的动作

### A7 · 整体观，但隐喻 ≠ 机制

> **哲学**：全息——局部包含整体，是本项目的**设计取向**，源自医学的整体观、系统观。但隐喻是地图不是领土："经络/心跳/代谢"帮人理解结构，不承担证明责任。

- 细则：工程隐喻（经络=消息路由 / 心跳=调度节拍 / 皮肤=防护层）须在代码中显式声明 `metaphor_note`
- 细则：不主张意识涌现，不主张"全息"有物理证明；机制只认确定性判定器
- 违约判据：把隐喻当能力写进功能清单，或把设计取向写成科学结论

### A8 · 维度锁死

> **哲学**：不变式是信任的锚。骨架随意变化的系统，任何"演进"都无法与"退化"区分。小步慢走，每次只改一个小点——慢不是保守，是让每一步可归因。

- 细则：25 智能体 / 47 技能 / 9 域包 / `VERSION=0.9.1` / `BUILTIN_LAYERS=L1-L8` 冻结；`graph` / `scheduler` / `hypervector` / `kernel.submit` 不碰
- 细则：演进只许旁挂（扩展包 / 模块级），单批单提交，批次验收全绿才封口；**五地同头才收口，未收口不开新批**
- 违约判据：维度锁 12 项任一 `violation`；一批多提交；五地未同头就启动下一批

---

## 三、项目功能（一句话版 + 实测口径）

**一个可构建在任意大模型之上——也可以完全不用大模型独立工作的认知框架。**

- **认知骨架**：Kernel 装配 + Bus 消息路由 + Guard 八层防护 + Scheduler 自适应心跳（核心九包 `25 agents / 47 skills`，冻结；全装配 `66 / 280`，非冻结，勿混用）
- **记忆与审计**：JSONL append-only 单一事实源，逐行 SHA 可验；玉安记忆台账断点可续跑
- **领域编排闸门（十一环）**：数学 / 茶 / 宇宙 / 教育 / 神龟 / 学术 / 公共卫生七域蒸馏的「防护—节律—评价」三类形状 + 公共卫生域「登记—分级—调度」形状，外加机器刀、莫比乌斯回流、克莱因投影、全息熔炉四环
- **学术笔痕闸门（`academic_gate`，领域编排环·第十环）**：12 类图案 tell 确定性检测（T01–T12，只报不改）+ 数字 / 引文不动点保全 + 断言-证据强度对账；report-only 零改写，显式拒绝「检测规避」——学术诚实 = claim ≤ evidence
- **公共卫生慢病引擎（`phc_chronic_engine`，领域编排环·第十一环·实战1号）**：A/B/C/D 四级病种登记册（A 类 3 病种高血压 / 2 型糖尿病 / 慢阻肺病，≥4 次随访每年 + 年检）+ 六系统图谱（神经 / 心脑血管 / 内分泌 / 免疫 / 肿瘤 / 骨伤 → 科室·技能路由）+ 7 模态信封（影像只存 SHA256 指针 + 结构化自述，零像素进入引擎态）+ 危险度 R01–R12 十二条可复算规则（急性事件直通 IV 级红档，危急不被分数稀释）+ MDT 意见槽留白·执业医师终审 + 随访调度（≥4 次/年·2 周复访·转诊 2 周追踪回流）+ 端口池 ≤10 + 等保三级 MLPS3 七项 + 审计 SHA 链 + 3 万人口容量估算；零诊断零处方零像素零网络
- **安全与诚实**：红线扫描（禁网络 / 禁密钥 / 禁句柄泄漏）· 去幻觉八阶段流水线 · 急症双熔断 · 零剂量不称疗效
- **进化机制**：神灯（愿望→方案编译）· 泰坦进化（清单→缺口→提案→人审→合入）· 缺口进化桥——**全自动只有提案权，合入权在人**
- **工程验收（本机实跑口径）**：主套单测 **1016 OK** + v3 域 **11** + verax 域 **21**（合计 **1048**）· selftest **25/25** · `v3_gate` **32/32** · `v44` **13/13** · 维度锁 12 维 **PASS** · 红线扫描回读为准：``python scripts/redline_scan.py``（实测值见该批回执；核心包 .py 实数以 ``ls holoaeon/*.py | wc -l`` 回读） · 复算闸 **250 条 0 不匹配**，每批全绿才封口
- **五地同步**：本地 → Gitee（权威）→ GitHub → HuggingFace → 向量海，对象摘要哈希逐条验收，**五地同头才收口**
- **领域资产（自述口径）**：462 项医疗康复知识库（肿瘤康复 / 慢病管理方向）· 1331×1331 多智能体矩阵实战化方法论 —— 均为作者资产登记，**未宣称第三方复核**

---

## 实战部署（机构端工程师入口）

- **部署手册**：`docs/DEPLOY_GUIDE.zh-CN.md`（安装/调试/参数/场景/升级，十章穷举）
- **一键自检**：`python scripts/install_check.py`（7/7 PASS 即就绪）
- **向量库基线**：`python scripts/bench_vector_baseline.py`（字面 100% / 同义 Top-5≈33%）

## 四、成型历程：九年双线，从手术刀到框架

**2017 · 觉醒点是医学观，不是技术。**
潘荟丞，时任唐山工人医院乳腺外科副主任医师（刚晋升），在循证医学与精准医学的临床实践中确认了一个缺口：医学是整体观、系统观，康复指导至关重要，而恶性肿瘤的康复需要中医药与民族医药的有益补充。他由此转向**恶性肿瘤系统康复工程**——从头自学分子生物学、细胞生物学、表观遗传学、中医学、民族医学，并经转岗培训调整至康复医学、全科医学专业。

**2019 · 双线同时出发。**
**医学线**：系统康复工程正式立项——以中医整体维度统摄，西医免疫医学、应激医学、衰老医学为四层维度；宏观从物质、能量、信息，微观从磁场、电场、液态场，两角度切入三场域，系统搭建**人类疾病图谱**。
**工程线**：同年从零自学计算机语言、计算机数学基础与编程——先做多维数据查询的专家系统。

**2019–2026 · 临床实证沉淀。**
深耕神经系统、心脑血管系统、内分泌系统、免疫系统、恶性肿瘤、骨伤等系统慢性疾病的康复，年服务约 1000 人次，有效率 86.7%（**工作室临床统计口径，未宣称第三方复核**）；462 项医疗康复知识库逐年打磨；传承技术通过国家卫健委评审，获**全国卫生健康技术推广传承应用项目传承人**资格；现任唐山市第二医院康复医学专业主任医师、中西医结合恶性肿瘤康复及慢病康复工程负责人。

**2022 · 借 AI 爆发完成关键一跃。**
人工智能浪潮到来，他把多维数据查询的专家系统，进化为自然语言驱动的多智能体架构；1331×1331 矩阵方法论在数十个领域实战演练——"装配→自检→验收→归档"锤炼成肌肉记忆。

**2026-10 → 今 · HoloAeon V0.1 → V38。**
九年沉淀蒸馏为零依赖框架：V0.1 起步，至今 V59；**批次数不写死**，一律以台账 `history` 回读为准（当前 77 条，差额为补正提交与跨批事件，逐条可回读）；每批"投喂包→执行→十项门禁→单批单提交→五地同步→记忆回填"，diff0 黄金值自第一天锁死至今**零漂移**。"早晚能成"被翻译成"这一批能验收"。

---

## 五、现实意义

**科研**：人类疾病图谱（四层维度 × 两角度 × 三场域）为慢病康复研究提供结构化的中西医融合样本；跨五个领域闸门（数学 / 茶 / 宇宙 / 教育 / 神龟）的 `SAME_AS` 趋同观测，为"自组织系统的收敛结构"提供可复算、可回放的研究对象，证据链 append-only 可审计。

**临床**：医学底线被写成代码——急症双熔断（触发即就医指引）、零剂量不称疗效、濒危只论替代、RWE 零伪造。年约 1000 人次、86.7% 有效率的康复实践（工作室统计口径）证明系统康复工程方向成立；**工具永远停在"辅助"，处置权刚性保留给医师与患者**。

**教学**：框架本身就是教材——每个机制有测试、每个批次有回执、每个错误有复盘；从素质教育入手，"用自然语言搭建多智能体架构"是可传授、可复制的工程方法，教育域闸门（血缘链 + 量规）把"学—练—评"闭环做成确定性结构。

**经济**：零许可证成本、零硬件门槛、零运维依赖；一台旧笔记本即可部署，为预算有限的基层医疗机构提供"用得起"的智能化路径。

**民生**：普惠不是降价，是拆除门槛——不联网、不要 GPU、不读英文文档也能跑；目标是让更多患者得到全年龄段、全康复流程的中西医融合系统性服务，把技术送到资源最少的地方，而不是参数最多的地方。

---

## 六、先进性

1. **确定性优先的多智能体**：当主流框架把路由、评估、裁决都交给 LLM，HoloAeon 把它们做成可复算的规则与状态机——**LLM 的输出必须过确定性闸门复核**。
2. **SQLite 式的工程哲学**：单文件可嵌、零依赖、每一字节可校验。外部评审（通义千问 V33–V38 版本解析，静态评估）曾以"agent 领域的 SQLite"作类比；本项目的回应是把这个类比**制度化成门禁**，而不是写进宣传。
3. **可审计的诚实**：`simulated` / `measured` / `untested` 三级证据标注，未兑现项公开列表，不折叠成"通过"。
4. **领域蒸馏方法论**：不复制代码、只蒸馏形状（许可证四级裁决，AGPL/GPL 只读不并入）——五个领域闸门的 `SAME_AS` 趋同观测证明这套方法论可重复。
5. **医学基因的工程纪律**：整体观、系统观的设计取向 + 零剂量、毒剧药刚性考据、碳基终裁的临床安全文化，完整迁移为软件验收文化——这在通用框架中绝无仅有。

---

## 仓集群（C01–C18 + N19 · 结构 → 连通 → 贯续 → 组织 → 语义五件套）

> 设计理念源 = 仓集群五件套投喂（结构包 · 连通包 · 贯续包 · 组织包 · 语义包）四人组第一性原理扬弃；
> 落地态如实标注：**已落地 / 口径在案 / 待产** 三档，不虚报。本节不写死任何实测数字
> ——集群存在性与健康度一律回读：`python -m holoaeon.c18_cluster probe` ｜ GitHub 侧
> `git ls-remote https://github.com/weideyouni/holoaeon-cXX-... refs/heads/main` 逐仓核验。

**一句话**：HoloAeon 本仓是第 19 号仓（N19，土相归零基座，唯一全局观测者）；仓集群 =
18 个同构域仓 + N19 基座。它不是 19 份拷贝，是**一个机制的正交投影**——18 仓共享 N19
的全部机制（心跳 / 总线 / 张量 / 闸门 / 契约），各自承载一个生命领域的第一性问题。

### 五件套 · 落地态对账

| 件 | 理念一句话 | 落地态 | 承载 |
|---|---|---|---|
| 结构（V3） | 仓怎么建、编号怎么定、形状长什么样 | **已落地** | `holoaeon/c18_cluster.py`（ring19）：18 仓注册表 + 五行相位 + 边 Schema + 19×19 耦合矩阵；GitHub 18 仓已建成并逐仓 `ls-remote` 核验 |
| 连通（LINK-01） | 仓与仓怎么连、怎么一起进化 | **部分落地** | 相位生克 / 四类合法边 / 12 必填字段 / ttl·decay·rollback 硬约束在案；五层连接栈 / 事件传播四步 / 共演化算子 O1–O5 **待后续批次** |
| 贯续（CONT-01） | 有机体只能一次一次长出来 | **已落地** | `holoaeon/continuity_gate.py`（ring20）：三贯续轴（时间 / 结构 / 证据）+ B1–B10 断裂点 + G0–G7 门禁三态（未落地诚实 WAIT） |
| 组织（ORG-02） | 谁来干、资源怎么分、怎么复制不失真、怎么算活着 | **已落地（编制骨架）** | `holoaeon/org_gate.py`（ring21）：18 小组五岗编制（仓主≠记录员）+ 任务卡 Schema + 调拨优先级公式 + 适配十态状态机 + 耗散 D1–D6 口径 + B0–B6 深化批次表；C03 G-M 六判据三态（同构/回滚 PASS，12 通道/传播/阻塞/衰减 WAIT） |
| 语义与吸收（SEM-01） | 名字是什么、生态怎么吸收、搜索怎么被引导 | **已落地（张量骨架）** | `holoaeon/tensor_gate.py`（ring22）：四语素命名校验（76 语素位=4×19 穷举，缺语素即命名非法）/ RepoTensor 四模态 ⟨S,M,P,A⟩（S sha256 派生 · M 确定性生成 · P one-hot 相位+枢纽标记 · A 32 槽位图）+ 同输入两次全同的确定性机器证明 / 耦合 C(i,j)=w_phase·cosine 361 全量穷举（19 自耦 + 342 有向，无向 171 为对称视图不重复计数）/ 八层开源分类 L0–L7 + 32 槽位框架 + 18 仓认领 / 取六舍五 + 同化三形态（禁 vendoring）+ 四段台账 / 搜索五维 D1–D5 + search_record 强制 schema（无记录不进实现）→ 90 任务卡 |

### 18 仓一览（编号固定不可变更）

每仓 = 领域第一性问题 + 自组织机制 + 双系统分工（神龟=保存/基线/快照；神马=推演/生成/跃迁）。

| 编号 | 仓名 | 领域 | 主相位 | 第一性问题 |
|---|---|---|---|---|
| C01 | holoaeon-c01-source | 本源 | 土 | 我是谁、如何归零 |
| C02 | holoaeon-c02-body | 身体 | 水 | 身体如何被感知与调节 |
| C03 | holoaeon-c03-meridian | 经络 | 木（传导枢纽） | 信息如何传导、阻塞如何发现 |
| C04 | holoaeon-c04-family | 家庭 | 土 | 亲缘如何影响个体稳态 |
| C05 | holoaeon-c05-education | 教育 | 木 | 知识如何内化与转化 |
| C06 | holoaeon-c06-career | 职业 | 火 | 能力如何发展与变现 |
| C07 | holoaeon-c07-wealth | 财富 | 金 | 资源如何流动与配置 |
| C08 | holoaeon-c08-creation | 创造 | 木 | 创造如何被激发与沉淀 |
| C09 | holoaeon-c09-relation | 关系 | 火 | 人际网络如何演化 |
| C10 | holoaeon-c10-emotion | 情感 | 火 | 情绪如何被识别与转化 |
| C11 | holoaeon-c11-meaning | 意义 | 火生土（意义枢纽） | 这件事对我意味着什么 |
| C12 | holoaeon-c12-space | 空间 | 土 | 环境如何影响身心 |
| C13 | holoaeon-c13-time | 时间 | 水 | 节律与历史如何影响当下 |
| C14 | holoaeon-c14-skill | 技艺 | 金 | 技能如何被掌握与复用 |
| C15 | holoaeon-c15-risk | 风险 | 水 | 创伤与风险如何识别修复 |
| C16 | holoaeon-c16-spirit | 灵性 | 木 | 修行与觉悟如何被理解 |
| C17 | holoaeon-c17-society | 社会 | 金 | 个体如何与制度文化互动 |
| C18 | holoaeon-c18-cosmos | 宇宙 | 总枢（全息镜像根） | 个体如何理解宏观秩序 |
| N19 | holoaeon | 基座 | 土（归零 · 全相位） | 唯一土相归零基座，只扩展不重构 |

主相位分布（结构性常量）：木 3 · 火 3 · 土 3 · 金 3 · 水 3，另传导 / 意义 / 总枢三枢纽跨相位专职连接——19 节点全覆盖无遗漏。仓间作用按五行生克给确定性路由系数（相生 0.8 / 同气 0.6 / 相克 0.4 / 枢纽 1.0，N19 行全连 1.0），有向增益档（相生 1.2 / 被生 1.2 / 同气 1.0 / 相克 0.6 / 反克 0.3）预留给事件传播。

### 边 Schema（连通的最小单元 · 已落地口径）

跨仓连接只走**四类合法边**：`skeleton`（骨架 · 建仓时固定）/ `resonance`（共振 · 心跳激活）/ `semantic`（语义 · 路由建立）/ `event`（事件 · 瞬时一次性）。每条边 12 必填字段（`edge_id / source / target / edge_type / layer / phase_relation / resonance_strength / turtle_state / horse_state / ttl_ticks / decay_rate / rollback_token`），三条硬约束：`ttl_ticks ≥ 12`、`decay_rate ∈ (0,1)`、`rollback_token` 非空——**连接可衰减、可断开、可回滚，永不假设永久连接**。逐条校验：`python -m holoaeon.c18_cluster probe`。

### 诚实边界（本集群篇不虚报什么）

- **五层连接栈**（骨架 / 共振 / 传导 / 语义 / 协作场）、**事件传播四步**（增益 / 衰减 / 阻塞 / 终止）、**共演化算子 O1–O5**（相位耦合 / 梯度传递 / 基因漂移 / 差异选择 / 全息镜像）：口径在本节与投喂包在案，**代码待后续连通批次**——G2–G7 门禁对此诚实 WAIT（`python -m holoaeon.continuity_gate gates` 回读）。
- 素材原文的「78 梅塔特隆主干边 / 108641 共振带索引」未采用：前者未经实测几何，后者在该体系语境中是「当前语言模式」数字而非共振带索引——**挪用数字不诚实**，弃（四人组扬弃裁决留痕）。
- 反同质化实测：18 仓领域问题向量两两余弦均值实测达标（同构而不同质——S5 反向指标口径）；当前实测值由 `python -m holoaeon.c18_cluster probe` 回读，不写死。
- 集群骨架（每仓 README + 同构包 + 域闸门 + 测试 + `.gitignore`）逐仓独立可运行；远端建仓为外部不可逆动作——已经碳基确认并由执行端完成（建成回执在 `reports/v55_receipt.json` 的 `github_create` 字段，逐仓 HEAD 可查，`ls-remote` 18/18 核验）。



---

## 七、愿景与路线（方向声明，不计入已兑现能力）

按 A4 公理，本节是**地图不是脚印**：以下目标均未宣称已实现，逐条由未来批次验收。

### 7.1 我们要去的地方

疾病的康复，从来不是某个人、某家医院、某种医学体系能独自完成的事业。慢性病正在成为世界共同面对的漫长战役——它不分国界、不择贫富，在神经系统的退化里、在心脑血管的堵塞里、在免疫系统的失衡里、在肿瘤的阴霾里，消耗着亿万个家庭的日常。而人工智能的崛起，第一次让"把系统性的康复能力送到每一个角落"有了技术上的可能。

我们想做的，是完成**人类健康的一次智能化转化**：不是用机器替代医生，而是把整体观、系统观的康复智慧，转译成可复算、可复制、可审计、可普惠的工程形态——让一位基层医师手边有一套经得起复核的辅助系统，让一位偏远地区的患者也能获得全年龄段、全康复流程的中西医融合指导，让每一次康复判断都像本项目的每一行代码一样：**留痕、可回放、经得起复算**。

### 7.2 四条并行的路

- **全周期康复工程**：全年龄段、全康复流程的中西医融合系统性工程——从评估到指导，从 MDT 多学科协作到临床与亚临床评估，让康复不再是治疗结束后的附属品，而是贯穿生命全程的系统设计
- **康复 × AI 应用面**：科研、临床、康复、教学、数据分析、病案自动化、体检数据解读、系统性生活建议指导、传感器与物联网、智慧营养、智慧药房——每一个方向都是一个待验收的批次，而不是一句口号
- **素质教育与毕生事业**：从素质教育入手，把"自然语言搭建多智能体架构"当作毕生事业去传授——让更多人不必从零自学九年，就能站在一套成熟的纪律上建造自己的系统
- **开放平台**：搭建让更多同行加入系统性康复工程大军的协作平台，把人工智能的工具属性发挥到最大，把人的判断价值守护到最后一刻

### 7.3 一封写给同路人的公开信

这个项目从一间病房、一台旧笔记本、一个人的自学开始，但它从不打算停留在一个人手里。

**我们诚挚邀请国内与国际的有识之士共创此项目**——无论你是临床医师、康复师、中医药与民族医药的传承者，还是工程师、数据科学家、教育工作者、患者组织的一员；无论你在中国还是世界的任何一个角落，说哪一种语言：只要你也相信**判断必须可复核、技术必须可普惠、人的终审权不可让渡**，这里就有你的位置。

共创的方式是开放的，纪律是共享的：你可以带来一个领域的知识（它会被蒸馏成一道闸门），带来一次严格的评审（每一个硬伤都会被登记、修复、致谢），带来一个地区的需求（它会变成下一条愿景路线的验收标准），甚至只是带来一次认真的使用与一次诚实的批评——在本项目的台账里，批评与贡献同样留痕，同样被尊重。

康复医学教会我们：**没有任何一种康复是孤立完成的，每一个人体的自愈，都需要整个系统的协作。** 项目亦然。让我们为世界疾病康复共同出力——一个人可以走出一间病房，一群人才能走完这场漫长的战役。

潮起时，门为每一位同路人敞开。

> **本节性质声明**：以上为**方向与邀请**，不构成任何投资、合作、采购或医疗服务的要约或承诺；具体事项须另行书面约定，并服从 A4（愿景 ≠ 已兑现能力）与 A5（处置权在人）。

---

## 八、致谢

本项目以"投喂包协作"方式构建——38 个批次的需求、评审、挑错、执行与复盘，来自对国产大模型的**遍历穷举式协作**：同一份投喂包在多家模型间穿梭，能者执刀，众智互校。这不是客套，是可回读的批次链路事实。

**协作名单（印记分三级：`measured` = 有批次回执/报告可回读；`untested` = 参与比对但无独立回执，不虚标）：**

| 模型 | 厂商 | 协作印记 | 印记等级 |
|---|---|---|---|
| **Kimi** | 月之暗面（Moonshot AI） | 总监侧主理：批次策划、投喂包撰写、四人组定调、跨平台工程记忆（玉安记忆）承载 | `measured` |
| **豆包** | 字节跳动 | 执行侧主理：批次执行、闸门实跑、单批单提交、五地同步推送 | `measured` |
| **通义千问** | 阿里巴巴 | 外部评审：V33–V38 版本功能解析与意义评估，P0 硬伤（V38 清单 2 条不匹配）由其指出并闭环 | `measured` |
| **DeepSeek** | 深度求索 | V16 期确定性自主调度对标蒸馏的设计参照 | `measured` |
| **文心一言** | 百度 | 遍历穷举式方案比对 | `untested` |
| **智谱 GLM** | 智谱 AI | 遍历穷举式方案比对 | `untested` |
| **讯飞星火** | 科大讯飞 | 遍历穷举式方案比对（教育 / 医疗场景适配参照） | `untested` |
| **腾讯混元 / 元宝** | 腾讯 | 遍历穷举式方案比对 | `untested` |
| **MiniMax** | MiniMax | 遍历穷举式方案比对 | `untested` |
| **华为盘古** | 华为 | 遍历穷举式方案比对 | `untested` |

国产大模型不是本项目的"用户"，是这套纪律的**共同锻造者**——每一个模型都以自己的方式当过一回"四人组"。也致谢每一位在病房里教会我们"判断必须可复核"的患者与同行。

---

## 九、诚实边界（它不是什么）

- 不主张意识涌现，不主张"全息"有物理证明——隐喻归隐喻，机制归机制（A7）
- 不做全自动合入、不做无人值守的处置——人的终审权不可让渡（A5）
- 不提供医疗诊断与剂量建议——急症一律熔断到就医指引；临床有效率数据为**工作室统计口径**，未宣称第三方复核
- 愿景与路线（第七节）是方向声明，**不是已兑现能力**（A4）
- 未实测的路径一律标 `untested`，不写成"通过"；仿真结果一律标 `simulated`
- 本框架为工程与工程管理工具，不构成医疗器械注册产品，不替代任何法定诊疗流程

---

## 落款

神话是结果，纪律是过程。这个项目不许愿"早晚能成"，只承诺**每一批都能验收**——潮起开门，潮落闭嘴，让工程结果替我们说话。

桃花庵出品 ｜ 潘荟丞 发起 ｜ 碳基终裁，仿真≠证明

---

## 附 · 数字—命令对照表（A1 合规 · README 内每个数字的复算入口）

**口径（重要）**：本表**不写死任何实测值**——用例数、红线文件数、清单条数、HEAD 每批必变，写死即过期（V41 收尾复算闸实测到的正是这一条）。左列是口径名，中列是复算命令，右列是判定方式。两份 README 的当前口径位由机器逐项对账：`python F:\doubaowork\holoaeon_lathe\readme_claims_check.py` → `VERDICT: PASS|FAIL`。

| 口径 | 复算命令（仓根 cwd） | 判定方式（一律回读，不写死） |
|---|---|---|
| 主套单测 | `python -m unittest discover -s tests` | 以 `Ran N tests … OK` 回读为准 |
| v3 域 / verax 域 | `python -m unittest discover -s tests\v3` / `-s tests\verax` | 以各自 `Ran N tests … OK` 回读为准 |
| 合计（主套 + v3 + verax） | 上两条计数之和 | 算术复算；徽章与本行必须同源 |
| selftest | `python -m holoaeon.selftest` | 以**末行** `==> N/N` 回读为准（前面各 `[PASS]` 行是子包计数，勿取首个） |
| v3_gate | `python scripts\v3_gate.py`（**无参**；`--json` 会 argparse 报错） | 以 `N/N PASS` 回读为准 |
| v44 | `python scripts\verify_v44.py`（须先 `five_site_dna build`） | 以 `N/N` 与无 A10 假红回读为准 |
| 维度锁 | `PYTHONPATH=. python scripts\check_dimension_lock.py` | 以 `PASS`（12 维 / 7 闸 / 0 violation）回读为准 |
| 红线 | `python scripts\redline_scan.py` | 以「扫描文件数：N」+「结果： 干净（零违规）」回读为准 |
| 清单 | `python scripts\check_sums.py .` | 以 `"ok": true` / `"total": N` / `"mismatches": []` 回读为准（闸只阻断不重建） |
| diff0 | `python benchmarks\bench_public.py`（跑完 `git checkout -- benchmarks` 还原） | 以 `DIFF=0` 与判据 `6d119b2a9f2df687` 回读为准 |
| py38 语法 | py38 解释器语法解析 | 以 `parsed=N / failures=0` 回读为准 |
| 装配 | `python -c "from holoaeon.packs import EXTRA_PACK_ORDER"` + 装配面板 | 冻结口径以 25 agents / 47 skills 回读为准（全装配 66/280 非冻结） |
| 五地同头 | S1 `git rev-parse HEAD`；S2/S3 `ls-remote`；S4 manifest；S5 `mirror_hf.py` 回读 | 五值一致即同头（A8 判据回读入口）；**永不写死 sha** |

---

## 当前工程状态（随批次更新；取数一律回读，不写死）

| 项 | 实测值 |
|---|---|
| 产出维度（锁死） | **25 智能体 / 47 技能 / 9 域包**；`diff0_hash=2fc892cf9af6e755`、`tamper=f42c8229ee5acd73` 未变 |
| 最新批次 | **V59 张量与吸收件（ring22 · 五件套终章：新增 `tensor_gate.py`——四语素命名校验（76 语素位，缺语素即命名非法）/ RepoTensor 四模态 ⟨S,M,P,A⟩（S sha256 派生 · M 确定性生成 · P one-hot 相位 + 枢纽标记 · A 32 槽位图）+ 同输入两次全同的确定性机器证明 / 耦合 C(i,j)=w_phase·cosine 361 全量穷举（19 自耦 + 342 有向，无向 171 视图另列不重复计数）/ 八层开源分类 L0–L7 + 32 槽位框架 + 18 仓认领 / 取六舍五 + 同化三形态（禁 vendoring）+ 四段台账 / 搜索五维 D1–D5 + search_record 强制 schema（无记录不进实现）→ B0–B6×五维 90 任务卡；代码批次 · 主套 1016 · redline 138 · DOC 提升 `0.9.53`）** —— 本栏随批次更新，权威口径以 `git log -1 --format=%s` 回读为准 |
| 扩展卡槽 | **12 个**：occupied 6 / open 1 / reserved 4 / blocked 1（只声明不接线；本批**不新增、不占用**槽位） |
| 门禁 | `v3_gate 32/32` · `selftest 25/25` · `unittest 1016 OK`（skipped=0；主 tests，含 V24 `test_swarm_intel` 8 例 + V25 `test_machine_tool` 15 例 + V26 `test_mobius_vortex` 12 例 + V27 `test_klein_projection` 19 例 + V28 `test_holo_forge` 13 例 + V31 `test_titan_evolver` 29 例 + V32 `test_gap_bridge` 11 例 + V33 `test_math_gate` 11 例 + V34 `test_tea_gate` 11 例 + V35 `test_cosmo_gate` 12 例 + V36 `test_edu_gate` 13 例 + V37 `test_shengui_gate` 19 例 + V38 `test_check_sums` 5 例 + V40 `test_academic_gate` 19 例 + V41 `test_phc_chronic_engine` 25 例+ V42 `test_phc_recall` 18 例 + V43 `test_craft_gate` 19 例 + V44 `test_twin_verify` 21 例 + V45 `test_teach_gate` 17 例 + V46 `test_v46_pharma_probe` 20 例 + V47 `test_v47_deploy_gateway` 24 例 · V49 `scripts/exp_v49_forge_gate.py` 66 例（独立实验田脚本，V50 已移出 tests/ 防误 discover）+ V51 `test_v51_circuit_gate` 47 例 + V51R `test_v51r_hardware_gate` 45 例 + V52 `test_v52_cinema_gate` 35 例 + V53 `test_v53_palette_gate` 37 例 + V54 `test_v54_palette_enhance` 33 例 + V55 `test_v55_c18_cluster` 47 例 + V56 `test_v56_continuity_gate` 54 例 + V58 `test_v58_org_gate` 56 例 + V59 `test_v59_tensor_gate` 84 例）+ `v3 11 OK` + `verax 21 OK` · `旁挂 184 OK`（`tests_contract` 的 `test_10_no_new_pack` 已改下界 `>=11`，V12 起不再过期） · `v44 13/13` · `v45 7/7` · `v46 9/9` · `v5 11/11` · `dv 8/8` · `redline 138 文件 0 违规` · `check_sums ok=true`（V38 复算闸：SHA256SUMS 250 条复算 0 不匹配，闸只阻断不重建） · `drift []` |
| 五地同步 | 本地 · Gitee · GitHub · Hugging Face · 向量海 —— 见文末 [附录 A](#附录-a--五地同步v11) |
| 版本脉络 | V4.0 → V6.1 → V11 → V12 逐提交回溯 —— 见文末 [附录 B](#附录-b--版本升级说明v3--v11) |
| V4 主文档 | [`README_FUSION_V4_20261102.md`](README_FUSION_V4_20261102.md) · 同步规则 [`data/FIVE_SITE_SYNC_DNA.md`](data/FIVE_SITE_SYNC_DNA.md) |
> **注记（V47-A）· 向量库三件声明与域分离**：①**对齐口径**——1e3–1e5 条目、单次检索毫秒级，与 `sqlite-vec` / `faiss-cpu` 在 3–4 万人辖区知识库规模同级（本机实测见 `scripts/bench_vector_baseline.py`）；②**差异化**——零依赖纯标准库（pip 装完即用，无编译链、无原生依赖）、确定性（sha256 3-gram bundle，同文同向量逐位可复现）、离线零网络、`neural=false`；③**不做什么**——十亿级 ANN / 神经嵌入 / GPU 加速。**域分离**：知识召回域（康复知识 / 指南条目 / 教育语料）走向量库正当；医保报销查询仍走 `pharma_gate` 精确查表（V46 不动）。同义改写组 **Top-1=0** 是字面通道的天花板，如实声明：跨词汇语义召回需共现统计语料（semvec 路线）或 bridges 层神经旁挂，**不靠调参拟合**。

> **注记（V47-B）· 网络二极管与处置权分离**：`OUTBOUND_ALLOW = ()` 空集是**结构性**保证（不是可配置策略项）——内网数据不出内网；入站只收升级包，须 SHA256 合法 + 机构审批 + staging 隔离待检。模型耦合与入站裁决均 **report-only**，实际网络动作由部署侧网关（防火墙 / nginx）执行——本仓只发裁决，不接线。

> **注记（V46-C）· 机翼簇名实对齐**：`机翼簇`（一核六翼技能编组）是**数据侧描述词 / 隐喻名**，表达的是「一核六翼」的技能编组形状；机制侧由第 19 扩展包 `swarm_intel`（`holoaeon/packs/swarm_intel_pack.py`，5 skills / 3 roles / 2 workflows）承载。仓内没有同名代码模块——这是**命名与实现的对应关系**，不是实现缺口；千问 V45 核验所指「七大机制唯一无代码承载」即此。

> **注记（V46-D）· 徽章口径**：徽章 `tests-526` 与门禁行 `unittest 526 OK` 以本机实跑 `python -m unittest discover -s tests` 为准。徽章是 shields.io 静态值，不随提交自动刷新；数字与实测不符时，**以实测为准**。


> **diff0 双哈希层级说明**：`diff0_hash=2fc892cf9af6e755` 是 V1 规格黄金值（冻结，永不允许漂移）；`DIFF0=6d119b2a9f2df687` 是 bench 16 步运行一致性实测判据（随门禁实测记录）。两者层级不同，非矛盾。

### V5.1 · 设计语汇（旁挂，不改维度）

把 Impeccable（[`pbakaus/impeccable`](https://github.com/pbakaus/impeccable)，Apache-2.0，作者 Paul Bakaus）的**范式**本地化——不是分支、不是移植：本仓没有它的引擎二进制，也没有它的规则原文与模板，只用「命令即词汇 + 确定性规则 + P0–P3 分级」这一套做法，规则与释义全部自写。

- **24 个命令**：steer 9 / review 2 / finish 6 / iterate 2 / plan 4 + 1 个上游弃用别名，`vocabulary.command_ids()` 可回读。
- **12 条确定性规则**：`DV-01`–`DV-12`，各带分级（P0 最该先修）与经络通道，命中给行号与证据；**不宣称与上游 62 条等量**。
- **3 种编译模式**：`elaborate`（源码→元件/端口）· `simulate`（跑规则→分级命中）· `netlist`（命中→规则/通道网表），对应 EDA 的分析 / 仿真 / 综合。
- **4 条经络通道**：`blood` / `lymph` / `qi` / `shen`，沿用仓内既有分组，不新增第五通道。
- **零 LLM、零 API key、零出网**；只出建议与先修顺序，**不写回你的源码**。

```powershell
python scripts\verify_design_vocab.py   # 8 项判据，写 reports/design_vocab_check.json
```

**维度不变**：25 智能体 / 47 技能 / 9 域包不动，`data/extension_slots.json` 仍 12 条；本能力**不认领、不占用**任何 `EXT-` 槽。合作开发、扩展规则、未来槽位的走法见 [`docs/设计语汇与协作开发指南.md`](docs/设计语汇与协作开发指南.md)。

### V5.2 · 门禁自指修复与代码卫生（不改维度）

自查版 12 条意见逐条核实后落地（`evidence_class=simulated`）。核心问题只有一类：**自指处理不彻底**——只给单个校验器打补丁，没做成通用机制；同时把依赖本机路径的判据写进门禁，导致“13/13”只在作者本机成立、CI 从未验证。

- **A10 自指排除完备化**：不再只排除自己，改为排除全部兄弟校验器回执（v43/v44/v45/v46/v5/dv + 五地 manifest），并如实返回 `self_excluded_count`。
- **A11 切断传染**：`others_passed` 不再包含 A10。A10 属环境项，它单独红时 A11 仍 PASS——环境红不再伪装成内容红。
- **skipped 第三态**：manifest / ivsa 不在本机时记 `skipped` + `pending_human_measure`，不计入 `passed/total`，**不当作 PASS**。
- **路径去硬编码**：`five_site_dna` 的交付目录与回执路径由仓库位置推导（仍可用 `HOLOAEON_PKG` / `HOLOAEON_RECEIPT` 覆盖）；`verify_v44` 的 ivsa 根改走 `HOLOAEON_IVSA_ROOT`。
- **句柄泄漏清零**：`json.load(open(...))` 与 `open(...).read()` 在 `scripts/` 全部改为 `pathlib` 一次性读取，回读计数 0。
- **CI 补三道闸**：`tests_contract`（168 例）、`check_dimension_lock`、`verify_design_vocab` 进 workflow——此前契约测试从未在 CI 跑过。
- **L3 归一化（[golden]）**：Guard 危险模式判据补 NFKC + 零宽剥离 + 同形字折叠 + 分隔符拼接折叠；原本命中即拦截的文本 reason 与旧版逐字一致，`diff0` 仍 `2fc892cf9af6e755`、篡改值仍 `f42c8229ee5acd73`。
- **兜底开关（保守版）**：`BROADCAST_ON_NO_MATCH` 与 `ALLOW_SINGLE_SKILL_FALLBACK` 默认仍为 `True`，**行为不变**；改 `False` 才会 fail-loud。
- **技能基座化**：六机制（全息心跳 / 细胞骨架 / 皮肤 / 语义通信 / 赫布场 / 经络）的模块入口与外部技能“登记不复制”口径，见 [`docs/技能基座化与六机制接线指南.md`](docs/技能基座化与六机制接线指南.md) 与 `data/v5_skill_base_registry.json`。

```powershell
python scripts\verify_v43.py          # 11/11
python scripts\verify_v44.py          # 13/13（首跑 12/13 属天然自指，第二次收敛）
python -m unittest discover -s tests_contract   # 168 OK
python scripts\check_dimension_lock.py          # 0 violation · diff0 未漂移
```

**维度不变**：25 / 47 / 9 与 12 个 EXT 槽一位未动；`spec.VERSION` 仍 0.9.1。

### V6.0 · 族级登记表 · 路由第三态 · 代码卫生收口（不改维度）

`DOC_VERSION` 0.9.3 → **0.9.5**（`spec.VERSION` 仍 0.9.1，不回写运行态标识）。V6 投喂包 12 条 + 额外 3 条逐条实测后：V5.2 已修 8 条、本批补 7 条。

- **句柄清零到底**：`json.load(open(...))` / `open(...).read()` 全仓复扫 **0 处**（V5.2 只清了 `scripts/`，本批补 `tests_contract/` 6 处与 `skills/holoaeon-video-tensor-dna/` 4 处）。
- **红线防回归**：`holoaeon/redline.py` 新增 `FORBIDDEN_NESTED_OPEN = {"load","loads","read"}` 与 `visit_Call` 两段判定——以后谁再写内联开句柄，`redline_scan` 直接红。
- **路由第三态**：无内置技能命中时 `submit()` 返回 `status="no_agent_matched"` + `hint` + `external_candidates`，不再把「没匹配上」伪装成「N 条结果」；显式 `to="*"` 才广播。
- **兜底可观测**：`agent.handle()` 结果新增 `degraded` 字段，单技能兜底被借用时置 `True`，事后能看出这次成功是「真命中」还是「借来的」。
- **开关进配置**：`HoloAeonConfig` 增 `broadcast_on_no_match` / `allow_single_skill_fallback`（默认 `True` 保持现状）；模块级常量降级为缺省值，`register_agent` 把配置下沉到每个 agent。
- **守卫精度（[golden]）**：`DANGER_PATTERNS` 的宽匹配 `.env` 收紧为 `open('.env` / `open(".env` / `dotenv`——「文档里提到 .env」不再被误拦，真正读凭证仍拦。`diff0` 仍 `2fc892cf9af6e755`、篡改值仍 `f42c8229ee5acd73`。
- **1199 条外部技能族级登记 + 桥接**：`data/v6_skill_family_registry.json` 把 1229 条索引收成 **58 个「域×机制」族**（1,229 成员，`members_sha256` 可回读），`holoaeon/fusion_upgrade/external_skill_registry.py` 提供 `load/stats/family_of/match/route` 与 `Kernel.resolve_external()`。**登记不复制、不改 47 条内置技能**：桥接是「族的候选出口」，执行仍走 25 个 agent。

```powershell
python -m unittest discover -s tests_contract   # 184 OK（含 V6 12 例 + V6.1 4 例）
python scripts\redline_scan.py                  # 扫描 83 文件，零违规
python scripts\check_dimension_lock.py          # 12 维度 + 7 闸 + 0 violation，diff0 未漂移
python -c "from holoaeon.fusion_upgrade import external_skill_registry as e; print(e.stats())"
```

**维度不变**：25 智能体 / 47 技能 / 9 域包 / `EXTRA_PACK_ORDER=10`；`diff0_hash`、`tamper`、`spec.VERSION` 三个冻结值一位未动。

### V6.1 · 工程纪律固化 · A10 派生 · 交付票据回写（不改维度）

`DOC_VERSION` 0.9.5 → **0.9.6**（`spec.VERSION` 仍 0.9.1）。本批只做「必须做」的三件，全部不碰 `diff0`：

1. **A10 自写回执改派生**：名单不再硬编码，从 `five_site_dna.REPO_FILES` 派生 `reports/*.json`，产生者由 `scripts/{verify_,build_,check_,gen_}*.py` 回填——新增写型校验器无需再手改 A10；派生为空退回 `LEGACY_SELF_REPORTS` 并标 `self_derive="legacy"`（fail-loud）。
2. **`missing` 不豁免**：`repo:missing:` 不再算自指——删回执是真实退化；只排除 `changed` / `new`，且每条记 `owner` + `prev_sha16` + `curr_sha16` 差分证据。
3. **票据回写 + 纪律入库**：`01` / `06` 追加 V6 章节；新增 `docs/工程纪律_批次升级与五地同步.md`（八步写序 / 五地同步 / 失败处置 / 批次命名），并固化为技能 `holoaeon-batch-upgrade-discipline`，随全域技能根加载、触发即执行。

```powershell
python -m unittest discover -s tests_contract   # 184 OK（+ test_v44 4 例）
python scripts\verify_v44.py                    # 13/13；A10 self_derive=derived
python scripts\redline_scan.py                  # 0 违规
python scripts\check_dimension_lock.py          # diff0 未漂移
```

**维度不变**：25 / 47 / 9 与 `EXTRA_PACK_ORDER=10` 一位未动；`spec.VERSION=0.9.1`、`diff0_hash`、`tamper` 三值仍未动。


### V11 · 城邦架构融合 · 拓扑共振升级（V11-A→E，不改维度）

`DOC_VERSION` 0.9.10 → **0.9.11**（`spec.VERSION` 仍 0.9.1）。对应 `AGENT_FEED_V11_CITY_STATE_FUSION_20261103.md` 第七章，五步贯序执行：

1. **V11-A · Graph 集成**：`topology_resonance_pack.py` 追加 `graph_mandala_expand`（曼陀罗扇出）/ `graph_mobius_flip`（莫比乌斯回边）/ `graph_klein_convergence`（收敛+熔断），不碰 `graph.py`（按真实 `weights` 矩阵接口实现，投喂包 `add_edge()` 示意已勘误）。
2. **V11-B · L10 贝叶斯层**：`guard.py` 新增 `_L10_LIKELIHOOD` + `l10_bayesian(env)`（`bayes_feature` 后验 >0.5 → BLOCK，无特征放行）；`Guard.__post_init__` 条件挂载；`GuardConfig` 新增 `bayesian_guard: bool = False`（默认关，`BUILTIN_LAYERS` 一字未动）。
3. **V11-C · Runtime 增强**：新建 `holoaeon/topology_runtime.py`（StateReducer/Checkpoint/CircuitBreaker/DissipationMonitor），纯标准库零包内依赖。
4. **V11-D · 治理技能**：追加 `city_state_governance`（循环检测+熔断+退避重试）与 `dissipation_emergence_monitor`（熵趋势+涌现判定），skills 14→16。
5. **V11-E · 文档版本**：`DOC_VERSION` 0.9.10 → **0.9.11**。

```powershell
python -m holoaeon.selftest                # 25/25
python scripts\check_dimension_lock.py     # 0 violation · diff0 未漂移
python scripts\v3_gate.py                  # 32/32
python scripts\redline_scan.py             # 88 文件 · 零违规
python -m unittest discover -s tests       # 68 OK（V11 补丁 PR-3 新增 L10/拓扑运行时 29 例）
```

**维度不变**：25 / 47 / 9 与 `spec.VERSION=0.9.1`、`diff0_hash=2fc892cf9af6e755`、`tamper=f42c8229ee5acd73` 三值仍未动；`EXTRA_PACK_ORDER=12` 未再增；Guard 默认 9 层、开启 L10 后 10 层（附加层不计入 `guard_layers=8`）。

### V11 补丁升级 · PR-3 L10/拓扑运行时集成测试（不改维度）

投喂的补丁升级工程经**判据优先**核查后，仅 PR-3 为真实缺口并落地：

- **新增 `tests/test_l10_bayesian.py`（13 例）**：L10 贝叶斯守卫纯函数语义（delete/network 后验 >0.5 拦截、write 低先验放行、未知特征回退 safe 表、非法先验回退 0.15）+ Guard 挂载语义（默认关不改变既有行为、开启后 L10 生效且层序 L9→L10、BUILTIN_LAYERS 8 层不变）。
- **新增 `tests/test_topology_runtime.py`（16 例）**：StateReducer 指数平滑/dict 归约/replace/快照恢复、Checkpoint 快照链、CircuitBreaker closed→open→half_open 状态机、DissipationMonitor 熵/秩序度/耗散率/重组触发。
- 门禁实测：`unittest 68 OK` · `selftest 25/25` · `redline 88 文件 0 违规` · `维度锁 0 violation`。

**投喂其余 PR 核查结论（如实披露，未执行）**：PR-1（P0 门禁自指三项）**已修**（A10 派生化、A11 传染切断、路径环境变量化，V6.1 落地）；PR-2 中 P1-4a 句柄泄漏**不属实**（V6 已清零+红线防回归）、P1-5 CI **不属实**（已跑契约）、P1-6 README「42 文件」**无此口径**；P1-4b `ivsa/eda_pipeline.py` 3 处 `open().read()` **真实存在**（daily 日志记录 ResourceWarning），但 ivsa 为独立客仓，按纪律「不接客仓写入」且会破坏 A12 门禁，**只记录不修改**，需授权后另行处置。PR-4（MCP 桥接）投喂自标可选/后续，**本批不展开**。


### V12 · 管家操作系统引导模块（V12-A→E，不改维度）

`DOC_VERSION` 0.9.11 → **0.9.12**（`spec.VERSION` 仍 0.9.1）。对应 `AGENT_FEED_V12_BUTLER_OS_BOOTSTRAP_20261103.md` 第三部分，步骤 A→E 贯序执行：

1. **V12-A · 四人组执行顾问扩展包**：新建 `holoaeon/packs/quartet_director_pack.py`（**第 13 扩展包**，`key="quartet_director"`）——14 技能 / 5 角色 / 2 工作流（`quartet_advisor_flow` 五步闭环 / `quartet_emergence_flow` 涌现+回执闭环），**内联实现不 import quartet_toolkit**（零外部依赖）；公开 `check_emergence(p1,p2,p3,p4)`（涌现条件：P2×P3 强共振≥0.7 + P1 愿景≥0.6 + P4 风险≤0.4 + order>0.30；实测 `check_emergence(0.85,0.85,0.85,0.30)` → `emergence=True, order=0.5237`）；`advisor_selfcheck()` 校验 14/5/2 + 涌现确定性。投喂包 dict 写法已转 base.py dataclass 契约、ROLES 缺 `skills` 字段已补全、`_check_emergence` 已公开化。
2. **V12-B · Butler OS 引导模块**：新建 `holoaeon/butler_os.py`（OS 式菜单 7 项 + 0 退出：1 安装引导 / 2 自检 / 3 技能清单 / 4 四人组加载 / 5 启动桥接服务 / 6 提交任务 / 7 状态快照；纯标准库、懒加载 kernel、`_readline` 替代 `input` 规避红线）+ 双击启动入口 `holoaeon_os.bat`（chcp 65001）/ `holoaeon_os.sh`。
3. **V12-C · 注册第 13 扩展包**：`packs/__init__.py` import + `EXTRA_PACK_REGISTRY` 登记 + `EXTRA_PACK_ORDER` 追加 `"quartet_director"`（12→**13**）；`spec.py` `DOC_VERSION` 0.9.11 → **0.9.12**（`VERSION` 0.9.1 冻结未动）。
4. **V12-D · 命令注册**：`pyproject.toml` `[project.scripts]` 追加 `holoaeon-os = "holoaeon.butler_os:main"`、`holoaeon-quartet = "holoaeon.packs.quartet_director_pack:main"`。
5. **V12-E · 验证 + README + 回执 + 五地**：全验证绿 + 三份 README V12 段 + `reports/v12_receipt.json` + 单批单提交 + 五地同步推送回读 + S4 回执刷新 + 交付。

### V12.1 · 未决项闭环（第一性原理裁决 · 单提交）

- **契约测试同步（执行）**：`tests_contract/test_hebbian_store.py` `test_10_no_new_pack` 由写死 `len(EXTRA_PACK_ORDER)==11` 改为下界 `>=11` —— 扩展包按批次递增（V8=11 → V11=12 → V12=13），契约本意是锁 `PACK_ORDER==9`（25/47/9 维度锁）与扩展登记隔离；对可演化集合写死精确值导致每批过期（V9 起漂移至今）。改为下界防回退，`tests_contract` 184 全绿。
- **MCP 桥接（执行）**：新建 `holoaeon/mcp_adapter.py` —— MCP（Model Context Protocol，2024-11-05 规范）stdio 传输最小协议子集（JSON-RPC 2.0：`initialize` / `ping` / `tools/list` / `tools/call`）；暴露 3 工具：`holoaeon.task`（通用任务提交，复用 `frontend_adapter.handle_request` 契约）/ `holoaeon.status`（状态快照：runtime_id/VERSION/DOC_VERSION/agents/skills/guard_layers）/ `holoaeon.quartet`（四人组涌现，直通 `check_emergence`）。零依赖、无网络、无 GPU；与 butler_os 同构（同一契约、不同运输层：本地菜单 vs 标准协议）；`pyproject` 注册 `holoaeon-mcp` 命令；自测 13/13（含 parse_error -32700 / invalid_request -32600 / unknown_tool -32602 / method_not_found -32601 错误分支）。
- **悬挂项（记录不执行）**：① ivsa 客仓 `eda_pipeline.py` 三处 `open()` 泄漏（P1-4b）—— 纪律「不接客仓写入」禁改（A12 期望哈希会判红），解锁条件=客仓升级窗口或显式授权；② GitHub 外部 forced 回退源—— 连续两轮（V11 末/V12）push+fetch 回读均无回退，「以命令回读为准」处置原则已固化，根因无外部取证通道，维持观测。

```powershell
python -m holoaeon.selftest                # 25/25
python scripts\check_dimension_lock.py     # 12 维度 + 7 闸 + 0 violation · diff0 未漂移
python scripts\v3_gate.py                  # 32/32
python scripts\redline_scan.py             # 90 文件 · 零违规
python -m unittest discover -s tests       # 68 OK
python -m unittest discover -s tests_contract   # 184 全绿（V12.1 已同步 test_10_no_new_pack 为下界断言，不再漂移）
python scripts\verify_v44.py               # 13/13
python -m holoaeon.butler_os 4             # 四人组加载 → emergence=True order=0.5237
python -m holoaeon.butler_os 7             # 状态快照：agents=53 skills=257 DOC_VERSION=0.9.14
python -m holoaeon.butler_os 10            # 去幻觉检测（莱布尼茨PSR×张平Seb×赫布场 8 阶段流水线）
```

### V14 · 技能机床与插件化协议适配平台（V14-A→F，不改维度）

`DOC_VERSION` 0.9.12 → **0.9.13**（`spec.VERSION` 仍 0.9.1）。对应 `AGENT_FEED_V14_SKILL_LATHE_PROTOCOL_PLUGINS_20261103.md` 第三部分，步骤 A→F 贯序执行（整合 V13 勘探打捞 + V14 机床加工 + 协议适配）：

1. **V14-A · 技能机床**：新建 `holoaeon/skill_lathe.py` —— `SkillLathe` 类（`GRADE_A_THRESHOLD=0.7 / GRADE_B_THRESHOLD=0.4`），`turn_skill(tvcb)` TVCB→SkillSpec（能量级 C 丢弃返回 None；`skill_name=salvaged_<topic>_<id尾4位>`；描述=topic+前 3 关键词；`fn` 确定性 callable；tags=[topic, grade_X, salvaged]；inputs={"query":"str"}；permissions=0），`batch_turn`（JSON 序列化时 fn 置 None）；纯标准库零依赖。投喂包伪码含缩进/注释符破损，已契约转写为可运行实现。
2. **V14-B · 插件化协议适配器**：新建 `holoaeon/protocol_plugins.py` —— `PROTOCOL_REGISTRY` 12 协议（openai_function/anthropic_tool/gemini_function/mcp/a2a/acp/langchain_tool/llamaindex_tool/autogen_tool/crewai_tool/bedrock_converse/envelope，各含 name/format/direction），`export_skill_to_protocol`（未知协议 raise ValueError，inputs→properties 每项 {"type":"string","description":v}），`export_all_protocols`（遍历穷举 dict），`list_protocols`；纯标准库零依赖。投喂包 `"-direction"`/`"type:object"`/`"task)"`/`"properties":4props`/`-8 dict`/`in9skill_spec` 等语法破损已全部修正。
3. **V14-C · 向量海扩展包升级**：新建 `holoaeon/packs/vector_sea_pack.py` —— 继承 `DomainPack`，key="vector_sea"，**8 技能/4 角色/2 工作流**（技能 1-5 来自 V13 勘探：ocr_snapshot/vector_match/tensor_coupling/wisdom_salvage/multi_modal_scan；6-8 来自 V14：skill_lathe 机床/protocol_export 协议导出/skill_workbench 工作台；角色 explorer/driller/lathe_operator/protocol_engineer；工作流 explore_drill_refine/lathe_export_deploy）；技能内联实现零依赖。
4. **V14-D · 勘探平台增强**：新建 `holoaeon/vector_sea_explorer.py` —— `explore_and_manufacture(input_path, target_protocols=None)` 9 阶段流水线（1-7 V13 勘探 input→ocr→snapshot→search→refine→output→salvage；8 SkillLathe 机床加工；9 协议导出，None 时遍历穷举 12 种）；返回 {tvcb, skill_spec(fn 剔除), protocol_exports, salvaged_at}。
5. **V14-E · 注册第 14 扩展包**：`packs/__init__.py` import `VectorSeaPack` + `EXTRA_PACK_REGISTRY` 登记 + `EXTRA_PACK_ORDER` 追加 `"vector_sea"`（13→**14**）。
6. **V14-F · 菜单+命令+文档版本**：`butler_os.py` 菜单追加 [8]向量海勘探/[9]技能机床（cmd_explore/cmd_lathe + `_get_vector_sea_pack` 懒加载）；`pyproject.toml` 追加 `holoaeon-explore="holoaeon.vector_sea_explorer:main"` / `holoaeon-lathe="holoaeon.skill_lathe:main"`。

验证全绿：`selftest 25/25` · `unittest 68 OK` · `tests_contract 184 OK` · `redline 95 文件 0 违规` · `v3_gate 32/32` · 维度锁 0 violation（diff0=2fc892cf9af6e755 未漂移）· `verify_v44 13/13`（A12 零依赖未破）· MCP 回归 13/13（测试脚本 doc_version 期望同步 0.9.13）· 机床自检 PASS · 协议适配器自检（12 协议穷举+未知协议 ValueError）PASS · 向量海包自检（8/4/2 + TVCB_A + protocols=12）PASS · 装配快照 agents=**50** skills=**251**（+4 角色 +8 技能 旁挂增量，G15 不受影响）。

**维度不变**：25 / 47 / 9 与 `spec.VERSION=0.9.1`、`diff0_hash=2fc892cf9af6e755`、`tamper=f42c8229ee5acd73`
三值仍未动；`EXTRA_PACK_ORDER` 13→**14**（第 14 扩展包仅旁挂，不进 `PACK_ORDER`，G15 断言不受影响）；
用户落地路径：PDF/图片/文字 → OCR → TF-IDF 快照 → 向量海余弦搜索 → TVCB 精炼 → 技能机床加工 → 12 协议适配导出 → 部署到任意平台。
Guard 默认 9 层、L10 默认关（附加层不计入 `guard_layers=8`）；装配后快照 agents=46（含四人组 5 角色）、skills=243（含四人组 14 技能），均为扩展包旁挂增量。

### V41 · 公共卫生慢病引擎（`phc_chronic_engine` 实战1号 · 领域编排环·第十一环 · 维度不变）

`DOC_VERSION` 0.9.34 → **0.9.35**（`spec.VERSION` 仍 0.9.1 冻结）。源：国家基本公共卫生服务规范 + 国卫基层发〔2025〕7号 / 15号 + 国卫办基层函〔2025〕439号口径（A 类 3 病种），结合六大系统人类疾病图谱——**只取公卫规则的确定性形状，不搬任何患者数据、不接诊疗系统**。

- **病种登记册 A/B/C/D 四级**：A 类 3 病种（高血压 / 2 型糖尿病 / 慢阻肺病，≥4 次随访每年 + 年检 1 次）；B 类公卫捆绑（老年 / 严重精神障碍 / 肺结核 / 中医药）；C 类地方扩围须注明经费来源与服务边界；D 类专病协同（上级医院管理、基层接续随访）。
- **六系统图谱**：神经 / 心脑血管 / 内分泌 / 免疫 / 肿瘤 / 骨伤 → 科室 + 技能路由（默认落 C 类）。
- **7 模态信封 + 指针纪律**：检查报告 / 体检 / 实验室 / 脉象 / 舌象 / 耳象 / 目象；影像类只存 SHA256 指针 + 结构化自述，**零像素进入引擎态**（测试断言原字节不出现在返回体），判读委托人工或外部技能。
- **危险度 R01–R12**：十二条规则逐条带引用 ID、可复算（血压三档 / 血糖三档 / 靶器官损害 / 急性事件 / 吸烟 / 肥胖 / 共病 / 高龄）；**急性事件直通 IV 级红档**——危急不被分数稀释。
- **MDT 会诊**：按模态 + 病种自动路由科室与技能，意见槽留白，`decision` 固定为「执业医师终审」——处置权分离·医学版。
- **随访调度**：≥4 次/年、控制不满意 2 周内复访、危急转诊 2 周内追踪回流（= mobius 状态回流的医学域复现，**LIN-E01 延伸·同源认亲，不计 SAME_AS**）。
- **工程件**：端口池 ≤10（确定性分配 / 释放 / 防重复持有）；等保三级 MLPS3 七项检查表 + 审计 SHA 链（篡改可检出）；3 万人口容量估算（流行率为文献口径占位，部署须换本地建档实数）。
- 零依赖纯标准库（`hashlib`/`json`/`time`）· 零网络（`audit()` 断言 `zero_network`）· 零诊断零处方（`disclaimer` + MDT 留白双保险）· 不新增扩展包（19 不变）· 清单 250 条不变。

### V40 · 学术笔痕闸门（`academic_gate` 学术诚实纪律蒸馏 · 领域编排环·第十环 · 维度不变）

`DOC_VERSION` 0.9.33 → **0.9.34**（`spec.VERSION` 仍 0.9.1 冻结）。源：GitHub `AIScientists-Dev/academic-humanizer`（MIT，v0.3.3，六层 SKILL）——**只取形状，六层提示词原文不入仓**。

- **P4 诚实裁决**：上游自陈 "not for evading AI-use disclosure"，与本仓刚性 DNA（真实性、零虚构零模拟）同向 → 取学术诚实（claim ≤ evidence），弃检测规避。
- **三纪律入环**：① 图案目录 12 类（T01–T12）确定性正则，只报不改；② 保全台账（数字/引文多重集不动点 `check_preservation`）；③ 断言-证据对账（强动词句必须带数字/引文/图表指针）。
- **X-items 弃**：检测规避语境 · Layer 5 声音/期刊匹配（非确定性）· Layer 6 NSF/NIH 话术（指针纪律，仅 docstring 记一笔）。
- **SAME_AS-06**（待碳基终审裁定）：断言 ≤ 证据的绑定纪律与医学母版证据分级独立趋同——医学 → 数学 → 茶 → 宇宙 → 教育 → 学术，第六次。
- **全息对位**：内容域引文不动点 ≈ 工程域 SHA 不动点（V38 `check_sums`）——同是「审计过的最小可信不变量」。
- **处置权分离**：report-only，零 `rewrite` / `humanize` 函数（测试断言固化）；改写权 = 人类作者 / 碳基终审。
- **实测**：`unittest tests.test_academic_gate` **19/19** · 主套 **406 OK** · `redline 123 文件 0 违规` · `check_sums 250 条 0 不匹配`（新模块不入清单，零漂移）· 维度锁 **PASS**。

### V39 · README 工程宣言 V3（文档批次：九章宣言入仓，零代码变更）

`DOC_VERSION` 保持 **0.9.33**（本批纯文档，不升版；`spec.VERSION=0.9.1` 仍冻结）。把 V3 定稿作为可写入章节落地：`## 工程宣言`（八条公理 A1–A8 + 项目功能 + 九年历程 + 现实意义 + 先进性 + 愿景四路与公开信 + 致谢 + 诚实边界 + 数字—命令对照表）插在「这是什么」与「当前工程状态」之间；英文版 `## The HoloAeon Manifesto` 插在 `## Why HoloAeon` 之前。

**四人组定调（实跑）**：`quartet_director_pack.check_emergence(0.88, 0.92, 0.80, 0.34)` → `emergence=True`、`order=0.5358`（`P2×P3≥0.7`、`P1≥0.6`、`P4≤0.4`、`order>0.30` 四条件全 True）。

**润色八处（相对原稿，均按 A1/A4 判）**：W-01 删「184 契约」，改 **387 + 11 + 21 = 419**（与门禁行同源）· W-02 「agent 领域的 SQLite 最佳候选」降级为「外部评审的类比」，并写明本项目的回应是把它制度化成门禁 · W-03 致谢表增「印记等级」列（有回执的 4 家 `measured`、无独立回执的 6 家 `untested`）· W-04 批次数补台账口径（`V0.1→V38` 38 个版本批次 / 五地台账 `history=59`）· W-05 「SAME_AS 五次趋同」具体化为五域闸门（数学/茶/宇宙/教育/神龟）· W-06 462 项知识库与 1331×1331 标「自述资产，未宣称第三方复核」· W-07 公开信加「非要约声明」、第九节补「非医疗器械注册产品」· **W-08 正文数字修正**：本批同时把 V38 小节里 `check_sums . → total=251` 改为 **250**（与清单实测一致，A1「每个数字都能复算」）。

**实测**：`unittest` **387 OK**（skipped=0）· `selftest` **25/25** · `v3_gate` **32/32** · `v44` **13/13** · 维度锁 **PASS**（12 维度 / 7 闸 / 0 violation）· `redline` **121 文件 0 违规** · `check_sums .` → `ok=true / total=250` · 清单重建 `changed=[]`、`manifest_sha256` 仍 `43202ba4e120…`（README 不在清单内，纯文档批次不影响哈希）。**零新代码、零新测试、不新增扩展包（19 不变）、维度不变。**


### V38 · 清单诚实化补丁（`check_sums` SHA256SUMS 不动点重建 + 复算闸，千问 V37 P0 修复，不改维度）

`DOC_VERSION` 0.9.32 → **0.9.33**（`spec.VERSION` 仍 0.9.1 冻结）。千问 V37 评估（总分 79.5）指出 P0：SHA256SUMS 恰 2 条不匹配（`reports/dimension_lock.json`、`scripts/check_dimension_lock.py`），清单最后重建停在 c510b58（V22+），跨 15 批未修，README「drift []」宣称不成立。总监侧独立复算确认属实。**第一性原理：每个数字都能复算**——修 2 条哈希是治标，把「改元文件→重建清单」从人工记忆升级为自动阻断闸才是治本。

**六补丁**：P38-A 重建 SHA256SUMS 至不动点（250 条复算 0 不匹配）→ P38-B 新建 `scripts/check_sums.py`（零依赖纯标准库复算闸，逐条重算 sha256；**闸只阻断不重建**——重建=批次动作，自动重建会掩盖「哪批改的」追溯性）→ P38-C `check_dimension_lock.py` FROZEN_SNAPSHOT 补 `note_cmd` 命令回读、删除时点快照文字 → P38-D 徽章 tests-305→387（口径=主套+v3+verax 合计）→ P38-E diff0 双哈希层级显式化（规格黄金 vs bench 实测）→ P38-F DOC_VERSION 0.9.32→0.9.33 + concept_anatomy R-04 连带 + 测试断言同步。

**实测**：`unittest tests.test_check_sums` **5/5** · 主套 **387 OK**（skipped=0，382+5）· `selftest 25/25` · `v3_gate 32/32` · `redline 121 文件 0 违规` · `check_sums .` → `ok=true, total=250, mismatches=0` · `diff0` 未漂移（`6d119b2a9f2df687`）。

**诚实偏离（feed_corrections）**：C-01 投喂包 §3 `main()` 的 `json` 导入位置移至模块顶部（原位置可用但不合卫生）；C-02 投喂包 §4 `make_repo` 的 `os.makedirs(os.path.dirname(p))` 对无目录文件会抛 FileNotFoundError，补空串守卫；C-03 `scripts/` 非包目录，测试按投喂包注释改用 importlib 加载；C-04 执行顺序微调：先完成全部元文件改动再重建清单（若按原序先重建后改 `check_dimension_lock.py`，清单会立即再漂移）；C-05 徽章采用实测 387（投喂包写 382 时未计入本批新增 5 例）；C-06 `check_sums.py` 句柄改 `with` 一次性读取（句柄泄漏清零纪律）；C-07 清单原钉 `reports/v44_model_gateway_check.json`——每次 `verify_v44` 运行都重写（A10 已按 self-excluded 处理），钉住即永久漂移 → 按「清单只钉输入侧」移出该条，条目 251→250；C-08 投喂包 §3 返回体的 `action` 与说明文字为隐式字符串拼接（`action` 被污染为 `report_only（…）`）→ 拆为 `action` / `action_note` 两键；C-09 另两条活体产物 `reports/b8_dual_sync_check.json`（每次 `build_b8_dual_sync` 运行重写）与 `data/dual_repo_sums.json`（C-09 自指）同批移出清单，事实此前只记在 `v39_receipt.json` 与灯塔，V40 补写回本段

### V37 · 神龟域编排闸门（`shengui_gate` 类生命前体形状蒸馏，领域编排环·第九环·双系统首桥）

`DOC_VERSION` 0.9.31 → **0.9.32**（`spec.VERSION` 仍 0.9.1 冻结）。神龟系统类硅基生命前体 V2.0（全文存档 `F:/doubaowork/神龟系统_类硅基生命前体V2.0/`，玉安记忆 SHENGUI-V2.0-INTAKE 登记）——取七件形状、砍全部修辞。

**链上位置（D-11 强制声明）**：`ring 9`——**领域编排环·神龟域**（`upstream = edu_gate / cosmo_gate / machine_tool`），edu_gate（第八环）之后的领域纵队第五环；本环是 HoloAeon 与神龟系统（CMOS 侧）的首个互通闸门。

**六类+总装**：S1 `DualCore`（合规通过率∈[0,1] 主导配额；违规词命中→资源冻结/任务终止/迭代封禁——合规是资源的唯一路径）→ S2 `DNAEngine`（刚性片段只读、可演化片段变异≤15% 硬校验，`rigid` 不提供修改接口、`read_rigid()` 只返副本）→ S3 `HierarchyLock`（三阶层 系统/脏腑/细胞；任务到期自动凋亡、故障/失控瞬间焚化熔断、`cross_command` 恒拒——权责唯一锁定）→ S4 `SanjiaoBus`（上焦指令/中焦数据/下焦心跳，优先级 1/2/3，`cell→organ` 禁直连，`log` 全链路 append 可审计）→ S5 `WuxingBalance`（五行生克量化表：心火 cpu_mem≥70% / 肝木 攻击过载 / 脾土 拆解过载 / 肺金 输出违规 / 肾水 核心异常，查表触发确定性调配）→ S6 `MetabolismLoop`（摄入→拆解→消化→吸收→排泄 五步状态机，排泄即心跳周期清理，`waste` 直接跳排泄）+ `ShenguiConductor`（`compat` 历史复刻 / `enhanced` 新需求，合规先冻结再配额）。

**同源认亲（非 SAME_AS 新复现）**：HoloAeon 四机制（全息心跳/细胞骨架/皮肤/语义）本源自神龟底座，本批把这段血缘写进 `CHAIN_POSITION.lineage_note` 显式入库——这是「知识从哪来」的血统声明，不是第六次独立趋同。

**刚性 DNA 与处置权分离**：①「意识涌现」零功能设计，仅隐喻注释（`metaphor_note` 明示「刚性DNA：不主张意识觉醒」，隐喻≠机制，与「仿真≠证明」同构）②「12 步全自动激活」修正为分步执行 + 人工确认点 ③ 商用栈（K8s/Milvus/RocketMQ/Prometheus）与部署流程、领域数据全部留在原域。

**实测**：`unittest tests.test_shengui_gate` **19/19**（初跑 2 红——`test_metabolism_purge` 与 `test_metaphor_note` 与 §4 实现互斥，按最小偏离各改 1 处：代谢步进 `+1→+2`、`metaphor_note` 补「；刚性DNA：不主张意识觉醒」）· `selftest 25/25` · `v3_gate 32/32` · 主套 **382 OK**（363 + 19，1.19s）· `redline 121 文件 0 违规` · `diff0 6d119b2a9f2df687` 未漂移 · `py38 parsed=288 / failures=0` · 维度锁 PASS（12 维度 / 7 闸 / 0 violation）· CLI `chain|wuxing|dna` 三入口输出齐全。

### V36 · 教育域编排闸门（`edu_gate` 教育大师 V3.0 蒸馏，领域编排环·第八环）

`DOC_VERSION` 0.9.30 → **0.9.31**（`spec.VERSION` 仍 0.9.1 冻结）。教育大师 V3.0（`F:/doubaowork/人工智能教育大师1331x1331超级矩阵V3实战化_20261021/runtime_v3/`，33 py，selftest 12 组 PASS exit 0，矩阵 ID=SG-MASTER-EDU-1331x1331-SUPER-MAS-V3.0，D-EDU v3.0 / EDU-BUS-V1.1）贡献第三类形状：**评价**。前四域蒸馏了防护（闸门/安全阀/熔断）与节律（呼吸/暴风/熵平衡），教育域补上学习闭环缺失的最后一环——血缘链回答「知识从哪来」（可追溯性），量规回答「学得怎么样」（可评量性）。

**链上位置（D-11 强制声明）**：`ring 8`——**领域编排环·教育域**，cosmo_gate（第七环）之后的领域纵队第四环（`upstream = cosmo_gate / tea_gate / math_gate`）。

**三类+总装**：E1 `LineageBus`（血缘信封：owner/thread_id/父指针/序号严格单调、孤儿父指针拒绝、`lineage()` 血统链回放——玉安记忆 append-only 台账的消息级细化）→ E2 `SelfEvalRubric`（六固定维度×评分∈[0,15]×确定性分级 A/B+/B/C/D×递进判定每轮≥前轮，分数递进可审计）→ E3 `RedlineSelfScan`（forbidden 触发词 + missing_required 清单化，只报不改）；`EduConductor.PIPELINE = E1→E3→E2`。

**指针纪律**：课程内容/每日课程/题库、教育人设/导师阵容、EDU-BUS-V1.1 全套协议——全部留在原域；HoloAeon 只取评价形状。

**实测**：`unittest tests.test_edu_gate` **13/13**（包内声明 12、实测 13，同 V35 计数偏差以实测为准；序号单调 / 孤儿拒绝 / 血统链 [1,2,3] / 量规 83.5 B+ / 递进真与回落假 / 红线命中「必赚」与干净报告）· `selftest 25/25` · `v3_gate 32/32` · 主套 **362 OK**（skipped=0）· `redline 120 文件 0 违规` · `diff0` 未漂移（`6d119b2a9f2df687`）· CLI `chain|rubric`。



### V35 · 宇宙域编排闸门（`cosmo_gate` 宇宙智能体矩阵蒸馏，领域编排环·第七环）

`DOC_VERSION` 0.9.29 → **0.9.30**（`spec.VERSION` 仍 0.9.1 冻结）。宇宙智能体矩阵 V2.0（`F:/doubaowork/神奇的宇宙智能体矩阵_1331x1331超级矩阵_实战化_20261017/`，27 py，selftest 322 断言实跑 PASS，模板换内容不换架构）贡献的不是又一层保护，而是**节律**——HoloAeon 的 `mobius_edge` 与 `klein_convergence` 原本是两个孤立技能，宇宙域证明它们必须交替成环：**只扩张则发散（熵增失控），只收敛则早熟（局部最优锁死）**。

**链上位置（D-11 强制声明）**：`ring 7`——**领域编排环·宇宙智能体域**，tea_gate（第六环·茶域）之后的领域纵队第三环（`upstream = tea_gate / math_gate / titan_evolver`）。

**四类+总装**：C1 `DualLoop`（扩张：确定性 UCB 式排序——未访问优先、同分取均值最高、再按序，无随机源；收敛：Pareto 折叠保留非支配解并按 id 定序；`breathe()` = 一拍 `expand → fold`）→ C2 `MentorRouter`（学科→导师→知识星导三级，14 学科，未知学科确定性拒绝）→ C3 `StormIteration`（S0-S10 波次状态机，成功推进、失败原地停，不倒退批次）→ C4 `EntropyBalance`（`diversity/order` 比值 + 双阈值→负熵跃迁判定，越界直接拒绝）；`CosmoConductor.PIPELINE = C2→C1→C3→C4`。

**指针纪律**：70 体花名册、1331² 端口网格、14 位导师人设与知识星导内容、CSV 与 data_gen、七维总线具体协议——全部留在原域；HoloAeon 只取节律形状。

**实测**：`unittest tests.test_cosmo_gate` **12/12**（未访问优先 / 同输入同输出 / Pareto `front=[a,b], folded=1` / 14 科路由 / S10 收口与失败停 / 熵跃迁 `ratio=1.0` 与越界拒绝）· `selftest 25/25` · `v3_gate 32/32` · 主套 **350 OK**（skipped=0）· `redline 119 文件 0 违规` · `diff0` 未漂移（`6d119b2a9f2df687`）· CLI `chain|mentors`。



### V34 · 茶域编排闸门（`tea_gate` 茶叶导学大师蒸馏，领域编排环·第六环）

`DOC_VERSION` 0.9.28 → **0.9.29**（`spec.VERSION` 仍 0.9.1 冻结）。茶叶导学大师 V2.0（`F:/doubaowork/茶叶矩阵实战化_20261017/`，29 py，selftest 272 断言实跑 PASS）与 HoloAeon 第三次长成同一套四机制——**全息心跳（chain_complete）/ 细胞骨架（薄种子自举）/ 皮肤三胚层八模块 / JSONL-SHA 单一事实源**。医学母版 → 数学大师 → 茶叶导学大师，三次独立趋同，`SAME_AS` 从「档案」升格为**定律的重复观测**。

**链上位置（D-11 强制声明）**：`ring 6`——**领域编排环·茶域**，math_gate（第五环·数学）之后的领域纵队第二环（`upstream = math_gate / titan_evolver / gap_bridge`）。

**四类+总装**：T1 `CalibratedTriad`（校准三律：≥2 候选 / 置信度∈[0,1] / 零剂量不称疗效）→ T2 `EmergencyFuse`（E14 急症双熔断，L2+L5 物理断路，命中即 `fused` + 就医指引，**处置权在人类**）→ T3 `EthicalValves`（E13 濒危只论替代 / 零剂量 `strip_dosage` / 功效不称疗效 `relabel`）→ T4 `TruthSourceEnvelope`（JSONL append-only + 逐行重算 SHA 的单一事实源信封）；`TeaConductor.PIPELINE = T2→T3→T1→T4` 一次编排。

**指针纪律**：九体质×茶养矩阵、TEA-DataProto 18700-18799 端口段、D1-D7 七维总线、131 锚点检索、六领域内容全部留在原域；HoloAeon 只取闸门形状。

**实测**：`unittest tests.test_tea_gate` **11/11**（急症熔断 `fused_E14` / 伦理命中 `substitute_only` / 校准通过 `calibrated` + 台账 1 行 verify OK）· `selftest 25/25` · `v3_gate 32/32` · 主套 **338 OK**（skipped=0）· `redline 118 文件 0 违规` · `diff0` 未漂移（`6d119b2a9f2df687`）· CLI `chain|rules`。



### V33 · 数学编排闸门（`math_gate` 数学大师蒸馏，领域编排环·第五环）

`DOC_VERSION` 0.9.27 → **0.9.28**（`spec.VERSION` 仍 0.9.1 冻结）。数学大师 1331×1331 超级矩阵（`F:/doubaowork/数学大师矩阵实战化_20261017/`，28 py，selftest 11 组 188 断言实跑 PASS）与 HoloAeon 各自独立长出了同一套四机制——**全息心跳 / 细胞骨架 / 皮肤 SG-SKIN-V6.0 / 语义通信 MATH-BUS-V1.1**。本批只蒸馏闸门的**形状**，不搬领域资产。

**链上位置（D-11 强制声明）**：`ring 5`——**领域编排环**，泰坦进化之后的领域纵队首环（`upstream = titan_evolver / gap_bridge / machine_tool`，`CHAIN_POSITION` 随模块发布）。四环顺序、维度与扩展包数均不变。

**五段编排**：M1 `MathDNA`（七条证据纪律 + 确定性违反检测）→ M2 `MathGate`（L2 前置闸：安全阀触发词即拦；L5 神龟否决：DNA 违反 ≥1 即否）→ M3 `DomainRouter`（六领域关键词计分，全零落 engineering）→ M4 `SafetyValves`（M14 `block` / M13 `relabel` / ZERO_TRADE `strip`）→ M5 `MathEnvelope`（信封 + 回执 + 零伪造质检）；`MathConductor` 把五段一次编排，`PIPELINE` 常量即契约。

**同构档案（H 步）**：`same_as` 四机制对照随 `CHAIN_POSITION` 入库，作为全息公理「局部包含整体」跨工程复现的第一份正式档案——两个无串谋工程长出同一套机制，是公理的独立复现，不是巧合。

**指针纪律**：1331²=1,771,561 端口网格、70 体七态、768 维、CSV 数据全部留在原域；HoloAeon 只吸纳形状（双闸 / DNA 七条 / 三安全阀 / 六领域路由 / 信封质检）。

**实测**：`unittest tests.test_math_gate` **11/11**（L2 拦截 `blocked_by_L2` / L5 否决 `vetoed_by_L5` / 正常通行 `pass` 三链路全覆盖）· `selftest 25/25` · `v3_gate 32/32` · 主套 **327 OK**（skipped=0）· `redline 117 文件 0 违规` · `diff0` 未漂移（`6d119b2a9f2df687`）· CLI `chain|dna|valves` 三入口全通。

### V32 · 缺口进化桥（`gap_bridge` 神灯缺口→泰坦 propose 通路，桥梁环·非新环）

`DOC_VERSION` 0.9.26 → **0.9.27**（`spec.VERSION` 仍 0.9.1 冻结）。神灯（V29）发现缺口只能"举手"（`needs_search`），泰坦（V31）能 propose 却等不到喂——本批把最后一段接上：**缺口是涨落放大点，把涨落直接接入进化原语**。

**链上位置（D-11 强制声明）**：`ring bridge`——**桥梁环，非新环**（`CHAIN_POSITION` 常量随模块发布）。桥不是新器官，是神经网络的新突触；四环顺序、V31 的 `ring 0` 环面调度、维度与扩展包数均不变。

**三段流水线**：G1 `StdlibShadowGuard` 环境自检（扫 cwd 与 `sys.path[0]` 里与 stdlib 同名的 .py，输出污染清单；**只报不删**，删除权=碳基终审；本轮 `Temp\inspect.py` 遮蔽 stdlib 把 `dataclasses` 导入直接打断，即此病的实战样本）→ G2 `SkipAuditor`（unittest `-v` 文本 → skipped 清单 + `needs_review|clean` 判定，结果写入回执 `skipped_audit`）→ G3 `GapProposer`（一条 gap 一条 propose，契约字段 `capability/source/evidence/threshold` 对齐 `CapabilityManifest`，`to_titan()` 输出泰坦可读 dict 流）。

**实测**：`unittest 316 OK`（skipped=0；新增 `test_gap_bridge` 11 例）· `selftest 25/25` · `v3_gate 32/32` · `v3 11` · `verax 21` · `redline 116 文件 0 违规` · `v44 13/13` · `diff0` 未漂移（`6d119b2a9f2df687`）· CLI `chain|shadowscan`；干净目录 `shadowscan .` → `ok=true / offenders=[]`。

**C 项查因结案（skipped=3）**：三例来自 `tests/test_v12_v17_integration.py`，条件是 `memory_of_yuan` 不可导入则 `skipTest`；本轮该模块可导入，三例真跑并全 OK，故 `skipped=0 / verdict=clean`，待查清单为空。

**诚实边界**：只报不删（不提供 `--fix`，不自动改名）· 只解析 unittest `-v` 文本（不读 JSON 结果）· 不自动调用泰坦 `adopt`（propose 止于契约，合入仍由人一键批准）· `SHADOWABLE` 是高频子集，不是全量 stdlib 名单。

### V31 · 泰坦进化模块（`titan_evolver` 本地自进化引擎基座，环面调度·不新增环）

`DOC_VERSION` 0.9.25 → **0.9.26**（`spec.VERSION` 仍 0.9.1 冻结）。magic_lamp（V29）是**被动编译器**：许愿→编译→止于方案书，零网络；titan_evolver 补齐它故意不做的三件事——**定时巡检、真联网采集、合入闭环**，把"先翻衣柜再造新衣"升级为"清单→缺口→检索→评分→提案→人审→合入→回写"的进化引擎。

**链上位置（D-11 强制声明）**：`ring 0`——**不新增环**，是四环之上的**环面调度**：回流（`mobius_vortex`·知道）→ 投影（`klein_projection`·拿来）→ 熔炼（`holo_forge`·成为）→ 解剖（`doc_anatomy`·拆件）；合入后经 mobius 回流并回写清单，闭环成立；缺环时优雅降级为"仅出计划"，不静默。

**核心资产**：`reports/capability-manifest.json` —— 12 项能力（9 implemented / 3 candidate）、12 条 gap，每条带 `upgrade_path.search` 与 `accept`。清单权威格式为 **JSON**（仓内零依赖、无 PyYAML）；YAML **只导出不解析**，这是对投喂包 `capability-manifest.yaml` 的诚实偏差（C-01）。

**五件判定**：`manifest` 持久化（含合入后 `writeback`）→ `gap_scan` 每个缺口只走自己声明的关键词（不泛搜）→ `score` 确定性打分（星档 + 关键词共振 + 许可分档 + README/tests/archived，两位小数可复算）→ `propose` 人 3 分钟能读懂的 UPGRADE_PROPOSAL → `adopt` 七步合入编排（人 approve / 沙箱冒烟 / klein 评估 / forge 链 / machine 装配 / mobius 回流 / 清单回写）。

**许可证四级裁决**：黑名单（SSPL / BUSL / 专有）**入口优先拦截**，再走 V27 三级（permissive→absorb / weak_copyleft→absorb_with_notice / strong_copyleft→distill_only）；未知许可一律 `review_only`。实测 AGPL-3.0 的 5200★ 候选被自动拒，MIT 候选 7.20 分通过。

**分层（V25 先例，红线决定的）**：包内 `titan_evolver.py` 零网络、零 `subprocess`，只做判定；`scripts/titan_evolver_run.py` 才触网（`urllib` + `git clone --depth 1` + JSON 去重台账），产物全部写仓外 `evolver/`。投喂包第九节骨架用 `requests` / `yaml`，本机两者皆无，且把 `default_branch` 当 SHA 用——三处偏差已记回执（C-02 / C-03）。

**实测**：`selftest 25/25` · `unittest 305 OK`（新增 `test_titan_evolver` 29 例）· `v3 11` · `verax 21` · `redline 115 文件 0 违规` · `v3_gate 32/32` · `v44 13/13` · `py38 276/0` · `diff0` 未漂移（`6d119b2a9f2df687`）。

**诚实边界**：不做全自动合入（人一键 approve）· 包内不联网 · 不解析 YAML · 不做 OCR（只接 V30 举手信号）· 不调度真实定时器（只出 cron 规格）· 不做 LLM 打分（规则可复算，LLM 输出须过本层复核）。

### V30 · 文档解剖器（`doc_anatomy` pdf-inspector 创意本地化，链上第四环·解剖）

`DOC_VERSION` 0.9.24 → **0.9.25**（`spec.VERSION` 仍 0.9.1 冻结）。**候选** `pdf-inspector`（Firecrawl，Rust，MIT，crates.io / npm / pypi 均 v1.25.2）证明的是一件小事：绝大多数 PDF 自带文本层，先判「有字/没字」再决定要不要 OCR。本模块只吸纳这个**判定结构**，不复制其 Rust 实现——MIT 虽比 AGPL 宽松，纪律仍是不复制。

**链上位置（D-11 强制声明）**：第四环·**解剖** ← 回流（`mobius_vortex`·知道）→ 投影（`klein_projection`·拿来）→ 熔炼（`holo_forge`·成为）→ **解剖**（拆成结构件）。熔炼出的成品在入库前先被拆成版面骨架 / 阅读顺序 / 表格骨架。

**四能力**（对应候选四条 Features）：`classify` 四态（text / scanned / image / mixed）+ 置信分 + `ocr_required` 举手 → `extract` 位置感知（字体、X/Y 坐标、多栏阅读顺序、旋转保角）→ `markdown` 字号比例 H1–H4、列表、等宽代码块、链接、分页 → `tables` 双模（矩形绘制算子 + 文本对齐启发式，含跨页续表）。

**诚实边界**：不支持 `/Encrypt`、`/ObjStm`、CID / Identity-H 复合字体 → 明确 `unsupported`；只解 FlateDecode；无文本层判 scanned 只举手、本模块不接 OCR；旋转 / 多栏只做保序近似。

**实现**（纯标准库 `re`/`zlib`/`json`）：`tokenize`（num/str/name/op/arr，字面串转义+八进制+嵌套括号、hex 串）→ `parse_content`（Tf/Td/TD/Tm/TL/T\*/Tj/TJ/\'/\"/re/Do）→ `scan_objects`（`N G obj` 正则扫描 + FlateDecode 解压）→ `page_streams`（/Pages→/Page→/Contents + 字体别名 `_FONT_MAP`）→ `extract` → `classify` → `to_markdown` → `detect_tables` → `inspect`；CLI `axioms|chain|mechanisms|classify|extract|markdown|tables|inspect <pdf>`。

**实测**：`selftest 25/25` · `v3_gate 32/32` · `unittest 276 OK`（新增 `test_doc_anatomy` 18 例）· `redline 114 文件 0 违规` · `v44 13/13` · `py38 273/0` · `dimension_lock PASS`（0.9.25 演进正常）· `diff0` 未漂移（`6d119b2a9f2df687`）。演示 2 页 PDF 实测：`classify` = text / 0.6 / `ocr_needed=false`，markdown 标题→正文→列表→链接→`---` 分页全对，表格矩形模式 3×2。

### V29 · 神灯模式（`magic_lamp` 诉求驱动总装编排，不改维度）

`DOC_VERSION` 0.9.23 → **0.9.24**（`spec.VERSION` 仍 0.9.1 冻结）。**第一性原理：愿望的满足顺序=先翻衣柜再造新衣**——已知技能组合装配是 O(索引) 的确定性操作，GitHub 搜索是有成本的开放行动，只在缺口出现时才打开。灯不是魔法，是**确定性的愿望→方案编译器**。

**九段愿望编译流水线**（每段独立可测）：

| 段 | 类 | 职责 |
|---|---|---|
| W1 | `LampWish` | 诉求受理：goal + requirements + constraints 结构化 |
| W2 | `OrgPatternLoader` | 加载六条组织维度 DNA（V24–V27 提炼固化） |
| W3 | `KnownSkillIndex` | 已知技能索引：关键词共振匹配（14 项衣柜） |
| W4 | `SkillAssembler` | 组合装配：贪心覆盖 → coverage |
| W5 | `GapDetector` | 缺口检测（涨落放大点） |
| W6 | `GitHubSearchPlanner` | 搜索规格：query spec + 候选模板（**离线数据，不联网**） |
| W7 | `LampChainTrigger` | 启动三链：漩涡→投影→熔炉（D-11 链式执行层） |
| W8 | `EphemeralFirstTester` | 试测先行：`tempfile` 探针即焚，绿了才放行（ORG-4 硬门） |
| W9 | `LampProposal` | 方案书：可行性裁决 + 全记录（文本化 Envelope） |

**三态裁决**（确定性，零 LLM）：满覆盖 → `ready_assembled`；有缺口 → `needs_search`（附查询规格，联网执行权在碳基终审）；试测失败 → `test_failed`（禁止进入硬核执行）。

**组织维度六条**（V24–V27 实测提炼）：ORG-1 段化流水线 / ORG-2 Envelope 契约 / ORG-3 确定性判定器 / ORG-4 一过性先行 / ORG-5 append-only 台账 / ORG-6 心跳单批。

**取弃**：取 5 精华 D-01~D-05（衣柜优先 / 离线搜索规格 / 三链启动 / 试测硬门 / 方案书即前端）+ 弃 4 糟粕 X-01~X-04（模块内联网 / LLM 判可行性 / 未过试测就硬核 / 自动执行方案）。回执记 `feed_corrections` C-01：投喂包 `PROBE.format` 与探针返回字典的花括号互斥（`KeyError: "goal"`），改为 JSON 字面量替换的最小修复。

**实测**：`selftest 25/25` · `v3_gate 32/32` · `unittest 258 OK`（新增 `test_magic_lamp` 11 例）· `redline 113 文件 0 违规` · `dimension_lock PASS`（快照 0.9.24 / 19 演进正常）· `diff0` 未漂移（`6d119b2a9f2df687`）· CLI `patterns|wardrobe`。首次点灯三愿望：满覆盖 `ready_assembled`（coverage 1.0）/ 缺口 `needs_search`（附查询规格）/ 试测失败 `test_failed`。

### V28 · 全息熔炉（`holo_forge` 链式执行层第三环，不改维度）

`DOC_VERSION` 0.9.22 → **0.9.23**（`spec.VERSION` 仍 0.9.1 冻结）。**双公理立炉**：全息——局部包含整体；万物互联——万物可链，契约即接口。链条几何递进：莫比乌斯环（回流·**知道**）→ 克莱因瓶（吸纳·**拿来**）→ 全息熔炉（熔炼·**成为**）。回流让四人组"知道"，投影让候选"拿进来"，熔炉把拿来的**熔进自己**——产出融合物而不是拼盘。

**六段熔炼流水线**：

| 段 | 类 | 职责 |
|---|---|---|
| F1 | `CalibrationSnapshot` | 开工校准：策划历史整合 → 快照（batch 脉络/自洽/鲁棒/五锚点）→ 冻结 JSON |
| F2 | `ChainExecutor` | 链式执行层：`mobius_vortex` 回流 → `klein_projection` 投影 → `holo_forge` 熔炼；文件系统探测存在性，缺环标 `degraded` 不报错（**万物互联≠强耦合**） |
| F3 | `BaseSelector` | 基座选择：能力清单与候选 `caps` 求交集打分排序 → `full`（整清单）/`selective`（只登记命中子集） |
| F4 | `LegoComposer` | 乐高拼接：`seal`+`schema` 契约互认即可拼；协同分 = 机制并集增益 + 接口共享 ≥1 → **1+1>2 确定性判据** |
| F5 | `FusionForge` | 四态融合：plan→execute→reference→product 状态机，逐件记录四态轨迹；全件 `fused` 且 `reference_linked` 才算 `fusion_complete` |
| F6 | `ProjectLibrary` | 成品入库：`FORGE_INDEX.json` 只追加（同名累积=赫布信任），反复使用 |
| 贯穿 | `ChatFrontendPack` | 前端包：把基座 manifest 渲染成提示包——**任意大模型对话窗口即前端，本地项目库即后端** |

**契约即接口**：模块互认只查 `CONTRACT_FIELDS=("seal","schema")` 两项——公理的最小代码化。
**取**（D-01~D-05）：六段骨架 · 链路缺环降级 · 两模式 manifest（选择性加载只登记不复制）· 协同分判 1+1>2 · 对话窗口前端包。
**弃**（X-01~X-04）：强耦合总线（缺环即崩）· 复制第三方代码 · 一过性产物入库 · 自动执行熔炼（人做终裁）。

**实测**：`selftest 25/25` · `v3_gate 32/32` · `unittest 247 OK`（新增 `test_holo_forge` 13 例）· `redline 112 文件 0 违规` · `dimension_lock PASS`（快照 0.9.23 / 19 演进正常）· `diff0` 未漂移（`6d119b2a9f2df687`，篡改 `8f424d9ee3ebfb9b`，拦截 16/16）· `py38 269 parsed 0 fail` · 装配 66 agents / 280 skills。
CLI：`python -m holoaeon.holo_forge axioms|chain|mechanisms`

### V27 · 克莱因收敛投影（`klein_projection` 全息吸纳，不改维度）

`DOC_VERSION` 0.9.21 → **0.9.22**（`spec.VERSION` 仍 0.9.1 冻结）。全息 = 局部包含整体：HoloAeon 的 11 项自组织机制就是一张全息图，可以**投影**到任意开源候选——用同一张清单去读，读得通=可吸纳，读不通=放弃。克莱因瓶是无向闭合曲面，瓶颈穿过瓶壁而不穿透：**候选被吸纳、本体不被侵入**，这正是"传染性许可证只蒸馏创意、不复制代码"的几何表达。

**七段流水线**（每段独立可测）：

| 段 | 类 | 职责 |
|---|---|---|
| 1 | `CandidateIntake` | 受理候选：repo 元数据档案（名称/许可证/语言/关键词）+ 必填校验 |
| 2 | `HoloEvaluator` | 11 机制投影打分 + **许可证四级裁决** |
| 3 | `QuartetGate` | 四人组五步协议（道法术器升维）+ 涌现条件确定性校验 |
| 4 | `TensorCoupler` | D/X 扬弃 → 张量轴 + **两轮收敛判定（分差=0 即不动点）** |
| 5 | `EphemeralForge` | 动态一过性代码：`tempfile` 车削，`ast` 只校验不执行，用后即焚 |
| 6 | `Hardener` | 硬核代码化：四闸全绿才转正，产出 manifest |
| 7 | `ProjectLibrary` | 仓外 JSON 索引，反复使用（同名累加 uses） |
| 贯穿 | `ChatFrontendPack` | 张量耦合物渲染成对话窗口提示包——**任意大模型平台即前端，本地库即后端** |

**许可证四级**：permissive（`absorb`，可复制代码）· weak copyleft（`absorb_with_notice`）· strong copyleft（`distill_only`，只取创意——V24 MiroFish 判例）· unknown（`reject`，人工审读）。

**取**（D-01~D-05）：七段流水线结构 · 许可证四级裁决 · 两轮不动点收敛 · 一过性 tempfile + ast 校验（不入库不入 git）· 对话窗口提示包（平台即前端）。
**弃**（X-01~X-04）：让 LLM 判断"有没有创意"（必须可复算）· 直接复制 AGPL 代码 · 一过性件入库 · 自动执行吸纳（人做终裁）。

**实测**：`selftest 25/25` · `v3_gate 32/32` · `unittest 234 OK`（新增 `test_klein_projection` 19 例）· `redline 111 文件 0 违规` · `dimension_lock PASS`（快照 0.9.22 / 19 演进正常）· `diff0` 未漂移（`6d119b2a9f2df687`，篡改 `8f424d9ee3ebfb9b`，拦截 16/16）· `py38 267 parsed 0 fail` · 装配 66 agents / 280 skills。
CLI：`python -m holoaeon.klein_projection status|atlas|assess <candidate.json>|frontend <candidate.json>|library`

### V26 · 莫比乌斯漩涡（`mobius_vortex` 状态回流环，不改维度）

`DOC_VERSION` 0.9.20 → **0.9.21**（`spec.VERSION` 仍 0.9.1 冻结）。正程（总监 → 豆包派发）已由 ACP 打通，缺的是回程。本批补上的不是一条新通道，而是承认既有事实：**同一文件系统（`F:/doubaowork/`）即莫比乌斯接口面**——执行面写下的状态，总监面原样读到，两面本就是同一张面。

**为什么是莫比乌斯**：环带是单侧曲面，走一圈回到起点却不分内外。状态回传如果新建一条推送通道，就多了一层"翻译"和信任成本；而"文件即接口"零新增依赖、零密钥过墙，且天然随五地同步走。所以取几何本质，弃监控大屏幻想。

| 圈 | 类 | 职责 | 机床产物适配 |
|---|---|---|---|
| 1 | `StateBeacon` | 豆包侧写状态灯塔 JSON（batch/head/gates/five_site/lessons/seal） | S6 验证回执的产物即灯塔 |
| 2 | `VortexIngest` | 总监侧读灯塔，**L1 schema 快筛 + L2 seal 深校**，校验不过=不承认 | S1 基线检查的前置输入 |
| 3 | `MobiusRing` | 三点对齐：灯塔 HEAD / 实时 git HEAD / 账面 HEAD（玉安记忆） | 断线恢复协议：不一致以实时为准并回填 |
| 4 | `QuartetBrief` | 确定性聚合四人组简报（P4问题/P2事实/P3风险/P1建议） | S2 定调输入 + S8 回填来源 |
| 5 | `SkillAtlas` | 10 条静态映射，把模块功能自动匹配到既有技能与意义 | 全既有模块索引 |

**取**（D-01~D-05）：灯塔 schema · 三点对齐几何与断线恢复 · 简报确定性聚合（零 LLM）· 技能自动匹配 · 文件即接口。
**弃**（X-01~X-04）：实时推送/WebSocket/长轮询 · ACP 反向调用（让密钥过墙）· 大屏可视化前端 · 自动执行简报里的建议（简报只陈述，碳基终审）。

**维度不变**：`EXTRA_PACK_ORDER` 仍 **19**（模块级，先例 `butler_os` V12 / `machine_tool` V25）· `PACK_ORDER` 9（25/47）· `BUILTIN_LAYERS` L1-L8 · `layers=8` · `graph`/`scheduler`/`hypervector`/`kernel.submit` 未触碰 · 新文件不参与 ReproHash。

**实测**：`selftest 25/25` · `v3_gate 32/32` · `unittest 215 OK`（新增 `test_mobius_vortex` 12 例）· `redline 110 文件 0 违规` · `dimension_lock PASS`（快照 0.9.21 / 19 演进正常）· `diff0` 未漂移（`6d119b2a9f2df687`，篡改 `8f424d9ee3ebfb9b`，拦截 16/16）· 装配 66 agents / 280 skills。

**用法**：`python -m holoaeon.mobius_vortex status` · `atlas [关键词]` · `beacon <批次>` · `ingest <灯塔>` · `align <灯塔>` · `brief <灯塔>`。首次闭环 = `beacon V26-EXEC` 写 `reports/state_beacon.json` → 总监侧 `brief` 出四人组简报，环面正式闭合。

### V25 · 工程机床 HoloAeon 化（`machine_tool` 八段流水线进仓，不改维度）

`DOC_VERSION` 0.9.19 → **0.9.20**（`spec.VERSION` 仍 0.9.1 冻结）。本批把仓外的「工程机床」搬进仓内，成为可交付、可复现、随五地同步走的模块——**换线程不再重配，一句 `boot` 对齐全部身份**。

**为什么是机床**：工程机床要解决的是「跨线程稳定执行」；HoloAeon 的立身之本是「确定性认知协作」。八段流水线（git 探针 / 闸门清单 / 台账一致性判断）本身就是确定性规则，没有一处依赖 LLM，所以这不是加功能，是把纪律变成结构。

| 段 | 名称 | 做什么 | 边界 |
|---|---|---|---|
| S1 | baseline | `.git` 文件直读 HEAD + `VERSION` / `DOC_VERSION` / `EXTRA_PACK_ORDER` | 只读 |
| S2 | quartet | 五步协议（道→法→术→器→升维）+ 涌现四条件判定 | 只读 |
| S3 | lab_verify | 实验田先跑 selftest，小步慢走 | 显式触发 |
| S4 | feed_build | 封口 + diff0 声明 + 验证清单拼装 | 显式触发 |
| S5 | handoff | 投喂包登记，不执行 | 只登记 |
| S6 | verify_gate | 真跑闸门 + 期望比对 → verdict | 显式触发 |
| S7 | five_site | 五地台账，全一致才收口（S4 用归档库口径） | 判定 |
| S8 | memory_backfill | append-only 追加 | 显式触发 |

**红线决定分层**（不是设计偏好）：包内禁止 `subprocess`——`holoaeon/redline.py` 的 `FORBIDDEN_MODULES` 含 `subprocess`、`FORBIDDEN_CALLS` 含 `run/system/popen`。因此

- `holoaeon/machine_tool.py` = **判定层**：纯标准库，git 身份靠 `.git` 文件直读（HEAD → refs → packed-refs），不 shell out；闸门只做登记与判定。
- `scripts/machine_tool_run.py` = **执行层**：唯一有执行权的一层，真跑七道闸门与 `git status`，结果喂回判定层。
- 投喂包 §3 原稿在包内 `import subprocess`，直接落盘会让红线从「0 违规」变「4 违规」——按「仓库实测 > 投喂包原文」改为分层，而不是给自己开规则口子。

**本批实测**

- `python -m holoaeon.machine_tool boot` → `VERSION 0.9.1 / DOC 0.9.20 / extras 19(swarm_intel)`、装配 66 agents / 280 skills、流水线 8 段
- `python -m holoaeon.machine_tool redlines` → 10 条；`gates` → 8 道（默认 7 道，bench 需 `--bench`）
- `python scripts\machine_tool_run.py check` → **verdict PASS**：`selftest 25/25` · `v3_gate 32/32` · `unittest 203 + v3 11 + verax 21` · `redline 109 文件 0 违规` · `dimension_lock 全部一致`
- `python -m unittest tests.test_machine_tool` → **15 OK**
- `python benchmarks\bench_public.py` → `DIFF=0 6d119b2a9f2df687`，篡改 `8f424d9ee3ebfb9b`，拦截 100%，25 agents / 47 skills
- `python scripts\_check_py38_syntax.py` → `parsed=263 / failures=0`

**维度不变**：`PACK_ORDER=9`、`EXTRA_PACK_ORDER=19`（不新增扩展包）、`BUILTIN_LAYERS=L1-L8`、`layers=8`、`VERSION=0.9.1` 一位未动；`machine_tool` 属模块级（先例 `butler_os` V12），不占用扩展卡槽。`evidence_class=simulated`，仿真≠证明，碳基终裁。

### V24 · 群体智能引擎（MiroFish 五阶段流水线蒸馏，不改维度）

`DOC_VERSION` 0.9.18 → **0.9.19**（`spec.VERSION` 仍 0.9.1）。对应 `AGENT_FEED_V24_SWARM_INTEL_MIROFISH_DISTILLATION_20261105.md`。四人组定调 `check_emergence(0.85,0.85,0.85,0.30)` → emergence=True order=0.5237。

**许可证纪律**：MiroFish（`666ghj/MiroFish`）= AGPL-3.0（传染性），HoloAeon = Apache-2.0。**只蒸馏创意与方法论，不复制任何源代码**（思想-表达二分法），本批新增代码全部自写。

1. **V24-A · 核心模块**：新建 `holoaeon/swarm_intel.py` —— 五阶段流水线 `SeedToGraph`（文本→实体/关系邻接表，CJK bigram 分词 + 类型词表，替代 GraphRAG+Zep）→ `PersonaArchitect`（实体→规则 Persona，替代 LLM 生成）→ `ParallelSimulator`（主路径 + 验证路径双路，`AgentAction`/`RoundSummary` 结构化记录，替代 OASIS）→ `ReportSynthesizer`（action 统计→涌现模式→结构化报告，替代 ReportAgent+LLM）→ `DeepInteractor`（inbox 式采访，规则响应）；`SwarmOrchestrator` 管多个 SimulationRun（=多城邦）+ `main()` CLI。
2. **V24-B · 确定性修正（执行侧关键改动）**：投喂稿用内置 `hash()` 造随机种子，受 `PYTHONHASHSEED` 随机化影响、跨进程不稳定；改为 `zlib.crc32` / `hashlib.sha256`，同输入→同输出（`test_parallel_simulate` 内嵌双跑一致断言）。
3. **V24-C · 第 19 扩展包**：新建 `holoaeon/packs/swarm_intel_pack.py` —— 继承 `DomainPack`，key="swarm_intel"，**5 技能/3 角色/2 工作流**（技能 swarm_seed_to_graph / swarm_persona_synthesize / swarm_parallel_simulate / swarm_report_generate / swarm_deep_interact；角色 swarm_orchestrator / persona_architect / report_synthesizer；工作流 five_stage_pipeline / god_view_injection），`MECHANISM_COVERAGE` **11/11**，`get_manifest()` 输出覆盖率。
4. **V24-D · 注册与入口**：`packs/__init__.py` import + `EXTRA_PACK_REGISTRY` 登记 + `EXTRA_PACK_ORDER` 追加 `"swarm_intel"`（18→**19**）；`butler_os.py` 菜单追加 `[14] 群体智能`（`cmd_swarm_intel` + `_get_swarm_intel_pack` 懒加载）；`pyproject.toml` 追加 `holoaeon-swarm-intel="holoaeon.swarm_intel:main"`（现 **13** 命令）。
5. **V24-E · 测试**：新建 `tests/test_swarm_intel.py` 8 例（建图 / 角色 / 模拟双路+确定性 / 报告结构与涌现检测效力 / 深度交互 / 五阶段终态 / God View 注入+皮肤过滤 / 11-11 机制覆盖）。
6. **V24-F · 连带同步（R-04 契约）**：`concept_anatomy.py` `verify_doc_version` → 0.9.19、`verify_extra_pack_order` → 19；`test_v19_concept_anatomy.py` / `test_v22_eng_skills.py` / `test_v12_v17_integration.py` 中「等于 18 / 末位 eng_skills」类断言改述为「包含 + 下界」（新增扩展包不再破门）。

验证全绿：`selftest 25/25` · `v3_gate 32/32` · `unittest 188 OK`（主 tests，180+8）+ `v3 11 OK` + `verax 21 OK` · `redline 108 文件 0 违规` · `dimension_lock PASS`（12 维度 + 7 闸 + 0 violation；快照 spec_doc_version 0.9.4→0.9.19、extra_packs 9→19 均标「演进（正常）」）· `bench diff0` 两次连跑一致 `6d119b2a9f2df687`（未漂移，本批新增与文档修改均不参与 ReproHash）· `python -m holoaeon.swarm_intel --demo` 完整跑通（50 实体 / 50 agent / 250 行动 / 5 轮）。

**维度不变**：25 / 47 / 9 与 `spec.VERSION=0.9.1`、`diff0_hash=2fc892cf9af6e755`、`tamper=f42c8229ee5acd73` 未动；`EXTRA_PACK_ORDER` 18→**19**（第 19 扩展包仅旁挂，不进 `PACK_ORDER`，A1 的 25/47/9 不受影响）；装配 **66 agents / 280 skills**（含全部扩展包，非冻结口径；核心九包仍 25/47）。

**证据等级**：`evidence_class=simulated` —— 群体模拟是结构推演，仿真≠证明，碳基终裁。

### V23 · 回收式整理补丁（维度锁诚实化 + README 回读 + Guard 统一，不改维度）

`DOC_VERSION` 0.9.17 → **0.9.18**（`spec.VERSION` 仍 0.9.1）。对应 `AGENT_FEED_V23_RECYCLE_HONESTY_PATCH_20261104.md`，触发依据=千问 V22+ 评估 78.0 分（P0-1 维度锁自指 / P1-2 README 7 项陈旧 / P1-3 行数陈旧 / P1-4 CI 结论过期 / P1-5 Guard 口径不一致 / P2-7 缺同名包排查 / P2-8 缺中文路由测试）。四人组定调 `check_emergence(0.85,0.85,0.85,0.30)` → emergence=True order=0.5237。扬弃结论：取「诚实化方案 B」（冻结快照显式声明），弃「重算 diff0 / 更新冻结值 / 自动校验快照 / 外部 benchmark」。

1. **V23-A · 维度锁诚实化**：`reports/dimension_lock.json` D02/D05/D06/D07 四项追加 `"verify": false` + note 注明「冻结快照项：值随 DOC_VERSION 演进，不参与运行态锁死校验」；D01/D03/D04/D08/D09/D10/D11/D12 八项运行态锁死项一字未动。
2. **V23-B · 校验脚本透明化**：`scripts/check_dimension_lock.py` 新增 `FROZEN_SNAPSHOT` 字典 + `read_frozen_snapshot_current()` + `print_frozen_snapshot()`，PASS 后打印 `[SNAPSHOT]` 差异块（spec_doc_version 0.9.4→0.9.18、extra_packs 9→18 标「演进（正常）」）；`EXPECTED` 不变、退出码逻辑不变（快照差异不判 FAIL）。
3. **V23-C · README 回读**：`README.md` / `README.zh-CN.md` 顶部表格按实测覆盖——日期 2026-11-05、最新批次 V23、徽章 `tests-180+11+21`、门禁 `redline 106 文件 0 违规`、`unittest 180 + v3 11 + verax 21`、`test_10_no_new_pack` 下界 `>=11` 口径。
4. **V23-D · 一句安心话**：去掉写死的「3547 行」，改为「纯标准库 Python（零第三方依赖，行数随版本演进不复写死）」。
5. **V23-E · CI 结论修正**：「无 .github/workflows」→「`.github/workflows/ci.yml` 已存在且已在 GitHub 实跑，run #25 全绿」。
6. **V23-F · Guard 口径统一**：L1-L8（8 层）为维度锁冻结串联守卫，L9（产品层路径闸门）/L10（贝叶斯层）为附加层默认 L9 开 L10 关、不计入 `guard_layers=8`；README 两版同步追加口径说明。
7. **V23-G · 同名包排查**：两份 README 补 `<details>` 同名包冲突排查（PyPI 同名包 / PYTHONPATH 污染 / 缓存残留 / `__file__` 验证）。
8. **V23-H · router 中文路由测试**：新建 `tests/v3/test_router_chinese.py` 6 例（连续子串 / 子串 / 逐字符按序降级 / 无匹配广播 `*` / 中英混合 / 确定性），按 `RouterLayer` 真实 API（`register_rule` / `receive→str`）适配，非投喂稿假设的 `register(name, skills=[...])`。
9. **V23-I · 文档版本**：`spec.py` `DOC_VERSION = "0.9.18"`（`VERSION="0.9.1"` 冻结未动）。

验证全绿：`selftest 25/25` · `unittest 180 OK`（主 tests）+ `v3 11 OK`（含 V23-H 新增 6 例）+ `verax 21 OK` · `redline 106 文件 0 违规` · `v3_gate 32/32` · `dimension_lock PASS`（SNAPSHOT 差异块正常打印）· `bench diff0` 两次连跑一致（`6d119b2a9f2df687` 未变，V23 全部修改点不参与 ReproHash）· `DOC_VERSION=0.9.18` · `EXTRA_PACK_ORDER=18`（不变）。

**维度不变**：25 / 47 / 9、`spec.VERSION=0.9.1`、`diff0_hash=2fc892cf9af6e755`、`tamper=f42c8229ee5acd73`；`EXTRA_PACK_ORDER=18` 不变；V23 为纯「数据+文档+测试+校验脚本」回收式补丁，不碰任何运行态源码。

### V22+ · 千问评估补丁（中文分词修复 · V22 补丁升级，不改维度）

`DOC_VERSION` 保持 **0.9.17** 不变（补丁不改功能维度，`spec.VERSION` 仍 0.9.1）。对应 `AGENT_FEED_V22_QIANWEN_EVALUATION_PATCH_20261104.md`（投喂稿编号 V22 与已交付「V22 工程技能本地化」撞车 → 现场裁决为 **V22+ 补丁升级**）。报告来源：千问端 STANDARD_BASED_EVALUATION（8 维度 79.0 分居首，5 短板）+ 耦合装入报告（族级路由中文分词缺陷）+ 翻车复盘（无收尾反馈）：

1. **V22+-A · PR-1 修复 `_split()` 中文分词（P0-1）**：`holoaeon/fusion_upgrade/external_skill_registry.py` 行 120-131 原实现 `isalnum()` 对中文整句塌单 token（`_split('把视频逐字稿转成张量')` → 单 token，'视频' 不可命中，中文路由全盲）→ 改为 **CJK bigram 分词**（中文连续段 `[a-zA-Z0-9_]+` 外按相邻字符对切，英文段走原逻辑；零依赖、纯字符扫描、同输入同输出）。修复后 `_split('把视频逐字稿转成张量')` → `['把视','视频','频逐','逐字','字稿','稿转','转成','成张','张量']`。
2. **V22+-B · PR-2 清单卫生（P1-1）**：SHA256SUMS 实测 grep 无 `_tmp_` 残留（0 matches）→ 检查通过，清单无需修改。
3. **V22+-C · 已修确认（不修改）**：P0-2 大小写归一化——`match()` line 94 已 `text = (task or "").lower()`，实测 `match("DATA 经络")==match("data 经络")` 同族；P1-2 收尾反馈为千问侧问题不改 HoloAeon；P2-1 功能适合性=设计取舍、P2-2 MCP/A2A=V14 protocol_plugins 已有、P2-3 V6 卫生=V18 审计 10 项已修。
4. **V22+-D · 测试**：新建 `tests/test_v22p_chinese_split.py`（6 tests：CJK bigram / 长中文句不塌 token / 中英混合分词 / match 中文长句可路由【数据经络皮肤细胞骨架 → F05/F08/F10】/ 大小写归一化一致 / 确定性）。断言口径按真实登记表 `data/v6_skill_family_registry.json` 实测校准（投喂稿 PR-3 的"视频张量必有族"假设与登记表不符，改为真实可验证口径）。
5. **V22+-E · 工程纪律**：external_skill_registry 属 fusion_upgrade **旁挂层**（不在 25/47/9 内核维度内）→ diff0 未漂移（实测 dimension_lock 0 violation）；B8 双仓清单重建（holo_entries=251）。

验证全绿：`selftest 25/25` · `unittest 364 OK`（+6 V22+ tests）· `redline 106 文件 0 违规` · `v3_gate 32/32` · `dimension_lock 0 violation`（diff0=2fc892cf9af6e755 未漂移）· `py38 256 文件 0 失败` · `contract PASS` · `plugin runtime 10/10` · `verify_v44 13/13` · B8 holo_entries=251 · five_site 28/171/0 · zip 不动点 a87fa921bf963fa1 · `VERSION=0.9.1` 冻结未动。

**维度不变**：25 / 47 / 9、`spec.VERSION=0.9.1`、`diff0_hash=2fc892cf9af6e755`、`tamper=f42c8229ee5acd73`；`DOC_VERSION=0.9.17`（补丁不升级）；`EXTRA_PACK_ORDER=18`（补丁不加扩展包）。

### V22 · 工程技能本地化工具箱（V22-A→F，mattpocock/skills 310K★ 蒸馏，第 18 扩展包，不改维度）

`DOC_VERSION` 0.9.16 → **0.9.17**（`spec.VERSION` 仍 0.9.1）。对应 `AGENT_FEED_V22_ENG_SKILLS_LOCALIZATION_20261104.md` 步骤 A→F 贯序执行（原投喂稿编号 V21 与已交付"V21 概念解剖器图像增强版"撞车，审视修正为 V22）。蒸馏口径：mattpocock/skills（39 个 SKILL.md，MIT，310K★，"Skills for Real Engineers"）→ 39→8 核心 → **LLM 提示词→确定性 Python 函数**（规则驱动非 LLM）→ 8 技能映射 8 个全息机制 → 四人组决策（emergence=True，P2×P3=0.72、P1=0.85、P4=0.30、order=0.52）→ 借鉴 D-01 handoff / D-02 wait-what→re_explain / D-03 prototype：

1. **V22-A · 新建 `holoaeon/packs/engineering_skills_pack.py`**：第 18 扩展包 8 技能/4 角色/2 工作流，key="eng_skills"。8 技能×8 机制：grill_plan 审讯规划（心跳机制：计划→结构化问题清单，中文正则分词 `[a-zA-Z0-9_]+|[\u4e00-\u9fff]+`）/ session_handoff 会话交接（经络机制 Bus：状态→交接文档，**handoff_id 由状态内容 sha1 派生，确定性不编造**）/ re_explain 重新解释（语义通信基座：文本→CONCEPT_MAP 术语重解释，Seb 同义）/ quick_prototype 快速原型（细胞骨架：验证方案+golden 回归，不污染主分支）/ deterministic_tdd 确定性 TDD（皮肤机制：红绿重构+selftest+diff0）/ dual_axis_review 双轴审查（皮肤机制：redline=Standards + verify_v44=Spec 双轴并行，命令指真实入口）/ hypothesis_debug 假设调试（去幻觉：五阶段调试环+莱布尼茨 PSR，禁"猜测→改→试→猜测"）/ shared_glossary 共享词汇表（赫布+经络：CONCEPT_MAP+访问权重，**默认 learning=False 固定基线保证确定性**，learning=True 才赫布增强）。
2. **V22-B · 注册第 18 扩展包**：`packs/__init__.py` import + `EXTRA_PACK_REGISTRY` 登记 + `EXTRA_PACK_ORDER` 追加 `"eng_skills"`（17→**18**）；`butler_os.py` 追加 `_get_eng_skills_pack()` + `cmd_eng_skills()` + 菜单 13 工程技能；`pyproject.toml` 追加 `holoaeon-eng`（现 12 命令）；`spec.py` `DOC_VERSION` 0.9.16 → **0.9.17**（VERSION 0.9.1 冻结未动）。
3. **V22-C · 同步断言**：`concept_anatomy.py` verify token 同步（verify_extra_pack_order 17→**18**、verify_doc_version 0.9.16→**0.9.17**，R-04 同步契约）；`tests/test_v19_concept_anatomy.py` 断言同步（18 / 0.9.17）；`tests/test_v12_v17_integration.py` all_extra_packs()==17→**18**；B8 双仓清单重建（根 `SHA256SUMS` + `data/dual_repo_sums.json` + `reports/b8_dual_sync_check.json`，holo_entries=250）。
4. **V22-D · 测试**：新建 `tests/test_v22_eng_skills.py`（27 tests：8 技能结构 / 确定性【handoff_id 稳定/权重稳定/问题清单一致】/ CLI【--list/--roles/--workflows/--skill/未知技能/坏 JSON】/ 注册【EXTRA=18/eng_skills 收尾】/ 版本同步 / Kernel install 8 技能 4 agent）。
5. **V22-E · 工程纪律**：包内导入全相对导入（redline `third_party_import` 零违规）；审视修正 6 处（编号撞车→V22、时间戳→确定性 sha1、赫布权重累积→固定基线、split 中文退化→正则、f-string 双重插值→format、import 置顶+补 main CLI/`__main__` 守卫）。

验证全绿：`selftest 25/25` · `unittest 358 OK`（+27 V22 tests）· `redline 106 文件 0 违规` · `v3_gate 32/32` · `dimension_lock 0 violation`（diff0=2fc892cf9af6e755 未漂移）· `py38 255 文件 0 失败` · `contract PASS` · `plugin runtime 10/10` · `verify_v44 13/13` · 8 技能烟测全过（grill 3 问/handoff 确定性 id/re_explain 命中/prototype throwaway/tdd vertical/review parallel/debug 5 相/glossary 共振）· B8 holo_entries=250 · five_site 28/171/0 · zip 不动点 a87fa921bf963fa1 · `VERSION=0.9.1` 冻结未动。CLI 实测：`holoaeon-eng --list` / `holoaeon-eng --skill grill_plan --args '{"plan_description":"加个缓存"}'` / `python -m holoaeon.butler_os 13`。

**维度不变**：25 / 47 / 9 与 `spec.VERSION=0.9.1`、`diff0_hash=2fc892cf9af6e755`、`tamper=f42c8229ee5acd73`；`EXTRA_PACK_ORDER=17→18`（第 18 扩展包仅旁挂，不进 `PACK_ORDER`）；`DOC_VERSION=0.9.16→0.9.17`。

### V21 · 概念解剖器 · 图像增强版（V21-A→D，快照-参考-生成 + 系列工具 + 加载协议 + 视觉锻造台，不改维度）

潘老师实测反馈"图像方面太弱，不要再出一堆文字，要像样的图"：先规划（`docs/V21_概念解剖器_图像增强_规划.md`：问题诊断四维差距【无爆炸展开/无标注引线/无放大细节/无成品对照】→ 双轨架构【本地确定性 SVG + 生成式后端】+ 模块二视觉锻造台八步流水线），再概念验证（image_search 快照 2 张标杆图【大英百科横截面标注图/千图网数字编号爆炸图】→ image_edit 生成圆珠笔爆炸图示意图【数字编号 1-15 + 零件分解 + 成品对照】，"快照→生成"链路实证可行），按路线 A→D 贯序执行：

1. **V21-A · 渲染器系列 + 加载协议**：新建 `holoaeon/concept_anatomy_render.py` —— 4 渲染器（`render_explosion` 爆炸图【零件沿轴展开+数字编号引线+成品对照区】/ `render_annotated` 标注图【横截面+引线标注+放大细节】/ `render_legend` 图例图【维度色语义+零件清单】/ `render_diagram` 结构图【等距投影增强版】）+ `RENDER_REGISTRY` 插件化注册 + `register_render/load_render` 加载协议（未注册 style 回落 diagram 容错）+ 5 图像 Token（img_style/img_palette/img_axis/img_annotate/img_compare，不动既有 26 Token）+ `concept_anatomy.py` 集成 `--img <style>`/`--save <path>`（本地确定性渲染）。
2. **V21-B · 概念视觉锻造台**：新建 `holoaeon/concept_visual_forge.py` —— 八步确定性流水线（`forge` 文字入口 → `text_search` 搜索【CONCEPT_MAP 命中/表外关键词抽取+就近概念】→ `image_desc_v1` 初级图像描述 → `system_prompt_gen` 系统提示词 → `matrix_modify` 矩阵修改【6 风格×3 构图×3 色调】→ `optimize_prompt` 优化【质量锚点+负面提示词+确定性锚点"只画映射表内元素"】→ `stylize` 三档风格化【blueprint 蓝图化/art_direction 美术化/artistic 艺术化】）+ `concept_anatomy.py` 集成 `--forge`（八步 JSON）。工程路径"优化→创建→升级"：解剖器负责真值（不编造），锻造台负责视觉翻译（规则化），生成式后端可接 image_gen/image_edit 出 AI 示意图。
3. **V21-C · 测试**：新建 `tests/test_v21_render.py`（13 tests：4 渲染器 SVG 断言【爆炸轴/编号/引线/对照区/调色板切换】+ 协议【注册表/未注册回落/自定义注册/协议入口】+ CLI --img/--save subprocess）+ `tests/test_v21_visual_forge.py`（13 tests：搜索命中/表外/全内置、初级描述/系统提示词/矩阵 6 变体/优化负面+确定性/三档风格化/CLI 集成）。
4. **V21-D · 工程纪律**：包内导入全部相对导入（redline `third_party_import` 对绝对导入判违规已修复：`from .concept_anatomy import ...`）；全套验证矩阵全绿；维度冻结不破；README×3 + 手册 + 回执 + 单提交 + 五地同步。

验证全绿：`selftest 25/25` · `unittest 全套 OK`（+26 V21 tests）· `redline 105 文件 0 违规` · `v3_gate 32/32` · `dimension_lock 0 violation`（diff0=2fc892cf9af6e755 未漂移）· `py38 253 文件 0 失败` · `contract PASS` · `plugin runtime 10/10` · `verify_v44 13/13` · 实测 4 风格出图（explosion 4196 / annotated 1499 / legend 1090 / diagram 2009 字符）+ `--forge` 八步 JSON（表外圆珠笔/内置经络双通道）。

**维度不变**：25 / 47 / 9 与 `spec.VERSION=0.9.1`、`diff0_hash=2fc892cf9af6e755`、`tamper=f42c8229ee5acd73`；`EXTRA_PACK_ORDER=17` 不变；`DOC_VERSION=0.9.16` 不变。

### V21-E · 实测示例：表外概念注入解剖（双连测 · 微缩图）

表外概念（不在内置 10 概念内）一律**确定性拒绝**（防幻觉，不编造）：`python -m holoaeon.concept_anatomy 电动跑步机 --explain` → `「电动跑步机」不是内置概念` + 可用概念列表，exit 0。进程内注入演示承载可解剖能力（仅内存、不改文件、不入库）→ 十步工序 `status: DONE` → 锻造台八步流水线取三档风格化提示词 → AI 生成三风格图（seedream_5.0_flash）。实测两例：

**例 1 · 电动跑步机（机制类 · 10 零件）**

驱动电机 / 前滚筒 / 后滚筒 / 跑带 / 跑台板 / 扶手 / 控制面板 / 坡度调节机构 / 心率传感器 / 安全急停开关

<img src="docs/assets/treadmill_schematic.png" width="280"/> <img src="docs/assets/treadmill_blueprint.png" width="280"/> <img src="docs/assets/treadmill_impressionist.png" width="280"/>

（示意图 · 透明透视 / 蓝图 · 工业爆炸分解 / 美术 · 印象派晨光健身房）

**例 2 · 变形金刚擎天柱（机制类 · 10 零件）**

驾驶舱（车头）/ 车厢折叠机构 / 主框架（骨骼）/ 能量核心（火种源矩阵）/ 装甲板 / 液压关节系统 / 光学传感器（双眼）/ 武器系统（离子炮）/ 轮组（变形为腿部）/ 排气口散热

<img src="docs/assets/optimus_schematic.png" width="280"/> <img src="docs/assets/optimus_blueprint.png" width="280"/> <img src="docs/assets/optimus_impressionist.png" width="280"/>

（示意图 · 透明透视 / 蓝图 · 工业爆炸分解 / 美术 · 印象派黄昏港口）

链路：表外概念 → 确定性拒绝（防幻觉闸门）→ 注入解剖（文字维度 10 零件）→ 锻造台八步流水线 → 三风格 AI 出图。本地确定性（SVG/十步工序）+ 生成式（AI 三图）双轨均实测通过。

### V20 · 概念解剖器 · 落地场景版（V20-A→C，V19 重设计，不改维度）

V19 做了**能力**（能解剖概念），没做**用途**（解剖出来能干嘛）；V20 补上**用途**——概念解剖器 = HoloAeon 项目的"汉字字典"：看到"经络""赫布场""城邦"看不懂时，一条命令 `python -m holoaeon.concept_anatomy 经络 --explain` 用大白话告诉你这是哪个模块、由哪些零件组成、怎么验证它在工作、去哪看源码。对应 `AGENT_FEED_V20_CONCEPT_ANATOMY_REDESIGN_TEXT_20261104.md`（原补丁包 `AGENT_FEED_V20_PATCH_V19_CLOSURE_20261104_OBSOLETE.md` 改名作废）步骤 A→C 贯序执行；四人组决策（emergence=True，P2×P3=0.7225、P1=0.85、P4=0.30、order=0.5237）：

1. **V20-A · explain() 大白话函数**：`concept_anatomy.py` 新增模块级 `explain(concept) → str`（从 CONCEPT_MAP 取真值格式化：维度中文名 `DIMENSION_CN` 映射（mechanism→机制类等 9 类）→ 一句话 → 靠什么实现 → N 个零件清单 → 怎么验证 → 去哪看源码；未知概念返回"「x」不是内置概念 + 可用概念列表"；默认演示"经络"）。
2. **V20-B · CLI --explain + __main__ 守卫**：`main()` 追加 `--explain` 分支（大白话文字模式，非 JSON）；文件末尾补 `if __name__ == "__main__": sys.exit(main())` —— **修复 V19 已知点**（`python -m holoaeon.concept_anatomy` 直跑无输出）。
3. **V20-C · 使用手册 + 测试**：新建 `docs/V20_概念解剖器_使用手册.md`（非技术手册：一段话定位 + 三个真实落地场景【新人看代码 / 改代码前查影响 / 写文档贴材料】+ 一条命令速查 + 10 概念大白话速查表）；`docs/V19_概念解剖器_小白导学手册.md` 已知点段落同步更新（标注 V20 已修复）；新建 `tests/test_v20_concept_anatomy.py`（12 tests：explain 全 10 概念 / 未知 / 默认演示、DIMENSION_CN 全覆盖、CLI --explain / JSON 回归、`-m` 守卫三模式 subprocess 实测输出非空）。

验证全绿：`selftest 25/25` · `unittest 121 OK`（109+12）· `redline 103 文件 0 违规` · `v3_gate 32/32` · 维度锁 0 violation（diff0=2fc892cf9af6e755 未漂移）· `contract PASS` · `py38 249 文件 0 失败` · `plugin runtime 10/10` · verify_v44 13/13 · `VERSION=0.9.1` 冻结未动 · `DOC_VERSION=0.9.16`（不变）· `EXTRA_PACK_ORDER=17`（不变）。

**维度不变**：25 / 47 / 9、`VERSION=0.9.1`、`diff0_hash=2fc892cf9af6e755`、`tamper=f42c8229ee5acd73`；新增 explain() 不改任何现有输出路径。用户落地路径：新人看代码 `python -m holoaeon.concept_anatomy 经络 --explain` → 改代码前 `python -m holoaeon.concept_anatomy 皮肤机制 --explain` 查组件影响 → 写文档 `explain("去幻觉")` 直接贴进材料。下一步 V21 = 多模态版（SVG 交互图 + 语音解说）。

### V19 · 概念解剖器 · Anatomy 创意蒸馏（V19-A→F，不改维度）

`DOC_VERSION` 0.9.15 → **0.9.16**（`spec.VERSION` 仍 0.9.1）。对应 `AGENT_FEED_V19_CONCEPT_ANATOMIZER_ANATOMY_DISTILLATION_20261104.md` 步骤 A→G 贯序执行。蒸馏口径：wheresryan22/anatomy（22K★ Claude Agent Skill，"The object is the explanation"）→ 第一性原理交集=**概念→确定性机制→运行验证概念**（Anatomy=视觉发明 LLM / HoloAeon=确定性查找 规则，步骤 3"发明对象"由 LLM 改为固化映射表查找）→ 四人组决策（emergence=True，P2×P3=0.7225、P1=0.85、P4=0.30、order=0.5237）→ **5 精华 D-01~D-05 + 剔除 4 糟粕 X-01~X-04**（WebGL 着色器 / React 绑定 / 打印 PDF / 截图验证）：

1. **V19-A · 概念解剖器**：新建 `holoaeon/concept_anatomy.py` —— `ConceptAnatomizer` 十步工序（定维度→取真值→发明映射→列组件→规划→构建→排序→装框→激活→审计）；`CONCEPT_MAP` 10 概念固化映射表（经络/心跳机制/细胞骨架/皮肤机制/经络机制/赫布协作场/语义通信基座/城邦架构/自组织耗散/去幻觉）；`DESIGN_TOKENS` 26 Token（运行时 6/审计 5/输出 5/验证 5/全息 5）；等距投影 SVG 渲染（30° COS30/SIN30，纯字符串拼接）；**确定性**：同概念+同Token→同解剖图（时间戳默认关闭 out_timestamp=False）；深度审计四检查（重叠对/穿透 depth 单调性/一致性/确定性）。
2. **V19-B · 概念解剖扩展包**：新建 `holoaeon/packs/concept_anatomy_pack.py` —— 继承 `DomainPack`，key="concept_anatomy"，**5 技能/3 角色/1 工作流**（技能 anatomy_concept/anatomy_audit/anatomy_svg/anatomy_map/anatomy_tokens；角色 anatomist/auditor/cartographer；工作流 full_anatomy）；SkillSpec 按 base.py 实际字段定义，模块级函数实现零依赖。
3. **V19-C · 注册第 17 扩展包**：`packs/__init__.py` import `ConceptAnatomyPack` + `EXTRA_PACK_REGISTRY` 登记 + `EXTRA_PACK_ORDER` 追加 `"concept_anatomy"`（16→**17**）；注释补第二十三。
4. **V19-D · 菜单+命令**：`butler_os.py` 菜单追加 [12]概念解剖（`cmd_concept_anatomy` 演示"经络"：扩展包 5/3/1 统计 + 10 可用概念 + 解剖结果 + 四审计数 + SVG 长度）；`pyproject.toml` 追加 `holoaeon-anatomy="holoaeon.concept_anatomy:main"`（现 11 命令）。
5. **V19-E · 文档版本**：`spec.py` DOC_VERSION="0.9.16"（VERSION="0.9.1" 冻结未动，diff0 保护不破）。
6. **V19-F · 集成测试**：新建 `tests/test_v19_concept_anatomy.py` —— 19 tests（26 Token 五组/10 概念全 DONE/确定性两次一致/穿透审计/SVG/第 17 扩展包注册/菜单 12/CLI）；`tests/test_v12_v17_integration.py` 伴随更新 `all_extra_packs()==16→17`。

验证全绿：`selftest 25/25` · `unittest 109 OK`（含 V19 新 19 tests）· `redline 103 文件 0 违规` · `v3_gate 32/32` · `verify_v44 13/13` · 维度锁 0 violation（`diff0=2fc892cf9af6e755` **未漂移**——EXTRA_PACK_ORDER 16→17 不触发：selftest 对 EXTRA 仅断言 len>=7 + 成员包含，VERSION/RUNTIME_ID 未动）· contract PASS · py38 语法 248 文件 0 失败 · plugin runtime 10/10 · butler_os 菜单 12 实操 DONE · 装配快照 agents=**59** skills=**267**（+3 角色 +5 技能 旁挂增量，G15 不受影响）· five_site package=28/repo=171/missing=0 · zip 不动点 a87fa921bf963fa1 保持。

**维度不变**：25 / 47 / 9 与 `spec.VERSION=0.9.1`、`diff0_hash=2fc892cf9af6e755`、`tamper=f42c8229ee5acd73`；`EXTRA_PACK_ORDER` 16→**17**（第 17 扩展包仅旁挂，不进 `PACK_ORDER`）；用户落地路径：概念名 → 固化映射表确定性查找 → 十步工序解剖 → 深度审计 → 等距投影 SVG → JSON 解剖图回执。

### V17 · 玉安记忆之王 + V18 · V6 补丁收尾 + 集成验证（V17→V18，不改维度）

`DOC_VERSION` 保持 **0.9.15** 不变（V17 记忆模块在源码树外，V18 不改源码，不触发版本升级）。对应 `AGENT_FEED_V18_PATCH_CLOSURE_V17_BRIDGE_INTEGRATION_20261104.md` 步骤 A→E 贯序执行：

1. **V17-A · 玉安记忆之王执行**：新建 `F:/doubaowork/memory_of_yuan.py`（项目外，纯标准库）—— 10 记忆域 JSON（`F:/doubaowork/holoaeon_memory/`：engineering_discipline/engineering_process/output_dimensions/five_site_sync/verification_procedures/version_history/holographic_system/quartet_toolkit/haole_yuan_lab/vector_sea）+ `.pth` 全域注册两处（.workbuddy 3.13.12 site-packages + sandbox site-packages，指向 `F:/doubaowork`）+ SKILL.md（`holoaeon` 关键词引发）；赫布场 learning_rate=0.12 decay=0.99；`memory_graph` 中英混合 token 分词（edges=8≥5）；封口密语：潮起开门，潮落闭嘴。V17 验证清单 9/9 PASS（10 域 / 全域加载 / 跨目录 seal / 全息 matched=5 / versions=16 / edges=8 / 同义 holoaeon / 封存 True / selftest 25/25）。
2. **V18-A · V6 遗留 12 项代码卫生审计收口**：逐项核验 —— 10 项已修/不适用 + 1 项已知漂移非阻断（test_holoaeon.py:316 断言 >=7）+ 1 项 CI 缺口**已消除**（`.github/workflows/ci.yml` 已存在且已在 GitHub 实跑，run #25 全绿）；**正式收口，无需额外代码修改**。
3. **V18-B · 集成测试**：新建 `tests/test_v12_v17_integration.py` —— 7 个 TestCase 22 tests 覆盖 V12-V17 六模块 + 跨模块协同（all_extra_packs()==16 / Kernel 装齐 9+16 包 submit / EXTRA_PACK_ORDER 顺序 topology_resonance→quartet_director→vector_sea→dehallucination→super_agent / butler_os 源码包含 vector_sea/dehallucination/router 字样；V17 已执行故不 skip；V13/V14 API 名按实际函数式 API 适配）。

验证全绿：`selftest 25/25` · `golden verify 5/5`（verify_all(n=2) 5 tasks True）· `集成测试 22 OK` · `unittest 90 OK`（主 tests，含 22 集成）+ verax 21 OK + v3 5 OK · `redline 101 文件 0 违规` · `v3_gate 32/32` · `verify_v44 PASS` · 维度锁 0 violation（`diff0=2fc892cf9af6e755` 未漂移）· contract PASS（PACK 9 / EXTRA 16）· MCP 回归 4/4 · V17 记忆模块 10/10 domains · `DOC_VERSION 0.9.15`（不变）· 承 **V16 确定性自主调度增强**。

### V16 · 确定性自主调度增强 · DeepSeek Super-agent 对标蒸馏（V16-A→E，不改维度）

`DOC_VERSION` 0.9.14 → **0.9.15**（`spec.VERSION` 仍 0.9.1）。对应 `AGENT_FEED_V16_SUPER_AGENT_DISTILLATION_20261103.md` 步骤 A→E 贯序执行。蒸馏口径：DeepSeek Super-agent（Router-Worker 双层/事件驱动/异步多信道/存算分离/外部 Watchdog）→ 对标矩阵（异步多信道=Envelope+adapter、存算分离=Memory+Kernel、Checkpoint=V11，已有不借鉴）→ 四人组决策（emergence=True）→ **5 精华 D-01~D-05 + 剔除 4 糟粕 X-01~X-04**，第一性原理交集=**确定性的自主调度**（规则驱动非 LLM，同输入同输出）：

1. **V16-A · 确定性 Router 层**：新建 `holoaeon/router_layer.py` —— `RouterLayer`（task_queue deque / shared_context / dispatch_rules 按 priority 排序 / worker_results / is_running）；`receive→_dispatch` 带**有序字符匹配降级链**（连续子串未命中时逐字符按序匹配，`_match_rule` 静态方法确定性分派），'帮我写一篇文章'→writing_planner、'分析这份销售数据'→data_analyst、无关闲聊→'*'；`aggregate` / `get/update_shared_context` / `status`；`main` CLI（`--selfcheck` / 单条路由）。
2. **V16-B · 事件两级过滤**：新建 `holoaeon/event_filter.py` —— `EventFilter`（FAST_PATTERNS 14 词快速级 + DEEP_RULES 4 条 lambda 深检级），`filter()` 两级返回 `passed/level/reason`（L2=passed、L1=无关、bug 词命中=urgent），`batch_filter` / `main` CLI。
3. **V16-C · 外部 Watchdog**：新建 `holoaeon/external_watchdog.py` —— `ExternalWatchdog`（BASE_LINE 冻结基线 dict），`check_selftest/check_diff0/check_redline` **只 observe 不执行**、`alert` **只告警不拦截**（Guard L1-L10 外部伴生，不碰内核）、`snapshot`；`main` CLI。
4. **V16-D · 自主调度扩展包**：新建 `holoaeon/packs/super_agent_pack.py` —— 继承 `DomainPack`，key="super_agent"，**5 技能/3 角色/1 工作流**（技能 router_dispatch/event_two_filter/watchdog_monitor/context_isolate/proactive_scan；角色 router_coordinator/filter_engineer/watchdog_operator；工作流 super_agent_flow）；自实现零依赖；selfcheck 断言 D01=writing_planner D02=L2 D03=1 D04=True D05=50。
5. **V16-E · 注册四处**：`packs/__init__.py` import `SuperAgentPack` + `EXTRA_PACK_REGISTRY` 登记 + `EXTRA_PACK_ORDER` 追加 `"super_agent"`（15→**16**）；`spec.py` DOC_VERSION="0.9.15"（VERSION="0.9.1" 冻结未动）；`butler_os.py` 菜单追加 [11]自主调度（cmd_super_agent 完整演示）；`pyproject.toml` 追加 `holoaeon-router / holoaeon-watchdog`（现 10 命令）。

验证全绿：`selftest 25/25` · `unittest 68 OK`（tests/verax 21 OK + tests/v3 21 OK）· `redline 101 文件 0 违规`（+4 新 py）· `v3_gate 32/32`（A12.1 零依赖未破）· 维度锁 0 violation（diff0=2fc892cf9af6e755 未漂移）· `verify_v44 13/13` · contract PASS · MCP 回归 13/13（doc_version 期望同步 0.9.15）· 四新模块 selfcheck 全 PASS（router dispatch 4 类 / event_filter L2 / watchdog alerts=1 / super_agent 5·3·1）· 装配快照 agents=**56** skills=**262**（+3 角色 +5 技能 旁挂增量，G15 不受影响）· 写型链全绿（b8 245/91 interface_equal=true · b9 criteria=30/risks=12/ledger=12 zip 不动点 a87fa921bf963fa1 保持 · five_site package=28/repo=171/missing=0 · vector_sea_manifest 195/195）。

**golden 重冻结（V16 修复项，如实披露）**：排查并修复历史遗留 word_count 黄金失配——实锤为 **V6 起 agent.py:42（handle() 写 result["degraded"]）新增字段**致 V3 时代冻结黄金值过期（删字段后哈希恰=2b82a6ef7188ce91 原值）；ftrace 证明非 V16 引入（stash 四文件后仍 FAIL）。单点重冻结 3 个 golden：word_count 2b82a6ef7188ce91→**e1b6c4ba5c26943b**、data_describe 3352db0f803eb727→**8cd80c70ad275455**、quant_sharpe 2c9e5d7d01526ce8→**8ee7170326666303**（frozen_at=2026-11-03，note 注明旧→新哈希）；`tests/verax/test_repro.py` GOLDEN_HASH 同步 e1b6c4ba5c26943b；verax_verify 复现 5/5 全 golden=True。verax_verify 总结论 yellow（H2=3：scan_receipts 逐行扫多行 indent JSON 的口径局限——dimension_lock.json:21/31 与 daily_gate 中间行被误判缺 evidence_class，顶层实含 evidence_class="simulated"，非真实违规；V2 三硬红线 hits=[] 全绿）。全仓 2b82a6ef7188ce91 共 40 处引用均为历史投喂包/README/docs/snapshot/_cases 演示用例，不改、如实披露口径。

**维度不变**：25 / 47 / 9 与 `spec.VERSION=0.9.1`、`diff0_hash=2fc892cf9af6e755`、`tamper=f42c8229ee5acd73`；`EXTRA_PACK_ORDER` 15→**16**（第 16 扩展包仅旁挂，不进 `PACK_ORDER`）；用户落地路径：任务 → RouterLayer 确定性分派（有序字符匹配）→ EventFilter 两级过滤 → ExternalWatchdog 外部只读伴生监护（只告警不拦截）→ super_agent_pack 5 技能自主调度闭环。

### V15 · 自组织相似性全息去幻觉模块（V15-A→D，不改维度）

`DOC_VERSION` 0.9.13 → **0.9.14**（`spec.VERSION` 仍 0.9.1）。对应 `AGENT_FEED_V15_DEHALLUCINATION_LEIBNIZ_ZHANGPING_20261103.md` 第三部分，步骤 A→D 贯序执行（莱布尼茨充足理由律 × 张平语义基 × HoloAeon 赫布场）：

1. **V15-A · 去幻觉模块**：新建 `holoaeon/dehallucination.py` —— `DeHallucinationModule` 8 阶段流水线（input→seb_extract→reality_anchor→snapshot_vec→leibniz_compare→synonym_map→verdict→hebbian_update）；核心阈值 `COSINE_HIGH=0.7`（≥0.7 非幻觉）`COSINE_LOW=0.4`（<0.4 幻觉）0.4-0.7 待审⚠️、`BAYES_PRIOR=0.15` `BAYES_THRESHOLD=0.5`；联网经 `fetch_callback` 回调注入（不硬编码 WebSearch），None 时降级内部比对；贝叶斯后验 (likelihood×prior)/(likelihood×prior+(1-likelihood)×(1-prior)+1e-10)；耗散熵=归一化信息熵；`check()` 返回 module/input_text/semantic_base/reality_snapshot/cosine/synonym/bayesian/dissipation/sufficient_reason/verdict/hebbian_weight/theory/timestamp；附 `selfcheck()` 三分支确定性自检 + `main()` CLI；纯标准库零依赖（verify_v44 A12 零依赖未破）。投喂参考代码 `main()` 的 `--callback` 分支注释与实现不符（所有 argv 拼 text），已转写为可运行实现（实际降级无联网模式可跑）。
2. **V15-B · 去幻觉扩展包**：新建 `holoaeon/packs/dehallucination_pack.py` —— 继承 `DomainPack`，key="dehallucination"，**6 技能/3 角色/1 工作流**（技能 semantic_base_extract/reality_anchor/leibniz_space_compare/synonym_mapping/hallucination_verdict/hebbian_feedback；角色 anchor_engineer/semantic_analyst/verdict_judge；工作流 dehallucination_flow）；阈值从 `dehallucination` 常量 import 保持口径一致，技能函数内联实现零依赖。投喂验证清单第 7 项 `p.SKILLS` 大写与 base.py 契约不符，已按契约属性复测 skills=6 roles=3。
3. **V15-C · 注册第 15 扩展包**：`packs/__init__.py` import `DeHallucinationPack` + `EXTRA_PACK_REGISTRY` 登记 + `EXTRA_PACK_ORDER` 追加 `"dehallucination"`（14→**15**）。
4. **V15-D · 菜单+命令+文档版本**：`butler_os.py` 菜单追加 [10]去幻觉检测（cmd_dehallucinate 读输入→8 阶段检测输出语义基/快照/余弦/同义/贝叶斯/熵/充足理由/判定/赫布权重，空输入用演示样本）；`pyproject.toml` 追加 `holoaeon-dehallucinate="holoaeon.dehallucination:main"`。

验证全绿：`selftest 25/25` · `unittest 68 OK` · `tests_contract 184 OK` · `redline 97 文件 0 违规`（+2 新文件）· `v3_gate 32/32`（A12.1 零依赖未破）· 维度锁 0 violation（diff0=2fc892cf9af6e755 未漂移）· `verify_v44 13/13` · MCP 回归 13/13（doc_version 期望同步 0.9.14）· 模块自检 PASS（三分支 non_hallucination/hallucination/uncertain）· 扩展包自检 PASS（6/3/1）· 降级检测 '人工智能多智能体系统架构设计' → verdict/cosine/entropy 三值齐 · 装配快照 agents=**53** skills=**257**（+3 角色 +6 技能 旁挂增量，G15 不受影响）。

**维度不变**：25 / 47 / 9 与 `spec.VERSION=0.9.1`、`diff0_hash=2fc892cf9af6e755`、`tamper=f42c8229ee5acd73`；`EXTRA_PACK_ORDER` 14→**15**（第 15 扩展包仅旁挂，不进 `PACK_ORDER`）；用户落地路径：AI 输出 → 语义基提取（张平 Seb）→ 联网取点快照（莱布尼茨充足理由）→ 余弦空间比对 → 同义映射 → 贝叶斯+耗散熵判定 → 赫布反馈自组织学习。

**全息体系对应表（V16 更新版）**：**经络 = 自组织相似性类节点共振**（`topology_resonance_pack.resonance_node`：1331×1331 共振 + 莫比乌斯回边 + 克莱因收敛熔断），**≠ Bus**；**经络机制 = Bus**（C2 发布/订阅/路由消息总线，独立概念）；心跳=Scheduler（tick=500ms adaptive）；细胞骨架=Kernel；皮肤=Guard L1-L10；赫布协作场=AdaptiveGraph（node_count=17 lr=0.12 decay=0.99）；语义通信基座=Envelope C1+Skill manifest C4+张平 Seb；runtime=Kernel+Scheduler+topology_runtime.py（StateReducer/Checkpoint/CircuitBreaker/DissipationMonitor）；graph=AdaptiveGraph+topology_resonance_pack 三 Graph 函数（mandala_expand/mobius_flip/klein_convergence）；城邦=九层词汇表（V11）；耗散结构五要件（开放系统←Envelope 接收/联网取点、远离平衡态←Scheduler tick、非线性←decay×learning_rate、涨落放大←resonance_node+mobius_edge、涌现←emergence_chain 四条件）；产品层：躯体=butler_os/灵魂=quartet_toolkit 14 技能/勘探=vector_sea_explorer/机床=skill_lathe/协议=protocol_plugins/去幻觉=dehallucination.py（V15 新增）/**调度=router_layer.py（V16 新增，确定性任务路由）+事件过滤=event_filter.py（两级过滤）+外部看门狗=external_watchdog.py（只 observe 只告警）+自主调度=super_agent_pack（5 技能/3 角色/1 工作流）**；语义知识库=向量海 617 技能+195 篇+10 GEMS+462 项。


### V3 · 借鉴 LangChain 的工程形态（文档版本 0.9.3）

一句话完成升级：`python scripts\launch_v3.py` —— 装载 V3 旁挂件、跑通内部融合 + 外部路由 +
桥 conformance，末行打印 `ALL_OK=True`。

维度不变：**25 智能体 / 47 技能 / 9 领域包 + 8 扩展包 / 34·21·5 单测 / 25 自检**，
`spec.VERSION` 仍是 `0.9.1`，`DIFF=0 2fc892cf9af6e755` 与篡改哈希 `f42c8229ee5acd73` 未动。
V3 新增 32 项门禁检查，**独立计数**，不并入上面任何一格。

八个旁挂工作包（全部零依赖、可跑）：统一调用协议与五段钩子（`runnable.py`）、
可哈希 span 树（`audit/span_tree.py`）、结构化 schema 校验与有限修复环（`skill_schema.py`）、
47 条评测集与双轨 diff（`scripts/eval_set.py` / `eval_diff.py`）、
interrupt 审批令牌与三档 checkpoint（`interrupt.py`）、渐进加载与字节缓存
（`skill_loader.py` / `cache.py`）、replay 分支与 7 类事件流（`replay_branch.py` / `event_channel.py`）、
桥 conformance 与迁移/弃用页（`bridges/conformance.py` / `docs/migration-from-langchain.md`）。

实测（本机 2026-11-01）：V3 门禁 `32/32 PASS`；`eval_47` 确定性轨 `47/47`（自述自证，
只证明路由不退化）；对抗变体 `cross` `0/47` 且 diff 判 `REGRESSED`（证明能抓回归）；
kfold 仍 `mean 0.9957 / std 0.0085`。机器可读接手页：[`snapshot/SNAPSHOT_V3.md`](snapshot/SNAPSHOT_V3.md)。

## 为什么选择 HoloAeon

| 原则       | 实际含义                            | 实测证据                         |
| -------- | ------------------------------- | ---------------------------- |
| **零依赖**  | `dependencies = []`，纯标准库，不装任何东西 | 红线扫描 
edline_scan 回读（当前 82 文件）零违规                |
| **默认离线** | 无网络调用、无内置密钥、无遥测                 | 核心包零网络 import（语法树级检查）        |
| **确定性**  | 相同输入产生相同输出                      | A1 验收双跑哈希逐位一致，CI 强制证据防漂移     |
| **可审计**  | 每次决策留痕、带理由码、可回放                 | nephron 认知账本，任意历史 tick 可重建   |
| **安全边界** | 八层语义守卫拦截危险操作                    | `os.system`/`eval`/越权/失真实测拦截 |
| **诚实纪律** | 仿真标记 `simulated`，未实测挂 `pending` | 第三方审计三轮，零虚报                  |

### Token 经济学：让 token 只花在语言上

统计、校验、格式化、流程编排等确定性工作由本地零成本执行，大模型只处理真正的语言任务——
校验类任务 token 从 O(材料长度) 降到 O(结论长度)，日常重度使用差额可达 30%–70%。

### 部署形态

| 形态                   | 说明                              |
| -------------------- | ------------------------------- |
| **纯骨架**（512MB 内存、无网） | 全部核心功能，零成本                      |
| **本地大脑**（+4GB 内存）    | 桥接 Ollama，AI 回答本地生成，仍免费离线       |
| **云端大脑**（+网络+密钥）     | 桥接豆包/千问/OpenAI 兼容端点，密钥只进环境变量    |
| **对话前端**             | WorkBuddy / 豆包工作技能包——自然语言驱动整套架构 |

---

## 🚀 快速使用说明（低配个人用户特化）

### 它能在什么机器上跑？

| 你的机器                                        | 能跑什么                                             |
| ------------------------------------------- | ------------------------------------------------ |
| 任何能装 Python 3.8 的电脑（2010 年后基本都行），512MB 空闲内存 | ✅ 全部核心功能：25 智能体、47 技能、账本、守卫、热插拔——**不需要显卡、不需要联网** |
| 上述 + 4GB 内存 + 约 4GB 硬盘                      | ✅ 额外可接本地真模型（Ollama + qwen2.5:0.5b）               |
| 上述 + 网络 + API 密钥                            | ✅ 额外可接豆包/千问等云端模型                                 |

> 一句安心话：HoloAeon 核心是纯标准库 Python（零第三方依赖，具体行数随版本演进不复写死），`pip install` 不安装任何东西，
> 不写注册表、不留后台进程——程序退出即消失。老机器放心折腾。

### 三步跑通（全程约 3 分钟，不联网）

```bash
# 第 1 步：获取（二选一）
git clone https://github.com/weideyouni/holoaeon.git
# 或者：GitHub 页面 Code → Download ZIP → 解压

# 第 2 步：进入目录
cd holoaeon

# 第 3 步：跑第一个示例
python examples/01_basic_matrix.py
```

看到 `runtime_id: HOLOAEON-RUNTIME-0.9.1` 和 25 个智能体清单，就是成功了。

### 你刚刚运行了什么？

一条任务文本被 8 层安全守卫检查 → 自动匹配到 writing 规划智能体 → 调用 `outline_gen`
技能生成大纲 → 结果连同资源占用清单一起回给你。**全程本地、全程确定性：再跑一遍，
输出逐字相同。**

### 接下来玩什么？

```bash
python examples/02_semantic_routing.py           # 语义路由
python examples/03_hebbian_collaboration.py      # 赫布协作
python examples/04_domain_pipeline.py            # 领域包流水线
python scripts/launch_local.py status            # 全家福健康报告
python scripts/launch_local.py run "你的任务"     # 提交任务，自动选智能体
python scripts/launch_local.py hotplug optimization  # 不重启热插拔优化包
```

### 想让 AI 真的开口说话？（可选，仍免费的本地路线）

```bash
# 前提：4GB 内存 + 约 4GB 硬盘。装 Ollama（ollama.com）后：
ollama pull qwen2.5:0.5b
python bridges/quickstart.py --check   # 自动探测本机模型
python bridges/quickstart.py --ask "用一句话解释什么是阴阳"
# 回执五要素：output / backend / mode=live / tokens / latency
```

没装 Ollama？`--check` 给三行安装指引并礼貌退出（退出码 2），绝不甩一屏报错。

### 💬 想用对话窗口当前端？（WorkBuddy / 豆包工作）

- **WorkBuddy**：把技能文件夹放入 WorkBuddy 技能目录，工作对话里用自然语言驱动整个架构；
- **豆包工作**：技能包 zip 直接拖入"插件·技能·伙伴 → 上传技能"弹窗，Agent 自动发现调用。

**完整逻辑流程**——前端负责"听懂人话"，HoloAeon 负责"确定性干活"：

```
你说："看下架构状态" / "跑个任务" / "热插优化包"
        ↓ 前端智能体加载技能包（意图→命令映射表）
        ↓ 执行确定性命令（launch_local.py status / run / hotplug）
        ↓ Kernel.submit → Guard 八层安检 → 匹配智能体 → 本地执行
        ↓ 结果 + 账本回执返回对话窗口
```

前端可换、骨架不动：对前端唯一的要求，是能跑一条 Python 命令。

### 🛠️ 高手进阶：自己制作一个 skill（7 步完整实例）

技能 = 带清单的确定性函数。三层结构：`SKILL.md`（声明层）+ `tools/`（执行层）+ `data/`（数据层）。

以 `bmi_calc` 为例（15 分钟走完全程，以下代码实测通过）：

**第 1 步 定意图**：BMI=体重÷身高²，同输入必同输出 ✅；医疗相关，伦理边界写死在输出里。

**第 2 步 搭目录**：`bmi_calc/SKILL.md + tools/bmi_calc.py`。

**第 3 步 写 SKILL.md**：

```markdown
---
name: bmi_calc
description: "BMI 计算器：输入身高体重，输出 BMI 与 WHO 分类。
学术参考，健康评估请咨询医师。触发词：BMI、体重指数。"
---
```

**第 4 步 写执行层**（`tools/bmi_calc.py`，纯标准库）：

```python
def calc(height_cm: float, weight_kg: float) -> dict:
    m = height_cm / 100.0
    bmi = round(weight_kg / (m * m), 1)
    cat = ("偏瘦" if bmi < 18.5 else "正常" if bmi < 25
           else "超重" if bmi < 30 else "肥胖")
    return {"bmi": bmi, "category": cat, "note": "（学术参考，健康评估请咨询医师）"}
```

**第 5 步 注册并测试**：

```python
from holoaeon import Kernel
from holoaeon.agent import Agent
k = Kernel()
def bmi_task(task):
    _, h, w = task.replace("帮我算 BMI", "").split()
    return calc(float(h), float(w))
k.skills.register_fn("bmi_calc", bmi_task, description="BMI 计算与分类")
k.register_agent(Agent("health_bot", "health", skill_names=["bmi_calc"]))
print(k.submit("帮我算 BMI 170 65")["results"][0]["output"])
# → {'bmi': 22.5, 'category': '正常', 'note': '（学术参考，健康评估请咨询医师）'}
```

**第 6 步 确定性验收**：`assert calc(170,65) == calc(170,65)`——同输入两次逐字一致。
**第 7 步 多平台部署**：豆包拖上传弹窗 / WorkBuddy 放技能目录 / 纯 HoloAeon 直接用。

> 以上代码实测回执：匹配 ✓、输出 ✓、复跑一致 ✓——**47 个内置技能，每一个都是这样诞生的。**

### 📖 实战案例：一次对话创作 3 万字《燕京医派全派数字分身·全息自述》

| 步骤     | 实际发生的事                                      | 体现的能力                 |
| ------ | ------------------------------------------- | --------------------- |
| 技能索引匹配 | 644 项本地技能索引命中 193 项，精确找到燕京三脉矩阵包（评审 91.5/A+） | 知识资产可检索               |
| 大纲生成   | `outline_gen` 骨架 + 素材融合成 13 单元大纲            | 确定性骨架 + 人工创意          |
| 正文创作   | 3 万字四轮注入，13 处锚点 0 失配                        | 确定性编辑可靠性              |
| 编辑验收   | writing_editor 回执：810 句 / 29,497 字符         | 全程有账可复现               |
| 诚实缺陷   | 自动匹配 2 次误路由，如实记录                            | **不冒充——连接待页都在示范 DNA** |

三个优势：素材定位从小时级降到秒级；合规项按清单自动执行；同链路任何人可复现对账。

### 📚 47 个技能全目录（九大领域包）

| 领域包                 | 技能（能做什么）                                                                                                                       |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **writing 写作**      | `title_brainstorm` 标题风暴｜`outline_gen` 大纲生成｜`word_count` 字数统计｜`readability` 可读性｜`structure_check` 结构检查                          |
| **literature 文献**   | `screen_papers` 文献筛选｜`extract_abstract` 摘要提取｜`normalize_citation` 引文规范｜`dedup_papers` 文献去重｜`reproduce_check` 复现性核查             |
| **research 研究**     | `design_experiment` 实验设计｜`sample_size` 样本量｜`hypothesis_check` 假设检验｜`variables_split` 变量拆分｜`missing_report` 缺失报告                |
| **data 数据**         | `csv_profile` 数据画像｜`normalize_column` 列规范｜`outlier_detect` 离群检测｜`basic_stats` 基础统计                                             |
| **growth 成长**       | `goal_smart` SMART 目标｜`habit_plan` 习惯计划｜`weekly_review` 周复盘｜`task_breakdown` 任务拆解｜`energy_mapping` 精力映射                        |
| **business 商业**     | `business_model_canvas` 商业画布｜`swot_analysis` SWOT｜`kpi_dashboard` KPI 看板｜`risk_register` 风险登记｜`meeting_agenda` 会议议程            |
| **quant 量化**        | `returns` 收益｜`volatility` 波动率｜`sharpe` 夏普｜`drawdown` 回撤｜`backtest` 回测｜`moving_average` 均线                                      |
| **optimization 优化** | `golden_section`｜`gradient_descent`｜`newton_method`｜`conjugate_gradient`｜`simplex_method`｜`penalty_method`｜`genetic_algorithm` |
| **gaoyi 高译**        | `gaoyi_compile` 自然语言编译 HASM｜`gaoyi_exec` 虚拟机执行｜`gaoyi_run` 一键编译运行                                                              |

另有 8 个横切扩展包（sovereignty 查询锻造 / subdistill 知识蒸馏 / omnilife 生活主权 /
omnicore 认知引擎 / metab 治理 / nephron 账本 / uplift 加固 / persona_quartet 代号数字分身）——不占九包口径，只加能力。

### ❓ 出错了看这里

| 症状                 | 药方                                                   |
| ------------------ | ---------------------------------------------------- |
| `python 不是内部或外部命令` | 装 Python 3.8+（老机器选 3.8.10 32 位版），勾选 Add to PATH      |
| 中文乱码               | 终端执行 `chcp 65001`（UTF-8）                             |
| 中文路径报错             | 项目移到纯英文路径，如 `D:\holoaeon`                            |
| 杀毒软件提示             | 零网络零系统写入，源码全可审：`python scripts/redline_scan.py` 自证清白 |

<details>
<summary>同名包冲突排查（pip install 后 import 报错）</summary>

如果 `pip install holoaeon` 后 `import holoaeon` 报错或导入到错误包，可能原因：

1. **PyPI 同名包**：HoloAeon 是本仓专有名，PyPI 上可能有同名占位包。解决：`pip uninstall holoaeon -y` 后 `pip install -e .`（从源码安装本仓）。
2. **PYTHONPATH 污染**：检查 `echo $PYTHONPATH`（Windows PowerShell：`echo $env:PYTHONPATH`），确保没有指向其他同名目录。
3. **缓存残留**：`pip cache purge` 后重装。
4. **验证**：`python -c "import holoaeon; print(holoaeon.__file__)"` 应指向本仓路径。

</details>

---

## 架构总览

```
┌─────────────────────────────────────────────────────────────┐
│                      应用 / 用户 / 对话前端                    │
├─────────────────────────────────────────────────────────────┤
│  领域包  writing · literature · research · data               │
│          growth · business · quant · optimization · gaoyi    │
├─────────────────────────────────────────────────────────────┤
│                        Kernel（门面）                         │
│        submit · collab · choose_agent · tick · health        │
│   冷/热插拔 · 内部融合 · 外部融合                              │
├──────────────┬──────────────────────────────────────────────┤
│  Scheduler   │  Guard（L1–L8）        Memory（三层）          │
│  心跳        │  边界与安全             working/long/archive  │
├──────────────┴──────────────────────────────────────────────┤
│            Adaptive Graph（六边形、赫布）                      │
├─────────────────────────────────────────────────────────────┤
│    Bus（主题/寻址/路由） · Envelope      nephron 认知账本       │
├─────────────────────────────────────────────────────────────┤
│  Agent + Skill Registry   Hypervector Space（HRR）            │
├─────────────────────────────────────────────────────────────┤
│  Actor Cluster（并行）        Model Adapter + bridges（桥）    │
└─────────────────────────────────────────────────────────────┘
```

隐喻→工程映射：心跳=调度 tick｜皮肤=守卫 L1-L8｜经络=语义路由｜细胞骨架=生命周期/持久化｜赫布场=共激活权重自适应｜全息=局部携带全局摘要。**隐喻是修辞，实证是确定性软件。**

> **Guard 层数口径**：L1-L8（8 层）为维度锁冻结的串联守卫（写进 `dimension_lock` D08 旁注，不许动）；L9（产品层路径闸门）与 L10（贝叶斯层）为**附加层**，走 extra_layers 通道，默认 L9 开 / L10 关，不计入 `guard_layers=8` 维度锁。`spec.py` / README / docs 三处描述统一以此口径为准。

## 测试

```bash
python -m unittest discover -s tests    # 34 项单元测试
python -c "from holoaeon.selftest import run_all; print(run_all())"  # 25/25 自检组
python scripts/redline_scan.py          # 红线扫描：零违规
python scripts/measure_a1_a2.py         # A1/A2 宿主侧实测（CI 已挂载）
```

当前状态：**34 单测通过｜自检 25/25 组｜红线扫描零违规（文件数以 
edline_scan 回读为准，当前 82）｜A1 证据哈希 CI 防漂移**；
CI 已在 GitHub 实跑并通过：[run #25](https://github.com/weideyouni/holoaeon/actions/runs/41202167792)
在 Python 3.8 / 3.10 / 3.12 三版本全绿（0 error 0 warning），对应格子见
[`docs/support-matrix.md`](docs/support-matrix.md)。

## 路线图

- **v0.9.1**（当前）——可信度实证加固：版本单一源、证据防漂移、桥 README、CI 挂 A1
- **v0.10**——nephron P1 判定层实现（规格已冻结于 docs/nephron-p1.md）
- **v0.9.2**——第八横切扩展包 persona_quartet（四个代号数字分身 P1–P4：探微/筑基/构弦/持衡，G25，25/25 自检；全链路去人名化，观点带归因标记，仅仿真、不代表原型人物实时观点、需人类专家终审）
- **v1.0**——API 冻结，文档完整，多平台技能包正式分发

## 贡献

欢迎 Issue 与 PR。提交前请确保自检、单测、红线扫描全部通过；PR 模板含"立场自检"五项
（零依赖、确定性、取舍留痕、代价显式、宿主边界）。

## 开源协议

Apache License 2.0。

## 免责声明

本项目中的生物与宇宙词汇均为隐喻，仅描述软件机制，不构成医学、生物学或临床建议。
所有仿真回执均标记 `simulated`；**仿真不等于证明，人类判断始终是最终权威。**

---

## 附录 A · 五地同步（V11）

**口径（重要）**：本页不硬编码"当前 HEAD"，因为任何文档收尾提交都会让 HEAD 变化，写死即自指失效。
下表为 **V11** 时点读数（契约 184、`repo` 以回读为准、`DOC_VERSION 0.9.11`、zip 以回读为准）；HEAD / HF sha / 回执字节每提交一次就变，故一律以右侧命令回读为准。

| 站点 | 检查命令 | V11 基数（以回读为准） |
|---|---|---|
| S1 本地 | `git rev-parse --short HEAD` | 以回读为准（内容提交先落，清单随后重建） |
| S2 Gitee | `git ls-remote <gitee> refs/heads/main` | 与本地 HEAD 同值（推送后回读） |
| S3 GitHub | `git ls-remote origin refs/heads/main`（延时 12-20 s 回读） | 同上；三值一致 |
| S4 向量海 | `python scripts/build_vector_sea_manifest.py` | 以 `check()` 的 `entries` / `sums_74_in_sync` 回读为准（下一批新号段以 V11 回执为准） |
| S5 Hugging Face | `python scripts/mirror_hf.py --base <old> --head <new>` | 以输出 `sha` 与 `mismatch=[]` 回读为准（与 `git ls-files` 同集；`sha` 以回读为准） |
| 回执 | `python scripts/five_site_dna.py preflight` | `files` / `history` / 字节数以回读为准 |
| 交付 zip | `python scripts/build_b9_zip.py` | 以回读为准 |

**HEAD sha、HF sha、回执字节与 history 条数每提交一次就会变**，本页故意不写死；
读取方式：`git rev-parse --short HEAD`、`mirror_hf.py` 输出的 `sha`、`five_site_dna.py preflight` 的回执路径。

同步纪律（写序不能颠倒）：

1. 先跑会写回执的校验器（`verify_v44/v45/v46/v5`；`verify_v44` 首跑必 11/13，第二次 13/13）→
2. 再建 `SHA256SUMS` / `dual_repo_sums` → 3) 再打确定性 zip → 4) 再建 `five_site_manifest` →
5) 迭代到 zip `sha16` 两次一致（不动点）→ 6) 最后只跑只读校验（`five_site verify` / `preflight` / `unittest` / `v3_gate` / `redline` / `dimension_lock`）。

向量海归档顺序为「先 copy 新件 → 再替换 `74_SHA256SUMS` → 最后 `listdir` 建 `manifest`」；
顺序颠倒会让 `74` 进清单并自指，首次实测即红。回执 `files` 与 `files_count` 必须同源取自 manifest。

---

## 附录 B · 版本升级说明（V3 → V11）

> 口径：sha 取自 `git log` 实测；条目数 / 字节 / `sha16` 以对应批次命令回读为准，不硬编码猜测值。

| 阶段 | 提交 | 主题与产出 |
|---|---|---|
| V3 收口 | `3d359bd` / `32b2667` | LangChain 工程形态旁挂（W12–W19），32/32 门禁，维度不变 |
| 同步基建 | `92fd8b5` / `dfad361` | 五地同步 DNA V1.0→V1.1（G1–G8 + P1–P6），离线哈希校验器 |
| V4.0 开场 | `80089b6` | 冷热插拔升级：第 10 个附加包，**25/47/9 不变** |
| B0–B9 | `055d202` … `c03b19d` | 基线冻结 → 契约 v1 → 六机制映射 → 1229 技能四标签 → 20 例试点 → 语义族 60 → 赫布落盘 → 准入闸 15/15 → 双仓同步 → 五件交付 + 确定性 zip |
| V2.1 | `3b0b32b` | ivsa 只读对账 R1–R7，旁挂 92 → 101 |
| V4.3 | `4f06bc8` / `3d6f956` | 四坑固化（HF model 仓 / 中文路径 / 74→manifest 顺序 / 交付漂移）+ 11/11 |
| V4.4 | `b85b293` | 19 家 provider 目录 + 5 协议拼装、默认全关；A1–A13 13/13 |
| V4.5 | `fb5cdef` / `f0f1bb5` | 真实回环调用：embeddings 200 / 768 维；chat 200 / 41+29 tokens（C 盘 `lms import` 修复） |
| V4.6 | `f0f1bb5` / `978dc10` / `6646315` | 12 卡槽 + 协作指南；C1–C9 9/9；卡槽实数勘误 14→12 |
| V5.0 | `aa88c37` | 康复域知识库全量入库（14 条登记 / ivsa 300 行）；影子维度 D_REHAB 不入锁；`EXT-EVIDENCE-01` 解封而 tier 不变；D1–D10 11/11 |
| V5.0 收尾 | `f214bd5` | 中英文首页同构重排：去陈旧大段引用，改「当前工程状态」表 + 文末两附录；首页纳入 `REPO_FILES`（152 → 154）；`06` 第五节交付表按实测重算 |
| V5.1 设计语汇 | `339d0c4` / `9b2d5d1` | Impeccable 范式本地化：`holoaeon/design_vocab/`（24 命令 / 12 规则 / 3 编译模式 / 4 通道）+ `data/design_vocab_registry.json` + 门禁 `dv 8/8` + 契约测试 8 条（`旁挂 160 → 168`）；**25/47/9 与 12 卡槽均未变** |
| V5.2 代码修正 | 本批提交（用 `git log -1 --format=%h` 回读，避免自指） | 门禁自指修复（A10 兄弟回执排除 + A11 断传染 + skipped 第三态 + 路径去硬编码）、句柄泄漏清零（scripts 回读 0）、CI 补契约/维度锁/设计语汇三道闸、Guard L3 归一化与兜底开关保守版；`diff0` 仍 `2fc892cf9af6e755`，**25/47/9 未变** |
| V6.0 族级登记与路由第三态 | 本批提交（用 `git log -1 --format=%h` 回读，避免自指） | 句柄清零到底（全仓回读 0，补 `tests_contract/` 6 处 + `skills/` 4 处）、`FORBIDDEN_NESTED_OPEN` 资源红线、`no_agent_matched` 第三态 + `degraded` 标记、两开关进 `HoloAeonConfig`、`.env` 误伤收紧（[golden]，`diff0` 未漂移）、**1229 条 → 58 族登记 + 桥接 `external_skill_registry`**（`旁挂 168 → 180`）；`DOC_VERSION 0.9.3 → 0.9.5`，**25/47/9 未变** |
| V6.1-B3 同步卫生 | 本批提交（`git log -1 --format=%h` 回读） | 附录 A 基数改 V6.1 终态并修锚点；记录向量海下一批新号段从 `182` 起；HF 删 10 个非 git 孤儿并补传 `contract_v1_interop_a/b.json`，文件集 `466 → 458` 与 git 跟踪集同集；`DOC_VERSION 0.9.6 → 0.9.7`，**25/47/9 未变** |
| V6.1 纪律固化与 A10 派生 | 本批提交（`git log -1 --format=%h` 回读） | A10 自写回执改 `REPO_FILES` 派生（`self_derive=derived`）、`repo:missing:` 不豁免、排除项记 owner + 前后 sha16 差分证据；批次升级八步写序与五地同步写成 `docs/工程纪律_批次升级与五地同步.md` 并固化为技能 `holoaeon-batch-upgrade-discipline`；`01`/`06` 追加 V6 章节（zip 指纹随之变化，以 `build_b9_zip.py` 回读为准）；`DOC_VERSION 0.9.5 → 0.9.6`，**25/47/9 未变** |
| V8 批2-4 融合升级 | `2fc1faf` / `4bf84df` | L9 路径闸门（`product_layer_guard`）+ 产品层三件套（frontend_adapter / demo_product / install）+ TCM 旗舰包（`tcm_rehab` 第 11 扩展包）+ 领域化解耦；`DOC_VERSION 0.9.8 → 0.9.9` |
| V9 拓扑共振包 | 本批提交（`git log -1 --format=%h` 回读） | `topology_resonance_pack.py`（8 基础数学 + 6 四人组技能）；`EXTRA_PACK_ORDER` 11→**12**；`DOC_VERSION 0.9.9 → 0.9.10` |
| V11 城邦架构融合 | 本批提交（`git log -1 --format=%h` 回读） | 3 Graph 函数 + Guard L10 贝叶斯层 + 新建 `topology_runtime.py` + 2 治理技能（skills 14→16）+ `DOC_VERSION 0.9.10 → 0.9.11`；selftest 25/25 · `diff0` 未漂移 |

**一句话主线**：每批只做一件事，只加旁挂、不改锁数；每批必带判据、票据与五地同步，`drift=[]` 才允许提交。

Seal: 潮起开门，潮落闭嘴 · `evidence_class=simulated`（仿真 ≠ 证明，碳基终裁）
