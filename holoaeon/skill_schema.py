# -*- coding: utf-8 -*-
"""
SkillSchema —— 结构化 schema 校验（W14，旁挂）
================================================================================
契约从"靠反射猜参数"升级为"显式 input_schema"。缺参 / 类型错 / 多余字段
一律显式报错并**指名字段**，不许静默兜底（V3-3）。

修复环默认 2 次：调用方给一个 repair(payload, errors) 回调；超限抛错。

纯标准库。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

TYPE_MAP = {
    "str": str, "int": int, "float": float, "bool": bool,
    "list": list, "dict": dict, "any": object,
}
# int 不算 float 的实例，float 允许 int 提升；bool 是 int 子类，需单独排除
_PROMOTABLE = {"float": ("int",)}


@dataclass
class SchemaField:
    name: str
    type: str = "any"
    required: bool = True
    default: Any = None

    def check(self, value: Any) -> Optional[str]:
        expect = TYPE_MAP.get(self.type)
        if expect is None:
            return "未知类型 '%s'" % self.type
        if expect is object:
            return None
        if self.type == "int" and isinstance(value, bool):
            return "期望 int，得到 bool"
        if isinstance(value, expect):
            return None
        for p in _PROMOTABLE.get(self.type, ()):
            if isinstance(value, TYPE_MAP[p]):
                return None
        return "期望 %s，得到 %s" % (self.type, type(value).__name__)


class SchemaError(RuntimeError):
    """schema 校验失败：errors 是按字段列出的明细。"""

    def __init__(self, errors: List[dict]):
        fields = ", ".join(e["field"] for e in errors)
        super().__init__("schema 校验失败（%d 处）：%s" % (len(errors), fields))
        self.errors = errors


def schema_from_inputs(inputs: Dict[str, str]) -> List[SchemaField]:
    """从 manifest 的 inputs 生成 schema：{"text": "str"} / {"n": "int?"}。
    `?` 结尾表示可选。"""
    out: List[SchemaField] = []
    for name, spec in inputs.items():
        text = str(spec).strip()
        required = not text.endswith("?")
        out.append(SchemaField(name=name,
                               type=text.rstrip("?").strip().lower() or "any",
                               required=required))
    return out


def validate(schema: List[SchemaField], payload: Dict[str, Any],
             *, allow_extra: bool = False) -> dict:
    """返回 {"ok": bool, "errors": [...]}；错误项含 field / reason / got。"""
    errors: List[dict] = []
    for f in schema:
        if f.name not in payload:
            if f.required:
                errors.append({"field": f.name, "reason": "缺少必填字段",
                               "got": None})
            continue
        reason = f.check(payload[f.name])
        if reason:
            errors.append({"field": f.name, "reason": reason,
                           "got": type(payload[f.name]).__name__})
    if not allow_extra:
        declared = {f.name for f in schema}
        for key in payload:
            if key in ("task", "query", "args", "output", "skill"):
                continue  # 协议层保留字段，不属技能入参
            if key not in declared:
                errors.append({"field": key, "reason": "多余字段（schema 未声明）",
                               "got": type(payload[key]).__name__})
    return {"ok": not errors, "errors": errors, "fields": len(schema)}


RepairFn = Callable[[Dict[str, Any], List[dict], int], Dict[str, Any]]


def call_with_repair(fn: Callable[..., Any], schema: List[SchemaField],
                     payload: Dict[str, Any], *,
                     repair: Optional[RepairFn] = None,
                     max_repair: int = 2,
                     allow_extra: bool = False,
                     args_key: str = "args") -> Tuple[Any, dict]:
    """先校验再调用；失败时按修复环重试，超限抛 SchemaError。

    返回 (结果, 元数据)；元数据记录 attempts / repaired。
    """
    attempts = 0
    notes: List[dict] = []
    body = dict(payload)
    while True:
        checked = validate(schema, body, allow_extra=allow_extra)
        if checked["ok"]:
            call_args = body.get(args_key) if isinstance(body.get(args_key), dict) else None
            if call_args is None:
                call_args = {k: v for k, v in body.items()
                             if k not in ("task", "query", "args", "skill")}
            result = fn(**call_args) if call_args else fn()
            return result, {"attempts": attempts, "repaired": bool(notes),
                            "notes": notes, "fields": checked["fields"]}
        attempts += 1
        if repair is None or attempts > max_repair:
            raise SchemaError(checked["errors"])
        body = repair(dict(body), checked["errors"], attempts) or body
        notes.append({"attempt": attempts, "errors": checked["errors"]})
