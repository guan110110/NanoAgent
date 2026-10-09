"""
Tutorial 01: 最简原生函数调用 (Raw Function Calling)
目的：脱离任何封装，用 50 行纯 Python 讲透大模型是如何决定调用函数并解析参数的。
运行方式: python tutorials/01_raw_function_call.py
"""

import os
import json
from openai import OpenAI

# 1. 定义一个真实的本地业务函数
def calculate_compound_interest(principal: float, annual_rate: float, years: int) -> float:
    """计算复利最终收益"""
    return round(principal * ((1 + annual_rate) ** years), 2)

# 2. 手写该函数的 OpenAPI JSON Schema 描述（大模型就是根据这个理解工具的）
tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "calculate_compound_interest",
            "description": "计算定期投资的复利终值",
            "parameters": {
                "type": "object",
                "properties": {
                    "principal": {"type": "number", "description": "本金金额"},
                    "annual_rate": {"type": "number", "description": "年化收益率，例如 0.05 代表 5%"},
                    "years": {"type": "integer", "description": "投资年限"}
                },
                "required": ["principal", "annual_rate", "years"]
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

    prompt = "我手头有 50,000 元本金，如果年化收益率是 4.5%，存 5 年后总共有多少钱？"
    print(f"用户问题: {prompt}\n")

    # 第一轮请求：把用户问题和工具描述一起发给大模型
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools_schema,
        tool_choice="auto"
    )
    choice = response.choices[0].message
    messages.append(choice)

    # 检查大模型是否做出了调用工具的决定
    if choice.tool_calls:
        call = choice.tool_calls[0]
        func_name = call.function.name
        func_args = json.loads(call.function.arguments)
        print(f"[模型决策] 触发工具调用: {func_name}")
        print(f"[模型参数] 解析出参数: {func_args}")

        # 本地执行真实函数
        if func_name == "calculate_compound_interest":
            result = calculate_compound_interest(**func_args)
            print(f"[本地执行] 真实函数运行结果: {result}")

            # 第二轮请求：将工具运行结果喂回给大模型以生成自然语言回答
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": str(result)
            })

            final_response = client.chat.completions.create(model=model, messages=messages)
            print(f"\n[最终回复] {final_response.choices[0].message.content}")

if __name__ == "__main__":
    main()
