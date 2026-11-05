# -*- coding: utf-8 -*-
"""V19 概念解剖器（Concept Anatomizer）集成测试。

覆盖：十步工序 / 10 概念映射表 / 确定性（同概念→同解剖图）/
深度审计（重叠+穿透+一致性）/ SVG 输出 / 第 17 扩展包注册 /
butler_os 菜单 12 / CLI 入口。纯标准库 unittest。
"""
import json
import unittest

from holoaeon.concept_anatomy import CONCEPT_MAP, DESIGN_TOKENS, ConceptAnatomizer


class TestDesignTokens(unittest.TestCase):
    def test_tokens_count_26(self):
        self.assertEqual(len(DESIGN_TOKENS), 26)

    def test_tokens_five_groups(self):
        self.assertEqual(len([k for k in DESIGN_TOKENS if k.startswith("rt_")]), 6)
        self.assertEqual(len([k for k in DESIGN_TOKENS if k.startswith("audit_")]), 5)
        self.assertEqual(len([k for k in DESIGN_TOKENS if k.startswith("out_")]), 5)
        self.assertEqual(len([k for k in DESIGN_TOKENS if k.startswith("verify_")]), 5)
        self.assertEqual(len([k for k in DESIGN_TOKENS if k.startswith("holo_")]), 5)

    def test_verify_tokens_synced_v19(self):
        # V19 建立：EXTRA=17 / DOC=0.9.16；V22 同步：EXTRA=18 / DOC=0.9.17；V23 同步 DOC=0.9.18
        # V25 同步：EXTRA=19 / DOC=0.9.20（VERSION 0.9.1 冻结不动）
        # V32 同步：DOC=0.9.27（gap_bridge 缺口进化桥，EXTRA 仍 19）
# V33 同步：DOC=0.9.28（math_gate 数学编排闸门，EXTRA 仍 19）
# V34 同步：DOC=0.9.29（tea_gate 茶域编排闸门，EXTRA 仍 19）
        self.assertEqual(DESIGN_TOKENS["verify_extra_pack_order"], 19)
        self.assertEqual(DESIGN_TOKENS["verify_doc_version"], "0.9.29")
        self.assertEqual(DESIGN_TOKENS["verify_version"], "0.9.1")
        self.assertEqual(DESIGN_TOKENS["verify_diff0"], "2fc892cf9af6e755")


class TestConceptMap(unittest.TestCase):
    def test_map_has_10_concepts(self):
        self.assertEqual(len(CONCEPT_MAP), 10)

    def test_meridian_entry(self):
        e = CONCEPT_MAP["经络"]
        self.assertEqual(e["dimension"], "mechanism")
        self.assertEqual(e["mechanism"], "topology_resonance.resonance_node")
        self.assertGreaterEqual(len(e["components"]), 8)

    def test_city_updated_to_17(self):
        e = CONCEPT_MAP["城邦架构"]
        self.assertIn("EXTRA_PACK_ORDER(17)", e["mechanism"])
        self.assertIn("concept_anatomy", e["components"])


class TestAnatomizeTenSteps(unittest.TestCase):
    def setUp(self):
        self.ca = ConceptAnatomizer()

    def test_meridian_done(self):
        r = self.ca.anatomize("经络")
        self.assertEqual(r["concept"], "经络")
        self.assertEqual(r["status"], "DONE")
        self.assertEqual(r["steps_completed"], 10)
        self.assertEqual(r["anatomy"]["component_count"], 8)
        self.assertTrue(r["anatomy"]["audit"]["all_passed"])
        self.assertEqual(r["anatomy"]["audit"]["checks"]["penetration"]["issues_found"], 0)

    def test_all_concepts_done(self):
        for concept in CONCEPT_MAP:
            r = self.ca.anatomize(concept)
            self.assertEqual(r["status"], "DONE", f"{concept} 应 DONE")
            self.assertTrue(r["anatomy"]["audit"]["all_passed"],
                            f"{concept} 审计应全过")
            self.assertGreaterEqual(r["anatomy"]["component_count"], 5)

    def test_determinism_same_concept_same_output(self):
        # 确定性：同概念两次解剖，解剖数据逐字节一致（默认无时间戳）
        a = self.ca.anatomize("赫布协作场")
        b = self.ca.anatomize("赫布协作场")
        ja = json.dumps(a["anatomy"], ensure_ascii=False, sort_keys=True)
        jb = json.dumps(b["anatomy"], ensure_ascii=False, sort_keys=True)
        self.assertEqual(ja, jb)
        self.assertNotIn("timestamp", a["anatomy"])

    def test_unknown_concept(self):
        r = self.ca.anatomize("不存在概念")
        self.assertIn("error", r)
        self.assertEqual(len(r["available"]), 10)

    def test_audit_four_checks(self):
        r = self.ca.anatomize("皮肤机制")
        checks = r["anatomy"]["audit"]["checks"]
        self.assertEqual(sorted(checks.keys()),
                         ["consistency", "determinism", "overlap", "penetration"])


class TestSvgOutput(unittest.TestCase):
    def test_svg_rendered(self):
        ca = ConceptAnatomizer()
        r = ca.anatomize("城邦架构")
        svg = r["output"].get("svg", "")
        self.assertGreater(len(svg), 500)
        self.assertIn("<svg", svg)
        self.assertIn("概念解剖图：城邦架构", svg)

    def test_svg_disabled_by_token(self):
        ca = ConceptAnatomizer({"rt_svg_enabled": False})
        r = ca.anatomize("经络")
        self.assertNotIn("svg", r["output"])


class TestPackRegistration(unittest.TestCase):
    def test_extra_pack_order_contains_concept_anatomy(self):
        from holoaeon.packs import EXTRA_PACK_ORDER
        self.assertGreaterEqual(len(EXTRA_PACK_ORDER), 7)
        self.assertIn("concept_anatomy", EXTRA_PACK_ORDER)
        self.assertIn("eng_skills", EXTRA_PACK_ORDER)   # V24：末位由 swarm_intel 接续，改「包含」断言
        self.assertGreaterEqual(len(EXTRA_PACK_ORDER), 18)  # 下界（V24 实为 19）

    def test_get_extra_pack_counts(self):
        from holoaeon.packs import get_extra_pack
        p = get_extra_pack("concept_anatomy")
        self.assertEqual(p.key, "concept_anatomy")
        self.assertEqual(len(p.skills), 5)
        self.assertEqual(len(p.roles), 3)
        self.assertEqual(len(p.workflows), 1)
        names = {s.name for s in p.skills}
        self.assertEqual(names,
                         {"anatomy_concept", "anatomy_audit", "anatomy_svg",
                          "anatomy_map", "anatomy_tokens"})

    def test_pack_skills_callable(self):
        from holoaeon.packs.concept_anatomy_pack import (
            anatomy_audit, anatomy_concept, anatomy_map, anatomy_svg, anatomy_tokens)
        self.assertEqual(anatomy_concept("经络")["status"], "DONE")
        self.assertTrue(anatomy_audit("经络")["all_passed"])
        self.assertTrue(anatomy_svg("城邦架构")["has_svg_tag"])
        self.assertEqual(anatomy_map("去幻觉")["mechanism"],
                         CONCEPT_MAP["去幻觉"]["mechanism"])
        self.assertEqual(anatomy_tokens()["token_count"], 26)


class TestButlerOsMenu(unittest.TestCase):
    def test_menu_has_12_concept_anatomy(self):
        from holoaeon import butler_os
        self.assertIn("12", butler_os.MENU)
        self.assertEqual(butler_os.MENU["12"][0], "概念解剖")
        self.assertIs(butler_os.MENU["12"][1], butler_os.cmd_concept_anatomy)


class TestCli(unittest.TestCase):
    def test_cli_no_args_lists_concepts(self):
        from holoaeon.concept_anatomy import main
        rc = main([])
        self.assertEqual(rc, 0)

    def test_cli_with_concept(self):
        from holoaeon.concept_anatomy import main
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = main(["经络"])
        out = buf.getvalue()
        self.assertEqual(rc, 0)
        self.assertIn('"status": "DONE"', out)
        self.assertIn("概念解剖图：经络", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
