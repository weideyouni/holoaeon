# -*- coding: utf-8 -*-
"""install_check — 机构端安装自检脚本（V48，工程师手册配套）
跑法：python scripts/install_check.py
用途：机构端工程师安装完成后一键自检——环境/依赖/核心模块/关键能力
冒烟/网络口径，输出确定性清单（全 PASS 才算装好）。
零依赖纯标准库。封口密语：潮起开门，潮落闭嘴。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SEAL = "潮起开门，潮落闭嘴"

CHECKS = []


def check(name):
    def deco(fn):
        CHECKS.append((name, fn))
        return fn
    return deco


@check("Python 版本 >= 3.10")
def c_python():
    ok = sys.version_info >= (3, 10)
    return ok, sys.version.split()[0]


@check("零第三方依赖（包内 import 扫描）")
def c_deps():
    import ast
    import pathlib
    std = set(sys.stdlib_module_names)
    bad = []
    pkg = pathlib.Path(os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "holoaeon"))
    if not pkg.is_dir():
        return False, "holoaeon/ 包未找到"
    for py in pkg.rglob("*.py"):
        try:
            tree = ast.parse(py.read_text(encoding="utf-8"))
        except (SyntaxError, OSError):
            bad.append("%s: parse error" % py.name)
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    root = a.name.split(".")[0]
                    if root not in std and root != "holoaeon":
                        bad.append("%s: %s" % (py.name, a.name))
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    root = node.module.split(".")[0]
                    if root not in std and root != "holoaeon" \
                            and node.level == 0:
                        bad.append("%s: from %s" % (py.name, node.module))
    return not bad, "第三方 import 0 处" if not bad else "; ".join(bad[:3])


@check("核心模块 import（抽样 8 件）")
def c_imports():
    mods = ("kernel", "guard", "bus", "graph", "hypervector",
            "phc_chronic_engine", "pharma_gate", "deploy_gate")
    miss = []
    for m in mods:
        try:
            __import__("holoaeon." + m)
        except Exception as e:  # noqa: BLE001
            miss.append("%s(%s)" % (m, e))
    return not miss, "8/8 就绪" if not miss else "; ".join(miss)


@check("向量库冒烟（建3条+检索1次）")
def c_vector():
    from holoaeon.deploy_gate import VectorStore
    vs = VectorStore(dim=256)
    vs.add("k1", "高血压患者应定期测量血压")
    vs.add("k2", "糖尿病饮食指导与血糖监测")
    vs.add("k3", "慢阻肺病呼吸训练方法")
    r = vs.search("血压", top_k=1)
    return r["hits"][0]["id"] == "k1", "latency=%sms" % r["latency_ms"]


@check("网络二极管口径（出站结构性 BLOCK）")
def c_diode():
    import importlib.util
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    spec = importlib.util.spec_from_file_location(
        "site_gateway", os.path.join(here, "bridges", "site_gateway.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    v = mod.NetDiode.outbound("任何请求")["verdict"]
    return v == "BLOCK", "outbound=%s（白名单空集）" % v


@check("药品闸门冒烟（登记表查表+零剂量）")
def c_pharma():
    from holoaeon import pharma_gate as pg
    reg = pg.build_default_registry()
    r = reg.lookup("二甲双胍片（示例）")
    dose_reject = not pg.validate_entry(
        dict(pg.SAMPLE_ENTRIES[0], dose="x"))["ok"]
    return r["found"] and dose_reject, "查表OK+零剂量拒收OK"


@check("危险度打分冒烟（规则引用可复算）")
def c_risk():
    from holoaeon.phc_chronic_engine import risk_score
    r = risk_score({"sbp": 160, "smoker": True})
    return "R02" in r["rule_refs"] and "R09" in r["rule_refs"], \
        "score=%s grade=%s" % (r["score"], r["grade"])


def main():
    results = []
    all_ok = True
    for name, fn in CHECKS:
        try:
            ok, detail = fn()
        except Exception as e:  # noqa: BLE001
            ok, detail = False, "异常: %s" % e
        all_ok = all_ok and ok
        results.append({"check": name, "ok": ok, "detail": str(detail)})
        print("[%s] %s — %s" % ("PASS" if ok else "FAIL", name, detail))
    print("-" * 40)
    print("总结论: %s（%d/%d 项通过）%s"
          % ("安装就绪" if all_ok else "存在问题",
             sum(1 for r in results if r["ok"]), len(results), SEAL))
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
