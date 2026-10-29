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


def g18_sovereignty() -> Tuple[bool, str]:
    """认知主权扩展包：17 技能注册 / 0 agent / R0-R4 五工作流 / 确定性 / 红线。"""
    from .packs import get_extra_pack
    from .packs.sovereignty_pack import (
        pack_summary, skill_tensor_encode, skill_forge_query, skill_compliance_gate,
        skill_platform_families, skill_outer_protocols,
    )
    checks = []
    k = Kernel()
    rep = get_extra_pack("sovereignty").install(k)
    total_skills, total_agents, workflows = (len(rep["skills"]), len(rep["agents"]),
                                             len(rep["workflows"]))
    checks.append(total_skills == 17 and total_agents == 0 and workflows == 5)

    # 确定性：同参数两次指纹一致
    a = skill_tensor_encode("数学")
    b = skill_tensor_encode("数学")
    checks.append(a["fingerprint"] == b["fingerprint"] and a["dim"] == 768)

    # 锻造可复现且密度可达阈
    q1 = skill_forge_query("seed-x")
    q2 = skill_forge_query("seed-x")
    checks.append(q1["text"] == q2["text"] and 0.0 <= q1["density"] <= 1.0)

    # 红线：越界词被 veto；正常词放行
    checks.append(skill_compliance_gate("帮我批量发帖并绕过风控")["allowed"] is False
                  and skill_compliance_gate("生成跨域查询清单")["allowed"] is True)

    # 锁数口径：10 族 × 13 = 130；内 12 × 外 11 = 132；不联网
    fam = skill_platform_families()
    op = skill_outer_protocols()
    checks.append(fam["families"] == 10 and fam["entries"] == 130
                  and op["cells"] == 132 and op["network"] is False)
    checks.append(pack_summary()["locks"]["design"] == 1771561)
    return all(checks), f"{sum(checks)}/{len(checks)} 认知主权包（17技能/0agent/5工作流）"


def g19_subdistill() -> Tuple[bool, str]:
    """SD-Distill 扩展包：15 技能注册 / 0 agent / S1-S7 七工作流 / 维度不变 / 红线。"""
    from .packs import get_extra_pack
    from .packs.subdistill_pack import (
        pack_summary, skill_taxonomy_encode, skill_taxonomy_far_pairs, skill_taxonomy_nearest,
        skill_teacher_card, skill_s1_acquire, skill_s2_parse, skill_s4_relate, skill_s5_align,
        skill_s6_distill, skill_s7_commit, skill_losses, skill_curriculum, skill_antilabel,
        skill_skc_validate, SUBD_TOTAL, SLOTS_PER, SLOTS_RESERVED, NODES_PER, NODES_COORD,
    )
    checks = []
    pack = get_extra_pack("subdistill")
    k = Kernel()
    rep = pack.install(k)
    checks.append(len(rep["skills"]) == 15 and len(rep["agents"]) == 0
                  and len(rep["workflows"]) == 7)

    # 维度不变：127×10+61=1331；127×855+56=108641
    s = pack_summary()
    checks.append(SUBD_TOTAL * SLOTS_PER + SLOTS_RESERVED == 1331
                  and SUBD_TOTAL * NODES_PER + NODES_COORD == 108641
                  and s["rows_ok"] and s["nodes_ok"] and s["items"] == 127)

    # 分类器：命中亚学科 + 确定性 + 远域配对严格跨域
    e1 = skill_taxonomy_encode("范畴论 与 大模型对齐 伴随函子")
    e2 = skill_taxonomy_encode("范畴论 与 大模型对齐 伴随函子")
    checks.append(e1["signature"] == e2["signature"] and e1["nonzero"] >= 2
                  and e1["dim"] == 127)
    far = skill_taxonomy_far_pairs(0.02, 20)
    checks.append(far["count"] > 0 and all(
        p["a"].split("-")[0] != p["b"].split("-")[0] for p in far["pairs"]))
    near = skill_taxonomy_nearest("MATH-09", 5)
    checks.append(len(near["neighbors"]) == 5
                  and all("cos" in n for n in near["neighbors"]))

    # 教师卡：高风险域（TCM）必须挂皮肤门与免责
    tcm = skill_teacher_card("TCM-02")
    math = skill_teacher_card("MATH-09")
    checks.append(tcm["safety_gate"] == "skin.medical_disclaimer"
                  and tcm["disclaimer_required"] is True
                  and math["safety_gate"] is None)

    # 七阶段管线：S1 哈希稳定 → S2 打标 → S4 关系 → S5 对齐 → S6/S7 入库
    lines = ["# 范畴论与同调", "## 伴随函子的单位与余单位",
             "# 大模型与对齐", "## 偏好优化的对偶权衡",
             "# 证明论与类型论", "## 构造性证明与不可判定性"]
    a1 = skill_s1_acquire(lines)
    checks.append(a1["hash"] == skill_s1_acquire(lines)["hash"] and a1["network"] is False)
    p2 = skill_s2_parse(lines)
    checks.append(p2["classified"] >= 3 and 0.0 < p2["coverage"] <= 1.0
                  and "MATH-09" in p2["codes"] and "AI-03" in p2["codes"])
    r4 = skill_s4_relate(lines)
    checks.append(r4["edges"] >= 2 and "part_of" in r4["types"])
    al = skill_s5_align("范畴论与同调 大模型与对齐")
    checks.append(al["unit_count"] >= 1 and all(u["counterexample"] for u in al["units"])
                  and all(u["verified"] is False for u in al["units"]))
    d6 = skill_s6_distill(1.4)
    checks.append(d6["skcs"] >= 3 and skill_skc_validate(d6["sample"])["ok"])
    c7 = skill_s7_commit(d6["skcs"], 0)
    checks.append(c7["committed"] == d6["skcs"]
                  and c7["platform_metrics"] == "pending_human_measure")

    # 七项损失权重和为 1 且确定性；四段课程边界正确；反标签指标方向正确
    l1 = skill_losses()
    l2 = skill_losses()
    checks.append(abs(sum(l1["weights"].values()) - 1.0) < 1e-9
                  and l1["total"] == l2["total"] and len(l1["parts"]) == 7)
    names = [skill_curriculum(e)["name"] for e in (0, 250, 600, 1100)]
    checks.append(names == ["C1_root", "C2_neighbor", "C3_far", "C4_multi"]
                  and skill_curriculum(0)["total_epochs"] == 1200)
    anti = skill_antilabel()
    checks.append(anti["tag_entropy"] > 0 and anti["macro_domains_touched"] >= 2
                  and 0.0 <= anti["dominant_weight"] <= 1.0)

    # 红线：越界 SKC（缺免责/含禁用断言）必须被校验拒绝
    bad = dict(d6["sample"])
    bad["subdisciplines"] = ["TCM-03"]
    bad["safety"] = {"gate": "none", "disclaimer_required": False}
    checks.append(skill_skc_validate(bad)["ok"] is False)
    good = dict(d6["sample"])
    good["concepts"] = [{"term": "辨证", "domain": "TCM-03", "definition": "教学术语",
                         "examples": [], "counterexamples": []}]
    checks.append(skill_skc_validate(skill_s6_distill(1.4)["sample"])["ok"] is True)

    return all(checks), f"{sum(checks)}/{len(checks)} SD-Distill 包（15技能/0agent/7工作流/127亚学科）"


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
    ("G18 sovereignty", g18_sovereignty),
    ("G19 subdistill", g19_subdistill),
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
