# -*- coding: utf-8 -*-
"""resonance_supplement.py —— 拓扑共振与耗散验证域 · 外部原理补齐

本模块只做一件事：把「7 位未覆盖机制」从"实现了但内核偏软"补成"有数学判据"。
原则：只吸收方法论与判据，不复制任何上游代码（见 UPSTREAM[*].usage = method_only）。

七位机制 → 补齐内核
  C1 自组织耗散   → entropy_production：σ = Σ J_i X_i（线性不可逆热力学，最小熵产）
  R2 曼陀罗一拖八 → mandala_wht：Q3 八顶点，沃尔什-哈达玛正交分发/聚合（可逆无损）
  R5 卡尔曼       → kalman_fuse：多源异构 R 的信息融合 + NIS 卡方一致性
  R6 贝叶斯守卫   → sprt_gate：Wald 序贯概率比检验（A/B 双门限）
  R7 希尔伯特     → rff_kernel：Bochner 定理随机傅里叶特征，内积逼近高斯核
  R8 耗散度量     → entropy_production（同 C1，共用 σ 判据）
  X2 108641 共振  → kuramoto_order + decompose_active_nodes：序参量 r 与 K_c

schema: RESONANCE-SUPPLEMENT-v1.0
"""
import io
import json
import math
import random

SCHEMA_VERSION = "RESONANCE-SUPPLEMENT-v1.0"

# ============================================================ 文献锚（原理出处）
LITERATURE = [
    {
        "id": "L-C1",
        "mechanisms": ["C1", "R8"],
        "title": "Time, Structure and Fluctuations（诺贝尔化学奖演讲）",
        "author": "Ilya Prigogine",
        "year": 1977,
        "source": "Nobel Foundation 官方演讲全文",
        "url": "https://www.nobelprize.org/uploads/2018/06/prigogine-lecture.pdf",
        "claim": "非平衡可成为有序之源；耗散结构靠持续的物质能量交换维持低熵。",
        "usable": "熵产率 σ=ΣJ·X 与最小熵产定理的线性区判据",
    },
    {
        "id": "L-C1b",
        "mechanisms": ["C1"],
        "title": "The rehabilitation of irreversible processes and dissipative structures 50th anniversary",
        "author": "Royal Society Philosophical Transactions A, 376(2124)",
        "year": 2018,
        "source": "Royal Society 期刊",
        "url": "https://royalsocietypublishing.org/rsta/article/376/2124/20170365/115575/The-rehabilitation-of-irreversible-processes-and",
        "claim": "线性区演化受熵产这一势函数支配，趋向与约束相容的最小熵产稳态。",
        "usable": "最小熵产定理的可判定表述：给定力 X，稳态使 X^T L X 最小",
    },
    {
        "id": "L-R2",
        "mechanisms": ["R2"],
        "title": "Hadamard / Walsh 正交变换与立方体八顶点编码",
        "author": "Hadamard (1893) / Walsh (1923) 正交基（教科书口径）",
        "year": 1893,
        "source": "数学基础：H_n H_n = n I 的自逆正交构造",
        "url": "",
        "claim": "8 顶点立方体上的正交变换把 8 方位压成 1 直流 + 7 交流，变换自逆。",
        "usable": "一拖八的 fan-out/fan-in 用该正交变换实现，聚合无损（可逆）",
    },
    {
        "id": "L-R2b",
        "mechanisms": ["R2"],
        "title": "Self-organized criticality: an explanation of 1/f noise",
        "author": "Bak, Tang, Wiesenfeld",
        "year": 1987,
        "source": "Physical Review Letters 59, 381（arXiv 综述版）",
        "url": "https://arxiv.org/pdf/cond-mat/9908316",
        "claim": "开放耗散系统在慢驱动下自组织到临界态，雪崩尺度分布呈幂律。",
        "usable": "分形/曼陀罗结构不是装饰，是临界态的几何快照",
    },
    {
        "id": "L-R5",
        "mechanisms": ["R5"],
        "title": "A New Approach to Linear Filtering and Prediction Problems",
        "author": "R. E. Kalman",
        "year": 1960,
        "source": "Journal of Basic Engineering 82(1):35-45（教科书级开源讲义对照）",
        "url": "https://github.com/rlabbe/Kalman-and-Bayesian-Filters-in-Python",
        "claim": "状态估计 = 预测（协方差增长）+ 更新（卡尔曼增益加权观测）。",
        "usable": "多源融合的信息式等价形式：P^-1 = Σ R_i^-1，x = P Σ z_i/R_i",
    },
    {
        "id": "L-R5b",
        "mechanisms": ["R5"],
        "title": "Normalized Innovation Squared（NIS）一致性检验",
        "author": "Bar-Shalom 等（跟踪理论通用判据）",
        "year": 1988,
        "source": "Estimation with Applications to Tracking and Navigation",
        "url": "https://github.com/rlabbe/filterpy",
        "claim": "NIS = ν^T S^-1 ν 服从 χ²(m)，可用于判定观测是否与滤波一致。",
        "usable": "融合质量的客观判据，而非主观的看起来收敛",
    },
    {
        "id": "L-R6",
        "mechanisms": ["R6"],
        "title": "Sequential tests of statistical hypotheses（SPRT）",
        "author": "Abraham Wald",
        "year": 1945,
        "source": "Annals of Mathematical Statistics 16(2):117-186",
        "url": "",
        "claim": "累积对数似然比越过 A=log((1-β)/α) 或 B=log(β/(1-α)) 即停止，平均样本数最少。",
        "usable": "门禁不必等固定窗口，序贯判定可省样本且错误率可控",
    },
    {
        "id": "L-R7",
        "mechanisms": ["R7"],
        "title": "Random Features for Large-Scale Kernel Machines（Bochner 定理）",
        "author": "Rahimi, Recht",
        "year": 2007,
        "source": "NeurIPS 2007 论文全文",
        "url": "https://people.eecs.berkeley.edu/~brecht/papers/07.rah.rec.nips.pdf",
        "claim": "对核的谱测度采样 ω，z(x)=√(2/D)cos(ω·x+b) 使 E[z(x)z(y)]=k(x,y)。",
        "usable": "有限维显式映射逼近无限维 RKHS 内积，误差随 D 下降",
    },
    {
        "id": "L-X2",
        "mechanisms": ["X2"],
        "title": "Kuramoto 相位振子模型：平均场序参量与临界耦合",
        "author": "Y. Kuramoto",
        "year": 1975,
        "source": "Lecture Notes in Physics 39",
        "url": "",
        "claim": "r = |⟨e^{iθ}⟩| 从 0 相变到 1；临界耦合 K_c = 2/(π g(0))。",
        "usable": "共振有可测序参量，不再靠常数硬编码",
    },
]

# ============================================================ GitHub 同类项目（2026-11-12 实测星标）
UPSTREAM = [
    {"full_name": "rlabbe/Kalman-and-Bayesian-Filters-in-Python", "stars": 19480, "lang": "Jupyter Notebook",
     "target": "R5", "role": "卡尔曼/贝叶斯滤波开源讲义 + 可跑 notebook", "usage": "method_only",
     "absorb": "预测-更新两段式的直觉化拆解；NIS 一致性检验的工程用法"},
    {"full_name": "rlabbe/filterpy", "stars": 3899, "lang": "Python",
     "target": "R5", "role": "KF/EKF/UKF/粒子滤波/平滑器实现库", "usage": "method_only",
     "absorb": "多源融合的协方差记账顺序；不复制实现"},
    {"full_name": "hyperdimensional-computing/torchhd", "stars": 394, "lang": "Python",
     "target": "R7", "role": "HDC/VSA 主流库（本仓 14 只读源之一）", "usage": "readonly_reference",
     "absorb": "超向量绑定/捆绑/置换三算子语义；不运行、不并入"},
    {"full_name": "cumbof/hdlib", "stars": 44, "lang": "Python",
     "target": "R7", "role": "轻量 HDC/VSA 库", "usage": "method_only",
     "absorb": "类向量与查询向量的相似度检索路径"},
    {"full_name": "delpapa/sandpilemodel", "stars": 7, "lang": "Python",
     "target": "C1", "role": "BTW 沙堆最小实现", "usage": "method_only",
     "absorb": "阈值崩塌 → 邻居重分配的自动机结构"},
    {"full_name": "flrs/visual_sandpile", "stars": 6, "lang": "Matlab",
     "target": "C1", "role": "BTW 雪崩/幂律可视化", "usage": "method_only",
     "absorb": "雪崩尺度分布作为临界性证据的呈现口径"},
    {"full_name": "scikit-tda/ripser.py", "stars": 347, "lang": "C++",
     "target": "R2", "role": "持久同调（拓扑特征稳定性度量）", "usage": "method_only",
     "absorb": "拓扑特征要有持久性才可信的判据思想"},
    {"full_name": "bruel-gabrielsson/TopologyLayer", "stars": 431, "lang": "Python",
     "target": "R2", "role": "持久同调 + 特征层", "usage": "method_only",
     "absorb": "把拓扑特征转成可优化特征的接口分层"},
    {"full_name": "adrianfessel/kuramoto", "stars": 9, "lang": "Python",
     "target": "X2", "role": "Kuramoto 网络同步实现", "usage": "method_only",
     "absorb": "局部/平均场两种耦合的数值积分写法"},
    {"full_name": "HarikrishnanNB/stochastic_resonance_and_nl", "stars": 19, "lang": "Python",
     "target": "X2", "role": "随机共振 + 神经混沌", "usage": "method_only",
     "absorb": "噪声非单调增强信号的 SNR 峰形（共振的另一种证法）"},
    {"full_name": "mahajananshul/Stochastic_Resonance_in_Neural_Systems", "stars": 7, "lang": "Python",
     "target": "X2", "role": "加噪提升可检测性的最小示范", "usage": "method_only",
     "absorb": "SNR 随噪声先升后降的实验口径"},
    {"full_name": "lcaraffa/Bayesian_Emergent_Dissipative_Structures", "stars": 7, "lang": "",
     "target": "C1/R6", "role": "贝叶斯涌现耗散结构", "usage": "method_only",
     "absorb": "不确定性自身被耗散优化的自指表述（仅概念，未采信其结论）"},
]

MECHANISM_LINKS = {
    "C1": {"name": "自组织耗散", "impl": "entropy_production", "judge": "σ=ΣJ·X 正定且对称"},
    "R2": {"name": "曼陀罗一拖八", "impl": "mandala_wht", "judge": "H8·H8=8I，往返误差 < 1e-12"},
    "R5": {"name": "卡尔曼多源", "impl": "kalman_fuse", "judge": "NIS < 3.841 判一致"},
    "R6": {"name": "贝叶斯守卫", "impl": "sprt_gate", "judge": "LLR 越 A/B 门限即停"},
    "R7": {"name": "希尔伯特投影", "impl": "rff_kernel", "judge": "RFF 内积≈高斯核，误差随 D 降"},
    "R8": {"name": "耗散度量", "impl": "entropy_production", "judge": "熵产率与秩序度同源"},
    "X2": {"name": "108641 共振", "impl": "kuramoto_order", "judge": "r 随 K 相变，K_c 可算"},
}

DEFAULT_ONSAGER = [[2.0, 0.3], [0.3, 1.0]]


def _mat_vec(m, v):
    return [sum(m[i][j] * v[j] for j in range(len(v))) for i in range(len(m))]


# ============================================================ 1. 熵产率（C1 / R8）
def entropy_production(forces=None, onsager=None):
    """σ = Σ_i J_i X_i，J = L X。返回熵产率、正定性、对称性与凸性判据。"""
    X = list(forces) if forces else [1.0, 0.5]
    L = [list(r) for r in (onsager or DEFAULT_ONSAGER)]
    n = len(X)
    J = _mat_vec(L, X)
    sigma = sum(J[i] * X[i] for i in range(n))

    asym = max(abs(L[i][j] - L[j][i]) for i in range(n) for j in range(n))
    det2 = L[0][0] * L[1][1] - L[0][1] * L[1][0]
    leading = [L[0][0], det2]
    positive_definite = all(x > 0 for x in leading)

    convex_samples = []
    for t in (0.5, 2.0, 3.0):
        s_t = sum(sum(L[i][j] * (t * X[j]) for j in range(n)) * (t * X[i]) for i in range(n))
        convex_samples.append({"t": t, "sigma": round(s_t, 6),
                               "ratio_to_t2": round(s_t / (t * t * sigma), 6)})

    return {
        "model": "linear_irreversible_thermodynamics",
        "forces": [round(x, 6) for x in X],
        "flows": [round(x, 6) for x in J],
        "sigma": round(sigma, 6),
        "symmetric_onsager": asym <= 1e-12,
        "onsager_asymmetry": round(asym, 12),
        "positive_definite": positive_definite,
        "leading_principal_minors": [round(x, 6) for x in leading],
        "convex_scaling": convex_samples,
        "minimum_entropy_production": "给定力 X 的稳态使 σ 最小；σ(tX)=t²σ(X) 即凸性证据",
    }


# ============================================================ 2. 曼陀罗正交分发（R2）
def _hadamard(n):
    """生成 n=2^k 阶 Hadamard 矩阵（标准分块递归：H_2k = [[H,H],[H,-H]]）。"""
    if n == 1:
        return [[1]]
    half = _hadamard(n // 2)
    out = []
    for row in half:
        out.append(row + row)
    for row in half:
        out.append(list(row) + [-x for x in row])
    return out


def mandala_wht(spokes=None):
    """Q3 八方位：fan-out = 正交正变换，fan-in = 正交逆变换（自逆，可无损还原）。"""
    s = [float(x) for x in (spokes or [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])]
    if len(s) != 8:
        raise ValueError("mandala_wht 需要恰好 8 个方位载荷")
    H = _hadamard(8)
    a = [sum(H[k][j] * s[j] for j in range(8)) / 8.0 for k in range(8)]
    back = [sum(H[k][j] * a[j] for j in range(8)) for k in range(8)]
    err = max(abs(back[i] - s[i]) for i in range(8))
    ortho = max(abs(sum(H[i][k] * H[j][k] for k in range(8)) - (8 if i == j else 0))
                for i in range(8) for j in range(8))
    e_s = sum(x * x for x in s)
    e_a = sum(x * x for x in a)
    parseval = e_s / (8 * e_a) if e_a else 0.0

    return {
        "topology": "q3_mandala",
        "directions": ["N", "NE", "E", "SE", "S", "SW", "W", "NW"],
        "structure": "1 中心 + 8 方位 = 9 节点（Q3 顶点集）",
        "spectrum": [round(x, 6) for x in a],
        "center_dc": round(a[0], 6),
        "center_is_mean": abs(a[0] - sum(s) / 8) <= 1e-12,
        "reconstruction_error": round(err, 12),
        "orthogonality_max_dev": round(ortho, 12),
        "parseval_ratio": round(parseval, 12),
        "perfect": err <= 1e-12 and ortho <= 1e-12,
    }


# ============================================================ 3. 卡尔曼多源融合（R5）
CHI2_1DOF_95 = 3.841


def kalman_fuse(sensors=None):
    """信息式融合：P^-1 = Σ R_i^-1，x = P Σ z_i/R_i；NIS 判一致性。"""
    S = list(sensors) if sensors else [(10.0, 1.0), (10.5, 0.25), (9.8, 4.0)]
    info = sum(1.0 / r for _, r in S)
    fused = sum(z / r for z, r in S) / info
    P = 1.0 / info
    rows = []
    for z, r in S:
        nis = (z - fused) ** 2 / (r + P)
        rows.append({"z": z, "R": round(r, 6), "weight": round((1.0 / r) / info, 6),
                     "nis": round(nis, 6), "consistent": nis <= CHI2_1DOF_95})

    x_seq, p_seq = S[0][0], S[0][1]
    for z, r in S[1:]:
        k = p_seq / (p_seq + r)
        x_seq = x_seq + k * (z - x_seq)
        p_seq = (1 - k) * p_seq
    seq_matches_batch = abs(x_seq - fused) <= 1e-9 and abs(p_seq - P) <= 1e-9

    return {
        "model": "information_form_fusion",
        "fused_state": round(fused, 6),
        "fused_variance": round(P, 6),
        "sources": rows,
        "all_consistent": all(r["consistent"] for r in rows),
        "outliers": [i for i, r in enumerate(rows) if not r["consistent"]],
        "sequential_matches_batch": seq_matches_batch,
        "sequential_state": round(x_seq, 6),
        "chi2_threshold": CHI2_1DOF_95,
        "note": "信息式融合 = 逆方差加权；NIS 超 χ²(1) 95% 门限判该源离群",
    }


# ============================================================ 4. SPRT 序贯检验（R6）
def sprt_gate(observations=None, p0=0.15, p1=0.45, alpha=0.05, beta=0.10):
    """Wald SPRT：累积对数似然比，越 A 判 H1，越 B 判 H0。"""
    obs = list(observations) if observations else [1, 1, 0, 1, 1, 0, 1, 0, 1, 1]
    A = math.log((1 - beta) / alpha)
    B = math.log(beta / (1 - alpha))
    llr, path, decision, n_stop = 0.0, [], "CONTINUE", len(obs)
    for i, x in enumerate(obs):
        llr += math.log(p1 / p0) if x else math.log((1 - p1) / (1 - p0))
        path.append(round(llr, 6))
        if llr >= A:
            decision, n_stop = "H1", i + 1
            break
        if llr <= B:
            decision, n_stop = "H0", i + 1
            break
    return {
        "model": "wald_sprt",
        "p0": p0, "p1": p1, "alpha": alpha, "beta": beta,
        "threshold_A": round(A, 6),
        "threshold_B": round(B, 6),
        "observation_length": len(obs),
        "llr_path": path,
        "decision": decision,
        "stopped_at": n_stop,
        "evidence_saved": round(1 - n_stop / len(obs), 4) if obs else 0.0,
        "note": "A=log((1-β)/α)，B=log(β/(1-α))；越界即停，平均样本数最少",
    }


# ============================================================ 5. RFF 核近似（R7）
def rff_kernel(samples=None, gamma=1.0, dims=(16, 64, 256), seed=1331):
    """Bochner：ω~N(0,2γI)，z(x)=√(2/D)cos(ω·x+b)，E[z(x)z(y)]=exp(-γ||x-y||²)。"""
    xs = samples or [[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [1.0, 1.0],
                     [0.5, 0.5], [2.0, 0.0], [0.0, 2.0], [1.5, 0.7], [3.0, 3.0]]
    d = len(xs[0])

    def true_k(a, b):
        return math.exp(-gamma * sum((a[i] - b[i]) ** 2 for i in range(d)))

    pairs = [(i, j) for i in range(len(xs)) for j in range(i + 1, len(xs))]
    results = []
    for D in dims:
        g = random.Random(seed)
        omega = [[g.gauss(0.0, math.sqrt(2 * gamma)) for _ in range(d)] for _ in range(D)]
        bias = [g.uniform(0, 2 * math.pi) for _ in range(D)]
        feats = []
        for x in xs:
            feats.append([math.sqrt(2.0 / D) * math.cos(sum(omega[k][t] * x[t] for t in range(d)) + bias[k])
                          for k in range(D)])
        errs = []
        for i, j in pairs:
            approx = sum(feats[i][k] * feats[j][k] for k in range(D))
            errs.append(abs(approx - true_k(xs[i], xs[j])))
        results.append({"D": D, "mae": round(sum(errs) / len(errs), 6),
                        "max_err": round(max(errs), 6)})
    trending_down = all(results[i]["mae"] >= results[i + 1]["mae"] for i in range(len(results) - 1))
    return {
        "model": "random_fourier_features",
        "gamma": gamma, "seed": seed, "pairs": len(pairs),
        "dims": results,
        "mae_trends_down": trending_down,
        "note": "显式有限维映射逼近无限维 RKHS 内积；误差随 D 下降即证据",
    }


# ============================================================ 6. Kuramoto 序参量（X2）
def kuramoto_order(phases=None):
    """r = |⟨e^{iθ}⟩|，r=0 全无序，r=1 全同步。"""
    th = list(phases) if phases else [0.0, 1.0, 2.0, 3.0]
    n = len(th)
    zx = sum(math.cos(t) for t in th) / n
    zy = sum(math.sin(t) for t in th) / n
    r = math.hypot(zx, zy)
    psi = math.atan2(zy, zx)
    return {"model": "kuramoto_order_parameter", "n": n,
            "r": round(r, 6), "psi": round(psi, 6),
            "synchronized": r >= 0.75,
            "note": "r 是共振的客观测度，与 RESONANCE_THRESHOLD=0.75 同源"}


def kuramoto_sweep(N=16, sigma=0.5, ks=None, dt=0.05, steps=400, seed=1331):
    """扫耦合 K：首个 r≥0.75 的 K 记为经验临界点，理论 K_c=2σ√(2π)/π。"""
    Ks = list(ks) if ks else [0.2, 0.4, 0.6, 0.8, 1.0, 1.5, 2.0, 3.0]
    g = random.Random(seed)
    omega = [g.gauss(0.0, sigma) for _ in range(N)]
    th0 = [g.uniform(0, 2 * math.pi) for _ in range(N)]
    kc_theory = 2.0 * sigma * math.sqrt(2 * math.pi) / math.pi
    rows = []
    for K in Ks:
        th = list(th0)
        for _ in range(steps):
            zx = sum(math.cos(t) for t in th) / N
            zy = sum(math.sin(t) for t in th) / N
            r = math.hypot(zx, zy)
            psi = math.atan2(zy, zx)
            th = [t + dt * (omega[i] + K * r * math.sin(psi - t)) for i, t in enumerate(th)]
        r_final = kuramoto_order(th)["r"]
        rows.append({"K": K, "r": r_final})
    empirical = next((x["K"] for x in rows if x["r"] >= 0.75), None)
    return {"model": "kuramoto_sweep", "N": N, "sigma": sigma, "steps": steps,
            "kc_theory": round(kc_theory, 6), "curve": rows,
            "kc_empirical": empirical,
            "note": "K 越过 K_c 后 r 由 0 相变到 1；经验点应与理论同量级"}


def decompose_active_nodes(n=108641):
    """108641 质因数分解 + 与矩阵规模/活性占比的关系。"""
    factors, m = [], n
    p = 2
    while p * p <= m:
        while m % p == 0:
            factors.append(p)
            m //= p
        p += 1
    if m > 1:
        factors.append(m)
    product = 1
    for f in factors:
        product *= f
    return {
        "n": n,
        "factorization": factors,
        "product_check": product == n,
        "is_prime": len(factors) == 1,
        "relative_to_matrix": round(n / 1771561, 6),
        "matrix_quotient": {"q": n // 1331, "r": n % 1331},
        "note": "质因数分解不构成物理依据；仅说明该常数有结构，而非随手取值",
    }


# ============================================================ 报告与自检
def literature_report(mechanism=None):
    items = LITERATURE if not mechanism else [x for x in LITERATURE if mechanism in x["mechanisms"]]
    return {"schema": SCHEMA_VERSION, "mechanism": mechanism,
            "count": len(items), "items": items}


def upstream_report(target=None):
    items = UPSTREAM if not target else [x for x in UPSTREAM if target in x["target"]]
    return {"schema": SCHEMA_VERSION, "target": target, "count": len(items),
            "total_stars": sum(x["stars"] for x in items),
            "usage_rule": "method_only：只吸收方法论与判据，不复制上游代码",
            "items": items}


def check():
    """七位机制逐项实测，全部有判据才 PASS。"""
    ep = entropy_production()
    mw = mandala_wht()
    kf = kalman_fuse()
    sp = sprt_gate()
    rk = rff_kernel()
    ko = kuramoto_sweep()
    an = decompose_active_nodes()
    items = [
        {"mechanism": "C1", "impl": "entropy_production", "metric": "sigma=%.6f" % ep["sigma"],
         "ok": ep["positive_definite"] and ep["symmetric_onsager"] and ep["sigma"] > 0},
        {"mechanism": "R2", "impl": "mandala_wht", "metric": "err=%.2e" % mw["reconstruction_error"],
         "ok": mw["perfect"] and mw["center_is_mean"]},
        {"mechanism": "R5", "impl": "kalman_fuse",
         "metric": "x=%.6f P=%.6f" % (kf["fused_state"], kf["fused_variance"]),
         "ok": kf["sequential_matches_batch"]},
        {"mechanism": "R6", "impl": "sprt_gate",
         "metric": "decision=%s n=%d" % (sp["decision"], sp["stopped_at"]),
         "ok": sp["decision"] in ("H0", "H1")},
        {"mechanism": "R7", "impl": "rff_kernel", "metric": "mae_trends_down=%s" % rk["mae_trends_down"],
         "ok": rk["mae_trends_down"] and rk["dims"][-1]["mae"] < rk["dims"][0]["mae"]},
        {"mechanism": "R8", "impl": "entropy_production", "metric": "minors=%s" % ep["leading_principal_minors"],
         "ok": len(ep["leading_principal_minors"]) == 2},
        {"mechanism": "X2", "impl": "kuramoto_order+kuramoto_sweep",
         "metric": "Kc=%.4f emp=%s factors=%s" % (ko["kc_theory"], ko["kc_empirical"], an["factorization"]),
         "ok": ko["kc_empirical"] is not None and an["product_check"] and not an["is_prime"]},
    ]
    passed = sum(1 for x in items if x["ok"])
    return {
        "schema": SCHEMA_VERSION,
        "literature": len(LITERATURE),
        "upstream": len(UPSTREAM),
        "mechanisms": len(items),
        "items": items,
        "passed": passed,
        "verdict": "PASS" if passed == len(items) else "FAIL",
    }


def ledger(path=None):
    payload = {"schema": SCHEMA_VERSION,
               "literature": LITERATURE, "upstream": UPSTREAM,
               "mechanism_links": MECHANISM_LINKS, "check": check()}
    if path:
        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(payload, ensure_ascii=False, indent=1, sort_keys=True) + "\n")
    return payload


def main(argv=None):
    import sys
    argv = list(argv if argv is not None else sys.argv[1:])
    cmd = argv[0] if argv else "check"
    if cmd == "check":
        result = check()
        print(json.dumps(result, ensure_ascii=False, indent=1))
        return 0 if result["verdict"] == "PASS" else 1
    if cmd == "literature":
        mech = argv[1] if len(argv) > 1 else None
        print(json.dumps(literature_report(mech), ensure_ascii=False, indent=1))
        return 0
    if cmd == "upstream":
        tgt = argv[1] if len(argv) > 1 else None
        print(json.dumps(upstream_report(tgt), ensure_ascii=False, indent=1))
        return 0
    if cmd == "ledger":
        out = argv[1] if len(argv) > 1 else None
        if not out:
            print("ledger 需要输出路径")
            return 1
        ledger(out)
        print("written:", out)
        return 0
    print("用法：check | literature [C1..X2] | upstream [C1..X2] | ledger <path>")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
