# -*- coding: utf-8 -*-
"""V46 药品域闸门 + 本地模型探测器测试。零依赖，确定性断言。"""
import importlib.util
import os
import sys
import tempfile
import unittest

from holoaeon import pharma_gate as pg


def _load_probe():
    """bridges/ 是脚本目录（非包）：按文件路径加载——与真实仓同构。"""
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(here, "bridges", "local_model_probe.py")
    spec = importlib.util.spec_from_file_location("local_model_probe", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


lp = _load_probe()


class TestPharmaGate(unittest.TestCase):
    def test_chain_ring14(self):
        self.assertEqual(pg.CHAIN_POSITION["ring"], 14)
        self.assertIn("药品域", pg.CHAIN_POSITION["name"])

    def test_seal(self):
        self.assertEqual(pg.SEAL, "潮起开门，潮落闭嘴")

    def test_schema_has_no_dose_field(self):
        self.assertNotIn("dose", pg.CATALOG_FIELDS)  # 零剂量：schema 级

    def test_validate_entry_rejects_dose(self):
        e = dict(pg.SAMPLE_ENTRIES[0], dose="25mg")
        r = pg.validate_entry(e)
        self.assertFalse(r["ok"])
        self.assertIn("零剂量", r["error"])

    def test_validate_entry_rejects_bad_class(self):
        e = dict(pg.SAMPLE_ENTRIES[0], insurance_class="丙类")
        self.assertFalse(pg.validate_entry(e)["ok"])

    def test_validate_entry_requires_evidence_class(self):
        e = {k: v for k, v in pg.SAMPLE_ENTRIES[0].items()
             if k != "evidence_class"}
        self.assertFalse(pg.validate_entry(e)["ok"])

    def test_validate_entry_rejects_bad_year(self):
        e = dict(pg.SAMPLE_ENTRIES[0], catalog_year="2025")
        self.assertFalse(pg.validate_entry(e)["ok"])

    def test_lookup_exact_match(self):
        reg = pg.build_default_registry()
        r = reg.lookup("二甲双胍片（示例）")
        self.assertTrue(r["found"])
        self.assertEqual(r["insurance_class"], "甲类")
        self.assertEqual(r["evidence_class"], "simulated")

    def test_lookup_unknown_not_noninsurance(self):
        reg = pg.build_default_registry()
        r = reg.lookup("不存在的药")
        self.assertFalse(r["found"])
        self.assertEqual(r["status"], "unknown")
        self.assertIn("未登记≠非医保", r["note"])  # 诚实四态

    def test_version_pin(self):
        reg = pg.build_default_registry()
        v = reg.version_pin()
        self.assertEqual(v["catalog_years"], [2025])
        self.assertEqual(v["entries"], 3)

    def test_disposal_gate_blocks_four(self):
        for a in pg.REDLINE_ACTIONS:
            self.assertEqual(pg.DisposalGate.check(a)["verdict"], "BLOCK")
        self.assertEqual(pg.DisposalGate.check("registry_query")["verdict"],
                         "ALLOW")

    def test_sample_entries_simulated(self):
        for e in pg.SAMPLE_ENTRIES:
            self.assertEqual(e["evidence_class"], "simulated")

    def test_audit_snapshot(self):
        s = pg.audit()
        self.assertFalse(s["has_dose_field"])
        self.assertTrue(s["zero_dose"])
        self.assertIn("exact", s["lookup_mode"])
        self.assertFalse(s["neural"])


class TestLocalModelProbe(unittest.TestCase):
    def test_seal(self):
        self.assertEqual(lp.SEAL, "潮起开门，潮落闭嘴")

    def test_probe_services_shape(self):
        r = lp.probe_services()
        self.assertEqual(len(r), 3)
        self.assertEqual({x["status"] for x in r} <= {"up", "down"}, True)

    def test_probe_port_closed_is_down(self):
        # 127.0.0.1:1 几乎必然 refused → down（确定性）
        self.assertEqual(lp.probe_port("127.0.0.1", 1, timeout=0.2), "down")

    def test_probe_gguf_tempdir(self):
        with tempfile.TemporaryDirectory() as d:
            open(os.path.join(d, "test-model.gguf"), "wb").write(b"\x00" * 10)
            found = lp.probe_gguf_files(extra_dirs=(d,))
            self.assertEqual(len(found), 1)
            self.assertEqual(found[0]["bytes"], 10)

    def test_probe_packages_shape(self):
        r = lp.probe_packages()
        self.assertEqual(len(r), 3)
        std = next(x for x in r if x["package"] == "llama_cpp")
        self.assertIsInstance(std["installed"], bool)

    def test_discover_readonly_with_stamp(self):
        r = lp.discover()
        self.assertTrue(r["ok"])
        self.assertTrue(r["read_only"])
        self.assertIn("scanned_at", r)  # 台账时点（SyncLedger 同构）

    def test_probe_not_in_core_package(self):
        # 位置纪律：探测器在 bridges/，核心包零网络不被污染
        self.assertFalse(hasattr(sys.modules["holoaeon"],
                                 "local_model_probe"))
        src = open(lp.__file__, encoding="utf-8").read()
        self.assertIn("import socket", src)


if __name__ == "__main__":
    unittest.main()

