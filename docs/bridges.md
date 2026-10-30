# 宿主模型桥 bridges（U2）

> 位置：仓库根 `bridges/`，**不在 `holoaeon/` 包内**，不在 `scripts/redline_scan.py` 的默认扫描目标里。
> 立场：零依赖是核心包的属性，不是用户能力的天花板。

---

## 1. 为什么桥必须在包外

框架本体承诺三件事：零第三方依赖、离线可跑、确定性。真实模型调用同时违反后两条（要网络、输出天然漂移）。二者不能共存于同一个目录里——所以网络被推到宿主侧：

```
holoaeon/          核心包  零网络 / 零第三方 / 确定性      ← 红线扫描盯着这里
bridges/           宿主桥  有网络 / 允许非确定 / 留痕     ← 不在扫描目标
examples/05_live_model.py  示例：有桥就跑，无桥就 skip
```

这与项目既有原则同源：N1「线程归宿主」、omnicore「快照 host_managed」——现在「网络也归宿主」。

## 2. 三后端

| 后端 | 默认 base_url | 路径 | 需要 key | 说明 |
|---|---|---|---|---|
| `ollama` | `http://127.0.0.1:11434` | `/api/chat` | 否 | 探活 `/api/tags` 列本机模型 |
| `openai_compat` | `http://127.0.0.1:8080` | `/v1/chat/completions` | 本地可空 | llamafile / LM Studio / vLLM 兼容 |
| `echo` | `echo://local` | — | 否 | **离线自检后端**，不发请求、不写审计，回执 `mode="echo"` |

密钥只从环境变量 `HOLOAEON_API_KEY` 读，**只在内存里进请求头**，不写文件、不写日志、不写账本。

## 3. 远程门禁（fail-closed）

| 情形 | 判定 | 结果 |
|---|---|---|
| `127.0.0.1 / localhost / ::1` | `LOCAL` | 放行 |
| 非本机 + 未设 `HOLOAEON_ALLOW_REMOTE=1` | `REMOTE_LOCKED` | 构造即拒（`ValueError`） |
| 已设 env 但未传 `allow_remote=True` | `REMOTE_NOT_CONFIRMED` | 拒 |
| 双重确认但地址不在白名单 | `REMOTE_NOT_ALLOWLISTED` | 拒 |
| env + flag + 白名单三者齐 | `REMOTE_ALLOWED` | 放行 |
| `scheme=echo` | `OFFLINE_BACKEND` | 放行（不参与网络准入） |

三重任一缺失即拒；env 只是解锁开关，**不能替代白名单**。

## 4. 回执三态

| mode | 含义 | 必备字段 |
|---|---|---|
| `live` | 真实调用过模型 | `output / backend / model / tokens / latency_ms` |
| `echo` | 离线自检，无网络调用 | 同上（`ok=True`） |
| `simulated` | 框架内离线路由的旧行为 | `output / backend / model` |

规则：**回执必须自带 `mode`；无 `mode` 的回执不得对外表述**。失败分支也标 `live` 且 `ok=False`，并附 `note` 说明"未重试、未伪造"。这是"不被 AI 忽悠"这条使命在工程上的落点。

## 5. 审计

每次真实调用追加一行到 `bridges/.live_audit.jsonl`（已 `.gitignore`）：

| 字段 | 内容 |
|---|---|
| `seq` | 单调序号（时间戳归一化，保证可比较） |
| `backend` / `model` | 后端与模型名 |
| `prompt_sha16` / `response_sha16` | 提示与响应哈希前 16 位 |
| `latency_ms` | 耗时 |
| `tokens` | 提示/生成 token 计数（后端没给就记 `null`，不猜 0） |

**禁记**：提示明文、响应明文、密钥、`Authorization` 头、`messages` 数组。留痕不等于留明文。

## 6. 五条命令

```
python bridges/quickstart.py --check          # 探本机 Ollama，列出模型
python bridges/quickstart.py --ask "问题"      # 默认 ollama + 本机第一个模型
python examples/05_live_model.py              # 无桥：skip 退出 0；有桥：全链路
```

本机（未安装 Ollama）实测：`--check` 打印三行安装指引并 `exit=2`，无 traceback；`05_live_model.py` 打印 `skip` 并 `exit=0`；真实调用路径 `LIVE_NO_SERVER: ok=False / error_type=timeout`（结构化失败，不抛异常）。

## 7. 本机能证与不能证

| 项 | 状态 |
|---|---|
| 核心包零网络（红线 34 文件零违规） | 已实测 |
| 三后端登记 / echo 装配 / 回执 `ok` | 已实测 |
| 远程门禁四分支 | 已实测 |
| 审计无明文（7 字段） | 已实测 |
| `--check` 无 Ollama 分支退出码 2 | 已实测 |
| 真实 `mode=live` 回执 | **未实测**（本机无 Ollama，标 `untested`） |

不写"桥已可用"这种会把未测项折叠成结论的话。

## 8. 快速上手（5 分钟）

1. 装 Ollama：<https://ollama.com> → `ollama pull qwen2.5:0.5b`
2. `python bridges/quickstart.py --check` → 看到模型列表
3. `python bridges/quickstart.py --ask "用一句话解释递归"` → 回执五要素齐全，`mode=live`
4. 想换本地 OpenAI 兼容端点：`--backend openai_compat --base-url http://127.0.0.1:8080`
5. 想把桥接到远程：设 `HOLOAEON_ALLOW_REMOTE=1` + 传 `--allow-remote` + 白名单，三者齐才放行

---

潮起开门，潮落闭嘴
