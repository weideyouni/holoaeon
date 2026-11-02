# -*- coding: utf-8 -*-
"""
Guard —— HoloAeon 守卫/策略边界（原"皮肤"）
================================================================================
Guard 是系统的语义级边界：所有进入/离开的信封都经过 L1-L8 串联检查。
每层职责单一，返回 (action, reason)；action ∈ allow | advise | block。
任一 block 即拦截；advise 放行但记入审计。

层级职责（工程属性，非生物学）：
  L1 结构完整   sender/topic/recipient 非空
  L2 体积限制   payload 序列化大小不超限
  L3 危险模式   注入/危险调用/密钥读取等模式
  L4 权限匹配   操作所需权限 ≤ 主体权限
  L5 越权/失真  未授权身份（unauthorized）/ 校验失真（garbled）
  L6 元数据     必要字段与 mode 合法
  L7 审计       记录出入站（不拦截）
  L8 一致性     trace 与消息体一致

纯标准库。
"""
from __future__ import annotations

import json
import time
import unicodedata
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

from .envelope import Envelope
from .spec import GuardConfig

ALLOW = "allow"
ADVISE = "advise"
BLOCK = "block"

# 危险模式（通用：明显的代码执行/越权/密钥读取）
DANGER_PATTERNS = (
    "__import__", "os.system", "subprocess", "eval(", "exec(",
    "open('/etc", "open(\"/etc", "rm -rf", "shutil.rmtree",
    ".env", "id_rsa", "access_token", "private_key",
)

MAX_PAYLOAD_BYTES = 1_000_000

# L3 归一化（V5.2 [golden]）：子串黑名单只能挡「原样复制」的攻击串。
# 这里补三层确定性归一，只做「等价折叠」，不新增语义判断：
#   NFKC           全角/兼容字符 → 半角（ｅｖａｌ → eval）
#   零宽字符剥离    \u200b-\u200d / \ufeff / \u00ad
#   同形字折叠     Cyrillic / Greek 里长得像拉丁字母的那几个
# 以及一层「拼接折叠」：把非字母数字全部删掉后再比一次，挡 "os . system"、"ev al(" 这类。
# 已知边界：拼接折叠只对紧凑长度 ≥5 的模式生效（eval/exec 这类 4 字符短词仅靠前三层），
# 这是刻意取舍——否则 "env"、"exec" 会在正常文本里大面积误杀。
ZERO_WIDTH = {ord(c): None for c in "\u200b\u200c\u200d\u2060\ufeff\u00ad"}
HOMOGLYPHS = str.maketrans({
    "а": "a", "е": "e", "о": "o", "р": "p", "с": "c", "у": "y", "х": "x",
    "і": "i", "ј": "j", "ѕ": "s",
    "ο": "o", "α": "a", "ρ": "p", "ν": "v", "κ": "k", "τ": "t", "υ": "u",
})
MIN_COMPACT_PATTERN = 5


def normalize_for_match(text: str) -> str:
    """NFKC + 零宽剥离 + 同形字折叠 + 小写。"""
    t = unicodedata.normalize("NFKC", text).translate(ZERO_WIDTH).lower()
    return t.translate(HOMOGLYPHS)


def compact_for_match(text: str) -> str:
    """在归一化基础上只留字母数字（含中日韩），用于挡分隔符拼接。"""
    return "".join(ch for ch in normalize_for_match(text) if ch.isalnum())


@dataclass
class Verdict:
    action: str
    layer: str
    reason: str = ""

    def to_dict(self) -> dict:
        return {"action": self.action, "layer": self.layer, "reason": self.reason}


LayerFn = Callable[[Envelope], Optional[Verdict]]


# ------------------------------------------------------------ 内置层
def l1_structure(env: Envelope) -> Optional[Verdict]:
    if not env.sender or not env.topic or not env.recipient:
        return Verdict(BLOCK, "L1", "信封缺少 sender/topic/recipient")
    return None


def l2_size(env: Envelope) -> Optional[Verdict]:
    try:
        size = len(json.dumps(env.payload, ensure_ascii=False).encode("utf-8"))
    except Exception:
        return Verdict(BLOCK, "L2", "payload 不可序列化")
    if size > MAX_PAYLOAD_BYTES:
        return Verdict(BLOCK, "L2", f"payload 超限 {size}>{MAX_PAYLOAD_BYTES}")
    return None


def l3_danger(env: Envelope) -> Optional[Verdict]:
    """危险模式（V5.2 归一化版）。

    判据顺序：原始串 → 归一化串（NFKC/零宽/同形字）→ 紧凑串（去分隔符）。
    原始串命中时 reason 与旧版逐字一致，保证既有审计文本与黄金值不漂移。
    """
    raw = json.dumps(env.payload, ensure_ascii=False).lower()
    text = normalize_for_match(raw)
    compact = compact_for_match(raw)
    for pat in DANGER_PATTERNS:
        hit = "raw" if pat in raw else ("norm" if pat in text else "")
        pat_compact = "".join(ch for ch in pat if ch.isalnum())
        if not hit and len(pat_compact) >= MIN_COMPACT_PATTERN and pat_compact in compact:
            hit = "compact"
        if hit:
            return Verdict(BLOCK, "L3", f"命中危险模式：{pat}")
    return None


def l4_permission(env: Envelope) -> Optional[Verdict]:
    need = int(env.metadata.get("permission_required", 0))
    have = int(env.metadata.get("permission", 0))
    if need > have:
        return Verdict(BLOCK, "L4", f"权限不足 need={need} have={have}")
    return None


def l5_unauthorized_garbled(env: Envelope) -> Optional[Verdict]:
    # 越权：声明的身份与发送者不一致
    claimed = env.metadata.get("as_identity")
    if claimed is not None and claimed != env.sender:
        return Verdict(BLOCK, "L5", f"越权：声明身份 '{claimed}' ≠ sender '{env.sender}'")
    # 失真：显式校验标记
    if env.metadata.get("garbled") is True:
        return Verdict(BLOCK, "L5", "消息失真（garbled）")
    return None


def l6_metadata(env: Envelope) -> Optional[Verdict]:
    if env.mode not in ("simulated", "live"):
        return Verdict(BLOCK, "L6", f"非法 mode：{env.mode}")
    return None


def l7_audit(env: Envelope) -> Optional[Verdict]:
    return None  # 审计在 Guard 层统一记录


def l8_consistency(env: Envelope) -> Optional[Verdict]:
    if env.sender not in env.trace:
        return Verdict(ADVISE, "L8", "trace 未包含 sender")
    return None


BUILTIN_LAYERS: List[Tuple[str, LayerFn]] = [
    ("L1", l1_structure),
    ("L2", l2_size),
    ("L3", l3_danger),
    ("L4", l4_permission),
    ("L5", l5_unauthorized_garbled),
    ("L6", l6_metadata),
    ("L7", l7_audit),
    ("L8", l8_consistency),
]


@dataclass
class Guard:
    """语义级边界：8 层串联 + 审计。"""
    config: GuardConfig = field(default_factory=GuardConfig)
    extra_layers: List[LayerFn] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.audit_log: List[dict] = []
        self.layers: List[Tuple[str, LayerFn]] = list(BUILTIN_LAYERS)
        for fn in self.extra_layers:
            self.layers.append((f"LX", fn))

    def inspect(self, env: Envelope) -> Verdict:
        verdict = Verdict(ALLOW, "L0", "通过")
        for name, fn in self.layers:
            v = fn(env)
            if v is None:
                continue
            if v.action == BLOCK:
                verdict = v
                break
            if v.action == ADVISE and verdict.action == ALLOW:
                verdict = v
        self._audit(env, verdict)
        return verdict

    def admit(self, env: Envelope) -> bool:
        return self.inspect(env).action != BLOCK

    def check_text(self, text: str, *, sender: str = "main",
                   recipient: str = "guard", topic: str = "check") -> Verdict:
        env = Envelope.create(sender, recipient, topic, {"task": text})
        return self.inspect(env)

    def _audit(self, env: Envelope, verdict: Verdict) -> None:
        if not self.config.audit_enabled:
            return
        self.audit_log.append({
            "ts": time.time(), "sender": env.sender, "topic": env.topic,
            "recipient": env.recipient, "verdict": verdict.to_dict(),
        })

    def stats(self) -> dict:
        blocked = sum(1 for a in self.audit_log
                      if a["verdict"]["action"] == BLOCK)
        return {"inspected": len(self.audit_log), "blocked": blocked,
                "layers": len(self.layers),
                "advised": sum(1 for a in self.audit_log
                               if a["verdict"]["action"] == ADVISE)}
