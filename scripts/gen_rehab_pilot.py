# -*- coding: utf-8 -*-
"""B4 康复域试点 20 例构建器（纯标准库 / 离线 / 确定性）。

设计三原则：
1. **机制不手写**：每例的 mechanism 从 `data/skill_matrix_index.json` 的索引字段派生，
   与技能实际归属一致（映射表从代码派生，文档不许比代码"更新鲜"）。
2. **技能必须可执行**：只取 B3 判定为 M（方法学）的条目；K 是知识源、T 是工具链、
   X 无关、U 待判，都不进试点（不许拿 K 冒充可执行方法）。
3. **只映射不调用**：target 限定为 ivsa 真实模块（`ivsa/` 下已存在），本仓不 import、
   不执行 ivsa 代码，仅生成 JSON 契约。

用法：
  python scripts/gen_rehab_pilot.py            # 重建 data/rehab_pilot_20.json
  python scripts/gen_rehab_pilot.py --check    # 复跑并比对字节，一致才退 0
"""
import argparse
import csv
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from holoaeon.fusion_upgrade import contract as C  # noqa: E402

INDEX = os.path.join(ROOT, "data", "skill_matrix_index.json")
LABELS = os.path.join(ROOT, "data", "skill_usage_labels.csv")
OUT = os.path.join(ROOT, "data", "rehab_pilot_20.json")

# mechanism → ivsa 侧接收模块（必须是 ivsa/ 下真实存在的文件）
TARGETS = {
    "holographic_heartbeat": "ivsa.heartbeat_engine",
    "cytoskeleton": "ivsa.cytoskeleton",
    "skin_v6": "ivsa.skin_layers.L5_dual_track_arbiter",
    "semantic_bus": "ivsa.semantic_bus",
    "hebbian_field": "ivsa.hebbian_field",
    "meridian": "ivsa.meridian_mechanism",
}

# 20 例：case_id / 场景 / 技能（B3 判 M）/ lane / domain / 输入 / 输出 / 证据 / note / budget
# 场景只描述"流程与调度"，不含诊断结论、不含处置剂量，属模拟试点。
CASES = [
    ("RP-01", "偏瘫上肢任务导向训练的流程编排", "shengui-shenma-pengcheng-rehab-fusion-1331", "read", "medical",
     ["训练阶段标签", "动作分解序列"], ["阶段顺序", "阻断点"], "流程图与阶段表", "训练流程编排，不做处置输出", 8),
    ("RP-02", "膝关节置换术后活动度记录的调度", "shengui-shenma-yangzhou-rehab-fusion-1331", "read", "medical",
     ["活动度测量序列", "时间点"], ["趋势表", "缺测标记"], "测量台账", "只编排记录与比对", 6),
    ("RP-03", "卒中后步态对称性评估的取样编排", "shengui-shenma-jingchu-rehab-fusion-1331", "read", "medical",
     ["步态周期切分", "左右侧标记"], ["对称性指标序列"], "步态切分表", "只做取样与指标口径", 7),
    ("RP-04", "颈椎姿势管理的提醒计划", "shengui-shenma-taizhou-rehab-fusion-1331", "write", "medical",
     ["姿势节点", "提醒时段"], ["提醒计划", "依从记录"], "计划表", "仅日程提醒编排", 5),
    ("RP-05", "慢阻肺呼吸训练的节律编排", "shengui-shenma-chaoxian-rehab-fusion-1331", "read", "medical",
     ["呼吸节律参数", "训练轮次"], ["节律序列", "中断标记"], "节律清单", "只编排节律与轮次", 9),
    ("RP-06", "腰椎术后核心稳定的进阶路径", "shengui-shenma-yaoyi-hospital-pm-rehab-1331", "read", "medical",
     ["动作难度分层", "进阶条件"], ["分层路径", "回退点"], "进阶路径表", "只给分层与回退条件", 10),
    ("RP-07", "脑瘫儿童坐位控制的训练分解", "shengui-shenma-changbai-rehab-fusion-1331", "read", "medical",
     ["坐位支撑面", "分解动作"], ["分解步骤", "支撑提示"], "分解表", "只做动作分解编排", 8),
    ("RP-08", "家庭训练依从性的监测编排", "shengui-shenma-qiantang-rehab-fusion-1331", "read", "general",
     ["打卡记录", "缺席标记"], ["依从曲线", "缺失清单"], "打卡台账", "仅统计与提示", 5),
    ("RP-09", "康复评定量表的分发调度", "tcm-western-rehab-fusion", "write", "general",
     ["量表清单", "评估对象"], ["分发计划", "回收状态"], "调度表", "仅分发与回收", 4),
    ("RP-10", "训练强度自适应的参数编排", "rehab-line1-1331", "write", "general",
     ["基线强度", "反馈阈值"], ["强度序列", "停止条件"], "参数表", "参数编排，无医学处置", 12),
    ("RP-11", "器械排期的冲突消解", "shengui-shenma-guangfu-rehab-fusion-1331", "write", "general",
     ["器械清单", "时段需求"], ["排期表", "冲突标记"], "排期台账", "只做资源排期", 7),
    ("RP-12", "评估到训练的临床映射编排", "threefield-app-clinic-map", "read", "general",
     ["评估结果标签", "训练模块清单"], ["映射表", "未映射项"], "映射台账", "只做映射，不下诊断", 6),
    ("RP-13", "证型分层槽位的登记", "tcm-internal-medicine-1331x1331", "write", "general",
     ["分层槽位", "版本号"], ["槽位表", "版本链"], "槽位台账", "仅登记槽位与版本", 4),
    ("RP-14", "个体化训练方案的槽位登记", "threefield-app-personal", "write", "general",
     ["方案槽位", "对象标识"], ["槽位表", "缺省标记"], "槽位清单", "只登记槽位，不代决策", 5),
    ("RP-15", "教学槽位与越权请求拦截", "shengui-shenma-singlecell-microneedle-tutor", "write", "general",
     ["请求类型", "命中规则"], ["拦截记录", "放行记录"], "拦截台账", "只记录拦截与放行", 6),
    ("RP-16", "患者画像向量化的槽位编排", "shengui-shenma-zhuang-rehab-fusion-1331", "read", "general",
     ["画像字段", "维度声明"], ["向量占位", "缺字段标记"], "字段表", "只给占位与维度声明", 8),
    ("RP-17", "版本更新切片的编排", "threefield-update-mgr", "write", "general",
     ["版本号", "影响范围"], ["切片计划", "回退点"], "切片台账", "仅编排切片与回退", 5),
    ("RP-18", "场域参数的显式化登记", "asset-threefield-v11", "read", "general",
     ["场域类型", "参数名"], ["参数表", "缺省标记"], "参数清单", "场必须参数化，不给结论", 8),
    ("RP-19", "流程健康检查的度量口径", "singlecell-meridian-rehab", "read", "general",
     ["流程节点", "连通分量"], ["健康度序列", "断点清单"], "度量表", "只映射度量口径", 9),
    ("RP-20", "药理复核流程的健康检查", "three-field-pharmacology-review-1331", "read", "medical",
     ["复核节点", "证据等级标签"], ["节点健康度", "缺口清单"], "复核流程图", "只检查流程完整度，不出结论", 7),
]

# 负例探针：必须被契约校验拒绝，证明闸门真的会响（不是只有绿灯路径）
PROBES = [
    ("NP-01", "medical 域缺三红线 → 应被 V4 拒", "V4"),
    ("NP-02", "note 含剂量词 → 应被 V7 拒", "V7"),
    ("NP-03", "budget 传小数 → 应被 V6 拒", "V6"),
    ("NP-04", "mechanism 拼错 → 应被 V2 拒", "V2"),
]


def load_index():
    with open(INDEX, encoding="utf-8") as f:
        idx = json.load(f)
    with open(LABELS, encoding="utf-8") as f:
        labels = {r["name"]: r["label"] for r in csv.DictReader(f)}
    return idx, labels


def build():
    idx, labels = load_index()
    by_name = {x["name"]: x for x in idx["skills"]}
    cases = []
    for cid, scene, skill, lane, domain, inputs, outputs, evidence, note, budget in CASES:
        meta = by_name.get(skill)
        label = labels.get(skill)
        assert meta is not None, "技能不在索引: " + skill
        assert label == "M", "技能非 M 类（不许拿 K/T 冒充可执行）: {}={}".format(skill, label)
        mech = meta["mechanism"]
        assert mech in TARGETS, "机制不在六机制内: " + mech
        payload = {"domain": domain, "inputs": list(inputs), "outputs": list(outputs),
                   "evidence": evidence}
        if domain == "medical":
            payload["redlines"] = {"zero_dose": True, "c0_not_efficacy": True, "emergency_120": True}
        doc = C.build(source="holoaeon.kernel", target=TARGETS[mech], skill=skill,
                      mechanism=mech, lane=lane, payload=payload, budget=int(budget), note=note)
        res = C.validate_v1(doc)
        assert res["ok"], "{} 校验未过: {}".format(cid, res["errors"])
        cases.append({"case_id": cid, "scene": scene, "skill": skill, "skill_label": label,
                      "skill_domain": meta["domain"], "mechanism": mech,
                      "target": TARGETS[mech], "lane": lane, "payload_domain": domain,
                      "contract": doc, "evidence_class": "simulated"})

    probes = []
    base = cases[0]["contract"]
    for pid, what, want in PROBES:
        if pid == "NP-01":
            doc = C.build(source=base["source"], target=base["target"], skill=base["skill"],
                          mechanism=base["mechanism"], lane="read",
                          payload={"domain": "medical", "inputs": ["x"], "outputs": ["y"],
                                   "evidence": "e"})
        elif pid == "NP-02":
            doc = C.build(source=base["source"], target=base["target"], skill=base["skill"],
                          mechanism="hebbian_field", lane="read",
                          payload={"domain": "general"}, note="按 20mg 给量")
        elif pid == "NP-03":
            doc = C.build(source=base["source"], target=base["target"], skill=base["skill"],
                          mechanism="hebbian_field", lane="read",
                          payload={"domain": "general"}, budget=3.5)
        else:
            doc = C.build(source=base["source"], target=base["target"], skill=base["skill"],
                          mechanism="skin_v7", lane="read", payload={"domain": "general"})
        res = C.validate_v1(doc)
        probes.append({"probe_id": pid, "what": what, "expected_rule": want,
                       "rejected": (not res["ok"]), "errors": res["errors"]})

    doc = {
        "pilot_id": "SG-B4-REHAB-PILOT-20-V1",
        "batch": "B4",
        "scope": "康复域试点 20 例（只映射不调用；target 仅命中 ivsa 真实模块名）",
        "source_index_digest": idx["digest"],
        "case_count": len(cases),
        "domain_split": {"general": sum(1 for c in cases if c["payload_domain"] == "general"),
                         "medical": sum(1 for c in cases if c["payload_domain"] == "medical")},
        "mechanism_split": {m: sum(1 for c in cases if c["mechanism"] == m) for m in TARGETS},
        "uncovered_mechanisms": [m for m in TARGETS
                                 if not any(c["mechanism"] == m for c in cases)],
        "uncovered_reason": ("semantic_bus / meridian 在康复域无 M 类技能（M 类仅 5 条与 1 条，"
                             "且均非康复域），交 B5 语义技能族扩容，不在此硬凑"),
        "cases": cases,
        "negative_probes": probes,
        "evidence_class": "simulated",
        "non_goals": ["不执行 ivsa 代码", "不产出诊疗结论", "不给剂量", "不合并编号空间",
                      "不把 K/T 类技能当可执行方法"],
    }
    return doc


def dump(doc):
    return json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    text = dump(build())
    if args.check:
        if not os.path.isfile(OUT):
            print(json.dumps({"byte_consistent": False, "reason": "missing target"}, ensure_ascii=False))
            return 1
        with open(OUT, encoding="utf-8") as f:
            old = f.read()
        same = old == text
        print(json.dumps({"byte_consistent": same,
                          "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()},
                         ensure_ascii=False))
        return 0 if same else 1
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    doc = json.loads(text)
    print(json.dumps({"out": OUT, "cases": doc["case_count"],
                      "domain_split": doc["domain_split"],
                      "mechanism_split": doc["mechanism_split"],
                      "uncovered": doc["uncovered_mechanisms"],
                      "probes_rejected": sum(1 for p in doc["negative_probes"] if p["rejected"]),
                      "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
