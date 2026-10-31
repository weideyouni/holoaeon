# -*- coding: utf-8 -*-
"""把 V3 各分册拼成一份可整篇导入飞书的合订稿（供向量海同步/入库入口阅读全文）。"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "HOLOAEON_DIFF0_FULL_20261031.md")

PARTS = [
    ("README_DIFF0_20261031.md", "一 · 对外 README（三数字徽章版）"),
    ("benchmarks/README.md", "二 · 公开基准实测（evidence_class=simulated）"),
    ("docs/spec-diff0.md", "三 · 确定性 Agent 运行时规范 v0.1"),
    ("docs/cookbooks.md", "四 · cookbook 索引"),
    ("cookbooks/01_make_your_skill/README.md", "五 · Cookbook 01 做一个你自己的技能"),
    ("cookbooks/02_add_ledger_to_your_agent/README.md", "六 · Cookbook 02 给 Agent 加账本"),
    ("cookbooks/03_offline_deploy_old_laptop/README.md", "七 · Cookbook 03 离线部署旧笔记本"),
    ("snapshot/SNAPSHOT.md", "八 · 项目快照（供其他智能体接手）"),
    ("AGENT_FEED_DIFF0_20261031.md", "九 · 面向智能体的一键复制投喂包"),
    ("docs/ops/repo-settings.md", "十 · 仓库运营件（topics / homepage / 镜像）"),
]

head = [
    "# HoloAeon DIFF=0 升级合订稿（2026-10-31）",
    "",
    "> 本文件是「确定性资产化」这一轮升级的全量证据合订本：对外 README、公开基准、",
    "> 开放规范、三本 cookbook、项目快照、智能体投喂包、仓库运营件。",
    "> 三个数字：`DIFF=0 2fc892cf9af6e755 | 拦截 100% | 冷装配 ≈31ms / 峰值 1.69MiB`。",
    "> 全部条目 `evidence_class=simulated`：仿真 ≠ 证明，碳基终裁。",
    "",
    "---",
    "",
]

lines = list(head)
for rel, title in PARTS:
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        lines += ["> 缺失：%s" % rel, ""]
        continue
    with open(p, encoding="utf-8") as fh:
        body = fh.read().strip()
    lines += ["## %s" % title, "", "> 源文件：`%s`" % rel, "", body, "", "---", ""]

text = "\n".join(lines)
with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(text)
print("written:", OUT)
print("chars:", len(text))
