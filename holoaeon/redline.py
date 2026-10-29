# -*- coding: utf-8 -*-
"""
Redline —— HoloAeon 红线扫描（AST，确定性）
================================================================================
扫描包内所有 .py 文件，确保：
  · 零网络：不 import socket/urllib/http.client/requests/ftplib/smtplib/...
  · 零第三方依赖：import 的顶层模块必须是标准库
  · 零危险调用：eval/exec/compile/__import__/os.system/os.popen/subprocess.*
  · 零凭证读取：open('.env'/'id_rsa'/...)

使用 AST 而不是文本匹配：guard.py 中作为【检测词表】的字符串（如 "os.system"、
"rm -rf"）不会被误判——只有真实的 import 语句和调用节点才会被报告。
"""
from __future__ import annotations

import ast
import os
import sys
from typing import Dict, List, Tuple

# 网络 / 危险模块（顶层名）
FORBIDDEN_MODULES = {
    "socket", "requests", "urllib3", "http", "requests_futures",
    "ftplib", "smtplib", "telnetlib", "xmlrpc", "aiohttp", "httpx",
    "subprocess", "pip", "setuptools",
}
# urllib 是包，需单独处理（urllib.request 等）
FORBIDDEN_PREFIXES = ("urllib",)
# 危险调用名（直接调用的函数名）
FORBIDDEN_CALLS = {"eval", "exec", "compile", "__import__", "input",
                   "system", "popen", "Popen", "check_output", "call", "run"}
# 凭证文件名
SECRET_FILES = {".env", "id_rsa", "credentials", ".netrc", "secret"}


def _stdlib_names() -> set:
    names = getattr(sys, "stdlib_module_names", None)
    if names:
        return set(names)
    # 回退：本项目实际使用的标准库（最小集合）
    return {"os", "sys", "ast", "io", "csv", "re", "math", "time", "cmath",
            "heapq", "queue", "hashlib", "threading", "dataclasses",
            "typing", "collections", "enum", "json", "abc", "itertools",
            "pathlib", "functools", "contextlib", "types", "inspect", "textwrap"}


class RedlineVisitor(ast.NodeVisitor):
    def __init__(self, filename: str, stdlib: set):
        self.filename = filename
        self.stdlib = stdlib
        self.violations: List[Dict[str, str]] = []

    def _add(self, kind: str, name: str, lineno: int) -> None:
        self.violations.append({"file": self.filename, "line": lineno,
                                "kind": kind, "name": name})

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            top = alias.name.split(".")[0]
            if top in FORBIDDEN_MODULES or any(
                    alias.name.startswith(p) for p in FORBIDDEN_PREFIXES):
                self._add("forbidden_import", alias.name, node.lineno)
            elif top not in self.stdlib:
                self._add("third_party_import", alias.name, node.lineno)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            top = node.module.split(".")[0]
            if top in FORBIDDEN_MODULES or any(
                    node.module.startswith(p) for p in FORBIDDEN_PREFIXES):
                self._add("forbidden_import", node.module, node.lineno)
            elif top not in self.stdlib and node.level == 0:
                self._add("third_party_import", node.module, node.lineno)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        func = node.func
        # 直接危险函数
        if isinstance(func, ast.Name) and func.id in FORBIDDEN_CALLS:
            self._add("dangerous_call", func.id, node.lineno)
        # 凭证读取：open(".env") 等
        if isinstance(func, ast.Name) and func.id == "open" and node.args:
            first = node.args[0]
            if isinstance(first, ast.Constant) and isinstance(first.value, str):
                base = os.path.basename(first.value).lower()
                if base in SECRET_FILES:
                    self._add("secret_access", first.value, node.lineno)
        # 属性调用，如 os.system / subprocess.Popen
        if isinstance(func, ast.Attribute):
            if func.attr in FORBIDDEN_CALLS:
                value = func.value
                if isinstance(value, ast.Name) and value.id in (
                        "os", "subprocess", "sys"):
                    self._add("dangerous_call",
                              f"{value.id}.{func.attr}", node.lineno)
        self.generic_visit(node)


def scan_file(path: str, stdlib: set) -> List[dict]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source, filename=path)
    except (SyntaxError, UnicodeDecodeError) as exc:
        return [{"file": path, "line": 0, "kind": "parse_error", "name": str(exc)}]
    rel = os.path.basename(path)
    visitor = RedlineVisitor(rel, stdlib)
    visitor.visit(tree)
    return visitor.violations


def scan_directory(root: str) -> Dict[str, object]:
    stdlib = _stdlib_names()
    all_violations: List[dict] = []
    files_scanned = 0
    for dirpath, dirnames, filenames in os.walk(root):
        # 跳过缓存/虚拟环境
        dirnames[:] = [d for d in dirnames if d != "__pycache__"
                       and not d.endswith(".egg-info")]
        for name in filenames:
            if name.endswith(".py"):
                files_scanned += 1
                all_violations.extend(
                    scan_file(os.path.join(dirpath, name), stdlib))
    return {
        "files_scanned": files_scanned,
        "violations": all_violations,
        "clean": len(all_violations) == 0,
    }
