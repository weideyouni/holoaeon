# -*- coding: utf-8 -*-
"""twin_verify — 双轨核对引擎（V44，REA×Craft Anything 融合 · 验证完备性）
D-11 链位：工艺域（第十二环）附属双轨核对层（layer=verify）——
craft_gate（同环流水线）与 phc_recall（ring11 召回层）的验证合成件。
缘起：对偶图揭示两种核对——
  REA 核对的是【底层算得对不对】（3205 组结果·63 字节：确定性复算，字节级）；
  Craft Anything 核对的是【表面长得像不像】（截图≈截图：感知/结构相似）。
P4 第一性原理裁决：对与像是验证的两个正交维度——
  对而不像 = 走样（correct but unlike）；
  像而不对 = 伪合（faithful but wrong）；
  既对且像 = 全息通过（holographic pass）。
正交维度不得加权压缩成单一分数——verdict 用规则合成（exact AND like≥θ），
两指标并列输出、各带处置建议（走样→craft refine 修表层；伪合→复算定位底层）。
指针纪律（诚实化）：「截图≈截图」在 holoaeon 语境=「特征≈特征」——
表层轨只收文本特征/清单特征（零像素）；像素比对委托外部，回填结构化特征
（与 V41 影像指针纪律同构）。
真实复用（不重写）：phc_recall.embed（字符3-gram确定性嵌入，neural=false）
做结构相似；craft_gate.similarity_score 做逐项命中——两轨引擎均已在仓，
本环只做合成与裁决。
关联声明：底层复算精神已在仓（check_sums/EvidenceLedger/risk_score
rule_refs 可复算）——本环=两轨合成的完备性验证，不计 SAME_AS。
零依赖纯标准库（复用同仓 phc_recall/craft_gate/hypervector）。
封口密语：潮起开门，潮落闭嘴。
"""
import hashlib
import time

SEAL = "潮起开门，潮落闭嘴"

CHAIN_POSITION = {
    "ring": 12,
    "layer": "verify（双轨核对层）",
    "name": "双轨核对引擎（REA×Craft Anything 融合）",
    "upstream": ("craft_gate", "phc_recall", "hypervector"),
    "role": "底层复算轨+表层相似轨+四态规则裁决+处置建议+证据链",
    "lineage_note": "复算精神已在仓：两轨合成为完备验证，关联声明不计SAME_AS",
    "disposition_note": "零像素：像素比对委托外部，回填结构化特征",
}

TWIN_AXIOM = ("对而不像=走样；像而不对=伪合；既对且像=全息通过；"
              "对/像正交，不加权压缩")

VERDICTS = {
    "PASS": "全息通过（既对且像）",
    "CORRECT_BUT_UNLIKE": "走样：对而不像——表层 refine（craft refine 循环）",
    "FAITHFUL_BUT_WRONG": "伪合：像而不对——底层复算定位（check_sums 惯例）",
    "FAIL": "双轨皆失——回炉重造",
}


def fingerprint(results_count, byte_size, digest):
    """底层轨（REA 式）指纹：组数·字节数·摘要——确定性，可复算。
    形状对齐对偶图口径「N 组结果 · M 字节」。"""
    for v in (results_count, byte_size):
        if not isinstance(v, int) or v < 0:
            return {"ok": False, "error": "count/size must be non-negative int",
                    "seal": SEAL}
    if not isinstance(digest, str) or len(digest) != 64:
        return {"ok": False, "error": "digest must be sha256 hex",
                "seal": SEAL}
    return {"ok": True, "results": results_count, "bytes": byte_size,
            "digest": digest, "seal": SEAL}


def exact_track(expected, actual):
    """底层轨：指纹相等校验。逐字段 diff（可复算到字段级）。"""
    if not (expected.get("ok") and actual.get("ok")):
        return {"ok": False, "error": "invalid fingerprint input", "seal": SEAL}
    fields = ("results", "bytes", "digest")
    diffs = [f for f in fields if expected[f] != actual[f]]
    return {"ok": not diffs, "track": "exact",
            "matched": not diffs, "diffs": diffs, "seal": SEAL}


def _cosine(a, b):
    num = sum(x * y for x, y in zip(a, b))
    da = sum(x * x for x in a) ** 0.5
    db = sum(x * x for x in b) ** 0.5
    if da == 0 or db == 0:
        return 0.0
    return num / (da * db)


def resemblance_track(space, expected_features, actual_features,
                      checklist=None, matched=None):
    """表层轨（Craft 式）：特征≈特征。两项并列、不加权合并：
      · sim：结构文本相似（phc_recall.embed 确定性嵌入 + 余弦）
      · coverage：清单逐项命中率（craft_gate.similarity_score）
    零像素：特征必须是 str 或 list[str]；bytes 输入拒绝（像素委托外部）。"""
    for name, feats in (("expected", expected_features),
                        ("actual", actual_features)):
        if isinstance(feats, (bytes, bytearray)):
            return {"ok": False, "error": "%s 含像素数据——零像素纪律："
                    "委托外部比对，回填结构化特征" % name, "seal": SEAL}
    fe = " ".join(expected_features) if isinstance(expected_features, list) \
        else str(expected_features)
    fa = " ".join(actual_features) if isinstance(actual_features, list) \
        else str(actual_features)
    from .phc_recall import embed
    sim = round(_cosine(embed(space, fe), embed(space, fa)), 4)
    coverage = None
    if checklist is not None:
        from .craft_gate import similarity_score
        r = similarity_score(checklist, matched or [])
        coverage = r["score"] if r["ok"] else None
    return {"ok": True, "track": "resemblance", "sim": sim,
            "coverage": coverage, "seal": SEAL}


def twin_verdict(exact, resemblance, like_threshold=0.85):
    """四态规则裁决（正交合成，非加权）：verdict + 处置建议。
    like 取 sim；若 coverage 并存，取两者较小值（短板决定像）。"""
    like = resemblance.get("sim", 0.0)
    cov = resemblance.get("coverage")
    if cov is not None:
        like = min(like, cov)
    like_ok = like >= like_threshold
    if exact.get("matched") and like_ok:
        v = "PASS"
    elif exact.get("matched"):
        v = "CORRECT_BUT_UNLIKE"
    elif like_ok:
        v = "FAITHFUL_BUT_WRONG"
    else:
        v = "FAIL"
    return {"ok": True, "verdict": v, "meaning": VERDICTS[v],
            "exact_matched": bool(exact.get("matched")),
            "like": like, "like_threshold": like_threshold,
            "dispositions": {"CORRECT_BUT_UNLIKE":
                             "craft refine 循环修表层",
                             "FAITHFUL_BUT_WRONG":
                             "底层复算逐字段定位（exact.diffs）"},
            "blended_score": None,  # 正交不标量压缩：显式置空
            "seal": SEAL}


class AuditTrail:
    """核对过程证据链（同构 EvidenceLedger/MLPS3）：append-only + SHA 链。"""

    def __init__(self):
        self.entries = []
        self._prev = ""

    def add(self, event, detail):
        digest = hashlib.sha256(
            (self._prev + event + detail).encode("utf-8")).hexdigest()
        self.entries.append({"event": event, "detail": detail,
                             "sha": digest, "ts": time.strftime("%H:%M:%S")})
        self._prev = digest
        return {"ok": True, "count": len(self.entries), "seal": SEAL}

    def verify(self):
        prev = ""
        for i, e in enumerate(self.entries):
            expect = hashlib.sha256(
                (prev + e["event"] + e["detail"]).encode("utf-8")
            ).hexdigest()
            if e["sha"] != expect:
                return {"ok": False, "broken_at": i, "seal": SEAL}
            prev = e["sha"]
        return {"ok": True, "entries": len(self.entries), "seal": SEAL}


def verify_twin(space, expected_fp, actual_fp, expected_features,
                actual_features, checklist=None, matched=None,
                like_threshold=0.85, trail=None):
    """总闸：双轨全跑 + 四态裁决 + 证据链登记。"""
    exact = exact_track(expected_fp, actual_fp)
    rese = resemblance_track(space, expected_features, actual_features,
                             checklist, matched)
    v = twin_verdict(exact, rese, like_threshold)
    out = {"ok": True, "exact": exact, "resemblance": rese,
           "verdict": v["verdict"], "meaning": v["meaning"],
           "disposition": v["dispositions"].get(v["verdict"], "无"),
           "like": v["like"], "blended_score": None, "seal": SEAL}
    if trail is not None:
        trail.add("twin_verdict", out["verdict"])
        out["trail"] = trail.verify()
    return out


def audit():
    """总闸快照：report-only。"""
    return {"seal": SEAL, "ring": CHAIN_POSITION["ring"],
            "layer": CHAIN_POSITION["layer"], "axiom": TWIN_AXIOM,
            "verdicts": sorted(VERDICTS),
            "reused": ("phc_recall.embed", "craft_gate.similarity_score"),
            "zero_pixel": True, "no_blended_score": True, "neural": False}
