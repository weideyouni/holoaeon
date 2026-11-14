# -*- coding: utf-8 -*-
"""V64 挂账清零批测试（tests/test_v64_hangover_zero.py）

六条挂账逐条对应：
  ① G-M 门禁四项 WAIT      -> TestBusChannel / TestC03Gate
  ② 12 协议缺口            -> TestGapAdapters
  ③ P4 小程序提示词         -> TestMiniappPrompt
  ④ 214 格 pending-evidence -> TestMeridianRecheck
  ⑤ 7 位机制未覆盖          -> TestMechanismBearers
  ⑥ 402e369 西里尔字符      -> TestErrata

纪律：只读仓内文件与模块，不联网、不写仓库（write_ledger 只写 data/，
本测试不复跑写盘命令）。
"""
import io
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _data(name):
    with io.open(os.path.join(ROOT, "data", name), encoding="utf-8") as f:
        return json.load(f)


def _report(name):
    with io.open(os.path.join(ROOT, "reports", name), encoding="utf-8") as f:
        return json.load(f)


class TestBusChannel(unittest.TestCase):
    """挂账 ①：G-M 门禁四判据（12 通道 / 传播 / 阻塞 / 衰减终止）。"""

    def setUp(self):
        from holoaeon import bus_channel
        self.bc = bus_channel

    def test_self_check_all_pass(self):
        rep = self.bc.self_check()
        self.assertEqual(rep["verdict"], "PASS")
        self.assertEqual(rep["passed"], 4)
        self.assertEqual(rep["failed"], [])

    def test_twelve_channels_split_5_4_3(self):
        self.assertEqual(len(self.bc.CHANNELS), 12)
        groups = {g["group"]: g["count"] for g in self.bc.CHANNEL_GROUPS}
        self.assertEqual(groups, {"气": 5, "血": 4, "神": 3})
        self.assertEqual(len(self.bc.UNMAPPED_TARGETS), 5)
        unmapped = {u["target"] for u in self.bc.UNMAPPED_TARGETS}
        self.assertEqual(unmapped, {"神4", "淋巴1", "淋巴2", "淋巴3", "淋巴4"})

    def test_patency_model_clamped(self):
        self.assertEqual(self.bc.patency(100, 9, 100), 91)
        self.assertEqual(self.bc.patency(100, 200, 100), 0)
        self.assertTrue(self.bc.is_blocked(39, 40))
        self.assertFalse(self.bc.is_blocked(40, 40))

    def test_three_demo_chains_reproducible(self):
        d1 = self.bc.check_propagation()["detail"]
        d2 = self.bc.check_propagation()["detail"]
        self.assertEqual(len(d1["chains"]), 3)
        self.assertEqual([c["tau"] for c in d1["chains"]], [c["tau"] for c in d2["chains"]])
        for c in d1["chains"]:
            self.assertTrue(c["reproducible"])
            self.assertEqual(c["hops"], 3)
        ids = [c["id"] for c in d1["chains"]]
        self.assertIn("C02-C03-C10", ids)

    def test_blocking_triggers_bayes_reroute(self):
        d = self.bc.check_blocking()["detail"]
        self.assertTrue(d["rolled_back"])
        self.assertEqual(d["blocked_at"], "LC03")
        self.assertEqual(d["top1"], "LC03")
        posts = [x["posterior"] for x in d["posterior_top"]]
        self.assertEqual(posts, sorted(posts, reverse=True))
        self.assertEqual(d["posterior_top"][0]["patency"], 0)

    def test_four_terminations_observable(self):
        d = self.bc.check_termination()["detail"]
        self.assertEqual(set(d.keys()),
                         {"gain_floor", "max_hops", "closed_loop", "blocked"})
        for kind in ("gain_floor", "max_hops", "closed_loop", "blocked"):
            self.assertEqual(d[kind], kind)

    def test_table_ledger_written(self):
        t = _data("bus_channel_table.json")
        self.assertEqual(t["channels"], 12)
        self.assertEqual(t["groups"], {"气": 5, "血": 4, "神": 3})
        self.assertEqual(t["check"]["verdict"], "PASS")


class TestC03Gate(unittest.TestCase):
    """挂账 ①：C03 G-M 门禁从「恒 WAIT」变「可吃证据」。"""

    def setUp(self):
        from holoaeon import org_gate, bus_channel
        self.org_gate = org_gate
        self.bc = bus_channel

    def test_default_still_wait_without_evidence(self):
        rep = self.org_gate.c03_gate_report()
        self.assertFalse(rep["pass"])
        self.assertEqual(rep["states"]["12 通道"], "WAIT")
        self.assertEqual(rep["states"]["事件传播"], "WAIT")
        self.assertEqual(rep["states"]["阻塞机制"], "WAIT")
        self.assertEqual(rep["states"]["衰减与终止"], "WAIT")
        self.assertEqual(sum(1 for v in rep["states"].values() if v == "WAIT"), 4)
        self.assertFalse(rep["evidence_supplied"])

    def test_live_report_all_pass(self):
        rep = self.org_gate.c03_gate_report_live()
        self.assertTrue(rep["pass"])
        self.assertTrue(rep["evidence_supplied"])
        self.assertEqual([v for v in rep["states"].values() if v == "WAIT"], [])
        self.assertEqual([v for v in rep["states"].values() if v == "FAIL"], [])

    def test_criteria_text_untouched(self):
        # 六判据三态原文（V63 定稿），本批一字未改
        self.assertEqual(len(self.org_gate.C03_GM_CRITERIA), 6)
        joined = "".join(c["item"] + c["test"] for c in self.org_gate.C03_GM_CRITERIA)
        self.assertIn("通畅度模型", joined)
        self.assertIn("贝叶斯衍射反演", joined)
        self.assertIn("衰减", joined)

    def test_gate_blocks_until_open(self):
        rep = self.org_gate.c03_gate_report()
        self.assertIn("禁止启动任何领域深化批次", rep["hard_rule"])
        self.assertEqual(rep["gate"], "G-M")


class TestMechanismBearers(unittest.TestCase):
    """挂账 ⑤：7 位未覆盖机制的真实承载者登记。"""

    def setUp(self):
        from holoaeon import mechanism_bearers
        self.mb = mechanism_bearers

    def test_seven_bearers_verified(self):
        rep = self.mb.check_bearers()
        self.assertEqual(rep["verdict"], "PASS")
        self.assertEqual(rep["verified"], 7)
        self.assertEqual(len(self.mb.BEARERS), 7)

    def test_symbols_resolve_to_real_objects(self):
        rep = self.mb.check_bearers()
        got = {r["mech"] for r in rep["rows"] if r["ok"]}
        for mid in ("C1", "R2", "R5", "R6", "R7", "R8", "X2"):
            self.assertIn(mid, got)

    def test_coverage_two_ways_union_full(self):
        cov = self.mb.coverage()
        self.assertEqual(cov["lathe_direct"]["count"], 18)
        self.assertEqual(cov["bearer_only"]["count"], 7)
        self.assertEqual(cov["total_unique"]["count"], 25)
        self.assertTrue(cov["full"])

    def test_mechanism_ids_is_25(self):
        self.assertEqual(len(self.mb.MECHANISM_IDS), 25)
        self.assertEqual(len(set(self.mb.MECHANISM_IDS)), 25)

    def test_ledger_written_with_root_cause(self):
        led = _data("mechanism_bearers.json")
        self.assertEqual(led["coverage"]["total_unique"]["count"], 25)
        self.assertIn("承载", led["root_cause"])


class TestGapAdapters(unittest.TestCase):
    """挂账 ②：12 平台缺口两态（V66 起 12 adapted / 0 gap）。"""

    def setUp(self):
        from holoaeon import gap_adapters
        self.ga = gap_adapters

    def test_twelve_total_twelve_adapted_zero_gap(self):
        rep = self.ga.check_gaps()
        self.assertEqual(rep["total"], 12)
        self.assertEqual(rep["adapted"], 12)
        self.assertEqual(rep["gaps"], 0)
        self.assertEqual(rep["gap_list"], [])
        self.assertEqual(rep["verdict"], "PASS")

    def test_platform_shapes_not_forced_into_openai(self):
        rep = self.ga.check_gaps()
        self.assertEqual(rep["model_shapes"], 5)
        self.assertEqual(rep["platform_shapes"], 4)
        for pid in ("dify", "dify-workflow", "coze", "n8n"):
            self.assertNotEqual(self.ga.get_platform(pid)["shape"], "openai_chat")

    def test_xfyun_is_openai_compatible(self):
        p = self.ga.get_platform("xfyun")
        self.assertEqual(p["shape"], "openai_chat")
        self.assertIn("spark-api-open.xf-yun.com", p["base_url"])
        self.assertIn("兼容 openAI SDK", p["evidence"])

    def test_build_request_urls(self):
        r = self.ga.build_request("xfyun", "generalv3.5", [{"role": "user", "content": "hi"}])
        self.assertEqual(r["url"], "https://spark-api-open.xf-yun.com/v1/chat/completions")
        self.assertIn("messages", r["body"])
        d = self.ga.build_request("dify", extra={"query": "你好"})
        self.assertEqual(d["url"], "https://api.dify.ai/v1/chat-messages")
        self.assertEqual(set(d["body"].keys()),
                         {"inputs", "query", "response_mode", "conversation_id", "user"})
        c = self.ga.build_request("coze", extra={"bot_id": "b1", "additional_messages": [
            {"role": "user", "content": "hi", "content_type": "text"}]})
        self.assertEqual(c["url"], "https://api.coze.cn/v3/chat")
        self.assertIn("additional_messages", c["body"])
        n = self.ga.build_request("n8n", extra={"action": "list_workflows"})
        self.assertTrue(n["url"].endswith("/api/v1/workflows"))
        self.assertIn("X-N8N-API-KEY", n["headers_hint"])

    def test_dify_workflow_adapted_from_source_code(self):
        """V66：dify-workflow 由源码取证补齐；V67 追加本机回环，verification 变成两段。"""
        p = self.ga.get_platform("dify-workflow")
        self.assertEqual(p["status"], "adapted")
        self.assertEqual(p["shape"], "dify_workflow")
        self.assertTrue(p["verification"].startswith("source_code_read"))
        self.assertIn("local_contract_loopback", p["verification"])
        self.assertIn("service_api/app/workflow.py", p["source_url"])
        self.assertIn("/workflows/run", p["evidence"])
        r = self.ga.build_request("dify-workflow", extra={"inputs": {"q": "x"}})
        self.assertEqual(r["url"], "https://api.dify.ai/v1/workflows/run")
        self.assertIn("user", r["body"])          # Service API 强制 user
        self.assertEqual(r["body"]["response_mode"], "blocking")
        s = self.ga.build_request("dify-workflow", extra={"inputs": {}}, stream=True)
        self.assertEqual(s["body"]["response_mode"], "streaming")
        self.assertTrue(s["stream"])

    def test_gap_raises_not_fake(self):
        """机制守卫：仍为 gap 的条目不得被假拼成请求（临时置 gap 验证）。"""
        p = self.ga.get_platform("dify-workflow")
        saved = (p["status"], p.get("missing"))
        try:
            p["status"], p["missing"] = "gap", "测试用临时缺口"
            with self.assertRaises(ValueError):
                self.ga.build_request("dify-workflow")
        finally:
            p["status"], p["missing"] = saved

    def test_every_adapted_has_source_url(self):
        for g in self.ga.GAPS:
            if g["status"] == "adapted":
                self.assertTrue(str(g["source_url"]).startswith("http")
                                or g["source_url"].startswith("vector-sea/"))

    def test_ledger_written(self):
        led = _data("protocol_gap_adapters.json")
        self.assertEqual(led["check"]["adapted"], 11)
        self.assertEqual(led["check"]["gaps"], 1)


class TestMeridianRecheck(unittest.TestCase):
    """挂账 ④：214 格 pending-evidence 复核（pending 归零）。"""

    def setUp(self):
        from holoaeon import meridian_recheck
        self.mr = meridian_recheck

    def test_pending_goes_to_zero(self):
        rep = self.mr.recheck()
        self.assertEqual(rep["summary"]["pending_after"], 0)
        self.assertEqual(rep["cells"], 250)
        self.assertEqual(rep["verdict"], "PASS")

    def test_states_sum_to_total(self):
        rep = self.mr.recheck()
        s = rep["summary"]
        self.assertEqual(s["linked"] + s["unlinked"], 250)
        self.assertEqual(s["pending_original"], 214)

    def test_v62_original_linked_kept(self):
        rep = self.mr.recheck()
        self.assertEqual(rep["summary"]["kept_v62"], 13)
        kept = [c for c in rep["cells_detail"] if c.get("origin") == "V62"]
        self.assertEqual(len(kept), 13)

    def test_linked_cells_carry_keyword_evidence(self):
        rep = self.mr.recheck()
        for c in rep["cells_detail"]:
            if c["state"] == "linked" and c.get("origin") == "V64-RECHECK":
                self.assertTrue(c["evidence"])
                self.assertEqual(c["evidence"][0]["kind"], "desc_keyword")
                self.assertTrue(c["evidence"][0]["hits"])

    def test_unlinked_has_explicit_reason(self):
        rep = self.mr.recheck()
        for c in rep["cells_detail"]:
            if c["state"] == "unlinked":
                self.assertIn("零命中", c.get("note", ""))

    def test_ledger_written(self):
        led = _data("searchnet_d03_meridian_recheck.json")
        self.assertEqual(led["summary"]["pending_after"], 0)
        self.assertEqual(len(led["cells"]), 250)

    def test_evidence_source_is_real_desc(self):
        src = _data("d03_fragment_essence.json")
        self.assertEqual(src["fragments"], 10)
        for r in src["rows"]:
            self.assertTrue(r["official_desc"])


class TestMiniappPrompt(unittest.TestCase):
    """挂账 ③：P4 小程序提示词工厂。"""

    def setUp(self):
        from holoaeon import miniapp_prompt
        self.mp = miniapp_prompt

    def test_three_recipes_check_pass(self):
        rep = self.mp.check()
        self.assertEqual(rep["verdict"], "PASS")
        self.assertEqual(rep["recipes"], 3)

    def test_pages_and_fields_complete(self):
        for r in self.mp.RECIPES:
            p = self.mp.build_prompt(r["domain"])
            self.assertGreaterEqual(len(p["pages"]), 5)
            for pg in p["pages"]:
                self.assertTrue(pg["components"])
                self.assertTrue(pg["fields"])
                self.assertTrue(pg["events"])

    def test_render_markdown_has_sections(self):
        p = self.mp.build_prompt("rehab-followup")
        md = self.mp.render_markdown(p)
        for sec in ("产品定位", "页面清单", "审核与合规", "交付验收", "禁止项"):
            self.assertIn(sec, md)
        self.assertGreater(len(md), 800)

    def test_deterministic_same_input_same_output(self):
        a = self.mp.build_prompt("farm-ledger")
        b = self.mp.build_prompt("farm-ledger")
        self.assertEqual(json.dumps(a, ensure_ascii=False, sort_keys=True),
                         json.dumps(b, ensure_ascii=False, sort_keys=True))

    def test_medical_recipe_forbids_diagnosis(self):
        p = self.mp.build_prompt("rehab-followup")
        joined = "".join(p["compliance"]) + "".join(p["do_not"])
        self.assertIn("不得出现诊断结论", joined)

    def test_unknown_domain_raises(self):
        with self.assertRaises(KeyError):
            self.mp.build_prompt("no-such-domain")

    def test_ledger_written(self):
        led = _data("miniapp_prompt_recipes.json")
        self.assertEqual(led["check"]["verdict"], "PASS")
        self.assertEqual(len(led["recipes"]), 3)


class TestErrata(unittest.TestCase):
    """挂账 ⑥：402e369 西里尔字符勘误；附 V63 回执口径勘误。"""

    def test_cyrillic_errata_registered(self):
        er = _report("commit_message_errata.json")
        self.assertEqual(er["char_index"], 410)
        self.assertEqual(er["codepoint"], "U+0435")
        self.assertEqual(er["utf8_bytes"], "D0 B5")
        self.assertIn("holoa", er["context"])

    def test_errata_records_measured_search_impact(self):
        er = _report("commit_message_errata.json")
        self.assertEqual(er["impact_measured"]["git_log_grep_latin_hits"], 0)
        self.assertGreaterEqual(er["impact_measured"]["git_log_grep_cyrillic_hits"], 1)

    def test_no_history_rewrite_discipline(self):
        er = _report("commit_message_errata.json")
        self.assertTrue(any("不 amend" in x for x in er["discipline"]["do"]))

    def test_v63_receipt_errata_registered(self):
        er = _report("v63_receipt_errata.json")
        self.assertEqual(er["correct_semantics"]["registered_count"], 12)
        self.assertEqual(er["correct_semantics"]["gap_count"], 12)
        self.assertEqual(er["v64_resolution"]["adapted"], 11)
        self.assertEqual(er["v64_resolution"]["gaps"], 1)


class TestBatchSurface(unittest.TestCase):
    """批次面：新增模块可导入、四件台账齐、DOC 已升号。"""

    def test_new_modules_importable(self):
        from holoaeon import bus_channel, mechanism_bearers, gap_adapters, meridian_recheck, miniapp_prompt
        for m in (bus_channel, mechanism_bearers, gap_adapters, meridian_recheck, miniapp_prompt):
            self.assertTrue(getattr(m, "SCHEMA_VERSION"))

    def test_four_ledgers_present(self):
        for name in ("bus_channel_table.json", "mechanism_bearers.json",
                     "protocol_gap_adapters.json", "miniapp_prompt_recipes.json",
                     "searchnet_d03_meridian_recheck.json", "d03_fragment_essence.json"):
            self.assertTrue(os.path.exists(os.path.join(ROOT, "data", name)))

    def test_doc_version_bumped(self):
        from holoaeon import spec
        self.assertEqual(spec.DOC_VERSION, "0.9.76")  # V82 起
        self.assertEqual(spec.VERSION, "0.9.1")


if __name__ == "__main__":
    unittest.main()
