# -*- coding: utf-8 -*-
"""test_v89_bayes_mech_matching.py · V89 贝叶斯内核机制匹配套件

五组：
  一、15 模块注册表（15/唯一/层 4-5-6/基座实现 6）
  二、机制匹配表（15 行全覆盖/锚 ⊆ 25 轴 import 对账/import 证据真解析/
     三态合法）
  三、基座既有贝叶斯族 8 符号统一账（真 import 可调零复制）
  四、18 分仓+主仓适配图（19 行/服务合法/无空仓/主仓驻地 15 全量）
  五、后验校验包（机制锚定先验/共轭方向性/三分流/实测锚真跑）
"""

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
# [V89 落盘最小修正] F1 落点在包内 holoaeon/bayes_reasoning.py；按包路径导入
# 以让包内相对 import 生效（红线口径：包内禁 `from holoaeon.*` 绝对导入）。

from holoaeon import bayes_reasoning as br  # noqa: E402


class T1Registry(unittest.TestCase):
    def test_modules_15_unique(self):
        self.assertEqual(len(br.B_MODULES), 15)
        self.assertEqual(len(set(m["id"] for m in br.B_MODULES)), 15)

    def test_layers_4_5_6(self):
        counts = {ly: sum(1 for m in br.B_MODULES if m["layer"] == ly)
                  for ly in ("light", "structure", "heavy")}
        self.assertEqual(counts, {"light": 4, "structure": 5, "heavy": 6})

    def test_implemented_six_on_base(self):
        impl = sorted(m["id"] for m in br.B_MODULES if m["implemented"])
        self.assertEqual(impl, sorted(br.B_IMPLEMENTED_ON_BASE))
        self.assertEqual(impl, ["B01", "B04", "B07", "B10", "B12", "B13"])


class T2MechMatch(unittest.TestCase):
    def test_match_rows_cover_all_modules(self):
        self.assertEqual(len(br.MECH_MATCH), 15)
        self.assertEqual({r["b"] for r in br.MECH_MATCH},
                         {m["id"] for m in br.B_MODULES})

    def test_anchors_within_25_axis(self):
        from holoaeon import meridian_link as ml
        axis = {m["id"] for m in ml.KERNEL_MECHANISMS}
        self.assertEqual(len(axis), 25)
        anchors = {a for r in br.MECH_MATCH for a in r["anchors"]}
        self.assertTrue(anchors <= axis)
        self.assertTrue(anchors)  # 非空

    def test_every_module_has_anchor(self):
        self.assertTrue(all(r["anchors"] for r in br.MECH_MATCH))

    def test_states_legal(self):
        self.assertTrue(all(r["state"] in
                            ("import-evidenced", "semantic-anchor",
                             "pending-implementation")
                            for r in br.MECH_MATCH))

    def test_import_evidence_resolvable(self):
        for r in br.MECH_MATCH:
            if r["state"] == "import-evidenced":
                self.assertTrue(r["symbols"],
                                "{} 缺 import 符号".format(r["b"]))
                for s in r["symbols"]:
                    self.assertTrue(br._resolve(s),
                                    "{} 符号不可解析: {}".format(r["b"], s))

    def test_b13_dual_kalman(self):
        r = next(x for x in br.MECH_MATCH if x["b"] == "B13")
        self.assertEqual(r["anchors"], ["R5"])
        self.assertEqual(len(r["symbols"]), 2)  # kalman_fuse + kalman_state


class T3BaseAssets(unittest.TestCase):
    def test_assets_8_resolvable(self):
        self.assertEqual(len(br.BASE_BAYES_ASSETS), 8)
        for a in br.BASE_BAYES_ASSETS:
            self.assertTrue(br._resolve(a["symbol"]),
                            "不可解析: " + a["symbol"])

    def test_assets_mechanisms_in_axis(self):
        from holoaeon import meridian_link as ml
        axis = {m["id"] for m in ml.KERNEL_MECHANISMS}
        self.assertTrue({a["mech"] for a in br.BASE_BAYES_ASSETS} <= axis)

    def test_guard_and_kalman_callable(self):
        from holoaeon.packs.topology_resonance_pack import (bayesian_guard,
                                                            kalman_state)
        self.assertTrue(callable(bayesian_guard))
        self.assertTrue(callable(kalman_state))


class T4RepoAdapters(unittest.TestCase):
    def test_adapter_rows_19(self):
        rows = br.repo_adapter_map()
        self.assertEqual(len(rows), 19)
        self.assertEqual(len(set(r["repo"] for r in rows)), 19)

    def test_adapter_from_forge_bureau(self):
        """适配图 import 对账 C18_NUMBERING——指针纪律"""
        from holoaeon.forge_bureau import C18_NUMBERING
        rows = br.repo_adapter_map()
        repos = {r["repo"] for r in rows}
        for c in C18_NUMBERING:
            self.assertIn(c["repo"], repos)

    def test_services_legal_and_nonempty(self):
        b_ids = {m["id"] for m in br.B_MODULES}
        for r in br.repo_adapter_map():
            self.assertTrue(r["services"])
            self.assertTrue(set(r["services"]) <= b_ids)

    def test_main_repo_resident_full_15(self):
        main = next(r for r in br.repo_adapter_map()
                    if r["repo_id"] == "MAIN")
        self.assertTrue(main["kernel_resident"])
        self.assertEqual(len(main["services"]), 15)

    def test_c15_risk_gets_b15_arbitration(self):
        c15 = br.REPO_SERVICES["C15"]
        self.assertIn("B15", c15)


class T5PosteriorPackage(unittest.TestCase):
    def test_package_shape(self):
        pkg = br.posterior_package("T5", {"sigma": 0.8})
        for k in ("query_id", "prior_score", "posterior_score",
                  "confidence_level", "decision", "update_policy"):
            self.assertIn(k, pkg)

    def test_mechanism_prior_not_feature_vector(self):
        """去特征向量化：先验只吃机制量化证据键"""
        pr = br.mechanism_prior({"sigma_c1": 0.9, "order_x2": 0.8})
        self.assertGreaterEqual(pr["alpha0"], 2.0 + 0.4 + 0.6)
        self.assertEqual(pr["evidence_used"],
                         ["order_x2=0.8", "sigma_c1=0.9"])

    def test_feedback_directional(self):
        good = br.posterior_package("g", {"x": 0.9}, n_success=6)
        bad = br.posterior_package("b", {"x": 0.1})
        self.assertGreater(good["posterior_score"], bad["posterior_score"])

    def test_three_way_tiers(self):
        """标定口径：三强证据→hot；单中证据→warm（(2,2) 基座拉回中位，
        弱证据不虚称 high——诚实贝叶斯）；负证据→cold"""
        tiers = {
            br.posterior_package("t", {"e1": 0.9, "e2": 0.9, "e3": 0.9})
            ["update_policy"]["tier"],
            br.posterior_package("t", {"x": 0.6})["update_policy"]["tier"],
            br.posterior_package("t", {"x": 0.2})["update_policy"]["tier"],
        }
        self.assertEqual(tiers, {"hot", "warm", "cold"})

    def test_live_anchor_evidence_real(self):
        live = br.live_anchor_evidence()
        self.assertIsInstance(live["sigma_c1"], float)
        self.assertIsInstance(live["order_x2"], float)
        pkg = br.posterior_package("live", live)
        self.assertTrue(0.0 < pkg["posterior_score"] < 1.0)

    def test_gate_pass(self):
        r = br.check_bayes_reasoning()
        self.assertEqual(r["verdict"], "PASS")
        self.assertEqual(r["failed"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
