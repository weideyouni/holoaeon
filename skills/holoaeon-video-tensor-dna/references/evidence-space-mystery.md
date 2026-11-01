# 参考档案：空间之谜（BV1msxp6yE3y）

首个跑通样本，用作回归基线。任何改动后跑 `build_tensor.py` 复算，指纹应仍为此值。

| 项 | 值 |
|---|---|
| 来源 | B 站 BV1msxp6yE3y，科普口播，909 秒 |
| 转写 | 妙记产物 `minutes/artifact-bilibili_BV1msxp6yE3y_p1_480P-*/transcript.txt` |
| 段数 | 17（Speaker 标记 17，无空段） |
| 字数 | 4334（均 254.9，最长 437 在第 5 段） |
| 设问 | 32 个（约每 28 秒一个） |
| 数字 | 32 个，全部为可校验常量 |
| 张量 | 17 × 24 × 4（d3 认知层 3 档） |
| 稀疏度 | 96 / 408 = 0.2353 |
| 指纹 | `0ec78ce5b1ca3029ad110feae0e05995070f90d04648a385399a907f3367fb74` |

## 已作废的旧值（勿当现状）

初版词表用「观测」而非原文的「观察」，导致该轴全篇 0 命中：
`nnz 95 / density 0.2328 / digest 64915a63…` —— 已作废，换成「观察」后重算。

## 首现序（`first_seen`）

空间1 · 时空1 · 牛顿1 · 莱布尼茨2 · 时间2 · 爱因斯坦4 · 广义相对论4 · 引力4 · 质量4
· 实验5 · 能量5 · 宇宙5 · 引力波6 · 天文台6 · 黑洞7 · 光年7 · 微观7 · 刚性9 · 观察11
· 弹性波11 · 涌现12 · 量子13 · 量子纠缠13 · 信息14

## 回归自检

```
python scripts/build_tensor.py --transcript <该 transcript.txt> --out <tmp> --name space-mystery-video-tensor
# digest.txt 必须等于 0ec78ce5b1ca3029ad110feae0e05995070f90d04648a385399a907f3367fb74
python scripts/audit_axes.py --dir <tmp>          # empty_axes=0，PASS
```
