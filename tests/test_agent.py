"""
Basic unit tests for NanoAgent core mechanics.
"""

from nano_agent.core import ToolRegistry
from nano_agent.tools.python_repl import PythonREPL
from nano_agent.tools.bash import execute_bash_command


def test_tool_registry():
    registry = ToolRegistry()

    @registry.register(
        name="add_numbers",
        description="Add two numbers together",
        parameters={
            "type": "object",
            "properties": {
                "a": {"type": "integer"},
                "b": {"type": "integer"}
            },
            "required": ["a", "b"]
        }
    )
    def add(a: int, b: int) -> int:
        return a + b

    # Check Schema Generation
    schemas = registry.schemas
    assert len(schemas) == 1
    assert schemas[0]["function"]["name"] == "add_numbers"

    # Check Execution
    result = registry.execute("add_numbers", {"a": 10, "b": 25})
    assert result == "35"


def test_python_repl():
    repl = PythonREPL()
    output = repl.run("x = 42\nprint(f'x is {x}')")
    assert "x is 42" in output


def test_safe_bash():
    output = execute_bash_command("echo HelloNanoAgent")
    assert "HelloNanoAgent" in output

    blocked = execute_bash_command("rm -rf /")
    assert "Security Error" in blocked
