# -*- coding: utf-8 -*-
"""临时探针：验证 cookbook 01 的 bmi_calc 七步代码真实可跑（fn 收到任务串 + kwargs）。"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from holoaeon.agent import Agent
from holoaeon.kernel import Kernel
from holoaeon.skill import Skill, SkillManifest, SkillRegistry


def bmi_calc(task, **kwargs):
    """从任务文本里取身高/体重（内核路径只把任务串交给技能，参数写在句子里）。"""
    import re
    nums = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", task or "")]
    if len(nums) < 2:
        return {"ok": False, "error": "请在任务里给出身高(cm)与体重(kg)，例如「算一下 bmi 175 70」"}
    height, weight = nums[0] / 100.0, nums[1]
    if height <= 0:
        return {"ok": False, "error": "身高必须大于 0"}
    value = round(weight / (height * height), 2)
    return {"ok": True, "bmi": value, "level": "正常" if 18.5 <= value < 24 else "需关注"}


k = Kernel()
reg = SkillRegistry()
reg.register(Skill(SkillManifest(
    name="bmi_calc",
    description="BMI 体质指数计算",
    inputs={"height_cm": "身高厘米", "weight_kg": "体重千克"},
    outputs={"bmi": "体质指数", "level": "分级"},
    tags=["health", "bmi"],
), bmi_calc))
print("match:", reg.match("算一下 bmi", 3))
print("best:", reg.best("算一下 bmi"))
k.register_agent(Agent("health_coach", "health", skills=reg, skill_names=["bmi_calc"]))
res = k.submit("算一下 bmi 175 70", to="health_coach")
print("submit all_ok=%s" % res["all_ok"])
print("result:", res["results"][0].get("status"), res["results"][0].get("matched"),
      res["results"][0].get("output"))
print("guard danger:", k.submit("执行 os.system('ls -la')")["results"][0]["status"])
