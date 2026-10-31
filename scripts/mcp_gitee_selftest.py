#!/usr/bin/env python
"""MCP 服务器自检：真起进程，走真实 stdio 协议，跑真实 Gitee 调用。

    python scripts/mcp_gitee_selftest.py --repo F:\\doubaowork\\holoaeon

校验四件事：
1. `initialize` 返回协议版本与 serverInfo；
2. `tools/list` 返回 5 个工具且名字与文档一致；
3. `tools/call gitee_status` 能取到本地与远端哈希（in_sync 为布尔）；
4. 未知工具返回 `isError`，而不是崩溃。
"""

import argparse
import json
import os
import subprocess
import sys

SERVER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_gitee_server.py")


def send(proc, payload):
    proc.stdin.write(json.dumps(payload, ensure_ascii=False) + "\n")
    proc.stdin.flush()


def recv(proc):
    line = proc.stdout.readline()
    if not line:
        raise RuntimeError("服务器提前退出")
    return json.loads(line)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=os.getcwd())
    args = parser.parse_args(argv)

    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.Popen(
        [sys.executable, SERVER],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        env=env,
    )

    checks = []

    send(proc, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    init = recv(proc)
    ok = init.get("result", {}).get("serverInfo", {}).get("name") == "gitee-publish"
    checks.append(("initialize", ok, init.get("result", {}).get("protocolVersion")))

    send(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    listing = recv(proc)
    names = [tool["name"] for tool in listing.get("result", {}).get("tools", [])]
    checks.append(("tools/list", len(names) == 5, ",".join(names)))

    send(proc, {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {
        "name": "gitee_status",
        "arguments": {"repo_path": os.path.abspath(args.repo)},
    }})
    status = recv(proc)
    text = status.get("result", {}).get("content", [{}])[0].get("text", "{}")
    payload = json.loads(text)
    checks.append(("gitee_status", "local_sha" in payload and "remote_sha" in payload,
                   "in_sync=%s" % payload.get("in_sync")))

    send(proc, {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {
        "name": "no_such_tool", "arguments": {},
    }})
    unknown = recv(proc)
    checks.append(("unknown_tool", unknown.get("error", {}).get("code") == -32601,
                   str(unknown.get("error", {}).get("code"))))

    proc.stdin.close()
    proc.wait(timeout=15)
    stderr = proc.stderr.read().strip()
    if stderr:
        print("[stderr] %s" % stderr.splitlines()[-1])

    failed = 0
    for name, ok, detail in checks:
        print("[%s] %s — %s" % ("PASS" if ok else "FAIL", name, detail))
        failed += 0 if ok else 1
    print("==> %d/%d" % (len(checks) - failed, len(checks)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
