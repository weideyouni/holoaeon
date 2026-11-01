# -*- coding: utf-8 -*-
"""
ReplayBranch —— 从第 N 步开分支 + 账本不可变（W18 之一，旁挂）
================================================================================
分支不等于改写：原账本字节不变（哈希不变），新分支独立记账，两支可并排比较。

账本行只写结构字段（seq / stage / value / verdict），不写时间。

纯标准库。
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


def _canon(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), default=str)


@dataclass
class Row:
    seq: int
    stage: str
    value: Any = None
    verdict: str = "ok"

    def to_dict(self) -> dict:
        return {"seq": self.seq, "stage": self.stage, "value": self.value,
                "verdict": self.verdict}


class Ledger:
    """追加式账本；digest 覆盖全部行，任何改写都会变。"""

    def __init__(self, rows: Optional[List[Row]] = None, branch: str = "main") -> None:
        self.rows: List[Row] = list(rows or [])
        self.branch = branch

    def append(self, stage: str, value: Any = None, verdict: str = "ok") -> Row:
        row = Row(seq=len(self.rows), stage=stage, value=value, verdict=verdict)
        self.rows.append(row)
        return row

    def digest(self) -> str:
        blob = _canon([r.to_dict() for r in self.rows])
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()

    def to_json(self) -> str:
        return _canon({"branch": self.branch, "rows": [r.to_dict() for r in self.rows]})

    def snapshot(self) -> dict:
        return {"branch": self.branch, "rows": len(self.rows),
                "digest": self.digest()}


class ReplayBranch:
    """在第 N 步之后开新分支：前缀继承（只读副本），其后独立追加。"""

    def __init__(self, ledger: Ledger) -> None:
        self.ledger = ledger
        self.original_digest = ledger.digest()

    def branch_from(self, n: int, name: str = "alt") -> Ledger:
        if n < -1 or n >= len(self.ledger.rows):
            raise ValueError("分支点越界：n=%d，账本 %d 行"
                             % (n, len(self.ledger.rows)))
        head = self.ledger.rows[:n + 1] if n >= 0 else []
        return Ledger(rows=[Row(**r.to_dict()) for r in head], branch=name)

    def untouched(self, original_snapshot: dict) -> dict:
        """复核：开分支前后原账本 digest 必须一致。"""
        now = self.ledger.digest()
        return {"same": now == original_snapshot.get("digest"),
                "before": original_snapshot.get("digest"), "after": now}


def compare(left: Ledger, right: Ledger) -> dict:
    """两支并排比较：按 seq 对齐，返回分歧步（只读，不改任何账本）。"""
    diffs: List[dict] = []
    limit = max(len(left.rows), len(right.rows))
    for i in range(limit):
        a = left.rows[i].to_dict() if i < len(left.rows) else None
        b = right.rows[i].to_dict() if i < len(right.rows) else None
        if a != b:
            diffs.append({"seq": i, "left": a, "right": b})
    return {"same": not diffs, "diffs": diffs,
            "left": left.snapshot(), "right": right.snapshot(),
            "comparable": True}
