# -*- coding: utf-8 -*-
"""gap_bridge — 缺口进化桥（V32）
D-11 链位：桥梁环（非新环）——连接 神灯 magic_lamp（W5 缺口）
与 泰坦 titan_evolver（propose 入口）。
第一性原理：缺口是涨落放大点——把涨落直接接入进化原语，
全息闭环的最后一段。环境自检是通路的路面平整度检查。
零依赖纯标准库。封口密语：潮起开门，潮落闭嘴。
红线：不新增扩展包；不碰冻结维度；G1 只报不删（处置权=碳基终审）。
"""
import json
import os
import sys

SEAL = "潮起开门，潮落闭嘴"

# D-11 链位自声明（桥梁环）
CHAIN_POSITION = {
    "ring": "bridge",
    "name": "缺口进化桥",
    "upstream": ("magic_lamp", "titan_evolver"),
    "role": "神灯缺口(W5) → 泰坦 propose 入口的最后一米",
    "note": "连接器不新增环，维度不变",
}

# 常被遮蔽的 stdlib 名（高频受害模块，可扩展）
SHADOWABLE = ("inspect", "json", "os", "sys", "time", "types",
              "test", "code", "token", "copy", "queue", "email")

# 泰坦 propose 契约（对齐 CapabilityManifest，执行时可适配字段名）
PROPOSE_FIELDS = ("capability", "source", "evidence", "threshold")


class StdlibShadowGuard:
    """G1：环境自检——stdlib 遮蔽检测（只报不删）。"""

    def __init__(self, cwd=None):
        self.cwd = cwd or os.getcwd()

    def scan(self, extra_paths=None):
        offenders = []
        checked = []
        for d in [self.cwd] + list(extra_paths or []):
            if not d or not os.path.isdir(d):
                continue
            checked.append(d)
            for name in SHADOWABLE:
                p = os.path.join(d, name + ".py")
                if os.path.exists(p):
                    offenders.append({"dir": d, "shadow": name + ".py",
                                      "stdlib": name})
        return {"ok": len(offenders) == 0, "offenders": offenders,
                "dirs_checked": checked, "action": "report_only"
                "（处置权=碳基终审，本模块不删除不改名）", "seal": SEAL}

    @staticmethod
    def unblock_hint(offenders):
        """给出处置建议（仍不执行）：改名或换 cwd。"""
        return [{"offender": o, "hint": f"rename {o['shadow']} or run from a clean cwd"}
                for o in offenders]


class SkipAuditor:
    """G2：unittest skipped 审计——清单化待查。"""

    @staticmethod
    def audit(lines):
        """输入 unittest -v 文本行，提取 skipped 用例。"""
        skips = []
        for ln in lines:
            if "skipped" in ln.lower():
                skips.append(ln.strip())
        return {"skipped_count": len(skips), "skipped": skips,
                "verdict": "needs_review" if skips else "clean",
                "seal": SEAL}


class GapProposer:
    """G3：神灯 gaps → 泰坦 propose 通路（最后一米）。"""

    def __init__(self, threshold=0.6):
        self.threshold = threshold

    def propose(self, gaps, goal, source="magic_lamp.W5"):
        """一条 gap 一条 propose（契约字段对齐 CapabilityManifest）。"""
        if isinstance(gaps, str):
            gaps = [gaps]
        props = []
        for g in gaps or []:
            props.append({"capability": g,
                          "source": source,
                          "evidence": f"wish goal: {goal}",
                          "threshold": self.threshold})
        return {"proposals": props, "count": len(props),
                "next_step": "titan_evolver adopt 编排（七步合入）",
                "seal": SEAL}

    @staticmethod
    def to_titan(proposals):
        """输出泰坦可读格式（dict 流，豆包执行时按 CapabilityManifest 适配）。"""
        return [{k: p.get(k) for k in PROPOSE_FIELDS} for p in proposals]


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "chain"
    if cmd == "chain":
        print(json.dumps(CHAIN_POSITION, ensure_ascii=False, indent=1))
    elif cmd == "shadowscan":
        g = StdlibShadowGuard(sys.argv[2] if len(argv) > 2 else None)
        print(json.dumps(g.scan(), ensure_ascii=False, indent=1))
    else:
        print("usage: python -m holoaeon.gap_bridge [chain|shadowscan [dir]]")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
