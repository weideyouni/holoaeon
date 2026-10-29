# ALGORITHM — Cognitive Optimization & Self-Organizing Search

This document describes the deterministic optimization layer shipped in
`holoaeon/packs/optimization.py`. It implements the classical numerical-optimization
algorithms from a standard *Optimal Design* curriculum and maps them onto the
multi-agent matrix's search behavior.

> **Scope of the metaphor.** "Search direction", "attention focus", "boundary penalty",
> and "population evolution" are **engineering analogies**. The implementation is plain,
> deterministic numerical mathematics — no biological cognition is claimed. Every
> algorithm runs only on **built-in safe benchmarks**; the layer never evaluates an
> arbitrary expression.

---

## 1. Topology and Objective

In classical optimization we build a mathematical model and minimize an objective. Here the
"design variables" are the agents' activation and the graph's collaboration weights. The
optimization layer does **not** optimize the whole framework at runtime; instead it gives
the agents a reusable, deterministic **set of solvers** for well-defined search problems.

| Classical concept | In the framework |
|---|---|
| Design variables | Problem coordinates (deterministic benchmark) |
| Objective `f(x)` | A built-in, closed-form function |
| Constraints `g(x) ≤ 0` | Built-in constraints, handled by the penalty method |
| Search process | Agents/solvers iterating toward an optimum |

---

## 2. Gradient and Numerical Differentiation

The gradient is the direction of steepest ascent; negating it gives steepest descent.
Because objective functions are passed as callables, gradients are approximated by a
**central finite difference** (no symbolic or autodiff dependency):

```
∂f/∂x_k ≈ [ f(x + h·e_k) − f(x − h·e_k) ] / (2h),     h = 1e-6
```

The same difference stencil provides the second derivative used by the Newton method.

---

## 3. One-Dimensional Search — Golden Section (Interval Elimination)

For a unimodal interval `[a, b]`, the golden-section search keeps two interior points at
the golden ratio `φ = (√5 − 1)/2 ≈ 0.618` and eliminates the subinterval that cannot
contain the minimum. Only one new function evaluation is needed per iteration.

- **Analogy:** interval elimination = attention focusing — the solver discards
  low-information regions instead of scanning everything.
- **Benchmark:** `f(x) = (x − 3)²` over `[0, 10]` → `x = 3.0` in 39 iterations.

---

## 4. Unconstrained Optimization

### 4.1 Gradient Descent (error negative-feedback)

Iterate `x ← x − η · ∇f(x)` with a fixed step size `η`. The prediction error drives the
point downhill until the step size falls below tolerance.

- **Benchmark:** `f(x, y) = (x − 2)² + (y + 1)²`, `η = 0.1` → `(2, −1)` in 90 iterations.

### 4.2 Newton's Method (second-order / curvature acceleration)

Using both the first and second derivatives, the 1-D Newton step is `x ← x − f′(x)/f″(x)`.
Accounting for curvature makes convergence much faster near the optimum.

- **Benchmark:** `f(x) = (x − 3)²` → `x = 3.0` in 3 iterations.

### 4.3 Conjugate Gradient (A-conjugate directions)

The conjugate-gradient method solves a symmetric positive-definite system `Ax = b`. Each
new search direction is **A-conjugate** to the previous ones, i.e. `p_iᵀ A p_j = 0`.

> **Correction (important).** Conjugate is **not** the same as orthogonal. Two vectors are
> conjugate *relative to a matrix* `A`; they are not required to satisfy `p_iᵀ p_j = 0`.
> The implementation uses the standard `pAp` denominator and the `β` recurrence.

- **Benchmark:** `A = [[4,1],[1,3]]`, `b = [1,2]` → `x = (1/11, 7/11) ≈ (0.0909, 0.6364)`
  in 2 iterations.

---

## 5. Linear Programming — Tableau Simplex (Vertex Walking)

The simplex method solves `max cᵀx` subject to `Ax ≤ b`, `x ≥ 0`. Slack variables turn the
constraints into a tableau; the algorithm walks between vertices of the feasible polytope by
**pivoting**:

- **Entering variable:** the most negative reduced cost;
- **Leaving variable:** the minimum ratio test;
- the pivot row is normalized and the basis is updated until no improving direction exists.

- **Benchmark:** `max 3x + 2y`, `2x + y ≤ 100`, `x + y ≤ 80`
  → `(x, y) = (20, 60)`, objective `180`, in 2 pivots.

---

## 6. Constrained Optimization — Penalty Method (Boundary Guardrail)

Constraints `g(x) ≤ 0` are folded into a quadratic penalty, converting the problem into a
sequence of unconstrained minimizations:

```
P(x) = f(x) + μ · Σ max(0, g(x))²
```

The penalty coefficient `μ` is doubled each round. As `μ → ∞`, the minimizer converges to
the constrained optimum.

> **Stability detail.** With a large `μ`, a fixed step size oscillates. The step size is
> therefore adapted as `η ≈ 0.2 / (1 + 2μ)`, and `μ` starts at `1` (not `10`).
- **Benchmark:** `min (x−5)² + (y−5)²` subject to `x + y ≤ 6`
  → `(3.0005, 3.0005)` (analytic optimum `(3, 3)`).

> **Claim we do not make.** Good convex-optimization properties **cannot** be obtained by
> "splitting" a non-convex task into convex regions at the boundary. Such a split is not
> generally valid, so the layer does not implement that idea. Convexity is a property of
> the objective itself, not of how a guard partitions a task.

---

## 7. Genetic Algorithm — Population Evolution

A binary-encoded population evolves over generations:

- **Selection:** roulette-wheel selection by fitness;
- **Crossover:** single-point crossover with probability `0.8`;
- **Mutation:** bit-flip with probability `0.05`;
- **Determinism:** a fixed `random.Random(seed)` makes every run reproducible.

- **Benchmark:** maximize `x²` for `x ∈ [0, 31]` (5-bit), `seed = 42`
  → `x = 31`, fitness `961`.

---

## 8. Benchmark Summary

| Solver | Problem | Known optimum | Result |
|---|---|---|---|
| Golden section | `(x−3)²` | `x = 3` | `3.0` |
| Gradient descent | `(x−2)²+(y+1)²` | `(2,−1)` | `(2,−1)` |
| Newton | `(x−3)²` | `x = 3` | `3.0` |
| Conjugate gradient | `Ax=b`, SPD | `(1/11, 7/11)` | `(0.0909, 0.6364)` |
| Simplex | LP factory | `(20,60)`, `180` | `(20,60)`, `180` |
| Penalty | constrained | `(3,3)` | `(3.0005, 3.0005)` |
| Genetic | `max x²`, 5-bit | `31`, `961` | `31`, `961` |

These checks are asserted in self-test group **G16** and in the `TestOptimization` unit-test
class.

---

## 9. Boundaries and Safety

- Objective functions are only the built-in closed-form benchmarks — no `eval`, no
  user-supplied expressions.
- All algorithms use the standard library alone and are deterministic (fixed seeds,
  fixed tolerances).
- The layer is a **solver toolkit**, not a proof of convergence for arbitrary inputs;
  simulation is not proof, and a human remains the final decision authority.
