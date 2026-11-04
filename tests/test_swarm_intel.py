# -*- coding: utf-8 -*-
"""
V24 · 群体智能引擎（Swarm Intelligence）测试
================================================================================
覆盖投喂包 §5 步骤 6 的 8 条用例，并在并行模拟用例内追加「同种子双跑一致」
的确定性校验（本批对投喂稿的关键修正：弃内置 hash()，改 crc32）。

密令：潮起开门，潮落闭嘴。evidence_class=simulated，仿真≠证明，碳基终裁。
"""
from __future__ import annotations

import unittest

from holoaeon.swarm_intel import (
    DEFAULT_SEED,
    AgentAction,
    DeepInteractor,
    ParallelSimulator,
    PersonaArchitect,
    ReportSynthesizer,
    SeedToGraph,
    Stage,
    SwarmOrchestrator,
)
from holoaeon.packs.swarm_intel_pack import (
    MECHANISM_COVERAGE,
    SwarmIntelPack,
    get_manifest,
)


class TestSeedToGraph(unittest.TestCase):
    def test_seed_to_graph(self):
        """种子文本→图：节点/边非空，实体类型可枚举。"""
        g = SeedToGraph.build_graph(DEFAULT_SEED)
        self.assertGreater(g.node_count, 0)
        self.assertGreater(g.edge_count, 0)
        self.assertTrue(g.entity_types)
        self.assertTrue(g.graph_id.startswith("swarm_"))
        for node in g.nodes.values():
            self.assertEqual(len(node.uuid), 16)
            self.assertTrue(node.entity_type)


class TestPersonaSynthesize(unittest.TestCase):
    def test_persona_synthesize(self):
        """图→Persona：一实体一角色，字段齐全。"""
        g = SeedToGraph.build_graph(DEFAULT_SEED)
        profiles = PersonaArchitect.generate_batch(g)
        self.assertEqual(len(profiles), g.node_count)
        for p in profiles:
            self.assertTrue(p.bio and p.persona)
            self.assertIn(p.mbti, PersonaArchitect.MBTI_TYPES)
            self.assertTrue(p.interested_topics)


class TestParallelSimulate(unittest.TestCase):
    def test_parallel_simulate(self):
        """模拟 5 轮：轮数正确、验证路径全通过、双跑结果一致（确定性）。"""
        g = SeedToGraph.build_graph(DEFAULT_SEED)
        profiles = PersonaArchitect.generate_batch(g)

        sim = ParallelSimulator(profiles, total_rounds=5)
        sim.run()
        self.assertEqual(len(sim.rounds), 5)
        self.assertTrue(all(x["ok"] for x in sim.verification_log))
        self.assertEqual(len(sim.all_actions), len(profiles) * 5)

        # 确定性：同输入第二次运行，action_type 序列完全相同
        sim2 = ParallelSimulator(profiles, total_rounds=5)
        sim2.run()
        self.assertEqual([a.action_type for a in sim.all_actions],
                         [a.action_type for a in sim2.all_actions])
        # 每轮 action 顺序与 agent 顺序一致
        for r in sim.rounds:
            self.assertEqual([a.agent_id for a in r.actions], r.active_agents)


class TestReportGenerate(unittest.TestCase):
    def test_report_generate(self):
        """报告：summary / 分布 / 意见领袖 / 趋势 / 涌现信号 结构完整。"""
        g = SeedToGraph.build_graph(DEFAULT_SEED)
        profiles = PersonaArchitect.generate_batch(g)
        sim = ParallelSimulator(profiles, total_rounds=5)
        sim.run()

        rep = ReportSynthesizer.generate(sim.all_actions, sim.rounds, profiles)
        self.assertIn("summary", rep)
        self.assertEqual(rep["summary"]["total_rounds"], 5)
        self.assertEqual(rep["summary"]["total_actions"], len(sim.all_actions))
        self.assertEqual(rep["summary"]["total_agents"], len(profiles))
        self.assertIn("emergent_signals", rep)
        self.assertIsInstance(rep["emergent_signals"], list)   # 分散分布下可为空（正常）
        self.assertTrue(rep["opinion_leaders"])
        self.assertEqual(len(rep["trend"]), 5)
        self.assertTrue(rep["conclusion"])

        for sig in rep["emergent_signals"]:
            self.assertGreater(sig["ratio"], 0.4)
            self.assertIn("主导", sig["pattern"])

        # 效力验证：单一动作占满 100% 时，涌现检测必须命中最高的那一类
        manual = [AgentAction(1, "t%d" % i, i, "n%d" % i, "CREATE_POST") for i in range(5)]
        rep2 = ReportSynthesizer.generate(manual, [], profiles[:5])
        self.assertTrue(rep2["emergent_signals"])
        self.assertEqual(rep2["emergent_signals"][0]["pattern"], "CREATE_POST主导")
        self.assertEqual(rep2["emergent_signals"][0]["ratio"], 1.0)


class TestDeepInteract(unittest.TestCase):
    def test_deep_interact(self):
        """深度交互：回复含 agent 姓名与提问原文，确定性可复现。"""
        g = SeedToGraph.build_graph(DEFAULT_SEED)
        profiles = PersonaArchitect.generate_batch(g)
        target = profiles[0]
        r1 = DeepInteractor.interview(target, "你对这次事件的看法？")
        r2 = DeepInteractor.interview(target, "你对这次事件的看法？")
        self.assertTrue(r1["success"])
        self.assertIn(target.name, r1["response"])
        self.assertIn("你对这次事件的看法？", r1["response"])
        self.assertEqual(r1["response"], r2["response"])
        self.assertEqual(r1["agent_name"], target.name)


class TestFiveStagePipeline(unittest.TestCase):
    def test_five_stage_pipeline(self):
        """完整五阶段：终态 INTERACT、城邦登记、报告落位。"""
        orch = SwarmOrchestrator()
        state = orch.run_pipeline(DEFAULT_SEED, total_rounds=3)
        self.assertEqual(state.current_stage, Stage.INTERACT)
        self.assertIsNotNone(state.completed_at)
        self.assertIsNotNone(state.graph)
        self.assertIsNotNone(state.report)
        self.assertEqual(state.current_round, 3)
        self.assertEqual(len(state.rounds), 3)
        self.assertIn(state.simulation_id, orch.simulations)
        listed = orch.list_simulations()
        self.assertEqual(len(listed), 1)
        self.assertEqual(listed[0]["simulation_id"], state.simulation_id)

        # 深度交互走编排器入口
        got = orch.interact(state.simulation_id, state.profiles[0].user_id, "你的立场？")
        self.assertTrue(got["success"])
        missed = orch.interact("no_such_sim", 0, "x")
        self.assertFalse(missed["success"])


class TestGodViewInject(unittest.TestCase):
    def test_god_view_inject(self):
        """God View：合法事件注入后 action 总数 +1；非法载荷被皮肤机制拦下。"""
        orch = SwarmOrchestrator()
        state = orch.run_pipeline(DEFAULT_SEED, total_rounds=2)
        before = len(state.all_actions)
        res = orch.god_view_inject(state.simulation_id,
                                   {"type": "policy_shift", "magnitude": 0.8})
        self.assertTrue(res["success"])
        self.assertEqual(len(state.all_actions), before + 1)
        injected = state.all_actions[-1]
        self.assertEqual(injected.action_type, "EVENT_INJECTION")
        self.assertEqual(injected.agent_name, "GOD_VIEW")

        bad = orch.god_view_inject(state.simulation_id, {})
        self.assertFalse(bad["success"])
        self.assertEqual(len(state.all_actions), before + 1)


class TestMechanismCoverage(unittest.TestCase):
    def test_mechanism_coverage(self):
        """扩展包：5 技能/3 角色/2 工作流，11/11 机制覆盖。"""
        p = SwarmIntelPack()
        self.assertEqual(p.key, "swarm_intel")
        self.assertEqual(len(p.skills), 5)
        self.assertEqual(len(p.roles), 3)
        self.assertEqual(len(p.workflows), 2)
        self.assertEqual(len(MECHANISM_COVERAGE), 11)

        manifest = get_manifest()
        self.assertEqual(manifest["coverage_count"], "11/11")
        self.assertEqual(len(manifest["skills"]), 5)
        self.assertEqual(len(manifest["roles"]), 3)
        self.assertEqual(len(manifest["workflows"]), 2)

        from holoaeon.packs import EXTRA_PACK_ORDER, get_extra_pack
        self.assertIn("swarm_intel", EXTRA_PACK_ORDER)
        self.assertEqual(EXTRA_PACK_ORDER.count("swarm_intel"), 1)
        self.assertEqual(get_extra_pack("swarm_intel").key, "swarm_intel")


if __name__ == "__main__":
    unittest.main()
