# -*- coding: utf-8 -*-
"""ClaimsGate — 叙述位与外部规定版本双注册簿闸门（V75 · claims 观测层 · CLAIMS-GATE-v1）

第一性原理
---------------------------------------------------------------
一个会随时间变化的事实，被复制成静态文本副本，而副本没有单一真源、
没有核实时间、没有过期判据 ——「README 写 526 而实测 1782」与
「README 写 2024-11-05 而代码支持 2026-07-28」是同一种病。

本闸不是新能力：它把 V38 `check_sums` 的「单一真源 → 复算闸 → 任一
mismatch 即红」推广到**叙述层**与**外部规定层**。升维句：
把「代码跑在文档前面」反转为「文档是代码的只读视图，外部规定是带核
实时间戳的指针」。

七面判据（每面都必须先证会红）
---------------------------------------------------------------
1. claim_registered      活体时变声明逐条有注册项（结构化清单比对）
2. readback_consistent   current 项的回读值 == expected_from 指向的真源
3. historical_timeboxed  historical 必带 as_of_batch + timeboxed 且不占活体位
4. regulation_pinned     规定针四必填字段齐、status 合法
5. pin_freshness         verified_at 未超 max_age_days；unknown 须显式登记
6. determinism_self_digest  两跑同 digest；self_digest 抓「建完改报告」
7. chain_position_coverage  模块头 docstring 显式 ring 声明的模块，必须有
                            模块级 CHAIN_POSITION 且 ring 一致（走 AST，不走文本正则）

诚实边界（写在这里，不只是写在回执里）
---------------------------------------------------------------
· `verified_at` 是人写快照，本模块**不联网**核实规定是否现行有效，只判超期；
· `unknown` 是合法状态（对齐 V69 `KNOWN_VACUUM`），必须显式登记，不许化装成已修复；
· 面 2 保证的是「文档视图 == 批次回执记录」，不是「重跑一遍测试」——
  主套数的真源是实跑，闸只锁视图不许漂移；
· 零第三方 import / 零网络 / 不调 subprocess / 不写任何文件 / 无搬运函数。

封口密语：潮起开门，潮落闭嘴。
"""
import ast
import hashlib
import json
import os
import re
import sys

SEAL = "潮起开门，潮落闭嘴"

SCHEMA = "CLAIMS-GATE-v1"
MAX_PIN_AGE_DAYS = 180
REQUIRED_PIN_FIELDS = ("doc_no", "version", "verified_at", "status")
VALID_PIN_STATUS = ("current", "superseded", "unknown")
VALID_CLAIM_KIND = ("current", "historical", "narrative")
REQUIRED_CLAIM_FIELDS = ("id", "kind", "readback", "expected_from", "sha16",
                         "as_of_batch", "timeboxed", "note", "evidence_class")

FACES = ("claim_registered", "readback_consistent", "historical_timeboxed",
         "regulation_pinned", "pin_freshness", "determinism_self_digest",
         "chain_position_coverage")

# 活体位：这些 id 必须出现在注册簿里（面 1）。
# 取值 = 与 README/规格里的活体副本一一对应的位，不是全部文本。
LIVE_POSITIONS = (
    "badge_tests_zh", "badge_tests_en",
    "acceptance_suite_zh", "acceptance_suite_en",
    "gate_suite_zh", "gate_redline_zh",
    "redline_files_computed", "checklist_entries",
    "doc_version_spec",
    "ring_count_zh", "batch_count_zh", "pyfiles_command_zh",
)

CN_DIGITS = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7,
             "八": 8, "九": 9, "十": 10, "十一": 11, "十二": 12, "十三": 13,
             "十四": 14, "十五": 15, "十六": 16, "十七": 17, "十八": 18,
             "十九": 19, "二十": 20, "二十一": 21, "二十二": 22,
             "二十三": 23, "二十四": 24}

EN_RING = re.compile(r"\bring\s*(\d+)\b")
CN_RING = re.compile(r"第([一二三四五六七八九十]+)环")


# ---------------------------------------------------------------------------
# 路径与加载
# ---------------------------------------------------------------------------
def repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def default_registry_path():
    return os.path.join(repo_root(), "data", "claims_registry.json")


def load_registry(path=None):
    """读注册簿（只读）。缺文件即抛 FileNotFoundError，由调用方记 INCOMPLETE。"""
    p = path or default_registry_path()
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _read_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# 回读器：结构化取值，不走「全文找数字」
# ---------------------------------------------------------------------------
def _ctx(root=None, texts=None):
    return {"root": root or repo_root(), "texts": dict(texts or {})}


def _text(ctx, key, relpath):
    if key in ctx["texts"]:
        return ctx["texts"][key]
    return _read_text(os.path.join(ctx["root"], relpath))


def _first_int(pattern, text):
    m = re.search(pattern, text)
    return int(m.group(1)) if m else None


def _last_int(pattern, text):
    """取最后一次匹配（活体口径行通常在文档后段；历史段会先命中旧值）。"""
    m = None
    for m in re.finditer(pattern, text):
        pass
    return int(m.group(1)) if m else None


def _count_py(root, recursive):
    pkg = os.path.join(root, "holoaeon")
    if recursive:
        return sum(1 for base, _dirs, files in os.walk(pkg)
                   for f in files if f.endswith(".py"))
    return sum(1 for f in os.listdir(pkg) if f.endswith(".py"))


def _sums_entries(root):
    path = os.path.join(root, "SHA256SUMS")
    if not os.path.exists(path):
        return None
    n = 0
    for line in _read_text(path).splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        n += 1
    return n


def _spec_doc_version(root):
    text = _read_text(os.path.join(root, "holoaeon", "spec.py"))
    m = re.search(r'DOC_VERSION\s*=\s*"([^"]+)"', text)
    return m.group(1) if m else None


READBACKS = {
    # 徽章（shields.io 静态值）：取徽章里的第一段数字（主套数）
    "readme.zh.tests_badge": lambda c: _first_int(
        r"badge/tests-(\d+)%2B", _text(c, "readme_zh", "README.zh-CN.md")),
    "readme.en.tests_badge": lambda c: _first_int(
        r"badge/tests-(\d+)%2B", _text(c, "readme_en", "README.md")),
    # 工程验收行（活体口径）
    "readme.zh.acceptance_main": lambda c: _last_int(
        r"主套单测\s*\*\*(\d+)\s*OK\*\*", _text(c, "readme_zh", "README.zh-CN.md")),
    "readme.en.acceptance_main": lambda c: _last_int(
        r"main suite\s*\*\*(\d+)\s*OK\*\*", _text(c, "readme_en", "README.md")),
    # 门禁行
    "readme.zh.gate_unittest": lambda c: _first_int(
        r"\| 门禁 \|[^\n]*unittest\s+(\d+)\s*OK",
        _text(c, "readme_zh", "README.zh-CN.md")),
    "readme.zh.gate_redline": lambda c: _first_int(
        r"redline\s+(\d+)\s+文件\s+0\s+违规", _text(c, "readme_zh", "README.zh-CN.md")),
    # 复算闸条数（活体口径）
    "readme.zh.checklist_entries": lambda c: _first_int(
        r"复算闸\s*\*\*(\d+)\s*条\s*0\s*不匹配\*\*",
        _text(c, "readme_zh", "README.zh-CN.md")),
    # 计算值（独立真源，不是文本副本）
    "computed.py_recursive": lambda c: _count_py(c["root"], True),
    "computed.py_top": lambda c: _count_py(c["root"], False),
    "computed.sums_entries": lambda c: _sums_entries(c["root"]),
    "spec.doc_version": lambda c: _spec_doc_version(c["root"]),
    # 回读式声明：文本里必须显式写「回读」二字（V41P 教训：删掉数字就假绿）
    "readme.zh.ring_readback": lambda c: _has_readback(
        _text(c, "readme_zh", "README.zh-CN.md"), "领域编排闸门"),
    "readme.zh.batch_readback": lambda c: _has_readback(
        _text(c, "readme_zh", "README.zh-CN.md"), "批次数不写死"),
    "readme.zh.pyfiles_recursive": lambda c: _uses_find(
        _text(c, "readme_zh", "README.zh-CN.md")),
}


def _has_readback(text, anchor):
    """锚点所在段落里必须出现「回读」字样；找不到锚点返回 False（假绿防线）。"""
    for i, line in enumerate(text.splitlines()):
        if anchor in line:
            return ("回读" in line) or ("readback" in line.lower())
    return False


def _uses_find(text):
    return bool(re.search(r"find\s+holoaeon\s+-name\s+'\*\.py'", text))


def readback(claim, ctx=None):
    """按 claim['readback'] 取结构化回读值；未知键返回 _UNKNOWN 便于判红。"""
    c = ctx or _ctx()
    key = claim.get("readback")
    fn = READBACKS.get(key)
    if fn is None:
        return _UNKNOWN
    try:
        return fn(c)
    except (OSError, ValueError, KeyError):
        return _UNKNOWN


class _Unknown(object):
    def __repr__(self):
        return "<UNKNOWN>"


_UNKNOWN = _Unknown()


# ---------------------------------------------------------------------------
# expected_from 解析：receipt.<field> / computed.<name> / literal.<id>
# ---------------------------------------------------------------------------
def _receipt(ctx):
    p = os.path.join(ctx["root"], "reports", "v75_receipt.json")
    if not os.path.exists(p):
        return None
    try:
        return _load_json(p)
    except ValueError:
        return None


def _int_of(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        m = re.search(r"(\d+)", value)
        return int(m.group(1)) if m else None
    return None


def _dig(obj, path):
    for key in path.split("."):
        if not isinstance(obj, dict):
            return None
        obj = obj.get(key)
    return obj


def resolve_expected(claim, ctx=None):
    c = ctx or _ctx()
    src = claim.get("expected_from") or ""
    if src.startswith("receipt."):
        rec = _receipt(c)
        if rec is None:
            return _UNKNOWN
        return _dig(rec, src.split(".", 1)[1])
    if src.startswith("computed."):
        name = "computed." + src.split(".", 1)[1]
        fn = READBACKS.get(name)
        return fn(c) if fn else _UNKNOWN
    if src.startswith("narrative."):
        return "readback"
    return _UNKNOWN


# ---------------------------------------------------------------------------
# 面 1-3：文档声明
# ---------------------------------------------------------------------------
def check_doc_claims(reg, ctx=None):
    """面 1 / 2 / 3 的失败清单。"""
    c = ctx or _ctx()
    fails = []
    claims = reg.get("doc_claims") or []
    ids = [x.get("id") for x in claims if isinstance(x, dict)]

    # 面 1：注册完整性（字段齐 + 活体位覆盖）
    for item in claims:
        if not isinstance(item, dict):
            fails.append({"face": "claim_registered", "id": "?", "detail": "非对象项"})
            continue
        miss = [k for k in REQUIRED_CLAIM_FIELDS if k not in item]
        if miss:
            fails.append({"face": "claim_registered", "id": item.get("id"),
                          "detail": "INCOMPLETE 缺字段 %s" % ",".join(miss)})
        kind = item.get("kind")
        if kind not in VALID_CLAIM_KIND:
            fails.append({"face": "claim_registered", "id": item.get("id"),
                          "detail": "kind=%r 非法" % (kind,)})
    for live in LIVE_POSITIONS:
        if live not in ids:
            fails.append({"face": "claim_registered", "id": live,
                          "detail": "活体位未注册"})

    live_ids = set(LIVE_POSITIONS)
    for item in claims:
        if not isinstance(item, dict):
            continue
        cid = item.get("id")
        kind = item.get("kind")

        # 面 2：current 回读一致
        if kind == "current":
            got = readback(item, c)
            exp = resolve_expected(item, c)
            if got is _UNKNOWN:
                fails.append({"face": "readback_consistent", "id": cid,
                              "detail": "回读键未知: %r" % (item.get("readback"),)})
            elif exp is _UNKNOWN or exp is None:
                fails.append({"face": "readback_consistent", "id": cid,
                              "detail": "INCOMPLETE expected_from 不可解析"})
            else:
                g_i, e_i = _int_of(got), _int_of(exp)
                if isinstance(got, str) and isinstance(exp, str) and g_i is None:
                    ok = got.strip() == exp.strip()
                elif g_i is None or e_i is None:
                    ok = got == exp
                else:
                    ok = g_i == e_i
                if not ok:
                    fails.append({"face": "readback_consistent", "id": cid,
                                  "detail": "MISMATCH readback=%r expected=%r" % (got, exp)})

        # 面 2（叙述项）：必须写回读式，不许写死
        if kind == "narrative":
            got = readback(item, c)
            if got is _UNKNOWN:
                fails.append({"face": "readback_consistent", "id": cid,
                              "detail": "回读键未知: %r" % (item.get("readback"),)})
            elif not got:
                fails.append({"face": "readback_consistent", "id": cid,
                              "detail": "叙述位未写回读式（写死或锚点缺失）"})

        # 面 3：historical 时点盒
        if kind == "historical":
            if not item.get("as_of_batch"):
                fails.append({"face": "historical_timeboxed", "id": cid,
                              "detail": "historical 缺 as_of_batch"})
            if not item.get("timeboxed"):
                fails.append({"face": "historical_timeboxed", "id": cid,
                              "detail": "historical 未标 timeboxed=true"})
            if cid in live_ids:
                fails.append({"face": "historical_timeboxed", "id": cid,
                              "detail": "historical 占了活体位"})
    return fails


# ---------------------------------------------------------------------------
# 面 4-5：外部规定针
# ---------------------------------------------------------------------------
def _age_days(verified_at, today):
    import datetime
    try:
        d = datetime.date(*[int(x) for x in str(verified_at).split("-")])
    except (ValueError, TypeError):
        return None
    return (today - d).days


def check_regulation_pins(reg, today=None):
    import datetime
    fails = []
    pins = reg.get("regulation_pins") or []
    if today is None:
        today = datetime.date.today()
    elif isinstance(today, str):
        today = datetime.date(*[int(x) for x in today.split("-")])
    for pin in pins:
        if not isinstance(pin, dict):
            fails.append({"face": "regulation_pinned", "id": "?", "detail": "非对象项"})
            continue
        pid = pin.get("id")
        miss = [k for k in REQUIRED_PIN_FIELDS if not pin.get(k)]
        if miss:
            fails.append({"face": "regulation_pinned", "id": pid,
                          "detail": "INCOMPLETE 缺 %s" % ",".join(miss)})
        status = pin.get("status")
        if status not in VALID_PIN_STATUS:
            fails.append({"face": "regulation_pinned", "id": pid,
                          "detail": "status=%r 非法" % (status,)})
        if not pin.get("source_pointer"):
            fails.append({"face": "regulation_pinned", "id": pid,
                          "detail": "缺 source_pointer（指针纪律）"})

        # 面 5：新鲜度
        if status in ("current", "superseded"):
            age = _age_days(pin.get("verified_at"), today)
            limit = pin.get("max_age_days") or MAX_PIN_AGE_DAYS
            if age is None:
                fails.append({"face": "pin_freshness", "id": pid,
                              "detail": "verified_at 不可解析"})
            elif age < 0:
                fails.append({"face": "pin_freshness", "id": pid,
                              "detail": "verified_at 在未来（%s）" % (pin.get("verified_at"),)})
            elif age > limit:
                fails.append({"face": "pin_freshness", "id": pid,
                              "detail": "STALE age=%d > %d" % (age, limit)})
        elif status == "unknown":
            if not pin.get("note"):
                fails.append({"face": "pin_freshness", "id": pid,
                              "detail": "unknown 须带 note 显式登记"})
    return fails


# ---------------------------------------------------------------------------
# 面 6：确定性 + 自摘要
# ---------------------------------------------------------------------------
def _canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha16(obj):
    return hashlib.sha256(_canonical(obj).encode("utf-8")).hexdigest()[:16]


def self_digest(reg):
    """注册簿自摘要：不含 self_digest 字段本身。"""
    payload = {k: v for k, v in reg.items() if k != "self_digest"}
    return _sha16(payload)


def check_self_digest(reg):
    declared = reg.get("self_digest")
    if not declared:
        return [{"face": "determinism_self_digest", "id": "registry",
                 "detail": "self_digest 未填"}]
    actual = self_digest(reg)
    if declared != actual:
        return [{"face": "determinism_self_digest", "id": "registry",
                 "detail": "self_digest %r != 实际 %r（建完改过注册簿）" % (declared, actual)}]
    return []


# ---------------------------------------------------------------------------
# 面 7：链位覆盖（AST，不走文本正则）
# ---------------------------------------------------------------------------
def _declared_rings(doc):
    """取 docstring 前 3 行（标题区）里的 ring 声明。

    英文 `ringN` 优先；紧邻全角左括号的形制视为「引用他环」，排除。
    返回 (value, ambiguous)：单值 → (int, False)；多值 → (None, True)。
    """
    head = "\n".join(doc.splitlines()[:3])
    en, cn = [], []
    for m in EN_RING.finditer(head):
        start = m.start()
        if start > 0 and head[start - 1] == "（":
            continue  # 「（ring11 召回层）」= 引用，不是自我声明
        en.append(int(m.group(1)))
    for m in CN_RING.finditer(head):
        v = CN_DIGITS.get(m.group(1))
        if v:
            cn.append(v)
    vals = en if en else cn
    uniq = sorted(set(vals))
    if len(uniq) == 1:
        return uniq[0], False
    if len(uniq) > 1:
        return None, True
    return None, False


def check_chain_position(pkg_dir=None):
    """面 7：docstring 声明 ring 的模块必须有模块级 CHAIN_POSITION 且 ring 一致。"""
    pkg = pkg_dir or os.path.join(repo_root(), "holoaeon")
    fails = []
    declared = 0
    constants = 0
    verified = 0
    for fn in sorted(os.listdir(pkg)):
        if not fn.endswith(".py"):
            continue
        path = os.path.join(pkg, fn)
        try:
            tree = ast.parse(_read_text(path))
        except SyntaxError:
            fails.append({"face": "chain_position_coverage", "id": fn,
                          "detail": "SYNTAX 无法解析"})
            continue
        cp_ring = None
        has_cp = False
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(
                    isinstance(t, ast.Name) and t.id == "CHAIN_POSITION" for t in node.targets):
                has_cp = True
                try:
                    val = ast.literal_eval(node.value)
                except (ValueError, SyntaxError):
                    val = None
                if isinstance(val, dict):
                    cp_ring = val.get("ring")
                break
        if has_cp:
            constants += 1
        ring, ambiguous = _declared_rings(ast.get_docstring(tree) or "")
        if not ring and not ambiguous:
            continue
        declared += 1
        if not has_cp:
            fails.append({"face": "chain_position_coverage", "id": fn,
                          "detail": "UNLOCATED 声明 ring=%s 但无 CHAIN_POSITION" % (ring if ring else "?",)})
            continue
        if ambiguous:
            verified += 1  # 提及多环（引用/列举）：只要求常量在位
            continue
        if cp_ring != ring:
            fails.append({"face": "chain_position_coverage", "id": fn,
                          "detail": "MISMATCH 声明 ring=%d / 常量 ring=%r" % (ring, cp_ring)})
            continue
        verified += 1
    return {"declared": declared, "constants": constants, "verified": verified,
            "fails": fails}


# ---------------------------------------------------------------------------
# 聚合
# ---------------------------------------------------------------------------
def _totals(reg):
    claims = reg.get("doc_claims") or []
    return {
        "doc_claims": len(claims),
        "regulation_pins": len(reg.get("regulation_pins") or []),
        "historical": sum(1 for x in claims if isinstance(x, dict) and x.get("kind") == "historical"),
        "narrative": sum(1 for x in claims if isinstance(x, dict) and x.get("kind") == "narrative"),
    }


def verify(reg=None, ctx=None, today=None):
    """七面聚合，返回 {verdict, faces, mismatch, digest, ...}。纯函数，两跑同 digest。"""
    r = reg if reg is not None else load_registry()
    c = ctx or _ctx()
    doc_fails = check_doc_claims(r, c)
    pin_fails = check_regulation_pins(r, today)
    dig_fails = check_self_digest(r)
    cp = check_chain_position(os.path.join(c["root"], "holoaeon"))

    faces = {}
    for f in FACES:
        faces[f] = {"ok": True, "fails": []}
    for item in doc_fails:
        faces[item["face"]]["ok"] = False
        faces[item["face"]]["fails"].append(item)
    for item in pin_fails:
        faces[item["face"]]["ok"] = False
        faces[item["face"]]["fails"].append(item)
    for item in dig_fails:
        faces[item["face"]]["ok"] = False
        faces[item["face"]]["fails"].append(item)
    for item in cp["fails"]:
        faces["chain_position_coverage"]["ok"] = False
        faces["chain_position_coverage"]["fails"].append(item)

    fails_total = sum(len(v["fails"]) for v in faces.values())
    body = {
        "schema": SCHEMA,
        "verdict": "PASS" if fails_total == 0 else "FAIL",
        "mismatch": fails_total,
        "totals": _totals(r),
        "faces": faces,
        "chain_position": {"declared": cp["declared"], "constants": cp["constants"],
                           "verified": cp["verified"],
                           "coverage": "%d/%d" % (cp["verified"], cp["declared"])},
        "declared_digest": r.get("self_digest"),
        "computed_digest": self_digest(r),
    }
    body["digest"] = _sha16(body)
    return body


def report(reg=None, ctx=None, today=None):
    """只读快照，供 README 回读（不含时间戳，两跑一致）。"""
    r = reg if reg is not None else load_registry()
    v = verify(r, ctx, today)
    snap = {
        "schema": SCHEMA,
        "verdict": v["verdict"],
        "totals": v["totals"],
        "rings": v["chain_position"],
        "pins": [
            {"id": p.get("id"), "version": p.get("version"), "status": p.get("status"),
             "verified_at": p.get("verified_at")}
            for p in (r.get("regulation_pins") or []) if isinstance(p, dict)
        ],
        "readbacks": {
            k: readback(item, ctx)
            for k, item in [(x.get("id"), x) for x in (r.get("doc_claims") or [])
                            if isinstance(x, dict) and x.get("kind") in ("current", "narrative")]
        },
        "faces": {f: v["faces"][f]["ok"] for f in FACES},
        "digest": v["digest"],
    }
    for k, val in list(snap["readbacks"].items()):
        if val is _UNKNOWN or not isinstance(val, (int, str, bool)):
            snap["readbacks"][k] = None
    snap["digest"] = _sha16(snap)
    return snap


def main(argv=None):
    """CLI：verify | report。异常路径 rc=1（不吞错）。"""
    args = list(argv if argv is not None else sys.argv[1:])
    cmd = args[0] if args else "verify"
    try:
        if cmd == "verify":
            v = verify()
            print("schema:", v["schema"])
            print("verdict:", v["verdict"], "| mismatch:", v["mismatch"],
                  "| digest:", v["digest"])
            print("totals:", _canonical(v["totals"]))
            print("chain_position:", v["chain_position"]["coverage"],
                  "| constants:", v["chain_position"]["constants"])
            for f in FACES:
                face = v["faces"][f]
                print("  [%s] %s" % ("PASS" if face["ok"] else "FAIL", f))
                for item in face["fails"][:6]:
                    print("    -", item.get("id"), item.get("detail"))
            return 0 if v["verdict"] == "PASS" else 1
        if cmd == "report":
            print(json.dumps(report(), ensure_ascii=False, indent=2, sort_keys=True))
            return 0
        print("unknown command: %r (use: verify | report)" % (cmd,))
        return 2
    except (OSError, ValueError, KeyError) as exc:
        print("ERROR:", type(exc).__name__, exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
