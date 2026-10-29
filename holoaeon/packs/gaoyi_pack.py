# -*- coding: utf-8 -*-
"""
gaoyi_pack —— 高译技能（GaoYi）：自然语言 → 高译汇编（HASM）→ 确定性执行
================================================================================
定位：HoloAeon 的第 9 个领域包。把用户在对话窗口输入的自然语言语句，
确定性编译为自定义汇编指令集 HASM（GaoYi Assembly），再由内置虚拟机
在 Kernel 上执行，全程零依赖、离线、可复现。

三层结构：
  1) 编译器  compile_nl(text) -> HasmProgram      自然语言 → 汇编（规则确定性）
  2) 汇编器  parse_assembly(text) -> HasmProgram  汇编文本 → 程序（可反汇编回读）
  3) 虚拟机  GaoyiVm.run(program, kernel)         汇编 → 内核执行 → 回执

HASM 指令集（v1.0，10 条）：
  .src     <原文>                ; 源语句备案
  .intent  <skill>               ; 识别出的意图（目标技能）
  .keyword <k1,k2,...>           ; 命中的匹配关键词
  .select  <agent_id>            ; 派单对象
  .mode    task|<param>          ; 参数模式：task=内容写入任务文本；否则走 ARG
  .load    R0, <任务文本>         ; 装载任务寄存器
  .arg     <name>, <json值>      ; 装载技能参数
  .submit  R0 -> R3              ; 提交内核执行，结果存 R3
  .expect  status=ok             ; 断言回执状态
  .print   <字段>                 ; 输出字段
  .halt                          ; 停机

诚实性声明：编译与执行全部是确定性规则；HASM 是本项目自定义的指令集，
不是任何真实 CPU 的汇编。识别失败时如实报 UNKNOWN，不猜测。
纯标准库。
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .base import DomainPack, RoleSpec, SkillSpec, WorkflowSpec

HASM_VERSION = "1.0"
GAOYI_ID = "GAOYI-HASM-" + HASM_VERSION


# ============================================================ 意图表
# 每条：技能名 / 派单 agent / 关键词（命中计分，越长越强）/ 参数模式
# param="task"：内容随任务文本提交；其余：args[<param>] = 内容
# 规则来源：scripts/全部技能演示.py 44/44 实测结论，一字未改。
@dataclass(frozen=True)
class Intent:
    skill: str
    agent: str
    keywords: Tuple[str, ...]
    param: str = "task"          # "task" 或 具体参数名
    default: Dict[str, Any] = field(default_factory=dict)


INTENTS: Tuple[Intent, ...] = (
    # ---- 写作部 ----
    Intent("word_count",        "writing_editor",   ("字数", "词数统计", "word_count")),
    Intent("readability",       "writing_editor",   ("可读性", "readability")),
    Intent("outline_gen",       "writing_planner",  ("大纲", "outline"), param="topic"),
    Intent("title_brainstorm",  "writing_planner",  ("标题", "起名", "起几个标题"), param="topic"),
    Intent("structure_check",   "writing_editor",   ("结构检查", "检查结构", "结构")),
    # ---- 文献部 ----
    Intent("keyword_extract",   "lit_reader",       ("关键词", "keyword_extract")),
    Intent("extract_abstract",  "lit_reader",       ("摘要", "abstract")),
    Intent("normalize_citation","lit_reviewer",     ("引用格式", "规范引用", "引用规范")),
    Intent("dedup_papers",      "lit_searcher",     ("去重", "dedup"), param="entries"),
    Intent("screen_papers",     "lit_searcher",     ("筛选文献", "文献筛选", "筛文献"),
           param="entries"),
    # ---- 科研部 ----
    Intent("hypothesis_check",  "research_designer",("假设", "hypothesis")),
    Intent("variables_split",   "research_designer",("变量拆分", "拆变量", "变量")),
    Intent("design_experiment", "research_designer",("实验设计", "试验设计")),
    Intent("sample_size",       "research_designer",("样本量", "样本"), param="effect_size",
           default={"effect_size": 0.5}),
    Intent("reproduce_check",   "research_analyzer",("复现", "可复现")),
    # ---- 数据部 ----
    Intent("csv_profile",       "data_analyst",     ("概况", "概览", "csv概况"), param="csv_text"),
    Intent("missing_report",    "data_cleaner",     ("缺失", "missing"), param="csv_text"),
    Intent("basic_stats",       "data_analyst",     ("描述统计", "basic_stats"), param="csv_text"),
    Intent("normalize_column",  "data_cleaner",     ("归一化", "标准化"), param="values"),
    Intent("outlier_detect",    "data_cleaner",     ("离群", "异常值", "outlier"), param="values"),
    # ---- 成长部 ----
    Intent("goal_smart",        "growth_goal_coach",("smart", "目标检查")),
    Intent("habit_plan",        "growth_habit_coach",("习惯")),
    Intent("task_breakdown",    "growth_goal_coach",("拆解", "分解任务", "任务拆解")),
    Intent("weekly_review",     "growth_review_coach",("复盘", "周报")),
    Intent("energy_mapping",    "growth_review_coach",("精力")),
    # ---- 企业部 ----
    Intent("business_model_canvas", "biz_strategist", ("画布", "商业模式")),
    Intent("okr_gen",           "biz_operator",     ("okr",)),
    Intent("swot_analysis",     "biz_strategist",   ("swot",)),
    Intent("kpi_dashboard",     "biz_operator",     ("kpi", "看板"), param="csv_text"),
    Intent("meeting_agenda",    "biz_operator",     ("会议", "议程")),
    Intent("risk_register",     "biz_risk_manager", ("风险")),
    # ---- 量化部 ----
    Intent("returns",           "quant_analyst",    ("收益率",), param="prices"),
    Intent("volatility",        "quant_risk",       ("波动率",), param="returns_s"),
    Intent("sharpe",            "quant_researcher", ("夏普",), param="returns_s"),
    Intent("drawdown",          "quant_risk",       ("回撤",), param="returns_s"),
    # 注意：backtest 必须排在 moving_average 之前——"均线策略回测"两句关键词
    # 同分时按表序裁决，回测优先（实测踩坑：均线先命中会抢走回测任务）。
    Intent("backtest",          "quant_researcher", ("回测",), param="prices"),
    Intent("moving_average",    "quant_analyst",    ("移动平均", "均线"), param="prices",
           default={"window": 3}),
    # ---- 优化部（只在内置基准题上运行） ----
    Intent("golden_section",    "line_searcher",    ("黄金分割",), param="problem",
           default={"problem": "quad1d"}),
    Intent("gradient_descent",  "gradient_solver",  ("梯度下降",), param="problem",
           default={"problem": "quad2d"}),
    Intent("newton_method",     "gradient_solver",  ("牛顿",), param="problem",
           default={"problem": "quad1d"}),
    Intent("conjugate_gradient","gradient_solver",  ("共轭",), param="problem",
           default={"problem": "spd_system"}),
    Intent("simplex_method",    "global_solver",    ("单纯形",), param="problem",
           default={"problem": "lp_factory"}),
    Intent("penalty_method",    "global_solver",    ("惩罚",), param="problem",
           default={"problem": "constrained"}),
    Intent("genetic_algorithm", "global_solver",    ("遗传",), param="problem",
           default={"problem": "binary_max"}),
)

_OPT_PROBLEMS = ("quad1d", "quad2d", "spd_system", "lp_factory", "constrained", "binary_max")
_NUM_RE = re.compile(r"[-+]?\d+\.?\d*")
_KV_RE = re.compile(r"([A-Za-z_\u4e00-\u9fff]+)\s*=\s*([^\s，。；;,]+)")


# ============================================================ 程序与指令
@dataclass
class HasmProgram:
    """一段 HASM 程序：指令 = (操作码, 操作数元组)。"""
    ops: List[Tuple[str, Tuple[str, ...]]] = field(default_factory=list)

    def add(self, op: str, *operands: str) -> None:
        self.ops.append((op, tuple(operands)))

    # ---- 反汇编：程序 → 汇编文本 ----
    def to_text(self, src: str = "", intent: str = "",
                keywords: Tuple[str, ...] = (), agent: str = "",
                param: str = "task") -> str:
        lines = [
            "; " + "=" * 56,
            f"; HASM v{HASM_VERSION} — 高译汇编 (GaoYi Assembly)",
            f"; {GAOYI_ID} · 由高译编译器从自然语言确定性编译生成",
            "; " + "=" * 56,
        ]
        for op, operands in self.ops:
            if op == ".src":
                lines.append(f'.src   "{operands[0]}"')
            elif op == ".intent":
                lines.append(f".intent {operands[0]:<20} ; 识别意图")
            elif op == ".keyword":
                lines.append(f".keyword {operands[0]:<18} ; 命中关键词")
            elif op == ".select":
                lines.append(f".select {operands[0]:<19} ; 派单对象")
            elif op == ".mode":
                lines.append(f".mode   {operands[0]:<19} ; 参数模式")
            elif op == ".load":
                lines.append(f'.load   R0, "{operands[1]}"')
            elif op == ".arg":
                lines.append(f'.arg    {operands[0]}, {operands[1]}')
            elif op == ".submit":
                lines.append(".submit R0 -> R3       ; 提交内核执行")
            elif op == ".expect":
                lines.append(f".expect {operands[0]:<19} ; 断言回执")
            elif op == ".print":
                lines.append(f".print  {operands[0]:<19} ; 输出字段")
            elif op == ".halt":
                lines.append(".halt")
        lines.append("; ==== END OF LISTING ====")
        return "\n".join(lines)

    # ---- 汇编：汇编文本 → 程序 ----
    @staticmethod
    def _strip_comment(line: str) -> str:
        """剥离行注释（; 或 #），但双引号字符串内的 ;/# 视为内容。
        实测踩坑：Markdown/正文载荷里普遍含 #，朴素 split('#') 会截断载荷。"""
        out, in_str, i, n = [], False, 0, len(line)
        while i < n:
            ch = line[i]
            if in_str:
                if ch == "\\" and i + 1 < n:      # 转义字符整体保留
                    out.append(line[i:i + 2])
                    i += 2
                    continue
                if ch == '"':
                    in_str = False
                out.append(ch)
            else:
                if ch == '"':
                    in_str = True
                    out.append(ch)
                elif ch in (";", "#"):
                    break                          # 引号外才是注释起点
                else:
                    out.append(ch)
            i += 1
        return "".join(out)

    @staticmethod
    def parse(text: str) -> "HasmProgram":
        p = HasmProgram()
        for raw in text.splitlines():
            line = HasmProgram._strip_comment(raw).strip()
            if not line:
                continue
            m = re.match(r"^\.(\w+)\s*(.*)$", line)
            if not m:
                raise ValueError(f"无法解析的汇编行：{raw.strip()!r}")
            op, rest = m.group(1), m.group(2).strip()
            if op == "src":
                v = re.match(r'^"(.*)"$', rest)
                p.add(".src", v.group(1) if v else rest)
            elif op == "load":
                parts = rest.split(",", 1)
                v = re.match(r'^\s*"(.*)"\s*$', parts[1]) if len(parts) > 1 else None
                p.add(".load", parts[0].strip(), v.group(1) if v else parts[1].strip())
            elif op == "arg":
                name, val = rest.split(",", 1)
                p.add(".arg", name.strip(), val.strip())
            elif op in ("intent", "keyword", "select", "mode", "expect", "print"):
                p.add("." + op, rest)
            elif op == "submit":
                p.add(".submit")
            elif op == "halt":
                p.add(".halt")
            else:
                raise ValueError(f"未知汇编操作码：.{op}")
        return p


# ============================================================ 编译器
def _split_content(text: str) -> Tuple[str, str]:
    """按首个全角/半角冒号切成（指令部分, 内容部分）；无冒号则内容=全文。"""
    for sep in ("：", ":"):
        if sep in text:
            a, b = text.split(sep, 1)
            return a, b
    return text, text


def _pick_intent(text: str) -> Tuple[Optional[Intent], Tuple[str, ...]]:
    """确定性意图匹配：关键词命中计分（长度加权），同分取表序靠前者。"""
    low = text.lower()
    best, best_score, hit_kws = None, 0, ()
    for it in INTENTS:
        hits = tuple(kw for kw in it.keywords if kw in low)
        if not hits:
            continue
        score = sum(len(kw) for kw in hits)
        if score > best_score:
            best, best_score, hit_kws = it, score, hits
    return best, hit_kws


def compile_nl(text: str) -> Tuple[HasmProgram, dict]:
    """自然语言 → (HASM 程序, 元信息)。确定性：同输入同输出。"""
    text = text.strip()
    instr, content = _split_content(text)
    intent, hits = _pick_intent(text)

    meta: Dict[str, Any] = {"gaoyi_id": GAOYI_ID, "source": text,
                            "keywords": list(hits)}
    p = HasmProgram()
    p.add(".src", text)

    if intent is None:
        meta.update(intent="UNKNOWN", agent="", args={}, param="task")
        p.add(".intent", "UNKNOWN")
        p.add(".halt")
        meta["assembly"] = p.to_text()
        return p, meta

    args: Dict[str, Any] = dict(intent.default)
    if intent.param == "task":
        task_text = text                      # 内容随任务文本提交
    else:
        task_text = text                      # 任务文本保留关键词供匹配
        data = content
        if intent.param in ("prices", "returns_s", "values"):
            nums = _NUM_RE.findall(data.replace("\\n", "\n"))
            if nums:
                args[intent.param] = ",".join(nums)
        elif intent.param == "effect_size":
            nums = _NUM_RE.findall(data)
            if nums:
                args["effect_size"] = float(nums[0])
        elif intent.param == "problem":
            found = next((x for x in _OPT_PROBLEMS if x in data.lower()), None)
            if found:
                args["problem"] = found
        elif intent.param == "entries":
            args["entries"] = data.replace("\\n", "\n")
            if intent.skill == "screen_papers":
                m = re.search(r"含(.+?)的", data)
                if m:
                    kws = re.split(r"或|、|和|,|，", m.group(1))
                    args["keywords"] = ",".join(k.strip() for k in kws if k.strip())
        else:                                  # topic / text / csv_text
            args[intent.param] = data.replace("\\n", "\n")

    # 通用 key=value 覆盖（如 窗口=5 / window=5）
    for k, v in _KV_RE.findall(content):
        if k.lower() in ("window", "窗口"):
            args["window"] = int(float(v))
        elif k in ("keywords",):
            args["keywords"] = v

    meta.update(intent=intent.skill, agent=intent.agent,
                param=intent.param, args=args)
    p.add(".intent", intent.skill)
    p.add(".keyword", ",".join(hits))
    p.add(".select", intent.agent)
    p.add(".mode", intent.param)
    p.add(".load", "R0", task_text)
    for k, v in args.items():
        p.add(".arg", k, json.dumps(v, ensure_ascii=False))
    p.add(".submit")
    p.add(".expect", "status=ok")
    p.add(".print", "output")
    p.add(".halt")
    meta["assembly"] = p.to_text()
    return p, meta


# ============================================================ 虚拟机
class GaoyiVmError(Exception):
    pass


class GaoyiVm:
    """HASM 虚拟机：在给定 Kernel 上逐条执行指令。"""

    def __init__(self, kernel: Any):
        self.k = kernel

    def _ensure_packs(self) -> None:
        """全域保障：若目标 agent 不在场，安装全部领域包（含高译自身）。"""
        from . import all_packs
        for pack in all_packs():
            pack.install(self.k)

    def run(self, program: HasmProgram) -> dict:
        r0_task, r2_args, r3 = "", {}, None
        selected, steps = None, []
        for op, operands in program.ops:
            if op == ".load":
                r0_task = operands[1]
            elif op == ".arg":
                try:
                    r2_args[operands[0]] = json.loads(operands[1])
                except json.JSONDecodeError:
                    r2_args[operands[0]] = operands[1]
            elif op == ".select":
                selected = operands[0]
            elif op == ".submit":
                if not r0_task:
                    raise GaoyiVmError("R0 为空：缺少 .load 任务文本")
                self._ensure_packs()
                to = selected or None
                rep = self.k.submit(r0_task, to=to, args=r2_args or None)
                res = rep["results"][0] if rep["results"] else {}
                r3 = res
                steps.append({"op": ".submit", "to": to, "matched": res.get("matched"),
                              "status": res.get("status")})
            elif op == ".expect":
                key, _, want = operands[0].partition("=")
                got = (r3 or {}).get(key)
                if got != want:
                    raise GaoyiVmError(
                        f".expect 失败：{key}={got!r}（期望 {want}）"
                        f"；err={(r3 or {}).get('err')}")
            elif op == ".print":
                pass
            elif op in (".src", ".intent", ".keyword", ".mode", ".halt"):
                pass
            else:
                raise GaoyiVmError(f"未知指令：{op}")
        if r3 is None:
            raise GaoyiVmError("未执行 .submit，无回执")
        return {
            "gaoyi_id": GAOYI_ID,
            "ok": r3.get("status") == "ok",
            "matched": r3.get("matched"),
            "output": r3.get("output"),
            "err": r3.get("err"),
            "steps": steps,
        }

    # 便捷：汇编文本直跑（汇编 → 执行）
    def run_asm(self, assembly_text: str) -> dict:
        return self.run(HasmProgram.parse(assembly_text))


# ============================================================ 领域包
def _make_fns(kernel: Any) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """闭包绑定 kernel，生成三个技能函数。"""

    def gaoyi_compile(text: str) -> dict:
        """自然语言 → HASM 汇编（只编译，不执行）。"""
        _, meta = compile_nl(text)
        return {"intent": meta["intent"], "agent": meta["agent"],
                "args": meta["args"], "assembly": meta["assembly"]}

    def gaoyi_run(text: str) -> dict:
        """自然语言 → 编译 → 汇编执行 → 回执（全链路）。"""
        program, meta = compile_nl(text)
        if meta["intent"] == "UNKNOWN":
            return {"ok": False, "intent": "UNKNOWN",
                    "err": "无法识别意图：话里没命中任何功能关键词",
                    "hint": "试试带上关键词，如 大纲/SWOT/夏普/归一化/样本量"}
        rep = GaoyiVm(kernel).run(program)
        rep["intent"] = meta["intent"]
        rep["assembly"] = meta["assembly"]
        return rep

    def gaoyi_exec(assembly_text: str) -> dict:
        """HASM 汇编文本 → 直接执行（供人工审查/修改后回放）。"""
        return GaoyiVm(kernel).run_asm(assembly_text)

    return ({"gaoyi_compile": gaoyi_compile,
             "gaoyi_run": gaoyi_run,
             "gaoyi_exec": gaoyi_exec},
            {"inputs": {"text": "str"},
             "inputs_exec": {"assembly_text": "str"}})


class GaoyiPack(DomainPack):
    """高译技能包：NL → HASM → 执行。第 9 个领域包，全域加载。"""
    key = "gaoyi"
    name = "高译技能"
    description = ("把对话自然语言确定性编译为高译汇编（HASM）并由虚拟机在内核上执行；"
                   "HASM 为本项目自定义指令集，非真实 CPU 汇编。")

    def __init__(self) -> None:
        self.skills = []
        self.roles = [RoleSpec("gaoyi_translator", "高译编译器",
                               ["gaoyi_compile", "gaoyi_run", "gaoyi_exec"])]
        self.workflows = [
            WorkflowSpec("gaoyi_pipeline",
                         ["gaoyi_translator"],
                         "自然语言→编译HASM→虚拟机执行→回执"),
        ]

    def install(self, kernel: Any, *, create_agents: bool = True,
                prefix: str = "") -> Dict[str, Any]:
        fns, io = _make_fns(kernel)
        self.skills = [
            SkillSpec("gaoyi_compile", fns["gaoyi_compile"], "高译编译器：自然语言编译为高译汇编",
                      ["gaoyi", "高译", "编译", "nl2asm"], io["inputs"]),
            SkillSpec("gaoyi_run", fns["gaoyi_run"], "高译运行器：自然语言编译并执行全链路",
                      ["gaoyi", "高译", "运行", "执行"], io["inputs"]),
            SkillSpec("gaoyi_exec", fns["gaoyi_exec"], "高译虚拟机：执行高译汇编文本",
                      ["gaoyi", "高译", "汇编", "执行"], io["inputs_exec"]),
        ]
        return super().install(kernel, create_agents=create_agents, prefix=prefix)
