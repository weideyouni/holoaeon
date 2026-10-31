# HoloAeon × 向量海 技能桥接（Sidecar · 主核只读）

> 唯一ID：SG-VECTORSEA-HOLOAEON-BRIDGE-V1.0 · 生成时间 2026-10-31 · 封存密令：潮起开门 / 潮落闭嘴
> 本目录是纯增量旁挂：**不触碰 `holoaeon/` 核心包**，只向 Kernel 技能注册表注入向量海技能。

## 这是什么

把向量海技能全集（`.user_skills` 挂载点）整体注册为 **HoloAeon 可发现、可调用**的技能：
- **文档型技能（1124 个）**：确定性函数返回 SKILL.md 全文 + 元数据（离线读取，同输入同输出）；
- **工具型技能（16 个已注册）**：静态红线扫描（纯标准库 / 无网络 / 无进程派生 / 无 eval-exec）通过才标
  `verified`，否则标 `pending`（诚实纪律：未验证不提供执行包装，不冒充）。

## 实测回执（2026-10-31 本机 Windows · Python 3.13 · 纯标准库）

```text
catalog_total_dirs     1161
catalog_with_skill_md  1146
catalog_with_name      1140
registerable           1140   （全部有 name 的技能已注册进 Kernel）
skipped_duplicate      0      （与内置 47 技能零冲突）
skipped_no_name        21     （15 个无 SKILL.md + 6 个缺 name，留痕不入库）
doc_skill_count        1124
tool_skills_total      16     （17 个工具目录中 1 个无 name 未注册）
tool_preflight         verified 2 / pending 15（pending 名单与理由见 selftest_receipt.json）
registry_verify        count 1140 · no_duplicates true
match_demo             "中医康复融合" → shengui-shenma-shishu-yidao-tianhelu-super-matrix (0.048)
mode                   sidecar（主核只读，零网络零依赖）
```

完整回执见 [`selftest_receipt.json`](selftest_receipt.json)。

## 怎么用

```powershell
# 前提：在仓库根目录运行（holoaeon 包可导入）
$env:PYTHONPATH = "F:\doubaowork\holoaeon"
python bridges\vectorsea\vectorsea_bridge.py      # 直接运行 = 输出 selftest 回执

# 在代码里装载（示例）
from holoaeon import Kernel
from bridges.vectorsea.vectorsea_bridge import register_all
k = Kernel()
receipt = register_all(k)              # 1140 个向量海技能进入注册表
print(k.skills.match("中医康复融合", k=3))   # 自动匹配可用
print(k.skills.get("life-meridian-1331").run(""))  # 读取该技能 SKILL.md 全文
```

## 目录结构（三层）

| 层 | 文件 | 说明 |
|---|---|---|
| SKILL.md 层 | `../vectorsea-holoaeon-bridge/SKILL.md`（.user_skills 技能包） | 技能声明（五段式） |
| tools 层 | `vectorsea_bridge.py`、`scan_skills.py` | 确定性注册器 + 静态红线扫描器 |
| data 层 | `catalog.json`、`selftest_receipt.json` | 向量海技能目录快照 + 本次实测回执 |

## 四条军规落实

1. **主核只读**：不修改 `holoaeon/` 任何文件；全部增量在 `bridges/vectorsea/` 与 `.user_skills/`。
2. **增量旁挂**：技能包已挂 `.user_skills/vectorsea-holoaeon-bridge/`（SKILL.md + tools/ + data/）全域加载。
3. **证据先于声明**：以上每个数字来自 `python bridges\vectorsea\vectorsea_bridge.py` 实测回执；
   工具未过静态红线一律 `pending`，不冒充 `verified`。
4. **同步收尾**：本桥接随本批次同步飞书向量海（入库入口登记 + 分发包 + SHA 回读对账）。

## 红线

零网络调用、零内置密钥、零遥测、不执行未验证工具脚本、不替用户决策；
静态红线扫描 = 静态分析，不等于"可安全执行"的最终承诺，执行前仍须人工复核。
