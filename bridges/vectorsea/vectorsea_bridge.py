# -*- coding: utf-8 -*-
"""
HoloAeon × 向量海 技能桥接（侧车，主核只读）
================================================================================
唯一ID：SG-VECTORSEA-HOLOAEON-BRIDGE-V1.0，封存密令：潮起开门 / 潮落闭嘴。

把向量海技能全集（.user_skills 挂载点，1161 目录）注册为 HoloAeon 可发现、
可调用的技能，遵循四条军规：
  主核只读：不触碰 holoaeon/ 核心包，仅以 bridges/ 侧车增量挂载；
  增量旁挂：三层结构（SKILL.md + tools/ + data/），catalog.json 即 data 层；
  证据先于声明：每个技能给出确定性回执；工具未过静态红线扫描一律 execution=pending；
  同步收尾：入库后由上层流程同步向量海（飞书入口 + 分发包 + SHA 回读）。

能力模型：
  · 文档型技能（无 tools/）：确定性函数返回 SKILL.md 全文 + 元数据（离线读取）。
  · 工具型技能（含 tools/ 或根目录脚本）：静态红线扫描（纯标准库 / 无网络 /
    无进程派生 / 无 eval-exec / 无系统调用）通过才标 verified，否则 pending。
红线：零网络、零密钥、零遥测、不执行未验证工具、不替用户决策。
"""
from __future__ import annotations

import ast
import json
import os
import sys
from typing import Any, Callable, Dict, List, Optional

# ---------------------------------------------------------------- 常量
DEFAULT_ROOTS = [
    r"C:\Users\Administrator\AppData\Local\DoubaoWork\User Data\Default\.doubaowork\agent_mode\workspace\.user_skills",
    r"F:\doubaowork\.user_skills",
]
CATALOG_NAME = "catalog.json"
BRIDGE_ID = "SG-VECTORSEA-HOLOAEON-BRIDGE-V1.0"
PASS = "verified"
PEND = "pending"

# 静态红线：命中即工具不可验证（pending），不提供执行包装
_NET_IMPORTS = {
    "socket", "http.client", "urllib", "requests", "httpx", "aiohttp",
    "ssl", "ftplib", "smtplib", "telnetlib", "xmlrpc.client", "asyncio",
}
_PROC_IMPORTS = {"subprocess", "os.system", "os.popen", "pty", "pexpect", "ctypes"}
_DANGER_CALLS = {"eval", "exec", "os.system", "os.popen", "input"}


def load_catalog(path: Optional[str] = None) -> dict:
    """读取技能目录快照（data 层）。缺失时返回空结构。"""
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), CATALOG_NAME)
    if not os.path.isfile(path):
        return {"stats": {"total_dirs": 0}, "entries": []}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def resolve_skill_dir(dirname: str, roots: Optional[List[str]] = None) -> Optional[str]:
    """按目录名在候选挂载点中定位技能目录（确定性，按 roots 顺序）。"""
    for r in (roots or DEFAULT_ROOTS):
        p = os.path.join(r, dirname)
        if os.path.isdir(p):
            return p
    return None


def check_tool_static(path: str) -> Dict[str, Any]:
    """对单个工具脚本做静态红线扫描（纯标准库 / 无网络 / 无进程派生）。
    返回 {"ok": bool, "reasons": [..], "stdlib_only": bool, "py_only": bool}。"""
    ext = os.path.splitext(path)[1].lower()
    if ext != ".py":
        return {"ok": False, "reasons": [f"非 Python 脚本（{ext or '无扩展名'}），未验证"],
                "stdlib_only": False, "py_only": False}
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            src = f.read()
    except OSError as e:
        return {"ok": False, "reasons": [f"读取失败: {e}"], "stdlib_only": False, "py_only": True}
    try:
        tree = ast.parse(src, filename=path)
    except SyntaxError as e:
        return {"ok": False, "reasons": [f"语法错误: {e}"], "stdlib_only": False, "py_only": True}
    reasons: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                top = a.name.split(".")[0]
                if a.name in _NET_IMPORTS or top in _NET_IMPORTS:
                    reasons.append(f"网络 import: {a.name}")
                if a.name in _PROC_IMPORTS or top in _PROC_IMPORTS:
                    reasons.append(f"进程/系统 import: {a.name}")
                if a.name not in sys.stdlib_module_names and top not in sys.stdlib_module_names:
                    reasons.append(f"非标准库 import: {a.name}")
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            top = mod.split(".")[0]
            if mod in _NET_IMPORTS or top in _NET_IMPORTS:
                reasons.append(f"网络 import: {mod}")
            if mod in _PROC_IMPORTS or top in _PROC_IMPORTS:
                reasons.append(f"进程/系统 import: {mod}")
            if mod and mod not in sys.stdlib_module_names and top not in sys.stdlib_module_names:
                reasons.append(f"非标准库 import: {mod}")
        elif isinstance(node, ast.Call):
            fname = ""
            if isinstance(node.func, ast.Name):
                fname = node.func.id
            elif isinstance(node.func, ast.Attribute):
                fname = f"{node.func.value.id}.{node.func.attr}" \
                    if isinstance(node.func.value, ast.Name) else ""
            if fname in _DANGER_CALLS:
                reasons.append(f"危险调用: {fname}")
    return {"ok": not reasons, "reasons": reasons, "stdlib_only": not reasons,
            "py_only": True}


def _preflight_tools(entries: List[dict], roots: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
    """对全部技能做静态红线扫描（仅工具型技能参与 verified/pending 判定），
    文档型技能标注 mode=doc（不参与工具预检）。产出 dir -> 检查结果。"""
    result: Dict[str, Dict[str, Any]] = {}
    for e in entries:
        dirname = e.get("dir", "")
        files = e.get("tool_files", [])
        if not files:
            result[dirname] = {"status": "doc", "reasons": []}
            continue
        ok_all, reasons_all = True, []
        for tf in files:
            p = resolve_skill_dir(dirname, roots)
            full = os.path.join(p, tf) if p else None
            if not full or not os.path.isfile(full):
                ok_all, reasons_all = False, reasons_all + [f"工具文件缺失: {tf}"]
                continue
            chk = check_tool_static(full)
            if not chk["ok"]:
                ok_all = False
                reasons_all += [f"{tf}: {';'.join(chk['reasons'])}"]
        result[dirname] = {"status": PASS if ok_all else PEND,
                           "reasons": reasons_all if not ok_all else []}
    return result


def _make_fn(entry: dict, roots: Optional[List[str]], preflight: Dict[str, Dict[str, Any]]) -> Callable:
    """为单个技能构造确定性调用函数：返回元数据 + SKILL.md 全文 + 执行状态。"""
    dirname = entry["dir"]
    name = entry.get("name")
    desc = entry.get("description") or ""

    def fn(task: str = "") -> Dict[str, Any]:
        path = resolve_skill_dir(dirname, roots)
        content = ""
        if path:
            sm = os.path.join(path, "SKILL.md")
            if os.path.isfile(sm):
                with open(sm, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
        pf = preflight.get(dirname, {"status": "doc", "reasons": []})
        is_tool = bool(entry.get("has_tools"))
        if not is_tool:
            note = "文档型技能：确定性离线读取（SKILL.md 全文），无执行包装"
        elif pf["status"] == PASS:
            note = "工具已过静态红线扫描（纯标准库/无网络/无进程派生），可在本地人工复核后执行"
        else:
            note = "工具未过静态红线扫描，不提供执行包装（执行状态 pending，理由见 execution_reasons）"
        return {
            "name": name,
            "description": desc,
            "source_dir": dirname,
            "resolved_path": path,
            "layers": {
                "skill_md": entry.get("skill_md", False),
                "has_tools": entry.get("has_tools", False),
                "has_data": entry.get("has_data", False),
                "has_references": entry.get("has_references", False),
            },
            "tool_files": entry.get("tool_files", []),
            "mode": "tool" if is_tool else "doc",
            "execution": pf["status"],
            "execution_reasons": pf["reasons"],
            "requested_task": task or None,
            "content": content,
            "note": note,
        }

    return fn


def register_all(kernel: Any, catalog: Optional[dict] = None,
                 roots: Optional[List[str]] = None) -> Dict[str, Any]:
    """把向量海技能全集注册进 HoloAeon Kernel（侧车；与内置技能同名者跳过并留痕）。"""
    cat = catalog if catalog is not None else load_catalog()
    entries = cat.get("entries", [])
    preflight = _preflight_tools(entries, roots)
    registered, skipped_dup, skipped_no_name, tool_count = [], [], [], 0
    for e in entries:
        name = e.get("name")
        if not name:
            skipped_no_name.append(e.get("dir", "?"))
            continue
        if kernel.skills.has(name):
            skipped_dup.append(name)
            continue
        desc = (e.get("description") or "")[:2000]
        kernel.skills.register_fn(name, _make_fn(e, roots, preflight),
                                  description=desc,
                                  tags=["vectorsea", "bridge"])
        registered.append(name)
        if e.get("has_tools"):
            tool_count += 1
    return {
        "bridge_id": BRIDGE_ID,
        "registered": registered,
        "registered_count": len(registered),
        "skipped_duplicate_builtin": skipped_dup,
        "skipped_duplicate_count": len(skipped_dup),
        "skipped_no_name": skipped_no_name,
        "skipped_no_name_count": len(skipped_no_name),
        "tool_skill_count": tool_count,
        "mode": "sidecar",
    }


def selftest(catalog: Optional[dict] = None, roots: Optional[List[str]] = None) -> Dict[str, Any]:
    """实测回执：扫描数 / 可注册数 / 工具预检结果 / 注册演示 / 匹配演示。"""
    cat = catalog if catalog is not None else load_catalog()
    entries = cat.get("entries", [])
    stats = cat.get("stats", {})
    preflight = _preflight_tools(entries, roots)
    tool_status = {"verified": 0, "pending": 0, "verified_names": [], "pending_names": []}
    for e in entries:
        if not e.get("has_tools"):
            continue
        st = preflight.get(e["dir"], {}).get("status", "pending")
        if st == PASS:
            tool_status["verified"] += 1
            tool_status["verified_names"].append(e["dir"])
        else:
            tool_status["pending"] += 1
            tool_status["pending_names"].append(e["dir"])
    # 内置核注册演示：导入 Kernel 并注册全部（不触碰核心包）
    from holoaeon import Kernel
    k = Kernel()
    reg = register_all(k, cat, roots)
    v = k.skills.verify()
    # 匹配演示（确定性）：取三个典型查询
    demos = []
    for q in ["帮我做一次数据统计", "写一份商业计划书", "中医康复融合"]:
        m = k.skills.match(q, k=2)
        demos.append({"query": q, "top_matches": [{"name": n, "score": s} for n, s in m]})
    doc_count = stats.get("with_name", 0) - reg["tool_skill_count"]
    return {
        "bridge_id": BRIDGE_ID,
        "catalog_total_dirs": stats.get("total_dirs", 0),
        "catalog_with_skill_md": stats.get("with_skill_md", 0),
        "catalog_with_name": stats.get("with_name", 0),
        "registerable": reg["registered_count"],
        "skipped_duplicate_builtin": reg["skipped_duplicate_count"],
        "skipped_no_name": reg["skipped_no_name_count"],
        "doc_skill_count": doc_count,
        "tool_skills_total": reg["tool_skill_count"],
        "tool_preflight": tool_status,
        "registry_verify": {"count": v["count"], "no_duplicates": v["no_duplicates"]},
        "match_demos": demos,
        "sample_skill": (reg["registered"][:3] if reg["registered"] else []),
        "mode": "sidecar (main-core untouched)",
    }


if __name__ == "__main__":
    # 直接运行：输出 selftest 回执（证据先于声明）
    print(json.dumps(selftest(), ensure_ascii=False, indent=1))
