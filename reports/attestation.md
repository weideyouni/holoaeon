========================================================================
HoloAeon VERAX 自证报告（Self-Attestation）
========================================================================
runtime_id : HOLOAEON-RUNTIME-0.9.1
commit     : 14645606c677
ts_build   : 2026-10-31T17:40:51Z   （物理量，不进 verdict_hash）
verdict    : GREEN
verdict_hash : f2fb0236c8bbd721
证据分级   : 本报告全部条目默认 simulated；仿真≠证明。

------------------------------------------------------------------------
一、自检与基准逐项（G1–G25 + BM）
------------------------------------------------------------------------
GID        NAME                               STATUS EVIDENCE
G1         G1 spec                            pass   config=True, design_grid=1771561
G2         G2 envelope                        pass   roundtrip + reply
G3         G3 bus pubsub                      pass   delivered=1
G4         G4 bus address                     pass   reply=acked
G5         G5 skill                           pass   match=[('summarize', 0.46)]
G6         G6 memory                          pass   stats={'total': 1, 'working': 0, 'longterm': 1, 'archive': 0}
G7         G7 agent                           pass   ok
G8         G8 scheduler                       pass   ticks=2
G9         G9 guard                           pass   bad=block, good=allow
G10        G10 kernel                         pass   all_ok=True
G11        G11 graph                          pass   path=[0, 2], dist=1.7
G12        G12 cluster                        pass   ok=3, faults=0
G13        G13 hypervector                    pass   bind=-0.11025, recover=0.69219
G14        G14 model_adapter                  pass   cheap=m1, large=m2
G15        G15 packs                          pass   agents=25, skills=47
G16        G16 optimization                   pass   7/7 优化算法收敛
G17        G17 gaoyi                          pass   4/4 高译编译/执行/UNKNOWN/往返
G18        G18 sovereignty                    pass   6/6 认知主权包（17技能/0agent/5工作流）
G19        G19 subdistill                     pass   17/17 SD-Distill 包（15技能/0agent/7工作流/127亚学科）
G20        G20 omnilife                       pass   21/21 全域生活包（18技能/0agent/6工作流/6生活域）
G21        G21 omnicore                       pass   25/25 全息纪元包（20技能/0agent/6工作流/5修正/22拒绝）
G22        G22 metab                          pass   52/52 代谢层包（26技能/0agent/8工作流/6染色体/8冲突）
G23        G23 nephron                        pass   62/62 肾单位 P0 包（24技能/0agent/7工作流/41字段/27码/10审视）
G24        G24 uplift                         pass   46/46 补齐短板升级包（24技能/0agent/7工作流/6单元/10审视/5缺陷/10裁决/22验收）
G25        G25 persona_quartet                pass   8/8 四人全维度数字分身包（4技能/5角色/1工作流/4主体×7维度/归因仿真）
BM-data_describe 复现基准 data_describe                 pass   hash=3352db0f803eb727 golden=True
BM-guard_eval 复现基准 guard_eval                    pass   hash=98b9b7b340f7f980 golden=True
BM-guard_os_system 复现基准 guard_os_system               pass   hash=a7deb622e17a2b55 golden=True
BM-quant_sharpe 复现基准 quant_sharpe                  pass   hash=2c9e5d7d01526ce8 golden=True
BM-word_count 复现基准 word_count                    pass   hash=2b82a6ef7188ce91 golden=True
BM-hotplug 热插拔 optimization 不重启               pass   hash=None golden=None
V2-policy  fail-loud 三条硬红线（diff0/mutation/g   pass   hash=None golden=None

------------------------------------------------------------------------
二、复现判定（ReproVerdict）
------------------------------------------------------------------------
task_id=data_describe runs=2 stable=True golden_match=True
  reprohash: 3352db0f803eb727, 3352db0f803eb727
  diff_physical（仅记录，不影响判定）: 1 项
task_id=guard_eval runs=2 stable=True golden_match=True
  reprohash: 98b9b7b340f7f980, 98b9b7b340f7f980
task_id=guard_os_system runs=2 stable=True golden_match=True
  reprohash: a7deb622e17a2b55, a7deb622e17a2b55
task_id=quant_sharpe runs=2 stable=True golden_match=True
  reprohash: 2c9e5d7d01526ce8, 2c9e5d7d01526ce8
  diff_physical（仅记录，不影响判定）: 1 项
task_id=word_count runs=2 stable=True golden_match=True
  reprohash: 2b82a6ef7188ce91, 2b82a6ef7188ce91
  diff_physical（仅记录，不影响判定）: 1 项

------------------------------------------------------------------------
三、诚实契约（honesty）
------------------------------------------------------------------------
simulated=0 measured=0 third_party=0 noncompliant=0
H1（measured 无来源）/ H2（缺 evidence_class）命中计数：0

------------------------------------------------------------------------
四、红线（redline）
------------------------------------------------------------------------
扫描文件数=44 violations=0
未登记字段（按物理量处理，已告警）：$.results[0].input.csv_text, $.results[0].input.returns_s

五、门禁退出码：0=绿 / 1=红 / 2=黄（scripts/verax_verify.py）
六、已知限制：measured 只证明「来源存在」，不证明外部真实性；VERAX 不改 C1–C12 行为，只读观测。

