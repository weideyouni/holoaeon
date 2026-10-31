# 公开基准（benchmarks）

> 三个数字，随发版重跑。全部条目 `evidence_class=simulated`：仿真 ≠ 证明。

```
DIFF=0 2fc892cf9af6e755 | 拦截 100% | 冷装配 31.66ms / 峰值 1.69MiB
```

## 一 · DIFF=0（确定性）

| 项 | 值 |
|---|---|
| workload 步数 | 16 |
| 规范化后两次一致 | True |
| run1 哈希 | `2fc892cf9af6e755` |
| run2 哈希 | `2fc892cf9af6e755` |
| DIFF=0 | **True** |
| 规范化保留的顶层键 | `runtime_id, steps` |

条文：两次运行各用全新内核，剔除 ts/uptime/elapsed/timestamp 等物理量后
对 canonicalize 结果求 sha256 前 16 位；两次相同即 DIFF=0。
为防「内容被整段剔除、哈希恒真空转」，另做篡改敏感性自检：把任务原文改一个字，
哈希必须变化（见下表）。

| 敏感性自检 | 值 |
|---|---|
| 原始哈希 | `2fc892cf9af6e755` |
| 篡改字段 | steps[*].value.task（word_count 任务原文） |
| 篡改后哈希 | `f42c8229ee5acd73` |
| 哈希对内容敏感 | **True** |

## 二 · 守卫拦截率（安全边界）

| 类别 | 样本 | 拦截 |
|---|---|---|
| danger | 5 | 5 |
| distort | 3 | 3 |
| legit | 4 | 0 |
| overflow | 3 | 3 |
| privilege | 5 | 5 |

危险请求 **16/16 拦截（100%）**；合法 **4/4 放行**。

## 三 · 零依赖足迹（可运行成本）

| 项 | 值 |
|---|---|
| 内核装配耗时 | 31.66 ms |
| 峰值内存（tracemalloc） | 1.69 MiB |
| 装齐后 agent / skill | 25 / 47 |

口径：`build_ms` 为进程内内核装配耗时，不是 OS 冷启动 import；
峰值内存为 tracemalloc 追踪的 Python 分配峰值，不含解释器常驻。

## 机器规格（披露字段，不参与哈希）

| 项 | 值 |
|---|---|
| platform | `Windows-10-10.0.19045-SP0` |
| machine | `AMD64` |
| cpu_count | 32 |
| python | 3.13.16 |
| 生成时刻 | 2026-10-31T11:58:22Z |

## 复跑

```powershell
python benchmarks\bench_public.py
```

同一台机器上连跑两次，`diff0.hash_run1 == hash_run2` 必须成立；
换机器后哈希仍应一致（物理量与机器规格都不进哈希）。
