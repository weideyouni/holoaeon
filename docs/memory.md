# 记忆（三层存储）

记忆提供线程安全的存取、检索、巩固与衰减。

## 1. 三层结构

| 层 | 容量 | 角色 |
|---|---|---|
| `working` | 256 | 当前任务上下文，可被巩固提升 |
| `longterm` | 100,000 | 跨任务沉淀，带强度与标签 |
| `archive` | 1,000,000 | 稳定事实与参考，不衰减 |

## 2. 记忆项（MemoryItem）

每条记忆含：`key`、`value`、`kind`、`tags`、`ts`（时间戳）、`strength`（强度）。

## 3. 核心操作

- `put(key, value, kind, tags, strength)`：写入，超容量时自动淘汰最弱项；
- `get(key)`：按键精确取值；
- `recall(query, k)`：按 token 重叠 + 标签命中打分，返回前 k；
- `consolidate(min_strength)`：足够强的工作记忆提升为长期记忆；
- `decay(rate)`：工作/长期记忆强度衰减，归档不衰减。

## 4. 检索打分

```
score = Jaccard(query_tokens, item_tokens) + 0.1 · strength
```

## 5. 持久化

支持 `to_dict` / `load` 的 JSON 序列化，便于跨会话恢复。

## 6. 用法

```python
from holoaeon.memory import Memory
m = Memory()
m.put("k", {"a": 1}, kind="working", tags=["x"])
m.consolidate()
print(m.get("k"))          # {'a': 1}
print(m.recall("x"))
```
