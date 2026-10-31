#!/usr/bin/env python
"""Gitee 直传器：把本地 Git 仓库推到 Gitee，并用远端哈希自证。

用法（零依赖，Python 3.8+）：

    python scripts/gitee_publish.py --repo . --branch main
    python scripts/gitee_publish.py --repo . --branch main --dry-run
    python scripts/gitee_publish.py --repo . --owner weideyouni --name vector-sea

设计口径：
- 令牌只从环境变量 `GITEE_TOKEN` 或令牌文件读取，绝不落到命令历史与仓库里。
- 推送后一律回读远端 ref 与本地 HEAD 比对，`verified=false` 时以非零码退出——
  也就是「推上去了」这句话必须由远端哈希签收，而不是由 push 的退出码签收。
- 不改写历史、不 `--force`；远端分叉时直接失败并打印两条哈希。
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time

TOKEN_ENV = "GITEE_TOKEN"
TOKEN_FILE_CANDIDATES = [
    os.path.join(os.path.expanduser("~"), ".gitee_token"),
    os.path.join(os.environ.get("USERPROFILE", ""), ".gitee_token"),
    os.path.join(os.environ.get("HOME", ""), ".gitee_token"),
]

EXIT_OK = 0
EXIT_TOKEN = 2
EXIT_GIT = 3
EXIT_VERIFY = 4
EXIT_DIRTY = 5


def load_token(explicit_path=None):
    """按 环境变量 → 显式文件 → 默认文件 的顺序取令牌。"""
    env_tok = os.environ.get(TOKEN_ENV, "").strip()
    if env_tok:
        return env_tok, "env:" + TOKEN_ENV
    paths = [explicit_path] if explicit_path else TOKEN_FILE_CANDIDATES
    for path in paths:
        if not path:
            continue
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as handle:
                tok = handle.read().strip()
            if tok:
                return tok, "file:" + path
    return "", ""


def mask(token):
    """日志里只留末四位，避免令牌被回显到终端或 CI 日志。"""
    if len(token) <= 4:
        return "****"
    return "****" + token[-4:]


def run_git(args, cwd, timeout=300):
    proc = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
    )
    return proc.returncode, proc.stdout.decode("utf-8", "replace").strip()


def git_config(cwd, key):
    code, out = run_git(["config", "--get", key], cwd)
    return out if code == 0 else ""


def resolve_slug(cwd, remote_name):
    """从 origin URL 解析 owner/name，兼容 https 与 ssh 两种写法。"""
    url = git_config(cwd, "remote.%s.url" % remote_name)
    match = re.search(r"[:/]([\w.\-]+)/([\w.\-]+?)(?:\.git)?$", url or "")
    if not match:
        return None, None
    return match.group(1), match.group(2)


def is_dirty(cwd):
    code, out = run_git(["status", "--porcelain"], cwd)
    return code == 0 and bool(out.strip()), out


def head_sha(cwd):
    code, out = run_git(["rev-parse", "HEAD"], cwd)
    return out if code == 0 else ""


def remote_sha(auth_url, ref, cwd):
    code, out = run_git(["ls-remote", auth_url, ref], cwd)
    if code != 0:
        return "", out
    for line in out.splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1].endswith(ref):
            return parts[0], ""
    return "", ""


def build_url(owner, name, token):
    return "https://oauth2:%s@gitee.com/%s/%s.git" % (token, owner, name)


def publish(repo_path, branch, owner, name, token, push_tags=True, allow_dirty=False,
            dry_run=False, remote_name="origin"):
    """执行推送并返回结构化回执；调用方据此判断退出码。"""
    receipt = {
        "repo": owner + "/" + name,
        "branch": branch,
        "local_sha": "",
        "remote_before": "",
        "remote_after": "",
        "pushed": False,
        "tags_pushed": False,
        "verified": False,
        "elapsed_s": 0.0,
        "token": mask(token),
        "error": "",
    }
    started = time.time()

    dirty, dirty_out = is_dirty(repo_path)
    if dirty and not allow_dirty:
        receipt["error"] = "工作树不干净，先提交或加 --allow-dirty；改动如下：" + dirty_out.replace("\n", " | ")
        receipt["elapsed_s"] = round(time.time() - started, 2)
        return receipt, EXIT_DIRTY

    local = head_sha(repo_path)
    receipt["local_sha"] = local
    if not local:
        receipt["error"] = "取不到本地 HEAD，检查 --repo 是否是 Git 仓库"
        receipt["elapsed_s"] = round(time.time() - started, 2)
        return receipt, EXIT_GIT

    url = build_url(owner, name, token)
    ref = "refs/heads/" + branch
    before, err = remote_sha(url, ref, repo_path)
    if err and "couldn't find remote ref" not in err.lower():
        receipt["error"] = "读远端 ref 失败：" + err.split("https://")[0].strip()
        receipt["elapsed_s"] = round(time.time() - started, 2)
        return receipt, EXIT_GIT
    receipt["remote_before"] = before

    if dry_run:
        receipt["error"] = "dry-run：只报告比对结果，未执行推送"
        receipt["remote_after"] = before
        receipt["verified"] = before == local
        receipt["elapsed_s"] = round(time.time() - started, 2)
        return receipt, EXIT_OK

    code, out = run_git(["push", url, "%s:%s" % (branch, branch)], repo_path)
    receipt["pushed"] = code == 0
    if code != 0:
        receipt["error"] = "推送失败：" + out.split("https://")[0].strip()[-400:]
        receipt["elapsed_s"] = round(time.time() - started, 2)
        return receipt, EXIT_GIT

    if push_tags:
        tag_code, tag_out = run_git(["push", url, "--tags"], repo_path)
        receipt["tags_pushed"] = tag_code == 0
        if tag_code != 0:
            receipt["error"] = "标签推送失败：" + tag_out.split("https://")[0].strip()[-200:]

    after, err = remote_sha(url, ref, repo_path)
    receipt["remote_after"] = after
    receipt["verified"] = bool(after) and after == local
    if not receipt["verified"]:
        receipt["error"] = receipt["error"] or "远端哈希未追平本地 HEAD"
    receipt["elapsed_s"] = round(time.time() - started, 2)
    return receipt, EXIT_OK if receipt["verified"] else EXIT_VERIFY


def main(argv=None):
    parser = argparse.ArgumentParser(description="本地仓库 → Gitee 直传（带远端哈希校验）")
    parser.add_argument("--repo", default=".", help="本地仓库路径，默认当前目录")
    parser.add_argument("--branch", default="main", help="推送分支，默认 main")
    parser.add_argument("--owner", default="", help="Gitee 用户名，缺省从 remote 解析")
    parser.add_argument("--name", default="", help="仓库名，缺省从 remote 解析")
    parser.add_argument("--remote-name", default="origin", help="解析 owner/name 用的 remote 名")
    parser.add_argument("--token-file", default="", help="令牌文件路径，缺省读环境变量或 ~/.gitee_token")
    parser.add_argument("--no-tags", action="store_true", help="不推标签")
    parser.add_argument("--allow-dirty", action="store_true", help="允许工作树有未提交改动")
    parser.add_argument("--dry-run", action="store_true", help="只比对，不推送")
    parser.add_argument("--json", action="store_true", help="只输出 JSON 回执")
    args = parser.parse_args(argv)

    repo_path = os.path.abspath(args.repo)
    if not os.path.isdir(repo_path):
        print("[FAIL] 仓库路径不存在：%s" % repo_path)
        return EXIT_GIT

    token, source = load_token(args.token_file or None)
    if not token:
        print("[FAIL] 找不到 Gitee 令牌：设 %s，或放到 ~/.gitee_token" % TOKEN_ENV)
        return EXIT_TOKEN

    owner, name = args.owner, args.name
    if not owner or not name:
        parsed_owner, parsed_name = resolve_slug(repo_path, args.remote_name)
        owner = owner or parsed_owner or ""
        name = name or parsed_name or ""
    if not owner or not name:
        print("[FAIL] 解析不出 owner/repo，请显式传 --owner 与 --name")
        return EXIT_GIT

    receipt, code = publish(
        repo_path=repo_path,
        branch=args.branch,
        owner=owner,
        name=name,
        token=token,
        push_tags=not args.no_tags,
        allow_dirty=args.allow_dirty,
        dry_run=args.dry_run,
        remote_name=args.remote_name,
    )
    receipt["token_source"] = source

    if args.json:
        print(json.dumps(receipt, ensure_ascii=False, indent=2))
    else:
        print("==> Gitee 直传 %s @ %s" % (receipt["repo"], receipt["branch"]))
        print("    local  : %s" % (receipt["local_sha"][:12] or "-"))
        print("    remote : %s -> %s" % (receipt["remote_before"][:12] or "(空)", receipt["remote_after"][:12] or "-"))
        print("    令牌   : %s (%s)" % (receipt["token"], source))
        print("    耗时   : %.2fs  标签=%s  校验=%s" % (
            receipt["elapsed_s"],
            "是" if receipt["tags_pushed"] else "否",
            "PASS" if receipt["verified"] else "FAIL",
        ))
        if receipt["error"]:
            print("    note   : %s" % receipt["error"])
        print("==> %s" % ("PASS" if receipt["verified"] or args.dry_run else "FAIL"))
    return code


if __name__ == "__main__":
    sys.exit(main())
