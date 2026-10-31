# Gitee 直传通道（本地 → Gitee）

> 生效日期：2026-11-01。本文替代旧的「Gitee 镜像（Pull 单向）」方案：镜像已删除，Gitee 侧内容由
> 本地仓库直接推送，不再经过 GitHub。

## 1 通道定义

| 项 | 取值 |
| --- | --- |
| 方向 | 本地 → Gitee，单向 |
| 传输 | HTTPS + 私人令牌（URL 形式 `https://oauth2:<token>@gitee.com/<owner>/<repo>.git`） |
| 账号 | `weideyouni`（Gitee「威德有你」） |
| 令牌名 | `holoaeon-gitee-upload`，权限 `user_info` + `projects`，永不过期 |
| 令牌存放 | `C:\Users\Administrator\.gitee_token`（UTF-8 无 BOM，单行）；亦可用环境变量 `GITEE_TOKEN` 覆盖 |
| 仓库 | `https://gitee.com/weideyouni/holoaeon`（`vector-sea` 同通道，见 §5） |

令牌不写进仓库、不写进 `.git/config` 的 remote URL：脚本在运行时拼装带令牌的临时 URL，只用于当次 push。
日志里的令牌一律打码成 `****` + 末四位。

## 2 为什么弃用镜像

2026-10-31 建成的 Pull 镜像（Gitee ← GitHub）在 2026-11-01 已删除，原因有两条，都是实测：

- 镜像的源是 GitHub，而 GitHub 侧 `main` 停在 `168d405`（本机 TLS 被节点掐断，`git push` 累计 25+ 次失败，
  统一报 `schannel: failed to receive handshake`）。Gitee 自动同步一旦触发，就会用 GitHub 的旧提交覆盖
  刚推进到 `29d3851` 的 Gitee `main`。
- 镜像依赖 GitHub 私人令牌（要求 `repo` + `admin:repo_hook`）。手上两枚 GitHub 令牌：一枚只有
  `public_repo` 被判「无效的私人令牌」，另一枚 90 天期的复测 401。源侧凭据失效，镜像本身就是个哑管道。

删除动作在 `https://gitee.com/weideyouni/holoaeon/mirrors` 完成，页面回执「删除成功」，列表回到空态。
删完之后 Gitee 侧不再有任何自动覆盖来源，本地推送即最终状态。

## 3 工程化：`scripts/gitee_publish.py`

零依赖、Python 3.8+，职责是「推送 + 自证」，口令是**远端哈希签收**：push 的退出码不算数，远端 ref 与
本地 `HEAD` 相等才算数。

```powershell
# 试跑：只比对，不推送
python scripts\gitee_publish.py --repo F:\doubaowork\holoaeon --branch main --dry-run

# 正式推送（默认同时推标签）
python scripts\gitee_publish.py --repo F:\doubaowork\holoaeon --branch main

# 换仓库（从 origin 解析不出 owner/name 时显式指定）
python scripts\gitee_publish.py --repo F:\doubaowork\vector-sea --owner weideyouni --name vector-sea
```

实测回执（2026-11-01，`dry-run` 与正式推送各一次）：

```
==> Gitee 直传 weideyouni/holoaeon @ main
    local  : 29d3851019cd
    remote : 29d3851019cd -> 29d3851019cd
    令牌   : ****2af7 (file:C:\Users\Administrator\.gitee_token)
    耗时   : 0.75s  标签=否  校验=PASS
==> PASS
```

退出码：`0` 通过、`2` 找不到令牌、`3` Git 失败、`4` 远端哈希未追平、`5` 工作树不干净（需先提交或
`--allow-dirty`）。远端分叉时脚本直接失败并打印两条哈希，不做 `--force`。

## 4 MCP 服务器：`scripts/mcp_gitee_server.py`

stdio 传输、JSON-RPC 2.0 换行分隔、零依赖。注册片段（以 Claude Desktop 为例，路径按实际填）：

```json
{
  "mcpServers": {
    "gitee": {
      "command": "python",
      "args": ["F:\\doubaowork\\holoaeon\\scripts\\mcp_gitee_server.py"],
      "env": {"GITEE_TOKEN": "<令牌>"}
    }
  }
}
```

令牌文件已存在时可省略 `env`。五个工具：

| 工具 | 作用 | 主要参数 |
| --- | --- | --- |
| `gitee_status` | 本地 HEAD 与远端 ref 比对，不推送 | `repo_path`、`branch` |
| `gitee_publish` | 推送分支/标签并回读校验 | `repo_path`、`branch`、`push_tags`、`allow_dirty` |
| `gitee_create_repo` | 建仓库 | `name`、`description`、`private`、`auto_init` |
| `gitee_repo_info` | 仓库元数据（体积、默认分支、更新时间） | `owner`、`repo` |
| `gitee_get_file` | 读仓库内文件文本 | `owner`、`repo`、`path`、`ref` |

自检走真实协议、真实调用（`scripts/mcp_gitee_selftest.py`），2026-11-01 实测 4/4：

```
[PASS] initialize — 2024-11-05
[PASS] tools/list — gitee_status,gitee_publish,gitee_create_repo,gitee_repo_info,gitee_get_file
[PASS] gitee_status — in_sync=True
[PASS] unknown_tool — -32601
==> 4/4
```

## 5 `vector-sea` 仓库（向量海）

- 源目录：`F:\doubaowork\向量海_本地库`（顶层 1261 项：目录 1187 / 文件 74）
- 工作库：`F:\doubaowork\vector-sea`，内容为源目录全量复制，排除两处嵌套外部数据集的 `.git`
- 规模：`10313` 个文件 / `106.91 MB`，单文件最大 2.78 MB
- 远端：`https://gitee.com/weideyouni/vector-sea`，分支 `main`，首次推送 `[new branch] main -> main`
- 更新方式：`robocopy` 覆盖源 → 工作库，再 `python scripts\gitee_publish.py --repo F:\doubaowork\vector-sea --owner weideyouni --name vector-sea`

## 6 验收（Gitee 侧维度对齐 GitHub 侧）

从 Gitee 重新克隆 `_gitee_verify_29d3851` 后实跑，2026-11-01：

| 项 | 结果 |
| --- | --- |
| `HEAD` | `29d3851`（与本地 `main` 一致） |
| 标签数 | 7 |
| `holoaeon/` 文件数 | 48 |
| `launch_local.py selftest` | `==> 25/25`，`rc=0` |
| `redline_scan.py` | 扫描文件数 42，干净（零违规），`rc=0` |
| `_check_py38_syntax.py` | `parsed=90  py38_syntax_failures=0`，`rc=0` |

## 7 已知边界

- GitHub 侧仍停在 `168d405`，比 Gitee 少一个提交（`29d3851` 的四步 annotation 版）；GitHub 推送在
  本机网络下依旧失败，恢复后需单独补推。
- Gitee 免费仓库有体积与单文件上限，`vector-sea` 已占 106.91 MB，后续增量要先算体积。
- 不支持 Git LFS：大二进制文件不能靠 LFS 绕过限制。
- 令牌永不过期，泄露即等同账号写权限；轮换入口 `https://gitee.com/profile/personal_access_tokens`。

## 8 飞书同步

两份文档已随本通道更新（2026-11-01）：

- HoloAeon DIFF=0 升级合订稿（V3）：`https://my.feishu.cn/docx/GqC7d2rAvoePjkxPlocccFX5nqe`，第十节 §4 由「Gitee 镜像」改写为「Gitee 直传通道」，并补齐脚本、MCP、vector-sea 与验收数字。
- Gitee 直传与向量海 · 通道说明（新建）：`https://my.feishu.cn/docx/Q1cVdQQ1uogX4lxr2lWcXZ9hnMb`，含通道表、退出码表、MCP 工具表、验收数字与边界。

