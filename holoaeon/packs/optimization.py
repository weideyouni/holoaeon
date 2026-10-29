# -*- coding: utf-8 -*-
"""领域包：优化求解（optimization）。
================================================================================
把《优化设计》的经典数值优化算法，代码化为确定性的"搜索/求解"认知能力：
  · 一维搜索 ：黄金分割法（区间消去）
  · 无约束   ：梯度下降（数值差分）、牛顿法（二阶曲率）、共轭梯度（A-共轭）
  · 线性规划 ：表格单纯形法（顶点游走）
  · 约束优化 ：惩罚函数法（边界惩罚）
  · 群体进化 ：遗传算法（选择/交叉/变异，确定性种子）

所有算法纯标准库、零依赖、可复现；目标函数只来自内置的安全 benchmark，
绝不 eval 任意表达式（红线）。
隐喻映射：搜索方向=思路；区间消去=注意力聚焦；惩罚=安全护栏；进化=群体迭代。
"""
from __future__ import annotations

import math
import random
from typing import List, Sequence, Tuple

from .base import DomainPack, RoleSpec, SkillSpec, WorkflowSpec


# ================================================================ 数值工具
def _grad(f, x: Sequence[float], h: float = 1e-6) -> List[float]:
    """中心差分数值梯度（梯度=最陡上升方向，取负即下降）。"""
    g = []
    for k in range(len(x)):
        xp = list(x); xm = list(x)
        xp[k] += h; xm[k] -= h
        g.append((f(xp) - f(xm)) / (2.0 * h))
    return g


# ================================================================ 核心算法
def golden_section(f, a: float, b: float,
                   tol: float = 1e-7, max_iter: int = 100) -> Tuple[float, int]:
    """黄金分割法：在单峰区间 [a,b] 上以 0.618 比例做区间消去，返回极小点。"""
    ratio = (math.sqrt(5.0) - 1.0) / 2.0  # ≈0.618
    c = b - ratio * (b - a)
    d = a + ratio * (b - a)
    fc, fd = f([c]), f([d])
    it = 0
    for it in range(1, max_iter + 1):
        if fc < fd:
            b, d, fd = d, c, fc
            c = b - ratio * (b - a)
            fc = f([c])
        else:
            a, c, fc = c, d, fd
            d = a + ratio * (b - a)
            fd = f([d])
        if abs(b - a) < tol:
            break
    return (a + b) / 2.0, it


def gradient_descent(f, x0: Sequence[float], lr: float = 0.1,
                     max_iter: int = 500, tol: float = 1e-9
                     ) -> Tuple[List[float], int, bool]:
    """梯度下降法：沿负梯度方向迭代（数值梯度），返回最优点、迭代数、是否收敛。"""
    x = list(x0)
    converged = False
    it = 0
    for it in range(1, max_iter + 1):
        g = _grad(f, x)
        xn = [x[k] - lr * g[k] for k in range(len(x))]
        step = max(abs(xn[k] - x[k]) for k in range(len(x)))
        x = xn
        if step < tol:
            converged = True
            break
    return x, it, converged


def newton_1d(f, x0: float, max_iter: int = 50,
              tol: float = 1e-11) -> Tuple[float, int, bool]:
    """一维牛顿法：用一阶/二阶（曲率）导数，x -= f'/f''，收敛更快。"""
    x = float(x0)
    converged = False
    it = 0
    for it in range(1, max_iter + 1):
        h = 1e-6
        fp = (f([x + h]) - f([x - h])) / (2 * h)
        fpp = (f([x + h]) - 2 * f([x]) + f([x - h])) / (h * h)
        if abs(fpp) < 1e-14:
            break
        xn = x - fp / fpp
        if abs(xn - x) < tol:
            x = xn
            converged = True
            break
        x = xn
    return x, it, converged


def conjugate_gradient(A: Sequence[Sequence[float]], b: Sequence[float],
                       tol: float = 1e-10, max_iter: int = None
                       ) -> Tuple[List[float], int, bool]:
    """共轭梯度法：求解对称正定方程组 Ax=b。
    注意：共轭（p_i^T A p_j = 0）是相对 A 定义的，不是简单正交。"""
    n = len(b)
    max_iter = max_iter or n
    x = [0.0] * n
    r = [b[i] - sum(A[i][j] * x[j] for j in range(n)) for i in range(n)]
    p = list(r)
    rr = sum(v * v for v in r)
    converged = False
    it = 0
    for it in range(1, max_iter + 1):
        Ap = [sum(A[i][j] * p[j] for j in range(n)) for i in range(n)]
        pAp = sum(p[i] * Ap[i] for i in range(n))
        if abs(pAp) < 1e-14:
            break
        alpha = rr / pAp
        x = [x[i] + alpha * p[i] for i in range(n)]
        r = [r[i] - alpha * Ap[i] for i in range(n)]
        rr_new = sum(v * v for v in r)
        if math.sqrt(rr_new) < tol:
            converged = True
            break
        beta = rr_new / rr
        p = [r[i] + beta * p[i] for i in range(n)]
        rr = rr_new
    return x, it, converged


def simplex(c: Sequence[float], A: Sequence[Sequence[float]],
            b: Sequence[float]) -> dict:
    """表格单纯形法：求解 max c^T x, Ax <= b, x>=0。
    在可行域多面体的顶点间做基变换（顶点游走），直到无改进方向。"""
    m, n = len(A), len(c)
    width = n + m + 1
    t = []
    for i in range(m):
        row = [float(A[i][j]) for j in range(n)] + [0.0] * m + [float(b[i])]
        row[n + i] = 1.0
        t.append(row)
    t.append([-float(c[j]) for j in range(n)] + [0.0] * m + [0.0])
    basis = list(range(n, n + m))
    it = 0
    while True:
        col = min(range(n + m), key=lambda j: t[m][j])
        if t[m][col] >= -1e-10:
            break
        ratios = []
        for i in range(m):
            if t[i][col] > 1e-10:
                ratios.append((t[i][width - 1] / t[i][col], i))
        if not ratios:
            return {"status": "unbounded"}
        _, row = min(ratios, key=lambda z: z[0])
        pivot = t[row][col]
        t[row] = [v / pivot for v in t[row]]
        for i in range(m + 1):
            if i != row:
                factor = t[i][col]
                t[i] = [t[i][j] - factor * t[row][j] for j in range(width)]
        basis[row] = col
        it += 1
    x = [0.0] * n
    for i in range(m):
        if basis[i] < n:
            x[basis[i]] = t[i][width - 1]
    return {"status": "optimal", "x": [round(v, 6) for v in x],
            "objective": round(t[m][width - 1], 6), "iterations": it}


def penalty_method(f, constraints, x0: Sequence[float],
                   rounds: int = 12, mu0: float = 1.0) -> Tuple[List[float], bool]:
    """惩罚函数法：把约束 g(x)<=0 转为二次惩罚项 mu*max(0,g)^2，
    逐轮增大惩罚系数并调用梯度下降，逼近约束最优（边界惩罚）。
    步长随 mu 自适应减小（lr≈0.2/(1+2mu)），避免大惩罚下振荡。"""
    def penalized(x):
        val = f(x)
        for g in constraints:
            val += mu * max(0.0, g(x)) ** 2
        return val

    x = list(x0)
    mu = mu0
    ok = False
    for _ in range(rounds):
        lr = 0.2 / (1.0 + 2.0 * mu)
        x, _, ok = gradient_descent(penalized, x, lr=lr,
                                    max_iter=3000, tol=1e-10)
        mu *= 2.0
    return x, ok


def genetic_algorithm(fitness, n_bits: int, pop_size: int = 24,
                      generations: int = 40, seed: int = 42,
                      cx_prob: float = 0.8, mut_prob: float = 0.05) -> dict:
    """遗传算法：二进制编码，轮盘赌选择、单点交叉、位变异；
    用固定种子保证确定性可复现（群体进化）。"""
    rng = random.Random(seed)

    def decode(ind):
        return sum(ind[i] << (n_bits - 1 - i) for i in range(n_bits))

    pop = [[rng.randint(0, 1) for _ in range(n_bits)] for _ in range(pop_size)]
    best = None
    for _ in range(generations):
        scored = sorted(((fitness(decode(ind)), ind) for ind in pop),
                        key=lambda z: -z[0])
        if best is None or scored[0][0] > best[0]:
            best = (scored[0][0], list(scored[0][1]))
        total = sum(s for s, _ in scored)

        def pick():
            point = rng.random() * total
            acc = 0.0
            for s, ind in scored:
                acc += s
                if acc >= point:
                    return list(ind)
            return list(scored[0][1])

        new_pop = []
        while len(new_pop) < pop_size:
            p1, p2 = pick(), pick()
            if rng.random() < cx_prob:
                cut = rng.randint(1, n_bits - 1)
                c1 = p1[:cut] + p2[cut:]
                c2 = p2[:cut] + p1[cut:]
            else:
                c1, c2 = p1, p2
            for child in (c1, c2):
                for i in range(n_bits):
                    if rng.random() < mut_prob:
                        child[i] = 1 - child[i]
                if len(new_pop) < pop_size:
                    new_pop.append(child)
        pop = new_pop
    return {"best_value": best[0], "best_bits": "".join(map(str, best[1])),
            "best_decoded": decode(best[1])}


# ================================================================ 内置安全问题
def _quad1d(x):
    return (x[0] - 3.0) ** 2                      # 最优 x=3


def _quad2d(x):
    return (x[0] - 2.0) ** 2 + (x[1] + 1.0) ** 2  # 最优 (2,-1)


def _uncon_2d(x):
    return (x[0] - 5.0) ** 2 + (x[1] - 5.0) ** 2  # 约束问题的目标，最优 (5,5)


# ================================================================ 技能封装
def skill_golden(problem: str = "quad1d", iters: int = 100) -> dict:
    """黄金分割一维搜索（区间消去→注意力聚焦）。"""
    if problem != "quad1d":
        problem = "quad1d"
    x, it = golden_section(_quad1d, 0.0, 10.0, max_iter=int(iters))
    return {"problem": problem, "optimum_x": round(x, 6),
            "true_optimum": 3.0, "iterations": it}


def skill_gradient(problem: str = "quad2d", lr: float = 0.1,
                   iters: int = 300) -> dict:
    """梯度下降求解（误差负反馈驱动）。"""
    x, it, ok = gradient_descent(_quad2d, [0.0, 0.0],
                                 lr=float(lr), max_iter=int(iters))
    return {"problem": "quad2d", "optimum": [round(v, 6) for v in x],
            "true_optimum": [2.0, -1.0], "iterations": it, "converged": ok}


def skill_newton(problem: str = "quad1d", iters: int = 50) -> dict:
    """牛顿法一维求解（二阶曲率加速）。"""
    x, it, ok = newton_1d(_quad1d, 0.0, max_iter=int(iters))
    return {"problem": "quad1d", "optimum_x": round(x, 6),
            "true_optimum": 3.0, "iterations": it, "converged": ok}


def skill_conjugate(problem: str = "spd_system") -> dict:
    """共轭梯度法求解对称正定方程组（搜索方向 A-共轭）。"""
    A = [[4.0, 1.0], [1.0, 3.0]]
    b = [1.0, 2.0]
    x, it, ok = conjugate_gradient(A, b)
    return {"problem": "spd_system", "solution": [round(v, 6) for v in x],
            "true_solution": [round(1 / 11, 6), round(7 / 11, 6)],
            "iterations": it, "converged": ok}


def skill_simplex(problem: str = "lp_factory") -> dict:
    """单纯形法求解线性规划（顶点游走）。"""
    c = [3.0, 2.0]
    A = [[2.0, 1.0], [1.0, 1.0]]
    b = [100.0, 80.0]
    res = simplex(c, A, b)
    res["problem"] = "lp_factory"
    res["true_optimum"] = [20.0, 60.0]
    res["true_objective"] = 180.0
    return res


def skill_penalty(problem: str = "constrained") -> dict:
    """惩罚函数法求解约束问题（边界惩罚）。"""
    constraints = [lambda x: x[0] + x[1] - 6.0]  # x+y <= 6
    x, ok = penalty_method(_uncon_2d, constraints, [0.0, 0.0])
    return {"problem": "constrained", "optimum": [round(v, 4) for v in x],
            "true_optimum": [3.0, 3.0], "converged": ok}


def skill_genetic(problem: str = "binary_max", generations: int = 40,
                  seed: int = 42) -> dict:
    """遗传算法最大化 x^2（x∈[0,31]，5位二进制；群体进化）。"""
    res = genetic_algorithm(lambda v: v * v, 5,
                            generations=int(generations), seed=int(seed))
    res["problem"] = "binary_max"
    res["true_max_value"] = 31 * 31
    res["true_best_decoded"] = 31
    return res


# ================================================================ 领域包
class OptimizationPack(DomainPack):
    key = "optimization"
    name = "优化求解"
    description = "黄金分割、梯度下降、牛顿、共轭梯度、单纯形、惩罚函数、遗传算法。"
    skills = [
        SkillSpec("golden_section", skill_golden, "黄金分割一维搜索",
                  ["optimization", "line search", "黄金分割"]),
        SkillSpec("gradient_descent", skill_gradient, "梯度下降求解",
                  ["optimization", "gradient", "梯度"]),
        SkillSpec("newton_method", skill_newton, "牛顿法二阶加速",
                  ["optimization", "newton", "牛顿"]),
        SkillSpec("conjugate_gradient", skill_conjugate, "共轭梯度法",
                  ["optimization", "conjugate", "共轭"]),
        SkillSpec("simplex_method", skill_simplex, "单纯形法线性规划",
                  ["optimization", "simplex", "单纯形"]),
        SkillSpec("penalty_method", skill_penalty, "惩罚函数约束优化",
                  ["optimization", "penalty", "约束"]),
        SkillSpec("genetic_algorithm", skill_genetic, "遗传算法群体进化",
                  ["optimization", "genetic", "遗传", "进化"]),
    ]
    roles = [
        RoleSpec("line_searcher", "一维区间搜索",
                 ["golden_section"]),
        RoleSpec("gradient_solver", "梯度/牛顿/共轭求解",
                 ["gradient_descent", "newton_method", "conjugate_gradient"]),
        RoleSpec("global_solver", "单纯形/约束/遗传全局求解",
                 ["simplex_method", "penalty_method", "genetic_algorithm"]),
    ]
    workflows = [
        WorkflowSpec("optimization_pipeline",
                     ["line_searcher", "gradient_solver", "global_solver"],
                     "一维聚焦→局部梯度求解→全局/约束/进化求解"),
    ]
