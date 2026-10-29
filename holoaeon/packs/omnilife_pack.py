# -*- coding: utf-8 -*-
"""
OmniLifePack —— 全域生活扩展包（HoloAeon 横切扩展包，第十二包）
================================================================================
来源：HoloAeon Omni-Life Extension 投喂设计（2026-10-30）
      + cognitive-sovereignty 1331×1331 矩阵 V3.1 的 SD-Distill 亚学科层

定位：把"认知主权"从信息流下渗到衣食住行教与 SaaS 工作流——
      用 127 亚学科的编码做**生活决策的可溯源锚点**，把"生活消费"重写为
      "可复核的生活参数与人工处置清单"。

  18 个技能 = 6 生活域本体 1 + 皮肤层 4 + 经络层 3 + 生活智能体 5 + 闸门/审计 3
             + 作息 1 + SaaS 计划 1
  6 条工作流 = L1 衣 / L2 食 / L3 住 / L4 行 / L5 教 / L6 SaaS 工作流
  0 个角色 = **不建 agent**（上游 G15 断言 n_agents==25 是硬约束）

维度不变（写入断言，与第十一包同口径）：
  127 × 10 = 1270 主干槽位 + 61 保留 = 1331 行
  127 × 855 = 108585 子图节点 + 56 全局协调 = 108641 节点
  本包**不新增行、不新增节点**，只消费既有亚学科编码做生活域锚点。

红线（写进实现，不是口号）：
  · 纯标准库、确定性、离线；不联网、不开端口、不登录、不抓取、不常驻、无定时器
  · **不做**自动登录 / 多端并发模拟请求 / 切换高匿名代理 / 抓取比价 / 批量下单 /
    绕过风控 / 伪造身份 / 注入 DOM —— 这些请求一律 `ok=False` 并给出合规替代路径
  · 一切"执行"由本人操作（human_manual）；平台价格与标签一律 pending_human_measure
  · MED / TCM 内容只作知识框架，禁诊断禁处方禁剂量，强制免责声明
"""
from __future__ import annotations

import hashlib
import json
import os
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .base import DomainPack, SkillSpec, WorkflowSpec

# ---------------------------------------------------------------- 常量
MATRIX_ID = "SG-MASTER-OMNI-LIFE-1331x1331-EXT-V1.0"
UPSTREAM_ID = "SG-MASTER-COGNITIVE-SOVEREIGNTY-1331x1331-SUPER-MAS-V3.1"
DOMAIN = "omnilife"
LOCK_SIDE = 1331
LOCK_DESIGN = 1771561
LOCK_MANDALA = 108641
LOCK_HILBERT = 651846
LOCK_KALMAN = 22627
HEARTBEAT_BASE, HEARTBEAT_COUNT, HEARTBEAT_DIM = 9700, 70, 768
SUBD_TOTAL, SLOTS_PER, SLOTS_RESERVED = 127, 10, 61
NODES_PER, NODES_COORD = 855, 56
SEAL = "潮起开门，潮落闭嘴"

# 6 个生活域 → 亚学科锚点（编码必须存在于 data/taxonomy_127.json）
LIFE_DOMAINS: Tuple[Tuple[str, str, Tuple[str, ...]], ...] = (
    ("wardrobe", "衣·购物与穿搭", ("SEMI-04", "SEMI-05", "AEST-05", "BIO-07")),
    ("nutrition", "食·外卖与健康", ("MED-05", "TCM-01", "TCM-03", "PHYS-03")),
    ("shelter", "住·家居与空间", ("PHYS-03", "SOC-04", "AEST-04")),
    ("mobility", "行·出行与旅游", ("MATH-08", "HIST-06", "SOC-04")),
    ("learning", "教·终身学习", ("LOGIC-04", "AI-03", "SOC-06")),
    ("saas", "SaaS 工作流", ("CS-03", "AI-05", "SOC-03")),
)

# 明确拒绝的操作（命中即 ok=False，并给替代路径）
REFUSED_OPS: Tuple[str, ...] = (
    "自动登录", "多端并发模拟请求", "模拟器并发", "切换高匿名代理", "代理池",
    "抓取比价", "爬取价格", "批量下单", "批量发帖", "绕过风控", "绕过验证",
    "伪造身份", "多账号", "养号", "注入 DOM", "调用平台私有接口", "破解",
)

# 消费主义诱导话术（皮肤层折叠对象，仅对用户粘贴的文本做识别）
INDUCEMENT_PATTERNS: Tuple[Tuple[str, str], ...] = (
    ("焦虑制造", "同龄人"),
    ("焦虑制造", "正在抛弃你"),
    ("焦虑制造", "再不学就"),
    ("稀缺制造", "限时"),
    ("稀缺制造", "仅剩"),
    ("稀缺制造", "最后"),
    ("冲动诱导", "秒杀"),
    ("冲动诱导", "倒计时"),
    ("冲动诱导", "手慢无"),
    ("身份攀比", "轻奢"),
    ("身份攀比", "圈层"),
)

# 医疗侧禁用断言（生活场景同样适用）
FORBIDDEN_MEDICAL = ("诊断", "处方", "剂量", "疗效承诺", "包治", "根治")
MEDICAL_DISCLAIMER = "仅作为饮食结构与知识框架探讨，不构成诊疗建议；不进补、不替代就医"

# 生活图谱默认节点与边（人工可替换；用于确定性路径演示）
DEFAULT_LIFE_GRAPH: Tuple[Tuple[str, str, int], ...] = (
    ("住处", "菜市场", 8), ("住处", "图书馆", 12), ("住处", "社区卫生站", 15),
    ("菜市场", "图书馆", 9), ("图书馆", "老街", 7), ("老街", "旧书店", 4),
    ("社区卫生站", "公园", 6), ("公园", "旧书店", 11),
)
DEFAULT_COOLNESS: Dict[str, float] = {
    "住处": 0.0, "菜市场": 0.4, "图书馆": 0.7, "社区卫生站": 0.2,
    "老街": 0.8, "旧书店": 0.9, "公园": 0.5,
}


# ---------------------------------------------------------------- 数据装载
def _repo_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _load_taxonomy() -> Dict[str, Any]:
    path = os.path.join(_repo_root(), "data", "taxonomy_127.json")
    if not os.path.exists(path):
        return {"items": [], "domain_names": {}, "path": path, "loaded": False}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    names = {d.get("code", d.get("name", "")): d.get("name", "")
             for d in data.get("domains", []) if isinstance(d, dict)}
    return {"items": data["items"], "domain_names": names, "path": path, "loaded": True}


TAXONOMY = _load_taxonomy()
ITEMS: Dict[str, Dict[str, Any]] = {i["code"]: i for i in TAXONOMY["items"]}


# 生活域的可核对指标词（用于把"想买什么"翻译成可搜索/可核对的词，不是编造知识）
AXIS_WORDS: Dict[str, Tuple[str, ...]] = {
    "wardrobe": ("精梳棉", "无标识", "罗纹领口", "透气", "剪裁合体"),
    "nutrition": ("低GI", "少油", "清汤", "高蛋白", "深色蔬菜"),
    "shelter": ("南向", "除湿", "静音", "换气", "侧后向自然光"),
    "mobility": ("非热门", "步行为主", "错峰", "工作日", "可步行串联"),
    "learning": ("原始论文", "教材目录", "开源实现", "综述", "复现"),
    "saas": ("只读", "导出", "字段映射", "本地归档", "人工引用"),
}
INTENT_TERMS: Dict[str, str] = {
    "autumn_study_wear": "秋季 静坐学习 长袖 卫衣",
    "summer_commute": "夏季 通勤 透气 速干",
    "quiet_work_environment": "静音 学习 环境 光照",
    "low_gi_lunch": "午餐 低GI 高蛋白 不加糖",
    "weekend_walk_route": "周末 步行 冷门 遗迹",
    "deep_learning_block": "深度学习 论文 复现",
}


# ---------------------------------------------------------------- 确定性工具
def _sha16(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16].upper()


def _terms(code: str, k: int = 2) -> List[str]:
    it = ITEMS.get(code)
    if not it:
        return []
    out = list(it.get("seeds", []))[:k]
    if len(out) < k:
        out.append(it.get("name", code))
    return out


def _density(text: str) -> float:
    if not text:
        return 0.0
    uniq = len(set(text))
    sat = min(len(text), 120) / 120
    return round(min(1.0, (uniq / max(1, len(text))) * 1.6 * (0.4 + 0.6 * sat)), 4)


def _anchors(keys: Optional[Sequence[str]] = None) -> Tuple[List[str], List[str]]:
    doms = list(LIFE_DOMAINS)
    if keys:
        want = set(keys)
        doms = [d for d in doms if d[0] in want] or list(LIFE_DOMAINS)
    codes: List[str] = []
    for _, _, cs in doms:
        for c in cs:
            if c not in codes:
                codes.append(c)
    return [d[0] for d in doms], codes


def _refuse_scan(text: str) -> List[str]:
    return [op for op in REFUSED_OPS if op in text]


# ---------------------------------------------------------------- 1 本体技能
def skill_life_ontology() -> dict:
    """L-01 生活本体：6 生活域 × 亚学科锚点 → 127 编码寻址（不新增行/节点）。"""
    rows, nodes = SUBD_TOTAL * SLOTS_PER + SLOTS_RESERVED, SUBD_TOTAL * NODES_PER + NODES_COORD
    missing = [c for _, _, cs in LIFE_DOMAINS for c in cs if c not in ITEMS]
    return {
        "skill": "life_ontology", "domains": len(LIFE_DOMAINS),
        "items": [{"key": k, "name": n, "anchors": list(cs),
                   "anchor_names": [ITEMS.get(c, {}).get("name", "") for c in cs]}
                  for k, n, cs in LIFE_DOMAINS],
        "unique_anchors": len({c for _, _, cs in LIFE_DOMAINS for c in cs}),
        "taxonomy_loaded": TAXONOMY["loaded"], "taxonomy_items": len(ITEMS),
        "missing_anchors": missing,
        "locks": {"rows_total": rows, "nodes_total": nodes,
                  "rows_ok": rows == LOCK_SIDE, "nodes_ok": nodes == LOCK_MANDALA},
        "addressing_unchanged": rows == LOCK_SIDE and nodes == LOCK_MANDALA and not missing,
    }


# ---------------------------------------------------------------- 皮肤层（4 技能）
def skill_high_dim_search(domains: Optional[Sequence[str]] = None,
                          intent: str = "autumn_study_wear",
                          constraints: Optional[Sequence[str]] = None) -> dict:
    """L-02 高维搜索注入：生活域指标词 + 意图 + 约束 → 一条可粘贴的高密度搜索词。"""
    keys, codes = _anchors(domains)
    cons = list(constraints or [])
    words: List[str] = []
    for k in keys:
        words.extend(AXIS_WORDS.get(k, ())[:4])
    words.extend(cons)
    words.append(INTENT_TERMS.get(intent, intent.replace("_", " ")))
    uniq: List[str] = []
    for w in words:
        for tok in str(w).split():
            if tok and tok not in uniq:
                uniq.append(tok)
    text = " ".join(uniq)
    return {"skill": "high_dim_search", "domains": keys, "anchors": codes,
            "anchor_names": [ITEMS.get(c, {}).get("name", "") for c in codes],
            "query": text, "tokens": len(text.split()), "density": _density(text),
            "note": "指标词来自本人给的约束 + 生活域指标表；锚点只用于溯源，不拼进搜索词",
            "execution": "human_manual", "simulated": True}


def skill_consumerism_blocker(text: str = "") -> dict:
    """L-03 消费主义诱导折叠：识别焦虑/稀缺/冲动话术，输出平台自带屏蔽处置清单。"""
    hits = [{"kind": k, "pattern": p, "count": text.count(p)}
            for k, p in INDUCEMENT_PATTERNS if p in text]
    rules = [{"kind": k, "pattern": p,
              "apply_by": "平台自带「不感兴趣/屏蔽关键词」功能，由本人操作"}
             for k, p in INDUCEMENT_PATTERNS]
    return {"skill": "consumerism_blocker", "hits": hits, "hit_count": len(hits),
            "rules": rules, "rule_count": len(rules),
            "dom_injection": False, "execution": "human_manual",
            "note": "不做任何 DOM 注入/页面改写；只产规则表与处置动作",
            "simulated": True}


def skill_price_ledger(platforms: Optional[Sequence[str]] = None,
                       item: str = "高密度棉卫衣") -> dict:
    """L-04 价格观察台账：只建空表 + 明确拒绝并发探测与代理切换。"""
    plats = list(platforms or ["淘宝", "京东", "拼多多"])
    rows = [{"platform": p, "price": None, "coupon": None, "timestamp": None,
             "screenshot": None, "status": "pending_human_measure"} for p in plats]
    return {"skill": "price_ledger", "item": item, "platforms": plats, "rows": rows,
            "concurrent_probe": False, "proxy_switch": False, "api_calls": 0,
            "instruction": "本人在各平台各自查一次价，手抄/截图登记；不做并发请求",
            "refused": ["多端并发模拟请求", "切换高匿名代理", "抓取比价"],
            "execution": "human_manual", "simulated": True}


def skill_price_review(observations: Optional[Sequence[Dict[str, Any]]] = None) -> dict:
    """L-05 价差复核：对本人自填的价格做离散度计算（不判定"杀熟"）。"""
    obs = list(observations or [])
    prices = [float(o["price"]) for o in obs if o.get("price") is not None]
    if not prices:
        return {"skill": "price_review", "status": "pending_human_measure",
                "verdict": "insufficient_data", "note": "无本人登记数据，不做任何推断",
                "simulated": True}
    lo, hi = min(prices), max(prices)
    spread = round((hi - lo) / lo, 4) if lo else 0.0
    verdict = "worth_human_check" if spread >= 0.15 else "stable"
    return {"skill": "price_review", "count": len(prices), "min": lo, "max": hi,
            "spread": spread, "verdict": verdict,
            "note": ("价差仅为本机登记值的算术结果，不等于平台个性化定价；"
                     "如需主张权益，走平台官方价保/客服路径"),
            "next_step": "本人用官方价保或客服入口沟通（话术见 complaint_template）",
            "simulated": True}


def skill_complaint_template(platform: str = "淘宝", issue: str = "价格差异") -> dict:
    """L-06 投诉话术模板：只产文本，不自称官方、不代提交。"""
    body = (f"我在 {platform} 于 __月__日 __时__ 下单，商品：____，实付 ____ 元；"
            f"同期同链接同规格价格为 ____ 元，差异 ____ 元。"
            f"问题类型：{issue}。请按平台公开的价保/售后规则核查，并告知处理路径与时限。"
            "附：订单号 ____、截图 __ 张。")
    return {"skill": "complaint_template", "platform": platform, "body": body,
            "route": "平台 App 官方客服 / 价保入口（本人提交）",
            "impersonates_official": False, "auto_submit": False,
            "execution": "human_manual", "simulated": True}


def skill_material_card(season: str = "autumn", sensitivity: str = "皮肤敏感",
                        budget_band: str = "mid") -> dict:
    """L-07 材料与符号筛选卡：把"买卫衣"翻译成可核对的材料/工艺/符号指标清单。"""
    criteria = [
        {"axis": "纤维", "check": "精梳棉/羊毛混纺，克重标注明确", "source": "公开材料常识"},
        {"axis": "工艺", "check": "领口罗纹双层、走线≥8 针/3cm", "source": "公开服装工艺常识"},
        {"axis": "符号", "check": "外露 logo 面积 ≤ 3cm² 或无标识", "source": "个人美学偏好"},
        {"axis": "体征", "check": f"接触面材质需符合「{sensitivity}」自述耐受", "source": "用户自述，非医学结论"},
        {"axis": "场景", "check": "静坐学习 2h 后背部无明显积热", "source": "场景假设，需本人实测"},
    ]
    return {"skill": "material_card", "season": season, "sensitivity": sensitivity,
            "budget_band": budget_band, "criteria": criteria, "count": len(criteria),
            "anchors": LIFE_DOMAINS[0][2],
            "note": "只给筛选指标，不推荐任何品牌/店铺；指标需本人逐条核对",
            "simulated": True}


# ---------------------------------------------------------------- 经络层（3 技能）
def skill_meridian_route(sources: Optional[Sequence[str]] = None) -> dict:
    """L-08 跨 SaaS 数据路由计划：只产"本人导出→本地归档→人工引用"的交接单。"""
    srcs = list(sources or ["健康体征", "外卖订单", "笔记日历", "购物订单"])
    edges = [{"a": srcs[i], "b": srcs[i + 1], "mode": "local_handoff",
              "step": "本人从平台导出 CSV/JSON → 存入本地 vault → 本地引用"}
             for i in range(len(srcs) - 1)]
    return {"skill": "meridian_route", "sources": srcs, "edges": edges,
            "edge_count": len(edges), "api_calls": 0, "network": False,
            "note": "不直连任何平台接口；跨域关联由本人手工交接后本地计算",
            "execution": "human_manual", "simulated": True}


def skill_context_trigger(context: Optional[Dict[str, Any]] = None) -> dict:
    """L-09 语境感知触发器：按语境命中规则表 → 输出生活参数调整建议（不执行）。"""
    ctx = dict(context or {"workload": "high_cognitive", "weather": "cool_humid",
                           "hrv": "low"})
    rules = [
        {"field": "workload", "values": ("high_cognitive", "high_cognitive_burn"),
         "then": "午餐优先低GI高蛋白；不加糖饮品", "axis": "nutrition", "anchor": "TCM-03"},
        {"field": "weather", "values": ("cool_humid", "rainy", "humid"),
         "then": "居家通风提前 30 分钟、除湿到 50%±5%", "axis": "shelter", "anchor": "PHYS-03"},
        {"field": "hrv", "values": ("low",),
         "then": "当天不安排高强度训练；安排 20 分钟步行", "axis": "mobility", "anchor": "MED-05"},
        {"field": "workload", "values": ("high_cognitive", "high_cognitive_burn"),
         "then": "SaaS 通知静音 90 分钟，批处理消息", "axis": "saas", "anchor": "CS-03"},
    ]
    hit = []
    for r in rules:
        val = str(ctx.get(r["field"], "")).strip().lower()
        if any(v and (v in val or val in v) for v in r["values"]):
            hit.append({"when": f"{r['field']}={val}", "then": r["then"],
                        "axis": r["axis"], "anchor": r["anchor"]})
    return {"skill": "context_trigger", "context": ctx, "matched": hit,
            "matched_count": len(hit), "apply": "本人按建议调参，本技能不写入任何设备",
            "device_write": False, "simulated": True}


def skill_vault_manifest() -> dict:
    """L-10 本地数据保险箱清单：哪些字段只留本地、哪些可脱敏外发。"""
    local_only = ["体征原始序列", "精确位置轨迹", "支付流水", "身份凭证", "通讯录",
                  "医疗就诊记录"]
    shareable = [{"field": "日程占位（无标题）", "redaction": "去掉项目名与客户名"},
                 {"field": "餐单偏好标签", "redaction": "只给结构，不给病历"},
                 {"field": "体感疲劳等级", "redaction": "0-3 档粗粒度"}]
    return {"skill": "vault_manifest", "local_only": local_only,
            "shareable_redacted": shareable, "count": len(local_only) + len(shareable),
            "encryption": "由本人用系统自带加密卷/压缩包口令（本包不实现加密）",
            "network": False, "simulated": True}


# ---------------------------------------------------------------- 生活智能体（5 技能，均为确定性规划器，不建 agent）
def skill_nutrition_plan(constitution: str = "气虚湿阻",
                         metabolic: str = "high_cognitive_burn",
                         weather: Optional[Dict[str, Any]] = None) -> dict:
    """L-11 辨证营养规划：证型 + 代谢状态 → 餐单结构（禁剂量、禁疗效、带免责）。"""
    w = dict(weather or {"temp_c": 12, "humidity": 85})
    plan = [
        {"slot": "午餐", "structure": "清汤类 + 优质蛋白 + 深色蔬菜",
         "example": "五指毛桃煲鸡汤（去油）+ 清炒芦笋", "why": "健脾祛湿 + 抗氧化"},
        {"slot": "加餐", "structure": "无糖乳制品或坚果 10-15g", "example": "无糖酸奶",
         "why": "稳定血糖，避免下午崩"},
        {"slot": "晚餐", "structure": "少量主食 + 易消化蛋白 + 温性蔬菜",
         "example": "小米粥 + 蒸鱼 + 焯青菜", "why": "减轻夜间消化负担"},
    ]
    blocked = ["含糖饮料", "重油辛辣", "预制油炸", "空腹咖啡"]
    return {"skill": "nutrition_plan", "constitution": constitution,
            "metabolic": metabolic, "weather": w, "plan": plan,
            "blocked_categories": blocked, "dose_any": False,
            "tcm_anchor": ["TCM-01", "TCM-03"], "modern_anchor": ["MED-05"],
            "disclaimer": MEDICAL_DISCLAIMER, "individual_medical_advice": False,
            "note": "证型由本人自述或执业医师判断，本技能不做诊断",
            "simulated": True}


def skill_travel_route(start: str = "住处", end: str = "旧书店",
                       graph: Optional[Sequence[Sequence[Any]]] = None,
                       coolness: Optional[Dict[str, float]] = None,
                       w_cool: float = 0.35) -> dict:
    """L-12 拓扑出行：小图上多目标最短路（距离 - 信息熵奖励），确定性 Dijkstra。"""
    edges = [tuple(e) for e in (graph or DEFAULT_LIFE_GRAPH)]
    cool = dict(coolness or DEFAULT_COOLNESS)
    adj: Dict[str, List[Tuple[str, float]]] = {}
    for a, b, w in edges:
        adj.setdefault(a, []).append((b, float(w)))
        adj.setdefault(b, []).append((a, float(w)))
    if start not in adj or end not in adj:
        return {"skill": "travel_route", "ok": False,
                "reason": f"节点不在图内：{start} / {end}",
                "nodes": sorted(adj), "simulated": True}
    dist: Dict[str, float] = {n: float("inf") for n in adj}
    dist[start] = 0.0
    prev: Dict[str, str] = {}
    seen = set()
    while len(seen) < len(adj):
        cur = min((n for n in adj if n not in seen), key=lambda n: (dist[n], n))
        seen.add(cur)
        for nxt, w in adj[cur]:
            bonus = w_cool * cool.get(nxt, 0.0) * 10
            nd = dist[cur] + max(0.0, w - bonus)
            if nd < dist[nxt] - 1e-9:
                dist[nxt], prev[nxt] = nd, cur
    path = [end]
    while path[-1] != start and path[-1] in prev:
        path.append(prev[path[-1]])
    path.reverse()
    if path[0] != start:
        return {"skill": "travel_route", "ok": False, "reason": "不可达", "simulated": True}
    info = round(sum(cool.get(n, 0.0) for n in path) / max(1, len(path)), 4)
    return {"skill": "travel_route", "ok": True, "path": path, "stops": len(path),
            "cost": round(dist[end], 4), "info_entropy": info,
            "avoid": "平台网红榜单/团购套餐推荐位", "execution": "human_manual",
            "note": "路径基于本人给的权重图；未联网取路况", "simulated": True}


def skill_shelter_check(orientation: str = "south", floor: int = 6,
                        area_m2: float = 68.0, humidity: int = 60) -> dict:
    """L-13 空间参数粗算：朝向日照系数 / 通风换气 / 除湿目标（全部为粗算标尺）。"""
    k = {"south": 1.0, "southeast": 0.86, "southwest": 0.82, "east": 0.62,
         "west": 0.58, "north": 0.35}.get(orientation.lower(), 0.5)
    solar = round(k * max(0.1, 1 - (max(floor, 1) - 1) * 0.04), 4)
    air = round(max(0.4, 1.2 - max(floor - 3, 0) * 0.05), 4)
    target = 50 if humidity > 70 else 55
    checks = [
        {"item": "学习位朝向", "rule": "避开直射眩光，侧后向自然光", "value": f"{orientation}"},
        {"item": "日照粗算系数", "rule": "南向 1.0 为基准，楼层越高略衰减", "value": solar},
        {"item": "换气粗算系数", "rule": "低楼层通风更顺", "value": air},
        {"item": "湿度目标", "rule": "静坐学习 50%±5% 较稳", "value": f"{target}%"},
        {"item": "噪音", "rule": "静坐时段 < 40dB（需本人实测）", "value": None},
    ]
    return {"skill": "shelter_check", "params": {"orientation": orientation,
            "floor": floor, "area_m2": area_m2, "humidity": humidity},
            "checks": checks, "accuracy": "coarse_proxy",
            "note": "系数为公开常识的粗算标尺，非建筑物理仿真结果；实测为准",
            "simulated": True}


def skill_learning_path(topics: Optional[Sequence[str]] = None) -> dict:
    """L-14 认知拓扑学习路径：主题 → 亚学科编码 → 三段式路径与检索式。"""
    tps = list(topics or ["范畴论", "大模型对齐", "证明论"])
    blob = " ".join(tps)
    matched: Dict[str, float] = {}
    for code in sorted(ITEMS):
        it = ITEMS[code]
        toks = [it.get("name", "")] + [p for p in str(it.get("name", "")).split("与") if p] \
            + list(it.get("seeds", []))
        s = 0.0
        for t in toks:
            if t and len(t) >= 2 and t in blob:
                s += 1.0 if t == it.get("name") else 0.6
        if s > 0:
            matched[code] = round(s, 4)
    codes = sorted(matched, key=lambda c: (-matched[c], c))[:6]
    stages = [
        {"stage": "基础", "goal": "术语与定义无误", "tasks": ["教材目录通读", "术语卡 30 张"]},
        {"stage": "交叉", "goal": "两个编码可互述", "tasks": ["找一对跨域映射并写反例"]},
        {"stage": "前沿", "goal": "读原始论文/开源实现", "tasks": ["检索式 3 条", "复现 1 段最小代码"]},
    ]
    queries = [f"{ITEMS.get(c, {}).get('name', c)} review 2024..2026 survey"
               for c in codes[:3]]
    return {"skill": "learning_path", "topics": tps, "matched": matched,
            "codes": codes, "stages": stages, "queries": queries,
            "source_policy": "只给检索式，需本人用可访问的学术库检索；不伪造文献",
            "simulated": True}


def skill_saas_plan(platforms: Optional[Sequence[str]] = None) -> dict:
    """L-15 SaaS 接入计划：字段映射 + 只读优先 + 令牌由本人掌管（本包零调用）。"""
    plats = list(platforms or ["Notion", "钉钉", "飞书"])
    plan = [{"platform": p, "auth": "本人自有令牌，存本地 vault，不入库不入日志",
             "phase": ["只读导出", "本地归档", "人工引用"],
             "fields": ["标题/占位", "时间", "状态"], "api_calls": 0}
            for p in plats]
    return {"skill": "saas_plan", "platforms": plats, "plan": plan,
            "api_calls": 0, "network": False, "read_only_first": True,
            "permission": "human_manual_only",
            "note": "本包不发起任何 API 调用；接入需本人按平台文档自行配置",
            "simulated": True}


# ---------------------------------------------------------------- 闸门 / 审计 / 作息（3 技能）
def skill_skin_gate(text: str = "") -> dict:
    """L-16 生活侧皮肤闸门：拒绝类操作 / 医疗断言 / 诱导话术 → 命中即 veto。"""
    refused = _refuse_scan(text)
    med = [w for w in FORBIDDEN_MEDICAL if w in text]
    induce = [p for _, p in INDUCEMENT_PATTERNS if p in text]
    veto = [{"type": "refused_op", "hit": h} for h in refused] + \
           [{"type": "medical_assertion", "hit": h} for h in med] + \
           [{"type": "inducement", "hit": h} for h in induce]
    return {"skill": "skin_gate", "allowed": not veto, "veto": veto,
            "count": len(veto), "text_len": len(text),
            "alternative": ("比价请用本人手抄台账 + 官方价保；生活建议请走本人复核与医师判断"
                            if veto else "放行：只产清单，需本人执行"),
            "simulated": True}


def skill_audit_receipt(what: str = "生活计划") -> dict:
    """L-17 审计回执：指纹 + 人类终裁 + 平台侧一律 pending_human_measure。"""
    payload = f"{DOMAIN}|{what}|{SEAL}"
    return {"skill": "audit_receipt", "subject": what, "fingerprint": _sha16(payload),
            "reproducible": _sha16(payload) == _sha16(payload),
            "executor": "human", "ai_role": "只产清单与参数",
            "platform_metrics": "pending_human_measure",
            "final": "carbon_based_arbiter", "seal": SEAL}


def skill_daily_hebbian_schedule(seed: str = "0") -> dict:
    """L-18 日常赫布作息：按精力曲线生成时段表（不注册定时器、不写日历）。"""
    h = int(_sha16(f"day:{seed}")[:8], 16)
    curve = (("07:30", 0.45, "轻整理/晨读 20 分钟"),
             ("09:00", 0.90, "深度块 A：最难任务 90 分钟"),
             ("11:30", 0.55, "邮件与杂务批处理"),
             ("13:30", 0.50, "午餐后散步 15 分钟"),
             ("15:00", 0.85, "深度块 B：写作/实现 80 分钟"),
             ("18:00", 0.40, "归档与次日排布"),
             ("21:30", 0.25, "阅读与复盘，不上信息流"))
    shift = h % 3 * 5
    slots = [{"time": t, "energy": e, "task": task,
              "note": (f"±{shift} 分钟可平移" if shift else "按表执行")}
             for t, e, task in curve]
    return {"skill": "daily_hebbian_schedule", "slots": slots, "count": len(slots),
            "auto": False, "timer": False, "calendar_write": False,
            "execution": "human_manual", "simulated": True}


SKILL_FNS = (
    skill_life_ontology,
    skill_high_dim_search, skill_consumerism_blocker, skill_price_ledger,
    skill_price_review, skill_complaint_template, skill_material_card,
    skill_meridian_route, skill_context_trigger, skill_vault_manifest,
    skill_nutrition_plan, skill_travel_route, skill_shelter_check,
    skill_learning_path, skill_saas_plan,
    skill_skin_gate, skill_audit_receipt, skill_daily_hebbian_schedule,
)

SKILL_NAMES = (
    "omnilife.life_ontology",
    "omnilife.high_dim_search", "omnilife.consumerism_blocker",
    "omnilife.price_ledger", "omnilife.price_review",
    "omnilife.complaint_template", "omnilife.material_card",
    "omnilife.meridian_route", "omnilife.context_trigger", "omnilife.vault_manifest",
    "omnilife.nutrition_plan", "omnilife.travel_route", "omnilife.shelter_check",
    "omnilife.learning_path", "omnilife.saas_plan",
    "omnilife.skin_gate", "omnilife.audit_receipt", "omnilife.daily_hebbian_schedule",
)


class OmniLifePack(DomainPack):
    key = "omnilife"
    name = "全域生活扩展包"
    description = ("衣食住行教 + SaaS 工作流：用 127 亚学科编码做生活决策锚点，"
                   "皮肤层拦截诱导、经络层做本地交接、生活智能体只产清单；"
                   "0 角色不建 agent，拒绝并发探测/代理切换/DOM 注入。")
    skills: List[SkillSpec] = [
        SkillSpec(name=SKILL_NAMES[i], fn=SKILL_FNS[i],
                  description=(SKILL_FNS[i].__doc__ or "").strip().splitlines()[0],
                  tags=["omnilife", "life", "offline"],
                  permissions=0)
        for i in range(len(SKILL_FNS))
    ]
    roles: List = []                        # 0 角色 → 不新增 agent
    workflows: List[WorkflowSpec] = [
        WorkflowSpec("L1_wardrobe", [], "衣：材料/符号筛选卡 → 高维搜索词 → 诱导折叠 → 本人下单"),
        WorkflowSpec("L2_nutrition", [], "食：语境触发 → 辨证结构餐单 → 拦截高糖 → 本人订餐"),
        WorkflowSpec("L3_shelter", [], "住：空间粗算 → 通风/除湿目标 → 设备由本人手动设置"),
        WorkflowSpec("L4_mobility", [], "行：权重图 → 多目标最短路 → 避开推荐位 → 本人出行"),
        WorkflowSpec("L5_learning", [], "教：主题→编码→三段路径→检索式，本人去学术库检索"),
        WorkflowSpec("L6_saas", [], "SaaS：字段映射 → 只读导出 → 本地归档 → 人工引用"),
    ]


def pack_summary() -> Dict[str, Any]:
    """供快速核对：生活域 / 锚点 / 维度不变 / 技能 / 拒绝清单。"""
    rows = SUBD_TOTAL * SLOTS_PER + SLOTS_RESERVED
    nodes = SUBD_TOTAL * NODES_PER + NODES_COORD
    missing = [c for _, _, cs in LIFE_DOMAINS for c in cs if c not in ITEMS]
    return {
        "matrix_id": MATRIX_ID, "upstream": UPSTREAM_ID,
        "domains": len(LIFE_DOMAINS),
        "anchors": len({c for _, _, cs in LIFE_DOMAINS for c in cs}),
        "locks": {"side": LOCK_SIDE, "design": LOCK_DESIGN, "mandala": LOCK_MANDALA,
                  "hilbert": LOCK_HILBERT, "kalman": LOCK_KALMAN,
                  "rows_total": rows, "nodes_total": nodes},
        "rows_ok": rows == LOCK_SIDE,
        "nodes_ok": nodes == LOCK_MANDALA,
        "addressing_unchanged": rows == LOCK_SIDE and nodes == LOCK_MANDALA and not missing,
        "missing_anchors": missing,
        "heartbeat": {"base": HEARTBEAT_BASE, "count": HEARTBEAT_COUNT, "dim": HEARTBEAT_DIM},
        "skills": len(SKILL_FNS), "workflows": len(OmniLifePack.workflows),
        "refused_ops": len(REFUSED_OPS), "inducement_rules": len(INDUCEMENT_PATTERNS),
        "taxonomy_loaded": TAXONOMY["loaded"], "items": len(ITEMS),
        "agents_created": 0, "network": False, "dom_injection": False,
        "api_calls": 0, "execution": "human_manual",
        "seal": SEAL,
    }
