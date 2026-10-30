# 支持矩阵 Support Matrix

> 规则：**只填实跑结果**。跑过的格子写 `measured`，没跑过的写 `untested`。
> 出现 `assume` / `expect` / `pass`（无证据）均视为违规——`uplift.support_matrix` 技能会把它们判为 `FAIL`。

## 1. 本地实测行（唯一有证据的行）

| Python | 单测 `unittest` | 自检 `run_all()` | 红线 `redline_scan` | 示例 01–04 | 采集日期 |
|---|---|---|---|---|---|
| **3.13.16** (Windows 10 / AMD64 / 32 核) | measured · 34 tests OK | measured · 24/24 组 | measured · 34 文件零违规 | measured · 全部 exit 0 | 2026-10-30 |

示例 05（宿主桥）同为 `measured · skip 退出 0`（本机无 Ollama，属预期分支）。

## 2. CI 矩阵行（尚未在 GitHub 实跑）

| Python | 单测 | 自检 | 红线 | 示例 01–04 |
|---|---|---|---|---|
| 3.8 | untested | untested | untested | untested |
| 3.10 | untested | untested | untested | untested |
| 3.12 | untested | untested | untested | untested |

这三行**不是"预计通过"**，是"没跑过"。`.github/workflows/ci.yml` 已经写好并会被 GitHub Actions 执行；跑通之后，应把对应格子改成 `measured` 并附运行链接。

## 3. 不在矩阵内但需要声明的

| Python | 状态 | 原因 |
|---|---|---|
| 3.9 | untested | 未纳入 CI 矩阵（可后补） |
| 3.11 | untested | 未纳入 CI 矩阵（可后补） |

## 4. 已知环境风险

- 本机 Python 为 **3.13.16**，CI 最低声明为 3.8：类型注解使用了 `from __future__ import annotations` 与 `Dict/List/Tuple` 显式泛型，理论上 3.8 可用，**但未实测**。
- `bridges/` 与 `scripts/` 不在红线扫描目标；桥内的网络 import 是**设计允许**的，不是漏扫。
- 所有实测结果都带环境绑定：换机器/换 Python，数字会变，格子需要重填。

## 5. 复核命令

```
python -m unittest discover -s tests -v
python -c "from holoaeon.selftest import run_all; r=run_all(); print(r['passed'],'/',r['groups'],r['failed'])"
python scripts/redline_scan.py
python examples/01_basic_matrix.py ; python examples/02_semantic_routing.py ; python examples/03_hebbian_collaboration.py ; python examples/04_domain_pipeline.py
python scripts/measure_a1_a2.py --runs 30
```

---

潮起开门，潮落闭嘴
