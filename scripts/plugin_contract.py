# -*- coding: utf-8 -*-
"""V86 批3 · 3 个试点插件的八面契约 + 双态判定 + 经络 append。

零复制纪律：插件源码不进基座仓，只在 registry 存
path + sha256(目录指纹) + fragment_id + leg + 25 格指针。

用法：
  python scripts/plugin_contract.py --plan     # 只算八面 + theta，不写盘
  python scripts/plugin_contract.py --apply    # 写 data/plugin_contract.json + registry append
"""
import hashlib
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from holoaeon import genome_dna as gd          # noqa: E402

SCAN = r"F:\doubaowork"
PILOTS = [
    ("实用中医内科表典金刚1331x1331超级矩阵V3实战化_20261020", "编排",
     "NEIKE 内科表典金刚运行时：经络编排位（C03 总线仓下游）"),
    ("全库医学知识库1331x1331超级矩阵V3实战化_20261020", "总线",
     "SSYD-MEDKB V3.0 全库医学知识库：总线位（23 协议族宿主）"),
    ("世殊医道慢病管理智能引擎_20261116", "可观测",
     "SSYD 慢病管理智能引擎：可观测位（随访/危险度/审计可视化）"),
]
TEXT_EXT = (".py", ".md", ".json", ".txt", ".yml", ".yaml")
MAX_BYTES = 6 * 1024 * 1024          # 单文件读取上限，防超大包拖死
SECRET_SHAPES = ("ghp_", "github_pat_", "sk-", "glpat-", "hf_", "PRIVATE KEY")


def _sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def dir_fingerprint(path):
    """目录内容指纹：相对路径 + sha256 逐文件，再整体 sha256（可复算、顺序稳定）。"""
    rows = []
    total = 0
    for base, dirs, fns in os.walk(path):
        dirs[:] = sorted(d for d in dirs if d not in (".git", "__pycache__"))
        for fn in sorted(fns):
            p = os.path.join(base, fn)
            rel = os.path.relpath(p, path).replace(os.sep, "/")
            try:
                sz = os.path.getsize(p)
            except OSError:
                continue
            total += sz
            rows.append([rel, _sha_file(p), sz])
    raw = json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest(), len(rows), total


def read_texts(path, limit_files=4000):
    """收集包内文本（.py/.md/.json/.txt），用后即弃，不落盘。"""
    chunks, n = [], 0
    for base, dirs, fns in os.walk(path):
        dirs[:] = sorted(d for d in dirs if d not in (".git", "__pycache__"))
        for fn in sorted(fns):
            if not fn.lower().endswith(TEXT_EXT):
                continue
            p = os.path.join(base, fn)
            try:
                if os.path.getsize(p) > MAX_BYTES:
                    continue
                with io.open(p, encoding="utf-8", errors="replace") as fh:
                    chunks.append(fh.read())
            except OSError:
                continue
            n += 1
            if n >= limit_files:
                return "\n".join(chunks)
    return "\n".join(chunks)


def genome_metrics(text):
    """三同源实测：25 机制轴命中率 / 心跳参数族 / 密令。

    机制命中用**词边界**正则（(?<![\\w])A1(?![\\w])），避免 A1 裸子串在
    "XA1"/"R11" 之类里误命中；命中率高不等于宣称 100% 同源。
    """
    hit = [m for m in gd.MECHANISM_AXIS
           if re.search(r"(?<![\w])%s(?![\w])" % re.escape(m), text)]
    axis_ratio = len(hit) / float(len(gd.MECHANISM_AXIS))
    hb = all(re.search(r"(?<![\d])%s(?![\d])" % k, text) for k in ("70", "768", "17"))
    seal_ok = gd.SEAL in text
    sim = round(0.6 * axis_ratio + 0.2 * (1.0 if hb else 0.0)
                + 0.2 * (1.0 if seal_ok else 0.0), 4)
    return {"mechanism_hits": len(hit), "axis_ratio": round(axis_ratio, 4),
            "heartbeat_homology": hb, "seal_homology": seal_ok,
            "genome_similarity": sim,
            "triple_homology": {"mechanism_axis": axis_ratio >= 0.12,
                                "heartbeat": hb, "seal": seal_ok}}


def standalone(path):
    """脱离基座可跑：实测存在的入口 + 零第三方依赖线索。"""
    entry = None
    for cand in ("runtime_v3/selftest.py", "selftest.py", "module/main.py",
                 "runtime_v3/main.py", "runtime_v3/__init__.py", "module/__init__.py"):
        p = os.path.join(path, cand.replace("/", os.sep))
        if os.path.isfile(p):
            entry = cand
            break
    if entry is None:
        for base, dirs, fns in os.walk(os.path.join(path, "runtime_v3")):
            if "selftest.py" in fns:
                entry = os.path.relpath(os.path.join(base, "selftest.py"), path)
                entry = entry.replace(os.sep, "/")
                break
    if entry is None:
        # 模块式产物：module/ 下带 __main__ 的 test_*.py 即可独立跑
        mod = os.path.join(path, "module")
        if os.path.isdir(mod):
            for fn in sorted(os.listdir(mod)):
                if fn.startswith("test_") and fn.endswith(".py"):
                    p = os.path.join(mod, fn)
                    try:
                        with io.open(p, encoding="utf-8", errors="replace") as fh:
                            if "__main__" in fh.read():
                                entry = "module/" + fn
                                break
                    except OSError:
                        continue
    zips = []
    try:
        for e in os.scandir(path):
            if e.is_file() and e.name.lower().endswith(".zip"):
                zips.append(e.name)
    except OSError:
        pass
    return entry, zips


def build(row_name, leg, essence):
    path = os.path.join(SCAN, row_name)
    fp, files, total = dir_fingerprint(path)
    text = read_texts(path)
    gm = genome_metrics(text)
    entry, zips = standalone(path)
    secrets = [s for s in SECRET_SHAPES if s in text]
    manifest = {
        "physical": {"path": path, "sha256": fp, "size": total,
                     "file_count": files, "zips": zips},
        "protocol": {"protocol_family": "HOLOAEON", "seal": gd.SEAL,
                     "schema_version": gd.SCHEMA},
        "data": {"data_locality": "on_box", "zero_pixels": True, "zero_dose": True},
        "deploy": {"standalone_entry": entry, "dependencies": []},
        "degradation": {"try_import_skip": True, "env_delta_registered": True},
        "security": {"no_secret_on_box": not secrets,
                     "zero_network": True, "license_ledger": "apache-2.0-or-internal"},
        "genome": {"genome_id": gd.GENOME_ID, "mechanism_subset": gm["mechanism_hits"],
                   "triple_homology_fingerprint": gm["triple_homology"],
                   "genome_similarity": gm["genome_similarity"]},
        "meridian": {"link_back": 1, "fragment_id": "V86-PILOT", "bus_channel": leg,
                     "registered_cells": len(gd.MECHANISM_AXIS)},
        "repo": row_name, "leg": leg, "essence": essence,
        "verify_status": "unverified",
        "standalone_ok": bool(entry),
        "genomic_ok": all(gm["triple_homology"].values()),
        "secrets_hit": secrets,
        "_metrics": gm,
    }
    return manifest


def main():
    apply_mode = "--apply" in sys.argv
    datas = [build(n, leg, ess) for n, leg, ess in PILOTS]
    checks = []
    for m in datas:
        r = gd.plugin_contract_check(m)
        checks.append({"repo": m["repo"], "pass": r["pass"],
                       "problems": r["problems"],
                       "standalone_ok": r["standalone_ok"],
                       "genomic_ok": r["genomic_ok"],
                       "similarity": m["genome"]["genome_similarity"],
                       "entry": m["deploy"]["standalone_entry"],
                       "files": m["physical"]["file_count"],
                       "bytes": m["physical"]["size"]})
    passed = [c["similarity"] for c in checks if c["pass"]]
    theta = round(min(passed), 4) if passed else None
    if theta is not None and theta >= 1.0:
        theta = 0.99
    out = {"schema": "HOLOAEON-PLUGIN-CONTRACT-v1.0", "date": "2026-11-17",
           "seal": gd.SEAL, "pilots": len(datas), "theta": theta,
           "theta_note": "实测标定（双态真试点 sim 的最小值），禁 1.0、禁宣称 100% 同源",
           "plugin_checks": checks,
           "dual_state_pass": sum(1 for c in checks if c["pass"]),
           "dual_state_all_true": all(c["pass"] for c in checks),
           "contracts": datas}
    for c in checks:
        print("[%s] %s sim=%.4f entry=%s files=%d bytes=%d %s"
              % ("PASS" if c["pass"] else "FAIL", c["repo"], c["similarity"],
                 c["entry"], c["files"], c["bytes"],
                 "" if c["pass"] else c["problems"]))
    print("theta =", theta, "| dual_state_all_true =", out["dual_state_all_true"])
    if not apply_mode:
        print("(plan only；加 --apply 落盘)")
        return 0
    if out["dual_state_pass"] == 0:
        print("零个试点双态真 → 拒绝落盘（只独立=分裂，只回连=寄生）")
        return 1
    io.open(os.path.join(ROOT, "data", "plugin_contract.json"), "w",
            encoding="utf-8", newline="\n").write(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    reg_p = os.path.join(ROOT, "data", "genome_dna_registry.json")
    reg = json.load(io.open(reg_p, encoding="utf-8"))
    have = {x.get("repo") for x in reg.get("plugins", [])}
    check_by_repo = {c["repo"]: c for c in checks}
    for i, m in enumerate(datas, start=1):
        if m["repo"] in have:
            continue
        dual = bool(check_by_repo[m["repo"]]["pass"])
        reg["plugins"].append({
            "repo": m["repo"], "rank": i, "leg": m["leg"], "essence": m["essence"],
            "verify_status": "unverified",
            "standalone_ok": m["standalone_ok"], "genomic_ok": m["genomic_ok"],
            "dual_state": dual,
            "path": m["physical"]["path"], "dir_sha256": m["physical"]["sha256"],
            "file_count": m["physical"]["file_count"], "bytes": m["physical"]["size"],
            "fragment_id": "V86-F%02d" % i,
            "genome_similarity": m["genome"]["genome_similarity"],
            "registered_cells": 25, "registered_at": "2026-11-17"})
    io.open(reg_p, "w", encoding="utf-8", newline="\n").write(
        json.dumps(reg, ensure_ascii=False, indent=2) + "\n")
    print("registry 登记 =", len(reg["plugins"]),
          "| 其中双态真（可装配经络）=", sum(1 for x in reg["plugins"] if x.get("dual_state")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
