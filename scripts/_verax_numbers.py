# -*- coding: utf-8 -*-
"""VERAX 归档数字：目录行数、维度计数、pack 明细（只读，用于 README 与自证报告）。"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from holoaeon.audit import build_kernel  # noqa: E402
from holoaeon.packs import (EXTRA_PACK_ORDER, PACK_ORDER,  # noqa: E402
                            get_extra_pack, get_pack)
from holoaeon.redline import scan_directory  # noqa: E402


def install_all(kernel, keys, extra=False):
    for key in keys:
        pack = get_extra_pack(key) if extra else get_pack(key)
        pack.install(kernel)


def count_lines(folder):
    files, lines = 0, 0
    for dirpath, dirnames, filenames in os.walk(folder):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for name in filenames:
            if name.endswith(".py"):
                files += 1
                with io.open(os.path.join(dirpath, name), "r",
                             encoding="utf-8") as fh:
                    lines += len(fh.read().splitlines())
    return files, lines


def main():
    core = count_lines(os.path.join(ROOT, "holoaeon"))
    audit = count_lines(os.path.join(ROOT, "holoaeon", "audit"))
    packs = count_lines(os.path.join(ROOT, "holoaeon", "packs"))
    print("holoaeon/ 全部 py（含 audit、packs）:", core)
    print("  audit/:", audit)
    print("  packs/:", packs)
    print("红线扫描:", scan_directory(os.path.join(ROOT, "holoaeon"))["files_scanned"],
          "文件,", len(scan_directory(os.path.join(ROOT, "holoaeon"))["violations"]),
          "违规")

    rows = []
    k1 = build_kernel(packs=list(PACK_ORDER))
    print("九包：agents=%d skills=%d" % (len(k1.agents), len(k1.skills.names())))
    wf = sum(len(get_pack(p).workflows) for p in PACK_ORDER)
    print("九包 workflows=%d" % wf)

    k2 = build_kernel(packs=list(PACK_ORDER))
    install_all(k2, EXTRA_PACK_ORDER, extra=True)
    print("全装：agents=%d skills=%d workflows=%d"
          % (len(k2.agents), len(k2.skills.names()),
             wf + sum(len(get_extra_pack(p).workflows) for p in EXTRA_PACK_ORDER)))
    for key in PACK_ORDER:
        pack = get_pack(key)
        info = pack.install(build_kernel(packs=[]))
        rows.append({"pack": key, "kind": "domain",
                     "skills": len(info["skills"]),
                     "agents": len(info["agents"]),
                     "workflows": len(info["workflows"])})
    for key in EXTRA_PACK_ORDER:
        pack = get_extra_pack(key)
        info = pack.install(build_kernel(packs=[]))
        rows.append({"pack": key, "kind": "extra",
                     "skills": len(info["skills"]),
                     "agents": len(info["agents"]),
                     "workflows": len(info["workflows"])})
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                       "reports", "verax_numbers.json")
    with io.open(out, "w", encoding="utf-8") as fh:
        json.dump({"core": core, "audit": audit, "packs": packs,
                   "packs_table": rows}, fh, ensure_ascii=False, indent=2)
    print("[saved]", os.path.abspath(out))


if __name__ == "__main__":
    main()
