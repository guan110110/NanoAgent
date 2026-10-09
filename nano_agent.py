"""
NanoAgent: A Minimalist, Transparent AI Agent Framework from Scratch in Pure Python.
零黑盒、轻量透明的纯 Python 自主智能体实现。
"""

import os
import sys
import json
import io
import contextlib
from typing import Callable, Dict, Any, List, Optional
from openai import OpenAI


# ==============================================================================
# 1. 终端美化高亮 (Terminal ANSI Color Styling)
# ==============================================================================
class Color:
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


# ==============================================================================
# 2. 工具注册中心 (Tool Registry)
# ==============================================================================
class ToolRegistry:
    """
    负责工具函数的管理、OpenAPI JSON Schema 自动化转换与安全执行。
    零框架依赖，纯 Python 原生实现。
    """
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._schemas: List[Dict[str, Any]] = []

    def register(self, name: str, description: str, parameters: dict):
        """
        装饰器：注册一个 Python 函数为 Agent 可调用的工具。
        """
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
        """获取所有已注册工具的 OpenAPI 标准定义"""
        return self._schemas

    def execute(self, name: str, args: dict) -> str:
        """
        分发并执行工具函数。
        如果工具内部执行报错，捕获 Traceback 并将其作为环境反馈 (Observation) 返回给大模型，
        促使智能体自主反思和修复。
        """
        if name not in self._tools:
            return f"Error: 未找到名为 '{name}' 的工具。"

        try:
            result = self._tools[name](**args)
            return str(result)
        except Exception as e:
            return f"Tool Execution Error ({type(e).__name__}): {str(e)}"


# ==============================================================================
# 3. 核心智能体调度引擎 (NanoAgent Engine)
# ==============================================================================
class NanoAgent:
    """
    极简自主智能体内核，实现完整的 ReAct (Thought -> Action -> Observation) 驱动循环。
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
        
        self.system_prompt = system_prompt or (
            "你是一个具备自主行动能力的 AI Agent。\n"
            "你可以自主调用提供的外部工具来探索环境、编写代码、操作文件并解决复杂问题。\n"
            "【执行原则】\n"
            "1. 每次行动前，请先输出简要的思考（Thought），然后选择合适的工具与参数（Action）；\n"
            "2. 如果工具执行报错，请仔细根据反馈中的错误原因（Observation）自我修正并重试；\n"
            "3. 当任务彻底完成时，直接向用户输出最终答案，无需再调用任何工具。"
        )

    def run(self, goal: str) -> Optional[str]:
        """
        启动智能体执行用户目标。
        """
        print(f"\n{Color.BOLD}{Color.CYAN}🎯 [任务目标]{Color.RESET} {goal}")
        print(f"{Color.GRAY}{'=' * 65}{Color.RESET}")

        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": goal}
        ]

        for step in range(1, self.max_steps + 1):
            print(f"\n{Color.BOLD}[Step {step}/{self.max_steps}]{Color.RESET} {Color.BLUE}Agent 正在推理...{Color.RESET}")

            # 1. 向大模型发起推理请求
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.registry.schemas if self.registry.schemas else None,
                    tool_choice="auto"
                )
            except Exception as err:
                print(f"{Color.YELLOW}API 请求异常: {err}{Color.RESET}")
                return None

            choice = response.choices[0]
            msg = choice.message
            messages.append(msg)

            # 2. 输出模型的中间思考或解释
            if msg.content:
                print(f"{Color.CYAN}💭 Thought:{Color.RESET} {msg.content}")

            # 3. 如果模型没有产生任何工具调用，说明已得出最终解答
            if not msg.tool_calls:
                print(f"\n{Color.BOLD}{Color.GREEN}✨ [任务完成]{Color.RESET}\n{msg.content}")
                return msg.content

            # 4. 依次执行模型给出的工具调用
            for tool_call in msg.tool_calls:
                func_name = tool_call.function.name
                try:
                    func_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    func_args = {}

                print(f"{Color.YELLOW}⚡ Action:{Color.RESET} 调用工具 `{func_name}`")
                print(f"   {Color.GRAY}参数:{Color.RESET} {json.dumps(func_args, ensure_ascii=False)}")

                # 执行工具获取 Observation
                obs = self.registry.execute(func_name, func_args)
                obs_display = obs if len(obs) <= 200 else obs[:200] + "...(截断)"
                print(f"{Color.MAGENTA}👁️ Observation:{Color.RESET} {obs_display}")

                # 将工具返回写回历史上下文
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": obs
                })

        print(f"\n{Color.YELLOW}⚠️ 已达最大循环步数 ({self.max_steps})，终止执行。{Color.RESET}")
        return None


# ==============================================================================
# 4. 默认内置工具集安装 (Built-in Tools)
# ==============================================================================
def register_default_tools(agent: NanoAgent):
    """为 Agent 挂载标准开发工具"""

    @agent.registry.register(
        name="execute_python",
        description="执行一段 Python 代码并返回控制台输出。可用于复杂数值计算、数据整理或逻辑验证。",
        parameters={
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "要运行的 Python 源码"}
            },
            "required": ["code"]
        }
    )
    def execute_python(code: str) -> str:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            scope = {}
            exec(code, scope)
        output = buf.getvalue()
        return output if output else "[代码执行完毕，无控制台输出]"

    @agent.registry.register(
        name="write_file",
        description="将指定内容写入本地文件。",
        parameters={
            "type": "object",
            "properties": {
                "filepath": {"type": "string", "description": "文件保存路径"},
                "content": {"type": "string", "description": "写入的文本内容"}
            },
            "required": ["filepath", "content"]
        }
    )
    def write_file(filepath: str, content: str) -> str:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"成功写入文件 '{filepath}' (共 {len(content)} 字符)。"

    @agent.registry.register(
        name="read_file",
        description="读取本地文件的完整文本内容。",
        parameters={
            "type": "object",
            "properties": {
                "filepath": {"type": "string", "description": "目标文件路径"}
            },
            "required": ["filepath"]
        }
    )
    def read_file(filepath: str) -> str:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"文件 '{filepath}' 不存在。")
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()


# ==============================================================================
# 5. 快速测试入口
# ==============================================================================
if __name__ == "__main__":
    # 支持 DeepSeek / OpenAI / Qwen / Ollama 等兼容接口
    api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY") or "your-api-key"
    base_url = os.getenv("BASE_URL") or "https://api.deepseek.com"
    model = os.getenv("MODEL_NAME") or "deepseek-chat"

    client = OpenAI(api_key=api_key, base_url=base_url)
    agent = NanoAgent(client=client, model=model, max_steps=8)
    register_default_tools(agent)

    task = (
        "用 Python 编写一段代码计算 1 到 1000 内所有素数之和；"
        "把结果和运行耗时写入到 'prime_sum.txt' 中；"
        "最后重新读取该文件核对内容无误后向我汇报。"
    )
    agent.run(task)
