# Cookbook 03 · 把 HoloAeon 离线部署到一台旧笔记本

目标：在 2GB 内存、无网络、Python 3.8+ 的旧机器上跑起来，并跑完整套自检。
前置：一台能装 Python 的旧机；一个 U 盘或内网拷贝通道（全程不需要联网）。
实测基线：内核装配 ≈31ms、峰值内存 1.69MiB、25 智能体 / 47 技能（v0.9.1）。

## 第 1 步 · 离线取包

在能联网的机器上打包，拷到旧机：

```powershell
git clone https://github.com/weideyouni/holoaeon.git
Copy-Item -Recurse holoaeon D:\holoaeon
```

没有 git 就下载 zip 解压。**不要**在旧机上 `pip install -r`——本项目 `dependencies=[]`，
一个第三方包都不需要。若解压后看到 `.venv`、`node_modules` 之类目录，说明你拿错了包。

## 第 2 步 · 确认 Python 版本

```powershell
python -V
```

必须是 3.8 及以上。Windows 7 上官方最后一个可用版本是 Python 3.8（3.9+ 不再支持 Win7），
这也是本项目的下限；Win10/11 用 3.10~3.13 都实测通过（本基线跑在 3.13）。

## 第 3 步 · 三行验证

```powershell
cd D:\holoaeon
python scripts\launch_local.py status
python scripts\launch_local.py demo
```

预期 `status`：`has_graph=True  has_adapter=True`。
预期 `demo`：总线 25 个地址、记忆四层计数、外部融合「低成本→local / 长上下文→cloud」、末行 `all_ok: True`。

这一条 `demo` 就是「内部融合协议 + 外部融合协议」的现场证据：
内部走总线投递信封，外部走 model_adapter 的本地/云端分流。

## 第 4 步 · 跑自检与单测

```powershell
python scripts\launch_local.py selftest      # 预期 ==> 24/24
python -m unittest discover -s tests         # 预期 Ran 34 tests ... OK
python -m unittest discover -s tests\verax   # 预期 Ran 16 tests ... OK
python -m unittest discover -s tests\v3      # 预期 Ran 5 tests ... OK
```

两条 `unittest discover` 必须分开跑：合并会把 34 项口径搅在一起，这是已知坑。

## 第 5 步 · 红线与公开基准

```powershell
python scripts\redline_scan.py               # 预期 干净（零违规）
python benchmarks\bench_public.py            # 预期 BENCH_EXIT=0
```

基准会打印三个数字：`DIFF=0 <hash>` / 拦截 100% / 冷装配 ~31ms、峰值 ~1.7MiB。
换机器后 DIFF=0 的哈希应当不变（物理量与机器规格都不进哈希）；拦截率与足迹允许变。

## 第 6 步 · 旧机上的取舍

| 症状 | 处理 |
|---|---|
| 启动慢于 3 秒 | 老机械盘 + 冷 import；改用 `python -X importtime` 看是不是磁盘问题，别改代码 |
| 内存吃紧 | 只装必要领域包：`get_pack('writing').install(k)`，别一次装 16 个 |
| PowerShell 5 中文乱码 | 用 `-Encoding utf8` 写文件；或 `$env:PYTHONUTF8='1'` 后再跑 |
| Win7 上 `pwsh` 不存在 | 全部命令改用 `powershell`（5.x）语法，本项目脚本本身不依赖 pwsh |

## 第 7 步 · 确认「零依赖」真的成立

```powershell
Select-String -Path pyproject.toml -Pattern "dependencies"
```

预期看到 `dependencies = []`。如果这一行变了，说明有人偷偷加了依赖，直接拒绕合入。

## 常见错误

| 现象 | 原因 | 处理 |
|---|---|---|
| `ModuleNotFoundError: holoaeon` | 在错误的目录跑脚本 | 必须在仓库根目录执行 `scripts\launch_local.py` |
| `No module named pytest` | 本项目不用 pytest | 用 `python -m unittest discover` |
| 自检 `24/24` 但某项静默跳过 | 早期 `selftest` 无 `__main__` 入口的坑 | 用 `python scripts\launch_local.py selftest`，不要用 `python -m holoaeon.selftest` |
| 门禁变黄 | 回执里出现无来源的 `measured` | 老老实实标 `simulated`，别把仿真写成实测 |

## 下一步

- 想给旧机加可视化：`python scripts\ledger_view.py --sample data\ledger_sample.jsonl` 生成单文件 HTML；
- 想接入自己的模型：读 `docs/model-adapter.md`，`ModelBackend` 里填本地端点即可，仍不引入第三方依赖；
- 想给别人复现你的结论：把 `benchmarks/results-*.json` 一起交付，别只给截图。
