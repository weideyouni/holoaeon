"""24 个设计语汇命令（本地化口径）。

来源范式：Impeccable（作者 Paul Bakaus，Apache-2.0，github.com/pbakaus/impeccable）README 的
"24 commands" 分组表。本仓只沿用"命令即词汇、每个命令一个可执行动作"的范式，命令的中文释义由
本仓自写，不复制上游文案；上游仍有 62 条规则，本仓规则见 detectors.py（自写 12 条，不做等量宣称）。
"""

GROUP_STEER = "steer"
GROUP_REVIEW = "review"
GROUP_FINISH = "finish"
GROUP_ITERATE = "iterate"
GROUP_PLAN = "plan"

GROUPS = (GROUP_STEER, GROUP_REVIEW, GROUP_FINISH, GROUP_ITERATE, GROUP_PLAN)

# (id, group, 中文释义, 作用目标)
COMMANDS = (
    ("bolder", GROUP_STEER, "把过于保守的设计放大：主视觉、对比与尺度都往前推", "页面/区块"),
    ("quieter", GROUP_STEER, "把过响的界面压下去：降饱和、降密度、让主体说话", "页面/区块"),
    ("distill", GROUP_STEER, "删掉页面不需要的东西，只留一个主叙事", "页面"),
    ("colorize", GROUP_STEER, "给灰掉的界面补回有依据的色彩体系", "组件/区块"),
    ("typeset", GROUP_STEER, "修字体、层级与字号，让阅读顺序立起来", "文本层"),
    ("layout", GROUP_STEER, "修间距与节奏，对齐栅格，去掉拥挤与空洞", "布局"),
    ("animate", GROUP_STEER, "加过渡与交互反馈，只加解释状态变化的那部分", "交互"),
    ("delight", GROUP_STEER, "加人格化细节，但要克制、可关", "细节"),
    ("overdrive", GROUP_STEER, "上重效果：着色器、弹性物理、滚动驱动，先备降级", "特效"),
    ("critique", GROUP_REVIEW, "按可用性启发做打分式评审，排出先修顺序", "整屏/组件"),
    ("audit", GROUP_REVIEW, "技术质量报告：无障碍、性能、主题、响应式，按 P0–P3 分级", "整屏"),
    ("polish", GROUP_FINISH, "上线前最后一遍：一致性、边角、状态", "整屏"),
    ("harden", GROUP_FINISH, "兜错误、国际化、溢出与边界场景", "整屏"),
    ("clarify", GROUP_FINISH, "重写不清楚的文案，保留事实不改口径", "文案"),
    ("adapt", GROUP_FINISH, "适配屏幕尺寸与设备，窄屏不塌、不裁切", "响应式"),
    ("optimize", GROUP_FINISH, "修加载与渲染性能，先量化再改", "性能"),
    ("onboard", GROUP_FINISH, "设计首次使用流程与空状态", "流程"),
    ("live", GROUP_ITERATE, "在浏览器里选元素、切变体、现场写回源码", "本地页面"),
    ("generate", GROUP_ITERATE, "按名字批量产出同一元素的多个变体", "组件"),
    ("shape", GROUP_PLAN, "写代码前先把 UX 结构与信息层级定下来", "策划"),
    ("init", GROUP_PLAN, "写 PRODUCT.md：用户、目标、约束", "项目上下文"),
    ("document", GROUP_PLAN, "写 DESIGN.md：把既有视觉系统记下来", "设计系统"),
    ("extract", GROUP_PLAN, "把重复出现的模式收进设计系统", "设计系统"),
    ("craft", GROUP_PLAN, "上游已弃用的别名，等同一次普通构建请求", "构建"),
)


def command_ids() -> tuple:
    """返回全部命令 id（含已弃用别名）。"""
    return tuple(c[0] for c in COMMANDS)


def by_group(group: str) -> tuple:
    """按分组取命令，未知分组返回空元组。"""
    if group not in GROUPS:
        return ()
    return tuple(c for c in COMMANDS if c[1] == group)
