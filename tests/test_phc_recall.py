# -*- coding: utf-8 -*-
"""V42 公共卫生召回层测试。零依赖，确定性断言。"""
import unittest

from holoaeon import phc_recall as pr
from holoaeon import phc_chronic_engine as pe


def _seed(index):
    rows = [
        {"id": "d1", "kind": "disease", "system": "cardio_cerebro",
         "text": "冠心病 心绞痛 胸闷 心悸 心前区不适 劳累后加重",
         "meta": {"level": "C类地方扩围"}},
        {"id": "d2", "kind": "disease", "system": "cardio_cerebro",
         "text": "脑卒中后遗症 偏瘫 言语不利 肢体麻木 康复训练",
         "meta": {}},
        {"id": "d3", "kind": "disease", "system": "ortho",
         "text": "腰椎间盘突出 腰痛 下肢放射痛 功能训练",
         "meta": {}},
        {"id": "s1", "kind": "syndrome", "system": "cardio_cerebro",
         "text": "胸痹 气阴两虚 痰湿内阻 心血瘀阻 证候",
         "meta": {}},
        {"id": "r1", "kind": "rehab", "system": "cardio_cerebro",
         "text": "运动处方 有氧训练 心肺康复 功能训练 循序渐进",
         "meta": {}},
        {"id": "f1", "kind": "redflag", "system": "cardio_cerebro",
         "text": "持续剧烈胸痛 大汗 濒死感 急性心肌梗死征象",
         "meta": {}},
        {"id": "i1", "kind": "insurance", "system": "phc_a",
         "text": "阿司匹林 肠溶片 国家医保目录 甲类",
         "meta": {"year": 2025}},
    ]
    for r in rows:
        index.add(r)
    return index


class TestPhcRecall(unittest.TestCase):
    def test_chain_position(self):
        self.assertEqual(pr.CHAIN_POSITION["ring"], 11)
        self.assertEqual(pr.CHAIN_POSITION["layer"], "recall（附属召回层）")
        self.assertIn("hypervector", pr.CHAIN_POSITION["upstream"])

    def test_seal(self):
        self.assertEqual(pr.SEAL, "潮起开门，潮落闭嘴")

    def test_item_kinds_seven(self):
        self.assertEqual(len(pr.ITEM_KINDS), 7)
        self.assertIn("redflag", pr.ITEM_KINDS)
        self.assertIn("insurance", pr.ITEM_KINDS)

    def test_shards_align_with_v41_atlas(self):
        for s in ("nervous", "cardio_cerebro", "endocrine", "immune",
                  "malignancy", "ortho"):
            self.assertIn(s, pr.SHARDS)
            self.assertIn(s, pe.SIX_SYSTEM_ATLAS)

    def test_validate_item(self):
        self.assertTrue(pr.validate_item(
            {"id": "x", "kind": "disease", "system": "ortho",
             "text": "颈椎病"})["ok"])
        self.assertFalse(pr.validate_item(
            {"id": "x", "kind": "bad", "system": "ortho",
             "text": "颈椎病"})["ok"])
        self.assertFalse(pr.validate_item(
            {"id": "x", "kind": "disease", "system": "bad",
             "text": "颈椎病"})["ok"])
        self.assertFalse(pr.validate_item(
            {"id": "x", "kind": "disease", "system": "ortho",
             "text": "  "})["ok"])

    def test_embed_deterministic(self):
        idx = pr.ShardIndex(dim=256)
        a1 = pr.embed(idx.space, "气阴两虚")
        a2 = pr.embed(idx.space, "气阴两虚")
        self.assertEqual(a1, a2)
        b = pr.embed(idx.space, "痰湿内阻")
        self.assertNotEqual(a1, b)
        self.assertEqual(len(a1), 256)

    def test_add_precomputes(self):
        idx = _seed(pr.ShardIndex(dim=256))
        self.assertEqual(len(idx.vecs), 7)
        r = idx.add({"id": "d1", "kind": "disease",
                     "system": "cardio_cerebro", "text": "重复add覆盖"})
        self.assertTrue(r["ok"])
        self.assertTrue(r["precomputed"])

    def test_recall_semantic_ranking(self):
        idx = _seed(pr.ShardIndex(dim=256))
        r = idx.search("患者胸闷心悸 心前区不适", top_k=3)
        top_ids = [h["id"] for h in r["hits"]]
        self.assertIn("d1", top_ids)
        self.assertNotEqual(top_ids[0], "d3")  # 骨伤不该排第一

    def test_structured_filter_kind(self):
        idx = _seed(pr.ShardIndex(dim=256))
        r = idx.search("胸痛", kind="redflag")
        self.assertEqual({h["kind"] for h in r["hits"]}, {"redflag"})

    def test_structured_filter_system(self):
        idx = _seed(pr.ShardIndex(dim=256))
        r = idx.search("康复 训练", system="ortho", top_k=5)
        self.assertEqual({h["system"] for h in r["hits"]}, {"ortho"})

    def test_top_k_respected(self):
        idx = _seed(pr.ShardIndex(dim=256))
        r = idx.search("慢病 康复 管理", top_k=2)
        self.assertLessEqual(len(r["hits"]), 2)

    def test_empty_index_graceful(self):
        idx = pr.ShardIndex(dim=256)
        r = idx.search("任何查询")
        self.assertTrue(r["ok"])
        self.assertEqual(r["hits"], [])

    def test_rule_gate_redflag(self):
        idx = _seed(pr.ShardIndex(dim=256))
        r = idx.search("剧烈胸痛 大汗", kind=None, top_k=7)
        g = pr.RuleGate.check(r["hits"])
        self.assertIn("f1", g["redflag"])
        self.assertIn("转诊", g["action"])
        self.assertTrue(g["zero_prescription"])

    def test_rule_gate_clean(self):
        g = pr.RuleGate.check([{"id": "d1", "kind": "disease",
                                "system": "cardio_cerebro", "text": "x",
                                "meta": {}}])
        self.assertEqual(g["redflag"], [])
        self.assertIn("无红旗", g["action"])

    def test_sync_ledger(self):
        led = pr.SyncLedger()
        led.record("国家医保目录", "2025版", "2026-01-01")
        m = led.manifest()
        self.assertEqual(m["records"][0]["version"], "2025版")
        self.assertIn("只更新索引", m["policy"])

    def test_pipeline_end_to_end(self):
        idx = _seed(pr.ShardIndex(dim=256))
        r = pr.recall_pipeline(idx, "胸口持续剧痛 出汗", top_k=7)
        self.assertTrue(r["ok"])
        self.assertTrue(r["candidates"])
        self.assertIn("执业医师终审", r["decision"])
        self.assertIn("非诊断非处方", r["disclaimer"])
        self.assertTrue(r["rule_gate"]["zero_prescription"])
        for c in r["candidates"]:
            self.assertIn("text", c)  # 可解释：带来源引用

    def test_pipeline_zero_prescription_fields(self):
        idx = _seed(pr.ShardIndex(dim=256))
        r = pr.recall_pipeline(idx, "高血压 用药", top_k=7)
        blob = str(r).lower()
        self.assertNotIn("dose", blob)
        self.assertNotIn("prescription:", blob)

    def test_audit_snapshot(self):
        s = pr.audit()
        self.assertTrue(s["zero_network"])
        self.assertTrue(s["zero_prescription"])
        self.assertFalse(s["neural"])
        self.assertIn("零新依赖", s["zero_dependency"])


if __name__ == "__main__":
    unittest.main()
