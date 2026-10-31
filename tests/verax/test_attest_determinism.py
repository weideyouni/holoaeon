# -*- coding: utf-8 -*-
"""VERAX 自证确定性测试：verdict_hash 跨构建稳定、jsonl 逐字节可复现。"""
from __future__ import annotations

import hashlib
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from holoaeon.audit import (assemble, load_golden, verify,  # noqa: E402
                            write_jsonl)

SELFTEST_FAKE = {"groups": 2, "passed": 2, "failed": 0, "ok": True,
                 "details": [{"group": "G1 spec", "passed": True,
                              "detail": "config=True"},
                             {"group": "G2 envelope", "passed": True,
                              "detail": "roundtrip"}],
                 "ok": True}
REDLINE = {"files": 34, "violations": 0}
HONESTY = {"h1": 0, "h2": 0, "simulated": 0, "measured": 0, "third_party": 0}


def _repro():
    golden = load_golden("word_count")
    return [verify("word_count", golden["task"], n=2, golden=golden)]


class TestAttestDeterminism(unittest.TestCase):
    def test_verdict_hash_stable_across_builds(self):
        repro = _repro()
        first = assemble(SELFTEST_FAKE, repro, HONESTY, REDLINE, "RT", "abc")
        second = assemble(SELFTEST_FAKE, repro, HONESTY, REDLINE, "RT", "abc")
        self.assertEqual(first.verdict_hash, second.verdict_hash)

    def test_ts_build_excluded_from_hash(self):
        repro = _repro()
        first = assemble(SELFTEST_FAKE, repro, HONESTY, REDLINE, "RT", "abc")
        second = assemble(SELFTEST_FAKE, repro, HONESTY, REDLINE, "RT", "abc")
        second.ts_build = "1999-01-01T00:00:00Z"
        self.assertNotEqual(first.ts_build, second.ts_build)
        self.assertEqual(first.verdict_hash, second.verdict_hash)

    def test_jsonl_bytes_identical(self):
        repro = _repro()
        attestation = assemble(SELFTEST_FAKE, repro, HONESTY, REDLINE, "RT", "abc")
        with tempfile.TemporaryDirectory() as tmp:
            p1 = os.path.join(tmp, "a.jsonl")
            p2 = os.path.join(tmp, "b.jsonl")
            write_jsonl(attestation, p1)
            write_jsonl(attestation, p2)
            with open(p1, "rb") as fh:
                h1 = hashlib.sha256(fh.read()).hexdigest()
            with open(p2, "rb") as fh:
                h2 = hashlib.sha256(fh.read()).hexdigest()
        self.assertEqual(h1, h2)

    def test_failing_check_turns_red(self):
        repro = _repro()
        attestation = assemble(SELFTEST_FAKE, repro, HONESTY, REDLINE, "RT", "abc")
        attestation.checks.append(type(attestation.checks[0])(
            gid="BM-x", name="bad", status="fail", evidence={}))
        from holoaeon.audit.attest import conclusion_of
        self.assertEqual(
            conclusion_of(attestation.checks,
                          {"h1": 0, "h2": 0}, {"violations": 0}), "red")


if __name__ == "__main__":
    unittest.main()
