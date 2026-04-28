"""
plugin_system/plugins/math_ops.py
A sample plugin for basic mathematical operations.
"""
from typing import Any

from . import PluginBase


class MathOpsPlugin(PluginBase):
    """Plugin for performing basic arithmetic."""

    @property
    def name(self) -> str:
        return "MathOpsPlugin"

    @property
    def version(self) -> str:
        return "1.1.0"

    def execute(self, data: Any) -> Any:
        """
        Expects data in the format: {"operation": str, "a": float, "b": float}.
        Operations: 'add', 'subtract', 'multiply', 'divide'
        """
        if not isinstance(data, dict) or "operation" not in data:
            raise ValueError("MathOpsPlugin requires dict with 'operation', 'a', 'b'")

        try:
            a = float(data.get("a", 0))
            b = float(data.get("b", 0))
        except (TypeError, ValueError):
            raise ValueError("Values 'a' and 'b' must be numbers")

        op = str(data["operation"]).lower()

        if op == "add":
            return a + b
        elif op == "subtract":
            return a - b
        elif op == "multiply":
            return a * b
        elif op == "divide":
            if b == 0:
                raise ZeroDivisionError("Cannot divide by zero")
            return a / b
        else:
            raise ValueError(f"Unknown operation: {op}")
