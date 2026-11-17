# -*- coding: utf-8 -*-
"""V87-A 单测：蜕皮合法化（change_class 分治）/ G-DNA-04 / 第九面 unity /
凭据排除可执行断言（G10）/ 投喂包漂移侧账（G11）/ CTUP 落点登记（G9）。

纪律：纯标准库 / 零网络 / 确定性 / 先红后绿；不写仓外真实文件。
"""
import hashlib
import io
import json
import os
import tempfile
import unittest

from holoaeon import genome_dna as gd

import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "scripts"))
import credential_exclusion_check as ce  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
TRUE_H = {"mechanism_axis": True, "heartbeat": True, "seal": True}


def _load(name):
    with io.open(os.path.join(DATA, name), "r", encoding="utf-8") as fh:
        return json.load(fh)


def _sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(65536), b""):
            h.update(c)
    return h.hexdigest()


class TestGeneRevision(unittest.TestCase):
    def test_dna_version_1_1_0(self):
        self.assertEqual(gd.DNA_VERSION, "1.1.0")
        self.assertEqual(_load("genome_dna.json")["dna_version"], "1.1.0")

    def test_four_axioms_with_unity(self):
        master = _load("genome_dna.json")
        self.assertEqual(len(master["axioms"]), 4)
        self.assertEqual([a["id"] for a in master["axioms"]],
                         ["G-DNA-01", "G-DNA-02", "G-DNA-03", "G-DNA-04"])
        self.assertEqual([a["id"] for a in gd.AXIOMS],
                         [a["id"] for a in master["axioms"]])

    def test_axiom03_formal_has_change_class(self):
        formal = [a for a in gd.AXIOMS if a["id"] == "G-DNA-03"][0]["formal"]
        self.assertIn("extension", formal)
        self.assertIn("governance", formal)
        self.assertIn("spec_sha_backfilled", formal)
        fals = [a for a in gd.AXIOMS if a["id"] == "G-DNA-03"][0]["falsifiers"]
        self.assertIn("bad_change_class", fals)
        self.assertIn("gov_without_backfill", fals)

    def test_genome_hash_revision_registered(self):
        master = _load("genome_dna.json")
        rev = master["genome_revision"]
        self.assertEqual(rev["after"], gd.genome_hash())
        self.assertEqual(len(rev["before"]), 64)
        self.assertNotEqual(rev["before"], rev["after"])

    def test_receipt_head_policy_present(self):
        pol = _load("genome_dna.json")["policy"]["receipt_head"]
        self.assertIn("回执 head", pol["rule"])
        self.assertIn("把「头不同」误报为漏回填", pol["forbidden"])

    def test_unity_nodes_quad(self):
        loci = _load("genome_dna.json")["loci"]["unity_nodes"]
        self.assertEqual(sorted(loci), ["coordinate", "credential", "readback", "state"])
        self.assertEqual(sorted(gd.LOCI["unity_nodes"]), ["coordinate", "credential",
                                                         "readback", "state"])


class TestMoltSplit(unittest.TestCase):
    def test_extension_requires_spec_identical(self):
        self.assertTrue(gd.robustness_check(True, True, True, True, 300, 300,
                                            TRUE_H)["pass"])
        self.assertFalse(gd.robustness_check(True, True, False, True, 300, 300,
                                             TRUE_H)["pass"])

    def test_governance_needs_trio(self):
        ok = gd.robustness_check(True, True, False, True, 300, 300, TRUE_H,
                                 "governance", True, True)
        self.assertTrue(ok["pass"], ok["problems"])
        for args in ((False, True), (True, False), (False, False)):
            self.assertFalse(gd.robustness_check(True, True, False, True, 300, 300,
                                                 TRUE_H, "governance", *args)["pass"])

    def test_governance_keeps_gene_conserved(self):
        """脱表型不脱基因：governance 下 genome_hash 漂移仍必红。"""
        self.assertFalse(gd.robustness_check(True, True, False, False, 300, 300,
                                             TRUE_H, "governance", True, True)["pass"])

    def test_illegal_change_class(self):
        self.assertFalse(gd.robustness_check(True, True, True, True, 300, 300,
                                             TRUE_H, "molt")["pass"])
        self.assertIn("change_class 非法", gd.robustness_check(
            True, True, True, True, 300, 300, TRUE_H, "molt")["problems"][0])


class TestUnityFace(unittest.TestCase):
    def test_nine_faces_and_contracts_synced(self):
        self.assertEqual(len(gd.PLUGIN_FACES), 9)
        c = _load("plugin_contract.json")
        self.assertEqual(c["faces"], 9)
        for item in c["contracts"]:
            self.assertIn("unity", item)
            self.assertEqual(item["unity"]["ctup_schema"], "CTUP-v1.0")

    def test_unity_four_nodes_independent_red(self):
        coord = {"head": "c461b51", "schema_same": True, "head_mismatch": False}
        state = {"receipt_present": True, "anchor_present": True,
                 "stage": "closed_execution_side"}
        cred = {"pointer": "holoaeon_memory/credential_registry.json", "status": "VALID"}
        read = {"evidence": "S1/S2/S3 同头 c461b51"}
        self.assertTrue(gd.unity_check(coord, state, cred, read)["pass"])
        self.assertFalse(gd.unity_check({}, state, cred, read)["pass"])
        self.assertFalse(gd.unity_check(coord, {"receipt_present": False},
                                        cred, read)["pass"])
        self.assertFalse(gd.unity_check(coord, state, {"status": "INVALID"},
                                        read)["pass"])
        self.assertFalse(gd.unity_check(coord, state, cred, {"evidence": "ok"})["pass"])

    def test_verify_counts(self):
        v = gd.verify()
        self.assertTrue(v["pass"], v["problems"])
        self.assertEqual(v["axioms"], 4)
        self.assertEqual(v["guards"], 5)


class TestCredentialExclusion(unittest.TestCase):
    def test_gitignore_rules_present(self):
        self.assertTrue(ce.check_gitignore(os.path.join(ROOT, ".gitignore"))["pass"])

    def test_live_repo_zero_plaintext(self):
        out = ce.run(ROOT, manifests=[os.path.join(DATA, "genome_dna.json")])
        self.assertTrue(out["pass"], out["problems"])
        self.assertTrue(out["zero_plaintext"])

    def test_manifest_with_credential_path_red(self):
        tmp = tempfile.mkdtemp(prefix="v87cred_")
        p = os.path.join(tmp, "fake_manifest.json")
        payload = {"repo": {"holoaeon_memory/credential_registry.json": {"bytes": 4200}}}
        with io.open(p, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False)
        r = ce.check_manifest(p)
        self.assertFalse(r["pass"])
        self.assertEqual(r["hit_count"], 1)

    def test_tree_with_plaintext_red(self):
        tmp = tempfile.mkdtemp(prefix="v87plain_")
        p = os.path.join(tmp, "leak.py")
        token = "ghp_" + "Z" * 36
        with io.open(p, "w", encoding="utf-8") as fh:
            fh.write("TOKEN = '" + token + "'\n")
        r = ce.check_tree(tmp)
        self.assertFalse(r["pass"])
        self.assertEqual(r["hits"], 1)
        self.assertNotIn(token, json.dumps(r, ensure_ascii=False))


class TestFeedDeltaLedger(unittest.TestCase):
    def test_schema_and_append_only(self):
        reg = _load("feed_delta_registry.json")
        self.assertEqual(reg["schema"], "HOLOAEON-FEED-DELTA/1.0")
        self.assertTrue(reg["policy"]["append_only"])
        self.assertFalse(reg["policy"]["history_backfill"])

    def test_entries_match_live_bytes(self):
        reg = _load("feed_delta_registry.json")
        self.assertGreaterEqual(len(reg["entries"]), 3)
        for e in reg["entries"]:
            p = e["path_abs"]
            if not os.path.isfile(p):
                continue
            self.assertEqual(os.path.getsize(p), e["bytes"])
            self.assertEqual(_sha(p), e["sha256"])

    def test_lineage_note_keeps_evolution(self):
        reg = _load("feed_delta_registry.json")
        self.assertIn("演进", reg["lineage_note"])
        self.assertIn("not", json.dumps(reg["policy"], ensure_ascii=False).lower())


class TestCtupOnboarding(unittest.TestCase):
    def test_record_fields_complete(self):
        rec = _load("ctup_onboarding.json")
        self.assertEqual(rec["schema"], "HOLOAEON-CTUP-ONBOARDING/1.0")
        for k in ("skill_dir_abs", "skill_md", "unity_check_py", "readback"):
            self.assertIn(k, rec)
        self.assertTrue(rec["skill_md"]["path_abs"].replace("\\", "/")
                        .endswith("cross-thread-unity-protocol/SKILL.md"))
        self.assertTrue(rec["unity_check_py"]["path_abs"].replace("\\", "/")
                        .endswith("scripts/unity_check.py"))

    def test_sha256_matches_live_files(self):
        rec = _load("ctup_onboarding.json")
        for key in ("skill_md", "unity_check_py"):
            p = rec[key]["path_abs"]
            if not os.path.isfile(p):
                self.skipTest("CTUP 落点不在本机（跨机只校记录）")
            self.assertEqual(_sha(p), rec[key]["sha256"])

    def test_two_repos_unity_ok_recorded(self):
        rec = _load("ctup_onboarding.json")
        self.assertEqual(rec["readback"]["holoaeon"]["verdict"], "UNITY_OK")
        self.assertEqual(rec["readback"]["neike"]["verdict"], "UNITY_OK")


if __name__ == "__main__":
    unittest.main()
