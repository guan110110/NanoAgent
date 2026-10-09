# 01. 深入剖析 Function Calling 的底层原理

大语言模型（LLM）本身是一个“纯文本概率预测机器”，它**并不能直接执行任何外部 Python 函数或系统命令**。那么，AI Agent 是如何能够“调用工具”的？

---

## 1. 揭开黑盒：Schema 是如何传给大模型的？

当我们通过 SDK 发送 `tools` 参数时，API 会将工具的函数名、描述和参数结构转换成标准的 JSON Schema，并拼装在隐藏的 System Prompt 中传递给模型：

```json
{
  "type": "function",
  "function": {
    "name": "calculate_tax",
    "description": "计算指定金额的所得税",
    "parameters": {
      "type": "object",
      "properties": {
        "income": { "type": "number", "description": "年收入总额" },
        "rate": { "type": "number", "description": "税率，如 0.2" }
      },
      "required": ["income", "rate"]
    }
  }
}
```

模型经过专门的微调训练后，能够识别出：
* 如果用户的问题需要外部能力（如当前天气、实时计算），模型会**放弃生成普通文本**；
* 转向输出一段符合上述 JSON Schema 规范的特殊文本格式（通常包含 `<tool_call>` 标识符或 JSON 块）。

---

## 2. 工具分发执行的闭环

```text
[用户输入] -> [大模型推理] -> [输出结构化参数 JSON] -> [宿主程序解析并调用 Python 函数] -> [获得结果并写回 Context]
```

1. **宿主程序拦截**：OpenAI 官方 SDK 会帮我们解析这段特殊输出，并在 `message.tool_calls` 中提供 `function.name` 和 `function.arguments`。
2. **本地执行**：我们本地的 Python 代码通过反射或字典路由找到真实函数，将参数解包传入执行。
3. **Observation 回填**：执行完成后，必须以角色 `role="tool"` 并携带对应的 `tool_call_id` 将字符串结果返回给大模型。

这就是现代所有 Agent 工具调用的核心物理本质！
