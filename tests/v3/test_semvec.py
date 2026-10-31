# -*- coding: utf-8 -*-
"""v3 单测：semvec 确定性表征。放在独立目录，保持 tests/ 顶层仍为 34 项。"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from holoaeon.kernel import Kernel  # noqa: E402
from holoaeon.packs import PACK_ORDER, get_pack  # noqa: E402
from holoaeon.semvec import SemanticIndex, docs_from_skills, tokenize  # noqa: E402


def corpus() -> list:
    k = Kernel()
    for key in PACK_ORDER:
        get_pack(key).install(k)
    return docs_from_skills(k.skills.all())


class TestSemvec(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.texts = corpus()
        cls.idx = SemanticIndex()
        cls.idx.fit(cls.texts)

    def test_tokenize_lexicon(self):
        toks = tokenize("患者数据统计")
        self.assertIn("stats", toks)
        self.assertIn("data", toks)
        self.assertIn("subject", toks)

    def test_fit_deterministic(self):
        other = SemanticIndex()
        other.fit(self.texts)
        self.assertEqual(self.idx.vocab, other.vocab)
        self.assertEqual(self.idx.vectors, other.vectors)

    def test_encode_unit_norm(self):
        vec = self.idx.encode("统计字数")
        norm = sum(x * x for x in vec) ** 0.5
        self.assertAlmostEqual(norm, 1.0, places=6)

    def test_similar_self_is_one(self):
        self.assertAlmostEqual(self.idx.similar("统计字数", "统计字数"), 1.0, places=6)

    def test_vocab_bound(self):
        self.assertLess(len(self.idx.vocab), 5000)
        self.assertTrue(self.idx.vectors)


if __name__ == "__main__":
    unittest.main()
