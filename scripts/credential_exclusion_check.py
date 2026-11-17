# -*- coding: utf-8 -*-
"""credential_exclusion_check.py — CTUP G10 凭据排除的可执行断言。

三层：
  L1 规则层：仓根 .gitignore 必须含凭据排除规则（显式声明，不能靠"没人加"）
  L2 清单层：五地清单/向量海清单/manifest 里不得出现凭据文件路径
  L3 内容层：仓内文本文件不得出现 gho_/ghp_/hf_/token= 等明文模式

纪律：纯标准库 / 零网络 / 只读 / 输出掩码（问题描述只报文件名，不回显命中内容）。
用法：
  python scripts/credential_exclusion_check.py            # 全跑，红则 exit 1
  python scripts/credential_exclusion_check.py --json     # 只输出 JSON
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

REPO = os.environ.get(
    "HOLOAEON_REPO",
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

GITIGNORE = os.path.join(REPO, ".gitignore")

REQUIRED_IGNORE_RULES = ("credential_registry.json", "holoaeon_memory", "*.bak_ctup_*")

CREDENTIAL_PATH_MARKERS = (
    "credential_registry", "holoaeon_memory", ".gitee_token", ".github_token",
    ".hf_token", ".ssh/", "id_ed25519", "longaeon_gh_ed25519",
)

PLAINTEXT_PATTERNS = (
    re.compile(r"gh[pousr]_[A-Za-z0-9]{16,}"),
    re.compile(r"hf_[A-Za-z0-9]{20,}"),
    re.compile(r"token=[A-Za-z0-9]{16,}"),
    re.compile(r"(?i)api[_-]?key\s*[:=]\s*['\"]?[A-Za-z0-9._-]{20,}"),
)

TEXT_EXT = (".py", ".json", ".md", ".txt", ".yml", ".yaml", ".cfg", ".ini", ".toml",
            ".csv", ".ps1", ".sh", ".gitignore")
SKIP_DIRS = (".git", "__pycache__", "node_modules", ".pytest_cache")
MAX_BYTES = 4 * 1024 * 1024


def check_gitignore(path: str = GITIGNORE) -> dict:
    problems = []
    if not os.path.isfile(path):
        return {"pass": False, "problems": ["缺 .gitignore：{}".format(path)]}
    text = ""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        return {"pass": False, "problems": ["读 .gitignore 失败：{}".format(type(exc).__name__)]}
    for rule in REQUIRED_IGNORE_RULES:
        if rule not in text:
            problems.append("缺显式排除规则：{}".format(rule))
    return {"pass": not problems, "problems": problems,
            "required": list(REQUIRED_IGNORE_RULES)}


def _walk_strings(node, out, key=""):
    """收集 (key, value)；指针字段（键名含 pointer / 值含「指针」）不参与否决。"""
    if isinstance(node, str):
        if key and "pointer" in key.lower():
            return
        if "指针" in node or "pointer" in node.lower():
            return
        out.append(node)
    elif isinstance(node, dict):
        for k, v in node.items():
            if "pointer" not in str(k).lower():
                _walk_strings(str(k), out, key)
            _walk_strings(v, out, str(k))
    elif isinstance(node, (list, tuple)):
        for v in node:
            _walk_strings(v, out, key)


def check_manifest(path: str) -> dict:
    if not os.path.isfile(path):
        return {"pass": True, "problems": [], "manifest": path, "note": "manifest 不存在，跳过"}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        return {"pass": False,
                "problems": ["manifest 不可解析：{}: {}".format(path, type(exc).__name__)],
                "manifest": path}
    hits = []
    strings = []
    _walk_strings(data, strings)
    for s in strings:
        low = s.lower()
        for marker in CREDENTIAL_PATH_MARKERS:
            if marker.lower() in low:
                hits.append("{}".format(os.path.basename(path)))
                break
    problems = []
    if hits:
        problems.append("清单 {} 含凭据文件路径（{} 处命中）".format(
            os.path.basename(path), len(hits)))
    return {"pass": not problems, "problems": problems, "manifest": path,
            "hit_count": len(hits)}


def check_tree(root: str = REPO) -> dict:
    problems = []
    scanned = 0
    hits = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if not name.lower().endswith(TEXT_EXT):
                continue
            p = os.path.join(dirpath, name)
            try:
                if os.path.getsize(p) > MAX_BYTES:
                    continue
                with open(p, "r", encoding="utf-8", errors="strict") as fh:
                    body = fh.read()
            except (OSError, UnicodeDecodeError):
                continue
            scanned += 1
            for pat in PLAINTEXT_PATTERNS:
                if pat.search(body):
                    # 只报文件名与模式序号，不回显命中内容（输出掩码纪律）
                    problems.append("{} 命中明文模式 #{}（内容已掩码）".format(
                        os.path.relpath(p, root), PLAINTEXT_PATTERNS.index(pat) + 1))
                    hits += 1
                    break
    return {"pass": not problems, "problems": problems,
            "scanned": scanned, "hits": hits}


def default_manifests(repo: str = REPO):
    cand = [
        os.path.join(repo, "reports", "five_site_manifest.json"),
        os.path.join(repo, "reports", "remote_sync_20261117.json"),
        os.path.join(repo, "data", "genome_dna.json"),
        os.path.join(repo, "data", "plugin_contract.json"),
    ]
    sea = os.path.join(os.path.dirname(repo), "vector-sea")
    if os.path.isdir(sea):
        for d in sorted(os.listdir(sea)):
            for name in ("VECTOR_SEA_MANIFEST.json", "manifest.json"):
                p = os.path.join(sea, d, name)
                if os.path.isfile(p):
                    cand.append(p)
    return [p for p in cand if os.path.isfile(p)]


def run(repo: str = REPO, manifests=None) -> dict:
    manifests = default_manifests(repo) if manifests is None else manifests
    layers = {
        "L1_gitignore": check_gitignore(os.path.join(repo, ".gitignore")),
        "L2_manifests": [check_manifest(p) for p in manifests],
        "L3_tree": check_tree(repo),
    }
    problems = list(layers["L1_gitignore"]["problems"])
    for m in layers["L2_manifests"]:
        problems.extend(m["problems"])
    problems.extend(layers["L3_tree"]["problems"])
    return {"pass": not problems, "problems": problems, "layers": layers,
            "repo": repo, "manifests": len(manifests),
            "zero_plaintext": layers["L3_tree"]["hits"] == 0}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=REPO)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    out = run(args.repo)
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print("credential_exclusion_check: {}".format("PASS" if out["pass"] else "FAIL"))
        print("  L1 gitignore 规则: {}".format(
            "ok" if out["layers"]["L1_gitignore"]["pass"] else "red"))
        print("  L2 清单扫描: {} 份 / 红 {} 份".format(
            out["manifests"],
            sum(1 for m in out["layers"]["L2_manifests"] if not m["pass"])))
        print("  L3 文本扫描: {} 文件 / 明文命中 {}".format(
            out["layers"]["L3_tree"]["scanned"], out["layers"]["L3_tree"]["hits"]))
        for p in out["problems"]:
            print("  - {}".format(p))
    return 0 if out["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
