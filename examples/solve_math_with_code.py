"""
Example 1: Agent 自动写 Python 算高难数学题 (Math Solver via Code)
运行方式: python examples/solve_math_with_code.py
"""

import os
import sys

# 导入 nano_agent 包
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI
from nano_agent import NanoAgent

if __name__ == "__main__":
    api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY") or "your-api-key"
    base_url = os.getenv("BASE_URL") or "https://api.deepseek.com"
    model = os.getenv("MODEL_NAME") or "deepseek-chat"

    client = OpenAI(api_key=api_key, base_url=base_url)
    agent = NanoAgent(client=client, model=model, max_steps=8)

    # 考验大模型通过编写代码解决复杂排列组合/蒙特卡洛/大数计算的能力
    task = (
        "假设从 1 到 100 这 100 个自然数中随机取出 3 个不同的数，"
        "它们的和能够被 3 整除的概率是多少？请编写 Python 脚本精确计算出组合数并求出确切概率。"
    )

    agent.run(task)
