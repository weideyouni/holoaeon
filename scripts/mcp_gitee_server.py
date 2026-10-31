#!/usr/bin/env python
"""Gitee MCP 服务器（stdio，JSON-RPC 2.0 换行分隔），零依赖，Python 3.8+。

启动：

    python scripts/mcp_gitee_server.py

在 MCP 客户端里注册（Claude Desktop / 豆包等 mcp 配置）：

    "gitee": {
      "command": "python",
      "args": ["F:\\\\doubaowork\\\\holoaeon\\\\scripts\\\\mcp_gitee_server.py"],
      "env": {"GITEE_TOKEN": "<令牌>"}
    }

令牌也可以放 ~/.gitee_token，此时 env 可省。提供五个工具：

| 工具 | 作用 |
|---|---|
| `gitee_status` | 本地 HEAD 与 Gitee 远端 ref 比对（不推送） |
| `gitee_publish` | 推送分支/标签，并用远端哈希回读自证 |
| `gitee_create_repo` | 在 Gitee 建仓库（可公开/私有） |
| `gitee_repo_info` | 读仓库元数据（体积、默认分支、更新时间） |
| `gitee_get_file` | 读仓库内单个文件内容 |
"""

import json
import os
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gitee_publish as pub  # noqa: E402  同目录复用令牌与推送逻辑

SERVER_NAME = "gitee-publish"
SERVER_VERSION = "1.0.0"
PROTOCOL_VERSION = "2024-11-05"
API_BASE = "https://gitee.com/api/v5"

TOOLS = [
    {
        "name": "gitee_status",
        "description": "比对本地仓库 HEAD 与 Gitee 远端分支 ref，不执行推送。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo_path": {"type": "string", "description": "本地仓库绝对路径"},
                "branch": {"type": "string", "description": "分支名，默认 main"},
                "owner": {"type": "string", "description": "Gitee 用户名，缺省从 origin 解析"},
                "name": {"type": "string", "description": "仓库名，缺省从 origin 解析"},
            },
            "required": ["repo_path"],
        },
    },
    {
        "name": "gitee_publish",
        "description": "把本地仓库推到 Gitee，并回读远端哈希校验；校验失败返回 isError。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo_path": {"type": "string", "description": "本地仓库绝对路径"},
                "branch": {"type": "string", "description": "分支名，默认 main"},
                "owner": {"type": "string", "description": "Gitee 用户名，缺省从 origin 解析"},
                "name": {"type": "string", "description": "仓库名，缺省从 origin 解析"},
                "push_tags": {"type": "boolean", "description": "是否推送标签，默认 true"},
                "allow_dirty": {"type": "boolean", "description": "允许工作树未提交改动，默认 false"},
            },
            "required": ["repo_path"],
        },
    },
    {
        "name": "gitee_create_repo",
        "description": "在 Gitee 创建仓库。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "仓库名（路径名）"},
                "description": {"type": "string", "description": "仓库描述"},
                "private": {"type": "boolean", "description": "是否私有，默认 false"},
                "auto_init": {"type": "boolean", "description": "是否自动初始化 README，默认 false"},
            },
            "required": ["name"],
        },
    },
    {
        "name": "gitee_repo_info",
        "description": "读取 Gitee 仓库元数据（体积、默认分支、更新时间等）。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "owner": {"type": "string", "description": "Gitee 用户名"},
                "repo": {"type": "string", "description": "仓库名"},
            },
            "required": ["owner", "repo"],
        },
    },
    {
        "name": "gitee_get_file",
        "description": "读取 Gitee 仓库内单个文件的文本内容。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "owner": {"type": "string", "description": "Gitee 用户名"},
                "repo": {"type": "string", "description": "仓库名"},
                "path": {"type": "string", "description": "仓库内文件路径"},
                "ref": {"type": "string", "description": "分支或提交，默认 main"},
            },
            "required": ["owner", "repo", "path"],
        },
    },
]


def api_request(path, token, params=None, method="GET", body=None):
    """调用 Gitee OpenAPI，返回 (ok, payload)；token 不进日志。"""
    query = dict(params or {})
    query["access_token"] = token
    url = API_BASE + path + "?" + urllib.parse.urlencode(query)
    data = None
    headers = {"Content-Type": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.loads(resp.read().decode("utf-8", "replace"))
        return True, payload
    except Exception as exc:  # 网络与 4xx 一律收敛成错误文本
        text = str(exc)
        return False, {"error": text.replace(token, "****")}


def tool_status(args):
    repo_path = os.path.abspath(args["repo_path"])
    branch = args.get("branch") or "main"
    token, source = pub.load_token()
    if not token:
        return {"error": "找不到 Gitee 令牌"}, True
    owner, name = args.get("owner"), args.get("name")
    if not owner or not name:
        parsed_owner, parsed_name = pub.resolve_slug(repo_path, "origin")
        owner, name = owner or parsed_owner, name or parsed_name
    if not owner or not name:
        return {"error": "解析不出 owner/repo"}, True
    local = pub.head_sha(repo_path)
    remote, err = pub.remote_sha(pub.build_url(owner, name, token), "refs/heads/" + branch, repo_path)
    return {
        "repo": owner + "/" + name,
        "branch": branch,
        "local_sha": local,
        "remote_sha": remote,
        "in_sync": bool(local) and local == remote,
        "token_source": source,
        "error": err.split("https://")[0].strip() if (err and not remote) else "",
    }, False


def tool_publish(args):
    repo_path = os.path.abspath(args["repo_path"])
    branch = args.get("branch") or "main"
    token, source = pub.load_token()
    if not token:
        return {"error": "找不到 Gitee 令牌"}, True
    owner, name = args.get("owner"), args.get("name")
    if not owner or not name:
        parsed_owner, parsed_name = pub.resolve_slug(repo_path, "origin")
        owner, name = owner or parsed_owner, name or parsed_name
    receipt, code = pub.publish(
        repo_path=repo_path,
        branch=branch,
        owner=owner,
        name=name,
        token=token,
        push_tags=args.get("push_tags", True),
        allow_dirty=args.get("allow_dirty", False),
    )
    receipt["token_source"] = source
    receipt["exit_code"] = code
    return receipt, not receipt["verified"]


def tool_create_repo(args):
    token, _ = pub.load_token()
    if not token:
        return {"error": "找不到 Gitee 令牌"}, True
    ok, payload = api_request("/user/repos", token, method="POST", body={
        "name": args["name"],
        "description": args.get("description", ""),
        "private": bool(args.get("private", False)),
        "auto_init": bool(args.get("auto_init", False)),
    })
    if not ok:
        return payload, True
    keep = ["full_name", "name", "html_url", "ssh_url", "private", "default_branch", "size"]
    return {key: payload.get(key) for key in keep}, False


def tool_repo_info(args):
    token, _ = pub.load_token()
    if not token:
        return {"error": "找不到 Gitee 令牌"}, True
    ok, payload = api_request("/repos/%s/%s" % (args["owner"], args["repo"]), token)
    if not ok:
        return payload, True
    keep = ["full_name", "human_name", "description", "private", "default_branch",
            "size", "updated_at", "html_url", "ssh_url"]
    return {key: payload.get(key) for key in keep}, False


def tool_get_file(args):
    token, _ = pub.load_token()
    if not token:
        return {"error": "找不到 Gitee 令牌"}, True
    ok, payload = api_request(
        "/repos/%s/%s/contents/%s" % (args["owner"], args["repo"], args["path"].lstrip("/")),
        token,
        params={"ref": args.get("ref") or "main"},
    )
    if not ok:
        return payload, True
    import base64
    content = base64.b64decode(payload.get("content", "")).decode("utf-8", "replace")
    return {
        "path": payload.get("path"),
        "size": payload.get("size"),
        "sha": payload.get("sha"),
        "content": content[:200000],
        "truncated": len(content) > 200000,
    }, False


HANDLERS = {
    "gitee_status": tool_status,
    "gitee_publish": tool_publish,
    "gitee_create_repo": tool_create_repo,
    "gitee_repo_info": tool_repo_info,
    "gitee_get_file": tool_get_file,
}


def respond(msg_id, result=None, error=None):
    body = {"jsonrpc": "2.0", "id": msg_id}
    if error is not None:
        body["error"] = error
    else:
        body["result"] = result
    sys.stdout.write(json.dumps(body, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def handle(message):
    method = message.get("method", "")
    msg_id = message.get("id")
    if method.startswith("notifications/"):
        return
    if method == "initialize":
        respond(msg_id, {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
        })
        return
    if method == "ping":
        respond(msg_id, {})
        return
    if method == "tools/list":
        respond(msg_id, {"tools": TOOLS})
        return
    if method == "tools/call":
        params = message.get("params") or {}
        name = params.get("name")
        args = params.get("arguments") or {}
        handler = HANDLERS.get(name)
        if handler is None:
            respond(msg_id, error={"code": -32601, "message": "未知工具：%s" % name})
            return
        try:
            payload, is_error = handler(args)
        except Exception as exc:
            respond(msg_id, {
                "content": [{"type": "text", "text": json.dumps({"error": str(exc)}, ensure_ascii=False)}],
                "isError": True,
            })
            return
        respond(msg_id, {
            "content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False, indent=2)}],
            "isError": bool(is_error),
        })
        return
    respond(msg_id, error={"code": -32601, "message": "未知方法：%s" % method})


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except ValueError:
            respond(None, error={"code": -32700, "message": "JSON 解析失败"})
            continue
        handle(message)
    return 0


if __name__ == "__main__":
    sys.exit(main())
