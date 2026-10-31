# HoloAeon V2 完成升级

**一句话：HoloAeon V2（文档版 0.9.2）赋能升级已完成——五个工作包全部旁挂落地并实测通过，维度不变、黄金值未漂移。**

## 实测（2026-11-01，本机实跑）

| 项 | 值 |
|---|---|
| 版本 | 运行态 0.9.1 / 文档 0.9.2（双版本号，不动 VERSION 以免黄金漂移） |
| 维度 | 25 智能体 / 47 技能 / 9 领域包 + 8 扩展包 / 34 单测（34·21·5 三套分开）/ 25 自检——全部未变 |
| 确定性 | DIFF=0 `2fc892cf9af6e755` 未漂移；篡改后 `f42c8229ee5acd73` |
| 门禁 | `conclusion=green` `verdict_hash=f2fb0236c8bbd721` `VERAX_EXIT=0` |
| W7 篡改自检 | `mutations=5 changed=5 sensitive=True` |
| W8 分层留出 | `mean=0.9957 std=0.0085`（folds=5，limit 0.05）；跨词汇锚点 11/12，未调参刷成 12/12 |
| W9 证据链 | `reports/repro_core.jsonl` 10 行，`sha16=e320111ec8491b05`，`--check` 全行复算一致 |
| W10 fail-loud | 漂移 / 篡改不敏感 / 黄金未冻结 → 必红，禁 advice 降级 |
| W11 快照 | `generated_at` 固定 2026-11-01，两轮现算字节一致（可回放） |
| 红线 | 44 文件扫描，0 违规 |

## 双端同步状态

- **Gitee（权威源）**：`https://gitee.com/weideyouni/holoaeon`，`main` 为全量代码 + 文档 + 证据。
- **GitHub（全量镜像）**：内容由 Gitee `main` 强制对齐，不做二次编辑；如需改动，请改 Gitee 后再同步，避免两侧分叉。
- 同步方式：本地到 GitHub 的 HTTPS/TLS 通道在本机不可用（`schannel` 与 `unexpected eof` 均复现），故改用 GitHub 侧一次性工作流从 Gitee 拉取并对齐 `main`。

## 入口

- 规范 v0.2：`docs/spec-diff0-v0.2.md`（§7 证据协议 / §8 fail-loud / §9 已知限制）
- 接手页：`snapshot/SNAPSHOT_V2.md` 与 `snapshot/project_snapshot_v2.json`
- 证据链：`reports/repro_core.jsonl`
- 投喂包：`AGENT_FEED_V2_DONE_20261101.md`
- 全文记录（飞书）：https://my.feishu.cn/docx/BrpJdSnaFowjrgxazb1cJjM4nPd

全部条目 `evidence_class=simulated`：仿真 ≠ 证明，碳基终裁。潮起开门，潮落闭嘴。
