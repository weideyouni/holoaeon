# -*- coding: utf-8 -*-
"""NephronPack —— 肾单位层 NEPHRON·P0 认知账本与回放器（HoloAeon 横切扩展包，第十五包）
================================================================================
来源：投喂文本「实现 NEPHRON 肾单位层 P0 —— 认知账本（Ledger）与回放器（Replayer）」
      （2026-10-30，另一智能体产出，本包在实现前先做审视与修正）

定位：把 P0 的**只读观测层**落成可判定的声明 + 算法层。三件事：
      ① 记录结构可校验（Page / SlotLedgerEntry / LedgerRecord / Event / WindowManifest 共 41 字段）
      ② 事件与理由码可校验（11 类事件 × 27 个已归类理由码 + UNKNOWN 兜底单独计数）
      ③ 回放可重建（窗口构成 / 槽位快照 / 决策输入 / 变更时间线），且同一账本两次回放哈希一致

  24 个技能 = 记录结构 4 + 事件理由码 3 + 采集开关 3 + 回放 5 + 隐私 2 + 指纹 2 + 边界验收 3 + 文档回执 2
  7 条工作流 = W1 观测 / W2 清单 / W3 回放 / W4 确定性 / W5 隐私 / W6 守卫 / W7 验收
  0 个角色   = 不建 agent（G15 的 n_agents==25 是硬约束）

P0 的纪律（写进实现，不是口号）：
  · **只记录、不决策**：本包不做分页 / 压缩 / 淘汰 / 预算控制（这些是 P1/P2）；
    任何"顺手优化"的痕迹都会被 `non_goal_scan` 判为越界。
  · **零侵入**：本包不接管采集。队列、异步刷写、落盘属于宿主（host_managed），
    包内只给语义契约与丢弃计数口径；本包自己不起线程、不写盘、不常驻。
  · **不宣称已测**：`A1 关闭态与开启态逐字节一致` 与 `开启 full 的额外开销` 两项都不是
    纯函数能证明的，一律输出 `pending_human_measure`，不得写成 pass。
  · 纯标准库、确定性、离线；不联网、不开端口、不调外部模型。

维度不变（与第十一 ~ 十四包同口径）：127 × 10 + 61 = 1331 行；127 × 855 + 56 = 108641 节点。

本包对投喂稿的 10 处审视（N1–N10）与 3 处修正（F1–F3）见 `docs/nephron.md` 第 2 章；
其中 N10（槽位快照无来源事件）改变了回放器的边界：P0 的槽位快照取"最近旁挂快照 + 年龄"，
重演属 P1，这是**明确的能力降级**，不是实现遗漏。
"""
from __future__ import annotations

import hashlib
import json
import os
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .base import DomainPack, SkillSpec, WorkflowSpec

# ---------------------------------------------------------------- 常量（锁数）
MATRIX_ID = "SG-MASTER-NEPHRON-1331x1331-EXT-V1.0"
UPSTREAM_ID = "SG-MASTER-METAB-1331x1331-EXT-V1.0"
UPSTREAM_ID_2 = "HOLOAEON-NEPHRON-P0-SPEC-V1.0"
DOMAIN = "nephron"
LOCK_SIDE = 1331
LOCK_DESIGN = 1771561
LOCK_MANDALA = 108641
LOCK_HILBERT = 651846
LOCK_KALMAN = 22627
HEARTBEAT_BASE, HEARTBEAT_COUNT, HEARTBEAT_DIM = 9800, 70, 768
HEARTBEAT_ALPHA = 0.18
SUBD_TOTAL, SLOTS_PER, SLOTS_RESERVED = 127, 10, 61
NODES_PER, NODES_COORD = 855, 56
SEAL = "潮起开门，潮落闭嘴"

METAPHOR_NOTE = ("'肾单位 / 肾小球 / 重吸收 / 髓质浓缩 / 集合管'沿用架构隐喻（metaphor=True）；"
                 "实证部分是确定性记账与回放算法：本包不产生任何生理行为、不扩大任何容量上限")

# 采集与回放阈值（本包自定默认；改动须留痕，不得在会话内悄悄漂移）
SAMPLE_RATE_MIN = 0.01
MAX_SNAPSHOT_AGE = 32
RAW_LEN_UNIT = "token"          # P0 统一口径（见 N/F 消解），禁止与字符口径混用
PAYLOAD_DIGEST_MIN = 8

# ---------------------------------------------------------------- 结构定义（41 字段）
PAGE_FIELDS: Tuple[Dict[str, Any], ...] = (
    {"name": "page_id", "type": "string", "range": "非空", "required": True,
     "note": "稳定哈希：内容不变则 id 不变"},
    {"name": "origin", "type": "enum", "range": "session|hebbian|skeleton|external",
     "required": True, "note": "页的来源层，与 layer_residency 同口径"},
    {"name": "payload_digest", "type": "string", "range": "非空，≥8 字符",
     "required": True, "note": "载荷摘要；P0 不存原文全文"},
    {"name": "raw_len", "type": "int", "range": ">=0", "required": True,
     "note": "统一按 token 计（RAW_LEN_UNIT），字符口径禁用"},
    {"name": "form", "type": "enum", "range": "raw|summary|fingerprint", "required": True,
     "note": "进入窗口时的形态"},
    {"name": "importance", "type": "float", "range": "0~1", "required": True,
     "note": "P0 只记录既有值，不重新计算；缺失按 0.0 记并告警"},
    {"name": "last_tick", "type": "int", "range": ">=0", "required": True,
     "note": "最后一次进入窗口的 tick"},
    {"name": "hit_count", "type": "int", "range": ">=0", "required": True,
     "note": "被检索命中累计次数"},
    {"name": "lineage_ref", "type": "string", "range": "血统账本引用或 \"NONE\"",
     "required": True, "note": "无血统必须显式 \"NONE\"，留空即违规（A6）"},
    {"name": "fingerprint", "type": "string", "range": "代际指纹", "required": True,
     "note": "与 LedgerRecord 的 fingerprint 同代际"},
)

SLOT_FIELDS: Tuple[Dict[str, Any], ...] = (
    {"name": "slot_id", "type": "string", "range": "非空", "required": True, "note": "槽位标识"},
    {"name": "slot_class", "type": "enum", "range": "trunk|reserve", "required": True,
     "note": "主干槽 / 备用槽"},
    {"name": "occupant_page", "type": "string|null", "range": "page_id 或 null",
     "required": True, "note": "空槽必须显式 null"},
    {"name": "allocated_tick", "type": "int", "range": ">=0", "required": True,
     "note": "分配时刻"},
    {"name": "fragment_flag", "type": "bool", "range": "true|false", "required": True,
     "note": "是否为碎片占位"},
    {"name": "owner_symbiont", "type": "string|null", "range": "共生体 id 或 null",
     "required": True, "note": "与 METAB 共生体注册表对得上"},
    {"name": "reclaimability", "type": "enum", "range": "cold|warm|hot", "required": True,
     "note": "可回收性（P0 只观察，不改）"},
)

RECORD_FIELDS: Tuple[Dict[str, Any], ...] = (
    {"name": "tick", "type": "int", "range": ">=0", "required": True, "note": "主键第一段"},
    {"name": "seq", "type": "int", "range": ">=0，全局单调", "required": True,
     "note": "主键第二段；同 tick 多记录按 seq 排序"},
    {"name": "window_budget", "type": "int", "range": ">=0", "required": True,
     "note": "本 tick 窗口预算（记录既有值）"},
    {"name": "window_used", "type": "int", "range": ">=0", "required": True,
     "note": "实际占用；应等于 admitted 数"},
    {"name": "layer_residency", "type": "map", "range": "{working,hebbian,skeleton,external}->int",
     "required": True, "note": "四键必须齐全"},
    {"name": "hit_rate", "type": "float|null", "range": "0~1 或 null", "required": True,
     "note": "无检索发生必须 null，不得填 0"},
    {"name": "compression_ratio", "type": "float|null", "range": "null（P0）", "required": True,
     "note": "P0 不做压缩，恒 null；P1 才有值"},
    {"name": "evicted_pages", "type": "int", "range": ">=0，P0 通常 0", "required": True,
     "note": "字段必须存在，即使为 0"},
    {"name": "external_calls", "type": "int", "range": ">=0", "required": True,
     "note": "外部调用次数（不含内容）"},
    {"name": "cost_estimate", "type": "float", "range": ">=0", "required": True,
     "note": "代价估计（既有值或显式 0）"},
    {"name": "confidence_estimate", "type": "float|null", "range": "0~1 或 null", "required": True,
     "note": "无法估计时必须 null，不得填 1.0"},
    {"name": "events", "type": "list<Event>", "range": "可为空", "required": True,
     "note": "本记录覆盖的事件"},
    {"name": "fingerprint", "type": "string", "range": "代际指纹", "required": True,
     "note": "与 Page 同代际"},
)

EVENT_FIELDS: Tuple[Dict[str, Any], ...] = (
    {"name": "type", "type": "enum", "range": "|".join((
        "window_build", "page_admit", "page_summarize", "page_reject",
        "layer_hit", "layer_miss", "retrieval", "eviction",
        "degradation", "fingerprint_mismatch", "budget_breach")), "required": True,
     "note": "11 类，不得扩展（新增须评审）"},
    {"name": "reason_code", "type": "string", "range": "27 码之一或 UNKNOWN", "required": True,
     "note": "且只携带一个主码"},
    {"name": "refs", "type": "list<string>", "range": "page_id/slot_id/symbiont_id", "required": True,
     "note": "可为空列表，但不得缺键"},
    {"name": "delta", "type": "map<string,number>", "range": "可选量化增量", "required": False,
     "note": "page_summarize 用 from_len/to_len 承载，不新增 Page 字段（F1）"},
)

MANIFEST_FIELDS: Tuple[Dict[str, Any], ...] = (
    {"name": "tick", "type": "int", "range": ">=0", "required": True, "note": "所描述 tick"},
    {"name": "admitted", "type": "list", "range": "{page_id,score,reason_code}", "required": True,
     "note": "进入窗口的页"},
    {"name": "summarized", "type": "list", "range": "{page_id,from_len,to_len,reason_code}",
     "required": True, "note": "被摘要的页"},
    {"name": "rejected", "type": "list", "range": "{page_id,reason_code}", "required": True,
     "note": "被拒的页与理由"},
    {"name": "budget_before", "type": "int", "range": ">=0", "required": True, "note": "构建前预算"},
    {"name": "budget_after", "type": "int", "range": ">=0", "required": True, "note": "构建后预算"},
    {"name": "fingerprint", "type": "string", "range": "代际指纹", "required": True,
     "note": "本次构建所用代际"},
)

STRUCTURES: Tuple[Dict[str, Any], ...] = (
    {"name": "Page", "fields": PAGE_FIELDS},
    {"name": "SlotLedgerEntry", "fields": SLOT_FIELDS},
    {"name": "LedgerRecord", "fields": RECORD_FIELDS},
    {"name": "Event", "fields": EVENT_FIELDS},
    {"name": "WindowManifest", "fields": MANIFEST_FIELDS},
)
FIELD_TOTAL = sum(len(s["fields"]) for s in STRUCTURES)   # 10+7+13+4+7 = 41

EVENT_TYPES: Tuple[str, ...] = (
    "window_build", "page_admit", "page_summarize", "page_reject",
    "layer_hit", "layer_miss", "retrieval", "eviction",
    "degradation", "fingerprint_mismatch", "budget_breach",
)

# ---------------------------------------------------------------- 理由码（27 + UNKNOWN 兜底）
REASON_CODES: Tuple[Dict[str, str], ...] = (
    {"code": "ADMIT_HIGH_RELEVANCE", "family": "admit", "for": "page_admit"},
    {"code": "ADMIT_RECENT", "family": "admit", "for": "page_admit"},
    {"code": "ADMIT_LINEAGE_TRUSTED", "family": "admit", "for": "page_admit"},
    {"code": "SUMM_LOW_VALUE_KEEP_TRACE", "family": "summ", "for": "page_summarize"},
    {"code": "SUMM_BUDGET_PRESSURE", "family": "summ", "for": "page_summarize"},
    {"code": "REJECT_REDUNDANT", "family": "reject", "for": "page_reject"},
    {"code": "REJECT_STALE_FINGERPRINT", "family": "reject", "for": "page_reject"},
    {"code": "REJECT_NO_LINEAGE", "family": "reject", "for": "page_reject"},
    {"code": "REJECT_BUDGET_EXCEEDED", "family": "reject", "for": "page_reject"},
    {"code": "REJECT_TRUST_RADIUS", "family": "reject", "for": "page_reject"},
    {"code": "LAYER_HIT_SHALLOW", "family": "layer", "for": "layer_hit"},
    {"code": "LAYER_HIT_DEEP", "family": "layer", "for": "layer_hit"},
    {"code": "LAYER_MISS_ALL", "family": "layer", "for": "layer_miss"},
    {"code": "RETRIEVAL_DEEP_TAX", "family": "retrieval", "for": "retrieval"},
    {"code": "RETRIEVAL_TIMEOUT", "family": "retrieval", "for": "retrieval"},
    {"code": "EVICT_LRU", "family": "evict", "for": "eviction"},
    {"code": "EVICT_LOW_IMPORTANCE", "family": "evict", "for": "eviction"},
    {"code": "EVICT_BUDGET", "family": "evict", "for": "eviction"},
    {"code": "DEGRADE_CONFIDENCE_FLOOR", "family": "degrade", "for": "degradation"},
    {"code": "DEGRADE_COST_BUDGET", "family": "degrade", "for": "degradation"},
    {"code": "DEGRADE_DISTURB_BUDGET", "family": "degrade", "for": "degradation"},
    {"code": "FINGERPRINT_MISMATCH_STALE", "family": "fingerprint", "for": "fingerprint_mismatch"},
    {"code": "FINGERPRINT_MISMATCH_MODEL", "family": "fingerprint", "for": "fingerprint_mismatch"},
    {"code": "BUDGET_BREACH_LATENCY", "family": "budget", "for": "budget_breach"},
    {"code": "BUDGET_BREACH_COST", "family": "budget", "for": "budget_breach"},
    {"code": "BUDGET_BREACH_DISTURBANCE", "family": "budget", "for": "budget_breach"},
    # R-01：投喂稿未给 window_build 任何理由码，此处按"新增需评审"逐条留痕新增 1 码
    {"code": "WINDOW_BUILD_COMPLETE", "family": "window", "for": "window_build"},
)

CODE_REVIEWS: Tuple[Dict[str, str], ...] = (
    {"id": "R-01", "added": "WINDOW_BUILD_COMPLETE",
     "why": "投喂稿 §7 理由码表覆盖了进/摘要/拒/层命中/检索/淘汰/降级/指纹/预算，"
            "但 window_build 事件本身没有码；不新增则只能硬塞错配码",
     "scope": "仅 window_build；不扩散到其他事件类型"},
)

UNKNOWN_CODE = "UNKNOWN"        # 兜底码：不入表，单独计数并告警

FAMILY_OF_TYPE: Tuple[Tuple[str, str], ...] = (
    ("window_build", "window"), ("page_admit", "admit"), ("page_summarize", "summ"),
    ("page_reject", "reject"), ("layer_hit", "layer"), ("layer_miss", "layer"),
    ("retrieval", "retrieval"), ("eviction", "evict"), ("degradation", "degrade"),
    ("fingerprint_mismatch", "fingerprint"), ("budget_breach", "budget"),
)

# ---------------------------------------------------------------- 10 处审视（N1–N10）
CONFLICTS: Tuple[Dict[str, str], ...] = (
    {"id": "N1",
     "point": "§6 要求「异步队列 + 落盘批量刷写」，与本项目红线「不起线程、不写盘」直接冲突",
     "A": "包内实现队列与落盘（线程 + 磁盘写）",
     "B": "包只给队列语义与丢弃计数口径，队列实例化与落盘归宿主（host_managed）",
     "chosen": "B",
     "reason": "红线是硬约束；把 I/O 交给宿主后，包仍能定义「队列满必须丢弃并计数」这条可判定契约"},
    {"id": "N2",
     "point": "§2「任意历史 tick 可回放」与 §6 三档开关 sampled（采样率 <1 时账本不完整）冲突",
     "A": "三档都宣称可回放（用抽样推断补齐）",
     "B": "off 与 sampled 不可完整回放，只有 full 可回放；sampled 只能回放已采样的 tick",
     "chosen": "B",
     "reason": "A3 要求'任意历史 tick 可被回放'——只有 full 能满足；抽档靠插值等于伪造账本"},
    {"id": "N3",
     "point": "§5「只追加、不可改写」与 §9「一键擦除」冲突",
     "A": "擦除 = 原地覆写或删除记录（破坏只追加）",
     "B": "擦除 = 独立受控操作：内容摘要替换为 ERASED:<hash>，并在账本尾部追加擦除记录（保留计数与指纹）",
     "chosen": "B",
     "reason": "擦除本身成为一条可回放事件，既满足隐私又保住 A5「不存在改写与删除路径」"},
    {"id": "N4",
     "point": "§5.3 有 compression_ratio 字段，§3 却把「压缩」列为 P0 非目标",
     "A": "记录既有系统的压缩比（若上游恰好有）",
     "B": "字段保留但 P0 恒为 null，并在字段字典注明「P1 才有值」",
     "chosen": "B",
     "reason": "P0 无压缩即无压缩比；宁可显式 null，也不把别处的数字冒充本层观测"},
    {"id": "N5",
     "point": "§7 规则允许使用 UNKNOWN 兜底码，但理由码表里没有 UNKNOWN",
     "A": "把 UNKNOWN 加入固定表（表变 28 码）",
     "B": "UNKNOWN 作保留码不入表：合法但必须单独计数并告警",
     "chosen": "B",
     "reason": "入表就变成'已归类'，等于把归类失败伪装成正常码；单列计数才看得见归类能力在退化"},
    {"id": "N6",
     "point": "§5.3 主键 (tick, seq) 与 §12 故障注入「时钟回跳」冲突：回跳会让新记录 tick 变小",
     "A": "照写，允许 (tick, seq) 乱序，靠 seq 排序",
     "B": "设水位线：tick 小于已见最大 tick 时拒绝追加，并记采集侧拒绝原因 APPEND_REJECT_CLOCK_REGRESSION",
     "chosen": "B",
     "reason": "只追加语义要求时间轴单调；回跳必须显式拒绝并留痕，不能静默插入"},
    {"id": "N7",
     "point": "A1「关闭态与开启态输出逐字节一致」与 §12「额外开销上限需实测」都不是纯函数能证明的",
     "A": "包内给出'已通过'的结论",
     "B": "包只产出断言契约（双跑 + 归一化字节比较、开销实测方法），状态一律 pending_human_measure",
     "chosen": "B",
     "reason": "声称未测过的事就是造假；契约 + 待测状态才能让 CI 真的去跑"},
    {"id": "N8",
     "point": "§5.1 raw_len 允许「token 或字符」两种口径，但只有一个字段",
     "A": "新增 len_unit 字段（改结构，违反「字段名与类型必须一致」）",
     "B": "锁死单一口径：账本级 meta 声明 len_unit=\"token\"，字符口径禁用",
     "chosen": "B",
     "reason": "同一字段两种单位会让所有长度比较静默失真；字段不能加，就锁口径"},
    {"id": "N9",
     "point": "§7 理由码表没有覆盖 window_build 事件的码",
     "A": "硬塞 LAYER_HIT_SHALLOW 等已有码（语义错配）",
     "B": "按「新增需评审」正式新增 WINDOW_BUILD_COMPLETE（R-01），并只作用于该事件",
     "chosen": "B",
     "reason": "规格自己写了'新增需评审'，这里就该真走一次评审并留痕，而不是错配"},
    {"id": "N10",
     "point": "§8 要求输出槽位快照，但 §5.4 的 11 类事件里没有任何 slot_alloc / slot_free，"
              "回放器无从由事件流重演槽位",
     "A": "扩展事件类型表，新增 slot_alloc / slot_free（表从 11 类变 13 类）",
     "B": "槽位快照改为账本旁挂周期性快照文件，P0 回放取「最近快照 ≤ tick」并披露快照年龄",
     "chosen": "B",
     "reason": "事件表是 P0 固定项（扩展即需评审）；旁挂快照不改枚举，代价是 P0 只披露年龄、"
               "不重演槽位变化——这条降级必须写进已知限制，不能假装已重演"},
)

# ---------------------------------------------------------------- 3 处修正（F1–F3）
FIXES: Tuple[Dict[str, str], ...] = (
    {"id": "F1", "finding": "§5 里 WindowManifest.summarized 需要 from_len/to_len，"
                            "而 Page 没有长度快照字段；若为此加字段会破坏「字段名必须一致」",
     "fix": "由 page_summarize 事件的 delta{from_len,to_len} 承载，Page 结构不动",
     "impact": "回放只读 delta 即可还原摘要前后长度；摘要正文不入账本"},
    {"id": "F2", "finding": "§5.1 importance 标 float 且「只记录既有值」，但既有系统可能不提供",
     "fix": "缺失按 0.0 记录，同时在 page_validate 的 warnings 里标 importance_absent（不改 Page 字段）",
     "impact": "下游若用 importance 做排序，必须同时看 warnings，否则会把'未知'当'最低'"},
    {"id": "F3", "finding": "§8「回放不依赖原文」被读成'必须存摘要正文'，但实际只要求重建"
                            "窗口构成 / 槽位快照 / 决策输入，这三者都不需要摘要正文",
     "fix": "P0 账本不存摘要正文，只存 payload_digest + raw_len + delta 长度；正文回放列入 P1 之后再谈",
     "impact": "隐私面最小化；代价是无法回放'模型当时看到的实际文本'——列已知限制"},
)

# ---------------------------------------------------------------- 采集侧拒绝原因（不入事件表）
APPEND_REJECTS: Tuple[Dict[str, str], ...] = (
    {"code": "APPEND_REJECT_CLOCK_REGRESSION", "why": "tick 小于已见最大 tick（时钟回跳）"},
    {"code": "APPEND_REJECT_DUPLICATE_PK", "why": "(tick, seq) 已存在"},
    {"code": "APPEND_REJECT_SCHEMA_INVALID", "why": "记录未通过结构校验"},
)

# ---------------------------------------------------------------- P0 非目标（越界即失败）
NON_GOALS: Tuple[Dict[str, str], ...] = (
    {"id": "NG1", "name": "分页", "flag": "paging"},
    {"id": "NG2", "name": "压缩", "flag": "compression"},
    {"id": "NG3", "name": "淘汰策略", "flag": "eviction_policy"},
    {"id": "NG4", "name": "预算控制", "flag": "budget_control"},
    {"id": "NG5", "name": "写内核态代码", "flag": "kernel_code"},
    {"id": "NG6", "name": "接入闭源二进制 / 逆向闭源组件", "flag": "closed_binary"},
)

# 采集 hook 点（零侵入接入清单）
HOOK_POINTS: Tuple[Dict[str, str], ...] = (
    {"name": "before_window_build", "event": "window_build", "why": "取预算与驻留基线"},
    {"name": "after_window_build", "event": "window_build", "why": "出完整清单（进/摘要/拒）"},
    {"name": "on_page_admit", "event": "page_admit", "why": "记分与理由码"},
    {"name": "on_page_summarize", "event": "page_summarize", "why": "记 from_len/to_len（delta）"},
    {"name": "on_page_reject", "event": "page_reject", "why": "记拒因（必带码）"},
    {"name": "on_layer_hit", "event": "layer_hit", "why": "记浅/深层命中"},
    {"name": "on_layer_miss", "event": "layer_miss", "why": "记全层未命中"},
    {"name": "on_retrieval", "event": "retrieval", "why": "记检索税与超时"},
    {"name": "on_eviction", "event": "eviction", "why": "P0 通常 0，但接口必须在"},
    {"name": "on_fingerprint_check", "event": "fingerprint_mismatch", "why": "失配必须留痕"},
    {"name": "on_budget_check", "event": "budget_breach", "why": "记延迟/成本/打扰越界"},
)

# A1–A8 验收
ACCEPTANCE: Tuple[Dict[str, str], ...] = (
    {"id": "A1", "claim": "关闭态与开启态系统输出逐字节一致（CI 断言）",
     "how": "同一输入双跑（off / full）+ 归一化字节比较", "pack_can_prove": "false"},
    {"id": "A2", "claim": "采集异常不影响主流程",
     "how": "注入队列满 / 写失败 / 序列化异常 / 时钟回跳", "pack_can_prove": "contract_only"},
    {"id": "A3", "claim": "任意历史 tick 可回放且窗口构成可解释",
     "how": "full 账本逐 tick 回放 + 每次进/摘要/拒都有码", "pack_can_prove": "true"},
    {"id": "A4", "claim": "回放确定性：两次回放输出哈希一致",
     "how": "归一化后重跑取哈希", "pack_can_prove": "true"},
    {"id": "A5", "claim": "账本只追加，无改写与删除路径",
     "how": "校验 seq 单调 + 主键唯一 + 链摘要", "pack_can_prove": "true"},
    {"id": "A6", "claim": "无血统页显式 lineage_ref=\"NONE\"",
     "how": "逐页校验，留空即 error", "pack_can_prove": "true"},
    {"id": "A7", "claim": "指纹失配必产 fingerprint_mismatch 事件",
     "how": "比对期望/实测指纹", "pack_can_prove": "true"},
    {"id": "A8", "claim": "文档完备（字段字典 / 理由码 / 开关 / 回放教程 / 隐私）",
     "how": "docs/nephron.md 与 field_dictionary 对齐", "pack_can_prove": "true"},
)

REFUSED_OPS: Tuple[str, ...] = (
    "改写在账记录", "删除账本记录", "用采样账本推断未采样 tick",
    "把窗内页原文写入账本", "记录外部调用请求体明文",
    "本包内起线程做异步刷写", "本包内直接落盘",
    "把 importance 缺失当成 0 参与排序而不告知",
    "指纹失配后静默复用旧页", "把 A1 或额外开销改写成'已通过'而不带证据与范围",
    "把 measured_with_scope 说成生产链路已闭环",
    "顺手做分页/压缩/淘汰/预算控制",
)


# ---------------------------------------------------------------- 内部工具
def _canon(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha16(obj: Any) -> str:
    return hashlib.sha256(_canon(obj).encode("utf-8")).hexdigest()[:16].upper()


def _norm(rec: Dict[str, Any]) -> Dict[str, Any]:
    """归一化：剔除外部时钟与运行环境因素，保证回放确定性（A4）。"""
    drop = ("timestamp", "ts", "ingested_at", "wall_clock", "host", "pid", "elapsed_ms")
    return {k: v for k, v in dict(rec).items() if k not in drop}


def _num(v: Any) -> Optional[float]:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _int(v: Any, dflt: int = 0) -> int:
    """整数化：0 不得被 `or` 吞成默认值（seq=0 / tick=0 是合法主键）。"""
    n = _num(v)
    return dflt if n is None else int(n)


# ---------------------------------------------------------------- 1. 记录结构
def skill_nephron_page_schema() -> Dict[str, Any]:
    """记录结构总表：五个结构、41 个字段、每个字段的类型与范围。"""
    return {"structures": [{"name": s["name"], "count": len(s["fields"]),
                           "fields": [f["name"] for f in s["fields"]]} for s in STRUCTURES],
            "structure_count": len(STRUCTURES), "field_total": FIELD_TOTAL,
            "raw_len_unit": RAW_LEN_UNIT,
            "note": "raw_len 统一按 %s 计；字符口径禁用（N8）" % RAW_LEN_UNIT,
            "stance_guard": "容量不扩大：结构只描述观测，不含任何扩容字段"}


def skill_nephron_page_validate(page: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """逐页校验：必填、枚举、范围、血统显式标注（A6）。"""
    p = dict(page or {})
    errors: List[str] = []
    warnings: List[str] = []
    for f in PAGE_FIELDS:
        if f["required"] and f["name"] not in p and f["name"] != "importance":
            errors.append("missing:%s" % f["name"])
    if p.get("origin") not in ("session", "hebbian", "skeleton", "external"):
        errors.append("enum:origin")
    if p.get("form") not in ("raw", "summary", "fingerprint"):
        errors.append("enum:form")
    dig = str(p.get("payload_digest") or "")
    if len(dig) < PAYLOAD_DIGEST_MIN:
        errors.append("payload_digest_too_short")
    if p.get("lineage_ref") is None or str(p.get("lineage_ref")) == "":
        errors.append("lineage_ref_empty_forbidden")      # A6：不得留空
    for k in ("raw_len", "last_tick", "hit_count"):
        n = _num(p.get(k))
        if n is None or n < 0:
            errors.append("range:%s" % k)
    imp = _num(p.get("importance"))
    if p.get("importance") is None:
        warnings.append("importance_absent_recorded_as_zero")   # F2
        imp = 0.0
    elif imp is None:
        errors.append("type:importance")
        imp = 0.0
    if not (0.0 <= imp <= 1.0):
        errors.append("range:importance")
    lineage_tag = "无血统（显式 NONE）" if str(p.get("lineage_ref")) == "NONE" else "有血统引用"
    return {"ok": not errors, "errors": errors, "warnings": warnings,
            "lineage_tag": lineage_tag,
            "raw_len_unit": RAW_LEN_UNIT,
            "stance_guard": "取舍必须留痕：缺什么、为什么不合格都写清楚"}


def skill_nephron_ledger_record(record: Optional[Dict[str, Any]] = None,
                                watermark: int = -1,
                                seen_keys: Optional[Sequence[Sequence[int]]] = None
                                ) -> Dict[str, Any]:
    """构造/校验一条 LedgerRecord：13 字段、四键驻留、只追加语义。"""
    r = dict(record or {})
    errors: List[str] = []
    for f in RECORD_FIELDS:
        if f["required"] and f["name"] not in r:
            errors.append("missing:%s" % f["name"])
    for k in ("updated_at", "rev", "version_of"):
        if k in r:
            errors.append("append_only_violation:%s" % k)
    res = r.get("layer_residency") or {}
    if set(("working", "hebbian", "skeleton", "external")) - set(res.keys()):
        errors.append("layer_residency_keys")
    if r.get("hit_rate") is not None and _num(r.get("hit_rate")) is None:
        errors.append("type:hit_rate")
    if r.get("compression_ratio") is not None:
        errors.append("p0_compression_ratio_must_be_null")       # N4
    if r.get("confidence_estimate") is not None and _num(r.get("confidence_estimate")) is None:
        errors.append("type:confidence_estimate")
    tick = int(_num(r.get("tick")) or 0)
    seq = int(_num(r.get("seq")) or 0)
    rejects: List[str] = []
    if watermark >= 0 and tick < watermark:
        rejects.append("APPEND_REJECT_CLOCK_REGRESSION")         # N6
    if [tick, seq] in [[int(a), int(b)] for a, b in (seen_keys or [])]:
        rejects.append("APPEND_REJECT_DUPLICATE_PK")
    if errors:
        rejects.append("APPEND_REJECT_SCHEMA_INVALID")
    digest = _sha16(_norm(r))
    return {"ok": not errors and not rejects, "errors": errors,
            "append_rejects": rejects, "record_digest": digest,
            "new_watermark": max(watermark, tick),
            "stance_guard": "取舍必须留痕：拒绝追加也要留拒绝原因"}


def skill_nephron_ledger_verify(records: Optional[Sequence[Dict[str, Any]]] = None,
                                anchor: str = "") -> Dict[str, Any]:
    """只追加核验：seq 单调、主键唯一、序号无缺口、tick 不倒退、链摘要比对（A5）。"""
    recs = [dict(x) for x in (records or [])]
    seqs = [_int(r.get("seq"), -1) for r in recs]
    ticks = [_int(r.get("tick"), -1) for r in recs]
    pks = [(_int(r.get("tick"), -1), _int(r.get("seq"), -1)) for r in recs]
    gap_at = [i for i, (a, b) in enumerate(zip(seqs, seqs[1:])) if b - a != 1]
    back_at = [i for i, (a, b) in enumerate(zip(ticks, ticks[1:])) if b < a]
    checks = {
        "seq_monotonic": all(a < b for a, b in zip(seqs, seqs[1:])) if len(seqs) > 1 else True,
        "pk_unique": len(set(pks)) == len(pks),
        "seq_no_gap": (not gap_at) and (not seqs or seqs[0] == 0),
        "tick_non_decreasing": not back_at,
    }
    running = ""
    for r in recs:
        running = _sha16(running + _canon(_norm(r)))
    chain = running or _sha16([])
    anchor_mismatch = bool(anchor) and anchor != chain
    broken = sorted(set(gap_at) | set(back_at))
    return {"ok": all(checks.values()) and not anchor_mismatch, "checks": checks,
            "broken_at": broken, "chain_digest": chain,
            "anchor": anchor, "anchor_mismatch": anchor_mismatch,
            "count": len(recs),
            "limits": "P0 只能发现结构性异常（缺口/重复/倒退）与锚点不符；"
                      "内容级篡改需宿主保存逐段锚点",
            "stance_guard": "可逆优先：异常定位到下标，而不是笼统失败"}


# ---------------------------------------------------------------- 2. 事件与理由码
def skill_nephron_reason_codes() -> Dict[str, Any]:
    """理由码表：27 个已归类码 + UNKNOWN 兜底（不入表，单独计数）。"""
    fams = sorted({c["family"] for c in REASON_CODES})
    return {"codes": len(REASON_CODES), "families": fams, "family_count": len(fams),
            "codes_by_family": {f: [c["code"] for c in REASON_CODES if c["family"] == f]
                                for f in fams},
            "unknown": {"code": UNKNOWN_CODE, "in_table": False,
                        "rule": "合法但必须单独计数并告警；不得静默吞掉"},
            "reviews": [dict(x) for x in CODE_REVIEWS],
            "stance_guard": "取舍必须留痕：新增码必须走评审并留痕（R-01）"}


def skill_nephron_event_validate(event: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """单个 Event 校验：11 类类型、单主码、码与类型族匹配、delta 数值化。"""
    e = dict(event or {})
    errors: List[str] = []
    if e.get("type") not in EVENT_TYPES:
        errors.append("type:not_in_11")
    code = str(e.get("reason_code") or "")
    by_code = {c["code"]: c for c in REASON_CODES}
    unclassified = code == UNKNOWN_CODE
    if not code:
        errors.append("reason_code_missing")
    elif unclassified:
        pass
    elif code not in by_code:
        errors.append("reason_code_not_in_table")
    else:
        fam = dict(FAMILY_OF_TYPE).get(str(e.get("type")), "")
        if by_code[code]["family"] != fam:
            errors.append("reason_code_type_mismatch")
    if "refs" not in e or not isinstance(e.get("refs"), list):
        errors.append("refs_missing_or_not_list")
    base = [k for k in ("type", "reason_code", "refs", "delta")]
    extra_reason = [k for k in e.keys() if k.endswith("reason_code") and k != "reason_code"]
    if extra_reason:
        errors.append("single_main_reason_code_only:%s" % ",".join(extra_reason))
    delta = e.get("delta") or {}
    if delta and not isinstance(delta, dict):
        errors.append("delta_not_map")
    bad_delta = [k for k, v in delta.items() if _num(v) is None] if isinstance(delta, dict) else []
    if bad_delta:
        errors.append("delta_not_numeric:%s" % ",".join(bad_delta))
    return {"ok": not errors, "errors": errors, "unclassified": unclassified,
            "alarm": 1 if unclassified else 0, "fields": base,
            "stance_guard": "可逆优先：无法归类的码单独计数，绝不静默吞掉"}


def skill_nephron_manifest_build(events: Sequence[Dict[str, Any]] | None = None,
                                 budget_before: int = 0, budget_after: int = 0,
                                 fingerprint: str = "") -> Dict[str, Any]:
    """由事件流构建 WindowManifest，并核对与 window_used 的一致性。"""
    evs = [dict(e) for e in (events or [])]
    admitted: List[Dict[str, Any]] = []
    summarized: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []
    for e in evs:
        code = str(e.get("reason_code") or "")
        refs = [str(x) for x in (e.get("refs") or [])]
        pid = refs[0] if refs else ""
        if e.get("type") == "page_admit":
            admitted.append({"page_id": pid,
                             "score": float((e.get("delta") or {}).get("score", 0.0)),
                             "reason_code": code})
        elif e.get("type") == "page_summarize":
            d = e.get("delta") or {}
            summarized.append({"page_id": pid,
                               "from_len": int(_num(d.get("from_len")) or 0),
                               "to_len": int(_num(d.get("to_len")) or 0),
                               "reason_code": code})
        elif e.get("type") == "page_reject":
            rejected.append({"page_id": pid, "reason_code": code})
    issues: List[str] = []
    for row in admitted + summarized + rejected:
        if not row["reason_code"]:
            issues.append("missing_reason_code:%s" % row["page_id"])
    if admitted and any(not r["reason_code"] for r in admitted):
        issues.append("admit_without_code")
    if summarized and not all(r["to_len"] <= r["from_len"] for r in summarized):
        issues.append("summary_not_shorter")
    return {"manifest": {"tick": int((evs[0].get("tick") if evs and "tick" in evs[0] else 0) or 0)
                             if evs else 0,
                         "admitted": admitted, "summarized": summarized,
                         "rejected": rejected,
                         "budget_before": int(budget_before),
                         "budget_after": int(budget_after),
                         "fingerprint": str(fingerprint)},
            "counts": {"admitted": len(admitted), "summarized": len(summarized),
                       "rejected": len(rejected)},
            "issues": issues, "ok": not issues,
            "stance_guard": "代价必须显式：每一次进/摘要/拒都必须带一个码"}


# ---------------------------------------------------------------- 3. 采集与开关
def skill_nephron_switch_policy(mode: str = "off", sample_rate: float = 0.0) -> Dict[str, Any]:
    """三档开关：off / sampled / full，默认 off，并声明各档的可回放范围（N2）。"""
    m = str(mode or "off")
    errors: List[str] = []
    if m not in ("off", "sampled", "full"):
        errors.append("mode:not_in(off|sampled|full)")
    if m == "sampled" and not (SAMPLE_RATE_MIN <= float(_num(sample_rate) or 0) <= 1.0):
        errors.append("sample_rate_out_of_range")
    scope = {"off": "none", "sampled": "only_sampled_ticks", "full": "all_ticks"}.get(m, "none")
    return {"mode": m, "enabled": m != "off", "sample_rate": float(_num(sample_rate) or 0.0),
            "replayable_scope": scope,
            "full_required_for_A3": True,
            "errors": errors, "ok": not errors,
            "default": "off",
            "stance_guard": "可逆优先：默认关闭，开与关都不改变系统既有输出"}


def skill_nephron_collect_plan() -> Dict[str, Any]:
    """采集方案契约：11 个 hook 点、失败静默、队列满丢弃计数、宿主负责刷写（N1）。"""
    return {"hooks": [dict(h) for h in HOOK_POINTS], "hook_count": len(HOOK_POINTS),
            "rules": {
                "attach": "hook / wrapper / 事件订阅，禁止在业务逻辑内散布记录代码",
                "failure": "任何采集失败静默降级为不记录，禁止抛到业务层",
                "queue": "异步队列 + 批量刷写由宿主实现；队列满则丢弃并计数",
                "drop_counters": ["dropped_queue_full", "failed_write", "failed_serialize"],
                "flush": "host_managed（本包不写盘、不起线程）"},
            "stance_guard": "取舍必须留痕：丢弃本身必须被计数，而不是消失"}


def skill_nephron_failure_injection_matrix() -> Dict[str, Any]:
    """四类采集故障的期望行为与禁止行为（A2 的契约面）。"""
    rows = (
        {"fault": "queue_full", "expected": "丢弃 + dropped_queue_full 计数", "forbidden": "阻塞主流程"},
        {"fault": "write_fail", "expected": "记 failed_write 并继续", "forbidden": "抛到业务层"},
        {"fault": "serialize_fail", "expected": "跳过该条并记 failed_serialize", "forbidden": "写半条记录"},
        {"fault": "clock_regression", "expected": "拒追加 + APPEND_REJECT_CLOCK_REGRESSION",
         "forbidden": "静默插入乱序记录"},
    )
    return {"rows": [dict(r) for r in rows], "count": len(rows),
            "claim_status": "contract_only（注入测试须由宿主执行）",
            "stance_guard": "可逆优先：任何故障都只能是'少记'，不能是'改行为'"}


# ---------------------------------------------------------------- 4. 回放
def skill_nephron_replay_window(records: Sequence[Dict[str, Any]] | None = None,
                                tick: int = 0, ledger_mode: str = "full") -> Dict[str, Any]:
    """回放某 tick 的窗口构成表（只读账本，不读原文）；非 full 账本明确拒绝。"""
    recs = [dict(r) for r in (records or [])]
    if ledger_mode != "full":
        return {"replayable": False, "reason": "partial_ledger_not_replayable",
                "scope": {"off": "none", "sampled": "only_sampled_ticks"}.get(ledger_mode, "none"),
                "manifest": None, "stance_guard": "可逆优先：不靠插值伪造未采样 tick"}
    hits = [r for r in recs if _int(r.get("tick"), -1) == int(tick)]
    if not hits:
        return {"replayable": False, "reason": "tick_not_in_ledger", "manifest": None}
    merged: List[Dict[str, Any]] = []
    for r in sorted(hits, key=lambda x: int(_num(x.get("seq")) or 0)):
        merged.extend([dict(e) for e in (r.get("events") or [])])
    built = skill_nephron_manifest_build(merged,
                                        int(_num(hits[-1].get("window_budget")) or 0),
                                        int(_num(hits[-1].get("window_used")) or 0),
                                        str(hits[-1].get("fingerprint") or ""))
    built["manifest"]["tick"] = int(tick)
    return {"replayable": True, "records_used": len(hits), "manifest": built["manifest"],
            "counts": built["counts"], "issues": built["issues"],
            "stance_guard": "取舍必须留痕：回放出来的每一次取舍都带原码"}


def skill_nephron_replay_slots(snapshots: Sequence[Dict[str, Any]] | None = None,
                               tick: int = 0) -> Dict[str, Any]:
    """槽位快照：取最近快照 ≤ tick，并披露快照年龄（P0 不重演，见 N10）。"""
    snaps = [dict(s) for s in (snapshots or [])]
    cand = [s for s in snaps if _int(s.get("tick"), -1) <= int(tick)]
    if not cand:
        return {"available": False, "reason": "no_snapshot_at_or_before_tick",
                "entries": [], "replay_scope": "snapshot_only"}
    snap = sorted(cand, key=lambda s: int(_num(s.get("tick")) or 0))[-1]
    entries = [dict(e) for e in (snap.get("entries") or [])]
    entries.sort(key=lambda e: str(e.get("slot_id")))
    age = int(tick) - int(snap.get("tick") or 0)
    errs: List[str] = []
    for e in entries:
        if e.get("slot_class") not in ("trunk", "reserve"):
            errs.append("enum:slot_class:%s" % e.get("slot_id"))
        if e.get("reclaimability") not in ("cold", "warm", "hot"):
            errs.append("enum:reclaimability:%s" % e.get("slot_id"))
        if "occupant_page" not in e:
            errs.append("occupant_page_missing:%s" % e.get("slot_id"))
    return {"available": True, "tick": int(tick), "snapshot_tick": int(snap.get("tick") or 0),
            "age_ticks": age, "stale": age > MAX_SNAPSHOT_AGE, "entries": entries,
            "errors": errs, "replay_scope": "snapshot_only",
            "not_implemented": "槽位变化重演（P1）",
            "stance_guard": "不扩大物理上限：只读快照，不改槽位分配"}


def skill_nephron_replay_inputs(records: Sequence[Dict[str, Any]] | None = None,
                                tick: int = 0) -> Dict[str, Any]:
    """决策输入重建：预算、四层驻留、命中率、代价、置信度、指纹。"""
    recs = [r for r in (records or []) if _int(r.get("tick"), -1) == int(tick)]
    if not recs:
        return {"available": False, "reason": "tick_not_in_ledger"}
    r = sorted(recs, key=lambda x: int(_num(x.get("seq")) or 0))[-1]
    return {"available": True, "tick": int(tick), "seq": int(_num(r.get("seq")) or 0),
            "window_budget": int(_num(r.get("window_budget")) or 0),
            "window_used": int(_num(r.get("window_used")) or 0),
            "layer_residency": dict(r.get("layer_residency") or {}),
            "hit_rate": r.get("hit_rate"),
            "hit_rate_null_ok": r.get("hit_rate") is None,
            "compression_ratio": r.get("compression_ratio"),
            "evicted_pages": int(_num(r.get("evicted_pages")) or 0),
            "external_calls": int(_num(r.get("external_calls")) or 0),
            "cost_estimate": _num(r.get("cost_estimate")),
            "confidence_estimate": r.get("confidence_estimate"),
            "fingerprint": str(r.get("fingerprint") or ""),
            "stance_guard": "代价必须显式：null 与 0 严格区分（无检索就是 null）"}


def skill_nephron_replay_timeline(records: Sequence[Dict[str, Any]] | None = None,
                                  tick_from: int = 0, tick_to: int = 0) -> Dict[str, Any]:
    """变更时间线：相邻 tick 窗口内页的进出、指纹变更、拒绝数变化。"""
    rows: List[Dict[str, Any]] = []
    recs = [dict(r) for r in (records or [])]
    ticks = sorted({_int(r.get("tick"), -1) for r in recs})
    prev: Optional[Dict[str, Any]] = None
    for t in ticks:
        if t < int(tick_from) or t > int(tick_to):
            continue
        rs = [r for r in recs if _int(r.get("tick"), -1) == t]
        rs.sort(key=lambda x: int(_num(x.get("seq")) or 0))
        admitted = sorted({str(p) for r in rs for p in
                           [str((e.get("refs") or [""])[0]) for e in (r.get("events") or [])
                            if e.get("type") == "page_admit"]})
        rejected = sum(1 for r in rs for e in (r.get("events") or [])
                       if e.get("type") == "page_reject")
        fp = str(rs[-1].get("fingerprint") or "") if rs else ""
        mism = sum(1 for r in rs for e in (r.get("events") or [])
                   if e.get("type") == "fingerprint_mismatch")
        row = {"tick": t, "admitted": admitted, "rejected": rejected,
               "fingerprint": fp, "fingerprint_mismatch": mism}
        if prev is not None:
            row["entered"] = sorted(set(admitted) - set(prev["admitted"]))
            row["left"] = sorted(set(prev["admitted"]) - set(admitted))
            row["fingerprint_changed"] = prev["fingerprint"] != fp
        rows.append(row)
        prev = row
    return {"rows": rows, "count": len(rows),
            "stance_guard": "取舍必须留痕：进出与失配都能按 tick 对齐"}


def skill_nephron_replay_determinism(records: Sequence[Dict[str, Any]] | None = None,
                                     ticks: Sequence[int] | None = None) -> Dict[str, Any]:
    """回放确定性：归一化后连跑两次，输出哈希必须一致（A4）。"""
    recs = [dict(r) for r in (records or [])]
    ts = [int(t) for t in (ticks or sorted({_int(r.get("tick"), -1) for r in recs}))]
    outs = []
    for _ in range(2):
        payload = []
        for t in ts:
            w = skill_nephron_replay_window(recs, t, "full")
            i = skill_nephron_replay_inputs(recs, t)
            payload.append({"tick": t, "manifest": w.get("manifest"),
                            "inputs": {k: v for k, v in i.items() if k != "stance_guard"}})
        outs.append(_sha16([_norm(x) if isinstance(x, dict) else x for x in payload]))
    return {"hash_1": outs[0], "hash_2": outs[1], "stable": outs[0] == outs[1],
            "ticks": ts, "count": len(ts),
            "stance_guard": "可逆优先：同一账本两次回放必须逐位一致，否则回放不可信"}


# ---------------------------------------------------------------- 5. 隐私
def skill_nephron_privacy_policy() -> Dict[str, Any]:
    """隐私规则：只存摘要与哈希；外部调用只记指纹与字节（P0 即需满足）。"""
    rows = (
        {"rule": "不存用户原文全文", "allowed": "payload_digest + raw_len + delta 长度",
         "forbidden": "payload 原文"},
        {"rule": "需存原文必须显式开启并加密", "allowed": "显式开关 + 加密仓（宿主）",
         "forbidden": "默认开启"},
        {"rule": "摘要生成不外送敏感字段", "allowed": "本地摘要器",
         "forbidden": "把敏感字段送外部模型"},
        {"rule": "本地摘要不可用", "allowed": "降级为仅存哈希 + 长度",
         "forbidden": "联网补摘要"},
        {"rule": "外部调用记录", "allowed": "调用指纹 + 字节数",
         "forbidden": "请求体明文"},
        {"rule": "账本目录权限", "allowed": "最小权限（宿主执行）", "forbidden": "全局可读"},
    )
    return {"rows": [dict(r) for r in rows], "count": len(rows),
            "stance_guard": "取舍必须留痕：连'没记录什么'也要写成规则"}


def skill_nephron_erase_operation(targets: Sequence[Dict[str, Any]] | None = None) -> Dict[str, Any]:
    """受控擦除：内容摘要替换为 ERASED:<hash>，保留计数与指纹，追加擦除记录（N3）。"""
    plan: List[Dict[str, Any]] = []
    for t in (targets or []):
        old = str(t.get("payload_digest") or "")
        plan.append({"page_id": str(t.get("page_id") or ""),
                     "payload_digest_after": "ERASED:%s" % _sha16(old) if old else "ERASED:",
                     "keep": ["raw_len", "hit_count", "lineage_ref", "fingerprint", "last_tick"],
                     "drop": ["payload_digest(原值)"]})
    return {"plan": plan, "count": len(plan),
            "append_record": {"type": "erase", "kept": ["counts", "fingerprints"]},
            "forbidden": ["删除账本记录", "改写历史记录", "抹掉计数与指纹"],
            "ok": all(p["page_id"] for p in plan),
            "stance_guard": "可逆优先：擦除也是追加一条记录，而不是让历史留白"}


# ---------------------------------------------------------------- 6. 指纹
def skill_nephron_generation_fingerprint(parts: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """代际指纹：权重 / 模板 / 量化 / LoRA 集 / 检索器五者的联合哈希。"""
    p = dict(parts or {})
    need = ("weights", "templates", "quantization", "loras", "retriever")
    missing = [k for k in need if k not in p]
    lor = p.get("loras") or []
    canon = {"weights": str(p.get("weights") or ""),
             "templates": str(p.get("templates") or ""),
             "quantization": str(p.get("quantization") or ""),
             "loras": sorted([str(x) for x in lor]) if isinstance(lor, list) else [str(lor)],
             "retriever": str(p.get("retriever") or "")}
    return {"fingerprint": _sha16(canon) if not missing else "",
            "parts_present": [k for k in need if k not in missing], "missing": missing,
            "ok": not missing, "canonical": canon,
            "stance_guard": "代价必须显式：缺一项就不算代际，不拿残缺指纹冒充"}


def skill_nephron_fingerprint_check(expected: str = "", observed: str = "",
                                    model_changed: bool = False) -> Dict[str, Any]:
    """指纹失配必须产出 fingerprint_mismatch 事件，禁止静默复用（A7）。"""
    if expected and expected == observed:
        return {"mismatch": False, "reuse_allowed": True, "event": None}
    code = "FINGERPRINT_MISMATCH_MODEL" if model_changed else "FINGERPRINT_MISMATCH_STALE"
    return {"mismatch": True, "reuse_allowed": False,
            "event": {"type": "fingerprint_mismatch", "reason_code": code,
                      "refs": [str(expected), str(observed)], "delta": {}},
            "code": code,
            "stance_guard": "取舍必须留痕：失配必须变成事件，不能变成'凑合还能用'"}


# ---------------------------------------------------------------- 7. 边界与验收
def skill_nephron_zero_intrusion_check() -> Dict[str, Any]:
    """A1 断言契约：off 与 full 双跑输出逐字节一致——只能由宿主 CI 证明（N7）。"""
    return {"assertion": "off_run_bytes == full_run_bytes",
            "method": ["同一输入双跑（off / full）", "剔除时间戳等外部因素",
                       "逐字节比较（非语义比较）"],
            "status": "pending_human_measure",
            "pack_can_prove": False,
            "why": "本包不起线程、不落盘、不观测宿主输出，无法自证零侵入",
            "must_fail_if": ["关账后输出有任何字节差异", "开启时业务层收到采集异常"],
            "stance_guard": "可逆优先：零侵入必须由外部证据成立，不能自封"}


def skill_nephron_non_goal_scan(config: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """P0 非目标扫描：出现分页/压缩/淘汰/预算控制/内核态/闭源即越界。"""
    c = dict(config or {})
    hits = [{"id": g["id"], "name": g["name"]} for g in NON_GOALS if c.get(g["flag"]) is True]
    return {"hits": hits, "count": len(hits), "clean": not hits,
            "checked": [g["id"] for g in NON_GOALS],
            "stance_guard": "不扩大物理上限：P0 只观测，任何'顺手优化'都算越界"}


def skill_nephron_acceptance_check(statuses: Dict[str, Any] | None = None,
                                   measured: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """A1–A8 验收状态机：pack 可证者自证，不可证者必须 pending；实测项由外部证据传入。"""
    st = dict(statuses or {})
    ev = dict(measured or {})
    rows: List[Dict[str, Any]] = []
    for a in ACCEPTANCE:
        provable = a["pack_can_prove"]
        given = st.get(a["id"])
        if provable == "true":
            state = given or "pass"
            if given in ("fail", "pending_human_measure"):
                state = given
        elif a["id"] in ev:
            state = "measured_with_scope"      # 只认外部证据，不认自说自话
        else:
            state = given if given == "fail" else "pending_human_measure"
        rows.append({"id": a["id"], "claim": a["claim"], "pack_can_prove": provable,
                     "status": state, "evidence": ev.get(a["id"], "")})
    pending = [r["id"] for r in rows if r["status"] == "pending_human_measure"]
    failed = [r["id"] for r in rows if r["status"] == "fail"]
    measured = [r["id"] for r in rows if r["status"] == "measured_with_scope"]
    verdict = ("reject" if failed else
               "provisional" if pending else
               "accepted_with_scope" if measured else "accepted")
    return {"rows": rows, "count": len(rows), "pending": pending, "failed": failed,
            "measured_with_scope": measured, "verdict": verdict,
            "scope_rule": "measured_with_scope 只表示「宿主侧限定范围实测」，不等于生产链路闭环",
            "rule": "pack 无法证明的项只能是 pending_human_measure，不得写成 pass",
            "stance_guard": "取舍必须留痕：待测项显式挂着，而不是默认合格"}


# ---------------------------------------------------------------- 8. 文档与回执
def skill_nephron_field_dictionary() -> Dict[str, Any]:
    """字段字典：41 字段逐条给出类型、范围、必填与备注（生成式，不手抄）。"""
    rows = [{"structure": s["name"], "field": f["name"], "type": f["type"],
             "range": f["range"], "required": f["required"], "note": f["note"]}
            for s in STRUCTURES for f in s["fields"]]
    return {"rows": rows, "count": len(rows), "match_schema": len(rows) == FIELD_TOTAL,
            "structures": [s["name"] for s in STRUCTURES],
            "stance_guard": "取舍必须留痕：字段字典与结构定义由同一份数据生成，不会各自漂移"}


def skill_nephron_audit_receipt(events: Sequence[Dict[str, Any]] | None = None) -> Dict[str, Any]:
    """审计回执：规范化本轮回执事件并给 16 位稳定指纹。"""
    evs = [{"kind": str(e.get("kind", "")), "ref": str(e.get("ref", "")),
            "result": str(e.get("result", ""))} for e in (events or [])]
    canon = _canon(evs)
    return {"events": evs, "event_count": len(evs), "fingerprint": _sha16(canon),
            "chain": _sha16(SEAL + canon), "execution": "human_manual", "seal": SEAL,
            "stance_guard": "可逆优先：判定本身也要可回放"}


# ---------------------------------------------------------------- 技能注册
SKILL_NAMES: Tuple[str, ...] = (
    "nephron.page_schema", "nephron.page_validate", "nephron.ledger_record",
    "nephron.ledger_verify", "nephron.reason_codes", "nephron.event_validate",
    "nephron.manifest_build", "nephron.switch_policy", "nephron.collect_plan",
    "nephron.failure_injection_matrix", "nephron.replay_window", "nephron.replay_slots",
    "nephron.replay_inputs", "nephron.replay_timeline", "nephron.replay_determinism",
    "nephron.privacy_policy", "nephron.erase_operation",
    "nephron.generation_fingerprint", "nephron.fingerprint_check",
    "nephron.zero_intrusion_check", "nephron.non_goal_scan",
    "nephron.acceptance_check", "nephron.field_dictionary", "nephron.audit_receipt",
)
SKILL_FNS: Tuple[Any, ...] = (
    skill_nephron_page_schema, skill_nephron_page_validate, skill_nephron_ledger_record,
    skill_nephron_ledger_verify, skill_nephron_reason_codes, skill_nephron_event_validate,
    skill_nephron_manifest_build, skill_nephron_switch_policy, skill_nephron_collect_plan,
    skill_nephron_failure_injection_matrix, skill_nephron_replay_window,
    skill_nephron_replay_slots, skill_nephron_replay_inputs, skill_nephron_replay_timeline,
    skill_nephron_replay_determinism, skill_nephron_privacy_policy,
    skill_nephron_erase_operation, skill_nephron_generation_fingerprint,
    skill_nephron_fingerprint_check, skill_nephron_zero_intrusion_check,
    skill_nephron_non_goal_scan, skill_nephron_acceptance_check,
    skill_nephron_field_dictionary, skill_nephron_audit_receipt,
)


# ---------------------------------------------------------------- 包定义
class NephronPack(DomainPack):
    key = DOMAIN
    name = "肾单位层·P0 认知账本与回放器 NEPHRON"
    description = ("把 NEPHRON P0 的只读观测层落成可判定声明 + 算法层：41 字段结构校验、"
                   "27 理由码 + UNKNOWN 兜底、三档开关的可回放范围、账本只追加核验、"
                   "窗口/槽位/决策输入/时间线四类回放与确定性核验、隐私与擦除、指纹失配拦截；"
                   "0 agent，不加行不加节点，不决策、不落盘、不起线程。")
    skills: List[SkillSpec] = [
        SkillSpec(name=SKILL_NAMES[i], fn=SKILL_FNS[i],
                  description=(SKILL_FNS[i].__doc__ or "").strip().splitlines()[0],
                  tags=["nephron", "ledger", "readonly", "deterministic"],
                  permissions=0)
        for i in range(len(SKILL_FNS))
    ]
    roles: List[Any] = []
    workflows: List[WorkflowSpec] = [
        WorkflowSpec(name="W1_observe",
                     description="观测：结构 → 校验页 → 开关档位 → 采集契约 → 落一条记录（宿主落盘）",
                     steps=["page_schema", "page_validate", "switch_policy",
                            "collect_plan", "ledger_record"]),
        WorkflowSpec(name="W2_manifest",
                     description="清单：事件校验 → 构建窗口构成表",
                     steps=["event_validate", "manifest_build"]),
        WorkflowSpec(name="W3_replay",
                     description="回放：窗口 → 槽位快照 → 决策输入 → 时间线",
                     steps=["replay_window", "replay_slots", "replay_inputs",
                            "replay_timeline"]),
        WorkflowSpec(name="W4_determinism",
                     description="确定性：两次回放哈希比对 → 账本只追加核验",
                     steps=["replay_determinism", "ledger_verify"]),
        WorkflowSpec(name="W5_privacy",
                     description="隐私：规则表 → 受控擦除计划",
                     steps=["privacy_policy", "erase_operation"]),
        WorkflowSpec(name="W6_guard",
                     description="守卫：代际指纹 → 失配拦截 → 非目标扫描",
                     steps=["generation_fingerprint", "fingerprint_check", "non_goal_scan"]),
        WorkflowSpec(name="W7_acceptance",
                     description="验收：零侵入契约 → A1–A8 状态机 → 回执",
                     steps=["zero_intrusion_check", "acceptance_check", "audit_receipt"]),
    ]


def pack_summary() -> Dict[str, Any]:
    """供快速核对：维度不变 / 计数 / 审视与修正 / 非目标 / 零开销声明。"""
    rows = SUBD_TOTAL * SLOTS_PER + SLOTS_RESERVED
    nodes = SUBD_TOTAL * NODES_PER + NODES_COORD
    return {
        "matrix_id": MATRIX_ID, "upstream": [UPSTREAM_ID, UPSTREAM_ID_2],
        "skills": len(SKILL_FNS), "workflows": len(NephronPack.workflows),
        "agents_created": 0, "skill_prefix": "nephron",
        "locks": {"rows_total": rows, "nodes_total": nodes,
                  "rows_ok": rows == LOCK_SIDE, "nodes_ok": nodes == LOCK_MANDALA,
                  "side": LOCK_SIDE, "design_grid": LOCK_DESIGN, "mandala": LOCK_MANDALA,
                  "subdisciplines": SUBD_TOTAL, "slots_per": SLOTS_PER,
                  "slots_reserved": SLOTS_RESERVED, "nodes_per": NODES_PER,
                  "nodes_coord": NODES_COORD},
        "addressing_unchanged": rows == LOCK_SIDE and nodes == LOCK_MANDALA,
        "structures": len(STRUCTURES), "fields": FIELD_TOTAL,
        "event_types": len(EVENT_TYPES), "reason_codes": len(REASON_CODES),
        "code_reviews": len(CODE_REVIEWS), "append_rejects": len(APPEND_REJECTS),
        "non_goals": len(NON_GOALS), "acceptance_items": len(ACCEPTANCE),
        "conflicts": len(CONFLICTS), "conflict_ids": [c["id"] for c in CONFLICTS],
        "fixes": len(FIXES), "refused_ops": len(REFUSED_OPS),
        "threads": 0, "timers": 0, "sleep": False, "disk_writes": 0,
        "deps": 0, "network": False, "api_calls": 0,
        "metaphor": True, "metaphor_note": METAPHOR_NOTE,
        "execution": "human_manual", "seal": SEAL,
    }
