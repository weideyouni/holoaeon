# -*- coding: utf-8 -*-
"""V2.0 十二批次计划（可查询、可校验的计划即数据）。

为什么从八批拆成十二批：八批做不到"每批都有可测判据"——契约层与映射层各自拆两批后，
每批都能落成"七道闸全绿 + 九字段满 + 判据可跑"。
"""
from __future__ import annotations

from typing import Any, Dict, List

from .manifest import digest_of

FORBIDDEN_WORDS = ("更好", "更自然", "更智能", "体验", "流畅", "顺手", "高级感")
FIELDS = ("id", "title", "owner", "inputs", "actions", "outputs",
          "criteria", "rollback", "hours", "risks", "not_touching")

BATCHES: List[Dict[str, Any]] = [
    {"id": "B0", "title": "基线冻结", "owner": "P2 筑基", "inputs": ["两仓现态"],
     "actions": ["七道闸全跑一遍并留存票据", "把 12 条维度锁写成 fusion_lock.json",
                 "复跑两侧单测确认 34/16 不动"],
     "outputs": ["data/fusion_lock.json", "B0_基线票据.md"],
     "criteria": ["python scripts/v3_gate.py --json reports/gate.json 返回 32/32 且 A1=25/47/9",
                  "python -m unittest discover -s tests 返回 34 OK",
                  "cd integrative-rehab-vsa && python main.py 返回 21/21",
                  "fusion_lock.json 含 12 个键且两侧脚本都能读"],
     "rollback": "只读批次，无需回滚", "hours": 0.5,
     "risks": ["控制台中文乱码导致票据字符错位 → 先设 UTF-8 再跑"],
     "not_touching": ["所有源码", "PACK_ORDER", "ivsa 自检"]},

    {"id": "B1a", "title": "契约字段草案", "owner": "P2 筑基", "inputs": ["B0_基线票据.md"],
     "actions": ["列出 6 个必填字段与 4 个可选字段", "给每个字段写类型与一个真实示例",
                 "写清 mechanism 枚举与 lane 取值"],
     "outputs": ["contract_v1_draft.md"],
     "criteria": ["字段总数 10 且必填 6", "每个字段都有类型与示例",
                  "contract.validate(样例) 返回 ok=true"],
     "rollback": "删除草案文件", "hours": 0.5,
     "risks": ["字段名与 ivsa 回执字段撞名 → 统一加 ct_ 前缀"],
     "not_touching": ["两仓代码", "既有回执格式"]},

    {"id": "B1b", "title": "同参指纹互认", "owner": "P2 筑基", "inputs": ["contract_v1_draft.md"],
     "actions": ["把草案固化为 contract_v1.json", "跑同参指纹互认：768 维与 decay 0.99 两侧一致",
                 "补 6 项契约单测"],
     "outputs": ["contract_v1.json", "tests/test_fusion_contract.py"],
     "criteria": ["契约单测 6 项全 OK", "768 维/α0.18/decay0.99 三项同参断言通过",
                  "contract.make() 产出的 contract_id 两次相同"],
     "rollback": "删除 contract_v1.json 与对应测试", "hours": 1,
     "risks": ["把同参当成同编号 → 映射表禁止算术推导"],
     "not_touching": ["六机制引擎", "编号空间"]},

    {"id": "B2a", "title": "六机制 1:1 映射表", "owner": "P3 构弦", "inputs": ["contract_v1.json"],
     "actions": ["为六机制各写一行：同参/差异/桥接规则", "把每行 bridge 写成一句可执行约束",
                 "跑 pairs() 断言六行且顺序固定"],
     "outputs": ["mechanism_map.json"],
     "criteria": ["映射表 6 行且 mechanism 顺序与枚举一致", "每行都有 same/diff/bridge 三段",
                  "pairs() digest 两次一致"],
     "rollback": "回退映射表文件", "hours": 0.5,
     "risks": ["把 70 体当成 1229 技能 → 映射表显式写主体数差异"],
     "not_touching": ["两套引擎实现", "A1 锁值"]},

    {"id": "B2b", "title": "12→17 通道映射 + 词表分域", "owner": "P4 持衡", "inputs": ["mechanism_map.json"],
     "actions": ["写 12 行 LC 显式分组映射", "登记 5 个未映射目标为待办",
                 "把医学 24E14+12E13 从通用闸剥离，改为按域注入"],
     "outputs": ["channel_map.csv", "词表分域规则.md"],
     "criteria": ["channel_map 12 行且分组合计 17", "通用闸词表仍为 10 token，不含 E13/E14",
                  "pending=5 且逐条列名"],
     "rollback": "回退映射与分域规则", "hours": 1,
     "risks": ["用 idx%17 推通道 → 映射表禁用取模，写死行"],
     "not_touching": ["通用闸 10 token", "ivsa 皮肤 36 条规则"]},

    {"id": "B3", "title": "用途二次分类", "owner": "P1 探微", "inputs": ["索引 1229"],
     "actions": ["对 1229 条逐条跑 dispatch 打分", "按 K/M/T/X 落值并保留待判",
                 "抽 40 条人工复核"],
     "outputs": ["用途四标签.csv", "抽样复核表.md"],
     "criteria": ["1229 行全有标签值", "抽样 40 条复核通过率 100%",
                  "待判条数 ≤20"],
     "rollback": "重跑即可，纯派生物", "hours": 2,
     "risks": ["X 类 15 条被硬塞进 K → 明确不纳入并留痕"],
     "not_touching": ["索引 digest", "机制轴口径"]},

    {"id": "B4", "title": "康复域试点 20 例", "owner": "P1 探微", "inputs": ["B2a", "B3"],
     "actions": ["选 20 条康复相关请求", "走 发现→契约→映射→只读回执 全链路",
                 "逐条核对回执带 simulated 与 evidence_class"],
     "outputs": ["试点20例_票据.md", "20 条契约回执"],
     "criteria": ["20/20 回执 mode=simulated", "20/20 回执含 evidence_class",
                  "试点后双仓七道闸仍全绿"],
     "rollback": "关桥开关即回滚", "hours": 2,
     "risks": ["回执写进临床结论 → 回执只允许写计算假设"],
     "not_touching": ["ivsa 医学红线", "E14 急症熔断"]},

    {"id": "B5", "title": "语义技能族扩容", "owner": "P3 构弦", "inputs": ["B3 K 类"],
     "actions": ["按十模块逐模块挑候选技能", "把语义技能从 19 扩到 ≥60",
                 "断言没有第十一模块"],
     "outputs": ["语义技能≥60.csv", "十模块覆盖表.md"],
     "criteria": ["语义技能计数 ≥60", "十模块每模块 ≥1 个技能",
                  "模块数断言恰为 10"],
     "rollback": "撤销新增归属", "hours": 2,
     "risks": ["为凑数量把无关技能塞进语义 → 每条须有模块归属理由"],
     "not_touching": ["引擎", "十模块定义"]},

    {"id": "B6", "title": "记忆与流量", "owner": "P2 筑基", "inputs": ["B4 回执"],
     "actions": ["赫布权重落盘为 JSON", "加重启一致测试：同查询 top-k 逐字相等",
                 "生成 12 通道负载表并对齐 17 通道配额"],
     "outputs": ["data/hebbian_field.json", "通道负载表.csv"],
     "criteria": ["重启前后 top-k 逐字相等", "落盘文件两次生成字节一致",
                  "负载表 12 行且与 17 通道配额表逐行对应"],
     "rollback": "删落盘文件回初始空场", "hours": 2,
     "risks": ["浮点写入顺序导致字节漂移 → 固定键序与精度"],
     "not_touching": ["decay 0.99", "经络 17 通道定义"]},

    {"id": "B7", "title": "分批准入", "owner": "P4 持衡", "inputs": ["B4", "B5", "B6"],
     "actions": ["每批最多 5 个技能过四道硬闸", "过闸后等人工签字", "累计入执行层不超过 15 个"],
     "outputs": ["准入票据_B7-N.md"],
     "criteria": ["每批 4 道硬闸全绿", "每批有签字人姓名与日期", "累计准入 ≤15"],
     "rollback": "撤销准入即回退到发现层", "hours": 0.5,
     "risks": ["无人签字就放行 → 票据缺签字即作废"],
     "not_touching": ["A1 锁值", "ivsa 21 组自检"]},

    {"id": "B8", "title": "双仓开源同步", "owner": "P3 构弦", "inputs": ["全链"],
     "actions": ["ivsa v1.2 做可选插件并默认关闭", "双仓各生成 SHA256SUMS",
                 "核对 MIT 与 MPL-2.0 分层无冲突"],
     "outputs": ["ivsa_v1.2_plugin.md", "双仓 SHA256SUMS"],
     "criteria": ["插件默认关闭且不装也能跑 21/21", "两仓 SHA256SUMS 互认可复算",
                  "许可分层清单无混用条目"],
     "rollback": "插件保持默认关闭即安全", "hours": 2,
     "risks": ["把 MPL 代码拷进 MIT 仓 → 只经契约交换，不拷文件"],
     "not_touching": ["两仓 LICENSE", "版本号"]},

    {"id": "B9", "title": "V2 收口", "owner": "四透镜合议", "inputs": ["全链"],
     "actions": ["补齐五份交付物", "逐批核对九字段是否写满",
                 "把判据逐条跑一遍"],
     "outputs": ["融合总策划_v2.md", "批次台账_v2.csv", "完美融合判据.md",
                 "风险与回滚登记.md", "四透镜评审意见.md"],
     "criteria": ["五份文件齐且路径可访问", "十二批九字段无一空格",
                  "每条判据都能贴命令复跑", "判据内无形容词"],
     "rollback": "回退到 V1.0 八批策划", "hours": 1,
     "risks": ["收口时临时加批 → 收口批只准删改，不准新增批次"],
     "not_touching": ["已完成批次的判据", "锁值"]},
]


def summary() -> Dict[str, Any]:
    hours = round(sum(b["hours"] for b in BATCHES), 2)
    return {"version": "V2.0", "batches": len(BATCHES), "total_hours": hours,
            "ids": [b["id"] for b in BATCHES],
            "by_owner": {owner: sum(1 for b in BATCHES if b["owner"] == owner)
                         for owner in sorted({b["owner"] for b in BATCHES})},
            "digest": digest_of([{"id": b["id"], "title": b["title"], "h": b["hours"]}
                                 for b in BATCHES])}


def get(batch_id: str = "") -> Dict[str, Any]:
    if not batch_id:
        return summary()
    for b in BATCHES:
        if b["id"].lower() == batch_id.lower():
            return dict(b)
    return {"error": "未知批次", "id": batch_id, "known": [b["id"] for b in BATCHES]}


def validate() -> Dict[str, Any]:
    problems: List[Dict[str, Any]] = []
    for b in BATCHES:
        missing = [f for f in FIELDS if not b.get(f)]
        if missing:
            problems.append({"id": b["id"], "kind": "missing_field", "detail": missing})
        crit = b.get("criteria", [])
        if len(crit) < 3:
            problems.append({"id": b["id"], "kind": "criteria_too_few", "detail": len(crit)})
        for c in crit:
            hit = [w for w in FORBIDDEN_WORDS if w in c]
            if hit:
                problems.append({"id": b["id"], "kind": "adjective_criterion", "detail": hit})
        if not b.get("rollback"):
            problems.append({"id": b["id"], "kind": "no_rollback"})
    return {"ok": not problems, "batches": len(BATCHES),
            "problems": problems, "fields_per_batch": len(FIELDS),
            "digest": summary()["digest"]}
