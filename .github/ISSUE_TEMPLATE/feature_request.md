# 需求 / Feature request

## 1. 你要解决什么问题

（先说问题，再说方案。只写"希望支持 X 框架"通常无法评估。）

## 2. 对应哪个原语 / 包

- [ ] 内核原语（agent / bus / cluster / envelope / graph / guard / hypervector / kernel / memory / scheduler / skill / model_adapter / spec）
- [ ] 扩展包：sovereignty / subdistill / omnilife / omnicore / metab / nephron / uplift
- [ ] 文档 / 示例 / 工具脚本
- [ ] 新东西（请说明为什么现有原语无法组合出来）

**具体模块或函数**：

## 3. 两个必答问题

1. **是否破坏零依赖？**（只能使用 Python 标准库；若需要第三方包，请说明为什么无法用标准库等价实现）

   - [ ] 不破坏
   - [ ] 会破坏（理由：**必填**）

2. **是否破坏确定性？**（相同输入必须相同输出；时间戳、随机源、字典序、线程完成序都必须归一化）

   - [ ] 不破坏
   - [ ] 会破坏（说明归一口径：**必填**）

## 4. 是否触碰红线

- [ ] 需要在 `holoaeon/` 内引入网络 / 子进程 / 动态执行（若勾选，请改为在 `bridges/` 宿主侧实现）
- [ ] 需要新增第三方依赖
- [ ] 都不需要

## 5. 验收标准（可判定）

请写 2–4 条**能被一条命令或一条断言判真假**的标准，例如"`python -m unittest discover -s tests` 全绿且总数 ≥ 30"。
