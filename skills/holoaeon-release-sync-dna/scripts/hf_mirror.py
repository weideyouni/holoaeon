#!/usr/bin/env python
"""HF 镜像器：把本地 Git 提交（不是工作树）镜像到 Hugging Face 代码仓 / Space。

用法（需要 `huggingface_hub`，令牌由 CLI 登录态自动提供）：

    python scripts/hf_mirror.py --repo <本地仓库> --name holoaeon --verify all
    python scripts/hf_mirror.py --repo <本地仓库> --name holoaeon --space-dir <静态页目录>
    python scripts/hf_mirror.py --repo <本地仓库> --name holoaeon --check-only

设计口径：
- 只镜像 `git archive HEAD` 的内容，绝不镜像工作树 —— 工作树脏时也不会把未提交改动推上去。
- 推送后必须回读：文件数一致 + 抽样/全量 sha256 与本地逐字节相同，才算 verified。
- 令牌只走 huggingface_hub 的登录态（~/.cache/huggingface/token），不落命令行、不落仓库。
"""

import argparse
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time

EXIT_OK = 0
EXIT_DEPS = 2
EXIT_GIT = 3
EXIT_VERIFY = 4


def git(repo, *args):
    proc = subprocess.run(["git", "-C", repo] + list(args),
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if proc.returncode != 0:
        raise RuntimeError(proc.stdout.decode("utf-8", "replace")[:400])
    return proc.stdout.decode("utf-8", "replace")


def head_of(repo):
    return git(repo, "rev-parse", "HEAD").strip()


def tracked_count(repo):
    return len(git(repo, "ls-files").splitlines())


def stage_from_head(repo, dest):
    """把 HEAD 的树解到 dest，返回文件清单。"""
    raw = subprocess.run(["git", "-C", repo, "archive", "--format=tar", "HEAD"],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if raw.returncode != 0:
        raise RuntimeError(raw.stderr.decode("utf-8", "replace")[:400])
    names = []
    with tarfile.open(fileobj=io.BytesIO(raw.stdout), mode="r:") as tar:
        for member in tar.getmembers():
            if not member.isfile():
                continue
            src = tar.extractfile(member)
            target = os.path.join(dest, member.name.replace("/", os.sep))
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, "wb") as fh:
                fh.write(src.read())
            names.append(member.name)
    return names


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def pick_samples(names, k):
    if k <= 0 or k >= len(names):
        return list(names)
    step = max(1, len(names) // k)
    return names[::step][:k]


def main(argv=None):
    ap = argparse.ArgumentParser(description="本地 Git 提交 → Hugging Face 镜像（带逐字节校验）")
    ap.add_argument("--repo", required=True)
    ap.add_argument("--name", default="holoaeon", help="HF 代码仓名")
    ap.add_argument("--owner", default="", help="HF 用户名，缺省用登录态")
    ap.add_argument("--private", action="store_true")
    ap.add_argument("--space-dir", default="", help="静态 Space 目录（含 index.html + README.md）")
    ap.add_argument("--space-name", default="", help="Space 名，缺省 <name>-demo")
    ap.add_argument("--check-only", action="store_true")
    ap.add_argument("--verify", default="sample", choices=["sample", "all", "none"])
    ap.add_argument("--sample", type=int, default=7)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    try:
        from huggingface_hub import HfApi, hf_hub_download
    except Exception as exc:  # noqa: BLE001
        print("[FAIL] 需要 huggingface_hub：%s" % exc)
        return EXIT_DEPS

    repo = os.path.abspath(args.repo)
    receipt = {"repo": repo, "head": "", "tracked": 0, "code_repo": "", "space": "",
               "uploaded": False, "remote_files": 0, "agree": "", "verified": False,
               "error": ""}
    try:
        head = head_of(repo)
        receipt["head"] = head
        receipt["tracked"] = tracked_count(repo)
    except Exception as exc:  # noqa: BLE001
        receipt["error"] = "读本地仓库失败：%s" % exc
        print(json.dumps(receipt, ensure_ascii=False))
        return EXIT_GIT

    api = HfApi()
    me = api.whoami()
    owner = args.owner or me["name"]
    code_repo = "%s/%s" % (owner, args.name)
    space_repo = "%s/%s" % (owner, args.space_name or (args.name + "-demo"))
    receipt["code_repo"] = "https://huggingface.co/" + code_repo
    if args.space_dir:
        receipt["space"] = "https://huggingface.co/spaces/" + space_repo

    stage = tempfile.mkdtemp(prefix="hf_mirror_")
    try:
        names = stage_from_head(repo, stage)
        sample_list = pick_samples(names, 0 if args.verify == "all" else args.sample)
        print("[i] HEAD=%s tracked=%d staged=%d verify=%s(%d)"
              % (head[:12], receipt["tracked"], len(names), args.verify, len(sample_list)))

        if not args.check_only:
            api.create_repo(repo_id=code_repo, repo_type="model", private=args.private, exist_ok=True)
            api.upload_folder(repo_id=code_repo, repo_type="model", folder_path=stage,
                              commit_message="mirror: %s (%s, %d files)" % (code_repo, head[:12], len(names)))
            receipt["uploaded"] = True

            if args.space_dir:
                space_dir = os.path.abspath(args.space_dir)
                api.create_repo(repo_id=space_repo, repo_type="space", space_sdk="static",
                                private=args.private, exist_ok=True)
                api.upload_folder(repo_id=space_repo, repo_type="space", folder_path=space_dir,
                                  commit_message="facade: static page @ %s" % head[:12])

        remote = api.list_repo_files(code_repo, repo_type="model")
        receipt["remote_files"] = len(remote)
        local_set = set(names)
        missing = sorted(local_set - set(remote))
        extra = sorted(set(remote) - local_set)

        if args.verify == "none":
            receipt["verified"] = not missing
            receipt["agree"] = "skipped"
        else:
            cache = os.path.join(tempfile.gettempdir(), "hf_mirror_cache")
            ok = 0
            failed_files = []
            for rel in sample_list:
                local_path = os.path.join(stage, rel.replace("/", os.sep))
                remote_path = ""
                last_exc = None
                for attempt in range(3):  # 本机到 HF 偶发 SSL EOF，单文件重试即可
                    try:
                        remote_path = hf_hub_download(repo_id=code_repo, filename=rel, cache_dir=cache)
                        break
                    except Exception as exc:  # noqa: BLE001
                        last_exc = exc
                        time.sleep(1 + attempt * 3)
                if not remote_path:
                    failed_files.append("%s (%s)" % (rel, str(last_exc)[:60]))
                    print("  RETRY-FAIL " + rel)
                    continue
                same = sha256_file(local_path) == sha256_file(remote_path)
                ok += same
                if args.verify != "all" or not same:
                    print(("  OK   " if same else "  DIFF ") + rel)
            receipt["agree"] = "%d/%d" % (ok, len(sample_list))
            receipt["verified"] = ok == len(sample_list) and not missing
            if failed_files:
                receipt["error"] = "下载失败 %d 个：%s" % (len(failed_files), failed_files[:3])

        if missing:
            receipt["error"] = "远端缺 %d 个文件：%s" % (len(missing), missing[:3])
        elif extra:
            receipt["error"] = receipt["error"] or "远端多 %d 个文件：%s" % (len(extra), extra[:3])
    finally:
        shutil.rmtree(stage, ignore_errors=True)

    if args.json:
        print(json.dumps(receipt, ensure_ascii=False))
    else:
        print("==> HF 镜像 %s @ %s" % (code_repo, receipt["head"][:12]))
        print("    tracked/remote : %d / %d" % (receipt["tracked"], receipt["remote_files"]))
        print("    byte agree     : %s" % receipt["agree"])
        if receipt["space"]:
            print("    space          : %s" % receipt["space"])
        if receipt["error"]:
            print("    note           : %s" % receipt["error"])
        print("==> %s" % ("PASS" if receipt["verified"] else "FAIL"))
    return EXIT_OK if receipt["verified"] else EXIT_VERIFY


if __name__ == "__main__":
    sys.exit(main())
