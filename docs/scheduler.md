# 调度器（心跳）

调度器是系统的周期性同步信号。每个心跳 tick 完成一次全局对齐。

## 1. 心跳体（HeartbeatBody）

每个心跳体包含：
- `bid`：唯一编号（默认号段 8700–8769，共 70 体）；
- `state`：768 维状态向量；
- `intensity`：对当前信号的投影强度；
- `status`：`idle` / `active` / `degraded`。

## 2. 每个 tick 做什么

```
tick(workload)
  ├─ 生成全局信号（由 tick 计数确定性派生）
  ├─ 每个 body 计算自身状态与信号的投影强度
  ├─ 超阈值 → active，否则 idle
  ├─ 指数平滑更新状态（α = 0.18）
  └─ 异常/低强度 body 标记 degraded
```

## 3. 指数平滑

状态更新采用指数移动平均：

```
state_new = α · signal + (1 − α) · state_old
```

α = 0.18 表示每个 tick 吸收约 18% 的新信号，保留 82% 的历史，兼顾响应性与稳定性。

## 4. 健康检查

`health()` 返回 tick 数、各状态 body 数（active/degraded/idle）与同步模式。

## 5. 同步模式

- `fixed`：固定节奏；
- `adaptive`：根据负载自适应（默认）。

## 6. 配置

所有参数（body 数、号段、状态维度、α、间隔）都在 `spec.py` 的 `SchedulerConfig` 中，
可整体替换。
