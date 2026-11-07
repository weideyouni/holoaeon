# -*- coding: utf-8 -*-
"""V38 复算闸测试。零依赖，确定性断言。
scripts/ 非包目录，按投喂包注释改用 importlib 加载。"""
import hashlib
import importlib.util
import io
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_spec = importlib.util.spec_from_file_location(
    "check_sums",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 "scripts", "check_sums.py"))
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
SEAL = _mod.SEAL
verify = _mod.verify


def make_repo(d, files, corrupt=None):
    lines = []
    for name, content in files.items():
        p = os.path.join(d, name)
        parent = os.path.dirname(p)
        if parent:
            os.makedirs(parent, exist_ok=True)
        h = hashlib.sha256(content.encode()).hexdigest()
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
        lines.append(f"{h}  {name}")
    with open(os.path.join(d, "SHA256SUMS"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    if corrupt:
        with open(os.path.join(d, corrupt), "a", encoding="utf-8") as f:
            f.write("tampered")


class TestCheckSums(unittest.TestCase):
    def test_clean_repo_ok(self):
        with tempfile.TemporaryDirectory() as d:
            make_repo(d, {"a.txt": "hello", "b/c.txt": "world"})
            r = verify("SHA256SUMS", d)
            self.assertTrue(r["ok"])
            self.assertEqual(r["total"], 2)

    def test_tamper_detected(self):
        with tempfile.TemporaryDirectory() as d:
            make_repo(d, {"a.txt": "hello"}, corrupt="a.txt")
            r = verify("SHA256SUMS", d)
            self.assertFalse(r["ok"])
            self.assertEqual(r["mismatches"][0]["file"], "a.txt")

    def test_missing_sums(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertFalse(verify("SHA256SUMS", d)["ok"])

    def test_report_only_no_rewrite(self):
        with tempfile.TemporaryDirectory() as d:
            make_repo(d, {"a.txt": "hello"}, corrupt="a.txt")
            before = io.open(os.path.join(d, "SHA256SUMS"),
                             encoding="utf-8").read()
            verify("SHA256SUMS", d)
            after = io.open(os.path.join(d, "SHA256SUMS"),
                            encoding="utf-8").read()
            self.assertEqual(before, after)   # 闸只阻断不重建

    def test_seal(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(verify("SHA256SUMS", d)["seal"], SEAL)


if __name__ == "__main__":
    unittest.main()
