#!/usr/bin/env python
"""三地同步：本地 Git 提交 → Gitee（权威源）→ GitHub（服务端定时对齐）→ Hugging Face（镜像）。

一条命令给出三端各自的结论，验收口径只有一个「对象摘要哈希」：

  本地      sha256( git ls-tree -r --full-tree HEAD，剔除 .github/，按字节序排序 )
  Gitee     branch main 的 head 必须等于本地 HEAD
  GitHub    sync-status 分支上的 .sync/object_digest.txt 必须等于本地摘要
  HF        文件数等于 tracked 数，且抽样/全量文件 sha256 与本地提交逐字节相同

用法：

    python scripts/three_way_sync.py --repo <仓库>                  # 只检查（默认）
    python scripts/three_way_sync.py --repo <仓库> --push-gitee --push-hf
    python scripts/three_way_sync.py --repo <仓库> --json --receipt <文件>

退出码：0 三端全 PASS；1 有端不一致；2 缺令牌/依赖；5 工作树脏导致跳过推送。
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import urllib.request

EXIT_OK = 0
EXIT_MISMATCH = 1
EXIT_DEPS = 2
EXIT_GIT = 3
EXIT_DIRTY = 5

GITEE_API = "https://gitee.com/api/v5/repos/%s/%s/branches/%s"
GITHUB_RAW = "https://raw.githubusercontent.com/%s/%s/sync-status/.sync/%s"


def git(repo, *args):
    proc = subprocess.run(["git", "-C", repo] + list(args),
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if proc.returncode != 0:
        raise RuntimeError(proc.stdout.decode("utf-8", "replace")[:400])
    return proc.stdout.decode("utf-8", "replace")


def read_text(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "three-way-sync"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "replace")


def load_token():
    env = os.environ.get("GITEE_TOKEN", "").strip()
    if env:
        return env
    for path in (os.path.join(os.path.expanduser("~"), ".gitee_token"),
                 os.path.join(os.environ.get("USERPROFILE", ""), ".gitee_token")):
        if path and os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as fh:
                tok = fh.read().strip()
            if tok:
                return tok
    return ""


def object_digest(repo):
    """与 GitHub 工作流同一口径：剔除 .github/ 后按字节序排序再 sha256。"""
    lines = git(repo, "ls-tree", "-r", "--full-tree", "HEAD").splitlines()
    keep = []
    for line in lines:
        path = line.split("\t", 1)[1] if "\t" in line else ""
        if path and not path.startswith(".github/"):
            keep.append(line)
    keep.sort(key=lambda s: s.encode("utf-8"))
    blob = ("\n".join(keep) + "\n").encode("utf-8")
    return hashlib.sha256(blob).hexdigest(), len(lines), len(keep)


def gitee_head(owner, name, branch, token):
    req = urllib.request.Request(GITEE_API % (owner, name, branch),
                                 headers={"Authorization": "token " + token,
                                          "User-Agent": "three-way-sync"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["commit"]["sha"]


def github_status(owner, name):
    heads = read_text(GITHUB_RAW % (owner, name, "heads.txt"))
    info = {}
    for line in heads.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            info[k.strip()] = v.strip()
    try:
        info["object_digest"] = read_text(GITHUB_RAW % (owner, name, "object_digest.txt")).strip()
    except Exception:  # noqa: BLE001
        info.setdefault("object_digest", "")
    return info


def main(argv=None):
    ap = argparse.ArgumentParser(description="本地 → Gitee → GitHub → Hugging Face 三地同步验收")
    ap.add_argument("--repo", required=True)
    ap.add_argument("--branch", default="main")
    ap.add_argument("--gitee-owner", default="weideyouni")
    ap.add_argument("--gitee-name", default="holoaeon")
    ap.add_argument("--github-owner", default="weideyouni")
    ap.add_argument("--github-name", default="holoaeon")
    ap.add_argument("--hf-script", default="", help="hf_mirror.py 路径，缺省用本目录")
    ap.add_argument("--hf-name", default="holoaeon")
    ap.add_argument("--hf-space-dir", default="")
    ap.add_argument("--hf-verify", default="sample", choices=["sample", "all", "none"])
    ap.add_argument("--push-gitee", action="store_true")
    ap.add_argument("--push-hf", action="store_true")
    ap.add_argument("--allow-dirty", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--receipt", default="")
    args = ap.parse_args(argv)

    repo = os.path.abspath(args.repo)
    if not os.path.isdir(repo):
        print("[FAIL] 仓库不存在：%s" % repo)
        return EXIT_GIT

    receipt = {"repo": repo, "branch": args.branch, "head": "", "dirty": False,
               "tracked": 0, "objects": 0, "object_digest": "", "gitee": {}, "github": {},
               "hf": {}, "verdict": ""}
    try:
        receipt["head"] = git(repo, "rev-parse", "HEAD").strip()
        receipt["tracked"] = len(git(repo, "ls-files").splitlines())
        receipt["dirty"] = bool(git(repo, "status", "--porcelain").strip())
        digest, total, keep = object_digest(repo)
        receipt["object_digest"] = digest
        receipt["objects"] = keep
        receipt["objects_all"] = total
    except Exception as exc:  # noqa: BLE001
        print("[FAIL] 读本地仓库失败：%s" % exc)
        return EXIT_GIT

    print("[i] local HEAD=%s tracked=%d objects=%d(all %d) dirty=%s"
          % (receipt["head"][:12], receipt["tracked"], receipt["objects"],
             receipt["objects_all"], receipt["dirty"]))
    print("[i] local object_digest=%s" % digest)

    # ---- Gitee
    failed = False
    token = load_token()
    if not token:
        receipt["gitee"] = {"ok": False, "error": "找不到 Gitee 令牌（~/.gitee_token 或 GITEE_TOKEN）"}
        failed = True
        print("[FAIL] gitee：缺令牌，跳过")
    else:
        try:
            remote = gitee_head(args.gitee_owner, args.gitee_name, args.branch, token)
            entry = {"head": remote, "ok": remote == receipt["head"]}
            if not entry["ok"] and args.push_gitee:
                if receipt["dirty"] and not args.allow_dirty:
                    entry["error"] = "工作树不干净，拒绝推送（先提交，或加 --allow-dirty）"
                    entry["ok"] = False
                else:
                    pub = os.path.join(repo, "scripts", "gitee_publish.py")
                    cmd = [sys.executable, pub, "--repo", repo, "--branch", args.branch,
                           "--owner", args.gitee_owner, "--name", args.gitee_name, "--json"]
                    if args.allow_dirty:
                        cmd.append("--allow-dirty")
                    out = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    text = out.stdout.decode("utf-8", "replace")
                    print(text.strip())
                    entry["push_rc"] = out.returncode
                    entry["head"] = gitee_head(args.gitee_owner, args.gitee_name, args.branch, token)
                    entry["ok"] = entry["head"] == receipt["head"]
            receipt["gitee"] = entry
            print("[%s] gitee head=%s" % ("OK" if entry["ok"] else "DIFF", entry["head"][:12]))
            failed = failed or not entry["ok"]
        except Exception as exc:  # noqa: BLE001
            receipt["gitee"] = {"ok": False, "error": "读 Gitee 失败：%s" % exc}
            failed = True
            print("[FAIL] gitee：%s" % exc)

    # ---- GitHub
    try:
        gh = github_status(args.github_owner, args.github_name)
        ok = (gh.get("object_digest") == digest) and (gh.get("gitee_head") == receipt["head"])
        receipt["github"] = {"ok": ok, "gitee_head": gh.get("gitee_head", ""),
                             "github_head": gh.get("github_head", ""),
                             "file_count": gh.get("file_count", ""),
                             "object_digest": gh.get("object_digest", "")}
        print("[%s] github gitee_head=%s digest=%s files=%s"
              % ("OK" if ok else "DIFF", (gh.get("gitee_head") or "-")[:12],
                 (gh.get("object_digest") or "-")[:16], gh.get("file_count", "-")))
        if not ok:
            receipt["github"]["error"] = ("stale: 等下一个整点定时（每 30 分钟一次）或由 agent 触发一次 "
                                          "sync-from-gitee（push/dispatch 均会触发）")
        failed = failed or not ok
    except Exception as exc:  # noqa: BLE001
        receipt["github"] = {"ok": False, "error": "读 GitHub sync-status 失败：%s" % exc}
        failed = True
        print("[FAIL] github：%s" % exc)

    # ---- Hugging Face
    hf_script = args.hf_script or os.path.join(os.path.dirname(os.path.abspath(__file__)), "hf_mirror.py")
    cmd = [sys.executable, hf_script, "--repo", repo, "--name", args.hf_name,
           "--verify", args.hf_verify, "--json"]
    if args.hf_space_dir:
        cmd += ["--space-dir", args.hf_space_dir]
    if not args.push_hf:
        cmd.append("--check-only")
    try:
        out = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        text = out.stdout.decode("utf-8", "replace").strip()
        try:
            hf = json.loads(text.splitlines()[-1])
        except Exception:  # noqa: BLE001
            hf = {"ok": False, "error": text[-400:]}
        hf["ok"] = bool(hf.get("verified"))
        receipt["hf"] = hf
        print("[%s] hf files=%s agree=%s" % ("OK" if hf["ok"] else "DIFF",
                                             hf.get("remote_files", "-"), hf.get("agree", "-")))
        failed = failed or not hf["ok"]
    except Exception as exc:  # noqa: BLE001
        receipt["hf"] = {"ok": False, "error": "HF 检查失败：%s" % exc}
        failed = True
        print("[FAIL] hf：%s" % exc)

    receipt["verdict"] = "FAIL" if failed else "PASS"
    if args.receipt:
        path = os.path.abspath(args.receipt)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
        print("[i] receipt -> %s" % path)

    if args.json:
        print(json.dumps(receipt, ensure_ascii=False))
    else:
        print("==> 三地一致性：%s" % receipt["verdict"])

    if receipt["verdict"] == "PASS":
        return EXIT_OK
    if receipt["dirty"] and receipt["gitee"].get("ok") is False:
        return EXIT_DIRTY
    return EXIT_MISMATCH


if __name__ == "__main__":
    sys.exit(main())
