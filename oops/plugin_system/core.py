"""
plugin_system/core.py
Manages dynamic discovery and loading of plugins using importlib and pkgutil.
"""
import importlib
import pkgutil
from typing import Dict, List, Type

import plugins  # The namespace package we defined
from plugins import PluginBase


class PluginManager:
    """Discovers, loads, and manages instances of PluginBase subclasses."""

    def __init__(self) -> None:
        self._plugins: Dict[str, PluginBase] = {}

    def discover_and_load(self) -> None:
        """
        Scans the `plugins` package directory, imports all modules found,
        and registers any valid PluginBase subclasses.
        """
        # 1. Iterate over all modules in the 'plugins' package
        for _, module_name, is_pkg in pkgutil.iter_modules(plugins.__path__, plugins.__name__ + "."):
            if not is_pkg:
                # 2. Dynamically import the module
                importlib.import_module(module_name)

        # 3. Find all available subclasses that were just loaded into memory
        self._register_subclasses()

    def _register_subclasses(self) -> None:
        """Finds all concrete subclasses of PluginBase and instantiates them."""
        self._plugins.clear()

        # __subclasses__() returns all currently loaded classes that directly inherit from PluginBase
        for plugin_class in PluginBase.__subclasses__():
            try:
                # Abstract Base Classes (ABCs) cannot be instantiated if they are missing
                # implementations for @abstractmethod. This will raise a TypeError if invalid.
                plugin_instance = plugin_class()
                
                # Register by the plugin's self-reported name
                self._plugins[plugin_instance.name] = plugin_instance
                
            except TypeError as e:
                # Catch classes that failed to implement the strict ABC interface
                print(f"Warning: Failed to load plugin {plugin_class.__name__}: {e}")
            except Exception as e:
                print(f"Warning: Unexpected error loading plugin {plugin_class.__name__}: {e}")

    @property
    def active_plugins(self) -> List[PluginBase]:
        """Return a list of all successfully loaded plugin instances."""
        return list(self._plugins.values())

    def get_plugin(self, name: str) -> PluginBase:
        """Retrieve a specific plugin by name."""
        if name not in self._plugins:
            raise KeyError(f"Plugin '{name}' not found. Available: {list(self._plugins.keys())}")
        return self._plugins[name]

    def reload(self) -> None:
        """Clear the cache and rescan for plugins."""
        self.discover_and_load()
