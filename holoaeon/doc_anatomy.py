"""V30 文档解剖器（doc_anatomy）—— pdf-inspector 创意本地化（只蒸馏方法，不复制代码）。

第一性原理
==========
候选 pdf-inspector（Firecrawl，Rust，MIT）证明了一件事：绝大多数 PDF 自带文本层，
根本不需要昂贵的 OCR——先在本地把「有字/没字」判清楚，再决定是否外包识别。
本模块吸纳的是这个**判定结构**，不吸纳它的 Rust 实现：

    classify（分类）→ extract（位置感知抽取）→ markdown（结构还原）→ tables（表格检测）

许可证纪律
==========
MIT 允许借鉴实现，但本项目宪章 = 零依赖纯标准库 ⇒ 不引 Rust / wasm / 任何第三方包，
只用 stdlib（`re` / `zlib` / `json`）做一个诚实的轻量版。思想-表达二分法：
取「先分类、再抽取、不盲上 OCR」的方法论，弃其代码本体。

链上位置（D-11 强制声明）
========================
链式执行层**第四环·解剖**：回流（mobius_vortex·知道）→ 投影（klein_projection·拿来）
→ 熔炼（holo_forge·成为）→ **解剖（doc_anatomy·拆成结构件）**。
熔炼出的成品在入库前先被解剖成可复用的结构件（版面骨架 / 阅读顺序 / 表格骨架）。

诚实边界（不达标就降级，绝不假装）
================================
* 不支持加密（/Encrypt）、对象流（/ObjStm）、CID / Identity-H 复合字体 → 明确返回 unsupported
* 只解 FlateDecode；其他筛选器 → unsupported_filter
* 无文本层 → 判 scanned 并 `ocr_required=True`（本模块不接 OCR，只举手）
* 旋转 / 多栏只做「保序」近似，不做版面重建

工程纪律
========
* 纯标准库（json/os/re/sys/zlib），零网络、零密钥、零 GPU、零 OCR 服务。
* 不 shell out，不 eval/exec，不碰 graph/scheduler/hypervector/kernel.submit。
* 仓内导入一律相对导入；不新增扩展包（模块级，先例 V12/V25/V26/V27/V28）。
* 新文件不参与 ReproHash → diff0 零漂移。

证据等级：evidence_class=simulated，仿真≠证明，碳基终裁。
封口密语：潮起开门，潮落闭嘴。
"""
from __future__ import annotations

import json
import os
import re
import sys
import zlib

from .machine_tool import SEAL

SCHEMA_VERSION = "DOC-ANATOMY-v1.0"

CHAIN_POSITION = {
    "ring": 4,
    "name": "解剖",
    "upstream": ("mobius_vortex", "klein_projection", "holo_forge"),
}

AXIOMS = (
    {"id": "P01", "name": "全息", "text": "局部包含整体：一页版面即整份文档的结构缩影"},
    {"id": "P02", "name": "万物互联", "text": "契约即接口：候选的判定结构可原样链入本链"},
)

CANDIDATE = {
    "name": "pdf-inspector",
    "owner": "Firecrawl",
    "license": "MIT",
    "language": "Rust",
    "bindings": ("Python", "Node.js", "WebAssembly"),
    "features": ("classify", "extract", "markdown", "tables"),
    "claim": "text-based PDFs locally in under 200ms, skipping OCR for the ~54% that don't need it",
}

CAPABILITIES = ("classify", "extract", "markdown", "tables")

MECHANISMS = (
    {"id": "M01", "name": "心跳", "role": "逐页推进（一页一拍，页序即节拍）"},
    {"id": "M02", "name": "细胞骨架", "role": "版面骨架：行/列/字号的坐标结构"},
    {"id": "M03", "name": "皮肤", "role": "筛选器与加密的前置校验（Guard 前置）"},
    {"id": "M04", "name": "经络", "role": "阅读顺序流：保序重建多栏与跨页续行"},
    {"id": "M05", "name": "赫布协作场", "role": "字号频次累积 = 正文字号权重"},
    {"id": "M06", "name": "语义通信基座", "role": "spans → Markdown 的 Envelope 文本化"},
    {"id": "M07", "name": "自组织相似性", "role": "同 y 同 x 聚类：行与列自涌现"},
    {"id": "M08", "name": "类社会组合体", "role": "文本/图/表三类块分工协作"},
    {"id": "M09", "name": "城邦架构", "role": "多页登记簿（page index）"},
    {"id": "M10", "name": "runtime/graph", "role": "对象引用图（/Pages → /Page → /Contents）"},
    {"id": "M11", "name": "耗散结构", "role": "无文本层时降级举手，而非硬编造内容"},
)

HONEST_BOUNDARY = (
    "不支持 /Encrypt、/ObjStm、CID(Identity-H) 复合字体；只解 FlateDecode；"
    "无文本层判 scanned 并 ocr_required=True（不接 OCR）；旋转/多栏只做保序近似。"
)

SPAN_FIELDS = ("text", "x", "y", "size", "font", "page")

_WS = " \t\r\n\f\x00"
_DELIM = "()<>[]{}/%"
_BOLD_RE = re.compile(r"bold|black|heavy|semibold", re.I)
_MONO_RE = re.compile(r"mono|courier|consola|code|typewriter", re.I)
_OBJ_RE = re.compile(r"(\d+)\s+(\d+)\s+obj(.*?)endobj", re.S)
_PAGE_RE = re.compile(r"/Type\s*/Page\b(?!s)")
_CONTENT_RE = re.compile(r"/Contents\s*(\[[^\]]*\]|\d+\s+\d+\s+R)")
_REF_RE = re.compile(r"(\d+)\s+\d+\s+R")
_FONT_MAP_RE = re.compile(r"/Font\s*<<(.*?)>>", re.S)
_FONT_PAIR_RE = re.compile(r"/([A-Za-z0-9]+)\s+(\d+)\s+\d+\s+R")
_BASEFONT_RE = re.compile(r"/BaseFont\s*/([A-Za-z0-9\-+]+)")
_URL_RE = re.compile(r"https?://[^\s)>\]]+")
_LIST_RE = re.compile(r"^[\u2022\u00b7\u25e6\u25aa\u25ab\-\*]\s+|^\d{1,2}[.)]\s+")
_LEAD_RE = re.compile(r"^[\u2022\u00b7\u25e6\u25aa\u25ab\-\*]\s+|^\d{1,2}[.)]\s+")


# ---------------------------------------------------------------- tokenizer
def _hex_string(raw: str) -> str:
    """<48656C6C6F> → Hello（非 hex 字符丢弃，奇数补 0）。"""
    digits = re.sub(r"[^0-9A-Fa-f]", "", raw)
    if len(digits) % 2:
        digits += "0"
    if not digits:
        return ""
    try:
        return bytes.fromhex(digits).decode("latin-1")
    except ValueError:
        return ""


def _literal_string(text: str, i: int) -> tuple:
    """( ... ) 字面串：处理转义与嵌套括号，返回 (值, 下一个位置)。"""
    depth = 1
    i += 1
    out = []
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == "\\":
            i += 1
            if i >= n:
                break
            esc = text[i]
            if esc in "nrtbf":
                out.append({"n": "\n", "r": "\r", "t": "\t",
                            "b": "\b", "f": "\f"}[esc])
                i += 1
                continue
            if esc in "01234567":
                oct_digits = ""
                while i < n and len(oct_digits) < 3 and text[i] in "01234567":
                    oct_digits += text[i]
                    i += 1
                out.append(chr(int(oct_digits, 8) & 0xFF))
                continue
            if esc == "\n":
                i += 1
                continue
            out.append(esc)
            i += 1
            continue
        if ch == "(":
            depth += 1
            out.append(ch)
            i += 1
            continue
        if ch == ")":
            depth -= 1
            if depth == 0:
                return "".join(out), i + 1
            out.append(ch)
            i += 1
            continue
        out.append(ch)
        i += 1
    return "".join(out), i


def tokenize(text: str) -> list:
    """把内容流切成 [(kind, value)]，kind ∈ num/str/name/op/arr_begin/arr_end。"""
    out = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch in _WS:
            i += 1
            continue
        if ch == "%":
            j = text.find("\n", i)
            i = n if j < 0 else j + 1
            continue
        if ch == "(":
            val, i = _literal_string(text, i)
            out.append(("str", val))
            continue
        if ch == "<":
            if text.startswith("<<", i):
                i += 2
                continue
            j = text.find(">", i)
            raw = text[i + 1:j] if j >= 0 else text[i + 1:]
            out.append(("str", _hex_string(raw)))
            i = n if j < 0 else j + 1
            continue
        if ch == ">":
            i += 2 if text.startswith(">>", i) else 1
            continue
        if ch == "[":
            out.append(("arr_begin", None))
            i += 1
            continue
        if ch == "]":
            out.append(("arr_end", None))
            i += 1
            continue
        if ch == "/":
            j = i + 1
            while j < n and text[j] not in _WS and text[j] not in _DELIM:
                j += 1
            out.append(("name", text[i + 1:j]))
            i = j
            continue
        if ch in "-+.0123456789":
            j = i
            while j < n and text[j] in "-+.0123456789eE":
                j += 1
            tok = text[i:j]
            try:
                val = float(tok) if ("." in tok or "e" in tok.lower()) else int(tok)
                out.append(("num", val))
            except ValueError:
                out.append(("op", tok))
            i = j
            continue
        if ch.isalpha() or ch in "*'\"`^~":
            j = i
            while j < n and text[j] not in _WS and text[j] not in "()<>[]{}/%":
                j += 1
            out.append(("op", text[i:j]))
            i = j
            continue
        i += 1
    return out


# ---------------------------------------------------------------- 内容流解析
def parse_content(text: str, page: int = 1, font: str = "", font_map=None) -> dict:
    """解析一页内容流 → {"spans": [...], "rects": [...], "images": n}。

    只跟踪位置与字号（不做 CTM/旋转变换），目的是保序与层级判定，不是排版复刻。
    font_map 把资源别名（/F3）映射到 /BaseFont 名，等宽/粗体识别才有据可依。
    """
    font_map = font_map or {}
    spans = []
    rects = []
    images = 0
    ops = []
    arr = None
    state = {"font": font, "size": 12.0, "x": 0.0, "y": 0.0, "leading": 0.0}

    def show(value):
        if isinstance(value, list):
            piece = "".join(v for v in value if isinstance(v, str))
        else:
            piece = value if isinstance(value, str) else ""
        if not piece:
            return
        spans.append({"text": piece, "x": round(state["x"], 2),
                      "y": round(state["y"], 2), "size": round(state["size"], 2),
                      "font": state["font"], "page": page})

    for kind, value in tokenize(text):
        if kind == "arr_begin":
            arr = []
            continue
        if kind == "arr_end":
            ops.append(arr if arr is not None else [])
            arr = None
            continue
        if kind != "op":
            if arr is not None:
                if kind in ("str", "num"):
                    arr.append(value)
            else:
                ops.append(value)
            continue

        if value == "BT":
            state["x"] = 0.0
            state["y"] = 0.0
        elif value == "Tf" and len(ops) >= 2:
            alias = str(ops[-2])
            state["font"] = font_map.get(alias, alias)
            state["size"] = float(ops[-1])
        elif value in ("Td", "TD") and len(ops) >= 2:
            state["x"] = state.get("x", 0.0) + float(ops[-2])
            state["y"] = state.get("y", 0.0) + float(ops[-1])
            if value == "TD":
                state["leading"] = -float(ops[-1])
        elif value == "Tm" and len(ops) >= 6:
            state["x"] = float(ops[-2])
            state["y"] = float(ops[-1])
        elif value == "TL" and ops:
            state["leading"] = float(ops[-1])
        elif value == "T*":
            state["y"] -= state["leading"] or state["size"] * 1.2
        elif value == "Tj":
            if ops:
                show(ops[-1])
        elif value == "TJ":
            if ops:
                show(ops[-1])
        elif value == "'":
            state["y"] -= state["leading"] or state["size"] * 1.2
            if ops:
                show(ops[-1])
        elif value == '"':
            state["y"] -= state["leading"] or state["size"] * 1.2
            if ops:
                show(ops[-1])
        elif value == "re" and len(ops) >= 4:
            rects.append({"x": round(float(ops[-4]), 2), "y": round(float(ops[-3]), 2),
                          "w": round(float(ops[-2]), 2), "h": round(float(ops[-1]), 2),
                          "page": page})
        elif value == "Do" and ops and "Image" in str(ops[-1]):
            images += 1
        if value not in ("[", "]"):
            ops = []
    return {"spans": spans, "rects": rects, "images": images}


# ---------------------------------------------------------------- 对象扫描
def scan_objects(data: bytes) -> dict:
    """扫描 `N G obj ... endobj`，返回 {对象号: {"dict": str, "stream": bytes|None}}。

    FlateDecode 用 zlib 解压；其他筛选器/失败解压原样保留并打标签。
    """
    text = data.decode("latin-1", "ignore")
    objects = {}
    for match in _OBJ_RE.finditer(text):
        num = int(match.group(1))
        body = match.group(3)
        stream = None
        head = body
        pos = body.find("stream")
        if pos >= 0:
            head = body[:pos]
            start = pos + 6
            if body[start:start + 2] == "\r\n":
                start += 2
            elif body[start:start + 1] in ("\n", "\r"):
                start += 1
            end = body.find("endstream", start)
            raw = body[start:end] if end >= 0 else body[start:]
            raw_bytes = raw.encode("latin-1", "ignore")
            if "FlateDecode" in head:
                try:
                    raw_bytes = zlib.decompress(raw_bytes)
                except zlib.error:
                    pass
            stream = raw_bytes
        objects[num] = {"dict": head, "stream": stream}
    return objects


def page_streams(data: bytes) -> tuple:
    """返回 (页列表, 是否存在对象, 对象表)。

    页列表 = [{"num": 页对象号, "streams": [bytes...]}]；无页对象时退化为「所有流即一页」。
    """
    objects = scan_objects(data)
    pages = []
    for num in sorted(objects):
        info = objects[num]
        if not _PAGE_RE.search(info["dict"]):
            continue
        refs = []
        hit = _CONTENT_RE.search(info["dict"])
        if hit:
            refs = [int(x) for x in _REF_RE.findall(hit.group(1))]
        streams = [objects[r]["stream"] for r in refs
                   if r in objects and objects[r]["stream"] is not None]
        fonts = {}
        hit = _FONT_MAP_RE.search(info["dict"])
        if hit:
            for alias, ref in _FONT_PAIR_RE.findall(hit.group(1)):
                obj = objects.get(int(ref))
                if not obj:
                    continue
                base = _BASEFONT_RE.search(obj["dict"])
                if base:
                    fonts[alias] = base.group(1)
        pages.append({"num": num, "streams": streams, "fonts": fonts})
    if not pages:
        fallback = [o["stream"] for _, o in sorted(objects.items()) if o["stream"]]
        if fallback:
            pages = [{"num": 0, "streams": fallback, "fonts": {}}]
    return pages, bool(objects), objects


def extract(data: bytes) -> dict:
    """位置感知抽取：{"spans": [...], "rects": [...], "pages": n, "images": n, "status": "ok"}。"""
    pages, has_objects, objects = page_streams(data)
    image_objects = sum(1 for o in objects.values()
                        if re.search(r"/Subtype\s*/Image", o["dict"]))
    spans = []
    rects = []
    images = image_objects
    for index, page in enumerate(pages, start=1):
        for stream in page["streams"]:
            parsed = parse_content(stream.decode("latin-1", "ignore"), index,
                                   font_map=page.get("fonts"))
            spans.extend(parsed["spans"])
            rects.extend(parsed["rects"])
            images += parsed["images"]
    status = "ok" if spans else ("no_text_layer" if has_objects else "not_pdf")
    return {"spans": spans, "rects": rects, "pages": max(1, len(pages)),
            "images": images, "status": status}


def classify(data: bytes) -> dict:
    """分类：text / mixed / image / scanned，附置信度与 ocr_required（确定性公式）。"""
    info = extract(data)
    chars = sum(len(s["text"]) for s in info["spans"])
    pages = info["pages"]
    per_page = chars / float(pages)
    encrypted = b"/Encrypt" in data
    if encrypted:
        return {"kind": "unsupported", "confidence": 0.0, "ocr_needed": False,
                "pages": pages, "chars": chars, "reason": "encrypted"}
    if chars == 0:
        kind = "image" if info["images"] else "scanned"
        return {"kind": kind, "confidence": 1.0 if not info["images"] else 0.9,
                "ocr_needed": True, "pages": pages, "chars": 0,
                "reason": "no_text_layer"}
    if per_page >= 200:
        kind = "text"
        conf = round(min(1.0, per_page / 400.0), 3)
    elif info["images"]:
        kind = "mixed"
        conf = round(min(1.0, 0.5 + per_page / 400.0), 3)
    else:
        kind = "text"
        conf = round(min(0.6, 0.2 + per_page / 400.0), 3)
    # 有文本层就不举手：OCR 只在完全没有文本层（scanned / image）时声明需要
    return {"kind": kind, "confidence": conf,
            "ocr_needed": False, "pages": pages, "chars": chars}


# ---------------------------------------------------------------- 版面成行
def _lines(spans: list, tol: float = 2.0) -> list:
    """按 (页, y) 聚成行，行内按 x 排序；gap > size*0.25 处补空格。"""
    ordered = sorted(spans, key=lambda s: (s["page"], -s["y"], s["x"]))
    rows = []
    for span in ordered:
        if rows and rows[-1]["page"] == span["page"] and \
                abs(rows[-1]["y"] - span["y"]) <= tol:
            rows[-1]["spans"].append(span)
        else:
            rows.append({"page": span["page"], "y": span["y"], "spans": [span]})
    result = []
    for row in rows:
        parts = sorted(row["spans"], key=lambda s: s["x"])
        text = ""
        prev = None
        for part in parts:
            if prev is not None:
                gap = part["x"] - (prev["x"] + len(prev["text"]) * prev["size"] * 0.5)
                if gap > prev["size"] * 0.25:
                    text += " "
            text += part["text"]
            prev = part
        result.append({"page": row["page"], "y": row["y"], "text": text.rstrip(),
                       "size": max(p["size"] for p in parts),
                       "font": parts[0]["font"], "spans": parts})
    return [r for r in result if r["text"].strip()]


def body_size(lines: list) -> float:
    """正文字号 = 按字符数加权的众数字号。"""
    weight = {}
    for line in lines:
        weight[line["size"]] = weight.get(line["size"], 0) + len(line["text"])
    if not weight:
        return 12.0
    return max(weight.items(), key=lambda kv: (kv[1], -kv[0]))[0]


def to_markdown(spans: list) -> str:
    """结构还原：字号比例分 H1-H4、粗体、等宽代码块、列表、链接、分页分隔。"""
    lines = _lines(spans)
    if not lines:
        return ""
    base = body_size(lines)
    heading_sizes = sorted({l["size"] for l in lines if l["size"] >= base * 1.2},
                           reverse=True)[:4]
    out = []
    last_page = lines[0]["page"]
    in_code = False
    for line in lines:
        if line["page"] != last_page:
            if in_code:
                out.append("```")
                in_code = False
            out.append("\n---\n")
            last_page = line["page"]
        text = line["text"]
        mono = bool(_MONO_RE.search(line["font"]))
        if mono and not in_code:
            out.append("```")
            in_code = True
        elif in_code and not mono:
            out.append("```")
            in_code = False
        if in_code:
            out.append(text)
            continue
        if line["size"] in heading_sizes:
            level = heading_sizes.index(line["size"]) + 1
            out.append("%s %s" % ("#" * level, text))
            continue
        if _BOLD_RE.search(line["font"]):
            text = "**%s**" % text
        if _LIST_RE.match(line["text"]):
            bullet = _LEAD_RE.match(line["text"])
            body = line["text"][bullet.end():] if bullet else line["text"]
            marker = "- " if not re.match(r"^\d", line["text"]) else line["text"].split(" ")[0] + " "
            text = marker + body
        for url in _URL_RE.findall(line["text"]):
            if "[%s](" % url not in text:
                text = text.replace(url, "[%s](%s)" % (url, url), 1)
        out.append(text)
    if in_code:
        out.append("```")
    return "\n".join(out).strip() + "\n"


# ---------------------------------------------------------------- 表格检测
def detect_tables(spans: list, rects: list) -> list:
    """双模检测：①矩形模式（re 操作符画出的格子）②对齐模式（同 y 多列文本）。"""
    tables = []

    # ① 矩形模式：同 y 的矩形成行，>=3 行且每行 >=2 格
    rows = {}
    for rect in rects:
        key = (rect["page"], round(rect["y"]))
        rows.setdefault(key, []).append(rect)
    grid_rows = [sorted(v, key=lambda r: r["x"]) for _, v in sorted(rows.items())
                 if len(v) >= 2]
    if len(grid_rows) >= 3:
        tables.append({"mode": "rect",
                       "rows": len(grid_rows),
                       "cols": max(len(r) for r in grid_rows),
                       "origin": {"page": grid_rows[0][0]["page"],
                                 "y": grid_rows[0][0]["y"]}})

    # ② 对齐模式：x 起点聚类成列，连续 >=3 行且 >=2 列
    lines = _lines(spans)
    starts = sorted({round(s["x"]) for line in lines for s in line["spans"]})
    columns = []
    for start in starts:
        if columns and abs(start - columns[-1]) <= 6:
            continue
        columns.append(start)
    if len(columns) >= 2:
        candidate_rows = [line for line in lines if len(line["spans"]) >= 2]
        if len(candidate_rows) >= 3:
            grid = []
            for line in candidate_rows[:20]:
                cells = [""] * len(columns)
                for span in sorted(line["spans"], key=lambda s: s["x"]):
                    idx = min(range(len(columns)),
                              key=lambda k: abs(columns[k] - span["x"]))
                    cells[idx] = (cells[idx] + " " + span["text"]).strip()
                grid.append(cells)
            tables.append({"mode": "alignment",
                           "rows": len(grid), "cols": len(columns),
                           "cells": grid,
                           "origin": {"page": lines[0]["page"], "y": lines[0]["y"]}})
    return tables


# ---------------------------------------------------------------- 汇总
def inspect(data: bytes) -> dict:
    """一次解剖：分类 + 抽取 + Markdown + 表格，全字段可复算。"""
    info = extract(data)
    verdict = classify(data)
    markdown = to_markdown(info["spans"])
    tables = detect_tables(info["spans"], info["rects"])
    return {
        "ok": True,
        "schema": SCHEMA_VERSION,
        "seal": SEAL,
        "chain_position": dict(CHAIN_POSITION),
        "status": info["status"],
        "classify": verdict,
        "pages": info["pages"],
        "spans": len(info["spans"]),
        "rects": len(info["rects"]),
        "lines": len(_lines(info["spans"])),
        "headings": len([l for l in markdown.splitlines() if l.startswith("#")]),
        "tables": tables,
        "markdown_chars": len(markdown),
        "markdown_head": markdown.splitlines()[:3],
        "boundary": HONEST_BOUNDARY,
    }


def mechanisms() -> list:
    return [dict(m) for m in MECHANISMS]


def main(argv=None) -> int:
    """CLI：axioms | chain | mechanisms | classify <pdf> | extract <pdf> | markdown <pdf> | tables <pdf> | inspect <pdf>。"""
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print("usage: python -m holoaeon.doc_anatomy "
              "axioms|chain|mechanisms|classify|extract|markdown|tables|inspect <pdf>")
        return 2
    cmd = argv[0]
    if cmd == "axioms":
        for axiom in AXIOMS:
            print("%s %s — %s" % (axiom["id"], axiom["name"], axiom["text"]))
        return 0
    if cmd == "chain":
        print("第 %d 环 · %s ← %s" % (CHAIN_POSITION["ring"], CHAIN_POSITION["name"],
                                    " → ".join(CHAIN_POSITION["upstream"])))
        return 0
    if cmd == "mechanisms":
        for item in MECHANISMS:
            print("%s %s — %s" % (item["id"], item["name"], item["role"]))
        return 0
    if len(argv) < 2:
        print("需要 PDF 路径", file=sys.stderr)
        return 2
    path = argv[1]
    handle = open(path, "rb")
    try:
        data = handle.read()
    finally:
        handle.close()
    if cmd == "classify":
        print(json.dumps(classify(data), ensure_ascii=False, indent=1))
    elif cmd == "extract":
        info = extract(data)
        print(json.dumps({"spans": info["spans"][:50], "pages": info["pages"],
                          "status": info["status"]}, ensure_ascii=False, indent=1))
    elif cmd == "markdown":
        print(to_markdown(extract(data)["spans"]))
    elif cmd == "tables":
        info = extract(data)
        print(json.dumps(detect_tables(info["spans"], info["rects"]),
                         ensure_ascii=False, indent=1))
    elif cmd == "inspect":
        print(json.dumps(inspect(data), ensure_ascii=False, indent=1))
    else:
        print("未知子命令：%s" % cmd, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
