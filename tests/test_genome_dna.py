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

    def test_registry_empty_by_default(self):
        self.assertEqual(gd.registered_fragments(), [])


class TestMeridianDynamic(unittest.TestCase):
    def _extra(self, name, rank):
        return {"repo": name, "rank": rank, "leg": "总线", "essence": None,
                "verify_status": "unverified", "origin": "test"}

    def test_10_fragments_250_green(self):
        frags = ml.load_fragments()
        self.assertEqual(len(frags), 10)
        table = ml.build_meridian_table()
        self.assertEqual(len(table), 250)
        self.assertTrue(ml.check_linkage()["pass"])

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
        self.assertEqual(s["fragments"], 10)
        self.assertEqual(s["cells"], 250)


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
