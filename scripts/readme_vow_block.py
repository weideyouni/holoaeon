# -*- coding: utf-8 -*-
"""V89-A README 主旨块插入件（两段插入文本 + 插入点说明）

插入块 A（中文）→ README.zh-CN.md：
  插入点：『## 一、项目宣言』节内，"它不承诺"智能"，它承诺**可检验**。"
  段落之后、"---"分隔线与"## 二、项目公理"之前。
插入块 B（英文镜像）→ README.md：
  插入点：项目宣言对应节（Engineering Manifesto / 项目宣言英文对应段落）
  之后，作为独立小节 "## The Vow (济世救民)"。

纪律：两块均为纯文字愿景段——零数字、零承诺、零徽章，不触碰任何
claims 口径；插入后须复跑 readme 对账闸与主套 discover 确认零回退。
"""

ZH_BLOCK = """
### 济世救民（主旨 · 合作方与总裁方版）

济世救民在这个仓里不是抒情，是三条可验证的工程条款：

1. **领域是真的**——药品查表、康复工程、慢病管理、教学量规，五个领域
   闸门全是真实现，不是玩具演示；
2. **诚实是结构性的**——不伪造临床证据、不主张意识觉醒，这两条"不做
   什么"与"做什么"同权重地写进了公理：一个系统的底线不在它宣称的上限，
   在它拒绝的下限；
3. **判断可失败**——每个承诺都挂着闸口，FAIL 即红，不折叠成"通过"。
   把"救人"从形容词做成判据，是这个仓存在的理由。

> 我，凡人一枚，有心报国。
> 九年从手术刀走到框架，不为热闹——为的是把"救人"两个字，
> 做成可复算的判据。
> 这套系统有没有人用，我都会一直做下去；做下去本身，就是意义，
> 就是我一生的事业。
> 愿我们的国家，在人工智能赋能的改造中一切顺利；
> 愿技术去到资源最少的地方，而不是参数最多的地方。
"""

EN_BLOCK = """
## The Vow (济世救民)

"To save lives and serve the people" is not sentiment here — it is three
verifiable engineering clauses:

1. **The domains are real** — medication lookup, rehabilitation
   engineering, chronic-disease management, teaching rubrics: five domain
   gates, all working implementations, no toy demos.
2. **Honesty is structural** — we do not fabricate clinical evidence and
   we do not claim machine consciousness. What a system refuses to do
   defines it as much as what it does; both are written into the axioms.
3. **Judgments can fail** — every promise hangs on a gate that can go
   red. Turning "saving lives" from an adjective into a test is the
   reason this repository exists.

> I am an ordinary person, with a heart for my country.
> Nine years from the scalpel to the framework — not for the noise, but
> to turn the words "saving lives" into recomputable judgments.
> Whether or not anyone uses this system, I will keep building it;
> the building itself is the meaning — it is my life's work.
> May our country's transformation through AI go steadily and well;
> may the technology reach where resources are scarcest,
> not where parameters are most.
"""

if __name__ == "__main__":
    import json
    print(json.dumps({
        "zh_insert_after": "它不承诺\"智能\"，它承诺**可检验**。（README.zh-CN.md 项目宣言节内）",
        "zh_block_bytes": len(ZH_BLOCK.encode("utf-8")),
        "en_block_bytes": len(EN_BLOCK.encode("utf-8")),
        "discipline": "零数字零承诺零徽章，插入后复跑 readme 对账闸与主套 discover",
    }, ensure_ascii=False, indent=1))
