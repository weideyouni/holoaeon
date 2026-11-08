# -*- coding: utf-8 -*-
"""V45 教学域闸门测试。零依赖，确定性断言。"""
import unittest

from holoaeon import teach_gate as tg


class TestTeachGate(unittest.TestCase):
    def test_chain_ring13(self):
        self.assertEqual(tg.CHAIN_POSITION["ring"], 13)
        self.assertIn("教学域", tg.CHAIN_POSITION["name"])

    def test_seal(self):
        self.assertEqual(tg.SEAL, "潮起开门，潮落闭嘴")

    def test_eleven_chapters(self):
        self.assertEqual(len(tg.CHAPTERS), 11)
        for cid in ("fine_tune", "prompting", "knowledge_edit",
                    "math_reasoning", "watermark", "jailbreak",
                    "steganography", "multimodal", "gui_agent",
                    "agent_safety", "rlhf_alignment"):
            self.assertIn(cid, tg.CHAPTERS)

    def test_defensive_chapters_marked(self):
        for cid in ("watermark", "jailbreak", "steganography",
                    "agent_safety"):
            self.assertEqual(tg.CHAPTERS[cid]["safety"], "defensive")
            self.assertIn("defense", tg.CHAPTERS[cid])

    def test_chapters_map_to_existing_skills(self):
        # 映射落点必须是有名有姓的既有模块（充技能匹配）
        self.assertIn("magic_lamp", tg.CHAPTERS["prompting"]["maps"])
        self.assertIn("math_gate", tg.CHAPTERS["math_reasoning"]["maps"])
        self.assertIn("guard", tg.CHAPTERS["jailbreak"]["maps"])
        self.assertIn("butler_os", tg.CHAPTERS["gui_agent"]["maps"])

    def test_lesson_unit_neutral_ok(self):
        u = tg.LessonUnit.create("prompting", "思维链与提示学习概念",
                                 "按手册步骤调用 API 完成练习", "dive-prompting")
        self.assertTrue(u["ok"])
        self.assertEqual(u["safety"], "neutral")
        self.assertEqual(set(u["steps"]), set(tg.LESSON_STEPS))

    def test_lesson_unit_unknown_chapter(self):
        self.assertFalse(tg.LessonUnit.create("nope", "a", "b", "c")["ok"])

    def test_zero_weaponization_forbidden_mark(self):
        u = tg.LessonUnit.create("jailbreak", "越狱提示词载荷生成教程",
                                 "练习", "x")
        self.assertFalse(u["ok"])
        self.assertIn("零武器化", u["error"])

    def test_defensive_requires_defense_content(self):
        bad = tg.LessonUnit.create("jailbreak", "泛泛而谈", "练习", "x")
        self.assertFalse(bad["ok"])
        good = tg.LessonUnit.create("jailbreak", "红线清单与拦截策略讲解",
                                    "用 guard 做防御性评测", "x")
        self.assertTrue(good["ok"])

    def test_safety_gate_block_and_allow(self):
        self.assertEqual(tg.SafetyGate.admit("含隐写编码器材料")["verdict"],
                         "BLOCK")
        self.assertEqual(tg.SafetyGate.admit("水印校验器使用方法")["verdict"],
                         "ALLOW")

    def test_concept_check_identical(self):
        r = tg.SelfTest.concept_check("思维链分步推理", "思维链分步推理")
        self.assertEqual(r["sim"], 1.0)
        self.assertTrue(r["passed"])

    def test_concept_check_similar_beats_unrelated(self):
        close = tg.SelfTest.concept_check("提示学习与思维链",
                                          "提示工程 思维链 分步推理")
        far = tg.SelfTest.concept_check("提示学习与思维链",
                                        "腰椎间盘突出康复训练")
        self.assertGreater(close["sim"], far["sim"])

    def test_practice_check_full_and_partial(self):
        full = tg.SelfTest.practice_check(["加载模型", "微调", "部署"],
                                          ["加载模型", "微调", "部署"])
        self.assertTrue(full["passed"])
        part = tg.SelfTest.practice_check(["加载模型"],
                                          ["加载模型", "微调", "部署"])
        self.assertFalse(part["passed"])
        self.assertEqual(part["diffs"], ["微调", "部署"])

    def test_curriculum_start_finish(self):
        c = tg.Curriculum()
        r = c.start_lesson("prompting")
        self.assertTrue(r["ok"])
        self.assertGreaterEqual(r["beat"], 1)
        self.assertIn("magic_lamp", r["maps"])
        f = c.finish_lesson("prompting", True)
        self.assertEqual(f["state"], "done")

    def test_curriculum_finish_before_start(self):
        c = tg.Curriculum()
        self.assertFalse(c.finish_lesson("prompting", True)["ok"])

    def test_curriculum_transcript(self):
        c = tg.Curriculum()
        c.start_lesson("prompting")
        c.finish_lesson("prompting", True)
        t = c.transcript()
        self.assertTrue(t["ok"])
        self.assertEqual(t["done"], 1)
        self.assertEqual(t["total"], 11)

    def test_audit_snapshot(self):
        s = tg.audit()
        self.assertTrue(s["zero_weaponization"])
        self.assertFalse(s["neural"])
        self.assertEqual(s["chapters"], 11)
        self.assertEqual(len(s["defensive"]), 4)
        self.assertIn("craft_gate.Heartbeat", s["reused"])


if __name__ == "__main__":
    unittest.main()
