# -*- coding: utf-8 -*-
"""
HoloAeon 本地启动器 / 融合引导（Local Launcher）
================================================================================
把"冷/热插拔 + 内部融合协议 + 外部融合协议"落到一个可执行的本地入口。

概念：
  · 冷插拔（cold plug）：系统启动阶段一次性安装领域包（默认装全部八包）。
  · 热插拔（hot plug）：系统运行中不停止服务，动态 install 一个新领域包。
  · 内部融合协议（Internal Fusion）：内核组件经 Envelope/Bus 通信、Graph 编排、
    Memory 共享、Scheduler 心跳同步、Guard 把关 —— 全部在进程内确定性闭环。
  · 外部融合协议（External Fusion）：经 ModelAdapter 对接外部模型（本地/云端）
    与外部工具；离线时只做注册与路由决策，不发起真实网络请求。

用法（在项目根目录执行）：
  python scripts/launch_local.py status                # 健康快照
  python scripts/launch_local.py demo                  # 内部+外部融合全链路演示
  python scripts/launch_local.py run "任务文本"        # 提交任务（自动选 agent）
  python scripts/launch_local.py hotplug optimization  # 运行时热插拔加载一个包
  python scripts/launch_local.py selftest              # 17 组自检
"""
from __future__ import annotations

import argparse
import json
import os
import sys

# 允许从 scripts/ 直接运行：把项目根加入模块搜索路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from holoaeon import (
    AdaptiveGraph,
    Kernel,
    ModelAdapter,
)
from holoaeon.model_adapter import ModelBackend
from holoaeon.spec import DOC_VERSION, VERSION, AdaptiveGraphConfig
from holoaeon.packs import PACK_ORDER, get_pack


def _radius_for(n: int) -> int:
    """六边形邻域半径：radius=2→19 位置，radius=3→37，radius=4→61。"""
    if n <= 19:
        return 2
    if n <= 37:
        return 3
    return 4


# ------------------------------------------------------------ 冷插拔引导
def bootstrap(kernel: Kernel = None, *, packs=None,
               bind_graph: bool = True,
               bind_adapter: bool = True) -> Kernel:
    """冷插拔：启动阶段安装领域包，并绑定内部图与外部模型适配器。"""
    k = kernel or Kernel()
    selected = packs if packs is not None else PACK_ORDER
    for key in selected:
        get_pack(key).install(k)

    if bind_graph:
        # 内部融合：把已注册 agent 映射进自适应协作图（节点数随 agent 数）
        aids = sorted(k.agents.keys())
        cfg = AdaptiveGraphConfig(
            node_count=len(aids),
            geometry_radius=_radius_for(len(aids)),
        )
        graph = AdaptiveGraph(cfg)
        for idx, aid in enumerate(aids):
            graph.map_agent(aid, idx)
        k.attach_graph(graph)

    if bind_adapter:
        # 外部融合：注册本地与云端模型后端（离线只做路由，不联网）
        adapter = ModelAdapter()
        adapter.register_backend(ModelBackend(
            "local", "local",
            context_window=32768, input_cost=0.0,
            capabilities=["local", "offline"]))
        adapter.register_backend(ModelBackend(
            "cloud", "cloud",
            context_window=200000, input_cost=0.02,
            capabilities=["remote", "long-context"]))
        k.attach_adapter(adapter)
    return k


def cmd_status(_args) -> int:
    k = bootstrap()
    print(json.dumps(k.snapshot(), ensure_ascii=False, indent=2))
    return 0


def cmd_demo(_args) -> int:
    k = bootstrap()
    print("=" * 64)
    print("内部融合协议（Internal Fusion）：心跳 → 图 → 总线 → 记忆")
    print("=" * 64)
    k.tick()
    print("心跳一拍完成；图节点数：", k.graph.snapshot().get("nodes"))
    print("图边数：", k.graph.snapshot().get("edges"))
    print("总线已注册地址数：", len(k.agents))
    print("记忆条目：", k.memory.stats())

    print()
    print("=" * 64)
    print("外部融合协议（External Fusion）：模型后端路由（离线决策）")
    print("=" * 64)
    print("低成本任务路由 ->", k.adapter.route("短任务", strategy="cheapest"))
    print("长上下文任务路由 ->",
          k.adapter.route("长上下文", strategy="largest_context"))

    print()
    print("=" * 64)
    print("端到端任务（确定性技能）")
    print("=" * 64)
    out = k.submit("统计字数，这是一个用于演示的句子")
    print("all_ok:", out["all_ok"])
    for r in out["results"]:
        print(" -", r.get("agent_id"), r.get("status"),
              r.get("output", r.get("verdict", "")))
    return 0 if out["all_ok"] else 1


def cmd_run(args) -> int:
    k = bootstrap()
    out = k.submit(args.task)
    print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
    return 0 if out["all_ok"] else 1


def cmd_hotplug(args) -> int:
    # 先冷插拔除目标包外的其余包
    k = bootstrap(packs=[p for p in PACK_ORDER if p != args.pack])
    before = len(k.skills.names())
    print(f"热插拔前技能数：{before}；运行中加载包 '{args.pack}' …")
    info = get_pack(args.pack).install(k)
    after = len(k.skills.names())
    print("热插拔结果：", json.dumps(info, ensure_ascii=False))
    print(f"热插拔后技能数：{after}（新增 {after - before}，全程未重启）")
    return 0


def cmd_v2(_args) -> int:
    """V2 一键本地跑通：篡改自检 → kfold → REPRO_CORE → 策略 → 快照。"""
    import subprocess
    k = bootstrap()
    print("=" * 64)
    print("HoloAeon V2 本地装载自检（运行态 %s / 文档 %s）" % (VERSION, DOC_VERSION))
    print("=" * 64)
    steps = [
        ("W7 篡改自检", [sys.executable, os.path.join(ROOT, "scripts", "verax_verify.py"), "--mutate", "5"]),
        ("W8 分层留出", [sys.executable, os.path.join(ROOT, "scripts", "bench_semvec_kfold.py"), "--folds", "5"]),
        ("W9 证据链", [sys.executable, os.path.join(ROOT, "scripts", "repro_core_emit.py"), "--out", os.path.join(ROOT, "reports", "repro_core.jsonl")]),
        ("W11 快照", [sys.executable, os.path.join(ROOT, "scripts", "snapshot_v2.py")]),
    ]
    failed = []
    for name, cmd in steps:
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        tail = [ln for ln in proc.stdout.splitlines() if ln.strip()][-3:]
        print("\n[%s] rc=%d" % (name, proc.returncode))
        for ln in tail:
            print("    " + ln)
        if proc.returncode != 0:
            failed.append(name)
    print("\n" + "=" * 64)
    print("V2 本地装载：%s" % ("全部通过" if not failed else "失败 %s" % failed))
    print("=" * 64)
    return 0 if not failed else 1


def cmd_selftest(_args) -> int:
    from holoaeon.selftest import run_all
    r = run_all(verbose=True)
    print("==>", f"{r['passed']}/{r['groups']}")
    return 0 if r["ok"] else 1


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="HoloAeon 本地启动器")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status").set_defaults(func=cmd_status)
    sub.add_parser("demo").set_defaults(func=cmd_demo)
    p_run = sub.add_parser("run"); p_run.add_argument("task")
    p_run.set_defaults(func=cmd_run)
    p_hot = sub.add_parser("hotplug"); p_hot.add_argument("pack")
    p_hot.set_defaults(func=cmd_hotplug)
    sub.add_parser("selftest").set_defaults(func=cmd_selftest)
    sub.add_parser("v2").set_defaults(func=cmd_v2)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
