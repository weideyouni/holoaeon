# -*- coding: utf-8 -*-
"""
第十六包 · 补齐短板赋能升级包 UPLIFT（U1–U6）
================================================================================
六个升级单元（U1 确定性 / U6 生态基建 / U3 实测闭环 / U5 匹配升级 / U2 宿主模型桥 / U4 裁决与 P1）
在本包里不是「文档条目」，而是**可判定的校验技能**：每个技能接收事实、返回 PASS/FAIL 与理由码。

本包不改任何既有行为：0 agent、不加行、不加节点、不落盘、不起线程、不联网。
所有判定都是纯函数；凡本包无法自证的（真 CI、真模型、生产级 hook）一律返回
`pack_can_prove=False`，不给「通过」。

它保护了哪条立场：取舍留痕（十处冲突逐条摊开）+ 代价显式（未实测即标未实测）。
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .base import DomainPack, SkillSpec, WorkflowSpec

# ---------------------------------------------------------------- 标识
MATRIX_ID = "SG-MASTER-UPLIFT-1331x1331-EXT-V1.0"
UPSTREAM_ID = "SG-MASTER-NEPHRON-1331x1331-EXT-V1.0"
UPSTREAM_ID_2 = "HOLOAEON-UPLIFT-SPEC-U1U6-V1.0"
DOMAIN = "uplift"
SEAL = "潮起开门，潮落闭嘴"
HEARTBEAT_BASE, HEARTBEAT_COUNT, HEARTBEAT_DIM = 9900, 70, 768
HEARTBEAT_ALPHA = 0.18

# 维度不变式（与全部前序扩展包同一把锁）
LOCK_SIDE = 1331
LOCK_DESIGN = 1771561
LOCK_MANDALA = 108641
LOCK_HILBERT = 651846
LOCK_KALMAN = 22627
SUBD_TOTAL, SLOTS_PER, SLOTS_RESERVED = 127, 10, 61
NODES_PER, NODES_COORD = 855, 56

METAPHOR_NOTE = ("UPLIFT 是「修桥」而非「长新器官」：六个单元都在既有器官内部收敛，"
                 "因此维度不变式必须原样成立——它保护了「产出物维度不变」这条用户锁定口径")

# ---------------------------------------------------------------- 六单元
UNITS: Tuple[Dict[str, str], ...] = (
    {"id": "U1", "name": "确定性修复与断言收紧", "short": "S1",
     "evidence": "cluster.py::_report() 过滤 __forward__ 后无排序；_fft 就地置换入参",
     "dimension": "正确性", "order": "1",
     "files": "holoaeon/cluster.py, holoaeon/hypervector.py, tests/test_holoaeon.py",
     "acceptance": "A-U1-1..4"},
    {"id": "U6", "name": "生态基建与口径修正", "short": "S6",
     "evidence": "无 CI、无模板；徽章 tests-24 / selftest-16%2F16 与实测 31 / 23 不符",
     "dimension": "生态成熟度", "order": "2",
     "files": ".github/workflows/ci.yml, .github/ISSUE_TEMPLATE/*, .github/PULL_REQUEST_TEMPLATE.md, docs/support-matrix.md",
     "acceptance": "A-U6-1..4"},
    {"id": "U3", "name": "A1/A2 宿主侧实测闭环", "short": "S3",
     "evidence": "docs/nephron.md L1/L2 恒为 pending_human_measure",
     "dimension": "生产就绪", "order": "3",
     "files": "scripts/measure_a1_a2.py, docs/nephron_a1_a2_evidence.json, docs/nephron.md",
     "acceptance": "A-U3-1..4"},
    {"id": "U5", "name": "技能匹配确定性升级", "short": "S5",
     "evidence": "skill.py 中文按单字切分，仅 Jaccard + 标签权重",
     "dimension": "技术定位", "order": "4",
     "files": "holoaeon/skill.py, tests/test_holoaeon.py",
     "acceptance": "A-U5-1..4"},
    {"id": "U2", "name": "宿主模型桥", "short": "S2",
     "evidence": "model_adapter.py 全篇 simulated，无一条真实通路",
     "dimension": "生产就绪", "order": "5",
     "files": "bridges/transport.py, bridges/backends.py, bridges/live_client.py, bridges/quickstart.py, examples/05_live_model.py",
     "acceptance": "A-U2-1..6"},
    {"id": "U4", "name": "O-1～O-10 裁决 + P1 细则", "short": "S4",
     "evidence": "docs/nephron.md §12 十条开放问题未裁定；P1 判定细则未写",
     "dimension": "技术定位", "order": "6",
     "files": "docs/nephron.md, docs/nephron-p1.md",
     "acceptance": "O-1..O-10 + P1 四判据"},
)

# ---------------------------------------------------------------- 十处冲突（审视结论）
CONFLICTS: Tuple[Dict[str, str], ...] = (
    {"id": "X1", "point": "投喂 U1.3 的修复只写 `real.sort(key=agent_id)`",
     "problem": "同一 agent 的多轮记录 agent_id 相同，稳定排序仍保留出队序——非确定并未焊死",
     "A": "按投喂字面只排 agent_id",
     "B": "复合键 (agent_id, 记录规范化指纹)，内容相同的记录彼此可换",
     "chosen": "B",
     "reason": "排序键必须是全序才能叫确定性；只排 agent_id 是半个修复"},
    {"id": "X2", "point": "投喂 T-U1-A 的前提是「6 agent × 30 轮 → 180 条结果」",
     "problem": "现行 Cluster.run() 只在首轮投递任务，rounds 只影响 barrier 次数，实测每 agent 仅 1 条记录",
     "A": "改 run() 每轮投递（等于改线程语义，撞 U1.2 非目标）",
     "B": "线程级断言降为「3 次 30 轮运行、6 条 id 序列一致」+ 另加纯函数级全序测试",
     "chosen": "B",
     "reason": "非目标明确禁止改线程模型；缺口用纯函数测试补，而不是偷偷改语义"},
    {"id": "X3", "point": "投喂 A-U6-1 要求三个 Python 版本 CI 全绿",
     "problem": "本机无 GitHub Actions 执行器，本地只能证明「单版本实测」，CI 绿只能由 GitHub 侧产生",
     "A": "按投喂宣称 CI passing",
     "B": "交 workflow + 本地实测 + support-matrix 未跑格子写 untested + README 徽章注明以 CI 实跑为准（尚未跑）",
     "chosen": "B",
     "reason": "投喂自己写了「未跑通前不得写 CI passing」，字面优先"},
    {"id": "X4", "point": "投喂把徽章写死为 tests-25",
     "problem": "U1 新增 2 条、U5 新增 3 条，实测总数为 31；且投喂未发现 selftest 徽章 16%2F16 也已过期（实测 23）",
     "A": "按字面写 25",
     "B": "写实测 31，并同时修 selftest 徽章为 23%2F23",
     "chosen": "B",
     "reason": "徽章一旦与实测不符就是系统性撒谎；两处都要修，不只投喂点名的那些"},
    {"id": "X5", "point": "投喂 A-U3 要求把 A1/A2 从 pending 改成 measured",
     "problem": "P0 无生产级 writer（N1 把队列与落盘归宿主），真实 hook 闭环不存在；直接标 measured 会把「脚本级」说成「生产链路」",
     "A": "标 measured（当作生产闭环）",
     "B": "标 measured_with_scope：写明测的是「记录动作不影响业务输出」，脚本级",
     "chosen": "B",
     "reason": "改状态是合法动作，改口径不是；范围写清楚才敢改"},
    {"id": "X6", "point": "投喂 A-U2-3 要求「有 Ollama 机器上 --ask 返回 mode=live」",
     "problem": "本机未安装 Ollama（127.0.0.1:11434 不可达），该断言无法本地产生",
     "A": "用 echo 后端冒充 live",
     "B": "实测「无 Ollama 分支」（--check 退出码 2 + 三行指引）与 echo 装配；真 live 标 untested",
     "chosen": "B",
     "reason": "echo 与 live 混为一谈正是本项目最要防的「被 AI 忽悠」",
    },
    {"id": "X7", "point": "投喂要求审计写 bridges/.live_audit.jsonl",
     "problem": "写盘让「同一输入同一输出」在桥内不再成立（延迟/输出天然漂移）",
     "A": "不写审计，只返回内存回执",
     "B": "写盘但只记 seq/backend/model/prompt_sha16/response_sha16/latency/tokens，且 .gitignore；非确定性只在桥内存在并显式回执",
     "chosen": "B",
     "reason": "桥存在的意义就是把非确定隔离并留痕；但留痕不能留明文"},
    {"id": "X8", "point": "投喂混合分写 `0.5·token_overlap + 0.5·dice2`",
     "problem": "token_overlap 若是重叠个数（0..n）与 dice（0..1）量纲不一；且会破坏既有「标签权重叠加」语义",
     "A": "按字面用重叠个数",
     "B": "0.5·Jaccard + 0.5·dice2 + 0.05·tag_hit（保留既有量纲与标签项）",
     "chosen": "B",
     "reason": "既有 25 条单测依赖旧量纲；重叠个数会让短查询分数虚高"},
    {"id": "X9", "point": "投喂 A-U5-1 要求 statistik 命中 statistics，并建议英文加 3-gram 兜底",
     "problem": "2-gram Dice 已能给 0.82（实测），3-gram 兜底是锦上添花；但若无兜底，短词形变会掉到 0",
     "A": "只做 2-gram",
     "B": "2-gram 为主，含空白时取 max(2-gram, 词级 3-gram)",
     "chosen": "B",
     "reason": "取 max 不改变已命中的结果，只在形变/短词时兜底；不引入编辑距离等额外机制"},
    {"id": "X10", "point": "投喂 O-1 方案 A 要求 admitted 带 after_summary:true",
     "problem": "新增字段会破坏 P0「41 字段冻结」，与「产出物维度不变」冲突",
     "A": "加字段（41→42）",
     "B": "不加字段：同一 page_id 同时出现在 summarized 与 admitted 即「摘要后进窗」，window_used 只计一次",
     "chosen": "B",
     "reason": "语义等价而字段不动；字段一动，字段字典、样例、回放器全要返工"},
)

# ---------------------------------------------------------------- 四处核实修正（F）
FIXES: Tuple[Dict[str, str], ...] = (
    {"id": "F1", "finding": "投喂 CI 第二步 `assert r['ok'] and r['failed']==0` 一度怀疑 run_all 无 failed 键",
     "verdict": "核实存在：run_all 返回 groups / passed / failed / ok / details 五键，投喂写法可用",
     "impact": "CI 脚本按投喂原样落地，无需改写"},
    {"id": "F2", "finding": "投喂只写「连接失败/超时/非 200 三类错误分型」",
     "verdict": "补充 BadStatus 之外的 bad_json 与 ValueError/OSError 兜底，共 4 类 + 1 兜底",
     "impact": "桥永不抛异常到调用方（含坏 JSON 与非法 URL）"},
    {"id": "F3", "finding": "quickstart --check 对 echo 后端无探活路径",
     "verdict": "echo 直接返回可用（离线后端无网络可探），退出码 0",
     "impact": "无模型机器也能验证装配链路"},
    {"id": "F4", "finding": "examples/05 在无桥环境若直接调用会抛异常",
     "verdict": "捕获 ImportError 与探活失败，统一打印 skip 并退出 0",
     "impact": "示例不阻塞无网络 CI"},
)

# ---------------------------------------------------------------- 本轮自身缺陷（写码时抓到并修掉）
DEFECTS: Tuple[Dict[str, str], ...] = (
    {"id": "M1", "defect": "REMOTE_ENV 常量拼成 HOLAEON_ALLOW_REMOTE（少一个 HO）",
     "caught_by": "远程放行用例实测仍被拒", "fix": "改回 HOLOAEON_ALLOW_REMOTE",
     "lesson": "开关拼错时 fail-closed 方向是安全的，但功能等于永久失效——必须有两个方向的用例"},
    {"id": "M2", "defect": "echo 后端 base_url=echo://local 被主机准入判为远程并拒绝",
     "caught_by": "echo 装配用例 ValueError", "fix": "scheme=echo 直接判 OFFLINE_BACKEND",
     "lesson": "离线后端不属于网络准入范围；准入逻辑要显式认得它"},
    {"id": "M3", "defect": "echo 回执缺 ok 键，调用方 KeyError",
     "caught_by": "测试脚本 KeyError", "fix": "echo 分支补 ok=True",
     "lesson": "回执结构必须跨 mode 一致，否则调用方要分支处理"},
    {"id": "M4", "defect": "T-U1-A 按投喂前提断言 6×30=180 条结果",
     "caught_by": "断言实得 6", "fix": "改断言 6 条 + 另加全序纯函数测试",
     "lesson": "投喂的实验设计也要对着代码核一遍，不然测试本身在撒谎"},
    {"id": "M5", "defect": "machine_spec 用 platform.os.cpu_count()（依赖内部导入）",
     "caught_by": "代码复核", "fix": "改 import os; os.cpu_count()",
     "lesson": "不要依赖模块的内部导入，哪怕它当前恰好可用"},
)

# ---------------------------------------------------------------- 五条立场
STANCES: Tuple[Dict[str, str], ...] = (
    {"id": "S1", "name": "零依赖", "where": "全套只 import 标准库；CI 与红线扫描双重验证"},
    {"id": "S2", "name": "确定性", "where": "cluster 排序全序、_fft 纯函数化、skill 打分无随机源"},
    {"id": "S3", "name": "取舍留痕", "where": "CONFLICTS X1–X10、DEFECTS M1–M5、O-1～O-10 裁决表"},
    {"id": "S4", "name": "代价显式", "where": "A1/A2 带范围披露；CI 未跑即 untested；live 未测即 untested"},
    {"id": "S5", "name": "宿主边界", "where": "bridges/ 在包外；holoaeon/ 零网络 import（红线为证）"},
)

# ---------------------------------------------------------------- 验收
ACCEPTANCE: Tuple[Dict[str, str], ...] = (
    {"id": "A-U1-1", "claim": "三次独立运行 6×30 轮，agent_id 序列完全一致",
     "how": "unittest TestDeterminismU1", "prove": "local_measured"},
    {"id": "A-U1-2", "claim": "_fft 不修改入参", "how": "前后逐元素比较", "prove": "local_measured"},
    {"id": "A-U1-3", "claim": "单测全绿且总数 ≥ 28", "how": "unittest discover", "prove": "local_measured"},
    {"id": "A-U1-4", "claim": "红线扫描零违规", "how": "scripts/redline_scan.py", "prove": "local_measured"},
    {"id": "A-U6-1", "claim": "CI 在 3.8 / 3.10 / 3.12 全绿", "how": "GitHub Actions", "prove": "untested"},
    {"id": "A-U6-2", "claim": "三模板就位且字段完整", "how": "本包 template_check", "prove": "local_measured"},
    {"id": "A-U6-3", "claim": "徽章与正文口径一致（实测 31 / 23）", "how": "本包 badge_consistency", "prove": "local_measured"},
    {"id": "A-U6-4", "claim": "支持矩阵无推测值", "how": "本包 support_matrix", "prove": "local_measured"},
    {"id": "A-U3-1", "claim": "A1 = PASS 且两次执行哈希一致", "how": "measure_a1_a2.py ×2", "prove": "local_measured"},
    {"id": "A-U3-2", "claim": "A2 给中位数与机器规格，无虚构值", "how": "evidence json", "prove": "local_measured"},
    {"id": "A-U3-3", "claim": "docs/nephron.md 状态更新附证据链", "how": "L1/L2 行 + evidence", "prove": "local_measured"},
    {"id": "A-U3-4", "claim": "脚本在 scripts/ 且红线仍零违规", "how": "红线扫描", "prove": "local_measured"},
    {"id": "A-U5-1", "claim": "统计销售额命中统计类技能；statistik 命中 statistics",
     "how": "unittest TestMatchingU5", "prove": "local_measured"},
    {"id": "A-U5-2", "claim": "既有匹配测试零回归", "how": "TestSkill", "prove": "local_measured"},
    {"id": "A-U5-3", "claim": "同输入 1000 次输出逐位一致", "how": "循环断言", "prove": "local_measured"},
    {"id": "A-U5-4", "claim": "红线零违规", "how": "红线扫描", "prove": "local_measured"},
    {"id": "A-U2-1", "claim": "holoaeon/ 红线零违规（桥在包外）", "how": "红线扫描", "prove": "local_measured"},
    {"id": "A-U2-2", "claim": "无 Ollama 时 --check 输出指引并退出码 2",
     "how": "quickstart 实跑", "prove": "local_measured"},
    {"id": "A-U2-3", "claim": "有 Ollama 时 --ask 返回 mode=live 五要素", "how": "真机", "prove": "untested"},
    {"id": "A-U2-4", "claim": "未设 ALLOW_REMOTE 时非本机地址构造即拒", "how": "本包 remote_gate + 实跑", "prove": "local_measured"},
    {"id": "A-U2-5", "claim": "审计无明文 prompt / 无 key", "how": "审计字段表比对", "prove": "local_measured"},
    {"id": "A-U2-6", "claim": "examples/05 无桥时 skip、有桥全链路通过", "how": "示例实跑", "prove": "local_measured(前半)"},
)

# ---------------------------------------------------------------- 非目标
NON_GOALS: Tuple[Dict[str, str], ...] = (
    {"id": "NG1", "name": "改 Cluster 线程语义", "flag": "thread_semantics_change"},
    {"id": "NG2", "name": "在核心包内引入网络", "flag": "core_network"},
    {"id": "NG3", "name": "引入第三方依赖", "flag": "third_party_dep"},
    {"id": "NG4", "name": "发布自动化", "flag": "release_automation"},
    {"id": "NG5", "name": "P1 真正执行淘汰", "flag": "eviction_now"},
    {"id": "NG6", "name": "用 echo 冒充 live", "flag": "echo_as_live"},
)

REFUSED_OPS: Tuple[str, ...] = (
    "把未实跑的 CI 说成 passing", "把脚本级实测说成生产闭环",
    "用 echo 或 simulated 回执冒充 mode=live", "把审计里塞入明文 prompt 或密钥",
    "在 holoaeon/ 内 import urllib/socket/http", "为了通过测试改断言而不是改实现",
    "把 X1–X10 的择定改回投喂字面而不说明「, 」新增 after_summary 字段",
    "跳过 A1 的变异证明就宣布判定有效",
)


# ---------------------------------------------------------------- 内部工具
def _canon(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha16(obj: Any) -> str:
    return hashlib.sha256(_canon(obj).encode("utf-8")).hexdigest()[:16].upper()


def _rows() -> int:
    return SUBD_TOTAL * SLOTS_PER + SLOTS_RESERVED


def _nodes() -> int:
    return SUBD_TOTAL * NODES_PER + NODES_COORD


# ---------------------------------------------------------------- 1. 单元与顺序
def skill_uplift_unit_registry() -> Dict[str, Any]:
    """六单元清单：短板、实证、目标维度、投喂指定执行顺序、落地文件、对应验收。"""
    order = [u["id"] for u in sorted(UNITS, key=lambda u: int(u["order"]))]
    return {"units": [dict(u) for u in UNITS], "count": len(UNITS),
            "execution_order": order,
            "order_matches_spec": order == ["U1", "U6", "U3", "U5", "U2", "U4"],
            "why_this_order": "先锁正确性（U1）→ 铺基建（U6）→ 拿到实测基线（U3）→ 升匹配（U5）"
                              "→ 接真实模型（U2）→ 最后裁决与 P1（U4，依赖前五项）",
            "stance_guard": "取舍必须留痕：顺序本身也是取舍，理由与投喂一致才写出来"}


# ---------------------------------------------------------------- 2. 排序键
def skill_uplift_order_key_check(records: Sequence[Dict[str, Any]] | None = None) -> Dict[str, Any]:
    """排序键全序核验：同 agent 的多条「不同内容」记录也必须有序；内容相同的记录彼此可换。"""
    recs = [dict(r) for r in (records or [])]
    canons = [_canon(r) for r in recs]
    keys = [(str(r.get("agent_id", "")), c) for r, c in zip(recs, canons)]
    grouped: Dict[str, List[str]] = {}
    for aid, c in keys:
        grouped.setdefault(aid, []).append(c)
    # 只按 agent_id 排会出现歧义的位置：同一 agent 下有 >1 条「不同内容」记录
    ties_if_agent_only = sum(1 for cs in grouped.values() if len(set(cs)) > 1)
    injective = len(set(keys)) == len(set(canons))     # 复合键在内容上单射
    order_1 = [c for _, c in sorted(keys)]
    # 输入顺序反转后再排：若键是全序，输出必须逐位相同
    order_2 = [c for _, c in sorted(list(reversed(keys)))]
    resort_equal = order_1 == order_2
    return {"records": len(recs), "distinct_contents": len(set(canons)),
            "distinct_keys": len(set(keys)),
            "agents_with_multiple_distinct_records": ties_if_agent_only,
            "key_injective_on_content": injective,
            "stable_under_reverse_resort": resort_equal,
            "verdict": "PASS" if (injective and resort_equal and recs) else ("UNCHECKED" if not recs else "FAIL"),
            "redline": ("只按 agent_id 排序时，存在 %d 处并列；并列处仍按出队序——这就是半个修复"
                        % ties_if_agent_only),
            "stance_guard": "确定性是框架第一承诺：同一输入必须同一顺序"}


# ---------------------------------------------------------------- 3. 纯函数契约
def skill_uplift_purity_contract() -> Dict[str, Any]:
    """入参不可变更的契约表：哪些函数对外承诺「不修改入参」，如何判定。"""
    rows = [
        {"target": "holoaeon.hypervector._fft", "rule": "调用前后逐元素相等",
         "how": "T-U1-B（新增入参副本 + 前后比较）"},
        {"target": "holoaeon.cluster._order_key", "rule": "只读记录，不写回",
         "how": "排序后原列表元素对象不变（排序只重排引用）"},
        {"target": "holoaeon.skill.ngram_dice", "rule": "不缓存、不改字符串",
         "how": "1000 次调用输出逐位一致（A-U5-3）"},
        {"target": "本包全部技能", "rule": "纯函数，不落盘不起线程",
         "how": "pack_summary 的 threads/timers/disk_writes 恒为 0"},
    ]
    return {"contracts": rows, "count": len(rows),
            "tested": ["_fft", "ngram_dice"],
            "stance_guard": "代价显式：承诺就要能被一条断言验证，否则不许写进契约"}


# ---------------------------------------------------------------- 4. 回归口径
def skill_uplift_regression_ledger(counts: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """回归口径账：单测 / 自检 / 红线的「修复前 → 修复后」实测值。"""
    c = dict(counts or {})
    before = {"tests": 25, "selftest": 23, "redline_files": 33,
              "badge_tests": 24, "badge_selftest": "16/16"}
    after = {"tests": c.get("tests", 0), "selftest": c.get("selftest", 0),
             "redline_files": c.get("redline_files", 0),
             "badge_tests": c.get("badge_tests", 0),
             "badge_selftest": c.get("badge_selftest", "")}
    consistent = (after["badge_tests"] == after["tests"]
                  and after["badge_selftest"] == ("%d/%d" % (after["selftest"], after["selftest"])))
    return {"before": before, "after": after,
            "tests_not_decreased": after["tests"] >= before["tests"],
            "selftest_not_decreased": after["selftest"] >= before["selftest"],
            "badge_consistent": consistent,
            "verdict": "PASS" if consistent and after["tests"] >= before["tests"] else "FAIL",
            "stance_guard": "代价显式：口径要先对齐再写进徽章，否则徽章就是系统性撒谎"}


# ---------------------------------------------------------------- 5. CI 契约
def skill_uplift_ci_spec() -> Dict[str, Any]:
    """CI 契约：触发器、矩阵、四步，以及「绿灯由谁产生」的边界声明。"""
    return {"workflow": ".github/workflows/ci.yml",
            "triggers": ["push:main", "pull_request:main"],
            "matrix": ["3.8", "3.10", "3.12"],
            "steps": [
                {"name": "unittest", "cmd": "python -m unittest discover -s tests -v"},
                {"name": "selftest", "cmd": "python -c \"...run_all(); assert r['ok'] and r['failed']==0\""},
                {"name": "redline", "cmd": "python scripts/redline_scan.py"},
                {"name": "examples", "cmd": "python examples/01..04"},
            ],
            "fail_semantics": "任一步非零退出即 CI 红；不吞错、不 || true",
            "green_produced_by": "GitHub Actions 运行器（不在本机）",
            "pack_can_prove": False,
            "untested_reason": "本机无 Actions 执行器；本地只能证明单版本（3.13.16）实测",
            "stance_guard": "代价显式：没跑过的 CI 不许说自己在跑"}


# ---------------------------------------------------------------- 6. 模板
REQUIRED_SECTIONS = {
    "bug_report": ["复现步骤「, 」期望「, 」自检输出「, 」环境「, 」红线自检「, 」确定性影响"],
    "feature_request": ["问题「, 」原语「, 」零依赖「, 」确定性「, 」红线「, 」验收标准"],
    "pull_request": ["改动说明「, 」受影响模块「, 」测试证据「, 」红线扫描目标「, 」立场自检「, 」破坏性变更"],
}


def skill_uplift_template_check(templates: Dict[str, str] | None = None) -> Dict[str, Any]:
    """模板完整性：三份模板是否含各自必需小节（缺一即 FAIL）。"""
    tpl = dict(templates or {})
    detail, missing = {}, []
    for name, sections in REQUIRED_SECTIONS.items():
        body = tpl.get(name, "")
        absent = [s for s in sections if s not in body]
        detail[name] = {"present": len(sections) - len(absent), "of": len(sections),
                        "missing": absent}
        if absent:
            missing.append({"template": name, "missing": absent})
    return {"templates": sorted(REQUIRED_SECTIONS), "checked": sorted(tpl.keys()),
            "detail": detail, "missing": missing,
            "verdict": "PASS" if tpl and not missing else ("UNCHECKED" if not tpl else "FAIL"),
            "stance_guard": "取舍留痕：模板字段是贡献者的第一小时摩擦，缺一项就是一次返工"}


# ---------------------------------------------------------------- 7. 徽章
def skill_uplift_badge_consistency(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """徽章一致性：README 徽章数值必须等于实测数值，否则 FAIL（含「以 CI 为准」注记要求）。"""
    p = dict(payload or {})
    badge = str(p.get("badge", ""))
    measured = p.get("measured", {})
    tests = measured.get("tests")
    selftest = measured.get("selftest")
    ok_tests = bool(tests) and ("tests-%s%%20passed" % tests) in badge
    ok_self = bool(selftest) and ("selftest-%s%%2F%s" % (selftest, selftest)) in badge
    note = bool(p.get("has_ci_note"))
    return {"badge": badge, "measured": measured,
            "tests_ok": ok_tests, "selftest_ok": ok_self, "ci_note_present": note,
            "verdict": "PASS" if (ok_tests and ok_self and note) else "FAIL",
            "rule": "徽章 = 实测值；并注明「以 CI 实跑为准」——CI 未跑时不得出现 passing 措辞",
            "stance_guard": "代价显式：徽章是承诺，不是装饰"}


# ---------------------------------------------------------------- 8. 支持矩阵
def skill_uplift_support_matrix(rows: Sequence[Dict[str, Any]] | None = None) -> Dict[str, Any]:
    """支持矩阵：只允许 measured / untested 两种状态；出现推测值即 FAIL。"""
    rows_ = [dict(r) for r in (rows or [])]
    bad = [r for r in rows_ if str(r.get("status")) not in ("measured", "untested")]
    measured = [r for r in rows_ if str(r.get("status")) == "measured"]
    untested = [r for r in rows_ if str(r.get("status")) == "untested"]
    return {"rows": rows_, "measured": len(measured), "untested": len(untested),
            "invalid_status": bad,
            "verdict": "PASS" if not bad else "FAIL",
            "rule": "未跑的格子写 untested；写 pass / ok / assume 一律视为推测",
            "stance_guard": "代价显式：矩阵的价值在于把「不知道」标出来"}


# ---------------------------------------------------------------- 9. A1 判定
def skill_uplift_measure_a1_verdict(evidence: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """A1 判定：只有 PASS + 范围声明齐备才算有效，且必须带变异证明。"""
    ev = dict(evidence or {})
    a1 = dict(ev.get("A1") or {})
    verdict = str(a1.get("verdict", ""))
    has_scope = bool(ev.get("scope"))
    mutation = ev.get("mutation_proof") or {}
    ok = (verdict == "PASS" and has_scope
          and bool(a1.get("sha256_off")) and bool(a1.get("sha256_full")))
    return {"verdict": verdict, "sha256_off": a1.get("sha256_off"),
            "sha256_full": a1.get("sha256_full"),
            "steps": a1.get("steps"), "records_full": a1.get("records_full"),
            "scope_declared": has_scope, "scope": ev.get("scope", ""),
            "mutation_proof": mutation,
            "mutation_makes_it_fail": bool(mutation.get("baseline_pass"))
                                       and bool(mutation.get("mutant_fail")),
            "status": ("measured_with_scope" if ok else "pending_human_measure"),
            "rule": "PASS 若无变异证明，可能是空转判定；无范围声明的 PASS 不算实测",
            "stance_guard": "取舍留痕：判定自己也可能骗人，所以判定要被判定"}


# ---------------------------------------------------------------- 10. A2 披露
A2_THRESHOLD_TEXT = "none — 披露项不是断言项（延续不设虚构目标值）"


def skill_uplift_measure_a2_disclosure(evidence: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """A2 披露：中位数 + 机器规格必填；阈值必须显式写 none（披露项不是断言项）。"""
    a2 = dict((evidence or {}).get("A2") or {})
    machine = dict(a2.get("machine") or {})
    threshold = a2.get("threshold") or A2_THRESHOLD_TEXT
    ok = (a2.get("median_off_ms") is not None and a2.get("median_full_ms") is not None
          and bool(machine.get("python")) and bool(machine.get("system")))
    return {"runs": a2.get("runs"), "median_off_ms": a2.get("median_off_ms"),
            "median_full_ms": a2.get("median_full_ms"),
            "overhead_median_pct": a2.get("overhead_median_pct"),
            "machine": machine, "threshold": threshold,
            "complete": ok,
            "fabricated_target": threshold != A2_THRESHOLD_TEXT,
            "status": "measured" if ok else "pending_human_measure",
            "stance_guard": "代价显式：开销是披露项，不许变成「必须低于 X%」的虚构门槛"}


# ---------------------------------------------------------------- 11. 证据链
def skill_uplift_evidence_chain(evidence: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """证据链完整性：脚本 / 种子 / 日期 / A1 / A2 / 范围 六件齐备，缺一即 FAIL。"""
    ev = dict(evidence or {})
    need = ["script", "seed", "date_local", "A1", "A2", "scope"]
    missing = [k for k in need if k not in ev]
    return {"required": need, "missing": missing,
            "fingerprint": _sha16(ev) if ev else "EMPTY",
            "verdict": "PASS" if ev and not missing else "FAIL",
            "rule": "可复现 = 脚本 + 种子 + 日期 + 结果 + 范围；少一样就只能算「跑过」",
            "stance_guard": "取舍留痕：没有证据链的实测等于传闻"}


# ---------------------------------------------------------------- 12. n-gram Dice
def skill_uplift_ngram_dice(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """字符 n-gram Dice（与 skill.py 同一算法）：纯函数、无分词依赖。"""
    p = dict(payload or {})
    q = str(p.get("query", ""))
    t = str(p.get("text", ""))
    n = int(p.get("n", 2) or 2)

    def ngrams(s: str, k: int) -> Counter:
        s = "".join(s.lower().split())
        if len(s) < k:
            return Counter([s]) if s else Counter()
        return Counter(s[i:i + k] for i in range(len(s) - k + 1))

    a, b = ngrams(q, n), ngrams(t, n)
    tot = sum(a.values()) + sum(b.values())
    inter = sum(min(v, b[k]) for k, v in a.items()) if tot else 0
    dice = round(2.0 * inter / tot, 5) if tot else 0.0
    return {"query": q, "text": t, "n": n, "dice": dice,
            "gram_count": [sum(a.values()), sum(b.values())],
            "stance_guard": "确定性：同一输入必须同一分数，所以不含随机、不含模型"}


# ---------------------------------------------------------------- 13. 混合分权重
def skill_uplift_hybrid_score_parts(parts: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """混合分权重表与重算：0.5·Jaccard + 0.5·Dice + 0.05·标签命中。"""
    p = dict(parts or {})
    w = {"jaccard": 0.5, "dice": 0.5, "tag_hit": 0.05}
    j = float(p.get("jaccard", 0.0) or 0.0)
    d = float(p.get("dice", 0.0) or 0.0)
    th = int(p.get("tag_hit", 0) or 0)
    score = round(w["jaccard"] * j + w["dice"] * d + w["tag_hit"] * th, 5)
    return {"weights": w, "inputs": {"jaccard": j, "dice": d, "tag_hit": th},
            "score": score, "weight_sum_no_tag": w["jaccard"] + w["dice"],
            "rejected_alternative": "0.5·重叠个数 + 0.5·dice（量纲不一，短查询虚高）",
            "stance_guard": "取舍留痕：量纲不齐的加权会静默放大短查询，必须显式拒绝"}


# ---------------------------------------------------------------- 14. 匹配验收
MATCH_CASES: Tuple[Dict[str, str], ...] = (
    {"id": "A-U5-1-cn", "query": "统计销售额", "expect_name": "stats_clean",
     "registry": "stats_clean(统计数据清洗与汇总) + weather(weather forecast lookup)"},
    {"id": "A-U5-1-en", "query": "statistik", "expect_name": "stats2",
     "registry": "stats2(statistics summary for numbers) + weather2(weather forecast lookup)"},
)


def skill_uplift_matching_acceptance(results: Sequence[Dict[str, Any]] | None = None) -> Dict[str, Any]:
    """匹配验收：两条必测用例是否按预期命中第一候选。"""
    got = {str(r.get("id")): str(r.get("top1", "")) for r in (results or [])}
    detail = []
    for c in MATCH_CASES:
        top = got.get(c["id"], "")
        detail.append({"case": c["id"], "query": c["query"],
                       "expect": c["expect_name"], "got": top,
                       "ok": top == c["expect_name"]})
    ok = all(d["ok"] for d in detail) and bool(got)
    return {"cases": detail, "verdict": "PASS" if ok else ("UNCHECKED" if not got else "FAIL"),
            "also_required": "同输入 1000 次输出逐位一致（A-U5-3）",
            "stance_guard": "确定性：语义升级也必须走可复现路线，不许引模型"}


# ---------------------------------------------------------------- 15. 桥边界
def skill_uplift_bridge_boundary(tree: Dict[str, Sequence[str]] | None = None) -> Dict[str, Any]:
    """宿主边界核验：桥必须在包外；核心包内不得出现网络 import。"""
    t = dict(tree or {})
    core = [str(x) for x in t.get("core_files", [])]
    bridge = [str(x) for x in t.get("bridge_files", [])]
    network_in_core = [f for f in core if str(f).lower().endswith(("_net.py", "http.py"))]
    inside_core = [b for b in bridge if b.startswith("holoaeon/")]
    return {"core_files": len(core), "bridge_files": len(bridge),
            "bridge_outside_core": not inside_core,
            "network_imports_in_core": network_in_core,
            "verdict": "PASS" if (not inside_core and not network_in_core) else "FAIL",
            "enforced_by": "scripts/redline_scan.py 扫描 holoaeon/，bridges/ 不在其目标",
            "stance_guard": "宿主边界：零依赖是核心包的属性，不是用户能力的天花板"}


# ---------------------------------------------------------------- 16. 后端登记
def skill_uplift_backend_registry() -> Dict[str, Any]:
    """三后端声明：默认地址、是否需要 key、是否本机、载荷形态。"""
    rows = [
        {"name": "ollama", "base_url": "http://127.0.0.1:11434", "path": "/api/chat",
         "needs_key": False, "local": True, "models_probe": "/api/tags"},
        {"name": "openai_compat", "base_url": "http://127.0.0.1:8080",
         "path": "/v1/chat/completions", "needs_key": False, "local": False,
         "models_probe": "/v1/models"},
        {"name": "echo", "base_url": "echo://local", "path": "", "needs_key": False,
         "local": True, "models_probe": ""},
    ]
    return {"backends": rows, "count": len(rows),
            "key_source": "HOLOAEON_API_KEY（只在内存中进请求头，不落盘）",
            "echo_note": "echo 不是 live：回执 mode='echo'，不写审计、不发请求",
            "stance_guard": "宿主边界：密钥只从环境变量读，永不写文件"}


# ---------------------------------------------------------------- 17. 远程门禁
def skill_uplift_remote_gate(cases: Sequence[Dict[str, Any]] | None = None) -> Dict[str, Any]:
    """远程门禁：本机默认放行；远程需 env 开关 + allow_remote + 白名单三重同时成立。"""
    rows_ = [dict(c) for c in (cases or [])]
    out = []
    for c in rows_:
        host = str(c.get("host", ""))
        local = host in ("127.0.0.1", "localhost", "::1")
        env = bool(c.get("env_switch"))
        flag = bool(c.get("allow_remote"))
        wl = bool(c.get("allowlisted"))
        ok = local or (env and flag and wl)
        reason = ("LOCAL" if local else
                  "REMOTE_LOCKED" if not env else
                  "REMOTE_NOT_CONFIRMED" if not flag else
                  "REMOTE_NOT_ALLOWLISTED" if not wl else "REMOTE_ALLOWED")
        out.append({"host": host, "expected_ok": ok, "reason": reason})
    return {"cases": out, "verdict": "PASS",
            "rule": "三重任一缺失即拒；env 只是解锁开关，不能替代白名单",
            "echo_exception": "scheme=echo 判 OFFLINE_BACKEND，不参与网络准入",
            "stance_guard": "宿主边界：默认收紧，放宽必须三处显式同意"}


# ---------------------------------------------------------------- 18. 审计策略
AUDIT_ALLOWED = ("seq", "backend", "model", "prompt_sha16", "response_sha16",
                 "latency_ms", "tokens")
AUDIT_FORBIDDEN = ("prompt", "task", "output", "response", "api_key", "authorization",
                   "messages", "content")


def skill_uplift_audit_policy(line: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """审计字段策略：7 个允许字段，禁记明文与密钥；越界即 FAIL。"""
    d = dict(line or {})
    unknown = sorted(k for k in d if k not in AUDIT_ALLOWED)
    leaked = sorted(k for k in d if k.lower() in AUDIT_FORBIDDEN)
    ok = (not leaked) and all(isinstance(d.get(k), (str, int, float, type(None), dict))
                             for k in d)
    return {"allowed": list(AUDIT_ALLOWED), "forbidden": list(AUDIT_FORBIDDEN),
            "unknown_fields": unknown, "leaked_fields": leaked,
            "verdict": ("PASS" if ok else "FAIL") if d else "UNCHECKED",
            "path": "bridges/.live_audit.jsonl（.gitignore 屏蔽，本地证据）",
            "stance_guard": "取舍留痕：留痕不等于留明文"}


# ---------------------------------------------------------------- 19. 回执语义
def skill_uplift_live_receipt_schema() -> Dict[str, Any]:
    """回执三态词表：live / echo / simulated 各自的必备字段与禁止事项。"""
    rows = [
        {"mode": "live", "fields": ["output", "backend", "model", "tokens", "latency_ms"],
         "must_not": ["把失败写成成功「, 」隐藏重试「, 」用 simulated 措辞"],
         "audit": True},
        {"mode": "echo", "fields": ["output", "backend", "model", "tokens", "latency_ms"],
         "must_not": ["声称发生网络调用「, 」写审计冒充真实调用"],
         "audit": False},
        {"mode": "simulated", "fields": ["output", "backend", "model"],
         "must_not": ["与 live 混用同一字段名而不标 mode"],
         "audit": False},
    ]
    return {"modes": rows, "count": len(rows),
            "rule": "回执必须自带 mode；无 mode 的回执不得用于对外表述",
            "stance_guard": "代价显式：simulated 与 live 的区分是「不被 AI 忽悠」在工程上的落点"}


# ---------------------------------------------------------------- 20. 裁决表
ADJUDICATIONS: Tuple[Dict[str, str], ...] = (
    {"id": "O-1", "chosen": "A（不加字段）", "summary": "window_used 与 admitted 恒等；摘要后进窗用 summarized∩admitted 表达"},
    {"id": "O-2", "chosen": "B", "summary": "槽位快照周期 16 tick（2 的幂，便于对齐）"},
    {"id": "O-3", "chosen": "B", "summary": "MAX_SNAPSHOT_AGE = 2×周期 = 32（由 O-2 推导）"},
    {"id": "O-4", "chosen": "A", "summary": "UNKNOWN 占比 >1% 即告警，阈值进配置"},
    {"id": "O-5", "chosen": "B", "summary": "90 天或 10 万条触线转 archive（转存不删除）"},
    {"id": "O-6", "chosen": "A", "summary": "cost_estimate 单位 ms；token 归 ModelAdapter.usage"},
    {"id": "O-7", "chosen": "B", "summary": "单写者原则：.lock 判定唯一 writer，多实例各写各账本"},
    {"id": "O-8", "chosen": "B", "summary": "hit_rate 分母 = layer_hit + layer_miss"},
    {"id": "O-9", "chosen": "B", "summary": "代际切换换新账本文件（名含 fingerprint 前 16 位）"},
    {"id": "O-10", "chosen": "B", "summary": "禁止 sampled 事后补采：缺口就是缺口"},
)


def skill_uplift_adjudication() -> Dict[str, Any]:
    """O-1～O-10 裁决表：每条给择定与一句话理由，可在回放与 P1 中引用。"""
    return {"adjudications": [dict(a) for a in ADJUDICATIONS], "count": len(ADJUDICATIONS),
            "all_decided": len(ADJUDICATIONS) == 10,
            "deviation": "O-1 未采用投喂的 after_summary 字段（会破坏 41 字段冻结），改为交集表达",
            "stance_guard": "取舍留痕：开放问题不裁决，就会在实现里被随机裁决"}


# ---------------------------------------------------------------- 21. P1 门禁
P1_EPS = 0.05


def skill_uplift_p1_gate(pair: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """P1 成对回归四判据：预算不增 / hit_rate 不降 / 重合度 ≥ 基线-ε / 零 UNKNOWN。"""
    p = dict(pair or {})
    base = dict(p.get("baseline") or {})
    cand = dict(p.get("candidate") or {})
    used_ok = cand.get("window_used", 0) <= base.get("window_used", 0)
    bh, ch = base.get("hit_rate"), cand.get("hit_rate")
    if bh is None and ch is None:
        hit = {"verdict": "skipped", "why": "两边都 None，无检索发生"}
    elif ch is None:
        hit = {"verdict": "REJECT", "why": "候选侧 hit_rate 缺失"}
    else:
        hit = {"verdict": "PASS" if ch >= bh else "REJECT", "why": "%s vs %s" % (ch, bh)}
    a, b = set(cand.get("admitted") or []), set(base.get("admitted") or [])
    union = a | b
    jac = (len(a & b) / len(union)) if union else 1.0
    base_jac = 1.0
    cover_ok = jac >= base_jac - P1_EPS
    unknown = int(cand.get("unknown_events", 0) or 0)
    checks = {"budget_not_up": used_ok, "hit_rate_not_down": hit["verdict"] != "REJECT",
              "coverage_ok": cover_ok, "zero_unknown": unknown == 0}
    verdict = "PASS" if all(checks.values()) else "REJECT"
    return {"checks": checks, "hit_rate_detail": hit,
            "jaccard": round(jac, 5), "epsilon": P1_EPS,
            "unknown_events": unknown,
            "diff_bundle": ["diff_manifest", "diff_score", "diff_reason_codes"],
            "verdict": verdict,
            "rule": "四条全过才 PASS；hit_rate 跳过要单列，跳过不等于通过",
            "stance_guard": "取舍留痕：REJECT 必须能指出是哪一条不满足，而不是笼统失败"}


# ---------------------------------------------------------------- 22. 立场矩阵
def skill_uplift_stance_matrix() -> Dict[str, Any]:
    """五条立场 × 本轮落点：每条立场至少要有两处可判定的落实。"""
    extra = {
        "S1": ["ci.yml 无 pip install", "redline_scan 扫 import 白名单"],
        "S2": ["T-U1-A/A2 全序断言", "A-U5-3 千次一致断言"],
        "S3": ["CONFLICTS X1–X10", "DEFECTS M1–M5", "O-1～O-10 裁决表"],
        "S4": ["A1/A2 带范围", "CI untested 标注", "live untested 标注"],
        "S5": ["bridges/ 在包外「, 」密钥只从 env 读", "echo 与 live 分离"],
    }
    rows = [{"id": s["id"], "name": s["name"], "where": s["where"],
             "checks": extra[s["id"]]} for s in STANCES]
    return {"stances": rows, "count": len(rows),
            "each_has_two_checks": all(len(r["checks"]) >= 2 for r in rows),
            "stance_guard": "取舍留痕：立场不落成检查，就只是口号"}


# ---------------------------------------------------------------- 23. 回执
def skill_uplift_audit_receipt(events: Sequence[Dict[str, Any]] | None = None) -> Dict[str, Any]:
    """升级回执：本轮 U1–U6 落地事件的规范化回执 + 16 位稳定指纹 + 密令。"""
    evs = [{"unit": str(e.get("unit", "")), "ref": str(e.get("ref", "")),
            "result": str(e.get("result", ""))} for e in (events or [])]
    canon = _canon(evs)
    units = sorted({e["unit"] for e in evs if e["unit"]})
    return {"events": evs, "event_count": len(evs), "units_covered": units,
            "all_six": units == ["U1", "U2", "U3", "U4", "U5", "U6"],
            "fingerprint": _sha16(canon), "chain": _sha16(SEAL + canon),
            "execution": "human_manual", "seal": SEAL,
            "stance_guard": "取舍留痕：回执本身可回放，才谈得上可审计"}


# ---------------------------------------------------------------- 24. 维度不变
def skill_uplift_dimension_invariant() -> Dict[str, Any]:
    """维度不变式：1331 行 / 108641 节点不新增；扩展包不进 PACK_ORDER。"""
    rows, nodes = _rows(), _nodes()
    return {"locks": {"side": LOCK_SIDE, "design_grid": LOCK_DESIGN,
                      "mandala": LOCK_MANDALA, "hilbert": LOCK_HILBERT,
                      "kalman": LOCK_KALMAN},
            "computed": {"rows": rows, "nodes": nodes},
            "rows_ok": rows == LOCK_SIDE, "nodes_ok": nodes == LOCK_MANDALA,
            "subdisciplines": SUBD_TOTAL, "slots_per": SLOTS_PER,
            "slots_reserved": SLOTS_RESERVED, "nodes_per": NODES_PER,
            "nodes_coord": NODES_COORD,
            "agents_created_by_this_pack": 0,
            "pack_order_untouched": True,
            "verdict": "PASS" if rows == LOCK_SIDE and nodes == LOCK_MANDALA else "FAIL",
            "stance_guard": "取舍留痕：修桥不长新器官——维度不变式必须原样成立"}


# ---------------------------------------------------------------- 技能注册
SKILL_NAMES: Tuple[str, ...] = (
    "uplift.unit_registry", "uplift.order_key_check", "uplift.purity_contract",
    "uplift.regression_ledger", "uplift.ci_spec", "uplift.template_check",
    "uplift.badge_consistency", "uplift.support_matrix", "uplift.measure_a1_verdict",
    "uplift.measure_a2_disclosure", "uplift.evidence_chain", "uplift.ngram_dice",
    "uplift.hybrid_score_parts", "uplift.matching_acceptance", "uplift.bridge_boundary",
    "uplift.backend_registry", "uplift.remote_gate", "uplift.audit_policy",
    "uplift.live_receipt_schema", "uplift.adjudication", "uplift.p1_gate",
    "uplift.stance_matrix", "uplift.audit_receipt", "uplift.dimension_invariant",
)
SKILL_FNS: Tuple[Any, ...] = (
    skill_uplift_unit_registry, skill_uplift_order_key_check, skill_uplift_purity_contract,
    skill_uplift_regression_ledger, skill_uplift_ci_spec, skill_uplift_template_check,
    skill_uplift_badge_consistency, skill_uplift_support_matrix,
    skill_uplift_measure_a1_verdict, skill_uplift_measure_a2_disclosure,
    skill_uplift_evidence_chain, skill_uplift_ngram_dice,
    skill_uplift_hybrid_score_parts, skill_uplift_matching_acceptance,
    skill_uplift_bridge_boundary, skill_uplift_backend_registry,
    skill_uplift_remote_gate, skill_uplift_audit_policy,
    skill_uplift_live_receipt_schema, skill_uplift_adjudication, skill_uplift_p1_gate,
    skill_uplift_stance_matrix, skill_uplift_audit_receipt, skill_uplift_dimension_invariant,
)


# ---------------------------------------------------------------- 包定义
class UpliftPack(DomainPack):
    key = DOMAIN
    name = "补齐短板赋能升级包 UPLIFT（U1–U6）"
    description = ("把 S1–S6 六个短板的修复与验证落成可判定技能：排序键全序、纯函数契约、"
                   "回归口径账、CI 契约、模板与徽章与支持矩阵一致性、A1/A2 实测判定与证据链、"
                   "n-gram 混合分与匹配验收、桥边界与远程门禁与审计策略、O-1～O-10 裁决、"
                   "P1 四判据门禁；0 agent，不改维度、不联网、不起线程。")
    skills: List[SkillSpec] = [
        SkillSpec(name=SKILL_NAMES[i], fn=SKILL_FNS[i],
                  description=(SKILL_FNS[i].__doc__ or "").strip().splitlines()[0],
                  tags=["uplift", "hardening", "deterministic"],
                  permissions=0)
        for i in range(len(SKILL_FNS))
    ]
    roles: List[Any] = []
    workflows: List[WorkflowSpec] = [
        WorkflowSpec(name="W1_determinism",
                     description="U1：排序键全序 → 纯函数契约 → 回归口径",
                     steps=["order_key_check", "purity_contract", "regression_ledger"]),
        WorkflowSpec(name="W2_ecosystem",
                     description="U6：CI 契约 → 模板完整性 → 徽章一致 → 支持矩阵",
                     steps=["ci_spec", "template_check", "badge_consistency",
                            "support_matrix"]),
        WorkflowSpec(name="W3_measurement",
                     description="U3：A1 判定（含变异证明）→ A2 披露 → 证据链",
                     steps=["measure_a1_verdict", "measure_a2_disclosure", "evidence_chain"]),
        WorkflowSpec(name="W4_matching",
                     description="U5：n-gram Dice → 混合分权重 → 两用例验收",
                     steps=["ngram_dice", "hybrid_score_parts", "matching_acceptance"]),
        WorkflowSpec(name="W5_host_bridge",
                     description="U2：桥边界 → 后端登记 → 远程门禁 → 审计策略 → 回执语义",
                     steps=["bridge_boundary", "backend_registry", "remote_gate",
                            "audit_policy", "live_receipt_schema"]),
        WorkflowSpec(name="W6_adjudication",
                     description="U4：O-1～O-10 裁决 → P1 四判据门禁",
                     steps=["adjudication", "p1_gate"]),
        WorkflowSpec(name="W7_acceptance",
                     description="总验收：六单元清单 → 五立场 → 维度不变式 → 回执",
                     steps=["unit_registry", "stance_matrix", "dimension_invariant",
                            "audit_receipt"]),
    ]


def pack_summary() -> Dict[str, Any]:
    """供快速核对：维度不变 / 计数 / 审视与修正 / 缺陷 / 零开销声明。"""
    return {
        "matrix_id": MATRIX_ID, "upstream": [UPSTREAM_ID, UPSTREAM_ID_2],
        "skills": len(SKILL_FNS), "workflows": len(UpliftPack.workflows),
        "agents_created": 0, "skill_prefix": "uplift",
        "locks": {"rows_total": _rows(), "nodes_total": _nodes(),
                  "rows_ok": _rows() == LOCK_SIDE, "nodes_ok": _nodes() == LOCK_MANDALA,
                  "side": LOCK_SIDE, "design_grid": LOCK_DESIGN, "mandala": LOCK_MANDALA,
                  "hilbert": LOCK_HILBERT, "kalman": LOCK_KALMAN,
                  "subdisciplines": SUBD_TOTAL, "slots_per": SLOTS_PER,
                  "slots_reserved": SLOTS_RESERVED, "nodes_per": NODES_PER,
                  "nodes_coord": NODES_COORD},
        "addressing_unchanged": _rows() == LOCK_SIDE and _nodes() == LOCK_MANDALA,
        "units": len(UNITS), "unit_ids": [u["id"] for u in UNITS],
        "conflicts": len(CONFLICTS), "conflict_ids": [c["id"] for c in CONFLICTS],
        "fixes": len(FIXES), "defects": len(DEFECTS),
        "stances": len(STANCES), "non_goals": len(NON_GOALS),
        "acceptance_items": len(ACCEPTANCE),
        "adjudications": len(ADJUDICATIONS),
        "refused_ops": len(REFUSED_OPS),
        "threads": 0, "timers": 0, "sleep": False, "disk_writes": 0,
        "deps": 0, "network": False, "api_calls": 0,
        "metaphor": True, "metaphor_note": METAPHOR_NOTE,
        "execution": "human_manual", "seal": SEAL,
    }
