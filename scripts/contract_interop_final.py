# -*- coding: utf-8 -*-
"""B1b 跨进程互认比对器：读两次独立运行的两份输出，字节相等才算"同参同指纹"。

用法：
  python scripts/contract_interop.py --out reports/a.json
  python scripts/contract_interop.py --out reports/b.json
  python scripts/contract_interop_final.py --a reports/a.json --b reports/b.json --out reports/contract_v1_interop.json

判据：exit 0 = 两次运行字节一致 + I1–I4 全绿。
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def get(argv, flag):
    if flag in argv:
        i = argv.index(flag)
        if i + 1 < len(argv):
            return argv[i + 1]
    return None


def main(argv):
    a = get(argv, "--a") or os.path.join(ROOT, "reports", "contract_v1_interop_a.json")
    b = get(argv, "--b") or os.path.join(ROOT, "reports", "contract_v1_interop_b.json")
    out = get(argv, "--out") or os.path.join(ROOT, "reports", "contract_v1_interop.json")

    if not (os.path.isfile(a) and os.path.isfile(b)):
        print(json.dumps({"verdict": "FAIL", "reason": "missing run output"}, ensure_ascii=False))
        return 1

    sha_a, sha_b = sha256_file(a), sha256_file(b)
    byte_equal = sha_a == sha_b
    with open(a, encoding="utf-8") as f:
        ra = json.load(f)
    ok = byte_equal and ra.get("same_params_equal") and ra.get("payload_changed_differs") \
        and ra.get("nonce_not_in_fingerprint") and ra.get("all_valid")

    report = {
        "experiment": "B1b-cross-process-fingerprint",
        "process_runs": 2,
        "run_a_sha256": sha_a,
        "run_b_sha256": sha_b,
        "byte_equal": byte_equal,
        "same_params_equal": bool(ra.get("same_params_equal")),
        "payload_changed_differs": bool(ra.get("payload_changed_differs")),
        "nonce_not_in_fingerprint": bool(ra.get("nonce_not_in_fingerprint")),
        "all_valid": bool(ra.get("all_valid")),
        "samples": ra.get("samples", []),
        "fingerprint_rule": ra.get("fingerprint_rule", ""),
        "verdict": "PASS" if ok else "FAIL",
    }
    text = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(text + "\n")
    print(text)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
