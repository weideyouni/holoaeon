# -*- coding: utf-8 -*-
"""内部融合协议 + 外部融合协议：全部离线、确定性、零网络。

内部融合（进程内闭环）：统一信封 → 皮肤八层守卫 → 消息总线投递 → 心跳节拍 → 技能匹配。
外部融合（出内核）：模型后端只做"路由决策"，不发起任何真实请求；
                    回执一律标 mode=simulated，证明"决策已算、调用未发"。
"""
from __future__ import annotations

from typing import Any, Dict, List

from ..envelope import Envelope
from .manifest import digest_of

BENIGN = "统计这周的康复训练时长并汇总"
DANGEROUS = "rm -rf / && eval(payload)"


def _ensure_adapter(kernel: Any) -> Any:
    """内核没有适配器时就地装一个（与本地启动器同口径，仅注册不联网）。"""
    if kernel.adapter is not None:
        return kernel.adapter
    from ..model_adapter import ModelAdapter, ModelBackend

    adapter = ModelAdapter()
    adapter.register_backend(ModelBackend(
        "local", "local", context_window=32768, input_cost=0.0,
        capabilities=["local", "offline"]))
    adapter.register_backend(ModelBackend(
        "cloud", "cloud", context_window=200000, input_cost=0.02,
        capabilities=["remote", "long-context"]))
    kernel.attach_adapter(adapter)
    return adapter


def internal_fuse(kernel: Any) -> Dict[str, Any]:
    """走一遍内部融合六步，每步给证据，缺一步就不算打通。"""
    steps: List[Dict[str, Any]] = []

    env = Envelope.create("main", "fusion.probe", "task", {"task": BENIGN},
                          metadata={"permission": 0})
    env_dict = env.to_dict()
    steps.append({"step": "envelope", "ok": bool(env_dict.get("message_id")),
                  "evidence": sorted(env_dict.keys())[:8]})

    benign = kernel.guard.inspect(env)
    danger = kernel.guard.inspect(Envelope.create(
        "main", "fusion.probe", "task", {"task": DANGEROUS},
        metadata={"permission": 0}))
    discriminated = (danger.action == "block") or (danger.action != benign.action)
    steps.append({"step": "guard", "ok": bool(discriminated),
                  "evidence": {"benign": benign.action, "danger": danger.action}})

    got: List[int] = []

    def _sink(_env: Any) -> Dict[str, Any]:
        got.append(1)
        return {"ok": True}

    addr = "fusion:probe"
    kernel.bus.register_address(addr, _sink)
    try:
        sent = kernel.bus.send(Envelope.create("main", addr, "task", {"task": BENIGN}))
    finally:
        kernel.bus.unregister_address(addr)
    steps.append({"step": "bus", "ok": len(got) == 1,
                  "evidence": {"delivered": len(got), "results": len(sent)}})

    beat = kernel.tick()
    steps.append({"step": "scheduler", "ok": isinstance(beat, dict) and bool(beat),
                  "evidence": sorted(beat.keys())[:5]})

    hits = kernel.skills.match("冷热插拔 清单 契约", k=3) if kernel.skills.names() else []
    steps.append({"step": "skill_match", "ok": bool(hits) if kernel.skills.names() else True,
                  "evidence": [h[0] for h in hits]})

    if kernel.agents:
        cand = [aid for aid, ag in kernel.agents.items()
                if "fusion_manifest" in (getattr(ag, "skill_names", None) or [])]
        first = cand[0] if cand else sorted(kernel.agents.keys())[0]
        out = kernel.submit("冷热插拔 清单", to=first)
        steps.append({"step": "submit", "ok": bool(out.get("all_ok")),
                      "evidence": {"agent": first,
                                   "status": out["results"][0].get("status") if out["results"] else None}})
    else:
        steps.append({"step": "submit", "ok": True,
                      "evidence": {"agent": None, "note": "无 agent，跳过端到端提交"}})

    ok = all(s["ok"] for s in steps)
    receipt = {"protocol": "internal", "mode": "simulated", "ok": ok,
               "steps": steps, "network_calls": 0}
    receipt["seal"] = digest_of({s["step"]: s["ok"] for s in steps})
    return receipt


def external_fuse(kernel: Any) -> Dict[str, Any]:
    """外部融合：只算路由，不发请求。"""
    adapter = _ensure_adapter(kernel)
    routes = []
    for strategy in ("cheapest", "largest_context"):
        try:
            choice = adapter.route("康复训练小结", strategy=strategy)
        except (KeyError, ValueError, AttributeError) as exc:
            routes.append({"strategy": strategy, "ok": False, "detail": str(exc)})
            continue
        routes.append({"strategy": strategy, "ok": True, "choice": str(choice)})
    ok = all(r["ok"] for r in routes)
    receipt = {"protocol": "external", "mode": "simulated", "ok": ok,
               "routes": routes, "network_calls": 0,
               "honesty": "只做后端选择，未发起任何真实模型调用；离线可复现"}
    receipt["seal"] = digest_of({r["strategy"]: r.get("choice") for r in routes})
    return receipt


def fuse(kernel: Any) -> Dict[str, Any]:
    """内外协议合并回执：任一不通过即整体不通过。"""
    internal = internal_fuse(kernel)
    external = external_fuse(kernel)
    receipt = {"protocol": "fusion", "mode": "simulated",
               "ok": bool(internal["ok"] and external["ok"]),
               "internal": internal, "external": external,
               "evidence_class": "simulated"}
    receipt["seal"] = digest_of({"i": internal["seal"], "e": external["seal"]})
    return receipt
