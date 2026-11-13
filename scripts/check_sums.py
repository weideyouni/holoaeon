# -*- coding: utf-8 -*-
"""check_sums — SHA256SUMS 复算闸（V38 引入；V78b 升级跨平台口径）
第一性原理：每个数字都能复算。闸只阻断不重建（重建=批次动作，
自动重建会掩盖追溯性）。改元文件→跑批次重建→闸放行。封口密语：潮起开门，潮落闭嘴。

V78b（P0-A / P0-B）两处升级：
  · P0-A 行尾归一化：文本文件按 **LF 字节口径** 哈希（CRLF 工作区与 Linux
    checkout 同一口径，本地绿=云端绿）；二进制文件按原字节。二进制后缀判定
    来自 .gitattributes 的 `*.xxx binary` 行，不在本文件硬编码——规则只有
    一份，闸与重建器（dual_sync.build_sums）各自解析同一份 .gitattributes。
  · P0-B 清单卫生：SHA256SUMS 里的条目必须是 git 已跟踪（index）且未被
    .gitignore 命中的文件。运行期产物（未跟踪 / 被忽略）一旦入清单，
    云端 checkout 上文件不存在，CI 必红——这条判据把「下次再混进去」
    从人肉对账变成机器拦截。git 不可用时这两项判据降级为不判并在结果中
    如实披露（git_unavailable），不冒充通过。

零依赖纯标准库（git 调用走 subprocess，仍属标准库）。
"""
import hashlib
import io
import json
import os
import subprocess
import sys

SEAL = "潮起开门，潮落闭嘴"


def _binary_patterns(root):
    """解析 .gitattributes：`*.zip binary` → 收集后缀 zip。规则唯一来源是仓库自身。"""
    p = os.path.join(root, ".gitattributes")
    out = []
    if not os.path.exists(p):
        return out
    try:
        with io.open(p, encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                s = line.strip()
                parts = s.split()
                if len(parts) == 2 and parts[0].startswith("*.") and parts[1] == "binary":
                    out.append(parts[0][2:])
    except OSError:
        pass
    return out


def _digest_file(fp, binary_exts):
    """P0-A 口径：文本文件 CRLF→LF 后哈希；二进制按原字节。"""
    with io.open(fp, "rb") as bf:
        raw = bf.read()
    name = os.path.basename(fp)
    ext = name.rsplit(".", 1)[1].lower() if "." in name else ""
    if ext not in binary_exts:
        raw = raw.replace(b"\r\n", b"\n")
    return hashlib.sha256(raw).hexdigest()


def _git_out(root, args, stdin_bytes=None):
    """跑一条 git 命令，返回 (rc, stdout_bytes)；失败返回 (None, b"")。"""
    try:
        proc = subprocess.run(
            ["git"] + args, cwd=root, input=stdin_bytes,
            capture_output=True, timeout=30,
        )
        return proc.returncode, proc.stdout
    except Exception:  # noqa: BLE001 —— OSError / timeout 都按不可用处理
        return None, b""


def _tracked_set(root):
    """git index 文件集合（ls-files 读 index：已 add 未 commit 也认，批次先闸后提交不断链）。"""
    rc, out = _git_out(root, ["-c", "core.quotepath=false", "ls-files", "-z"])
    if rc is None or rc != 0:
        return None
    return set(x for x in out.decode("utf-8", "replace").split("\0") if x)


def _ignored_list(root, files):
    """git check-ignore：返回 files 中被 .gitignore 命中的子集；git 不可用返回 None。"""
    if not files:
        return []
    stdin = "\0".join(files).encode("utf-8")
    rc, out = _git_out(root, ["check-ignore", "-z", "--stdin"], stdin)
    if rc is None or rc not in (0, 1):  # 0=有命中 1=无命中 128=错误
        return None
    return [x for x in out.decode("utf-8", "replace").split("\0") if x]


def verify(sums_path="SHA256SUMS", root=None):
    root = root or os.getcwd()
    mismatches, unreadable, untracked, ignored = [], [], [], []
    total = 0
    p = os.path.join(root, sums_path)
    if not os.path.exists(p):
        return {"ok": False, "error": "SHA256SUMS not found", "seal": SEAL}
    binary_exts = set(_binary_patterns(root))
    entries = []                                                # [(listed_hash, name)]
    with io.open(p, encoding="utf-8", errors="ignore") as fh:   # C-06 句柄 with
        for line in fh:
            parts = line.split()
            if len(parts) < 2:
                continue
            entries.append((parts[0], parts[-1]))
    total = len(entries)
    names = [n for _, n in entries]

    tracked = _tracked_set(root)
    ign = _ignored_list(root, names) if tracked is not None else None

    for listed, f in entries:
        fp = os.path.join(root, f)
        try:
            actual = _digest_file(fp, binary_exts)
        except Exception as e:                                 # noqa: BLE001
            unreadable.append({"file": f, "error": str(e)[:60]})
            continue
        if actual != listed:
            mismatches.append({"file": f, "listed": listed[:12],
                               "actual": actual[:12]})

    if tracked is not None:
        for f in names:
            if f not in tracked:
                untracked.append(f)
    if ign is not None:
        hit = set(ign)
        for f in names:
            if f in hit:
                ignored.append(f)

    ok = not (mismatches or unreadable or untracked or ignored)
    rep = {
        "ok": ok,
        "total": total,
        "mismatches": mismatches,
        "unreadable": unreadable,
        "action": "report_only",                                 # C-08 拆分，不作隐式拼接
        "action_note": "重建由批次流程执行，闸只阻断",
        "caliber": "lf_normalized_text_raw_binary",             # V78b P0-A 口径
        "seal": SEAL,
    }
    if tracked is None:
        rep["git"] = "unavailable（跟踪/忽略判据降级为不判，如实披露）"
    if untracked:
        rep["untracked"] = untracked
    if ignored:
        rep["ignored"] = ignored
    return rep


def main(argv):
    root = argv[1] if len(argv) > 1 else os.getcwd()
    r = verify("SHA256SUMS", root)
    print(json.dumps(r, ensure_ascii=False, indent=1))
    return 0 if r["ok"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
