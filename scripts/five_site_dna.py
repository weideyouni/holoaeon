"""五地同步 DNA 校验器（纯标准库 / 离线 / 不调用 git / 不联网）。

用法：
  python scripts/five_site_dna.py build    # 生成 reports/five_site_manifest.json
  python scripts/five_site_dna.py verify   # 复算并与清单比对，输出漂移清单

设计原则（对应 data/FIVE_SITE_SYNC_DNA.md 的 R3 / R8）：
  1. 只读文件字节算 sha256，不做任何写操作（verify 模式）
  2. 路径全部来自显式参数或环境变量，不猜
  3. 输出稳定排序，两次跑逐字一致
"""

import hashlib
import json
import os
import sys

REPO = os.environ.get("HOLOAEON_REPO", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PKG = os.environ.get("HOLOAEON_PKG", r"F:\doubaowork\HoloAeon_V4冷热插拔赋能升级_20261102")
MANIFEST = os.path.join(REPO, "reports", "five_site_manifest.json")

PKG_FILES = [
    "01_V4赋能升级总策划.md",
    "02_一键复制投喂包_面向智能体.md",
    "03_内外融合协议与冷热插拔SOP.md",
    "04_项目快照.json",
    "05_README_V4_赋能升级.md",
    "06_验收票据.md",
    "data/B0_基线票据_v4fusion.md",
    "data/B0_自动匹配技能.csv",
    "data/B0_批次进度.csv",
    "data/十二批台账.csv",
    "data/冷热插拔清单.csv",
    "data/六机制对照与通道映射.csv",
    "data/全域技能匹配清单.csv",
    "reports/b0_lock_v4fusion.json",
    "reports/fusion_selftest.json",
]

REPO_FILES = [
    "README_FUSION_V4_20261102.md",
    "data/B0_基线票据_v4fusion.md",
    "data/B0_自动匹配技能.csv",
    "data/B0_批次进度.csv",
    "data/five_site_dna.json",
    "data/FIVE_SITE_SYNC_DNA.md",
    "reports/b0_lock_v4fusion.json",
    "reports/gate_b0_v4.json",
    "scripts/b0_match.py",
    "scripts/five_site_dna.py",
]

ZIP_NAME = "holoaeon_v4_fusion_upgrade_20261102.zip"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def collect():
    out = {"package": {}, "repo": {}, "missing": []}
    for rel in PKG_FILES:
        p = os.path.join(PKG, rel.replace("/", os.sep))
        if not os.path.isfile(p):
            out["missing"].append("pkg:" + rel)
            continue
        out["package"][rel] = {"bytes": os.path.getsize(p), "sha256": sha256_file(p)}
    zp = os.path.join(PKG, ZIP_NAME)
    if os.path.isfile(zp):
        s = sha256_file(zp)
        out["package"][ZIP_NAME] = {"bytes": os.path.getsize(zp), "sha256": s, "sha16": s[:16]}
    else:
        out["missing"].append("pkg:" + ZIP_NAME)
    for rel in REPO_FILES:
        p = os.path.join(REPO, rel.replace("/", os.sep))
        if not os.path.isfile(p):
            out["missing"].append("repo:" + rel)
            continue
        out["repo"][rel] = {"bytes": os.path.getsize(p), "sha256": sha256_file(p)}
    return out


def build():
    data = collect()
    doc = {
        "dna_id": "SG-DNA-FIVE-SITE-SYNC-V1.0",
        "built_at": "2026-11-02T01:42+08:00",
        "evidence_class": "simulated",
        "seal": "潮起开门，潮落闭嘴",
        "package_root": PKG,
        "repo_root": REPO,
        "counts": {"package": len(data["package"]), "repo": len(data["repo"]), "missing": len(data["missing"])},
        "package": dict(sorted(data["package"].items())),
        "repo": dict(sorted(data["repo"].items())),
        "missing": sorted(data["missing"]),
    }
    os.makedirs(os.path.dirname(MANIFEST), exist_ok=True)
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    print(json.dumps({"manifest": MANIFEST, "counts": doc["counts"], "zip_sha16":
                      doc["package"].get(ZIP_NAME, {}).get("sha16", "")}, ensure_ascii=False))


def verify():
    if not os.path.isfile(MANIFEST):
        print("manifest 不存在，先跑 build")
        return 1
    with open(MANIFEST, encoding="utf-8") as f:
        old = json.load(f)
    now = collect()
    drift = []
    for scope in ("package", "repo"):
        for rel, meta in old.get(scope, {}).items():
            cur = now[scope].get(rel)
            if cur is None:
                drift.append(scope + ":missing:" + rel)
            elif cur["sha256"] != meta["sha256"] or cur["bytes"] != meta["bytes"]:
                drift.append(scope + ":changed:" + rel)
        for rel in now[scope]:
            if rel not in old.get(scope, {}):
                drift.append(scope + ":new:" + rel)
    payload = {
        "verdict": "PASS" if not drift else "FAIL",
        "checked": {"package": len(now["package"]), "repo": len(now["repo"])},
        "drift": sorted(drift),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not drift else 1


def main(argv):
    mode = argv[1] if len(argv) > 1 else "build"
    if mode == "build":
        build()
        return 0
    if mode == "verify":
        return verify()
    print("用法: python scripts/five_site_dna.py build|verify")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
