"""
Tutorial 02: 经典 ReAct 循环实战
目的：展示如何用一个简单的 while/for 循环驱动 Thought -> Action -> Observation 的多轮自主交互。
运行方式: python tutorials/02_react_loop.py
"""

import os
import json
from openai import OpenAI

# 模拟工具：一个简易内存键值数据库
database = {
    "apple": "苹果公司，市值约 3.4 万亿美元",
    "microsoft": "微软公司，云计算与操作系统巨头",
    "nvidia": "英伟达公司，AI 算力 GPU 领头羊"
}

tools = [
    {
        "type": "function",
        "function": {
            "name": "lookup_company",
            "description": "查询公司的基本市场信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_name": {"type": "string", "description": "公司英文代号，例如 apple, microsoft, nvidia"}
                },
                "required": ["company_name"]
            }
        }
    }
]

def execute_tool(name: str, args: dict) -> str:
    if name == "lookup_company":
        key = args.get("company_name", "").lower()
        return database.get(key, f"未找到公司 '{key}' 的相关记录。")
    return "Error: 未知工具"

def run_react_agent(goal: str, max_steps: int = 5):
    client = OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY") or "your-api-key",
        base_url=os.getenv("BASE_URL") or "https://api.deepseek.com"
    )
    model = os.getenv("MODEL_NAME") or "deepseek-chat"

    messages = [
        {"role": "system", "content": "你是一个自主研究智能体。请先思考需要什么数据，通过工具获取后再给出总结。"},
        {"role": "user", "content": goal}
    ]

    print(f"🎯 任务目标: {goal}\n" + "="*50)

    for step in range(1, max_steps + 1):
        print(f"\n[Step {step}] 思考中...")
        res = client.chat.completions.create(model=model, messages=messages, tools=tools)
        msg = res.choices[0].message
        messages.append(msg)

        if msg.content:
            print(f"💭 Thought: {msg.content}")

        # 没有工具调用，说明已得出结论
        if not msg.tool_calls:
            print(f"\n✨ 最终回答:\n{msg.content}")
            return

        # 执行工具调用
        for call in msg.tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments)
            print(f"⚡ Action: 调用 `{name}`(参数: {args})")
            
            obs = execute_tool(name, args)
            print(f"👁️ Observation: {obs}")

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": obs
            })

if __name__ == "__main__":
    run_react_agent("请分别对比一下苹果(apple)和英伟达(nvidia)的业务定位，并给出简要评价。")
