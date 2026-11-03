# -*- coding: utf-8 -*-
"""V4.3 · S5 镜像器（HF model 仓专用，把踩过的四个坑固化进代码）。

为什么存在
----------
本仓在 Hugging Face 上是 **model 仓**（不是 dataset 仓）。用 `repo_type="dataset"` 会直接
404；`HfApi.model_info` 也不接受 `repo_type` 关键字。另外 `git diff --name-only` 默认会把
中文路径转义成 `\\346\\217\\222`，拿去当本地路径会报「不是本地文件」。这三处任一踩中，
镜像会静默半途失败或漏件。本脚本把口径写死：

1. `REPO_TYPE = "model"` 是唯一合法值，`upload_file` 用它，`model_info` **不传**它。
2. 取改动一律 `git -c core.quotepath=false`，路径保持 UTF-8 原文。
3. 判等用 git blob sha1（`sha1(b"blob %d\\0" + data)`），**不用** lfs.sha256。
4. 只推「本批改动里真实存在的文件」，回读后逐件比对，`mismatch` 非空即退出码 1。

用法
----
    python scripts/mirror_hf.py --base f50cd1c --head HEAD --check   # 只看计划
    python scripts/mirror_hf.py --base f50cd1c --head HEAD           # 推 + 回读

`--check` 不写远端；两种模式都输出一行 JSON（`verdict` / `changed` / `remote_files` / `sha` / `mismatch`）。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from typing import Any, Dict, Iterable, List, Optional, Tuple

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_TYPE = "model"
DEFAULT_REPO_ID = os.environ.get("HOLOAEON_HF_REPO", "weideyouni/holoaeon")


def blob_sha1(path: str) -> str:
    """git blob sha1：sha1(b"blob %d\\0" + data)。用于与 siblings[].blob_id 判等。"""
    with open(path, "rb") as f:
        data = f.read()
    h = hashlib.sha1()
    h.update(b"blob %d\0" % len(data))
    h.update(data)
    return h.hexdigest()


def changed_files(repo: str, base: str, head: str = "HEAD") -> List[str]:
    """取 base..head 的改动路径；强制关闭 git 的路径转义。"""
    out = subprocess.run(
        ["git", "-c", "core.quotepath=false", "diff", "--name-only", base, head],
        cwd=repo, capture_output=True, text=True, encoding="utf-8",
    )
    if out.returncode != 0:
        raise RuntimeError("git diff 失败: %s" % (out.stderr or "").strip())
    return [ln.strip() for ln in out.stdout.splitlines() if ln.strip()]


def build_plan(repo: str, rels: Iterable[str]) -> List[str]:
    """只保留在仓库里真实存在的文件（中文路径按 UTF-8 原文解析）。"""
    plan: List[str] = []
    for rel in rels:
        path = os.path.join(repo, rel.replace("/", os.sep))
        if os.path.isfile(path):
            plan.append(rel)
    return plan


def verify_remote(sib: Dict[str, Tuple[str, Optional[str]]], repo: str,
                  plan: Iterable[str]) -> List[str]:
    """逐件比对：普通文件用 git blob sha1 判等；LFS 文件用内容 sha256 判等。"""
    bad = []
    for rel in plan:
        path = os.path.join(repo, rel.replace("/", os.sep))
        if not os.path.isfile(path):
            continue
        blob, lfs_sha = sib.get(rel, (None, None))
        if lfs_sha:
            local = hashlib.sha256(open(path, "rb").read()).hexdigest()
            if local != lfs_sha:
                bad.append(rel)
        else:
            local = blob_sha1(path)
            if blob != local:
                bad.append(rel)
    return bad


def run(repo: str, base: str, head: str, check_only: bool, repo_id: str,
        token: Optional[str] = None) -> Dict[str, Any]:
    rels = changed_files(repo, base, head)
    plan = build_plan(repo, rels)
    skipped = [r for r in rels if r not in plan]
    if check_only:
        return {"verdict": "PLAN" if plan else "NO_CHANGE", "repo_type": REPO_TYPE,
                "repo_id": repo_id, "base": base, "head": head,
                "changed": plan, "skipped_missing": skipped}

    from huggingface_hub import HfApi  # 延迟导入：--check 不需要网络依赖

    api = HfApi(token=token) if token else HfApi()
    uploaded = []
    for rel in plan:
        api.upload_file(path_or_fileobj=os.path.join(repo, rel.replace("/", os.sep)),
                        path_in_repo=rel, repo_id=repo_id, repo_type=REPO_TYPE,
                        commit_message="sync %s..%s" % (base, head))
        uploaded.append(rel)
    info = api.model_info(repo_id, files_metadata=True)  # 注意：不传 repo_type
    sib: Dict[str, Tuple[str, Optional[str]]] = {}
    for s in info.siblings:
        lfs = getattr(s, "lfs", None)
        sib[s.rfilename] = (s.blob_id, lfs.sha256 if lfs else None)
    mismatch = verify_remote(sib, repo, plan)
    return {"verdict": "PASS" if not mismatch else "FAIL", "repo_type": REPO_TYPE,
            "repo_id": repo_id, "base": base, "head": head,
            "changed": plan, "uploaded": len(uploaded),
            "remote_files": len(sib), "sha": info.sha, "mismatch": mismatch}


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="HF model 仓差异镜像 + blob 回读判等")
    ap.add_argument("--repo", default=REPO_ROOT)
    ap.add_argument("--repo-id", default=DEFAULT_REPO_ID)
    ap.add_argument("--base", required=True)
    ap.add_argument("--head", default="HEAD")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--token-env", default="HF_TOKEN")
    args = ap.parse_args(argv)
    token = os.environ.get(args.token_env) or None
    res = run(args.repo, args.base, args.head, args.check, args.repo_id, token)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0 if res["verdict"] in ("PASS", "PLAN", "NO_CHANGE") else 1


if __name__ == "__main__":
    sys.exit(main())
