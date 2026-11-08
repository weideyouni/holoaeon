# -*- coding: utf-8 -*-
"""V44 双轨核对引擎测试。零依赖，确定性断言。"""
import unittest

from holoaeon import twin_verify as tv
from holoaeon.hypervector import HypervectorConfig, HypervectorSpace
from holoaeon.phc_recall import embed


def _space():
    return HypervectorSpace(HypervectorConfig(dim=256))


def _fp(results, nbytes, digest):
    return tv.fingerprint(results, nbytes, digest)


SHA1 = "a" * 64
SHA2 = "b" * 64


class TestTwinVerify(unittest.TestCase):
    def test_chain_position(self):
        self.assertEqual(tv.CHAIN_POSITION["ring"], 12)
        self.assertEqual(tv.CHAIN_POSITION["layer"], "verify（双轨核对层）")

    def test_seal(self):
        self.assertEqual(tv.SEAL, "潮起开门，潮落闭嘴")

    def test_axiom(self):
        self.assertIn("正交", tv.TWIN_AXIOM)
        self.assertIn("全息通过", tv.TWIN_AXIOM)

    def test_fingerprint_deterministic(self):
        a = _fp(3205, 63, SHA1)
        b = _fp(3205, 63, SHA1)
        self.assertEqual(a, b)
        self.assertEqual(a["results"], 3205)
        self.assertEqual(a["bytes"], 63)

    def test_fingerprint_rejects_bad(self):
        self.assertFalse(_fp(-1, 63, SHA1)["ok"])
        self.assertFalse(_fp(10, 63, "short")["ok"])

    def test_exact_track_match_and_diff(self):
        ok = tv.exact_track(_fp(3205, 63, SHA1), _fp(3205, 63, SHA1))
        self.assertTrue(ok["matched"])
        bad = tv.exact_track(_fp(3205, 63, SHA1), _fp(3204, 63, SHA2))
        self.assertFalse(bad["matched"])
        self.assertIn("results", bad["diffs"])
        self.assertIn("digest", bad["diffs"])

    def test_resemblance_identical_text(self):
        r = tv.resemblance_track(_space(), "贪吃蛇网页游戏 玩法 配色",
                                 "贪吃蛇网页游戏 玩法 配色")
        self.assertEqual(r["sim"], 1.0)

    def test_resemblance_similar_beats_unrelated(self):
        sp = _space()
        close = tv.resemblance_track(sp, "冠心病 胸闷 心悸",
                                     "患者胸闷 心前区不适 心悸")
        far = tv.resemblance_track(sp, "冠心病 胸闷 心悸",
                                   "腰椎间盘突出 下肢放射痛")
        self.assertGreater(close["sim"], far["sim"])

    def test_resemblance_rejects_pixels(self):
        r = tv.resemblance_track(_space(), b"\x89PNG", "特征")
        self.assertFalse(r["ok"])
        self.assertIn("零像素", r["error"])

    def test_resemblance_coverage(self):
        r = tv.resemblance_track(_space(), "特征集", "特征集",
                                 checklist=["玩法", "计分", "配色"],
                                 matched=["玩法", "配色"])
        self.assertAlmostEqual(r["coverage"], 0.6667, places=3)

    def test_verdict_pass(self):
        v = tv.twin_verdict({"matched": True}, {"sim": 0.95})
        self.assertEqual(v["verdict"], "PASS")

    def test_verdict_correct_but_unlike(self):
        v = tv.twin_verdict({"matched": True}, {"sim": 0.5})
        self.assertEqual(v["verdict"], "CORRECT_BUT_UNLIKE")
        self.assertIn("refine", v["dispositions"]["CORRECT_BUT_UNLIKE"])

    def test_verdict_faithful_but_wrong(self):
        v = tv.twin_verdict({"matched": False}, {"sim": 0.95})
        self.assertEqual(v["verdict"], "FAITHFUL_BUT_WRONG")
        self.assertIn("复算", v["dispositions"]["FAITHFUL_BUT_WRONG"])

    def test_verdict_fail(self):
        v = tv.twin_verdict({"matched": False}, {"sim": 0.3})
        self.assertEqual(v["verdict"], "FAIL")

    def test_no_blended_score(self):
        v = tv.twin_verdict({"matched": True}, {"sim": 0.9})
        self.assertIsNone(v["blended_score"])  # 正交不标量压缩

    def test_coverage_shortboard_rule(self):
        # sim 高但 coverage 低 → 短板决定 like → 走样
        v = tv.twin_verdict({"matched": True},
                            {"sim": 0.99, "coverage": 0.5})
        self.assertEqual(v["verdict"], "CORRECT_BUT_UNLIKE")

    def test_audit_trail_chain_and_tamper(self):
        t = tv.AuditTrail()
        t.add("check1", "exact")
        t.add("check2", "resemblance")
        self.assertTrue(t.verify()["ok"])
        t.entries[0]["event"] = "TAMPERED"
        self.assertFalse(t.verify()["ok"])

    def test_verify_twin_end_to_end_pass(self):
        r = tv.verify_twin(_space(),
                           _fp(3205, 63, SHA1), _fp(3205, 63, SHA1),
                           "贪吃蛇网页游戏 玩法 配色",
                           "贪吃蛇网页游戏 玩法 配色",
                           checklist=["玩法", "配色"], matched=["玩法", "配色"])
        self.assertEqual(r["verdict"], "PASS")
        self.assertIsNone(r["blended_score"])

    def test_verify_twin_end_to_end_wrong(self):
        r = tv.verify_twin(_space(),
                           _fp(3205, 63, SHA1), _fp(3204, 63, SHA1),
                           "特征A 特征B", "特征A 特征B")
        self.assertEqual(r["verdict"], "FAITHFUL_BUT_WRONG")
        self.assertIn("复算", r["disposition"])

    def test_verify_twin_with_trail(self):
        t = tv.AuditTrail()
        tv.verify_twin(_space(), _fp(1, 1, SHA1), _fp(1, 1, SHA1),
                       "x", "x", trail=t)
        self.assertTrue(t.verify()["ok"])

    def test_audit_snapshot(self):
        s = tv.audit()
        self.assertTrue(s["zero_pixel"])
        self.assertTrue(s["no_blended_score"])
        self.assertFalse(s["neural"])
        self.assertIn("phc_recall.embed", s["reused"])
        self.assertIn("craft_gate.similarity_score", s["reused"])


if __name__ == "__main__":
    unittest.main()
