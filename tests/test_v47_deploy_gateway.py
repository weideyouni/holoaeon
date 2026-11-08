# -*- coding: utf-8 -*-
"""V47 部署域闸门+现场网关测试。零依赖，确定性断言。"""
import importlib.util
import os
import sys
import tempfile
import unittest

from holoaeon import deploy_gate as dg


def _load_gateway():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(here, "bridges", "site_gateway.py")
    spec = importlib.util.spec_from_file_location("site_gateway", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


gw = _load_gateway()


class TestDeployGate(unittest.TestCase):
    def test_chain_ring15(self):
        self.assertEqual(dg.CHAIN_POSITION["ring"], 15)
        self.assertIn("部署域", dg.CHAIN_POSITION["name"])

    def test_seal(self):
        self.assertEqual(dg.SEAL, "潮起开门，潮落闭嘴")

    def test_deliberate_choice_declaration(self):
        dc = dg.DELIBERATE_CHOICE
        self.assertIn("sqlite-vec", dc["aligned_peers"])   # 对齐声明
        self.assertTrue(dc["differentiators"])             # 差异化声明
        self.assertIn("domain_note", dc)                    # 域分离声明

    def test_capacity_profile_3to4w(self):
        cp = dg.CAPACITY_PROFILE
        self.assertEqual(cp["population_range"], (30000, 40000))
        self.assertEqual(cp["terminals_default"], 10)
        self.assertEqual(cp["terminals_reserved"], 30)

    def test_capacity_plan_in_range(self):
        r = dg.capacity_plan(35000)
        self.assertTrue(r["ok"])
        self.assertEqual(r["adults_35plus"], 19250)

    def test_capacity_plan_out_of_range(self):
        self.assertFalse(dg.capacity_plan(50000)["ok"])

    def test_vector_store_add_search(self):
        vs = dg.VectorStore(dim=256)
        vs.add("k1", "高血压患者应定期测量血压")
        r = vs.search("高血压 测量", top_k=1)
        self.assertEqual(r["hits"][0]["id"], "k1")
        self.assertIsNotNone(r["latency_ms"])

    def test_vector_store_duplicate_rejected(self):
        vs = dg.VectorStore(dim=256)
        vs.add("k1", "文本")
        self.assertFalse(vs.add("k1", "文本")["ok"])

    def test_vector_store_persistence_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "vs.jsonl")
            vs = dg.VectorStore(dim=256, store_path=p)
            vs.add("a", "冠心病 胸闷", {"s": 1})
            vs.save()
            vs2 = dg.VectorStore(dim=256, store_path=p)
            r = vs2.load()
            self.assertEqual(r["loaded"], 1)
            hit = vs2.search("胸闷", top_k=1)["hits"][0]
            self.assertEqual(hit["id"], "a")   # 向量读回免重算，检索如常

    def test_vector_store_stats(self):
        vs = dg.VectorStore(dim=256)
        vs.add("a", "文本")
        s = vs.stats()
        self.assertEqual(s["entries"], 1)
        self.assertFalse(s["neural"])
        self.assertTrue(s["deterministic"])

    def test_memory_store_write_read(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "mem.jsonl")
            ms = dg.MemoryStore(path=p)
            ms.write("patient_001", "建档：高血压 A类")
            ms.write("patient_001", "第2次随访")
            r = ms.read("patient_001")
            self.assertEqual(len(r["records"]), 2)

    def test_terminal_pool_default10(self):
        tp = dg.TerminalPool()
        for i in range(10):
            self.assertTrue(tp.acquire("t%d" % i)["ok"])
        self.assertFalse(tp.acquire("t10")["ok"])

    def test_terminal_pool_expand_needs_approval(self):
        tp = dg.TerminalPool()
        self.assertFalse(tp.expand(20)["ok"])               # 无审批拒绝
        self.assertTrue(tp.expand(20, approved=True)["ok"])  # 审批通过
        self.assertFalse(tp.expand(31, approved=True)["ok"])  # 超 30 上限拒绝

    def test_audit_snapshot(self):
        s = dg.audit()
        self.assertTrue(s["zero_dependency"])
        self.assertTrue(s["offline"])
        self.assertFalse(s["neural"])


class TestSiteGateway(unittest.TestCase):
    def test_seal(self):
        self.assertEqual(gw.SEAL, "潮起开门，潮落闭嘴")

    def test_outbound_structurally_blocked(self):
        for req in ("上传患者数据", "POST /api", "sync"):
            self.assertEqual(gw.NetDiode.outbound(req)["verdict"], "BLOCK")
        self.assertEqual(gw.OUTBOUND_ALLOW, ())  # 出站白名单=空集

    def test_inbound_only_upgrade(self):
        self.assertEqual(gw.NetDiode.inbound("patient_data")["verdict"],
                         "BLOCK")
        sha = "a" * 64
        r = gw.NetDiode.inbound("upgrade_package", sha256=sha)
        self.assertEqual(r["verdict"], "BLOCK")  # 无审批仍拒
        ok = gw.NetDiode.inbound("upgrade_package", sha256=sha, approved=True)
        self.assertEqual(ok["verdict"], "ALLOW")
        self.assertEqual(ok["destination"], "staging/")

    def test_inbound_bad_sha(self):
        self.assertEqual(gw.NetDiode.inbound(
            "upgrade_package", sha256="xyz", approved=True)["verdict"],
            "BLOCK")

    def test_digest_of(self):
        self.assertEqual(len(gw.NetDiode.digest_of(b"pkg")), 64)

    def test_model_couple_from_discovery(self):
        fake = {"services": [{"backend": "ollama", "host": "127.0.0.1",
                              "port": 11434, "status": "up"}],
                "gguf_files": [], "packages": []}
        r = gw.ModelAutoCouple.couple(fake)
        self.assertTrue(r["coupled"])
        self.assertEqual(r["backend"], "ollama")
        self.assertEqual(r["endpoint"], "http://127.0.0.1:11434")

    def test_model_couple_priority(self):
        fake = {"services": [{"backend": "vllm", "host": "127.0.0.1",
                              "port": 8000, "status": "up"},
                             {"backend": "lmstudio", "host": "127.0.0.1",
                              "port": 1234, "status": "up"}],
                "gguf_files": [], "packages": []}
        self.assertEqual(gw.ModelAutoCouple.couple(fake)["backend"],
                         "lmstudio")  # 优先级 ollama>lmstudio>vllm

    def test_model_couple_fallback_gguf(self):
        fake = {"services": [], "gguf_files": [{"path": "m.gguf",
                                                "bytes": 1}],
                "packages": []}
        r = gw.ModelAutoCouple.couple(fake)
        self.assertEqual(r["backend"], "gguf_local")

    def test_model_couple_none_found(self):
        fake = {"services": [], "gguf_files": [], "packages": []}
        self.assertFalse(gw.ModelAutoCouple.couple(fake)["coupled"])

    def test_gateway_report_matrix(self):
        r = gw.gateway_report()
        self.assertIn("boundary", r["protocol_matrix"])
        self.assertTrue(any("不直连" in b
                            for b in r["protocol_matrix"]["boundary"]))
        self.assertIn("结构性零出站", r["outbound_note"])


if __name__ == "__main__":
    unittest.main()
