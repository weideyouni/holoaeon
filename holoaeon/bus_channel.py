# -*- coding: utf-8 -*-
"""
bus_channel —— C03 总线仓 · 12 通道经络总线（V64 · G-M 门禁通关件）
================================================================================
来源（诚实溯源，零编造）：
  · 12 通道表 LC01–LC12（气 5 / 血 4 / 神 3）来自向量海落盘素材
    F:\\doubaowork\\vector-sea\\holoaeon-v4-cold-hot-plug\\26_通道映射表.csv
  · 通道预算 100 / 负载实测 / headroom 口径来自同目录 47_channel_quota.csv
  · 「12 通道 = 预算 + 淤堵 + 再平衡」「12 vs 17 显式分组映射」来自
    data_六机制对照与通道映射.csv（六机制 meridian 行）
  · 17 通道（气5/血4/神4/淋巴4）在 ivsa 侧；本仓只承接 12 通道（LC01–LC12），
    淋巴 4 条属 pending 位，本模块**不补位、不取模**（同素材注记）

本模块只做一件事：把 org_gate 里 G-M 门禁四项 WAIT 判据变成可执行、可观测、
可复现的实测实现——
  1) 12 通道   ：12 条通道齐、分组齐、每通道有通畅度模型与上下限；
  2) 事件传播 ：≥3 条示范链路可复现（含 C02→C03→C10 的通道化表达 LC02→LC03→LC10）；
  3) 阻塞机制 ：人为压低通畅度可触发阻塞，并启动贝叶斯衍射反演定位最可能被堵通道；
  4) 衰减与终止：增益衰减 / 跳数上限 / 闭环终止 三类终止可观测。

硬边界（不做什么）：
  · 不联网、不读外部配置、不算墙钟；全部确定性（同输入同输出，跨进程逐字节一致）。
  · 不做「配额真实下发」——本模块只有通畅度与传播模型，配额仲裁仍归 org_gate。
  · 淋巴 4 条通道不补位（素材 B2b 待办，如实留空）。
"""
from __future__ import annotations

import io
import json
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

SEAL = "潮起开门，潮落闭嘴"
SCHEMA_VERSION = "BUS-CHANNEL-v1.0"
DATA_OUT_NAME = "bus_channel_table.json"

# ---------------------------------------------------------------------------
# 一、12 通道表（LC01–LC12：气 5 / 血 4 / 神 3）
# ---------------------------------------------------------------------------

CHANNEL_GROUPS: Tuple[Dict[str, Any], ...] = (
    {"group": "气", "range": ("LC01", "LC05"), "count": 5, "role": "调度与驱动（呼吸/动力）"},
    {"group": "血", "range": ("LC06", "LC09"), "count": 4, "role": "承载与输运（物质/数据）"},
    {"group": "神", "range": ("LC10", "LC12"), "count": 3, "role": "决策与反馈（意识/信号）"},
)

# 每通道：lc / name（气1..气5/血1..血4/神1..神3）/ group / budget / floor（淤堵线）/
# ceil（通畅上限）/ load（基线负载，取素材实测值，0 者如实 0）
CHANNELS: Tuple[Dict[str, Any], ...] = (
    {"lc": "LC01", "name": "气1", "group": "气", "budget": 100, "floor": 40, "ceil": 100, "load": 9},
    {"lc": "LC02", "name": "气2", "group": "气", "budget": 100, "floor": 40, "ceil": 100, "load": 8},
    {"lc": "LC03", "name": "气3", "group": "气", "budget": 100, "floor": 40, "ceil": 100, "load": 5},
    {"lc": "LC04", "name": "气4", "group": "气", "budget": 100, "floor": 40, "ceil": 100, "load": 1},
    {"lc": "LC05", "name": "气5", "group": "气", "budget": 100, "floor": 40, "ceil": 100, "load": 1},
    {"lc": "LC06", "name": "血1", "group": "血", "budget": 100, "floor": 40, "ceil": 100, "load": 0},
    {"lc": "LC07", "name": "血2", "group": "血", "budget": 100, "floor": 40, "ceil": 100, "load": 0},
    {"lc": "LC08", "name": "血3", "group": "血", "budget": 100, "floor": 40, "ceil": 100, "load": 0},
    {"lc": "LC09", "name": "血4", "group": "血", "budget": 100, "floor": 40, "ceil": 100, "load": 0},
    {"lc": "LC10", "name": "神1", "group": "神", "budget": 100, "floor": 40, "ceil": 100, "load": 0},
    {"lc": "LC11", "name": "神2", "group": "神", "budget": 100, "floor": 40, "ceil": 100, "load": 0},
    {"lc": "LC12", "name": "神3", "group": "神", "budget": 100, "floor": 40, "ceil": 100, "load": 0},
)

# 素材侧 12→17 映射的「未映射目标」如实登记（不补位、不取模）
UNMAPPED_TARGETS: Tuple[Dict[str, str], ...] = (
    {"target": "神4", "why": "ivsa 侧 17 通道之神 4 条，本仓 12 通道只到神 3"},
    {"target": "淋巴1", "why": "淋巴 4 条属 B2b 待办，配额未分配"},
    {"target": "淋巴2", "why": "同上"},
    {"target": "淋巴3", "why": "同上"},
    {"target": "淋巴4", "why": "同上"},
)

DEMO_CHAINS: Tuple[Dict[str, Any], ...] = (
    {"id": "C02-C03-C10", "path": ("LC02", "LC03", "LC10"), "why": "素材点名的示范链路 C02→C03→C10 的通道化表达"},
    {"id": "C01-C05-C11", "path": ("LC01", "LC05", "LC11"), "why": "进气→驱动→决策三段"},
    {"id": "C06-C08-C12", "path": ("LC06", "LC08", "LC12"), "why": "输运→承载→反馈三段"},
)


# ---------------------------------------------------------------------------
# 二、通畅度模型
# ---------------------------------------------------------------------------

def patency(budget: int, load: int, ceil: int = 100) -> int:
    """通畅度 = 预算 − 负载（夹在 0..ceil）。确定性整数，避免浮点噪声。"""
    p = budget - load
    if p < 0:
        return 0
    if p > ceil:
        return ceil
    return p


def is_blocked(p: int, floor: int) -> bool:
    """通畅度低于淤堵线即阻塞（floor 之下 = 通道堵死）。"""
    return p < floor


class Channel(object):
    """单通道：预算/负载/淤堵线与可逆变更（rollback_token 精确还原）。"""

    __slots__ = ("lc", "name", "group", "budget", "floor", "ceil", "load", "_tokens")

    def __init__(self, spec: Dict[str, Any]) -> None:
        self.lc = spec["lc"]
        self.name = spec["name"]
        self.group = spec["group"]
        self.budget = int(spec["budget"])
        self.floor = int(spec["floor"])
        self.ceil = int(spec["ceil"])
        self.load = int(spec["load"])
        self._tokens: List[Tuple[str, int, int]] = []

    def patency(self) -> int:
        return patency(self.budget, self.load, self.ceil)

    def blocked(self) -> bool:
        return is_blocked(self.patency(), self.floor)

    def press(self, amount: int, reason: str = "阻塞演练") -> str:
        """人为压低通畅度（= 增加负载）。返回 rollback_token。"""
        if amount <= 0:
            raise ValueError("press 需要正数负载增量")
        token = "{}:{}:{}".format(self.lc, self.load, reason)
        self._tokens.append((token, self.load, amount))
        self.load = min(self.budget, self.load + int(amount))
        return token

    def release(self, amount: int) -> int:
        if amount <= 0:
            raise ValueError("release 需要正数负载减量")
        self.load = max(0, self.load - int(amount))
        return self.load

    def rollback(self, token: str) -> bool:
        """按 token 精确还原到变更前状态（G-M「回滚」判据的通道级实现）。"""
        for idx in range(len(self._tokens) - 1, -1, -1):
            t, prev_load, amt = self._tokens[idx]
            if t == token:
                self.load = prev_load
                del self._tokens[idx]
                return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {"lc": self.lc, "name": self.name, "group": self.group,
                "budget": self.budget, "floor": self.floor, "ceil": self.ceil,
                "load": self.load, "patency": self.patency(), "blocked": self.blocked()}


# ---------------------------------------------------------------------------
# 三、总线：事件传播 + 三类终止
# ---------------------------------------------------------------------------

GAIN_DEFAULT = 0.96
GAIN_FLOOR_DEFAULT = 0.60
MAX_HOPS_DEFAULT = 8
EVENT_WEIGHT_DEFAULT = 6


class BusChannel(object):
    """12 通道总线：沿链路传播事件，逐跳衰减，三类终止可观测。"""

    def __init__(self, channels: Optional[List[Dict[str, Any]]] = None) -> None:
        self.channels: Dict[str, Channel] = {}
        for spec in (channels or CHANNELS):
            ch = Channel(spec)
            self.channels[ch.lc] = ch

    # --- 基础查询 ---
    def lcs(self) -> List[str]:
        return sorted(self.channels.keys())

    def group_of(self, lc: str) -> str:
        return self.channels[lc].group

    def patency(self, lc: str) -> int:
        return self.channels[lc].patency()

    def press(self, lc: str, amount: int, reason: str = "阻塞演练") -> str:
        return self.channels[lc].press(amount, reason)

    def rollback(self, lc: str, token: str) -> bool:
        return self.channels[lc].rollback(token)

    # --- 传播 ---
    def propagate(self, event: str, path: Tuple[str, ...], gain: float = GAIN_DEFAULT,
                  max_hops: int = MAX_HOPS_DEFAULT, gain_floor: float = GAIN_FLOOR_DEFAULT,
                  weight: int = EVENT_WEIGHT_DEFAULT) -> Dict[str, Any]:
        """沿 path 传播事件。返回 trace（逐跳 patency/gain/load）与终止原因。

        终止三类（+1 类安全网）：
          · blocked     通畅度 < floor（阻塞）
          · gain_floor  增益衰减到 gain_floor 之下
          · max_hops    跳数超过上限
          · closed_loop 回到已访问通道（闭环）
        """
        trace: List[Dict[str, Any]] = []
        visited: List[str] = []
        g = 1.0
        reason = "completed"
        for hop, lc in enumerate(path, start=1):
            if lc not in self.channels:
                raise ValueError("未知通道：{}".format(lc))
            if lc in visited:
                reason = "closed_loop"
                trace.append({"hop": hop, "lc": lc, "gain": round(g, 6), "patency": self.patency(lc),
                              "blocked": self.channels[lc].blocked(), "note": "回到已访问通道 → 闭环终止"})
                break
            if hop > max_hops:
                reason = "max_hops"
                trace.append({"hop": hop, "lc": lc, "gain": round(g, 6), "patency": self.patency(lc),
                              "blocked": self.channels[lc].blocked(), "note": "跳数超上限 → 终止"})
                break
            p = self.patency(lc)
            blocked = self.channels[lc].blocked()
            trace.append({"hop": hop, "lc": lc, "gain": round(g, 6), "patency": p,
                          "blocked": blocked, "note": "通畅" if not blocked else "淤堵（<floor）"})
            if blocked:
                reason = "blocked"
                break
            visited.append(lc)
            self.channels[lc].load = min(self.channels[lc].budget,
                                         self.channels[lc].load + int(weight))
            g = g * gain
            if g < gain_floor:
                reason = "gain_floor"
                break
        return {"event": event, "path": tuple(path), "trace": trace, "reason": reason,
                "hops": len(trace), "tau_event": round(_fold(trace), 6)}

    # --- 贝叶斯衍射反演 ---
    def bayes_reroute(self, observed: float, top_k: int = 3) -> Dict[str, Any]:
        """贝叶斯衍射反演：给定「观测到达率」反推最可能被堵的通道。

        prior 均匀（1/12）；likelihood_i ∝ (1 − patency_i/ceil)；
        posterior_i = prior_i·L_i / Σ；返回 top_k 及归一化后验。
        纯确定性（无随机、无采样），可复现。
        """
        if not 0.0 <= observed <= 1.0:
            raise ValueError("observed 须在 0..1")
        lcs = self.lcs()
        prior = 1.0 / float(len(lcs))
        lik = {}
        for lc in lcs:
            p = self.patency(lc)
            ceil = self.channels[lc].ceil or 100
            base = 1.0 - float(p) / float(ceil)
            # 观测到达率越低，淤堵解释力越强：L_i = base × (1 + (1 − observed))
            lik[lc] = base * (1.0 + (1.0 - observed))
        total = sum(prior * v for v in lik.values())
        if total <= 0.0:
            post = {lc: prior for lc in lcs}
        else:
            post = {lc: (prior * lik[lc]) / total for lc in lcs}
        ranked = sorted(post.items(), key=lambda kv: (-kv[1], kv[0]))[:top_k]
        return {"observed": observed, "prior": round(prior, 6),
                "posterior": {k: round(v, 6) for k, v in post.items()},
                "top": [{"lc": k, "posterior": round(v, 6), "patency": self.patency(k)} for k, v in ranked],
                "normalized": round(sum(post.values()), 6)}


def _fold(trace: List[Dict[str, Any]]) -> float:
    """把 trace 折成一个确定性标量（用于同链两次传播的逐值比对）。"""
    s = 0.0
    for t in trace:
        s += t["gain"] * (t["patency"] + 1.0) / 100.0
    return s


# ---------------------------------------------------------------------------
# 四、四判据自检（供 org_gate G-M 门禁消费）
# ---------------------------------------------------------------------------

def check_channels() -> Dict[str, Any]:
    """判据 1：12 通道齐、分组齐、每通道有通畅度模型与上下限。"""
    bus = BusChannel()
    problems: List[str] = []
    if len(bus.channels) != 12:
        problems.append("通道数 != 12（实 {}）".format(len(bus.channels)))
    groups = {g["group"]: 0 for g in CHANNEL_GROUPS}
    for ch in bus.channels.values():
        if ch.group not in groups:
            problems.append("未登记分组：{}".format(ch.group))
            continue
        groups[ch.group] += 1
        if not (0 <= ch.floor <= ch.ceil <= ch.budget):
            problems.append("{} 边界不成立 floor/ceil/budget".format(ch.lc))
        if ch.patency() > ch.ceil:
            problems.append("{} 通畅度越上限".format(ch.lc))
    want = {g["group"]: g["count"] for g in CHANNEL_GROUPS}
    if groups != want:
        problems.append("分组计数不符：{} vs {}".format(groups, want))
    # 上下限可观测：press 后下降、release 后恢复、rollback 精确还原
    probe = bus.channels["LC03"]
    before = probe.patency()
    tok = probe.press(50)
    after = probe.patency()
    probe.release(50)
    restored = probe.patency()
    if not (after < before and restored == before):
        problems.append("通畅度上下限不可观测（{}→{}→{}）".format(before, after, restored))
    tok2 = probe.press(30)
    if not probe.rollback(tok2) or probe.patency() != before:
        problems.append("rollback_token 无法精确还原")
    if tok:  # 第一次 press 已 release，token 栈应被清空
        probe.rollback(tok)
    return {"pass": not problems, "problems": problems,
            "detail": {"channels": 12, "groups": groups, "sample": [probe.lc, before, after, restored]}}


def check_propagation() -> Dict[str, Any]:
    """判据 2：≥3 条示范链路可复现（含 LC02→LC03→LC10），两次运行逐值相同。"""
    problems: List[str] = []
    runs: List[Dict[str, Any]] = []
    for chain in DEMO_CHAINS:
        a = BusChannel().propagate("demo:" + chain["id"], chain["path"])
        b = BusChannel().propagate("demo:" + chain["id"], chain["path"])
        same = json.dumps(a, ensure_ascii=False, sort_keys=True) == \
               json.dumps(b, ensure_ascii=False, sort_keys=True)
        if not same:
            problems.append("链路 {} 两次传播不一致（不可复现）".format(chain["id"]))
        if a["reason"] != "completed":
            problems.append("链路 {} 基线运行即终止：{}".format(chain["id"], a["reason"]))
        runs.append({"id": chain["id"], "hops": a["hops"], "reason": a["reason"],
                     "tau": a["tau_event"], "reproducible": same})
    if len(DEMO_CHAINS) < 3:
        problems.append("示范链路不足 3 条")
    has_c02_c03_c10 = any(c["id"] == "C02-C03-C10" for c in DEMO_CHAINS)
    if not has_c02_c03_c10:
        problems.append("缺 C02→C03→C10 示范链")
    return {"pass": not problems, "problems": problems, "detail": {"chains": runs}}


def check_blocking() -> Dict[str, Any]:
    """判据 3：压低通畅度 → 阻塞触发 + 贝叶斯衍射反演定位到该通道。"""
    problems: List[str] = []
    bus = BusChannel()
    token = bus.press("LC03", 100, "阻塞演练：压到 0")
    rep = bus.propagate("blocking-probe", ("LC02", "LC03", "LC10"))
    if rep["reason"] != "blocked":
        problems.append("压低 LC03 未触发阻塞（reason={}）".format(rep["reason"]))
    last = rep["trace"][-1] if rep["trace"] else {}
    if last.get("lc") != "LC03" or not last.get("blocked"):
        problems.append("阻塞点不在 LC03：{}".format(last))
    post = bus.bayes_reroute(observed=0.2, top_k=3)
    top1 = post["top"][0]["lc"] if post["top"] else None
    if top1 != "LC03":
        problems.append("贝叶斯反演 top1 != LC03（实 {}）".format(top1))
    if abs(post["normalized"] - 1.0) > 1e-6:
        problems.append("后验未归一化：{}".format(post["normalized"]))
    rolled = bus.rollback("LC03", token)
    if not rolled or bus.patency("LC03") != 95:
        problems.append("阻塞演练未能回滚到基线（{}）".format(bus.patency("LC03")))
    return {"pass": not problems, "problems": problems,
            "detail": {"blocked_at": last.get("lc"), "reason": rep["reason"],
                       "top1": top1, "posterior_top": post["top"], "rolled_back": rolled}}


def check_termination() -> Dict[str, Any]:
    """判据 4：增益衰减 / 跳数上限 / 闭环终止 三类终止可观测。"""
    problems: List[str] = []
    seen: Dict[str, Any] = {}

    # ① 增益衰减：长链 + 较强衰减
    long_path = tuple(["LC01"] * 0 + ["LC01", "LC02", "LC03", "LC04", "LC05", "LC06",
                                      "LC07", "LC08", "LC09", "LC10", "LC11", "LC12"])
    a = BusChannel().propagate("term-gain", long_path, gain=0.85, max_hops=20, gain_floor=0.60)
    seen["gain_floor"] = a["reason"]

    # ② 跳数上限：把 max_hops 压到 2
    b = BusChannel().propagate("term-hops", ("LC06", "LC07", "LC08", "LC09"), max_hops=2)
    seen["max_hops"] = b["reason"]

    # ③ 闭环：路径里重复同一通道
    c = BusChannel().propagate("term-loop", ("LC10", "LC11", "LC10"))
    seen["closed_loop"] = c["reason"]

    # ④ 阻塞（安全网，另一类终止）
    d = BusChannel()
    d.press("LC09", 100)
    e = d.propagate("term-blocked", ("LC06", "LC09"))
    seen["blocked"] = e["reason"]

    for kind in ("gain_floor", "max_hops", "closed_loop"):
        if seen.get(kind) != kind:
            problems.append("{} 终止不可观测（实 {}）".format(kind, seen.get(kind)))
    if seen.get("blocked") != "blocked":
        problems.append("阻塞终止不可观测（实 {}）".format(seen.get("blocked")))
    return {"pass": not problems, "problems": problems, "detail": seen}


def self_check() -> Dict[str, Any]:
    """四判据自检总闸——G-M 门禁的实测证据源。"""
    parts = {
        "12 通道": check_channels(),
        "事件传播": check_propagation(),
        "阻塞机制": check_blocking(),
        "衰减与终止": check_termination(),
    }
    failed = [k for k, v in parts.items() if not v["pass"]]
    return {
        "schema": SCHEMA_VERSION,
        "criteria": 4,
        "passed": 4 - len(failed),
        "failed": failed,
        "verdict": "PASS" if not failed else "FAIL",
        "items": {k: {"pass": v["pass"], "problems": v["problems"], "detail": v["detail"]}
                  for k, v in parts.items()},
        "provenance": {
            "channels": "vector-sea/holoaeon-v4-cold-hot-plug/26_通道映射表.csv",
            "quota": "vector-sea/holoaeon-v4-cold-hot-plug/47_channel_quota.csv",
            "semantics": "data_六机制对照与通道映射.csv（六机制 meridian 行）",
        },
    }


# ---------------------------------------------------------------------------
# 五、台账落盘（确定性、无墙钟）
# ---------------------------------------------------------------------------

def build_table() -> Dict[str, Any]:
    bus = BusChannel()
    rows = [bus.channels[lc].to_dict() for lc in bus.lcs()]
    return {
        "schema": SCHEMA_VERSION,
        "batch": "V64-HANGOVER-ZERO",
        "dom": "C03 总线仓（G-M 门禁通关件）",
        "channels": 12,
        "groups": {g["group"]: g["count"] for g in CHANNEL_GROUPS},
        "rows": rows,
        "unmapped_targets": list(UNMAPPED_TARGETS),
        "demo_chains": [{"id": c["id"], "path": list(c["path"])} for c in DEMO_CHAINS],
        "provenance": self_check()["provenance"],
        "check": self_check(),
        "seal": SEAL,
    }


def write_table(path: Optional[str] = None) -> str:
    out = path or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)),
                                               ), "data", DATA_OUT_NAME)
    payload = build_table()
    io.open(out, "w", encoding="utf-8", newline="\n").write(
        json.dumps(payload, ensure_ascii=False, indent=1) + "\n")
    return out


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(argv if argv is not None else [])
    if not argv:
        print("用法：python -m holoaeon.bus_channel check | table [--out PATH]")
        return 1
    cmd = argv[0]
    if cmd == "check":
        rep = self_check()
        print(json.dumps(rep, ensure_ascii=False, indent=1))
        return 0 if rep["verdict"] == "PASS" else 1
    if cmd == "table":
        out = None
        if len(argv) > 1:
            if argv[1] != "--out" or len(argv) < 3:
                print("--out 需要路径参数")
                return 1
            out = argv[2]
        p = write_table(out)
        print("台账已写：{}".format(p))
        return 0
    print("未知命令：{}".format(cmd))
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
