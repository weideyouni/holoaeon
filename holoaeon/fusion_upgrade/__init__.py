# -*- coding: utf-8 -*-
"""fusion_upgrade —— 冷热插拔赋能升级 + 内外融合协议（第 10 扩展包的内核）

六块能力，全部纯标准库、确定性、离线：
  · manifest  冷/热插拔清单：哪些包只能启动期装、哪些可运行期插拔、回滚点在哪
  · swap      运行期热插拔与回滚（含往返一致性探针）
  · protocol  内部融合协议（信封→守卫→总线→节拍→技能匹配）与外部融合协议（离线路由决策）
  · contract  两仓 JSON 契约 v1（6 必填 + 4 可选）、六机制对照表、12→17 通道映射表
  · plan      V2.0 十二批次计划（每批九字段，可校验）
  · snapshot  面向其他智能体的项目快照（自包含、可解析）
"""
from __future__ import annotations

FUSION_ID = "SG-FUSION-UPGRADE-HOLOAEON-V4.0"
FUSION_DOC_VERSION = "0.9.4-fusion"
FUSION_PROTOCOL = "HOLOAEON-FUSION-PROTOCOL-v1.0"
MODE_SIMULATED = "simulated"

__all__ = ["FUSION_ID", "FUSION_DOC_VERSION", "FUSION_PROTOCOL", "MODE_SIMULATED"]
