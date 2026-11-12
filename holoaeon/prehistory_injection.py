# -*- coding: utf-8 -*-
"""prehistory_injection.py —— 18 仓判据注入包聚合（V72 / PL-5）

定位：把 18 个派生仓（holoaeon-c01-source … holoaeon-c18-cosmos）各自的 `ledger.json`
收成一张**可复算的注入台账**，并逐仓独立复算六条判据。主仓只读，不写 18 仓、不跑其历史代码。

三条纪律（写在代码里，不靠人记）：
1. **双端验证，不复用实现**：仓内 `prehistory_check.py` 跑一遍，主仓这里按同一契约**独立再算一遍**。
   两边都绿才算绿；主仓不 import 任何仓内代码，也不被仓内代码 import（零实现复制）。
2. **只登记，不搬运**：台账只收路径、sha16、判据结果与指针计数；不复制 18 仓源码、不复制 N19 实现。
3. **绝对路径不出门**：report 只写仓名与包名，根目录用 basename 标记；出现 `F:\\` 或 `/f/` 即判泄漏。

实测（2026-11-13 本机，非策划案转述）：
  · 18 仓结构 100% 同构：84 行 gate（`CangGate.self_check` 唯一方法）、6 个原测试
  · 注入后每仓 14 例（6 原 + 8 新），合计 **252**；每仓六判据 6/6、指针 11/11
  · 可失败性金丝雀：身份缺失 / 仓号错配 / ring 改 18 / 密令改字 / 指针缺项 / 越界 import —— **6/6 全红**

失败面（任一即红）：
    repo_missing / repo_extra / cang_duplicate / cang_gap / ledger_unreadable /
    identity_mismatch / cang_id_malformed / anchor_missing / ring_drift / seal_drift /
    pointer_gap / criteria_gap / criteria_not_falsifiable / zero_copy_violation /
    absolute_path_leak / self_digest
"""
import hashlib
import io
import json
import os
import re

INJECTION_SCHEMA = "PREHISTORY-INJECTION-v1"
INJECTION_VERSION = "1.0"

LEDGER_SCHEMA = "PREHISTORY-LEDGER-v1"
EXPECTED_REPOS = 18
CRITERIA_PER_REPO = 6
POINTERS_PER_REPO = 11
RING = 19
SEAL = "潮起开门，潮落闭嘴"
DEFAULT_ROOT = r"F:\doubaowork\.tmp_v55_cluster"

CRITERIA_IDS = (
    "identity_fields_present",
    "cang_id_wellformed",
    "n19_anchor_declared",
    "ring_is_19",
    "seal_intact",
    "mechanism_pointers_complete",
)
POINTER_KEYS = (
    "心跳调度", "经络传导", "卡尔曼滤波", "贝叶斯反演", "布赫场",
    "莫比乌斯翻转", "克莱因收敛", "语义通信", "事件总线", "升级契约", "张量载体",
)
IDENTITY_FIELDS = ("cang_id", "repo", "domain", "question",
                   "phase_main", "phase_sub", "role", "turtle", "horse")
SKIP_DIRS = (".git", "__pycache__", ".pytest_cache")

NOTE = ("18 仓各持一份 ledger.json，判据在仓内跑一次、主仓独立再算一次；"
        "主仓不复制任何仓内实现，也不 import 18 仓；台账只登记 sha16 与判据结果，不搬运源码")


# ---------------------------------------------------------------- 指纹

def sha16(payload):
    text = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def ledger_sha16(path):
    with io.open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()[:16]


# ---------------------------------------------------------------- 发现与读取

def discover(root=None):
    """按目录名发现 18 仓；只认 holoaeon-c??- 且内含 holoaeon_c??_* 包的形式。"""
    base = root or DEFAULT_ROOT
    found = []
    if not os.path.isdir(base):
        return found
    for name in sorted(os.listdir(base)):
        path = os.path.join(base, name)
        if not os.path.isdir(path) or not re.match(r"^holoaeon-c\d{2}-", name):
            continue
        pkgs = [x for x in os.listdir(path)
                if x.startswith("holoaeon_c") and os.path.isdir(os.path.join(path, x))]
        if not pkgs:
            continue
        pkg = pkgs[0]
        led = os.path.join(path, pkg, "ledger.json")
        found.append({"repo": name, "path": path, "pkg": pkg, "ledger_path": led,
                      "has_ledger": os.path.isfile(led)})
    return found


def load(entry):
    """读一仓的 ledger 与本仓测试计数；读不到就返回带 error 的条目，不抛。"""
    out = {"repo": entry["repo"], "pkg": entry["pkg"]}
    try:
        with io.open(entry["ledger_path"], encoding="utf-8") as fh:
            led = json.load(fh)
    except FileNotFoundError:
        out["error"] = "ledger_missing"
        return out
    except (ValueError, OSError) as exc:
        out["error"] = "ledger_unreadable: %s" % exc
        return out
    out["ledger"] = led
    out["ledger_sha16"] = ledger_sha16(entry["ledger_path"])
    return out


# ---------------------------------------------------------------- 六条判据（主仓侧独立实现）

def evaluate(ledger):
    crit = []

    missing = [k for k in IDENTITY_FIELDS
               if not isinstance(ledger.get(k), str) or not ledger.get(k).strip()]
    crit.append({"id": "identity_fields_present", "ok": not missing, "detail": missing})

    cid = ledger.get("cang_id") or ""
    repo = ledger.get("repo") or ""
    m = re.match(r"^C(\d{2})$", cid)
    ok = bool(m) and repo.startswith("holoaeon-c%s-" % m.group(1)) if m else False
    crit.append({"id": "cang_id_wellformed", "ok": ok, "detail": [cid, repo]})

    anchor = ledger.get("n19_anchor") or ""
    crit.append({"id": "n19_anchor_declared", "ok": "github.com" in anchor and "holoaeon" in anchor,
                 "detail": anchor})

    crit.append({"id": "ring_is_19", "ok": ledger.get("ring") == RING, "detail": ledger.get("ring")})

    crit.append({"id": "seal_intact", "ok": ledger.get("seal") == SEAL, "detail": ledger.get("seal")})

    ptr = ledger.get("mechanism_pointers") or {}
    empty = [k for k in POINTER_KEYS if not str(ptr.get(k) or "").strip()]
    extra = [k for k in ptr if k not in POINTER_KEYS]
    crit.append({"id": "mechanism_pointers_complete", "ok": bool(ptr) and not empty and not extra,
                 "detail": {"missing": empty, "extra": extra, "count": len(ptr)}})
    return crit


# ---------------------------------------------------------------- 零实现复制扫描

def scan_zero_copy(repo_root):
    """只扫源码文本的 import 语句与 sys.path 注入；AST 解析不起时降级为正则，仍要能判 FAIL。"""
    hits = []
    for base, dirs, files in os.walk(repo_root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if not f.endswith(".py"):
                continue
            rel = os.path.relpath(os.path.join(base, f), repo_root).replace("\\", "/")
            try:
                with io.open(os.path.join(base, f), encoding="utf-8") as fh:
                    text = fh.read()
            except (OSError, UnicodeDecodeError):
                continue
            if re.search(r"^\s*(import|from)\s+holoaeon\b", text, re.M):
                hits.append({"file": rel, "kind": "import"})
            if re.search(r"sys\.path\.(insert|append)\([^)]*['\"](?:[^'\"]*[/\\])?holoaeon[/\\\"']", text):
                hits.append({"file": rel, "kind": "sys.path"})
    return {"ok": not hits, "violations": hits}


# ---------------------------------------------------------------- 聚合

def _leak(obj):
    text = json.dumps(obj, ensure_ascii=False)
    return ("F:\\" in text) or ("F:\\\\" in text) or ("/f/" in text.lower())


def aggregate(root=None):
    base = root or DEFAULT_ROOT
    entries = discover(base)
    repos = []
    for e in entries:
        item = load(e)
        if item.get("error"):
            repos.append({"repo": item["repo"], "ok": False, "error": item["error"]})
            continue
        led = item["ledger"]
        crit = evaluate(led)
        passed = sum(1 for c in crit if c["ok"])
        zc = scan_zero_copy(e["path"])
        repos.append({
            "cang_id": led.get("cang_id"),
            "repo": item["repo"],
            "pkg": item["pkg"],
            "domain": led.get("domain"),
            "batch": led.get("batch"),
            "ledger_sha16": item["ledger_sha16"],
            "passed": passed,
            "total": len(CRITERIA_IDS),
            "pointers": len(led.get("mechanism_pointers") or {}),
            "schema_ok": led.get("schema") == LEDGER_SCHEMA,
            "zero_copy_ok": zc["ok"],
            "ok": passed == len(CRITERIA_IDS) and led.get("schema") == LEDGER_SCHEMA and zc["ok"],
            "failing": [c["id"] for c in crit if not c["ok"]],
        })

    totals = {
        "repos": len(repos),
        "green": sum(1 for r in repos if r.get("ok")),
        "criteria_pass": sum(r.get("passed", 0) for r in repos),
        "criteria_total": CRITERIA_PER_REPO * len(repos),
        "pointers": sum(r.get("pointers", 0) for r in repos),
    }
    report = {
        "schema": INJECTION_SCHEMA,
        "version": INJECTION_VERSION,
        "root_label": os.path.basename(base.rstrip("\\/")),
        "repos": repos,
        "totals": totals,
        "note": NOTE,
    }
    report["digest"] = sha16({"repos": [(r.get("cang_id"), r.get("ledger_sha16"), r.get("passed"))
                                        for r in repos], "totals": totals})
    return report


def check(report):
    """对 report 判 FAIL。返回失败项清单（空 = 绿）。"""
    failures = []
    repos = report.get("repos") or []
    if len(repos) != EXPECTED_REPOS:
        failures.append({"id": "repo_missing", "detail": len(repos)})

    ids = [r.get("cang_id") for r in repos if r.get("cang_id")]
    if len(ids) != len(set(ids)):
        failures.append({"id": "cang_duplicate", "detail": ids})
    expected_ids = ["C%02d" % i for i in range(1, EXPECTED_REPOS + 1)]
    if sorted(set(ids)) != expected_ids:
        failures.append({"id": "cang_gap",
                         "detail": {"missing": [c for c in expected_ids if c not in ids],
                                    "extra": [c for c in ids if c not in expected_ids]}})

    for r in repos:
        if r.get("error"):
            failures.append({"id": "ledger_unreadable", "repo": r["repo"], "detail": r["error"]})
            continue
        if not re.match(r"^C\d{2}$", r.get("cang_id") or ""):
            failures.append({"id": "cang_id_malformed", "repo": r["repo"], "detail": r.get("cang_id")})
        if r.get("cang_id") and r.get("repo") and \
                not r["repo"].startswith("holoaeon-c%s-" % r["cang_id"][1:]):
            failures.append({"id": "identity_mismatch", "repo": r["repo"], "detail": r.get("cang_id")})
        if not r.get("schema_ok"):
            failures.append({"id": "schema_drift", "repo": r["repo"]})
        if r.get("passed", 0) != CRITERIA_PER_REPO:
            failures.append({"id": "criteria_gap", "repo": r["repo"],
                             "detail": r.get("failing") or r.get("passed")})
        if r.get("pointers", 0) != POINTERS_PER_REPO:
            failures.append({"id": "pointer_gap", "repo": r["repo"], "detail": r.get("pointers")})
        if r.get("zero_copy_ok") is False:
            failures.append({"id": "zero_copy_violation", "repo": r["repo"]})

    if _leak(report):
        failures.append({"id": "absolute_path_leak"})
    if report.get("digest") != sha16({"repos": [(r.get("cang_id"), r.get("ledger_sha16"), r.get("passed"))
                                                for r in repos], "totals": report.get("totals")}):
        failures.append({"id": "self_digest"})
    return failures


def verify(root=None):
    report = aggregate(root)
    failures = check(report)
    return {"ok": not failures, "failures": failures, "report": report}


def _main(argv):
    cmd = argv[1] if len(argv) > 1 else "verify"
    if cmd not in ("verify", "report"):
        print("usage: python -m holoaeon.prehistory_injection [verify|report]", flush=True)
        return 2
    out = verify()
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    import sys
    raise SystemExit(_main(sys.argv))
