# 超向量表示（HRR / VSA）

超向量空间提供基于全息缩减表示（Holographic Reduced Representation）的联想与绑定能力，
全部建立在手写 FFT 之上，不依赖 NumPy。

## 1. 基本思想

向量符号架构（Vector Symbolic Architecture）用高维向量表示符号，用代数运算实现组合：

- 相似的向量表示相近的概念；
- 绑定（bind）把两个角色组合成一个新向量；
- 打包（bundle）把多个概念叠加；
- 运算结果仍在同一空间，可级联。

## 2. 为什么是 1024 维

绑定用圆卷积，通过 FFT 实现。FFT 要求维度为 2 的幂，因此默认维度为 **1024**（而非任意
值）。维度越高，随机向量越接近正交，绑定越近似可逆。

## 3. 核心运算

| 运算 | 实现 | 性质 |
|---|---|---|
| `make(seed)` | 由种子确定性派生 | 同种子 → 同向量 |
| `bind(a, b)` | 圆卷积（FFT 相乘） | 近似可逆，与 a/b 都不相关 |
| `unbind(ab, b)` | 用逆核近似 | 可恢复 a |
| `bundle(a, b)` | 逐元素相加 | 与两者都相关 |
| `permute(v)` | 确定性置换 | 用于结构化角色 |
| `cosine(a, b)` | 余弦相似度 | −1 到 1 |

## 4. 手写 FFT

`_fft` 实现 radix-2 Cooley–Tukey 算法：

```
把向量按奇偶拆半 → 递归 FFT → 旋转因子（twiddle）合成
```

纯标准库（`cmath`），千维向量约数毫秒。

## 5. 实测性质

- `cosine(a, a) = 1.0`；
- `bind(a,b)` 与 a、b 的余弦都接近 0（成功"隐藏"成分）；
- `unbind(bind(a,b), b)` 与 a 的余弦约 0.7（近似恢复）。

## 6. 用途

- 快速联想记忆（encode_pair / retrieve）；
- 类比与角色绑定；
- 层次结构的分布式表示；
- 作为符号推理与神经表示之间的桥梁。

## 7. 用法

```python
from holoaeon.hypervector import HypervectorSpace
hv = HypervectorSpace()
a, b = hv.make("a"), hv.make("b")
ab = hv.bind(a, b)
recovered = hv.unbind(ab, b)
print(hv.cosine(recovered, a))
```
