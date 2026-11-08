# -*- coding: utf-8 -*-
"""test_v50 —— 千问 V49 评估 P0/P1/P2 采纳批（V50）· unittest 主套用例。

覆盖：MCP 双版本（legacy 握手 / server/discover 新 RPC / 无握手直通 /
通知帧静默 / _meta 新式请求）、forge_gate CHAIN_POSITION 补齐、
ModelSplitRules 拒绝消息责任条款、model_base_registry compliance_note、
MLPS3 诚实化声明与映射表。"""
import importlib.util
import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

from holoaeon.mcp_adapter import _handle_line, PROTOCOL_VERSION, SUPPORTED_PROTOCOL_VERSIONS
from holoaeon.forge_gate import CHAIN_POSITION, ModelSplitRules, ForgeGate, SEAL


def _rpc(method, msg_id="x", params=None, meta=False):
    p = {"jsonrpc": "2.0", "id": msg_id, "method": method, "params": params or {}}
    if meta:
        p["params"]["_meta"] = {"io.modelcontextprotocol/clientInfo":
                                {"name": "new-client", "version": "1.0"}}
    return _handle_line(json.dumps(p))


class TestMcpDualVersion(unittest.TestCase):
    """P0-2：MCP 2024-11-05 legacy + 2026-07-28 无状态双规范（SEP-2575 官方双版本路径）。"""

    def test_legacy_version_constant(self):
        self.assertEqual(PROTOCOL_VERSION, "2024-11-05")

    def test_dual_version_declaration(self):
        self.assertEqual(SUPPORTED_PROTOCOL_VERSIONS, ("2024-11-05", "2026-07-28"))

    def test_legacy_initialize_handshake(self):
        r = _rpc("initialize", 1)
        self.assertEqual(r["result"]["protocolVersion"], "2024-11-05")
        self.assertEqual(r["result"]["serverInfo"]["name"], "holoaeon-mcp")

    def test_server_discover_new_rpc(self):
        r = _rpc("server/discover", 2)
        self.assertIn("2026-07-28", r["result"]["protocolVersions"])
        self.assertIn("2024-11-05", r["result"]["protocolVersions"])
        self.assertTrue(r["result"]["stateless"])

    def test_stateless_tools_list_without_handshake(self):
        r = _rpc("tools/list", 3)
        names = [t["name"] for t in r["result"]["tools"]]
        self.assertEqual(names, ["holoaeon.task", "holoaeon.status", "holoaeon.quartet"])

    def test_ping_without_handshake(self):
        self.assertEqual(_rpc("ping", 4)["result"], {})

    def test_notification_frame_silent(self):
        r = _handle_line(json.dumps({"jsonrpc": "2.0",
                                     "method": "notifications/initialized"}))
        self.assertIsNone(r)

    def test_any_notification_silent(self):
        r = _handle_line(json.dumps({"jsonrpc": "2.0", "method": "notifications/cancelled",
                                     "params": {"requestId": 99}}))
        self.assertIsNone(r)

    def test_unknown_tool_protocol_error(self):
        r = _rpc("tools/call", 5, {"name": "no.such.tool", "arguments": {}})
        self.assertEqual(r["error"]["code"], -32602)

    def test_parse_error(self):
        r = _handle_line("not-json{{")
        self.assertEqual(r["error"]["code"], -32700)

    def test_invalid_request(self):
        r = _handle_line(json.dumps([1, 2, 3]))
        self.assertEqual(r["error"]["code"], -32600)

    def test_unknown_method_still_error(self):
        r = _rpc("roots/list", 6)
        self.assertEqual(r["error"]["code"], -32601)

    def test_meta_new_style_request_passthrough(self):
        r = _rpc("tools/list", 7, meta=True)
        self.assertEqual(len(r["result"]["tools"]), 3)

    def test_docstring_dual_version_and_sep_reference(self):
        import holoaeon.mcp_adapter as ma
        self.assertIn("2024-11-05", ma.__doc__)
        self.assertIn("2026-07-28", ma.__doc__)
        self.assertIn("SEP-2575", ma.__doc__)
        self.assertIn("MAY", ma.__doc__)  # 官方双版本路径原文引用


class TestForgeGateConsistency(unittest.TestCase):
    """P2-1：ring16 CHAIN_POSITION 补齐（与前 15 环同构）。"""

    def test_chain_position_present(self):
        self.assertEqual(CHAIN_POSITION["ring"], 16)
        self.assertEqual(CHAIN_POSITION["layer"], "assembly")

    def test_chain_position_upstream(self):
        self.assertIn("craft_gate", json.dumps(CHAIN_POSITION["upstream"]))

    def test_route_rejection_includes_compliance_note(self):
        """P1-3：platform_large 拒绝消息引用备案责任条款。"""
        r = ModelSplitRules().route("plugin_upgrade", explicit_auth=False)
        self.assertFalse(r["ok"])
        self.assertIn("备案", r["compliance_note"])
        self.assertIn("部署方", r["compliance_note"])

    def test_route_authorized_still_ok(self):
        self.assertTrue(ModelSplitRules().route("plugin_upgrade",
                                                explicit_auth=True)["ok"])

    def test_forge_run_regression(self):
        m = ForgeGate().run("回归 装配")
        for s in ("philosophy", "math", "language", "module", "code"):
            self.assertEqual(m["rail_final_state"][s], "done")
        self.assertEqual(m["frontend_brief"]["schema"], "holoaeon-frontend-brief-v1")
        self.assertEqual(m["seal"], SEAL)


class TestRegistryComplianceNote(unittest.TestCase):
    """P1-3：bridges 侧 coupling_plan 备案责任边界字段。"""

    @classmethod
    def setUpClass(cls):
        p = os.path.join(ROOT, "bridges", "model_base_registry.py")
        spec = importlib.util.spec_from_file_location("model_base_registry_v50", p)
        cls.reg = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.reg)

    def test_compliance_note_present(self):
        cp = self.reg.coupling_plan()
        self.assertIn("第二条第三款", cp["compliance_note"])
        self.assertIn("部署方", cp["compliance_note"])

    def test_bases_unchanged(self):
        self.assertEqual(len(self.reg.MODEL_BASES), 14)

    def test_seal_unchanged(self):
        self.assertEqual(self.reg.SEAL, SEAL)


class TestMlps3Honesty(unittest.TestCase):
    """P1-2：MLPS3 设计对齐自查表诚实化 + 映射表。"""

    def test_docstring_self_check_claim(self):
        from holoaeon.phc_chronic_engine import MLPS3
        self.assertIn("设计对齐自查表", MLPS3.__doc__)
        self.assertIn("非等保测评结论", MLPS3.__doc__)

    def test_docstring_responsibility_boundary(self):
        from holoaeon.phc_chronic_engine import MLPS3
        self.assertIn("运营主体", MLPS3.__doc__)
        self.assertIn("测评机构", MLPS3.__doc__)

    def test_docstring_mapping_table_reference(self):
        from holoaeon.phc_chronic_engine import MLPS3
        self.assertIn("MLPS3_MAPPING.md", MLPS3.__doc__)

    def test_mapping_table_three_states(self):
        t = open(os.path.join(ROOT, "docs", "MLPS3_MAPPING.md"), encoding="utf-8").read()
        for k in ("天然不适用", "已对齐", "须运营主体补"):
            self.assertIn(k, t)

    def test_mapping_table_nine_controls(self):
        t = open(os.path.join(ROOT, "docs", "MLPS3_MAPPING.md"), encoding="utf-8").read()
        for k in ("身份鉴别", "访问控制", "安全审计", "入侵防范", "恶意代码防范",
                  "可信验证", "数据完整性", "数据保密性", "备份恢复"):
            self.assertIn(k, t)

    def test_mapping_table_seal(self):
        t = open(os.path.join(ROOT, "docs", "MLPS3_MAPPING.md"), encoding="utf-8").read()
        self.assertIn("潮起开门，潮落闭嘴", t)


if __name__ == "__main__":
    unittest.main()
