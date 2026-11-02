# -*- coding: utf-8 -*-
"""向量海（S4）归档清单自检：manifest 条目必须与目录实际文件一一对应。

背景：B3 归档时曾出现"目录 39 个文件、清单只有 35 条"，少的正好是 3 个新条目 +
README，而回执照样写 PASS——这类缺项是静默的，必须用差集判。

用法：
  python scripts/check_vector_sea_manifest.py            # 默认 S4 路径
  python scripts/check_vector_sea_manifest.py --dir <S4> # 指定目录
退出码 0 = 清单与目录一致；1 = 有缺项/多项/哈希不符。
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_S4 = r"F:\doubaowork\vector-sea\holoaeon-v4-cold-hot-plug"
MANIFEST = "manifest.json"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv):
    target = DEFAULT_S4
    if "--dir" in argv:
        target = argv[argv.index("--dir") + 1]
    mf = os.path.join(target, MANIFEST)
    if not os.path.isfile(mf):
        print(json.dumps({"verdict": "FAIL", "reason": "manifest 缺失"}, ensure_ascii=False))
        return 1
    with open(mf, encoding="utf-8") as f:
        man = json.load(f)
    files = sorted(n for n in os.listdir(target)
                   if os.path.isfile(os.path.join(target, n)) and n != MANIFEST)
    missing = [n for n in files if n not in man]
    extra = [n for n in man if n not in files]
    bad_hash = [n for n in files if n in man
                and man[n].get("sha256") != sha256(os.path.join(target, n))]
    bad_bytes = [n for n in files if n in man
                 and man[n].get("bytes") != os.path.getsize(os.path.join(target, n))]
    ok = not (missing or extra or bad_hash or bad_bytes)
    print(json.dumps({"verdict": "PASS" if ok else "FAIL", "dir": target,
                      "manifest_entries": len(man), "dir_files": len(files),
                      "missing": missing, "extra": extra,
                      "bad_sha256": bad_hash[:5], "bad_bytes": bad_bytes[:5]},
                     ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
