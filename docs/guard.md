# 守卫（安全边界）

守卫是系统的语义级边界，所有进入/离开的信封都经过 L1–L8 串联检查。

## 1. 三种动作

每个检查返回 `Verdict`：
- `allow`：放行；
- `advise`：放行但记入审计；
- `block`：拦截。

任一 `block` 即拦截该信封。

## 2. 八层结构

| 层 | 职责 | 失败动作 |
|---|---|---|
| **L1** | 结构完整：sender/topic/recipient 非空 | block |
| **L2** | 体积限制：payload 可序列化且不超限 | block |
| **L3** | 危险模式：注入 / 危险调用 / 密钥读取 | block |
| **L4** | 权限匹配：所需权限 ≤ 主体权限 | block |
| **L5** | 越权 / 失真：身份冒用（unauthorized）/ 消息失真（garbled） | block |
| **L6** | 元数据：必要字段与 mode 合法 | block |
| **L7** | 审计：记录出入站 | advise |
| **L8** | 一致性：trace 与消息体一致 | advise |

## 3. 危险模式检测（L3）

L3 维护一个危险模式词表（如 `os.system`、`eval`、`__import__`、`rm -rf`），对信封
文本做模式匹配。注意：词表本身是字符串常量，红线扫描器通过 AST 区分"词表定义"与
"实际调用"，不会误报。

## 4. 越权与失真（L5）

- **越权**：信封声明身份与实际 sender 不符；
- **失真**：显式标记 `garbled=True` 的消息。

## 5. 审计

`audit_enabled=True` 时，每个决策（含时间、发送者、主题、Verdict）写入审计日志。

## 6. 用法

```python
from holoaeon.guard import Guard
g = Guard()
verdict = g.check_text("os.system('rm -rf')")
print(verdict.action)   # block
print(verdict.layer)    # L3
```
