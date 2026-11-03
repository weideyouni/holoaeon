# -*- coding: utf-8 -*-
"""
全仓 runtime 体检（批 1 · V6.1-B4）
====================================
定位：对 F:\\doubaowork 顶层目录做只读体检，五分类判定：
  - OK   ✅ 能跑：找到 selftest/main 入口，自检运行 exit=0 且输出含 PASS
  - GAP  ⚠️ 能跑但有缺口：自检 exit!=0 / 部分 PASS / 超时 / 缺依赖
  - DOC  📄 仅文档：无代码入口，只有 md
  - NONE ❌ 不可判定：有 py 但无入口且无 README
  - SKIP ⏭ 非本项目工程：_/. 开头目录、第三方开源源码镜像、归档临时类

红线：全程只读；不 pip 安装（缺依赖记 note）；不改目标目录任何文件；
     医学内容不出剂量、不做诊断（本脚本只做工程判定）。
输出：reports/runtime_audit.json + 控制台汇总表（✅/⚠️/📄/❌ 各多少）。
"""
import json
import os
import re
import subprocess
import sys
import io
from datetime import datetime, timezone

ROOT = r"F:\doubaowork"
REPORTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports")
TIMEOUT = 30   # 首轮自检上限（秒）
TIMEOUT_LONG = 240  # 超时后的慢启动复核上限（秒）

# 排除：_/. 开头（临时/隐藏/校验/归档类）+ 第三方开源源码镜像 + 明确非工程关键词
EXCLUDE_WORDS = (
    "source", "历史", "归档", "镜像", "回收", "临时", "下载", "logs", "blobs",
    "chats", "snapshots", "wheels", "scratch", "verify", "校验", "验证",
    "extract", "解压", "备份", "副本", "tmp", "temp", "build", "wfc_index",
    "holoaeon_devtools", "lark_tmp", "new_api_bridge", "vector_sea_sync",
    "vector-sea", "知识星球", "magpie", "mattpocock", "claude", "codebuddy",
    "trae", "zcode", "workbuddy", "hermes", "evolver", "projection",
    "sync_state", "v4_restore", "cmos_skill_build", "evo_skill_build",
    "loader_skill_build", "user_skills", "ingest", "mineru", "cmos-platform",
    "tcm_library", "wmirror_llm_slots", "download", "GITHUB-LEARN",
    "cron迁移", "整机巡检", "全域同步", "飞书同步", "向量海同步",
    "系统升级工程", "系统中枢", "秘密进阶", "wake-seed", "book_digital_avatar",
    "chico", "hevs_iter", "类思维工具工程链", "系统皮肤机制", "三胚层进化",
    "三人行", "奇门日课", "潮起邮差", "对话最伟大的头脑", "导学大典全套合集",
    "合集权威基底", "大黄牡丹汤导学", "陈丽华_episode_drafts", "金庸通史",
    "世界电影导演简史", "计算机语言通史", "人工智能顶层架构三年研学",
    "名医类案晨课", "数字分身全集", "小白数字分身", "道藏讲习录",
    "伤寒温病百年之争", "三矩阵觉醒", "三链反思固化", "周易300万",
    "视频张量", "张量拆解", "经济", "方药频率联动",
)

HOST = "holoaeon"  # 宿主内核，特殊处理：基线 selftest 25/25，不外部运行

BIG_WORDS = ("1600", "1771561", "1331×1331", "108641", "锁数", "全息心跳",
             "曼陀罗", "多智能体", "超级矩阵")

ENTRY_NAMES = ("selftest.py", "selfcheck.py", "run_selfcheck.py", "selftest_main.py",
               "main.py", "app.py", "run.py", "entry.py", "cli.py",
               "selftest_runtime.py", "tests_lite.py")
RUNTIME_DIR_RE = re.compile(r"^(runtime|src|core|engine|sanchang|kernel|matrix|holo)", re.I)


def bj():
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")


def excluded(name):
    low = name.lower()
    if low.startswith(("_", ".")):
        return True
    if low == HOST:
        return False
    if low.endswith("-source") or low.endswith("_source"):
        return True
    return any(w in low for w in EXCLUDE_WORDS)


def read_head(path, n=6000):
    try:
        with io.open(path, encoding="utf-8", errors="replace") as f:
            return f.read(n)
    except Exception:
        return ""


def probe_entries(path):
    """探测目录内自检/主入口：selftest 系优先，其次 main 系，递归 runtime 子目录，最后包级 __main__。"""
    hits = []
    try:
        items = sorted(os.listdir(path))
    except Exception:
        return [], []
    dirs = [d for d in items if os.path.isdir(os.path.join(path, d))]
    files = [f for f in items if os.path.isfile(os.path.join(path, f))]
    self_names = ("selftest.py", "selfcheck.py", "run_selfcheck.py",
                  "selftest_main.py", "selftest_runtime.py", "tests_lite.py")
    for f in files:
        low = f.lower()
        if low in self_names:
            hits.append(("selftest", os.path.join(path, f)))
    if not hits:
        for f in files:
            if f.lower() == "main.py":
                hits.append(("main", os.path.join(path, f)))
                break
    if not hits:
        # runtime/tests 子目录一层
        for d in dirs:
            if RUNTIME_DIR_RE.match(d) or d.lower() in ("tests",):
                sub = os.path.join(path, d)
                try:
                    sfiles = sorted(os.listdir(sub))
                except Exception:
                    continue
                for f in sfiles:
                    low = f.lower()
                    if low in self_names:
                        hits.append(("selftest", os.path.join(sub, f)))
                        break
                if not hits:
                    for f in sfiles:
                        if f.lower() == "main.py":
                            hits.append(("main", os.path.join(sub, f)))
                            break
                if not hits:
                    # runtime/tests 二级
                    try:
                        tfiles = sorted(os.listdir(os.path.join(sub, "tests")))
                    except Exception:
                        tfiles = []
                    for f in tfiles:
                        if f.lower() in self_names:
                            hits.append(("selftest", os.path.join(sub, "tests", f)))
                            break
                if hits:
                    break
    if not hits:
        # 包级 __main__.py：python -m <子包>
        for d in dirs:
            if os.path.isfile(os.path.join(path, d, "__main__.py")) and d.isidentifier():
                hits.append(("pkgmain", os.path.join(path, d)))
                break
    return hits, dirs


def run_selfcheck(cmd, cwd, timeout=TIMEOUT, env=None):
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True,
                           timeout=timeout, shell=False, env=env)
        out = ""
        for b in (r.stdout, r.stderr):
            try:
                out += b.decode("utf-8", errors="replace")
            except Exception:
                pass
        return r.returncode, out
    except subprocess.TimeoutExpired:
        return "TIMEOUT", ""
    except Exception as e:
        return "ERR", str(e)


def audit_dir(name, path):
    rec = {"name": name, "path": path}
    try:
        items = os.listdir(path)
    except Exception as e:
        rec["category"] = "NONE"
        rec["note"] = "listdir 失败: %s" % e
        return rec

    top_py = [f for f in items if f.endswith(".py")]
    top_md = [f for f in items if f.lower().endswith((".md", ".markdown"))]
    readme = os.path.join(path, "README.md") if os.path.isfile(os.path.join(path, "README.md")) else None
    readme_txt = read_head(readme) if readme else ""
    big_found = [w for w in BIG_WORDS if w in readme_txt]
    has_data = os.path.isdir(os.path.join(path, "data"))

    rec["top_py"] = len(top_py)
    rec["top_md"] = len(top_md)
    rec["big_words"] = big_found[:6]
    rec["has_data"] = has_data

    hits, dirs = probe_entries(path)
    if not hits:
        if not top_py:
            rec["category"] = "DOC"
            rec["note"] = "无代码入口（仅文档/台账）"
            return rec
        rec["category"] = "NONE"
        rec["note"] = "有 py %d 个但无 selftest/main 入口" % len(top_py)
        return rec

    kind, entry = hits[0]
    rec["entry"] = os.path.relpath(entry, path)
    rec["entry_kind"] = kind

    python = sys.executable
    if kind == "pkgmain":
        code, out = run_selfcheck([python, "-m", os.path.basename(entry)], path)
    else:
        code, out = run_selfcheck([python, entry], path)

    # 包级相对导入失败 → 兜底 python -m <子包>.selftest（cwd=顶层）
    if isinstance(code, int) and code != 0 and re.search(r"relative import|no known parent package",
                                                        out, re.I):
        rel = os.path.relpath(entry, path)
        parts = rel.split(os.sep)
        if len(parts) >= 2 and parts[0].isidentifier():
            mod = "%s.selftest" % parts[0]
            env = dict(os.environ)
            env["PYTHONPATH"] = path + os.pathsep + env.get("PYTHONPATH", "")
            code2, out2 = run_selfcheck([python, "-m", mod], path, env=env)
            if code2 == 0 and out2:
                code, out = code2, out2

    # 首轮超时 → 慢启动复核一次（长超时）
    if code == "TIMEOUT":
        if kind == "pkgmain":
            code, out = run_selfcheck([python, "-m", os.path.basename(entry)], path, TIMEOUT_LONG)
        else:
            code, out = run_selfcheck([python, entry], path, TIMEOUT_LONG)
        rec["slow_start"] = True
    rec["tail"] = out[-2600:]

    # 真实失败判定：汇总行「失败 N / 组失败 N / FAILED N / [FAIL] / json failures>0」中 N>0 才算
    def fail_count(txt):
        n = 0
        for m in re.finditer(r"失败\s*(\d+)", txt):
            n = max(n, int(m.group(1)))
        for m in re.finditer(r"(\d+)\s*组失败", txt):
            n = max(n, int(m.group(1)))
        for m in re.finditer(r"FAIL(?:ED)?\s*[:=]?\s*(\d+)", txt, re.I):
            n = max(n, int(m.group(1)))
        n += len(re.findall(r"\[FAIL\]", txt))
        for m in re.finditer(r"\"failures\"\s*:\s*(\d+)", txt):
            n = max(n, int(m.group(1)))
        for m in re.finditer(r"\"failed\"\s*:\s*(\d+)", txt):
            n = max(n, int(m.group(1)))
        return n

    if code == 0:
        fc = fail_count(out)
        if fc > 0:
            rec["category"] = "GAP"
            rec["note"] = "自检 exit=0 但失败计数=%d（有缺口）" % fc
        elif (re.search(r"PASS|OK|通过|全绿|success|✓|✅", out, re.I)
              or re.search(r"\"ok\"\s*:\s*true|\"all_pass\"\s*:\s*true|ALL PASS|全部通过", out, re.I)
              or re.search(r"\"failures\"\s*:\s*0", out)
              or re.search(r"\"errors\"\s*:\s*\{\}", out)):
            rec["category"] = "OK"
            rec["note"] = "自检 exit=0 且含 PASS/OK"
            m = re.findall(r"(\d+)\s*/\s*(\d+)", out)
            if m:
                rec["summary"] = m[:3]
        else:
            rec["category"] = "GAP"
            rec["note"] = "自检 exit=0 但输出无可判定 PASS 标记"
    elif code == "TIMEOUT":
        rec["category"] = "GAP"
        rec["note"] = "自检超时 %ds（可能卡死或等待输入）" % TIMEOUT
    elif isinstance(code, str):
        rec["category"] = "GAP"
        rec["note"] = "自检异常: %s" % code
    else:
        reason = "自检 exit=%s" % code
        if re.search(r"ImportError|ModuleNotFoundError", out):
            reason += "（缺依赖/导入失败）"
        rec["category"] = "GAP"
        rec["note"] = reason
    return rec


def main():
    entries = []
    try:
        names = sorted(os.listdir(ROOT))
    except Exception as e:
        print("无法读取 ROOT: %s" % e)
        return 1

    for name in names:
        path = os.path.join(ROOT, name)
        if not os.path.isdir(path):
            continue
        if excluded(name):
            entries.append({"name": name, "path": path,
                            "category": "SKIP", "note": "非本项目工程/镜像/临时"})
            continue
        if name.lower() == HOST:
            entries.append({"name": name, "path": path, "category": "OK",
                            "entry": "holoaeon.selftest",
                            "note": "宿主内核：基线 selftest 25/25（八步写序只读验证复核），不外部运行"})
            continue
        try:
            rec = audit_dir(name, path)
        except Exception as e:
            rec = {"name": name, "path": path, "category": "NONE",
                   "note": "体检异常: %s" % e}
        entries.append(rec)

    cats = {}
    for e in entries:
        cats[e["category"]] = cats.get(e["category"], 0) + 1

    report = {
        "schema_version": "1.1",
        "generated": bj(),
        "batch": "V6.1-B4",
        "root": ROOT,
        "total_dirs": len(entries),
        "categories": cats,
        "entries": entries,
    }
    os.makedirs(REPORTS, exist_ok=True)
    out_path = os.path.join(REPORTS, "runtime_audit.json")
    with io.open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)

    print("=== 全仓 runtime 体检汇总（%s）===" % ROOT)
    print("扫描目录总数: %d（含宿主 holoaeon）" % len(entries))
    for k in ("OK", "GAP", "DOC", "NONE", "SKIP"):
        print("  %s = %d" % ({"OK": "✅ 能跑", "GAP": "⚠️ 有缺口",
                             "DOC": "📄 仅文档", "NONE": "❌ 不可判定",
                             "SKIP": "⏭ 跳过"}[k], cats.get(k, 0)))
    print("\n--- 能跑（OK）清单 ---")
    for e in entries:
        if e["category"] == "OK":
            print("  ✅ %-48s entry=%s %s" % (e["name"], e.get("entry"), e.get("note", "")))
    print("\n--- 有缺口（GAP）清单 ---")
    for e in entries:
        if e["category"] == "GAP":
            print("  ⚠️ %-48s entry=%s %s" % (e["name"], e.get("entry"), e.get("note", "")))
    print("\n输出: %s" % out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
