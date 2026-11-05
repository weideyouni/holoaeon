"""V31 泰坦进化模块（titan_evolver）—— 本地自进化引擎基座（判定层，零网络）。

第一性原理
==========
系统的“进化”不是爬得多快，而是先有一份诚实的能力清单：我有什么、我缺什么、
我该往哪走。本模块把 V29 magic_lamp 的 KnownSkillIndex（运行时索引）**持久化**为
能力清单，并为每条能力补上 `gap` 与 `upgrade_path`，于是“知道自己有什么”变成
“知道自己缺什么、往哪进化”。

    manifest（清单·核心资产）→ gap_scan（缺口→检索规格）→ score（确定性评分+许可裁决）
    → propose（提案·人审）→ adopt（合入编排·回写清单）

与 magic_lamp(V29) 的关系
=========================
magic_lamp 是**被动编译器**：用户许愿 → 编译方案 → 止于方案书（零网络）。
titan_evolver 是**主动进化引擎**：定时巡检 + 真联网采集 + 提案制合入 + 闭环回写。
两者共享 KnownSkillIndex 的数据结构思路，本模块把它落盘为清单并补齐缺口字段。

链上位置（D-11 强制声明）
========================
本模块**不新增环**，是四环之上的**环面调度·进化编排**：
    回流（mobius_vortex）→ 投影（klein_projection）→ 熔炼（holo_forge）→ 解剖（doc_anatomy）
    ↑___________ 进化编排（titan_evolver：清单→采集→评分→提案→合入）___________↓
合入后经 mobius 回流、回写清单，闭环成立；缺环时优雅降级为“仅出计划”。

诚实边界（不达标就降级，绝不假装）
================================
* **不做全自动合入**：机器只生成候选与提案，人一键 approve 才合入（供应链安全）。
* **不联网**：包内零网络、零 subprocess；GitHub Search / 浅克隆在 scripts 执行层。
* **不解析 YAML**：仓内零依赖，清单权威格式为 JSON；YAML 只导出、不读入。
* **不做 OCR / 不调度真实定时器**：doc_anatomy 只举手（V30 边界），调度只出规格。
* **不做 LLM 打分**：评分是确定性规则，可复算、可审计；LLM 若用，其输出必须过本层复核。

工程纪律
========
* 纯标准库（json/os/re/sys/time/hashlib），零依赖、零 GPU、零服务。
* 不 shell out，不 import requests/yaml，不碰 kernel.submit。
* 仓内导入一律相对导入；不新增扩展包（模块级，先例 V12/V25/V26/V27/V28/V29/V30）。
* 新文件不参与 ReproHash → diff0 零漂移。

证据等级：evidence_class=simulated，仿真≠证明，碳基终裁。
封口密语：潮起开门，潮落闭嘴。
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time

from .klein_projection import LICENSE_RULES
from .machine_tool import SEAL

SCHEMA_VERSION = "TITAN-EVOLVER-v1.0"

CHAIN_POSITION = {
    "ring": 0,                       # 0 = 不新增环，四环之上的环面调度
    "name": "进化编排（环面调度，不新增环）",
    "upstream": ("mobius_vortex", "klein_projection", "holo_forge",
                 "doc_anatomy", "machine_tool"),
    "note": "合入后经 mobius 回流并回写清单，形成进化闭环；缺环则降级为仅出计划",
}

AXIOMS = (
    {"id": "P01", "name": "全息", "text": "局部包含整体：一条能力的缺口即全局演进方向的一条线索"},
    {"id": "P02", "name": "万物互联", "text": "契约即接口：候选只需可判定的元数据即可入链，不必强耦合"},
)

CAPABILITIES = ("manifest", "gap_scan", "score", "propose", "adopt")

MECHANISMS = (
    {"id": "M01", "name": "心跳", "en": "heartbeat",
     "role": "定时节拍：daily 采集 / weekly 提案的调度规格（本模块只出规格不运行）"},
    {"id": "M02", "name": "细胞骨架", "en": "cytoskeleton",
     "role": "清单结构：id/status/impl/gap/upgrade_path 六字段构成能力骨"},
    {"id": "M03", "name": "皮肤", "en": "skin",
     "role": "许可证裁决与阈值门：GPL/AGPL/SSPL/BUSL 在入口被拦"},
    {"id": "M04", "name": "经络", "en": "meridian",
     "role": "缺口→检索规格的路由：每条 gap 只走自己声明的关键词"},
    {"id": "M05", "name": "赫布协作场", "en": "hebbian",
     "role": "被采纳次数累积为信任权重，重复上榜的能力优先复核"},
    {"id": "M06", "name": "语义通信基座", "en": "semantic_bus",
     "role": "提案文本即接口：人能在 3 分钟内读懂的 Markdown 契约"},
    {"id": "M07", "name": "自组织相似性", "en": "similarity",
     "role": "关键词共振打分：候选文本与能力关键词的交集成确定性分数"},
    {"id": "M08", "name": "runtime", "en": "runtime",
     "role": "巡检计划：采集/评分/提案三阶段的可复算步骤序列"},
    {"id": "M09", "name": "graph", "en": "graph",
     "role": "依赖图：dependencies 字段把候选挂到上游仓库，升级可追溯"},
    {"id": "M10", "name": "类社会组合体", "en": "society",
     "role": "分工：机器生成候选与提案，人做 approve/reject，权责不混"},
    {"id": "M11", "name": "城邦架构", "en": "citystate",
     "role": "登记簿：清单与已处理 SHA 台账构成可回溯的项目库"},
)

# 抓取范围白名单（防信息过载）：只抓三类，不爬 Trending、不泛搜
FETCH_SCOPE = (
    "manifest 中 gap 对应关键词命中仓库",
    "已依赖项目的上游仓库新版本（依赖升级）",
    "fork/star 过仓库的更新",
)

# 许可证黑名单（传染性 + 专有）+ 未知从严
LICENSE_BLACKLIST = ("GPL", "AGPL", "SSPL", "BUSL")

HARD_BLOCK = ("sspl", "busl", "busl-1.1", "proprietary")

DEFAULT_THRESHOLD = 7.0
SCORE_CEIL = 10.0

TITAN_HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_MANIFEST = os.path.join(TITAN_HOME, "reports", "capability-manifest.json")

SCHEDULE_SPEC = (
    {"job": "collect", "cron": "0 9 * * *", "note": "每日 09:00 采集（Windows 任务计划）"},
    {"job": "propose", "cron": "0 10 * * 1", "note": "每周一 10:00 出提案"},
    {"job": "review", "cron": "0 10 * * 1", "note": "提案后人工 approve/reject（最长 10min）"},
)

SEED_CAPABILITIES = (
    {"id": "swarm_intel.filter", "name": "群体智能候选筛选", "status": "implemented",
     "impl": "holoaeon/swarm_intel.py (V24, HEAD=cfddea8)",
     "gap": "五阶段流水线固定，无法动态调整角色权重",
     "upgrade_path": {"search": ["swarm intelligence dynamic role",
                                 "multi-agent weight tuning"],
                      "accept": "本地可跑，不破坏现有五阶段结构"}},
    {"id": "machine_tool.assemble", "name": "工程机床总装", "status": "implemented",
     "impl": "holoaeon/machine_tool.py (V25, HEAD=57ba280)",
     "gap": "仅装配不存数据；进化回写需手动",
     "upgrade_path": {"search": ["self-evolving agent", "auto upgrade architecture"],
                      "accept": "本模块实现"}},
    {"id": "mobius_vortex.feedback", "name": "莫比乌斯状态回流", "status": "implemented",
     "impl": "holoaeon/mobius_vortex.py (V26, HEAD=8f0afb3)",
     "gap": "五圈固定，无法扩展回流路径",
     "upgrade_path": {"search": ["feedback loop extensible", "state reflux plugin"],
                      "accept": "不破坏现有五圈结构"}},
    {"id": "klein_projection.assess", "name": "克莱因收敛投影评估", "status": "implemented",
     "impl": "holoaeon/klein_projection.py (V27, HEAD=552951d)",
     "gap": "11 机制投影打分固定，无法自定义评估维度",
     "upgrade_path": {"search": ["custom evaluation metrics", "projection scoring"],
                      "accept": "不破坏现有七段流水线"}},
    {"id": "holo_forge.chain", "name": "全息熔炉链式执行", "status": "implemented",
     "impl": "holoaeon/holo_forge.py (V28, HEAD=91d7dad)",
     "gap": "三链固定（漩涡→投影→熔炼），无法插入新环节",
     "upgrade_path": {"search": ["chain executor plugin", "pipeline extension"],
                      "accept": "不破坏现有链式契约"}},
    {"id": "magic_lamp.compile", "name": "神灯愿望编译", "status": "implemented",
     "impl": "holoaeon/magic_lamp.py (V29, HEAD=d4f25da)",
     "gap": "被动响应诉求，不主动巡检；GitHub 搜索只出 spec 不执行",
     "upgrade_path": {"search": ["proactive agent", "scheduled self-evolution"],
                      "accept": "本模块(titan_evolver)实现"}},
    {"id": "doc_anatomy.parse", "name": "文档解剖器 PDF 解析", "status": "implemented",
     "impl": "holoaeon/doc_anatomy.py (V30, HEAD=3340bc1)",
     "gap": "纯标准库解析，/Encrypt 与 CID/Identity-H 不支持；无文本层只举手不接 OCR",
     "upgrade_path": {"search": ["PDF encrypted parse", "CID font decoding",
                                 "OCR fallback"],
                      "accept": "本地可跑，不破坏现有四能力结构"}},
    {"id": "ocr.document", "name": "文档 OCR 识别", "status": "implemented",
     "impl": "mineru@4.0.12（GPU 加速，standard 层级模型 + VLM）",
     "gap": "表格结构还原偶有错位；扫描件倾斜校正弱",
     "upgrade_path": {"search": ["table recognition", "layout analysis", "OCR"],
                      "accept": "能输出 Markdown 表格且本地可跑"},
     "dependencies": ["mineru"]},
    {"id": "ocr.fallback_cpu", "name": "CPU 级 OCR 备选", "status": "candidate",
     "impl": None,
     "gap": "GPU 不可用时无降级方案",
     "upgrade_path": {"search": ["PaddleOCR", "RapidOCR", "CPU OCR chinese"],
                      "accept": "中文准确率≥90%，单图<2s，CPU 可跑"}},
    {"id": "scheduler.task", "name": "定时任务调度", "status": "candidate",
     "impl": None,
     "gap": "未实现；依赖本模块首次构建",
     "upgrade_path": {"search": ["APScheduler retry", "task scheduler backoff"],
                      "accept": "支持指数退避重试 + 失败告警"}},
    {"id": "collector.github_search", "name": "GitHub 定向检索", "status": "candidate",
     "impl": None,
     "gap": "未实现；magic_lamp W6 只出 spec 不执行，本模块补齐真联网",
     "upgrade_path": {"search": ["GitHub Search API python", "repo shallow clone"],
                      "accept": "支持 Token 限流 + SHA 去重 + 浅克隆"},
     "dependencies": ["github_token"]},
    {"id": "kb.vector_search", "name": "向量海检索", "status": "implemented",
     "impl": "sqlite-vec@0.1.9（10363 片段，440 体系，字符 3-gram 哈希 256 维）",
     "gap": "非神经嵌入，语义相似度弱；增量重建需攒批",
     "upgrade_path": {"search": ["sqlite-vec neural embedding", "BGE embedding"],
                      "accept": "本地可跑，语义准确率提升且不破坏现有索引"}},
)

STATUS_VALUES = ("implemented", "candidate", "deprecated")


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def _digest(text):
    return hashlib.sha256(str(text).encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# T1 CapabilityManifest —— 能力清单（核心资产，持久化）
# ---------------------------------------------------------------------------
class CapabilityManifest:
    """清单权威格式为 JSON（仓内零依赖）；YAML 只导出不读入。"""

    def __init__(self, path=None, data=None):
        self.path = path or DEFAULT_MANIFEST
        self.data = data if isinstance(data, dict) else None

    @classmethod
    def seed(cls, path=None):
        return cls(path, {
            "manifest_version": "0.1.0",
            "owner": "潘荟丞",
            "last_updated": time.strftime("%Y-%m-%d"),
            "capabilities": [dict(c) for c in SEED_CAPABILITIES],
            "fetch_scope": list(FETCH_SCOPE),
            "license_blacklist": list(LICENSE_BLACKLIST),
            "schedule": [dict(s) for s in SCHEDULE_SPEC],
        })

    @classmethod
    def load(cls, path=None):
        path = path or DEFAULT_MANIFEST
        try:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, ValueError):
            return cls(path, None)
        if not isinstance(data, dict) or not isinstance(data.get("capabilities"), list):
            return cls(path, None)
        return cls(path, data)

    def ready(self):
        return self.data is not None

    def save(self):
        if self.data is None:
            return {"ok": False, "reason": "清单未初始化"}
        parent = os.path.dirname(os.path.abspath(self.path))
        if parent and not os.path.isdir(parent):
            os.makedirs(parent, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump(self.data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        return {"ok": True, "path": self.path, "capabilities": len(self.items())}

    def items(self):
        return list((self.data or {}).get("capabilities") or [])

    def gaps(self):
        """有缺口的能力 = 可选进化点（实现且无 gap 的跳过）。"""
        out = []
        for cap in self.items():
            if not cap.get("gap"):
                continue
            out.append(cap)
        return out

    def find(self, capability_id):
        for cap in self.items():
            if cap.get("id") == capability_id:
                return cap
        return None

    def writeback(self, capability_id, status=None, impl=None, gap=None, note=None):
        """合入后回写：status / impl / gap 更新，附带 last_updated。"""
        cap = self.find(capability_id)
        if cap is None:
            return {"ok": False, "reason": "未知能力：%s" % capability_id}
        if status is not None:
            if status not in STATUS_VALUES:
                return {"ok": False, "reason": "status 取值不合法：%s" % status}
            cap["status"] = status
        if impl is not None:
            cap["impl"] = impl
        if gap is not None:
            cap["gap"] = gap
        if note:
            cap["last_writeback"] = {"note": note, "at": _now()}
        if self.data is not None:
            self.data["last_updated"] = time.strftime("%Y-%m-%d")
        return {"ok": True, "capability": cap["id"], "status": cap.get("status")}

    def summary(self):
        items = self.items()
        by_status = {}
        for cap in items:
            key = cap.get("status") or "unknown"
            by_status[key] = by_status.get(key, 0) + 1
        return {"total": len(items), "by_status": by_status,
                "with_gap": len(self.gaps()),
                "digest": _digest(json.dumps(items, ensure_ascii=False, sort_keys=True))}


def export_yaml(manifest):
    """把清单渲染为 YAML 文本（只导出，不解析；仓内不引 PyYAML）。"""
    data = manifest.data or {}
    lines = ["# capability-manifest.yaml —— 泰坦进化模块能力清单（由 titan_evolver 导出）",
             "# 权威格式为 reports/capability-manifest.json；本文件仅供阅读/交接，包内不解析",
             'manifest_version: "%s"' % data.get("manifest_version", "0.1.0"),
             'owner: "%s"' % data.get("owner", ""),
             'last_updated: "%s"' % data.get("last_updated", ""),
             "", "capabilities:"]
    for cap in data.get("capabilities") or []:
        lines.append("  - id: %s" % cap.get("id"))
        lines.append("    name: %s" % cap.get("name"))
        lines.append("    status: %s" % cap.get("status"))
        lines.append('    impl: "%s"' % (cap.get("impl") or "null"))
        lines.append('    gap: "%s"' % (cap.get("gap") or ""))
        up = cap.get("upgrade_path") or {}
        lines.append("    upgrade_path:")
        lines.append("      search: [%s]" % ", ".join(
            '"%s"' % kw for kw in (up.get("search") or [])))
        lines.append('      accept: "%s"' % (up.get("accept") or ""))
        deps = cap.get("dependencies")
        if deps:
            lines.append("    dependencies: [%s]" % ", ".join('"%s"' % d for d in deps))
    lines.append("")
    lines.append("fetch_scope:")
    for item in data.get("fetch_scope") or []:
        lines.append('  - "%s"' % item)
    lines.append("")
    lines.append("license_blacklist:")
    for item in data.get("license_blacklist") or []:
        lines.append("  - %s" % item)
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# T2 GapScanner —— 缺口 → 检索规格（复用 magic_lamp GapDetector 思路）
# ---------------------------------------------------------------------------
def gap_queries(manifest, limit=None):
    """每条 gap 只走自己声明的关键词；返回可交给执行层的 query spec。"""
    specs = []
    for cap in manifest.gaps():
        up = cap.get("upgrade_path") or {}
        keywords = [kw for kw in (up.get("search") or []) if kw]
        if not keywords:
            continue
        specs.append({
            "capability": cap.get("id"),
            "keywords": keywords,
            "accept": up.get("accept") or "",
            "executed_by": "scripts/titan_evolver_run.py（执行层·联网侧，包内零网络）",
        })
    if limit is not None:
        specs = specs[:int(limit)]
    return specs


# ---------------------------------------------------------------------------
# T3 CandidateScorer —— 确定性评分 + 许可证裁决
# ---------------------------------------------------------------------------
def license_verdict(spdx):
    """四级裁决：hard_block / strong_copyleft / weak_copyleft / permissive。

    黑名单在入口优先拦截（SSPL/BUSL/专有 → reject），再走 V27 的三级规则。
    """
    norm = (spdx or "unknown").strip().lower()
    if (norm in HARD_BLOCK or norm.startswith("sspl") or norm.startswith("busl")
            or norm.startswith("proprietary")):
        return {"spdx": norm, "class": "hard_block", "mode": "reject", "allow": False}
    for rule in LICENSE_RULES:
        if re.match(rule["pattern"], norm):
            return {"spdx": norm, "class": rule["class"], "mode": rule["mode"],
                    "allow": rule["class"] != "strong_copyleft"}
    return {"spdx": norm, "class": "unknown", "mode": "review_only", "allow": False}


def score(candidate, capability=None):
    """确定性打分（0–10，两位小数）；同一输入必得同一分。"""
    if not isinstance(candidate, dict):
        return {"ok": False, "reason": "候选必须是对象"}

    stars = candidate.get("stars") or 0
    try:
        stars = int(stars)
    except (TypeError, ValueError):
        stars = 0
    if stars >= 1000:
        pts = 3.0
    elif stars >= 300:
        pts = 2.0
    elif stars >= 100:
        pts = 1.5
    elif stars >= 10:
        pts = 0.8
    else:
        pts = 0.3

    cap = capability or {}
    keywords = [kw for kw in ((cap.get("upgrade_path") or {}).get("search") or []) if kw]
    blob = " ".join([
        str(candidate.get("name") or ""),
        str(candidate.get("title") or ""),
        str(candidate.get("description") or ""),
        " ".join(str(t) for t in (candidate.get("topics") or [])),
    ]).lower()
    hits = [kw for kw in keywords if str(kw).lower() in blob]
    hit_pts = min(len(hits) * 0.6, 3.0)

    lic = license_verdict(candidate.get("license"))
    lic_pts = {"permissive": 2.0, "weak_copyleft": 1.0,
               "strong_copyleft": -2.0, "hard_block": -3.0}.get(lic["class"], 0.0)

    readme_pts = 1.0 if candidate.get("readme") else 0.0
    tests_pts = 0.5 if candidate.get("tests") else 0.0
    entry_pts = 0.5 if candidate.get("entry") else 0.0
    archived_pts = -1.0 if candidate.get("archived") else 0.0

    total = pts + hit_pts + lic_pts + readme_pts + tests_pts + entry_pts + archived_pts
    total = max(0.0, min(SCORE_CEIL, total))
    return {"ok": True, "score": round(total, 2),
            "components": {"stars": pts, "keywords": round(hit_pts, 2),
                           "license": lic_pts, "readme": readme_pts,
                           "tests": tests_pts, "entry": entry_pts,
                           "archived": archived_pts},
            "keyword_hits": hits, "license": lic,
            "eligible": bool(lic["allow"])}


def rank(candidates, manifest, threshold=DEFAULT_THRESHOLD):
    """按能力分组评分，过滤阈值与许可证，输出 selected / rejected。"""
    selected, rejected = [], []
    for cand in candidates or []:
        if not isinstance(cand, dict):
            continue
        cap = manifest.find(cand.get("capability")) if manifest.ready() else None
        result = score(cand, cap)
        if not result["ok"]:
            continue
        row = {"repo": cand.get("repo"), "capability": cand.get("capability"),
               "score": result["score"], "license": result["license"]["spdx"],
               "verdict": result["license"]["mode"], "hits": result["keyword_hits"]}
        if result["score"] >= threshold and result["license"]["allow"]:
            selected.append(row)
        else:
            row["reason"] = ("许可证不允许（%s）" % result["license"]["class"]
                             if not result["license"]["allow"] else "分数低于阈值")
            rejected.append(row)
    selected.sort(key=lambda r: (-r["score"], r["repo"] or ""))
    return {"selected": selected, "rejected": rejected}


# ---------------------------------------------------------------------------
# T4 ProposalWriter —— UPGRADE_PROPOSAL（人 3 分钟能读懂）
# ---------------------------------------------------------------------------
def propose(candidates, manifest, threshold=DEFAULT_THRESHOLD, date=None):
    ranked = rank(candidates, manifest, threshold)
    if not ranked["selected"]:
        return {"ok": False, "reason": "无候选通过阈值/许可证裁决",
                "rejected": ranked["rejected"], "markdown": ""}
    date = date or time.strftime("%Y-%m-%d")
    lines = ["# UPGRADE_PROPOSAL · %s" % date, "",
             "> 提案制：机器只生成候选，**人决定合入**。approve 前请核对许可证、体积、可回滚。",
             "> 证据等级 evidence_class=simulated；仿真≠证明，碳基终裁。", "",
             "## 一、候选总览", "",
             "| # | 能力 | 仓库 | 分数 | 许可 | 裁决 | 关键词命中 |",
             "|---|------|------|------|------|------|------------|"]
    for idx, row in enumerate(ranked["selected"], 1):
        lines.append("| %d | %s | %s | %.2f | %s | %s | %s |" % (
            idx, row["capability"], row["repo"], row["score"],
            row["license"], row["verdict"],
            ", ".join(row["hits"]) or "—"))
    lines += ["", "## 二、逐条建议", ""]
    for row in ranked["selected"]:
        cap = manifest.find(row["capability"]) or {}
        lines.append("### %s ← %s" % (row["capability"], row["repo"]))
        lines.append("- 当前缺口：%s" % (cap.get("gap") or "（清单未记录）"))
        lines.append("- 采纳判据：%s" % ((cap.get("upgrade_path") or {}).get("accept") or "—"))
        lines.append("- 机器评分：%.2f / %.1f（许可证 %s）" % (row["score"], SCORE_CEIL,
                                                          row["license"]))
        lines.append("- 合入前必须：沙箱冒烟 + 红线扫描 + 可一键回滚")
        lines.append("")
    lines += ["## 三、被拒候选（供优化关键词）", ""]
    if ranked["rejected"]:
        for row in ranked["rejected"][:10]:
            lines.append("- %s（%s）：%s" % (row["repo"], row["capability"],
                                           row.get("reason") or "—"))
    else:
        lines.append("- （无）")
    lines += ["", "## 四、审批", "", "```",
              "approve: python scripts/titan_evolver_run.py --approve --proposal=%s" % date,
              "reject : 在本文件下方写原因（用于优化关键词与阈值）",
              "```", "",
              "封口密语：潮起开门，潮落闭嘴。"]
    return {"ok": True, "markdown": "\n".join(lines) + "\n",
            "selected": ranked["selected"], "rejected": ranked["rejected"],
            "digest": _digest("\n".join(lines))}


# ---------------------------------------------------------------------------
# T5 AdoptionPlanner —— approve 后的合入编排（缺环优雅降级）
# ---------------------------------------------------------------------------
ADOPTION_STEPS = (
    {"step": "human_approve", "module": None, "gate": True,
     "detail": "人一键 approve（机器不自动合入）"},
    {"step": "sandbox_smoke", "module": None, "gate": True,
     "detail": "沙箱冒烟 + 红线扫描 + 体积检查（候选代码在 evolver/candidates/）"},
    {"step": "klein_assess", "module": "klein_projection",
     "detail": "KleinProjection().assess(候选档案.json)：11 机制投影 + 许可证裁决 + 收敛判定"},
    {"step": "forge_chain", "module": "holo_forge",
     "detail": "HoloForge.run_chain(envelope)：漩涡→投影→熔炼三链"},
    {"step": "machine_assemble", "module": "machine_tool",
     "detail": "MachineTool 装配（判定层/执行层分层，scripts 触网）"},
    {"step": "mobius_reflect", "module": "mobius_vortex",
     "detail": "MobiusVortex.emit(batch, gates, five_site, lessons)：回流灯塔"},
    {"step": "manifest_writeback", "module": None, "gate": True,
     "detail": "CapabilityManifest.writeback：status/impl/gap 更新，闭环成立"},
)


def _probe_modules():
    available = {}
    try:
        from . import klein_projection  # noqa: F401
        available["klein_projection"] = True
    except Exception:
        available["klein_projection"] = False
    try:
        from . import holo_forge  # noqa: F401
        available["holo_forge"] = True
    except Exception:
        available["holo_forge"] = False
    try:
        from . import machine_tool  # noqa: F401
        available["machine_tool"] = True
    except Exception:
        available["machine_tool"] = False
    try:
        from . import mobius_vortex  # noqa: F401
        available["mobius_vortex"] = True
    except Exception:
        available["mobius_vortex"] = False
    return available


def adoption_plan(capability_id, modules=None):
    """approve 之后的合入编排；缺环标记 available=False 但仍给出降级路径。"""
    modules = modules if modules is not None else _probe_modules()
    steps = []
    blocked = []
    for spec in ADOPTION_STEPS:
        item = dict(spec)
        mod = item.get("module")
        if mod:
            item["available"] = bool(modules.get(mod))
            if not item["available"]:
                blocked.append(mod)
        else:
            item["available"] = True
        steps.append(item)
    return {"ok": True, "capability": capability_id, "steps": steps,
            "degraded": bool(blocked), "blocked_modules": blocked,
            "note": "缺环不静默：仍可 approve 但只能走到可用步，下游需人工补",
            "seal": SEAL}


# ---------------------------------------------------------------------------
# T6 去重与调度规格
# ---------------------------------------------------------------------------
def dedup_key(repo, sha):
    return "%s@%s" % (repo, sha)


def is_duplicate(seen, repo, sha):
    return dedup_key(repo, sha) in set(seen or [])


def schedule_spec():
    return [dict(s) for s in SCHEDULE_SPEC]


def mechanisms():
    return [dict(m) for m in MECHANISMS]


def inspect(manifest=None):
    manifest = manifest or CapabilityManifest.load()
    summary = manifest.summary() if manifest.ready() else {"total": 0}
    return {
        "module": "titan_evolver",
        "version": "V31",
        "schema": SCHEMA_VERSION,
        "seal": SEAL,
        "chain_position": dict(CHAIN_POSITION),
        "capabilities": list(CAPABILITIES),
        "mechanisms": len(MECHANISMS),
        "manifest_path": manifest.path,
        "manifest_ready": manifest.ready(),
        "manifest": summary,
        "gaps": [c.get("id") for c in manifest.gaps()] if manifest.ready() else [],
        "threshold": DEFAULT_THRESHOLD,
        "license_blacklist": list(LICENSE_BLACKLIST),
        "fetch_scope": list(FETCH_SCOPE),
        "schedule": schedule_spec(),
        "collected_at": _now(),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "inspect"
    rest = argv[1:]

    if cmd == "axioms":
        for axiom in AXIOMS:
            print("%s %s — %s" % (axiom["id"], axiom["name"], axiom["text"]))
        return 0

    if cmd == "chain":
        print("ring %d · %s ← %s" % (CHAIN_POSITION["ring"], CHAIN_POSITION["name"],
                                     " → ".join(CHAIN_POSITION["upstream"])))
        print(CHAIN_POSITION["note"])
        return 0

    if cmd == "mechanisms":
        for item in MECHANISMS:
            print("%s %s — %s" % (item["id"], item["name"], item["role"]))
        return 0

    if cmd == "manifest":
        path = rest[0] if rest else DEFAULT_MANIFEST
        if "--init" in rest or not os.path.isfile(path):
            manifest = CapabilityManifest.seed(path)
            print(json.dumps(manifest.save(), ensure_ascii=False))
        else:
            manifest = CapabilityManifest.load(path)
            print(json.dumps(manifest.summary(), ensure_ascii=False))
        return 0

    if cmd == "export-yaml":
        path = rest[0] if rest else DEFAULT_MANIFEST
        manifest = CapabilityManifest.load(path)
        if not manifest.ready():
            print("清单未初始化：先跑 manifest --init", file=sys.stderr)
            return 2
        sys.stdout.write(export_yaml(manifest))
        return 0

    if cmd == "gaps":
        manifest = CapabilityManifest.load(rest[0] if rest else DEFAULT_MANIFEST)
        if not manifest.ready():
            print("清单未初始化：先跑 manifest --init", file=sys.stderr)
            return 2
        for spec in gap_queries(manifest):
            print(json.dumps(spec, ensure_ascii=False))
        return 0

    if cmd == "license":
        if not rest:
            print("需要 SPDX 名，例如 MIT / AGPL-3.0 / SSPL", file=sys.stderr)
            return 2
        print(json.dumps(license_verdict(rest[0]), ensure_ascii=False))
        return 0

    if cmd == "score":
        if not rest:
            print("需要候选 JSON 文件", file=sys.stderr)
            return 2
        with open(rest[0], "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        cand = payload.get("candidate") if isinstance(payload, dict) and "candidate" in payload else payload
        print(json.dumps(score(cand), ensure_ascii=False, indent=1))
        return 0

    if cmd == "proposal":
        if not rest:
            print("需要候选 JSON 文件", file=sys.stderr)
            return 2
        with open(rest[0], "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        candidates = payload.get("candidates") if isinstance(payload, dict) else payload
        manifest = CapabilityManifest.load(
            payload.get("manifest") if isinstance(payload, dict) else None)
        result = propose(candidates, manifest,
                         threshold=(payload.get("threshold")
                                    if isinstance(payload, dict) and payload.get("threshold")
                                    else DEFAULT_THRESHOLD))
        if not result["ok"]:
            print(json.dumps({"ok": False, "reason": result["reason"],
                              "rejected": result["rejected"]}, ensure_ascii=False, indent=1))
            return 1
        sys.stdout.write(result["markdown"])
        return 0

    if cmd == "plan":
        cap_id = rest[0] if rest else "doc_anatomy.parse"
        print(json.dumps(adoption_plan(cap_id), ensure_ascii=False, indent=1))
        return 0

    if cmd == "inspect":
        path = rest[0] if rest else DEFAULT_MANIFEST
        manifest = CapabilityManifest.load(path)
        print(json.dumps(inspect(manifest), ensure_ascii=False, indent=1))
        return 0

    print("usage: python -m holoaeon.titan_evolver "
          "axioms|chain|mechanisms|manifest [--init]|export-yaml|gaps|license <spdx>|"
          "score <json>|proposal <json>|plan <capability>|inspect", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
