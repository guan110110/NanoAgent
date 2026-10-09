"""
Python REPL Sandbox execution tool.
"""

import io
import contextlib
from typing import Dict, Any

class PythonREPL:
    """持久化的 Python 会话沙箱，支持多步变量复用"""
    def __init__(self):
        self.scope: Dict[str, Any] = {}

    def run(self, code: str) -> str:
        stdout_buf = io.StringIO()
        stderr_buf = io.StringIO()

        try:
            with contextlib.redirect_stdout(stdout_buf), contextlib.redirect_stderr(stderr_buf):
                exec(code, self.scope)
            output = stdout_buf.getvalue()
            err = stderr_buf.getvalue()
            if err:
                output += ("\n[stderr]: " + err)
            return output if output.strip() else "[Code executed successfully without stdout output]"
        except Exception as e:
            return f"Traceback Error ({type(e).__name__}): {str(e)}"
