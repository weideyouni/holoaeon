# -*- coding: utf-8 -*-
"""把 README / VERAX 设计说明 / 投喂包 合成一份可整段阅读的交付文档（供飞书入库）。"""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTS = [
    ("README_VERAX_20261031.md", "一、新版 README（升级版开源项目说明）"),
    ("docs/VERAX.md", "二、VERAX 设计说明（字段表 / 分级 / 门禁 / 限制）"),
    ("AGENT_FEED_VERAX_20261031.md", "三、面向智能体的一键复制投喂包"),
]
HEADER = """# HoloAeon VERAX 可信层 · 交付全文

升级日期：2026-10-31　|　版本：v0.9.1 + audit
产出维度不变：25 智能体 / 47 技能 / 9 领域包 + 7 扩展包 / 34 单测 / 24 自检 / 红线零违规 / 零依赖 / 离线 / 确定性

实测回执（本轮真实跑出）：

- 自检 `==> 24/24`；`tests/` `Ran 34 tests / OK`；`tests/verax/` `Ran 16 tests / OK`
- 红线 `扫描文件数 40 / 结果 干净（零违规）`
- 门禁 `green VERAX_EXIT=0 / yellow VERAX_EXIT=2 / red VERAX_EXIT=1`，三色 verdict_hash 各不相同
- 热插拔 `40 → 47（新增 7，全程未重启）`；本地融合 `总线 25 地址 / all_ok=True`
- 规模：`holoaeon/` 40 个 py / 11,408 行（核心 16/3,851，packs 18/6,872，audit 6/685）

---

"""


def main():
    out = []
    out.append(HEADER)
    for rel, title in PARTS:
        path = os.path.join(ROOT, rel)
        with io.open(path, "r", encoding="utf-8") as handle:
            body = handle.read()
        # 把各分册一级标题降为二级，保留内部层级
        body = body.replace("\n# ", "\n## ").replace("# ", "## ", 1)
        out.append("## " + title + "\n\n")
        out.append(body.rstrip() + "\n\n---\n\n")
    target = os.path.join(ROOT, "docs", "HOLOAEON_VERAX_FULL_20261031.md")
    with io.open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("".join(out))
    print("[saved]", target, len("".join(out)), "chars")


if __name__ == "__main__":
    main()
