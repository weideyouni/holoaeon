# -*- coding: utf-8 -*-
"""
VERAX · 可复现性与诚实契约横切子系统（只读观测层）
================================================================================
入口只导出公共 API，import 层零网络、零第三方依赖。

用法：
    from holoaeon.audit import reprohash, canonicalize, verify, verify_all
"""
from __future__ import annotations

from .attest import (Attestation, CheckResult, assemble, checks_from_repro,
                     checks_from_selftest, conclusion_of, verdict_hash,
                     write_jsonl, write_markdown)
from .fields import (CLASS_TABLE, PHYSICAL_KEYS, REPRO_KEYS, canonical_json,
                     canonicalize, canonicalize_report, classify, reprohash,
                     split_physical)
from .honesty import compliance, inspect_receipt, scan_receipts
from .receipt import EVIDENCE_CLASSES, Receipt
from .verify import (build_kernel, list_golden, load_golden, run_task,
                     verify, verify_all)

__all__ = [
    "Receipt", "EVIDENCE_CLASSES", "CLASS_TABLE", "PHYSICAL_KEYS", "REPRO_KEYS",
    "canonicalize", "canonicalize_report", "canonical_json", "reprohash",
    "classify", "split_physical", "verify", "verify_all", "run_task",
    "build_kernel", "load_golden", "list_golden", "inspect_receipt",
    "scan_receipts", "compliance", "Attestation", "CheckResult", "assemble",
    "checks_from_selftest", "checks_from_repro", "conclusion_of",
    "verdict_hash", "write_markdown", "write_jsonl",
]
