# -*- coding: utf-8 -*-
"""
Hypervector —— HoloAeon 超维表示（VSA / HDC）
================================================================================
超维计算把"符号/概念"编码为高维向量，用代数运算实现组合与检索：

  · make(key)   由 key 确定性派生一个单位向量（sha256，不使用随机数）
  · bind(a,b)   HRR 圆周卷积（绑定两个概念，可逆，结果近似不相关）
  · unbind      绑定的逆（用于从组合中取出角色）
  · bundle      元素相加（集合/多集，归一化）
  · permute     循环移位（编码序列/顺序）
  · cosine      余弦相似度（检索/匹配）

HRR 用迭代 Cooley-Tukey FFT（dim 取 2 的幂，默认 1024）。纯标准库、确定性。
"""
from __future__ import annotations

import cmath
import hashlib
import math
from dataclasses import dataclass
from typing import Dict, List, Sequence

from .spec import HypervectorConfig

PI = math.pi


# ------------------------------------------------------------ FFT（radix-2）
def _fft(a: List[complex], invert: bool = False) -> List[complex]:
    """radix-2 FFT。

    不修改入参：内部先做 `a = list(a)`，bit-reversal 置换与蝶形运算只作用于副本。
    正向变换采用 e^{+2πi} 约定，逆变换内部已除 n。
    """
    a = list(a)
    n = len(a)
    j = 0
    for i in range(1, n):
        bit = n >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j ^= bit
        if i < j:
            a[i], a[j] = a[j], a[i]
    length = 2
    while length <= n:
        ang = 2 * PI / length * (-1 if invert else 1)
        wlen = cmath.cos(ang) + 1j * cmath.sin(ang)
        for i in range(0, n, length):
            w = complex(1)
            half = length // 2
            for k in range(half):
                u = a[i + k]
                v = a[i + k + half] * w
                a[i + k] = u + v
                a[i + k + half] = u - v
                w *= wlen
        length <<= 1
    if invert:
        a = [x / n for x in a]
    return a


def _normalize(v: List[float]) -> List[float]:
    norm = math.sqrt(sum(x * x for x in v))
    return [x / norm for x in v] if norm else v


@dataclass
class HypervectorSpace:
    """VSA 空间：make/bind/unbind/bundle/permute/cosine。"""
    config: HypervectorConfig = None

    def __post_init__(self) -> None:
        if self.config is None:
            self.config = HypervectorConfig()
        self.dim = self.config.dim
        self._cache: Dict[str, List[float]] = {}

    # ------------------------------------------------------------ 生成
    def make(self, key: str) -> List[float]:
        if key in self._cache:
            return list(self._cache[key])
        vals: List[float] = []
        counter = 0
        while len(vals) < self.dim:
            h = hashlib.sha256(f"hv:{key}:{counter}".encode("utf-8")).digest()
            for b in h:
                vals.append((b / 255.0 - 0.5) * 2)  # [-1,1)
                if len(vals) >= self.dim:
                    break
            counter += 1
        v = _normalize(vals[:self.dim])
        self._cache[key] = v
        return list(v)

    # ------------------------------------------------------------ HRR 绑定
    def bind(self, a: Sequence[float], b: Sequence[float]) -> List[float]:
        if self.config.binding == "permutation":
            return self.permute(a, 1)
        fa = _fft([complex(x) for x in a], False)
        fb = _fft([complex(x) for x in b], False)
        fc = [x * y for x, y in zip(fa, fb)]
        c = _fft(fc, True)
        return _normalize([x.real for x in c])

    def unbind(self, combo: Sequence[float], b: Sequence[float]) -> List[float]:
        """从 combo 中按 b 的逆取出（HRR 逆 = 频域共轭）。"""
        fc = _fft([complex(x) for x in combo], False)
        fb = _fft([complex(x) for x in b], False)
        fa = [c * y.conjugate() for c, y in zip(fc, fb)]
        a = _fft(fa, True)
        return _normalize([x.real for x in a])

    # ------------------------------------------------------------ 集合 / 顺序
    def bundle(self, vectors: Sequence[Sequence[float]]) -> List[float]:
        if not vectors:
            return [0.0] * self.dim
        acc = [0.0] * self.dim
        for v in vectors:
            for i, x in enumerate(v):
                acc[i] += x
        return _normalize(acc)

    def permute(self, v: Sequence[float], shift: int = 1) -> List[float]:
        shift = shift % self.dim
        return list(v[-shift:]) + list(v[:-shift])

    # ------------------------------------------------------------ 相似
    @staticmethod
    def cosine(a: Sequence[float], b: Sequence[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(y * y for y in b))
        return round(dot / (na * nb), 5) if na and nb else 0.0

    def encode_pair(self, role: str, filler: str) -> List[float]:
        """角色-填充对：bind(permute(role), filler)。"""
        return self.bind(self.permute(self.make(role)), self.make(filler))

    def retrieve(self, query: Sequence[float], candidates: Sequence[str],
                 k: int = 1) -> List[tuple]:
        scored = [(c, self.cosine(query, self.make(c))) for c in candidates]
        scored.sort(key=lambda t: -t[1])
        return scored[:k]
