# -*- coding: utf-8 -*-
"""
Interrupt —— 可恢复暂停 + checkpoint 三档（W16，旁挂，不挂内核）
================================================================================
高危动作不直接拒绝，而是**挂起等人签核**：暂停态可序列化、可跨进程恢复。
令牌必须是离线 JSON 文件，不联网（V3-4）。未获批的动作永不执行。

checkpoint 三档（none / step / tick）每档写清保证与代价。
checkpoint 字节必须可复现：只写结构字段，不写时间戳（V2 G-7）。

纯标准库。
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

PENDING, APPROVED, REJECTED = "pending", "approved", "rejected"

# 三档：保证 / 代价 / 恢复粒度
CHECKPOINT_TIERS = {
    "none": {
        "guarantee": "不写盘；中断即丢，仅用于可重放的纯函数任务",
        "cost": "0 字节 IO；强杀后需整套重跑",
        "resume_granularity": "从头",
    },
    "step": {
        "guarantee": "每个逻辑步写一次盘；强杀后从最近完成步继续",
        "cost": "每步一次 JSON 落盘（O(步数) IO）",
        "resume_granularity": "步",
    },
    "tick": {
        "guarantee": "每次节拍写一次盘；强杀后最多丢一个节拍",
        "cost": "每拍一次 JSON 落盘（IO 最重）",
        "resume_granularity": "拍",
    },
}


def _canon(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"))


def _atomic_write(path: str, text: str) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    os.replace(tmp, path)


@dataclass
class Interrupt:
    """一次待签核的动作。frozen 是冻结后的信封（dict），审批后可原位恢复。"""

    action: str
    frozen: Dict[str, Any]
    interrupt_id: str = ""
    status: str = PENDING
    reason: str = ""
    approval_token: str = ""

    def __post_init__(self) -> None:
        if not self.interrupt_id:
            blob = _canon({"action": self.action, "frozen": self.frozen})
            self.interrupt_id = hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]
        if self.status == PENDING and not self.approval_token:
            self.approval_token = self._mint_token()

    def _mint_token(self) -> str:
        """令牌 = sha256(frozen + action + interrupt_id)[:24]；离线、纯函数。"""
        blob = _canon({"frozen": self.frozen, "action": self.action,
                       "id": self.interrupt_id})
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:24]

    def to_dict(self) -> dict:
        return {"interrupt_id": self.interrupt_id, "action": self.action,
                "status": self.status, "reason": self.reason,
                "approval_token": self.approval_token, "frozen": self.frozen}

    @staticmethod
    def from_dict(d: dict) -> "Interrupt":
        return Interrupt(action=d["action"], frozen=dict(d["frozen"]),
                         interrupt_id=d.get("interrupt_id", ""),
                         status=d.get("status", PENDING),
                         reason=d.get("reason", ""),
                         approval_token=d.get("approval_token", ""))


class InterruptStore:
    """离线令牌仓：一条中断一个 JSON 文件，路径由 interrupt_id 决定。"""

    def __init__(self, directory: str) -> None:
        self.dir = directory
        os.makedirs(self.dir, exist_ok=True)

    def path(self, interrupt_id: str) -> str:
        return os.path.join(self.dir, "%s.json" % interrupt_id)

    def save(self, it: Interrupt) -> str:
        _atomic_write(self.path(it.interrupt_id), _canon(it.to_dict()))
        return self.path(it.interrupt_id)

    def load(self, interrupt_id: str) -> Interrupt:
        with open(self.path(interrupt_id), "r", encoding="utf-8") as fh:
            return Interrupt.from_dict(json.load(fh))

    def resolve(self, interrupt_id: str, decision: str, *,
                token: str = "", reason: str = "") -> dict:
        """签核入口：校验令牌后改状态；未获批永不执行由调用方保证。"""
        it = self.load(interrupt_id)
        if token and token != it.approval_token:
            return {"ok": False, "reason": "令牌不匹配", "interrupt_id": interrupt_id}
        if decision not in (APPROVED, REJECTED):
            return {"ok": False, "reason": "decision 只能是 approved/rejected",
                    "interrupt_id": interrupt_id}
        it.status = decision
        it.reason = reason
        self.save(it)
        return {"ok": True, "status": decision, "interrupt_id": interrupt_id,
                "path": self.path(interrupt_id)}


def halt(action: str, frozen: Dict[str, Any], directory: str) -> Interrupt:
    """挂起一个动作：写令牌文件，返回待签核对象。"""
    it = Interrupt(action=action, frozen=frozen)
    InterruptStore(directory).save(it)
    return it


def resume(store: InterruptStore, interrupt_id: str,
           decision: str, *, token: str = "") -> dict:
    """恢复入口：只有 approved 才返回可执行载荷。"""
    it = store.load(interrupt_id)
    if decision == APPROVED and token and token != it.approval_token:
        return {"ok": False, "executable": False, "reason": "令牌不匹配"}
    if decision == REJECTED:
        store.resolve(interrupt_id, REJECTED, token=token)
        return {"ok": True, "executable": False, "status": REJECTED,
                "payload": None}
    if it.status != PENDING and it.status != APPROVED:
        return {"ok": False, "executable": False, "reason": "状态不可恢复：%s" % it.status}
    store.resolve(interrupt_id, APPROVED, token=token)
    return {"ok": True, "executable": True, "status": APPROVED,
            "payload": dict(it.frozen), "interrupt_id": interrupt_id}


@dataclass
class Checkpoint:
    """一步/一拍的结构快照；只写结构字段，不写时间。"""

    seq: int
    stage: str
    payload: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {"seq": self.seq, "stage": self.stage, "payload": self.payload}


class CheckpointStore:
    """三档 checkpoint 落盘器；tier=none 时不写盘（返回 None）。"""

    def __init__(self, directory: str, tier: str = "step") -> None:
        if tier not in CHECKPOINT_TIERS:
            raise ValueError("未知档位：%s" % tier)
        self.dir = directory
        self.tier = tier
        if tier != "none":
            os.makedirs(self.dir, exist_ok=True)

    def policy(self) -> dict:
        return {"tier": self.tier, **CHECKPOINT_TIERS[self.tier]}

    def write(self, seq: int, stage: str, payload: Dict[str, Any]) -> Optional[str]:
        if self.tier == "none":
            return None
        path = os.path.join(self.dir, "ckpt-%06d.json" % seq)
        _atomic_write(path, _canon(Checkpoint(seq, stage, payload).to_dict()))
        return path

    def latest(self) -> Optional[Checkpoint]:
        if self.tier == "none" or not os.path.isdir(self.dir):
            return None
        files = sorted(f for f in os.listdir(self.dir)
                       if f.startswith("ckpt-") and f.endswith(".json"))
        if not files:
            return None
        with open(os.path.join(self.dir, files[-1]), "r", encoding="utf-8") as fh:
            d = json.load(fh)
        return Checkpoint(seq=d["seq"], stage=d["stage"], payload=d.get("payload", {}))

    def resume_from(self, total_steps: int) -> List[int]:
        """返回剩余步序列：强杀后从最近 checkpoint 的下一步继续。"""
        last = self.latest()
        start = 0 if last is None else last.seq + 1
        return list(range(start, total_steps))
