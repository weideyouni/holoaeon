# -*- coding: utf-8 -*-
"""把 HoloAeon V2 资产打包成向量海域（可自证：registry 记录每份副本 sha256）。"""
import hashlib
import json
import os
import shutil

REPO = r"F:\doubaowork\holoaeon"
SKILL = os.path.join(r"C:\Users\Administrator\AppData\Local\DoubaoWork\User Data\Default\.doubaowork\agent_mode\workspace\.user_skills\holoaeon-v2-empower-upgrade", "SKILL.md")
DST = r"F:\doubaowork\向量海_本地库\holoaeon-v2-20261101"

PLAN = [
    (os.path.join(REPO, "snapshot", "SNAPSHOT_V2.md"), "docs/SNAPSHOT_V2.md"),
    (os.path.join(REPO, "snapshot", "project_snapshot_v2.json"), "assets/project_snapshot_v2.json"),
    (os.path.join(REPO, "docs", "spec-diff0-v0.2.md"), "docs/spec-diff0-v0.2.md"),
    (os.path.join(REPO, "AGENT_FEED_V2_DONE_20261101.md"), "docs/AGENT_FEED_V2_DONE_20261101.md"),
    (os.path.join(REPO, "reports", "repro_core.jsonl"), "assets/repro_core.jsonl"),
    (os.path.join(REPO, "reports", "attestation.jsonl"), "assets/verax_attestation.jsonl"),
    (os.path.join(REPO, "benchmarks", "results-semvec-kfold-0.9.2.json"), "assets/results-semvec-kfold-0.9.2.json"),
    (os.path.join(REPO, "scripts", "snapshot_v2.py"), "scripts/snapshot_v2.py"),
    (os.path.join(REPO, "scripts", "repro_core_emit.py"), "scripts/repro_core_emit.py"),
    (os.path.join(REPO, "scripts", "bench_semvec_kfold.py"), "scripts/bench_semvec_kfold.py"),
    (os.path.join(REPO, "scripts", "build_semvec_corpus_v2.py"), "scripts/build_semvec_corpus_v2.py"),
    (os.path.join(REPO, "holoaeon", "audit", "mutation.py"), "scripts/audit_mutation.py"),
    (os.path.join(REPO, "holoaeon", "audit", "verdict_policy.py"), "scripts/audit_verdict_policy.py"),
    (SKILL, "docs/skill-holoaeon-v2-empower-upgrade.md"),
]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    rows = []
    for src, rel in PLAN:
        if not os.path.isfile(src):
            print("MISSING", src)
            continue
        out = os.path.join(DST, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(out), exist_ok=True)
        shutil.copyfile(src, out)
        rows.append({"file": rel, "sha256": sha256(out), "bytes": os.path.getsize(out),
                     "source": src.replace("\\", "/")})
    registry = {
        "domain": "holoaeon-v2-20261101",
        "title": "HoloAeon V2 赋能升级（文档版 0.9.2）",
        "generated_at": "2026-11-01",
        "evidence_class": "simulated",
        "runtime_version": "0.9.1",
        "doc_version": "0.9.2",
        "dimensions_unchanged": {"agents": 25, "skills": 47, "domain_packs": 9,
                                 "extra_packs": 8, "tests": 34, "selftests": 25,
                                 "primitives": 12},
        "key_figures": {
            "diff0": "2fc892cf9af6e755",
            "mutation_sensitive": "f42c8229ee5acd73",
            "guard": "16/16 + 4/4",
            "kfold": "mean=0.9957 std=0.0085",
            "repro_core_rows": 10,
            "verdict_hash": "f2fb0236c8bbd721",
            "ledger_sha": "98940b774566543b",
            "semvec_digest_v1": "789b71a36bfcd66a",
        },
        "files": rows,
    }
    with open(os.path.join(DST, "registry.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(registry, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    print("files=%d" % len(rows))
    for row in rows:
        print("%-42s %s %d" % (row["file"], row["sha256"][:16], row["bytes"]))


if __name__ == "__main__":
    main()
