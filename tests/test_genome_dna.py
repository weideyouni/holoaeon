# -*- coding: utf-8 -*-
"""V86 内核基因 DNA 单测：三基因可失败 / 恒真守卫 / 八面双态 / 经络动态化。

纪律：纯标准库 / 零网络 / 确定性 / 零剂量 / 先红后绿。
"""
import copy
import hashlib
import io
import json
import os
import unittest

from holoaeon import genome_dna as gd
from holoaeon import meridian_link as ml

TRUE_HOMOLOGY = {"mechanism_axis": True, "heartbeat": True, "seal": True}


def _manifest(**overrides):
    m = {
        "physical": {"path": "F:/doubaowork/x", "sha256": "a" * 64},
        "protocol": {"protocol_family": "HOLOAEON", "seal": gd.SEAL},
        "data": {"data_locality": "on_box", "zero_dose": True},
        "deploy": {"standalone_entry": "python main.py", "dependencies": []},
        "degradation": {"try_import_skip": True, "env_delta_registered": True},
        "security": {"zero_network": True, "no_secret_on_box": True},
        "genome": {"genome_id": gd.GENOME_ID, "mechanism_subset": list(gd.MECHANISM_AXIS)},
        "meridian": {"link_back": 3, "fragment_id": "p001", "bus_channel": "bus"},
        "standalone_ok": True, "genomic_ok": True,
    }
    m.update(overrides)
    return m


class TestIdentity(unittest.TestCase):
    def test_genome_id(self):
        self.assertEqual(gd.GENOME_ID, "HOLOAEON-GENOME-DNA-v1.0")

    def test_dna_version_self_governed(self):
        self.assertEqual(gd.DNA_VERSION, "1.0.0")

    def test_seal(self):
        self.assertEqual(gd.SEAL, "潮起开门，潮落闭嘴")
        self.assertEqual(gd.SEAL, ml.SEAL)

    def test_25_axis_identical_to_meridian_link(self):
        self.assertEqual(len(gd.MECHANISM_AXIS), 25)
        self.assertEqual(list(gd.MECHANISM_AXIS),
                         [m["id"] for m in ml.KERNEL_MECHANISMS])

    def test_eight_faces(self):
        self.assertEqual(len(gd.PLUGIN_FACES), 8)
        self.assertIn("genome", gd.PLUGIN_FACES)
        self.assertIn("meridian", gd.PLUGIN_FACES)


class TestGrowthAxiom(unittest.TestCase):
    def test_growth_green(self):
        r = gd.growth_check(3, 0, 3, "HOLOAEON", gd.SEAL)
        self.assertTrue(r["pass"])
        self.assertEqual(r["verdict"], "growth")

    def test_copies_red(self):
        self.assertFalse(gd.growth_check(3, 1, 3, "HOLOAEON", gd.SEAL)["pass"])

    def test_no_linkback_red(self):
        self.assertFalse(gd.growth_check(0, 0, 0, "HOLOAEON", gd.SEAL)["pass"])

    def test_seal_mismatch_red(self):
        self.assertFalse(gd.growth_check(3, 0, 3, "HOLOAEON", "错密令")["pass"])

    def test_family_mismatch_red(self):
        self.assertFalse(gd.growth_check(3, 0, 3, "OTHER", gd.SEAL)["pass"])

    def test_negative_input_red(self):
        self.assertFalse(gd.growth_check(-1, 0, 3, "HOLOAEON", gd.SEAL)["pass"])


class TestDifferentiationAxiom(unittest.TestCase):
    def test_differentiation_green(self):
        r = gd.differentiation_check(0.9, TRUE_HOMOLOGY, True, 0.8)
        self.assertTrue(r["pass"])

    def test_theta_none_red(self):
        self.assertFalse(gd.differentiation_check(0.9, TRUE_HOMOLOGY, True, None)["pass"])

    def test_theta_one_red(self):
        self.assertFalse(gd.differentiation_check(0.99, TRUE_HOMOLOGY, True, 1.0)["pass"])

    def test_similarity_below_theta_red(self):
        self.assertFalse(gd.differentiation_check(0.5, TRUE_HOMOLOGY, True, 0.8)["pass"])

    def test_axis_drift_red(self):
        h = dict(TRUE_HOMOLOGY, mechanism_axis=False)
        self.assertFalse(gd.differentiation_check(0.9, h, True, 0.8)["pass"])

    def test_not_specialized_red(self):
        self.assertFalse(gd.differentiation_check(0.9, TRUE_HOMOLOGY, False, 0.8)["pass"])


class TestRobustnessAxiom(unittest.TestCase):
    def test_robust_green(self):
        self.assertTrue(gd.robustness_check(True, True, True, True, 250, 250,
                                           TRUE_HOMOLOGY)["pass"])

    def test_skip_swallowed_red(self):
        self.assertFalse(gd.robustness_check(False, True, True, True, 250, 250,
                                            TRUE_HOMOLOGY)["pass"])

    def test_output_drift_red(self):
        self.assertFalse(gd.robustness_check(True, False, True, True, 250, 250,
                                            TRUE_HOMOLOGY)["pass"])

    def test_spec_modified_red(self):
        self.assertFalse(gd.robustness_check(True, True, False, True, 250, 250,
                                            TRUE_HOMOLOGY)["pass"])

    def test_cells_mismatch_red(self):
        self.assertFalse(gd.robustness_check(True, True, True, True, 275, 250,
                                            TRUE_HOMOLOGY)["pass"])

    def test_genome_hash_drift_red(self):
        self.assertFalse(gd.robustness_check(True, True, True, False, 250, 250,
                                            TRUE_HOMOLOGY)["pass"])


class TestPluginContract(unittest.TestCase):
    def test_dual_state_green(self):
        r = gd.plugin_contract_check(_manifest())
        self.assertTrue(r["pass"])
        self.assertTrue(r["dual_state_ok"])

    def test_orphan_red(self):
        self.assertFalse(gd.plugin_contract_check(_manifest(genomic_ok=False))["pass"])

    def test_parasite_red(self):
        self.assertFalse(gd.plugin_contract_check(_manifest(standalone_ok=False))["pass"])

    def test_missing_face_red(self):
        m = _manifest()
        m.pop("genome")
        self.assertFalse(gd.plugin_contract_check(m)["pass"])

    def test_no_linkback_red(self):
        m = _manifest(meridian={"link_back": 0})
        self.assertFalse(gd.plugin_contract_check(m)["pass"])


class TestGenomeIntegrity(unittest.TestCase):
    def test_verify_green(self):
        v = gd.verify()
        self.assertTrue(v["pass"], v["problems"])
        self.assertEqual(v["axioms"], 3)

    def test_eternal_true_guard_present(self):
        self.assertEqual(gd.verify()["guards"], 4)

    def test_self_check_deterministic(self):
        a = json.dumps(gd.self_check(), ensure_ascii=False, sort_keys=True)
        b = json.dumps(gd.self_check(), ensure_ascii=False, sort_keys=True)
        self.assertEqual(a, b)

    def test_genome_hash_stable(self):
        self.assertEqual(gd.genome_hash(), gd.genome_hash())
        self.assertEqual(len(gd.genome_hash()), 64)

    def test_registry_only_dual_state_fragments(self):
        """注册表可空可实：registered_fragments 只返回**双态同时为真**的条目。

        V86 批3 起注册表承载真实试点，故不再断言「恒为空」——那只在
        初始态成立；硬断空表会让第一次合法 append 就把测试打红。
        """
        with io.open(gd._REGISTRY_PATH, "r", encoding="utf-8") as fh:
            reg = json.load(fh)
        self.assertEqual(reg["schema"], gd.SCHEMA)
        self.assertTrue(reg["append_only"])
        expect = sum(1 for x in reg.get("plugins", [])
                     if x.get("standalone_ok") and x.get("genomic_ok"))
        self.assertEqual(len(gd.registered_fragments()), expect)


class TestMeridianDynamic(unittest.TestCase):
    def _extra(self, name, rank):
        return {"repo": name, "rank": rank, "leg": "总线", "essence": None,
                "verify_status": "unverified", "origin": "test"}

    def test_10_fragments_250_green(self):
        """B 榜历史基线：注入空 extra → 10 碎片 250 格零回退。"""
        frags = ml.load_fragments(extra_fragments=[])
        self.assertEqual(len(frags), 10)
        table = ml.build_meridian_table(frags)
        self.assertEqual(len(table), 250)
        self.assertTrue(ml.check_linkage(table=table, fragments=frags)["pass"])

    def test_live_table_fragments_x25(self):
        """实盘：格数 == 碎片数 × 25（公理是乘积，不是 250 这个实例值）。"""
        frags = ml.load_fragments()
        table = ml.build_meridian_table(frags)
        self.assertEqual(len(table), len(frags) * len(ml.KERNEL_MECHANISMS))
        self.assertTrue(ml.check_linkage(table=table, fragments=frags)["pass"])

    def test_11_fragments_275_green(self):
        frags = ml.load_fragments(extra_fragments=[self._extra("dna-test-a", 11)])
        self.assertEqual(len(frags), 11)
        table = ml.build_meridian_table(frags)
        self.assertEqual(len(table), 275)
        self.assertTrue(ml.check_linkage(table=table, fragments=frags)["pass"])

    def test_13_fragments_325_green(self):
        extras = [self._extra("dna-test-a", 11), self._extra("dna-test-b", 12),
                  self._extra("dna-test-c", 13)]
        frags = ml.load_fragments(extra_fragments=extras)
        table = ml.build_meridian_table(frags)
        self.assertEqual(len(table), 325)
        self.assertTrue(ml.check_linkage(table=table, fragments=frags)["pass"])

    def test_missing_cell_red(self):
        frags = ml.load_fragments(extra_fragments=[self._extra("dna-test-a", 11)])
        table = ml.build_meridian_table(frags)[:-1]
        self.assertFalse(ml.check_linkage(table=table, fragments=frags)["pass"])

    def test_extra_cell_red(self):
        frags = ml.load_fragments(extra_fragments=[self._extra("dna-test-a", 11)])
        table = ml.build_meridian_table(frags)
        ghost = {"repo": "ghost", "rank": 99, "mech": "A1", "mech_name": "全息",
                 "layer": "公理", "state": "pending-evidence", "evidence": []}
        self.assertFalse(ml.check_linkage(table=table + [ghost], fragments=frags)["pass"])

    def test_duplicate_repo_red(self):
        with self.assertRaises(ValueError):
            ml.load_fragments(extra_fragments=[self._extra("dup", 11),
                                              self._extra("dup", 12)])

    def test_summary_dynamic(self):
        s = ml.meridian_summary()
        frags = ml.load_fragments()
        self.assertEqual(s["fragments"], len(frags))
        self.assertEqual(s["cells"], len(frags) * len(ml.KERNEL_MECHANISMS))


class TestSpecUntouched(unittest.TestCase):
    def test_spec_sha256_matches_dna_master(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(ml.__file__)))
        with io.open(os.path.join(root, "holoaeon", "spec.py"), "rb") as fh:
            actual = hashlib.sha256(fh.read()).hexdigest()
        with io.open(os.path.join(root, "data", "genome_dna.json"), "r",
                    encoding="utf-8") as fh:
            master = json.load(fh)
        self.assertEqual(actual, master["genesis"]["spec_sha256_measured"])


if __name__ == "__main__":
    unittest.main()
