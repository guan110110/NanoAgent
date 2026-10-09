"""
Tutorial 04: Python 代码执行沙箱与自愈实战 (Code Sandbox & Self-Healing)
目的：展示当 Agent 编写的代码在沙箱中抛出异常时，如何优雅地将 Traceback 喂回给大模型进行自主修复。
运行方式: python tutorials/04_code_sandbox_self_heal.py
"""

import os
import io
import json
import contextlib
from openai import OpenAI

def execute_python_code(code: str) -> str:
    """在沙箱环境中执行 Python 代码，若出错则返回详细错误堆栈"""
    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(stdout_buf), contextlib.redirect_stderr(stderr_buf):
            local_scope = {}
            exec(code, local_scope)
        res = stdout_buf.getvalue()
        return res if res else "[Success: No stdout output]"
    except Exception as e:
        return f"Runtime Error ({type(e).__name__}): {str(e)}"

tools = [
    {
        "type": "function",
        "function": {
            "name": "run_python",
            "description": "执行 Python 脚本并捕获输出结果",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Python 代码内容"}
                },
                "required": ["code"]
            }
        }
    }
]

def main():
    client = OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY") or "your-api-key",
        base_url=os.getenv("BASE_URL") or "https://api.deepseek.com"
    )
    model = os.getenv("MODEL_NAME") or "deepseek-chat"

    task = "写一段 Python 代码，故意先尝试除以零 1/0，看到报错后捕获或者修正它，并正确计算 100/4 的值打印出来。"
    print(f"🎯 任务: {task}\n")

    messages = [
        {"role": "system", "content": "你是一个能够自我编写并调试 Python 代码的 AI 智能体。遇到报错请反思并修正。"},
        {"role": "user", "content": task}
    ]

    for step in range(1, 6):
        res = client.chat.completions.create(model=model, messages=messages, tools=tools)
        msg = res.choices[0].message
        messages.append(msg)

        if msg.content:
            print(f"[Step {step}] 思考/解释: {msg.content}")

        if not msg.tool_calls:
            print("\n✨ 任务圆满解决并退出!")
            break

        for call in msg.tool_calls:
            args = json.loads(call.function.arguments)
            code = args.get("code", "")
            print(f"\n[执行代码]:\n{code}\n")
            
            obs = execute_python_code(code)
            print(f"[环境反馈 Observation]:\n{obs}\n" + "-"*40)

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": obs
            })

if __name__ == "__main__":
    main()
