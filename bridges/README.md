# bridges/ —— 宿主模型桥

> 这里**不属于**核心包。`holoaeon/` 保持零网络、零第三方依赖、确定性；
> 真实模型调用破坏"离线"与"确定性"，所以它被隔离在这一层，并留痕。
> 密令 **潮起开门，潮落闭嘴**

## 一分钟理解

| | 位置 | 允许联网 | 允许非确定性 | 谁守护 |
|---|---|---|---|---|
| 核心包 | `holoaeon/` | 否 | 否 | `scripts/redline_scan.py` |
| 宿主桥 | `bridges/`（本目录） | 是 | **是，且必须如实回执** | 远程门禁 + 审计 |

同一原则此前已用在两处：线程归宿主（NEPHRON N1）、快照 `host_managed`（OMNICORE）。
**网络也归宿主。** 这不是妥协，是让"零依赖"与"可接真实模型"同时成立的办法。

## 五分钟上手

```bash
# 1) 本机探测（不会调用模型，只列可用模型）
python bridges/quickstart.py --check

# 2) 首次调用
python bridges/quickstart.py --ask "用一句话说明这个仓库是做什么的"

# 3) 离线自检（不联网、不需要任何服务，用来验证桥的装配与审计链路）
python bridges/quickstart.py --ask "自检" --backend echo
```

`--check` 在没有任何本地模型的机器上会打印三行安装指引并以 **退出码 2** 结束——
**这是预期分支，不是错误**（无 traceback）。契约写死在
`docs/support-matrix.md` 与 `docs/bridges.md` 里，也由 `examples/05_live_model.py` 覆盖。

## 三个后端

| 后端 | 默认地址 | 需要密钥 | 说明 |
|---|---|---|---|
| `ollama` | `127.0.0.1:11434/api/chat` | 否 | 本机推理，`temperature=0`，返回 `prompt_eval_count` / `eval_count` |
| `openai_compat` | `127.0.0.1:8080/v1/chat/completions` | 本机可空 | llamafile / LM Studio / vLLM 均兼容 |
| `echo` | `echo://local` | 否 | **离线自检后端**，回执 `mode="echo"`，永不冒充 `live` |

## 门禁（fail-closed）

远程地址要同时满足三件事才放行，缺一即在**构造阶段**拒绝（结构化报错，不抛异常）：

1. 环境变量 `HOLOAEON_ALLOW_REMOTE=1`；
2. 显式 `--allow-remote` 参数；
3. 主机在 `--allow-host` 白名单内。

密钥只从环境变量 `HOLOAEON_API_KEY` 读取，**不写入任何文件、日志、账本**。

## 回执五要素

```
{"ok": true, "mode": "live", "output": "...", "backend": "ollama",
 "model": "qwen2.5:0.5b", "tokens": {"prompt": 12, "completion": 40}, "latency_ms": 812.4}
```

`mode` 只有两个合法值：`live`（真实模型）与 `echo`（离线自检）。
**`simulated` 回归核心包的 `ModelAdapter`**——两者不可互相顶替，也不可把 `echo` 写进文档冒充 `live`。

## 审计（`bridges/.live_audit.jsonl`，已 gitignore）

每行七个字段，**不含明文**：

```
seq / backend / model / prompt_sha16 / response_sha16 / latency_ms / tokens
```

同一输入两次调用的 `latency_ms` 与 `response_sha16` 允许不同——**桥必须如实呈现这一非确定性**。
这正是桥存在的理由：把非确定的部分隔离在一层，并留痕。

## 本机能证 / 不能证

| 项 | 状态 |
|---|---|
| 离线后端 `echo` 全链路 + 审计 7 字段 | 已实测 |
| 远程门禁四分支（默认锁 / 缺白名单 / 缺 env / 放行） | 已实测 |
| 无本地模型的 `--check` 分支（退出码 2 + 三行指引） | 已实测 |
| `examples/05_live_model.py` 在无桥环境跳过 | 已实测（`skip`，exit 0） |
| **真实 `mode="live"` 回执** | **未实测**（本机未安装本地推理服务）→ 记为 `untested`，不得写成通过 |

## 文件

```
bridges/
├── README.md        # 本文件
├── transport.py     # post_json：4 类错误分型 + 兜底，永不抛到调用方
├── backends.py      # 三后端 + 远程门禁 check_target（六分支）
├── live_client.py   # LiveModelClient.ask()：路由 → 调用 → 回执 → 审计
└── quickstart.py    # --check / --ask
```

上层说明见 [`../docs/bridges.md`](../docs/bridges.md)。
