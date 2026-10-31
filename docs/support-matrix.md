# 支持矩阵 Support Matrix

> 规则：**只填实跑结果**。跑过的格子写 `measured`，没跑过的写 `untested`。
> 出现 `assume` / `expect` / `pass`（无证据）均视为违规——`uplift.support_matrix` 技能会把它们判为 `FAIL`。

## 1. 本地实测行（唯一有证据的行）

| Python | 单测 `unittest` | 自检 `run_all()` | 红线 `redline_scan` | 示例 01–04 | 采集日期 |
|---|---|---|---|---|---|
| **3.13.16** (Windows 10 / AMD64 / 32 核) | measured · 34 tests OK | measured · 25/25 组 | measured · 42 文件零违规 | measured · 全部 exit 0 | 2026-10-31 |

示例 05（宿主桥）同为 `measured · skip 退出 0`（本机无 Ollama，属预期分支）。

## 2. CI 矩阵行（已在 GitHub Actions 实跑）

| Python | 单测 | 自检 | 红线 | 示例 01–04 | A1 判定 | 运行 |
|---|---|---|---|---|---|---|
| 3.8 | measured | measured | measured | measured | measured · PASS + 篡改 FAIL | [run #25](https://github.com/weideyouni/holoaeon/actions/runs/41202167792) @ `afb31ed` |
| 3.10 | measured | measured | measured | measured | measured · PASS + 篡改 FAIL | [run #25](https://github.com/weideyouni/holoaeon/actions/runs/41202167792) @ `afb31ed` |
| 3.12 | measured | measured | measured | measured | measured · PASS + 篡改 FAIL | [run #25](https://github.com/weideyouni/holoaeon/actions/runs/41202167792) @ `afb31ed` |

这三行由 run #25 的 `py3.8 / py3.10 / py3.12 · tests+selftest+redline` 三个 job 产出，总数 0 error
0 warning（仅剩 GitHub 自己的 `ubuntu-latest` 迁移通告，属平台告示不是本仓警告）。

> 3.8 能跑到 `measured` 是两处真实修复的结果，不是放宽判据：
> ① `ubuntu-latest` 已滚到 26.04、预编译清单里没有 3.8，`ci.yml` 改为按行带 `os`，3.8 钉 `ubuntu-22.04`；
> ② 3.8/3.9 没有 `sys.stdlib_module_names`，红线回退清单漏了 `lib-dynload` 里的 `math`/`cmath` 扩展模块，
> 导致 3.8 假红；改为按解释器标准库目录枚举 `.py` + `.so/.pyd`。
> 证据链：run #21（`fd48011`）3.8 红在 Red-line scan → annotation 给出 `[third_party_import] semvec.py:23 — math`
> → 修 `redline.py` → run #24 / #25 三版本全绿。

## 3. 不在矩阵内但需要声明的

| Python | 状态 | 原因 |
|---|---|---|
| 3.9 | untested | 未纳入 CI 矩阵（可后补） |
| 3.11 | untested | 未纳入 CI 矩阵（可后补） |

## 4. 已知环境风险

- 本机 Python 为 **3.13.16**，CI 最低声明为 3.8：类型注解使用了 `from __future__ import annotations` 与 `Dict/List/Tuple` 显式泛型，3.8 语法层用 `ast.parse(feature_version=(3,8))` 扫全仓 88 个 .py 为 0 失败，运行时层由 CI 的 3.8 job 实测（run #25 `measured`）。
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
