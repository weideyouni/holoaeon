# -*- coding: utf-8 -*-
"""
HoloAeon SelfTest —— 自检套件（G1-G17）
================================================================================
逐组验证核心模块与机制，全部确定性、离线、零依赖。
run_all() 返回 {groups, passed, failed, ok, details}。
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Tuple

from .agent import Agent
from .bus import Bus
from .envelope import Envelope
from .graph import AdaptiveGraph
from .guard import Guard
from .hypervector import HypervectorSpace
from .kernel import Kernel
from .memory import Memory
from .model_adapter import ModelAdapter, ModelBackend
from .packs import all_packs
from .scheduler import Scheduler
from .skill import SkillRegistry
from .spec import (DEFAULT_CONFIG, config_verify, lock_check)
from .cluster import Cluster


# ------------------------------------------------------------ 自检组
def g1_spec() -> Tuple[bool, str]:
    ok_config = config_verify(DEFAULT_CONFIG)
    locks = lock_check(DEFAULT_CONFIG)
    return bool(ok_config), f"config={ok_config}, design_grid={locks['design_grid']}"


def g2_envelope() -> Tuple[bool, str]:
    e = Envelope.create("a", "b", "t", {"task": "x"})
    d = e.to_dict()
    e2 = Envelope.from_dict(d)
    r = Envelope.reply(e, "b", {"ok": True})
    return e2.message_id == e.message_id and r.conversation == e.conversation, \
        "roundtrip + reply"


def g3_bus_pubsub() -> Tuple[bool, str]:
    b = Bus()
    got = []
    b.subscribe("news", lambda env: got.append(env))
    b.publish("news", {"v": 1}, "src")
    return len(got) == 1, f"delivered={len(got)}"


def g4_bus_addr() -> Tuple[bool, str]:
    b = Bus()
    b.register_address("x", lambda env: "acked")
    rep = b.send(Envelope.create("m", "x", "d", {}))
    ok = bool(rep) and rep[0]["ok"] and rep[0]["out"] == "acked"
    return ok, f"reply={rep[0]['out'] if rep else None}"


def g5_skill() -> Tuple[bool, str]:
    r = SkillRegistry()
    r.register_fn("summarize", lambda task: "s", description="summarize text",
                  tags=["summary"])
    m = r.match("please summarize this text")
    return bool(m) and m[0][0] == "summarize", f"match={m}"


def g6_memory() -> Tuple[bool, str]:
    m = Memory()
    m.put("k", {"a": 1}, kind="working")
    m.consolidate()
    got = m.get("k")
    return got is not None and got["a"] == 1, f"stats={m.stats()}"


def g7_agent() -> Tuple[bool, str]:
    r = SkillRegistry()
    r.register_fn("echo", lambda task: "echo:" + task, description="echo text")
    a = Agent("ag", "role", r)
    res = a.run_task("echo hello")
    return res["status"] == "ok" and res["output"] == "echo:echo hello", str(res["status"])


def g8_scheduler() -> Tuple[bool, str]:
    s = Scheduler()
    s.tick(); s.tick()
    h = s.health()
    return h["tick_count"] == 2 and h["bodies"] == 70, f"ticks={h['tick_count']}"


def g9_guard() -> Tuple[bool, str]:
    g = Guard()
    bad = g.check_text("import os; os.system('rm -rf /')")
    good = g.check_text("a normal safe sentence")
    return bad.action == "block" and good.action != "block", \
        f"bad={bad.action}, good={good.action}"


def g10_kernel() -> Tuple[bool, str]:
    k = Kernel()
    k.skills.register_fn("plan", lambda task: "plan:" + task,
                         description="plan outline")
    k.register_agent(Agent("pl", "planner"))
    res = k.submit("please plan the work")
    return res["all_ok"], f"all_ok={res['all_ok']}"


def g11_graph() -> Tuple[bool, str]:
    g = AdaptiveGraph(flow_edges=[(0, 1), (1, 2)])
    path, dist = g.shortest_path(0, 2)
    bn = g.bottleneck()
    g.hebbian_step([0, 1])
    return bool(path) and bn, f"path={path}, dist={dist}"


def g12_cluster() -> Tuple[bool, str]:
    r = SkillRegistry()
    r.register_fn("work", lambda task: "w:" + task, description="work task")
    agents = [Agent(f"a{i}", "role", r) for i in range(3)]
    c = Cluster(agents)
    rep = c.run(1, {f"a{i}": f"work task {i}" for i in range(3)})
    return rep["ok"] == 3 and rep["consistent"] and not rep["faults"], \
        f"ok={rep['ok']}, faults={rep['faults']}"


def g13_hypervector() -> Tuple[bool, str]:
    hv = HypervectorSpace()
    a, b = hv.make("a"), hv.make("b")
    ab = hv.bind(a, b)
    rec = hv.unbind(ab, b)
    return abs(hv.cosine(a, a) - 1.0) < 1e-6 and hv.cosine(ab, a) < 0.2 \
        and hv.cosine(rec, a) > 0.5, \
        f"bind={hv.cosine(ab,a)}, recover={hv.cosine(rec,a)}"


def g14_model_adapter() -> Tuple[bool, str]:
    ma = ModelAdapter()
    ma.register_backend(ModelBackend("m1", "local", input_cost=0.0))
    ma.register_backend(ModelBackend("m2", "cloud", context_window=100000,
                                     input_cost=0.02))
    cheap = ma.route("x", strategy="cheapest")
    large = ma.route("x", strategy="largest_context")
    return cheap == "m1" and large == "m2", f"cheap={cheap}, large={large}"


def g15_packs() -> Tuple[bool, str]:
    k = Kernel()
    n_skills, n_agents = 0, 0
    for pack in all_packs():
        rep = pack.install(k)
        n_skills += len(rep["skills"]); n_agents += len(rep["agents"])
    return n_agents == 25 and n_skills == 47, \
        f"agents={n_agents}, skills={n_skills}"


def g16_optimization() -> Tuple[bool, str]:
    """优化求解层：各算法收敛到已知最优解。"""
    from .packs.optimization import (
        skill_golden, skill_gradient, skill_newton, skill_conjugate,
        skill_simplex, skill_penalty, skill_genetic,
    )
    checks = []
    g = skill_golden(); checks.append(abs(g["optimum_x"] - 3.0) < 1e-4)
    gd = skill_gradient()
    checks.append(abs(gd["optimum"][0] - 2.0) < 1e-3 and
                  abs(gd["optimum"][1] + 1.0) < 1e-3)
    n = skill_newton(); checks.append(abs(n["optimum_x"] - 3.0) < 1e-4)
    cg = skill_conjugate()
    checks.append(abs(cg["solution"][0] - 1 / 11) < 1e-4 and
                  abs(cg["solution"][1] - 7 / 11) < 1e-4)
    sm = skill_simplex()
    checks.append(sm["objective"] == 180.0 and sm["x"] == [20.0, 60.0])
    pn = skill_penalty()
    checks.append(abs(pn["optimum"][0] - 3.0) < 1e-2 and
                  abs(pn["optimum"][1] - 3.0) < 1e-2)
    ga = skill_genetic()
    checks.append(ga["best_decoded"] == 31 and ga["best_value"] == 961)
    return all(checks), f"{sum(checks)}/7 优化算法收敛"


def g17_gaoyi() -> Tuple[bool, str]:
    """高译包：NL→HASM 编译、虚拟机执行、UNKNOWN 兜底、汇编往返。"""
    from .packs.gaoyi_pack import compile_nl, HasmProgram, GaoyiVm
    checks = []
    # 1) 编译：大纲意图正确派单
    p, meta = compile_nl("帮我做个大纲：人工智能")
    checks.append(meta["intent"] == "outline_gen"
                  and meta["agent"] == "writing_planner")
    # 2) 虚拟机执行全链路（虚拟机内部会安装全部包）
    rep = GaoyiVm(Kernel()).run(p)
    checks.append(bool(rep["ok"]) and rep["matched"] == "outline_gen")
    # 3) 无关键词如实报 UNKNOWN，不猜测
    _, m2 = compile_nl("今天天气怎么样啊哈哈")
    checks.append(m2["intent"] == "UNKNOWN")
    # 4) 汇编往返：parse 反汇编文本，指令数一致
    parsed = HasmProgram.parse(meta["assembly"])
    checks.append(len(parsed.ops) == len(p.ops))
    return all(checks), f"{sum(checks)}/4 高译编译/执行/UNKNOWN/往返"


GROUPS: List[Tuple[str, Callable[[], Tuple[bool, str]]]] = [
    ("G1 spec", g1_spec),
    ("G2 envelope", g2_envelope),
    ("G3 bus pubsub", g3_bus_pubsub),
    ("G4 bus address", g4_bus_addr),
    ("G5 skill", g5_skill),
    ("G6 memory", g6_memory),
    ("G7 agent", g7_agent),
    ("G8 scheduler", g8_scheduler),
    ("G9 guard", g9_guard),
    ("G10 kernel", g10_kernel),
    ("G11 graph", g11_graph),
    ("G12 cluster", g12_cluster),
    ("G13 hypervector", g13_hypervector),
    ("G14 model_adapter", g14_model_adapter),
    ("G15 packs", g15_packs),
    ("G16 optimization", g16_optimization),
    ("G17 gaoyi", g17_gaoyi),
]


def run_all(verbose: bool = False) -> Dict[str, Any]:
    details = []
    passed = 0
    for name, fn in GROUPS:
        try:
            ok, msg = fn()
        except Exception as exc:  # noqa: BLE001
            ok, msg = False, f"exception: {exc}"
        details.append({"group": name, "passed": bool(ok), "detail": msg})
        if ok:
            passed += 1
        if verbose:
            print(f"[{'PASS' if ok else 'FAIL'}] {name} — {msg}")
    return {
        "groups": len(GROUPS), "passed": passed,
        "failed": len(GROUPS) - passed,
        "ok": passed == len(GROUPS), "details": details,
    }
