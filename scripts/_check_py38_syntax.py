"""用 3.8 的语法版本解析全仓 .py，判断「Python 3.8 兼容」是真声明还是口号。

只查语法（ast.parse 的 feature_version），不查运行时 API：3.8 上被移除/新增的标准库
行为差异（如 dict 顺序、zoneinfo）无法靠语法发现，那一层仍要靠真机 CI。
"""
import ast
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "build", "dist", "_shots"}
TARGET = (3, 8)


def main():
    bad = []
    total = 0
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            if not name.endswith(".py"):
                continue
            path = os.path.join(base, name)
            total += 1
            try:
                src = open(path, encoding="utf-8").read()
                ast.parse(src, filename=path, feature_version=TARGET)
            except SyntaxError as exc:
                bad.append((os.path.relpath(path, ROOT), exc.lineno, exc.msg))
    print("parsed=%d  py38_syntax_failures=%d" % (total, len(bad)))
    for row in bad[:20]:
        print("  FAIL %s:%s %s" % row)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
