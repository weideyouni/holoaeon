# -*- coding: utf-8 -*-
"""B8 · 双仓同步（ivsa v1.2 插件默认关闭 + 双仓 SHA256SUMS 互认）· 旁挂单测。

运行：python -m unittest discover -s tests_contract -v
"""
import csv
import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from holoaeon.fusion_upgrade import dual_sync as DS  # noqa: E402

DATA = os.path.join(ROOT, "data")
REPORTS = os.path.join(ROOT, "reports")
IVSA_ROOT = r"F:\doubaowork\开源发布_中西医融合康复工程_20261026\integrative-rehab-vsa"
SUMS_PATH = os.path.join(ROOT, "SHA256SUMS")


class DualSyncTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.desc = json.load(open(os.path.join(DATA, "ivsa_plugin_v1.2.json"), encoding="utf-8"))
        cls.doc = json.load(open(os.path.join(DATA, "dual_repo_sums.json"), encoding="utf-8"))
        cls.check = json.load(open(os.path.join(REPORTS, "b8_dual_sync_check.json"),
                                   encoding="utf-8"))
        with open(os.path.join(DATA, "许可分层清单.csv"), encoding="utf-8", newline="") as f:
            cls.layers = list(csv.DictReader(f))
        cls.sums_text = open(SUMS_PATH, encoding="utf-8").read()

    def test_01_plugin_default_off(self):
        self.assertEqual(self.desc["plugin_id"], DS.PLUGIN_ID)
        self.assertEqual(self.desc["version"], "1.2")
        self.assertFalse(self.desc["enabled_by_default"])
        self.assertTrue(self.desc["requires_explicit_enable"])
        self.assertEqual(self.desc["default_state"], "disabled")

    def test_02_load_plugin_does_not_auto_enable(self):
        off = DS.load_plugin()
        self.assertEqual(off["state"], "disabled")
        self.assertEqual(off["capabilities_loaded"], 0)
        on = DS.load_plugin(enable=True)
        self.assertEqual(on["state"], "enabled")
        self.assertEqual(on["capabilities_loaded"], len(DS.CAPABILITIES))

    def test_03_dimension_contract_untouched(self):
        self.assertEqual(self.desc["dimension_contract"],
                         {"agents": 25, "skills": 47, "packs": 9})

    def test_04_unknown_capability_rejected(self):
        with self.assertRaises(KeyError):
            DS.resolve_capability("phantom")
        self.assertTrue(DS.resolve_capability("channel_groups_17")["ok"])

    def test_05_interface_equal_17(self):
        iface = DS.interface_check(os.path.join(ROOT, DS.INTERFACE["holo"]),
                                   os.path.join(IVSA_ROOT, DS.INTERFACE["ivsa"]))
        self.assertTrue(iface["equal"])
        self.assertEqual(iface["total_holo"], 17)
        self.assertEqual(iface["groups_holo_mapped"],
                         {"blood": 4, "lymph": 4, "qi": 5, "shen": 4})

    def test_06_interface_mismatch_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            holo = os.path.join(tmp, "h.csv")
            ivsa = os.path.join(tmp, "i.csv")
            with open(holo, "w", encoding="utf-8", newline="") as f:
                f.write("group\n气\n气\n气\n气\n气\n血\n")
            with open(ivsa, "w", encoding="utf-8", newline="") as f:
                f.write("group\nqi\nqi\nqi\nqi\nqi\nblood\nblood\n")
            self.assertFalse(DS.interface_check(holo, ivsa)["equal"])

    def test_07_sums_deterministic_and_self_excluded(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name in ("b.txt", "a.txt"):
                with open(os.path.join(tmp, name), "w", encoding="utf-8") as f:
                    f.write(name)
            open(os.path.join(tmp, "SHA256SUMS"), "w", encoding="utf-8").close()
            lines = DS.build_sums(tmp, ["b.txt", "a.txt", "SHA256SUMS"])
            self.assertEqual([l.split("  ")[1] for l in lines], ["a.txt", "b.txt"])
            self.assertEqual(DS.sums_digest(lines), DS.sums_digest(lines))

    def test_08_tamper_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "x.txt")
            with open(path, "w", encoding="utf-8") as f:
                f.write("v1")
            text = "\n".join(DS.build_sums(tmp, ["x.txt"])) + "\n"
            self.assertTrue(DS.verify_sums(tmp, text)["ok"])
            with open(path, "w", encoding="utf-8") as f:
                f.write("v2")
            got = DS.verify_sums(tmp, text)
            self.assertFalse(got["ok"])
            self.assertEqual(got["bad_sha256"], ["x.txt"])

    def test_09_license_layers_no_mixing(self):
        self.assertGreaterEqual(len(self.layers), 5)
        self.assertEqual(DS.license_mixed(self.layers), [])
        self.assertTrue(all(r["license"] in ("Apache-2.0", "MPL-2.0", "data-only")
                            for r in self.layers))

    def test_10_dual_doc_verdict_and_counts(self):
        self.assertEqual(self.doc["sums_id"], "SG-B8-DUAL-REPO-SUMS-V1")
        self.assertEqual(self.doc["verdict"], "PASS")
        self.assertTrue(self.doc["interface"]["result"]["equal"])
        self.assertEqual(self.doc["ivsa"]["recompute"]["checked"], 91)
        self.assertGreaterEqual(self.doc["holoaeon"]["entries"], 150)
        self.assertEqual(self.check["verdict"], "PASS")
        self.assertEqual(self.check["failed"], [])

    def test_11_sums_match_recorded_digest(self):
        recomputed = DS.sums_digest([l for l in self.sums_text.splitlines() if l.strip()])
        self.assertEqual(recomputed, self.doc["holoaeon"]["sums_sha256"])
        v = DS.verify_sums(ROOT, self.sums_text)
        self.assertTrue(v["ok"])
        self.assertEqual(v["checked"], self.doc["holoaeon"]["entries"])


if __name__ == "__main__":
    unittest.main()
