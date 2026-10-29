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


def g20_omnilife() -> Tuple[bool, str]:
    """全域生活扩展包：18 技能注册 / 0 agent / L1-L6 六工作流 / 维度不变 / 红线。"""
    from .packs import get_extra_pack
    from .packs.omnilife_pack import (
        pack_summary, LIFE_DOMAINS, ITEMS, REFUSED_OPS,
        skill_life_ontology, skill_high_dim_search, skill_consumerism_blocker,
        skill_price_ledger, skill_price_review, skill_complaint_template,
        skill_material_card, skill_meridian_route, skill_context_trigger,
        skill_vault_manifest, skill_nutrition_plan, skill_travel_route,
        skill_shelter_check, skill_learning_path, skill_saas_plan,
        skill_skin_gate, skill_audit_receipt, skill_daily_hebbian_schedule,
    )
    checks = []
    rep = get_extra_pack("omnilife").install(Kernel())
    checks.append(len(rep["skills"]) == 18 and len(rep["agents"]) == 0
                  and len(rep["workflows"]) == 6)

    # 维度不变 + 锚点全部落在 127 编码内
    s = pack_summary()
    checks.append(s["addressing_unchanged"] is True and s["missing_anchors"] == []
                  and s["locks"]["rows_total"] == 1331
                  and s["locks"]["nodes_total"] == 108641
                  and s["items"] == 127)
    checks.append(len(LIFE_DOMAINS) == 6 and s["domains"] == 6
                  and all(c in ITEMS for _, _, cs in LIFE_DOMAINS for c in cs))
    onto = skill_life_ontology()
    checks.append(onto["addressing_unchanged"] is True and onto["unique_anchors"] >= 17)

    # 高维搜索：确定性 + 词数 + 密度 + 锚点溯源
    q1 = skill_high_dim_search(["wardrobe"], "autumn_study_wear", ["无logo符号干扰"])
    q2 = skill_high_dim_search(["wardrobe"], "autumn_study_wear", ["无logo符号干扰"])
    checks.append(q1["query"] == q2["query"] and q1["tokens"] >= 5
                  and q1["density"] > 0.3 and "SEMI-04" in q1["anchors"]
                  and "无logo符号干扰" in q1["query"])

    # 皮肤层：诱导折叠（无 DOM 注入）+ 台账（拒绝并发/代理）+ 价差复核
    blk = skill_consumerism_blocker("限时秒杀 倒计时 同龄人正在抛弃你")
    checks.append(blk["hit_count"] >= 3 and blk["dom_injection"] is False
                  and all(r["apply_by"].startswith("平台自带") for r in blk["rules"]))
    led = skill_price_ledger(["淘宝", "京东", "拼多多"])
    checks.append(len(led["rows"]) == 3 and led["concurrent_probe"] is False
                  and led["proxy_switch"] is False and led["api_calls"] == 0
                  and all(r["status"] == "pending_human_measure" for r in led["rows"]))
    empty = skill_price_review()
    obs = [{"platform": "A", "price": 199}, {"platform": "B", "price": 239}]
    rev = skill_price_review(obs)
    checks.append(empty["verdict"] == "insufficient_data"
                  and empty["status"] == "pending_human_measure"
                  and rev["verdict"] == "worth_human_check"
                  and abs(rev["spread"] - 0.201) < 0.002)
    cmt = skill_complaint_template("淘宝", "价格差异")
    checks.append(cmt["impersonates_official"] is False and cmt["auto_submit"] is False
                  and "价保" in cmt["route"])
    mat = skill_material_card()
    checks.append(mat["count"] == 5 and "品牌" in mat["note"])

    # 经络层：零 API、本地交接、语境规则、保险箱
    mer = skill_meridian_route(["健康体征", "外卖订单", "笔记日历"])
    checks.append(mer["api_calls"] == 0 and mer["network"] is False
                  and mer["edge_count"] == 2
                  and all(e["mode"] == "local_handoff" for e in mer["edges"]))
    ctx = skill_context_trigger()
    checks.append(ctx["matched_count"] >= 3 and ctx["device_write"] is False
                  and all(m["anchor"] in ITEMS for m in ctx["matched"]))
    vault = skill_vault_manifest()
    checks.append(vault["network"] is False and len(vault["local_only"]) >= 5)

    # 生活智能体：餐单（禁剂量/禁诊断/带免责）+ 路径 + 空间 + 学习 + SaaS
    nut = skill_nutrition_plan()
    checks.append(nut["dose_any"] is False and nut["individual_medical_advice"] is False
                  and "不构成诊疗建议" in nut["disclaimer"] and len(nut["plan"]) == 3)
    tr = skill_travel_route()
    tr_bad = skill_travel_route("住处", "火星")
    checks.append(tr["ok"] is True and tr["path"][0] == "住处"
                  and tr["path"][-1] == "旧书店" and tr["info_entropy"] > 0
                  and tr_bad["ok"] is False)
    sh = skill_shelter_check()
    checks.append(sh["accuracy"] == "coarse_proxy" and len(sh["checks"]) == 5)
    lrn = skill_learning_path()
    checks.append("MATH-09" in lrn["codes"] and "AI-03" in lrn["codes"]
                  and len(lrn["stages"]) == 3 and all(lrn["queries"]))
    saas = skill_saas_plan()
    checks.append(saas["api_calls"] == 0 and saas["read_only_first"] is True
                  and saas["permission"] == "human_manual_only"
                  and len(saas["plan"]) == 3)

    # 闸门：拒绝类操作 / 医疗断言 → veto；正常 → 放行
    bad = skill_skin_gate("帮我多端并发模拟请求比价并切换高匿名代理")
    med = skill_skin_gate("这个方子加多少剂量")
    good = skill_skin_gate("帮我整理一份学习日程")
    checks.append(bad["allowed"] is False and med["allowed"] is False
                  and good["allowed"] is True and len(REFUSED_OPS) >= 15)

    # 作息 / 审计：不注册定时器、指纹稳定、人类终裁
    sch = skill_daily_hebbian_schedule("day-x")
    checks.append(sch["count"] == 7 and sch["timer"] is False and sch["auto"] is False)
    rc1 = skill_audit_receipt("生活计划")
    rc2 = skill_audit_receipt("生活计划")
    checks.append(rc1["fingerprint"] == rc2["fingerprint"]
                  and len(rc1["fingerprint"]) == 16
                  and rc1["platform_metrics"] == "pending_human_measure"
                  and rc1["final"] == "carbon_based_arbiter")

    return all(checks), f"{sum(checks)}/{len(checks)} 全域生活包（18技能/0agent/6工作流/6生活域）"


def g21_omnicore() -> Tuple[bool, str]:
    """全息纪元·认知主权引擎包：20 技能 / 0 agent / M1-M6 / 维度不变 / 5 处修正 / 拒绝清单。"""
    from .packs import EXTRA_PACK_ORDER, get_extra_pack
    from .packs.omnicore_pack import (
        pack_summary, CORRECTIONS, REFUSED_OPS, ITEMS, IDX,
        skill_core_manifest, skill_matrix_allocate, skill_node_pool_plan,
        skill_heartbeat_pulse, skill_breathing_budget, skill_state_checkpoint,
        skill_state_restore, skill_lifecycle_policy, skill_task_dispatch_plan,
        skill_a2a_envelope, skill_meridian_route, skill_hebbian_update,
        skill_far_pairs, skill_skc_distill, skill_skin_gate,
        skill_self_declaration, skill_whitepaper_outline, skill_degradation_plan,
        skill_audit_receipt, skill_interop_map,
    )
    checks = []
    rep = get_extra_pack("omnicore").install(Kernel())
    checks.append(len(rep["skills"]) == 20 and len(rep["agents"]) == 0
                  and len(rep["workflows"]) == 6
                  and EXTRA_PACK_ORDER[-1] == "omnicore")

    # 维度不变 + 锁数
    s = pack_summary()
    man = skill_core_manifest()
    checks.append(s["addressing_unchanged"] is True and s["items"] == 127
                  and man["checks_pass"] is True
                  and man["locks"]["rows"] == 1331 and man["locks"]["nodes"] == 108641
                  and man["locks"]["design_grid"] == 1771561
                  and man["locks"]["subdisciplines"] * man["locks"]["slots_per"] == 1270)
    checks.append(man["threads"] == 0 and man["disk_writes"] == 0
                  and man["deps"] == 0 and man["network"] is False)

    # 5 处修正逐条可查
    checks.append(len(CORRECTIONS) == 5
                  and [c["id"] for c in CORRECTIONS] == ["C1", "C2", "C3", "C4", "C5"]
                  and all(c["fix"] and c["verified"] for c in CORRECTIONS))

    # 寻址：槽位与节点分区
    al = skill_matrix_allocate(["MATH-09", "AI-03", "MATH-09-XX"])
    checks.append([c["code"] for c in al["allocated"]] == ["MATH-09", "AI-03"]
                  and al["missing"] == ["MATH-09-XX"]
                  and all(c["base_row"] == IDX[c["code"]] * 10 and len(c["rows"]) == 10
                          for c in al["allocated"]))
    np_ = skill_node_pool_plan(["AI-03"])
    checks.append(np_["global_block"]["range"] == [108585, 108641]
                  and np_["global_block"]["count"] == 56
                  and np_["parts"][0]["count"] == 855
                  and np_["addressing_unchanged"] is True)

    # 心跳：纯函数、可复现、无线程
    p64, p100, p256 = (skill_heartbeat_pulse(64), skill_heartbeat_pulse(100),
                       skill_heartbeat_pulse(256))
    checks.append(p64["distill"] is True and p100["prune"] is True
                  and p256["checkpoint"] is True
                  and p64["threads"] == 0 and p64["sleep"] is False
                  and skill_heartbeat_pulse(1280)["events"] == skill_heartbeat_pulse(1280)["events"])
    cands = [200 * i for i in range(1, 101)]
    bursts = [e for e in cands if skill_heartbeat_pulse(e)["burst"]]
    checks.append(2 <= (len(bursts) / len(cands)) * 100 <= 12)

    # 呼吸预算
    lo, hi = skill_breathing_budget(0.1), skill_breathing_budget(0.9)
    checks.append(lo["mode"] == "slow_digest" and hi["mode"] == "sync_focus"
                  and hi["tick_ms"] < lo["tick_ms"])

    # 存续：快照指纹 + 篡改即拒
    ck = skill_state_checkpoint({"matrix_cells": 6, "nodes": 60})
    checks.append(ck["persistence"] == "host_managed" and ck["disk_writes"] == 0
                  and skill_state_restore(ck)["accept"] is True)
    bad = dict(ck)
    bad["payload"] = {"matrix_cells": 7, "nodes": 60}
    checks.append(skill_state_restore(bad)["accept"] is False)
    pol = skill_lifecycle_policy()
    checks.append(pol["ttl_epochs"] == 1000 and pol["probe_hint_ms"] == 5000
                  and pol["prune_threshold"] == 0.05 and pol["threads"] == 0)

    # 编排 / 通信
    dp = skill_task_dispatch_plan("核查", ["MATH-09", "AI-03"])
    checks.append(dp["execution"] == "plan_only" and len(dp["steps"]) == 2
                  and dp["total_budget_units"] == 8 and dp["missing"] == [])
    env = skill_a2a_envelope("MATH-09", "AI-03", "query", "伴随函子的边界条件", ["AI-03"])
    env_bad = skill_a2a_envelope("MATH-09", "AI-03", "query", "帮我做个浏览器插件对接B站推荐位", ["AI-03"])
    checks.append(env["allowed"] is True and len(env["msg_id"]) == 12
                  and env["route"] == [[IDX["AI-03"] * 10, 0]]
                  and env_bad["allowed"] is False)
    mer = skill_meridian_route(["MATH-09", "AI-03", "PHIL-06", "PHYS-04"])
    mer_bad = skill_meridian_route(["MATH-09", "NOPE-99"])
    checks.append(mer["hops"] == 3 and len(mer["edges"]) == 3 and mer["missing"] == []
                  and mer["api_calls"] == 0 and mer_bad["missing"] == ["NOPE-99"])

    # 代谢
    hb = skill_hebbian_update()
    hb_prune = skill_hebbian_update(decay=0.49)
    checks.append(all(r["w_after_coactivate"] > r["w_before"] for r in hb["updated"])
                  and all(r["w_after_decay"] <= r["w_after_coactivate"] for r in hb["updated"])
                  and hb["pruned_count"] == 0 and hb_prune["pruned_count"] >= 1)
    far = skill_far_pairs(4)
    checks.append(far["count"] == 4
                  and all(ITEMS[p["a"]]["domain"] != ITEMS[p["b"]]["domain"] for p in far["pairs"])
                  and all(far["pairs"][i]["distance"] >= far["pairs"][i + 1]["distance"]
                          for i in range(len(far["pairs"]) - 1)))
    skc = skill_skc_distill("TCM-02", "PHYS-01", 1.4)
    skc_cs = skill_skc_distill("MATH-09", "AI-03", 1.4)
    checks.append(skc["ok"] is True and skc["safety"]["gate"] == "skin.medical_disclaimer"
                  and skc["safety"]["disclaimer_required"] is True
                  and skc_cs["safety"]["gate"] is None
                  and skc["relations"][0]["verified"] is False
                  and bool(skc["relations"][0]["counterexample"])
                  and skc["query_templates"][0]["anti_label_score"] == 0.68)
    checks.append(skill_skc_distill("MATH-09", "NOPE-99")["ok"] is False)

    # 闸门三态 + 绝对断言
    g1 = skill_skin_gate("帮我做个浏览器插件对接B站推荐位")
    g2 = skill_skin_gate("这个方子加多少剂量")
    g3 = skill_skin_gate("整理一份学习日程")
    g4 = skill_skin_gate("这个方案一定有效")
    checks.append(g1["veto"] == "refused_op" and g2["veto"] == "medical_assertion"
                  and g3["allowed"] is True and g4["veto"] == "absolute_claim"
                  and len(REFUSED_OPS) >= 20)

    # 宣告 / 白皮书 / 对照表 / 兜底 / 审计
    dec = skill_self_declaration()
    checks.append(dec["block_count"] == 4 and dec["metaphor"] is True
                  and "身份边界" in dec["prompt_text"] and "拒绝清单" in dec["prompt_text"])
    wp = skill_whitepaper_outline()
    checks.append(wp["chapter_count"] == 7 and wp["total_words"] == 19500
                  and all(c["points"] for c in wp["chapters"]))
    io_ = skill_interop_map()
    checks.append(io_["row_count"] == 20 and io_["unimplemented"] == ["沙箱隔离"])
    dg = skill_degradation_plan()
    checks.append(dg["level_count"] == 3 and all(l["auto"] is False for l in dg["levels"])
                  and dg["escalate_to"] == "carbon_based_arbiter")
    a1, a2 = skill_audit_receipt("omnicore"), skill_audit_receipt("omnicore")
    checks.append(len(a1["fingerprint"]) == 16 and a1["fingerprint"] == a2["fingerprint"]
                  and a1["final"] == "carbon_based_arbiter"
                  and a1["server_metrics"] == "pending_human_measure")

    return all(checks), f"{sum(checks)}/{len(checks)} 全息纪元包（20技能/0agent/6工作流/5修正/22拒绝）"


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
    ("G20 omnilife", g20_omnilife),
    ("G21 omnicore", g21_omnicore),
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
