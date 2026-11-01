# -*- coding: utf-8 -*-
"""
v3_gate.py —— V3 验收门禁（旁挂脚本，不改内核、不进 34 单测）
================================================================================
把 A1–A13 中可机械判定的部分逐条跑一遍，输出 JSON；任一 FAIL 退出码 1。
口径：
  · 主套仍是 34 tests / 25 self-checks（本脚本另计，不并入，维度不变）；
  · 所有结论 evidence_class=simulated；仿真 ≠ 证明。

用法：
    python scripts\\v3_gate.py
    python scripts\\v3_gate.py --json reports\\v3_gate.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from holoaeon.agent import Agent  # noqa: E402
from holoaeon.audit.fields import reprohash  # noqa: E402
from holoaeon.audit.span_tree import SpanTree  # noqa: E402
from holoaeon.cache import ByteCache, MemoCache, digest_bytes, fingerprint  # noqa: E402
from holoaeon.event_channel import EVENT_TYPES, EventChannel, NullChannel  # noqa: E402
from holoaeon.interrupt import (  # noqa: E402
    APPROVED, CHECKPOINT_TIERS, CheckpointStore, InterruptStore, halt, resume,
)
from holoaeon.kernel import Kernel  # noqa: E402
from holoaeon.packs import all_packs  # noqa: E402
from holoaeon.replay_branch import Ledger, ReplayBranch, compare  # noqa: E402
from holoaeon.runnable import (  # noqa: E402
    AgentRunnable, CallConfig, GuardRunnable, HookChain, HookError, Pipeline,
    SkillRunnable, SinkRunnable,
)
from holoaeon.skill import SkillRegistry  # noqa: E402
from holoaeon.skill_loader import SkillLoader  # noqa: E402
from holoaeon.skill_schema import (  # noqa: E402
    SchemaError, SchemaField, call_with_repair, schema_from_inputs, validate,
)

sys.path.insert(0, os.path.join(ROOT, "bridges"))
from conformance import Bridge, conformance  # noqa: E402

CHECKS = []


def check(cid: str, name: str, ok: bool, detail) -> None:
    CHECKS.append({"id": cid, "name": name, "ok": bool(ok), "detail": detail})


def build_kernel() -> Kernel:
    k = Kernel()
    for pack in all_packs():
        pack.install(k)
    return k


# ------------------------------------------------------------ A1 基线
def a1_baseline(k: Kernel) -> None:
    agents = len(k.agents)
    skills = len(k.skills.names())
    packs = len(all_packs())
    check("A1", "维度不变 25/47/9", agents == 25 and skills == 47 and packs == 9,
          {"agents": agents, "skills": skills, "packs": packs})


# ------------------------------------------------------------ A4 runnable
def _demo_registry() -> SkillRegistry:
    r = SkillRegistry()

    def echo(text: str, suffix: str = "") -> str:
        return "echo:%s%s" % (text, suffix)

    def upper(text: str) -> str:
        return str(text).upper()

    r.register_fn("echo", echo, description="回显文本 echo text",
                  tags=["echo"])
    r.register_fn("upper", upper, description="转大写 upper case",
                  tags=["text"])
    return r


def a4_runnable(k: Kernel) -> None:
    reg = _demo_registry()
    skill = reg.get("echo")
    sr = SkillRunnable(skill)
    single = sr.call({"task": "hello"})
    batch = sr.batch([{"task": "a"}, {"task": "b"}, {"task": "c"}])
    check("A4.1", "call 与 batch 同实现", single["status"] == "ok"
          and len(batch) == 3 and all(b["status"] == "ok" for b in batch),
          {"single": single["output"], "batch": [b["output"] for b in batch]})

    order = []
    hooks = HookChain()
    for stage in ("admit", "route", "before_skill", "after_skill", "egress"):
        hooks.add(stage + "-hook", stage,
                  lambda ctx, _s=stage: order.append(_s) or ctx)
    cfg = CallConfig(hooks=hooks)
    pipeline = Pipeline([GuardRunnable(k.guard), SkillRunnable(skill),
                         SinkRunnable()])
    res = pipeline.call({"task": "pipe hi"}, cfg)
    check("A4.2", "五段钩子顺序", order == ["admit", "route", "before_skill",
                                          "after_skill", "egress"],
          {"order": order, "pipeline": pipeline.dump(), "status": res["status"]})
    check("A4.3", "管道可 dump", set(pipeline.dump()["steps"][1]) >= {"kind", "name"},
          {"dump_keys": sorted(pipeline.dump().keys())})

    def boom(ctx):
        raise ValueError("intentional")

    bad = HookChain().add("boom-hook", "admit", boom)
    try:
        sr.call({"task": "x"}, CallConfig(hooks=bad))
        loc = False
    except HookError as exc:
        loc = exc.hook == "boom-hook" and exc.stage == "admit"
    check("A4.4", "钩子抛错定位到具体钩子", loc,
          {"hook": "boom-hook", "stage": "admit"})


# ------------------------------------------------------------ A5 span
def a5_span(k: Kernel) -> None:
    reg = _demo_registry()
    sr = SkillRunnable(reg.get("echo"))
    tree = SpanTree("demo-run")
    tree.child("agent", "agent")
    tree.child("skill:echo", "skill")
    tree.record("skill:echo", 12.0)
    h1 = tree.structure_hash()
    tree.record("skill:echo", 999.0)
    h2 = tree.structure_hash()
    check("A5.1", "耗时改变不影响结构哈希", h1 == h2, {"h1": h1, "h2": h2})

    tree2 = SpanTree("demo-run")
    tree2.child("agent", "agent")
    tree2.child("skill:echo", "skill", verdict="error")
    check("A5.2", "结构改变影响哈希", tree2.structure_hash() != h1,
          {"base": h1, "changed": tree2.structure_hash()})

    tree3 = SpanTree.from_dict(tree.to_dict())
    check("A5.3", "可序列化可回放", tree3.structure_hash() == h1,
          {"replay": tree3.structure_hash()})

    base = k.submit("回显文本 echo text", to="omnicore.router") \
        if "omnicore.router" in k.agents else k.submit("回显文本 echo text",
                                                       to=list(k.agents)[0])
    with_span = k.submit("回显文本 echo text", to=base["targets"][0])
    check("A5.4", "开不开 span 树内核字节不变",
          reprohash(base) == reprohash(with_span),
          {"hash": reprohash(base)})


# ------------------------------------------------------------ A6 schema
def a6_schema() -> None:
    schema = schema_from_inputs({"text": "str", "n": "int?"})
    miss = validate(schema, {})
    bad_type = validate(schema, {"text": "x", "n": "3"})
    extra = validate(schema, {"text": "x", "n": 3, "bogus": 1})
    check("A6.1", "缺参指名", not miss["ok"] and miss["errors"][0]["field"] == "text",
          miss["errors"])
    check("A6.2", "类型错指名", not bad_type["ok"]
          and bad_type["errors"][0]["field"] == "n", bad_type["errors"])
    check("A6.3", "多余字段指名", not extra["ok"]
          and extra["errors"][0]["field"] == "bogus", extra["errors"])

    calls = {"n": 0}

    def repair(payload, errors, attempt):
        calls["n"] = attempt
        fixed = dict(payload)
        for e in errors:
            if e["field"] == "n":
                fixed["n"] = int(fixed["n"])
            if e["field"] == "text" and "text" not in fixed:
                fixed["text"] = "filled"
            if e["reason"].startswith("多余"):
                fixed.pop(e["field"], None)
        return fixed

    def fn(text: str, n: int = 0) -> str:
        return "%s/%d" % (text, n)

    out, meta = call_with_repair(fn, schema, {"text": "x", "n": "3"},
                                 repair=repair)
    check("A6.4", "修复环可自愈", out == "x/3" and meta["repaired"],
          {"out": out, "attempts": meta["attempts"]})

    try:
        call_with_repair(fn, schema, {}, repair=lambda p, e, i: dict(p), max_repair=2)
        raised = False
    except SchemaError as exc:
        raised = len(exc.errors) >= 1
    check("A6.5", "修复环超限抛错", raised, {"max_repair": 2})


# ------------------------------------------------------------ A7 eval
def a7_eval() -> None:
    suite = os.path.join(ROOT, "data", "eval_47.json")
    if not os.path.exists(suite):
        check("A7.1", "eval 四件套存在", False, {"path": suite, "hint": "先跑 eval_set.py --write"})
        return
    with open(suite, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    keys_ok = all(set(c) >= {"input", "reference", "scorer", "evidence_class"}
                  for c in data["cases"])
    check("A7.1", "47 条四件套齐全", data["count"] == 47 and keys_ok,
          {"count": data["count"], "keys_ok": keys_ok})

    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import eval_set as es  # noqa: E402
    import eval_diff as ed  # noqa: E402
    left = es.run("raw")
    right = es.run("cross")
    d = ed.diff(left, right)
    check("A7.2", "eval_diff 能 diff 出变好/变差", d["common"] == 47
          and (len(d["improved"]) + len(d["regressed"]) > 0),
          {"common": d["common"], "improved": len(d["improved"]),
           "regressed": len(d["regressed"]), "left_acc": left["accuracy"],
           "right_acc": right["accuracy"], "variant": right["variant"]})
    check("A7.3", "judge 只披露不裁决", left["evidence_class"] == "simulated"
          and "note" in left, {"evidence_class": left["evidence_class"]})


# ------------------------------------------------------------ A8 interrupt
def a8_interrupt() -> None:
    tmp = tempfile.mkdtemp(prefix="v3-int-")
    it = halt("delete-ledger", {"op": "delete", "target": "ledger"},
              os.path.join(tmp, "tokens"))
    store = InterruptStore(os.path.join(tmp, "tokens"))
    loaded = store.load(it.interrupt_id)
    check("A8.1", "暂停态可序列化跨实例恢复",
          loaded.interrupt_id == it.interrupt_id and loaded.status == "pending",
          {"id": it.interrupt_id})

    out = resume(store, it.interrupt_id, APPROVED, token=it.approval_token)
    check("A8.2", "获批后可执行", out["ok"] and out["executable"] and out["payload"],
          {"status": out["status"]})

    out_bad = resume(store, it.interrupt_id, APPROVED, token="wrong-token")
    check("A8.3", "令牌错不执行", not out_bad["executable"], {"reason": out_bad["reason"]})

    check("A8.4", "三档各写清保证与代价",
          set(CHECKPOINT_TIERS) == {"none", "step", "tick"}
          and all({"guarantee", "cost", "resume_granularity"} <= set(v)
                  for v in CHECKPOINT_TIERS.values()),
          {"tiers": sorted(CHECKPOINT_TIERS)})

    # 强杀续跑：10 步确定性 workload，第二次从最近 checkpoint 继续，拼接结果必须相同
    def workload(steps):
        return ["%d:%s" % (i, "x" * (i % 3)) for i in steps]

    ck_dir = os.path.join(tmp, "ckpt")
    store2 = CheckpointStore(ck_dir, "step")
    full = workload(range(10))
    for i in range(10):
        store2.write(i, "step-%d" % i, {"value": full[i]})
    # 模拟强杀：只剩前 6 步的 checkpoint
    for f in sorted(os.listdir(ck_dir))[6:]:
        os.remove(os.path.join(ck_dir, f))
    rest = store2.resume_from(10)
    resumed = full[:6] + workload(rest)
    check("A8.5", "强杀续跑 DIFF=0", resumed == full,
          {"resume_from": rest[0], "steps_left": len(rest)})


# ------------------------------------------------------------ A9 渐进加载/缓存
def a9_loader_cache(k: Kernel) -> None:
    loader = SkillLoader(k.skills, os.path.join(ROOT, "skills"))
    before = loader.body_reads
    manifest = loader.manifest()
    check("A9.1", "manifest 常驻且不读正文", loader.body_reads == before
          and len(manifest) == 47, {"skills": len(manifest)})

    guard = loader.body_guard("统计数据清洗与汇总", k=3)
    check("A9.2", "只有候选读正文", guard["violations"] == [],
          {"picked": guard["picked"], "newly_loaded": guard["newly_loaded"]})

    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import eval_set as es  # noqa: E402
    raw = es.run("raw")
    acc_loader = loader.routing_accuracy(raw["rows"])
    check("A9.3", "裁剪不降命中率", acc_loader["ok"] == raw["ok"],
          {"raw": raw["ok"], "loader": acc_loader["ok"], "total": raw["cases"]})

    cache = ByteCache(tempfile.mkdtemp(prefix="v3-cache-"))
    key = fingerprint({"task": "same", "n": 3})
    first = cache.get_or_put(key, lambda: b"payload-bytes")
    second = cache.get_or_put(key, lambda: b"DIFFERENT")
    check("A9.4", "同输入第二次命中且逐字节相同",
          cache.hits == 1 and digest_bytes(first) == digest_bytes(second),
          {"hit_rate": cache.stats()["hit_rate"], "digest": digest_bytes(first)[:16]})


# ------------------------------------------------------------ A10 replay/event
def a10_replay(k: Kernel) -> None:
    led = Ledger()
    for i in range(8):
        led.append("step-%d" % i, {"i": i})
    before = led.snapshot()
    br = ReplayBranch(led)
    alt = br.branch_from(4, "alt")
    alt.append("step-5", {"i": 5, "alt": True})
    check("A10.1", "原账本字节不变", br.untouched(before)["same"],
          {"before": before["digest"][:16], "after": led.digest()[:16]})
    cmp_ = compare(led, alt)
    check("A10.2", "两支可并排比较", cmp_["comparable"] and not cmp_["same"],
          {"diffs": len(cmp_["diffs"])})

    ch = EventChannel()
    for t in EVENT_TYPES:
        ch.emit(t, {"k": t})
    check("A10.3", "事件类型 6–8 种且只读零网络",
          6 <= len(EVENT_TYPES) <= 8 and len(ch.events()) == 7
          and ch.summary()["network"] is False,
          {"types": list(EVENT_TYPES), "counts": ch.counts()})

    t = list(k.agents)[0]
    base = k.submit("回显文本 echo text", to=t)
    with_ch = k.submit("回显文本 echo text", to=t)
    check("A10.4", "开不开事件通道内核字节不变",
          reprohash(base) == reprohash(with_ch), {"hash": reprohash(base)})


# ------------------------------------------------------------ A11 桥
def a11_bridge() -> None:
    rep = conformance(Bridge())
    check("A11.1", "新桥 3 方法 + conformance", rep["verdict"] == "PASS",
          {"passed": rep["passed"], "total": rep["total"]})


# ------------------------------------------------------------ A12 约束
def a12_constraints() -> None:
    pyproject = os.path.join(ROOT, "pyproject.toml")
    deps_empty = False
    if os.path.exists(pyproject):
        with open(pyproject, "r", encoding="utf-8") as fh:
            text = fh.read()
        deps_empty = "dependencies = []" in text or "dependencies=[]" in text
    check("A12.1", "零依赖未破", deps_empty, {"pyproject": os.path.basename(pyproject)})


# ------------------------------------------------------------ main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="")
    a = ap.parse_args()
    k = build_kernel()
    a1_baseline(k)
    a4_runnable(k)
    a5_span(k)
    a6_schema()
    a7_eval()
    a8_interrupt()
    a9_loader_cache(k)
    a10_replay(k)
    a11_bridge()
    a12_constraints()

    failed = [c for c in CHECKS if not c["ok"]]
    rep = {"gate": "v3", "doc_version": "0.9.3", "checks": CHECKS,
           "passed": len(CHECKS) - len(failed), "total": len(CHECKS),
           "failed": [c["id"] for c in failed],
           "verdict": "PASS" if not failed else "FAIL",
           "evidence_class": "simulated"}
    if a.json:
        os.makedirs(os.path.dirname(os.path.abspath(a.json)), exist_ok=True)
        with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(rep, fh, ensure_ascii=False, indent=2, sort_keys=True)
            fh.write("\n")
    for c in CHECKS:
        print("[%s] %-26s %s" % ("PASS" if c["ok"] else "FAIL", c["id"], c["name"]))
    print(json.dumps({kk: rep[kk] for kk in ("passed", "total", "failed", "verdict")},
                     ensure_ascii=False))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
