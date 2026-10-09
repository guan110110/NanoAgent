"""
Tutorial 05: 拥抱现代化协议 —— MCP (Model Context Protocol) 最小客户端实现
目的：演示现代标准化的工具协议 MCP 如何通过 JSON-RPC 规范解耦 Agent 与外部工具服务。
运行方式: python tutorials/05_mcp_client.py
"""

import json
from typing import Dict, Any

class MockMCPServer:
    """
    模拟一个标准的外部 MCP (Model Context Protocol) 服务端。
    通过 JSON-RPC 2.0 协议提供工具发现与工具调用。
    """
    def handle_request(self, request_json: str) -> str:
        req = json.loads(request_json)
        method = req.get("method")
        msg_id = req.get("id")

        # 1. 工具列表发现 (tools/list)
        if method == "tools/list":
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": [
                        {
                            "name": "mcp_get_system_time",
                            "description": "获取当前服务器系统时间",
                            "inputSchema": {
                                "type": "object",
                                "properties": {"timezone": {"type": "string"}},
                                "required": []
                            }
                        }
                    ]
                }
            })

        # 2. 执行具体工具 (tools/call)
        elif method == "tools/call":
            params = req.get("params", {})
            tool_name = params.get("name")
            if tool_name == "mcp_get_system_time":
                return json.dumps({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [{"type": "text", "text": "2026-10-09 11:45:00 UTC+8"}]
                    }
                })

        return json.dumps({"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": "Method not found"}})


class MCPClientAdapter:
    """MCP 适配器：将 MCP 服务端的协议转换为大模型 OpenAI 标准的 Function Calling 工具格式"""
    def __init__(self, server: MockMCPServer):
        self.server = server

    def discover_tools(self):
        req = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
        resp = json.loads(self.server.handle_request(req))
        mcp_tools = resp["result"]["tools"]

        # 转化为大模型认识的 OpenAPI tools 格式
        formatted_tools = []
        for t in mcp_tools:
            formatted_tools.append({
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": t["inputSchema"]
                }
            })
        return formatted_tools

    def call_tool(self, name: str, arguments: dict) -> str:
        req = json.dumps({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments}
        })
        resp = json.loads(self.server.handle_request(req))
        return resp["result"]["content"][0]["text"]

if __name__ == "__main__":
    print("🚀 初始化 MCP 服务端与客户端通信...")
    server = MockMCPServer()
    client = MCPClientAdapter(server)

    tools = client.discover_tools()
    print("\n✅ 成功通过 MCP JSON-RPC 发现并转换工具:")
    print(json.dumps(tools, indent=2, ensure_ascii=False))

    print("\n⚡ 发起 MCP 工具调用:")
    res = client.call_tool("mcp_get_system_time", {})
    print(f"<- MCP 执行返回结果: {res}")
