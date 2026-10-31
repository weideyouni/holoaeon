# 仓库运营件（W5）

> 当前状态（2026-11-01）：代码与文档均已入库并推送，主通道是**本地直推 Gitee**（见 §4），工作树干净。
> GitHub Actions 自 `#31`（`c4c7d36`）起转红，`#32`~`#37` 三 job 全 failed，step 级日志需登录
> （`Sign in to view logs`），最近一次运行见 `https://github.com/weideyouni/holoaeon/actions`；同一份代码
> 在本地与 Gitee 克隆副本上三闸全过（`selftest 25/25`、红线 42 文件零违规、py3.8 `parsed=90` 0 失败）。
> 状态行故意不写死 commit 哈希——每次改文档都会让它过期，看 run 列表比看哈希可靠。
> **两个网页开关已于 2026-10-31 打开**：7 个 topic 与 Website 链接已在仓库 About 区生效，
> 匿名访问复核通过（见 §3 验收框）。GitHub 的 topics / homepage 没有 API 可写
> （`github-remote` MCP 只覆盖文件、Issue、PR，不覆盖仓库设置），所以那一步是在已登录
> `weideyouni` 的浏览器里点完的——这也解释了为什么它不能进 CI。
> 操作路径有个坑记在 §3.1：Topics 与 Website **不在 Settings → General 里了**，现在只在仓库首页
> About 右侧齿轮打开的弹窗里。
> **O2 于 2026-11-01 改道并收口**：Gitee 镜像已删除（源侧 GitHub 被网络掐断，自动同步会用旧提交覆盖新内容），
> 通道改为「本地 → Gitee 直传」（HTTPS + 私人令牌），Gitee `main` 已推进到 `29d3851`，克隆副本
> 48 文件 / `selftest 25/25` / 红线 42 文件零违规，见 §4 与 `docs/ops/gitee-publish.md`。

## 1 GitHub topics（网页手工一步，脚本改不了）

仓库首页 → 右侧 **About** 区右上角齿轮 ⚙ → 弹窗里的 **Topics** 输入框，逐个输入（每输入一个按
**Enter** 确认成胶囊）：

```
multi-agent, llm, deterministic, zero-dependency, cognitive-architecture, offline-first, reproducibility
```

这些词对应本项目的真实属性，不是堆量：`deterministic` 与 `reproducibility` 是 DIFF=0 协议的关键词，
`zero-dependency` 与 `offline-first` 是立身原则，`cognitive-architecture` 指 12 原语分层。

## 2 Homepage

Settings → Website，填（新版界面同样在首页 About 齿轮弹窗的 **Website** 字段）：

```
https://github.com/weideyouni/holoaeon/blob/main/benchmarks/README.md
```

指向三个数字的页面，而不是仓库根：**让别人 30 秒看到证据，而不是先看长 README。**

## 3 验收（人工核对，三条都做完才算 W5 完成）

- [x] O1-1 topics 生效：仓库页右侧出现 7 个标签 —— 2026-10-31 已勾，匿名抓取 `github.com/weideyouni/holoaeon` 读回
  `topics/cognitive-architecture`、`deterministic`、`llm`、`multi-agent`、`offline-first`、`reproducibility`、`zero-dependency` 共 7 条；
- [x] O1-2 homepage 生效：仓库页顶部出现 Website 链接 —— 同日已勾，About 区外链为
  `github.com/weideyouni/holoaeon/blob/main/benchmarks/README.md`；
- [x] O2 Gitee 直传克隆可跑通三步（见下）—— 2026-11-01 已勾：`https://gitee.com/weideyouni/holoaeon`
  由本地直推送平到 `main = 29d3851`（镜像已于同日删除），克隆副本 `HEAD` 与本地同哈希、包内 48 文件，
  三闸 `rc` 全 0：`selftest` 25/25、`redline_scan` 42 文件零违规、`_check_py38_syntax` `parsed=90` 0 失败
  （逐项证据见 §4.4）。

### 3.1 一次做完的操作路径

1. 浏览器登录 `weideyouni` → 打开 `https://github.com/weideyouni/holoaeon`；
2. 点右侧 **About** 区的齿轮 ⚙（**不是** 顶部 Settings——Settings → General 里已经找不到 Topics 了，
   本页字段都在那个弹窗里）；
3. 弹窗里：**Website** 填 homepage URL；**Topics** 逐个输入、每输入一个按 Enter 变胶囊；
4. 点 **Save changes** → 回首页刷新：About 区应出现 7 个 topic 胶囊与外链。

> 实测踩坑：`cu.type("multi-agent\n")` 这类「文本自带换行」在 Topics 框里**不会**生成胶囊，
> 7 个词会被连成一个 `multi-agentllmdeterministic…`；必须 `type` 与 `press("enter")` 分成两次，
> 且两次之间留 ~1 秒，否则相邻两个词会粘在同一颗胶囊里。

### 3.2 做完怎么验证（不用登录也能查）

```powershell
# topics 是否生效（无需登录，读 HTML 里的 topic 链接）
(Invoke-WebRequest -UseBasicParsing "https://github.com/weideyouni/holoaeon").Content -match "topics/"
```

页面 HTML 里出现 `topics/multi-agent` 这类链接即生效；homepage 同理，仓库 About 区出现 `benchmarks/README.md` 的外链。
2026-10-31 复核结果：topic 链接 7 条、Website 外链 1 条，均已生效（本项已勾）。

## 4 Gitee 直传（本地 → Gitee，2026-11-01 起）

仓库：`https://gitee.com/weideyouni/holoaeon`（开源）。内容由本地仓库直接推送，不再经过 GitHub。
完整操作手册见 [`docs/ops/gitee-publish.md`](gitee-publish.md)，本节只留通道口径与验收。

### 4.1 通道与令牌

- 传输：HTTPS + Gitee 私人令牌，运行期拼装 `https://oauth2:<token>@gitee.com/<owner>/<repo>.git`，只用于当次 push。
- 令牌名 `holoaeon-gitee-upload`，权限 `user_info` + `projects`，永不过期；存 `C:\Users\Administrator\.gitee_token`，
  脚本日志里一律打码成 `****` + 末四位。
- 工程化命令：`python scripts\gitee_publish.py --repo . --branch main`（`--dry-run` 只比对不推送）。
- 判定标准是**远端哈希签收**：push 的退出码不算数，远端 ref 与本地 `HEAD` 相等才算数；不等时脚本以 `rc=4` 退出。

### 4.2 镜像为什么被删（2026-11-01）

| 事实 | 实测 |
|---|---|
| 镜像方向 | Pull（Gitee ← GitHub），勾了自动同步 |
| 源侧状态 | GitHub `main` 停在 `168d405`；本机 `git push` 25+ 次全失败（`schannel: failed to receive handshake`） |
| 风险 | 自动同步一旦触发，会用 `168d405` 覆盖 Gitee 刚推到的 `29d3851` |
| 源侧凭据 | 两枚 GitHub 令牌一枚「无效的私人令牌」，另一枚 401 |
| 处置 | 在 `https://gitee.com/weideyouni/holoaeon/mirrors` 删除镜像，页面回执「删除成功」，列表回到空态 |

旧镜像页留下三条不可行通道的记录（省下重试时间）：`projects/import` 404；HTTPS push 无本地凭据
（`could not read Username`，`rc=128`）；专用 ed25519 密钥 push 仍 `Permission denied (publickey)`，`rc=255`。

### 4.3 验收（三步，2026-11-01 实跑）

```powershell
git clone https://gitee.com/weideyouni/holoaeon.git
cd holoaeon
python scripts\launch_local.py selftest
python scripts\redline_scan.py
python scripts\_check_py38_syntax.py
```

### 4.4 实测数字（在 Gitee 克隆副本 `_gitee_verify_29d3851` 上跑）

| 项 | 结果 |
|---|---|
| `HEAD` | `29d3851`（与本地 `main` 同哈希） |
| 标签 | 7 |
| `holoaeon/` 文件数 | 48 |
| `selftest` | `==> 25/25`，`[FAIL]` 0，`rc=0` |
| `redline_scan` | 扫描文件数 42，干净（零违规），`rc=0` |
| `_check_py38_syntax` | `parsed=90  py38_syntax_failures=0`，`rc=0` |

远端是否落后，用 `git log -1 --format=%H` 与本地 `HEAD` 比对；不一致即为落后。

## 5 README 徽章（可选，一行）

```markdown
![DIFF=0](https://img.shields.io/badge/DIFF%3D0-2fc892cf9af6e755-1F6F5C)
![Guard](https://img.shields.io/badge/guard-100%25%20blocked-B0472C)
![Footprint](https://img.shields.io/badge/footprint-31ms%20%2F%201.69MiB-8A6A1E)
```

数字要随发版重跑 `python benchmarks\bench_public.py` 后手改；徽章是展示，证据在
`benchmarks/results-*.json`。徽章与证据不一致时，以 json 为准。
