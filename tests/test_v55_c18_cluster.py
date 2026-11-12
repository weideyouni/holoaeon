# -*- coding: utf-8 -*-
"""V55 测试：C18 仓库集群基座件（四人组扬弃裁决的可测子集）。

七组真 unittest（V50 纪律）：
  组1 TestNumbering     18 仓注册表穷举
  组2 TestWuxing        五行生克五档穷举（含 V55 补全"被生"方向）
  组3 TestCoupling      19×19 耦合矩阵（对称/锚定/枢纽）
  组4 TestEdgeSchema    边 Schema 四类与硬约束
  组5 TestReuseMap      知己知彼表（素材概念→在仓真实模块）
  组6 TestClusterTensor 集群张量（确定性/分化度）
  组7 TestGate          总闸与 CLI 等价

运行：cd .tmp_v55 && python -m unittest tests.test_v55_c18_cluster -v
"""
import json
import os
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holoaeon.c18_cluster import (  # noqa: E402
    AFFINITY, C18_NUMBERING, ClusterGate, ClusterTensor, CouplingMatrix,
    EDGE_REQUIRED_FIELDS, EDGE_TYPES, GITHUB_ORG, HUB_IDS, KE, N19_REPO,
    PHASES, PHASE_GAIN, REUSE_MAP, SHENG, fingerprint, phase_affinity,
    phase_relation, probe, validate_edge)


class TestNumbering(unittest.TestCase):
    """组1：18 仓注册表。"""

    def test_count_18(self):
        self.assertEqual(len(C18_NUMBERING), 18)

    def test_ids_sequential(self):
        self.assertEqual([c["id"] for c in C18_NUMBERING],
                         ["C%02d" % i for i in range(1, 19)])

    def test_fields_complete(self):
        for c in C18_NUMBERING:
            for f in ("id", "repo", "domain", "question", "phase_main",
                      "phase_sub", "role", "turtle", "horse"):
                self.assertTrue(c.get(f), "%s 缺字段 %s" % (c["id"], f))

    def test_repo_names_unique(self):
        repos = [c["repo"] for c in C18_NUMBERING]
        self.assertEqual(len(set(repos)), 18)
        for r in repos:
            self.assertTrue(r.startswith("holoaeon-c"))

    def test_domain_unique(self):
        domains = [c["domain"] for c in C18_NUMBERING]
        self.assertEqual(len(set(domains)), 18)

    def test_github_org_and_n19(self):
        self.assertEqual(GITHUB_ORG, "weideyouni")
        self.assertEqual(N19_REPO, "holoaeon")

    def test_turtle_horse_split(self):
        for c in C18_NUMBERING:
            # 神龟=保存/记录基线族（素材原文两词并用）
            self.assertTrue("保存" in c["turtle"] or "记录" in c["turtle"],
                            "%s 神龟职责非基线族" % c["id"])
            # 神马=推演/生成路径族
            self.assertTrue("推演" in c["horse"] or "生成" in c["horse"],
                            "%s 神马职责非路径族" % c["id"])


class TestWuxing(unittest.TestCase):
    """组2：五行生克五档（含 V55 补全被生方向——显式声明）。"""

    def test_sheng_ring(self):
        self.assertEqual(SHENG, {"木": "火", "火": "土", "土": "金",
                                 "金": "水", "水": "木"})

    def test_ke_ring(self):
        self.assertEqual(KE, {"木": "土", "土": "水", "水": "火",
                              "火": "金", "金": "木"})

    def test_relation_exhaustive_no_unknown(self):
        # 穷举 25 对（含同气）无"无关"——生克环全覆盖
        for a in PHASES:
            for b in PHASES:
                self.assertNotEqual(phase_relation(a, b), "无关",
                                    "%s→%s 无关" % (a, b))

    def test_relation_directions(self):
        self.assertEqual(phase_relation("木", "火"), "相生")
        self.assertEqual(phase_relation("火", "木"), "被生")   # V55 补全档
        self.assertEqual(phase_relation("水", "火"), "相克")
        self.assertEqual(phase_relation("火", "水"), "反克")
        self.assertEqual(phase_relation("土", "土"), "同气")
        self.assertEqual(phase_relation("枢纽", "水"), "枢纽")

    def test_gain_five_tiers(self):
        self.assertEqual(set(PHASE_GAIN),
                         {"相生", "被生", "同气", "相克", "反克"})
        self.assertEqual(PHASE_GAIN["被生"], PHASE_GAIN["相生"])

    def test_affinity_symmetric(self):
        for a in PHASES:
            for b in PHASES:
                self.assertEqual(phase_affinity(a, b), phase_affinity(b, a))

    def test_hub_ids(self):
        self.assertEqual(set(HUB_IDS), {"C03", "C11", "C18"})

    def test_phase_distribution(self):
        mains = [c["phase_main"] for c in C18_NUMBERING]
        for p in PHASES:
            self.assertEqual(sum(1 for m in mains if m == p), 3, p)
        self.assertEqual(sum(1 for m in mains if m not in PHASES), 3)


class TestCoupling(unittest.TestCase):
    """组3：19×19 耦合矩阵（无向亲和——工程裁决）。"""

    @classmethod
    def setUpClass(cls):
        cls.cm = CouplingMatrix()

    def test_size_19(self):
        m = self.cm.matrix()
        self.assertEqual(len(m), 19)
        self.assertTrue(all(len(row) == 19 for row in m.values()))

    def test_ids_domain(self):
        self.assertEqual(set(self.cm.ids),
                         {"C%02d" % i for i in range(1, 19)} | {"N19"})

    def test_diagonal_zero(self):
        m = self.cm.matrix()
        for a in self.cm.ids:
            self.assertEqual(m[a][a], 0.0)

    def test_symmetric(self):
        m = self.cm.matrix()
        for a in self.cm.ids:
            for b in self.cm.ids:
                self.assertEqual(m[a][b], m[b][a],
                                 "(%s,%s) 非对称" % (a, b))

    def test_n19_anchor_all_connected(self):
        m = self.cm.matrix()
        for b in self.cm.ids:
            if b != "N19":
                self.assertEqual(m["N19"][b], 1.0)
                self.assertEqual(m[b]["N19"], 1.0)

    def test_hub_rows(self):
        m = self.cm.matrix()
        for h in HUB_IDS:
            for b in self.cm.ids:
                if b != h and b != "N19":
                    self.assertEqual(m[h][b], AFFINITY["枢纽"])

    def test_sheng_pair_value(self):
        # 木火对（相生）= 0.8
        self.assertEqual(self.cm.value("C05", "C06"), AFFINITY["生"])

    def test_ke_pair_value(self):
        # 水火对（相克）= 0.4
        self.assertEqual(self.cm.value("C02", "C10"), AFFINITY["克"])

    def test_same_phase_value(self):
        # 土土（C01/C04 同主相）= 0.6
        self.assertEqual(self.cm.value("C01", "C04"), AFFINITY["同"])

    def test_validate_ok(self):
        v = self.cm.validate()
        self.assertTrue(v["ok"], v["problems"])


class TestEdgeSchema(unittest.TestCase):
    """组4：边 Schema（素材字段口径——缺字段非法）。"""

    def _good(self):
        return {"edge_id": "e_000001", "source": "C02", "target": "C10",
                "edge_type": "resonance", "layer": "L2",
                "phase_relation": "水克火", "resonance_strength": 0.87,
                "turtle_state": "baseline_locked",
                "horse_state": "pathway_exploring", "ttl_ticks": 12,
                "decay_rate": 0.85, "rollback_token": "rb_v55_0001"}

    def test_good_edge_passes(self):
        self.assertTrue(validate_edge(self._good())["ok"])

    def test_four_types(self):
        self.assertEqual(set(EDGE_TYPES),
                         {"skeleton", "resonance", "semantic", "event"})

    def test_bad_type_rejected(self):
        r = validate_edge(dict(self._good(), edge_type="magic"))
        self.assertFalse(r["ok"])

    def test_missing_field_rejected(self):
        for f in EDGE_REQUIRED_FIELDS:
            e = dict(self._good())
            e.pop(f)
            r = validate_edge(e)
            self.assertFalse(r["ok"], "缺 %s 未报" % f)

    def test_ttl_hard_constraint(self):
        r = validate_edge(dict(self._good(), ttl_ticks=6))
        self.assertFalse(r["ok"])

    def test_decay_bounds(self):
        for bad in (0.0, 1.0, 1.5, -0.1):
            r = validate_edge(dict(self._good(), decay_rate=bad))
            self.assertFalse(r["ok"], "decay=%r 未报" % bad)

    def test_rollback_required(self):
        r = validate_edge(dict(self._good(), rollback_token=""))
        self.assertFalse(r["ok"])

    def test_endpoint_domain(self):
        r = validate_edge(dict(self._good(), source="C99"))
        self.assertFalse(r["ok"])
        r2 = validate_edge(dict(self._good(), target="D01"))
        self.assertFalse(r2["ok"])


class TestReuseMap(unittest.TestCase):
    """组5：知己知彼表——素材要"新建"的机制在 N19 的真实落点。"""

    def test_twelve_entries(self):
        self.assertEqual(len(REUSE_MAP), 12)

    def test_all_point_to_real_modules(self):
        # 表中每个在仓模块名真实存在（import 验证——非纸面虚构）
        import importlib
        mods = {"butler_os": "holoaeon.butler_os", "bus": "holoaeon.bus",
                "fusion_upgrade": "holoaeon.fusion_upgrade",
                "concept_anatomy": "holoaeon.concept_anatomy",
                "dehallucination": "holoaeon.dehallucination",
                "craft_gate": "holoaeon.craft_gate",
                "mobius_vortex": "holoaeon.mobius_vortex",
                "klein_projection": "holoaeon.klein_projection",
                "semvec": "holoaeon.semvec",
                "event_channel": "holoaeon.event_channel",
                "hypervector": "holoaeon.hypervector"}
        for name, path in mods.items():
            try:
                importlib.import_module(path)
            except ImportError:
                self.fail("REUSE_MAP 引用模块不存在: %s" % name)

    def test_no_fabricated_numbers(self):
        # 扬弃实录：78 梅塔特隆边/108641 共振带索引不入 REUSE_MAP（虚构弃）
        for v in REUSE_MAP.values():
            self.assertNotIn("78", v)
            self.assertNotIn("108641", v)

    def test_grep_evidence_words(self):
        # 关键词映射真实语义（心跳/经络/卡尔曼/贝叶斯/布赫场…）
        for k in ("心跳调度", "经络传导", "卡尔曼滤波", "贝叶斯反演",
                  "布赫场", "莫比乌斯翻转", "克莱因收敛", "语义通信",
                  "事件总线", "升级契约", "张量载体"):
            self.assertIn(k, REUSE_MAP)


class TestClusterTensor(unittest.TestCase):
    """组6：集群张量（张量耦合不变——V52/V53/V54 同族）。"""

    @classmethod
    def setUpClass(cls):
        cls.ct = ClusterTensor()

    def test_encode_deterministic(self):
        c = C18_NUMBERING[0]
        a = self.ct.encode_cang(c)
        b = self.ct.encode_cang(c)
        self.assertEqual([round(x, 9) for x in a], [round(x, 9) for x in b])

    def test_encode_all_18(self):
        vecs = self.ct.encode_all()
        self.assertEqual(len(vecs), 18)
        dim = self.ct.space.dim
        self.assertTrue(all(len(v) == dim for v in vecs.values()))

    def test_similarity_symmetric_range(self):
        a, b = C18_NUMBERING[0], C18_NUMBERING[1]
        s1 = self.ct.similarity(a, b)
        s2 = self.ct.similarity(b, a)
        self.assertEqual(s1, s2)
        self.assertTrue(-1.0 <= s1 <= 1.0)

    def test_diversity_s5(self):
        # S5 反向指标（素材口径）：两两 cosine 均值 ≤0.70——同构不同质
        vecs = self.ct.encode_all()
        ids = list(vecs)
        sims = [self.ct.space.cosine(vecs[ids[i]], vecs[ids[j]])
                for i in range(len(ids)) for j in range(i + 1, len(ids))]
        mean = sum(sims) / len(sims)
        self.assertLessEqual(mean, 0.70)
        self.assertGreater(mean, 0.0)     # 非正交死系统（有共通基因）


class TestGate(unittest.TestCase):
    """组7：总闸。"""

    @classmethod
    def setUpClass(cls):
        cls.g = ClusterGate()

    def test_self_check_all_green(self):
        sc = self.g.self_check()
        self.assertTrue(sc["ok"], json.dumps(sc, ensure_ascii=False)[:400])
        for k in ("numbering", "phases", "matrix", "edge_schema", "diversity"):
            self.assertIn(k, sc["checks"])
            self.assertTrue(sc["checks"][k]["ok"], k)

    def test_repo_urls_19(self):
        urls = self.g.repo_urls()
        self.assertEqual(len(urls), 19)
        self.assertIn("N19", urls)
        self.assertTrue(urls["C01"].endswith("holoaeon-c01-source"))

    def test_probe_module_fn(self):
        p = probe()
        self.assertTrue(p["ok"])
        self.assertEqual(p["cang_count"], 18)

    def test_fingerprint(self):
        fp = fingerprint()
        self.assertEqual(fp["module"], "c18_cluster")
        self.assertEqual(fp["ring"], 19)
        self.assertEqual(fp["seal"], "潮起开门，潮落闭嘴")

    def test_cli_probe_exit0(self):
        r = subprocess.run(
            [sys.executable, "-m", "holoaeon.c18_cluster", "probe"],
            capture_output=True, text=True, cwd=os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))))
        self.assertEqual(r.returncode, 0, r.stderr)
        out = json.loads(r.stdout)
        self.assertTrue(out["ok"])

    def test_cli_fingerprint(self):
        r = subprocess.run(
            [sys.executable, "-m", "holoaeon.c18_cluster", "fingerprint"],
            capture_output=True, text=True, cwd=os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)["module"], "c18_cluster")


if __name__ == "__main__":
    unittest.main()
