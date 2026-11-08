# -*- coding: utf-8 -*-
"""local_model_probe — 本地模型探测器（V46，千问 V45 评估 P0-2 采纳）
位置纪律（千问原话级正确）：本文件放 bridges/ 而非 holoaeon/ 包内——
探测端口需 socket，而核心包「零网络」是四轮核验确认的硬属性
（包内网络模块 import=0）。bridges/ 是可选层：挂载即用、删除即回滚。
能力：扫描本地已装模型并列举（确定性清单，可复算可审计）。
  · Ollama      127.0.0.1:11434 试连（短超时）
  · LM Studio   127.0.0.1:1234 试连
  · vLLM        127.0.0.1:8000 试连
  · GGUF 文件   glob 常见目录 *.gguf（只读文件名与大小，零解析器依赖）
  · Python 包   importlib.util.find_spec 只探测不导入（llama_cpp 等）
零依赖纯标准库；全部只读探测，不发任何写请求。
台账模式与 phc_recall.SyncLedger 同构（探测结果带时点）。
封口密语：潮起开门，潮落闭嘴。
"""
import glob
import importlib.util
import os
import socket
import time

SEAL = "潮起开门，潮落闭嘴"

# 探测目标（端口语义与 bridges/backends.py 对齐）
PROBE_TARGETS = (
    ("ollama", "127.0.0.1", 11434),
    ("lmstudio", "127.0.0.1", 1234),
    ("vllm", "127.0.0.1", 8000),
)

# GGUF 常见目录（存在才扫；只读文件名+大小）
GGUF_DIRS = (
    os.path.expanduser("~/.cache/huggingface"),
    os.path.expanduser("~/models"),
    "models",
    "bridges/models",
)

# 只探测不导入的包清单
PROBE_PACKAGES = ("llama_cpp", "transformers", "torch")


def probe_port(host, port, timeout=0.3):
    """端口试连（短超时，refused/timeout 都算 down——确定性三态语义）。"""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return "up"
    except OSError:
        return "down"


def probe_services():
    """服务端点探测：确定性清单。"""
    return [{"backend": name, "host": host, "port": port,
             "status": probe_port(host, port)}
            for name, host, port in PROBE_TARGETS]


def probe_gguf_files(extra_dirs=()):
    """GGUF 文件扫描：只读文件名与大小（字节），零解析。"""
    found = []
    for d in tuple(GGUF_DIRS) + tuple(extra_dirs):
        if not os.path.isdir(d):
            continue
        for p in glob.glob(os.path.join(d, "**", "*.gguf"),
                           recursive=True):
            try:
                size = os.path.getsize(p)
            except OSError:
                size = -1
            found.append({"path": p, "bytes": size})
    return sorted(found, key=lambda x: x["path"])


def probe_packages():
    """已装包探测：find_spec 只探测不导入。"""
    out = []
    for pkg in PROBE_PACKAGES:
        try:
            spec = importlib.util.find_spec(pkg)
        except (ImportError, ValueError):
            spec = None
        out.append({"package": pkg, "installed": spec is not None})
    return out


def discover(extra_dirs=()):
    """总探测：确定性清单 + 时点台账。report-only，零写请求。"""
    return {"ok": True,
            "services": probe_services(),
            "gguf_files": probe_gguf_files(extra_dirs),
            "packages": probe_packages(),
            "scanned_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "read_only": True, "seal": SEAL}


if __name__ == "__main__":
    import json
    print(json.dumps(discover(), ensure_ascii=False, indent=2))

