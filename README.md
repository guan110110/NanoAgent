<div align="center">

# ⚡ NanoAgent

**从零手写极致轻量、透明、无过度封装的现代化 AI 智能体框架**  
*A Minimalist, Educational AI Agent Framework from Scratch in < 200 Lines of Pure Python.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI Compatible](https://img.shields.io/badge/LLM-DeepSeek%20%7C%20OpenAI%20%7C%20Ollama-success.svg)](#支持的模型与服务)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/guan110110/NanoAgent/pulls)

[English](#english-overview) | [简体中文](#-为什么设计-nanoagent)

</div>

---

## 💡 为什么设计 NanoAgent？

当前各大开源社区充斥着庞大而复杂的 Agent 框架（如 LangChain、AutoGPT、CrewAI）。随着多层类继承、复杂回调与层层抽象的叠加，许多学习者常常困惑：
* **大模型到底接收到了什么 Prompt？**
* **Function Calling 与 ReAct 循环是如何在底层一步步驱动环境与工具的？**
* **智能体执行失败时，究竟是如何根据报错信息完成“自主反思与自愈 (Self-Correction)”的？**

**NanoAgent 的宗旨是：做 Agent 领域的 nanoGPT。**  
彻底剥离一切沉重的包装与魔法语法糖，仅用不到 200 行标准纯 Python 代码，让读者在 10 分钟内看清现代自主智能体的每一个核心运转齿轮。

---

## ✨ 核心特性

- 🎯 **纯粹极简**：单文件核心实现，零沉重第三方框架依赖，只有标准的 `openai` 接口协议。
- 🔄 **完整 ReAct 循环**：严格遵循 `Thought -> Action -> Observation -> ... -> Final Answer` 范式。
- 🛡️ **天然错误自愈 (Self-Healing)**：工具报错不崩溃，错误信息作为观察结果自动反馈给大模型，驱动智能体自主修正参数与代码。
- 🎨 **终端高亮输出**：内置色彩美化，思考过程、工具调用与执行反馈层次分明，观感极佳。
- 🌐 **全模型通用**：原生兼容 DeepSeek、OpenAI、阿里云百炼、通义千问、Kimi、Ollama 本地大模型。

---

## 📊 对比主流框架

| 比较维度 | 传统厚重框架 (如 LangChain) | **NanoAgent (本项目)** |
| :--- | :--- | :--- |
| **代码量** | 动辄数万行，调用栈深不可测 | **< 200 行，透明清晰，单文件可读完** |
| **调试难度** | 需要学习复杂的专用 Debugger 和 Callback | **直接 `print` 或单步断点调试，零心智负担** |
| **上手耗时** | 学习周期几天至数周 | **10 分钟看懂全部底层机制** |
| **自愈机制** | 内部黑盒处理或直接抛错 | **开放式异常捕获，直接作为 Observation 触发自愈** |

---

## 🏗️ 架构流转原理

```mermaid
flowchart TD
    User([用户目标输入]) --> LoopStart[开始 ReAct 自主循环]
    
    subgraph AgentEngine [NanoAgent 核心调度引擎]
        LLM[大语言模型推理]
        Decision{是否触发工具调用?}
        Obs[环境观察与反馈 Observation]
    end

    subgraph ToolRegistry [工具管理中心]
        ToolExec[Python代码沙箱 / 文件读写 / API]
    end

    LoopStart --> LLM
    LLM --> Decision
    Decision -- 是 (Action) --> ToolExec
    ToolExec --> Obs
    Obs --> LLM
    Decision -- 否 (任务完成) --> Done([最终答案输出])
```

---

## 🚀 30 秒极速上手

### 1. 克隆仓库与安装依赖

```bash
git clone https://github.com/guan110110/NanoAgent.git
cd NanoAgent

# 仅需安装标准 openai 库
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填写你的 API Key（以极高性价比的 **DeepSeek** 为例）：

```bash
# Windows PowerShell
$env:DEEPSEEK_API_KEY="your-deepseek-api-key"
$env:BASE_URL="https://api.deepseek.com"
$env:MODEL_NAME="deepseek-chat"

# Linux / macOS
export DEEPSEEK_API_KEY="your-deepseek-api-key"
export BASE_URL="https://api.deepseek.com"
export MODEL_NAME="deepseek-chat"
```

### 3. 运行体验

```bash
python nano_agent.py
```

终端将打印漂亮的彩色思考与行动轨迹：
```text
🎯 [任务目标] 用 Python 编写一段代码计算 1 到 1000 内所有素数之和；把结果写入 'prime_sum.txt' 中并验证。
=================================================================

[Step 1/8] Agent 正在推理...
💭 Thought: 需要计算 1 到 1000 内所有素数的和。为了确保结果准确，我应该使用 Python 代码进行计算。
⚡ Action: 调用工具 `execute_python`
   参数: {"code": "def is_prime(n):\n    if n < 2:\n        return False\n    for i in range(2, int(n**0.5) + 1):\n        if n % i == 0:\n            return False\n    return True\n\nprime_sum = sum(i for i in range(1, 1001) if is_prime(i))\nprint(prime_sum)"}
👁️ Observation: 76127

[Step 2/8] Agent 正在推理...
💭 Thought: 素数之和计算完成，结果为 76127。接下来将结果写入文件 'prime_sum.txt'。
⚡ Action: 调用工具 `write_file`
...
```

---

## 🛠️ 如何添加自定义工具？

利用自带的 `@agent.registry.register` 装饰器，您可以像写普通 Python 函数一样轻松挂载任何工具：

```python
from nano_agent import NanoAgent, register_default_tools

agent = NanoAgent()
register_default_tools(agent)

# 注册一个自定义天气查询工具
@agent.registry.register(
    name="get_weather",
    description="查询指定城市的天气温度",
    parameters={
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "城市名称，例如北京、上海"}
        },
        "required": ["city"]
    }
)
def get_weather(city: str) -> str:
    return f"{city} 当前天气晴朗，气温 22℃。"

# 开始执行
agent.run("帮我查一下北京今天的天气，并根据天气推荐穿衣风格。")
```

---

## 🗺️ 后续路线图 (Roadmap)

- [x] 极简 ReAct 驱动引擎与终端高亮
- [x] 原生 Python REPL 与文件安全沙箱
- [ ] 增加 MCP (Model Context Protocol) 客户端适配支持
- [ ] 增加滑动窗口长任务记忆上下文压缩 (Sliding Memory Buffer)
- [ ] 支持轻量 WebUI 交互界面 (Streamlit / Gradio)

---

<div id="english-overview"></div>

## 🌐 English Overview

**NanoAgent** is an educational, production-ready AI Agent framework built from scratch in less than 200 lines of Python. It strips away all obscure layers of abstraction found in mainstream frameworks, making the mechanics of **ReAct loops, function calling, tool dispatching, and self-reflection** completely transparent and enjoyable to learn.

---

## 📄 开源许可证

本项目采用 [MIT License](LICENSE) 开源协议，欢迎自由学习、商用与二次开发。

如果你觉得这个项目对你理解 AI Agent 的运作原理有所帮助，请在 GitHub 上点一颗 **⭐️ Star** 支持一下！
