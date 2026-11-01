# 五地同步 · 刚性工程 DNA（HoloAeon V4）

- DNA ID：`SG-DNA-FIVE-SITE-SYNC-V1.0`
- 生效：2026-11-02（+08:00）
- 适用：HoloAeon / ivsa 双仓及其全部升级批次（B0–B9）
- 证据等级：`evidence_class=simulated`（记录来源为现场命令回读，非声明）
- 密令：潮起开门，潮落闭嘴

---

## 一、五地是什么（各自只干一件事）

| # | 地 | 角色 | 方向 | 判据 |
|---|---|---|---|---|
| S1 | 本地 `F:\doubaowork\holoaeon` | **源**（唯一写入点） | 所有改动先落本地 | `git rev-parse HEAD` |
| S2 | Gitee `weideyouni/holoaeon` | **权威镜像**（三地 DNA 的权威端） | S1 → S2 快进 | `git ls-remote … main` |
| S3 | GitHub `weideyouni/holoaeon` | **公开对齐端** | S1 → S3 快进；若远端领先则先对齐再推 | `git ls-remote origin main` |
| S4 | 向量海 `F:\doubaowork\vector-sea\holoaeon-v4-cold-hot-plug\` | **归档 / 检索端**（技能入口 + 逐文件哈希） | S1 → S4 复制 + 重建 `manifest.json` | `manifest.json` 逐文件 sha256 |
| S5 | Hugging Face `weideyouni/holoaeon`（model 仓） | **外部镜像端**（跨平台可访问） | S1 → S5 整树上传 | HF `commit sha` |

飞书 docx 为**阅读入口**，不参与哈希验收（在线协作内容可变），只在回执里记录 URL 与 `job_status`。

---

## 二、十条刚性规则（违反任一条即同步失败）

- **R1 单向**：本地是唯一写入点；Gitee 是权威镜像；GitHub 只做对齐；向量海只做归档；HF 只做外部镜像。禁止反向把远端改动直接覆盖本地。
- **R2 同提交**：一次同步结束时，S1/S2/S3 三处 `main` 必须是**同一个 commit sha**，不接受"内容差不多"。
- **R3 对象哈希验收**：每份归档文件记 `sha256`，整包记 `sha16`；回执里逐条列出，任何人可复算。
- **R4 只读铁律**：定时任务（日检/周检/月报）**只跑只读闸 + 出票据**，不 `push`、不改代码、不签字。
- **R5 冲突处置固定动作**：远端领先 → `git stash push`（只 stash 漂移文件）→ `git -c core.autocrlf=false rebase origin/main` → `git stash pop` → 再推。禁止 `push --force`、禁止 `reset --hard`。
- **R6 凭证纪律**：令牌只从 `C:\Users\Administrator\.gitee_token` 读取；`GIT_ASKPASS` 临时脚本用完即删；任何回执、日志、票据里不得出现令牌明文。
- **R7 维度闸**：同步前后各跑一次 `python scripts/v3_gate.py --json <path>`，A1 必须仍是 `{agents:25, skills:47, packs:9}`；变了就是同步带来污染，必须先回退。
- **R8 静默失败判据**：`git push` 回显成功不算成功，必须 `git ls-remote` **回读远端 ref**；HF 上传必须回读 `commit sha`。
- **R9 回执唯一**：一次同步一份 `*_receipt.json`，含五地状态 + 哈希 + 时间 + 密令；旧回执不覆盖，按日期并存。
- **R10 降级阶梯**：某地不可达时，其余四地照常完成，回执写明"某地 pending + 原因 + 重试入口"，禁止因一地失败而宣称整体完成。

---

## 三、一次标准同步的九步（可照抄）

1. **闸**：`python scripts/v3_gate.py --json reports/gate_sync_pre.json`（记 A1）。
2. **清单**：`python scripts/five_site_dna.py build` → `reports/five_site_manifest.json`（逐文件 sha256 + zip sha16）。
3. **提交**：`git add <显式路径>`（禁 `git add -A`）→ `git commit -m "<批次>: <一句话>"`。
4. **推 Gitee**：`GIT_ASKPASS=<临时bat> git push https://weideyouni@gitee.com/weideyouni/holoaeon.git main`。
5. **推 GitHub**：`git push origin main`；若被拒按 R5 处理。
6. **回读**：`git ls-remote` 两处，确认 sha 相同（R2/R8）。
7. **归档向量海**：复制产物 → 重建 `manifest.json` → 写回执。
8. **HF 镜像**：剔除 `.git`/`__pycache__` 后整树上传 → 回读 `commit sha`。
9. **收口**：`python scripts/five_site_dna.py verify`（比对清单与回执）→ 再跑一次 `v3_gate`（R7）→ 出票据。

---

## 四、机读规范

```json
{
  "dna_id": "SG-DNA-FIVE-SITE-SYNC-V1.0",
  "sites": {"S1":"local","S2":"gitee","S3":"github","S4":"vector_sea","S5":"huggingface"},
  "authority": "S2",
  "write_source": "S1",
  "acceptance": {"commit_equal": ["S1","S2","S3"], "object_hash": "sha256 per file", "package": "sha16"},
  "forbidden": ["push --force", "reset --hard", "add -A", "token in receipt"],
  "gates": {"pre": "v3_gate", "post": "v3_gate", "lock": "A1=25/47/9"},
  "failure_mode": "one site down -> others finish, receipt marks pending with reason"
}
```

对应文件：`data/five_site_dna.json`（同内容机读版）。
校验器：`scripts/five_site_dna.py build|verify`（纯标准库、离线、不联网、不调用 git）。

---

## 五、与既有 DNA 的关系

- 三地版本（本地→Gitee→GitHub）为 V1 基础，本 DNA 升为**五地**：新增 S4 向量海（归档）、S5 Hugging Face（外部镜像）。
- 与"维度不变"约束一致：同步只搬字节，不改 `spec.VERSION`、不改 `PACK_ORDER`、不动 ivsa 红线。
- 与定时任务边界一致：自动化只读，人签字才准入。

---

潮起开门，潮落闭嘴。
