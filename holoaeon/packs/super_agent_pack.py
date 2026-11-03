# -*- coding: utf-8 -*-
"""
SuperAgentPack —— 确定性自主调度扩展包（第 16 个扩展包）
================================================================================
V16-SUPER-AGENT-DISTILLATION · DeepSeek Super-agent 对标蒸馏（精华 D-01~D-05，
糟粕 X-01~X-04 剔除），第一性原理交集 = 确定性的自主调度：

  5 技能（对应 router_layer/event_filter/external_watchdog 三模块 + 隔离/扫描）：
    router_dispatch    — Router 规则分派（D-01，规则驱动非 LLM）
    event_two_filter   — 两级过滤（D-02，L1 快滤 + L2 深查）
    watchdog_monitor   — 外部 Watchdog 监控（D-03，只告警不拦截）
    context_isolate    — Worker 上下文隔离（D-04，强化 Agent inbox 隔离）
    proactive_scan     — 确定性主动扫描（D-05，规则扫描非 LLM 推理）

3 角色 / 1 工作流；key = "super_agent"（EXTRA_PACK_ORDER 15→16）。
纯标准库、零外部依赖、确定性、离线；
维度不变（只进 EXTRA_PACK_REGISTRY，不进 PACK_ORDER —— A1 的 25/47/9 不受影响）。
"""
from __future__ import annotations

import os
import sys
from typing import Any, Dict, List, Optional

from .base import DomainPack, RoleSpec, SkillSpec, WorkflowSpec
from ..event_filter import EventFilter
from ..external_watchdog import ExternalWatchdog
from ..router_layer import RouterLayer

# 确定性默认分派规则（同输入→同分派结果，非 LLM）
_DEFAULT_RULES = [
    ("写文章", "writing_planner", 0),
    ("分析数据", "data_analyst", 0),
    ("监控", "watchdog_operator", 1),
    ("审查", "reviewer", 1),
    ("修复", "debugger", 1),
]


# ============================================================ 技能：Router 规则分派
def router_dispatch(task: str = "", rules: Optional[List[dict]] = None,
                    **_a: Any) -> dict:
    """Router 规则分派（D-01）：关键词规则匹配，确定性分派目标 Agent。"""
    r = RouterLayer()
    for pat, target, pri in rules or _DEFAULT_RULES:
        r.register_rule(pat, target, pri)
    target = r.receive(str(task or ""))
    return {"status": "ok", "target": target,
            "rules_count": r.status()["rules_count"],
            "queue_size": r.status()["queue_size"]}


# ============================================================ 技能：两级过滤
def event_two_filter(event_text: str = "", **_a: Any) -> dict:
    """两级过滤（D-02）：L1 快速预过滤 + L2 深度检查，确定性过滤事件。"""
    f = EventFilter()
    result = f.filter(str(event_text or ""))
    return {"status": "ok", "passed": result["passed"],
            "level": result["level"], "reason": result["reason"]}


# ============================================================ 技能：外部 Watchdog 监控
def watchdog_monitor(level: str = "info", message: str = "",
                     detail: Optional[dict] = None, **_a: Any) -> dict:
    """外部 Watchdog 监控（D-03）：只告警不拦截，记录健康快照。"""
    w = ExternalWatchdog(".")
    alert = w.alert(str(level), str(message or "health_check"),
                    dict(detail or {}))
    snap = w.snapshot()
    return {"status": "ok", "alert_level": alert["level"],
            "alert_message": alert["message"],
            "alerts_count": snap["alerts_count"],
            "history_count": snap["history_count"]}


# ============================================================ 技能：Worker 上下文隔离
_ISOLATION_BUCKETS: Dict[str, Dict[str, Any]] = {}


def context_isolate(worker_id: str = "worker", context: Optional[dict] = None,
                    **_a: Any) -> dict:
    """Worker 上下文隔离（D-04）：每个 Worker 独立隔离桶，互不串扰。"""
    wid = str(worker_id or "worker")
    bucket = _ISOLATION_BUCKETS.setdefault(wid, {})
    bucket.update(dict(context or {}))
    return {"status": "ok", "worker_id": wid,
            "isolated": True,
            "bucket_keys": sorted(bucket.keys()),
            "bucket_values": dict(bucket),
            "bucket_size": len(bucket)}


# ============================================================ 技能：确定性主动扫描
def proactive_scan(root: str = ".", limit: int = 200, **_a: Any) -> dict:
    """确定性主动扫描（D-05）：规则扫描 *.py 文件计数（非 LLM 推理）。"""
    root = str(root or ".")
    count, dirs = 0, 0
    for dirpath, _dirnames, filenames in os.walk(root):
        dirs += 1
        for fn in filenames:
            if fn.endswith(".py") and count < int(limit):
                count += 1
        if count >= int(limit):
            break
    return {"status": "ok", "root": root, "py_files_seen": count,
            "dirs_scanned": dirs, "limit": int(limit)}


# ============================================================ 扩展包定义
class SuperAgentPack(DomainPack):
    key = "super_agent"
    name = "确定性自主调度（Super-agent 对标蒸馏）"
    description = (
        "蒸馏 DeepSeek Super-agent 五大精华适配 HoloAeon 确定性：Router 规则分派"
        "（D-01）+ 事件两级过滤（D-02）+ 外部 Watchdog（D-03）+ Worker 上下文隔离"
        "（D-04）+ 确定性主动扫描（D-05）；剔除多渠道/LLM 主动性等 4 糟粕；"
        "第一性原理交集=确定性的自主调度，纯标准库离线可跑"
    )

    skills = [
        SkillSpec("router_dispatch", router_dispatch,
                  "Router 规则分派（D-01）：关键词规则匹配确定性分派目标 Agent",
                  tags=["super_agent", "router", "dispatch", "deterministic"],
                  inputs={"task": "str", "rules": "list"}),
        SkillSpec("event_two_filter", event_two_filter,
                  "两级过滤（D-02）：L1 快速预过滤 + L2 深度检查确定性过滤事件",
                  tags=["super_agent", "filter", "event", "two_level"],
                  inputs={"event_text": "str"}),
        SkillSpec("watchdog_monitor", watchdog_monitor,
                  "外部 Watchdog 监控（D-03）：只告警不拦截，记录健康快照",
                  tags=["super_agent", "watchdog", "monitor", "alert"],
                  inputs={"level": "str", "message": "str", "detail": "dict"}),
        SkillSpec("context_isolate", context_isolate,
                  "Worker 上下文隔离（D-04）：独立隔离桶互不串扰",
                  tags=["super_agent", "isolation", "context", "worker"],
                  inputs={"worker_id": "str", "context": "dict"}),
        SkillSpec("proactive_scan", proactive_scan,
                  "确定性主动扫描（D-05）：规则扫描 *.py 文件计数（非 LLM 推理）",
                  tags=["super_agent", "proactive", "scan", "rule"],
                  inputs={"root": "str", "limit": "int"}),
    ]

    roles = [
        RoleSpec("router_coordinator", "Router 协调员（持续运行层）：接收任务→规则分派→聚合结果",
                 ["router_dispatch"]),
        RoleSpec("filter_engineer", "过滤工程师（两级过滤）：L1 快滤 + L2 深查事件",
                 ["event_two_filter"]),
        RoleSpec("watchdog_operator", "Watchdog 操作员（外部监控）：告警 + 健康快照 + 主动扫描",
                 ["watchdog_monitor", "proactive_scan"]),
    ]

    workflows = [
        WorkflowSpec("super_agent_flow",
                     ["router_coordinator", "filter_engineer",
                      "router_coordinator", "watchdog_operator",
                      "watchdog_operator", "router_coordinator"],
                     "接收→分派→过滤→执行→监控→聚合（六步确定性自主调度闭环）"),
    ]


def pack_summary() -> Dict[str, Any]:
    p = SuperAgentPack()
    return {"key": p.key, "skills": len(p.skills), "roles": len(p.roles),
            "workflows": len(p.workflows)}


def main(argv: Optional[List[str]] = None) -> int:
    """CLI 入口（演示）：5 技能 / 3 角色 / 1 工作流 + 端到端演示。"""
    args = list(sys.argv[1:] if argv is None else argv)
    print("== HoloAeon 确定性自主调度扩展包（super_agent 第16扩展包）==")
    print("包契约:", pack_summary())
    if args and args[0].strip() == "--selfcheck":
        # D-01 规则分派确定性
        r1 = router_dispatch("帮我写一篇文章")
        # D-02 两级过滤
        r2 = event_two_filter("代码审查发现一个bug")
        # D-03 外部监控
        r3 = watchdog_monitor("warn", "test alert")
        # D-04 上下文隔离
        r4 = context_isolate("worker_a", {"slot": 1})
        r5 = context_isolate("worker_b", {"slot": 2})
        # D-05 确定性主动扫描
        r6 = proactive_scan("holoaeon", limit=50)
        ok = (len(SuperAgentPack.skills) == 5
              and len(SuperAgentPack.roles) == 3
              and len(SuperAgentPack.workflows) == 1
              and r1["target"] == "writing_planner"
              and r2["passed"] is True and r2["level"] == "L2"
              and r3["alerts_count"] == 1
              and r4["worker_id"] == "worker_a"
              and r5["worker_id"] == "worker_b"
              and r4["bucket_values"] != r5["bucket_values"]
              and r6["status"] == "ok")
        print("自检:", "PASS" if ok else "FAIL",
              "skills=5 roles=3 workflows=1 D01=%s D02=%s D03=%s D04=%s D05=%s"
              % (r1["target"], r2["level"], r3["alerts_count"],
                 r4["bucket_values"] != r5["bucket_values"], r6["py_files_seen"]))
        return 0 if ok else 1
    print("5 技能: %s" % ", ".join(s.name for s in SuperAgentPack.skills))
    print("3 角色: %s" % ", ".join(r.name for r in SuperAgentPack.roles))
    print("1 工作流: %s" % ", ".join(w.name for w in SuperAgentPack.workflows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
