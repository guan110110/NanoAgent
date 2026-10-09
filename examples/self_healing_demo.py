"""
示范 NanoAgent 的自我纠错与反思能力 (Self-Healing / Error Recovery Demo)
任务故意包含一个可能出错的操作，展示 Agent 如何捕获错误并自动修正。
"""

import os
import sys

# 引入父级目录的 nano_agent 模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nano_agent import NanoAgent, register_default_tools
from openai import OpenAI

if __name__ == "__main__":
    api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY") or "your-api-key"
    base_url = os.getenv("BASE_URL") or "https://api.deepseek.com"
    model = os.getenv("MODEL_NAME") or "deepseek-chat"

    client = OpenAI(api_key=api_key, base_url=base_url)
    agent = NanoAgent(client=client, model=model, max_steps=8)
    register_default_tools(agent)

    # 给出一个需要先探索、发现报错并自主修正的任务
    task = (
        "读取当前目录下的 `data_report.txt` 文件，如果文件不存在，"
        "请使用 Python 编写一段生成包含 5 个虚拟用户消费统计的逻辑，"
        "生成并写入到 `data_report.txt`，最后读取并输出前 3 行内容。"
    )

    agent.run(task)
