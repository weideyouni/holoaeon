"""验证红线扫描在「没有 sys.stdlib_module_names」的 3.8/3.9 环境下不再假红。

做法：先按当前解释器跑一遍，再删掉 sys.stdlib_module_names 模拟 3.8 重跑。
两次都必须 clean=True、violations=0，否则 CI 的 py3.8 job 仍会 exit 1。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holoaeon.redline import scan_directory  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "holoaeon")


def run(tag):
    rep = scan_directory(ROOT)
    print("%s: files=%s clean=%s violations=%s"
          % (tag, rep["files_scanned"], rep["clean"], len(rep["violations"])))
    for v in rep["violations"][:5]:
        print("   %s:%s %s %s" % (v["file"], v["line"], v["kind"], v["name"]))
    return rep["clean"]


def main():
    ok_now = run("with sys.stdlib_module_names")
    if hasattr(sys, "stdlib_module_names"):
        del sys.stdlib_module_names
    ok_38 = run("simulated py3.8 fallback")
    from holoaeon.redline import _stdlib_names

    names = _stdlib_names()
    # 扩展模块（Linux 上是 lib-dynload/*.so）最容易漏：CI 的 py3.8 就是被
    # math / cmath 误判成第三方而 red 的，这两条必须显式断言。
    missing = [n for n in ("math", "cmath", "shutil", "tempfile") if n not in names]
    print("fallback_size=%s missing=%s" % (len(names), missing or "none"))
    ok = ok_now and ok_38 and not missing
    print("both_clean=%s" % ok)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
