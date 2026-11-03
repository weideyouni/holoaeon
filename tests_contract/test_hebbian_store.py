# -*- coding: utf-8 -*-
"""B6 · 赫布落盘 + 通道配额 · 旁挂单测（不并入主套 34 项）。

运行：python -m unittest discover -s tests_contract -v
"""
import csv
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from holoaeon.fusion_upgrade import hebbian_store as HS  # noqa: E402
from holoaeon.skill_matrix.mech import MECHANISMS, HebbianField  # noqa: E402

STORE = os.path.join(ROOT, "data", "hebbian_store.json")
QUOTA = os.path.join(ROOT, "data", "channel_quota.csv")
RESTART = os.path.join(ROOT, "reports", "b6_restart.json")


class HebbianStoreTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(STORE, "r", encoding="utf-8") as f:
            cls.doc = json.load(f)
        with open(QUOTA, "r", encoding="utf-8") as f:
            cls.quota = list(csv.DictReader(f))
        with open(RESTART, "r", encoding="utf-8") as f:
            cls.restart = json.load(f)

    def test_01_store_identity(self):
        self.assertEqual(self.doc["store_id"], "SG-B6-HEBBIAN-STORE-V1")
        self.assertEqual(self.doc["batch"], "B6")
        self.assertEqual(self.doc["evidence_class"], "simulated")

    def test_02_self_hash_recomputes(self):
        v = HS.verify(self.doc)
        self.assertTrue(v["hash_ok"])
        self.assertEqual(v["sha256"], v["recomputed"])

    def test_03_edges_sorted_and_bounded(self):
        keys = [(e["a"], e["b"]) for e in self.doc["edges"]]
        self.assertEqual(keys, sorted(keys))
        self.assertGreater(len(keys), 0)
        self.assertEqual(self.doc["edge_count"], len(keys))
        for e in self.doc["edges"]:
            self.assertGreater(e["w"], 0.0)
            self.assertLessEqual(e["w"], HS.CAP)
            self.assertEqual(round(e["w"], HS.ROUND), e["w"])

    def test_04_nodes_cover_edges(self):
        nodes = set(self.doc["nodes"])
        for e in self.doc["edges"]:
            self.assertIn(e["a"], nodes)
            self.assertIn(e["b"], nodes)
        self.assertEqual(self.doc["node_count"], len(nodes))

    def test_05_restore_roundtrip_topk_exact(self):
        f = HebbianField(HS.DECAY)
        HS.restore(self.doc, f)
        text = HS.topk_text(f, self.doc["topk"]["seeds"], self.doc["topk"]["k"])
        lines = []
        for row in self.doc["topk"]["rows"]:
            for nb in row["neighbors"]:
                lines.append("%s\t%s\t%.5f" % (row["seed"], nb["name"], nb["w"]))
            if not row["neighbors"]:
                lines.append("%s\t-\t0.00000" % row["seed"])
        self.assertEqual(text, "\n".join(lines))

    def test_06_seeds_include_all_mechanisms(self):
        seeds = set(self.doc["topk"]["seeds"])
        for m in MECHANISMS:
            self.assertIn(m, seeds)

    def test_07_quota_shape(self):
        self.assertEqual(len(self.quota), 17)
        self.assertEqual(sum(1 for r in self.quota if r["status"] == "mapped"), 12)
        self.assertEqual(sum(1 for r in self.quota if r["status"] == "pending"), 5)
        self.assertEqual(sum(int(r["quota"]) for r in self.quota), 1200)
        self.assertEqual(len({r["channel"] for r in self.quota}), 17)
        for r in self.quota:
            self.assertGreaterEqual(int(r["headroom"]), 0)

    def test_08_pending_channels_not_allocated(self):
        for r in self.quota:
            if r["status"] == "pending":
                self.assertEqual(int(r["quota"]), 0)
                self.assertIn(r["group"], ("神", "淋巴"))
                self.assertIn("待办", r["note"])

    def test_09_restart_report_pass(self):
        self.assertEqual(self.restart["verdict"], "PASS")
        self.assertTrue(self.restart["equal_live_vs_child"])
        self.assertTrue(self.restart["equal_frozen_vs_child"])
        self.assertNotEqual(self.restart["parent_pid"], self.restart["child_pid"])
        self.assertEqual(self.restart["store_sha256"], self.doc["sha256"])

    def test_10_no_new_pack(self):
        from holoaeon.packs import EXTRA_PACK_ORDER, PACK_ORDER
        from holoaeon import spec as SPEC
        self.assertEqual(len(PACK_ORDER), 9)
        # 批4 领域化解耦（AGENT_FEED_V8_BATCH2_4）：tcm_rehab 为投喂包预定的第 11 扩展包，
        # 只进 EXTRA_PACK_ORDER、不进 PACK_ORDER（25/47/9 维度锁不变）。
        # V11 topology_resonance → 12；V12 quartet_director → 13。
        # 扩展包登记按批次递增，契约只锁下界（防回退），不写死精确值（防每批过期）。
        self.assertGreaterEqual(len(EXTRA_PACK_ORDER), 11)
        self.assertEqual(SPEC.VERSION, "0.9.1")


if __name__ == "__main__":
    unittest.main()
