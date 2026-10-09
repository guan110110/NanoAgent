"""
NanoAgent Core Engine Implementation.
"""

import os
import json
from typing import Callable, Dict, Any, List, Optional
from openai import OpenAI

from nano_agent.ui import AgentUI
from nano_agent.tools.bash import execute_bash_command
from nano_agent.tools.python_repl import PythonREPL
from nano_agent.tools.web_search import web_search


class ToolRegistry:
    """工具注册与参数 Schema 转化中心"""
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._schemas: List[Dict[str, Any]] = []

    def register(self, name: str, description: str, parameters: dict):
        def decorator(func: Callable):
            self._tools[name] = func
            self._schemas.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": parameters
                }
            })
            return func
        return decorator

    @property
    def schemas(self) -> List[Dict[str, Any]]:
        return self._schemas

    def execute(self, name: str, args: dict) -> str:
        if name not in self._tools:
            return f"Error: Tool '{name}' not found."
        try:
            return str(self._tools[name](**args))
        except Exception as e:
            return f"Tool Execution Error ({type(e).__name__}): {str(e)}"


class NanoAgent:
    """
    轻量模块化自主智能体
    """
    def __init__(
        self,
        client: Optional[OpenAI] = None,
        model: str = "deepseek-chat",
        max_steps: int = 10,
        system_prompt: Optional[str] = None
    ):
        self.client = client or OpenAI()
        self.model = model
        self.max_steps = max_steps
        self.registry = ToolRegistry()
        self.repl = PythonREPL()

        self.system_prompt = system_prompt or (
            "你是一个具备自主行动能力的 AI Agent。\n"
            "你可以自主调用提供的外部工具来探索环境、运行代码、检索信息并解决复杂问题。\n"
            "【原则】\n"
            "1. 每次行动前，先输出简要思考（Thought），然后调用工具（Action）；\n"
            "2. 如果工具报错，仔细阅读反馈（Observation）并自我纠错重试；\n"
            "3. 任务彻底完成后，直接向用户输出最终回答，不再调用任何工具。"
        )
        self._mount_default_tools()

    def _mount_default_tools(self):
        """挂载开箱即用的三大核心工具"""
        @self.registry.register(
            name="python_repl",
            description="在持久化沙箱中运行 Python 代码，可进行数学运算、数据清洗或算法验证。",
            parameters={
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Python 代码"}
                },
                "required": ["code"]
            }
        )
        def run_python(code: str) -> str:
            return self.repl.run(code)

        @self.registry.register(
            name="bash_command",
            description="执行安全的系统终端命令（如 ls, dir, git 等）。",
            parameters={
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "终端命令"}
                },
                "required": ["command"]
            }
        )
        def run_bash(command: str) -> str:
            return execute_bash_command(command)

        @self.registry.register(
            name="web_search",
            description="在互联网上检索信息和知识摘要。",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索关键词"}
                },
                "required": ["query"]
            }
        )
        def run_search(query: str) -> str:
            return web_search(query)

    def run(self, goal: str) -> Optional[str]:
        AgentUI.print_goal(goal)

        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": goal}
        ]

        for step in range(1, self.max_steps + 1):
            AgentUI.print_step_header(step, self.max_steps)

            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.registry.schemas if self.registry.schemas else None,
                    tool_choice="auto"
                )
            except Exception as err:
                print(f"API Error: {err}")
                return None

            msg = response.choices[0].message
            messages.append(msg)

            if msg.content:
                AgentUI.print_thought(msg.content)

            if not msg.tool_calls:
                AgentUI.print_final_answer(msg.content)
                return msg.content

            for tool_call in msg.tool_calls:
                name = tool_call.function.name
                try:
                    args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    args = {}

                AgentUI.print_action(name, args)
                obs = self.registry.execute(name, args)
                AgentUI.print_observation(obs)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": obs
                })

        return None
