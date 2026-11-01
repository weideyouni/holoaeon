# 坑表（全部真实踩过）

| # | 现象 | 处理 |
|---|---|---|
| 1 | 概念轴用近义词（「观测」）对原文（「观察」）→ 该轴全篇 0 命中，矩阵照样算得出来 | 定轴后先跑 `audit_axes.py`，空轴=词表错，不是内容空 |
| 2 | 稀疏度漂亮（0.23）被当成「质量好」 | 稀疏度只是描述量，验收看 A3 空轴数 + A6 规律有据 |
| 3 | 只读首尾两段就下结论 | 规律必须逐段对账，尤其要检查中段是否出现「证据断崖」 |
| 4 | 转写返回 `last_notes_error: minute not ready` 就重跑 | 先查 `minutes/artifact-*/` 是否已落地；文件在就别重跑 |
| 5 | `pip install --user av` 报 User site-packages disabled | 去掉 `--user`，直接 `python -m pip install av` |
| 6 | 用 `Speaker` 行数当段数 | 段数 = 正则命中数 − 空段；空段要记账 |
| 7 | 末段时间与片头标注时长不一致就改数据 | 差 < 30 秒属正常（片尾静音/片头元数据），写明即可 |
| 8 | 把人工标注（角色/证据/层级）算进指纹 | 标注不进指纹；否则每支视频的「贴标签」都会让指纹漂 |
| 9 | 改完轴不重跑，md 里的旧数字留着 | 换轴=换档，全部统计、首现序、指纹一起重算，旧指纹显式作废 |
| 10 | 结构图标签两行堆叠压字 | 单行 + 简易避让（候选位移 15px，最多 4 次），阈值放宽到 C−14/C+6 |
| 11 | 用 PowerShell 内联正则查重叠 | 写 `check_viz_overlap.py`，PowerShell 内联正则会解析崩 |
| 12 | 复跑一次 digest 变了却以为偶发 | 先查是否混进物理量（时间戳/耗时）；本技能指纹只覆盖计数，天然免疫 |

## 幂等自检（每次交付前跑）

```
python scripts/build_tensor.py --transcript <t> --out <tmp1>
python scripts/build_tensor.py --transcript <t> --out <tmp2>
# 两个 digest.txt 必须逐字节相等
```
