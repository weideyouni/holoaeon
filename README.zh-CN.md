<div align="center">

# HoloAeon

### 零依赖、生物启发的通用多智能体认知框架——给大模型当管家，给普通人当工具

![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)

![Python](https://img.shields.io/badge/python-3.8%2B-green.svg)

![Dependencies](https://img.shields.io/badge/dependencies-0-success.svg)

![Tests](https://img.shields.io/badge/tests-34%20passed-success.svg)

![SelfTest](https://img.shields.io/badge/selftest-25%2F25-success.svg)

[English](README.md) · [中文](README.zh-CN.md)

</div>

---

## 这是什么

HoloAeon 是**纯标准库、全离线、确定性**的多智能体认知框架：零依赖、零安装、零成本起步，
一台十年前的旧笔记本即可运行。它可构建在任意大模型之上——也可以完全不用大模型独立工作。

**它的定位：给大模型当管家。**&#x5927;模型负责语言与生成，HoloAeon 负责安检、记账、路由、
复现——让 AI 的每一次回答旁边，站着一个可审计的记忆体。

## 为什么选择 HoloAeon

| 原则       | 实际含义                            | 实测证据                         |
| -------- | ------------------------------- | ---------------------------- |
| **零依赖**  | `dependencies = []`，纯标准库，不装任何东西 | 红线扫描 34 文件零违规                |
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

> 一句安心话：HoloAeon 核心是 3547 行纯标准库 Python，`pip install` 不安装任何东西，
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

## 测试

```bash
python -m unittest discover -s tests    # 34 项单元测试
python -c "from holoaeon.selftest import run_all; print(run_all())"  # 25/25 自检组
python scripts/redline_scan.py          # 红线扫描：零违规
python scripts/measure_a1_a2.py         # A1/A2 宿主侧实测（CI 已挂载）
```

当前状态：**34 单测通过｜自检 25/25 组｜红线扫描零违规（42 文件）｜A1 证据哈希 CI 防漂移**；
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
