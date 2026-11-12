# -*- coding: utf-8 -*-
"""prehistory_contract.py —— V3 runtime 骨架契约包（V68 / PL-2）

定位：把「22 个 runtime 打包件长得像」这件事，从形容词变成**可失败的断言**。
只读 zip、只用 ast 解析源码，**不执行任何史前代码**。

三条实测事实（2026-11-12 本机，非策划案转述）：
1. 22 个 runtime zip 的共同 py 文件名 = 19 位（22/22 全覆盖）；
2. 共同函数签名合计 **65** 个（若只数 _base/threadbus/spec/heartbeat/main 是 21——那是抽样口径，不是全集）；
3. 每实例 assert 数 **不是 101**：min 0 / max 96 / 合计 1410，且
   `北京瑶医医院项目管理..._runtime_20261018.zip` 的 selftest.py 有 198 行、G1-G11 标记齐全，但 **assert = 0**。
   → 这正是「有自检形、无自检实」的空转样本，本契约把它登记为已知例外并单独判 FAIL 条件。
"""
import ast
import hashlib
import io
import json
import os
import re
import zipfile

CONTRACT_SCHEMA = "PREHISTORY-CONTRACT-v1"
V68_CONTRACT_VERSION = "1.0"

EXPECTED_INSTANCES = 22
EXPECTED_G_GROUPS = 11

ISOMORPHIC_FILES = (
    "__init__.py", "_base.py", "analytics.py", "clinical.py", "content.py",
    "cytoskeleton.py", "gen_data.py", "heartbeat_engine.py", "knowledge.py",
    "main.py", "ops.py", "research.py", "selftest.py", "semantic_bus.py",
    "skin.py", "skin_v6.py", "spec.py", "teaching.py", "threadbus.py",
)

# 交集函数签名实数（实测 65；按文件分布见 build_contract 的 shared_defs）
SHARED_DEFS_MIN = 65
ASSERT_TOTAL_MIN = 1400

# 已知「零断言」实例：不是漏检，是登记在案的缺陷样本
KNOWN_ZERO_ASSERT = (
    "北京瑶医医院项目管理1331x1331_SUPER-MAS-V3.0_runtime_20261018.zip",
)


def runtime_zips(root):
    """root 顶层的 *_runtime*.zip（按名排序，保证两次跑同序）。"""
    if not os.path.isdir(root):
        return []
    out = []
    for e in os.scandir(root):
        low = e.name.lower()
        if e.is_file(follow_symlinks=False) and low.endswith(".zip") and "_runtime" in low:
            out.append(e.path)
    return sorted(out, key=lambda p: os.path.basename(p))


def analyze_instance(path):
    """解析单个 zip：文件集、每文件 def 集、selftest 的 assert 数与 G 组数。不执行代码。"""
    rec = {
        "zip": os.path.basename(path),
        "entries": 0, "py": 0,
        "files": [], "missing_isomorphic": [],
        "defs": {}, "shared_def_count": 0,
        "asserts": 0, "g_groups": 0, "selftest_lines": 0,
        "parse_errors": [],
    }
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        rec["entries"] = len(names)
        py_names = [n for n in names if n.endswith(".py")]
        rec["py"] = len(py_names)
        bases = sorted({n.split("/")[-1] for n in py_names})
        rec["files"] = bases
        rec["missing_isomorphic"] = [f for f in ISOMORPHIC_FILES if f not in bases]
        for n in py_names:
            base = n.split("/")[-1]
            try:
                src = z.read(n).decode("utf-8", "replace")
                tree = ast.parse(src)
            except (SyntaxError, ValueError, KeyError):
                rec["parse_errors"].append(n)
                continue
            ds = sorted({node.name for node in ast.walk(tree)
                         if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))})
            rec["defs"][base] = ds
            if base == "selftest.py":
                rec["asserts"] = sum(1 for node in ast.walk(tree) if isinstance(node, ast.Assert))
                rec["selftest_lines"] = len(src.splitlines())
                rec["g_groups"] = len(set(re.findall(r"G(\d{1,2})", src)))
    return rec


def _shared_by_file(instances):
    """共同文件名上逐文件的 def 交集（只保留非空项）。"""
    shared_names = list(instances[0]["files"])
    for r in instances[1:]:
        shared_names = [f for f in shared_names if f in r["files"]]
    out = {}
    for fn in shared_names:
        s = set(instances[0]["defs"].get(fn, []))
        for r in instances[1:]:
            s &= set(r["defs"].get(fn, []))
        if s:
            out[fn] = sorted(s)
    return out


def build_contract(root):
    """建契约。返回 dict，含每实例差异位与交集签名。"""
    paths = runtime_zips(root)
    instances = [analyze_instance(p) for p in paths]
    shared = _shared_by_file(instances) if instances else {}
    total_shared = sum(len(v) for v in shared.values())
    zero = [r["zip"] for r in instances if r["asserts"] == 0]

    contract = {
        "schema": CONTRACT_SCHEMA,
        "version": V68_CONTRACT_VERSION,
        "criteria": {
            "expected_instances": EXPECTED_INSTANCES,
            "isomorphic_files": list(ISOMORPHIC_FILES),
            "shared_defs_min": SHARED_DEFS_MIN,
            "assert_total_min": ASSERT_TOTAL_MIN,
            "expected_g_groups": EXPECTED_G_GROUPS,
            "known_zero_assert": list(KNOWN_ZERO_ASSERT),
            "fingerprint": "content sha256[:16] per zip",
        },
        "summary": {
            "instances": len(instances),
            "entries": sum(r["entries"] for r in instances),
            "py": sum(r["py"] for r in instances),
            "shared_files": len(shared),
            "shared_defs_total": total_shared,
            "assert_min": min([r["asserts"] for r in instances]) if instances else 0,
            "assert_max": max([r["asserts"] for r in instances]) if instances else 0,
            "assert_sum": sum(r["asserts"] for r in instances),
            "zero_assert_instances": zero,
            "unknown_zero_assert": [z for z in zero if z not in KNOWN_ZERO_ASSERT],
        },
        "shared_defs": shared,
        "instances": instances,
        "package_sha256": "",
    }
    contract["package_sha256"] = digest(contract)
    return contract


def digest(contract):
    payload = {"schema": contract["schema"], "criteria": contract["criteria"],
               "summary": contract["summary"], "shared_defs": contract["shared_defs"],
               "instances": contract["instances"]}
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def zip_fingerprint(path):
    h = hashlib.sha256()
    with io.open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def verify_contract(contract, root=None):
    """可失败判据。返回 (ok, problems)。

    只要出现「新增的零断言实例」「缺 19 位骨架文件」「交集签名少于 65」任一项即 FAIL。
    """
    problems = []
    if contract.get("schema") != CONTRACT_SCHEMA:
        problems.append("schema mismatch")

    s = contract.get("summary") or {}
    if s.get("instances") != EXPECTED_INSTANCES:
        problems.append("instances %s != %d" % (s.get("instances"), EXPECTED_INSTANCES))

    unknown_zero = s.get("unknown_zero_assert") or []
    if unknown_zero:
        problems.append("new zero-assert instance(s) not registered: %s" % unknown_zero)

    if s.get("shared_defs_total", 0) < SHARED_DEFS_MIN:
        problems.append("shared defs %s < %d" % (s.get("shared_defs_total"), SHARED_DEFS_MIN))

    if s.get("assert_sum", 0) < ASSERT_TOTAL_MIN:
        problems.append("assert sum %s < %d" % (s.get("assert_sum"), ASSERT_TOTAL_MIN))

    for r in contract.get("instances") or []:
        if r.get("missing_isomorphic"):
            problems.append("%s missing isomorphic files: %s" % (r["zip"], r["missing_isomorphic"]))
        if r.get("parse_errors"):
            problems.append("%s parse errors: %s" % (r["zip"], r["parse_errors"]))

    if root:
        for p in runtime_zips(root):
            rec = next((r for r in contract.get("instances") or []
                        if r["zip"] == os.path.basename(p)), None)
            if rec is None:
                problems.append("zip not in contract: %s" % os.path.basename(p))

    if contract.get("package_sha256") != digest(contract):
        problems.append("package_sha256 mismatch (contract edited after build)")

    return (not problems), problems
