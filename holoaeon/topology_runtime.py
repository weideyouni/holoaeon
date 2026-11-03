# -*- coding: utf-8 -*-
"""
topology_runtime —— 城邦运行时增强（V11-C）
================================================================================
把城邦运行时层（Runtime/Harness/Runner）的四个核心概念代码化为确定性组件：

  StateReducer        状态归约器：节点增量更新 → 全局状态（State Reducer）
  Checkpoint          状态快照：中断恢复/断点续跑/时间旅行调试（Replay）
  CircuitBreaker      熔断器：持续失败时隔离节点（Retry Policy + Loop Detection）
  DissipationMonitor  耗散监控：Observability + Traceability + 耗散熵趋势

城邦映射：State → Shared State 一致性；Checkpoint → Replay 能力；
         Circuit Breaker → Retry Policy + Loop Detection；
         可观测与治理层 → Observability / Traceability / Audit。

纯标准库、确定性、离线。不导入包内任何旧模块（零依赖），
不影响 BUILTIN_LAYERS / VERSION / layers=8 / PACK_ORDER / diff0。
"""
from __future__ import annotations

import math
import time
from typing import Any, Dict, List, Optional


class StateReducer:
    """状态归约器：把节点增量更新合并到全局状态。

    语义：归约函数 reduce(old, delta) -> new。
      · delta 为数值 → 指数平滑（alpha 加权）
      · delta 为 dict → 递归归约合并
      · reducer="replace" → 直接替换
    城邦映射：State Reducer → Shared State 一致性。
    """

    def __init__(self, alpha: float = 0.5) -> None:
        self.alpha = max(0.0, min(1.0, alpha))
        self._state: Dict[str, Any] = {}
        self._revision: int = 0

    def apply(self, key: str, delta: Any, *,
              reducer: Optional[str] = None) -> dict:
        """合并增量到全局状态。返回本次归约后的修订信息。"""
        old = self._state.get(key)
        if reducer == "replace" or old is None:
            new = delta
        elif isinstance(old, dict) and isinstance(delta, dict):
            merged = dict(old)
            for k, v in delta.items():
                merged[k] = self._merge_value(old.get(k), v)
            new = merged
        else:
            try:
                new = (self.alpha * float(delta)
                       + (1.0 - self.alpha) * float(old))
            except (TypeError, ValueError):
                new = delta
        self._state[key] = new
        self._revision += 1
        return {"key": key, "revision": self._revision,
                "value": new, "alpha": self.alpha}

    @staticmethod
    def _merge_value(old: Any, new: Any) -> Any:
        if isinstance(old, dict) and isinstance(new, dict):
            merged = dict(old)
            merged.update(new)
            return merged
        return new

    def get(self, key: str) -> Any:
        return self._state.get(key)

    def snapshot(self) -> dict:
        return {"revision": self._revision, "state": dict(self._state)}

    def restore(self, snap: Dict[str, Any]) -> None:
        self._state = dict(snap.get("state", {}))
        self._revision = snap.get("revision", 0)


class Checkpoint:
    """状态快照：中断恢复/断点续跑/时间旅行调试。

    内存版快照链（确定性序号），支持 save / restore / list / count。
    城邦映射：Checkpoint → Replay 能力（基于历史轨迹重新执行）。
    """

    def __init__(self) -> None:
        self._chain: List[Dict[str, Any]] = []

    def save(self, label: str, state: Dict[str, Any]) -> dict:
        cp = {"seq": len(self._chain), "label": label,
              "ts": round(time.time(), 3), "state": dict(state)}
        self._chain.append(cp)
        return {"seq": cp["seq"], "label": label, "ts": cp["ts"]}

    def restore(self, seq: Optional[int] = None) -> Optional[Dict[str, Any]]:
        if not self._chain:
            return None
        if seq is None:
            cp = self._chain[-1]
        else:
            cp = next((c for c in self._chain if c["seq"] == seq), None)
            if cp is None:
                return None
        return dict(cp["state"])

    def list(self) -> List[dict]:
        return [{"seq": c["seq"], "label": c["label"], "ts": c["ts"]}
                for c in self._chain]

    def count(self) -> int:
        return len(self._chain)


class CircuitBreaker:
    """熔断器：持续失败时隔离节点。

    规则：
      · 连续 failure_threshold 次失败 → OPEN（隔离）
      · OPEN 状态每 reset_after 次调用 → HALF_OPEN（探测放行一次）
      · HALF_OPEN 成功 → CLOSED；失败 → 回到 OPEN
    城邦映射：Circuit Breaker → Retry Policy + Loop Detection。
    """

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

    def __init__(self, failure_threshold: int = 3,
                 reset_after: int = 5) -> None:
        self.failure_threshold = max(1, int(failure_threshold))
        self.reset_after = max(1, int(reset_after))
        self._failures: int = 0
        self._calls: int = 0
        self._state: str = self.CLOSED
        self._log: List[dict] = []

    def record(self, ok: bool, node: str = "") -> dict:
        """记录一次调用结果并更新熔断状态。"""
        self._calls += 1
        if ok:
            if self._state == self.HALF_OPEN:
                self._state = self.CLOSED
            self._failures = max(0, self._failures - 1)
        else:
            self._failures += 1
            if self._failures >= self.failure_threshold:
                self._state = self.OPEN
        # OPEN 经过 reset_after 次调用 → HALF_OPEN 探测
        if self._state == self.OPEN and self._calls % self.reset_after == 0:
            self._state = self.HALF_OPEN
        tripped = self._state == self.OPEN
        self._log.append({"node": node, "ok": ok, "state": self._state,
                          "calls": self._calls, "failures": self._failures})
        return {"state": self._state, "tripped": tripped,
                "calls": self._calls, "failures": self._failures}

    def is_open(self) -> bool:
        return self._state == self.OPEN

    def status(self) -> dict:
        return {"state": self._state, "failures": self._failures,
                "calls": self._calls, "threshold": self.failure_threshold,
                "reset_after": self.reset_after}

    def trace(self) -> List[dict]:
        return list(self._log)


class DissipationMonitor:
    """耗散监控：Observability + Traceability + 耗散熵趋势。

    时间序列记录 ok/fail（滑动窗口），实时计算 Shannon 熵、秩序度、
    耗散率与自组织触发（熵 > 0.95 或 秩序 < 0.3 → 重组）。
    城邦映射：可观测与治理层（Observability / Traceability / Audit）。
    """

    def __init__(self, window: int = 10) -> None:
        self.window = max(2, int(window))
        self._flow: List[bool] = []

    def record(self, ok: bool, node: str = "", detail: str = "") -> dict:
        """记录一次结果并返回当前窗口的耗散指标。"""
        self._flow.append(ok)
        if len(self._flow) > self.window:
            del self._flow[:-self.window]
        return self.metrics()

    def metrics(self) -> dict:
        total = len(self._flow)
        if total == 0:
            return {"window": self.window, "total": 0, "success": 0,
                    "failure": 0, "prob_ok": 1.0, "prob_fail": 0.0,
                    "shannon_entropy": 0.0, "order": 1.0,
                    "dissipation_rate": 0.0, "needs_reorganization": False}
        ok_c = sum(1 for x in self._flow if x)
        fail_c = total - ok_c
        p_ok = ok_c / total
        p_fail = fail_c / total
        entropy = 0.0
        if p_ok > 0:
            entropy -= p_ok * math.log2(p_ok)
        if p_fail > 0:
            entropy -= p_fail * math.log2(p_fail)
        entropy_max = 1.0  # 二元分布最大熵
        order = 1.0 - entropy / entropy_max if entropy_max else 1.0
        return {
            "window": self.window, "total": total,
            "success": ok_c, "failure": fail_c,
            "prob_ok": round(p_ok, 4), "prob_fail": round(p_fail, 4),
            "shannon_entropy": round(entropy, 6),
            "order": round(order, 6),
            "dissipation_rate": round(fail_c / total, 4),
            "needs_reorganization": entropy > 0.95 or order < 0.3,
        }

    def trend(self) -> List[dict]:
        """耗散熵时间序列趋势（每步快照，Traceability）。"""
        out = []
        for i in range(len(self._flow)):
            sub = self._flow[:i + 1]
            ok_c = sum(1 for x in sub if x)
            p_ok = ok_c / len(sub)
            p_fail = 1.0 - p_ok
            ent = 0.0
            if p_ok > 0:
                ent -= p_ok * math.log2(p_ok)
            if p_fail > 0:
                ent -= p_fail * math.log2(p_fail)
            out.append({"step": i, "entropy": round(ent, 6),
                        "order": round(1.0 - ent, 6)})
        return out

    def trace(self) -> List[dict]:
        return [{"step": i, "ok": v} for i, v in enumerate(self._flow)]
