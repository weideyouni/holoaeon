#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""结构图文本重叠复检：估算每个 <text> 的外框，逐对判交叠。

只处理本技能生成的静态 SVG（text 带 x/y/font-size/text-anchor）。
退出码：0 无重叠；1 有重叠；2 读取失败。
"""
import argparse
import re
import sys

PAT = re.compile(r'<text x="([0-9.]+)" y="([0-9.]+)" font-size="([0-9]+)"[^>]*'
                 r'text-anchor="([a-z]+)">([^<]+)</text>')


def width_of(txt, fs):
    # CJK 按 1.0 em、ASCII 按 0.55 em 估算
    return sum(1.0 if ord(ch) > 127 else 0.55 for ch in txt) * fs


def box(x, y, fs, anchor, txt):
    w = width_of(txt, fs)
    if anchor == "end":
        x0 = x - w
    elif anchor == "middle":
        x0 = x - w / 2.0
    else:
        x0 = x
    return (x0, x0 + w, y - fs, y + fs * 0.25, txt)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", required=True)
    args = ap.parse_args()
    try:
        html = open(args.html, encoding="utf-8").read()
    except Exception as e:  # noqa: BLE001
        print("读取失败：%s" % e)
        return 2

    boxes = [box(float(m.group(1)), float(m.group(2)), int(m.group(3)), m.group(4), m.group(5))
             for m in PAT.finditer(html)]
    bad = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            if not (a[1] < b[0] or a[0] > b[1] or a[3] < b[2] or a[2] > b[3]):
                bad.append((a[4], b[4], round(a[0]), round(a[2]), round(b[0]), round(b[2])))

    print("texts=%d overlaps=%d" % (len(boxes), len(bad)))
    for x in bad[:10]:
        print("  %s × %s  x[%s..%s] vs x[%s..%s]" % x)
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
