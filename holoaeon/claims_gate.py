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

九面判据（每面都必须先证会红）
---------------------------------------------------------------
1. claim_registered      活体时变声明逐条有注册项（结构化清单比对）
2. readback_consistent   current 项的回读值 == expected_from 指向的真源
3. historical_timeboxed  historical 必带 as_of_batch + timeboxed 且不占活体位
4. regulation_pinned     规定针四必填字段齐、status 合法
5. pin_freshness         verified_at 未超 max_age_days；unknown 须显式登记
6. determinism_self_digest  两跑同 digest；self_digest 抓「建完改报告」
7. chain_position_coverage  模块头 docstring 显式 ring 声明的模块，必须有
                            模块级 CHAIN_POSITION 且 ring 一致（走 AST，不走文本正则）
8. registry_coverage     活体窗口内出现的写死叙述位（版本范围 / 徽章数 / 复算条数）
                            必须在注册簿 coverage 段登记；漏登记即红、登记后文本消失即红、
                            声称已改回读式但窗口里没有「回读」字样也红
                            —— 这一面是「闸自己也会漏自己」的自覆盖判据（V77 新增）

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

# --- V81 面 9：规定契约语义一致性 + 通用新鲜度契约 -----------------------------
# 三条判据共用一套 schema，外部规定针（regulation_pins）与内部实测基线
# （internal_baselines）都走它，不再给基线单独复制一套 _age_days。
FACE_REGULATION_SEMANTIC = "regulation_semantic_consistency"
RISK_TIER_MAX_AGE = {"fast": 90, "annual": 180, "stable": 365}

# --- V79 面 10：跨账口径一致性（cross_ledger_consistency）-------------------------
# 把「同一事实在七本账里的不同写法」做成可失败判据。权威顺序：碳基口述终裁
# 高于任何派生账本记录——两者冲突时判「记录」红，不判碳基红。
FACE_CROSS_LEDGER = "cross_ledger_consistency"

AUTHORITATIVE_SOURCES = {
    "head": "git_rev_parse_HEAD",
    "doc_version": "holoaeon/spec.py:DOC_VERSION",
    "batch_stage": "memory_of_yuan.version_history[-1].stage",
    "five_site_head": "git_ls_remote_origin_main",
    "main_suite": "unittest_discover_measured",
    "redline": "redline_scan_measured",
    "carbon_intent": "carbon_utterance_terminal",
}
# 明确不算证据：本地 remote-tracking 引用 / 运行期快照 / 历史 timeboxed 副本
NON_EVIDENCE = ("git_remote_tracking_ref", "runtime_snapshot", "timeboxed_historical")
# 意图误记特征词：命中即要求显式登记为 intent_vs_blocker，否则红
BLOCKER_AS_INTENT_MARKERS = ("决议不", "选择不", "不干", "永不",
                             "以后条件允许再做", "暂缓即取消")
CONFLICT_KINDS = ("intent_vs_blocker", "stale_pointer", "caliber_difference",
                  "non_evidence", "runtime_snapshot", "known_boundary")
# 这几类是「合法差异/边界」，登记后可容忍值不同，但事实变了要重新登记
TOLERANT_KINDS = ("caliber_difference", "non_evidence", "runtime_snapshot",
                  "known_boundary")
CARBON_PRECEDENCE = "above_all_derived_ledgers"
# 这三条只做权威/结构校验，不做「数值漂移」比对：
# head 与 five_site_head 在提交窗口内天然滞后（提交后才定 sha），
# carbon_intent 由 canon 一致性校验，不比数值。
DECLARED_ONLY = ("head", "five_site_head", "carbon_intent", "batch_stage")
PIN_SEMANTIC_FIELDS = ("claim_sites", "runtime_pointer", "version_chain",
                       "risk_tier", "source_sha16", "change_probe")
VALID_RUNTIME_ROLE = ("current", "legacy")
VALID_PROBE_MODE = ("manual_review_only",)
BASELINE_FIELDS = ("id", "path", "measured_at", "max_age_days", "risk_tier",
                   "source_sha16", "core_py_count")
_VER_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
_VER_YEAR = re.compile(r"(?<!\d)(?:19|20)\d{2}(?!\d)")
_VER_ED_CN = re.compile(r"第[一二三四五六七八九十百零]+\s*版")
_VER_ED_NUM = re.compile(r"第\s*\d+\s*版|\d+\s*版")
_PTR_CONST = re.compile(r"^\s*([A-Z][A-Z0-9_]*)\s*(?::[^=]*)?=\s*[\"']([^\"']+)[\"']")
_PTR_LINES = re.compile(r"^L(\d+)(?:-L(\d+))?$")

FACES = ("claim_registered", "readback_consistent", "historical_timeboxed",
         "regulation_pinned", "pin_freshness", "determinism_self_digest",
         "chain_position_coverage", "registry_coverage",
         "regulation_semantic_consistency", "cross_ledger_consistency")

# 面 8 的扫描规则：只认这几类"会变的叙述位"，不扫普通文字。
COVERAGE_PATTERNS = {
    "version_range": re.compile(r"V\d+\.\d+\s*(?:→|->|~|to)\s*V\d+"),
    "tests_badge": re.compile(r"tests-(\d+)"),
    "suite_count": re.compile(r"主套单测\s*\*\*(\d+)\s*OK\*\*|main suite\s*\*\*(\d+)\s*OK\*\*"),
    "count_decl": re.compile(r"(\d+)\s*条\s*0\s*不匹配"),
}

# 活体窗口：锚点行 ±1 行。历史段落不在此列，故不会误红。
LIVE_WINDOWS = (
    {"id": "zh_badge", "file": "README.zh-CN.md", "key": "readme_zh",
     "anchor": "![Tests](", "patterns": ("tests_badge",)},
    {"id": "zh_acceptance", "file": "README.zh-CN.md", "key": "readme_zh",
     "anchor": "工程验收（本机实跑口径）", "patterns": ("suite_count",)},
    {"id": "zh_timeline", "file": "README.zh-CN.md", "key": "readme_zh",
     "anchor": "2026-10 → 今", "patterns": ("version_range",)},
    {"id": "en_badge", "file": "README.md", "key": "readme_en",
     "anchor": "[![Tests](", "patterns": ("tests_badge",)},
    {"id": "en_acceptance", "file": "README.md", "key": "readme_en",
     "anchor": "Gates (measured on this machine)", "patterns": ("suite_count",)},
    {"id": "en_timeline", "file": "README.md", "key": "readme_en",
     "anchor": "2026-10 → present", "patterns": ("version_range",)},
)

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
    # V77 新增：时间线行的版本范围必须改回读式（不许写死 V0.1 → V38 / V59）
    "readme.zh.timeline_readback": lambda c: _has_readback(
        _text(c, "readme_zh", "README.zh-CN.md"), "2026-10 → 今"),
    "readme.en.timeline_readback": lambda c: _has_readback(
        _text(c, "readme_en", "README.md"), "2026-10 → present"),
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
    """最新批次回执：按回执自身的 doc_version 最高者自动发现。

    V76 修正：V75 版把文件名写死成 v75_receipt.json，于是每批都要改源码才
    能读到本批回执 —— 这正是本模块要治的「会变的事实被复制成静态副本」，
    现在还回来了。改为按版本号取最大，批次换了不必再动这一行。

    V78b 再修：正则放宽到 `v<N><字母?>_receipt.json`，且「最新」的判据从
    文件名里的 N 改为回执自身的 doc_version —— V78b（字母后缀批次）在时间
    上晚于 V81，按 N 取最大会指到旧回执，doc_version 才是批次先后的真判据。
    """
    d = os.path.join(ctx["root"], "reports")
    if not os.path.isdir(d):
        return None
    best_key, best_p = None, None
    for name in os.listdir(d):
        m = re.match(r"^v(\d+)([a-z]?)_receipt\.json$", name)
        if not m:
            continue
        p = os.path.join(d, name)
        try:
            data = _load_json(p)
        except ValueError:
            continue
        dv = data.get("doc_version") if isinstance(data, dict) else None
        try:
            key = (tuple(int(x) for x in str(dv).split(".")), name)
        except (TypeError, ValueError):
            key = ((-1,), name)
        if best_key is None or key > best_key:
            best_key, best_p = key, p
    if best_p is None or not os.path.exists(best_p):
        return None
    try:
        return _load_json(best_p)
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


def _is_version(value):
    """版本号字面（0.9.69 / 12.0.1）：必须逐字符比，禁止归零成整数。"""
    if not isinstance(value, str):
        return False
    return bool(re.fullmatch(r"\d+(?:\.\d+)+", value.strip()))


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
                # V77 修：形如 0.9.69 / 1.2.3 的版本号不得走 _int_of（它只会抓第一段
                # 数字，0.9.69 与 0.9.70 都归零 → 版本升号被闸当成「没变」，是假绿）
                if _is_version(got) or _is_version(exp):
                    ok = str(got).strip() == str(exp).strip()
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
def _today_cst():
    """仓内日期口径 = Asia/Shanghai（UTC+8）。

    GitHub runner 用的是 UTC：本地 2026-11-14 02:36 时 UTC 仍是 2026-11-13，
    `date.today()` 会把「当天登记的 verified_at」判成「在未来」（V81 实测
    三个 py 版本的 Unit tests 全红即由此假红而来）。本仓的日期口径是本地
    日期（回执 / 锚点 / 台账 / pin 登记一致），所以闸必须显式按 UTC+8 取今天，
    而不是跟随运行机器的本地时区。用固定 +8 偏移而非 zoneinfo：CI 覆盖 py3.8，
    zoneinfo 自 3.9 才有。
    """
    import datetime
    return (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).date()


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
        today = _today_cst()
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
# 面 9（V81）：规定契约语义一致性 + 通用新鲜度契约
# ---------------------------------------------------------------------------
def _vtokens(text):
    """把任意版本表述压成可比 token：完整日期 / 四位年份 / 版次。

    只做「同一事实的不同写法」归一（2026-07-28 ≡ 2026 年 ≡ 第 5 版），
    不做语义理解——看不懂的字符串原样不产出 token，宁可判红也不猜。
    """
    s = str(text or "")
    toks = set(_VER_DATE.findall(s))
    toks |= set(_VER_YEAR.findall(s))
    for m in _VER_ED_CN.findall(s):
        toks.add(re.sub(r"\s+", "", m))
    for m in _VER_ED_NUM.findall(s):
        toks.add(re.sub(r"\s+", "", m))
    return toks


def _allowed_tokens(pin):
    """一条针允许出现的版本 token 集合 = version ∪ version_chain 各档。"""
    allowed = _vtokens(pin.get("version"))
    for link in (pin.get("version_chain") or []):
        if isinstance(link, dict):
            allowed |= _vtokens(link.get("version"))
    return allowed


def _split_pointer(pointer):
    """'path#L12' / 'path#L12-L14' / 'path#CONST' → (path, spec)。"""
    p = str(pointer or "")
    if "#" not in p:
        return p.strip(), ""
    path, _, spec = p.rpartition("#")
    return path.strip(), spec.strip()


def _read_pointer(root, pointer):
    """定位一个指针位，返回 (ok, 该位文本, 说明)。只读文件，不发任何请求。"""
    path, spec = _split_pointer(pointer)
    if not path:
        return False, "", "指针为空"
    full = os.path.join(root, path.replace("/", os.sep))
    if not os.path.isfile(full):
        return False, "", "文件不存在: %s" % path
    try:
        lines = _read_text(full).splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        return False, "", "读不出: %s" % exc
    m = _PTR_LINES.match(spec)
    if m:
        a = int(m.group(1))
        b = int(m.group(2) or a)
        if a < 1 or b < a or b > len(lines):
            return False, "", "行号越界 %s（文件 %d 行）" % (spec, len(lines))
        return True, "\n".join(lines[a - 1:b]), "%s#%s" % (path, spec)
    if spec.startswith("~"):
        needle = spec[1:].strip()
        if not needle:
            return False, "", "子串锚为空"
        hit = [ln for ln in lines if needle in ln]
        if not hit:
            return False, "", "子串锚未命中: %s" % needle
        return True, "\n".join(hit), "%s#~%s" % (path, needle)
    if spec:
        hit = [ln for ln in lines if re.search(r"\b%s\b" % re.escape(spec), ln)]
        if not hit:
            return False, "", "符号未找到: %s" % spec
        return True, "\n".join(hit), "%s#%s" % (path, spec)
    return True, "\n".join(lines), path


def claim_site_consistent(reg, root=None):
    """判据 1：各 claim_sites 出现的版本字样必须 ⊆ {version ∪ version_chain}。"""
    root = root or repo_root()
    fails = []
    for pin in (reg.get("regulation_pins") or []):
        if not isinstance(pin, dict):
            continue
        pid = pin.get("id")
        sites = pin.get("claim_sites")
        if not isinstance(sites, list) or not sites:
            fails.append({"face": FACE_REGULATION_SEMANTIC, "id": pid,
                          "detail": "claim_sites 缺失或为空（登记了规定，没说它写在哪）"})
            continue
        allowed = _allowed_tokens(pin)
        for site in sites:
            ok, text, detail = _read_pointer(root, site)
            if not ok:
                fails.append({"face": FACE_REGULATION_SEMANTIC, "id": pid,
                              "detail": "叙述位不可定位 %s（%s）" % (site, detail)})
                continue
            seen = _vtokens(text)
            if not seen:
                fails.append({"face": FACE_REGULATION_SEMANTIC, "id": pid,
                              "detail": "叙述位 %s 未出现任何版本字样（叙述位漂移）" % site})
                continue
            drift = sorted(seen - allowed)
            if drift:
                fails.append({"face": FACE_REGULATION_SEMANTIC, "id": pid,
                              "detail": "claim_site_drift %s 出现未登记版本 %s（已登记 %s）"
                                        % (site, ",".join(drift), ",".join(sorted(allowed)))})
    return fails


def runtime_version_registered(reg, root=None):
    """判据 2：运行时真正生效的常量必须登记，且与谱系自洽。"""
    root = root or repo_root()
    fails = []
    for pin in (reg.get("regulation_pins") or []):
        if not isinstance(pin, dict):
            continue
        pid = pin.get("id")
        ptr = pin.get("runtime_pointer")
        role = pin.get("runtime_role")
        value = pin.get("runtime_value")
        chain = [c for c in (pin.get("version_chain") or []) if isinstance(c, dict)]
        if not ptr:
            fails.append({"face": FACE_REGULATION_SEMANTIC, "id": pid,
                          "detail": "runtime_pointer 缺失（登记口径与运行时口径不可判）"})
        if role not in VALID_RUNTIME_ROLE:
            fails.append({"face": FACE_REGULATION_SEMANTIC, "id": pid,
                          "detail": "runtime_role=%r 非 current/legacy" % (role,)})
        if not value:
            fails.append({"face": FACE_REGULATION_SEMANTIC, "id": pid,
                          "detail": "runtime_value 缺失"})
        if not ptr:
            continue
        ok, text, detail = _read_pointer(root, ptr)
        if not ok:
            fails.append({"face": FACE_REGULATION_SEMANTIC, "id": pid,
                          "detail": "运行时指针不可定位 %s（%s）" % (ptr, detail)})
            continue
        if value and str(value) not in text:
            fails.append({"face": FACE_REGULATION_SEMANTIC, "id": pid,
                          "detail": "runtime_value=%r 未出现在 %s（登记与运行时脱钩）"
                                    % (value, detail)})
        if value:
            unreg = sorted(_vtokens(value) - _allowed_tokens(pin))
            if unreg:
                fails.append({"face": FACE_REGULATION_SEMANTIC, "id": pid,
                              "detail": "runtime_value 版本 %s 不在 version_chain（无谱系即红）"
                                        % ",".join(unreg)})
            if role == "legacy":
                link = next((c for c in chain if str(c.get("version")) == str(value)), None)
                if link is None:
                    fails.append({"face": FACE_REGULATION_SEMANTIC, "id": pid,
                                  "detail": "legacy 值 %r 不在 version_chain" % (value,)})
                elif link.get("role") != "legacy" or not link.get("superseded_by"):
                    fails.append({"face": FACE_REGULATION_SEMANTIC, "id": pid,
                                  "detail": "legacy 谱系条目不完整（须 role=legacy + superseded_by）"})
    return fails


def _file_sha16(root, relpath):
    full = os.path.join(root, str(relpath).replace("/", os.sep))
    if not os.path.isfile(full):
        return None
    with open(full, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def freshness_contract(reg, root=None, today=None):
    """判据 3：一套 schema 同时管外部针与内部基线（不复制第二套 _age_days）。"""
    import datetime
    root = root or repo_root()
    if today is None:
        today = _today_cst()
    elif isinstance(today, str):
        today = datetime.date(*[int(x) for x in today.split("-")])
    fails = []
    for pin in (reg.get("regulation_pins") or []):
        if not isinstance(pin, dict):
            continue
        pid = pin.get("id")
        tier = pin.get("risk_tier")
        if tier not in RISK_TIER_MAX_AGE:
            fails.append({"face": FACE_REGULATION_SEMANTIC, "id": pid,
                          "detail": "risk_tier=%r 未登记（只认 fast/annual/stable）" % (tier,)})
        else:
            want = RISK_TIER_MAX_AGE[tier]
            if pin.get("max_age_days") != want:
                fails.append({"face": FACE_REGULATION_SEMANTIC, "id": pid,
                              "detail": "risk_tier=%s 应配 %d 天，登记 %r（分级不匹配）"
                                        % (tier, want, pin.get("max_age_days"))})
        sha = pin.get("source_sha16")
        src = _split_pointer(pin.get("source_pointer"))[0]
        if not sha:
            fails.append({"face": FACE_REGULATION_SEMANTIC, "id": pid,
                          "detail": "source_sha16 缺失（无法判源是否已变）"})
        elif src:
            actual = _file_sha16(root, src)
            if actual is None:
                fails.append({"face": FACE_REGULATION_SEMANTIC, "id": pid,
                              "detail": "source_pointer 指向文件不存在: %s" % src})
            elif actual != sha:
                fails.append({"face": FACE_REGULATION_SEMANTIC, "id": pid,
                              "detail": "source_sha16 漂移 %s → %s（改源须同时更新 verified_at 与 sha16）"
                                        % (sha, actual)})
        probe = pin.get("change_probe")
        if not isinstance(probe, dict):
            fails.append({"face": FACE_REGULATION_SEMANTIC, "id": pid,
                          "detail": "change_probe 缺失（离线复核检索指针）"})
        else:
            mode = probe.get("mode")
            if mode not in VALID_PROBE_MODE:
                fails.append({"face": FACE_REGULATION_SEMANTIC, "id": pid,
                              "detail": "change_probe.mode=%r 非法（离线项目不得声称已联网核实）"
                                        % (mode,)})
            if not (probe.get("probe_url") or probe.get("probe_query")):
                fails.append({"face": FACE_REGULATION_SEMANTIC, "id": pid,
                              "detail": "change_probe 无检索指针（probe_url / probe_query）"})

    core_py = _count_py(root, True)
    for base in (reg.get("internal_baselines") or []):
        if not isinstance(base, dict):
            fails.append({"face": FACE_REGULATION_SEMANTIC, "id": "?",
                          "detail": "internal_baselines 含非对象项"})
            continue
        bid = base.get("id")
        miss = [k for k in BASELINE_FIELDS if base.get(k) in (None, "", [])]
        if miss:
            fails.append({"face": FACE_REGULATION_SEMANTIC, "id": bid,
                          "detail": "基线缺字段 %s（不许省 measured_at）" % ",".join(miss)})
        tier = base.get("risk_tier")
        if tier in RISK_TIER_MAX_AGE and base.get("max_age_days") != RISK_TIER_MAX_AGE[tier]:
            fails.append({"face": FACE_REGULATION_SEMANTIC, "id": bid,
                          "detail": "基线 risk_tier=%s 应配 %d 天，登记 %r"
                                    % (tier, RISK_TIER_MAX_AGE[tier], base.get("max_age_days"))})
        age = _age_days(base.get("measured_at"), today)
        limit = base.get("max_age_days")
        if age is None:
            fails.append({"face": FACE_REGULATION_SEMANTIC, "id": bid,
                          "detail": "measured_at 不可解析"})
        elif age < 0:
            fails.append({"face": FACE_REGULATION_SEMANTIC, "id": bid,
                          "detail": "measured_at 在未来（%s）——伪造旧值换绿" % (base.get("measured_at"),)})
        elif isinstance(limit, int) and age > limit:
            fails.append({"face": FACE_REGULATION_SEMANTIC, "id": bid,
                          "detail": "STALE_BASELINE age=%d > %d（如实登记，禁伪造 measured_at）"
                                    % (age, limit)})
        sha = base.get("source_sha16")
        actual = _file_sha16(root, base.get("path"))
        if actual is None:
            fails.append({"face": FACE_REGULATION_SEMANTIC, "id": bid,
                          "detail": "基线文件不存在: %s" % (base.get("path"),)})
        elif sha and actual != sha:
            fails.append({"face": FACE_REGULATION_SEMANTIC, "id": bid,
                          "detail": "基线文件 sha16 漂移 %s → %s" % (sha, actual)})
        if base.get("stale_if_core_py_count_changes"):
            want_py = base.get("core_py_count")
            if isinstance(want_py, int) and core_py != want_py:
                fails.append({"face": FACE_REGULATION_SEMANTIC, "id": bid,
                              "detail": "核心包 .py 数 %d → %d，基线可能失效（须重测）"
                                        % (want_py, core_py)})
    return fails


def regulation_semantic_consistency(reg, root=None, today=None):
    """面 9 聚合：三条判据 + 四类漂移列表（只报告 drifted 项，不做裁决）。"""
    root = root or repo_root()
    site = claim_site_consistent(reg, root)
    run = runtime_version_registered(reg, root)
    fresh = freshness_contract(reg, root, today)
    fails = site + run + fresh

    def _ids(items, tag):
        return [x.get("id") for x in items if tag in str(x.get("detail", ""))]

    tiers = {}
    for pin in (reg.get("regulation_pins") or []):
        if isinstance(pin, dict):
            t = pin.get("risk_tier") or "unregistered"
            tiers[t] = tiers.get(t, 0) + 1
    return {
        "face": FACE_REGULATION_SEMANTIC,
        "ok": not fails,
        "fails": fails,
        "claim_site_drift": _ids(site, "drift"),
        "runtime_unregistered": _ids(run, "脱钩") + _ids(run, "缺失") + _ids(run, "不可定位"),
        "freshness_violations": _ids(fresh, "STALE") + _ids(fresh, "漂移") + _ids(fresh, "不匹配"),
        "internal_stale": _ids(fresh, "STALE_BASELINE"),
        "risk_tier_dist": tiers,
        "pins_with_contract": sum(1 for p in (reg.get("regulation_pins") or [])
                                  if isinstance(p, dict)
                                  and all(p.get(k) not in (None, "", [], {}) for k in PIN_SEMANTIC_FIELDS)),
        "internal_baselines": len(reg.get("internal_baselines") or []),
    }


# ---------------------------------------------------------------------------
# 面 6：确定性 + 自摘要
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# 面 10：跨账口径一致性（V79）
# ---------------------------------------------------------------------------
def _git_ref_head(root):
    """纯文件读 HEAD（不启子进程、不联网）；读不到返回 None。"""
    gitdir = os.path.join(root, ".git")
    headfile = os.path.join(gitdir, "HEAD")
    if os.path.isfile(gitdir):
        with open(gitdir, "r", encoding="utf-8", errors="replace") as f:
            ref = f.read().strip()
        return ref or None if not ref.startswith("ref:") else None
    if not os.path.isfile(headfile):
        return None
    with open(headfile, "r", encoding="utf-8", errors="replace") as f:
        ref = f.read().strip()
    if not ref.startswith("ref:"):
        return ref or None
    rel = ref[4:].strip()
    p = os.path.join(gitdir, *rel.split("/"))
    if not os.path.isfile(p):
        return None
    with open(p, "r", encoding="utf-8", errors="replace") as f:
        return f.read().strip() or None


def _memory_dir(root):
    return os.path.join(os.path.dirname(os.path.abspath(root)), "holoaeon_memory")


def _memory_stage(root):
    """玉安 version_history 最后一条的 stage；仓外文件缺失返回 None。"""
    p = os.path.join(_memory_dir(root), "version_history.json")
    try:
        data = _load_json(p)
    except (OSError, ValueError):
        return None
    hist = data.get("history") or []
    return hist[-1].get("stage") if hist else None


def _claims_by_id(reg):
    return {x.get("id"): x for x in (reg.get("doc_claims") or []) if isinstance(x, dict)}


def _readback_or_none(reg, cid, ctx):
    claim = _claims_by_id(reg).get(cid)
    if not claim:
        return None
    val = readback(claim, ctx)
    return None if val is _UNKNOWN else val


def ledger_observed(reg, ctx=None):
    """各权威源的当前实测值。不联网、不跑测试：能本地读的实时读，
    测试数与 redline 从注册簿既有 readback 取（不重跑）。"""
    c = ctx or _ctx()
    texts = dict(c.get("texts") or {})
    root = c["root"]
    obs = {
        "head": texts.get("head") or _git_ref_head(root),
        "doc_version": texts.get("doc_version") or _spec_doc_version(root),
        "batch_stage": texts.get("batch_stage") or _memory_stage(root),
        "five_site_head": texts.get("five_site_head"),
        "main_suite": texts.get("main_suite"),
        "redline": texts.get("redline"),
        "carbon_intent": texts.get("carbon_intent"),
    }
    if obs["main_suite"] is None:
        obs["main_suite"] = _readback_or_none(reg, "acceptance_suite_zh", c)
    if obs["redline"] is None:
        obs["redline"] = _readback_or_none(reg, "gate_redline_zh", c)
    return obs


def _landed_batches(root):
    """已落地批次：reports/ 下 v<xx>_receipt.json 的文件名（含字母后缀批次）。"""
    got = set()
    d = os.path.join(root, "reports")
    if not os.path.isdir(d):
        return got
    for name in os.listdir(d):
        m = re.match(r"^v(\d+[a-z]?)_receipt\.json$", name)
        if m:
            got.add(m.group(1))
    return got


def _conflict_covers(conflicts, key):
    for e in conflicts:
        if key in (e.get("keys") or []):
            return e
        where = e.get("where")
        if isinstance(where, str) and key in where:
            return e
        if isinstance(where, (list, tuple)) and key in where:
            return e
    return None


def _conflict_kind_counts(conflicts):
    out = {}
    for e in conflicts:
        k = e.get("kind") or "unknown"
        out[k] = out.get(k, 0) + 1
    return out


_WHERE_FILE = re.compile(r"[A-Za-z0-9_.\-]+\.(?:md|py|json|yml|yaml)")


def _where_files(where):
    return set(_WHERE_FILE.findall((where or "").replace("\\", "/")))


def _intent_registered(conflicts, where):
    """原文所在位置是否已有 intent_vs_blocker 挂账（按文件名交集匹配）。"""
    files = _where_files(where)
    for e in conflicts:
        if e.get("kind") != "intent_vs_blocker":
            continue
        reg_where = e.get("where")
        if not isinstance(reg_where, str) or not reg_where:
            continue
        reg_files = _where_files(reg_where)
        if files and reg_files and (files & reg_files):
            return e
        if reg_where.replace("\\", "/") in (where or "").replace("\\", "/"):
            return e
    return None


def cross_ledger_consistency(reg, ctx=None, today=None):
    """跨账冲突：未登记即红；登记后事实漂移也红；陈旧指针即红；
    技术阻塞被写成碳基意图即红（intent_vs_blocker）。纯本地、不联网。"""
    c = ctx or _ctx()
    srcs = reg.get("ledger_sources")
    conflicts = [e for e in (reg.get("ledger_conflicts") or []) if isinstance(e, dict)]
    fails = []

    def add(item_id, detail, kind):
        fails.append({"face": FACE_CROSS_LEDGER, "id": item_id,
                      "detail": detail, "kind": kind})

    # --- 结构判据：没有登记面的闸等同摆设 ---
    if not isinstance(srcs, dict):
        add("ledger_sources_missing", "ledger_sources 段缺失：跨账判据没有登记面",
            "structure")
        srcs = {}
    missing = [k for k in AUTHORITATIVE_SOURCES if k not in srcs]
    if missing:
        add("ledger_sources_incomplete",
            "权威源未登记: %s" % ", ".join(sorted(missing)), "structure")

    for key in sorted(AUTHORITATIVE_SOURCES):
        if key not in srcs or not isinstance(srcs[key], dict):
            continue
        s = srcs[key]
        auth = s.get("authority")
        if auth != AUTHORITATIVE_SOURCES[key]:
            add("authority_mismatch:%s" % key,
                "%s 的 authority=%r，应为 %r" % (key, auth, AUTHORITATIVE_SOURCES[key]),
                "structure")
        for ne in (s.get("non_evidence") or []):
            if ne not in NON_EVIDENCE:
                add("non_evidence_unknown:%s" % key,
                    "%s 的 non_evidence 含未登记项 %r（非证据不得冒充权威源）" % (key, ne),
                    "structure")

    carbon = srcs.get("carbon_intent") if isinstance(srcs.get("carbon_intent"), dict) else {}
    if carbon.get("precedence") != CARBON_PRECEDENCE:
        add("carbon_precedence",
            "carbon_intent.precedence 必须为 %r（碳基口述高于派生账本）" % CARBON_PRECEDENCE,
            "structure")

    for e in conflicts:
        for fld in ("id", "kind", "where", "was", "truth", "disposition"):
            if not e.get(fld):
                add("conflict_field:%s" % (e.get("id") or "?"),
                    "冲突登记缺字段 %s" % fld, "structure")
        if e.get("kind") and e["kind"] not in CONFLICT_KINDS:
            add("conflict_kind:%s" % (e.get("id") or "?"),
                "kind=%r 不在允许集合（把边界伪装成已解决也算越界）" % e.get("kind"),
                "structure")

    # --- A 未登记冲突：登记时观测与当前实测不一致却没登记 ---
    now = ledger_observed(reg, c)
    for key in sorted(AUTHORITATIVE_SOURCES):
        if key in DECLARED_ONLY:
            continue
        s = srcs.get(key) if isinstance(srcs.get(key), dict) else {}
        was = s.get("observed")
        cur = now.get(key)
        if was in (None, "") or cur in (None, ""):
            continue
        if was == cur:
            continue
        if _conflict_covers(conflicts, key) is None:
            add("unregistered_conflict:%s" % key,
                "%s 两账不同（登记 %r / 实测 %r）且未登记冲突" % (key, was, cur),
                "unregistered_conflict")

    # --- B stale_pointer：账面指针指向已落地批次 ---
    landed = set(c.get("landed_batches") or []) or _landed_batches(c["root"])
    note = (c.get("texts") or {}).get("pending_note")
    if note is None:
        try:
            note = _load_json(os.path.join(c["root"], "reports",
                                           "feed_index.json")).get("pending_note")
        except (OSError, ValueError):
            note = None
    if isinstance(note, str) and note.strip():
        for b in re.findall(r"V(\d+[a-z]?)", note):
            if b in landed:
                add("stale_pointer",
                    "pending_note 指向已落地批次 V%s：%r" % (b, note.strip()[:90]),
                    "stale_pointer")
                break

    # --- C intent_vs_blocker：意图误记 ---
    for e in conflicts:
        was = e.get("was") or ""
        hits = [m for m in BLOCKER_AS_INTENT_MARKERS if m in was]
        if hits and e.get("kind") != "intent_vs_blocker":
            add("intent_vs_blocker:%s" % (e.get("id") or "?"),
                "把技术阻塞写成意图（命中 %s）却未登记为 intent_vs_blocker"
                % "、".join(hits), "intent_vs_blocker")
        if e.get("kind") == "intent_vs_blocker":
            if "blocker_not_intent" not in (e.get("disposition") or ""):
                add("intent_vs_blocker:%s:disposition" % (e.get("id") or "?"),
                    "intent_vs_blocker 的 disposition 必须写明 blocker_not_intent",
                    "intent_vs_blocker")
            canon = carbon.get("observed")
            if canon and e.get("carbon_canon") != canon:
                add("intent_vs_blocker:%s:canon" % (e.get("id") or "?"),
                    "登记与碳基口述终裁相悖（carbon_canon 未对齐，判记录红不判碳基红）",
                    "intent_vs_blocker")

    # --- C2 原文级：账本措辞把技术阻塞写成意图，且未挂账 ---
    intent_texts = (c.get("texts") or {}).get("intent_texts") or []
    for item in intent_texts:
        if not isinstance(item, dict):
            continue
        where = item.get("where") or "?"
        text = item.get("text") or ""
        hits = [m for m in BLOCKER_AS_INTENT_MARKERS if m in text]
        if not hits:
            continue
        if _intent_registered(conflicts, where) is None:
            add("intent_vs_blocker:%s" % os.path.basename(where.replace("\\", "/")),
                "账本措辞命中 %s，且未登记为 blocker_not_intent：%r"
                % ("、".join(hits), text.strip()[:90]), "intent_vs_blocker")

    # --- D drift_after_register：已登记差异的事实值变了 ---
    for e in conflicts:
        if e.get("kind") not in TOLERANT_KINDS:
            continue
        obs_reg = e.get("observed_at_register") or {}
        for key in sorted(obs_reg):
            cur = now.get(key)
            if cur in (None, ""):
                continue
            if obs_reg[key] != cur:
                add("drift_after_register:%s:%s" % (e.get("id") or "?", key),
                    "已登记差异的事实值变了（登记 %r / 实测 %r），登记未更新"
                    % (obs_reg[key], cur), "drift_after_register")

    return {
        "face": FACE_CROSS_LEDGER,
        "ok": not fails,
        "fails": fails,
        "ledger_sources": len(srcs),
        "ledger_conflicts": len(conflicts),
        "by_kind": _conflict_kind_counts(conflicts),
        "unregistered": [f["id"] for f in fails if f["kind"] == "unregistered_conflict"],
        "drifted": [f["id"] for f in fails if f["kind"] == "drift_after_register"],
        "stale_pointers": [f["id"] for f in fails if f["kind"] == "stale_pointer"],
        "intent_vs_blocker": [f["id"] for f in fails if f["kind"] == "intent_vs_blocker"],
        "registered_boundaries": [e.get("id") for e in conflicts
                                  if e.get("kind") in TOLERANT_KINDS],
    }


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
# 面 8：注册簿自覆盖（活体窗口内的写死叙述位必须登记）
# ---------------------------------------------------------------------------
def check_registry_coverage(reg, ctx=None):
    """面 8：活体窗口 × 模式扫描 → 未登记即红；登记后文本消失即红。

    fails 的 detail 前缀是机器可读标签：
      UNREGISTERED   窗口里出现写死位，但注册簿无对应 coverage 条目
      VANISHED       注册簿登记了（且 must_appear），窗口里却找不到该写死位
      NOT_READBACK   登记项声称已改回读式，但窗口里没有「回读」字样
      ANCHOR_MISSING 窗口锚点整行消失（README 结构被改，判红而非静默跳过）
      UNKNOWN_WINDOW coverage 条目指向不存在的窗口
    """
    c = ctx or _ctx()
    fails = []
    cov = [x for x in (reg.get("coverage") or []) if isinstance(x, dict)]
    win_ids = [w["id"] for w in LIVE_WINDOWS]

    for e in cov:
        if e.get("window") not in win_ids:
            fails.append({"face": "registry_coverage", "id": e.get("id"),
                          "detail": "UNKNOWN_WINDOW %r" % (e.get("window"),)})

    for w in LIVE_WINDOWS:
        try:
            text = _text(c, w["key"], w["file"])
        except (OSError, KeyError):
            fails.append({"face": "registry_coverage", "id": w["id"],
                          "detail": "ANCHOR_MISSING 文件不可读 %s" % (w["file"],)})
            continue
        lines = text.splitlines()
        idx = [i for i, ln in enumerate(lines) if w["anchor"] in ln]
        if not idx:
            fails.append({"face": "registry_coverage", "id": w["id"],
                          "detail": "ANCHOR_MISSING %r" % (w["anchor"],)})
            continue
        lo = max(0, min(idx) - 1)
        hi = min(len(lines) - 1, max(idx) + 1)
        win_text = "\n".join(lines[lo:hi + 1])

        for pat_id in w["patterns"]:
            pat = COVERAGE_PATTERNS[pat_id]
            hits = []
            for i in range(lo, hi + 1):
                for m in pat.finditer(lines[i]):
                    hits.append((i + 1, m.group(0)))
            entries = [e for e in cov
                       if e.get("window") == w["id"] and e.get("pattern") == pat_id]
            for ln, frag in hits:
                if not entries:
                    fails.append({"face": "registry_coverage", "id": w["id"],
                                  "detail": "UNREGISTERED %s 写死位 %r @L%d（%s）"
                                            % (pat_id, frag, ln, w["file"])})
            if entries and not hits:
                for e in entries:
                    if e.get("must_appear", True):
                        fails.append({"face": "registry_coverage", "id": e.get("id"),
                                      "detail": "VANISHED %s 登记在册但窗口内已无写死位"
                                                % (pat_id,)})
            if entries and hits:
                for e in entries:
                    if e.get("must_write_readback") and not (
                            ("回读" in win_text) or ("readback" in win_text.lower())):
                        fails.append({"face": "registry_coverage", "id": e.get("id"),
                                      "detail": "NOT_READBACK 登记项声称回读式，窗口内无「回读」字样"})
    return fails


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
    cov_fails = check_registry_coverage(r, c)
    for item in cov_fails:
        faces["registry_coverage"]["ok"] = False
        faces["registry_coverage"]["fails"].append(item)
    sem = regulation_semantic_consistency(r, c["root"], today)
    for item in sem["fails"]:
        faces[FACE_REGULATION_SEMANTIC]["ok"] = False
        faces[FACE_REGULATION_SEMANTIC]["fails"].append(item)
    cl = cross_ledger_consistency(r, c, today)
    for item in cl["fails"]:
        faces[FACE_CROSS_LEDGER]["ok"] = False
        faces[FACE_CROSS_LEDGER]["fails"].append(item)

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
        "registry_coverage": {"windows": len(LIVE_WINDOWS),
                              "entries": len(r.get("coverage") or [])},
        "regulation_semantic": {
            "face": FACE_REGULATION_SEMANTIC,
            "pins_with_contract": sem["pins_with_contract"],
            "internal_baselines": sem["internal_baselines"],
            "risk_tier_dist": sem["risk_tier_dist"],
            "internal_stale": sem["internal_stale"],
            "claim_site_drift": sem["claim_site_drift"],
            "runtime_unregistered": sem["runtime_unregistered"],
            "freshness_violations": sem["freshness_violations"],
        },
        "cross_ledger": {
            "face": FACE_CROSS_LEDGER,
            "ledger_sources": cl["ledger_sources"],
            "ledger_conflicts": cl["ledger_conflicts"],
            "by_kind": cl["by_kind"],
            "unregistered": cl["unregistered"],
            "drifted": cl["drifted"],
            "stale_pointers": cl["stale_pointers"],
            "intent_vs_blocker": cl["intent_vs_blocker"],
            "registered_boundaries": cl["registered_boundaries"],
        },
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
        "regulation_semantic": v["regulation_semantic"],
        "cross_ledger": {
            "sources": v["cross_ledger"]["ledger_sources"],
            "conflicts": v["cross_ledger"]["ledger_conflicts"],
            "by_kind": v["cross_ledger"]["by_kind"],
            "registered_boundaries": v["cross_ledger"]["registered_boundaries"],
        },
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
