# 模型适配层

模型适配层让框架用一个接口对接任意大模型——本地、私有或云端，不绑定厂商。

## 1. 模型后端（ModelBackend）

每个后端描述：
- `name`、`provider`（local / private / cloud）；
- `family`：chat / completion / embedding / vision；
- `context_window`：上下文窗口；
- `input_cost` / `output_cost`：单位成本；
- `latency_ms`：延迟；
- `modalities`：支持的模态；
- 能力与限流参数。

## 2. 八种路由策略

| 策略 | 选择依据 |
|---|---|
| `cheapest` | 单位成本最低 |
| `largest_context` | 上下文窗口最大 |
| `fastest` | 延迟最低 |
| `capability_match` | 能力匹配度最高 |
| `round_robin` | 轮询 |
| `load_balance` | 负载均衡 |
| `modality_match` | 模态匹配 |
| `fallback` | 主后端失败时回退 |

## 3. 十种消息格式

`openai_chat`、`anthropic`、`gemini`、`llama`、`completion`、`embedding`、
`function_call`、`vision`、`tool_use`、`batch`。

`format_messages` 把统一消息转换为目标后端的格式，屏蔽各家 API 差异。

## 4. 八项用量指标

`prompt_tokens`、`completion_tokens`、`total_tokens`、`latency_ms`、`input_cost`、
`output_cost`、`total_cost`、`requests`。

`record_usage` 记录每次调用，`usage_report` 汇总成本与容量，便于预算管控。

## 5. 离线定位

适配层本身**不发起网络请求**——它只做后端注册、路由决策、格式转换与用量核算。真正的
调用由你提供的后端实现完成，因此核心可在离线环境完整测试。

## 6. 用法

```python
from holoaeon.model_adapter import ModelAdapter, ModelBackend
ma = ModelAdapter()
ma.register_backend(ModelBackend("local", "local", input_cost=0.0))
ma.register_backend(ModelBackend("cloud", "cloud",
                                 context_window=100000, input_cost=0.02))
print(ma.route("x", strategy="cheapest"))       # local
print(ma.route("x", strategy="largest_context"))  # cloud
```
