# -*- coding: utf-8 -*-
"""prehistory_family.py —— 史前矩阵族谱（V71 / PL-4）

定位：把「22 个 zip + 194 个目录里谁和谁是一家人」从印象变成**可复算的族谱**。
只读目录清单与 zip 目录项（名字 + 字节数），**不解包内容、不执行任何史前代码、不搬运一个字节**。

实测先行（2026-11-13 本机，非策划案转述）：
  · 194 目录 = 8,277 文件 / 98,484,518 B（**排除隐藏文件**；唯一隐藏件是 薛立斋…/logs/.gitkeep 5 B）
  · 严格骨架签名（清单+大小）下，216 个对象**两两不同** —— 同骨架族只出现在「目录 vs zip」跨域，
    实测 **14 对**双态；域内同骨架 0 对。→ 所以族谱必须分两层，只做一层等于交白卷。

两层结构：
  L1 精确族（twin）：签名完全相同。跨域同骨架 = 同一资产的解包/打包两态，母版/派生关系不成立，只称"双态"。
  L2 近亲族（near）：同一 scope 内**文件名集合** Jaccard ≥ 0.50 的连通分量。
      这才是「母版/派生」真正发生的地方（同一医派的不同版本 = 文件名高度重叠、大小有增删改）。
      证据等级必须写明 `name_jaccard>=0.50`，且 `content_verified=False`——骨架相似不等于内容同源。

三条纪律（写在代码里，不靠人记）：
1. **骨架签名只证形状，不证内容**：字段叫 skeleton，不叫 content。
2. **母版不是最早的那版**：母版 = 同族中骨架最完整者（文件多 → 字节多 → 名字短 → 字典序），规则确定可复算。
   真正的「历史先后」需要时间戳或作者声明，骨架给不出来，就不冒充。
3. **跨域只提示不判血缘**：目录与 zip 同骨架只登记 twin，不判父子。

失败面（任一即红）：
    schema_drift / dir_count / zip_count / file_total / exact_family_count / singleton_count /
    phantom_lineage / master_missing / master_rule_violation / orphan_diff /
    diff_not_reproducible / near_evidence_missing / jaccard_not_reproducible /
    absolute_path_leak / self_digest
"""
import hashlib
import json
import os
import zipfile

FAMILY_SCHEMA = "PREHISTORY-FAMILY-v1"
FAMILY_VERSION = "1.0"

EXPECTED_DIRS = 194
EXPECTED_ZIPS = 22
EXPECTED_FILES = 8277           # 194 个目录的文件总数（排除隐藏件，2026-11-13 实测）
EXPECTED_BYTES = 98484518       # 同上，字节总数
EXPECTED_EXACT_FAMILIES = 14    # 同骨架跨域双态族（实测）
EXPECTED_SINGLETONS = 188       # 216 - 14×2

FILE_CAP = 3000                 # 单对象遍历上限：防某个大目录把一次构建拖死
JACCARD_MIN = 0.5
NEAR_EVIDENCE = "name_jaccard>=0.50"
MASTER_RULE = ("files_desc", "bytes_desc", "name_len_asc", "name_asc")
SIG_RULE = 'sha256(json(sorted([rel_path, bytes])))[:16]'
EXCLUDES_HIDDEN = True

NOTE = ("母版 = 同族骨架最完整者（不是历史上最早的版本）；"
        "L1 跨域双态只因骨架相同、不判父子；L2 近亲族的证据只是文件名 Jaccard，内容同源未经核验；"
        "骨架签名只证清单与大小，不证字节")


# ---------------------------------------------------------------- 指纹原语

def sha16(payload):
    """对已序化的载荷取 sha256 前 16 位。"""
    text = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _rel(base, path):
    rel = os.path.relpath(base, path).replace("\\", "/")
    return "" if rel == "." else rel


def dir_skeleton(path, cap=FILE_CAP):
    """目录骨架：只读名字与大小，不读内容；排除隐藏件与隐藏目录。"""
    items = []
    truncated = False
    for base, dnames, fnames in os.walk(path):
        dnames[:] = sorted(d for d in dnames if not d.startswith("."))
        rel_base = _rel(base, path)
        for f in sorted(fnames):
            if f.startswith("."):
                continue
            rel = (rel_base + "/" + f) if rel_base else f
            try:
                size = os.path.getsize(os.path.join(base, f))
            except OSError:
                size = -1
            items.append((rel, size))
            if len(items) >= cap:
                truncated = True
                break
        if truncated:
            break
    items.sort()
    return {
        "scope": "dir", "items": items, "files": len(items),
        "bytes": sum(s for _, s in items if s > 0), "capped": truncated,
    }


def zip_skeleton(path, cap=FILE_CAP):
    """zip 骨架：只读中央目录（名字 + 未压缩大小），不解包。"""
    items = []
    truncated = False
    with zipfile.ZipFile(path) as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            name = info.filename.replace("\\", "/")
            if name.startswith("__MACOSX/") or name.split("/")[-1].startswith("."):
                continue
            items.append((name, info.file_size))
            if len(items) >= cap:
                truncated = True
                break
    items.sort()
    return {
        "scope": "zip", "items": items, "files": len(items),
        "bytes": sum(s for _, s in items if s > 0), "capped": truncated,
    }


def signature(items):
    """骨架签名：对已排序的 (rel, size) 列表取 sha16。"""
    return sha16([[n, s] for n, s in items])


def skeleton(path, cap=FILE_CAP):
    """按路径类型分派；两条路都只读。"""
    if os.path.isdir(path):
        rec = dir_skeleton(path, cap)
        rec["name"] = os.path.basename(os.path.normpath(path))
    elif os.path.isfile(path) and path.lower().endswith(".zip"):
        rec = zip_skeleton(path, cap)
        rec["name"] = os.path.basename(path)
    else:
        raise ValueError("unsupported artefact: %s" % path)
    rec["sig"] = signature(rec["items"])
    return rec


# ---------------------------------------------------------------- L1 精确族

def cluster(records):
    """按签名分组（**不再按 scope 分域**：同一资产的两态必须能对上）。"""
    groups = {}
    for r in records:
        groups.setdefault(r["sig"], []).append(r)
    return groups


def pick_master(members):
    """同族母版：文件多 → 字节多 → 名字短 → 字典序。确定性，可复算。"""
    return sorted(members, key=lambda r: (-r["files"], -r["bytes"], len(r["name"]), r["name"]))[0]


def diff_matrix(master, child):
    """母版 vs 派生：文件级增 / 删 / 改大小。只比清单，不比内容。"""
    m = {n: s for n, s in master["items"]}
    c = {n: s for n, s in child["items"]}
    added = sorted(n for n in c if n not in m)
    removed = sorted(n for n in m if n not in c)
    resized = sorted([n, m[n], c[n]] for n in c if n in m and m[n] != c[n])
    payload = {"added": added, "removed": removed, "resized": resized}
    return {
        "master": master["name"], "child": child["name"],
        "added": added, "removed": removed, "resized": resized,
        "added_count": len(added), "removed_count": len(removed), "resized_count": len(resized),
        "diff_sha16": sha16(payload),
    }


# ---------------------------------------------------------------- L2 近亲族

def name_set(rec):
    return {n for n, _ in rec["items"]}


def jaccard_sets(a, b):
    """文件名集合 Jaccard；空集返回 0.0（不制造"0/0 相似"的假证据）。"""
    if not a or not b:
        return 0.0
    return len(a & b) / float(len(a | b))


def components(records, threshold=JACCARD_MIN):
    """同 scope 内按文件名 Jaccard 做并查集连通分量。返回 (comps, pairs)。"""
    sets = {r["name"]: name_set(r) for r in records}
    parent = {r["name"]: r["name"] for r in records}

    def find(x):
        root = x
        while parent[root] != root:
            root = parent[root]
        while parent[x] != root:
            parent[x], x = root, parent[x]
        return root

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[ry] = rx

    pairs = []
    for i in range(len(records)):
        for k in range(i + 1, len(records)):
            a, b = records[i], records[k]
            if a["scope"] != b["scope"]:
                continue
            j = jaccard_sets(sets[a["name"]], sets[b["name"]])
            if j >= threshold:
                pairs.append({"a": a["name"], "b": b["name"], "jaccard": round(j, 4)})
                union(a["name"], b["name"])

    comps = {}
    for r in records:
        comps.setdefault(find(r["name"]), []).append(r)
    return comps, sorted(pairs, key=lambda p: (-p["jaccard"], p["a"], p["b"]))


# ---------------------------------------------------------------- 现场扫描

def scan_objects(root):
    """现场对象清单：194 个核心目录（复用 V70 判据，不另立第二份口径）+ 22 个 runtime zip。"""
    from . import prehistory_criteria as pc
    from . import prehistory_contract as pcon
    names, _note = pc.scan_tier_names(root)
    core = pc.match_names(names, pc.CRITERIA_V1)
    dirs = []
    for name in core:
        path = os.path.join(root, name)
        if os.path.isdir(path):
            dirs.append(path)
    zips = pcon.runtime_zips(root)
    return (sorted(dirs, key=lambda p: os.path.basename(p)),
            sorted(zips, key=lambda p: os.path.basename(p)))


# ---------------------------------------------------------------- 构族

def _record(r):
    return {"name": r["name"], "scope": r["scope"], "sig": r["sig"],
            "files": r["files"], "bytes": r["bytes"], "capped": r["capped"],
            "items": [[n, s] for n, s in r["items"]]}


def build_family(root, dir_paths=None, zip_paths=None, cap=FILE_CAP):
    """建族谱。未给显式路径时按现场扫描（194 + 22）。"""
    if dir_paths is None or zip_paths is None:
        d, z = scan_objects(root)
        dir_paths = d if dir_paths is None else dir_paths
        zip_paths = z if zip_paths is None else zip_paths

    records = []
    for p in list(dir_paths) + list(zip_paths):
        rec = skeleton(p, cap)
        records.append(rec)

    # L1 精确族
    groups = cluster(records)
    exact = []
    singles = []
    for sig, members in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        if len(members) < 2:
            singles.extend(members)
            continue
        master = pick_master(members)
        scopes = sorted({m["scope"] for m in members})
        exact.append({
            "family_id": "twin-%s" % sig if len(scopes) > 1 else "clone-%s" % sig,
            "sig": sig, "size": len(members), "scopes": scopes,
            "kind": "twin" if len(scopes) > 1 else "clone",
            "master": master["name"],
            "members": sorted(m["name"] for m in members),
            "diffs": [diff_matrix(master, m) for m in sorted(members, key=lambda r: r["name"]) if m is not master],
        })

    # L2 近亲族
    comps, pairs = components(records)
    near = []
    for root_name, members in sorted(comps.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        if len(members) < 2:
            continue
        master = pick_master(members)
        scope = members[0]["scope"]
        jac_min = min(p["jaccard"] for p in pairs
                      if (p["a"] in {m["name"] for m in members} and p["b"] in {m["name"] for m in members}))
        near.append({
            "family_id": "near-%s-%s" % (scope, sha16(sorted(m["name"] for m in members))),
            "scope": scope, "size": len(members),
            "evidence": NEAR_EVIDENCE, "jaccard_min": jac_min, "content_verified": False,
            "master": master["name"],
            "members": sorted(m["name"] for m in members),
            "diffs": [diff_matrix(master, m) for m in sorted(members, key=lambda r: r["name"]) if m is not master],
        })

    dir_recs = [r for r in records if r["scope"] == "dir"]
    report = {
        "schema": FAMILY_SCHEMA,
        "version": FAMILY_VERSION,
        "criteria": {
            "expected_dirs": EXPECTED_DIRS,
            "expected_zips": EXPECTED_ZIPS,
            "expected_files": EXPECTED_FILES,
            "expected_bytes": EXPECTED_BYTES,
            "expected_exact_families": EXPECTED_EXACT_FAMILIES,
            "expected_singletons": EXPECTED_SINGLETONS,
            "master_rule": list(MASTER_RULE),
            "signature_rule": SIG_RULE,
            "jaccard_min": JACCARD_MIN,
            "near_evidence": NEAR_EVIDENCE,
            "excludes_hidden": EXCLUDES_HIDDEN,
            "file_cap": cap,
        },
        "summary": {
            "dirs": len(dir_recs),
            "zips": len([r for r in records if r["scope"] == "zip"]),
            "files": sum(r["files"] for r in dir_recs),
            "bytes": sum(r["bytes"] for r in dir_recs),
            "exact_families": len(exact),
            "singletons": len(singles),
            "near_families": len(near),
            "largest_exact": max([f["size"] for f in exact] + [0]),
            "largest_near": max([f["size"] for f in near] + [0]),
            "capped_objects": [r["name"] for r in records if r["capped"]],
        },
        "families": exact,
        "near_families": near,
        "near_pairs": pairs,
        "singletons": sorted(r["name"] for r in singles),
        "records": [_record(r) for r in records],
        "note": NOTE,
        "family_digest": "",
    }
    report["family_digest"] = digest(report)
    return report


def digest(report):
    payload = {
        "schema": report.get("schema"), "version": report.get("version"),
        "criteria": report.get("criteria"), "summary": report.get("summary"),
        "families": report.get("families"),
        "near_families": report.get("near_families"),
        "near_pairs": report.get("near_pairs"),
        "singletons": report.get("singletons"),
        "records": report.get("records"), "note": report.get("note"),
    }
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


# ---------------------------------------------------------------- 判据

def _leak(items):
    """绝对路径泄漏：签名项必须是相对路径（不得盘符、不得以 / 开头、不得含反斜杠）。"""
    for name, _ in items:
        if not name or name.startswith("/") or ":" in name or "\\" in name:
            return name
    return None


def recompute_diff(master_rec, child_rec):
    """零 IO 复算：直接用报告里保存的 items。"""
    m = {"scope": master_rec["scope"], "name": master_rec["name"],
         "items": [tuple(x) for x in master_rec["items"]]}
    c = {"scope": child_rec["scope"], "name": child_rec["name"],
         "items": [tuple(x) for x in child_rec["items"]]}
    return diff_matrix(m, c)


def _check_family_block(f, recs, kind, problems):
    members = f.get("members") or []
    for m in members:
        if m not in recs:
            problems.append("%s %s member not in records: %s" % (kind, f.get("family_id"), m))
    if len(members) < 2:
        problems.append("%s %s has fewer than 2 members" % (kind, f.get("family_id")))
    if f.get("master") not in members:
        problems.append("%s %s master missing: %s" % (kind, f.get("family_id"), f.get("master")))

    live = [recs[m] for m in members if m in recs]
    if kind == "exact":
        sigs = {r["sig"] for r in live}
        if len(sigs) != 1:
            problems.append("phantom lineage in %s: %s" % (f.get("family_id"), sorted(sigs)))
        if sigs and f.get("sig") not in sigs:
            problems.append("exact family %s sig mismatch" % f.get("family_id"))

    if live and f.get("master") in recs:
        best = pick_master([{"name": r["name"], "files": r["files"], "bytes": r["bytes"]} for r in live])
        if best["name"] != f.get("master"):
            problems.append("master rule violation in %s: %s vs %s"
                            % (f.get("family_id"), f.get("master"), best["name"]))

    seen = {d["child"] for d in (f.get("diffs") or [])}
    for m in members:
        if m != f.get("master") and m not in seen:
            problems.append("orphan diff in %s: %s" % (f.get("family_id"), m))
    for d in f.get("diffs") or []:
        if d.get("master") != f.get("master"):
            problems.append("diff master mismatch in %s" % f.get("family_id"))
        if d.get("child") in recs and f.get("master") in recs:
            redo = recompute_diff(recs[f["master"]], recs[d["child"]])
            if redo["diff_sha16"] != d.get("diff_sha16"):
                problems.append("diff not reproducible: %s vs %s" % (d.get("master"), d.get("child")))

    if kind == "near":
        if not f.get("evidence"):
            problems.append("near family %s missing evidence" % f.get("family_id"))
        if f.get("content_verified") is not False:
            problems.append("near family %s must declare content_verified=False" % f.get("family_id"))


def check_family(report):
    """可失败判据。返回 (ok, problems)。"""
    problems = []
    if report.get("schema") != FAMILY_SCHEMA:
        problems.append("schema mismatch")

    s = report.get("summary") or {}
    if s.get("dirs") != EXPECTED_DIRS:
        problems.append("dirs %s != %d" % (s.get("dirs"), EXPECTED_DIRS))
    if s.get("zips") != EXPECTED_ZIPS:
        problems.append("zips %s != %d" % (s.get("zips"), EXPECTED_ZIPS))
    if s.get("files") != EXPECTED_FILES:
        problems.append("files %s != %d" % (s.get("files"), EXPECTED_FILES))
    if s.get("bytes") != EXPECTED_BYTES:
        problems.append("bytes %s != %d" % (s.get("bytes"), EXPECTED_BYTES))
    if s.get("exact_families") != EXPECTED_EXACT_FAMILIES:
        problems.append("exact families %s != %d" % (s.get("exact_families"), EXPECTED_EXACT_FAMILIES))
    if s.get("singletons") != EXPECTED_SINGLETONS:
        problems.append("singletons %s != %d" % (s.get("singletons"), EXPECTED_SINGLETONS))
    if s.get("capped_objects"):
        problems.append("objects hit file cap: %s" % s["capped_objects"])

    recs = {r["name"]: r for r in (report.get("records") or [])}

    for r in report.get("records") or []:
        bad = _leak([tuple(x) for x in r.get("items") or []])
        if bad:
            problems.append("%s leaks absolute path in skeleton: %s" % (r["name"], bad))

    for f in report.get("families") or []:
        _check_family_block(f, recs, "exact", problems)
    for f in report.get("near_families") or []:
        _check_family_block(f, recs, "near", problems)

    # 近亲边必须可复算
    for p in report.get("near_pairs") or []:
        a, b = recs.get(p["a"]), recs.get(p["b"])
        if a and b:
            j = jaccard_sets(name_set({"items": [tuple(x) for x in a["items"]]}),
                             name_set({"items": [tuple(x) for x in b["items"]]}))
            if round(j, 4) != p.get("jaccard"):
                problems.append("jaccard not reproducible: %s vs %s" % (p["a"], p["b"]))

    if report.get("family_digest") != digest(report):
        problems.append("family_digest mismatch (report edited after build)")

    return (not problems), problems


def verify_family(report, root=None):
    """现场复验：对象数与签名逐一比对（root 给定时才做磁盘 IO）。"""
    problems = []
    ok, probs = check_family(report)
    problems.extend(probs)

    if root:
        d, z = scan_objects(root)
        recs = {r["name"]: r for r in (report.get("records") or [])}
        if len(d) != len([r for r in recs.values() if r["scope"] == "dir"]):
            problems.append("dir set size changed: %d vs %d"
                            % (len(d), len([r for r in recs.values() if r["scope"] == "dir"])))
        if len(z) != len([r for r in recs.values() if r["scope"] == "zip"]):
            problems.append("zip set size changed: %d vs %d"
                            % (len(z), len([r for r in recs.values() if r["scope"] == "zip"])))
        for p in d:
            name = os.path.basename(os.path.normpath(p))
            rec = recs.get(name)
            if rec is None:
                problems.append("dir not in family: %s" % name)
                continue
            if signature([tuple(x) for x in rec["items"]]) != signature(dir_skeleton(p)["items"]):
                problems.append("dir skeleton drifted: %s" % name)
        for p in z:
            name = os.path.basename(p)
            rec = recs.get(name)
            if rec is None:
                problems.append("zip not in family: %s" % name)
                continue
            if signature([tuple(x) for x in rec["items"]]) != signature(zip_skeleton(p)["items"]):
                problems.append("zip skeleton drifted: %s" % name)
    return (not problems), problems
