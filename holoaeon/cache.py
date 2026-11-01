# -*- coding: utf-8 -*-
"""
Cache —— 可复算本地指纹缓存（W17 之一，旁挂）
================================================================================
键 = 输入指纹（规范化 JSON 的 sha256），值 = 输出字节。
同一输入第二次调用必须命中，且输出**逐字节相同**。纯本地文件，不联网。

物理量（耗时、机器信息）不进键，也不进值。

纯标准库。
"""
from __future__ import annotations

import hashlib
import json
import os
from typing import Any, Dict, Optional


def _canon(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), default=str)


def fingerprint(obj: Any) -> str:
    """输入指纹：规范化 JSON 的 sha256（前 32 位）。"""
    return hashlib.sha256(_canon(obj).encode("utf-8")).hexdigest()[:32]


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class ByteCache:
    """把"输入指纹 → 输出字节"落在本地；命中即返回同一份字节。"""

    def __init__(self, directory: str) -> None:
        self.dir = directory
        os.makedirs(self.dir, exist_ok=True)
        self.hits = 0
        self.misses = 0

    def path(self, key: str) -> str:
        return os.path.join(self.dir, "%s.bin" % key)

    def get(self, key: str) -> Optional[bytes]:
        p = self.path(key)
        if not os.path.exists(p):
            self.misses += 1
            return None
        with open(p, "rb") as fh:
            data = fh.read()
        self.hits += 1
        return data

    def put(self, key: str, data: bytes) -> str:
        p = self.path(key)
        tmp = p + ".tmp"
        with open(tmp, "wb") as fh:
            fh.write(data)
        os.replace(tmp, p)
        return p

    def get_or_put(self, key: str, producer) -> bytes:
        """命中即复用；未命中才调用 producer（producer 必须返回 bytes）。"""
        cached = self.get(key)
        if cached is not None:
            return cached
        data = producer()
        if not isinstance(data, bytes):
            data = str(data).encode("utf-8")
        self.put(key, data)
        return data

    def stats(self) -> dict:
        total = self.hits + self.misses
        return {"hits": self.hits, "misses": self.misses, "total": total,
                "hit_rate": round(self.hits / total, 4) if total else 0.0,
                "dir": self.dir}


class MemoCache:
    """进程内缓存（同样的键/字节语义），用于不想落盘的场景。"""

    def __init__(self) -> None:
        self._store: Dict[str, bytes] = {}
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[bytes]:
        if key in self._store:
            self.hits += 1
            return self._store[key]
        self.misses += 1
        return None

    def put(self, key: str, data: bytes) -> None:
        self._store[key] = bytes(data)

    def stats(self) -> dict:
        total = self.hits + self.misses
        return {"hits": self.hits, "misses": self.misses, "total": total,
                "hit_rate": round(self.hits / total, 4) if total else 0.0}
