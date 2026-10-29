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
        self.assertEqual(agents, 24)
        self.assertEqual(skills, 44)


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


if __name__ == "__main__":
    unittest.main()
