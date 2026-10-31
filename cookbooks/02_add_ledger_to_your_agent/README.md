# Cookbook 02 · 给现有 Agent 加账本（十分钟）

目标：让你已有的 Agent 每次动作都留一条可回放、可渲染的账本记录，并能一键生成 HTML 视图。
前置：仓库根目录、Python 3.8+、零依赖（不装任何包）。实测：6 条记录 → 5,860 字节 HTML。

## 为什么账本是「记录」而不是「日志」

日志给人看，账本给机器复算：固定 `tick` / `seq` 排序、理由码可枚举、同一账本渲染两次字节一致。
这样别人拿到你的账本，能验你「说过什么」，而不是只能信你「说过」。

## 第 1 步 · 账本的最小记录结构

```json
{"tick": 1, "seq": 0, "window_used": 1,
 "events": [{"seq": 0, "reason_code": "ok", "level": "info", "detail": "..."}],
 "updated_at": "2026-10-31T10:00:00Z", "fingerprint": "fp01"}
```

- `tick`：心跳序号，同一个 tick 内的事件必须同组；
- `reason_code`：可枚举的理由码（`ok / advise / warn / block / error`），不要写自由文本；
- `updated_at` 只用于展示：**渲染器不把它写进 HTML**，否则两次渲染字节就不一致了。

## 第 2 步 · 从内核心跳取材

```powershell
python scripts\ledger_view.py --sample data\ledger_sample.jsonl
```

预期：`sample written: ... (6 records)`。它用 6 次 `kernel.tick()` 造了 6 条记录，
其中第 3 条带 `advise`、第 5 条带 `block`，用来验证分歧高亮。

想知道 tick 里有什么：`python -c "from holoaeon.kernel import Kernel; print(Kernel().tick())"`
键为 `tick / ts / active / degraded / idle / faults / watch_count`——注意 `ts` 是物理量，别进指纹。

## 第 3 步 · 接上你自己的 Agent

在你的循环里，每完成一步就追加一行 JSONL（`encoding='utf-8'`，`sort_keys=True`）：

```python
import json

def log_step(fh, tick, seq, code, detail="", level="info"):
    rec = {"tick": tick, "seq": seq, "window_used": 1,
           "events": [{"seq": seq, "reason_code": code, "level": level, "detail": detail}],
           "updated_at": "2026-10-31T10:00:00Z", "fingerprint": "fp%02d" % (seq + 1)}
    fh.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")
```

## 第 4 步 · 渲染成单文件 HTML

```powershell
python scripts\ledger_view.py data\ledger_sample.jsonl -o reports\ledger.html
```

预期：`html: reports\ledger.html  size=5860 bytes  sha=98940b774566543b  records=6`。
双击 HTML 即可打开，无外部资源、无 JS，断网也能看。

## 第 5 步 · 验证「确定性渲染」

```powershell
python scripts\ledger_view.py data\ledger_sample.jsonl -o reports\ledger_a.html
python scripts\ledger_view.py data\ledger_sample.jsonl -o reports\ledger_b.html
(Get-FileHash reports\ledger_a.html).Hash -eq (Get-FileHash reports\ledger_b.html).Hash
```

预期 `True`。若不相等，检查是不是往输出里塞了时间戳或随机 id。

## 第 6 步 · 让账本进 CI

```powershell
python scripts\verax_verify.py --out reports
```

末行应为 `VERAX_EXIT=0`。VERAX 会把「红线 + 复现 + 诚实」合成一个退出码，
账本里的 `block` 记录不会让门禁变红（它是被正确拦下的证据，不是失败）。

## 常见错误

| 现象 | 原因 | 处理 |
|---|---|---|
| 两次渲染哈希不同 | 输出里含 `updated_at` / 随机 id | 渲染器只认结构字段，展示字段一律不进 HTML |
| 分歧区一片空白 | 事件里没有 `level` 也没 `reason_code` | 至少写 `reason_code`，`ok/warn/block` 即可着色 |
| HTML 打开是空白 | 账本路径写错，读到 0 行 | 先 `Get-Content` 数行，再渲染 |
| 中文乱码 | 用 `>` 或 `Out-File` 写文件 | 用 `encoding='utf-8'` 显式写，别过 PowerShell 管道 |

## 下一步

- 把账本挂进 `holoaeon/audit/receipt.py` 的 `Receipt`，让每条回执自带 `evidence_class`；
- 想让别人能复算你的账本：读 `docs/spec-diff0.md` 的「DIFF=0 哈希协议」；
- 想把账本视图当交付物：直接交付 HTML，别转成截图。
