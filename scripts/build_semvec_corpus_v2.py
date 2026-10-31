# -*- coding: utf-8 -*-
"""
build_semvec_corpus_v2.py —— 生成 V2 分层留出语料（5 层 × 47 技能 = 235 条）
================================================================================
为什么要有它：V1 的 12 条意图是从同一批意图里选参数选出来的，属于"同集选定"，
泛化无从证明。V2 把评测语料扩成 5 个**问法层**（原句 / 口语请求 / 客气请求 /
书面指令 / 追加话术），每层覆盖全部 47 个技能各一条，再按层做 5 折评估。

诚实声明（必须一并告知使用者）：
  1) 语料由**代码里的基准问法 + 确定性模板**生成，evidence_class=simulated；
  2) 5 折是"问法风格分层"，不是训练折 —— semvec 索引只在技能自述上 fit，
     评测问句从不进语料，因此不存在训练/测试泄漏，但也不能把 std 读成
     "模型泛化能力"；它读作"路由对问法风格的敏感度"；
  3) 每条问句都保留 expect 标签（技能名），标签来自技能清单明文。

用法：
    python scripts\\build_semvec_corpus_v2.py            # 写 data\\semvec_corpus_v2.json
    python scripts\\build_semvec_corpus_v2.py --check    # 只校验已落盘文件
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

OUT = os.path.join(ROOT, "data", "semvec_corpus_v2.json")

TIERS = ("t0_raw", "t1_casual", "t2_polite", "t3_formal", "t4_appended")

# 47 条基准问法（人工撰写，一问对一技能；不含技能自述原文句式）
BASE = [
    ("backtest", "用历史行情把策略回测一遍"),
    ("basic_stats", "给这列数据算均值和标准差"),
    ("business_model_canvas", "画一张商业模式画布"),
    ("conjugate_gradient", "用共轭梯度法解线性方程组"),
    ("csv_profile", "看一下这个 CSV 的列类型和分布"),
    ("dedup_papers", "把论文列表去重"),
    ("design_experiment", "给实验设计一个方案模板"),
    ("drawdown", "最大回撤是多少"),
    ("energy_mapping", "做一张精力映射表"),
    ("extract_abstract", "从这篇论文里抽取式摘要"),
    ("gaoyi_compile", "把这段话编译成高译汇编"),
    ("gaoyi_exec", "执行这段高译汇编"),
    ("gaoyi_run", "自然语言直接编译并运行高译"),
    ("genetic_algorithm", "用遗传算法做群体进化"),
    ("goal_smart", "检查这个目标是否符合 SMART"),
    ("golden_section", "用黄金分割法做一维搜索"),
    ("gradient_descent", "用梯度下降求解"),
    ("habit_plan", "制定习惯养成计划"),
    ("hypothesis_check", "检验这个假设能不能被检验"),
    ("keyword_extract", "提取关键词"),
    ("kpi_dashboard", "做一个 KPI 看板"),
    ("meeting_agenda", "排一份会议议程"),
    ("missing_report", "出一份缺失值报告"),
    ("moving_average", "算移动平均"),
    ("newton_method", "用牛顿法做二阶加速"),
    ("normalize_citation", "把引用格式规范化"),
    ("normalize_column", "把这列数据归一化"),
    ("okr_gen", "生成一份 OKR"),
    ("outlier_detect", "检测离群值"),
    ("outline_gen", "生成文章结构大纲"),
    ("penalty_method", "用惩罚函数做约束优化"),
    ("readability", "算可读性指标"),
    ("reproduce_check", "出一份可复现性清单"),
    ("returns", "算收益率序列"),
    ("risk_register", "建一个风险登记表"),
    ("sample_size", "估算实验样本量"),
    ("screen_papers", "筛选相关文献"),
    ("sharpe", "计算夏普比率"),
    ("simplex_method", "用单纯形法解线性规划"),
    ("structure_check", "检查文章结构"),
    ("swot_analysis", "做一次 SWOT 分析"),
    ("task_breakdown", "拆解一下这个任务"),
    ("title_brainstorm", "想几个标题候选"),
    ("variables_split", "把变量拆分"),
    ("volatility", "算年化波动率"),
    ("weekly_review", "把一周工作整理成周报"),
    ("word_count", "统计字数"),
]


def variants(query: str) -> dict:
    """同一问句的 5 种问法层（确定性、无随机）。"""
    return {
        "t0_raw": query,
        "t1_casual": "帮我" + query,
        "t2_polite": "能不能" + query + "？",
        "t3_formal": "请对以下内容执行：" + query,
        "t4_appended": query + "，给出结果",
    }


def build() -> dict:
    items = []
    for expect, query in BASE:
        for tier in TIERS:
            text = variants(query)[tier]
            items.append({"id": "%s@%s" % (expect, tier), "tier": tier,
                          "query": text, "expect": expect,
                          "evidence_class": "simulated"})
    payload = {
        "version": "v2",
        "generated_by": "scripts/build_semvec_corpus_v2.py",
        "evidence_class": "simulated",
        "skills": len(BASE),
        "tiers": list(TIERS),
        "count": len(items),
        "note": ("5 个问法层 × 47 技能；分层是风格分层，不是训练折；"
                 "semvec 索引只在技能自述上 fit，问句从不进语料。"),
        "items": items,
    }
    body = json.dumps(payload, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"))
    payload["corpus_sha"] = hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]
    return payload


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if "--check" in argv:
        if not os.path.isfile(OUT):
            print("missing: %s" % OUT)
            return 1
        with open(OUT, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
        print("count=%d skills=%d tiers=%d corpus_sha=%s"
              % (payload["count"], payload["skills"], len(payload["tiers"]),
                 payload.get("corpus_sha")))
        return 0 if payload["count"] == 235 else 1

    payload = build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False, indent=2,
                            sort_keys=True))
        fh.write("\n")
    print("count=%d skills=%d tiers=%d corpus_sha=%s"
          % (payload["count"], payload["skills"], len(payload["tiers"]),
             payload["corpus_sha"]))
    print("written: %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
