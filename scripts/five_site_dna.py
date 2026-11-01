"""五地同步 DNA 校验器 · V1.1（纯标准库 / 离线 / 不调用 git / 不联网 / 不写文件）。

用法：
  python scripts/five_site_dna.py build       # 生成 reports/five_site_manifest.json
  python scripts/five_site_dna.py verify      # 复算并与清单比对，输出漂移清单
  python scripts/five_site_dna.py preflight   # 开工前置检测（P1–P6），PASS 才允许开批

设计原则（对应 data/FIVE_SITE_SYNC_DNA.md 的 R3 / R8 / G1 / P1–P6）：
  1. 只读文件字节算 sha256，不做任何写操作（verify / preflight 模式）
  2. 路径全部来自显式参数或环境变量，不猜
  3. 输出稳定排序，两次跑逐字一致；不写时间戳
"""

import hashlib
import json
import os
import sys

REPO = os.environ.get("HOLOAEON_REPO", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PKG = os.environ.get("HOLOAEON_PKG", r"F:\doubaowork\HoloAeon_V4冷热插拔赋能升级_20261102")
RECEIPT = os.environ.get("HOLOAEON_RECEIPT",
                         r"F:\doubaowork\vector-sea\_holoaeon_v4_five_site_receipt_20261102.json")
MANIFEST = os.path.join(REPO, "reports", "five_site_manifest.json")

DNA_ID = "SG-DNA-FIVE-SITE-SYNC-V1.1"
LOCK = {"agents": 25, "skills": 47, "packs": 9}

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
GATE_PRE = os.path.join(REPO, "reports", "gate_b0_v4.json")
PROGRESS_CSV = os.path.join(REPO, "data", "B0_批次进度.csv")


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


def drift_now():
    """返回 (drift 列表, 当前采集结果, 旧清单)。清单不存在时 drift 视为未验证。"""
    if not os.path.isfile(MANIFEST):
        return None, None, None
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
    return sorted(drift), now, old


def build():
    data = collect()
    doc = {
        "dna_id": DNA_ID,
        "built_at": "2026-11-02T02:40+08:00",
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
    drift, now, old = drift_now()
    if drift is None:
        print("manifest 不存在，先跑 build")
        return 1
    payload = {
        "verdict": "PASS" if not drift else "FAIL",
        "checked": {"package": len(now["package"]), "repo": len(now["repo"])},
        "drift": drift,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not drift else 1


def preflight():
    """开工前置检测 P1–P6。任一 FAIL → 退出码 1，禁止开批。"""
    checks = []

    def add(pid, ok, detail):
        checks.append({"id": pid, "ok": bool(ok), "detail": detail})

    drift, now, old = drift_now()

    # P1 清单存在且可复算
    add("P1", drift is not None and not drift,
        "drift={}".format(len(drift)) if drift is not None else "manifest missing")

    # P2 文件齐 + 整包在位
    missing = (now or {}).get("missing", [])
    has_zip = ZIP_NAME in (now or {}).get("package", {})
    add("P2", not missing and has_zip, "missing={} zip={}".format(len(missing), has_zip))

    # P3 开工前闸证据
    ok3, det3 = False, "gate file missing"
    if os.path.isfile(GATE_PRE):
        try:
            g = json.load(open(GATE_PRE, encoding="utf-8"))
            ok3 = int(g.get("passed", -1)) == int(g.get("total", -2)) == 32 and not g.get("failed")
            det3 = "{}/{} failed={}".format(g.get("passed"), g.get("total"), len(g.get("failed") or []))
        except Exception as exc:  # 不是静默吞错，写进 detail
            det3 = "unreadable: " + type(exc).__name__
    add("P3", ok3, det3)

    # P4 五地回执在位且 PASS
    ok4, det4 = False, "receipt missing"
    if os.path.isfile(RECEIPT):
        try:
            r = json.load(open(RECEIPT, encoding="utf-8"))
            verdict = str((r.get("gates") or {}).get("verdict", ""))
            readme_ok = bool((r.get("readme_status") or {}).get("all_five_updated", False))
            ok4 = "PASS" in verdict and readme_ok
            det4 = "gates='{}' all_five_updated={}".format(verdict, readme_ok)
        except Exception as exc:
            det4 = "unreadable: " + type(exc).__name__
    add("P4", ok4, det4)

    # P5 批次节奏：进行中 ≤1，且 B0 已完成
    ok5, det5 = False, "progress csv missing"
    if os.path.isfile(PROGRESS_CSV):
        rows = []
        with open(PROGRESS_CSV, encoding="utf-8") as f:
            head = f.readline().strip().split(",")
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rows.append(line)
        inprog = 0
        b0_done = False
        for line in rows:
            parts = line.split(",")
            if len(parts) >= 3:
                if parts[2].strip() == "进行中":
                    inprog += 1
                if parts[0].strip() == "B0" and parts[2].strip() == "已完成":
                    b0_done = True
        ok5 = inprog <= 1 and b0_done
        det5 = "in_progress={} b0_done={} rows={}".format(inprog, b0_done, len(rows))
    add("P5", ok5, det5)

    # P6 DNA 版本一致
    ok6 = bool(old) and old.get("dna_id") == DNA_ID
    add("P6", ok6, "manifest dna_id={}".format((old or {}).get("dna_id")))

    verdict = "PASS" if all(c["ok"] for c in checks) else "FAIL"
    payload = {
        "dna_id": DNA_ID,
        "verdict": verdict,
        "failed": [c["id"] for c in checks if not c["ok"]],
        "checks": checks,
        "lock": LOCK,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if verdict == "PASS" else 1


def main(argv):
    mode = argv[1] if len(argv) > 1 else "build"
    if mode == "build":
        build()
        return 0
    if mode == "verify":
        return verify()
    if mode == "preflight":
        return preflight()
    print("用法: python scripts/five_site_dna.py build|verify|preflight")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
