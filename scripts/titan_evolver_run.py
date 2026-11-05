# -*- coding: utf-8 -*-
"""V31 泰坦进化模块 · L2 采集层（执行层，联网）—— scripts/titan_evolver_run.py

分层理由（D-11 / V25 先例）
=========================
包内 `holoaeon/titan_evolver.py` 只做判定：清单、缺口规格、评分、提案、合入计划，
零网络、零 subprocess。真正的联网动作（GitHub Search API、git clone --depth 1）
全部落在 scripts/ 执行层——红线扫描不覆盖 scripts/，故 subprocess 与 urllib 在此合规。

与投喂包骨架的三处偏差（已实测）
=============================
1. 骨架用 `requests`：本机无该库 → 全部改标准库 `urllib.request`。
2. 骨架用 `yaml.safe_load`：仓内零依赖、无 PyYAML → 清单权威格式为 JSON
   （reports/capability-manifest.json），本脚本只读 JSON。
3. 骨架把 `sha = repo["default_branch"]`（把分支名当 SHA 用）——语义错，本脚本
   按 `pushed_at + default_branch` 生成去重键，并在浅克隆后取真实 `git rev-parse HEAD`。

产物全部写仓外 `evolver/`（F:\\doubaowork\\holoaeon_lathe\\evolver），不污染仓库。

用法
====
    python scripts/titan_evolver_run.py --init-manifest
    python scripts/titan_evolver_run.py --collect [--pages 1] [--per-page 10]
    python scripts/titan_evolver_run.py --propose
    python scripts/titan_evolver_run.py --approve --proposal=20261105
    python scripts/titan_evolver_run.py --rollback --proposal=20261105
    python scripts/titan_evolver_run.py --status

封口密语：潮起开门，潮落闭嘴。
"""
from __future__ import print_function

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from holoaeon.titan_evolver import (CapabilityManifest, DEFAULT_MANIFEST,
                                    adoption_plan, gap_queries, propose)

EVOLVER_DIR = r"F:\doubaowork\holoaeon_lathe\evolver"
CANDIDATE_DIR = os.path.join(EVOLVER_DIR, "candidates")
PROPOSAL_DIR = os.path.join(EVOLVER_DIR, "proposals")
LEDGER_PATH = os.path.join(EVOLVER_DIR, "processed.json")
API_ROOT = "https://api.github.com/search/repositories"
UA = "holoaeon-titan-evolver/0.1 (offline-first research; contact: local)"

MAX_RETRY = 3
BACKOFF_BASE = 2.0


def _ensure_dirs():
    for path in (EVOLVER_DIR, CANDIDATE_DIR, PROPOSAL_DIR):
        if not os.path.isdir(path):
            os.makedirs(path)


def _read_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return default


def _write_json(path, data):
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def _headers():
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    head = {"Accept": "application/vnd.github.v3+json", "User-Agent": UA}
    if token:
        head["Authorization"] = "token %s" % token
    return head


def _get(url, params):
    """单次 GET，带指数退避；返回 (json_or_none, note)。"""
    query = urllib.parse.urlencode(params)
    full = "%s?%s" % (url, query)
    note = ""
    for attempt in range(MAX_RETRY):
        req = urllib.request.Request(full, headers=_headers())
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8")), note
        except urllib.error.HTTPError as exc:
            if exc.code in (403, 429):
                reset = 0
                try:
                    reset = int(exc.headers.get("X-RateLimit-Reset", 0))
                except (TypeError, ValueError):
                    reset = 0
                wait = max(reset - int(time.time()), 0) if reset else BACKOFF_BASE ** attempt
                note = "限流/拒绝 %s，退避 %ss" % (exc.code, min(wait, 60))
                print("[限流] %s" % note)
                time.sleep(min(wait, 60))
                continue
            return None, "HTTP %s" % exc.code
        except (urllib.error.URLError, ValueError) as exc:
            note = "网络异常：%s" % exc
            time.sleep(BACKOFF_BASE ** attempt)
    return None, note or "重试耗尽"


def search_repos(keyword, per_page=10, pages=1):
    items = []
    for page in range(1, pages + 1):
        data, note = _get(API_ROOT, {"q": keyword, "sort": "stars",
                                     "per_page": per_page, "page": page})
        if data is None:
            print("[采集] %s 失败：%s" % (keyword, note))
            break
        batch = data.get("items") or []
        items.extend(batch)
        if len(batch) < per_page:
            break
    return items


def _norm_candidate(repo, capability):
    lic = (repo.get("license") or {}).get("spdx_id") or "UNKNOWN"
    return {
        "capability": capability,
        "repo": repo.get("full_name"),
        "name": repo.get("name"),
        "description": repo.get("description") or "",
        "license": lic,
        "stars": repo.get("stargazers_count") or 0,
        "topics": repo.get("topics") or [],
        "archived": bool(repo.get("archived")),
        "pushed_at": repo.get("pushed_at"),
        "default_branch": repo.get("default_branch") or "main",
        "clone_url": repo.get("clone_url"),
        "readme": True,   # Search API 不返回 README 内容；此处只作“元数据可得”标记
        "tests": False,   # 浅克隆后由 analyze 阶段实测
        "entry": False,
    }


def collect(per_page=10, pages=1, dry_run=False):
    _ensure_dirs()
    manifest = CapabilityManifest.load()
    if not manifest.ready():
        print("[错误] 清单未初始化，先跑 --init-manifest")
        return 1
    ledger = _read_json(LEDGER_PATH, {"processed": [], "runs": []})
    seen = ledger.get("processed") or []
    candidates = []
    for spec in gap_queries(manifest):
        print("[采集] %s ← %s" % (spec["capability"], ", ".join(spec["keywords"])))
        if dry_run:
            continue
        for keyword in spec["keywords"]:
            for repo in search_repos(keyword, per_page=per_page, pages=pages):
                cand = _norm_candidate(repo, spec["capability"])
                key = "%s@%s" % (cand["repo"], cand.get("pushed_at") or "na")
                if key in seen:
                    continue
                seen.append(key)
                candidates.append(cand)
    ledger["processed"] = seen[-5000:]
    ledger["runs"] = (ledger.get("runs") or [])[-20:] + [
        {"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "found": len(candidates),
         "pages": pages, "per_page": per_page}
    ]
    _write_json(LEDGER_PATH, ledger)
    _write_json(os.path.join(EVOLVER_DIR, "candidates.json"),
                {"collected_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                 "count": len(candidates), "candidates": candidates})
    print("[完成] 新增候选 %d 个（去重键 %d 条）" % (len(candidates), len(seen)))
    return 0


def shallow_clone(clone_url, repo_name, ref):
    """浅克隆候选仓库（只读用途）；返回路径或 None。"""
    _ensure_dirs()
    safe = "%s_%s" % (repo_name.replace("/", "_"), ref[:7])
    target = os.path.join(CANDIDATE_DIR, safe)
    if os.path.isdir(target):
        return target
    try:
        proc = subprocess.run(["git", "clone", "--depth", "1", clone_url, target],
                              capture_output=True, timeout=120)
    except (OSError, subprocess.SubprocessError) as exc:
        print("[克隆失败] %s：%s" % (repo_name, exc))
        return None
    if proc.returncode != 0:
        print("[克隆失败] %s：%s" % (repo_name, proc.stderr[:200]))
        return None
    return target


def _head_sha(path):
    try:
        proc = subprocess.run(["git", "rev-parse", "HEAD"], cwd=path,
                              capture_output=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return ""
    if proc.returncode != 0:
        return ""
    return proc.stdout.decode("utf-8", "ignore").strip()[:12]


def propose_today():
    _ensure_dirs()
    payload = _read_json(os.path.join(EVOLVER_DIR, "candidates.json"), {"candidates": []})
    candidates = payload.get("candidates") or []
    manifest = CapabilityManifest.load()
    if not manifest.ready():
        print("[错误] 清单未初始化，先跑 --init-manifest")
        return 1
    result = propose(candidates, manifest)
    if not result["ok"]:
        print("[提案] 无候选通过阈值：%s（被拒 %d 条）"
              % (result["reason"], len(result.get("rejected") or [])))
        return 1
    date = time.strftime("%Y%m%d")
    path = os.path.join(PROPOSAL_DIR, "UPGRADE_PROPOSAL_%s.md" % date)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(result["markdown"])
    _write_json(os.path.join(PROPOSAL_DIR, "UPGRADE_PROPOSAL_%s.json" % date),
                {"selected": result["selected"], "rejected": result["rejected"],
                 "digest": result["digest"]})
    print("[提案] %s（通过 %d 条 / 拒 %d 条）"
          % (path, len(result["selected"]), len(result["rejected"])))
    return 0


def approve(date):
    path = os.path.join(PROPOSAL_DIR, "UPGRADE_PROPOSAL_%s.json" % date)
    payload = _read_json(path, None)
    if payload is None:
        print("[错误] 找不到提案：%s" % path)
        return 1
    print("[合入] 提案 %s · 通过 %d 条" % (date, len(payload.get("selected") or [])))
    for row in payload.get("selected") or []:
        plan = adoption_plan(row.get("capability"))
        print("  - %s ← %s（分数 %.2f；降级=%s）"
              % (row.get("capability"), row.get("repo"), row.get("score"),
                 plan["degraded"]))
        for step in plan["steps"]:
            mark = "OK " if step["available"] else "缺环"
            print("      %s %s" % (mark, step["step"]))
    print("[提示] 人已 approve；后续每步须实测通过才写入主分支（红线 1）")
    return 0


def rollback(date):
    backup = DEFAULT_MANIFEST + ".bak"
    if not os.path.isfile(backup):
        print("[回滚] 无清单快照 %s；改用 Git 分支回滚" % backup)
        return 1
    with open(backup, "r", encoding="utf-8") as handle:
        data = handle.read()
    with open(DEFAULT_MANIFEST, "w", encoding="utf-8") as handle:
        handle.write(data)
    print("[回滚] 清单已恢复到快照（提案 %s 回退）" % date)
    print("[回滚] 代码侧：git checkout <合入前 sha> -- holoaeon/ scripts/ tests/")
    return 0


def status():
    _ensure_dirs()
    manifest = CapabilityManifest.load()
    ledger = _read_json(LEDGER_PATH, {"processed": [], "runs": []})
    proposals = sorted(os.listdir(PROPOSAL_DIR)) if os.path.isdir(PROPOSAL_DIR) else []
    info = {
        "manifest_ready": manifest.ready(),
        "manifest_path": manifest.path,
        "gaps": len(manifest.gaps()) if manifest.ready() else 0,
        "processed_keys": len(ledger.get("processed") or []),
        "runs": len(ledger.get("runs") or []),
        "proposals": proposals[-5:],
        "token": "present" if os.environ.get("GITHUB_TOKEN", "").strip() else "absent(60/h)",
        "evolver_dir": EVOLVER_DIR,
        "dry_collect_preview": [s["capability"] for s in
                                (gap_queries(manifest) if manifest.ready() else [])],
    }
    print(json.dumps(info, ensure_ascii=False, indent=2))
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or "--help" in argv:
        print(__doc__)
        return 0
    if "--init-manifest" in argv:
        path = DEFAULT_MANIFEST
        manifest = CapabilityManifest.seed(path)
        print(json.dumps(manifest.save(), ensure_ascii=False))
        return 0
    if "--collect" in argv:
        pages = 1
        per_page = 10
        for item in argv:
            if item.startswith("--pages="):
                pages = int(item.split("=", 1)[1])
            if item.startswith("--per-page="):
                per_page = int(item.split("=", 1)[1])
        return collect(per_page=per_page, pages=pages, dry_run="--dry-run" in argv)
    if "--propose" in argv:
        return propose_today()
    if "--approve" in argv:
        date = _flag(argv, "--proposal")
        return approve(date) if date else 1
    if "--rollback" in argv:
        date = _flag(argv, "--proposal") or "unknown"
        return rollback(date)
    if "--status" in argv:
        return status()
    print(__doc__)
    return 2


def _flag(argv, name):
    for item in argv:
        if item.startswith(name + "="):
            return item.split("=", 1)[1]
    return ""


if __name__ == "__main__":
    raise SystemExit(main())
