# -*- coding: utf-8 -*-
"""领域包：量化分析（quant）。收益、波动、夏普、回撤、均线、回测。
注意：均为确定性的历史数据计算工具，不预测、不荐股、不构成投资建议。"""
from __future__ import annotations

import math
from typing import List

from .base import DomainPack, RoleSpec, SkillSpec, WorkflowSpec

PERIODS = 252  # 年化交易日


def _prices(s: str) -> List[float]:
    return [float(x) for x in s.split(",") if x.strip()]


def returns(prices: str) -> dict:
    """简单收益率序列。"""
    p = _prices(prices)
    r = [round(p[i] / p[i - 1] - 1, 5) for i in range(1, len(p))]
    return {"returns": r}


def volatility(returns_s: str) -> dict:
    """年化波动率（标准差 × sqrt(252)）。"""
    r = [float(x) for x in returns_s.split(",") if x.strip()]
    if len(r) < 2:
        return {"volatility": 0}
    mean = sum(r) / len(r)
    std = math.sqrt(sum((x - mean) ** 2 for x in r) / (len(r) - 1))
    return {"daily_std": round(std, 5),
            "annual_volatility": round(std * math.sqrt(PERIODS), 4)}


def sharpe(returns_s: str, rf: float = 0.0) -> dict:
    """年化夏普比率（rf 为年化无风险利率）。"""
    r = [float(x) for x in returns_s.split(",") if x.strip()]
    if len(r) < 2:
        return {"sharpe": 0}
    mean = sum(r) / len(r)
    std = math.sqrt(sum((x - mean) ** 2 for x in r) / (len(r) - 1))
    if not std:
        return {"sharpe": 0}
    daily_rf = rf / PERIODS
    sr = (mean - daily_rf) / std * math.sqrt(PERIODS)
    return {"sharpe": round(sr, 4)}


def drawdown(returns_s: str) -> dict:
    """最大回撤。"""
    r = [float(x) for x in returns_s.split(",") if x.strip()]
    equity, peak, max_dd = 1.0, 1.0, 0.0
    for x in r:
        equity *= (1 + x)
        peak = max(peak, equity)
        max_dd = min(max_dd, equity / peak - 1)
    return {"max_drawdown": round(max_dd, 4)}


def moving_average(prices: str, window: int = 5) -> dict:
    """简单移动平均（SMA）。"""
    p = _prices(prices)
    w = int(window)
    sma = [round(sum(p[i - w + 1:i + 1]) / w, 4)
           for i in range(w - 1, len(p))]
    return {"window": w, "sma": sma}


def backtest(prices: str, fast: int = 3, slow: int = 5) -> dict:
    """均线交叉教学回测：快线上穿慢线持有，否则空仓。
    仅用于方法演示，不构成投资建议。"""
    p = _prices(prices)
    f, s = int(fast), int(slow)
    if len(p) <= s:
        return {"error": "数据不足"}
    eq, held = 1.0, False
    for i in range(s, len(p)):
        fma = sum(p[i - f + 1:i + 1]) / f
        sma = sum(p[i - s + 1:i + 1]) / s
        held = fma > sma
        if held:
            eq *= (p[i] / p[i - 1])
    bh = p[-1] / p[s]
    return {"strategy_final": round(eq, 4),
            "buy_hold_final": round(bh, 4),
            "note": "教学演示，不构成投资建议"}


class QuantPack(DomainPack):
    key = "quant"
    name = "量化分析"
    description = "收益、波动、夏普、回撤、均线与教学回测。"
    skills = [
        SkillSpec("returns", returns, "收益率序列",
                  ["returns"], {"prices": "str"}),
        SkillSpec("volatility", volatility, "年化波动率",
                  ["risk", "volatility"], {"returns_s": "str"}),
        SkillSpec("sharpe", sharpe, "夏普比率",
                  ["risk", "sharpe"], {"returns_s": "str"}),
        SkillSpec("drawdown", drawdown, "最大回撤",
                  ["risk", "drawdown"], {"returns_s": "str"}),
        SkillSpec("moving_average", moving_average, "移动平均",
                  ["ma", "indicator"], {"prices": "str"}),
        SkillSpec("backtest", backtest, "教学回测",
                  ["backtest", "strategy"], {"prices": "str"}),
    ]
    roles = [
        RoleSpec("quant_analyst", "指标计算",
                 ["returns", "moving_average"]),
        RoleSpec("quant_researcher", "策略研究",
                 ["backtest", "sharpe"]),
        RoleSpec("quant_risk", "风险指标",
                 ["volatility", "drawdown"]),
    ]
    workflows = [
        WorkflowSpec("quant_pipeline",
                     ["quant_analyst", "quant_researcher", "quant_risk"],
                     "指标→策略→风控"),
    ]
