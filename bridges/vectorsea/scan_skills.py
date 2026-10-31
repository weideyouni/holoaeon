# -*- coding: utf-8 -*-
"""扫描向量海技能挂载点(.user_skills)，解析 SKILL.md frontmatter 与工具层，输出目录 JSON。
纯标准库，确定性。用法: python scan_skills.py <root> <out_json>"""
import json
import os
import re
import sys

FRONT_RE = re.compile(r"^---\s*$", re.M)
NAME_RE = re.compile(r"^name\s*:\s*(.+?)\s*$", re.M)
DESC_RE = re.compile(r"^description\s*:\s*(.+?)\s*$", re.M | re.S)


def parse_frontmatter(text):
    m = FRONT_RE.search(text)
    if not m:
        return None, None
    fm_end = FRONT_RE.search(text, m.end())
    if not fm_end:
        return None, None
    fm = text[m.end():fm_end.start()]
    name_m = NAME_RE.search(fm)
    desc_m = DESC_RE.search(fm)
    name = name_m.group(1).strip() if name_m else None
    desc = desc_m.group(1).strip() if desc_m else None
    return name, desc


def scan(root):
    entries = []
    for d in sorted(os.listdir(root)):
        dpath = os.path.join(root, d)
        if not os.path.isdir(dpath):
            continue
        skill_md = os.path.join(dpath, "SKILL.md")
        if not os.path.isfile(skill_md):
            entries.append({"dir": d, "skill_md": False, "name": None,
                            "description": None, "has_tools": False,
                            "tool_files": [], "has_data": False,
                            "has_references": False, "note": "no SKILL.md"})
            continue
        with open(skill_md, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
        name, desc = parse_frontmatter(text)
        has_tools = os.path.isdir(os.path.join(dpath, "tools"))
        tool_files = []
        if has_tools:
            for sub in sorted(os.listdir(os.path.join(dpath, "tools"))):
                if sub.lower().endswith((".py", ".sh", ".ps1", ".js", ".rb")):
                    tool_files.append(os.path.join("tools", sub))
        has_data = os.path.isdir(os.path.join(dpath, "data"))
        has_refs = os.path.isdir(os.path.join(dpath, "references"))
        # 根目录下的可执行脚本也算工具层
        for sub in sorted(os.listdir(dpath)):
            if sub.lower().endswith((".py", ".sh", ".ps1", ".js")):
                tool_files.append(sub)
        entries.append({
            "dir": d, "skill_md": True, "name": name, "description": desc,
            "has_tools": bool(tool_files), "tool_files": tool_files,
            "has_data": has_data, "has_references": has_refs, "note": "ok",
        })
    return entries


def main():
    root, out = sys.argv[1], sys.argv[2]
    entries = scan(root)
    names = [e["name"] for e in entries if e["name"]]
    dups = sorted({n for n in names if names.count(n) > 1})
    stats = {
        "root": root,
        "total_dirs": len(entries),
        "with_skill_md": sum(1 for e in entries if e["skill_md"]),
        "no_skill_md": sum(1 for e in entries if not e["skill_md"]),
        "with_name": sum(1 for e in entries if e["name"]),
        "with_description": sum(1 for e in entries if e["description"]),
        "has_tools": sum(1 for e in entries if e["has_tools"]),
        "has_data": sum(1 for e in entries if e["has_data"]),
        "has_references": sum(1 for e in entries if e["has_references"]),
        "dup_names": dups,
        "dup_name_count": len(dups),
    }
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"stats": stats, "entries": entries}, f, ensure_ascii=False, indent=1)
    print(json.dumps(stats, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
