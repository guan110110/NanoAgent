"""
Terminal UI Renderer with Rich formatting and ANSI fallback.
"""

from typing import Optional

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.markdown import Markdown
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None


class AgentUI:
    """负责在控制台输出层次分明、视觉优美的 Agent 执行轨迹"""

    @staticmethod
    def print_goal(goal: str):
        if RICH_AVAILABLE:
            console.print(Panel(f"[bold cyan]{goal}[/bold cyan]", title="🎯 [bold]任务目标 (Goal)[/bold]", border_style="cyan"))
        else:
            print(f"\n\033[1;96m🎯 [任务目标]\033[0m {goal}\n" + "=" * 60)

    @staticmethod
    def print_step_header(step: int, max_steps: int):
        if RICH_AVAILABLE:
            console.rule(f"[bold yellow]Step {step}/{max_steps}[/bold yellow]")
        else:
            print(f"\n\033[1;33m--- [Step {step}/{max_steps}] ---\033[0m")

    @staticmethod
    def print_thought(content: str):
        if RICH_AVAILABLE:
            console.print(f"[bold blue]💭 Thought:[/bold blue] {content}")
        else:
            print(f"\033[94m💭 Thought:\033[0m {content}")

    @staticmethod
    def print_action(tool_name: str, args: dict):
        if RICH_AVAILABLE:
            console.print(f"[bold yellow]⚡ Action:[/bold yellow] [bold]{tool_name}[/bold] -> [dim]{args}[/dim]")
        else:
            print(f"\033[93m⚡ Action:\033[0m 调用 `{tool_name}` 参数: {args}")

    @staticmethod
    def print_observation(obs: str):
        preview = obs if len(obs) <= 300 else obs[:300] + "... [truncated]"
        if RICH_AVAILABLE:
            console.print(Panel(preview, title="👁️ Observation", border_style="magenta", expand=False))
        else:
            print(f"\033[95m👁️ Observation:\033[0m {preview}")

    @staticmethod
    def print_final_answer(answer: str):
        if RICH_AVAILABLE:
            console.print(Panel(Markdown(answer), title="✨ 最终完成结果 (Final Answer)", border_style="green"))
        else:
            print(f"\n\033[1;92m✨ [最终完成结果]\033[0m\n{answer}\n")
