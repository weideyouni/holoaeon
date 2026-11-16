# -*- coding: utf-8 -*-
"""V86 独立基因闸门（不改 v3_gate.py）。

判据：spec.py byte-identical / DNA verify / 确定性 / 经络动态格数 / registry schema。
用法：cd F:/doubaowork/holoaeon && python scripts/genome_dna_gate.py
退出码：0 全绿，1 任一红。
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from holoaeon import genome_dna as gd        # noqa: E402
from holoaeon import meridian_link as ml     # noqa: E402


def _sha256(path):
    with io.open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def run():
    checks = []
    with io.open(os.path.join(ROOT, "data", "genome_dna.json"), "r",
                 encoding="utf-8") as fh:
        master = json.load(fh)

    spec_sha = _sha256(os.path.join(ROOT, "holoaeon", "spec.py"))
    checks.append(("spec_byte_identical",
                   spec_sha == master["genesis"]["spec_sha256_measured"], spec_sha))

    v = gd.verify()
    checks.append(("dna_verify", bool(v["pass"]), v["problems"]))

    h1, h2 = gd.genome_hash(), gd.genome_hash()
    checks.append(("genome_hash_diff0", h1 == h2, h1))

    sc = gd.self_check()
    checks.append(("self_check_pass", bool(sc["verify"]["pass"]), sc["genome_hash"]))

    frags = ml.load_fragments()
    table = ml.build_meridian_table()
    expected = len(frags) * len(ml.KERNEL_MECHANISMS)
    checks.append(("cells_dynamic", len(table) == expected,
                   "fragments={} cells={} expected={}".format(len(frags), len(table), expected)))

    lk = ml.check_linkage()
    checks.append(("linkage_pass", bool(lk["pass"]), lk["problems"][:3]))

    with io.open(os.path.join(ROOT, "data", "genome_dna_registry.json"), "r",
                 encoding="utf-8") as fh:
        reg = json.load(fh)
    checks.append(("registry_schema", reg.get("schema") == gd.SCHEMA and
                   reg.get("append_only") is True, len(reg.get("plugins", []))))

    problems = [name for name, ok, _ in checks if not ok]
    return {
        "gate": "GENOME-DNA-GATE-v1.0", "seal": gd.SEAL,
        "genome_id": gd.GENOME_ID, "dna_version": gd.DNA_VERSION,
        "checks": [{"name": n, "pass": bool(ok), "detail": d} for n, ok, d in checks],
        "pass": not problems, "problems": problems,
    }


def main():
    out = run()
    print(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if out["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
