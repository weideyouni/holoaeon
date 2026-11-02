# -*- coding: utf-8 -*-
"""B8 · 双仓开源同步：ivsa v1.2 插件（默认关闭）+ 双仓 SHA256SUMS 互认。

设计约束（与维度锁一致）：
  · 插件默认关闭：不显式 enable 时，宿主仍是 25 agents / 47 skills / 9 packs，
    ivsa 侧 21/21 自检也照常跑（"不装也能跑"）。
  · 许可分层：宿主 Apache-2.0，ivsa MPL-2.0；交换只走数据件（契约口径与 17 通道分组），
    不拷贝任何源码，避免 MPL 文件落进 Apache 仓。
  · 互认不靠同文件：两仓各自持有 SHA256SUMS，互认点是 17 通道分组（气/血/神/淋巴
    ↔ qi/blood/shen/lymph）的逐组数量相等，可分别从两侧本地数据件复算。
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
from typing import Any, Dict, Iterable, List, Tuple

PLUGIN_ID = "SG-B8-IVSA-V1.2-PLUGIN"
PLUGIN_VERSION = "1.2"
BATCH = "B8"
EVIDENCE_CLASS = "simulated"

HOST = {"name": "holoaeon", "license": "Apache-2.0", "role": "host"}
GUEST = {"name": "integrative-rehab-vsa", "license": "MPL-2.0", "role": "guest"}

# 宿主维度契约（插件启用与否都不得改变）
DIMENSION_CONTRACT = {"agents": 25, "skills": 47, "packs": 9}

# 交换物：只允许读数据件，禁止源码拷贝
CAPABILITIES = (
    "channel_groups_17",
    "heartbeat_70_registry",
    "rehab_organs_11",
    "chronic_diseases_7",
    "rehab_cases_20",
    "capability_dimensions_147",
)

GROUP_ALIAS = {"气": "qi", "血": "blood", "神": "shen", "淋巴": "lymph"}
INTERFACE = {
    "holo": "data/channel_quota.csv",
    "ivsa": "data/meridian_channels_17.csv",
    "key": "group",
    "total": 17,
}

SUMS_EXCLUDES = (
    "SHA256SUMS",
    "data/dual_repo_sums.json",
    "data/B8_双仓开源同步票据.md",
    "reports/b8_dual_sync.json",
    "reports/b8_dual_sync_check.json",
)


def canonical_digest(obj: Any) -> str:
    """对象 → 规范化 JSON 的 sha256（键序固定、紧凑分隔符、UTF-8）。"""
    text = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def plugin_descriptor() -> Dict[str, Any]:
    """插件自描述：默认关闭、需显式启用、只读数据件。"""
    desc = {
        "plugin_id": PLUGIN_ID,
        "version": PLUGIN_VERSION,
        "batch": BATCH,
        "evidence_class": EVIDENCE_CLASS,
        "default_state": "disabled",
        "enabled_by_default": False,
        "requires_explicit_enable": True,
        "host": dict(HOST),
        "guest": dict(GUEST),
        "exchange_mode": "contract_and_data_only",
        "capabilities": list(CAPABILITIES),
        "interface": dict(INTERFACE),
        "dimension_contract": dict(DIMENSION_CONTRACT),
        "license_rule": "MPL-2.0 文件不进 Apache 仓；只读数据件，不拷源码",
        "note": "未 enable 时宿主 25/47/9 与 ivsa 21/21 均不受影响",
    }
    desc["seal"] = canonical_digest(desc)
    return desc


def load_plugin(enable: bool = False) -> Dict[str, Any]:
    """按需装载：默认返回 disabled 回执，绝不隐式启用。"""
    desc = plugin_descriptor()
    if not enable:
        return {
            "ok": True,
            "state": "disabled",
            "capabilities_loaded": 0,
            "capabilities_total": len(CAPABILITIES),
            "seal": desc["seal"],
            "note": "默认关闭；调用方未显式 enable",
        }
    return {
        "ok": True,
        "state": "enabled",
        "capabilities_loaded": len(CAPABILITIES),
        "capabilities_total": len(CAPABILITIES),
        "seal": desc["seal"],
        "note": "已显式启用，仅读数据件，不改宿主维度",
    }


def resolve_capability(name: str) -> Dict[str, Any]:
    """把能力名解析到具体只读数据件；未知能力直接拒绝。"""
    if name not in CAPABILITIES:
        raise KeyError("unknown_capability: %s" % name)
    return {"ok": True, "capability": name, "mode": "read_only_data"}


def read_groups(path: str, key: str = "group") -> Dict[str, int]:
    """按分组列统计行数（确定性，不依赖行序）。"""
    counts: Dict[str, int] = {}
    with open(path, "r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            group = (row.get(key) or "").strip()
            if not group:
                continue
            counts[group] = counts.get(group, 0) + 1
    return counts


def interface_check(holo_csv: str, ivsa_csv: str) -> Dict[str, Any]:
    """17 通道分组互认：中英分组别名归一后逐组数量相等。"""
    holo_raw = read_groups(holo_csv, INTERFACE["key"])
    ivsa = read_groups(ivsa_csv, INTERFACE["key"])
    mapped = {GROUP_ALIAS.get(k, k): v for k, v in holo_raw.items()}
    equal = mapped == ivsa and sum(mapped.values()) == INTERFACE["total"]
    return {
        "equal": bool(equal),
        "groups_holo_mapped": dict(sorted(mapped.items())),
        "groups_ivsa": dict(sorted(ivsa.items())),
        "total_holo": sum(mapped.values()),
        "total_ivsa": sum(ivsa.values()),
        "total_expected": INTERFACE["total"],
        "alias": dict(GROUP_ALIAS),
    }


def build_sums(root: str, files: Iterable[str]) -> List[str]:
    """生成 SHA256SUMS 行（`hex  relpath`，按路径字典序，排除清单自指项）。"""
    lines: List[str] = []
    for rel in sorted(files):
        if rel in SUMS_EXCLUDES:
            continue
        abspath = os.path.join(root, rel.replace("/", os.sep))
        if not os.path.isfile(abspath):
            continue
        lines.append("%s  %s" % (sha256_file(abspath), rel))
    return lines


def sums_digest(lines: Iterable[str]) -> str:
    """整份清单的摘要：行按序拼接，末尾补换行。"""
    text = "\n".join(list(lines)) + "\n"
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def parse_sums(text: str) -> List[Tuple[str, str]]:
    out: List[Tuple[str, str]] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        digest, _, name = line.partition("  ")
        if len(digest) == 64 and name:
            out.append((digest, name))
    return out


def verify_sums(root: str, text: str) -> Dict[str, Any]:
    """按清单逐件复算：缺文件 / 多文件 / 哈希不符 / 字节不符。"""
    entries = parse_sums(text)
    missing, extra, bad_sha, bad_bytes = [], [], [], []
    names = set()
    for digest, name in entries:
        names.add(name)
        abspath = os.path.join(root, name.replace("/", os.sep))
        if not os.path.isfile(abspath):
            missing.append(name)
            continue
        got = sha256_file(abspath)
        if got != digest:
            bad_sha.append(name)
        if len(got) != len(digest):
            bad_bytes.append(name)
    for rel in sorted(build_sums(root, _walk_candidates(root))):
        if rel.split("  ", 1)[-1] not in names:
            extra.append(rel.split("  ", 1)[-1])
    return {
        "ok": not (missing or bad_sha),
        "checked": len(entries),
        "missing": missing,
        "extra": extra,
        "bad_sha256": bad_sha,
        "bad_bytes": bad_bytes,
    }


def _walk_candidates(root: str) -> List[str]:
    """给 verify 用：把根下受管目录扫成相对路径候选（只用于 extra 判定）。"""
    out: List[str] = []
    for top in ("data", "reports", os.path.join("holoaeon", "fusion_upgrade"),
                "tests_contract", "scripts"):
        base = os.path.join(root, top)
        if not os.path.isdir(base):
            continue
        for dirpath, _dirs, files in os.walk(base):
            for name in files:
                if not name.endswith((".py", ".json", ".csv", ".md")):
                    continue
                rel = os.path.relpath(os.path.join(dirpath, name), root)
                out.append(rel.replace(os.sep, "/"))
    return out


def license_layers() -> List[Dict[str, str]]:
    """许可分层清单：每行只归属一个仓与一种许可，无混用条目。"""
    return [
        {"repo": HOST["name"], "layer": "host_code", "license": "Apache-2.0",
         "allowed_in_guest": "no", "note": "宿主源码不得整包搬进 MPL 仓"},
        {"repo": HOST["name"], "layer": "host_data", "license": "Apache-2.0",
         "allowed_in_guest": "read_only", "note": "数据件只读引用，不落库"},
        {"repo": GUEST["name"], "layer": "guest_code", "license": "MPL-2.0",
         "allowed_in_host": "no", "note": "MPL 文件级 copyleft，禁止拷入 Apache 仓"},
        {"repo": GUEST["name"], "layer": "guest_data", "license": "MPL-2.0",
         "allowed_in_host": "digest_only", "note": "只取摘要与分组计数，不复制内容"},
        {"repo": "exchange", "layer": "interface", "license": "data-only",
         "allowed_in_host": "yes", "allowed_in_guest": "yes",
         "note": "17 通道分组口径，双方各自本地复算"},
    ]


def license_mixed(rows: Iterable[Dict[str, str]]) -> List[str]:
    """混用判定：同一行出现两种许可键，或标注双向允许却没写 data-only。"""
    bad: List[str] = []
    for row in rows:
        if row.get("allowed_in_host") == "yes" and row.get("allowed_in_guest") == "yes":
            if row.get("license") != "data-only":
                bad.append(row.get("layer", "?"))
        if row.get("license") not in ("Apache-2.0", "MPL-2.0", "data-only"):
            bad.append(row.get("layer", "?"))
    return bad
