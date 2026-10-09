# 02. 从零构建经典 ReAct 范式

**ReAct** 代表 **Reasoning + Acting**（推理 + 行动）。它最早由普林斯顿大学与 Google 在论文《ReAct: Synergizing Reasoning and Acting in Language Models》中提出。

---

## 1. 为什么单纯的 CoT (思维链) 不够用？

传统的 CoT（Chain of Thought）只在模型内部“思考”，由于模型参数中知识具有时效性且容易产生幻觉（Hallucination），对于需要依赖外部环境反馈、精准数学运算或动态查询的任务往往无能为力。

ReAct 建立了这样一个循环三部曲：
1. **Thought（思考）**：当前进度如何？还需要什么信息？下一步应该使用什么工具？
2. **Action（行动）**：决定调用哪一个外部工具，以及构造什么样的参数。
3. **Observation（观察）**：执行工具后，从外部物理世界获得的真实反馈。

---

## 2. ReAct 状态机循环

在代码层面，一个完整的 ReAct Loop 本质上就是一个 `while` 或限定最大步数的 `for` 循环：

```python
for step in range(max_steps):
    # 1. 询问大脑 (LLM)
    response = call_llm(messages, tools=registered_tools)
    
    # 2. 如果大脑认为任务已完成（未发起 Tool Call），输出最终回答并退出
    if not response.tool_calls:
        return response.content
        
    # 3. 否则，执行大脑选择的动作，获得观察结果
    for action in response.tool_calls:
        obs = execute_tool(action.name, action.args)
        messages.append({"role": "tool", "content": obs, "tool_call_id": action.id})
```

每一次 Observation 被追加进 `messages` 历史后，大模型在下一轮就看到了外部真实的执行反馈，从而产生新的思考（Next Thought），直到问题被彻底解决。
