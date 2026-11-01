# -*- coding: utf-8 -*-
"""
launch_v3.py —— V3 本地装载与内外融合全链路（旁挂入口）
================================================================================
把 V3 的八个旁挂包装进本地内核，跑一遍：
  内部融合：心跳 → 图 → 总线 → 统一调用协议管道 → span 树 → 事件流
  外部融合：模型后端路由（离线决策）+ 桥 conformance

不改内核字节、不改既有入口；launch_local.py 仍可单独使用。

用法：
    python scripts\\launch_v3.py
    python scripts\\launch_v3.py --json reports\\v3_launch.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "bridges"))

from holoaeon.audit.fields import reprohash  # noqa: E402
from holoaeon.audit.span_tree import SpanRecorder, SpanTree  # noqa: E402
from holoaeon.event_channel import EventChannel  # noqa: E402
from holoaeon.runnable import (  # noqa: E402
    CallConfig, GuardRunnable, HookChain, Pipeline, SkillRunnable, SinkRunnable,
)
from holoaeon.skill_schema import call_with_repair, schema_from_inputs, validate  # noqa: E402
from launch_local import bootstrap  # noqa: E402

from conformance import Bridge, conformance  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="")
    a = ap.parse_args()

    k = bootstrap()
    report = {"doc_version": "0.9.3", "runtime_version": None,
              "evidence_class": "simulated"}

    from holoaeon.spec import DOC_VERSION, VERSION
    report["doc_version"] = DOC_VERSION
    report["runtime_version"] = VERSION

    # ---------------------------------------------------------- 内部融合
    k.tick()
    internal = {
        "agents": len(k.agents),
        "skills": len(k.skills.names()),
        "graph": k.graph.snapshot() if k.graph else {},
        "memory": k.memory.stats(),
    }

    ev = EventChannel()
    ev.emit("run_start", {"run": "launch_v3"})

    # 选一个能接受单文本参数的确定性技能
    skill_name = k.skills.best("统计字数 文本 单词")
    skill = k.skills.get(skill_name)
    schema = schema_from_inputs({"text": "str"})
    pre = validate(schema, {"task": ""})
    note = "技能 %s 的 manifest 未声明 inputs，按文本注入" % skill_name

    tree = SpanTree("launch_v3")
    rec = SpanRecorder(tree)
    root = rec.span("pipeline", "run")

    composition = Pipeline([
        GuardRunnable(k.guard),
        SkillRunnable(skill),
        SinkRunnable(),
    ])
    hooks = HookChain().add("trace-route", "route",
                            lambda ctx: ev.emit("route", {"node": ctx.get("node", "")}) or ctx)
    cfg = CallConfig(trace=rec, hooks=hooks,
                     budget={"calls": 0, "max_calls": 5})
    res = composition.call({"task": "统计字数，这是 V3 本地装载的演示句。"}, cfg)
    ev.emit("skill_call", {"skill": skill_name, "status": res.get("status")})
    rec.close(root, 3.0, "ok")
    ev.emit("run_end", {"status": res.get("status")})

    pipeline_part = {
        "skill": skill_name,
        "status": res.get("status"),
        "trail": res.get("trail"),
        "output_type": type(res.get("output")).__name__,
        "span_summary": tree.summary(),
        "events": ev.counts(),
        "budget": cfg.budget,
        "schema_probe_ok": pre["ok"],
        "schema_note": note,
    }

    # 内核侧同任务复核：开不开旁挂，内核字节一致
    bus = k.submit("统计字数，这是 V3 本地装载的演示句。")
    pipeline_part["kernel_hash"] = reprohash(bus)
    pipeline_part["kernel_all_ok"] = bus["all_ok"]

    # ---------------------------------------------------------- 外部融合
    routes = {"cheapest": k.adapter.route("短任务", strategy="cheapest"),
              "largest_context": k.adapter.route("长上下文任务",
                                                 strategy="largest_context")}
    bridge = conformance(Bridge())
    external = {"routes": routes, "bridge": bridge["verdict"],
                "bridge_checks": bridge["passed"], "network": "none"}

    report["internal"] = internal
    report["pipeline"] = pipeline_part
    report["external"] = external
    report["all_ok"] = bool(pipeline_part["kernel_all_ok"] and res.get("status") == "ok"
                            and bridge["verdict"] == "PASS")

    if a.json:
        os.makedirs(os.path.dirname(os.path.abspath(a.json)), exist_ok=True)
        with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(report, fh, ensure_ascii=False, indent=2, sort_keys=True)
            fh.write("\n")

    print("=" * 72)
    print("HoloAeon V3 本地装载（运行态 %s / 文档 %s）" % (VERSION, DOC_VERSION))
    print("=" * 72)
    print("内部融合   agents=%d skills=%d graph_nodes=%s memory=%s"
          % (internal["agents"], internal["skills"],
             internal["graph"].get("nodes"), internal["memory"]))
    print("统一协议   skill=%s status=%s trail=%s"
          % (skill_name, res.get("status"), res.get("trail")))
    print("span 树    %s" % json.dumps(tree.summary(), ensure_ascii=False))
    print("事件流     %s" % json.dumps(ev.counts(), ensure_ascii=False))
    print("内核复核   all_ok=%s hash=%s" % (bus["all_ok"], pipeline_part["kernel_hash"]))
    print("外部融合   routes=%s" % json.dumps(routes, ensure_ascii=False))
    print("桥 conformance  %s (%d/%d)" % (bridge["verdict"], bridge["passed"], bridge["total"]))
    print("-" * 72)
    print("ALL_OK=%s" % report["all_ok"])
    return 0 if report["all_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
