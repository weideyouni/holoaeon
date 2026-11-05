# -*- coding: utf-8 -*-
"""magic_lamp — 神灯模式（V29，诉求驱动总装编排层）
第一性原理：愿望的满足顺序=先翻衣柜再造新衣。
已知技能组合装配（O(索引)确定性）→ 缺口才生成 GitHub 搜索规格
（模块零网络，联网由总监/豆包侧执行）→ 启动三链（漩涡→投影→熔炉）
→ 试测先行（在测试前先测试）→ 论证可行后执行。
组织维度 DNA 六条（V24-V27 提炼）：段化流水线/Envelope契约/确定性判定/
一过性先行/append-only台账/心跳单批。
零依赖纯标准库。封口密语：潮起开门，潮落闭嘴。
"""
import json
import os
import sys
import tempfile
import time

SEAL = "潮起开门，潮落闭嘴"

# ── ORG-1~6：V24-V27 提炼的组织维度模式（固化注册表）──
ORG_PATTERNS = [
    {"id": "ORG-1", "name": "段化流水线", "source": "V24-V27",
     "rule": "每段一个类，单测独立，顺序推进"},
    {"id": "ORG-2", "name": "Envelope契约", "source": "V25/V26/V27",
     "rule": "段间传递带 seal 的载荷"},
    {"id": "ORG-3", "name": "确定性判定器", "source": "V25/V26/V27/V28",
     "rule": "涌现/收敛/兼容/一致均为阈值规则，零LLM"},
    {"id": "ORG-4", "name": "一过性先行", "source": "V27",
     "rule": "试测绿了才转正，硬核前必先试测"},
    {"id": "ORG-5", "name": "append-only台账", "source": "V25/V26/V27",
     "rule": "只追加，赫布信任累积"},
    {"id": "ORG-6", "name": "心跳单批", "source": "V25/D-13",
     "rule": "一次一批，小步慢走"},
]

# ── 已知技能索引（衣柜）：19扩展包 + 四人组14技能 + 链上三模块 ──
KNOWN_SKILLS = [
    {"name": "swarm_intel", "caps": ["群体模拟", "五阶段流水线", "persona", "报告生成"]},
    {"name": "machine_tool", "caps": ["基线检查", "投喂包", "五地同步", "闸门"]},
    {"name": "mobius_vortex", "caps": ["状态回传", "三点对齐", "简报"]},
    {"name": "klein_projection", "caps": ["开源吸纳", "投影评估", "一过性车削", "项目库"]},
    {"name": "holo_forge", "caps": ["基座选择", "乐高拼接", "四态融合"]},
    {"name": "dehallucination", "caps": ["真实性校验", "去幻觉"]},
    {"name": "vector_sea", "caps": ["技能索引", "勘探", "选择性加载"]},
    {"name": "skill_lathe", "caps": ["技能车削", "协议适配"]},
    {"name": "quartet_tensor", "caps": ["张量耦合", "扬弃分析"]},
    {"name": "emergence_chain", "caps": ["涌现判定", "五步协议"]},
    {"name": "butler_os", "caps": ["低硬件躯体", "对话前端"]},
    {"name": "protocol_plugins", "caps": ["多平台适配", "协议"]},
    {"name": "concept_anatomy", "caps": ["概念解剖", "创意评估"]},
    {"name": "topology_resonance", "caps": ["拓扑", "共振"]},
]

STATES = ("ready_assembled", "needs_search", "test_failed")


class LampWish:
    """W1段：诉求受理（细胞骨架）。"""

    @staticmethod
    def create(goal, requirements, constraints=None):
        if not goal or not requirements:
            return {"ok": False, "error": "goal/requirements required"}
        return {"ok": True, "goal": goal,
                "requirements": [r.lower() for r in requirements],
                "constraints": constraints or [],
                "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}


class OrgPatternLoader:
    """W2段：加载组织维度 DNA。"""

    @staticmethod
    def load():
        return [dict(p) for p in ORG_PATTERNS]


class KnownSkillIndex:
    """W3段：已知技能索引——关键词共振匹配（经络）。"""

    @staticmethod
    def match(requirements, registry=None):
        reg = registry or KNOWN_SKILLS
        hits = []
        for skill in reg:
            caps = [c.lower() for c in skill["caps"]]
            hit = [r for r in requirements
                   if any(r in c or c in r for c in caps)]
            if hit:
                hits.append({"skill": skill["name"], "covers": hit})
        return hits


class SkillAssembler:
    """W4段：组合装配——贪心覆盖。"""

    @staticmethod
    def assemble(requirements, hits):
        covered, plan = set(), []
        for h in sorted(hits, key=lambda x: -len(x["covers"])):
            new = [r for r in h["covers"] if r not in covered]
            if new:
                covered.update(new)
                plan.append({"skill": h["skill"], "covers": new})
        return {"plan": plan, "coverage": round(
            len(covered) / max(len(requirements), 1), 4)}


class GapDetector:
    """W5段：缺口检测（涨落放大点）。"""

    @staticmethod
    def detect(requirements, covered):
        return [r for r in requirements if r not in covered]


class GitHubSearchPlanner:
    """W6段：搜索规格——零网络，只出数据（联网执行权在碳基终审）。"""

    @staticmethod
    def plan(gaps, goal):
        queries = [" ".join(gaps[:3]) + " github",
                   goal + " open source github"]
        template = {"name": None, "repo": None, "license": None,
                    "language": None, "keywords": gaps}
        return {"gaps": gaps, "queries": queries, "candidate_template":
                template, "executed_by": "director_or_doubao(联网侧)",
                "module_network": False, "seal": SEAL}


class LampChainTrigger:
    """W7段：启动三链——漩涡→投影→熔炉（D-11 链式执行层）。"""

    CHAIN = ["mobius_vortex(回流)", "klein_projection(投影)", "holo_forge(熔炼)"]

    @staticmethod
    def trigger(wish, plan):
        return {"chain": list(LampChainTrigger.CHAIN),
                "payload": {"goal": wish["goal"], "assembly": plan,
                            "seal": SEAL},
                "order": "回流(状态)→投影(吸纳)→熔炼(融合)"}


class EphemeralFirstTester:
    """W8段：试测先行——在测试前先测试（ORG-4 硬门）。"""

    PROBE = ('def probe():\n'
             '    """一过性探针：验证装配方案的最小可运行性。"""\n'
             '    return {"goal": __GOAL__, "steps": __STEPS__}\n')

    @staticmethod
    def test(goal, plan, checker=None):
        # C-01 最小修复：原 PROBE 用 str.format，与探针返回字典的花括号冲突
        # （KeyError: '"goal"'）；改用 JSON 字面量替换，既避冲突又防引号注入。
        code = (EphemeralFirstTester.PROBE
                .replace("__GOAL__", json.dumps(goal, ensure_ascii=False))
                .replace("__STEPS__", json.dumps(len(plan), ensure_ascii=False)))
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "lamp_probe.py")
            with open(path, "w", encoding="utf-8") as f:
                f.write(code)
            ok = True if checker is None else bool(checker(path))
        return {"probe_ok": ok, "burned": not os.path.exists(tmp),
                "code_chars": len(code)}


class LampProposal:
    """W9段：方案书——可行性裁决+全记录（文本化 Envelope）。"""

    @staticmethod
    def render(wish, assembly, gap_result, chain, probe, patterns):
        if not probe["probe_ok"]:
            state = "test_failed"
        elif gap_result["coverage"] >= 1.0:
            state = "ready_assembled"
        else:
            state = "needs_search"
        lines = [
            "# 神灯方案书 · " + wish["goal"], "",
            "> 封口密语：" + SEAL,
            "> 组织维度DNA：" + "、".join(p["id"] for p in patterns),
            "> 状态：" + state + "（碳基终审签收前不执行硬核动作）", "",
            "## 装配方案", "",
        ]
        for item in assembly["plan"]:
            lines.append(f"- {item['skill']} ← {item['covers']}")
        lines.append("")
        lines.append(f"- 覆盖率：{gap_result['coverage']}")
        if state == "needs_search":
            lines.append("- 缺口（待联网勘探）：" +
                         "、".join(gap_result["gaps"]))
        lines.append(f"- 三链：{chain['order']}")
        lines.append(f"- 试测：{'PASS（探针已焚）' if probe['probe_ok'] else 'FAIL'}")
        return {"state": state, "text": "\n".join(lines), "seal": SEAL}


class MagicLamp:
    """总装：愿望编译流水线 W1-W9（心跳：一个愿望一轮）。"""

    PIPELINE = ["W1_intake", "W2_patterns", "W3_index", "W4_assemble",
                "W5_gap", "W6_search_plan", "W7_chain", "W8_probe", "W9_proposal"]

    def __init__(self, registry=None):
        self.registry = registry

    def wish(self, goal, requirements, constraints=None, checker=None):
        w = LampWish.create(goal, requirements, constraints)
        if not w["ok"]:
            return w
        patterns = OrgPatternLoader.load()
        hits = KnownSkillIndex.match(w["requirements"], self.registry)
        asm = SkillAssembler.assemble(w["requirements"], hits)
        gaps = GapDetector.detect(w["requirements"], set(
            r for p in asm["plan"] for r in p["covers"]))
        search = GitHubSearchPlanner.plan(gaps, w["goal"]) if gaps else None
        chain = LampChainTrigger.trigger(w, asm["plan"])
        probe = EphemeralFirstTester.test(w["goal"], asm["plan"],
                                          checker=checker)
        proposal = LampProposal.render(w, asm,
                                       {"coverage": asm["coverage"],
                                        "gaps": gaps},
                                       chain, probe, patterns)
        return {"wish": w, "patterns": patterns, "assembly": asm,
                "gaps": gaps, "search_plan": search, "chain": chain,
                "probe": probe, "proposal": proposal, "seal": SEAL}


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "patterns"
    if cmd == "patterns":
        for p in ORG_PATTERNS:
            print(f"{p['id']} {p['name']}（{p['source']}）：{p['rule']}")
    elif cmd == "wardrobe":
        for s in KNOWN_SKILLS:
            print(f"{s['name']}: {', '.join(s['caps'])}")
    else:
        print("usage: python -m holoaeon.magic_lamp [patterns|wardrobe]")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
