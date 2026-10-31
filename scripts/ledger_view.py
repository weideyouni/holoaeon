# -*- coding: utf-8 -*-
"""
ledger_view.py —— 账本 JSONL → 单文件 HTML（确定性静态渲染）
================================================================================
不是托管平台，是一条命令生成一个能双击打开的文件：
    python scripts\\ledger_view.py --sample data\\ledger_sample.jsonl   # 造样例账本
    python scripts\\ledger_view.py data\\ledger_sample.jsonl -o reports\\ledger.html

设计约束：
  - 零依赖、零外部资源（CSS 全内联，无 CDN、无字体引用、无 JS）；
  - 确定性：同一账本两次渲染逐字节一致（排序固定、不写时间戳、不写随机 id）；
  - 体积：单文件 < 500KB。

账本记录（nephron 体例，字段缺失时降级显示，不报错）：
    {"tick": 8, "seq": 1, "window_used": 2,
     "events": [{"seq": 1, "reason_code": "ok", "level": "info", "detail": "..."}],
     "updated_at": "2026-10-31T10:00:00Z", "fingerprint": "abc123"}
"""
from __future__ import annotations

import hashlib
import html
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SEV = {
    "ok": ("#1F6F5C", "allow"),
    "info": ("#33484F", "info"),
    "advise": ("#8A6A1E", "advise"),
    "warn": ("#8A6A1E", "warn"),
    "block": ("#B0472C", "block"),
    "error": ("#B0472C", "error"),
    "fault": ("#B0472C", "fault"),
}


# ------------------------------------------------------------ 读取
def load(path: str) -> list:
    records = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            s = line.strip()
            if not s:
                continue
            records.append(json.loads(s))
    records.sort(key=lambda r: (int(r.get("tick", 0)), int(r.get("seq", 0))))
    return records


def _sev(event: dict) -> tuple:
    code = str(event.get("reason_code") or event.get("reason") or "ok")
    level = str(event.get("level") or "")
    if level in SEV and level not in ("info",):
        return SEV[level]
    if code in SEV:
        return SEV[code]
    if code.startswith("block") or "blocked" in code:
        return SEV["block"]
    return SEV["info"]


def _is_divergent(event: dict) -> bool:
    if event.get("ok") is False:
        return True
    return str(event.get("level") or "").lower() in ("warn", "error", "fault", "block")


# ------------------------------------------------------------ 渲染
def render(records: list, title: str = "HoloAeon 账本视图") -> str:
    by_tick = {}
    for r in records:
        by_tick.setdefault(int(r.get("tick", 0)), []).append(r)
    ticks = sorted(by_tick)
    total_events = sum(len(r.get("events") or []) for r in records)
    divergences = [(r, e) for r in records for e in (r.get("events") or []) if _is_divergent(e)]
    fp = hashlib.sha256(
        json.dumps(records, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()[:16]

    parts = [
        "<!DOCTYPE html>",
        '<html lang="zh-CN"><head><meta charset="utf-8">',
        "<title>%s</title>" % html.escape(title),
        "<style>",
        "*{box-sizing:border-box}body{margin:0;background:#E3EAEC;color:#10262C;"
        "font:14px/1.65 'Microsoft YaHei',system-ui,sans-serif}",
        ".wrap{max-width:1080px;margin:0 auto;padding:28px 20px 56px}",
        "h1{font:600 26px/1.3 Georgia,'SimSun',serif;margin:0 0 6px}",
        ".meta{font:12px/1.6 Consolas,monospace;color:#33484F;border-top:1px solid #10262C;"
        "border-bottom:1px solid #10262C;padding:8px 0;margin:12px 0 24px;"
        "display:flex;gap:24px;flex-wrap:wrap}",
        "h2{font:600 17px/1.4 Georgia,'SimSun',serif;margin:28px 0 10px;"
        "border-left:3px solid #10262C;padding-left:10px}",
        "table{width:100%;border-collapse:collapse;background:#FFF;margin:8px 0 16px}",
        "th,td{border:1px solid #10262C;padding:6px 10px;text-align:left;vertical-align:top;"
        "font-size:13px}th{background:#F3F6F7}td.n{font-family:Consolas,monospace}",
        ".tick{background:#FFF;border:1px solid #10262C;margin:0 0 14px}",
        ".tick-h{display:flex;gap:16px;padding:8px 12px;border-bottom:1px solid #10262C;"
        "font:13px/1.5 Consolas,monospace;background:#F3F6F7}",
        ".ev{display:block;padding:6px 12px;border-left:4px solid #10262C;margin:6px 10px;"
        "background:#FBFCFC}",
        ".ev .code{font-family:Consolas,monospace;font-weight:600}",
        ".ev .who{color:#33484F;margin-left:10px}",
        ".diverge{border-left-color:#B0472C;background:#FDF3F0}",
        ".tag{display:inline-block;font:11px/1.6 Consolas,monospace;padding:0 6px;"
        "border:1px solid currentColor;margin-left:8px}",
        "footer{margin-top:32px;border-top:1px solid #10262C;padding-top:10px;"
        "font:12px/1.6 Consolas,monospace;color:#33484F}",
        "</style></head><body><div class=\"wrap\">",
        "<h1>%s</h1>" % html.escape(title),
        '<div class="meta"><span>ledger_fp=%s</span><span>ticks=%d</span>'
        "<span>records=%d</span><span>events=%d</span><span>divergences=%d</span></div>"
        % (fp, len(ticks), len(records), total_events, len(divergences)),
        '<div class="meta"><span>渲染口径：确定性静态渲染，无 JS、无外部资源；'
        "相册时间戳不进输出，故同账本两次渲染字节一致</span></div>",
    ]

    # 视图一：事件时间线
    parts.append("<h2>一 · 事件时间线（按 tick 分组，理由码着色）</h2>")
    if not ticks:
        parts.append("<p>账本为空。</p>")
    for t in ticks:
        recs = by_tick[t]
        used = sum(int(r.get("window_used") or 0) for r in recs)
        parts.append('<div class="tick"><div class="tick-h">'
                     "<span>tick=%d</span><span>records=%d</span>"
                     "<span>window_used=%d</span></div>" % (t, len(recs), used))
        for r in recs:
            events = r.get("events") or []
            if not events:
                parts.append('<div class="ev"><span class="code">(空)</span>'
                             '<span class="who">seq=%s 无事件</span></div>'
                             % html.escape(str(r.get("seq"))))
            for e in events:
                color, label = _sev(e)
                cls = "ev diverge" if _is_divergent(e) else "ev"
                code = html.escape(str(e.get("reason_code") or e.get("reason") or "ok"))
                detail = html.escape(str(e.get("detail") or e.get("note") or ""))
                who = html.escape(str(e.get("agent_id") or e.get("actor") or ""))
                parts.append(
                    '<div class="%s" style="border-left-color:%s">'
                    '<span class="code" style="color:%s">%s</span>'
                    '<span class="tag" style="color:%s">%s</span>'
                    '<span class="who">%s%s</span></div>'
                    % (cls, color, color, code, color, label, who,
                       ("｜" + detail) if detail else "")
                )
        parts.append("</div>")

    # 视图二：窗口构成表
    parts.append("<h2>二 · 窗口构成（每 tick 的记录数与窗口占用）</h2>")
    parts.append("<table><tr><th>tick</th><th>records</th><th>window_used</th>"
                 "<th>events</th><th>fingerprint</th></tr>")
    for t in ticks:
        recs = by_tick[t]
        used = sum(int(r.get("window_used") or 0) for r in recs)
        evn = sum(len(r.get("events") or []) for r in recs)
        fps = ",".join(str(r.get("fingerprint") or "-") for r in recs)[:60]
        parts.append('<tr><td class="n">%d</td><td class="n">%d</td>'
                     '<td class="n">%d</td><td class="n">%d</td>'
                     '<td class="n">%s</td></tr>'
                     % (t, len(recs), used, evn, html.escape(fps)))
    parts.append("</table>")

    # 视图三：分歧记录
    parts.append("<h2>三 · 分歧记录（warn / error / block / ok=false）</h2>")
    if not divergences:
        parts.append('<p>无分歧记录。</p>')
    else:
        parts.append("<table><tr><th>tick</th><th>seq</th><th>理由码</th>"
                     "<th>级别</th><th>明细</th></tr>")
        for r, e in divergences:
            parts.append('<tr><td class="n">%s</td><td class="n">%s</td>'
                         '<td class="n" style="color:%s">%s</td><td>%s</td>'
                         '<td>%s</td></tr>'
                         % (html.escape(str(r.get("tick"))),
                            html.escape(str(e.get("seq", r.get("seq")))),
                            _sev(e)[0],
                            html.escape(str(e.get("reason_code") or e.get("reason") or "")),
                            html.escape(str(e.get("level") or "")),
                            html.escape(str(e.get("detail") or ""))))
        parts.append("</table>")

    parts += [
        "<footer>%s</footer>" % html.escape(
            "ledger_fp=%s ｜ 零依赖静态渲染 ｜ 仿真 ≠ 证明，碳基终裁" % fp),
        "</div></body></html>",
    ]
    return "\n".join(parts)


# ------------------------------------------------------------ 样例账本
def make_sample(path: str) -> list:
    """用内核 tick + 守卫裁决造一份确定性样例账本（不含真实时间戳）。"""
    sys.path.insert(0, ROOT)
    from holoaeon.kernel import Kernel
    from holoaeon.packs import PACK_ORDER, get_pack

    k = Kernel()
    for key in PACK_ORDER:
        get_pack(key).install(k)
    records = []
    ticks = [k.tick() for _ in range(6)]
    for i, t in enumerate(ticks):
        events = [
            {"seq": 0, "reason_code": "ok", "level": "info",
             "detail": "tick 心跳 active=%d idle=%d" % (t.get("active", 0), t.get("idle", 0))},
        ]
        if i == 2:
            events.append({"seq": 1, "reason_code": "advise", "level": "advise",
                           "detail": "L8 trace 未包含 sender（放行但记录）"})
        if i == 4:
            events.append({"seq": 1, "reason_code": "block", "level": "block",
                           "detail": "L3 命中危险模式：os.system"})
        records.append({
            "tick": t.get("tick", i + 1),
            "seq": 0,
            "window_used": 1 if i < 3 else 2,
            "events": events,
            "updated_at": "2026-10-31T10:00:00Z",
            "fingerprint": "fp%02d" % (i + 1),
        })
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        for r in records:
            fh.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
    return records


def main(argv: list) -> int:
    args = [a for a in argv[1:] if not a.startswith("-")]
    out = "reports/ledger.html"
    for i, a in enumerate(argv):
        if a in ("-o", "--out") and i + 1 < len(argv):
            out = argv[i + 1]
    if "--sample" in argv:
        idx = argv.index("--sample")
        target = argv[idx + 1] if idx + 1 < len(argv) else os.path.join(ROOT, "data", "ledger_sample.jsonl")
        target = target if os.path.isabs(target) else os.path.join(ROOT, target)
        recs = make_sample(target)
        print("sample written: %s (%d records)" % (target, len(recs)))
        args = [target]
    elif not args:
        print("用法：python scripts\\ledger_view.py <ledger.jsonl> [-o out.html] | --sample")
        return 2
    src = args[0] if os.path.isabs(args[0]) else os.path.join(ROOT, args[0])
    records = load(src)
    doc = render(records, title="HoloAeon 账本视图 · %s" % os.path.basename(src))
    out_abs = out if os.path.isabs(out) else os.path.join(ROOT, out)
    os.makedirs(os.path.dirname(out_abs), exist_ok=True)
    with open(out_abs, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(doc)
    size = os.path.getsize(out_abs)
    sha = hashlib.sha256(doc.encode("utf-8")).hexdigest()[:16]
    print("html: %s  size=%d bytes  sha=%s  records=%d" % (out_abs, size, sha, len(records)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
