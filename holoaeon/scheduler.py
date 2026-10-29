# -*- coding: utf-8 -*-
"""
Scheduler —— HoloAeon 时钟/节拍（原"全息心跳"）
================================================================================
Scheduler 是系统的统一时钟：每个 tick 完成
  · 健康体（body）状态更新：确定性状态向量 + 指数平滑强度（alpha）
  · 注册对象（agent/组件）的存活检测与健康判定
  · 全局状态快照（供恢复/审计）

"全息"的工程含义：每个 body 携带整体信号的一个确定性投影，局部可观测整体；
"心跳"的工程含义：以固定/自适应节奏做同步。tick 可确定性步进（不依赖真实墙钟），
interval 仅在 live 模式下用于真实等待。纯标准库。
"""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .spec import SchedulerConfig

# 健康状态
IDLE = "idle"
ACTIVE = "active"
DEGRADED = "degraded"
FAULT = "fault"


def _seed_vector(seed: str, dim: int) -> List[float]:
    """用 sha256 迭代派生 dim 维 [0,1) 确定性向量（不使用随机数）。"""
    out: List[float] = []
    counter = 0
    while len(out) < dim:
        h = hashlib.sha256(f"{seed}:{counter}".encode("utf-8")).digest()
        for b in h:
            out.append(b / 255.0)
            if len(out) >= dim:
                break
        counter += 1
    return out[:dim]


@dataclass
class HeartbeatBody:
    bid: int
    state: List[float] = field(default_factory=list)
    intensity: float = 0.0
    status: str = IDLE

    def snapshot(self) -> dict:
        return {"id": self.bid, "status": self.status,
                "intensity": round(self.intensity, 4),
                "state_dim": len(self.state)}


class Scheduler:
    """时钟/节拍：健康体 + 存活检测 + 快照。"""

    def __init__(self, config: Optional[SchedulerConfig] = None,
                 watch: Optional[List[Any]] = None):
        self.cfg = config or SchedulerConfig()
        self.watch: List[Any] = list(watch or [])
        self.bodies: List[HeartbeatBody] = [
            HeartbeatBody(
                bid=self.cfg.id_base + i,
                state=_seed_vector(f"body:{self.cfg.id_base + i}", self.cfg.state_dim),
                intensity=0.0,
            )
            for i in range(self.cfg.body_count)
        ]
        self.tick_count = 0
        self.snapshots: List[dict] = []
        self._started = time.time()

    def watch_add(self, obj: Any) -> None:
        self.watch.append(obj)

    # ------------------------------------------------------------ 信号
    def _signal(self, tick: int) -> List[float]:
        """每个 tick 的全局确定性信号（每个 body 投影不同）。"""
        return _seed_vector(f"tick:{tick}", self.cfg.state_dim)

    # ------------------------------------------------------------ tick
    def tick(self, workload: Optional[Dict[str, float]] = None) -> dict:
        self.tick_count += 1
        signal = self._signal(self.tick_count)
        active = 0
        for i, body in enumerate(self.bodies):
            # 该 body 对全局信号的投影强度（与自身状态做点积）
            proj = sum(a * b for a, b in zip(body.state, signal)) / self.cfg.state_dim
            target = proj * 2.0
            if workload and str(body.bid) in workload:
                target = workload[str(body.bid)]
            # 指数平滑
            body.intensity = (1 - self.cfg.alpha) * body.intensity + self.cfg.alpha * target
            body.intensity = max(0.0, min(1.0, body.intensity))
            if body.intensity >= 0.6:
                body.status = ACTIVE
                active += 1
            elif body.intensity >= 0.3:
                body.status = DEGRADED
            else:
                body.status = IDLE

        # 存活检测：被监视对象若有 snapshot 且标记 fault 则计入
        faults = self._check_watch()

        snap = {
            "tick": self.tick_count,
            "ts": time.time(),
            "active": active,
            "degraded": sum(1 for b in self.bodies if b.status == DEGRADED),
            "idle": sum(1 for b in self.bodies if b.status == IDLE),
            "faults": faults,
            "watch_count": len(self.watch),
        }
        if self.cfg.snapshot_enabled:
            self.snapshots.append(snap)
        return snap

    def _check_watch(self) -> List[str]:
        faults: List[str] = []
        for obj in self.watch:
            try:
                snap = obj.snapshot() if callable(getattr(obj, "snapshot", None)) else {}
                if snap.get("status") == FAULT or snap.get("fault") is True:
                    faults.append(snap.get("agent_id", str(obj)))
            except Exception:  # noqa: BLE001
                faults.append(str(getattr(obj, "agent_id", obj)))
        return faults

    def run(self, ticks: int, workload: Optional[Dict[str, float]] = None) -> List[dict]:
        return [self.tick(workload) for _ in range(ticks)]

    def health(self) -> dict:
        return {
            "tick_count": self.tick_count,
            "bodies": len(self.bodies),
            "active": sum(1 for b in self.bodies if b.status == ACTIVE),
            "degraded": sum(1 for b in self.bodies if b.status == DEGRADED),
            "idle": sum(1 for b in self.bodies if b.status == IDLE),
            "sync_mode": self.cfg.sync_mode,
            "watch": len(self.watch),
        }

    def body_snapshot(self) -> List[dict]:
        return [b.snapshot() for b in self.bodies]
