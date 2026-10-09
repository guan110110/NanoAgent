"""
Example 2: 自主检索并整理研究报告 (Autonomous Researcher)
运行方式: python examples/autonomous_researcher.py
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

    task = (
        "通过搜索或代码分析，总结目前大语言模型主流架构 Transformer 与新兴架构 Mamba/SSM 的核心区别与优缺点对比，"
        "并整理成 Markdown 结构清晰的技术调研报告。"
    )

    agent.run(task)
