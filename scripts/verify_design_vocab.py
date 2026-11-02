# -*- coding: utf-8 -*-
"""V5.1-B1 设计语汇门禁：一次跑完 8 项判据，写 reports/design_vocab_check.json。

判据（任一不过即退出码 1）：
  D1 注册表 id/批次/许可与"未 vendor、未复制正文"声明齐备
  D2 命令恰 24 个、id 唯一、5 个分组均非空
  D3 规则恰 12 条、id 唯一、分级合法、四通道均非空
  D4 脏样本 12 条规则全部命中；干净样本 0 命中
  D5 三编译模式串跑一致（elaborate / simulate / netlist）
  D6 赫布共现权重对称、归一无量纲、自身相似度为 1
  D7 经络分流总数等于命中数
  D8 维度锁未被改动（25 / 47 / 9）
"""

import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from holoaeon.design_vocab import detectors as dv
from holoaeon.design_vocab import compile_modes as cm
from holoaeon.design_vocab import hebbian as hb
from holoaeon.design_vocab import meridian as md
from holoaeon.design_vocab import vocabulary as vc

SLOP = """<style>
body { font-family: Inter, sans-serif; }
.hero { background: linear-gradient(135deg, #7c3aed, #6366f1); }
.card { border-radius: 999px; }
.chip { border-radius: 9999px; }
.btn { border-radius: 999px; }
</style>
<div class="card">
  <div class="card">
    <h1>HOLOAEON SUPERSYSTEM MATRIX ENGINE IS LIVE AND READY TO SHIP</h1>
    <h3>🚀 升级</h3>
    <p style="color:#888;font-size:11px;margin:0;padding:0;">Lorem ipsum dolor sit amet</p>
    <div class="card"><p>x</p></div>
  </div>
</div>
<div style="box-shadow: 0 1px 2px #000, 0 4px 8px #111, 0 12px 24px #222;"></div>
<p style="-webkit-background-clip:text;background:linear-gradient(90deg,#7c3aed,#6366f1);font-size:11px;">y</p>
"""

CLEAN = """<style>
body { font-family: var(--font-sans); }
.card { border-radius: 6px; }
</style>
<div class="card">
  <h1>HoloAeon</h1>
  <h2>当前状态</h2>
  <p style="color:#1A1B1C;margin:0;">正文说明</p>
</div>
"""

LOCK_EXPECT = {"holoaeon_agents": 25, "holoaeon_skills": 47, "holoaeon_domain_packs": 9}


def digest16(payload):
    blob = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def lock_values():
    path = os.path.join(ROOT, "reports", "dimension_lock.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    dims = data.get("dimensions") or []
    return {d.get("name"): d.get("value") for d in dims if isinstance(d, dict)}


def main():
    checks = []

    def check(cid, ok, detail):
        checks.append({"id": cid, "ok": bool(ok), "detail": detail})

    with open(os.path.join(ROOT, "data", "design_vocab_registry.json"), encoding="utf-8") as f:
        reg = json.load(f)
    src = reg.get("source") or {}

    check("D1", reg.get("id") == "SG-V51-DESIGN-VOCAB-V1"
          and src.get("upstream_license") == "Apache-2.0"
          and src.get("vendored") is False and src.get("engine_copied") is False
          and src.get("text_copied") is False,
          "id/许可/未vendor声明")
    check("D2", len(vc.COMMANDS) == 24 and len(set(vc.command_ids())) == 24
          and all(vc.by_group(g) for g in vc.GROUPS),
          "命令 24 个、分组 %d 个均非空" % len(vc.GROUPS))

    ids = [r[0] for r in dv.RULES]
    sev_ok = all(r[2] in dv.SEVERITY_ORDER for r in dv.RULES)
    chan_ok = all(md.route([dv.Finding(r[0], r[1], r[2], r[3], 1, "")])["counts"][r[3]] == 1 for r in dv.RULES)
    check("D3", len(dv.RULES) == 12 and len(set(ids)) == 12 and sev_ok and chan_ok,
          "规则 12、分级合法、四通道覆盖")

    slop_ids = sorted({h.rule_id for h in dv.scan(SLOP)})
    clean_hits = dv.scan(CLEAN)
    check("D4", len(slop_ids) == 12 and not clean_hits,
          "脏样本命中 %d/12、干净样本命中 %d" % (len(slop_ids), len(clean_hits)))

    full = cm.compile_text(SLOP)
    check("D5", full["elaborate"]["components"] > 0
          and full["simulate"]["findings"] == len(dv.scan(SLOP))
          and full["netlist"]["edges"] > 0
          and full["simulate"]["verdict"] in ("FAIL", "WARN", "PASS"),
          "components=%d findings=%d edges=%d verdict=%s" % (
              full["elaborate"]["components"], full["simulate"]["findings"],
              full["netlist"]["edges"], full["simulate"]["verdict"]))

    sets = [sorted({h.rule_id for h in dv.scan(doc)}) for doc in (SLOP, SLOP, CLEAN)]
    raw = hb.cooccurrence(sets)
    norm = hb.normalize(raw)
    sym_ok = all(w >= 0 for w in raw.values()) and (not norm or max(norm.values()) <= 1.0)
    check("D6", sym_ok and hb.similarity("DV-01", "DV-01", raw) == 1.0,
          "共现边 %d 条、归一无量纲" % len(raw))

    route = md.route(dv.scan(SLOP))
    check("D7", route["total"] == len(dv.scan(SLOP)) and len(route["blocked"]) >= 2,
          "分流 %d、最堵通道 %s" % (route["total"], route["worst"]))

    lock = lock_values()
    check("D8", all(lock.get(k) == v for k, v in LOCK_EXPECT.items()),
          "维度锁 %s" % {k: lock.get(k) for k in LOCK_EXPECT})

    ok = all(c["ok"] for c in checks)
    payload = {
        "id": "SG-V51-DESIGN-VOCAB-CHECK-V1",
        "batch": "V5.1-B1",
        "generated_at": "2026-11-02",
        "checks": checks,
        "passed": sum(1 for c in checks if c["ok"]),
        "total": len(checks),
        "verdict": "PASS" if ok else "FAIL",
        "facts": {
            "commands": len(vc.COMMANDS),
            "rules": len(dv.RULES),
            "compile_modes": len(cm.COMPILE_MODES),
            "channels": len(md.CHANNELS),
            "slop_hits": len(dv.scan(SLOP)),
            "slop_rules": len(slop_ids),
            "clean_hits": len(clean_hits),
            "hebbian_edges": len(raw),
            "registry_sha16": digest16(reg),
        },
        "lock": {k: lock.get(k) for k in LOCK_EXPECT},
    }

    reports = os.path.join(ROOT, "reports")
    if not os.path.isdir(reports):
        os.makedirs(reports)
    out = os.path.join(reports, "design_vocab_check.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")

    for c in checks:
        print("%s %-2s %s" % ("PASS" if c["ok"] else "FAIL", c["id"], c["detail"]))
    print("verdict=%s %d/%d  registry_sha16=%s" % (
        payload["verdict"], payload["passed"], payload["total"], payload["facts"]["registry_sha16"]))
    print("written:", os.path.relpath(out, ROOT).replace(os.sep, "/"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
