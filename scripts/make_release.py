# -*- coding: utf-8 -*-
"""幂等打包发布 zip（平铺仓库内容），排除 __pycache__、*.pyc 与飞书入库入口文档。

用法：
    python scripts/make_release.py [版本号] [输出zip路径]

默认版本号取自 holoaeon.spec.VERSION，输出到 F:\\doubaowork\\holoaeon_v<version>_<date>.zip。
注意：飞书入库入口文档（HoloAeon_入库入口_全文.md）是独立产物，不打入代码包，
这样入口文档里记录的 zip SHA256 才能稳定（避免自引用）。
"""
import hashlib
import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EXCLUDE_DIRS = {"__pycache__", ".git", ".pytest_cache"}
EXCLUDE_FILES = {"HoloAeon_入库入口_全文.md"}
EXCLUDE_SUFFIX = (".pyc", ".pyo")


def collect_files():
    out = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for name in filenames:
            if name in EXCLUDE_FILES or name.endswith(EXCLUDE_SUFFIX):
                continue
            abs_p = os.path.join(dirpath, name)
            rel_p = os.path.relpath(abs_p, ROOT).replace(os.sep, "/")
            out.append((abs_p, rel_p))
    return sorted(out, key=lambda x: x[1])


def main():
    version = sys.argv[1] if len(sys.argv) > 1 else None
    if version is None:
        sys.path.insert(0, ROOT)
        from holoaeon.spec import VERSION, DATE
        version = VERSION
        date = DATE.replace("-", "")
    else:
        date = "20261029"
    out_zip = (sys.argv[2] if len(sys.argv) > 2
               else os.path.join(os.path.dirname(ROOT),
                                 "holoaeon_v%s_%s.zip" % (version, date)))
    files = collect_files()
    if os.path.exists(out_zip):
        os.remove(out_zip)
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for abs_p, rel_p in files:
            zf.write(abs_p, rel_p)
    data = open(out_zip, "rb").read()
    sha = hashlib.sha256(data).hexdigest()
    print("zip:", out_zip)
    print("files:", len(files))
    print("size:", len(data), "B")
    print("sha256:", sha.upper())


if __name__ == "__main__":
    main()
