# -*- coding: utf-8 -*-
"""示例 2：总线与语义路由 —— 主题订阅、直接寻址、路由规则。
运行：python examples/02_semantic_routing.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holoaeon.bus import Bus
from holoaeon.envelope import Envelope


def main() -> None:
    bus = Bus()

    # 1) 主题订阅：多个订阅者
    log = []
    bus.subscribe("task.new", lambda env: log.append(("sub", env.payload)))
    bus.subscribe("task.new", lambda env: log.append(("audit", env.payload)))

    # 2) 直接寻址：注册一个地址
    bus.register_address("executor", lambda env: f"executed:{env.payload['task']}")

    # 3) 路由规则：把某主题的广播改写到指定地址
    bus.register_route("task.route", "executor")

    # 发布主题
    bus.publish("task.new", {"task": "写一份报告"}, "planner")
    print("订阅者收到：", len(log), "条")

    # 走路由
    rep = bus.publish("task.route", {"task": "分析数据"}, "planner")
    print("路由结果：", rep[0]["out"])

    # 直接寻址
    direct = bus.send(Envelope.create("m", "executor", "d", {"task": "画图"}))
    print("寻址结果：", direct[0]["out"])


if __name__ == "__main__":
    main()
