# -*- coding: utf-8 -*-
"""
skill_matrix.selftest —— 六机制 + 索引 + 跨线程挂载的确定性自检
================================================================================
不依赖本机技能库（用临时迷你技能根自造），故任何机器、任何时刻结果一致。
"""
from __future__ import annotations

import json
import os
import shutil
import tempfile
from typing import Dict, List, Tuple

from . import index as Ix
from .mech import (CHANNELS, MECHANISMS, HebbianField, Meridian, build_skeleton,
                   decode, encode, heartbeat, hologram_residual, node_vector,
                   skeleton_robustness, skin_gate, text_signature)
from .runtime import MatrixRuntime

_MINI = {
    "alpha-data-skill": "数据清洗与统计报表",
    "beta-security-skill": "合规审查与安全校验红线",
    "gamma-writing-skill": "公众号文案写作与润色",
    "delta-bus-skill": "语义路由与消息总线",
}


def _mini_index(tmp: str) -> Tuple[dict, str]:
    root = os.path.join(tmp, "skills")
    for name, desc in _MINI.items():
        d = os.path.join(root, name)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "SKILL.md"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("---\nname: %s\ndescription: %s\n---\n\n正文\n" % (name, desc))
    idx = Ix.build([root])
    path = os.path.join(tmp, "index.json")
    Ix.save(idx, path)
    return idx, path


def run() -> Dict[str, object]:
    checks: List[Tuple[str, bool, str]] = []
    tmp = tempfile.mkdtemp(prefix="skill_matrix_")
    try:
        idx, path = _mini_index(tmp)

        # 1 全息心跳：确定性 + 越全越清晰
        names = ["a", "b", "c", "d", "e", "f"]
        h1, h2 = heartbeat(names), heartbeat(names)
        residual = [hologram_residual(names, k)["cosine"] for k in (2, 4, 6)]
        checks.append(("heartbeat", h1 == h2 and h1["nodes"] == 6 and len(h1["beats"]) == 6,
                       "sig=%s" % h1["signature"]))
        checks.append(("hologram", residual[0] < residual[1] < residual[2] and residual[2] == 1.0,
                       "cos=%s" % residual))

        # 2 细胞骨架
        sk = build_skeleton([("A", "B", 1), ("A", "C", 1), ("B", "C", 1), ("C", "D", 1)])
        rb = skeleton_robustness([("A", "B", 1), ("A", "C", 1), ("B", "C", 1), ("C", "D", 1)])
        checks.append(("skeleton", sk["nodes"] == 4 and sk["edges"] == 4
                       and sk["degree"]["C"] == 3 and rb["base_components"] == 1,
                       "backbone=%s" % sk["backbone"]))

        # 3 皮肤八层：正常放行 / 红线拒绝 / 缺字段拒绝
        ok = skin_gate({"query": "统计这周的销售额", "lane": "read"})
        bad = skin_gate({"query": "用 eval( 执行这段字符串", "lane": "read"})
        miss = skin_gate({"query": "x", "permission": 0})
        checks.append(("skin_pass", ok["verdict"] == "PASS" and len(ok["trace"]) == 8, ok.get("seal", "")))
        checks.append(("skin_redline", bad["verdict"] == "REJECT" and bad["layer"] == "L5_redline",
                       bad["trace"][-1]["reason"]))
        checks.append(("skin_schema", miss["verdict"] == "REJECT" and miss["layer"] == "L3_schema",
                       miss["trace"][-1]["reason"]))

        # 4 语义通信：编码→解码往返 + 篡改必失败
        env = encode("数据统计", {"n": 3})
        checks.append(("bus_roundtrip", decode(env)["ok"] and decode(env)["payload"] == {"n": 3},
                       env["fp"]))
        env2 = dict(env, payload={"n": 4})
        checks.append(("bus_tamper", decode(env2)["ok"] is False, "篡改载荷被识别"))

        # 5 赫布：幂等强化 + 衰减 + 最短路
        f1, f2 = HebbianField(), HebbianField()
        for _ in range(5):
            f1.co_activate("a", "b")
            f2.co_activate("a", "b")
        w = f1.weight("a", "b")
        dec = f1.decay_all()
        f3 = HebbianField()
        f3.co_activate("a", "b")
        f3.co_activate("b", "c")
        checks.append(("hebbian", w == f2.weight("a", "b") and 0.0 < w <= 0.99 and dec >= 1,
                       "w=%.4f" % w))
        checks.append(("hebbian_path", f3.path("a", "c")["path"] == ["a", "b", "c"],
                       str(f3.path("a", "c"))))

        # 6 经络：灌满—淤堵—再平衡
        m = Meridian(budget=10)
        for _ in range(10):
            m.flow("LC02", 1)
        blocked = m.flow("LC02", 1)["ok"] is False
        bal = m.balance()
        checks.append(("meridian", blocked and len(CHANNELS) == 12 and m.used["LC02"] == 10,
                       "blocked=%s moved=%s" % (blocked, bal["moved"])))

        # 7 索引：条数 / 机制归类 / digest 稳定 / 落盘字节可复算
        checks.append(("index_stats", idx["count"] == 4
                       and idx["stats"]["by_mechanism"]["skin_v6"] == 1,
                       str(idx["stats"]["by_mechanism"])))
        idx2 = Ix.build([idx["roots"][0]])
        checks.append(("index_digest_stable", idx2["digest"] == idx["digest"],
                       "%s == %s" % (idx2["digest"], idx["digest"])))

        # 8 运行时：调度 + 跨线程一致性
        rt = MatrixRuntime(idx)
        r = rt.dispatch("数据清洗 报表")
        probe = rt.concurrency_probe("合规审查 红线", n=8)
        checks.append(("runtime_dispatch", r["verdict"] == "PASS" and r["mechanism"] in MECHANISMS
                       and bool(r["channel"]), "%s/%s" % (r["mechanism"], r["channel"])))
        checks.append(("thread_safe", probe["identical"] and probe["distinct_views"] == 1,
                       "distinct=%d" % probe["distinct_views"]))

        # 9 挂载：只登记元数据，不执行外部脚本
        from ..kernel import Kernel
        k = Kernel()
        before = len(k.skills.names())
        info = rt.mount(k, limit=4)
        after = len(k.skills.names())
        checks.append(("mount_isolated", info["mounted"] == 4 and after == before + 4
                       and len([n for n in k.skills.names() if n.startswith("mx.")]) == 4,
                       "before=%d after=%d" % (before, after)))

        # 10 四人组复核
        q = rt.quartet_review("安全合规审查")
        checks.append(("quartet", len(q["panel"]) == 4
                       and {p["persona"] for p in q["panel"]} ==
                       {"P1_探微", "P2_筑基", "P3_构弦", "P4_持衡"},
                       ",".join(p["mechanism"] for p in q["panel"])))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    passed = sum(1 for _, ok, _ in checks if ok)
    return {"groups": len(checks), "passed": passed,
            "ok": passed == len(checks),
            "detail": [{"check": n, "ok": ok, "evidence": ev} for n, ok, ev in checks]}
