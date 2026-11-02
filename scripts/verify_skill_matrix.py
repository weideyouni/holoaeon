# -*- coding: utf-8 -*-
"""verify_skill_matrix.py —— 技能矩阵六机制 + 扩展包 + 跨线程调度的统一验证（只读仓库，不写盘）。"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holoaeon.kernel import Kernel                      # noqa: E402
from holoaeon.packs import EXTRA_PACK_ORDER, get_extra_pack  # noqa: E402
from holoaeon.packs.skill_matrix_pack import SkillMatrixPack, pack_summary  # noqa: E402
from holoaeon.skill_matrix import MATRIX_ID, default_roots  # noqa: E402
from holoaeon.skill_matrix import index as Ix           # noqa: E402
from holoaeon.skill_matrix.runtime import MatrixRuntime  # noqa: E402
from holoaeon.skill_matrix.selftest import run as run_selftest  # noqa: E402

INDEX = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "data", "skill_matrix_index.json")


def main() -> int:
    out = {"matrix_id": MATRIX_ID, "index_path": INDEX}
    out["selftest"] = run_selftest()

    # 扩展包注册与装包（维度不变的前提：不进 PACK_ORDER）
    out["pack"] = {"in_extras": "skill_matrix" in EXTRA_PACK_ORDER,
                   "order_len": len(EXTRA_PACK_ORDER), "summary": pack_summary()}
    k = Kernel()
    core_before = len(k.skills.names())
    info = get_extra_pack("skill_matrix").install(k)
    out["pack"]["install"] = info
    out["pack"]["core_before_install"] = core_before
    out["pack"]["core_after_pack"] = len(k.skills.names())

    # 索引运行时
    idx = Ix.load(INDEX)
    if idx is None:
        out["runtime"] = {"error": "索引缺失，先跑 scripts/build_skill_matrix.py"}
    else:
        rt = MatrixRuntime(idx)
        queries = ["统计这周的销售额并出报表", "合规审查 红线 校验", "多智能体协作 圆桌 分身"]
        out["runtime"] = {
            "skills": len(rt.rows), "digest": idx["digest"],
            "queries": [rt.dispatch(q) for q in queries],
            "thread_probe": rt.concurrency_probe("语义路由与消息总线", n=8),
            "quartet": rt.quartet_review("把技能基座化并给出升级方向"),
        }
        km = Kernel()
        before = len(km.skills.names())
        mounted = rt.mount(km, limit=12)
        out["runtime"]["mount"] = {"mounted": mounted["mounted"],
                                   "core_skills_before": before,
                                   "core_skills_after": len(km.skills.names())}

    print(json.dumps(out, ensure_ascii=False, indent=1, default=str))
    return 0 if out["selftest"]["ok"] and out["pack"]["install"]["skills"] else 1


if __name__ == "__main__":
    sys.exit(main())
