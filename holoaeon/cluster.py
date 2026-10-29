# -*- coding: utf-8 -*-
"""
Cluster —— HoloAeon 多线程 Actor 邮箱集群
================================================================================
把一组 Agent 包装为真正的【多线程 Actor】：每个 Agent 一个 OS 线程 + 一个邮箱
（Queue），轮次之间用 Barrier 同步，结果通过结果队列回传。

保证：
  · 故障隔离：单个 Agent 处理异常只在本线程捕获，不影响其他 Actor
  · 一致性：每轮 Barrier 对齐，结束后做 L8 一致性校验
  · 无死锁：Barrier parties 固定，所有线程必然到达
  · 可转发：handle 结果中的 forward_to 会被投递到对应 Actor 的邮箱

纯标准库。
"""
from __future__ import annotations

import queue
import threading
import time
from typing import Any, Dict, List, Optional

from .agent import Agent
from .envelope import Envelope


class ActorWorker:
    """单个 Agent 的线程外壳：邮箱 + 工作循环。"""

    def __init__(self, agent: Agent):
        self.agent = agent
        self.inbox: "queue.Queue[Envelope]" = queue.Queue()
        self.thread: Optional[threading.Thread] = None

    def _process_inbox(self, results: "queue.Queue") -> None:
        processed = 0
        while True:
            try:
                env = self.inbox.get_nowait()
            except queue.Empty:
                break
            try:
                res = self.agent.handle(env)
                results.put({"agent_id": self.agent.agent_id, **res})
                # 转发到下一个 actor（若有）
                fwd = (res.get("output") or {})
                if isinstance(fwd, dict) and fwd.get("forward_to"):
                    results.put({"__forward__": fwd["forward_to"],
                                 "from": self.agent.agent_id,
                                 "payload": fwd.get("payload", {})})
            except Exception as exc:  # noqa: BLE001 —— 故障隔离在本线程
                results.put({"agent_id": self.agent.agent_id,
                             "status": "fault", "err": str(exc)})
            processed += 1
        return None


class Cluster:
    """多线程 Actor 集群：邮箱 + Barrier + 故障隔离 + 一致性校验。"""

    def __init__(self, agents: List[Agent]):
        if not agents:
            raise ValueError("Cluster 至少需要一个 Agent")
        self.workers: Dict[str, ActorWorker] = {
            a.agent_id: ActorWorker(a) for a in agents
        }
        self.results: "queue.Queue[dict]" = queue.Queue()
        self._lock = threading.Lock()

    def _worker_loop(self, worker: ActorWorker, barrier: threading.Barrier,
                     rounds: int) -> None:
        for _ in range(rounds):
            worker._process_inbox(self.results)
            try:
                barrier.wait(timeout=10)
            except threading.BrokenBarrierError:
                break

    def run(self, rounds: int = 1,
            tasks: Optional[Dict[str, str]] = None) -> dict:
        """运行 rounds 轮：tasks 为 {agent_id: task}，首轮投递到各邮箱。"""
        tasks = tasks or {}
        parties = len(self.workers)
        barrier = threading.Barrier(parties)
        threads: List[threading.Thread] = []

        # 首轮投递任务
        for aid, text in tasks.items():
            if aid in self.workers:
                env = Envelope.create("cluster", aid, "task", {"task": text})
                self.workers[aid].inbox.put(env)

        for aid, worker in self.workers.items():
            t = threading.Thread(
                target=self._worker_loop,
                args=(worker, barrier, rounds),
                name=f"actor-{aid}", daemon=True,
            )
            worker.thread = t
            threads.append(t)

        start = time.time()
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=15)

        # 处理转发（最多两轮，防止无限转发）
        collected = self._drain_results()
        for _ in range(2):
            forwards = [c for c in collected if "__forward__" in c]
            if not forwards:
                break
            for f in forwards:
                target = f["__forward__"]
                if target in self.workers:
                    env = Envelope.create(
                        f["from"], target, "task",
                        {"task": f["payload"].get("task", "")})
                    self.workers[target].inbox.put(env)
            # 再跑一轮处理转发
            barrier2 = threading.Barrier(parties)
            ts = []
            for worker in self.workers.values():
                t = threading.Thread(target=self._worker_loop,
                                     args=(worker, barrier2, 1), daemon=True)
                t.start(); ts.append(t)
            for t in ts:
                t.join(timeout=15)
            collected.extend(self._drain_results())

        elapsed = round(time.time() - start, 4)
        return self._report(collected, elapsed, rounds)

    def _drain_results(self) -> List[dict]:
        out = []
        while True:
            try:
                out.append(self.results.get_nowait())
            except queue.Empty:
                break
        return out

    def _report(self, collected: List[dict], elapsed: float, rounds: int) -> dict:
        real = [c for c in collected if "__forward__" not in c]
        faults = [c for c in real if c.get("status") == "fault"]
        ok = [c for c in real if c.get("status") == "ok"]
        alive = sum(1 for w in self.workers.values()
                    if w.thread is not None and not w.thread.is_alive())
        # L8 一致性：所有启动线程都已退出
        consistent = alive == len(self.workers)
        return {
            "actors": len(self.workers),
            "rounds": rounds,
            "ok": len(ok),
            "faults": len(faults),
            "fault_detail": faults,
            "consistent": consistent,
            "elapsed_s": elapsed,
            "results": real,
        }
