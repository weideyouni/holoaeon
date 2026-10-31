# 仓库运营件（W5）

> 当前状态（2026-10-31）：代码与文档均已入库并推送，工作树干净；CI 已在 GitHub 实跑并全绿
> （Python 3.8 / 3.10 / 3.12 三 job 全过，0 error 0 warning），最近一次运行见
> `https://github.com/weideyouni/holoaeon/actions`。状态行故意不写死 commit 哈希——每次改文档都会
> 让它过期，看 run 列表比看哈希可靠。
> **两个网页开关已于 2026-10-31 打开**：7 个 topic 与 Website 链接已在仓库 About 区生效，
> 匿名访问复核通过（见 §3 验收框）。GitHub 的 topics / homepage 没有 API 可写
> （`github-remote` MCP 只覆盖文件、Issue、PR，不覆盖仓库设置），所以那一步是在已登录
> `weideyouni` 的浏览器里点完的——这也解释了为什么它不能进 CI。
> 操作路径有个坑记在 §3.1：Topics 与 Website **不在 Settings → General 里了**，现在只在仓库首页
> About 右侧齿轮打开的弹窗里。

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

## 3 验收（人工核对，两条都做完才算 W5 完成）

- [x] O1-1 topics 生效：仓库页右侧出现 7 个标签 —— 2026-10-31 已勾，匿名抓取 `github.com/weideyouni/holoaeon` 读回
  `topics/cognitive-architecture`、`deterministic`、`llm`、`multi-agent`、`offline-first`、`reproducibility`、`zero-dependency` 共 7 条；
- [x] O1-2 homepage 生效：仓库页顶部出现 Website 链接 —— 同日已勾，About 区外链为
  `github.com/weideyouni/holoaeon/blob/main/benchmarks/README.md`；
- [ ] O2 Gitee 镜像克隆可跑通三步（见下）—— 镜像未建，如实留空。

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

## 4 Gitee 镜像说明（不做自动同步承诺）

镜像仓库由构建者手动推送，本项目不承诺自动同步，也不保证镜像与主仓同步时延：

```powershell
git clone https://gitee.com/<你的账号>/holoaeon.git
cd holoaeon
python scripts\launch_local.py status
```

三步快速开始（克隆 → status → selftest）若任一失败，先确认镜像是否是本仓最新 `main`：

```powershell
git log -1 --format=%H
```

与 GitHub 上 `main` 的 HEAD 比对，不一致就说明镜像滞后。

## 5 README 徽章（可选，一行）

```markdown
![DIFF=0](https://img.shields.io/badge/DIFF%3D0-2fc892cf9af6e755-1F6F5C)
![Guard](https://img.shields.io/badge/guard-100%25%20blocked-B0472C)
![Footprint](https://img.shields.io/badge/footprint-31ms%20%2F%201.69MiB-8A6A1E)
```

数字要随发版重跑 `python benchmarks\bench_public.py` 后手改；徽章是展示，证据在
`benchmarks/results-*.json`。徽章与证据不一致时，以 json 为准。
