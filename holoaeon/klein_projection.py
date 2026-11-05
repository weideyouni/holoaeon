"""V27 克莱因收敛投影模块（klein_projection）—— 全息投影吸纳。

第一性原理
==========
全息 = 局部包含整体。HoloAeon 的 11 项自组织机制构成一张全息图，可以**投影**到任意
开源候选：用同一张机制清单去读候选，读得通=可吸纳，读不通=放弃。
克莱因瓶 = 无向闭合曲面：瓶颈穿过瓶壁而不穿透 —— 候选被吸纳、本体不被侵入
（许可证"只蒸馏创意不复制代码"的几何表达）。
收敛判据 = 两轮投影分差为 0（不动点）：成像不再变化，吸纳完成。

七段流水线（每段独立可测）
=========================
1. CandidateIntake   受理候选：repo 元数据档案 + 必填校验
2. HoloEvaluator     11 机制投影打分 + 许可证裁决（四级）
3. QuartetGate       四人组五步协议 + 涌现条件确定性校验
4. TensorCoupler     D/X 扬弃 → 张量轴 + 两轮收敛判定（分差=0）
5. EphemeralForge    一过性代码：tempfile 车削，ast 校验，用后即焚（不入库不入 git）
6. Hardener          硬核代码化：测试全绿才转正，产出 manifest 条目
7. ProjectLibrary    本地项目库 JSON 索引（仓外），反复使用
   ChatFrontendPack  贯穿段：张量耦合物渲染为对话窗口提示包（任意大模型平台即前端）

工程纪律
========
* 纯标准库（json/os/ast/tempfile/re/sys/time/hashlib），零网络、零密钥、零 GPU。
* 不 shell out（redline 禁 subprocess），一过性代码只做 ast.parse 语法校验，不执行。
* 仓内导入一律相对导入；不碰 graph/scheduler/hypervector/kernel.submit。
* 不新增扩展包（模块级，先例 butler_os V12 / machine_tool V25 / mobius_vortex V26）。
* 新文件不参与 ReproHash → diff0 零漂移。

证据等级：evidence_class=simulated，仿真≠证明，碳基终裁。
封口密语：潮起开门，潮落闭嘴。
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import sys
import tempfile
import time

from .machine_tool import SEAL

SCHEMA_VERSION = "KLEIN-PROJECTION-v1.0"

# 11 项全息机制（关键词表刻意不含机制中文名本身，避免"自命中"破坏收敛判据）
MECHANISMS = (
    {"id": "M01", "name": "心跳", "en": "heartbeat",
     "keywords": ("heartbeat", "tick", "pulse", "interval", "周期")},
    {"id": "M02", "name": "细胞骨架", "en": "cytoskeleton",
     "keywords": ("agent", "scaffold", "assemble", "builder", "persona")},
    {"id": "M03", "name": "皮肤", "en": "skin",
     "keywords": ("guard", "filter", "validate", "sanitize", "schema", "guardrail")},
    {"id": "M04", "name": "经络", "en": "meridian",
     "keywords": ("route", "channel", "dispatch", "bus", "pipeline")},
    {"id": "M05", "name": "赫布协作场", "en": "hebbian",
     "keywords": ("weight", "reinforce", "coactivate", "hebb", "trust")},
    {"id": "M06", "name": "语义通信基座", "en": "semantic_bus",
     "keywords": ("envelope", "message", "protocol", "codec", "json")},
    {"id": "M07", "name": "自组织相似性", "en": "similarity",
     "keywords": ("cluster", "resonance", "similarity", "embedding", "vector")},
    {"id": "M08", "name": "runtime", "en": "runtime",
     "keywords": ("runtime", "loop", "scheduler", "orchestrat", "worker")},
    {"id": "M09", "name": "graph", "en": "graph",
     "keywords": ("graph", "node", "edge", "adjacency", "rag", "entity")},
    {"id": "M10", "name": "类社会组合体", "en": "society",
     "keywords": ("role", "division", "emergent", "society", "cooperation")},
    {"id": "M11", "name": "城邦架构", "en": "citystate",
     "keywords": ("registry", "ledger", "registry_book", "archive", "index")},
)

# 许可证四级裁决：传染性许可证只蒸馏创意，不复制代码（V24 MiroFish 判例）
LICENSE_RULES = (
    {"pattern": r"^(mit|bsd-2-clause|bsd-3-clause|apache-2\.0|isc|0bsd)$",
     "class": "permissive", "mode": "absorb"},
    {"pattern": r"^(mpl-2\.0|lgpl-2\.1|lgpl-3\.0|epl-2\.0)$",
     "class": "weak_copyleft", "mode": "absorb_with_notice"},
    {"pattern": r"^(gpl-2\.0|gpl-3\.0|agpl-3\.0|sspl|cc-by-sa-4\.0)$",
     "class": "strong_copyleft", "mode": "distill_only"},
)

CANDIDATE_REQUIRED = ("name", "license", "language", "keywords")

# 4 条硬纪律（转正前置）
PROMOTE_GATES = ("tests_green", "no_forbidden_import", "ast_parse_ok", "manifest_written")

DEFAULT_LIBRARY = r"F:\doubaowork\holoaeon_lathe\project_library.json"
MAX_ROUNDS = 4
CONVERGE_EPS = 0.0

ATLAS_ENTRIES = (
    {"segment": "TensorCoupler", "part": "收敛判定", "target": "klein_convergence",
     "source": "quartet_toolkit", "meaning": "克莱因收敛原语归位：两轮投影不动点=吸纳完成"},
    {"segment": "HoloEvaluator", "part": "全息评估", "target": "concept_anatomy",
     "source": "V19 概念解剖器", "meaning": "概念解剖先例：把候选拆到创意骨骼"},
    {"segment": "HoloEvaluator", "part": "许可证裁决", "target": "swarm_intel 蒸馏纪律",
     "source": "V24 先例", "meaning": "AGPL 只取创意不复制代码（思想-表达二分法）"},
    {"segment": "EphemeralForge", "part": "一过性车削", "target": "skill_lathe",
     "source": "V14 技能机床", "meaning": "车削隐喻本义：毛坯一过性试切，成品才入库"},
    {"segment": "ChatFrontendPack", "part": "对话窗口前端", "target": "protocol_plugins",
     "source": "V14 协议适配", "meaning": "12 种协议适配=任意大模型平台即前端"},
    {"segment": "KleinProjection", "part": "低硬件躯体", "target": "butler_os",
     "source": "V12 管家 OS", "meaning": "零依赖躯体先例：无 GPU 无服务纯标准库"},
    {"segment": "TensorCoupler", "part": "张量耦合", "target": "quartet_tensor",
     "source": "quartet_toolkit", "meaning": "D/X 扬弃 → 张量轴耦合物"},
    {"segment": "HoloEvaluator", "part": "投影扇出", "target": "mandala_fanout",
     "source": "quartet_toolkit", "meaning": "一张全息图扇出到任意候选"},
    {"segment": "KleinProjection", "part": "评估回传", "target": "mobius_vortex",
     "source": "V26", "meaning": "评估档案经灯塔回流，四人组掌握"},
    {"segment": "ProjectLibrary", "part": "账面查询", "target": "memory_of_yuan",
     "source": "V17 专用记忆", "meaning": "工程维度历史唯一来源"},
)


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def _sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _write_json(path, data):
    parent = os.path.dirname(os.path.abspath(path))
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


# ---------------------------------------------------------------------------
# 第一段：CandidateIntake —— 受理候选
# ---------------------------------------------------------------------------
class CandidateIntake:
    def parse(self, data):
        if not isinstance(data, dict):
            return {"ok": False, "problems": ["候选档案必须是 JSON 对象"]}
        problems = []
        for key in CANDIDATE_REQUIRED:
            if not data.get(key):
                problems.append("缺必填字段：%s" % key)
        kws = data.get("keywords")
        if kws is not None and not isinstance(kws, (list, tuple)):
            problems.append("keywords 必须是数组")
        if problems:
            return {"ok": False, "problems": problems}
        profile = {
            "name": str(data["name"]),
            "license": str(data["license"]).strip().lower(),
            "language": str(data["language"]),
            "keywords": [str(k).strip().lower() for k in data["keywords"] if str(k).strip()],
            "description": str(data.get("description") or ""),
            "url": str(data.get("url") or ""),
            "stars": data.get("stars"),
        }
        if not profile["keywords"] and not profile["description"]:
            return {"ok": False, "problems": ["keywords 与 description 不能同时为空"]}
        return {"ok": True, "profile": profile, "problems": []}

    def load(self, path):
        data = _read_json(path)
        if data is None:
            return {"ok": False, "problems": ["候选档案不可读：%s" % path]}
        return self.parse(data)


# ---------------------------------------------------------------------------
# 第二段：HoloEvaluator —— 11 机制投影 + 许可证裁决
# ---------------------------------------------------------------------------
class HoloEvaluator:
    def __init__(self, mechanisms=None):
        self.mechanisms = list(mechanisms or MECHANISMS)

    def license_ruling(self, license_id):
        license_id = str(license_id or "").strip().lower()
        for rule in LICENSE_RULES:
            if re.match(rule["pattern"], license_id):
                return {"license": license_id, "class": rule["class"], "mode": rule["mode"],
                        "copy_code": rule["class"] == "permissive"}
        return {"license": license_id, "class": "unknown", "mode": "distill_only",
                "copy_code": False}

    @staticmethod
    def _text(profile):
        kws = " ".join(profile.get("keywords") or [])
        desc = profile.get("description") or ""
        return (kws + " " + desc + " " + (profile.get("language") or "")).lower()

    def project(self, profile):
        text = self._text(profile)
        scores = []
        for mech in self.mechanisms:
            hits = [kw for kw in mech["keywords"] if kw in text]
            score = min(1.0, round(len(hits) / 2.0, 3))
            scores.append({
                "id": mech["id"], "name": mech["name"], "en": mech["en"],
                "score": score, "hits": hits,
            })
        matched = [s for s in scores if s["score"] > 0]
        coverage = round(len(matched) / float(len(self.mechanisms)), 3)
        return {"scores": scores, "matched": len(matched), "coverage": coverage}

    def evaluate(self, profile):
        projection = self.project(profile)
        ruling = self.license_ruling(profile.get("license"))
        coverage = projection["coverage"]
        if ruling["class"] == "unknown":
            verdict = "reject"
            reason = "许可证不可判定：只做人工审读"
        elif coverage >= 0.5:
            verdict = "integrate"
            reason = "机制覆盖 %.0f%%：可吸纳" % (coverage * 100)
        elif coverage >= 0.3:
            verdict = "blend"
            reason = "机制覆盖 %.0f%%：部分吸纳（仅取命中机制）" % (coverage * 100)
        else:
            verdict = "reject"
            reason = "机制覆盖 %.0f%%：与全息图不兼容" % (coverage * 100)
        return {
            "candidate": profile.get("name"),
            "license_ruling": ruling,
            "projection": projection,
            "coverage": coverage,
            "verdict": verdict,
            "reason": reason,
            "evaluated_at": _now(),
        }


# ---------------------------------------------------------------------------
# 第三段：QuartetGate —— 四人组五步协议 + 涌现条件
# ---------------------------------------------------------------------------
class QuartetGate:
    STEPS = ("道", "法", "术", "器", "升维")

    @staticmethod
    def emergence(order_inputs):
        p1 = float(order_inputs.get("p1") or 0.0)
        p2 = float(order_inputs.get("p2") or 0.0)
        p3 = float(order_inputs.get("p3") or 0.0)
        p4 = float(order_inputs.get("p4") or 0.0)
        coverage = float(order_inputs.get("coverage") or 0.0)
        order = round(0.30 * (p2 * p3) + 0.25 * p1 + 0.20 * (1.0 - p4) + 0.25 * coverage, 4)
        ok = (p2 * p3) >= 0.7 and p1 >= 0.6 and p4 <= 0.4 and order > 0.30
        return {"order": order, "conditions_met": bool(ok)}

    def gate(self, evaluation, order_inputs=None):
        coverage = evaluation.get("coverage") or 0.0
        inputs = dict(order_inputs or {})
        inputs.setdefault("p1", 0.7 if coverage >= 0.5 else 0.5)
        inputs.setdefault("p2", 0.8)
        inputs.setdefault("p3", 0.9)
        inputs.setdefault("p4", 0.3)
        inputs.setdefault("coverage", coverage)
        em = self.emergence(inputs)
        ruling = evaluation.get("license_ruling") or {}
        if evaluation.get("verdict") == "reject":
            verdict = "BLOCK"
        elif ruling.get("mode") == "distill_only" or not em["conditions_met"]:
            verdict = "ATTENTION"
        else:
            verdict = "PASS"
        return {
            "protocol": list(self.STEPS),
            "inputs": inputs,
            "emergence": em,
            "verdict": verdict,
            "note": "distill_only=只蒸馏创意不复制代码；涌现未达条件 → 转人工复核",
        }


# ---------------------------------------------------------------------------
# 第四段：TensorCoupler —— D/X 张量轴 + 克莱因收敛
# ---------------------------------------------------------------------------
class TensorCoupler:
    def couple(self, evaluation, adopted=None, rejected=None):
        matched = (evaluation.get("projection") or {}).get("scores") or []
        auto_d = [s for s in matched if s.get("score", 0) > 0]
        auto_x = [s for s in matched if s.get("score", 0) == 0]
        d_axis = list(adopted) if adopted is not None else [s["id"] for s in auto_d]
        x_axis = list(rejected) if rejected is not None else [s["id"] for s in auto_x]
        shape = [len(d_axis), len(x_axis)]
        return {
            "d_axis": d_axis,
            "x_axis": x_axis,
            "tensor_shape": shape,
            "rank": min(shape) if shape else 0,
            "license_mode": (evaluation.get("license_ruling") or {}).get("mode"),
            "note": "D=取（可吸纳机制）/ X=弃（不兼容或传染性许可证代码）",
        }

    def converge(self, profile, evaluator=None, max_rounds=MAX_ROUNDS):
        ev = evaluator or HoloEvaluator()
        rounds = []
        extra_kw = []
        for i in range(1, max_rounds + 1):
            probe = dict(profile)
            probe["keywords"] = list(profile.get("keywords") or []) + list(extra_kw)
            vec = ev.project(probe)
            rounds.append({"round": i, "coverage": vec["coverage"],
                           "vector": [s["score"] for s in vec["scores"]],
                           "added_keywords": list(extra_kw)})
            if i >= 2:
                prev, cur = rounds[-2]["vector"], rounds[-1]["vector"]
                delta = max(abs(a - b) for a, b in zip(prev, cur))
                if delta <= CONVERGE_EPS:
                    return {"rounds": rounds, "rounds_used": i,
                            "delta_max": round(delta, 6), "fixed_point": True,
                            "verdict": "CONVERGED"}
            matched = [s["name"] for s in ev.project(probe)["scores"] if s["score"] > 0]
            new_kw = [n for n in matched if n not in extra_kw]
            if not new_kw:
                if i >= 2:
                    break
                new_kw = []
            extra_kw = extra_kw + new_kw
            if not extra_kw and i >= 2:
                break
        delta = 0.0
        if len(rounds) >= 2:
            delta = max(abs(a - b) for a, b in
                        zip(rounds[-2]["vector"], rounds[-1]["vector"]))
        return {"rounds": rounds, "rounds_used": len(rounds),
                "delta_max": round(delta, 6), "fixed_point": delta <= CONVERGE_EPS,
                "verdict": "CONVERGED" if delta <= CONVERGE_EPS else "NOT_CONVERGED"}


# ---------------------------------------------------------------------------
# 第五段：EphemeralForge —— 动态一过性代码（tempfile 车削，用后即焚）
# ---------------------------------------------------------------------------
PROBE_TEMPLATE = '''# -*- coding: utf-8 -*-
"""{name} · 一过性探针（EphemeralForge 车削件，不入仓不入 git）"""
MECHANISMS = {mechanisms}


def fingerprint():
    return {{"name": {name!r}, "coverage": {coverage}, "matched": {matched}}}


def probe():
    return fingerprint()
'''


class EphemeralForge:
    def forge(self, evaluation):
        projection = evaluation.get("projection") or {}
        matched = [s["id"] for s in projection.get("scores") or [] if s["score"] > 0]
        source = PROBE_TEMPLATE.format(
            name=evaluation.get("candidate") or "candidate",
            mechanisms=sorted(matched),
            coverage=projection.get("coverage", 0.0),
            matched=projection.get("matched", 0),
        )
        tree_ok = True
        tree_err = ""
        try:
            ast.parse(source)
        except SyntaxError as exc:  # 语法坏的一过性件禁止转正
            tree_ok = False
            tree_err = str(exc)
        digest = _sha256(source)
        tmp = tempfile.mkdtemp(prefix="klein_forge_")
        path = os.path.join(tmp, "probe.py")
        with open(path, "w", encoding="utf-8") as f:
            f.write(source)
        return {
            "ok": tree_ok,
            "ast_parse_ok": tree_ok,
            "ast_error": tree_err,
            "path": path,
            "tmpdir": tmp,
            "sha256": digest,
            "lines": len(source.splitlines()),
            "ephemeral": True,
            "note": "一过性件只做语法校验不执行；tmpdir 用后即焚，不写入仓库",
        }

    @staticmethod
    def burn(tmpdir):
        removed = 0
        for root, _dirs, files in os.walk(tmpdir, topdown=False):
            for name in files:
                try:
                    os.remove(os.path.join(root, name))
                    removed += 1
                except OSError:
                    pass
            try:
                os.rmdir(root)
            except OSError:
                pass
        return {"ok": not os.path.exists(tmpdir), "removed": removed, "tmpdir": tmpdir}


# ---------------------------------------------------------------------------
# 第六段：Hardener —— 硬核代码化（测试全绿才转正）
# ---------------------------------------------------------------------------
class Hardener:
    def harden(self, candidate, forge_result, gates):
        unmet = [g for g in PROMOTE_GATES if not gates.get(g)]
        if unmet:
            return {"ok": False, "promoted": False, "unmet": unmet,
                    "note": "四闸未全绿，保持一过性，禁止转正"}
        manifest = {
            "name": candidate,
            "module": "%s.py" % re.sub(r"[^a-z0-9_]+", "_", candidate.lower()),
            "sha256": forge_result.get("sha256"),
            "lines": forge_result.get("lines"),
            "gates": {g: True for g in PROMOTE_GATES},
            "promoted_at": _now(),
            "seal": SEAL,
            "note": "转正件必须带测试与 manifest；一过性件永不入库",
        }
        return {"ok": True, "promoted": True, "unmet": [], "manifest": manifest}


# ---------------------------------------------------------------------------
# 第七段：ProjectLibrary —— 本地项目库（仓外 JSON 索引，反复使用）
# ---------------------------------------------------------------------------
class ProjectLibrary:
    def __init__(self, path=None):
        self.path = path or DEFAULT_LIBRARY

    def load(self):
        doc = _read_json(self.path)
        if not isinstance(doc, dict):
            doc = {"schema_version": SCHEMA_VERSION, "projects": [], "updated_at": None}
        doc.setdefault("projects", [])
        return doc

    def register(self, manifest, extra=None):
        doc = self.load()
        name = manifest.get("name")
        entry = {"name": name, "license_mode": (extra or {}).get("license_mode"),
                 "coverage": (extra or {}).get("coverage"),
                 "sha256": manifest.get("sha256"), "lines": manifest.get("lines"),
                 "registered_at": _now()}
        for i, item in enumerate(doc["projects"]):
            if item.get("name") == name:
                entry["uses"] = int(item.get("uses") or 1) + 1
                doc["projects"][i] = entry
                break
        else:
            entry["uses"] = 1
            doc["projects"].append(entry)
        doc["updated_at"] = _now()
        _write_json(self.path, doc)
        return {"ok": True, "path": self.path, "total": len(doc["projects"]),
                "entry": entry, "uses": entry["uses"]}

    def index(self):
        doc = self.load()
        return {"path": self.path, "total": len(doc.get("projects") or []),
                "projects": doc.get("projects") or []}


# ---------------------------------------------------------------------------
# 贯穿段：ChatFrontendPack —— 对话窗口提示包（平台即前端，本地库即后端）
# ---------------------------------------------------------------------------
class ChatFrontendPack:
    TEMPLATE = """# {name} · 吸纳作业提示包（{schema}）

> 把本包整段粘贴到任意大模型对话窗口即可开工：平台即前端，本地项目库即后端。
> 封口密语：{seal} ｜ 证据等级：simulated，仿真≠证明，碳基终裁。

## 一、候选概况
- 候选：{name}
- 许可证：{license}（{license_class} / 模式 {mode}）
- 机制覆盖：{coverage}
- 裁决：{verdict} —— {reason}

## 二、全息投影（11 机制）
{mechanism_lines}

## 三、张量耦合物
- D 轴（取）：{d_axis}
- X 轴（弃）：{x_axis}
- 张量形状：{shape}

## 四、收敛判据
- 两轮投影分差：{delta}
- 结论：{converged}

## 五、硬纪律（粘贴执行时逐条守住）
1. 传染性许可证只蒸馏创意，不复制代码（思想-表达二分法）。
2. 一过性代码只进临时目录，永不入库、永不入 git。
3. 转正必须四闸全绿：{gates}。
4. 不新增扩展包、不动冻结核心、diff0 不漂移。

## 六、下一步（人工指令）
按上面 D/X 轴决定吸纳范围 → 交机床车削 → 测试全绿再转正入库。
"""

    def render(self, evaluation, coupler, convergence=None):
        projection = evaluation.get("projection") or {}
        ruling = evaluation.get("license_ruling") or {}
        lines = []
        for s in projection.get("scores") or []:
            mark = "✅" if s["score"] > 0 else "·"
            lines.append("%s %s（%s）score=%.2f%s" % (
                mark, s["name"], s["en"], s["score"],
                (" hits=" + ",".join(s["hits"])) if s["hits"] else ""))
        conv = convergence or {}
        return self.TEMPLATE.format(
            name=evaluation.get("candidate"),
            schema=SCHEMA_VERSION,
            seal=SEAL,
            license=ruling.get("license"),
            license_class=ruling.get("class"),
            mode=ruling.get("mode"),
            coverage=projection.get("coverage"),
            verdict=evaluation.get("verdict"),
            reason=evaluation.get("reason"),
            mechanism_lines="\n".join(lines),
            d_axis=",".join(coupler.get("d_axis") or []) or "(空)",
            x_axis=",".join(coupler.get("x_axis") or []) or "(空)",
            shape=coupler.get("tensor_shape"),
            delta=conv.get("delta_max", "n/a"),
            converged=conv.get("verdict", "n/a"),
            gates="/".join(PROMOTE_GATES),
        )


# ---------------------------------------------------------------------------
# 总装：KleinProjection —— 一张全息图读任意候选
# ---------------------------------------------------------------------------
class KleinProjection:
    def __init__(self, library_path=None):
        self.intake = CandidateIntake()
        self.evaluator = HoloEvaluator()
        self.gate = QuartetGate()
        self.coupler = TensorCoupler()
        self.forge = EphemeralForge()
        self.hardener = Hardener()
        self.library = ProjectLibrary(library_path)
        self.frontend = ChatFrontendPack()

    def status(self):
        return {
            "module": "klein_projection",
            "version": "V27",
            "schema": SCHEMA_VERSION,
            "seal": SEAL,
            "mechanisms": len(self.evaluator.mechanisms),
            "license_rules": len(LICENSE_RULES),
            "promote_gates": list(PROMOTE_GATES),
            "library": self.library.path,
            "atlas_entries": len(ATLAS_ENTRIES),
            "collected_at": _now(),
        }

    def assess(self, path, adopt=True):
        intake = self.intake.load(path)
        if not intake["ok"]:
            return {"ok": False, "stage": "intake", "intake": intake}
        profile = intake["profile"]
        evaluation = self.evaluator.evaluate(profile)
        gate = self.gate.gate(evaluation)
        coupler = self.coupler.couple(evaluation)
        convergence = self.coupler.converge(profile, self.evaluator)
        forge = self.forge.forge(evaluation)
        gates = {
            "tests_green": False,          # 转正前必须实测，默认不绿（诚实化）
            "no_forbidden_import": True,
            "ast_parse_ok": bool(forge.get("ast_parse_ok")),
            "manifest_written": False,
        }
        harden = self.hardener.harden(profile["name"], forge, gates)
        pack = self.frontend.render(evaluation, coupler, convergence)
        if adopt:
            self.forge.burn(forge.get("tmpdir"))
        return {
            "ok": True,
            "stage": "assessed",
            "profile": profile,
            "evaluation": evaluation,
            "gate": gate,
            "coupler": coupler,
            "convergence": convergence,
            "forge": {"sha256": forge["sha256"], "lines": forge["lines"],
                      "ast_parse_ok": forge["ast_parse_ok"], "burned": adopt},
            "harden": harden,
            "frontend_pack": pack,
            "seal": SEAL,
        }

    def atlas(self):
        return [dict(item) for item in ATLAS_ENTRIES]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _main(argv):
    if not argv:
        print("usage: python -m holoaeon.klein_projection "
              "status|atlas|assess <candidate.json>|frontend <candidate.json>|library")
        return 1
    cmd = argv[0]
    kp = KleinProjection()
    if cmd == "status":
        print(json.dumps(kp.status(), ensure_ascii=False, indent=2))
        return 0
    if cmd == "atlas":
        for item in kp.atlas():
            print("%-16s %-10s -> %-24s [%s]" % (
                item["segment"], item["part"], item["target"], item["source"]))
        print("total:", len(kp.atlas()))
        return 0
    if cmd == "library":
        print(json.dumps(kp.library.index(), ensure_ascii=False, indent=2))
        return 0
    if cmd in ("assess", "frontend"):
        if len(argv) < 2:
            print("need candidate json path")
            return 2
        result = kp.assess(argv[1])
        if cmd == "frontend":
            print(result.get("frontend_pack") or json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get("ok") else 3
    print("unknown command:", cmd)
    return 1


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
