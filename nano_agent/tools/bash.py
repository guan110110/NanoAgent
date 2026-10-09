"""
Safe Bash / Subprocess Execution Tool.
"""

import subprocess
import shlex
import sys

def execute_bash_command(command: str, timeout: int = 15) -> str:
    """在当前环境安全执行终端命令并返回输出"""
    # 基础防护黑名单（避免极端误操作）
    forbidden = ["rm -rf /", ":(){ :|:& };:", "mkfs", "dd if="]
    for pattern in forbidden:
        if pattern in command:
            return f"Security Error: 命令包含危险模式 '{pattern}'，已拦截。"

    try:
        res = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        output = res.stdout
        if res.stderr:
            output += ("\n[stderr]: " + res.stderr)
        return output if output.strip() else "[Command executed successfully with empty output]"
    except subprocess.TimeoutExpired:
        return f"Timeout Error: 命令在 {timeout} 秒内未执行完毕。"
    except Exception as e:
        return f"Execution Error ({type(e).__name__}): {str(e)}"
