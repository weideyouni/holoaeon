"""V81 · 规定契约语义一致性 + 通用新鲜度契约（claims_gate 面 9）。

十组 ≥40 例 + 8 只金丝雀。全部用自造 tmp 上下文：
**不写死真实 HEAD / DOC / 面数**，也不依赖真实仓当前的叙述位文字。

这一批要治的病：登记（版本 / 核实日 / 指针）与运行时实际脱钩，却没有任何一面会红。
所以本文件的重点不是「函数返回什么」，而是「哪一只金丝雀能单独把面 9 打红」。
"""

import ast
import copy
import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from holoaeon import claims_gate as cg

TODAY = "2026-11-14"
MCP_SRC = ('PROTOCOL_VERSION = "2024-11-05"\n'
           'SUPPORTED_PROTOCOL_VERSIONS = ("2024-11-05", "2026-07-28")\n')
MCP_LINE = "MCP (Model Context Protocol, 2024-11-05) stdio transport.\n"


# ---------------------------------------------------------------------------
# 自造上下文
# ---------------------------------------------------------------------------
def _mk(root, rel, text):
    full = os.path.join(root, rel.replace("/", os.sep))
    d = os.path.dirname(full)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with open(full, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return full


def _sha16(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def _mcp_pin(root, **over):
    src = _mk(root, "pkg/mcp.py", MCP_SRC)
    _mk(root, "README.md", MCP_LINE)
    pin = {
        "id": "MCP",
        "version": "2026-07-28（第 5 版）",
        "source_pointer": "pkg/mcp.py#SUPPORTED_PROTOCOL_VERSIONS",
        "source_sha16": _sha16(src),
        "claim_sites": ["README.md#L1"],
        "runtime_pointer": "pkg/mcp.py#PROTOCOL_VERSION",
        "runtime_role": "legacy",
        "runtime_value": "2024-11-05",
        "version_chain": [
            {"version": "2024-11-05", "role": "legacy", "superseded_by": "2026-07-28"},
            {"version": "2026-07-28", "role": "current", "supersedes": "2024-11-05"},
        ],
        "risk_tier": "fast",
        "max_age_days": cg.RISK_TIER_MAX_AGE["fast"],
        "change_probe": {"probe_query": "mcp version", "mode": "manual_review_only"},
    }
    pin.update(over)
    return pin, src


def _baseline(root, **over):
    art = _mk(root, "benchmarks/res.json", '{"a": 1}\n')
    item = {
        "id": "b1",
        "path": "benchmarks/res.json",
        "measured_at": "2026-11-01",
        "max_age_days": cg.RISK_TIER_MAX_AGE["fast"],
        "risk_tier": "fast",
        "source_sha16": _sha16(art),
        "core_py_count": cg._count_py(root, True),
        "stale_if_core_py_count_changes": True,
    }
    item.update(over)
    return item, art


def _wrap(pin):
    return {"regulation_pins": [pin]}


class _Tmp(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="v81_")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# 组 1：契约字段完整性
# ---------------------------------------------------------------------------
class T1_Contract(_Tmp):
    def test_01_six_semantic_fields(self):
        self.assertEqual(len(cg.PIN_SEMANTIC_FIELDS), 6)
        for k in ("claim_sites", "runtime_pointer", "version_chain",
                  "risk_tier", "source_sha16", "change_probe"):
            self.assertIn(k, cg.PIN_SEMANTIC_FIELDS)

    def test_02_baseline_fields(self):
        for k in ("measured_at", "path", "source_sha16", "core_py_count"):
            self.assertIn(k, cg.BASELINE_FIELDS)

    def test_03_runtime_role_domain(self):
        self.assertEqual(set(cg.VALID_RUNTIME_ROLE), {"current", "legacy"})

    def test_04_probe_mode_is_offline_only(self):
        self.assertEqual(set(cg.VALID_PROBE_MODE), {"manual_review_only"})


# ---------------------------------------------------------------------------
# 组 2：risk_tier → 允许复核间隔
# ---------------------------------------------------------------------------
class T2_Tier(unittest.TestCase):
    def test_05_fast_90(self):
        self.assertEqual(cg.RISK_TIER_MAX_AGE["fast"], 90)

    def test_06_annual_180(self):
        self.assertEqual(cg.RISK_TIER_MAX_AGE["annual"], 180)

    def test_07_stable_365(self):
        self.assertEqual(cg.RISK_TIER_MAX_AGE["stable"], 365)

    def test_08_unknown_tier_not_wildcard(self):
        self.assertNotIn("critical", cg.RISK_TIER_MAX_AGE)


# ---------------------------------------------------------------------------
# 组 3：claim_site_consistent
# ---------------------------------------------------------------------------
class T3_ClaimSite(_Tmp):
    def test_09_registered_version_passes(self):
        pin, _ = _mcp_pin(self.tmp)
        self.assertEqual(cg.claim_site_consistent(_wrap(pin), self.tmp), [])

    def test_10_unregistered_version_drifts(self):
        pin, _ = _mcp_pin(self.tmp)
        _mk(self.tmp, "README.md", "MCP version 2025-01-01 declared here.\n")
        fails = cg.claim_site_consistent(_wrap(pin), self.tmp)
        self.assertTrue(fails)
        self.assertIn("claim_site_drift", fails[0]["detail"])

    def test_11_missing_site_file(self):
        pin, _ = _mcp_pin(self.tmp, claim_sites=["README.md#L1", "gone.md#L1"])
        fails = cg.claim_site_consistent(_wrap(pin), self.tmp)
        self.assertTrue(any("不可定位" in f["detail"] for f in fails))

    def test_12_site_without_version_token(self):
        pin, _ = _mcp_pin(self.tmp)
        _mk(self.tmp, "README.md", "MCP transport description only.\n")
        fails = cg.claim_site_consistent(_wrap(pin), self.tmp)
        self.assertTrue(any("版本字样" in f["detail"] for f in fails))

    def test_13_claim_sites_absent(self):
        pin, _ = _mcp_pin(self.tmp)
        pin.pop("claim_sites")
        fails = cg.claim_site_consistent(_wrap(pin), self.tmp)
        self.assertTrue(any("claim_sites 缺失" in f["detail"] for f in fails))

    def test_14_line_number_out_of_range(self):
        pin, _ = _mcp_pin(self.tmp, claim_sites=["README.md#L900"])
        fails = cg.claim_site_consistent(_wrap(pin), self.tmp)
        self.assertTrue(any("越界" in f["detail"] for f in fails))

    def test_14b_substring_anchor_survives_insertion(self):
        pin, _ = _mcp_pin(self.tmp, claim_sites=["README.md#~Model Context Protocol"])
        _mk(self.tmp, "README.md", "inserted line\n" + MCP_LINE)
        self.assertEqual(cg.claim_site_consistent(_wrap(pin), self.tmp), [])

    def test_14c_substring_anchor_miss_is_red(self):
        pin, _ = _mcp_pin(self.tmp, claim_sites=["README.md#~nonexistent phrase"])
        fails = cg.claim_site_consistent(_wrap(pin), self.tmp)
        self.assertTrue(any("子串锚未命中" in f["detail"] for f in fails))


# ---------------------------------------------------------------------------
# 组 4：runtime_version_registered（四分支）
# ---------------------------------------------------------------------------
class T4_Runtime(_Tmp):
    def test_15_registered_legacy_passes(self):
        pin, _ = _mcp_pin(self.tmp)
        self.assertEqual(cg.runtime_version_registered(_wrap(pin), self.tmp), [])

    def test_16_missing_pointer(self):
        pin, _ = _mcp_pin(self.tmp)
        pin.pop("runtime_pointer")
        fails = cg.runtime_version_registered(_wrap(pin), self.tmp)
        self.assertTrue(any("runtime_pointer 缺失" in f["detail"] for f in fails))

    def test_17_bad_role(self):
        pin, _ = _mcp_pin(self.tmp, runtime_role="default")
        fails = cg.runtime_version_registered(_wrap(pin), self.tmp)
        self.assertTrue(any("runtime_role" in f["detail"] for f in fails))

    def test_18_missing_value(self):
        pin, _ = _mcp_pin(self.tmp, runtime_value="")
        fails = cg.runtime_version_registered(_wrap(pin), self.tmp)
        self.assertTrue(any("runtime_value 缺失" in f["detail"] for f in fails))

    def test_19_pointer_unresolvable(self):
        pin, _ = _mcp_pin(self.tmp, runtime_pointer="pkg/absent.py#X")
        fails = cg.runtime_version_registered(_wrap(pin), self.tmp)
        self.assertTrue(any("不可定位" in f["detail"] for f in fails))

    def test_20_value_not_in_source(self):
        pin, _ = _mcp_pin(self.tmp, runtime_value="2030-01-01")
        fails = cg.runtime_version_registered(_wrap(pin), self.tmp)
        self.assertTrue(any("脱钩" in f["detail"] for f in fails))

    def test_21_value_without_genealogy(self):
        pin, _ = _mcp_pin(self.tmp)
        pin["version_chain"] = [c for c in pin["version_chain"]
                                if "2024-11-05" not in str(c.get("version"))]
        fails = cg.runtime_version_registered(_wrap(pin), self.tmp)
        self.assertTrue(any("不在 version_chain" in f["detail"] for f in fails))

    def test_22_legacy_entry_incomplete(self):
        pin, _ = _mcp_pin(self.tmp)
        pin["version_chain"][0] = {"version": "2024-11-05", "role": "current"}
        fails = cg.runtime_version_registered(_wrap(pin), self.tmp)
        self.assertTrue(any("谱系条目不完整" in f["detail"] for f in fails))


# ---------------------------------------------------------------------------
# 组 5：freshness_contract 时效与分级
# ---------------------------------------------------------------------------
class T5_Freshness(_Tmp):
    def test_23_tier_mismatch(self):
        pin, _ = _mcp_pin(self.tmp, max_age_days=365)
        fails = cg.freshness_contract(_wrap(pin), self.tmp, TODAY)
        self.assertTrue(any("分级不匹配" in f["detail"] for f in fails))

    def test_24_unknown_tier_is_red(self):
        pin, _ = _mcp_pin(self.tmp, risk_tier="critical")
        fails = cg.freshness_contract(_wrap(pin), self.tmp, TODAY)
        self.assertTrue(any("risk_tier" in f["detail"] for f in fails))

    def test_25_missing_source_sha(self):
        pin, _ = _mcp_pin(self.tmp)
        pin.pop("source_sha16")
        fails = cg.freshness_contract(_wrap(pin), self.tmp, TODAY)
        self.assertTrue(any("source_sha16 缺失" in f["detail"] for f in fails))

    def test_26_missing_probe(self):
        pin, _ = _mcp_pin(self.tmp)
        pin.pop("change_probe")
        fails = cg.freshness_contract(_wrap(pin), self.tmp, TODAY)
        self.assertTrue(any("change_probe 缺失" in f["detail"] for f in fails))

    def test_27_probe_without_query(self):
        pin, _ = _mcp_pin(self.tmp, change_probe={"mode": "manual_review_only"})
        fails = cg.freshness_contract(_wrap(pin), self.tmp, TODAY)
        self.assertTrue(any("检索指针" in f["detail"] for f in fails))


# ---------------------------------------------------------------------------
# 组 6：source_sha16 漂移
# ---------------------------------------------------------------------------
class T6_SourceSha(_Tmp):
    def test_28_untouched_source_passes(self):
        pin, _ = _mcp_pin(self.tmp)
        self.assertEqual(cg.freshness_contract(_wrap(pin), self.tmp, TODAY), [])

    def test_29_one_byte_change_drifts(self):
        pin, src = _mcp_pin(self.tmp)
        with open(src, "a", encoding="utf-8", newline="\n") as f:
            f.write("# drift\n")
        fails = cg.freshness_contract(_wrap(pin), self.tmp, TODAY)
        self.assertTrue(any("漂移" in f["detail"] for f in fails))

    def test_30_source_file_missing(self):
        pin, src = _mcp_pin(self.tmp)
        os.remove(src)
        fails = cg.freshness_contract(_wrap(pin), self.tmp, TODAY)
        self.assertTrue(any("文件不存在" in f["detail"] for f in fails))

    def test_31_baseline_file_drift(self):
        item, art = _baseline(self.tmp)
        with open(art, "a", encoding="utf-8", newline="\n") as f:
            f.write("\n")
        fails = cg.freshness_contract({"regulation_pins": [],
                                       "internal_baselines": [item]}, self.tmp, TODAY)
        self.assertTrue(any("基线文件 sha16 漂移" in f["detail"] for f in fails))


# ---------------------------------------------------------------------------
# 组 7：内部基线（STALE 合法登记不误报）
# ---------------------------------------------------------------------------
class T7_Baseline(_Tmp):
    def test_32_honest_registration_is_green(self):
        item, _ = _baseline(self.tmp)
        fails = cg.freshness_contract({"regulation_pins": [],
                                       "internal_baselines": [item]}, self.tmp, TODAY)
        self.assertEqual(fails, [])

    def test_33_overdue_named_as_stale(self):
        item, _ = _baseline(self.tmp, measured_at="2026-06-01")
        fails = cg.freshness_contract({"regulation_pins": [],
                                       "internal_baselines": [item]}, self.tmp, TODAY)
        self.assertTrue(any("STALE_BASELINE" in f["detail"] for f in fails))

    def test_34_missing_measured_at(self):
        item, _ = _baseline(self.tmp)
        item.pop("measured_at")
        fails = cg.freshness_contract({"regulation_pins": [],
                                       "internal_baselines": [item]}, self.tmp, TODAY)
        self.assertTrue(any("measured_at" in f["detail"] for f in fails))

    def test_35_future_measured_at_is_fake(self):
        item, _ = _baseline(self.tmp, measured_at="2026-12-31")
        fails = cg.freshness_contract({"regulation_pins": [],
                                       "internal_baselines": [item]}, self.tmp, TODAY)
        self.assertTrue(any("在未来" in f["detail"] for f in fails))

    def test_36_core_py_count_changed(self):
        item, _ = _baseline(self.tmp, core_py_count=999)
        fails = cg.freshness_contract({"regulation_pins": [],
                                       "internal_baselines": [item]}, self.tmp, TODAY)
        self.assertTrue(any("核心包 .py 数" in f["detail"] for f in fails))

    def test_37_baseline_tier_mismatch(self):
        item, _ = _baseline(self.tmp, max_age_days=365)
        fails = cg.freshness_contract({"regulation_pins": [],
                                       "internal_baselines": [item]}, self.tmp, TODAY)
        self.assertTrue(any("基线 risk_tier" in f["detail"] for f in fails))


# ---------------------------------------------------------------------------
# 组 8：change_probe 零联网（AST 扫描）
# ---------------------------------------------------------------------------
class T8_NoNetwork(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(ROOT, "holoaeon", "claims_gate.py"), encoding="utf-8") as f:
            cls.tree = ast.parse(f.read())
        cls.top_imports = set()
        for node in cls.tree.body:
            if isinstance(node, ast.Import):
                for a in node.names:
                    cls.top_imports.add(a.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                cls.top_imports.add(node.module.split(".")[0])

    def test_38_no_socket_import(self):
        self.assertNotIn("socket", self.top_imports)

    def test_39_no_urllib_or_requests(self):
        for bad in ("urllib", "urllib2", "requests", "http", "httpx"):
            self.assertNotIn(bad, self.top_imports)

    def test_40_probe_is_manual_only(self):
        self.assertIn("manual_review_only", cg.VALID_PROBE_MODE)
        self.assertNotIn("auto_verified", cg.VALID_PROBE_MODE)


# ---------------------------------------------------------------------------
# 组 9：八只金丝雀
# ---------------------------------------------------------------------------
class T9_Canary(_Tmp):
    def test_41_c1_single_version_site_red(self):
        pin, _ = _mcp_pin(self.tmp)
        pin["version_chain"] = [c for c in pin["version_chain"]
                                if "2024-11-05" not in str(c.get("version"))]
        fails = cg.claim_site_consistent(_wrap(pin), self.tmp)
        self.assertTrue(fails)
        self.assertIn("README.md#L1", fails[0]["detail"])

    def test_42_c2_runtime_pointer_red(self):
        pin, _ = _mcp_pin(self.tmp)
        pin.pop("runtime_pointer")
        self.assertTrue(cg.runtime_version_registered(_wrap(pin), self.tmp))

    def test_43_c3_no_chain_red(self):
        pin, _ = _mcp_pin(self.tmp)
        pin.pop("version_chain")
        self.assertTrue(cg.runtime_version_registered(_wrap(pin), self.tmp))

    def test_44_c4_fast_but_365_red(self):
        pin, _ = _mcp_pin(self.tmp, max_age_days=365)
        self.assertTrue(cg.freshness_contract(_wrap(pin), self.tmp, TODAY))

    def test_45_c5_source_drift_red(self):
        pin, src = _mcp_pin(self.tmp)
        with open(src, "a", encoding="utf-8", newline="\n") as f:
            f.write("# c5\n")
        self.assertTrue(cg.freshness_contract(_wrap(pin), self.tmp, TODAY))

    def test_46_c6_baseline_fake_red(self):
        item, _ = _baseline(self.tmp)
        item.pop("measured_at")
        self.assertTrue(cg.freshness_contract({"regulation_pins": [],
                                               "internal_baselines": [item]}, self.tmp, TODAY))

    def test_47_c7_probe_claims_online_red(self):
        pin, _ = _mcp_pin(self.tmp, change_probe={"probe_query": "x", "mode": "auto_verified"})
        fails = cg.freshness_contract(_wrap(pin), self.tmp, TODAY)
        self.assertTrue(any("不得声称已联网核实" in f["detail"] for f in fails))

    def test_48_c8_self_digest_red(self):
        reg = {"regulation_pins": [], "self_digest": "0" * 16}
        self.assertTrue(cg.check_self_digest(reg))


# ---------------------------------------------------------------------------
# 组 10：自摘要自洽 + 零第三方依赖
# ---------------------------------------------------------------------------
class T10_Digest(unittest.TestCase):
    def _reg(self):
        reg = {"regulation_pins": [], "internal_baselines": [],
               "doc_claims": [], "coverage": [], "totals": {}}
        reg["self_digest"] = cg.self_digest(reg)
        return reg

    def test_49_self_digest_self_consistent(self):
        reg = self._reg()
        self.assertEqual(cg.check_self_digest(reg), [])

    def test_50_edit_without_rehash_red(self):
        reg = self._reg()
        reg["doc_claims"] = [{"id": "x"}]
        self.assertTrue(cg.check_self_digest(reg))

    def test_51_self_digest_excludes_itself(self):
        reg = self._reg()
        before = cg.self_digest(reg)
        reg["self_digest"] = "f" * 16
        self.assertEqual(cg.self_digest(reg), before)

    def test_52_full_verify_is_deterministic(self):
        reg = self._reg()
        v1 = cg.verify(reg, cg._ctx(ROOT), TODAY)
        v2 = cg.verify(reg, cg._ctx(ROOT), TODAY)
        self.assertEqual(v1["digest"], v2["digest"])

    def test_53_no_third_party_imports(self):
        with open(os.path.join(ROOT, "holoaeon", "claims_gate.py"), encoding="utf-8") as f:
            tree = ast.parse(f.read())
        if hasattr(sys, "stdlib_module_names"):
            allowed = set(sys.stdlib_module_names)
        else:
            # py3.8 没有 sys.stdlib_module_names（3.10 才引入）。空集会把 json/hashlib
            # 这类标准库也判成第三方，于是 py3.8 的 CI 必红（V81 实测）。这里退回
            # 「内置模块名 + 本闸实际允许的标准库白名单」——仍是白名单，不是放行。
            allowed = set(sys.builtin_module_names) | {
                "ast", "json", "datetime", "hashlib", "os", "re", "sys", "io",
                "shutil", "tempfile", "collections", "textwrap", "typing", "time",
                "urllib", "pathlib", "subprocess", "itertools", "functools",
                "copy", "inspect", "traceback", "random", "math",
            }
        for node in tree.body:
            mods = []
            if isinstance(node, ast.Import):
                mods = [a.name.split(".")[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                mods = [node.module.split(".")[0]]
            for m in mods:
                self.assertTrue(m == "holoaeon" or m in allowed or m.startswith("_"),
                                "第三方顶层 import: %s" % m)


# =========================================================================
# 组 11 · 日期口径（UTC runner 假红，V81 实测 CI 三版本全红后补）
# =========================================================================
class TestTodayCaliber(unittest.TestCase):
    """GitHub runner 是 UTC：本地 2026-11-14 02:36 时 UTC 仍是 11-13。

    闸原先用 `date.today()`，会把「当天（本地）登记的 verified_at」判成
    「在未来」，于是 pin_freshness 面变红 → test_v75 test_39（断言其他面
    不得跟着红）在 CI 上必红。修法是把「今天」显式定成仓内口径 UTC+8。
    """

    def test_56_today_is_utc_plus_8(self):
        import datetime
        utc = datetime.datetime.utcnow()
        self.assertEqual(cg._today_cst(), (utc + datetime.timedelta(hours=8)).date())
        # 与 UTC 日期最多差 1 天（08:00 前后的窗口），不会漂更多
        self.assertIn((cg._today_cst() - utc.date()).days, (0, 1))

    def test_57_future_pin_still_red(self):
        """口径改成 UTC+8 不等于放过未来日期：today 早于 verified_at 照样红。"""
        reg = {"regulation_pins": [{
            "id": "TZ", "version": "1.0", "status": "current",
            "verified_at": "2026-11-14", "max_age_days": 90,
        }]}
        rep = cg.check_regulation_pins(reg, today="2026-11-13")
        detail = " ".join(f["detail"] for f in rep)
        self.assertIn("在未来", detail)


if __name__ == "__main__":
    unittest.main()
