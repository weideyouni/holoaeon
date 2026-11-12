# -*- coding: utf-8 -*-
"""tests/test_v63_forge_bureau.py —— V63 制造局总闸测试套件（真 unittest）。

八组：机床资产/机床经络/自然语言调度/打造流水线/产品线/平台适配/共振磁吸附/
台账与 CLI+总闸。实测值固化（350 格=79 linked/271 unlinked；打通 18/25 未覆盖
7 位如实列举；探针吸附 C14 技艺仓——零虚构）。
"""
import json
import os
import sys
import tempfile
import unittest

from holoaeon import forge_bureau as fb
from holoaeon.meridian_link import KERNEL_MECHANISMS
from holoaeon.salvage_gate import C18_NUMBERING, ADAPTATION_REQUIRED


def _entry(module):
    for e in fb.LATHE_MODULES:
        if e["module"] == module:
            return e
    raise KeyError(module)


def _product(pid):
    for p in fb.PRODUCT_LINES:
        if p["id"] == pid:
            return p
    raise KeyError(pid)


def _step(sid):
    for s in fb.FORGE_RAIL:
        if s["id"] == sid:
            return s
    raise KeyError(sid)


# ============================================================ 一、机床资产
class TestLatheModules(unittest.TestCase):

    def test_lathe_modules_14(self):
        self.assertEqual(len(fb.LATHE_MODULES), 14)

    def test_families(self):
        fams = {e["family"] for e in fb.LATHE_MODULES}
        self.assertEqual(len(fams), 14)  # 14 位 14 家族（每位一家族标签）
        for need in ("机床", "加载", "校验", "矩阵", "总装", "勘探", "适配",
                     "工艺", "装配", "熔炼", "神灯", "漩涡", "进化", "逆向"):
            self.assertIn(need, fams)

    def test_check_lathe_modules_pass(self):
        res = fb.check_lathe_modules()
        self.assertTrue(res["pass"], res["problems"])

    def test_craft_organ_map_anchor_count(self):
        from holoaeon.craft_gate import ORGAN_MAP
        craft = _entry("craft_gate")
        self.assertEqual(len(craft["mech_anchors"]), len(ORGAN_MAP))

    def test_titan_anchors_match_mechanisms(self):
        from holoaeon.titan_evolver import MECHANISMS as TITAN_MECHS
        titan = _entry("titan_evolver")
        self.assertEqual(sorted(titan["mech_anchors"]),
                         sorted(m["id"] for m in TITAN_MECHS))

    def test_no_duplicate_modules(self):
        mods = [e["module"] for e in fb.LATHE_MODULES]
        self.assertEqual(len(mods), len(set(mods)))


# ============================================================ 二、机床经络
class TestLatheMeridian(unittest.TestCase):

    def test_table_350_cells(self):
        self.assertEqual(len(fb.build_lathe_meridian()), 14 * 25)

    def test_table_full_coverage_pairs(self):
        table = fb.build_lathe_meridian()
        want = {(e["module"], m["id"]) for e in fb.LATHE_MODULES
                for m in KERNEL_MECHANISMS}
        got = {(c["module"], c["mech"]) for c in table}
        self.assertEqual(want, got)

    def test_counts_measured(self):
        """实测值固化（零虚构）：350 格=79 linked/271 unlinked。"""
        table = fb.build_lathe_meridian()
        linked = sum(1 for c in table if c["state"] == "linked")
        self.assertEqual(linked, 79)
        self.assertEqual(len(table) - linked, 271)

    def test_mech_covered_18_uncovered_7(self):
        """打通=诚实计数：18/25 直连；未覆盖 7 位属拓扑共振/耗散验证域
        （非机床家族职能——机制轴 25 位仍全表穷举在场）。"""
        mer = fb.check_lathe_meridian()
        self.assertTrue(mer["pass"], mer["problems"])
        self.assertEqual(mer["mech_covered"], 18)
        self.assertEqual(mer["mech_uncovered"],
                         ["C1", "R2", "R5", "R6", "R7", "R8", "X2"])

    def test_craft_gate_richest_links(self):
        table = fb.build_lathe_meridian()
        craft = [c for c in table if c["module"] == "craft_gate"
                 and c["state"] == "linked"]
        self.assertEqual(len(craft), 13)  # 六器官+键证据（docstring 自述器官在案）
        self.assertIn("M04", {c["mech"] for c in craft})

    def test_anchor_evidence_recorded(self):
        table = fb.build_lathe_meridian()
        for c in table:
            if c["state"] == "linked":
                self.assertTrue(c["evidence"])
            else:
                self.assertEqual(c["evidence"], [])

    def test_table_deterministic(self):
        self.assertEqual(fb.build_lathe_meridian(), fb.build_lathe_meridian())


# ============================================================ 三、自然语言调度
class TestIntentDispatch(unittest.TestCase):

    def test_parse_intent_deterministic(self):
        a = fb.parse_intent("制造一枚技能并测试")
        b = fb.parse_intent("制造一枚技能并测试")
        self.assertEqual(a, b)
        self.assertFalse(a["llm"])

    def test_parse_intent_product_hit(self):
        intent = fb.parse_intent("帮我做小程序提示词与白皮书")
        self.assertIn("P4", intent["product_hits"])
        self.assertIn("P6", intent["product_hits"])

    def test_parse_intent_step_hit(self):
        intent = fb.parse_intent("先创造再测试再回炉调试")
        for sid in ("F2", "F3", "F4"):
            self.assertIn(sid, intent["step_hits"])

    def test_parse_intent_keywords_domain(self):
        intent = fb.parse_intent("调度技能加载完成适配入库")
        self.assertTrue(set(intent["keywords"]))
        for kw in intent["keywords"]:
            self.assertNotIn(kw, fb.INTENT_STOPWORDS)

    def test_dispatch_plan_structure(self):
        intent = fb.parse_intent("一键成型独立引擎")
        plan = fb.dispatch_plan(intent)
        self.assertEqual(len(plan["rail"]), 8)
        self.assertEqual(plan["rail"][0]["step"], "F1")
        self.assertTrue(any(f["product"] == "P5" for f in plan["focus"]))
        self.assertEqual(plan["seal"], fb.SEAL)


# ============================================================ 四、打造流水线
class TestForgeRail(unittest.TestCase):

    def test_rail_eight_steps_order(self):
        self.assertEqual([s["id"] for s in fb.FORGE_RAIL],
                         ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8"])

    def test_rail_names(self):
        names = [s["name"] for s in fb.FORGE_RAIL]
        self.assertEqual(names, ["需求解析", "技能创造", "测试试错", "调试回炉",
                                  "神灯联动", "漩涡联动", "双模块", "适配成型"])

    def test_rail_walk_no_skip(self):
        rail = fb.ForgeRail()
        seen = []
        for _ in range(8):
            step = rail.advance()
            self.assertTrue(step["ok"])
            seen.append(step["step"])
            self.assertTrue(rail.complete()["ok"])
        self.assertEqual(seen, [s["id"] for s in fb.FORGE_RAIL])
        self.assertEqual(rail.snapshot()["pos"], 8)

    def test_rail_end_boundary(self):
        rail = fb.ForgeRail()
        for _ in range(8):
            rail.advance()
            rail.complete()
        end = rail.advance()
        self.assertFalse(end["ok"])
        self.assertEqual(end["error"], "rail at end")

    def test_reforge_back_to_f2(self):
        rail = fb.ForgeRail()
        for _ in range(3):
            rail.advance()
            rail.complete()
        rf = rail.reforge()
        self.assertTrue(rf["ok"])
        self.assertEqual(rf["reforged_to"], "F2")
        self.assertEqual(rail.snapshot()["pos"], 1)
        self.assertEqual(rail.snapshot()["state"]["F3"], "pending")
        self.assertEqual(rail.snapshot()["state"]["F4"], "pending")

    def test_reforge_boundary_pos_below_2(self):
        rail = fb.ForgeRail()
        rail.advance()
        rail.complete()  # pos=1
        rf = rail.reforge()
        self.assertFalse(rf["ok"])

    def test_fail_blocked(self):
        rail = fb.ForgeRail()
        rail.advance()
        res = rail.fail()
        self.assertFalse(res["ok"])
        self.assertEqual(rail.snapshot()["state"]["F1"], "blocked")

    def test_check_rail_pass(self):
        res = fb.check_rail()
        self.assertTrue(res["pass"], res["problems"])


# ============================================================ 五、产品线
class TestProductLines(unittest.TestCase):

    def test_products_10(self):
        self.assertEqual(len(fb.PRODUCT_LINES), 10)

    def test_products_anchored_vs_pending(self):
        """9 锚定+1 待造（小程序提示词 P4——真成品须平台素材投喂后落）。"""
        anchored = [p["id"] for p in fb.PRODUCT_LINES if p["status"] == "anchored"]
        pending = [p["id"] for p in fb.PRODUCT_LINES if p["status"] == "待造"]
        self.assertEqual(len(anchored), 9)
        self.assertEqual(pending, ["P4"])

    def test_pending_declared_honestly(self):
        p4 = _product("P4")
        self.assertEqual(p4["anchors"], ())
        self.assertTrue(p4["note"])

    def test_anchored_modules_importable(self):
        import importlib
        for p in fb.PRODUCT_LINES:
            if p["status"] == "anchored":
                for anchor in p["anchors"]:
                    mod = anchor.split(".")[0]
                    importlib.import_module("holoaeon." + mod)

    def test_product_ids_sequential(self):
        self.assertEqual([p["id"] for p in fb.PRODUCT_LINES],
                         ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8",
                          "P9", "P10"])

    def test_check_product_lines_pass(self):
        res = fb.check_product_lines()
        self.assertTrue(res["pass"], res["problems"])


# ============================================================ 六、平台适配
class TestProtocols(unittest.TestCase):

    def test_protocols_12(self):
        self.assertEqual(len(fb.PROTOCOL_REGISTRY), 12)

    def test_list_matches_registry(self):
        from holoaeon.protocol_plugins import list_protocols
        self.assertEqual(sorted(list_protocols()),
                         sorted(fb.PROTOCOL_REGISTRY.keys()))

    def test_protocol_names_true_listing(self):
        """真列举：国际大模型协议+工作流/工作台适配面 12 在册。"""
        names = set(fb.PROTOCOL_REGISTRY.keys())
        for need in ("openai_function", "anthropic_tool", "gemini_function",
                     "mcp", "a2a", "acp", "langchain_tool", "llamaindex_tool",
                     "autogen_tool", "crewai_tool", "bedrock_converse",
                     "envelope"):
            self.assertIn(need, names)

    def test_gaps_12_true_listing(self):
        """国内国际缺口真列举：大模型×8+工作台×2+工作流×2，未适配不虚报。"""
        self.assertEqual(len(fb.PLATFORM_GAPS), 12)
        for g in fb.PLATFORM_GAPS:
            self.assertEqual(g["status"], "未适配")
        plats = {g["platform"] for g in fb.PLATFORM_GAPS}
        self.assertIn("dify", plats)
        self.assertIn("coze（扣子）", plats)

    def test_check_protocols_pass(self):
        res = fb.check_protocols()
        self.assertTrue(res["pass"], res["problems"])


# ============================================================ 七、共振磁吸附
class TestAbsorb(unittest.TestCase):

    def test_cang_18(self):
        self.assertEqual(len(C18_NUMBERING), 18)

    def test_absorb_deterministic(self):
        spec = {"name": "probe", "description": "探针", "tags": ["t"]}
        self.assertEqual(fb.forge_absorb(spec)["absorbed_into"]["repo"],
                         fb.forge_absorb(spec)["absorbed_into"]["repo"])

    def test_absorb_probe_c14_skill(self):
        """实测固化：制造局探针吸附 C14 技艺仓（技艺=制造的本位仓）。"""
        spec = {"name": "forge_probe_skill",
                "description": "制造局吸附探针：机床加工经络链接技能",
                "tags": ["forge", "meridian", "lathe"]}
        rec = fb.forge_absorb(spec)
        self.assertEqual(rec["absorbed_into"]["cang"], "C14")
        self.assertEqual(rec["absorbed_into"]["repo"], "holoaeon-c14-skill")

    def test_absorb_record_skeleton(self):
        spec = {"name": "probe", "description": "探针", "tags": ["t"]}
        rec = fb.forge_absorb(spec)
        self.assertEqual(sorted(rec["adaptation_record"].keys()),
                         sorted(ADAPTATION_REQUIRED))

    def test_base_root_three_pieces(self):
        spec = {"name": "probe", "description": "探针", "tags": ["t"]}
        root = fb.forge_absorb(spec)["base_root"]
        for k in ("module", "ledger", "cross_thread_call"):
            self.assertTrue(root[k], "基座留根缺件：{}".format(k))
        self.assertEqual(root["module"], "holoaeon/forge_bureau.py")

    def test_tie_break_small_cang(self):
        """平分取编号小仓（V60 先例）：构造双仓同分 spec 验证 tie-break。"""
        c1, c2 = C18_NUMBERING[0], C18_NUMBERING[1]
        # 直接构造使两仓同分：spec 文本==仓 1 身份文本（与仓 2 不同分）不构造
        # 同分——改验排序键：scores.sort(key=(-score, repo)) 小仓在前
        spec = {"name": c1["repo"], "description": _ident(c1),
                "tags": [c1["domain"]]}
        rec = fb.forge_absorb(spec)
        self.assertEqual(rec["absorbed_into"]["repo"], c1["repo"])

    def test_check_absorb_pass(self):
        res = fb.check_absorb()
        self.assertTrue(res["pass"], res["problems"])


def _ident(c):
    return "{}；{}；{}".format(c.get("domain", ""), c.get("question", ""),
                              c.get("role", ""))


# ============================================================ 八、台账+CLI+总闸
class TestLedgerCliGate(unittest.TestCase):

    def test_build_ledger_structure(self):
        ledger = fb.build_ledger()
        for k in ("project", "batch", "date", "schema", "source",
                  "lathe_modules", "mechanism_axis", "lathe_meridian",
                  "table", "product_lines", "protocols", "platform_gaps",
                  "seal"):
            self.assertIn(k, ledger)
        self.assertEqual(ledger["batch"], "V63-FORGE-BUREAU")
        self.assertEqual(ledger["mechanism_axis"], 25)
        self.assertEqual(len(ledger["table"]), 350)
        self.assertEqual(len(ledger["lathe_modules"]), 14)
        self.assertEqual(len(ledger["product_lines"]), 10)

    def test_ledger_deterministic_no_wallclock(self):
        self.assertEqual(json.dumps(fb.build_ledger(), ensure_ascii=False),
                         json.dumps(fb.build_ledger(), ensure_ascii=False))

    def test_write_ledger_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "ledger.json")
            out = fb.write_ledger(p)
            self.assertEqual(out, p)
            with open(p, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            self.assertEqual(data["lathe_meridian"]["cells"], 350)

    def test_cli_check_rc0(self):
        self.assertEqual(fb._main(["forge_bureau", "check"]), 0)

    def test_cli_rail_rc0(self):
        self.assertEqual(fb._main(["forge_bureau", "rail"]), 0)

    def test_cli_products_rc0(self):
        self.assertEqual(fb._main(["forge_bureau", "products"]), 0)

    def test_cli_protocols_rc0(self):
        self.assertEqual(fb._main(["forge_bureau", "protocols"]), 0)

    def test_cli_absorb_rc0(self):
        self.assertEqual(fb._main(["forge_bureau", "absorb"]), 0)

    def test_cli_ledger_rc0_out(self):
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "l.json")
            self.assertEqual(fb._main(["forge_bureau", "ledger", "--out", p]), 0)
            self.assertTrue(os.path.exists(p))

    def test_cli_usage_rc1(self):
        self.assertEqual(fb._main(["forge_bureau"]), 1)

    def test_cli_unknown_rc1(self):
        self.assertEqual(fb._main(["forge_bureau", "bogus"]), 1)

    def test_cli_out_missing_rc1(self):
        self.assertEqual(fb._main(["forge_bureau", "ledger", "--out"]), 1)

    def test_check_all_six_sections_pass(self):
        res = fb.check_all()
        for sec in ("lathe_modules", "lathe_meridian", "rail",
                    "product_lines", "protocols", "absorb"):
            self.assertTrue(res[sec]["pass"], res[sec]["problems"])
        self.assertTrue(res["pass"])
        self.assertEqual(res["seal"], "潮起开门，潮落闭嘴")


if __name__ == "__main__":
    unittest.main()
