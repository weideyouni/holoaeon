# -*- coding: utf-8 -*-
# 另一份（技能开发副本）在 C:\Users\Administrator\AppData\Local\DoubaoWork\User Data\Default\.doubaowork\agent_mode\workspace\.user_skills\cross-thread-unity-protocol\scripts\unity_check.py；以仓内 scripts/ 本件为准（V88 P1-A 方案A 复制，非移动）。
"""CTUP unity_check —— 跨线程联通节点巡检（纯标准库，零依赖）

用法：
    python unity_check.py --project F:\\doubaowork\\holoaeon \
        --memory F:\\doubaowork\\holoaeon_memory --lathe F:\\doubaowork\\holoaeon_lathe [--remote]

输出 JSON：{schema, verdict, nodes{N1..N4,ledger,feed}, gaps[], checked_at}
verdict = UNITY_OK | UNITY_GAP；退出码 0 / 1。
"""
from __future__ import annotations

import argparse
import glob
import io
import json
import os
import re
import subprocess
import sys
import time

GIT_DIR = r"C:\Program Files\Git\cmd"


def _git(args, cwd):
    env = dict(os.environ)
    if os.name == "nt" and GIT_DIR not in env.get("PATH", ""):
        env["PATH"] = GIT_DIR + ";" + env.get("PATH", "")
    env["GIT_TERMINAL_PROMPT"] = "0"
    try:
        return subprocess.run(
            ["git"] + args, cwd=cwd, capture_output=True, text=True,
            encoding="utf-8", errors="replace", env=env, timeout=60,
        ).stdout.strip()
    except Exception as exc:  # noqa: BLE001
        return "<git failed: %s>" % type(exc).__name__


def node_coords(project):
    out = {"path": project, "exists": os.path.isdir(project)}
    if not out["exists"]:
        return out
    out["head"] = _git(["rev-parse", "HEAD"], project)
    out["branch"] = _git(["rev-parse", "--abbrev-ref", "HEAD"], project)
    remotes = {}
    for line in _git(["remote", "-v"], project).splitlines():
        parts = line.split()
        if len(parts) >= 3:
            remotes.setdefault(parts[0], {})[parts[2]] = parts[1]
    out["remotes"] = remotes
    out["commit_count"] = _git(["rev-list", "--count", "HEAD"], project)
    return out


def node_state(project, lathe, memory, memory_data):
    out = {}
    receipts = sorted(glob.glob(os.path.join(project, "reports", "*_receipt.json")))
    out["receipts"] = [os.path.basename(p) for p in receipts]
    if receipts:
        try:
            latest = json.load(io.open(receipts[-1], encoding="utf-8"))
            out["latest_receipt"] = {
                "file": os.path.basename(receipts[-1]),
                "batch": latest.get("batch"),
                "status": latest.get("status"),
                "head": latest.get("head"),
            }
        except Exception as exc:  # noqa: BLE001
            out["latest_receipt_error"] = type(exc).__name__
    anchors = sorted(glob.glob(os.path.join(lathe, "ANCHOR_*.md")))
    out["anchors_count"] = len(anchors)
    out["latest_anchor"] = os.path.basename(anchors[-1]) if anchors else None
    state_file = os.path.join(lathe, "ENGINE_LATHE_STATE.json")
    out["lathe_state"] = bool(os.path.exists(state_file))
    if out["lathe_state"]:
        out["lathe_state_mtime"] = time.strftime(
            "%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(state_file)))
    vh_path = os.path.join(memory, "version_history.json")
    if os.path.exists(vh_path):
        vh = json.load(io.open(vh_path, encoding="utf-8"))
        hist = vh.get("history") or []
        out["version_history_len"] = len(hist)
        if hist:
            last = hist[-1]
            out["last_history"] = {
                "batch": last.get("batch"),
                "stage": last.get("stage"),
                "head": last.get("head"),
                "date": last.get("date"),
            }
    ep_path = os.path.join(memory, "engineering_process.json")
    if os.path.exists(ep_path):
        out["engineering_process_len"] = len((json.load(io.open(ep_path, encoding="utf-8")).get("history") or []))
    return out


def node_credentials(memory):
    out = {"file": os.path.join(memory, "credential_registry.json"), "present": False}
    if not os.path.exists(out["file"]):
        return out
    doc = json.load(io.open(out["file"], encoding="utf-8"))
    out["present"] = True
    out["schema"] = doc.get("schema")
    out["updated_at"] = doc.get("updated_at")
    out["no_plaintext_policy"] = any(
        ("不存明文" in p) or ("指针" in p) for p in (doc.get("policy") or [])
    )
    status = {}
    for e in doc.get("entries") or []:
        status[e.get("id")] = e.get("status")
    out["entries"] = status
    out["valid_count"] = sum(1 for v in status.values() if v == "VALID")
    return out


def _with_gitee_token(url):
    """gitee 的 ssh 地址无法非交互回读 → 若本机有令牌，改写成 https 注入式（返回值用于命令，不打印）。"""
    tok_path = r"C:\Users\Administrator\.gitee_token"
    if "gitee.com" not in url or not os.path.exists(tok_path):
        return url
    tok = io.open(tok_path, encoding="utf-8").read().strip()
    if not tok:
        return url
    if url.startswith("git@gitee.com:"):
        path = url.split("git@gitee.com:", 1)[1]
        return "https://weideyouni:%s@gitee.com/%s" % (tok, path)
    if url.startswith("https://gitee.com/"):
        return url.replace("https://gitee.com/", "https://weideyouni:%s@gitee.com/" % tok)
    if url.startswith("https://") and "@gitee.com/" in url:
        return url
    return url


def node_readback(project, remote, memory):
    out = {}
    if not os.path.isdir(project):
        return out
    lines = [ln for ln in _git(["status", "--porcelain"], project).splitlines() if ln.strip()]
    tracked_dirty = [ln for ln in lines if not ln.startswith("??")]
    untracked = [ln for ln in lines if ln.startswith("??")]
    out["tracked_dirty"] = len(tracked_dirty)
    out["untracked"] = len(untracked)
    out["worktree_sample"] = tracked_dirty[:5] or untracked[:3]
    if not remote:
        return out
    coords = node_coords(project)
    out["head"] = coords.get("head")
    checks = {}
    for name, urls in (coords.get("remotes") or {}).items():
        url = urls.get("(push)") or urls.get("(fetch)")
        if not url:
            continue
        use = _with_gitee_token(url)
        res = _git(["ls-remote", use, "refs/heads/main"], project)
        sha = res.split()[0] if res and not res.startswith("<git failed") else None
        masked = re.sub(r"https://[^@]*@", "https://***@", url)
        if "gitee.com" in url and use != url:
            masked = masked.replace("git@gitee.com:", "https://***@gitee.com/")
        checks[name] = {
            "url": masked,
            "remote_main": sha,
            "same_as_local": sha == out["head"],
        }
    out["remote_checks"] = checks
    return out


def node_feed(lathe):
    files = sorted(glob.glob(os.path.join(lathe, "FEED_STATUS_*.json")))
    done, other = [], []
    for p in files:
        try:
            doc = json.load(io.open(p, encoding="utf-8"))
        except Exception:  # noqa: BLE001
            other.append(os.path.basename(p))
            continue
        (done if doc.get("state") == "EXECUTED_DONE" else other).append(
            {"file": os.path.basename(p), "batch": doc.get("batch"), "state": doc.get("state")})
    return {"executed": done, "not_executed": other, "total": len(files)}


def main(argv=None):
    ap = argparse.ArgumentParser(description="CTUP 跨线程联通节点巡检")
    ap.add_argument("--project", default=r"F:\doubaowork\holoaeon")
    ap.add_argument("--memory", default=r"F:\doubaowork\holoaeon_memory")
    ap.add_argument("--lathe", default=r"F:\doubaowork\holoaeon_lathe")
    ap.add_argument("--remote", action="store_true", help="额外做 ls-remote 同头校验（联网）")
    args = ap.parse_args(argv)

    nodes = {
        "N1_coords": node_coords(args.project),
        "N2_state": node_state(args.project, args.lathe, args.memory, None),
        "N3_credentials": node_credentials(args.memory),
        "N4_readback": node_readback(args.project, args.remote, args.memory),
        "feed": node_feed(args.lathe),
    }

    gaps = []
    if not nodes["N1_coords"].get("exists"):
        gaps.append("N1 项目路径不存在: %s" % args.project)
    if not nodes["N1_coords"].get("head"):
        gaps.append("N1 取不到 HEAD（不是 git 仓？）")
    if not nodes["N2_state"].get("receipts"):
        gaps.append("N2 无批次回执 reports/v*_receipt.json")
    if not nodes["N2_state"].get("anchors_count"):
        gaps.append("N2 无锚点 ANCHOR_*.md")
    if not nodes["N2_state"].get("lathe_state"):
        gaps.append("N2 无 ENGINE_LATHE_STATE.json（机床未快照）")
    if nodes["N2_state"].get("version_history_len") is None:
        gaps.append("N2 玉安 version_history 不可读")
    if not nodes["N3_credentials"].get("present"):
        gaps.append("N3 无 credential_registry.json")
    elif nodes["N3_credentials"].get("valid_count", 0) < 2:
        gaps.append("N3 可用凭证少于 2（PATH 或凭据管理器可能失联）")
    if nodes["N4_readback"].get("tracked_dirty", 0) > 0:
        gaps.append("N4 已跟踪文件有改动（%d 条）" % nodes["N4_readback"]["tracked_dirty"])
    if args.remote:
        for name, v in (nodes["N4_readback"].get("remote_checks") or {}).items():
            if not v.get("same_as_local"):
                gaps.append("N4 远端 %s 与本地不同头（remote=%s）" % (name, v.get("remote_main")))

    verdict = "UNITY_OK" if not gaps else "UNITY_GAP"
    doc = {
        "schema": "CTUP-UNITY-CHECK/1.0",
        "checked_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "verdict": verdict,
        "nodes": nodes,
        "gaps": gaps,
    }
    print(json.dumps(doc, ensure_ascii=False, indent=2))
    return 0 if verdict == "UNITY_OK" else 1


if __name__ == "__main__":
    sys.exit(main())
