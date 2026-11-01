---
name: holoaeon-release-sync-dna
description: "三地同步线路 DNA（Gitee 权威源 → GitHub 服务端全量对齐 → Hugging Face 镜像），验收口径是单个对象摘要哈希。当用户要求「同步 Gitee/GitHub/Hugging Face 三地」「从 Gitee 推到 GitHub」「发布/升级后收尾」「检查三端是否一致」「把仓库镜像到 HF」时使用；也用于修复 GitHub 落后、HF 与提交不一致、工作树脏导致推送失败等场景。"
---

# 三地同步线路 DNA

一条链、三个落点、一个验收字符串。

```
本地提交（唯一事实源）
  ├─① 本地 → Gitee        权威源，git push + ls-remote 回读签收
  ├─② Gitee → GitHub      服务端：仓库自带 workflow 每 30 分钟拉 Gitee 并对齐 main
  └─③ 本地 → Hugging Face 镜像：只传 git archive HEAD 的字节，逐文件 sha256 复核
```

## 角色与硬边界

| 站点 | 角色 | 允许差异 |
|---|---|---|
| 本地 Git | 提交产生地；工作树可以脏，但推送只认 commit | — |
| Gitee `weideyouni/holoaeon` | 权威源，`main` | — |
| GitHub `weideyouni/holoaeon` | 全量镜像，`main` 由 runner 强制对齐 | 仅 `.github/` |
| HF `weideyouni/holoaeon` | 代码镜像（model 型） | 仅 HF 自动生成的 `.gitattributes` |

`.github/` 是唯一允许两地不同的目录：GitHub 必须保留自己的工作流，Gitee 不需要。
其余对象必须逐个相等——这是「全量同步」的判据，不是「看起来差不多」。

## 验收口径：对象摘要哈希

三端各自算、字符串相等即等价（`.github/` 之外）：

```bash
git ls-tree -r --full-tree HEAD \
  | grep -v -P '^\S+ \S+ \S+\t\.github/' \
  | LC_ALL=C sort \
  | sha256sum | awk '{print $1}'
```

GitHub 侧由工作流算同一口径，发布到 `sync-status` 分支的 `.sync/object_digest.txt`；
本地由 `scripts/three_way_sync.py` 用同一口径复算。两者逐字符相等才算对齐。

`file_count` 天然是三端不一致的（GitHub 多一个 `sync-from-gitee.yml`、HF 多一个 `.gitattributes`），
所以**永远不要拿行数当验收**，只认 digest。

## 一条命令

```bash
python <skill>/scripts/three_way_sync.py --repo <仓库>            # 只检查
python <skill>/scripts/three_way_sync.py --repo <仓库> --push-gitee --push-hf
python <skill>/scripts/three_way_sync.py --repo <仓库> --json --receipt receipt.json
```

输出三行结论（Gitee / GitHub / HF），退出码：`0` 全 PASS、`1` 有端不一致、
`2` 缺令牌或依赖、`5` 工作树脏导致跳过推送。

单独用两个子能力：

```bash
python <skill>/scripts/hf_mirror.py --repo <仓库> --name holoaeon --verify all
python <仓库>/scripts/gitee_publish.py --repo <仓库> --owner weideyouni --name holoaeon --json
```

## 发布收尾五步（照这个顺序做，不许跳）

1. `git add -A && git commit`（只提交本次升级的内容；用户的在途草稿不进权威源）
2. 推 Gitee：`gitee_publish.py --owner weideyouni --name holoaeon`（回读 `ls-remote` 签收）
3. 触发 GitHub 对齐：MCP 写一个可被吞掉的文件，或等 schedule（当前实测 schedule 不可靠，见坑 12）
4. 验三端：`three_way_sync.py --repo <仓库> --hf-verify all --receipt receipt.json`，退出码 0 才算发布完成
5. 需要时补 HF：`--push-hf`（只镜像提交字节）

第 3 步的确定性写法（15 秒内起跑，实测 3 次全成功）：

```
create_or_update_file(owner=weideyouni, repo=holoaeon, path='.sync-nudge.txt',
                      content=<时间戳>, branch='main',
                      sha=<先 get_file_contents 取到的旧 blob sha>)
```

它造出的 commit 会被工作流的 force push 覆盖，main 上不留痕迹。

## 每一跳怎么做

### ① 本地 → Gitee

`gitee_publish.py` 是现成执行器：读 `~/.gitee_token`，`git push https://oauth2:<token>@gitee.com/...`，
推完必 `ls-remote` 回读比对 `local_sha == remote_after`。

- 本机 `origin` 指向 GitHub，**不是** Gitee：不显式传 `--owner weideyouni --name holoaeon` 会解析错。
- 工作树脏默认拒推（退出码 5）。只推已提交内容时先 `git commit`，不要用 `--allow-dirty` 掩盖。

### ② Gitee → GitHub（服务端，无需本机参与）

工作流 `.github/workflows/sync-from-gitee.yml`（原文见 `references/sync-from-gitee.yml`）：

- 触发：`schedule: '*/30 * * * *'`（每 30 分钟）、`workflow_dispatch`、`push: main`。
- 动作：`git fetch gitee` → `checkout -B align` → `git checkout origin/main -- .github`（保住自己的工作流）
→ 提交信息带 `gitee=<sha>` → `git push --force origin align:main`。
- 收尾：把 `git ls-tree` 清单、`object_digest.txt`、`heads.txt`、`last.log` 推到 `sync-status` 分支（孤儿分支，不污染 main）。

关键：**没有 `schedule` 的旧版只能被 push 触发**，Gitee 单独前进时 GitHub 永远追不上——这是这类机制最常见的漏。

### ③ 本地 → Hugging Face

`hf_mirror.py`：`git archive HEAD` 解到临时目录 → `upload_folder` → `list_repo_files` 比对缺失
→ `hf_hub_download` 回读，逐文件 sha256 与本地比较，全等才 `verified=true`。

- 令牌走 `huggingface_hub` 登录态（`~/.cache/huggingface/token`），不落命令行。
- 只传提交字节，**不传工作树**：见下面第 1 条坑。

## 踩过的坑（每条都真实发生过）

1. **CRLF 假同步**：Windows 工作树是 CRLF、git blob 是 LF。按工作树文件传 HF，抽样只对上 2/7，
   三端永不相等。镜像必须走 `git archive HEAD`（等价 blob 字节），不是磁盘上的文件。
2. **行数当验收会误导**：GitHub 207 / HF 207 / 本地 206，差的那几个是 `.github/` 与 `.gitattributes`。
3. **本机到 GitHub 是半通的**：`git push`（`SSL routines::unexpected eof`）与 `api.github.com` 都不通，
   但 `raw.githubusercontent.com` 用 urllib 能直读。所以 GitHub 侧只做「服务端对齐 + 只读验收」，
   本机永不当写入方。
4. **改 GitHub 工作流只能用 MCP**：`create_or_update_file` 先 `get_file_contents` 取同 ref 的 blob sha，
   否则更新被拒；本地 `git push` 改不了。
5. **手工触发一次 = 往 main 写一个可被对齐吞掉的文件**：MCP 写文件产生 push 事件 → 跑一轮同步 →
   该文件被 force push 覆盖，零残留。没有 dispatch API 时用这招。
6. **孤儿分支必须 `git rm -rqf .`**：否则 `sync-status` 会带上整棵旧的 main 树而 push 失败。
7. **HF 的 `.gitattributes` 是自动生成的**：`list_repo_files` 会比 tracked 多 1，不要判成脏数据。
8. **Space 卡片配色白名单**：`red yellow green blue indigo purple pink gray`（**无 teal**）。
9. **dirty 工作树里的未提交改动**（如 `reports/attestation.md`）属于用户的在途工作，
   既不要顺手 commit 进权威源，也不要让镜像把它带上：`git archive` 天然规避。
10. **`run:` 默认是 `bash -e`**：任何一条 git 失败就让整步变成 `exit code 128`，而匿名看不了日志，
   只能看到两个光秃秃的 128。工作流必须 `set +e` 并在每条命令后写 `*_rc=$?` 记账，
   把状态落到 `sync-status` 的 `last.log`，否则故障不可诊断。
11. **push 触发的本轮可能偶发失败、下一轮又正常**：同一份工作流 04:00 那轮 128 失败，04:08 那轮全 `rc=0`。
    验收只认 `sync-status` 里最新一轮的 `push_rc=0` + `object_digest` 相同，不认「我推过」。
12. **`schedule` 是免费的但不保证准时**：GitHub cron 按 UTC、可能排队延迟甚至丢轮次，
    两轮窗口都没跑起来时要靠第 5 条（MCP 写一个可被吞掉的文件）做确定性补触发。

## 验收判据（逐条可判定）

- **A1 三端同源**：本地 `HEAD` = Gitee `main` head = GitHub 提交信息里的 `gitee=head`。
- **A2 对象相等**：本地 digest = GitHub `.sync/object_digest.txt`，逐字符相同。
- **A3 字节相等**：HF 抽样（推荐 `--verify all`）sha256 与本地 blob 全等，缺失文件数为 0。
- **A4 无人工**：`sync-status` 最新一轮的 `event` 为 `schedule`，且 `push_rc=0`、`object_digest` 与本地相同。
  GitHub cron 会延迟丢轮，等不到就退一步用 MCP 写文件触发（`event=push` 同样算出 `push_rc=0`），
  并在交付里写明这一轮是人触发还是定时触发——不许把 push 触发的成功说成「定时已生效」。

## 不做

- 不向 GitHub 反向镜像（用户已拒绝），不 `git push` 到 GitHub。
- 不为了凑一致性改 `VERSION`、重建 golden、调参刷分；内容以提交为准，机制只负责搬运。
- 不把 `vector-sea`（Gitee 私有，107 MB）纳入本机制。
- 不用行数、时间戳、commit 数量当一致性证据。

潮起开门，潮落闭嘴。
