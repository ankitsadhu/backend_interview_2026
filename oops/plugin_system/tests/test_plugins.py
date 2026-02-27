"""
tests/test_plugins.py — Validates concrete plugin behavior and ABC enforcement.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from plugins import PluginBase
from plugins.math_ops import MathOpsPlugin
from plugins.string_ops import StringOpsPlugin


# ============================================================
# ABC Enforcement
# ============================================================

def test_incomplete_plugin_raises_typeerror():
    """Prove that the ABC prevents instantiating plugins missing the interface."""
    class BadPlugin(PluginBase):
        @property
        def name(self): return "Bad"
        # Missing version and execute()

    with pytest.raises(TypeError):
        b = BadPlugin()


# ============================================================
# MathOpsPlugin
# ============================================================

def test_math_add():
    plugin = MathOpsPlugin()
    res = plugin.execute({"operation": "add", "a": 5, "b": 3})
    assert res == 8


def test_math_divide():
    plugin = MathOpsPlugin()
    res = plugin.execute({"operation": "divide", "a": 10, "b": 2})
    assert res == 5


def test_math_divide_by_zero():
    plugin = MathOpsPlugin()
    with pytest.raises(ZeroDivisionError):
        plugin.execute({"operation": "divide", "a": 10, "b": 0})


def test_math_invalid_data():
    plugin = MathOpsPlugin()
    with pytest.raises(ValueError, match="requires dict"):
        plugin.execute("not a dict")


def test_math_invalid_values():
    plugin = MathOpsPlugin()
    with pytest.raises(ValueError, match="must be numbers"):
        plugin.execute({"operation": "add", "a": "foo", "b": 3})


# ============================================================
# StringOpsPlugin
# ============================================================

def test_string_reverse():
    plugin = StringOpsPlugin()
    res = plugin.execute({"operation": "reverse", "text": "hello"})
    assert res == "olleh"


def test_string_uppercase():
    plugin = StringOpsPlugin()
    res = plugin.execute({"operation": "uppercase", "text": "hello"})
    assert res == "HELLO"


def test_string_invalid_op():
    plugin = StringOpsPlugin()
    with pytest.raises(ValueError, match="Unknown operation"):
        plugin.execute({"operation": "magic", "text": "hello"})
