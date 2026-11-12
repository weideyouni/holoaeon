# -*- coding: utf-8 -*-
"""
miniapp_prompt —— P4 小程序提示词工厂（V64 · 产品线 P4 锚点落地）
================================================================================
挂账原文（V63 product_lines）：
  total 10 / anchored 9 / pending 1，
  pending_item = 「P4 小程序提示词（待造位，锚未落，如实声明）」。

本批做法：把 P4 造成**确定性生成器**，而不是写一段样例文案充数。
  · 输入：业务域配方（domain）+ 实体/字段扩展；
  · 输出：可直接交给 AI 或开发者落地的小程序提示词包——
    产品定位 / 页面清单（每页组件+数据字段+交互事件）/ 数据模型 /
    接口约定 / 审核与合规清单 / 交付验收清单；
  · 三套内置配方（医疗康复随访 / 农业基地台账 / 课程学习打卡）都是
    结构化模板，不含任何真实患者或机构数据。

纪律：
  · 零网络、零随机、零墙钟——同输入逐字节同输出（可进测试与哈希）；
  · 不生成任何医疗诊疗结论或剂量建议（医疗域只做「随访记录/提醒/宣教」骨架，
    合规项里强制写明「不得在小程序内做诊断与处方」）；
  · 提示词是**骨架**，不承诺「一键生成可上线小程序」——上线须资质与审核。
"""
from __future__ import annotations

import io
import json
import os
from typing import Any, Dict, List, Optional

SEAL = "潮起开门，潮落闭嘴"
SCHEMA_VERSION = "MINIAPP-PROMPT-v1.0"
DATA_OUT_NAME = "miniapp_prompt_recipes.json"

# 通用页面骨架（小程序五页法：首页 / 列表 / 详情 / 表单 / 我的）
BASE_PAGES: tuple = (
    {"key": "P0", "name": "首页", "components": ["swiper 轮播", "grid 功能入口", "notice-bar 公告"],
     "fields": ["banner_list", "entry_list", "notice"], "events": ["onLoad", "onEntryTap"]},
    {"key": "P1", "name": "列表页", "components": ["search-bar 搜索", "filter-tabs 筛选", "list 列表", "load-more 加载更多"],
     "fields": ["keyword", "filter", "items[]", "page", "has_more"], "events": ["onSearch", "onFilterChange", "onReachBottom"]},
    {"key": "P2", "name": "详情页", "components": ["rich-text 富文本", "action-bar 操作栏", "share-button 分享"],
     "fields": ["id", "title", "content", "attachments[]", "meta"], "events": ["onLoad(id)", "onActionTap", "onShareAppMessage"]},
    {"key": "P3", "name": "表单页", "components": ["form 表单", "picker 选择器", "uploader 上传", "submit-button 提交"],
     "fields": ["form_schema[]", "draft", "files[]"], "events": ["onInput", "onSubmit", "onUpload"]},
    {"key": "P4", "name": "我的", "components": ["avatar 头像", "cell 单元格", "settings 设置"],
     "fields": ["user", "records[]", "settings"], "events": ["onLoad", "onLogin"]},
)

# 合规基线（所有配方共用；医疗域另有加严项）
BASE_COMPLIANCE: tuple = (
    "隐私政策与用户协议必须在首次启动弹窗确认（wx.getPrivacySetting）",
    "手机号/位置/相册等敏感能力须用户显式授权，拒绝后功能须可降级",
    "不得诱导分享、不得强制关注、不得虚假承诺（微信审核红线）",
    "数据最小化：只采集业务必需字段，留痕可删除",
    "上线前需选择正确服务类目并备齐资质，类目不符会被驳回",
)

RECIPES: tuple = (
    {
        "domain": "rehab-followup", "label": "康复随访（医疗加严）",
        "positioning": "面向康复患者的随访记录与提醒工具（只记录、不诊断）",
        "entities": ["患者档案（脱敏）", "随访记录", "量表评分", "复诊提醒", "宣教内容"],
        "extra_pages": [
            {"key": "P5", "name": "随访记录页",
             "components": ["timeline 时间轴", "score-card 评分卡", "photo 患处照片（可选）"],
             "fields": ["record_id", "visit_date", "score", "photos[]", "note"],
             "events": ["onLoad(patient_id)", "onSave", "onRemindSet"]},
            {"key": "P6", "name": "提醒设置页",
             "components": ["calendar 日历", "switch 开关", "subscribe-message 订阅消息"],
             "fields": ["remind_at", "channel", "enabled"],
             "events": ["onRemindChange", "onSubscribe"]},
        ],
        "compliance_extra": [
            "医疗类目须具备相应资质；小程序内不得出现诊断结论、处方、剂量建议",
            "患处照片属敏感信息，须单独授权与加密存储，且可一键删除",
            "随访量表若涉版权（如 ODI/JOA），须取得授权或改用自有量表",
        ],
        "acceptance": ["随访记录可增删改查且留痕", "提醒可订阅可关闭", "敏感信息授权与删除闭环"],
    },
    {
        "domain": "farm-ledger", "label": "农业基地台账",
        "positioning": "面向基地管理员的种植/投入品/采收台账工具",
        "entities": ["地块", "作物", "投入品（肥料/农药）", "作业记录", "采收批次"],
        "extra_pages": [
            {"key": "P5", "name": "地块地图页",
             "components": ["map 地图", "marker 标记", "polygon 边界"],
             "fields": ["plot_id", "geo", "area_mu", "crop"],
             "events": ["onLoad", "onPlotTap", "onBoundaryEdit"]},
            {"key": "P6", "name": "投入品登记页",
             "components": ["scan 扫码", "form 表单", "stepper 步进器"],
             "fields": ["product", "batch_no", "amount", "unit", "operator", "ts"],
             "events": ["onScan", "onSubmit"]},
        ],
        "compliance_extra": [
            "农药登记须记录通用名/剂型/登记证号，不得省略（追溯要求）",
            "地图能力须申请位置权限并说明用途",
        ],
        "acceptance": ["地块-作物-投入品-采收四表可关联查询", "扫码登记可用", "导出月度台账"],
    },
    {
        "domain": "course-checkin", "label": "课程学习打卡",
        "positioning": "面向学员的课程学习与打卡工具",
        "entities": ["课程", "章节", "打卡记录", "作业", "证书"],
        "extra_pages": [
            {"key": "P5", "name": "章节学习页",
             "components": ["video 视频", "audio 音频", "progress 进度条"],
             "fields": ["course_id", "chapter_id", "progress", "duration"],
             "events": ["onPlay", "onProgress", "onFinish"]},
            {"key": "P6", "name": "打卡日历页",
             "components": ["calendar 日历", "badge 徽章", "share-card 分享卡"],
             "fields": ["checkin_list[]", "streak", "badge_list[]"],
             "events": ["onCheckin", "onShare"]},
        ],
        "compliance_extra": [
            "课程内容版权须自有或已授权；不得搬运他人课程",
            "未成年人使用须有监护人同意路径，且不得设置付费诱导",
        ],
        "acceptance": ["章节进度可续播", "打卡连续天数正确", "证书生成可下载"],
    },
)

API_CONTRACT: Dict[str, Any] = {
    "auth": "wx.login → code → 后端换 session（openid 不下发前端）",
    "request": "统一 wx.request 封装：base_url + token + 重试 1 次 + 错误码映射",
    "pagination": "page/page_size + has_more；列表接口必须支持游标或页码二选一并写死",
    "upload": "wx.uploadFile → 对象存储 → 返回 file_id（不存原始路径）",
    "subscribe": "订阅消息模板须先申请，前端只做 requestSubscribeMessage",
}


def _pages_for(recipe: Dict[str, Any]) -> List[Dict[str, Any]]:
    pages = [dict(p) for p in BASE_PAGES]
    for p in recipe.get("extra_pages") or []:
        pages.append(dict(p))
    return pages


def build_prompt(domain: str, extras: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """按配方生成小程序提示词包（确定性，纯结构）。"""
    recipe = None
    for r in RECIPES:
        if r["domain"] == domain:
            recipe = r
            break
    if recipe is None:
        raise KeyError("未登记的小程序配方：{}（可选 {}）".format(
            domain, ", ".join(r["domain"] for r in RECIPES)))
    ex = extras or {}
    pages = _pages_for(recipe)
    if ex.get("extra_entities"):
        entities = list(recipe["entities"]) + list(ex["extra_entities"])
    else:
        entities = list(recipe["entities"])
    compliance = list(BASE_COMPLIANCE) + list(recipe.get("compliance_extra") or [])
    prompt = {
        "schema": SCHEMA_VERSION,
        "domain": domain,
        "label": recipe["label"],
        "positioning": recipe["positioning"],
        "platform": "微信小程序（原生 WXML/WXSS/JS，或 Taro 跨端）",
        "entities": entities,
        "pages": pages,
        "api_contract": dict(API_CONTRACT),
        "compliance": compliance,
        "acceptance": list(recipe.get("acceptance") or []),
        "style_guide": {
            "primary_color": "#1F6F6B",
            "font": "系统默认（PingFang SC / 思源黑体）",
            "spacing": "8pt 栅格，卡片圆角 12rpx，主按钮高度 88rpx",
            "a11y": "正文 ≥ 28rpx；对比度 ≥ 4.5:1；所有图标有文字标签",
        },
        "do_not": [
            "不生成诊疗结论、处方、剂量",
            "不虚构资质与备案号",
            "不内置第三方统计 SDK（须显式声明）",
        ],
        "seal": SEAL,
    }
    return prompt


def render_markdown(prompt: Dict[str, Any]) -> str:
    """把提示词包渲染成可直接投喂 AI/开发者的 Markdown（确定性排版）。"""
    lines = [
        "# 小程序提示词包 · {}".format(prompt["label"]),
        "",
        "> 域：`{}`　平台：{}".format(prompt["domain"], prompt["platform"]),
        "",
        "## 一、产品定位",
        prompt["positioning"],
        "",
        "## 二、核心实体",
    ]
    for e in prompt["entities"]:
        lines.append("- {}".format(e))
    lines += ["", "## 三、页面清单（{} 页）".format(len(prompt["pages"]))]
    for p in prompt["pages"]:
        lines.append("### {} {}".format(p["key"], p["name"]))
        lines.append("- 组件：{}".format("、".join(p["components"])))
        lines.append("- 数据字段：{}".format("、".join(p["fields"])))
        lines.append("- 交互事件：{}".format("、".join(p["events"])))
    lines += ["", "## 四、接口约定"]
    for k, v in prompt["api_contract"].items():
        lines.append("- **{}**：{}".format(k, v))
    lines += ["", "## 五、审核与合规（逐条自查）"]
    for c in prompt["compliance"]:
        lines.append("- [ ] {}".format(c))
    lines += ["", "## 六、交付验收"]
    for a in prompt["acceptance"]:
        lines.append("- [ ] {}".format(a))
    lines += ["", "## 七、视觉与可及性"]
    for k, v in prompt["style_guide"].items():
        lines.append("- **{}**：{}".format(k, v))
    lines += ["", "## 八、禁止项"]
    for d in prompt["do_not"]:
        lines.append("- {}".format(d))
    lines += ["", "---", prompt["seal"], ""]
    return "\n".join(lines)


def check() -> Dict[str, Any]:
    """结构自检：三配方齐全、每配方页面 ≥5、字段与事件非空、渲染非空。"""
    problems: List[str] = []
    if len(RECIPES) != 3:
        problems.append("配方数 != 3（实 {}）".format(len(RECIPES)))
    for r in RECIPES:
        p = build_prompt(r["domain"])
        if len(p["pages"]) < 5:
            problems.append("{} 页面不足 5".format(r["domain"]))
        for pg in p["pages"]:
            if not pg["components"] or not pg["fields"] or not pg["events"]:
                problems.append("{} 页 {} 字段/组件/事件有空白".format(r["domain"], pg["key"]))
        if not p["compliance"] or not p["acceptance"]:
            problems.append("{} 合规/验收清单为空".format(r["domain"]))
        md = render_markdown(p)
        if len(md) < 800:
            problems.append("{} 渲染文本过短（{} 字符）".format(r["domain"], len(md)))
        # 确定性：两次生成逐字节相同
        if json.dumps(p, ensure_ascii=False, sort_keys=True) != \
           json.dumps(build_prompt(r["domain"]), ensure_ascii=False, sort_keys=True):
            problems.append("{} 生成不确定".format(r["domain"]))
    return {"schema": SCHEMA_VERSION, "recipes": len(RECIPES),
            "problems": problems, "verdict": "PASS" if not problems else "FAIL"}


def build_ledger() -> Dict[str, Any]:
    return {
        "schema": SCHEMA_VERSION,
        "batch": "V64-HANGOVER-ZERO",
        "dom": "P4 小程序提示词工厂（产品线 P4 锚点）",
        "hangover_origin": "V63 product_lines：P4 待造位、锚未落",
        "page_framework": list(BASE_PAGES),
        "compliance_baseline": list(BASE_COMPLIANCE),
        "api_contract": dict(API_CONTRACT),
        "recipes": [{k: v for k, v in r.items()} for r in RECIPES],
        "check": check(),
        "seal": SEAL,
    }


def write_ledger(path: Optional[str] = None) -> str:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = path or os.path.join(root, "data", DATA_OUT_NAME)
    io.open(out, "w", encoding="utf-8", newline="\n").write(
        json.dumps(build_ledger(), ensure_ascii=False, indent=1) + "\n")
    return out


def main(argv: Optional[List[str]] = None) -> int:
    import sys
    argv = list(argv if argv is not None else sys.argv[1:])
    if not argv:
        print("用法：python -m holoaeon.miniapp_prompt check | recipes | build <domain> | md <domain> | ledger")
        return 1
    cmd = argv[0]
    if cmd == "check":
        rep = check()
        print(json.dumps(rep, ensure_ascii=False, indent=1))
        return 0 if rep["verdict"] == "PASS" else 1
    if cmd == "recipes":
        for r in RECIPES:
            print("{:20s} {}".format(r["domain"], r["label"]))
        return 0
    if cmd in ("build", "md"):
        if len(argv) < 2:
            print("需要 domain 参数：{} <domain>".format(cmd))
            return 1
        p = build_prompt(argv[1])
        if cmd == "md":
            print(render_markdown(p))
        else:
            print(json.dumps(p, ensure_ascii=False, indent=1))
        return 0
    if cmd == "ledger":
        print("台账已写：{}".format(write_ledger()))
        return 0
    print("未知命令：{}".format(cmd))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
