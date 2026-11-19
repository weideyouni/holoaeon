# -*- coding: utf-8 -*-
"""恒真判据常驻金哨 · A 口径静态扫描器（V84）

病的定义（A 口径，两方独立复核收敛）：
    一条比较的**结果能否因被测输入而改变**。不能改变、且语义上冒充「对输入的判据」= 病。
    V82（`quartet_director_pack` 的 `governable` / `P2×P3`）与
    V83（`topology_resonance_pack.quartet_tensor` 的 `sims["P2×P3"]`）治的就是这类。

静态只能判「字面」（B 口径），判不了「语义是否冒充判据」（A 口径）。
所以本模块的定位是：**把 B 口径命中全部摆到台面上**，用白名单登记账把 8 处正当用途
（常量不变式自检 / 配置常量分派 / 声明在位检查）逐条登记，剩下的「未登记命中」
= 需要人审的疑似 A 类，闸上判红。**它不是自动判定 A 类的机器，也不冒充。**

边界（诚实声明，写死在这里，回执同步）：
    · 只扫 `holoaeon/` 包；`scripts/` `tests/` 不入范围（测试里的常量断言是锁定用途）；
    · 函数**参数**、`for`/`with`/`except` 目标、**多次赋值**的变量一律不算常量
      （否则会把「默认值赋给参数后比较」误判成恒真——执行端 v1 曾 16 处误报）；
    · 链式比较按 `(left, op[0], cmp[0]) (cmp[0], op[1], cmp[1])…` 成对展开
      （否则 `0 <= x <= 1` 会拆错边——四人组 v1 曾 25 处误报）；
    · **不覆盖**：常量经函数返回值传递、跨模块导入、`getattr`/`dict.get`、字符串拼装
      等隐晦形态。静态可判定边界到此为止，不冒充全覆盖。
    · 纯 AST，零执行、零网络、零新依赖，py3.8 兼容。

封口密语：潮起开门，潮落闭嘴。
"""

import ast
import hashlib
import importlib
import io
import json
import os
import random
import re
import sys
import threading

TAUTOLOGY_SEAL = "潮起开门，潮落闭嘴"
ALLOWLIST_SCHEMA = "TAUTOLOGY-ALLOWLIST-v1"
ALLOWLIST_REL = "data/tautology_allowlist.json"
LINE_TOLERANCE = 5
PKG_DIRNAME = "holoaeon"


class _Unknown(object):
    """不可静态求值的哨兵（不用 None，避免与真实 None 混淆）。"""

    __slots__ = ()

    def __repr__(self):
        return "<unknown>"


UNKNOWN = _Unknown()

_ORDER_OPS = {
    ast.Eq: ("eq", lambda a, b: a == b),
    ast.NotEq: ("ne", lambda a, b: a != b),
    ast.Gt: ("gt", lambda a, b: a > b),
    ast.GtE: ("ge", lambda a, b: a >= b),
    ast.Lt: ("lt", lambda a, b: a < b),
    ast.LtE: ("le", lambda a, b: a <= b),
}


def _norm(text):
    """归一化：去空白与各类引号，供 expr 锚做子串匹配。"""
    return re.sub(r"[\s'\"\u2018\u2019\u201c\u201d]", "", text or "")


def _eval(node, env):
    """静态求值：字面量 / 单次赋值的常量名 / 常量 dict 下标 / 一元负 / 四则。"""
    if isinstance(node, ast.Constant):
        v = node.value
        if isinstance(v, (int, float, str, bool)):
            return v
        return UNKNOWN
    if isinstance(node, ast.Name):
        return env.get(node.id, UNKNOWN)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        v = _eval(node.operand, env)
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            return -v
        return UNKNOWN
    if isinstance(node, ast.BinOp):
        a, b = _eval(node.left, env), _eval(node.right, env)
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            try:
                if isinstance(node.op, ast.Add):
                    return a + b
                if isinstance(node.op, ast.Sub):
                    return a - b
                if isinstance(node.op, ast.Mult):
                    return a * b
                if isinstance(node.op, ast.Div) and b != 0:
                    return a / b
            except Exception:  # noqa: BLE001
                return UNKNOWN
        return UNKNOWN
    if isinstance(node, ast.Subscript):
        base = _eval(node.value, env)
        if isinstance(base, dict):
            sl = node.slice
            if hasattr(ast, "Index") and isinstance(sl, ast.Index):  # py3.8
                sl = sl.value
            key = _eval(sl, env)
            if isinstance(key, (int, float, str, bool)) and key in base:
                return base[key]
        return UNKNOWN
    return UNKNOWN


def _arg_names(fn):
    names = set()
    a = fn.args
    for dst in list(getattr(a, "posonlyargs", [])) + list(a.args) + list(a.kwonlyargs):
        names.add(dst.arg)
    if getattr(a, "vararg", None):
        names.add(a.vararg.arg)
    if getattr(a, "kwarg", None):
        names.add(a.kwarg.arg)
    return names


def _bound_names(body):
    """函数体内所有「被绑定过」的名字（出现次数用于剔除多次赋值者）。"""
    names = []

    def add(target):
        if isinstance(target, ast.Name):
            names.append(target.id)
        elif isinstance(target, (ast.Tuple, ast.List)):
            for e in target.elts:
                add(e)
        elif isinstance(target, ast.Starred):
            add(target.value)

    for n in ast.walk(ast.Module(body=body, type_ignores=[])):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                add(t)
        elif isinstance(n, (ast.AugAssign, ast.AnnAssign)):
            add(n.target)
        elif isinstance(n, (ast.For, ast.AsyncFor)):
            add(n.target)
        elif isinstance(n, ast.withitem):
            if n.optional_vars is not None:
                add(n.optional_vars)
        elif isinstance(n, ast.ExceptHandler) and n.name:
            names.append(n.name)
        elif isinstance(n, (ast.Global, ast.Nonlocal)):
            names.extend(n.names)
        elif isinstance(n, ast.comprehension):
            add(n.target)
        elif isinstance(n, ast.Delete):
            for t in n.targets:
                add(t)
    return names


def _const_env(body, seed):
    """只收「赋值恰好一次 + 无其他绑定 + 值可静态求值」的名字（含常量 dict）。"""
    counts = {}
    for nm in _bound_names(body):
        counts[nm] = counts.get(nm, 0) + 1
    env = dict(seed)
    for st in body:
        if not isinstance(st, ast.Assign) or len(st.targets) != 1:
            continue
        tgt = st.targets[0]
        if not isinstance(tgt, ast.Name):
            continue
        nm = tgt.id
        if counts.get(nm, 0) != 1:
            continue
        if isinstance(st.value, ast.Dict):
            d = {}
            ok = True
            for k, v in zip(st.value.keys, st.value.values):
                if k is None:
                    ok = False
                    break
                kv = _eval(k, env)
                vv = _eval(v, env)
                if kv is UNKNOWN or vv is UNKNOWN:
                    ok = False
                    break
                d[kv] = vv
            if ok:
                env[nm] = d
            continue
        v = _eval(st.value, env)
        if v is not UNKNOWN:
            env[nm] = v
    return env


def _classify(op, verdict):
    if isinstance(op, (ast.In, ast.NotIn)):
        return "membership_in_const"
    name = _ORDER_OPS.get(type(op), ("", None))[0]
    if name == "eq" and verdict:
        return "tautology_eq"
    if verdict:
        return "dead_always_true"
    if verdict is False:
        return "dead_always_false"
    return "opaque"


def _pairs(cmp_node, env):
    out = []
    left = cmp_node.left
    for op, right in zip(cmp_node.ops, cmp_node.comparators):
        lv, rv = _eval(left, env), _eval(right, env)
        hit = None
        if isinstance(op, (ast.In, ast.NotIn)):
            if isinstance(rv, (dict, str, list, tuple, set)) or isinstance(rv, type):
                verdict = None
                if not isinstance(rv, type):
                    try:
                        verdict = bool((lv in rv) if isinstance(op, ast.In) else (lv not in rv))
                    except Exception:  # noqa: BLE001
                        verdict = None
                if lv is not UNKNOWN:
                    hit = {"kind": "membership_in_const", "verdict": verdict,
                           "left": repr(lv), "op": type(op).__name__, "right": repr(rv)[:80]}
        elif lv is not UNKNOWN and rv is not UNKNOWN:
            fn = _ORDER_OPS.get(type(op))
            if fn is not None:
                verdict = None
                try:
                    verdict = bool(fn[1](lv, rv))
                except Exception:  # noqa: BLE001
                    verdict = None
                hit = {"kind": _classify(op, verdict), "verdict": verdict,
                       "left": repr(lv), "op": type(op).__name__, "right": repr(rv)}
        if hit is not None:
            out.append(hit)
        left = right
    return out


def scan_source(src, rel, seed=None):
    """扫一段源码，返回 hit 列表（rel 用于回填归属）。"""
    tree = ast.parse(src)
    hits = []
    mod_env = _const_env(tree.body, seed or {})
    for st in tree.body:
        if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        for node in ast.walk(st):
            if isinstance(node, ast.Compare):
                for h in _pairs(node, mod_env):
                    h.update({"file": rel, "line": node.lineno,
                              "expr": _line_of(src, node.lineno)})
                    hits.append(h)
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        env = dict(mod_env)
        f_env = _const_env(fn.body, env)
        for nm in _arg_names(fn):
            f_env.pop(nm, None)
        for node in ast.walk(fn):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node is not fn:
                continue
            if isinstance(node, ast.Compare):
                for h in _pairs(node, f_env):
                    h.update({"file": rel, "line": node.lineno,
                              "expr": _line_of(src, node.lineno)})
                    hits.append(h)
    return hits


_LINES = {}


def _line_of(src, lineno):
    key = id(src)
    lines = _LINES.get(key)
    if lines is None or lines[0] is not src:
        lines = (src, src.splitlines())
        _LINES[key] = lines
    try:
        return lines[1][lineno - 1].strip()
    except IndexError:
        return ""


def _root_repo():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def scan_root(path):
    """遍历一个包目录，返回 (hits, files_scanned, parse_errors)。"""
    hits, files, errors = [], 0, []
    for root, dirs, names in os.walk(path):
        dirs[:] = sorted(d for d in dirs if d != "__pycache__")
        for n in sorted(names):
            if not n.endswith(".py"):
                continue
            files += 1
            full = os.path.join(root, n)
            rel = os.path.relpath(full, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            rel = rel.replace("\\", "/")
            try:
                src = io.open(full, encoding="utf-8").read()
                hits.extend(scan_source(src, rel))
            except SyntaxError as exc:
                errors.append({"file": rel, "error": str(exc)[:120]})
    return hits, files, errors


# --------------------------------------------------------- 白名单
def canonical_digest(obj):
    body = {k: v for k, v in obj.items() if k != "self_digest" and not k.startswith("_")}
    blob = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def load_allowlist(repo_root):
    p = os.path.join(repo_root, ALLOWLIST_REL)
    if not os.path.exists(p):
        return {"schema": ALLOWLIST_SCHEMA, "entries": [], "self_digest": "",
                "_missing": True, "_path": p}
    with io.open(p, encoding="utf-8") as fh:
        data = json.load(fh)
    data["_missing"] = False
    data["_path"] = p
    return data


def _entry_anchors(entry):
    anchors = [a for a in (entry.get("anchors") or []) if a]
    if not anchors:
        raw = entry.get("expr") or ""
        anchors = [p.strip() for p in re.split(r"/|\band\b", raw) if p.strip()]
    return [_norm(a) for a in anchors]


def match_hit(hit, entries):
    """file 精确 + line ±容差 + expr 锚归一化子串。"""
    hf = _norm(hit["file"])
    hx = _norm(hit["expr"])
    for e in entries:
        if _norm(e.get("file", "")) != hf:
            continue
        try:
            line = int(e.get("line") or 0)
        except (TypeError, ValueError):
            line = 0
        if line and abs(line - int(hit["line"])) > LINE_TOLERANCE:
            continue
        anchors = _entry_anchors(e)
        if not anchors:
            continue
        if any(a and a in hx for a in anchors):
            return e
    return None


def _selfcheck():
    """扫描器自检：链式比较 / 参数 / for 目标 / 多次赋值 / 真恒真 / in。"""
    cases = [
        ("chain_no_false_positive",
         "def f(x):\n    return 0 <= x <= 1\n", 0),
        ("param_default_not_const",
         'def f(mode="stagnation_first"):\n    return mode == "stagnation_first"\n', 0),
        ("for_target_not_const",
         "def f():\n    for i in [1, 2]:\n        if i == 1:\n            return 1\n    return 0\n", 0),
        ("multi_assign_not_const",
         "def f():\n    x = 0\n    x = 1\n    return x == 1\n", 0),
        ("with_target_not_const",
         "def f(h):\n    with h() as fh:\n        return fh == 1\n", 0),
        ("genuine_tautology_detected",
         "CONST = 0.7\n\ndef f():\n    return CONST >= 0.7\n", 1),
        ("local_const_dict_detected",
         'def f():\n    sims = {"P2xP3": 0.7}\n    return sims["P2xP3"] >= 0.7\n', 1),
        ("membership_detected",
         'D = {"images": "x"}\n\ndef f():\n    return "images" in D\n', 1),
    ]
    out, fails = [], []
    for name, src, expect in cases:
        try:
            got = len(scan_source(src, "(selfcheck)", {}))
        except Exception as exc:  # noqa: BLE001
            out.append({"name": name, "expected": expect, "got": "ERR:%s" % exc})
            fails.append(name)
            continue
        out.append({"name": name, "expected": expect, "got": got})
        if got != expect:
            fails.append(name)
    return {"ok": not fails, "cases": out, "failures": fails}


# --------------------------------------------------------- V88 P1-B 第五类：activity_probe
# 扰动测活性（显式开关，默认关；纯标准库，固定种子，超时熔断）。
# 委托来源（跨仓零 import，只登记指针，不复制实现）：
#   repo : longaeon-rejuvenation-matrix @ ea4e2c1ec732e2b0cd6c4dcd2ced6a3d9b516196
#   file : longaeon/models/_guard.py  L99-L108  activity_check
#   思路 : 同一判据函数喂 base / perturbed 两组输入，输出不变 ⇒ 常数输出疑似（activity_suspect）。
ACTIVITY_SEED = 20261119
ACTIVITY_TIMEOUT = 5.0
ACTIVITY_TOLERANCE = 1e-9
ACTIVITY_CRITERION_RE = re.compile(
    r"(check|gate|verdict|judge|score|emerge|classify|governable)", re.I)


def _activity_rng():
    return random.Random(ACTIVITY_SEED)


def _activity_scalar(rng, perturbed):
    base = 0.5
    return round(base + rng.uniform(-0.2, 0.2), 6) if perturbed else base


def _run_with_timeout(fn, args, timeout):
    box = {}

    def _target():
        try:
            box["value"] = fn(*args)
        except Exception as exc:  # noqa: BLE001
            box["error"] = "%s: %s" % (type(exc).__name__, exc)

    th = threading.Thread(target=_target, daemon=True)
    th.start()
    th.join(timeout)
    if th.is_alive():
        return None, "activity_timeout"
    err = box.get("error")
    if err is not None:
        return None, err
    return box.get("value"), None


def _activity_equal(a, b, tolerance=ACTIVITY_TOLERANCE):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) \
            and not isinstance(a, bool) and not isinstance(b, bool):
        return abs(float(a) - float(b)) <= tolerance
    return repr(a) == repr(b)


def probe_callable(fn, base_args, perturbed_args, tolerance=ACTIVITY_TOLERANCE,
                   timeout=ACTIVITY_TIMEOUT):
    """扰动测活性：base 与 perturbed 输出相同 ⇒ suspect=True（待复核，非判定病）。"""
    base, b_err = _run_with_timeout(fn, base_args, timeout)
    if b_err:
        return {"suspect": None, "reason": "base_unverifiable:%s" % b_err}
    pert, p_err = _run_with_timeout(fn, perturbed_args, timeout)
    if p_err:
        return {"suspect": None, "reason": "perturbed_unverifiable:%s" % p_err}
    if _activity_equal(base, pert, tolerance):
        return {"suspect": True, "reason": "constant_output",
                "base": repr(base)[:80], "perturbed": repr(pert)[:80]}
    return {"suspect": False, "reason": "output_changes",
            "base": repr(base)[:80], "perturbed": repr(pert)[:80]}


def _iter_pack_criteria(pkg_dir):
    out = []
    packs = os.path.join(pkg_dir, "packs")
    if not os.path.isdir(packs):
        return out
    for fn_name in sorted(os.listdir(packs)):
        if not fn_name.endswith(".py") or fn_name.startswith("_"):
            continue
        full = os.path.join(packs, fn_name)
        rel = os.path.relpath(full, pkg_dir).replace("\\", "/")
        try:
            tree = ast.parse(io.open(full, encoding="utf-8").read())
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                    and ACTIVITY_CRITERION_RE.search(node.name):
                out.append((rel, node.name, node.lineno, len(node.args.args)))
    return out


def activity_probe(root=None, with_activity=False):
    """第五类探针：默认关闭；开启后对 packs/ 判据函数做扰动活性测试。

    命中标 `activity_suspect`（待复核，不是判定病）；不可执行/超时/参数不匹配记
    unverifiable，不冒充命中。固定种子 + 线程超时熔断。
    """
    pkg = root or os.path.join(_root_repo(), PKG_DIRNAME)
    if not with_activity:
        return {"enabled": False, "suspects": [], "probed": 0, "unverifiable": 0,
                "note": "默认纯静态零执行；--with-activity 才开扰动探针"
                        "（固定种子 %d，超时 %.1fs）" % (ACTIVITY_SEED, ACTIVITY_TIMEOUT)}
    rng = _activity_rng()
    suspects, probed, unverifiable = [], 0, 0
    for rel, name, lineno, argc in _iter_pack_criteria(pkg):
        mod_name = "holoaeon.packs." + os.path.splitext(os.path.basename(rel))[0]
        try:
            mod = importlib.import_module(mod_name)
            fn = getattr(mod, name, None)
            if fn is None or not callable(fn):
                continue
            base = [_activity_scalar(rng, False) for _ in range(argc)]
            pert = [_activity_scalar(rng, True) for _ in range(argc)]
            res = probe_callable(fn, base, pert)
            probed += 1
            if res["suspect"] is True:
                suspects.append({"file": rel, "line": lineno, "func": name, **res})
            elif res["suspect"] is None:
                unverifiable += 1
        except Exception as exc:  # noqa: BLE001
            unverifiable += 1
            suspects.append({"file": rel, "line": lineno, "func": name,
                             "suspect": None,
                             "reason": "import_error:%s" % type(exc).__name__})
    return {"enabled": True, "suspects": suspects, "probed": probed,
            "unverifiable": unverifiable, "seed": ACTIVITY_SEED,
            "timeout_s": ACTIVITY_TIMEOUT,
            "note": "activity_suspect 为待复核标记，不是判定为病；与未登记命中口径一致"}


def scan(root=None, allowlist_path=None, with_activity=False):
    """A 口径扫描（静态 B 口径检测 + 白名单登记 + 扫描器自检）。

    root 缺省 = 本仓 `holoaeon/` 包目录；allowlist 缺省 = <repo>/data/tautology_allowlist.json。
    ok = 无未登记命中 且 白名单无漂移/缺活性/摘要不符 且 扫描器自检通过。
    """
    repo_root = _root_repo()
    pkg = root or os.path.join(repo_root, PKG_DIRNAME)
    hits, files, errors = scan_root(pkg)
    al = load_allowlist(repo_root if allowlist_path is None else None) if allowlist_path is None \
        else _load_allowlist_path(allowlist_path)

    entries = al.get("entries") or []
    allowlisted, unregistered = [], []
    for h in hits:
        e = match_hit(h, entries)
        if e is None:
            unregistered.append(h)
        else:
            h = dict(h)
            h["entry"] = e.get("id")
            allowlisted.append(h)

    drift, liveness_missing = [], []
    for e in entries:
        eid = e.get("id")
        if not (e.get("liveness") or "").strip():
            liveness_missing.append(eid)
        cat = e.get("category")
        if cat not in ("invariant_selfcheck", "config_dispatch", "presence_check"):
            drift.append({"id": eid, "why": "category 不在三值枚举", "category": cat})
        if not any(h.get("entry") == eid for h in allowlisted):
            drift.append({"id": eid, "why": "条目在位但代码位未命中（过期登记或锚失效）"})

    exp_digest = al.get("self_digest") or ""
    act_digest = canonical_digest(al)
    digest_ok = bool(exp_digest) and exp_digest == act_digest

    sc = _selfcheck()
    ap = activity_probe(pkg, with_activity)
    ok = (not unregistered) and (not drift) and (not liveness_missing) \
        and digest_ok and sc["ok"] and not errors and not al.get("_missing")

    return {
        "ok": ok,
        "schema": ALLOWLIST_SCHEMA,
        "scope": "holoaeon/ 包（%d 文件）；scripts/ tests/ 不入范围；隐晦形态不覆盖" % files,
        "files_scanned": files,
        "hits_total": len(hits),
        "hits": hits,
        "allowlisted": allowlisted,
        "unregistered": unregistered,
        "allowlist_entries": len(entries),
        "drift": drift,
        "liveness_missing": liveness_missing,
        "digest": {"expected": exp_digest, "actual": act_digest, "ok": digest_ok},
        "allowlist_missing": bool(al.get("_missing")),
        "parse_errors": errors,
        "scanner_selfcheck": sc,
        "activity_probe": ap,
        "a_caliber_note": "静态检测只能判 B 口径（字面常量比较）；A 口径（是否冒充输入判据）"
                          "仍需人审。未登记命中 = 待复核/判红，不等于已判定为病。",
        "seal": TAUTOLOGY_SEAL,
    }


def _load_allowlist_path(path):
    if not os.path.exists(path):
        return {"schema": ALLOWLIST_SCHEMA, "entries": [], "self_digest": "",
                "_missing": True, "_path": path}
    with io.open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    data["_missing"] = False
    data["_path"] = path
    return data


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    out = ""
    with_activity = "--with-activity" in argv
    argv = [a for a in argv if a != "--with-activity"]
    if "--json" in argv:
        i = argv.index("--json")
        if i + 1 < len(argv):
            out = argv[i + 1]
    rep = scan(with_activity=with_activity)
    if out:
        d = os.path.dirname(os.path.abspath(out))
        if d and not os.path.isdir(d):
            os.makedirs(d)
        with io.open(out, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(rep, fh, ensure_ascii=False, indent=2, sort_keys=True)
            fh.write("\n")
    print("[%s] tautology_scan  hits=%d allowlisted=%d unregistered=%d drift=%d selfcheck=%s"
          % ("PASS" if rep["ok"] else "FAIL", rep["hits_total"],
             len(rep["allowlisted"]), len(rep["unregistered"]),
             len(rep["drift"]), "ok" if rep["scanner_selfcheck"]["ok"] else "FAIL"))
    if rep["unregistered"]:
        for h in rep["unregistered"][:12]:
            print("  UNREG %s:%s  %s  (%s %s)" % (h["file"], h["line"], h["kind"],
                                                  h["left"], h["op"]))
    for d in rep["drift"][:8]:
        print("  DRIFT %s  %s" % (d.get("id"), d.get("why")))
    return 0 if rep["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
