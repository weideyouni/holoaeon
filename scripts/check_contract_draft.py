"""B1a 契约字段草案校验器（纯标准库 / 离线 / 只读）。

用法：
  python scripts/check_contract_draft.py            # 打印 JSON 结果，退出码 0/1
  python scripts/check_contract_draft.py --path <draft.md>

判据（对应 data/contract_v1_draft.md §六）：
  C1 顶层 6 必填 + 4 可选 = 10 行齐，每行类型/约束/示例非空
  C2 payload 白名单 6 键齐，每键类型与约束非空
  C3 三条口径决定 D1–D3 在案
  C4 两条示例块均为合法 JSON

不做的事：不写文件、不联网、不调 git、不 import 非标准库。
"""

import hashlib
import json
import os
import sys

REPO = os.environ.get("HOLOAEON_REPO", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_DRAFT = os.path.join(REPO, "data", "contract_v1_draft.md")

TOP_FIELDS = ["contract_id", "source", "target", "skill", "mechanism", "lane", "payload", "nonce", "budget", "note"]
PAYLOAD_KEYS = ["domain", "inputs", "outputs", "evidence", "redlines", "notes"]
DECISIONS = ["D1", "D2", "D3"]


def read_text(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def row_for(text, name):
    """定位 '| `name` | ...' 表格行，返回单元格列表；找不到返回 None。"""
    token = "| `" + name + "` |"
    for line in text.splitlines():
        if line.strip().startswith(token):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            return cells
    return None


def row_ok(cells, want):
    if not cells or len(cells) < want:
        return False, "cells={} want>={}".format(len(cells) if cells else 0, want)
    for c in cells[2:want]:
        if not c:
            return False, "empty cell"
    return True, "ok"


def json_blocks(text):
    blocks = []
    cur = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "```json":
            cur = []
            continue
        if cur is not None and stripped == "```":
            blocks.append("\n".join(cur))
            cur = None
            continue
        if cur is not None:
            cur.append(line)
    return blocks


def check(path):
    checks = []

    def add(cid, ok, detail):
        checks.append({"id": cid, "ok": bool(ok), "detail": detail})

    if not os.path.isfile(path):
        add("C0", False, "draft missing: " + path)
        return checks
    text = read_text(path)

    # C1 顶层 10 行
    miss, bad = [], []
    for name in TOP_FIELDS:
        cells = row_for(text, name)
        ok, detail = row_ok(cells, 5)
        if cells is None:
            miss.append(name)
        elif not ok:
            bad.append(name + ":" + detail)
    add("C1", not miss and not bad,
        "rows={} missing={} bad={}".format(len(TOP_FIELDS) - len(miss), miss, bad))

    # C2 payload 6 键
    miss2, bad2 = [], []
    for key in PAYLOAD_KEYS:
        cells = row_for(text, key)
        ok, detail = row_ok(cells, 5)
        if cells is None:
            miss2.append(key)
        elif not ok:
            bad2.append(key + ":" + detail)
    add("C2", not miss2 and not bad2,
        "keys={} missing={} bad={}".format(len(PAYLOAD_KEYS) - len(miss2), miss2, bad2))

    # C3 三条口径
    found = [d for d in DECISIONS if d in text]
    add("C3", len(found) == len(DECISIONS), "decisions={}".format(found))

    # C4 示例 JSON 可解析
    blocks = json_blocks(text)
    parsed, errs, objs = 0, [], []
    for i, b in enumerate(blocks):
        if '"contract_id"' not in b:
            continue
        try:
            obj = json.loads(b)
            if isinstance(obj, dict) and "contract_id" in obj:
                parsed += 1
                objs.append(obj)
        except Exception as exc:
            errs.append("block{}:{}".format(i, type(exc).__name__))
    add("C4", parsed >= 2 and not errs, "parsed={} errors={}".format(parsed, errs))

    # C5 示例指纹可复算（同参同指纹，见草案 §四）
    bad_ids = []
    for obj in objs:
        body = {}
        for k in ("source", "target", "skill", "mechanism", "lane", "payload"):
            if k in obj:
                body[k] = obj[k]
        canon = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        want = hashlib.sha256(canon.encode("utf-8")).hexdigest()[:12]
        if obj.get("contract_id") != want:
            bad_ids.append("{}!={}".format(obj.get("contract_id"), want))
    add("C5", not bad_ids, "recomputed={} mismatch={}".format(len(objs), bad_ids))

    return checks


def main(argv):
    path = DEFAULT_DRAFT
    if "--path" in argv:
        idx = argv.index("--path")
        if idx + 1 < len(argv):
            path = argv[idx + 1]
    checks = check(path)
    verdict = "PASS" if all(c["ok"] for c in checks) else "FAIL"
    payload = {
        "batch": "B1a",
        "draft": path,
        "verdict": verdict,
        "failed": [c["id"] for c in checks if not c["ok"]],
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
