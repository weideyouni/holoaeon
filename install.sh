#!/usr/bin/env sh
# ============================================================================
# HoloAeon —— 一键安装（Linux/macOS）· 批3 产品层
# 新手小白：把本脚本放进仓库根目录，执行  ./install.sh
# 零依赖：仅需 python3（>=3.8），无需 pip 安装任何第三方包。
# 只读校验 + 自检，不改动任何既有源码之外的产物。
# ============================================================================
set -eu

echo "== HoloAeon 安装（Linux/macOS）=="
if ! command -v python3 >/dev/null 2>&1; then
  echo "!! 未找到 python3，请先安装 Python 3.8+"
  exit 1
fi

PY=$(command -v python3)
echo "python: $PY"
"$PY" - <<'PY'
import sys
if sys.version_info < (3, 8):
    sys.exit("!! 需要 Python 3.8+，当前 %s" % sys.version)
PY

echo "== ① 校验内核装配（维度不变 25/47/9）=="
python3 - <<'PY'
from holoaeon.packs import PACK_ORDER, EXTRA_PACK_ORDER
from holoaeon.spec import VERSION, DOC_VERSION
print("  version=%s doc=%s" % (VERSION, DOC_VERSION))
print("  domain_packs=%d extra_packs=%d" % (len(PACK_ORDER), len(EXTRA_PACK_ORDER)))
assert len(PACK_ORDER) == 9, "领域包必须为 9"
assert len(EXTRA_PACK_ORDER) >= 10, "扩展包至少 10（含 L9 后的 fusion_upgrade）"
print("  装配校验通过")
PY

echo "== ② 跑内核自检（25/25）=="
python3 scripts/launch_local.py selftest | tail -n 1

echo "== ③ 产品层 demo（一键体验）=="
python3 -m holoaeon.demo_product

echo ""
echo "== 安装完成 =="
echo "  对话界面驱动： python -m holoaeon.frontend_adapter '你的任务'"
echo "  或安装为命令： pip install -e .  （可选；本仓库零依赖，不装也能跑）"
echo "  封口密语：潮起开门，潮落闭嘴。evidence_class=simulated，仿真≠证明，碳基终裁。"
