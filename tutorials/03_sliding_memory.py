"""
Tutorial 03: 滑动窗口记忆管理 (Sliding Window Memory)
目的：解决长时间运行的长任务中上下文 (Context Window) 暴涨导致的超出限制与高昂费用。
运行方式: python tutorials/03_sliding_memory.py
"""

from typing import List, Dict, Any

class SlidingMemoryBuffer:
    """
    固定容量的滑动上下文记忆窗口。
    保留：系统提示词 (System Prompt) + 最初的用户目标 + 最近 N 轮交互记录。
    """
    def __init__(self, max_history_turns: int = 4):
        self.max_history_turns = max_history_turns
        self.system_message: Dict[str, Any] = {}
        self.initial_user_message: Dict[str, Any] = {}
        self.history: List[Dict[str, Any]] = []

    def set_system_message(self, content: str):
        self.system_message = {"role": "system", "content": content}

    def set_initial_goal(self, goal: str):
        self.initial_user_message = {"role": "user", "content": goal}

    def append(self, message: Dict[str, Any]):
        self.history.append(message)

    def get_context(self) -> List[Dict[str, Any]]:
        """获取组装后的有效上下文（滑动截断）"""
        context = []
        if self.system_message:
            context.append(self.system_message)
        if self.initial_user_message:
            context.append(self.initial_user_message)

        # 截取最近的 N 条消息
        recent_history = self.history[-self.max_history_turns:]
        context.extend(recent_history)
        return context

    def summary(self) -> str:
        return f"当前总历史消息: {len(self.history)}, 发送给模型的活动窗口大小: {len(self.get_context())}"

if __name__ == "__main__":
    mem = SlidingMemoryBuffer(max_history_turns=4)
    mem.set_system_message("你是一个高效的编程助手。")
    mem.set_initial_goal("请帮我完成数据分析任务。")

    # 模拟经过 10 轮繁复的工具调用与中间日志
    for i in range(1, 11):
        mem.append({"role": "assistant", "content": f"正在执行第 {i} 步排查..."})
        mem.append({"role": "tool", "content": f"第 {i} 步排查返回了大量原始文本数据..."})

    print(mem.summary())
    print("\n当前上下文前台渲染列表:")
    for idx, item in enumerate(mem.get_context(), 1):
        print(f"  {idx}. [{item['role']}]: {item['content'][:40]}...")
