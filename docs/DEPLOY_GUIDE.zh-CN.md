# HoloAeon 机构端部署手册（工程师版）

> 对象：机构端（社区卫生服务中心/卫生院级，辖区 3-4 万人）实施工程师。
> 版本基准：DOC 0.9.41（V47 部署域收口后）。本手册只写仓内已实测能力。
> 一键自检：`python scripts/install_check.py` → 7/7 PASS 即安装就绪。

## 一、这是什么（概念逻辑）

HoloAeon 是**零依赖、确定性、离线优先**的大模型对接认知框架（Python 库载体）：
- **零依赖**：`pip` 装完即用，无编译链、无原生库、无第三方包（`dependencies = []`）。
- **确定性**：所有打分/检索/校验可复算（同输入必同输出），无模型权重漂移。
- **离线优先**：核心包零网络；内网可全程自主运行；外网只进升级信息（网络二极管）。
- **不是模型**：接入大模型（本地小模型或服务器模型）后获得 AI 属性；引擎本体=规则与编排。

**领域编排环（ring0-15）**：每个领域一个确定性闸门模块——
教学(teach_gate)/学术(academic_gate)/公共卫生(phc_chronic_engine+phc_recall)/
工艺(craft_gate+twin_verify)/药品(pharma_gate)/部署(deploy_gate)等。

## 二、底层原理（六机制与向量库）

| 机制 | 仓内落点（工程师可直接 import 验证） |
|---|---|
| 全息心跳 | `holoaeon.bus.Bus.heartbeat()` / `craft_gate.Heartbeat` |
| 细胞骨架 | `holoaeon.kernel`（Kernel） |
| 皮肤机制 | `holoaeon.guard`（Guard L1-L10） |
| 语义通信底座 | `holoaeon.bus`（Envelope） |
| 赫布协作场 | `holoaeon.graph.AdaptiveGraph.hebbian_step` |
| 经络机制 | `concept_anatomy.holo_meridian` → topology_resonance |

**轻量向量库原理（deploy_gate.VectorStore）**：
- 嵌入=字符 3-gram → sha256 派生向量 → bundle（neural=false，逐位可复现）。
- 检索=混合通道：`0.6×trigram余弦 + 0.4×bigram Dice`（字面+词汇双通道）。
- 基线实测（scripts/bench_vector_baseline.py）：字面查询 Top-1/Top-5=100%（~1.5ms）；
  同义改写 Top-5=33.3%——**诚实边界**：跨词汇语义召回需共现语料（semvec 路线）
  或 bridges 层神经旁挂（可选 side-car，主核零依赖不动）。
- 同级对齐：sqlite-vec / faiss-cpu 在 1e3-1e5 条目、毫秒级延迟口径同级；
  差异化=零依赖/确定性/离线。

**网络二极管原理（bridges/site_gateway.NetDiode）**：
- 出站白名单=**空集**：结构性零出站（非策略项，不可配置）——内网数据不出内网。
- 入站白名单=升级包：类型+SHA256+机构审批三重门 → staging 隔离区 → 检后装载。
- 内外网协议在网关边界适配（PROTOCOL_MATRIX），两侧不直连。

## 三、实现途径（包结构导览）

```
holoaeon/            核心包（零网络零第三方 import）
  phc_chronic_engine.py   公卫慢病引擎（V41：危险度R01-R12/MDT/随访/端口池/等保MLPS3）
  phc_recall.py           召回层（V42：七类本体/六系统分片/预计算嵌入）
  pharma_gate.py          药品域（V46：医保登记表精确查表/零剂量/四态）
  deploy_gate.py          部署域（V47：VectorStore/MemoryStore/TerminalPool/容量）
  teach_gate.py 等        其余领域闸门
bridges/              可选层（网络语义在此，删除即回滚）
  local_model_probe.py    本地模型探测器（V46）
  site_gateway.py         现场网关（V47：模型耦合+网络二极管）
scripts/              运维脚本
  install_check.py        安装自检（V48）
  bench_vector_baseline.py 向量库基线（V47）
  check_sums.py           SHA 清单复算闸（V38）
tests/                测试套（安装后可全量回归）
```

## 四、落地场景（第一个实战项目口径）

- 辖区 3-4 万人；35+ 建档与慢病管理（A类3病种：高血压/2型糖尿病/慢阻肺）。
- 流程：多模态投喂（检验/体检/实验室/脉象/舌象/耳象/目象——影像零像素只存 SHA 指针）
  → 危险度打分（R01-R12，四档分级）→ MDT 路由 → 随访调度（≥4次/年，2周复访规则）
  → 知识召回（VectorStore）→ 药品查询（pharma_gate 精确查表）。
- 医疗红线：**零诊断零处方零像素零网络**；决策权归执业医师；保持教学/科研/管理工具定位。

## 五、安装步骤（穷举）

1. **环境要求**：Python ≥ 3.10（3.13 实测通过）。无其他要求——无 GPU、无编译器、无数据库服务。
2. **获取**：`git clone https://github.com/weideyouni/holoaeon.git`（或机构内部镜像分发，内网离线拷贝亦可）。
3. **安装**（二选一）：
   - 源码直用：`cd holoaeon && pip install -e .`（零依赖，秒装）；
   - 纯拷贝：把 `holoaeon/`、`bridges/`、`scripts/` 三目录拷入项目，`sys.path` 指向仓库根即可。
4. **验证**：`python scripts/install_check.py` → 预期 `7/7 项通过 / 安装就绪`。
   任一 FAIL 按其 detail 排查（见 §九）。
5. **基线**：`python scripts/bench_vector_baseline.py` → 预期字面组 100%、同义组 Top-5≈33%
   （机器差异允许毫秒级波动，命中率应一致）。

## 六、调试说明（穷举，每步含命令/预期/故障分支）

### 6.1 本地模型发现与耦合
```
python -c "import importlib.util,os,json;
spec=importlib.util.spec_from_file_location('lp','bridges/local_model_probe.py');
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m);
print(json.dumps(m.discover(),ensure_ascii=False,indent=2))"
```
- 预期：services 三行（ollama/lmstudio/vllm 各 up/down）、gguf_files 清单、packages 探测。
- 故障分支：全 down 且无 gguf → 安装 ollama（`ollama pull qwen2.5:1.5b` 量级模型）或放置 GGUF 文件于 `~/models/`。
- 耦合：`ModelAutoCouple.couple(discovery)` → 产出耦合配置单（endpoint）；实际连接由部署侧执行。

### 6.2 向量库建库与检索
```
python -c "from holoaeon.deploy_gate import VectorStore;
vs=VectorStore(dim=256, store_path='mykb.jsonl');
vs.batch_add([('k1','高血压患者应定期测量血压',{}),('k2','糖尿病饮食指导',{})]);
print(vs.search('血压', top_k=2)); vs.save(); print(vs.stats())"
```
- 预期：hits 排序、latency_ms 毫秒级、save 后 mykb.jsonl 存在。
- 故障分支：duplicate id 报错 → 换 id；检索空 → 检查 store_path 装载（`vs.load()`）。

### 6.3 网络二极管验证
```
python -c "import importlib.util;
s=importlib.util.spec_from_file_location('sg','bridges/site_gateway.py');
g=importlib.util.module_from_spec(s); s.loader.exec_module(g);
print(g.NetDiode.outbound('任何请求')); print(g.gateway_report())"
```
- 预期：outbound=BLOCK（白名单空集）；gateway_report 出协议矩阵。

### 6.4 药品登记表
```
python -c "from holoaeon import pharma_gate as pg;
reg=pg.build_default_registry(); print(reg.lookup('二甲双胍片（示例）'));
print(reg.version_pin())"
```
- 预期：found=True/甲类/simulated；version_pin 出年份与来源。
- **部署侧动作**：以国家医保局官方目录替换示例条目（evidence_class 改 measured，带文号年份）。

### 6.5 终端池与扩容
```
python -c "from holoaeon.deploy_gate import TerminalPool;
tp=TerminalPool();
[tp.acquire('t%d'%i) for i in range(10)];
print(tp.acquire('t10')); print(tp.expand(20, approved=True))"
```
- 预期：t10 拒绝（limit=10）；approved=True 扩到 20 成功；31 拒绝（上限 30）。

### 6.6 全量回归
```
python -m unittest discover -s tests -q && python scripts/check_sums.py
```
- 预期：全绿；SHA256SUMS 零漂移。

## 七、参数调整步骤（穷举表）

| 参数 | 位置 | 默认 | 调整步骤 | 影响 |
|---|---|---|---|---|
| 辖区人口 | `deploy_gate.capacity_plan(population)` | 35000 | 传 30000-40000 内任意值 | 建档/随访容量估算 |
| 终端上限 | `deploy_gate.TerminalPool(default, reserved)` | 10/30 | 构造参数；扩容走 `expand(n, approved=True)` | 并发终端数（等保边界） |
| 检索 top_k | `VectorStore.search(query, top_k)` | 5 | 调用参数 | 返回条数与延迟 |
| 嵌入维度 | `VectorStore(dim=)` | 256 | 构造参数（256/512/1024） | 精度-内存权衡 |
| 混合权重 | `deploy_gate.VectorStore.search` 内 0.6/0.4 | 0.6/0.4 | 改源码常量并重跑基线 | 字面/词汇通道配比 |
| 危险度阈值 | `phc_chronic_engine.GRADES` | 70/50/30 | 改常量（每条规则 R01-R12 同文件可审） | 分级档位 |
| 随访频次 | `DISEASE_REGISTRY.A.*.followup_per_year` | 4 | 改常量（公卫口径，慎改） | 随访调度 |
| 端口探测超时 | `local_model_probe.probe_port(timeout)` | 0.3s | 调用参数 | 探测灵敏度 |
| 耦合优先级 | `site_gateway.ModelAutoCouple.PRIORITY` | ollama>lmstudio>vllm | 改元组顺序 | 首选后端 |
| **出站白名单** | `site_gateway.OUTBOUND_ALLOW` | **空集** | **不可调**（结构性零出站） | 安全边界 |
| 入站白名单 | `site_gateway.INBOUND_ALLOW` | 升级包 | 原则上不加（加=扩大攻击面） | 升级通道 |
| 医保类别 | `pharma_gate.VALID_CLASSES` | 甲/乙/非医保 | 不建议改（国家口径） | 查表合法性 |

## 八、升级路径（外网→内网）

1. 外网侧下载升级包 → 计算 SHA256（`NetDiode.digest_of(文件字节)`）。
2. 机构审批（审批卡=处置权分离）→ `NetDiode.inbound("upgrade_package", sha256=…, approved=True)` → ALLOW 落 staging/。
3. staging 检验（跑 install_check + 测试套）→ 通过后装载。
4. 任何出站请求一律 BLOCK——内网数据不出内网，无需配置。

## 九、故障排查表

| 现象 | 定位 | 处置 |
|---|---|---|
| install_check 零依赖 FAIL | detail 列出文件与 import 名 | 检查是否误装了带第三方依赖的分支 |
| 核心模块 import FAIL | 缺文件/路径 | 确认 `holoaeon/` 完整；sys.path 指向仓库根 |
| 向量检索空 | store 未 load | `vs.load()` 或重新 batch_add |
| 模型探测全 down | 未装本地模型 | 装 ollama 或放 GGUF；或确认服务已启动 |
| SHA256SUMS 漂移 | 改了包内文件未走批次流程 | 走 V38 复算闸流程重建（勿手改清单） |
| 测试套红 | 环境差异 | 对比失败用例名与提交批次说明 |

## 十、能力边界声明（诚实边界）

1. 零诊断零处方零急救指令——决策权归执业医师。
2. 同义改写召回 Top-5≈33%（字面 100%）——跨词汇语义需语料扩展或神经旁挂。
3. 出站结构性零——若机构需要数据上报，走人工导出+审批，不走本框架网络层。
4. 医保报销查询=精确查表——未登记≠非医保，以官方目录为准。
5. 影像零像素——判读委托人工/外部技能，本框架只存 SHA 指针与结构化自述。
6. NMPA 边界——保持教学/科研/管理工具定位，不跨入诊疗决策。

—— 手册完。安装有问题先跑 `python scripts/install_check.py`。潮起开门，潮落闭嘴。
