"""V26 莫比乌斯漩涡模块测试（11 例，确定性断言）。

覆盖：灯塔 schema/seal、两级校验、三点对齐（含断线恢复）、四人组简报判定、技能图谱与 CLI。
不改真实仓库：对齐测试用临时目录构造 `.git`，只有一处读真仓 HEAD 且只断言格式。
"""
import json
import os
import shutil
import tempfile
import unittest

from holoaeon.machine_tool import SEAL
from holoaeon.mobius_vortex import (
    ATLAS_ENTRIES,
    BEACON_REQUIRED,
    MobiusRing,
    MobiusVortex,
    QuartetBrief,
    SCHEMA_VERSION,
    SkillAtlas,
    StateBeacon,
    VortexIngest,
    main,
)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEAD_A = "a" * 40
HEAD_B = "b" * 40


def make_repo(root, head=HEAD_A):
    """在 root 下造一个最小 git 结构，让 BaselineProbe 能直读 HEAD。"""
    git_dir = os.path.join(root, ".git")
    os.makedirs(os.path.join(git_dir, "refs", "heads"), exist_ok=True)
    with open(os.path.join(git_dir, "HEAD"), "w", encoding="utf-8") as handle:
        handle.write("ref: refs/heads/main\n")
    with open(os.path.join(git_dir, "refs", "heads", "main"), "w", encoding="utf-8") as handle:
        handle.write(head + "\n")
    return root


def make_memory(root, head):
    os.makedirs(root, exist_ok=True)
    payload = {"domain": "version_history",
               "history": [{"batch": "VFIX", "head": head}]}
    path = os.path.join(root, "version_history.json")
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    return root


class BeaconTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="mobius_")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_01_beacon_payload_keys(self):
        """灯塔必填键齐全，schema 与封口密语正确（L2 校验的前提）。"""
        beacon = StateBeacon(batch="V26-EXEC", head=HEAD_A, doc_version="0.9.21",
                             extra_packs=19)
        payload = beacon.payload()
        for key in BEACON_REQUIRED:
            self.assertIn(key, payload)
        self.assertEqual(payload["schema_version"], SCHEMA_VERSION)
        self.assertEqual(payload["seal"], SEAL)
        self.assertEqual(payload["head_short"], "aaaaaaa")

    def test_02_beacon_roundtrip(self):
        """写→读往返字节等价（文件即接口）。"""
        beacon = StateBeacon(batch="V26-EXEC", head=HEAD_A, gates={"selftest": True},
                             five_site={"S1": {"head": HEAD_A, "ok": True}})
        path = os.path.join(self.tmp, "beacon.json")
        beacon.write(path)
        loaded = StateBeacon.read(path)
        self.assertEqual(loaded["batch"], "V26-EXEC")
        self.assertEqual(loaded["gates"], {"selftest": True})
        self.assertEqual(loaded["seal"], SEAL)


class IngestTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="mobius_")
        self.ingest = VortexIngest()
        self.good = StateBeacon(batch="V26-EXEC", head=HEAD_A).payload()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_03_schema_rejected(self):
        """L1 快筛：schema_version 不符 → 拒绝，且标记 L1_schema。"""
        bad = dict(self.good)
        bad["schema_version"] = "MOBIUS-BEACON-v0.9"
        result = self.ingest.validate(bad)
        self.assertFalse(result["ok"])
        self.assertEqual(result["level"], "L1_schema")

    def test_04_seal_rejected(self):
        """L2 深校：封口密语不符 → 拒绝（回执真实性是生命线）。"""
        bad = dict(self.good)
        bad["seal"] = "潮起开门"
        result = self.ingest.validate(bad)
        self.assertFalse(result["ok"])
        self.assertFalse(result["seal_ok"])
        self.assertEqual(result["level"], "L2_seal")

    def test_05_missing_key_rejected(self):
        """缺必填键 → 拒绝。"""
        bad = {k: v for k, v in self.good.items() if k != "gates"}
        result = self.ingest.validate(bad)
        self.assertFalse(result["ok"])
        self.assertTrue(any("gates" in p for p in result["problems"]))

    def test_06_good_beacon_accepted(self):
        """合法灯塔通过两级校验。"""
        result = self.ingest.validate(self.good)
        self.assertTrue(result["ok"])
        self.assertEqual(result["level"], "ok")
        self.assertTrue(result["seal_ok"] and result["schema_ok"])

    def test_07_file_level_ingest(self):
        """磁盘路径入口同样能过（总监侧真实读法）。"""
        path = os.path.join(self.tmp, "beacon.json")
        StateBeacon(batch="V26-EXEC", head=HEAD_A).write(path)
        result = self.ingest.load(path)
        self.assertTrue(result["ok"])
        self.assertEqual(result["path"], path)


class RingTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="mobius_")
        self.memory = make_memory(os.path.join(self.tmp, "mem"), HEAD_A)
        self.repo = make_repo(os.path.join(self.tmp, "repo"), HEAD_A)
        self.ring = MobiusRing(self.repo, self.memory)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_08_aligned(self):
        """灯塔=实时=账面 → ALIGNED，无需回填。"""
        result = self.ring.align(HEAD_A)
        self.assertTrue(result["consistent"])
        self.assertEqual(result["verdict"], "ALIGNED")
        self.assertFalse(result["backfill_needed"])

    def test_09_drift_prefers_live(self):
        """灯塔/账面是旧值 → DRIFT，以实时为准并要求回填（断线恢复协议）。"""
        result = self.ring.align(HEAD_B)
        self.assertFalse(result["consistent"])
        self.assertEqual(result["verdict"], "DRIFT")
        self.assertEqual(result["source_of_truth"], "live")
        self.assertEqual(result["live_head"], HEAD_A)
        self.assertTrue(result["backfill_needed"])
        self.assertTrue(any("灯塔" in note for note in result["notes"]))

    def test_10_real_repo_head_shape(self):
        """真仓 HEAD 必须是 40 位十六进制（防"退出码 0 但静默"）。"""
        live = MobiusRing(REPO).live_head()
        self.assertIsNotNone(live)
        self.assertRegex(live, r"^[0-9a-f]{40}$")


class BriefTest(unittest.TestCase):
    def test_11_pass_and_block(self):
        """全绿→PASS；红灯/漂移→BLOCK；四段结构恒定。"""
        brief = QuartetBrief()
        ok_beacon = {
            "batch": "V26-EXEC", "head": HEAD_A, "head_short": HEAD_A[:7],
            "doc_version": "0.9.21", "extra_packs": 19,
            "gates": {"selftest": True, "v3_gate": True},
            "five_site": {"S1": {"ok": True}, "S2": {"ok": True}},
            "lessons": [],
        }
        aligned = {"verdict": "ALIGNED", "consistent": True, "notes": []}
        good = brief.compose(ok_beacon, aligned)
        self.assertEqual(good["verdict"], "PASS")
        for key in ("p4_question", "p2_facts", "p3_risks", "p1_advice"):
            self.assertIn(key, good)
        self.assertEqual(len(good["roles"]), 4)

        bad_beacon = dict(ok_beacon)
        bad_beacon["gates"] = {"selftest": False, "v3_gate": True}
        drift = {"verdict": "DRIFT", "consistent": False,
                 "notes": ["灯塔 HEAD aaaaaaa ≠ 实时 HEAD bbbbbbb"]}
        bad = brief.compose(bad_beacon, drift)
        self.assertEqual(bad["verdict"], "BLOCK")
        self.assertTrue(any("selftest" in risk for risk in bad["p3_risks"]))


class AtlasAndCliTest(unittest.TestCase):
    def test_12_atlas_ten_and_cli(self):
        """技能图谱 10 条、可检索；CLI status 输出含封口密语。"""
        atlas = SkillAtlas()
        self.assertEqual(len(atlas.all()), 10)
        self.assertEqual(len(ATLAS_ENTRIES), 10)
        self.assertTrue(atlas.match("环面"))
        self.assertTrue(atlas.match("dehallucination"))
        self.assertEqual(atlas.match(""), [])

        tool = MobiusVortex(repo=REPO)
        status = tool.status()
        self.assertEqual(status["seal"], SEAL)
        self.assertEqual(status["atlas_entries"], 10)

        import io
        from contextlib import redirect_stdout
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            main(["status"])
        self.assertIn(SEAL, buffer.getvalue())


if __name__ == "__main__":
    unittest.main()
