"""B9 收口打包器 · 纯标准库 / 离线 / 确定性 zip。

用法：python scripts/build_b9_zip.py [--check]

规则：
  1. 只打交付目录（HOLOAEON_PKG，默认 F:\\doubaowork\\HoloAeon_V4冷热插拔赋能升级_20261102）
  2. 排除 zip 自身与 __pycache__，其余按相对路径排序写入
  3. 固定时间戳（1980-01-01 00:00）与固定压缩级别 → 同内容两次打包 sha256 一致
  4. 不打印绝对路径（便于日志留档）
"""

import hashlib
import json
import os
import sys
import zipfile

PKG = os.environ.get("HOLOAEON_PKG", r"F:\doubaowork\HoloAeon_V4冷热插拔赋能升级_20261102")
ZIP_NAME = "holoaeon_v4_fusion_upgrade_20261102.zip"
FIXED_DATE = (1980, 1, 1, 0, 0, 0)


def iter_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d != "__pycache__")
        for name in sorted(filenames):
            abs_path = os.path.join(dirpath, name)
            rel = os.path.relpath(abs_path, root).replace(os.sep, "/")
            if rel == ZIP_NAME or name.endswith(".pyc"):
                continue
            yield rel, abs_path


def build(root=None, out=None):
    root = root or PKG
    out = out or os.path.join(root, ZIP_NAME)
    entries = []
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for rel, abs_path in iter_files(root):
            info = zipfile.ZipInfo(rel, date_time=FIXED_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, open(abs_path, "rb").read())
            entries.append(rel)
    h = hashlib.sha256(open(out, "rb").read()).hexdigest()
    return {"zip": ZIP_NAME, "entries": len(entries), "bytes": os.path.getsize(out),
            "sha256": h, "sha16": h[:16], "names": entries}


def main():
    argv = sys.argv[1:]
    result = build()
    if "--check" in argv:
        again = build()
        if again["sha256"] != result["sha256"]:
            print(json.dumps({"verdict": "FAIL", "reason": "non-deterministic zip"}, ensure_ascii=False))
            return 1
        result["deterministic"] = True
    print(json.dumps({k: v for k, v in result.items() if k != "names"}, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
