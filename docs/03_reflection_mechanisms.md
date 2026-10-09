# 03. Agent 的自我反思与错误自愈机制 (Reflection & Self-Healing)

真正让 AI Agent 展现出“智能感”的瞬间，并不是它一次性给出完美答案，而是在**执行遇到错误、抛出异常或结果不符合预期时，它能够像人类程序员一样自我反思并修正**。

---

## 1. 错误的“无崩溃拦截”原则

许多初学者在编写 Agent 工具时，习惯在工具抛出异常时让 Python 程序崩溃（例如 `raise e`）。这是写 Agent 的大忌。

在 `NanoAgent` 中，我们遵循如下捕获原则：

```python
def execute(self, tool_name: str, args: dict) -> str:
    try:
        return str(self.tools[tool_name](**args))
    except Exception as e:
        # 捕获异常作为环境反馈 Observation，不崩溃！
        return f"Tool Execution Error ({type(e).__name__}): {str(e)}"
```

---

## 2. 激发自我反思的提示词设计

除了捕获 Traceback 之外，System Prompt 中需要赋予模型“反思者”的角色预期：

> *"如果工具执行报错，请仔细阅读反馈中的具体报错信息（Observation），思考引发错误的原因，并在下一步调整参数或重写代码进行重试。"*

### 典型自愈场景：
1. **语法/运行时错误自愈**：Agent 写了一段 Python 脚本，因为缺少变量或除以零报错 `ZeroDivisionError`。模型看到报错后，在下一步重写修复后的代码。
2. **环境探索自愈**：Agent 试图读取文件 `data.csv`，工具反馈 `FileNotFoundError`。Agent 随即自我调整：先调用文件列表工具查找是否存在类似命名的文件，或者自动生成一份示例数据。
