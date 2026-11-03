# -*- coding: utf-8 -*-
"""
demo_product —— holoaeon-demo 命令行入口（批3 · 产品层三件套）
================================================================================
新手小白一键体验：无需懂代码，安装后运行 `holoaeon-demo` 即可看到
「内核已装配 → 守卫生效 → 任务可跑」的确定性回执。

演示三条路径：
  1. hello    —— 内核装配体检（agents/skills 计数 + guard 状态）
  2. demo     —— 跑一个内置技能（如 health_check / 任一命中的技能）
  3. l9       —— L9 路径闸门现场演示（越界读被拦 / 授权写放行）

全部零依赖、无网络、无 GPU、确定性可复现。evidence_class=simulated。
"""
from __future__ import annotations

import sys

from .frontend_adapter import build_kernel
from .spec import VERSION, DOC_VERSION, RUNTIME_ID, MODE_SIMULATED


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    mode = args[0] if args else "hello"

    kernel = build_kernel()
    guard_state = {
        "guard_layers": kernel.cfg.guard.layers,
        "product_layer_guard": kernel.cfg.guard.product_layer_guard,
        "extra_layers": [n for n, _ in kernel.guard.layers
                         if n not in ("L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8")],
    }

    if mode == "l9":
        from .envelope import Envelope
        # 现场演示：越界读被 L9 拦（product_layer_guard 默认 True）
        v_deny = kernel.guard.inspect(Envelope.create(
            "main", "guard", "l9demo", {"x": 1},
            metadata={"path_requested": r"C:\Windows\system32",
                      "allowed_paths": (r"F:\doubaowork\holoaeon",),
                      "path_mode": "read"}))
        v_allow = kernel.guard.inspect(Envelope.create(
            "main", "guard", "l9demo", {"x": 1},
            metadata={"path_requested": r"F:\doubaowork\holoaeon\README.md",
                      "allowed_paths": (r"F:\doubaowork\holoaeon",),
                      "path_mode": "read"}))
        print("=== HoloAeon L9 路径闸门演示 ===")
        print("越界读 : %s %s %s" % (v_deny.action, v_deny.layer, v_deny.reason))
        print("授权读 : %s %s" % (v_allow.action, v_allow.layer))
        return 0

    if mode == "demo":
        # 跑一个确定性技能：让内核自己体检
        result = kernel.submit("status", None)
        print("=== HoloAeon demo 技能回执 ===")
        print("status : %s | all_ok=%s" % (result.get("status"), result.get("all_ok")))
        print("targets: %s" % (result.get("targets") or []))
        return 0

    # 默认 hello：装配体检
    print("=== HoloAeon 已就绪（holoaeon-demo）===")
    print("version : %s (doc %s)" % (VERSION, DOC_VERSION))
    print("runtime : %s" % RUNTIME_ID)
    print("mode    : %s" % MODE_SIMULATED)
    print("agents  : %d" % len(kernel.agents))
    print("skills  : %d" % len(kernel.skills.names()))
    print("guard   : %s" % guard_state)
    print("")
    print("下一步：用对话界面（豆包/千问/元宝）驱动 holoaeon —— 见 README 产品层章节。")
    print("封口密语：潮起开门，潮落闭嘴。evidence_class=simulated，仿真≠证明，碳基终裁。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
