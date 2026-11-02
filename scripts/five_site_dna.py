"""五地同步 DNA 校验器 · V1.2（纯标准库 / 离线 / 不调用 git / 不联网 / 不写文件）。

用法：
  python scripts/five_site_dna.py build       # 生成 reports/five_site_manifest.json
  python scripts/five_site_dna.py verify      # 复算并与清单比对，输出漂移清单
  python scripts/five_site_dna.py preflight   # 开工前置检测（P1–P7），PASS 才允许开批

设计原则（对应 data/FIVE_SITE_SYNC_DNA.md 的 R3 / R8 / G1 / P1–P7）：
  1. 只读文件字节算 sha256，不做任何写操作（verify / preflight 模式）
  2. 路径全部来自显式参数或环境变量，不猜
  3. 输出稳定排序，两次跑逐字一致；不写时间戳
"""

import hashlib
import json
import os
import re
import sys

REPO = os.environ.get("HOLOAEON_REPO", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PKG = os.environ.get("HOLOAEON_PKG", r"F:\doubaowork\HoloAeon_V4冷热插拔赋能升级_20261102")
RECEIPT = os.environ.get("HOLOAEON_RECEIPT",
                         r"F:\doubaowork\vector-sea\_holoaeon_v4_five_site_receipt_20261102.json")
MANIFEST = os.path.join(REPO, "reports", "five_site_manifest.json")

DNA_ID = "SG-DNA-FIVE-SITE-SYNC-V1.2"
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
    "data/FIVE_SITE_SYNC_DNA.md",
    "data/ivsa_plugin_v1.2.json",
    "data/dual_repo_sums.json",
    "data/许可分层清单.csv",
    "data/B8_双仓开源同步票据.md",
    "data/B9_融合总策划_v2.md",
    "data/B9_批次台账_v2.csv",
    "data/B9_完美融合判据.md",
    "data/B9_风险与回滚登记.md",
    "data/B9_四透镜评审意见.md",
    "data/B9_收口票据.md",
    "reports/b0_lock_v4fusion.json",
    "reports/fusion_selftest.json",
    "reports/preflight_v11.json",
]

REPO_FILES = [
    "README_FUSION_V4_20261102.md",
    "data/B0_基线票据_v4fusion.md",
    "data/B0_自动匹配技能.csv",
    "data/B0_批次进度.csv",
    "data/contract_v1_draft.md",
    "data/contract_v1.json",
    "data/mechanism_map.json",
    "data/channel_map.csv",
    "data/channel_map.json",
    "data/skin_lexicon_rehab.json",
    "data/rehab_pilot_20.json",
    "data/B4_康复域试点票据.md",
    "data/B5_语义技能族票据.md",
    "data/B6_赫布落盘票据.md",
    "data/admission_rules.json",
    "data/admission_ledger.csv",
    "data/B7_准入票据_B7-1.md",
    "data/B7_准入票据_B7-2.md",
    "data/B7_准入票据_B7-3.md",
    "data/B7_准入票据_B7-4.md",
    "data/ivsa_plugin_v1.2.json",
    "data/dual_repo_sums.json",
    "data/许可分层清单.csv",
    "data/B8_双仓开源同步票据.md",
    "data/semantic_modules.json",
    "data/semantic_family.json",
    "data/hebbian_store.json",
    "data/skill_usage_labels.csv",
    "data/channel_quota.csv",
    "data/b3_sample_verdicts.json",
    "data/b3_usage_labels_README.md",
    "data/five_site_dna.json",
    "data/FIVE_SITE_SYNC_DNA.md",
    "holoaeon/fusion_upgrade/contract.py",
    "holoaeon/fusion_upgrade/semantic_family.py",
    "holoaeon/fusion_upgrade/hebbian_store.py",
    "holoaeon/fusion_upgrade/admission.py",
    "holoaeon/fusion_upgrade/dual_sync.py",
    "reports/b0_lock_v4fusion.json",
    "reports/b5_semantic_check.json",
    "reports/b6_hebbian_check.json",
    "reports/b6_restart.json",
    "reports/b7_admission_check.json",
    "reports/b7_gates.json",
    "reports/b8_dual_sync.json",
    "reports/b8_dual_sync_check.json",
    "reports/contract_v1_check.json",
    "reports/contract_v1_interop.json",
    "reports/gate_b0_v4.json",
    "scripts/b0_match.py",
    "scripts/build_mechanism_map.py",
    "scripts/check_contract_draft.py",
    "scripts/check_contract_v1.py",
    "scripts/check_mechanism_map.py",
    "scripts/check_channel_map.py",
    "scripts/classify_skill_usage.py",
    "scripts/check_vector_sea_manifest.py",
    "scripts/gen_rehab_pilot.py",
    "scripts/check_rehab_pilot.py",
    "scripts/check_skill_usage_labels.py",
    "scripts/expand_semantic.py",
    "scripts/check_semantic_family.py",
    "scripts/hebbian_persist.py",
    "scripts/gen_channel_quota.py",
    "scripts/test_restart_consistency.py",
    "scripts/check_hebbian_store.py",
    "scripts/admit_batch.py",
    "scripts/build_b8_dual_sync.py",
    "scripts/verify_b8_dual_sync.py",
    "scripts/gen_channel_map.py",
    "scripts/gen_skin_lexicon.py",
    "scripts/contract_interop.py",
    "scripts/contract_interop_final.py",
    "scripts/five_site_dna.py",
    "scripts/freeze_contract_v1.py",
    "SHA256SUMS",
    "tests_contract/test_contract_v1.py",
    "tests_contract/test_mechanism_map.py",
    "tests_contract/test_channel_map.py",
    "tests_contract/test_skill_usage_labels.py",
    "tests_contract/test_rehab_pilot.py",
    "tests_contract/test_semantic_family.py",
    "tests_contract/test_hebbian_store.py",
    "tests_contract/test_admission_gate.py",
    "tests_contract/test_dual_sync.py",
    "data/B9_融合总策划_v2.md",
    "data/B9_批次台账_v2.csv",
    "data/B9_完美融合判据.md",
    "data/B9_风险与回滚登记.md",
    "data/B9_四透镜评审意见.md",
    "data/B9_收口票据.md",
    "scripts/build_b9_zip.py",
    "scripts/build_b9_closeout.py",
    "scripts/verify_b9_closeout.py",
    "tests_contract/test_b9_closeout.py",
    "data/V2.1_ivsa只读对账票据.md",
    "scripts/verify_ivsa_recon.py",
    "tests_contract/test_ivsa_recon.py",
    "data/plugin_capability_registry.json",
    "data/V4.1_插件接推理票据.md",
    "holoaeon/fusion_upgrade/plugin_runtime.py",
    "scripts/verify_plugin_runtime.py",
    "tests_contract/test_plugin_runtime.py",
    "reports/v41_plugin_runtime_check.json",
    "data/semantic_modules_v4.json",
    "data/V4.1_语义扩容至100票据.md",
    "scripts/verify_semantic_100.py",
    "tests_contract/test_semantic_100.py",
    "reports/v41_semantic_100_check.json",
    "data/three_field_cards.json",
    "data/V4.2_三场卡电场补齐票据.md",
    "holoaeon/fusion_upgrade/three_field.py",
    "scripts/verify_three_field.py",
    "tests_contract/test_three_field.py",
    "reports/v42_three_field_check.json",
    "scripts/mirror_hf.py",
    "scripts/build_vector_sea_manifest.py",
    "scripts/check_delivery_pkg.py",
    "holoaeon/fusion_upgrade/reasoning_adapter.py",
    "scripts/verify_v43.py",
    "tests_contract/test_v43.py",
    "data/semantic_family_identity_v2.json",
    "data/v43_gap_literature_probe.json",
    "reports/v43_hardening_check.json",
    "data/V4.3_工程硬化与遗留收尾票据.md",
    # ---- V4.4-B1 真实模型桥接（7 件）
    "data/model_provider_catalog.json",
    "data/V4.4_真实模型桥接票据.md",
    "docs/接入真实模型_配置指南.md",
    "holoaeon/fusion_upgrade/model_gateway.py",
    "scripts/verify_v44.py",
    "tests_contract/test_v44.py",
    "reports/v44_model_gateway_check.json",
    # ---- V4.5-B1 本地运行时联调（5 件）
    "data/V4.5_本地运行时联调票据.md",
    "scripts/live_gateway_probe.py",
    "scripts/verify_v45.py",
    "tests_contract/test_v45.py",
    "reports/v45_live_probe.json",
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
    """开工前置检测 P1–P7。任一 FAIL → 退出码 1，禁止开批。"""
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

    # P7 五地实体回读（只读回执，不联网）
    ok7 = False
    det7 = "receipt missing"
    try:
        with open(RECEIPT, encoding="utf-8") as f:
            receipt = json.load(f)
        sites = receipt.get("sites", {})
        s1 = str(sites.get("S1_local", "")).split("（")[0].strip()
        s2 = str(sites.get("S2_gitee", "")).strip()
        s3 = str(sites.get("S3_github", "")).strip()
        hf = str(sites.get("S5_hf", "")).strip()
        same = bool(s1) and s1[:7] == s2[:7] == s3[:7]
        hf_ok = bool(re.match(r"[0-9a-f]{40}", hf))
        vec = int(receipt.get("files_count") or 0)
        vec_ok = vec > 0 and vec == len(receipt.get("files") or {})
        ok7 = same and hf_ok and vec_ok
        det7 = "sha_same={} hf40={} vector_files={}".format(same, hf_ok, vec)
    except Exception as exc:
        det7 = "receipt unreadable: {}".format(type(exc).__name__)
    add("P7", ok7, det7)

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
