# 安全分级自评表（L1–L5）· 2026-11-19

> schema: `HOLOAEON-SECURITY-SELF-ASSESSMENT/1.0`
> `self_assessed=true` —— **本表为自评估，非第三方认证，不写成「获证」**。
> 对照依据：《智能助手类智能体安全分级规范与建设指南》（2026-06-10，新华网 / 信通院等公开发布）公开分级表。本表只对照公开能力项，不伪造条文编号与测评结论。
> 结论档位：**L3–L4（自评）**。
> 桃花庵出品 · 封存密令「潮起开门，潮落闭嘴」。

## 一、自评结论

| 项 | 值 |
|---|---|
| 自评档位 | **L3–L4** |
| 档位含义（自评口径） | L3：全生命周期留痕、判据可回读、关键不变量有门禁；L4：对中高级风险具备结构性韧性（零依赖 / 凭据零明文 / 出站白名单空集 / 金丝雀先红后绿）。 |
| 未达档位 | **L5 未达**：无第三方测评机构认证、无受监管生产级部署资质；本仓为离线研究 / 工程基线，不对外提供在线服务。 |
| 评估日期 | 2026-11-19 |
| 评估方式 | 代码级证据 + 现场回读命令；不引用未实测的承诺值。 |

## 二、分级能力项逐条自评

| # | 能力项（公开分级表口径） | 自评档位 | 代码级证据 | 回读命令（本机现场可复跑） |
|---|---|---|---|---|
| 1 | 身份与权限最小化 | L3 | 本地离线运行，无外联账号、无在线服务；出站白名单为空集，且为结构性不变量而非可配置策略项 | `python -X utf8 -c "from bridges.site_gateway import OUTBOUND_ALLOW; print(OUTBOUND_ALLOW)"`（应输出 `()`） |
| 2 | 输入校验与内容护栏 | L3 | 红线扫描（禁违禁词 / 夸大表述）、claims_gate 十三面判据、redline 扫描 0 违规 | `python scripts\redline_scan.py`；`python -m holoaeon.claims_gate verify` |
| 3 | 全生命周期留痕（append-only） | L3 | 台账只追加不覆盖：`data/claims_registry.json`、玉安 `version_history.json`；批次更正另开补正条，禁删史 | `python -X utf8 -c "import json,io; r=json.load(io.open('data/claims_registry.json',encoding='utf-8')); print(r['totals'])"` |
| 4 | 产物完整性（逐行 SHA） | L3 | `SHA256SUMS` 清单 + `check_sums.py` 复算闸；规定针 `source_sha16` 漂移即红 | `python scripts\check_sums.py` |
| 5 | 快照与回滚 | L3 | git 提交快照；改动前备份至 `_holoaeon_devtools/backups/`；当日锚点 `ANCHOR_YYYYMMDD_*.md` 记还原点 | `git -C F:\doubaowork\holoaeon log --oneline -5` |
| 6 | 关键不变量维度锁 | L3 | 12 维度 + 7 闸；`verify:false` 快照项显式声明、永不判 FAIL；锁被改动即门禁红 | `python scripts\check_dimension_lock.py` |
| 7 | 供应链韧性（抵御投毒） | L4 | 核心包 `holoaeon/` 零第三方依赖，`pyproject.toml` `dependencies = []`；零网络 import | `python -X utf8 -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['dependencies'])"`（应输出 `[]`） |
| 8 | 凭据零明文 | L3 | 凭证节点只登记指针 + 状态 + 掩码指纹，不复制明文；令牌存于用户目录令牌文件 / Windows 凭据管理器，输出一律掩码 | `python -X utf8 -c "import json,io; r=json.load(io.open(r'F:\doubaowork\holoaeon_memory\credential_registry.json',encoding='utf-8')); print([e['id'] for e in r['entries']])"` |
| 9 | 出站边界 | L3 | `bridges/site_gateway.py` `OUTBOUND_ALLOW = ()` 空集；入站升级包须 SHA256 合法 + 机构审批 + staging 隔离（部署侧网关执行，本仓只发裁决） | 见第 1 项命令；`bridges/site_gateway.py#L38` |
| 10 | 韧性与先红后绿 | L4 | 每面判据配金丝雀（改错必红）；diff0 双口径复现；五地回读同头才收口；门禁可复算 | `python scripts\v3_gate.py`；`python -m unittest discover -s tests` |

## 三、全生命周期证据链（L3 落点）

1. **立项 / 投喂**：`AGENT_FEED_V88_*.md` 落仓根（不提交），执行后归档 `_DONE`。
2. **落盘 / 测试**：先写金丝雀证明判据能拦错（先红），再转绿；测试入 `tests/`，零第三方 import。
3. **留痕**：批次三件 = 回执 `reports/v88_receipt.json` + 锚点 `ANCHOR_20261119_*.md` + 台账 `version_history.json`（stage 幂等）。
4. **完整性**：清单重建后 `check_sums.py` 0 不匹配；注册簿 `self_digest` 自指防改。
5. **回滚**：改动前 `shutil.copyfile` 备份；提交窗口内活体产物归位，不把运行期生成物钉进清单。

## 四、抵御中高级风险证据（L4 落点）

- **供应链投毒**：核心包零依赖，不安装任何第三方发行包；对 2026-11-17 微软 `agent-framework` PyPI 投毒事件（恶意版 1.26.1 / 1.26.2、`.pth` 启动级凭据窃取、周下载约 4.1 万、扫 60 凭据文件 / 读 300 进程环境变量）在结构上不引入该攻击面。
- **凭据泄露**：仓内不存明文令牌；凭证节点只存指针与掩码指纹；输出 / 回执 / 日志一律掩码。
- **越权外联**：出站白名单空集为结构性保证；模型耦合与入站裁决均 report-only，实际网络动作由部署侧网关执行。
- **静默漂移**：规定针 `source_sha16` 整文件哈希比对，源字节一变即红；`self_digest` 防注册簿事后篡改。

## 五、边界三条款（供应链登记，原样保留）

1. 零依赖**仅覆盖核心包 `holoaeon/`**；`bridges/` 部署环境除外，其依赖由部署侧负责。
2. 装入**已含恶意包的宿主环境**时，宿主 `.pth` 仍会被解释器执行，**本仓不能保护宿主**。
3. 正确表述是「**不引入该风险**」，**不是「能防御该风险」**；本仓不承诺对已投毒环境的清除能力。

## 六、诚实边界（未达 / 不主张）

- 本表是**自评估**，未经过第三方测评机构认证；任何对外材料不得写成「获证 / 认证通过」。
- 零依赖、零出站、凭据零明文的证据均限于本仓代码与本机配置；宿主操作系统、部署网关、第三方账号环境不在本仓保护范围。
- L5 所要求的受监管生产级部署、外部审计与持续监测，本仓当前不具备。
- 本仓为离线工程基线，`neural=false`、`claim=0`、确定性复现；不替代临床决策与合规审批。
