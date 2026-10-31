# Cookbooks 索引

三本 cookbook，都是一台机器、十分钟、零依赖能跑完的实战记录。代码逐步实测过。

| 编号 | 标题 | 你要解决的事 | 实测证据 |
|---|---|---|---|
| 01 | [做一个你自己的技能](cookbooks/01_make_your_skill/README.md) | 从零加一个 `bmi_calc` 技能，跑通注册 → 路由 → 执行 | 路由 `[('bmi_calc', 0.20757)]`；提交 `bmi 22.86`；危险调用 `blocked` |
| 02 | [给现有 Agent 加账本](cookbooks/02_add_ledger_to_your_agent/README.md) | 每次动作留一条可复算的记录，并渲染成单文件 HTML | 6 条记录 → 5,860 字节 HTML；两次渲染 sha 一致 `98940b774566543b` |
| 03 | [离线部署到旧笔记本](cookbooks/03_offline_deploy_old_laptop/README.md) | 2GB 旧机、无网络、Python 3.8+ 上跑完整套自检 | 装配 ≈31ms；峰值 1.69MiB；`selftest 24/24`；`34 tests OK` |

## 三本共用的纪律

- **零依赖**：全程 `pip install` 零次，`pyproject.toml` 的 `dependencies = []` 不许破；
- **默认离线**：不开端口、不联网、不读 `.env`；
- **确定性**：任何「两次跑应当一样」的说法，都要给出两次的哈希；
- **诚实**：仿真标 `simulated`，没实测的不写成实测。

## 阅读顺序建议

先读 01 建立「技能 = 清单 + 函数」的最小认知，再读 02 明白「记录 ≠ 日志」，
最后读 03 把它搬到没有网络的机器上。三本都读完，你已经能把 HoloAeon 当作
「一个带回执的确定性内核」来用，而不只是读它的代码。

## 与规范的关系

cookbook 教你怎么做，[确定性 Agent 运行时规范 v0.1](spec-diff0.md) 规定做到什么程度算合格。
想声称「DIFF=0」，先过规范第 7 节的十条自检。
