# 仓库运营件（W5）

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
