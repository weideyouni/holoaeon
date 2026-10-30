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
                  and "omnicore" in EXTRA_PACK_ORDER)

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


def g22_metab() -> Tuple[bool, str]:
    """代谢层包：26 技能 / 0 agent / T1-T8 / 维度不变 / 六染色体 / 8 处冲突消解 / fail-closed。"""
    from .kernel import Kernel
    from .packs import EXTRA_PACK_ORDER, get_extra_pack
    from .packs.metab_pack import (
        pack_summary, CONFLICTS, REFUSED_OPS, CHROMOSOMES, PURITY_LADDER,
        STATES, STAGES, AUTH_LAYERS, REDLINES, ANTIPATTERNS, COMBO_WHITELIST_SEED,
        skill_metab_genome_schema, skill_metab_genome_validate, skill_metab_purity_ladder,
        skill_metab_state_classify, skill_metab_state_effects, skill_metab_rhythm_plan,
        skill_metab_lifecycle_transition, skill_metab_sham_report, skill_metab_sleep_plan,
        skill_metab_archive_package, skill_metab_authority_layers,
        skill_metab_fail_closed_check, skill_metab_gut_channels, skill_metab_contagion_scan,
        skill_metab_lineage_record, skill_metab_trust_radius, skill_metab_borrowed_ratio,
        skill_metab_sensor_loop, skill_metab_probe_baseline, skill_metab_combo_check,
        skill_metab_redlines, skill_metab_scorecard, skill_metab_interface_contract,
        skill_metab_generation_gate, skill_metab_antipattern_scan, skill_metab_audit_receipt,
    )
    checks: List[bool] = []

    # 包级：注册、计数、维度不变
    s = pack_summary()
    checks.append("metab" in EXTRA_PACK_ORDER and get_extra_pack("metab").key == "metab")
    checks.append(s["skills"] == 26 and s["workflows"] == 8 and s["agents_created"] == 0
                  and s["addressing_unchanged"] is True
                  and s["locks"]["rows_total"] == 1331 and s["locks"]["nodes_total"] == 108641)
    k = Kernel()
    rep = get_extra_pack("metab").install(k)
    checks.append(len(rep["skills"]) == 26 and len(rep["agents"]) == 0
                  and k.skills.has("metab.genome_validate"))

    # 六个染色体 + 8 处冲突消解
    schema = skill_metab_genome_schema()
    checks.append(schema["count"] == 6
                  and all(c["criterion"] and c["bad"] and c["axiom"] for c in schema["chromosomes"]))
    checks.append(len(CONFLICTS) == 8
                  and all(c["A"] and c["B"] and c["chosen"] in ("A", "B") for c in CONFLICTS)
                  and len({c["id"] for c in CONFLICTS}) == 8)

    # 基因组校验：缺条 / 合格 / 三类语义 veto
    v0 = skill_metab_genome_validate()
    checks.append(v0["allowed"] is False and len(v0["missing_chromosomes"]) == 6)
    good = {"phenotype": {"does": "a", "produces": "b", "not_do": "c"},
            "purity": {"level": "官方文档级", "evidence_kind": "doc"},
            "lineage": {"source": "s", "license": "MIT",
                        "contagion_class": "none", "hash_chain": ["h1"]},
            "toxicity": {"blast_radius": "1 slot", "irreversible_point": "none",
                         "degradation_path": "backup", "level": "green"},
            "energy": {"compute": "0", "storage": "0", "external_calls": "0",
                       "attention_quota": "0"},
            "rhythm": {"plug_state": "breathing", "depends_on": [],
                       "depended_by": [], "unload_cost": "0"}}
    checks.append(skill_metab_genome_validate(good)["allowed"] is True)
    bad_tox = dict(good)
    bad_tox["toxicity"] = {"blast_radius": "x", "irreversible_point": "x", "level": "red"}
    checks.append("no_degradation_path" in skill_metab_genome_validate(bad_tox)["vetoes"])
    bad_pur = dict(good)
    bad_pur["purity"] = {"level": "黑箱借用级", "evidence_kind": "behavior"}
    checks.append("black_box_without_borrowed_tag"
                  in skill_metab_genome_validate(bad_pur)["vetoes"])

    # 纯度四级：黑箱不得进主干
    lad = skill_metab_purity_ladder("黑箱借用级")["query"]
    checks.append(lad["rank"] == 3 and lad["may_enter_backbone"] is False
                  and len(PURITY_LADDER) == 4
                  and skill_metab_purity_ladder("官方文档级")["query"]["may_enter_backbone"] is True)

    # 四问定态：优先级 + 保守默认
    checks.append(skill_metab_state_classify({"touches_main_slot": True})["state"] == "metabolism")
    checks.append(skill_metab_state_classify({"rewrites_hebbian_baseline": True})["state"] == "metabolism")
    checks.append(skill_metab_state_classify({"crosses_trust_boundary": True})["state"] == "circulation")
    checks.append(skill_metab_state_classify({"new_data_source": True})["state"] == "metabolism")
    checks.append(skill_metab_state_classify({"only_threshold": True})["state"] == "breathing")
    unk = skill_metab_state_classify({})
    checks.append(unk["state"] == "circulation" and unk["questions_fired"] == [])
    eff = skill_metab_state_effects()
    checks.append([r["boundary"] for r in eff["rows"]]
                  == ["tick 边界", "心跳屏障边界（一次对齐后生效）", "checkpoint 边界"]
                  and len(STATES) == 3)

    # 节律：依赖优先于态序；有环拒绝装载
    plan = skill_metab_rhythm_plan([
        {"id": "a", "state": "metabolism"},
        {"id": "b", "state": "breathing"},
        {"id": "c", "state": "circulation", "depends_on": ["a"]}])
    checks.append(plan["load_order"] == ["b", "a", "c"]
                  and plan["unload_order"] == ["c", "a", "b"] and plan["ok"] is True)
    cyc = skill_metab_rhythm_plan([{"id": "x", "depends_on": ["y"]},
                                   {"id": "y", "depends_on": ["x"]}])
    checks.append(cyc["ok"] is False and sorted(cyc["cycles"]) == ["x", "y"])

    # 生命周期：假饲不可跳过、负结论阻断、观察有最小拍数、灰度仅在只读态可降级
    t1 = skill_metab_lifecycle_transition("sham", {"sham_data": True, "sham_verdict": "positive"})
    checks.append(t1["next"] == "gray" and t1["skippable"] is False)
    t2 = skill_metab_lifecycle_transition("sham", {"sham_data": True, "sham_verdict": "negative"})
    checks.append(t2["allowed"] is False and "sham_verdict_negative" in t2["blocked_by"])
    t3 = skill_metab_lifecycle_transition("observe", {"observe_ticks": 10})
    checks.append(t3["allowed"] is False and "observe_ticks_below_min" in t3["blocked_by"])
    t4 = skill_metab_lifecycle_transition("gray", {"gray_ran": True, "read_only": True,
                                                   "writes_state": False, "external_calls": 0})
    checks.append(t4["skippable"] is True and len(STAGES) == 8)

    # 假饲报告：样本量与增益阈值
    sh1 = skill_metab_sham_report({"succ": 0.80}, {"succ": 0.90}, 10)
    checks.append(sh1["verdict"] == "insufficient" and sh1["may_advance_to_gray"] is False)
    sh2 = skill_metab_sham_report({"succ": 0.80}, {"succ": 0.90}, 40)
    checks.append(sh2["verdict"] == "positive" and sh2["effective_now"] is False)

    # 休眠 / 归档
    sl = skill_metab_sleep_plan({"id": "s1", "hebbian_edges": ["e1"]})
    checks.append(sl["allowed"] is False and sl["blocked_by"] == ["no_backup_path"]
                  and sl["hebbian"]["action"] == "freeze")
    checks.append(skill_metab_sleep_plan({"id": "s1", "backup_path": ["p2"]})["allowed"] is True)
    checks.append(skill_metab_archive_package({"config": 1})["status"] == "archived_incomplete"
                  and skill_metab_archive_package({"config": 1, "genome": 1, "lineage": 1,
                                                   "effect_report": 1, "rebuild_ref": 1,
                                                   "hash": 1})["status"] == "archived")

    # 三层授权 + fail-closed
    checks.append(len(AUTH_LAYERS) == 3
                  and [r["cycle"] for r in skill_metab_authority_layers()["layers"]]
                  == ["季度级", "周级", "会话级"])
    bad_cfg = skill_metab_fail_closed_check({"new_symbiote_default": "on",
                                             "remember_choice": True,
                                             "fasting_mode": False, "auto_widen": True})
    checks.append(bad_cfg["compliant"] is False and len(bad_cfg["violations"]) == 6)
    good_cfg = skill_metab_fail_closed_check({"new_symbiote_default": "off",
                                              "red_toxicity_second_confirm": True,
                                              "one_key_return": True, "fasting_mode": True})
    checks.append(good_cfg["compliant"] is True)

    # 消化道双通道：结构 IR 只放哈希
    gc = skill_metab_gut_channels({"entities": 1, "provenance_hashes": ["h"],
                                   "carries_verbatim": False})
    gb = skill_metab_gut_channels({"text": "原文", "carries_verbatim": True})
    checks.append(gc["ir_check"]["passed"] is True and gb["ir_check"]["passed"] is False
                  and "原始材料" in gc["contract"]["construct"]["must_not_read"])

    # 传染性：跨域即隔离区
    checks.append(skill_metab_contagion_scan({"rewrites_downstream_terms": True,
                                              "domains": ["MED", "TCM"]})["zone"] == "quarantine")
    checks.append(skill_metab_contagion_scan({"rewrites_downstream_terms": False})["zone"] == "main")

    # 血统链：可验 + 篡改即断
    n1 = skill_metab_lineage_record({"symbiote": "s1", "source": "u", "license": "MIT",
                                     "purity": "p"})
    node1 = {"chain_hash": n1["chain_hash"], "payload_hash": n1["payload_hash"],
             "prev_hash": "", "symbiote": "s1", "source": "u", "license": "MIT", "purity": "p"}
    checks.append(skill_metab_lineage_record(chain=[node1])["verified"] is True)
    node2 = dict(node1)
    node2["source"] = "u-tampered"
    checks.append(skill_metab_lineage_record(chain=[node2])["verified"] is False
                  and skill_metab_lineage_record(chain=[node2])["broken_at"] == [0])

    # 信任半径 / 借来信念
    tr = skill_metab_trust_radius({"name": "api", "read_scope": "r", "return_scope": "x",
                                   "degradation_path": "backup"})
    checks.append(tr["allowed"] is True and tr["borrowed"] is True
                  and tr["fasting_unavailable"] is True)
    br = skill_metab_borrowed_ratio(
        [{"id": "c%d" % i} for i in range(6)] + [{"id": "c6", "depends_on": ["d1"]}],
        {"d1": {"audited": False}})
    checks.append(br["borrowed"] == 1 and br["total"] == 7
                  and br["borrowed_ratio"] == round(1 / 7, 6) and br["within_limit"] is True)

    # 感受器闭环：收敛即降权；噪声底不动作；基线重建属代谢态
    se = skill_metab_sensor_loop({"direction": "convergence", "magnitude": 0.08}, {"t1": 0.5})
    checks.append(se["template_weights_after"] == {"t1": 0.4}
                  and se["temperature_delta"] == -0.2 and se["state"] == "breathing")
    checks.append(skill_metab_sensor_loop({"direction": "convergence", "magnitude": 0.001},
                                          {"t1": 0.5})["action"] == "below_noise_floor")
    pb = skill_metab_probe_baseline([{"id": "p"}], False)
    checks.append(pb["allowed"] is False and pb["state"] == "metabolism"
                  and pb["boundary"] == "checkpoint 边界")

    # 组合治理：白名单 / 未知 / 放大需整体评审 / 传染传播
    ok_combo = skill_metab_combo_check([{"id": "a", "category": "probe_set",
                                         "purity": {"level": "公开语料级"}},
                                        {"id": "b", "category": "strategy",
                                         "purity": {"level": "公开语料级"}}])
    checks.append(ok_combo["allowed"] is True and len(COMBO_WHITELIST_SEED) == 4)
    unk_combo = skill_metab_combo_check([{"id": "a", "category": "probe_set"},
                                        {"id": "b", "category": "external_capability"}])
    checks.append(unk_combo["allowed"] is False
                  and "unknown_pair_not_in_whitelist" in unk_combo["blocked_by"])
    amp = skill_metab_combo_check([{"id": "a", "category": "probe_set", "amplifies": ["z"]},
                                   {"id": "b", "category": "strategy"}], reviewed=False)
    checks.append(amp["review_required"] is True
                  and "high_risk_combo_needs_whole_review" in amp["blocked_by"])

    # 红线 / 度量卡
    rl = skill_metab_redlines()
    checks.append(len(rl["redlines"]) == 4 and len(REDLINES) == 4
                  and rl["zero_tolerance"] == ["不可逆事件数"])
    gates_ok = {"sham_data": True, "degradation_path": "b", "one_key_disable": True,
                "lineage": "h"}
    energy_ok = {"compute": 0, "storage": 0, "external_calls": 0,
                 "attention_interruptions": 1}
    sc_pass = skill_metab_scorecard(
        {"sham_gain": 0.2, "task_success_rate": 0.95}, energy_ok,
        {"irreversible_events": 0},
        {"residue_after_sleep": 0, "core_availability_after_force_remove": 0.995},
        {"borrowed_belief_ratio": 0.1, "fasting_coverage": 0.5}, gates_ok)
    checks.append(sc_pass["verdict"] == "pass")
    sc_rej = skill_metab_scorecard(
        {"sham_gain": 0.2, "task_success_rate": 0.95}, energy_ok,
        {"irreversible_events": 1},
        {"residue_after_sleep": 0, "core_availability_after_force_remove": 0.995},
        {"borrowed_belief_ratio": 0.1, "fasting_coverage": 0.5}, gates_ok)
    checks.append(sc_rej["verdict"] == "reject"
                  and "immunity:irreversible_event_nonzero" in sc_rej["reasons"])

    # 接口契约 / 代际 / 反模式 / 回执
    ic = skill_metab_interface_contract()
    checks.append(ic["count"] == 9
                  and all(r["violation"] for r in ic["rows"]))
    checks.append(skill_metab_generation_gate(
        [{"card_id": "c1", "generation": 3}, {"card_id": "c2", "generation": 2}], 3
    )["stale"] == ["c2"])
    checks.append(len(ANTIPATTERNS) == 7
                  and skill_metab_antipattern_scan({"bulk_enable_all": True,
                                                     "sham_skipped": True})["count"] == 2)
    a1, a2 = skill_metab_audit_receipt([{"kind": "k", "ref": "r", "result": "ok"}] * 2), \
        skill_metab_audit_receipt([{"kind": "k", "ref": "r", "result": "ok"}] * 2)
    checks.append(len(a1["fingerprint"]) == 16 and a1["fingerprint"] == a2["fingerprint"]
                  and a1["execution"] == "human_manual")
    checks.append(len(REFUSED_OPS) == 12
                  and all(len([c for c in CHROMOSOMES]) == 6 for _ in range(1)))

    return all(checks), f"{sum(checks)}/{len(checks)} 代谢层包（26技能/0agent/8工作流/6染色体/8冲突）"


def g23_nephron() -> Tuple[bool, str]:
    """肾单位 P0 包：24 技能 / 0 agent / W1-W7 / 41 字段 / 27 理由码 / 10 处审视 / 只读回放。"""
    from .kernel import Kernel
    from .packs import EXTRA_PACK_ORDER, get_extra_pack
    from .packs.nephron_pack import (
        pack_summary, CONFLICTS, FIXES, REFUSED_OPS, NON_GOALS, ACCEPTANCE,
        REASON_CODES, EVENT_TYPES, APPEND_REJECTS, FIELD_TOTAL, RAW_LEN_UNIT,
        skill_nephron_page_schema, skill_nephron_page_validate, skill_nephron_ledger_record,
        skill_nephron_ledger_verify, skill_nephron_reason_codes, skill_nephron_event_validate,
        skill_nephron_manifest_build, skill_nephron_switch_policy, skill_nephron_collect_plan,
        skill_nephron_failure_injection_matrix, skill_nephron_replay_window,
        skill_nephron_replay_slots, skill_nephron_replay_inputs, skill_nephron_replay_timeline,
        skill_nephron_replay_determinism, skill_nephron_privacy_policy,
        skill_nephron_erase_operation, skill_nephron_generation_fingerprint,
        skill_nephron_fingerprint_check, skill_nephron_zero_intrusion_check,
        skill_nephron_non_goal_scan, skill_nephron_acceptance_check,
        skill_nephron_field_dictionary, skill_nephron_audit_receipt,
    )
    checks: List[bool] = []

    # 包级：注册 / 计数 / 维度不变
    s = pack_summary()
    checks.append("nephron" in EXTRA_PACK_ORDER and get_extra_pack("nephron").key == "nephron")
    checks.append(s["skills"] == 24 and s["workflows"] == 7 and s["agents_created"] == 0
                  and s["addressing_unchanged"] is True
                  and s["locks"]["rows_total"] == 1331 and s["locks"]["nodes_total"] == 108641)
    k = Kernel()
    rep = get_extra_pack("nephron").install(k)
    checks.append(len(rep["skills"]) == 24 and len(rep["agents"]) == 0
                  and k.skills.has("nephron.replay_window"))
    checks.append(s["structures"] == 5 and s["fields"] == FIELD_TOTAL == 41
                  and s["event_types"] == 11 and s["reason_codes"] == 27)
    checks.append(s["conflicts"] == 10 and [c["id"] for c in CONFLICTS]
                  == ["N%d" % i for i in range(1, 11)]
                  and all(c["A"] and c["B"] and c["chosen"] in ("A", "B") for c in CONFLICTS))
    checks.append(s["fixes"] == 3 and all(f["finding"] and f["fix"] for f in FIXES))
    checks.append(len(REFUSED_OPS) == 12 and len(NON_GOALS) == 6 and len(ACCEPTANCE) == 8
                  and len(APPEND_REJECTS) == 3)

    # 记录结构：41 字段 / raw_len 口径锁定
    sch = skill_nephron_page_schema()
    checks.append(sch["field_total"] == 41 and sch["structure_count"] == 5
                  and sch["raw_len_unit"] == RAW_LEN_UNIT == "token")
    fd = skill_nephron_field_dictionary()
    checks.append(fd["count"] == 41 and fd["match_schema"] is True
                  and [r["structure"] for r in fd["rows"]][0] == "Page")

    # Page 校验：合格 / 无血统留空 / NONE 合法 / importance 缺失只告警
    page = {"page_id": "p1", "origin": "session", "payload_digest": "aabbccddeeff0011",
            "raw_len": 120, "form": "raw", "importance": 0.4, "last_tick": 7,
            "hit_count": 2, "lineage_ref": "L-9", "fingerprint": "FP1"}
    checks.append(skill_nephron_page_validate(page)["ok"] is True)
    checks.append(skill_nephron_page_validate(dict(page, lineage_ref=""))["errors"]
                  == ["lineage_ref_empty_forbidden"])
    none_page = {kk: vv for kk, vv in page.items() if kk != "importance"}
    none_page["lineage_ref"] = "NONE"
    pv = skill_nephron_page_validate(none_page)
    checks.append(pv["ok"] is True and pv["warnings"] == ["importance_absent_recorded_as_zero"]
                  and "显式 NONE" in pv["lineage_tag"])
    checks.append(skill_nephron_page_validate(dict(page, origin="kernel"))["errors"] == ["enum:origin"])

    # LedgerRecord：合格 / 压缩比必须 null / 时钟回跳 / 主键重复 / 改写字段
    rec = {"tick": 7, "seq": 0, "window_budget": 8, "window_used": 3,
           "layer_residency": {"working": 1, "hebbian": 1, "skeleton": 0, "external": 1},
           "hit_rate": None, "compression_ratio": None, "evicted_pages": 0,
           "external_calls": 1, "cost_estimate": 0.2, "confidence_estimate": None,
           "events": [], "fingerprint": "FP1"}
    checks.append(skill_nephron_ledger_record(rec)["ok"] is True)
    checks.append(skill_nephron_ledger_record(dict(rec, compression_ratio=0.5))["append_rejects"]
                  == ["APPEND_REJECT_SCHEMA_INVALID"])
    checks.append(skill_nephron_ledger_record(dict(rec, tick=3, seq=1),
                                              watermark=7)["append_rejects"]
                  == ["APPEND_REJECT_CLOCK_REGRESSION"])
    checks.append(skill_nephron_ledger_record(dict(rec, seq=1),
                                              seen_keys=[[7, 1]])["append_rejects"]
                  == ["APPEND_REJECT_DUPLICATE_PK"])
    checks.append(skill_nephron_ledger_record(dict(rec, updated_at="now"))["append_rejects"]
                  == ["APPEND_REJECT_SCHEMA_INVALID"])
    checks.append(skill_nephron_ledger_record(
        dict(rec, layer_residency={"working": 1}))["errors"] == ["layer_residency_keys"])

    # 账本核验：正常 / 序号缺口 / tick 倒退 / 锚点不符
    evs = [{"type": "page_admit", "reason_code": "ADMIT_RECENT", "refs": ["p1"],
            "delta": {"score": 0.7}},
           {"type": "page_admit", "reason_code": "ADMIT_LINEAGE_TRUSTED", "refs": ["p2"],
            "delta": {"score": 0.5}},
           {"type": "page_summarize", "reason_code": "SUMM_BUDGET_PRESSURE", "refs": ["p3"],
            "delta": {"from_len": 900, "to_len": 90}},
           {"type": "page_reject", "reason_code": "REJECT_REDUNDANT", "refs": ["p4"], "delta": {}}]
    ledger = [dict(rec, events=[]), dict(rec, tick=8, seq=1, window_used=2, events=evs)]
    good = skill_nephron_ledger_verify(ledger)
    checks.append(good["ok"] is True and good["checks"]["seq_no_gap"] is True
                  and len(good["chain_digest"]) == 16)
    gapped = skill_nephron_ledger_verify([dict(rec, seq=0), dict(rec, tick=8, seq=2)])
    checks.append(gapped["ok"] is False and gapped["checks"]["seq_no_gap"] is False)
    backwards = skill_nephron_ledger_verify([dict(rec, tick=9, seq=0), dict(rec, tick=8, seq=1)])
    checks.append(backwards["ok"] is False and backwards["checks"]["tick_non_decreasing"] is False)
    checks.append(skill_nephron_ledger_verify(ledger, anchor="DEAD")["anchor_mismatch"] is True)
    checks.append(skill_nephron_ledger_verify(ledger, anchor=good["chain_digest"])["ok"] is True)

    # 理由码：27 码 / 10 族 / UNKNOWN 不入表 / R-01 评审留痕
    rc = skill_nephron_reason_codes()
    checks.append(rc["codes"] == 27 and len(REASON_CODES) == 27
                  and rc["unknown"]["in_table"] is False and rc["unknown"]["code"] == "UNKNOWN")
    checks.append(rc["codes_by_family"]["window"] == ["WINDOW_BUILD_COMPLETE"]
                  and rc["reviews"][0]["id"] == "R-01")

    # 事件校验：合格 / 类型码错配 / UNKNOWN 兜底计数 / 单主码 / delta 非数值
    ok_ev = skill_nephron_event_validate({"type": "page_admit", "reason_code": "ADMIT_RECENT",
                                          "refs": ["p1"], "delta": {"score": 0.6}})
    checks.append(ok_ev["ok"] is True and ok_ev["alarm"] == 0)
    checks.append(skill_nephron_event_validate({"type": "page_reject",
                                                "reason_code": "ADMIT_RECENT",
                                                "refs": ["p1"]})["errors"]
                  == ["reason_code_type_mismatch"])
    unk = skill_nephron_event_validate({"type": "page_reject", "reason_code": "UNKNOWN",
                                        "refs": ["p1"]})
    checks.append(unk["ok"] is True and unk["unclassified"] is True and unk["alarm"] == 1)
    checks.append(skill_nephron_event_validate({"type": "window_build",
                                                "reason_code": "WINDOW_BUILD_COMPLETE",
                                                "refs": []})["ok"] is True)
    checks.append(skill_nephron_event_validate({"type": "page_reject",
                                                "reason_code": "REJECT_REDUNDANT",
                                                "refs": ["p1"], "sub_reason_code": "X"})["errors"]
                  == ["single_main_reason_code_only:sub_reason_code"])
    checks.append(skill_nephron_event_validate({"type": "retrieval",
                                                "reason_code": "RETRIEVAL_TIMEOUT",
                                                "refs": [], "delta": {"ms": "slow"}})["errors"]
                  == ["delta_not_numeric:ms"])
    checks.append(len(EVENT_TYPES) == 11)

    # 窗口清单：计数 / 摘要变短 / 缺码
    man = skill_nephron_manifest_build(evs, 8, 2, "FP1")
    checks.append(man["counts"] == {"admitted": 2, "summarized": 1, "rejected": 1}
                  and man["ok"] is True)
    checks.append(skill_nephron_manifest_build(
        [{"type": "page_summarize", "reason_code": "SUMM_BUDGET_PRESSURE",
          "refs": ["p9"], "delta": {"from_len": 10, "to_len": 99}}])["issues"]
                  == ["summary_not_shorter"])

    # 开关三档：可回放范围 / 默认 off / 采样率校验
    sw = skill_nephron_switch_policy()
    checks.append(sw["mode"] == "off" and sw["enabled"] is False
                  and sw["replayable_scope"] == "none" and sw["default"] == "off")
    checks.append(skill_nephron_switch_policy("sampled", 0.1)["replayable_scope"]
                  == "only_sampled_ticks")
    checks.append(skill_nephron_switch_policy("full")["replayable_scope"] == "all_ticks")
    checks.append(skill_nephron_switch_policy("sampled", 0.0)["errors"]
                  == ["sample_rate_out_of_range"])

    # 采集契约 / 故障矩阵
    cp = skill_nephron_collect_plan()
    checks.append(cp["hook_count"] == 11 and cp["rules"]["flush"].startswith("host_managed")
                  and len(cp["rules"]["drop_counters"]) == 3)
    fi = skill_nephron_failure_injection_matrix()
    checks.append(fi["count"] == 4
                  and [r["fault"] for r in fi["rows"]]
                  == ["queue_full", "write_fail", "serialize_fail", "clock_regression"]
                  and all(r["forbidden"] for r in fi["rows"]))

    # 回放四件套 + 确定性
    w = skill_nephron_replay_window(ledger, 8, "full")
    checks.append(w["replayable"] is True and w["counts"]["admitted"] == 2
                  and w["manifest"]["fingerprint"] == "FP1")
    checks.append(skill_nephron_replay_window(ledger, 8, "sampled")["reason"]
                  == "partial_ledger_not_replayable")          # N2
    checks.append(skill_nephron_replay_window(ledger, 99, "full")["reason"]
                  == "tick_not_in_ledger")
    snaps = [{"tick": 4, "entries": [
        {"slot_id": "s2", "slot_class": "trunk", "occupant_page": "p1", "allocated_tick": 4,
         "fragment_flag": False, "owner_symbiont": None, "reclaimability": "cold"},
        {"slot_id": "s1", "slot_class": "reserve", "occupant_page": None, "allocated_tick": 3,
         "fragment_flag": True, "owner_symbiont": "m-1", "reclaimability": "hot"}]}]
    sl = skill_nephron_replay_slots(snaps, 8)
    checks.append(sl["available"] is True and sl["snapshot_tick"] == 4
                  and sl["age_ticks"] == 4 and sl["stale"] is False
                  and [e["slot_id"] for e in sl["entries"]] == ["s1", "s2"]
                  and sl["replay_scope"] == "snapshot_only")     # N10 的降级声明
    checks.append(skill_nephron_replay_slots(snaps, 40)["stale"] is True)
    checks.append(skill_nephron_replay_slots([], 8)["reason"] == "no_snapshot_at_or_before_tick")
    inp = skill_nephron_replay_inputs(ledger, 8)
    checks.append(inp["available"] is True and inp["window_used"] == 2
                  and inp["hit_rate"] is None and inp["hit_rate_null_ok"] is True
                  and inp["compression_ratio"] is None)
    tl = skill_nephron_replay_timeline(ledger, 0, 99)
    checks.append(tl["count"] == 2 and tl["rows"][-1]["entered"] == ["p1", "p2"]
                  and tl["rows"][-1]["rejected"] == 1)
    det = skill_nephron_replay_determinism(ledger)
    checks.append(det["stable"] is True and det["hash_1"] == det["hash_2"]
                  and len(det["hash_1"]) == 16)                  # A4

    # 隐私与擦除
    pp = skill_nephron_privacy_policy()
    checks.append(pp["count"] == 6
                  and any("请求体明文" in r["forbidden"] for r in pp["rows"]))
    er = skill_nephron_erase_operation([{"page_id": "p1", "payload_digest": "aabbccdd"}])
    checks.append(er["ok"] is True and er["plan"][0]["payload_digest_after"].startswith("ERASED:")
                  and "raw_len" in er["plan"][0]["keep"]
                  and "改写历史记录" in er["forbidden"])            # N3

    # 指纹：联合哈希 / 缺项 / 失配拦截
    fp = skill_nephron_generation_fingerprint(
        {"weights": "w", "templates": "t", "quantization": "q4",
         "loras": ["b", "a"], "retriever": "r1"})
    checks.append(fp["ok"] is True and fp["missing"] == [] and len(fp["fingerprint"]) == 16
                  and fp["canonical"]["loras"] == ["a", "b"])
    checks.append(skill_nephron_generation_fingerprint({"weights": "w"})["missing"]
                  == ["templates", "quantization", "loras", "retriever"])
    checks.append(skill_nephron_fingerprint_check("A", "A")["reuse_allowed"] is True)
    bad_fp = skill_nephron_fingerprint_check("A", "B", model_changed=True)
    checks.append(bad_fp["mismatch"] is True and bad_fp["reuse_allowed"] is False
                  and bad_fp["event"]["type"] == "fingerprint_mismatch"
                  and bad_fp["code"] == "FINGERPRINT_MISMATCH_MODEL")   # A7

    # 边界：零侵入契约（只能是 pending）/ 非目标 / A1-A8 状态机
    zi = skill_nephron_zero_intrusion_check()
    checks.append(zi["status"] == "pending_human_measure" and zi["pack_can_prove"] is False)
    checks.append(skill_nephron_non_goal_scan({"paging": True, "compression": True,
                                               "budget_control": True})["count"] == 3)
    ac = skill_nephron_acceptance_check()
    checks.append(ac["pending"] == ["A1", "A2"] and ac["verdict"] == "provisional"
                  and ac["count"] == 8)
    checks.append(skill_nephron_acceptance_check({"A4": "fail"})["verdict"] == "reject")
    checks.append(all(r["status"] != "pass" or r["pack_can_prove"] == "true"
                      for r in ac["rows"]))

    # 回执
    a1, a2 = skill_nephron_audit_receipt([{"kind": "k", "ref": "r", "result": "ok"}]), \
        skill_nephron_audit_receipt([{"kind": "k", "ref": "r", "result": "ok"}])
    checks.append(len(a1["fingerprint"]) == 16 and a1["fingerprint"] == a2["fingerprint"]
                  and a1["execution"] == "human_manual")

    return all(checks), f"{sum(checks)}/{len(checks)} 肾单位 P0 包（24技能/0agent/7工作流/41字段/27码/10审视）"


def g24_uplift() -> Tuple[bool, str]:
    """补齐短板升级包 U1–U6：24 技能 / 0 agent / W1–W7 / 六单元 / 十审视 / 五缺陷 / 十裁决。"""
    import json as _json
    import os as _os
    from .packs import EXTRA_PACK_ORDER, get_extra_pack
    from .packs.uplift_pack import (
        pack_summary, UNITS, CONFLICTS, FIXES, DEFECTS, STANCES, NON_GOALS,
        ACCEPTANCE, ADJUDICATIONS, REFUSED_OPS, REQUIRED_SECTIONS,
        skill_uplift_unit_registry, skill_uplift_order_key_check,
        skill_uplift_purity_contract, skill_uplift_regression_ledger,
        skill_uplift_ci_spec, skill_uplift_template_check, skill_uplift_badge_consistency,
        skill_uplift_support_matrix, skill_uplift_measure_a1_verdict,
        skill_uplift_measure_a2_disclosure, skill_uplift_evidence_chain,
        skill_uplift_ngram_dice, skill_uplift_hybrid_score_parts,
        skill_uplift_matching_acceptance, skill_uplift_bridge_boundary,
        skill_uplift_backend_registry, skill_uplift_remote_gate,
        skill_uplift_audit_policy, skill_uplift_live_receipt_schema,
        skill_uplift_adjudication, skill_uplift_p1_gate,
        skill_uplift_stance_matrix, skill_uplift_audit_receipt,
        skill_uplift_dimension_invariant,
    )
    checks: List[bool] = []

    # 包级：注册 / 计数 / 维度不变 / 不进 PACK_ORDER
    s = pack_summary()
    checks.append("uplift" in EXTRA_PACK_ORDER
                  and get_extra_pack("uplift").key == "uplift"
                  and len(EXTRA_PACK_ORDER) == 7)
    checks.append(s["skills"] == 24 and s["workflows"] == 7 and s["agents_created"] == 0)
    checks.append(s["addressing_unchanged"] is True
                  and s["locks"]["rows_total"] == 1331 and s["locks"]["nodes_total"] == 108641)
    checks.append(s["threads"] == 0 and s["timers"] == 0 and s["network"] is False
                  and s["disk_writes"] == 0 and s["deps"] == 0)
    checks.append(s["units"] == 6 and s["conflicts"] == 10 and s["fixes"] == 4
                  and s["defects"] == 5 and s["stances"] == 5 and s["non_goals"] == 6
                  and s["acceptance_items"] == 22 and s["adjudications"] == 10
                  and s["refused_ops"] == len(REFUSED_OPS) and len(REFUSED_OPS) >= 8)

    # U1：执行顺序 / 排序键全序 / 纯函数契约
    u = skill_uplift_unit_registry()
    checks.append(u["order_matches_spec"] is True
                  and [x["id"] for x in u["units"]] == ["U1", "U6", "U3", "U5", "U2", "U4"])
    recs = [{"agent_id": "a1", "out": i, "status": "ok"} for i in range(4)]
    recs += [{"agent_id": "a1", "out": 0, "status": "ok"}]        # 同 agent 同内容
    ok_key = skill_uplift_order_key_check(recs)
    checks.append(ok_key["verdict"] == "PASS"
                  and ok_key["agents_with_multiple_distinct_records"] == 1
                  and ok_key["distinct_contents"] == 4
                  and ok_key["key_injective_on_content"] is True)
    checks.append(skill_uplift_order_key_check([])["verdict"] == "UNCHECKED")
    checks.append(skill_uplift_purity_contract()["count"] == 4)

    # U6：回归口径 / CI 契约 / 模板 / 徽章 / 支持矩阵
    rl = skill_uplift_regression_ledger({"tests": 31, "selftest": 24, "redline_files": 37,
                                         "badge_tests": 31, "badge_selftest": "24/24"})
    checks.append(rl["verdict"] == "PASS" and rl["tests_not_decreased"] is True
                  and rl["before"]["badge_tests"] == 24)          # 旧徽章过期是事实
    ci = skill_uplift_ci_spec()
    checks.append(ci["pack_can_prove"] is False and len(ci["matrix"]) == 3
                  and len(ci["steps"]) == 4)
    tpl = {k: " ".join(v) for k, v in REQUIRED_SECTIONS.items()}
    checks.append(skill_uplift_template_check(tpl)["verdict"] == "PASS")
    checks.append(skill_uplift_template_check(
        {"bug_report": "复现步骤 期望"})["verdict"] == "FAIL")
    checks.append(skill_uplift_badge_consistency(
        {"badge": "tests-31%20passed selftest-24%2F24", "measured": {"tests": 31, "selftest": 24},
         "has_ci_note": True})["verdict"] == "PASS")
    checks.append(skill_uplift_badge_consistency(
        {"badge": "tests-31%20passed", "measured": {"tests": 31, "selftest": 24},
         "has_ci_note": True})["verdict"] == "FAIL")
    checks.append(skill_uplift_support_matrix(
        [{"py": "3.8", "status": "untested"}, {"py": "3.12", "status": "measured"}]
    )["verdict"] == "PASS")
    checks.append(skill_uplift_support_matrix([{"py": "3.8", "status": "assume pass"}])["verdict"]
                  == "FAIL")

    # U3：A1 判定（含变异证明）/ A2 披露 / 证据链
    root = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
    ev_path = _os.path.join(root, "docs", "nephron_a1_a2_evidence.json")
    ev = {}
    if _os.path.exists(ev_path):
        with open(ev_path, "r", encoding="utf-8") as fh:
            ev = _json.load(fh)
    a1 = skill_uplift_measure_a1_verdict(ev)
    checks.append(a1["status"] == "measured_with_scope"
                  and a1["mutation_makes_it_fail"] is True and a1["scope_declared"] is True)
    checks.append(skill_uplift_measure_a1_verdict({})["status"] == "pending_human_measure")
    no_mut = dict(ev)
    no_mut.pop("mutation_proof", None)
    checks.append(skill_uplift_measure_a1_verdict(no_mut)["mutation_makes_it_fail"] is False)
    a2 = skill_uplift_measure_a2_disclosure(ev)
    checks.append(a2["complete"] is True and a2["status"] == "measured"
                  and a2["threshold"] == "none — 披露项不是断言项（延续不设虚构目标值）")
    checks.append(skill_uplift_evidence_chain(ev)["verdict"] == "PASS")
    checks.append(skill_uplift_evidence_chain({"script": "s"})["verdict"] == "FAIL")

    # U5：n-gram / 混合分 / 两用例
    d1 = skill_uplift_ngram_dice({"query": "statistik", "text": "statistics"})
    d2 = skill_uplift_ngram_dice({"query": "统计销售额", "text": "统计数据清洗"})
    checks.append(d1["dice"] == 0.82353 and d2["dice"] == 0.22222)
    checks.append(skill_uplift_ngram_dice({"query": "", "text": "abc"})["dice"] == 0.0)
    checks.append(skill_uplift_hybrid_score_parts(
        {"jaccard": 1.0, "dice": 1.0, "tag_hit": 1})["score"] == 1.05)
    checks.append(skill_uplift_matching_acceptance(
        [{"id": "A-U5-1-cn", "top1": "stats_clean"}, {"id": "A-U5-1-en", "top1": "stats2"}]
    )["verdict"] == "PASS")
    checks.append(skill_uplift_matching_acceptance([])["verdict"] == "UNCHECKED")

    # U2：桥边界 / 后端 / 远程门禁 / 审计 / 回执语义
    checks.append(skill_uplift_bridge_boundary(
        {"core_files": ["holoaeon/kernel.py"], "bridge_files": ["bridges/transport.py"]}
    )["verdict"] == "PASS")
    checks.append(skill_uplift_bridge_boundary(
        {"core_files": ["holoaeon/http.py"], "bridge_files": ["holoaeon/bridge.py"]}
    )["verdict"] == "FAIL")
    bg = skill_uplift_backend_registry()
    checks.append(bg["count"] == 3 and any(b["name"] == "echo" for b in bg["backends"]))
    rg = skill_uplift_remote_gate([
        {"host": "127.0.0.1"},
        {"host": "10.0.0.5"},
        {"host": "10.0.0.5", "env_switch": True, "allow_remote": True},
        {"host": "10.0.0.5", "env_switch": True, "allow_remote": True, "allowlisted": True},
    ])["cases"]
    checks.append([c["reason"] for c in rg] == ["LOCAL", "REMOTE_LOCKED",
                                                "REMOTE_NOT_ALLOWLISTED", "REMOTE_ALLOWED"])
    checks.append(skill_uplift_audit_policy({"seq": 1, "prompt_sha16": "A", "tokens": {"a": 1}})
                  ["verdict"] == "PASS")
    checks.append(skill_uplift_audit_policy({"seq": 1, "prompt": "明文"})["verdict"] == "FAIL")
    checks.append(skill_uplift_live_receipt_schema()["count"] == 3)

    # U4：裁决 / P1 四判据
    adj = skill_uplift_adjudication()
    checks.append(adj["all_decided"] is True and [a["id"] for a in adj["adjudications"]]
                  == ["O-%d" % i for i in range(1, 11)]
                  and "after_summary" in adj["deviation"])
    pair = {"baseline": {"window_used": 8, "hit_rate": 0.5, "admitted": ["p1", "p2", "p3"]},
            "candidate": {"window_used": 8, "hit_rate": 0.5, "admitted": ["p1", "p2", "p3"],
                          "unknown_events": 0}}
    checks.append(skill_uplift_p1_gate(pair)["verdict"] == "PASS")
    bad_pair = {"baseline": {"window_used": 8, "hit_rate": 0.6, "admitted": ["p1", "p2"]},
                "candidate": {"window_used": 9, "hit_rate": 0.4, "admitted": ["p3"],
                              "unknown_events": 2}}
    bp = skill_uplift_p1_gate(bad_pair)
    checks.append(bp["verdict"] == "REJECT" and bp["checks"]["budget_not_up"] is False
                  and bp["checks"]["zero_unknown"] is False)
    checks.append(skill_uplift_p1_gate(
        {"baseline": {"hit_rate": None}, "candidate": {"hit_rate": None}}
    )["hit_rate_detail"]["verdict"] == "skipped")

    # 总：立场 / 维度 / 回执
    checks.append(skill_uplift_stance_matrix()["each_has_two_checks"] is True)
    checks.append(len(STANCES) == 5 and len(NON_GOALS) == 6 and len(FIXES) == 4
                  and len(DEFECTS) == 5 and len(CONFLICTS) == 10 and len(UNITS) == 6
                  and len(ACCEPTANCE) == 22)
    checks.append(skill_uplift_dimension_invariant()["verdict"] == "PASS")
    rc = skill_uplift_audit_receipt([{"unit": x, "ref": "r", "result": "ok"}
                                     for x in ("U1", "U2", "U3", "U4", "U5", "U6")])
    rc2 = skill_uplift_audit_receipt([{"unit": x, "ref": "r", "result": "ok"}
                                      for x in ("U1", "U2", "U3", "U4", "U5", "U6")])
    checks.append(rc["all_six"] is True and len(rc["fingerprint"]) == 16
                  and rc["fingerprint"] == rc2["fingerprint"] and rc["seal"] == "潮起开门，潮落闭嘴")

    bad = [i for i, ok in enumerate(checks) if not ok]
    return all(checks), (f"{sum(checks)}/{len(checks)} 补齐短板升级包（24技能/0agent/7工作流/"
                         f"6单元/10审视/5缺陷/10裁决/22验收）"
                         + (f" 失败项序号={bad}" if bad else ""))


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
    ("G22 metab", g22_metab),
    ("G23 nephron", g23_nephron),
    ("G24 uplift", g24_uplift),
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
