# -*- coding: utf-8 -*-
"""B8 构建器：出 ivsa v1.2 插件描述、双仓 SHA256SUMS、互认件与许可分层清单。

只读两仓文件 + 写 data/ 与 reports/，不动源码、不加技能、不改 25/47/9。

用法：
  python scripts/build_b8_dual_sync.py
"""
from __future__ import annotations

import csv
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from holoaeon.fusion_upgrade import dual_sync as DS  # noqa: E402

IVSA_ROOT = r"F:\doubaowork\开源发布_中西医融合康复工程_20261026\integrative-rehab-vsa"
DATA = os.path.join(ROOT, "data")
REPORTS = os.path.join(ROOT, "reports")
SUMS_PATH = os.path.join(ROOT, "SHA256SUMS")


def _tracked_files(root: str):
    """git index 文件集合（V78b：清单只绑已跟踪文件；git 不可用直接失败，宁可响不可错）。"""
    proc = subprocess.run(
        ["git", "-c", "core.quotepath=false", "ls-files", "-z", "--"],
        cwd=root, capture_output=True, timeout=60,
    )
    if proc.returncode != 0:
        raise RuntimeError("git ls-files 失败，无法判定受管目录的跟踪边界")
    return set(x for x in proc.stdout.decode("utf-8", "replace").split("\0") if x)


def release_files(root: str):
    """V78b：只收 git 已跟踪文件——未跟踪运行期产物（daily_* / gate 临时件）一律不入清单。"""
    tracked = _tracked_files(root)
    files = []
    for top in ("data", "reports", "holoaeon/fusion_upgrade", "tests_contract", "scripts"):
        base = os.path.join(root, *top.split("/"))
        if not os.path.isdir(base):
            continue
        for dirpath, _dirs, names in os.walk(base):
            for name in names:
                if not name.endswith((".py", ".json", ".csv", ".md")):
                    continue
                rel = os.path.relpath(os.path.join(dirpath, name), root).replace(os.sep, "/")
                if rel not in tracked:
                    continue
                files.append(rel)
    return files


def main() -> int:
    desc = DS.plugin_descriptor()
    with open(os.path.join(DATA, "ivsa_plugin_v1.2.json"), "w", encoding="utf-8",
              newline="\n") as f:
        json.dump(desc, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")

    layers = DS.license_layers()
    with open(os.path.join(DATA, "许可分层清单.csv"), "w", encoding="utf-8",
              newline="\n") as f:
        writer = csv.DictWriter(f, fieldnames=["repo", "layer", "license",
                                               "allowed_in_host", "allowed_in_guest", "note"])
        writer.writeheader()
        for row in layers:
            writer.writerow({k: row.get(k, "") for k in writer.fieldnames})

    # 宿主清单（先算，供互认件记录摘要）
    holo_files = release_files(ROOT)
    holo_lines = DS.build_sums(ROOT, holo_files)
    with open(SUMS_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(holo_lines) + "\n")

    # ivsa 侧：读它自己的 SHA256SUMS，逐件复算（只读，不写对方仓）
    ivsa_sums = os.path.join(IVSA_ROOT, "SHA256SUMS")
    ivsa_text = ""
    ivsa_ctrl = {"ok": False, "checked": 0, "missing": ["SHA256SUMS"], "bad_sha256": []}
    if os.path.isfile(ivsa_sums):
        with open(ivsa_sums, "r", encoding="utf-8") as f:
            ivsa_text = f.read()
        ivsa_ctrl = DS.verify_sums(IVSA_ROOT, ivsa_text)
        ivsa_ctrl["extra"] = []  # 对方仓扫不到同款受管目录，不判 extra

    iface = DS.interface_check(
        os.path.join(ROOT, DS.INTERFACE["holo"]),
        os.path.join(IVSA_ROOT, DS.INTERFACE["ivsa"]),
    )

    mixed = DS.license_mixed(layers)
    doc = {
        "sums_id": "SG-B8-DUAL-REPO-SUMS-V1",
        "batch": DS.BATCH,
        "evidence_class": DS.EVIDENCE_CLASS,
        "generated_at": "2026-11-14",  # V78b 重建：P0-A LF 口径 + P0-B 移出 5 条运行期产物
        "holoaeon": {
            "root": ROOT.replace(os.sep, "/"),
            "manifest": "SHA256SUMS",
            "entries": len(holo_lines),
            "sums_sha256": DS.sums_digest(holo_lines),
            "excludes": list(DS.SUMS_EXCLUDES),
            "exclude_reason": "清单自身与派生件不入清单，避免自指循环；"
                              "V78b 起另排除 5 条运行期产物（3 未跟踪 + 2 gitignore）",
            "v78b_note": "P0-A：文本文件 LF 归一化口径（CRLF 工作区与 Linux checkout 同清单）；"
                         "P0-B：运行期产物移出（旧清单 251 条中在列的 5 条）+ 重建只收 git 已跟踪文件"
                         "（追平 V 系批次新增的已跟踪件），251→332",
        },
        "ivsa": {
            "root": IVSA_ROOT.replace(os.sep, "/"),
            "manifest": "SHA256SUMS",
            "entries": len(DS.parse_sums(ivsa_text)),
            "sums_sha256": DS.sums_digest([l for l in ivsa_text.splitlines() if l.strip()]),
            "recompute": ivsa_ctrl,
        },
        "interface": {
            "holo_file": DS.INTERFACE["holo"],
            "ivsa_file": DS.INTERFACE["ivsa"],
            "expected_total": DS.INTERFACE["total"],
            "result": iface,
        },
        "license_layering": {
            "rows": len(layers),
            "mixed": mixed,
            "file": "data/许可分层清单.csv",
        },
        "plugin": {
            "file": "data/ivsa_plugin_v1.2.json",
            "plugin_id": desc["plugin_id"],
            "enabled_by_default": desc["enabled_by_default"],
            "seal": desc["seal"],
        },
    }
    verdict_ok = (
        bool(iface["equal"])
        and ivsa_ctrl["ok"]
        and not mixed
        and desc["enabled_by_default"] is False
    )
    doc["verdict"] = "PASS" if verdict_ok else "FAIL"
    # 自摘要放在数据件末尾，不参与验收（避免又一轮自指）
    with open(os.path.join(DATA, "dual_repo_sums.json"), "w", encoding="utf-8",
              newline="\n") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")

    receipt = {
        "batch": DS.BATCH,
        "id": "SG-B8-DUAL-SYNC-RECEIPT-V1",
        "verdict": doc["verdict"],
        "holo_entries": doc["holoaeon"]["entries"],
        "holo_sums_sha256": doc["holoaeon"]["sums_sha256"],
        "ivsa_entries": doc["ivsa"]["entries"],
        "ivsa_recompute_ok": bool(ivsa_ctrl["ok"]),
        "ivsa_checked": ivsa_ctrl["checked"],
        "interface_equal": bool(iface["equal"]),
        "groups": iface["groups_holo_mapped"],
        "license_rows": len(layers),
        "license_mixed": mixed,
        "plugin_disabled_by_default": bool(desc["enabled_by_default"] is False),
        "dimension_contract": dict(DS.DIMENSION_CONTRACT),
    }
    receipt["seal"] = DS.canonical_digest(receipt)
    with open(os.path.join(REPORTS, "b8_dual_sync.json"), "w", encoding="utf-8",
              newline="\n") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")

    print(json.dumps({"verdict": doc["verdict"], "holo_entries": len(holo_lines),
                      "ivsa_entries": doc["ivsa"]["entries"],
                      "ivsa_recompute_ok": ivsa_ctrl["ok"],
                      "interface_equal": iface["equal"], "groups": iface["groups_holo_mapped"],
                      "license_mixed": mixed,
                      "plugin_default_off": desc["enabled_by_default"] is False},
                     ensure_ascii=False))
    return 0 if verdict_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
