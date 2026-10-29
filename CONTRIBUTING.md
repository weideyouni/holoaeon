# 贡献指南

感谢你对 HoloAeon 的兴趣！欢迎通过 Issue 和 Pull Request 参与贡献。

## 开始之前

1. Fork 本仓库并克隆到本地；
2. 确认环境为 Python 3.8+；
3. 本项目**零依赖**，无需安装第三方包。

## 开发流程

1. 从 `main` 创建特性分支：`git checkout -b feature/your-feature`；
2. 完成改动并保持代码风格一致；
3. 添加或更新测试；
4. 确保以下三项全部通过；
5. 提交并推送，创建 Pull Request。

## 提交前必须通过

```bash
# 1. 自检套件（G1–G15）
python -c "from holoaeon.selftest import run_all; print(run_all(verbose=True))"

# 2. 单元测试
python -m unittest discover -s tests -v

# 3. 红线扫描（零网络 / 零第三方依赖 / 零危险调用）
python scripts/redline_scan.py
```

## 编码约定

- 仅使用 Python 标准库，不引入第三方依赖；
- 保持确定性：相同输入产生相同输出；
- 不发起网络请求、不读取凭证、不常驻、不写 cron；
- 新增模块请包含模块级 docstring；
- 生物/宇宙词汇仅作隐喻，核心以工程概念命名。

## Pull Request 内容

PR 描述请尽量包含：

- 改动说明与动机；
- 受影响的模块；
- 测试用例或示例；
- 文档更新；
- 兼容性说明。

## 新增领域包

如果你想贡献新的领域包，请参考 [docs/packs.md](docs/packs.md) 中的"自定义领域包"一节，
并确保包含技能、角色与工作流。

## 报告问题

提交 Issue 时请说明：问题描述、复现步骤、预期与实际行为、Python 版本与操作系统。

## 行为准则

参与本项目请遵守 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)。
