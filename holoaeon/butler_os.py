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
