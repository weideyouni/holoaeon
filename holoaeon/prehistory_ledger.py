# -*- coding: utf-8 -*-
"""prehistory_ledger.py —— 史前资产指针总账（V68 / PL-1）

定位：只读扫描、只登记指针，**零搬动、零改写、零删除**。
一件史前资产在本模块眼里只有：路径 + 指纹 + 类别 + 证据等级 + 三态。

三条硬纪律（写进代码，不靠自觉）：
1. 不动原件：本模块只 open(...,"rb") 与 os.scandir/os.walk，无任何写入/改名/删除调用；
2. 不猜归属：归属仓（owner）一律留空由 forge_absorb 复算，本模块只标类别；
3. 活体设施不入史前账：五地同步/镜像仍是活设施，误登记会把 S4 权威源记成"史前遗产"。

指纹口径（诚实标注）：
- 文件：内容 sha256 前 16 位（`sha16`）；
- 目录：**元数据指纹** `(相对路径, 字节数)` 排序后的 sha256 前 16 位（`meta_sha16`），
  不读内容，因此能证明"目录清单未变"，不能证明"文件内容未变"。字段名分开写，避免混用。
"""
import hashlib
import io
import os

LEDGER_SCHEMA = "PREHISTORY-LEDGER-v1"
V68_LEDGER_VERSION = "1.0"

# 类别（与 规划局 V1 分类清单同源，可复算）
CLS_A = "A_关联_不动"
CLS_B = "B_史前记忆"
CLS_C = "C_待定"

# 第一批作业面（B1+B2+B3+B5）；B4 整包挂起（碳基 2026-11-12 裁决）
FIRST_BATCH_SUBS = ("B1_runtime硬核", "B2_矩阵实战化目录", "B3_史前文档", "B5_其他史前资产")
SUSPENDED_SUBS = ("B4_归档与镜像",)

# 活体同步/镜像设施：目前在用，剔除出史前账（碳基裁决）
ACTIVE_INFRA = (
    "vector-sea",
    "向量海云端镜像",
    "向量海·阿赖耶识",
    "向量海同步",
    "向量海_本地库",
    ".sync_state",
    "snapshots",
)

HARD_A_PREFIXES = ("holoaeon", "holmem", "AGENT_FEED_", "HOLOAEON_", "HoloAeon_", "workbuddy-director")
SOFT_A_PREFIXES = (".tmp_v", "_")
SOFT_A_SUFFIXES = ("-source", "-ref", "_source", "_ref")

B_KEYWORDS = (
    "1331", "矩阵实战化", "runtime", "SUPER-MAS", "超级矩阵", "多智能体矩阵",
    "类硅基", "神龟神马", "坍缩", "曼陀罗", "数字分身", "医派", "医药",
    "大典", "通史", "复刻", "实战化", "金刚", "之王", "师",
)
B4_KEYWORDS = ("归档", "镜像", "快照", "snapshots", "sync_state", "向量海", "本地养分", "备份")
B3_KEYWORDS = ("通史", "大典", "讲稿", "逐字稿", "合集", "私塾", "导学", "日课", "晨课", "播客", "全集")

THREE_STATE = ("OBSERVED", "REGISTERED", "VERIFIED")


def _mb(nbytes):
    return round(nbytes / (1024.0 * 1024.0), 3)


def classify(name, kind):
    """名称 + 类型判据 → {cls, sub, why}。优先级：活设施 > HARD_A > B > SOFT_A > C。

    这是**名称初判**，不是内容鉴定；每条都留 why，便于反向质疑。
    """
    if name in ACTIVE_INFRA:
        return {"cls": CLS_A, "sub": "A2_活体同步设施", "why": "活体设施（同步/镜像在用），剔除出史前账"}

    for p in HARD_A_PREFIXES:
        if name.startswith(p):
            sub = "A0_项目本体" if p in ("holoaeon", "holmem", "workbuddy-director") else "A1_关联素材与实验田"
            return {"cls": CLS_A, "sub": sub, "why": "项目本体或关联前缀：%s" % p}

    low = name.lower()
    if any(k in name for k in B4_KEYWORDS):
        return {"cls": CLS_B, "sub": "B4_归档与镜像", "why": "归档/镜像/快照类关键词（默认挂起）"}
    if "_runtime" in low or (low.endswith(".zip") and "runtime" in low):
        return {"cls": CLS_B, "sub": "B1_runtime硬核", "why": "runtime 打包件"}
    if any(k in name for k in B3_KEYWORDS):
        return {"cls": CLS_B, "sub": "B3_史前文档", "why": "史前文档/大部头关键词"}
    if any(k in name for k in B_KEYWORDS):
        if kind == "dir" and ("1331" in name or "矩阵" in name or "实战化" in name):
            return {"cls": CLS_B, "sub": "B2_矩阵实战化目录", "why": "矩阵/实战化目录"}
        return {"cls": CLS_B, "sub": "B5_其他史前资产", "why": "史前语义关键词"}

    if name.startswith(SOFT_A_PREFIXES) or name.endswith(SOFT_A_SUFFIXES):
        return {"cls": CLS_A, "sub": "A1_关联素材与实验田", "why": "素材/实验田/临时目录前缀或后缀"}

    return {"cls": CLS_C, "sub": "C1_未判定", "why": "未命中任何判据"}


def props(path):
    """(文件数, 字节数) —— 递归统计，不读内容。用 scandir 栈遍历，避免 os.walk 的额外开销。"""
    if os.path.isfile(path):
        try:
            return 1, os.path.getsize(path)
        except OSError:
            return 1, 0
    files = 0
    total = 0
    stack = [path]
    while stack:
        cur = stack.pop()
        try:
            with os.scandir(cur) as it:
                for e in it:
                    try:
                        if e.is_dir(follow_symlinks=False):
                            stack.append(e.path)
                        elif e.is_file(follow_symlinks=False):
                            files += 1
                            total += e.stat(follow_symlinks=False).st_size
                    except OSError:
                        pass
        except OSError:
            pass
    return files, total


def fingerprint(path):
    """文件 → 内容 sha16；目录 → 元数据指纹 meta_sha16。返回 (kind, value)。"""
    if os.path.isfile(path):
        h = hashlib.sha256()
        with io.open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 16), b""):
                h.update(chunk)
        return "sha16", h.hexdigest()[:16]
    h = hashlib.sha256()
    rows = []
    for base, _dirs, names in os.walk(path):
        for n in names:
            p = os.path.join(base, n)
            try:
                rows.append((os.path.relpath(p, path).replace("\\", "/"), os.path.getsize(p)))
            except OSError:
                pass
    for rel, size in sorted(rows):
        h.update(("%s|%d\n" % (rel, size)).encode("utf-8"))
    return "meta_sha16", h.hexdigest()[:16]


def scan_top(root):
    """顶层扫描：589 项量级，逐条留 name/kind/files/mb/mtime/csv 对照位。"""
    out = []
    if not os.path.isdir(root):
        return out
    for e in os.scandir(root):
        try:
            st = e.stat(follow_symlinks=False)
        except OSError:
            continue
        kind = "dir" if e.is_dir(follow_symlinks=False) else "file"
        files, nbytes = props(e.path)
        c = classify(e.name, kind)
        out.append({
            "name": e.name, "kind": kind, "files": files, "mb": _mb(nbytes),
            "mtime": int(st.st_mtime),
            "cls": c["cls"], "sub": c["sub"], "why": c["why"],
            "first_batch": c["sub"] in FIRST_BATCH_SUBS,
        })
    return out


def _load_csv(csv_path):
    """读规划局 V1 分类清单做对照（可选）。缺失时返回空 dict，不报错。"""
    import csv
    m = {}
    if not csv_path or not os.path.isfile(csv_path):
        return m
    with io.open(csv_path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            name = row.get("name")
            if name:
                m[name] = {"csv_cls": row.get("cls"), "csv_sub": row.get("sub"),
                           "csv_why": row.get("why")}
    return m


def build_ledger(root, deep=True, csv_path=None, inherit_csv=True):
    """建账。deep=True 时只对第一批作业面（B1/B2/B3/B5）算指纹；挂起项只登记体量。

    inherit_csv=True（默认）：类别一律继承 V1 分类清单，**只把活体设施改判**——
    碳基只裁了「剔除活设施」一条，本模块无权重写整套分类体系。
    无 csv 或 inherit_csv=False 时退回内置判据（供测试与离线场景）。
    """
    entries = scan_top(root)
    v1 = _load_csv(csv_path)

    for x in entries:
        ref = v1.get(x["name"])
        if ref:
            x["csv_cls"] = ref["csv_cls"]
            x["csv_sub"] = ref["csv_sub"]
            x["csv_why"] = ref["csv_why"]
            if x["name"] in ACTIVE_INFRA:
                # 唯一授权改判：活体同步/镜像设施不入史前账
                x["cls"] = CLS_A
                x["sub"] = "A2_活体同步设施"
                x["why"] = "活体设施（同步/镜像在用），碳基 2026-11-12 裁决剔除出史前账"
                x["reclassified"] = True
            elif inherit_csv:
                x["cls"] = ref["csv_cls"]
                x["sub"] = ref["csv_sub"]
                x["why"] = ref["csv_why"]
                x["reclassified"] = False
            else:
                x["reclassified"] = ref["csv_sub"] != x["sub"]
        else:
            x["csv_cls"] = ""
            x["csv_sub"] = ""
            x["csv_why"] = ""
            x["reclassified"] = False

    for x in entries:
        x["first_batch"] = x["sub"] in FIRST_BATCH_SUBS

    first = [x for x in entries if x["first_batch"]]
    if deep:
        for x in first:
            kind, val = fingerprint(os.path.join(root, x["name"]))
            x[kind] = val
            x["evidence"] = "meta+name" if kind == "meta_sha16" else "content+name"
            x["three_state"] = "OBSERVED"
    for x in entries:
        if not x["first_batch"]:
            x["three_state"] = "SUSPENDED"
            x["evidence"] = "name+time"

    summary = {
        "total": len(entries),
        "by_cls": {k: sum(1 for x in entries if x["cls"] == k) for k in (CLS_A, CLS_B, CLS_C)},
        "by_sub": {},
        "first_batch": {"items": len(first), "files": sum(x["files"] for x in first),
                        "mb": round(sum(x["mb"] for x in first), 3)},
        "suspended": {"items": len(entries) - len(first),
                      "mb": round(sum(x["mb"] for x in entries if not x["first_batch"]), 3)},
        "reclassified": sum(1 for x in entries if x.get("reclassified")),
        "csv_compared": bool(v1),
    }
    for x in entries:
        summary["by_sub"][x["sub"]] = summary["by_sub"].get(x["sub"], 0) + 1

    ledger = {
        "schema": LEDGER_SCHEMA,
        "version": V68_LEDGER_VERSION,
        "criteria": {
            "priority": ["ACTIVE_INFRA", "HARD_A", "B", "SOFT_A", "C"],
            "hard_a_prefixes": list(HARD_A_PREFIXES),
            "soft_a_prefixes": list(SOFT_A_PREFIXES),
            "soft_a_suffixes": list(SOFT_A_SUFFIXES),
            "b_keywords": list(B_KEYWORDS),
            "b3_keywords": list(B3_KEYWORDS),
            "b4_keywords": list(B4_KEYWORDS),
            "active_infra": list(ACTIVE_INFRA),
            "first_batch_subs": list(FIRST_BATCH_SUBS),
            "suspended_subs": list(SUSPENDED_SUBS),
            "v1_csv": os.path.basename(csv_path) if csv_path else "",
            "note": "名称+类型初判，非内容鉴定；判据入账以便两次跑逐字节可比",
        },
        "summary": summary,
        "entries": entries,
        "package_sha256": "",
    }
    ledger["package_sha256"] = digest(ledger)
    return ledger


def digest(ledger):
    """账本自校验：对 entries 的稳定序列化取 sha256（不含本字段）。"""
    import json
    payload = {"schema": ledger["schema"], "criteria": ledger["criteria"],
               "summary": ledger["summary"], "entries": ledger["entries"]}
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def verify_ledger(ledger, root):
    """可失败判据。返回 (ok, problems)。"""
    problems = []
    if ledger.get("schema") != LEDGER_SCHEMA:
        problems.append("schema mismatch")

    entries = ledger.get("entries") or []
    if not entries:
        problems.append("entries empty")
        return False, problems

    # 1) 条目守恒：账内条数 == 实际顶层条数（新建文件会 +N，故用"账内每条都能落地"更强）
    for x in entries:
        p = os.path.join(root, x["name"])
        if not os.path.exists(p):
            problems.append("missing on disk: %s" % x["name"])
            continue
        if x.get("first_batch"):
            kind, val = fingerprint(p)
            if x.get(kind) != val:
                problems.append("fingerprint drift: %s (%s)" % (x["name"], kind))

    # 2) 活设施不得进 B 类
    for x in entries:
        if x["cls"] == CLS_B and x["name"] in ACTIVE_INFRA:
            problems.append("active infra misclassified as prehistory: %s" % x["name"])

    # 3) 零搬动：账内不得出现仓库内路径（史前资产都在仓外）
    for x in entries:
        if x["name"].replace("\\", "/").startswith("holoaeon/"):
            problems.append("repo path leaked into prehistory ledger: %s" % x["name"])

    # 4) 自校验
    if ledger.get("package_sha256") != digest(ledger):
        problems.append("package_sha256 mismatch (ledger edited after build)")

    return (not problems), problems
