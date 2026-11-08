# -*- coding: utf-8 -*-
"""site_gateway — 现场网关（V47，模型自动耦合 + 网络二极管）
位置纪律：bridges/ 可选层（承 V46 探测器先例），socket/网络语义不进核心包。
能力一 · 模型自动发现与耦合：
  discover（复用 local_model_probe）→ couple（首选可用后端 → 耦合配置单）。
  自动发现服务器或本地电脑端安装的轻量级小模型并自动耦合——
  耦合=登记配置+健康探测（report-only，实际连接由部署侧执行）。
能力二 · 网络二极管（内外网协议融合）：
  · 内外网不打通：无任何直连路由；
  · 内网数据不出内网：出站一律 BLOCK（白名单为空，结构性保证）；
  · 外网接口只进升级信息：入站白名单=upgrade 包，须 SHA256 校验
    +机构审批双验证，落 staging 隔离区待检。
协议融合矩阵（PROTOCOL_MATRIX）：内外网协议在网关边界适配转换，
两侧不直连——外网 HTTPS 升级源 → 网关校验落盘 → 内网按需装载。
零依赖纯标准库。封口密语：潮起开门，潮落闭嘴。
"""
import hashlib
import importlib.util
import json
import os
import time

SEAL = "潮起开门，潮落闭嘴"

# 协议融合矩阵（内外网不打通，边界适配）
PROTOCOL_MATRIX = {
    "intranet": ("本地进程调用", "机构内 HTTP(仅 127.0.0.1/内网段)",
                 "JSONL 台账交换"),
    "boundary": ("外网 HTTPS 升级源 → 网关（SHA+审批双验）→ staging 落盘",
                 "内外网不直连，无路由穿透"),
    "internet": ("仅入站升级包", "无出站（结构性零出站）"),
}

# 入站白名单（唯一允许的外网→内网信息类型）
INBOUND_ALLOW = ("upgrade_manifest", "upgrade_package")

# 出站白名单：空集——内网数据不出内网（结构性保证，非策略声明）
OUTBOUND_ALLOW = ()


class ModelAutoCouple:
    """自动发现+自动耦合：discover 结果 → 首选可用后端 → 耦合配置单。
    优先级：up 的服务端点（ollama>lmstudio>vllm）> GGUF 文件 > 已装包。"""

    PRIORITY = ("ollama", "lmstudio", "vllm")

    @classmethod
    def couple(cls, discovery=None):
        if discovery is None:
            here = os.path.dirname(os.path.abspath(__file__))
            spec = importlib.util.spec_from_file_location(
                "local_model_probe",
                os.path.join(os.path.dirname(here) if "bridges" in here
                             else here, "bridges", "local_model_probe.py"))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            discovery = mod.discover()
        services = discovery.get("services", [])
        up = {s["backend"]: s for s in services if s["status"] == "up"}
        for backend in cls.PRIORITY:
            if backend in up:
                s = up[backend]
                return {"ok": True, "coupled": True, "backend": backend,
                        "endpoint": "http://%s:%d" % (s["host"], s["port"]),
                        "mode": "auto_coupled",
                        "note": "耦合=登记+健康探测；实际连接由部署侧执行",
                        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
                        "seal": SEAL}
        gguf = discovery.get("gguf_files", [])
        if gguf:
            return {"ok": True, "coupled": True, "backend": "gguf_local",
                    "endpoint": gguf[0]["path"],
                    "candidates": len(gguf), "mode": "auto_coupled",
                    "seal": SEAL}
        pkgs = [p["package"] for p in discovery.get("packages", [])
                if p["installed"]]
        if pkgs:
            return {"ok": True, "coupled": True, "backend": "python_package",
                    "endpoint": ",".join(pkgs), "mode": "auto_coupled",
                    "seal": SEAL}
        return {"ok": True, "coupled": False,
                "note": "未发现可用本地模型——请安装 ollama 或放置 GGUF",
                "discovered": {"services": len(services),
                               "gguf": len(gguf), "packages": len(pkgs)},
                "seal": SEAL}


class NetDiode:
    """网络二极管：出站结构性零放行；入站白名单+SHA+审批三重门。
    report-only 裁决，实际执行由部署侧网关（nginx/防火墙）落地。"""

    @classmethod
    def outbound(cls, request):
        """内网数据不出内网：一律 BLOCK（白名单空集=结构性保证）。"""
        return {"verdict": "BLOCK", "request": str(request)[:60],
                "reason": "网络二极管：出站白名单为空，内网数据不出内网",
                "allowlist": list(OUTBOUND_ALLOW), "seal": SEAL}

    @classmethod
    def inbound(cls, packet_type, sha256="", approved=False):
        """外网只进升级信息：白名单类型+SHA 合法+审批三重验证。"""
        if packet_type not in INBOUND_ALLOW:
            return {"verdict": "BLOCK", "reason": "非白名单类型（仅升级信息）",
                    "seal": SEAL}
        if len(sha256) != 64 or any(c not in "0123456789abcdef"
                                    for c in sha256.lower()):
            return {"verdict": "BLOCK", "reason": "SHA256 校验不合法",
                    "seal": SEAL}
        if not approved:
            return {"verdict": "BLOCK",
                    "reason": "须机构审批（处置权分离）", "seal": SEAL}
        return {"verdict": "ALLOW", "packet_type": packet_type,
                "sha256": sha256, "destination": "staging/",
                "note": "落 staging 隔离区待检后才可装载", "seal": SEAL}

    @classmethod
    def digest_of(cls, payload_bytes):
        """升级包摘要计算（网关侧对真实文件算 SHA256）。"""
        return hashlib.sha256(payload_bytes).hexdigest()


def gateway_report():
    """网关状态报告：协议矩阵+二极管口径（report-only）。"""
    return {"ok": True, "protocol_matrix": PROTOCOL_MATRIX,
            "inbound_allow": list(INBOUND_ALLOW),
            "outbound_allow": list(OUTBOUND_ALLOW),
            "outbound_note": "出站白名单为空集=结构性零出站（非策略可配置项）",
            "seal": SEAL}


if __name__ == "__main__":
    print(json.dumps(gateway_report(), ensure_ascii=False, indent=2))
