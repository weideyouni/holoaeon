# -*- coding: utf-8 -*-
"""HoloAeon 单元测试（unittest，标准库）。运行：
    python -m unittest discover -s tests -v
"""
from __future__ import annotations

import unittest

from holoaeon.agent import Agent
from holoaeon.bus import Bus
from holoaeon.cluster import Cluster
from holoaeon.envelope import Envelope
from holoaeon.graph import AdaptiveGraph, hex_points
from holoaeon.guard import Guard
from holoaeon.hypervector import HypervectorSpace
from holoaeon.kernel import Kernel
from holoaeon.memory import Memory
from holoaeon.model_adapter import ModelAdapter, ModelBackend
from holoaeon.packs import all_packs
from holoaeon.scheduler import Scheduler
from holoaeon.skill import SkillRegistry
from holoaeon.selftest import run_all


class TestEnvelope(unittest.TestCase):
    def test_roundtrip(self):
        e = Envelope.create("a", "b", "t", {"task": "x"})
        e2 = Envelope.from_dict(e.to_dict())
        self.assertEqual(e.message_id, e2.message_id)
        self.assertEqual(e.payload, e2.payload)

    def test_reply(self):
        e = Envelope.create("a", "b", "t", {"task": "x"})
        r = Envelope.reply(e, "b", {"ok": True})
        self.assertEqual(r.sender, "b")
        self.assertEqual(r.conversation, e.conversation)
        self.assertEqual(len(r.trace), 2)


class TestBus(unittest.TestCase):
    def test_pubsub(self):
        b = Bus()
        got = []
        b.subscribe("news", lambda env: got.append(env))
        b.publish("news", {"v": 1}, "src")
        self.assertEqual(len(got), 1)

    def test_address(self):
        b = Bus()
        b.register_address("x", lambda env: "acked")
        rep = b.send(Envelope.create("m", "x", "d", {}))
        self.assertTrue(rep[0]["ok"])
        self.assertEqual(rep[0]["out"], "acked")


class TestSkill(unittest.TestCase):
    def test_match(self):
        r = SkillRegistry()
        r.register_fn("summarize", lambda task: "s",
                      description="summarize text", tags=["summary"])
        m = r.match("please summarize this text")
        self.assertEqual(m[0][0], "summarize")


class TestMemory(unittest.TestCase):
    def test_consolidate(self):
        m = Memory()
        m.put("k", {"a": 1}, kind="working")
        m.consolidate()
        self.assertEqual(m.get("k")["a"], 1)


class TestAgent(unittest.TestCase):
    def test_run(self):
        r = SkillRegistry()
        r.register_fn("echo", lambda task: "echo:" + task,
                      description="echo text")
        a = Agent("ag", "role", r)
        res = a.run_task("echo hi")
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["output"], "echo:echo hi")


class TestScheduler(unittest.TestCase):
    def test_ticks(self):
        s = Scheduler()
        s.tick(); s.tick()
        self.assertEqual(s.health()["tick_count"], 2)
        self.assertEqual(s.health()["bodies"], 70)


class TestGuard(unittest.TestCase):
    def test_block(self):
        g = Guard()
        self.assertEqual(g.check_text("os.system('rm -rf')").action, "block")
        self.assertNotEqual(g.check_text("safe text").action, "block")


class TestGraph(unittest.TestCase):
    def test_geometry(self):
        pts = hex_points(2)
        self.assertEqual(len(pts), 19)

    def test_path(self):
        g = AdaptiveGraph(flow_edges=[(0, 1), (1, 2)])
        path, _ = g.shortest_path(0, 2)
        self.assertTrue(path)

    def test_hebb(self):
        g = AdaptiveGraph()
        rep = g.hebbian_step([0, 1])
        self.assertGreater(rep["strengthened"], 0)


class TestCluster(unittest.TestCase):
    def test_parallel(self):
        r = SkillRegistry()
        r.register_fn("work", lambda task: "w:" + task,
                      description="work task")
        agents = [Agent(f"a{i}", "role", r) for i in range(3)]
        rep = Cluster(agents).run(
            1, {f"a{i}": f"work task {i}" for i in range(3)})
        self.assertEqual(rep["ok"], 3)
        self.assertTrue(rep["consistent"])
        self.assertEqual(rep["faults"], 0)


class TestHypervector(unittest.TestCase):
    def test_hrr(self):
        hv = HypervectorSpace()
        a, b = hv.make("a"), hv.make("b")
        ab = hv.bind(a, b)
        self.assertLess(hv.cosine(ab, a), 0.2)
        self.assertGreater(hv.cosine(hv.unbind(ab, b), a), 0.5)


class TestModelAdapter(unittest.TestCase):
    def test_route(self):
        ma = ModelAdapter()
        ma.register_backend(ModelBackend("m1", "local", input_cost=0.0))
        ma.register_backend(ModelBackend("m2", "cloud",
                                         context_window=100000, input_cost=0.02))
        self.assertEqual(ma.route("x", strategy="cheapest"), "m1")
        self.assertEqual(ma.route("x", strategy="largest_context"), "m2")


class TestPacks(unittest.TestCase):
    def test_install_all(self):
        k = Kernel()
        agents = skills = 0
        for pack in all_packs():
            rep = pack.install(k)
            agents += len(rep["agents"]); skills += len(rep["skills"])
        self.assertEqual(agents, 25)
        self.assertEqual(skills, 47)

    def test_gaoyi_compile_and_run(self):
        from holoaeon.packs.gaoyi_pack import compile_nl, GaoyiVm
        p, meta = compile_nl("帮我做个大纲：人工智能")
        self.assertEqual(meta["intent"], "outline_gen")
        self.assertEqual(meta["agent"], "writing_planner")
        rep = GaoyiVm(Kernel()).run(p)
        self.assertTrue(rep["ok"])
        self.assertEqual(rep["matched"], "outline_gen")
        _, m2 = compile_nl("无意义的句子xyz哈哈")
        self.assertEqual(m2["intent"], "UNKNOWN")


class TestOptimization(unittest.TestCase):
    def test_golden(self):
        from holoaeon.packs.optimization import golden_section, _quad1d
        x, _ = golden_section(_quad1d, 0.0, 10.0)
        self.assertAlmostEqual(x, 3.0, places=4)

    def test_gradient(self):
        from holoaeon.packs.optimization import gradient_descent
        f = lambda x: (x[0] - 2) ** 2 + (x[1] + 1) ** 2
        x, _, ok = gradient_descent(f, [0.0, 0.0], lr=0.1)
        self.assertTrue(ok)
        self.assertAlmostEqual(x[0], 2.0, places=3)
        self.assertAlmostEqual(x[1], -1.0, places=3)

    def test_newton(self):
        from holoaeon.packs.optimization import newton_1d, _quad1d
        x, _, ok = newton_1d(_quad1d, 0.0)
        self.assertTrue(ok)
        self.assertAlmostEqual(x, 3.0, places=5)

    def test_conjugate(self):
        from holoaeon.packs.optimization import conjugate_gradient
        A = [[4.0, 1.0], [1.0, 3.0]]; b = [1.0, 2.0]
        x, _, ok = conjugate_gradient(A, b)
        self.assertTrue(ok)
        self.assertAlmostEqual(x[0], 1 / 11, places=5)
        self.assertAlmostEqual(x[1], 7 / 11, places=5)

    def test_simplex(self):
        from holoaeon.packs.optimization import simplex
        res = simplex([3.0, 2.0], [[2.0, 1.0], [1.0, 1.0]],
                      [100.0, 80.0])
        self.assertEqual(res["status"], "optimal")
        self.assertEqual(res["x"], [20.0, 60.0])
        self.assertEqual(res["objective"], 180.0)

    def test_penalty(self):
        from holoaeon.packs.optimization import penalty_method
        f = lambda x: (x[0] - 5) ** 2 + (x[1] - 5) ** 2
        x, _ = penalty_method(f, [lambda v: v[0] + v[1] - 6.0],
                              [0.0, 0.0])
        self.assertAlmostEqual(x[0], 3.0, places=1)
        self.assertAlmostEqual(x[1], 3.0, places=1)

    def test_genetic(self):
        from holoaeon.packs.optimization import genetic_algorithm
        res = genetic_algorithm(lambda v: v * v, 5, seed=42)
        self.assertEqual(res["best_decoded"], 31)
        self.assertEqual(res["best_value"], 961)


class TestSelfTest(unittest.TestCase):
    def test_all_pass(self):
        rep = run_all()
        self.assertTrue(rep["ok"], msg=str(rep["details"]))


class TestDeterminismU1(unittest.TestCase):
    """U1：Cluster 结果顺序确定性 + _fft 入参纯函数化（永久回归）。"""

    def _run_once(self, name: str) -> list:
        import random
        import time as _t

        r = SkillRegistry()

        def jittery(task: str, _name: str = name) -> str:
            _t.sleep(random.Random("20261030-" + _name).random() * 0.002)
            return "w:" + task

        r.register_fn("work", jittery, description="work task")
        agents = [Agent(f"a{i}", "role", r) for i in range(6)]
        rep = Cluster(agents).run(30, {f"a{i}": "work task" for i in range(6)})
        self.assertEqual(rep["faults"], 0)
        return [c.get("agent_id") for c in rep["results"]]

    def test_t_u1_a_result_order_stable(self):
        seqs = [self._run_once(str(i)) for i in range(3)]
        self.assertEqual(seqs[0], seqs[1])
        self.assertEqual(seqs[1], seqs[2])
        # 现行 run() 只在首轮投递任务（rounds 只影响 barrier 次数），故每 agent 一条记录
        self.assertEqual(len(seqs[0]), 6)

    def test_t_u1_a2_order_key_is_total_order(self):
        """纯函数级：同一 agent 的多条记录也必须稳定排序（线程测试覆盖不到这一层）。"""
        from holoaeon.cluster import _order_key
        recs = []
        for i in range(6):
            recs.append({"agent_id": f"a{i}", "status": "ok", "out": "x"})
            recs.append({"agent_id": f"a{i}", "status": "ok", "out": "y"})
        seqs = [list(map(_order_key, recs)) for _ in range(6)]
        shuffled = [sorted(recs, key=_order_key) for _ in range(6)]
        self.assertEqual(seqs[0], seqs[1])
        self.assertEqual([r["out"] for r in shuffled[0]],
                         [r["out"] for r in shuffled[5]])
        self.assertEqual(len({k for k in seqs[0]}), 12)

    def test_t_u1_b_fft_does_not_mutate_input(self):
        from holoaeon.hypervector import _fft
        v = [1 + 0j, 2 + 0j, 3 + 0j, 4 + 0j]
        before = list(v)
        _fft(v, False)
        self.assertEqual(v, before)
        _fft(v, True)
        self.assertEqual(v, before)


class TestMatchingU5(unittest.TestCase):
    """U5：字符 2-gram Dice 混合分（中文无分词 + 单词形变）。"""

    def test_cn_query_hits_by_char_overlap(self):
        r = SkillRegistry()
        r.register_fn("stats_clean", lambda t: "ok",
                      description="统计数据清洗与汇总", tags=["统计"])
        r.register_fn("weather", lambda t: "ok",
                      description="weather forecast lookup", tags=["weather"])
        self.assertEqual(r.match("统计销售额")[0][0], "stats_clean")

    def test_en_deformed_word_hits(self):
        r = SkillRegistry()
        r.register_fn("stats2", lambda t: "ok",
                      description="statistics summary for numbers")
        r.register_fn("weather2", lambda t: "ok",
                      description="weather forecast lookup")
        self.assertEqual(r.match("statistik")[0][0], "stats2")

    def test_matching_is_bit_identical_over_1000_runs(self):
        from holoaeon.skill import ngram_dice
        r = SkillRegistry()
        r.register_fn("a", lambda t: 1, description="统计数据清洗")
        r.register_fn("b", lambda t: 1, description="weather forecast")
        first = r.match("统计销售额数据")
        for _ in range(1000):
            self.assertEqual(r.match("统计销售额数据"), first)
        self.assertEqual(ngram_dice("statistik", "statistics"),
                         ngram_dice("statistik", "statistics"))


class TestUpliftU16(unittest.TestCase):
    """U1–U6 升级包：注册与维度不变 / n-gram 纯函数 / P1 门禁拒收。"""

    def test_pack_registered_without_dimension_change(self):
        from holoaeon.packs import EXTRA_PACK_ORDER, get_extra_pack
        from holoaeon.packs.uplift_pack import pack_summary
        # uplift 不许丢，且不得低于原基线 7 个扩展包；
        # 更多的扩展包（如 persona_quartet）只能旁挂，由各自专属测试守护。
        self.assertIn("uplift", EXTRA_PACK_ORDER)
        self.assertGreaterEqual(len(EXTRA_PACK_ORDER), 7)
        self.assertEqual(get_extra_pack("uplift").key, "uplift")
        s = pack_summary()
        self.assertEqual((s["skills"], s["workflows"], s["agents_created"]), (24, 7, 0))
        self.assertTrue(s["addressing_unchanged"])
        self.assertEqual((s["threads"], s["timers"], s["disk_writes"], s["deps"]),
                         (0, 0, 0, 0))
        self.assertFalse(s["network"])

    def test_ngram_dice_is_pure_and_repeatable(self):
        from holoaeon.packs.uplift_pack import skill_uplift_ngram_dice
        a = skill_uplift_ngram_dice({"query": "statistik", "text": "statistics"})
        b = skill_uplift_ngram_dice({"query": "statistik", "text": "statistics"})
        self.assertEqual(a, b)
        self.assertEqual(a["dice"], 0.82353)
        q, t = "统计销售额", "统计数据清洗"
        before = (q, t)
        skill_uplift_ngram_dice({"query": q, "text": t})
        self.assertEqual((q, t), before)      # 不修改入参（与 U1 的 _fft 同一条纪律）

    def test_p1_gate_rejects_budget_and_unknown(self):
        from holoaeon.packs.uplift_pack import skill_uplift_p1_gate
        ok = skill_uplift_p1_gate({"baseline": {"window_used": 8, "hit_rate": 0.5,
                                                "admitted": ["p1", "p2"]},
                                   "candidate": {"window_used": 8, "hit_rate": 0.5,
                                                 "admitted": ["p1", "p2"], "unknown_events": 0}})
        self.assertEqual(ok["verdict"], "PASS")
        bad = skill_uplift_p1_gate({"baseline": {"window_used": 8, "hit_rate": 0.6,
                                                 "admitted": ["p1"]},
                                    "candidate": {"window_used": 9, "hit_rate": 0.4,
                                                  "admitted": ["p2"], "unknown_events": 1}})
        self.assertEqual(bad["verdict"], "REJECT")
        self.assertFalse(bad["checks"]["budget_not_up"])
        self.assertFalse(bad["checks"]["zero_unknown"])
        self.assertEqual(bad["diff_bundle"],
                         ["diff_manifest", "diff_score", "diff_reason_codes"])


if __name__ == "__main__":
    unittest.main()
