"""
tests/test_plugin_manager.py — Validates dynamic plugin discovery.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core import PluginManager
from plugins import PluginBase


def test_discover_and_load():
    manager = PluginManager()
    manager.discover_and_load()

    plugins = manager.active_plugins
    assert len(plugins) >= 2  # Math and String plugins should be found

    names = [p.name for p in plugins]
    assert "MathOpsPlugin" in names
    assert "StringOpsPlugin" in names


def test_get_plugin():
    manager = PluginManager()
    manager.discover_and_load()

    plugin = manager.get_plugin("MathOpsPlugin")
    assert plugin.name == "MathOpsPlugin"
    assert plugin.version == "1.1.0"
    assert isinstance(plugin, PluginBase)


def test_get_nonexistent_plugin():
    manager = PluginManager()
    manager.discover_and_load()

    import pytest
    with pytest.raises(KeyError):
        manager.get_plugin("DoesNotExistPlugin")
