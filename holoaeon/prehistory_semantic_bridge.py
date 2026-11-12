# -*- coding: utf-8 -*-
"""PL-3 领域语义桥（Prehistory Semantic Bridge）—— 给「零分兜底」补一条可审计的桥。

问题（实测，非推测）：磁吸附 `forge_absorb` 用字符二元组 Dice
（`skill.ngram_dice`）把资产文本与 18 仓身份文本（中文领域名）比对。史前资产
名多为「英文代号 + 中文项目名 + 1331/SUPER-MAS 等通用尾巴」，与仓身份的**中文
领域词几乎零重叠**，于是全 0 分，被 tie-break 兜底到编号最小的 C01 本源——
这是算法兜底，不是归属。

本模块做什么：**只加文本，不改打分函数、不改 tie-break**。桥的两侧都是显式词表：
- 资产侧：从资产名里认出「区分性领域词」（沙盘/法务/医派/数学…）；
- 仓侧：把该领域的同义词挂到 C18 对应仓的身份文本后面。
桥接分 = 同一个 `ngram_dice`(资产文本+资产词, 仓身份+仓词)。旧语义（`forge_absorb`）
一字未动，新口径另出一组分数与记录。

三条硬边界（写进模块字段，不靠嘴说）：
1. **卡库是人写的领域先验，不是理解**。桥只是把先验显式化、可复算、可审计；
   它不会「读懂」资产，只会在词表命中时把两侧拉到同一词汇面。
2. **维度真空不可救**。名字里根本没有领域线索的资产（如纯英文代号），桥后仍
   是 0 分——这类实例登记为 `KNOWN_VACUUM`，**不伪装成已修复**。
3. **零 LLM、零网络、零随机**：纯标准库、纯函数，同输入同输出。

判据（FAIL-able）：
- 基线零分数必须等于实测值（漂了就说明口径变了）；
- 桥后零分数不得高于 `ZERO_AFTER_MAX`，且剩下的必须逐个在 `KNOWN_VACUUM` 册上；
- 15 样本必须有卡命中（真空样本单列）；
- 同一输入连跑两次结果逐字段一致；
- 报告带自摘要，人工改过即 FAIL。
"""

from __future__ import annotations

from typing import Any, Dict, List, Sequence, Tuple

from .c18_cluster import C18_NUMBERING
from .forge_bureau import _repo_identity
from .skill import ngram_dice

BRIDGE_SCHEMA = "PREHISTORY-BRIDGE-v1"
SEAL = "潮起开门，潮落闭嘴"

# 实测基线：name-only 口径下 15 样本有 13 个零分（策划案记「4 个」是带描述文本
# 的另一口径，两者不可混比——见回执 feed_corrections）。
EXPECTED_ZERO_BEFORE = 13
ZERO_AFTER_MAX = 1

# 维度真空：名字里没有可用领域线索，桥不伪装修复
KNOWN_VACUUM: Tuple[str, ...] = ("SG-MASTER-SONGJIANG",)

# 两侧显式词表。asset_terms 只收「区分性词」——绝不放 1331/矩阵/runtime 这类
# 几乎所有资产都带的通用尾巴，否则会把全部资产一起拽向同一仓。
LEXICON: Tuple[Dict[str, Any], ...] = (
    {"label": "cosmos", "cang": "C18",
     "asset_terms": ("沙盘", "宇宙", "母体", "arena", "星图"),
     "cang_terms": ("沙盘", "宇宙", "母体", "总沙盘")},
    {"label": "risk_legal", "cang": "C15",
     "asset_terms": ("法务", "合规", "审计", "验证", "安全", "风险", "门控", "隐私"),
     "cang_terms": ("法务", "合规", "审计", "安全", "隐私", "门控", "验证", "风险")},
    {"label": "education", "cang": "C05",
     "asset_terms": ("教育", "课程", "教学", "早课", "教材", "学堂", "学习"),
     "cang_terms": ("教育", "课程", "教学", "学习", "教材", "早课")},
    {"label": "creation", "cang": "C08",
     "asset_terms": ("创作", "工坊", "邮差", "作品", "叙事", "剧本"),
     "cang_terms": ("创作", "工坊", "作品", "表达", "叙事")},
    {"label": "time_arch", "cang": "C13",
     "asset_terms": ("考古", "历史", "纪元", "遗迹", "编年", "朝代", "年表"),
     "cang_terms": ("考古", "历史", "时间", "周期", "遗迹", "纪元")},
    {"label": "craft_math", "cang": "C14",
     "asset_terms": ("数学", "张量", "拓扑", "算子", "几何", "微积分", "拆解", "算法"),
     "cang_terms": ("数学", "张量", "拓扑", "算子", "几何", "算法", "拆解")},
    {"label": "meridian_med", "cang": "C03",
     "asset_terms": ("医派", "中医", "经络", "脉学", "针灸", "方证", "本草"),
     "cang_terms": ("经络", "医派", "中医", "脉", "针", "方证", "本草")},
    {"label": "body_med", "cang": "C02",
     "asset_terms": ("医院", "临床", "康复", "病案", "诊疗", "健康", "养生"),
     "cang_terms": ("身体", "临床", "康复", "诊疗", "健康")},
    {"label": "meaning", "cang": "C11",
     "asset_terms": ("儒释道", "三教", "修行", "意义", "禅", "佛学", "道学"),
     "cang_terms": ("意义", "儒释道", "三教", "修行", "禅", "佛", "儒")},
    {"label": "relation", "cang": "C09",
     "asset_terms": ("关系", "人际", "协作", "社交", "团队", "联盟"),
     "cang_terms": ("关系", "人际", "协作", "团队", "联盟", "社交")},
    {"label": "career", "cang": "C06",
     "asset_terms": ("办公", "职业", "履历", "公文", "秘书", "效率"),
     "cang_terms": ("办公", "职业", "公文", "秘书", "效率", "履历")},
    {"label": "sovereign", "cang": "C01",
     "asset_terms": ("主权", "认知", "身份", "归零", "本源", "自我"),
     "cang_terms": ("本源", "身份", "认知", "主权", "归零", "自我")},
    {"label": "wealth", "cang": "C07",
     "asset_terms": ("财富", "资产", "投资", "配置", "金流"),
     "cang_terms": ("财富", "资产", "投资", "配置", "金流")},
    {"label": "skill_master", "cang": "C14",
     "asset_terms": ("技巧", "技法", "工艺", "手工", "手法"),
     "cang_terms": ("技能", "技艺", "方法", "工具", "手作")},
)

# 15 个样本（顶层名截断后仍可复算；与策划案 §6 同源，取 CSV 命中行）
SAMPLES: Tuple[str, ...] = (
    "总沙盘母体Arena1331x1331多智能体矩阵V3实战化_20261024",
    "王静斋V3.0_runtime_独立验证与安全审计报告_20261018.md",
    "天元法务金刚1331x1331超级矩阵V3实战化_20261018",
    "超级办公之王1331x1331超级矩阵V3实战化_20261020",
    "隐私门控路由本地化1331x1331多智能体矩阵V3实战化_20261031",
    "AI教育大师每日课程",
    "认知主权1331x1331多智能体矩阵V3实战化_20261030",
    "世界考古大师1331x1331超级矩阵V3实战化_20261020",
    "潮起邮差_四重宇宙创作工坊_20261019",
    "儒释道三教合一1331x1331_SUPER-MAS-V3.0_runtime_20261018.zip",
    "数学大师1331_数学史早课",
    "海派中医全派1331x1331超级矩阵V3_runtime_v3.zip",
    "SG-MASTER-SONGJIANG-1331x1331-SUPER-MAS-V3.0_runtime_20261019.zip",
    "吴门医派1331x1331_SUPER-MAS-V3.0_runtime_20261018.zip",
    "张量拆解双王矩阵实战化_20261017",
)


# ---------------------------------------------------------------- 卡片识别
def normalize(name: str) -> str:
    """小写 + 去空白（与 ngram_dice 的归一化口径同源，便于对照）。"""
    return "".join((name or "").lower().split())


def card_for(name: str) -> Dict[str, Any]:
    """从资产名认出领域卡：命中的词、标签、目标仓。

    只做子串命中——不做词干化、不做同义词扩展、不做任何推理。命中即证据，
    未命中即无证据（真空）。
    """
    low = normalize(name)
    hits: List[Dict[str, Any]] = []
    for rule in LEXICON:
        terms = [t for t in rule["asset_terms"] if t in low]
        if terms:
            hits.append({"label": rule["label"], "cang": rule["cang"],
                         "terms": terms})
    labels = [h["label"] for h in hits]
    return {
        "name": name,
        "labels": labels,
        "targets": sorted({h["cang"] for h in hits}),
        "matched_terms": sorted({t for h in hits for t in h["terms"]}),
        "hits": hits,
        "vacuum": (not hits) and any(v in name for v in KNOWN_VACUUM),
        "evidence": "lexicon_substring" if hits else "none",
    }


def _is_vacuum(name: str) -> bool:
    return any(v in name for v in KNOWN_VACUUM)


# ---------------------------------------------------------------- 桥接文本
def asset_text(spec: Dict[str, Any]) -> str:
    """资产原文本（与 forge_absorb 完全同构：name；description；tags）。"""
    return "{}；{}；{}".format(
        spec.get("name", ""),
        spec.get("description", ""),
        "、".join(spec.get("tags") or []),
    )


def cang_text(cang: Dict[str, Any]) -> str:
    """仓身份原文本（与 forge_bureau._repo_identity 同构）。"""
    return _repo_identity(cang)


def cang_bridge_text(cang: Dict[str, Any]) -> str:
    """仓侧桥接文本 = 原身份 + 该仓所有 cang_terms。"""
    ext = [t for rule in LEXICON if rule["cang"] == cang["id"]
           for t in rule["cang_terms"]]
    base = cang_text(cang)
    return base + ("；" + "、".join(ext) if ext else "")


def asset_bridge_text(spec: Dict[str, Any]) -> str:
    """资产侧桥接文本 = 原文本 + 命中词（照抄名字里的词，不生成新词）。"""
    base = asset_text(spec)
    card = card_for(spec.get("name", ""))
    terms = card["matched_terms"]
    return base + ("；" + "、".join(terms) if terms else "")


# ---------------------------------------------------------------- 打分
def score_table(spec: Dict[str, Any], bridged: bool = False) -> List[Tuple[float, str, str]]:
    """18 仓全量打分，排序口径与 forge_absorb 一致：(-分, 仓名)。"""
    left = asset_bridge_text(spec) if bridged else asset_text(spec)
    rows = []
    for c in C18_NUMBERING:
        right = cang_bridge_text(c) if bridged else cang_text(c)
        rows.append((ngram_dice(left, right), c["repo"], c["domain"]))
    rows.sort(key=lambda t: (-t[0], t[1]))
    return rows


def bridged_absorb(spec: Dict[str, Any]) -> Dict[str, Any]:
    """桥前/桥后双分数对照记录。旧语义不改，新口径另成一组。"""
    base = score_table(spec, bridged=False)
    bridged = score_table(spec, bridged=True)
    base_best, base_runner = base[0], base[1]
    best, runner = bridged[0], bridged[1]
    card = card_for(spec.get("name", ""))
    cang = next(c for c in C18_NUMBERING if c["repo"] == best[1])
    return {
        "skill": spec.get("name", ""),
        "baseline": {"repo": base_best[1], "domain": base_best[2],
                     "score": round(base_best[0], 4),
                     "runner_up": round(base_runner[0], 4)},
        "bridged": {"repo": best[1], "cang": cang["id"], "domain": best[2],
                    "score": round(best[0], 4),
                    "runner_up": round(runner[0], 4)},
        "delta": round(best[0] - base_best[0], 4),
        "card": {"labels": card["labels"], "terms": card["matched_terms"],
                 "targets": card["targets"], "evidence": card["evidence"],
                 "vacuum": card["vacuum"]},
        "repaired": base_best[0] == 0.0 and best[0] > 0.0,
        "still_zero": best[0] == 0.0,
        "note": "桥只加文本：打分函数仍是 ngram_dice，tie-break 仍是小编号仓",
        "seal": SEAL,
    }


def compare(samples: Sequence[str] = SAMPLES) -> Dict[str, Any]:
    """15 样本对照：逐样本桥前/桥后 + 汇总。"""
    rows = []
    for name in samples:
        rec = bridged_absorb({"name": name, "description": "", "tags": []})
        rows.append(rec)
    zero_before = [r for r in rows if r["baseline"]["score"] == 0.0]
    zero_after = [r for r in rows if r["bridged"]["score"] == 0.0]
    no_card = [r for r in rows if r["card"]["evidence"] == "none"]
    vacuum = [r for r in rows if r["card"]["vacuum"]]
    changed = [r for r in rows
               if r["baseline"]["repo"] != r["bridged"]["repo"]]
    return {
        "schema": BRIDGE_SCHEMA,
        "samples": len(rows),
        "zero_before": len(zero_before),
        "zero_after": len(zero_after),
        "no_card": len(no_card),
        "vacuum": len(vacuum),
        "cang_changed": len(changed),
        "zero_before_list": [r["skill"] for r in zero_before],
        "zero_after_list": [r["skill"] for r in zero_after],
        "no_card_list": [r["skill"] for r in no_card],
        "rows": rows,
        "seal": SEAL,
    }


# ---------------------------------------------------------------- 自检与校验
FAILS = (
    "baseline_drift",
    "zero_after_exceeds",
    "unregistered_zero",
    "no_card_exceeds",
    "nondeterministic",
    "self_digest",
)


def digest(report: Dict[str, Any]) -> str:
    """自摘要：只覆盖判决相关字段，避免把行序/时间戳搅进来。"""
    import hashlib
    import json
    payload = {
        "schema": report.get("schema"),
        "samples": report.get("samples"),
        "zero_before": report.get("zero_before"),
        "zero_after": report.get("zero_after"),
        "no_card": report.get("no_card"),
        "vacuum": report.get("vacuum"),
        "cang_changed": report.get("cang_changed"),
        "zero_after_list": report.get("zero_after_list"),
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def check_bridge(samples: Sequence[str] = SAMPLES) -> Dict[str, Any]:
    """自检：口径漂移、零分残留、覆盖、确定性。"""
    rep1 = compare(samples)
    rep2 = compare(samples)
    det = all(
        rep1["rows"][i]["baseline"] == rep2["rows"][i]["baseline"]
        and rep1["rows"][i]["bridged"] == rep2["rows"][i]["bridged"]
        for i in range(len(rep1["rows"]))
    )
    problems: List[str] = []
    if rep1["zero_before"] != EXPECTED_ZERO_BEFORE:
        problems.append("baseline_drift：基线零分 %d≠实测 %d"
                        % (rep1["zero_before"], EXPECTED_ZERO_BEFORE))
    if rep1["zero_after"] > ZERO_AFTER_MAX:
        problems.append("zero_after_exceeds：桥后零分 %d>上限 %d"
                        % (rep1["zero_after"], ZERO_AFTER_MAX))
    unregistered = [n for n in rep1["zero_after_list"] if not _is_vacuum(n)]
    if unregistered:
        problems.append("unregistered_zero：未登记真空 %s" % unregistered)
    if rep1["no_card"] - rep1["vacuum"] > 0:
        problems.append("no_card_exceeds：有卡缺失但非真空 %d"
                        % (rep1["no_card"] - rep1["vacuum"]))
    if not det:
        problems.append("nondeterministic：两次结果不一致")
    return {
        "schema": BRIDGE_SCHEMA,
        "pass": not problems,
        "problems": problems,
        "stats": {k: rep1[k] for k in
                  ("samples", "zero_before", "zero_after", "no_card",
                   "vacuum", "cang_changed")},
        "report_digest": digest(rep1),
        "note": "零分下降=可复算判据；真空单列，不伪装成已修复",
        "seal": SEAL,
    }


def verify_bridge(report: Dict[str, Any], expect_digest: str = "") -> Dict[str, Any]:
    """对一份对照报告做四失败面校验（缺一即 FAIL）。"""
    problems: List[str] = []
    if report.get("schema") != BRIDGE_SCHEMA:
        problems.append("self_digest：schema 非法")
    if report.get("zero_before", -1) != EXPECTED_ZERO_BEFORE:
        problems.append("baseline_drift")
    if report.get("zero_after", 999) > ZERO_AFTER_MAX:
        problems.append("zero_after_exceeds")
    unregistered = [n for n in (report.get("zero_after_list") or [])
                    if not _is_vacuum(n)]
    if unregistered:
        problems.append("unregistered_zero：%s" % unregistered)
    if (report.get("no_card", 0) - report.get("vacuum", 0)) > 0:
        problems.append("no_card_exceeds")
    got = digest(report)
    if expect_digest and got != expect_digest:
        problems.append("self_digest：%s≠%s" % (got, expect_digest))
    return {"schema": BRIDGE_SCHEMA, "pass": not problems,
            "problems": problems, "digest": got,
            "fail_faces": list(FAILS), "seal": SEAL}


def probe() -> Dict[str, Any]:
    """一行可复算的总览。"""
    return check_bridge()
