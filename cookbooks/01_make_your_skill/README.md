# Cookbook 01 · 十分钟做一个你自己的技能

目标：给 HoloAeon 加一个自己的技能（BMI 计算），跑通「注册 → 路由 → 执行」全链路。
前置：Python 3.8+，仓库根目录，**不需要 pip install 任何东西**。
耗时实测：10 分钟内可完成（本仓库实测代码见下，全部逐行跑过）。

## 第 1 步 · 站在仓库根目录

```powershell
cd F:\doubaowork\holoaeon
python scripts\launch_local.py status
```

预期输出（摘要）：

```
has_graph=True  has_adapter=True  agents=25  skills=47
```

`has_graph / has_adapter` 都为 True，说明内核与协作图已装好。若这一步就失败，先别看后面的步骤。

## 第 2 步 · 写技能函数

技能函数只收到**一个任务字符串**（内核路径不会把 payload 当关键字参数传进来），
所以参数写在句子里，用正则取出来。这一条是最容易踩的坑，实测确认过。

```python
import re

def bmi_calc(task, **kwargs):
    nums = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", task or "")]
    if len(nums) < 2:
        return {"ok": False, "error": "请给出身高(cm)与体重(kg)，例如「算一下 bmi 175 70」"}
    height, weight = nums[0] / 100.0, nums[1]
    value = round(weight / (height * height), 2)
    return {"ok": True, "bmi": value, "level": "正常" if 18.5 <= value < 24 else "需关注"}
```

## 第 3 步 · 声明清单（manifest）

```python
from holoaeon.skill import Skill, SkillManifest, SkillRegistry

reg = SkillRegistry()
reg.register(Skill(SkillManifest(
    name="bmi_calc",
    description="BMI 体质指数计算",
    inputs={"height_cm": "身高厘米", "weight_kg": "体重千克"},
    outputs={"bmi": "体质指数", "level": "分级"},
    tags=["health", "bmi"],
), bmi_calc))
```

`description` 与 `tags` 决定路由得分：既有 `Registry.score` 用 Jaccard + 字符 2-gram + 标签命中，
语义通道（`holoaeon/semvec.py`）可另加 0.75 权重（`scripts/bench_semvec.py` 的 `WEIGHT_SEM`，
配合基线噪声地板 `BASE_FLOOR=0.15`）。清单写得越具体，路由越准。

## 第 4 步 · 验证路由

```python
print(reg.match("算一下 bmi", 3))   # [('bmi_calc', 0.20757)]
```

实测返回 `[('bmi_calc', 0.20757)]`。数值低是正常的——短查询与长描述的字符 2-gram 重叠小，
只要目标技能排第一就算通过。

## 第 5 步 · 挂到智能体

```python
from holoaeon.agent import Agent
from holoaeon.kernel import Kernel

k = Kernel()
k.register_agent(Agent("health_coach", "health", skills=reg, skill_names=["bmi_calc"]))
```

`skill_names` 限定这个智能体只能用这一项技能，避免它去抢别的包。

## 第 6 步 · 端到端跑一次

```python
res = k.submit("算一下 bmi 175 70", to="health_coach")
print(res["all_ok"], res["results"][0]["output"])
```

预期输出：

```
True ok {'ok': True, 'bmi': 22.86, 'level': '正常'}
```

再确认守卫是活的：

```python
print(k.submit("执行 os.system('ls -la')")["results"][0]["status"])   # blocked
```

## 第 7 步 · 守住零依赖与红线

```powershell
python scripts\redline_scan.py
```

预期：`扫描文件数：41` / `结果： 干净（零违规）`。
新技能里不要出现 `os.system / eval( / subprocess` 这类调用，否则会被 L3 直接拦掉。

## 常见错误

| 现象 | 原因 | 处理 |
|---|---|---|
| `status='error'`，`err` 里 `'str' object has no attribute 'payload'` | 把技能函数当成收信封来写 | 技能签名是 `fn(task, **kwargs)`，参数从任务串取 |
| 输出里参数全是 0 / 报「请给出身高」 | 任务串里没写数字 | 把数字写进任务，如 `算一下 bmi 175 70` |
| `status='no_skill'` | `match` 没命中 | 补 `description` 与 `tags`，让词面对齐 |
| 提交被 `blocked` | 命中危险模式或越权 | 去掉危险调用；不要伪造 `as_identity` |

## 下一步

- 把技能放进领域包：`holoaeon/packs/<pack>.py` 里追加，再 `get_pack(key).install(k)`；
- 给技能加语义路由：读 `holoaeon/semvec.py` 与 `scripts/bench_semvec.py`，按 0.75 权重 + 噪声地板混合；
- 想让它可审计：读 Cookbook 02，给这个智能体加账本。
