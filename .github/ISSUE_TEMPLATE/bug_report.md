# 缺陷报告 / Bug report

> 提交前请先跑一遍自检，并把最后 5 行贴进来——没有自检输出的缺陷报告通常无法复现。

## 1. 复现步骤

1.
2.
3.

**最小复现代码**（能直接 `python -c` 或单文件运行）：

```python
# 尽量只保留触发缺陷的那几行
```

## 2. 期望 vs 实际

| | 内容 |
|---|---|
| 期望行为 | |
| 实际行为 | （贴完整 traceback） |

## 3. 环境

| 项 | 值 |
|---|---|
| Python 版本 | `python --version` 输出 |
| 操作系统 | |
| 安装方式 | 克隆 / `pip install -e .` / 解压发行包 |
| 内核版本 | `holoaeon.spec.VERSION` |
| 启用的扩展包 | sovereignty / subdistill / omnilife / omnicore / metab / nephron（勾选） |

## 4. 自检输出（末 5 行）

```
python -c "from holoaeon.selftest import run_all; run_all(verbose=True)"
```

```text
（贴最后 5 行）
```

## 5. 红线自检

```
python scripts/redline_scan.py
```

- [ ] 红线扫描零违规（若不是，请说明是哪条规则被误报还是真违规）

## 6. 确定性影响

- [ ] 该缺陷会导致**相同输入产生不同输出**（若勾选，请给出两次运行的 diff）
- [ ] 该缺陷只在多线程 / 多进程下出现
- [ ] 与确定性无关
