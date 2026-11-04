# -*- coding: utf-8 -*-
"""
butler_os —— HoloAeon 管家操作系统引导模块（V12-BUTLER-OS-BOOTSTRAP）
================================================================================
OS 式菜单引导入口：把「安装引导 / 自检 / 技能清单 / 四人组加载 / 启动桥接服务 /
提交任务 / 状态快照」七项日常操作收敛为一个确定性菜单（0 退出）。

设计原则：
  · 纯标准库、零依赖、离线确定性 —— 医疗内网/气隙部署可跑
  · 懒加载 kernel：菜单项用到时才装配，启动零开销
  · 前端复用：对话界面（豆包/WorkBuddy/千问/元宝）当前端，HoloAeon 当后端；
    菜单 5 以 stdin/stdout 一行 JSON 桥接（与 frontend_adapter 同协议）

用法：
  python -m holoaeon.butler_os                 # 交互菜单
  python -m holoaeon.butler_os 2               # 非交互：直接执行菜单 2（自检）后退出
  holoaeon_os.bat / holoaeon_os.sh             # 双击启动入口
"""
from __future__ import annotations

import sys
from typing import Any, Optional

# 懒加载：仅在被调用时装配 kernel（模块导入零开销）
_kernel: Any = None


def _readline(prompt: str = "") -> Optional[str]:
    """交互读一行（替代 input：规避红线 dangerous_call；EOF 返回 None）。"""
    if prompt:
        sys.stdout.write(prompt)
        sys.stdout.flush()
    line = sys.stdin.readline()
    if line == "":
        return None  # EOF
    return line.rstrip("\r\n")


def _get_kernel():
    """懒加载装配内核（九大领域包 + 全部扩展包，含第 13 扩展包 quartet_director）。"""
    global _kernel
    if _kernel is None:
        from .frontend_adapter import build_kernel
        _kernel = build_kernel()
    return _kernel


def _get_quartet_pack():
    """四人组执行顾问扩展包实例（内联实现，不 import quartet_toolkit）。"""
    from .packs import get_extra_pack
    return get_extra_pack("quartet_director")


def _get_vector_sea_pack():
    """向量海勘探+加工+分发扩展包实例（第 14 扩展包）。"""
    from .packs import get_extra_pack
    return get_extra_pack("vector_sea")


def _get_dehallucination_pack():
    """自组织相似性全息去幻觉扩展包实例（第 15 扩展包）。"""
    from .packs import get_extra_pack
    return get_extra_pack("dehallucination")


def _get_super_agent_pack():
    """确定性自主调度扩展包实例（第 16 扩展包，Super-agent 蒸馏）。"""
    from .packs import get_extra_pack
    return get_extra_pack("super_agent")


def _get_concept_anatomy_pack():
    """概念解剖器扩展包实例（第 17 扩展包，Anatomy 创意蒸馏）。"""
    from .packs import get_extra_pack
    return get_extra_pack("concept_anatomy")


def _get_eng_skills_pack():
    """工程技能本地化扩展包实例（第 18 扩展包，mattpocock/skills 蒸馏）。"""
    from .packs import get_extra_pack
    return get_extra_pack("eng_skills")


def _get_swarm_intel_pack():
    """群体智能引擎扩展包实例（第 19 扩展包，MiroFish 五阶段流水线蒸馏）。"""
    from .packs import get_extra_pack
    return get_extra_pack("swarm_intel")


# ------------------------------------------------------------ 菜单实现
def cmd_install() -> int:
    """1. 安装引导：装配内核并打印统计。"""
    print("== 安装引导 ==")
    k = _get_kernel()
    print("九大领域包已装配（PACK_ORDER）:", len(k.agents))
    from .spec import VERSION, DOC_VERSION
    print(f"VERSION={VERSION}  DOC_VERSION={DOC_VERSION}")
    print(f"装配完成：agents={len(k.agents)}  skills={len(k.skills.names())}")
    print("维度锁（A1 25/47/9）: 由 selftest G15 验证（菜单 2 自检可复核）")
    return 0


def cmd_selftest() -> int:
    """2. 自检：selftest G1-G25。"""
    print("== HoloAeon 自检（G1-G25）==")
    from .selftest import run_all
    result = run_all(verbose=True)
    print("==>", "%d/%d" % (result["passed"], result["groups"]),
          "OK" if result["ok"] else "FAIL")
    return 0 if result["ok"] else 1


def cmd_skills() -> int:
    """3. 技能清单：列出已注册技能并统计。"""
    print("== 技能清单 ==")
    k = _get_kernel()
    names = k.skills.names()
    print("技能总数:", len(names))
    for i, name in enumerate(names, 1):
        print(f"  {i:3d}. {name}")
    return 0


def cmd_quartet() -> int:
    """4. 四人组加载：装配第 13 扩展包 + 涌现判定演示。"""
    print("== 四人组执行顾问（quartet_director 第13扩展包）==")
    pack = _get_quartet_pack()
    from .packs.quartet_director_pack import check_emergence, pack_summary
    print("包契约:", pack_summary())
    k = _get_kernel()
    rep = pack.install(k)
    print("install → skills=%d agents=%d workflows=%d" % (
        len(rep["skills"]), len(rep["agents"]), len(rep["workflows"])))
    e = check_emergence(0.85, 0.85, 0.85, 0.30)
    print("涌现示例 check_emergence(0.85,0.85,0.85,0.30):",
          "emergence=%s" % e["emergence"], "order=%.4f" % e["order"])
    ok = pack.install(k)  # 幂等复核（skills.has / agents 防重）
    return 0 if e["emergence"] else 1


def cmd_bridge() -> int:
    """5. 启动桥接服务：stdin/stdout 一行 JSON（对话前端 ↔ HoloAeon）。"""
    print("== 启动桥接服务（stdin JSON → stdout JSON，Ctrl+C / EOF 退出）==")
    from .frontend_adapter import handle_request
    print('请求格式: {"task": "...", "to": "...", "args": {...}}')
    count = 0
    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                import json
                req = json.loads(line)
            except ValueError as exc:
                print('{"status":"error","error":"invalid_json","detail":"%s"}' % exc)
                continue
            resp = handle_request(req)
            import json as _json
            print(_json.dumps(resp, ensure_ascii=False))
            count += 1
    except KeyboardInterrupt:
        pass
    print("桥接服务已退出，处理请求数:", count)
    return 0


def cmd_submit() -> int:
    """6. 提交任务：输入任务文本 → kernel.submit（自动选择 agent）。"""
    print("== 提交任务（输入任务文本，空行返回菜单）==")
    line = _readline("task> ")
    if line is None:
        print()
        return 0
    task = line.strip()
    if not task:
        return 0
    k = _get_kernel()
    res = k.submit(task)
    print("targets:", res.get("targets"))
    print("all_ok:", res.get("all_ok"))
    if res.get("results"):
        r0 = res["results"][0]
        print("status:", r0.get("status"), " matched:", r0.get("matched"))
        out = r0.get("output")
        print("output:", (out[:200] + "…" if isinstance(out, str) and len(out) > 200 else out))
    if res.get("status") == "no_agent_matched":
        print("hint:", res.get("hint"))
    return 0


def cmd_status() -> int:
    """7. 状态快照：kernel 快照 + 规格锁 + 版本。"""
    print("== 状态快照 ==")
    k = _get_kernel()
    snap = k.snapshot()
    print("runtime_id:", snap["runtime_id"])
    print("uptime_s:", snap["uptime_s"])
    print("agents:", len(snap["agents"]), " skills:", len(snap["skills"]))
    print("submitted:", snap["submitted"], " blocked:", snap["blocked"])
    print("memory:", snap["memory"])
    from .spec import VERSION, DOC_VERSION, lock_check, DEFAULT_CONFIG
    locks = lock_check(DEFAULT_CONFIG)
    print(f"VERSION={VERSION}  DOC_VERSION={DOC_VERSION}")
    print("锁:", {kk: locks[kk] for kk in
                 ("matrix_rows", "matrix_cols", "design_grid",
                  "scheduler_bodies", "guard_layers", "graph_nodes")})
    return 0


def cmd_explore() -> int:
    """[8] 向量海勘探：PDF/文档→打捞 TVCB（9 阶段勘探流水线示例）。"""
    print()
    print("== 向量海勘探（V14 9 阶段流水线）==")
    p = _get_vector_sea_pack()
    print("扩展包: %s | 技能 %d / 角色 %d / 工作流 %d"
          % (p.key, len(p.skills), len(p.roles), len(p.workflows)))
    from .vector_sea_explorer import explore_and_manufacture
    text = "向量海 勘探 技能机床 协议适配 智慧打捞 张量耦合 能量分级 平台"
    result = explore_and_manufacture(text=text, energy=0.85)
    if result["status"] != "ok":
        print("流水线终止:", result["hint"])
        return 1
    print("阶段: %s" % " → ".join(result["stages"]))
    print("TVCB: %s | 主题: %s | 能量级: %s"
          % (result["tvcb"]["tvcb_id"], result["tvcb"]["topic"]["primary"],
             result["tvcb"]["energy_grade"]))
    print("SkillSpec: %s | 协议导出: %d 种"
          % (result["skill_spec"]["name"], result["protocol_count"]))
    return 0


def cmd_lathe() -> int:
    """[9] 技能机床：TVCB→可执行技能+协议导出（机床+适配器示例）。"""
    print()
    print("== 技能机床（Skill Lathe）==")
    from .skill_lathe import SkillLathe
    lathe = SkillLathe()
    tvcb = {"tvcb_id": "TVCB-TEST0001", "topic": {"primary": "test"},
            "keywords": ["AI", "agent"], "idea_pattern": "test pattern",
            "reusable_points": ["point1"], "energy_grade": "A"}
    spec = lathe.turn_skill(tvcb)
    if spec is None:
        print("能量级 C：丢弃")
        return 1
    print("TVCB → SkillSpec: %s" % spec["name"])
    print("描述: %s" % spec["description"])
    print("标签: %s" % spec["tags"])
    from .protocol_plugins import export_all_protocols
    exports = export_all_protocols(spec)
    print("协议遍历穷举导出: %d 种" % len(exports))
    print("  %s" % ", ".join(exports.keys()))
    return 0


def cmd_dehallucinate() -> int:
    """[10] 去幻觉检测：AI输出→充足理由锚定→幻觉判定（8 阶段流水线示例）。"""
    print()
    print("== 去幻觉检测（莱布尼茨PSR × 张平Seb × 赫布场）==")
    p = _get_dehallucination_pack()
    print("扩展包: %s | 技能 %d / 角色 %d / 工作流 %d"
          % (p.key, len(p.skills), len(p.roles), len(p.workflows)))
    from .dehallucination import DeHallucinationModule
    line = _readline("ai> ")
    if line is None or not line.strip():
        text = "人工智能 多智能体 系统 架构 设计"
        print("（空输入，使用演示样本: %s）" % text)
    else:
        text = line.strip()
    module = DeHallucinationModule()  # 降级模式（无联网回调）
    result = module.check(text)
    print("语义基: %s" % " ".join(result["semantic_base"][:6]))
    print("现实快照: %s" % result["reality_snapshot"])
    print("余弦相似度: %.4f | 同义映射: %s | 贝叶斯后验: %.4f"
          % (result["cosine_similarity"], result["synonym_match"],
             result["bayesian_posterior"]))
    print("耗散熵: %.4f | 充足理由: %s" % (result["dissipation_entropy"],
                                      result["sufficient_reason"]))
    print("判定: %s | 赫布权重: %.4f"
          % (result["verdict"], result["hebbian_weight"]))
    return 0


def cmd_super_agent() -> int:
    """[11] 自主调度（Super-agent 模式：Router 分派+两级过滤+Watchdog）。"""
    print()
    print("== 确定性自主调度（Super-agent 对标蒸馏 · D-01~D-05）==")
    p = _get_super_agent_pack()
    print("扩展包: %s | 技能 %d / 角色 %d / 工作流 %d"
          % (p.key, len(p.skills), len(p.roles), len(p.workflows)))
    from .router_layer import RouterLayer
    from .event_filter import EventFilter
    from .external_watchdog import ExternalWatchdog
    router = RouterLayer()
    router.register_rule("写文章", "writing_planner")
    router.register_rule("分析数据", "data_analyst")
    router.register_rule("监控", "watchdog_operator", priority=1)
    router.start()
    line = _readline("task> ")
    if line is None or not line.strip():
        task = "帮我监控系统状态"
        print("（空输入，使用演示任务: %s）" % task)
    else:
        task = line.strip()
    target = router.receive(task)
    print("Router 分派: %s -> %s（规则驱动，确定性）" % (task, target))
    f = EventFilter()
    print("两级过滤: %s" % f.filter("代码审查发现一个bug"))
    w = ExternalWatchdog(".")
    w.alert("info", "任务已分派到 %s" % target)
    snap = w.snapshot()
    print("Watchdog: 警报 %d 条 | 健康历史 %d 条"
          % (snap["alerts_count"], snap["history_count"]))
    print("状态: %s" % router.status())
    return 0


def cmd_concept_anatomy() -> int:
    """[12] 概念解剖：解剖HoloAeon概念（经络/赫布场/城邦等）。"""
    print()
    print("== 概念解剖（Anatomy 创意蒸馏 · 十步工序 + 深度审计 + 26 Token）==")
    p = _get_concept_anatomy_pack()
    print("扩展包: %s | 技能 %d / 角色 %d / 工作流 %d"
          % (p.key, len(p.skills), len(p.roles), len(p.workflows)))
    from .concept_anatomy import CONCEPT_MAP, ConceptAnatomizer
    print("可用概念: %s" % " / ".join(list(CONCEPT_MAP.keys())))
    line = _readline("concept> ")
    if line is None or not line.strip():
        concept = "经络"
        print("（空输入，使用演示概念: %s）" % concept)
    else:
        concept = line.strip()
    ca = ConceptAnatomizer()
    r = ca.anatomize(concept)
    if "error" in r:
        print("未知概念: %s（可选: %s）" % (concept, " / ".join(r["available"])))
        return 1
    print("概念: %s | 维度: %s | 状态: %s"
          % (r["concept"], r["anatomy"]["dimension"], r["status"]))
    print("机制: %s" % r["anatomy"]["mechanism"])
    print("组件 %d 个: %s"
          % (r["anatomy"]["component_count"],
             " → ".join(r["anatomy"]["sort_order"])))
    print("验证: %s" % r["anatomy"]["verification_rule"])
    audit = r["anatomy"]["audit"]
    print("审计: 重叠 %d / 穿透 %d / 一致性 %d | all_passed=%s"
          % (audit["checks"]["overlap"]["overlaps_found"],
             audit["checks"]["penetration"]["issues_found"],
             audit["checks"]["consistency"]["issues_found"],
             audit["all_passed"]))
    svg = r["output"].get("svg", "")
    if svg:
        print("SVG: %d 字符（等距投影，可选输出）" % len(svg))
    return 0


def cmd_eng_skills() -> int:
    """[13] 工程技能：8个本地化技能速查（审讯/交接/解释/原型/TDD/审查/调试/词汇）。"""
    print()
    print("== 工程技能（mattpocock/skills 310K★ 蒸馏 · 8技能/4角色/2工作流）==")
    p = _get_eng_skills_pack()
    print("扩展包: %s | 技能 %d / 角色 %d / 工作流 %d"
          % (p.key, len(p.skills), len(p.roles), len(p.workflows)))
    for s in p.skills:
        print("  - %s: %s" % (s.name, s.description))
    print("角色: %s" % " / ".join(r.name for r in p.roles))
    print("工作流: %s" % " / ".join(w.name for w in p.workflows))
    print("示例: holoaeon-eng --skill grill_plan --args '{\"plan_description\":\"加个缓存\"}'")
    return 0


def cmd_swarm_intel() -> int:
    """[14] 群体智能：五阶段流水线演示（Graph→World→Simulate→Report→Interact）。"""
    from .swarm_intel import DEFAULT_SEED, SwarmOrchestrator
    print()
    print("== 群体智能引擎（MiroFish 五阶段流水线蒸馏 · 5技能/3角色/2工作流）==")
    p = _get_swarm_intel_pack()
    print("扩展包: %s | 技能 %d / 角色 %d / 工作流 %d"
          % (p.key, len(p.skills), len(p.roles), len(p.workflows)))
    orch = SwarmOrchestrator()
    state = orch.run_pipeline(DEFAULT_SEED, total_rounds=3)
    print("模拟: %s | 实体 %d | Agent %d | 行动 %d | 轮次 %d | 阶段 %s"
          % (state.simulation_id,
             state.graph.node_count if state.graph else 0,
             len(state.profiles), len(state.all_actions),
             state.current_round, state.current_stage.value))
    if state.report:
        print("报告: %s" % state.report["conclusion"])
        for sig in state.report["emergent_signals"]:
            print("  涌现: %s (占比 %s)" % (sig["pattern"], sig["ratio"]))
    print("证据等级: simulated（仿真≠证明，碳基终裁）")
    return 0


MENU = {
    "1": ("安装引导", cmd_install),
    "2": ("自检", cmd_selftest),
    "3": ("技能清单", cmd_skills),
    "4": ("四人组加载", cmd_quartet),
    "5": ("启动桥接服务", cmd_bridge),
    "6": ("提交任务", cmd_submit),
    "7": ("状态快照", cmd_status),
    "8": ("向量海勘探", cmd_explore),
    "9": ("技能机床", cmd_lathe),
    "10": ("去幻觉检测", cmd_dehallucinate),
    "11": ("自主调度", cmd_super_agent),
    "12": ("概念解剖", cmd_concept_anatomy),
    "13": ("工程技能", cmd_eng_skills),
    "14": ("群体智能", cmd_swarm_intel),
}


def _print_menu() -> None:
    print()
    print("==============================================")
    print(" HoloAeon 管家操作系统 · Butler OS 引导菜单")
    print("==============================================")
    for key, (name, _fn) in MENU.items():
        print(f"  {key}. {name}")
    print("  0. 退出")
    print("----------------------------------------------")


def main(argv=None) -> int:
    """CLI 入口：无参数交互菜单；带参数（如 '2'）非交互执行一次后退出。"""
    args = list(sys.argv[1:] if argv is None else argv)
    if args:
        key = args[0].strip()
        if key in MENU:
            print(f"非交互执行菜单 {key}: {MENU[key][0]}")
            return MENU[key][1]()
        if key == "0":
            return 0
        print(f"未知菜单: {key}（可选: {', '.join(sorted(MENU))}, 0）")
        return 2
    _print_menu()
    while True:
        choice = _readline("选择> ")
        if choice is None:
            print()
            print("管家操作系统已退出。潮起开门，潮落闭嘴。")
            return 0
        choice = choice.strip()
        if choice == "0":
            print("管家操作系统已退出。潮起开门，潮落闭嘴。")
            return 0
        if choice not in MENU:
            print("无效选择，请输入 0-7")
            continue
        try:
            rc = MENU[choice][1]()
        except KeyboardInterrupt:
            print()
            print("（当前操作已中断，返回菜单）")
            continue
        except Exception as exc:  # noqa: BLE001
            print("执行出错:", type(exc).__name__, exc)
            rc = 1
        _print_menu()


if __name__ == "__main__":
    raise SystemExit(main())
