# -*- coding: utf-8 -*-
"""
V22 工程技能本地化工具箱（第18扩展包 eng_skills）测试
覆盖：8 技能结构 / 确定性（同输入→同输出）/ CLI / 扩展包注册 / 版本同步
"""
from __future__ import annotations

import json
import unittest

from holoaeon.packs.engineering_skills_pack import (
    EngineeringSkillsPack, PACK,
    grill_plan, session_handoff, re_explain, quick_prototype,
    deterministic_tdd, dual_axis_review, hypothesis_debug, shared_glossary,
    main,
)


class TestPackSpec(unittest.TestCase):
    def test_pack_counts(self):
        self.assertEqual(PACK.key, "eng_skills")
        self.assertEqual(len(PACK.skills), 8)
        self.assertEqual(len(PACK.roles), 4)
        self.assertEqual(len(PACK.workflows), 2)

    def test_skill_names(self):
        names = [s.name for s in PACK.skills]
        self.assertEqual(names, ["grill_plan", "session_handoff", "re_explain",
                                 "quick_prototype", "deterministic_tdd",
                                 "dual_axis_review", "hypothesis_debug",
                                 "shared_glossary"])

    def test_roles_workflows(self):
        self.assertEqual([r.name for r in PACK.roles],
                         ["planner", "reviewer", "debugger", "linguist"])
        self.assertEqual([w.name for w in PACK.workflows],
                         ["full_engineering", "quick_fix"])

    def test_registry_registered(self):
        from holoaeon.packs import EXTRA_PACK_ORDER, EXTRA_PACK_REGISTRY, get_extra_pack
        self.assertIn("eng_skills", EXTRA_PACK_ORDER)
        self.assertIn("eng_skills", EXTRA_PACK_REGISTRY)
        self.assertIn("eng_skills", EXTRA_PACK_ORDER)   # V24：swarm_intel 接续末位，改「包含」断言
        self.assertGreaterEqual(len(EXTRA_PACK_ORDER), 18)  # 下界（V24 实为 19）
        p = get_extra_pack("eng_skills")
        self.assertEqual(p.key, "eng_skills")

    def test_version_sync(self):
        from holoaeon.spec import DOC_VERSION, VERSION
        self.assertEqual(DOC_VERSION, "0.9.25")  # V30：0.9.24→0.9.25
        self.assertEqual(VERSION, "0.9.1")       # 冻结不动

    def test_install_on_kernel(self):
        from holoaeon.kernel import Kernel
        k = Kernel()
        rep = EngineeringSkillsPack().install(k)
        self.assertEqual(rep["pack"], "eng_skills")
        self.assertEqual(len(rep["skills"]), 8)
        self.assertEqual(len(rep["agents"]), 4)


class TestGrillPlan(unittest.TestCase):
    def test_structure(self):
        r = grill_plan("加个缓存")
        self.assertEqual(r["total_rounds"], 3)
        self.assertGreaterEqual(r["total_questions"], 1)
        for q in r["questions"]:
            self.assertIn("round", q)
            self.assertIn("question", q)
            self.assertIn("recommended_answer", q)
            self.assertIn("branch", q)

    def test_chinese_segmentation(self):
        # 中文无空格：正则分词拿到真实计划文本（而非 split() 空列表→fallback "plan" 假关键词）
        r = grill_plan("加个缓存")
        qs = " ".join(q["question"] for q in r["questions"])
        self.assertIn("缓存", qs)
        self.assertNotIn("plan", qs)  # 不退化到 fallback 假关键词
        r2 = grill_plan("")
        qs2 = " ".join(q["question"] for q in r2["questions"])
        self.assertIn("plan", qs2)  # 仅空输入才 fallback

    def test_deterministic(self):
        a = grill_plan("加个缓存", depth=3)
        b = grill_plan("加个缓存", depth=3)
        self.assertEqual(a, b)


class TestSessionHandoff(unittest.TestCase):
    def test_structure(self):
        r = session_handoff({"task": "写测试", "status": "wip:50%"}, "验证")
        self.assertTrue(r["handoff_id"].startswith("handoff_"))
        self.assertTrue(r["redacted"])
        self.assertEqual(r["mechanism"], "经络机制")
        self.assertIn("grill_plan", r["suggested_skills"])  # design 触发

    def test_deterministic_handoff_id(self):
        # 关键确定性修复：handoff_id 由状态派生，不含时间戳
        state = {"task": "重构内核", "todo": "剩余3项"}
        a = session_handoff(state, "review")
        b = session_handoff(state, "review")
        self.assertEqual(a["handoff_id"], b["handoff_id"])
        self.assertNotIn("time", a["handoff_id"])

    def test_unfinished_detection(self):
        r = session_handoff({"a": "todo:继续", "b": "done", "c": "wip:一半"})
        self.assertEqual(sorted(r["unfinished"]), ["a", "c"])


class TestReExplain(unittest.TestCase):
    def test_glossary_hit(self):
        r = re_explain("经络是自组织共振")
        self.assertGreaterEqual(r["glossary_terms_found"], 1)
        self.assertIn("【经络】", r["simplified"])
        self.assertEqual(r["mechanism"], "语义通信基座")

    def test_deterministic_no_learning(self):
        a = re_explain("经络是自组织共振")
        b = re_explain("经络是自组织共振")
        self.assertEqual(a, b)


class TestQuickPrototype(unittest.TestCase):
    def test_structure(self):
        r = quick_prototype("验证状态机")
        self.assertTrue(r["throwaway"])
        self.assertEqual(r["mode"], "logic")
        self.assertEqual(len(r["validation_plan"]), 6)
        self.assertEqual(r["golden_check"], "diff0不变")

    def test_mode_fallback(self):
        self.assertEqual(quick_prototype("x", mode="bogus")["mode"], "logic")
        self.assertEqual(quick_prototype("x", mode="ui")["mode"], "ui")


class TestDeterministicTdd(unittest.TestCase):
    def test_cycle(self):
        r = deterministic_tdd("缓存")
        self.assertEqual([c["step"] for c in r["cycle"]],
                         ["RED", "GREEN", "REFACTOR"])
        self.assertTrue(r["vertical_slice"])
        self.assertIn("diff0", r["cycle"][2]["guard"])


class TestDualAxisReview(unittest.TestCase):
    def test_structure(self):
        r = dual_axis_review()
        self.assertTrue(r["parallel"])
        self.assertEqual(r["axis_standards"]["tool"], "redline")
        self.assertEqual(r["axis_spec"]["tool"], "verify_v44")
        self.assertIn("verify_v44.py", r["axis_spec"]["command"])


class TestHypothesisDebug(unittest.TestCase):
    def test_phases(self):
        r = hypothesis_debug("崩溃")
        self.assertEqual(len(r["phases"]), 5)
        self.assertEqual(r["phases"][1]["guard"], "莱布尼茨PSR")
        self.assertEqual(r["anti_pattern"], "猜测→改→试→猜测（禁止）")


class TestSharedGlossary(unittest.TestCase):
    def test_full_glossary(self):
        r = shared_glossary()
        self.assertGreaterEqual(r["total_terms"], 10)
        g = r["glossary"]
        self.assertIn("经络", g)
        self.assertIn("access_weight", g["经络"])

    def test_query_resonance(self):
        r = shared_glossary("经络")
        self.assertGreaterEqual(r["resonance_count"], 1)
        self.assertEqual(r["mechanism"], "赫布协作场+经络")

    def test_deterministic_weights(self):
        # 关键确定性修复：默认 learning=False，权重=dimension 固定基线，两次调用一致
        a = shared_glossary()
        b = shared_glossary()
        self.assertEqual(a["glossary"]["经络"]["access_weight"],
                         b["glossary"]["经络"]["access_weight"])


class TestCli(unittest.TestCase):
    def test_list(self):
        rc = main(["--list"])
        self.assertEqual(rc, 0)

    def test_roles_workflows(self):
        self.assertEqual(main(["--roles"]), 0)
        self.assertEqual(main(["--workflows"]), 0)

    def test_skill_invoke(self):
        rc = main(["--skill", "grill_plan",
                   "--args", json.dumps({"plan_description": "加个缓存"})])
        self.assertEqual(rc, 0)

    def test_unknown_skill(self):
        self.assertEqual(main(["--skill", "nope"]), 1)

    def test_bad_json(self):
        self.assertEqual(main(["--skill", "grill_plan", "--args", "{bad"]), 1)


if __name__ == "__main__":
    unittest.main()
