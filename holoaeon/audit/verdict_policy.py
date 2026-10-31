# -*- coding: utf-8 -*-
"""
VERAX · fail-loud 裁决策略（verdict_policy）
================================================================================
V2 / W10。规范 v0.2 §8 的三条硬红线，任一命中必须 red，且不允许 advice 降级：

  P1 diff0_drift         确定性哈希与冻结值不一致（DIFF≠0）
  P2 mutation_insensitive 篡改自检未能让哈希改变（哈希对内容不敏感）
  P3 golden_unfrozen      黄金值缺失/未冻结（无法证明"同逻辑同哈希"）

为什么单独成模块：它是对"裁决如何形成"的静态约束，不接入内核、不改变任何技能行为。
Kernel 不认识它；只有 CI 入口（verax_verify.py）与测试会调用。
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List

POLICY_ID = "HOLOAEON-VERDICT-POLICY-v0.2"
POLICY_SECTION = "spec-diff0 v0.2 §8"

RULE_IDS: tuple = ("diff0_drift", "mutation_insensitive", "golden_unfrozen")

RULE_TEXT = {
    "diff0_drift": "确定性哈希与冻结值不一致 → 必须 red",
    "mutation_insensitive": "篡改自检未让哈希改变 → 必须 red",
    "golden_unfrozen": "黄金值缺失或未冻结 → 必须 red",
}

ALLOWED_VERDICTS = ("green", "yellow", "red")


def evaluate(diff0_drift: bool = False,
             mutation_sensitive: bool = True,
             golden_frozen: bool = True) -> Dict[str, Any]:
    """按三条硬规则给出裁决；命中任意一条即 red。"""
    hits: List[str] = []
    if diff0_drift:
        hits.append("diff0_drift")
    if not mutation_sensitive:
        hits.append("mutation_insensitive")
    if not golden_frozen:
        hits.append("golden_unfrozen")
    return {
        "policy_id": POLICY_ID,
        "section": POLICY_SECTION,
        "conclusion": "red" if hits else "green",
        "hits": hits,
        "reasons": [RULE_TEXT[h] for h in hits],
        "downgradable": False,
        "rules": list(RULE_IDS),
    }


def enforce(verdict: str, policy: Dict[str, Any]) -> str:
    """把策略结论并入既有裁决：只许"变红"，不许把 red 降级成 yellow/green。

    verdict: 由 attestation 得出的 green / yellow / red
    返回最终结论；policy 命中即为 red。
    """
    if verdict not in ALLOWED_VERDICTS:
        raise ValueError("未知裁决：%r（允许 %s）" % (verdict, ALLOWED_VERDICTS))
    if policy.get("conclusion") == "red":
        return "red"
    return verdict


def assert_no_downgrade(requested: str, policy: Dict[str, Any]) -> None:
    """若策略是 red 而调用方想写 yellow/green，直接抛错（fail loud）。"""
    if policy.get("conclusion") == "red" and requested != "red":
        raise ValueError("策略 %s 命中 %s，禁止降级为 %s"
                         % (POLICY_ID,
                            ",".join(policy.get("hits", [])), requested))


def describe() -> Dict[str, Any]:
    """给文档/README 用的静态描述（不含任何运行态）。"""
    return {"policy_id": POLICY_ID, "section": POLICY_SECTION,
            "rules": [{"id": r, "text": RULE_TEXT[r]} for r in RULE_IDS],
            "downgradable": False}
