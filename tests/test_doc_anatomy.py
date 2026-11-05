# -*- coding: utf-8 -*-
"""V30 文档解剖器测试（18 例）。

构造最小合法 PDF（对象用正则扫描，不依赖 xref），覆盖：
tokenizer / 位置 / TJ / Td·T* / 多页 / FlateDecode /
分类四态 / Markdown 四级标题·粗体·等宽·列表·链接 / 表格双模 / inspect 汇总。
"""
import unittest
import zlib

from holoaeon.doc_anatomy import (AXIOMS, CHAIN_POSITION, MECHANISMS, SCHEMA_VERSION,
                                  classify, detect_tables, extract, inspect,
                                  parse_content, to_markdown, tokenize)
from holoaeon.machine_tool import SEAL


def _pdf(contents, extra=()):
    """contents: 内容流字符串，或 (内容, True) 表示 FlateDecode 压缩。"""
    objs = ["1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj"]
    kids = " ".join("%d 0 R" % (3 + 2 * i) for i in range(len(contents)))
    objs.append("2 0 obj << /Type /Pages /Kids [%s] /Count %d >> endobj"
                % (kids, len(contents)))
    for i, content in enumerate(contents):
        page_no = 3 + 2 * i
        cont_no = page_no + 1
        objs.append("%d 0 obj << /Type /Page /Parent 2 0 R /Contents %d 0 R >> endobj"
                    % (page_no, cont_no))
        if isinstance(content, tuple):
            raw = zlib.compress(content[0].encode("latin-1"))
            objs.append("%d 0 obj << /Length %d /Filter /FlateDecode >>\nstream\n%s\n"
                        "endstream endobj" % (cont_no, len(raw), raw.decode("latin-1")))
        else:
            objs.append("%d 0 obj << /Length %d >>\nstream\n%s\nendstream endobj"
                        % (cont_no, len(content), content))
    objs.extend(list(extra))
    return ("%PDF-1.4\n" + "\n".join(objs) + "\ntrailer << /Root 1 0 R >>\n%%EOF\n"
            ).encode("latin-1")


def _span(text, x, y, size=10.0, font="Helv", page=1):
    return {"text": text, "x": x, "y": y, "size": size, "font": font, "page": page}


class TestTokenizer(unittest.TestCase):
    def test_literal_escape_and_hex(self):
        toks = tokenize(r"(A\(B\)C) Tj <48656C6C6F> Tj 1.5 0 0 1 10 20 Tm")
        texts = [v for k, v in toks if k == "str"]
        self.assertEqual(texts[0], "A(B)C")
        self.assertEqual(texts[1], "Hello")
        nums = [v for k, v in toks if k == "num"]
        self.assertEqual(nums[:2], [1.5, 0])

    def test_nested_paren_and_octal(self):
        toks = tokenize(r"(x(y)z\101)")
        self.assertEqual(toks[0][1], "x(y)zA")


class TestParseContent(unittest.TestCase):
    def test_tm_position_and_size(self):
        result = parse_content("BT /F1 24 Tf 1 0 0 1 72 700 Tm (Title) Tj ET")
        self.assertEqual(len(result["spans"]), 1)
        span = result["spans"][0]
        self.assertEqual(span["text"], "Title")
        self.assertEqual(span["x"], 72.0)
        self.assertEqual(span["y"], 700.0)
        self.assertEqual(span["size"], 24.0)
        self.assertEqual(span["font"], "F1")

    def test_tj_array_concatenation(self):
        result = parse_content(
            "BT /F1 12 Tf 1 0 0 1 72 700 Tm [(Hel) -20 (lo)] TJ ET")
        self.assertEqual(result["spans"][0]["text"], "Hello")

    def test_td_and_tstar_leading(self):
        result = parse_content(
            "BT /F1 12 Tf 14 TL 72 700 Td (one) Tj T* (two) Tj ET")
        self.assertEqual([s["text"] for s in result["spans"]], ["one", "two"])
        self.assertAlmostEqual(result["spans"][1]["y"], 686.0, places=2)


class TestDocument(unittest.TestCase):
    def test_multipage(self):
        data = _pdf(["BT /F1 12 Tf 72 700 Td (page one) Tj ET",
                     "BT /F1 12 Tf 72 700 Td (page two) Tj ET"])
        info = extract(data)
        self.assertEqual(info["pages"], 2)
        self.assertEqual([s["page"] for s in info["spans"]], [1, 2])

    def test_flate_decode(self):
        data = _pdf([("BT /F1 12 Tf 72 700 Td (compressed words) Tj ET", True)])
        info = extract(data)
        self.assertEqual(info["spans"][0]["text"], "compressed words")
        self.assertEqual(info["status"], "ok")

    def test_font_alias_resolved(self):
        data = ("%PDF-1.4\n"
                "1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
                "2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
                "3 0 obj << /Type /Page /Parent 2 0 R /Contents 4 0 R "
                "/Resources << /Font << /F9 5 0 R >> >> >> endobj\n"
                "4 0 obj << /Length 46 >>\nstream\n"
                "BT /F9 10 Tf 72 700 Td (code) Tj ET\n"
                "endstream endobj\n"
                "5 0 obj << /Type /Font /BaseFont /Courier >> endobj\n"
                "%%EOF\n").encode("latin-1")
        info = extract(data)
        self.assertEqual(info["spans"][0]["font"], "Courier")
        self.assertIn("```", to_markdown(info["spans"]))


class TestClassify(unittest.TestCase):
    def test_text_based(self):
        long_line = "A" * 300
        data = _pdf(["BT /F1 12 Tf 72 700 Td (%s) Tj ET" % long_line])
        verdict = classify(data)
        self.assertEqual(verdict["kind"], "text")
        self.assertFalse(verdict["ocr_needed"])
        self.assertAlmostEqual(verdict["confidence"], 0.75, places=3)

    def test_scanned(self):
        data = _pdf(["BT ET"])
        verdict = classify(data)
        self.assertEqual(verdict["kind"], "scanned")
        self.assertTrue(verdict["ocr_needed"])
        self.assertEqual(verdict["chars"], 0)

    def test_image_or_mixed(self):
        image = "5 0 obj << /Type /XObject /Subtype /Image /Width 10 /Height 10 >> endobj"
        data = _pdf(["BT /F1 12 Tf 72 700 Td (%s) Tj ET" % ("B" * 50)], extra=[image])
        verdict = classify(data)
        self.assertEqual(verdict["kind"], "mixed")
        # 有文本层（50 字）+ 图 → mixed，但不需要 OCR：只是版式混合，不是无字
        self.assertFalse(verdict["ocr_needed"])


class TestMarkdown(unittest.TestCase):
    def test_heading_levels(self):
        spans = [_span("Big Title", 72, 760, 24),
                 _span("Section", 72, 720, 18),
                 _span("body text here", 72, 690, 10)]
        markdown = to_markdown(spans)
        self.assertIn("# Big Title", markdown)
        self.assertIn("## Section", markdown)
        self.assertIn("body text here", markdown)

    def test_bold_and_mono(self):
        spans = [_span("bold line", 72, 700, 10, "Helvetica-Bold"),
                 _span("code one", 72, 680, 10, "Courier"),
                 _span("code two", 72, 670, 10, "Courier")]
        markdown = to_markdown(spans)
        self.assertIn("**bold line**", markdown)
        self.assertEqual(markdown.count("```"), 2)
        self.assertIn("code one", markdown)

    def test_list_and_link(self):
        spans = [_span("- first item", 72, 700),
                 _span("1. second item", 72, 690),
                 _span("see https://example.com/a now", 72, 680)]
        markdown = to_markdown(spans)
        self.assertIn("- first item", markdown)
        self.assertIn("1. second item", markdown)
        self.assertIn("[https://example.com/a](https://example.com/a)", markdown)


class TestTables(unittest.TestCase):
    def test_alignment_mode(self):
        spans = []
        for row in range(3):
            y = 700 - row * 20
            spans.append(_span("row%d-a" % row, 72, y))
            spans.append(_span("row%d-b" % row, 200, y))
        tables = detect_tables(spans, [])
        self.assertEqual(len(tables), 1)
        self.assertEqual(tables[0]["mode"], "alignment")
        self.assertEqual(tables[0]["rows"], 3)
        self.assertEqual(tables[0]["cols"], 2)
        self.assertEqual(tables[0]["cells"][0][0], "row0-a")

    def test_rect_mode(self):
        rects = []
        for row in range(3):
            y = 700 - row * 20
            rects.append({"x": 72, "y": y, "w": 100, "h": 18, "page": 1})
            rects.append({"x": 200, "y": y, "w": 100, "h": 18, "page": 1})
        tables = detect_tables([], rects)
        self.assertEqual(len(tables), 1)
        self.assertEqual(tables[0]["mode"], "rect")
        self.assertEqual(tables[0]["rows"], 3)
        self.assertEqual(tables[0]["cols"], 2)


class TestInspect(unittest.TestCase):
    def test_summary_contract(self):
        data = _pdf(["BT /F1 12 Tf 72 700 Td (%s) Tj ET" % ("C" * 250)])
        result = inspect(data)
        self.assertTrue(result["ok"])
        self.assertEqual(result["schema"], SCHEMA_VERSION)
        self.assertEqual(result["seal"], SEAL)
        self.assertEqual(result["chain_position"]["ring"], 4)
        self.assertEqual(result["chain_position"]["name"], "解剖")
        self.assertEqual(result["classify"]["kind"], "text")
        self.assertEqual(result["pages"], 1)

        # 清空数据 → 诚实降级，不编造内容
        empty = inspect(b"%PDF-1.4\n%%EOF\n")
        self.assertEqual(empty["classify"]["kind"], "scanned")
        self.assertTrue(empty["classify"]["ocr_needed"])
        self.assertEqual(empty["markdown_chars"], 0)


class TestContracts(unittest.TestCase):
    def test_chain_and_mechanisms(self):
        self.assertEqual(len(MECHANISMS), 11)
        self.assertEqual(len(AXIOMS), 2)
        self.assertEqual(CHAIN_POSITION["upstream"],
                         ("mobius_vortex", "klein_projection", "holo_forge"))
        self.assertEqual(SEAL, "潮起开门，潮落闭嘴")


if __name__ == "__main__":
    unittest.main()
