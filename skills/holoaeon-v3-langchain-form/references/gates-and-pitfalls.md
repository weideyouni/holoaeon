# A1–A13 判据与 V3-1..V3-12 坑表（全表）

## 一 A1–A13（逐条可判定）

| # | 判据 | 通过形态 |
|---|---|---|
| A1 | 基线三闸 | `Ran 34 OK` + `True 25` + 红线零违规 |
| A2 | 确定性 | `DIFF=0 2fc892cf9af6e755`，篡改 `f42c8229ee5acd73`，`sensitive=True` |
| A3 | 守卫 | 20 条集：拦截 16/16=100%，合法放行 4/4 |
| A4 | runnable | call/batch 同实现；五段顺序；dump 可读；钩子错可定位 |
| A5 | span_tree | 树可导出可哈希；耗时不进哈希；开关它内核字节不变 |
| A6 | schema | 缺参/类型/多余字段指名；修复环 2 次超限抛错 |
| A7 | eval | 47 条四件套；diff 抓得到回归；judge 只披露 |
| A8 | interrupt+checkpoint | 跨实例恢复；未批不执行；三档有保证与代价；强杀续跑 DIFF=0 |
| A9 | 渐进加载+缓存 | 不读无关正文；命中率不降；缓存逐字节同 |
| A10 | replay+event | 原账本不变；可比；7 类事件只读零网络；开关字节不变 |
| A11 | 桥 | 3 方法 + conformance 6/6，不加内核代码 |
| A12 | 约束 | `dependencies = []`；无新增依赖；既有 golden 全留 |
| A13 | 诚实 | 新数字有出处；eval 标 `simulated`；judge 不进裁决轨 |

现状：A1–A13 全部满足（见 `reports/v3_gate.json` 32 项 + 人工复核 A13）。

## 二 坑表（每条都真实发生过）

| # | 现象 | 原因 | 处理 |
|---|---|---|---|
| V1-1 | `python -m holoaeon.selftest` 早期报无 `__main__` | 历史坑 | 用 `launch_local.py selftest` 或直接 `run_all()` |
| V2-1 | `assertEqual(ORDER, 7)` 失败 | `persona_quartet` 使扩展包变 8 | 已改下界 `>= 7`，不许改回等值 |
| V2-2 | persona 化名 P1–P4 与公开人物版并存 | 命名空间隔离 | 调用必须用 P1–P4 |
| V3-1 | `runnable` 与 `kernel.submit` 双入口 | 抽象缠绕 | `Runnable.call` 只做协议封装，内部仍走既有执行路径 |
| V3-2 | span 树哈希含耗时 → 漂移 | 物理量进哈希 | 结构哈希只取结构字段 |
| V3-3 | schema 失败静默兜底 | 隐藏魔法 | 显式指名字段，超限抛 `SchemaError` |
| V3-4 | interrupt 令牌联网 | 破离线 | 令牌落 JSON 文件本地比对 |
| V3-5 | eval 用 judge 裁决 | 软化红线 | judge 只披露，结论 `simulated` |
| V3-6 | replay 分支改原账本 | 破确定性 | 分支独立记账，原 `digest` 字节不变 |
| V3-7 | 渐进加载降命中率 | 裁剪过度 | `routing_accuracy` 对齐全量，降了就回退 |
| V3-8 | `inspect.getsource(实例)` 抛 `TypeError` | 传了实例不是函数 | 用 `inspect.getfile(type(obj))` |
| V3-9 | conformance 把桥误判成"在内核里" | 路径含 `\holoaeon\` 是仓库目录名 | 用内核目录**绝对前缀**比较 |
| V3-10 | 五段钩子出现双 route | Pipeline 与 Skill 各跑一次 | admit/route/egress 只在顶层 `call`；嵌套 `_nested=True` |
| V3-11 | `run_all()["groups"]` 用 `len()` 崩 | 它是 int 计数 | 直接打印 |
| V3-12 | `trunc12` / `reverse` 变体不降点 | 变体不够对抗 | 用 `cross`（别条技能自述当问句） |

## 三 改完必跑

```bash
python scripts\v3_gate.py --json reports\v3_gate.json
```

任何 `Write` 级别的小错（漏括号、少参数）都只有真跑才暴露；
`v3_gate` 跑绿之前不要写"已完成"。
