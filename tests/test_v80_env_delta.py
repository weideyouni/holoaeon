# -*- coding: utf-8 -*-
"""V80 · claims_gate 第 11 面 `env_delta_consistency` 测试。

50 例 / 十组 / 8 只金丝雀（C1–C8）。
纪律：不写死真实仓数值，全部走自造 tmp 上下文（沿用 test_v75/v79 先例）；
不联网、不读 CI 日志、不跑外部命令；除 G10 只读真注册簿外零副作用。
"""
import io
import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holoaeon import claims_gate as cg  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GUARD_SRC = '''# -*- coding: utf-8 -*-
import os
import unittest

SITE = os.path.isdir(r"F:\\\\tmp\\\\site")
GUARD = unittest.skipUnless(os.path.isdir(r"F:\\\\tmp\\\\guest"), "no guest")


@unittest.skipUnless(os.path.isdir(r"F:\\\\tmp\\\\site"), "no site")
class GMain(unittest.TestCase):
    def test_a(self):
        pass

    def test_b(self):
        pass


@GUARD
def test_alias_guarded(self):
    pass


class GRuntime(unittest.TestCase):
    def setUp(self):
        raise unittest.SkipTest("real site missing")

    def test_c(self):
        pass

    def test_d(self):
        pass


class GManual(unittest.TestCase):
    def test_e(self):
        self.skipTest("runtime none")
'''

ZH_OK = "- **工程验收（双口径回读）**：主套 **100 OK**（本机）／**95 OK**（云端 py3.12），差值逐条见注册簿"
EN_OK = "- **Gates (measured on this machine)**: main suite **100 local / 95 cloud** per env registry"


def mkroot():
    return tempfile.mkdtemp(prefix="v80_env_")


def w(root, rel, text):
    p = os.path.join(root, rel)
    d = os.path.dirname(p)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with io.open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return p


def guard_file(root, rel="tests/test_guarded.py", src=GUARD_SRC):
    return w(root, rel, src)


def seed_parity_entries(explained_main=("D01",), explained_contract=("D02",),
                        d01_cloud_skip=10, d01_cloud_nd=5,
                        d01_local_skip=0, d01_local_nd=0,
                        main_local=(100, 1), main_cloud=(95, 11),
                        con_local=(184, 0), con_cloud=(184, 11),
                        status_d01="", status_d02=""):
    """主套差值：ran -5 / skip +10；契约套：ran 0 / skip +11。"""
    d01 = {"id": "D01", "dimension": "f_drive_assets", "title": "F 盘素材",
           "local": {"value": "present", "evidence": "本机有 F 盘"},
           "cloud": {"value": "absent", "evidence": "云端无 F 盘"},
           "guards": [], "measured_at": "2026-11-14", "risk_tier": "fast",
           "suite": "main",
           "skip_attributed": {"local": d01_local_skip, "cloud": d01_cloud_skip},
           "not_discovered": {"local": d01_local_nd, "cloud": d01_cloud_nd}}
    if status_d01:
        d01["status"] = status_d01
    d02 = {"id": "D02", "dimension": "ivsa_guest_repo", "title": "客仓",
           "local": {"value": "present", "evidence": "本机有客仓"},
           "cloud": {"value": "absent", "evidence": "云端无客仓"},
           "guards": [], "measured_at": "2026-11-14", "risk_tier": "fast",
           "suite": "contract",
           "skip_attributed": {"local": 0, "cloud": 11}}
    if status_d02:
        d02["status"] = status_d02
    d04 = {"id": "D04", "dimension": "memory_of_yuan_module", "title": "仓外模块",
           "local": {"value": "absent", "evidence": "本机未装"},
           "cloud": {"value": "absent", "evidence": "云端未装"},
           "guards": [], "measured_at": "2026-11-14", "risk_tier": "stable",
           "suite": "main", "skip_attributed": {"local": 1, "cloud": 1}}
    d08 = {"id": "D08", "dimension": "parity_main_suite", "title": "主套对账",
           "local": {"ran": main_local[0], "skipped": main_local[1],
                     "executed": main_local[0] - main_local[1], "evidence": "本机"},
           "cloud": {"ran": main_cloud[0], "skipped": main_cloud[1],
                     "executed": main_cloud[0] - main_cloud[1], "evidence": "云端"},
           "gap": {"ran_diff": main_cloud[0] - main_local[0],
                   "executed_diff": (main_cloud[0] - main_cloud[1]) - (main_local[0] - main_local[1]),
                   "explained_by": list(explained_main)},
           "guards": [], "measured_at": "2026-11-14", "risk_tier": "fast", "suite": "main"}
    d09 = {"id": "D09", "dimension": "parity_contract_suite", "title": "契约对账",
           "local": {"ran": con_local[0], "skipped": con_local[1],
                     "executed": con_local[0] - con_local[1], "evidence": "本机"},
           "cloud": {"ran": con_cloud[0], "skipped": con_cloud[1],
                     "executed": con_cloud[0] - con_cloud[1], "evidence": "云端"},
           "gap": {"ran_diff": con_cloud[0] - con_local[0],
                   "executed_diff": (con_cloud[0] - con_cloud[1]) - (con_local[0] - con_local[1]),
                   "explained_by": list(explained_contract)},
           "guards": [], "measured_at": "2026-11-14", "risk_tier": "fast", "suite": "contract"}
    return [d01, d02, d04, d08, d09]


def seal(entries):
    reg = {"schema": cg.ENV_DELTA_SCHEMA, "as_of": "2026-11-14", "entries": entries}
    reg["self_digest"] = cg._sha16(reg)
    return reg


def ctx_of(root, zh=ZH_OK, en=EN_OK):
    return cg._ctx(root=root, texts={"readme_zh": zh, "readme_en": en})


def fails_of(reg, root, zh=ZH_OK, en=EN_OK):
    return cg.env_delta_consistency(reg, ctx_of(root, zh, en))["fails"]


def kw(fails, needle):
    return [f for f in fails if needle in (f.get("detail") or "")]


class G1Structural(unittest.TestCase):
    """结构：第 11 面进 FACES、面序、report 回读。"""

    def test_01_face_constant(self):
        self.assertEqual(cg.FACE_ENV_DELTA, "env_delta_consistency")

    def test_02_face_registered_in_faces(self):
        self.assertIn(cg.FACE_ENV_DELTA, cg.FACES)

    def test_03_face_is_last(self):
        self.assertEqual(cg.FACES[-1], cg.FACE_ENV_DELTA)

    def test_04_face_count_is_eleven(self):
        self.assertEqual(len(cg.FACES), 11)

    def test_05_report_exposes_eleven_faces(self):
        rep = cg.report()
        self.assertEqual(len(rep["faces"]), 11)
        self.assertIn(cg.FACE_ENV_DELTA, rep["faces"])

    def test_06_report_has_env_delta_block(self):
        rep = cg.report()
        self.assertIn("env_delta", rep)
        self.assertIn("guards_total", rep["env_delta"])


class G2SchemaAndEntry(unittest.TestCase):
    """注册簿 schema 与条目完备性。"""

    def setUp(self):
        self.root = mkroot()

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_07_good_registry_passes(self):
        reg = seal(seed_parity_entries())
        self.assertEqual([], fails_of(reg, self.root))

    def test_08_missing_registry_is_red(self):
        self.assertTrue(kw(fails_of(cg.load_env_registry(self.root), self.root), "缺失或为空"))

    def test_09_bad_schema_is_red(self):
        reg = seal(seed_parity_entries())
        reg["schema"] = "WRONG-v9"
        reg["self_digest"] = cg._sha16({k: v for k, v in reg.items() if k != "self_digest"})
        self.assertTrue(kw(fails_of(reg, self.root), "schema"))

    def test_10_entry_without_id_is_red(self):
        e = seed_parity_entries()
        del e[0]["id"]
        self.assertTrue(kw(fails_of(seal(e), self.root), "缺字段 id"))

    def test_11_entry_without_evidence_is_red(self):
        e = seed_parity_entries()
        del e[0]["local"]["evidence"]
        self.assertTrue(kw(fails_of(seal(e), self.root), "local.evidence 缺失"))

    def test_12_cloud_evidence_required(self):
        e = seed_parity_entries()
        del e[0]["cloud"]["evidence"]
        self.assertTrue(kw(fails_of(seal(e), self.root), "cloud.evidence 缺失"))

    def test_13_empty_side_is_red(self):
        e = seed_parity_entries()
        e[0]["local"] = {}
        self.assertTrue(kw(fails_of(seal(e), self.root), "local 段缺失或为空"))

    def test_14_duplicate_id_is_red(self):
        e = seed_parity_entries()
        e[1]["id"] = "D01"
        self.assertTrue(kw(fails_of(seal(e), self.root), "条目 id 重复"))


class G3GuardCensus(unittest.TestCase):
    """守卫普查：四类守卫的识别与归属。"""

    def setUp(self):
        self.root = mkroot()

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_15_decorator_detected(self):
        guard_file(self.root)
        kinds = [g["kind"] for g in cg.scan_env_guards(self.root)]
        self.assertIn("decorator", kinds)

    def test_16_module_alias_detected(self):
        guard_file(self.root)
        names = [g["symbol"] for g in cg.scan_env_guards(self.root)]
        self.assertIn("GUARD", names)

    def test_17_module_alias_gets_method_count(self):
        guard_file(self.root)
        gs = [g for g in cg.scan_env_guards(self.root) if g["kind"] == "module_alias"]
        self.assertEqual(1, len(gs))
        self.assertEqual(1, gs[0]["methods"])

    def test_18_runtime_skip_detected(self):
        guard_file(self.root)
        self.assertIn("runtime_skip", [g["kind"] for g in cg.scan_env_guards(self.root)])

    def test_19_raise_skip_detected(self):
        guard_file(self.root)
        self.assertIn("raise_skip", [g["kind"] for g in cg.scan_env_guards(self.root)])

    def test_20_unregistered_guard_is_red_C1(self):
        """C1：新造 F 盘守卫不登记 → unregistered_guard 红。"""
        guard_file(self.root)
        reg = seal(seed_parity_entries())
        f = fails_of(reg, self.root)
        self.assertTrue(kw(f, "未登记的环境守卫"))

    def test_21_register_all_guards_turns_green(self):
        guard_file(self.root)
        guards = ["tests/test_guarded.py:%d" % g["line"]
                  for g in cg.scan_env_guards(self.root)]
        e = seed_parity_entries()
        e[0]["guards"] = guards
        self.assertEqual([], kw(fails_of(seal(e), self.root), "未登记的环境守卫"))

    def test_22_empty_tests_dir_has_no_guards(self):
        self.assertEqual([], cg.scan_env_guards(self.root))


class G4LineAnchor(unittest.TestCase):
    """行锚容差 ±10 与漂移判据。"""

    def setUp(self):
        self.root = mkroot()
        guard_file(self.root)
        self.g = [x for x in cg.scan_env_guards(self.root) if x["kind"] == "decorator"][0]

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_23_exact_line_hits(self):
        e = seed_parity_entries()
        e[0]["guards"] = ["tests/test_guarded.py:%d" % self.g["line"]]
        self.assertEqual([], kw(fails_of(seal(e), self.root), "行锚漂移"))

    def test_24_within_tolerance_hits(self):
        e = seed_parity_entries()
        e[0]["guards"] = ["tests/test_guarded.py:%d" % (self.g["line"] + 8)]
        self.assertEqual([], kw(fails_of(seal(e), self.root), "行锚漂移"))

    def test_25_beyond_tolerance_is_red_C6(self):
        """C6：行号漂移超容差 → 红。"""
        e = seed_parity_entries()
        e[0]["guards"] = ["tests/test_guarded.py:%d" % (self.g["line"] + 60)]
        self.assertTrue(kw(fails_of(seal(e), self.root), "行锚漂移"))

    def test_26_missing_file_is_red(self):
        e = seed_parity_entries()
        e[0]["guards"] = ["tests/nope.py:1"]
        self.assertTrue(kw(fails_of(seal(e), self.root), "文件不存在"))

    def test_27_multi_line_spec_parses(self):
        e = seed_parity_entries()
        e[0]["guards"] = ["tests/test_guarded.py:%d,%d" % (self.g["line"], self.g["line"] + 1)]
        self.assertEqual(2, len(cg._guard_anchors(e[0])[-2:]))


class G5ParityDisclosed(unittest.TestCase):
    """双端计数对账：差值必须登记且计算自洽。"""

    def setUp(self):
        self.root = mkroot()

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_28_missing_parity_entry_is_red(self):
        e = [x for x in seed_parity_entries() if x["dimension"] != "parity_contract_suite"]
        self.assertTrue(kw(fails_of(seal(e), self.root), "缺 parity_contract_suite"))

    def test_29_non_integer_ran_is_red(self):
        reg = seal(seed_parity_entries())
        reg["entries"][3]["cloud"]["ran"] = "1976"
        reg["self_digest"] = cg._sha16({k: v for k, v in reg.items() if k != "self_digest"})
        self.assertTrue(kw(fails_of(reg, self.root), "必须是整数"))

    def test_30_ran_diff_mismatch_is_red(self):
        reg = seal(seed_parity_entries())
        reg["entries"][3]["gap"]["ran_diff"] = -1
        reg["self_digest"] = cg._sha16({k: v for k, v in reg.items() if k != "self_digest"})
        self.assertTrue(kw(fails_of(reg, self.root), "ran_diff 登记"))

    def test_31_executed_diff_mismatch_is_red_C4(self):
        """C4：executed_diff 少报 5 → 红。"""
        reg = seal(seed_parity_entries())
        reg["entries"][3]["gap"]["executed_diff"] = -10
        reg["self_digest"] = cg._sha16({k: v for k, v in reg.items() if k != "self_digest"})
        self.assertTrue(kw(fails_of(reg, self.root), "executed_diff 登记"))

    def test_32_empty_explained_by_is_red(self):
        e = seed_parity_entries(explained_main=())
        self.assertTrue(kw(fails_of(seal(e), self.root), "explained_by 为空"))

    def test_33_unknown_explained_id_is_red_C3(self):
        """C3：explained_by 指向不存在 id → 红。"""
        e = seed_parity_entries(explained_main=("D99",))
        self.assertTrue(kw(fails_of(seal(e), self.root), "指向不存在的条目"))


class G6CoverageLoop(unittest.TestCase):
    """skip 构成与差值覆盖的闭环。"""

    def setUp(self):
        self.root = mkroot()

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_34_skip_composition_mismatch_is_red(self):
        e = seed_parity_entries()
        e[0]["skip_attributed"]["cloud"] = 3          # 12 != cloud 11
        e[2]["skip_attributed"]["cloud"] = 1
        f = fails_of(seal(e), self.root)
        self.assertTrue(kw(f, "云端 skip 构成") or kw(f, "覆盖 skip 差"))

    def test_35_local_skip_composition_mismatch_is_red(self):
        e = seed_parity_entries()
        e[2]["skip_attributed"]["local"] = 0          # 0 != local 1
        self.assertTrue(kw(fails_of(seal(e), self.root), "本机 skip 构成"))

    def test_36_explained_skip_shortfall_is_red(self):
        e = seed_parity_entries(explained_main=("D04",))   # D04 差 0，覆盖不了 10
        self.assertTrue(kw(fails_of(seal(e), self.root), "覆盖 skip 差"))

    def test_37_ran_coverage_required(self):
        e = seed_parity_entries(d01_cloud_nd=0)            # 未解释 ran -5
        f = fails_of(seal(e), self.root)
        self.assertTrue(kw(f, "覆盖 ran 差") or kw(f, "云端 skip 构成"))

    def test_38_resolved_entry_as_explanation_is_red_C8(self):
        """C8：已治项（resolved_by_*）被挪去解释现行差值 → 红。"""
        e = seed_parity_entries(status_d01="resolved_by_V78b")
        self.assertTrue(kw(fails_of(seal(e), self.root), "不得充数解释现行差值"))

    def test_39_full_loop_is_green(self):
        self.assertEqual([], fails_of(seal(seed_parity_entries()), self.root))


class G7ReadmeDualCaliber(unittest.TestCase):
    """README 双口径同屏回读。"""

    def setUp(self):
        self.root = mkroot()

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_40_dual_caliber_green(self):
        self.assertEqual([], fails_of(seal(seed_parity_entries()), self.root))

    def test_41_missing_cloud_number_is_red_C7(self):
        """C7：验收行只写本机数 → 红。"""
        bad = "- **工程验收（本机实跑口径）**：主套 **100 OK**"
        self.assertTrue(kw(fails_of(seal(seed_parity_entries()), self.root, zh=bad),
                           "缺云端数"))

    def test_42_missing_local_number_is_red(self):
        bad = "- **工程验收（双口径回读）**：云端 py3.12 **95 OK**"
        self.assertTrue(kw(fails_of(seal(seed_parity_entries()), self.root, zh=bad),
                           "缺本机数"))

    def test_43_missing_cloud_marker_is_red(self):
        bad = "- **工程验收（双口径回读）**：主套 **100 OK** ／ **95 OK**"
        self.assertTrue(kw(fails_of(seal(seed_parity_entries()), self.root, zh=bad),
                           "未标注云端口径"))

    def test_44_missing_anchor_is_red(self):
        self.assertTrue(kw(fails_of(seal(seed_parity_entries()), self.root, en="no gate line"),
                           "找不到验收行锚"))


class G8SelfDigest(unittest.TestCase):
    """注册簿自摘要：改一字节不重算即红。"""

    def setUp(self):
        self.root = mkroot()

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_45_correct_digest_green(self):
        self.assertEqual([], fails_of(seal(seed_parity_entries()), self.root))

    def test_46_one_byte_edit_is_red_C5(self):
        """C5：改一字节不重算 self_digest → 红。"""
        reg = seal(seed_parity_entries())
        reg["entries"][0]["title"] = reg["entries"][0]["title"] + "x"
        self.assertTrue(kw(fails_of(reg, self.root), "改过注册簿未重算"))

    def test_47_missing_digest_is_red(self):
        reg = seal(seed_parity_entries())
        del reg["self_digest"]
        self.assertTrue(kw(fails_of(reg, self.root), "self_digest 未填"))

    def test_48_digest_is_canonical_sixteen_hex(self):
        reg = seal(seed_parity_entries())
        self.assertEqual(reg["self_digest"], cg._sha16({k: v for k, v in reg.items()
                                                        if k != "self_digest"}))
        self.assertEqual(16, len(reg["self_digest"]))


class G9RegistryStates(unittest.TestCase):
    """注册簿缺/坏/空三态都不抛，只判红。"""

    def setUp(self):
        self.root = mkroot()

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_49_broken_json_is_red_not_raise(self):
        w(self.root, "data/env_delta_registry.json", "{not json")
        reg = cg.load_env_registry(self.root)
        self.assertTrue(reg.get("_broken"))
        self.assertTrue(kw(cg.env_delta_consistency(reg, ctx_of(self.root))["fails"], "缺失或为空"))

    def test_50_empty_entries_is_red(self):
        w(self.root, "data/env_delta_registry.json",
          json.dumps({"schema": cg.ENV_DELTA_SCHEMA, "entries": []}, ensure_ascii=False))
        reg = cg.load_env_registry(self.root)
        self.assertTrue(kw(cg.env_delta_consistency(reg, ctx_of(self.root))["fails"], "缺失或为空"))


class G10RealRegistry(unittest.TestCase):
    """真注册簿的静态自洽（只读；README 双口径面独立判）。"""

    def setUp(self):
        self.reg = cg.load_env_registry(ROOT)
        self.res = cg.env_delta_consistency(self.reg, cg._ctx(root=ROOT))

    def test_51_real_registry_present(self):
        self.assertFalse(self.reg.get("_missing"))
        self.assertGreaterEqual(len(self.reg.get("entries") or []), 9)

    def test_52_every_guard_attributed(self):
        self.assertEqual(self.res["guards_total"], self.res["guards_attributed"])
        self.assertEqual([], self.res["unregistered"])

    def test_53_no_anchor_drift(self):
        self.assertEqual([], self.res["drifted"])

    def test_54_self_digest_consistent(self):
        self.assertEqual(self.reg["self_digest"],
                         cg._sha16({k: v for k, v in self.reg.items() if k != "self_digest"}))

    def test_55_parity_entries_closed(self):
        for dim in cg.ENV_PARITY_DIMS:
            self.assertIn(dim, self.res["parity"])
            item = self.res["parity"][dim]
            self.assertTrue(item["explained_by"])
        # 除 README 双口径位外，本面不应有其他红
        left = [f for f in self.res["fails"]
                if not str(f.get("id") or "").startswith("readme_")]
        self.assertEqual([], left)


if __name__ == "__main__":
    unittest.main(verbosity=2)
