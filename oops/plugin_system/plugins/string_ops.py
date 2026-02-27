"""
plugin_system/plugins/string_ops.py
A sample plugin for string manipulation.
"""
from typing import Any

from . import PluginBase


class StringOpsPlugin(PluginBase):
    """Plugin that provides string manipulation tools."""

    @property
    def name(self) -> str:
        return "StringOpsPlugin"

    @property
    def version(self) -> str:
        return "1.0.0"

    def execute(self, data: Any) -> Any:
        """
        Expects data in the format: {"operation": str, "text": str}.
        Operations: 'reverse', 'uppercase', 'lowercase'
        """
        if not isinstance(data, dict) or "text" not in data or "operation" not in data:
            raise ValueError("StringOpsPlugin requires dict with 'operation' and 'text'")

        text = str(data["text"])
        op = str(data["operation"]).lower()

        if op == "reverse":
            return text[::-1]
        elif op == "uppercase":
            return text.upper()
        elif op == "lowercase":
            return text.lower()
        else:
            raise ValueError(f"Unknown operation: {op}")
