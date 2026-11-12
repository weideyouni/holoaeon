# -*- coding: utf-8 -*-
"""test_v60_salvage_gate —— V60 打捞之王仓库端模块真 unittest（ring23 打捞局）。

九组：资产自动匹配/名词穷举/搜索网/判定口径/提示词模板/汇总去重/日程/
吸纳本地化/总闸+CLI。
真实数据声明：资产身份（600万/600 双分身/记忆打捞/金刚/角色卡）为向量海
对账事实；测试以 fixture 资产树验证自动匹配机制（本机真根实测另由 CLI
--root 实跑留痕，见投喂包实测链）。
"""

from __future__ import annotations

import os
import shutil
import tempfile
import unittest

from holoaeon.salvage_gate import (
    ADAPTATION_REQUIRED,
    AGGREGATE_REQUIRED,
    DIMENSIONS,
    DIM_RECORD_REQUIRED,
    DOMAIN_NOUNS,
    ESSENCE_MARKETING_WORDS,
    KNOWN_CROSS_LAYER_NOUNS,
    MECHANISM_NOUNS,
    NOUN_DIM_COVERAGE,
    NOUN_SLOTS_MEASURED,
    PHASE_NOUNS,
    PER_DIM_TARGETS,
    RESULT_REQUIRED,
    SALVAGE_ASSETS,
    SALVAGE_CYCLE_DAYS,
    SALVAGE_ORDER,
    SCORE_WEIGHTS,
    STRUCTURAL_NOUNS,
    TOTAL_EXPECTED,
    SalvageGate,
    build_prompt,
    check_assets,
    check_assimilation,
    check_dimensions,
    check_essence,
    check_nouns,
    check_scoring,
    check_schedule,
    check_template,
    composite_score,
    day_plan,
    dim_of,
    discover_salvage_assets,
    fingerprint,
    hard_gate,
    probe,
    recency_score,
    resolve_duplicates,
    schedule_report,
    slot_enrichment_plan,
    validate_adaptation,
    validate_dim_record,
)
from holoaeon.c18_cluster import C18_NUMBERING
from holoaeon.tensor_gate import SEARCH_DIMENSIONS, SEARCH_RECORD_REQUIRED


def _mk(path: str, is_file: bool = False) -> None:
    if is_file:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("fixture")
    else:
        os.makedirs(path, exist_ok=True)


class TestAssetDiscovery(unittest.TestCase):
    """一、打捞之王资产自动匹配（登记基座——指针纪律）。"""

    @classmethod
    def setUpClass(cls):
        cls.root = tempfile.mkdtemp(prefix="salvage_fx_")
        r = cls.root
        _mk(os.path.join(r, "打捞之王600万1331x1331超级矩阵V3实战化_20261020"))
        _mk(os.path.join(r, "账号记忆打捞1331x1331多智能体矩阵V3实战化_20261023"))
        _mk(os.path.join(r, "向量海", "03_知识角色库", "打捞之王部落"))
        _mk(os.path.join(r, "向量海", "台账与清单", "向量海结构化打捞_20260926"))
        _mk(os.path.join(r, "向量海", "02_源文件", "打捞之王定向矩阵金刚.md"), is_file=True)
        _mk(os.path.join(r, "向量海", "03_知识角色库", "打捞之王",
                         "千问端角色卡_打捞之王_V1.0_20260929.md"), is_file=True)
        _mk(os.path.join(r, "镜像区", "VECTOR-MATRIX", "打捞600语义确认.md"), is_file=True)
        _mk(os.path.join(r, "_历史工程归档", "打捞之王600万旧归档"))  # 应被跳过扫描

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.root, ignore_errors=True)

    def test_registry_ten_assets(self):
        self.assertEqual(len(SALVAGE_ASSETS), 10)

    def test_registry_unique_ids(self):
        ids = [a["id"] for a in SALVAGE_ASSETS]
        self.assertEqual(len(set(ids)), 10)

    def test_6m_identity_facts(self):
        a = next(x for x in SALVAGE_ASSETS if x["id"] == "sk6m_600m")
        self.assertEqual(a["sg_id"], "SG-MASTER-SALVAGE-KING-6M-1331x1331-SUPER-MAS-V3.0")
        self.assertTrue(a["required"])

    def test_600_twins_distinct(self):
        defect = next(x for x in SALVAGE_ASSETS if x["id"] == "defect_600")
        know = next(x for x in SALVAGE_ASSETS if x["id"] == "knowledge_600")
        self.assertEqual(defect["sg_id"], "SG-SALVAGE-KING-600-SUPER-MATRIX-V1.0")
        self.assertEqual(know["sg_id"],
                         "SG-UPGRADE-KNOWLEDGE-SALVAGE-KING-600AGENT-20260517")
        self.assertNotEqual(defect["sg_id"], know["sg_id"])  # 双分身不可混用

    def test_knowledge_600_authorized_landed(self):
        a = next(x for x in SALVAGE_ASSETS if x["id"] == "knowledge_600")
        self.assertIsNone(a["pattern"])  # 实体=本模块（授权落地）
        self.assertIn("授权落地", a["nature"])

    def test_discover_fixture_hits(self):
        m = discover_salvage_assets(self.root)
        self.assertTrue(m["sk6m_600m"])
        self.assertTrue(m["mem_salvage"])
        self.assertTrue(m["tribe"])
        self.assertTrue(m["diamond_log"])
        self.assertTrue(m["role_card"])
        self.assertTrue(m["structured_ledger"])
        self.assertTrue(m["semantics_600"])

    def test_discover_deterministic(self):
        self.assertEqual(discover_salvage_assets(self.root),
                         discover_salvage_assets(self.root))

    def test_discover_skips_underscore_dirs(self):
        m = discover_salvage_assets(self.root)
        for paths in m.values():
            for p in paths:
                self.assertNotIn("_历史工程归档", p)

    def test_discover_depth_three_found(self):
        m = discover_salvage_assets(self.root)
        self.assertTrue(any("打捞之王部落" in p for p in m["tribe"]))

    def test_check_assets_pass_on_fixture(self):
        r = check_assets(self.root)
        self.assertTrue(r["pass"], r["problems"])

    def test_check_assets_knowledge_state(self):
        r = check_assets(self.root)
        by_id = {a["id"]: a for a in r["assets"]}
        self.assertEqual(by_id["knowledge_600"]["state"], "authorized-landed")

    def test_check_assets_missing_required_fails(self):
        empty = tempfile.mkdtemp(prefix="salvage_empty_")
        try:
            r = check_assets(empty)
            self.assertFalse(r["pass"])
            self.assertTrue(r["problems"])
        finally:
            shutil.rmtree(empty, ignore_errors=True)

    def test_check_assets_unspecified_root_wait(self):
        r = check_assets(None)
        self.assertFalse(r["pass"])
        self.assertEqual(r["state"], "WAIT")  # 门禁三态：不替未来签字
        self.assertTrue(any("WAIT" in p or "未指定" in p for p in r["problems"]))

    def test_pointer_discipline_no_absolute_paths_in_code(self):
        import inspect
        from holoaeon import salvage_gate as sg
        src = inspect.getsource(sg)
        self.assertNotIn("F:/doubaowork", src)  # 仓内零本机路径硬编码
        self.assertNotIn("F:\\doubaowork", src)


class TestNouns(unittest.TestCase):
    """二、名词四层穷举（实测 65 位——素材声称 62 澄清留痕）。"""

    def test_65_slots_measured(self):
        self.assertEqual(NOUN_SLOTS_MEASURED, 65)

    def test_layers_measured_counts(self):
        self.assertEqual(len(STRUCTURAL_NOUNS), 11)  # 素材声称 10——实测列 11
        self.assertEqual(len(DOMAIN_NOUNS), 18)
        self.assertEqual(len(PHASE_NOUNS), 10)  # 素材声称 9——实测列 10
        self.assertEqual(len(MECHANISM_NOUNS), 26)  # 素材声称 25——实测列 26

    def test_domain_nouns_match_c18(self):
        self.assertEqual(DOMAIN_NOUNS, tuple(c["domain"] for c in C18_NUMBERING))

    def test_known_cross_layer_dup(self):
        self.assertEqual(KNOWN_CROSS_LAYER_NOUNS, ("全息镜像根",))  # 素材两层重复列举如实留痕

    def test_no_orphan_nouns(self):
        r = check_nouns()
        self.assertTrue(r["pass"], r["problems"])

    def test_coverage_dims_valid(self):
        valid = {"D{:02d}".format(i) for i in range(1, 19)} | {"ALL"}
        for noun, dims in NOUN_DIM_COVERAGE.items():
            for d in dims:
                self.assertIn(d, valid, "{}->{}".format(noun, d))

    def test_all_nouns_covered(self):
        all_nouns = set(STRUCTURAL_NOUNS) | set(DOMAIN_NOUNS) | set(PHASE_NOUNS) | set(MECHANISM_NOUNS)
        for n in all_nouns:
            self.assertTrue(n in NOUN_DIM_COVERAGE or n in DOMAIN_NOUNS,
                            "孤立名词：{}".format(n))

    def test_mechanism_nouns_full_set(self):
        for w in ("传导", "阻塞", "内化", "变现", "节律", "觉悟", "稳态",
                  "自组织相似性", "共同演化", "耗散结构式耦合"):
            self.assertIn(w, MECHANISM_NOUNS)


class TestDimensions(unittest.TestCase):
    """三、18 维搜索网（一仓一维，N19 基座元层不占维）。"""

    def test_18_dims(self):
        self.assertEqual(len(DIMENSIONS), 18)

    def test_dim_codes_d01_to_d18(self):
        self.assertEqual([d["dim"] for d in DIMENSIONS],
                         ["D{:02d}".format(i) for i in range(1, 19)])

    def test_one_cang_one_dim(self):
        cangs = [d["cang"] for d in DIMENSIONS]
        self.assertEqual(sorted(cangs), sorted(c["id"] for c in C18_NUMBERING))
        self.assertEqual(len(set(cangs)), 18)

    def test_n19_not_a_dim(self):
        self.assertNotIn("N19", [d["cang"] for d in DIMENSIONS])

    def test_dim_of_lookup(self):
        d = dim_of("C03")
        self.assertIsNotNone(d)
        self.assertEqual(d["dim"], "D03")
        self.assertIsNone(dim_of("N19"))

    def test_d03_contains_base_layer_note(self):
        d = dim_of("C03")
        self.assertIn("基座元层", d["intent"])

    def test_per_dim_and_total(self):
        self.assertEqual(PER_DIM_TARGETS, 10)
        self.assertEqual(TOTAL_EXPECTED, 180)

    def test_dual_numbering_coexists(self):
        # D1-D5（每仓五问，V59）与 D01-D18（一仓一维，本模块）双体系并存
        self.assertEqual(len(SEARCH_DIMENSIONS), 5)
        self.assertEqual(len(DIMENSIONS), 18)
        v59_codes = {d[0] for d in SEARCH_DIMENSIONS}
        self.assertEqual(v59_codes, {"D1", "D2", "D3", "D4", "D5"})
        v60_codes = {d["dim"] for d in DIMENSIONS}
        self.assertFalse(v59_codes & v60_codes)  # 零填充可区分——零冲突

    def test_check_dimensions_pass(self):
        r = check_dimensions()
        self.assertTrue(r["pass"], r["problems"])


class TestScoring(unittest.TestCase):
    """四、头部目标判定口径（四指标权重+硬门槛+降权——禁止自由发挥）。"""

    def test_weights_sum_one(self):
        self.assertEqual(round(sum(SCORE_WEIGHTS.values()), 6), 1.0)

    def test_weights_values(self):
        self.assertEqual(SCORE_WEIGHTS["stars"], 0.40)
        self.assertEqual(SCORE_WEIGHTS["recency"], 0.20)

    def test_recency_boundaries(self):
        self.assertEqual(recency_score(0.0), 1.0)
        self.assertEqual(recency_score(24.0), 0.0)
        self.assertEqual(recency_score(48.0), 0.0)

    def test_recency_linear(self):
        self.assertEqual(recency_score(12.0), 0.5)

    def test_recency_unknown_is_none(self):
        self.assertIsNone(recency_score(None))
        self.assertIsNone(recency_score(-1))

    def test_composite_sample(self):
        # V61 P3 修订：归一化后加权（对数归一+线性截断+二值），综合分落 [0,1]
        from holoaeon.salvage_gate import norm_value
        s = composite_score({"stars": 100, "forks": 10, "contributors": 5,
                              "citation": 1, "last_commit_months": 6})
        self.assertIsNotNone(s)
        self.assertTrue(0.0 <= s <= 1.0)
        expected = round(0.40 * norm_value("stars", 100)
                         + 0.15 * norm_value("forks", 10)
                         + 0.20 * 0.75
                         + 0.15 * norm_value("contributors", 5)
                         + 0.10 * 1.0, 4)
        self.assertEqual(s, expected)

    def test_composite_deterministic(self):
        c = {"stars": 50, "forks": 5, "contributors": 3, "citation": 0,
             "last_commit_months": 3}
        self.assertEqual(composite_score(c), composite_score(c))

    def test_composite_unknown_metric_is_none(self):
        for missing in ("stars", "forks", "contributors", "citation",
                        "last_commit_months"):
            c = {"stars": 1, "forks": 1, "contributors": 1, "citation": 1,
                 "last_commit_months": 1}
            c[missing] = None
            self.assertIsNone(composite_score(c), missing)  # 禁估算——任一未知即整体 None

    def test_hard_gate_archived_out(self):
        r = hard_gate({"archived": True, "readme_or_desc": True})
        self.assertEqual(r["verdict"], "OUT")

    def test_hard_gate_mirror_out(self):
        r = hard_gate({"is_mirror": True, "readme_or_desc": True})
        self.assertEqual(r["verdict"], "OUT")
        r2 = hard_gate({"is_fork_copy": True, "readme_or_desc": True})
        self.assertEqual(r2["verdict"], "OUT")

    def test_hard_gate_no_readme_out(self):
        r = hard_gate({"readme_or_desc": False})
        self.assertEqual(r["verdict"], "OUT")

    def test_hard_gate_license_none_demoted_not_out(self):
        r = hard_gate({"readme_or_desc": True, "license": "none"})
        self.assertEqual(r["verdict"], "KEEP")
        self.assertTrue(r["license_demoted"])  # 降权不淘汰

    def test_hard_gate_dataset_capped(self):
        r = hard_gate({"readme_or_desc": True, "obj_type": "dataset"})
        self.assertEqual(r["verdict"], "KEEP-CAPPED")  # 最多 2 席并标注类型

    def test_hard_gate_software_keep(self):
        r = hard_gate({"readme_or_desc": True, "license": "MIT"})
        self.assertEqual(r["verdict"], "KEEP")
        self.assertFalse(r["license_demoted"])

    def test_check_scoring_pass(self):
        r = check_scoring()
        self.assertTrue(r["pass"], r["problems"])


class TestPromptTemplate(unittest.TestCase):
    """五、提示词模板（变量注入+反幻觉硬约束）。"""

    def test_build_prompt_d03(self):
        p = build_prompt("D03", "2026-11-12T09:00:00")
        self.assertIn("D03", p)
        self.assertIn("holoaeon-c03-meridian", p)
        self.assertIn("agent orchestration framework routing observability", p)
        self.assertIn("2026-11-12T09:00:00", p)

    def test_build_prompt_deterministic(self):
        self.assertEqual(build_prompt("D05", "T0"), build_prompt("D05", "T0"))

    def test_prompt_antihallucination_markers(self):
        p = build_prompt("D03", "T0")
        for marker in ("不得凭记忆补全", "禁止估算填数", "不要伪造结果",
                       "search_unavailable", "unverified"):
            self.assertIn(marker, p, marker)

    def test_prompt_all_dims_injectable(self):
        for d in DIMENSIONS:
            p = build_prompt(d["dim"], "T0")
            self.assertIn(d["dim"], p)
            self.assertIn(d["main"], p)

    def test_build_prompt_unknown_dim_raises(self):
        with self.assertRaises(ValueError):
            build_prompt("D19", "T0")

    def test_prompt_has_steps_and_rules(self):
        p = build_prompt("D03", "T0")
        self.assertIn("严格按序，不得跳步", p)
        self.assertIn("压缩规则", p)

    def test_check_essence_valid(self):
        r = check_essence("基于显式状态图的编排框架。它解决自由调用不可控难回滚的问题。")
        self.assertTrue(r["pass"], r["problems"])

    def test_check_essence_too_many_sentences(self):
        r = check_essence("一。二。三。")
        self.assertFalse(r["pass"])

    def test_check_essence_too_long_sentence(self):
        r = check_essence("这是一个非常非常非常非常非常非常非常非常非常长长长长长长的句子超过四十字上限检验用例。")
        self.assertFalse(r["pass"])

    def test_check_essence_marketing_words(self):
        for w in ESSENCE_MARKETING_WORDS:
            r = check_essence("强大的{}工具。解决问题。".format(w))
            self.assertFalse(r["pass"], w)

    def test_check_template_pass(self):
        r = check_template()
        self.assertTrue(r["pass"], r["problems"])


class TestAggregate(unittest.TestCase):
    """六、180 目标汇总结构（跨维去重+验收口径）。"""

    def _result(self, **kw):
        base = {"rank": 1, "repo": "o/r", "url": "https://github.com/o/r",
                "stars": 100, "forks": 10, "last_commit": "2026-11-01",
                "contributors": 5, "license": "MIT", "language": "Python",
                "official_desc": "official", "essence": "它是什么。解决什么问题。",
                "dimension_mapping": "可吸收", "absorb_form": "架构思路",
                "reject_reason": None, "verify_status": "verified"}
        base.update(kw)
        return base

    def _record(self, **kw):
        base = {"dim_id": "D03", "cang": "holoaeon-c03-meridian",
                "snapshot_time": "T0", "queries_used": ["q"],
                "results": [self._result()], "shortfall": None}
        base.update(kw)
        return base

    def test_aggregate_required_fields(self):
        self.assertEqual(len(AGGREGATE_REQUIRED), 9)

    def test_dim_record_required_fields(self):
        self.assertEqual(len(DIM_RECORD_REQUIRED), 6)

    def test_result_required_fields(self):
        self.assertIn("verify_status", RESULT_REQUIRED)
        self.assertIn("essence", RESULT_REQUIRED)

    def test_validate_dim_record_pass(self):
        r = validate_dim_record(self._record())
        self.assertTrue(r["pass"], r["problems"])

    def test_validate_dim_record_missing_field(self):
        r = validate_dim_record(self._record(shortfall=None, snapshot_time=""))
        self.assertFalse(r["pass"])

    def test_validate_absorb_needs_form(self):
        rec = self._record()
        rec["results"][0] = self._result(absorb_form=None)
        r = validate_dim_record(rec)
        self.assertFalse(r["pass"])
        self.assertTrue(any("absorb_form" in p for p in r["problems"]))

    def test_validate_reject_needs_reason(self):
        rec = self._record()
        rec["results"][0] = self._result(dimension_mapping="需扬弃",
                                        reject_reason=None, absorb_form=None)
        r = validate_dim_record(rec)
        self.assertFalse(r["pass"])

    def test_validate_null_metric_verified_forbidden(self):
        rec = self._record()
        rec["results"][0] = self._result(stars=None)
        r = validate_dim_record(rec)
        self.assertFalse(r["pass"])
        self.assertTrue(any("verified" in p for p in r["problems"]))

    def test_validate_essence_copy_forbidden(self):
        rec = self._record()
        rec["results"][0] = self._result(essence="official")
        r = validate_dim_record(rec)
        self.assertFalse(r["pass"])
        self.assertTrue(any("照抄" in p for p in r["problems"]))

    def test_resolve_duplicates_keeps_best_score(self):
        hi = {"repo": "o/r", "dim_id": "D03", "stars": 100, "forks": 10,
              "contributors": 5, "citation": 1, "last_commit_months": 6}
        lo = {"repo": "o/r", "dim_id": "D18", "stars": 50, "forks": 5,
              "contributors": 2, "citation": 1, "last_commit_months": 6}
        r = resolve_duplicates([hi, lo])
        self.assertEqual(r["total_actual"], 1)  # 不重复计数
        self.assertEqual(r["duplicates"][0]["dims"], ["D03", "D18"])
        self.assertIn("D03", r["duplicates"][0]["resolution"])

    def test_resolve_duplicates_tie_breaks_by_dim_code(self):
        a = {"repo": "o/r", "dim_id": "D18", "stars": 10, "forks": 1,
             "contributors": 1, "citation": 1, "last_commit_months": 1}
        b = {"repo": "o/r", "dim_id": "D03", "stars": 10, "forks": 1,
             "contributors": 1, "citation": 1, "last_commit_months": 1}
        r = resolve_duplicates([a, b])
        self.assertIn("D03", r["duplicates"][0]["resolution"])  # 平分取维度编号小

    def test_resolve_duplicates_unique_kept(self):
        one = {"repo": "a/x", "dim_id": "D01", "stars": 1, "forks": 1,
               "contributors": 1, "citation": 1, "last_commit_months": 1}
        two = {"repo": "b/y", "dim_id": "D02", "stars": 1, "forks": 1,
               "contributors": 1, "citation": 1, "last_commit_months": 1}
        r = resolve_duplicates([one, two])
        self.assertEqual(r["total_actual"], 2)
        self.assertEqual(r["duplicates"], [])

    def test_resolve_duplicates_unscored_treated_last(self):
        # 综合分 None（指标未知）排末位不淘汰——有分数者为主记录
        unscored = {"repo": "o/r", "dim_id": "D03", "stars": None}
        scored = {"repo": "o/r", "dim_id": "D18", "stars": 1, "forks": 1,
                  "contributors": 1, "citation": 1, "last_commit_months": 1}
        r = resolve_duplicates([unscored, scored])
        self.assertIn("D18", r["duplicates"][0]["resolution"])


class TestSchedule(unittest.TestCase):
    """七、每天打捞日程（确定性 18 天一轮——不建 cron）。"""

    def test_d03_first(self):
        self.assertEqual(SALVAGE_ORDER[0], "D03")

    def test_cycle_eighteen(self):
        self.assertEqual(SALVAGE_CYCLE_DAYS, 18)
        self.assertEqual(len(SALVAGE_ORDER), 18)
        self.assertEqual(len(set(SALVAGE_ORDER)), 18)

    def test_day_plan_first_day_d03(self):
        p = day_plan(1)
        self.assertEqual(p["dim"], "D03")
        self.assertEqual(p["cang"], "C03")
        self.assertEqual(p["cycle_round"], 1)

    def test_day_plan_last_day_d18(self):
        self.assertEqual(day_plan(18)["dim"], "D18")

    def test_day_plan_round_two_starts_over(self):
        p = day_plan(19)
        self.assertEqual(p["cycle_round"], 2)
        self.assertEqual(p["dim"], "D03")

    def test_day_plan_invalid_raises(self):
        with self.assertRaises(ValueError):
            day_plan(0)

    def test_schedule_report_eighteen_entries(self):
        rep = schedule_report(18)
        self.assertEqual(len(rep), 18)
        self.assertEqual([p["dim"] for p in rep], list(SALVAGE_ORDER))

    def test_day_plan_deterministic(self):
        self.assertEqual(day_plan(7), day_plan(7))

    def test_check_schedule_pass(self):
        r = check_schedule()
        self.assertTrue(r["pass"], r["problems"])
        self.assertIn("不建 cron", r["cadence_note"])


class TestAssimilation(unittest.TestCase):
    """八、选择性吸纳与本地化适配（复用 V59 强制 schema 零复制）。"""

    def test_adaptation_required_fields(self):
        self.assertEqual(ADAPTATION_REQUIRED,
                         ("仓", "槽", "吸收形态", "本地化改造说明", "验证"))

    def test_validate_adaptation_pass(self):
        r = validate_adaptation({"仓": "holoaeon-c03-meridian", "槽": "L4-0",
                                 "吸收形态": "接口形态",
                                 "本地化改造说明": "取消息总线思路不改核心",
                                 "验证": "unittest 复跑"})
        self.assertTrue(r["pass"], r["problems"])

    def test_validate_adaptation_bad_slot(self):
        r = validate_adaptation({"仓": "holoaeon-c03-meridian", "槽": "L9-9",
                                 "吸收形态": "接口形态", "本地化改造说明": "x",
                                 "验证": "v"})
        self.assertFalse(r["pass"])

    def test_validate_adaptation_bad_form(self):
        r = validate_adaptation({"仓": "holoaeon-c03-meridian", "槽": "L4-0",
                                 "吸收形态": "vendoring", "本地化改造说明": "x",
                                 "验证": "v"})
        self.assertFalse(r["pass"])  # 禁 vendoring

    def test_validate_adaptation_bad_cang(self):
        r = validate_adaptation({"仓": "holoaeon-c99-unknown", "槽": "L4-0",
                                 "吸收形态": "评测方法", "本地化改造说明": "x",
                                 "验证": "v"})
        self.assertFalse(r["pass"])

    def test_validate_adaptation_missing_field(self):
        r = validate_adaptation({"仓": "holoaeon-c03-meridian", "槽": "L4-0",
                                 "吸收形态": "评测方法"})  # 缺说明与验证
        self.assertFalse(r["pass"])

    def test_slot_enrichment_plan_d03(self):
        plan = slot_enrichment_plan("D03")
        self.assertTrue(2 <= len(plan) <= 3)  # V59 认领口径
        for p in plan:
            self.assertEqual(p["仓"], "holoaeon-c03-meridian")
            self.assertIn("search_record", p["前置"])  # 无 search_record 不得进实现

    def test_slot_enrichment_plan_unknown_dim(self):
        with self.assertRaises(ValueError):
            slot_enrichment_plan("D19")

    def test_search_record_reuse_eight_fields(self):
        self.assertEqual(len(SEARCH_RECORD_REQUIRED), 8)  # V59 零复制复用

    def test_check_assimilation_pass(self):
        r = check_assimilation()
        self.assertTrue(r["pass"], r["problems"])


class TestGateCLI(unittest.TestCase):
    """九、总闸+指纹/探针/CLI。"""

    @classmethod
    def setUpClass(cls):
        cls.root = tempfile.mkdtemp(prefix="salvage_fx_")
        r = cls.root
        _mk(os.path.join(r, "打捞之王600万1331x1331超级矩阵V3实战化_20261020"))
        _mk(os.path.join(r, "账号记忆打捞1331x1331多智能体矩阵V3实战化_20261023"))
        _mk(os.path.join(r, "向量海", "打捞之王部落"))
        _mk(os.path.join(r, "向量海", "向量海结构化打捞_20260926"))
        _mk(os.path.join(r, "打捞之王定向矩阵金刚.md"), is_file=True)
        _mk(os.path.join(r, "千问端角色卡_打捞之王_V1.0_20260929.md"), is_file=True)
        _mk(os.path.join(r, "打捞600语义确认.md"), is_file=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.root, ignore_errors=True)

    def test_self_check_nine_checks_pass(self):
        # V61 修订：七检查→九检查（新增 d03_b 数据检查+patch 修订清单检查）
        g = SalvageGate(self.root)
        sc = g.self_check()
        self.assertTrue(sc["pass"], sc["problems"])
        self.assertEqual(len(sc["checks"]), 9)
        self.assertTrue(all(sc["checks"].values()))

    def test_summary_report_ring23(self):
        rep = SalvageGate(self.root).summary_report()
        self.assertEqual(rep["ring"], 23)
        self.assertEqual(rep["module"], "salvage_gate")
        self.assertEqual(rep["salvage_assets"], 10)
        self.assertEqual(rep["noun_slots"], 65)
        self.assertEqual(rep["dims"], 18)
        self.assertEqual(rep["total_expected"], 180)

    def test_fingerprint_fields(self):
        fp = fingerprint()
        self.assertEqual(fp["module"], "salvage_gate")
        self.assertEqual(fp["ring"], 23)
        self.assertEqual(fp["noun_slots"], 65)
        self.assertEqual(fp["total_expected"], 180)
        self.assertEqual(fp["cycle_days"], 18)
        self.assertEqual(len(fp["sha16"]), 16)

    def test_fingerprint_deterministic(self):
        self.assertEqual(fingerprint(), fingerprint())

    def test_probe_with_root(self):
        p = probe(self.root)
        self.assertTrue(p["self_check"]["pass"])
        self.assertEqual(p["day1_plan"]["dim"], "D03")
        self.assertIsNotNone(p["sample_score"])
        self.assertEqual(p["dedup_sample"], 1)

    def test_cli_run_with_root(self):
        from holoaeon.salvage_gate import _main
        self.assertEqual(_main(["salvage_gate", "run", "--root", self.root]), 0)

    def test_cli_probe_dims_schedule_prompt(self):
        from holoaeon.salvage_gate import _main
        for cmd in ("probe", "dims", "schedule", "prompt"):
            self.assertEqual(_main(["salvage_gate", cmd]), 0, cmd)

    def test_cli_assets_requires_root(self):
        from holoaeon.salvage_gate import _main
        self.assertEqual(_main(["salvage_gate", "assets"]), 1)  # 不在默认路径猜测

    def test_cli_assets_with_root(self):
        from holoaeon.salvage_gate import _main
        self.assertEqual(_main(["salvage_gate", "assets", "--root", self.root]), 0)


if __name__ == "__main__":
    unittest.main()
