# -*- coding: utf-8 -*-
"""
桥 conformance —— 新桥只需 3 个方法即可接入（W19，旁挂）
================================================================================
契约：advertise() / invoke() / close()。不加内核代码、不碰零依赖。
conformance 用一组确定性检查替人做验收：方法齐备、返回结构合格、close 幂等、
不引入网络调用。

纯标准库。
"""
from __future__ import annotations

import inspect
import os
from typing import Any, Dict, List


REQUIRED_METHODS = ("advertise", "invoke", "close")


class Bridge:
    """桥的参考实现（既是模板也是被测对象）。"""

    name = "reference-bridge"

    def advertise(self) -> dict:
        return {"name": self.name, "methods": list(REQUIRED_METHODS),
                "capabilities": ["invoke"], "offline": True}

    def invoke(self, request: Dict[str, Any]) -> dict:
        return {"status": "ok", "output": request.get("task"),
                "bridge": self.name}

    def close(self) -> dict:
        return {"closed": True, "bridge": self.name}


def _calls_network(fn) -> bool:
    """静态扫描：函数体里出现 socket/urllib/requests 即判为联网。"""
    try:
        src = inspect.getsource(fn)
    except (OSError, TypeError):
        return False
    bans = ("import socket", "import urllib", "import requests",
            "urlopen(", "http://", "https://")
    return any(b in src for b in bans)


def conformance(candidate: Any) -> dict:
    """对任意候选桥跑一遍 conformance；返回 checks + verdict。"""
    checks: List[dict] = []
    name = getattr(candidate, "name", type(candidate).__name__)

    missing = [m for m in REQUIRED_METHODS if not callable(getattr(candidate, m, None))]
    checks.append({"id": "C1-methods", "ok": not missing,
                   "detail": "missing=%s" % missing})

    if not missing:
        adv = candidate.advertise()
        checks.append({"id": "C2-advertise", "ok": isinstance(adv, dict)
                       and "name" in adv and "capabilities" in adv
                       and "offline" in adv,
                       "detail": "keys=%s" % sorted(adv) if isinstance(adv, dict) else "not-dict"})

        res = candidate.invoke({"task": "conformance probe"})
        checks.append({"id": "C3-invoke", "ok": isinstance(res, dict)
                       and "status" in res,
                       "detail": "status=%s" % (res.get("status") if isinstance(res, dict) else None)})

        first = candidate.close()
        second = candidate.close()
        checks.append({"id": "C4-close-idempotent", "ok": first == second,
                       "detail": "两次 close 返回相同"})

        net = [m for m in REQUIRED_METHODS
               if callable(getattr(candidate, m, None))
               and _calls_network(getattr(candidate, m))]
        checks.append({"id": "C5-offline", "ok": not net,
                       "detail": "network_methods=%s" % net})

        try:
            mod_file = os.path.abspath(inspect.getfile(type(candidate)))
        except (OSError, TypeError):
            mod_file = ""
        kernel_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                  "holoaeon") + os.sep
        inside_kernel = mod_file.startswith(kernel_dir)
        checks.append({"id": "C6-no-kernel-edit", "ok": bool(mod_file) and not inside_kernel,
                       "detail": "桥实现文件：%s" % (mod_file or "unknown")})
    else:
        checks.append({"id": "C2-C6", "ok": False, "detail": "方法不全，跳过后续检查"})

    passed = sum(1 for c in checks if c["ok"])
    return {"bridge": name, "checks": checks, "passed": passed,
            "total": len(checks), "verdict": "PASS" if passed == len(checks) else "FAIL"}
