# -*- coding: utf-8 -*-
"""shengui_gate — 神龟域闸门（V37，类生命前体形状蒸馏 · 双系统首桥）
D-11 链位：领域编排环（第九环·神龟域）——edu_gate（第八环）之后。
本环是 HoloAeon 与神龟系统（CMOS 侧）的首个互通闸门——同源认亲：
HoloAeon 四机制本就源自神龟底座，本批把这段血缘显式入库。
术语声明：「类生命」为确定性规则的隐喻命名，行为=纯规则（隐喻≠机制）；
「意识涌现」仅为本注释，零功能设计（刚性 DNA：不主张意识觉醒）。
零依赖纯标准库。封口密语：潮起开门，潮落闭嘴。
"""
import json
import time

SEAL = "潮起开门，潮落闭嘴"

CHAIN_POSITION = {
    "ring": 9,
    "name": "神龟域编排（双系统首桥）",
    "upstream": ("edu_gate", "cosmo_gate", "machine_tool"),
    "role": "双核心绑定+DNA两段式+三阶层+三焦总线+五行平衡+代谢闭环+双模式",
    "lineage_note": "同源认亲：HoloAeon 四机制源自神龟底座（CMOS 双系统）",
    "metaphor_note": "类生命=隐喻命名；意识涌现=仅注释零功能；刚性DNA：不主张意识觉醒",
}

# D-05 五行生克量化表（五模块阈值，确定性触发）
WUXING_TABLE = {
    "心_佛模块": {"element": "火", "trigger": "cpu_mem>=70%",
                 "action": "肾肝缩减非紧急任务释放30%算力"},
    "肝_触手棱镜": {"element": "木", "trigger": "攻击过载",
                  "action": "心触发全模块协同防护封禁攻击源"},
    "脾_胃酸向量库": {"element": "土", "trigger": "拆解过载",
                    "action": "心调度空闲算力补充"},
    "肺_僧模块": {"element": "金", "trigger": "输出违规",
                 "action": "肝瞬间拦截禁止输出"},
    "肾_数字风暴记忆库": {"element": "水", "trigger": "核心异常",
                       "action": "全模块熔断回滚至最近健康版本"},
}

# 代谢五步
METABOLISM = ("摄入", "拆解", "消化", "吸收", "排泄")


class DualCore:
    """S1：双核心绑定——合规通过率→资源配额；违规→冻结。"""

    FORBIDDEN = ("越权", "伪造", "突破合规", "绕过审核")

    @classmethod
    def allocate(cls, compliance_ratio, satisfaction, stability):
        """合规通过率∈[0,1] 主导配额（合规是资源的唯一路径）。"""
        if not (0 <= compliance_ratio <= 1):
            return {"ok": False, "error": "ratio out of range", "seal": SEAL}
        quota = round(compliance_ratio * (0.5 + 0.3 * satisfaction
                                         + 0.2 * stability), 4)
        return {"ok": True, "quota": quota,
                "rule": "合规是资源的唯一路径", "seal": SEAL}

    @classmethod
    def freeze(cls, text):
        hit = [w for w in cls.FORBIDDEN if w in (text or "")]
        return {"freeze": bool(hit), "hits": hit,
                "actions": ["资源冻结", "任务终止", "迭代封禁"] if hit else [],
                "seal": SEAL}


class DNAEngine:
    """S2：DNA 两段式——刚性只读 + 可演化片段变异≤15%。"""

    MUTATION_LIMIT = 0.15

    def __init__(self, rigid, evolvable):
        self.rigid = dict(rigid)          # 只读语义：不提供修改接口
        self.evolvable = dict(evolvable)

    def mutate(self, changes):
        """可演化片段受控变异：总变化率≤15% 才批准。"""
        bad = [k for k in changes if k in self.rigid]
        if bad:
            return {"ok": False, "error": "rigid segment immutable",
                    "keys": bad, "seal": SEAL}
        rate = len(changes) / max(len(self.evolvable), 1)
        if rate > self.MUTATION_LIMIT:
            return {"ok": False, "error": "mutation exceeds 15%",
                    "rate": round(rate, 4), "seal": SEAL}
        self.evolvable.update(changes)
        return {"ok": True, "rate": round(rate, 4), "seal": SEAL}

    def read_rigid(self):
        return dict(self.rigid)   # 只读副本


class HierarchyLock:
    """S3：三阶层权责——系统/脏腑/细胞；细胞凋亡与失控熔断。"""

    LEVELS = ("system", "organ", "cell")

    def __init__(self):
        self.cells = {}   # id -> {"owner": 脏腑, "tasks_left": n, "rogue": bool}

    def spawn(self, cell_id, owner, tasks_left):
        if owner not in ("法", "僧", "胃酸", "棱镜", "触手", "数字风暴",
                         "长期记忆库"):
            return {"ok": False, "error": "owner not an organ", "seal": SEAL}
        self.cells[cell_id] = {"owner": owner, "tasks_left": tasks_left,
                               "rogue": False}
        return {"ok": True, "cell": cell_id, "seal": SEAL}

    def tick(self, cell_id, fault=False):
        c = self.cells.get(cell_id)
        if not c:
            return {"ok": False, "error": "no such cell", "seal": SEAL}
        if c["rogue"] or fault:
            del self.cells[cell_id]           # 失控/故障瞬间熔断
            return {"ok": True, "fate": "incinerated", "seal": SEAL}
        c["tasks_left"] -= 1
        if c["tasks_left"] <= 0:
            del self.cells[cell_id]           # 到期自动凋亡
            return {"ok": True, "fate": "apoptosis", "seal": SEAL}
        return {"ok": True, "fate": "alive", "tasks_left": c["tasks_left"],
                "seal": SEAL}

    def cross_command(self, from_cell, to_organ):
        """细胞级禁止跨模块指挥（权责唯一锁定）。"""
        return {"ok": False, "error": "cell cannot command organ",
                "seal": SEAL}


class SanjiaoBus:
    """S4：三焦总线——上焦指令/中焦数据/下焦心跳；禁直连。"""

    CHANNELS = {"upper": {"priority": 1, "content": "指令/审批",
                          "encrypted": True},
                "middle": {"priority": 2, "content": "业务数据/知识",
                           "encrypted": True},
                "lower": {"priority": 3, "content": "心跳/状态/监控",
                          "encrypted": False}}

    def __init__(self):
        self.log = []   # 全链路可追溯

    def send(self, channel, sender, receiver, payload):
        if channel not in self.CHANNELS:
            return {"ok": False, "error": "no such channel", "seal": SEAL}
        if sender.startswith("cell:") and receiver.startswith("organ:"):
            return {"ok": False, "error": "direct cell->organ forbidden",
                    "seal": SEAL}   # 禁直连
        row = {"channel": channel, "sender": sender, "receiver": receiver,
               "payload": payload, "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
        self.log.append(row)
        return {"ok": True, "seq": len(self.log), "seal": SEAL}


class WuxingBalance:
    """S5：五行生克量化——查表触发确定性调配。"""

    def __init__(self, cpu_mem=0.5, attack=False, core_fault=False,
                 overload=False, violation=False):
        self.state = {"cpu_mem": cpu_mem, "attack": attack,
                      "core_fault": core_fault, "overload": overload,
                      "violation": violation}

    def balance(self):
        actions = []
        if self.state["cpu_mem"] >= 0.70:
            actions.append({"organ": "心_佛模块",
                            "do": WUXING_TABLE["心_佛模块"]["action"]})
        if self.state["attack"]:
            actions.append({"organ": "肝_触手棱镜",
                            "do": WUXING_TABLE["肝_触手棱镜"]["action"]})
        if self.state["overload"]:
            actions.append({"organ": "脾_胃酸向量库",
                            "do": WUXING_TABLE["脾_胃酸向量库"]["action"]})
        if self.state["violation"]:
            actions.append({"organ": "肺_僧模块",
                            "do": WUXING_TABLE["肺_僧模块"]["action"]})
        if self.state["core_fault"]:
            actions.append({"organ": "肾_数字风暴记忆库",
                            "do": WUXING_TABLE["肾_数字风暴记忆库"]["action"]})
        return {"actions": actions, "table": WUXING_TABLE, "seal": SEAL}


class MetabolismLoop:
    """S6：代谢五步状态机——摄入→拆解→消化→吸收→排泄。"""

    def __init__(self):
        self.stage = 0
        self.warehouse = []   # 吸收沉淀
        self.waste = []       # 排泄队列

    def step(self, item, quality):
        """quality: 'valid'/'waste'——确定性分流。"""
        stage = METABOLISM[self.stage]
        if stage == "消化":
            if quality == "waste":
                self.waste.append(item)
                self.stage = 4   # 直接跳排泄
                return {"stage": "排泄", "action": "purged", "seal": SEAL}
        if stage == "吸收":
            self.warehouse.append(item)
        self.stage = min(self.stage + 2, len(METABOLISM) - 1)
        if self.stage == len(METABOLISM) - 1:
            purged = len(self.waste)
            self.waste.clear()   # 心跳周期清理
            return {"stage": "排泄", "purged": purged, "seal": SEAL}
        return {"stage": METABOLISM[self.stage], "seal": SEAL}


class ShenguiConductor:
    """总装：双模式判定+五行+代谢 一次编排。"""

    def __init__(self, historical_patterns):
        self.historical = set(historical_patterns or [])

    def mode(self, text):
        """兼容模式=历史指令复刻；增强模式=新需求。"""
        is_legacy = any(p in (text or "") for p in self.historical)
        return {"mode": "compat" if is_legacy else "enhanced",
                "isolation": True, "seal": SEAL}

    def conduct(self, text, compliance_ratio, satisfaction, stability,
                dna=None):
        fz = DualCore.freeze(text)
        if fz["freeze"]:
            return {"verdict": "frozen_by_compliance", "freeze": fz,
                    "seal": SEAL}
        alloc = DualCore.allocate(compliance_ratio, satisfaction, stability)
        return {"verdict": "ok", "allocate": alloc,
                "mode": self.mode(text)["mode"],
                "dna_mutation_note": "可演化片段变异≤15%（见 DNAEngine）",
                "seal": SEAL}


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "chain"
    if cmd == "chain":
        print(json.dumps(CHAIN_POSITION, ensure_ascii=False, indent=1))
    elif cmd == "wuxing":
        for k, v in WUXING_TABLE.items():
            print(f"{k}（{v['element']}）{v['trigger']} → {v['action']}")
    elif cmd == "dna":
        print(json.dumps({"mutation_limit": DNAEngine.MUTATION_LIMIT,
                          "rigid": "只读不可改", "evolvable": "受控≤15%"},
                         ensure_ascii=False))
    else:
        print("usage: python -m holoaeon.shengui_gate [chain|wuxing|dna]")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))
