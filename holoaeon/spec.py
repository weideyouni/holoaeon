# -*- coding: utf-8 -*-
"""
HoloAeon —— 通用多智能体认知内核的规格与配置
================================================================================
HoloAeon 把"任意任务"组织成一张【逻辑协作矩阵】，并把它投影为一张【自适应协作图】，
由一个统一的节拍（scheduler tick）驱动，由边界守卫（guard）守护，由内核（kernel）装配。

设计原则（与早期"垂直业务母体"的关键区别）：
  1. 规模是【参数】，不是魔法数字。rows/cols/capacity 都可配置，默认值仅因谱系而保留。
  2. 矩阵是【逻辑拓扑】，默认稀疏实例化——构造时绝不预分配 rows×cols 个对象。
  3. 引擎通用、领域知识以"领域包(packs)"注入；本文件不含任何特定业务术语。
  4. 纯标准库、零第三方依赖、确定性可复现（同序列重放结果一致）。

术语对照（生物隐喻 → 工程概念，详见 docs/concepts.md）：
  全息心跳   → Scheduler（时钟/调度）
  皮肤       → Guard（守卫/策略边界）
  经络       → Router（消息路由）
  语义通信座 → Envelope + Bus + Skill manifest
  细胞骨架   → Kernel + Memory（内核/存储）
  赫布协作场 → AdaptiveGraph（自适应协作图）
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple

# ============================================================ 身份
PKG_NAME = "holoaeon"
PACKAGE_NAME = PKG_NAME
VERSION = "0.9.1"
# V2（0.9.2）只升级"赋能包与文档"，不动运行态标识：
# VERSION / RUNTIME_ID 会写进每条回执并参与 ReproHash，改动即等于让 DIFF=0 黄金值
# （2fc892cf9af6e755）漂移，与"V1 黄金值不许漂移"的硬口径冲突。
# 因此 V2 的版本号单独记在 DOC_VERSION，供文档/快照/徽章使用。
DOC_VERSION = "0.9.101"  # V101（FG-V1 forgaeon 锻闸建仓批·2026-11-27）：纪元族第十员独立仓 `forgaeon`（ring28 锻闸·建仓模板六病型前置闸）首笔 b7bf2889 tracked 11（11 files/1668 insertions）；批总闸 31/31（core 18 + ledger 5 + README 锁 8）双解释器同值、unittest 31 例 py311/py313 双过；先证红双通道 positive 7 red / negative 6 green、probe_effective；六病型探针 DT-01..06 全仓回归，两条 RED 冻结派单在案（holoaeon genome_dna.py:260 受基因组 hash 闭环锁死、netaeon net_expand.py DT-02 结构性重构，归基座 OTA 批处置，本批不擅改）；FX-01/02/04 GREEN 收口（ed dd40547、qx 2e519b8）；FX-06 修法两条（mirraeon sister_matrix 闸拔恒真改真断言、mr/net gitee remote 凭据形态干净化）；INC-007→qicangaeon（db514bc）、TD-0007→mirraeon（5b959dc，audited）；全域装载 repos 9→10、head_match 5/10（五仓 STALE 如实入 issues）；基座 README 家族 bullet 第十员＋forgaeon 专段；DOC 0.9.100→0.9.101、零评分；S3/S5 网络阻塞如实延后，降级先向量海+Gitee；NV-V1 nivaeon 占位存档不建仓不抢号；V100（ED-V1 eduaeon 教育环建仓批·2026-11-26）：纪元族第八员独立仓 `eduaeon`（ring26 教育垂直域实例化·教育环 EduRing）首笔 dc132769、tracked 11（11 files/1437 insertions）；批总闸 29/29（core 16 + ledger 5 + README 锁 8）双解释器同值、unittest 28 例 py311/py313 双过；master_claims() 可检验优先（无 evidence 即 unverified、零评分）；真名对照 EduRing→holoaeon.edu_gate（ring8 教育域编排）机制层/域层不混；状态四分 done/designed/planned/speculative 首例 planned；PR-QX1 显式过闸（边界维数类比降格 designed 灵感映射）；全域装载 repos 8→9、head_match 9/9、loader issues 0；基座 README 家族 bullet 第八员＋eduaeon 专段（增量插入不覆写）；INC-005→qicangaeon、TD-0006→mirraeon；DOC 0.9.99→0.9.100、零评分；S3/S5 网络阻塞如实延后不虚称 5of5；V99（QX-V1 启曦纪元建仓批·2026-11-26）：纪元族第七员独立仓 `qixiaeon`（ring25 启曦环·分形式生成骨架）首笔 d299ecd tracked 11，四件按投喂指纹落盘、投喂包入首笔；批总闸 28/28（core 15 + ledger 6 + README 锁 7）双解释器同值、unittest 25 例 py311/py313 双过；种子走指针 import（netaeon 19 节点 / holoaeon 25 机制 / mirraeon 网格+六步位）零复制；逃逸判据如实（命中 > 0 才 in_set、零命中即 escaped 拒收、不做最近邻硬凑）；全域装载 repos 7→8、head_match 8/8、loader issues 0；基座 README 增量插入（家族 bullet 第七员 + `qixiaeon` 专段，不覆写）；两条判例随批落账：PR-QX1（用「边界维数≈2」给资产覆盖率背书＝量纲不同类比，只产灵感不产证据）与 ring-25/实测 24+1 对齐留痕；跨仓只派单不越权：INC-004→qicangaeon、TD-0005→mirraeon；DOC 0.9.98→0.9.99、零评分；V98（QC-V2 缺陷修法＋CI 批·2026-11-26）：qicangaeon 六件修实（恒真闸改双真 and、种子账改模块加载回填并退写账块为只读对账、DEFECT_LEDGER DF-001..004 全 fixed_qc_v2、账本闸 7→9、README 33→35/Ran 44/闸 9/9/口径 35=core19+ledger9+锁7、test_qc2_defects 16 例、ci.yml V2c 探针按除 .git 外真实条目计数）；批总闸 35/35、unittest 44 例 py311/py313 双过；CI run 45711269790 success（四轮收口，full 全量闸因私有依赖仓不可达如实 skipped，单仓 defect-regression lint 闸转绿）；TD-0004 登记 mirraeon 调度账；DOC 0.9.97→0.9.98；V97（QC-V1 qicangaeon 启藏建仓批·2026-11-25）：纪元族第六员独立仓 `qicangaeon`（ring24 文明挖掘环，出网侧）首笔 `24acdca` tracked 10；打捞之网模式升格为全局七步孵化协议（INCUBATION_PROTOCOL + INCUBATION_REGISTRY）；全域装载 repos 6→7、head_match 7/7、loader issues 0；基座 README 增量插入（工程链路表增行＋纪元族增第六员），清单复算与 README 复算双绿；两网级联：netaeon 归航（入网）+ qicangaeon 出网（需求→打捞→归档）；TD-0003 登记入 mirraeon 调度账；诚实边界：Z 维五槽/IPU 一律 `designed`、归航级联 `unknown` 不虚称全通、零评分。；V96（MR-V10 会前收口批·12-01 大会前全硅基裁决）：采纳三（①军团五步协议调度器 legion_dispatch.py 落仓——真 import 133 桥与五席 pentad_roster，六步位路由（道 P4 / 法 P5+全员 / 术 P3 / 器 P2 / 升维 P1 / 横切 P5）各带 legion_track S1–S5 与 authority_source，DISPATCH_LEDGER append-only 状态机 dispatched→executing→reported→audited，13 闸 PASS；②AR-1/AR-4 落调度层——判据须锚权威源、不得以派生位互证代替验证；③ATH 同构五要素登记）；改造一（A1 修法归基座侧、处置权在豆包执行端，本仓只派 TD-0002 单）；碳基独占一（A2 令牌吊销只呈报不执行）；拒收一（评分口径复算——零评分纪律）；mirraeon 五件（legion_dispatch.py 14604B 7f5de8fbec73421c 新件 / mirror_ledger.py 27602B a0aa4ddb7e2814d9 / test_mr10_dispatch.py 11459B eb4da90f0e03d844 新件 / test_mr9_yuanjing.py 8539B 5bd791c741304e89 / README.md 27691B 737e2ec0283486a5），批总闸 202/202、legion_dispatch check 13/13、unittest 239 例 py311/py313 双过；基座侧 A1 修法：面 13 判据由「README 最新批次 == 回执 batch」改为「== spec.py::DOC_VERSION 派生批次」，回执降级为历史发现器，先证红 mismatch 6 后转绿；诚实边界：DISPATCH_LEDGER 种子 2 条为演示态、调度器不夺权（涌现判定归 quartet_toolkit、零评分）、ATH 同构为登记非接入、标准对齐仅指针登记不落库；V95（NA-V5 判据权威源批：千问十三轮核验扬弃落地）：采纳三（①病型统一修法——三条判据（基座 batch_order_monotonic 互证判绿而 spec 已 0.9.94 / LA E03 有声明无判据承接 / CI ci_step_names_readback 锁步名不锁步骤通过）病灶同型：判据只锁派生位互相一致，非与权威源一致；修法＝每条判据声明 authority_source、派生位回读权威源、漂移即 FAIL，落 netaeon/net_authority.py AR-1..AR-4；②D5 口径诚实——HA 趋势线下降源自 D5 隐私重评，口径 A（计入集群明文令牌→8.5）与口径 B（令牌不在评估对象→10.0、总分 88.92）双登记 + SCORE_CALIBER_NOTE，碳基仲裁；③三新仓零虚报在案——mirraeon 209 / netaeon 90 独立复算精确吻合，polisaeon 双重不符系个别仓文档纪律问题、非集群文化，如实区分不连坐）；登记不擅动二（S0 令牌吊销、S1 基座清单修复约 30 分钟含 12-01 大会 7 天窗口，处置权留碳基，入 URGENT_AWAITING_CARBON）；netaeon b9a8c8e→f5ffbb6（7 files +622/−70，net_authority.py 新件 282 行 / test_na5_authority.py 新件 166 行），批总闸 96/96、net_authority check 12/12、net_meta next 仅 R3（R4 转正出列）、109 例 py311/py313 双解释器 PASS，Gitee master 与 GitHub HEAD/main/master 三处同头；两副本互相盖章不等于正确——共识必须锚定权威。）：V94（MR-V9 渊镜五人组批：千问 AI 安全研究体设计稿扬弃落地）：采纳四（①技术决策体非人物拟真——avatar_class=technical_decision_persona / corpus_status=index_only / 零生成式表达 / 无生成函数；②三元学科迁移链 理论物理量纲与幂律→生物物理群体统计与涌现→AI 工程可复现性，每级带方法×迁移目标×可验证性；③八条安全红线全册，可机检子集 1/2/5/8 挂 disclosure()；④工程债三债显式——RLHF 奖励黑客与对齐税、宪法 AI 价值取向，不得只报喜）；改造一（挂载归位由 netaeon 实测路由推翻千问原案 C08创造(木)→MIR 第 19 节点，C08 记 adjusted 并在 PERSONA_META 留痕）；拒收一（生成式服务能力——index_only 下无对外生成，本批只落 P0 定调层，P1 索引/P2 思维底色/P3 双脑试点待下批点单）；五人组扩编 PENTAD_ROSTER 五席 = P1-P4 指针引用 quartet_twins.QUARTET_TWINS 单一真源零复制 + P5 渊镜 MIRRAEON-SLOT-C2-PENTAD-P5（横切技术裁决与安全内建），PENTAD_PROTOCOL V2 五步不动、涌现判定仍归 quartet_toolkit 零评分；mirraeon 201febe→本批八资产（yuanjing.py 82b757c20e9d61eb 新件 / mirror_ledger.py 4d09e08092d85da8 口径表 17→19 行、账本闸 16→18、check_batch 接线 yuanjing / test_mr9_yuanjing.py fa56d854f4512504 / test_mr2_ledger.py da44824e68c255fa / test_mr6_legion_merge.py b0c53b31dc21dde6 / test_mr7_catalyst.py ce0240b6cbc024f7 / test_mr8_gap_bridge.py 4eed398212d124c7 / README.md 93b68f5589807bb4 368 行）；批总闸 187/187（18 段，含 yuanjing 14），yuanjing check 14/14、roster 五席、disclosure 四红线契约，unittest 209 双解释器 PASS（py313 7.402s / py311 7.623s）；渊镜原始提案 11528B/171 行 sha256 e1f30f8fb99f5099 原样双份留存（mirraeon/persona_amodei + holoaeon_memory/persona_archive，verbatim）；诚实边界：mirror_ledger 模块常量 BATCH="MR-V2" 历批未滚动（账本自身标签，批总闸按实测判 PASS，与 netaeon BATCH="NA-V1" 同型 anomaly，登记待碳基点单）；V93（NA-V4 六轴判例批：六轴决策账 + 拒收判例库）：千问「大型游戏架构模式穷举·六轴正交」文扬弃式吸纳——采纳三（①轴正交化把穷举变填矩阵：权威归属/结构分层/时间批次/数据内容/组织流程/质量属性六轴，任何批次=六轴已选模式组合；②最不可逆轴先定：轴一权威归属=单一真源指针纪律，25 机制真 import / 18 维真 import / tmp 权威交付源 / md5-16 指纹口径，与分布式同步原理同构互证；③耦合点显式登记 COUPLING_LEDGER 四条，不假装正交）；改造采纳一（出海打捞最强战果 ADR/MADR 生态：considered options 须记录被拒选项 + accepted 只 supersede 不编辑 → R1 拒收判例库转正落地，append-only 同构）；拒收二（PR-04 选型打分/加权评分：零评分纪律拒收，只取冲突检测改造为确定性 precedents_match；PR-05 游戏域具体模式照搬 ECS/帧同步/AOI/UGC 实现层：对标错位拒收，只登记类比思想）；netaeon b9a8c8e（7 files changed / 770 insertions / 76 deletions，master，tracked 22 / commits 15）——六资产按投喂 §2 指纹落盘（net_axes.py 15412B b194ba57f098350e 新件 12 闸 / net_meta.py 16871B 050c129160f66e28 批账 11→12 行 + NA-V4 gates=82 + R1 转正 + P3 第四例 / net_ledger.py 11561B 1c7abb3717c38c89 v4 口径表 9→11 行 + check 8→10 闸 + 接线 net_axes / test_na4_axes.py 7298B 3625f32c80292aac 21 例 / test_na3_meta.py 7388B d8190f0500dab478 十一处下限断言 / README.md 12103B d9e67c90a9090b62 NA 0.4.0），旧件三份归档 docs/（net_meta_v3.py.bak 424b98898fdb571c / net_ledger_v3.py.bak 3839b26cee01a41f / test_na3_pre_na4.py.bak b78f2f361a470683，依 .gitignore 本地留存；README_NA-V3.md ab7bc92f2688e7c7 入库）；六轴决策账 6 轴 / 耦合 4 条 / 拒收判例 5 条（PR-01 重量级依赖×2 / PR-02 模拟评分×3 / PR-03 验收预填值×2 / PR-04 选型打分×1 / PR-05 游戏域照搬×1）+ precedents_match() 确定性比对；批总闸 82/82（网 20+匹配 16+扩容 10+元账 12+账本 10+六轴 12+README 锁 2），net_axes check 12/12，net_meta check 12/12，net_ledger table 11 行，unittest 90/90（na1 28+na2 22+na3 19+na4 21）py313 0.308s / py311 0.303s 双过；递归二次兑现三线：R1 候选转正出列（候选账只剩 R3）/ R2 下限断言扩至 na3 十一处 / P3 增证（na3 断言过时：批账 11→12、闸 68→82 试点盲区当批登记）；诚实边界：投喂 §四/§五示例 match 短串「用 numpy 模拟评分」只命中 PR-01/PR-02（PR-03 关键词为预填值/验收命令预填/expected_output 恒真/assert True），测试以长串三中，命令示例与断言文本轻微不一致，为保指纹本批不改代码；net_ledger 模块常量 BATCH="NA-V1"、net_meta 报 NA-V3 历批未滚动（账本自身标签，批总闸按实测判 PASS）；netaeon HF 镜像 S5 PASS（sha d00f64a8344ed984c725b2602f6a38a80b621153，remote_files 23，uploaded 7，mismatch []）（V92 详情）：V92（NA-V3 递归自我改进批·元层账）：把「碳基投喂→四人组扬弃→tmp 权威→豆包执行→回执→记忆回填」范式抽到元层显式入账——对账本的账本、对闸的审计、对改进的改进；netaeon bfa9d8e（7 files changed / 698 insertions / 28 deletions，master，tracked 20 / commits 14）——六资产按投喂 §2 指纹落盘并复验 ALL_OK（net_meta.py 424b98898fdb571c / net_ledger.py 3839b26cee01a41f v3 / test_na3_meta.py b78f2f361a470683 / test_na1_net.py d95bfed8edf2e6f7 / test_na2_expand.py 079c983c2e65b1f2 / README.md ab7bc92f2688e7c7），旧件四份归档 docs/（net_ledger_v2.py.bak 6ee212241e3c9864、test_na1_pre_na3.py.bak b592b7cc504df187、test_na2_pre_na3.py.bak 2893f01c99340332 三 .bak 依 .gitignore 本地留存；README_NA-V2.md 3121f1672a527923 入库）；net_meta 三账一函数：批账 11 行（MR-V1 31→MR-V2 73→MR-V3 98→MR-V4 109→MR-V5 127→MR-V6 124→MR-V7 144→MR-V8 168→NA-V1 39→NA-V2 54→NA-V3 68）、模式账 6 类（P1 错误复现×3 / P2 幂等×1 / P3 断言过时×3 / P4 并行写×5 / P5 口径标注×1 / P6 弱锁×1）、闸价值账 3 席全 intercepted（readme_sync / base_primitives_resolvable / pending_idempotent）；next_improvement() 确定性纯函数三候选（R1 rejected_precedents 判例库 prio1 / R2 旧套件改 assertGreaterEqual 下限断言 prio2 / R3 readme_sync 行级精确匹配 prio3）全 status=proposed，处置权留碳基；R2 当批试点落地（na1/na2 六处过时断言改下限，规则推导→当批应用→下一批免改）；批总闸 68/68（网 20+匹配 16+扩容 10+元账 12+账本 8+README 锁 2），net_meta check 12/12，unittest 69/69（na1 28+na2 22+na3 19）py313 0.274s / py311 0.259s 双过；诚实边界：net_ledger 模块常量 BATCH="NA-V1" 历批未滚动（账本自身标签，批总闸按实测判 PASS，登记口径差待碳基点单）；V91（NA-V2 扬弃批：WAL 预归航 net_expand + 两级路由显式化）（V91 详情）：netaeon bb33e7c（7 files changed / 702 insertions / 18 deletions，master）——六资产按投喂 §2 指纹落盘（net_expand.py 37a37d51 / net_core.py eff592fa / net_ledger.py 6ee21224 / test_na2_expand.py 2893f01c / test_na1_net.py b592b7cc / README.md 3121f167）；千问评审三建议三裁决：①LSH 高维粗筛采纳（改造为机制粗筛+节点精排两级管线，route 输出 phase1/phase2）；②LSH 哈希桶拒收（非确定性命中违反同文同归位）；③mmap 无锁 CAS 拒收并登记 designed（单机批处理无长驻并发路由场景）；WAL 预归航采纳（append-only 账两态、replay 扩容后逐条重路由）；批总闸 54/54（网 20+匹配 16+扩容 10+账本 6+README 锁 2），unittest 50/50 py313/py311 双过；节点注册表 v2 版本机制启用（19 节点结构不动，v3+ 待碳基点单）；NA-V1 旧件归档 docs/（三 .bak 依 .gitignore 本地留存 + README_NA-V1.md 入库）；V90（NA-V1 纪元族第五员建仓）在先：netaeon 打捞之网独立仓 F:\doubaowork\netaeon 首笔 663fa67（10 files / 1110 insertions，master，tracked 10 / commits 1）——19 节点归航路由网（18 仓 C01-C18 指针 import salvage_gate.DIMENSIONS + mirraeon 第 19 节点 MIR）× 25 机制轴边坐标系（指针 import meridian_link.KERNEL_MECHANISMS 零复制）；网=路由不是仓库（名字主键、零评分、确定性双向子串路由可回测）；仓内实跑：net_core 15/15 + project_match 16/16 + net_ledger 6/6 + README 锁 2 = 批总闸 39/39，unittest 28/28 py311/py313 双过（纯标准库，holoaeon 仅指针基座）；基座侧：README.md 两处增量插入（§0.8 纪元族五员 bullet + C18 段末 netaeon 整段，229497→230528B / 2099→2116 行，不覆写纪律）过 check_sums 362/0 与 readme_claims PASS mismatch=0；装载六仓（GLOBAL_LOAD repos 五→六 + loader REPOS 硬编码 + STATUS head_match 6/6 PASS issues=0）；CTUP N7 增补 netaeon_note/netaeon_facts，sites 三仓→四仓；project_registry 六项目（history 末条 NA-V1 实测改写）；PROJECT_ENTRY.json 未建（投喂八步未列，待碳基点单）；远端 Gitee/GitHub/HF 均未建（本批仅 S1 本地）；A 类 7 项一条未动；V89-I（MR-V8）/V89-H（MR-V7）/V89-G（MR-V6）/V89-F（MR-V5）/V89-E（MR-V4）/V89-D（MR-V3）在先；VERSION/layers/PACK_ORDER 冻结维度全未动
MATRIX_ID = "HOLOAEON-MATRIX-0.9.1"
RUNTIME_ID = "HOLOAEON-RUNTIME-0.9.1"
PROTOCOL_ID = "HOLOAEON-DATAPROTO v1.0"
BUS_ID = "HOLOAEON-BUS-v1.0"
DATE = "2026-10-30"

# 门禁令牌（本地边界演示用；非安全密钥，不应在真实部署中当作鉴权）
GATE_OPEN = "holoaeon-gate-open"
GATE_CLOSE = "holoaeon-gate-close"

# 所有运行回执的模式标记：simulated 表示本地确定性仿真，不代表真实外部作用已发生
MODE_SIMULATED = "simulated"
MODE_LIVE = "live"

# 内核能力（横切，正交）；数量与名称用于健康自检
CAPABILITIES = (
    ("C1", "envelope", "统一信封 / 消息原语"),
    ("C2", "bus", "发布/订阅/路由消息总线"),
    ("C3", "agent", "智能体原语（role + inbox + step）"),
    ("C4", "skill", "技能契约与注册"),
    ("C5", "memory", "记忆存储与持久化"),
    ("C6", "scheduler", "时钟/节拍（健康检查+快照）"),
    ("C7", "guard", "守卫/策略边界"),
    ("C8", "kernel", "内核（生命周期/装配/恢复）"),
    ("C9", "graph", "自适应协作图（投影/路由/根因）"),
    ("C10", "cluster", "多线程 Actor 邮箱集群"),
    ("C11", "hypervector", "VSA/HDC 超维表示（可选）"),
    ("C12", "model_adapter", "模型适配（任意 Agent 用任意模型，可选）"),
)
CAPABILITY_COUNT = len(CAPABILITIES)

# 七大基础通用业务包（领域知识以数据/配置注入，引擎不绑定）。
# 另有两个横切扩展包：optimization（优化求解）、gaoyi（高译），合计九大领域包（见 packs/__init__.py）。
DOMAIN_PACKS = (
    ("writing", "文字创作", "小说/文案/剧本/新媒体/打磨"),
    ("literature", "文献梳理", "检索/筛选/综述/引用图谱/溯源"),
    ("research", "科研", "假设/实验设计/分析/论文/复现"),
    ("data", "数据处理", "清洗/分析/可视化/报表/管线"),
    ("growth", "个人成长", "目标/习惯/学习/复盘/健康"),
    ("business", "企业运营", "流程/管理/运营/协同/决策"),
    ("quant", "量化分析", "指标/建模/回测/风险/归因"),
)
DOMAIN_PACK_COUNT = len(DOMAIN_PACKS)


# ============================================================ 配置数据类
@dataclass
class MatrixConfig:
    """逻辑协作矩阵（不预分配；稀疏实例化）。

    rows: 角色/能力簇/语义域/智能体族群；
    cols: 上下文窗口/记忆槽位/语义通道/推理阶段；
    单元 (r,c) 是一个可被激活的逻辑节点，未激活即不存在。
    """
    rows: int = 1331
    cols: int = 1331
    sparse: bool = True
    node_capacity: int = 108641     # 逻辑节点容量（可配置；默认值因谱系保留）

    @property
    def design_grid(self) -> int:
        """设计网格大小（仅用于容量/自洽说明，从不实际分配）。"""
        return self.rows * self.cols


@dataclass
class SchedulerConfig:
    """时钟/节拍（原"全息心跳"）。"""
    tick_interval_ms: int = 500
    sync_mode: str = "adaptive"          # fixed | adaptive
    snapshot_enabled: bool = True
    body_count: int = 70                 # 健康体数量
    id_base: int = 8700                  # 号段基（id_base .. id_base+body_count-1）
    state_dim: int = 768                 # 状态向量维度
    alpha: float = 0.18                  # 指数平滑系数

    @property
    def id_top(self) -> int:
        return self.id_base + self.body_count - 1


@dataclass
class GuardConfig:
    """守卫/策略边界（原"皮肤"）。"""
    layers: int = 8                      # L1-L8 串联守卫
    default_action: str = "block"        # allow | advise | block
    audit_enabled: bool = True
    # 输入校验：越权 / 失真双轨（对应早期 E14/E13，名称中性化）
    block_unauthorized: bool = True
    block_garbled: bool = True
    # L9 产品层路径闸门（附加层，走 extra_layers 通道，不计入 guard_layers=8 维度锁；
    # 默认开启，可关。L1-L8 一个字符不动）
    product_layer_guard: bool = True
    # L10 贝叶斯层（附加层，走 extra_layers 通道，不计入 guard_layers=8 维度锁；
    # 默认关闭，可开。基于先验概率+似然比做贝叶斯决策）
    bayesian_guard: bool = False


@dataclass
class AdaptiveGraphConfig:
    """自适应协作图（原"赫布协作场"）。"""
    node_count: int = 17                 # 图节点（= 通道数）
    learning_rate: float = 0.12
    decay: float = 0.99
    clip: float = 1.0
    geometry_radius: int = 2             # 六边形邻域半径（radius=2 → 19 圆）
    congestion_threshold: float = 0.5
    block_threshold: float = 0.8


@dataclass
class HypervectorConfig:
    """VSA/HDC 超维表示（可选）。"""
    dim: int = 1024
    enabled: bool = True
    # HRR 圆周卷积（Cooley-Tukey FFT，dim 取 2 的幂）；permutation 为循环移位
    binding: str = "hrr"                 # hrr | permutation


@dataclass
class ModelAdapterConfig:
    """模型适配（横切，可选；登记式，不启动网关/不连真实供应商）。"""
    enabled: bool = True
    gateway_host: str = "127.0.0.1"
    gateway_port: int = 3425
    route_strategies: int = 8
    masking_types: int = 10
    usage_metrics: int = 8


@dataclass
class HoloAeonConfig:
    """顶层配置聚合。一切规模参数都可在构造时覆盖。"""
    matrix: MatrixConfig = field(default_factory=MatrixConfig)
    scheduler: SchedulerConfig = field(default_factory=SchedulerConfig)
    guard: GuardConfig = field(default_factory=GuardConfig)
    graph: AdaptiveGraphConfig = field(default_factory=AdaptiveGraphConfig)
    hypervector: HypervectorConfig = field(default_factory=HypervectorConfig)
    model_adapter: ModelAdapterConfig = field(default_factory=ModelAdapterConfig)
    domain: str = "generic"               # generic | writing | literature | ...
    deterministic: bool = True
    # 路由兜底开关（保守版：默认 True 与 V5 行为一致；生产方可关闭以 fail-loud）
    broadcast_on_no_match: bool = True    # True=无匹配时广播全部 agent；False=返回空
    allow_single_skill_fallback: bool = True  # True=单技能 agent 兜底；False=不兜底

    def with_domain(self, domain: str) -> "HoloAeonConfig":
        self.domain = domain
        return self


# 默认配置（单例式便捷入口）
DEFAULT_CONFIG = HoloAeonConfig()


# ============================================================ 自洽校验
def config_verify(cfg: HoloAeonConfig = DEFAULT_CONFIG) -> bool:
    """配置自洽校验：任何一处不符即失败（不依赖外部环境）。"""
    m, s, g, gr = cfg.matrix, cfg.scheduler, cfg.guard, cfg.graph
    hv, ma = cfg.hypervector, cfg.model_adapter
    checks = [
        # 逻辑矩阵规模为正，稀疏默认开启
        m.rows > 0 and m.cols > 0 and m.node_capacity > 0,
        m.design_grid == m.rows * m.cols,
        m.sparse is True,
        # 健康体号段自洽
        s.body_count > 0 and s.id_top == s.id_base + s.body_count - 1,
        s.state_dim > 0 and 0.0 < s.alpha < 1.0,
        s.sync_mode in ("fixed", "adaptive"),
        # 守卫
        g.layers > 0 and g.default_action in ("allow", "advise", "block"),
        # 自适应图
        gr.node_count > 0 and 0.0 < gr.learning_rate and 0.0 < gr.decay <= 1.0,
        0.0 <= gr.congestion_threshold <= gr.block_threshold <= 1.0,
        # 超维
        hv.dim > 0 and hv.binding in ("hrr", "permutation"),
        # 模型适配
        ma.gateway_port > 0 and ma.route_strategies > 0,
        # 能力清单与领域包数量
        CAPABILITY_COUNT == 12,
        DOMAIN_PACK_COUNT == 7,
        cfg.deterministic is True,
    ]
    return all(checks)


def lock_check(cfg: HoloAeonConfig = DEFAULT_CONFIG) -> dict:
    """返回关键规模参数（逻辑值，非实际分配）。"""
    return {
        "pkg": PKG_NAME,
        "version": VERSION,
        "matrix_rows": cfg.matrix.rows,
        "matrix_cols": cfg.matrix.cols,
        "design_grid": cfg.matrix.design_grid,
        "node_capacity": cfg.matrix.node_capacity,
        "sparse": cfg.matrix.sparse,
        "scheduler_bodies": cfg.scheduler.body_count,
        "scheduler_id_range": [cfg.scheduler.id_base, cfg.scheduler.id_top],
        "state_dim": cfg.scheduler.state_dim,
        "guard_layers": cfg.guard.layers,
        "graph_nodes": cfg.graph.node_count,
        "hv_dim": cfg.hypervector.dim,
        "capabilities": CAPABILITY_COUNT,
        "domain_packs": DOMAIN_PACK_COUNT,
        "domain": cfg.domain,
    }


if __name__ == "__main__":
    assert config_verify(), "HoloAeon 配置自洽校验失败"
    print("HoloAeon spec 自洽通过：", MATRIX_ID, PROTOCOL_ID, "deterministic=true")
    print("默认规模（逻辑/稀疏，不预分配）：", lock_check())
