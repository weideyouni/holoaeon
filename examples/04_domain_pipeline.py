# -*- coding: utf-8 -*-
"""示例 4：安装七大领域包并运行跨领域流水线。
运行：python examples/04_domain_pipeline.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holoaeon.kernel import Kernel
from holoaeon.packs import all_packs


def main() -> None:
    k = Kernel()
    # 安装全部七大领域包（写作/文献/科研/数据/成长/企业/量化）
    for pack in all_packs():
        pack.install(k)
    print("已安装：", len(k.agents), "个 agent，", len(k.skills.names()), "个技能")

    # 数据领域：描述统计
    stats = k.submit("basic stats", to="data_analyst",
                     args={"csv_text": "x,y\n1,10\n2,20\n3,30"})
    print("描述统计：", stats["results"][0]["output"]["x"])

    # 量化领域：夏普比率
    sharpe = k.submit("sharpe", to="quant_researcher",
                      args={"returns_s": "0.01,-0.02,0.03,0.01"})
    print("夏普比率：", sharpe["results"][0]["output"])

    # 成长领域：SMART 目标
    smart = k.submit("smart goal", to="growth_goal_coach",
                     args={"text": "30天内写3篇文章，每篇3000字"})
    print("SMART 检查：", smart["results"][0]["output"]["checks"])


if __name__ == "__main__":
    main()
