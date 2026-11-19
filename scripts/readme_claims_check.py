# -*- coding: utf-8 -*-
# 另一份（开发副本）在 F:\doubaowork\holoaeon_lathe\readme_claims_check.py；以仓内 scripts/ 本件为准（V88 P1-A 方案A 复制，非移动）。
"""README 当前口径数字复算闸（仓外零侵入）：把「README 是否可信」从人工复核变成可复算判定。

判定对象 = 两份 README 的**当前口径位**（徽章 / 工程验收行 / 门禁行 / 清单行 / V41 小节存在性）。
历史批次行（V22/V38/V39/V40 小节）里的旧数字属当时实测，不参与判定；顶部宣言头单列为 STALE_HEADER 供裁决。
判定用「存在性」而非固定中英标签，避免中英措辞差异造成假红。
"""
from __future__ import annotations

import io
import json
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "reports", "readme_claims_check.json")


def run(cmd, cwd=REPO):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def measured():
    m = {}
    sys.path.insert(0, REPO)
    from holoaeon import spec  # noqa: E402
    m["doc_version"] = spec.DOC_VERSION
    m["head"] = subprocess.run(["git", "-C", REPO, "rev-parse", "--short", "HEAD"],
                               capture_output=True, text=True).stdout.strip()

    for key, path in (("unittest_main", "tests"),
                      ("unittest_v3", os.path.join("tests", "v3")),
                      ("unittest_verax", os.path.join("tests", "verax"))):
        rc, out = run([sys.executable, "-m", "unittest", "discover", "-s", path])
        hits = re.findall(r"Ran\s+(\d+)\s+tests", out)
        # 取最后一个（V54 实测教训）：套件内部若做兼容回归（TextTestRunner 自跑子套件），
        # 会先打印子套件的 "Ran N"（如 35/37），全局汇总恒在最后；取首个会误读成 35。
        m[key] = int(hits[-1]) if hits else None

    rc, out = run([sys.executable, "-m", "holoaeon.selftest"])
    hits = re.findall(r"(\d+)\s*/\s*(\d+)", out)
    m["selftest"] = "%s/%s" % hits[-1] if hits else ("OK" if rc == 0 else "FAIL")
    m["v3_gate"] = m.get("v3_gate") or ""

    rc, out = run([sys.executable, os.path.join("scripts", "v3_gate.py")])
    hit = re.search(r"(\d+)\s*/\s*(\d+)\s*PASS", out)
    m["v3_gate"] = "%s/%s" % (hit.group(1), hit.group(2)) if hit else ("OK" if rc == 0 else "FAIL")

    rc, out = run([sys.executable, os.path.join("scripts", "redline_scan.py")])
    hit = re.search(r"扫描文件数[:：]\s*(\d+)", out)
    m["redline_files"] = int(hit.group(1)) if hit else None
    m["redline_violations"] = 0 if "零违规" in out else None

    rc, out = run([sys.executable, os.path.join("scripts", "check_sums.py"), "."])
    hit = re.search(r'"total"\s*:\s*(\d+)', out)
    m["sums_total"] = int(hit.group(1)) if hit else None
    m["sums_ok"] = ('"ok": true' in out.replace(" ", " ")) or ("ok=true" in out)
    return m


def check(fn, m):
    t = io.open(os.path.join(REPO, fn), encoding="utf-8", newline="").read()
    L = t.split("\n")

    def has(pred):
        return any(pred(x) for x in L)

    a, b, c = m["unittest_main"], m["unittest_v3"], m["unittest_verax"]
    tot = a + b + c
    rows = []

    def add(name, readme, ok):
        rows.append({"claim": name, "readme": readme, "measured": str(ok if not callable(ok) else ok),
                     "verdict": "MATCH" if ok is True else "MISMATCH"})

    badge = has(lambda x: re.search(r"tests-%d%%2B%d%%2B%d" % (a, b, c), x) is not None)
    add("徽章 tests-%d%%2B%d%%2B%d" % (a, b, c), "tests-%d%%2B%d%%2B%d" % (a, b, c), badge)

    acc = has(lambda x: (("%d OK" % a) in x) and (
        (re.search(r"(合计|total)[^0-9]{0,12}%d" % tot, x) is not None)
        or (re.search(r"%d\*\*[^0-9]{0,8}(total|合计)" % tot, x) is not None)
        or (re.search(r"\(%d\)|=%d|%d\)" % (tot, tot, tot), x) is not None)))
    add("工程验收行（主套+合计）", "%d OK / 合计 %d" % (a, tot), acc)

    gate = has(lambda x: (("unittest %d OK" % a) in x) and (("redline %d 文件 0 违规" % m["redline_files"]) in x))
    add("门禁行（主套+redline）", "unittest %d OK / redline %d" % (a, m["redline_files"]), gate)

    sums = has(lambda x: (("清单 %d 条" % m["sums_total"]) in x)
               or (("%d 条 0 不匹配" % m["sums_total"]) in x)
               or (("%d entries" % m["sums_total"]) in x and "mismatch" in x))
    add("清单条数", "%d 条 0 不匹配" % m["sums_total"], sums)

    v41 = "### V41" in t
    add("### V41 小节存在", "present", v41)

    # 顶部宣言头：写死值才比对（STALE）；已改回读式的判 MATCH(readback)，防止「删掉数字就假绿」
    head = next((x for x in L if x.startswith("> 版本 V3") or x.startswith("> Version V3")), "")
    if ("回读" in head) or ("read back" in head.lower()) or ("readback" in head.lower()):
        rows.append({"claim": "宣言头 DOC/HEAD（回读式）", "readme": "readback-style",
                     "measured": "readback-style", "verdict": "MATCH"})
    else:
        doc_in = re.search(r"(DOC|docs)\s*`([0-9.]+)`", head)
        sha_in = re.search(r"HEAD\s*`([0-9a-f]{7,40})`", head)
        if doc_in:
            rows.append({"claim": "顶部宣言头 DOC", "readme": doc_in.group(2), "measured": m["doc_version"],
                         "verdict": "MATCH" if doc_in.group(2) == m["doc_version"] else "STALE_HEADER"})
        if sha_in:
            rows.append({"claim": "顶部宣言头 HEAD", "readme": sha_in.group(1), "measured": m["head"],
                         "verdict": "MATCH" if sha_in.group(1) == m["head"] else "STALE_HEADER"})
        if not (doc_in or sha_in):
            rows.append({"claim": "顶部宣言头", "readme": "(无写死值也无回读声明)", "measured": "-", "verdict": "MISMATCH"})

    # 中文侧另有「数字—命令对照表」：必须去硬编码（不得留"本机实测"写死列）
    if "README.zh" in fn:
        add("对照表去硬编码（无“| 本机实测 |”列）", "absent",
            not any(x.startswith("| 本机实测") for x in L))
        add("对照表改为回读判定列", "present",
            any("判定方式（一律回读，不写死）" in x for x in L))
    return rows


def main():
    m = measured()
    allrows = {fn: check(fn, m) for fn in ("README.zh-CN.md", "README.md")}
    bad = [r for v in allrows.values() for r in v if r["verdict"] == "MISMATCH"]
    stale = [r for v in allrows.values() for r in v if r["verdict"] == "STALE_HEADER"]
    res = {"schema": "README-CLAIMS-CHECK-v1.0", "measured": m, "readme": allrows,
           "counts": {"claims": sum(len(v) for v in allrows.values()), "mismatch": len(bad), "stale_header": len(stale)},
           "verdict": "PASS" if not bad else "FAIL"}
    io.open(OUT, "w", encoding="utf-8", newline="").write(json.dumps(res, ensure_ascii=False, indent=1))
    print("MEASURED:", json.dumps(m, ensure_ascii=False))
    for fn, rows in allrows.items():
        print("==", fn)
        for r in rows:
            print("  %-26s readme=%-22s measured=%-14s %s" % (r["claim"], r["readme"], r["measured"], r["verdict"]))
    print("VERDICT:", res["verdict"], "| mismatch=%d stale_header=%d" % (len(bad), len(stale)))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
