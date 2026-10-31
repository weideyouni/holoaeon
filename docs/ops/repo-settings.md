# 仓库运营件（W5）

> 当前状态（2026-10-31）：代码已入库并推送（`main` = `afb31ed`，182 个受控文件），
> CI 已全绿（run #25：py3.8 / 3.10 / 3.12 三 job 全过，0 error 0 warning）。
> **只剩本节两个网页开关没打开**——GitHub 的 topics / homepage 没有 API 可写（`github-remote` MCP
> 只覆盖文件、Issue、PR，不覆盖仓库设置），必须在已登录 `weideyouni` 的浏览器里点两下。
> 下面步骤按「打开即做」写成，预计 3 分钟。

## 1 GitHub topics（网页手工一步，脚本改不了）

仓库首页 → 右上 ⚙ Settings → Topics，粘贴下面 7 个（逗号分隔）：

```
multi-agent, llm, deterministic, zero-dependency, cognitive-architecture, offline-first, reproducibility
```

这些词对应本项目的真实属性，不是堆量：`deterministic` 与 `reproducibility` 是 DIFF=0 协议的关键词，
`zero-dependency` 与 `offline-first` 是立身原则，`cognitive-architecture` 指 12 原语分层。

## 2 Homepage

Settings → Website，填：

```
https://github.com/weideyouni/holoaeon/blob/main/benchmarks/README.md
```

指向三个数字的页面，而不是仓库根：**让别人 30 秒看到证据，而不是先看长 README。**

## 3 验收（人工核对，两条都做完才算 W5 完成）

- [ ] O1-1 topics 生效：仓库页右侧出现 7 个标签；
- [ ] O1-2 homepage 生效：仓库页顶部出现 Website 链接，点开是 benchmarks 页面；
- [ ] O2 Gitee 镜像克隆可跑通三步（见下）。

### 3.1 一次做完的操作路径

1. 浏览器登录 `weideyouni` → 打开 `https://github.com/weideyouni/holoaeon`；
2. 点右上 ⚙ **Settings**；留在 **General** 页，右侧 **Topics** 输入框逐个粘贴 7 个词（每粘一个按空格或逗号确认）；
3. 同一页往下 **Website** 填 homepage URL → **Save changes**；
4. 回到仓库首页刷新：右侧应出现 7 个 topic 胶囊，顶部 About 区应出现 Website 链接。

### 3.2 做完怎么验证（不用登录也能查）

```powershell
# topics 是否生效（无需登录，读 HTML 里的 topic 链接）
(Invoke-WebRequest -UseBasicParsing "https://github.com/weideyouni/holoaeon").Content -match "topics/"
```

页面 HTML 里出现 `topics/multi-agent` 这类链接即生效；homepage 同理，仓库 About 区出现 `benchmarks/README.md` 的外链。
两项都勾上后把本节三条 `[ ]` 改成 `[x]` 并提交，W5 才算闭环。

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
