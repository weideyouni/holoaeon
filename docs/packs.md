# 七大领域包

领域包是自包含的能力集合：若干技能 + 若干角色 + 一个端到端工作流。全部安装后共
**21 个智能体、37 个技能、7 个工作流**。

## 1. writing（文字创作）

- 技能：`word_count`、`readability`、`outline_gen`、`title_brainstorm`、`structure_check`
- 角色：writing_planner、writing_drafter、writing_editor
- 工作流：`creation_pipeline`（提纲 → 起草 → 编辑）

## 2. literature（文献梳理）

- 技能：`keyword_extract`、`extract_abstract`、`normalize_citation`、`dedup_papers`、`screen_papers`
- 角色：lit_searcher、lit_reader、lit_reviewer
- 工作流：`review_pipeline`（检索 → 阅读 → 评审）

## 3. research（科研）

- 技能：`hypothesis_check`、`variables_split`、`design_experiment`、`sample_size`、`reproduce_check`
- 角色：research_designer、research_executor、research_analyzer
- 工作流：`research_pipeline`（设计 → 执行 → 分析）

## 4. data（数据处理）

- 技能：`csv_profile`、`missing_report`、`basic_stats`、`normalize_column`、`outlier_detect`
- 角色：data_cleaner、data_analyst、data_reporter
- 工作流：`data_pipeline`（清洗 → 分析 → 报告）

## 5. growth（个人成长）

- 技能：`goal_smart`、`habit_plan`、`task_breakdown`、`weekly_review`、`energy_mapping`
- 角色：growth_goal_coach、growth_habit_coach、growth_review_coach
- 工作流：`growth_loop`（目标 → 习惯 → 复盘）

## 6. business（企业运营）

- 技能：`business_model_canvas`、`okr_gen`、`swot_analysis`、`kpi_dashboard`、`meeting_agenda`、`risk_register`
- 角色：biz_strategist、biz_operator、biz_risk_manager
- 工作流：`business_pipeline`（战略 → 运营 → 风控）

## 7. quant（量化分析）

- 技能：`returns`、`volatility`、`sharpe`、`drawdown`、`moving_average`、`backtest`
- 角色：quant_analyst、quant_researcher、quant_risk
- 工作流：`quant_pipeline`（收益 → 研究 → 风险）

## 8. 安装方式

```python
from holoaeon.kernel import Kernel
from holoaeon.packs import get_pack, all_packs

k = Kernel()
get_pack("data").install(k)      # 安装单个
for p in all_packs():            # 安装全部
    p.install(k)
```

## 9. 自定义领域包

继承 `DomainPack`，定义 `key`、`skills`（SkillSpec 列表）、`roles`（RoleSpec 列表）、
`workflows`（WorkflowSpec 列表），然后在 `packs/__init__.py` 注册即可。所有技能函数
应保持确定性、纯标准库。
