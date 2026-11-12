# -*- coding: utf-8 -*-
"""test_v61_salvage_patch —— V61 打捞局修补批真 unittest（ring23 patch1）。

八组：归一化公式/数据源口径/语义门槛/查询句法与扩展词/排名两段式/
B 榜数据入仓/CLI 修正/总闸九检查。
真实数据声明：B 榜 10 条与偏题案例均来自豆包端 D03 真跑回执实录
（2026-11-12 验证批），本套件以其固化回归——防七毛病复发。
"""

from __future__ import annotations

import unittest

from holoaeon.salvage_gate import (
    CITATION_COLLECTION,
    CITATION_SOURCES,
    CONTRIBUTOR_SOURCE,
    DIMENSIONS,
    NORM_REFS,
    OFF_TOPIC_CASE,
    PATCH_SEVEN_FIXES,
    REL_MIN_HITS,
    SalvageGate,
    build_prompt,
    check_d03_b,
    check_patch,
    check_scoring,
    composite_score,
    dim_keywords,
    fingerprint,
    load_d03_b,
    norm_value,
    probe,
    rank_candidates,
    recency_score,
    relevance_gate,
    relevance_hits,
    resolve_duplicates,
)


class TestNormFormula(unittest.TestCase):
    """一、P3 归一化公式（量纲统一——修 stars 一家说了算）。"""

    def test_norm_refs_declared(self):
        self.assertEqual(NORM_REFS["stars"], 100000)
        self.assertEqual(NORM_REFS["forks"], 10000)
        self.assertEqual(NORM_REFS["contributors"], 500)

    def test_norm_stars_log(self):
        import math
        expected = round(math.log10(1 + 60807) / math.log10(1 + 100000), 4)
        self.assertEqual(norm_value("stars", 60807), expected)

    def test_norm_stars_cap_at_one(self):
        self.assertEqual(norm_value("stars", 10 ** 9), 1.0)  # 上限截断

    def test_norm_forks_log(self):
        import math
        expected = round(math.log10(1 + 8000) / math.log10(1 + 10000), 4)
        self.assertEqual(norm_value("forks", 8000), expected)

    def test_norm_contributors_linear_cap(self):
        self.assertEqual(norm_value("contributors", 300), round(300 / 500, 4))
        self.assertEqual(norm_value("contributors", 900), 1.0)

    def test_norm_citation_binary(self):
        self.assertEqual(norm_value("citation", 1), 1.0)
        self.assertEqual(norm_value("citation", 0), 0.0)

    def test_norm_unknown_none(self):
        self.assertIsNone(norm_value("stars", None))
        self.assertIsNone(norm_value("contributors", -1))

    def test_norm_unknown_kind_raises(self):
        with self.assertRaises(ValueError):
            norm_value("watchers", 100)

    def test_norm_monotonic(self):
        self.assertLess(norm_value("stars", 100), norm_value("stars", 1000))

    def test_composite_in_unit_interval(self):
        for stars in (0, 100, 60807, 122903):
            s = composite_score({"stars": stars, "forks": 500, "contributors": 100,
                                 "citation": 1, "last_commit_months": 1})
            self.assertIsNotNone(s)
            self.assertTrue(0.0 <= s <= 1.0, stars)

    def test_composite_log_compression(self):
        # P3 实证口径：星数差 10 倍，综合分只差对数压缩比（非 10 倍raw差）
        big = composite_score({"stars": 122903, "forks": 50, "contributors": 50,
                               "citation": 1, "last_commit_months": 0})
        small = composite_score({"stars": 12290, "forks": 50, "contributors": 50,
                                 "citation": 1, "last_commit_months": 0})
        self.assertLess(big / small, 1.5)  # 对数归一压平量纲（修复前 raw 差≈10 倍权重差）

    def test_composite_deterministic(self):
        c = {"stars": 60807, "forks": 8000, "contributors": 300, "citation": 1,
             "last_commit_months": 6}
        self.assertEqual(composite_score(c), composite_score(c))

    def test_composite_unknown_still_none(self):
        for missing in ("stars", "forks", "contributors", "citation", "last_commit_months"):
            c = {"stars": 1, "forks": 1, "contributors": 1, "citation": 1,
                 "last_commit_months": 1}
            c[missing] = None
            self.assertIsNone(composite_score(c), missing)  # 禁估算纪律不动

    def test_recency_unchanged(self):
        self.assertEqual(recency_score(0.0), 1.0)
        self.assertEqual(recency_score(24.0), 0.0)


class TestDataSourceSpecs(unittest.TestCase):
    """二、P4/P5 数据源口径（贡献者 403 实测与榜单引用采集方式）。"""

    def test_contributor_source_primary(self):
        self.assertIn("Link header", CONTRIBUTOR_SOURCE["primary"])

    def test_contributor_source_unavailable_policy(self):
        self.assertIn("null", CONTRIBUTOR_SOURCE["unavailable"])
        self.assertIn("unverified", CONTRIBUTOR_SOURCE["unavailable"])

    def test_contributor_source_rejects_badges(self):
        self.assertIn("rejected", CONTRIBUTOR_SOURCE)
        self.assertIn("不采", CONTRIBUTOR_SOURCE["rejected"])

    def test_citation_sources_whitelist(self):
        self.assertTrue(len(CITATION_SOURCES) >= 3)
        joined = " ".join(CITATION_SOURCES)
        self.assertIn("awesome-", joined)
        self.assertIn("Trending", joined)

    def test_citation_collection_method(self):
        self.assertIn("URL 检索确认", CITATION_COLLECTION)
        self.assertIn("二值化", CITATION_COLLECTION)

    def test_check_scoring_reports_sources(self):
        r = check_scoring()
        self.assertTrue(r["pass"], r["problems"])
        self.assertIn("Link header", r["contributor_source"])
        self.assertTrue(r["citation_sources"] >= 3)
        self.assertEqual(r["rel_min_hits"], 2)
        self.assertIn("norm_refs", r)


class TestRelevanceGate(unittest.TestCase):
    """三、P6 语义门槛两段式（治本——碳基裁定采 B）。"""

    def test_rel_min_hits_two(self):
        self.assertEqual(REL_MIN_HITS, 2)

    def test_off_topic_case_registered(self):
        self.assertEqual(OFF_TOPIC_CASE["repo"], "stablyai/orca")
        self.assertEqual(OFF_TOPIC_CASE["stars"], 122903)

    def test_off_topic_blocked(self):
        # A 榜第一 122903★ 编码智能体 IDE——必须被拦（固化回归）
        g = relevance_gate({**OFF_TOPIC_CASE, "topics": ["coding-agent", "ide"]}, "D03")
        self.assertEqual(g["verdict"], "OUT")

    def test_off_topic_blocked_even_with_all_metrics(self):
        g = relevance_gate({**OFF_TOPIC_CASE, "forks": 900, "contributors": 400,
                            "citation": 1, "last_commit_months": 0,
                            "readme_or_desc": True}, "D03")
        self.assertEqual(g["verdict"], "OUT")  # 热度再高也拦

    def test_b_list_crewai_in(self):
        g = relevance_gate({"repo": "crewAIInc/crewAI",
                            "desc": "Framework for orchestrating role-playing AI agents",
                            "topics": ["agent", "orchestration"]}, "D03")
        self.assertEqual(g["verdict"], "IN")

    def test_b_list_kafka_in(self):
        g = relevance_gate({"repo": "apache/kafka",
                            "desc": "distributed log streaming platform",
                            "topics": ["event-streaming", "pub-sub", "message-broker"]}, "D03")
        self.assertEqual(g["verdict"], "IN")

    def test_b_list_jaeger_signoz_in(self):
        for repo, desc, topics in (
                ("jaegertracing/jaeger", "Distributed Tracing Platform", ["tracing", "monitoring"]),
                ("SigNoz/signoz", "open source observability", ["observability", "tracing", "metrics"])):
            g = relevance_gate({"repo": repo, "desc": desc, "topics": topics}, "D03")
            self.assertEqual(g["verdict"], "IN", repo)

    def test_dim_keywords_derived(self):
        kw = dim_keywords("D03")
        self.assertIn("orchestration", kw)
        self.assertIn("tracing", kw)
        self.assertIn("pub", kw)  # P2 能力词扩容后入键
        self.assertIn("event", kw)

    def test_dim_keywords_stopwords_removed(self):
        for dim in ("D01", "D05", "D18"):
            for w in dim_keywords(dim):
                self.assertNotIn(w, ("for", "and", "the", "open", "source"), w)

    def test_dim_keywords_unknown_dim_raises(self):
        with self.assertRaises(ValueError):
            dim_keywords("D19")

    def test_relevance_hits_text_mode(self):
        self.assertGreaterEqual(relevance_hits("workflow engine with tracing", "D03"), 2)

    def test_relevance_hits_zero_for_empty(self):
        self.assertEqual(relevance_hits("", "D03"), 0)
        self.assertEqual(relevance_hits({}, "D03"), 0)

    def test_relevance_hits_deterministic(self):
        c = {"repo": "x/y", "desc": "workflow engine", "topics": ["bus"]}
        self.assertEqual(relevance_hits(c, "D03"), relevance_hits(c, "D03"))

    def test_relevance_matches_repo_and_topics(self):
        g = relevance_gate({"repo": "o/workflow-engine", "desc": "", "topics": []}, "D03")
        self.assertGreaterEqual(g["hits"], 2)  # 仓名命中也算


class TestQuerySyntaxAndExpand(unittest.TestCase):
    """四、P1 查询句法 + P2 扩展词双类扩容。"""

    def test_prompt_contains_syntax_rules(self):
        p = build_prompt("D03", "T0")
        self.assertIn("禁整句单查", p)
        self.assertIn("OR 连接", p)
        self.assertIn("能力词", p)
        self.assertIn("total_count=1", p)  # 真跑实证留痕

    def test_d03_expand_expanded_to_eight(self):
        d03 = DIMENSIONS[2]
        self.assertEqual(d03["dim"], "D03")
        self.assertTrue(6 <= len(d03["expand"]) <= 8)
        self.assertIn("pub/sub", d03["expand"])
        self.assertIn("event-driven architecture", d03["expand"])

    def test_expand_kind_dual_note(self):
        d03 = DIMENSIONS[2]
        joined = " ".join(d03["expand"])
        self.assertIn("tracing", joined)  # 能力词
        self.assertIn("message bus", joined)  # 品类词保留

    def test_prompt_d03_lists_capability_words(self):
        p = build_prompt("D03", "T0")
        self.assertIn("pub/sub", p)
        self.assertIn("checkpoint", p)


class TestRankCandidates(unittest.TestCase):
    """五、两段式排名（先语义门槛后综合分）。"""

    def _cand(self, repo, desc, topics, stars, months=1):
        return {"repo": repo, "desc": desc, "topics": topics, "stars": stars,
                "forks": 100, "contributors": 50, "citation": 1,
                "last_commit_months": months, "readme_or_desc": True}

    def test_rank_filters_off_topic_first(self):
        cands = [
            self._cand("stablyai/orca", "coding agent IDE for autonomous development",
                       ["ide"], 122903),
            self._cand("jaegertracing/jaeger", "Distributed Tracing Platform",
                       ["tracing"], 23403),
        ]
        r = rank_candidates(cands, "D03")
        self.assertEqual(r["ranked"][0]["repo"], "jaegertracing/jaeger")
        self.assertEqual(r["rejected"], 1)

    def test_rank_order_by_composite(self):
        cands = [
            self._cand("a/small-rel", "workflow engine tracing", ["bus"], 100, months=0),
            self._cand("b/big-rel", "workflow engine tracing", ["bus"], 60000, months=12),
        ]
        r = rank_candidates(cands, "D03")
        self.assertEqual(r["ranked"][0]["repo"], "b/big-rel")

    def test_rank_none_score_sinks_not_dropped(self):
        cands = [
            self._cand("a/unknown-metric", "workflow engine tracing", ["bus"], None),
            self._cand("b/full-metric", "workflow engine tracing", ["bus"], 500),
        ]
        r = rank_candidates(cands, "D03")
        self.assertEqual(len(r["ranked"]), 2)  # None 沉底保留不淘汰
        self.assertEqual(r["ranked"][0]["repo"], "b/full-metric")
        self.assertIsNone(r["scores"][1])

    def test_rank_gate_log_complete(self):
        cands = [
            self._cand("stablyai/orca", "coding agent IDE", ["ide"], 122903),
            self._cand("a/rel", "workflow engine tracing", ["bus"], 100),
        ]
        r = rank_candidates(cands, "D03")
        self.assertEqual(len(r["gate_log"]), 2)
        self.assertEqual(r["gate_log"][0]["verdict"], "OUT")

    def test_rank_deterministic(self):
        cands = [
            self._cand("a/x", "workflow engine tracing", ["bus"], 100),
            self._cand("b/y", "workflow engine tracing", ["bus"], 100),
        ]
        r1, r2 = rank_candidates(cands, "D03"), rank_candidates(cands, "D03")
        self.assertEqual([c["repo"] for c in r1["ranked"]],
                         [c["repo"] for c in r2["ranked"]])

    def test_resolve_duplicates_uses_normalized_scores(self):
        hi = {"repo": "o/r", "dim_id": "D03", "stars": 60000, "forks": 8000,
              "contributors": 400, "citation": 1, "last_commit_months": 1}
        lo = {"repo": "o/r", "dim_id": "D18", "stars": 50, "forks": 5,
              "contributors": 2, "citation": 0, "last_commit_months": 20}
        r = resolve_duplicates([hi, lo])
        self.assertEqual(r["total_actual"], 1)
        self.assertIn("D03", r["duplicates"][0]["resolution"])


class TestD03BData(unittest.TestCase):
    """六、B 榜真跑数据入仓（验证批成果正式落盘）。"""

    def test_load_d03_b(self):
        data = load_d03_b()
        self.assertEqual(data["dim_id"], "D03")
        self.assertEqual(data["cang"], "holoaeon-c03-meridian")

    def test_ten_results(self):
        self.assertEqual(len(load_d03_b()["results"]), 10)

    def test_b_list_repos_match_receipt(self):
        repos = [r["repo"] for r in load_d03_b()["results"]]
        self.assertEqual(repos[0], "crewAIInc/crewAI")
        self.assertEqual(repos[1], "apache/kafka")
        self.assertEqual(repos[9], "microsoft/agent-framework")

    def test_b_list_stars_match_receipt(self):
        by_repo = {r["repo"]: r["stars"] for r in load_d03_b()["results"]}
        self.assertEqual(by_repo["crewAIInc/crewAI"], 60807)
        self.assertEqual(by_repo["apache/kafka"], 34214)
        self.assertEqual(by_repo["stablyai/orca" if False else "SigNoz/signoz"], 32598)

    def test_all_unverified_honest(self):
        for r in load_d03_b()["results"]:
            self.assertEqual(r["verify_status"], "unverified")
            self.assertIsNone(r["contributors"])  # 403 实测未估算

    def test_kafka_essence_recorded(self):
        by_repo = {r["repo"]: r for r in load_d03_b()["results"]}
        self.assertIn("分布式追加日志式事件平台", by_repo["apache/kafka"]["essence"])

    def test_essence_absent_is_null_not_fabricated(self):
        # 回执全文只给了 kafka 一条 essence——其余如实 null 零虚构
        nulls = [r["repo"] for r in load_d03_b()["results"] if r["essence"] is None]
        self.assertEqual(len(nulls), 9)

    def test_off_topic_not_in_b_list(self):
        repos = [r["repo"] for r in load_d03_b()["results"]]
        self.assertNotIn("stablyai/orca", repos)

    def test_license_three_states(self):
        licenses = {r["license"] for r in load_d03_b()["results"]}
        self.assertIn("NOASSERTION", licenses)  # FastGPT/SignOz——降权不淘汰口径

    def test_check_d03_b_pass(self):
        r = check_d03_b()
        self.assertTrue(r["pass"], r["problems"])
        self.assertEqual(r["count"], 10)
        self.assertEqual(sorted(r["legs"]), ["可观测", "总线", "编排"])


class TestCLIFix(unittest.TestCase):
    """七、P7 CLI 修正（--root 全子命令+prompt --dim）。"""

    def test_prompt_dim_switchable(self):
        p5 = build_prompt("D05", "T0")
        p13 = build_prompt("D13", "T0")
        self.assertIn("spaced repetition", p5)
        self.assertIn("time series forecasting", p13)

    def test_cli_prompt_with_dim(self):
        from holoaeon.salvage_gate import _main
        self.assertEqual(_main(["salvage_gate", "prompt", "--dim", "D11"]), 0)

    def test_cli_prompt_bad_dim_fails(self):
        from holoaeon.salvage_gate import _main
        self.assertEqual(_main(["salvage_gate", "prompt", "--dim", "D99"]), 1)

    def test_cli_root_on_all_subcommands(self):
        from holoaeon.salvage_gate import _main
        for cmd in ("dims", "schedule", "prompt", "d03b"):
            self.assertEqual(
                _main(["salvage_gate", cmd, "--root", "F:/doubaowork"]), 0, cmd)

    def test_cli_d03b_command(self):
        from holoaeon.salvage_gate import _main
        self.assertEqual(_main(["salvage_gate", "d03b"]), 0)

    def test_cli_probe_reports_off_topic(self):
        p = probe()
        self.assertEqual(p["off_topic_gate"], "OUT")
        self.assertEqual(p["d03_b_count"], 10)
        self.assertTrue(0.0 <= p["sample_score"] <= 1.0)


class TestGateNineChecks(unittest.TestCase):
    """八、总闸九检查 + 修订清单。"""

    def test_patch_seven_fixes_complete(self):
        self.assertEqual(len(PATCH_SEVEN_FIXES), 7)
        codes = [f[0] for f in PATCH_SEVEN_FIXES]
        for p in ("P1", "P2", "P3", "P4", "P5", "P6", "P7"):
            self.assertTrue(any(c.startswith(p) for c in codes), p)

    def test_check_patch_pass(self):
        r = check_patch()
        self.assertTrue(r["pass"], r["problems"])
        self.assertEqual(len(r["fixes"]), 7)

    def test_nine_checks_with_fixture_root(self):
        import os, shutil, tempfile
        root = tempfile.mkdtemp(prefix="salvage_fx_")
        try:
            for name in ("打捞之王600万1331x1331超级矩阵V3实战化_20261020",
                         "账号记忆打捞1331x1331多智能体矩阵V3实战化_20261023",
                         "向量海结构化打捞_20260926", "打捞之王部落"):
                os.makedirs(os.path.join(root, name), exist_ok=True)
            for fname in ("打捞之王定向矩阵金刚.md",
                          "千问端角色卡_打捞之王_V1.0_20260929.md",
                          "打捞600语义确认.md"):
                with open(os.path.join(root, fname), "w", encoding="utf-8") as fh:
                    fh.write("fx")
            sc = SalvageGate(root).self_check()
            self.assertTrue(sc["pass"], sc["problems"])
            self.assertEqual(len(sc["checks"]), 9)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_summary_report_patch_field(self):
        rep = SalvageGate().summary_report()
        self.assertEqual(rep["ring"], 23)
        self.assertEqual(rep["patch"], 1)

    def test_fingerprint_patch(self):
        fp = fingerprint()
        self.assertEqual(fp["ring"], 23)
        self.assertEqual(fp["patch"], 1)
        self.assertEqual(fp["total_expected"], 180)

    def test_fingerprint_deterministic(self):
        self.assertEqual(fingerprint(), fingerprint())


if __name__ == "__main__":
    unittest.main()
