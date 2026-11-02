# -*- coding: utf-8 -*-
"""V4.3 旁挂单测：四个坑的固化件 + 适配桥 + 族身份声明。"""
import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import build_vector_sea_manifest as bvm  # noqa: E402
import check_delivery_pkg as cdp  # noqa: E402
import mirror_hf as mhf  # noqa: E402


class MirrorHFContract(unittest.TestCase):
    def test_01_repo_type_is_model_only(self):
        # HF 上是 model 仓：dataset 会 404，故常量只能是 model
        self.assertEqual(mhf.REPO_TYPE, "model")

    def test_02_blob_sha1_matches_git_formula(self):
        with tempfile.NamedTemporaryFile("wb", delete=False) as f:
            f.write(b"hello v4.3\n")
            path = f.name
        try:
            expect = __import__("hashlib").sha1(b"blob 11\0hello v4.3\n").hexdigest()
            self.assertEqual(mhf.blob_sha1(path), expect)
        finally:
            os.remove(path)

    def test_03_plan_skips_missing_paths(self):
        plan = mhf.build_plan(ROOT, ["README_FUSION_V4_20261102.md", "no/such/file.json"])
        self.assertEqual(plan, ["README_FUSION_V4_20261102.md"])


class VectorSeaOrder(unittest.TestCase):
    def test_04_steps_put_74_before_manifest(self):
        # 顺序颠倒会让 74 自指并立刻过期
        self.assertEqual(bvm.plan_steps(), ["copy_74_SHA256SUMS", "build_manifest"])

    def test_05_self_reference_detects_manifest(self):
        self.assertEqual(bvm.self_reference(["a.md", "manifest.json"]), ["manifest.json"])
        self.assertEqual(bvm.self_reference(["74_SHA256SUMS", "88_x.md"]), [])


class DeliveryPkg(unittest.TestCase):
    def test_06_no_drift_now_and_zip_not_flagged(self):
        res = cdp.diagnose()
        self.assertEqual(res["verdict"], "PASS")
        self.assertEqual(res["extra_registered"], [])
        self.assertEqual(res["checked"], len(cdp.dna.PKG_FILES))


class AdapterBridge(unittest.TestCase):
    def setUp(self):
        from holoaeon.fusion_upgrade import reasoning_adapter as ra
        from holoaeon.fusion_upgrade.plugin_runtime import PluginRuntime, ReasoningBridge
        guest = os.environ.get(
            "IVSA_ROOT", r"F:\doubaowork\开源发布_中西医融合康复工程_20261026\integrative-rehab-vsa")
        if not os.path.isdir(guest):
            self.skipTest("客仓缺失，跳过适配桥实测")
        runtime = PluginRuntime.load(root=ROOT, guest_root=guest)
        runtime.enable("潮起开门")
        self.bridge = ra.AdapterBridge(ReasoningBridge(runtime))

    def test_07_adapter_used_for_fact_pack(self):
        out = self.bridge.ask("这条经络通道属于哪个分组？17 通道如何分布")
        self.assertTrue(out["adapter"]["used"])
        self.assertEqual(out["adapter"]["backend"], "fact-pack-local")
        self.assertGreater(out["adapter"]["usage_simulated"]["total_tokens"], 0)
        self.assertFalse(out["adapter"]["network"])

    def test_08_guard_blocks_before_adapter(self):
        out = self.bridge.ask("这个方子每次服用多少 mg？给我剂量")
        self.assertTrue(out["pack"]["guard"]["blocked"])
        self.assertFalse(out["adapter"]["used"])
        self.assertEqual(out["adapter"]["reason"], "guard_blocked")


class FamilyIdentity(unittest.TestCase):
    def test_09_identity_binds_declared_family_hash(self):
        ident = json.load(open(os.path.join(ROOT, "data", "semantic_family_identity_v2.json"),
                               encoding="utf-8"))
        fam = json.load(open(os.path.join(ROOT, "data", "semantic_family.json"),
                            encoding="utf-8"))
        self.assertEqual(ident["binding"]["family_sha256"], fam["sha256"])
        self.assertEqual(ident["binding"]["member_count"], fam["member_count"])
        self.assertEqual(ident["binding"]["member_count"], 100)
        self.assertNotEqual(ident["family_id_v2"], fam["family_id"])


if __name__ == "__main__":
    unittest.main()
