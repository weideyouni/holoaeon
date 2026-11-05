# -*- coding: utf-8 -*-
"""V31 泰坦进化模块测试（29 例）。

覆盖：公理/链上声明/11 机制/清单种子与持久化/缺口检索规格/许可证四级裁决/
确定性评分/排名过滤/提案生成/合入编排与缺环降级/去重/调度规格/inspect。
"""
import json
import os
import tempfile
import unittest

from holoaeon.machine_tool import SEAL
from holoaeon.titan_evolver import (ADOPTION_STEPS, AXIOMS, CAPABILITIES, CHAIN_POSITION,
                                    FETCH_SCOPE, LICENSE_BLACKLIST, MECHANISMS,
                                    SCHEMA_VERSION, SEED_CAPABILITIES,
                                    CapabilityManifest, adoption_plan, dedup_key,
                                    export_yaml, gap_queries, inspect, is_duplicate,
                                    license_verdict, propose, rank, schedule_spec, score)


def _manifest(tmpdir):
    path = os.path.join(tmpdir, "capability-manifest.json")
    manifest = CapabilityManifest.seed(path)
    assert manifest.save()["ok"]
    return CapabilityManifest.load(path)


def _candidate(**kwargs):
    base = {"repo": "acme/ocr-toolkit", "capability": "ocr.fallback_cpu",
            "name": "ocr-toolkit", "description": "CPU OCR chinese layout analysis",
            "license": "MIT", "stars": 1200, "readme": True, "tests": True,
            "entry": True, "topics": ["ocr"], "archived": False}
    base.update(kwargs)
    return base


class TestTitanEvolver(unittest.TestCase):
    def test_schema_and_seal(self):
        self.assertEqual(SCHEMA_VERSION, "TITAN-EVOLVER-v1.0")
        self.assertIn("潮起开门", SEAL)

    def test_axioms_two(self):
        self.assertEqual([a["id"] for a in AXIOMS], ["P01", "P02"])

    def test_chain_declares_no_new_ring(self):
        self.assertEqual(CHAIN_POSITION["ring"], 0)
        self.assertIn("不新增环", CHAIN_POSITION["name"])
        self.assertIn("mobius_vortex", CHAIN_POSITION["upstream"])
        self.assertIn("doc_anatomy", CHAIN_POSITION["upstream"])

    def test_capabilities_and_mechanisms(self):
        self.assertEqual(len(CAPABILITIES), 5)
        self.assertEqual(len(MECHANISMS), 11)
        ens = {m["en"] for m in MECHANISMS}
        self.assertIn("heartbeat", ens)
        self.assertIn("citystate", ens)

    def test_seed_covers_v24_to_v30(self):
        ids = {c["id"] for c in SEED_CAPABILITIES}
        for expected in ("swarm_intel.filter", "machine_tool.assemble",
                         "mobius_vortex.feedback", "klein_projection.assess",
                         "holo_forge.chain", "magic_lamp.compile", "doc_anatomy.parse"):
            self.assertIn(expected, ids)
        self.assertGreaterEqual(len(SEED_CAPABILITIES), 12)

    def test_manifest_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = _manifest(tmp)
            self.assertTrue(manifest.ready())
            self.assertEqual(len(manifest.items()), len(SEED_CAPABILITIES))
            summary = manifest.summary()
            self.assertEqual(summary["total"], len(SEED_CAPABILITIES))
            self.assertGreater(summary["with_gap"], 0)
            self.assertEqual(len(summary["digest"]), 16)

    def test_manifest_missing_file_is_not_ready(self):
        manifest = CapabilityManifest.load(os.path.join(tempfile.gettempdir(), "no_such_manifest.json"))
        self.assertFalse(manifest.ready())
        self.assertEqual(manifest.items(), [])

    def test_writeback_updates_status_and_impl(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = _manifest(tmp)
            result = manifest.writeback("collector.github_search", status="implemented",
                                        impl="scripts/titan_evolver_run.py (V31)",
                                        gap="仅采集不评分", note="V31 合入")
            self.assertTrue(result["ok"])
            cap = manifest.find("collector.github_search")
            self.assertEqual(cap["status"], "implemented")
            self.assertIn("titan_evolver_run", cap["impl"])
            self.assertIn("last_writeback", cap)

    def test_writeback_rejects_bad_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = _manifest(tmp)
            result = manifest.writeback("scheduler.task", status="done")
            self.assertFalse(result["ok"])

    def test_export_yaml_sections(self):
        with tempfile.TemporaryDirectory() as tmp:
            text = export_yaml(_manifest(tmp))
            for token in ("capabilities:", "fetch_scope:", "license_blacklist:",
                          "upgrade_path:", "ocr.fallback_cpu"):
                self.assertIn(token, text)
            self.assertNotIn("null:", text)

    def test_gap_queries_shape(self):
        with tempfile.TemporaryDirectory() as tmp:
            specs = gap_queries(_manifest(tmp))
            self.assertGreater(len(specs), 0)
            for spec in specs:
                self.assertTrue(spec["capability"])
                self.assertTrue(spec["keywords"])
                self.assertIn("执行层", spec["executed_by"])

    def test_gap_queries_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = _manifest(tmp)
            self.assertEqual(len(gap_queries(manifest, limit=2)), 2)

    def test_license_permissive_absorbs(self):
        v = license_verdict("MIT")
        self.assertEqual(v["class"], "permissive")
        self.assertTrue(v["allow"])
        self.assertEqual(license_verdict("Apache-2.0")["mode"], "absorb")

    def test_license_agpl_distill_only(self):
        v = license_verdict("AGPL-3.0")
        self.assertEqual(v["class"], "strong_copyleft")
        self.assertEqual(v["mode"], "distill_only")
        self.assertFalse(v["allow"])

    def test_license_sspl_hard_block(self):
        v = license_verdict("SSPL")
        self.assertEqual(v["class"], "hard_block")
        self.assertFalse(v["allow"])

    def test_license_unknown_review_only(self):
        v = license_verdict(None)
        self.assertEqual(v["class"], "unknown")
        self.assertEqual(v["mode"], "review_only")
        self.assertFalse(v["allow"])

    def test_score_is_deterministic(self):
        first = score(_candidate())
        second = score(_candidate())
        self.assertEqual(first["score"], second["score"])
        self.assertEqual(first["keyword_hits"], second["keyword_hits"])

    def test_score_keyword_hits_add_points(self):
        cap = {"id": "ocr.fallback_cpu",
               "upgrade_path": {"search": ["PaddleOCR", "CPU OCR chinese"]}}
        hit = score(_candidate(), cap)
        miss = score(_candidate(description="unrelated graphics library"), cap)
        self.assertEqual(len(hit["keyword_hits"]), 1)
        self.assertGreater(hit["score"], miss["score"])

    def test_score_archived_penalised(self):
        live = score(_candidate())
        dead = score(_candidate(archived=True))
        self.assertEqual(live["score"] - dead["score"], 1.0)

    def test_score_caps_at_ten(self):
        big = score(_candidate(stars=99999, description="PaddleOCR CPU OCR chinese"),
                    {"upgrade_path": {"search": ["PaddleOCR", "CPU OCR chinese"]}})
        self.assertLessEqual(big["score"], 10.0)

    def test_rank_filters_copyleft(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = _manifest(tmp)
            candidates = [_candidate(repo="acme/good", license="MIT"),
                          _candidate(repo="acme/agpl", license="AGPL-3.0")]
            ranked = rank(candidates, manifest)
            repos = [r["repo"] for r in ranked["selected"]]
            self.assertIn("acme/good", repos)
            self.assertNotIn("acme/agpl", repos)
            self.assertEqual(len(ranked["rejected"]), 1)

    def test_rank_threshold_filters_low_score(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = _manifest(tmp)
            ranked = rank([_candidate(stars=3, readme=False, tests=False, entry=False,
                                      description="nothing")], manifest, threshold=7.0)
            self.assertEqual(ranked["selected"], [])
            self.assertEqual(len(ranked["rejected"]), 1)

    def test_propose_markdown_has_sections(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = _manifest(tmp)
            result = propose([_candidate()], manifest, date="2026-11-05")
            self.assertTrue(result["ok"])
            for token in ("# UPGRADE_PROPOSAL", "## 一、候选总览", "## 二、逐条建议",
                          "## 四、审批", "approve:", "潮起开门"):
                self.assertIn(token, result["markdown"])
            self.assertEqual(len(result["digest"]), 16)

    def test_propose_rejects_when_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = propose([], _manifest(tmp))
            self.assertFalse(result["ok"])
            self.assertEqual(result["markdown"], "")

    def test_adoption_plan_steps_and_gates(self):
        plan = adoption_plan("doc_anatomy.parse", modules={m: True for m in
                                                           ("klein_projection", "holo_forge",
                                                            "machine_tool", "mobius_vortex")})
        self.assertTrue(plan["ok"])
        self.assertEqual(len(plan["steps"]), len(ADOPTION_STEPS))
        self.assertEqual(plan["steps"][0]["step"], "human_approve")
        self.assertEqual(plan["steps"][-1]["step"], "manifest_writeback")
        self.assertTrue(all(step["available"] for step in plan["steps"]))
        self.assertFalse(plan["degraded"])

    def test_adoption_plan_degrades_without_modules(self):
        plan = adoption_plan("ocr.fallback_cpu", modules={})
        self.assertTrue(plan["degraded"])
        self.assertIn("klein_projection", plan["blocked_modules"])
        self.assertTrue(plan["steps"][0]["available"])
        self.assertTrue(plan["steps"][-1]["available"])

    def test_dedup_and_schedule(self):
        key = dedup_key("acme/repo", "abc123")
        self.assertIn("acme/repo", key)
        self.assertTrue(is_duplicate([key], "acme/repo", "abc123"))
        self.assertFalse(is_duplicate([key], "acme/repo", "def456"))
        jobs = {item["job"] for item in schedule_spec()}
        self.assertEqual(jobs, {"collect", "propose", "review"})

    def test_inspect_reports_baseline_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            info = inspect(_manifest(tmp))
            self.assertEqual(info["module"], "titan_evolver")
            self.assertEqual(info["version"], "V31")
            self.assertEqual(info["mechanisms"], 11)
            self.assertTrue(info["manifest_ready"])
            self.assertEqual(info["threshold"], 7.0)
            self.assertEqual(info["license_blacklist"], list(LICENSE_BLACKLIST))
            self.assertEqual(len(info["fetch_scope"]), len(FETCH_SCOPE))
            self.assertIn("ocr.fallback_cpu", info["gaps"])

    def test_cli_license_and_chain(self):
        from holoaeon.titan_evolver import main
        self.assertEqual(main(["license", "MIT"]), 0)
        self.assertEqual(main(["chain"]), 0)
        self.assertEqual(main(["axioms"]), 0)


if __name__ == "__main__":
    unittest.main()
