"""V2.1 · ivsa 只读对账校验器（纯标准库 / 离线 / 只读）。

用法：python scripts/verify_ivsa_recon.py [--json reports/ivsa_recon.json]

对账口径：本脚本只以只读方式打开 ivsa 侧文件，不写入、不改名、不删任何 ivsa 文件；
所有结论可由本地件复算。校验 R1–R7：

  R1  ivsa SHA256SUMS 91/91 逐件复算（missing=0 / bad_sha256=0 / bad_bytes=0）
  R2  17 通道分组互认（宿主中文分组映射后逐组相等、合计 17）
  R3  许可分层（宿主 Apache-2.0 / ivsa MPL-2.0，无混用条目）
  R4  插件默认关闭；显式 enable 才装载 6 项能力；维度契约仍 25/47/9
  R5  ivsa 源码未拷入宿主（main.py / selftest.py / ivsa 目录均不存在于宿主根）
  R6  双仓摘要口径一致（data/dual_repo_sums.json 的宿主/ivsa 行数与实算一致）
  R7  规格 0.9.1 且 dimension_lock 三数 = 25/47/9
"""

import hashlib
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

IVSA = os.environ.get(
    "HOLOAEON_IVSA",
    r"F:\doubaowork\开源发布_中西医融合康复工程_20261026\integrative-rehab-vsa")
LOCK = {"agents": 25, "skills": 47, "packs": 9}
EVIDENCE_CLASS = "simulated"

from holoaeon.fusion_upgrade import dual_sync as DS  # noqa: E402


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path):
    with io.open(path, encoding="utf-8") as f:
        return f.read()


def load_json(path):
    if not os.path.isfile(path):
        return None
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def check_ivsa_sums():
    path = os.path.join(IVSA, "SHA256SUMS")
    if not os.path.isfile(path):
        return False, "ivsa SHA256SUMS missing"
    entries = DS.parse_sums(read_text(path))
    missing, bad_sha, bad_bytes = [], [], []
    for digest, name in entries:
        target = os.path.join(IVSA, name.replace("/", os.sep))
        if not os.path.isfile(target):
            missing.append(name)
            continue
        got = sha256_file(target)
        if got != digest:
            bad_sha.append(name)
        if len(got) != len(digest):
            bad_bytes.append(name)
    ok = len(entries) == 91 and not missing and not bad_sha
    detail = "checked=%d missing=%d bad_sha=%d bad_bytes=%d" % (
        len(entries), len(missing), len(bad_sha), len(bad_bytes))
    return ok, detail


def check_channels():
    result = DS.interface_check(
        os.path.join(ROOT, "data", "channel_quota.csv"),
        os.path.join(IVSA, "data", "meridian_channels_17.csv"))
    ok = bool(result["equal"]) and result["total_ivsa"] == 17
    detail = "total_holo=%d total_ivsa=%d equal=%s" % (
        result["total_holo"], result["total_ivsa"], result["equal"])
    return ok, detail


def check_license():
    host_text = read_text(os.path.join(ROOT, "LICENSE"))
    guest_text = read_text(os.path.join(IVSA, "LICENSE"))
    mixed = DS.license_mixed(DS.license_layers())
    host_ok = "Apache License" in host_text
    guest_ok = "Mozilla Public License" in guest_text
    ok = host_ok and guest_ok and not mixed
    detail = "apache=%s mpl=%s mixed=%s" % (host_ok, guest_ok, mixed)
    return ok, detail


def check_plugin_default():
    desc = DS.plugin_descriptor()
    off = DS.load_plugin()
    on = DS.load_plugin(enable=True)
    ok = (desc["enabled_by_default"] is False
          and desc["requires_explicit_enable"] is True
          and off["state"] == "disabled" and off["capabilities_loaded"] == 0
          and on["state"] == "enabled"
          and on["capabilities_loaded"] == on["capabilities_total"] == 6
          and desc["dimension_contract"] == LOCK)
    detail = "off=%s on=%d contract=%s" % (
        off["state"], on["capabilities_loaded"], desc["dimension_contract"])
    return ok, detail


def check_no_source_copy():
    hits = []
    for rel in ("main.py", "selftest.py"):
        if os.path.exists(os.path.join(ROOT, rel)):
            hits.append(rel)
    if os.path.isdir(os.path.join(ROOT, "ivsa")):
        hits.append("ivsa/")
    return not hits, "hits=%s" % hits


def check_dual_sums():
    path = os.path.join(ROOT, "data", "dual_repo_sums.json")
    facts = load_json(path)
    if not facts:
        return False, "dual_repo_sums missing"
    host_path = os.path.join(ROOT, "SHA256SUMS")
    ivsa_path = os.path.join(IVSA, "SHA256SUMS")
    host_lines = len([l for l in read_text(host_path).splitlines() if l.strip()])
    ivsa_lines = len([l for l in read_text(ivsa_path).splitlines() if l.strip()])
    host_sha = sha256_file(host_path)
    ivsa_sha = sha256_file(ivsa_path)
    recorded = facts.get("holoaeon", {}) or {}
    recorded_ivsa = facts.get("ivsa", {}) or {}
    ok = (recorded.get("entries") == host_lines and recorded.get("sums_sha256") == host_sha
          and recorded_ivsa.get("entries") == ivsa_lines and recorded_ivsa.get("sums_sha256") == ivsa_sha)
    detail = "host=%s/%s ivsa=%s/%s" % (
        recorded.get("entries"), host_lines, recorded_ivsa.get("entries"), ivsa_lines)
    return bool(ok), detail


def check_spec_lock():
    spec = read_text(os.path.join(ROOT, "holoaeon", "spec.py"))
    match = re.search(r'VERSION\s*=\s*"([^"]+)"', spec)
    version = match.group(1) if match else "?"
    lock = load_json(os.path.join(ROOT, "reports", "dimension_lock.json")) or {}
    dims = {d.get("name"): d.get("value") for d in lock.get("dimensions", [])}
    got = {"agents": dims.get("holoaeon_agents"), "skills": dims.get("holoaeon_skills"),
           "packs": dims.get("holoaeon_domain_packs")}
    ok = version == "0.9.1" and got == LOCK and dims.get("spec_version") == version
    detail = "spec=%s lock=%s" % (version, got)
    return ok, detail


CHECKS = [
    ("R1", "ivsa 清单 91/91 复算", check_ivsa_sums),
    ("R2", "17 通道分组互认", check_channels),
    ("R3", "许可分层无混用", check_license),
    ("R4", "插件默认关闭且维度不变", check_plugin_default),
    ("R5", "ivsa 源码未入宿主", check_no_source_copy),
    ("R6", "双仓摘要口径一致", check_dual_sums),
    ("R7", "spec 0.9.1 + 维度锁", check_spec_lock),
]


def facts():
    ivsa_sums = os.path.join(IVSA, "SHA256SUMS")
    host_sums = os.path.join(ROOT, "SHA256SUMS")
    channels = DS.interface_check(
        os.path.join(ROOT, "data", "channel_quota.csv"),
        os.path.join(IVSA, "data", "meridian_channels_17.csv"))
    return {
        "batch": "V2.1",
        "evidence_class": EVIDENCE_CLASS,
        "readonly": True,
        "ivsa_root": IVSA,
        "ivsa_sums": {
            "lines": len([l for l in read_text(ivsa_sums).splitlines() if l.strip()]),
            "bytes": os.path.getsize(ivsa_sums),
            "sha256": sha256_file(ivsa_sums),
        },
        "host_sums": {
            "lines": len([l for l in read_text(host_sums).splitlines() if l.strip()]),
            "bytes": os.path.getsize(host_sums),
            "sha256": sha256_file(host_sums),
        },
        "channels": channels,
        "license": {"host": "Apache-2.0", "guest": "MPL-2.0",
                    "mixed": DS.license_mixed(DS.license_layers())},
        "dimension_contract": dict(LOCK),
    }


def run():
    results = []
    for cid, name, fn in CHECKS:
        try:
            ok, detail = fn()
        except Exception as exc:
            ok, detail = False, "exc=%s: %s" % (type(exc).__name__, exc)
        results.append({"id": cid, "name": name, "passed": bool(ok), "detail": detail})
    passed = sum(1 for r in results if r["passed"])
    report = {"verdict": "PASS" if passed == len(results) else "FAIL",
              "passed": passed, "total": len(results),
              "checks": results,
              "failed": [r["id"] for r in results if not r["passed"]],
              "facts": facts()}
    report["seal"] = DS.canonical_digest(report)
    return report


def main():
    argv = sys.argv[1:]
    report = run()
    out = None
    if "--json" in argv:
        idx = argv.index("--json")
        out = argv[idx + 1] if len(argv) > idx + 1 else None
    if out:
        path = out if os.path.isabs(out) else os.path.join(ROOT, out)
        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
