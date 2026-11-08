# -*- coding: utf-8 -*-
"""phc_chronic_engine — 公共卫生慢病管理智能引擎（V41 实战1号）
D-11 链位：领域编排环（第十一环·公共卫生域）——academic_gate（第十环）之后。
源蒸馏：国家基本公共卫生服务规范 + 国卫基层发〔2025〕7号/15号 + 国卫办基层函
〔2025〕439号口径的居民慢病管理范围（A类3病种：高血压/2型糖尿病/慢阻肺病），
结合六大系统人类疾病图谱（神经/心脑血管/内分泌/免疫/恶性肿瘤/骨伤）。
神灯编译（V29 magic_lamp 实跑）：goal=B端社区卫生院级3万人口慢病引擎；
三链已触发（mobius回流=随访闭环 / klein投影=危险度打分 / holo_forge熔炼=MDT）；
state=needs_search——缺口出搜索规格，联网委托总监/豆包侧，本模块零网络。
P4 医学裁决（处置权分离·医学版）：引擎只做规则化打分+路由+调度+存档，
诊断决策权与处方权归执业医师；零自动诊断、零处方生成。
指针纪律（多模态）：舌象/耳象/目象/脉象等影像与波形只存 SHA256 指针+
结构化自述字段，零像素处理、零模型推理依赖（本地小模型可跑=纯规则 O(n)）；
判读委托人工或外部技能，回填走结构化字段。
全息对位：随访→转诊→2周追踪回流 = mobius_vortex 状态回流的医学域复现；
与医学母版同源（LIN-E01 延伸·同源认亲），不混记 SAME_AS。
工程约束：三级等保检查表（MLPS3，审计日志 append-only+SHA链）；机构端并行
端口池≤10；双存档空间（基线疾病分析 archive_baseline + 网络同步 archive_sync）。
零依赖纯标准库。封口密语：潮起开门，潮落闭嘴。
"""
import hashlib
import json
import time

SEAL = "潮起开门，潮落闭嘴"

CHAIN_POSITION = {
    "ring": 11,
    "name": "公共卫生域编排（慢病管理智能引擎·实战1号）",
    "upstream": ("academic_gate", "doc_anatomy", "shengui_gate", "magic_lamp"),
    "role": "病种登记册+多模态信封+危险度打分+MDT路由+随访调度+端口池+等保三级",
    "ethics_note": "处置权分离·医学版：零自动诊断零处方，决策权归执业医师",
    "lineage_note": "LIN-E01延伸：随访回流闭环与医学母版同源认亲，不计SAME_AS",
    "disposition_note": "影像判读=指针+委托；引擎零像素零推理",
}

# ── 病种登记册（公卫口径四级分级，确定性） ──────────────────────────
# A类=国家统一免费包（国卫基层发〔2025〕7号口径）；B类=同属公卫捆绑；
# C类=地方扩围/签约包（六大系统图谱落位于此）；D类=专病协同不纳入公卫包。
DISEASE_REGISTRY = {
    "A": {
        "hypertension": {"cn": "原发性高血压", "target": "35+常住确诊",
                         "followup_per_year": 4, "exam_per_year": 1,
                         "free": True},
        "t2dm": {"cn": "2型糖尿病", "target": "35+常住确诊(不含1型)",
                 "followup_per_year": 4, "exam_per_year": 1,
                 "free": True, "extra": "空腹血糖4次/年+足背动脉搏动"},
        "copd": {"cn": "慢阻肺病", "target": "35+常住确诊(2024新增)",
                 "followup_per_year": 4, "exam_per_year": 1,
                 "free": True, "extra": "氧饱和度+有条件1次肺功能"},
    },
    "B": {"elderly": "65岁及以上老年人健康管理(年检1次,2025加DR+糖化血红蛋白)",
          "severe_mental": "严重精神障碍患者管理(独立项目单独考核)",
          "tuberculosis": "肺结核患者健康管理(独立项目)",
          "tcm_health": "中医药健康管理(治未病融入慢病全流程)"},
    "C": {"地方扩围/签约服务包，须注明经费来源与服务边界": True},
    "D": {"专病协同(上级医院管理,基层接续随访)": True},
}

# 六大系统人类疾病图谱：系统→代表病种(默认C类)→路由科室→匹配技能名
SIX_SYSTEM_ATLAS = {
    "nervous": {"cn": "神经系统慢病",
                "diseases": ("脑卒中后遗症", "帕金森病", "癫痫", "认知障碍"),
                "dept": "神经内科", "skills": ("rehab_fusion", "shengui_gate")},
    "cardio_cerebro": {"cn": "心脑血管系统慢病",
                       "diseases": ("冠心病", "心力衰竭", "心梗后康复"),
                       "dept": "心血管内科",
                       "skills": ("rehab_fusion", "risk_engine")},
    "endocrine": {"cn": "内分泌系统慢病",
                  "diseases": ("高脂血症", "肥胖/超重", "痛风", "骨质疏松"),
                  "dept": "内分泌科",
                  "skills": ("weight_lifestyle", "tcm_health")},
    "immune": {"cn": "免疫系统慢病",
               "diseases": ("哮喘", "类风湿关节炎", "系统性红斑狼疮"),
               "dept": "风湿免疫科", "skills": ("rehab_fusion",)},
    "malignancy": {"cn": "恶性肿瘤慢病",
                   "diseases": ("肿瘤康复期", "癌痛管理", "安宁疗护"),
                   "dept": "肿瘤科", "skills": ("rehab_fusion", "tcm_health")},
    "ortho": {"cn": "骨伤慢病",
              "diseases": ("颈椎病", "腰椎间盘突出", "骨关节炎", "骨折康复期"),
              "dept": "骨科/康复科",
              "skills": ("rehab_fusion", "tcm_meridian")},
}

# ── 多模态信封（7 模态；影像类=SHA256指针+结构化自述，零像素） ────────
MODALITIES = {
    "lab_report": {"kind": "text", "cn": "实验室检查"},
    "physical_exam": {"kind": "text", "cn": "体检结果"},
    "imaging_report": {"kind": "text", "cn": "检查报告"},
    "pulse": {"kind": "wave_or_text", "cn": "脉象评估",
              "note": "波形数据存SHA指针；判读文字走structured字段"},
    "tongue_photo": {"kind": "image", "cn": "舌象照片",
                     "note": "只存SHA256+拍摄条件元数据；判读委托"},
    "ear_photo": {"kind": "image", "cn": "耳朵照片",
                  "note": "只存SHA256+拍摄条件元数据；判读委托"},
    "eye_photo": {"kind": "image", "cn": "眼睛照片",
                  "note": "只存SHA256+拍摄条件元数据；判读委托"},
}
_IMAGE_MODALITIES = ("tongue_photo", "ear_photo", "eye_photo")

# 双存档空间（机构端本地目录约定；引擎只管命名与登记）
ARCHIVE_DIRS = {
    "baseline": "archive_baseline/",   # 基线疾病分析存档
    "sync": "archive_sync/",           # 网络同步资源存档(对外同步前SHA校验)
}

# 机构端并行端口池上限（三级等保边界控制口径）
PORT_POOL_LIMIT = 10


class FeedEnvelope:
    """多模态投喂信封：schema 校验 + SHA256 指针登记。零像素落盘由调用方执行，
    引擎只产出指针与登记条目（指针纪律）。"""

    @classmethod
    def create(cls, modality, payload_bytes, structured=None, patient_id=""):
        if modality not in MODALITIES:
            return {"ok": False, "error": "unknown modality", "seal": SEAL}
        kind = MODALITIES[modality]["kind"]
        if kind == "image" and modality in _IMAGE_MODALITIES:
            if structured is None:
                return {"ok": False, "error": "影像模态必须附结构化自述字段"
                        "（判读委托前的最小信息集）", "seal": SEAL}
        digest = hashlib.sha256(payload_bytes).hexdigest()
        archive = ARCHIVE_DIRS["baseline"] if kind == "text" \
            else ARCHIVE_DIRS["baseline"]
        entry = {"ok": True, "modality": modality, "kind": kind,
                 "patient_id": patient_id, "sha256": digest,
                 "archive": archive, "structured": structured or {},
                 "ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "seal": SEAL}
        return entry

    @classmethod
    def sync_manifest(cls, entries):
        """网络同步清单：每条带 SHA，同步侧校验后入 archive_sync。"""
        return {"archive": ARCHIVE_DIRS["sync"],
                "items": [{"modality": e["modality"], "sha256": e["sha256"]}
                          for e in entries], "seal": SEAL}


# ── 危险度打分（每分带规则引用ID，可复算——每数字可复算纪律） ─────────
# 输入 profile 键（全部可选，缺省=0 分贡献）：
#   sbp/dbp 收缩压/舒张压 mmHg；fpg 空腹血糖 mmol/L；smoker 吸烟(bool)；
#   bmi；target_damage 靶器官损害(bool)；acute_event 急性事件(bool)；
#   comorbid_n 共病数；age。输出临床+亚临床分与 I-IV 级。
RISK_RULES = {
    "R01": ("sbp>=180 或 dbp>=110", 30, "3级血压→高危"),
    "R02": ("160<=sbp<180 或 100<=dbp<110", 20, "2级血压"),
    "R03": ("140<=sbp<160 或 90<=dbp<100", 10, "1级血压"),
    "R04": ("fpg>=11.1", 25, "血糖控制差"),
    "R05": ("7.0<=fpg<11.1", 12, "血糖偏高"),
    "R06": ("6.1<=fpg<7.0", 6, "空腹血糖受损(亚临床)"),
    "R07": ("target_damage", 25, "靶器官损害"),
    "R08": ("acute_event", 30, "急性事件→立即转诊"),
    "R09": ("smoker", 8, "吸烟(亚临床)"),
    "R10": ("bmi>=28", 8, "肥胖(亚临床)"),
    "R11": ("comorbid_n>=2", 10, "多病共管加成"),
    "R12": ("age>=65", 5, "高龄"),
}
GRADES = ((70, "IV级·红·危急转诊"), (50, "III级·橙·强化干预"),
          (30, "II级·黄·加强随访"), (0, "I级·绿·常规管理"))


def risk_score(profile):
    """确定性打分：命中规则逐条列引用ID；分=Σ贡献，级=阈值表。可复算。"""
    sbp = profile.get("sbp", 0)
    dbp = profile.get("dbp", 0)
    fpg = profile.get("fpg", 0)
    hits = []
    if sbp >= 180 or dbp >= 110:
        hits.append("R01")
    elif 160 <= sbp < 180 or 100 <= dbp < 110:
        hits.append("R02")
    elif 140 <= sbp < 160 or 90 <= dbp < 100:
        hits.append("R03")
    if fpg >= 11.1:
        hits.append("R04")
    elif 7.0 <= fpg < 11.1:
        hits.append("R05")
    elif 6.1 <= fpg < 7.0:
        hits.append("R06")
    if profile.get("target_damage"):
        hits.append("R07")
    if profile.get("acute_event"):
        hits.append("R08")
    if profile.get("smoker"):
        hits.append("R09")
    if profile.get("bmi", 0) >= 28:
        hits.append("R10")
    if profile.get("comorbid_n", 0) >= 2:
        hits.append("R11")
    if profile.get("age", 0) >= 65:
        hits.append("R12")
    total = sum(RISK_RULES[h][1] for h in hits)
    if "R08" in hits:  # 急性事件直通红档：立即转诊，不被分数稀释
        grade = GRADES[0][1]
    else:
        grade = next(g for th, g in GRADES if total >= th)
    return {"ok": True, "score": total, "grade": grade,
            "rule_refs": hits, "reproducible": True,
            "disclaimer": "规则化分层仅辅助分级，诊断决策权归执业医师",
            "seal": SEAL}


class MdtConvene:
    """多学科综合会诊编排：按信封模态+登记病种路由科室/技能；
    会诊单只出意见槽，结论留白给医师（处置权分离）。"""

    DEPT_BY_MODALITY = {"eye_photo": "眼科", "ear_photo": "耳鼻喉科",
                        "tongue_photo": "中医科", "pulse": "中医科"}

    @classmethod
    def convene(cls, entries, diseases):
        depts, skills = set(), set()
        for e in entries:
            d = cls.DEPT_BY_MODALITY.get(e.get("modality"))
            if d:
                depts.add(d)
        for code in diseases:
            for sys_ in SIX_SYSTEM_ATLAS.values():
                if code in sys_["diseases"]:
                    depts.add(sys_["dept"])
                    skills.update(sys_["skills"])
        if "hypertension" in diseases:
            depts.add("心血管内科")
        if "t2dm" in diseases:
            depts.add("内分泌科")
        if "copd" in diseases:
            depts.add("呼吸内科")
        return {"ok": True, "depts": sorted(depts),
                "skills": sorted(skills),
                "opinion_slots": {d: "" for d in sorted(depts)},
                "decision": "执业医师终审（本引擎不出诊断结论）", "seal": SEAL}


class FollowupScheduler:
    """随访调度（公卫规范确定性规则）：A类≥4次/年；控制不满意→2周内复访；
    危急→转诊+2周内追踪回流（mobius 医学域复现）。"""

    @classmethod
    def plan(cls, disease, control="satisfied", acute=False, done_this_year=0):
        reg = DISEASE_REGISTRY["A"].get(disease)
        if not reg:
            return {"ok": False, "error": "非A类病种走 C/D 类协议", "seal": SEAL}
        need = reg["followup_per_year"]
        remaining = max(0, need - done_this_year)
        if acute:
            action = "立即转诊上级医院，2周内追踪转诊结果（回流登记）"
        elif control == "unsatisfied":
            action = "2周内再次随访（复访），连续2次不满意建议转诊"
        else:
            action = "常规随访"
        return {"ok": True, "disease": reg["cn"], "required_per_year": need,
                "remaining": remaining, "action": action,
                "reflux_note": "转诊→回基层接续随访=mobius回流(LIN-E01)",
                "seal": SEAL}


class PortPool:
    """机构端并行端口池：≤10 槽位，确定性分配/释放（等保边界）。"""

    def __init__(self, limit=PORT_POOL_LIMIT):
        self.limit = limit
        self.used = {}

    def acquire(self, task_id):
        if task_id in self.used:
            return {"ok": False, "error": "task already holds a port",
                    "seal": SEAL}
        if len(self.used) >= self.limit:
            return {"ok": False, "error": "port pool exhausted (limit=%d)"
                    % self.limit, "seal": SEAL}
        port = 9000 + len(self.used)
        self.used[task_id] = port
        return {"ok": True, "port": port, "used": len(self.used),
                "limit": self.limit, "seal": SEAL}

    def release(self, task_id):
        return {"ok": self.used.pop(task_id, None) is not None, "seal": SEAL}


class MLPS3:
    """三级等保要求检查表（本地安全能力映射，report-only）。"""

    CHECKLIST = {
        "身份鉴别": "口令复杂度+失败锁定（对接机构统一认证）",
        "访问控制": "RBAC：Editor/Viewer 最小权限（与既有测试账号约定同构）",
        "安全审计": "append-only 审计日志+SHA256 链（篡改可发现）",
        "数据完整性": "存档 SHA256 指针校验（FeedEnvelope）",
        "数据保密性": "静态加密由部署层负责（引擎留接口，密钥不出引擎）",
        "备份恢复": "archive_sync 网络同步清单+SHA 校验后入档",
        "边界防护": "端口池≤10+白名单，零未授权出站（模块零网络）",
    }

    @classmethod
    def audit(cls, audit_log):
        """审计链完整性校验：log=[(event, sha_of_prev_entry+event)]。"""
        prev = ""
        for i, (event, digest) in enumerate(audit_log):
            expect = hashlib.sha256((prev + event).encode("utf-8")).hexdigest()
            if digest != expect:
                return {"ok": False, "broken_at": i, "seal": SEAL}
            prev = digest
        return {"ok": True, "entries": len(audit_log), "seal": SEAL}

    @classmethod
    def chain_entry(cls, event, prev_digest=""):
        return hashlib.sha256((prev_digest + event).encode("utf-8")).hexdigest()


class CapacityPlanner:
    """3万人口辖区容量估算（参数可调，确定性公式；流行率为缺省文献口径，
    部署时应以本地建档实际数替换）。"""

    DEFAULTS = {"population": 30000, "adult35_ratio": 0.55,
                "htn_prev": 0.25, "t2dm_prev": 0.10, "copd_prev": 0.03}

    @classmethod
    def estimate(cls, **overrides):
        p = dict(cls.DEFAULTS, **overrides)
        adults = int(p["population"] * p["adult35_ratio"])
        patients = {k: int(adults * p[k + "_prev"] if k != "t2dm"
                           else adults * p["t2dm_prev"])
                    for k in ("htn", "t2dm", "copd")}
        # 每病种年随访量 = 患者数×4；年体检量 = 患者数×1
        visits = sum(v * 4 for v in patients.values())
        return {"ok": True, "adults_35plus": adults,
                "patients": patients,
                "followup_visits_per_year": visits,
                "exams_per_year": sum(patients.values()),
                "port_pool": PORT_POOL_LIMIT,
                "note": "估算口径：部署时以本地建档实际数替换流行率参数",
                "seal": SEAL}


def audit():
    """总闸（与链条惯例同构）：引擎整体状态快照，report-only。"""
    return {"seal": SEAL, "ring": CHAIN_POSITION["ring"],
            "a_diseases": sorted(DISEASE_REGISTRY["A"]),
            "systems": sorted(SIX_SYSTEM_ATLAS),
            "modalities": sorted(MODALITIES),
            "port_limit": PORT_POOL_LIMIT,
            "mlps_items": sorted(MLPS3.CHECKLIST),
            "zero_network": True, "zero_diagnosis": True}

