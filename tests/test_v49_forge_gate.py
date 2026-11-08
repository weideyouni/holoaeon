# -*- coding: utf-8 -*-
"""test_v49_forge_gate —— 实验田实测（.tmp_v49）。
覆盖：五段轨道不可跳步 / 组件索引匹配 / 分工路由授权门 / 落地模式穷举 /
前端需求卡（真实复用 ConceptAnatomizer）/ 基座登记表（真实品牌+就绪检查+零连接）。"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print("PASS  %s" % name)
    else:
        FAIL += 1
        print("FAIL  %s  %s" % (name, detail))


def main() -> int:
    # ---------- 1. 五段轨道 ----------
    from holoaeon.forge_gate import (AssemblyRail, ComponentIndex, ModelSplitRules,
                                     DeployModeMatrix, FrontendBriefCard, ForgeGate,
                                     STAGES, SEAL)

    rail = AssemblyRail()
    check("rail.五段顺序", STAGES == ("philosophy", "math", "language", "module", "code"))
    r1 = rail.advance()
    check("rail.首段philosophy", r1["ok"] and r1["stage"] == "philosophy")
    rail.complete()
    r2 = rail.advance()
    check("rail.第二段math", r2["stage"] == "math")
    sc = rail.skip_check()
    check("rail.中途无违规", sc["ok"] and sc["violations"] == [])
    # 跳步检测：手工置 pending 后 pos 前移
    rail2 = AssemblyRail()
    rail2.pos = 2  # 假装走了两段但 state 全 pending
    sc2 = rail2.skip_check()
    check("rail.跳步被识破", not sc2["ok"] and len(sc2["violations"]) == 2)
    # 走完全程
    rail.complete(); rail.advance(); rail.complete(); rail.advance(); rail.complete(); rail.advance(); rail.complete()
    r_end = rail.advance()
    check("rail.终点拒推进", not r_end["ok"])
    check("rail.全done", all(v == "done" for v in rail.state.values()))

    # ---------- 2. 组件索引 ----------
    idx = ComponentIndex()
    cat = idx.catalog()
    check("index.目录7域", len(cat["domains"]) == 7, str(cat))
    m = idx.match("本地 probe 耦合")
    check("index.匹配命中", m["ok"] and len(m["hits"]) >= 1 and "deploy" in m["domains"])
    check("index.匹配含probe", any("local_model_probe" in h["module"] for h in m["hits"]))
    m2 = idx.match("不存在的概念xyzqqq")
    check("index.零命中如实返回", m2["ok"] and m2["hits"] == [])

    # ---------- 3. 分工路由 ----------
    split = ModelSplitRules()
    r = split.route("internal_data")
    check("split.内网数据→小模型", r["ok"] and r["carrier"] == "local_small")
    r = split.route("mlps3_compliance")
    check("split.等保→小模型", r["ok"] and r["carrier"] == "local_small")
    r = split.route("offline_runtime")
    check("split.断网→小模型", r["ok"] and r["carrier"] == "local_small")
    r = split.route("plugin_upgrade", explicit_auth=False)
    check("split.插件升级未授权→拒发", not r["ok"] and "explicit_auth" in r["error"])
    r = split.route("plugin_upgrade", explicit_auth=True)
    check("split.插件升级授权→放行", r["ok"] and r["carrier"] == "platform_large")
    r = split.route("vector_upgrade", explicit_auth=True)
    check("split.向量库升级→大模型", r["ok"] and r["carrier"] == "platform_large")
    r = split.route("瞎编任务")
    check("split.未知任务→拒", not r["ok"])

    # ---------- 4. 落地模式穷举 ----------
    modes = DeployModeMatrix()
    em = modes.enumerate_modes()
    check("modes.穷举6模式", em["count"] == 6 and set(em["modes"]) ==
          {"personal_pc", "standalone_server", "lan_server", "distributed_cluster",
           "edge_offline", "air_gapped"})
    check("modes.个人PC推荐", modes.recommend(population=5)["recommended"] == "personal_pc")
    check("modes.单服务器推荐", modes.recommend(population=35000)["recommended"] == "standalone_server")
    check("modes.分布式推荐", modes.recommend(population=200000)["recommended"] == "distributed_cluster")
    check("modes.局域网推荐", modes.recommend(population=500)["recommended"] == "lan_server")
    check("modes.离线推荐", modes.recommend(offline=True)["recommended"] == "edge_offline")
    check("modes.等保推荐", modes.recommend(mlps3=True)["recommended"] == "air_gapped")

    # ---------- 5. 前端需求卡（真实复用 ConceptAnatomizer）----------
    card = FrontendBriefCard(project_id="test-fe-001",
                             brief_text="康复工程 前端工作台 装配 轨道")
    brief = card.build()
    check("brief.schema", brief["schema"] == "holoaeon-frontend-brief-v1")
    check("brief.封口密语", brief["seal"] == "潮起开门，潮落闭嘴")
    check("brief.逆向双模块声明", len(brief["reverse_modules"]) == 2 and
          brief["reverse_modules"][0]["module"] == "holoaeon.concept_anatomy")
    check("brief.解剖摘要16位", len(brief["intent_anatomy"]["digest"]) == 16)
    check("brief.页面树4页", len(brief["pages"]) == 4)
    check("brief.耦合点≥5", len(brief["coupling_points"]) >= 5)
    check("brief.耦合点真实模块", all("." in c["module"] for c in brief["coupling_points"]))
    check("brief.协议三通道", set(brief["protocols"]) == {"internal", "external", "frontend_channel"})
    check("brief.升级槽4个", len(brief["upgrade_slots"]) == 4)
    check("brief.验收含7/7", "7/7" in brief["acceptance"]["install_check"])
    check("brief.执行提示在", len(brief["execution_hint"]) > 40)
    # 确定性：同输入同 digest（解剖确定性传导）
    card2 = FrontendBriefCard(project_id="test-fe-001",
                               brief_text="康复工程 前端工作台 装配 轨道")
    b2 = card2.build()
    check("brief.确定性同digest", b2["intent_anatomy"]["digest"] == brief["intent_anatomy"]["digest"])

    # ---------- 6. ForgeGate 总编排 ----------
    g = ForgeGate()
    m = g.run("装配 康复 工作台", population=35000)
    check("gate.五段全done", all(m["rail_final_state"][s2] == "done" for s2 in STAGES))
    check("gate.跳步检查通过", m["skip_check"]["ok"])
    check("gate.stages记录10条", len(m["stages"]) == 10, str(len(m["stages"])))
    check("gate.组件目录在", m["component_catalog"]["total"] >= 15)
    check("gate.模式推荐3.5万人→单服务器", m["deploy_recommend"]["recommended"] == "standalone_server")
    check("gate.穷举6模式声明", m["deploy_modes_all"] == 6)
    check("gate.需求卡内嵌", m["frontend_brief"]["schema"] == "holoaeon-frontend-brief-v1")
    check("gate.产物卡五件入manifest", set(m["artifacts"]) ==
          {"philosophy_card", "math_card", "language_card", "module_card", "code_receipt"})
    check("gate.防撞名守卫在", "holo_forge" in json.dumps(m["artifacts"]["module_card"], ensure_ascii=False))
    check("gate.封口密语", m["seal"] == SEAL)

    # ---------- 7. 基座登记表（bridges，零连接）----------
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bridges"))
    # site_gateway import 方式（命名空间）：直接按路径加载
    import importlib.util
    _brg = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bridges", "model_base_registry.py")
    spec = importlib.util.spec_from_file_location("model_base_registry", _brg)
    reg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reg)

    check("reg.基座14条", len(reg.MODEL_BASES) == 14, str(len(reg.MODEL_BASES)))
    check("reg.国际6条", len([b for b in reg.MODEL_BASES if b["origin"] == "国际"]) == 6)
    check("reg.国内8条", len([b for b in reg.MODEL_BASES if b["origin"] == "国内"]) == 8)
    cls = reg.classify()
    check("reg.openai_chat分组≥10", len(cls["openai_chat"]) >= 10, str(cls))
    check("reg.anthropic=claude", cls["anthropic_messages"] == ["claude"])
    check("reg.gemini协议", cls["google_genai"] == ["gemini"])
    check("reg.纯本地协议组=llama", cls["local_weights"] == ["llama"])
    check("reg.开放权重可用≥7", len([b for b in reg.MODEL_BASES if b["local_weights"]]) >= 7)
    check("reg.qwen在列", "qwen" in cls["openai_chat"])
    check("reg.deepseek在列", "deepseek" in cls["openai_chat"])
    check("reg.glm在列", "glm" in cls["openai_chat"])
    check("reg.kimi在列", "kimi" in cls["openai_chat"])
    # 就绪检查（无 env → not_ready，如实不报错）
    os.environ.pop("DEEPSEEK_API_KEY", None)
    rd = reg.readiness("deepseek")
    check("reg.未配置→not_ready如实", rd["ready"] is False and rd["key_set"] is False)
    os.environ["DEEPSEEK_API_KEY"] = "test-only"
    os.environ.setdefault("DEEPSEEK_BASE_URL", "https://example.invalid")
    rd2 = reg.readiness("deepseek")
    check("reg.配置→ready", rd2["ready"] is True)
    del os.environ["DEEPSEEK_API_KEY"]
    if "DEEPSEEK_BASE_URL" in os.environ and os.environ["DEEPSEEK_BASE_URL"] == "https://example.invalid":
        del os.environ["DEEPSEEK_BASE_URL"]
    rdw = reg.readiness("llama")
    check("reg.本地权重→ready走耦合", rdw["ready"] is True and "ModelAutoCouple" in rdw["note"])
    try:
        reg.get("不存在的基座")
        check("reg.未知基座→KeyError", False)
    except KeyError:
        check("reg.未知基座→KeyError", True)
    cp = reg.coupling_plan()
    check("reg.耦合方案含三重门", "三重门" in json.dumps(cp, ensure_ascii=False))
    check("reg.耦合方案零出站", "空集" in json.dumps(cp, ensure_ascii=False))
    check("reg.封口密语", reg.SEAL == SEAL)

    print("\n===== 实验田汇总: PASS=%d FAIL=%d =====" % (PASS, FAIL))
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
