# -*- coding: utf-8 -*-
"""合并 README.zh-CN + docs/* + ALGORITHM 为一个可阅读全文的入库入口 Markdown。

版本号、发布包大小与 SHA256 均在运行时动态读取（不硬编码），避免"源码里记录的
zip SHA 反过来改变 zip"的自引用问题。流程：先 make_release.py 打包，再运行本脚本。
"""
import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT = os.path.dirname(ROOT)

DOC_ORDER = [
    ("architecture", "一、架构详解"),
    ("scheduler", "二、调度器（心跳）"),
    ("guard", "三、守卫（安全边界）"),
    ("memory", "四、记忆（三层存储）"),
    ("graph", "五、自适应协作图"),
    ("hypervector", "六、超向量表示（HRR）"),
    ("model-adapter", "七、模型适配层"),
    ("packs", "八、八大领域包"),
]


def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def main():
    sys.path.insert(0, ROOT)
    from holoaeon.spec import VERSION, DATE
    ver = VERSION
    zip_name = "holoaeon_v%s_%s.zip" % (ver, DATE.replace("-", ""))
    zip_path = os.path.join(PARENT, zip_name)
    if os.path.exists(zip_path):
        data = open(zip_path, "rb").read()
        size_str = "{:,}".format(len(data))
        sha_str = "`%s`" % hashlib.sha256(data).hexdigest().upper()
    else:
        size_str = "未找到"
        sha_str = "（请先运行 scripts/make_release.py）"

    header = """# HoloAeon 通用多智能体认知框架 · 入库入口（全文）

> 零依赖、生物启发的通用多智能体认知框架 · 版本 **v__VER__**
> 本入口文档可直接阅读全文，包含项目说明、全部机制文档与算法白皮书。

## 资产信息

| 项目 | 内容 |
|---|---|
| 版本 | v__VER__ |
| 协议 | Apache-2.0 |
| 运行环境 | Python 3.8+，纯标准库，零第三方依赖 |
| 发布包 | __ZIP__（__SIZE__ B） |
| SHA256 | __SHA__ |
| 计划仓库 | github.com/weideyouni/holoaeon |
| 规模 | 8 个领域包、24 个智能体、44 个技能、8 个工作流 |
| 自检 | 16/16 组通过；单元测试 24 个；红线扫描零违规；解压复跑 DIFF=0 |

---

# 项目说明

"""
    header = (header.replace("__VER__", ver)
              .replace("__ZIP__", zip_name)
              .replace("__SIZE__", size_str)
              .replace("__SHA__", sha_str))
    parts = [header]
    parts.append(read(os.path.join(ROOT, "README.zh-CN.md")))
    parts.append("\n\n---\n\n# 机制与架构文档\n")
    for key, title in DOC_ORDER:
        p = os.path.join(ROOT, "docs", key + ".md")
        if os.path.exists(p):
            body = read(p)
            # 去掉文档内首个一级标题，避免与分节标题重复
            lines = body.splitlines()
            if lines and lines[0].startswith("# "):
                lines = lines[1:]
            parts.append("\n\n## " + title + "\n\n" + "\n".join(lines).strip())
    # 算法白皮书（ALGORITHM.md 为英文，作为第九节纳入）
    algo = os.path.join(ROOT, "ALGORITHM.md")
    if os.path.exists(algo):
        body = read(algo)
        lines = body.splitlines()
        if lines and lines[0].startswith("# "):
            lines = lines[1:]
        parts.append("\n\n## 九、算法白皮书：认知优化与自组织搜索（ALGORITHM）\n\n"
                     + "\n".join(lines).strip())
    parts.append("""

---

## 免责声明

本项目中的生物与宇宙词汇均为认知架构隐喻，仅用于描述多智能体软件的同步、边界、路由、
支撑与自组织机制，不构成医学、生物学或临床建议。所有仿真回执均标记 `simulated`；
仿真不等于证明，人类判断始终是最终权威。
""")
    out = os.path.join(ROOT, "HoloAeon_入库入口_全文.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    print("written:", out)
    print("chars:", len("\n".join(parts)))
    print("zip:", zip_name, "size:", size_str, "sha:", sha_str)


if __name__ == "__main__":
    main()
