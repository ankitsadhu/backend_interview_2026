"""
plugin_system/plugins/__init__.py
Defines the Abstract Base Class (ABC) for all plugins.
"""
from abc import ABC, abstractmethod
from typing import Any


class PluginBase(ABC):
    """
    Abstract Base Class for all dynamic plugins.
    Any class inheriting from this MUST implement the abstract methods/properties.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the display name of the plugin."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Return the plugin version string."""
        pass

    @abstractmethod
    def execute(self, data: Any) -> Any:
        """
        Main execution logic for the plugin.
        
        Args:
            data (Any): Input data for the plugin to process.
            
        Returns:
            Any: The result of the plugin's processing.
        """
        pass
