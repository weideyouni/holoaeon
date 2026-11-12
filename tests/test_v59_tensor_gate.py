# -*- coding: utf-8 -*-
"""test_v59_tensor_gate —— V59 张量耦合与开源扬弃件真 unittest（ring22）。

八组：命名规范/语素穷举/四模态张量与确定性/耦合穷举/八层与32槽能力/
取六舍五吸收/搜索五维与 search_record/总闸+CLI。
真实数据声明：C18_NUMBERING/HUB_IDS/PHASE_GAIN 均为 V55 在仓真实注册表
（c18_cluster 实测回读）；素材口径核查三结论（零迁移/361 算术/五档复用）
以断言固化，防未来漂移。
"""

from __future__ import annotations

import math
import unittest

from holoaeon.tensor_gate import (
    ABSORBED_PATTERNS,
    ASSIMILATION_FORMS,
    CAPABILITY_SLOTS,
    CAPACITY_PER_LAYER,
    CLAIMED_LAYERS,
    DOMAIN_WORD_MEANINGS,
    DOMAIN_WORDS,
    FOUR_PART_LEDGER,
    HUB_BOOST,
    MORPHEME_KEYS,
    MORPHEME_MEANINGS,
    N19_META_DUTY,
    NAMING_PATTERN,
    OSS_LAYERS,
    REJECTED_DEPENDENCIES,
    SEARCH_DIMENSIONS,
    SEARCH_RECORD_REQUIRED,
    RepoTensor,
    TensorGate,
    batch_search_plan,
    check_capabilities,
    check_couplings,
    check_morphemes,
    claimed_slots,
    coupling,
    enumerate_couplings,
    fingerprint,
    probe,
    repo_name,
    search_plan,
    validate_repo_name,
    validate_search_record,
    w_phase,
)
from holoaeon.c18_cluster import C18_NUMBERING, HUB_IDS, PHASE_GAIN

C03 = next(c for c in C18_NUMBERING if c["id"] == "C03")
C01 = next(c for c in C18_NUMBERING if c["id"] == "C01")


def _cang(cid: str):
    return next(c for c in C18_NUMBERING if c["id"] == cid)


class TestNaming(unittest.TestCase):
    """一、命名规范（编号内嵌式——GitHub 18 仓已合规，零迁移如实声明）。"""

    def test_pattern_accepts_canonical(self):
        self.assertIsNotNone(NAMING_PATTERN.match("holoaeon-c01-source"))

    def test_pattern_rejects_legacy_name(self):
        self.assertIsNone(NAMING_PATTERN.match("holoaeon-source"))  # 旧式无编号

    def test_pattern_rejects_upper_domain(self):
        self.assertIsNone(NAMING_PATTERN.match("holoaeon-c01-Source"))

    def test_pattern_rejects_three_digit(self):
        self.assertIsNone(NAMING_PATTERN.match("holoaeon-c001-source"))

    def test_repo_name_compose(self):
        self.assertEqual(repo_name("C01", "source"), "holoaeon-c01-source")
        self.assertEqual(repo_name("C18", "cosmos"), "holoaeon-c18-cosmos")

    def test_repo_name_lowercase_id(self):
        self.assertEqual(repo_name("C03", "meridian"), "holoaeon-c03-meridian")

    def test_validate_pass(self):
        r = validate_repo_name("holoaeon-c03-meridian", "C03")
        self.assertTrue(r["pass"], r["problems"])
        self.assertEqual(r.get("number"), "03")

    def test_validate_number_mismatch(self):
        r = validate_repo_name("holoaeon-c04-meridian", "C03")
        self.assertFalse(r["pass"])
        self.assertTrue(any("编号不匹配" in p for p in r["problems"]))

    def test_validate_bad_format(self):
        r = validate_repo_name("holoaeon-meridian", "C03")
        self.assertFalse(r["pass"])
        self.assertEqual(len(r["problems"]), 1)

    def test_all_18_repo_names_pass(self):
        from holoaeon.tensor_gate import _word_of
        for c in C18_NUMBERING:
            name = repo_name(c["id"], _word_of(c["id"]))
            r = validate_repo_name(name, c["id"])
            self.assertTrue(r["pass"], "{}: {}".format(c["id"], r["problems"]))

    def test_github_slug_matches_c18_repo_field(self):
        # 在仓 c18_cluster 的 repo 字段即 GitHub 真实建仓名（V55 G-step 18/18 核验）
        for c in C18_NUMBERING:
            self.assertTrue(NAMING_PATTERN.match(c["repo"]), c["repo"])


class TestMorphemes(unittest.TestCase):
    """二、词元穷举（四语素 × 19 名 = 76 语素位）。"""

    def test_four_morpheme_keys(self):
        self.assertEqual(MORPHEME_KEYS, ("holo", "aeon", "cXX", "domain"))

    def test_morpheme_meanings_complete(self):
        self.assertEqual(set(MORPHEME_MEANINGS), set(MORPHEME_KEYS))
        for k, v in MORPHEME_MEANINGS.items():
            self.assertTrue(v.get("意义") and v.get("工程映射"), k)

    def test_18_domain_words(self):
        self.assertEqual(len(DOMAIN_WORD_MEANINGS), 18)
        self.assertEqual(len(DOMAIN_WORDS), 18)

    def test_domain_word_meanings_triple(self):
        for w, tri in DOMAIN_WORD_MEANINGS.items():
            self.assertEqual(len(tri), 3, w)  # 本义/引申/工程核心
            self.assertTrue(all(tri), w)

    def test_76_slots(self):
        r = check_morphemes()
        self.assertTrue(r["pass"], r["problems"])
        self.assertEqual(r["morpheme_slots"], 76)  # 4×19

    def test_domain_words_unique(self):
        self.assertEqual(len(set(DOMAIN_WORDS)), 18)  # 语义无重复


class TestRepoTensor(unittest.TestCase):
    """三、四模态张量 T(c)=⟨S,M,P,A⟩ 与确定性。"""

    def setUp(self):
        self.t = RepoTensor()

    def test_modal_s_dim8_and_range(self):
        v = self.t.modal_s(C01)
        self.assertEqual(len(v), 8)
        for x in v:
            self.assertTrue(-1.0 <= x <= 1.0, x)

    def test_modal_s_deterministic(self):
        self.assertEqual(self.t.modal_s(C01), self.t.modal_s(C01))

    def test_modal_s_differs_across_cangs(self):
        ids = [c["id"] for c in C18_NUMBERING[:4]]
        vecs = [tuple(self.t.modal_s(_cang(i))) for i in ids]
        self.assertEqual(len(set(vecs)), len(vecs))  # 仓仓不同可寻址

    def test_modal_m_dim1024(self):
        self.assertEqual(len(self.t.modal_m(C01)), 1024)

    def test_modal_m_no_random_init(self):
        # 同输入必得同向量——两次独立计算全同（M 无随机初始化机器证明）
        self.assertEqual(self.t.modal_m(C01), self.t.modal_m(C01))

    def test_modal_m_differs_across_cangs(self):
        a, b = self.t.modal_m(_cang("C02")), self.t.modal_m(_cang("C15"))
        self.assertNotEqual(a, b)

    def test_modal_p_non_hub_dim10(self):
        v = self.t.modal_p(_cang("C02"))
        self.assertEqual(len(v), 10)
        self.assertNotIn(_cang("C02")["id"], HUB_IDS)

    def test_modal_p_hub_dim11_with_marker(self):
        v = self.t.modal_p(C03)
        self.assertEqual(len(v), 11)
        self.assertEqual(v[10], HUB_BOOST)  # 枢纽标记独立第 11 位

    def test_modal_p_sub_one_hot(self):
        v = self.t.modal_p(C03)
        self.assertEqual(sum(v[5:10]), 1.0)  # 副相位 one-hot（C03 副相位=水）
        self.assertEqual(v[5 + ("木", "火", "土", "金", "水").index(C03["phase_sub"])], 1.0)

    def test_modal_a_dim32(self):
        self.assertEqual(len(self.t.modal_a(C01)), 32)

    def test_modal_a_claimed_slots_set(self):
        slots = claimed_slots("C01")  # L7-0, L4-0
        v = self.t.modal_a(C01)
        for s in slots:
            layer, idx = int(s.split("-")[0][1:]), int(s.split("-")[1])
            self.assertEqual(v[layer * 4 + idx], 1.0, s)

    def test_modal_a_unclaimed_slots_zero(self):
        v = self.t.modal_a(C01)
        set_bits = [i for i, x in enumerate(v) if x == 1.0]
        self.assertEqual(len(set_bits), len(claimed_slots("C01")))  # 零虚构：未认领即零

    def test_tensor_four_modalities(self):
        self.assertEqual(set(self.t.tensor(C01)), {"S", "M", "P", "A"})

    def test_tensor_deterministic_all_cangs(self):
        for c in C18_NUMBERING:
            self.assertTrue(self.t.tensor_deterministic(c), c["id"])

    def test_determinism_across_instances(self):
        # 两个独立 RepoTensor 实例同输入同张量（sha256 派生全链确定性）
        t2 = RepoTensor()
        self.assertEqual(self.t.tensor(C03), t2.tensor(C03))

    def test_semantic_similarity_self_is_one(self):
        sim = self.t.semantic_similarity(C01, C01)
        self.assertTrue(math.isclose(sim, 1.0, abs_tol=1e-9), sim)

    def test_semantic_similarity_symmetric(self):
        a = self.t.semantic_similarity(_cang("C02"), _cang("C10"))
        b = self.t.semantic_similarity(_cang("C10"), _cang("C02"))
        self.assertTrue(math.isclose(a, b, abs_tol=1e-9))


class TestCouplings(unittest.TestCase):
    """四、双仓耦合 C(i,j)：361 单元全量穷举（素材算术澄清固化）。"""

    def test_w_phase_ke_control(self):
        # C02(水)→C10(火)：相克 0.6（素材口径复检值）
        self.assertEqual(w_phase("C02", "C10"), 0.6)

    def test_w_phase_hub_boost(self):
        # C03 枢纽任一端乘 HUB_BOOST：同气基数 1.0×1.5=1.5
        self.assertEqual(w_phase("C03", "C07"), 1.5)

    def test_w_phase_self_same_qi(self):
        self.assertEqual(w_phase("C01", "C01"), 1.0)  # 自耦同气 1.0 非枢纽

    def test_w_phase_uses_repo_phase_gain_five(self):
        # 复用在仓五档 PHASE_GAIN（含被生——素材漏档 V55 已补）不覆写
        self.assertEqual(len(PHASE_GAIN), 5)
        self.assertIn("被生", PHASE_GAIN)
        self.assertEqual(PHASE_GAIN["相生"], 1.2)

    def test_w_phase_hub_boost_constant(self):
        self.assertEqual(HUB_BOOST, 1.5)  # 素材新采信项单列，不覆写 PHASE_GAIN

    def test_w_phase_unknown_endpoint_raises(self):
        with self.assertRaises(ValueError):
            w_phase("C99", "C01")

    def test_w_phase_n19_accepted(self):
        self.assertIsInstance(w_phase("N19", "C01"), float)  # N19 土相位入域

    def test_coupling_record_fields(self):
        r = coupling("C02", "C10")
        self.assertEqual(set(r), {"i", "j", "w_phase", "semantic_cos", "value"})
        self.assertTrue(-1.0 <= r["semantic_cos"] <= 1.0)
        self.assertTrue(math.isclose(r["value"], round(r["w_phase"] * r["semantic_cos"], 4), abs_tol=1e-4))

    def test_coupling_n19_semantic_is_one(self):
        # N19 无语义向量条目（元职责仓），semantic_cos 诚实置 1.0 不虚构
        r = coupling("N19", "C05")
        self.assertEqual(r["semantic_cos"], 1.0)

    def test_enumerate_361_units(self):
        r = enumerate_couplings()
        self.assertEqual(r["total"], 361)  # 19 自耦+342 有向

    def test_enumerate_counts(self):
        r = enumerate_couplings()
        self.assertEqual(r["self_count"], 19)
        self.assertEqual(r["directed_count"], 342)
        self.assertEqual(r["undirected_view"], 171)  # 对称压缩视图不重复计数

    def test_enumerate_units_len_matches_total(self):
        r = enumerate_couplings()
        self.assertEqual(len(r["units"]), 361)

    def test_check_couplings_pass(self):
        r = check_couplings()
        self.assertTrue(r["pass"], r["problems"])
        self.assertEqual(r["total"], 361)
        self.assertEqual(r["undirected"], 171)


class TestCapabilities(unittest.TestCase):
    """五、八层开源分类 + 32 能力槽 + 18 仓认领。"""

    def test_eight_layers_l0_to_l7(self):
        self.assertEqual(len(OSS_LAYERS), 8)
        self.assertEqual([l[0] for l in OSS_LAYERS],
                         ["L{}".format(i) for i in range(8)])

    def test_layer_triples_nonempty(self):
        for code, name, core in OSS_LAYERS:
            self.assertTrue(code and name and core, code)

    def test_32_slots(self):
        self.assertEqual(len(CAPABILITY_SLOTS), 32)
        self.assertEqual(CAPACITY_PER_LAYER, 4)

    def test_slot_ids_format(self):
        for s in CAPABILITY_SLOTS:
            self.assertRegex(s, r"^L[0-7]-[0-3]$")

    def test_slots_unique(self):
        self.assertEqual(len(set(CAPABILITY_SLOTS)), 32)

    def test_claimed_layers_18_repos(self):
        self.assertEqual(len(CLAIMED_LAYERS), 18)

    def test_claimed_layers_only_valid_codes(self):
        valid = {l[0] for l in OSS_LAYERS}
        for cid, layers in CLAIMED_LAYERS.items():
            self.assertTrue(layers, cid)
            for l in layers:
                self.assertIn(l, valid, "{}:{}".format(cid, l))

    def test_claimed_slots_are_first_slot_of_layer(self):
        for cid in CLAIMED_LAYERS:
            for s in claimed_slots(cid):
                self.assertTrue(s.endswith("-0"), s)  # 槽内细分待 search_record

    def test_n19_meta_duty_declared(self):
        self.assertIn("全层元职责", N19_META_DUTY)

    def test_check_capabilities_pass(self):
        r = check_capabilities()
        self.assertTrue(r["pass"], r["problems"])
        self.assertEqual(r["slots"], 32)
        self.assertEqual(r["layers"], 8)


class TestAbsorption(unittest.TestCase):
    """六、开源扬弃：取六条 / 舍五条 / 同化三形态 / 四段台账。"""

    def test_absorbed_six(self):
        self.assertEqual(len(ABSORBED_PATTERNS), 6)

    def test_absorbed_pairs_nonempty(self):
        for name, assim in ABSORBED_PATTERNS:
            self.assertTrue(name and assim)

    def test_absorbed_no_runtime_import(self):
        # 只取思维模型不取实现——吸收条目不得引入 vendoring 词
        joined = " ".join(a for _, a in ABSORBED_PATTERNS)
        self.assertNotIn("vendor", joined.lower())

    def test_rejected_five(self):
        self.assertEqual(len(REJECTED_DEPENDENCIES), 5)

    def test_rejected_reasons_nonempty(self):
        for name, reason in REJECTED_DEPENDENCIES:
            self.assertTrue(name and reason)

    def test_rejected_covers_determinism(self):
        joined = " ".join(n for n, _ in REJECTED_DEPENDENCIES)
        self.assertIn("非确定性", joined)  # 护同任务两次哈希一致

    def test_assimilation_three_forms(self):
        self.assertEqual(ASSIMILATION_FORMS, ("思维模型", "接口形态", "评测方法"))

    def test_four_part_ledger(self):
        self.assertEqual(FOUR_PART_LEDGER, ("来源", "吸收形态", "改造说明", "拒绝项"))


class TestSearchGuide(unittest.TestCase):
    """七、搜索引导五维 D1-D5 + search_record 强制 schema。"""

    def test_five_dimensions(self):
        self.assertEqual(len(SEARCH_DIMENSIONS), 5)
        self.assertEqual([d[0] for d in SEARCH_DIMENSIONS],
                         ["D1", "D2", "D3", "D4", "D5"])

    def test_dimension_quadruples_nonempty(self):
        for code, name, ask, query in SEARCH_DIMENSIONS:
            self.assertTrue(code and name and ask and query, code)

    def test_search_plan_c03_five_tasks(self):
        plan = search_plan("C03")
        self.assertEqual(len(plan), 5)
        self.assertEqual([p["维度"] for p in plan],
                         ["D1", "D2", "D3", "D4", "D5"])

    def test_search_plan_repo_name_embedded(self):
        for p in search_plan("C03"):
            self.assertEqual(p["仓"], "holoaeon-c03-meridian")
            self.assertIn("meridian", p["查询"])

    def test_search_plan_unknown_cang_raises(self):
        with self.assertRaises(ValueError):
            search_plan("C99")

    def test_batch_plan_integrates_v58_batches(self):
        b = batch_search_plan()
        self.assertEqual(b["batches"], 7)  # B0-B6 复用 V58 DEEPENING_BATCHES
        self.assertEqual(b["cang_plans"], 18)
        self.assertEqual(b["tasks"], 90)  # 18 仓×5 维

    def test_record_required_fields(self):
        self.assertEqual(SEARCH_RECORD_REQUIRED,
                         ("仓", "维度", "查询", "命中", "取", "舍", "同化形态", "验证"))

    def test_validate_record_pass(self):
        rec = {"仓": "holoaeon-c03-meridian", "维度": "D2", "查询": "meridian 开源 项目 能力 对比",
               "命中": "3 条", "取": "分层决策树思路", "舍": "重依赖实现",
               "同化形态": "思维模型", "验证": "unittest 复跑"}
        r = validate_search_record(rec)
        self.assertTrue(r["pass"], r["problems"])

    def test_validate_record_missing_field(self):
        rec = {"仓": "holoaeon-c03-meridian", "维度": "D2", "查询": "q", "命中": "h",
               "取": "t", "舍": "s", "同化形态": "思维模型"}  # 缺"验证"
        r = validate_search_record(rec)
        self.assertFalse(r["pass"])
        self.assertTrue(any("验证" in p for p in r["problems"]))

    def test_validate_record_empty_take_or_give(self):
        # "取/舍"缺一即未做扬弃——空值即拒（素材 6.4 强制）
        base = {"仓": "holoaeon-c03-meridian", "维度": "D2", "查询": "q", "命中": "h",
                "取": "t", "舍": "", "同化形态": "思维模型", "验证": "v"}
        r = validate_search_record(base)
        self.assertFalse(r["pass"])

    def test_validate_record_bad_dimension(self):
        rec = {"仓": "holoaeon-c03-meridian", "维度": "D9", "查询": "q", "命中": "h",
               "取": "t", "舍": "s", "同化形态": "思维模型", "验证": "v"}
        r = validate_search_record(rec)
        self.assertFalse(r["pass"])
        self.assertTrue(any("D1-D5" in p for p in r["problems"]))

    def test_validate_record_bad_repo_name(self):
        rec = {"仓": "holoaeon-meridian", "维度": "D2", "查询": "q", "命中": "h",
               "取": "t", "舍": "s", "同化形态": "思维模型", "验证": "v"}
        r = validate_search_record(rec)
        self.assertFalse(r["pass"])


class TestGateCLI(unittest.TestCase):
    """八、总闸 TensorGate + 指纹/探针/CLI。"""

    def test_self_check_five_checks_all_pass(self):
        g = TensorGate()
        sc = g.self_check()
        self.assertTrue(sc["pass"], sc["problems"])
        self.assertEqual(set(sc["checks"]),
                         {"naming", "morphemes", "tensor", "couplings", "capabilities"})
        self.assertTrue(all(sc["checks"].values()))

    def test_summary_report_ring22(self):
        rep = TensorGate().summary_report()
        self.assertEqual(rep["ring"], 22)
        self.assertEqual(rep["module"], "tensor_gate")
        self.assertEqual(rep["morpheme_slots"], 76)
        self.assertEqual(rep["coupling_units"], 361)
        self.assertEqual(rep["capability_slots"], 32)
        self.assertEqual(rep["absorbed"], 6)
        self.assertEqual(rep["rejected"], 5)
        self.assertEqual(rep["search_dimensions"], 5)

    def test_fingerprint_fields(self):
        fp = fingerprint()
        self.assertEqual(fp["module"], "tensor_gate")
        self.assertEqual(fp["ring"], 22)
        self.assertEqual(fp["morpheme_slots"], 76)
        self.assertEqual(fp["coupling_units"], 361)
        self.assertEqual(fp["capability_slots"], 32)
        self.assertEqual(fp["layers"], 8)
        self.assertEqual(len(fp["sha16"]), 16)

    def test_fingerprint_deterministic(self):
        self.assertEqual(fingerprint(), fingerprint())

    def test_probe_keys(self):
        p = probe()
        self.assertEqual(set(p), {"fingerprint", "self_check", "determinism_proof",
                                  "sample_coupling", "sample_hub_coupling",
                                  "c03_search_first2"})
        self.assertTrue(p["determinism_proof"])

    def test_probe_hub_coupling_boosted(self):
        self.assertEqual(probe()["sample_hub_coupling"]["w_phase"], 1.5)

    def test_cli_five_commands(self):
        from holoaeon.tensor_gate import _main
        for cmd in ("run", "probe", "couplings", "capabilities", "search"):
            self.assertEqual(_main(["tensor_gate", cmd]), 0, cmd)


if __name__ == "__main__":
    unittest.main()
