"""V2.1 · ivsa 只读对账契约单测（旁挂）。只读校验：不写 ivsa、不联网。

覆盖：对账器整体 PASS / ivsa 清单 91/91 / 17 通道互认 / 许可分层 / 插件默认关闭 /
源码未入宿主 / 双仓摘要口径 / spec 与维度锁 / 票据在位。
"""

import importlib.util
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

_spec = importlib.util.spec_from_file_location(
    "verify_ivsa_recon", os.path.join(ROOT, "scripts", "verify_ivsa_recon.py"))
V = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V)


class TestIivsaRecon(unittest.TestCase):
    def test_01_ticket_present(self):
        path = os.path.join(ROOT, "data", "V2.1_ivsa只读对账票据.md")
        self.assertTrue(os.path.isfile(path) and os.path.getsize(path) > 0, path)

    def test_02_ivsa_sums_91(self):
        ok, detail = V.check_ivsa_sums()
        self.assertTrue(ok, detail)

    def test_03_channels_17(self):
        ok, detail = V.check_channels()
        self.assertTrue(ok, detail)

    def test_04_license_layers(self):
        ok, detail = V.check_license()
        self.assertTrue(ok, detail)

    def test_05_plugin_default_disabled(self):
        ok, detail = V.check_plugin_default()
        self.assertTrue(ok, detail)

    def test_06_no_source_copy(self):
        ok, detail = V.check_no_source_copy()
        self.assertTrue(ok, detail)

    def test_07_dual_sums_consistent(self):
        ok, detail = V.check_dual_sums()
        self.assertTrue(ok, detail)

    def test_08_spec_and_lock(self):
        ok, detail = V.check_spec_lock()
        self.assertTrue(ok, detail)

    def test_09_recon_all_green(self):
        report = V.run()
        self.assertEqual(report["verdict"], "PASS",
                         json.dumps(report["failed"], ensure_ascii=False))
        self.assertEqual(report["total"], 7)
        self.assertEqual(len(report["seal"]), 64)


if __name__ == "__main__":
    unittest.main()
